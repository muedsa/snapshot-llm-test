#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-08 捐赠感谢卡（900×1200 竖卡）。
衬线感谢语（行距 1.6+）+ 捐赠人抬头 + 款项用途三行（金额自洽）+ 徽记签名。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b02_common import *  # noqa: F403
from b02_common import _bar_between

W, H = 900, 1200

USES = [
    ("300.00", "2023 秋季候鸟食堂 · 谷物补充 60 公斤"),
    ("200.00", "2 号观鸟点栈道 · 防腐木板更换 24 块"),
    ("100.00", "「小小巡护员」儿童任务卡 · 印制 500 张"),
]

THANKS = [
    "感谢您把一份心意，",
    "留在了这片湿地上。",
    "",
    "苇荡记得每一次雁群的起落，",
    "而我们会记得您的托付。",
]


def dsl():
    n = []
    n.append(rect(0, 0, W, H, PAPER))
    # 邮封适配边框（对折线 + 安全边距）
    n.append(rect(36, 36, W - 72, H - 72, "transparent", 0))
    n.append(rect(36, 36, W - 72, 2.5, TEAL))
    n.append(rect(36, H - 38.5, W - 72, 2.5, TEAL))
    n.append(rect(36, 36, 2.5, H - 72, TEAL))
    n.append(rect(W - 38.5, 36, 2.5, H - 72, TEAL))
    # ---------------- 徽记 + 品牌 ----------------
    n += logo(W / 2, 148, 120, INK, ORANGE, TEAL)
    n.append(text_node("鹭洲湿地访客中心", W / 2 - 220, 236, 440, 30, 20, INK, "CENTER", "NORMAL", SERIF))
    n.append(text_node("LUZHOU WETLAND VISITOR CENTER", W / 2 - 260, 270, 520, 20, 10, TEAL, "CENTER", "NORMAL", INTER, spacing=1.8))
    n += wave(W / 2, 312, 300, 7, ORANGE, 3.5, 2)
    # ---------------- 感谢语（衬线 · 宽行距） ----------------
    ty = 360
    n.append(text_node("致 捐赠人 张禾 先生：", 90, ty, W - 180, 30, 22, INK, "LEFT", "NORMAL", SERIF))
    for i, ln in enumerate(THANKS):
        if ln:
            n.append(text_node(ln, 90, ty + 62 + i * 56, W - 180, 48, 27, INK, "LEFT", "NORMAL", SERIF))
        else:
            n += wave(W / 2, ty + 62 + i * 56 + 24, 200, 5, TEAL, 2.5, 2)
    # ---------------- 款项用途三行 ----------------
    uy = 700
    n.append(rect(90, uy - 16, W - 180, 2, TEAL))
    n.append(text_node("您的捐赠已按以下用途使用", 90, uy + 6, W - 180, 26, 17, INK, "LEFT", "NORMAL", SANS))
    for i, (amt, use) in enumerate(USES):
        cy0 = uy + 48 + i * 54
        n.append(circle(118, cy0 + 17, 8, ORANGE))
        n.append(text_node("¥ " + amt, 140, cy0, 200, 34, 22, ORANGE_DEEP, "LEFT", "NORMAL", MONO))
        n.append(text_node(use, 360, cy0 + 2, W - 450, 28, 18, INK, "LEFT", "NORMAL", SANS))
    # 合计
    n.append(rect(90, uy + 48 + 3 * 54 + 4, W - 180, 2, TEAL))
    n.append(text_node("合计", 140, uy + 48 + 3 * 54 + 14, 200, 30, 18, INK, "LEFT", "NORMAL", SANS))
    n.append(text_node("¥ 600.00", 360, uy + 48 + 3 * 54 + 10, 300, 34, 24, INK, "LEFT", "NORMAL", MONO))
    n.append(text_node("票据编号 LZ-D2023-0917 · 已开具公益捐赠统一票据", 140, uy + 48 + 3 * 54 + 48, W - 280, 22, 13, REED, "LEFT", "NORMAL", SANS))
    # ---------------- 徽记 + 签名 ----------------
    sy = 1030
    n += logo(W / 2, sy + 34, 64, INK, ORANGE, TEAL)
    n.append(text_node("鹭洲湿地保护基金会", W / 2 - 240, sy + 84, 480, 26, 16, INK, "CENTER", "NORMAL", SERIF))
    n.append(text_node("理事长 陈鹭洲 · 谨致", W / 2 - 240, sy + 112, 480, 24, 15, INK, "CENTER", "NORMAL", SERIF))
    n.append(text_node("2023 年 12 月 20 日", W / 2 - 240, sy + 140, 480, 22, 14, REED, "CENTER", "NORMAL", MONO))
    # ---------------- 邮封适配说明 ----------------
    n.append(text_node("卡片规格 180 × 240 mm · 适配标准邮封 · 请沿裁切线折叠",
                       W / 2 - 340, H - 74, 680, 20, 11, REED, "CENTER", "NORMAL", SANS))
    return snapshot(W, H, n, PAPER)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "case-08-v01.snapshot"
    out.write_text(dsl(), encoding="utf-8")
    print("wrote", out)
