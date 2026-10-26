#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-10 产品发布电子邀请函 1080×1080（1:1 方卡）。
鹭洲湿地公园「秋迁观鸟季启幕仪式」邀请函（公园系列活动，时间地点与
B02 规范一致：2026-11-20 周五 16:00–17:30 淡季开放时段内）。
主导手法：WidgetSpan 行内嵌件（日期徽章/图标/菱形分隔）+ 嵌套 Span 混排
（关键词橙/数字 Inter/引文衬线）+ Noto Color Emoji 彩色表情 +
decoration 层级（UNDERLINE/LINE_THROUGH 组合）。
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import *  # noqa: F403
from b03_common import (T, positioned, rect, circle, assert_canvas, WARN,
                        grad, rich_text, clip_path,
                        INK, TEAL, PAPER, ORANGE, INDIGO, REED, SKY, WHITE,
                        SERIF, SANS, MONO, INTER, snapshot)

W, H = 1080, 1080
BG = "#12233A"          # 夜蓝卡纸
BG2 = "#0D1929"
CARD = "#F5EFE3"        # 米色内卡
INK_C = "#1F2A38"
CREAM = "#F5EFE3"
GOLD = "#D9A441"
ORANGE_C = "#D96C3D"
DIMC = "#93A5B8"
EMOJI = "Noto Color Emoji"


def leaf_path(w: float, h: float, n: int = 20) -> str:
    tip = (w * 0.5, 0.0)
    base = (w * 0.5, h)
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * tip[0] + 2 * (1 - t) * t * w + t ** 2 * base[0]
        y = (1 - t) ** 2 * tip[1] + 2 * (1 - t) * t * h * 0.30 + t ** 2 * base[1]
        pts.append((x, y))
    for i in range(n, -1, -1):
        t = i / n
        x = (1 - t) ** 2 * tip[0] + 2 * (1 - t) * t * 0.0 + t ** 2 * base[0]
        y = (1 - t) ** 2 * tip[1] + 2 * (1 - t) * t * h * 0.30 + t ** 2 * base[1]
        pts.append((x, y))
    return "M " + " L ".join(f"{px:.2f},{py:.2f}" for px, py in pts) + " Z"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def chip_widget(xml):
    return ("WIDGET", {"xml": xml, "align": "BOTTOM"})


def dsl() -> str:
    n = []

    # ================= 卡纸底 =================
    n.append(grad(0, 0, W, H, [BG, BG2], stops=[0, 1], gtype="LINEAR",
                  begin="TOP_CENTER", end="BOTTOM_CENTER", nodes=n))
    # 顶部 RADIAL 微光
    n.append(grad(340, -120, 400, 400, ["#3E6E8E33", "#3E6E8E00"],
                  stops=[0, 1], gtype="RADIAL", center="CENTER",
                  radius=0.8, nodes=n))
    # 细纸纹
    y = 40.0
    while y < H - 30:
        n.append(rect(40, y, W - 80, 1, "#FFFFFF05"))
        y += 40

    # ================= 双线装饰框 =================
    n.append(rect(40, 40, W - 80, H - 80, "transparent").replace(
        'color="transparent"',
        'color="transparent" border="1 SOLID #D9A44155"'))
    n.append(rect(54, 54, W - 108, H - 108, "transparent").replace(
        'color="transparent"',
        'color="transparent" border="1 SOLID #D9A44133"'))

    # ================= 顶部徽标行 =================
    n.append(clip_path(96, 96, 34, 52, leaf_path(34, 52),
                       f'<Container width="34" height="52" '
                       f'color="{GOLD}"/>', nodes=n))
    T("鹭洲湿地公园", 144, 100, 400, 30, 22, CREAM, "LEFT", "BOLD", SERIF,
      spacing=4, nodes=n)
    T("INVITATION · 启幕邀请", 144, 132, 400, 20, 12, DIMC, "LEFT",
      "NORMAL", INTER, spacing=3, nodes=n)
    # 右上角 Emoji 串（Noto Color Emoji 字体，probe-v02 实证）
    T("🦢🍂🦆", 800, 100, 200, 40, 30, CREAM, "RIGHT", "NORMAL", EMOJI,
      nodes=n)
    T("NO.2026-11", 800, 146, 200, 20, 12, DIMC, "RIGHT", "NORMAL",
      MONO, spacing=2, nodes=n)

    # ================= 主标题 =================
    T("秋迁观鸟季", 90, 236, 900, 120, 92, CREAM, "LEFT", "BOLD", SERIF,
      spacing=10, shadow="0 6 24 #00000055", nodes=n)
    # 空心描边副题（STROKE 霓虹/活版感）
    T("启幕仪式", 90, 356, 900, 120, 92, GOLD, "LEFT", "BOLD", SERIF,
      spacing=10, stroke=GOLD, stroke_w=1.8,
      decoration="UNDERLINE", decoration_color=ORANGE_C, nodes=n)

    # ================= 邀请正文（WidgetSpan + 嵌套 Span 混排） =================
    rich_text(90, 520, 900, 150, 19, "#D8E2EC",
              [("我们诚邀您出席 ", {}),
               ("秋迁观鸟季", {"color": GOLD, "style": "BOLD",
                              "family": SERIF}),
               ("启幕仪式——与 ", {}),
               ("287", {"color": ORANGE_C, "style": "BOLD",
                        "family": INTER}),
               (" 种候鸟一起，送走今年最后一批北方的客人。", {})],
              family=SANS, height=1.85, nodes=n)
    rich_text(90, 640, 900, 150, 19, "#D8E2EC",
              [("当日有 ", {}),
               chip_widget(f'<Container width="30" height="30" '
                           f'shape="CIRCLE" color="{GOLD}">'
                           f'<Container width="30" height="30" '
                           f'shape="CIRCLE" color="transparent" '
                           f'alignment="CENTER">'
                           f'<Text fontSize="15" color="{BG}" '
                           f'fontFamily="{INTER}" fontStyle="BOLD">'
                           f'4</Text></Container></Container>'),
               (" 场定点观测讲解、夜观装备体验与茶点；凭此函可携 ", {}),
               ("1", {"color": ORANGE_C, "style": "BOLD", "family": INTER}),
               (" 名同行人入场。", {})],
              family=SANS, height=1.85, nodes=n)

    # ================= 信息条（WidgetSpan 日期徽章） =================
    rich_text(90, 786, 900, 90, 26, CREAM,
              [chip_widget(f'<Container width="56" height="56" '
                          f'shape="CIRCLE" color="{ORANGE_C}">'
                          f'<Container width="56" height="56" '
                          f'shape="CIRCLE" color="transparent" '
                          f'alignment="CENTER">'
                          f'<Text fontSize="26" color="{CREAM}" '
                          f'fontFamily="{SERIF}" fontStyle="BOLD">'
                          f'20</Text></Container></Container>'),
               ("  十一月 · 周五 ", {"family": SERIF, "style": "BOLD"}),
               ("16:00 – 17:30", {"family": INTER, "style": "BOLD",
                                 "color": GOLD}),
               ("   ·   鹭洲湿地公园 科普馆露台", {"family": SERIF})],
              family=SANS, height=1.6, nodes=n)
    # 菱形分隔装饰行（WidgetSpan 小菱形 + 文字）
    rich_text(90, 880, 900, 30, 15, DIMC,
              [chip_widget(f'<Container width="10" height="10" '
                          f'shape="CIRCLE" color="{GOLD}"/>'),
               ("  秋迁最佳观测期 11–12 月 · 建议携带望远镜与防风外套  ",
                {}),
               chip_widget(f'<Container width="10" height="10" '
                           f'shape="CIRCLE" color="{GOLD}"/>')],
              family=SANS, nodes=n)

    # ================= RSVP 行动区 =================
    n.append(grad(90, 936, 420, 64, ["#E8B04B", "#D96C3D"],
                  stops=[0, 1], gtype="LINEAR", begin="CENTER_LEFT",
                  end="CENTER_RIGHT", radius_corner=32,
                  shadow="0 10 28 0 #D96C3D40", nodes=n))
    T("确认出席 · RSVP", 90, 954, 420, 28, 20, "#3A2408", "CENTER",
      "BOLD", SANS, spacing=3, nodes=n)
    T("0512-6688-0000", 550, 954, 300, 28, 19, CREAM, "LEFT", "BOLD",
      INTER, spacing=2, nodes=n)
    T("回复截止 11 月 18 日", 550, 984, 300, 20, 12, DIMC, "LEFT",
      "NORMAL", SANS, nodes=n)
    # 右下 Emoji + 装饰
    T("🦆", 880, 930, 100, 60, 44, CREAM, "CENTER", "NORMAL", EMOJI,
      nodes=n)
    T("凭此函入场 · 儿童需成人陪同", 90, 1016, 900, 22, 13, DIMC,
      "LEFT", "NORMAL", SANS, nodes=n)

    # ================= 页脚 =================
    n.append(rect(90, 1004, 900, 1, "#D9A44133"))
    T("TIDE · LINZHOU WETLAND PARK", 90, 1040, 500, 20, 11, "#7E93A8",
      "LEFT", "NORMAL", INTER, spacing=3, nodes=n)
    T("秋迁观鸟季启幕仪式 · 2026.11.20", 490, 1040, 500, 20, 11, "#7E93A8",
      "RIGHT", "NORMAL", SANS, nodes=n)

    out = snapshot(W, H, n, BG)
    probs = assert_canvas(out, W, H)
    for p in probs + WARN:
        print("WARN:", p)
    return out


if __name__ == "__main__":
    s = dsl()
    out = Path(__file__).resolve().parent / "case-10-v01.snapshot"
    out.write_text(s, encoding="utf-8")
    print("wrote", out, len(s), "B")
