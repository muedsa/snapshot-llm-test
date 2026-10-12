"""B01 case-04 · 急诊科分诊态势屏（2560×1440，暗色大屏）。

受众：急诊护士长与分诊台护士；使用时刻：21:30 交班高峰，站在 8 米外的走廊里
判断「哪个科室压床、谁等得最久、下一辆救护车几点到」。
所有数字来自同一份虚构患者队列：随机种子固定，到达时刻/分诊等级/分区/床位在脚本里
生成，候诊时长、平均等待、最长等待、占用率全部由队列反算，可互相核对。
医院、患者编号、主诉组合均为虚构演示数据。
"""
import os
import random
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
sys.path.insert(0, str(root / "tmp" / rid / "B01"))
from dslkit import Doc, TextFit  # noqa: E402
import b01kit as K  # noqa: E402

OUT = root / "tmp" / rid / "B01" / "case-04"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------- 队列模型 ----------------
OPEN_T, NOW = 17 * 60 + 30, 21 * 60 + 30          # 观察窗口（分钟）
ZONES = [("抢救室", 6), ("急诊内科", 14), ("急诊外科", 12),
         ("儿科", 8), ("骨科", 6), ("留观", 10)]
ZIDX = {n: i for i, (n, _) in enumerate(ZONES)}
ESI = {1: ("ESI-1 复苏", "#EF4444"), 2: ("ESI-2 危急", "#F97316"),
       3: ("ESI-3 急", "#FBBF24"), 4: ("ESI-4 亚急", "#34D399"),
       5: ("ESI-5 非急", "#22D3EE")}
BAY = {1: [0], 2: [0, 1], 3: [1, 2, 5], 4: [1, 2, 3, 5], 5: [3, 4, 5]}

rng = random.Random(20261009)
PTS = []
for i in range(96):
    t = rng.randint(OPEN_T, NOW - 2)
    r = rng.random()
    esi = (1 if r < .035 else 2 if r < .16 else 3 if r < .52 else
           4 if r < .86 else 5)
    PTS.append(dict(id="A-%03d" % (100 + i), t=t, esi=esi,
                    z=rng.choice(BAY[esi]),
                    st=rng.choices(["候诊", "在诊", "待床", "已处置"],
                                   weights=[26, 34, 14, 26])[0],
                    age=rng.randint(4, 92), sex=rng.choice(["男", "女"]),
                    cc=rng.choice(["胸痛", "腹痛", "高热", "外伤", "气促",
                                   "头晕", "呕吐", "骨折", "过敏", "意识改变"])))
for p in PTS:
    p["wait"] = NOW - p["t"]
QUEUE = sorted([p for p in PTS if p["st"] in ("候诊", "待床")],
               key=lambda p: (-p["esi"], p["t"]))
OCC = {}
for name, cap in ZONES:
    used = len([p for p in PTS if p["z"] == ZIDX[name]
                and p["st"] in ("在诊", "待床")])
    OCC[name] = (min(used, cap), cap)
AVG_WAIT = sum(p["wait"] for p in QUEUE) / len(QUEUE)
LONGEST = max(QUEUE, key=lambda p: p["wait"])
ESI_CNT = {e: len([p for p in QUEUE if p["esi"] == e]) for e in (1, 2, 3, 4, 5)}
ESI_MAXW = {e: max([p["wait"] for p in QUEUE if p["esi"] == e], default=0)
            for e in (1, 2, 3, 4, 5)}
RESUS = OCC["抢救室"]
PENDING = len([p for p in QUEUE if p["st"] == "待床"])
AMBS = [("皖A·3F21", 21 * 60 + 38, "胸痛", 2),
        ("皖A·7C05", 21 * 60 + 52, "车祸多发伤", 1),
        ("皖A·9K17", 22 * 60 + 9, "高热惊厥（儿童）", 2),
        ("皖A·1D48", 22 * 60 + 24, "跌倒髋痛", 4)]


def hhmm(m):
    return "%d:%02d" % (m // 60, m % 60)


def dur(m):
    return "%dh%02dm" % (m // 60, m % 60)


# ---------------- 画布 ----------------
W, H = 2560, 1440
d = Doc(W, H, bg="#080D18", palette={
    "card": "#0E1524", "card2": "#131C2E", "border": "#1E293B",
    "grid": "#18223A", "axis": "#475569", "row": "#111A2B",
    "t0": "#F1F5F9", "t1": "#94A3B8", "t2": "#64748B",
    "cyan": "#22D3EE", "amber": "#FBBF24", "green": "#34D399",
    "red": "#EF4444", "violet": "#A78BFA", "slate": "#64748B", "pink": "#F472B6"})
P = d.P
tf = TextFit()
d.rect(0, 0, W, H, "#080D18")
K.radial_disc(d, 1960, -300, 1250, ["#0E2A3A", "#080D18"], radius="0.55")

# ---------------- 顶部 ----------------
d.pos(0, 0, W, 128, d.box(W, 128, color="#0B1220"))
d.line(0, 128, W, 128, 2, P["border"])
d.label(40, 26, 620, 40, "云州市第一人民医院 · 急诊中心", P["t0"], 34, "BOLD")
d.label(40, 72, 700, 26, "分诊态势屏（虚构演示数据，不含任何真实患者信息）",
        P["t2"], 20)
d.pos(2180, 22, 340, 76, d.box(340, 76, align="CENTER_RIGHT",
                               inner=K.T("21:30", d.font, color=P["t0"],
                                         fontSize=58, fontStyle="BOLD")))
d.label(2120, 96, 400, 22, "夜班 · 距交班 30 分钟", P["t2"], 17, align="END")
KPI = [("在院候诊", "%d 人" % len(QUEUE), P["amber"]),
       ("平均候诊", "%d 分钟" % round(AVG_WAIT), P["cyan"]),
       ("最长等待", "%s（%s）" % (dur(LONGEST["wait"]), LONGEST["id"]), P["red"]),
       ("待床", "%d 人" % PENDING, P["violet"]),
       ("在岗医护", "9 / 14", P["green"])]
kx = 780
for lab, val, col in KPI:
    wd = 250 if lab != "最长等待" else 320
    d.pos(kx, 24, wd, 80, d.box(wd, 80, color="#111C30", radius=12,
                                border="1 SOLID %s" % P["border"]))
    d.rect(kx, 24, 5, 80, col)
    d.label(kx + 22, 34, wd - 34, 22, lab, P["t2"], 17)
    d.label(kx + 22, 58, wd - 34, 34, val, col, 24, "BOLD")
    tf.check("c4-kpi", val, 24, wd - 34, 34)
    kx += wd + 16

# ---------------- 告警条 ----------------
d.pos(40, 146, W - 80, 62, d.box(W - 80, 62, color="#2A1220", radius=12,
                                 border="1 SOLID #EF444466"))
d.rect(40, 146, 6, 62, P["red"])
HOT = max(OCC.items(), key=lambda kv: kv[1][0] / kv[1][1])
HOTW = "满员" if HOT[1][0] >= HOT[1][1] else "接近满员"
alert = ("%s %d/%d %s · %d 名 ESI-1/2 仍在候诊（最久 %s）· 建议启动二级分流，"
         "把 ESI-4/5 转至合作门诊单元（需值班组长确认）"
         % (HOT[0], HOT[1][0], HOT[1][1], HOTW, ESI_CNT[1] + ESI_CNT[2],
            dur(ESI_MAXW[1] or ESI_MAXW[2])))
d.label(70, 146, W - 140, 62, alert, "#FECACA", 26, "BOLD")
tf.check("c4-alert", alert, 26, W - 140, 62)

# ================= 左：分诊等级 + 分区压力 =================
LX, LY, LW = 40, 232, 780
K.card(d, LX, LY, LW, 452, "分诊等级构成（在院候诊 %d 人）" % len(QUEUE),
       "条长＝人数；右侧为该等级中最久已等待")
K.bars_h(d, LX + 20, LY + 104, 150, 300,
         [(ESI[e][0], ESI_CNT[e], max(ESI_CNT.values())) for e in (1, 2, 3, 4, 5)],
         h=44, gap=13, unit=" 人", label_size=20, value_size=21,
         colors=[ESI[e][1] for e in (1, 2, 3, 4, 5)], track="#16203455")
for i, e in enumerate((1, 2, 3, 4, 5)):
    d.label(LX + 590, LY + 104 + i * 57, 170, 44,
            "最久 %s" % dur(ESI_MAXW[e]) if ESI_MAXW[e] else "—",
            P["t1"] if ESI_MAXW[e] < 90 else P["red"], 19, align="END")

K.card(d, LX, LY + 476, LW, 692, "分区压力与床位",
       "每格 1 床：实心＝已占，空心＝可立即收治")
zy = LY + 556
for name, cap in ZONES:
    zp = [p for p in QUEUE if p["z"] == ZIDX[name]]
    used, cap = OCC[name]
    free = cap - used
    st = "满员" if free <= 0 else ("紧张" if free <= 1 else "可收治")
    col = P["red"] if free <= 0 else (P["amber"] if free <= 1 else P["green"])
    d.label(LX + 20, zy, 150, 28, name, P["t0"], 21, "BOLD")
    zline = ("候诊 %d 人 · 最长 %s · 平均 %d min"
             % (len(zp), dur(max([p["wait"] for p in zp], default=0)),
                round(sum(p["wait"] for p in zp) / len(zp)) if zp else 0))
    d.label(LX + 20, zy + 30, 400, 24, zline, P["t1"], 18)
    tf.check("c4-zone", zline, 18, 400, 24)
    d.label(LX + 20, zy + 56, 300, 24, "占用 %d/%d · 空床 %d" % (used, cap, free),
            P["t2"], 18)
    d.chip(LX + 330, zy + 52, 86, 28, st, "#080D18", col, 17)
    cols = min(8, cap)
    K.waffle(d, LX + 452, zy + 4, cols, -(-cap // cols), 30, 6, used,
             col, "#16223A", total=cap)
    zy += 100

# ================= 中：候诊时间轴 =================
MX, MY, MW = 844, 232, 1000
K.card(d, MX, MY, MW, 1136, "候诊时间轴 · 越靠左等待越久",
       "圆点＝一名在院患者，纵向为其分区，横轴为到院时刻；紫环＝已确诊待床")
for i, (lab, col, r) in enumerate([(ESI[e][0], ESI[e][1],
                                    {1: 13, 2: 12, 3: 11, 4: 9, 5: 8}[e])
                                   for e in (1, 2, 3, 4, 5)]):
    lx = MX + 20 + i * 186
    d.pos(lx, MY + 100 - r, r * 2, r * 2, d.box(r * 2, r * 2, color=col, radius=r))
    d.label(lx + r * 2 + 8, MY + 86, 150, 26, lab, P["t1"], 17)
PX, PY = MX + 118, MY + 150
PW_, PH_ = MW - 160, 878
for i in range(9):
    m = OPEN_T + i * 30
    x = PX + PW_ * (m - OPEN_T) / (NOW - OPEN_T)
    d.line(x, PY, x, PY + PH_, 1, P["grid"])
    d.label(x - 34, PY + PH_ + 12, 68, 22, hhmm(m), P["t2"], 17, align="CENTER")
for zi, (name, cap) in enumerate(ZONES):
    yy = PY + PH_ * (zi + 0.5) / len(ZONES)
    d.line(PX, yy, PX + PW_, yy, 1, "#16203455")
    d.label(MX + 20, yy - 13, 92, 26, name, P["t1"], 18, align="END")
    if not any(p["z"] == zi for p in QUEUE):
        d.label(PX + 12, yy - 12, PW_ - 24, 24,
                "当前无候诊患者（空床 %d）" % (OCC[name][1] - OCC[name][0]), P["t2"], 16,
                align="CENTER")
d.line(PX + PW_ - 1, PY - 16, PX + PW_ - 1, PY + PH_ + 6, 3, P["red"])
d.label(PX + PW_ - 96, PY - 46, 94, 24, "NOW 21:30", P["red"], 17, "BOLD",
        align="END")
for p in QUEUE:
    x = PX + PW_ * (p["t"] - OPEN_T) / (NOW - OPEN_T)
    yy = PY + PH_ * (p["z"] + 0.5) / len(ZONES)
    r = {1: 13, 2: 12, 3: 11, 4: 9, 5: 8}[p["esi"]]
    d.pos(x - r, yy - r, r * 2, r * 2, d.box(r * 2, r * 2, color=ESI[p["esi"]][1],
                                             radius=r))
    if p["st"] == "待床":
        d.pos(x - r - 4, yy - r - 4, (r + 4) * 2, (r + 4) * 2,
              d.box((r + 4) * 2, (r + 4) * 2, radius=r + 4,
                    border="2 SOLID %s" % P["violet"]))
placed = {}
for p in sorted(QUEUE, key=lambda q: -q["wait"]):
    if p["wait"] < 200:
        continue
    used = placed.setdefault(p["z"], [])
    x = PX + PW_ * (p["t"] - OPEN_T) / (NOW - OPEN_T)
    if len(used) >= 2 or any(abs(x - u) < 190 for u in used):
        continue
    used.append(x)
    yy = PY + PH_ * (p["z"] + 0.5) / len(ZONES)
    r = {1: 13, 2: 12, 3: 11, 4: 9, 5: 8}[p["esi"]]
    d.pos(x - 79, yy - r - 30, 158, 24,
          d.box(158, 24, color="#0B1428E6", radius=6,
                inner=d.text("%s · %s" % (p["id"], dur(p["wait"])), P["t1"], 15,
                             align="CENTER")))
    d.line(x, yy - r - 6, x, yy - r, 1, "#334155")
d.label(MX + 20, MY + 1082, MW - 40, 24,
        "观察窗口 17:30–21:30，共 96 人次到院；当前在院候诊 %d 人，其中 %d 人等待超过 60 分钟"
        % (len(QUEUE), len([p for p in QUEUE if p["wait"] > 60])), P["t2"], 18)

# ================= 右：救护车 / 主诉 / 优先级 =================
RX, RY, RW = 1868, 232, 652
K.card(d, RX, RY, RW, 404, "救护车在途（4 辆）", "院前通报等级与预计到达")
ay = RY + 112
for plate, eta, note, esi in AMBS:
    d.label(RX + 20, ay, 140, 26, plate, P["t0"], 20, "BOLD")
    d.label(RX + 166, ay, 220, 26, note, P["t1"], 18)
    d.label(RX + RW - 22 - 130, ay, 130, 26, "%s 到" % hhmm(eta), P["cyan"], 19,
            "BOLD", align="END")
    d.rect(RX + 20, ay + 34, 6, 14, ESI[esi][1])
    d.label(RX + 34, ay + 30, 420, 22,
            "%s · 距现在 %d 分钟准备" % (ESI[esi][0], eta - NOW), P["t2"], 16)
    ay += 74

K.card(d, RX, RY + 428, RW, 336, "主诉分布（在院候诊）", "同一患者只计首诊主诉")
ccs = {}
for p in QUEUE:
    ccs[p["cc"]] = ccs.get(p["cc"], 0) + 1
top = sorted(ccs.items(), key=lambda kv: (-kv[1], kv[0]))[:6]
K.bars_h(d, RX + 20, RY + 508, 120, 320,
         [(a, b, top[0][1]) for a, b in top], h=32, gap=9, unit=" 人",
         label_size=19, value_size=19,
         colors=[P["cyan"], P["green"], P["amber"], P["violet"], P["pink"],
                 P["slate"]], track="#16203455")

K.card(d, RX, RY + 788, RW, 348, "当前处置优先级前 5",
       "等级相同则等待久者优先（脱敏编号）")
hy = RY + 868
for p in QUEUE[:5]:
    d.rect(RX + 20, hy, 6, 30, ESI[p["esi"]][1])
    d.label(RX + 36, hy, 96, 28, p["id"], P["t0"], 19, "BOLD")
    d.label(RX + 138, hy, 150, 28, "%s/%d岁" % (p["sex"], p["age"]), P["t1"], 18)
    d.label(RX + 286, hy, 150, 28, p["cc"], P["t1"], 18)
    d.label(RX + RW - 22 - 150, hy, 150, 28, "已候 %d min" % p["wait"],
            P["red"] if p["wait"] > 60 else P["amber"], 19, "BOLD", align="END")
    hy += 44

d.label(40, 1404, W - 80, 24,
        "复现：随机种子 20261009 · 96 人次 · 观察窗口 17:30–21:30；"
        "所有等待/占用数字由同一队列反算，改任一参数整屏同步。", P["t2"], 17)

dsl = d.dsl()
(OUT / "case04.snapshot").write_text(dsl, encoding="utf-8")
print("bytes", len(dsl), "textfit", tf.n, tf.problems)
print("queue", len(QUEUE), "avg", round(AVG_WAIT), "longest", LONGEST["id"],
      LONGEST["wait"], "esi", ESI_CNT, "esi_maxw", ESI_MAXW, "resus", RESUS,
      "pending", PENDING)
print("occ", OCC)
