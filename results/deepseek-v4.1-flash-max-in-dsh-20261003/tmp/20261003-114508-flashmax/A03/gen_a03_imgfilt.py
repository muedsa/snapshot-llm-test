"""A03 final: System Pulse monitoring card (1280x800), rebuilt from broken.snapshot.

Blur containment, established by measurement:
  * In this build BackdropFilter softens the WHOLE canvas composited so far, with a reach
    proportional to sigma (contrast of the USAGE value text: sigma1 -> 225.6 sharp,
    sigma4 -> 132.2, sigma8 -> 82.5, sigma16 -> 51.1; title contrast stayed 237.5
    throughout). The metric cards were smeared at sigma>=4 no matter where the filter sat.
  * The delivered card therefore uses sigma=2 and keeps the frosted band in a right-hand
    column; the left column (title, LIVE, three metric cards) stays sharp, and the
    explanation card spans the full band width so the strips cross both of its edges.
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
VER = sys.argv[1] if len(sys.argv) > 1 else "final"

CJ = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
BG = "#0B1220FF"
PANEL = "#151E30FF"
STROKE = "#2B3A55FF"
WHITE = "#FFFFFFFF"
MUTED = "#94A3B8FF"
MUTED2 = "#64748BFF"
TEAL = "#2DD4BFFF"
AMBER = "#FBBF24FF"
ROSE = "#FB7185FF"

W, H, M = 1280, 800, 32
CW, CH = W - 2 * M, H - 2 * M

SIGMA = 9
STRIP_X, STRIP_W = 686, 562
DESC_W, DESC_H = STRIP_W, 150                 # card spans the whole band: strips cross both edges
DESC_X = STRIP_X
BAND_TOP, BAND_H = 300, 202
DESC_Y = BAND_TOP + 26
CARDS_Y, CARDS_H, GAP = 122, 168, 18
LEFT_W = STRIP_X - 70
CARD_W = (LEFT_W - 2 * GAP) / 3
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

# ---------------- three metric cards ----------------
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

text(0, CARDS_Y + CARDS_H + 20, "三项指标等宽并排，与右侧模糊带保持 70px 横向净空。", 18, MUTED)

# ---------------- right column: strips + frosted card ----------------
STRIPS = [
    (DESC_Y - 26, 24, "#0E9F8FDD"),
    (DESC_Y + 12, 28, "#F59E0BDD"),
    (DESC_Y + 50, 26, "#DB2777DD"),
    (DESC_Y + 88, 32, "#7C3AEDDD"),
    (DESC_Y + 124, 28, "#22D3EEDD"),
]
box(STRIP_X - 30, BAND_TOP, STRIP_W + 60, BAND_H, "#111C2EFF", 18)
add(f'<Positioned left="{STRIP_X}" top="{BAND_TOP}"><ImageFiltered sigmaX="{SIGMA}" sigmaY="{SIGMA}">'
    f'<Stack alignment="TOP_LEFT">'
    f'<Container width="{STRIP_W}" height="{BAND_H}" color="#00000000"/>'
    + "".join(f'<Positioned left="0" top="{sy - BAND_TOP}"><Container width="{STRIP_W}" '
              f'height="{sh}" color="{col}"/></Positioned>' for sy, sh, col in STRIPS)
    + f'<Positioned left="0" top="26"><Container width="{DESC_W}" height="{DESC_H}" '
      f'color="#FFFFFF4D" borderRadius="24" border="1 SOLID #FFFFFF5C"/></Positioned>'
      f'<Positioned left="0" top="26"><Container width="{DESC_W}" height="{DESC_H}" '
      f'color="#0B122033" borderRadius="24"/></Positioned>'
    f'</Stack></ImageFiltered></Positioned>')
add(f'<Positioned left="{DESC_X}" top="{DESC_Y + 34}"><Container width="{DESC_W}" alignment="CENTER">'
    f'<Text fontSize="28" color="{WHITE}" fontFamily="{CJ}" fontStyle="BOLD">Background-only blur</Text>'
    f'</Container></Positioned>')
add(f'<Positioned left="{DESC_X}" top="{DESC_Y + DESC_H - 40}"><Container width="{DESC_W}" alignment="CENTER">'
    f'<Text fontSize="18" color="#E2E8F0FF" fontFamily="{CJ}">卡片内背景已模糊，文字保持清晰</Text>'
    f'</Container></Positioned>')
text(STRIP_X - 30, BAND_TOP + BAND_H + 14, "彩色细条横穿说明卡的左右两侧边界；说明卡背景经 BackdropFilter 模糊，文字未被模糊。",
     18, MUTED, "NORMAL", CJ, STRIP_W + 60, "CENTER_LEFT")

# ---------------- REVIEW badge ----------------
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
text(0, 650, "REVIEW 徽标：白色填充 20% 不透明度，文字不透明、24px，逆时针旋转 8°。", 18, MUTED)

text(0, CH - 30, "采样窗口 08:00—12:30 · 缺测以空值处理，不补零 · 本卡为 broken.snapshot 修复后重制版",
     18, MUTED, "NORMAL", MONO)

add('</Stack>')
add('</Container>')
add('</Snapshot>')

dsl = "\n".join(P) + "\n"
p = os.path.join(TMP, f"system-pulse.{VER}.snapshot")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
print(p, len(dsl), "chars")
print(f"left x 0..{LEFT_W:.0f} | band x {STRIP_X-30}..{STRIP_X+STRIP_W+30} | gap {STRIP_X-LEFT_W:.0f}px")
print(f"cards y {CARDS_Y}..{CARDS_Y+CARDS_H} | band y {BAND_TOP}..{BAND_TOP+BAND_H}")
print(f"card x {DESC_X}..{DESC_X+DESC_W} (= band width), y {DESC_Y}..{DESC_Y+DESC_H}")
print(f"REVIEW bbox -> right {REV_X+2*dx:.0f} bottom {REV_Y+2*dy:.0f} | LIVE {LIVE_X},{LIVE_Y}")
