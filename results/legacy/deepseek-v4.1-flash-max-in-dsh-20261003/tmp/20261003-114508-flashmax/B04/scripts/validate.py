"""validate.py - final pre-handoff check for a task's output directory."""
from __future__ import annotations

import json
import os
import re
import sys

from PIL import Image

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TASK = sys.argv[1] if len(sys.argv) > 1 else "B04"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)

pf = json.load(open(os.path.join(OUT, "portfolio.json"), encoding="utf-8"))
problems = []
checked = 0
for c in pf["cases"]:
    cid = c["id"]
    dpng = os.path.join(OUT, c["png"].replace("/", os.sep))
    ddsl = os.path.join(OUT, c["snapshot"].replace("/", os.sep))
    dmd = os.path.join(OUT, c["case_md"].replace("/", os.sep))
    for p in (dpng, ddsl, dmd):
        if not os.path.exists(p):
            problems.append(f"{cid}: missing {p}")
    if not os.path.exists(dpng):
        continue
    with open(dpng, "rb") as fh:
        if fh.read(8) != b"\x89PNG\r\n\x1a\n":
            problems.append(f"{cid}: final.png is not a PNG")
    with Image.open(dpng) as im:
        if [im.width, im.height] != c["dimensions"]:
            problems.append(f"{cid}: dims {im.width}x{im.height} != metadata {c['dimensions']}")
    raw = open(ddsl, "rb").read()
    if raw[:3] == b"\xef\xbb\xbf":
        problems.append(f"{cid}: final.snapshot has a BOM")
    txt = raw.decode("utf-8")
    if not txt.startswith("<Snapshot"):
        problems.append(f"{cid}: snapshot does not start with <Snapshot")
    if "</Snapshot>" not in txt:
        problems.append(f"{cid}: snapshot not closed")
    if "<Image" in txt:
        problems.append(f"{cid}: snapshot embeds an <Image> element")
    n = len(re.findall(r"<[A-Za-z]", txt))
    if n > 4096:
        problems.append(f"{cid}: {n} elements over the 4096 cap")
    checked += 1

# gallery links
gh = open(os.path.join(OUT, "gallery.html"), encoding="utf-8").read()
for m in re.finditer(r'(?:href|src)="([^"]+)"', gh):
    t = m.group(1)
    if t.startswith(("http", "#", "mailto")):
        problems.append(f"gallery.html: remote link {t}")
        continue
    if not os.path.exists(os.path.join(OUT, t.replace("/", os.sep))):
        problems.append(f"gallery.html: broken relative link {t}")
if "<script" in gh.lower():
    problems.append("gallery.html contains a script tag")

print(f"{TASK}: cases={checked} problems={len(problems)}")
for p in problems:
    print("  !", p)
print("element counts:", end=" ")
for c in pf["cases"]:
    d = os.path.join(OUT, c["snapshot"].replace("/", os.sep))
    if os.path.exists(d):
        print(f"{c['id'][-2:]}:{len(re.findall(r'<[A-Za-z]', open(d, encoding='utf-8').read()))}",
              end=" ")
print()
sys.exit(1 if problems else 0)
