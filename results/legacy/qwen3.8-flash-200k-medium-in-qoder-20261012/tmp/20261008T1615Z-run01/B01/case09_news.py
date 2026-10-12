"""B01 case-09 · 数据新闻长图：城市通勤十年（1200×H，移动端深度阅读）。

受众：普通读者在手机竖屏上花 3 分钟读完「十年间通勤变长了多少、变在哪种方式上、
早高峰是不是摊平了」。全部数字来自本文件顶部的一份方式表：逐年占比、加权平均时长、
十年增量、年通勤小时、距离与速度、峰时比例互相反算，改任一数字整图同步。
城市名与全部数据为虚构演示数据（口径见文末方法论）。
"""
import math
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
sys.path.insert(0, str(root / "tmp" / rid / "B01"))
from dslkit import Doc, TextFit, n  # noqa: E402
import b01kit as K  # noqa: E402

OUT = root / "tmp" / rid / "B01" / "case-09"
OUT.mkdir(parents=True, exist_ok=True)

# ==================== 数据（唯一来源） ====================
YEARS = list(range(2015, 2026))
# (方式, 2015 占比%, 2025 占比%, 2015 单程分钟, 2025 单程分钟, 颜色)
MODES = [
    ("轨道交通", 18.0, 34.0, 42.0, 46.0, "#0E6E6E"),
    ("常规公交", 26.0, 17.0, 38.0, 41.0, "#2F5C8F"),
    ("小汽车", 22.0, 19.0, 31.0, 38.0, "#B4863C"),
    ("出租 / 网约", 5.0, 6.0, 29.0, 35.0, "#5B4B8A"),
    ("自行车 / 共享", 12.0, 15.0, 22.0, 24.0, "#3F7D53"),
    ("步行", 14.0, 7.0, 15.0, 16.0, "#B4441F"),
    ("其他", 3.0, 2.0, 20.0, 22.0, "#8A9AA8"),
]
assert abs(sum(m[1] for m in MODES) - 100.0) < 1e-9
assert abs(sum(m[2] for m in MODES) - 100.0) < 1e-9

RAIL_KM = {2015: 460.0, 2025: 1104.0}          # 轨交运营里程
DIST = {2015: 6.8, 2025: 9.4}                  # 平均单程距离 km
PEAK = {2015: 41.5, 2025: 36.2}                # 7:00-9:00 占全天通勤出行 %
WORKDAYS = 250                                 # 年工作日（双向）
# (拐点位置 t, 陡度 k)：占比变化有快慢段，不是十年一条直线
LOGISTIC = {"轨道交通": (0.42, 0.16), "常规公交": (0.55, 0.20),
            "小汽车": (0.62, 0.26), "出租 / 网约": (0.50, 0.22),
            "自行车 / 共享": (0.38, 0.18), "步行": (0.60, 0.24),
            "其他": (0.50, 0.30)}


def eased(i, t):
    """把 t∈[0,1] 映射到该方式的 S 形进度，端点严格 0 / 1。"""
    m, k = LOGISTIC[MODES[i][0]]

    def g(x):
        return 1.0 / (1.0 + math.exp(-(x - m) / k))
    return (g(t) - g(0.0)) / (g(1.0) - g(0.0))


def shares_at(t):
    """插值到 t∈[0,1] 的占比，并把舍入残差补给轨道交通，保证合计严格 100%。"""
    vals = [round(m[1] + (m[2] - m[1]) * eased(i, t), 2)
            for i, m in enumerate(MODES)]
    vals[0] = round(vals[0] + (100.0 - sum(vals)), 2)
    return vals


def share(i, year):
    return shares_at((year - YEARS[0]) / float(YEARS[-1] - YEARS[0]))[i]


def year_shares(year):
    return shares_at((year - YEARS[0]) / float(YEARS[-1] - YEARS[0]))


def minutes(i, year):
    t = (year - YEARS[0]) / float(YEARS[-1] - YEARS[0])
    m = MODES[i]
    return m[3] + (m[4] - m[3]) * t


def avg(year):
    """加权平均单程时长 = Σ 占比 × 该方式时长 / 100。"""
    sh = year_shares(year)
    return sum(sh[i] * minutes(i, year) for i in range(len(MODES))) / 100.0


SERIES = [round(avg(y), 2) for y in YEARS]
A0, A1 = SERIES[0], SERIES[-1]
D_MIN = A1 - A0
D_PCT = D_MIN / A0 * 100.0
HOUR0 = A0 * 2 * WORKDAYS / 60.0
HOUR1 = A1 * 2 * WORKDAYS / 60.0
SPEED0 = DIST[2015] / (A0 / 60.0)
SPEED1 = DIST[2025] / (A1 / 60.0)
RAIL_X = RAIL_KM[2025] / RAIL_KM[2015]
PEAK_D = PEAK[2025] - PEAK[2015]
MAXY = max(SERIES)
MAXY_YEAR = YEARS[SERIES.index(MAXY)]
RISE = sum(1 for a, b in zip(SERIES, SERIES[1:]) if b > a)
SHARE_DELTA = [(m[0], m[2] - m[1], m[4] - m[3], m[5]) for m in MODES]
BIG_RISE = max(SHARE_DELTA, key=lambda x: x[1])
BIG_FALL = min(SHARE_DELTA, key=lambda x: x[1])

# ==================== 画布 ====================
W = 1200
M = 64
IX, IW = M, W - 2 * M
PAL = {"card": "#FFFFFF", "card2": "#EFEBE1", "border": "#D8D2C4",
       "row": "#F7F4EE", "t0": "#182230", "t1": "#4A5A6B", "t2": "#8A9AA8",
       "rust": "#B4441F", "teal": "#0E6E6E", "gold": "#B4863C",
       "violet": "#5B4B8A", "green": "#3F7D53", "blue": "#2F5C8F",
       "grey": "#8A9AA8", "bg": "#F4F1EA"}
d = Doc(W, 4000, bg=PAL["bg"], font="Inter,Noto Sans CJK SC", palette=PAL)
P = d.P
tf = TextFit()
tag = "c9"


def L(x, y, w, h, s, size, col=None, style=None, align="START", valign="MIDDLE",
      **kw):
    tf.check(tag, s, size, w, h, kw.get("maxlines") or 1)
    d.label(x, y, w, h, s, col or P["t0"], size, style, align=align,
            valign=valign, **kw)


def R(xr, y, w, h, s, size, col=None, style=None, **kw):
    L(xr - w, y, w, h, s, size, col, style, align="END", **kw)


def fr(x, y, w, h, radius, border):
    d.pos(x, y, w, h, d.box(w, h, radius=radius, border=border))


def mix(hex6, a, over="#FFFFFF"):
    """预合成实色：逐列面积图用 8 位 alpha 时，相邻列重叠会叠成竖纹。"""
    o = [int(hex6[i:i + 2], 16) for i in (1, 3, 5)]
    u = [int(over[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(int(round(o[i] * a + u[i] * (1 - a)))
                                   for i in range(3))


def panel(x, y, w, h, fill=None, border="#D8D2C4", radius=10):
    assert x >= IX - 0.01 and x + w <= IX + IW + 0.01, (x, w)
    d.rect(x, y, w, h, fill or P["card"], radius=radius)
    if border:
        fr(x, y, w, h, radius, "1 SOLID %s" % border)


def sec(y, num, title, stand):
    """栏目标题 + 一句话结论（数据新闻的 so-what 行）。"""
    d.rect(IX, y + 6, 4, 40, P["rust"])
    L(IX + 16, y, 44, 26, num, 15, P["rust"], "BOLD", valign="TOP")
    L(IX + 46, y - 2, 640, 34, title, 27, P["t0"], "BOLD", valign="TOP")
    L(IX + 46, y + 34, IW - 46, 26, stand, 17, P["t1"], valign="TOP")
    d.line(IX, y + 66, IX + IW, y + 66, 1, P["border"])
    return y + 80


# ==================== 00 头部 ====================
d.rect(0, 0, W, 8, P["rust"])
Y = 40
L(IX, Y, 500, 22, "城市观察 · 数据新闻 · 第 41 期", 15, P["rust"], "BOLD",
  valign="TOP", spacing=2)
R(IX + IW, Y, 300, 22, "2026 年 10 月 10 日 刊发", 15, P["t2"], valign="TOP")
Y += 40
L(IX, Y, IW, 88, "通勤十年", 78, P["t0"], "BOLD", valign="TOP", spacing=10)
Y += 98
L(IX, Y, IW, 40, "十年里单程通勤多花 %g 分钟——变长的不是路，是换乘"
  % round(D_MIN, 1), 30, P["rust"], valign="TOP", maxlines=1)
Y += 52
LEAD = ("十年间，这座城的轨道交通运营里程从 %g 公里铺到 %g 公里（%.1f 倍），"
        "通勤者却并没有因此省时间：平均单程从 %.1f 分钟涨到 %.1f 分钟，"
        "一年两头算下来多出 %.0f 个小时。差别在于，把大家送得更远的那部分运力，"
        "同时把换乘、步行接驳和等车的时间一起拉长了。" % (
            RAIL_KM[2015], RAIL_KM[2025], RAIL_X, A0, A1, HOUR1 - HOUR0))
L(IX, Y, IW, 108, LEAD, 20, P["t1"], valign="TOP", maxlines=4, height=1.6)
Y += 120
L(IX, Y, 700, 24, "文 / 城市观察数据组    图 / Snapshot 生成    "
  "数据为虚构演示口径", 16, P["t2"], valign="TOP")
R(IX + IW, Y, 380, 24, "样本：常住通勤人口 %d 人 · 年报口径" % 12000, 16,
  P["t2"], valign="TOP")
Y += 46

# ==================== 01 核心数字 ====================
Y = sec(Y, "01", "四个数先看结论", "十年增量的规模、结构与代价")
KPI = [("平均单程时长", "%.1f" % A1, "分钟", "2015 年 %.1f 分钟" % A0, P["teal"]),
       ("十年增量", "+%.1f" % D_MIN, "分钟", "同比 +%g%%" % round(D_PCT, 1),
        P["rust"]),
       ("轨交运营里程", "%.1f" % RAIL_X, "倍", "%g → %g 公里" % (
        RAIL_KM[2015], RAIL_KM[2025]), P["blue"]),
       ("一年多花", "%.0f" % (HOUR1 - HOUR0), "小时", "按 %d 个工作日双向" %
        WORKDAYS, P["gold"])]
kw = (IW - 3 * 14) / 4.0
for i, (lab, big, unit, sub, col) in enumerate(KPI):
    x = IX + i * (kw + 14)
    panel(x, Y, kw, 150)
    d.rect(x, Y, kw, 4, col, radius=2)
    L(x + 18, Y + 22, kw - 36, 22, lab, 16, P["t2"], valign="TOP")
    L(x + 18, Y + 50, kw - 36 - 46, 56, big, 46, col, "BOLD", valign="TOP")
    L(x + 18, Y + 108, kw - 36, 24, unit, 17, P["t1"], valign="TOP")
    L(x + 18, Y + 128, kw - 36, 20, sub, 14, P["t2"], valign="TOP")
Y += 174

# ==================== 02 十年趋势折线 ====================
JUMPS = [(SERIES[i + 1] - SERIES[i], YEARS[i], YEARS[i + 1])
         for i in range(len(SERIES) - 1)]
JUMP, JY0, JY1 = max(JUMPS, key=lambda j: j[0])
Y = sec(Y, "02", "十年曲线：涨上去就下不来",
        "%d 个年份里有 %d 年在变长，最大一跳 %+.1f 分钟出现在 %d→%d 年" % (
            len(JUMPS), RISE, JUMP, JY0, JY1))
CH_X, CH_Y, CH_W, CH_H = IX, Y, IW, 268
panel(CH_X, CH_Y, CH_W, CH_H + 70)
lo = math.floor(min(SERIES) / 2.0) * 2.0
hi = math.ceil(max(SERIES) / 2.0) * 2.0 + 2
ticks = [lo + k * 2 for k in range(int((hi - lo) / 2) + 1)]
PL, PR, PT, PB = 74, 40, 34, 46
pw = CH_W - PL - PR
ph = CH_H - PT - PB


def px(i):
    return CH_X + PL + pw * i / float(len(YEARS) - 1)


def py(v):
    return CH_Y + PT + ph * (1 - (v - lo) / (hi - lo))


for t in ticks:
    yy = py(t)
    d.line(CH_X + PL, yy, CH_X + CH_W - PR, yy, 1, P["border"])
    R(CH_X + PL - 12, yy - 11, 52, 22, "%g" % t, 14, P["t2"], valign="TOP")
for i, yr in enumerate(YEARS):
    if (yr - YEARS[0]) % 2:
        continue
    L(px(i) - 30, CH_Y + PT + ph + 12, 60, 20, str(yr), 14, P["t2"],
      align="CENTER", valign="TOP")
pts = [(px(i), py(v)) for i, v in enumerate(SERIES)]
# 面积（逐列矩形，避免 path 图元）
for i in range(len(pts) - 1):
    (x1, y1), (x2, y2) = pts[i], pts[i + 1]
    steps = 14
    for k in range(steps):
        f = k / float(steps)
        xx = x1 + (x2 - x1) * f
        hh = (CH_Y + PT + ph) - (y1 + (y2 - y1) * f)
        d.rect(xx, y1 + (y2 - y1) * f, (x2 - x1) / steps + 1.2, hh,
               mix(P["rust"], 0.10))
K.polyline(d, pts, 3, P["rust"])
JIDX = YEARS.index(JY1)
for i, (x, y) in enumerate(pts):
    big = i == 0 or i == len(pts) - 1 or i == JIDX
    d.rect(x - (5 if big else 3.2), y - (5 if big else 3.2),
           10 if big else 6.4, 10 if big else 6.4,
           P["card"] if big else P["rust"], radius=5 if big else 3.2)
    if big:
        fr(x - 5, y - 5, 10, 10, 5, "2 SOLID %s" % P["rust"])
L(pts[0][0] + 14, pts[0][1] - 6, 130, 22, "起点 %.1f" % A0, 15, P["t1"],
  valign="TOP")
L(pts[-1][0] - 152, pts[-1][1] + 10, 138, 22, "终点 %.1f" % A1, 15, P["t1"],
  align="END", valign="TOP")
jx, jy = pts[JIDX]
L(jx - 88, jy - 40, 176, 22, "最快一年 %+.1f 分" % JUMP, 15, P["rust"],
  "BOLD", align="CENTER", valign="TOP")
d.line(jx, jy - 16, jx, jy - 6, 1, P["rust"])
if MAXY_YEAR not in (YEARS[0], YEARS[-1]):
    mx, my = pts[SERIES.index(MAXY)]
    L(mx - 60, my - 34, 120, 22, "峰值 %.1f" % MAXY, 15, P["rust"], "BOLD",
      align="CENTER", valign="TOP")
L(IX + 18, CH_Y + CH_H + 40, CH_W - 36, 24,
  "口径：加权平均单程通勤时长（含等车与换乘步行），单位分钟。逐年由方式占比与"
  "分方式时长反算。", 15, P["t2"], valign="TOP")
Y += CH_H + 70 + 22

# ==================== 03 小倍数：七种方式的占比变化 ====================
Y = sec(Y, "03", "小倍数：谁在变多，谁在变少",
        "%s 十年占比 +%.0f 个百分点，%s −%.0f 个百分点" % (
            BIG_RISE[0], BIG_RISE[1], BIG_FALL[0], abs(BIG_FALL[1])))
SM = 4
gw = (IW - (SM - 1) * 14) / float(SM)
gh = 156
for i, (nm, s0, s1, m0, m1, col) in enumerate(MODES):
    r, c = divmod(i, SM)
    x = IX + c * (gw + 14)
    y = Y + r * (gh + 14)
    panel(x, y, gw, gh)
    L(x + 16, y + 14, gw - 100, 24, nm, 18, P["t0"], "BOLD", valign="TOP")
    dl = s1 - s0
    R(x + gw - 16, y + 16, 80, 22, "%+.0f pp" % dl, 16,
      P["green"] if dl > 0 else (P["rust"] if dl < 0 else P["t2"]),
      "BOLD", valign="TOP")
    vals = [share(i, yr) for yr in YEARS]
    v0, v1 = min(vals), max(vals)
    bx, by, bw, bh = x + 16, y + 52, gw - 32, 66
    span = (v1 - v0) or 1.0
    sp = [(bx + bw * k / float(len(vals) - 1),
           by + bh * (1 - (vals[k] - v0) / span)) for k in range(len(vals))]
    for k in range(len(sp) - 1):
        (ax, ay), (bxx, byy) = sp[k], sp[k + 1]
        steps = 10
        for t in range(steps):
            f = t / float(steps)
            hh = (by + bh) - (ay + (byy - ay) * f)
            d.rect(ax + (bxx - ax) * f, ay + (byy - ay) * f,
                   (bxx - ax) / steps + 1.2, hh, mix(col, 0.16))
    K.polyline(d, sp, 2.5, col)
    d.rect(sp[-1][0] - 3.5, sp[-1][1] - 3.5, 7, 7, col, radius=3.5)
    L(x + 16, y + 126, gw - 32, 20, "占比 %.0f%% → %.0f%%" % (s0, s1), 14,
      P["t1"], valign="TOP")
    L(x + 16, y + 144, gw - 32, 20, "单程 %.0f → %.0f 分钟" % (m0, m1), 14,
      P["t2"], valign="TOP")
rows = int(math.ceil(len(MODES) / float(SM)))
Y += rows * (gh + 14) + 8

# ==================== 04 waffle：出行结构 100 格 ====================
Y = sec(Y, "04", "结构对照：每格 1% 的十年",
        "两幅各 100 格（10×10），一格等于 1% 的通勤者")
CELL, GAP = 22.0, 3.0
GRID = CELL * 10 + GAP * 9
gy = Y
for k, (yr, idx) in enumerate([(2015, 1), (2025, 2)]):
    gx = IX + k * (GRID + 90)
    L(gx, gy, GRID, 26, "%d 年" % yr, 20, P["t0"], "BOLD", valign="TOP")
    sh = year_shares(yr)
    acc = 0
    for i, m in enumerate(MODES):
        cnt = int(round(sh[i]))
        for j in range(cnt):
            c = (acc + j) % 10
            r = (acc + j) // 10
            d.rect(gx + c * (CELL + GAP), gy + 36 + r * (CELL + GAP),
                   CELL, CELL, m[5], radius=3)
        acc += cnt
    assert acc == 100, acc
    R(gx + GRID, gy, 200, 26, "加权 %.1f 分钟" % SERIES[YEARS.index(yr)], 16,
      P["t2"], valign="TOP")
lx = IX + 2 * GRID + 90 * 2 - 40
L(lx, gy - 6, 260, 24, "图例（2015 → 2025）", 16, P["t1"], "BOLD", valign="TOP")
for i, m in enumerate(MODES):
    yy = gy + 28 + i * 27
    d.rect(lx, yy, 16, 16, m[5], radius=3)
    L(lx + 26, yy - 4, 130, 22, m[0], 15, P["t1"], valign="TOP")
    R(lx + 262, yy - 4, 100, 22, "%.0f%% → %.0f%%" % (m[1], m[2]), 14,
      P["t2"], valign="TOP")
Y += 36 + GRID + 22

# ==================== 05 arc 环：峰时摊平 ====================
Y = sec(Y, "05", "早高峰摊平了，但通勤没变短",
        "7:00–9:00 出行占比 %+.1f 个百分点，长尾时段在变厚" % PEAK_D)
ring_y = Y
for k, (yr, col) in enumerate([(2015, P["blue"]), (2025, P["rust"])]):
    cx = IX + 120 + k * 250
    cy = ring_y + 120
    K.donut(d, cx, cy, 92, 26, [(PEAK[yr], col), (100 - PEAK[yr], "#E4DFD3")],
            start=-90.0)
    L(cx - 92, cy - 30, 184, 40, "%.1f%%" % PEAK[yr], 34, col, "BOLD",
      align="CENTER", valign="TOP")
    L(cx - 92, cy + 12, 184, 24, "%d 年峰时占比" % yr, 15, P["t2"],
      align="CENTER", valign="TOP")
tx = IX + 540
L(tx, ring_y + 24, 400, 26, "峰时之外，通勤者被摊到哪去了", 19, P["t0"],
  "BOLD", valign="TOP")
TAIL = [("9:00–16:00 平峰", 24.6, 29.8), ("16:00–19:00 晚高峰", 22.4, 23.5),
        ("19:00 以后", 11.5, 10.5)]
assert abs(sum(t[1] for t in TAIL) + PEAK[2015] - 100.0) < 0.05, "分时段占比未闭合"
assert abs(sum(t[2] for t in TAIL) + PEAK[2025] - 100.0) < 0.05, "分时段占比未闭合"
for i, (lab, a, b) in enumerate(TAIL):
    yy = ring_y + 62 + i * 44
    L(tx, yy, 190, 22, lab, 16, P["t1"], valign="TOP")
    bx2, bw2 = tx + 200, 170
    tk = mix(P["grey"], 0.22, PAL["bg"])
    d.rect(bx2, yy + 2, bw2, 12, tk, radius=6)
    d.rect(bx2, yy + 2, bw2 * a / PEAK[2015], 12, P["blue"], radius=6)
    d.rect(bx2, yy + 18, bw2, 12, tk, radius=6)
    d.rect(bx2, yy + 18, bw2 * b / PEAK[2015], 12, P["rust"], radius=6)
    R(IX + IW, yy, 150, 22, "%.1f → %.1f%%" % (a, b), 15, P["t2"],
      valign="TOP")
L(tx, ring_y + 200, 500, 22, "深蓝 = 2015，锈红 = 2025；条长满格 = %.1f%%，"
  "与左侧峰时占比同一尺度" % PEAK[2015], 14, P["t2"], valign="TOP")
Y = ring_y + 250

# ==================== 06 分方式时长成对条 ====================
Y = sec(Y, "06", "变长的是哪一段路",
        "七种方式的单程时长全部在增加，%s +%.0f 分钟最多" %
        (max(MODES, key=lambda m: m[4] - m[3])[0],
         max(m[4] - m[3] for m in MODES)))
pairs = sorted([(nm, m0, m1, col) for nm, _s0, _s1, m0, m1, col in MODES],
               key=lambda r: -r[2])
PMAX = 50.0
py0 = Y
for i, (nm, m0, m1, col) in enumerate(pairs):
    yy = py0 + i * 52
    L(IX, yy + 6, 170, 24, nm, 17, P["t0"], valign="TOP")
    bx = IX + 186
    bw = IW - 186 - 150
    d.rect(bx, yy, bw * m0 / PMAX, 17, mix(P["grey"], 0.16, PAL["bg"]),
           radius=4)
    fr(bx, yy, bw * m0 / PMAX, 17, 4, "1 SOLID %s" % mix(P["grey"], 0.60))
    d.rect(bx, yy + 21, bw * m1 / PMAX, 17, col, radius=4)
    R(IX + IW, yy - 2, 140, 20, "2015 %.0f" % m0, 14, P["t2"], valign="TOP")
    R(IX + IW, yy + 20, 140, 20, "2025 %.0f" % m1, 14, P["t1"], "BOLD",
      valign="TOP")
Y = py0 + len(pairs) * 52 + 12

# ==================== 07 距离与速度反算表 ====================
Y = sec(Y, "07", "走得更远了，也并没有更快",
        "平均单程距离 +%.1f 公里，而门到门速度只提高 %.1f 公里/小时" % (
            DIST[2025] - DIST[2015], SPEED1 - SPEED0))
tbl = [("平均单程距离", "%.1f 公里" % DIST[2015], "%.1f 公里" % DIST[2025],
        "+%.1f" % (DIST[2025] - DIST[2015])),
       ("平均单程时长", "%.1f 分钟" % A0, "%.1f 分钟" % A1, "+%.1f" % D_MIN),
       ("门到门速度", "%.1f 公里/小时" % SPEED0, "%.1f 公里/小时" % SPEED1,
        "+%.1f" % (SPEED1 - SPEED0)),
       ("年通勤总时长", "%.0f 小时" % HOUR0, "%.0f 小时" % HOUR1,
        "+%.0f" % (HOUR1 - HOUR0))]
TW = [IW - 3 * 200 - 150, 200, 200, 150]
ALG = ["START", "CENTER", "CENTER", "END"]
ty = Y


def cell(cx, cw, yy, ch, txt, size, col, style=None, alg="START"):
    pad = 16
    if alg == "END":
        R(cx + cw - pad, yy, cw - 2 * pad, ch, txt, size, col, style,
          valign="TOP")
    elif alg == "CENTER":
        L(cx + pad, yy, cw - 2 * pad, ch, txt, size, col, style,
          align="CENTER", valign="TOP")
    else:
        L(cx + pad, yy, cw - 2 * pad, ch, txt, size, col, style, valign="TOP")


d.rect(IX, ty, IW, 44, P["card2"])
for j, htxt in enumerate(["指标", "2015 年", "2025 年", "十年变化"]):
    cell(IX + sum(TW[:j]), TW[j], ty, 44, htxt, 16, P["t1"], "BOLD", ALG[j])
for i, row in enumerate(tbl):
    yy = ty + 44 + i * 52
    if i % 2 == 0:
        d.rect(IX, yy, IW, 52, P["row"])
    for j, c in enumerate(row):
        cell(IX + sum(TW[:j]), TW[j], yy, 52, c, 18,
             P["rust"] if j == 3 else P["t0"], "BOLD" if j == 3 else None,
             ALG[j])
    d.line(IX, yy + 52, IX + IW, yy + 52, 1, P["border"])
Y = ty + 44 + len(tbl) * 52 + 18
L(IX, Y, IW, 24, "校验：距离 ÷ 时长 = 速度。%.1f km ÷ (%.1f/60) h = %.1f，"
  "%.1f km ÷ (%.1f/60) h = %.1f，与表内数值一致。" % (
      DIST[2015], A0, SPEED0, DIST[2025], A1, SPEED1), 16, P["t2"],
  valign="TOP")
Y += 40

# ==================== 08 结论与方法论 ====================
Y = sec(Y, "08", "三条结论", "如果只记住三句话")
CONC = [("运力翻倍不等于时间变短",
         "轨交里程 %.1f 倍的同时，平均出行距离从 %.1f 公里涨到 %.1f 公里，"
         "多出来的运力先被用来把人送得更远。" % (RAIL_X, DIST[2015], DIST[2025])),
        ("时间花在接驳与换乘上",
         "加权时长涨 %.1f 分钟，其中轨道交通自身只涨 %.0f 分钟；"
         "涨幅主要来自步行与公交向轨道转移后的换乘与等车。" % (
             D_MIN, MODES[0][4] - MODES[0][3])),
        ("峰时摊平，长尾变厚",
         "早高峰占比 %+.1f 个百分点，平峰 %+.1f 个百分点——通勤没有变短，"
         "只是不再挤在同一小时。" % (PEAK_D, TAIL[0][2] - TAIL[0][1]))]
for i, (t1, t2) in enumerate(CONC):
    yy = Y + i * 86
    d.rect(IX, yy + 4, 30, 30, P["rust"], radius=15)
    L(IX, yy + 4, 30, 30, str(i + 1), 16, "#FFFFFF", "BOLD", align="CENTER")
    L(IX + 46, yy, IW - 46, 28, t1, 21, P["t0"], "BOLD", valign="TOP")
    L(IX + 46, yy + 32, IW - 46, 48, t2, 17, P["t1"], valign="TOP",
      maxlines=2, height=1.5)
Y += len(CONC) * 86 + 8
panel(IX, Y, IW, 150, fill="#EFEBE1", border="#D8D2C4")
L(IX + 22, Y + 16, IW - 44, 24, "方法论与数据来源", 18, P["t0"], "BOLD",
  valign="TOP")
METH = ("口径：12 000 名常住通勤人口的年报抽样，单程门到门时间含步行接驳、等车与换乘；"
        "加权平均 = Σ 方式占比 × 该方式时长 ÷ 100，逐年占比按各方式的 S 形路径内插"
        "（拐点与陡度为演示设定，端点严格等于首末年实测值）后归一至 100%%。\n"
        "本图为 Snapshot DSL 生成的演示作品：城市名、样本量、占比、时长、里程、峰时分布"
        "全部为虚构数据，不对应任何真实城市或统计机构发布值。\n"
        "图形全部由 DSL 构造，未使用外部图片或字体素材；改任一数字后趋势、waffle、"
        "环图、成对条与本表同步重算。")
L(IX + 22, Y + 46, IW - 44, 104, METH, 15, P["t1"], valign="TOP", maxlines=7,
  height=1.5)
Y += 166
d.line(IX, Y, IX + IW, Y, 1, P["border"])
Y += 14
L(IX, Y, 700, 22, "城市观察 · 通勤十年 · 共 %d 个年份 %d 种方式" % (
    len(YEARS), len(MODES)), 15, P["t2"], valign="TOP")
R(IX + IW, Y, 300, 22, "虚构演示数据", 15, P["rust"], "BOLD", valign="TOP")
Y += 40

d.H = int(math.ceil(Y))
dsl = d.dsl()
(OUT / "case09.snapshot").write_text(dsl, encoding="utf-8")
print("canvas %dx%d bytes %d textfit %d %s" % (
    W, d.H, len(dsl), tf.n, tf.problems[:6]))
print("avg %.2f -> %.2f  delta %.2f (%.1f%%)  hours %.1f -> %.1f" % (
    A0, A1, D_MIN, D_PCT, HOUR0, HOUR1))
print("series", SERIES)
print("speed %.2f -> %.2f  rail x%.2f  peak %.1f -> %.1f  rise %d/%d" % (
    SPEED0, SPEED1, RAIL_X, PEAK[2015], PEAK[2025], RISE, len(SERIES) - 1))
for y_ in (2015, 2020, 2025):
    print(y_, year_shares(y_), sum(year_shares(y_)))
