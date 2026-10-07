# -*- coding: utf-8 -*-
"""A09 probe 1: verify Transform matrix column order, pivot semantics and direction.

Each panel shows one 120x120 stamp under a different Transform variant, on top of a
reference frame (dashed 120x120 box) + pivot cross, so the effective pivot and the
rotation direction can be read straight off the image.
"""
import json
import math
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
SUITE = os.path.join(ROOT, "tmp", "20261004-182918", "_suite")
sys.path.insert(0, SUITE)
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "A09"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)

STAMP = os.path.join(ROOT, "tasks", "A09-transform-atlas", "inputs", "stamp.json")
st = json.load(open(STAMP, encoding="utf-8"))
RECS = [r["xywh"] for r in st["rectangles"]]
COLS = [r["color"] for r in st["rectangles"]]
DOT = st["dot"]


def stamp_kids():
    kids = []
    for (x, y, w, h), c in zip(RECS, COLS):
        kids.append(D.box(x, y, w, h, color=c + "FF"))
    cx, cy = DOT["center"]
    r = DOT["radius"]
    kids.append(D.box(cx - r, cy - r, 2 * r, 2 * r, color=DOT["color"] + "FF", radius=r))
    return kids


def m4(a, b, c, d, e, f):
    return "(%.6f,%.6f,0,0,%.6f,%.6f,0,0,0,0,1,0,%.4f,%.4f,0,1)" % (a, b, c, d, e, f)


def rot_cw(deg):
    th = math.radians(deg)
    return math.cos(th), math.sin(th), -math.sin(th), math.cos(th)


def pivot_compose(a, b, c, d, px=60.0, py=60.0):
    return px - (a * px + c * py), py - (b * px + d * py)


LIN90 = rot_cw(90)
E90 = pivot_compose(*LIN90)
LIN30 = rot_cw(30)
E30 = pivot_compose(*LIN30)
LIN270 = rot_cw(270)
E270 = pivot_compose(*LIN270)

# name, matrix, origin, alignment, note
PANELS = [
    ("P1 cw90 L, o0+C", m4(*LIN90, 0, 0), "(0,0)", "CENTER"),
    ("P2 cw90 M, o0+C", m4(*LIN90, *E90), "(0,0)", "CENTER"),
    ("P3 cw270 L, o0+C", m4(*LIN270, 0, 0), "(0,0)", "CENTER"),
    ("P4 mirH L, o0+C", m4(-1, 0, 0, 1, 0, 0), "(0,0)", "CENTER"),
    ("P5 mirH M, o0+C", m4(-1, 0, 0, 1, 120, 0), "(0,0)", "CENTER"),
    ("P6 cw30 L, o0+C", m4(*LIN30, 0, 0), "(0,0)", "CENTER"),
    ("P7 cw30 M, o0+C", m4(*LIN30, *E30), "(0,0)", "CENTER"),
    ("P8 cw90 L, no orig", m4(*LIN90, 0, 0), None, "CENTER"),
]

lines = []
for n, mx, o, a in PANELS:
    lines.append("%s | origin=%s alignment=%s | %s" % (n, o, a, mx))
notes = "\n".join(lines)
print(notes)
with open(os.path.join(TMP, "probe1-variants.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(notes + "\n")

W, H = 1180, 780
COLS_N, PITCH_X, PITCH_Y = 4, 280, 330
kids = [D.text_el("probe1: frame = untransformed 120x120, cross = pivot(60,60); "
                  "L = linear only, M = pivot-composed",
                  x=30, y=20, size=20, color="#0F172AFF")]
for i, (name, mx, org, al) in enumerate(PANELS):
    cxp = 30 + (i % COLS_N) * PITCH_X
    cyp = 70 + (i // COLS_N) * PITCH_Y
    ox, oy = cxp + 70, cyp + 30
    ta = {"matrix": mx, "alignment": al}
    if org is not None:
        ta["origin"] = org
    kids.append(D.box(cxp - 8, cyp - 8, PITCH_X - 8, 268, color="#F8FAFCFF",
                      border="1 SOLID #E2E8F0FF", radius=10))
    kids.append(D.box(ox - 6, oy - 6, 132, 132, border="1 SOLID #CBD5E1FF"))
    kids.append(D.box(ox + 59, oy, 2, 120, color="#94A3B8FF"))
    kids.append(D.box(ox, oy + 59, 120, 2, color="#94A3B8FF"))
    inner = D.stack(stamp_kids(), 120, 120)
    kids.append(D.el("Positioned", {"left": ox, "top": oy, "width": 120, "height": 120},
                      [D.el("Transform", ta, [inner])]))
    kids.append(D.text_el(name, x=cxp, y=oy + 150, w=PITCH_X - 16, size=20,
                           color="#0F172AFF", font=D.MONO))
    kids.append(D.text_alike if False else D.text_el(
        "org=%s al=%s" % (org, al), x=cxp, y=oy + 178, w=PITCH_X - 16, size=20,
        color="#475569FF", font=D.MONO))

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#FFFFFFFF")
drafts = os.path.join(TMP, "drafts")
os.makedirs(drafts, exist_ok=True)
with open(os.path.join(drafts, "v01-probe1.snapshot"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
r = snapkit.render(dsl, "probe1.png", "probe1.snapshot", final=False)
print("render:", r)
for w in D.warnings():
    print("WARN", w)