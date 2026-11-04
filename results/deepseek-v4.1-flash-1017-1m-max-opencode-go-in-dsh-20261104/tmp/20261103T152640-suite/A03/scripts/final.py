# -*- coding: utf-8 -*-
"""A03 final v2: System Pulse card with background-only blur built from layers."""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402

TASK = "A03"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)

BG = "#0B1220"
TEXT = "#F1F5F9"
TEXT2 = "#93A4BC"
MUTED = "#5C6E88"
CARD = "#111C31"
BORDER = "#1F2E4A"
CYAN = "#22D3EE"
AMBER = "#FBBF24"
GREEN = "#34D399"
VIOLET = "#A78BFA"

W, H, M = 1280, 800, 32
CX, CY, CW, CH, RAD = 390, 444, 500, 150, 24
RX, RY, RW, RH = 1078, 698, 160, 56

th = math.radians(-8)
c, s = math.cos(th), math.sin(th)
MATRIX = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"

METRICS = [("USAGE", "72%", CYAN), ("LATENCY", "148 ms", AMBER), ("SUCCESS", "99.2%", GREEN)]
STRIPES = [(466, "#22D3EE"), (492, "#FBBF24"), (540, "#A78BFA"), (566, "#34D399")]
SX0, SX1 = 250, 1030

p: list[str] = []
p.append(K.rect(-160, -200, 620, 520, radius=260,
                gradient='gradientType="RADIAL" gradientColors="#0E7490B3,#0E749000" gradientCenter="CENTER" gradientRadius="0.5"'))
p.append(K.rect(700, 380, 700, 600, radius=300,
                gradient='gradientType="RADIAL" gradientColors="#4338CA80,#4338CA00" gradientCenter="CENTER" gradientRadius="0.5"'))

p.append(K.text(M, 32, "System Pulse", size=44, color=TEXT, bold=True, spacing=-0.4))
p.append(K.rect(M, 100, W - 2 * M, 1, color="#1B2942"))
p.append(K.rect(W - M - 96, 34, 96, 36, color="#F43F5E22", radius=18, border="1 SOLID #F43F5E66"))
p.append(K.rect(W - M - 96 + 18, 52, 8, 8, color="#FB7185", radius=4))
p.append(K.text(W - M - 96 + 34, 42, "LIVE", width=56, size=18, color="#FECDD3", bold=True, spacing=1.2))

card_w, gap, card_y, card_h = 389.0, 24.0, 128.0, 176.0
for i, (label, value, accent) in enumerate(METRICS):
    x = M + i * (card_w + gap)
    p.append(K.rect(x, card_y, card_w, card_h, color=CARD, radius=18, border=f"1 SOLID {BORDER}"))
    p.append(K.rect(x, card_y + 22, 4, card_h - 44, color=accent, radius=2))
    p.append(K.text(x + 30, card_y + 30, label, size=28, color=TEXT2, spacing=1.6))
    p.append(K.text(x + 30, card_y + 84, value, size=28, color=TEXT, bold=True, spacing=-0.2))
    p.append(K.rect(x + 30, card_y + 140, 48, 4, color=accent, radius=2))

# sharp stripe segments outside the card, blurred band inside it
for y, color in STRIPES:
    p.append(K.rect(SX0, y, CX - SX0, 8, color=color))
    p.append(K.rect(CX + CW, y, SX1 - (CX + CW), 8, color=color))

blur_stripes = "".join(
    f'<Positioned left="-32" top="{y - CY}"><Container width="{CW + 64}" height="8" color="{color}"/></Positioned>'
    for y, color in STRIPES
)
p.append(f'<Positioned left="{CX}" top="{CY}">'
         f'<ClipRRect borderRadius="{RAD}" clipBehavior="ANTI_ALIAS">'
         f'<SizedBox width="{CW}" height="{CH}">'
         f'<ImageFiltered sigmaX="10" sigmaY="10" tileMode="CLAMP">'
         f'<Stack alignment="TOP_LEFT" clipBehavior="NONE">{blur_stripes}</Stack>'
         f'</ImageFiltered></SizedBox></ClipRRect></Positioned>')

p.append(K.rect(CX, CY, CW, CH, color="#FFFFFF14", radius=RAD, border="1 SOLID #FFFFFF38"))
p.append(K.text(CX, CY + 58, "Background-only blur", width=CW, size=28, color="#FFFFFF", bold=True,
                align="CENTER"))

p.append(f'<Positioned left="{RX}" top="{RY}">'
         f'<Transform matrix="{MATRIX}" alignment="CENTER">'
         f'<Container width="{RW}" height="{RH}" color="#FFFFFF33" radius="10" '
         f'border="1 SOLID #FFFFFF55" alignment="CENTER">'
         f'<Text fontSize="24" color="#FFFFFF" fontStyle="BOLD" letterSpacing="1.2">REVIEW</Text>'
         f'</Container></Transform></Positioned>')

p.append(K.text(M, H - M - 18, "System Pulse · 1280 × 800 · 卡内背景经 ImageFiltered 高斯模糊（σ=10），文字层独立绘制",
                size=16, color=MUTED))

dsl = K.document(W, H, p, background=BG)
path = OUT / "system-pulse.snapshot"
path.write_text(dsl, encoding="utf-8")
warn = K.drain_warnings()
logger = api.TaskLogger(TASK, TMP)
rec = logger.render(path, OUT / "system-pulse.png", "final v2: layered background-only blur")
print("final:", rec["http_status"], rec["response_bytes"], rec["elapsed_s"], "s")
for x in warn:
    print(x)
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:2000])
    raise SystemExit(1)
print("size:", api.measure_png(OUT / "system-pulse.png"))
