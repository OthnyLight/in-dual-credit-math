#!/usr/bin/env python3
"""07_briefs.py — NACEP session proposal and Indiana written statement, numbers from paper/stats.json.

Run from repo root:  python code/07_briefs.py [--final]
"""
import argparse
import json
import os

ap = argparse.ArgumentParser()
ap.add_argument("--final", action="store_true")
FINAL = ap.parse_args().final
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(os.path.join(ROOT, "paper", "stats.json")))
AU = json.load(open(os.path.join(ROOT, "AUTHORS.json")))["authors"][0]

G, C, W, A, D, SM = S["models"]["gpa"], S["models"]["credits"], S["within_school"], S["access"], S["descriptives"], S["sample"]
fq = A["by_frl_quartile"]
city = A["by_locale"]["City"]
none_s = A["tiers"]["No dual enrollment reported"]["schools"]
thin_s = A["tiers"]["Thin pathway: no calculus and low uptake"]["schools"]
pc = lambda x, d=0: f"{100 * x:.{d}f}%"
sg = lambda x, d=3: f"{'+' if x >= 0 else '−'}{abs(x):.{d}f}"
no_calc_n = round(A["traditional_schools"] * A["no_calc_share_schools"])
banner = "" if FINAL else "> **DRAFT — not verified by the author. Do not submit or circulate.**\n\n"

# --------------------------------------------------------------------------- NACEP proposal
title = "Who Dual Credit Reaches, and Where Math Can't Start: School-Level Evidence from Indiana"
desc = (
    f"Indiana graduates earn dual credit at high rates ({pc(D['dc_share_weighted_mean'])} of the 2021–2024 public "
    f"high school cohorts studied), but does a school's dual-credit uptake translate into better first-year college "
    f"performance, and can every school offer the mathematics that leads into it? Linking Commission for Higher "
    f"Education outcomes to federal Civil Rights Data Collection course data for {SM['schools']} public high schools, "
    f"we find that higher-uptake schools send graduates with modestly higher first-year GPAs and more credits "
    f"after accounting for poverty, AP success, Algebra I timing, and math offerings; about {pc(S['attenuation_gpa_M1_to_M3'])} "
    f"of the raw advantage reflects which schools offer dual credit, and part of the rest is dual-credit work counted "
    f"on the college record. Within schools, the gap between dual-credit "
    f"earners and their classmates widens as programs grow. Meanwhile {pc(A['no_calc_share_schools'])} of traditional "
    f"public high schools offered no calculus in either recent year, rising to {fq['Q4 highest']['no_calculus_pct_schools']:.0f}% "
    f"of the highest-poverty schools. Drawing on experience teaching IU Advance College Project MATH M118 (Finite "
    f"Mathematics) in partner high schools, the session walks through an interactive access atlas and a replicable "
    f"public-data method that partnerships in any state can run on their own schools."
)
outcomes = [
    "Interpret school-level dual-credit outcome data without mistaking selection for program effect.",
    "Identify schools in their own service area where the mathematics pathway into dual credit is missing, using public federal data.",
    "Apply a replicable, open method (code and data provided) to evaluate their partnership's readiness outcomes.",
]
nacep = f"""{banner}# NACEP National Conference — breakout session proposal kit

**Target call:** 2027 NACEP National Conference. The 2026 call (Cleveland, October 18–20, 2026) closed April 10, 2026.
[VERIFY: 2027 call dates, deadline, and field limits when the call opens — typically announced in winter; the 2026 form required every field and asked for track, program mode, and audience. Trim the text below to the stated limits.]

**Format:** 45-minute breakout session, up to three speakers. Willing to prerecord: [VERIFY yes/no].

## Title
{title}

## Session description ({len(desc.split())} words)
{desc}

## Learning outcomes
""" + "\n".join(f"{i + 1}. {o}" for i, o in enumerate(outcomes)) + f"""

## Track / audience / program mode
- **Track:** [VERIFY: choose from the 2027 track list — likely research/evaluation or equity and access]
- **Audience:** partnership directors, institutional researchers, state policy staff, high school counselors and math department leads
- **Program mode:** concurrent enrollment taught by credentialed high school instructors (IU ACP model) and dual enrollment generally

## Session plan (45 minutes)
- 0–8 min: Indiana's dual-credit expansion and the question a school-level view answers
- 8–20 min: findings: readiness association, how much is selection, where math pathways are missing
- 20–30 min: live walk-through of the access atlas; finding your own schools
- 30–38 min: from the classroom: building an ACP M118 section at Lawrence Central from 8 students to more than 20 (with students from a sister school), 17 of whom completed the year; how students are recommended (B or better in Honors Geometry or Algebra II, work ethic) and why unprepared placements withdraw; what happened to students when the school briefly lost its approved teacher; and why awareness of the course is the cheapest barrier to fix
- 38–45 min: questions; how to rerun the method for another state

## Presenter
- {AU['name']}, {AU['affiliation']} · {AU['email']}
- Bio (75 words): Othniel Iyassa Sa'anga is an independent education researcher in Indianapolis and a mathematics teacher with eleven years of classroom experience, four of them in the United States. Since 2024 he has taught MATH M118, Finite Mathematics, at Lawrence Central High School through Indiana University's Advance College Project. He holds a Master of Education in Mathematics (2015) and a master's degree in applied mathematics (2023). His research uses public data to study who dual credit reaches and where college mathematics pathways are missing.

## Prior presentation disclosure
[VERIFY: list any prior presentation of this work, or "Not previously presented."]
"""
open(os.path.join(ROOT, "paper", "nacep_proposal.md"), "w").write(nacep)

# --------------------------------------------------------------------------- Indiana written statement
stmt = f"""{banner}# Written statement on dual-credit access and college readiness in Indiana

**To:** Indiana Commission for Higher Education, in connection with its September 10, 2026 Request for Information on expanding access to the Indiana College Core and dual credit; and the Indiana Department of Education review of dual-credit, career-technical, and Advanced Placement offerings directed by the General Assembly.
[VERIFY: the RFI's response deadline, submission address, and whether it accepts research input from individuals; if not, send as a letter to the Commission and the Secretary of Education.]

**From:** {AU['name']}, {AU['affiliation']}. Submitted in my individual capacity. I am a certified mathematics teacher with the Metropolitan School District of Lawrence Township and have taught MATH M118, Finite Mathematics, at Lawrence Central High School through Indiana University's Advance College Project since 2024-25. ACP pays a stipend each time I attend one of its training workshops. The views here are my own and not those of Indiana University or the district.

**Date:** [VERIFY date of submission]

## Summary
I analyzed public data on {SM['schools']} Indiana public high schools and the {SM['inpub']:,} graduates from the 2021–2024 classes who enrolled at an Indiana public college. Three findings bear on the Commission's review.

1. **Dual credit's readiness return at the school level is modest at most.** Schools where more graduates earn dual credit send students with somewhat higher first-year GPAs and more credits, even after accounting for school poverty, AP success, Algebra I timing, and math offerings. Moving from a low-uptake school to a high-uptake school ({S['p10_p90_implied']['dc_pp']:.0f} percentage points) corresponds to at most about {S['p10_p90_implied']['gpa']:.2f} GPA points and {S['p10_p90_implied']['credits']:.1f} credits. Roughly {pc(S['attenuation_gpa_M1_to_M3'])} of the raw advantage reflects differences between the schools that offer dual credit and those that do not. Part of the rest is mechanical: the first-year GPA and credits the state reports include dual-credit grades and hours earned in high school. Remediation, which is not affected by that overlap, shows no clear relationship. The Commission could separate these by reporting first-year outcomes that exclude credit earned before enrollment.

2. **The gap between dual-credit earners and their classmates is widest where programs are largest.** Within a school, dual-credit earners average {W['gpa_gap_mean']:.2f} GPA points higher in their first college year than classmates who did not earn dual credit (partly because their dual-credit grades count), and that gap is wider in schools where dual credit is more common. As programs grow, the remaining students are the least prepared, and they are the ones whose outcomes have the most room to improve.

3. **The mathematics pathway into college credit is missing where poverty is highest.** {no_calc_n} of {A['traditional_schools']} traditional public high schools ({pc(A['no_calc_share_schools'])}) offered no calculus in either of the last two federal civil-rights collections (2021-22, 2023-24). That rate is {fq['Q1 lowest']['no_calculus_pct_schools']:.0f}% in the lowest-poverty quarter of schools and {fq['Q4 highest']['no_calculus_pct_schools']:.0f}% in the highest. {city['no_calculus_pct_schools']:.0f}% of city high schools offered no calculus, and in {A['counties_no_calc_anywhere']} counties no public high school did. {none_s} schools reported no dual enrollment at all, and {thin_s} more had neither calculus nor substantial dual-credit uptake.

## Recommendations
1. **Report dual credit by subject.** State data identify whether a graduate earned dual credit, not in what subject. Adding subject (at minimum, mathematics and English) to CHE's high school reports would let the state see where college-level math is reached and where it is not.
2. **Target capacity grants at the schools without a math pathway.** The schools identified here lack the sequence that feeds college-level mathematics. Support for credentialing a mathematics teacher, sharing a section across schools, or a college-taught online section would reach students the current expansion misses. In my own district, when Lawrence Central briefly had no approved finite-mathematics teacher, its students could take the course only because a sister school nearby had one; most of the schools on this list have no such fallback.
3. **Measure success by who is reached, not only by how many credits are earned.** Because outcomes for non-participants are weakest where programs are largest, state goals should track the share of graduates, by school poverty level, who complete a college-level mathematics course before graduation.

## Method and materials
The analysis uses only public data: CHE College-Going datasets (2019 and 2021–2024 cohorts), the U.S. Department of Education Civil Rights Data Collection (2021-22 and 2023-24), and NCES Common Core of Data. Associations are school-level and observational; they are not estimates of the effect of dual credit on individual students. Code, data, an interactive map of every school, and a full manuscript are available at https://github.com/OthnyLight/in-dual-credit-math.

I would welcome the opportunity to share the school-level map with Commission staff.

{AU['name']}
{AU['email']}
"""
open(os.path.join(ROOT, "paper", "indiana_statement.md"), "w").write(stmt)
heads = f"""{banner}# Headline numbers

Generated by `code/07_briefs.py` from `paper/stats.json`. Verified by the author on 2026-10-21.

- Sample: {SM['schools']} public high schools, {SM['school_cohorts']:,} school-cohorts (graduating classes 2021–2024), {SM['inpub']:,} Indiana public college enrollees.
- Per 10-point higher dual-credit share, first-year GPA: {sg(G['M1']['b'])} unadjusted; {sg(G['M3']['b'])} adjusted (95% CI {G['M3']['lo']:.3f} to {G['M3']['hi']:.3f}); {sg(G['M5']['b'])} with school fixed effects.
- Per 10 points, first-year credits: {sg(C['M1']['b'], 2)} unadjusted; {sg(C['M3']['b'], 2)} adjusted.
- GPA and credit measures include dual-credit work earned in high school, so both estimates are upper bounds; remediation (unaffected) shows no robust association.
- Share of the raw GPA association explained by school characteristics: {pc(S['attenuation_gpa_M1_to_M3'])}.
- Within-school GPA gap, dual-credit earners vs. classmates: {W['gpa_gap_mean']:.2f} points ({W['schools']} schools).
- Traditional public high schools with no calculus in CRDC 2021-22 or 2023-24: {no_calc_n} of {A['traditional_schools']} ({pc(A['no_calc_share_schools'])}); lowest- vs highest-poverty quartile {fq['Q1 lowest']['no_calculus_pct_schools']:.0f}% vs {fq['Q4 highest']['no_calculus_pct_schools']:.0f}%.
"""
open(os.path.join(ROOT, "docs", "HEADLINES.md"), "w").write(heads)
print("wrote paper/nacep_proposal.md, paper/indiana_statement.md;", len(desc.split()), "word description")
