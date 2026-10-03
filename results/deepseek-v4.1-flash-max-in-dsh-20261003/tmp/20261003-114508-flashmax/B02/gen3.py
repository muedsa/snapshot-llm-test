# -*- coding: utf-8 -*-
"""B02 touchpoints 05-06: volunteer shift board and membership card."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kit import Doc, CJK, MONO, tw  # noqa: E402
from b02lib import *  # noqa: E402,F403

N5 = "t05-shift-board"
N6 = "t06-member-card"

VOLS = ["林昭", "周砚", "陈知远", "苏澜", "沈鹭", "何叶", "郑野", "白露", "许青"]
DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
DATES = ["03-09", "03-10", "03-11", "03-12", "03-13", "03-14", "03-15"]
SHIFTS = [("早班", "07:00–10:00"), ("午班", "12:00–15:00"), ("晚班", "17:30–19:30")]
TASKS = ["浇水", "通风", "除草", "追肥", "记录", "工具房", "接待"]
PLAN = [
    [("林昭", "浇水"), ("周砚", "通风"), ("陈知远", "除草")],
    [("苏澜", "浇水"), ("沈鹭", "记录"), ("何叶", "浇水")],
    [("郑野", "追肥"), ("白露", "工具房"), ("许青", "浇水")],
    [("林昭", "浇水"), ("周砚", "除草"), ("陈知远", "通风")],
    [("苏澜", "浇水"), ("沈鹭", "浇水"), ("何叶", "记录")],
    [("郑野", "接待"), ("白露", "浇水"), ("许青", "除草")],
    [("林昭", "浇水"), ("周砚", "工具房"), ("陈知远", "记录")],
]


def build5(ver="v1", outdir=None):
    counts = {}
    total = 0
    for c in PLAN:
        for nm, tk in c:
            counts[nm] = counts.get(nm, 0) + 1
            total += 1
    data = {
        "project": PROJECT_FULL, "week": "2026-03-09 — 03-15",
        "slots": total, "volunteers": len(counts),
        "shift_load": {nm: counts[nm] for nm in sorted(counts, key=lambda k: -counts[k])},
        "focus": ["本周进入番茄移栽窗口，2 号地块优先",
                  "周六屋顶市集，需 2 人负责摊位与收银",
                  "雨水桶液位偏低，晚上班负责补水",
                  "记录表本周开始登记每箱产量"],
        "weather": [("周一–周三", "晴，7–16 ℃", "正常排班"),
                    ("周四", "小雨，9–14 ℃", "户外浇水取消，改为检查排水"),
                    ("周五–周日", "多云转晴，10–19 ℃", "市集照常，注意防晒")],
        "contacts": [("值班协调", "林昭（虚构）· 站内广播 03"),
                     ("工具与耗材", "白露（虚构）· 工具房登记本"),
                     ("紧急情况", "物业值班室（虚构）· 内线 8119")],
    }
    d = Doc(1600, 1000, PAPER)
    header(d, 1600, 96, "志愿者排班与任务板 · 本周",
           "%s · %s · %d 个班次 · %d 位志愿者" % (SITE, data["week"], total, len(counts)),
           right=[("张贴于工具房 · 每周日更新", "#9DB0A2FF", 15),
                  ("值班结束请在小程序打卡", "#6E8478FF", 14)])

    # ---------------------------------------------------------------- grid
    GX, GY, GW, GH = 32, 120, 1120, 700
    card(d, GX, GY, GW, GH)
    LABW = 116
    cw = (GW - 40 - LABW) / 7.0
    rowh = (GH - 108 - 40) / 3.0
    for j in range(7):
        x = GX + 20 + LABW + j * cw
        d.box(x, GY + 40, cw - 6, 52, INK if j < 5 else LEAF, radius=8)
        d.ctext(x, GY + 46, DAYS[j], 16, CARD, "BOLD", w=cw - 6, h=22, align="CENTER")
        d.ctext(x, GY + 68, DATES[j], 13, "#B9C7BCFF", family=MONO, w=cw - 6, h=18,
                align="CENTER")
    for si, (sname, stime) in enumerate(SHIFTS):
        y = GY + 108 + si * rowh
        d.ctext(GX + 20, y + 24, sname, 16, INK, "BOLD", w=LABW - 12, h=22)
        d.ctext(GX + 20, y + 48, stime, 13, MUTE, family=MONO, w=LABW - 12, h=18)
        for j in range(7):
            x = GX + 20 + LABW + j * cw
            nm, tk = PLAN[j][si]
            d.box(x, y, cw - 6, rowh - 12, CARD, radius=8,
                  border="1 SOLID " + ("#D9E6DCFF" if si != 2 else "#F0E4C8FF"))
            d.disc(x + 18, y + 24, 22, mix(LEAF, PAPER, 0.82, alpha="FF"))
            d.ctext(x + 7, y + 13, nm[0], 14, LEAF, "BOLD", w=22, h=22, align="CENTER")
            d.ctext(x + 36, y + 12, nm, 15, INK, "BOLD", w=cw - 50, h=22)
            tag(d, x + 12, y + 44, tk, SKY if si != 2 else SUN, size=12, height=20)
            d.ctext(x + 12, y + 74, "已确认" if (j + si) % 4 else "待确认", 12,
                    MUTE if (j + si) % 4 else CLAY, w=cw - 24, h=18)
            if si == 2:
                d.ctext(x + 12, y + 92, "结束后关灯锁门", 11, MUTE, w=cw - 24, h=16)
    d.box(GX + 20, GY + GH - 44, GW - 40, 1, RULE)
    d.ctext(GX + 20, GY + GH - 36, "浅黄底色的晚班需要最后离场并锁门；雨天户外任务自动转为棚下作业。",
            13, MUTE, w=GW - 40, h=18)

    # ---------------------------------------------------------------- right
    RX, RW = 1176, 392
    card(d, RX, 120, RW, 268)
    section(d, RX + 20, 140, RW - 40, "本周重点")
    for i, s in enumerate(data["focus"]):
        y = 182 + i * 50
        d.disc(RX + 30, y + 9, 16, SUN)
        d.ctext(RX + 20, y + 1, "%d" % (i + 1), 13, CARD, "BOLD", family=MONO, w=20,
                h=18, align="CENTER")
        d.ctext(RX + 48, y, clip(s, 14, RW - 76), 14, INK_SOFT, w=RW - 76, h=36)

    card(d, RX, 404, RW, 244)
    section(d, RX + 20, 424, RW - 40, "天气与备选")
    for i, (k, v, note) in enumerate(data["weather"]):
        y = 466 + i * 58
        d.ctext(RX + 20, y, k, 14, INK, "BOLD", w=110, h=20)
        d.ctext(RX + 136, y, clip(v, 13, 236), 13, SKY, family=MONO, w=236, h=20)
        d.ctext(RX + 20, y + 22, clip(note, 13, RW - 40), 13, MUTE, w=RW - 40, h=18)

    card(d, RX, 664, RW, 156)
    section(d, RX + 20, 684, RW - 40, "联系与交接")
    for i, (k, v) in enumerate(data["contacts"]):
        y = 724 + i * 32
        d.ctext(RX + 20, y, k, 13, MUTE, w=90, h=20)
        d.ctext(RX + 116, y, clip(v, 13, RW - 136), 13, INK_SOFT, w=RW - 136, h=20)

    # ---------------------------------------------------------------- footer
    card(d, 32, 844, 1536, 120, "#FBF8F0FF")
    d.text(56, 862, "值班须知", 16, INK, "BOLD")
    notes = ["签到：到工具房扫描排班牌上的图形码",
             "记录：每次浇水/施肥后填写箱位记录卡",
             "安全：屋顶风大，禁止攀爬围栏与水箱",
             "交接：离开前在群里发一张全景照片"]
    for i, s in enumerate(notes):
        x = 56 + (i % 2) * 768
        y = 898 + (i // 2) * 30
        d.disc(x + 8, y + 9, 12, LEAF_L)
        d.ctext(x + 22, y, clip(s, 13, 700), 13, INK_SOFT, w=700, h=20)
    d.ctext(56, 962, "%s 项目、志愿者姓名与排班均为虚构演示。" % DSL_ONLY, 12, MUTE,
            w=1488, h=18)

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (N5, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % N5), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data


def build6(ver="v1", outdir=None):
    months = ["3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "1", "2"]
    used = [0, 1, 2]
    data = {
        "member": "周砚（虚构）", "card_no": "OS-M-0427", "tier": "共耕会员",
        "share": "每周 1 份（约 1.2 kg）", "valid": "2026-03-01 — 2027-02-28",
        "boxes": ["B02", "B17"], "pickup": "每周三 17:00–19:00 · 3 号楼屋顶工具房旁",
        "months_used": [months[i] for i in used],
        "benefits": ["每周采收份额", "每季借种 5 包", "工作坊优先报名", "市集摊位 8 折"],
        "fictional": True,
    }
    d = Doc(1012, 638, PAPER)
    # card body
    d.box(24, 24, 964, 590, CARD, radius=18, border="1 SOLID " + RULE,
          shadow="0 4 14 0 #1E2A2214 NORMAL")
    d.box(24, 24, 12, 590, LEAF, tl=18, bl=18)
    seed_mark(d, 84, 78, 22, LEAF, CARD)
    d.text(120, 56, PROJECT, 28, INK, "BOLD")
    d.text(120, 92, "社区种子图书馆 · 会员卡", 13, MUTE)
    d.ctext(700, 56, "2026 – 2027 生长年", 16, LEAF, "BOLD", family=MONO, w=256, h=22,
            align="CENTER_RIGHT")
    d.ctext(700, 84, "MEMBER CARD", 12, MUTE, family=MONO, w=256, h=18,
            align="CENTER_RIGHT")
    d.box(56, 128, 900, 1, RULE)

    d.text(56, 148, "持卡人", 13, MUTE)
    d.text(56, 170, data["member"], 36, INK, "BOLD")
    d.text(56, 222, "卡号", 13, MUTE)
    d.text(56, 242, data["card_no"], 22, LEAF, "BOLD", family=MONO)

    for i, (k, v) in enumerate([("等级", data["tier"]), ("份额", data["share"]),
                                ("有效期", data["valid"])]):
        x = 56 + i * 300
        d.text(x, 300, k, 13, MUTE)
        d.ctext(x, 320, clip(v, 15, 284), 15, INK, w=284, h=22)

    # punch row
    d.box(56, 366, 900, 1, RULE)
    d.text(56, 384, "份额领取记录（每月 1 格）", 13, MUTE)
    for i, m in enumerate(months):
        x = 60 + i * 74
        done = i in used
        d.disc(x + 20, 434, 34, LEAF if done else CARD,
               border="2 SOLID " + (LEAF if done else RULE))
        if done:
            d.seg(x + 10, 434, x + 18, 442, CARD, 4)
            d.seg(x + 18, 442, x + 32, 424, CARD, 4)
        d.ctext(x, 456, "%s 月" % m, 12, MUTE, family=MONO, w=40, h=18, align="CENTER")

    # benefits + barcode
    d.text(56, 496, "会员权益", 13, MUTE)
    for i, s in enumerate(data["benefits"]):
        x = 56 + (i % 2) * 300
        y = 518 + (i // 2) * 26
        d.disc(x + 6, y + 8, 10, LEAF_L)
        d.ctext(x + 18, y, s, 14, INK_SOFT, w=270, h=20)
    d.box(660, 500, 296, 56, CARD, radius=6, border="1 SOLID " + RULE)
    h = 9173
    x = 670
    while x < 946:
        h = (1103515245 * h + 12345) & 0x7FFFFFFF
        wbar = 1 + (h >> 8) % 3
        d.box(x, 508, wbar, 34, INK)
        x += wbar + 1 + (h >> 5) % 3
    d.ctext(660, 560, data["card_no"], 11, MUTE, family=MONO, w=296, h=16,
            align="CENTER")
    d.ctext(56, 584, clip(data["pickup"], 12, 580), 12, MUTE, w=580, h=16)
    d.ctext(660, 584, "卡面信息为虚构演示", 11, MUTE, w=296, h=16, align="CENTER_RIGHT")

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (N6, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % N6), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data
