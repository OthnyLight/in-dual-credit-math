#!/usr/bin/env python3
"""09_pbi_figures.py — Power BI–style figures for the preprint (vector PDF + PNG preview).

Run from repo root after 03_analysis.py and 08_preprint_stats.py:  python code/09_pbi_figures.py
Style: report canvas #F3F2F1, white visual cards, Segoe-like sans (Open Sans, OFL), Power BI default
theme colours (#118DFF, #E66C37, #12239E), dotted light gridlines, data labels on marks.
"""
import json
import os
import warnings

import geopandas as gpd
import matplotlib
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(ROOT, "paper", "preprint", "figures")
os.makedirs(OUT, exist_ok=True)
S = json.load(open(os.path.join(ROOT, "paper", "stats.json")))
X = json.load(open(os.path.join(ROOT, "paper", "preprint", "stats_extra.json")))

for f in os.listdir(os.path.join(ROOT, "code", "fonts")):
    if f.endswith(".ttf"):
        fm.fontManager.addfont(os.path.join(ROOT, "code", "fonts", f))
FONT = "Open Sans"

CANVAS, CARD, BORDER = "#F3F2F1", "#FFFFFF", "#E1DFDD"
INK, INK2, INK3, GRID = "#252423", "#605E5C", "#8A8886", "#E1DFDD"
B1, O1, N1 = "#118DFF", "#E66C37", "#12239E"
SEQ = ["#E8F3FF", "#B9DCFF", "#7DBEFF", "#3E9CFF", "#0B6FD6", "#08488C"]
plt.rcParams.update({
    "font.family": FONT, "font.size": 7, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.facecolor": CARD, "figure.facecolor": CANVAS, "savefig.facecolor": CANVAS,
    "pdf.fonttype": 42, "ps.fonttype": 42, "axes.titlesize": 8, "legend.fontsize": 6.5,
    "xtick.major.size": 0, "ytick.major.size": 0, "axes.linewidth": 0.6,
})
COL, FULL = 3.4, 7.0


def card(fig, ax, title, subtitle=None, ybounds=None):
    """Draw a white Power BI visual card behind an axes, with title (and subtitle) in its header.
    Header sizes are in inches so they hold at any figure height; ybounds forces a shared card height."""
    fig.canvas.draw()
    W, Hh = fig.get_size_inches()
    bb = ax.get_tightbbox(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
    x0, x1 = bb.x0 - 0.07 / W, bb.x1 + 0.07 / W
    y0, top = (bb.y0 - 0.05 / Hh, bb.y1) if ybounds is None else ybounds
    y1 = top + ((0.34 if subtitle else 0.22) / Hh)
    fig.patches.append(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=0.006",
                                      transform=fig.transFigure, facecolor=CARD, edgecolor=BORDER, lw=0.6,
                                      zorder=-10))
    fig.text(x0 + 0.08 / W, y1 - 0.07 / Hh, title, fontsize=8, fontweight="bold", color=INK, va="top", ha="left")
    if subtitle:
        fig.text(x0 + 0.08 / W, y1 - 0.20 / Hh, subtitle, fontsize=6.2, color=INK3, va="top", ha="left")


def shared_y(fig, axes):
    fig.canvas.draw()
    W, Hh = fig.get_size_inches()
    bbs = [a.get_tightbbox(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted()) for a in axes]
    return (min(b.y0 for b in bbs) - 0.05 / Hh, max(b.y1 for b in bbs))


def grid(ax, axis="y"):
    ax.grid(axis=axis, color=GRID, lw=0.6, ls=(0, (1, 2)))
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".pdf"), bbox_inches="tight", pad_inches=0.04)
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=220, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    print("wrote", name)


def legend(ax, items, loc="upper left", anchor=(0, 1.02), ncol=2):
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker="o", ls="", color=c, ms=5, label=l) for l, c in items]
    ax.legend(handles=h, loc=loc, bbox_to_anchor=anchor, ncol=ncol, frameon=False, handletextpad=0.3,
              columnspacing=1.0, borderaxespad=0)


fq = S["access"]["by_frl_quartile"]
TR = pd.DataFrame(X["trend"])

# =========================================================== Fig 1: overview dashboard (KPI cards + trends)
fig = plt.figure(figsize=(FULL, 3.15))
kpis = [(f"{S['sample']['schools']}", "Public high schools", "in analytic sample"),
        (f"{S['sample']['school_cohorts']:,}", "School-cohorts", "classes of 2021–2024"),
        (f"{S['sample']['inpub'] / 1000:.1f}K", "In-state public enrollees", "outcome population"),
        (f"{100 * S['descriptives']['dc_share_median']:.0f}%", "Median dual-credit share", "graduates per school"),
        (f"{100 * S['access']['no_calc_share_schools']:.0f}%", "Schools with no calculus", "CRDC 2021-22 or 2023-24")]
w, gap, x = (1 - 0.02 * 2 - 0.015 * 4) / 5, 0.015, 0.02
for big, lab, sub in kpis:
    fig.patches.append(FancyBboxPatch((x, 0.70), w, 0.27, boxstyle="round,pad=0,rounding_size=0.008",
                                      transform=fig.transFigure, facecolor=CARD, edgecolor=BORDER, lw=0.6))
    fig.text(x + w / 2, 0.865, big, ha="center", va="center", fontsize=17, fontweight="bold",
             color=N1 if "calculus" not in lab else O1)
    fig.text(x + w / 2, 0.765, lab, ha="center", va="center", fontsize=6.6, color=INK2)
    fig.text(x + w / 2, 0.725, sub, ha="center", va="center", fontsize=5.6, color=INK3)
    x += w + gap
axs = [fig.add_axes([0.055 + i * 0.33, 0.09, 0.265, 0.43]) for i in range(3)]
c = TR.cohort.astype(str)
ax = axs[0]
bars = ax.bar(c, 100 * TR.dc_share, color=B1, width=0.62)
for b, v in zip(bars, 100 * TR.dc_share):
    ax.text(b.get_x() + b.get_width() / 2, v + 1.2, f"{v:.0f}%", ha="center", fontsize=6, color=INK)
ax.set_ylim(0, 80)
ax.set_yticks([0, 20, 40, 60, 80])
ax.set_yticklabels([f"{t}%" for t in [0, 20, 40, 60, 80]])
grid(ax)
for ax_, col, lab, fmt, lim in [(axs[1], "gpa", "GPA", "{:.2f}", (2.6, 2.95)),
                               (axs[2], "remed", "remediation", "{:.1%}", (0, 0.11))]:
    ax_.plot(c, TR[col], color=B1 if col == "gpa" else O1, lw=1.8, marker="o", ms=4, mec=CARD, mew=1)
    for xi, v in zip(c, TR[col]):
        ax_.text(xi, v + (lim[1] - lim[0]) * 0.045, fmt.format(v), ha="center", fontsize=6, color=INK)
    ax_.set_ylim(*lim)
    grid(ax_)
axs[2].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
titles = [("Dual-credit share of graduates", "weighted by graduates, by cohort"),
          ("First-year GPA", "in-state public enrollees, weighted"),
          ("Enrollees needing remediation", "share of in-state public enrollees")]
yb = shared_y(fig, axs)
for ax_, (t, s_) in zip(axs, titles):
    card(fig, ax_, t, s_, ybounds=yb)
save(fig, "fig1_overview")

# =========================================================== Fig 2: distribution of dual-credit share
h = X["dc_hist"]
fig, ax = plt.subplots(figsize=(COL, 1.9))
fig.subplots_adjust(left=0.1, right=0.97, top=0.72, bottom=0.17)
mid = [100 * (a + b) / 2 for a, b in zip(h["edges"][:-1], h["edges"][1:])]
ax.bar(mid, h["counts"], width=4.4, color=B1)
med = 100 * S["descriptives"]["dc_share_median"]
ax.axvline(med, color=N1, lw=1, ls=(0, (3, 2)))
ax.text(med - 1.5, max(h["counts"]) * 0.97, f"median {med:.0f}%", color=N1, fontsize=6.2, va="top", ha="right",
        bbox=dict(facecolor=CARD, edgecolor="none", pad=0.6))
ax.set_xlabel("Graduates earning dual credit from an Indiana public college (%)", fontsize=6.5)
ax.set_ylabel("School-cohorts", fontsize=6.5)
ax.set_xlim(0, 100)
grid(ax)
card(fig, ax, "Distribution of school dual-credit share", "analytic sample, cohorts 2021–2024")
save(fig, "fig2_dc_distribution")

# =========================================================== Fig 3: coefficients across models
labels = ["M1 Cohort only", "M2 + poverty, AP, size, locale", "M3 + Algebra I timing, math offerings",
          "M4 + in-state college-going", "M5 School fixed effects"]
keys = ["M1", "M2", "M3", "M4", "M5"]
fig, axes = plt.subplots(1, 2, figsize=(FULL, 2.35), sharey=True)
fig.subplots_adjust(left=0.205, right=0.985, top=0.80, bottom=0.17, wspace=0.12)
for ax, y, title, unit, d in [(axes[0], "gpa", "First-year GPA", "GPA points", 3),
                              (axes[1], "credits", "First-year credits earned", "credits", 2)]:
    m = S["models"][y]
    b = np.array([m[k]["b"] for k in keys])
    lo = np.array([m[k]["lo"] for k in keys])
    hi = np.array([m[k]["hi"] for k in keys])
    yy = np.arange(len(keys))[::-1]
    cols = [INK3 if k == "M1" else (N1 if k == "M3" else B1) for k in keys]
    ax.barh(yy, b, color=cols, height=0.56)
    ax.errorbar(b, yy, xerr=[b - lo, hi - b], fmt="none", ecolor=INK, elinewidth=0.8, capsize=2)
    for yi, bi, hii in zip(yy, b, hi):
        ax.text(max(hii, bi) + (hi.max() * 0.03), yi, f"{bi:+.{d}f}", va="center", fontsize=6.3, color=INK)
    ax.axvline(0, color=INK2, lw=0.7)
    ax.set_xlim(min(0, lo.min()) * 1.15, hi.max() * 1.28)
    ax.set_xlabel(f"{unit} per +10 points dual-credit share (95% CI)", fontsize=6.5)
    grid(ax, "x")
axes[0].set_yticks(np.arange(5)[::-1])
axes[0].set_yticklabels(labels, fontsize=6.5)
yb = shared_y(fig, axes)
card(fig, axes[0], "First-year GPA", "WLS, enrollee-weighted, SEs clustered by school", ybounds=yb)
card(fig, axes[1], "First-year credits earned", "M3 (navy) is the preferred specification", ybounds=yb)
save(fig, "fig3_coefficients")

# =========================================================== Fig 4: binned scatter, raw vs adjusted
p = pd.read_csv(os.path.join(PROC, "school_cohort_panel.csv"), dtype={"NCESSCH": str})
d = p[(p.cohort >= 2021) & p.gpa.notna() & p.dc_share.notna() & (p.enr_inpub >= S["sample"]["min_inpub"])].copy()
d["alg"] = d.corp_early_alg.clip(upper=1)
d["calc"] = d.calc_offered.astype(float)
d["advm"] = d.advm_offered.astype(float)
d["lgr"] = np.log(d.grads)
d = d.dropna(subset=["alg", "calc", "advm", "locale4", "frl_share", "inpub_rate"])
ctrl = "frl_share + ap_pass_share + lgr + C(locale4) + alg + calc + advm + C(cohort)"
d["gpa_adj"] = smf.wls(f"gpa ~ {ctrl}", d, weights=d.enr_inpub).fit().resid + np.average(d.gpa, weights=d.enr_inpub)
d["dc_adj"] = smf.wls(f"dc_share ~ {ctrl}", d, weights=d.enr_inpub).fit().resid + np.average(d.dc_share, weights=d.enr_inpub)
fig, ax = plt.subplots(figsize=(COL, 2.55))
fig.subplots_adjust(left=0.13, right=0.97, top=0.72, bottom=0.16)
for xc, yc, col, lab in [("dc_share", "gpa", O1, "Unadjusted"), ("dc_adj", "gpa_adj", B1, "Adjusted (M3 controls)")]:
    g = d.groupby(pd.qcut(d[xc], 20, duplicates="drop"), observed=True).apply(lambda t: pd.Series({
        "x": np.average(t[xc], weights=t.enr_inpub), "y": np.average(t[yc], weights=t.enr_inpub)}),
        include_groups=False)
    ax.scatter(100 * g.x, g.y, s=16, color=col, edgecolor=CARD, lw=0.6, zorder=3, label=lab)
    f = np.polyfit(100 * g.x, g.y, 1)
    xs = np.array([100 * g.x.min(), 100 * g.x.max()])
    ax.plot(xs, np.polyval(f, xs), color=col, lw=1.4, zorder=2)
ax.set_xlabel("Dual-credit share of graduates (%)", fontsize=6.5)
ax.set_ylabel("First-year GPA", fontsize=6.5)
ax.set_xlim(10, 100)
grid(ax)
legend(ax, [("Unadjusted", O1), ("Adjusted (M3 controls)", B1)])
card(fig, ax, "School first-year GPA by dual-credit share", "20 equal-count bins; both axes residualised for adjusted series")
save(fig, "fig4_binscatter")

# =========================================================== Fig 5: within-school clustered columns
sx = pd.DataFrame(X["within_sextiles"])
fig, ax = plt.subplots(figsize=(COL, 2.45))
fig.subplots_adjust(left=0.1, right=0.97, top=0.70, bottom=0.17)
xi = np.arange(len(sx))
ax.bar(xi - 0.2, sx.dc_gpa, width=0.38, color=B1)
ax.bar(xi + 0.2, sx.nodc_gpa, width=0.38, color=O1)
for i, (a1, a2) in enumerate(zip(sx.dc_gpa, sx.nodc_gpa)):
    ax.text(i - 0.2, a1 + 0.03, f"{a1:.2f}", ha="center", fontsize=5.6, color=INK, rotation=90, va="bottom")
    ax.text(i + 0.2, a2 + 0.03, f"{a2:.2f}", ha="center", fontsize=5.6, color=INK, rotation=90, va="bottom")
ax.set_xticks(xi)
ax.set_xticklabels([f"{100 * v:.0f}%" for v in sx.dc_share_med])
ax.set_xlabel("School dual-credit share (median of sextile)", fontsize=6.5)
ax.set_ylim(1.8, 3.35)
ax.set_ylabel("First-year GPA", fontsize=6.5)
grid(ax)
legend(ax, [("Earned dual credit", B1), ("Did not", O1)])
card(fig, ax, "Earners vs. classmates within the same schools", f"{S['within_school']['schools']} schools with 10+ enrollees in both groups")
save(fig, "fig5_within_school")

# =========================================================== Fig 6: heterogeneity
H = S["heterogeneity"]
rows = [("High-poverty", "frl_hi", True), ("Lower-poverty", "frl_hi", False), ("Rural", "rural", True),
        ("Non-rural", "rural", False), ("Late Algebra I corp.", "alg_lo", True), ("Earlier Algebra I corp.", "alg_lo", False),
        ("Offers calculus", "calc", True), ("No calculus", "calc", False)]
fig, ax = plt.subplots(figsize=(COL, 2.75))
fig.subplots_adjust(left=0.33, right=0.95, top=0.76, bottom=0.14)
yy = np.arange(len(rows))[::-1]
for yi, (lab, k, grp) in zip(yy, rows):
    e = H[k]["gpa"]
    b, se = (e["slope_group"], e["se_group"]) if grp else (e["slope_other"], e["se_other"])
    ax.barh(yi, b, height=0.6, color=B1 if grp else "#7DBEFF")
    ax.errorbar(b, yi, xerr=1.96 * se, fmt="none", ecolor=INK, elinewidth=0.7, capsize=1.8)
    ax.text(b + 1.96 * se + 0.002, yi, f"{b:+.3f}", va="center", fontsize=6, color=INK)
    if grp:
        ax.text(0.0435, yi - 0.5, f"p(diff) = {e['p_interaction']:.2f}", fontsize=5.6, color=INK3, va="center")
ax.axvline(0, color=INK2, lw=0.7)
ax.set_yticks(yy)
ax.set_yticklabels([r[0] for r in rows], fontsize=6.4)
ax.set_xlim(-0.012, 0.058)
ax.set_xlabel("GPA points per +10 points dual-credit share (95% CI)", fontsize=6.5)
grid(ax, "x")
card(fig, ax, "Heterogeneity of the GPA association", "M3 with group interaction; p-value tests the difference")
save(fig, "fig6_heterogeneity")

# =========================================================== Fig 7: sensitivity
lab = {"main": "Main (M3)", "no_virtual": "Exclude virtual schools", "unweighted": "Unweighted",
       "min30": "30+ in-state enrollees", "hs_alg": "High-school Algebra I measure",
       "both_alg": "Both Algebra I measures", "with2019": "Add 2019 cohort", "only2024": "2024 cohort only"}
SE = S["sensitivity"]
fig, axes = plt.subplots(1, 2, figsize=(FULL, 2.3), sharey=True)
fig.subplots_adjust(left=0.18, right=0.985, top=0.74, bottom=0.17, wspace=0.12)
keys = list(lab)
yy = np.arange(len(keys))[::-1]
for ax, y, unit, dd in [(axes[0], "gpa", "GPA points", 3), (axes[1], "credits", "credits", 2)]:
    b = np.array([SE[k][y]["b"] for k in keys])
    se = np.array([SE[k][y]["se"] for k in keys])
    ax.barh(yy, b, height=0.56, color=[N1 if k == "main" else B1 for k in keys])
    ax.errorbar(b, yy, xerr=1.96 * se, fmt="none", ecolor=INK, elinewidth=0.7, capsize=1.8)
    for yi, bi, si in zip(yy, b, se):
        ax.text(bi + 1.96 * si + abs(b).max() * 0.03, yi, f"{bi:+.{dd}f}", va="center", fontsize=6, color=INK)
    ax.axvline(0, color=INK2, lw=0.7)
    ax.set_xlim(min(0, (b - 1.96 * se).min()) * 1.2, (b + 1.96 * se).max() * 1.25)
    ax.set_xlabel(f"{unit} per +10 points dual-credit share (95% CI)", fontsize=6.5)
    grid(ax, "x")
axes[0].set_yticks(yy)
axes[0].set_yticklabels([lab[k] for k in keys], fontsize=6.5)
yb = shared_y(fig, axes)
card(fig, axes[0], "Sensitivity: first-year GPA", "M3 re-estimated under alternative choices", ybounds=yb)
card(fig, axes[1], "Sensitivity: first-year credits", "navy = main specification", ybounds=yb)
save(fig, "fig7_sensitivity")

# =========================================================== Fig 8: access by poverty and locale
a = pd.read_csv(os.path.join(PROC, "school_access_tiers.csv"), dtype={"NCESSCH": str, "CNTY": str})
t = a[a.tier != "Virtual or alternative"].copy()
t["calc_offered"] = t.calc_offered.astype(bool)
t["dual_any"] = t.dual_any.astype(bool)
t["frl_q"] = pd.qcut(t.frl_share_pooled, 4, labels=["Q1 lowest", "Q2", "Q3", "Q4 highest"])
fig, axes = plt.subplots(1, 2, figsize=(FULL, 2.35), sharey=True)
fig.subplots_adjust(left=0.07, right=0.985, top=0.70, bottom=0.14, wspace=0.08)
for ax, col, order in [(axes[0], "frl_q", ["Q1 lowest", "Q2", "Q3", "Q4 highest"]),
                       (axes[1], "locale4", ["Rural", "Town", "Suburb", "City"])]:
    g = t.groupby(col, observed=True)
    nc = (100 * g.calc_offered.apply(lambda s: (~s).mean())).reindex(order)
    nd = (100 * g.dual_any.apply(lambda s: (~s).mean())).reindex(order)
    n = g.size().reindex(order)
    xi = np.arange(len(order))
    ax.bar(xi - 0.19, nc, width=0.36, color=B1)
    ax.bar(xi + 0.19, nd, width=0.36, color=O1)
    for i in range(len(order)):
        ax.text(i - 0.19, nc.iloc[i] + 0.8, f"{nc.iloc[i]:.0f}%", ha="center", fontsize=6.2, color=INK)
        ax.text(i + 0.19, nd.iloc[i] + 0.8, f"{nd.iloc[i]:.0f}%", ha="center", fontsize=6.2, color=INK)
    ax.set_xticks(xi)
    ax.set_xticklabels([f"{o}\n(n={n.iloc[i]})" for i, o in enumerate(order)], fontsize=6.3)
    ax.set_ylim(0, 50)
    grid(ax)
axes[0].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(100, decimals=0))
legend(axes[0], [("No calculus (either year)", B1), ("No dual enrollment", O1)])
yb = shared_y(fig, axes)
card(fig, axes[0], "Missing pathway by school poverty quartile", "free/reduced-lunch share of graduates, 2021–2024", ybounds=yb)
card(fig, axes[1], "Missing pathway by NCES locale", "traditional public high schools", ybounds=yb)
save(fig, "fig8_access_columns")

# =========================================================== Fig 9: 100% stacked bar of tiers by locale
order_t = ["Dual credit and calculus", "Dual credit, but no calculus", "Thin pathway: no calculus and low uptake",
           "No dual enrollment reported"]
short = ["Dual credit + calculus", "Dual credit, no calculus", "Thin pathway", "No dual enrollment"]
cols = [B1, "#7DBEFF", N1, O1]
locs = ["Rural", "Town", "Suburb", "City"]
fig, ax = plt.subplots(figsize=(COL, 2.45))
fig.subplots_adjust(left=0.14, right=0.97, top=0.62, bottom=0.12)
left = np.zeros(len(locs))
for tier, s_, c_ in zip(order_t, short, cols):
    v = np.array([100 * X["access_tier_by_locale"][l].get(tier, 0) / sum(X["access_tier_by_locale"][l].values())
                  for l in locs])
    ax.barh(locs[::-1], v[::-1], left=left[::-1], color=c_, height=0.6, edgecolor=CARD, lw=0.8, label=s_)
    for i, (vv, ll) in enumerate(zip(v[::-1], left[::-1])):
        if vv >= 6:
            ax.text(ll + vv / 2, i, f"{vv:.0f}%", ha="center", va="center", fontsize=5.8,
                    color="white" if c_ in (B1, N1, O1) else INK)
    left += v
ax.set_xlim(0, 100)
ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(100, decimals=0))
grid(ax, "x")
legend(ax, list(zip(short, cols)), anchor=(0, 1.30), ncol=2)
card(fig, ax, "Access tier by locale", "share of traditional public high schools")
save(fig, "fig9_tiers")

# =========================================================== Fig 10: filled map
z = os.path.join(ROOT, "data", "raw", "geo", "cb_2023_us_county_500k.zip")
cty = gpd.read_file(f"zip://{z}")
cty = cty[cty.STATEFP == "18"].to_crs(epsg=26916)
ct = pd.read_csv(os.path.join(ROOT, "paper", "tables", "table7_access_by_county.csv"), dtype={"CNTY": str})
cty = cty.merge(ct, left_on="GEOID", right_on="CNTY", how="left")
bins = [-0.1, 0.1, 10, 25, 50, 99.9, 100]
labs = ["0%", "<10%", "10–25%", "25–50%", "50–99%", "100%"]
cty["cls"] = pd.cut(cty.pct_students_no_calc, bins, labels=labs)
pts = gpd.GeoDataFrame(t, geometry=gpd.points_from_xy(t.LON, t.LAT), crs=4326).to_crs(epsg=26916)
fig = plt.figure(figsize=(COL, 4.6))
ax = fig.add_axes([0.02, 0.02, 0.66, 0.86])
for l_, c_ in zip(labs, SEQ):
    sub = cty[cty.cls == l_]
    if len(sub):
        sub.plot(ax=ax, color=c_, edgecolor="white", linewidth=0.5)
cty[cty.cls.isna()].plot(ax=ax, color="#F3F2F1", edgecolor="white", linewidth=0.5)
for tier, (mk, c_, sz) in {"No dual enrollment reported": ("o", O1, 14),
                           "Thin pathway: no calculus and low uptake": ("D", N1, 11)}.items():
    s_ = pts[pts.tier == tier]
    ax.scatter(s_.geometry.x, s_.geometry.y, marker=mk, s=sz, color=c_, edgecolor="white", lw=0.5, zorder=5)
ax.set_axis_off()
lax = fig.add_axes([0.69, 0.22, 0.28, 0.56])
lax.set_xlim(0, 1)
lax.set_ylim(0, 1)
lax.set_axis_off()
lax.text(0, 1.0, "Students in schools\nwith no calculus", fontsize=6.4, color=INK, va="top", fontweight="bold")
for i, (l_, c_) in enumerate(zip(labs, SEQ)):
    yv = 0.80 - i * 0.075
    lax.add_patch(plt.Rectangle((0, yv), 0.16, 0.05, color=c_))
    lax.text(0.22, yv + 0.025, l_, fontsize=6.2, color=INK2, va="center")
lax.add_patch(plt.Rectangle((0, 0.80 - 6 * 0.075), 0.16, 0.05, facecolor="#F3F2F1", edgecolor=BORDER, lw=0.5))
lax.text(0.22, 0.80 - 6 * 0.075 + 0.025, "No school in data", fontsize=6.2, color=INK2, va="center")
lax.scatter([0.08], [0.17], marker="o", s=14, color=O1, edgecolor="white")
lax.text(0.22, 0.17, "No dual enrollment", fontsize=6.2, color=INK2, va="center")
lax.scatter([0.08], [0.09], marker="D", s=11, color=N1, edgecolor="white")
lax.text(0.22, 0.09, "Thin pathway", fontsize=6.2, color=INK2, va="center")
fig.patches.append(FancyBboxPatch((0.01, 0.005), 0.98, 0.985, boxstyle="round,pad=0,rounding_size=0.01",
                                  transform=fig.transFigure, facecolor=CARD, edgecolor=BORDER, lw=0.6, zorder=-10))
fig.text(0.04, 0.955, "Where dual-credit math is out of reach", fontsize=8, fontweight="bold", color=INK, va="top")
fig.text(0.04, 0.915, f"{S['access']['counties_no_calc_anywhere']} counties with no calculus at any public high school",
         fontsize=6.2, color=INK3, va="top")
save(fig, "fig10_map")
