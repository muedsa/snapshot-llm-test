"""Final check for A13-A16: files, pairing, PNG magic, sizes, and the required JSON keys."""
from __future__ import annotations

import json
import os
import sys

from PIL import Image

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"

REQUIRED = {
    "A13": {
        "png": {"symbol-color.png": (512, 512), "symbol-black.png": (512, 512),
                "brand-banner.png": (1200, 400), "launch-poster.png": (1080, 1350)},
        "extra": ["brand-system.json", "rationale.md", "snapshot-usage.md", "task-metrics.json"],
    },
    "A14": {
        "png": {f"card-K0{i}.png": (1200, 630) for i in range(1, 9)},
        "extra": ["batch-audit.json", "snapshot-usage.md", "task-metrics.json"],
    },
    "A15": {
        "png": {"reconstructed.png": (1440, 900)},
        "extra": ["reconstruction-audit.json", "comparison.md",
                  "snapshot-usage.md", "task-metrics.json"],
    },
    "A16": {
        "png": {"corrected-report.png": (1280, 900)},
        "extra": ["findings.json", "corrected-data.json",
                  "snapshot-usage.md", "task-metrics.json"],
    },
}

ok = True
for task, spec in REQUIRED.items():
    out = os.path.join(ROOT, "outputs", RUN, task)
    tmp = os.path.join(ROOT, "tmp", RUN, task)
    print(f"=== {task}  out={os.path.relpath(out, ROOT)}")
    for name, (ew, eh) in spec["png"].items():
        p = os.path.join(out, name)
        dsl = p[:-4] + ".snapshot"
        if not os.path.exists(p):
            print(f"  MISSING {name}"); ok = False; continue
        with open(p, "rb") as fh:
            magic = fh.read(8)
        im = Image.open(p)
        size_ok = tuple(im.size) == (ew, eh)
        dsl_ok = os.path.exists(dsl) and os.path.getsize(dsl) > 0
        is_png = magic == b"\x89PNG\r\n\x1a\n"
        flag = "OK " if (size_ok and dsl_ok and is_png) else "BAD"
        if flag == "BAD":
            ok = False
        print(f"  {flag} {name:24s} {im.size} expect=({ew},{eh}) "
              f"png={is_png} snapshot={dsl_ok} bytes={os.path.getsize(p)}")
    for name in spec["extra"]:
        p = os.path.join(out, name)
        good = os.path.exists(p) and os.path.getsize(p) > 0
        if not good:
            ok = False
        print(f"  {'OK ' if good else 'BAD'} {name}")
    m = json.load(open(os.path.join(out, "task-metrics.json"), encoding="utf-8"))
    print(f"      metrics: status={m['status']} renders={m['requests']['render_requests']}"
          f" ok={m['requests']['render_success']} fail={m['requests']['render_failed']}"
          f" dsl={m['dsl_versions']} pngs={m['final_pngs']}"
          f" views={m['iterations']['image_reviews']}"
          f" wall={m['wall_clock_seconds']}s")
    for kind, fn in (("requests", "requests.jsonl"), ("iterations", "iterations.jsonl"),
                     ("views", "image-views.jsonl")):
        p = os.path.join(tmp, fn)
        n = sum(1 for _ in open(p, encoding="utf-8-sig")) if os.path.exists(p) else 0
        print(f"      tmp {fn}: {n} records")

print("\nALL OK" if ok else "\nPROBLEMS FOUND")
