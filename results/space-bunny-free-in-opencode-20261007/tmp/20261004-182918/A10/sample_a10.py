# -*- coding: utf-8 -*-
"""A10 采样器：从服务真实响应的 PNG 读取指定点/区域的像素，产出 composite-audit.json 的实测部分。"""
from __future__ import annotations

import json
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A10")
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A10")

COLS = [48, 560, 1072]
ROWS = [186, 572]
PW, PH = 320, 240
TINT = (246, 185, 74)          # #F6B94A


def cell_origin(i):
    return COLS[i % 3], ROWS[i // 3]


def hexs(rgb):
    return "#%02X%02X%02X" % tuple(rgb)


# 格内坐标 (x, y)；名称与审计 JSON 一致
POINTS = {
    0: [("overlap", 180, 100), ("red_only", 70, 60), ("blue_only", 250, 180),
        ("panel_white", 305, 25)],
    1: [("overlap", 180, 100), ("red_only", 70, 60), ("blue_only", 250, 180),
        ("panel_white", 305, 25)],
    2: [("card_stripe_bar", 45, 60), ("card_stripe_gap", 55, 60),
        ("out_stripe_bar", 25, 60), ("out_stripe_gap", 35, 60),
        ("card_text_stroke", 66, 46), ("card_bg", 200, 46)],
    3: [("card_stripe_bar", 45, 60), ("card_stripe_gap", 55, 60),
        ("out_stripe_bar", 25, 60), ("out_stripe_gap", 35, 60),
        ("card_text_stroke", 66, 46), ("card_bg", 200, 46)],
    4: [("tint_gap", 30, 30), ("tint_gap2", 130, 150), ("dark_rect", 70, 80),
        ("just_outside_left", 18, 120), ("just_inside_left", 26, 120),
        ("outside_tint", 8, 210)],
    5: [("circle_center", 160, 120), ("circle_edge_left", 62, 120),
        ("square_corner", 66, 26), ("outside_circle", 160, 232),
        ("outside_circle_left", 40, 120)],
}

# 文字区域（格内坐标的 left, top, right, bottom）：SHARP / BLUR 的字形范围
TEXT_REGION = (56, 66, 264, 106)


def _is_tint(px):
    return (abs(px[0] - TINT[0]) <= 3 and abs(px[1] - TINT[1]) <= 3
            and abs(px[2] - TINT[2]) <= 6)


def analyse(path):
    im = Image.open(path).convert("RGB")
    out = {}
    for i in range(6):
        ox, oy = cell_origin(i)
        pts = {}
        for name, x, y in POINTS[i]:
            px = im.getpixel((ox + x, oy + y))
            pts[name] = {"panel_xy": [x, y], "image_xy": [ox + x, oy + y],
                         "rgb": list(px), "hex": hexs(px)}
        st = {}
        if i in (2, 3):
            st["card_stripe_delta"] = abs(
                im.getpixel((ox + 45, oy + 60))[2]
                - im.getpixel((ox + 55, oy + 60))[2])
            st["out_stripe_delta"] = abs(
                im.getpixel((ox + 25, oy + 60))[2]
                - im.getpixel((ox + 35, oy + 60))[2])
            l, t, r, b = TEXT_REGION
            crop = im.crop((ox + l, oy + t, ox + r, oy + b))
            vals = list(crop.getdata())
            lum = [0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2] for p in vals]
            st["text_region_min_rgb"] = list(min(vals, key=lambda p: sum(p)))
            st["text_region_min_luma"] = round(min(lum), 1)
            st["text_region_mean_luma"] = round(sum(lum) / len(lum), 1)
            # 相邻像素最大落差 = 边缘锐度；整卡范围扫描
            best = (0, None)
            for y in (50, 60, 70):
                for x in range(l, r):
                    d = abs(im.getpixel((ox + x, oy + y))[2]
                            - im.getpixel((ox + x + 1, oy + y))[2])
                    if d > best[0]:
                        best = (d, (x, y))
            st["card_max_adjacent_delta"] = best[0]
            st["card_max_adjacent_delta_at"] = list(best[1]) if best[1] else None
            bo, bi = 0, None
            for y in (50, 60, 70):
                for x in range(4, 38):
                    d = abs(im.getpixel((ox + x, oy + y))[2]
                            - im.getpixel((ox + x + 1, oy + y))[2])
                    if d > bo:
                        bo, bi = d, (x, y)
            st["outside_max_adjacent_delta"] = bo
            st["outside_max_adjacent_delta_at"] = list(bi) if bi else None
        if i == 4:
            xs, ys = [], []
            for y in range(PH):
                for x in range(PW):
                    if _is_tint(im.getpixel((ox + x, oy + y))):
                        xs.append(x)
                        ys.append(y)
            if xs:
                st["tint_bbox"] = "x%d–%d y%d–%d" % (min(xs), max(xs), min(ys),
                                                      max(ys))
                st["tint_bbox_xyxy"] = [min(xs), min(ys), max(xs), max(ys)]
                st["tint_expansion_from_subtree"] = [
                    min(xs) - 40, min(ys) - 40, 279 - max(xs), 199 - max(ys)]
        if i == 5:
            xs, ys = [], []
            for y in range(PH):
                for x in range(PW):
                    if _is_tint(im.getpixel((ox + x, oy + y))):
                        xs.append(x)
                        ys.append(y)
            if xs:
                st["tint_bbox"] = "x%d–%d y%d–%d" % (min(xs), max(xs), min(ys),
                                                      max(ys))
                st["tint_bbox_xyxy"] = [min(xs), min(ys), max(xs), max(ys)]
                st["expected_clip_box"] = [60, 20, 259, 219]
        out[str(i + 1)] = {"points": pts, "stats": st}
    return out


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        OUT, "compositing-lab.png")
    res = analyse(path)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as fh:
            json.dump(res, fh, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()