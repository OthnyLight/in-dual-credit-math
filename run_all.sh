#!/usr/bin/env bash
# Run the full pipeline in order. Pass --final only after the author's verification.
set -euo pipefail
cd "$(dirname "$0")"
FINAL="${1:-}"
python code/01_fetch.py
python code/02_build.py
python code/03_analysis.py
python code/04_figures.py $FINAL
python code/05_atlas.py $FINAL
node code/06_manuscript.js $FINAL
if [ "$FINAL" = "--final" ] && unzip -p paper/manuscript.docx word/document.xml | grep -q 'VERIFY'; then
  echo "manuscript.docx still contains [VERIFY] text; resolve it in code/06_manuscript.js" >&2; exit 1
fi
python code/07_briefs.py $FINAL
python code/08_preprint_stats.py
python code/09_pbi_figures.py
python code/10_preprint.py
echo "done; QA in data/processed/qa_report.txt, numbers in paper/stats.json"
