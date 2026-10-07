# -*- coding: utf-8 -*-
"""A13: render candidate geometries of the chosen direction side by side so the
choice can be made by looking at one image instead of guessing."""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402
import layerlight as L  # noqa: E402

TASK = "A13"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
PREV = os.path.join(TMP, "preview")
os.makedirs(PREV, exist_ok=True)

CANDS = [
    ("C1 solid core r64 o92", L.build_dir_a(plate=300, radius=64, offset=92, origin=60),
     L.ROLE_COLOR["A"]),
    ("C2 void r64 o92", L.build_mark(plate=300, radius=64, offset=92, origin=60),
     L.MARK_ROLE_COLOR),
    ("C3 void r60 o150", L.build_mark(plate=300, radius=60, offset=150, origin=6),
     L.MARK_ROLE_COLOR),
    ("C4 void r64 o170", L.build_mark(plate=300, radius=64, offset=170, origin=0),
     L.MARK_ROLE_COLOR),
    ("C5 void r56 o132", L.build_mark(plate=300, radius=56, offset=132, origin=20),
     L.MARK_ROLE_COLOR),
    ("C6 void r72 o120", L.build_mark(plate=300, radius=72, offset=120, origin=26),
     L.MARK_ROLE_COLOR),
]

CELL = 340
INK = 280
W = CELL * len(CANDS) + 40
H = 420
BG = "#F6F7FBFF"
kids = []
for i, (name, mark, cols) in enumerate(CANDS):
    cx = 20 + i * CELL + CELL / 2.0
    ox, oy, k = L.fitted(mark, cx, 170.0, INK)
    kids += L.emit(mark, ox, oy, k, cols, gradient=None)
    xs, ys, xe, ye = L.bbox(mark)
    # the void, drawn as a dashed guide so the negative space is measurable
    v = mark.get("void")
    if v:
        vx, vy, vw, vh = v["rect"]
        gx0, gy0 = ox + vx * k, oy + vy * k
        gx1, gy1 = gx0 + vw * k, gy0 + vh * k
        kids.append(D.dashed(gx0, gx1, gy0, "#B91C1CFF", 1, 6, 5))
        kids.append(D.dashed(gx0, gx1, gy1, "#B91C1CFF", 1, 6, 5))
        kids.append(D.dashed(gx0, gy0, gy1, "#B91C1CFF", 1, 6, 5))
        kids.append(D.dashed(gx1, gy0, gy1, "#B91C1CFF", 1, 6, 5))
    kids.append(D.hline(cx - 140, cx + 140, 330, "#C9D1E0FF", 1))
    kids.append(D.text_el(name, x=cx - 150, y=346, w=300, h=24, size=17,
                          color="#0B1020FF", align="CENTER"))
    span = max(xe - xs, ye - ys)
    kids.append(D.text_el("span %.0f  void %.0f  %.0f%% of span  r %.0f" % (
        span, vw if v else 0, (vw / span * 100) if v else 0, mark["params"]["radius"]),
        x=cx - 150, y=372, w=300, h=22, size=15, color="#5B6478FF",
        align="CENTER", font=D.MONO))

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg=BG)
with open(os.path.join(TMP, "drafts", "v07-candidates.snapshot"), "w",
          encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
r = snapkit.render(dsl, "candidates.png", "candidates.snapshot", final=False, out_dir=PREV)
print("render ok=%s status=%s bytes=%s" % (r.get("ok"), r.get("status"), r.get("bytes")))
if not r.get("ok"):
    print(r.get("error"))
for w in D.warnings():
    print("WARN", w)