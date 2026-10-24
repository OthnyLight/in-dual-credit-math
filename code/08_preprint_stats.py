#!/usr/bin/env python3
"""08_preprint_stats.py — additional statistics for the preprint; writes paper/preprint/stats_extra.json.

Run from repo root after 03_analysis.py:  python code/08_preprint_stats.py
Reuses the exact sample and specifications of 03_analysis.py.
"""
import json
import os
import re
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(ROOT, "paper", "preprint")
os.makedirs(OUT, exist_ok=True)
S = json.load(open(os.path.join(ROOT, "paper", "stats.json")))
X = {}


def r(x, k=4):
    if x is None:
        return None
    x = float(x)
    return None if np.isnan(x) else round(x, k)


p0 = pd.read_csv(os.path.join(PROC, "school_cohort_panel.csv"), dtype={"NCESSCH": str, "idoe_sch": str})
MIN = S["sample"]["min_inpub"]


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


base = prep(p0[(p0.cohort >= 2021) & p0.gpa.notna() & p0.dc_share.notna() & (p0.enr_inpub >= MIN)])
full = base.dropna(subset=["alg10", "calc", "advm", "locale4", "inpub10", "frl10"])
assert len(full) == S["sample"]["school_cohorts"], "sample differs from 03_analysis.py"

# ---------------------------------------------------------------- full coefficient table for M2, M3, M5
M2 = "dc10 + frl10 + ap10 + lgr + C(locale4) + C(cohort)"
M3 = "dc10 + frl10 + ap10 + lgr + C(locale4) + alg10 + calc + advm + C(cohort)"
M4 = M3.replace(" + C(cohort)", " + inpub10 + C(cohort)")
X["full_models"] = {}
for y in ["gpa", "credits", "remed_rate"]:
    X["full_models"][y] = {}
    for key, rhs in [("M2", M2), ("M3", M3), ("M4", M4)]:
        m = smf.wls(f"{y} ~ {rhs}", full, weights=full.enr_inpub).fit(
            cov_type="cluster", cov_kwds={"groups": full.NCESSCH})
        X["full_models"][y][key] = {
            k: {"b": r(m.params[k], 5), "se": r(m.bse[k], 5), "p": r(m.pvalues[k], 4)}
            for k in m.params.index if k != "Intercept"}
        X["full_models"][y][key]["_n"] = int(m.nobs)
        X["full_models"][y][key]["_r2"] = r(m.rsquared, 3)
        X["full_models"][y][key]["_clusters"] = int(full.NCESSCH.nunique())

# ---------------------------------------------------------------- cohort trends (all public linked, unrestricted by controls)
trend = []
for c, g in p0[p0.gpa.notna() & p0.dc_share.notna() & (p0.enr_inpub >= MIN)].groupby("cohort"):
    trend.append({
        "cohort": int(c), "schools": int(g.NCESSCH.nunique()), "grads": int(g.grads.sum()),
        "inpub": int(g.enr_inpub.sum()),
        "dc_share": r(g.dc_n.sum() / g.grads[g.dc_n.notna()].sum()),
        "inpub_rate": r(g.enr_inpub.sum() / g.grads.sum()),
        "gpa": r(np.average(g.gpa, weights=g.enr_inpub), 3),
        "credits": r(np.average(g.credits, weights=g.enr_inpub), 2),
        "remed": r(g.need_remed.sum() / g.enr_inpub.sum()),
        "frl": r(g.frl_n.sum() / g.grads[g.frl_n.notna()].sum()),
    })
X["trend"] = trend

# ---------------------------------------------------------------- distribution of dual-credit share (analytic sample)
h, edges = np.histogram(full.dc_share, bins=np.arange(0, 1.05, 0.05))
X["dc_hist"] = {"counts": [int(v) for v in h], "edges": [r(e, 2) for e in edges]}
X["dc_share_quantiles"] = {q: r(full.dc_share.quantile(float(q)), 3) for q in ["0.1", "0.25", "0.5", "0.75", "0.9"]}
X["n_dc_zero"] = int((full.dc_share == 0).sum())
X["n_dc_ge_90"] = int((full.dc_share >= 0.9).sum())

# ---------------------------------------------------------------- correlations
cols = ["dc_share", "frl_share", "ap_pass_share", "corp_early_alg", "calc", "gpa", "credits", "remed_rate"]
X["corr"] = {a: {b: r(full[[a, b]].corr().iloc[0, 1], 2) for b in cols} for a in cols}

# ---------------------------------------------------------------- weighted descriptives table (mean, sd, min, max)
def wstats(s, w):
    m = np.average(s, weights=w)
    return {"mean": r(m, 3), "sd": r(np.sqrt(np.average((s - m) ** 2, weights=w)), 3),
            "min": r(s.min(), 3), "max": r(s.max(), 3)}


X["desc"] = {c: wstats(full[c], full.enr_inpub) for c in
             ["dc_share", "frl_share", "ap_pass_share", "corp_early_alg", "hs_alg_rate", "calc", "advm",
              "inpub_rate", "gpa", "credits", "remed_rate"] if full[c].notna().all()}
X["desc"]["hs_alg_rate"] = wstats(full.hs_alg_rate.dropna().clip(upper=1.2),
                                  full.enr_inpub[full.hs_alg_rate.notna()])
X["desc"]["grads"] = {"mean": r(full.grads.mean(), 1), "sd": r(full.grads.std(), 1),
                      "min": int(full.grads.min()), "max": int(full.grads.max())}
X["locale_mix"] = {k: int(v) for k, v in full.drop_duplicates("NCESSCH").locale4.value_counts().items()}
X["math_remed_share_of_remed"] = r(
    (full.rem_math_only.fillna(0) + full.rem_both.fillna(0)).sum() / full.need_remed.sum(), 3)

# ---------------------------------------------------------------- within-school sextiles
w = p0[(p0.cohort >= 2021) & p0.dc_gpa_gap.notna() & p0.nodc_inpub.ge(10) & p0.dc_inpub.ge(10)].copy()
w["sext"] = pd.qcut(w.dc_share, 6, labels=False)
sx = []
for k, g in w.groupby("sext"):
    sx.append({"sextile": int(k) + 1, "n": int(len(g)), "dc_share_med": r(g.dc_share.median(), 3),
               "dc_gpa": r(np.average(g.dc_gpa, weights=g.dc_inpub), 3),
               "nodc_gpa": r(np.average(g.nodc_gpa, weights=g.nodc_inpub), 3),
               "dc_credits": r(np.average(g.dc_credits.dropna(), weights=g.dc_inpub[g.dc_credits.notna()]), 2),
               "nodc_credits": r(np.average(g.nodc_credits.dropna(), weights=g.nodc_inpub[g.nodc_credits.notna()]), 2)})
X["within_sextiles"] = sx

# ---------------------------------------------------------------- linkage counts from the QA report
qa = open(os.path.join(PROC, "qa_report.txt"), encoding="utf-8").read()
X["linkage"] = {}
for c, n, l, pct in re.findall(r"cohort (\d{4}): (\d+) schools; linked to an IDOE number: (\d+) \(([\d.]+)%\)", qa):
    X["linkage"][c] = {"schools": int(n), "linked": int(l), "pct": float(pct)}
m = re.search(r"school-cohorts: (\d+); with numeric \(public\) IDOE number: (\d+)", qa)
X["linkage"]["school_cohorts_all"], X["linkage"]["school_cohorts_public"] = int(m.group(1)), int(m.group(2))
m = re.search(r"after dropping nonpublic, unmatched, and correctional facilities: (\d+) school-cohorts, (\d+) schools", qa)
X["linkage"]["panel_school_cohorts"], X["linkage"]["panel_schools"] = int(m.group(1)), int(m.group(2))
m = re.search(r"matched to CRDC: ([\d.]+)%; hs_alg_rate available: ([\d.]+)%; corp_early_alg available: ([\d.]+)%", qa)
X["linkage"]["crdc_match_pct"], X["linkage"]["hs_alg_pct"], X["linkage"]["corp_alg_pct"] = map(float, m.groups())
m = re.search(r"calculus status changed .* at (\d+) schools", qa)
X["linkage"]["calc_changed"] = int(m.group(1))
m = re.search(r"CCD schools offering grade 12 \(excluding correctional\): (\d+)", qa)
X["linkage"]["ccd_hs"] = int(m.group(1))
for t in ["2021-22", "2023-24"]:
    m = re.search(rf"CRDC {t}: Indiana schools (\d+); offering grade 12: (\d+); dual-enrollment indicator Yes: (\d+)", qa)
    X["linkage"][f"crdc_{t}"] = {"schools": int(m.group(1)), "g12": int(m.group(2)), "dual_yes": int(m.group(3))}
    m = re.search(rf"{t}: corporations with early-Algebra measure \(>=20 eighth graders\): (\d+); median ([\d.]+)", qa)
    X["linkage"][f"corp_alg_{t}"] = {"corps": int(m.group(1)), "median": float(m.group(2))}

# ---------------------------------------------------------------- access detail
a = pd.read_csv(os.path.join(PROC, "school_access_tiers.csv"), dtype={"NCESSCH": str, "CNTY": str})
t = a[a.tier != "Virtual or alternative"].copy()
X["access_tier_by_locale"] = {loc: {tier: int(n) for tier, n in g.tier.value_counts().items()}
                              for loc, g in t.groupby("locale4")}
ct = pd.read_csv(os.path.join(ROOT, "paper", "tables", "table7_access_by_county.csv"), dtype={"CNTY": str})
X["counties_no_calc"] = ct[ct.pct_students_no_calc >= 99.999].sort_values("NMCNTY")[
    ["NMCNTY", "schools", "students"]].to_dict("records")
X["counties_majority_no_calc"] = ct[(ct.pct_students_no_calc > 50)].sort_values(
    "pct_students_no_calc", ascending=False)[["NMCNTY", "schools", "students", "pct_students_no_calc"]].round(1).to_dict("records")
X["students_no_calc"] = int(t.loc[~t.calc_offered.astype(bool), "enr"].sum())
X["students_trad"] = int(t.enr.sum())
X["no_calc_but_dual"] = int((~t.calc_offered.astype(bool) & t.dual_any.astype(bool)).sum())
X["marion_no_calc_schools"] = int(((t.NMCNTY == "Marion County") & ~t.calc_offered.astype(bool)).sum())
X["marion_schools"] = int((t.NMCNTY == "Marion County").sum())
X["no_calc_frl_median"] = r(t.loc[~t.calc_offered.astype(bool), "frl_share_pooled"].median(), 3)
X["calc_frl_median"] = r(t.loc[t.calc_offered.astype(bool), "frl_share_pooled"].median(), 3)
X["no_calc_dc_median"] = r(t.loc[~t.calc_offered.astype(bool), "dc_share_pooled"].median(), 3)
X["calc_dc_median"] = r(t.loc[t.calc_offered.astype(bool), "dc_share_pooled"].median(), 3)
X["no_calc_enr_median"] = r(t.loc[~t.calc_offered.astype(bool), "enr"].median(), 0)
X["calc_enr_median"] = r(t.loc[t.calc_offered.astype(bool), "enr"].median(), 0)

json.dump(X, open(os.path.join(OUT, "stats_extra.json"), "w"), indent=1)
print("wrote paper/preprint/stats_extra.json")
print(json.dumps({k: X[k] for k in ["trend", "dc_share_quantiles", "math_remed_share_of_remed", "counties_no_calc",
                                     "students_no_calc", "no_calc_but_dual", "marion_no_calc_schools", "marion_schools",
                                     "no_calc_frl_median", "calc_frl_median", "no_calc_dc_median", "calc_dc_median",
                                     "no_calc_enr_median", "calc_enr_median", "locale_mix", "linkage"]}, indent=0)[:4000])
