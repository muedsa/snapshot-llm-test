#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-09 杂志跨页破版特辑 1754×1240（√2 横版跨页）。
虚构生活方式杂志《潮汐》2026 秋季特辑「追潮汐的人」。
主导手法：ClipRect 硬边裁切出血图 + SizedOverflowBox 破界（标题越中缝、
底部色带通栏）+ Positioned 跨栏压图（圆月跨中缝）。
版式数据自洽：左页 40–877、右页 877–1714；中缝 x=877。
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import *  # noqa: F403
from b03_common import (T, positioned, rect, circle, assert_canvas, WARN,
                        grad, rotate,
                        INK, INK_DEEP, TEAL, PAPER, ORANGE, INDIGO, REED,
                        SKY, WHITE, SERIF, SANS, MONO, INTER, snapshot)

W, H = 1754, 1240
GUTTER = 877          # 中缝
PAPER_C = "#F5EFE3"   # 杂志纸
INK_C = "#1F2A38"     # 墨蓝
LAKE = "#2E5A6E"      # 湖蓝
SAND = "#E8D9BE"      # 暖砂
ORANGE_C = "#D96C3D"  # 秋橙
DIM = "#6B7684"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def dsl() -> str:
    n = []

    # ================= 纸底与版心网格 =================
    n.append(rect(0, 0, W, H, PAPER_C))
    # 细网格（版心参考线）
    gx = 87.0
    while gx < W:
        n.append(rect(gx, 0, 1, H, "#1F2A3808"))
        gx += 87
    # 中缝
    n.append(rect(GUTTER, 40, 1, H - 80, "#1F2A3830"))

    # ================= 左页主图（ClipRect 硬边裁切出血图） =================
    scene = (
        # 天
        f'<Container width="820" height="560" gradientType="LINEAR" '
        f'gradientColors="#F2D9B8,#E8B98C,#C98A6B" gradientStops="0,0.55,1" '
        f'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"/>'
        # 日轮
        f'<Positioned left="560" top="150" width="180" height="180">'
        f'<Container width="180" height="180" shape="CIRCLE" '
        f'color="#F7E3B8"/></Positioned>'
        # 远山（两层剪影）
        f'<Positioned left="-40" top="360" width="500" height="220">'
        f'<Container width="500" height="220" shape="CIRCLE" '
        f'color="#B08A7A"/></Positioned>'
        f'<Positioned left="320" top="390" width="560" height="240">'
        f'<Container width="560" height="240" shape="CIRCLE" '
        f'color="#8A6A62"/></Positioned>'
        # 湖面
        f'<Positioned left="0" top="520" width="820" height="340">'
        f'<Container width="820" height="340" gradientType="LINEAR" '
        f'gradientColors="#3E6E7E,#2E5A6E,#24506B" gradientStops="0,0.5,1" '
        f'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"/>'
        f'</Positioned>'
        # 波光（横向短亮线，确定性间隔）
        + "".join(
            f'<Positioned left="{80 + (i * 97) % 640}" top="{560 + i * 26}" '
            f'width="{40 + (i * 13) % 60}" height="3">'
            f'<Container width="{40 + (i * 13) % 60}" height="3" '
            f'color="#BFE0E8AA"/></Positioned>' for i in range(10))
        # 渔船剪影
        + f'<Positioned left="430" top="640" width="150" height="10">'
        f'<Container width="150" height="10" color="#1F2A38" '
        f'borderRadius="5"/></Positioned>'
        f'<Positioned left="500" top="560" width="4" height="80">'
        f'<Container width="4" height="80" color="#1F2A38"/></Positioned>'
        f'<Positioned left="504" top="566" width="46" height="60">'
        f'<Container width="46" height="60" shape="CIRCLE" '
        f'color="#1F2A38"/></Positioned>'
        # 树（左岸）
        f'<Positioned left="60" top="470" width="16" height="120">'
        f'<Container width="16" height="120" color="#2A3B2E"/></Positioned>'
        f'<Positioned left="20" top="400" width="160" height="160">'
        f'<Container width="160" height="160" shape="CIRCLE" '
        f'color="#3E5A44"/></Positioned>'
        # 飞鸟（三只）
        + "".join(
            f'<Positioned left="{bx}" top="{by}" width="{r * 2}" '
            f'height="{r}">'
            f'<Container width="{r * 2}" height="{r}" color="#1F2A38" '
            f'shape="CIRCLE"/></Positioned>'
            for bx, by, r in [(300, 240, 12), (350, 210, 10), (400, 250, 8)]))
    n.append(positioned(40, 140, 820, 860,
                        f'<ClipRect clipBehavior="HARD_EDGE">'
                        f'<Stack alignment="TOP_LEFT" fit="EXPAND" '
                        f'clipBehavior="NONE">{scene}</Stack>'
                        f'</ClipRect>'))

    # ================= 跨栏圆月（Positioned 跨中缝压图） =================
    n.append(circle(GUTTER, 300, 300, "#F7E3B8"))
    n.append(circle(GUTTER, 300, 300, "transparent").replace(
        'color="transparent"',
        'color="transparent" border="2 SOLID #D96C3D55"'))
    # 月面纹理（两个淡圆）
    n.append(circle(GUTTER - 50, 250, 46, "#EFD3A0"))
    n.append(circle(GUTTER + 40, 360, 30, "#EFD3A0"))

    # 右侧竖排刊名（跨栏圆月旁）
    for i, ch in enumerate("潮汐"):
        T(ch, 1080, 170 + i * 56, 60, 56, 34, INK_C, "LEFT", "BOLD",
          SERIF, nodes=n)
    T("TIDE QUARTERLY", 1080, 300, 300, 20, 12, DIM, "LEFT", "NORMAL",
      INTER, spacing=3, nodes=n)
    n.append(rect(1076, 330, 1, 90, "#1F2A3855"))

    # ================= 破版主标题（逐字 Positioned 跨中缝压图） =================
    # 注：SOB 内 Text 会被盒约束压缩（实测墨迹止于盒右缘），故文字破版用
    # 逐字 Positioned；SOB 破版保留给通栏色带（非文字溢出）。
    # 170px SERIF 每字 185px；第 4、5 字越过中缝 877 进入右页
    for i, ch in enumerate("追潮汐的人"):
        T(ch, 80 + i * 185, 1000, 190, 190, 170, INK_C, "LEFT", "BOLD",
          SERIF, nodes=n)

    # ================= 右页文字区 =================
    # 栏目注音行（右页，跟随竖排刊名）
    T("THE TIDE CHASERS · 秋季特辑 · VOL.11", 1080, 430, 600, 30, 22,
      ORANGE_C, "LEFT", "BOLD", INTER, spacing=4, nodes=n)
    # 导语
    T("海水退去时，滩涂上留下一整天的故事。我们跟着四位渔民下了海——",
      940, 490, 740, 60, 20, INK_C, "LEFT", "NORMAL", SERIF, height=1.5,
      nodes=n)
    T("从凌晨三点的缯网，到黄昏最后一舱梭子蟹，潮汐表是他们唯一的钟。",
      940, 550, 740, 40, 20, INK_C, "LEFT", "NORMAL", SERIF, height=1.5,
      nodes=n)
    # 数据条（三数字）
    n.append(rect(940, 620, 740, 2, "#1F2A3830"))
    stats = [("2", "次", "每日潮汐"), ("42", "户", "跟访渔民"), ("11", "年", "记录跨度")]
    for i, (num, unit, lab) in enumerate(stats):
        sx = 940 + i * 250
        T(num, sx, 648, 120, 70, 52, ORANGE_C, "LEFT", "BOLD", SERIF,
          nodes=n)
        T(unit, sx + 92, 690, 40, 24, 14, DIM, "LEFT", "NORMAL", SANS,
          nodes=n)
        T(lab, sx, 726, 200, 22, 13, DIM, "LEFT", "NORMAL", SANS,
          nodes=n)
        if i < 2:
            n.append(rect(sx + 220, 650, 1, 90, "#1F2A3830"))
    # 正文两栏
    body_l = ("　　老陈的船叫「潮生」，船头漆成朱红。他说这名字是父亲取的，"
              "取「潮生而生」的意思——潮水从不迟到，人也不能。")
    body_l2 = ("　　凌晨三点半，缯网下水。浮标的铃铛在雾里响，一声，两声，"
               "像远处村镇的鸡鸣。这一网要守到日出。")
    body_r = ("　　小暑后的滩涂格外慷慨。招潮蟹在洞穴口列队，弹涂鱼甩出"
              "泥浆里的弧线，白鹭单脚立在竹架旁，等一条漏网的跳跳鱼。")
    body_r2 = ("　　「看潮吃饭的人，心里都装着两片海。」老陈收网时说，"
               "「一片在水里，一片在天上。」")
    T(body_l, 940, 790, 360, 150, 14, INK_C, "LEFT", "NORMAL", SANS,
      height=1.9, nodes=n)
    T(body_l2, 940, 950, 360, 120, 14, INK_C, "LEFT", "NORMAL", SANS,
      height=1.9, nodes=n)
    T(body_r, 1330, 790, 360, 150, 14, INK_C, "LEFT", "NORMAL", SANS,
      height=1.9, nodes=n)
    T(body_r2, 1330, 950, 360, 120, 14, INK_C, "LEFT", "NORMAL", SANS,
      height=1.9, nodes=n)

    # ================= 破版通栏色带（SizedOverflowBox 横贯两页） =================
    # 盒 (40,1190,800,50) 装 1700×50 → 从纸左缘通到 1740，贴画布底
    n.append(positioned(40, 1190, 800, 50,
                        f'<SizedOverflowBox width="800" height="50" '
                        f'alignment="CENTER_LEFT">'
                        f'<SizedBox width="1700" height="50">'
                        f'<Container width="1700" height="50" '
                        f'color="{INK_C}"/></SizedBox></SizedOverflowBox>'))
    T("潮汐 · TIDE QUARTERLY", 60, 1204, 500, 24, 14, PAPER_C, "LEFT",
      "BOLD", SERIF, spacing=6, nodes=n)
    T("2026 秋季特辑 · 追潮汐的人", 760, 1206, 500, 22, 13, SAND, "RIGHT",
      "NORMAL", SANS, nodes=n)
    T("P.024 — 031", 1300, 1206, 394, 22, 13, SAND, "RIGHT", "NORMAL",
      MONO, spacing=2, nodes=n)

    # 页脚（避开标题第 5 字跨栏区 820–1010）
    T("本刊文章人物为虚构创作 · 潮汐数据参考近海典型半日潮", 1060, 1150,
      640, 20, 11, DIM, "LEFT", "NORMAL", SANS, nodes=n)

    out = snapshot(W, H, n, PAPER_C)
    probs = assert_canvas(out, W, H)
    for p in probs + WARN:
        print("WARN:", p)
    return out


if __name__ == "__main__":
    s = dsl()
    out = Path(__file__).resolve().parent / "case-09-v01.snapshot"
    out.write_text(s, encoding="utf-8")
    print("wrote", out, len(s), "B")
