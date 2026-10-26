#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-05 志愿者招募海报（1080×1920 竖）。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b02_common import *  # noqa: F403
from b02_common import _bar_between

W, H = 1080, 1920

ROLES = [
    ("观鸟讲解员", "bird", "在栈道为访客讲解当季鸟种与观察要点。",
     "每月 2 次 · 每次 3 小时", "通过周六通识培训"),
    ("苇丛巡护员", "reed", "协助巡护员巡查苇丛，记录异常痕迹。",
     "每月 1 次 · 上午 3 小时", "18 岁以上 · 体力良好"),
    ("自然教育助教", "kid", "协助儿童探索课程，带队小组活动。",
     "每月 3 次 · 每次 2 小时", "喜欢孩子 · 有耐心"),
    ("监测数据员", "data", "整理鸟类监测记录、校对照片档案。",
     "每月 2 次 · 居家线上完成", "能熟练使用表格软件"),
]

TRAININGS = [
    ("10 / 25", "周六 09:30", "园区生态通识", "访客中心教室"),
    ("11 / 08", "周六 09:30", "观鸟技巧与讲解", "栈道实地实训"),
    ("11 / 22", "周六 09:30", "安全与应急规范", "访客中心教室"),
]


def role_icon(cx, cy, s, icon):
    out = []
    if icon == "bird":
        out += bird(cx, cy + s * 0.1, s * 0.5, INK, max(s * 0.09, 2.0), 0.72)
        out.append(_bar_between(cx, cy - s * 0.3, cx + s * 0.05, cy + s * 0.1, s * 0.05, INK, 0))
    elif icon == "reed":
        for i, hh in enumerate([0.7, 1.0, 0.8, 0.9]):
            bx = cx - s * 0.33 + i * s * 0.22
            out.append(_bar_between(bx, cy + s * 0.35, bx + s * 0.05, cy + s * 0.35 - s * hh,
                                    s * 0.06, INK, s * 0.03))
            out.append(circle(bx + s * 0.05, cy + s * 0.35 - s * hh, s * 0.07, ORANGE))
    elif icon == "kid":
        out.append(circle(cx, cy - s * 0.22, s * 0.3, INK))
        out += ring_segment(cx, cy + s * 0.28, s * 0.42, s * 0.36, 20, 160, INK, 16)
        out.append(_bar_between(cx - s * 0.42, cy + s * 0.42, cx + s * 0.42, cy + s * 0.42,
                                s * 0.07, ORANGE, s * 0.035))
    else:
        hs = [0.5, 0.8, 0.35, 1.0, 0.6, 0.9, 0.45, 0.7, 0.3, 0.85, 0.55, 0.65]
        for r in range(3):
            for c in range(4):
                h = hs[r * 4 + c]
                bx = cx - s * 0.42 + c * s * 0.24
                by = cy + s * 0.35 - h * s * 0.8
                out.append(rect(bx, by, s * 0.14, h * s * 0.8,
                                TEAL if (r + c) % 2 else INK, s * 0.03))
    return out


def dsl():
    n = []
    # 页眉
    n.append(rect(0, 0, W, 170, INK))
    n += logo(86, 86, 100, PAPER, ORANGE, PAPER)
    n.append(text_node("鹭洲湿地访客中心 · 志愿者计划", 152, 52, 700, 32, 24, PAPER, "LEFT", "NORMAL", SERIF))
    n.append(text_node("VOLUNTEER PROGRAM · 2026 秋冬季", 152, 94, 700, 24, 14, SKY, "LEFT", "NORMAL", INTER, spacing=1.6))
    n.append(text_node("第 7 期招募", W - 280, 60, 240, 28, 18, ORANGE, "RIGHT", "NORMAL", SANS))
    # 主主张
    n.append(rect(0, 170, W, 400, PAPER))
    n += wave(W / 2, 300, 720, 14, TEAL, 4, 3)
    n.append(text_node("把周末交给苇荡与雁群", (W - (W - 120)) / 2, 216, W - 120, 60, 46, INK, "CENTER", "NORMAL", SERIF))
    n.append(text_node("你需要的不只是一次志愿服务，", (W - (W - 160)) / 2, 300, W - 160, 40, 24, INK, "CENTER", "NORMAL", SERIF))
    n.append(text_node("而是一段与这片湿地共同生长的时光。", (W - (W - 160)) / 2, 348, W - 160, 40, 24, INK, "CENTER", "NORMAL", SERIF))
    n += bird_flock([(300, 440, 16), (360, 420, 20), (430, 448, 14),
                     (640, 436, 18), (720, 424, 22), (790, 450, 13)], INK)
    n.append(text_node("现有在册志愿者 86 人 · 累计服务 5,200 小时 · 守护鸟类 213 种",
                       (W - (W - 160)) / 2, 500, W - 160, 28, 17, REED, "CENTER", "NORMAL", SANS))
    # 岗位 2x2
    n.append(text_node("四类岗位 · 总有一款适合你", 60, 586, 600, 34, 26, INK, "LEFT", "NORMAL", SERIF))
    cw, ch = 480, 300
    for i, (name, icon, desc, tm, req) in enumerate(ROLES):
        cx0 = 60 + (i % 2) * (cw + 0)
        cy0 = 632 + (i // 2) * (ch + 12)
        n += card(cx0, cy0, cw, ch, WHITE, TEAL, 18, 2.0)
        n.append(rect(cx0, cy0, 96, ch, TEAL, 18))
        n.append(rect(cx0 + 74, cy0, 22, ch, TEAL))
        n.append(text_node(str(i + 1), cx0, cy0 + 18, 96, 40, 30, PAPER, "CENTER", "NORMAL", MONO))
        n += role_icon(cx0 + 48, cy0 + 120, 64, icon)
        n.append(text_node("岗位", cx0, cy0 + ch - 46, 96, 22, 13, SKY, "CENTER", "NORMAL", SANS))
        tx = cx0 + 116
        n.append(text_node(name, tx, cy0 + 18, cw - 136, 34, 24, INK, "LEFT", "NORMAL", SERIF))
        n.append(text_node(desc, tx, cy0 + 62, cw - 136, 24, 14, INK, "LEFT", "NORMAL", SANS))
        n.append(rect(tx, cy0 + 128, cw - 136, 56, SKY, 10))
        n.append(text_node("时长 " + tm, tx + 12, cy0 + 136, cw - 160, 22, 14, INK, "LEFT", "NORMAL", MONO))
        n.append(text_node("要求 " + req, tx + 12, cy0 + 158, cw - 160, 22, 14, INK, "LEFT", "NORMAL", MONO))
        n.append(rect(tx, cy0 + 196, 130, 34, ORANGE, 17))
        n.append(text_node("我要报名", tx, cy0 + 202, 130, 24, 14, PAPER, "CENTER", "NORMAL", SANS))
        n.append(text_node("扫码选择岗位 " + str(i + 1), tx + 146, cy0 + 204, cw - 280, 22, 12, REED, "LEFT", "NORMAL", SANS))
    # 培训日程
    ty = 1256
    n.append(text_node("新志愿者培训日程", 60, ty, 600, 34, 26, INK, "LEFT", "NORMAL", SERIF))
    n.append(text_node("完成任一场次即获得上岗资格", 60, ty + 38, 600, 24, 15, REED, "LEFT", "NORMAL", SANS))
    for i, (d, t, name, place) in enumerate(TRAININGS):
        cy0 = ty + 76 + i * 92
        n += card(60, cy0, W - 120, 80, WHITE, TEAL, 14, 1.5)
        n.append(rect(60, cy0, 150, 80, INK, 14))
        n.append(rect(198, cy0, 12, 80, INK))
        n.append(text_node(d, 60, cy0 + 16, 150, 26, 17, PAPER, "CENTER", "NORMAL", MONO))
        n.append(text_node(t, 60, cy0 + 44, 150, 22, 13, SKY, "CENTER", "NORMAL", MONO))
        n.append(text_node(name, 232, cy0 + 14, 500, 30, 21, INK, "LEFT", "NORMAL", SANS))
        n.append(text_node("地点 " + place, 232, cy0 + 46, 500, 24, 14, TEAL, "LEFT", "NORMAL", SANS))
        n.append(rect(W - 240, cy0 + 22, 150, 36, PAPER_DIM, 18))
        n.append(text_node("剩余 " + str(18 - i * 5) + " 席", W - 240, cy0 + 29, 150, 24, 14, INK, "CENTER", "NORMAL", SANS))
    # 报名方式
    ay = ty + 76 + 3 * 92 + 10
    n += card(60, ay, W - 120, 120, INK, INK, 18)
    n += logo(130, ay + 60, 76, PAPER, ORANGE, PAPER)
    n.append(text_node("扫码报名 · 选择岗位与场次", 200, ay + 24, 640, 32, 24, PAPER, "LEFT", "NORMAL", SERIF))
    n.append(text_node("报名截止 10 月 23 日 18:00 · 咨询 0512-6688-2046", 200, ay + 66, 640, 26, 15, SKY, "LEFT", "NORMAL", SANS))
    n.append(rect(W - 300, ay + 30, 180, 60, ORANGE, 30))
    n.append(text_node("立即报名", W - 300, ay + 44, 180, 32, 20, PAPER, "CENTER", "NORMAL", SANS))
    # 页脚
    n += footer_band(0, H - 56, W, 56, "LZ-P05 · 招募海报", "05 / 10", INK, PAPER, 32)
    return snapshot(W, H, n, PAPER)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "case-05-v01.snapshot"
    out.write_text(dsl(), encoding="utf-8")
    print("wrote", out)
