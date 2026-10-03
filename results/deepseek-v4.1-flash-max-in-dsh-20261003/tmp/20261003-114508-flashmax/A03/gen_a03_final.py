"""A03 final: System Pulse monitoring card (1280x800), rebuilt from broken.snapshot.

Verified facts driving the layout (all observed, not assumed):
  * BackdropFilter blurs every widget painted BEFORE it inside the same Stack, and the
    blow reaches roughly 4x sigma above its own top edge -> the filter top must stay a
    clear distance below the metric cards.
  * A single flat `Stack alignment="TOP_LEFT" fit="EXPAND"` renders every Positioned
    child; nesting bands inside a Column(mainAxisSize="MIN") fails with
    RENDER_ERROR "renderBox.parentData must be StackParentData", and a nested
    `Stack fit="EXPAND"` inside a positioned Container collapsed children in testing.
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
CW, CH = W - 2 * M, H - 2 * M
CARDS_Y, CARDS_H, GAP = 560, 114, 20
CARD_W = (CW - 2 * GAP) / 3
DESC_W, DESC_H = 500, 150
DESC_X, DESC_Y = (CW - DESC_W) / 2, 330
STRIP_X, STRIP_W = DESC_X - 96, DESC_W + 192
STRIPS = [
    (DESC_Y - 22, 22, "#0E9F8FCC"),
    (DESC_Y + 16, 26, "#F59E0BCC"),
    (DESC_Y + 54, 22, "#DB2777CC"),
    (DESC_Y + 92, 30, "#7C3AEDCC"),
    (DESC_Y + 128, 26, "#22D3EECC"),
]

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

# ---- background glow behind the strips -------------------------------------------
box(STRIP_X + 40, DESC_Y - 34, STRIP_W - 80, DESC_H + 70, "#111C2EFF", 18)

# ---- header (painted before the filter, but far enough above it to stay sharp) ----
text(0, 0, "System Pulse", 44, WHITE, "BOLD")
text(0, 54, "实验舱遥测 · 实时汇总", 20, MUTED)
text(0, 78, "上：标题与状态；中：说明卡（模糊仅作用于卡内背景）；下：三项指标。三层互不重叠。", 18, MUTED)
LIVE_W, LIVE_H, LIVE_X, LIVE_Y = 96, 36, CW - 96, 6
box(LIVE_X, LIVE_Y, LIVE_W, LIVE_H, "#7F1D1DFF", 18, f"1 SOLID {ROSE}")
box(LIVE_X + 12, LIVE_Y + 13, 10, 10, ROSE, 5)
text(LIVE_X + 30, LIVE_Y + 7, "LIVE", 20, "#FECDD3FF", "BOLD", MONO, LIVE_W - 40, "CENTER_LEFT")

# ---- three equal metric cards ----------------------------------------------------
METRICS = [
    ("USAGE", "72", "%", "0.72", TEAL),
    ("LATENCY", "148", "ms", "p95 · 目标 ≤ 200", AMBER),
    ("SUCCESS", "99.2", "%", "0.992", TEAL),
]
for i, (label, value, unit, note, col) in enumerate(METRICS):
    x = i * (CARD_W + GAP)
    box(x, CARDS_Y, CARD_W, CARDS_H, PANEL, 16, f"1 SOLID {STROKE}")
    box(x, CARDS_Y, CARD_W, 4, col, tl=16, tr=16)
    text(x + 22, CARDS_Y + 16, label, 20, MUTED, "BOLD", MONO)
    text(x + 22, CARDS_Y + 44, value, 38, WHITE, "BOLD", MONO)
    text(x + 22 + int(len(value) * 22.8) + 6, CARDS_Y + 60, unit, 20, col, "BOLD", MONO)
    text(x + 22, CARDS_Y + 88, note, 18, MUTED, "NORMAL", MONO)

# ---- frosted band: the BackdropFilter wraps the strips AND the card, and the band is
# ---- placed in a horizontal zone of the canvas that holds nothing else, because the
# ---- filter's blur was measured to bleed ~190px above its own top edge.
BAND_TOP = DESC_Y - 26
BAND_H = 202
add(f'<Positioned left="{STRIP_X}" top="{BAND_TOP}"><BackdropFilter sigmaX="3" sigmaY="3">'
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

# ---- REVIEW badge: 160x56, rotated 8° counter-clockwise --------------------------
REV_W, REV_H = 160, 56
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

text(0, CH - 30, "采样窗口 08:00—12:30 · 缺测以空值处理，不补零 · 本卡为修复后重制版", 18, MUTED, "NORMAL", MONO)

add('</Stack>')
add('</Container>')
add('</Snapshot>')

dsl = "\n".join(P) + "\n"
p = os.path.join(TMP, f"system-pulse.{VER}.snapshot")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
print(p, len(dsl), "chars")
print(f"cards bottom {CARDS_Y+CARDS_H} | filter top {DESC_Y} (gap {DESC_Y-(CARDS_Y+CARDS_H)}px)")
print(f"desc {DESC_X},{DESC_Y} {DESC_W}x{DESC_H} -> bottom {DESC_Y+DESC_H}, right {DESC_X+DESC_W}")
print(f"strips x {STRIP_X}..{STRIP_X+STRIP_W} (card {DESC_X}..{DESC_X+DESC_W})")
print(f"REVIEW rotated bbox {round(2*dx)}x{round(2*dy)} -> right {REV_X+2*dx:.0f}, bottom {REV_Y+2*dy:.0f}")
print(f"LIVE {LIVE_X},{LIVE_Y} {LIVE_W}x{LIVE_H}; title right edge ~262 -> gap {LIVE_X-262}")
print(f"footer y {CH-30}..{CH-30+24}")
