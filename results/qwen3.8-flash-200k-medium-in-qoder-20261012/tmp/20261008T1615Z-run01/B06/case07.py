"""件-07「入口立牌的四行字」1200×1600（停车分段计费）。

原始口径：立牌四行字——免费 15 分钟／首小时 6 元／之后每 30 分钟 3 元／24 小时封顶 40 元。
换算：把四行字画成阶梯函数（分钟→元），并算出跳变点、封顶到达时刻与每小时均价。
行动：给出三个常见时长的应付金额、"跳变点前 1 分钟最划算"与跨天重复计费的临界。

费率与时长均为 self_defined_demo，不是任何停车场的现行价格；note 字段声明超 24 h 按日封顶重复计。
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

W, H = 1200, 1600
PX, PW = 118.0, 1000.0
PY, PH = 424.0, 400.0
BY = PY + PH
XMAX, YMAX = 1440.0, 40.0


def gx(m):
    return PX + m / XMAX * PW


def gy(c):
    return BY - c / YMAX * PH


def dashes(d, x0, x1, y, color, seg=10, gap=8, thick=2):
    cx = x0
    while cx < x1:
        d.rect(cx, y, min(seg, x1 - cx), thick, color)
        cx += seg + gap


def build():
    d, tf = K.doc(W, H, ground="dark")
    P = d.P
    c = K.data()["cases"]["case07"]
    tbl = dict((r["min"], r) for r in c["table"])
    steps = [(x["from"], x["to"], x["cost"]) for x in c["steps"]]
    jumps = [(f, cst) for f, _t, cst in steps if f > 0]

    # ---------- 页眉 ----------
    d.rect(0, 0, W, 92, K.BASE)
    d.rect(0, 90, W, 2, P["line"])
    K.tlab(d, tf, "h-t", 40, 14, 700, 40, "入口立牌的四行字", 32, P["t0"])
    K.tlab(d, tf, "h-s", 40, 56, 760, 24,
           "四行字是一条阶梯函数：这里把它画出来，再标出跳变点与封顶时刻", 15, P["t2"])
    K.chip(d, tf, "h-c1", W - 400, 22, 120, 42, "演示费率", P["t2"], P["card2"],
           border="1 SOLID " + P["border"], size=15)
    K.chip(d, tf, "h-c2", W - 270, 22, 230, 42, "停 7 小时不用口算", P["t1"],
           P["panel2"], border="1 SOLID " + P["border"], size=15)

    # ---------- ① 原始口径：四行字 ----------
    x1, cy1, w1 = K.card(d, tf, "c1", 40, 104, 1120, 210,
                         "① 立牌上写的：四行字，四个数")
    tiles = [("免费 %d 分钟" % c["free_min"], "0–%d min 都是 0 元" % c["free_min"]),
             ("首小时 %d 元" % c["first_price"],
              "%d–75 min 一律 %d 元" % (c["free_min"] + 1, c["first_price"])),
             ("之后每 %d 分钟 %d 元" % (c["step_min"], c["step_price"]),
              "每 %d min 跳一次价" % c["step_min"]),
             ("24 小时内封顶 %d 元" % c["cap"],
              "第 %d 分钟就到 %d 元" % (c["cap_at_min"], c["cap"]))]
    for i, (big, note) in enumerate(tiles):
        bx = x1 + i * 274
        K.panel(d, bx, cy1 - 6, 250, 88, P["card2"], radius=12,
                border="1 SOLID " + P["border"])
        K.tlab(d, tf, "c1-a%d" % i, bx + 14, cy1 + 4, 222, 26, big, 16, P["t0"],
               lines=2, valign="TOP")
        K.tlab(d, tf, "c1-b%d" % i, bx + 14, cy1 + 52, 222, 22, note, 12, P["t2"])
    assert cy1 + 82 <= 104 + 210 - 22, cy1

    # ---------- ② 阶梯函数 ----------
    x2, cy2, w2 = K.card(d, tf, "c2", 40, 326, 1120, 640,
                         "② 换算：分钟 → 元的阶梯",
                         sub="横轴 24 小时，纵轴 0–%d 元；每一横段是一个价格平台" % c["cap"])
    for yen in (0, 6, 12, 18, 24, 30, 36, 40):
        yy = gy(yen)
        K.mono(d, tf, "c2-y%d" % yen, 62, yy - 10, 44, 20, "%d" % yen, 12, P["t2"],
               align="END")
        if yen:
            d.rect(PX, yy, PW, 1, P["grid"])
    d.line(PX, BY, PX + PW, BY, 2, P["axis"])
    for m0, m1, cost in steps:
        col = P["gold"] if cost >= c["cap"] else P["teal"]
        hgt = BY - gy(cost)
        if hgt > 0.5:
            d.rect(gx(m0), gy(cost), max(2.0, gx(m1 + 1) - gx(m0) - 1), hgt, col,
                   radius=2)
    for m0, _m1, cost in steps[1:]:
        d.line(gx(m0), gy(cost - c["step_price"]), gx(m0), gy(cost), 2, P["coral"])
    dashes(d, PX, PX + PW, gy(c["cap"]), P["coral"])
    K.mono(d, tf, "c2-cap", gx(c["cap_at_min"]) + 10, gy(c["cap"]) - 26, 420, 22,
           "第 %d 分钟（%d h %02d min）起封顶 %d 元"
           % (c["cap_at_min"], c["cap_at_min"] // 60, c["cap_at_min"] % 60, c["cap"]),
           13, P["coral"])
    K.tlab(d, tf, "c2-p1", gx(c["cap_at_min"]) + 20, gy(c["cap"]) + 120,
           gx(1440) - gx(c["cap_at_min"]) - 40, 26,
           "封顶平台：第 %d 分钟一直到 24 小时，都只付 %d 元" % (c["cap_at_min"], c["cap"]),
           16, "#10181C", align="CENTER")
    K.tlab(d, tf, "c2-p2", gx(c["cap_at_min"]) + 20, gy(c["cap"]) + 152,
           gx(1440) - gx(c["cap_at_min"]) - 40, 24,
           "多停 %d 小时不加钱——这一段没有台阶，因为价格不再随时间变化"
           % int((1440 - c["cap_at_min"]) / 60), 14, "#1F2A2E", align="CENTER")
    fx = gx(c["free_min"])
    d.line(fx, BY, fx, gy(c["first_price"]), 2, P["mist"])
    ly = gy(c["first_price"]) - 6
    while ly > PY + 52:
        d.rect(fx - 1, ly - 5, 2, 5, P["mist"])
        ly -= 8
    K.mono(d, tf, "c2-free", PX + 6, PY + 26, 250, 22,
           "第 %d 分钟：0 → %d 元" % (c["free_min"] + 1, c["first_price"]), 13, P["t0"])
    for hr in (0, 1, 2, 3, 4, 6, 8, 12, 16, 20, 24):
        K.mono(d, tf, "c2-x%d" % hr, gx(hr * 60) - 22, BY + 6, 44, 20, "%d h" % hr,
               12, P["t2"], align="CENTER")
    fy = BY + 36
    K.tlab(d, tf, "c2-f1", 62, fy, 1076, 22,
           "台阶＝同一价格覆盖的时长；竖线是跳变点，共 %d 个（%s）。"
           % (len(jumps), "、".join("%d min" % m for m, _b in jumps[:6]) + " …"),
           13, P["t2"])
    K.tlab(d, tf, "c2-f2", 62, fy + 26, 1076, 22,
           "最后一段（%d–%d min）都是 %d 元：封顶以后每多停 1 分钟不加钱。"
           % (c["cap_at_min"], XMAX, c["cap"]), 13, P["t2"])
    K.tlab(d, tf, "c2-f3", 62, fy + 52, 1076, 22,
           "青色＝按小时累加的部分，金色＝封顶平台。", 13, P["t2"])
    assert fy + 74 <= 326 + 640 - 22, fy

    # ---------- ③ 三个常见时长 ----------
    x3, cy3, w3 = K.card(d, tf, "c3", 40, 978, 1120, 234,
                         "③ 三个常见时长：应付多少",
                         sub="直接从阶梯上读，不用口算")
    picks = [(45, "接孩子／买菜"), (120, "逛商场"), (480, "上班一整天")]
    for i, (m, lab) in enumerate(picks):
        r = tbl[m]
        bx = x3 + i * 368
        K.panel(d, bx, cy3 - 6, 340, 100, P["card2"], radius=12,
                border="1 SOLID " + P["border"])
        K.tlab(d, tf, "c3-l%d" % i, bx + 16, cy3 + 2, 300, 22, lab, 13, P["t2"])
        K.mono(d, tf, "c3-v%d" % i, bx + 16, cy3 + 24, 120, 34, "%g" % r["cost"], 28,
               P["t0"])
        K.tlab(d, tf, "c3-u%d" % i, bx + 16 + (46 if r["cost"] >= 10 else 26), cy3 + 34,
               120, 24, "元", 15, P["t2"])
        K.tlab(d, tf, "c3-w%d" % i, bx + 16, cy3 + 62, 308, 22,
               "%s｜折 %.1f 元/小时" % (r["why"], r["cost"] / (m / 60.0)), 12, P["t2"])
    K.tlab(d, tf, "c3-n", x3, cy3 + 104, w3, 22,
           "同样按小时算：45 分钟折 %.1f 元/h，2 小时 %.1f 元/h，8 小时 %.1f 元/h——"
           "越接近封顶越划算。" % (tbl[45]["cost"] / 0.75, tbl[120]["cost"] / 2,
                             tbl[480]["cost"] / 8), 13, P["t1"])
    assert cy3 + 126 <= 978 + 234 - 22, cy3

    # ---------- ④ 临界点与行动 ----------
    x4, cy4, w4 = K.card(d, tf, "c4", 40, 1224, 1120, 234,
                         "④ 临界点：哪一分钟最不值",
                         sub="跳变点前 1 分钟，是同一价格里最划算的位置")
    rows = [("跳变点", "每 %d 分钟一跳：%s" % (c["step_min"],
             "、".join("%d min→%g 元" % (m, b) for m, b in jumps[:5]))),
            ("最不值的一分钟", "%d min（刚跳到 %g 元）；最划算的是 %d min（同样 %g 元）"
             % (jumps[1][0], jumps[1][1], jumps[1][0] + c["step_min"] - 1,
                jumps[1][1])),
            ("封顶之后", "%d min 到 %d min 都付 %d 元——多停 %d 小时不加钱"
             % (c["cap_at_min"], XMAX, c["cap"], int((XMAX - c["cap_at_min"]) / 60))),
            ("行动", "预计超过 %d 分钟就不用再盯表：当天价格不再变；跨到第 2 天重新计，"
             "25 h ＝ %d ＋ %d ＝ %g 元"
             % (c["cap_at_min"], c["cap"], c["first_price"], tbl[1500]["cost"]))]
    ry = cy4
    for i, (lab, val) in enumerate(rows):
        col = P["gold"] if i == len(rows) - 1 else P["t0"]
        K.tlab(d, tf, "c4-l%d" % i, x4, ry, 150, 22, lab, 13, P["t2"])
        K.tlab(d, tf, "c4-v%d" % i, x4 + 158, ry, w4 - 158, 22, val, 14, col)
        ry += 30
    assert ry <= 1224 + 234 - 22, ry

    # ---------- ⑤ 口径与限制 ----------
    nb = K.note_band(d, tf, "c5", 40, 1470, 1120, [
        "口径：免费 %d 分钟；超过后首小时一口价 %d 元；之后每 %d 分钟 %d 元、"
        "不足一段按一段计；24 h 内封顶 %d 元。"
        % (c["free_min"], c["first_price"], c["step_min"], c["step_price"], c["cap"]),
        "费率与时长为演示值（%s）；真实停车场以入口公示与计费系统为准。" % c["note"],
    ], size=14)
    assert nb + 8 + 26 <= H - 12, nb
    K.credit(d, tf, "credit", 40, nb + 8, 1120, [
        "数据：tmp/%s/B06/research/demo.json（b06data.py case07，seed=%s）｜台阶 %d 段、"
        "跳变 %d 个｜横轴 %g min ＝ %g px，纵轴 %g 元 ＝ %g px"
        % (RID, K.data()["seed"], len(steps), len(jumps), XMAX, PW, YMAX, PH),
    ], size=12)
    info = {"case": "07", "kind": "everyday-info-reinvented", "canvas": [W, H],
            "steps": len(steps), "jumps": jumps,
            "cap_reached_at_min": c["cap_at_min"],
            "durations": dict((tbl[m]["label"], tbl[m]["cost"]) for m, _ in picks),
            "per_hour": {"45min": round(tbl[45]["cost"] / 0.75, 2),
                         "2h": round(tbl[120]["cost"] / 2, 2),
                         "8h": round(tbl[480]["cost"] / 8, 2)}}
    return d, tf, info
