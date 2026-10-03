# -*- coding: utf-8 -*-
"""B02 touchpoints 01-02: season poster and sowing calendar wall chart."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kit import Doc, CJK, MONO, tw  # noqa: E402
from b02lib import *  # noqa: E402,F403

N1 = "t01-season-poster"
N2 = "t02-sowing-calendar"

CROPS = [
    ("樱桃萝卜", (3, 9), None, (4, 10)), ("小白菜", (3, 10), None, (4, 11)),
    ("菠菜", (2, 4), (8, 10), (4, 5), (10, 12)), ("生菜", (3, 6), (8, 9), (5, 7), (10, 11)),
    ("芝麻菜", (4, 9), None, (5, 10)), ("豌豆", (10, 11), (2, 3), (5, 6)),
    ("番茄", None, (4, 5), (7, 9)), ("黄瓜", None, (4, 5), (6, 9)),
    ("辣椒", None, (5, 5), (7, 10)), ("茄子", None, (5, 5), (7, 9)),
    ("罗勒", (4, 6), None, (6, 9)), ("万寿菊", (4, 5), None, (6, 10)),
    ("向日葵", (4, 6), None, (8, 10)), ("草莓", None, (3, 4), (5, 6)),
    ("大蒜", (10, 11), None, (6, 7)), ("迷迭香", None, (4, 5), (5, 11)),
]
# normalise: (name, sow, transplant, harvest) where sow/transplant may be a
# tuple of one or two ranges
ROWS = [
    ("樱桃萝卜", [(3, 9)], [], [(4, 10)]),
    ("小白菜", [(3, 10)], [], [(4, 11)]),
    ("菠菜", [(2, 4), (8, 10)], [], [(4, 5), (10, 12)]),
    ("生菜", [(3, 6), (8, 9)], [], [(5, 7), (10, 11)]),
    ("芝麻菜", [(4, 9)], [], [(5, 10)]),
    ("豌豆", [(10, 11), (2, 3)], [], [(5, 6)]),
    ("番茄", [], [(4, 5)], [(7, 9)]),
    ("黄瓜", [], [(4, 5)], [(6, 9)]),
    ("辣椒", [], [(5, 5)], [(7, 10)]),
    ("茄子", [], [(5, 5)], [(7, 9)]),
    ("罗勒", [(4, 6)], [], [(6, 9)]),
    ("万寿菊", [(4, 5)], [], [(6, 10)]),
    ("向日葵", [(4, 6)], [], [(8, 10)]),
    ("草莓", [], [(3, 4)], [(5, 6)]),
    ("大蒜", [(10, 11)], [], [(6, 7)]),
    ("迷迭香", [], [(4, 5)], [(5, 11)]),
]


def build1(ver="v1", outdir=None):
    data = {
        "project": PROJECT_FULL, "site": SITE, "season": "2026 春季开放季",
        "open_from": "2026-03-01", "open_to": "2026-06-30",
        "sessions": [
            {"date": "2026-03-14", "time": "10:00–12:00", "title": "开箱日：认领你的种植箱",
             "seats": 40, "left": 6},
            {"date": "2026-04-11", "time": "09:30–11:30", "title": "留种工作坊：从花到种子",
             "seats": 24, "left": 9},
            {"date": "2026-05-23", "time": "15:00–17:00", "title": "屋顶市集：把收成摆出来",
             "seats": 30, "left": 21},
        ],
        "steps": ["在社区服务站或线上登记，领取借种卡",
                  "每季最多借 5 包种子，登记品种与播期",
                  "收获后归还同品种种子 1 小包（不少于 30 粒）",
                  "参与 1 次公共地块维护，即可续借下一季"],
        "contact": "云栖里社区服务站 1 楼 · 每周二、四 14:00–18:00",
        "fictional": True,
    }
    d = Doc(1240, 1754, PAPER)
    # ---------------------------------------------------------------- ink block
    d.box(0, 0, 1240, 520, INK)
    seed_mark(d, 86, 92, 30, LEAF_L, INK)
    d.text(150, 62, PROJECT, 52, CARD, "BOLD")
    d.text(150, 132, "社区种子图书馆 × 屋顶农场", 20, "#9DB0A2FF")
    d.ctext(760, 66, PROJECT_EN, 16, "#6E8478FF", family=MONO, w=448, h=22,
            align="CENTER_RIGHT")
    d.ctext(760, 94, SITE, 16, "#6E8478FF", w=448, h=22, align="CENTER_RIGHT")
    d.text(86, 214, "2026 春季开放季", 64, CARD, "BOLD")
    d.text(86, 300, "借一包种子，还一把收成", 26, SUN)
    d.box(86, 348, 96, 5, LEAF_L, radius=2)
    # rooftop scene
    sun(d, 1080, 250, 40, SUN)
    d.box(0, 452, 1240, 3, "#3A4A40FF")
    planter(d, 86, 372, 260, 80, 4, crop=LEAF_L, crop_h=40, label=None)
    planter(d, 372, 396, 260, 56, 4, crop=LEAF_L, crop_h=30, label=None)
    planter(d, 658, 360, 260, 92, 3, crop=SUN_P, crop_h=52, label=None)
    planter(d, 944, 388, 210, 64, 3, crop=LEAF_L, crop_h=34, label=None)
    d.text(86, 470, "3 号楼屋顶 · 46 个种植箱 · 218 户会员 · 建成于 2023 年", 17,
           "#7E9386FF")

    # ---------------------------------------------------------------- facts
    facts = [("开放期", "2026-03-01 — 06-30", "每天 07:00–19:00"),
             ("地点", "云栖里 3 号楼屋顶", "电梯至 11 层，步行 1 层"),
             ("费用", "会员免费 · 非会员 20 元/季", "含种子、工具与用水")]
    for i, (k, v, s) in enumerate(facts):
        x = 32 + i * 398
        card(d, x, 552, 380, 116)
        d.box(x, 552, 5, 116, [LEAF, SKY, SUN][i], tl=RADIUS, bl=RADIUS)
        d.text(x + 20, 570, k, 14, MUTE)
        d.ctext(x + 20, 592, v, 20, INK, "BOLD", w=344, h=28)
        d.ctext(x + 20, 626, s, 14, MUTE, w=344, h=20)

    # ---------------------------------------------------------------- sessions
    card(d, 32, 692, 1176, 330)
    section(d, 56, 712, 1128, "本季三场活动")
    for i, s in enumerate(data["sessions"]):
        y = 752 + i * 86
        d.box(56, y, 86, 66, mix(LEAF, PAPER, 0.88, alpha="FF"), radius=8)
        d.ctext(56, y + 8, s["date"][5:], 20, LEAF, "BOLD", family=MONO, w=86, h=26,
                align="CENTER")
        d.ctext(56, y + 38, s["date"][:4], 12, MUTE, family=MONO, w=86, h=18,
                align="CENTER")
        d.ctext(160, y + 6, s["title"], 21, INK, "BOLD", w=620, h=30)
        d.ctext(160, y + 38, "%s · 名额 %d 人 · 剩余 %d 位" % (s["time"], s["seats"],
                                                              s["left"]), 15, MUTE,
                w=620, h=22)
        bar(d, 800, y + 22, 220, 12, 1 - s["left"] / float(s["seats"]), LEAF)
        d.ctext(1030, y + 16, "已报 %d%%" % round((1 - s["left"] / float(s["seats"])) * 100),
                14, LEAF, family=MONO, w=120, h=22, align="CENTER_RIGHT")
        if i < 2:
            d.box(56, y + 74, 1128, 1, RULE)

    # ---------------------------------------------------------------- steps
    card(d, 32, 1046, 1176, 300)
    section(d, 56, 1066, 1128, "怎么加入")
    for i, s in enumerate(data["steps"]):
        y = 1108 + i * 58
        d.disc(76, y + 16, 34, mix(LEAF, PAPER, 0.84, alpha="FF"))
        d.ctext(59, y - 1, "%d" % (i + 1), 18, LEAF, "BOLD", family=MONO, w=34, h=34,
                align="CENTER")
        d.ctext(110, y + 3, s, 17, INK_SOFT, w=1050, h=26)

    # ---------------------------------------------------------------- join
    card(d, 32, 1370, 1176, 220)
    qr_block(d, 56, 1394, 172, seed=17)
    d.ctext(56, 1574, "扫码登记（示意图形）", 12, MUTE, w=172, h=18, align="CENTER")
    d.text(252, 1396, "登记与借种", 22, INK, "BOLD")
    d.ctext(252, 1432, "线上登记后 1 个工作日内收到借种卡编号；凭编号到服务站领取种子。",
            16, INK_SOFT, w=920, h=24)
    d.ctext(252, 1462, data["contact"], 16, MUTE, w=920, h=24)
    d.ctext(252, 1494, "留种提示：采收后请把最健壮的 3 株留到最后，种子完全成熟再剪下阴干。",
            15, MUTE, w=920, h=24)
    d.ctext(252, 1526, "会员每季可借 5 包种子；种子来源为上一季会员归还与社区交换。",
            15, MUTE, w=920, h=24)
    d.box(252, 1560, 920, 1, RULE)
    d.ctext(252, 1568, DSL_ONLY + " 农场、社区与活动日期均为虚构演示。", 12, MUTE,
            w=920, h=18)

    # ---------------------------------------------------------------- footer
    d.box(0, 1622, 1240, 132, INK)
    d.box(0, 1622, 1240, 4, LEAF_L)
    seed_mark(d, 76, 1688, 24, LEAF_L, INK)
    d.text(120, 1662, PROJECT_FULL, 20, CARD, "BOLD")
    d.text(120, 1694, "借种 · 共耕 · 留种 · 市集", 15, "#9DB0A2FF")
    for i in range(5):
        sprout(d, 620 + i * 40, 1700, 20 + (i % 3) * 6, "#4C6154FF", 3)
    d.ctext(760, 1662, "云栖里社区服务站 · 每周二、四 14:00–18:00", 14, "#9DB0A2FF",
            w=448, h=20, align="CENTER_RIGHT")
    d.ctext(760, 1690, "海报设计：一粒设计组 · 版本 2026S-1", 13, "#6E8478FF", w=448,
            h=18, align="CENTER_RIGHT")

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (N1, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % N1), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data


def build2(ver="v1", outdir=None):
    months = [("%d 月" % m) for m in range(1, 13)]
    open_year = [("樱桃萝卜", 0), ("小白菜", 1), ("菠菜", 2), ("生菜", 3), ("芝麻菜", 4),
                 ("豌豆", 5), ("番茄", 6), ("黄瓜", 7), ("辣椒", 8), ("茄子", 9),
                 ("罗勒", 10), ("万寿菊", 11), ("向日葵", 12), ("草莓", 13),
                 ("大蒜", 14), ("迷迭香", 15)]
    sow_weeks = sum(len(r[1]) for r in ROWS)
    hv_weeks = sum(len(r[3]) for r in ROWS)
    data = {
        "project": PROJECT_FULL, "year": 2026,
        "crops": [{"name": r[0], "sow": r[1], "transplant": r[2], "harvest": r[3]}
                  for r in ROWS],
        "crop_count": len(ROWS), "sow_windows": sow_weeks, "harvest_windows": hv_weeks,
        "frost": "本地终霜期约 3 月 20 日，初霜期约 11 月 5 日（示例数据）",
        "april_todo": ["补播菠菜与生菜（第 2 茬）", "番茄、黄瓜移栽到 3 号地块",
                       "追肥：每箱 200 g 腐熟堆肥", "检查滴灌带，清理过滤网",
                       "搭番茄支架与爬藤网", "记录第一茬采收量"],
    }
    d = Doc(1680, 1050, PAPER)
    header(d, 1680, 96, "播种日历 · 2026", "%s · %s · %d 种作物 · 终霜期约 3 月 20 日"
           % (PROJECT_FULL, SITE, len(ROWS)),
           right=[("每周二 / 四 更新", "#9DB0A2FF", 15),
                  ("版本 2026.1 · 张贴于工具房", "#6E8478FF", 14)])

    # ---------------------------------------------------------------- grid
    GX, GY, GW, GH = 32, 120, 1180, 800
    card(d, GX, GY, GW, GH)
    NAMEW = 150
    cw = (GW - 40 - NAMEW) / 12.0
    rowh = (GH - 78 - 52) / float(len(ROWS))
    for j, m in enumerate(months):
        x = GX + 20 + NAMEW + j * cw
        d.ctext(x, GY + 52, m, 14, INK, "BOLD", family=MONO, w=cw, h=20, align="CENTER")
    d.ctext(GX + 20, GY + 52, "作物", 14, MUTE, w=NAMEW, h=20)
    d.box(GX + 20, GY + 74, GW - 40, 1, RULE)
    for i, (name, sow, tp, hv) in enumerate(ROWS):
        y = GY + 78 + i * rowh
        if i % 2 == 0:
            d.box(GX + 20, y, GW - 40, rowh, "#FBF8F0FF")
        d.ctext(GX + 20, y + rowh * 0.5 - 10, name, 15, INK, w=NAMEW, h=20)
        for j in range(12):
            x = GX + 20 + NAMEW + j * cw
            d.box(x, y, 1, rowh, "#F0ECE1FF")
            for (a, b) in sow:
                if a <= j + 1 <= b:
                    d.box(x + 3, y + rowh * 0.16, cw - 6, rowh * 0.24, LEAF, radius=3)
            for (a, b) in tp:
                if a <= j + 1 <= b:
                    d.box(x + 3, y + rowh * 0.42, cw - 6, rowh * 0.20, SKY, radius=3)
            for (a, b) in hv:
                if a <= j + 1 <= b:
                    d.box(x + 3, y + rowh * 0.66, cw - 6, rowh * 0.20, SUN, radius=3)
        d.box(GX + 20, y + rowh, GW - 40, 1, "#F0ECE1FF")
    # legend + frost note
    LY = GY + GH - 44
    for i, (col, lab) in enumerate([(LEAF, "播种"), (SKY, "移栽"), (SUN, "采收"),
                                    ("#EDE9DDFF", "非适期")]):
        x = GX + 20 + i * 170
        d.box(x, LY + 4, 22, 12, col, radius=3)
        d.ctext(x + 30, LY, lab, 14, INK_SOFT, w=120, h=20)
    d.ctext(GX + GW - 640, LY, data["frost"], 13, MUTE, w=620, h=20,
            align="CENTER_RIGHT")

    # ---------------------------------------------------------------- right
    RX, RW = 1236, 412
    card(d, RX, 120, RW, 420)
    section(d, RX + 20, 140, RW - 40, "4 月待办（本月）")
    for i, s in enumerate(data["april_todo"]):
        y = 180 + i * 54
        d.box(RX + 20, y + 6, 18, 18, CARD, radius=5, border="1 SOLID " + LEAF_L)
        d.ctext(RX + 48, y + 2, s, 15, INK_SOFT, w=RW - 76, h=24)
        if i < len(data["april_todo"]) - 1:
            d.box(RX + 20, y + 40, RW - 40, 1, "#F1EDE2FF")

    card(d, RX, 560, RW, 360)
    section(d, RX + 20, 580, RW - 40, "地块与留种提醒")
    tips = [("1 号地块", "叶菜轮作区 · 本季第 2 茬，注意跳甲"),
            ("2 号地块", "果菜区 · 番茄需搭架，单干整枝"),
            ("3 号地块", "根茎与香草区 · 大蒜 6 月收"),
            ("留种", "十字花科需与近缘种隔离 500 m 以上"),
            ("留种", "豆类留种选植株中下部最早成熟的荚")]
    for i, (k, v) in enumerate(tips):
        y = 620 + i * 56
        d.ctext(RX + 20, y, k, 15, LEAF, "BOLD", w=90, h=22)
        d.ctext(RX + 118, y, clip(v, 15, RW - 138), 15, INK_SOFT, w=RW - 138, h=22)
        d.ctext(RX + 118, y + 22, "", 12, MUTE, w=RW - 138, h=18)

    d.ctext(32, 936, "网格 = 12 个月；每格内的三条色带自上而下分别表示播种、移栽、采收的适期。",
            14, INK_SOFT, w=900, h=22)
    d.ctext(32, 962, "播种适期由本地终霜期与作物生育期推算，为演示数据；" + DSL_ONLY, 13,
            MUTE, w=1160, h=20)
    d.ctext(32, 992, "共 %d 个播种适期区间、%d 个采收区间，由脚本按作物表统计。"
            % (sow_weeks, hv_windows(data)), 13, MUTE, w=900, h=20)

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (N2, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % N2), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data


def hv_windows(data):
    return sum(len(c["harvest"]) for c in data["crops"])
