#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A23 · 单元表、五角星几何与帧间轨迹（纯参数层，不产生 DSL）。

设计约束（来自 tasks/A23-capability-delivery/TASK.md）：
- 12 个单元 U01–U12，稳定 ID，每帧各出现一次；ID 不印在图中。
- 每个 ID 的几何类型 / 未旋转宽高 / RGB 颜色 / 自身 alpha 跨帧一致；
  只允许位置与旋转角度变化（不缩放、不变形、不变色、不渐隐）。
- 位置 = 几何中心 (x, y)，画布左上原点，像素；旋转以自身中心为原点、顺时针度数。
- 帧 t = 0, 250, 500, 750, 1000, 1250 ms；循环周期 1500 ms。
- 插值：分段线性（题面示例明确许可），p_k = k/5，位置与旋转同步推进。
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------- 画布
FRAME_W = FRAME_H = 600
COVER_W, COVER_H = 1200, 800
FRAME_CENTER = (FRAME_W / 2.0, FRAME_H / 2.0)      # (300, 300)

FRAME_MS = [0, 250, 500, 750, 1000, 1250]
PERIOD_MS = 1500
N_FRAMES = 6

# ---------------------------------------------------------------- 星形几何
# 正五角星（pentagram 描边）：外顶点半径 R_OUT，内顶点半径 R_IN = R_OUT/phi^2
R_OUT = 205.0
R_IN = R_OUT * (3.0 - math.sqrt(5.0)) / 2.0         # ≈ 78.30
BAR_T = 20.0          # 条带厚度（未旋转高度）
BAR_OV = 13.0         # 两端外延量，用于在尖角与凹角处形成实体接头
BAR_RADIUS = 2.0      # 圆角
# 内点圆 / 菱形点缀
CORE_D = 52.0
GEM = 28.0            # 菱形（圆角方块）边长
GEM_RADIUS = 7.0

# 接头实体化核算（写入 snapshot-usage.md 的依据）：
#   凹角（内角 252°，转角 108°）：内部缺口沿角平分线深 0.618*BAR_T；
#     该点沿任一边的投影 = 0.588 * 0.618 * BAR_T ≈ 0.363*BAR_T < BAR_OV  -> 全填满
#   尖角（内角 36°，转角 72°）：尖端实体深度 = BAR_OV/cos(36°) ≈ 1.70*BAR_T；
#     外延端两点间距 = 2*BAR_OV*sin(36°) ≈ 15.3 < BAR_T              -> 不分叉
JOINT_CHECK = {
    "concave_gap_depth": round(0.618 * BAR_T, 2),
    "concave_need_overlap": round(0.363 * BAR_T, 2),
    "tip_solid_depth": round(BAR_OV / math.cos(math.radians(36)), 2),
    "tip_prong_separation": round(2 * BAR_OV * math.sin(math.radians(36)), 2),
}


def star_vertices():
    """返回 (outer[5], inner[5])，角度为屏幕顺时针、-90° 为正上。"""
    outer, inner = [], []
    for k in range(5):
        ao = math.radians(-90.0 + 72.0 * k)
        ai = math.radians(-90.0 + 36.0 + 72.0 * k)
        outer.append((FRAME_CENTER[0] + R_OUT * math.cos(ao),
                      FRAME_CENTER[1] + R_OUT * math.sin(ao)))
        inner.append((FRAME_CENTER[0] + R_IN * math.cos(ai),
                      FRAME_CENTER[1] + R_IN * math.sin(ai)))
    return outer, inner


def star_edges():
    """五角星描边的 10 条边，顺序 O0,I0,O1,I1,...；返回 [(p0, p1, role)]。

    role = 'spoke'（外顶点->内顶点，五条）/ 'chord'（内顶点->下一外顶点，五条）。
    """
    outer, inner = star_vertices()
    seq = []
    for k in range(5):
        seq.append((outer[k], inner[k], "spoke"))
        seq.append((inner[k], outer[(k + 1) % 5], "chord"))
    return seq


def bar_for_edge(p0, p1):
    """边 -> 条带参数：中心、未旋转宽高、旋转角（顺时针度数）。"""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    cx, cy = (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0
    ang = math.degrees(math.atan2(dy, dx))
    return {"cx": cx, "cy": cy, "w": L + 2 * BAR_OV, "h": BAR_T,
            "rot": ang, "edge_len": L}


# ---------------------------------------------------------------- 单元表
# 每项：id / geom / w,h（未旋转）/ color / alpha / 末帧目标位姿 / 首帧散开位姿
#   geom: 'bar'      -> 圆角矩形（未旋转 w×h）
#         'circle'   -> 正圆（直径 = w = h）
#         'gem'      -> 圆角方块（未旋转 w×h）
def _unit_table():
    units = []
    edges = star_edges()
    for i, (p0, p1, role) in enumerate(edges):
        b = bar_for_edge(p0, p1)
        col = "#4F46E5" if role == "spoke" else "#7C3AED"
        units.append({
            "id": f"U{i + 1:02d}", "geom": "bar", "role": role,
            "w": round(b["w"], 4), "h": BAR_T, "radius": BAR_RADIUS,
            "color": col, "alpha": 1.00 if role == "spoke" else 0.92,
            "edge_len": round(b["edge_len"], 4),
            "target": (round(b["cx"], 4), round(b["cy"], 4)),
            "target_rot": round(b["rot"], 4),
        })
    # U11 中心圆 / U12 菱形点缀
    units.append({
        "id": "U11", "geom": "circle", "role": "core",
        "w": CORE_D, "h": CORE_D, "radius": None,
        "color": "#F59E0B", "alpha": 1.00,
        "target": (300.0, 300.0), "target_rot": 0.0,
    })
    units.append({
        "id": "U12", "geom": "gem", "role": "gem",
        "w": GEM, "h": GEM, "radius": GEM_RADIUS,
        "color": "#FBBF24", "alpha": 0.90,
        "target": (300.0 - 56.0, 300.0 - 34.0), "target_rot": 45.0,
    })
    return units


def _scatter(units):
    """确定性散开位姿：目标位姿 + 固定种子的方向/距离偏移，并保证整体留在画布内。

    偏移由“远离画面中心的径向推开 + 固定切向漂移”构成；随后按旋转后半宽
    求出仍不越界的最大比例 t，整体收缩到该比例（题面：不能把单元移出画布）。
    """
    golden = math.radians(137.50776405003785)
    MARGIN = 10.0
    out = []
    for i, u in enumerate(units):
        j = ((i * 2654435761) % 1000) / 1000.0
        dist = 118.0 + 88.0 * j                       # 118–206 px
        ang = golden * (i + 1)
        ox = math.cos(ang) * dist
        oy = math.sin(ang) * dist
        # 目标 -> 散开：径向（远离中心，中心单元用索引方向兜底）+ 切向漂移
        tx, ty = u["target"]
        vx, vy = tx - FRAME_CENTER[0], ty - FRAME_CENTER[1]
        vl = math.hypot(vx, vy)
        if vl < 1e-6:
            vx, vy, vl = math.cos(ang), math.sin(ang), 1.0
        push = (vx / vl, vy / vl)
        drift = (-push[1], push[0])
        offx = push[0] * dist + drift[0] * (dist * 0.38)
        offy = push[1] * dist + drift[1] * (dist * 0.38)
        # 旋转角偏移（确定性）
        drot = 148.0 - 296.0 * j
        srot = u["target_rot"] + drot
        hw, hh = half_extent(u, srot)
        # 求最大 t∈[0,1] 使 target + t*off 的外包框留在 [MARGIN, W-MARGIN] 内
        tmax = 1.0
        for (c, half, lo, hi, d) in ((tx, hw, MARGIN, FRAME_W - MARGIN, offx),
                                     (ty, hh, MARGIN, FRAME_H - MARGIN, offy)):
            if half * 2 > (hi - lo):                   # 单元比可用空间还宽
                tmax = 0.0
                continue
            A = lo + half - c                          # t*d >= A
            B = hi - half - c                          # t*d <= B
            if abs(d) < 1e-9:
                tmax = min(tmax, 1.0 if A <= 0.0 <= B else 0.0)
                continue
            lo_t, hi_t = (A / d, B / d) if d > 0 else (B / d, A / d)
            tmax = min(tmax, max(0.0, min(1.0, hi_t)))
        t = max(0.0, min(1.0, tmax))
        sx = tx + offx * t
        sy = ty + offy * t
        out.append({"scatter": (round(sx, 4), round(sy, 4)),
                    "scatter_rot": round(srot, 4),
                    "scatter_offset": round(dist, 4),
                    "scatter_scale": round(t, 4)})
    return out


def half_extent(u, rot_deg):
    """未旋转 w×h 绕自身中心旋转 rot 后的外包半宽/半高。

    注意：圆形（geom == 'circle'）的外包框与旋转无关；此函数对圆返回的仍是
    按方框估算的较大值，仅用于“散开时不离画布”的保守约束。
    """
    a = math.radians(rot_deg)
    c, s = abs(math.cos(a)), abs(math.sin(a))
    return (u["w"] / 2.0 * c + u["h"] / 2.0 * s,
            u["w"] / 2.0 * s + u["h"] / 2.0 * c)


def bbox_half(u, rot_deg):
    """外包框半宽/半高（圆形与旋转无关；圆角方块的圆角会略小于此值）。"""
    if u["geom"] == "circle":
        return u["w"] / 2.0, u["h"] / 2.0
    return half_extent(u, rot_deg)


def units():
    """完整单元表（含散开位姿）。"""
    us = _unit_table()
    sc = _scatter(us)
    for u, s in zip(us, sc):
        u.update(s)
    return us


def progress(k: int) -> float:
    """分段线性进度：p_k = k/5。"""
    return k / (N_FRAMES - 1)


def pose_at(u, k: int):
    """第 k 帧（k=0..5）该单元的中心、旋转、可见外包框。"""
    p = progress(k)
    tx, ty = u["target"]
    sx, sy = u["scatter"]
    cx = sx + (tx - sx) * p
    cy = sy + (ty - sy) * p
    rot = u["scatter_rot"] + (u["target_rot"] - u["scatter_rot"]) * p
    hw, hh = half_extent(u, rot)
    return {"cx": cx, "cy": cy, "rot": rot,
            "box": (cx - hw, cy - hh, cx + hw, cy + hh)}


def angle_delta(a: float, b: float) -> float:
    """b - a，归一到 (-180, 180]（360° 等价）。"""
    d = (b - a) % 360.0
    if d > 180.0:
        d -= 360.0
    return d


def trajectories(us=None):
    """逐单元相邻帧位移/角差 + 插值规则 + 循环接缝。"""
    us = us or units()
    traj = []
    for u in us:
        steps = []
        for k in range(N_FRAMES - 1):
            a, b = pose_at(u, k), pose_at(u, k + 1)
            dx, dy = b["cx"] - a["cx"], b["cy"] - a["cy"]
            steps.append({
                "from_t_ms": FRAME_MS[k], "to_t_ms": FRAME_MS[k + 1],
                "dx": round(dx, 4), "dy": round(dy, 4),
                "distance": round(math.hypot(dx, dy), 4),
                "d_rotation_deg": round(angle_delta(a["rot"], b["rot"]), 4),
            })
        # 循环接缝：frame-06 (t=1250) -> frame-01 (t=1500 ≡ 0)
        f6, f1 = pose_at(u, N_FRAMES - 1), pose_at(u, 0)
        dx, dy = f1["cx"] - f6["cx"], f1["cy"] - f6["cy"]
        seam = {
            "from_t_ms": 1250, "to_t_ms": 1500,
            "dx": round(dx, 4), "dy": round(dy, 4),
            "distance": round(math.hypot(dx, dy), 4),
            "d_rotation_deg": round(angle_delta(f6["rot"], f1["rot"]), 4),
        }
        inter = [s["distance"] for s in steps]
        traj.append({
            "id": u["id"], "interpolation": "piecewise_linear",
            "easing": "p_k = k/5（分段线性，位置与旋转同步；未渲染中间帧）",
            "steps": steps,
            "interframe_distance_max": round(max(inter), 4),
            "interframe_distance_min": round(min(inter), 4),
            "interframe_distance_mean": round(sum(inter) / len(inter), 4),
            "seam_step_1250_to_1500": seam,
            "seam_vs_mean_ratio": round(seam["distance"]
                                        / (sum(inter) / len(inter)), 4),
        })
    return traj


if __name__ == "__main__":
    us = units()
    print(f"units={len(us)}  R_OUT={R_OUT} R_IN={R_IN:.2f} "
          f"edge≈{us[0]['edge_len']} bar={us[0]['w']:.2f}x{us[0]['h']}")
    print("joint:", JOINT_CHECK)
    for u in us:
        f1, f6 = pose_at(u, 0), pose_at(u, 5)
        print(f"{u['id']} {u['geom']:6s} {u['color']} a={u['alpha']:.2f} "
              f"tgt=({u['target'][0]:7.2f},{u['target'][1]:7.2f}) "
              f"rot={u['target_rot']:7.2f} | f1=({f1['cx']:7.2f},{f1['cy']:7.2f}) "
              f"rot={f1['rot']:8.2f} box=({f1['box'][0]:6.1f},{f1['box'][1]:6.1f},"
              f"{f1['box'][2]:6.1f},{f1['box'][3]:6.1f})")
