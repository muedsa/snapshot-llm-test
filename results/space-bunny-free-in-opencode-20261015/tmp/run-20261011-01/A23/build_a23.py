#!/usr/bin/env python
# A23 「结构汇聚成图像」：封面 + 6 帧透明关键帧。
# 启动基准：总任务根 (suite_root)。用法：python build_a23.py [ver]
#
# 【12 个单元的守恒】几何类型、未旋转宽高、RGB、自身 alpha 跨帧完全一致，
# 只有位置与旋转角变化。单元尺寸存的是**未旋转**的几何宽高——
# 旋转后的外包框变化不是缩放，frame-data.json 两者都记并明确区分。
#
# 【循环接缝】收敛轨迹是单调的：12 个单元从散布位置沿 smoothstep 汇入末帧的
# 光圈图形。要让「末帧→首帧」也连续，几何上不可能同时满足
# 「单调汇聚」+「每步等长」+「闭合」——第 6 步必须一次跨完全程。
# 因此本实现**不宣称无缝**：在 timing.json 与 limitations.md 里如实给出
# 接缝的位置、位移、旋转差、与其余步长的比值，以及实际观看结论。
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
DRAFTS = BASE / "tmp/run-20261011-01/A23/drafts"

FRAME = 600
COVER = (1200, 800)
N_UNITS = 12
N_FRAMES = 6
FPS_MS = 250
CYCLE_MS = 1500
CENTER = (300.0, 300.0)
OUTER_R = 158.0          # 外圈 8 枚叶片的圆心半径
INNER_R = 80.0           # 内圈 4 枚节点方块的圆心半径
SCATTER_R = (226.0, 248.0)

OUTER_IDS = list(range(8))            # U01–U08 外圈叶片
INNER_IDS = list(range(8, 12))        # U09–U12 内圈节点
BLADE_W, BLADE_H, BLADE_R = 76.0, 24.0, 12.0
NODE_W, NODE_H, NODE_R = 34.0, 34.0, 8.0
UNIT_ALPHA = 1.0
COLORS = ["#2563EB", "#EA7C2D", "#16A34A", "#7C3AED", "#0891B2", "#DB2777"]


def unit_spec(i: int) -> dict:
    """第 i 个单元的**恒定**属性（跨帧不变的部分）。"""
    outer = i in OUTER_IDS
    w = BLADE_W if outer else NODE_W
    h = BLADE_H if outer else NODE_H
    col = COLORS[i % 4] if outer else COLORS[4 + (i - 8) % 2]
    return {
        "unit_id": f"U{i+1:02d}",
        "geometry": "rounded_blade" if outer else "square_node",
        "unrotated_width_px": w, "unrotated_height_px": h,
        "border_radius_px": BLADE_R if outer else NODE_R,
        "color_rgb": col,
        "alpha": UNIT_ALPHA,
    }


def angle(deg):
    a = math.radians(deg)
    return math.cos(a), math.sin(a)


def scatter_and_figure(i: int):
    """散布位置与末帧图形位置（都保证完整落在 600×600 内）。

    末帧图形 = 同心光圈：外圈 8 枚叶片沿半径 158 切向排布并互相搭接成整圈，
    内圈 4 枚节点方块沿半径 80 落在叶片之间的角平分方向上。
    """
    if i in OUTER_IDS:
        k = i
        rad = OUTER_R
        th = -90.0 + k * (360.0 / len(OUTER_IDS))
        half = max(BLADE_W, BLADE_H) / 2
    else:
        k = i - len(OUTER_IDS)
        rad = INNER_R
        th = -90.0 + 45.0 + k * (360.0 / len(INNER_IDS))
        half = NODE_W / 2
    fx, fy = angle(th)
    fig = (CENTER[0] + rad * fx, CENTER[1] + rad * fy)
    # 叶片切向摆放；内圈方块保持正立，作为光圈的「核」。
    fig_rot = (th + 90.0) % 360.0 if i in OUTER_IDS else 0.0

    # 散布：半径与角度都打乱，但保证完整落在 600×600 内
    r0, r1 = SCATTER_R
    rr = r0 + (r1 - r0) * ((i * 7 % N_UNITS) / (N_UNITS - 1))
    ph = -90.0 + i * (360.0 / N_UNITS) + 34.0 * ((i % 3) - 1)
    ux, uy = angle(ph)
    px = CENTER[0] + rr * ux
    py = CENTER[1] + rr * uy
    px = min(max(px, half + 2), FRAME - half - 2)
    py = min(max(py, half + 2), FRAME - half - 2)
    scat = (px, py)
    scat_rot = (fig_rot + 58.0 * ((i % 5) - 2)) % 360.0
    return scat, scat_rot, fig, fig_rot


def smoothstep(s):
    s = min(1.0, max(0.0, s))
    return s * s * (3 - 2 * s)


def frame_states():
    """6 帧的插值参数；k 帧对应 s = k/(N_FRAMES-1)。"""
    return [(k * FPS_MS, smoothstep(k / (N_FRAMES - 1))) for k in range(N_FRAMES)]


def positions():
    out = []
    for k, (t, e) in enumerate(frame_states(), 1):
        rows = []
        for i in range(N_UNITS):
            spec = unit_spec(i)
            scat, srot, fig, frot = scatter_and_figure(i)
            x = scat[0] + (fig[0] - scat[0]) * e
            y = scat[1] + (fig[1] - scat[1]) * e
            rot = srot + (frot - srot) * e
            rows.append({**spec, "frame": k, "t_ms": t,
                         "center_x_px": round(x, 4), "center_y_px": round(y, 4),
                         "rotation_deg_clockwise": round(rot % 360.0, 4)})
        out.append({"frame": k, "t_ms": t, "easing_value_e": round(e, 6), "units": rows})
    return out


# ---------------------------------------------------------------- 图元
def rect(x, y, w, h, color, radius=0):
    c = "" if color is None else f' color="{color}"'
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container width="{w:.2f}" height="{h:.2f}"{c} borderRadius="{radius}"/>'
            f'</Positioned>')


def txt(t, x, y, w, h, size, color, family="Inter,Noto Sans CJK SC",
        weight="Inter Medium", align=None):
    q = "'" if '"' in t else '"'
    # textAlign 的合法取值是**大写**的 START / CENTER / END / JUSTIFY（另有 LEFT/RIGHT）。
    # 小写的 "left"/"right"/"center" 一律 400——这是本服务真实响应验证过的，
    # 见 tmp/run-20261011-01/_suite/probe/textalign-clippath-probe.json。
    at = (f' textAlign="{align}"' if align else "")
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Text{at} fontSize="{size}" color="{color}" '
            f'fontFamily="{weight},{family}" text={q}{t}{q}/></Positioned>')


def draw_unit(cx, cy, spec, rot, alpha_note=None):
    """在画布上画一个单元：绕自身中心顺时针旋转 rot 度。

    旋转用 Transform 的 4x4 仿射矩阵，box 只声明**未旋转**的宽高，
    因此「尺寸守恒」在 DSL 层面就是字面成立的。
    """
    w, h = spec["unrotated_width_px"], spec["unrotated_height_px"]
    r = spec["border_radius_px"]
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    # 4x4 列主序，纯旋转、平移为单位矩阵：Transform 的局部原点经 alignment="CENTER"
    # 正好落在外层 Positioned 盒的中心，也就是单元自己的中心，所以不用再加平移项。
    m = (f"{c:.6f},{s:.6f},0,0,"      # 第一列
         f"{-s:.6f},{c:.6f},0,0,"     # 第二列（顺时针 rot 度）
         f"0,0,1,0,"
         f"0,0,0,1")
    return (f'<Positioned left="{cx - w/2:.2f}" top="{cy - h/2:.2f}" '
            f'width="{w:.2f}" height="{h:.2f}">'
            f'<Transform matrix="({m})" alignment="CENTER">'
            f'<Container width="{w:.2f}" height="{h:.2f}" '
            f'color="{spec["color_rgb"]}" borderRadius="{r}"/></Transform></Positioned>')


def frame_dsl(states):
    b = []
    for row in states["units"]:
        b.append(draw_unit(row["center_x_px"], row["center_y_px"], row,
                           row["rotation_deg_clockwise"]))
    # 背景容器**不给 color**，因此画布是真实透明的
    return (f'<Snapshot type="png">\n<Container width="{FRAME}" height="{FRAME}">'
            f'<Stack fit="EXPAND">{"".join(b)}</Stack></Container>\n</Snapshot>\n')


def cover_dsl():
    W, H = COVER
    C_BG = "#0B1020"
    C_INK = "#F8FAFC"
    C_SUB = "#A5B4FC"
    b = [rect(0, 0, W, H, C_BG)]
    b.append(txt("从结构到画面", 84, 196, 700, 96, 72, C_INK, weight="Inter Semi Bold"))
    b.append(txt("Layerlight 结构化方法 · 发布预告", 84, 310, 700, 40, 30, C_SUB))
    b.append(rect(84, 386, 120, 4, "#FBBF24", 2))

    # 左栏：一行说明
    b.append(txt("12 个几何单元从散布位置逐步汇聚，", 84, 428, 620, 36, 26, C_INK))
    b.append(txt("在末帧闭合为可识别的光圈图形。", 84, 470, 620, 36, 26, C_INK))
    b.append(txt("6 帧 · 250 ms/帧 · 循环 1500 ms", 84, 560, 620, 32, 24, C_SUB))
    b.append(txt("透明关键帧 600×600 ｜ 封面 1200×800", 84, 600, 620, 32, 24, C_SUB))

    # 左栏底部：帧时序条（6 个采样点，与 timing.json 的 t_ms 一一对应）
    TR_X, TR_W, TR_Y = 84, 516, 668
    b.append(rect(TR_X, TR_Y, TR_W, 6, "#1E293B", 3))
    for k in range(1, N_FRAMES + 1):
        dx = TR_X + (k - 1) / (N_FRAMES - 1) * TR_W
        col = "#FBBF24" if k == N_FRAMES else "#60A5FA"
        b.append(rect(dx - 5, TR_Y - 5, 10, 16, col, 5))
        b.append(txt(f"f{k}", dx - 16, TR_Y + 22, 40, 26, 20, "#94A3B8"))
    b.append(txt("帧时序 0 / 250 / 500 / 750 / 1000 / 1250 ms，循环 1500 ms",
                 TR_X, TR_Y + 54, TR_W + 120, 28, 20, "#64748B"))

    # 右栏：末帧的 12 单元图形（封面里作为主视觉，不嵌任何预渲染图）
    scale = 1.28
    for i in range(N_UNITS):
        spec = unit_spec(i)
        scat, srot, fig, frot = scatter_and_figure(i)
        cx = 900 + (fig[0] - CENTER[0]) * scale
        cy = 392 + (fig[1] - CENTER[1]) * scale
        b.append(draw_unit(cx, cy, spec, frot))
    ring = (OUTER_R + BLADE_W / 2 + 8) * scale
    b.append(f'<Positioned left="{900 - ring:.2f}" top="{392 - ring:.2f}" '
             f'width="{2*ring:.2f}" height="{2*ring:.2f}">'
             f'<Container width="{2*ring:.2f}" height="{2*ring:.2f}" '
             f'color="#FFFFFF00" borderRadius="{ring}" border="2 SOLID #1E293B"/>'
             f'</Positioned>')
    b.append(txt("末帧 · 结构汇聚成的光圈", 900 - ring, 392 + ring + 30,
                 2 * ring, 30, 24, C_SUB, align="CENTER"))
    return (f'<Snapshot type="png">\n<Container width="{W}" height="{H}" color="{C_BG}">'
            f'<Stack fit="EXPAND">{"".join(b)}</Stack></Container>\n</Snapshot>\n')


def contact_sheet_dsl(states):
    """6 帧接触表：3 列 × 2 行，每格把 600×600 的帧按 0.5 缩放重绘。

    刻意**不**用 <Image> 贴已渲染的帧——那才是「嵌预渲染帧」。
    这里是把同一份 frame_states() 的参数再走一遍 draw_unit()，
    所以接触表与各帧必然一致，同时 contact-sheet 本身也是一次真实服务响应。
    """
    W, H = 1020, 812
    S = 0.5                      # 每格 300×300
    CW, CH = 320, 330            # 格子含边距（130 顶部偏移 + 300 格高 + 30 标签）
    b = [rect(0, 0, W, H, "#0B1020")]
    b.append(txt("关键帧接触表 · 6 帧 · 250 ms/帧", 40, 30, 700, 44, 34, "#F8FAFC",
                 weight="Inter Semi Bold", align="CENTER"))
    b.append(txt("单元位置与旋转由同一份参数重绘，未嵌入任何已渲染帧", 40, 78, 940, 30,
                 22, "#A5B4FC", align="CENTER"))
    for f in states:
        k = f["frame"] - 1
        ox = 40 + (k % 3) * CW
        oy = 130 + (k // 3) * CH
        b.append(rect(ox, oy, FRAME * S, FRAME * S, "#FFFFFF0A", 10))
        for u in f["units"]:
            # 帧内坐标 (0..600) -> 格内 (0..300)，再平移到格子原点
            sx = u["center_x_px"] * S
            sy = u["center_y_px"] * S
            su = {**u,
                  "unrotated_width_px": u["unrotated_width_px"] * S,
                  "unrotated_height_px": u["unrotated_height_px"] * S,
                  "border_radius_px": u["border_radius_px"] * S}
            b.append(draw_unit(ox + sx, oy + sy, su, u["rotation_deg_clockwise"]))
        b.append(txt(f'f{f["frame"]} · t={f["t_ms"]} ms', ox, oy + FRAME * S + 6,
                     200, 26, 20, "#94A3B8"))
    return (f'<Snapshot type="png">\n<Container width="{W}" height="{H}" color="#0B1020">'
            f'<Stack fit="EXPAND">{"".join(b)}</Stack></Container>\n</Snapshot>\n')


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    DRAFTS.mkdir(parents=True, exist_ok=True)
    st = positions()

    # ---- 守恒断言：每个 ID 的几何/宽高/颜色/alpha 跨帧一致
    base = {u["unit_id"]: u for u in st[0]["units"]}
    for f in st[1:]:
        for u in f["units"]:
            b0 = base[u["unit_id"]]
            for k in ("geometry", "unrotated_width_px", "unrotated_height_px",
                      "border_radius_px", "color_rgb", "alpha"):
                assert u[k] == b0[k], f'{u["unit_id"]} 的 {k} 跨帧变化'
    for f in st:
        assert len(f["units"]) == N_UNITS
        for u in f["units"]:
            hw = max(u["unrotated_width_px"], u["unrotated_height_px"]) / 2
            assert hw <= u["center_x_px"] <= FRAME - hw, f'{u["unit_id"]} 越出画布'
            assert hw <= u["center_y_px"] <= FRAME - hw, f'{u["unit_id"]} 越出画布'
    (DRAFTS / f"states-{ver}.json").write_text(
        json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")

    for f in st:
        k = f["frame"]
        (DRAFTS / f"a23-frame-{k:02d}-{ver}.snapshot").write_text(
            frame_dsl(f), encoding="utf-8")
    (DRAFTS / f"a23-cover-{ver}.snapshot").write_text(cover_dsl(), encoding="utf-8")
    (DRAFTS / f"a23-contact-sheet-{ver}.snapshot").write_text(
        contact_sheet_dsl(st), encoding="utf-8")

    # ---- 接缝量测
    steps = []
    for k in range(N_FRAMES - 1):
        a, b2 = st[k]["units"], st[k + 1]["units"]
        rows = []
        for u0, u1 in zip(a, b2):
            d = math.hypot(u1["center_x_px"] - u0["center_x_px"],
                           u1["center_y_px"] - u0["center_y_px"])
            dr = (u1["rotation_deg_clockwise"] - u0["rotation_deg_clockwise"]) % 360.0
            if dr > 180:
                dr -= 360.0
            rows.append({"from_frame": u0["frame"], "to_frame": u1["frame"],
                         "displacement_px": round(d, 3),
                         "rotation_delta_deg": round(dr, 3)})
        steps.append({"step": f"{u0['frame']}->{u1['frame']}", "units": rows})
    seam = []
    for u0, u1 in zip(st[-1]["units"], st[0]["units"]):
        d = math.hypot(u1["center_x_px"] - u0["center_x_px"],
                       u1["center_y_px"] - u0["center_y_px"])
        dr = (u1["rotation_deg_clockwise"] - u0["rotation_deg_clockwise"]) % 360.0
        if dr > 180:
            dr -= 360.0
        seam.append({"unit_id": u0["unit_id"], "displacement_px": round(d, 3),
                     "rotation_delta_deg": round(dr, 3)})
    mean_step = sum(s["units"][0]["displacement_px"] for s in steps) / len(steps)
    (DRAFTS / f"steps-{ver}.json").write_text(
        json.dumps({"steps": steps, "seam": seam,
                    "mean_first_unit_step_px": round(mean_step, 3)},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("frames written:", len(st), "| units:", N_UNITS)
    print("seam U01 disp:", seam[0], "| mean step U01:", round(mean_step, 2))


if __name__ == "__main__":
    main()