"""件-08「14 个图标，我只想选对这一件」1080×1920（洗衣机面板贴纸）。

原始口径：旋钮旁 14 个程序图标，只有名字（demo.json `cases.case08.progs`）。
换算：把"面料含棉吗／脏污够重吗／今晚来得及吗"三问画成三层扇环，14 个程序逐层收敛。
行动：给出 3 个能用的程序与各自结束时刻、剩余晾晒窗口，以及 4 个最容易误选的程序。

程序名、温度、转速、时长全部是 self_defined_demo；note 字段声明"以你家机器说明书为准"。
没有做真实用户验证，不声称做过。
"""
import math
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for _p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B06"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import b06kit as K  # noqa: E402

W, H = 1080, 1920
CX, RMAX = 540.0, 272.0


def pol(cy, r, deg):
    a = math.radians(deg)
    return CX + r * math.cos(a), cy + r * math.sin(a)


def mins(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def clock(total):
    return "%02d:%02d" % (total // 60 % 24, total % 60)


PREP = 15          # 到家到开机之间的预处理分钟数（步骤 1–3，演示值）


def build():
    d, tf = K.doc(W, H, ground="dark")
    P = d.P
    c = K.data()["cases"]["case08"]
    progs, q = c["progs"], c["q"]
    n = len(progs)
    slot = 180.0 / n

    g1 = [i for i in range(n) if q["fab"] in progs[i]["fab"]]
    g2 = [i for i in g1 if q["soil"] in progs[i]["soil"]]
    g3 = [i for i in g2 if progs[i]["min"] <= q["max_min"]
          and not progs[i].get("empty")]
    assert (len(g1), len(g2), len(g3)) == (6, 3, 3), (len(g1), len(g2), len(g3))
    assert set(p["id"] for p in c["pick"]) == set(progs[i]["id"] for i in g3), g3
    best = sorted(c["pick"], key=lambda p: (-p["score"], p["min"]))[0]
    assert best["id"] == c["pick"][0]["id"], (best, c["pick"][0])
    dry_by = mins(q["must_dry_by"])
    start = mins(q["clock_in"])
    # demo.json 的 done_at ＝ 到家立即开机；本图把 PREP 分钟预处理算进去，另加一次推迟
    assert all(mins(p["done_at"]) == start + p["min"] for p in c["pick"]), c["pick"]

    def finish(p):
        return clock(mins(p["done_at"]) + PREP)

    # ---------- 页眉 ----------
    d.rect(0, 0, W, 92, K.BASE)
    d.rect(0, 90, W, 2, P["line"])
    K.tlab(d, tf, "h-t", 40, 14, 660, 40, "14 个图标，我只想选对这一件", 30, P["t0"])
    K.tlab(d, tf, "h-s", 40, 56, 640, 24,
           "沾了火锅红油的棉 T 恤｜%s 到家，%s 前要干" % (q["clock_in"], q["must_dry_by"]),
           15, P["t2"])
    K.chip(d, tf, "h-c1", W - 236, 22, 196, 42, "演示程序名", P["t1"],
           P["panel2"], border="1 SOLID " + P["border"], size=15)
    K.chip(d, tf, "h-c2", W - 452, 22, 200, 42, "答案：%s" % best["name"], P["t0"],
           P["panel2"], border="1 SOLID " + P["gold"], size=15)

    # ---------- ① 面板原样 ----------
    x1, cy1, w1 = K.card(d, tf, "c1", 40, 104, 1000, 240,
                         "① 面板上有的：14 个名字",
                         sub="旋钮旁边只有图标和程序名，温度／转速／能洗什么都不写")
    for i, p in enumerate(progs):
        bx = x1 + (i % 7) * 136
        by = cy1 + (i // 7) * 52
        K.panel(d, bx, by, 130, 44, P["card2"], radius=10,
                border="1 SOLID " + P["border"])
        K.mono(d, tf, "c1-i%d" % i, bx + 8, by + 4, 40, 18, p["id"], 11, P["t2"])
        K.tlab(d, tf, "c1-n%d" % i, bx + 8, by + 22, 116, 20, p["name"], 13, P["t0"])
    K.tlab(d, tf, "c1-f", x1, cy1 + 106, w1, 22,
           "14 个里有 %d 个是空桶程序（筒自洁／单脱水／漂洗＋脱水），%d 个带衣物。"
           % (sum(1 for p in progs if p.get("empty")),
              sum(1 for p in progs if not p.get("empty"))), 13, P["t2"])
    assert cy1 + 128 <= 104 + 240 - 22, cy1

    # ---------- ② 决策扇形 ----------
    x2, cy2, w2 = K.card(d, tf, "c2", 40, 360, 1000, 690,
                         "② 三问收敛：14 → %d → %d → 1" % (len(g1), len(g2)),
                         sub="外环＝面料，中环＝脏污等级，内环＝今晚来得及；灰段是被筛掉的")
    fy0 = cy2 + 30
    CY = fy0 + RMAX + 30
    rings = [(RMAX, RMAX - 40, g1, P["teal"]),
             (RMAX - 52, RMAX - 92, g2, P["gold"]),
             (RMAX - 104, RMAX - 144, g3, P["grass"])]
    for i in range(n):
        a0 = 180 + i * slot + 1.0
        a1 = 180 + (i + 1) * slot - 1.0
        for ro, ri, keep, col in rings:
            K.pie_ring(d, CX, CY, ro, ri, a0, a1, col if i in keep else P["border"])
        lx, ly = pol(CY, RMAX + 28, 180 + (i + 0.5) * slot)
        K.mono(d, tf, "c2-l%d" % i, lx - 26, ly - 10, 52, 20, progs[i]["id"], 12,
               P["t0"] if i in g3 else P["t2"], align="CENTER")
    K.disc(d, CX, CY, 104, P["card2"])
    K.disc_outline(d, CX, CY, 104, 2, P["gold"])
    K.tlab(d, tf, "c2-h0", CX - 96, CY - 76, 192, 22, "选这个", 13, P["t2"],
           align="CENTER")
    K.tlab(d, tf, "c2-h1", CX - 96, CY - 50, 192, 28, best["name"], 19, P["t0"],
           align="CENTER")
    K.mono(d, tf, "c2-h2", CX - 96, CY - 14, 192, 22,
           "%d min｜%d℃｜%d 转" % (best["min"], best["temp"], best["rpm"]), 13,
           P["t1"], align="CENTER")
    K.mono(d, tf, "c2-h3", CX - 96, CY + 16, 192, 22,
           "%s 结束" % finish(best), 14, P["gold"], align="CENTER")
    leg = [("问① 面料含棉（外环）", "%d → %d 个" % (n, len(g1)), P["teal"],
            "棉 T 恤先看这一条：化纤／牛仔／羊毛／真丝／空桶程序全部排除"),
           ("问② 脏污够重（中环）", "%d → %d 个" % (len(g1), len(g2)), P["gold"],
            "重脏要温度与机械力够；40℃ 以下的棉麻程序带不动红油"),
           ("问③ 来得及（内环）", "%d → %d 个" % (len(g2), len(g3)), P["grass"],
            "时长 ≤ %d min 且非空桶；三个都在 %s 前洗完" % (q["max_min"], q["must_dry_by"])),
           ("再按评分与结束时刻排序", "%d → 1 个" % len(g3), P["t0"],
            "%s 与 %s 同为 %d 分，%s 早 %d min 结束、转速高 %d 转更好晾"
            % (c["pick"][0]["id"], c["pick"][1]["id"], c["pick"][0]["score"],
               c["pick"][0]["id"], c["pick"][1]["min"] - c["pick"][0]["min"],
               c["pick"][0]["rpm"] - c["pick"][1]["rpm"]))]
    ly = CY + 112
    for i, (lab, cnt, col, why) in enumerate(leg):
        d.rect(x2, ly + 5, 6, 16, col)
        K.tlab(d, tf, "c2-g%d" % i, x2 + 16, ly, 210, 22, lab, 14, P["t0"])
        K.mono(d, tf, "c2-c%d" % i, x2 + 232, ly, 96, 22, cnt, 13, col)
        K.tlab(d, tf, "c2-w%d" % i, x2 + 336, ly, w2 - 336, 22, why, 13, P["t2"])
        ly += 28
    assert ly <= 360 + 690 - 22, ly

    # ---------- ③ 三个候选的账 ----------
    x3, cy3, w3 = K.card(d, tf, "c3", 40, 1066, 1000, 320,
                         "③ 三个候选各留下多少晾晒时间",
                         sub="结束时刻含 %d min 预处理；晾干所需时间没有实测数据" % PREP)
    rows = []
    for p in c["pick"]:
        left = dry_by - mins(finish(p))
        rows.append([(p["id"] + " " + p["name"], P["t0"]), "%d℃" % p["temp"],
                     "%d" % p["rpm"], "%d min" % p["min"], finish(p),
                     ("%d min" % left, P["gold"] if left >= 75 else P["coral"]),
                     ("推荐" if p["id"] == best["id"] else "备选",
                      P["grass"] if p["id"] == best["id"] else P["t1"])])
    ty = K.coltable(d, tf, "c3-t", x3, cy3, w3,
                    [("程序", 250, "START"), ("水温", 80, "END"), ("转速", 80, "END"),
                     ("时长", 90, "END"), ("结束", 90, "END"), ("剩可晾", 100, "END"),
                     ("判定", 66, "END")],
                    rows, row_h=40, head_h=34, size=14)
    av = c["avoid"]
    neg = Counter(r for a in av for r in a["why"]
                  if r not in ("面料匹配", "可处理油脂"))
    K.tlab(d, tf, "c3-f1", x3, ty + 10, w3, 22,
           "最容易误选的 %d 个（14 个里共 %d 个不选）：%s"
           % (len(av), n - len(c["pick"]),
              "、".join("%s %s" % (a["id"], a["name"]) for a in av)), 13, P["t1"])
    K.tlab(d, tf, "c3-f2", x3, ty + 32, w3, 22,
           "它们的失败原因计数：%s——第一个问题看着都能过，卡在第二问。"
           % "、".join("%s×%d" % (kk, vv) for kk, vv in neg.most_common()), 13, P["coral"])
    assert ty + 54 <= 1066 + 320 - 22, ty

    # ---------- ④ 今晚的时间账与洗前动作 ----------
    x4, cy4, w4 = K.card(d, tf, "c4", 40, 1402, 1000, 366,
                         "④ 今晚的时间账",
                         sub="%s 到家到 %s 要干，中间一共 %d 分钟" % (
                             q["clock_in"], q["must_dry_by"], dry_by - mins(q["clock_in"])))
    nodes = [(q["clock_in"], "到家", "刮掉凝固的牛油"),
             (clock(start + 8), "涂洗涤剂", "领口／油点，静置 5–10 min"),
             (clock(start + PREP), "开机", "翻面、拉好拉链"),
             (finish(best), "洗完", "%s %d min" % (best["name"], best["min"])),
             (q["must_dry_by"], "要干", "剩 %d min 晾晒" % (dry_by - mins(finish(best))))]
    ty4 = cy4 + 26
    seg = (w4 - 240) / (len(nodes) - 1)
    d.line(x4 + 120, ty4 + 34, x4 + 120 + seg * (len(nodes) - 1), ty4 + 34, 3,
           P["axis"])
    for i, (t_, name, note) in enumerate(nodes):
        cx = x4 + 120 + seg * i
        last = i == len(nodes) - 1
        d.dot(cx, ty4 + 35, 15, P["gold"] if last else P["teal"])
        K.mono(d, tf, "c4-t%d" % i, cx - 70, ty4, 140, 22, t_, 14,
               P["gold"] if last else P["t1"], align="CENTER")
        K.tlab(d, tf, "c4-n%d" % i, cx - 110, ty4 + 50, 220, 22, name, 15, P["t0"],
               align="CENTER")
        K.tlab(d, tf, "c4-d%d" % i, cx - 110, ty4 + 74, 220, 22, note, 12, P["t2"],
               align="CENTER")
    sy = ty4 + 108
    for i, s in enumerate(c["steps"]):
        K.mono(d, tf, "c4-s%d" % i, x4, sy, 30, 22, "%d" % (i + 1), 14, P["gold"])
        K.tlab(d, tf, "c4-b%d" % i, x4 + 38, sy, w4 - 38, 22, s, 13, P["t1"])
        sy += 24
    assert sy <= 1402 + 366 - 22, sy

    # ---------- ⑤ 口径与限制 ----------
    nb = K.note_band(d, tf, "c5", 40, 1784, 1000, [
        "口径：三问按面料→脏污→时间逐层筛，判据取自面板程序表；结束时刻含 %d min "
        "预处理（原始数据按到家立即开机算）。" % PREP,
        "「剩可晾」只是两个时刻之差，不等于一定能干；%s；没有做真实用户验证。" % c["note"],
    ], size=14)
    K.credit(d, tf, "c5-cr", 40, nb + 10, 1000, [
        "数据：tmp/%s/B06/research/demo.json（b06data.py case08，seed=%s）｜"
        "扇环 3 层 ×14 段，弧线为图元逼近。" % (RID, K.data()["seed"]),
    ])
    assert nb + 36 <= H - 16, nb
    info = {"case": "08", "kind": "everyday-info-reinvented", "canvas": [W, H],
            "programs": n, "gates": {"fabric": len(g1), "soil": len(g2),
                                     "time": len(g3)},
            "fan": {"rings": 3, "r_out": RMAX, "slot_deg": round(slot, 3)},
            "pick": best["id"], "pick_finish": finish(best),
            "prep_min": PREP,
            "drying_window_min": dry_by - mins(finish(best)),
            "avoid": [a["id"] for a in av]}
    return d, tf, info


if __name__ == "__main__":
    d, tf, info = build()
    print("texts", tf.n, "problems", tf.problems)
    print(info)
