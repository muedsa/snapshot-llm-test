"""B03 capability probes - what does the service actually do with the frontier tags?

Each probe is a small canvas that isolates one documented capability, so technique-notes.md
can state "confirmed by request <id>" instead of "the docs say". Nothing here is a deliverable.

Run:  python tmp/<run_id>/B03/probe.py <which>
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from snap import C, Container, Node, Positioned, Snapshot, Stack, Text, Transform  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"


def dsl(body, w, h, bg="#FFFFFF"):
    return Snapshot(Stack(C(width=str(w), height=str(h), color=bg), *body),
                    background=bg, type="png").render() + "\n"


def pos(child, x, y, w=None, h=None):
    a = {"left": str(x), "top": str(y)}
    if w is not None:
        a["width"] = str(w)
    if h is not None:
        a["height"] = str(h)
    return Positioned(child, **a)


def p_blur():
    """BackdropFilter inside ClipRRect over a striped background: does it really blur?"""
    bg = [pos(C(width="420", height="60", color="#E63946"), 0, 40 * i) for i in range(7)]
    bg += [pos(C(width="60", height="300", color="#1D3557"), 60 * i, 20) for i in range(7)]
    glass = Node("BackdropFilter", {"sigmaX": "9", "sigmaY": "9"},
                 [C(width="240", height="120", color="#FFFFFF88", borderRadius="18")])
    clipped = Node("ClipRRect", {"borderRadius": "18", "clipBehavior": "ANTI_ALIAS"},
                   [glass])
    return dsl(bg + [pos(clipped, 90, 90),
                     pos(Text("frosted?", fontSize="26", color="#111"), 120, 220, w=200)],
               420, 300), "blur"


def p_sweep():
    """SWEEP gradient with angles, stops and rotation."""
    a = C(width="180", height="180", borderRadius="90", gradientType="SWEEP",
          gradientColors="#0B3954,#FF5522,#FFD166,#0B3954",
          gradientStartAngle="0", gradientEndAngle="6.283", gradientCenter="CENTER")
    b = C(width="180", height="180", gradientType="SWEEP",
          gradientColors="#111,#EEE", gradientStartAngle="1.57", gradientEndAngle="4.71",
          borderRadius="12")
    return dsl([pos(a, 20, 20), pos(b, 220, 20),
                pos(Text("sweep", fontSize="20", color="#111"), 20, 216, w=180)],
               420, 250), "sweep"


def p_blend():
    """ColorFiltered MULTIPLY + backgroundBlendMode + foregroundGradient."""
    base = C(width="180", height="180", gradientType="LINEAR",
             gradientColors="#FFFFFF,#4CC9F0", borderRadius="12")
    over = Node("ColorFiltered", {"color": "#FF005588", "blendMode": "MULTIPLY"},
                [C(width="180", height="180", color="#FFFFFF", borderRadius="12")])
    fg = C(width="180", height="180", color="#FEE440", borderRadius="12",
           foregroundGradientType="LINEAR", foregroundGradientColors="#00000000,#00000088",
           backgroundBlendMode="MULTIPLY")
    return dsl([pos(base, 20, 20), pos(over, 220, 20), pos(fg, 20, 220),
                pos(Text("blend / foreground / bgBlend", fontSize="20", color="#111"),
                    220, 240, w=200)], 420, 420), "blend"


def p_textfx():
    """fontFeatures, letterSpacing, textShadow, nested Text spans, WidgetSpan."""
    t1 = Text("TABULAR 0123456789", fontSize="24", color="#111", fontFeatures="tnum",
              letterSpacing="2")
    t2 = Text("SMALLCAPS abcdefg", fontSize="24", color="#111", fontFeatures="smcp")
    t3 = Text("shadow", fontSize="34", color="#111", textShadow="3 4 1.5 #E5393588")
    t4 = Node("Text", {}, [Text("rich ", fontSize="24", color="#111"),
                           Text("red", fontSize="24", color="#C62828", fontStyle="BOLD"),
                           Text(" span", fontSize="24", color="#111")])
    body = [pos(t1, 20, 20), pos(t2, 20, 60), pos(t3, 20, 100), pos(t4, 20, 160)]
    try:
        ws = Node("Text", {}, [Text("inline box: ", fontSize="24", color="#111"),
                               Node("WidgetSpan", {"alignment": "MIDDLE"},
                                    [C(width="26", height="26", color="#2A9D8F",
                                       borderRadius="6")])])
        body.append(pos(ws, 20, 200))
    except Exception as exc:                                    # pragma: no cover
        body.append(pos(Text(f"widgetspan failed {exc}", fontSize="20", color="#C62828"),
                        20, 200))
    return dsl(body, 460, 260), "textfx"


def p_transform():
    """Transform matrix around Text (rotate) and around a Container (skew-ish)."""
    import math
    th = math.radians(-20)
    m = (f"({math.cos(th):.4f},{math.sin(th):.4f},0,0,"
         f"{-math.sin(th):.4f},{math.cos(th):.4f},0,0,0,0,1,0,0,0,0,1)")
    rot = Transform(Text("ROTATED TEXT", fontSize="28", color="#111"), matrix=m,
                    alignment="CENTER")
    th2 = math.radians(12)
    m2 = (f"(1,{math.tan(th2):.4f},0,0,0,1,0,0,0,0,1,0,0,0,0,1)")   # x-skew
    skew = Transform(C(width="150", height="60", color="#E76F51", borderRadius="8"),
                     matrix=m2, alignment="CENTER")
    return dsl([pos(rot, 40, 30, w=300, h=60), pos(skew, 60, 150, w=150, h=60)],
               420, 260), "transform"


def p_tile():
    """gradientTileMode REPEAT / MIRROR with tight stops: stripe and twill patterns."""
    rep = C(width="180", height="180", gradientType="LINEAR",
            gradientColors="#1D3557,#E63946", gradientStops="0,0.5",
            gradientTileMode="REPEAT", gradientBegin="TOP_LEFT", gradientEnd="BOTTOM_RIGHT")
    mir = C(width="180", height="180", gradientType="LINEAR",
            gradientColors="#1D3557,#E63946", gradientStops="0,0.5",
            gradientTileMode="MIRROR", gradientBegin="TOP_LEFT", gradientEnd="BOTTOM_RIGHT")
    rad = C(width="180", height="180", gradientType="RADIAL",
            gradientColors="#111,#FFF", gradientStops="0,0.14", gradientTileMode="REPEAT",
            gradientRadius="0.2")
    return dsl([pos(rep, 20, 20), pos(mir, 220, 20), pos(rad, 20, 220),
                pos(Text("REPEAT / MIRROR / radial repeat", fontSize="20", color="#111"),
                    220, 260, w=200)], 420, 420), "tile"


def p_clipstack():
    """ClipPath wrapping a Stack of several children (composite mask), and nesting."""
    inner = Stack(*[C(width="300", height="30", color=col) for col in
                    ("#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51")])
    stripes = ("#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51")
    wrapped = Node("Stack", {}, [pos(C(width="300", height="30", color=col), 0, 30 * i)
                                 for i, col in enumerate(stripes)])
    clip = Node("ClipPath", {"path": "M 0 0 L 300 0 L 300 150 Q 150 200 0 150 Z"},
                [wrapped])
    nest = Node("ClipPath", {"path": "M 0 0 L 300 0 L 300 150 Q 150 200 0 150 Z"},
                [Node("ClipRRect", {"borderRadius": "20", "clipBehavior": "ANTI_ALIAS"},
                      [C(width="300", height="200", color="#8AB17D")])])
    return dsl([pos(clip, 20, 20, w=300, h=200), pos(nest, 20, 240, w=300, h=200),
                pos(inner, 340, 20)], 660, 460), "clipstack"


def p_shadow():
    """boxShadow elevation names, including on rotated children."""
    import math
    th = math.radians(-14)
    m = (f"({math.cos(th):.4f},{math.sin(th):.4f},0,0,"
         f"{-math.sin(th):.4f},{math.cos(th):.4f},0,0,0,0,1,0,0,0,0,1)")
    cards = []
    for i, e in enumerate(("ELEVATION_2", "ELEVATION_8", "ELEVATION_24")):
        cards.append(pos(C(width="220", height="70", color="#FFFFFF", borderRadius="12",
                           boxShadow=e), 30, 30 + i * 96))
    cards.append(pos(Transform(C(width="220", height="70", color="#FFF", borderRadius="12",
                                 boxShadow="ELEVATION_16"), matrix=m, alignment="CENTER"),
                     30, 320, w=220, h=70))
    return dsl(cards, 300, 420, bg="#E9ECEF"), "shadow"


PROBES = {"blur": p_blur, "sweep": p_sweep, "blend": p_blend, "textfx": p_textfx,
          "transform": p_transform, "tile": p_tile, "clipstack": p_clipstack,
          "shadow": p_shadow}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn in PROBES.items():
        if which not in ("all", name):
            continue
        text, tag = fn()
        (TMP / f"probe-{tag}.snapshot").write_text(text, encoding="utf-8")
        print("wrote", tag, len(text))
