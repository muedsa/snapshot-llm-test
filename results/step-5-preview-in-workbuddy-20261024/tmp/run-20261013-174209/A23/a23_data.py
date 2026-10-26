#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A23 · 生成 frame-data.json / timing.json / limitations.md。

frame-data.json 与 timing.json 的字段遵循
tasks/A23-capability-delivery/templates/audit-fields.json 的最小字段约定；
所有几何/轨迹数值由 a23_units 的参数实时计算，像素类证据（墨迹像素数、
实际外包框）从最终 PNG 实测回填，不预填、不虚构。
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))

from a23_units import (units, pose_at, bbox_half, angle_delta, trajectories,
                       progress, FRAME_W, FRAME_H, COVER_W, COVER_H,
                       FRAME_MS, PERIOD_MS, N_FRAMES, R_OUT, R_IN, BAR_T,
                       BAR_OV, BAR_RADIUS, CORE_D, GEM, JOINT_CHECK,
                       star_edges)

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = "run-20261013-174209"
OUT = ROOT / "outputs" / RUN_ID / "A23"
TMP = ROOT / "tmp" / RUN_ID / "A23"


def measure_unit(arr, u, k):
    """从最终 PNG 实测该单元的墨迹像素数与可见性。"""
    col = np.array([int(u["color"][1:3], 16), int(u["color"][3:5], 16),
                    int(u["color"][5:7], 16)])
    d = np.abs(arr[:, :, :3].astype(int) - col).max(axis=2)
    need = int(round(u["alpha"] * 255))
    m = (d <= 14) & (arr[:, :, 3] >= max(1, need - 12))
    cnt = int(m.sum())
    if cnt:
        ys, xs = np.nonzero(m)
        box = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    else:
        box = None
    return cnt, box


def geom_name(u):
    return {"bar": "rounded_rect", "circle": "circle", "gem": "rounded_square"}[
        u["geom"]]


def build():
    us = units()
    imgs = {k: np.asarray(
        Image.open(OUT / f"frame-{k:02d}.png").convert("RGBA"))
        for k in range(1, N_FRAMES + 1)}

    # ---------------- units ----------------
    unit_tbl = []
    for u in us:
        r, g, b = (int(u["color"][1:3], 16), int(u["color"][3:5], 16),
                   int(u["color"][5:7], 16))
        unit_tbl.append({
            "id": u["id"], "role": u["role"], "geometry": geom_name(u),
            "width": u["w"], "height": u["h"],
            "border_radius": (u["radius"] if u["geom"] != "circle" else None),
            "color": u["color"], "rgb": [r, g, b], "alpha": u["alpha"],
            "notes": ("未旋转宽高；跨帧恒定" if u["geom"] != "circle" else
                      "正圆，直径 = width = height；跨帧恒定"),
        })

    # ---------------- frames ----------------
    frames = []
    for k in range(1, N_FRAMES + 1):
        arr = imgs[k]
        fu = []
        for u in us:
            p = pose_at(u, k - 1)
            hw, hh = bbox_half(u, p["rot"])
            cnt, mbox = measure_unit(arr, u, k)
            fully_inside = (p["cx"] - hw >= 0 and p["cy"] - hh >= 0
                            and p["cx"] + hw <= FRAME_W
                            and p["cy"] + hh <= FRAME_H)
            fu.append({
                "id": u["id"], "geometry": geom_name(u),
                "visible": bool(cnt > 0),
                "x": round(p["cx"], 4), "y": round(p["cy"], 4),
                "width": u["w"], "height": u["h"],
                "rotation_deg": round(p["rot"], 4),
                "color": u["color"], "alpha": u["alpha"],
                "declared_box": [round(p["cx"] - hw, 4), round(p["cy"] - hh, 4),
                                 round(p["cx"] + hw, 4), round(p["cy"] + hh, 4)],
                "fully_inside_canvas": bool(fully_inside),
                "measured_ink_pixels": cnt,
                "measured_color_bbox": mbox,
            })
        frames.append({
            "id": f"frame-{k:02d}", "t_ms": FRAME_MS[k - 1],
            "png": f"frame-{k:02d}.png", "dsl": f"frame-{k:02d}.snapshot",
            "canvas": [FRAME_W, FRAME_H], "background": "transparent",
            "contains_text": False,
            "units": fu,
        })

    # ---------------- trajectories ----------------
    traj = trajectories(us)
    traj_out = []
    for t in traj:
        u = next(x for x in us if x["id"] == t["id"])
        steps = []
        for s in t["steps"]:
            steps.append({
                "from_t_ms": s["from_t_ms"], "to_t_ms": s["to_t_ms"],
                "dx": s["dx"], "dy": s["dy"],
                "distance_px": s["distance"],
                "direction_deg": round(math.degrees(
                    math.atan2(s["dy"], s["dx"])) % 360.0, 4),
                "d_rotation_deg": s["d_rotation_deg"],
            })
        seam = t["seam_step_1250_to_1500"]
        traj_out.append({
            "id": t["id"],
            "interpolation": "piecewise_linear",
            "easing_formula": t["easing"],
            "intermediate_frames_rendered": False,
            "steps": steps,
            "interframe_distance_max_px": t["interframe_distance_max"],
            "interframe_distance_min_px": t["interframe_distance_min"],
            "interframe_distance_mean_px": t["interframe_distance_mean"],
            "seam_step_1250_to_1500": {
                "from_t_ms": seam["from_t_ms"], "to_t_ms": seam["to_t_ms"],
                "dx": seam["dx"], "dy": seam["dy"],
                "distance_px": seam["distance"],
                "direction_deg": round(math.degrees(
                    math.atan2(seam["dy"], seam["dx"])) % 360.0, 4),
                "d_rotation_deg": seam["d_rotation_deg"],
            },
            "seam_over_mean_ratio": t["seam_vs_mean_ratio"],
        })

    # ---------------- seam ----------------
    seam_units = []
    for t in traj:
        u = next(x for x in us if x["id"] == t["id"])
        s = t["seam_step_1250_to_1500"]
        dirs = [math.degrees(math.atan2(st["dy"], st["dx"])) % 360.0
                for st in t["steps"]]
        seam_dir = math.degrees(math.atan2(s["dy"], s["dx"])) % 360.0
        # 方向差（与首步方向比，360 等价）
        ddir = ((seam_dir - dirs[0]) + 180) % 360 - 180
        seam_units.append({
            "id": t["id"],
            "seam_dx": s["dx"], "seam_dy": s["dy"],
            "seam_distance_px": s["distance"],
            "seam_direction_deg": round(seam_dir, 4),
            "other_step_direction_deg": round(dirs[0], 4),
            "seam_direction_delta_vs_first_step_deg": round(ddir, 4),
            "seam_d_rotation_deg": s["d_rotation_deg"],
            "other_step_distance_mean_px": t["interframe_distance_mean"],
            "seam_over_mean_ratio": t["seam_vs_mean_ratio"],
        })
    # 位置闭合：循环使 t=1500 与 t=0 位姿相同（逐 ID 位移即散开偏移）
    pos_closed = True
    for u in us:
        if abs(pose_at(u, 0)["cx"] - pose_at(u, N_FRAMES - 1)["cx"]) > 1e-6:
            pos_closed = False
    seam = {
        "from_frame": "frame-06", "to_frame": "frame-01",
        "from_t_ms": 1250, "to_t_ms": 1500,
        "duration_ms": 250,
        "position_closed_by_loop": bool(pos_closed),
        "position_closed_note": "循环播放使 t=1500ms 的位姿与 t=0ms 相同；"
                                "因此接缝位移等于该单元首帧散开偏移的整体回退",
        "velocity_continuous": False,
        "velocity_note": "分段线性使第 1→6 帧每步位移恒为该单元总偏移的 1/5、"
                         "方向全部相同；接缝一步走完整条偏移，位移量为其余各步的 "
                         "5.0 倍、方向与其余各步相反（相差 180°）",
        "rotation_closed_by_loop": True,
        "units": seam_units,
        "seam_over_mean_ratio_range": [
            round(min(x["seam_over_mean_ratio"] for x in seam_units), 4),
            round(max(x["seam_over_mean_ratio"] for x in seam_units), 4)],
        "conclusion": "not_seamless",
        "conclusion_detail": (
            "末帧（可识别五角星）到首帧（分散）在 250ms 内一次性回退全部偏移，"
            "播放时在 frame-06 → frame-01 处出现一次可见的整体跳回；"
            "不宣称无缝循环。若要消除跳变，需改为双向（ping-pong）播放并补足 "
            "11 个关键帧，或改用闭合轨迹（但那样无法满足“由分散逐步汇聚”）。"),
        "viewing_evidence": (
            "tmp/run-20261013-174209/A23/preview/contact-sheet.png："
            "6 帧横向排列实际查看，frame-06 → frame-01 的位姿差为整体回退，"
            "肉眼可辨的一次性跳变"),
    }

    fd = {
        "schema_version": 1, "task_id": "A23", "path_base": "output_dir",
        "run_id": RUN_ID,
        "coordinate_system": {
            "origin": "canvas_top_left",
            "x_axis": "right", "y_axis": "down", "unit": "pixel",
            "position_semantics": "geometric_center_of_unrotated_geometry",
            "rotation_origin": "unit_own_center",
            "rotation_direction": "clockwise",
            "rotation_unit": "degree",
            "box_format": "[left, top, right, bottom]",
            "note": "宽高按未旋转几何记录；旋转只改朝向，不改变 width/height，"
                    "外包框变化不属于缩放",
        },
        "units": unit_tbl,
        "frames": frames,
        "trajectories": traj_out,
        "seam": seam,
        "design_constants": {
            "frame_canvas": [FRAME_W, FRAME_H],
            "cover_canvas": [COVER_W, COVER_H],
            "frame_count": N_FRAMES, "frame_interval_ms": 250,
            "period_ms": PERIOD_MS,
            "star_outer_radius": R_OUT, "star_inner_radius": round(R_IN, 4),
            "bar_thickness": BAR_T, "bar_end_overlap": BAR_OV,
            "bar_corner_radius": BAR_RADIUS,
            "core_diameter": CORE_D, "gem_size": GEM,
            "joint_solidity_check": JOINT_CHECK,
            "interpolation": "piecewise_linear, p_k = k/5",
        },
        "evidence": {
            "verification_report": "tmp/run-20261013-174209/A23/verify.json",
            "preview_dir": "tmp/run-20261013-174209/A23/preview/",
            "requests_log": "tmp/run-20261013-174209/A23/requests.jsonl",
        },
    }
    (OUT / "frame-data.json").write_text(
        json.dumps(fd, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------------- timing.json ----------------
    timing = {
        "schema_version": 1, "task_id": "A23", "path_base": "output_dir",
        "run_id": RUN_ID,
        "frames": [{
            "id": f"frame-{k:02d}", "order": k, "t_ms": FRAME_MS[k - 1],
            "duration_ms": 250, "file": f"frame-{k:02d}.png",
            "dsl": f"frame-{k:02d}.snapshot",
            "width": FRAME_W, "height": FRAME_H,
            "background": "transparent", "contains_text": False,
            "unit_count": len(us),
        } for k in range(1, N_FRAMES + 1)],
        "loop": True,
        "period_ms": PERIOD_MS,
        "frame_interval_ms": 250,
        "seamless": False,
        "seam_evidence": {
            "seam_step": "frame-06 (t=1250ms) -> frame-01 (t=1500ms == 0ms)",
            "position_closed_by_loop": seam["position_closed_by_loop"],
            "velocity_continuous": False,
            "seam_over_mean_ratio_range": seam["seam_over_mean_ratio_range"],
            "seam_direction_delta_vs_other_steps_deg": [
                round(x["seam_direction_delta_vs_first_step_deg"], 4)
                for x in seam_units],
            "rotation_delta_deg": [round(x["seam_d_rotation_deg"], 4)
                                   for x in seam_units],
            "detail": seam["velocity_note"],
            "conclusion": seam["conclusion"],
            "jump_description": (
                "循环时在 frame-06 → frame-01 处出现一次整体回跳：12 个单元在 "
                "250ms 内从汇聚完成位姿一次性回到首帧分散位姿，位移量为其余各步 "
                "的 5.0 倍、方向相反；视觉上是一次可辨的“重置”，不是无缝循环。"),
            "per_unit_evidence": "frame-data.json -> seam.units",
            "visual_check": (
                "tmp/run-20261013-174209/A23/preview/contact-sheet.png 实际查看"),
            "recommended_alternative": (
                "若需无缝：改为双向播放（frame-01..06 再 05..02）并补 11 个关键帧，"
                "或改为闭合轨迹；本题按题面授权只交付 6 个关键帧与时间数据。"),
        },
        "playback_note": (
            "6 张 PNG 为关键帧，未合成 GIF、未渲染中间帧；250ms/帧、"
            "循环、周期 1500ms 由本文件表达，需外部播放器或合成步骤落地。"),
        "cover": {"file": "cover.png", "dsl": "cover.snapshot",
                  "width": COVER_W, "height": COVER_H, "background": "#F4F6FB",
                  "title_text": "从结构到画面"},
    }
    (OUT / "timing.json").write_text(
        json.dumps(timing, ensure_ascii=False, indent=1), encoding="utf-8")
    print("frame-data.json / timing.json written")
    print("seam ratios:", seam["seam_over_mean_ratio_range"])
    print("seam dir deltas:", [round(x["seam_direction_delta_vs_first_step_deg"], 2)
                               for x in seam_units])
    print("seam rot deltas:", [round(x["seam_d_rotation_deg"], 2)
                               for x in seam_units])


if __name__ == "__main__":
    build()
