#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B02 case-02 · 访客导览手册内页跨页（1754×1240 横，A4 横放比例）。

左页：园区简介 + 三条推荐动线（里程按右页示意图几何比例折算）+ 观鸟月历；
右页：动线示意图（路线几何避开水域，比例尺与路线长度一致）+ 服务设施图标表；
底部通栏：文明观鸟守则 6 条。页脚带复用品牌组件。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b02_common import *  # noqa: F403
from b02_common import _bar_between

W, H = 1754, 1240
LX0, LX1 = 40, 850
RX0, RX1 = 904, 1714
GUT = 877
LAKE = (1300, 380)   # 湖心
LAKE_R = 75          # 湖半径（d=150）

# ---------------------------------------------------------------- 动线几何
WP_A = [(1270, 582), (1420, 449), (1470, 380), (1420, 311), (1300, 240),
        (1180, 311), (1130, 380), (1180, 449), (1240, 555), (1270, 582)]
WP_B = [(1270, 582), (1130, 540), (1055, 430), (1090, 300), (1230, 245),
        (1430, 245), (1560, 270), (1615, 345)]
WP_C = [(1270, 582), (1360, 570), (1395, 525), (1340, 500), (1250, 505),
        (1185, 530), (1195, 570), (1270, 582)]


def _len(pts):
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
               for i in range(len(pts) - 1))


def _clear(pts):
    """折线到湖心的最小距离（须 > LAKE_R）。"""
    best = 1e9
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy
        if L2 < 1e-9:
            continue
        t = max(0, min(1, ((LAKE[0] - x0) * dx + (LAKE[1] - y0) * dy) / L2))
        px, py = x0 + t * dx, y0 + t * dy
        best = min(best, math.hypot(px - LAKE[0], py - LAKE[1]))
    return best


def dsl() -> str:
    len_a, len_b, len_c = _len(WP_A), _len(WP_B), _len(WP_C)
    for nm, pts in (("A", WP_A), ("B", WP_B), ("C", WP_C)):
        assert _clear(pts) > LAKE_R + 8, f"动线 {nm} 侵入水域"
    km_per_px = 3.8 / len_b          # B 芦苇线 3.8 km 为基准
    km_a = round(len_a * km_per_px, 1)
    km_b = round(len_b * km_per_px, 1)
    km_c = round(len_c * km_per_px, 1)
    bar_km = 0.5
    bar_px = bar_km / km_per_px

    n = []
    n.append(rect(0, 0, W, H, PAPER))
    n.append(rect(GUT, 40, 2, 1000, REED))

    # ---------------- 页眉 ----------------
    n += logo(96, 78, 56, INK, ORANGE, TEAL)
    n.append(text_node("访客导览手册", 140, 52, 400, 34, 28, INK, "LEFT", "BOLD", SERIF))
    n.append(text_node("园区动线 · 设施 · 守则", 140, 88, 400, 24, 18, TEAL))
    n.append(text_node("P04 – P05", RX1 - 200, 56, 200, 28, 22, INK, "RIGHT", "NORMAL", MONO))
    n.append(hline(LX0, 128, LX1 - LX0, REED, 1.5))
    n.append(hline(RX0, 128, RX1 - RX0, REED, 1.5))

    # ---------------- 左页：简介 ----------------
    n.append(text_node("园区简介", LX0, 158, 400, 34, 26, INK, "LEFT", "BOLD", SERIF))
    n.append(text_block(wrap("鹭洲湿地位于临州市滨江区，总面积 862 公顷，是东亚—澳大利西亚候鸟迁飞路线上的重要停歇地。园区已记录鸟类 287 种，其中国家一级保护鸟类 6 种、二级 38 种；高等植物 426 种，含原生芦苇群落 210 公顷。", 21, LX1 - LX0 - 20),
                        LX0, 204, LX1 - LX0 - 10, 21, 32, INK, "LEFT", "NORMAL", SANS))
    n.append(text_block(wrap("访客中心设生态展厅、观鸟屋与自然教育教室，全部栈道无障碍通行。建议游览时长 2–4 小时，请按推荐动线参观，共同保护湿地生态。", 21, LX1 - LX0 - 20),
                        LX0, 340, LX1 - LX0 - 10, 21, 32, TEAL, "LEFT", "NORMAL", SANS))

    # ---------------- 左页：三条动线 ----------------
    n.append(text_node("推荐动线", LX0, 420, 400, 34, 26, INK, "LEFT", "BOLD", SERIF))
    routes = [
        ("A", "环湖线", km_a, 45, "平缓木栈道，适合全家同行；可观湖面雁鸭与鹭鸟", ORANGE),
        ("B", "芦苇线", km_b, 50, "穿越芦苇荡至北观鸟台；最佳观鸟 15:00–17:00", TEAL),
        ("C", "无障碍短环", km_c, 25, "全平路面，适合轮椅与婴儿车；设 3 处休息亭", INDIGO),
    ]
    y = 466
    for code, name, km, mins, desc, color in routes:
        n += badge(LX0 + 34, y + 44, 44, code, color, PAPER, 22)
        n.append(text_node(f"动线 {code} · {name}", LX0 + 72, y + 6, 500, 32, 24, INK, "LEFT", "BOLD", SANS))
        n.append(text_node(f"{km:.1f} km · 约 {mins} 分钟", LX0 + 72, y + 42, 500, 28, 20, color, "LEFT", "BOLD", MONO))
        n.append(text_block(wrap(desc, 19, LX1 - LX0 - 90), LX0 + 72, y + 74, LX1 - LX0 - 80, 19, 26, REED))
        n.append(hline(LX0, y + 106, LX1 - LX0, REED, 1))
        y += 120
    n.append(text_node("里程按右页示意图比例折算，误差 ±0.1 km", LX0, y + 6, 700, 24, 17, REED))

    # ---------------- 左页：观鸟月历 ----------------
    n.append(text_node("观鸟与景观月历", LX0, 890, 500, 30, 24, INK, "LEFT", "BOLD", SERIF))
    months = [("1–2 月", "越冬雁鸭 · 灰鹤"), ("3–4 月", "候鸟北迁高峰"),
              ("5–6 月", "繁殖季 · 请远观"), ("7–8 月", "荷花 · 萤火虫"),
              ("9–10 月", "南迁 · 芦苇金黄"), ("11–12 月", "豆雁抵达 · 黄金期")]
    for k, (m, ev) in enumerate(months):
        col, row = k % 3, k // 3
        cx = LX0 + col * 270
        cy = 932 + row * 48
        n += card(cx, cy, 260, 40, WHITE, REED, 10, 1.2)
        n.append(text_node(m, cx + 14, cy + 9, 76, 24, 17, TEAL, "LEFT", "BOLD", MONO))
        n.append(text_node(ev, cx + 96, cy + 9, 156, 24, 16, INK))

    # ---------------- 右页：动线示意图 ----------------
    mx0, my0, mx1, my1 = RX0, 158, RX1, 640
    n += card(mx0, my0, mx1 - mx0, my1 - my0, WHITE, REED, 20, 2)
    n.append(text_node("园区动线示意图", mx0 + 36, my0 + 26, 500, 32, 24, INK, "LEFT", "BOLD", SERIF))
    n.append(text_node("示意图 · 非精确测绘", mx1 - 300, my0 + 32, 264, 24, 17, REED, "RIGHT"))
    # 水域 + 岛
    n.append(circle(LAKE[0], LAKE[1], 150, SKY))
    n.append(circle(LAKE[0], LAKE[1], 52, PAPER))
    n += ring_segment(LAKE[0], LAKE[1], 55, 51, 0, 360, TEAL, 36)
    # 保育区（东南角虚线框）
    cax, cay, caw, cah = 1490, 500, 165, 100
    for i in range(9):
        t = i / 8
        n.append(_bar_between(cax + caw * t, cay, cax + caw * t + 12, cay, 2, REED, 1))
        n.append(_bar_between(cax + caw * t, cay + cah, cax + caw * t + 12, cay + cah, 2, REED, 1))
        n.append(_bar_between(cax, cay + cah * t, cax, cay + cah * t + 10, 2, REED, 1))
        n.append(_bar_between(cax + caw, cay + cah * t, cax + caw, cay + cah * t + 10, 2, REED, 1))
    n.append(text_node("保育区", cax, cay + 34, caw, 24, 18, REED, "CENTER", "BOLD"))
    n.append(text_node("请勿进入", cax, cay + 58, caw, 24, 16, REED, "CENTER"))
    # 访客中心
    n.append(rect(1200, 560, 140, 44, INK, 6))
    n.append(text_node("访客中心", 1200, 572, 140, 24, 17, PAPER, "CENTER"))
    # 三条动线
    n += polyline(WP_A, 7, ORANGE, 3.5)
    n += polyline(WP_B, 7, TEAL, 3.5)
    n += polyline(WP_C, 7, INDIGO, 3.5)
    # 起终点徽章
    n += badge(1270, 582, 34, "起", INK, PAPER, 16)
    n += badge(1615, 345, 34, "望", TEAL, PAPER, 16)
    # 北箭头（左下）
    n.append(_bar_between(975, 560, 975, 520, 3, INK))
    n.append(_bar_between(975, 520, 967, 532, 3, INK))
    n.append(_bar_between(975, 520, 983, 532, 3, INK))
    n.append(text_node("北", 958, 566, 34, 22, 15, INK, "CENTER"))

    # ---------------- 图例条 ----------------
    ly = 648
    n.append(rect(RX0, ly, RX1 - RX0, 64, PAPER_DIM, 12))
    chips = [("A", "环湖线", km_a, ORANGE, 936), ("B", "芦苇线", km_b, TEAL, 1146),
             ("C", "短环", km_c, INDIGO, 1356)]
    for code, name, km, color, x in chips:
        n.append(rect(x, ly + 16, 30, 6, color))
        n.append(text_node(f"{code} {name} {km:.1f} km", x + 40, ly + 8, 240, 24, 18, INK))
    n.append(text_node(f"比例尺 {bar_km:g} km", RX1 - 210, ly + 8, 170, 22, 15, INK, "RIGHT"))
    n.append(rect(RX1 - 200 - bar_px, ly + 34, bar_px, 6, INK))
    n.append(rect(RX1 - 200 - bar_px / 2, ly + 34, bar_px / 2, 6, PAPER))
    n.append(text_node("起＝访客中心（门票 · 咨询 · 观光车）　望＝北观鸟台", RX0 + 20, ly + 36, 560, 22, 15, REED))

    # ---------------- 右页：服务设施 ----------------
    fy = 740
    n.append(text_node("服务设施", RX0, fy, 400, 30, 24, INK, "LEFT", "BOLD", SERIF))
    fac = ["停车场", "卫生间", "母婴室", "急救站", "餐饮部", "观光车站"]
    fw = (RX1 - RX0) / 6
    for k, name in enumerate(fac):
        cx = RX0 + fw * k + fw / 2
        n.append(circle(cx, fy + 70, 54, PAPER_DIM))
        if k == 0:
            n.append(rect(cx - 16, fy + 54, 32, 22, INK, 4))
            n.append(circle(cx - 8, fy + 62, 5, PAPER))
            n.append(circle(cx + 8, fy + 62, 5, PAPER))
        elif k == 1:
            n.append(circle(cx - 7, fy + 58, 6, INK))
            n.append(circle(cx + 7, fy + 58, 6, INK))
            n.append(rect(cx - 9, fy + 68, 18, 20, INK, 3))
        elif k == 2:
            n.append(circle(cx, fy + 58, 9, INK))
            n.append(_bar_between(cx, fy + 58, cx, fy + 82, 3.5, INK, 1.5))
            n.append(_bar_between(cx, fy + 68, cx - 10, fy + 74, 3, INK, 1.5))
            n.append(_bar_between(cx, fy + 68, cx + 10, fy + 74, 3, INK, 1.5))
        elif k == 3:
            n.append(_bar_between(cx - 12, fy + 54, cx - 12, fy + 86, 5, INK))
            n.append(_bar_between(cx - 24, fy + 62, cx, fy + 62, 5, INK))
        elif k == 4:
            n.append(circle(cx, fy + 64, 13, INK))
            n.append(_bar_between(cx - 13, fy + 80, cx + 13, fy + 80, 4, INK))
        else:
            n.append(rect(cx - 20, fy + 56, 40, 26, INK, 5))
            n.append(circle(cx - 10, fy + 78, 5, PAPER))
            n.append(circle(cx + 10, fy + 78, 5, PAPER))
        n.append(text_node(name, cx - 60, fy + 104, 120, 24, 18, INK, "CENTER"))
    n.append(text_node("设施位置见示意图与现场指引牌", RX0, fy + 142, 600, 22, 16, REED))

    # ---------------- 底部通栏：文明观鸟守则 ----------------
    ry = 1032
    n.append(rect(LX0, ry, RX1 - LX0, 128, INK, 20))
    n.append(text_node("文明观鸟守则", LX0 + 36, ry + 18, 400, 30, 22, PAPER, "LEFT", "BOLD", SERIF))
    rules = ["请勿大声喧哗，与鸟类保持 20 米以上距离", "请勿投喂野生动物，勿带入宠物入园",
             "请勿进入滩涂、保育区与未开放区域", "请勿使用无人机拍摄，避免惊扰鸟类",
             "垃圾请带离园区或按标识分类投放", "请勿采摘植物，勿踩踏保育围栏内植被"]
    for k, r in enumerate(rules):
        col, row = k % 2, k // 2
        n.append(circle(LX0 + 56 + col * 830, ry + 48 + row * 26, 7, ORANGE))
        n.append(text_node(r, LX0 + 74 + col * 830, ry + 36 + row * 26, 700, 24, 18, PAPER))

    # ---------------- 页脚带 ----------------
    n += footer_band(0, H - 60, W, 60, "LZ-P02 · 导览手册跨页", "第 4–5 页", INK, PAPER, 34)
    return snapshot(W, H, n, PAPER)


if __name__ == "__main__":
    text = dsl()
    out = Path(__file__).resolve().parent / "case-02-v01.snapshot"
    out.write_text(text, encoding="utf-8")
    print("wrote", out, len(text), "bytes")
