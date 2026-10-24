#!/usr/bin/env python3
"""10_preprint.py — build the two-column RevTeX preprint (paper/preprint/preprint.tex → preprint.pdf).

Run from repo root after 03, 08 and 09:  python code/10_preprint.py
Every number is interpolated from paper/stats.json, paper/preprint/stats_extra.json or the pipeline tables
through @@key@@ placeholders; the script refuses to finish if any placeholder is left unfilled.
Requires revtex4-2 (CTAN) and mathpazo.
"""
import json
import os
import re
import subprocess

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRE = os.path.join(ROOT, "paper", "preprint")
TAB = os.path.join(ROOT, "paper", "tables")
S = json.load(open(os.path.join(ROOT, "paper", "stats.json")))
X = json.load(open(os.path.join(PRE, "stats_extra.json")))
AU = json.load(open(os.path.join(ROOT, "AUTHORS.json")))["authors"][0]


# ------------------------------------------------------------------------ formatting helpers
def f(x, d=3):
    return f"{x:.{d}f}"


def sg(x, d=3):
    return ("+" if x >= 0 else "$-$") + f"{abs(x):.{d}f}"


def pc(x, d=0):
    return f"{100 * x:.{d}f}\\%"


def n(x):
    return f"{int(round(x)):,}"


def pv(p):
    return "$p<0.001$" if p < 0.001 else f"$p={p:.3f}$"


def ci(m, d=3):
    return f"95\\% CI [{f(m['lo'], d)}, {f(m['hi'], d)}]"


G, C, R = S["models"]["gpa"], S["models"]["credits"], S["models"]["remed_rate"]
H, W, A, D, SM, SE = S["heterogeneity"], S["within_school"], S["access"], S["descriptives"], S["sample"], S["sensitivity"]
fq, L = A["by_frl_quartile"], A["by_locale"]
T = A["tiers"]
LK = X["linkage"]
TR = {t["cohort"]: t for t in X["trend"]}

V = {
    "AUTHOR": AU["name"], "ORCID": AU["orcid"], "EMAIL": AU["email"],
    "AFFIL": AU["affiliation"].replace("Independent Researcher, ", ""),
    "NSCH": n(SM["schools"]), "NSC": n(SM["school_cohorts"]), "NGRAD": n(SM["grads"]), "NINPUB": n(SM["inpub"]),
    "NSCBEFORE": n(SM["school_cohorts_before_controls"]), "MININPUB": str(SM["min_inpub"]),
    "DCMED": pc(D["dc_share_median"]), "DCP10": pc(D["dc_share_p10"]), "DCP90": pc(D["dc_share_p90"]),
    "DCQ25": pc(X["dc_share_quantiles"]["0.25"]), "DCQ75": pc(X["dc_share_quantiles"]["0.75"]),
    "DCWMEAN": pc(D["dc_share_weighted_mean"]), "GPAMEAN": f(D["gpa_weighted_mean"], 2),
    "CRMEAN": f(D["credits_weighted_mean"], 1), "REMMEAN": pc(D["remed_rate_weighted_mean"], 1),
    "FRLMED": pc(D["frl_share_median"]), "ALGMED": f(D["corp_early_alg_median"], 2),
    "CALCSHARE": pc(D["calc_offered_share_schools"]), "CORRDCFRL": f(D["corr_dc_frl"], 2).replace("-", "$-$"),
    "CORRDCGPA": f(D["corr_dc_gpa"], 2), "NDCZERO": str(X["n_dc_zero"]), "NDC90": str(X["n_dc_ge_90"]),
    "MATHREMSHARE": pc(X["math_remed_share_of_remed"]),
    "G1": sg(G["M1"]["b"]), "G2": sg(G["M2"]["b"]), "G3": sg(G["M3"]["b"]), "G4": sg(G["M4"]["b"]), "G5": sg(G["M5"]["b"]),
    "G3CI": ci(G["M3"]), "G2CI": ci(G["M2"]), "G5CI": ci(G["M5"]), "G4P": pv(G["M4"]["p"]), "G5P": pv(G["M5"]["p"]),
    "G3P": pv(G["M3"]["p"]), "G3SE": f(G["M3"]["se"], 4), "G1SE": f(G["M1"]["se"], 4),
    "C1": sg(C["M1"]["b"], 2), "C3": sg(C["M3"]["b"], 2), "C4": sg(C["M4"]["b"], 2), "C5": sg(C["M5"]["b"], 2),
    "C3CI": ci(C["M3"], 2), "C3P": pv(C["M3"]["p"]), "C4P": pv(C["M4"]["p"]), "C5P": pv(C["M5"]["p"]),
    "R1": sg(R["M1"]["b"], 4), "R3": sg(R["M3"]["b"], 4), "R3P": pv(R["M3"]["p"]), "R5": sg(R["M5"]["b"], 4),
    "R5P": pv(R["M5"]["p"]), "R1P": pv(R["M1"]["p"]),
    "ALGB": sg(G["M3_controls"]["alg10"]["b"]), "ALGP": pv(G["M3_controls"]["alg10"]["p"]),
    "CALCB": sg(G["M3_controls"]["calc"]["b"]), "CALCP": pv(G["M3_controls"]["calc"]["p"]),
    "FRLB": sg(G["M3_controls"]["frl10"]["b"]), "APB": sg(G["M3_controls"]["ap10"]["b"]),
    "ADVMB": sg(G["M3_controls"]["advm"]["b"]), "ADVMP": pv(G["M3_controls"]["advm"]["p"]),
    "R2M1": f(G["M1"]["r2"], 2), "R2M3": f(G["M3"]["r2"], 2), "R2M5": f(G["M5"]["r2"], 2),
    "ATTG": pc(S["attenuation_gpa_M1_to_M3"]), "ATTC": pc(S["attenuation_credits_M1_to_M3"]),
    "P1090": f(S["p10_p90_implied"]["dc_pp"], 0), "P1090G": f(S["p10_p90_implied"]["gpa"], 2),
    "P1090C": f(S["p10_p90_implied"]["credits"], 1),
    "HFRLG": sg(H["frl_hi"]["gpa"]["slope_group"]), "HFRLO": sg(H["frl_hi"]["gpa"]["slope_other"]),
    "HFRLP": pv(H["frl_hi"]["gpa"]["p_interaction"]), "HFRLCG": sg(H["frl_hi"]["credits"]["slope_group"], 2),
    "HFRLCO": sg(H["frl_hi"]["credits"]["slope_other"], 2), "HFRLCP": pv(H["frl_hi"]["credits"]["p_interaction"]),
    "HRURP": pv(H["rural"]["gpa"]["p_interaction"]), "HALGP": pv(H["alg_lo"]["gpa"]["p_interaction"]),
    "HCALCP": pv(H["calc"]["gpa"]["p_interaction"]),
    "WSC": n(W["school_cohorts"]), "WSCH": n(W["schools"]), "WGAP": f(W["gpa_gap_mean"], 2),
    "WCGAP": f(W["credit_gap_mean"], 1), "WPOS": pc(W["share_positive_gap"]),
    "WSLOPE": f(W["gap_slope_dc10"], 3), "WSLOPEP": pv(W["gap_slope_p"]), "WNODC": sg(W["nodc_gpa_slope_dc10"], 3),
    "SENSGLO": sg(S["sensitivity_range_gpa"][0], 4), "SENSGHI": sg(S["sensitivity_range_gpa"][1], 4),
    "SENSCLO": sg(S["sensitivity_range_credits"][0], 2), "SENSCHI": sg(S["sensitivity_range_credits"][1], 2),
    "SUNW": sg(SE["unweighted"]["gpa"]["b"], 4), "SMIN30": sg(SE["min30"]["gpa"]["b"], 4),
    "SMIN30P": pv(SE["min30"]["gpa"]["p"]), "SNOVIRTC": sg(SE["no_virtual"]["credits"]["b"], 2),
    "SNOVIRTCP": pv(SE["no_virtual"]["credits"]["p"]), "SNOVIRTG": sg(SE["no_virtual"]["gpa"]["b"], 4),
    "S2019": sg(SE["with2019"]["gpa"]["b"], 4), "SHSALG": sg(SE["hs_alg"]["gpa"]["b"], 4),
    "S2024": sg(SE["only2024"]["gpa"]["b"], 4), "S2024P": pv(SE["only2024"]["gpa"]["p"]),
    "ACRDC": n(A["schools_crdc_2324"]), "ATRAD": n(A["traditional_schools"]), "AVALT": n(A["virtual_alt_schools"]),
    "ANOCALC": pc(A["no_calc_share_schools"]), "ANOCALCN": n(A["traditional_schools"] * A["no_calc_share_schools"]),
    "ANOCALCST": pc(A["no_calc_share_students"]), "ANOCALCSTN": n(X["students_no_calc"]), "ATRADST": n(X["students_trad"]),
    "ANODUAL": pc(A["no_dual_share_schools"]),
    "TNONE": n(T["No dual enrollment reported"]["schools"]), "TNONEST": n(T["No dual enrollment reported"]["students"]),
    "TTHIN": n(T["Thin pathway: no calculus and low uptake"]["schools"]),
    "TTHINST": n(T["Thin pathway: no calculus and low uptake"]["students"]),
    "TNOCALC": n(T["Dual credit, but no calculus"]["schools"]), "TNOCALCST": n(T["Dual credit, but no calculus"]["students"]),
    "TOK": n(T["Dual credit and calculus"]["schools"]), "TOKST": n(T["Dual credit and calculus"]["students"]),
    "Q1NC": f(fq["Q1 lowest"]["no_calculus_pct_schools"], 0), "Q2NC": f(fq["Q2"]["no_calculus_pct_schools"], 0),
    "Q3NC": f(fq["Q3"]["no_calculus_pct_schools"], 0), "Q4NC": f(fq["Q4 highest"]["no_calculus_pct_schools"], 0),
    "Q1DC": pc(fq["Q1 lowest"]["median_dc_share"]), "Q4DC": pc(fq["Q4 highest"]["median_dc_share"]),
    "CITYNC": f(L["City"]["no_calculus_pct_schools"], 0), "CITYND": f(L["City"]["no_dual_pct_schools"], 0),
    "RURNC": f(L["Rural"]["no_calculus_pct_schools"], 0), "RURND": f(L["Rural"]["no_dual_pct_schools"], 1),
    "SUBNC": f(L["Suburb"]["no_calculus_pct_schools"], 0), "TOWNNC": f(L["Town"]["no_calculus_pct_schools"], 0),
    "CITYTHIN": f(L["City"]["thin_or_none_pct_students"], 1), "RURTHIN": f(L["Rural"]["thin_or_none_pct_students"], 1),
    "NCOUNTY": str(A["counties"]), "NCNOCALC": str(A["counties_no_calc_anywhere"]),
    "NCMAJ": str(A["counties_majority_no_calc"]),
    "CNOCALCLIST": ", ".join(c["NMCNTY"].replace(" County", "") for c in X["counties_no_calc"]),
    "MARIONNC": str(X["marion_no_calc_schools"]), "MARION": str(X["marion_schools"]),
    "NCFRL": pc(X["no_calc_frl_median"]), "CFRL": pc(X["calc_frl_median"]), "NCDC": pc(X["no_calc_dc_median"]),
    "CDC": pc(X["calc_dc_median"]), "NCENR": n(X["no_calc_enr_median"]), "CENR": n(X["calc_enr_median"]),
    "NOCALCDUAL": str(X["no_calc_but_dual"]), "CALCCHANGED": str(LK["calc_changed"]),
    "LK19": str(LK["2019"]["schools"]), "LK19L": f"{LK['2019']['pct']:.1f}", "LK24": str(LK["2024"]["schools"]),
    "LKALL": n(LK["school_cohorts_all"]), "LKPUB": n(LK["school_cohorts_public"]),
    "LKPANEL": n(LK["panel_school_cohorts"]), "LKPANELS": n(LK["panel_schools"]),
    "CRDCMATCH": f"{LK['crdc_match_pct']:.1f}", "CORPALGPCT": f"{LK['corp_alg_pct']:.1f}",
    "HSALGPCT": f"{LK['hs_alg_pct']:.1f}", "CCDHS": str(LK["ccd_hs"]),
    "CRDC22G12": str(LK["crdc_2021-22"]["g12"]), "CRDC24G12": str(LK["crdc_2023-24"]["g12"]),
    "CORPS22": str(LK["corp_alg_2021-22"]["corps"]), "CORPS24": str(LK["corp_alg_2023-24"]["corps"]),
    "CORPMED22": f(LK["corp_alg_2021-22"]["median"], 2), "CORPMED24": f(LK["corp_alg_2023-24"]["median"], 2),
    "TR19DC": pc(TR[2019]["dc_share"]), "TR24DC": pc(TR[2024]["dc_share"]), "TR19GPA": f(TR[2019]["gpa"], 2),
    "TR21GPA": f(TR[2021]["gpa"], 2), "TR24GPA": f(TR[2024]["gpa"], 2), "TR19REM": pc(TR[2019]["remed"], 1),
    "TR21REM": pc(TR[2021]["remed"], 1), "TR24REM": pc(TR[2024]["remed"], 1), "TR19INP": pc(TR[2019]["inpub_rate"]),
    "TR24INP": pc(TR[2024]["inpub_rate"]), "TR24CR": f(TR[2024]["credits"], 1), "TR19CR": f(TR[2019]["credits"], 1),
    "MECHC": f(0.1 * 10, 1),
    "REPO": "https://github.com/OthnyLight/in-dual-credit-math",
}


# ------------------------------------------------------------------------ author-approved text, single source: 06_manuscript.js
JS = open(os.path.join(ROOT, "code", "06_manuscript.js"), encoding="utf-8").read()


def js_par(start):
    m = re.search(r'P\("(' + re.escape(start) + r'[^"]*)"\)', JS)
    assert m, start
    t = m.group(1).replace("\\'", "'")
    t = re.sub(r"\*\*[^*]+\*\* ?", "", t)          # drop **Label.** prefixes
    t = t.replace("Section 6.6", "Sec.~\\ref{sec:access}").replace("%", "\\%").replace("&", "\\&")
    return t


V["M118A"] = js_par("This question comes from my own classroom.")
V["M118B"] = js_par("My experience teaching M118")
V["COMPETING"] = js_par("**Competing interests.**")
V["FUNDING"] = js_par("**Funding.**")
V["AIUSE"] = js_par("**Use of AI tools.**")
V["CREDIT"] = AU["name"] + ": " + ", ".join(AU["roles"]).replace("Writing - ", "Writing -- ") + "."


# ------------------------------------------------------------------------ tables
def tabular(cols, header, rows, note=None, star=False, caption="", label="", size="\\footnotesize"):
    env = "table*" if star else "table"
    out = [f"\\begin{{{env}}}[t]", f"\\caption{{{caption}}}", f"\\label{{{label}}}", size,
           "\\begin{adjustbox}{max width=\\linewidth}",
           f"\\begin{{tabular}}{{{cols}}}", "\\hline\\hline", " & ".join(header) + " \\\\", "\\hline"]
    for r in rows:
        out.append("\\hline" if r == "---" else " & ".join(str(c) for c in r) + " \\\\")
    out += ["\\hline\\hline", "\\end{tabular}", "\\end{adjustbox}"]
    if note:
        out.append(f"\\par\\smallskip\\parbox{{{'0.92' if star else '0.98'}\\linewidth}}{{\\scriptsize {note}}}")
    out.append(f"\\end{{{env}}}")
    return "\n".join(out)


def star(p):
    return "^{***}" if p < 0.001 else "^{**}" if p < 0.01 else "^{*}" if p < 0.05 else ""


TB = {}
TB["T_SAMPLE"] = tabular(
    "lrr", ["Step", "School-cohorts", "Schools"],
    [["CHE school rows, cohorts 2019 and 2021--2024", V["LKALL"], "--"],
     ["\\quad with a numeric (public) IDOE school number", V["LKPUB"], "--"],
     ["\\quad matched to CCD; correctional facilities removed", V["LKPANEL"], V["LKPANELS"]],
     ["Cohorts 2021--2024, outcome and exposure observed, $\\geq$" + V["MININPUB"] + " enrollees", V["NSCBEFORE"], "--"],
     ["\\quad and all controls observed (analytic sample)", V["NSC"], V["NSCH"]]],
    note="Name-based linkage of pre-2024 CHE files to IDOE numbers succeeded for " + V["LK19L"] +
         "\\% of 2019 rows and 100\\% of 2024 rows; unlinked rows are mainly nonpublic, closed or renamed schools. "
         "Matches to CRDC: " + V["CRDCMATCH"] + "\\% of panel school-cohorts.",
    caption="Construction of the analytic sample.", label="tab:sample")

DL = {"dc_share": "Dual-credit share $s$", "frl_share": "Free/reduced-lunch share", "ap_pass_share": "AP-pass share",
      "corp_early_alg": "Corporation early Algebra I $a^{\\rm corp}$", "hs_alg_rate": "High-school Algebra I $a^{\\rm hs}$ (capped)",
      "calc": "Offers calculus", "advm": "Offers advanced mathematics", "inpub_rate": "In-state public college-going",
      "gpa": "First-year GPA $\\bar G$", "credits": "First-year credits $\\bar C$", "remed_rate": "Share needing remediation $\\rho$",
      "grads": "Graduates per cohort (unweighted)"}
rows = []
for k, lab in DL.items():
    d = X["desc"][k]
    dd = 1 if k == "grads" else 3
    rows.append([lab, f(d["mean"], dd), f(d["sd"], dd), f(d["min"], dd if k != "grads" else 0),
                 f(d["max"], dd if k != "grads" else 0)])
TB["T_DESC"] = tabular("lrrrr", ["Variable", "Mean", "SD", "Min", "Max"], rows,
                       note="Analytic sample (" + V["NSC"] + " school-cohorts). Means and SDs weighted by Indiana public "
                            "enrollees except graduates. Shares are fractions.",
                       caption="Summary statistics.", label="tab:desc")

t1 = pd.read_csv(os.path.join(TAB, "table1_descriptives_by_dc_tercile.csv"))
TB["T_TERC"] = tabular(
    "lrrr", ["", "Low", "Middle", "High"],
    [["School-cohorts"] + [n(v) for v in t1.school_cohorts],
     ["Dual-credit share"] + [pc(v) for v in t1.dc_share],
     ["Free/reduced lunch"] + [pc(v) for v in t1.frl_share],
     ["AP-pass share"] + [pc(v) for v in t1.ap_pass_share],
     ["Early Algebra I (corp.)"] + [f(v, 2) for v in t1.corp_early_alg],
     ["Offers calculus"] + [pc(v) for v in t1.calc_offered],
     ["Rural"] + [pc(v) for v in t1.rural],
     ["Graduates"] + [n(v) for v in t1.grads],
     ["First-year GPA"] + [f(v, 2) for v in t1.gpa],
     ["First-year credits"] + [f(v, 1) for v in t1.credits],
     ["Needing remediation"] + [pc(v, 1) for v in t1.remed_rate]],
    note="Medians within terciles of dual-credit share (shares of schools for calculus and rural).",
    caption="School characteristics by tercile of dual-credit share.", label="tab:terc")

mrows = []
names = {"M1": "M1 cohort only", "M2": "M2 + poverty, AP, size, locale", "M3": "M3 + Algebra I, math offerings",
         "M4": "M4 + in-state college-going", "M5": "M5 school fixed effects"}
for k in ["M1", "M2", "M3", "M4", "M5"]:
    cells = [names[k]]
    for y, d in [("gpa", 4), ("credits", 3), ("remed_rate", 4)]:
        m = S["models"][y][k]
        cells.append(f"${m['b']:+.{d}f}{star(m['p'])}$ ({m['se']:.{d}f})")
    cells.append(f"{S['models']['gpa'][k]['r2']:.2f}")
    mrows.append(cells)
TB["T_MAIN"] = tabular(
    "lrrrr", ["Specification", "GPA", "Credits", "Remediation", "$R^2_{\\rm GPA}$"], mrows, star=True,
    note="Coefficient $\\beta$ on dual-credit share in tens of percentage points, Eq.~(\\ref{eq:main}); cluster-robust "
         "standard errors (by school) in parentheses. $N=" + V["NSC"] + "$ school-cohorts, " + V["NSCH"] +
         " clusters, weights = Indiana public enrollees. All models include cohort indicators. $^{*}p<0.05$, "
         "$^{**}p<0.01$, $^{***}p<0.001$. GPA and credit outcomes include dual-credit coursework recorded before "
         "enrollment (Sec.~\\ref{sec:overlap}); remediation does not.",
    caption="Association between school dual-credit share and graduates' first-year outcomes.", label="tab:main")

hrows = []
for k, lab in [("frl_hi", "High-poverty (FRL $\\geq$ median)"), ("rural", "Rural"),
               ("alg_lo", "Below-median early Algebra I"), ("calc", "Offers calculus")]:
    for y, d in [("gpa", 3), ("credits", 2)]:
        e = H[k][y]
        hrows.append([f"{lab}: {'GPA' if y == 'gpa' else 'credits'}", f"${e['slope_group']:+.{d}f}$ ({e['se_group']:.{d}f})",
                      f"${e['slope_other']:+.{d}f}$ ({e['se_other']:.{d}f})", f"${e['interaction']:+.{d}f}$",
                      f"{e['p_interaction']:.2f}"])
TB["T_HET"] = tabular("lrrrr", ["Group / outcome", "In group", "Others", "Diff.", "$p$"], hrows,
                      note="Slopes per 10 points of dual-credit share from M3 with an interaction, Eq.~(\\ref{eq:het}). "
                           "Group SEs from the full covariance matrix.",
                      caption="Heterogeneity of the association.", label="tab:het")

srows = [[f"{s['dc_share_med'] * 100:.0f}\\%", n(s["n"]), f(s["dc_gpa"], 2), f(s["nodc_gpa"], 2),
          f(s["dc_gpa"] - s["nodc_gpa"], 2), f(s["dc_credits"], 1), f(s["nodc_credits"], 1)] for s in X["within_sextiles"]]
TB["T_WITHIN"] = tabular("rrrrrrr", ["$s$", "$N$", "$G^{\\rm DC}$", "$G^{\\rm no}$", "Gap", "$C^{\\rm DC}$", "$C^{\\rm no}$"],
                         srows, note="Sextiles of school dual-credit share (median shown), school-cohorts where both groups "
                                     "have $\\geq$10 Indiana public enrollees; enrollee-weighted means.",
                         caption="First-year outcomes of dual-credit earners and non-earners within the same schools.",
                         label="tab:within")

lab = {"main": "Main specification (M3)", "no_virtual": "Exclude virtual schools", "unweighted": "Unweighted",
       "min30": "Only school-cohorts with $\\geq$30 enrollees", "hs_alg": "High-school Algebra I measure",
       "both_alg": "Both Algebra I measures", "with2019": "Add 2019 cohort", "only2024": "2024 cohort only"}
TB["T_SENS"] = tabular(
    "lrrr", ["Check", "GPA", "Credits", "$N$"],
    [[lab[k], f"${SE[k]['gpa']['b']:+.4f}{star(SE[k]['gpa']['p'])}$ ({SE[k]['gpa']['se']:.4f})",
      f"${SE[k]['credits']['b']:+.3f}{star(SE[k]['credits']['p'])}$ ({SE[k]['credits']['se']:.3f})",
      n(SE[k]["gpa"]["n"])] for k in lab],
    note="Each row re-estimates M3 under one change. Cluster-robust SEs in parentheses.",
    caption="Sensitivity of the main estimate.", label="tab:sens")

tiers = [("Dual credit and calculus", "Dual credit and calculus"), ("Dual credit, but no calculus", "Dual credit, no calculus"),
         ("Thin pathway: no calculus and low uptake", "Thin pathway"), ("No dual enrollment reported", "No dual enrollment")]
tot_s = sum(T[k]["schools"] for k, _ in tiers)
tot_n = sum(T[k]["students"] for k, _ in tiers)
TB["T_TIERS"] = tabular("lrrrr", ["Tier", "Schools", "\\%", "Students", "\\%"],
                        [[l, n(T[k]["schools"]), pc(T[k]["schools"] / tot_s, 1), n(T[k]["students"]),
                          pc(T[k]["students"] / tot_n, 1)] for k, l in tiers] + ["---", ["Total", n(tot_s), "", n(tot_n), ""]],
                        note="Traditional public high schools matched to CRDC 2023-24; enrollment from CRDC 2023-24. "
                             + V["AVALT"] + " virtual or alternative schools excluded.",
                        caption="Access tiers, Indiana public high schools.", label="tab:tiers")

t5 = pd.read_csv(os.path.join(TAB, "table5_access_by_locale.csv"))
t6 = pd.read_csv(os.path.join(TAB, "table6_access_by_poverty.csv"))
arows = [[r.locale4, n(r.schools), n(r.students), f(r.no_calculus_pct_schools, 0) + "\\%", f(r.no_dual_pct_schools, 0) + "\\%",
          f(r.thin_or_none_pct_students, 1) + "\\%", pc(r.median_dc_share)] for r in t5.itertuples()]
arows += ["---"] + [[f"FRL {r.frl_q}", n(r.schools), "--", f(r.no_calculus_pct_schools, 0) + "\\%", "--", "--",
                     pc(r.median_dc_share)] for r in t6.itertuples()]
TB["T_ACCESS"] = tabular("lrrrrrr", ["Group", "Schools", "Students", "No calc.", "No DE", "Thin/none (st.)", "Med.\\ $s$"],
                         arows, star=True,
                         note="No calc.: no calculus section in CRDC 2021-22 or 2023-24. No DE: no dual enrollment in either "
                              "year. Thin/none: share of students in schools with no dual enrollment or a thin pathway. "
                              "Med.\\ $s$: median pooled dual-credit share (cohorts 2021--2024). FRL quartiles of pooled "
                              "free/reduced-lunch share.",
                         caption="Access to calculus and dual enrollment by locale and school poverty.", label="tab:access")

TB["T_COUNTY"] = tabular("lrrr", ["County", "Schools", "Students", "No calc.\\ (\\% st.)"],
                         [[c["NMCNTY"].replace(" County", ""), n(c["schools"]), n(c["students"]),
                           f"{c['pct_students_no_calc']:.0f}\\%"] for c in X["counties_majority_no_calc"]],
                         note="Counties where most students in traditional public high schools attend a school with no "
                              "calculus in either CRDC year.",
                         caption="Counties where most public high school students lack calculus.", label="tab:county")

FM = X["full_models"]
coef_lab = [("dc10", "Dual-credit share (per 10 pts)"), ("frl10", "FRL share (per 10 pts)"),
            ("ap10", "AP-pass share (per 10 pts)"), ("lgr", "log graduates"), ("alg10", "Early Algebra I (per 0.1)"),
            ("calc", "Offers calculus"), ("advm", "Offers advanced math"),
            ("C(locale4)[T.Rural]", "Locale: rural"), ("C(locale4)[T.Suburb]", "Locale: suburb"),
            ("C(locale4)[T.Town]", "Locale: town"), ("inpub10", "In-state college-going (per 10 pts)")]
crow = []
for k, l in coef_lab:
    row = [l]
    for y, mk, d in [("gpa", "M3", 4), ("gpa", "M4", 4), ("credits", "M3", 3), ("remed_rate", "M3", 4)]:
        e = FM[y][mk].get(k)
        row.append("--" if e is None else f"${e['b']:+.{d}f}{star(e['p'])}$ ({e['se']:.{d}f})")
    crow.append(row)
crow += ["---", ["$R^2$"] + [f"{FM[y][mk]['_r2']:.2f}" for y, mk in [("gpa", "M3"), ("gpa", "M4"), ("credits", "M3"), ("remed_rate", "M3")]]]
TB["T_FULL"] = tabular("lrrrr", ["", "GPA (M3)", "GPA (M4)", "Credits (M3)", "Remed.\\ (M3)"], crow, star=True,
                       note="Reference locale: city. Cohort indicators included, not shown. Cluster-robust SEs in "
                            "parentheses. $^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.",
                       caption="Full coefficient estimates.", label="tab:full")

VARS = [("$s_{jt}$", "Graduates earning dual credit from an Indiana public college $\\div$ graduates", "CHE"),
        ("$\\bar G_{jt}$", "Average first-year GPA, Indiana public enrollees", "CHE"),
        ("$\\bar C_{jt}$", "Average first-year credits earned, Indiana public enrollees", "CHE"),
        ("$\\rho_{jt}$", "Enrollees needing remediation $\\div$ Indiana public enrollees", "CHE"),
        ("$w_{jt}$", "Indiana public enrollees (regression weight)", "CHE"),
        ("$f_{jt}$", "Free/reduced-lunch graduates $\\div$ graduates", "CHE"),
        ("$p_{jt}$", "Graduates passing an AP exam $\\div$ graduates", "CHE"),
        ("$a^{\\rm corp}_{c(j)}$", "Corporation 7th--8th grade Algebra I enrollment $\\div$ 8th-grade membership", "CRDC, CCD"),
        ("$a^{\\rm hs}_{j}$", "Grades 9--12 Algebra I enrollment $\\div$ 9th-grade membership", "CRDC, CCD"),
        ("$k_j$, $m_j$", "Any calculus / advanced-mathematics section", "CRDC"),
        ("$\\ell_j$", "NCES locale (city, suburb, town, rural)", "EDGE")]
TB["T_VARS"] = "\n".join(["\\begin{table*}[t]", "\\caption{Variable definitions and sources.}", "\\label{tab:vars}",
                          "\\footnotesize", "\\begin{tabular}{lp{0.62\\linewidth}l}", "\\hline\\hline",
                          "Symbol & Definition & Source \\\\", "\\hline"] +
                         [" & ".join(v) + " \\\\" for v in VARS] + ["\\hline\\hline", "\\end{tabular}", "\\end{table*}"])

# ------------------------------------------------------------------------ references (ordered by first citation)
REFS = {
    "cherelease": "Indiana Commission for Higher Education, \\textit{Indiana College Core update} [press release] (Indianapolis, IN, 13 October 2026), \\url{https://www.in.gov/che/Press-Releases/261013_RELEASE_ICC\\%20Update.pdf}.",
    "icc": "Indiana Capital Chronicle, \\textit{Indiana higher ed commission to review dual-college credit accessibility} (11 September 2026), \\url{https://indianacapitalchronicle.com/2026/09/11/indiana-higher-ed-commission-to-review-dual-college-credit-accessibility/}.",
    "an2013": "B. P. An, The impact of dual enrollment on college degree attainment: Do low-SES students benefit?, \\textit{Educ. Eval. Policy Anal.} \\textbf{35}, 57 (2013), \\href{https://doi.org/10.3102/0162373712461933}{doi:10.3102/0162373712461933}.",
    "karp2007": "M. M. Karp, J. C. Calcagno, K. L. Hughes, D. W. Jeong, and T. R. Bailey, \\textit{The Postsecondary Achievement of Participants in Dual Enrollment: An Analysis of Student Outcomes in Two States} (Community College Research Center, Teachers College, Columbia University, New York, 2007).",
    "speroni2011": "C. Speroni, \\textit{Determinants of Students' Success: The Role of Advanced Placement and Dual Enrollment Programs} (National Center for Postsecondary Research, New York, 2011).",
    "giani2014": "M. Giani, C. Alexander, and P. Reyes, Exploring variation in the impact of dual-credit coursework on postsecondary outcomes: A quasi-experimental analysis of Texas students, \\textit{High Sch. J.} \\textbf{97}, 200 (2014), \\href{https://doi.org/10.1353/hsj.2014.0007}{doi:10.1353/hsj.2014.0007}.",
    "allen2012": "D. Allen and M. Dadgar, Does dual enrollment increase students' success in college? Evidence from a quasi-experimental analysis of dual enrollment in New York City, \\textit{New Dir. High. Educ.} \\textbf{2012}(158), 11 (2012), \\href{https://doi.org/10.1002/he.20010}{doi:10.1002/he.20010}.",
    "miller2017": "T. Miller, H. Kosiewicz, E. Wang, E. Marwah, S. Delhommer, and L. Daugherty, \\textit{Dual Credit Education in Texas: Interim Report} (RAND Corporation, Santa Monica, CA, 2017), \\href{https://doi.org/10.7249/RR2043}{doi:10.7249/RR2043}.",
    "lee2022": "J. Lee, F. Fernandez, H. Ro, and H. Suh, Does dual enrollment influence high school graduation, college enrollment, choice, and persistence?, \\textit{Res. High. Educ.} \\textbf{63}, 825 (2022), \\href{https://doi.org/10.1007/s11162-021-09667-3}{doi:10.1007/s11162-021-09667-3}.",
    "wwc2017": "What Works Clearinghouse, \\textit{Transition to College Intervention Report: Dual Enrollment Programs} (Institute of Education Sciences, U.S. Department of Education, Washington, DC, 2017).",
    "taylor2015": "J. L. Taylor, Accelerating pathways to college: The (in)equitable effects of community college dual credit, \\textit{Community Coll. Rev.} \\textbf{43}, 355 (2015), \\href{https://doi.org/10.1177/0091552115594880}{doi:10.1177/0091552115594880}.",
    "fink2017": "J. Fink, D. Jenkins, and T. Velasco, \\textit{What Happens to Students Who Take Community College Dual Enrollment Courses in High School?} (Community College Research Center, Teachers College, Columbia University, New York, 2017).",
    "che2016": "Indiana Commission for Higher Education, \\textit{College Readiness Report Supplement: A Closer Look at Dual Credit Students} (Indianapolis, IN, May 2016).",
    "long2012": "M. C. Long, D. Conger, and P. Iatarola, Effects of high school course-taking on secondary and postsecondary success, \\textit{Am. Educ. Res. J.} \\textbf{49}, 285 (2012), \\href{https://doi.org/10.3102/0002831211431952}{doi:10.3102/0002831211431952}.",
    "clotfelter2015": "C. T. Clotfelter, H. F. Ladd, and J. L. Vigdor, The aftermath of accelerating algebra: Evidence from district policy initiatives, \\textit{J. Hum. Resour.} \\textbf{50}, 159 (2015), \\href{https://doi.org/10.1353/jhr.2015.0005}{doi:10.1353/jhr.2015.0005}.",
    "domina2015": "T. Domina, A. McEachin, A. Penner, and E. Penner, Aiming high and falling short: California's eighth-grade algebra-for-all effort, \\textit{Educ. Eval. Policy Anal.} \\textbf{37}, 275 (2015), \\href{https://doi.org/10.3102/0162373714543685}{doi:10.3102/0162373714543685}.",
    "bailey2010": "T. Bailey, D. W. Jeong, and S.-W. Cho, Referral, enrollment, and completion in developmental education sequences in community colleges, \\textit{Econ. Educ. Rev.} \\textbf{29}, 255 (2010), \\href{https://doi.org/10.1016/j.econedurev.2009.09.002}{doi:10.1016/j.econedurev.2009.09.002}.",
    "chedata": "Indiana Commission for Higher Education, \\textit{College Readiness and College-Going Datasets, High School Graduating Cohorts 2019 and 2021--2024} [data sets] (Indianapolis, IN, 2021--2026), \\url{https://www.in.gov/che/college-going-reports/}.",
    "cheguide": "Indiana Commission for Higher Education, \\textit{College Readiness Report User Guide} (Indianapolis, IN), \\url{https://www.in.gov/che/college-going-reports/}.",
    "crdc": "U.S. Department of Education, Office for Civil Rights, \\textit{Civil Rights Data Collection, 2021--22 and 2023--24 Public-Use Data Files} (Washington, DC, 2025--2026), \\url{https://civilrightsdata.ed.gov/data}.",
    "ccd": "National Center for Education Statistics, \\textit{Common Core of Data: Public Elementary/Secondary School Universe Survey (Directory, 2023--24; Membership, 2021--22 and 2023--24)} (U.S. Department of Education, Washington, DC), \\url{https://nces.ed.gov/ccd/}.",
    "edge": "National Center for Education Statistics, \\textit{Education Demographic and Geographic Estimates (EDGE): Public School Geocodes, 2023--24} (U.S. Department of Education, Washington, DC), \\url{https://nces.ed.gov/programs/edge/}.",
    "census": "U.S. Census Bureau, \\textit{2023 Cartographic Boundary Files: Counties, 1:500,000} (Washington, DC).",
    "seabold2010": "S. Seabold and J. Perktold, Statsmodels: Econometric and statistical modeling with Python, in \\textit{Proceedings of the 9th Python in Science Conference} (2010), p. 92, \\href{https://doi.org/10.25080/Majora-92bf1922-011}{doi:10.25080/Majora-92bf1922-011}.",
    "mckinney2010": "W. McKinney, Data structures for statistical computing in Python, in \\textit{Proceedings of the 9th Python in Science Conference} (2010), p. 56, \\href{https://doi.org/10.25080/Majora-92bf1922-00a}{doi:10.25080/Majora-92bf1922-00a}.",
    "hunter2007": "J. D. Hunter, Matplotlib: A 2D graphics environment, \\textit{Comput. Sci. Eng.} \\textbf{9}, 90 (2007), \\href{https://doi.org/10.1109/MCSE.2007.55}{doi:10.1109/MCSE.2007.55}.",
    "repo": "O. I. Sa'anga, \\textit{Dual-Credit Mathematics as a Readiness Lever: Indiana School-Level Analysis and Access Atlas}, version 0.1.0 (2026), \\url{https://github.com/OthnyLight/in-dual-credit-math}.",
}

# ------------------------------------------------------------------------ the document
TEX = open(os.path.join(ROOT, "code", "preprint_template.tex"), encoding="utf-8").read()
for k, v in TB.items():
    TEX = TEX.replace(f"@@{k}@@", v)
for k, v in V.items():
    TEX = TEX.replace(f"@@{k}@@", v)
left = re.findall(r"@@[A-Z0-9_]+@@", TEX)
assert not left, f"unfilled placeholders: {sorted(set(left))}"
order = []
for grp in re.findall(r"\\cite\{([^}]+)\}", TEX):
    for k in grp.split(","):
        k = k.strip()
        if k not in order:
            order.append(k)
missing = [k for k in order if k not in REFS]
assert not missing, f"cited but undefined: {missing}"
unused = [k for k in REFS if k not in order]
assert not unused, f"defined but never cited: {unused}"
bib = "\\begin{thebibliography}{99}\n" + "\n".join(f"\\bibitem{{{k}}} {REFS[k]}" for k in order) + "\n\\end{thebibliography}"
TEX = TEX.replace("%%BIBLIOGRAPHY%%", bib)
open(os.path.join(PRE, "preprint.tex"), "w", encoding="utf-8").write(TEX)
for _ in range(3):
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "preprint.tex"], cwd=PRE,
                       capture_output=True, text=True)
if r.returncode != 0:
    print(r.stdout[-4000:])
    raise SystemExit("pdflatex failed")
log = open(os.path.join(PRE, "preprint.log"), encoding="latin-1").read()
print("undefined refs:", len(re.findall(r"undefined", log)), "| overfull boxes:", len(re.findall(r"Overfull \\hbox", log)))
print("wrote paper/preprint/preprint.pdf")
