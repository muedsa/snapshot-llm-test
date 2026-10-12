# -*- coding: utf-8 -*-
"""B02 touchpoints 09-10: harvest log form and annual impact one-pager."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kit import Doc, CJK, MONO, tw  # noqa: E402
from b02lib import *  # noqa: E402,F403

N9 = "t09-harvest-log"
N10 = "t10-impact-report"

UPLOADS = [
    ("2026 年度参与人次", "1 860", "人次", LEAF, "+34 % 同比"),
    ("屋顶累计产量", "1 246", "kg", SUN, "+18 % 同比"),
    ("归还种子", "412", "包", SKY, "借出 386 包"),
    ("志愿者工时", "968", "小时", CLAY, "42 位志愿者"),
]
MONTHLY = [42, 58, 96, 148, 186, 214, 238, 226, 168, 132, 84, 56]
MONTH_LABELS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
FUNDING = [("种子与种苗采购", 38, LEAF), ("工具与耗材", 24, SKY),
           ("工作坊材料", 18, SUN), ("堆肥与土壤", 14, SOIL), ("其他", 6, MUTE)]
FLOW = [("借出", ["会员借种 386 包", "工作坊发放 124 包", "市集兑换 62 包"]),
        ("种植", ["屋顶箱位 46 个", "阳台种植 112 户", "学校地块 3 处"]),
        ("归还", ["会员归还 298 包", "社区交换 114 包", "留种工作坊 86 包"])]


def build9(ver="v1", outdir=None):
    data = {
        "project": PROJECT_FULL, "form_no": "FORM-H-2026-03",
        "plot": "3 号楼屋顶 · 2 号地块", "recorder": "周砚（虚构）",
        "month": "2026 年 3 月", "rows": 12,
        "quality": ["优", "良", "合格", "瑕疵"],
        "fields": ["日期", "箱位", "作物", "产量 kg", "品质", "备注"],
        "reminder": ["产量按可食部分称重，不带根与老叶",
                     "品质按四档勾选：优 / 良 / 合格 / 瑕疵",
                     "异常（虫害、裂果、缺素）请写在备注并拍照",
                     "每箱每月至少登记 1 次，未登记不参与季度评优"],
    }
    d = Doc(1480, 1050, PAPER)
    header(d, 1480, 96, "收获记录卡 · %s" % data["month"],
           "%s · %s · 表单编号 %s" % (data["plot"], PROJECT_FULL, data["form_no"]),
           right=[("记录人：%s" % data["recorder"], "#9DB0A2FF", 15),
                  ("每箱每月至少登记 1 次", "#6E8478FF", 14)])

    # ---------------------------------------------------------------- meta
    card(d, 32, 120, 1416, 104)
    for i, (k, v) in enumerate([("地块", "2 号地块（果菜区）"), ("箱位", "B05 / B06"),
                                ("记录人", data["recorder"]),
                                ("填表日期", "2026-03-__")]):
        x = 56 + i * 350
        d.ctext(x, 138, k, 13, MUTE, w=100, h=18)
        d.ctext(x, 162, v, 17, INK, "BOLD", w=320, h=24)
        d.box(x + 320, 150, 1, 60, RULE)
    d.ctext(56, 194, "填写说明：本卡按周填写，月末交到工具房记录夹；也可在服务站的平板端录入。",
            13, MUTE, w=1360, h=18)

    # ---------------------------------------------------------------- table
    card(d, 32, 244, 1416, 604)
    cols = [("日期", 56, 130), ("箱位", 186, 110), ("作物", 296, 220),
            ("产量 kg", 516, 140), ("品质", 656, 240), ("备注（虫害 / 天气 / 处置）", 896, 526)]
    for name, x, w in cols:
        d.ctext(56 + x - 56, 264, name, 14, INK, "BOLD", w=w, h=20)
    d.box(56, 290, 1368, 1, INK)
    for r in range(12):
        y = 300 + r * 45
        if r % 2 == 0:
            d.box(56, y, 1368, 45, "#FBF8F0FF")
        for name, x, w in cols:
            d.box(56 + x, y + 6, 1, 33, "#F1EDE2FF")
        d.ctext(66, y + 12, "2026-03-__", 14, "#C6C0B2FF", family=MONO, w=120, h=22)
        if r < 2:
            d.ctext(196, y + 12, ["B05", "B06"][r], 14, INK, family=MONO, w=100, h=22)
            d.ctext(306, y + 12, ["番茄", "黄瓜"][r], 14, INK, w=200, h=22)
        for k in range(4):
            bx = 666 + k * 58
            d.box(bx, y + 13, 18, 18, CARD, radius=4, border="1 SOLID " + LEAF_L)
            d.ctext(bx + 22, y + 12, data["quality"][k], 12, MUTE, w=34, h=20)
        # a single writing line per row doubles as the row divider
        d.box(516 + 10, 300 + r * 45 + 38, 878, 1, "#D8D2C4FF")
    d.box(56, 840, 1368, 1, INK)

    # ---------------------------------------------------------------- tally
    card(d, 32, 868, 900, 138, "#FBF8F0FF")
    d.text(56, 886, "本月累计（由记录汇总）", 16, INK, "BOLD")
    for i, (k, unit) in enumerate([("番茄", "kg"), ("黄瓜", "kg"), ("叶菜", "kg"),
                                   ("香草", "把")]):
        x = 56 + i * 214
        d.ctext(x, 924, k, 14, MUTE, w=100, h=20)
        d.box(x, 948, 130, 1, "#D8D2C4FF")
        d.ctext(x + 134, 942, unit, 12, MUTE, w=40, h=18)

    card(d, 948, 868, 500, 138, "#FBF8F0FF")
    d.text(972, 886, "核对与签字", 16, INK, "BOLD")
    d.ctext(972, 920, "记录人签字", 13, MUTE, w=110, h=18)
    d.box(972, 944, 200, 1, "#D8D2C4FF")
    d.ctext(1192, 920, "地块负责人签字", 13, MUTE, w=140, h=18)
    d.box(1192, 944, 200, 1, "#D8D2C4FF")
    d.ctext(972, 962, "汇总后请把本卡放回工具房 3 号文件夹。", 12, MUTE, w=440, h=16)

    d.ctext(32, 1020, "%s 项目与人物均为虚构演示；表单本身可直接打印使用。" % DSL_ONLY,
            12, MUTE, w=1416, h=16)

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (N9, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % N9), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data


def build10(ver="v1", outdir=None):
    total_funding = sum(f[1] for f in FUNDING)
    data = {
        "project": PROJECT_FULL, "year": 2026, "kpis": [
            {"label": k, "value": v, "unit": u, "delta": dl} for k, v, u, _c, dl in UPLOADS],
        "monthly": MONTHLY, "monthly_total": sum(MONTHLY),
        "peak_month": MONTH_LABELS[MONTHLY.index(max(MONTHLY))],
        "funding": [{"name": f[0], "pct": f[1]} for f in FUNDING],
        "funding_total_pct": total_funding,
        "flow": [{"stage": f[0], "items": f[1]} for f in FLOW],
        "quote": "一开始只是想换点种子，后来发现换的是「怎么把一件事做下去」。",
        "quote_by": "会员 LZ · 2025 年冬季回访（虚构）",
    }
    d = Doc(1200, 1200, PAPER)
    header(d, 1200, 100, "一粒 · 2026 年度影响一页",
           "%s · 数据周期 2026-01-01 — 12-31 · 全部为演示数据" % SITE,
           right=[("理事会 / 社区公示版", "#9DB0A2FF", 15),
                  ("版本 2027-01 · 编制：一粒工作组", "#6E8478FF", 14)])

    # ---------------------------------------------------------------- kpis
    for i, k in enumerate(data["kpis"]):
        x = 32 + i * 288
        card(d, x, 124, 272, 116)
        d.box(x, 124, 272, 4, [LEAF, SUN, SKY, CLAY][i], tl=RADIUS, tr=RADIUS)
        d.ctext(x + 18, 142, k["label"], 13, MUTE, w=236, h=18)
        d.ctext(x + 18, 164, k["value"], 34, INK, "BOLD", family=MONO, w=180, h=42)
        d.ctext(x + 18, 210, k["unit"], 14, MUTE, w=60, h=20)
        d.ctext(x + 84, 206, k["delta"], 13, [LEAF, SUN, SKY, CLAY][i], w=170, h=20,
                align="CENTER_RIGHT")

    # ---------------------------------------------------------------- monthly
    card(d, 32, 260, 1136, 300)
    d.text(56, 278, "每月参与人次", 17, INK, "BOLD")
    d.ctext(700, 280, "全年合计 %d 人次 · 峰值在 %s 月" % (sum(MONTHLY), data["peak_month"]),
            14, MUTE, w=444, h=22, align="CENTER_RIGHT")
    bx0, bx1, by0, by1 = 96, 1144, 340, 520
    top = 240.0
    for g in range(0, 5):
        y = by1 - (by1 - by0) * g / 4.0
        d.box(bx0, y, bx1 - bx0, 1, "#F1EDE2FF")
        d.ctext(bx0 - 14, y - 10, "%d" % round(top * g / 4.0), 12, MUTE, family=MONO,
                w=48, h=18, align="CENTER_RIGHT")
    bw = (bx1 - bx0) / 12.0
    for i, v in enumerate(MONTHLY):
        h = (by1 - by0) * v / float(top)
        x = bx0 + i * bw
        d.box(x + 10, by1 - h, bw - 20, h, LEAF if v == top else LEAF_L, radius=4)
        d.ctext(x, by1 - h - 22, "%d" % v, 12, INK, "BOLD", family=MONO, w=bw, h=18,
                align="CENTER")
        d.ctext(x, by1 + 8, "%s 月" % MONTH_LABELS[i], 12, MUTE, family=MONO, w=bw,
                h=18, align="CENTER")

    # ---------------------------------------------------------------- funding donut
    card(d, 32, 580, 556, 300)
    d.text(56, 598, "资金去向", 17, INK, "BOLD")
    cx, cy, r = 200, 742, 92
    a = -90.0
    for name, pct, col in FUNDING:
        span = 360.0 * pct / 100.0
        d.arc_fill(cx, cy, r * 0.62, r, col, a + 0.8, a + span - 0.8, step=6.0)
        a += span
    d.disc(cx, cy, r * 1.1, CARD)
    d.ctext(cx - 50, cy - 22, "100 %", 20, INK, "BOLD", family=MONO, w=100, h=26,
            align="CENTER")
    d.ctext(cx - 50, cy + 6, "种子基金", 12, MUTE, w=100, h=18, align="CENTER")
    for i, (name, pct, col) in enumerate(FUNDING):
        y = 636 + i * 44
        d.box(330, y + 6, 16, 16, col, radius=4)
        d.ctext(354, y + 2, clip(name, 14, 130), 14, INK_SOFT, w=130, h=22)
        d.ctext(488, y + 2, "%d %%" % pct, 14, col, "BOLD", family=MONO, w=70, h=22,
                align="CENTER_RIGHT")

    # ---------------------------------------------------------------- flow
    card(d, 612, 580, 556, 300)
    d.text(636, 598, "种子流向", 17, INK, "BOLD")
    for i, (stage, items) in enumerate(FLOW):
        x = 636 + i * 178
        d.box(x, 630, 160, 30, [LEAF, SKY, SUN][i], radius=8)
        d.ctext(x, 630, stage, 16, CARD, "BOLD", w=160, h=30, align="CENTER")
        for j, s in enumerate(items):
            y = 676 + j * 58
            d.box(x, y, 160, 50, "#FBF8F0FF", radius=8, border="1 SOLID " + RULE)
            d.ctext(x + 10, y + 6, clip(s, 13, 140), 13, INK_SOFT, w=140, h=20)
            d.ctext(x + 10, y + 26, "", 11, MUTE, w=140, h=16)
        if i < 2:
            d.seg(x + 162, 645, x + 174, 645, MUTE, 2)
            d.seg(x + 168, 640, x + 174, 645, MUTE, 2)
            d.seg(x + 168, 650, x + 174, 645, MUTE, 2)

    # ---------------------------------------------------------------- quote
    card(d, 32, 904, 1136, 172, "#FBF8F0FF")
    d.ctext(64, 934, "“", 56, LEAF_P, "BOLD", w=60, h=64)
    d.ctext(120, 938, data["quote"], 22, INK, w=1000, h=34)
    d.ctext(120, 984, data["quote_by"], 14, MUTE, w=1000, h=22)
    d.box(120, 1024, 1000, 1, RULE)
    d.ctext(120, 1032, "脚注：本页所有数字为脚本按月度表与资金表计算的演示数据，"
            "不代表任何真实机构的经营结果。" + DSL_ONLY, 12, MUTE, w=1000, h=18)

    d.ctext(32, 1104, "数据说明：参与人次 = 借种 + 工作坊 + 市集 + 维护打卡；"
            "产量为可食部分称重合计；种子归还率按包数统计。", 13, MUTE, w=1136, h=20)
    d.ctext(32, 1130, "本页可由脚本按 data/t10-impact-report.json 重新生成，"
            "柱高、扇区角度与百分比一一对应。", 13, MUTE, w=1136, h=20)

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (N10, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % N10), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data
