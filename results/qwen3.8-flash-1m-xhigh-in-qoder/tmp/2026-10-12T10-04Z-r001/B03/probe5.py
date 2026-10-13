"""B03 probe round 5: why did Opacity render at full alpha next to a BackdropFilter?

probe2-filter2 asked for `Opacity opacity="0.35"` and the pixels came back fully opaque
(230,57,70), while probe4-opacity with the same DSL line blended correctly (246,185,189).
The only difference was a later BackdropFilter sibling, so these three canvases add one
variable at a time.

Run: python tmp/<run_id>/B03/probe5.py
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


def emit(name, body, bg="#F2F2F2", w=460, h=170):
    (TMP / f"probe5-{name}.snapshot").write_text(
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


OPAQUE = lambda: pos(Node("Opacity", {"opacity": "0.35"},  # noqa: E731
                          [C(width="150", height="60", color="#E63946", borderRadius="8")]),
                     20, 40)
CHECK = lambda: pos(Text("check", fontSize="14", color="#555"), 200, 44, w=100)  # noqa: E731

emit("a-plain", [OPAQUE(), CHECK()])

emit("b-backdrop", [OPAQUE(), CHECK(),
                    pos(Node("BackdropFilter", {"sigmaX": "8", "sigmaY": "8"},
                             [C(width="120", height="60", color="#00000000")]), 300, 40)])

emit("c-clipped-backdrop", [OPAQUE(), CHECK(),
                             pos(Node("ClipRRect",
                                       {"borderRadius": "6", "clipBehavior": "ANTI_ALIAS"},
                                       [Node("BackdropFilter", {"sigmaX": "8", "sigmaY": "8"},
                                             [C(width="120", height="60",
                                                color="#00000000")])]), 300, 40)])

emit("d-colorfiltered", [OPAQUE(), CHECK(),
                         pos(Node("ColorFiltered", {"color": "#0B3954",
                                                    "blendMode": "MULTIPLY"},
                                 [C(width="120", height="60", color="#FFFFFF")]), 300, 40)])

emit("e-imagefiltered", [OPAQUE(), CHECK(),
                         pos(Node("ImageFiltered", {"sigmaX": "4", "sigmaY": "4"},
                                  [C(width="120", height="60", color="#1D3557")]), 300, 40)])

# does an unclipped BackdropFilter touch the whole canvas?
checks = [pos(C(width="26", height="26", color=c), 20 + 34 * i, 20)
          for i, c in enumerate(("#E63946", "#F4A261", "#E9C46A", "#2A9D8F", "#457B9D"))]
emit("f-wholecanvas", checks + [pos(Node("ClipRRect", {"borderRadius": "0",
                                                       "clipBehavior": "HARD_EDGE"},
                                        [Node("BackdropFilter",
                                              {"sigmaX": "0", "sigmaY": "0",
                                               "blendMode": "MODULATE"},
                                              [C(width="60", height="60",
                                                 color="#00000000")])]), 200, 20)],
     h=90)
