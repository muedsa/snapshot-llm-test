"""A19 - the two occlusion versions.

Both files are built by the same function with one argument swapped, so the canvas, the
background, the visible objects, the occluder and every rendering parameter are
literally the same nodes. What differs is only the layer painted *under* the occluder:
version A hides three objects, version B hides five different ones. Every hidden shape
keeps at least 24 px inside the occluder and carries no shadow or filter, so nothing it
paints can leak past the covering panel - which is exactly what equivalence.py then
proves on pixels.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from snap import C, Container, Node, Positioned, Snapshot, Stack, num  # noqa: E402

W = H = 800
BG = "#FFFFFF"
PANEL = "#EDF1F7"
OCC = "#16233A"
COL = {"blue": "#2B5BD7", "orange": "#E0913B", "green": "#1F8A5F", "violet": "#7A4FD3"}
MONO = "Noto Sans Mono CJK SC"
LABEL = "#33404F"

# the covering panel: [left, top, right, bottom]
OCCLUDER = [296, 296, 552, 552]

# objects that stay visible in both versions: id, colour, shape, size, centre
VISIBLE = [
    ("V01", "blue", "circle", 80, (120, 120)),
    ("V02", "orange", "square", 64, (400, 120)),
    ("V03", "green", "rounded-square", 48, (680, 120)),
    ("V04", "violet", "ring", 80, (120, 400)),
    ("V05", "orange", "circle", 48, (680, 400)),
    ("V06", "blue", "square", 80, (120, 680)),
    ("V07", "green", "circle", 64, (400, 680)),
    ("V08", "violet", "rounded-square", 80, (680, 680)),
]

# hidden layers - only these differ between the two delivered files
HIDDEN_A = [
    ("H_A1", "blue", "square", 64, (360, 360)),
    ("H_A2", "green", "circle", 64, (480, 420)),
    ("H_A3", "orange", "ring", 64, (360, 480)),
]
HIDDEN_B = [
    ("H_B1", "violet", "circle", 64, (352, 352)),
    ("H_B2", "orange", "rounded-square", 64, (456, 352)),
    ("H_B3", "blue", "ring", 64, (352, 456)),
    ("H_B4", "green", "square", 64, (456, 456)),
    ("H_B5", "violet", "circle", 48, (404, 404)),
]


def subject(shape, colour, size):
    hexc = COL[colour]
    if shape == "circle":
        return C(width=num(size), height=num(size), color=hexc, shape="CIRCLE")
    if shape == "square":
        return C(width=num(size), height=num(size), color=hexc)
    if shape == "rounded-square":
        return C(width=num(size), height=num(size), color=hexc,
                 borderRadius=num(size * 0.25))
    return Stack(C(width=num(size), height=num(size), color=hexc, shape="CIRCLE"),
                 C(width=num(size / 2), height=num(size / 2), color=OCC,
                   shape="CIRCLE"),
                 alignment="CENTER", clipBehavior="NONE")


def place(o, hole_colour=None):
    oid, colour, shape, size, (cx, cy) = o
    node = subject(shape, colour, size)
    if shape == "ring" and hole_colour is not None:
        node = Stack(C(width=num(size), height=num(size), color=colour and COL[colour],
                       shape="CIRCLE"),
                     C(width=num(size / 2), height=num(size / 2), color=hole_colour,
                       shape="CIRCLE"),
                     alignment="CENTER", clipBehavior="NONE")
    return Positioned(node, left=num(cx - size / 2), top=num(cy - size / 2))


def build(hidden):
    l, t, r, b = OCCLUDER
    els = [
        C(width=num(W), height=num(H), color=BG),
        Positioned(C(width=num(W - 80), height=num(H - 80), color=PANEL,
                     borderRadius="24"), left="40", top="40"),
    ]
    els += [place(o, hole_colour=PANEL) for o in VISIBLE]
    els.append(Positioned(Node("Text", {"fontSize": "26", "color": LABEL,
                                        "fontFamily": MONO}, [], "OCCLUDED REGION"),
                          left="300", top="252"))
    hidden_nodes = [place(o) for o in hidden]
    occluder = Positioned(C(width=num(r - l), height=num(b - t), color=OCC,
                            borderRadius="18"), left=num(l), top=num(t))
    kids = els + hidden_nodes + [occluder]
    return Snapshot(Node("Stack", {"alignment": "TOP_LEFT", "clipBehavior": "HARD_EDGE"},
                         [C(width=num(W), height=num(H))] + kids),
                    background=BG, type="png")


def margins(hidden):
    """How far each hidden object stays inside the occluder (must be > 0)."""
    l, t, r, b = OCCLUDER
    out = []
    for oid, _, _, size, (cx, cy) in hidden:
        out.append({"id": oid, "size_px": size,
                    "box": [cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2],
                    "inset_px": [round(cx - size / 2 - l, 1),
                                 round(cy - size / 2 - t, 1),
                                 round(r - (cx + size / 2), 1),
                                 round(b - (cy + size / 2), 1)]})
    return out


ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
a = ap.parse_args()
TMP = ROOT / "tmp" / RUN / "A19"
for name, hid in (("occlusion", HIDDEN_A), ("occlusion-alternative", HIDDEN_B)):
    (TMP / f"{a.ver}-{name}.snapshot").write_text(build(hid).render() + "\n",
                                                  encoding="utf-8")
info = {
    "occluder_box": OCCLUDER,
    "visible_objects": [{"id": v[0], "colour": v[1], "shape": v[2], "size_px": v[3],
                         "centre": list(v[4])} for v in VISIBLE],
    "hidden_A": [{"id": v[0], "colour": v[1], "shape": v[2], "size_px": v[3],
                  "centre": list(v[4])} for v in HIDDEN_A],
    "hidden_B": [{"id": v[0], "colour": v[1], "shape": v[2], "size_px": v[3],
                  "centre": list(v[4])} for v in HIDDEN_B],
    "hidden_A_insets": margins(HIDDEN_A),
    "hidden_B_insets": margins(HIDDEN_B),
}
(TMP / f"{a.ver}-occlusion.json").write_text(
    json.dumps(info, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps({"min_inset_A": min(min(m["inset_px"]) for m in margins(HIDDEN_A)),
                  "min_inset_B": min(min(m["inset_px"]) for m in margins(HIDDEN_B))},
                 ensure_ascii=False))
