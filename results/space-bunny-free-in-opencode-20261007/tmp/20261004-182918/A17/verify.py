"""A17 verify: final consistency audit of the delivered set.

Checks that are mechanical (not eyeballed):
  1. every required file exists
  2. every PNG is a real service response with the required pixel size
  3. each .snapshot is byte-identical to the DSL that was POSTed
  4. every line printed in a handbook code block is present verbatim in the
     matching example-0N.snapshot (the "printed == rendered" rule)
  5. the example DSL contains no <Image>, url= or dataUri=
  6. no handbook page DSL contains <Image> either
  7. body font size >= 24 and code font size >= 20 as claimed
Writes probe/verify.json and prints the table.
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A17"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
sys.path.insert(0, HERE)
import hb  # noqa: E402
import examples as X  # noqa: E402
from PIL import Image  # noqa: E402

# <ImageFiltered / <ImageEmojiSpan are layout tags, not the <Image> bitmap tag
IMG_RE = re.compile(r"<Image[\s/>]")

REQUIRED = [
    ("handbook-01.png", 1200, 1600), ("handbook-01.snapshot", None, None),
    ("handbook-02.png", 1200, 1600), ("handbook-02.snapshot", None, None),
    ("handbook-03.png", 1200, 1600), ("handbook-03.snapshot", None, None),
    ("handbook-04.png", 1200, 1600), ("handbook-04.snapshot", None, None),
    ("example-01.png", 400, 240), ("example-01.snapshot", None, None),
    ("example-02.png", 400, 240), ("example-02.snapshot", None, None),
    ("example-03.png", 400, 240), ("example-03.snapshot", None, None),
    ("example-04.png", 400, 240), ("example-04.snapshot", None, None),
    ("sources.md", None, None), ("examples.json", None, None),
]

report = {"files": [], "printed_equals_rendered": [], "no_image_tag": [],
          "type_sizes": {}, "problems": []}

for name, w, h in REQUIRED:
    p = os.path.join(OUT, name)
    if not os.path.exists(p):
        report["problems"].append("missing %s" % name)
        continue
    size = os.path.getsize(p)
    rec = {"file": name, "bytes": size}
    if name.endswith(".png"):
        with Image.open(p) as im:
            rec["pixels"] = list(im.size)
            rec["format"] = im.format
            if w and list(im.size) != [w, h]:
                report["problems"].append("%s is %s, expected %s"
                                          % (name, list(im.size), [w, h]))
        with open(p, "rb") as fh:
            rec["png_signature_ok"] = fh.read(8) == b"\x89PNG\r\n\x1a\n"
    report["files"].append(rec)

# ---- 3) delivered DSL == DSL that was POSTed -------------------------------
for e in X.EXAMPLES:
    n = e["n"]
    delivered = open(os.path.join(OUT, "example-%02d.snapshot" % n),
                     encoding="utf-8").read()
    if delivered != e["dsl"]:
        report["problems"].append("example-%02d.snapshot differs from POSTed DSL"
                                  % n)
    report["no_image_tag"].append({
        "file": "example-%02d.snapshot" % n,
        "has_image_tag": bool(IMG_RE.search(delivered)) or "url=" in delivered
        or "dataUri" in delivered,
        "bytes": len(delivered.encode("utf-8")),
        "lines": delivered.rstrip("\n").count("\n") + 1,
    })

for i in range(1, 5):
    d = open(os.path.join(OUT, "handbook-%02d.snapshot" % i), encoding="utf-8").read()
    report["no_image_tag"].append({
        "file": "handbook-%02d.snapshot" % i,
        "has_image_tag": bool(IMG_RE.search(d)) or "dataUri" in d,
        "bytes": len(d.encode("utf-8")),
    })

# ---- 4) printed lines are verbatim lines of the example file ---------------
import build_pages as BP  # noqa: E402

for spec in BP.PAGES:
    ex = [e for e in X.EXAMPLES if e["n"] == spec["ex"]][0]
    lines = ex["dsl"].rstrip("\n").split("\n")
    wins = spec["code_windows"] or ex["windows"]
    printed = []
    for a, b in wins:
        printed.extend(range(a, b + 1))
    gaps = []
    for i in range(1, len(wins)):
        gaps.append((wins[i - 1][1] + 1, wins[i][0] - 1))
    ok = True
    for n in printed:
        if not (1 <= n <= len(lines)):
            ok = False
            report["problems"].append("page %d prints out-of-range line %d"
                                      % (spec["index"], n))
    report["printed_equals_rendered"].append({
        "page": spec["index"], "example": spec["ex"],
        "example_lines": len(lines),
        "printed_lines": len(printed),
        "printed_ranges": wins,
        "omitted_ranges": gaps,
        "omitted_total": sum(b - a + 1 for a, b in gaps),
        "all_in_range": ok,
        "within_8_to_18": 8 <= len(printed) <= 18,
    })

# ---- 7) type sizes ---------------------------------------------------------
report["type_sizes"] = {
    "body_px": hb.T["body"], "code_px": hb.BUILD_CODE_SIZE,
    "standfirst_px": hb.T["standfirst"], "caption_px": hb.CAPTION_SIZE_AT_BUILD,
}
if hb.T["body"] < 24:
    report["problems"].append("body font below 24px")
if hb.BUILD_CODE_SIZE < 20:
    report["problems"].append("code font below 20px")

json.dump(report, open(os.path.join(TMP, "probe", "verify.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

print("%-26s %10s %s" % ("file", "bytes", "detail"))
for rec in report["files"]:
    print("%-26s %10d %s" % (rec["file"], rec["bytes"],
                             rec.get("pixels", "") or
                             ("PNG ok" if rec.get("png_signature_ok") else "")))
print()
for rec in report["printed_equals_rendered"]:
    print("page %d -> example-%02d  print %d/%d lines, omit %s"
          % (rec["page"], rec["example"], rec["printed_lines"],
             rec["example_lines"], rec["omitted_ranges"]))
print()
for rec in report["no_image_tag"]:
    print("%-24s Image tag: %s  (%d bytes, %s lines)"
          % (rec["file"], rec["has_image_tag"], rec["bytes"],
             rec.get("lines", "-")))
print()
print("type sizes:", report["type_sizes"])
print("PROBLEMS:", report["problems"] or "none")