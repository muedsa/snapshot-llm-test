"""A05 DSL generator: 实验舱 · 08:00–12:30 三联趋势报告 (1440x1000).

The three charts share one x mapping (PLOT_X / PXPERMIN) and one set of 15-minute reference
lines, so a sample time reads vertically across all panels. Missing samples break the line:
no interpolated or dashed filler is drawn between segments.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A05"
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
D = json.load(open(os.path.join(OUT, "normalized-data.json"), encoding="utf-8"))
VER = sys.argv[1] if len(sys.argv) > 1 else "v1"

CJ = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
BG, CARD = "#F1F5F9FF", "#FFFFFFFF"
INK, INK2, MUTED, MUTED2 = "#0B1220FF", "#1E293BFF", "#5B6B7FFF", "#94A3B8FF"
LINE, NAVY = "#E2E8F0FF", "#0F172AFF"
RED, BLUE, TEAL = "#E11D48FF", "#2563EBFF", "#0E9F8FFF"
AMBER, AMBER_D = "#D97706FF", "#B45309FF"
GAP_FILL, GAP_LINE = "#FEF3C7FF", "#F59E0BFF"

W, H = 1440, 1000
T0, T1 = 480, 750
PLOT_X, PLOT_W = 132, 1266
PXM = PLOT_W / (T1 - T0)


def xof(minute: int) -> float:
    return PLOT_X + (minute - T0) * PXM


def xof_time(t: str) -> float:
    """'HH:MM' -> x. Kept separate from xof so both minute numbers and clock labels work."""
    hh, mm = t.split(":")
    return xof(int(hh) * 60 + int(mm))


def hm(minute: int) -> str:
    return f"{minute // 60:02d}:{minute % 60:02d}"


SER = D["series"]
PANELS = [
    ("temperature_c", 146, 160, 194.0, 18.5, 24.0),
    ("humidity_pct", 314, 160, 194.0, 33.0, 42.0),
    ("pressure_kpa", 482, 160, 194.0, -1.2, 1.5),
]
PT = [0, 30, 90, 195, 230]
GAP_LO, GAP_HI = 580, 650          # 09:40 and 10:50
NEGATIVE_TICKS = [580, 610, 650]

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
    import math
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
box(0, 0, W, 104, NAVY)
box(0, 0, 8, 104, TEAL)
text(40, 14, "实验舱 · 08:00–12:30 三联趋势报告", 34, "#FFFFFFFF", "BOLD")
text(40, 62, "三图共用同一真实时间比例的横轴与同一组纵向参考线（每 15 分钟一条）", 21, "#94A3B8FF")
text(1010, 14, "采样 12 次 · 间隔 10–35 分钟不等", 21, "#5EEAD4FF", "BOLD", CJ, 400, "CENTER_RIGHT")
text(1010, 46, "缺测以 — 表示，线段断开，不补值", 21, "#FBBF24FF", "BOLD", CJ, 400, "CENTER_RIGHT")
text(1010, 76, "压差可正可负，零线清晰", 20, "#94A3B8FF", "NORMAL", CJ, 400, "CENTER_RIGHT")

# legend under the header
LX = 40
for label, col in (("温度 °C", RED), ("相对湿度 %", BLUE), ("压差 kPa", TEAL)):
    box(LX, 122, 16, 16, col, 4)
    text(LX + 24, 118, label, 20, INK2)
    LX += 150
box(LX, 124, 26, 3, "#0F172A55")
text(LX + 34, 118, "零线", 20, INK2)
box(LX + 100, 122, 16, 16, GAP_FILL, 4, f"1 SOLID {GAP_LINE}")
text(LX + 124, 118, "缺测断线区间", 20, INK2)
box(LX + 300, 122, 16, 16, "#FFFFFFFF", 8, f"3 SOLID {MUTED}")
text(LX + 324, 118, "真实采样点", 20, INK2)

# ============================== three aligned panels ==============================
for key, py, ph, _, lo, hi in PANELS:
    st = SER[key]
    unit = st["unit"]
    label = st["label"]
    box(40, py, 1360, ph, CARD, 12, f"1 SOLID {LINE}", "0 2 6 0 #0F172A10 NORMAL")
    text(56, py + 8, f"{label}（{unit}）", 22, INK, "BOLD")
    text(260, py + 12,
         f"有效 {st['valid_count']} / 12 · min {st['min']['value']} {unit} @ {st['min']['time']} · "
         f"max {st['max']['value']} {unit} @ {st['max']['time']}",
         20, MUTED)
    # missing-sample shading runs through every panel (shared time axis)
    box(round(xof(GAP_LO)), py + 30, round(xof(GAP_HI) - xof(GAP_LO)), ph - 34, "#FDE68A44")

    PT_, PB = py + 34, py + ph - 26
    def yof(v, lo=lo, hi=hi, a=PT_, b=PB):
        return b - (v - lo) / (hi - lo) * (b - a)

    # horizontal gridlines + right-edge tick labels
    step = 1.0 if hi - lo <= 4 else 1.0
    n = int(round((hi - lo) / step))
    for i in range(n + 1):
        v = lo + i * step
        gy = round(yof(v))
        is_zero = abs(v) < 1e-9
        col = "#0F172A88" if is_zero else LINE
        add(f'<Positioned left="{PLOT_X}" top="{gy}" width="{PLOT_W}"><Container height="{2 if is_zero else 1}" color="{col}"/></Positioned>')
        txt = f"{v:g}"
        text(PLOT_X - 62, gy - 11, txt, 20, MUTED, "NORMAL", MONO, 54, "CENTER_RIGHT")
    text(PLOT_X - 62, PT_ - 26, f"{unit}", 20, MUTED, "BOLD", CJ, 54, "CENTER_RIGHT")

    # 15-minute vertical reference lines across all panels
    for m in range(T0, T1 + 1, 15):
        gx = round(xof(m))
        hour = (m % 60 == 0)
        add(f'<Positioned left="{gx}" top="{PT_}" width="1" height="{PB-PT_}"><Container color="{"#CBD5E1FF" if hour else "#EEF2F7FF"}"/></Positioned>')

    # negative-span markers inside this panel
    for gx in NEGATIVE_TICKS:
        add(f'<Positioned left="{round(xof(gx))}" top="{PT_}" width="1" height="{PB-PT_}"><Container color="#F59E0B99"/></Positioned>')

    # line segments (broken at missing samples) + individual sample markers
    stroke = {"temperature_c": RED, "humidity_pct": BLUE, "pressure_kpa": TEAL}[key]
    for s in st["segments"]:
        pts = []
        for t in s:
            rec = next(p for p in D["points"] if p["time"] == t)
            pts.append((xof_time(rec["time"]), yof(rec[key])))
        for i in range(len(pts) - 1):
            seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], stroke, 4)
    for p in D["points"]:
        if p[key] is None:
            continue
        cx, cy = xof_time(p["time"]), yof(p[key])
        box(round(cx - 5), round(cy - 5), 10, 10, "#FFFFFFFF", 5, f"3 SOLID {stroke}")

# ============================== summary cards ==============================
SCY, SCH = 650, 78
names = [("温度", "temperature_c", RED), ("相对湿度", "humidity_pct", BLUE), ("压差", "pressure_kpa", TEAL), ("缺测合计", None, AMBER)]
CW2, GAP2 = (1360 - 3 * 16) / 4, 16
for i, (nm, key, col) in enumerate(names):
    x = 40 + i * (CW2 + GAP2)
    box(x, SCY, CW2, SCH, CARD, 12, f"1 SOLID {LINE}", "0 2 6 0 #0F172A10 NORMAL")
    box(x, SCY, CW2, 5, col, tl=12, tr=12)
    text(x + 18, SCY + 16, nm, 21, MUTED, "BOLD")
    if key:
        st = SER[key]
        text(x + 18, SCY + 42, f"有效 {st['valid_count']} / 12", 24, INK, "BOLD", MONO)
        text(x + 180, SCY + 44, f"min {st['min']['value']} · max {st['max']['value']} {st['unit']}", 20, INK2)
        text(x + 18, SCY + 70, f"缺测 {st['missing_count']} 次" + ("（" + "、".join(st["missing_times"]) + "）" if st["missing_times"] else "（无）"),
             20, MUTED2 if not st["missing_times"] else AMBER_D)
    else:
        total = sum(SER[k]["missing_count"] for k in SER)
        text(x + 18, SCY + 42, f"{total} 次", 24, INK, "BOLD", MONO)
        text(x + 150, SCY + 44, "温度 2 次、湿度 1 次、压差 0 次", 20, INK2)
        text(x + 18, SCY + 70, "缺测不按 0 处理", 20, AMBER_D, "BOLD")

# ============================== detail table ==============================
TX, TY, TW = 40, SCY + SCH + 10, 1360
HY = TY + 24
ROWH = 18
N = len(D["points"])
FY = HY + N * ROWH + 2
TH = FY + 24 - TY
box(TX, TY, TW, TH, CARD, 12, f"1 SOLID {LINE}", "0 2 6 0 #0F172A10 NORMAL")
text(TX + 18, TY + 8, "全部 12 个时点明细", 21, INK, "BOLD")
text(TX + 230, TY + 10, "缺测以 — 表示；数值与上图逐点一致", 20, MUTED)
add(f'<Positioned left="{TX+12}" top="{HY}" width="{TW-24}"><Container height="1" color="#CBD5E1FF"/></Positioned>')
COLS = [("时点", 30, 150, "LEFT"), ("偏移（min）", 170, 330, "RIGHT"),
        ("温度 °C", 360, 540, "RIGHT"), ("湿度 %", 570, 750, "RIGHT"),
        ("压差 kPa", 780, 960, "RIGHT"), ("采样间隔", 1000, 1180, "RIGHT"),
        ("该点缺测", 1210, 1330, "LEFT")]
for name, xl, xr, al in COLS:
    if al == "RIGHT":
        text(TX + xl, HY - 24, name, 20, MUTED, "BOLD", CJ, xr - xl, "CENTER_RIGHT")
    else:
        text(TX + xl, HY - 24, name, 20, MUTED, "BOLD")
for i, p in enumerate(D["points"]):
    ry = HY + 2 + i * ROWH
    if i % 2 == 1:
        box(TX + 12, ry - 2, TW - 24, ROWH - 1, "#F8FAFCFF", 5)
    prev = D["points"][i - 1] if i else None
    gap = f"+{p['offset_min'] - prev['offset_min']} min" if prev else "—"
    missing = [n for k, n in (("temperature_c", "温度"), ("humidity_pct", "湿度"), ("pressure_kpa", "压差"))
               if p[k] is None]
    vals = [
        (p["time"], INK, "BOLD", MONO),
        (f"{p['offset_min']}", INK2, "NORMAL", MONO),
        (f"{p['temperature_c']:.1f}" if p["temperature_c"] is not None else "—",
         RED if p["temperature_c"] is None else INK, "BOLD" if p["temperature_c"] is None else "NORMAL", MONO),
        (f"{p['humidity_pct']:.0f}" if p["humidity_pct"] is not None else "—",
         BLUE if p["humidity_pct"] is None else INK, "BOLD" if p["humidity_pct"] is None else "NORMAL", MONO),
        (f"{p['pressure_kpa']:+.1f}", AMBER_D if p["pressure_kpa"] < 0 else INK, "BOLD" if p["pressure_kpa"] < 0 else "NORMAL", MONO),
        (gap, MUTED, "NORMAL", MONO),
        ("、".join(missing) + " 缺测" if missing else "—", AMBER_D if missing else MUTED2, "BOLD" if missing else "NORMAL", CJ),
    ]
    for (name, xl, xr, al), (s, col, wt, fam) in zip(COLS, vals):
        if al == "RIGHT":
            text(TX + xl, ry, s, 20, col, wt, fam, xr - xl, "CENTER_RIGHT")
        else:
            text(TX + xl, ry, s, 20, col, wt, fam)

# ============================== conclusion / footnote ==============================
CY = FY + 30
box(40, CY, 1360, 62, NAVY, 10)
add(f'<Positioned left="40" top="{CY}"><Container width="6" height="62" color="{AMBER}" '
    f'borderRadiusTopLeft="10" borderRadiusBottomLeft="10"/></Positioned>')
text(58, CY + 8, "读图要点", 21, "#5EEAD4FF", "BOLD")
text(150, CY + 7, "压差的负值出现在 09:40、10:10、10:50 三个实际采样点（图中琥珀色竖线与浅黄区间标出），不表示 09:40–10:50 的每一刻都为负。",
     21, "#F8FAFCFF", "BOLD")
text(150, CY + 36, "温度在 09:15 与 11:40 缺测、湿度在 09:40 缺测，对应线段断开为 " +
     f"{SER['temperature_c']['segment_count']} 段与 {SER['humidity_pct']['segment_count']} 段；压差 12 点齐全，连为一段。",
     21, "#E2E8F0FF")

text(40, CY + 82, "口径：空单元格 = 缺测（null），不按 0 处理，不插值、不平滑、不用虚线补值；横轴为真实时间比例（08:00–12:30 共 270 分钟）；单位：温度 °C、相对湿度 %、压差 kPa。",
     20, MUTED)
text(1080, CY + 82, "渲染：Snapshot DSL · 1440×1000", 20, MUTED2, "NORMAL", MONO, 320, "CENTER_RIGHT")

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
      f"{PANELS[2][1]}..{PANELS[2][1]+PANELS[2][2]} | cards {SCY}..{SCY+SCH} | table {TY}..{TY+TH} | footer {CY+82+24}")
assert PANELS[-1][1] + PANELS[-1][2] < SCY, "panels overlap cards"
assert SCY + SCH < TY, "cards overlap table"
assert CY + 82 + 24 < H, f"footnote leaves the canvas ({CY + 106})"
print("vertical budget OK")
