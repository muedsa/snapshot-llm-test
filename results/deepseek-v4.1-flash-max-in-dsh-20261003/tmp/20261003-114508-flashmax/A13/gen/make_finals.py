"""A13 · final deliverables for the chosen direction (A "层窗 / pane-stack").

Builds symbol-color, symbol-black, brand-banner and launch-poster from the SAME
emit_mark() geometry, and dumps the resolved pixel geometry of every application to
brand-geometry.json so brand-system.json can quote real numbers.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from a13lib import (Doc, CJK, MONO, INK, INK_SOFT, TEAL, BLUE, AMBER, PAPER, CARD,  # noqa: E402
                    LINE, SLATE, SLATE_L, BLACK, hexa, emit_mark, rot_box, rot_bar,
                    PAL_COLOR, palette_color)

TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A13"
DSL = os.path.join(TMP, "dsl", "final")
GEO = {}

PAL_COLOR_FINAL = palette_color(None)          # 3 crisp components, no ghost
PAL_BLACK_FINAL = {"pane_outer": hexa(BLACK, 0xFF), "pane_inner": hexa(BLACK, 0xFF),
                   "core": hexa(BLACK, 0xFF), "ghost": None}


# --------------------------------------------------------------------------- icons
def symbol_color() -> str:
    d = Doc(512, 512, background="transparent")
    GEO["symbol-color"] = emit_mark(d, 256, 256, 384, PAL_COLOR_FINAL, ghost=False)
    return d.finish()


def symbol_black() -> str:
    d = Doc(512, 512, background="transparent")
    GEO["symbol-black"] = emit_mark(d, 256, 256, 384, PAL_BLACK_FINAL, ghost=False)
    return d.finish()


# --------------------------------------------------------------------------- banner
def brand_banner() -> str:
    W, H = 1200, 400
    d = Doc(W, H, background=INK)
    # Decorative rings in the mark's own geometry language, bleeding off the right edge.
    # Only teal + blue: an amber ring at low alpha over the ink background reads as a
    # muddy olive (seen in v1) and fought with the wordmark.
    for size, bw, r, col in ((672, 30, 158, hexa(TEAL, 0x1F)),
                             (470, 24, 112, hexa(BLUE, 0x26))):
        rot_box(d, 1120, 200, size, size, 0, border=f"{bw} SOLID {col}", radius=r)

    GEO["brand-banner"] = dict(
        mark=emit_mark(d, 140, 200, 208, PAL_COLOR_FINAL, ghost=False),
        mark_scale_note="same emit_mark() rules as symbol-color, scale 208/384",
    )

    d.box(274, 100, 2, 200, hexa("#24334D", 0xFF))
    d.text(316, 104, "STRUCTURED VISUAL TOOLS", 18, hexa(TEAL, 0xFF), family=MONO)
    d.text(316, 140, "叠光 Layerlight", 60, "#FFFFFF", weight="BOLD")
    d.text(316, 232, "把复杂信息，组织成清晰画面", 28, hexa(SLATE_L, 0xFF))
    d.box(316, 296, 84, 6, hexa(TEAL, 0xFF), radius=3)
    d.text(316, 326, "layerlight.example.org", 18, hexa("#64748B", 0xFF), family=MONO)
    return d.finish()


# --------------------------------------------------------------------------- poster
def launch_poster() -> str:
    W, H = 1080, 1350
    d = Doc(W, H, background=INK)
    # ---- dark hero zone 0..940 -------------------------------------------------
    # Two *offset* halo rings instead of concentric ones: v1 stacked four concentric
    # rounded squares (halo + halo + the mark's own two rings) and read as a target
    # rather than as stacked panes.
    rot_box(d, 540, 352, 880, 880, 0, border=f"30 SOLID {hexa(TEAL, 0x12)}", radius=206)
    rot_box(d, 488, 300, 716, 716, 0, border=f"26 SOLID {hexa(BLUE, 0x10)}", radius=168)

    hero = emit_mark(d, 540, 360, 360, PAL_COLOR_FINAL, ghost=False)

    # header row
    head = emit_mark(d, 104, 96, 64, PAL_COLOR_FINAL, ghost=False)
    d.text(160, 78, "叠光 Layerlight", 30, "#FFFFFF", weight="BOLD")
    chip_w = 9 * 0.60 * 22 + 44
    d.box(W - 72 - chip_w, 74, chip_w, 46, hexa(TEAL, 0x1F), radius=23,
          border=f"2 SOLID {hexa(TEAL, 0x99)}")
    d.text(W - 72 - chip_w, 84, "OPEN BETA", 22, hexa(TEAL, 0xFF), family=MONO,
           w=chip_w, align="CENTER")

    d.text(0, 580, "叠光", 170, "#FFFFFF", weight="BOLD", w=W, align="CENTER")
    d.text(0, 800, "Layerlight", 50, hexa(TEAL, 0xFF), w=W, align="CENTER")

    # ---- light information zone 940..1350 --------------------------------------
    d.box(0, 940, W, H - 940, PAPER)
    d.box(88, 972, 904, 328, CARD, radius=28, border=f"1 SOLID {LINE}",
          shadow="0 10 30 0 #0F172A1F NORMAL")
    d.text(144, 1006, "把复杂信息，组织成清晰画面", 32, hexa(INK_SOFT, 0xFF))
    d.text(144, 1072, "2026.11.07 · ONLINE", 58, hexa(INK, 0xFF), family=MONO)
    d.text(144, 1166, "layerlight.example.org", 22, hexa("#64748B", 0xFF), family=MONO)
    d.box(144, 1216, 84, 6, hexa(TEAL, 0xFF), radius=3)
    bchip = 9 * 0.60 * 22 + 40
    d.box(144, 1240, bchip, 44, hexa(INK, 0x0F), radius=22,
          border=f"2 SOLID {hexa(INK, 0x33)}")
    d.text(144, 1249, "OPEN BETA", 22, hexa(INK, 0xFF), family=MONO, w=bchip,
           align="CENTER")
    card_mark = emit_mark(d, 872, 1136, 152, PAL_COLOR_FINAL, ghost=False)
    d.box(0, 1342, W, 8, hexa(TEAL, 0xFF))

    GEO["launch-poster"] = dict(hero=hero, header_mark=head, card_mark=card_mark)
    GEO["_poster_notes"] = dict(
        hero_scale="360/384 of the master mark", header_scale="64/384",
        card_scale="152/384", dark_zone="0..940", light_zone="940..1350")
    return d.finish()


BUILDERS = {
    "symbol-color": symbol_color,
    "symbol-black": symbol_black,
    "brand-banner": brand_banner,
    "launch-poster": launch_poster,
}


def main() -> None:
    os.makedirs(DSL, exist_ok=True)
    for name, fn in BUILDERS.items():
        text = fn()
        path = os.path.join(DSL, f"{name}.snapshot")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"{name}: {len(text)} bytes -> {path}")
    with open(os.path.join(TMP, "brand-geometry.json"), "w", encoding="utf-8") as fh:
        json.dump(GEO, fh, ensure_ascii=False, indent=2)
    print("geometry dumped")


if __name__ == "__main__":
    main()
