# Codebook

## data/processed/school_cohort_panel.csv

One row per public high school × graduating cohort (2019, 2021–2024), Indiana public schools linked to NCES. Built by `code/02_build.py`.

| Column | Definition | Source | Transformation |
|---|---|---|---|
| idoe_sch | Indiana DOE school number (4 digits) | CHE `LocationId` (2024); name match for earlier cohorts | zero-padded |
| cohort | High school graduating year | CHE | |
| che_name | School name as reported by CHE | CHE `Location` | |
| grads | High school graduates | CHE Average row `HSGrads` | |
| enr_any | Graduates enrolling in any college (NSC-participating) | CHE `EnrCollegeN` | |
| enr_inpub | Graduates enrolling in an Indiana public college | CHE `EnrINPubCollegeN` | |
| need_remed | Indiana public enrollees needing remediation | CHE `NeedRemedN` | |
| gpa | Average first-year GPA, Indiana public enrollees | CHE `AvgFreshmanGPA` | 'DS' (suppressed) → missing |
| credits | Average first-year credits earned, Indiana public enrollees | CHE `AvgFreshmanCreditEarned` | 'DS' → missing |
| dc_n / nodc_n | Graduates who did / did not earn dual credit from an Indiana public college | CHE Dual Credit breakout `HSGrads` | a suppressed half is recovered as total minus the other half |
| dc_inpub / nodc_inpub | Indiana public enrollees in each dual-credit group | CHE Dual Credit breakout | |
| dc_gpa / nodc_gpa, dc_credits / nodc_credits | First-year GPA and credits by dual-credit group | CHE Dual Credit breakout | |
| frl_n / nonfrl_n | Graduates eligible / not eligible for free or reduced lunch | CHE Socioeconomic Status breakout | recovered as above |
| ap_pass_n | Graduates who took and passed an AP exam | CHE Advanced Placement breakout | missing → 0 when total present |
| rem_math_only / rem_both | Enrollees needing math-only / math-and-ELA remediation | CHE Remediation Type breakout | |
| dc_share | dc_n / grads | derived | |
| frl_share | frl_n / grads | derived | |
| ap_pass_share | ap_pass_n / grads | derived | |
| inpub_rate | enr_inpub / grads | derived | |
| college_rate | enr_any / grads | derived | |
| remed_rate | need_remed / enr_inpub | derived | |
| math_remed_rate | (rem_math_only + rem_both) / enr_inpub | derived | 0 when need_remed = 0 |
| dc_gpa_gap, dc_credit_gap | dual-credit minus non-dual-credit GPA / credits | derived | |
| NCESSCH | NCES 12-digit school ID | CCD 2023-24 directory | joined on IDOE number from `ST_SCHID` |
| idoe_corp | IDOE corporation number | CCD `ST_LEAID` | |
| LEAID, SCH_NAME, LEA_NAME, SCH_TYPE_TEXT, CHARTER_TEXT, LEVEL, G_12_OFFERED, SY_STATUS_TEXT | directory fields | CCD 2023-24 | |
| crdc_year | CRDC collection matched to the cohort | 2021-22 for cohorts 2019–2022; 2023-24 for 2023–2024 | |
| SCH_DUAL_IND | School reports dual enrollment | CRDC Dual Enrollment | |
| dual_n | Students in dual enrollment | CRDC `TOT_DUALENR_M/F/X` | summed; negative reserve codes → missing |
| calc_classes, calc_n | Calculus sections, students | CRDC Calculus | |
| advm_classes, advm_n | Advanced-mathematics sections, students | CRDC Advanced Mathematics | |
| alg78_n, alg910_n, alg1112_n | Algebra I enrollment, grades 7–8, 9–10, 11–12 | CRDC Algebra I | |
| enr_total | Total school enrollment | CRDC Enrollment | |
| g8, g9 | Grade 8 and 9 membership | CCD membership (052), year matched to CRDC | |
| hs_alg_rate | (alg910_n + alg1112_n) / g9 | derived; g9 ≥ 20 | capped at 1.2 in analysis |
| corp_early_alg | Σ alg78_n / Σ g8 across the school's LEA | derived; LEA g8 ≥ 20 | capped at 1.0 in analysis |
| dual_any | dual enrollment indicator Yes and dual_n > 0 | derived | |
| calc_offered, advm_offered | at least one section | derived | |
| dual_rate_crdc, calc_rate | dual_n / enr_total, calc_n / enr_total | derived | |
| CNTY, NMCNTY, LOCALE, LAT, LON | county FIPS and name, NCES locale code, coordinates | EDGE 2023-24 | |
| locale4 | City / Suburb / Town / Rural | first digit of LOCALE | |
| virtual | school is virtual | CRDC `SCH_VIRT_IND` or name contains Virtual/Online/eAcademy/Digital | |

## data/processed/school_access.csv and school_access_tiers.csv

One row per open Indiana public school offering grade 12 in CCD 2023-24 (Department of Correction facilities excluded). Columns as above, plus:

| Column | Definition |
|---|---|
| calc_offered_2122, dual_any_2122 | the same indicators from CRDC 2021-22 |
| calc_either, dual_either | offered in CRDC 2021-22 or 2023-24 |
| dc_share_pooled | Σ dc_n / Σ grads over cohorts 2021–2024 |
| frl_share_pooled | Σ frl_n / Σ grads over cohorts 2021–2024 |
| grads_pooled | Σ grads, cohorts 2021–2024 |
| alt | alternative school (CRDC) or CCD type other than Regular School |
| enr | enr_total (CRDC 2023-24) |
| tier | Virtual or alternative · No dual enrollment reported · Thin pathway: no calculus and low uptake (dc_share_pooled < 1/3 or missing) · Dual credit, but no calculus · Dual credit and calculus |

## paper/stats.json

Every number quoted in the manuscript, proposal, statement, and headlines. Coefficients (`b`) are per 10 percentage points of dual-credit share, with standard errors (`se`), p-values (`p`), and 95% CI bounds (`lo`, `hi`).
