"""B01 case-10 · 机场出发航显 FIDS 超宽屏（2880×1080，大厅 3 米外扫读）。

受众：到港楼出发大厅的旅客，站在 3 米外 5 秒内要找到自己要乘的航班、登机口和状态；
同屏还有值机岛侧的接送人员看"还有多久开始登机"。全部时刻、状态、汇总数由一张
FLIGHTS 表 + 一个模拟时钟 NOW 反算：预计=计划+延误，登机=预计−40，截止=预计−15，
到达当地=预计+飞行+(时区差)，状态由 NOW 与三个节点比较得出，改任一数字整屏同步。
机场、航班号、时刻、登机口全部为虚构演示数据。
"""
import math
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
sys.path.insert(0, str(root / "tmp" / rid / "B01"))
from dslkit import Doc, TextFit, minutes  # noqa: E402
import b01kit as K  # noqa: E402

OUT = root / "tmp" / rid / "B01" / "case-10"
OUT.mkdir(parents=True, exist_ok=True)

# ==================== 数据（唯一来源） ====================
TZ_LOCAL = 8                    # 本地时区 UTC+8
NOW = 14 * 60 + 32              # 模拟时刻 14:32 本地
BOARD_LEAD = 40                 # 预计起飞前 40 分钟开始登机
CLOSE_LEAD = 15                 # 起飞前 15 分钟截止
CHECKIN_LEAD = 150              # 起飞前 150 分钟开放值机

# (航班, 航司, 到达城市, 城市英文, IATA, 时区, 计划HH:MM, 飞行分钟, 值机区, 登机口,
#  延误, 取消, 改口后登机口, 备注)
FLIGHTS = [
    ("MU 5118", "东方航空", "东京成田", "Tokyo", "NRT", 9, "14:45", 170, "E", "C21",
     0, False, None, ""),
    ("CA 9831", "国际航空", "首尔仁川", "Seoul", "ICN", 9, "15:05", 110, "F", "C08",
     0, False, None, ""),
    ("MU 2150", "东方航空", "昆明长水", "Kunming", "KMG", 8, "15:10", 165, "D", "B12",
     0, False, None, ""),
    ("3U 8890", "四川航空", "成都天府", "Chengdu", "TFU", 8, "15:00", 135, "B", "A07",
     25, False, None, "流控 · 区域等待"),
    ("CZ 3102", "南方航空", "广州白云", "Guangzhou", "CAN", 8, "15:40", 150, "C", "D03",
     0, False, None, ""),
    ("HO 1385", "吉祥航空", "曼谷素万那普", "Bangkok", "BKK", 7, "16:05", 260, "G", "D21",
     0, False, None, "经停 45 分钟"),
    ("MU 777", "东方航空", "洛杉矶", "Los Angeles", "LAX", -7, "15:55", 675, "K", "C33",
     0, True, None, "机型故障 · 改签 MU 771"),
    ("ZH 9102", "深圳航空", "深圳宝安", "Shenzhen", "SZX", 8, "16:50", 45, "A", "B09",
     0, False, None, ""),
    ("AF 383", "法国航空", "巴黎戴高乐", "Paris", "CDG", 2, "16:30", 690, "J", "C24",
     40, False, "C28", "远程机位 · 摆渡车 15 分钟"),
    ("SQ 825", "新加坡航空", "新加坡", "Singapore", "SIN", 8, "17:30", 300, "H", "B18",
     0, False, None, ""),
]


def hhmm(m):
    """分钟 -> HH:MM（跨日由 daymark 单独给出）。"""
    return "%02d:%02d" % divmod(int(m) % 1440, 60)


def daymark(m):
    return int(math.floor(m / 1440.0))


def build(row):
    (fl, air, city, en, iata, tz, sched, fly, desk, gate, delay, cxl,
     newgate, note) = row
    std = minutes(sched)
    est = std + delay
    f = dict(fl=fl, air=air, city=city, en=en, iata=iata, tz=tz, sched=std,
             est=est, fly=fly, desk=desk, gate=newgate or gate,
             oldgate=gate, delay=delay, cxl=cxl, note=note,
             board=est - BOARD_LEAD, close=est - CLOSE_LEAD,
             open_at=est - CHECKIN_LEAD)
    f["arr"] = est + fly + (tz - TZ_LOCAL) * 60
    f["arr_day"] = daymark(f["arr"]) - daymark(est)
    if f["cxl"]:
        f["st"] = "取消"
    elif NOW >= f["close"]:
        f["st"] = "最后催促"
    elif NOW >= f["board"]:
        f["st"] = "开始登机"
    elif NOW >= f["open_at"]:
        f["st"] = "值机开放"
    else:
        f["st"] = "计划"
    return f


ROWS = sorted([build(r) for r in FLIGHTS],
              key=lambda f: (f["cxl"], f["est"]))
LIVE = [f for f in ROWS if not f["cxl"]]
ST_COLOR = {"取消": "red", "最后催促": "rust", "开始登机": "green",
            "值机开放": "cyan", "计划": "dim"}
N_CXL = sum(1 for f in ROWS if f["cxl"])
N_DELAY = sum(1 for f in LIVE if f["delay"] > 0)
AVG_DELAY = sum(f["delay"] for f in LIVE if f["delay"]) / float(N_DELAY)
ON_TIME = 100.0 * (len(LIVE) - N_DELAY) / len(LIVE)
N_OPEN = sum(1 for f in LIVE if NOW >= f["open_at"])
N_SOON = sum(1 for f in LIVE if 0 <= f["est"] - NOW <= 60)
N_BOARD = sum(1 for f in LIVE if f["st"] in ("开始登机", "最后催促"))
N_GATECHG = sum(1 for f in LIVE if f["gate"] != f["oldgate"])
FIRST_LIVE = LIVE[0]

ZONES = [(9, "东京 / 首尔", "UTC+9"), (TZ_LOCAL, "本地 · 上海", "UTC+8"),
         (7, "曼谷", "UTC+7"), (2, "巴黎", "UTC+2"), (-7, "洛杉矶", "UTC−7")]

# ==================== 画布 ====================
W, H = 2880, 1080
PAL = {"bg": "#05090F", "panel": "#0D1521", "panel2": "#111B29",
       "border": "#1E2C3F", "line": "#17222F", "t0": "#EAF2FB",
       "t1": "#9FB3C8", "t2": "#63798F", "green": "#2FBF71",
       "cyan": "#38B6E0", "amber": "#F2A93B", "rust": "#E4572E",
       "red": "#E23D3D", "violet": "#8B7BE8", "dim": "#54687E",
       "gold": "#C9A227"}
d = Doc(W, H, bg=PAL["bg"], font="Inter,Noto Sans CJK SC", palette=PAL)
P = d.P
tf = TextFit()
tag = "c10"


def L(x, y, w, h, s, size, col=None, style=None, align="START", valign="MIDDLE",
      **kw):
    tf.check(tag, s, size, w, h, kw.get("maxlines") or 1)
    d.label(x, y, w, h, s, col or P["t0"], size, style, align=align,
            valign=valign, **kw)


def R(xr, y, w, h, s, size, col=None, style=None, **kw):
    L(xr - w, y, w, h, s, size, col, style, align="END", **kw)


def C(xc, y, w, h, s, size, col=None, style=None, **kw):
    L(xc - w / 2.0, y, w, h, s, size, col, style, align="CENTER", **kw)


def fr(x, y, w, h, radius, border):
    d.pos(x, y, w, h, d.box(w, h, radius=radius, border=border))


def panel(x, y, w, h, fill=None, border="#1E2C3F", radius=12):
    d.rect(x, y, w, h, fill or P["panel"], radius=radius)
    if border:
        fr(x, y, w, h, radius, "1 SOLID %s" % border)


# ==================== 顶栏 ====================
d.rect(0, 0, W, 140, P["panel"])
d.rect(0, 138, W, 2, K.hexa(P["cyan"], 0.55))
L(56, 30, 200, 84, "PVG", 64, P["t0"], "BOLD", valign="TOP", spacing=2)
L(256, 34, 460, 40, "上海浦东国际机场", 30, P["t0"], valign="TOP")
L(256, 78, 460, 32, "SHANGHAI PUDONG · 航站楼 2", 19, P["t2"], valign="TOP")
d.line(700, 34, 700, 106, 1, P["border"])
L(736, 30, 420, 56, "出发", 44, P["cyan"], "BOLD", valign="TOP", spacing=8)
L(736, 88, 420, 28, "DEPARTURES · 实时航班显示", 19, P["t2"], valign="TOP")
# 右侧大字时钟 + 日期 + 时区
R(W - 56, 22, 300, 74, hhmm(NOW), 70, P["t0"], "BOLD", valign="TOP",
  features="tnum")
R(W - 56, 96, 300, 28, "2026 年 10 月 10 日 星期六", 19, P["t2"], valign="TOP")
L(W - 386, 34, 120, 30, "UTC+08", 24, P["cyan"], "BOLD", align="END",
  valign="TOP", features="tnum")
d.line(W - 360, 34, W - 360, 106, 1, P["border"])
R(W - 420, 40, 180, 26, "下次刷新", 18, P["t2"], valign="TOP")
R(W - 420, 66, 180, 34, "30 秒后", 24, P["amber"], "BOLD", valign="TOP")

# ==================== 左栏 ====================
RX, RY, RW = 56, 176, 520
# --- 概览 ---
panel(RX, RY, RW, 236)
L(RX + 24, RY + 18, RW - 48, 28, "本时段态势", 23, P["t0"], "BOLD",
  valign="TOP")
R(RX + RW - 24, RY + 18, 200, 28, "由下表实时汇总", 17, P["t2"], valign="TOP")
MET = [("在表航班", "%d" % len(LIVE), "另有 %d 班取消" % N_CXL, P["cyan"]),
       ("已开放值机", "%d" % N_OPEN, "起飞前 %d 分钟开放" % CHECKIN_LEAD, P["green"]),
       ("60 分钟内起飞", "%d" % N_SOON, "最近一班 %s" % FIRST_LIVE["fl"], P["gold"]),
       ("登机中 / 催促", "%d" % N_BOARD, "含最后催促 %d 班"
        % sum(1 for f in LIVE if f["st"] == "最后催促"), P["cyan"]),
       ("延误班次", "%d" % N_DELAY, "平均延误 %.1f 分钟" % AVG_DELAY, P["amber"]),
       ("准点率", "%.1f%%" % ON_TIME, "口径：无延误占比", P["green"])]
cw = (RW - 48) / 3.0
for i, (lab, big, sub, col) in enumerate(MET):
    r, c = divmod(i, 3)
    x = RX + 24 + c * cw
    y = RY + 58 + r * 90
    L(x, y, cw - 10, 22, lab, 17, P["t2"], valign="TOP")
    L(x, y + 22, cw - 10, 40, big, 34, col, "BOLD", valign="TOP",
      features="tnum")
    L(x, y + 64, cw - 8, 20, sub, 15, P["t1"], valign="TOP")
    if c:
        d.line(x - 12, y + 4, x - 12, y + 78, 1, P["line"])
RY2 = RY + 236 + 20

# --- 时区带 ---
panel(RX, RY2, RW, 272)
L(RX + 24, RY2 + 18, RW - 48, 28, "时区带 · 各到达地此刻", 23, P["t0"], "BOLD",
  valign="TOP")
tz_y = RY2 + 62
band_x, band_w = RX + 132, RW - 132 - 150
for off, name, code in ZONES:
    lm = (NOW + (off - TZ_LOCAL) * 60) % 1440
    frac = lm / 1440.0
    L(RX + 24, tz_y - 2, 104, 24, name, 17, P["t1"], valign="TOP")
    d.rect(band_x, tz_y + 2, band_w, 16, "#08101A", radius=8)
    d.rect(band_x + band_w * 6 / 24.0, tz_y + 2, band_w * 16 / 24.0, 16,
           "#1D2C3D")
    for tk in (6, 12, 18):
        d.line(band_x + band_w * tk / 24.0, tz_y + 2,
               band_x + band_w * tk / 24.0, tz_y + 18, 1, P["bg"])
    mx = band_x + band_w * frac
    d.rect(mx - 3, tz_y - 4, 6, 28, P["cyan"], radius=3)
    hh, mi = divmod(lm, 60)
    R(RX + RW - 24, tz_y - 2, 146, 24, "%02d:%02d  %s" % (hh, mi, code), 17,
      P["t0"], "BOLD", valign="TOP", features="tnum")
    tz_y += 36
L(RX + 24, tz_y + 2, RW - 48, 22, "刻度 00→24 点；深色 = 当地 22:00–06:00",
  15, P["t2"], valign="TOP")
RY3 = RY2 + 272 + 20

# --- 状态图例 ---
LEG_H = 988 - RY3
panel(RX, RY3, RW, LEG_H)
L(RX + 24, RY3 + 18, RW - 48, 28, "状态图例", 23, P["t0"], "BOLD", valign="TOP")
LEG = [("开始登机", "green", "登机口已开，%d 分钟内到" % BOARD_LEAD),
       ("最后催促", "rust", "已过截止，立即前往"),
       ("值机开放", "cyan", "可办票，尚未开始登机"),
       ("计划", "dim", "起飞前 %d 分钟开放值机" % CHECKIN_LEAD),
       ("取消", "red", "不再执行，按备注改签"),
       ("登机口变更", "violet", "备注列给出新旧口")]
ly = RY3 + 56
for nm, key, desc in LEG:
    d.chip(RX + 24, ly, 150, 30, nm, P[key], K.hexa(P[key], 0.18), size=17)
    L(RX + 190, ly - 2, RW - 214, 22, desc, 16, P["t1"], valign="TOP")
    ly += 34

# ==================== 主表 ====================
TX = RX + RW + 32
TW = W - TX - 56
COLS = [("计划 STD", 132, "CENTER"), ("预计 ETD", 132, "CENTER"),
        ("航班 FLIGHT", 190, "START"), ("到达城市 DESTINATION", 400, "START"),
        ("飞行", 130, "CENTER"), ("值机", 110, "CENTER"), ("登机口", 130, "CENTER"),
        ("当地时间", 150, "CENTER"), ("状态", 220, "CENTER")]
REMARK_W = TW - sum(c[1] for c in COLS)
RH = 76
TY = 176
d.rect(TX, TY, TW, 52, P["panel2"])
cx = TX
for name, w, alg in COLS:
    if alg == "CENTER":
        C(cx + w / 2.0, TY, w, 52, name, 19, P["t2"], "BOLD", valign="MIDDLE")
    else:
        L(cx + 18, TY, w - 18, 52, name, 19, P["t2"], "BOLD", valign="MIDDLE")
    cx += w
L(cx + 18, TY, REMARK_W - 18, 52, "备注 REMARKS", 19, P["t2"], "BOLD",
  valign="MIDDLE")
d.line(TX, TY + 52, TX + TW, TY + 52, 1, P["border"])

ry = TY + 52
for i, f in enumerate(ROWS):
    key = ST_COLOR[f["st"]]
    if f["st"] == "最后催促":
        d.rect(TX, ry, TW, RH, K.hexa(P["rust"], 0.10))
    elif i % 2 == 0:
        d.rect(TX, ry, TW, RH, "#0A121C")
    d.rect(TX, ry, 8, RH, P[key])
    dim = f["cxl"]
    ink = P["t2"] if dim else P["t0"]
    cx = TX
    # 计划
    struck = f["delay"] > 0
    C(cx + 132 / 2.0, ry, 132, RH, hhmm(f["sched"]), 40,
      P["t2"] if struck else ink, "BOLD", valign="MIDDLE", features="tnum")
    if struck:
        mid = cx + 132 / 2.0
        d.line(mid - 34, ry + RH / 2.0, mid + 34, ry + RH / 2.0, 2, P["amber"])
    cx += 132
    # 预计
    C(cx + 132 / 2.0, ry, 132, RH, hhmm(f["est"]), 40,
      P["amber"] if struck else P["t2"], "BOLD", valign="MIDDLE",
      features="tnum")
    cx += 132
    L(cx + 18, ry, 190 - 18, RH, f["fl"], 32, ink, "BOLD", valign="MIDDLE",
      features="tnum")
    cx += 190
    L(cx + 18, ry + 4, 400 - 18, 38, f["city"], 32, ink, valign="TOP")
    L(cx + 18, ry + 44, 400 - 18, 22, "%s %s · %s" % (f["en"], f["iata"],
      f["air"]), 19, P["t2"], valign="TOP")
    cx += 400
    C(cx + 130 / 2.0, ry, 130, RH, "%dh%02dm" % divmod(f["fly"], 60), 26,
      P["t1"], valign="MIDDLE", features="tnum")
    cx += 130
    C(cx + 110 / 2.0, ry, 110, RH, f["desk"], 30, P["t1"], "BOLD",
      valign="MIDDLE")
    cx += 110
    gc = P["violet"] if f["gate"] != f["oldgate"] else ink
    C(cx + 130 / 2.0, ry, 130, RH, "—" if f["cxl"] else f["gate"], 34, gc,
      "BOLD", valign="MIDDLE")
    cx += 130
    C(cx + 150 / 2.0, ry - 8, 150, 34, hhmm(f["arr"]), 28, P["t1"] if not dim
      else P["t2"], "BOLD", valign="TOP", features="tnum")
    C(cx + 150 / 2.0, ry + 24, 150, 24, "当日" if f["arr_day"] == 0
      else "%+d 日" % f["arr_day"], 16,
      P["amber"] if f["arr_day"] else P["t2"], valign="TOP")
    cx += 150
    d.chip(cx + 20, ry + RH / 2.0 - 20, 180, 40, f["st"], P[key],
           K.hexa(P[key], 0.18), size=22)
    cx += 220
    # 备注
    bx = cx + 18
    if f["gate"] != f["oldgate"]:
        d.chip(bx, ry + RH / 2.0 - 17, 150, 34, "登机口变更", P["violet"],
               K.hexa(P["violet"], 0.18), size=17)
        L(bx + 162, ry, REMARK_W - 180, RH, "%s → %s · %s" % (
            f["oldgate"], f["gate"], f["note"]), 20, P["t1"], valign="MIDDLE")
    else:
        cnt = {"开始登机": "还有 %d 分钟截止" % (f["close"] - NOW),
               "值机开放": "%d 分钟后开始登机" % (f["board"] - NOW),
               "计划": "%d 分钟后开放值机" % (f["open_at"] - NOW),
               "最后催促": "登机口已截止 %d 分钟，请立即前往"
               % (NOW - f["close"])}.get(f["st"], "")
        txt = f["note"] if f["cxl"] else " · ".join([x for x in (cnt, f["note"])
                                                     if x])
        L(bx, ry, REMARK_W - 18, RH, txt, 21, P["t1"], valign="MIDDLE")
    d.line(TX, ry + RH, TX + TW, ry + RH, 1, P["line"])
    ry += RH

# ==================== 底栏 ====================
BY = H - 76
d.rect(0, BY, W, 2, P["border"])
L(56, BY + 18, 900, 30, "登机口于起飞前 %d 分钟关闭；国际航班请预留 %d 分钟"
  "边检与安检时间。" % (CLOSE_LEAD, 90), 21, P["t1"], valign="TOP")
L(1000, BY + 18, 700, 30, "本屏 %d 个航班、%d 个状态全部由同一张表反算，"
  "时刻互相可核对。" % (len(ROWS), len(LIVE)), 21, P["t2"], valign="TOP")
R(W - 56, BY + 14, 900, 34, "数据为虚构演示 · Snapshot DSL 生成 · 更新于 %s"
  % hhmm(NOW), 21, P["t2"], valign="TOP", features="tnum")

dsl = d.dsl()
(OUT / "case10.snapshot").write_text(dsl, encoding="utf-8")
print("canvas %dx%d bytes %d textfit %d %s" % (W, int(d.H), len(dsl),
                                               tf.n, tf.problems[:6]))
print("rows %d live %d cxl %d delay %d avg %.1f ontime %.1f open %d soon %d"
      % (len(ROWS), len(LIVE), N_CXL, N_DELAY, AVG_DELAY, ON_TIME, N_OPEN,
         N_SOON))
for f in ROWS:
    print("  %-9s %-12s std %s est %s arr %s(%+d) %-4s %s" % (
        f["fl"], f["city"], hhmm(f["sched"]), hhmm(f["est"]), hhmm(f["arr"]),
        f["arr_day"], f["st"], f["gate"]))
