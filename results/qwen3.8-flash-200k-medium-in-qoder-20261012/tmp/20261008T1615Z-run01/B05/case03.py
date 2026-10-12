"""件-03 值班室调度大屏（2560×1440，实时态）。

内容任务：值班员在 3 米外一眼看清"风险在哪、今天谁做什么、哪张单超时"。
所有数字来自同一份 stats.json / orders.json；字号按大屏最小 20 px 设定。
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B05"))
import b05kit as B  # noqa: E402

W, H = 2560, 1440


def build():
    st = B.data()
    wo = json.load(open(ROOT / "tmp" / RID / "B05" / "research" / "orders.json",
                        encoding="utf-8"))
    orders = wo["orders"]
    mx = B.trees()
    names = {i["street_code"]: i["street"] for i in st["incidents"]}

    # ---- 头部 ----
    d, tf = B.doc(W, H, ground="dark")
    MX = 64
    d.rect(0, 0, W, 116, "#0B1009")
    d.rect(0, 116, W, 3, d.P["leaf"])
    B.tlab(d, tf, "h-t", MX, 22, 1100, 56, "枝安 · 行道树风险调度台", 40, d.P["t0"],
           style="BOLD")
    B.tlab(d, tf, "h-s", MX, 80, 1100, 28, "汀州市园林中心 值班室 ｜ 每 5 分钟刷新 ｜ "
           "字号按 3 米视距设定", 20, d.P["t2"])
    B.num(d, tf, "h-clock", W - MX - 420, 20, 420, 60, "09:20", 52, d.P["t0"])
    B.mono(d, tf, "h-snap", W - MX - 560, 84, 560, 26,
           "数据快照 %s" % st["generated_at"][:16].replace("T", " "), 20, d.P["t2"],
           align="END")

    # ---- KPI 行 ----
    in_prog = st["orders"]["total"] - st["orders"]["states"]["已归档"]
    kpis = [("在册行道树", B.fmt(st["total"]), "%d 条路段 / %d 个街道"
             % (st["roads"], st["streets"]), d.P["t0"]),
            ("立即处置", B.fmt(st["bands"]["立即处置"]), "R≥70 ｜ 24 h 内必须到场",
             d.P["rust"]),
            ("限期处置", B.fmt(st["bands"]["限期处置"]), "55-69 ｜ 72 h 内完成",
             d.P["amber"]),
            ("在办工单", B.fmt(in_prog), "累计开单 %d 张" % st["orders"]["total"],
             d.P["teal"]),
            ("超时", B.fmt(st["orders"]["overdue"]), "其中立即处置 %d 张"
             % st["orders"]["overdue_urgent"], d.P["rust"])]
    kw = (W - 2 * MX - 4 * 20) / 5.0
    for i, (lab, val, sub, col) in enumerate(kpis):
        x = MX + i * (kw + 20)
        B.panel(d, x, 146, kw, 172, d.P["card"], radius=16,
                border="1 SOLID " + d.P["border"])
        d.rect(x, 146, 6, 172, col)
        B.tlab(d, tf, "k%d-l" % i, x + 26, 164, kw - 46, 30, lab, 24, d.P["t2"])
        B.num(d, tf, "k%d-v" % i, x + 26, 196, kw - 46, 84, val, 68, col)
        B.tlab(d, tf, "k%d-s" % i, x + 26, 286, kw - 46, 26, sub, 19, d.P["t2"])

    # ---- 左：热力栅格 ----
    LX, LW = MX, 1380
    px, py, pw = B.card(d, tf, "heat", LX, 348, LW, 662)
    B.tlab(d, tf, "heat-t", px, py, 900, 36, "立即处置树的空间落点", 30, d.P["t0"],
           style="BOLD")
    B.tlab(d, tf, "heat-s", px, py + 40, pw, 28,
           "8×8 栅格，每格约 1.2 km 见方；格内数字＝该格 R≥70 的棵数；报号用列 A–H 行 1–8",
           20, d.P["t2"])
    gx0, gy0, cw_, ch_, gap = px + 34, py + 106, 150, 50, 8
    for c in range(8):
        B.tlab(d, tf, "hc-c%d" % c, gx0 + c * (cw_ + gap), gy0 - 28, cw_, 24,
               "ABCDEFGH"[c], 19, d.P["t2"], align="CENTER")
    for r, row in enumerate(st["heat"]):
        B.tlab(d, tf, "hc-r%d" % r, px, gy0 + r * (ch_ + gap) + 12, 26, 26,
               "%d" % (r + 1), 19, d.P["t2"], align="CENTER")
        for c, v in enumerate(row):
            n = int(round(v / 100.0))
            x = gx0 + c * (cw_ + gap)
            y = gy0 + r * (ch_ + gap)
            col = (d.P["rust"] if n >= 4 else d.P["amber"] if n >= 2 else
                   "#33502F" if n == 1 else d.P["grid"])
            d.rect(x, y, cw_, ch_, col, radius=6)
            if n:
                B.num(d, tf, "hc%d%d" % (r, c), x + 8, y + 12, cw_ - 16, 32, "%d" % n,
                      24, "#FFFFFF")
    ly = gy0 + 8 * (ch_ + gap) + 12
    for i, (col, lab) in enumerate([(d.P["grid"], "0 棵"), ("#33502F", "1 棵"),
                                    (d.P["amber"], "2-3 棵"), (d.P["rust"], "≥4 棵")]):
        x = px + i * 170
        d.rect(x, ly + 6, 26, 20, col, radius=4)
        B.tlab(d, tf, "lg%d" % i, x + 36, ly + 2, 120, 28, lab, 20, d.P["t2"])
    inside = int(round(sum(sum(r) for r in st["heat"]) / 100.0))
    B.tlab(d, tf, "heat-n", px + 720, ly + 2, pw - 720, 28,
           "栅格覆盖 %d / %d 棵，其余 %d 棵落在网格外缘（东、南两侧）"
           % (inside, st["bands"]["立即处置"], st["bands"]["立即处置"] - inside),
           20, d.P["t2"], align="END")

    # ---- 右上：工单流水 ----
    RX, RW = MX + LW + 32, W - MX - (MX + LW + 32)
    px, py, pw = B.card(d, tf, "flow", RX, 348, RW, 316)
    B.tlab(d, tf, "flow-t", px, py, pw, 36, "工单流水（状态分布）", 30, d.P["t0"],
           style="BOLD")
    B.tlab(d, tf, "flow-s", px, py + 40, pw, 28,
           "累计 %d 张 ｜ 在办 %d 张 ｜ 非漏斗：状态是并行工位 ｜ 琥珀＝尚未到场"
           % (st["orders"]["total"], in_prog), 20, d.P["t2"])
    yy = py + 78
    bw = pw - 300
    for s in wo["flow"]:
        n = st["orders"]["states"][s]
        B.tlab(d, tf, "f-%s" % s, px, yy, 150, 28, s, 21, d.P["t1"])
        B.hbar(d, tf, "fb-%s" % s, px + 164, yy + 6, bw, 18, n / 70.0,
               d.P["teal"] if s not in ("待复核", "已派单") else d.P["amber"],
               bg=d.P["grid"])
        B.num(d, tf, "fv-%s" % s, px + pw - 120, yy, 120, 30, "%d" % n, 23, d.P["t0"])
        yy += 32

    # ---- 右下：超时清单 ----
    px, py, pw = B.card(d, tf, "od", RX, 694, RW, 316)
    B.tlab(d, tf, "od-t", px, py, pw - 300, 36, "超时最多的 5 张单", 30, d.P["rust"],
           style="BOLD")
    od = sorted([o for o in orders if o["overdue"]],
                key=lambda o: -(o["age_hours"] - o["sla_hours"]))
    B.tlab(d, tf, "od-s", px, py + 40, pw, 28,
           "超时 %d 张 ｜ 已归档但曾超时 %d 张 ｜ 时长＝开单至今 − SLA"
           % (st["orders"]["overdue"], sum(1 for o in od if o["state"] == "已归档")),
           20, d.P["t2"])
    cols = [("工单 / 树号", 380, "START"), ("路段", 190, "START"),
            ("档位", 150, "START"), ("状态", 140, "START"),
            ("超时", 130, "END")]
    B.coltable(d, tf, "odt", px, py + 76, pw, cols,
               [[("%s · %s" % (o["wo"], o["tree"])), o["road"], o["band"], o["state"],
                 "+%d h" % (o["age_hours"] - o["sla_hours"])] for o in od[:5]],
               row_h=32, head_h=34, size=20, head_size=18)

    # ---- 左下：街道构成 ----
    px, py, pw = B.card(d, tf, "str", LX, 1040, LW, 290)
    B.tlab(d, tf, "str-t", px, py, 700, 34, "六个街道的风险构成", 28, d.P["t0"],
           style="BOLD")
    order_keys = [("urgent", d.P["rust"], "立即处置"), ("limited", d.P["amber"], "限期"),
                  ("watch", "#B98A16", "观察")]
    lx = px + 400
    for key, col, lab in order_keys:
        d.rect(lx, py + 8, 24, 18, col)
        B.tlab(d, tf, "sl-%s" % key, lx + 32, py + 4, 110, 26, lab, 19, d.P["t2"])
        lx += 150
    B.tlab(d, tf, "str-n", lx + 6, py + 4, 430, 26, "条长＝非正常棵数，不含「正常」",
           19, d.P["t2"])
    yy = py + 48
    risks = {c: ps["total"] - ps["normal"] for c, ps in st["per_street"].items()}
    rmax = max(risks.values())
    wseg = pw - 146 - 250
    for code, ps in sorted(st["per_street"].items(), key=lambda kv: -kv[1]["urgent"]):
        B.tlab(d, tf, "sn-%s" % code, px, yy, 130, 28, names.get(code, code), 21,
               d.P["t1"])
        x = px + 146
        rk = risks[code]
        for key, col, _ in order_keys:
            seg = wseg * rk / float(rmax) * ps[key] / float(rk)
            d.rect(x, yy + 4, seg, 22, col)
            x += seg
        B.num(d, tf, "sv-%s" % code, px + pw - 244, yy, 244, 30,
              "%d 棵 ｜ %.1f %%" % (rk, 100.0 * rk / ps["total"]), 19, d.P["t2"])
        yy += 32

    # ---- 右下：班组与覆盖率 ----
    px, py, pw = B.card(d, tf, "crew", RX, 1040, RW, 290)
    B.tlab(d, tf, "crew-t", px, py, pw, 34, "班组负载（在办 / 累计 327 张）", 28,
           d.P["t0"], style="BOLD")
    inhand = {}
    for o in orders:
        if o["state"] != "已归档":
            inhand[o["crew"]] = inhand.get(o["crew"], 0) + 1
    yy = py + 50
    crews = sorted(st["orders"]["crew"].items(), key=lambda kv: -inhand.get(kv[0], 0))
    for name, n in crews:
        B.tlab(d, tf, "cw-%s" % name, px, yy, 210, 28, name, 21, d.P["t1"])
        B.hbar(d, tf, "cb-%s" % name, px + 224, yy + 4, pw - 384, 20,
               inhand.get(name, 0) / 100.0, d.P["leaf"], bg=d.P["grid"])
        B.num(d, tf, "cv-%s" % name, px + pw - 150, yy, 150, 30,
              "%d / %d" % (inhand.get(name, 0), n), 22, d.P["t0"])
        yy += 38
    B.tlab(d, tf, "cw-n", px, yy + 6, pw, 28,
           "90 天巡检覆盖率 %.1f %% ｜ 365 天 %.1f %% ｜ 超 365 天未巡检 %s 棵"
           % (st["coverage_90d"], st["coverage_365d"],
              B.fmt(st["inspect_age"][">365 天"])), 20, d.P["t2"])

    B.credit(d, tf, "foot", MX, 1352, W - 2 * MX, [
        "演示数据：汀州市与「枝安」为虚构产品，3,725 棵树与全部工单由 b05data.py（固定种子 "
        "%d）生成，可复算；本页不含任何真实市政系统数据。" % st["seed"],
        "栅格由树的档案坐标聚合；「超时」＝ age − SLA > 0，已归档单仍计入历史超时。"],
        size=18)
    return d, tf, dict(case="case-03", kind="值班室调度大屏（实时态）",
                       total=st["total"], urgent=st["bands"]["立即处置"],
                       overdue=st["orders"]["overdue"], inside=inside)
