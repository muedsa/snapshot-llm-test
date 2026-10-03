"""A05 DSL generator: 实验舱 · 08:00–12:30 三联趋势报告 (1440x1000).

All three charts share one x mapping and one set of 15-minute reference lines, so a sample
reads vertically across panels. Missing samples break the line - no interpolated or dashed
filler is drawn. Vertical budget is solved explicitly (see the asserts at the bottom)
because the sheet must also carry a summary row and a 12-row table.
"""
from __future__ import annotations

import json
import math
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A05"
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
D = json.load(open(os.path.join(OUT, "normalized-data.json"), encoding="utf-8"))
VER = sys.argv[1] if len(sys.argv) > 1 else "final"

CJ = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
BG, CARD = "#F1F5F9FF", "#FFFFFFFF"
INK, INK2, MUTED, MUTED2 = "#0B1220FF", "#1E293BFF", "#5B6B7FFF", "#94A3B8FF"
LINE, NAVY = "#E2E8F0FF", "#0F172AFF"
RED, BLUE, TEAL = "#E11D48FF", "#2563EBFF", "#0E9F8FFF"
AMBER, AMBER_D = "#D97706FF", "#B45309FF"
COLOR = {"temperature_c": RED, "humidity_pct": BLUE, "pressure_kpa": TEAL}

W, H = 1440, 1000
T0, T1 = 480, 750
PLOT_X, PLOT_W = 128, 1270
PXM = PLOT_W / (T1 - T0)


def xof(minute: int) -> float:
    return PLOT_X + (minute - T0) * PXM


def xof_time(t: str) -> float:
    hh, mm = t.split(":")
    return xof(int(hh) * 60 + int(mm))


SER = D["series"]
PTS = D["points"]

# (key, top_y, height, plot_top, plot_bottom, axis_min, axis_max, grid values)
PANELS = [
    ("temperature_c", 124, 90, 148, 182, 18.0, 24.5, [20, 22, 24]),
    ("humidity_pct", 218, 90, 242, 276, 33.0, 42.0, [34, 38, 42]),
    ("pressure_kpa", 312, 90, 336, 370, -1.2, 1.5, [-1.0, 0.0, 1.0]),
]
GAP_LO, GAP_HI = 580, 650
NEGATIVE_TICKS = [580, 610, 650]
TIME_AXIS_Y = 372

P: list[str] = []
add = P.append


def box(x, y, w, h, color, radius=None, border=None, shadow=None, tl=None, tr=None, bl=None, br=None):
    a = f'<Container width="{w}" height="{h}" color="{color}"'
    if radius:
        a += f' borderRadius="{radius}"'
    for n, v in (("TopLeft", tl), ("TopRight", tr), ("BottomLeft", bl), ("BottomRight", br)):
        if v:
            a += f' borderRadius{n}="{v}"'
    if border:
        a += f' border="{border}"'
    if shadow:
        a += f' boxShadow="{shadow}"'
    add(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')


def text(x, y, s, size, color, weight="NORMAL", family=CJ, w=None, align="CENTER_LEFT"):
    a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
    body = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if w:
        add(f'<Positioned left="{x}" top="{y}" width="{w}"><Container alignment="{align}">'
            f'<Text {a}>{body}</Text></Container></Positioned>')
    else:
        add(f'<Positioned left="{x}" top="{y}"><Text {a}>{body}</Text></Positioned>')


def seg(x0, y0, x1, y1, color, th):
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)
    m11, m12 = math.cos(ang), math.sin(ang)
    m21, m22 = -m12, m11
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    tx = mx - m11 * (length / 2) - m21 * (th / 2)
    ty = my - m12 * (length / 2) - m22 * (th / 2)
    mat = f"(1,0,0,0,0,1,0,0,0,0,1,0,{tx:.3f},{ty:.3f},0,1)"
    add(f'<Positioned left="0" top="0"><Transform matrix="{mat}"><Container width="{length:.2f}" '
        f'height="{th}" color="{color}" borderRadius="{th/2}"/></Transform></Positioned>')


add(f'<Snapshot background="{BG}" type="png">')
add(f'<Container width="{W}" height="{H}">')
add('<Stack alignment="TOP_LEFT" fit="EXPAND">')

# ============================== header ==============================
box(0, 0, W, 92, NAVY)
box(0, 0, 8, 92, TEAL)
text(40, 12, "实验舱 · 08:00–12:30 三联趋势报告", 32, "#FFFFFFFF", "BOLD")
text(40, 58, "三图共用同一真实时间比例的横轴与同一组纵向参考线（每 15 分钟一条）", 20, "#94A3B8FF")
text(1000, 12, "采样 12 次 · 间隔 10–35 分钟", 20, "#5EEAD4FF", "BOLD", CJ, 400, "CENTER_RIGHT")
text(1000, 40, "缺测以 — 表示，线段断开，不补值", 20, "#FBBF24FF", "BOLD", CJ, 400, "CENTER_RIGHT")
text(1000, 66, "压差可正可负，零线清晰", 20, "#94A3B8FF", "NORMAL", CJ, 400, "CENTER_RIGHT")

LX = 40
for label, col in (("温度 °C", RED), ("相对湿度 %", BLUE), ("压差 kPa", TEAL)):
    box(LX, 102, 14, 14, col, 4)
    text(LX + 22, 98, label, 20, INK2)
    LX += 138
box(LX, 104, 24, 3, "#0F172A55")
text(LX + 32, 98, "零线", 20, INK2)
box(LX + 96, 102, 14, 14, "#FDE68AFF", 4, f"1 SOLID {AMBER}")
text(LX + 118, 98, "缺测断线区间 / 压差负值区段", 20, INK2)
box(LX + 396, 102, 14, 14, "#FFFFFFFF", 7, f"3 SOLID {MUTED}")
text(LX + 418, 98, "真实采样点", 20, INK2)

# ============================== three aligned panels ==============================
for key, py, ph, pt_, pb, lo, hi, grid in PANELS:
    st = SER[key]
    unit = st["unit"]

    def yof(v, lo=lo, hi=hi, a=pt_, b=pb):
        return b - (v - lo) / (hi - lo) * (b - a)

    box(40, py, 1360, ph, CARD, 12, f"1 SOLID {LINE}", "0 2 6 0 #0F172A10 NORMAL")
    text(56, py + 6, f"{st['label']}（{unit}）", 21, INK, "BOLD")
    text(250, py + 9,
         f"有效 {st['valid_count']} / 12 · min {st['min']['value']}{unit} @ {st['min']['time']}"
         f" · max {st['max']['value']}{unit} @ {st['max']['time']} · 连接段 {st['segment_count']} 段",
         20, MUTED)

    # missing-sample span + negative-pressure span, drawn through every panel
    box(round(xof(GAP_LO)), pt_ - 12, round(xof(GAP_HI) - xof(GAP_LO)), pb - pt_ + 16, "#FDE68A44")

    for v in grid:
        gy = round(yof(v))
        is_zero = abs(v) < 1e-9
        add(f'<Positioned left="{PLOT_X}" top="{gy}" width="{PLOT_W}"><Container height="{2 if is_zero else 1}" color="{"#0F172A88" if is_zero else LINE}"/></Positioned>')
        text(PLOT_X - 60, gy - 11, f"{v:g}", 20, MUTED, "NORMAL", MONO, 52, "CENTER_RIGHT")
    text(PLOT_X - 60, pt_ - 26, unit, 20, MUTED, "BOLD", CJ, 52, "CENTER_RIGHT")

    for m in range(T0, T1 + 1, 15):
        gx = round(xof(m))
        hour = (m % 60 == 0)
        add(f'<Positioned left="{gx}" top="{pt_}" width="1" height="{pb-pt_}"><Container color="{"#CBD5E1FF" if hour else "#EEF2F7FF"}"/></Positioned>')
    for gx in NEGATIVE_TICKS:
        add(f'<Positioned left="{round(xof(gx))}" top="{pt_}" width="1" height="{pb-pt_}"><Container color="#F59E0B99"/></Positioned>')

    stroke = COLOR[key]
    for s in st["segments"]:
        pts = [(xof_time(t), yof(next(p[key] for p in PTS if p["time"] == t))) for t in s]
        for i in range(len(pts) - 1):
            seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], stroke, 4)
    for p in PTS:
        if p[key] is None:
            continue
        cx, cy = xof_time(p["time"]), yof(p[key])
        box(round(cx - 5), round(cy - 5), 10, 10, "#FFFFFFFF", 5, f"3 SOLID {stroke}")

# time axis under the pressure panel (the three panels share it)
for m in range(T0, T1 + 1, 30):
    gx = round(xof(m))
    text(gx - 34, TIME_AXIS_Y, f"{m//60:02d}:{m%60:02d}", 20, INK2, "BOLD", MONO, 68, "CENTER_LEFT")

# ============================== summary row ==============================
SCY, SCH = 412, 68
names = [("温度", "temperature_c", RED), ("相对湿度", "humidity_pct", BLUE),
         ("压差", "pressure_kpa", TEAL), ("缺测合计", None, AMBER)]
CW2, GAP2 = (1360 - 3 * 14) / 4, 14
for i, (nm, key, col) in enumerate(names):
    x = 40 + i * (CW2 + GAP2)
    box(x, SCY, CW2, SCH, CARD, 12, f"1 SOLID {LINE}", "0 2 6 0 #0F172A10 NORMAL")
    box(x, SCY, CW2, 5, col, tl=12, tr=12)
    text(x + 16, SCY + 13, nm, 20, MUTED, "BOLD")
    if key:
        st = SER[key]
        text(x + 16, SCY + 34, f"有效 {st['valid_count']} / 12", 22, INK, "BOLD", MONO)
        text(x + 16, SCY + 58, f"min {st['min']['value']} · max {st['max']['value']} {st['unit']}", 20, INK2)
    else:
        total = sum(SER[k]["missing_count"] for k in SER)
        text(x + 16, SCY + 34, f"{total} 次", 22, INK, "BOLD", MONO)
        text(x + 16, SCY + 58, "温度 2 · 湿度 1 · 压差 0；不按 0 处理", 20, AMBER_D, "BOLD")

# ============================== detail table ==============================
TX, TY, TW = 40, SCY + SCH + 14, 1360
HY = TY + 50
ROWH = 21
N = len(PTS)
FY = HY + N * ROWH + 2
TH = FY + 22 - TY
box(TX, TY, TW, TH, CARD, 12, f"1 SOLID {LINE}", "0 2 6 0 #0F172A10 NORMAL")
text(TX + 16, TY + 7, "全部 12 个时点明细", 20, INK, "BOLD")
text(TX + 200, TY + 8, "缺测以 — 表示；数值与上图逐点一致", 20, MUTED)
add(f'<Positioned left="{TX+12}" top="{HY}" width="{TW-24}"><Container height="1" color="#CBD5E1FF"/></Positioned>')
COLS = [("时点", 30, 130, "LEFT"), ("偏移 min", 150, 280, "RIGHT"),
        ("温度 °C", 310, 450, "RIGHT"), ("湿度 %", 480, 620, "RIGHT"),
        ("压差 kPa", 650, 790, "RIGHT"), ("间隔 min", 820, 950, "RIGHT"),
        ("该点缺测", 980, 1160, "LEFT")]
for name, xl, xr, al in COLS:
    if al == "RIGHT":
        text(TX + xl, HY - 24, name, 18, MUTED, "BOLD", CJ, xr - xl, "CENTER_RIGHT")
    else:
        text(TX + xl, HY - 24, name, 18, MUTED, "BOLD")
for i, p in enumerate(PTS):
    ry = HY + 26 + i * ROWH
    if i % 2 == 1:
        box(TX + 12, ry - 3, TW - 24, ROWH - 1, "#F8FAFCFF", 5)
    prev = PTS[i - 1] if i else None
    gap = f"+{p['offset_min'] - prev['offset_min']}" if prev else "—"
    missing = [n for k, n in (("temperature_c", "温度"), ("humidity_pct", "湿度"), ("pressure_kpa", "压差"))
               if p[k] is None]
    vals = [
        (p["time"], INK, "BOLD", MONO),
        (f"{p['offset_min']}", INK2, "NORMAL", MONO),
        (f"{p['temperature_c']:.1f}" if p["temperature_c"] is not None else "—",
         RED if p["temperature_c"] is None else INK, "BOLD" if p["temperature_c"] is None else "NORMAL", MONO),
        (f"{p['humidity_pct']:.0f}" if p["humidity_pct"] is not None else "—",
         BLUE if p["humidity_pct"] is None else INK, "BOLD" if p["humidity_pct"] is None else "NORMAL", MONO),
        (f"{p['pressure_kpa']:+.1f}", AMBER_D if p["pressure_kpa"] < 0 else INK,
         "BOLD" if p["pressure_kpa"] < 0 else "NORMAL", MONO),
        (gap, MUTED, "NORMAL", MONO),
        ("、".join(missing) if missing else "—", AMBER_D if missing else MUTED2, "BOLD" if missing else "NORMAL", CJ),
    ]
    for (name, xl, xr, al), (s, col, wt, fam) in zip(COLS, vals):
        if al == "RIGHT":
            text(TX + xl, ry, s, 17, col, wt, fam, xr - xl, "CENTER_RIGHT")
        else:
            text(TX + xl, ry, s, 20, col, wt, fam)

# ============================== reading notes + footnote ==============================
CY = TY + TH + 10
box(40, CY, 1360, 54, NAVY, 10)
add(f'<Positioned left="40" top="{CY}"><Container width="6" height="54" color="{AMBER}" '
    f'borderRadiusTopLeft="10" borderRadiusBottomLeft="10"/></Positioned>')
text(56, CY + 6, "读图要点", 20, "#5EEAD4FF", "BOLD")
text(146, CY + 5, "压差负值出现在 09:40、10:10、10:50 三个实际采样点（琥珀竖线与浅黄区间标出），不表示 09:40–10:50 每一刻都为负。",
     20, "#F8FAFCFF", "BOLD")
text(146, CY + 29, f"温度 09:15、11:40 缺测断成 {SER['temperature_c']['segment_count']} 段；湿度 09:40 缺测断成 "
     f"{SER['humidity_pct']['segment_count']} 段；压差 12 点齐全，连为 1 段。",
     20, "#E2E8F0FF")

text(40, CY + 62, "口径：空单元格 = 缺测（null），不按 0 处理，不插值、不平滑、不用虚线补值。", 20, MUTED)
text(40, CY + 86, "横轴为真实时间比例（08:00–12:30 共 270 分钟）；单位：温度 °C、相对湿度 %、压差 kPa。", 20, MUTED)
text(1120, CY + 86, "渲染：Snapshot DSL · 1440×1000", 20, MUTED2, "NORMAL", MONO, 280, "CENTER_RIGHT")

add('</Stack>')
add('</Container>')
add('</Snapshot>')

dsl = "\n".join(P) + "\n"
os.makedirs(TMP, exist_ok=True)
p = os.path.join(TMP, f"sensor-report.{VER}.snapshot")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)

print(p, len(dsl), "chars")
print(f"panels {PANELS[0][1]}..{PANELS[0][1]+PANELS[0][2]} / {PANELS[1][1]}..{PANELS[1][1]+PANELS[1][2]} / "
      f"{PANELS[2][1]}..{PANELS[2][1]+PANELS[2][2]} | axis 468 | cards {SCY}..{SCY+SCH} | "
      f"table {TY}..{TY+TH} | notes {CY}..{CY+62} | footnote {CY+70+24}")
assert PANELS[-1][1] + PANELS[-1][2] < SCY, "panels overlap cards"
assert SCY - TIME_AXIS_Y >= 26, "time axis row needs room"
assert SCY + SCH < TY, "cards overlap table"
assert CY + 86 + 24 < H, f"footnote leaves the canvas ({CY + 110})"
print("vertical budget OK")
