# -*- coding: utf-8 -*-
"""B01 case-07 -- 儿童疫苗接种时间轴（竖版，随访用）.

A fictional child's record: the timeline is generated from a milestone table, the
age of the child on the print date and every status badge are computed, and the
"delayed" row carries the two-month gap that the table actually contains.
"""
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import Doc, CJK, MONO, clip, tw  # noqa: E402

NAME = "c07-vaccine-timeline"
W, H = 1240, 1560

BG = "#F1F5F9FF"
INK = "#0F172AFF"
CARD = "#FFFFFFFF"
LINE = "#E2E8F0FF"
DIM = "#64748BFF"
SUB = "#94A3B8FF"
DONE = "#0E9F8FFF"
LATE = "#D97706FF"
NEXT = "#D92D20FF"
FUT = "#94A3B8FF"

BIRTH = date(2024, 8, 12)
TODAY = date(2026, 10, 8)

MILESTONES = [
    (0, "出生 24 小时内", ["卡介苗 ①", "乙肝疫苗 ①"], "done", "2024-08-12"),
    (1, "1 月龄", ["乙肝疫苗 ②"], "done", "2024-09-13"),
    (2, "2 月龄", ["脊灰灭活 ①"], "done", "2024-10-14"),
    (3, "3 月龄", ["脊灰灭活 ②", "百白破 ①"], "done", "2024-11-12"),
    (4, "4 月龄", ["脊灰减毒 ③", "百白破 ②"], "done", "2024-12-11"),
    (5, "5 月龄", ["百白破 ③"], "done", "2025-01-10"),
    (6, "6 月龄", ["乙肝疫苗 ③", "流脑 A ①"], "done", "2025-02-12"),
    (8, "8 月龄", ["麻腮风 ①", "乙脑减毒 ①"], "done", "2025-04-14"),
    (9, "9 月龄", ["流脑 A ②"], "done", "2025-05-13"),
    (18, "18 月龄", ["百白破 ④", "麻腮风 ②", "甲肝减毒 ①"], "late", "2026-04-20"),
    (24, "2 岁", ["乙脑减毒 ②", "甲肝减毒 ②"], "done", "2026-08-18"),
    (36, "3 岁", ["流脑 A ③"], "next", "2027-08-12 前后"),
    (48, "4 岁", ["脊灰减毒 ④"], "future", "2028-08-12 前后"),
    (72, "6 岁", ["白破 ①", "流脑 A ④"], "catchup", "2030-08-12 前后"),
]
STATUS = {
    "done": ("已完成", DONE),
    "late": ("延迟补种", LATE),
    "next": ("下次应种", NEXT),
    "future": ("未到时间", FUT),
    "catchup": ("补种评估", "#1D4ED8FF"),
}


def months_between(a, b):
    return (b.year - a.year) * 12 + (b.month - a.month) - (1 if b.day < a.day else 0)


def build(ver="v1", outdir=None):
    age_m = months_between(BIRTH, TODAY)
    done = sum(1 for m in MILESTONES if m[3] == "done")
    data = {
        "child": "示例儿童（虚构）", "birth": BIRTH.isoformat(),
        "print_date": TODAY.isoformat(), "age_months": age_m,
        "age_text": "%d 岁 %d 个月" % (age_m // 12, age_m % 12),
        "milestones_total": len(MILESTONES),
        "status_counts": {k: sum(1 for m in MILESTONES if m[3] == k) for k in STATUS},
        "doses_total": sum(len(m[2]) for m in MILESTONES),
        "doses_done": sum(len(m[2]) for m in MILESTONES if m[3] in ("done", "late")),
        "late_gap_days": (date(2026, 4, 20) - date(2026, 2, 12)).days,
        "milestones": [{"age_months": m[0], "label": m[1], "vaccines": m[2],
                        "status": m[3], "date": m[4]} for m in MILESTONES],
    }

    d = Doc(W, H, BG)
    # ---------------------------------------------------------------- header
    d.box(0, 0, W, 112, "#0F172AFF")
    d.box(0, 0, 8, 112, DONE)
    d.text(32, 16, "儿童疫苗接种时间轴", 30, "#FFFFFFFF", "BOLD")
    d.text(32, 58, "示例儿童（虚构）· 出生 2024-08-12 · 打印日期 2026-10-08 · 当前 %s"
           % data["age_text"], 17, "#94A3B8FF")
    d.text(32, 84, "共 %d 个接种节点 · %d 剂次 · 已完成 %d 剂次"
           % (len(MILESTONES), data["doses_total"], data["doses_done"]), 16, "#64748BFF")
    d.ctext(720, 18, "本表为演示作品，不构成医疗建议", 16, "#FCA5A5FF", "BOLD",
            w=488, h=24, align="CENTER_RIGHT")
    d.ctext(720, 48, "接种安排请以接种证与门诊通知为准", 16, "#CBD5E1FF", w=488, h=24,
            align="CENTER_RIGHT")
    for i, k in enumerate(["done", "late", "next", "future", "catchup"]):
        lab, col = STATUS[k]
        x = 720 + i * 98
        d.box(x, 84, 12, 12, col, radius=3)
        d.text(x + 18, 80, lab, 13, "#94A3B8FF")

    # ---------------------------------------------------------------- timeline
    GX, GY, GW, GH = 32, 132, 1176, 1290
    d.card(GX, GY, GW, GH, CARD, radius=14, border="1 SOLID " + LINE)
    d.text(GX + 20, GY + 14, "0 – 6 岁接种节点", 19, INK, "BOLD")
    d.ctext(GX + 400, GY + 16, "左侧为月龄，圆点颜色对应状态；延迟节点标出实际补种日期",
            15, DIM, w=756, h=24, align="CENTER_RIGHT")

    SPINE = GX + 196
    TOPY = GY + 60
    ROWH = 82
    d.box(SPINE + 1, TOPY + 41, 2, ROWH * (len(MILESTONES) - 1), "#E2E8F0FF")
    for i, (m, label, vac, status, when) in enumerate(MILESTONES):
        y = TOPY + i * ROWH
        mid = y + 41
        lab, col = STATUS[status]
        d.ctext(GX + 20, mid - 28, "%d" % m, 24, INK if status != "future" else SUB,
                "BOLD", family=MONO, w=76, h=30, align="CENTER_RIGHT")
        d.ctext(GX + 20, mid + 4, "月龄" if m != 0 else "出生", 12, SUB,
                w=76, h=16, align="CENTER_RIGHT")
        d.disc(SPINE + 1, mid, 16, CARD)
        d.disc(SPINE + 1, mid, 12, col)
        # connector
        d.box(SPINE + 10, mid, 26, 2, "#E2E8F0FF")
        # card
        cx, cw = SPINE + 40, GX + GW - 20 - (SPINE + 40)
        d.box(cx, y + 4, cw, ROWH - 14, "#F8FAFCFF" if status == "future" else CARD,
              radius=10, border="1 SOLID " + (col if status in ("next", "late") else LINE))
        d.box(cx, y + 4, 5, ROWH - 14, col, tl=10, bl=10)
        d.ctext(cx + 18, y + 12, label, 17, INK, "BOLD", w=150, h=24)
        vx = cx + 176
        for v in vac:
            vw = tw(v, 15) + 20
            d.box(vx, y + 13, vw, 24, "#EEF2F7FF", radius=12)
            d.ctext(vx, y + 13, v, 15, INK, w=vw, h=24, align="CENTER")
            vx += vw + 8
        d.ctext(cx + 18, y + 42, "实际日期：%s" % when, 14, DIM, family=MONO, w=260, h=20)
        if status == "late":
            orig = "计划 2026-02-12 · 延迟 %d 天" % data["late_gap_days"]
            d.ctext(cx + 290, y + 42, orig, 14, LATE, w=280, h=20)
        elif status == "next":
            d.ctext(cx + 290, y + 42, "距 3 岁剂次还有 %d 个月"
                    % max(0, 36 - data["age_months"]), 14, NEXT, w=280, h=20)
        elif status == "catchup":
            d.ctext(cx + 290, y + 42, "入学前查验，需提前预约", 14, "#1D4ED8FF", w=280, h=20)
        bw = tw(lab, 14) + 24
        d.box(cx + cw - bw - 16, y + 14, bw, 24, col, radius=12)
        d.ctext(cx + cw - bw - 16, y + 14, lab, 14, "#FFFFFFFF", "BOLD", w=bw, h=24,
                align="CENTER")
    d.box(GX + 20, GY + GH - 78, GW - 40, 1, LINE)
    d.ctext(GX + 20, GY + GH - 68, "说明：节点与剂次由脚本按接种表生成；本图为演示作品，「示例儿童」为虚构人物，"
            "疫苗名称与剂次仅作排布示例，实际接种请遵接种门诊安排。", 13, SUB, w=GW - 40, h=18)

    # ---------------------------------------------------------------- bottom
    d.card(32, 1444, 1176, 92, CARD, radius=14, border="1 SOLID " + LINE)
    notes = [("接种前", "携带接种证；发热或急性病期暂缓"), ("接种后", "留观 30 分钟；48 小时内避免剧烈活动"),
             ("记录", "记录体温与局部反应，保留接种凭证"),
             ("补种", "延迟剂次无需重新开始，听从门诊安排")]
    for i, (k, v) in enumerate(notes):
        x = 52 + i * 292
        d.box(x, 1458, 4, 60, [DONE, NEXT, "#1D4ED8FF", LATE][i], radius=2)
        d.ctext(x + 16, 1458, k, 16, INK, "BOLD", w=120, h=22)
        d.ctext(x + 16, 1482, clip(v, 14, 264), 14, DIM, w=264, h=36)

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
