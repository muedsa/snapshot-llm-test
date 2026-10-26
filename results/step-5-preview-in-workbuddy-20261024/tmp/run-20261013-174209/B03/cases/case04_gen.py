#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-04 双色马拉松数据海报（1080×1350，4:5 社交竖版）。
虚构赛事「2026 鹭洲湿地半程马拉松」（2026-10-25 周日）完赛数据海报。
主导手法：ColorFiltered 嵌套双色调（内层 SCREEN 靛蓝映射暗部 ×
外层 MULTIPLY 暖黄映射亮部，作用于 PIL 生成的灰度赛照 dataUri 与渐变
Container）+ Flex（Row/Expanded/Column）大数字排版 + 偏移框破版。
所有赛事数据为虚构演示数据（case.md 已注明）。"""
from __future__ import annotations

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import *  # noqa: F403
from b03_common import (T, positioned, assert_canvas, WARN,
                        INK, INK_DEEP, TEAL, PAPER, PAPER_DIM, ORANGE,
                        ORANGE_DEEP, INDIGO, REED, SKY, WHITE,
                        SERIF, SANS, MONO, INTER,
                        rect, chip)

W, H = 1080, 1350
IMG = Path(__file__).resolve().parent / "race-photo.png"
B64 = base64.b64encode(IMG.read_bytes()).decode("ascii")
DURI = f"data:image/png;base64,{B64}"

C_WARM = "#F6DEA0"    # 双色调暖端（高光）
C_COOL = "#16294F"    # 双色调冷端（暗部，加深穿透 MULTIPLY）


def duotone_img(w, h, fit="COVER"):
    return (f'<ColorFiltered color="{C_WARM}" blendMode="MULTIPLY">'
            f'<ColorFiltered color="{C_COOL}" blendMode="SCREEN">'
            f'<Image dataUri="{DURI}" width="{w}" height="{h}" '
            f'fit="{fit}"/></ColorFiltered></ColorFiltered>')


def dsl() -> str:
    n = []
    n.append(rect(0, 0, W, H, PAPER))

    # ================= 报头 =================
    T("鹭洲湿地半程马拉松", 64, 62, 700, 56, 44, INK, "LEFT", "BOLD",
      SERIF, nodes=n)
    T("LUHOU WETLAND HALF MARATHON · 2ND EDITION", 64, 124, 620, 20, 13,
      REED, "LEFT", "NORMAL", MONO, spacing=3, nodes=n)
    T("2026.10.25 周日 · 晴 18°C", 64, 124, 952, 20, 15, INK, "RIGHT",
      "NORMAL", MONO, nodes=n)
    n.append(rect(64, 162, 952, 3, INK))
    n.append(rect(64, 172, 952, 1, "#1E3B2F33"))

    # ================= 主图：双色调赛照 + 偏移框 =================
    n.append(rect(74, 194, 952, 480, INK))          # 偏移实体框（破版感）
    n.append(positioned(64, 184, 952, 480, duotone_img(952, 480)))
    # 图上标签
    n.append(chip(88, 208, 208, 34, "FINISHER POSTER", PAPER, INK, 13,
                  family=MONO))
    T("赛道途经 · 鹭洲路 — 湿地主环线 — 观鸟屋 — 苇岸餐厅折返", 88, 616,
      760, 24, 14, "#FFF6E0CC", "LEFT", "NORMAL", SANS, nodes=n)

    # ================= 距离带（墨底 + 暖色大数字） =================
    n.append(rect(64, 692, 952, 128, INK))
    T("21.0975", 96, 706, 480, 92, 76, C_WARM, "LEFT", "BOLD", INTER,
      nodes=n)
    T("KM", 408, 744, 120, 40, 28, PAPER, "LEFT", "BOLD", INTER, nodes=n)
    T("赛道全长 · 累计爬升 86 m", 620, 716, 360, 30, 17, "#FFFFFFD9",
      "RIGHT", "NORMAL", SANS, nodes=n)
    T("环湖生态赛道 · 补给站 6 处", 620, 748, 360, 26, 13, "#FFFFFF8C",
      "RIGHT", "NORMAL", SANS, nodes=n)

    # ================= 数据行（Flex 大数字） =================
    stats = [("3,742", "完赛人数 · 人"), ("1:58:26", "平均完赛成绩"),
             ("96.9%", "完赛率"), ("420", "志愿者 · 名")]
    cells = []
    for i, (num, lab) in enumerate(stats):
        if i:
            cells.append('<SizedBox width="1" height="86">'
                         f'<Container width="1" height="86" '
                         f'color="#1E3B2F2E"/></SizedBox>')
        cells.append(
            f'<Expanded flex="1"><Column crossAxisAlignment="START" '
            f'mainAxisSize="MIN">'
            f'<Text fontSize="54" fontStyle="BOLD" color="{INDIGO}" '
            f'fontFamily="{INTER}" softWrap="false">{num}</Text>'
            f'<SizedBox width="1" height="12"/>'
            f'<Text fontSize="13" color="{REED}" '
            f'fontFamily="{SANS}">{lab}</Text>'
            f'</Column></Expanded>')
    n.append(positioned(64, 856, 952, 150,
                        f'<Row crossAxisAlignment="CENTER">'
                        f'{"".join(cells)}</Row>'))
    T("* 报名 3,860 人，完赛 3,742 人；成绩为芯片净成绩", 64, 1006, 952, 20,
      12, REED, "LEFT", "NORMAL", SANS, nodes=n)

    # ================= 成绩分布条形图 =================
    T("完赛成绩分布 · 净成绩", 64, 1052, 500, 26, 18, INK, "LEFT", "BOLD",
      SANS, nodes=n)
    T("占比 %", 816, 1056, 200, 22, 12, REED, "RIGHT", "NORMAL", SANS,
      nodes=n)
    bins = [("≤ 1:30", 8), ("1:30–1:45", 17), ("1:45–2:00", 31),
            ("2:00–2:15", 26), ("≥ 2:15", 18)]
    base_y, max_h = 1244, 96
    n.append(rect(64, base_y, 952, 2, INK))
    for i, (lab, v) in enumerate(bins):
        bx = 132 + i * 172
        bh = max_h * v / 31.0
        color = ORANGE if i == 2 else INDIGO
        n.append(rect(bx, base_y - bh, 112, bh, color))
        T(f"{v}%", bx, base_y - bh - 28, 112, 24, 15, INK, "CENTER",
          "BOLD", MONO, nodes=n)
        T(lab, bx - 20, base_y + 12, 152, 22, 13, REED, "CENTER", "NORMAL",
          MONO, nodes=n)

    # ================= 页脚 =================
    n.append(rect(64, 1302, 952, 1, "#1E3B2F33"))
    T("主办：临州市体育局 · 鹭洲湿地公园管理处", 64, 1316, 620, 22, 13,
      REED, "LEFT", "NORMAL", SANS, nodes=n)
    T("下一场 · 2027 鹭洲湿地马拉松（全程）2027.04.18", 64, 1316, 952, 22,
      13, INK, "RIGHT", "BOLD", SANS, nodes=n)

    out = snapshot(W, H, n, PAPER)
    probs = assert_canvas(out, W, H)
    for p in probs + WARN:
        print("WARN:", p)
    return out


if __name__ == "__main__":
    s = dsl()
    out = Path(__file__).resolve().parent / "case-04-v01.snapshot"
    out.write_text(s, encoding="utf-8")
    print("wrote", out, len(s), "B")
