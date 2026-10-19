# -*- coding: utf-8 -*-
"""A05 · 不规则采样与缺测的仪表报告（实验舱 08:00–12:30 三联趋势）。
数据源：tasks/A05-irregular-sensors/inputs/readings.csv（12 时点，真实读值，空=缺测 null）。
产出（路径基准 = 本题输出根 outputs/<run_id>/A05/）：
  sensor-report.snapshot / normalized-data.json（visual_checks 由查看后 finalize_audit.py 填写）

画布 1440×1000 布局：
  标题带（题 + 徽标 + 副题）→ 3 概要 chips（有效数 + 观察最小/最大）→ 图例行 y176
  → 三联图表卡 (64,214)-(1376,734)：三面板纵排，共享 08:00–12:30 真实分钟比例横轴
     x(t)=110 + t×1232/270；每 30 分钟竖参考线贯穿三联（252..702）
     p1 温度 19–24 °C：y = 370 − 23.6(v−19)
     p2 相对湿度 30–45 %：y = 536 − 7.86667(v−30)
     p3 压差 −1 – 1.5 kPa：y = 702 − 47.2(v+1)，零线 y=654.8 强调
     负压实际采样区段 09:40–10:50（band = x(100)..x(170)），只标实际采样，不外推
  → 全部 12 时点双栏简表（缺测 “—”，非 0）

连线手段（默认 39 标签无 Paint/Stroke）：线段 = ClipPath 填充四边形（文档示例
SizedBox>ClipPath>Container），圆点 = ClipOval 双层圆环，缺测菱形 = ClipPath 多边形环。
缺测时点两侧样本不跨接（不能用直线/虚线补值），线在缺测处断开。
"""
import json
import os
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = TASK_ROOT / "outputs" / RUN_ID / "A05"
OUT.mkdir(parents=True, exist_ok=True)
TMP = TASK_ROOT / "tmp" / RUN_ID / "A05"
TMP.mkdir(parents=True, exist_ok=True)

FONT = "Noto Sans CJK SC"
FN = "Inter"
FAM_MIX = FN + "," + FONT

# =====================================================================
# 原始数据（tasks/A05-irregular-sensors/inputs/readings.csv，逐行原值）
# =====================================================================
RAW = [
    # (time, temperature_c, humidity_pct, pressure_kpa)  None = 缺测
    ("08:00", 19.2, 41, 0.2),
    ("08:10", 19.6, 40, 0.4),
    ("08:35", 20.1, 39, 0.7),
    ("09:00", 21.0, 38, 1.1),
    ("09:15", None, 37, 1.3),
    ("09:40", 21.9, None, -0.2),
    ("10:10", 22.3, 35, -0.8),
    ("10:50", 23.1, 34, -0.3),
    ("11:00", 22.8, 35, 0.1),
    ("11:40", None, 36, 0.6),
    ("12:10", 22.0, 37, 0.3),
    ("12:30", 21.7, 38, 0.0),
]

METRICS = [
    ("temperature_c", "温度", "°C", "① ",
     {"light": "#BED8FC", "main": "#2E90FA"}),
    ("humidity_pct", "相对湿度", "%", "②",
     {"light": "#F5D48A", "main": "#F59E0B"}),
    ("pressure_kpa", "压差", "kPa", "③",
     {"light": "#C9B4F5", "main": "#7C3AED"}),
]
MISSING_RANGE = {}   # 校验观察最小/最大与已知范围一致
EXPECT = {
    "temperature_c": (10, 19.2, 23.1),
    "humidity_pct": (11, 34, 41),
    "pressure_kpa": (12, -0.8, 1.3),
}
for _, key in [(m[0], m[1]) for m in METRICS]:
    pass
vals = {m[0]: [r[i] for r in RAW] for m, i in
        zip(METRICS, (1, 2, 3))}
for (key, _, _, _, _), i in zip(METRICS, (1, 2, 3)):
    col = [r[i] for r in RAW]
    vv = [v for v in col if v is not None]
    valid, mn, mx = EXPECT[key]
    assert len(vv) == valid, (key, len(vv), valid)
    assert min(vv) == mn and max(vv) == mx, (key, min(vv), max(vv))
TIME0 = "08:00"
SPANN = 270
assert [r[0] for r in RAW] == [
    "08:00", "08:10", "08:35", "09:00", "09:15", "09:40",
    "10:10", "10:50", "11:00", "11:40", "12:10", "12:30"], [r[0] for r in RAW]
OFFS = [0, 10, 35, 60, 75, 100, 130, 170, 180, 220, 250, 270]
assert OFFS[-1] == SPANN
NEG = [(i, OFFS[i], RAW[i][3]) for i in range(12) if RAW[i][3] is not None and RAW[i][3] < 0]
assert NEG == [(5, 100, -0.2), (6, 130, -0.8), (7, 170, -0.3)], NEG

# =====================================================================
# 文本轮宽估计（保守；CJK=1.0em，Inter 数字≈0.60em）；超限即失败退出
# =====================================================================
def estw(s: str, size: float) -> float:
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o < 0x80:
            if ch == " ":
                w += 0.30 * size
            elif ch in ":.,~":
                w += 0.30 * size
            elif ch == "·":
                w += 0.35 * size
            elif ch in "/／":
                w += 0.55 * size
            elif ch in "—–…→↑↓":
                w += 1.00 * size
            elif ch in "−=+":
                w += 0.60 * size
            elif ch == "%":
                w += 0.60 * size
            elif ch == "°":
                w += 0.50 * size
            elif ch.isdigit():
                w += 0.60 * size
            elif ch.isupper():
                w += 0.70 * size
            else:
                w += 0.54 * size
        else:
            w += 1.00 * size  # CJK / 全角
    return w

WARN = []

def fit(label, s, size, box_w):
    w = estw(s, size)
    if w > box_w:
        WARN.append(f"{label}: estw({w:.1f}) > box {box_w} :: {s}")

# =====================================================================
# DSL 发射器（扁平 Stack + 画布绝对坐标；A01–A04 验证过的模式）
# =====================================================================
def fnum(v) -> str:
    s = f"{float(v):.2f}".rstrip("0").rstrip(".")
    return s if s else "0"

def rect(x, y, w, h, color=None, radius=None, border=None):
    a = f'<Container width="{fnum(w)}" height="{fnum(h)}"'
    if color:
        a += f' color="{color}"'
    if radius is not None and radius > 0:
        a += f' borderRadius="{fnum(radius)}"'
    if border:
        a += f' border="{border}"'
    return (f'<Positioned left="{fnum(x)}" top="{fnum(y)}"'
            f' width="{fnum(w)}" height="{fnum(h)}">' + a + " /></Positioned>")

def text(x, y, content, size, color, family=FONT, bold=False, align="START", box_w=None):
    lx, ly = fnum(x), fnum(y)
    sty = f'<Text fontSize="{fnum(size)}" color="{color}" fontFamily="{family}"'
    if bold:
        sty += ' fontStyle="BOLD"'
    sty += ' maxLines="1" overflow="CLIP"'
    if align != "START":
        sty += f' textAlign="{align}"'
    sty += f'>{content}</Text>'
    if box_w is None:
        return f'<Positioned left="{lx}" top="{ly}">{sty}</Positioned>'
    return f'<Positioned left="{lx}" top="{ly}" width="{fnum(box_w)}">{sty}</Positioned>'

def polygon(pts, color):
    """任意凸多边形填充：ClipPath(SVG d) + Container（文档 Shape 示例模式）。"""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = min(xs), min(ys)
    w = max(xs) - x0
    h = max(ys) - y0
    if w < 0.5 or h < 0.5:
        WARN.append(f"polygon 太小 {pts}")
        return None
    d = "M " + " L ".join(f"{fnum(px - x0)} {fnum(py - y0)}" for px, py in pts) + " Z"
    return (f'<Positioned left="{fnum(x0)}" top="{fnum(y0)}"'
            f' width="{fnum(w)}" height="{fnum(h)}">'
            f'<SizedBox width="{fnum(w)}" height="{fnum(h)}">'
            f'<ClipPath path="{d}"><Container color="{color}" /></ClipPath>'
            f'</SizedBox></Positioned>')

def quad(p1, p2, color, thick=3.5):
    """线段 = 沿段方向加半宽法向偏移的四边形填充。"""
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    import math
    L = math.hypot(dx, dy)
    if L == 0:
        WARN.append("零长线段")
        return None
    nx, ny = dy / L, -dx / L
    hw = thick / 2
    pts = [(x1 + nx * hw, y1 + ny * hw), (x2 + nx * hw, y2 + ny * hw),
           (x2 - nx * hw, y2 - ny * hw), (x1 - nx * hw, y1 - ny * hw)]
    return polygon(pts, color)

def oval(x, y, d, color):
    """ClipOval 圆点：外层 d、内层自适应（双层调用形成圆环）。"""
    r = d / 2
    return (f'<Positioned left="{fnum(x - r)}" top="{fnum(y - r)}"'
            f' width="{fnum(d)}" height="{fnum(d)}">'
            f'<SizedBox width="{fnum(d)}" height="{fnum(d)}">'
            f'<ClipOval><Container color="{color}" /></ClipOval>'
            f'</SizedBox></Positioned>')

def marker(x, y, color, d=14, hole=6):
    return oval(x, y, d, color) + oval(x, y, hole, "#FFFFFF")

def diamond_ring(x, y, color, outer=7, inner=3.2):
    s1 = polygon([(x, y - outer), (x + outer, y), (x, y + outer), (x - outer, y)], color)
    s2 = polygon([(x, y - inner), (x + inner, y), (x, y + inner), (x - inner, y)], "#FFFFFF")
    return s1 + s2

def snapshot(bg, items):
    return ('<Snapshot background="' + bg + '" type="png">\n<Stack>\n'
            + "\n".join(items) + "\n</Stack>\n</Snapshot>\n")

# =====================================================================
# 画布与配色
# =====================================================================
W, H = 1440, 1000
BG = "#F3F6FB"; INK = "#17233D"; SUB = "#55657F"; FAINT = "#8494AE"
CARD = "#FFFFFF"; BORD = "1 SOLID #E3EAF4"; GRID = "#E1E8F3"; AXIS = "#B9C6D8"
ZERO = "#94A3B8"; ZEBRA = "#F4F7FC"
BAND = "#FDECEC"; BAND_ED = "#F1A7A7"; NEG_TX = "#B42318"

CX, CY, CW, CH = 64, 214, 1312, 520        # 图表卡
TROW = {"cx": 64, "cy": 742, "w": 1312, "h": 246}   # 表格卡

# 共享横轴
PX_MIN = 1232 / 270                        # 4.56296 px/min
X0 = 110.0

def xof(minutes):
    return X0 + minutes * PX_MIN

S = [f'<SizedBox width="{W}" height="{H}" />']
GEO = {}

# ---------------------------------------------------------------- 标题带
title = "实验舱 · 08:00–12:30 不规则采样三联趋势"
fit("标题", title, 34, 1312)
S.append(text(64, 16, title, 34, INK, family=FAM_MIX, bold=True))
badge = "12 时点 · 间隔 10–40 分钟"
fit("徽标", badge, 18, 376)
S.append(text(1000, 24, badge, 18, SUB, family=FAM_MIX, align="END", box_w=376))
subtitle = "温度（°C）、相对湿度（%）、压差（kPa）三联合轴；横轴为 08:00–12:30 真实分钟比例，空白＝缺测（非 0），断线不插值。"
fit("副题", subtitle, 20, 1312)
S.append(text(64, 60, subtitle, 20, SUB, family=FAM_MIX))

# ---------------------------------------------------------------- chips
CHIPS = [
    ("温度", "10/12 有效 · 19.2 ~ 23.1 °C", METRICS[0][4]["main"]),
    ("湿度", "11/12 有效 · 34 ~ 41 %", METRICS[1][4]["main"]),
    ("压差", "12/12 有效 · −0.8 ~ 1.3 kPa", METRICS[2][4]["main"]),
]
chi_xs = (64, 512, 960)
chi_ws = (424, 424, 416)
for (name, val, col), cx, cwd in zip(CHIPS, chi_xs, chi_ws):
    S.append(rect(cx, 96, cwd, 44, CARD, 10, BORD))
    S.append(oval(cx + 22, 118, 12, col))
    label = f"{name}  {val}"
    fit(f"chip{name}", label, 20, cwd - 44)
    S.append(text(cx + 32, 105, label, 20, INK, family=FAM_MIX, bold=True))

# ---------------------------------------------------------------- 图例（缺测与断线）
LEG_Y = 176
leg_items = []
LEG_ENTRIES = [
    ("dots", "真实读数（圆点）"),
    ("diamond", "缺测时点（断线不补值）"),
    ("vline", "30 分钟参考线（三联合轴）"),
    ("band", "压差为负的实际采样区段（间隔时刻未采样）"),
]
lx = 64.0
GLYP = 14
for kind, lab in LEG_ENTRIES:
    if kind == "dots":
        S.append(oval(lx + 5, LEG_Y + 11, 10, METRICS[0][4]["main"]))
        S.append(oval(lx + 15, LEG_Y + 11, 10, METRICS[1][4]["main"]))
        S.append(oval(lx + 25, LEG_Y + 11, 10, METRICS[2][4]["main"]))
        tx, gw = lx + GLYP * 3 + 4, GLYP * 3
    elif kind == "diamond":
        S.append(diamond_ring(lx + 7, LEG_Y + 11, SUB))
        tx, gw = lx + GLYP + 6, GLYP
    elif kind == "vline":
        S.append(rect(lx + 6, LEG_Y + 5, 2, 12, AXIS))
        tx, gw = lx + GLYP + 6, GLYP
    else:
        S.append(rect(lx, LEG_Y + 6, 16, 10, BAND, border="1 SOLID " + BAND_ED))
        tx, gw = lx + 20 + 4, 20
    tw = estw(lab, 18)
    leg_items.append({"kind": kind, "label": lab, "x": round(lx, 2),
                      "text_x": round(tx, 2), "text_w": round(tw, 2)})
    S.append(text(tx, LEG_Y, lab, 18, SUB, family=FAM_MIX))
    lx = tx + tw + 30
LEG_TOTAL = lx - 30 - 64
GEO["legend_total_w"] = round(LEG_TOTAL, 2)
if LEG_TOTAL > 1312:
    WARN.append(f"图例总宽 {LEG_TOTAL:.0f} > 1312")

# ---------------------------------------------------------------- 三联面板几何
BAND_Y = {"p1": (252, 370), "p2": (418, 536), "p3": (584, 702)}

def y1(v): return 370 - 23.6 * (v - 19)
def y2(v): return 536 - 7.86667 * (v - 30)
def y3(v): return 702 - 47.2 * (v + 1)

S.append(rect(CX, CY, CW, CH, CARD, 16, BORD))

# 负压实际采样区段（先画在最底，只在 p3）
nbx0, nbx1 = xof(100), xof(170)
S.append(rect(nbx0, 584, nbx1 - nbx0, 118, BAND))
S.append(rect(nbx0, 584, 1, 118, BAND_ED))
S.append(rect(nbx1 - 1, 584, 1, 118, BAND_ED))

# 三联贯穿的竖参考线（每 30 分钟；先画，供三个面板对齐）
REF_X = []
for t in range(0, 271, 30):
    gx = xof(t)
    REF_X.append({"minutes": t, "x": round(gx, 2)})
    S.append(rect(gx, 252, 1, 450, GRID))
GEO["vertical_ref_lines"] = REF_X

HEADS = [
    ("① 温度（°C）", "缺测 09:15 · 11:40 → 两处断线", 220),
    ("② 相对湿度（%）", "缺测 09:40 → 一处断线", 374),
    ("③ 压差（kPa）", "12 个时点全有效 · 三点为负（浅红区段）", 540),
]
for htxt, note, hy in HEADS:
    fit("面板头", htxt, 20, 300)
    S.append(text(110, hy, htxt, 20, INK, family=FAM_MIX, bold=True))
    fit("面板注", note, 18, 470)
    S.append(text(872, hy + 2, note, 18, FAINT, family=FAM_MIX,
                  align="END", box_w=470))

# ---- 横网格 + 纵轴刻度（独立单位与比例）
def hgrid(y, color=GRID, h=1, x_from=110, x_to=1342):
    S.append(rect(x_from, y, x_to - x_from, h, color))

# p1 温度：基线 19（AXIS 实线）；细网格 20–24；标注 20/22/24
for v in (20, 21, 22, 23, 24):
    if v in (20, 22, 24):
        fit("p1刻度", str(v), 18, 30)
        S.append(text(76, y1(v) - 9, str(v), 18, FAINT, family=FN,
                      align="END", box_w=30))
    hgrid(y1(v))
S.append(rect(110, 369, 1232, 2, AXIS))
# p2 湿度：基线 30；网格 35/40/45 全标注
for v in (35, 40, 45):
    fit("p2刻度", str(v), 18, 30)
    S.append(text(76, y2(v) - 9, str(v), 18, FAINT, family=FN, align="END", box_w=30))
    hgrid(y2(v))
S.append(rect(110, 535, 1232, 2, AXIS))
# p3 压差：基线 −1（AXIS）；零线 0 强调（ZERO，+左侧 “0”）；网格 −0.5/0.5/1/1.5；标注 −1/0/1
for v, lab in ((-0.5, None), (0.5, None), (1.0, "1"), (1.5, None)):
    hgrid(y3(v))
for v, lab in ((-1, "−1"), (0, "0"), (1, "1")):
    fit("p3刻度", lab, 18, 30)
    S.append(text(76, y3(v) - 9, lab, 18, SUB if v == 0 else FAINT,
                  family=FN, bold=(v == 0), align="END", box_w=30))
S.append(rect(110, 655.8 - 1.5, 1232, 3, ZERO))   # 零线 v=0 → y=654.8±1.5 画粗
S.append(rect(110, 701, 1232, 2, AXIS))           # 基线 −1

# ---- 连线（只连相邻有效样本；缺测处断开）
runs = {"temperature_c": [], "humidity_pct": [], "pressure_kpa": []}
pairs_map = {}
for (key, _, _, _style, _c), fi in zip(METRICS, (1, 2, 3)):
    colv = [r[fi] for r in RAW]
    run, lasts = [], []
    run_cur = []
    for i, v in enumerate(colv):
        if v is not None:
            run_cur.append(i)
            if i + 1 >= len(colv) or colv[i + 1] is None:
                if len(run_cur) >= 2:
                    runs[key].append(run_cur)
                run_cur = []
        else:
            pass
    pairs = []
    for run in runs[key]:
        for a in range(len(run) - 1):
            pairs.append([run[a], run[a + 1]])
    pairs_map[key] = pairs
GEO["runs"] = runs
GEO["segments"] = pairs_map

drawn_pairs = []
for (key, _name, _unit, _pre, cs), fi, py in zip(METRICS, (1, 2, 3), (y1, y2, y3)):
    colv = [r[fi] for r in RAW]
    for a, b in pairs_map[key]:
        pa = (xof(OFFS[a]), py(colv[a]))
        pb = (xof(OFFS[b]), py(colv[b]))
        seg = quad(pa, pb, cs["main"], 3.5)
        if seg:
            S.append(seg)
        drawn_pairs.append({"key": [key, a, b],
                            "p1": [round(pa[0], 2), round(pa[1], 2)],
                            "p2": [round(pb[0], 2), round(pb[1], 2)]})
GEO["drawn_segments"] = drawn_pairs

# ---- 负采样样本底衬上写字（band 说明，仅三点范围内）
blab = "负压实际采样区段 09:40–10:50"
fit("带标签", blab, 18, 300)
S.append(text((nbx0 + nbx1) / 2 - 150, 588, blab, 18, NEG_TX,
              family=FAM_MIX, bold=True, align="CENTER", box_w=300))

# ---- 每个真实读数：独立采样标记（圆环点）
marker_geo = {}
for (key, _n, _u, _p, cs), fi, py in zip(METRICS, (1, 2, 3), (y1, y2, y3)):
    colv = [r[fi] for r in RAW]
    marker_geo[key] = []
    for i, v in enumerate(colv):
        if v is None:
            continue
        mx, my = xof(OFFS[i]), py(v)
        S.append(marker(mx, my, cs["main"], 14, 6))
        marker_geo[key].append({"i": i, "time": RAW[i][0],
                                "x": round(mx, 2), "y": round(my, 2)})
GEO["markers"] = marker_geo

# ---- 缺测菱形（标记于面板顶部空区，非数据位置）
def top_gap_y(key):
    return {"temperature_c": 268, "humidity_pct": 434}[key]

for (key, _n, _u, _p, cs), fi in zip(METRICS, (1, 2, 3)):
    colv = [r[fi] for r in RAW]
    for i, v in enumerate(colv):
        if v is not None:
            continue
        gx = xof(OFFS[i])
        S.append(diamond_ring(gx, top_gap_y(key), cs["main"]))
        GEO.setdefault("missing_marks", []).append(
            {"key": key, "i": i, "time": RAW[i][0], "x": round(gx, 2),
             "y": top_gap_y(key)})

# ---- x 轴时标（30 分钟）
for rl in REF_X:
    lab = f"{rl['minutes'] // 60 + 8:02d}:{rl['minutes'] % 60:02d}"
    fit("轴标" + lab, lab, 18, 60)
    S.append(text(rl["x"] - 30, 706, lab, 18, FAINT, family=FN,
                  align="CENTER", box_w=60))

# ---------------------------------------------------------------- 12 时点简表
TR = TROW
S.append(rect(TR["cx"], TR["cy"], TR["w"], TR["h"], CARD, 16, BORD))
capt = "全部 12 个时点 · 空单元格＝缺测（表中以 — 表示，不是 0）"
fit("表标题", capt, 18, 720)
S.append(text(88, TR["cy"] + 12, capt, 18, SUB, family=FAM_MIX, bold=True))
hint = "左列：08:00–09:40 → 右列：10:10–12:30"
fit("表提示", hint, 18, 380)
S.append(text(972, TR["cy"] + 12, hint, 18, FAINT, family=FAM_MIX,
              align="END", box_w=380))

HALVES = (88, 760)


def col_sites(h):
    return {"time": (h, "START"), "v1": (h + 150, "END", h + 270),
            "v2": (h + 300, "END", h + 420), "v3": (h + 450, "END", h + 570)}


for h in HALVES:
    # 表头
    hsites = col_sites(h)
    S.append(text(hsites["time"][0], 776, "时间", 18, SUB, bold=True))
    for ck, lab in (("v1", "温度（°C）"), ("v2", "湿度（%）"), ("v3", "压差（kPa）")):
        fit("表头" + lab, lab, 18, 120)
        S.append(text(hsites[ck][0], 776, lab, 18, SUB, bold=True,
                      align="END", box_w=120))
    S.append(rect(h, 798, 592, 1, GRID))
# 半分栏竖线
S.append(rect(722, 776, 1, 206, GRID))
S.append(rect(88, TR["cy"] + 10, 592, 1, GRID))
S.append(rect(760, TR["cy"] + 10, 592, 1, GRID))

GEO["table_rows"] = []
for half in range(2):
    h = HALVES[half]
    hsites = col_sites(h)
    for k in range(6):
        i = half * 6 + k
        t_st, temp, hum, press = RAW[i]
        yy = 806 + 29 * k
        if k in (1, 3, 5):
            S.append(rect(h + 0, yy - 4, 592, 28, ZEBRA))
        fit(f"行{i}时间", t_st, 20, 110)
        S.append(text(hsites["time"][0], yy, t_st, 20, INK, family=FAM_MIX))
        for ck, key, fmt, idx in (("v1", "温度", "{:.1f}", 1), ("v2", "湿度", "{}", 2),
                                  ("v3", "压差", "{:.1f}", 3)):
            v = RAW[i][idx]
            bx, _al, right = hsites[ck]
            if v is None:
                lab = "—"
                col_used = FAINT
            else:
                lab = (f"{v:.1f}" if idx == 1 else
                       f"{int(v)}" if idx == 2 else
                       f"{v:.1f}".replace("-", "−"))
                col_used = NEG_TX if idx == 3 and v < 0 else INK
            fit(f"行{i}{key}", lab, 20, 110)
            S.append(text(bx, yy, lab, 20, col_used, family=FAM_MIX,
                          bold=(idx == 3 and v is not None and v < 0),
                          align="END", box_w=120))
        GEO["table_rows"].append({"time": t_st, "y": yy})

# ---------------------------------------------------------------- 注记与校验
if WARN:
    print(json.dumps({"estw_overflows": WARN}, ensure_ascii=False, indent=2))
    raise SystemExit(f"{len(WARN)} 处文本估宽超限/几何告警，先修正再渲染")

# =====================================================================
# 写出 DSL
# =====================================================================
dsl = snapshot(BG, S)
(OUT / "sensor-report.snapshot").write_text(dsl, encoding="utf-8")

# =====================================================================
# normalized-data.json（题面专用审计；visual_checks 由实际看图后填入）
# =====================================================================
samples = []
for i, (tt, tv, hv, pv) in enumerate(RAW):
    samples.append({
        "index": i,
        "time": tt,
        "minutes": OFFS[i],
        "temperature_c": tv,
        "humidity_pct": hv,
        "pressure_kpa": pv,
    })
statistics = {}
for key, name, unit, _pre, _cs in METRICS:
    fi = 1 if key == "temperature_c" else (2 if key == "humidity_pct" else 3)
    colv = [r[fi] for r in RAW]
    vv = [v for v in colv if v is not None]
    miss = [RAW[i][0] for i, v in enumerate(colv) if v is None]
    statistics[key] = {
        "name": name,
        "unit": unit,
        "valid_count": len(vv),
        "invalid_count": len(colv) - len(vv),
        "missing_times": miss,
        "observed_min": min(vv),
        "observed_max": max(vv),
    }
axes = {
    "shared_x": {
        "base_time": "08:00",
        "span_minutes": SPANN,
        "mapping": "x_px = 110 + minutes × 1232 / 270",
        "px_per_minute": round(PX_MIN, 6),
        "chart_area_x": [110, 1342],
        "vertical_ref_lines_every_minutes": 30,
        "vertical_ref_lines": REF_X,
        "axis_ticks": [f"{8 + t // 60:02d}:{t % 60:02d}" for t in range(0, 271, 30)],
    },
    "panels": [
        {"metric": "temperature_c", "name": "温度", "unit": "°C",
         "range": [19, 24], "px_per_unit": 23.6,
         "mapping": "y_px = 370 − 23.6 × (v − 19)",
         "chart_band_y": [252, 370], "gridlines": [20, 21, 22, 23, 24],
         "labels": [20, 22, 24], "baseline_value": 19},
        {"metric": "humidity_pct", "name": "相对湿度", "unit": "%",
         "range": [30, 45], "px_per_unit": 7.86667,
         "mapping": "y_px = 536 − 7.86667 × (v − 30)",
         "chart_band_y": [418, 536], "gridlines": [35, 40, 45],
         "labels": [30, 35, 40, 45], "baseline_value": 30},
        {"metric": "pressure_kpa", "name": "压差", "unit": "kPa",
         "range": [-1, 1.5], "px_per_unit": 47.2,
         "mapping": "y_px = 702 − 47.2 × (v + 1)",
         "chart_band_y": [584, 702], "gridlines": [-0.5, 0.5, 1, 1.5],
         "labels": [-1, 0, 1], "baseline_value": -1,
         "zero_line_y": 654.8,
         "negative_sampling_band": {"times": ["09:40", "10:50"],
                                    "x_px": [round(nbx0, 2), round(nbx1, 2)],
                                    "statement": "只标注实际负值采样的时点跨度；"
                                                 "区段内未采样的时刻不作连续为负的推断"}},
    ],
}
normalized = {
    "schema_version": 1,
    "task_id": "A05",
    "path_base": "output_dir",
    "question": "不规则采样与缺测的仪表报告",
    "inputs": {
        "path_base": "suite_root",
        "paths": ["tasks/A05-irregular-sensors/inputs/readings.csv"],
        "rows_used": 12,
        "modifications": "无——温度/湿度/压差按输入原值；空单元格→null，不当作 0",
    },
    "samples": samples,
    "statistics": statistics,
    "segments": {
        "note": "只连接相邻两个时点且双方均有有效读数的样本对；缺测两侧不跨接、不插值",
        "temperature_c": {"runs": runs["temperature_c"],
                          "pairs": pairs_map["temperature_c"]},
        "humidity_pct": {"runs": runs["humidity_pct"],
                         "pairs": pairs_map["humidity_pct"]},
        "pressure_kpa": {"runs": runs["pressure_kpa"],
                         "pairs": pairs_map["pressure_kpa"]},
    },
    "negative_samples": {
        "definition": "压差实测值 < 0 的采样时点（不推断连续区间）",
        "items": [{"index": i, "time": RAW[i][0], "minutes": OFFS[i],
                   "pressure_kpa": v} for i, _o, v in NEG],
        "statement": "09:40（−0.2）、10:10（−0.8）、10:50（−0.3）三点实测为负；"
                     "其间/间隔时刻未采样，图中色带仅覆盖该实际采样区段",
    },
    "axes": axes,
    "images": {
        "sensor-report.png": {"size": [1440, 1000], "dsl": "sensor-report.snapshot",
                              "product": "三联趋势（共轴真实分钟比例·断线不补值）+ 12 时点简表"},
    },
    "visual_checks": [],       # 由 finalize_audit.py 在实际查看图像后填写
    "build_script": {"path_base": "suite_root", "path": f"tmp/{RUN_ID}/A05/build_a05.py"},
}
(OUT / "normalized-data.json").write_text(
    json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({
    "snapshot_bytes": len(dsl.encode("utf-8")),
    "segments": {k: len(v) for k, v in pairs_map.items()},
    "markers": {k: len(v) for k, v in marker_geo.items()},
    "legend_total_w": GEO["legend_total_w"],
    "ref_lines": len(REF_X),
    "neg_band_px": [round(nbx0, 2), round(nbx1, 2)],
}, ensure_ascii=False))
