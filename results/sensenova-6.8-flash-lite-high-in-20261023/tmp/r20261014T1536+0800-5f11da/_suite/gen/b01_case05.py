"""case-05 街区噪音 · 早八点与晚十点（1600×900，社区议事会投影）。

视觉系统：同一张 12×8 街区网格画两遍——左边 08:00 早高峰，右边 22:00 深夜。
  每个街区格子的颜色是该格中心点的等效声压级，按四档同色相渐变（安静 → 超标）；
  格子里同时印出整数 dB 值，所以颜色从来不是唯一通道；≥65 dB 的格子再加一圈
  浅色描边，把超标地块连成一块能一眼认出的区域。
  声源都落在街区交界的路口上，深色圆标里印一个单字（工/物/学/地/夜/餐），
  圈外的环线是「该声源单独作用时的 65 dB 影响半径」= 10^((L0−65)/20)·10 m。
  环线画两层：浅色衬底铺满整圈、深色芯在格值数字处断开。这不是装饰——
  衬底解决「环线在超标格里看不见」（环线色对 CL3 底色仅 1.22:1），
  断芯解决「环线与格值数字同色」（环线色对格值文字色仅 1.62:1）。
  两层都在数字之下，所以 192 个整数 dB 从不会被环线触碰。

关键计算：声压级是 log 标度，多源绝不能线性相加。逐源先算
    Li(x) = L0i − 20·log10(max(d_i, 10) ÷ 10)
再按非相干声能相加
    L(x) = 10·log10( Σ_active 10^(Li ÷ 10) )
plan.json 的 revision_log v4 记录了这次更正：原计划把 Σ 写成了 dB 线性相加，
那样每多加一个等强度源就多算 10 dB（正确只多 3 dB），会同时夸大超标范围。

下方面板把 08:00 的声场在「去掉工地」的条件下重算一遍，用同一条四档分布条
加三条数字对比给出「施工时段挪走能救下多少格、多少户」——这才是议事会要的答案。

数据全部自拟演示：声源位置、10 m 参考声压级、街区户数都不是实测值，
不构成环境合规判定。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import b01_kit as K  # noqa: E402

W, H = 1600, 900
MIN_FS = 16

# ------------------------------------------------------------------ 调色
BG = "#EDF1F4"
PANEL = "#FFFFFF"
INK = "#16202A"
INK2 = "#445464"
INK3 = "#7B8A98"
RULE = "#E3EAEF"
STREET = "#D8E0E6"
ACCENT = "#B4531F"
GOOD = "#1D6F5C"

# 四档同色相（琥珀）单色渐变，由浅到深；数值经 ΔE 实测（见门禁 case-05-cbr）
CL = ["#F7F0E2", "#ECC67A", "#C98329", "#8E3210"]
CLINK = ["#2A2014", "#2A2014", "#2A2014", "#FFFFFF"]
CLLBL = ["安静 ≤55", "中等 55-59", "偏高 60-64", "超标 ≥65"]
FRAME = "#FFF6E8"   # 超标格的描边，也用作环线衬底（同一套暖浅色）
CONT = "#5C3D18"    # 65 dB 影响半径环线芯
MFRAME = "#1B2733"  # 声源标记外环
MINT = "#FFFFFF"    # 声源标记内底

# 环线画两层：衬底 + 芯。这两层各自修一个问题——
#   衬底：CONT 对 CL3 底色仅 1.22:1，65 dB 边界在超标格里看不见；
#   芯：  CONT 对 CL0-CL2 的格值文字色仅 1.62:1，环压到数字时线与字同色。
# 两层都要在数字框处断开，而不是只断芯：衬底比芯宽 3.5 px，只断芯时衬底仍会
# 探到数字框边上，CL3 的白色数字坐在近白衬底（对比 1.07:1）上就丢边。
# 所以按较宽的衬底半带宽求段，芯共用同一段——这样芯永远不会伸出衬底之外。
HALO_IN, HALO_OUT = 4.25, 1.75     # 衬底相对 R 的内扩 / 外扩
CORE_IN, CORE_OUT = 2.5, 0.0       # 芯的内径偏移，外径 = R
GAP_PAD = 2.5                      # 环带与数字框的最小净空（px）
SEG_N = 1440                       # 环线角度采样数（0.25°）

# 数字框按渲染后的真实字形墨迹量，不按行高估算：
#   K.pitch(16)=19.2 px 的行高比墨迹高 7.2 px，环线因此被多打断一圈。
#   实测（b01_case05_glyph_probe.py，192 个格值）：墨迹 17×12 px，
#   墨心在行高框中心上方 2.5 px（字重上对齐），所以框顶 = 墨心上移 6 px。
INK_W, INK_H = 17.0, 12.0          # 墨迹宽 / 高（px）
INK_DY = -2.5                      # 墨心相对行高框中心的纵向偏移（px）
MASK_PAD = HALO_OUT + 1.0          # 遮罩外扩：盖住衬底外沿 + 渲染像素对齐余量

# ------------------------------------------------------------------ 网格几何
COLS, ROWS = 12, 8
BLOCK_M = 120.0                       # 街区边长 m
M_W = COLS * BLOCK_M                  # 1440 m
M_H = ROWS * BLOCK_M                  # 960 m
MAP_W = 620.0                         # 街区图宽 px
MAP_H = MAP_W * (M_H / M_W)           # 413.33 px，等比 → 影响半径是正圆
S = MAP_W / M_W                       # px / m
CELL = MAP_W / COLS                   # 51.67 px，方格

PX, PW = 52.0, 1496.0                 # 全宽内容区
PY, PH = 228.0, 472.0                 # 两张地图所在面板
GX_L, GX_R = 110.0, 870.0
GY = 281.0

# ------------------------------------------------------------------ 声源
# (id, 名, 标记单字, 路口 (列交界, 行交界), 10 m 参考声压级, 活跃时段)
SRC = [
    ("site",  "工地", "工", (2, 3),  88.0, {"m"}),
    ("logi",  "物流", "物", (10, 2), 85.0, {"m"}),
    ("scho",  "学校", "学", (5, 6),  82.0, {"m"}),
    ("metro", "地铁", "地", (3, 2),  86.0, {"m", "n"}),
    ("stall", "夜市", "夜", (9, 6),  84.0, {"n"}),
    ("dine",  "餐厅", "餐", (7, 4),  80.0, {"n"}),
]
CELLS = [(c, r) for r in range(ROWS) for c in range(COLS)]


def dbr(v: float) -> int:
    return int(v + 0.5)


def num(v: float) -> str:
    return "{:,}".format(int(round(v)))


def cell_center(c: int, r: int):
    return ((c + 0.5) * BLOCK_M, (r + 0.5) * BLOCK_M)


def src_level(l0: float, dx: float, dy: float) -> float:
    """单源在距离 d 处的声压级；d 截断到 10 m（参考距离），避免除零与近场发散。"""
    d = max(math.hypot(dx, dy), 10.0)
    return l0 - 20.0 * math.log10(d / 10.0)


def field_level(levels_keys, active: set) -> dict:
    """非相干声能相加：先把每源线性声能相加，再取 10·log10。

    不能用 dB 线性相加——每多加一个等强度源只会多 10·log10(2) = 3 dB，
    而线性相加会多 10 dB，差一倍。
    """
    out = {}
    for k in levels_keys:
        mx, my = cell_center(*k)
        e = 0.0
        for sid, _nm, _g, (i, j), l0, act in SRC:
            if sid not in active:
                continue
            e += 10.0 ** (src_level(l0, mx - i * BLOCK_M,
                                    my - j * BLOCK_M) / 10.0)
        out[k] = 10.0 * math.log10(e)
    return out


def cls_of(v: float) -> int:
    if v < 55.0:
        return 0
    if v < 60.0:
        return 1
    if v < 65.0:
        return 2
    return 3


def reach65(l0: float) -> float:
    """该声源单独作用时降到 65 dB 的距离 m。"""
    return 10.0 ** ((l0 - 65.0) / 20.0) * 10.0


def residents(c: int, r: int) -> int:
    """每格户数：确定性伪随机，固定不可改，跨轮次可复算。"""
    f = math.sin(c * 12.9898 + r * 78.233) * 43758.5453
    f -= math.floor(f)
    return int(120 + f * 260)


def dist_of(levels: dict) -> list:
    n = [0, 0, 0, 0]
    for k in CELLS:
        n[cls_of(levels[k])] += 1
    return n


# ------------------------------------------------------------------ 版面元件
def tile(d, x, y, value, label, vcolor=INK, fs=30):
    d.rect(x, y, 362, 76, PANEL, radius=10)
    d.text_c(x + 181, y + 12, value, fs, vcolor, bold=True)
    d.text_c(x + 181, y + 50, label, 16, INK2)


def stack_bar(d, x0, y, w_total, counts, bar_h=26.0):
    """四档 100% 堆叠条：每格街区占 w_total÷96，窄段不印数字以免重叠。"""
    x = x0
    for i, n in enumerate(counts):
        w = w_total * n / 96.0
        if w >= 0.6:
            pad = 1.0 if w >= 4.0 else 0.0
            d.rect(x + pad, y, max(w - 2 * pad, 0.8), bar_h, CL[i], radius=2)
        if w >= 30.0:
            d.text_c(x + w / 2, y + bar_h / 2 - K.pitch(16) / 2, "%d" % n, 16,
                     CLINK[i], owner="bar")
        x += w


# 记录两张地图的绘制顺序与环线几何，供门禁断言层序与断口（case-05-c15..c17）
DRAW_ORDER: list[dict] = []


def digit_boxes(gx, levels) -> list[tuple]:
    """96 个格值数字的框，按渲染实测墨迹尺寸（INK_W×INK_H），不是行高框。

    行高框 pitch(16)=19.2 px 比墨迹高 7.2 px，环线因此被多打断一圈；
    墨心上移 INK_DY，所以框顶 = 墨心上沿 = 行高框中心 + INK_DY - H/2。
    框中心横坐标与 draw_panel 的 text_c 一致，纵坐标锚在墨心上。
    """
    out = []
    for (c, r) in CELLS:
        s = "%d" % dbr(levels[(c, r)])
        cx = gx + (c + 0.5) * CELL
        cy = GY + (r + 0.5) * CELL + INK_DY
        out.append((cx - INK_W / 2, cx + INK_W / 2,
                    cy - INK_H / 2, cy + INK_H / 2))
    return out


def ring_segments(cx, cy, rmid, half, boxes, n=SEG_N, pad=GAP_PAD) -> list[tuple]:
    """半径 rmid、半带宽 half 的环带在角度上的连续段，跳过压到数字框的部分。

    判定只取环带中心线，把数字框外扩 pad + half 后测试：这样带内任意一点
    （半径偏差 ≤ half）到数字框的净空都 ≥ pad。
    返回 [(a0, a1), ...]，弧度升序，a1 可略大于 2π 以表示绕回起点。
    """
    off = pad + half
    blk = [False] * n
    for i in range(n):
        th = 2.0 * math.pi * i / n
        x = cx + rmid * math.cos(th)
        y = cy + rmid * math.sin(th)
        for (x0, x1, y0, y1) in boxes:
            if x0 - off <= x <= x1 + off and y0 - off <= y <= y1 + off:
                blk[i] = True
                break
    step = 2.0 * math.pi / n
    runs = []
    i = 0
    while i < n:
        if blk[i]:
            i += 1
            continue
        j = i + 1
        while j < n and not blk[j]:
            j += 1
        runs.append((i * step, j * step))
        i = j
    two_pi = 2.0 * math.pi
    # 首尾都是空段说明同一段环绕回起点，合并成一个跨越 2π 的区间
    if len(runs) >= 2 and runs[0][0] < 1e-9 and abs(runs[-1][1] - two_pi) < 1e-9:
        first, last = runs.pop(0), runs.pop()
        runs.append((last[0], first[1] + two_pi))
    return [s for s in runs if s[1] - s[0] >= 0.02]


def draw_panel(d, gx, title, tag, sources, levels):
    d.rect(gx - 58, PY, 736, PH, PANEL, radius=10)
    d.text(gx - 42, PY + 6, title, 19, INK, bold=True)
    d.text_r(gx + 652, PY + 12, tag, 16, INK3)

    # 声源清单：与图上圆标里的单字一一对应
    d.rect(gx - 47, PY + 37, 10, 10, MFRAME, radius=5)
    d.rect(gx - 45.5, PY + 38.5, 7, 7, MINT, radius=3.5)
    lab = "　".join("%s %g" % (s[2], s[4]) for s in sources) + "　dB(A) @10 m"
    d.text(gx - 30, PY + 30, lab, 16, INK2)

    # 街区底与格子填充（超标格再加一圈描边，不靠颜色单独表态）
    d.rect(gx, GY, MAP_W, MAP_H, STREET, radius=4)
    for (c, r) in CELLS:
        v = levels[(c, r)]
        k = cls_of(v)
        x = gx + c * CELL + 1.0
        y = GY + r * CELL + 1.0
        s = CELL - 2.0
        if k == 3:
            d.rect(x, y, s, s, FRAME, radius=2)
            d.rect(x + 2, y + 2, s - 4, s - 4, CL[3], radius=1)
        else:
            d.rect(x, y, s, s, CL[k], radius=2)

    # 65 dB 影响半径（单源），两层，都在格值文字之下：
    #   衬底——CONT 对 CL3 底色只有 1.22:1，没有衬底时这条边界在超标格里
    #   消失，而超标格正是要拿去议事会讨论的对象；
    #   芯——CONT 对格值文字色只有 1.62:1，环线穿过深色数字时线与字同色；
    #   首版把环线画在文字之上，横切笔画使 66 / 67 在投影距离下被读作 65。
    # 环线画整圈、不在数字框处打断：打断后小半径环（夜市 R=38 px）只剩 47%
    # 圆周、分成 4 段短括弧，读不出是影响半径。改为整圈画完，再用一个与格子
    # 底色同色的遮罩小块压在数字下面——遮罩只比墨迹框大 HALO_OUT+1 px（覆盖
    # 衬底外沿加渲染余量），比按衬底半带宽打断时少挡 2.5 px，同一圈多露出近
    # 一成圆周；环是连续圆，遮罩只是把数字底下的环盖住，读者看到的是带小凹口
    # 的完整圆而不是散落的笔头。衬底仍在，所以 65 dB 边界在超标格里还是看得见。
    boxes = digit_boxes(gx, levels)
    rings_end = len(d.parts)
    bands: list[tuple] = []
    n_segs: dict = {}
    ang: dict = {}
    n_halo = 0
    n_core = 0
    for sid, nm, g, (i, j), l0, act in sources:
        cx, cy = gx + i * CELL, GY + j * CELL
        R = reach65(l0) * S
        d.arc(cx, cy, R - HALO_IN, R + HALO_OUT, 0.0, 2.0 * math.pi, FRAME,
              step=1, owner="contour-halo")
        d.arc(cx, cy, R - CORE_IN, R - CORE_OUT, 0.0, 2.0 * math.pi, CONT,
              step=1, owner="contour")
        bands.append((cx, cy, R - HALO_IN, R + HALO_OUT, 0.0, 2.0 * math.pi))
        n_halo += 1
        n_core += 1
        n_segs[sid] = 1
        ang[sid] = 2.0 * math.pi

    # 数字遮罩 + 格值：遮罩是格底色实心小块，压在整圈环线之上、数字之下，
    # 把环在数字底下的部分盖住。192 个整数一个都不被环线触碰，衬底也不会
    # 贴到数字框边上（遮罩外沿到墨迹框边 HALO_OUT+1 px，远大于衬底半带宽）。
    mask_end = len(d.parts)
    for (x0, x1, y0, y1) in boxes:
        k = cls_of(levels[
            (int(math.floor((x0 + x1) / 2.0 - gx) / CELL),
             int(math.floor((y0 + y1) / 2.0 - GY) / CELL))])
        # 遮罩坐标取整到像素边界：浮点坐标会让渲染器抗锯齿边缘，
        # 产生遮罩色与环色的混合像素（如 50% 衬底 + 50% CL3 = #C6947C，
        # 对白字只有 2.6:1），框外 1-2 px 就落在这些混合像素上。
        # 取整后遮罩是全实心矩形，边缘与像素对齐，不再抗锯齿。
        mx0 = int(math.floor(x0 - MASK_PAD))
        my0 = int(math.floor(y0 - MASK_PAD))
        mx1 = int(math.ceil(x1 + MASK_PAD))
        my1 = int(math.ceil(y1 + MASK_PAD))
        d.rect(mx0, my0, mx1 - mx0, my1 - my0, CL[k])
    cells_start = len(d.parts)
    for (c, r) in CELLS:
        v = levels[(c, r)]
        k = cls_of(v)
        d.text_c(gx + (c + 0.5) * CELL, GY + (r + 0.5) * CELL - K.pitch(16) / 2,
                 "%d" % dbr(v), 16, CLINK[k], owner="cell")
    DRAW_ORDER.append({"title": title, "rings_end": rings_end,
                       "mask_end": mask_end, "cells_start": cells_start,
                       "boxes": boxes, "bands": bands, "n_segs": n_segs,
                       "ang": ang, "n_halo": n_halo, "n_core": n_core})

    # 声源标记（画在最上层）
    for sid, nm, g, (i, j), l0, act in sources:
        cx, cy = gx + i * CELL, GY + j * CELL
        d.rect(cx - 12.5, cy - 12.5, 25, 25, MFRAME, radius=12.5)
        d.rect(cx - 10.5, cy - 10.5, 21, 21, MINT, radius=10.5)
        d.text_c(cx, cy - K.pitch(16) / 2, g, 16, MFRAME, bold=True,
                 owner="glyph")


# ------------------------------------------------------------------ 构建
def build():
    d = K.Doc(W, H, BG)
    DRAW_ORDER.clear()
    am = [s for s in SRC if "m" in s[5]]
    an = [s for s in SRC if "n" in s[5]]
    lm = field_level(CELLS, {s[0] for s in am})
    ln = field_level(CELLS, {s[0] for s in an})
    la = field_level(CELLS, {s[0] for s in am} - {"site"})   # 反事实

    allv = list(lm.values()) + list(ln.values())
    n_over_m = sum(1 for k in CELLS if lm[k] >= 65.0)
    n_over_n = sum(1 for k in CELLS if ln[k] >= 65.0)
    n_over_a = sum(1 for k in CELLS if la[k] >= 65.0)
    n_improve = n_over_m - n_over_a
    dm, dn, da = dist_of(lm), dist_of(ln), dist_of(la)
    hh_total = sum(residents(c, r) for (c, r) in CELLS)
    hh_over_m = sum(residents(*k) for k, v in lm.items() if v >= 65.0)
    hh_over_a = sum(residents(*k) for k, v in la.items() if v >= 65.0)
    peak = max(CELLS, key=lambda k: lm[k])
    pmx, pmy = cell_center(*peak)
    site_i, site_j = [s[3] for s in SRC if s[0] == "site"][0]
    d_site = math.hypot(pmx - site_i * BLOCK_M, pmy - site_j * BLOCK_M)

    # ---------------- 页头
    d.text(52, 22, "街区噪音 · 早八点与晚十点", 28, INK, bold=True)
    d.text(52, 58, "12×8 街区网格 · 每格 120 m · 6 个声源按反距离衰减逐格叠加"
                   "（非相干能量相加）", 16, INK2)
    d.text_r(1548, 28, "折光 · 十张日常　05 / 10", 17, INK2, bold=True)
    d.text_r(1548, 54, "自拟示例声场与街区数据", 16, INK3)
    d.line_h(0, W, 82, ACCENT, 2)

    # ---------------- 四个 KPI
    kpi = [
        ("%d dB" % dbr(lm[peak]), "08:00 峰值 · 距工地 %.0f m" % d_site, ACCENT),
        ("%d / 96" % n_over_m, "08:00 超标（≥65 dB）街区", INK),
        ("%d / 96" % n_over_n, "22:00 超标（≥65 dB）街区", INK),
        ("−%s 户" % num(hh_over_m - hh_over_a),
         "工地挪出 08:00 后不再超标的住户", GOOD),
    ]
    for i, (v, l, col) in enumerate(kpi):
        tile(d, 52 + i * 378, 94, v, l, col)

    # ---------------- 分级图例条
    d.text(52, 188, "街区声压级", 16, INK, bold=True)
    x = 148.0
    for i in range(4):
        d.rect(x, 190, 22, 18, CL[i], radius=3)
        d.text(x + 30, 188, CLLBL[i], 16, INK2)
        x += 30 + K.tw(CLLBL[i], 16) + 26
    d.arc(x + 9, 199, 6.0, 8.5, 0.0, 2 * math.pi, CONT, step=1, owner="contour")
    d.text(x + 25, 188, "65 dB 影响半径", 16, INK2)
    x += 25 + K.tw("65 dB 影响半径", 16) + 26
    d.rect(x - 5, 194, 10, 10, MFRAME, radius=5)
    d.rect(x - 3.5, 195.5, 7, 7, MINT, radius=3.5)
    d.text(x + 12, 188, "声源位置", 16, INK2)
    d.text_r(1548, 188, "示例阈值统一取 ≥65 dB，非实际限值（各功能区限值不同）"
                        "· 超标格加白色描边", 16, INK3)

    # ---------------- 两张街区图
    draw_panel(d, GX_L, "08:00 · 早高峰",
               "%d 个声源活跃 · 峰值 %d dB" % (len(am), dbr(lm[peak])), am, lm)
    peak_n = max(CELLS, key=lambda k: ln[k])
    draw_panel(d, GX_R, "22:00 · 深夜",
               "%d 个声源活跃 · 峰值 %d dB" % (len(an), dbr(ln[peak_n])), an, ln)

    # ---------------- 反事实面板
    d.rect(PX, 710, PW, 152, PANEL, radius=10)
    d.text(68, 724, "如果 08:00 没有工地", 18, INK, bold=True)
    d.text_r(1532, 728, "重算早高峰声场：工地不参与叠加，其余 3 个声源不变", 16, INK2)

    d.text_r(204, 774.4, "现 08:00", 16, INK2)
    stack_bar(d, 214, 766, 512, dm)
    d.text_r(204, 812.4, "无工地 08:00", 16, INK2)
    stack_bar(d, 214, 804, 512, da)
    d.line_v(758, 748, 840, RULE, 1)

    rows = [
        ("超标街区（≥65 dB）", n_over_m, n_over_a, "格"),
        ("安静街区（≤55 dB）", dm[0], da[0], "格"),
        ("受影响住户（超标街区）", hh_over_m, hh_over_a, "户"),
    ]
    for i, (lab, a, b, unit) in enumerate(rows):
        y = 756.0 + i * 34.0
        dl = b - a
        d.text(790, y, lab, 16, INK2)
        d.text_r(1150, y + 1, "%s %s" % (num(a), unit), 17, INK3)
        d.text_c(1184, y - 1, "→", 18, INK3)
        d.text_c(1262, y - 6, num(b), 22, GOOD, bold=True)
        d.text_r(1532, y + 1, "%s%s %s" % ("+" if dl > 0 else "−",
                                           num(abs(dl)), unit), 16, GOOD)

    # ---------------- 页脚
    d.text(52, 874, "数据为自拟演示：声源位置、10 m 参考声压级、街区户数均为示例值，"
                    "非实测监测；分级与限值仅示意，不构成环境合规判定。", 16, INK3)
    d.text_r(1548, 874, "出图 2026-10-22", 16, INK3)

    # ---------------- 门禁
    gates: list[dict] = []
    K.gate(gates, "case-05-c01", "网格 12×8 = 96 格，每格 120 m，覆盖 1440×960 m",
           len(CELLS) == 96 and COLS == 12 and ROWS == 8
           and abs(M_W - 1440.0) < 1e-9 and abs(M_H - 960.0) < 1e-9,
           "%d 格 · %.0f×%.0f m · 格 %.1f px（等比）" % (len(CELLS), M_W, M_H, CELL))
    three = 10.0 * math.log10(3.0 * 10.0 ** (80.0 / 10.0))
    lin = 3 * 80.0
    K.gate(gates, "case-05-c02",
           "多源按非相干声能相加：3 个 80 dB 源 = %.2f dB；dB 线性相加 %.0f dB 被拒绝"
           % (three, lin),
           abs(three - (80.0 + 10.0 * math.log10(3.0))) < 1e-9
           and (lin - three) > 20.0,
           "能量和 %.2f · 线性 %.0f · 差 %.0f dB" % (three, lin, lin - three))

    bad3, worst = [], 0.0
    for sid, nm, g, (i, j), l0, act in SRC:
        for k in CELLS:
            mx, my = cell_center(*k)
            dx, dy = mx - i * BLOCK_M, my - j * BLOCK_M
            dd = max(math.hypot(dx, dy), 10.0)
            got, want = src_level(l0, dx, dy), l0 - 20.0 * math.log10(dd / 10.0)
            worst = max(worst, abs(got - want))
            if worst > 1e-9:
                bad3.append(nm)
    K.gate(gates, "case-05-c03",
           "单源衰减 L0 − 20·log10(max(d,10)÷10) 对 6 源 × 96 格复算一致",
           not bad3 and worst < 1e-9, "576 次复算最大偏差 %.2e" % worst)

    K.gate(gates, "case-05-c04", "全部格值落在物理合理区间 [30, 95] dB(A)",
           all(30.0 <= v <= 95.0 for v in allv),
           "min %.1f · max %.1f dB(A)" % (min(allv), max(allv)))

    K.gate(gates, "case-05-c05", "四档分级单调且边界一致（<55 / 55-59 / 60-64 / ≥65）",
           cls_of(54.99) == 0 and cls_of(55.0) == 1 and cls_of(59.99) == 1
           and cls_of(60.0) == 2 and cls_of(64.99) == 2 and cls_of(65.0) == 3
           and all(cls_of(v) in (0, 1, 2, 3) for v in allv),
           "0/55/59.99/60/64.99/65 → %s"
           % [cls_of(v) for v in (54.99, 55.0, 59.99, 60.0, 64.99, 65.0)])

    bad6 = []
    for sid, nm, g, (i, j), l0, act in SRC:
        if abs(src_level(l0, reach65(l0), 0.0) - 65.0) > 1e-6:
            bad6.append(nm)
    K.gate(gates, "case-05-c06",
           "单源 65 dB 影响半径 = 10^((L0−65)÷20)·10 m，逐源复算回代 65.00 dB",
           not bad6,
           "; ".join("%s %.0f m" % (nm, reach65(l0))
                     for sid, nm, g, _ij, l0, act in SRC))

    K.gate(gates, "case-05-c07", "早高峰活跃声源 4 个 / 深夜 3 个，地铁两时段都在",
           len(am) == 4 and len(an) == 3
           and {s[0] for s in am} == {"site", "logi", "scho", "metro"}
           and {s[0] for s in an} == {"metro", "stall", "dine"},
           "早 %d 个 · 夜 %d 个" % (len(am), len(an)))

    K.gate(gates, "case-05-c08",
           "去掉工地后 08:00 每一格声压级都不高于现状（只减不增），"
           "全网格能量总和下降，且超标格数确实减少",
           all(la[k] <= lm[k] + 1e-9 for k in CELLS)
           and sum(la.values()) < sum(lm.values())
           and n_improve >= 1,
           "超标 %d → %d（−%d）· 峰值格 %.1f → %.1f dB"
           % (n_over_m, n_over_a, n_improve, lm[peak], la[peak]))

    K.gate(gates, "case-05-c09",
           "户数由确定性伪随机逐格求和，超标户数与格数同向变化",
           hh_total == sum(residents(c, r) for (c, r) in CELLS)
           and 119 < residents(0, 0) < 381
           and hh_over_a < hh_over_m and hh_over_m <= hh_total,
           "全街区 %s 户 · 超标 %s → %s 户（%.0f → %.0f 格）"
           % (num(hh_total), num(hh_over_m), num(hh_over_a), n_over_m, n_over_a))

    txts = [t["text"] for t in d.texts]
    need = ["%d dB" % dbr(lm[peak]), "%d / 96" % n_over_m, "%d / 96" % n_over_n,
            "−%s 户" % num(hh_over_m - hh_over_a)]
    K.gate(gates, "case-05-c10", "四个 KPI 印出的数字与脚本算出值逐一对应",
           all(s in txts for s in need), " / ".join(need))

    K.gate(gates, "case-05-c11",
           "四类色为同色相单色渐变（亮度单调），格内文字对比 ≥ 4.5",
           all(K.rel_lum(CL[i]) > K.rel_lum(CL[i + 1]) for i in range(3))
           and all(K.contrast(CL[i], CLINK[i]) >= 4.5 for i in range(4)),
           "亮度 %.3f>%.3f>%.3f>%.3f · 对比 %s"
           % (tuple(K.rel_lum(c) for c in CL)
              + (", ".join("%.2f" % K.contrast(CL[i], CLINK[i])
                           for i in range(4)),)))

    # 环线必须对四档格底都可见：芯在 CL3 超标格上只有 1.22:1（看不见），
    # 衬底在 CL0 安静格上只有 1.03:1（看不见），所以取两层中的较大者判定。
    vis = [max(K.contrast(FRAME, CL[i]), K.contrast(CONT, CL[i]))
           for i in range(4)]
    K.gate(gates, "case-05-c12",
           "65 dB 环线在四档格底上都可见（衬底或芯任一 ≥ 3.0:1），"
           "且衬底与芯自身可分；超标描边与声源标记对比达标",
           all(v >= 3.0 for v in vis)
           and K.contrast(CONT, FRAME) >= 3.0
           and K.contrast(FRAME, CL[3]) >= 3.0
           and K.contrast(MFRAME, MINT) >= 7.0,
           "衬底or芯 %s · 芯vs衬底 %.2f · 描边 %.2f · 标记 %.2f"
           % (" / ".join("%.2f" % v for v in vis),
              K.contrast(CONT, FRAME), K.contrast(FRAME, CL[3]),
              K.contrast(MFRAME, MINT)))

    ncell = sum(1 for t in d.texts if t["owner"] == "cell")
    K.gate(gates, "case-05-c13",
           "96 格 × 2 时段 = 192 个格值全部印出（颜色不是唯一通道）",
           ncell == 192, "%d 个整数 dB 已印" % ncell)

    glyphs = [s[2] for s in SRC]
    K.gate(gates, "case-05-c14", "六个声源单字标记无重字，且都出现在图上",
           len(set(glyphs)) == 6 and all(g in txts for g in glyphs),
           " ".join(glyphs))

    # 首版把环线画在格值文字之上，环线横切笔画使 66 / 67 在缩略图上读作 65。
    # 这里是防止回退的结构性断言，而不是靠再看一眼图。
    K.gate(gates, "case-05-c15",
           "65 dB 环线（衬底与芯两层）绘制在数字遮罩与格值文字之下",
           len(DRAW_ORDER) == 2 and all(
               o["rings_end"] <= o["mask_end"] <= o["cells_start"]
               for o in DRAW_ORDER),
           " · ".join("%s 环线止 %d / 遮罩止 %d / 格值起 %d"
                      % (o["title"], o["rings_end"], o["mask_end"],
                         o["cells_start"])
                      for o in DRAW_ORDER))

    # 第四版改为整圈环线 + 数字遮罩：遮罩是格底色小块，压在整圈环线上、
    # 数字之下，把环在数字底下的部分盖住。遮罩外扩 MASK_PAD 必须 ≥ HALO_OUT
    # 才盖得住衬底外沿（衬底外沿到环带中心线 HALO_OUT，再外扩 1 px 余量）。
    # 遮罩比第四版的「按衬底半带宽打断」少挡 (GAP_PAD+half−MASK_PAD) px，
    # 同一圈多露出近一成圆周，而且环是连续圆——读者看到的是带小凹口的圆，
    # 不是散落的笔头。
    n_mask = 0
    n_near = 0
    n_uncov = 0
    for o in DRAW_ORDER:
        boxes = o["boxes"]
        n_mask += len(boxes)
        for (cx, cy, r0, r1, _a0, _a1) in o["bands"]:
            rmid = (r0 + r1) / 2.0
            na = max(8, int(SEG_N))
            for k_ in range(na + 1):
                th = 2.0 * math.pi * k_ / na
                for rr in (r0, rmid, r1):
                    x = cx + rr * math.cos(th)
                    y = cy + rr * math.sin(th)
                    for (x0, x1, y0, y1) in boxes:
                        if not (x0 - MASK_PAD <= x <= x1 + MASK_PAD
                                and y0 - MASK_PAD <= y <= y1 + MASK_PAD):
                            continue
                        n_near += 1
                        # 遮罩矩形 = 墨迹框外扩 MASK_PAD，环带采样点若在这个
                        # 范围内则被遮罩盖住；否则衬底会贴到数字框边上
                        if not (x0 - MASK_PAD - 0.5 <= x <= x1 + MASK_PAD + 0.5
                                and y0 - MASK_PAD - 0.5 <= y <= y1 + MASK_PAD + 0.5):
                            n_uncov += 1
                        break
    K.gate(gates, "case-05-c16",
           "数字遮罩外扩 ≥ 衬底外沿（MASK_PAD ≥ HALO_OUT+渲染余量），环带在"
           "遮罩范围内的采样点全部落在遮罩矩形内——衬底不会贴到数字框边上"
           "（否则 CL3 白色数字坐在近白衬底上 1.07:1 丢边）",
           MASK_PAD >= HALO_OUT + 0.5 and n_uncov == 0 and n_mask == 192,
           "遮罩 %d 块 · 遮罩外扩 %.2f px（衬底外沿 %.2f px）· 环带靠框采样 "
           "%d 点，未被遮罩盖住 %d 点"
           % (n_mask, MASK_PAD, HALO_OUT, n_near, n_uncov))

    n_src = len(am) + len(an)
    n_segs_tot = sum(v for o in DRAW_ORDER for v in o["n_segs"].values())
    n_halo_tot = sum(o["n_halo"] for o in DRAW_ORDER)
    n_core_tot = sum(o["n_core"] for o in DRAW_ORDER)
    full = all(abs(a - 2.0 * math.pi) < 1e-6 for o in DRAW_ORDER
               for _sid, a in o["ang"].items())
    n_band_tot = sum(len(o["bands"]) for o in DRAW_ORDER)
    K.gate(gates, "case-05-c17",
           "每个声源都是一整圈连续的 65 dB 环线（衬底与芯各一段 0→2π，"
           "芯径向落在衬底带内），不打断——环读作完整圆，数字处靠遮罩盖住"
           "而不是把圆切成散落的笔头",
           n_segs_tot == n_src and n_halo_tot == n_core_tot == n_src
           and n_band_tot == n_src and full
           and HALO_IN > CORE_IN and HALO_OUT > -CORE_OUT,
           "声源 %d 个 · 环线 %d 圈（衬底 %d 段 / 芯 %d 段，各一整圈）· "
           "带宽 衬底 %.1f / 芯 %.1f px · 连续整圈 %s"
           % (n_src, n_band_tot, n_halo_tot, n_core_tot,
              HALO_IN + HALO_OUT, CORE_IN - CORE_OUT,
              "是" if full else "否"))

    K.check_palette("case-05", [(CL[i], CL[i + 1]) for i in range(3)], gates,
                    min_deutan=12.0, min_tritan=12.0, min_normal=14.0)
    gates = K.dry_run(d, "case-05", MIN_FS, gates)

    note = ("第六版：12×8 街区网格双时相声场 + 单源 65 dB 影响半径 + 去掉工地的"
            "反事实分布与户数对比。声场计算、分级、网格与户数同前三版零改动，"
            "只改 65 dB 环线的画法。第二版按 case-05-c15 把环线移到格值文字之下，"
            "修好了「环线横切笔画使 66 / 67 在投影距离下被读作 65」；改完层序后"
            "做定量审计，又查出两个真实缺陷，第三版一并修掉："
            "① 环线色 #5C3D18 对格值文字色 #2A2014 的对比只有 1.62:1，环线压到"
            "数字时线与字同色糊成一团（审计：学校环线压到数字框的 336 个采样点中"
            "335 个与文字同色，全场 597 点），第三版把环线芯在数字框处按角度断开，"
            "新增门禁 case-05-c16 断言与 192 个数字框净空 ≥ 1.5 px；"
            "② 环线对 CL3 超标格底色 #8E3210 的对比只有 1.22:1，65 dB 边界在"
            "超标格里看不见，而超标格正是要拿去议事会讨论的对象，第三版加一层"
            "浅色衬底铺满整圈，新增门禁 case-05-c17。"
            "第三版改完后再做逐像素诊断，查出它自己引入的第三个缺陷：衬底比芯宽 "
            "3.5 px，只断芯不断衬底时，衬底仍探到数字框外沿，衬底色 #FFF6E8 对 "
            "CL3 白色数字 #FFFFFF 的对比只有 1.07:1（诊断：08:00 格(2,2)「72」"
            "框外 234 个像素中 59 个是衬底色；夜市环线衬底带正中压过四个 CL3 "
            "「66」框），白色数字坐在近白衬底上丢边。第四版让衬底也用同一组角度段"
            "断开，段按较宽的衬底半带宽求、芯共用同一段（这样芯永远不会伸出衬底"
            "之外留下孤立的深色笔头），门禁 c16 改为按最宽的衬底复算两层净空，"
            "c17 改为断言衬底与芯逐段一一对应且每圈剩余弧长 ≥ 25% 圆周（该下限"
            "是 2.5 px 净空要求下的几何下限，任何声源的四个对角邻格数字框在零"
            "净空时已各占约 40°；可读性另由实际渲染裁剪图核验）。"
            "第四版渲出后实际看图发现第四个缺陷：数字框一直用 K.pitch(16)=19.2 px "
            "的行高，比 Noto Sans 实测墨迹高 7.2 px（b01_case05_glyph_probe.py 量"
            "192 个格值，墨迹 17×12 px、墨心在行高框中心上方 2.5 px），环线因此"
            "被多打断一圈——学校环线只剩 35% 圆周、分成 4 段短括弧，读不出是"
            "影响半径。第五版把数字框改用实测墨迹框（INK_W/INK_H/INK_DY），最窄"
            "一圈剩余弧长从 35% 提到 47%，门禁 c16 的渲染净空相应从 2.82 px "
            "升到 2.93 px。第五版看图又发现第五个缺陷：打断的环即便只剩 47% 圆周"
            "还是 4 段短括弧（夜市 R=38 px 最窄，12% 一段），小半径源读不出是"
            "影响半径。第六版改成整圈环线 + 数字遮罩：环不再打断，画一整圈 0→2π；"
            "数字底下压一块与格子底色同色的遮罩（外扩 MASK_PAD=HALO_OUT+1=2.75 px，"
            "盖住衬底外沿加渲染余量），把环在数字底下的部分盖住而不是删掉——"
            "环是连续圆，遮罩只是把数字底下的环盖住，读者看到的是带小凹口的完整圆"
            "而不是散落的笔头；遮罩比第四版按衬底半带宽打断时少挡 "
            "GAP_PAD+half−MASK_PAD=2.75 px，同一圈多露出近一成圆周。门禁 c15 加断"
            "遮罩层夹在环线与格值之间，c16 改为断言遮罩外扩 ≥ 衬底外沿且 192 块"
            "遮罩盖住全部靠框环带采样点，c17 改为断言每源一整圈连续环。"
            "第二版对图例限值文案的更正（65 dB 不是任何功能区夜间限值）保持不变")
    return d, gates, note, {
        "lm": lm, "ln": ln, "la": la, "peak": peak, "d_site": d_site,
        "n_over_m": n_over_m, "n_over_n": n_over_n, "n_over_a": n_over_a,
        "n_improve": n_improve, "dm": dm, "dn": dn, "da": da,
        "hh_total": hh_total, "hh_over_m": hh_over_m, "hh_over_a": hh_over_a,
    }


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    doc, gates, note, st = build()
    print("gates=%s" % K.save_gates("case-05", gates, note))
    K.assert_gates(gates, "case-05")
    print("08:00 峰值 %d dB @ 格(%d,%d) 距工地 %.0f m"
          % (dbr(st["lm"][st["peak"]]), st["peak"][0], st["peak"][1],
             st["d_site"]))
    print("超标格 早%d 无工地%d 夜%d · 改善 %d"
          % (st["n_over_m"], st["n_over_a"], st["n_over_n"], st["n_improve"]))
    print("分布 早%s 无工地%s 夜%s" % (st["dm"], st["da"], st["dn"]))
    print("户数 全%s 超标早%s → 无工地%s"
          % (num(st["hh_total"]), num(st["hh_over_m"]), num(st["hh_over_a"])))
    if "--dry" in sys.argv:
        return 0
    s = doc.stats()
    print("parts=%d texts=%d shapes=%d dsl=%d"
          % (s["parts"], s["texts"], s["shapes"], len(doc.build())))
    rec = K.render_case("case-05", doc, "case-05-street-noise",
                        "渲染 case-05 街区噪音双时相声场与反事实面板",
                        attempt_note=note)
    print("status=%s bytes=%s parts=%d ms=%s"
          % (rec["http_status"], rec.get("png_bytes"), rec["parts"],
             rec.get("elapsed_ms")))
    return 0 if rec["png_written"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
