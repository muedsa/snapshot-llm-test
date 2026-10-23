"""A08 几何换算：格心 → 画布像素、偏移折线、等宽带多边形、虚线、箭头。

规则来自题面第 4 条：逻辑路径按格心序列计算；绘制允许同中心线的宽底线/窄虚线组合
（本题采用），允许平行偏移（本题未用，lateral_offset_px 恒为 0）。
所有像素几何都从 model.json 的逻辑格心序列推导，路线长度一律按逻辑格间边计数。
"""

from __future__ import annotations

CELL = 40.0          # 单格像素边长（题面要求 ≥36）
D_LAT = 0.0          # 相对逻辑中心线的横向偏移（0 = 同中心线，见题面第 4 条）
PERIOD = 40.0        # 虚线周期 = 一格长，使虚线接缝恰好落在格心，转角不留断口
DASH, GAP = 24.0, 16.0


def perp(dx, dy):
    """方向 (dx,dy) 的左侧法向：屏幕坐标 y 向下，(dy,-dx) 为行进左侧。"""
    return (dy, -dx)


def vlen(x1, y1, x2, y2):
    return float(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)


def offset_poly(cells, ox, oy, d=D_LAT):
    """格心序列 → 画布折线（转角取 miter，即两个左侧法向之和）。

    d=0 时 miter 不额外外扩，返回纯格心折线；d>0 时可得到平行偏移折线。
    """
    if len(cells) < 2:
        raise ValueError("路线至少两个格")
    pts = [(ox + (x + 0.5) * CELL, oy + (y + 0.5) * CELL) for x, y in cells]
    if d == 0:
        return pts
    out = []
    for i, p in enumerate(pts):
        if i == 0:
            dx, dy = pts[1][0] - p[0], pts[1][1] - p[1]
            out.append((p[0] + d * dy, p[1] - d * dx))
        elif i == len(pts) - 1:
            dx, dy = p[0] - pts[-2][0], p[1] - pts[-2][1]
            out.append((p[0] + d * dy, p[1] - d * dx))
        else:
            a = perp(*[pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]])
            b = perp(*[pts[i + 1][0] - p[0], pts[i + 1][1] - p[1]])
            out.append((p[0] + d * (a[0] + b[0]), p[1] + d * (a[1] + b[1])))
    return out


def band(poly, hw):
    """等宽带的填充多边形：沿折线两侧各留 hw，转角自动 miter。

    共线顶点处只留一个采样点，保证带宽全程一致（不会在直线中段被收窄）。
    开头先折叠连续重复点：零长段的法向是 (0,0)，会让偏移塌回中心线，
    把矩形变成退化的三角形（这是 v1/v2 里 R2 虚线画成倒三角的根因）。
    """
    dedup = [poly[0]]
    for p in poly[1:]:
        if vlen(*dedup[-1], *p) > 1e-9:
            dedup.append(p)
    poly = dedup
    n = len(poly)
    if n < 2:
        raise ValueError("带至少两点")
    nrm = []                                   # 每段的单位左侧法向
    for i in range(n - 1):
        dx = poly[i + 1][0] - poly[i][0]
        dy = poly[i + 1][1] - poly[i][1]
        L = vlen(poly[i][0], poly[i][1], poly[i + 1][0], poly[i + 1][1]) or 1.0
        nrm.append((dy / L, -dx / L))
    left = [(poly[0][0] + nrm[0][0] * hw, poly[0][1] + nrm[0][1] * hw)]
    for i in range(1, n - 1):
        nx, ny = nrm[i - 1]
        mx, my = nrm[i]
        if abs(nx * my - ny * mx) >= 1e-9:
            # 转弯：取前后两条偏移线的**交点**（即 corner + hw*(n_prev+n_next)）。
            # 网格路径只有 90° 转角，等距 miter 与两线交点重合。
            # 只留 n_prev 或 n_next 单独的外扩点会在转角内侧切出一道缺口。
            left.append((poly[i][0] + (nx + mx) * hw, poly[i][1] + (ny + my) * hw))
        else:                                  # 共线（不转弯）→ 只留一点，带宽恒定
            left.append((poly[i][0] + nx * hw, poly[i][1] + ny * hw))
    left.append((poly[-1][0] + nrm[-1][0] * hw, poly[-1][1] + nrm[-1][1] * hw))
    right = [(poly[-1][0] - nrm[-1][0] * hw, poly[-1][1] - nrm[-1][1] * hw)]
    for i in range(n - 2, 0, -1):
        nx, ny = nrm[i - 1]
        mx, my = nrm[i]
        if abs(nx * my - ny * mx) >= 1e-9:
            right.append((poly[i][0] - (nx + mx) * hw, poly[i][1] - (ny + my) * hw))
        else:
            right.append((poly[i][0] - nx * hw, poly[i][1] - ny * hw))
    right.append((poly[0][0] - nrm[0][0] * hw, poly[0][1] - nrm[0][1] * hw))
    seq = left + right
    return "M" + " L".join(f"{g(x)} {g(y)}" for x, y in seq) + " Z"


def g(v):
    """路径坐标格式化。"""
    return f"{v:.2f}".rstrip("0").rstrip(".")


def dash_polys(poly, hw, dash=DASH, gap=GAP, phase=0.0):
    """把折线切成 dash 段的多边形列表（沿弧长取段，接缝自动 miter）。"""
    cum = [0.0]
    for i in range(len(poly) - 1):
        cum.append(cum[-1] + vlen(*poly[i], *poly[i + 1]))
    total = cum[-1]
    out = []
    k = 0
    while True:
        a = phase + k * (dash + gap)
        if a >= total:
            break
        b = min(a + dash, total)
        out.append(segment_band(poly, cum, max(a, 0.0), b, hw))
        k += 1
    return out


def segment_band(poly, cum, a, b, hw):
    """弧长区间 [a,b] 内的折线段 → 等宽带多边形。"""
    seg = []
    for i in range(len(poly) - 1):
        l0, l1 = cum[i], cum[i + 1]
        if l1 < a - 1e-9 or l0 > b + 1e-9:
            continue
        sa = max(a, l0)
        sb = min(b, l1)
        if sb - sa <= 1e-9:
            continue        # 零长重叠（本段仅刚好触到边界）不能进折线，
                            # 否则 band() 会拿到零长段、法向退化成 (0,0)
        t0, t1 = (sa - l0) / (l1 - l0), (sb - l0) / (l1 - l0)
        seg.append((poly[i][0] + t0 * (poly[i + 1][0] - poly[i][0]),
                    poly[i][1] + t0 * (poly[i + 1][1] - poly[i][1])))
        seg.append((poly[i][0] + t1 * (poly[i + 1][0] - poly[i][0]),
                    poly[i][1] + t1 * (poly[i + 1][1] - poly[i][1])))
    return band(seg, hw)


def arrow(cx, cy, ux, uy, w, h, color):
    """行进方向箭头：底边居中、尖端指向 (ux,uy) 的实心三角。"""
    tip = (cx + ux * h, cy + uy * h)
    bl = (cx - ux * h / 2 - uy * w / 2, cy - uy * h / 2 + ux * w / 2)
    br = (cx - ux * h / 2 + uy * w / 2, cy - uy * h / 2 - ux * w / 2)
    return (f'<ClipPath path="M{g(tip[0])} {g(tip[1])} L{g(bl[0])} {g(bl[1])} '
            f'L{g(br[0])} {g(br[1])} Z" viewBox="0 0 1560 1080" fit="FILL">'
            f'<Container width="1560" height="1080" color="{color}"></Container>'
            f'</ClipPath>')
