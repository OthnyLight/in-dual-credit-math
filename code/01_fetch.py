#!/usr/bin/env python3
"""01_fetch.py — download every raw input and log provenance.

Run from the repository root:  python code/01_fetch.py [--force]

Each file is fetched once (skipped if present unless --force) and a record
(date, file, bytes, SHA-256, URL, note) is appended to data/raw/PROVENANCE.txt.

URL notes
- CHE: files are linked from https://www.in.gov/che/college-going-reports/ .
  The page links them under secure.in.gov, which returns 404 for downloads;
  the same /dA/ paths resolve on www.in.gov. If a link breaks, re-scrape that
  page for hrefs ending in .xlsx.
- CRDC: the data page (https://civilrightsdata.ed.gov/data) is a JavaScript
  app; its "Download" buttons resolve to
  https://civilrightsdata.ed.gov/assets/ocr/docs/<YYYY-YY>-crdc-data.zip
- CCD / EDGE: standard NCES file-server paths.
"""
import argparse
import hashlib
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
LOG = os.path.join(RAW, "PROVENANCE.txt")
CHE = "https://www.in.gov/dA/{}?language_id=1"

SOURCES = [
    # (subdir, filename, url, note)
    ("che", "che_cohort2024.xlsx", CHE.format("d1c423c709/2026-College-Going-Dataset-2024-Cohort.xlsx"),
     "CHE 2026 College-Going Dataset, 2024 HS graduating cohort (prepared May 12, 2026)"),
    ("che", "che_cohort2023.xlsx", CHE.format("2f8404d686/2025-College-Readiness-Dataset-2023-Cohort_update.xlsx"),
     "CHE 2025 College Readiness Dataset, 2023 cohort (update)"),
    ("che", "che_cohort2022.xlsx", CHE.format("667abc107d/2024-College-Readiness-Dataset-2022-Cohort.xlsx"),
     "CHE 2024 College Readiness Dataset, 2022 cohort"),
    ("che", "che_cohort2021.xlsx", CHE.format("412db3af32/2023-College-Readiness-Dataset-2021-Cohort.xlsx"),
     "CHE 2023 College Readiness Dataset, 2021 cohort"),
    ("che", "che_cohort2019.xlsx", CHE.format("cb87996212/2021-College-Readiness-Dataset-2019-Cohort.xlsx"),
     "CHE 2021 College Readiness Dataset, 2019 cohort (pre-COVID sensitivity)"),
    ("che", "che_dualcredit_supplement.pdf",
     CHE.format("414d4c01ac/College_Readiness_Report_Supplement_A_Closer_Look_at_Dual_Credit_Students.pdf"),
     "CHE supplement on dual credit students (context)"),
    ("che", "che_user_guide.pdf", CHE.format("4ee48e7626/College_Readiness_Report_User_Guide_generic.pdf"),
     "CHE College Readiness report user guide (definitions)"),
    ("crdc", "crdc_2023-24.zip", "https://civilrightsdata.ed.gov/assets/ocr/docs/2023-24-crdc-data.zip",
     "CRDC 2023-24 public-use data (files dated 2026-08-06)"),
    ("crdc", "crdc_2021-22.zip", "https://civilrightsdata.ed.gov/assets/ocr/docs/2021-22-crdc-data.zip",
     "CRDC 2021-22 public-use data"),
    ("ccd", "ccd_sch_029_2324.zip", "https://nces.ed.gov/ccd/Data/zip/ccd_sch_029_2324_w_1a_073124.zip",
     "NCES CCD 2023-24 school directory, v1a"),
    ("ccd", "ccd_sch_052_2324.zip", "https://nces.ed.gov/ccd/Data/zip/ccd_sch_052_2324_l_1a_073124.zip",
     "NCES CCD 2023-24 membership by grade (long format) — grade 8/9 denominators for Algebra I timing"),
    ("ccd", "ccd_sch_052_2122.zip", "https://nces.ed.gov/ccd/Data/zip/ccd_sch_052_2122_l_1a_071722.zip",
     "NCES CCD 2021-22 membership by grade — denominators matched to CRDC 2021-22"),
    ("ccd", "edge_geocode_2324.zip", "https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_2324.zip",
     "NCES EDGE 2023-24 public school geocodes (lat/lon, NCES locale)"),
    ("geo", "cb_2023_us_county_500k.zip", "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip",
     "Census 2023 cartographic boundary counties, 1:500k (map base layer)"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def logged():
    if not os.path.exists(LOG):
        return set()
    with open(LOG, encoding="utf-8") as f:
        return {line.split(" | ")[1] for line in f if " | " in line}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    done = logged()
    for sub, fn, url, note in SOURCES:
        d = os.path.join(RAW, sub)
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, fn)
        if a.force or not os.path.exists(path):
            print("fetch", fn)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research replication)"})
            with urllib.request.urlopen(req, timeout=1800) as r, open(path, "wb") as out:
                while chunk := r.read(1 << 20):
                    out.write(chunk)
        with open(path, "rb") as f:
            head = f.read(4)
        if head[:2] not in (b"PK", b"%P"):
            sys.exit(f"{fn}: not a zip/xlsx/pdf — the URL may have moved ({url})")
        if a.force or fn not in done:
            subprocess.run([sys.executable, os.path.join(ROOT, "code", "provenance.py"),
                            path, url, "--log", LOG, "--note", note], check=True)
    print("all sources present; provenance in data/raw/PROVENANCE.txt")


if __name__ == "__main__":
    main()
