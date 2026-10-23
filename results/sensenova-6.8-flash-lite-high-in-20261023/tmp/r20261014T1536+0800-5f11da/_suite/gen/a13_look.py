"""A13 看图辅助：把预览合成到浅底、做 32×32 缩略与复核表。

透明 PNG 在查看器里按黑底渲染，半透明描边几乎看不见；方向选择与 32×32
复核都必须在真实浅底上做。本脚本只写临时目录，不改动任何交付件。

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a13_look.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402
import a13_pixels as P  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A13"
_, TMP = S.task_dirs(TASK)
PRE = TMP / "preview"

SRC = ["preview-a", "preview-b"]

# 方向选择要看的东西：512 原图在浅底上、32×32 在浅底上、以及放大看边缘
out: list[Path] = []
for tag in SRC:
    src = PRE / (tag + ".png")
    if not src.exists():
        print("缺", src)
        continue
    im, dec = P.open_rgba(src)
    # 原尺寸合成到浅底
    p1 = PRE / (tag + "-onlight.png")
    P.composite(im, P.LIGHT_BG, 1).save(p1, format="PNG")
    out.append(p1)
    # 32×32：预乘 alpha + Lanczos
    th, tmeta = P.thumb32(im, 32)
    p2 = PRE / (tag + "-32.png")
    p3 = PRE / (tag + "-32-onlight.png")
    th.save(p2, format="PNG")
    P.composite(th, P.LIGHT_BG, 1).save(p3, format="PNG")
    out.extend([p2, p3])

    d = P.arr(im)
    a = d[:, :, 3]
    # 512 上沿几何中心横切：层与层之间必须真的是空白
    runs_x = P.line_runs(im, "x", im.height // 2)
    runs_y = P.line_runs(im, "y", im.width // 2)
    d32 = P.arr(th)
    t32 = {
        "line_x_at_16": P.line_runs(th, "x", 16),
        "line_y_at_16": P.line_runs(th, "y", 16),
        "x_run_widths": [r[1] - r[0] + 1
                         for r in P.line_runs(th, "x", 16)],
        "y_run_widths": [r[1] - r[0] + 1
                         for r in P.line_runs(th, "y", 16)],
        "x_gaps": [P.line_runs(th, "x", 16)[i + 1][0]
                   - P.line_runs(th, "x", 16)[i][1] - 1
                   for i in range(len(P.line_runs(th, "x", 16)) - 1)],
        "y_gaps": [P.line_runs(th, "y", 16)[i + 1][0]
                   - P.line_runs(th, "y", 16)[i][1] - 1
                   for i in range(len(P.line_runs(th, "y", 16)) - 1)],
        "coverage_pct": round(float((d32[:, :, 3] > 0).sum()) / 1024 * 100, 2),
    }
    print(f"\n{tag}")
    print("  解码", json.dumps(dec, ensure_ascii=False))
    print("  512 alpha", json.dumps(P.alpha_report(im), ensure_ascii=False))
    print("  512 bbox", P.alpha_bbox(im))
    print("  512 中心横切", runs_x)
    print("  512 中心纵切", runs_y)
    print("  32  ", json.dumps(t32, ensure_ascii=False))
    print("  32  bbox", P.alpha_bbox(th))
    print("  32  逐行覆盖", [int(v) for v in (d32[:, :, 3] > 0).sum(axis=1)])

# 复核表：32 px 原尺寸 + 4× 放大并排，便于一次看完两个方向
cells = []
for tag in SRC:
    p = PRE / (tag + "-32.png")
    if p.exists():
        cells.append((tag, P.Image.open(p).convert("RGBA")))
if cells:
    sheet = P.sheet(cells, cell=32, magnify=4, pad=20, cols=1)
    sp = PRE / "a13-direction-32-sheet.png"
    sheet.save(sp, format="PNG")
    out.append(sp)

for p in out:
    print("查看", S.rel(p), p.stat().st_size, "B")
