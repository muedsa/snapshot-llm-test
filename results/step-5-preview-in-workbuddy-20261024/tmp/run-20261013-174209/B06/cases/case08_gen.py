#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-08 垃圾分类易错榜（A4 竖版 1240×1754，贴垃圾桶上方/厨房门后）。

问题：四分类口诀听过就忘；易错物品每次现查现疑。
重构：四桶色卡（定义+投放要求）→ 易错榜 Top10（物品+归属+一句为什么）
→ 三问决策树 → 投放前处理四件事。

数据纪律：四分法与投放要求依据北京市政府《垃圾分类您都门儿清了吗》
与《北京市生活垃圾管理条例》（2026-10-24 访问）；具体以当地条例为准。
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

W, H = 1240, 1754
M = 64

# 四桶（北京四分法）
BINS = [
    ("厨余垃圾", "#5E7F3E", "#EDF2E4", "易腐：菜叶、瓜皮、剩饭、茶渣",
     "沥干水分；纯流质（牛奶）倒下水道"),
    ("可回收物", "#2E6FA8", "#E4EDF6", "纸、塑料、玻璃、金属、织物、电器",
     "清洁干燥；纸箱压扁；玻璃包裹轻放"),
    ("有害垃圾", "#C0392B", "#F9E5E1", "电池、灯管、温度计、药品、油漆",
     "器物完整；药品连带包装一并投放"),
    ("其他垃圾", "#6E7873", "#ECEEEB", "以上三类之外：纸巾、陶片、大骨、猫砂",
     "沥干后投放；难以辨识的投这里"),
]
# 易错榜（物品, 归属桶索引, 一句为什么）
TRAPS = [
    ("大棒骨", 3, "难腐烂，不属于厨余——这是最多人错的一件"),
    ("过期药品", 2, "连带包装一并投有害，别冲下水道"),
    ("5 号/7 号干电池", 3, "无汞碱性电池归其他；充电/纽扣电池才是有害"),
    ("猫砂", 3, "混合物不可回收也不易腐，属其他垃圾"),
    ("用过的纸巾", 3, "水溶性强、被污染，不可回收"),
    ("碎陶瓷", 3, "属其他垃圾；包裹后轻放防割伤"),
    ("快递纸箱", 1, "拆胶带、压扁，干净纸板才值钱"),
    ("旧衣服", 1, "织物属可回收物；先洗净再投放"),
    ("节能灯", 2, "易碎含汞，连带包装或包裹后轻放"),
    ("剩饭剩菜", 0, "易腐但必须沥水，别连汤带水倒入"),
]
# 三问决策树（问题, 判定, 结果桶索引, 备注）
TREE = [
    ("第一问：它能卖钱吗", "干净的纸 / 塑料 / 玻璃 / 金属 / 织物 / 电器", 1,
     "脏污染后要降级——油纸盒不是可回收物"),
    ("第二问：它有毒有害吗", "电池（充电/纽扣）/ 灯管 / 温度计 / 药品 / 油漆", 2,
     "「有害」看成分不看大小，纽扣电池也是有害"),
    ("第三问：它容易腐烂吗", "食材弃料 / 剩饭 / 瓜皮 / 茶渣 / 蛋壳", 0,
     "容易腐但汤水多：先沥水，纯流质倒下水道"),
    ("三问都不是", "难以辨识、被污染、难降解——大骨、猫砂、陶片", 3,
     "拿不准就投其他垃圾，这比投错更安全"),
]
PREP = [
    ("沥水", "厨余垃圾投放前先沥干，做到无玻璃陶瓷、无金属、无塑料橡胶"),
    ("压扁", "立体包装（瓶罐纸箱）清空清洁后压扁，省空间也防脏臭"),
    ("完整", "有害垃圾保证器物完整；灯管、温度计包裹后轻放"),
    ("连带包装", "过期药品连带包装一并投放；有包装的食品拆包分类"),
]


def bin_badge(x, y, idx, nodes, w=96, h=30):
    name, col, soft, _, _ = BINS[idx]
    badge(x, y, w, h, name, col, "#FFFFFF", 12.5, nodes=nodes)


def dsl() -> str:
    n: list[str] = []
    n.append(rect(0, 0, W, H, "#F6F4EE"))

    # ================= 页头 =================
    page_head(M, 50, W - 2 * M, "08", "垃圾分类易错榜",
              "拿到一件不确定的东西，30 秒走到正确的桶",
              nodes=n, num_bg="#5E7F3E", title_size=32)
    badge(M, 126, 190, 28, "北京四分法", "#EDF2E4", "#5E7F3E", 12.5,
          nodes=n)
    tag(M + 202, 126, "各地口径有差异，以当地条例为准", "#EFEDE6", INK_DIM,
        12, nodes=n)

    # ================= A. 四桶卡 =================
    ay = 176
    kicker(M, ay, "四类桶：一句话定义 + 一条投放要求", "#4A6B2E", 16,
           nodes=n)
    bw = (W - 2 * M - 3 * 20) / 4
    for i, (name, col, soft, define, req) in enumerate(BINS):
        x0 = M + i * (bw + 20)
        rect(x0, ay + 32, bw, 204, PAPER_CARD, 16, nodes=n)
        rect(x0, ay + 32, bw, 8, col, radius=4, nodes=n)
        # 桶形图标（梯形桶身）
        bx0 = x0 + 20
        clip = (f'<Container width="52" height="52" color="{col}"/>')
        from b03_common import clip_path as _cp
        _cp(bx0, ay + 54, 52, 52,
            "M 4,10 L 48,10 L 43,50 L 9,50 Z", clip, viewbox="0 0 52 52",
            nodes=n)
        rect(bx0 + 2, ay + 46, 48, 8, col, radius=4, nodes=n)
        T(name, bx0 + 66, ay + 60, bw - 90, 30, 20, col, "LEFT", "BOLD",
          nodes=n)
        T(define, x0 + 20, ay + 118, bw - 40, 44, 12, INK_TXT, nodes=n)
        hline(x0 + 20, ay + 168, bw - 40, LINE, 1, nodes=n)
        T("投放：" + req, x0 + 20, ay + 176, bw - 40, 40, 11, INK_DIM,
          nodes=n)

    # ================= B. 易错榜 =================
    by = 444
    kicker(M, by, "易错榜 Top 10（按出错频率排）", "#4A6B2E", 16, nodes=n)
    col_w = (W - 2 * M - 24) / 2
    for i, (item, idx, why) in enumerate(TRAPS):
        x0 = M + (i % 2) * (col_w + 24)
        y0 = by + 34 + (i // 2) * 92
        rect(x0, y0, col_w, 80, PAPER_CARD, 12, nodes=n)
        # 排名
        T(f"{i + 1:02d}", x0 + 14, y0 + 24, 44, 30, 20, "#C9CFC4",
          "LEFT", "BOLD", nodes=n)
        T(item, x0 + 62, y0 + 14, 240, 26, 16.5, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(why, x0 + 62, y0 + 44, col_w - 190, 24, 11.5, INK_DIM, nodes=n)
        bin_badge(x0 + col_w - 116, y0 + 24, idx, n)

    # ================= C. 三问决策树 =================
    cy = 970
    kicker(M, cy, "拿不准？按顺序问三个问题", "#4A6B2E", 16, nodes=n)
    ty = cy + 34
    for i, (q, judge, idx, note) in enumerate(TREE):
        y0 = ty + i * 102
        last = (i == len(TREE) - 1)
        card(M, y0, W - 2 * M, 88, "#FBFAF5" if not last else "#F0F2EC",
             12, nodes=n, border_color="#E3E0D5")
        # 问题
        badge(M + 16, y0 + 26, 118, 34, f"第 {i + 1} 问" if not last else
              "都不中", "#5E7F3E", "#FFFFFF", 13, nodes=n)
        T(q, M + 146, y0 + 14, 420, 26, 15.5, INK_TXT, "LEFT", "BOLD",
          nodes=n)
        T(judge, M + 146, y0 + 46, 560, 24, 12, INK_DIM, nodes=n)
        # 结果
        bin_badge(M + W - 2 * M - 130, y0 + 26, idx, n, w=114, h=36)
        T(note, M + W - 2 * M - 130, y0 + 62, 380, 20, 10, INK_FAINT,
          "RIGHT", nodes=n)
        # 向下箭头
        if not last:
            arrow_d(M + 75, y0 + 88, 18, 16, "#9AA79A", nodes=n)

    # ================= D. 投放前四件事 =================
    dy = 1424
    kicker(M, dy, "不管投哪桶，先做这四件事", "#4A6B2E", 16, nodes=n)
    pw = (W - 2 * M - 3 * 18) / 4
    for i, (t, d) in enumerate(PREP):
        x0 = M + i * (pw + 18)
        rect(x0, dy + 32, pw, 138, PAPER_CARD, 14, nodes=n)
        badge(x0 + 16, dy + 48, 96, 32, t, "#5E7F3E", "#FFFFFF", 14,
              nodes=n)
        T(d, x0 + 16, dy + 92, pw - 32, 64, 11.5, INK_DIM, nodes=n)

    # ================= 脚注 =================
    fy = 1630
    hline(M, fy, W - 2 * M, LINE, 1, nodes=n)
    foot_note(M, fy + 12, W - 2 * M, [
        "四分法与投放要求依据：北京市人民政府《垃圾分类您都门儿清了吗》、《北京市生活垃圾管理条例》"
        "（2026-10-24 访问）。",
        "易错榜物品归类按上述条文；各地分类口径可能存在差异（如干电池、大棒骨），请以当地条例为准。",
    ], color=INK_FAINT, size=11, lh=15, nodes=n)

    return snapshot(W, H, n, "#F6F4EE")
