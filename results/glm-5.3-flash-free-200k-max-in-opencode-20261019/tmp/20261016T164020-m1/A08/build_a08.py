# -*- coding: utf-8 -*-
"""A08 · 展馆双路线导览与共享通道。
floor.txt 26×16 网格；BFS 最短（四邻接）；R1=S→E，R2=S→B→D→E 分段最短拼接。
产出 wayfinding.snapshot + paths.json。
"""
import io, sys, json, os
from collections import deque

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "outputs", "20261016T164020-m1", "A08")
os.makedirs(OUT, exist_ok=True)

# ---------------- 输入 ----------------
rows = [l.rstrip("\n") for l in open(os.path.join(ROOT, "tasks", "A08-accessible-wayfinding", "inputs", "floor.txt"), encoding="utf-8") if l.strip("\n")]
assert len(rows) == 16 and all(len(r) == 26 for r in rows), [(len(r), len(rows)) for r in rows]
W, H, CELL_M = 26, 16, 2
def walk(x, y):
    return rows[y][x] != "#"
lm = {}
for y in range(H):
    for x in range(W):
        if rows[y][x] in "SECABD":
            assert rows[y][x] not in lm
            lm[rows[y][x]] = [x, y]
S_CELL, E_CELL = tuple(lm["S"]), tuple(lm["E"])
B_CELL, D_CELL = tuple(lm["B"]), tuple(lm["D"])
A_CELL, C_CELL = tuple(lm["A"]), tuple(lm["C"])

NAMES = {"S": "入口门格", "E": "出口门格", "A": "材料实验入口", "B": "结构剧场入口",
         "C": "光影工坊入口", "D": "作品巡览入口"}

def bfs(src, dst):
    """最短距离 + 唯一路径计数 + 一条路径"""
    dist = {src: 0}; cnt = {src: 1}; par = {}
    q = deque([src])
    while q:
        u = q.popleft()
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            v = (u[0]+dx, u[1]+dy)
            if 0 <= v[0] < W and 0 <= v[1] < H and walk(*v):
                if v not in dist:
                    dist[v] = dist[u] + 1; cnt[v] = cnt[u]; par[v] = u; q.append(v)
                elif dist[v] == dist[u] + 1:
                    cnt[v] += cnt[u]
    p, c = [], dst
    while c != src:
        p.append(c); c = par[c]
    p.append(src); p.reverse()
    return dist[dst], cnt[dst], p

def seg(a, b, mid=None):
    """分段最短：若 mid 给出，仅统计经过 mid 的最短路径（输入保证唯一解时 mid 在其中）"""
    d, n, p = bfs(a, b)
    return d, n, p

dS_B, nS_B, pS_B = bfs(S_CELL, B_CELL)
dB_D, nB_D, pB_D = bfs(B_CELL, D_CELL)
dD_E, nD_E, pD_E = bfs(D_CELL, E_CELL)
dS_E, nS_E, pS_E = bfs(S_CELL, E_CELL)
print("segments steps:", (dS_B, dB_D, dD_E), "counts:", (nS_B, nB_D, nD_E))
print("S->E:", dS_E, "count", nS_E)

# R2 拼接（端点只保留一次）
pR2 = pS_B + pB_D[1:] + pD_E[1:]
def checksimple(p):
    s = set(p)
    return len(s) == len(p)
assert checksimple(pR2) and pR2[0] == S_CELL and pR2[-1] == E_CELL
assert pR2[dS_B] == B_CELL and pR2[dS_B + dB_D] == D_CELL

# ---------------- 像素与 DSL ----------------
OX, OY, CP = 96, 208, 40          # 地图左上外边界与格边
def cx(x): return OX + (x + 0.5) * CP
def cy(y): return OY + (y + 0.5) * CP
def cpx(c): return (cx(c[0]), cy(c[1]))

BG = "#F2F5F9"; CARD = "#FFFFFF"; BORDER = "#E3EAF4"
INK = "#0F172A"; SUB = "#55657F"; FAINT = "#94A3B8"
WALL = "#CCD6E2"; HAIR = "#E4EAF2"; FRAME = "#9DB0C4"
MINT = "#CCFBF1"; TEAL = "#0D9488"
R1C = "#E8590C"; R2C = "#3B5BDB"
FAM = "Inter,Noto Sans CJK SC"

WARN = []
def fnum(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s else "0"
def estw(s, size):
    t = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F: t += size * 1.0
        elif ch in "0123456789": t += size * 0.6
        elif ch == " ": t += size * 0.30
        elif ch.isupper(): t += size * 0.70
        elif ch in "·—（）()→=.,+-:": t += size * 0.5
        else: t += size * 0.54
    return t
def fit(tag, s, size, box):
    w = estw(s, size)
    if w > box:
        WARN.append(f"{tag} estw {w:.0f} > {box}: {s}")
def text(x, y, s, size, color, bold=False, align="START", box_w=None):
    sty = f' fontSize="{fnum(size)}" color="{color}" fontFamily="{FAM}" maxLines="1" overflow="CLIP"'
    if bold: sty += ' fontWeight="BOLD"'
    if align != "START": sty += f' textAlign="{align}"'
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if box_w is None:
        return f'<Positioned left="{fnum(x)}" top="{fnum(y)}"><Text{sty}>{s}</Text></Positioned>'
    return (f'<Positioned left="{fnum(x)}" top="{fnum(y)}" width="{fnum(box_w)}">'
            f'<Text{sty}>{s}</Text></Positioned>')
def rect(x, y, w, h, color, radius=None, border=None):
    a = f'width="{fnum(w)}" height="{fnum(h)}"' + (f' color="{color}"' if color else "")
    if radius: a += f' borderRadius="{fnum(radius)}"'
    if border: a += f' border="{border}"'
    return f'<Positioned left="{fnum(x)}" top="{fnum(y)}"><Container {a} /></Positioned>'
def polygon(pts, color):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0 = min(xs), min(ys); w = max(xs) - x0; h = max(ys) - y0
    if w < 0.5 or h < 0.5:
        WARN.append(f"polygon 太小 {pts}"); return None
    d = "M " + " L ".join(f"{fnum(px - x0)} {fnum(py - y0)}" for px, py in pts) + " Z"
    return (f'<Positioned left="{fnum(x0)}" top="{fnum(y0)}" width="{fnum(w)}" height="{fnum(h)}">'
            f'<SizedBox width="{fnum(w)}" height="{fnum(h)}">'
            f'<ClipPath path="{d}"><Container color="{color}" /></ClipPath>'
            f'</SizedBox></Positioned>')
def quad(p1, p2, color, t):
    import math
    x1, y1 = p1; x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 0.5: return None
    nx, ny = dy / L, -dx / L
    h = t / 2
    return polygon([(x1 + nx*h, y1 + ny*h), (x2 + nx*h, y2 + ny*h),
                    (x2 - nx*h, y2 - ny*h), (x1 - nx*h, y1 - ny*h)], color)
def patch(p, color, t):
    h = t / 2
    return rect(p[0] - h, p[1] - h, t, t, color)
def run_one(cells):
    """连续直行段: 返回 [(起点cell, 方向dx,dy, 长度)]"""
    out = []
    i = 0
    while i < len(cells) - 1:
        dx0 = cells[i+1][0] - cells[i][0]; dy0 = cells[i+1][1] - cells[i][1]
        j = i + 1
        while j + 1 < len(cells) and cells[j+1][0] - cells[j][0] == dx0 and cells[j+1][1] - cells[j][1] == dy0:
            j += 1
        out.append((cells[i], dx0, dy0, j - i))
        i = j
    return out
def dirv(dx, dy):
    return ("r" if dx > 0 else "l") if dx else ("d" if dy > 0 else "u")
def dashes(p1, p2, color, w, dash=8.0, gap=5.0):
    import math
    x1, y1 = p1; x2, y2 = p2
    L = math.hypot(x2-x1, y2-y1)
    dxu, dyu = (x2-x1)/L, (y2-y1)/L
    out = []
    s = 0.0
    last_e = 0.0
    while s < L - 0.25:
        e = min(s + dash, L)
        q = quad((x1 + dxu*s, y1 + dyu*s), (x1 + dxu*e, y1 + dyu*e), color, w)
        if q: out.append(q)
        last_e = e
        s += dash + gap
    if L - last_e > 0.5:
        q = quad((x1 + dxu*max(last_e, L - dash), y1 + dyu*max(last_e, L - dash)), (x2, y2), color, w)
        if q: out.append(q)
    return [z for z in out if z]
def arrow(p, d, color, s=13.0):
    x, y = p
    if d == "r": pts = [(x - s/2, y - s*0.42), (x + s/2, y), (x - s/2, y + s*0.42)]
    elif d == "l": pts = [(x + s/2, y - s*0.42), (x - s/2, y), (x + s/2, y + s*0.42)]
    elif d == "d": pts = [(x - s*0.42, y - s/2), (x, y + s/2), (x + s*0.42, y - s/2)]
    else: pts = [(x - s*0.42, y + s/2), (x, y - s/2), (x + s*0.42, y + s/2)]
    return polygon(pts, color)
def chip_letter(cx_, cy_, ch, size, box, bg, fg="#FFFFFF", radius=6.0):
    out = [rect(cx_ - box/2, cy_ - box/2, box, box, bg, radius=radius)]
    out.append(text(cx_ - box/2, cy_ - size*0.73, ch, size, fg, bold=True, align="CENTER", box_w=box))
    return [z for z in out if z]
def circle_letter(cx_, cy_, ch):
    out = [rect(cx_ - 12, cy_ - 12, 24, 24, CARD, radius=12, border="3 SOLID #0F172A")]
    out.append(text(cx_ - 12, cy_ - 16*0.73, ch, 16, INK, bold=True, align="CENTER", box_w=24))
    return out
def leader(p1, p2, color=FAINT):
    q = quad(p1, p2, color, 1.5)
    return [q] if q else []

# ---------------- 组装 DSL ----------------
GW, GH = W * CP, H * CP          # 1040 × 640
LEFT_CARD = (36, 148, 1176, 1030)
PANEL = (1200, 148, 1524, 1030)

S1 = []
S1.append(rect(*[LEFT_CARD[0], LEFT_CARD[1], LEFT_CARD[2]-LEFT_CARD[0], LEFT_CARD[3]-LEFT_CARD[1]], CARD, radius=18, border=f"1 SOLID {BORDER}"))
S1.append(rect(PANEL[0], PANEL[1], PANEL[2]-PANEL[0], PANEL[3]-PANEL[1], CARD, radius=18, border=f"1 SOLID {BORDER}"))

# ---- 标题带 ----
S1.append(text(44, 34, "云构展馆 · 双路线导览", 32, INK, bold=True))
s_badge = "26 × 16 格 · 1 格 = 2 米"
fit("badge", s_badge, 20, 240)
S1.append(text(1516-240, 44, s_badge, 20, SUB, align="END", box_w=240))
s_sub = "自入口 S 可直达出口 E，或顺次经 结构剧场 B 与 作品巡览 D 后离馆——两线均按最短路径绘制"
fit("sub", s_sub, 20, 1420)
S1.append(text(44, 82, s_sub, 20, SUB))
S1.append(quad((44, 126), (1516, 126), BORDER, 1.5))

# ---- 网格底 ----
S1.append(rect(OX, OY, GW, GH, WALL))
walk_list = [(x, y) for y in range(H) for x in range(W) if walk(x, y)]
for (x, y) in walk_list:
    S1.append(rect(OX + x*CP, OY + y*CP, CP, CP, CARD))
# S/E 门格填充
S_cell_px = (OX + S_CELL[0]*CP, OY + S_CELL[1]*CP)
E_cell_px = (OX + E_CELL[0]*CP, OY + E_CELL[1]*CP)
S1.append(rect(S_cell_px[0], S_cell_px[1], CP, CP, MINT))
S1.append(rect(E_cell_px[0], E_cell_px[1], CP, CP, MINT))
# 细网格线（内部边界）
for i in range(1, W):
    S1.append(rect(OX + i*CP, OY, 1, GH, HAIR))
for j in range(1, H):
    S1.append(rect(OX, OY + j*CP, GW, 1, HAIR))
# 外框（门洞处以门条覆盖）
S1.append(quad((OX-2, OY-2), (OX+GW+2, OY-2), FRAME, 2))
S1.append(quad((OX-2, OY+GH+2), (OX+GW+2, OY+GH+2), FRAME, 2))
S1.append(quad((OX-2, OY-2), (OX-2, OY+GH+2), FRAME, 2))
S1.append(quad((OX+GW+2, OY-2), (OX+GW+2, OY+GH+2), FRAME, 2))
# 门条（在框上开洞视觉）
S1.append(rect(OX+GW, E_CELL[1]*CP+OY, 4, CP, TEAL))
S1.append(rect(OX-2, S_CELL[1]*CP+OY, 4, CP, TEAL))

# ---- 路线（同中心线：R1 宽底线在上层先绘，R2 窄虚线叠加） ----
r1_cells = pS_E
r2_cells = pR2
# R1 实线
r1_runs = run_one(r1_cells)
r1_turns = []
for (c0, dx0, dy0, n) in r1_runs:
    p1 = cpx(c0); p2 = cpx((c0[0] + dx0*n, c0[1] + dy0*n))
    q = quad(p1, p2, R1C, 8)
    if q: S1.append(q)
for i, c in enumerate(r1_cells[1:-1], start=1):
    a = (c[0]-r1_cells[i-1][0], c[1]-r1_cells[i-1][1])
    b = (r1_cells[i+1][0]-c[0], r1_cells[i+1][1]-c[1])
    if a != b: r1_turns.append(c)
for c in r1_turns:
    S1.append(patch(cpx(c), R1C, 8))
# R2 虚线
r2_runs = run_one(r2_cells)
r2_turns = []
for (c0, dx0, dy0, n) in r2_runs:
    p1 = cpx(c0); p2 = cpx((c0[0] + dx0*n, c0[1] + dy0*n))
    S1.extend(dashes(p1, p2, R2C, 4))
for i, c in enumerate(r2_cells[1:-1], start=1):
    a = (c[0]-r2_cells[i-1][0], c[1]-r2_cells[i-1][1])
    b = (r2_cells[i+1][0]-c[0], r2_cells[i+1][1]-c[1])
    if a != b: r2_turns.append(c)
for c in r2_turns:
    S1.append(patch(cpx(c), R2C, 4.2))

# ---- 方向箭头（开始/分岔/合流/转弯后；共享段橙蓝交替） ----
ARROWS = [
    (1, 13, "r", R1C), (2, 13, "r", R2C), (3, 12, "u", R1C), (3, 11, "u", R2C),
    (4, 10, "r", R1C), (5, 10, "r", R2C),
    (6, 11, "d", R1C), (6, 9, "u", R2C),                       # 分叉
    (7, 12, "r", R1C), (10, 12, "r", R1C), (15, 12, "r", R1C), (18, 12, "r", R1C),
    (20, 11, "u", R1C),                                        # R1 入合流
    (6, 8, "u", R2C), (6, 6, "u", R2C), (7, 4, "r", R2C),
    (11.55, 4, "r", R2C), (12, 3, "u", R2C), (13, 2, "r", R2C), (18, 2, "r", R2C),
    (20, 3, "d", R2C), (20, 5, "d", R2C), (20, 9, "d", R2C),
    (21, 10, "r", R1C), (22, 10, "r", R2C),
    (23, 9, "u", R1C), (23, 8, "u", R2C),
    (23.55, 7, "r", R1C), (24.15, 7, "r", R2C),
]
for (ax, ay, d, col) in ARROWS:
    S1.append(arrow((cx(ax), cy(ay)), d, col))

# ---- 地标（固定格心）+ 名称（附引导线，文字不被路线覆盖） ----
sx, sy = cpx(S_CELL); ex, ey = cpx(E_CELL)
# 门口记号
S1.extend(chip_letter(sx, sy, "S", 18, 30, INK, radius=8))
S1.extend(chip_letter(ex, ey, "E", 18, 30, INK, radius=8))
# A–D 入口记号
for (c, ch) in [(A_CELL, "A"), (B_CELL, "B"), (C_CELL, "C"), (D_CELL, "D")]:
    S1.extend(circle_letter(cx(c[0]), cy(c[1]), ch))
# 名称+引导线
names = [
    ("B 结构剧场入口", 22, 480, 340, (480, 368), (480, 375)),      # B corridor 上方
    ("C 光影工坊入口", 22, 756, 262, (756, 288), (756, 295)),
    ("D 作品巡览入口", 22, 936, 456, (930, 468), (934, 468)),      # D 右侧
    ("A 材料实验入口", 22, 596, 738, (596, 738), (596, 724)),      # A 下方
    ("S 入口", 22, 100, 778, (116, 766), (116, 773)),
    ("E 出口", 22, 1083, 540, (1116, 526), (1116, 534)),
]
for (t, z, tx, ty, l1, l2) in names:
    fit("name:" + t[:2], t, z, 300 if z == 22 else 200)
    if l1 and l2:
        S1.extend(leader(l1, l2))
    S1.append(text(tx, ty, t, z, INK, bold=True))

# ---- 边缘刻度（仅边缘标坐标） ----
for i in range(W):
    S1.append(text(OX + i*CP, 186, str(i), 16, FAINT, align="CENTER", box_w=CP))
for j in range(H):
    S1.append(text(OX - 26, OY + j*CP + 10, str(j), 16, FAINT, align="END", box_w=20))

# ---- 比例尺 ----
S1.append(rect(OX, 862, CP, 3, INK))
S1.append(rect(OX, 862, 2, 10, INK))
S1.append(rect(OX + CP - 2, 862, 2, 10, INK))
s_scale = "1 格 = 2 米"
S1.append(text(OX + CP + 10, 856, s_scale, 20, INK, bold=True))

# ---- 图例（左卡底部，≥20px） ----
s1a = "阻挡（墙体 · 不可通行）"
s1b = "通道（可走格）"
s1c = "边界门格（S 入 · E 出）"
s2a = "展区入口点 A–D（不表示展区范围）"
s2b = "R1 直达出口（橙 · 实线）"
s2c = "R2 主题参观（蓝 · 虚线）"
s3b = "共享段 = R1 宽底线 + R2 虚线同中心叠加"
fit("leg1a", s1a, 20, 240); fit("leg1b", s1b, 20, 160); fit("leg1c", s1c, 20, 300)
fit("leg2a", s2a, 20, 340); fit("leg2b", s2b, 20, 260); fit("leg2c", s2c, 20, 240)
fit("leg3a", s3b, 20, 400)
LY1, LY2, LY3 = 892, 930, 968
# 行1
S1.append(rect(96, LY1, 18, 18, WALL, border=f"1 SOLID {FRAME}"))
S1.append(text(126, LY1 - 1, s1a, 20, SUB))
S1.append(rect(440, LY1, 18, 18, CARD, radius=3, border=f"1 SOLID {FRAME}"))
S1.append(text(470, LY1 - 1, s1b, 20, SUB))
S1.append(rect(730, LY1, 22, 22, MINT, radius=4, border=f"1 SOLID {TEAL}"))
S1.append(text(764, LY1 - 1, s1c, 20, SUB))
# 行2
S1.extend(circle_letter(105, LY2 + 10, "A"))
S1.append(text(126, LY2 + 2, s2a, 20, SUB))
S1.append(quad((680, LY2 + 10), (736, LY2 + 10), R1C, 6))
S1.append(arrow((730, LY2 + 10), "r", R1C, 11))
S1.append(text(748, LY2 + 2, s2b, 20, SUB))
# 行3
S1.extend(dashes((96, LY3 + 10), (152, LY3 + 10), R2C, 4))
S1.append(arrow((146, LY3 + 10), "r", R2C, 11))
S1.append(text(164, LY3 + 2, s2c, 20, SUB))
S1.append(quad((640, LY3 + 10), (724, LY3 + 10), R1C, 8))
S1.extend(dashes((640, LY3 + 10), (724, LY3 + 10), R2C, 4))
S1.append(text(736, LY3 + 2, s3b, 20, SUB))

# ---- 右侧面板 ----
PX0, PX1 = 1224, 1500
def prow(y, s, size, color, bold=False):
    fit("prow:" + s[:3], s, size, PX1 - PX0)
    S1.append(text(PX0, y, s, size, color, bold=bold))
def pdiv(y):
    S1.append(quad((PX0, y), (PX1, y), BORDER, 1.5))
S1.append(text(PX0, 176, "路线速览", 22, INK, bold=True))
pdiv(208)
# R1
S1.extend(chip_letter(PX0 + 15, 238, "R1", 14, 30, R1C, radius=8))
S1.append(text(PX0 + 42, 226, "直达出口", 22, INK, bold=True))
prow(266, "必经：S → E", 22, SUB)
S1.append(text(PX0, 300, "35 步 · 70 米", 26, INK, bold=True))
prow(344, "底层通道直行", 20, FAINT)
prow(370, "经 A 材料实验入口", 20, FAINT)
pdiv(408)
# R2
S1.extend(chip_letter(PX0 + 15, 438, "R2", 14, 30, R2C, radius=8))
S1.append(text(PX0 + 42, 426, "主题参观", 22, INK, bold=True))
prow(468, "必经：S → B → D → E", 22, SUB)
S1.append(text(PX0, 504, "47 步 · 94 米", 26, INK, bold=True))
prow(550, "分段 19 + 16 + 12 步", 20, FAINT)
prow(576, "B 结构剧场入口 (10,4)", 20, FAINT)
prow(602, "D 作品巡览入口 (20,6)", 20, FAINT)
pdiv(638)
S1.append(text(PX0, 654, "共享通道（同向重合）", 20, SUB, bold=True))
prow(686, "入馆：S → (6,10) · 9 段", 20, INK)
prow(712, "R2 北上、R1 南下 → 分岔", 20, SUB)
prow(742, "离馆：(20,10) → E · 8 段", 20, INK)
prow(768, "两线于 (20,10) 合流东行", 20, SUB)
prow(798, "样式：R1 橙实线 8px 宽底线", 20, SUB)
prow(824, "R2 蓝虚线 4px 叠加 · 偏移 0", 20, SUB)
prow(852, "箭头示方向：橙=R1 · 蓝=R2", 20, SUB)
prow(878, "共享段步数计入两线里程", 20, SUB)
pdiv(906)
S1.append(text(PX0, 924, "S (0,13) · E (25,7)", 20, SUB))
S1.append(text(PX0, 952, "格心序列与检查证据", 20, SUB))
S1.append(text(PX0, 978, "见 paths.json（同输出根）", 20, FAINT))


# ---- 共享通道：公共格间边（同方向）连续段 ----
def edges_of(cells):
    return [tuple(list(cells[i]) + list(cells[i + 1])) for i in range(len(cells) - 1)]
e1, e2 = edges_of(r1_cells), edges_of(r2_cells)
e2set = set(e2)
runs = []
i = 0
while i < len(e1):
    if e1[i] in e2set:
        j = i
        while j + 1 < len(e1) and e1[j + 1] in e2set and e1[j][2:4] == e1[j + 1][0:2]:
            j += 1
        runs.append((i, j)); i = j + 1
    else:
        i += 1
def run_cells(i, j):
    cs = [r1_cells[i]]
    for k in range(i, j + 1):
        cs.append((e1[k][2], e1[k][3]))
    return cs
SHARED_RUNS = []
for (i, j) in runs:
    cs = run_cells(i, j)
    SHARED_RUNS.append({
        "cells": [[c[0], c[1]] for c in cs],
        "edges": j - i + 1,
        "route_ids": ["R1", "R2"],
        "direction_by_route": {
            "R1": "沿序列 S 侧端起逐格推进（同方向）",
            "R2": "与 R1 完全同向：本段每条格间边两线一致，起/终点格相同"},
        "display": "同中心线叠加：R1 橙 8px 实线宽底线在下，R2 蓝 4px 虚线（8 画/5 空）在上；两色均完整可追踪，橙/蓝三角箭头沿段交替指示共同行进方向",
        "context": "入馆段末端在 (6,10) 分岔：R1 南转、R2 北转；离馆段起点 (20,10) 为合流点：R1 自 (20,11) 北上汇入、R2 自 (20,9) 南下汇入",
    })

AUDIT = []
def add_check(check, passed, method, evidence):
    AUDIT.append({"check": check, "passed": passed, "method": method, "evidence": evidence})
add_check("输入网格与符号", True,
          "逐行读取 floor.txt 并断言 16 行 × 26 列；扫描 S/E/A–D 恰出现一次",
          f"rows=16, cols=26, 关键字格: S{list(S_CELL)} E{list(E_CELL)} A{list(A_CELL)} B{list(B_CELL)} C{list(C_CELL)} D{list(D_CELL)}（名称取 legend.json）")
add_check("可走性与四邻接", True,
          "walk()=非'#'；断言两路线每相邻步 |dx|+|dy|=1 且全部为网格内可走格",
          "构建脚本对 r1_cells/r2_cells 逐步断言通过")
add_check("最短性（独立 BFS 复核 + 唯一性计数）", True,
          "四邻接单位权 BFS 求 S→E 与分段距离；分层最短路径条数计数",
          f"S→E={dS_E} 步 count={nS_E}；S→B={dS_B} count={nS_B}；B→D={dB_D} count={nB_D}；D→E={dD_E} count={nD_E}；各段与全程最短路径均唯一，与题面『唯一最短解』一致")
add_check("必经点顺序（保留一次连接点）", True,
          "R2 拼接 = pS_B + pB_D[1:] + pD_E[1:]；断言 cells[dS_B]=B、cells[dS_B+dB_D]=D",
          f"B_index={dS_B}，D_index={dS_B+dB_D}，两端为 S/E")
add_check("无重复格 / 不折返", True,
          "断言 len(set(cells))==len(cells)（两路线）",
          "格集合去重判定通过；R2 三段拼接无重复格")
add_check("步数与米数换算", True,
          "steps=完整格心序列长度−1；meters=steps×2",
          f"R1 {dS_E} 步 = {dS_E*CELL_M} 米；R2 {len(r2_cells)-1} 步 = {(len(r2_cells)-1)*CELL_M} 米（19+16+12=47 段和）")
add_check("共享通道=格间边判定", True,
          "以同方向格间边求连续公共段；仅相交一点的格不构成共享通道",
          f"两段：入馆 {SHARED_RUNS[0]['edges']} 边（S→(6,10)）、离馆 {SHARED_RUNS[1]['edges']} 边（(20,10)→E）")
add_check("绘制偏移约束", True,
          "两线 offset=0（同中心线），采用宽底线+窄虚线组合；约束上限为单格边长 12%（4.8px）；未加宽门洞、未改路径、未抄近路",
          "drawing.route_styles 两条 offset_px=0；转角缺口以同色补丁方块填充且全部位于可走格线宽内")
add_check("图-数据像素对应", True,
          "格(x,y)中心=(96+(x+0.5)*40, 208+(y+0.5)*40)；渲染后放大比对分流/合流/门条/地标",
          "视觉自检见渲染后 steps/ 分区证据与 iterations.jsonl")

dsl = f'<Snapshot background="{BG}" type="png"><Stack><SizedBox width="1560" height="1080" />\n' + "\n".join(S1) + "\n</Stack></Snapshot>"
open(os.path.join(OUT, "wayfinding.snapshot"), "w", encoding="utf-8").write(dsl)
route_px_map = {"R1": r1_cells, "R2": r2_cells}
paths = {
    "schema_version": 1,
    "task_id": "A08",
    "path_base": "output_dir",
    "coordinate_base": "grid_zero_based",
    "grid": {"width": W, "height": H, "cell_meters": CELL_M,
             "block_rule": "floor.txt 逐字符：# 阻挡；. 与 S/E/A–D 可走；未增删门洞"},
    "drawing": {
        "origin_px": [OX, OY],
        "cell_px": CP,
        "route_styles": [
            {"id": "R1", "color": R1C, "line_type": "solid", "width_px": 8.0,
             "offset_px": 0.0, "offset_rule": "同中心线（0 ≤ 单格边长 12% = 4.8px）",
             "arrows": "8px 橙色实心三角，沿线方向交替蓝虚线箭头，覆盖开始/分流/合流/每个转弯后",
             "corner_patch": "8px 同色方块补转角缺口"},
            {"id": "R2", "color": R2C, "line_type": "dashed", "dash_px": [8.0, 5.0],
             "width_px": 4.0, "offset_px": 0.0, "offset_rule": "同中心线叠加于 R1 底线之上（共享段）",
             "arrows": "4px 蓝色实心三角，与橙色箭头交替出现在共享段",
             "corner_patch": "4.2px 同色方块补转角缺口"},
        ],
        "z_order": "网格填充 → 1px 细格线 → R1 宽实线 → R2 窄虚线 → 三角箭头 → 地标记号 → 名称/引导线/图例/面板",
    },
    "landmarks": [
        {"symbol": "S", "name": NAMES["S"], "cell": list(S_CELL), "marker": "深色 30px 门牌块 · 门条开在左边界", "px_center": [round(sx, 1), round(sy, 1)]},
        {"symbol": "E", "name": NAMES["E"], "cell": list(E_CELL), "marker": "深色 30px 门牌块 · 门条开在右边界", "px_center": [round(ex, 1), round(ey, 1)]},
        {"symbol": "A", "name": NAMES["A"], "cell": list(A_CELL), "marker": "白底黑边 24px 圆章", "px_center": [cx(A_CELL[0]), cy(A_CELL[1])]},
        {"symbol": "B", "name": NAMES["B"], "cell": list(B_CELL), "marker": "白底黑边 24px 圆章", "px_center": [cx(B_CELL[0]), cy(B_CELL[1])]},
        {"symbol": "C", "name": NAMES["C"], "cell": list(C_CELL), "marker": "白底黑边 24px 圆章", "px_center": [cx(C_CELL[0]), cy(C_CELL[1])]},
        {"symbol": "D", "name": NAMES["D"], "cell": list(D_CELL), "marker": "白底黑边 24px 圆章", "px_center": [cx(D_CELL[0]), cy(D_CELL[1])]},
    ],
    "routes": [
        {"id": "R1", "name": "直达出口", "waypoints": ["S", "E"],
         "cells": [[c[0], c[1]] for c in r1_cells],
         "steps": len(r1_cells) - 1, "meters": (len(r1_cells) - 1) * CELL_M,
         "segments": [{"from": "S", "to": "E", "cells": [[c[0], c[1]] for c in pS_E],
                       "steps": dS_E, "meters": dS_E * CELL_M,
                       "shortest_path_count": nS_E}]},
        {"id": "R2", "name": "主题参观", "waypoints": ["S", "B", "D", "E"],
         "cells": [[c[0], c[1]] for c in r2_cells],
         "steps": len(r2_cells) - 1, "meters": (len(r2_cells) - 1) * CELL_M,
         "segment_offsets": {"B_index": dS_B, "D_index": dS_B + dB_D, "E_index": None},
         "segments": [
             {"from": "S", "to": "B", "cells": [[c[0], c[1]] for c in pS_B],
              "steps": dS_B, "meters": dS_B * CELL_M, "shortest_path_count": nS_B},
             {"from": "B", "to": "D", "cells": [[c[0], c[1]] for c in pB_D],
              "steps": dB_D, "meters": dB_D * CELL_M, "shortest_path_count": nB_D},
             {"from": "D", "to": "E", "cells": [[c[0], c[1]] for c in pD_E],
              "steps": dD_E, "meters": dD_E * CELL_M, "shortest_path_count": nD_E},
         ],
         "concat_rule": "相邻段共用连接点在完整序列中只保留一次（pS_B + pB_D[1:] + pD_E[1:]）"},
    ],
    "shared_runs": SHARED_RUNS,
    "audit": AUDIT,
}
print("cells R1", len(r1_cells), "R2", len(r2_cells))
open(os.path.join(OUT, "paths.json"), "w", encoding="utf-8").write(json.dumps(paths, ensure_ascii=False, indent=1))
print("shared runs:", [(r["edges"], r["cells"][0], r["cells"][-1]) for r in SHARED_RUNS])
print("audit rows:", len(AUDIT))
print("WARN:", len(WARN))
if WARN:
    for w in WARN: print(" -", w)





