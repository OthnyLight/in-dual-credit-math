# Limitations

Written before the discussion section of the manuscript. The paper may not claim anything this file rules out.

1. **School-level, observational design.** Estimates relate a school's share of graduates earning dual credit to the average first-year outcomes of its college-going graduates. They do not identify the effect of dual credit on any individual student, and schools that expand dual credit may differ in ways the controls do not capture. The school fixed-effects model removes stable school differences but rests on year-to-year changes in uptake, which are small and noisy.

2. **Outcomes cover only Indiana public college enrollees.** CHE reports GPA, credits, and remediation only for graduates who enroll at an Indiana public college the next year (about a third of graduates at the median school). If dual credit changes who enrolls, average outcomes can move for reasons unrelated to readiness. Model M4 conditions on in-state public enrollment as a bound. Graduates who enroll out of state or at private colleges are not observed.

3. **Dual credit is not observed by subject or volume.** CHE records whether a graduate earned any dual credit from an Indiana public college, not the subject or number of credits, and it excludes dual credit from private or out-of-state colleges. The study therefore cannot isolate dual-credit mathematics. The access analysis approximates the mathematics pathway with CRDC calculus sections and overall dual-credit uptake. A school without calculus may still offer dual-credit finite mathematics or college algebra.

4. **Mechanical overlap in outcomes.** CHE's first-year GPA and credits include dual-credit coursework taken in high school (author's account: dual-credit grades are recorded by the sponsoring college, e.g., ACP instructors upload final grades to IU, and are on the student's record at enrollment). Schools with more dual-credit earners therefore show more first-year credits and a GPA that blends in high school dual-credit grades regardless of college performance. GPA and credit estimates are upper bounds on any readiness effect. Remediation is not affected and shows no robust association. Asking CHE for first-year outcomes that exclude pre-matriculation credit is the priority next step (docs/NEXT_STEPS.md).

5. **Algebra I timing is a proxy.** CRDC reports 7th–8th grade Algebra I enrollment at middle schools, not at the high school a student later attends. The main measure is the school corporation's 7th–8th grade Algebra I enrollment per 8th grader in the matched CRDC year; it does not follow each graduating cohort, and grade-7 takers can push the ratio above 1 (capped at 1). The high-school alternative (9th–12th grade Algebra I enrollment per 9th grader) exceeds 1.2 in many school-cohorts, likely due to repeaters or reporting differences, and is capped at 1.2.

6. **CRDC year matching.** CRDC 2021-22 is matched to the 2021 and 2022 cohorts and 2023-24 to the 2023 and 2024 cohorts. Course offerings in a graduate's senior year may differ from those in earlier grades. Calculus status changed between the two collections at 65 schools; the access analysis counts calculus as offered if reported in either year.

7. **Suppression and small schools.** CHE suppresses small cells. School-cohorts with fewer than 10 Indiana public enrollees are excluded, and within-school comparisons are possible only where both groups are reported (179 schools). Unweighted estimates are about twice the weighted ones, and the GPA estimate is smaller and not significant among schools with 30 or more in-state enrollees, so the association is concentrated in smaller schools.

8. **Linkage.** Earlier CHE files lack school identifiers; schools are linked by exact name to the 2024 file. Schools that closed, merged, or were renamed before 2024 drop out of the earlier cohorts (listed in `data/processed/qa_report.txt`). Nonpublic schools are excluded because they do not appear in CCD or CRDC.

9. **Self-reported federal data.** CRDC values are reported by schools and districts and are known to contain errors. Negative CRDC reserve codes are treated as missing.

10. **The 2020 cohort is omitted** because its first college year coincided with the onset of the pandemic. The 2021–2023 cohorts also completed high school during pandemic disruption.
