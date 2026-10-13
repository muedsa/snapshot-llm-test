"""B03 probe round 4: settle the six things rounds 2-3 could not decide.

Each canvas is built for measurement, not for looks: paired rows share a font, spacing and
origin so a single attribute is the only variable.

Run: python tmp/<run_id>/B03/probe4.py   (from the suite task root)
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


def emit(name, w, h, body, bg="#FFFFFF"):
    (TMP / f"probe4-{name}.snapshot").write_text(
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


# 1. Opacity A/B, same card, nothing else on top
emit("opacity", 420, 120, [
    pos(C(width="180", height="60", color="#E63946", borderRadius="8"), 20, 30),
    pos(Node("Opacity", {"opacity": "0.35"},
            [C(width="180", height="60", color="#E63946", borderRadius="8")]), 220, 30),
    pos(Text("opacity 1 / 0.35", fontSize="14", color="#555"), 20, 100, w=200),
])

# 2. `height` on wrapped copy: same text, same width, only the line multiplier differs
WRAP = "the measured text model wraps this copy into several lines of equal width"
emit("lineheight", 520, 300, [
    pos(Text(WRAP, fontSize="22", color="#111111", height="1.0"), 20, 20, w=220),
    pos(Text(WRAP, fontSize="22", color="#111111", height="2.4"), 280, 20, w=220),
    pos(Text("height 1.0", fontSize="14", color="#555"), 20, 260, w=200),
    pos(Text("height 2.4", fontSize="14", color="#555"), 280, 260, w=200),
])

# 3. Raw keeps spaces that plain Text trims
emit("rawspan", 520, 130, [
    pos(Text([Text("|", fontSize="26", color="#111111"),
              Text("   spaced   ", fontSize="26", color="#111111"),
              Text("|", fontSize="26", color="#111111")]), 20, 20),
    pos(Text([Text("|", fontSize="26", color="#111111"),
              Node("Raw", {}, None, "   spaced   "),
              Text("|", fontSize="26", color="#111111")]), 20, 70),
])

# 4. custom boxShadow: a card with no text anywhere near the measured scan
emit("shadowscan", 320, 320, [
    pos(C(width="200", height="70", color="#FFFFFF", borderRadius="10",
          boxShadow="6 8 14 #00000066"), 60, 40),
    pos(C(width="200", height="70", color="#FFFFFF", borderRadius="10",
          boxShadow="ELEVATION_6"), 60, 190),
])

# 5. RADIAL tile modes: small radius so the period is visible inside the box
for i, mode in enumerate(("CLAMP", "REPEAT", "MIRROR", "DECAL")):
    emit(f"radialtile{mode}", 200, 200, [
        pos(C(width="180", height="180", gradientType="RADIAL",
              gradientColors="#111111,#EEEEEE", gradientCenter="CENTER",
              gradientRadius="0.18", gradientTileMode=mode), 10, 10),
    ], bg="#FFFFFF")

# 6. dotted vs dashed runs, and WidgetSpan BASELINE next to descenders
emit("decorun", 620, 150, [
    pos(Text("dotted line style sample", fontSize="24", color="#111111",
             decoration="UNDERLINE", decorationLineStyle="DOTTED",
             decorationColor="#E63946"), 20, 20, w=560),
    pos(Text("dashed line style sample", fontSize="24", color="#111111",
             decoration="UNDERLINE", decorationLineStyle="DASHED",
             decorationColor="#E63946"), 20, 60, w=560),
    pos(Text([Text("gjp qty ", fontSize="34", color="#111111"),
              Node("WidgetSpan", {"alignment": "BASELINE", "baseline": "ALPHABETIC"},
                   [C(width="20", height="20", color="#E63946")]),
              Text(" tail", fontSize="34", color="#111111")]), 20, 100),
])

# 7. small caps: same string twice, only fontFeatures differs
emit("smallcaps", 420, 120, [
    pos(Text("Handy Ampersand abcdefg", fontSize="30", color="#111111"), 20, 20),
    pos(Text("Handy Ampersand abcdefg", fontSize="30", color="#111111",
             fontFeatures="smcp"), 20, 70),
])
