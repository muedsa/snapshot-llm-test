"""B03 case-03：手电 AX-3 轴测拆解评审图版（1600×1000）。

受众：工业设计评审（判断装配顺序与零件命名）；情境：评审会上对着图版逐件过。
手法：Snapshot 透视矩阵不生效（探针 01c 实测），所以轴测体全部用 2D 仿射列向量拼：
三个单位基向量 e1/e2/e3 决定顶面、右下面、左下面的平行四边形，圆面用 (e2,e3) 剪切
圆得到椭圆盖。零件表里的质量、总长、重心全部由几何与材料密度换算，不手填。
产品与数据为虚构演示数据。
"""
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B03"):
    sys.path.insert(0, str(p))
from dslkit import Doc, TextFit              # noqa: E402
import b03kit as K                            # noqa: E402

VER = os.environ.get("B03_VER", "v01")
W, H = 1600, 1000
PAPER, INK, DIM, HOT = "#F2EFE9", "#1B1E22", "#2E5468", "#C8552B"
TOP, RIGHT, LEFT, RIM = "#E4DCCB", "#B7AB94", "#8A7F6B", "#5F5748"
# 每种材料给三个受光面（顶 / 右下 / 左下），评审时靠色相就能分辨零件材质
MAT_FACE = {"铝合金 6061": (TOP, RIGHT, LEFT),
            "无氧铜": ("#EBC9A0", "#BE8E58", "#8F6742"),
            "光学 PC": ("#CFDEDB", "#AABEC0", "#7E9498"),
            "FR-4 玻纤": ("#D9E2CC", "#9EB28A", "#728866"),
            "不锈钢 304": ("#E7E7EA", "#B3B5BC", "#888B94"),
            "丁腈橡胶": ("#54555E", "#3A3B43", "#26272D")}
COS30 = math.cos(math.pi / 6)
E1 = (COS30, 0.5)        # 装配轴：向右下
E2 = (-COS30, 0.5)       # 横向：向左下
E3 = (0.0, -1.0)         # 高：向上
PRINT_W_MM = 841.0       # A1 横向幅宽（1600×1000 同比例）
S = W / PRINT_W_MM       # px / mm：按该幅宽打印时保持 1:1
GAP = 40.0               # 爆炸间距 mm
AX, AY = 172.0, 214.0    # 装配轴起点（屏幕坐标）
PANEL_R = 1000           # 绘图区右界

DENS = {"铝合金 6061": 2.70, "光学 PC": 1.20, "无氧铜": 8.96,
        "FR-4 玻纤": 1.85, "不锈钢 304": 7.85, "丁腈橡胶": 1.05}

# (名称, 形状, 长mm, 直径/宽mm, 高mm, 材料, 插入深度mm, 工序, 体积折算系数)
# 系数＝实际材料体积 / 外包络体积：空心壳体、旋压杯和实心板的量级完全不同，
# 直接按外包络算会把 18 mm 厚的反光杯算成 114 g 的铜锭。
PARTS = [
    ("压圈", "tube", 8.0, 34.0, 0, "铝合金 6061", 0.0, "CNC + 喷砂阳极", 0.42),
    ("反光杯", "tube", 18.0, 30.0, 0, "无氧铜", 3.0, "旋压制杯 + 镀银", 0.16),
    ("灯头壳", "box", 26.0, 32.0, 32.0, "光学 PC", 0.0, "注塑 + 超声波焊", 0.38),
    ("驱动板", "box", 4.0, 28.0, 28.0, "FR-4 玻纤", 2.0, "SMT 回流 + 三防", 0.86),
    ("筒身", "tube", 96.0, 28.0, 0, "铝合金 6061", 0.0, "挤压 + 滚花 + 硬质阳极", 0.30),
    ("尾盖", "tube", 14.0, 30.0, 0, "铝合金 6061", 4.0, "CNC + 阳极（与筒身同批）", 0.55),
    ("密封圈", "ring", 2.5, 29.0, 0, "丁腈橡胶", 0.0, "模压 + 修边", 0.34),
]


def pt(u, v, w):
    """零件局部坐标 (u,v,w) mm -> 屏幕坐标。"""
    return (AX + (u * E1[0] + v * E2[0]) * S,
            AY + (u * E1[1] + v * E2[1] + w * E3[1]) * S)


def face(d, u0, v0, w0, du, dv, cu, cv, color):
    """以 (u0,v0,w0) 为角、沿 cu/cv 两组单位基向量铺一个平行四边形面。

    尺寸（du/dv）已经换算成屏幕像素，矩阵只负责把局部坐标轴指向基向量方向；
    v01 把 S 同时写进尺寸和矩阵，整块体被放大 2.4 倍糊成一片。
    """
    x, y = pt(u0, v0, w0)
    K.xform(d, x, y, du, dv, K.basis(cu, cv),
            f'<Container width="{K.n(du)}" height="{K.n(dv)}" color="{color}"/>',
            align="TOP_LEFT")


def disc(d, u, v, w, r, color):
    """垂直于装配轴的圆面：剪切到 (e2,e3) 平面 -> 屏幕上是椭圆。"""
    cx, cy = pt(u, v, w)
    rr = r * S
    K.xform(d, cx - rr, cy - rr, rr * 2, rr * 2, K.basis(E2, E3),
            f'<ClipOval clipBehavior="ANTI_ALIAS"><Container width="{K.n(rr*2)}" '
            f'height="{K.n(rr*2)}" color="{color}"/></ClipOval>', align="CENTER")


def tangent_uv():
    """圆柱侧面轮廓（silhouette）在圆坐标里的切点方向。

    侧面不能画成竖直矩形：剪切后椭圆盖的竖直跨度是 1.5r，v02 用 2r 竖边，端盖
    从筒壁上下各露出一截。这里对 a×(M v) 取极值解出切点，侧面＝两切点连线沿轴拉伸。
    """
    m11, m12, m21, m22 = E2[0], E3[0], E2[1], E3[1]
    pv, qv = E1[0] * m21 - E1[1] * m11, E1[0] * m22 - E1[1] * m12
    sc = math.hypot(pv, qv)
    return (pv / sc, qv / sc)


TUV = tangent_uv()


def tube(d, u0, L, dia, mat):
    top, rgt, lft = MAT_FACE[mat]
    r = dia / 2.0
    bx, by = pt(u0, r * TUV[0], r * TUV[1])       # 近端下切点
    tx, ty = pt(u0, -r * TUV[0], -r * TUV[1])     # 近端上切点
    th = math.hypot(tx - bx, ty - by)
    dv = ((tx - bx) / th, (ty - by) / th)
    disc(d, u0 + L, 0, 0, r, K.mix(lft, 0.80))    # 远端盖
    K.xform(d, bx, by, L * S, th, K.basis(E1, dv),
            f'<Container width="{K.n(L*S)}" height="{K.n(th)}" color="{rgt}"/>',
            align="TOP_LEFT")
    disc(d, u0, 0, 0, r, top)                     # 近端盖


def box(d, u0, L, D, Hh, mat):
    """方件绕装配轴居中，只画朝向观察者的三个面（u 最大、v 最大、w 最大）。

    v06 画的是 u 最小与 v 最小那两个背面，于是壳体看起来像个敞口的屋顶。
    """
    top, rgt, lft = MAT_FACE[mat]
    v0, w0 = -D / 2.0, -Hh / 2.0
    face(d, u0 + L, v0, w0, D * S, Hh * S, E2, E3, rgt)      # 右下面
    face(d, u0, v0 + D, w0, L * S, Hh * S, E1, E3, lft)      # 左下面
    face(d, u0, v0, w0 + Hh, L * S, D * S, E1, E2, top)      # 顶面


def ring(d, u0, L, dia, mat):
    tube(d, u0, L, dia, mat)
    disc(d, u0, 0, 0, dia / 2.0 * 0.68, "#6E665A")    # 孔口阴影
    disc(d, u0, 0, 0, dia / 2.0 * 0.60, PAPER)


# ---------- 换算：质量 / 总长 / 重心 ----------
def envelope(p):
    _, shape, L, D, Hh, _, _, _, _ = p
    return math.pi * (D / 2) ** 2 * L if shape in ("tube", "ring") else L * D * Hh


def mass(p):
    return envelope(p) * p[8] / 1000.0 * DENS[p[5]]


MASS = [mass(p) for p in PARTS]
TOTAL_MASS = sum(MASS)
STACK = sum(p[2] for p in PARTS) - sum(p[6] for p in PARTS)
AXIS_MM = STACK + GAP * (len(PARTS) - 1)
END = pt(AXIS_MM, 0, 0)
assert END[0] < PANEL_R and END[1] < 800, "轴测体越出绘图区：%s" % (END,)
# 重心沿装配轴：按“装后”位置累计（不含爆炸间距），以第一件前端为零点
gsum = 0.0
_u = 0.0
for p, m in zip(PARTS, MASS):
    gsum += m * (_u + p[2] / 2.0)
    _u += p[2] - p[6]
CG = gsum / TOTAL_MASS
assert abs(_u - STACK) < 1e-6, "装配累计长度与 STACK 不一致：%s vs %s" % (_u, STACK)

d = Doc(W, H, PAPER, font="Inter,Noto Sans CJK SC")
tf = TextFit()
d.font = "Inter,Noto Sans CJK SC"

# ---------- 页眉 ----------
K.tlab(d, tf, "title", 60, 44, 700, 44, "AX-3 手电 · 轴测拆解评审图版", 32, INK,
       style="BOLD")
K.tlab(d, tf, "sub", 60, 88, 900, 28,
       "爆炸视图沿装配轴展开 · 质量 = 几何体积 × 折算系数 × 材料密度，系数按壁厚列在表中",
       19, DIM)
K.tlab(d, tf, "sheet", W - 460, 44, 400, 28, "图号 AX3-EXP-07 · 单位 mm · 幅宽 841",
       19, INK, align="END")
K.tlab(d, tf, "rev", W - 520, 76, 460, 28, "Rev B · 按 841 mm 幅宽打印 1:1 · 2026-10-10", 19, DIM,
       align="END")
d.rect(60, 128, W - 120, 2, INK)

# ---------- 装配轴 ----------
ax0 = pt(-14, 0, 0)
ax1 = pt(AXIS_MM + 14, 0, 0)
# 装配轴用 d.line：v06 这里手写矩阵时把 S 又乘进方向向量，
# 变换后的内容超出 Positioned 盒宽被裁成一条水平线。
d.line(ax0[0], ax0[1], ax1[0], ax1[1], 1.5, HOT)

# ---------- 逐个零件 ----------
u = 0.0
ANCH = []
for i, p in enumerate(PARTS):
    nm, shape, L, D, Hh, mat, ins, proc, fill = p
    if shape == "tube":
        tube(d, u, L, D, mat)
    elif shape == "ring":
        ring(d, u, L, D, mat)
    else:
        box(d, u, L, D, Hh, mat)
    cx, cy = pt(u + L / 2.0, 0, max(D, Hh) / 2.0 + 6)
    ANCH.append((cx, cy, u, L))
    u += L + GAP - ins

# ---------- 引线 + 编号气泡 ----------
TX, TY = 1040, 168
ROW = 62
for i, ((cx, cy, u0, L), p) in enumerate(zip(ANCH, PARTS)):
    ry = TY + i * ROW + 20
    d.line(cx + 6, cy - 6, TX - 34, ry, 1, DIM)
    d.dot(TX - 34, ry, 5, DIM)
    bx, by = pt(u0 + L / 2.0, 0, 0)
    d.dot(bx, by, 26, HOT)
    K.tlab(d, tf, "bub%d" % i, bx - 13, by - 13, 26, 26, str(i + 1), 17, PAPER,
           style="BOLD", align="CENTER")

# ---------- 爆炸展开尺寸线（文字处断线，CAD 惯例） ----------
DV = 52.0
GAP_U = (170 / (E1[0] * S)) + 6          # 文字半宽换算成轴向 mm
p0, p1 = pt(0, DV, 0), pt(AXIS_MM, DV, 0)
ga, gb = pt(AXIS_MM / 2 - GAP_U, DV, 0), pt(AXIS_MM / 2 + GAP_U, DV, 0)
d.line(p0[0], p0[1], ga[0], ga[1], 1.5, DIM)
d.line(gb[0], gb[1], p1[0], p1[1], 1.5, DIM)
for uu in (0.0, AXIS_MM):
    a, b = pt(uu, DV - 7, 0), pt(uu, DV + 7, 0)
    d.line(a[0], a[1], b[0], b[1], 1.5, DIM)
mx, my = pt(AXIS_MM / 2.0, DV, 0)
K.tlab(d, tf, "dim", mx - 170, my - 13, 340, 26,
       f"爆炸展开 {AXIS_MM:.1f} mm（装后 {STACK:.1f}）", 17, DIM, align="CENTER")

# ---------- 零件表 ----------
K.tlab(d, tf, "tb-hd", TX, TY - 34, 200, 28, "零件表", 22, INK, style="BOLD")
K.tlab(d, tf, "tb-hd2", TX + 200, TY - 34, 300, 28, "质量 / 工序由材料密度换算",
       17, DIM, align="END")
d.rect(TX, TY - 6, W - 60 - TX, 2, INK)
for i, ((cx, cy, u0, L), p) in enumerate(zip(ANCH, PARTS)):
    nm, shape, ln, D, Hh, mat, ins, proc, fill = p
    y = TY + i * ROW
    K.tlab(d, tf, "t%d-n" % i, TX, y, 26, 26, "%d" % (i + 1), 19, HOT, style="BOLD")
    K.tlab(d, tf, "t%d-a" % i, TX + 30, y, 130, 26, nm, 20, INK, style="BOLD")
    K.tlab(d, tf, "t%d-b" % i, TX + 30, y + 24, 300, 24,
           f"{mat} · Ø{D:g}" + (f" × {Hh:g} 方" if shape == "box" else "")
           + f" · ×{fill:.2f}", 17, DIM)
    K.tlab(d, tf, "t%d-c" % i, TX + 30, y + 44, 320, 24, proc, 16, "#6A6151")
    K.tlab(d, tf, "t%d-d" % i, W - 210, y, 150, 26, "%.1f g" % MASS[i], 20, INK,
           align="END")
    K.tlab(d, tf, "t%d-e" % i, W - 210, y + 26, 150, 24,
           f"L {ln:g} mm" + (f" · 插入 {ins:g}" if ins else ""), 16, DIM, align="END")
    if i:
        d.rect(TX, y - 8, W - 60 - TX, 1, "#D6CDBB")

# ---------- 底部：装配顺序与合计 ----------
BY = 800
d.rect(60, BY - 26, TX - 60, 2, INK)
K.tlab(d, tf, "asm-hd", 60, BY - 12, 300, 28, "装配顺序（自前向后）", 20, INK,
       style="BOLD")
order = [0, 1, 2, 3, 4, 6, 5]
ox = 60
for k, idx in enumerate(order):
    cw = 132
    d.rect(ox, BY + 24, cw, 40, "#E4DCCB", radius=6)
    d.dot(ox + 20, BY + 44, 22, HOT if idx in (1, 6) else DIM)
    K.tlab(d, tf, "o%d" % k, ox + 9, BY + 33, 22, 22, str(idx + 1), 15, PAPER,
           style="BOLD", align="CENTER")
    K.tlab(d, tf, "on%d" % k, ox + 38, BY + 24, cw - 46, 40, PARTS[idx][0], 18, INK,
           valign="MIDDLE")
    if k < len(order) - 1:
        K.tlab(d, tf, "oa%d" % k, ox + cw, BY + 30, 14, 28, "›", 20, DIM,
               align="CENTER")
    ox += cw + 12

SUMS = [
    ("装后总长", f"{STACK:.1f} mm"),
    ("零件合计质量", f"{TOTAL_MASS:.1f} g"),
    ("重心距前端（装后）", f"{CG:.1f} mm · 沿装配轴"),
    ("爆炸件数", f"{len(PARTS)} 件 · 过盈插入 {sum(1 for p in PARTS if p[6])} 处"),
]
sx = 60
for k, v in SUMS:
    K.tlab(d, tf, "s-%s" % k, sx, BY + 92, 200, 26, k, 17, DIM)
    K.tlab(d, tf, "sv-%s" % k, sx, BY + 114, 260, 28, v, 19, INK, style="BOLD")
    sx += 280

# ---------- 右栏下部：待评审清单 ----------
REV = [("反光杯与压圈为过盈配合，未留热胀间隙",
        "铜 16.5 / 铝 23 ×10⁻⁶/K，装配力随两地温差变化，口径需复核"),
       ("密封圈实际装于筒身退刀槽，爆炸图置于尾盖之后",
        "评审按装配顺序讲，不把序号当安装位置；顺序表已按实物排列"),
       ("驱动板未画限流电阻位，需确认与 Ø28 内壁净空",
        "如补件，Ø28 内径与板边间隙小于 1.5 mm，需改筒身或改板框")]
d.rect(TX, 636, W - 60 - TX, 2, INK)
K.tlab(d, tf, "rev-hd", TX, 644, 340, 26, "待评审项（每条附复核口径）", 19, INK,
       style="BOLD")
ry = 686
for i, (txt, note) in enumerate(REV):
    d.dot(TX + 9, ry + 10, 18, HOT)
    K.tlab(d, tf, "rn%d" % i, TX + 1, ry + 2, 18, 18, str(i + 1), 13, PAPER,
           style="BOLD", align="CENTER")
    K.tlab(d, tf, "rv%d" % i, TX + 26, ry, W - 60 - TX - 26, 24, txt, 15, "#3A3A38")
    K.tlab(d, tf, "rt%d" % i, TX + 26, ry + 24, W - 60 - TX - 26, 22, note, 14,
           "#8A8172")
    ry += 52

# ---------- 左下：投影与读图说明 ----------
K.tlab(d, tf, "prj-hd", 60, 646, 300, 26, "投影与读图说明", 19, INK, style="BOLD")
NOTES = [
    "等角投影：e1 = (0.87, 0.50) 沿装配轴 · e2 = (-0.87, 0.50) 横向 · e3 = (0, -1) 高度",
    "本服务不支持透视矩阵（探针 01c 实测），轴测体全部由 2D 仿射列向量拼接，"
    "圆面用 (e2, e3) 剪切得到椭圆盖",
    "侧面轮廓取 a×Mv 极值的切点连线，端盖椭圆与筒壁相切；序号气泡落在装配轴上",
    f"1 px = {PRINT_W_MM/W:.3f} mm：按 {PRINT_W_MM:g} mm 幅宽打印为 1:1，"
    f"图版落幅 {PRINT_W_MM:.0f} × {H * PRINT_W_MM / W:.0f} mm",
]
ny = 674
for i, t in enumerate(NOTES):
    d.dot(66, ny + 11, 5, HOT)
    K.tlab(d, tf, "prj%d" % i, 78, ny, 860, 22, t, 15, "#6A6151")
    ny += 21

BOTTOMS = {"sums": BY + 142, "rev": ry, "table": TY + (len(PARTS) - 1) * ROW + 68,
           "axis": END[1] + 34 * S, "notes": ny}
assert max(BOTTOMS["sums"], BOTTOMS["rev"]) <= H - 46, "下部越出页脚线：%s" % BOTTOMS
assert BOTTOMS["notes"] <= BY - 28, "读图说明压到分隔线：%s" % BOTTOMS

K.tlab(d, tf, "foot", 60, H - 40, W - 120, 26,
       "虚构演示产品：AX-3 手电的零件、材料、工序与评审意见均为演示数据，"
       "不代表任何真实在售产品；透视矩阵在本服务不生效，轴测体全部由 2D 仿射基向量拼接。",
       16, DIM)

dsl = d.dsl()
out = ROOT / "tmp" / RID / "B03" / f"case03-{VER}.snapshot"
out.write_text(dsl, encoding="utf-8")
print(VER, "chars", len(dsl), "TextFit", tf.n, "problems", len(tf.problems))
for p in tf.problems[:12]:
    print("  !", p)
print("axis_mm %.1f end %s stack %.1f mass %.1f cg %.1f" %
      (AXIS_MM, (round(END[0]), round(END[1])), STACK, TOTAL_MASS, CG))
print("masses", [round(m, 1) for m in MASS])
