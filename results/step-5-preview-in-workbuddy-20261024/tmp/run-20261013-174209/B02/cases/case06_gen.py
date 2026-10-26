#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-06 秋季迁徙季活动海报（1080×1350，4:5 社交竖版）。
「秋迁季」主题：芦苇 + 三层雁阵 + 3 场活动卡 + 报名入口。"""
from __future__ import annotations

import datetime

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b02_common import *  # noqa: F403
from b02_common import _bar_between

W, H = 1080, 1350

EVENTS = [
    dict(name="雁阵观测上午场", date="11 月 02 日", time="08:30 – 10:00",
         place="雁群停歇塘 · 2 号观鸟点", quota="限额 30 人", status="报名中"),
    dict(name="芦苇手作工坊", date="11 月 09 日", time="14:00 – 16:30",
         place="访客中心 · 自然教室", quota="限额 20 人", status="余 6 席"),
    dict(name="夜观湿地星虫", date="11 月 16 日", time="18:30 – 20:00",
         place="苇丛观察道 · 3 号点", quota="限额 16 人", status="即将满员"),
]


def dsl():
    n = []
    # ---------------- 顶部主视觉：晨雾天空 + 三层雁阵 + 芦苇剪影 ----------------
    n.append(rect(0, 0, W, 760, "#E9EFE9"))
    # 远山/天际线
    n.append(rect(0, 640, W, 120, "#D5E0D8"))
    # 水面
    n.append(rect(0, 700, W, 60, SKY))
    # 三层雁阵（远小 → 近大，≥3 层次）
    far = [(200, 180, 12), (280, 150, 14), (360, 190, 11), (430, 160, 13), (510, 185, 10),
           (820, 170, 13), (890, 145, 15), (960, 180, 11), (700, 195, 12)]
    mid = [(180, 300, 22), (280, 265, 26), (390, 295, 20), (480, 270, 24), (590, 300, 18),
           (760, 280, 24), (860, 255, 27), (950, 290, 21)]
    near = [(240, 430, 40), (390, 400, 46), (540, 435, 38), (690, 405, 44), (840, 440, 36)]
    n += bird_flock(far, REED)
    n += bird_flock(mid, TEAL)
    n += bird_flock(near, INK)
    # 太阳
    n.append(circle(880, 120, 90, "#F2D9B8"))
    n.append(circle(880, 120, 90, "#F2D9B8"))
    # 芦苇剪影（左右两簇，深浅两层）
    n += reed_cluster(90, 760, 300, "#9AA89A", 6, 90)
    n += reed_cluster(1000, 760, 340, "#7C8C7A", 7, 110)
    n += reed_cluster(150, 760, 200, TEAL, 4, 60)
    # 标题区
    n.append(text_node("秋迁季", 60, 90, 480, 120, 96, INK, "LEFT", "NORMAL", SERIF))
    n.append(text_node("AUTUMN MIGRATION SEASON", 64, 216, 520, 30, 16, TEAL, "LEFT", "NORMAL", INTER, spacing=3))
    n += wave(300, 268, 420, 10, ORANGE, 5, 3)
    n.append(text_node("十万只候鸟途经鹭洲 · 三个周末与你相遇", 64, 300, 620, 36, 22, INK, "LEFT", "NORMAL", SERIF))
    # ---------------- 活动卡 3 张 ----------------
    n.append(rect(0, 760, W, 590, PAPER))
    for i, e in enumerate(EVENTS):
        cy0 = 786 + i * 152
        n += card(60, cy0, W - 120, 144, WHITE, TEAL, 18, 2.0)
        # 左侧日期块
        n.append(rect(60, cy0, 190, 144, INK, 18))
        n.append(rect(238, cy0, 12, 144, INK))
        n.append(text_node(e["date"], 60, cy0 + 14, 190, 36, 25, PAPER, "CENTER", "NORMAL", MONO))
        _m = int(e["date"].split(" ")[0]); _d = int(e["date"].split(" ")[2].replace(" 日", ""))
        _wd = "周" + "一二三四五六日"[datetime.date(2026, _m, _d).weekday()]
        n.append(text_node(_wd, 60, cy0 + 52, 190, 20, 14, SKY, "CENTER", "NORMAL", SANS))
        n.append(text_node(e["time"], 60, cy0 + 78, 190, 26, 15, ORANGE, "CENTER", "NORMAL", MONO))
        # 右侧内容
        tx = 280
        n.append(text_node(e["name"], tx, cy0 + 14, 460, 38, 29, INK, "LEFT", "NORMAL", SERIF))
        n.append(text_node("地点 " + e["place"], tx, cy0 + 60, 460, 26, 16, TEAL, "LEFT", "NORMAL", SANS))
        n.append(text_node(e["quota"], tx, cy0 + 92, 460, 24, 15, REED, "LEFT", "NORMAL", SANS))
        # 状态徽章
        st_c = ORANGE if i < 2 else ORANGE_DEEP
        n.append(rect(W - 240, cy0 + 26, 160, 40, st_c, 20))
        n.append(text_node(e["status"], W - 240, cy0 + 33, 160, 26, 16, PAPER, "CENTER", "NORMAL", SANS))
        n.append(text_node("扫码报名", W - 240, cy0 + 80, 160, 24, 13, REED, "CENTER", "NORMAL", SANS))
    # ---------------- 报名入口 ----------------
    ay = 1252
    n.append(rect(60, ay, W - 120, 82, ORANGE, 41))
    n.append(text_node("扫码报名 · 三场活动可同报", 60, ay + 12, W - 120, 36, 24, PAPER, "CENTER", "NORMAL", SANS))
    n.append(text_node("报名通道于访客中心公众号「鹭洲湿地」开放", 60, ay + 48, W - 120, 26, 15, "#FBE3D3", "CENTER", "NORMAL", SANS))
    return snapshot(W, H, n, PAPER)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "case-06-v01.snapshot"
    out.write_text(dsl(), encoding="utf-8")
    print("wrote", out)
