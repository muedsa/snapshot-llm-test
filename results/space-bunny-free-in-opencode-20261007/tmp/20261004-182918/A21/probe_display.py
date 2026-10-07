# -*- coding: utf-8 -*-
"""A21 probe 2: measure the same strings in the DISPLAY face (Inter Black),
which is wider than Inter BOLD, so layout boxes must be sized from real ink."""
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

SAMPLES = [
    ("d_cjk_108", B.COPY["brand_cjk"], 108, "BOLD", 2, DISPLAY),
    ("d_latin_64", B.COPY["brand_latin"], 64, "BOLD", 1, DISPLAY),
    ("d_wordmark_24", B.COPY["brand_latin"], 24, "BOLD", 2, DISPLAY),
    ("d_latin_32", B.COPY["brand_latin"], 32, "BOLD", 2, DISPLAY),
    ("d_cjk_32", B.COPY["brand_cjk"], 32, "BOLD", 2, DISPLAY),
    ("d_lt52a", B.COPY["long_title_a"], 52, "BOLD", 0, DISPLAY),
    ("d_lt52b", B.COPY["long_title_b"], 52, "BOLD", 0, DISPLAY),
    ("d_lt48a", B.COPY["long_title_a"], 48, "BOLD", 0, DISPLAY),
    ("d_lt48b", B.COPY["long_title_b"], 48, "BOLD", 0, DISPLAY),
    ("d_lt56a", B.COPY["long_title_a"], 56, "BOLD", 0, DISPLAY),
    ("d_lt56b", B.COPY["long_title_b"], 56, "BOLD", 0, DISPLAY),
    ("d_cjk_96", B.COPY["brand_cjk"], 96, "BOLD", 2, DISPLAY),
    ("d_latin_60", B.COPY["brand_latin"], 60, "BOLD", 1, DISPLAY),
    ("d_chip26", B.COPY["online"], 26, "BOLD", 2, DISPLAY),
    ("u_chip_26", B.COPY["online"], 26, "BOLD", 2, UI),
    ("u_tagline_32", B.COPY["tagline"], 32, "NORMAL", 2, UI),
    ("u_datetime_30", B.COPY["datetime"], 30, "BOLD", 0.5, UI),
    ("u_speakers_26", B.COPY["speakers"], 26, "NORMAL", 1, UI),
    ("u_url_28", B.COPY["url"], 28, "BOLD", 0.5, UI),
    ("u_sponsor_28", B.COPY["sponsor"], 28, "NORMAL", 0.5, UI),
    ("u_free_28", B.COPY["free"], 28, "NORMAL", 1, UI),
    ("u_clarity_28", B.COPY["clarity_en"], 28, "NORMAL", 1, UI),
    ("u_sponsor_26", B.COPY["sponsor"], 26, "NORMAL", 0.5, UI),
    ("u_free_26", B.COPY["free"], 26, "NORMAL", 1, UI),
]

kids = []
meta = []
y = 30
for key, s, size, style, ls, font in SAMPLES:
    kids.append(D.text_el(s, x=60, y=y, color="#000000FF", size=size,
                          font=font, style=style, ls=ls))
    meta.append({"key": key, "text": s, "size": size, "style": style, "ls": ls,
                 "font": font, "box_top": y})
    y += int(size * 2.05) + 34

W = 1600
H = y + 40
dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#FFFFFFFF")
res = snapkit.render(dsl, "probe-display.png", "probe-display.snapshot", final=False)
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
                    minx = min(minx, xx)
                    maxx = max(maxx, xx)
                    miny = min(miny, yy)
                    maxy = max(maxy, yy)
        rec = {"key": m["key"], "text": m["text"], "size": m["size"],
               "style": m["style"], "ls": m["ls"], "font": m["font"],
               "ink_w": maxx - minx + 1 if maxx >= 0 else None,
               "ink_h": maxy - miny + 1 if maxx >= 0 else None,
               "ink_dy": miny - top if maxx >= 0 else None}
        out.append(rec)
        print("%-14s size=%-4s w=%-5s h=%-4s dy=%-4s %s" %
              (m["key"], m["size"], rec["ink_w"], rec["ink_h"], rec["ink_dy"],
               "DISPLAY" if m["font"] == DISPLAY else "UI"))
    with open(os.path.join(TMP, "probe-display.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)