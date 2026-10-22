# -*- coding: utf-8 -*-
"""A15 shared text glyph measurer.

Measures visible glyph bounding boxes for every reconstruction text element
using the SAME window + predicate for any input image. Run on
reference.png -> texts-reference.json (targets), run on reconstructed.png
-> recon: actual values. Calibration compares the anchored edge only:
  anchor=left   -> compare box[0]
  anchor=center -> compare (box[0]+box[2])/2
  anchor=right  -> compare box[2]
vertical always compares box[1] (visible glyph top).

Usage: python measure_texts.py <image> <out.json>
"""
import json
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(".")


def lum(p):
    return (p[0] * 299 + p[1] * 587 + p[2] * 114) // 1000


def dark(p):
    return lum(p) < 160


def bright(p):
    return lum(p) > 150


# key: (win x1,y1,x2,y2, predicate, anchor)
SPECS = {
    "northstar": ((58, 28, 215, 62), bright, "left"),
    "nav_overview": ((55, 115, 205, 152), bright, "left"),
    "nav_projects": ((55, 182, 205, 215), bright, "left"),
    "nav_analytics": ((55, 246, 205, 280), bright, "left"),
    "nav_settings": ((55, 310, 205, 345), bright, "left"),
    "ws1": ((32, 762, 190, 790), bright, "left"),
    "ws2": ((32, 796, 190, 824), bright, "left"),
    "ws3": ((32, 828, 190, 856), bright, "left"),
    "title": ((255, 32, 620, 76), dark, "left"),
    "subtitle": ((255, 80, 540, 110), dark, "left"),
    "button": ((1195, 48, 1395, 84), bright, "center"),
    "kpi1_label": ((275, 154, 560, 180), dark, "left"),
    "kpi1_value": ((275, 190, 600, 234), dark, "left"),
    "kpi1_change": ((275, 240, 560, 266), dark, "left"),
    "kpi2_label": ((659, 154, 960, 180), dark, "left"),
    "kpi2_value": ((660, 190, 980, 234), dark, "left"),
    "kpi2_change": ((659, 240, 960, 266), dark, "left"),
    "kpi3_label": ((1043, 154, 1330, 180), dark, "left"),
    "kpi3_value": ((1044, 190, 1370, 234), dark, "left"),
    "kpi3_change": ((1043, 240, 1330, 266), dark, "left"),
    "chart_title": ((275, 330, 560, 366), dark, "left"),
    "chart_period": ((870, 330, 1000, 362), dark, "right"),
    "unit": ((278, 368, 420, 394), dark, "left"),
    "tick_120": ((270, 392, 330, 415), dark, "right"),
    "tick_90": ((270, 428, 330, 451), dark, "right"),
    "tick_60": ((270, 464, 330, 487), dark, "right"),
    "tick_30": ((270, 500, 330, 523), dark, "right"),
    "tick_0": ((270, 536, 330, 559), dark, "right"),
    "month_Apr": ((330, 555, 440, 580), dark, "center"),
    "month_May": ((430, 555, 540, 580), dark, "center"),
    "month_Jun": ((531, 555, 641, 580), dark, "center"),
    "month_Jul": ((632, 555, 742, 580), dark, "center"),
    "month_Aug": ((733, 555, 843, 580), dark, "center"),
    "month_Sep": ((834, 555, 944, 580), dark, "center"),
    "activity_title": ((1045, 328, 1330, 364), dark, "left"),
    "act_t1": ((1070, 388, 1330, 416), dark, "left"),
    "act_time1": ((1070, 418, 1330, 442), dark, "left"),
    "act_t2": ((1070, 448, 1330, 476), dark, "left"),
    "act_time2": ((1070, 478, 1330, 502), dark, "left"),
    "act_t3": ((1070, 508, 1330, 538), dark, "left"),
    "act_time3": ((1070, 538, 1330, 562), dark, "left"),
    "table_title": ((275, 636, 640, 676), dark, "left"),
    "th_project": ((290, 694, 460, 714), dark, "left"),
    "th_owner": ((775, 694, 890, 714), dark, "left"),
    "th_status": ((1025, 694, 1140, 714), dark, "left"),
    "th_due": ((1222, 694, 1330, 714), dark, "left"),
    "r1_project": ((290, 726, 640, 756), dark, "left"),
    "r1_owner": ((775, 726, 900, 752), dark, "left"),
    "r1_due": ((1222, 726, 1340, 752), dark, "left"),
    "r2_project": ((290, 762, 640, 790), dark, "left"),
    "r2_owner": ((775, 762, 900, 788), dark, "left"),
    "r2_due": ((1222, 762, 1340, 788), dark, "left"),
    "r3_project": ((290, 797, 640, 825), dark, "left"),
    "r3_owner": ((775, 797, 900, 823), dark, "left"),
    "r3_due": ((1222, 797, 1340, 823), dark, "left"),
    "pill_progress": ((1032, 732, 1172, 754), dark, "center"),
    "pill_review": ((1032, 767, 1172, 789), dark, "center"),
    "pill_done": ((1032, 802, 1172, 824), dark, "center"),
    "footer": ((255, 860, 545, 886), dark, "left"),
}


def main():
    img_path = pathlib.Path(sys.argv[1])
    out_path = pathlib.Path(sys.argv[2])
    img = Image.open(img_path).convert("RGB")
    px = img.load()
    R = {}
    for key, ((x1, y1, x2, y2), pred, anchor) in SPECS.items():
        xs, ys = [], []
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                if pred(px[x, y]):
                    xs.append(x)
                    ys.append(y)
        R[key] = {
            "box": [min(xs), min(ys), max(xs), max(ys)] if xs else None,
            "anchor": anchor,
            "win": [x1, y1, x2, y2],
        }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(R, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    missing = [k for k, v in R.items() if v["box"] is None]
    print(f"measured {len(R)} texts from {img_path.as_posix()}; "
          f"missing={missing}")


if __name__ == "__main__":
    main()
