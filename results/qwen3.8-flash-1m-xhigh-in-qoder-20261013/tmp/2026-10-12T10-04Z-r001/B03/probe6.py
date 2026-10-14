"""B03 probe round 6: bisect the probe2-filter2 canvas that made Opacity look opaque.

probe5 showed Opacity 0.35 blends correctly beside BackdropFilter, ColorFiltered and
ImageFiltered siblings, so the anomaly in probe2-filter2 must come from the combination.
Two slices of that canvas, one request each.

Run: python tmp/<run_id>/B03/probe6.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from snap import C, Node, Positioned, Snapshot, Stack, Text  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"


def emit(name, body, w=480, h=380, bg="#F2F2F2"):
    (TMP / f"probe6-{name}.snapshot").write_text(
        Snapshot(Stack(C(width=str(w), height=str(h), color=bg), *body),
                 background=bg, type="png").render() + "\n", encoding="utf-8")
    print("wrote", name)


def pos(child, x, y, w=None, h=None):
    a = {"left": str(x), "top": str(y)}
    if w is not None:
        a["width"] = str(w)
    if h is not None:
        a["height"] = str(h)
    return Positioned(child, **a)


row_cf_text = pos(Node("ColorFiltered", {"color": "#FF5500", "blendMode": "SRC_ATOP"},
                      [Text("COLOURISE", fontSize="42", color="#111111")]),
                  20, 20, w=300, h=70)
row_cf_mul = pos(Node("ColorFiltered", {"color": "#0B395488", "blendMode": "MULTIPLY"},
                      [Text("MULTIPLY", fontSize="42", color="#FFFFFF")]),
                 20, 110, w=300, h=70)
row_imgf = pos(Node("ImageFiltered", {"sigmaX": "4", "sigmaY": "4"},
                    [Text("BLURRED SUBTREE", fontSize="34", color="#111111")]),
               20, 200, w=340, h=60)
row_op = pos(Node("Opacity", {"opacity": "0.35"},
                  [C(width="150", height="60", color="#E63946", borderRadius="8")]),
             20, 280)
row_bd = pos(Node("BackdropFilter", {"sigmaX": "8", "sigmaY": "8",
                                     "blendMode": "SRC_OVER"},
                  [C(width="150", height="60", color="#00000000")]), 300, 280)

# only the two bottom rows of the original canvas
emit("bottom-only", [row_op, row_bd])
# full original, backdrop row replaced by a clipped one
emit("clipped-backdrop", [row_cf_text, row_cf_mul, row_imgf, row_op,
                          pos(Node("ClipRRect",
                                    {"borderRadius": "0", "clipBehavior": "ANTI_ALIAS"},
                                    [Node("BackdropFilter",
                                          {"sigmaX": "8", "sigmaY": "8"},
                                          [C(width="150", height="60",
                                             color="#00000000")])]), 300, 280)])
# full original verbatim, as a control
emit("control", [row_cf_text, row_cf_mul, row_imgf, row_op, row_bd])
