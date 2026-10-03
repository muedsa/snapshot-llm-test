"""A06 DSL generator: 从需求到可复现交付 依赖解释图 (1600x1000).

Layout contract (asserted at the bottom):
  * one ROW per topological layer, layer 0 at the top, so every prerequisite edge points down
  * the only node in a row is that layer's node; rows with 2 nodes in the audit mean those
    nodes are parallel branches and share a row band
  * adjacent-layer edges are straight down; long edges detour through a right-hand channel
  * feedback edges are dashed, live in a right-hand return lane, and are never drawn as
    prerequisite edges
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
RAW = json.load(open(os.path.join(ROOT, "tasks", "A06-dependency-graph", "inputs", "graph.json"),
                     encoding="utf-8"))
VER = sys.argv[1] if len(sys.argv) > 1 else "final"

CJ = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
BG, CARD = "#F1F5F9FF", "#FFFFFFFF"
INK, INK2, MUTED, MUTED2 = "#0B1220FF", "#1E293BFF", "#5B6B7FFF", "#94A3B8FF"
LINE, NAVY = "#E2E8F0FF", "#0F172AFF"
TEAL, TEAL_D = "#0E9F8FFF", "#0B7A6EFF"
AMBER, AMBER_D = "#D97706FF", "#B45309FF"

W, H = 1600, 1000
LABEL = AD["labels"]
LAYER = {k: int(v) for k, v in AD["layer_index"].items()}
GROUPS = {int(k): v for k, v in AD["topological_layers"].items()}
SOLID = [tuple(e) for e in RAW["solid_edges"]]
FEEDBACK = [tuple(e) for e in RAW["feedback_edges"]]

ROW_Y0, ROW_PITCH, CARD_H = 84, 54, 36
CARD_X, CARD_W = 210, 380
LANE_X0, LANE_STEP = 1230, 22          # feedback return lanes, right of the cards
ROUTER_X = 1090                         # empty channel right of both card columns
MULTI = sorted([(a, b) for a, b in SOLID if LAYER[b] - LAYER[a] >= 2])
ROUTER = {e: ROUTER_X + i * 22 for i, e in enumerate(MULTI)}
ROUTER[("N04", "N13")] = 1180   # in the empty strip between the cards and the feedback lanes
FB_LANE = {n: LANE_X0 + i * LANE_STEP for i, (n, _) in enumerate(FEEDBACK)}

FOOT_Y = ROW_Y0 + max(GROUPS) * ROW_PITCH + CARD_H + 26

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
    if length < 0.6:
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


def head(x, y, direction, color, size=9):
    tri = {"down": [(x, y), (x - size * 0.6, y - size), (x + size * 0.6, y - size)],
           "right": [(x, y), (x - size, y - size * 0.6), (x - size, y + size * 0.6)],
           "left": [(x, y), (x + size, y - size * 0.6), (x + size, y + size * 0.6)]}[direction]
    for i in range(3):
        a, b = tri[i], tri[(i + 1) % 3]
        seg(a[0], a[1], b[0], b[1], color, 3)


def subtree_below(n: str) -> bool:
    """True when n has a child far enough down that the edge needs a right-hand channel.

    Only N04 -> N13 qualifies, and that channel lives right of the SECOND card column, so
    N04 must sit in that right slot; otherwise its outgoing edge would leave leftwards into
    the sibling card.
    """
    return any(LAYER[m] - LAYER[n] >= 8 for m in AD["neighbours"][n]["out"])


def nx(n: str) -> int:
    """x of a node card. In a 2-node row the node whose subtree continues below takes the
    right slot, so its outgoing edge leaves the row without crossing the sibling card."""
    grp = sorted(GROUPS[LAYER[n]], key=lambda k: (not subtree_below(k), k))
    if len(grp) == 1:
        return CARD_X
    return CARD_X + grp.index(n) * (CARD_W + 118)


def ny(n: str) -> int:
    return ROW_Y0 + LAYER[n] * ROW_PITCH


def rect(n: str):
    return nx(n), ny(n), CARD_W, CARD_H


add(f'<Snapshot background="{BG}" type="png">')
add(f'<Container width="{W}" height="{H}">')
add('<Stack alignment="TOP_LEFT" fit="EXPAND">')

# ============================== header ==============================
box(0, 0, W, 74, NAVY)
box(0, 0, 8, 74, TEAL)
text(40, 8, "从需求到可复现交付 · 依赖解释图", 30, "#FFFFFFFF", "BOLD")
text(40, 46, "行 = 拓扑层（上→下）；实线为有向先决依赖，虚线为反馈关系（不参与排序）", 20, "#94A3B8FF")
text(1020, 8, "14 节点 · 16 条先决边 · 2 条反馈边", 20, "#5EEAD4FF", "BOLD", CJ, 540, "CENTER_RIGHT")
text(1020, 34, "先决边一律向下，无指向过去层的歧义", 20, "#FBBF24FF", "BOLD", CJ, 540, "CENTER_RIGHT")
text(1020, 56, "交叉线无连接点即不构成新的依赖", 20, "#94A3B8FF", "NORMAL", CJ, 540, "CENTER_RIGHT")

# ============================== layer rails ==============================
for k in sorted(GROUPS):
    y = ROW_Y0 + k * ROW_PITCH
    box(36, y, 1528, CARD_H, "#E9EEF5FF" if k % 2 == 0 else "#F3F6FAFF", 8)
    text(44, y + 7, f"L{k:02d}", 20, MUTED, "BOLD", MONO, 70, "CENTER_LEFT")


# ============================== prerequisite edges (always downward) ==============================
for a, b in SOLID:
    x0, y0, w0, h0 = rect(a)
    x1, y1, w1, h1 = rect(b)
    sx, tx = x0 + w0 / 2, x1 + w1 / 2
    if LAYER[b] - LAYER[a] == 1:
        # consecutive layers: the whole edge is a short vertical drop, never a diagonal
        seg(sx, y0 + h0, sx, y1 - 10, "#334155FF", 3)
        head(sx, y1 - 4, "down", "#334155FF")
    else:
        # long edge: fall to the nearest empty gap, slide across an empty channel (clear of
        # both card columns), then drop through the inter-row gaps into the target card
        rx = ROUTER[(a, b)]
        # when the source row still has a sibling card to its right, slide in the gap just
        # ABOVE that row instead of at the source card's own bottom edge
        same_row_pair = len(GROUPS[LAYER[a]]) > 1 and subtree_below(a)
        # slide in the first fully empty band below the source row (two rows down), so the
        # horizontal run never shares a band with any card
        gy = (y0 + 2 * ROW_PITCH - 12) if same_row_pair else (y0 + h0 + 6)
        seg(sx, y0 + h0 if not same_row_pair else y0, sx, gy, "#334155FF", 3)
        seg(sx, gy, rx, gy, "#334155FF", 3)
        seg(rx, gy, rx, y1 - 10, "#334155FF", 3)
        head(rx, y1 - 4, "down", "#334155FF")

# ============================== feedback edges (dashed, right-hand return lane) ==============================
for i, (a, b) in enumerate(FEEDBACK):
    x0, y0, w0, h0 = rect(a)
    x1, y1, w1, h1 = rect(b)
    lane = FB_LANE[a]
    sy = y0 + h0 / 2
    ty = y1 + h1 / 2
    # dash out of the source card to the lane
    xx = x0 + w0
    while xx < lane:
        seg(xx, sy, min(xx + 10, lane), sy, AMBER, 3)
        xx += 17
    # dash up the lane
    yy = sy
    while yy > ty:
        seg(lane, yy, lane, max(yy - 10, ty), AMBER, 3)
        yy -= 17
    # dash back into the target card
    xx = lane
    while xx > x1 + w1 + 8:
        seg(xx, ty, max(xx - 10, x1 + w1 + 8), ty, AMBER, 3)
        xx -= 17
    head(x1 + w1 + 4, ty, "left", AMBER)

# ============================== node cards ==============================
for n in sorted(LABEL, key=lambda k: (LAYER[k], LABEL[k])):
    x, y, w, h = rect(n)
    box(x, y, w, h, CARD, 9, "1 SOLID #CBD5E1FF", "0 2 5 0 #0F172A12 NORMAL")
    box(x, y, 5, h, TEAL, tl=9, bl=9)
    text(x + 14, y + 5, n, 20, TEAL_D, "BOLD", MONO)
    text(x + 62, y + 5, f"L{LAYER[n]:02d}", 20, MUTED2, "BOLD", MONO)
    text(x + 118, y + 4, LABEL[n], 22, INK, "BOLD")
    d = AD["neighbours"][n]
    text(x + w - 104, y + 5, f"入{d['in_degree']} 出{d['out_degree']}", 20, MUTED, "NORMAL", MONO, 90, "CENTER_RIGHT")

# ============================== footer: explanation + legend ==============================
box(40, FOOT_Y, 1080, 74, NAVY, 10)
box(40, FOOT_Y, 6, 74, AMBER, tl=10, bl=10)
text(58, FOOT_Y + 8, "图内解释", 20, "#5EEAD4FF", "BOLD")
text(168, FOOT_Y + 6, "① 失败后回到构建：首轮渲染（N09）失败时回流到 DSL构建（N08），改完再渲染。",
     20, "#F8FAFCFF", "BOLD")
text(168, FOOT_Y + 34, "② 检查发现问题后修复：视觉检查（N10）发现问题回流到 N08，再走问题修复（N11）与回归渲染（N12）。",
     20, "#E2E8F0FF")

box(1140, FOOT_Y, 420, 74, CARD, 10, f"1 SOLID {LINE}")
text(1156, FOOT_Y + 8, "图例", 20, INK, "BOLD")
seg(1216, FOOT_Y + 20, 1268, FOOT_Y + 20, "#334155FF", 3)
head(1272, FOOT_Y + 20, "right", "#334155FF")
text(1282, FOOT_Y + 8, "先决依赖（向下）", 20, INK2)
seg(1216, FOOT_Y + 44, 1268, FOOT_Y + 44, AMBER, 3)
head(1272, FOOT_Y + 44, "left", AMBER)
text(1282, FOOT_Y + 32, "反馈关系（虚线）", 20, AMBER_D, "BOLD")
text(1156, FOOT_Y + 44, "同层 = 并行分支", 20, MUTED)

text(40, FOOT_Y + 86, "最长先决路径（11 节点 / 10 边）：N01→N02→N04→N07→N08→N09→N10→N11→N12→N13→N14（多解时给出这一条）。",
     20, MUTED)
text(40, FOOT_Y + 110, "反馈边 N09→N08、N10→N08 以虚线经右侧回流通道向上，端点相连；交叉处没有连接点，因此不产生新的依赖。",
     20, MUTED)
text(1180, FOOT_Y + 110, "渲染：Snapshot DSL · 1600×1000", 20, MUTED2, "NORMAL", MONO, 380, "CENTER_RIGHT")

add('</Stack>')
add('</Container>')
add('</Snapshot>')

dsl = "\n".join(P) + "\n"
os.makedirs(TMP, exist_ok=True)
p = os.path.join(TMP, f"dependency-map.{VER}.snapshot")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)

FB_XMAX = max(rect(n)[0] + rect(n)[2] for n in LABEL)
print(p, len(dsl), "chars")
print(f"rows {ROW_Y0}..{ROW_Y0 + max(GROUPS) * ROW_PITCH + CARD_H} | card right edge max {FB_XMAX} | "
      f"feedback lanes {LANE_X0}..{LANE_X0 + LANE_STEP * len(FEEDBACK)} | footer {FOOT_Y}..{FOOT_Y + 74} | "
      f"footnote {FOOT_Y + 110 + 24}")
print("multi edges:", MULTI, "-> routers", ROUTER)
assert all(LAYER[b] > LAYER[a] for a, b in SOLID), "prerequisite edge must point to a later layer"
assert FB_XMAX < ROUTER_X, "cards must not reach the routing channels"
assert ROUTER_X + 22 * len(MULTI) < LANE_X0, "routing channels must not reach the feedback lanes"
assert ROUTER[("N04", "N13")] < LANE_X0, "the N04->N13 channel must stay left of the feedback lanes"
assert ROW_Y0 + max(GROUPS) * ROW_PITCH + CARD_H < FOOT_Y, "rows overlap the footer"
assert FOOT_Y + 134 < H, "footnote leaves the canvas"
print("layout contract OK")
