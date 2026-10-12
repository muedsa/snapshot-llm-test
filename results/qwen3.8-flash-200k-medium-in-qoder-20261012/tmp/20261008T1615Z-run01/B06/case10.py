"""件-10「入职第一个月，我只把这 8 条对上了」1240×1754（A4 打印核对打孔卡）。

原始口径：合同条款与 HR 口头说明散在多处，新人不知道该拿什么去对。
换算：8 项各拆成「规则／合同写的／该是多少／怎么办」四栏，判定只有三种状态；
加班小时数单独按 0–80 h 刻度画出来，和 36 h 上限放在同一根轴上。
行动：每项给一句可执行动作，另给第一个月 6 个时间点。

条款口径是 common_rule_needs_check（本图不声明法律意见），合同与排班内容是
self_defined_demo；没有做真实用户验证，不声称做过。
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

W, H = 1240, 1754
ROW_H, ROW_GAP = 80, 8
OT_MAX = 80.0                          # 加班刻度轴上限（h），演示取整


def build():
    d, tf = K.doc(W, H, ground="dark")
    P = d.P
    c = K.data()["cases"]["case10"]
    checks = c["checks"]
    n_bad = sum(1 for x in checks if x["verdict"] == "不符")
    n_gap = sum(1 for x in checks if x["verdict"] == "缺项")
    n_ok = len(checks) - n_bad - n_gap
    assert (n_bad, n_gap, n_ok) == (c["n_bad"], c["n_gap"], c["n_ok"])
    vc = {"不符": P["coral"], "缺项": P["gold"], "通过": P["grass"]}
    ot, cap = c["overtime_hours"], c["overtime_cap"]
    assert ot - cap == c["overtime_over_h"] and ot > cap

    # ---------- 页眉 ----------
    d.rect(0, 0, W, 140, K.BASE)
    d.rect(0, 138, W, 2, P["line"])
    K.tlab(d, tf, "h-t", 48, 18, 860, 42, "入职第一个月，我只把这 %d 条对上了"
           % len(checks), 31, P["t0"])
    K.tlab(d, tf, "h-s", 48, 64, 820, 24, "左边打孔：对一项勾一项；勾不满的就是要走流程的",
           15, P["t2"])
    K.tlab(d, tf, "h-m", 48, 96, 820, 22, "示例：汀州市（虚构）某岗位，月薪 %s 元、合同 %d 个月"
           % ("{:,}".format(c["monthly"]), c["contract_months"]), 13, P["t1"])
    K.chip(d, tf, "h-c1", W - 250, 26, 202, 44, "不是法律意见", P["t1"], P["panel2"],
           border="1 SOLID " + P["border"], size=15)
    K.chip(d, tf, "h-c2", W - 470, 26, 204, 44, "条款需自行核对", P["t1"], P["panel2"],
           border="1 SOLID " + P["gold"], size=15)

    # ---------- ① 打孔状态条 ----------
    x1, cy1, w1 = K.card(d, tf, "c1", 48, 152, 1144, 168,
                         "① 打孔状态：%d 项里 %d 项不符、%d 项缺项" % (len(checks), n_bad, n_gap),
                         sub="孔没打满不是我没核对，是合同本身给不出这些数字")
    assert cy1 == 152 + 86
    pitch = 90.0
    for i, x in enumerate(checks):
        cx = x1 + 20 + i * pitch
        col = vc[x["verdict"]]
        K.disc(d, cx, cy1 + 14, 13, col)
        K.disc(d, cx, cy1 + 14, 6, P["ground"])
        K.mono(d, tf, "c1-k%d" % i, cx - 26, cy1 + 32, 52, 18, x["id"], 11, P["t2"],
               align="CENTER")
    assert x1 + 20 + 7 * pitch + 13 <= x1 + 740, x1
    lab = [("不符 %d" % n_bad, P["coral"]), ("缺项 %d" % n_gap, P["gold"]),
           ("通过 %d" % n_ok, P["grass"])]
    for i, (s, col) in enumerate(lab):
        K.chip(d, tf, "c1-c%d" % i, x1 + 760 + i * 112, cy1 + 2, 104, 30, s, col,
               P["panel2"], border="1 SOLID " + col, size=14)
    K.tlab(d, tf, "c1-n", x1 + 760, cy1 + 40, 336, 20,
           "通过 0 项：这一份合同没有一条能直接勾" if n_ok == 0 else
           "通过 %d 项" % n_ok, 12, P["t1"])
    assert cy1 + 58 <= 152 + 168 - 22, cy1

    # ---------- ② 八项核对打孔卡主体 ----------
    x2, cy2, w2 = K.card(d, tf, "c2", 48, 332, 1144, 838,
                         "② 逐项：规则／合同写的／该是多少／不对怎么办",
                         sub="五列里后四列照抄来源文本，不改写；判定只有三种：不符、缺项、通过")
    col_head = [("项目", x2 + 56, 240), ("规则与依据", x2 + 300, 200),
                ("合同／HR 写的", x2 + 516, 200), ("该是多少", x2 + 732, 156),
                ("不对怎么办", x2 + 904, 196)]
    for i, (t, hx, hw) in enumerate(col_head):
        K.tlab(d, tf, "c2-h%d" % i, hx, cy2, hw, 18, t, 12, P["t2"])
    d.line(x2, cy2 + 24, x2 + w2, cy2 + 24, 1, P["grid"])
    ry = cy2 + 34
    for i, x in enumerate(checks):
        col = vc[x["verdict"]]
        K.panel(d, x2, ry, w2, ROW_H, P["card2"], radius=12,
                border="1 SOLID " + P["border"])
        d.rect(x2, ry, 5, ROW_H, col, radius=2)
        K.disc_outline(d, x2 + 34, ry + 30, 13, 3, col)
        K.mono(d, tf, "c2-%d-id" % i, x2 + 56, ry + 14, 44, 22, x["id"], 14, col)
        K.chip(d, tf, "c2-%d-v" % i, x2 + 110, ry + 12, 88, 26, x["verdict"], col,
               P["panel2"], border="1 SOLID " + col, size=13)
        K.tlab(d, tf, "c2-%d-k" % i, x2 + 56, ry + 44, 230, 22, x["k"], 15, P["t0"])
        K.tlab(d, tf, "c2-%d-r" % i, x2 + 300, ry + 20, 200, 52, x["rule"], 12, P["t1"],
               lines=3)
        K.tlab(d, tf, "c2-%d-i" % i, x2 + 516, ry + 20, 200, 52, x["in"], 12, P["t1"],
               lines=3)
        K.tlab(d, tf, "c2-%d-s" % i, x2 + 732, ry + 20, 156, 52, x["should"], 12, col,
               lines=3)
        K.tlab(d, tf, "c2-%d-a" % i, x2 + 904, ry + 20, 196, 52, x["act"], 12, P["t1"],
               lines=3)
        ry += ROW_H + ROW_GAP
    ry -= ROW_GAP
    assert ry <= 332 + 838 - 22, ry

    # ---------- ③ 加班小时数 ----------
    x3, cy3, w3 = K.card(d, tf, "c3", 48, 1182, 1144, 184,
                         "③ 排班表上的加班：与 36 h 上限放在同一根轴上",
                         sub="轴上限 %d h 是画图取整，不是任何标准；数据只有 %d h 与 %d h 两个数"
                             % (OT_MAX, ot, cap))
    tw = 820.0
    K.hbar(d, tf, "c3-t", x3, cy3 + 10, tw, 26, ot / OT_MAX, P["coral"], bg=P["panel2"])
    tx = x3 + cap / OT_MAX * tw
    d.rect(tx - 1, cy3 + 2, 3, 42, P["gold"])
    K.mono(d, tf, "c3-cap", tx - 60, cy3 + 48, 120, 20, "上限 %d h" % cap, 12, P["gold"],
           align="CENTER")
    K.num(d, tf, "c3-v", x3 + tw + 20, cy3 + 2, 240, 40, "%d h" % ot, 30, P["coral"])
    K.tlab(d, tf, "c3-o", x3 + tw + 20, cy3 + 46, 240, 22,
           "超出 %d h＝上限的 %.0f%%" % (ot - cap, (ot - cap) / cap * 100), 13, P["t1"])
    K.tlab(d, tf, "c3-n", x3, cy3 + 52, 280, 22,
           "台账里 %d h 是 3 月单月；K5 判定就来自这条" % ot, 12, P["t2"])
    assert cy3 + 74 <= 1182 + 184 - 22, cy3

    # ---------- ④ 第一个月 ----------
    x4, cy4, w4 = K.card(d, tf, "c4", 48, 1378, 1144, 206,
                         "④ 第一个月的 6 个时间点",
                         sub="顺序按“先拿到证据，再提要求”排；每条都能留书面记录")
    fm = c["first_month"]
    fp = w4 / len(fm)
    d.line(x4 + 10, cy4 + 16, x4 + w4 - 10, cy4 + 16, 2, P["axis"])
    for i, s in enumerate(fm):
        cx = x4 + i * fp + 10
        K.disc(d, cx, cy4 + 16, 7, P["teal"])
        K.mono(d, tf, "c4-d%d" % i, cx, cy4 + 32, 120, 20, s["d"], 13, P["t0"])
        K.tlab(d, tf, "c4-k%d" % i, cx, cy4 + 54, fp - 26, 44, s["k"], 12, P["t1"],
               lines=2)
    assert cy4 + 98 <= 1378 + 206 - 22, cy4

    # ---------- ⑤ 口径与限制 ----------
    nb = K.note_band(d, tf, "c5", 48, 1594, 1144, [
        "口径：8 项判定只分不符／缺项／通过；「缺项」指合同与附件里没有写，不等于公司一定没做。",
        "规则文本是常见公开口径；来源标注里 %d 项 common_rule_needs_check、%d 项 self_defined_demo，"
        "落地前按现行法规与当地执行口径核对。"
        % (sum(1 for x in checks if x["src"] == "common_rule_needs_check"),
           sum(1 for x in checks if x["src"] == "self_defined_demo")),
        c["note"] + "；月薪、合同期、排班 61 h 与 HR 说法均为演示值；没有做真实用户验证，不声称做过。",
    ], size=13)
    K.credit(d, tf, "c5-cr", 48, nb + 10, 1144, [
        "数据：tmp/%s/B06/research/demo.json（case10，seed=%s）｜8 项 ＝ 不符 %d＋缺项 %d＋通过 %d｜"
        "打印尺寸 1240×1754（A4 比例）" % (RID, K.data()["seed"], n_bad, n_gap, n_ok),
    ])
    assert nb + 34 <= H - 16, nb
    info = {"case": "10", "kind": "everyday-info-reinvented", "canvas": [W, H],
            "checks": len(checks), "n_bad": n_bad, "n_gap": n_gap, "n_ok": n_ok,
            "overtime": [ot, cap, ot - cap], "first_month": len(fm),
            "src_kinds": sorted(set(x["src"] for x in checks))}
    return d, tf, info


if __name__ == "__main__":
    d, tf, info = build()
    print("texts", tf.n, "problems", tf.problems)
    print(info)
