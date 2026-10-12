"""件-05「体检报告的箭头不够用」1440×1080（报告单阅读页）。

原始口径：每项一个 ↑/↓ 箭头 + 参考区间，12 项里 9 项有箭头，符号完全相同。
换算：dev = |结果 − 区间中点| / 半宽（我自定义的归一化偏离度），
      与"超出最近边界的百分比"并列，两个口径会把不同项目推到第一位。
行动：按 dev 给复查节奏（2 周内／6 周内／3 个月内／随年度）与分科挂号清单。

12 项数值与区间均为演示值（demo.json case05），不是任何实验室参考值，不作诊断。
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

W, H = 1440, 1080
LX, LW = 40, 920
RX, RW = 984, 416


def pace(s):
    return ("2 周内" if s.startswith("2") else "6 周内" if s.startswith("6")
            else "3 个月" if s.startswith("3") else "随年度")


def num(v):
    return ("%g" % v)


def build():
    d, tf = K.doc(W, H, ground="dark")
    P = d.P
    c = K.data()["cases"]["case05"]
    items = sorted(c["items"], key=lambda it: -it["abs_dev"])
    mx_dev = max(it["abs_dev"] for it in items)
    by_rel = sorted(c["items"], key=lambda it: -abs(it["rel_out_pct"]))

    # ---------- 页眉 ----------
    d.rect(0, 0, W, 92, K.BASE)
    d.rect(0, 90, W, 2, P["line"])
    K.tlab(d, tf, "h-t", LX, 14, 700, 40, "报告单的箭头不够用", 32, P["t0"])
    K.tlab(d, tf, "h-s", LX, 56, 760, 24,
           "12 项里 %d 项带箭头，箭头不分轻重；这里换成可排序的偏离度" % c["n_abnormal"],
           15, P["t2"])
    K.chip(d, tf, "h-c1", W - 400, 22, 120, 42, "演示数据", P["t2"], P["card2"],
           border="1 SOLID " + P["border"], size=15)
    K.chip(d, tf, "h-c2", W - 270, 22, 230, 42, "不作诊断，只帮排序", P["t1"],
           P["panel2"], border="1 SOLID " + P["border"], size=15)

    # ---------- ① 报告原样 ----------
    x1, cy1, w1 = K.card(d, tf, "c1", LX, 104, LW, 176, "① 报告单原样：符号只有两种")
    row = items[:4]
    for i, it in enumerate(row):
        bx = x1 + i * 218
        K.panel(d, bx, cy1 - 4, 206, 40, P["card2"], radius=8,
                border="1 SOLID " + P["border"])
        K.tlab(d, tf, "c1-a%d" % i, bx + 10, cy1 + 2, 120, 24, it["k"], 13, P["t1"])
        K.mono(d, tf, "c1-b%d" % i, bx + 128, cy1 + 2, 70, 24,
               "%s %s" % (num(it["v"]), "↑" if it["flag"] == "high" else "↓"), 13,
               P["coral"], align="END")
    K.tlab(d, tf, "c1-n1", x1, cy1 + 44, w1, 22,
           "↑＝高于参考上限，↓＝低于参考下限：%d 个箭头长得一模一样，"
           "看不出谁偏得最远、谁只是刚过线、谁该先复查。" % c["n_abnormal"],
           13, P["t2"])
    assert cy1 + 66 <= 104 + 176 - 22, cy1

    # ---------- ② 偏离度发散条 ----------
    x2, cy2, w2 = K.card(d, tf, "c2", LX, 292, LW, 656,
                         "② 换算：把每一项放到同一把尺上",
                         sub="dev＝|结果−区间中点|÷半宽；左＝低于区间，右＝高于区间")
    cols = [("项目", 62, 168, "START"), ("结果", 232, 96, "END"),
            ("参考区间", 330, 104, "END"), ("dev", 726, 52, "END"),
            ("超界", 782, 62, "END"), ("复查", 848, 90, "END")]
    for lab, cx, cw, _al in cols:
        if lab in ("dev", "超界", "复查"):
            K.tlab(d, tf, "c2-h" + lab, cx, cy2 - 2, cw, 20, lab, 12, P["t2"],
                   align="END")
        else:
            K.tlab(d, tf, "c2-h" + lab, cx, cy2 - 2, cw, 20, lab, 12, P["t2"])
    K.tlab(d, tf, "c2-hb", 440, cy2 - 2, 280, 20, "← 低于区间　　0　　高于区间 →",
           12, P["t2"], align="CENTER")
    BXR, BWR, ZF = 440.0, 280.0, 0.5
    ry = cy2 + 22
    for i, it in enumerate(items):
        if i % 2 == 0:
            d.rect(62, ry - 3, 876, 32, P["card2"], radius=6)
        K.tlab(d, tf, "c2-n%d" % i, 62, ry, 168, 24, it["k"], 14,
               P["t0"] if it["flag"] != "in" else P["t2"])
        K.mono(d, tf, "c2-v%d" % i, 232, ry, 96, 24, num(it["v"]), 14,
               P["t0"] if it["flag"] != "in" else P["t2"], align="END")
        K.mono(d, tf, "c2-r%d" % i, 330, ry, 104, 24,
               ("≤ %s" % num(it["high"])) if it["one_sided"]
               else "%s–%s" % (num(it["low"]), num(it["high"])), 13, P["t2"],
               align="END")
        col = (P["rust"] if it["abs_dev"] >= 1.5 else P["gold"] if it["abs_dev"] >= 1.0
               else P["teal"])
        K.diverging_bar(d, tf, "c2-b%d" % i, BXR, ry + 2, BWR, ZF,
                        it["dev"] / (mx_dev + 0.2) * 0.5, 20, col, col, radius=4)
        K.mono(d, tf, "c2-d%d" % i, 726, ry, 52, 24, "%+.2f" % it["dev"], 14, col,
               align="END")
        K.mono(d, tf, "c2-o%d" % i, 782, ry, 62, 24,
               "%+.1f%%" % it["rel_out_pct"] if it["rel_out_pct"] else "—", 13,
               P["t1"] if it["flag"] != "in" else P["t2"], align="END")
        K.tlab(d, tf, "c2-p%d" % i, 848, ry, 90, 24,
               pace(it["recheck"]) if it["flag"] != "in" else "—", 13,
               P["t1"] if it["flag"] != "in" else P["t2"], align="END")
        ry += 36
    ry += 4
    K.tlab(d, tf, "c2-f1", 62, ry, 876, 22,
           "条长按 dev 等比；%s 的 dev %.2f 最长，%s 只有 %.2f。"
           % (items[0]["k"], items[0]["abs_dev"], items[-1]["k"], items[-1]["abs_dev"]),
           13, P["t2"])
    ry += 24
    _d = [x for x in items if x["k"] == "维生素 D"][0]
    K.tlab(d, tf, "c2-f2", 62, ry, 876, 22,
           "「超界」＝离最近边界超出的百分比（低于下界记负）：%s 低于下界 %.1f%%，"
           "幅度最大，dev 却只排第 %d。" % (_d["k"], abs(_d["rel_out_pct"]),
                              1 + [x["k"] for x in items].index(_d["k"])),
           13, P["t2"])
    ry += 24
    K.tlab(d, tf, "c2-f3", 62, ry, 876, 22,
           "颜色按 dev 分级：≥1.5 珊瑚／1.0–1.5 金／<1.0 青——只表示排序靠前，"
           "不代表病情轻重。", 13, P["t2"])
    assert ry + 22 <= 292 + 656 - 22, ry

    # ---------- ③ 两个口径谁说了算 ----------
    x3, cy3, w3 = K.card(d, tf, "c3", RX, 104, RW, 386, "③ 两个口径，两种第一",
                         sub="同一份数据，排序会换")
    K.tlab(d, tf, "c3-a", x3, cy3, w3, 24, "按 dev（本卡采用）", 15, P["t0"])
    ry = cy3 + 30
    for i, it in enumerate(items[:3]):
        K.mono(d, tf, "c3-d%d" % i, x3, ry, 58, 22, "%.2f" % it["abs_dev"], 14,
               P["gold"], align="END")
        K.tlab(d, tf, "c3-e%d" % i, x3 + 66, ry, w3 - 66, 22,
               "%s（%s %s）" % (it["k"], num(it["v"]), it["u"]), 13, P["t1"])
        ry += 26
    ry += 10
    K.tlab(d, tf, "c3-b", x3, ry, w3, 24, "按超界幅度（取绝对值）", 15, P["t0"])
    ry += 30
    for i, it in enumerate(by_rel[:3]):
        K.mono(d, tf, "c3-f%d" % i, x3, ry, 58, 22,
               "%+.1f%%" % it["rel_out_pct"], 14, P["coral"], align="END")
        K.tlab(d, tf, "c3-g%d" % i, x3 + 66, ry, w3 - 66, 22,
               "%s（%s %s）" % (it["k"], num(it["v"]), it["u"]), 13, P["t1"])
        ry += 26
    ry += 8
    it_d = [x for x in c["items"] if x["k"] == "维生素 D"][0]
    it_hb = [x for x in c["items"] if x["k"] == "血红蛋白"][0]
    rank_of_d = 1 + [x["k"] for x in items].index("维生素 D")
    rank_of_hb = 1 + [x["k"] for x in items].index("血红蛋白")
    K.tlab(d, tf, "c3-n1", x3, ry, w3, 22,
           "超界幅度不看区间宽窄：血红蛋白只超下界 %.1f%%（dev 第 %d），"
           % (abs(it_hb["rel_out_pct"]), rank_of_hb), 12, P["t2"])
    K.tlab(d, tf, "c3-n2", x3, ry + 22, w3, 22,
           "维生素 D 超下界 %.1f%% 却只排第 %d；dev 把区间宽度算进去。"
           % (abs(it_d["rel_out_pct"]), rank_of_d), 12, P["t2"])
    assert ry + 44 <= 104 + 386 - 22, ry

    # ---------- ④ 行动：分科与节奏 ----------
    x4, cy4, w4 = K.card(d, tf, "c4", RX, 502, RW, 446, "④ 行动：先看哪几科",
                         sub="按本科最长 dev 排序")
    dept_rows = []
    for dp, ks in c["depts"].items():
        sub = [it for it in items if it["k"] in ks]
        worst = max(sub, key=lambda it: it["abs_dev"])
        dept_rows.append((dp, worst, ks))
    dept_rows.sort(key=lambda r: -r[1]["abs_dev"])
    ry = cy4
    for i, (dp, worst, ks) in enumerate(dept_rows):
        col = (P["rust"] if worst["abs_dev"] >= 1.5 else P["gold"]
               if worst["abs_dev"] >= 1.0 else P["teal"])
        d.rect(x4, ry + 2, 5, 40, col, radius=2)
        K.tlab(d, tf, "c4-a%d" % i, x4 + 16, ry, 150, 24, dp, 15, P["t0"])
        K.tlab(d, tf, "c4-b%d" % i, x4 + 16, ry + 22, w4 - 16, 20,
               "、".join(ks), 12, P["t2"])
        K.mono(d, tf, "c4-c%d" % i, x4 + w4 - 96, ry, 96, 22, pace(worst["recheck"]),
               13, col, align="END")
        ry += 46
    ry += 4
    K.panel(d, x4, ry, w4, 88, P["card2"], radius=12,
            border="1 SOLID " + P["border"])
    _fast = [it["k"] for it in items if it["need_fast"]]
    K.tlab(d, tf, "c4-s1", x4 + 14, ry + 10, w4 - 28, 34, "空腹项 %d 个：%s"
           % (len(_fast), "、".join(_fast)), 12, P["t1"], lines=2, valign="TOP")
    K.tlab(d, tf, "c4-s2", x4 + 14, ry + 48, w4 - 28, 34,
           "复查时这 %d 项要重新空腹采血，别只挂号不安排时间。" % len(_fast), 12, P["t2"],
           lines=2, valign="TOP")
    assert ry + 88 <= 502 + 446 - 22, ry

    # ---------- ⑤ 口径与限制 ----------
    nb = K.note_band(d, tf, "c5", LX, 954, LW + 24 + RW, [
        "口径：dev＝|结果−区间中点|÷半宽（区间不对称时按实际边界取符号），"
        "是我自己定的归一化偏离度；它只用于排序，不是诊断阈值，也不判断病因。",
        "12 项数值、参考区间、科室归属与复查节奏全为演示值；真实报告请以医生复核为准。"
        "本卡不预测疾病，也不替代任何一项复检。",
    ], size=14)
    assert nb + 8 + 26 <= H - 12, nb
    K.credit(d, tf, "credit", LX, nb + 8, LW + 24 + RW, [
        "数据：tmp/%s/B06/research/demo.json（b06data.py，seed=%s）｜140 px ＝ %g dev"
        "｜%d 项异常（%d 高 %d 低），%d 项区间只有上界。"
        % (RID, K.data()["seed"], mx_dev + 0.2, c["n_abnormal"], c["n_high"],
           c["n_low"], c["n_one_sided"]),
    ], size=12)
    info = {"case": "05", "kind": "everyday-info-reinvented", "canvas": [W, H],
            "order_by_dev": [it["k"] for it in items],
            "order_by_rel": [it["k"] for it in by_rel[:3]],
            "n_abnormal": c["n_abnormal"], "n_one_sided": c["n_one_sided"],
            "paces": dict((it["k"], pace(it["recheck"])) for it in items
                          if it["flag"] != "in"),
            "dept_order": [r[0] for r in dept_rows]}
    return d, tf, info
