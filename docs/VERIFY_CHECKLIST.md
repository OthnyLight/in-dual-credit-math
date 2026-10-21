# Verification checklist (author completes before any release)

Initial and date each line in your own copy. `code/publish_gate.py` checks the mechanical items; these are yours.

## Reproduce
- [ ] Fresh fetch via `code/01_fetch.py --force`; file sizes and hashes match `data/raw/PROVENANCE.txt`, or the drift is explained (CHE files are replaced when updated)
- [ ] `bash run_all.sh` completes; `paper/stats.json` and `data/processed/*.csv` match the committed versions
- [ ] Every number in the manuscript, proposal, statement, and `docs/HEADLINES.md` traced to `stats.json` after the re-run

## Source-level checks
- [ ] Spot checks in `data/processed/qa_report.txt` section [7] confirmed by hand against the CHE 2024 workbook (filter `Location`) and the CRDC school pages: Brownsburg HS, Arsenal Technical HS, Knox Community HS, Bloomington HS South, 21st Century Charter School of Gary
- [ ] Extremes checked: Seeger Memorial Jr-Sr HS (dual-credit share 100%), Shortridge HS (1%), BELIEVE Circle City HS (0%)
- [ ] Five random schools from `school_access_tiers.csv` (record the seed) checked against CRDC calculus and dual-enrollment status
- [ ] Each of the 3 counties shown with no calculus (`paper/tables/table7_access_by_county.csv`) checked: are there public high schools there that offer calculus but were missed or misclassified?
- [ ] Source vintages confirmed current; CHE and CRDC terms re-read

## Judgment calls to own (edit the code or record your agreement)
- [x] **Credits/GPA definition.** Author confirmed (2026-10-21) that first-year GPA and credits include dual-credit grades and hours from high school. Results, discussion, limitations, statement, and proposal rewritten to treat GPA/credit estimates as upper bounds.
- [ ] **Algebra I timing.** Corporation-level 7th–8th grade Algebra I per 8th grader is the main measure; the high-school measure is a sensitivity check. Agree, or swap.
- [ ] **"Out of reach" definition.** No calculus in either CRDC year, no dual enrollment, or thin pathway (no calculus and under one-third uptake). Is one-third the right threshold?
- [ ] **Minimum sample.** School-cohorts with fewer than 10 Indiana public enrollees are dropped.
- [ ] **Interpretation.** The estimate is concentrated in smaller schools (unweighted larger; not significant in schools with 30+ enrollees). The manuscript says so in 6.5; confirm the abstract and statement do not overstate it.
- [x] **Citations.** Author confirmed all seven sources exist (2026-10-21); converted to APA with a References list; CHE supplement year corrected to 2016 from the PDF cover.

## Your own words
- [ ] The two M118 paragraphs (Section 1 and Section 7), drafted from your notes on 2026-10-21, read and revised in your own voice
- [ ] NACEP presenter bio, session minutes 30–38, prior-presentation disclosure
- [ ] Indiana statement: recipient, submission route, and the RFI deadline confirmed; individual-capacity and IU-disclaimer sentence in your words
- [ ] Competing interests (ACP teaching) and funding statements
- [x] AI-use disclosure is accurate (author confirmed 2026-10-21); recheck against the chosen journal's policy at submission
- [x] Verification phrase restored to the AI-use statement at the author's request (2026-10-21)

## Before it goes public
- [ ] `AUTHORS.json` complete (name, ORCID, affiliation); `CITATION.cff` updated from it
- [ ] `bash run_all.sh --final`; `python code/publish_gate.py .` passes
- [ ] Evidence log row written the day of release
