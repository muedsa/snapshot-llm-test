# -*- coding: utf-8 -*-
"""A06 · 十四节点依赖图与反馈回路（“从需求到可复现交付”）。
数据源：tasks/A06-dependency-graph/inputs/graph.json（14 节点/16 先决边/2 反馈边）。
产出（路径基准 = 本题输出根 outputs/<run_id>/A06/）：
  dependency-map.snapshot / graph-audit.json（visual_checks 由查看后 finalize_audit.py 填写）

画布 1600×1000：
  标题带 → 图例行 y100 → 图卡 (56,144,1488,664)
    列 = 拓扑层 L0..L10（Kahn 层由 solid_edges 计算；先决边绝不指回更早层）
    并行节点同层两行：上排 y=320 / 下排 y=560；独占列居中 y=426
    节点盒 104×72：阶段色条 + 编号(22px) + 标签(22px bold)
    边：实线暗灰 3px + 11px 实心箭头；N03→N06 顶部绕行、N04→N13 图底绕行
    反馈：红虚线，N09→N08=①渲染失败回构建、N10→N08=②检查缺陷返回构建
  → 底部“读图与反馈”说明卡
"""
import json
import os
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = TASK_ROOT / "outputs" / RUN_ID / "A06"
OUT.mkdir(parents=True, exist_ok=True)
TMP = TASK_ROOT / "tmp" / RUN_ID / "A06"
TMP.mkdir(parents=True, exist_ok=True)

FONT = "Noto Sans CJK SC"
FN = "Inter"
FAM_MIX = FN + "," + FONT

NODES = {
    "N01": "需求冻结", "N02": "输入检查", "N03": "字体查询", "N04": "数据计算",
    "N05": "内容规划", "N06": "版式系统", "N07": "图表生成", "N08": "DSL构建",
    "N09": "首轮渲染", "N10": "视觉检查", "N11": "问题修复", "N12": "回归渲染",
    "N13": "产物校验", "N14": "交付归档",
}
SOLID = [
    ("N01", "N02"), ("N01", "N03"), ("N02", "N04"), ("N02", "N05"),
    ("N03", "N06"), ("N05", "N06"), ("N04", "N07"), ("N06", "N08"),
    ("N07", "N08"), ("N08", "N09"), ("N09", "N10"), ("N10", "N11"),
    ("N11", "N12"), ("N12", "N13"), ("N13", "N14"), ("N04", "N13"),
]
FEEDBACK = [("N09", "N08"), ("N10", "N08")]

# ---- Kahn 拓扑层（solid_edges 原值计算；assert 输入无环）
IND = {n: [] for n in NODES}
OUTD = {n: [] for n in NODES}
for a, b in SOLID:
    OUTD[a].append(b)
    IND[b].append(a)
assert len(OUTD["N01"]) == 2 and len(OUTD["N02"]) == 2, (OUTD["N01"], OUTD["N02"])
LAYERS = {}
lay = {}
for n in NODES:
    lay[n] = 0
changed = True
while changed:
    changed = False
    for a, b in SOLID:
        if lay[b] < lay[a] + 1:
            lay[b] = lay[a] + 1
            changed = True
for n in NODES:
    LAYERS.setdefault(lay[n], []).append(n)
MAXL = max(LAYERS)
LAYER_SEQ = [LAYERS[k] for k in range(MAXL + 1)] if (MAXL := max(LAYERS)) >= 0 else []
# 校验最长路径层=10 且 N14 独占末层
assert lay["N14"] == 10, lay["N14"]
assert all(lay[b] > lay[a] for a, b in SOLID), "solid_edges 必须指向更晚拓扑层（无回指歧义）"

# 最长先决路径 DP
best = {}
memo = {}
def lp(n):
    if n in memo:
        return memo[n]
    r = 1 + max((lp(p) for p in IND[n]), default=0)
    memo[n] = r
    return r
for n in NODES:
    lp(n)
def path_of(n):
    seq = []
    while n:
        seq.append(n)
        preds = IND[n]
        if not preds:
            break
        n = max(preds, key=lambda p: (memo[p], p))  # 并列取 ID 较大分支（N04→N07）
    return seq[::-1]
LONGEST = path_of(max(NODES, key=lambda n: memo[n]))
LLEN = len(LONGEST)
assert LLEN == 11 and LONGEST == [
    "N01", "N02", "N04", "N07", "N08", "N09", "N10", "N11", "N12", "N13", "N14"], LONGEST

# ---- 每节点入/出邻居（审计用）
NEI = {n: {"in": IND[n][:], "out": OUTD[n][:]} for n in NODES}

# =====================================================================
# 文本轮宽估计/发射器（A05 模式）
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
            elif ch in "—–…→↔⇄":
                w += 1.00 * size
            elif ch in "−=+":
                w += 0.60 * size
            elif ch == "%":
                w += 0.60 * size
            elif ch.isdigit():
                w += 0.60 * size
            elif ch.isupper():
                w += 0.70 * size
            else:
                w += 0.54 * size
        else:
            w += 1.00 * size
    return w

WARN = []
def fit(label, s, size, box_w):
    w = estw(s, size)
    if w > box_w:
        WARN.append(f"{label}: estw({w:.1f}) > box {box_w} :: {s}")

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
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0 = min(xs), min(ys)
    w = max(xs) - x0; h = max(ys) - y0
    if w < 0.5 or h < 0.5:
        WARN.append(f"polygon 太小 {pts}")
        return None
    d = "M " + " L ".join(f"{fnum(px - x0)} {fnum(py - y0)}" for px, py in pts) + " Z"
    return (f'<Positioned left="{fnum(x0)}" top="{fnum(y0)}"'
            f' width="{fnum(w)}" height="{fnum(h)}">'
            f'<SizedBox width="{fnum(w)}" height="{fnum(h)}">'
            f'<ClipPath path="{d}"><Container color="{color}" /></ClipPath>'
            f'</SizedBox></Positioned>')

def quad(p1, p2, color, thick=3.0):
    import math
    x1, y1 = p1; x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    nx, ny = dy / L, -dx / L
    hw = thick / 2
    return polygon([(x1 + nx*hw, y1 + ny*hw), (x2 + nx*hw, y2 + ny*hw),
                    (x2 - nx*hw, y2 - ny*hw), (x1 - nx*hw, y1 - ny*hw)], color)

def hseg(x1, x2, y, color, thick):
    return quad((x1, y), (x2, y), color, thick)

def vseg(x, y1, y2, color, thick=3.0):
    return quad((x, y1), (x, y2), color, thick)

def arrowhead(cx, cy, direction, color, size=22.0, length=18.0):
    """direction: R/L/D/U"""
    dd = {"R": (1, 0), "L": (-1, 0), "D": (0, 1), "U": (0, -1)}[direction]
    dx, dy = dd
    nx, ny = dy, -dx
    hl, hw_ = length / 2, size / 2
    tip = (cx + dx*hl, cy + dy*hl)
    b1 = (cx - dx*hl + nx*hw_, cy - dy*hl + ny*hw_)
    b2 = (cx - dx*hl - nx*hw_, cy - dy*hl - ny*hw_)
    return polygon([tip, b1, b2], color)

def snapshot(bg, items):
    return ('<Snapshot background="' + bg + '" type="png">\n<Stack>\n'
            + "\n".join(items) + "\n</Stack>\n</Snapshot>\n")

# =====================================================================
# 配色
# =====================================================================
W, H = 1600, 1000
BG = "#F3F6FB"; INK = "#17233D"; SUB = "#55657F"; FAINT = "#8494AE"
CARD = "#FFFFFF"; BORD = "1 SOLID #E3EAF4"; GRID = "#E1E8F3"

S = [f'<SizedBox width="{W}" height="{H}" />']
GEO = {}
PHASE = {
    "准备": "#2E90FA", "构图": "#14B8A6", "构建": "#F59E0B",
    "审校": "#7C3AED", "收束": "#059669",
}
PH_OF = {
    "N01": "准备", "N02": "准备", "N03": "准备", "N04": "准备",
    "N05": "构图", "N06": "构图", "N07": "构图", "N08": "构建",
    "N09": "审校", "N10": "审校", "N11": "审校", "N12": "审校",
    "N13": "收束", "N14": "收束",
}

# =====================================================================
# 标题带 + 图例行 + 图卡框架 + 节点
# =====================================================================
title = "从需求到可复现交付 · 14 节点依赖图"
S.append(text(56, 20, title, 32, INK, family=FAM_MIX, bold=True))
badge = "16 条先决依赖 · 2 条反馈回路"
fit("徽标", badge, 20, 384)
S.append(text(1160, 28, badge, 20, SUB, family=FAM_MIX, align="END", box_w=384))
subtitle = "先决依赖（实线）按拓扑层自左向右推进；反馈（红虚线）是运行中的回退，不参与排序。"
fit("副题", subtitle, 20, 1488)
S.append(text(56, 62, subtitle, 20, SUB, family=FAM_MIX))

LEG_Y = 100
lx = 56.0
S.append(hseg(lx, lx + 34, LEG_Y + 10, "#6B7A93", 3))
S.append(arrowhead(lx + 43, LEG_Y + 10, "R", "#6B7A93"))
l1 = "先决依赖（下一步的硬前置）"
fit("图例1", l1, 18, 300)
S.append(text(lx + 62, LEG_Y, l1, 18, SUB, family=FAM_MIX))
lx += 62 + estw(l1, 18) + 40
vx = lx
for _k in range(3):
    S.append(hseg(vx, vx + 9, LEG_Y + 10, "#C0392B", 3))
    vx += 16
S.append(arrowhead(vx + 7, LEG_Y + 10, "R", "#C0392B"))
l2 = "反馈回路（失败/缺陷回退，不参与排序）"
fit("图例2", l2, 18, 400)
S.append(text(vx + 26, LEG_Y, l2, 18, "#C0392B", family=FAM_MIX))
xw = vx + 26 + estw(l2, 18) + 40
for kk in ("准备", "构图", "构建", "审校", "收束"):
    S.append(rect(xw, LEG_Y + 2, 18, 16, PHASE[kk], 4))
    S.append(text(xw + 26, LEG_Y, kk, 18, SUB, family=FAM_MIX))
    xw += 26 + estw(kk, 18) + 18

GX, GY, GW, GH = 56, 144, 1488, 664
S.append(rect(GX, GY, GW, GH, CARD, 16, BORD))

CL, CR = GX + 60, GX + GW - 60          # 116..1484
colw = (CR - CL) / 10.0                  # 136.8
COLX = {L: CL + colw * L for L in range(11)}
NW, NH = 104.0, 72.0

LAYER_NAMES = ["L0 启动", "L1 输入", "L2 分析", "L3 设计", "L4 构建",
               "L5 渲染", "L6 检查", "L7 修复", "L8 回归", "L9 校验", "L10 归档"]
MEMBERS_SORT = [sorted(ms) for ms in LAYER_SEQ]
POS = {}
for L, members in enumerate(MEMBERS_SORT):
    if len(members) == 1:
        POS[members[0]] = (COLX[L], 426)
    elif len(members) == 2:
        POS[members[0]] = (COLX[L], 320)
        POS[members[1]] = (COLX[L], 560)
    else:
        raise SystemExit(f"L{L} 成员数 {len(members)} 超出两行排布假设: {members}")
# 同层双行次序（绘制决策，不改拓扑）：L1 上=N03/下=N02；L2 上=N05/下=N04
POS["N03"] = (COLX[1], 320); POS["N02"] = (COLX[1], 560)
POS["N05"] = (COLX[2], 320); POS["N04"] = (COLX[2], 560)

NODE_BOX = {}
for nid, (cx, cy) in POS.items():
    NODE_BOX[nid] = [cx - NW/2, cy - NH/2, cx + NW/2, cy + NH/2]
GEO["node_boxes"] = NODE_BOX

for L in range(11):
    parts = LAYER_NAMES[L].split(" ")
    S.append(text(COLX[L], 158, parts[0], 18, FAINT, align="CENTER", box_w=120))
    S.append(text(COLX[L], 178, parts[1], 18, SUB, family=FAM_MIX, bold=True,
                  align="CENTER", box_w=120))

for nid in sorted(NODES):
    bx = NODE_BOX[nid]
    cx, cy = POS[nid]
    S.append(rect(bx[0], bx[1], NW, NH, "#FFFFFF", 10, BORD))
    S.append(rect(bx[0], bx[1], 6, NH, PHASE[PH_OF[nid]], 5))
    num = nid[1:]
    S.append(text(cx - 46, cy - 27, num, 22, FAINT, family=FN, bold=True))
    lab = NODES[nid]
    fit("节点" + nid, lab, 22, 98)
    S.append(text(cx - 46, cy - 1, lab, 22, INK, family=FAM_MIX, bold=True))

# =====================================================================
# 先决边（实线 + 箭头；显式折线路由，弯折绕行避字）
# =====================================================================
EDGE_COL = "#6B7A93"
EDGE_PX = []

def port_l(nid):
    b = NODE_BOX[nid]
    return (b[0], (b[1] + b[3]) / 2)

def port_r(nid):
    b = NODE_BOX[nid]
    return (b[2], (b[1] + b[3]) / 2)

def port_t(nid):
    b = NODE_BOX[nid]
    return ((b[0] + b[2]) / 2, b[1])

def port_b(nid):
    b = NODE_BOX[nid]
    return ((b[0] + b[2]) / 2, b[3])

def seg_pts(points, color, thick=3.0):
    out = []
    for i in range(len(points) - 1):
        q = quad(points[i], points[i + 1], color, thick)
        if q:
            out.append(q)
    return out

def arrow_at(tip, direction, color):
    dd = {"R": (1, 0), "L": (-1, 0), "U": (0, -1), "D": (0, 1)}[direction]
    return arrowhead(tip[0] - dd[0] * 9, tip[1] - dd[1] * 9, direction, color)

# 显式折线路由（Option B：L2 上排 N05 / 下排 N04）
def ex(p):  return [[round(x, 2), round(y, 2)] for x, y in p]
E5P = [port_r("N03"), (COLX[1] + 77.2, port_r("N03")[1]),
       (COLX[1] + 77.2, 252), (COLX[2] + 70.4, 252), (COLX[2] + 70.4, 302),
       (NODE_BOX["N06"][0], 302)]
ROUTES = {
    ("N01", "N02"): ([port_r("N01"), (COLX[0] + 68, port_r("N01")[1]),
                      (COLX[0] + 68, port_l("N02")[1]), port_l("N02")], "R"),
    ("N01", "N03"): ([port_r("N01"), (COLX[0] + 68, port_r("N01")[1]),
                      (COLX[0] + 68, port_l("N03")[1]), port_l("N03")], "R"),
    ("N02", "N05"): ([port_t("N02"), (port_t("N02")[0], 380), (COLX[2], 380),
                      (COLX[2], NODE_BOX["N05"][3])], "U"),
    ("N02", "N04"): ([port_r("N02"), port_l("N04")], "R"),
    ("N03", "N06"): (E5P, "R"),
    ("N05", "N06"): ([port_r("N05"), port_l("N06")], "R"),
    ("N04", "N07"): ([port_r("N04"), port_l("N07")], "R"),
    ("N06", "N08"): ([port_r("N06"), (COLX[3] + 67.6, port_r("N06")[1]),
                      (COLX[3] + 67.6, NODE_BOX["N08"][1] + 18),
                      (NODE_BOX["N08"][0], NODE_BOX["N08"][1] + 18)], "R"),
    ("N07", "N08"): ([port_r("N07"), (COLX[3] + 67.6, port_r("N07")[1]),
                      (COLX[3] + 67.6, NODE_BOX["N08"][3] - 18),
                      (NODE_BOX["N08"][0], NODE_BOX["N08"][3] - 18)], "R"),
    ("N08", "N09"): ([port_r("N08"), port_l("N09")], "R"),
    ("N09", "N10"): ([port_r("N09"), port_l("N10")], "R"),
    ("N10", "N11"): ([port_r("N10"), port_l("N11")], "R"),
    ("N11", "N12"): ([port_r("N11"), port_l("N12")], "R"),
    ("N12", "N13"): ([port_r("N12"), port_l("N13")], "R"),
    ("N13", "N14"): ([port_r("N13"), port_l("N14")], "R"),
    ("N04", "N13"): ([port_b("N04"), (COLX[2], GY + GH - 28), (COLX[9], GY + GH - 28),
                      (COLX[9], NODE_BOX["N13"][3])], "U"),
}
assert set(ROUTES) == set(SOLID), set(ROUTES) ^ set(SOLID)

for (a, b), (pts, d) in ROUTES.items():
    for q in seg_pts(pts, EDGE_COL):
        S.append(q)
    tip = pts[-1]
    S.append(arrow_at(tip, d, EDGE_COL))
    EDGE_PX.append({"from": a, "to": b,
                    "polyline": ex(pts),
                    "arrow_tip": ex([tip])[0], "arrow_direction": d})

# =====================================================================
# 反馈边（红虚线；N09→N08 顶部环 / N10→N08 底部环；不参与排序）
# =====================================================================
FB_COL = "#C0392B"
FB_PX = []

def dash_run(x1, x2, y, color, thick=3.0, dash=9.0, gap=7.0):
    x = min(x1, x2)
    end = max(x1, x2)
    out = []
    while x < end:
        x2d = min(x + dash, end)
        out.append(quad((x, y), (x2d, y), color, thick))
        x = x2d + gap
    return out

def dash_vrun(y1, y2, x, color, thick=3.0, dash=9.0, gap=7.0):
    y = min(y1, y2)
    end = max(y1, y2)
    out = []
    while y < end:
        y2d = min(y + dash, end)
        out.append(quad((x, y), (x, y2d), color, thick))
        y = y2d + gap
    return out

F1P = [(port_t("N09")[0] - 24, NODE_BOX["N09"][1]), (port_t("N09")[0] - 24, 350),
       (port_t("N08")[0] - 5, 350), (port_t("N08")[0] - 5, NODE_BOX["N08"][1])]
F2P = [(port_b("N10")[0] - 4, NODE_BOX["N10"][3]), (port_b("N10")[0] - 4, 502),
       (port_b("N08")[0] - 5, 502), (port_b("N08")[0] - 5, NODE_BOX["N08"][3])]
for (a, b), pts, fdir in ((("N09", "N08"), F1P, "D"), (("N10", "N08"), F2P, "U")):
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        if y1 == y2:
            for q in dash_run(x1, x2, y1, FB_COL):
                S.append(q)
        else:
            for q in dash_vrun(y1, y2, x1, FB_COL):
                S.append(q)
    S.append(arrow_at(pts[-1], fdir, FB_COL))
    FB_PX.append({"from": a, "to": b, "polyline": ex(pts),
                  "arrow_tip": ex([pts[-1]])[0],
                  "drawn": "红虚线 9px 划线 / 7px 间隔，末端实心箭头指入目标节点"})

# 反馈标签（图内解释）
lab1 = "① 渲染失败 → 回到构建"
fit("反馈注1", lab1, 18, 220)
S.append(text(680, 322, lab1, 18, FB_COL, family=FAM_MIX, bold=True))
lab2 = "② 检查发现问题 → 返回构建"
fit("反馈注2", lab2, 18, 240)
S.append(text(690, 508, lab2, 18, FB_COL, family=FAM_MIX, bold=True))
det1 = "跨层先决：字体查询 → 版式系统"
fit("绕行注1", det1, 18, 280)
S.append(text(334, 222, det1, 18, EDGE_COL, family=FAM_MIX))
det2 = "跨层先决：数据计算 → 产物校验"
fit("绕行注2", det2, 18, 280)
S.append(text(740, 752, det2, 18, EDGE_COL, family=FAM_MIX))

# =====================================================================
# 底部读图说明卡
# =====================================================================
NOTE = (56, 824, 1488, 156)
S.append(rect(NOTE[0], NOTE[1], NOTE[2], NOTE[3], CARD, 16, BORD))
S.append(rect(56, 824, 5, 132, "#C0392B", 2))
S.append(text(84, 838, "读图要点", 20, INK, family=FAM_MIX, bold=True))
n1 = "① 反馈回路（红虚线）：首轮渲染失败 → 返回 DSL构建 重新生成；② 视觉检查发现问题 → 返回 DSL构建 修复后再渲染；反馈不参与拓扑排序。"
fit("注1", n1, 18, 1420)
S.append(text(84, 870, n1, 18, SUB, family=FAM_MIX))
n2 = "两条跨层先决边沿顶部/图底空带绕行（见灰色小注），不穿过任何节点；全图边线零交叉，反馈环走节点上下空带，不与先决边相接。"
fit("注2", n2, 18, 1420)
S.append(text(84, 898, n2, 18, SUB, family=FAM_MIX))
n3 = "最长先决路径（11 节点）：" + " → ".join(NODES[n] for n in LONGEST) + "。"
fit("注3", n3, 18, 1420)
S.append(text(84, 926, n3, 18, INK, family=FAM_MIX))

if WARN:
    print(json.dumps({"estw_overflows": WARN}, ensure_ascii=False, indent=2))
    raise SystemExit(f"{len(WARN)} 处文本估宽超限/几何告警，先修正再渲染")

# =====================================================================
# 写出 DSL
# =====================================================================
dsl = snapshot(BG, S)
(OUT / "dependency-map.snapshot").write_text(dsl, encoding="utf-8")

# =====================================================================
# graph-audit.json（题面专用审计；visual_checks 由实际看图后填入）
# =====================================================================
nodes_audit = []
for nid in sorted(NODES):
    b = NODE_BOX[nid]
    nodes_audit.append({
        "id": nid, "label": NODES[nid],
        "layer": lay[nid],
        "in_neighbors": NEI[nid]["in"], "out_neighbors": NEI[nid]["out"],
        "box_px": [round(b[0], 2), round(b[1], 2), round(b[2], 2), round(b[3], 2)],
        "phase": PH_OF[nid], "phase_color": PHASE[PH_OF[nid]],
    })
prereq_audit = []
for e in EDGE_PX:
    a, b = e["from"], e["to"]
    assert lay[b] > lay[a], (a, b, lay[a], lay[b])
    prereq_audit.append({
        "from": a, "to": b, "from_label": NODES[a], "to_label": NODES[b],
        "polyline_px": e["polyline"], "arrow_tip_px": e["arrow_tip"],
        "arrow_direction": e["arrow_direction"],
        "drawn": "实线 #6B7A93 3px + 实心箭头",
        "layer_check": f"L{lay[a]} → L{lay[b]}（指向更晚层）",
    })
feedback_audit = []
for e in FB_PX:
    feedback_audit.append({
        "from": e["from"], "to": e["to"],
        "from_label": NODES[e["from"]], "to_label": NODES[e["to"]],
        "polyline_px": e["polyline"], "arrow_tip_px": e["arrow_tip"],
        "drawn": e["drawn"],
        "not_part_of_dag": True,
        "meaning": "运行中的回退关系：不改变任何节点的拓扑层与先决次序",
    })
crossings = []
segs = []
for e in EDGE_PX + FB_PX:
    pl = e["polyline"]
    for i in range(len(pl) - 1):
        segs.append((e["from"] + "→" + e["to"], pl[i], pl[i + 1]))
def seg_int(s1, s2):
    (x1, y1), (x2, y2) = s1; (x3, y3), (x4, y4) = s2
    d = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    if d == 0:
        return None
    t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / d
    u = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / d
    if 0 < t < 1 and 0 < u < 1:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None
for i in range(len(segs)):
    for j in range(i + 1, len(segs)):
        p = seg_int(segs[i][1:], segs[j][1:])
        if p:
            crossings.append({"edges": [segs[i][0], segs[j][0]],
                              "at_px": [round(p[0], 2), round(p[1], 2)],
                              "note": "交叉处无连接点，不构成新依赖"})
audit = {
    "schema_version": 1,
    "task_id": "A06",
    "path_base": "output_dir",
    "question": "十四节点依赖图与反馈回路",
    "inputs": {
        "path_base": "suite_root",
        "paths": ["tasks/A06-dependency-graph/inputs/graph.json"],
        "nodes_used": 14, "solid_edges_used": len(SOLID), "feedback_edges_used": len(FEEDBACK),
        "modifications": "无——节点/边按输入原值；布局与绕行是绘制决策，不改变图语义",
    },
    "topology": {
        "method": "以 solid_edges 为 DAG，按 最长前驱层 分层（Kahn 等价）；feedback_edges 不参与",
        "layer_count": MAXL + 1,
        "layers": {f"L{k}": sorted(v) for k, v in sorted(LAYERS.items())},
        "forward_only_check": "所有先决边 from 层 < to 层（无指向过去层的布局歧义）",
    },
    "nodes": nodes_audit,
    "prerequisite_edges": prereq_audit,
    "longest_path": {
        "node_sequence": LONGEST,
        "labels": [NODES[n] for n in LONGEST],
        "length_nodes": LLEN,
        "length_edges": LLEN - 1,
        "method": "DAG 最长路径动态规划（拓扑序、按节点数计）；并列最优取先出者",
        "alternative_same_length": ["N01", "N02", "N05", "N06", "N08", "N09", "N10",
                                    "N11", "N12", "N13", "N14"],
    },
    "feedback_edges": feedback_audit,
    "crossings": crossings,
    "legend": {
        "solid": "实线灰箭头 = 先决依赖（拓扑排序内）",
        "dashed_red": "红虚线 = 反馈回路（不参与排序，指回构建）",
        "phase": "节点左色条 = 阶段：准备/构图/构建/审校/收束",
    },
    "images": {
        "dependency-map.png": {"size": [1600, 1000], "dsl": "dependency-map.snapshot",
                               "product": "14 节点依赖与反馈解释图（层列 + 绕行 + 反馈环）"},
    },
    "visual_checks": [],
    "build_script": {"path_base": "suite_root", "path": f"tmp/{RUN_ID}/A06/build_a06.py"},
}
(OUT / "graph-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({
    "snapshot_bytes": len(dsl.encode("utf-8")),
    "edges": len(EDGE_PX), "feedback": len(FB_PX),
    "longest": LONGEST, "crossings": len(crossings),
}, ensure_ascii=False))
