#!/usr/bin/env python3
"""04_figures.py — paper figures and the access map (static PNG + interactive HTML data).

Run from repo root:  python code/04_figures.py [--final]
Without --final every figure carries a DRAFT stamp. Palette: dataviz reference instance (light mode).
"""
import argparse
import json
import os
import warnings
import zipfile

import geopandas as gpd
import matplotlib
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

warnings.filterwarnings("ignore")
ap = argparse.ArgumentParser()
ap.add_argument("--final", action="store_true")
FINAL = ap.parse_args().final

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "paper", "figures")
MAPDIR = os.path.join(ROOT, "map")
os.makedirs(FIG, exist_ok=True)
S = json.load(open(os.path.join(ROOT, "paper", "stats.json")))

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "savefig.facecolor": SURF, "axes.titlecolor": INK, "axes.titleweight": "bold",
                     "axes.titlesize": 11, "axes.titlelocation": "left"})
SRC = ("Sources: Indiana CHE College-Going/Readiness datasets (cohorts 2021-2024); CRDC 2021-22, 2023-24; "
       "NCES CCD/EDGE 2023-24.")


def finish(fig, name, note=SRC):
    fig.text(0.01, -0.02, note, fontsize=7, color=INK2, ha="left", va="top")
    if not FINAL:
        fig.text(0.99, 0.99, "DRAFT — not verified", fontsize=9, color="#e34948", ha="right", va="top",
                 fontweight="bold")
    fig.savefig(os.path.join(FIG, name), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def grid(ax, axis="y"):
    ax.grid(axis=axis, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


# --------------------------------------------------------------------------- data for fig 1-3
p = pd.read_csv(os.path.join(PROC, "school_cohort_panel.csv"), dtype={"NCESSCH": str})
d = p[(p.cohort >= 2021) & p.gpa.notna() & p.dc_share.notna() & (p.enr_inpub >= S["sample"]["min_inpub"])].copy()
d["alg"] = d.corp_early_alg.clip(upper=1)
d["calc"] = d.calc_offered.astype(float)
d["advm"] = d.advm_offered.astype(float)
d["lgr"] = np.log(d.grads)
d = d.dropna(subset=["alg", "calc", "advm", "locale4", "frl_share"])

# ---------------------------------------------------------------- Figure 1: coefficient across models
labels = ["Cohort only", "+ poverty, AP,\nsize, locale", "+ Algebra I timing,\nmath offerings",
          "+ in-state public\ncollege-going", "School fixed\neffects"]
keys = ["M1", "M2", "M3", "M4", "M5"]
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
for ax, y, title, unit in [(axes[0], "gpa", "First-year GPA", "GPA points"),
                           (axes[1], "credits", "First-year credits earned", "credits")]:
    m = S["models"][y]
    b = [m[k]["b"] for k in keys]
    lo = [m[k]["lo"] for k in keys]
    hi = [m[k]["hi"] for k in keys]
    yy = np.arange(len(keys))[::-1]
    ax.axvline(0, color=INK2, lw=0.8)
    ax.hlines(yy, lo, hi, color=BLUE, lw=2)
    ax.plot(b, yy, "o", color=BLUE, ms=8, mec=SURF, mew=2)
    for yi, bi in zip(yy, b):
        ax.annotate(f"{bi:+.3f}" if y == "gpa" else f"{bi:+.2f}", (bi, yi), xytext=(0, 9),
                    textcoords="offset points", ha="center", fontsize=8, color=INK)
    ax.set_yticks(yy)
    ax.set_yticklabels(labels if ax is axes[0] else [""] * 5, fontsize=8.5)
    ax.set_title(title)
    ax.set_xlabel(f"{unit} per +10 pts dual-credit share (95% CI)")
    grid(ax, "x")
fig.suptitle("Most of the raw dual-credit advantage reflects which schools offer it", x=0.01, ha="left",
             fontsize=12.5, fontweight="bold", color=INK, y=1.04)
fig.tight_layout()
finish(fig, "fig1_coefficients.png", SRC + " WLS weighted by Indiana public enrollees; SEs clustered by school.")

# ---------------------------------------------------------------- Figure 2: binned scatter raw vs adjusted
ctrl = "frl_share + ap_pass_share + lgr + C(locale4) + alg + calc + advm + C(cohort)"
ry = smf.wls(f"gpa ~ {ctrl}", d, weights=d.enr_inpub).fit().resid
rx = smf.wls(f"dc_share ~ {ctrl}", d, weights=d.enr_inpub).fit().resid
d["gpa_adj"] = ry + np.average(d.gpa, weights=d.enr_inpub)
d["dc_adj"] = rx + np.average(d.dc_share, weights=d.enr_inpub)
fig, ax = plt.subplots(figsize=(7, 4.4))
for xcol, ycol, col, lab in [("dc_share", "gpa", INK2, "Unadjusted"),
                             ("dc_adj", "gpa_adj", BLUE, "Adjusted for poverty, AP, size, locale,\n"
                                                         "Algebra I timing, math offerings")]:
    bins = pd.qcut(d[xcol], 20, duplicates="drop")
    g = d.groupby(bins, observed=True).apply(lambda t: pd.Series({
        "x": np.average(t[xcol], weights=t.enr_inpub), "y": np.average(t[ycol], weights=t.enr_inpub)}),
        include_groups=False)
    ax.plot(g.x * 100, g.y, "o", color=col, ms=7, mec=SURF, mew=1.5, alpha=0.95)
    fit = np.polyfit(g.x * 100, g.y, 1)
    xs = np.array([g.x.min(), g.x.max()]) * 100
    ax.plot(xs, np.polyval(fit, xs), color=col, lw=2)
    ax.annotate(lab, (xs[1], np.polyval(fit, xs[1])), xytext=(6, 0), textcoords="offset points", fontsize=8.5,
                color=INK, va="center")
ax.set_xlabel("Share of graduates earning dual credit from an Indiana public college (%)")
ax.set_ylabel("Average first-year GPA of\nIndiana public college enrollees")
ax.set_xlim(0, 135)
ax.set_xticks([0, 20, 40, 60, 80, 100])
grid(ax)
ax.set_title("School first-year GPA by dual-credit share (20 equal-count bins, 2021-2024 cohorts)")
finish(fig, "fig2_binscatter.png", SRC + " Adjusted series residualizes both axes on the controls.")

# ---------------------------------------------------------------- Figure 3: within-school selection
w = p[(p.cohort >= 2021) & p.dc_gpa_gap.notna() & p.nodc_inpub.ge(10) & p.dc_inpub.ge(10)].copy()
w["bin"] = pd.qcut(w.dc_share, 6)
g = w.groupby("bin", observed=True).apply(lambda t: pd.Series({
    "x": t.dc_share.median() * 100,
    "dc": np.average(t.dc_gpa, weights=t.dc_inpub), "nodc": np.average(t.nodc_gpa, weights=t.nodc_inpub)}),
    include_groups=False)
fig, ax = plt.subplots(figsize=(7, 4.2))
for col, c, lab in [("dc", BLUE, "Graduates who earned dual credit"), ("nodc", ORANGE, "Classmates who did not")]:
    ax.plot(g.x, g[col], "-o", color=c, lw=2, ms=8, mec=SURF, mew=2)
    ax.annotate(lab, (g.x.iloc[-1], g[col].iloc[-1]), xytext=(8, 0), textcoords="offset points", fontsize=8.5,
                color=INK, va="center")
ax.set_xlim(g.x.min() - 5, g.x.max() + 22)
ax.set_xlabel("School's share of graduates earning dual credit (%), median of sextile")
ax.set_ylabel("Average first-year GPA")
grid(ax)
ax.set_title("The dual-credit GPA gap is wider in schools where dual credit is common")
finish(fig, "fig3_within_school.png",
       SRC + f" {S['within_school']['schools']} schools where both groups have 10+ Indiana public enrollees.")

# ---------------------------------------------------------------- Figure 4: access gaps by poverty and locale
a = pd.read_csv(os.path.join(PROC, "school_access_tiers.csv"), dtype={"NCESSCH": str, "CNTY": str})
t = a[a.tier != "Virtual or alternative"].copy()
t["frl_q"] = pd.qcut(t.frl_share_pooled, 4, labels=["Lowest", "Second", "Third", "Highest"])
fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
for ax, col, order, title in [(axes[0], "frl_q", ["Lowest", "Second", "Third", "Highest"],
                               "By school poverty quartile (free/reduced lunch)"),
                              (axes[1], "locale4", ["Rural", "Town", "Suburb", "City"], "By NCES locale")]:
    v = t.groupby(col, observed=True).calc_offered.apply(lambda s: 100 * (~s.astype(bool)).mean()).reindex(order)
    n = t.groupby(col, observed=True).size().reindex(order)
    bars = ax.bar(range(len(order)), v.values, color=BLUE, width=0.6, edgecolor=SURF, linewidth=2)
    for i, (val, nn) in enumerate(zip(v.values, n.values)):
        ax.text(i, val + 1, f"{val:.0f}%", ha="center", fontsize=9, color=INK)
        ax.text(i, -6.5, f"n={nn}", ha="center", fontsize=7.5, color=INK2)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(order)
    ax.set_title(title, fontsize=10)
    grid(ax)
axes[0].set_ylabel("% of public high schools\nwith no calculus")
axes[0].set_ylim(-9, 50)
fig.suptitle("Calculus is least available where poverty is highest and in cities", x=0.01, ha="left",
             fontsize=12.5, fontweight="bold", color=INK, y=1.04)
fig.tight_layout()
finish(fig, "fig4_access_bars.png", "Sources: CRDC 2021-22 and 2023-24 (no calculus section in either year); "
       "CHE cohorts 2021-2024; NCES EDGE. Traditional public high schools only.")

# ---------------------------------------------------------------- Figure 5: map
z = os.path.join(ROOT, "data", "raw", "geo", "cb_2023_us_county_500k.zip")
cty = gpd.read_file(f"zip://{z}")
cty = cty[cty.STATEFP == "18"].to_crs(epsg=26916)
ct = pd.read_csv(os.path.join(ROOT, "paper", "tables", "table7_access_by_county.csv"), dtype={"CNTY": str})
cty = cty.merge(ct, left_on="GEOID", right_on="CNTY", how="left")
pts = gpd.GeoDataFrame(t, geometry=gpd.points_from_xy(t.LON, t.LAT), crs=4326).to_crs(epsg=26916)
fig, ax = plt.subplots(figsize=(6.4, 8.6))
bins = [-0.1, 0.1, 10, 25, 50, 99.9, 100]
labs = ["0%", "<10%", "10-25%", "25-50%", "50-99%", "100%"]
ramp = ["#f1f0ec", SEQ[0], SEQ[1], SEQ[3], SEQ[5], SEQ[6]]
cty["cls"] = pd.cut(cty.pct_students_no_calc, bins, labels=labs)
for lab, col in zip(labs, ramp):
    sub = cty[cty.cls == lab]
    if len(sub):
        sub.plot(ax=ax, color=col, edgecolor=SURF, linewidth=0.8)
cty[cty.cls.isna()].plot(ax=ax, color="#ffffff", edgecolor=GRID, linewidth=0.8, hatch="///")
sel = {"No dual enrollment reported": ("o", ORANGE, 46),
       "Thin pathway: no calculus and low uptake": ("D", "#0b0b0b", 34)}
for tier_name, (mk, col, sz) in sel.items():
    s = pts[pts.tier == tier_name]
    ax.scatter(s.geometry.x, s.geometry.y, marker=mk, s=sz, color=col, edgecolor=SURF, linewidth=1.2, zorder=5)
ax.set_axis_off()
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
h1 = [Patch(color=c, label=l) for l, c in zip(labs, ramp)]
h2 = [Line2D([], [], marker=v[0], ls="", color=v[1], mec=SURF, ms=7, label=k.replace("Thin pathway: ", "Thin: "))
      for k, v in sel.items()]
l1 = ax.legend(handles=h1, title="Students in public HS\nwith no calculus", loc="upper left", frameon=False,
               fontsize=8.5, title_fontsize=9, bbox_to_anchor=(1.0, 0.80))
ax.add_artist(l1)
ax.legend(handles=h2, loc="upper left", frameon=False, fontsize=8.5, bbox_to_anchor=(1.0, 0.45))
ax.set_title("Where dual-credit math is out of reach", fontsize=13)
ax.text(0, 1.0, f"{S['access']['counties_no_calc_anywhere']} counties had no calculus at any public high school "
        "in 2021-22 or 2023-24", transform=ax.transAxes, fontsize=8.5, color=INK2, va="bottom")
finish(fig, "fig5_access_map.png", "Sources: CRDC 2021-22, 2023-24; NCES EDGE 2023-24 geocodes; Census 2023 "
       "cartographic boundaries; CHE cohorts 2021-2024.\nTraditional public high schools; virtual and alternative "
       "schools excluded. 'Thin' = no calculus and under one-third of graduates earning dual credit.")

# ---------------------------------------------------------------- data for the interactive map
cty_wgs = cty.to_crs(epsg=4326)[["GEOID", "NAME", "schools", "students", "pct_students_no_calc",
                                 "pct_students_thin_or_none", "geometry"]]
cty_wgs["geometry"] = cty_wgs.geometry.simplify(0.003)
os.makedirs(MAPDIR, exist_ok=True)
cty_wgs.to_file(os.path.join(MAPDIR, "counties.geojson"), driver="GeoJSON")
keep = ["SCH_NAME", "LEA_NAME", "NMCNTY", "locale4", "LAT", "LON", "enr", "dc_share_pooled", "frl_share_pooled",
        "calc_offered", "dual_any", "tier"]
t[keep].round(4).to_json(os.path.join(MAPDIR, "schools.json"), orient="records")
print("wrote map/counties.geojson, map/schools.json")
