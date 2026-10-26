#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-03 体检报告：三十个箭头里只有三件事要紧（9:16 手机 1080×1920）。

问题：体检报告几十项指标带上下箭头，普通人无法分级。
重构：三级色带（关注/复查/就医）从 32 项里捞出 4 项放大讲解，
每项带「参考区间条」把数值画在区间上的位置；其余收进「已核对」统计；
右侧行动时间轴按 7 天/3 个月/1 年分桶。

数据纪律：参考区间为常用体检区间（以报告单所印为准）；
患者数据为演示数据（虚构）。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from b06_common import *  # noqa: F403
from b06_common import (T, snapshot, rect, circle, hline, vline, polyline,  # noqa: E501
                        grad, PAPER_BG, PAPER_CARD, INK_TXT, INK_DIM,
                        INK_FAINT, LINE, TEAL, TEAL_DEEP, TEAL_SOFT,
                        AMBER, AMBER_SOFT, RED, RED_DEEP, RED_SOFT,
                        GREEN, GREEN_SOFT, GREY, GREY_SOFT, BLUE, BLUE_SOFT,
                        PURPLE, PURPLE_SOFT,
                        card, badge, tag, kicker, foot_note, page_head,
                        bullet, arrow_r, arrow_d, hbar, donut, vbar)

W, H = 1080, 1920
M = 48

# ------------------------------------------------ 演示数据（虚构）
LEVEL = {  # 等级 → (色, 浅底, 深字)
    "关注": (AMBER, AMBER_SOFT, "#8A5A14"),
    "复查": ("#D2691E", "#FBEADB", "#8A4210"),
    "就医": (RED, RED_SOFT, RED_DEEP),
}
# (指标, 数值文本, 单位, 参考区间文本, 区间几何 lo/hi/marker, 等级, 三句话)
ITEMS = [
    ("血尿酸", "480", "μmol/L", "参考 150–416", 150, 416, 480, "关注",
     "身体代谢嘌呤后的产物，经肾排出。",
     "长期偏高可能析出尿酸盐结晶，先伤肾、后伤关节。",
     "3 个月内复查；少喝啤酒和海鲜汤；每天喝水 2 L。"),
    ("低密度脂蛋白胆固醇", "3.9", "mmol/L", "参考 ＜3.4", 1.5, 3.4, 3.9,
     "复查",
     "把胆固醇运进血管的「运输车」。",
     "偏高会让胆固醇沉积在血管壁，是斑块的原料。",
     "挂心内科门诊，由医生评估是否用药；少吃饱和脂肪。"),
    ("乳腺结节 BI-RADS", "4A", "类", "3 类及以下常规随访", 0, 3, 4.6,
     "就医",
     "影像报告对结节恶性风险的分类，4A 为低度可疑。",
     "4A 类恶性可能约 2–10%，需要专科判断而非等待。",
     "3 个月内挂乳腺外科；带报告原件，必要时增强检查。"),
    ("体重指数 BMI", "26.4", "kg/m²", "中国成人 18.5–23.9", 18.5, 23.9, 26.4,
     "关注",
     "体重（kg）除以身高（m）的平方。",
     "24–27.9 为超重，与血脂、尿酸、血压偏高同向作用。",
     "本年度目标 −3 kg；先改晚餐主食量，不必剧烈运动。"),
]
BUCKETS = [
    ("7 天内", TEAL_DEEP, TEAL_SOFT, [
        "预约乳腺外科门诊（带报告原件）",
        "把复查项目加入日历：尿酸 + 血脂",
    ]),
    ("3 个月内", "#8A4210", "#FBEADB", [
        "乳腺外科就诊完成，按医嘱复查",
        "尿酸复查看是否降到 420 以下",
    ]),
    ("1 年内", BLUE, BLUE_SOFT, [
        "体重 −3 kg；血脂、尿酸、血压三项一起看趋势",
        "明年体检加做同一机构，保证可比",
    ]),
]


def range_bar(x, y, w, lo, hi, mark, color, nodes, label_lo="", label_hi=""):
    """参考区间条：轨道 + 参考区（lo–hi）+ 数值标记。"""
    # 轨道全宽代表 [0, max(hi*1.35, mark*1.08)] 便于显示越界值
    dom_hi = max(hi * 1.35, mark * 1.08)
    fx = lambda v: x + w * (v / dom_hi)
    rect(x, y, w, 14, GREY_SOFT, radius=7, nodes=nodes)
    rect(fx(lo), y, fx(hi) - fx(lo), 14, "#D5DED8", radius=7, nodes=nodes)
    # 数值标记
    mx = fx(mark)
    rect(mx - 3, y - 7, 6, 28, color, radius=3, nodes=nodes)
    if label_lo:
        T(label_lo, x, y + 22, 200, 18, 10.5, INK_FAINT, nodes=nodes)
    if label_hi:
        T(label_hi, x + w - 200, y + 22, 200, 18, 10.5, INK_FAINT,
          "RIGHT", nodes=nodes)
    return mx


def dsl() -> str:
    n: list[str] = []
    n.append(rect(0, 0, W, H, "#F2F5F4"))

    # ================= 页头 =================
    page_head(M, 44, W - 2 * M, "03", "体检报告：只有三件事要紧",
              "32 项指标 · 4 项需要行动 · 其余 28 项已核对无异常",
              nodes=n, num_bg=BLUE, title_size=32)
    badge(M, 122, 150, 28, "演示数据 · 虚构", BLUE_SOFT, BLUE, 12.5,
          nodes=n)
    tag(M + 162, 122, "报告日 2026-09-18", "#EDF1EF", INK_DIM, 12.5,
        nodes=n)

    # ================= A. 结论卡 =================
    ay = 172
    rect(M, ay, W - 2 * M, 168, "#FFFFFF", 20, nodes=n)
    T("本次结论", M + 28, ay + 20, 200, 24, 14, BLUE, "LEFT", "BOLD",
      nodes=n)
    T("32 项里捞出 4 项", M + 28, ay + 46, 420, 40, 30, INK_TXT, "LEFT",
      "BOLD", nodes=n)
    T("按「关注 / 复查 / 就医」三级分开，各怎么办写在卡片上。",
      M + 28, ay + 94, 620, 22, 12.5, INK_DIM, nodes=n)
    # 三级计数
    counts = {"关注": 2, "复查": 1, "就医": 1}
    cx0 = M + 660
    for i, (lv, cnt) in enumerate(counts.items()):
        col, soft, deep = LEVEL[lv]
        bx0 = cx0 + i * 118
        rect(bx0, ay + 34, 104, 100, soft, 14, nodes=n)
        T(str(cnt), bx0, ay + 44, 104, 46, 36, deep, "CENTER", "BOLD",
          nodes=n)
        T(lv, bx0, ay + 96, 104, 24, 14, deep, "CENTER", "BOLD", nodes=n)

    # ================= B. 四项放大 =================
    by = 372
    kicker(M, by, "需要行动的四项（按紧急程度排序）", BLUE, 16, nodes=n)
    iy = by + 34
    for i, (name, val, unit, ref, lo, hi, mark, lv, s1, s2, s3) in \
            enumerate(ITEMS):
        col, soft, deep = LEVEL[lv]
        y0 = iy + i * 292
        rect(M, y0, W - 2 * M, 276, "#FFFFFF", 18, nodes=n)
        rect(M, y0, 8, 276, col, radius=4, nodes=n)
        # 名称 + 等级
        T(name, M + 28, y0 + 20, 460, 30, 21, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        badge(M + W - 2 * M - 108, y0 + 20, 80, 28, lv, col, "#FFFFFF",
              13, nodes=n)
        # 大数值
        T(val, M + 28, y0 + 56, 300, 76, 62, deep, "LEFT", "BOLD", nodes=n)
        T(unit, M + 28 + 150, y0 + 100, 120, 24, 15, INK_DIM, nodes=n)
        # 参考区间条
        rb_x = M + 360
        rb_w = W - 2 * M - 360 - 40
        T(ref, rb_x, y0 + 56, rb_w, 22, 12.5, INK_DIM, nodes=n)
        range_bar(rb_x, y0 + 88, rb_w, lo, hi, mark, col, n,
                  label_lo=str(lo), label_hi=str(hi))
        # 三句话
        rows = [("这是什么", s1), ("为什么要紧", s2), ("去做什么", s3)]
        for j, (lab, txt) in enumerate(rows):
            ry = y0 + 148 + j * 40
            T(lab, M + 28, ry, 90, 22, 12, deep, "LEFT", "BOLD", nodes=n)
            T(txt, M + 126, ry, W - 2 * M - 160, 42, 13.5, INK_TXT,
              nodes=n)

    # ================= C. 行动时间轴 =================
    cy = 1600
    kicker(M, cy, "行动时间轴", BLUE, 16, nodes=n)
    for i, (lab, col, soft, acts) in enumerate(BUCKETS):
        y0 = cy + 34 + i * 62
        rect(M, y0, W - 2 * M, 52, soft, 12, nodes=n)
        badge(M + 12, y0 + 10, 104, 32, lab, col, "#FFFFFF", 13, nodes=n)
        for j, a in enumerate(acts):
            T(a, M + 132 + j * 420, y0 + 14, 410, 24, 13, INK_TXT,
              nodes=n)

    # ================= D. 折叠统计 =================
    fy = 1832
    rect(M, fy, W - 2 * M, 56, "#E8EEF5", 12, nodes=n)
    T("其余 28 项已逐项核对：血常规、肝肾功能、血糖、血脂四项、心电图、"
      "腹部超声均在参考区间内。", M + 24, fy + 16, W - 2 * M - 48, 24, 12.5,
      "#3C5871", nodes=n)

    return snapshot(W, H, n, "#F2F5F4")
