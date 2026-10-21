# Next steps (v0.2 and beyond)

0. **Outcomes without pre-matriculation credit.** Ask CHE for school-level first-year GPA and credits that exclude dual-credit grades and hours earned in high school, and rerun `03_analysis.py`. This is the single most important improvement, because current measures include the exposure.
1. **Subject-specific dual credit.** Request from CHE (or IDOE) graduate-level dual-credit records by course subject, at least aggregated by school, so the exposure can be dual-credit mathematics rather than any dual credit. Partner lists from IU ACP and Ivy Tech for MATH courses (M118, college algebra) would make the access map math-specific.
2. **Gateway-math outcomes.** Ask CHE for completion of a college-level mathematics course in the first year by high school and dual-credit status; this is the readiness outcome closest to the question.
3. **Persistence.** Add second-year persistence where CHE reports it (earlier College Readiness files did).
4. **Cohort-matched Algebra I timing.** Link each graduating cohort to its 8th-grade CRDC year when the 2025-26 collection is released, and use feeder-school assignments where IDOE can supply them.
5. **Indiana College Core.** Add the CHE list of Core-participating high schools (328 schools for 2026-27) as an access layer on the atlas.
6. **Annual refresh.** CHE releases a new cohort each spring. Rerun `run_all.sh` with the new file added to `01_fetch.py` and release a versioned update.
7. **Other states.** The CRDC access analysis runs for any state as written; the readiness half needs a state with school-level outcome reports similar to CHE's.
