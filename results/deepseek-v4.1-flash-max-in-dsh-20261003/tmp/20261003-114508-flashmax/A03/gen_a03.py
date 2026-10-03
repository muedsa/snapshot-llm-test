"""A03 final: System Pulse monitoring card (1280x800), rebuilt from the broken draft.

Layout note: BackdropFilter blurs every widget painted before it in the SAME Stack
(observed in system-pulse.v3/v4, where the title and metric cards went soft). The page
is therefore built as three sibling bands, each its own padded Container + Stack:

  band 1  background  : base glow only
  band 2  backdrop    : the colour strips + the BackdropFilter that softens them
  band 3  foreground  : title, LIVE badge, metric cards, card text, REVIEW badge

So the blur can only ever affect the strips, while all text stays sharp.

Every coordinate below is in page space (0..1280, 0..800); `band()` converts.
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

W, H = 1280, 800
M = 32
CW, CH = W - 2 * M, H - 2 * M
CARDS_Y, CARDS_H, GAP = 108, 132, 20
CARD_W = (CW - 2 * GAP) / 3
DESC_W, DESC_H = 500, 150
DESC_X, DESC_Y = (CW - DESC_W) / 2, 356
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


def band() -> None:
    add('</Stack>')
    add('</Container></Positioned>')


BAND_TOP = 0


def open_band() -> None:
    """One absolutely positioned 1280x800 band; its inner Stack restarts at the safe margin.

    NOTE: the inner Stack must NOT use `fit` and the band must not be wrapped in a
    Column with mainAxisSize="MIN" — both were tested and collapse the band to nothing
    (iso-expand-in-column.snapshot even returned RENDER_ERROR
    "renderBox.parentData must be StackParentData"). A plain TOP_LEFT Stack with an
    explicit 1280x800 Container is the combination that renders all Positioned children.
    """
    global BAND_TOP
    add(f'<Positioned left="0" top="{BAND_TOP}"><Container width="{W}" height="{H}" padding="{M}">')
    add('<Stack alignment="TOP_LEFT">')
    BAND_TOP += H


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
add(f'<Container width="{W}" height="{H}">')
add('<Stack alignment="TOP_LEFT" fit="EXPAND">')

# ============================== band 1: backdrop strips ==============================
# These strips are page-space siblings of the band below, so the BackdropFilter there
# picks them up: it blurs everything painted before it in the same Stack.
open_band()
box(STRIP_X + 40, DESC_Y - 34, STRIP_W - 80, DESC_H + 70, "#111C2EFF", 18)
for sy, sh, col in STRIPS:
    box(STRIP_X, sy, STRIP_W, sh, col)
band()

# ============================== band 2: frosted card ==============================
open_band()
add(f'<Positioned left="{DESC_X}" top="{DESC_Y}"><BackdropFilter sigmaX="10" sigmaY="10">'
    '<Stack alignment="TOP_LEFT">'
    f'<Container width="{DESC_W}" height="{DESC_H}" color="#FFFFFF33" borderRadius="24" '
    f'border="1 SOLID #FFFFFF3D"/>'
    '</Stack></BackdropFilter></Positioned>')
band()

# ============================== band 3: foreground ==============================
open_band()
# header
text(0, 0, "System Pulse", 44, WHITE, "BOLD")
text(0, 54, "实验舱遥测 · 实时汇总", 20, MUTED)
LIVE_W, LIVE_H, LIVE_X, LIVE_Y = 96, 36, CW - 96, 6
box(LIVE_X, LIVE_Y, LIVE_W, LIVE_H, "#7F1D1DFF", 18, f"1 SOLID {ROSE}")
box(LIVE_X + 12, LIVE_Y + 13, 10, 10, ROSE, 5)
text(LIVE_X + 30, LIVE_Y + 7, "LIVE", 20, "#FECDD3FF", "BOLD", MONO, LIVE_W - 40, "CENTER_LEFT")

# three equal metric cards
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
    text(x + 22 + int(len(value) * 24.0) + 6, CARDS_Y + 74, unit, 20, col, "BOLD", MONO)
    text(x + 22, CARDS_Y + 104, note, 18, MUTED, "NORMAL", MONO)

# explanation card text (sharp, drawn after the blurred backdrop)
add(f'<Positioned left="{DESC_X}" top="{DESC_Y + 46}">'
    f'<Container width="{DESC_W}" alignment="CENTER"><Text fontSize="28" color="{WHITE}" '
    f'fontFamily="{CJ}" fontStyle="BOLD">Background-only blur</Text></Container></Positioned>')
add(f'<Positioned left="{DESC_X}" top="{DESC_Y + DESC_H - 40}">'
    f'<Container width="{DESC_W}" alignment="CENTER"><Text fontSize="18" color="#E2E8F0FF" '
    f'fontFamily="{CJ}">卡片内背景已模糊，文字保持清晰</Text></Container></Positioned>')

# REVIEW badge: 160x56, rotated 8° counter-clockwise, inside the safe margin
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
band()
add('</Snapshot>')

dsl = "\n".join(P) + "\n"
p = os.path.join(TMP, f"system-pulse.{VER}.snapshot")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
print(p, len(dsl), "chars")
print(f"LIVE {LIVE_X},{LIVE_Y} {LIVE_W}x{LIVE_H} | title right edge ~262")
print(f"DESC {DESC_X},{DESC_Y} {DESC_W}x{DESC_H} | strips x {STRIP_X}..{STRIP_X+STRIP_W}")
print(f"REVIEW rotated bbox {round(2*dx)}x{round(2*dy)} at {REV_X},{REV_Y} -> right {REV_X+2*dx}, bottom {REV_Y+2*dy}")
