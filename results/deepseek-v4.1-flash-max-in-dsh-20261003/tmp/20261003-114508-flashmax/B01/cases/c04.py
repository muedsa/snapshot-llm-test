# -*- coding: utf-8 -*-
"""B01 case-04 -- 家庭用药周计划（照护者用，竖版）.

The chip grid is generated from the prescription table, so the legend, the grid,
the daily pill counts and the refill run-out days can never disagree.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import Doc, CJK, MONO, clip, tw  # noqa: E402

NAME = "c04-med-plan"
W, H = 1120, 1620

BG = "#F1F5F9FF"
INK = "#0F172AFF"
CARD = "#FFFFFFFF"
LINE = "#E2E8F0FF"
DIM = "#64748BFF"
SUB = "#94A3B8FF"
RED = "#D92D20FF"

# id, full name, short name, dose, colour, indication, tablets in stock
DRUGS = [
    ("A", "苯磺酸氨氯地平", "氨氯地平", "5 mg", "#2563EBFF", "高血压", 28),
    ("B", "二甲双胍缓释片", "二甲双胍", "0.5 g", "#0E9F8FFF", "2 型糖尿病", 40),
    ("C", "阿托伐他汀钙", "阿托伐他汀", "20 mg", "#7C3AEDFF", "血脂异常", 14),
    ("D", "阿司匹林肠溶片", "阿司匹林", "100 mg", "#D97706FF", "抗血小板", 28),
    ("E", "碳酸钙 D3 片", "碳酸钙D3", "600 mg", "#DB2777FF", "补钙", 12),
]
SLOTS = [("早餐后", "07:30"), ("午餐后", "12:30"), ("晚餐后", "18:30"), ("睡前", "21:30")]
PLAN = {0: ["A", "B", "D"], 1: ["E"], 2: ["B"], 3: ["C"]}
DAYS = [("周一", "10/05"), ("周二", "10/06"), ("周三", "10/07"), ("周四", "10/08"),
        ("周五", "10/09"), ("周六", "10/10"), ("周日", "10/11")]


def build(ver="v1", outdir=None):
    short = {r[0]: r[2] for r in DRUGS}
    col_of = {r[0]: r[4] for r in DRUGS}
    daily = {r[0]: sum(1 for ids in PLAN.values() if r[0] in ids) for r in DRUGS}
    runout = {r[0]: (r[6] // daily[r[0]] if daily[r[0]] else 0) for r in DRUGS}
    data = {
        "patient": "陈素云（虚构）", "week": "2026-10-05 ~ 2026-10-11",
        "drugs": [{"id": r[0], "name": r[1], "dose": r[3], "indication": r[5],
                   "per_day": daily[r[0]], "stock_tablets": r[6],
                   "days_left": runout[r[0]],
                   "refill_by": ("提前 5 天" if runout[r[0]] <= 21 else "库存充足")}
                  for r in DRUGS],
        "daily_tablet_total": sum(daily.values()),
        "weekly_tablet_total": sum(daily.values()) * 7,
        "slot_counts": {SLOTS[s][0]: len(ids) for s, ids in PLAN.items()},
        "red_flag_rows": [r[0] for r in DRUGS if runout[r[0]] <= 14],
    }

    d = Doc(W, H, BG)
    # ---------------------------------------------------------------- header
    d.box(0, 0, W, 128, INK)
    d.box(0, 0, 8, 128, "#0E9F8FFF")
    d.text(32, 18, "家庭用药周计划", 32, "#FFFFFFFF", "BOLD")
    d.text(32, 62, "陈素云（虚构示例）· 72 岁 · 高血压 / 2 型糖尿病 / 血脂异常", 18,
           "#94A3B8FF")
    d.text(32, 92, "2026-10-05 ~ 10-11 · 每日 6 片 · 本周共 42 片 · 照护者：家属", 17,
           "#64748BFF")
    d.ctext(700, 18, "本周提醒", 17, "#7DD3FCFF", "BOLD", w=388, h=24,
            align="CENTER_RIGHT")
    d.ctext(700, 46, "10-09 复诊（内分泌科 09:00）", 17, "#FFFFFFFF", w=388, h=24,
            align="CENTER_RIGHT")
    d.ctext(700, 74, "血压 ≥ 150/95 时当日联系医生", 17, "#FCA5A5FF", w=388, h=24,
            align="CENTER_RIGHT")
    d.ctext(700, 100, "C、E 两种药余量不足，见下表", 15, "#94A3B8FF", w=388, h=22,
            align="CENTER_RIGHT")

    # ---------------------------------------------------------------- drug legend
    LX, LY, LW, LH = 32, 152, 1056, 336
    d.card(LX, LY, LW, LH, CARD, radius=14, border="1 SOLID " + LINE)
    d.text(LX + 20, LY + 14, "药品清单与库存", 19, INK, "BOLD")
    d.ctext(LX + 560, LY + 16, "余量 ≤ 14 天标红", 14, RED, w=456, h=22,
            align="CENTER_RIGHT")
    heads = [("代号", 20, 56, 0), ("药品名", 84, 300, 0), ("单次剂量", 396, 120, 0),
             ("适应症", 528, 160, 0), ("每日", 700, 100, 2), ("库存", 812, 100, 2),
             ("可服天数", 924, 108, 2)]
    for label, hx, hw, al in heads:
        d.ctext(LX + hx, LY + 46, label, 14, SUB, w=hw, h=20,
                align="CENTER_RIGHT" if al else "CENTER_LEFT")
    d.box(LX + 20, LY + 70, LW - 40, 1, LINE)
    for i, (did, name, sn, dose, col, ind, stock) in enumerate(DRUGS):
        y = LY + 84 + i * 42
        d.box(LX + 20, y + 6, 28, 28, col, radius=8)
        d.ctext(LX + 20, y + 6, did, 16, "#FFFFFFFF", "BOLD", family=MONO, w=28, h=28,
                align="CENTER")
        d.ctext(LX + 84, y + 8, name, 18, INK, w=300, h=26)
        d.ctext(LX + 396, y + 8, dose, 17, INK, family=MONO, w=120, h=26)
        d.ctext(LX + 528, y + 8, ind, 17, DIM, w=160, h=26)
        d.ctext(LX + 700, y + 8, "%d 次" % daily[did], 17, INK, family=MONO, w=100, h=26,
                align="CENTER_RIGHT")
        d.ctext(LX + 812, y + 8, "%d 片" % stock, 17, INK, family=MONO, w=100, h=26,
                align="CENTER_RIGHT")
        left = runout[did]
        d.ctext(LX + 924, y + 8, "%d 天" % left, 17,
                RED if left <= 14 else "#0E9F8FFF", "BOLD", family=MONO, w=108, h=26,
                align="CENTER_RIGHT")
        d.box(LX + 20, y + 40, LW - 40, 1, "#F1F5F9FF")
    d.box(LX + 20, LY + 296, LW - 40, 1, LINE)
    d.ctext(LX + 20, LY + 304, "库存与「可服天数」由处方表算出；可服天数 ≤ 14 天标红，请提前 5 天补货。",
            14, DIM, w=LW - 40, h=20)

    # ---------------------------------------------------------------- week grid
    GX, GY, GW, GH = 32, 504, 1056, 664
    d.card(GX, GY, GW, GH, CARD, radius=14, border="1 SOLID " + LINE)
    d.text(GX + 20, GY + 14, "一周服药格（每格可打勾）", 19, INK, "BOLD")
    d.ctext(GX + 640, GY + 16, "每日 6 片 · 本周 42 片", 16, DIM, w=396, h=24,
            align="CENTER_RIGHT")

    COLW = 131
    TX = GX + 20
    DAYX0 = TX + 104
    HY = GY + 56
    for j, (wd, dt) in enumerate(DAYS):
        x = DAYX0 + j * COLW
        d.box(x, HY, COLW - 6, 50, "#F8FAFCFF", radius=8, border="1 SOLID " + LINE)
        d.ctext(x, HY + 6, wd, 16, INK, "BOLD", w=COLW - 6, h=22, align="CENTER")
        d.ctext(x, HY + 26, dt, 14, DIM, family=MONO, w=COLW - 6, h=20, align="CENTER")
    d.ctext(TX, HY + 14, "时段", 15, DIM, w=96, h=22)

    ROWH = 138
    for s, (slot, clock) in enumerate(SLOTS):
        y = HY + 58 + s * ROWH
        d.box(TX, y, 96, ROWH - 10, "#F8FAFCFF", radius=10, border="1 SOLID " + LINE)
        d.ctext(TX, y + 14, slot, 17, INK, "BOLD", w=96, h=24, align="CENTER")
        d.ctext(TX, y + 40, clock, 15, DIM, family=MONO, w=96, h=22, align="CENTER")
        d.ctext(TX, y + 68, "%d 种" % len(PLAN[s]), 14, SUB, w=96, h=20, align="CENTER")
        for j in range(7):
            x = DAYX0 + j * COLW
            weekend = j >= 5
            d.box(x, y, COLW - 6, ROWH - 10, "#F5F3FF" if weekend else "#F8FAFCFF",
                  radius=10, border="1 SOLID " + LINE)
            for k, did in enumerate(PLAN[s]):
                cy = y + 10 + k * 36
                d.box(x + 8, cy, COLW - 22, 30, col_of[did], radius=8)
                d.ctext(x + 16, cy + 4, short[did], 13, "#FFFFFFFF", w=70, h=22)
                d.box(x + COLW - 34, cy + 7, 16, 16, "#FFFFFF55", radius=4)
                d.ctext(x + COLW - 34, cy + 7, did, 11, "#FFFFFFFF", "BOLD", family=MONO,
                        w=16, h=16, align="CENTER")

    # ---------------------------------------------------------------- bottom cards
    BY, BH = 1188, 396
    d.card(32, BY, 520, BH, CARD, radius=14, border="1 SOLID " + LINE)
    d.text(52, BY + 14, "用药提示与风险", 19, INK, "BOLD")
    tips = [
        ("服药顺序", "阿司匹林肠溶片整片吞服，不可掰开或嚼碎"),
        ("体位性低血压", "起床先坐 1 分钟；出现头晕立即坐下并记录"),
        ("漏服处理", "当天想起即补服；已到下次服药时间则跳过，不加倍"),
        ("血糖监测", "二甲双胍期间每周至少 3 次空腹血糖"),
        ("相互作用", "碳酸钙与阿司匹林间隔 2 小时以上服用"),
        ("复诊携带", "带本表与血压血糖记录；10-09 09:00 内分泌科"),
    ]
    for i, (k, v) in enumerate(tips):
        y = BY + 54 + i * 56
        d.box(52, y + 4, 4, 40, ["#0E9F8FFF", "#D97706FF", "#7C3AEDFF", "#2563EBFF",
                                 "#D92D20FF", "#0F172AFF"][i], radius=2)
        d.ctext(68, y, k, 16, INK, "BOLD", w=180, h=22)
        d.ctext(68, y + 22, clip(v, 15, 452), 15, DIM, w=452, h=20)

    d.card(568, BY, 520, BH, CARD, radius=14, border="1 SOLID " + LINE)
    d.text(588, BY + 14, "血压 / 血糖记录", 19, INK, "BOLD")
    d.text(588, BY + 46, "日期", 14, SUB)
    d.text(688, BY + 46, "血压 mmHg", 14, SUB)
    d.text(812, BY + 46, "血糖 mmol/L", 14, SUB)
    d.text(948, BY + 46, "备注", 14, SUB)
    d.box(588, BY + 68, 480, 1, LINE)
    for j, (wd, dt) in enumerate(DAYS):
        y = BY + 78 + j * 38
        d.ctext(588, y, "%s %s" % (dt, wd), 15, INK, family=MONO, w=100, h=24)
        d.box(688, y, 116, 28, "#F8FAFCFF", radius=6, border="1 SOLID " + LINE)
        d.box(812, y, 128, 28, "#F8FAFCFF", radius=6, border="1 SOLID " + LINE)
        d.box(948, y, 120, 28, "#F8FAFCFF", radius=6, border="1 SOLID " + LINE)
        d.box(588, y + 34, 480, 1, "#F1F5F9FF")
    d.box(588, BY + 352, 480, 1, LINE)
    d.ctext(588, BY + 358, "本表为演示作品；人名、药品与剂量均为虚构示例，实际用药请遵医嘱。",
            13, SUB, w=480, h=18)

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (NAME, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % NAME), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data


if __name__ == "__main__":
    out = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _, info = build("v1", out)
    print(json.dumps(info, ensure_ascii=False, indent=2))
