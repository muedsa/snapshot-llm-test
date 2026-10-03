# -*- coding: utf-8 -*-
"""B02 touchpoints 07-08: market stall price board and kids workshop poster."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kit import Doc, CJK, MONO, tw  # noqa: E402
from b02lib import *  # noqa: E402,F403

N7 = "t07-market-board"
N8 = "t08-kids-workshop"

ITEMS = [
    ("菠菜", "1 把 ≈ 300 g", "B01", "03-08", 8.0, 6.0),
    ("生菜", "奶油生菜 · 1 棵", "B02", "03-08", 6.0, 4.5),
    ("小白菜", "1 把 ≈ 400 g", "B03", "03-07", 6.0, 4.5),
    ("芝麻菜", "1 袋 ≈ 120 g", "B04", "03-08", 9.0, 7.0),
    ("樱桃萝卜", "1 把 ≈ 250 g", "B09", "03-08", 10.0, 8.0),
    ("胡萝卜", "1 袋 ≈ 500 g", "B10", "03-07", 8.0, 6.0),
    ("豌豆尖", "1 袋 ≈ 150 g", "B17", "03-08", 12.0, 9.5),
    ("迷迭香", "鲜枝 1 束", "B12", "03-06", 7.0, 5.0),
    ("罗勒", "鲜枝 1 束", "B13", "03-08", 7.0, 5.0),
    ("薄荷", "鲜枝 1 束", "B21", "03-08", 6.0, 4.0),
    ("百里香", "鲜枝 1 束", "B22", "03-06", 8.0, 6.0),
    ("万寿菊", "盆花 1 盆", "B14", "03-08", 15.0, 12.0),
    ("波斯菊", "盆花 1 盆", "B23", "03-08", 15.0, 12.0),
    ("堆肥", "腐熟堆肥 2 kg", "—", "03-05", 10.0, 0.0),
]

SESSIONS = [
    ("03-21", "周六 10:00–11:30", "种子的旅行", "5–7 岁", 12, 4, "把一粒种子拆开看：种皮、胚、养分"),
    ("04-18", "周六 10:00–11:30", "一颗种子的家", "6–9 岁", 14, 9, "配土、装盆、播种，带走自己的小盆"),
    ("05-16", "周六 15:00–16:30", "留下来年的种子", "7–10 岁", 12, 7, "辨认成熟种子，做一包自己的留种袋"),
]
STAGES = [("种子", "种皮保护胚芽，遇到水才醒"), ("发芽", "胚根先出来，再顶起子叶"),
          ("长大", "子叶展开，开始自己制造养分"), ("开花结籽", "授粉后结成新的种子")]


def build7(ver="v1", outdir=None):
    priced = [i for i in ITEMS if i[5] > 0]
    data = {
        "project": PROJECT_FULL, "date": "2026-03-08（周日）",
        "time": "09:00–12:00", "place": "云栖里社区北广场 · 一粒摊位（虚构）",
        "items": [{"name": i[0], "note": i[1], "box": i[2], "harvest": i[3],
                   "price": i[4], "member": i[5]} for i in ITEMS],
        "item_count": len(ITEMS),
        "price_min": min(i[4] for i in ITEMS), "price_max": max(i[4] for i in ITEMS),
        "special": [("芝麻菜 + 樱桃萝卜 组合", "原价 19 元", 15.0),
                    ("香草三件套（迷迭香/罗勒/薄荷）", "原价 20 元", 15.0),
                    ("腐熟堆肥 2 kg", "会员免费领取，每户限 1 袋", 0.0)],
    }
    d = Doc(1200, 1500, PAPER)
    header(d, 1200, 110, "屋顶市集 · 今日价目与产地牌",
           "%s · %s · %s" % (data["date"], data["time"], data["place"]),
           right=[("全部来自 3 号楼屋顶 · 当日采收", "#9DB0A2FF", 15),
                  ("会员价需出示会员卡", "#6E8478FF", 14)], title_size=28)

    card(d, 32, 134, 1136, 880)
    section(d, 56, 154, 1088, "今日供应（%d 项）" % len(ITEMS))
    COLW = 536
    for i, it in enumerate(ITEMS):
        c, r = i % 2, i // 2
        x = 56 + c * (COLW + 16)
        y = 196 + r * 116
        if r % 2 == 0:
            d.box(x - 8, y - 6, COLW, 108, "#FBF8F0FF", radius=8)
        d.ctext(x, y, it[0], 20, INK, "BOLD", w=200, h=28)
        d.ctext(x, y + 30, it[1], 13, MUTE, w=300, h=18)
        d.ctext(x, y + 52, "箱位 %s · 采收 %s" % (it[2], it[3]), 13, LEAF, family=MONO,
                w=300, h=18)
        d.ctext(x + 320, y - 2, "%.1f" % it[4], 30, INK, "BOLD", family=MONO, w=120,
                h=36, align="CENTER_RIGHT")
        d.ctext(x + 446, y + 6, "元", 14, MUTE, w=30, h=20)
        if it[5] > 0:
            d.ctext(x + 320, y + 40, "会员 %.1f 元" % it[5], 14, SUN, "BOLD",
                    family=MONO, w=156, h=20, align="CENTER_RIGHT")
        else:
            d.ctext(x + 320, y + 40, "会员免费", 14, SUN, "BOLD", w=156, h=20,
                    align="CENTER_RIGHT")
        d.box(x, y + 100, COLW - 16, 1, "#F1EDE2FF")

    card(d, 32, 1038, 1136, 152, "#FBF8F0FF")
    section(d, 56, 1056, 1088, "今日特惠")
    for i, (name, note, price) in enumerate(data["special"]):
        x = 56 + i * 366
        d.box(x, 1096, 342, 76, CARD, radius=10, border="1 SOLID " + SUN_P)
        d.ctext(x + 14, 1106, clip(name, 15, 314), 15, INK, "BOLD", w=314, h=22)
        d.ctext(x + 14, 1132, clip(note, 13, 200), 13, MUTE, w=200, h=18)
        d.ctext(x + 214, 1126, ("%.1f 元" % price) if price else "免费", 20, CLAY,
                "BOLD", family=MONO, w=116, h=26, align="CENTER_RIGHT")

    card(d, 32, 1214, 1136, 242)
    qr_block(d, 56, 1238, 160, seed=29)
    d.ctext(56, 1404, "扫码查看本周产量（示意）", 12, MUTE, w=160, h=16, align="CENTER")
    d.text(244, 1240, "购买与产地说明", 18, INK, "BOLD")
    lines = [
        "支付：现金 / 微信 / 支付宝；会员价需出示会员卡或卡号。",
        "产地：全部来自 3 号楼屋顶 46 个种植箱，采收日期标在每项下方。",
        "保鲜：叶菜请当日冷藏；香草可插水杯存放 3–5 天。",
        "包装：请自备袋子，摊位提供可循环菜筐（押金 10 元）。",
        "收入：扣包装与耗材后，余款进入种子基金，用于下季采购与工作坊。",
    ]
    for i, s in enumerate(lines):
        y = 1274 + i * 26
        d.ctext(244, y, clip(s, 14, 900), 14, INK_SOFT, w=900, h=20)
    d.box(244, 1410, 900, 1, RULE)
    d.ctext(244, 1418, "%s 项目、价格与产地均为虚构演示，不代表任何真实摊位的售价。"
            % DSL_ONLY, 12, MUTE, w=900, h=18)

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (N7, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % N7), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data


def build8(ver="v1", outdir=None):
    seats = sum(s[4] for s in SESSIONS)
    left = sum(s[5] for s in SESSIONS)
    data = {
        "project": PROJECT_FULL, "season": "2026 春季",
        "sessions": [{"date": s[0], "time": s[1], "title": s[2], "age": s[3],
                      "seats": s[4], "left": s[5], "content": s[6]} for s in SESSIONS],
        "seats_total": seats, "seats_left": left,
        "stages": [{"name": s[0], "note": s[1]} for s in STAGES],
        "notes": ["每场由 2 位志愿者带领，家长可全程陪同",
                  "提供围裙、手套与全部材料，无需自带",
                  "活动在屋顶进行，请穿防滑鞋并注意防晒",
                  "如遇雨天改到 1 楼社区活动室"],
        "signup": "社区服务站登记，或扫描下方图形码填写表单",
    }
    d = Doc(1240, 1748, PAPER)
    # ---------------------------------------------------------------- top
    d.box(0, 0, 1240, 330, LEAF)
    d.box(0, 322, 1240, 8, SUN)
    for i in range(5):
        d.disc(120 + i * 260, 60 + (i % 2) * 26, 26 + (i % 3) * 10, "#3E7A54FF")
    sun(d, 1080, 92, 44, SUN_P)
    seed_mark(d, 76, 96, 26, CARD, LEAF)
    d.text(120, 66, PROJECT, 26, CARD, "BOLD")
    d.text(120, 104, "社区种子图书馆 × 屋顶农场", 14, "#C9DFCFFF")
    d.text(76, 168, "种子的旅行", 62, CARD, "BOLD")
    d.text(76, 246, "春季儿童工作坊 · 三场 · 5–10 岁", 24, SUN_P)
    d.ctext(700, 300, "免费参加 · 名额共 %d 个 · 剩余 %d 个" % (seats, left), 15,
            "#C9DFCFFF", family=MONO, w=464, h=22, align="CENTER_RIGHT")

    # ---------------------------------------------------------------- cycle
    card(d, 32, 362, 1176, 300)
    d.text(56, 380, "一粒种子会经历什么？", 18, INK, "BOLD")
    cx = [180, 460, 740, 1020]
    for i in range(3):
        d.dashed(cx[i] + 74, 512, cx[i + 1] - 74, 512, LEAF_L, 2, 10, 8)
    for i, (name, note) in enumerate(STAGES):
        x = cx[i]
        d.disc(x, 512, 128, [SUN_P, LEAF_P, "#DCEBE2FF", "#F3E6D8FF"][i])
        d.disc(x, 512, 104, CARD)
        if i == 0:
            d.disc(x, 512, 34, SOIL)
            d.seg(x - 14, 512, x + 14, 512, "#8A6242FF", 4)
        elif i == 1:
            sprout(d, x, 546, 66, LEAF, 7)
            d.disc(x, 550, 14, SOIL)
        elif i == 2:
            sprout(d, x, 552, 84, LEAF, 8)
            d.disc(x - 30, 486, 26, LEAF_L)
            d.disc(x + 30, 498, 22, LEAF_L)
        else:
            sprout(d, x, 548, 70, LEAF, 7)
            for k, (dx, dy) in enumerate(((-40, -6), (0, -18), (40, -6))):
                d.disc(x + dx, 470 + dy, 24, SUN)
        d.ctext(x - 90, 590, name, 18, INK, "BOLD", w=180, h=24, align="CENTER")
        d.ctext(x - 106, 616, clip(note, 12, 212), 12, MUTE, w=212, h=16, align="CENTER")

    # ---------------------------------------------------------------- sessions
    card(d, 32, 686, 1176, 400)
    section(d, 56, 706, 1128, "三场工作坊")
    for i, s in enumerate(SESSIONS):
        y = 748 + i * 108
        d.box(56, y, 116, 92, [SUN_P, LEAF_P, "#DCEBE2FF"][i], radius=10)
        d.ctext(56, y + 14, s[0], 24, INK, "BOLD", family=MONO, w=116, h=30,
                align="CENTER")
        d.ctext(56, y + 50, s[1].split(" ")[0], 12, MUTE, w=116, h=18, align="CENTER")
        d.ctext(56, y + 66, s[1].split(" ")[1], 12, MUTE, family=MONO, w=116, h=18,
                align="CENTER")
        d.ctext(196, y + 8, s[2], 22, INK, "BOLD", w=460, h=30)
        d.ctext(196, y + 42, clip(s[6], 14, 560), 14, INK_SOFT, w=560, h=22)
        tag(d, 196, y + 68, "适龄 %s" % s[3], SKY, size=13, height=22)
        d.ctext(680, y + 16, "%d / %d 已报" % (s[4] - s[5], s[4]), 14, MUTE,
                family=MONO, w=140, h=20, align="CENTER_RIGHT")
        bar(d, 836, y + 18, 200, 12, 1 - s[5] / float(s[4]), LEAF)
        d.ctext(1050, y + 12, "剩 %d 位" % s[5], 15, CLAY if s[5] <= 5 else LEAF,
                "BOLD", family=MONO, w=120, h=22, align="CENTER_RIGHT")

    # ---------------------------------------------------------------- notes
    card(d, 32, 1110, 1176, 300)
    section(d, 56, 1130, 1128, "家长须知")
    for i, s in enumerate(data["notes"]):
        x = 56 + (i % 2) * 580
        y = 1176 + (i // 2) * 96
        d.box(x, y, 540, 76, "#FBF8F0FF", radius=10)
        d.disc(x + 34, y + 38, 36, LEAF_P)
        d.ctext(x + 16, y + 22, "%d" % (i + 1), 20, LEAF, "BOLD", family=MONO, w=36,
                h=32, align="CENTER")
        d.ctext(x + 76, y + 16, clip(s, 15, 440), 15, INK_SOFT, w=440, h=44)

    # ---------------------------------------------------------------- signup
    card(d, 32, 1434, 1176, 250)
    qr_block(d, 56, 1458, 170, seed=41)
    d.ctext(56, 1634, "扫码报名（示意图形）", 12, MUTE, w=170, h=16, align="CENTER")
    d.text(252, 1460, "怎么报名", 20, INK, "BOLD")
    d.ctext(252, 1496, data["signup"], 15, INK_SOFT, w=920, h=22)
    d.ctext(252, 1526, "报名时请说明孩子年龄；名额按登记顺序先到先得。", 15, MUTE,
            w=920, h=22)
    d.ctext(252, 1556, "活动由志愿者带领，不收取费用；材料来自种子基金。", 15, MUTE,
            w=920, h=22)
    d.box(252, 1590, 920, 1, RULE)
    d.ctext(252, 1598, "咨询：云栖里社区服务站（虚构）· 每周二、四 14:00–18:00", 14,
            INK_SOFT, w=920, h=20)
    d.ctext(252, 1626, "%s 项目、场次与名额均为虚构演示。" % DSL_ONLY, 12, MUTE,
            w=920, h=18)

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (N8, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % N8), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data
