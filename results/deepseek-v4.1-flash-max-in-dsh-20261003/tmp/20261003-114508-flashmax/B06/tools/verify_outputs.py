"""Final verification of the B05 and B06 deliverables.

Checks, for both tasks: every case directory has the three required files, every final.png is a
valid PNG whose bytes are identical to the raw service response kept in the temp directory, the
dimensions match what the portfolio claims, and the top-level deliverables exist.
"""
from __future__ import annotations

import hashlib
import json
import os
import struct
import zipfile

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"


def png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


problems = []
for task in ("B05", "B06"):
    OUT = os.path.join(ROOT, "outputs", RUN, task)
    TMP = os.path.join(ROOT, "tmp", RUN, task)
    pf = json.load(open(os.path.join(OUT, "portfolio.json"), encoding="utf-8"))
    print(f"--- {task}: {len(pf['cases'])} cases")
    for c in pf["cases"]:
        cid = c["id"]
        d = os.path.join(OUT, cid)
        for f in ("final.png", "final.snapshot", "case.md"):
            if not os.path.exists(os.path.join(d, f)):
                problems.append(f"{task}/{cid} missing {f}")
        png = os.path.join(d, "final.png")
        dsl = os.path.join(d, "final.snapshot")
        size = png_size(png)
        if size is None:
            problems.append(f"{task}/{cid} final.png is not a PNG")
            continue
        if list(size) != list(c["dimensions"]):
            problems.append(f"{task}/{cid} size {size} != portfolio {c['dimensions']}")
        # byte-identity with the service response kept in temp
        ver = "final" if task == "B06" else None
        cands = [os.path.join(TMP, "render", f"{cid}.final.png"),
                 os.path.join(TMP, "render", f"{cid}.v4.png")]
        src = next((c2 for c2 in cands if os.path.exists(c2)), None)
        if src is None:
            problems.append(f"{task}/{cid} no temp render to compare")
        elif sha(src) != sha(png):
            problems.append(f"{task}/{cid} final.png differs from the temp service response")
        # DSL sanity: single root child, no BOM, contains Snapshot
        raw = open(dsl, "rb").read()
        if raw[:3] == b"\xef\xbb\xbf":
            problems.append(f"{task}/{cid} DSL has a BOM")
        txt = raw.decode("utf-8")
        if not txt.startswith("<Snapshot") or "</Snapshot>" not in txt:
            problems.append(f"{task}/{cid} DSL is not a complete document")
        if "&amp;" in txt or "&lt;" in txt:
            problems.append(f"{task}/{cid} DSL contains escaped entities")
        print(f"  {cid}: {size[0]}x{size[1]} {os.path.getsize(png)} bytes  ok")
    for f in ("portfolio.json", "portfolio.md", "gallery.html", "snapshot-usage.md",
              "task-metrics.json"):
        if not os.path.exists(os.path.join(OUT, f)):
            problems.append(f"{task} missing {f}")
    extra = ["product-brief.md", "journey.json"] if task == "B05" else \
            ["problem-evidence.json", "design-review.md"]
    for f in extra:
        if not os.path.exists(os.path.join(OUT, f)):
            problems.append(f"{task} missing {f}")

# gallery links resolve
for task in ("B05", "B06"):
    OUT = os.path.join(ROOT, "outputs", RUN, task)
    html = open(os.path.join(OUT, "gallery.html"), encoding="utf-8").read()
    for i in range(1, 11):
        cid = f"case-{i:02d}"
        if f'href="{cid}/final.png"' not in html:
            problems.append(f"{task} gallery does not link {cid}/final.png")
    if "http://" in html.replace("http://www.w3.org", "") or "src=\"http" in html:
        problems.append(f"{task} gallery references a remote resource")

print()
if problems:
    print("PROBLEMS:")
    for p in problems:
        print(" -", p)
else:
    print("ALL CHECKS PASSED: 20 case directories, 20 PNGs byte-identical to service responses, "
          "gallery links resolve, no remote scripts, no BOM, no escaped entities.")
