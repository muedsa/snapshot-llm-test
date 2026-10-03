# -*- coding: utf-8 -*-
"""B02 touchpoints 03-04: seed-packet label and rooftop plot map."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kit import Doc, CJK, MONO, tw  # noqa: E402
from b02lib import *  # noqa: E402,F403

N3 = "t03-seed-label"
N4 = "t04-plot-map"

FAMILIES = [
    ("叶菜", LEAF, "#E7F0E8FF"), ("果菜", CLAY, "#F7E8E0FF"),
    ("根茎", SOIL, "#F0E9E0FF"), ("香草", SKY, "#E4EFF2FF"),
    ("花卉", SUN, "#FAF0D8FF"), ("休耕", MUTE, "#EEECE6FF"),
]
CROPS = ["菠菜", "生菜", "小白菜", "芝麻菜", "番茄", "黄瓜", "辣椒", "茄子",
         "樱桃萝卜", "胡萝卜", "大蒜", "迷迭香", "罗勒", "万寿菊", "向日葵", "草莓",
         "豌豆", "洋葱", "甜菜", "茴香", "薄荷", "百里香", "波斯菊", "休耕"]
FAM_IDX = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 1,
           0, 2, 2, 3, 3, 3, 4, 5]
OWNERS = ["LZ", "WQ", "CH", "YR", "SM", "ZT", "HL", "GX", "PY", "DJ", "FK", "NB",
          "LZ", "WQ", "CH", "YR", "SM", "ZT", "HL", "GX", "PY", "DJ", "FK", "—"]


def build3(ver="v1", outdir=None):
    data = {
        "packet_no": "OS-2026S-0417", "variety": "樱桃萝卜", "latin": "Raphanus sativus var. radicula",
        "lot": "LOT 25-0921", "germination_pct": 92, "purity_pct": 98.5,
        "net_seeds": 180, "sow_window": "3 月 — 9 月", "depth_mm": 10, "spacing_cm": "3 × 15",
        "days_to_harvest": "22–28 天", "returned_by": "会员 LZ · 2025 秋",
        "fictional": True,
    }
    d = Doc(560, 800, PAPER)
    # ---------------------------------------------------------------- band
    d.box(0, 0, 560, 140, LEAF)
    seed_mark(d, 44, 46, 20, CARD, LEAF)
    d.text(80, 28, PROJECT, 26, CARD, "BOLD")
    d.text(80, 62, "种子图书馆 · 借种包", 13, "#C9DFCFFF")
    d.ctext(300, 30, "2026 春季", 15, "#C9DFCFFF", family=MONO, w=228, h=22,
            align="CENTER_RIGHT")
    d.ctext(300, 56, data["packet_no"], 15, SUN_P, "BOLD", family=MONO, w=228, h=22,
            align="CENTER_RIGHT")
    d.ctext(300, 84, "借出后请登记播期", 12, "#A9C6B3FF", w=228, h=18,
            align="CENTER_RIGHT")

    # ---------------------------------------------------------------- illustration
    d.box(0, 140, 560, 196, "#F2EFE4FF")
    d.box(0, 296, 560, 40, "#E4DCC9FF")
    for k in range(14):
        d.box(20 + k * 40, 288, 12, 8, SOIL, radius=3)
    # radish bulb + leaves + root tip
    d.disc(300, 236, 84, CLAY)
    d.disc(300, 214, 58, "#C96A45FF")
    d.seg(300, 264, 300, 300, "#F0E4D6FF", 7)
    for dx, dy in ((-30, -46), (0, -58), (30, -44)):
        d.seg(300, 200, 300 + dx, 200 + dy, LEAF, 5)
    for dx, dy in ((-52, -18), (52, -18)):
        d.seg(300 + dx * 0.5, 200 + dy * 0.4, 300 + dx, 200 + dy, LEAF, 4)
    sun(d, 96, 200, 22, SUN)
    d.text(40, 152, "① 实物比例示意", 12, MUTE)
    d.text(420, 152, "1 : 1.4", 12, MUTE, family=MONO)

    # ---------------------------------------------------------------- names
    d.text(40, 350, "樱桃萝卜", 42, INK, "BOLD")
    d.text(40, 404, "Cherry Radish", 16, MUTE, family=MONO)
    d.ctext(40, 428, data["latin"], 12, MUTE, w=480, h=18)
    d.box(40, 452, 60, 4, LEAF, radius=2)

    # ---------------------------------------------------------------- table
    rows = [("批号 LOT", data["lot"]), ("发芽率", "%d %%" % data["germination_pct"]),
            ("净度", "%.1f %%" % data["purity_pct"]), ("每包粒数", "%d 粒" % data["net_seeds"]),
            ("播种适期", data["sow_window"]), ("播种深度", "%d mm" % data["depth_mm"])]
    for i, (k, v) in enumerate(rows):
        y = 476 + i * 30
        if i % 2 == 0:
            d.box(32, y - 3, 496, 28, "#FBF8F0FF", radius=4)
        d.ctext(40, y, k, 14, MUTE, w=120, h=20)
        d.ctext(170, y, v, 15, INK, "BOLD", family=MONO, w=350, h=20)

    # ---------------------------------------------------------------- strip
    for i, (lab, sub) in enumerate([("株行距", data["spacing_cm"] + " cm"),
                                    ("采收", data["days_to_harvest"]),
                                    ("归还", "留种 30 粒")]):
        x = 32 + i * 168
        d.box(x, 668, 152, 62, CARD, radius=8, border="1 SOLID " + RULE)
        d.ctext(x + 12, 678, lab, 13, MUTE, w=128, h=18)
        d.ctext(x + 12, 698, sub, 15, LEAF, "BOLD", w=128, h=22)

    # ---------------------------------------------------------------- barcode
    d.box(32, 744, 300, 38, CARD, radius=4, border="1 SOLID " + RULE)
    h = 48271
    x = 40
    while x < 324:
        h = (1103515245 * h + 12345) & 0x7FFFFFFF
        wbar = 1 + (h >> 8) % 3
        d.box(x, 750, wbar, 24, INK)
        x += wbar + 1 + (h >> 5) % 3
    d.ctext(32, 786, data["packet_no"], 11, MUTE, family=MONO, w=300, h=14)
    d.ctext(348, 744, "归还人：%s" % data["returned_by"], 12, INK_SOFT, w=180, h=16)
    d.ctext(348, 762, "种子来源：会员归还与社区交换", 11, MUTE, w=180, h=14)
    d.ctext(348, 778, "请勿食用包内干燥剂", 11, CLAY, w=180, h=14)

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (N3, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % N3), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data


def build4(ver="v1", outdir=None):
    fam_count = {}
    for i in FAM_IDX:
        fam_count[FAMILIES[i][0]] = fam_count.get(FAMILIES[i][0], 0) + 1
    claimed = sum(1 for o in OWNERS if o != "—")
    data = {
        "project": PROJECT_FULL, "site": SITE, "boxes_total": len(CROPS),
        "boxes_claimed": claimed, "boxes_free": len(CROPS) - claimed,
        "family_counts": fam_count,
        "taps": ["A 区东侧（1 号水龙头）", "B 区西侧（2 号水龙头）", "C 区北侧（雨水桶）"],
        "rules": ["每户最多认领 2 箱，每季重新分配一次",
                  "连续 3 周未维护的箱位自动释放",
                  "共用工具用完洗净归还工具房",
                  "禁止使用化学农药与除草剂",
                  "采摘后请在小程序登记产量"],
        "access": "屋顶东侧无障碍坡道宽 1.2 m，可通行轮椅；种植箱台面高 0.85 m。",
    }
    d = Doc(1500, 1000, PAPER)
    header(d, 1500, 96, "屋顶种植箱平面图 · 2026 春季",
           "%s · %d 个箱位（已认领 %d / 空闲 %d）· 更新于 2026-03-08"
           % (SITE, len(CROPS), claimed, len(CROPS) - claimed),
           right=[("北 ↑ 位于图面正上方", "#9DB0A2FF", 15),
                  ("比例 1 箱 ≈ 0.6 m × 1.2 m", "#6E8478FF", 14)])

    # ---------------------------------------------------------------- plan
    PX, PY, PW, PH = 32, 120, 1000, 700
    card(d, PX, PY, PW, PH)
    d.text(PX + 20, PY + 14, "3 号楼屋顶 · 平面图", 18, INK, "BOLD")
    OX, OY, OW, OH = PX + 40, PY + 62, 920, 560
    d.box(OX, OY, OW, OH, "#F2EFE4FF", radius=10, border="2 SOLID " + INK)
    # grid
    paper_grid(d, OX, OY, OW, OH, step=23, col="#E9E4D6FF")
    # water taps
    for i, (tx, ty) in enumerate([(OX + OW - 14, OY + 40), (OX + 14, OY + OH - 60),
                                  (OX + OW / 2, OY + 10)]):
        d.disc(tx, ty, 24, SKY)
        d.ctext(tx - 12, ty - 11, "水", 13, CARD, "BOLD", w=24, h=22, align="CENTER")
    # boxes: 8 columns x 3 rows inside the 920x560 roof outline
    BW, BH = 94, 154
    for i in range(len(CROPS)):
        r, c = i // 8, i % 8
        x = OX + 34 + c * (BW + 14)
        y = OY + 30 + r * (BH + 18)
        fname, fcol, fbg = FAMILIES[FAM_IDX[i]]
        d.box(x, y, BW, BH, fbg, radius=8, border="2 SOLID " + fcol)
        d.box(x, y, BW, 26, fcol, tl=8, tr=8)
        d.ctext(x, y, "B%02d" % (i + 1), 13, CARD, "BOLD", family=MONO, w=BW, h=26,
                align="CENTER")
        d.ctext(x + 8, y + 30, CROPS[i], 16, INK, "BOLD", w=BW - 16, h=22)
        d.ctext(x + 8, y + 52, fname, 12, fcol, w=BW - 16, h=18)
        d.box(x + 8, y + 74, BW - 16, 1, "#FFFFFFAA")
        d.ctext(x + 8, y + 80, OWNERS[i] if OWNERS[i] != "—" else "空闲",
                15, INK if OWNERS[i] != "—" else MUTE, "BOLD", family=MONO,
                w=BW - 16, h=24)
        for k in range(2):
            sprout(d, x + 30 + k * 34, y + 142, 26 + (k % 2) * 6, fcol, 3)
    # legend row inside the plan card
    LY = PY + PH - 62
    for i, (fname, fcol, fbg) in enumerate(FAMILIES):
        x = PX + 24 + i * 158
        d.box(x, LY + 4, 20, 12, fbg, radius=3, border="1 SOLID " + fcol)
        d.ctext(x + 28, LY, "%s %d 箱" % (fname, data["family_counts"].get(fname, 0)),
                13, INK_SOFT, w=124, h=20)
    d.box(PX + 24, PY + PH - 30, PW - 48, 1, RULE)
    d.ctext(PX + 24, PY + PH - 22, data["access"], 13, MUTE, w=PW - 48, h=18)

    # ---------------------------------------------------------------- right
    RX, RW = 1064, 404
    card(d, RX, 120, RW, 264)
    section(d, RX + 20, 140, RW - 40, "认领状态")
    for i, (fname, fcol, fbg) in enumerate(FAMILIES):
        y = 182 + i * 28
        cnt = data["family_counts"].get(fname, 0)
        d.ctext(RX + 20, y, fname, 14, INK_SOFT, w=70, h=20)
        bar(d, RX + 96, y + 5, 210, 10, cnt / 24.0, fcol)
        d.ctext(RX + 316, y, "%d" % cnt, 14, fcol, "BOLD", family=MONO, w=60, h=20,
                align="CENTER_RIGHT")
    d.box(RX + 20, 348, RW - 40, 1, RULE)
    d.ctext(RX + 20, 354, "共 %d 箱 · 已认领 %d 箱 · 空闲 %d 箱"
            % (len(CROPS), claimed, len(CROPS) - claimed), 13, MUTE, w=RW - 40, h=18)

    card(d, RX, 396, RW, 250)
    section(d, RX + 20, 410, RW - 40, "认领规则")
    for i, s in enumerate(data["rules"]):
        y = 452 + i * 36
        d.disc(RX + 28, y + 8, 12, LEAF_L)
        d.ctext(RX + 44, y, clip(s, 14, RW - 74), 14, INK_SOFT, w=RW - 74, h=22)

    card(d, RX, 662, RW, 158)
    section(d, RX + 20, 680, RW - 40, "水源与维护")
    for i, s in enumerate(data["taps"]):
        y = 722 + i * 32
        d.ctext(RX + 20, y, "·", 16, SKY, "BOLD", w=16, h=22)
        d.ctext(RX + 40, y, clip(s, 14, RW - 70), 14, INK_SOFT, w=RW - 70, h=22)

    d.ctext(32, 848, "每个箱位标注编号（B01–B24）、当季作物、科属配色与认领人代号；"
            "「空闲」表示本季尚未认领，可到服务站登记。", 14, INK_SOFT, w=1360, h=20)
    d.ctext(32, 876, "%s 项目、社区、作物表与认领人代号均为虚构演示。" % DSL_ONLY, 13,
            MUTE, w=1360, h=20)
    d.ctext(32, 906, "箱位数、科属统计与空闲数由脚本按作物表算出，与图面逐格一致。", 13,
            MUTE, w=1360, h=20)

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (N4, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % N4), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data
