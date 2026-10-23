"""A16 参考图诊断（第 5 步）：修正 diag4 中被裁切/被污染的文本框，并裁底部区块。

diag4.json 有三处搜索窗太窄：page_title 与 footer 的左边缘正好压在窗口边界
（ink_bbox.left == search_box.left），chart_unit 顶部被切；yaxis_ticks 的窗口
横向包含了卡片标题「收入与成本对比」。本步放宽窗口重测，并额外量利润明细四列与
重点提示框的文字框，供 findings.json 的「图片位置」使用。

只做测量与出图；判断写在 findings.json。运行方式：
    python -I tmp/<run_id>/_suite/gen/a16_diag5.py
"""
from __future__ import annotations

import collections
import json
import pathlib

import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TASK = SUITE_ROOT / "tasks" / "A16-visual-data-forensics"
OUT = SUITE_ROOT / "tmp" / RUN_ID / "A16" / "gen" / "a16"

TEXT_REGIONS = [
    ("page_title", 10, 36, 700, 86),
    ("page_subtitle", 10, 90, 700, 120),
    ("chart_unit", 80, 226, 400, 256),
    ("yaxis_ticks", 96, 276, 175, 578),
    ("profit_card_title", 80, 652, 700, 700),
    ("callout_title", 950, 652, 1220, 700),
    ("callout_body", 950, 700, 1220, 800),
    ("footer", 10, 844, 700, 880),
]

CROPS = [
    (60, 640, 1230, 830, "crop-14-bottom.png", 2),
    (60, 640, 700, 830, "crop-15-profit-left.png", 3),
    (700, 640, 1230, 830, "crop-16-callout-right.png", 3),
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    img = Image.open(TASK / "inputs" / "flawed-report.png").convert("RGB")
    arr = np.array(img)
    h, w, _ = arr.shape
    ai = arr.astype(int)

    entries = []
    for name, x0, y0, x1, y1 in TEXT_REGIONS:
        sub = ai[y0:y1, x0:x1]
        common = collections.Counter(
            map(tuple, sub.reshape(-1, 3))).most_common(1)[0][0]
        bg = np.array([int(v) for v in common])
        dist = np.abs(sub - bg).max(axis=2)
        sat = sub.max(axis=2) - sub.min(axis=2)
        ink = (dist > 30) & (sat <= 60)
        e: dict = {"region": name, "search_box": [x0, y0, x1, y1],
                   "bg": [int(v) for v in bg]}
        if not ink.any():
            e["found"] = False
            entries.append(e)
            continue
        ys, xs = np.nonzero(ink)
        e.update({
            "found": True,
            "ink_bbox": [int(xs.min()) + x0, int(ys.min()) + y0,
                         int(xs.max()) + x0, int(ys.max()) + y0],
            "ink_w": int(xs.max() - xs.min() + 1),
            "ink_h": int(ys.max() - ys.min() + 1),
            "ink_px": int(ink.sum()),
        })
        d = np.abs(sub - bg).sum(axis=2)
        d[~ink] = -1
        cy, cx = np.unravel_index(int(np.argmax(d)), d.shape)
        e["ink_core_rgb"] = [int(v) for v in sub[cy, cx]]
        # 是否仍被搜索窗裁切（若贴边则结果不可用，需再放宽）
        e["clipped"] = [bool(xs.min() == 0), bool(ys.min() == 0),
                        bool(xs.max() == sub.shape[1] - 1),
                        bool(ys.max() == sub.shape[0] - 1)]
        entries.append(e)

    # 利润明细四列：在 y 690..800 之间找墨迹列段
    band = ai[686:806, 80:1220]
    b0 = collections.Counter(map(tuple, band.reshape(-1, 3))).most_common(1)[0][0]
    bg = np.array([int(v) for v in b0])
    m = (np.abs(band - bg).max(axis=2) > 30) & \
        ((band.max(axis=2) - band.min(axis=2)) <= 60)
    colsum = m.sum(axis=0)
    segs, start = [], None
    for i, v in enumerate(colsum):
        if v > 0 and start is None:
            start = i
        elif v == 0 and start is not None:
            if i - start >= 3:
                segs.append([int(start) + 80, int(i - 1) + 80])
            start = None
    if start is not None:
        segs.append([int(start) + 80, int(len(colsum) - 1) + 80])
    rows = []
    for (a, b) in segs:
        sub = ai[686:806, a:b + 1]
        mm = m[:, a - 80:b + 1]
        ys, xs = np.nonzero(mm)
        rows.append({
            "col_range_x": [a, b],
            "ink_bbox": [int(xs.min()) + a, int(ys.min()) + 686,
                         int(xs.max()) + a, int(ys.max()) + 686],
            "ink_w": int(xs.max() - xs.min() + 1),
            "ink_h": int(ys.max() - ys.min() + 1),
            "ink_px": int(mm.sum()),
        })

    crops = []
    for x0, y0, x1, y1, name, scale in CROPS:
        sub = img.crop((x0, y0, min(x1, w), min(y1, h)))
        sub = sub.resize((sub.width * scale, sub.height * scale), Image.LANCZOS)
        sub.save(OUT / name)
        crops.append({"name": name, "box": [x0, y0, x1, y1], "scale": scale})

    out = {
        "image_size": [w, h],
        "note": "clipped=[left,top,right,bottom] 为真说明该边仍贴在搜索窗上",
        "regions": entries,
        "profit_band_y": [686, 806],
        "profit_columns": rows,
        "crops": crops,
    }
    print(json.dumps(out, ensure_ascii=True, indent=1))
    (OUT / "diag5.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("->", OUT / "diag5.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
