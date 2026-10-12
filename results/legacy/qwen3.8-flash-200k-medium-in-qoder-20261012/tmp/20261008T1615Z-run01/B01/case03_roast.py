"""B01 case-03 · 精品咖啡烘焙曲线工作台（1440×900，浅色）。

受众：烘焙师；使用时刻：出炉前 30 秒判断这一炉是否偏离目标曲线并决定下一步。
曲线不是手画形状：由「分段线性 RoR 模型」在脚本内积分得到豆温序列，
发展率、转黄时刻、每 30 秒 RoR 条、阶段条宽度全部来自同一模型，可互相核对。
品牌与批次数据为虚构演示。
"""
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
sys.path.insert(0, str(root / "tmp" / rid / "B01"))
from dslkit import Doc, TextFit  # noqa: E402
import b01kit as K  # noqa: E402

OUT = root / "tmp" / rid / "B01" / "case-03"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------- 数据模型 ----------------
T_TP, BT_TP = 90.0, 93.6          # 回转点
BT_FC = 196.0                     # 一爆温度
ROR_TP, ROR_FC = 16.2, 8.0        # ℃/min，线性下降到一爆
ROR_FC_END, ROR_DROP = 5.5, 3.2   # 一爆后 RoR 快速衰减
CHARGE_KG, END_KG = 12.0, 10.30
DEV_TARGET = 0.200                # 目标发展率


def bt_at(t, ror_after_fc=ROR_FC_END):
    """由 RoR 模型积分出豆温。"""
    if t <= T_TP:
        return 172.5 - (172.5 - BT_TP) * (t / T_TP)
    # 一爆时刻：TP→FC 段积分到 BT_FC
    u = 2 * (BT_FC - BT_TP) / (ROR_TP + ROR_FC) * 60.0      # 秒
    t_fc = T_TP + u
    if t <= t_fc:
        dt = (t - T_TP) / 60.0
        r_end = ROR_TP - (ROR_TP - ROR_FC) * (t - T_TP) / u
        return BT_TP + dt * (ROR_TP + r_end) / 2.0
    dt2 = (t - t_fc) / 60.0
    r_end = ror_after_fc - (ror_after_fc - ROR_DROP) * min(1.0, dt2 / 3.0)
    return BT_FC + dt2 * (ror_after_fc + r_end) / 2.0


def t_at_bt(target, ror_after_fc=ROR_FC_END):
    lo, hi = T_TP, 1200.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if bt_at(mid, ror_after_fc) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


T_FC = t_at_bt(BT_FC)
T_DROP = 731.0                                   # 本炉实际出炉时刻
DEV = T_DROP - T_FC
DEV_RATIO = DEV / T_DROP
T_YELLOW = t_at_bt(150.0)
T_TARGET_DROP = T_FC + DEV_TARGET * (T_FC + DEV_TARGET * 0)  # 占位，下面精确求
# 目标发展率 20% ⇒ dev_t / (T_FC + dev_t) = 0.20
DEV_T = DEV_TARGET * T_FC / (1 - DEV_TARGET)
T_TARGET_DROP = T_FC + DEV_T
WEIGHT_LOSS = 1 - END_KG / CHARGE_KG


def mmss(s):
    return "%d:%02d" % (int(s) // 60, int(s) % 60)


# ---------------- 画布 ----------------
W, H = 1440, 900
d = Doc(W, H, bg="#F5F6F8", palette={
    "card": "#FFFFFF", "card2": "#F8FAFC", "border": "#E2E8F0", "grid": "#EDF1F6",
    "axis": "#94A3B8", "row": "#F8FAFC",
    "t0": "#0F172A", "t1": "#475569", "t2": "#94A3B8",
    "cyan": "#0F766E", "amber": "#B45309", "green": "#15803D", "red": "#B91C1C",
    "violet": "#6D28D9", "slate": "#64748B"})
P = d.P
tf = TextFit()

d.rect(0, 0, W, H, "#F5F6F8")

# 顶部
d.pos(0, 0, W, 84, d.box(W, 84, color="#FFFFFF"))
d.line(0, 84, W, 84, 1, P["border"])
d.label(32, 18, 260, 30, "岩屋咖啡 · 烘焙工坊", P["t0"], 24, "BOLD")
d.label(32, 50, 300, 22, "Roast Log 工作台（虚构演示）", P["t2"], 17)
d.pos(330, 20, 1, 44, d.box(1, 44, color=P["border"]))
META = [(356, 90, "批次", "A-231"),
        (462, 300, "豆种", "埃塞俄比亚 古吉 手选 G1"),
        (778, 110, "处理法", "日晒"),
        (900, 130, "投豆", "%.2f kg" % CHARGE_KG),
        (1042, 170, "出炉", "%.2f kg" % END_KG)]
for x, w, k, v in META:
    d.label(x, 20, w, 22, k, P["t2"], 17)
    d.label(x, 42, w, 28, v, P["t0"], 20, "BOLD")
    tf.check("c3-meta", v, 20, w, 28)
d.label(1220, 20, 188, 26, "当前时间", P["t2"], 17, align="END")
d.label(1220, 42, 188, 30, "12:11 · 已出炉", P["red"], 22, "BOLD", align="END")

# ---------------- 主图表 ----------------
GX, GY, GW, GH = 32, 108, 940, 552
d.pos(GX, GY, GW, GH, d.box(GW, GH, color="#FFFFFF", radius=16,
                            border="1 SOLID %s" % P["border"]))
d.label(GX + 24, GY + 16, 500, 28, "豆温曲线 vs 目标曲线", P["t0"], 22, "BOLD")

PX, PY = GX + 76, GY + 84
PW_, PH_ = GW - 116, GH - 132
TMAX = 780.0
BMIN, BMAX = 80.0, 220.0

d.label(GX + 24, GY + 44, 620, 22, "纵轴＝豆温 ℃ · RoR 由分段线性模型积分，1 px ≈ %.2f s / %.3f ℃"
        % ((TMAX) / (GW - 116), (BMAX - BMIN) / (GH - 132)), P["t2"], 16)


def px(t):
    return PX + PW_ * t / TMAX


def py(b):
    return PY + PH_ * (1 - (b - BMIN) / (BMAX - BMIN))


for i in range(8):
    y = PY + PH_ * i / 7
    d.line(PX, y, PX + PW_, y, 1, P["grid"])
    d.label(PX - 62, y - 12, 52, 24, "%.0f" % (BMAX - (BMAX - BMIN) * i / 7),
            P["t2"], 17, align="END")
for i in range(14):
    x = PX + PW_ * i / 13
    d.line(x, PY, x, PY + PH_, 1, P["grid"])
    t = TMAX * i / 13
    d.label(x - 30, PY + PH_ + 8, 60, 22, mmss(t), P["t2"], 16, align="CENTER")


# 目标曲线（虚线）
seg = []
for i in range(0, 53):
    t = T_TARGET_DROP * i / 52
    seg.append((px(t), py(bt_at(t, 6.2) - 1.2)))
for a, b in zip(seg, seg[1:]):
    d.line(a[0], a[1], a[0] + (b[0] - a[0]) * 0.62, a[1] + (b[1] - a[1]) * 0.62,
           3, "#94A3B8")

# 实际曲线
pts = [(px(TMAX * i / 60), py(bt_at(TMAX * i / 60))) for i in range(61)
       if TMAX * i / 60 <= T_DROP]
K.polyline(d, pts, 5, P["amber"])

# 阶段底色
d.rect(PX, py(220), px(T_YELLOW) - PX, py(150) - py(220), "#FEF3C7", radius=0)
d.rect(px(T_YELLOW), py(220), px(T_FC) - px(T_YELLOW), py(196) - py(220),
       "#FFEDD5", radius=0)
d.rect(px(T_FC), py(220), px(T_DROP) - px(T_FC), py(196) - py(220), "#FEE2E2",
       radius=0)

# 关键事件标记
for t, b, lab, col in [(T_YELLOW, 150.0, "转黄 %s / %.1f℃" % (mmss(T_YELLOW), 150.0),
                        P["amber"]),
                       (T_FC, BT_FC, "一爆 %s / %.1f℃" % (mmss(T_FC), BT_FC),
                        P["red"]),
                       (T_DROP, bt_at(T_DROP), "出炉 %s / %.1f℃" %
                        (mmss(T_DROP), bt_at(T_DROP)), P["t0"])]:
    d.line(px(t), py(b) - 0, px(t), PY + PH_, 2, col)
    d.dot(px(t), py(b), 14, col)
    w = 250
    x = min(px(t) + 10, PX + PW_ - w)
    d.label(x, py(b) - 34, w, 26, lab, col, 19, "BOLD")
    tf.check("c3-ev", lab, 19, w, 26)

# 毛玻璃实时读数卡（覆盖曲线，BackdropFilter 真实生效）
K.frosted(d, PX + PW_ - 300, PY + PH_ - 152, 292, 138, radius=14, sigma=18,
          tint="#FFFFFFF0", border="#FFFFFF",
          content=d.col([d.box(268, 6, color=None),
                         d.box(268, 22, align="CENTER_LEFT",
                               inner=K.T("出炉前读数", d.font, color=P["t2"],
                                         fontSize=16)),
                         d.box(268, 34, align="CENTER_LEFT",
                               inner=K.T("%.1f ℃" % bt_at(T_DROP), d.font,
                                         color=P["t0"], fontSize=27,
                                         fontStyle="BOLD")),
                         d.box(268, 24, align="CENTER_LEFT",
                               inner=K.T("RoR %.1f ℃/min" % (bt_at(T_DROP) - bt_at(T_DROP - 60)),
                                         d.font, color=P["amber"], fontSize=19,
                                         fontStyle="BOLD")),
                         d.box(268, 22, align="CENTER_LEFT",
                               inner=K.T("发展 %s · %.1f%%（目标 %.1f%%）" % (mmss(DEV), DEV_RATIO * 100,
                                                           DEV_TARGET * 100), d.font,
                                         color=P["red"], fontSize=16))]))

# 图例
lg = [("本炉实际", P["amber"], "line"), ("目标曲线", "#94A3B8", "dash"),
      ("一爆后发展区", "#FEE2E2", "box")]
lg_w = sum(30 + tf.w(t_, 18) + 40 for t_, _, _ in lg) - 40
lx = GX + GW - 24 - lg_w
LY = GY + 24
for txt_, col, kind in lg:
    if kind == "box":
        d.rect(lx, LY, 22, 14, col, radius=3)
    else:
        d.line(lx, LY + 7, lx + 22, LY + 7, 4, col)
    d.label(lx + 30, LY - 5, 190, 24, txt_, P["t1"], 18)
    lx += 30 + tf.w(txt_, 18) + 40

# ---------------- 右侧指标 ----------------
RX, RY, RW = 996, 108, 412
y = RY
metrics = [
    ("发展率", "%.1f%%" % (DEV_RATIO * 100), "目标 20.0%% · 差 %.1f pt" %
     ((DEV_TARGET - DEV_RATIO) * 100), P["red"]),
    ("发展时间", mmss(DEV), "目标 %s · 提前 %d 秒出炉" % (mmss(DEV_T), T_TARGET_DROP - T_DROP),
     P["amber"]),
    ("总时长", mmss(T_DROP), "回转点 %s / %.1f℃" % (mmss(T_TP), BT_TP), P["t0"]),
    ("失重率", "%.1f%%" % (WEIGHT_LOSS * 100), "投豆 %.2f kg → 出炉 %.2f kg" %
     (CHARGE_KG, END_KG), P["t0"]),
]
for i, (k, v, sub, col) in enumerate(metrics):
    d.pos(RX, y, RW, 92, d.box(RW, 92, color="#FFFFFF", radius=14,
                               border="1 SOLID %s" % P["border"]))
    d.rect(RX, y, 5, 92, col)
    d.label(RX + 22, y + 12, 200, 24, k, P["t2"], 18)
    d.label(RX + 22, y + 36, 220, 36, v, col, 28, "BOLD")
    d.label(RX + 22, y + 64, RW - 44, 22, sub, P["t1"], 17)
    tf.check("c3-m%d" % i, sub, 17, RW - 44, 22)
    y += 100

# 火力/风门 SWEEP 仪表
d.pos(RX, y, RW, 168, d.box(RW, 168, color="#FFFFFF", radius=14,
                            border="1 SOLID %s" % P["border"]))
d.label(RX + 22, y + 14, 240, 24, "火力 / 风门（出炉瞬间）", P["t0"], 19, "BOLD")
d.label(RX + 22, y + 40, RW - 44, 20, "一爆后火力阶梯下调 3 档，风门保持", P["t2"], 15)
for j, (lab, val, col) in enumerate([("火力", 62, P["amber"]), ("风门", 45, P["cyan"])]):
    yy = y + 74 + j * 46
    d.label(RX + 22, yy - 4, 56, 24, lab, P["t1"], 18, "BOLD")
    d.rect(RX + 88, yy, RW - 88 - 78, 16, "#E2E8F0", radius=8)
    d.rect(RX + 88, yy, (RW - 88 - 78) * val / 100.0, 16, col, radius=8)
    for q in (25, 50, 75):
        d.rect(RX + 88 + (RW - 88 - 78) * q / 100.0, yy - 3, 1, 22, "#CBD5E1")
    d.label(RX + RW - 72, yy - 6, 50, 28, "%d%%" % val, P["t0"], 20, "BOLD",
            align="END")
d.label(RX + 88, y + 142, RW - 88 - 78, 18, "0 · 1/4 · 1/2 · 3/4 · 满档", P["t2"], 13)
y += 176

# ---------------- 底部：阶段条 + 决策 ----------------
BY = 684
d.pos(32, BY, W - 64, 184, d.box(W - 64, 184, color="#FFFFFF", radius=16,
                                 border="1 SOLID %s" % P["border"]))
d.label(56, BY + 16, 400, 26, "阶段构成（宽度＝时长占比）", P["t0"], 20, "BOLD")
phases = [("预热至回转", T_TP, "#CBD5E1"), ("脱水段", T_YELLOW - T_TP, "#FDE68A"),
          ("美拉德段", T_FC - T_YELLOW, "#FDBA74"), ("发展段", DEV, "#FCA5A5")]
bx = 56
bw_total = 560
for name, dur, col in phases:
    w = bw_total * dur / T_DROP
    d.rect(bx, BY + 52, w, 34, col, radius=6)
    if w > 64:
        d.label(bx + 8, BY + 59, w - 12, 20, "%.1f%%" % (100 * dur / T_DROP),
                "#334155", 14, "BOLD")
    bx += w
for i, (name, dur, col) in enumerate(phases):
    lx = 56 + i * 140
    d.rect(lx, BY + 101, 12, 12, col, radius=3)
    d.label(lx + 20, BY + 94, 116, 24, name, P["t1"], 16, "BOLD")
    d.label(lx + 20, BY + 116, 116, 20, "%s · %.1f%%" % (mmss(dur), 100 * dur / T_DROP),
            P["t2"], 15)
    tf.check("c3-pl%d" % i, name, 16, 116, 24)

d.line(648, BY + 18, 648, BY + 164, 1, P["border"])
d.label(672, BY + 16, 260, 24, "每分钟 RoR（℃/min）", P["t0"], 19, "BOLD")
ror = []
for m in range(12):
    t0 = T_TP + m * 60
    if t0 + 60 > T_DROP:
        break
    ror.append((m + 1, (bt_at(t0 + 60) - bt_at(t0))))
bx = 672
bw = (1000 - bx) / len(ror)
for i, (m, v) in enumerate(ror):
    h = 74.0 * min(1.0, v / 17.0)
    d.rect(bx + i * bw + 3, BY + 132 - h, bw - 8, h,
           P["amber"] if v > 8 else P["red"], radius=3)
    d.label(bx + i * bw - 1, BY + 136, bw + 2, 18, "%d" % m, P["t2"], 14,
            align="CENTER")
d.label(bx, BY + 156, 320, 20,
        "%.1f → %.1f 逐分钟衰减，末端低于 5 需警惕停滞" % (ror[0][1], ror[-1][1]),
        P["t2"], 14)

d.pos(W - 64 - 356, BY + 14, 336, 156,
      d.box(336, 156, color="#FEF2F2", radius=14, border="1 SOLID #B91C1C55"))
d.label(W - 64 - 336, BY + 26, 300, 26, "本炉结论", P["red"], 20, "BOLD")
d.label(W - 64 - 336, BY + 54, 300, 110,
        "发展率 %.1f%% 低于目标 %.1f%%，比目标曲线早 %.0f 秒出炉；"
        "下一炉保持同一 RoR 斜率，一爆后 %s 再出，或提前 30 秒降火力 5%%。"
        % (DEV_RATIO * 100, DEV_TARGET * 100, T_TARGET_DROP - T_DROP, mmss(DEV_T)), P["t1"], 17)
tf.check("c3-concl", "发展率 %.1f%% 低于目标 %.1f%%，比目标曲线早 %.0f 秒出炉；" % (DEV_RATIO * 100, DEV_TARGET * 100, T_TARGET_DROP - T_DROP), 17, 300, 90, lines=4)

dsl = d.dsl()
(OUT / "case03.snapshot").write_text(dsl, encoding="utf-8")
print("bytes", len(dsl))
print("T_FC=%.0f (%s) T_YELLOW=%.0f (%s) T_DROP=%.0f DEV=%.0f ratio=%.3f target_drop=%.0f"
      % (T_FC, mmss(T_FC), T_YELLOW, mmss(T_YELLOW), T_DROP, DEV, DEV_RATIO,
         T_TARGET_DROP))
print("ror", [(m, round(v, 1)) for m, v in ror])
print("textfit", tf.n, tf.problems)
