# -*- coding: utf-8 -*-
"""A10 透明合成与滤镜语义实验板（1440x1100）。

六格：
  1 红蓝矩形各 50% alpha（#FF000080 / #0000FF80），蓝在上
  2 同样两个不透明矩形放在 Opacity(0.5) 组内
  3 条纹背景 + 圆角卡，仅背景模糊（BackdropFilter）
  4 相同条纹，卡内文字与形状一起子树模糊（ImageFiltered）
  5 ColorFiltered(MULTIPLY) + 子树高斯模糊
  6 同 5 再限定于圆形裁剪

关键：BackdropFilter / ImageFiltered / ColorFiltered 都是单子节点 Widget；
Opacity 也是单子节点。多个构件要用 Stack 承载。
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A10"
OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1440, 1100
SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

BG = "#EEF2F6"
INK = "#0F172A"
INK2 = "#334155"
MUTED = "#64748B"
DARK = "#0F172A"
CARD = "#FFFFFF"
FRAME = "#CBD5E1"

RED = "#FF0000"
BLUE = "#0000FF"
RED_A = "#FF000080"      # 128/255 alpha
BLUE_A = "#0000FF80"
STRIPE_A = "#0F172A"     # 条纹深色
STRIPE_B = "#F8FAFC"     # 条纹浅色
TINT = "#F6B94A"         # 5/6 滤色

CELL_W, CELL_H = 320, 240
GAP = 32
COLS, ROWS = 3, 2
TITLE_H = 96
GRID_W = COLS * CELL_W + (COLS - 1) * GAP
GRID_H = ROWS * CELL_H + (ROWS - 1) * GAP
OX = (W - GRID_W) // 2
OY = TITLE_H + 24


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(s, *, x, y, w, size, color=INK, family=SANS, bold=False, align="LEFT", h=None,
        wrap=True):
    return (
        f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}"'
        + (f' height="{h}"' if h else "")
        + f'><Container color="transparent"><Text fontSize="{size}" fontFamily="{family}"'
        + (' fontStyle="BOLD"' if bold else "")
        + f' color="{color}" textAlign="{align}" softWrap="{"true" if wrap else "false"}"'
        + f' maxLines="1">{esc(s)}</Text></Container></Positioned>'
    )


def box(x, y, w, h, color, *, radius=None, border=None):
    a = ""
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    return f'<Positioned left="{x:.1f}" top="{y:.1f}" width="{w:.1f}" height="{h:.1f}"><Container color="{color}"{a}/></Positioned>'


nodes = [box(0, 0, W, H, BG)]

# ---------- 标题 ----------
nodes.append(box(0, 0, W, TITLE_H - 8, DARK))
nodes.append(box(0, TITLE_H - 11, W, 3, TINT))
nodes.append(txt("看到差异，才能说用对了", x=40, y=20, w=900, size=34, color="#F8FAFC", bold=True))
nodes.append(txt("六格透明合成与滤镜语义实验 · 每格实验区 320x240 白底 · 局部坐标原点为实验区左上外边界",
                 x=40, y=60, w=1000, size=18, color="#94A3B8"))
nodes.append(txt("滤镜 sigmaX = sigmaY = 6", x=W - 40 - 400, y=26, w=400, size=19, color=TINT,
                 align="RIGHT", bold=True))
nodes.append(txt("①② 采样点 (180,100) · ③-⑥ 目视判定并引用 DSL 节点",
                 x=W - 40 - 460, y=54, w=460, size=17, color="#94A3B8", align="RIGHT"))

# ---------- 六格 ----------
origins = {}
for idx in range(6):
    col, row = idx % COLS, idx // COLS
    ox = OX + col * (CELL_W + GAP)
    oy = OY + row * (CELL_H + GAP)
    origins[idx + 1] = [ox, oy]

    # 区外编号与说明
    nodes.append(txt(f"实验 {idx + 1}", x=ox, y=oy - 30, w=140, size=21, color=INK, bold=True))
    # 实验区（白底）
    nodes.append(box(ox, oy, CELL_W, CELL_H, CARD, border=f"1 SOLID {FRAME}"))

    if idx == 0:
        # ① 红蓝各 50% alpha，蓝在上
        nodes.append(box(ox + 40, oy + 40, 160, 120, RED_A))
        nodes.append(box(ox + 120, oy + 80, 160, 120, BLUE_A))
        nodes.append(txt("矩形各设 50% alpha", x=ox + 4, y=oy + CELL_H + 8, w=CELL_W - 8, size=18,
                         color=INK2))
        nodes.append(txt("红 #FF000080 / 蓝 #0000FF80，蓝在上层",
                         x=ox + 4, y=oy + CELL_H + 30, w=CELL_W - 8, size=17, color=MUTED))
    elif idx == 1:
        # ② 不透明红蓝放在 Opacity(0.5) 组内
        nodes.append(
            f'<Positioned left="{ox}" top="{oy}" width="{CELL_W}" height="{CELL_H}">'
            f'<Opacity opacity="0.5">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
            + box(40, 40, 160, 120, RED)
            + box(120, 80, 160, 120, BLUE)
            + "</Stack></Opacity></Positioned>")
        nodes.append(txt("不透明矩形 + 组 opacity=0.5", x=ox + 4, y=oy + CELL_H + 8, w=CELL_W - 8,
                         size=18, color=INK2))
        nodes.append(txt("红蓝均不透明，整组半透明",
                         x=ox + 4, y=oy + CELL_H + 30, w=CELL_W - 8, size=17, color=MUTED))
    elif idx in (2, 3):
        # ③④ 共享同一基础场景：条纹背景 + 圆角卡 + 文字 + 前景形状
        # 条纹：宽 24 深色 + 24 浅色，跨满实验区
        stripes = []
        sx = 0
        toggle = 0
        while sx < CELL_W:
            stripes.append(box(sx, 0, 24, CELL_H, STRIPE_A if toggle % 2 == 0 else STRIPE_B))
            sx += 24
            toggle += 1
        # 前景形状（卡内，清晰）：一个小圆
        fg = box(150, 110, 40, 40, "#0D9488", radius=20)
        # 卡片：局部 (40,40)，240x160，圆角 20
        # ③④ 共用同一卡片外观：白底 + 圆角 + 边框 + 阴影 + 文字 + 前景形状
        card = (
            f'<Positioned left="40" top="40" width="240" height="160">'
            f'<Container color="{CARD}" borderRadius="20" border="1 SOLID #CBD5E1" '
            f'boxShadow="0 4 12 0 #00000022">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
            f'<Positioned left="0" top="52" width="240" height="30">'
            f'<Container color="transparent"><Text fontSize="24" color="{INK}" '
            f'fontFamily="{SANS}" fontStyle="BOLD" textAlign="CENTER" softWrap="false" '
            f'maxLines="1">SHARP / BLUR</Text></Container></Positioned>'
            + fg +
            "</Stack></Container></Positioned>")
        base = "".join(stripes) + card
        if idx == 2:
            # ③ 仅背景模糊：BackdropFilter 读取卡片区域背后的条纹并模糊，
            # 卡片本体用透明底（只保留边框/阴影/文字/前景），使模糊背景可见。
            nodes.append(
                f'<Positioned left="{ox}" top="{oy}" width="{CELL_W}" height="{CELL_H}">'
                f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
                + "".join(stripes)
                # 1) 先模糊卡片覆盖处的背景（限定在圆角区域内）
                + f'<Positioned left="40" top="40" width="240" height="160">'
                  f'<ClipRRect borderRadius="20">'
                  f'<BackdropFilter sigmaX="6" sigmaY="6">'
                  f'<Container width="240" height="160" color="transparent"/>'
                  f'</BackdropFilter></ClipRRect></Positioned>'
                # 2) 再叠加清晰的卡片边框、阴影、文字与前景形状（透明底）
                + f'<Positioned left="40" top="40" width="240" height="160">'
                  f'<Container color="transparent" borderRadius="20" '
                  f'border="1 SOLID #CBD5E1" boxShadow="0 4 12 0 #00000022">'
                  f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
                  f'<Positioned left="0" top="52" width="240" height="30">'
                  f'<Container color="transparent"><Text fontSize="24" color="{INK}" '
                  f'fontFamily="{SANS}" fontStyle="BOLD" textAlign="CENTER" softWrap="false" '
                  f'maxLines="1">SHARP / BLUR</Text></Container></Positioned>'
                  + fg +
                  "</Stack></Container></Positioned>"
                + "</Stack></Positioned>")
            nodes.append(txt("仅背景模糊（BackdropFilter）", x=ox + 4, y=oy + CELL_H + 8,
                             w=CELL_W - 8, size=18, color=INK2))
            nodes.append(txt("条纹背景被模糊，卡内文字与前景形状保持清晰",
                             x=ox + 4, y=oy + CELL_H + 30, w=CELL_W - 8, size=17, color=MUTED))
        else:
            # ④ 子树模糊：ImageFiltered 包住整张卡（含文字与前景）
            nodes.append(
                f'<Positioned left="{ox}" top="{oy}" width="{CELL_W}" height="{CELL_H}">'
                f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
                + "".join(stripes)
                + f'<Positioned left="40" top="40" width="240" height="160">'
                  f'<ImageFiltered sigmaX="6" sigmaY="6">'
                  f'<Container width="240" height="160" color="{CARD}" borderRadius="20" '
                  f'border="1 SOLID #CBD5E1" boxShadow="0 4 12 0 #00000022">'
                  f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
                  f'<Positioned left="0" top="52" width="240" height="30">'
                  f'<Container color="transparent"><Text fontSize="24" color="{INK}" '
                  f'fontFamily="{SANS}" fontStyle="BOLD" textAlign="CENTER" softWrap="false" '
                  f'maxLines="1">SHARP / BLUR</Text></Container></Positioned>'
                  + fg +
                  "</Stack></Container></ImageFiltered></Positioned>"
                + "</Stack></Positioned>")
            nodes.append(txt("子树模糊（ImageFiltered）", x=ox + 4, y=oy + CELL_H + 8,
                             w=CELL_W - 8, size=18, color=INK2))
            nodes.append(txt("背景、文字与前景形状一起被模糊",
                             x=ox + 4, y=oy + CELL_H + 30, w=CELL_W - 8, size=17, color=MUTED))
    else:
        # ⑤⑥ 共享同一基础场景：ColorFiltered(MULTIPLY, #F6B94A) + 子树高斯模糊
        # 内部含透明间隙、深色矩形和阴影；有一处有色形状跨过圆周（半径100，圆心(160,120)）
        inner = (
            # 深色矩形（跨出圆周左上方）
            box(30, 40, 120, 90, "#1E293B", radius=8)
            # 半透明间隙矩形（透明区域，用于观察 MULTIPLY 对透明像素的影响）
            + box(170, 30, 110, 70, "#00000000", radius=8,
                  border="2 SOLID #94A3B8")
            # 中等色块（跨出圆周右下方）
            + box(180, 150, 130, 80, "#0D9488", radius=8)
            # 小圆点
            + box(120, 170, 50, 50, "#DC2626", radius=25)
            # 文字
            + txt("MULTIPLY", x=60, y=110, w=200, size=22, color="#F8FAFC", bold=True,
                  align="CENTER")
        )
        # 注意：ImageFiltered / ColorFiltered / Opacity / ClipOval / ClipRRect / BackdropFilter
        # 都是单子节点 Widget，且其子节点不能是 Positioned（Positioned 需要 StackParentData）。
        # 因此滤镜链的子节点一律用 Stack 承载，由外层 Positioned 负责定位。
        # 基础场景不铺满白底：让实验区自身的白底作为背景，
        # 这样 MULTIPLY 滤色只作用于有色形状与文字，透明间隙保持透明，
        # 才能同时观察「滤色作用范围」与「裁剪边界」。
        base_scene = (
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
            + inner
            + "</Stack>")
        filtered = (
            f'<ColorFiltered color="{TINT}" blendMode="MULTIPLY">'
            f'<ImageFiltered sigmaX="6" sigmaY="6">'
            + base_scene
            + "</ImageFiltered></ColorFiltered>")
        if idx == 4:
            # ⑤ 无圆形裁剪：滤镜链直接作为实验区内容
            nodes.append(
                f'<Positioned left="{ox}" top="{oy}" width="{CELL_W}" height="{CELL_H}">'
                f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
                + box(0, 0, CELL_W, CELL_H, "#FFFFFF")
                + filtered
                + "</Stack></Positioned>")
            nodes.append(txt("ColorFiltered(MULTIPLY) + 子树模糊", x=ox + 4, y=oy + CELL_H + 8,
                             w=CELL_W - 8, size=18, color=INK2))
            nodes.append(txt("滤色 #F6B94A 后再 sigma=6 高斯模糊，无圆形裁剪",
                             x=ox + 4, y=oy + CELL_H + 30, w=CELL_W - 8, size=17, color=MUTED))
        else:
            # ⑥ 同 ⑤ 再限定于圆形裁剪：ClipOval 包住滤镜链
            nodes.append(
                f'<Positioned left="{ox}" top="{oy}" width="{CELL_W}" height="{CELL_H}">'
                f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
                + box(0, 0, CELL_W, CELL_H, "#FFFFFF")
                + f'<Positioned left="60" top="20" width="200" height="200">'
                  f'<ClipOval clipBehavior="ANTI_ALIAS">'
                  + filtered +
                  "</ClipOval></Positioned>"
                + "</Stack></Positioned>")
            nodes.append(txt("同 ⑤ + 圆形裁剪（ClipOval）", x=ox + 4, y=oy + CELL_H + 8,
                             w=CELL_W - 8, size=18, color=INK2))
            nodes.append(txt("圆心局部 (160,120) 半径 100，裁剪边界可检查",
                             x=ox + 4, y=oy + CELL_H + 30, w=CELL_W - 8, size=17, color=MUTED))

dsl = (
    f'<Snapshot type="png" background="{BG}">'
    f'<Container width="{W}" height="{H}">'
    '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
    + "".join(nodes) + "</Stack></Container></Snapshot>"
)
(TMP_DIR / "compositing-lab.snapshot").write_text(dsl, encoding="utf-8")
print("wrote compositing-lab.snapshot", len(dsl))
print("origins:", origins)
