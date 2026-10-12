"""件-04「外卖价格解剖」1080×1440（结算页的替代物）。

原始口径：结算页两行——「¥23.22」「已优惠 ¥8」。
换算：把实付拆成 菜品原价 → 满减 → 优惠券 → 包装 → 配送 五步瀑布，
      再换成 每 100 g 单价 与 费用占实付比例。
行动：算清"再加 15 元凑下一档满减"到底省了多少（净多花 9 元）。

两单与全部数字为 self_defined_demo（demo.json case04）。
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

W, H = 1080, 1440
MX = 40
CW = W - 2 * MX


def money(v):
    return K.fmt(v, 2)


def build():
    d, tf = K.doc(W, H, ground="dark")
    P = d.P
    c = K.data()["cases"]["case04"]
    o1, o2 = c["orders"][0], c["orders"][1]

    # ---------- 页眉 ----------
    d.rect(0, 0, W, 92, K.BASE)
    d.rect(0, 90, W, 2, P["line"])
    K.tlab(d, tf, "h-t", MX, 14, 620, 40, "外卖价格解剖", 32, P["t0"])
    K.tlab(d, tf, "h-s", MX, 56, 700, 24,
           "结算页只写两行，这里把它摊成五步", 15, P["t2"])
    K.chip(d, tf, "h-c1", W - 400, 22, 120, 42, "演示数据", P["t2"], P["card2"],
           border="1 SOLID " + P["border"], size=15)
    K.chip(d, tf, "h-c2", W - 250, 22, 210, 42, o1["shop"], P["t1"], P["panel2"],
           border="1 SOLID " + P["border"], size=15)

    # ---------- ① 结算页原样 ----------
    x1, cy1, w1 = K.card(d, tf, "c1", MX, 104, CW, 184, "① 结算页只给你两行")
    K.mono(d, tf, "c1-big", x1, cy1 - 8, 300, 62, "¥" + money(o1["pay"]), 50,
           P["amber"])
    K.chip(d, tf, "c1-off", x1 + 220, cy1 + 6, 210, 40,
           "已优惠 ¥" + money(o1["discount"] + o1["coupon"]), P["grass"], P["card2"],
           border="1 SOLID " + P["border"], size=16)
    K.tlab(d, tf, "c1-n1", x1 + 560, cy1 - 6, 380, 26, "这两行之外看不到的：", 15,
           P["t1"])
    K.tlab(d, tf, "c1-n2", x1 + 560, cy1 + 20, 380, 26,
           "满减怎么算的、优惠券算在哪、包装费", 15, P["t2"])
    K.tlab(d, tf, "c1-n3", x1 + 560, cy1 + 46, 380, 26,
           "配送费里的里程加价、每 100 g 多少钱", 15, P["t2"])
    assert cy1 + 72 <= 104 + 184 - 22, cy1
    y = 296

    # ---------- ② 五步瀑布 ----------
    x2, cy2, w2 = K.card(d, tf, "c2", MX, y, CW, 440, "② 换算：实付是五步叠出来的",
                         sub="左＝步骤，中＝浮动条（同一比例尺），右＝该步金额与累计")
    steps = [("菜品原价", o1["subtotal"], P["teal"],
              " + ".join("%s %s" % (it["n"], money(it["price"] * it["qty"]))
                         for it in o1["items"])),
             ("满减", -o1["discount"], P["grass"], o1["discount_rule"]),
             ("商家优惠券", -o1["coupon"], P["grass"], "店内可领，1 张"),
             ("包装费", o1["package"], P["gold"],
              " + ".join("%s×%.1f" % (it["n"], it["pkg"]) for it in o1["items"])),
             ("配送费", o1["delivery"], P["gold"],
              "起步 %s + 超 %s km×%s" % (money(o1["delivery_base"]),
                                        K.fmt(o1["dist_km"] - o1["free_km"], 1),
                                        money(o1["per_km"])))]
    bx, bw = x2 + 190, 470
    scale = bw / float(o1["subtotal"])
    cy = cy2 + 4
    prev = 0.0
    for i, (name, amt, col, detail) in enumerate(steps):
        cur = prev + amt
        a0, a1 = min(prev, cur), max(prev, cur)
        K.tlab(d, tf, "c2-n%d" % i, x2, cy, 180, 24, name, 16, P["t0"])
        K.tlab(d, tf, "c2-d%d" % i, x2, cy + 26, 180, 22, detail, 12, P["t2"])
        d.rect(bx, cy + 4, bw, 30, P["grid"], radius=4)
        d.rect(bx + a0 * scale, cy + 4, max(3.0, (a1 - a0) * scale), 30, col,
               radius=4)
        if i:
            d.line(bx + prev * scale, cy - 6, bx + prev * scale, cy + 4, 1.5,
                   P["mist"])
        K.mono(d, tf, "c2-a%d" % i, bx + bw + 12, cy + 4, 96, 30,
               ("+" if amt >= 0 else "-") + money(abs(amt)), 16, col, align="END")
        K.mono(d, tf, "c2-c%d" % i, bx + bw + 118, cy + 4, 148, 30,
               "累计 " + money(cur), 15, P["t1"], align="END")
        prev = cur
        cy += 56
    # 实付行
    d.rect(bx, cy + 4, prev * scale, 30, P["violet"], radius=4)
    K.tlab(d, tf, "c2-fn", x2, cy, 180, 24, "实付", 17, P["t0"])
    K.tlab(d, tf, "c2-fd", x2, cy + 26, 180, 22, "= 菜品 - 优惠 + 费用", 12, P["t2"])
    K.mono(d, tf, "c2-fa", bx + bw + 12, cy + 4, 96, 30, money(prev), 17, P["violet"],
           align="END")
    K.mono(d, tf, "c2-fc", bx + bw + 118, cy + 4, 148, 30,
           "共 %.0f g" % o1["grams"], 14, P["t2"], align="END")
    cy += 40
    assert cy <= y + 440 - 22, cy
    y = 748

    # ---------- ③ 换个分母 ----------
    x3, cy3, w3 = K.card(d, tf, "c3", MX, y, CW, 286, "③ 换个分母：谁更贵",
                         sub="条长＝实付（同一比例尺）；三截＝净菜价 / 包装 / 配送")
    bbx, bbw = x3 + 210, 470
    mx_pay = max(o1["pay"], o2["pay"])
    pscale = bbw / float(mx_pay)
    for i, o in enumerate((o1, o2)):
        ry = cy3 + i * 64
        net = o["subtotal"] - o["discount"] - o["coupon"]
        K.tlab(d, tf, "c3-n%d" % i, x3, ry, 200, 24, o["shop"], 15, P["t0"])
        K.mono(d, tf, "c3-g%d" % i, x3, ry + 26, 200, 22,
               "%s 元/100 g ｜ %.0f g" % (money(o["per_100g"]), o["grams"]), 13,
               P["t2"])
        cx = bbx
        for key, val, col in (("净菜", net, P["teal"]), ("包装", o["package"], P["gold"]),
                              ("配送", o["delivery"], P["gold"])):
            wd = max(3.0, val * pscale)
            d.rect(cx, ry + 4, wd, 34, col, radius=4)
            if key != "净菜" and wd > 46:
                K.mono(d, tf, "c3-%s%d" % (key, i), cx + 4, ry + 12, wd - 8, 20,
                       money(val), 12, "#10181C")
            cx += wd
        K.mono(d, tf, "c3-b%d" % i, bbx, ry + 44, max(120.0, cx - bbx - 12), 20,
               "净菜 %s ＋ 包装 %s ＋ 配送 %s"
               % (money(net), money(o["package"]), money(o["delivery"])), 12, P["t2"])
        d.line(cx + 8, ry + 4, cx + 8, ry + 38, 2, P["mist"])
        K.mono(d, tf, "c3-p%d" % i, cx + 18, ry + 2, 100, 26, money(o["pay"]), 17,
               P["t0"], align="END")
        K.mono(d, tf, "c3-s%d" % i, cx + 18, ry + 26, 100, 20,
               "%.1f%% 是费用" % o["fee_share_pct"], 12, P["coral"], align="END")
    ry = cy3 + 2 * 64
    K.tlab(d, tf, "c3-k", x3, ry, w3, 26,
           "同一比例尺下：实付少 %s 元的那单，包装＋配送占掉实付 %.1f%%，"
           "另一单 %.1f%%——这两单里，实付越少，费用占比越高。"
           % (money(abs(o2["pay"] - o1["pay"])), o1["fee_share_pct"],
              o2["fee_share_pct"]), 14, P["t1"], lines=2, valign="TOP")
    assert ry + 26 <= y + 286 - 22, ry
    y = 1046

    # ---------- ④ 行动 ----------
    x4, cy4, w4 = K.card(d, tf, "c4", MX, y, CW, 232, "④ 行动：这一单该不该再加 15 元")
    nxt_pay = (o1["subtotal"] + o1["add_to_next"]) - 14 - o1["coupon"] + o1["package"] \
        + o1["delivery"]
    rows = [("现在（满 30 减 8）", money(o1["pay"]), P["t0"], "净菜 %s 元"
             % money(o1["subtotal"] - o1["discount"] - o1["coupon"])),
            ("再加 %s 元（满 45 减 14）" % money(o1["add_to_next"]), money(nxt_pay),
             P["amber"], "多减 %s 元，多花 %s 元"
             % (money(o1["add_gain"]), money(o1["add_net"])))]
    ry = cy4
    for i, (lab, val, col, sub) in enumerate(rows):
        K.tlab(d, tf, "c4-a%d" % i, x4, ry, 420, 26, lab, 16, P["t0"])
        K.mono(d, tf, "c4-b%d" % i, x4 + 430, ry - 2, 150, 30, val, 20, col,
               align="END")
        K.tlab(d, tf, "c4-c%d" % i, x4 + 600, ry, 340, 26, sub, 14, P["t2"])
        ry += 34
    K.chip(d, tf, "c4-verdict", x4, ry + 6, 150, 46, "结论：不值", P["rust"],
           P["card2"], border="1 SOLID " + P["rust"], size=17)
    K.tlab(d, tf, "c4-v1", x4 + 170, ry + 6, w4 - 170, 26,
           "多花 %s 元只为了多减 %s 元，净多支出 %s 元。"
           % (money(o1["add_to_next"]), money(o1["add_gain"]), money(o1["add_net"])),
           15, P["t1"])
    K.tlab(d, tf, "c4-v2", x4 + 170, ry + 32, w4 - 170, 26,
           "除非那 %s 元的东西你本来就要吃；否则凑单省下的不是钱，是冰箱。"
           % money(o1["add_to_next"]), 15, P["t1"])
    assert ry + 6 + 46 <= y + 232 - 22, ry

    # ---------- ⑤ 口径与限制 ----------
    nb = K.note_band(d, tf, "c5", MX, 1290, CW, [
        "口径：配送费＝起步 %s 元 + 超出免费里程 %.1f km × %s 元/km；满减与优惠券可叠加，"
        "按店内标示顺序计算。" % (money(o1["delivery_base"]),
                                o1["dist_km"] - o1["free_km"], money(o1["per_km"])),
        "凑单那一档按「加购件不再产生包装费、配送费不变」计，这是最省算法；"
        "真实加购通常还要加包装费，只会更不值。",
        "本卡不含：会员红包、时段折扣、准时宝与骑手小费、发票与税。店铺、菜品、价格、"
        "里程均为虚构演示值，不是任何平台报价。",
    ], size=14)
    assert nb + 8 + 26 <= H - 12, nb
    K.credit(d, tf, "credit", MX, nb + 8, CW, [
        "数据：tmp/%s/B06/research/demo.json（b06data.py，seed=%s）｜浮动条比例尺 "
        "%.0f px = 1 元；条长严格等比，未做最小宽度修饰。"
        % (RID, K.data()["seed"], scale),
    ], size=12)
    info = {"case": "04", "kind": "everyday-info-reinvented", "canvas": [W, H],
            "order": o1["id"], "pay": o1["pay"], "steps": [s[1] for s in steps],
            "step_sum": round(prev, 2), "grams": o1["grams"],
            "per_100g": o1["per_100g"], "fee_share_pct": o1["fee_share_pct"],
            "compare": {"other_shop": o2["shop"], "other_pay": o2["pay"],
                        "other_fee_share_pct": o2["fee_share_pct"]},
            "addon": {"spend": o1["add_to_next"], "gain": o1["add_gain"],
                      "net": o1["add_net"], "next_pay": round(nxt_pay, 2),
                      "worth": o1["add_worth"]}}
    return d, tf, info
