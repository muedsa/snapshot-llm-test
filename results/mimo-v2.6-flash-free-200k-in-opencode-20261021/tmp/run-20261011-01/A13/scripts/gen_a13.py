# -*- coding: utf-8 -*-
"""A13 brand system generator.

Two genuinely different geometric directions for the 叠光 / Layerlight mark:
  A - orthogonal staggered rounded plates (family: rounded rectangles)
  B - radial aperture: ring + eccentric lens disc + light dot (family: circles)

Usage:  gen_a13.py a|b|final
  a/b     writes the 512x512 transparent preview drafts
  final   writes the four delivery drafts for the chosen direction
          (symbol-color, symbol-black, brand-banner, launch-poster)

The banner and poster rebuild the same icon geometry through the same
parameterised rules (no embedded PNG).
"""
import pathlib
import sys

ROOT = pathlib.Path(".")
RUN = "run-20261011-01"
TASK = "A13"
DRAFTS = ROOT / "tmp" / RUN / TASK / "drafts"
DRAFTS.mkdir(parents=True, exist_ok=True)

CHOSEN = None  # set after viewing the previews
choice_file = ROOT / "tmp" / RUN / TASK / "chosen-direction.txt"
if choice_file.exists():
    CHOSEN = choice_file.read_text(encoding="utf-8").strip()

SANS = "Inter,Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

INK_TOP, INK_MID, INK_BOT = "#0B1220", "#0D1526", "#111C31"
CYAN, BLUE, VIOLET, AMBER = "#22D3EE", "#3B82F6", "#7C3AED", "#F59E0B"
TEXT, TEXT2 = "#F8FAFC", "#A9BCD8"

# ---------------------------------------------------------------- icon rules
# All coordinates live in the 512 icon box; scaling is uniform (scale s,
# origin offset) so colour/black icons, banner and poster share one geometry.

ICON = {
    "A": {
        "kind": "stacked plates",
        "bar": {"w": 304, "h": 76, "r": 38},
        "instances": [(64, 96), (104, 218), (144, 340)],
        "colors": [CYAN, BLUE, VIOLET],
    },
    # refined after the 512 + 32px review of both previews:
    #  - disc 176->160 and pushed outward: ring stays continuous at 45deg
    #    (29.5px rim left, ~2px at 32px) instead of being overrun
    #  - disc now opaque: its 85% alpha over the ring muddied the silhouette
    #    at 32px (read as a squarish blob); opacity would also weaken the
    #    pure-black build
    #  - dot 48->56 so it survives the 32px check (~3.5px)
    #  - gaps kept >=36px (>=2.3px at 32px): ring/disc 50.5, ring/dot 36.4,
    #    disc/dot 46.1 in icon units
    "B": {
        "kind": "radial aperture",
        "ring": {"x": 56, "y": 56, "d": 400, "border": 72, "color": CYAN},
        "disc": {"x": 240, "y": 240, "d": 160, "color": VIOLET},
        "dot": {"x": 183, "y": 183, "d": 56, "color": BLUE},
    },
}


def sc(v, s):
    return v * s


def icon_elements(direction, s, ox, oy, black=False):
    """Geometry of the mark, scaled by s and moved to (ox, oy)."""
    e = []
    black_ring = black_disc = black_dot = "#000000"
    g = ICON[direction]
    if direction == "A":
        for i, (x, y) in enumerate(g["instances"]):
            color = "#000000" if black else g["colors"][i]
            e.append(f'<Positioned left="{round(sc(x, s) + ox, 2)}" '
                     f'top="{round(sc(y, s) + oy, 2)}" '
                     f'width="{round(sc(g["bar"]["w"], s), 2)}" '
                     f'height="{round(sc(g["bar"]["h"], s), 2)}">'
                     f'<Container color="{color}" '
                     f'borderRadius="{round(sc(g["bar"]["r"], s), 2)}"/></Positioned>')
    else:
        r, d, dot = g["ring"], g["disc"], g["dot"]
        ring_color = black_ring if black else r["color"]
        disc_color = black_disc if black else d["color"]
        dot_color = black_dot if black else dot["color"]
        e.append(f'<Positioned left="{round(sc(r["x"], s) + ox, 2)}" '
                 f'top="{round(sc(r["y"], s) + oy, 2)}" '
                 f'width="{round(sc(r["d"], s), 2)}" '
                 f'height="{round(sc(r["d"], s), 2)}">'
                 f'<Container shape="CIRCLE" '
                 f'border="{round(sc(r["border"], s), 2)} SOLID {ring_color}"/></Positioned>')
        e.append(f'<Positioned left="{round(sc(d["x"], s) + ox, 2)}" '
                 f'top="{round(sc(d["y"], s) + oy, 2)}" '
                 f'width="{round(sc(d["d"], s), 2)}" '
                 f'height="{round(sc(d["d"], s), 2)}">'
                 f'<Container shape="CIRCLE" color="{disc_color}"/></Positioned>')
        e.append(f'<Positioned left="{round(sc(dot["x"], s) + ox, 2)}" '
                 f'top="{round(sc(dot["y"], s) + oy, 2)}" '
                 f'width="{round(sc(dot["d"], s), 2)}" '
                 f'height="{round(sc(dot["d"], s), 2)}">'
                 f'<Container shape="CIRCLE" color="{dot_color}"/></Positioned>')
    return e


def wrap(elements, w, h, background=None):
    bg = f' background="{background}"' if background else ""
    body = "\n    ".join(elements)
    return (f'<Snapshot type="png"{bg}>\n'
            f'  <SizedBox width="{w}" height="{h}">\n'
            f'    <Stack alignment="TOP_LEFT" clipBehavior="NONE">\n'
            f'    {body}\n'
            f'    </Stack>\n'
            f'  </SizedBox>\n'
            f'</Snapshot>\n')


def text_el(x, y, w, size, color, s, font=SANS, bold=False, align=None, lh="1.2"):
    assert not any(ch in s for ch in "<>&"), s
    ta = [f'left="{x}"', f'top="{y}"', f'width="{w}"']
    sa = [f'fontSize="{size}"', f'color="{color}"', f'fontFamily="{font}"',
          f'height="{lh}"']
    if bold:
        sa.append('fontStyle="BOLD"')
    if align:
        sa.append(f'textAlign="{align}"')
    return f'<Positioned {" ".join(ta)}><Text {" ".join(sa)}>{s}</Text></Positioned>'


def rect_el(x, y, w, h, color, radius=None, border=None):
    a = [f'left="{x}"', f'top="{y}"', f'width="{w}"', f'height="{h}"']
    ca = []
    if color:
        ca.append(f'color="{color}"')
    if radius:
        ca.append(f'borderRadius="{radius}"')
    if border:
        ca.append(f'border="{border}"')
    return f'<Positioned {" ".join(a)}><Container {" ".join(ca)}/></Positioned>'


def gradient_bg(w, h, colors, begin="TOP_CENTER", end="BOTTOM_CENTER"):
    return (f'<Positioned left="0" top="0" width="{w}" height="{h}">'
            f'<Container gradientType="LINEAR" gradientColors="{colors}" '
            f'gradientBegin="{begin}" gradientEnd="{end}"/></Positioned>')


mode = sys.argv[1] if len(sys.argv) > 1 else "preview"

if mode in ("a", "b"):
    d = mode.upper()
    dsl = wrap(icon_elements(d, 1.0, 0, 0), 512, 512)  # transparent canvas
    (DRAFTS / f"preview-{mode}.snapshot").write_text(dsl, encoding="utf-8")
    print(f"preview-{mode} written ({ICON[d]['kind']})")

elif mode == "final":
    assert CHOSEN in ("A", "B"), "choose a direction first"
    g = ICON[CHOSEN]

    # ---- colour icon (transparent 512)
    dsl = wrap(icon_elements(CHOSEN, 1.0, 0, 0), 512, 512)
    (DRAFTS / "symbol-color.snapshot").write_text(dsl, encoding="utf-8")

    # ---- black icon (identical geometry, RGB 0)
    dsl = wrap(icon_elements(CHOSEN, 1.0, 0, 0, black=True), 512, 512)
    (DRAFTS / "symbol-black.snapshot").write_text(dsl, encoding="utf-8")

    # ---- banner 1200x400: icon rebuilt at scale 0.375 (box 192) at left
    s, ix, iy = 0.375, 72, 104
    el = [gradient_bg(1200, 400, f"{INK_TOP},{INK_MID},{INK_BOT}",
                      begin="TOP_LEFT", end="BOTTOM_RIGHT")]
    el += icon_elements(CHOSEN, s, ix, iy)
    el.append(rect_el(336, 96, 56, 4, CYAN, radius=2))
    el.append(text_el(336, 132, 780, 60, TEXT, "叠光 Layerlight", bold=True))
    el.append(text_el(336, 232, 780, 28, TEXT2, "把复杂信息，组织成清晰画面"))
    el.append(text_el(336, 316, 780, 22, CYAN, "layerlight.example.org", font=MONO))
    dsl = wrap(el, 1200, 400, background=INK_TOP)
    (DRAFTS / "brand-banner.snapshot").write_text(dsl, encoding="utf-8")

    # ---- poster 1080x1350: independent vertical composition, icon at 0.62
    s, ix, iy = 0.62, 382, 176
    el = [gradient_bg(1080, 1350, f"{INK_TOP},{INK_MID},{INK_BOT}")]
    el += icon_elements(CHOSEN, s, ix, iy)
    # OPEN BETA pill
    el.append(rect_el(420, 560, 240, 56, AMBER, radius=28))
    el.append(text_el(420, 576, 240, 26, "#0B1220", "OPEN BETA", font=MONO,
                      bold=True, align="CENTER"))
    el.append(text_el(140, 666, 800, 76, TEXT, "叠光 Layerlight", bold=True,
                      align="CENTER"))
    el.append(text_el(140, 790, 800, 34, TEXT2, "把复杂信息，组织成清晰画面",
                      align="CENTER"))
    el.append(rect_el(470, 890, 140, 4, CYAN, radius=2))
    el.append(text_el(140, 940, 800, 34, TEXT, "2026.11.07 · ONLINE", font=MONO,
                      align="CENTER"))
    el.append(rect_el(260, 1140, 560, 1, "#2A3B5C"))
    el.append(text_el(140, 1186, 800, 30, CYAN, "layerlight.example.org",
                      font=MONO, align="CENTER"))
    dsl = wrap(el, 1080, 1350, background=INK_TOP)
    (DRAFTS / "launch-poster.snapshot").write_text(dsl, encoding="utf-8")
    print(f"final drafts written for direction {CHOSEN}")
else:
    raise SystemExit(f"unknown mode {mode}")
