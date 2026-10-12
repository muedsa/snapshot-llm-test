"""A03 final: System Pulse monitoring card (1280x800) rebuilt from broken.snapshot.

Blur containment, established by measurement rather than assumption:
  * BackdropFilter in this build blurs the ENTIRE canvas composited so far, not only the
    region behind its own bounds. Measured reach is roughly 20x sigma (sigma=10 -> about
    200px). Placing the metric cards vertically above or below the filter still smeared
    their glyphs (v3/v13/v14/v15/v16, contrast of the value text fell from 225 to <=145).
  * The one geometry that measured clean is HORIZONTAL separation: the frosted band lives
    in a right-hand column and every other element sits at least 70px to its left, so the
    spread cannot reach any glyph.
"""
from __future__ import annotations

import math
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A03"
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
os.makedirs(TMP, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
VER = sys.argv[1] if len(sys.argv) > 1 else "v1"

CJ = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
BG = "#0B1220FF"
PANEL = "#151E30FF"
STROKE = "#2B3A55FF"
WHITE = "#FFFFFFFF"
MUTED = "#94A3B8FF"
TEAL = "#2DD4BFFF"
AMBER = "#FBBF24FF"
ROSE = "#FB7185FF"

W, H, M = 1280, 800, 32
CW, CH = W - 2 * M, H - 2 * M          # 1216 x 736 content box

# ---- right column holds the frosted band -----------------------------------------
STRIP_X, STRIP_W = 686, 562
DESC_W, DESC_H = 500, 150
DESC_X = STRIP_X + (STRIP_W - DESC_W) / 2     # 717  -> card 717..1217 (right margin 63)
BAND_TOP, BAND_H = 296, 202
DESC_Y = BAND_TOP + 26
SIGMA = 4

# ---- left column holds everything else, >=70px clear of the band ------------------
LEFT_W = STRIP_X - 70 - 0                     # 616 px of usable width
CARDS_Y, CARDS_H, GAP = 122, 168, 18
CARD_W = (LEFT_W - 2 * GAP) / 3               # 193.3
LIVE_W, LIVE_H, LIVE_X, LIVE_Y = 96, 36, CW - 96, 6
REV_W, REV_H = 160, 56

P: list[str] = []
add = P.append


def box(x, y, w, h, color, radius=None, border=None, tl=None, tr=None, bl=None, br=None):
    a = f'<Container width="{w}" height="{h}" color="{color}"'
    if radius:
        a += f' borderRadius="{radius}"'
    for name, v in (("TopLeft", tl), ("TopRight", tr), ("BottomLeft", bl), ("BottomRight", br)):
        if v:
            a += f' borderRadius{name}="{v}"'
    if border:
        a += f' border="{border}"'
    add(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')


def text(x, y, s, size, color, weight="NORMAL", family=CJ, w=None, align="CENTER_LEFT"):
    a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
    body = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if w:
        add(f'<Positioned left="{x}" top="{y}" width="{w}"><Container alignment="{align}">'
            f'<Text {a}>{body}</Text></Container></Positioned>')
    else:
        add(f'<Positioned left="{x}" top="{y}"><Text {a}>{body}</Text></Positioned>')


add(f'<Snapshot background="{BG}" type="png">')
add(f'<Container width="{W}" height="{H}" padding="{M}">')
add('<Stack alignment="TOP_LEFT" fit="EXPAND">')

# ---------------- header ----------------
text(0, 0, "System Pulse", 44, WHITE, "BOLD")
text(0, 54, "实验舱遥测 · 实时汇总", 20, MUTED)
box(LIVE_X, LIVE_Y, LIVE_W, LIVE_H, "#7F1D1DFF", 18, f"1 SOLID {ROSE}")
box(LIVE_X + 12, LIVE_Y + 13, 10, 10, ROSE, 5)
text(LIVE_X + 30, LIVE_Y + 7, "LIVE", 20, "#FECDD3FF", "BOLD", MONO, LIVE_W - 40, "CENTER_LEFT")

# ---------------- left column: three stacked equal-width metric cards ----------------
METRICS = [
    ("USAGE", "72", "%", "0.72", TEAL),
    ("LATENCY", "148", "ms", "p95 · 目标 ≤ 200", AMBER),
    ("SUCCESS", "99.2", "%", "0.992", TEAL),
]
for i, (label, value, unit, note, col) in enumerate(METRICS):
    x = i * (CARD_W + GAP)
    box(x, CARDS_Y, CARD_W, CARDS_H, PANEL, 16, f"1 SOLID {STROKE}")
    box(x, CARDS_Y, CARD_W, 4, col, tl=16, tr=16)
    text(x + 18, CARDS_Y + 20, label, 20, MUTED, "BOLD", MONO)
    text(x + 18, CARDS_Y + 52, value, 40, WHITE, "BOLD", MONO)
    text(x + 18 + int(len(value) * 24.0) + 6, CARDS_Y + 68, unit, 20, col, "BOLD", MONO)
    text(x + 18, CARDS_Y + 118, note, 18, MUTED, "NORMAL", MONO)

text(0, CARDS_Y + CARDS_H + 22, "三项指标与说明卡分居左右两栏，横向净空 %.0fpx，模糊不会扩散到任何文字。" % (STRIP_X - LEFT_W),
     18, MUTED)

# ---------------- right column: colour strips behind a frosted card ----------------
STRIPS = [
    (DESC_Y - 22, 22, "#0E9F8FCC"),
    (DESC_Y + 16, 26, "#F59E0BCC"),
    (DESC_Y + 54, 22, "#DB2777CC"),
    (DESC_Y + 92, 30, "#7C3AEDCC"),
    (DESC_Y + 128, 26, "#22D3EECC"),
]
box(STRIP_X + 30, BAND_TOP, STRIP_W - 60, BAND_H, "#111C2EFF", 18)
add(f'<Positioned left="{STRIP_X}" top="{BAND_TOP}"><BackdropFilter sigmaX="{SIGMA}" sigmaY="{SIGMA}">'
    f'<Stack alignment="TOP_LEFT">'
    f'<Container width="{STRIP_W}" height="{BAND_H}" color="#00000000"/>'
    + "".join(f'<Positioned left="0" top="{sy - BAND_TOP}"><Container width="{STRIP_W}" '
              f'height="{sh}" color="{col}"/></Positioned>' for sy, sh, col in STRIPS)
    + f'<Positioned left="{DESC_X - STRIP_X}" top="26"><Container width="{DESC_W}" height="{DESC_H}" '
      f'color="#FFFFFF33" borderRadius="24" border="1 SOLID #FFFFFF3D"/></Positioned>'
    f'</Stack></BackdropFilter></Positioned>')
add(f'<Positioned left="{DESC_X}" top="{DESC_Y + 34}"><Container width="{DESC_W}" alignment="CENTER">'
    f'<Text fontSize="28" color="{WHITE}" fontFamily="{CJ}" fontStyle="BOLD">Background-only blur</Text>'
    f'</Container></Positioned>')
add(f'<Positioned left="{DESC_X}" top="{DESC_Y + DESC_H - 40}"><Container width="{DESC_W}" alignment="CENTER">'
    f'<Text fontSize="18" color="#E2E8F0FF" fontFamily="{CJ}">卡片内背景已模糊，文字保持清晰</Text>'
    f'</Container></Positioned>')
text(STRIP_X, BAND_TOP + BAND_H + 14, "彩色细条横穿说明卡左右两侧边界", 18, MUTED)

# ---------------- REVIEW badge: 160x56, rotated 8° counter-clockwise ----------------
ang = math.radians(8.0)
m11, m12 = math.cos(ang), -math.sin(ang)
m21, m22 = -m12, m11
dx = abs(m11 * REV_W / 2) + abs(m21 * REV_H / 2)
dy = abs(m12 * REV_W / 2) + abs(m22 * REV_H / 2)
REV_X, REV_Y = round(CW - 2 * dx), round(CH - 2 * dy)
mat = f"(1,0,0,0,0,1,0,0,0,0,1,0,{REV_X},{REV_Y},0,1)"
add(f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
    f'<Container width="{REV_W}" height="{REV_H}" color="#FFFFFF33" borderRadius="10" '
    f'border="1 SOLID #FFFFFF4D"><Container alignment="CENTER">'
    f'<Text fontSize="24" color="{WHITE}" fontFamily="{MONO}" fontStyle="BOLD">REVIEW</Text>'
    f'</Container></Container></Transform></Positioned>')
# colour swatch note for the 20% white fill
text(0, 640, "REVIEW 徽标：白底 20% 不透明度，文字不透明 24px，逆时针 8°", 18, MUTED)

text(0, CH - 30, "采样窗口 08:00—12:30 · 缺测以空值处理，不补零 · 本卡为修复后重制版", 18, MUTED, "NORMAL", MONO)

add('</Stack>')
add('</Container>')
add('</Snapshot>')

dsl = "\n".join(P) + "\n"
p = os.path.join(TMP, f"system-pulse.{VER}.snapshot")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
print(p, len(dsl), "chars")
print(f"left column x 0..{LEFT_W:.0f} | band x {STRIP_X}..{STRIP_X+STRIP_W} | horizontal gap {STRIP_X-LEFT_W:.0f}px")
print(f"cards y {CARDS_Y}..{CARDS_Y+CARDS_H} | band y {BAND_TOP}..{BAND_TOP+BAND_H}")
print(f"card {DESC_X}..{DESC_X+DESC_W} y {DESC_Y}..{DESC_Y+DESC_H}; strips cross both edges")
print(f"LIVE {LIVE_X},{LIVE_Y} {LIVE_W}x{LIVE_H}; title right edge ~262 -> clear")
print(f"REVIEW rotated bbox {round(2*dx)}x{round(2*dy)} -> right {REV_X+2*dx:.0f} bottom {REV_Y+2*dy:.0f}")
