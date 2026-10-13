"""A13 - 叠光 / Layerlight identity: two geometric directions, then one system.

The symbol geometry is written once as a scale-aware function, so the banner and the
poster re-derive the same construction instead of embedding the icon PNG.

Run from the suite task root:
  python tmp/<run_id>/A13/gen.py --ver v001 --targets preview-a,preview-b
  python tmp/<run_id>/A13/gen.py --ver v002 --targets color,black,banner,poster --chosen A
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Container, Node, Positioned, Snapshot, Stack, Transform, label, matrix2d, num,
)

RUN = "2026-10-12T10-04Z-r001"
TASK = "A13"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

# snap.label() defaults to align="CENTER"; a probe (probe-align.snapshot) confirmed the
# parser honours START/LEFT/END/RIGHT/CENTER, so every left-set line here must say so.
_label = label


def label(*args, **kw):
    kw.setdefault("align", "LEFT")
    return _label(*args, **kw)


SANS = "Noto Sans CJK SC,Noto Sans CJK JP,Inter"
MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"

PAL = {
    "blue": "#1F5FA8", "teal": "#2E9E8F", "amber": "#E8A33D",
    "rust": "#C2703D", "ink": "#0E1A2B", "paper": "#F5F2EA",
}
# The black cut keeps the layer order readable through alpha only: back layer lightest,
# front layer fully black, so compositing an upper layer over a lower one always raises
# alpha and therefore darkness. Compositing (0,0,0,a) over transparent never introduces a
# non-zero channel, so every pixel with alpha > 0 — including the anti-aliased rim —
# still has R=G=B=0.
BLACK = {"blue": "#000000A0", "teal": "#000000D0", "amber": "#000000FF",
         "rust": "#000000FF", "ink": "#000000FF"}


def col(palette, key):
    return palette[key]


def box(v, c, s):
    """Map one axis of the 512-unit design grid into a canvas at centre c, scale s."""
    return c + (v - 256) * s


# ---------------------------------------------------------------- direction A
def symbol_A(cx, cy, s, palette, *, stroke_scale=1.0):
    """正交层叠：三个同尺寸圆角方框沿对角线错位 + 一个实心小圆作为光源。

    母形是"圆角正方形"，实例 3 个；再加 1 个圆，共 4 个主要几何构件。
    """
    def sq(x, y, w, h, r, key, *, fill=False, sw=16):
        sw = sw * s * stroke_scale
        a = {"width": num(w * s), "height": num(h * s), "borderRadius": num(r * s)}
        if fill:
            a["color"] = col(palette, key)
        else:
            a["border"] = f"{num(sw)} SOLID {col(palette, key)}"
            a["color"] = None
        return Positioned(Container(**a), left=num(box(x, cx, s)), top=num(box(y, cy, s)))

    # v001 used two 16-unit outlines; at 32px they resampled to ~1px and the stack
    # reading collapsed (57 of 1024 pixels survived fully opaque), so the back layer is
    # now solid, the middle layer keeps a 34-unit frame that still shows the back layer
    # through its hole, and the front layer is a smaller solid block.
    els = [sq(110, 96, 216, 216, 40, "blue", fill=True),
           sq(182, 200, 216, 216, 40, "teal", sw=34),
           sq(270, 152, 132, 132, 26, "amber", fill=True)]
    d = 56 * s
    els.append(Positioned(C(width=num(d), height=num(d), color=col(palette, "ink"),
                            shape="CIRCLE"),
                          left=num(box(130, cx, s)), top=num(box(332, cy, s))))
    return els


# ---------------------------------------------------------------- direction B
def symbol_B(cx, cy, s, palette, *, stroke_scale=1.0):
    """放射光圈：一个圆环 + 三条过心的旋转弦 + 一个实心圆心。

    母形是"圆/圆环"1 个与"圆角长条"3 个实例，再加圆心 1 个，共 5 个主要几何构件。
    """
    ring_sw = 22 * s * stroke_scale
    els = [Positioned(C(width=num(340 * s), height=num(340 * s), shape="CIRCLE",
                        border=f"{num(ring_sw)} SOLID {col(palette, 'blue')}"),
                      left=num(box(86, cx, s)), top=num(box(86, cy, s)))]
    for ang, key in ((0, "teal"), (60, "amber"), (120, "rust")):
        rad = math.radians(ang)
        inner = C(width=num(300 * s), height=num(26 * s * stroke_scale),
                  color=col(palette, key), borderRadius=num(13 * s * stroke_scale))
        tr = Node("Transform", {"matrix": matrix2d(math.cos(rad), math.sin(rad)),
                                "alignment": "CENTER"}, [inner])
        els.append(Positioned(tr, left=num(box(106, cx, s)), top=num(box(243, cy, s))))
    d = 76 * s
    els.append(Positioned(C(width=num(d), height=num(d), color=col(palette, "ink"),
                            shape="CIRCLE"),
                          left=num(cx - d / 2), top=num(cy - d / 2)))
    return els


SYMBOLS = {"A": symbol_A, "B": symbol_B}

COMPONENTS = {
    "A": [
        {"id": "A1", "primitive": "rounded square (solid)", "instance": 1,
         "unit_geom": "box 110,96 216x216 r40 fill #1F5FA8", "role": "后层（被叠的底图）",
         "dsl": "Positioned > Container(color, borderRadius=40)"},
        {"id": "A2", "primitive": "rounded square (frame)", "instance": 2,
         "unit_geom": "box 182,200 216x216 r40 border 34 #2E9E8F", "role": "中层框",
         "negative_space": "框内孔 = 216-2·34 = 148 见方、内圆角 40-34 = 6；"
                           "孔由 border 生成，不另计构件，且透过它仍能看到 A1 的边",
         "dsl": "Positioned > Container(border='34 SOLID …', borderRadius=40)"},
        {"id": "A3", "primitive": "rounded square (solid)", "instance": 3,
         "unit_geom": "box 270,152 132x132 r26 fill #E8A33D", "role": "前层小块",
         "dsl": "Positioned > Container(color, borderRadius=26)"},
        {"id": "A4", "primitive": "circle (solid)", "instance": 1,
         "unit_geom": "box 130,332 d=56 fill #0E1A2B", "role": "光源点",
         "dsl": "Positioned > Container(shape=CIRCLE, color)"},
    ],
    "B": [
        {"id": "B1", "primitive": "circle ring", "instance": 1,
         "unit_geom": "box 86,86 340x340 stroke 22", "role": "光圈外环",
         "negative_space": "环内孔由 border 生成，不另计构件",
         "dsl": "Positioned > Container(shape=CIRCLE, border='22 SOLID #1F5FA8')"},
        {"id": "B2", "primitive": "rounded bar (chord)", "instance": 1,
         "unit_geom": "300x26 r13 rotate 0° about centre", "role": "水平弦",
         "dsl": "Positioned > Transform(matrix, alignment=CENTER) > Container"},
        {"id": "B3", "primitive": "rounded bar (chord)", "instance": 2,
         "unit_geom": "300x26 r13 rotate 60°", "role": "右斜弦", "dsl": "同 B2"},
        {"id": "B4", "primitive": "rounded bar (chord)", "instance": 3,
         "unit_geom": "300x26 r13 rotate 120°", "role": "左斜弦", "dsl": "同 B2"},
        {"id": "B5", "primitive": "circle (solid)", "instance": 1,
         "unit_geom": "d=76 at centre", "role": "光心", "dsl": "Container(shape=CIRCLE)"},
    ],
}


def symbol_doc(direction, palette, size=512, stroke_scale=1.0):
    els = SYMBOLS[direction](size / 2, size / 2, size / 512, palette,
                             stroke_scale=stroke_scale)
    return Snapshot(
        Stack(C(width=num(size), height=num(size)), *els,
              alignment="TOP_LEFT", clipBehavior="HARD_EDGE"), type="png")


WORDMARK = ("叠光", "Layerlight")
TAGLINE = "把复杂信息，组织成清晰画面"
POSTER_EXTRA = ["2026.11.07 · ONLINE", "OPEN BETA", "layerlight.example.org"]


def banner_doc(direction, size=(1200, 400)):
    W, H = size
    m = 44
    els = SYMBOLS[direction](m + 140, H / 2, 280 / 512, PAL)
    tx = m + 280 + 44
    els.append(label(tx, 132, WORDMARK[0], 62, PAL["ink"], anchor="left_top", width=W - tx - m,
                     font=SANS, bold=True))
    els.append(label(tx + 232, 132 + (62 - 44) * 0.8, WORDMARK[1], 44,
                     PAL["blue"], anchor="left_top",
                     width=W - tx - 232 - m, font=SANS, bold=True))
    els.append(label(tx, 226, TAGLINE, 30, PAL["ink"], anchor="left_top",
                     width=W - tx - m, font=SANS))
    els.append(label(tx, 278, "信息叠加后仍然清晰 · IDENTITY SYSTEM", 20, "#7A889F",
                     anchor="left_top", width=W - tx - m, font=MONO))
    return Snapshot(Stack(C(width=num(W), height=num(H), color=PAL["paper"]), *els,
                          alignment="TOP_LEFT", clipBehavior="HARD_EDGE"),
                    background=PAL["paper"], type="png")


def poster_doc(direction, size=(1080, 1350)):
    W, H = size
    m = 56
    els = [Positioned(C(width=num(W), height="430", color=PAL["ink"]), left="0", top="0")]
    # symbol becomes the poster's own composition, not a pasted render
    els += SYMBOLS[direction](W / 2, 250, 300 / 512,
                              {"blue": "#8FC7F2", "teal": "#7FD6C4", "amber": "#F2C063",
                               "rust": "#E8A07A", "ink": "#FFFFFF"}, stroke_scale=1.15)
    els.append(label(W - m, 74, "OPEN BETA", 24, "#F2C063", anchor="right_top", width=300,
                     font=MONO, bold=True, align="RIGHT"))
    els.append(label(m, 356, "叠光 / Layerlight", 26, "#BFD6EA", anchor="left_top",
                     width=W - 2 * m, font=SANS))
    els.append(label(m, 500, "叠光", 92, PAL["ink"], anchor="left_top", width=W - 2 * m,
                     font=SANS, bold=True))
    els.append(label(m, 618, "Layerlight", 52, PAL["blue"], anchor="left_top",
                     width=W - 2 * m, font=SANS, bold=True))
    els.append(label(m, 706, TAGLINE, 34, PAL["ink"], anchor="left_top", width=W - 2 * m,
                     font=SANS, line_height=1.3))
    els.append(label(m, 790, "信息叠加后仍然清晰", 24, "#5A6B85", anchor="left_top",
                     width=W - 2 * m, font=SANS))
    els.append(Positioned(C(width=num(W - 2 * m), height="1", color="#CFC7B4"),
                          left=num(m), top="864"))
    rows = [("日期", "2026.11.07 · ONLINE"), ("状态", "OPEN BETA"),
            ("官网", "layerlight.example.org")]
    y = 892
    for k, v in rows:
        els.append(label(m, y, k, 20, "#8A96A8", anchor="left_top", width=90, font=SANS))
        els.append(label(m + 96, y - 3, v, 30, PAL["ink"], anchor="left_top",
                         width=W - 2 * m - 96, font=MONO))
        y += 62
    els.append(Positioned(C(width=num(W - 2 * m), height=num(96), color=PAL["ink"],
                            borderRadius="16"), left=num(m), top="1112"))
    els.append(label(m + 32, 1144, "layerlight.example.org", 32, "#FFFFFF",
                     anchor="left_top", width=W - 2 * m - 64, font=MONO, bold=True))
    els.append(label(W - m - 32, 1150, "OPEN BETA", 22, "#F2C063", anchor="right_top",
                     width=300, font=MONO, align="RIGHT"))
    els.append(label(m, 1252, "叠光 / Layerlight — 结构化视觉工具 · 本图为虚构品牌排版样张",
                     20, "#7A889F", anchor="left_top", width=W - 2 * m, font=SANS))
    return Snapshot(Stack(C(width=num(W), height=num(H)), *els,
                          alignment="TOP_LEFT", clipBehavior="HARD_EDGE"),
                    background=PAL["paper"], type="png")


TARGETS = {
    "preview-a": lambda: symbol_doc("A", PAL),
    "preview-b": lambda: symbol_doc("B", PAL),
    "color": None, "black": None, "banner": None, "poster": None,
}

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
ap.add_argument("--targets", default="preview-a,preview-b")
ap.add_argument("--chosen", default="A")
a = ap.parse_args()

OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

made = {}
for t in a.targets.split(","):
    t = t.strip()
    if not t:
        continue
    if t == "color":
        d = symbol_doc(a.chosen, PAL)
    elif t == "black":
        d = symbol_doc(a.chosen, BLACK)
    elif t == "banner":
        d = banner_doc(a.chosen)
    elif t == "poster":
        d = poster_doc(a.chosen)
    else:
        d = TARGETS[t]()
    name = {"color": "symbol-color", "black": "symbol-black", "banner": "brand-banner",
            "poster": "launch-poster"}.get(t, t)
    (TMP_DIR / f"{a.ver}-{name}.snapshot").write_text(d.render() + "\n", encoding="utf-8")
    made[name] = len(d.render().encode())

meta = {
    "direction": a.chosen,
    "components": COMPONENTS[a.chosen],
    "component_count": len(COMPONENTS[a.chosen]),
    "limit": 6,
    "within_limit": len(COMPONENTS[a.chosen]) <= 6,
}
(TMP_DIR / f"{a.ver}-geometry.json").write_text(
    json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"ver": a.ver, "made": made, "chosen": a.chosen,
                  "component_count": len(COMPONENTS[a.chosen])}, ensure_ascii=False))
