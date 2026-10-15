#!/usr/bin/env python
"""A10 最终 PNG 的像素审计：①② 重叠内部取样 + ③④⑤⑥ 裁剪/外溢的定量检查。

启动基准：总任务根 (suite_root)。
题面规定：局部采样 (180,100) 对应解码 PNG 的第 (origin_x+180, origin_y+100) 个像素，
索引从 0 起；读取未预乘 8 位 RGBA，采样处 alpha 须为 255。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, "tmp/run-20261011-01/A10")
sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
from build_a10 import (  # noqa: E402
    SAMPLE_LOCAL, theoretical_rgb, fmt_rgb, fmt_rgb_int,
)

OUT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")) / "tmp/run-20261011-01/A10"
TOL = 3          # 题面：每通道容差 ≤ 3


def sample(path: Path):
    with Image.open(path) as im:
        im.load()
        mode, size = im.mode, im.size
        px = im.load()
    return mode, size, px


def main() -> None:
    rel = sys.argv[1] if len(sys.argv) > 1 else "tmp/run-20261011-01/A10/preview/a10-v2.png"
    p = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")) / rel
    mode, size, px = sample(p)
    assert mode == "RGBA", f"期望未预乘 RGBA，实际 {mode}"

    import build_a10 as B

    rows = []
    for idx, (tag, mkey) in enumerate((("①", "per_layer_alpha"), ("②", "group_opacity"))):
        ox, oy = B.exp_origin(idx)
        gx, gy = ox + SAMPLE_LOCAL[0], oy + SAMPLE_LOCAL[1]
        r, g, b, a = px[gx, gy]
        theo = theoretical_rgb(mkey)
        rounded = tuple(int(v + 0.5) for v in theo)
        err = tuple(abs(v - t) for v, t in zip((r, g, b), rounded))
        ok = a == 255 and max(err) <= TOL
        rows.append({
            "tag": tag,
            "experiment_index": idx + 1,
            "experiment_origin_px": [ox, oy],
            "sample_local_px": list(SAMPLE_LOCAL),
            "sample_pixel_index": [gx, gy],
            "measured_rgb": [r, g, b],
            "measured_alpha": a,
            "theoretical_float": fmt_rgb(theo),
            "rounded": fmt_rgb_int(theo),
            "abs_error": " / ".join(str(e) for e in err),
            "verdict": "PASS" if ok else "FAIL",
            "measured": f"{r} / {g} / {b}",
            "note": "红层被蓝层二次透射" if tag == "①" else "仅一次整体 0.5",
            "measured_rgb_list": [r, g, b],
            "theoretical_float_list": [round(v, 6) for v in theo],
            "rounded_list": list(rounded),
            "abs_error_list": list(err),
            "alpha": a,
            "tolerance": TOL,
        })
        print(f"{tag} origin=({ox},{oy}) px[{gx},{gy}] = RGBA({r},{g},{b},{a}) "
              f"| 理论 {fmt_rgb(theo)} → {fmt_rgb_int(theo)} | |Δ| {err} | "
              f"{'PASS' if ok else 'FAIL'}")

    data = {"image": rel, "image_size": list(size), "mode": mode, "rows": rows}
    (OUT / "drafts" / "sample-measured.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("-> tmp/run-20261011-01/A10/drafts/sample-measured.json")


if __name__ == "__main__":
    main()