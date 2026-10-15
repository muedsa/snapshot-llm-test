#!/usr/bin/env python
"""A15 参考图第四次测量：侧栏文字色、状态药丸精确框、表头带 x 范围、图表月标签 x。"""
from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path

from PIL import Image

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
REF = BASE / "tasks/A15-reference-reconstruction/inputs/reference.png"
OUTD = BASE / "tmp/run-20261011-01/A15/drafts"
WHITE = (255, 255, 255)
MAIN = (243, 246, 251)
SIDE = (20, 35, 60)


def hx(t):
    return "#%02X%02X%02X" % t[:3]


def lightest(box, img, skip_bg):
    px = img.load()
    x0, y0, x1, y1 = box
    cnt = Counter()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = px[x, y]
            if c != skip_bg:
                cnt[c] += 1
    return [(hx(c), n) for c, n in cnt.most_common(5)]


def main() -> None:
    with Image.open(REF) as s:
        s.load()
        im = s.convert("RGB")
    px = im.load()
    r = {}

    # 侧栏文字（取最亮的非底色）
    r["brand_text"] = lightest((72, 36, 192, 56), im, SIDE)[:2]
    r["nav_overview_text"] = lightest((63, 126, 200, 148), im, (41, 68, 103))[:2]
    r["nav_other_text"] = lightest((63, 250, 200, 276), im, SIDE)[:2]
    r["nav_selected_bg"] = hx(px[100, 120])
    r["nav_other_dot"] = lightest((34, 254, 46, 270), im, SIDE)[:2]
    r["nav_sel_dot"] = lightest((34, 128, 46, 144), im, (41, 68, 103))[:2]
    r["pro_label"] = lightest((36, 764, 192, 786), im, (35, 57, 84))[:2]
    r["pro_members"] = lightest((36, 798, 192, 822), im, (35, 57, 84))[:2]
    r["pro_manage"] = lightest((36, 828, 192, 854), im, (35, 57, 84))[:2]
    r["brand_mark"] = {
        "outer": lightest((30, 33, 57, 60), im, SIDE)[:2],
        "inner": hx(px[43, 46]), "corner": hx(px[31, 34]),
    }

    # 状态药丸：以列扫描精确框
    for i, yc in enumerate((742, 776, 811)):
        xs = [x for x in range(1000, 1210) if px[x, yc] != WHITE]
        ys = [y for y in range(yc - 30, yc + 30) if px[1040, y] != WHITE]
        # 只取属于本行的连续段
        run = []
        prev = None
        start = None
        for y in range(yc - 30, yc + 30):
            isb = px[1040, y] != WHITE
            if isb and prev is not True:
                start = y
            if (not isb) and prev is True:
                run.append((start, y - 1))
            prev = isb
        if prev:
            run.append((start, yc + 29))
        run = [q for q in run if q[1] - q[0] >= 10]
        r[f"pill{i}"] = {"x": [min(xs), max(xs)], "y": run,
                         "fill": hx(px[min(xs) + 2, yc]),
                         "text_x": None}
        # 药丸内文字墨迹
        tx = [x for x in range(min(xs), max(xs) + 1)
              if sum(px[x, yc]) < 600]
        r[f"pill{i}"]["text_x"] = [min(tx), max(tx)] if tx else None

    # 表头底色带 x 范围（沿 y=705 找 MAIN 连通段）
    segs = []
    cur, s = False, None
    for x in range(240, 1440):
        isb = px[x, 705] == MAIN
        if isb and not cur:
            s = x
        if (not isb) and cur:
            segs.append((s, x - 1))
        cur = isb
    if cur:
        segs.append((s, 1439))
    r["header_band_x_segments_at_y705"] = [q for q in segs if q[1] - q[0] > 20]

    # 表格分隔线 x 范围
    for y in (760, 795):
        xs = [x for x in range(240, 1440) if hx(px[x, y]) == "#EBEFF5"]
        r[f"sep_y{y}_x"] = [min(xs), max(xs)] if xs else None

    # 月标签 x（按每个柱中心附近的墨迹）
    for i, cx in enumerate((383.5, 484.5, 585.5, 686.5, 787.5, 888.5)):
        xs = [x for x in range(int(cx) - 45, int(cx) + 45)
              if sum(px[x, 566]) < 700]
        r[f"month{i}_x"] = [min(xs), max(xs)] if xs else None

    # 活动项文字 x
    for i, (y0, y1) in enumerate([(393, 414), (420, 436), (453, 474), (480, 496),
                                  (513, 534), (540, 556)]):
        xs = [x for x in range(1070, 1400) if sum(px[x, y0]) < 700]
        r[f"activity{i}_x"] = [min(xs), max(xs)] if xs else None

    # KPI 卡内文字 x
    for i, x0 in enumerate((260, 644, 1028)):
        for nm, (ya, yb) in {"label": (158, 174), "value": (196, 232),
                             "change": (243, 262)}.items():
            xs = [x for x in range(x0 + 5, x0 + 355) if sum(px[x, ya]) < 690]
            r[f"kpi{i}_{nm}_x"] = [min(xs), max(xs)] if xs else None

    # 导出按钮内文字
    xs = [x for x in range(1184, 1400) if sum(px[x, 63]) > 600]
    r["export_text_x"] = [min(xs), max(xs)] if xs else None
    ys = [y for y in range(43, 91) if sum(px[1290, y]) > 600]
    r["export_text_y"] = [min(ys), max(ys)] if ys else None
    # 按钮圆角
    r["export_corner"] = [hx(px[x, 44]) for x in range(1184, 1200)]

    (OUTD / "reference-geometry-4.json").write_text(
        json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    for k, v in r.items():
        print(k, "=", v)


if __name__ == "__main__":
    main()