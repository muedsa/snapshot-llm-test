"""A03 · System Pulse 监控卡（1280×800）— 修复后最终 DSL 生成器。"""
from __future__ import annotations

import math
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT_DIR = ROOT / "outputs" / RUN_ID / "A03"
TMP_DIR = ROOT / "tmp" / RUN_ID / "A03"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1280, 800
M = 32  # 安全边距
SANS = "Noto Sans CJK SC"

BG = "#0B1220"
CARD = "#1E293B"
CARD_BORDER = "#334155"
INK = "#F8FAFC"
MUTED = "#94A3B8"
C_USAGE = "#38BDF8"
C_LAT = "#A78BFA"
C_SUCC = "#34D399"
C_LIVE = "#EF4444"
C_BAR1 = "#F472B6"
C_BAR2 = "#38BDF8"

ang = math.radians(-8)
c, s = math.cos(ang), math.sin(ang)
CCW8 = f"({c},{s},0,0,{-s},{c},0,0,0,0,1,0,0,0,0,1)"

# 中央说明卡
CW, CH = 500, 150
CX, CY = (W - CW) // 2, (H - CH) // 2

nodes: list[str] = []
nodes.append(f'<Container width="{W}" height="{H}" color="{BG}"/>')

# 标题
nodes.append(
    f'<Positioned left="{M}" top="{M}" width="800" height="56">'
    f'<Container color="transparent"><Text fontSize="44" color="{INK}" fontFamily="{SANS}" '
    f'fontStyle="BOLD" softWrap="false" maxLines="1">System Pulse</Text></Container></Positioned>'
)

# LIVE 标签 96×36，右上，避开标题（标题宽约 320px，标签从右侧 32px 起）
LIVE_W, LIVE_H = 96, 36
LIVE_X, LIVE_Y = W - M - LIVE_W, M
nodes.append(
    f'<Positioned left="{LIVE_X}" top="{LIVE_Y}" width="{LIVE_W}" height="{LIVE_H}">'
    f'<Container color="{C_LIVE}" borderRadius="8" alignment="CENTER">'
    f'<Text fontSize="20" color="#FFFFFF" fontFamily="{SANS}" fontStyle="BOLD" '
    f'softWrap="false" maxLines="1">LIVE</Text></Container></Positioned>'
)

# 三个等宽指标卡
KPI_Y = M + 72
KPI_H = 200
KPI_GAP = 24
KPI_W = (W - 2 * M - 2 * KPI_GAP) // 3
kpis = [
    ("USAGE", "72", "%", C_USAGE, "CPU / MEM 综合"),
    ("LATENCY", "148", " ms", C_LAT, "P95 响应"),
    ("SUCCESS", "99.2", "%", C_SUCC, "近 1 小时"),
]
for i, (label, value, unit, col, sub) in enumerate(kpis):
    x = M + i * (KPI_W + KPI_GAP)
    nodes.append(
        f'<Positioned left="{x}" top="{KPI_Y}" width="{KPI_W}" height="{KPI_H}">'
        f'<Container color="{CARD}" borderRadius="16" border="1 SOLID {CARD_BORDER}" '
        f'padding="(20,24)">'
        f'<Column crossAxisAlignment="START" mainAxisSize="MIN">'
        f'<Text fontSize="22" color="{MUTED}" fontFamily="{SANS}" letterSpacing="2" '
        f'softWrap="false" maxLines="1">{label}</Text>'
        f'<Container height="10"/>'
        f'<Row crossAxisAlignment="BASELINE" textBaseline="ALPHABETIC" mainAxisSize="MIN">'
        f'<Text fontSize="56" color="{col}" fontFamily="{SANS}" fontStyle="BOLD" '
        f'softWrap="false" maxLines="1">{value}</Text>'
        f'<Text fontSize="24" color="{col}" fontFamily="{SANS}" softWrap="false" '
        f'maxLines="1">{unit}</Text>'
        f'</Row>'
        f'<Container height="10"/>'
        f'<Text fontSize="18" color="{MUTED}" fontFamily="{SANS}" softWrap="false" '
        f'maxLines="1">{sub}</Text>'
        f'</Column></Container></Positioned>'
    )

# 中央说明卡 + 背景-only 模糊
# 先画穿过卡片两侧边界的彩色细条（Stack 中位于卡片下层）
BAR_H = 6
bar_top = CY + CH // 2 - BAR_H // 2
nodes.append(
    f'<Positioned left="0" top="{bar_top}" width="{W}" height="{BAR_H}">'
    f'<Container gradientType="LINEAR" gradientColors="{C_BAR1},{C_BAR2},{C_BAR1}" '
    f'gradientBegin="CENTER_LEFT" gradientEnd="CENTER_RIGHT"/></Positioned>'
)

# 说明卡：ClipRRect 限定 BackdropFilter 作用区域
nodes.append(
    f'<Positioned left="{CX}" top="{CY}" width="{CW}" height="{CH}">'
    f'<ClipRRect borderRadius="24">'
    f'<BackdropFilter sigmaX="12" sigmaY="12">'
    f'<Container width="{CW}" height="{CH}" color="#FFFFFF33" alignment="CENTER" '
    f'border="1 SOLID #FFFFFF55" borderRadius="24">'
    f'<Text fontSize="28" color="{INK}" fontFamily="{SANS}" fontStyle="BOLD" '
    f'softWrap="false" maxLines="1">Background-only blur</Text>'
    f'</Container></BackdropFilter></ClipRRect></Positioned>'
)

# REVIEW 标签 160×56，右下，视觉逆时针 8°，白底 20% 不透明，文字不透明 24px
REV_W, REV_H = 160, 56
REV_X, REV_Y = W - M - REV_W, H - M - REV_H
nodes.append(
    f'<Positioned left="{REV_X}" top="{REV_Y}" width="{REV_W}" height="{REV_H}">'
    f'<Transform matrix="{CCW8}" origin="(80,28)">'
    f'<Container width="{REV_W}" height="{REV_H}" color="#FFFFFF33" borderRadius="10" '
    f'border="1 SOLID #FFFFFF66" alignment="CENTER">'
    f'<Text fontSize="24" color="#FFFFFF" fontFamily="{SANS}" fontStyle="BOLD" '
    f'softWrap="false" maxLines="1">REVIEW</Text>'
    f'</Container></Transform></Positioned>'
)

# 左下状态脚注
nodes.append(
    f'<Positioned left="{M}" top="{H - M - 24}" width="600" height="24">'
    f'<Container color="transparent"><Text fontSize="16" color="{MUTED}" fontFamily="{SANS}" '
    f'softWrap="false" maxLines="1">采样间隔 5s · 深底 #0B1220 · 安全边距 32</Text>'
    f'</Container></Positioned>'
)

dsl = (
    f'<Snapshot type="png" background="{BG}">'
    f'<Container width="{W}" height="{H}">'
    '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
    + "".join(nodes)
    + "</Stack></Container></Snapshot>"
)
(TMP_DIR / "system-pulse.snapshot").write_text(dsl, encoding="utf-8")
print("wrote", (TMP_DIR / "system-pulse.snapshot").relative_to(ROOT).as_posix(), len(dsl))
print(f"geometry: KPI y={KPI_Y} h={KPI_H} w={KPI_W}; card=({CX},{CY},{CW},{CH}); "
      f"LIVE=({LIVE_X},{LIVE_Y}); REVIEW=({REV_X},{REV_Y}); bar_top={bar_top}")
