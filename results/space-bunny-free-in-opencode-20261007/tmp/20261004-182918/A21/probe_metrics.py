# -*- coding: utf-8 -*-
"""A21 probe: measure real advance widths of every string/size the poster needs,
and verify Transform / gradient / BOLD all work on the live service.

Output: tmp/20261004-182918/A21/preview/probe-metrics.png
        tmp/20261004-182918/A21/probe-metrics.json  (measured ink boxes)
"""
import json
import math
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
from PIL import Image  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A21")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A21")
snapkit.configure("A21", OUT, TMP)

UI = "Inter,Noto Sans CJK SC"

# (key, text, fontSize, fontStyle, letterSpacing)
SAMPLES = [
    ("title_cjk_108", "叠光", 108, "BOLD", 2),
    ("title_latin_64", "Layerlight", 64, "BOLD", 1),
    ("tagline_36", "让复杂信息变得清晰", 36, "NORMAL", 3),
    ("chip_24", "ONLINE LAUNCH", 24, "BOLD", 2),
    ("datetime_28", "2026.11.07 19:30", 28, "BOLD", 0.5),
    ("speakers_28", "讲者：林川 / 苏言", 28, "NORMAL", 1),
    ("url_26", "layerlight.example.org", 26, "BOLD", 0.5),
    ("wordmark_24", "Layerlight", 24, "BOLD", 2),
    ("label_24", "讲者", 24, "NORMAL", 1),
    ("date_28", "2026.11.07", 28, "BOLD", 1),
    ("time_28", "19:30", 28, "BOLD", 1),
    ("lt_title_52a", "当所有信息都想成为标题：", 52, "BOLD", 0),
    ("lt_title_52b", "让复杂信息变得清晰的结构化方法", 52, "BOLD", 0),
    ("lt_title_48a", "当所有信息都想成为标题：", 48, "BOLD", 0),
    ("lt_title_48b", "让复杂信息变得清晰的结构化方法", 48, "BOLD", 0),
    ("sponsor_26", "Northstar Research / 云构工具", 26, "NORMAL", 0.5),
    ("free_26", "免费参加 · 无需报名", 26, "NORMAL", 1),
    ("clarity_26", "Clarity through structure", 26, "NORMAL", 1),
    ("tagline_32", "让复杂信息变得清晰", 32, "NORMAL", 2),
    ("presenter_30", "讲者：林川 / 苏言", 30, "NORMAL", 1),
]

kids = []
meta = []
y = 30
for key, s, size, style, ls in SAMPLES:
    kids.append(D.text_el(s, x=60, y=y, color="#000000FF", size=size,
                          font=UI, style=style, ls=ls))
    meta.append({"key": key, "text": s, "size": size, "style": style,
                 "ls": ls, "box_top": y})
    y += int(size * 2.05) + 34

W = 1600
H = y + 470


def rot_matrix(deg):
    th = math.radians(deg)
    a, b = math.cos(th), -math.sin(th)
    c, d = math.sin(th), math.cos(th)
    return "(%f,%f,0,0,%f,%f,0,0,0,0,1,0,0,0,0,1)" % (a, b, c, d)


sx, sy = 120, y + 20
kids.append(D.box(sx, sy, 180, 90, color="#6D4AFFFF", radius=10))
kids.append(D.el("Positioned", {"left": sx + 220, "top": sy, "width": 180, "height": 90},
                 [D.el("Transform", {"matrix": rot_matrix(18), "origin": "(0,0)",
                                     "alignment": "CENTER"},
                       [D.el("Container", {"width": 180, "height": 90,
                                           "color": "#4BE3C8FF",
                                           "borderRadius": "6"})])]))
kids.append(D.box(sx + 440, sy, 90, 90, color="#FF6D4AFF", radius=45))
kids.append(D.box(sx + 560, sy, 90, 90, radius=45, border="3 SOLID #6D4AFFFF"))
kids.append(D.box(sx + 680, sy, 200, 90, radius=12,
                  gradient={"gradientType": "LINEAR",
                            "gradientColors": "#6D4AFF,#4BE3C8",
                            "gradientBegin": "TOP_LEFT",
                            "gradientEnd": "BOTTOM_RIGHT"}))
kids.append(D.box(sx + 910, sy, 160, 160, radius=80,
                  gradient={"gradientType": "RADIAL",
                            "gradientColors": "#FFFFFF00,#4BE3C8AA",
                            "gradientStops": "0,1"}))
kids.append(D.box(sx + 1110, sy, 180, 90, color="#6D4AFFB3", radius=12))
kids.append(D.dashed(sx, sx + 1290, sy + 120, "#000000FF", 3, 16, 10))
kids.append(D.text_el("BOLD ITALIC 叠光", x=sx, y=sy + 150,
                      color="#6D4AFFFF", size=36, font=UI,
                      style="BOLD_ITALIC", ls=4))
kids.append(D.text_el("Inter Black 叠光 Layerlight", x=sx, y=sy + 220,
                      color="#000000FF", size=40, font="Inter Black,Noto Sans CJK SC",
                      ls=1))

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#FFFFFFFF")
res = snapkit.render(dsl, "probe-metrics.png", "probe-metrics.snapshot",
                     final=False)
print("render ok=%s status=%s bytes=%s" % (res.get("ok"), res.get("status"),
                                           res.get("bytes")))
for w in D.warnings():
    print("WARN", w)
if res.get("ok"):
    im = Image.open(res["image"]).convert("L")
    Wd, Hd = im.size
    px = im.load()
    out = {"canvas": [Wd, Hd], "samples": []}
    for m in meta:
        top = m["box_top"]
        bot = top + int(m["size"] * 1.75)
        minx, miny, maxx, maxy = Wd, Hd, -1, -1
        for yy in range(max(0, top - 8), min(Hd, bot)):
            for xx in range(40, Wd):
                if px[xx, yy] < 200:
                    minx = min(minx, xx)
                    maxx = max(maxx, xx)
                    miny = min(miny, yy)
                    maxy = max(maxy, yy)
        m2 = dict(m)
        m2["ink_x0"] = minx if maxx >= 0 else None
        m2["ink_x1"] = maxx if maxx >= 0 else None
        m2["ink_y0"] = miny if maxx >= 0 else None
        m2["ink_y1"] = maxy if maxx >= 0 else None
        m2["ink_w"] = (maxx - minx + 1) if maxx >= 0 else None
        m2["ink_h"] = (maxy - miny + 1) if maxx >= 0 else None
        m2["ink_dy"] = (miny - top) if maxx >= 0 else None
        m2["est_w"] = round(D.est_width(m["text"], m["size"]), 1)
        out["samples"].append(m2)
        print("%-16s size=%-4s x=%s..%s w=%s h=%s dy=%s est_w=%s" %
              (m["key"], m["size"], m2["ink_x0"], m2["ink_x1"], m2["ink_w"],
               m2["ink_h"], m2["ink_dy"], m2["est_w"]))
    with open(os.path.join(TMP, "probe-metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print("probe canvas", im.size, "shape probe top-left", (sx, sy))