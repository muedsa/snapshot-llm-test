"""件-06「100 GB 的两行小字」1920×1080（套餐详情/投屏页）。

原始口径：详情页一行大字"100 GB"+两行小字"高速流量 40 GB，超出后降至 1 Mbps，次月恢复"。
换算：把 30 天逐日用量累加成面积，找出撞 40 GB 的那一天与那一刻；再把 1 Mbps 翻译成
"这件事能不能做"。
行动：40 GB÷30 天＝每日预算 1.33 GB，与实际日均对照，给出中途预警线。

用量、费率、所需带宽全为演示值（demo.json case06，seed 固定）；不冒充任何运营商报价。
"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for _p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B06"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import b06kit as K  # noqa: E402

W, H = 1920, 1080
NOMINAL_GB = 100.0          # 详情页大字（演示口径，不是数据里的用量）
YMAX_GB = 100.0             # 面积图纵轴上限，与大字同高，让"没用满"看得见

# 面积图几何
PX, PDW = 108.0, 38.0       # 30 天 × 38 px = 1140 px
PY, PH = 414.0, 340.0
BY = PY + PH                # 762 基线


def gy(gb):
    return BY - gb / YMAX_GB * PH


def dashes(d, x0, x1, y, color, seg=10, gap=8, thick=2):
    cx = x0
    while cx < x1:
        d.rect(cx, y, min(seg, x1 - cx), thick, color)
        cx += seg + gap


def build():
    d, tf = K.doc(W, H, ground="dark")
    P = d.P
    c = K.data()["cases"]["case06"]
    usage, cum = c["usage"], c["cum"]
    cap = c["cap_gb"]
    n = len(usage)
    PW = PDW * n
    cap_y = gy(cap)
    x_hit = PX + ((c["hit_day"] - 1) + (c["hit_hour"] + c["hit_minute"] / 60.0) / 24.0) * PDW
    budget = cap / n
    actual = c["month_total"] / n
    over_days = [i + 1 for i, u in enumerate(usage) if u > budget]
    rate15 = cum[14] / 15.0
    proj_day = cap / rate15
    hours_at_1m = c["gb_after_cap_hours"]

    # ---------- 页眉 ----------
    d.rect(0, 0, W, 92, K.BASE)
    d.rect(0, 90, W, 2, P["line"])
    K.tlab(d, tf, "h-t", 40, 14, 900, 40, "「100 GB」的两行小字", 32, P["t0"])
    K.tlab(d, tf, "h-s", 40, 56, 900, 24,
           "大字是 100 GB，小字是 40 GB 后降到 1 Mbps——把 30 天摊开看哪天开始卡",
           15, P["t2"])
    K.chip(d, tf, "h-c1", W - 400, 22, 120, 42, "演示数据", P["t2"], P["card2"],
           border="1 SOLID " + P["border"], size=15)
    K.chip(d, tf, "h-c2", W - 270, 22, 230, 42, "不报运营商价格", P["t1"],
           P["panel2"], border="1 SOLID " + P["border"], size=15)

    # ---------- ① 原始口径 ----------
    x1, cy1, w1 = K.card(d, tf, "c1", 40, 104, 1840, 200,
                         "① 详情页给你的：一行大字，两行小字", sub=c["detail"])
    K.mono(d, tf, "c1-big", x1, cy1 - 6, 300, 56, "%g" % NOMINAL_GB, 46, P["t0"])
    K.tlab(d, tf, "c1-unit", x1 + 118, cy1 + 14, 160, 30, "GB（大字）", 17, P["t2"])
    K.tlab(d, tf, "c1-note", x1, cy1 + 60, 500, 24,
           "本月你实际用掉 %.1f GB——从没接近过大字" % c["month_total"], 14, P["t1"])
    tiles = [("高速流量额度", "%g GB" % cap, "超出后立刻降速"),
             ("降速后的速度", "%g Mbps" % c["speed_after"], "≈ %.2f GB/小时" % (c["speed_after"] * 3600.0 / 8.0 / 1000.0)),
             ("月费", "¥%d" % c["price"], "演示价格"),
             ("撞线时刻", "第 %d 天 %02d:%02d" % (c["hit_day"], c["hit_hour"], c["hit_minute"]),
              "之前 %d 天／之后 %d 天" % (c["fast_days"], c["slow_days"]))]
    for i, (lab, val, sub) in enumerate(tiles):
        bx = x1 + 560 + i * 288
        K.panel(d, bx, cy1 - 6, 270, 88, P["card2"], radius=12,
                border="1 SOLID " + P["border"])
        K.tlab(d, tf, "c1-l%d" % i, bx + 16, cy1 + 4, 240, 20, lab, 12, P["t2"])
        K.mono(d, tf, "c1-v%d" % i, bx + 16, cy1 + 26, 240, 28, val, 20, P["t0"])
        K.tlab(d, tf, "c1-s%d" % i, bx + 16, cy1 + 58, 240, 20, sub, 12, P["t2"])
    assert cy1 + 82 <= 104 + 200 - 22, cy1

    # ---------- ② 逐日累计面积 ----------
    x2, cy2, w2 = K.card(d, tf, "c2", 40, 316, 1240, 568,
                         "② 换算：把 30 天用量累起来，看它什么时候撞上 40 GB",
                         sub="柱高＝当天累计已用 GB；青色在额度内，珊瑚色是降速之后还在用的部分")
    for gb in (0, 20, 40, 60, 80, 100):
        yy = gy(gb)
        K.mono(d, tf, "c2-y%d" % gb, 62, yy - 10, 38, 20, "%d" % gb, 12, P["t2"],
               align="END")
        if gb:
            d.rect(PX, yy, PW, 1, P["grid"])
    d.line(PX, BY, PX + PW, BY, 2, P["axis"])
    for i in range(n):
        top = gy(cum[i])
        cx = PX + i * PDW
        teal_h = BY - max(top, cap_y)
        if teal_h > 0.5:
            d.rect(cx, max(top, cap_y), PDW - 2, teal_h, P["teal"], radius=2)
        if top < cap_y:
            d.rect(cx, top, PDW - 2, cap_y - top, P["coral"], radius=2)
    dashes(d, PX, PX + PW, cap_y, P["gold"])
    K.mono(d, tf, "c2-cap", PX + 6, cap_y - 28, 246, 22,
           "高速额度 %g GB（虚线）" % cap, 13, P["gold"])
    d.line(x_hit, PY, x_hit, BY, 2, P["coral"])
    K.mono(d, tf, "c2-hit", x_hit - 232, cap_y - 58, 224, 22,
           "第 %d 天 %02d:%02d 起降速" % (c["hit_day"], c["hit_hour"], c["hit_minute"]),
           14, P["coral"], align="END")
    K.mono(d, tf, "c2-end", PX + PW - 250, gy(cum[-1]) - 30, 246, 22,
           "月末累计 %.1f GB" % cum[-1], 13, P["t1"], align="END")
    for i in range(n):
        d.rect(PX + i * PDW, gy(budget * (i + 1)) - 1, PDW - 2, 3, P["mist"])
    K.mono(d, tf, "c2-bud", PX + 6, PY + 40, 620, 22,
           "灰线＝每天 %.2f GB 的预算线：跑满 %d 天正好 %g GB" % (budget, n, cap),
           13, P["t2"])
    K.tlab(d, tf, "c2-gap", PX + 6, PY + 68, 760, 22,
           "实际曲线在第 %d 天穿线，之后 %d 天用的 %.2f GB 都发生在 1 Mbps 之下。"
           % (c["hit_day"], c["slow_days"], c["gb_after_cap"]), 13, P["t2"])
    d.rect(PX, PY, PW, 2, P["mist"])
    K.mono(d, tf, "c2-nom", PX + 4, PY + 8, 300, 22,
           "大字 %g GB（本月最高累计 %.1f GB）" % (NOMINAL_GB, cum[-1]), 13, P["t2"])
    SY, SH = 766.0, 40.0
    mx_u = max(usage)
    K.tlab(d, tf, "c2-dl", 62, SY + 10, 40, 20, "日用", 12, P["t2"])
    for i, u in enumerate(usage):
        hh = u / mx_u * SH
        d.rect(PX + i * PDW, SY + (SH - hh), PDW - 2, hh,
               P["coral"] if i + 1 in over_days else P["mist"], radius=2)
    for day in (1, 5, 10, 15, 22, 25, 30):
        K.mono(d, tf, "c2-x%d" % day, PX + (day - 1) * PDW - 18, SY + SH + 6, 40, 20,
               "%d 日" % day, 12, P["t2"], align="CENTER")
    K.tlab(d, tf, "c2-f1", 62, SY + SH + 30, 1180, 22,
           "珊瑚色日用量＝超过每日预算 %.2f GB 的日子（%d 天）；降速后又用掉 %.2f GB，"
           "按 %g Mbps 折算需要 %.1f 小时连续传输。"
           % (budget, len(over_days), c["gb_after_cap"], c["speed_after"], hours_at_1m),
           13, P["t2"])
    assert SY + SH + 52 <= 316 + 568 - 22, SY + SH + 52

    # ---------- ③ 1 Mbps 能做什么 ----------
    x3, cy3, w3 = K.card(d, tf, "c3", 1304, 316, 576, 280,
                         "③ 降速之后：1 Mbps 能做什么",
                         sub="所需带宽为演示估值，够不够按 %g Mbps 判" % c["speed_after"])
    ry = cy3
    for i, it in enumerate(c["can_do"]):
        ok = it["ok"]
        K.tlab(d, tf, "c3-n%d" % i, x3, ry, 300, 22, it["s"], 14,
               P["t0"] if ok else P["t1"])
        K.mono(d, tf, "c3-v%d" % i, x3 + 300, ry, 86, 22, "%g Mbps" % it["need"], 13,
               P["t2"], align="END")
        K.chip(d, tf, "c3-c%d" % i, x3 + 398, ry - 1, 134, 24,
               "还能用" if ok else "会卡", P["t0"] if ok else "#10181C",
               P["teal"] if ok else P["coral"], size=13)
        ry += 24
    assert ry - 3 <= 316 + 280 - 22, ry

    # ---------- ④ 行动 ----------
    x4, cy4, w4 = K.card(d, tf, "c4", 1304, 608, 576, 276, "④ 行动：把额度摊到每天",
                         sub="换算完只剩三个数")
    rows = [("每日预算", "%g GB ÷ %d 天 ＝ %.2f GB" % (cap, n, budget), P["teal"]),
            ("实际日均", "%.1f GB ÷ %d ＝ %.2f GB（超预算 %.0f%%）"
             % (c["month_total"], n, actual, (actual / budget - 1) * 100), P["coral"]),
            ("超预算天数", "%d 天（前 5 个：%s）" % (len(over_days),
                          "、".join(str(i) for i in over_days[:5])), P["gold"]),
            ("中途预警线", "第 15 天已用 %.1f GB，按这个速度第 %d 天见底"
             % (cum[14], int(proj_day) + 1), P["t0"])]
    ry = cy4
    for i, (lab, val, col) in enumerate(rows):
        K.tlab(d, tf, "c4-l%d" % i, x4, ry, 130, 22, lab, 13, P["t2"])
        K.tlab(d, tf, "c4-v%d" % i, x4 + 136, ry, w4 - 136, 22, val, 14, col,
               align="END" if i < 3 else "START")
        ry += 32
    K.chip(d, tf, "c4-act", x4, ry + 2, w4, 34,
           "把每日提醒设在 %.2f GB；第 15 天过 %.0f GB 就开始省着用" % (budget, cum[14]),
           "#10181C", P["gold"], size=14)
    assert ry + 36 <= 608 + 276 - 22, ry

    # ---------- ⑤ 口径与限制 ----------
    nb = K.note_band(d, tf, "c5", 40, 900, 1840, [
        "口径：面积按逐日累计（当天用量记在当天末尾，故柱形是台阶而不是斜线）；"
        "撞线时刻＝额度剩余÷当日用量，按 24 小时线性摊到那一天。",
        "100 GB、40 GB、1 Mbps、¥39、30 天用量与各应用所需带宽均为演示值，"
        "不对应任何在营套餐；降速后的实际体验还受基站拥塞与终端影响。",
    ], size=14)
    assert nb + 8 + 26 <= H - 12, nb
    K.credit(d, tf, "credit", 40, nb + 8, 1840, [
        "数据：tmp/%s/B06/research/demo.json（b06data.py case06，seed=%s）｜台阶宽 %g px/天，"
        "纵轴 %g GB ＝ %g px｜降速后 %.2f GB ÷ %g Mbps ＝ %.1f h 连续传输"
        % (RID, K.data()["seed"], PDW, YMAX_GB, PH, c["gb_after_cap"], c["speed_after"],
           hours_at_1m),
    ], size=12)
    info = {"case": "06", "kind": "everyday-info-reinvented", "canvas": [W, H],
            "hit": "第 %d 天 %02d:%02d" % (c["hit_day"], c["hit_hour"], c["hit_minute"]),
            "budget_per_day": round(budget, 3), "actual_per_day": round(actual, 3),
            "over_budget_days": over_days, "projection_day": round(proj_day, 2),
            "cum_day15": cum[14], "hours_at_1m": hours_at_1m,
            "blocked": [it["s"] for it in c["can_do"] if not it["ok"]]}
    return d, tf, info
