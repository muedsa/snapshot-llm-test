"""A23 - assemble the delivered JSONs.

frame-data.json merges what the DSL claims (kit.py) with what the pixels show (audit.py),
so every position, size and visibility statement in it is backed by a measurement rather
than by the generator's own hope. timing.json carries the playback contract and the
honest seam verdict.

Run:  python tmp/<run_id>/A23/deliver.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A23"
OUT = ROOT / "outputs" / RUN / "A23"
sys.path.insert(0, str(TMP))
import kit as K  # noqa: E402


def main():
    fd = json.loads((TMP / "frame-data.json").read_text(encoding="utf-8"))
    au = json.loads((TMP / "audit.json").read_text(encoding="utf-8"))
    meas = {(fr["frame"], u["id"]): u for fr in au["frames"] for u in fr["units"]}
    by_id = {u["id"]: u for u in fd["units"]}

    frames = []
    for n in range(1, 7):
        entries = []
        for uid, u in by_id.items():
            st = u["frames"][n - 1]
            m = meas[(n, uid)]
            entries.append({
                "id": uid, "shape": u["shape"],
                "unrotated_size": [u["w"], u["h"]],
                "x": st["x"], "y": st["y"], "rotation_deg": st["rot"],
                "colour": u["colour"], "alpha": u["alpha"],
                "painted_px": m["painted_px"],
                "expected_visible_samples": m["expected_visible_samples"],
                "missing_samples": m["missing_samples"],
                "missing_interior_samples": m["missing_interior_samples"],
                "painted_outside_footprint_pad4": m["painted_outside_footprint_pad4"],
                "visibility_ratio": m["visibility_ratio"],
                "visible": m["painted_px"] > 200 and m["visibility_ratio"] > 0.5,
                "hidden_by_later_units_px": m["hidden_samples"],
                "png": f"frame-{n:02d}.png", "dsl": f"frame-{n:02d}.snapshot"})
        frames.append({"frame": n, "id": f"frame-{n:02d}", "t_ms": (n - 1) * K.STEP_MS,
                       "png": f"frame-{n:02d}.png", "dsl": f"frame-{n:02d}.snapshot",
                       "transparent": True,
                       "transparent_fraction": au["frames"][n - 1]["transparent_fraction"],
                       "png_mode": au["frames"][n - 1]["mode"],
                       "units": entries})

    trajectories = []
    for uid, u in by_id.items():
        trajectories.append({
            "id": uid,
            "interpolation": {"kind": "closed-form spiral with smoothstep",
                              "position": "r(τ)=r0+(r_slot-r0)·e(τ), "
                                          "θ(τ)=θ0+(θ_slot-θ0)·e(τ)",
                              "rotation": "rot(τ)=rot0+(rot_slot-rot0)·e(τ)",
                              "easing": "e(τ)=τ²(3-2τ)", "tau": "τ=(frame-1)/5",
                              "note": "插值只描述设计轨迹；中间帧未渲染，交付的就是这 6 帧"},
            "steps": u["steps"], "seam_step": u["seam_step"]})

    out = {
        "schema_version": 1, "task_id": "A23", "path_base": "output_dir",
        "coordinate_system": {
            "origin": "canvas top-left", "x": "right", "y": "down", "unit": "px",
            "position_meaning": "单元几何中心 (x, y)",
            "rotation": "以自身中心为原点、顺时针度数（Transform.matrix + alignment=CENTER）",
            "size_meaning": "w/h 为未旋转几何尺寸；旋转后的外包框不计入尺寸"},
        "canvas": fd["canvas"],
        "conservation_rule": fd["conservation"],
        "units": [{k: v for k, v in u.items() if k != "frames"} for u in fd["units"]],
        "frames": frames,
        "trajectories": trajectories,
        "seam": {
            "transition": "frame-06 (t=1250ms) -> frame-01 (t=1500ms ≡ 0ms)",
            "per_unit": [u["seam_step"] for u in fd["units"]],
            "closed_trajectory": False,
            "position_continuous_at_wrap": False,
            "rotation_continuous_at_wrap": False,
            "measured": au["loop"],
            "comparison": (
                "序列内相邻步长中位数 "
                f"{au['loop']['in_sequence_displacement_px']['median']}px、"
                f"转向中位数 {au['loop']['in_sequence_rotation_delta_deg']['median']}°；"
                f"接缝位移中位数 {au['loop']['seam_displacement_px']['median']}px"
                f"（{au['loop']['seam_over_in_sequence_median']}×）、"
                f"转向中位数 {au['loop']['seam_rotation_delta_deg']['median']}°，"
                "方向与各单元到达画面的方向相反"),
            "verdict": ("跳变：第 6 帧是终点而不是环上一点，循环播放时 12 个单元会沿各自"
                        "螺旋瞬间退回散布起点；不宣称无缝"),
            "evidence": {
                "path_base": "suite_root",
                "path": f"tmp/{RUN}/A23/audit.json",
                "contact_sheet": f"tmp/{RUN}/A23/contact-sheet.png"},
        },
        "verification": {
            "method": au["method"],
            "tolerance_sum_abs": au["tolerance_sum_abs"],
            "min_pairwise_colour_distance_sum_abs": au["min_pairwise_colour_distance_sum_abs"],
            "footprint_padding_px": au["footprint_padding_px"],
            "sample_step_px": au["sample_step_px"],
            "per_frame": [{"frame": f["frame"],
                           "units_visible": sum(1 for e in f["units"] if e["visible"]),
                           "max_missing_interior_samples":
                               au["frames"][n - 1]["max_missing_interior_samples"],
                           "max_painted_outside_footprint_pad4":
                               au["frames"][n - 1]["max_outside_footprint_pad4"],
                           "any_unit_touches_canvas_edge":
                               au["frames"][n - 1]["any_touches_edge"],
                           "transparent_fraction": f["transparent_fraction"],
                           "png_mode": f["png_mode"]}
                          for n, f in enumerate(frames, 1)],
            "conservation": au["conservation"]},
        "cover": {"png": "cover.png", "dsl": "cover.snapshot",
                  "size": list(K.COVER), "opaque_background": "#F5F7FC",
                  "headline": "从结构到画面"},
    }
    (OUT / "frame-data.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    timing = {
        "schema_version": 1, "task_id": "A23", "path_base": "output_dir",
        "intent": "6 帧透明 PNG 关键帧 + 时间数据；本题不交付 GIF（服务不支持，见 limitations.md）",
        "frames": [{"order": n, "id": f"frame-{n:02d}", "file": f"frame-{n:02d}.png",
                    "dsl": f"frame-{n:02d}.snapshot", "t_ms": (n - 1) * K.STEP_MS,
                    "duration_ms": K.STEP_MS} for n in range(1, 7)],
        "frame_duration_ms": K.STEP_MS,
        "loop": True,
        "period_ms": K.PERIOD_MS,
        "frame_count": 6,
        "transparent": True,
        "seamless": False,
        "seam_evidence": {
            "where": "frame-06 (t=1250ms) 之后回到 frame-01 (t=1500ms ≡ 0ms)",
            "effect": "12 个单元瞬间从画面位置退回各自散布起点，画面消失",
            "measured": {
                "seam_displacement_px_median":
                    out["seam"]["measured"]["seam_displacement_px"]["median"],
                "in_sequence_displacement_px_median":
                    out["seam"]["measured"]["in_sequence_displacement_px"]["median"],
                "ratio": out["seam"]["measured"]["seam_over_in_sequence_median"],
                "seam_rotation_delta_deg_median":
                    out["seam"]["measured"]["seam_rotation_delta_deg"]["median"]},
            "per_unit_reference": "frame-data.json → seam.per_unit",
            "viewed": {"path_base": "suite_root",
                       "path": f"tmp/{RUN}/A23/contact-sheet.png",
                       "note": "接触表按 1→6 顺序逐格查看，末格为首尾相接的样子"},
            "why_not_closed": (
                "轨迹是单向汇聚：匀速闭合轨道会让第 1 帧的离散度低于第 3 帧（必须先散后聚），"
                "与“由分散逐步汇聚”冲突，因此保留跳变并如实记录"),
            "workaround_for_playback": "需要无跳变播放时按 1→6→5→…→2 往返（ping-pong）播放，"
                                       "或把第 6 帧作为定格终点单次播放"},
        "easing": out["trajectories"][0]["interpolation"],
    }
    (OUT / "timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1)
                                     + "\n", encoding="utf-8")
    print(json.dumps({"frames": len(frames), "units": len(out["units"]),
                      "visible_all": all(len([e for e in f["units"] if e["visible"]]) == 12
                                         for f in frames),
                      "seamless": timing["seamless"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
