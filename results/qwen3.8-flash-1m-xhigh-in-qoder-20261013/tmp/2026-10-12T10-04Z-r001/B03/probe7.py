"""B03 probe round 7: is it the explicit `blendMode` on BackdropFilter that flattens alpha?

probe6 narrowed the anomaly to one variable: the same Opacity card renders 0.35 next to a
BackdropFilter that omits `blendMode`, but turns fully opaque when `blendMode="SRC_OVER"`
is written out explicitly. Three canvases, identical except for the clip and the attribute.

Run: python tmp/<run_id>/B03/probe7.py
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
SHEET = "#F2F2F2"


def pos(child, x, y, w=None, h=None):
    a = {"left": str(x), "top": str(y)}
    if w is not None:
        a["width"] = str(w)
    if h is not None:
        a["height"] = str(h)
    return Positioned(child, **a)


def backdrop(sigma, blend=None, clip=None):
    bd = Node("BackdropFilter",
              {"sigmaX": str(sigma), "sigmaY": str(sigma), "blendMode": blend},
              [C(width="150", height="60", color="#00000000")])
    if clip:
        bd = Node("ClipRRect", {"borderRadius": "0", "clipBehavior": clip}, [bd])
    return bd


def canvas(name, blend, clip):
    body = [
        C(width="460", height="180", color=SHEET),
        pos(Node("Opacity", {"opacity": "0.35"},
                [C(width="150", height="60", color="#E63946", borderRadius="8")]), 20, 60),
        pos(C(width="150", height="40", color="#1D3557", borderRadius="8"), 20, 130),
        pos(backdrop(8, blend, clip), 290, 60),
    ]
    (TMP / f"probe7-{name}.snapshot").write_text(
        Snapshot(Stack(*body), background=SHEET, type="png").render() + "\n",
        encoding="utf-8")
    print("wrote", name)


canvas("no-blend-no-clip", None, None)
canvas("blend-no-clip", "SRC_OVER", None)
canvas("blend-clip", "SRC_OVER", "ANTI_ALIAS")
