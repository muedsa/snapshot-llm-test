"""Probe 04c: paragraph behaviour only, one case per generous row.

Question: what does Snapshot do when a Text needs more height than it is given,
and what do maxLines / overflow actually produce?
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P  # noqa: E402
import dsllib as D  # noqa: E402

W, H = 1500, 1420
k = []
LONG = ("这段中文用于验证多行排版与截断行为。Snapshot 的 Text 在固定高度装不下时会静默丢弃"
        "溢出部分，而 maxLines 配合 overflow 才会出现省略号。这是第一行第二行第三行第四行。")

CASES = [
    ("h=34 (about one line)", dict(h=34)),
    ("h=64 (two lines worth)", dict(h=64)),
    ("h=100, no maxLines", dict(h=100)),
    ("maxLines=2 + overflow=ELLIPSIS",
     dict(h=100, a={"maxLines": 2, "overflow": "ELLIPSIS"})),
    ("maxLines=2 + overflow=CLIP", dict(h=100, a={"maxLines": 2})),
    ("maxLines=2 + overflow=FADE",
     dict(h=100, a={"maxLines": 2, "overflow": "FADE"})),
    ("maxLines=2 + overflow=VISIBLE",
     dict(h=100, a={"maxLines": 2, "overflow": "VISIBLE"})),
    ("maxLines=2 + overflow=ELLIPSIS, h huge",
     dict(h=300, a={"maxLines": 2, "overflow": "ELLIPSIS"})),
    ("h=100 + softWrap=false", dict(h=100, a={"softWrap": "false"})),
    ("h=100 + textAlign=CENTER", dict(h=100, a={"textAlign": "CENTER"})),
    ("h=140 + lineHeight=1.9", dict(h=140, a={"lineHeight": 1.9})),
]

TW = 640
y = 90
k.append(D.text_el("PROBE 04c · Text height / maxLines / overflow", x=40,
                   y=24, size=20, color="#F8FAFCFF", w=900, h=28,
                   style="BOLD"))
k.append(D.text_el("identical 4-sentence CJK string in every row; "
                   "grey frame = the Positioned box actually given",
                   x=40, y=52, size=12, color="#64748BFF", w=1200, h=18))

for lab, kw in CASES:
    kw = dict(kw)
    h = kw.pop("h", 110)
    w = kw.pop("w", TW)
    extra = kw.pop("a", {})
    k.append(D.box(760, y - 6, TW + 16, h + 8, color=None,
                   border="1 SOLID #334155FF"))
    k.append(D.el("Positioned", {"left": 60, "top": y, "width": w, "height": h},
                  [D.el("Text", dict({"color": "#F8FAFCFF", "fontSize": 22,
                                      "fontFamily": D.CJK}, **extra, **kw),
                        [D.cdata(LONG)])]))
    k.append(D.text_el(lab, x=1000, y=y + 2, size=12,
                       color="#7DD3FCFF", w=460, h=18))
    y += h + 34

dsl = D.snapshot([D.stack(k, W, H)], W, H, bg="#0B1020FF")
r = P.probe(dsl, "p04c-paragraph")
print("probe04c", r.get("ok"), r.get("status"), r.get("error"))

from PIL import Image  # noqa: E402
if r.get("ok"):
    im = Image.open(r["image"]).convert("RGB")
    yy = 90
    for lab, kw in CASES:
        h = dict(kw).pop("h", 110)
        # count non-background text rows inside the box
        rows = 0
        prev = False
        for t in range(yy, min(yy + h, im.size[1])):
            ink = sum(1 for x in range(60, 60 + TW)
                      if sum(im.getpixel((x, t))) > 330)
            if ink > 2 and not prev:
                rows += 1
            prev = ink > 2
        print("  %-34s rendered_text_rows=%d" % (lab, rows))
        yy += h + 34