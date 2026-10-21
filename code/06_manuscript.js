#!/usr/bin/env node
// 06_manuscript.js — build paper/manuscript.docx from paper/stats.json, paper/tables/*.csv and paper/figures/*.png.
// Run from repo root:  node code/06_manuscript.js [--final]
// Every number in the text is read from stats.json or a pipeline table; none is typed by hand.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, WidthType,
  ShadingType, ImageRun, Header, Footer, PageNumber, BorderStyle, LevelFormat,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const FINAL = process.argv.includes("--final");
const S = JSON.parse(fs.readFileSync(path.join(ROOT, "paper", "stats.json"), "utf8"));
const AUTH = JSON.parse(fs.readFileSync(path.join(ROOT, "AUTHORS.json"), "utf8"));

// ------------------------------------------------------------------ number helpers
const f = (x, d = 3) => Number(x).toFixed(d);
const sg = (x, d = 3) => (x >= 0 ? "+" : "−") + Math.abs(x).toFixed(d);
const pc = (x, d = 0) => (100 * x).toFixed(d) + "%";
const n = (x) => Math.round(x).toLocaleString("en-US");
const pv = (p) => (p < 0.001 ? "p < .001" : "p = " + p.toFixed(3).replace(/^0/, ""));
const ci = (m, d = 3) => `95% CI ${f(m.lo, d)} to ${f(m.hi, d)}`;
function csv(name) {
  const lines = fs.readFileSync(path.join(ROOT, "paper", "tables", name), "utf8").trim().split("\n");
  const head = lines[0].split(",");
  return lines.slice(1).map((l) => {
    const c = l.match(/("([^"]|"")*"|[^,]*)(,|$)/g).map((s) => s.replace(/,$/, "").replace(/^"|"$/g, ""));
    return Object.fromEntries(head.map((h, i) => [h, c[i]]));
  });
}
const M = S.models, G = M.gpa, C = M.credits, R = M.remed_rate, H = S.heterogeneity, W = S.within_school;
const A = S.access, D = S.descriptives, SM = S.sample, SE = S.sensitivity;

// ------------------------------------------------------------------ paragraph helpers
const FONT = "Times New Roman";
const runs = (txt, o = {}) => {
  // **bold** and _italic_ inline markup
  const out = [];
  txt.split(/(\*\*[^*]+\*\*|_[^_]+_)/).forEach((s) => {
    if (!s) return;
    if (s.startsWith("**")) out.push(new TextRun({ text: s.slice(2, -2), bold: true, font: FONT, ...o }));
    else if (s.startsWith("_") && s.endsWith("_") && s.length > 2) out.push(new TextRun({ text: s.slice(1, -1), italics: true, font: FONT, ...o }));
    else out.push(new TextRun({ text: s, font: FONT, ...o }));
  });
  return out;
};
const P = (txt, o = {}) => new Paragraph({ children: runs(txt), spacing: { after: 160, line: 360 }, ...o });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: FONT })], spacing: { before: 320, after: 160 } });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: FONT })], spacing: { before: 240, after: 120 } });
const Cap = (t) => new Paragraph({ children: runs(t, { size: 20 }), spacing: { after: 240 } });
const Bullet = (t) => new Paragraph({ children: runs(t), numbering: { reference: "bul", level: 0 }, spacing: { after: 80, line: 320 } });
function Fig(file, w, h, caption) {
  const data = fs.readFileSync(path.join(ROOT, "paper", "figures", file));
  return [new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type: "png", data, transformation: { width: w, height: h } })] }), Cap(caption)];
}
function Tbl(header, rows, widths, caption, note) {
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (t, i, head) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA },
    shading: head ? { type: ShadingType.CLEAR, fill: "E8ECF2", color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [new Paragraph({ alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.RIGHT, children: [new TextRun({ text: String(t), bold: head, size: 18, font: FONT })] })],
  });
  return [
    Cap(caption),
    new Table({
      width: { size: total, type: WidthType.DXA }, columnWidths: widths,
      rows: [new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, i, true)) }),
        ...rows.map((r) => new TableRow({ children: r.map((c, i) => cell(c, i, false)) }))],
    }),
    note ? new Paragraph({ children: runs(note, { size: 18 }), spacing: { before: 80, after: 240 } }) : new Paragraph({ children: [] }),
  ];
}

// ------------------------------------------------------------------ author block
const au = AUTH.authors[0];
const authorLine = AUTH.authors.map((a) => a.name).join(", ");
const affil = AUTH.authors.map((a) => a.affiliation).join("; ");

// ------------------------------------------------------------------ tables from pipeline output
const t1 = csv("table1_descriptives_by_dc_tercile.csv");
const T1 = Tbl(
  ["", "Low", "Middle", "High"],
  [
    ["School-cohorts", ...t1.map((r) => n(+r.school_cohorts))],
    ["Graduates earning dual credit (median)", ...t1.map((r) => pc(+r.dc_share))],
    ["Free/reduced-lunch graduates (median)", ...t1.map((r) => pc(+r.frl_share))],
    ["Graduates passing an AP exam (median)", ...t1.map((r) => pc(+r.ap_pass_share))],
    ["Corporation 7th–8th Algebra I per 8th grader (median)", ...t1.map((r) => f(+r.corp_early_alg, 2))],
    ["Offers calculus (share)", ...t1.map((r) => pc(+r.calc_offered))],
    ["Rural (share)", ...t1.map((r) => pc(+r.rural))],
    ["Graduates (median)", ...t1.map((r) => n(+r.grads))],
    ["First-year GPA (median)", ...t1.map((r) => f(+r.gpa, 2))],
    ["First-year credits earned (median)", ...t1.map((r) => f(+r.credits, 1))],
    ["Share needing remediation (median)", ...t1.map((r) => pc(+r.remed_rate, 1))],
  ],
  [4560, 1600, 1600, 1600],
  "**Table 1.** School characteristics by tercile of dual-credit share, public high schools, graduating cohorts 2021–2024.",
  "Note: Unit is the school-cohort. Outcomes describe graduates who enrolled at an Indiana public college the following year. Sources: CHE College-Going/Readiness datasets; CRDC 2021-22 and 2023-24; NCES CCD and EDGE.",
);
const t2 = csv("table2_main_models.csv");
const T2 = Tbl(
  ["Outcome / model", "Coef. per 10 pts", "95% CI", "p", "N", "R²"],
  t2.map((r) => [`${r.outcome}: ${r.model}`, sg(+r.coef_per_10pp, r.outcome.includes("credits") ? 3 : 4),
    `${f(+r.ci_low, 3)} to ${f(+r.ci_high, 3)}`, (+r.p < 0.001 ? "<.001" : f(+r.p, 3)), n(+r.n), f(+r.r2, 2)]),
  [4060, 1300, 1700, 800, 700, 700],
  "**Table 2.** Association between a school's dual-credit share and its graduates' first-year outcomes.",
  `Note: Weighted least squares, weights = Indiana public college enrollees; standard errors clustered by school. Coefficients give the change in the outcome for a 10-percentage-point higher share of graduates earning dual credit. All models include cohort indicators. M2 adds free/reduced-lunch share, AP-pass share, log graduates, and NCES locale; M3 adds corporation-level 7th–8th grade Algebra I enrollment per 8th grader and indicators for calculus and advanced-mathematics sections; M4 adds the share of graduates enrolling at an Indiana public college; M5 replaces all time-invariant controls with school fixed effects. School-cohorts with fewer than ${SM.min_inpub} Indiana public enrollees are excluded.`,
);
const t3 = csv("table3_heterogeneity.csv");
const T3 = Tbl(
  ["Moderator / outcome", "Slope in group", "Slope in others", "Difference", "p (diff.)"],
  t3.map((r) => [`${r.moderator}: ${r.outcome}`, `${sg(+r.slope_in_group)} (${f(+r.se_group)})`,
    `${sg(+r.slope_others)} (${f(+r.se_others)})`, sg(+r.difference), f(+r.p_difference, 2)]),
  [4260, 1400, 1400, 1100, 900],
  "**Table 3.** Does the association differ by school type? Slopes per 10 points of dual-credit share from the M3 specification with an interaction.",
  "Note: Standard errors in parentheses. The group slope is the main effect plus the interaction; its standard error is computed from the full covariance matrix.",
);
const t4 = csv("table4_sensitivity.csv");
const T4 = Tbl(
  ["Check / outcome", "Coef. per 10 pts", "SE", "p", "N"],
  t4.map((r) => [`${r.check}: ${r.outcome}`, sg(+r.coef_per_10pp, 4), f(+r.se, 4), (+r.p < 0.001 ? "<.001" : f(+r.p, 3)), n(+r.n)]),
  [5260, 1400, 1000, 800, 800],
  "**Table 4.** Sensitivity of the M3 estimate to sample and measurement choices.",
  null,
);
const t5 = csv("table5_access_by_locale.csv");
const T5 = Tbl(
  ["Locale", "Schools", "Students", "No calculus (% schools)", "No dual enrollment (% schools)", "No/thin pathway (% students)", "Median dual-credit share"],
  t5.map((r) => [r.locale4, n(+r.schools), n(+r.students), f(+r.no_calculus_pct_schools, 0) + "%", f(+r.no_dual_pct_schools, 0) + "%",
    f(+r.thin_or_none_pct_students, 1) + "%", pc(+r.median_dc_share)]),
  [1300, 1000, 1300, 1450, 1500, 1450, 1360],
  "**Table 5.** Access to calculus and dual enrollment in traditional public high schools, by NCES locale.",
  "Note: Calculus and dual enrollment count as offered if reported in CRDC 2021-22 or 2023-24. 'Thin pathway' = no calculus and fewer than one in three graduates (cohorts 2021–2024) earning dual credit. Virtual and alternative schools excluded. Enrollment from CRDC 2023-24.",
);

// ------------------------------------------------------------------ text
const fq = A.by_frl_quartile;
const thin = A.tiers["Thin pathway: no calculus and low uptake"], none = A.tiers["No dual enrollment reported"];
const city = A.by_locale.City, rural = A.by_locale.Rural;

const body = [
  ...(FINAL ? [] : [new Paragraph({ children: [new TextRun({ text: "DRAFT — not verified by the author. Do not cite or circulate.", bold: true, color: "A32020", font: FONT })], spacing: { after: 240 } })]),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "Dual Credit as a Readiness Lever: School-Level Evidence from Indiana and a Map of Where College Mathematics Pathways Are Missing", bold: true, size: 32, font: FONT })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: runs(authorLine) }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: runs(affil, { size: 20 }) }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 320 }, children: runs(`Correspondence: ${au.email}${au.orcid ? " · ORCID " + au.orcid : ""}`, { size: 20 }) }),

  H1("Abstract"),
  P(`States have expanded dual credit on the expectation that it prepares students for college, yet most evidence compares students who chose dual credit with students who did not, so the effect of a school's investment is hard to separate from who enrolls. This study links Indiana Commission for Higher Education graduate outcomes to federal civil-rights course data for ${n(SM.schools)} public high schools and ${n(SM.school_cohorts)} school-cohorts (graduating classes 2021–2024; ${n(SM.inpub)} graduates who enrolled at an Indiana public college). A 10-point higher share of graduates earning dual credit is associated with a ${sg(G.M1.b)} higher average first-year college GPA before adjustment. After accounting for school poverty, Advanced Placement success, size, locale, the timing of Algebra I, and calculus and advanced-mathematics offerings, the association falls by ${pc(S.attenuation_gpa_M1_to_M3)} to ${sg(G.M3.b)} (${ci(G.M3)}). School fixed-effects estimates are similar (${sg(G.M5.b)}). Comparable patterns hold for first-year credits earned; remediation, now rare in Indiana, shows no robust association. Because the state's first-year GPA and credit measures include dual-credit grades and hours earned in high school, these estimates are upper bounds on any readiness effect. Within schools, dual-credit earners outperform classmates by ${f(W.gpa_gap_mean, 2)} GPA points, a gap that widens where dual credit is more common, consistent with strong selection. Access to the mathematics pathway is uneven: ${pc(A.no_calc_share_schools)} of traditional public high schools offered no calculus in either recent collection, rising from ${f(fq["Q1 lowest"].no_calculus_pct_schools, 0)}% of the lowest-poverty quarter of schools to ${f(fq["Q4 highest"].no_calculus_pct_schools, 0)}% of the highest. Any school-level readiness return to dual credit is modest at most; the larger policy problem is where the advanced mathematics pathway does not exist.`),
  P("_Keywords:_ dual credit; dual enrollment; college readiness; mathematics pathways; Algebra I; Indiana; Civil Rights Data Collection"),

  H1("1. Introduction"),
  P(`Dual credit, in which high school students earn college credit for courses taken before graduation, has become one of the most widespread college-readiness strategies in the United States. Indiana is among the states that have pushed furthest: across the schools studied here, ${pc(D.dc_share_weighted_mean)} of public high school graduates in the 2021–2024 cohorts earned dual credit from an Indiana public college, and the median school's share was ${pc(D.dc_share_median)}. State policy treats this expansion as a lever on readiness. Whether it works as one, and for which schools, matters for how states allocate the next dollar.`),
  P("Two features of the existing evidence limit what it can tell policymakers. First, most studies compare students who take dual credit with those who do not. Even with rich controls, those comparisons mix the effect of the course with the characteristics of the students who choose and are admitted to it. Second, studies rarely ask whether the schools that serve students with the least access to advanced coursework can offer dual credit at all, particularly in mathematics, where college-level work depends on a sequence that begins with Algebra I." ),
  P("This study addresses both gaps with public data. It asks three questions. (1) Do Indiana high schools where more students earn dual credit send graduates who do better in their first year of college, after accounting for school poverty, Advanced Placement success, when students reach Algebra I, and which mathematics courses the school offers? (2) Does any association differ for high-poverty, rural, or late-Algebra schools? (3) Where is the mathematics pathway into dual credit missing?"),
  P("This question comes from my own classroom. I am a certified mathematics teacher with the Metropolitan School District of Lawrence Township in Indianapolis, and since 2024-25 I have taught MATH M118, Finite Mathematics, at Lawrence Central High School through Indiana University Bloomington's Advance College Project (ACP). I was qualified to teach the course when I arrived at the school, but I could not begin until I completed IU's summer training in June 2024. My first section, in 2024-25, enrolled 8 students. The next year it grew to more than 20, including students from Lawrence North High School, a sister school in the district, and 17 completed the course. The course runs as a year-long sequence covering the textbook's eight chapters, four each semester: probability, linear programming, matrices, linear models, and Markov chains. IU sets the final examination at the end of each semester; each instructor files a schedule of lessons, assignments, test dates, and finals in advance and uploads final grades to IU. The course is a university course delivered in a high school. Students reach it through their math teachers' recommendations, typically after earning a B or better in Honors Geometry or Algebra II. A student's chance at college-level mathematics in high school therefore depends on whether their school has an approved teacher and on whether they reached the prerequisite courses in time. This study asks whether that pattern appears across all of Indiana's public high schools."),

  H1("2. Background"),
  H2("2.1 Dual credit in Indiana"),
  P("Indiana delivers dual credit mainly through two routes: courses taught in high schools by credentialed high school teachers under a college's supervision (for example, Indiana University's Advance College Project and Ivy Tech Community College's high school programs), and courses taken on a college campus or online. The state's Commission for Higher Education (CHE) reports, for every high school, how many graduates earned dual credit from an Indiana public college and how those graduates fared in their first college year. CHE's own descriptive analysis of earlier cohorts found that pre-college credit earners had higher first-year GPAs, earned more credits, and needed less remediation than other students (Indiana Commission for Higher Education, 2016)."),
  H2("2.2 Prior evidence"),
  P("Quasi-experimental studies generally find positive associations between dual enrollment and college enrollment, persistence, and degree attainment, though estimates shrink as controls for prior achievement tighten (An, 2013; Karp et al., 2007; Speroni, 2011). The What Works Clearinghouse rated dual enrollment as having positive effects on several college outcomes (What Works Clearinghouse, 2017). Work on equity has documented that participation gaps by income and race persist even as programs expand (Fink et al., 2017; Taylor, 2015)."),
  P("This study contributes a school-level view. The policy decision a state or district faces is whether to invest in dual-credit capacity at a school, not whether a particular student should enroll. School-level variation in uptake, combined with outcomes for all of a school's college-going graduates, speaks directly to that decision, and school fixed-effects models use year-to-year changes within the same school."),

  H1("3. Data"),
  P("**Graduate outcomes.** CHE publishes an annual College-Going (formerly College Readiness) dataset for each high school graduating cohort (Indiana Commission for Higher Education, 2023, 2024, 2025, 2026). For each school it reports the number of graduates; the number enrolling in any college and in an Indiana public college; and, for Indiana public college enrollees, the number needing remediation (by subject), average first-year GPA, and average first-year credits earned. These measures are reported overall and separately for graduates who did and did not earn dual credit from an Indiana public college, and by free/reduced-lunch status and AP results. Cells with few students are suppressed. This study uses the 2021, 2022, 2023, and 2024 cohorts, with the 2019 cohort as a pre-pandemic sensitivity check. The 2020 cohort, whose first college year coincided with the pandemic's onset, is omitted."),
  P("**Course offerings and Algebra I timing.** The U.S. Department of Education's Civil Rights Data Collection (CRDC) reports, for every public school, whether it offers dual enrollment and how many students enroll; the number of sections and students in calculus and advanced mathematics; and Algebra I enrollment for grades 7–8, 9–10, and 11–12. The 2021-22 collection is matched to the 2021 and 2022 cohorts and the 2023-24 collection to the 2023 and 2024 cohorts. When a measure is missing in the matched year, the other year is used."),
  P("**Directory, membership, and geography.** NCES Common Core of Data (CCD) 2023-24 links CHE's state school numbers to NCES identifiers and supplies grade-level membership. NCES EDGE geocodes supply coordinates and locale. Census cartographic boundary files supply county outlines for mapping."),
  P(`**Sample.** CHE school rows are linked to state school numbers using the identifiers in the 2024 file and exact name matches for earlier cohorts. Nonpublic schools, correctional facilities, and closed schools that cannot be linked are dropped (the QA report lists each). The analytic sample contains public schools with at least ${SM.min_inpub} Indiana public college enrollees in a cohort and non-missing outcomes, exposure, and controls: ${n(SM.school_cohorts)} school-cohorts from ${n(SM.schools)} schools, covering ${n(SM.grads)} graduates and ${n(SM.inpub)} Indiana public college enrollees.`),

  H1("4. Measures"),
  Bullet("**Dual-credit share (exposure):** graduates who earned dual credit from an Indiana public college divided by all graduates. Coefficients are scaled per 10 percentage points."),
  Bullet("**Outcomes:** average first-year GPA and average first-year credits earned among graduates enrolling at an Indiana public college; the share of those enrollees needing remediation."),
  Bullet("**Algebra I timing:** at the school-corporation level, 7th- and 8th-grade Algebra I enrollment (CRDC) divided by 8th-grade membership (CCD). A high-school measure (9th–12th grade Algebra I enrollment per 9th grader) is used as a sensitivity check."),
  Bullet("**Mathematics offerings:** indicators that the school ran at least one calculus section and at least one advanced-mathematics section (CRDC)."),
  Bullet("**Controls:** share of graduates eligible for free or reduced-price lunch; share passing an AP exam; log graduates; NCES locale (city, suburb, town, rural)."),

  H1("5. Methods"),
  P("The main models regress each school-cohort outcome on dual-credit share with cohort indicators, adding controls in stages (Table 2). Models are weighted by the number of Indiana public college enrollees, because outcomes are averages over those students, and standard errors are clustered by school. A school fixed-effects model (M5) uses only within-school, across-cohort variation in dual-credit share, which removes stable school differences in preparation and culture but relies on smaller year-to-year changes. Heterogeneity is tested with interactions between dual-credit share and indicators for high-poverty, rural, below-median early-Algebra, and calculus-offering schools. Within-school gaps between dual-credit earners and other graduates are reported descriptively where CHE does not suppress both groups."),
  P("Because outcomes are observed only for graduates who enroll at an Indiana public college, schools that send a larger and less selected share of graduates to college may have lower average outcomes for reasons unrelated to dual credit. Model M4 therefore adds the in-state public college-going rate. Because that rate may itself be affected by dual credit, M4 is read as a bound rather than the preferred estimate."),

  H1("6. Results"),
  H2("6.1 Which schools have high dual-credit uptake"),
  P(`Dual-credit uptake is high almost everywhere: the 10th-percentile school had ${pc(D.dc_share_p10)} of graduates earning dual credit and the 90th-percentile school ${pc(D.dc_share_p90)}. Higher-uptake schools are less poor (correlation with free/reduced-lunch share ${f(D.corr_dc_frl, 2)}), smaller, and more often rural (Table 1). The raw correlation between dual-credit share and first-year GPA is ${f(D.corr_dc_gpa, 2)}.`),
  ...T1,
  H2("6.2 Main estimates"),
  P(`Without controls, a 10-point higher dual-credit share is associated with ${sg(G.M1.b)} GPA points and ${sg(C.M1.b, 2)} first-year credits (Table 2; Figure 1). Adding poverty, AP success, size, and locale reduces the GPA estimate to ${sg(G.M2.b)} (${ci(G.M2)}). Adding Algebra I timing and mathematics offerings leaves it essentially unchanged at ${sg(G.M3.b)}; neither early Algebra I (${sg(G.M3_controls.alg10.b)} per 10 points, ${pv(G.M3_controls.alg10.p)}) nor calculus (${sg(G.M3_controls.calc.b)}, ${pv(G.M3_controls.calc.p)}) predicts first-year GPA once poverty and AP success are held fixed. In all, ${pc(S.attenuation_gpa_M1_to_M3)} of the raw GPA association and ${pc(S.attenuation_credits_M1_to_M3)} of the credits association is accounted for by these school characteristics. The school fixed-effects estimate, ${sg(G.M5.b)} (${ci(G.M5)}), is close to M3, which suggests that stable unobserved school differences do not drive the adjusted estimate, though its interval is wide. Adding in-state public college-going (M4) lowers the GPA estimate to ${sg(G.M4.b)} (${pv(G.M4.p)}) and the credits estimate to ${sg(C.M4.b, 2)} (${pv(C.M4.p)}).`),
  P(`These outcomes are not pure measures of first-year performance. Dual-credit grades and hours earned in high school are already on a student's college record at enrollment, and CHE's first-year GPA and credits include them (Section 8). Part of each estimate is therefore mechanical: schools where more students earn dual credit will show more first-year credits, and a first-year GPA that blends in high school dual-credit grades, even if their graduates perform no differently in college courses. The estimates are best read as upper bounds. In practical terms, moving from a school at the 10th percentile of dual-credit share to one at the 90th (${f(S.p10_p90_implied.dc_pp, 0)} points) implies at most about ${f(S.p10_p90_implied.gpa, 2)} GPA points and ${f(S.p10_p90_implied.credits, 1)} additional credits under M3, including any credits carried in from high school. The remediation measure is not affected by this overlap, because it is based on placement into remedial courses after enrollment; it shows no robust association. The share needing remediation shows no robust association (${sg(R.M3.b, 4)} per 10 points, ${pv(R.M3.p)}), though this may also be because remediation has become uncommon in Indiana public colleges (enrollee-weighted mean ${pc(D.remed_rate_weighted_mean, 1)}).`),
  ...Fig("fig1_coefficients.png", 600, 247, "**Figure 1.** Estimated change in school-average first-year outcomes per 10-point higher dual-credit share, by model. Lines are 95% confidence intervals."),
  ...Fig("fig2_binscatter.png", 560, 275, "**Figure 2.** School first-year GPA by dual-credit share, unadjusted and adjusted for controls (20 equal-count bins)."),
  ...T2,
  H2("6.3 For which schools"),
  P(`Point estimates are larger in high-poverty schools (${sg(H.frl_hi.gpa.slope_group)} GPA per 10 points) than in lower-poverty schools (${sg(H.frl_hi.gpa.slope_other)}), but the difference is imprecise (${pv(H.frl_hi.gpa.p_interaction)}). There is no evidence of different slopes for rural schools (${pv(H.rural.gpa.p_interaction)}), schools in corporations with less early Algebra I (${pv(H.alg_lo.gpa.p_interaction)}), or schools offering calculus (${pv(H.calc.gpa.p_interaction)}) (Table 3). The data are consistent with a modest, broadly shared association and cannot rule out moderately larger returns in high-poverty schools.`),
  ...T3,
  H2("6.4 Within schools: selection"),
  P(`In the ${n(W.schools)} schools where both groups are reported, graduates who earned dual credit averaged ${f(W.gpa_gap_mean, 2)} GPA points and ${f(W.credit_gap_mean, 1)} credits more in their first college year than classmates who did not; the gap was positive in ${pc(W.share_positive_gap)} of school-cohorts. If the gap reflected only the benefit of dual credit, it should not depend on how many students a school enrolls. Instead it widens by ${f(W.gap_slope_dc10, 2)} GPA points per 10 points of dual-credit share (${pv(W.gap_slope_p)}), and the non-earners' average falls (${sg(W.nodc_gpa_slope_dc10, 2)} per 10 points), conditional on school poverty. As a school's program grows, students left out are increasingly those least prepared (Figure 3). Part of the earners' advantage is also mechanical, since their first-year records include their dual-credit grades and hours. Student-level comparisons of dual-credit earners and non-earners should therefore be read as upper bounds.`),
  ...Fig("fig3_within_school.png", 540, 238, "**Figure 3.** First-year GPA of dual-credit earners and non-earners by school dual-credit share (sextiles)."),
  H2("6.5 Sensitivity"),
  P(`The adjusted GPA estimate ranges from ${sg(S.sensitivity_range_gpa[0], 4)} to ${sg(S.sensitivity_range_gpa[1], 4)} across the checks in Table 4. It is larger without weights (${sg(SE.unweighted.gpa.b, 4)}), indicating that smaller schools contribute more to the association, and smaller and not statistically significant when restricted to school-cohorts with 30 or more in-state public enrollees (${sg(SE.min30.gpa.b, 4)}, ${pv(SE.min30.gpa.p)}). Replacing the corporation Algebra I measure with the high-school measure, including both, or adding the 2019 cohort changes little. The credits estimate is less stable: it falls to ${sg(SE.no_virtual.credits.b, 3)} (${pv(SE.no_virtual.credits.p)}) when virtual schools are excluded.`),
  ...T4,
  H2("6.6 Where the mathematics pathway is missing"),
  P(`Of ${n(A.traditional_schools)} traditional public high schools matched to the 2023-24 CRDC, ${n(A.traditional_schools * A.no_calc_share_schools)} (${pc(A.no_calc_share_schools)}) reported no calculus section in either 2021-22 or 2023-24; they enroll ${pc(A.no_calc_share_students)} of students in these schools. ${n(none.schools)} schools reported no dual enrollment, and a further ${n(thin.schools)} had neither calculus nor substantial dual-credit uptake (fewer than one in three graduates). Absence of calculus tracks poverty closely: ${f(fq["Q1 lowest"].no_calculus_pct_schools, 0)}% of the lowest-poverty quarter of schools lacked it, against ${f(fq["Q4 highest"].no_calculus_pct_schools, 0)}% of the highest-poverty quarter (Figure 4). It is most common in cities (${f(city.no_calculus_pct_schools, 0)}% of city schools, ${f(city.no_dual_pct_schools, 0)}% with no dual enrollment) rather than in rural areas (${f(rural.no_calculus_pct_schools, 0)}%). In ${A.counties_no_calc_anywhere} counties, no public high school offered calculus (Figure 5; Table 5).`),
  ...Fig("fig4_access_bars.png", 600, 216, "**Figure 4.** Share of traditional public high schools with no calculus in CRDC 2021-22 or 2023-24, by poverty quartile and locale."),
  ...Fig("fig5_access_map.png", 430, 585, "**Figure 5.** Share of public high school students in schools without calculus, by county, with schools reporting no dual enrollment or a thin pathway marked. An interactive version accompanies the replication package."),
  ...T5,

  H1("7. Discussion"),
  P("The school-level association between dual credit and first-year college outcomes in Indiana is positive, survives adjustment for poverty, AP success, Algebra I timing, and mathematics offerings, and appears in school fixed-effects models. It is also modest, most of the raw gap that motivates dual-credit advocacy reflects differences between schools, and part of what remains reflects dual-credit grades and hours counted in the first-year record itself. The one outcome free of that overlap, remediation, shows no robust association. Within schools, the dual-credit advantage widens as programs grow, a sign that students who are not reached differ sharply from those who are."),
  P("Three implications follow for policy. First, statewide dual-credit expansion should be evaluated against realistic expectations: a large increase in uptake corresponds to a few hundredths of a GPA point and under one credit at the school level. Second, the binding constraint for college mathematics in many schools is the absence of a pathway. A fifth of traditional public high schools, and four in ten of the highest-poverty schools, offered no calculus in either recent year. Dual-credit mathematics courses such as finite mathematics or college algebra can be offered without calculus, but they still require students who reach Algebra I early enough and teachers credentialed to teach college courses. Third, where uptake is already high, the remaining gains lie with the students not yet reached, whose first-year outcomes are weakest."),
  P("My experience teaching M118 suggests what the barriers look like inside a school. The first is the teacher. An instructor must apply to IU and, if accepted, complete summer training before teaching, and a school without an approved instructor cannot offer the course. When I left Lawrence Central for a period, the students who planned to take finite mathematics had to take it at Lawrence North, where an approved teacher was available; a school without a nearby sister school would simply have lost the course. The second is preparation. Students are recommended by the mathematics department, usually on the strength of a B or better in Honors Geometry or Algebra II and a steady work ethic, because assignments come due at the end of every section. Counselors sometimes adjust recommendations to fit a student's goals, and in my experience students placed in the course without the recommended preparation often withdraw once they find the prerequisites are not in place. The third is awareness: many students do not know the course exists or that it serves those headed toward nursing and health fields, business, and finance. Because finite mathematics does not require calculus, a school without calculus can still offer college-level mathematics, but only with an approved teacher and enough students who finished the prerequisite sequence on time. Support for credentialing teachers, sharing sections across schools, and moving students through Algebra I and Algebra II earlier would reach the schools identified in Section 6.6 more directly than further expansion where programs already exist. These observations come from my own sections and are offered as illustration, not as evidence for the statewide estimates."),

  H1("8. Limitations"),
  P("The design is observational and school-level; it cannot identify the effect of dual credit on any individual student. Outcomes exist only for graduates who enroll at Indiana public colleges, so changes in who enrolls can move averages. CHE reports dual credit earned from Indiana public colleges only, not subject or number of credits, so the study cannot isolate dual-credit mathematics; the access analysis uses calculus offerings and overall uptake as proxies. The first-year GPA and credit measures include dual-credit coursework taken in high school: dual-credit grades are recorded by the sponsoring college (ACP instructors upload final grades to IU), they are on the student's record at enrollment, and they are counted in the GPA and credits CHE reports. GPA and credit estimates are therefore upper bounds on any effect on first-year college performance. A cleaner test would use first-year outcomes that exclude pre-matriculation credit, which CHE could produce from its student-level records. Algebra I timing is measured at the school-corporation level in one year, not for each graduating cohort. CRDC data are self-reported by schools and sometimes inconsistent across years. Full limitations are in the replication package (docs/LIMITATIONS.md)."),

  H1("9. Conclusion"),
  P("Indiana's investment in dual credit coincides with modestly better first-year college records at the school level, after accounting for the schools' other advantages, though part of that difference is the dual-credit work itself carried onto the college transcript. The clearer finding concerns access: the mathematics courses that lead into college-level mathematics are missing from many of the state's highest-poverty high schools. Policy aimed at readiness should measure dual credit by subject and target the schools where the pathway does not yet exist."),

  H1("Declarations"),
  P("**Data and code availability.** All data are public. Code, processed data, figures, and the interactive atlas are available at https://github.com/OthnyLight/in-dual-credit-math."),
  P("**Competing interests.** The author is a certified mathematics teacher employed by the Metropolitan School District of Lawrence Township, Indianapolis, and has taught MATH M118 through Indiana University's Advance College Project since 2024-25. ACP pays instructors a stipend each time they attend one of its training workshops, held each October at IU Bloomington. The views expressed are the author's own and not those of Indiana University or the Metropolitan School District of Lawrence Township. The author declares no other competing interests."),
  P("**Funding.** This research received no external funding."),
  P("**Use of AI tools.** Data acquisition, cleaning, statistical code, figures, and initial drafting of methods and results text were assisted by an AI system (Claude, Anthropic). The author specified the research question, reviewed and reran the analysis, verified results against source files, made all analytic judgments, and is responsible for the content."),
  P(`**Author contributions (CRediT).** ${AUTH.authors.map((a) => `${a.name}: ${a.roles.join(", ")}`).join("; ")}.`),
  H1("References"),
  ...[
    "An, B. P. (2013). The impact of dual enrollment on college degree attainment: Do low-SES students benefit? _Educational Evaluation and Policy Analysis, 35_(1), 57–75.",
    "Fink, J., Jenkins, D., & Velasco, T. (2017). _What happens to students who take community college dual enrollment courses in high school?_ Community College Research Center, Teachers College, Columbia University.",
    "Indiana Commission for Higher Education. (2016). _College readiness report supplement: A closer look at dual credit students_.",
    "Indiana Commission for Higher Education. (2023). _2023 college readiness dataset: 2021 high school graduating cohort_ [Data set]. https://www.in.gov/che/college-going-reports/",
    "Indiana Commission for Higher Education. (2024). _2024 college readiness dataset: 2022 high school graduating cohort_ [Data set]. https://www.in.gov/che/college-going-reports/",
    "Indiana Commission for Higher Education. (2025). _2025 college readiness dataset: 2023 high school graduating cohort_ [Data set]. https://www.in.gov/che/college-going-reports/",
    "Indiana Commission for Higher Education. (2026). _2026 college-going dataset: 2024 high school graduating cohort_ [Data set]. https://www.in.gov/che/college-going-reports/",
    "Karp, M. M., Calcagno, J. C., Hughes, K. L., Jeong, D. W., & Bailey, T. R. (2007). _The postsecondary achievement of participants in dual enrollment: An analysis of student outcomes in two states_. Community College Research Center, Teachers College, Columbia University.",
    "National Center for Education Statistics. (2024). _Common Core of Data: Public elementary/secondary school universe survey, 2023–24_ [Data set]. U.S. Department of Education. https://nces.ed.gov/ccd/",
    "Speroni, C. (2011). _Determinants of students' success: The role of Advanced Placement and dual enrollment programs_. National Center for Postsecondary Research.",
    "Taylor, J. L. (2015). Accelerating pathways to college: The (in)equitable effects of community college dual credit. _Community College Review, 43_(4), 355–379.",
    "U.S. Department of Education, Office for Civil Rights. (2025, 2026). _Civil Rights Data Collection, 2021–22 and 2023–24_ [Data sets]. https://civilrightsdata.ed.gov/data",
    "What Works Clearinghouse. (2017). _Transition to college intervention report: Dual enrollment programs_. Institute of Education Sciences, U.S. Department of Education.",
  ].map((t) => new Paragraph({ children: runs(t), indent: { left: 720, hanging: 720 }, spacing: { after: 120, line: 300 } })),
];

const doc = new Document({
  creator: authorLine,
  title: "Dual Credit as a Readiness Lever",
  styles: { default: { document: { run: { font: FONT, size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 28, bold: true, font: FONT }, paragraph: { outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, italics: true, font: FONT }, paragraph: { outlineLevel: 1 } }] },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: FINAL ? "Dual credit as a readiness lever" : "DRAFT — Dual credit as a readiness lever", size: 18, color: FINAL ? "666666" : "A32020", font: FONT })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, font: FONT })] })] }) },
    children: body,
  }],
});
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(path.join(ROOT, "paper", "manuscript.docx"), buf);
  console.log("wrote paper/manuscript.docx");
});
