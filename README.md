# Dual-credit mathematics as a readiness lever (Indiana)

**Status:** v0.1.0, verified by the author 2026-10-21 | **Maintainer:** see `AUTHORS.json` | **License:** code MIT; data, figures, and text CC BY 4.0

Do Indiana high schools where more students earn dual credit send graduates who do better in their first year of college, after accounting for when students reach Algebra I and which math courses the school offers? And where is the mathematics pathway into dual credit missing? This repository answers both questions with public data only. It is meant for state and district policymakers, dual-credit partnership staff, and researchers who want to rerun the analysis for their own schools.

Headline numbers are in `docs/HEADLINES.md`, generated from `paper/stats.json`.

## What is here

```
code/
  01_fetch.py        download every source; log bytes + SHA-256 to data/raw/PROVENANCE.txt
  02_build.py        link CHE outcomes to CCD/CRDC; build the school-cohort panel and access file; write qa_report.txt
  03_analysis.py     models, heterogeneity, sensitivity, access tables; write paper/stats.json and paper/tables/
  04_figures.py      paper figures (review stamp unless --final) and map data
  05_atlas.py        interactive atlas page map/atlas.html
  06_manuscript.js   manuscript paper/manuscript.docx, every number read from stats.json
  07_briefs.py       NACEP proposal, Indiana written statement, docs/HEADLINES.md
  08_preprint_stats.py, 09_pbi_figures.py, 10_preprint.py   preprint (paper/preprint/preprint.pdf); needs revtex4-2
data/raw/            inputs as fetched (not committed; see .gitignore) + PROVENANCE.txt
data/processed/      school_cohort_panel.csv, school_access.csv, school_access_tiers.csv, qa_report.txt
paper/               stats.json, tables/, figures/, manuscript.docx, nacep_proposal.md, indiana_statement.md
map/                 atlas.html (self-contained), counties.geojson, schools.json
docs/                CODEBOOK, LIMITATIONS, VERIFY_CHECKLIST, NEXT_STEPS, HEADLINES, PUBLISH_GUIDE
```

## Run it

Python 3.11+ and Node 18+.

```
pip install -r requirements.txt
npm install docx@9
bash run_all.sh            # or the scripts one at a time, in order
bash run_all.sh --final    # publication build without review stamps
```

The fetch downloads about 1.4 GB (the CRDC 2021-22 archive is 832 MB). Every later step runs offline from `data/raw/`. A stranger running these steps should reproduce `data/processed/` and `paper/stats.json` exactly.

## Sources

| Source | Vintage | Terms | Accessed |
|---|---|---|---|
| Indiana Commission for Higher Education, College-Going / College Readiness datasets, https://www.in.gov/che/college-going-reports/ | cohorts 2019, 2021–2024 (2024 file prepared May 12, 2026) | Indiana state public record | 2026-10-17 |
| U.S. Dept. of Education, Civil Rights Data Collection, https://civilrightsdata.ed.gov/data | 2021-22; 2023-24 (files dated 2026-08-06) | U.S. federal public domain | 2026-10-17 |
| NCES Common Core of Data: school directory (029) and membership (052), https://nces.ed.gov/ccd/files.asp | 2023-24 v1a; 2021-22 membership | U.S. federal public domain | 2026-10-17 |
| NCES EDGE public school geocodes | 2023-24 | U.S. federal public domain | 2026-10-17 |
| U.S. Census Bureau cartographic boundary files, counties 1:500k | 2023 | U.S. federal public domain | 2026-10-17 |

Exact URLs, sizes, and hashes are in `data/raw/PROVENANCE.txt`.

## Limitations

Read `docs/LIMITATIONS.md` before using or citing anything here. In short, the results are school-level associations, not effects on individual students, and neither the state nor federal data identify the subject of dual-credit courses.

## Citation

See `CITATION.cff`. Repository: https://github.com/OthnyLight/in-dual-credit-math. DOI: added after the first Zenodo deposit.
