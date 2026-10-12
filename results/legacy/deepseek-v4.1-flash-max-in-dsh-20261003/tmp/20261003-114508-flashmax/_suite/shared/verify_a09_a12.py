"""Final verification for A09-A12: deliverables, PNG headers, DSL pairing, BOM check."""
from __future__ import annotations

import json
import os

from PIL import Image

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
OUT = os.path.join(ROOT, "outputs", "20261003-114508-flashmax")

EXPECT = {
    "A09": {"png": {"transform-atlas.png": (1600, 1200)},
            "extra": ["geometry-audit.json", "snapshot-usage.md", "task-metrics.json"]},
    "A10": {"png": {"compositing-lab.png": (1440, 1100)},
            "extra": ["composite-audit.json", "snapshot-usage.md", "task-metrics.json"]},
    "A11": {"png": {"invoice-page-01.png": (1200, 1600), "invoice-page-02.png": (1200, 1600)},
            "extra": ["invoice-audit.json", "text-map.json", "snapshot-usage.md",
                      "task-metrics.json"]},
    "A12": {"png": {"mobile.png": (360, 800), "tablet.png": (768, 1024),
                    "desktop.png": (1440, 900), "stage.png": (1920, 1080)},
            "extra": ["design-tokens.json", "content-map.json", "snapshot-usage.md",
                      "task-metrics.json"]},
}

ok = True
for task, spec in EXPECT.items():
    d = os.path.join(OUT, task)
    print(f"== {task} {d}")
    for png, (w, h) in spec["png"].items():
        p = os.path.join(d, png)
        dsl = os.path.join(d, png.replace(".png", ".snapshot"))
        head = open(p, "rb").read(8)
        im = Image.open(p)
        dsl_bytes = open(dsl, "rb").read()
        good = (head == b"\x89PNG\r\n\x1a\n" and im.size == (w, h)
                and dsl_bytes[:3] != b"\xef\xbb\xbf" and b"<Snapshot" in dsl_bytes)
        ok &= good
        print(f"   {png:24s} {im.size} {im.format} png_magic={head[:4] == b'\\x89PNG'[:4]} "
              f"dsl={os.path.getsize(dsl)}B bom_free={dsl_bytes[:3] != b'\\xef\\xbb\\xbf'} "
              f"{'OK' if good else 'FAIL'}")
    for extra in spec["extra"]:
        p = os.path.join(d, extra)
        exists = os.path.exists(p)
        ok &= exists
        size = os.path.getsize(p) if exists else 0
        print(f"   {extra:24s} {size:>8d}B {'OK' if exists else 'MISSING'}")
    m = json.load(open(os.path.join(d, "task-metrics.json"), encoding="utf-8"))
    print(f"   metrics: status={m['status']} pngs={m['final_pngs']} "
          f"req={m['requests']['render_success']}/{m['requests']['render_requests']} "
          f"fail={m['requests']['render_failed']} versions={m['dsl_versions']} "
          f"wall={m['wall_clock_seconds']}s tz={m['timezone']}")

print("\nALL OK" if ok else "\nSOME CHECKS FAILED")
