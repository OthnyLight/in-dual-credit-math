#!/usr/bin/env python3
"""05_atlas.py — build the interactive atlas page (map/atlas.html) from map data and paper/stats.json.

Run from repo root:  python code/05_atlas.py [--final]
"""
import argparse
import json
import os

ap = argparse.ArgumentParser()
ap.add_argument("--final", action="store_true")
FINAL = ap.parse_args().final
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, "map")

tpl = open(os.path.join(M, "atlas_template.html"), encoding="utf-8").read()
counties = open(os.path.join(M, "counties.geojson"), encoding="utf-8").read()
schools = open(os.path.join(M, "schools.json"), encoding="utf-8").read()
stats = json.load(open(os.path.join(ROOT, "paper", "stats.json")))
note = ("" if FINAL else
        "DRAFT — not yet verified by the author. Figures may change; do not cite or share.")
html = (tpl.replace("__COUNTIES__", counties).replace("__SCHOOLS__", schools)
        .replace("__STATS__", json.dumps({"access": stats["access"]})).replace("__DRAFT_NOTE__", note))
if FINAL:
    html = html.replace('<div class="draft" id="draft"></div>', "")
open(os.path.join(M, "atlas.html"), "w", encoding="utf-8").write(html)
print("wrote map/atlas.html", len(html), "bytes")
