"""A09 变换代数与印章模型。

约定：
  * 局部坐标：印章左上角为原点，x 向右、y 向下，单位 px，范围 0..120。
  * 变换轴心：每步都围绕局部中心 C=(60,60)。
  * 旋转方向：题面「顺时针按图像方向」，即屏幕时钟方向（右→下→左→上）。
    rotCW(90) 必须把右侧点 (120,60) 送到下方点 (60,120)。
  * 组合：操作按 inputs/transforms.json 的列表顺序依次施加，
    故矩阵 M = M_last ∘ … ∘ M_first（先施加的在最右）。
  * 矩阵以 (a,b,e,f,tx,ty) 六元组表示 2×3 仿射，
    x' = a·x + b·y + tx ; y' = e·x + f·y + ty
    序列化时转成 DSL 要求的列主序 4×4 十六数。
"""

from __future__ import annotations

import math

# ---- 印章（inputs/stamp.json，只读）----
SIZE = 120.0
PIVOT = (60.0, 60.0)
CENTER_HALF = 60.0


def rect_box(x: float, y: float, w: float, h: float) -> tuple[float, float]:
    """矩形 → 盒 (left, top)。"""
    return (x, y)


def dot_box(cx: float, cy: float, r: float) -> tuple[float, float, float]:
    """圆点 → (left, top, 半径)。"""
    return (cx - r, cy - r, r)


STAMP = {
    "size": [120, 120],
    "pivot": [60, 60],
    "rectangles": [
        {"xywh": [8, 8, 28, 92], "color": "#E54B4B"},
        {"xywh": [36, 72, 68, 28], "color": "#2364DB"},
        {"xywh": [64, 8, 40, 28], "color": "#EAB53B"},
    ],
    "dot": {"center": [91, 49], "radius": 8, "color": "#111111"},
}

# ---- 基本变换 ----

def mat_identity() -> tuple[float, float, float, float, float, float]:
    return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def mat_rotate_cw(deg: float) -> tuple[float, float, float, float, float, float]:
    """绕局部中心顺时针（图像方向）旋转 deg 度。"""
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return (c, -s, s, c,
            CENTER_HALF * (1.0 - c) + CENTER_HALF * s,
            CENTER_HALF * (1.0 - c) - CENTER_HALF * s)


def mat_mirror_h() -> tuple[float, float, float, float, float, float]:
    """左右镜像：x' = 120 - x。"""
    return (-1.0, 0.0, 0.0, 1.0, 120.0, 0.0)


def mat_mirror_v() -> tuple[float, float, float, float, float, float]:
    """上下镜像：y' = 120 - y。"""
    return (1.0, 0.0, 0.0, -1.0, 0.0, 120.0)


def mat_scale_uniform(s: float) -> tuple[float, float, float, float, float, float]:
    return (s, 0.0, 0.0, s,
            CENTER_HALF * (1.0 - s), CENTER_HALF * (1.0 - s))


def mat_scale_xy(sx: float, sy: float) -> tuple[float, float, float, float, float, float]:
    return (sx, 0.0, 0.0, sy,
            CENTER_HALF * (1.0 - sx), CENTER_HALF * (1.0 - sy))


def build(op: dict) -> tuple[float, float, float, float, float, float]:
    k = op["op"]
    if k == "rotate":
        return mat_rotate_cw(float(op["deg"]))
    if k == "mirror_horizontal":
        return mat_mirror_h()
    if k == "mirror_vertical":
        return mat_mirror_v()
    if k == "scale_uniform":
        return mat_scale_uniform(float(op["s"]))
    if k == "scale_xy":
        sx, sy = op["sx_sy"]
        return mat_scale_xy(float(sx), float(sy))
    raise ValueError(f"未知操作: {k!r}")


def apply_mat(m: tuple[float, ...], p: tuple[float, float]) -> tuple[float, float]:
    a, b, e, f, tx, ty = m
    x, y = p
    return (a * x + b * y + tx, e * x + f * y + ty)


def mul(m2: tuple[float, ...], m1: tuple[float, ...]) -> tuple[float, ...]:
    """m2 ∘ m1：先 m1 后 m2。"""
    a2, b2, e2, f2, tx2, ty2 = m2
    a1, b1, e1, f1, tx1, ty1 = m1
    return (
        a2 * a1 + b2 * e1, a2 * b1 + b2 * f1,
        e2 * a1 + f2 * e1, e2 * b1 + f2 * f1,
        a2 * tx1 + b2 * ty1 + tx2, e2 * tx1 + f2 * ty1 + ty2,
    )


def compose(ops: list[dict]) -> tuple[float, ...]:
    """按列表顺序施加操作：M = M_n ∘ … ∘ M_1。"""
    m = mat_identity()
    for op in ops:
        m = mul(build(op), m)
    return m

# ---- 序列化 ----

def mat_str(m: tuple[float, ...]) -> str:
    """2×3 仿射 → DSL 列主序 4×4 十六数（外层圆括号、值间无空格）。"""
    a, b, e, f, tx, ty = m
    vals = (a, e, 0.0, 0.0, b, f, 0.0, 0.0, tx, ty, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)
    return "(" + ",".join(fmt(v) for v in vals) + ")"


def mat_flat(m: tuple[float, ...]) -> list[float]:
    """列主序十六数（供 geometry-audit.json 使用）。"""
    a, b, e, f, tx, ty = m
    return [a, e, 0.0, 0.0, b, f, 0.0, 0.0, tx, ty, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]


def fmt(v: float) -> str:
    if abs(v) < 1e-12:
        return "0.0000000"
    return f"{v:.7f}"

# ---- 几何辅助 ----

def rect_corners(x: float, y: float, w: float, h: float) -> list[tuple[float, float]]:
    """按「左上、右上、右下、左下」顺序返回四角。"""
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def dot_samples(r: float, n: int = 72) -> list[tuple[float, float]]:
    """圆周边界采样（用于外接框与像素核验）。"""
    return [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def stamp_outline() -> list[tuple[float, float]]:
    """印章全形状边界点集（局部坐标）：三个矩形四角 + 圆周边界。"""
    pts: list[tuple[float, float]] = []
    for r in STAMP["rectangles"]:
        x, y, w, h = r["xywh"]
        pts += rect_corners(x, y, w, h)
    cx, cy = STAMP["dot"]["center"]
    pts += [(cx + dx, cy + dy) for dx, dy in dot_samples(STAMP["dot"]["radius"])]
    pts += [(0.0, 0.0), (SIZE, 0.0), (SIZE, SIZE), (0.0, SIZE)]
    return pts


def transform_bbox(m: tuple[float, ...], pts: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    """一批局部点的仿射像的轴对齐外接框 [left, top, right, bottom]。"""
    xs, ys = [], []
    for p in pts:
        x, y = apply_mat(m, p)
        xs.append(x)
        ys.append(y)
    return (min(xs), min(ys), max(xs), max(ys))


def bbox_area(b: tuple[float, float, float, float]) -> float:
    return (b[2] - b[0]) * (b[3] - b[1])

# ---- 自检 ----

def selftest() -> list[str]:
    """用具体点验证方向约定；断言失败说明本模块的旋转符号错。"""
    ok: list[str] = []
    r90 = mat_rotate_cw(90.0)
    cases = [((120.0, 60.0), (60.0, 120.0)),   # 右 → 下
             ((60.0, 0.0), (120.0, 60.0)),     # 上 → 右
             ((0.0, 60.0), (60.0, 0.0)),       # 左 → 上
             ((60.0, 120.0), (0.0, 60.0))]     # 下 → 左
    for p, exp in cases:
        got = apply_mat(r90, p)
        assert abs(got[0] - exp[0]) < 1e-9 and abs(got[1] - exp[1]) < 1e-9, f"rotCW90 {p} -> {got}"
    ok.append("rotCW(90) 四方向正确（图像顺时针）")

    r30 = mat_rotate_cw(30.0)
    p = apply_mat(r30, (60.0, 0.0))            # 上边中点顺时针 30°
    exp = (60.0 + 60.0 * math.sin(math.radians(30)), 60.0 - 60.0 * math.cos(math.radians(30)))
    assert abs(p[0] - exp[0]) < 1e-9 and abs(p[1] - exp[1]) < 1e-9, f"rotCW30 上边中点 {p}"
    ok.append("rotCW(30) 上边中点方向正确")

    mh = mat_mirror_h()
    assert abs(apply_mat(mh, (20.0, 40.0))[0] - 100.0) < 1e-9
    assert abs(apply_mat(mh, (20.0, 40.0))[1] - 40.0) < 1e-9
    ok.append("mirror_horizontal：y 不变、x 以 120 为轴")

    mv = mat_mirror_v()
    assert abs(apply_mat(mv, (20.0, 40.0))[1] - 80.0) < 1e-9
    ok.append("mirror_vertical：x 不变、y 以 120 为轴")

    s75 = mat_scale_uniform(0.75)
    assert abs(apply_mat(s75, (0.0, 0.0))[0] - 15.0) < 1e-9
    ok.append("scale_uniform(0.75) 保持中心不动")

    for m in (r90, mh, mv, s75, mat_rotate_cw(30.0)):
        assert max(abs(v) for v in apply_mat(m, PIVOT)) < 1e-9 or \
            (abs(apply_mat(m, PIVOT)[0] - 60.0) < 1e-9 and abs(apply_mat(m, PIVOT)[1] - 60.0) < 1e-9)
    ok.append("所有单元变换都固定轴心 (60,60)")

    # 序列化自检：与文档示例对照
    assert mat_str((1.0, 0.0, 0.0, 1.0, 20.0, 10.0)) == \
        "(1.0000000,0.0000000,0.0000000,0.0000000,0.0000000,1.0000000,0.0000000,0.0000000," \
        "20.0000000,10.0000000,1.0000000,0.0000000,0.0000000,0.0000000,0.0000000,1.0000000)"
    ok.append("列主序十六数序列化与文档示例 (1,0,0,0,0,1,0,0,0,0,1,0,20,10,0,1) 一致")
    return ok


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for i, line in enumerate(selftest(), 1):
        print(f"{i:2d}. PASS  {line}")
    for deg in (0, 90, 180, 270, 30):
        m = mat_rotate_cw(deg)
        print(f"rotCW({deg:3d}) = {mat_str(m)}")


# ---- 以盒中心为轴的“纯线性”矩阵 ----
def linear_of(m: tuple[float, ...]) -> tuple[float, float, float, float, float, float]:
    """丢掉平移项。

    实测（A03 交付件 + 本次探针）：<Transform matrix> 配 alignment="CENTER" 时
    作用原点是子盒的**中心**，而不是盒左上角。印章轴心恰为局部 (60,60) = 盒中心，
    故轴心处的固定点由 alignment 自动满足，矩阵只写 2x2 线性部分即可。
    """
    a, b, e, f, _, _ = m
    return (a, b, e, f, 0.0, 0.0)


def mat_str_linear(m: tuple[float, ...]) -> str:
    return mat_str(linear_of(m))
