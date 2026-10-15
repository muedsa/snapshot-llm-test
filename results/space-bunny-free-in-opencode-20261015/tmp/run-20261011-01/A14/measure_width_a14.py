#!/usr/bin/env python
"""A14 字宽标定：量 probe-width.png 的每行墨迹宽度，反推 est_em_str 的系数。

启动基准：总任务根 (suite_root)。
输出：tmp/run-20261011-01/A14/drafts/width-calibration.json
      记录每条的「实测墨迹宽 / 估算宽」比值，并给出应写回 char_em() 的系数。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, "tmp/run-20261011-01/A14")
import build_a14 as m  # noqa: E402

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
T = BASE / "tmp/run-20261011-01/A14"
PNG = T / "preview/probe-width.png"
ROWS = json.loads((T / "drafts/probe-width-rows.json").read_text(encoding="utf-8"))
import probe_width_a14 as pw  # noqa: E402

TEXT = {lab: txt for lab, txt, _ in pw.ROWS}


def ink_bbox(im, y0, y1, thresh=24):
    px = im.load()
    x0, x1 = None, None
    for x in range(im.size[0]):
        col = 0
        for y in range(y0, y1):
            if px[x, y][0] > thresh:
                col += 1
        if col:
            if x0 is None:
                x0 = x
            x1 = x
    return x0, x1


def main() -> None:
    with Image.open(PNG) as s:
        s.load()
        im = s.convert("RGB")

    rows = []
    for r in ROWS:
        text = TEXT[r["label"]]
        a, b = ink_bbox(im, r["y0"], r["y0"] + 130)
        if a is None:
            rows.append({"label": r["label"], "text": text, "measured_px": None})
            continue
        measured = b - a + 1
        est = m.est_em_str(text) * pw.SIZE
        n_cjk = sum(1 for c in text if m.is_fullwidth(c))
        n_other = len(text) - n_cjk
        rows.append({
            "label": r["label"], "text": text,
            "measured_px": measured,
            "ink_left_px": a, "ink_right_px": b,
            "estimated_px": round(est, 1),
            "ratio": round(measured / est, 4),
            "cjk_chars": n_cjk, "other_chars": n_other,
            "per_cjk_em": round(measured / (n_cjk * pw.SIZE), 4) if n_cjk else None,
            "per_other_em": round((measured - n_cjk * 1.0 * pw.SIZE) / (n_other * pw.SIZE), 4)
                             if n_other else None,
        })
        print(f"{r['label']:12} measured={measured:5} est={est:7.1f} ratio={measured/est:.3f}"
              f"  cjk={n_cjk} other={n_other}")

    # 汇总：CJK 类用「每字 em」平均；拉丁类用「系数」平均（相对现模型的比值）
    cjk_vals = [r["per_cjk_em"] for r in rows if r.get("per_cjk_em") is not None]
    lat_rows = [r for r in rows if r["other_chars"] > 0]
    lat_ratio = sum(r["measured_px"] / r["estimated_px"] for r in lat_rows) / len(lat_rows)
    pure_lat = [r for r in lat_rows if r["cjk_chars"] == 0]
    pure_lat_ratio = (sum(r["measured_px"] / r["estimated_px"] for r in pure_lat)
                      / len(pure_lat)) if pure_lat else 1.0

    out = {
        "tool": {"name": "Pillow", "size_px": pw.SIZE, "box_width_px": pw.BOX_W,
                 "method": "每行文字放在 1600px 宽的框里（远大于字面宽，不会被裁），"
                           "用 PIL 逐列扫描该行 y 区间的亮像素取墨迹包围盒",
                 "note": "墨迹包围盒量的是**字形外沿**，不含右侧 advance 空间，"
                         "因此比排版 advance 略窄；用于估算时已加安全余量"},
        "rows": rows,
        "derived": {
            "cjk_em_measured": round(sum(cjk_vals) / len(cjk_vals), 4),
            "cjk_em_in_model": 1.0,
            "latin_ratio_vs_model_all": round(lat_ratio, 4),
            "latin_ratio_vs_model_pure_latin": round(pure_lat_ratio, 4),
            "recommendation": "把非全角字符的 char_em() 整体乘 latin_ratio_vs_model_pure_latin，"
                              "全角保持 1.0em；并在 TITLE_FIT_W 上再留安全余量",
        },
    }
    p = T / "drafts/width-calibration.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print()
    print(json.dumps(out["derived"], ensure_ascii=False, indent=2))
    print("->", p.as_posix())


if __name__ == "__main__":
    main()