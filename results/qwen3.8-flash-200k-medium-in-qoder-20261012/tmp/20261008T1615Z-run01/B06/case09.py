"""件-09「『0 蔗糖』那瓶，方糖堆到第 6 块」1080×1350（饮料背标 / 货架卡）。

原始口径：背标营养成分表只写"每 100 mL 糖 X g"，另有"0 蔗糖""无糖"两种字样。
换算：按整瓶净含量折算成克，再除以 4.5 g／块画成方糖堆，叠上 25 g 与 50 g 两条建议上限。
行动：给出"喝到多少毫升就过 25 g"，并拆穿"0 蔗糖"与"无糖"的口径差。

含量、瓶型、上限均为 self_defined_demo／常见公开建议口径（note 字段要求落地前核对）；
没有做真实用户验证，不声称做过。
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

W, H = 1080, 1350
CUBE, GAP, PER = 34.0, 4.0, 3          # 每 3 块一行，一行代表 3×4.5 g
BASE_Y = 620.0                         # 方糖堆基线（0 g）


def build():
    d, tf = K.doc(W, H, ground="dark")
    P = d.P
    c = K.data()["cases"]["case09"]
    drinks = c["drinks"]
    cg, best, soft = c["cube_g"], c["daily_best"], c["daily_soft"]
    ppg = (CUBE + GAP) / (PER * cg)    # px / g
    by = BASE_Y
    assert by - soft * ppg >= 312 + 86 + 20, by - soft * ppg   # 50 g 线不压住 ② 标题
    tallest = max(x["cubes"] for x in drinks)
    ttop = by - (int(tallest) // PER) * (CUBE + GAP) - (tallest - int(tallest)) * CUBE
    assert ttop > by - soft * ppg, (tallest, ttop)

    def dashes(x0, x1, y, color, seg=10, gap=8, thick=2):
        cx = x0
        while cx < x1:
            d.rect(cx, y, min(seg, x1 - cx), thick, color)
            cx += seg + gap

    def stack(x, n, edge):
        """整块一堆，余量按同比例画矮块（最低 6 px）；返回实际堆顶 y。"""
        full = int(n)
        frac = n - full
        part = frac >= 0.2
        top = by
        for i in range(full + (1 if part else 0)):
            r, col = divmod(i, PER)
            bx = x + col * (CUBE + GAP)
            hh = CUBE if (i < full or part is False) else frac * CUBE
            t = by - r * (CUBE + GAP) - hh
            d.rect(bx, t, CUBE, hh, P["card2"], radius=4)
            K.outline_rect(d, bx, t, CUBE, hh, edge, radius=4, thick=2)
            d.line(bx + 3, t + hh - 4, bx + CUBE - 4, t + 3, 1.5, edge)
            top = min(top, t)
        return top

    # ---------- 页眉 ----------
    d.rect(0, 0, W, 92, K.BASE)
    d.rect(0, 90, W, 2, P["line"])
    s3 = [x for x in drinks if x["id"] == "S3"][0]
    K.tlab(d, tf, "h-t", 40, 14, 700, 40, "「0 蔗糖」那瓶，方糖堆到第 %d 块"
           % int(s3["cubes"]), 30, P["t0"])
    K.tlab(d, tf, "h-s", 40, 56, 660, 24,
           "背标只写每 100 mL，没有人按整瓶算", 15, P["t2"])
    K.chip(d, tf, "h-c1", W - 236, 22, 196, 42, "演示含量", P["t1"],
           P["panel2"], border="1 SOLID " + P["border"], size=15)
    K.chip(d, tf, "h-c2", W - 452, 22, 200, 42, "上限是建议值", P["t1"],
           P["panel2"], border="1 SOLID " + P["gold"], size=15)

    # ---------- ① 背标原样 ----------
    x1, cy1, w1 = K.card(d, tf, "c1", 40, 104, 1000, 196,
                         "① 背标上写的：每 100 mL",
                         sub="五个数字都印在同一张营养成分表上，单位却不是「整瓶」")
    for i, x in enumerate(drinks):
        bx = x1 + i * 192
        lb = x["label"]
        v = "%g" % x["per100"]
        K.panel(d, bx, cy1, 180, 84, P["card2"], radius=10,
                border="1 SOLID " + (P["gold"] if lb == "0 蔗糖"
                                     else P["grass"] if lb else P["border"]))
        K.tlab(d, tf, "c1-n%d" % i, bx + 10, cy1 + 6, 160, 20, x["name"], 12, P["t0"])
        K.mono(d, tf, "c1-v%d" % i, bx + 10, cy1 + 28, 90, 30, v, 24, P["t0"])
        K.tlab(d, tf, "c1-u%d" % i, bx + 16 + int(14.6 * len(v)),
               cy1 + 38, 112, 20, "g/100 mL", 12, P["t2"])
        K.tlab(d, tf, "c1-m%d" % i, bx + 10, cy1 + 62, 160, 18,
               "净含量 %d mL｜%s" % (x["vol"], "标了 %s" % lb if lb else "无相关字样"),
               11, P["t2"])
    assert cy1 + 84 <= 104 + 196 - 22, cy1

    # ---------- ② 整瓶方糖堆 ----------
    x2, cy2, w2 = K.card(d, tf, "c2", 40, 312, 1000, 404,
                         "② 换算成整瓶：方糖堆",
                         sub="1 块＝%g g，每行 3 块；虚线是常见公开建议口径，不是本国现行标准" % cg)
    K.tlab(d, tf, "c2-hint", x2, cy2 + 4, w2, 22,
           "读数法：堆顶越过虚线＝喝完这一瓶就超过该建议量", 14, P["t1"])
    TAG_W = 140                       # 左侧只放两条上限的短标签，避免压住堆
    plot_x = x2 + TAG_W
    plot_w = w2 - TAG_W
    d.line(plot_x - 8, by, x2 + w2, by, 2, P["axis"])
    dashes(plot_x - 8, x2 + w2, by - best * ppg - 1, P["gold"])
    dashes(plot_x - 8, x2 + w2, by - soft * ppg - 1, P["coral"])
    K.mono(d, tf, "c2-b0", x2, by - 8, 128, 22, "0 g", 13, P["t2"])
    K.mono(d, tf, "c2-b1", x2, by - best * ppg - 15, 128, 22,
           "%g g 建议" % best, 13, P["gold"])
    K.mono(d, tf, "c2-b2", x2, by - soft * ppg - 15, 128, 22,
           "%g g 上限" % soft, 13, P["coral"])
    colw = plot_w / len(drinks)
    assert colw >= CUBE * PER + GAP * (PER - 1) + 40, colw
    for i, x in enumerate(drinks):
        bx = plot_x + i * colw
        over = x["over_best"]
        edge = P["coral"] if over else P["grass"]
        top = stack(bx, x["cubes"], edge)
        sx = bx + (PER * (CUBE + GAP) - GAP) / 2
        K.tlab(d, tf, "c2-n%d" % i, bx - 26, by + 10, colw - 8, 20, x["name"], 12,
               P["t0"], align="CENTER")
        K.mono(d, tf, "c2-g%d" % i, bx - 26, by + 30, colw - 8, 22,
               "%g g｜%d 块" % (x["total_g"], x["cubes_int"]), 13,
               P["coral"] if over else P["grass"], align="CENTER")
        K.tlab(d, tf, "c2-p%d" % i, bx - 26, by + 52, colw - 8, 20,
               "占建议 %d%%" % x["pct_best"], 11, P["t2"], align="CENTER")
        if x["label"]:
            col = P["gold"] if x["label"] == "0 蔗糖" else P["grass"]
            cy = top - 36
            assert all(abs(cy + 13 - (by - g * ppg)) > 17 for g in (best, soft)), \
                (x["id"], cy)          # 标签不骑在两条虚线上
            K.chip(d, tf, "c2-c%d" % i, sx - 48, cy, 96, 26, x["label"], col,
                   P["panel2"], border="1 SOLID " + col, size=13)
    assert by + 74 <= 312 + 404 - 22, by + 74

    # ---------- ③ 喝到多少毫升过线 ----------
    x3, cy3, w3 = K.card(d, tf, "c3", 40, 728, 1000, 236,
                         "③ 喝到多少毫升就吃掉 %g g" % best,
                         sub="条形＝这一口占整瓶的比例；剩下的每一口都还在算")
    ry = cy3
    for i, x in enumerate([k for k in drinks if k["ml_to_best"]]):
        frac = x["ml_to_best"] / x["vol"]
        K.tlab(d, tf, "c3-n%d" % i, x3, ry, 250, 22, x["name"], 13, P["t0"])
        K.hbar(d, tf, "c3-b%d" % i, x3 + 260, ry + 2, 420, 18, frac,
               P["coral"] if frac > 0.8 else P["teal"], bg=P["panel2"])
        K.mono(d, tf, "c3-v%d" % i, x3 + 692, ry, 264, 22,
               "%d / %d mL＝%d%%｜半瓶 %g g" % (x["ml_to_best"], x["vol"],
                                             round(frac * 100), x["half_bottle_g"]),
               13, P["t1"])
        ry += 30
    assert ry <= 728 + 236 - 22, ry

    # ---------- ④ 0 蔗糖不等于无糖 ----------
    x4, cy4, w4 = K.card(d, tf, "c4", 40, 976, 1000, 190,
                         "④ 两种字样的差别",
                         sub=c["trap_note"])
    s5 = [x for x in drinks if x["id"] == "S5"][0]
    for i, (x, lab) in enumerate([(s3, "写着「0 蔗糖」"), (s5, "写着「无糖」")]):
        bx = x4 + i * 480
        col = P["gold"] if i == 0 else P["grass"]
        K.panel(d, bx, cy4, 460, 76, P["card2"], radius=10, border="1 SOLID " + col)
        K.tlab(d, tf, "c4-a%d" % i, bx + 14, cy4 + 8, 220, 22, lab, 14, P["t0"])
        K.mono(d, tf, "c4-b%d" % i, bx + 14, cy4 + 32, 430, 20,
               "背标每 100 mL 写 %g g" % x["per100"], 12, P["t2"])
        K.mono(d, tf, "c4-c%d" % i, bx + 14, cy4 + 52, 430, 22,
               "%d mL → %g g ＝ %.1f 块｜占建议 %d%%"
               % (x["vol"], x["total_g"], x["cubes"], x["pct_best"]), 13, col)
    assert cy4 + 76 <= 976 + 190 - 22, cy4

    # ---------- ⑤ 口径与限制 ----------
    nb = K.note_band(d, tf, "c5", 40, 1178, 1000, [
        "口径：整瓶克数＝每 100 mL 克数 × 净含量 ÷ 100；方糖按 %g g／块折算。" % cg,
        "余量不足 0.2 块不画，其余按同比例高度画；改成按整块取整会改写数字（%s）。"
        % "、".join("%s %.1f→%d 块" % (x["id"], x["cubes"], x["cubes_int"])
                    for x in drinks if x["cubes"] != round(x["cubes"])),
        c["note"] + "；没有做真实用户验证，不声称做过。",
    ], size=14)
    K.credit(d, tf, "c5-cr", 40, nb + 10, 1000, [
        "数据：tmp/%s/B06/research/demo.json（case09，seed=%s）｜5 款｜1 行 3 块＝%g g｜"
        "基线 y＝%d" % (RID, K.data()["seed"], PER * cg, by),
    ], size=13)
    assert nb + 36 <= H - 16, nb
    info = {"case": "09", "kind": "everyday-info-reinvented", "canvas": [W, H],
            "drinks": len(drinks), "cube_g": cg, "best_g": best, "soft_g": soft,
            "cubes": dict((x["id"], x["cubes"]) for x in drinks),
            "over_best": [x["id"] for x in drinks if x["over_best"]],
            "trap": c["trap"], "px_per_g": round(ppg, 4), "baseline_y": by}
    return d, tf, info


if __name__ == "__main__":
    d, tf, info = build()
    print("texts", tf.n, "problems", tf.problems)
    print(info)
