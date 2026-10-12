"""A15 · rebuild the 1440x900 NORTHSTAR dashboard reference with Snapshot DSL.

All coordinates come from the pixel measurements in gen/measure.py + gen/probe*.py, which
read the reference image only to observe colours and boundaries. Nothing from the
reference is embedded, cropped or traced into the output.

Layout constants below are the *reference* values in canvas pixels; text `top` values were
corrected after the first render by comparing measured ink boxes (see iterations.jsonl).
"""
from __future__ import annotations

import json
import os
import sys

TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A15"
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared"))
from dslkit import Doc  # noqa: E402

W, H = 1440, 900
UI = "Inter"

# ---------------------------------------------------------------- sampled colours
C_PAGE = "#F3F6FB"
C_CARD = "#FFFFFF"
C_BORDER = "#E2E8F1"
C_SIDE = "#14233C"
C_SIDE_PILL = "#294467"
C_SIDE_DIM = "#BECADD"
C_SIDE_DOT = "#7C8CA6"
C_PANEL = "#233954"
C_TEAL = "#64DBB6"
C_BLUE = "#245CE4"
C_INK = "#18283F"
C_INK_SOFT = "#63748F"
C_MUTED = "#63748F"
C_MUTED2 = "#63748F"
C_GRID = "#E7EDF5"
C_SEP = "#EBEFF5"
C_HEADBG = "#F3F6FB"
C_GREEN = "#168267"
C_PILL_BLUE_BG = "#E7EFFF"
C_PILL_AMBER_BG = "#FFF3D7"
C_PILL_AMBER_FG = "#9D6613"
C_PILL_GREEN_BG = "#DCF5EC"
C_DOT_AMBER = "#EAAF40"

CONTENT = json.load(open(os.path.join(ROOT, "tasks", "A15-reference-reconstruction",
                                      "inputs", "content.json"), encoding="utf-8"))


def esc(s: str) -> str:
    return f"<![CDATA[{s}]]>" if "<" in s else s


def T(d, x, y, s, size, color, weight="NORMAL", family=UI, w=None,
      align="CENTER_LEFT", spacing=None):
    a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
    if spacing:
        a += f' letterSpacing="{spacing}"'
    body = esc(str(s))
    if w:
        d.raw(f'<Positioned left="{x}" top="{y}" width="{w}">'
              f'<Container alignment="{align}"><Text {a}>{body}</Text>'
              f'</Container></Positioned>')
    else:
        d.raw(f'<Positioned left="{x}" top="{y}"><Text {a}>{body}</Text></Positioned>')


# text vertical placement: Snapshot puts the line box top at `top`; Inter's default line
# height is ~1.21em and the cap top sits ~0.24em below the box top at these sizes.
def ty(ink_top, size, k=0.245):
    return round(ink_top - k * size)


def build() -> str:
    d = Doc(W, H, background=C_PAGE)

    # ================================================================= sidebar
    d.box(0, 0, 220, H, C_SIDE)
    d.box(30, 33, 28, 28, C_TEAL, radius=9)
    d.box(38, 41, 12, 12, C_SIDE, radius=4)
    T(d, 73, ty(38, 17), CONTENT["brand"], 17, "#FFFFFF", "BOLD", spacing=1.5)

    for i, label in enumerate(CONTENT["navigation"]):
        y = 116 + i * 64
        if i == 0:
            d.box(18, y, 184, 48, C_SIDE_PILL, radius=10)
            # the selected row keeps a dot, but a teal one: reference anchor [34,128,45,139]
            d.box(34, y + 12, 12, 12, C_TEAL, radius=6)
            T(d, 62, ty(128, 19), label, 19, "#FFFFFF", "BOLD")
        else:
            d.box(34, y + 11, 12, 12, C_SIDE_DOT, radius=6)
            T(d, 62, ty(y + 11, 19), label, 19, C_SIDE_DIM)
    # -- workspace panel ------------------------------------------------------
    d.box(22, 752, 176, 116, C_PANEL, radius=10)
    T(d, 38, ty(770, 11), CONTENT["workspace_info"][0], 11, C_TEAL, "BOLD", spacing=1.2)
    T(d, 38, ty(804, 16), CONTENT["workspace_info"][1], 16, "#FFFFFF")
    T(d, 38, ty(835, 14), CONTENT["workspace_info"][2], 14, C_SIDE_DIM)

    # ================================================================= header
    T(d, 260, ty(39, 32), CONTENT["title"], 32, C_INK, "BOLD")
    T(d, 260, ty(86, 18), CONTENT["subtitle"], 18, C_MUTED)
    d.box(1184, 43, 216, 48, C_BLUE, radius=8)
    T(d, 1184, ty(55, 17), CONTENT["button"], 17, "#FFFFFF", "BOLD", w=216,
      align="CENTER")

    # ================================================================= KPI cards
    for i, kpi in enumerate(CONTENT["kpis"]):
        x = 260 + i * 384
        d.box(x, 139, 355, 141, C_CARD, radius=12, border=f"1 SOLID {C_BORDER}")
        T(d, x + 24, ty(161, 12.6), kpi["label"], 12.6, C_MUTED, "BOLD", spacing=1.0)
        T(d, x + 24, ty(199, 32), kpi["value"], 32, C_INK, "BOLD")
        up = kpi["change"].startswith("+") or kpi["change"].startswith("\u2212")
        T(d, x + 24, ty(246, 16), kpi["change"], 16,
          C_GREEN if up else "#B42318", "BOLD")

    # ================================================================= chart card
    cx, cy, cw, ch = 260, 311, 740, 283
    d.box(cx, cy, cw, ch, C_CARD, radius=12, border=f"1 SOLID {C_BORDER}")
    T(d, cx + 24, ty(336, 22), CONTENT["chart_title"], 22, C_INK, "BOLD")
    T(d, 0, ty(337, 17), CONTENT["chart_period"], 17, C_MUTED2, w=cx + cw - 26,
      align="CENTER_RIGHT")
    T(d, cx + 28, ty(376, 13), CONTENT["chart_unit"], 13, C_MUTED2)

    ZERO_Y, PX_PER_UNIT = 549.0, 1.2
    PX0, SLOT = 332.0, 101.333
    BARW = 54.0
    ticks = CONTENT["chart_ticks"]
    for t in ticks:
        gy = round(ZERO_Y - t * PX_PER_UNIT)
        d.box(286, gy, cw - 62, 1, C_GRID)
        T(d, 0, ty(gy - 7, 13), str(t), 13, C_MUTED2, w=320, align="CENTER_RIGHT")
    for i, v in enumerate(CONTENT["chart_values"]):
        bx = PX0 + SLOT * (i + 0.5) - BARW / 2
        bh = v * PX_PER_UNIT
        d.box(round(bx), round(ZERO_Y - bh), BARW, round(bh), C_BLUE)
        T(d, round(bx - 30), ty(561, 13), CONTENT["months"][i], 13, C_MUTED2,
          w=BARW + 60, align="CENTER")

    # ================================================================= activity card
    ax, ay, aw, ah = 1031, 311, 369, 283
    d.box(ax, ay, aw, ah, C_CARD, radius=12, border=f"1 SOLID {C_BORDER}")
    T(d, ax + 24, ty(335, 22), CONTENT["activity_title"], 22, C_INK, "BOLD")
    DOT_COLORS = [C_DOT_AMBER, C_BLUE, C_GREEN]
    for i, (name, tstr) in enumerate(CONTENT["activity"]):
        iy = 394 + i * 60
        d.box(1053, iy + 3, 10, 10, DOT_COLORS[i], radius=5)
        T(d, 1077, ty(iy + 2, 17), name, 17, C_INK, "BOLD")
        T(d, 1077, ty(iy + 30, 14.5), tstr, 14.5, C_MUTED2)

    # ================================================================= table card
    tx, tyy, tw, th = 260, 624, 1140, 218
    d.box(tx, tyy, tw, th, C_CARD, radius=12, border=f"1 SOLID {C_BORDER}")
    T(d, tx + 24, ty(645, 22), CONTENT["table_title"], 22, C_INK, "BOLD")
    d.box(284, 688, 1090, 34, C_HEADBG, radius=6)
    COLX = [298, 782, 1033, 1234]
    for i, col in enumerate(CONTENT["table_columns"]):
        T(d, COLX[i], ty(697, 11), col, 11, C_MUTED2, "BOLD", spacing=1.0)
    PILL = {
        "In progress": (C_PILL_BLUE_BG, C_BLUE),
        "Review": (C_PILL_AMBER_BG, C_PILL_AMBER_FG),
        "Done": (C_PILL_GREEN_BG, C_GREEN),
    }
    for r, row in enumerate(CONTENT["rows"]):
        ry = 726 + r * 35
        if r:
            d.box(284, ry - 1, 1090, 1, C_SEP)
        T(d, COLX[0], ty(ry + 10, 16), row[0], 16, C_INK, "BOLD")
        T(d, COLX[1], ty(ry + 10, 16), row[1], 16, C_INK_SOFT)
        bg, fg = PILL[row[2]]
        d.box(1028, ry + 3, 148, 28, bg, radius=14)
        T(d, 1028, ty(ry + 13, 14), row[2], 14, fg, "BOLD", w=148, align="CENTER")
        T(d, COLX[3], ty(ry + 10, 16), row[3], 16, C_INK_SOFT)

    T(d, 260, ty(867, 13), CONTENT["footer"], 13, "#7B8BA3")
    return d.finish()


if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    text = build()
    os.makedirs(os.path.join(TMP, "dsl"), exist_ok=True)
    p = os.path.join(TMP, "dsl", f"reconstructed.{version}.snapshot")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("wrote", p, len(text), "chars")
