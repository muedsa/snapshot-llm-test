# -*- coding: utf-8 -*-
"""Probe: measure real glyph advances of the service fonts at 20px.

Renders one strip of known strings, then measures ink extents with Pillow.
Writes tmp/<run>/_suite/shared/text-metrics.json.
"""
import json
import os
import sys
from pathlib import Path

from PIL import Image

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402

PROBE = SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "probes"
PROBE.mkdir(parents=True, exist_ok=True)

SAMPLES = [
    ("cjk", "退款率是本期利润的最强解释项"),
    ("digits", "0123456789"),
    ("upper", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    ("lower", "abcdefghijklmnopqrstuvwxyz"),
    ("mixed_cn", "净收入 91.86 万元"),
    ("date", "2026-04"),
    ("pct", "5.00%"),
    ("sentence", "管理结论：两月回到 5.00% 可多留 9,782 元。"),
]
SIZE = 20
LINE_H = 44
TOP = 20

parts = []
for i, (key, s) in enumerate(SAMPLES):
    y = TOP + i * LINE_H
    parts.append(f'<Positioned left="20" top="{y}"><Text fontSize="{SIZE}" color="#FFFFFF" '
                 f'fontFamily="Inter,Noto Sans CJK SC">{s}</Text></Positioned>')

dsl = ('<Snapshot background="#000000" type="png"><Container width="1400" '
       f'height="{TOP * 2 + len(SAMPLES) * LINE_H}"><Stack alignment="TOP_LEFT">'
       + "".join(parts) + "</Stack></Container></Snapshot>")

path = PROBE / "text-metrics.snapshot"
path.write_text(dsl, encoding="utf-8")
log = api.TaskLogger("_suite", PROBE)
rec = log.render(path, PROBE / "text-metrics.png", "text metrics calibration @20px")
print("render", rec["http_status"], rec["response_bytes"])
if rec["http_status"] != 200:
    print((PROBE / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1200])
    raise SystemExit(1)

img = Image.open(PROBE / "text-metrics.png").convert("RGB")
px = img.load()
result = {"calibrated_at": api.iso_now(), "font_size": SIZE, "samples": []}
for i, (key, s) in enumerate(SAMPLES):
    y0 = TOP + i * LINE_H - 4
    y1 = y0 + LINE_H
    xs = []
    ys = []
    for y in range(max(0, y0), min(img.height, y1)):
        for x in range(img.width):
            r, g, b = px[x, y]
            if r + g + b > 30:
                xs.append(x)
                ys.append(y)
    if not xs:
        continue
    w = max(xs) - min(xs) + 1
    h = max(ys) - min(ys) + 1
    result["samples"].append({
        "key": key, "text": s, "chars": len(s), "ink_width": w, "ink_height": h,
        "ink_left": min(xs), "ink_top": min(ys),
        "width_per_char": round(w / len(s), 3),
    })
    print(f"{key:9s} chars={len(s):2d} w={w:4d} h={h:2d} per_char={w/len(s):6.2f}")

out = SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "shared" / "text-metrics.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote", out.relative_to(SUITE_ROOT).as_posix())
