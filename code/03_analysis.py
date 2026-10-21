#!/usr/bin/env python3
"""03_analysis.py — models, heterogeneity, sensitivity, access tables; writes paper/stats.json and tables.

Run from repo root:  python code/03_analysis.py
Every number quoted in any document comes from paper/stats.json (written here) or the tables it writes.
"""
import json
import os
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(ROOT, "data", "processed")
PAPER = os.path.join(ROOT, "paper")
TAB = os.path.join(PAPER, "tables")
os.makedirs(TAB, exist_ok=True)
S = {}  # the stats file


def r(x, k=3):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), k)


# --------------------------------------------------------------------------- data
p0 = pd.read_csv(os.path.join(PROC, "school_cohort_panel.csv"), dtype={"NCESSCH": str, "idoe_sch": str})
MIN_INPUB = 10   # school-cohorts with fewer Indiana public enrollees are dropped (outcome means too noisy)


def prep(df):
    d = df.copy()
    d["dc10"] = d.dc_share * 10
    d["frl10"] = d.frl_share * 10
    d["ap10"] = d.ap_pass_share * 10
    d["alg10"] = d.corp_early_alg.clip(upper=1.0) * 10
    d["hsalg10"] = d.hs_alg_rate.clip(upper=1.2) * 10
    d["lgr"] = np.log(d.grads)
    d["inpub10"] = d.inpub_rate * 10
    d["calc"] = d.calc_offered.astype(float)
    d["advm"] = d.advm_offered.astype(float)
    d["rural"] = (d.locale4 == "Rural").astype(float)
    return d


base = prep(p0[(p0.cohort >= 2021) & p0.gpa.notna() & p0.dc_share.notna() & (p0.enr_inpub >= MIN_INPUB)])
full = base.dropna(subset=["alg10", "calc", "advm", "locale4", "inpub10", "frl10"])
S["sample"] = {
    "cohorts": "2021-2024",
    "min_inpub": MIN_INPUB,
    "school_cohorts": int(len(full)),
    "schools": int(full.NCESSCH.nunique()),
    "grads": int(full.grads.sum()),
    "inpub": int(full.enr_inpub.sum()),
    "school_cohorts_before_controls": int(len(base)),
}
S["descriptives"] = {
    "dc_share_median": r(full.dc_share.median()),
    "dc_share_p10": r(full.dc_share.quantile(.1)),
    "dc_share_p90": r(full.dc_share.quantile(.9)),
    "dc_share_weighted_mean": r(np.average(full.dc_share, weights=full.grads)),
    "gpa_weighted_mean": r(np.average(full.gpa, weights=full.enr_inpub), 2),
    "credits_weighted_mean": r(np.average(full.credits, weights=full.enr_inpub), 1),
    "remed_rate_weighted_mean": r(np.average(full.remed_rate, weights=full.enr_inpub)),
    "frl_share_median": r(full.frl_share.median()),
    "corp_early_alg_median": r(full.corp_early_alg.median()),
    "calc_offered_share_schools": r(full.drop_duplicates("NCESSCH").calc.mean()),
    "corr_dc_frl": r(full[["dc_share", "frl_share"]].corr().iloc[0, 1], 2),
    "corr_dc_gpa": r(full[["dc_share", "gpa"]].corr().iloc[0, 1], 2),
}

# --------------------------------------------------------------------------- main models
SPECS = {
    "M1 cohort only": "dc10 + C(cohort)",
    "M2 + poverty, AP, size, locale": "dc10 + frl10 + ap10 + lgr + C(locale4) + C(cohort)",
    "M3 + Algebra I timing, math offerings": "dc10 + frl10 + ap10 + lgr + C(locale4) + alg10 + calc + advm + C(cohort)",
    "M4 + in-state public college-going": "dc10 + frl10 + ap10 + lgr + C(locale4) + alg10 + calc + advm + inpub10 + C(cohort)",
    "M5 school fixed effects": "dc10 + C(NCESSCH) + C(cohort)",
}
OUTCOMES = {"gpa": "First-year GPA", "credits": "First-year credits earned", "remed_rate": "Share needing remediation"}


def fit(y, rhs, d, weighted=True):
    d = d.dropna(subset=[y])
    w = d.enr_inpub if weighted else np.ones(len(d))
    return smf.wls(f"{y} ~ {rhs}", d, weights=w).fit(cov_type="cluster", cov_kwds={"groups": d.NCESSCH})


rows, S["models"] = [], {}
for y, ylab in OUTCOMES.items():
    S["models"][y] = {}
    for name, rhs in SPECS.items():
        m = fit(y, rhs, full)
        b, se, pv = m.params["dc10"], m.bse["dc10"], m.pvalues["dc10"]
        ci = m.conf_int().loc["dc10"]
        key = name.split()[0]
        S["models"][y][key] = {"b": r(b, 4), "se": r(se, 4), "p": r(pv, 4), "lo": r(ci[0], 4), "hi": r(ci[1], 4),
                               "n": int(m.nobs), "r2": r(m.rsquared, 3)}
        rows.append({"outcome": ylab, "model": name, "coef_per_10pp": b, "se": se, "ci_low": ci[0], "ci_high": ci[1],
                     "p": pv, "n": int(m.nobs), "r2": m.rsquared})
        if key == "M3":
            S["models"][y]["M3_controls"] = {k: {"b": r(m.params[k], 4), "p": r(m.pvalues[k], 4)}
                                             for k in ["frl10", "ap10", "alg10", "calc", "advm", "lgr"]}
pd.DataFrame(rows).to_csv(os.path.join(TAB, "table2_main_models.csv"), index=False)

g = S["models"]["gpa"]
S["attenuation_gpa_M1_to_M3"] = r(1 - g["M3"]["b"] / g["M1"]["b"], 2)
c = S["models"]["credits"]
S["attenuation_credits_M1_to_M3"] = r(1 - c["M3"]["b"] / c["M1"]["b"], 2)
# implied difference between a p10 and p90 dual-credit school under M3
gap = (full.dc_share.quantile(.9) - full.dc_share.quantile(.1)) * 10
S["p10_p90_implied"] = {"dc_pp": r(gap * 10, 1), "gpa": r(g["M3"]["b"] * gap, 3), "credits": r(c["M3"]["b"] * gap, 2)}

# --------------------------------------------------------------------------- heterogeneity ("for which schools")
M3 = SPECS["M3 + Algebra I timing, math offerings"]
het = []
S["heterogeneity"] = {}
full["frl_hi"] = (full.frl_share >= full.frl_share.median()).astype(float)
full["alg_lo"] = (full.corp_early_alg < full.corp_early_alg.median()).astype(float)
for mod, lab in [("frl_hi", "High-poverty school (FRL share at or above median)"),
                 ("rural", "Rural school"),
                 ("alg_lo", "Below-median early Algebra I in corporation"),
                 ("calc", "Offers calculus")]:
    S["heterogeneity"][mod] = {}
    for y in ["gpa", "credits"]:
        m = fit(y, M3 + f" + dc10:{mod}" + ("" if mod in ("rural", "calc") else f" + {mod}"), full)
        k = f"dc10:{mod}"
        base_b = m.params["dc10"]
        # slope for the moderator group = main + interaction; SE from the covariance matrix
        V = m.cov_params()
        grp_b = base_b + m.params[k]
        grp_se = np.sqrt(V.loc["dc10", "dc10"] + V.loc[k, k] + 2 * V.loc["dc10", k])
        S["heterogeneity"][mod][y] = {"slope_other": r(base_b, 4), "se_other": r(m.bse["dc10"], 4),
                                      "slope_group": r(grp_b, 4), "se_group": r(grp_se, 4),
                                      "interaction": r(m.params[k], 4), "p_interaction": r(m.pvalues[k], 4)}
        het.append({"moderator": lab, "outcome": OUTCOMES[y], "slope_in_group": grp_b, "se_group": grp_se,
                    "slope_others": base_b, "se_others": m.bse["dc10"], "difference": m.params[k],
                    "p_difference": m.pvalues[k]})
pd.DataFrame(het).to_csv(os.path.join(TAB, "table3_heterogeneity.csv"), index=False)

# --------------------------------------------------------------------------- within-school gap (descriptive)
w = p0[(p0.cohort >= 2021) & p0.dc_gpa_gap.notna() & p0.nodc_inpub.ge(10) & p0.dc_inpub.ge(10)].copy()
wt = w.dc_inpub + w.nodc_inpub
S["within_school"] = {
    "school_cohorts": int(len(w)), "schools": int(w.NCESSCH.nunique()),
    "gpa_gap_mean": r(np.average(w.dc_gpa_gap, weights=wt), 2),
    "credit_gap_mean": r(np.average(w.dc_credit_gap.dropna(), weights=wt[w.dc_credit_gap.notna()]), 1),
    "share_positive_gap": r((w.dc_gpa_gap > 0).mean(), 2),
}
w = prep(w)
mg = smf.wls("dc_gpa_gap ~ dc10 + frl10 + C(cohort)", w, weights=wt).fit(
    cov_type="cluster", cov_kwds={"groups": w.NCESSCH})
S["within_school"]["gap_slope_dc10"] = r(mg.params["dc10"], 4)
S["within_school"]["gap_slope_p"] = r(mg.pvalues["dc10"], 4)
S["within_school"]["nodc_gpa_slope_dc10"] = r(
    smf.wls("nodc_gpa ~ dc10 + frl10 + C(cohort)", w, weights=w.nodc_inpub).fit(
        cov_type="cluster", cov_kwds={"groups": w.NCESSCH}).params["dc10"], 4)

# --------------------------------------------------------------------------- sensitivity
sens = []
S["sensitivity"] = {}


def add_sens(key, label, d, rhs=M3, weighted=True):
    out = {}
    for y in ["gpa", "credits"]:
        m = fit(y, rhs, d, weighted)
        out[y] = {"b": r(m.params["dc10"], 4), "se": r(m.bse["dc10"], 4), "p": r(m.pvalues["dc10"], 4), "n": int(m.nobs)}
        sens.append({"check": label, "outcome": OUTCOMES[y], "coef_per_10pp": m.params["dc10"], "se": m.bse["dc10"],
                     "p": m.pvalues["dc10"], "n": int(m.nobs)})
    S["sensitivity"][key] = out


add_sens("main", "Main specification (M3)", full)
add_sens("no_virtual", "Exclude virtual schools", full[~full.virtual])
add_sens("unweighted", "Unweighted", full, weighted=False)
add_sens("min30", "Schools with 30+ Indiana public enrollees", full[full.enr_inpub >= 30])
hs_alg = base.dropna(subset=["hsalg10", "calc", "advm", "locale4", "frl10"])
add_sens("hs_alg", "High-school Algebra I measure instead of corporation measure",
         hs_alg, M3.replace("alg10", "hsalg10"))
both_alg = base.dropna(subset=["hsalg10", "alg10", "calc", "advm", "locale4", "frl10"])
add_sens("both_alg", "Both Algebra I measures", both_alg, M3 + " + hsalg10")
with19 = prep(p0[p0.gpa.notna() & p0.dc_share.notna() & (p0.enr_inpub >= MIN_INPUB)]).dropna(
    subset=["alg10", "calc", "advm", "locale4", "frl10"])
add_sens("with2019", "Add pre-pandemic 2019 cohort", with19)
add_sens("only2024", "2024 cohort only", full[full.cohort == 2024], M3.replace(" + C(cohort)", ""))
pd.DataFrame(sens).to_csv(os.path.join(TAB, "table4_sensitivity.csv"), index=False)
S["sensitivity_range_gpa"] = [r(min(v["gpa"]["b"] for v in S["sensitivity"].values()), 4),
                              r(max(v["gpa"]["b"] for v in S["sensitivity"].values()), 4)]
S["sensitivity_range_credits"] = [r(min(v["credits"]["b"] for v in S["sensitivity"].values()), 4),
                                  r(max(v["credits"]["b"] for v in S["sensitivity"].values()), 4)]

# --------------------------------------------------------------------------- access ("out of reach")
a = pd.read_csv(os.path.join(PROC, "school_access.csv"), dtype={"NCESSCH": str, "CNTY": str})
a = a[a.dual_any.notna()].copy()                       # matched to CRDC 2023-24
a["enr"] = a.enr_total
# a school counts as offering calculus / dual enrollment if it did in either CRDC year (2021-22 or 2023-24)
a["dual_any"] = a.dual_either.astype(bool)
a["calc_offered"] = a.calc_either.astype(bool)
LOW_UPTAKE = 1 / 3


def tier(x):
    if x.virtual or x.alt:
        return "Virtual or alternative"
    if not x.dual_any:
        return "No dual enrollment reported"
    if (not x.calc_offered) and (pd.isna(x.dc_share_pooled) or x.dc_share_pooled < LOW_UPTAKE):
        return "Thin pathway: no calculus and low uptake"
    if not x.calc_offered:
        return "Dual credit, but no calculus"
    return "Dual credit and calculus"


a["tier"] = a.apply(tier, axis=1)
a.to_csv(os.path.join(PROC, "school_access_tiers.csv"), index=False)
trad = a[a.tier != "Virtual or alternative"]
S["access"] = {
    "schools_crdc_2324": int(len(a)),
    "traditional_schools": int(len(trad)),
    "low_uptake_threshold": r(LOW_UPTAKE, 3),
    "tiers": {t: {"schools": int((trad.tier == t).sum()), "students": int(trad.loc[trad.tier == t, "enr"].sum())}
              for t in trad.tier.unique()},
    "no_calc_share_schools": r((~trad.calc_offered).mean()),
    "no_calc_share_students": r(trad.loc[~trad.calc_offered, "enr"].sum() / trad.enr.sum()),
    "no_dual_share_schools": r((~trad.dual_any).mean()),
    "virtual_alt_schools": int((a.tier == "Virtual or alternative").sum()),
}
by_loc = trad.groupby("locale4").apply(lambda t: pd.Series({
    "schools": len(t), "students": t.enr.sum(),
    "no_calculus_pct_schools": 100 * (~t.calc_offered).mean(),
    "no_dual_pct_schools": 100 * (~t.dual_any).mean(),
    "thin_or_none_pct_students": 100 * t.loc[t.tier.isin(["No dual enrollment reported",
                                                          "Thin pathway: no calculus and low uptake"]), "enr"].sum()
    / t.enr.sum(),
    "median_dc_share": t.dc_share_pooled.median()}), include_groups=False)
by_loc.to_csv(os.path.join(TAB, "table5_access_by_locale.csv"))
S["access"]["by_locale"] = {k: {kk: r(vv, 3) for kk, vv in v.items()} for k, v in by_loc.to_dict("index").items()}
trad = trad.assign(frl_q=pd.qcut(trad.frl_share_pooled, 4, labels=["Q1 lowest", "Q2", "Q3", "Q4 highest"]))
by_frl = trad.groupby("frl_q", observed=True).apply(lambda t: pd.Series({
    "schools": len(t), "no_calculus_pct_schools": 100 * (~t.calc_offered).mean(),
    "median_dc_share": t.dc_share_pooled.median()}), include_groups=False)
by_frl.to_csv(os.path.join(TAB, "table6_access_by_poverty.csv"))
S["access"]["by_frl_quartile"] = {str(k): {kk: r(vv, 3) for kk, vv in v.items()}
                                  for k, v in by_frl.to_dict("index").items()}
cty = trad.groupby(["CNTY", "NMCNTY"]).apply(lambda t: pd.Series({
    "schools": len(t), "students": t.enr.sum(),
    "pct_students_no_calc": 100 * t.loc[~t.calc_offered, "enr"].sum() / t.enr.sum(),
    "pct_students_thin_or_none": 100 * t.loc[t.tier.isin(["No dual enrollment reported",
                                                          "Thin pathway: no calculus and low uptake"]), "enr"].sum()
    / t.enr.sum()}), include_groups=False).reset_index()
cty.to_csv(os.path.join(TAB, "table7_access_by_county.csv"), index=False)
S["access"]["counties"] = int(len(cty))
S["access"]["counties_no_calc_anywhere"] = int((cty.pct_students_no_calc >= 99.999).sum())
S["access"]["counties_majority_no_calc"] = int((cty.pct_students_no_calc > 50).sum())

# --------------------------------------------------------------------------- table 1 descriptives
t1 = full.assign(dc_tercile=pd.qcut(full.dc_share, 3, labels=["Low", "Middle", "High"])).groupby(
    "dc_tercile", observed=True).agg(
    school_cohorts=("NCESSCH", "size"), dc_share=("dc_share", "median"), frl_share=("frl_share", "median"),
    ap_pass_share=("ap_pass_share", "median"), corp_early_alg=("corp_early_alg", "median"),
    calc_offered=("calc", "mean"), rural=("rural", "mean"), grads=("grads", "median"),
    gpa=("gpa", "median"), credits=("credits", "median"), remed_rate=("remed_rate", "median"))
t1.to_csv(os.path.join(TAB, "table1_descriptives_by_dc_tercile.csv"))
S["table1"] = {str(k): {kk: r(vv, 3) for kk, vv in v.items()} for k, v in t1.to_dict("index").items()}

with open(os.path.join(PAPER, "stats.json"), "w") as f:
    json.dump(S, f, indent=2)
print(json.dumps({k: S[k] for k in ["sample", "attenuation_gpa_M1_to_M3", "p10_p90_implied", "within_school",
                                    "sensitivity_range_gpa", "sensitivity_range_credits"]}, indent=1))
print(json.dumps(S["models"]["gpa"], indent=0)[:900])
print(json.dumps(S["heterogeneity"], indent=0)[:1600])
print(json.dumps(S["access"], indent=0)[:2500])
