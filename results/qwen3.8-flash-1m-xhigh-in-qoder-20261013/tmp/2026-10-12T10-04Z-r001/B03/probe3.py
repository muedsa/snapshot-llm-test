"""B03 probe round 3: isolate undocumented value formats, one request per variant.

Round 2 returned two PARSE_ERRORs (Transform `origin="30,30"`, decorationLineStyle
"DOUBLED"), so each candidate spelling gets its own request: a 400 names one attribute
without hiding the rest of the canvas.

Run: python tmp/<run_id>/B03/probe3.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from snap import C, Node, Positioned, Snapshot, Stack, Text, Transform  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"


def emit(name, w, h, body, bg="#FFFFFF"):
    # the Stack needs one non-positioned sized child: Positioned children alone give
    # "Layout size is infinite" (400 RENDER_ERROR), confirmed by request B03-misc
    (TMP / f"probe3-{name}.snapshot").write_text(
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


def mat(a, b, c, d, tx=0.0, ty=0.0):
    return f"({a},{b},0,0,{c},{d},0,0,0,0,1,0,{tx},{ty},0,1)"


# --- Transform origin spellings ---------------------------------------------------
for i, spec in enumerate(["30 30", "(30,30)", "30,30"]):
    card = Transform(C(width="60", height="60", color="#E63946", borderRadius="6"),
                     matrix=mat(0.866, 0.5, -0.5, 0.866, 0, 0), origin=spec)
    emit(f"origin{i}", 200, 200, [pos(card, 60, 60),
                                  pos(Text(repr(spec), fontSize="14", color="#555"),
                                       60, 160, w=130)])

# --- decorationLineStyle spellings -----------------------------------------------
for style in ["SOLID", "DOTTED", "DASHED", "DOUBLE", "WAVY", "DOUBLE_SOLID"]:
    t = Text(f"decoration {style}", fontSize="26", color="#111111",
             decoration="UNDERLINE", decorationLineStyle=style, decorationColor="#E63946")
    emit(f"deco-{style}", 360, 70, [pos(t, 16, 20)])

# --- misc formats used by the B03 works ------------------------------------------
emit("misc", 620, 470, [
    pos(Text("maxLines 1 + ELLIPSIS", fontSize="22", color="#111111", maxLines="1",
             overflow="ELLIPSIS"), 16, 16, w=200),
    pos(Text("textAlign END inside 300", fontSize="22", color="#111111",
             textAlign="END"), 16, 60, w=300),
    pos(Text("fontFeatures on CJK 一二三四五六七八九十", fontSize="22", color="#111111",
             fontFeatures="tnum"), 16, 104, w=420),
    pos(Node("ClipPath", {"path": "M 20 20 L 180 20 A 80 80 0 0 1 180 120 L 20 120 Z"},
             [C(width="200", height="140", gradientType="LINEAR",
                gradientColors="#111111,#E63946", gradientBegin="TOP_LEFT",
                gradientEnd="BOTTOM_RIGHT")]), 16, 150),
    pos(Node("ClipPath", {"path": "M 0 0 L 200 0 L 200 140 L 0 140 Z "
                                  "M 60 40 L 60 100 L 140 100 L 140 40 Z"},
             [C(width="200", height="140", color="#2A9D8F")]), 240, 150),
    pos(C(width="180", height="60", color="#FEE440", borderRadius="8",
          boxShadow="6 8 14 #00000066"), 470, 150),
    pos(Text("custom shadow", fontSize="14", color="#555"), 470, 220, w=170),
    pos(C(width="180", height="60", gradientType="LINEAR", gradientColors="#111,#888",
          gradientRotation="0.7854", borderRadius="8"), 16, 320),
    pos(Text("gradientRotation 0.7854", fontSize="14", color="#555"), 16, 386, w=200),
    pos(C(width="180", height="60", gradientType="RADIAL", gradientColors="#111,#888",
          gradientRotation="0.7854", borderRadius="8"), 220, 320),
    pos(Text("RADIAL + gradientRotation", fontSize="14", color="#555"), 220, 386, w=200),
    pos(C(width="180", height="60", color="#FFFFFF", borderRadius="8",
          foregroundGradientType="LINEAR",
          foregroundGradientColors="#E63946,#0B3954"), 420, 320),
    pos(Text("foregroundGradient on Container", fontSize="14", color="#555"),
        420, 386, w=200),
    pos(Text([Text("normal ", fontSize="20", color="#111111"),
              Node("WidgetSpan", {"alignment": "BASELINE", "baseline": "ALPHABETIC"},
                   [C(width="18", height="18", color="#E63946", borderRadius="4")]),
              Text("baseline span", fontSize="20", color="#111111")]), 16, 420),
])
