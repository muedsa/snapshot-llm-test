"""B03 probe round 8 (last probing round): the four questions still open.

Run: python tmp/<run_id>/B03/probe8.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from snap import C, Emoji, Node, Positioned, Snapshot, Stack, Text  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"
PNG_1PX = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQD"
           "wAEhAGAh3LpJgAAAAAASUVORK5CYII=")


def emit(name, body, w, h, bg="#FFFFFF"):
    (TMP / f"probe8-{name}.snapshot").write_text(
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


# a) does Raw inherit fontSize, or must the span carry its own style?
emit("rawstyle", [
    pos(Text([Text("A", fontSize="30", color="#111111"),
              Node("Raw", {}, None, "  b  "),
              Text("C", fontSize="30", color="#111111")]), 20, 20),
    pos(Text([Text("A", fontSize="30", color="#111111"),
              Node("Raw", {"fontSize": "30", "color": "#111111"}, None, "  b  "),
              Text("C", fontSize="30", color="#111111")]), 20, 70),
    pos(Text([Text("A", fontSize="30", color="#111111"),
              Text("  b  ", fontSize="30", color="#111111"),
              Text("C", fontSize="30", color="#111111")]), 20, 120),
], 400, 170)

# b) inline pictogram from a data URI, and Emoji as a standalone widget
emit("emoji", [
    pos(Text([Text("inline ", fontSize="28", color="#111111"),
              Emoji(dataUri=PNG_1PX, width="28", height="28", alignment="MIDDLE"),
              Text(" end", fontSize="28", color="#111111")]), 20, 20),
    pos(Node("ClipRRect", {"borderRadius": "0"},
             [Emoji(dataUri=PNG_1PX, width="60", height="60")]),
        20, 70),
    pos(Text("two data-uri pngs above (1px red, scaled)", fontSize="14", color="#666"),
        20, 150, w=360),
], 400, 180)

# c) gradientRotation with no begin/end, and with them
for i, extra in enumerate(({}, {"gradientBegin": "TOP_LEFT", "gradientEnd": "TOP_RIGHT"})):
    attrs = {"width": "150", "height": "150", "gradientType": "LINEAR",
             "gradientColors": "#111111,#FFFFFF", "gradientRotation": "1.5708",
             "borderRadius": "4", **extra}
    emit(f"rot{i}", [pos(C(**attrs), 20, 20)], 200, 200)

# d) shape=CIRCLE alone, and overflow modes on a too-small box
emit("shapeoverflow", [
    pos(C(width="120", height="120", color="#2A9D8F", shape="CIRCLE"), 20, 20),
    pos(C(width="120", height="60", color="#E76F51", shape="CIRCLE"), 160, 20),
    pos(Text("CLIP default", fontSize="16", color="#111111", overflow="CLIP"),
        20, 160, w=90),
    pos(Text("FADE mode", fontSize="16", color="#111111", overflow="FADE"), 20, 190, w=90),
    pos(Text("VISIBLE mode", fontSize="16", color="#111111", overflow="VISIBLE"),
        160, 160, w=90),
    pos(Text("strut enabled text", fontSize="16", color="#111111", strutEnabled="true",
             strutFontSize="40", strutHeight="1.5"), 300, 160, w=120),
], 460, 260)
