"""B03 probe round 2: A/B canvases that settle what round 1 left ambiguous.

Round 1 (probe.py) left blur, tile modes and the text effects unmeasurable because the
reference geometry was wrong (contiguous stripes, vertical samples of a horizontal
gradient, a shadow test that only looked for pure red). Each canvas here is built so the
measurement coordinates are computed at build time and written to probe2-measure.json.

Run: python tmp/<run_id>/B03/probe2.py [which]
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from snap import C, Container, Node, Positioned, Snapshot, Stack, Text, Transform  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"
MEASURE: dict = {}


def emit(name, w, h, body, bg="#FFFFFF"):
    dsl = Snapshot(Stack(C(width=str(w), height=str(h), color=bg), *body),
                   background=bg, type="png").render() + "\n"
    (TMP / f"probe2-{name}.snapshot").write_text(dsl, encoding="utf-8")
    print("wrote", name, len(dsl))


def pos(child, x, y, w=None, h=None):
    a = {"left": str(x), "top": str(y)}
    if w is not None:
        a["width"] = str(w)
    if h is not None:
        a["height"] = str(h)
    return Positioned(child, **a)


def checker(x0, y0, w, h, cell, dark, light):
    """Explicit checkerboard so blur has real edges to destroy."""
    out = []
    ny, nx = int(h // cell), int(w // cell)
    for j in range(ny):
        for i in range(nx):
            out.append(pos(C(width=str(cell), height=str(cell),
                             color=dark if (i + j) % 2 == 0 else light),
                           x0 + i * cell, y0 + j * cell))
    return out


# ----------------------------------------------------------------- 1. blur A/B
def p_blur2():
    cell, n = 12, 10
    w, h = 30 * n + 20, cell * n + 40        # two 10x10 checkerboards
    body = []
    body += checker(10, 30, cell * n, cell * n, cell, "#111111", "#FFFFFF")
    body += checker(240, 30, cell * n, cell * n, cell, "#111111", "#FFFFFF")
    # right panel: background already painted, then a blurred glass over it
    glass = Node("ClipRRect", {"borderRadius": "0", "clipBehavior": "ANTI_ALIAS"},
                 [Node("BackdropFilter", {"sigmaX": "6", "sigmaY": "6"},
                       [C(width=str(cell * n), height=str(cell * n), color="#00000000")])])
    body.append(pos(glass, 240, 30))
    MEASURE["blur2"] = {
        "sharp_row": (10, 30 + cell * 5, 10 + cell * n),
        "glass_row": (240, 30 + cell * 5, 240 + cell * n),
        "cell": cell, "expect_transitions": n * 2 - 1,
    }
    emit("blur2", w + 230, h, body)


# ----------------------------------------------------------------- 2. tile modes
def p_tile2():
    modes = ["CLAMP", "REPEAT", "MIRROR", "DECAL"]
    s, gap = 160, 20
    body = []
    for i, m in enumerate(modes):
        x = gap + i * (s + gap)
        body.append(pos(C(width=str(s), height=str(s), gradientType="LINEAR",
                          gradientColors="#111111,#FFFFFF", gradientStops="0,0.5",
                          gradientBegin="TOP_LEFT", gradientEnd="TOP_RIGHT",
                          gradientTileMode=m), x, gap))
        body.append(pos(Text(m, fontSize="16", color="#C62828"), x + 4, gap + s + 6, w=s))
    MEASURE["tile2"] = {"rows": [(gap + i * (s + gap), 2 * gap + s // 2,
                                  gap + i * (s + gap) + s) for i in range(len(modes))],
                        "modes": modes}
    emit("tile2", gap + len(modes) * (s + gap), 2 * gap + s + 40, body)


# ----------------------------------------------------------------- 3. rotation / focal
def p_gradrot():
    s = 160
    body = [
        pos(C(width=str(s), height=str(s), gradientType="LINEAR",
              gradientColors="#111111,#FFFFFF", gradientBegin="TOP_LEFT",
              gradientEnd="TOP_RIGHT"), 20, 20),
        pos(C(width=str(s), height=str(s), gradientType="LINEAR",
              gradientColors="#111111,#FFFFFF", gradientBegin="TOP_LEFT",
              gradientEnd="TOP_RIGHT", gradientRotation="1.5708"), 200, 20),
        pos(C(width=str(s), height=str(s), gradientType="RADIAL",
              gradientColors="#111111,#FFFFFF", gradientCenter="CENTER",
              gradientRadius="0.5"), 20, 200),
        pos(C(width=str(s), height=str(s), gradientType="RADIAL",
              gradientColors="#111111,#FFFFFF", gradientCenter="CENTER",
              gradientRadius="0.5", gradientFocal="TOP_LEFT",
              gradientFocalRadius="0.05"), 200, 200),
    ]
    MEASURE["gradrot"] = {
        "plain_tl": (30, 30), "plain_br": (170, 170),
        "rot_tl": (210, 30), "rot_br": (350, 170),
        "radial_centre": (100, 280), "focal_dark_centroid_box": (200, 200, 200 + s, 200 + s),
    }
    emit("gradrot", 380, 380, body)


# ----------------------------------------------------------------- 5. shadow formats
def p_shadow2():
    cards = []
    for i, e in enumerate(("ELEVATION_0", "ELEVATION_1", "ELEVATION_3", "ELEVATION_6",
                           "ELEVATION_9", "ELEVATION_12")):
        cards.append(pos(C(width="200", height="56", color="#FFFFFF", borderRadius="10",
                           boxShadow=e), 26, 20 + i * 76))
        cards.append(pos(Text(e, fontSize="14", color="#444"), 32, 96 + i * 76 - 50, w=190))
    MEASURE["shadow2"] = {"levels": 6, "card_h": 56, "pitch": 76, "x0": 26, "y0": 20,
                          "below_y": 20 + 56 + 6}
    emit("shadow2", 250, 20 + 6 * 76, cards, bg="#E9ECEF")


def p_shadowcustom():
    body = [pos(C(width="220", height="60", color="#FFFFFF", borderRadius="10",
                  boxShadow="6 8 14 #00000066"), 30, 30),
            pos(Text("custom boxShadow string", fontSize="16", color="#333"), 30, 120, w=240)]
    MEASURE["shadowcustom"] = {"below": (140, 100), "sheet": (140, 12)}
    emit("shadowcustom", 300, 180, body, bg="#E9ECEF")


# ----------------------------------------------------------------- 6. filters on content
def p_filter2():
    txt = Text("COLOURISE", fontSize="42", color="#111111")
    body = [
        pos(Node("ColorFiltered", {"color": "#FF5500", "blendMode": "SRC_ATOP"}, [txt]),
            20, 20, w=300, h=70),
        pos(Node("ColorFiltered", {"color": "#0B395488", "blendMode": "MULTIPLY"},
                 [Text("MULTIPLY", fontSize="42", color="#FFFFFF")]), 20, 110, w=300, h=70),
        pos(Node("ImageFiltered", {"sigmaX": "4", "sigmaY": "4"},
                 [Text("BLURRED SUBTREE", fontSize="34", color="#111111")]),
            20, 200, w=340, h=60),
        pos(Node("Opacity", {"opacity": "0.35"},
                 [C(width="150", height="60", color="#E63946", borderRadius="8")]),
            20, 280),
        pos(Node("BackdropFilter", {"sigmaX": "8", "sigmaY": "8",
                                    "blendMode": "SRC_OVER"},
                 [C(width="150", height="60", color="#00000000")]), 300, 280),
    ]
    MEASURE["filter2"] = {"tint_row": (30, 55, 300), "blur_row": (30, 230, 350),
                          "opacity_px": (95, 310), "backdrop_px": (375, 310)}
    emit("filter2", 480, 380, body, bg="#F2F2F2")


# ----------------------------------------------------------------- 7. clip family
def p_clip2():
    src = Stack(*[pos(C(width="240", height="24", color=c), 0, 24 * i)
                  for i, c in enumerate(("#264653", "#2A9D8F", "#E9C46A", "#F4A261",
                                         "#E76F51", "#8AB17D", "#DDA15E", "#BC6C25"))])
    body = [
        pos(Node("ClipOval", {}, [src]), 20, 20, w=240, h=192),
        pos(Node("ClipRect", {}, [src]), 300, 20, w=120, h=96),
        pos(Node("ClipRRect", {"borderRadius": "32", "clipBehavior":
                               "ANTI_ALIAS_WITH_SAVE_LAYER"},
                [C(width="200", height="120", gradientType="SWEEP",
                   gradientColors="#111111,#FFFFFF,#111111",
                   gradientStartAngle="0", gradientEndAngle="6.28")]), 20, 240),
        pos(Node("ClipPath", {"path": "M 0 0 L 200 0 L 200 60 L 100 160 L 0 60 Z"},
                [Stack(*[pos(C(width="200", height="16", color=c), 0, 16 * i)
                         for i, c in enumerate(("#111111", "#E63946", "#F1FAEE", "#A8DADC",
                                                "#457B9D", "#2A9D8F", "#E9C46A",
                                                "#F4A261"))])]), 300, 160, w=200, h=160),
    ]
    MEASURE["clip2"] = {"oval_corner": (22, 22), "oval_centre": (140, 116),
                        "rrect_corner": (22, 242), "rrect_centre": (120, 300),
                        "path_outside": (302, 310), "path_inside": (400, 200)}
    emit("clip2", 520, 400, body)


# ----------------------------------------------------------------- 8. transform depth
def p_transform2():
    def mat(a, b, c, d, tx=0.0, ty=0.0):
        return (f"({a},{b},0,0,{c},{d},0,0,0,0,1,0,{tx},{ty},0,1)")
    body = [
        pos(Transform(C(width="140", height="48", color="#E76F51"),
                      matrix=mat(1, 0.22, 0, 1), alignment="TOP_LEFT"), 30, 30),
        pos(Transform(C(width="140", height="48", color="#2A9D8F"),
                      matrix=mat(1, 0, -0.22, 1), alignment="TOP_LEFT"), 30, 120),
        pos(Transform(C(width="140", height="48", color="#457B9D"),
                      matrix=mat(1.4, 0, 0, 0.6, 0, 0), alignment="CENTER"), 220, 30),
        pos(Transform(Text("MIRROR", fontSize="34", color="#111111"),
                      matrix=mat(-1, 0, 0, 1, 120, 0), alignment="TOP_LEFT"), 220, 120),
        pos(Transform(C(width="60", height="60", color="#111111", borderRadius="6"),
                      matrix=mat(0.866, 0.5, -0.5, 0.866, 0, 0), alignment="TOP_LEFT"),
            60, 220),
        pos(Transform(C(width="60", height="60", color="#E63946", borderRadius="6"),
                      matrix=mat(0.866, 0.5, -0.5, 0.866, 0, 0), alignment="CENTER"),
            200, 220),
    ]
    MEASURE["transform2"] = {"yshear_box": (30, 120, 170, 168),
                             "negx_text_box": (220, 120, 340, 170),
                             "origin_box": (60, 220, 120, 280),
                             "align_box": (200, 220, 260, 280)}
    emit("transform2", 400, 320, body)


PROBES = {"blur2": p_blur2, "tile2": p_tile2, "gradrot": p_gradrot,
          "shadow2": p_shadow2, "shadowcustom": p_shadowcustom, "filter2": p_filter2,
          "clip2": p_clip2, "transform2": p_transform2}

# text A/B is emitted by its own builder because the rows share one canvas
def p_textab_canvas():
    y, lh = 16, 46
    rows = [
        ("digits-plain", Text("0123456789", fontSize="30", color="#111111")),
        ("digits-tnum", Text("0123456789", fontSize="30", color="#111111",
                             fontFeatures="tnum")),
        ("caps-plain", Text("abcdefg", fontSize="30", color="#111111")),
        ("caps-smcp", Text("abcdefg", fontSize="30", color="#111111", fontFeatures="smcp")),
        ("ls-plain", Text("SNAPSHOT", fontSize="30", color="#111111")),
        ("ls-6", Text("SNAPSHOT", fontSize="30", color="#111111", letterSpacing="6")),
        ("ws-plain", Text("one two three", fontSize="26", color="#111111")),
        ("ws-14", Text("one two three", fontSize="26", color="#111111", wordSpacing="14")),
        ("ts-none", Text("shadow", fontSize="34", color="#111111")),
        ("ts-red", Text("shadow", fontSize="34", color="#111111",
                        textShadow="4 5 2 #E53935")),
        ("ts-two", Text("shadow", fontSize="34", color="#111111",
                        textShadow="4 5 2 #E53935,-4 0 0 #0D47A1")),
        ("hi-1.0", Node("Text", {"height": "1.0"},
                        [Text("line-one", fontSize="22", color="#111111"),
                         Text("line-two", fontSize="22", color="#111111")])),
        ("hi-2.6", Node("Text", {"height": "2.6"},
                        [Text("line-one", fontSize="22", color="#111111"),
                         Text("line-two", fontSize="22", color="#111111")])),
        ("dec-ul", Text("underlined words", fontSize="24", color="#111111",
                        decoration="UNDERLINE", decorationColor="#E63946",
                        decorationThickness="3")),
        ("dec-lt", Text("struck through", fontSize="24", color="#111111",
                        decoration="LINE_THROUGH", decorationGaps="1 2")),
        ("raw-sp", Text([Text("|", fontSize="24", color="#111111"),
                         Node("Raw", {}, None, "   spaced   ", False),
                         Text("|", fontSize="24", color="#111111")])),
        ("fg-stroke", Text("STROKE", fontSize="40", color="#FFFFFF",
                           foregroundColor="#111111", foregroundMode="STROKE",
                           foregroundStrokeWidth="2")),
        ("bg-text", Text("boxed", fontSize="26", color="#FFFFFF",
                         backgroundColor="#2A9D8F")),
        ("align-end", Text("right aligned", fontSize="22", color="#111111",
                           textAlign="END")),
    ]
    # measure ink extent per row by rendering each row alone at a fixed origin:
    # widths are read back from the PNG, so the row list must stay ordered.
    MEASURE["textab"] = {"x0": 16, "lh": lh, "rows": [n for n, _ in rows]}
    emit("textab", 560, y + lh * len(rows), [pos(n, 16, y + lh * i)
                                             for i, (nm, n) in enumerate(rows)],
         bg="#FFFFFF")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn in PROBES.items():
        if which in ("all", name):
            fn()
    if which in ("all", "textab"):
        p_textab_canvas()
    (TMP / "probe2-measure.json").write_text(json.dumps(MEASURE, indent=2),
                                             encoding="utf-8")
