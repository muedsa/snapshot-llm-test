# -*- coding: utf-8 -*-
"""case-01 · GRIDNIGHT · 凌晨的城市电网调度台 (1920x1080).

Brief: a control-room wall display for the on-duty operator. The operator is
reading, at a glance, four things at once - total load against the night's
frozen forecast envelope, system frequency against its deadband, how much of
each region and intertie is already committed, and what happened at 02:14.
Everything is dark because the room is dark; only out-of-band information is
allowed to be warm.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run  # noqa: E402
import atelier as A  # noqa: E402
import dsllib as D  # noqa: E402

tw = A.tw

run.fresh()
CASE = "case-01"
W, H = 1920, 1080

# ------------------------------------------------------------------ palette
BG = "#070C18FF"
PANEL = "#0E1526FF"
LINE = "#1E2A44FF"
GRID = "#182238FF"
INK = "#E8F0FFFF"
MUTED = "#8296B4FF"
FAINT = "#5A6A88FF"
CYAN = "#38E1D0FF"
CYAN_D = "#0E3F44FF"
AMBER = "#FFB454FF"
AMBER_D = "#40300FFF"
RED = "#FF5C6CFF"
GREEN = "#5BE49BFF"
VIOLET = "#9B9CFFFF"

M, G = 48, 24
HEAD_H = 108
KPI_Y, KPI_H = 132, 124
MAIN_Y = 284
EVENT_Y, EVENT_H = 924, 92

# ------------------------------------------------------------------- content
load = [   # GW, sampled at every :30
    41.8, 40.9, 40.1, 39.6, 39.9, 41.2, 43.8, 47.1, 50.6, 53.4, 55.1, 55.8,
    55.0, 54.1, 54.6, 56.3, 59.1, 62.4, 66.2, 68.0, 67.1, 63.8, 58.9, 52.4,
]
f_hi = [h + (1.6 if 5 <= i <= 11 else (2.4 if 16 <= i <= 22 else 1.1))
        for i, h in enumerate(load)]
f_lo = [h - (2.9 if 5 <= i <= 11 else (3.4 if 16 <= i <= 22 else 2.2))
        for i, h in enumerate(load)]

AREAS = [
    ("京津冀", 46.2, 0.88, "normal"),
    ("冀北", 21.4, 0.94, "tight"),
    ("山东", 63.9, 0.79, "normal"),
    ("华中", 41.7, 0.86, "normal"),
    ("东北", 28.5, 0.62, "normal"),
    ("西北", 34.1, 0.71, "normal"),
]
TIE = [
    ("银东直流 800kV", 3120, "送华北"),
    ("晋北交流 500kV", 1840, "送华北"),
    ("东北直流 500kV", 1180, "送华北"),
    ("华中交联 500kV", 940, "送华东"),
    ("华东交联 500kV", -1260, "受入"),
]
EVENTS = [
    (2.23, "02:14", "冀北 4 号主变过负荷告警", "N-1 降载 640MW · 用时 12min", "amber"),
    (3.03, "03:02", "银东直流通道复归", "通道可用率恢复 100%", "green"),
    (3.67, "03:40", "负荷越预报上沿", "+1.8GW · 转事故拉路预案", "red"),
    (4.33, "04:20", "风电出力回升", "+1.8GW · 弃风率 0%", "cyan"),
]
yest = [   # GW, same clock yesterday - the operator's reference line
    39.4, 38.8, 38.2, 37.9, 38.3, 39.6, 42.3, 45.9, 49.2, 51.6, 52.8, 53.1,
    52.4, 51.6, 52.2, 54.1, 57.2, 60.4, 63.9, 65.6, 64.4, 60.9, 56.2, 50.1,
]

kids = []

# ------------------------------------------------------------------- header
kids.append(D.box(0, 0, W, HEAD_H, color=PANEL))
kids.append(D.hline(0, W, HEAD_H - 1, LINE, 1.4))
kids.append(A.label(M, 20, "GRIDNIGHT", size=14, color=CYAN, ls=4.0,
                    font=A.BLACK))
kids.append(A.one_line(M, 42, "华北电网 · 区域调度主站实时画面", size=26,
                       color=INK, font=A.SEMI, pad=20))
x = M + 430
for txt, fill, fg in (("实时", CYAN_D, CYAN), ("AGC 已投入", CYAN_D, CYAN),
                      ("计划值 01:00 冻结", "#1B2740FF", MUTED),
                      ("数据延迟 1.2s", "#1B2740FF", FAINT)):
    ck, cwd = A.chip(x, 62, txt, fill=fill, fg=fg, size=14, h=30)
    kids += ck
    x += cwd + 10
kids.append(A.one_line(W - M, 30, "03:52:41", size=24, color=INK, font=A.MONO,
                       pad=10, anchor="RIGHT"))
kids.append(A.one_line(W - M, 64, "LOCAL · 2026-07-19", size=14, color=FAINT,
                       font=A.SEMI, pad=10, anchor="RIGHT", ls=0.8))

# --------------------------------------------------------------- KPI ribbon
kw = (W - 2 * M - 4 * 20) / 5.0
KPIS = [
    ("全网负荷", "68.0", "GW", "较同时刻昨日 +4.2GW", CYAN, 0.62),
    ("系统频率", "50.006", "Hz", "死区 ±0.05Hz · 未越限", GREEN, 0.12),
    ("旋转备用", "4280", "MW", "占最大负荷 6.3% · 达标", GREEN, 0.63),
    ("跨区受入", "1260", "MW", "华东通道满档运行", AMBER, 0.88),
    ("联络线重载", "2", "条", "冀北 4 号主变 N-1 关注", AMBER, 0.55),
]
for i, (cap, val, unit, sub, col, fr) in enumerate(KPIS):
    x = M + i * (kw + 20)
    kids.append(A.plate(x, KPI_Y, kw, KPI_H, fill=PANEL, radius=12, line=LINE))
    kids.append(A.label(x + 20, KPI_Y + 16, cap, size=12, color=FAINT, ls=2.2))
    vw = tw(val, 42)
    kids.append(A.one_line(x + 20, KPI_Y + 34, val, size=42, color=INK,
                           font=A.BLACK, pad=8))
    kids.append(A.one_line(x + 20 + vw + 10, KPI_Y + 56, unit, size=17,
                           color=col, pad=8))
    kids.append(A.one_line(x + 20, KPI_Y + 84, sub, size=13, color=MUTED, pad=8))
    kids += A.bar(x + 20, KPI_Y + 108, kw - 40, 4, fr, col, track=GRID, radius=2)

# --------------------------------------------------------------- main chart
CX, CW = M, 1180
MAIN_H = EVENT_Y - 28 - MAIN_Y
kids.append(A.plate(CX, MAIN_Y, CW, MAIN_H, fill=PANEL, radius=14, line=LINE))
kids.append(A.label(CX + 24, MAIN_Y + 22, "全网负荷 / GW", size=13, color=FAINT,
                    ls=2.2))
kids.append(A.one_line(CX + 24, MAIN_Y + 42, "过去 24 小时实测 vs 夜间预报包络",
                       size=20, color=INK, font=A.SEMI, pad=20))
LEG = [("实测", CYAN_D, CYAN), ("昨日同期", "#16202EFF", MUTED),
       ("预报上沿", AMBER_D, AMBER)]
ly = MAIN_Y + MAIN_H - 40
lx = CX + CW - 24 - sum(A.tw(t, 13) + 26 for t, _f, _g in LEG) - 16
for txt, fill, fg in LEG:
    ck, cwd = A.chip(lx, ly, txt, fill=fill, fg=fg, size=13, h=26)
    kids += ck
    lx += cwd + 8

PX0, PY0 = CX + 76, MAIN_Y + 104
PW = CW - 76 - 66
PH = MAIN_H - 104 - 92
VMIN, VMAX = 34.0, 74.0


def ty(v):
    return PY0 + PH - (v - VMIN) / (VMAX - VMIN) * PH


def tx(fh):
    return PX0 + PW * fh / 23.0


# evening-peak band, behind everything
PEAK0, PEAK1 = 17.0, 23.0
kids.append(D.box(tx(PEAK0), PY0, tx(PEAK1) - tx(PEAK0), PH,
                  color=A.A(VIOLET, 0.055)))
kids.append(A.label(tx(PEAK0) + 10, PY0 + 8, "晚高峰 17:00–23:00", size=12,
                    color=A.A(VIOLET, 0.85), ls=1.0,
                    w=tw("晚高峰 17:00–23:00", 12) + 8))

for v in range(35, 75, 5):
    kids.append(D.hline(PX0, PX0 + PW, ty(v), GRID, 1))
    kids.append(A.one_line(CX + 24, ty(v) - 10, str(v), size=13, color=FAINT,
                           font=A.MONO, align="RIGHT", pad=6, w=42, h=20))
kids.append(D.hline(PX0, PX0 + PW, PY0 + PH, LINE, 1.4))
for i in range(0, 24, 2):
    kids.append(A.one_line(tx(i) - 16, PY0 + PH + 10, "%02d" % i, size=13,
                           color=FAINT, font=A.MONO, pad=6, w=44, h=20))
kids.append(A.one_line(CX + 24, MAIN_Y + MAIN_H - 32,
                       "包络来自 01:00 冻结的日前计划；越上沿即进入事故拉路预案",
                       size=13, color=FAINT, pad=8))

# measured load first, so the forecast ribbon can sit cleanly on top of it
lp = [(tx(i), ty(v)) for i, v in enumerate(load)]
kids += A.area(lp, PY0 + PH, A.A(CYAN, 0.20), 3)

# yesterday, as a dashed reference line
yp = [(tx(i), ty(v)) for i, v in enumerate(yest)]
for j in range(0, 23, 2):
    kids += A.polyline([yp[j], yp[j + 1]], MUTED, 1.6)

# the frozen forecast envelope as a smooth ribbon between its two edges
hi_p = [(tx(i), ty(f_hi[i])) for i in range(24)]
lo_p = [(tx(i), ty(f_lo[i])) for i in range(24)]
kids += A.band(hi_p, lo_p, A.A(VIOLET, 0.11), 3)
kids += A.polyline(hi_p, AMBER, 1.6)
kids += A.polyline(lo_p, FAINT, 1.6)

kids += A.polyline(lp, CYAN, 3.0)
kids.append(A.dot(tx(18), ty(load[18]), 7.5, BG))
kids.append(A.dot(tx(18), ty(load[18]), 4.5, CYAN))
# the callout lives in clear air to the upper-left of the peak, with a leader
AX_, AY_ = 750, 306
kids.append(A.one_line(AX_, AY_, "18:30   68.0 GW", size=18, color=INK,
                       font=A.SEMI, pad=10))
kids.append(A.one_line(AX_, AY_ + 24, "越预报上沿 +1.8GW · 系统频率未越限",
                       size=13, color=AMBER, pad=8))
kids.append(A.seg(AX_ + 152, AY_ + 36, tx(18) - 10, ty(load[18]) - 8, A.A(AMBER, 0.5), 1.2))
kids.append(A.dot(tx(18) - 10, ty(load[18]) - 8, 2.6, A.A(AMBER, 0.8)))

# event flags on the time axis
for fh, _hh, _t, _s, c in EVENTS:
    ex = tx(fh)
    kids += A.dashed_v(ex, PY0 + 4, PY0 + PH, "#FFFFFF1F", 1.2, 5.0, 6.0)
    kids.append(A.dot(ex, PY0 + PH, 4.5,
                      {"amber": AMBER, "green": GREEN, "red": RED,
                       "cyan": CYAN}[c]))

# ------------------------------------------------------------ right column
RX = CX + CW + G
RW = W - M - RX
kids.append(A.plate(RX, MAIN_Y, RW, MAIN_H, fill=PANEL, radius=14, line=LINE))
kids.append(A.label(RX + 24, MAIN_Y + 22, "分区供电 · 计划已用比例", size=13,
                    color=FAINT, ls=2.2))
kids.append(A.one_line(RX + 24, MAIN_Y + 42, "冀北 94% 触发二级预警", size=20,
                       color=AMBER, font=A.SEMI, pad=20))
BY = MAIN_Y + 88
for name, gw, fr, state in AREAS:
    col = {"normal": CYAN, "tight": AMBER, "hot": RED}[state]
    kids.append(A.one_line(RX + 24, BY, name, size=15, color=INK, pad=6))
    kids.append(A.one_line(RX + RW - 24, BY, "%.1f GW · 已用 %d%%" % (gw, round(fr * 100)),
                           size=13, color=MUTED, font=A.MONO, anchor="RIGHT",
                           pad=8))
    kids += A.bar(RX + 24, BY + 24, RW - 48, 7, fr, col, track=GRID, radius=3.5)
    BY += 44
kids.append(D.hline(RX + 24, RX + RW - 24, BY + 8, LINE, 1))
kids.append(A.label(RX + 24, BY + 22, "直流 / 交流联络线 · MW 正为送出",
                    size=12, color=FAINT, ls=2.0))
TY_ = BY + 52
BCX = RX + RW // 2 - 4
BMAX = (RW - 48) / 2 - 10
for name, mw, way in TIE:
    out_ = mw < 0
    col = VIOLET if out_ else CYAN
    kids.append(A.one_line(RX + 24, TY_, name, size=14, color=INK, pad=6))
    s = ("受入 " if out_ else "送出 ") + ("%+d" % mw)
    kids.append(A.one_line(RX + RW - 24, TY_, s, size=13, color=col,
                           font=A.MONO, anchor="RIGHT", pad=8))
    kids.append(D.vline(BCX, TY_ + 20, TY_ + 36, GRID, 1.4))
    span = abs(mw) / 4000.0 * BMAX
    bx0 = BCX - span if out_ else BCX
    kids.append(D.box(bx0, TY_ + 24, span, 8, color=A.A(col, 0.8), radius=4))
    TY_ += 40

# ------------------------------------------------------------- event strip
kids.append(A.plate(M, EVENT_Y, W - 2 * M, EVENT_H, fill=PANEL, radius=14,
                    line=LINE))
kids.append(A.label(M + 24, EVENT_Y + 14, "夜间事件流", size=12, color=FAINT,
                    ls=2.2, anchor="LEFT"))
colw = (W - 2 * M - 48) / 4.0
for i, (fh, hh, title, sub, c) in enumerate(EVENTS):
    x = M + 24 + i * colw
    col = {"amber": AMBER, "green": GREEN, "red": RED, "cyan": CYAN}[c]
    kids.append(D.box(x, EVENT_Y + 38, 3, 42, color=col))
    kids.append(A.one_line(x + 14, EVENT_Y + 38, hh, size=14, color=col,
                           font=A.MONO, pad=6))
    kids.append(A.one_line(x + 74, EVENT_Y + 38, title, size=15, color=INK,
                           pad=8))
    kids.append(A.one_line(x + 74, EVENT_Y + 60, sub, size=12, color=MUTED,
                           pad=8))
    if i < 3:
        kids.append(D.vline(x + colw - 18, EVENT_Y + 34, EVENT_Y + 84, LINE, 1))

# ------------------------------------------------------------------ footer
kids.append(D.hline(M, W - M, H - 52, LINE, 1))
kids.append(A.label(M, H - 40,
                    "全部数值为自拟演示数据，不代表任何真实电网的运行记录",
                    size=13, color=FAINT, ls=0.6))
kids.append(A.one_line(W - M, H - 40, "CASE 01 / 10", size=13, color=FAINT,
                       font=A.MONO, anchor="RIGHT", pad=8))

dsl = A.root(kids, W, H, BG)
if __name__ == "__main__":
    import json
    final = "--final" in sys.argv
    r = run.emit(CASE, dsl, final=final, label=CASE)
    print(json.dumps({k: v for k, v in r.items() if k != "dsl"},
                     ensure_ascii=False))