# Publish guide — P5 Dual-credit mathematics as a readiness lever

Nothing has been pushed or submitted. Every step below happens **after** `docs/VERIFY_CHECKLIST.md` is complete and `python code/publish_gate.py .` passes. Each step is written so you can finish it in one sitting.

## 0. Finalize (about 10 minutes)
1. Fill every `[VERIFY ...]` field in `AUTHORS.json` and `CITATION.cff` (name, ORCID, affiliation).
2. Rewrite the `[VERIFY: author ...]` paragraphs in `code/06_manuscript.js` and the fields in `code/07_briefs.py` in your own words. They live in the scripts so a rerun never loses them.
3. `bash run_all.sh --final` regenerates every figure, the atlas, the manuscript, and the briefs without DRAFT stamps.
4. `python code/publish_gate.py . --allow-draft-in code/ docs/VERIFY_CHECKLIST.md docs/PUBLISH_GUIDE.md map/atlas_template.html paper/nacep_proposal.md paper/indiana_statement.md` (the last two are submission kits whose remaining tags are filled at submission time) must report clear. (The scripts and these two guides mention the stamps by name; `run_all.sh --final` separately refuses to finish if the manuscript still contains any `[VERIFY]` text.)

## 1. GitHub (no token was supplied)
1. Create an empty repository at github.com/new, for example `in-dual-credit-math`, with no README.
2. In the project folder:
   ```
   git init -b main
   git add -A
   git commit -m "v0.1.0: Indiana dual-credit readiness analysis and access atlas"
   git remote add origin https://github.com/USER/in-dual-credit-math.git
   git push -u origin main
   ```
   Raw downloads are excluded by `.gitignore`; `data/raw/PROVENANCE.txt` lets anyone re-fetch them.
3. Releases → Draft a new release → tag `v0.1.0`. Release notes: "First public release: school-level analysis of dual credit and first-year college outcomes for Indiana public high schools (2021–2024 cohorts) and an atlas of schools lacking calculus or dual enrollment. Public data only."
4. Optional: Settings → Pages → deploy from `main` `/map` so `atlas.html` has a public URL. (Alternatively share the private Claude artifact link after verification.)

Alternative with a token: `GITHUB_TOKEN=... python code/publish_github.py .` (scope: `repo`; revoke after use).

## 2. Zenodo DOI
1. Log in at zenodo.org with ORCID.
2. Account → GitHub → switch on `in-dual-credit-math`, then publish the GitHub release (step 1.3). Zenodo mints a DOI within minutes.
3. Copy the DOI into `CITATION.cff`, the README status line, the manuscript Data Availability statement (`code/06_manuscript.js`), and `evidence_log.csv`. Rerun `bash run_all.sh --final` and push a v0.1.1 commit.

Alternative with a token: `ZENODO_SANDBOX_TOKEN=... python code/zenodo_deposit.py . --sandbox` first, then `ZENODO_TOKEN=...` without `--sandbox` (scopes `deposit:write`, `deposit:actions`).

## 3. Preprint (optional, before journal submission)
Education research preprints go to **EdArXiv** (osf.io/preprints/edarxiv), not arXiv or medRxiv.
1. Convert `paper/manuscript.docx` to PDF.
2. Submit: title and authors as in `AUTHORS.json`; abstract from the manuscript; subjects Education → Higher Education, Education Policy; license CC BY 4.0; link the GitHub repository and Zenodo DOI.
3. Check the target journal's preprint policy first. [VERIFY target journal]

## 4. Journal (article in preparation)
Candidate fee-free, indexed outlets include _Education Policy Analysis Archives_, _AERA Open_ (check APC), _Educational Evaluation and Policy Analysis_, and _Community College Review_. [VERIFY policy and fees for the chosen outlet; reformat to its style.] Submit personally through the journal's system; include the AI-use disclosure and the competing-interest statement about ACP teaching.

## 5. NACEP 2027 national conference
`paper/nacep_proposal.md` is the kit. When the 2027 call opens (watch nacep.org; the 2026 call closed April 10, 2026):
1. Open the online form ("Submit Proposal"); proposals in other formats are not accepted.
2. Paste the title, description, and learning outcomes; trim to the stated limits.
3. Choose track, audience, and program mode; answer the prerecording question.
4. Log the submission confirmation in `evidence_log.csv`.

## 6. Indiana written statement
`paper/indiana_statement.md` is addressed to the Commission for Higher Education in connection with its September 10, 2026 Request for Information on Indiana College Core and dual-credit access, and to the Department of Education's legislatively directed review.
1. Find the RFI document on che.in.gov (or ask the Commission's office), and confirm its deadline and whether it takes research input from individuals. If not, send the statement as a letter to the Commission and to the Secretary of Education's office.
2. Convert to PDF on plain letterhead, sign, and attach the map figure (`paper/figures/fig5_access_map.png`).
3. Submit by the route the RFI specifies. Save the confirmation email and log it in `evidence_log.csv` the same day.
4. If an interim study committee takes testimony on dual credit, submit the same statement to that committee through iga.in.gov.

## After every submission
Add a row to `evidence_log.csv`: date, artifact, venue, link or DOI, status, a saved confirmation (PDF or screenshot).
