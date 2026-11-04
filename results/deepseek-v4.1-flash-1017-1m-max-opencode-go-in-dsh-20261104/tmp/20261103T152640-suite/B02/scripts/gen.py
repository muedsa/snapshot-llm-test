# -*- coding: utf-8 -*-
"""B02: one client, ten touchpoints - 夜巡 Night Run Club."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "B02"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

BG, SURF, INK, DIM = "#0A0F1A", "#131C2B", "#F2F6FF", "#8A97AB"
LIME, WARM, COOL = "#C6FF4A", "#FF7A45", "#4CC9F0"

def R(x, y, w, h, c, r=0, b=None):
    return K.rect(x, y, w, h, color=c, radius=r, border=b)

def T(x, y, s, w, size, c=INK, bold=False, align=None, label=None):
    return K.text(x, y, s, width=w, size=size, color=c, bold=bold, align=align, label=label)

def mark(x, y, s=1.0, color=LIME):
    """three chevrons = 夜巡 mark; each chevron is its own 44x44 clip"""
    path = "M0 0 L22 44 L44 0 L30 0 L22 22 L14 0 Z"
    step = 34 * s
    out = []
    for i in range(3):
        out.append(f'<Positioned left="{x + i * step:g}" top="{y:g}">'
                   f'<ClipPath path="{path}" fillRule="NON_ZERO" clipBehavior="ANTI_ALIAS">'
                   f'<Container width="{44 * s:g}" height="{44 * s:g}" color="{color}"/></ClipPath></Positioned>')
    return "".join(out)
def fmt_pace(sec):
    return f"{sec // 60}′{sec % 60:02d}″"

# 1. recruitment poster 1080x1350
def c1():
    W, H = 1080, 1350
    p = [R(0, 0, W, H, BG)]
    for i in range(5):
        p.append(R(0, 1230 + i * 22, W, 22, "#0E1522" if i % 2 else "#0B1220"))
    p.append(mark(72, 64, 1.0))
    p.append(T(72, 140, "夜巡跑团", 600, 30, LIME, True))
    p.append(T(72, 184, "NIGHT RUN CLUB", 600, 20, DIM))
    p.append(T(72, 300, "城市睡了", 900, 90, INK, True))
    p.append(T(72, 400, "我们才出发", 900, 90, LIME, True))
    p.append(R(72, 520, 180, 6, WARM))
    p.append(T(72, 556, "每周三 / 六 · 21:00 · 江滨灯塔集合", 900, 28, INK))
    p.append(T(72, 604, "5km 与 10km 两条配速线 · 新手有人带", 900, 24, DIM))
    p.append(R(72, 700, 936, 2, "#243149"))
    tips = [("21:00", "集合与热身"), ("21:20", "分组出发"), ("22:30", "补给与复盘")]
    for i, (t, d) in enumerate(tips):
        y = 740 + i * 96
        p.append(T(72, y, t, 200, 40, LIME, True))
        p.append(T(300, y + 8, d, 600, 26, INK))
    p.append(R(72, 1060, 936, 2, "#243149"))
    p.append(T(72, 1090, "扫码加入 · 免费参加前三次", 700, 26, INK, True))
    p.append(T(72, 1140, "nightrun.example / 微信公众号「夜巡」", 800, 22, DIM))
    return K.document(W, H, p, background=BG)

# 2. app home 390x844
def c2():
    W, H = 390, 844
    p = [R(0, 0, W, H, BG)]
    p.append(R(0, 0, W, 300, "#101A2B"))
    p.append(mark(24, 44, 0.5))
    p.append(T(96, 48, "夜巡", 120, 24, LIME, True))
    p.append(T(306, 52, "···", 76, 24, DIM, align="RIGHT"))
    p.append(T(24, 120, "今晚 21:00", 300, 22, DIM))
    p.append(T(24, 150, "江滨灯塔 · 10km", 340, 30, INK, True))
    p.append(R(24, 206, 342, 1, "#243149"))
    p.append(T(24, 222, "已有 12 人报名 · 2 位领跑", 300, 20, DIM))
    p.append(R(24, 262, 342, 1, "#243149"))
    p.append(R(24, 320, 342, 150, SURF, 16))
    p.append(T(44, 338, "本周里程", 200, 20, DIM))
    p.append(T(44, 364, "28.4", 140, 44, LIME, True))
    p.append(T(160, 386, "km", 60, 20, DIM))
    p.append(T(196, 364, "配速 5′42″", 146, 20, INK, align="RIGHT"))
    p.append(T(196, 396, "连续 6 周", 146, 20, WARM, align="RIGHT"))
    p.append(T(24, 500, "最近活动", 300, 22, INK, True))
    acts = [("11-05", "江滨 8km", "5′50″", LIME), ("11-02", "环湖 12km", "6′05″", COOL),
            ("10-29", "夜爬台阶", "6′30″", WARM)]
    for i, (d, name, pace, col) in enumerate(acts):
        y = 540 + i * 76
        p.append(R(24, y, 342, 64, SURF, 12))
        p.append(R(24, y, 4, 64, col, 2))
        p.append(T(44, y + 12, name, 200, 22, INK, True))
        p.append(T(44, y + 40, d, 120, 17, DIM))
        p.append(T(250, y + 22, pace, 100, 22, col, True, "RIGHT"))
    p.append(R(24, 770, 342, 56, LIME, 28))
    p.append(T(24, 784, "报名今晚", 342, 24, "#0A0F1A", True, "CENTER"))
    return K.document(W, H, p, background=BG)

# 3. route map 1600x900
def c3():
    W, H = 1600, 900
    p = [R(0, 0, W, H, "#0B1220")]
    # faint street grid for map feel
    for i in range(9):
        p.append(R(0, 200 + i * 74, W, 1, "#141F30"))
    for i in range(12):
        p.append(R(120 + i * 130, 160, 1, 640, "#141F30"))
    # river
    p.append(R(0, 330, W, 190, "#0F2436"))
    p.append(R(0, 330, W, 3, "#1D4A63"))
    p.append(R(0, 517, W, 3, "#1D4A63"))
    p.append(T(1330, 360, "江 面", 200, 24, "#2E5A78", True))
    p.append(T(64, 48, "10km 路线 · 江滨环线", 800, 36, INK, True))
    p.append(T(64, 96, "累计爬升 42m · 全程路灯 · 2 个补给点 · 逆时针", 900, 22, DIM))
    pts = [(200, 470), (420, 430), (660, 466), (900, 424), (1140, 462), (1390, 430)]
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        ln = math.hypot(x2 - x1, y2 - y1)
        ang = math.atan2(y2 - y1, x2 - x1)
        p.append(f'<Positioned left="{(x1 + x2) / 2 - ln / 2:g}" top="{(y1 + y2) / 2 - 5:g}">'
                 f'<Transform matrix="({math.cos(ang):.6f},{math.sin(ang):.6f},0,0,{-math.sin(ang):.6f},{math.cos(ang):.6f},0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
                 f'<Container width="{ln:g}" height="10" color="{LIME}"/></Transform></Positioned>')
    labels = ["灯塔集合", "补给 A · 3.2km", "桥下折返 · 5.0km", "补给 B · 7.4km", "终点"]
    for i, (x, y) in enumerate(pts):
        p.append(R(x - 9, y - 9, 18, 18, LIME, 9, "3 SOLID #0B1220"))
        if i < len(labels):
            p.append(T(x - 90, 548, labels[i], 180, 20, INK, align="CENTER"))
    p.append(R(64, 600, 430, 96, SURF, 10))
    p.append(T(84, 616, "配速分组（出发时按牌站队）", 380, 18, DIM))
    p.append(T(84, 644, "5′30″ / 6′15″ / 7′00″", 380, 24, LIME, True))
    p.append(R(1106, 600, 430, 96, SURF, 10))
    p.append(T(1126, 616, "关门与收队", 380, 18, DIM))
    p.append(T(1126, 644, "23:30 灯塔集合，收队车随行", 390, 22, INK, True))
    p.append(T(64, 830, "路线为示意图，实际以当晚领跑带队为准", 800, 18, DIM))
    return K.document(W, H, p, background="#0B1220")
# 4. race bib 800x600
def c4():
    W, H = 800, 600
    p = [R(0, 0, W, H, BG)]
    p.append(R(0, 0, W, 8, LIME))
    p.append(R(24, 24, 752, 552, SURF, 12))
    p.append(T(52, 48, "夜巡 · 江滨夜跑", 400, 20, DIM))
    p.append(T(52, 84, "0496", 500, 120, LIME, True))
    p.append(T(52, 226, "苏言", 400, 34, INK, True))
    p.append(T(52, 274, "10KM · 5′30″ 组", 400, 22, DIM))
    p.append(R(52, 330, 360, 2, "#243149"))
    p.append(T(52, 356, "紧急联系人", 300, 18, DIM))
    p.append(T(52, 382, "林川 138-0000-0000", 360, 22, INK))
    p.append(R(460, 48, 288, 288, "#0E1522", 12))
    for i in range(6):
        for j in range(6):
            if (i + j) % 3 == 0:
                p.append(R(476 + i * 44, 64 + j * 44, 30, 30, LIME, 3))
    p.append(T(460, 356, "扫描签到", 288, 18, DIM, align="CENTER"))
    p.append(T(52, 500, "2026.11.07 · 21:00 起点灯塔", 500, 20, DIM))
    return K.document(W, H, p, background=BG)

# 5. schedule card 1080x1350
def c5():
    W, H = 1080, 1350
    p = [R(0, 0, W, H, BG)]
    p.append(T(72, 56, "11 月 · 夜巡日程", 700, 40, INK, True))
    p.append(T(72, 112, "固定周三 / 周六 · 雨天顺延", 700, 22, DIM))
    items = [("11-04 周三", "江滨 10km", "21:00", "灯塔", LIME),
             ("11-07 周六", "环湖 12km", "20:30", "东门", COOL),
             ("11-11 周三", "台阶间歇", "21:00", "南塔", WARM),
             ("11-14 周六", "长距离 18km", "20:00", "灯塔", LIME),
             ("11-18 周三", "恢复跑 5km", "21:00", "书院", COOL),
             ("11-21 周六", "夜爬 8km", "20:30", "北山", WARM),
             ("11-25 周三", "江滨 10km", "21:00", "灯塔", LIME),
             ("11-28 周六", "月度计时赛", "20:00", "奥体", LIME)]
    for i, (date, name, time, place, col) in enumerate(items):
        y = 170 + i * 140
        p.append(R(72, y, 936, 118, SURF, 14))
        p.append(R(72, y, 6, 118, col, 3))
        p.append(T(96, y + 16, date, 260, 22, col, True))
        p.append(T(96, y + 48, name, 420, 30, INK, True))
        p.append(T(560, y + 50, time, 160, 26, INK, align="RIGHT"))
        p.append(T(760, y + 52, place, 220, 24, DIM, align="RIGHT"))
    return K.document(W, H, p, background=BG)

# 6. finisher certificate 1400x1000
def c6():
    W, H = 1400, 1000
    p = [R(0, 0, W, H, "#F7F4EC")]
    p.append(R(0, 0, W, 10, LIME))
    p.append(mark(600, 80, 1.0, "#1A2333"))
    p.append(T(80, 190, "完赛证书", 600, 26, "#6B7280"))
    p.append(T(80, 240, "夜巡 2026 秋季赛", 900, 56, "#14181F", True))
    p.append(R(80, 330, 1240, 2, "#D8D2C2"))
    p.append(T(80, 370, "兹证明", 300, 24, "#6B7280"))
    p.append(T(80, 410, "苏言", 900, 64, "#14181F", True))
    p.append(T(80, 500, "于 2026.11.07 完成 10KM，净计时 00:57:12，配速 5′43″。", 1200, 26, "#3C4552"))
    stats = [("净计时", "00:57:12"), ("平均配速", "5′43″"), ("总排名", "38 / 216"), ("组别", "女子 30–39")]
    for i, (k, v) in enumerate(stats):
        x = 80 + (i % 2) * 620
        y = 570 + (i // 2) * 96
        p.append(T(x, y, k, 300, 20, "#6B7280"))
        p.append(T(x, y + 28, v, 400, 32, "#14181F", True))
    p.append(R(80, 800, 1240, 2, "#D8D2C2"))
    p.append(T(80, 830, "夜巡跑团 · 赛事委员会", 700, 20, "#6B7280"))
    p.append(T(1000, 830, "编号 NR-2026-0496", 320, 20, "#6B7280", align="RIGHT"))
    return K.document(W, H, p, background="#F7F4EC")

# 7. social story 1080x1920
def c7():
    W, H = 1080, 1920
    p = [R(0, 0, W, H, BG)]
    p.append(R(0, 0, W, H, "#101A2B"))
    p.append(mark(80, 120, 1.4))
    p.append(T(80, 240, "今晚", 700, 28, DIM))
    p.append(T(80, 288, "21:00", 900, 150, LIME, True))
    p.append(T(80, 460, "江滨灯塔", 900, 60, INK, True))
    p.append(T(80, 540, "10km · 5′30″ 组还有 3 个位置", 900, 30, DIM))
    p.append(R(80, 640, 920, 2, "#243149"))
    steps = [("21:00", "集合"), ("21:15", "热身"), ("21:20", "出发"), ("22:30", "补给")]
    for i, (t, d) in enumerate(steps):
        y = 700 + i * 110
        p.append(R(80, y + 10, 16, 16, LIME, 8))
        p.append(T(120, y, t, 200, 30, LIME, True))
        p.append(T(340, y + 2, d, 300, 30, INK))
    p.append(R(80, 1160, 920, 2, "#243149"))
    p.append(T(80, 1192, "今晚提醒", 600, 26, INK, True))
    for i, tip in enumerate(["带头灯或反光条，江边有一段没有路灯", "补给点只提供水与电解质，能量胶自备", "配速组由领跑带队，掉队请等在最近的补给点"]):
        p.append(R(80, 1244 + i * 62, 10, 10, LIME, 5))
        p.append(T(112, 1234 + i * 62, tip, 880, 22, DIM))
    p.append(R(80, 1600, 920, 120, LIME, 16))
    p.append(T(80, 1640, "向上滑动报名", 920, 32, "#0A0F1A", True, "CENTER"))
    p.append(T(80, 1780, "nightrun.example", 700, 24, DIM))
    return K.document(W, H, p, background="#101A2B")

# 8. aid station sign 900x1200
def c8():
    W, H = 900, 1200
    p = [R(0, 0, W, H, BG)]
    p.append(R(0, 0, W, 16, LIME))
    p.append(T(60, 70, "补给站 A", 700, 64, LIME, True))
    p.append(T(60, 156, "AID STATION", 700, 28, DIM))
    p.append(R(60, 210, 780, 3, "#243149"))
    rows = [("水", "常温 / 冰"), ("电解质", "柠檬 / 原味"), ("能量胶", "每人 1 支"), ("急救", "AED 在右侧帐篷")]
    for i, (k, v) in enumerate(rows):
        y = 260 + i * 130
        p.append(T(60, y, k, 240, 36, INK, True))
        p.append(T(320, y + 4, v, 500, 28, DIM))
        p.append(R(60, y + 76, 780, 1, "#1C2838"))
    p.append(R(60, 830, 780, 140, SURF, 12))
    p.append(T(84, 850, "前方 2.5km 到补给 B", 600, 26, INK, True))
    p.append(T(84, 890, "折返点请注意来车", 600, 22, WARM))
    p.append(T(60, 1050, "夜巡 · 江滨夜跑", 600, 22, DIM))
    p.append(T(60, 1090, "如需帮助，请找穿荧光背心的志愿者", 780, 20, DIM))
    return K.document(W, H, p, background=BG)

# 9. membership card 1000x600
def c9():
    W, H = 1000, 600
    p = [R(0, 0, W, H, BG)]
    p.append(R(32, 32, 936, 536, "#101A2B", 20))
    p.append(R(32, 32, 936, 8, LIME))
    p.append(mark(72, 84, 0.9))
    p.append(T(72, 156, "夜巡跑团", 500, 34, INK, True))
    p.append(T(72, 200, "NIGHT RUN CLUB · MEMBER", 500, 18, DIM))
    p.append(T(72, 300, "苏言", 400, 44, LIME, True))
    p.append(T(72, 356, "NO. 0496 · 2024 年加入", 500, 20, DIM))
    p.append(R(72, 420, 400, 2, "#243149"))
    p.append(T(72, 444, "累计 128 次 · 1,246 km", 460, 22, INK))
    p.append(T(72, 484, "连续 6 周在跑", 460, 22, WARM, True))
    p.append(R(700, 84, 220, 220, "#0E1522", 16))
    for i in range(4):
        for j in range(4):
            p.append(R(716 + i * 52, 100 + j * 52, 34, 34, LIME if (i + j) % 2 == 0 else "#1E2A3C", 4))
    p.append(T(700, 320, "扫码查看我的记录", 220, 18, DIM))
    return K.document(W, H, p, background=BG)

# 10. year in review 1200x1600
def c10():
    W, H = 1200, 1600
    p = [R(0, 0, W, H, BG)]
    p.append(T(80, 64, "2026", 400, 26, LIME, True))
    p.append(T(80, 104, "这一年的夜", 900, 56, INK, True))
    p.append(T(80, 180, "夜巡跑团 · 年度回顾", 700, 22, DIM))
    stats = [("出勤", "86", "次"), ("累计", "1,246", "km"), ("最长", "18.2", "km"), ("最快", "5′12″", "配速")]
    for i, (k, v, u) in enumerate(stats):
        x = 80 + (i % 2) * 540
        y = 260 + (i // 2) * 150
        p.append(T(x, y, k, 200, 20, DIM))
        p.append(T(x, y + 30, v, 320, 52, INK, True))
        p.append(T(x + 200, y + 58, u, 100, 20, DIM))
    p.append(R(80, 580, 1040, 2, "#243149"))
    p.append(T(80, 610, "每月出勤", 600, 24, INK, True))
    vals = [5, 6, 7, 8, 6, 9, 10, 7, 8, 9, 6, 5]
    for i, v in enumerate(vals):
        h = v * 34
        x = 92 + i * 86
        p.append(R(x, 900 - h, 54, h, LIME if v >= 9 else "#1E6B3A", 8))
        p.append(T(x - 8, 912, f"{i+1}", 70, 18, DIM, align="CENTER"))
    p.append(R(80, 960, 1040, 2, "#243149"))
    p.append(T(80, 992, "常跑的路线", 600, 24, INK, True))
    routes = [("江滨环线 10km", "38 次", 38), ("环湖 12km", "22 次", 22), ("台阶间歇", "14 次", 14)]
    for i, (name, cnt, n) in enumerate(routes):
        y = 1040 + i * 96
        p.append(T(80, y, name, 500, 24, INK))
        p.append(T(620, y, cnt, 160, 24, DIM, align="RIGHT"))
        p.append(R(800, y + 6, int(n * 5.6), 20, LIME, 10))
    p.append(R(80, 1400, 1040, 2, "#243149"))
    p.append(T(80, 1432, "「一个人跑得快，一群人跑得远。」", 1000, 30, INK))
    p.append(T(80, 1500, "nightrun.example", 600, 22, DIM))
    return K.document(W, H, p, background=BG)

CASES = [
    ("case-01", "招新海报", c1, (1080, 1350), "awareness", "微信公众号与线下张贴",
     "新人对跑团一无所知，需要在 3 秒内看到时间、地点与门槛"),
    ("case-02", "小程序首页", c2, (390, 844), "usage", "手机随身处",
     "老会员确认今晚活动并报名，同时看到自己的周里程"),
    ("case-03", "路线图", c3, (1600, 900), "usage", "集合点展板与群内图片",
     "出发前看清 10km 路线、补给点与配速分组"),
    ("case-04", "号码布", c4, (800, 600), "event", "比赛现场佩戴",
     "现场识别身份、组别与紧急联系人"),
    ("case-05", "月度日程卡", c5, (1080, 1350), "planning", "群公告与朋友圈",
     "一次看完整月安排，决定来哪几场"),
    ("case-06", "完赛证书", c6, (1400, 1000), "feedback", "赛后分享与打印",
     "把一次完赛变成可分享、可留存的凭证"),
    ("case-07", "社交故事卡", c7, (1080, 1920), "reminder", "朋友圈 / 小红书",
     "活动当天提醒，并给出当晚时间线"),
    ("case-08", "补给站指示牌", c8, (900, 1200), "event", "赛道现场",
     "夜间远距离可读的补给与急救指引"),
    ("case-09", "会员卡", c9, (1000, 600), "retention", "入会礼与电子卡",
     "身份感与累积成就，鼓励持续参加"),
    ("case-10", "年度回顾", c10, (1200, 1600), "feedback", "年末推送",
     "用数据回看一年，强化归属感"),
]

logger = api.TaskLogger(TASK, TMP)
ONLY = os.environ.get("B02_ONLY", "").split(",") if os.environ.get("B02_ONLY") else None
meta = []
for cid, title, fn, size, stage, channel, need in CASES:
    if ONLY and cid not in ONLY:
        continue
    d = OUT / cid
    d.mkdir(parents=True, exist_ok=True)
    dsl = fn()
    (d / "final.snapshot").write_text(dsl, encoding="utf-8")
    warn = K.drain_warnings()
    rec = logger.render(d / "final.snapshot", d / "final.png", cid)
    ok = rec["http_status"] == 200 and api.measure_png(d / "final.png") == size
    print(f"{cid}: {rec['http_status']} {rec['response_bytes']}B {rec['elapsed_s']}s ok={ok}")
    for w in warn:
        print("   ", w)
    meta.append({"case": cid, "title": title, "size": list(size), "stage": stage,
                 "channel": channel, "need": need, "png": f"{cid}/final.png",
                 "dsl": f"{cid}/final.snapshot", "bytes": rec["response_bytes"]})
if not ONLY:
    api.write_json(TMP / "cases.json", meta)
print("rendered", len(meta))
