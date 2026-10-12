# -*- coding: utf-8 -*-
"""A21 probe 3: measure the exact round-02 / round-03 title strings at the
exact sizes they will be set in, so every layout box is sized from real ink."""
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "A21"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
from PIL import Image  # noqa: E402
import brandkit as B  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A21")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A21")
snapkit.configure("A21", OUT, TMP)
DISPLAY = B.DISPLAY
UI = B.UI
C = B.COPY

SAMPLES = [
    ("s48a", "\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670", 48, "BOLD", 0, DISPLAY),
    ("s48b", "\u7684\u7ed3\u6784\u5316\u65b9\u6cd5", 48, "BOLD", 0, DISPLAY),
    ("s52a", "\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670", 52, "BOLD", 0, DISPLAY),
    ("s52b", "\u7684\u7ed3\u6784\u5316\u65b9\u6cd5", 52, "BOLD", 0, DISPLAY),
    ("lock32", C["brand_cjk"] + " " + C["brand_latin"], 32, "BOLD", 2, DISPLAY),
    ("cjk44", C["brand_cjk"], 44, "BOLD", 2, DISPLAY),
    ("full52", C["long_title_a"] + C["long_title_b"], 52, "BOLD", 0, DISPLAY),
    ("s46a", "\u8ba9\u590d\u6742\u4fe1\u606f\u53d8\u5f97\u6e05\u6670", 46, "BOLD", 0, DISPLAY),
    ("free26b", C["free"], 26, "BOLD", 1, UI),
    ("sponsor26b", C["sponsor"], 26, "NORMAL", 0.5, UI),
]

kids, meta = [], []
y = 30
for key, s, size, style, ls, font in SAMPLES:
    kids.append(D.text_el(s, x=60, y=y, color="#000000FF", size=size,
                          font=font, style=style, ls=ls))
    meta.append({"key": key, "text": s, "size": size, "style": style, "ls": ls,
                 "font": font, "box_top": y})
    y += int(size * 2.05) + 34

W, H = 1900, y + 40
dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#FFFFFFFF")
res = snapkit.render(dsl, "probe-r02.png", "probe-r02.snapshot", final=False)
print("render ok=%s status=%s" % (res.get("ok"), res.get("status")))
for w in D.warnings():
    print("WARN", w)
if res.get("ok"):
    im = Image.open(res["image"]).convert("L")
    Wd, Hd = im.size
    px = im.load()
    out = []
    for m in meta:
        top = m["box_top"]
        bot = top + int(m["size"] * 1.75)
        minx, miny, maxx, maxy = Wd, Hd, -1, -1
        for yy in range(max(0, top - 8), min(Hd, bot)):
            for xx in range(40, Wd):
                if px[xx, yy] < 200:
                    minx, maxx = min(minx, xx), max(maxx, xx)
                    miny, maxy = min(miny, yy), max(maxy, yy)
        rec = {"key": m["key"], "text": m["text"], "size": m["size"],
               "style": m["style"], "ls": m["ls"],
               "font": "DISPLAY" if m["font"] == DISPLAY else "UI",
               "ink_w": maxx - minx + 1 if maxx >= 0 else None,
               "ink_h": maxy - miny + 1 if maxx >= 0 else None,
               "ink_dy": miny - top if maxx >= 0 else None}
        out.append(rec)
        print("%-10s size=%-4s w=%-5s h=%-4s dy=%-4s %s" %
              (m["key"], m["size"], rec["ink_w"], rec["ink_h"], rec["ink_dy"],
               rec["text"]))
    with open(os.path.join(TMP, "probe-r02.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)