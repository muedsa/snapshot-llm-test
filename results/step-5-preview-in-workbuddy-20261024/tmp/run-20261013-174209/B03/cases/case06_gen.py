#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-06 活版印刷书展海报「活字」1240×1754（A2 竖版）。
临州独立书展 · 第七回（虚构书展，临州市图书馆场地为虚构信息，case.md 注明）。
主导手法：Text STROKE 套印错版 + textShadow 压印 + decoration 装饰线 +
letterSpacing 字距 + height 行距 + 衬线排版；纸纹/套印十字/色条等
活版印刷语汇全部用 DSL 图元构造。
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import *  # noqa: F403
from b03_common import (T, positioned, rect, circle, assert_canvas, WARN,
                        grad,
                        INK, INK_DEEP, TEAL, PAPER, PAPER_DIM, ORANGE,
                        ORANGE_DEEP, INDIGO, REED, SKY, WHITE,
                        SERIF, SANS, MONO, INTER, snapshot)

W, H = 1240, 1754
PAPER_C = "#F1E9D8"   # 米黄纸
INK_C = "#221E1A"     # 活版油墨黑
TEAL_C = "#1F4E5F"    # 套印青
ORANGE_C = "#C8551B"  # 套印橙
FAINT = "#8A7F6E"     # 淡墨


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def reg_mark(x, y, r=10, color=None):
    """套印十字标：外层 Stack 内平铺 Positioned（Positioned 只能直挂 Stack）。
    返回单个 Positioned(Stack) 节点。"""
    c = color or INK_C
    inner = (
        f'<Container width="{2*r}" height="{2*r}" color="transparent" '
        f'shape="CIRCLE" border="1 SOLID {c}55"/>'
        f'<Positioned left="{r-1}" top="{r-9}" width="2" height="18">'
        f'<Container width="2" height="18" color="{c}"/></Positioned>'
        f'<Positioned left="{r-9}" top="{r-1}" width="18" height="2">'
        f'<Container width="18" height="2" color="{c}"/></Positioned>'
        f'<Positioned left="{r-1.5}" top="{r-1.5}" width="3" height="3">'
        f'<Container width="3" height="3" color="{c}"/></Positioned>')
    return positioned(x, y, 2 * r, 2 * r,
                      f'<Stack alignment="TOP_LEFT" fit="EXPAND" '
                      f'clipBehavior="NONE">{inner}</Stack>')


def dsl() -> str:
    n = []

    # ================= 纸底与纸纹 =================
    n.append(rect(0, 0, W, H, PAPER_C))
    # 纸纹：横向细线（每 36px，极低 alpha）
    y = 18.0
    while y < H - 20:
        n.append(rect(0, y, W, 1, "#221E1A0A"))
        y += 36
    # 纸纹：纵向细线（每 44px）
    x = 22.0
    while x < W - 20:
        n.append(rect(x, 0, 1, H, "#221E1A08"))
        x += 44
    # 三角做旧淡墨（RADIAL 渐变盒收于画布内，圆心对齐各角，柔边无硬界）
    n.append(grad(0, 0, 480, 480, ["#221E1A1C", "#221E1A00"],
                  stops=[0, 1], gtype="RADIAL", center="TOP_LEFT",
                  radius=1.0, nodes=n))
    n.append(grad(W - 480, H - 480, 480, 480, ["#221E1A18", "#221E1A00"],
                  stops=[0, 1], gtype="RADIAL", center="BOTTOM_RIGHT",
                  radius=1.0, nodes=n))
    n.append(grad(W - 480, 0, 480, 480, ["#221E1A14", "#221E1A00"],
                  stops=[0, 1], gtype="RADIAL", center="TOP_RIGHT",
                  radius=1.0, nodes=n))

    # 装订齿孔（左缘 6 枚半露圆孔）
    for i in range(6):
        hy = 300 + i * 240
        n.append(positioned(-8, hy, 40, 40,
                            '<Container shape="CIRCLE" color="#E3D9C4" '
                            'border="1 SOLID #221E1A22"/>'))

    # 套印十字标（四角）
    n.append(reg_mark(48, 60))
    n.append(reg_mark(W - 68, 60))
    n.append(reg_mark(48, H - 68))
    n.append(reg_mark(W - 68, H - 68))

    # ================= 顶部题眉 =================
    n.append(rect(120, 132, W - 240, 3, INK_C))
    n.append(rect(120, 142, W - 240, 1, INK_C))
    T("临州独立书展 · 第七回", 120, 158, W - 240, 24, 15, INK_C, "CENTER",
      "NORMAL", SANS, spacing=6, nodes=n)
    T("INDEPENDENT BOOK FAIR · LINZHOU", 120, 188, W - 240, 20, 12, FAINT,
      "CENTER", "NORMAL", INTER, spacing=4, nodes=n)

    # ================= 主标题：活字（三层套印错版） =================
    # 错版层 1：套印青，右偏移 +8
    T("活字", 128 + 8, 268 + 8, 500, 200, 190, TEAL_C, "LEFT", "BOLD",
      SERIF, stroke=TEAL_C, stroke_w=2.0, nodes=n)
    # 错版层 2：套印橙，右偏移 +16（更淡，营造旧版重印）
    T("活字", 128 + 16, 268 + 16, 500, 200, 190, ORANGE_C, "LEFT", "BOLD",
      SERIF, stroke=ORANGE_C, stroke_w=2.0, nodes=n)
    # 压印层：墨黑实心 + 硬凹痕投影
    T("活字", 128, 268, 500, 200, 190, INK_C, "LEFT", "BOLD", SERIF,
      shadow="3 3 0 #221E1A2E", nodes=n)

    # 拉丁副标：STROKE 空心 + 装饰线
    T("LIVE TYPE", 128, 500, 700, 60, 46, PAPER_C, "LEFT", "NORMAL", INTER,
      spacing=14, stroke=INK_C, stroke_w=1.6,
      decoration="UNDERLINE", decoration_color=ORANGE_C, nodes=n)

    # 一句话主张（衬线大字 + 行高）
    T("字是活的，纸是宽的。", 128, 590, 984, 120, 34, INK_C, "LEFT",
      "NORMAL", SERIF, height=1.9, nodes=n)

    # ================= 装饰分隔：细线 + 菱形 =================
    n.append(rect(128, 742, 480, 1, INK_C))
    n.append(rect(W - 608, 742, 480, 1, INK_C))
    n.append(positioned(W / 2 - 9, 733, 18, 18,
                        '<Container shape="CIRCLE" color="transparent" '
                        'border="1.5 SOLID ' + INK_C + '"/>'))
    n.append(positioned(W / 2 - 4, 738, 8, 8,
                        '<Container color="' + ORANGE_C + '"/>'))

    # ================= 信息栏（三栏 + 竖分隔线） =================
    col_w = 320
    cols = [
        ("日期", "2026.11.20", "— 11.22 · 周五至周日", "10:00 – 18:00"),
        ("场地", "临州市图书馆", "中庭 · 二层回廊", "地铁 2 号线图书馆站"),
        ("票务", "免费入场", "现场预约 · 每日 800 名", "工作坊另计"),
    ]
    for i, (lab, big, l1, l2) in enumerate(cols):
        cx = 128 + i * (col_w + 40)
        T(lab, cx, 786, col_w, 20, 13, ORANGE_C, "LEFT", "NORMAL", SANS,
          spacing=8, decoration="OVERLINE", decoration_color=INK_C, nodes=n)
        T(big, cx, 816, col_w, 56, 40, INK_C, "LEFT", "BOLD", SERIF,
          nodes=n)
        T(l1, cx, 884, col_w, 22, 14, FAINT, "LEFT", "NORMAL", SANS,
          nodes=n)
        T(l2, cx, 910, col_w, 22, 14, FAINT, "LEFT", "NORMAL", SANS,
          nodes=n)
        if i < 2:
            n.append(rect(cx + col_w + 20, 780, 1, 150, "#221E1A33"))

    # ================= 八场讲座（编号 + 题目 + 讲者） =================
    n.append(rect(128, 990, W - 256, 1, "#221E1A33"))
    T("讲座 · 八场", 128, 1004, 400, 22, 15, INK_C, "LEFT", "BOLD", SANS,
      spacing=4, nodes=n)
    talks = [
        ("壹", "活字的明天：铅与像素的对话", "沈砚秋 · 字体设计师"),
        ("贰", "一本独立杂志的十年", "《渡口》编辑部"),
        ("叁", "纸上建筑：书籍设计夜校", "顾一鸣 · 书籍设计师"),
        ("肆", "方言入字：造词实验", "阿禾 · 方言保护志愿者"),
    ]
    for i, (num, title, who) in enumerate(talks):
        ty = 1040 + i * 58
        T(num, 128, ty, 44, 40, 26, ORANGE_C, "LEFT", "BOLD", SERIF,
          nodes=n)
        T(title, 184, ty + 2, 660, 34, 21, INK_C, "LEFT", "NORMAL", SERIF,
          nodes=n)
        T(who, 860, ty + 6, 300, 26, 14, FAINT, "LEFT", "NORMAL", SANS,
          nodes=n)
        if i < 3:
            n.append(rect(128, ty + 46, W - 256, 1, "#221E1A1A"))

    # ================= 参展书店名单（三列小字） =================
    n.append(rect(128, 1310, W - 256, 1, "#221E1A33"))
    T("参展书店 · 四十二家", 128, 1324, 500, 22, 15, INK_C, "LEFT", "BOLD",
      SANS, spacing=4, nodes=n)
    shops = [
        "纸上行舟 · 旧书与地图", "慢半拍书局", "野果书店 · 诗歌专门",
        "灯塔文库", "折角角童书店", "无名出版社", "海涯邮局书店",
        "半山散文馆", "十三月刊行", "荒野植物志书店", "烫金旧规 · 装帧样本",
        "城南声音书店", "黑胶与纸", "一寸光阴", "对页咖啡书店",
        "候鸟迁徙书店", "蓝墨水供应站", "旧城旧书店", "无名剧本书房",
        "山海舆图局", "拾字铺", "晚灯书集", "清昼文库", "苔藓书店",
        "逆风邮差书局", "小满绘本书店", "铁皮屋顶书房", "淡水河畔书店",
        "柚子与字", "废墟档案室", "南墙书店", "风物志书店",
        "银盐照相纸书局", "旧钟表书店", "候车室文库", "银杏叶书店",
        "盐田诗歌铺", "木铎书房", "夜航船书店", "霜降书简", "远洋出版社门市",
        "种子书店",
    ]
    col_n = 3
    per = (len(shops) + col_n - 1) // col_n
    for ci in range(col_n):
        chunk = shops[ci * per:(ci + 1) * per]
        # 每行独立 Text + height 行高倍数，Column 纵排
        # 14 行 × 13 × 1.55 ≈ 282px，收于 1362–1644（色条 1662 之前）
        items = "".join(
            f'<Text fontSize="13" color="#4A4238" fontFamily="{SANS}" '
            f'height="1.55">{esc(s)}</Text>' for s in chunk)
        n.append(positioned(128 + ci * 330, 1362, 320, 290,
                            f'<Column crossAxisAlignment="START" '
                            f'mainAxisSize="MIN">{items}</Column>'))

    # ================= 底部：色条 + 印记 =================
    # 印刷色标条
    bar_colors = [INK_C, TEAL_C, ORANGE_C, "#8A7F6E", "#3E6B4F"]
    for i, c in enumerate(bar_colors):
        n.append(rect(128 + i * 60, 1662, 44, 14, c))
    T("四色印张 · 米黄纸 120g", 428, 1660, 400, 20, 11, FAINT, "LEFT",
      "NORMAL", MONO, spacing=2, nodes=n)
    T("NO.07 / 2026", W - 428, 1660, 300, 20, 12, INK_C, "RIGHT",
      "NORMAL", MONO, spacing=3, nodes=n)
    n.append(rect(128, 1696, W - 256, 2, INK_C))
    n.append(rect(128, 1702, W - 256, 1, INK_C))
    T("主办：临州阅读推广中心 · 协办：临州市图书馆（虚构）", 128, 1716,
      760, 20, 11, FAINT, "LEFT", "NORMAL", SANS, nodes=n)
    T("预约：linzhou-bookfair.example / 0512-6600-0700", 128, 1716, W - 256,
      20, 11, FAINT, "RIGHT", "NORMAL", SANS, nodes=n)

    out = snapshot(W, H, n, PAPER_C)
    probs = assert_canvas(out, W, H)
    for p in probs + WARN:
        print("WARN:", p)
    return out


if __name__ == "__main__":
    s = dsl()
    out = Path(__file__).resolve().parent / "case-06-v01.snapshot"
    out.write_text(s, encoding="utf-8")
    print("wrote", out, len(s), "B")
