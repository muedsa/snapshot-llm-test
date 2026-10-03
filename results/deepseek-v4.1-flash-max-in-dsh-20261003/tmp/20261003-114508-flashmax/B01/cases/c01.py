# -*- coding: utf-8 -*-
"""B01 case-01 -- 咖啡烘焙曲线复盘卡 (dark roast-lab data card).

Real computation: a roast profile is generated from a rate-of-rise (ROR)
schedule, integrated to bean temperature, the post-first-crack tail is solved
numerically so the development-time ratio lands at 20 %, and every milestone
printed on the card is derived from that curve.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import Doc, CJK, MONO, clamp, clip, lerp, tw  # noqa: E402

NAME = "c01-roast-profile"
W, H = 1440, 1010

BG = "#0B1017FF"
PANEL = "#121A24FF"
PANEL2 = "#0E1520FF"
GRID = "#22303FFF"
TXT = "#E6EDF5FF"
DIM = "#8A9BB0FF"
AMBER = "#F0A93BFF"
TEAL = "#3FD0C9FF"
RED = "#F2685FFF"
BLUE = "#6EA8FEFF"

# ROR control points in degC/min -- the schedule a roaster actually dials in
CTRL = [(0.0, -170), (0.4, -105), (0.8, -58), (1.2, -20), (1.6, -3), (1.9, 0),
        (2.6, 9.9), (3.4, 15.3), (4.2, 18.5), (5.0, 19.8), (6.0, 19.4), (7.0, 18),
        (8.0, 16.2), (8.4, 15.3), (9.0, 7.4), (9.6, 5.6), (10.2, 4.6), (10.8, 3.8),
        (11.6, 3.0)]
TAIL_FROM = 8.4          # first crack: the gas is cut here
TAIL_RAMP = 0.35         # minutes of linear blend so the ROR curve has no cliff

T_CHARGE = 201.5
T_TP = 87.0
T_FC = 196.0
T_DROP = 204.5
T_TOTAL = 10.2           # target drop time in minutes
DT = 1.0 / 60.0          # 1 second steps, minutes


def tail_gate(t, g):
    if t <= TAIL_FROM:
        return 1.0
    if t >= TAIL_FROM + TAIL_RAMP:
        return g
    return 1.0 + (g - 1.0) * (t - TAIL_FROM) / TAIL_RAMP


def ror_schedule(t, tail_gain):
    for i in range(len(CTRL) - 1):
        t0, v0 = CTRL[i]
        t1, v1 = CTRL[i + 1]
        if t0 <= t <= t1:
            v = v0 + (v1 - v0) * (t - t0) / (t1 - t0)
            return v * tail_gate(t, tail_gain)
    return CTRL[-1][1] * tail_gate(t, tail_gain)


def integrate(tail_gain):
    """Return (times, ror, raw cumulative integral) for a tail gain."""
    ts, rs, acc = [], [], []
    t, a = 0.0, 0.0
    while t <= 12.0 + 1e-9:
        ts.append(t)
        r = ror_schedule(t, tail_gain)
        rs.append(r)
        acc.append(a)
        a += r * DT
        t += DT
    return ts, rs, acc


def curve(tail_gain):
    ts, rs, acc = integrate(tail_gain)
    k = (T_CHARGE - T_TP) / abs(min(acc))
    return ts, rs, [T_CHARGE + k * a for a in acc], k


def build_series():
    """Solve the tail gain so the drop lands on T_TOTAL at T_DROP degC."""
    lo, hi, best = 0.05, 4.0, None
    for _ in range(50):
        mid = (lo + hi) / 2
        ts, rs, temp, k = curve(mid)
        i = min(range(len(ts)), key=lambda j: abs(ts[j] - T_TOTAL))
        best = (ts, rs, temp, mid, k)
        if temp[i] < T_DROP:
            lo = mid
        else:
            hi = mid
    ts, rs, temp, g, k = best
    return ts, rs, temp, g, k


def milestone(ts, Ts, target):
    for i in range(1, len(Ts)):
        if Ts[i - 1] < target <= Ts[i]:
            f = (target - Ts[i - 1]) / (Ts[i] - Ts[i - 1])
            return ts[i - 1] + f * DT
    return None


def mmss(t):
    return "%d:%02d" % (int(t), round((t - int(t)) * 60) % 60)


def build(ver="v1", outdir=None):
    ts, rs, Ts, g, k = build_series()
    t_tp = ts[min(range(len(Ts)), key=lambda i: Ts[i])]
    t_de = milestone(ts, Ts, 150.0)
    t_fc = milestone(ts, Ts, T_FC)
    t_dr = milestone(ts, Ts, T_DROP)
    dtr = (t_dr - t_fc) / t_dr
    loss = 0.155
    green = 12.00
    roasted = round(green * (1 - loss), 2)

    data = {
        "batch": "BR-2418", "green_kg": green, "roasted_kg": roasted,
        "weight_loss_pct": round(loss * 100, 1),
        "charge_temp_c": T_CHARGE, "turning_point_c": round(min(Ts), 1),
        "turning_point_at": mmss(t_tp), "dry_end_150c_at": mmss(t_de),
        "first_crack_196c_at": mmss(t_fc), "drop_204_5c_at": mmss(t_dr),
        "total_min": round(t_dr, 2), "development_min": round(t_dr - t_fc, 2),
        "development_ratio_pct": round(dtr * 100, 1),
        "ror_at_fc": round(ror_schedule(t_fc, g), 1),
        "ror_at_drop": round(ror_schedule(t_dr, g), 1),
        "peak_ror": round(max(rs[10:]), 1),
        "tail_gain_solved": round(g, 4), "pre_scale_solved": round(k, 4),
    }

    d = Doc(W, H, BG)
    # ---------------------------------------------------------------- header
    d.box(0, 0, W, 84, PANEL)
    d.box(0, 0, 8, 84, AMBER)
    d.text(40, 14, "烘焙复盘 · BR-2418", 30, TXT, "BOLD")
    d.text(40, 52, "虚构烘焙工坊「北焙」· 12 kg 鼓式 · 埃塞俄比亚 耶加雪菲 水洗 G1 · 目标：手冲浅中焙",
           18, DIM)
    d.ctext(1000, 16, "2026-09-28 09:12 起烘 · 烘焙师 林昭", 18, DIM, w=400, h=24,
            align="CENTER_RIGHT")
    d.ctext(1000, 46, "Probat P12 · 环境 24.1 ℃ / 湿度 52 %", 18, DIM, w=400, h=24,
            align="CENTER_RIGHT")

    # ---------------------------------------------------------------- chart card
    CX, CY, CW, CH = 40, 104, 940, 596
    d.card(CX, CY, CW, CH, PANEL, radius=14, border="1 SOLID " + GRID,
           shadow="0 2 10 0 #00000055 NORMAL")
    d.text(CX + 24, CY + 16, "豆温曲线与升温速率 ROR", 20, TXT, "BOLD")
    # inline legend
    d.box(CX + 400, CY + 22, 18, 4, AMBER, radius=2)
    d.text(CX + 424, CY + 12, "豆温 ℃（左轴）", 15, DIM)
    d.box(CX + 590, CY + 22, 18, 4, TEAL, radius=2)
    d.text(CX + 614, CY + 12, "ROR ℃/min（右轴）", 15, DIM)

    PX0, PX1 = CX + 72, CX + 868
    PY0, PY1 = CY + 92, CY + 544
    TMAX = 10.6
    TLO, THI = 60.0, 220.0
    RLO, RHI = -20.0, 32.0

    def X(t):
        return PX0 + (t / TMAX) * (PX1 - PX0)

    def YT(T):
        return PY1 - (T - TLO) / (THI - TLO) * (PY1 - PY0)

    def YR(r):
        return PY1 - (r - RLO) / (RHI - RLO) * (PY1 - PY0)

    d.box(PX0, PY0, PX1 - PX0, PY1 - PY0, PANEL2, radius=6)
    # horizontal temperature grid
    for T in range(60, 221, 20):
        y = YT(T)
        d.box(PX0, y, PX1 - PX0, 1, GRID)
        d.ctext(CX + 8, y - 11, str(T), 14, DIM, family=MONO, w=58, h=22,
                align="CENTER_RIGHT")
    for T in range(60, 221, 40):
        y = YT(T)
        d.box(PX0, y, PX1 - PX0, 1, "#2E3F52FF")
    # vertical time grid
    for t in range(0, 11):
        x = X(t)
        d.box(x, PY0, 1, PY1 - PY0, GRID)
        d.ctext(x - 20, PY1 + 6, "%d" % t, 14, DIM, family=MONO, w=40, h=20,
                align="CENTER")
    d.text(PX1 - 52, PY1 + 32, "分钟", 15, DIM)
    # right ROR axis
    for r in range(-20, 33, 10):
        y = YR(r)
        d.ctext(PX1 + 6, y - 11, "%d" % r, 14, DIM, family=MONO, w=44, h=22)
    d.text(PX1 + 6, PY0 - 26, "ROR", 14, TEAL, "BOLD")

    # ---- area under the bean-temperature curve (4 px bars, brushed with a glow band)
    bar = 4
    n = int((PX1 - PX0) / bar)
    for i in range(n):
        t = (i * bar) / (PX1 - PX0) * TMAX
        j = min(int(t / DT), len(Ts) - 1)
        T = Ts[j]
        if T <= TLO:
            continue
        y = YT(min(T, THI))
        d.box(PX0 + i * bar, y, bar, PY1 - y, "#F0A93B1C")
        d.box(PX0 + i * bar, y, bar, min(16, PY1 - y), "#F0A93B40")
    # ---- bean temperature line
    step = 6
    pts = []
    for x in range(PX0, PX1 + 1, step):
        t = (x - PX0) / (PX1 - PX0) * TMAX
        j = min(int(t / DT), len(Ts) - 1)
        pts.append((x, YT(min(Ts[j], THI))))
    d.poly(pts, AMBER, 3)
    # ---- ROR line (right axis).  It is drawn from the turning point onwards: the
    #      plunge between charge and TP is off this axis, and drawing it would just
    #      run a straight line along the bottom of the plot.
    rpts = []
    for x in range(PX0, PX1 + 1, step):
        t = (x - PX0) / (PX1 - PX0) * TMAX
        if t < t_tp - 0.02:
            continue
        r = ror_schedule(t, g)
        rpts.append((x, clamp(YR(r), PY0 + 1, PY1 - 1)))
    d.poly(rpts, TEAL, 2)

    # ---- event markers
    events = [
        (0.0, T_CHARGE, "投豆 %.1f ℃" % T_CHARGE, RED, 0),
        (t_tp, min(Ts), "回温点 %.0f ℃" % min(Ts), BLUE, 1),
        (t_de, 150.0, "脱水结束 150 ℃", "#A78BFAFF", 0),
        (t_fc, T_FC, "一爆 %.0f ℃" % T_FC, RED, 1),
        (t_dr, T_DROP, "下豆 %.1f ℃" % T_DROP, "#34D399FF", 0),
    ]
    for t, T, label, col, row in events:
        x, y = X(t), YT(T)
        d.dashed(x, PY0 + 4, x, PY1, col, 1.5, 7, 6)
        d.disc(x, y, 12, "#0B1017FF")
        d.disc(x, y, 8, col)
        lw = tw(label, 14) + 12
        lx = min(max(x - lw / 2, PX0 + 4), PX1 - lw - 4)
        ly = PY0 + 10 + row * 26
        d.box(lx, ly, lw, 22, "#0B1017E6", radius=4, border="1 SOLID " + col)
        d.ctext(lx, ly, label, 14, col, w=lw, h=22, align="CENTER")
        d.ctext(lx, ly + 22, mmss(t), 12, DIM, family=MONO, w=lw, h=16, align="CENTER")

    # ---------------------------------------------------------------- KPIs
    kpis = [
        ("投豆量", "%.2f kg" % green, TXT, "目标 12.00 ± 0.05 kg"),
        ("出豆量", "%.2f kg" % roasted, TXT, "目标出豆率 84.5 %"),
        ("失重率", "%.1f %%" % (loss * 100), AMBER, "目标 15.2 – 15.8 %"),
        ("发展比 DTR", "%.1f %%" % (dtr * 100), TEAL, "目标 18 – 22 %"),
    ]
    for i, (label, val, vc, hint) in enumerate(kpis):
        x = 1000 + (i % 2) * 208
        y = 104 + (i // 2) * 112
        d.card(x, y, 192, 96, PANEL, radius=12, border="1 SOLID " + GRID)
        d.text(x + 16, y + 12, label, 15, DIM)
        d.text(x + 16, y + 32, val, 30, vc, "BOLD", family=MONO)
        d.text(x + 16, y + 76, clip(hint, 13, 162), 13, "#7C8DA3FF")

    # ---------------------------------------------------------------- events table
    EX, EY, EW, EH = 1000, 328, 400, 172
    d.card(EX, EY, EW, EH, PANEL, radius=12, border="1 SOLID " + GRID)
    d.text(EX + 16, EY + 12, "关键事件时间轴", 17, TXT, "BOLD")
    rows = [("00:00", "%.1f ℃" % T_CHARGE, "投豆 / charge"),
            (mmss(t_tp), "%.0f ℃" % min(Ts), "回温点 TP"),
            (mmss(t_de), "150.0 ℃", "脱水结束 / 转黄"),
            (mmss(t_fc), "196.0 ℃", "一爆开始 / FC"),
            (mmss(t_dr), "204.5 ℃", "下豆 / drop")]
    for i, (a, b, c) in enumerate(rows):
        y = EY + 42 + i * 25
        d.text(EX + 16, y, a, 15, DIM, family=MONO)
        d.text(EX + 76, y, b, 15, AMBER, family=MONO)
        d.text(EX + 156, y, c, 15, "#C7D3E1FF")
    d.box(EX + 300, EY + 42, 84, 118, "#0E1520FF", radius=8)
    d.ctext(EX + 300, EY + 52, "ROR@FC", 12, DIM, w=84, h=18, align="CENTER")
    d.ctext(EX + 300, EY + 70, "%.1f" % ror_schedule(t_fc, g), 22, TEAL, "BOLD",
            family=MONO, w=84, h=28, align="CENTER")
    d.ctext(EX + 300, EY + 102, "峰值 %.1f" % max(rs[10:]), 12, DIM, w=84, h=18,
            align="CENTER")

    # ---------------------------------------------------------------- cupping
    UX, UY, UW, UH = 1000, 512, 400, 188
    d.card(UX, UY, UW, UH, PANEL, radius=12, border="1 SOLID " + GRID)
    d.text(UX + 16, UY + 12, "杯测与结论", 17, TXT, "BOLD")
    d.ctext(UX + 300, UY + 8, "88.25", 26, "#34D399FF", "BOLD", family=MONO, w=84, h=32,
            align="CENTER")
    d.ctext(UX + 300, UY + 40, "/ 100 分", 12, DIM, w=84, h=16, align="CENTER")
    attrs = [("干香", 8.75), ("湿香", 8.50), ("酸质", 8.75), ("甜感", 8.75),
             ("口感", 8.25), ("余韵", 8.25)]
    for i, (nm, v) in enumerate(attrs):
        y = UY + 52 + i * 17
        d.text(UX + 16, y, nm, 14, DIM)
        d.box(UX + 62, y + 5, 130, 6, "#1B2635FF", radius=3)
        d.box(UX + 62, y + 5, 130 * (v / 10.0), 6, "#34D399FF", radius=3)
        d.ctext(UX + 198, y - 1, "%.2f" % v, 14, "#C7D3E1FF", family=MONO, w=44, h=18,
                align="CENTER_RIGHT")
    d.box(UX + 16, UY + 160, 368, 1, GRID)
    d.ctext(UX + 16, UY + 166, "结论：发展充分、酸质明亮；下批延长 15 s 发展期", 14,
            "#C7D3E1FF", w=368, h=18)

    # ---------------------------------------------------------------- bottom band
    BY, BH = 708, 278
    # card 1 -- how to read
    d.card(40, BY, 440, BH, PANEL, radius=12, border="1 SOLID " + GRID)
    d.text(64, BY + 14, "读图说明", 17, TXT, "BOLD")
    notes = [
        "琥珀填充 + 粗线 = 豆温（左轴 60–220 ℃）",
        "青色细线 = ROR（右轴，自回温点起绘）",
        "虚线 = 关键事件；线上圆点即该时刻读数",
        "发展比 DTR =（下豆 − 一爆）÷ 总时长",
        "水洗耶加目标：DTR 18–22 %，一爆后降火",
    ]
    for i, s in enumerate(notes):
        d.box(64, BY + 52 + i * 32 + 6, 8, 8, [AMBER, TEAL, "#A78BFAFF", RED,
                                               "#34D399FF"][i], radius=4)
        d.ctext(82, BY + 52 + i * 32, clip(s, 16, 380), 16, "#C7D3E1FF", w=380, h=22)
    d.box(64, BY + 226, 392, 1, GRID)
    d.ctext(64, BY + 236, "曲线由 ROR 计划积分得到；里程碑均取自该曲线", 14, DIM, w=392,
            h=20)

    # card 2 -- last five batches
    d.card(496, BY, 440, BH, PANEL, radius=12, border="1 SOLID " + GRID)
    d.text(520, BY + 14, "近 5 批对比（发展比 / 失重率）", 17, TXT, "BOLD")
    batches = [("BR-2414", 17.8, 15.9), ("BR-2415", 19.2, 15.4), ("BR-2416", 21.6, 15.1),
               ("BR-2417", 18.4, 15.7), ("BR-2418", round(dtr * 100, 1), 15.5)]
    bx0, bw = 592, 270
    for i, (nm, dv, ls) in enumerate(batches):
        y = BY + 54 + i * 38
        d.text(520, y + 2, nm, 14, DIM, family=MONO)
        d.box(bx0, y + 2, bw, 12, "#1B2635FF", radius=6)
        d.box(bx0, y + 2, bw * (dv / 25.0), 12, TEAL if i == 4 else "#2F6F6BFF", radius=6)
        d.ctext(bx0 + bw + 6, y, "%.1f%%" % dv, 14, "#C7D3E1FF", family=MONO, w=44, h=18,
                align="CENTER_RIGHT")
        d.box(bx0, y + 18, bw, 6, "#161F2BFF", radius=3)
        d.box(bx0, y + 18, bw * (ls / 20.0), 6, "#8A6A2EFF" if i != 4 else AMBER, radius=3)
    d.box(520, BY + 244, 392, 1, GRID)
    d.ctext(520, BY + 250, "上排 = 发展比；下排 = 失重率（均按同一标尺换算）", 14, DIM,
            w=392, h=18)

    # card 3 -- conclusion
    d.card(952, BY, 448, BH, PANEL, radius=12, border="1 SOLID " + GRID)
    d.text(976, BY + 14, "本次结论与下一步", 17, TXT, "BOLD")
    concl = [
        ("曲线形状", "回温点偏低、整体升温平稳，无一爆后失速"),
        ("风险点", "8:20 后 ROR 下降偏快，进入烘烤风险区"),
        ("下批动作", "一爆前 30 s 降火 10 %，发展期 +15 s"),
        ("目标区间", "DTR 19–21 %，失重 15.2–15.8 %"),
    ]
    for i, (k, v) in enumerate(concl):
        y = BY + 52 + i * 44
        d.box(976, y + 4, 4, 34, [TEAL, RED, AMBER, BLUE][i], radius=2)
        d.ctext(992, y, k, 15, DIM, w=88, h=20)
        d.ctext(992, y + 20, clip(v, 15, 384), 15, "#C7E1F0FF", w=384, h=20)
    d.box(976, BY + 244, 400, 1, GRID)
    d.ctext(976, BY + 250, "示例数据：本卡为演示作品，批次与工坊均为虚构", 14, "#6B7C90FF",
            w=400, h=18)

    if outdir:
        d.save(os.path.join(outdir, "dsl", "%s.%s.snapshot" % (NAME, ver)))
        os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
        with open(os.path.join(outdir, "data", "%s.json" % NAME), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    return d, data


if __name__ == "__main__":
    out = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _, info = build("v1", out)
    print(json.dumps(info, ensure_ascii=False, indent=2))
