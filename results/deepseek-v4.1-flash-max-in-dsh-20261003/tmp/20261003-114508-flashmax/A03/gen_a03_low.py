"""A03 final: System Pulse monitoring card (1280x800), rebuilt from the broken draft.

Every change is traceable to repair-log.json; geometry is computed so the LIVE badge
cannot overlap the title and the REVIEW badge stays inside the 32px safe margin.
"""
from __future__ import annotations

import json
import math
import os

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A03"
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
os.makedirs(TMP, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
VER = __import__("sys").argv[1] if len(__import__("sys").argv) > 1 else "v1"

CJ = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
BG = "#0B1220FF"
PANEL = "#151E30FF"
PANEL2 = "#1B2742FF"
STROKE = "#2B3A55FF"
WHITE = "#FFFFFFFF"
MUTED = "#94A3B8FF"
TEAL = "#2DD4BFFF"
AMBER = "#FBBF24FF"
ROSE = "#FB7185FF"

W, H = 1280, 800
M = 32                       # required safe margin
CW, CH = W - 2 * M, H - 2 * M

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

# ---------------------------------------------------------------- header
text(0, 0, "System Pulse", 44, WHITE, "BOLD")
text(0, 54, "实验舱遥测 · 实时汇总", 20, MUTED)

# LIVE badge: 96x36, fully right of the title, inside the safe margin
LIVE_W, LIVE_H = 96, 36
LIVE_X, LIVE_Y = CW - LIVE_W, 6
box(LIVE_X, LIVE_Y, LIVE_W, LIVE_H, "#7F1D1DFF", 18, f"1 SOLID {ROSE}")
box(LIVE_X + 12, LIVE_Y + 13, 10, 10, ROSE, 5)
text(LIVE_X + 28, LIVE_Y + 7, "LIVE", 20, "#FECDD3FF", "BOLD", MONO, LIVE_W - 36, "CENTER_LEFT")

# ---------------------------------------------------------------- three equal metric cards
CARDS_Y, CARDS_H = 108, 132
GAP = 20
CARD_W = (CW - 2 * GAP) / 3
METRICS = [
    ("USAGE", "72", "%", "0.72", TEAL),
    ("LATENCY", "148", "ms", "p95 · 目标 ≤ 200", AMBER),
    ("SUCCESS", "99.2", "%", "0.992", TEAL),
]
for i, (label, value, unit, note, col) in enumerate(METRICS):
    x = i * (CARD_W + GAP)
    box(x, CARDS_Y, CARD_W, CARDS_H, PANEL, 16, f"1 SOLID {STROKE}")
    box(x, CARDS_Y, CARD_W, 4, col, tl=16, tr=16)
    text(x + 22, CARDS_Y + 22, label, 20, MUTED, "BOLD", MONO)
    text(x + 22, CARDS_Y + 56, value, 40, WHITE, "BOLD", MONO)
    tw = int(len(value) * 24.0) + 6
    text(x + 22 + tw, CARDS_Y + 74, unit, 20, col, "BOLD", MONO)
    text(x + 22, CARDS_Y + 104, note, 18, MUTED, "NORMAL", MONO)

# ---------------------------------------------------------------- explanation card with background-only blur
DESC_X, DESC_Y, DESC_W, DESC_H = (CW - 500) / 2, 360, 500, 150
STRIP_X, STRIP_W = DESC_X - 96, DESC_W + 192        # strips pass through BOTH card edges

# background: base glow + colour strips that cross the card boundaries
box(STRIP_X + 40, DESC_Y - 44, STRIP_W - 80, DESC_H + 88, "#111C2EFF", 18)
STRIPS = [
    (DESC_Y - 26, 22, "#0E9F8FCC"),
    (DESC_Y + 14, 26, "#F59E0BCC"),
    (DESC_Y + 56, 20, "#DB2777CC"),
    (DESC_Y + 96, 30, "#7C3AEDCC"),
    (DESC_Y + 132, 24, "#22D3EECC"),
]
for sy, sh, col in STRIPS:
    box(STRIP_X, sy, STRIP_W, sh, col)

# BackdropFilter blurs ONLY what is painted behind it, so the card wipes the strips
add(f'<Positioned left="{DESC_X}" top="{DESC_Y}"><BackdropFilter sigmaX="12" sigmaY="12">'
    f'<Container width="{DESC_W}" height="{DESC_H}" color="#FFFFFF33" borderRadius="24" '
    f'border="1 SOLID #FFFFFF3D"/></BackdropFilter></Positioned>')
text(DESC_X, DESC_Y, "Background-only blur", 28, WHITE, "BOLD", CJ, DESC_W, "CENTER")
add(f'<Positioned left="{DESC_X}" top="{DESC_Y + 150 - 34}">'
    f'<Container width="{DESC_W}" alignment="CENTER"><Text fontSize="18" color="#E2E8F0FF" '
    f'fontFamily="{CJ}">卡片内背景已模糊，文字保持清晰</Text></Container></Positioned>')

# ---------------------------------------------------------------- REVIEW badge, rotated 8° counter-clockwise
REV_W, REV_H = 160, 56
ang = math.radians(8.0)                      # CCW = negative angle in screen coords
m11, m12 = math.cos(ang), -math.sin(ang)
m21, m22 = -m12, m11
# choose the top-left so the *rotated* box still sits inside the safe margin
half_w, half_h = REV_W / 2, REV_H / 2
dx = abs(m11 * half_w) + abs(m21 * half_h)
dy = abs(m12 * half_w) + abs(m22 * half_h)
REV_X = round(CW - 2 * dx)
REV_Y = round(CH - 2 * dy)
mat = f"(1,0,0,0,0,1,0,0,0,0,1,0,{REV_X},{REV_Y},0,1)"
add(f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
    f'<Container width="{REV_W}" height="{REV_H}" color="#FFFFFF33" borderRadius="10" '
    f'border="1 SOLID #FFFFFF4D"><Container alignment="CENTER">'
    f'<Text fontSize="24" color="#FFFFFFFF" fontFamily="{MONO}" fontStyle="BOLD">REVIEW</Text>'
    f'</Container></Container></Transform></Positioned>')

# ---------------------------------------------------------------- footer note
text(0, CH - 30, "采样窗口 08:00—12:30 · 缺测以空值处理，不补零 · 本卡为修复后重制版", 18, MUTED, "NORMAL", MONO)

add('</Stack>')
add('</Container>')
add('</Snapshot>')

dsl = "\n".join(P) + "\n"
p = os.path.join(TMP, f"system-pulse.{VER}.snapshot")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
print(p, len(dsl), "chars")
print("LIVE", LIVE_X, LIVE_Y, "| title ends ~", 12 + 250, "| REVIEW rotated bbox", round(2 * dx), round(2 * dy))
print("DESC", DESC_X, DESC_Y, DESC_W, DESC_H, "| strips", STRIP_X, STRIP_W)
