"""件-05 台风前 48 小时加固优先序（1920×1200，平板，规划态）。

内容任务：98 棵"立即处置"不可能一夜做完，这屏要回答两件事——
名额怎么排（排序键可复算），以及排完之后还差多少（容量与物料）。
"""
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "B05"))
import b05kit as B  # noqa: E402

W, H = 1920, 1200
CAP = 12                      # 本轮可调配的加固名额（3 个班组 × 4 棵）


def build():
    st = B.data()
    mx = B.trees()["trees"]
    f = st["featured"]["tree"]
    urg = sorted([t for t in mx if t["band"] == "立即处置"],
                 key=lambda t: (-t["risk"], -t["exposure"], -t["tilt_deg"]))
    plan = urg[:CAP]
    rank = [i for i, t in enumerate(urg, 1) if t["id"] == f["id"]][0]
    fence = sum(2 * math.pi * (t["height_m"] + 6.0) for t in plan)
    hard, tape = round(fence / 3.0 / 5) * 5, round(fence * 2 / 3 / 5) * 5
    cones = 16 * CAP        # 与件-06 单树布设图同口径：每树 16 只、间距 6 m

    d, tf = B.doc(W, H, ground="light")
    MX = 64
    # ---- 头部 ----
    B.tlab(d, tf, "h-t", MX, 40, 900, 54, "台风前 48 小时：加固优先序", 38, d.P["t0"],
           style="BOLD")
    B.tlab(d, tf, "h-s", MX, 96, 900, 30, "值班调度排定 · 平板横屏 · 名单可直接派给班组",
           19, d.P["t2"])
    scen = [("情景", "演练：虚构台风「叠浪」"), ("登陆", "10-13 02:00 前后"),
            ("阵风", "12-13 级"), ("持续雨", "80-140 mm")]
    x = W - MX
    for lab, val in reversed(scen):
        w = 46 + 21 * len(val)
        B.panel(d, x - w, 44, w, 76, d.P["card2"], radius=12,
                border="1 SOLID " + d.P["border"])
        B.tlab(d, tf, "sc-%s" % lab, x - w + 18, 54, w - 36, 24, lab, 15, d.P["t2"])
        B.tlab(d, tf, "sv-%s" % lab, x - w + 18, 78, w - 36, 30, val, 19, d.P["t0"])
        x -= w + 14

    # ---- KPI 条 ----
    kpis = [("立即处置总数", "%d 棵" % st["bands"]["立即处置"], "R≥70，24 h 内需到场",
             d.P["rust"]),
            ("本轮排入", "%d 棵" % CAP, "3 个班组 × 4 棵", d.P["leaf"]),
            ("本轮未排入", "%d 棵" % (st["bands"]["立即处置"] - CAP), "转入下一轮，仍挂限时",
             d.P["amber"]),
            ("硬质围挡", "%s m" % B.fmt(hard), "只围道路侧 1/3 弧长", d.P["teal"]),
            ("警示带 / 交通锥", "%s m / %d 只" % (B.fmt(tape), cones),
             "其余弧长软隔离；每树 16 只、间距 6 m",
             d.P["t0"])]
    kw = (W - 2 * MX - 4 * 18) / 5.0
    for i, (lab, val, sub, col) in enumerate(kpis):
        x = MX + i * (kw + 18)
        B.panel(d, x, 150, kw, 138, d.P["card"], radius=14,
                border="1 SOLID " + d.P["border"])
        d.rect(x, 150, 5, 138, col)
        B.tlab(d, tf, "k%d-l" % i, x + 22, 164, kw - 40, 26, lab, 18, d.P["t2"])
        B.num(d, tf, "k%d-v" % i, x + 22, 192, kw - 40, 46, val, 34, col)
        B.tlab(d, tf, "k%d-s" % i, x + 22, 248, kw - 40, 26, sub, 15, d.P["t2"])

    # ---- 左：排序解释 + R 分布 ----
    LW = 1096
    px, py, pw = B.card(d, tf, "why", MX, 316, LW, 812)
    B.tlab(d, tf, "why-t", px, py, 700, 36, "名额怎么排出来的", 26, d.P["t0"],
           style="BOLD")
    keys = [("①", "风险分 R 从高到低", "R = 0.30 倾斜 + 0.25 空洞 + 0.20 根系 + 0.15 "
             "暴露 + 0.10 历史"),
            ("②", "R 相同时看暴露对象分", "下游 12 m 内是人车密集点者优先"),
            ("③", "仍相同看实测倾斜角", "三键都不分才按树号，排序可复算"),
            ("④", "已在办的不占名额", "班组已到场的单走原工单，不重复排")]
    yy = py + 48
    for idx, (n, t, s) in enumerate(keys):
        B.chip(d, tf, "ky%d-i" % idx, px, yy, 40, 34, n, "#FFFFFF", d.P["leaf"],
               size=18)
        B.tlab(d, tf, "ky%d-t" % idx, px + 54, yy + 2, 420, 30, t, 20, d.P["t0"])
        B.tlab(d, tf, "ky%d-s" % idx, px + 54, yy + 32, pw - 64, 26, s, 16, d.P["t2"])
        yy += 56
    B.note_band(d, tf, "why-n", px, yy + 4, pw, [
        "没有用「离台风路径的距离」这一项：本轮没有可查证的官方路径与阵风预报接口，",
        "硬编一个距离因子会让排序看起来比实际更准。演练情景只用于设定 48 h 时限。"],
        size=16)
    # R 分布条形图
    cy = yy + 4 + 22 + 2 * 26 + 18
    B.tlab(d, tf, "ch-t", px, cy, 700, 30, "前 20 名的风险分（红＝本轮排入，灰＝转入下一轮）",
           20, d.P["t1"])
    cy += 36
    ch = 196
    base = cy + ch
    d.rect(px, base, pw, 2, d.P["line"])
    for gv in (70, 75, 80):
        gy = base - (gv - 68) / (84 - 68) * ch
        d.rect(px, gy, pw, 1, d.P["grid"])
        B.mono(d, tf, "gv%d" % gv, px, gy - 24, 60, 22, "%d" % gv, 15, d.P["t2"])
    n = 20
    bw = (pw - 70 - (n - 1) * 6) / n
    cut_x = px + 70 + CAP * (bw + 6)
    d.line(cut_x, cy - 8, cut_x, base, 3, d.P["rust"])
    B.tlab(d, tf, "cut", cut_x - 190, cy - 34, 180, 26, "本轮名额 12 →", 16, d.P["rust"],
           align="END")
    for i, t in enumerate(urg[:n]):
        x = px + 70 + i * (bw + 6)
        hgt = (t["risk"] - 68) / (84 - 68) * ch
        col = d.P["rust"] if i < CAP else "#C9C2B4"
        d.rect(x, base - hgt, bw, hgt, col, radius=3)
        B.mono(d, tf, "cx%d" % i, x - 8, base + 8, bw + 20, 22,
               t["id"].replace("TZ-", ""), 12, d.P["t2"], align="CENTER")
        B.num(d, tf, "cv%d" % i, x - 6, base - hgt - 26, bw + 12, 24, "%d" % t["risk"],
              15, d.P["t1"], align="CENTER")
    B.tlab(d, tf, "ch-x", px, base + 36, pw, 26,
           "树号（路段代码-序号）；R 值相同者按暴露对象分、再按倾斜角排序", 15, d.P["t2"])
    # 入选末位 vs 落选首位
    a, b_ = urg[CAP - 1], urg[CAP]
    why = ("R 低 %d 分" % (a["risk"] - b_["risk"]) if a["risk"] != b_["risk"] else
           ("同 R，暴露 %d < %d" % (b_["exposure"], a["exposure"])
            if b_["exposure"] != a["exposure"] else
            ("同 R 同暴露，倾斜 %.2f° < %.2f°" % (b_["tilt_deg"], a["tilt_deg"])
             if abs(b_["tilt_deg"] - a["tilt_deg"]) > 1e-9 else
             "三键全同，按 ④ 树号字典序 %s ＜ %s" % (a["id"][3:], b_["id"][3:]))))
    B.tlab(d, tf, "cmp-t", px, base + 70, pw, 28,
           "入选末位 vs 落选首位：并列时按 ②③ 破开", 18, d.P["t1"])
    for i, (tag, t, tail) in enumerate([
            ("第 %d 名" % CAP, a, "占最后 1 个名额"),
            ("第 %d 名" % (CAP + 1), b_, "落选：%s" % why)]):
        y = base + 104 + i * 34
        B.tlab(d, tf, "cmp%d" % i, px, y, pw, 30,
               "%s %s ｜ %s ｜ R=%d ｜ 暴露 %d ｜ 倾斜 %.1f° ｜ %s" %
               (tag, t["id"], t["road"], t["risk"], t["exposure"], t["tilt_deg"],
                tail), 17, d.P["t0"] if i == 0 else d.P["t2"], font=B.MONO)

    # ---- 右：清单 ----
    RX, RW = MX + LW + 32, W - MX - (MX + LW + 32)
    px, py, pw = B.card(d, tf, "list", RX, 316, RW, 812)
    B.tlab(d, tf, "list-t", px, py, pw, 36, "本轮加固清单（12 棵）", 26, d.P["t0"],
           style="BOLD")
    B.tlab(d, tf, "list-s", px, py + 40, pw, 26,
           "园林二班全天在件-04 处置单，本轮由另 3 班各做 4 棵；日时＝开始时刻",
           16, d.P["t2"])
    on_crew = [o["crew"] for o in json.load(
        open(ROOT / "tmp" / RID / "B05" / "research" / "orders.json",
             encoding="utf-8"))["orders"] if o["tree"] == f["id"]][0]
    crews = [c for c in sorted(st["orders"]["crew"].keys()) if c != on_crew]
    cols = [("序", 38, "END"), ("树号 / 路段", 256, "START"), ("R", 38, "END"),
            ("措施", 90, "START"), ("班组", 116, "START"), ("日时", 78, "START")]
    rows = []
    for i, t in enumerate(urg[:CAP]):
        rows.append(["%d" % (i + 1),
                     "%s ｜ %s" % (t["id"], t["road"]),
                     "%d" % t["risk"],
                     "钢撑+疏剪" if t["cavity_pct"] >= 35 else "钢撑+围挡",
                     crews[i % 3].replace("·", ""),
                     "%d日%02d" % (11 + i // 9, 8 + (i % 9) // 3 * 4)])
    y2 = B.coltable(d, tf, "lt", px, py + 72, pw, cols, rows, row_h=38, head_h=36,
                    size=15, head_size=14)
    B.note_band(d, tf, "list-n", px, y2 + 14, pw, [
        "第 %d 名 %s（R=%d）不进本表：" % (rank, f["id"], f["risk"]),
        "它 08:20 已开单、09:58 班组到场，走件-04 闭环；",
        "算进本轮等于把同一批人力排两次。"], size=16)
    B.tlab(d, tf, "list-f", px, y2 + 14 + 112 + 10, pw, 28,
           "剩余 %d 棵立即处置树转入下一轮，仍按 24 h 挂限时。"
           % (st["bands"]["立即处置"] - CAP), 17, d.P["amber"])

    B.credit(d, tf, "foot", MX, 1138, W - 2 * MX, [
        "演示数据：树号、风险分、暴露对象、班组与台风情景均为虚构（b05data.py，固定种子 "
        "%d）；名额 12 = 3 个班组各 4 棵，是产品设定的调度参数，不是行业规范。" % st["seed"],
        "围挡长度按各树禁入半径的圆周长估算，道路侧 1/3 用硬质围挡、其余用警示带；未做真实用户验证。"],
        size=15)
    return d, tf, dict(case="case-05", kind="台风前 48 h 加固优先序（平板，规划态）",
                       urgent=st["bands"]["立即处置"], cap=CAP, rank=rank,
                       hard_fence_m=hard, tape_m=tape, cones=cones)
