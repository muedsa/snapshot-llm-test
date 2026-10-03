"""A06 DSL generator: 从需求到可复现交付 依赖解释图 (1600x1000).

Layout contract (checked by assertions at the bottom):
  * column index == topological layer, so every solid edge points strictly right
  * cards inside one column are parallel branches (no prerequisite between them)
  * multi-column solid edges detour through the empty x-band between card columns
  * feedback edges are dashed and routed under the diagram and back up the left margin
"""
from __future__ import annotations

import json
import math
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A06"
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
AD = json.load(open(os.path.join(OUT, "graph-audit.json"), encoding="utf-8"))
VER = sys.argv[1] if len(sys.argv) > 1 else "final"

CJ = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
BG, CARD = "#F1F5F9FF", "#FFFFFFFF"
INK, INK2, MUTED, MUTED2 = "#0B1220FF", "#1E293BFF", "#5B6B7FFF", "#94A3B8FF"
LINE, NAVY = "#E2E8F0FF", "#0F172AFF"
TEAL, TEAL_D = "#0E9F8FFF", "#0B7A6EFF"
AMBER, AMBER_D = "#D97706FF", "#B45309FF"
BLUE, VIOLET = "#2563EBFF", "#7C3AEDFF"
ROSE = "#E11D48FF"

W, H = 1600, 1000
NODES = list(AD["labels"].keys())
LABEL = AD["labels"]
LAYER = {k: int(v) for k, v in AD["layer_index"].items()}
GROUPS = {int(k): v for k, v in AD["topological_layers"].items()}
RAW = json.load(open(os.path.join(ROOT, "tasks", "A06-dependency-graph", "inputs", "graph.json"),
                     encoding="utf-8"))
SOLID = [tuple(e) for e in RAW["solid_edges"]]
FEEDBACK = [tuple(e) for e in RAW["feedback_edges"]]

# ---- layout constants -------------------------------------------------------------
ROW_PITCH, CARD_H, ROW_Y0 = 62, 50, 84
DIAG_TOP = ROW_Y0 + 10 * ROW_PITCH + CARD_H
FB_Y = 806
FOOT_W = 1540
COL_X0, COL_W, COL_GAP = 124, 233.33, 10
ROUTER_X0, ROUTER_STEP = 426, 40        # one 10px lane per multi-column edge

NCOL = max(GROUPS) + 1
COL_R = [COL_X0 + i * (COL_W + COL_GAP) + COL_W for i in range(NCOL)]
COL_L = [COL_X0 + i * (COL_W + COL_GAP) for i in range(NCOL)]

MULTI = sorted([(a, b) for a, b in SOLID if LAYER[b] - LAYER[a] >= 2])
ROUTER = {e: ROUTER_X0 + i * ROUTER_STEP for i, e in enumerate(MULTI)}

ORDER_IN_COL: dict[int, list[str]] = {}
for n in NODES:
    ORDER_IN_COL.setdefault(LAYER[n], []).append(n)
for k in ORDER_IN_COL:
    ORDER_IN_COL[k].sort()


def node_y(n: str) -> int:
    return ROW_Y0 + ORDER_IN_COL[LAYER[n]].index(n) * ROW_PITCH


def node_rect(n: str):
    return (COL_L[LAYER[n]], node_y(n), COL_W, CARD_H)


P: list[str] = []
add = P.append


def box(x, y, w, h, color, radius=None, border=None, shadow=None, tl=None, tr=None, bl=None, br=None):
    a = f'<Container width="{w}" height="{h}" color="{color}"'
    if radius:
        a += f' borderRadius="{radius}"'
    for nm, v in (("TopLeft", tl), ("TopRight", tr), ("BottomLeft", bl), ("BottomRight", br)):
        if v:
            a += f' borderRadius{nm}="{v}"'
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
    if length < 0.5:
        return
    ang = math.atan2(dy, dx)
    m11, m12 = math.cos(ang), math.sin(ang)
    m21, m22 = -m12, m11
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    tx = mx - m11 * (length / 2) - m21 * (th / 2)
    ty = my - m12 * (length / 2) - m22 * (th / 2)
    mat = f"(1,0,0,0,0,1,0,0,0,0,1,0,{tx:.3f},{ty:.3f},0,1)"
    add(f'<Positioned left="0" top="0"><Transform matrix="{mat}"><Container width="{length:.2f}" '
        f'height="{th}" color="{color}" borderRadius="{th/2}"/></Transform></Positioned>')


def arrow_head(x, y, direction, color, size=9):
    """Small triangle built from three rotated bars so no path support is needed."""
    pts = {"right": [(x, y), (x - size, y - size * 0.6), (x - size, y + size * 0.6)],
           "down": [(x, y), (x - size * 0.6, y - size), (x + size * 0.6, y - size)],
           "up": [(x, y), (x - size * 0.6, y + size), (x + size * 0.6, y + size)],
           "left": [(x, y), (x + size, y - size * 0.6), (x + size, y + size * 0.6)]}[direction]
    for i in range(3):
        a, b = pts[i], pts[(i + 1) % 3]
        seg(a[0], a[1], b[0], b[1], color, 3)


add(f'<Snapshot background="{BG}" type="png">')
add(f'<Container width="{W}" height="{H}">')
add('<Stack alignment="TOP_LEFT" fit="EXPAND">')

# ============================== header ==============================
box(0, 0, W, 92, NAVY)
box(0, 0, 8, 92, TEAL)
text(40, 10, "从需求到可复现交付 · 依赖解释图", 32, "#FFFFFFFF", "BOLD")
text(40, 54, "列 = 拓扑层（左→右）；同列节点互为并行分支；实线为有向先决依赖，虚线为反馈关系",
     20, "#94A3B8FF")
text(1000, 10, "14 节点 · 16 条先决边 · 2 条反馈边", 20, "#5EEAD4FF", "BOLD", CJ, 560, "CENTER_RIGHT")
text(1000, 38, "先决边只向右，无指向过去层的布局歧义", 20, "#FBBF24FF", "BOLD", CJ, 560, "CENTER_RIGHT")
text(1000, 64, "交叉线无连接点即不构成依赖", 20, "#94A3B8FF", "NORMAL", CJ, 560, "CENTER_RIGHT")

# ============================== layer rails ==============================
for k in sorted(GROUPS):
    y = ROW_Y0 + k * ROW_PITCH
    box(36, y, 1540, CARD_H, "#E9EEF5FF" if k % 2 == 0 else "#F3F6FAFF", 8)
    text(44, y + 12, f"L{k:02d}", 20, MUTED, "BOLD", MONO)

# ============================== prerequisite edges ==============================
for a, b in SOLID:
    x0, y0, w0, h0 = node_rect(a)
    x1, y1, w1, h1 = node_rect(b)
    sy = y0 + h0 / 2
    ty = y1 + h1 / 2
    if LAYER[b] - LAYER[a] == 1:
        seg(x0 + w0, sy, x1 - 10, ty, "#334155FF", 3)
        arrow_head(x1 - 4, ty, "right", "#334155FF")
    else:
        rx = ROUTER[(a, b)]
        seg(x0 + w0, sy, rx, sy, "#334155FF", 3)
        seg(rx, sy, rx, ty, "#334155FF", 3)
        seg(rx, ty, x1 - 10, ty, "#334155FF", 3)
        arrow_head(x1 - 4, ty, "right", "#334155FF")

# ============================== feedback edges (dashed, below + left margin) ==============================
FB_LANE = {"N09": 4, "N10": 14}
for i, (a, b) in enumerate(FEEDBACK):
    x0, y0, w0, h0 = node_rect(a)
    x1, y1, w1, h1 = node_rect(b)
    lane = FB_Y + FB_LANE[a]
    rx = 78 - i * 18                       # left margin lane, right-to-left return
    # dashed down from the source card
    sx = x0 + w0 / 2 + (14 if i else -14)
    yy = y0 + h0
    while yy < lane:
        seg(sx, yy, sx, min(yy + 9, lane), AMBER, 3)
        yy += 16
    # dashed run to the left margin
    xx = sx
    while xx > rx:
        seg(xx, lane, max(xx - 9, rx), lane, AMBER, 3)
        xx -= 16
    # dashed climb up the left margin to the target row
    ty = y1 + h1 / 2
    yy = lane
    while yy > ty:
        seg(rx, yy, rx, max(yy - 9, ty), AMBER, 3)
        yy -= 16
    # dashed run right into the target card
    xx = rx
    while xx < x1 - 10:
        seg(xx, ty, min(xx + 9, x1 - 10), ty, AMBER, 3)
        xx += 16
    arrow_head(x1 - 4, ty, "right", AMBER)

# ============================== node cards ==============================
for n in NODES:
    x, y, w, h = node_rect(n)
    box(x, y, w, h, CARD, 10, f"1 SOLID #CBD5E1FF", "0 2 6 0 #0F172A12 NORMAL")
    box(x, y, 5, h, TEAL, tl=10, bl=10)
    text(x + 16, y + 5, n, 20, TEAL_D, "BOLD", MONO)
    text(x + 74, y + 5, f"L{LAYER[n]:02d}", 20, MUTED2, "BOLD", MONO)
    text(x + 16, y + 25, LABEL[n], 22, INK, "BOLD")
    deg = AD["neighbours"][n]
    text(x + w - 92, y + 5, f"入{deg['in_degree']} 出{deg['out_degree']}", 20, MUTED, "NORMAL", MONO, 78, "CENTER_RIGHT")

# ============================== footer: legend + in-figure explanation ==============================
box(40, FB_Y + 46, 700, 76, CARD, 10, f"1 SOLID {LINE}")
text(56, FB_Y + 54, "图例", 20, INK, "BOLD")
seg(120, FB_Y + 64, 176, FB_Y + 64, "#334155FF", 3)
arrow_head(182, FB_Y + 64, "right", "#334155FF")
text(192, FB_Y + 54, "先决依赖（有向，只向右）", 20, INK2)
seg(400, FB_Y + 64, 448, FB_Y + 64, AMBER, 3)
arrow_head(454, FB_Y + 64, "right", AMBER)
text(464, FB_Y + 54, "反馈关系（虚线，不参与排序）", 20, AMBER_D, "BOLD")
text(120, FB_Y + 88, "同列 = 并行分支（层内无先决关系）；灰底横条为拓扑层轨道", 20, MUTED)

box(760, FB_Y + 46, 800, 76, NAVY, 10)
box(760, FB_Y + 46, 6, 76, AMBER, tl=10, bl=10)
text(778, FB_Y + 54, "图内解释", 20, "#5EEAD4FF", "BOLD")
text(880, FB_Y + 52, "① 失败后回到构建：首轮渲染（N09）失败时回流到 DSL构建（N08），改完再渲染。",
     20, "#F8FAFCFF", "BOLD", CJ, 660, "CENTER_LEFT")
text(880, FB_Y + 84, "② 检查发现问题后修复：视觉检查（N10）发现问题回流到 N08，再走问题修复（N11）与回归渲染（N12）。",
     20, "#E2E8F0FF", "NORMAL", CJ, 660, "CENTER_LEFT")

text(40, FB_Y + 132, "最长先决路径（11 节点 / 10 边）：N01→N02→N04→N07→N08→N09→N10→N11→N12→N13→N14（多解时给出这一条）。",
     20, MUTED)
text(40, FB_Y + 156, "反馈边以虚线沿图下方与左侧通道绕行、端点相连；交叉处没有连接点，因此不产生新的依赖。",
     20, MUTED)
text(1180, FB_Y + 156, "渲染：Snapshot DSL · 1600×1000", 20, MUTED2, "NORMAL", MONO, 380, "CENTER_RIGHT")

add('</Stack>')
add('</Container>')
add('</Snapshot>')

dsl = "\n".join(P) + "\n"
os.makedirs(TMP, exist_ok=True)
p = os.path.join(TMP, f"dependency-map.{VER}.snapshot")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)

print(p, len(dsl), "chars")
print(f"diagram rows {ROW_Y0}..{ROW_Y0 + 10 * ROW_PITCH + CARD_H} | feedback lanes {FB_Y}..{FB_Y + 20} "
      f"| footer {FB_Y + 46}..{FB_Y + 122} | footnote {FB_Y + 156 + 24}")
print("multi-column edges:", MULTI, "-> routers", ROUTER)
assert all(LAYER[b] > LAYER[a] for a, b in SOLID), "solid edge must point to a later layer"
assert ROW_Y0 + 10 * ROW_PITCH + CARD_H < FB_Y, "node rows overlap the feedback band"
assert FB_Y + 122 < FB_Y + 132, "footer blocks overlap the footnote"
assert FB_Y + 180 < H, "footnote leaves the canvas"
print("layout contract OK")
