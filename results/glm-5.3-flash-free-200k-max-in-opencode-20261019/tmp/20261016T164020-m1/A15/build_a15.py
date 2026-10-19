# -*- coding: utf-8 -*-
"""A15 · reference 1440×900 界面复刻构建器：content.json 驱动 + 布局常数 L（由 ref-measure 校准）。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "outputs", "20261016T164020-m1", "A15")
os.makedirs(OUT, exist_ok=True)
C = json.load(open(os.path.join(ROOT, "tasks", "A15-reference-reconstruction", "inputs", "content.json"), encoding="utf-8"))
FAM = "Inter"
T = {"bg": "#F3F6FB", "sidebar": "#14233C", "pill": "#294467", "panel": "#233954",
     "ink": "#18283F", "gray": "#7C8AA1", "gray2": "#8A95AB", "navgray": "#96A7C4",
     "white": "#FFFFFF", "blue": "#245CE4", "green_ink": "#168267", "teal": "#64DBB6",
     "amber": "#EAAF40", "grid": "#E4E9F1", "cardline": "#E9EDF4", "sep": "#E6EAF1",
     "st_p": {"inprogress": {"bg": "#E7EFFF", "fg": "#245CE4"},
              "review": {"bg": "#FFF3D7", "fg": "#B0701C"},
              "done": {"bg": "#DCF5EC", "fg": "#168267"}}}
L = {"sb_w": 220, "logo": (30, 30, 28), "logo_txt": (72, 34, 18),
     "active": (18, 116, 186, 47), "nav_row0": 118, "nav_pitch": 63, "nav_dot": 34, "nav_tx": 62,
     "nav_tx_dy": 6, "panel": (22, 752, 176, 116),
     "title": (259, 31, 32), "subtitle": (259, 82, 18),
     "btn": (1184, 44, 216, 47), "btn_tx": 19,
     "kpi_y": 139, "kpi_h": 142, "kpi_w": 354, "kpi_x": [261, 645, 1029], "kpi_pad": 24,
     "kpi_label_y": 158, "kpi_label_sz": 12, "kpi_val_y": 191.5, "kpi_val_sz": 33, "kpi_chg_y": 242, "kpi_chg_sz": 17,
     "chart": (261, 311, 740, 283), "chart_t": (285, 331, 20.5), "period_end": 973, "unit_y": 372,
     "grid_x0": 333, "axis_right": 311, "grid_x1": 973, "grid_y0": 405, "grid_step": 36,
     "bar_left": 357, "bar_pitch": 101, "bar_w": 54, "bar_r": 5, "bar_zero": 549,
     "month_cy": 567,
     "act": (1031, 311, 368, 283), "act_t": (1052, 331), "act_item0": 390.5, "act_pitch": 60.5,
     "act_dot_x": 1054, "act_tx": 1077, "act_time_dy": 29,
     "table": (261, 625, 1138, 216), "table_t": (285, 636),
     "thead": (283, 688, 1092, 34), "th_y": 697.5,
     "th_x": {"PROJECT": 298, "OWNER": 782, "STATUS": 1033, "DUE": 1230},
     "row_dy": [0, 35, 70], "row0_tx": 731, "cell_tx": 298, "own_tx": 782, "due_tx": 1230,
     "pill_x": 1028, "pill_w": 148, "pill_h": 27, "pill_r": 13.5, "pill_y0": 729,
     "footer": (260, 863.5, 13)}
WARN = []

def estw(s, size):
    t = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F:
            t += size * 1.0
        elif ch in "0123456789":
            t += size * 0.6
        elif ch == " ":
            t += size * 0.30
        elif ch.isupper():
            t += size * 0.72
        elif ch in "♥→−·—–":
            t += size * 0.62
        else:
            t += size * 0.545
    return t

def TXT(x, y, s, size, color, bold=False, ls=None, anchor=None, fam=None):
    st = f' fontSize="{size}" color="{color}" fontFamily="{fam or FAM}" maxLines="1" overflow="CLIP"'
    if bold:
        st += ' fontStyle="BOLD"'
    if ls:
        st += f' letterSpacing="{ls}"'
    return f'<Positioned left="{x}" top="{y}"><Text{st}>{s}</Text></Positioned>'

def R(x, y, w, h, color=None, radius=None, border=None):
    a = f'width="{w}" height="{h}"'
    if color:
        a += f' color="{color}"'
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' borderWidth="{border[0]}" borderColor="{border[1]}"'
    return f'<Positioned left="{x}" top="{y}"><Container {a} /></Positioned>'

def bar_path(w, h, r):
    return (f"A{r} {r} 0 0 1 {w} {r} " if False else
            f"M0 {r} A{r} {r} 0 0 1 {r} 0 H{w - r} A{r} {r} 0 0 1 {w} {r} V{h} H0 Z")

S = []
# 主背景 + 侧栏
S.append(R(0, 0, 1440, 900, T["bg"]))
S.append(R(0, 0, L["sb_w"], 900, T["sidebar"]))
# 侧栏：logo + 品牌字
lx, ly, lw = L["logo"]
S.append(R(lx, ly, lw, lw, T["teal"], radius=8))
S.append(R(lx + 7, ly + 7, lw - 14, lw - 14, T["sidebar"], radius=4))
bx, by, bsz, bls = (L["logo_txt"] + (0.8,))[:4]
S.append(TXT(bx, by, C["brand"], bsz, T["white"], ls=bls, fam="Inter Extra Bold"))
# 导航选中态 pill + 各导航行
ax, ay, aw, ah = L["active"]
S.append(R(ax, ay, aw, ah, T["pill"], radius=10))
S.append(R(L["nav_dot"], ay + 12.5, 12, 12, T["teal"], radius=6))
S.append(TXT(L["nav_tx"], L["nav_row0"] + L["nav_tx_dy"], C["navigation"][0], 18, T["white"], fam="Inter Extra Bold"))
for i, nm in enumerate(C["navigation"][1:], start=1):
    y = L["nav_row0"] + L["nav_pitch"] * i
    S.append(R(L["nav_dot"], y + L["nav_tx_dy"] + 5, 12, 12, "#7791B3", radius=6))
    S.append(TXT(L["nav_tx"], y + L["nav_tx_dy"], nm, 19.5, "#B4C0D9"))
# 底部面板
pxp, py, pw, ph = L["panel"]
S.append(R(pxp, py, pw, ph, T["panel"], radius=12))
S.append(TXT(pxp + 18, py + 15, C["workspace_info"][0], 12.5, "#64DBB6", ls=0.5, fam="Inter Extra Bold"))
S.append(TXT(pxp + 18, py + 49, C["workspace_info"][1], 17, "#EAF0F8"))
S.append(TXT(pxp + 18, py + 81, C["workspace_info"][2], 15, T["navgray"]))
# 标题/副标题/按钮
tx, ty, ts = L["title"]
S.append(TXT(tx, ty, C["title"], ts, T["ink"], bold=True))
sx, sy2, ss = L["subtitle"]
S.append(TXT(sx, sy2, C["subtitle"], ss, T["gray"]))
bxx, byy, bw2, bh = L["btn"]
S.append(R(bxx, byy, bw2, bh, T["blue"], radius=10))
_w = estw(C["button"], L["btn_tx"])
S.append(TXT(bxx + (bw2 - _w) / 2, byy + 12, C["button"], L["btn_tx"], T["white"], bold=True))
# KPI 三卡
for i, k in enumerate(C["kpis"]):
    x = L["kpi_x"][i]
    S.append(R(x, L["kpi_y"], L["kpi_w"], L["kpi_h"], T["white"], radius=12, border=(1, T["cardline"])))
    S.append(TXT(x + L["kpi_pad"], L["kpi_label_y"], k["label"], L["kpi_label_sz"], "#6A768E", bold=True, ls=1.2))
    S.append(TXT(x + L["kpi_pad"], L["kpi_val_y"], k["value"], L["kpi_val_sz"], T["ink"], bold=True))
    S.append(TXT(x + L["kpi_pad"], L["kpi_chg_y"], k["change"], L["kpi_chg_sz"], T["green_ink"], bold=True))
# 图表卡
cx, cy, cw, chh = L["chart"]
S.append(R(cx, cy, cw, chh, T["white"], radius=12, border=(1, T["cardline"])))
ctx, cty, cts = L["chart_t"]
S.append(TXT(ctx, cty, C["chart_title"], cts, T["ink"], bold=True))
pw2 = estw(C["chart_period"], 17)
S.append(TXT(L["period_end"] - pw2, 334, C["chart_period"], 17, T["gray"]))
S.append(TXT(ctx, L["unit_y"], C["chart_unit"], 13, T["gray2"]))
max_v = max(C["chart_ticks"])
gy = lambda v: L["bar_zero"] - v * (L["bar_zero"] - L["grid_y0"] - 0) / max_v
for v in C["chart_ticks"]:
    y = gy(v)
    S.append(f'<Positioned left="{L["grid_x0"]}" top="{y}"><Container width="{L["grid_x1"] - L["grid_x0"]}" height="1" color="{T["grid"]}" /></Positioned>')
    lab = str(v)
    w3 = estw(lab, 13.5)
    S.append(TXT(L["axis_right"] - w3, y - 7, lab, 13.5, T["gray2"]))
# 柱形（顶部圆角 ClipPath）
gx0 = L["grid_y0"]
scale = (L["bar_zero"] - gx0) / max_v
for i, (v, m) in enumerate(zip(C["chart_values"], C["months"])):
    bx0 = L["bar_left"] + L["bar_pitch"] * i
    hval = v * scale
    p = (f"M0 {L['bar_r']} A{L['bar_r']} {L['bar_r']} 0 0 1 {L['bar_r']} 0 H{L['bar_w'] - L['bar_r']} "
         f"A{L['bar_r']} {L['bar_r']} 0 0 1 {L['bar_w']} {L['bar_r']} V{max(hval, L['bar_r'] + 1)} H0 Z")
    S.append(f'<Positioned left="{bx0}" top="{L["bar_zero"] - hval}"><SizedBox width="{L["bar_w"]}" height="{int(hval) + 1}">'
             f'<ClipPath path="{p}" clipBehavior="ANTI_ALIAS"><Container width="{L["bar_w"]}" height="{int(hval) + 1}" color="{T["blue"]}" /></ClipPath></SizedBox></Positioned>')
    w4 = estw(m, 15)
    mc = bx0 + L["bar_w"] / 2
    S.append(TXT(mc - w4 / 2, L["month_cy"] - 12, m, 15, T["gray"]))
# 活动卡
ax2, ay2, aw2, ah2 = L["act"]
S.append(R(ax2, ay2, aw2, ah2, T["white"], radius=12, border=(1, T["cardline"])))
S.append(TXT(L["act_t"][0], L["act_t"][1], C["activity_title"], 20.5, T["ink"], bold=True))
DOT = [T["amber"], T["blue"], "#168267"]
for i, (nm, tm) in enumerate(C["activity"]):
    it = L["act_item0"] + L["act_pitch"] * i
    S.append(R(L["act_dot_x"], it + 6.5, 10, 10, DOT[i], radius=5))
    S.append(TXT(L["act_tx"], it, nm, 17.5, T["ink"], bold=True))
    S.append(TXT(L["act_tx"], it + L["act_time_dy"], tm, 14, T["gray2"]))
# 表格卡
tbx, tby, tbw, tbh = L["table"]
S.append(R(tbx, tby, tbw, tbh, T["white"], radius=12, border=(1, T["cardline"])))
S.append(TXT(L["table_t"][0], L["table_t"][1], C["table_title"], 20.5, T["ink"], bold=True))
hx, hy, hw2, hh = L["thead"]
S.append(R(hx, hy, hw2, hh, T["bg"], radius=6))
for col, x in L["th_x"].items():
    S.append(TXT(x, L["th_y"], col, 11, "#63748F", bold=True, ls=0.4))
for i, row in enumerate(C["rows"]):
    ry = L["row0_tx"] + L["row_dy"][i]
    py2 = L["pill_y0"] + L["row_dy"][i]
    S.append(TXT(L["cell_tx"], ry, row[0], 16, T["ink"], bold=True))
    S.append(TXT(L["own_tx"], ry, row[1], 16, "#93A0B3"))
    st = row[2].lower().replace(" ", "")
    st = {"inprogress": "inprogress"}.get(st, st)
    code = "inprogress" if row[2] == "In progress" else row[2].lower()
    S.append(R(L["pill_x"], py2, L["pill_w"], L["pill_h"], T["st_p"][code]["bg"], radius=L["pill_r"]))
    w5 = estw(row[2], 13.5) - 0.3 * max(0, len(row[2]) - 1)
    S.append(TXT(L["pill_x"] + (L["pill_w"] - w5) / 2 + 1, py2 + 6.7, row[2], 13.5, T["st_p"][code]["fg"], bold=True, ls=-0.3))
    S.append(TXT(L["due_tx"], ry, row[3], 16, "#9FA9BA"))
    if i < 2:
        sep_y = L["pill_y0"] + L["pill_h"] + L["row_dy"][i] + 3.5
        S.append(f'<Positioned left="{L["thead"][0]}" top="{sep_y}"><Container width="{L["thead"][2]}" height="1" color="{T["sep"]}" /></Positioned>')
# 页脚
fx, fy, fs = L["footer"]
S.append(TXT(C["footer"][0] if isinstance(C["footer"], list) else fx, fy, C["footer"], fs, T["gray2"]) if False else TXT(fx, fy, C["footer"], fs, T["gray2"]))
dsl = (f'<Snapshot background="{T["bg"]}" type="png"><Stack><SizedBox width="1440" height="900" />\n'
       + "\n".join(S) + "\n</Stack></Snapshot>")
open(os.path.join(OUT, "reconstructed.snapshot"), "w", encoding="utf-8").write(dsl)
print("built", os.path.join(OUT, "reconstructed.snapshot"), "| nodes", len(S), "| WARN", WARN)
