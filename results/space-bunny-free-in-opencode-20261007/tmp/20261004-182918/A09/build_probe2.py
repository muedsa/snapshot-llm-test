# -*- coding: utf-8 -*-
"""A09 probe 2: can the DSL apply the FULL pivot-composed matrix (i.e. is the
pivot the child top-left instead of the center)?  Plus a Stack clipBehaviour check."""
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

st = json.load(open(os.path.join(ROOT, "tasks", "A09-transform-atlas",
                                  "inputs", "stamp.json"), encoding="utf-8"))
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


th = math.radians(90)
LIN = (math.cos(th), math.sin(th), -math.sin(th), math.cos(th))
E = (120.0, 0.0)
MATS = {
    "L": m4(*LIN, 0, 0),
    "M": m4(*LIN, *E),
}

# name, matrix key, alignment, origin, clip
PANELS = [
    ("Q1 al=(0,0) M", "M", "(0,0)", "(0,0)", None),
    ("Q2 al=(0,0) L", "L", "(0,0)", "(0,0)", None),
    ("Q3 al=TOP_LEFT M", "M", "TOP_LEFT", None, None),
    ("Q4 al=TOP_LEFT L", "L", "TOP_LEFT", None, None),
    ("Q5 al=CENTER M", "M", "CENTER", None, None),
    ("Q6 al=(0,0) L o60", "L", "(0,0)", "(60,60)", None),
    ("Q7 al omitted L", "L", None, None, None),
    ("Q8 al omitted M", "M", None, None, None),
]

W, H = 1180, 780
COLS_N, PITCH_X, PITCH_Y = 4, 280, 330
kids = [D.text_el("probe2: M = pivot-composed matrix (e=120), L = linear only; "
                  "want: transform applied about the child top-left so M is the true composite",
                  x=30, y=20, size=20, color="#0F172AFF")]
for i, (name, mk, al, org, _clip) in enumerate(PANELS):
    cxp = 30 + (i % COLS_N) * PITCH_X
    cyp = 70 + (i // COLS_N) * PITCH_Y
    ox, oy = cxp + 70, cyp + 30
    ta = {"matrix": MATS[mk]}
    if al is not None:
        ta["alignment"] = al
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
    kids.append(D.text_el("al=%s org=%s" % (al, org), x=cxp, y=oy + 178, w=PITCH_X - 16,
                           size=20, color="#475569FF", font=D.MONO))

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#FFFFFFFF")
drafts = os.path.join(TMP, "drafts")
os.makedirs(drafts, exist_ok=True)
with open(os.path.join(drafts, "v02-probe2.snapshot"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
r = snapkit.render(dsl, "probe2.png", "probe2.snapshot", final=False)
print("render:", r)
for w in D.warnings():
    print("WARN", w)