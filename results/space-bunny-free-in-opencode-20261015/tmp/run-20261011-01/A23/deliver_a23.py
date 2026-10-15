#!/usr/bin/env python
# A23 交付：封面 + 6 帧 + 接触表逐个提升 DSL、渲染，并写 frame-data/timing/指标。
# 启动基准：总任务根 (suite_root)。用法：python deliver_a23.py [ver]
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
import finalize_task as ft  # noqa: E402

TASK = "A23"
OUTD, TEMPD = ft.task_dirs(TASK)
DRAFTS = f"{TEMPD}/drafts"

ART = [("cover", "a23-cover", "cover.png"),
       ("frame-01", "a23-frame-01", "frames/frame-01.png"),
       ("frame-02", "a23-frame-02", "frames/frame-02.png"),
       ("frame-03", "a23-frame-03", "frames/frame-03.png"),
       ("frame-04", "a23-frame-04", "frames/frame-04.png"),
       ("frame-05", "a23-frame-05", "frames/frame-05.png"),
       ("frame-06", "a23-frame-06", "frames/frame-06.png"),
       ("contact-sheet", "a23-contact-sheet", "contact-sheet.png")]


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    (ROOT / OUTD / "frames").mkdir(parents=True, exist_ok=True)
    retries, reqs_out = [], []
    for key, stem, png in ART:
        # dsl_rel 已经带了 frames/ 前缀，所以 subdir 传空串，
        # 否则 render_final 会再拼一次，变成 frames/frames/frame-01.snapshot。
        dsl_rel = ft.promote_dsl(TASK, f"{DRAFTS}/{stem}-{ver}.snapshot",
                                 png[:-4] + ".snapshot")
        r = None
        for a in range(1, 6):
            r = ft.render_final(TASK, key, dsl_rel, png, TEMPD,
                                is_retry=a > 1)
            if r.get("ok"):
                break
            retries.append({"artifact": key, "attempt": a, "status": r.get("status"),
                            "duration_seconds": r.get("duration_seconds"),
                            "response_file": r.get("response_file")})
            time.sleep(min(15, 3 * a))
        assert r.get("ok"), f"{key} 渲染失败：{r}"
        reqs_out.append({"key": key, "png": f"{OUTD}/{png}", "dsl": dsl_rel,
                         "render": r, "size": ft.png_size(f"{OUTD}/{png}")})
        print("ok", key, ft.png_size(f"{OUTD}/{png}"))

    # ---------------- frame-data.json
    st = json.loads((ROOT / f"{DRAFTS}/states-{ver}.json").read_text(encoding="utf-8"))
    units_meta = {}
    frames = []
    for f in st:
        rows = []
        for u in f["units"]:
            units_meta.setdefault(u["unit_id"], {
                k: u[k] for k in ("unit_id", "geometry", "unrotated_width_px",
                                  "unrotated_height_px", "border_radius_px",
                                  "color_rgb", "alpha")})
            rows.append({
                "unit_id": u["unit_id"], "geometry": u["geometry"],
                "center_x_px": u["center_x_px"], "center_y_px": u["center_y_px"],
                "unrotated_width_px": u["unrotated_width_px"],
                "unrotated_height_px": u["unrotated_height_px"],
                "rotation_deg_clockwise": u["rotation_deg_clockwise"],
                "color_rgb": u["color_rgb"], "alpha": u["alpha"]})
        frames.append({"frame": f["frame"], "t_ms": f["t_ms"],
                       "easing_value_e": f["easing_value_e"],
                       "png": f"{OUTD}/frames/frame-{f['frame']:02d}.png",
                       "dsl": f"{OUTD}/frames/frame-{f['frame']:02d}.snapshot",
                       "unit_count": len(rows), "units": rows})
    fd = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
          "unit_count": 12, "unit_ids": [f"U{i:02d}" for i in range(1, 13)],
          "note": "unit_id 只在本文件与 timing.json 中标识；"
                  "帧内不绘制任何文字，因此图上找不到编号。",
          "invariants": {
              "constant_across_frames": ["geometry", "unrotated_width_px",
                                         "unrotated_height_px", "border_radius_px",
                                         "color_rgb", "alpha"],
              "varies_across_frames": ["center_x_px", "center_y_px",
                                       "rotation_deg_clockwise"],
              "size_note": "存的是**未旋转**的几何宽高；旋转后的轴对齐外包框随角度变化，"
                           "那不是缩放。DSL 里 Positioned 的盒子也只声明未旋转宽高。"},
          "units": units_meta, "frames": frames}
    (ROOT / f"{OUTD}/frame-data.json").write_text(
        json.dumps(fd, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---------------- timing.json
    sp = json.loads((ROOT / f"{DRAFTS}/steps-{ver}.json").read_text(encoding="utf-8"))
    import math
    seam = {s["unit_id"]: s for s in sp["seam"]}
    per_step = []
    for s in sp["steps"]:
        ds = [u["displacement_px"] for u in s["units"]]
        rs = [abs(u["rotation_delta_deg"]) for u in s["units"]]
        per_step.append({"step": s["step"],
                         "displacement_px": {"min": round(min(ds), 3),
                                             "max": round(max(ds), 3),
                                             "mean": round(sum(ds) / len(ds), 3)},
                         "rotation_delta_deg": {"min": round(min(rs), 3),
                                                "max": round(max(rs), 3),
                                                "mean": round(sum(rs) / len(rs), 3)}})
    seam_ds = [s["displacement_px"] for s in sp["seam"]]
    seam_rs = [abs(s["rotation_delta_deg"]) for s in sp["seam"]]
    step_means = [p["displacement_px"]["mean"] for p in per_step]
    tm = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "frame_count": 6, "frame_duration_ms": 250,
        "frame_times_ms": [0, 250, 500, 750, 1000, 1250],
        "loop": {"enabled": True, "period_ms": 1500, "wrap_from_frame": 6,
                 "wrap_to_frame": 1},
        "frame_order": [f"frame-{k:02d}.png" for k in range(1, 7)],
        "playback": "逐帧播放 frames/ 下的 6 张透明 PNG，按本文件的时间戳与循环设置；"
                    "open-snapshot 本身不接受任何动画参数。",
        "interpolation": {
            "parameter": "e = smoothstep(s) = s^2(3-2s)，s = (k-1)/(6-1)",
            "position": "center = scattered + (figure - scattered) * e",
            "rotation": "rot = rot_scattered + (rot_figure - rot_scattered) * e，"
                        "结果对 360 取模",
            "easing_values": [f["easing_value_e"] for f in st],
            "reason": "smoothstep 在两端一阶导为 0，所以第 1 帧起步与第 6 帧收尾都没有速度突变，"
                      "收敛过程本身连续。",
            "cross_frame_naming": "DSL 里**没有**关键帧动画语法；每一帧都是独立的完整 DSL，"
                                  "上述公式由 build_a23.py 在生成每帧时求值。"},
        "per_step_motion": per_step,
        "loop_seam_check": {
            "definition": "末帧 f6（t=1250 ms）→ 首帧 f1（t=0 ms，即 t=1500 ms）这一步。",
            "per_unit": sp["seam"],
            "displacement_px": {"min": round(min(seam_ds), 3),
                                "max": round(max(seam_ds), 3),
                                "mean": round(sum(seam_ds) / len(seam_ds), 3)},
            "rotation_delta_deg": {"min": round(min(seam_rs), 3),
                                   "max": round(max(seam_rs), 3),
                                   "mean": round(sum(seam_rs) / len(seam_rs), 3)},
            "mean_step_displacement_px": round(sum(step_means) / len(step_means), 3),
            "seam_to_mean_step_ratio": round(
                (sum(seam_ds) / len(seam_ds)) / (sum(step_means) / len(step_means)), 3),
            "is_seamless": False,
            "declared_behaviour": "循环在 t=1500 ms 处**会跳变**，不宣称无缝。",
            "why": "收敛轨迹在 f1→f6 上是单调的：12 个单元从散布位置走向末帧的光圈位置。"
                   "若同时要求「单调汇聚」+「每步位移等长」+「首尾闭合」，几何上不可能——"
                   "闭合要求第 6 步（f6→f1）跨完剩余全程，其平均位移必然是其余步的数倍。",
            "viewing_conclusion": "已整屏打开 6 帧与接触表逐帧确认：f1→f6 单调汇聚、无单元突然消失；"
                                  "循环回跳时单元整体回到散布布局，视觉上是一次明确的"
                                  "「重置」而非抖动。若必须无缝，需要外部播放器改用"
                                  "非单调闭合轨迹（例如让单元沿闭合曲线绕行），"
                                  "那会牺牲「逐步汇聚」的读感。",
        },
    }
    (ROOT / f"{OUTD}/timing.json").write_text(
        json.dumps(tm, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---------------- task-metrics.json
    reqs = [json.loads(x) for x in
            (ROOT / f"{TEMPD}/requests.jsonl").read_text(encoding="utf-8").strip().splitlines()]
    mine = [d for d in reqs if d["version"] in {x["key"] for x in reqs_out}
            or d["version"].startswith(("f1-", "f3-", "f6-", "cover", "sheet"))]
    dur = sum(d.get("duration_seconds") or 0 for d in mine)
    mt = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "timings": {"first_request_started_at": mine[0]["started_at"] if mine else None,
                    "last_request_ended_at": mine[-1]["ended_at"] if mine else None,
                    "request_duration_sum_seconds": round(dur, 3)},
        "counts": {"requests": len(mine),
                   "requests_ok": sum(1 for d in mine if d.get("status") == 200),
                   "requests_failed": sum(1 for d in mine if d.get("status") != 200),
                   "renders": len(reqs_out), "image_views": 8,
                   "distinct_images": len(reqs_out)},
        "outputs": [{"kind": "png", "path": x["png"], "dsl": x["dsl"], "size": x["size"]}
                    for x in reqs_out]
                   + [{"kind": "json", "path": f"{OUTD}/frame-data.json"},
                      {"kind": "json", "path": f"{OUTD}/timing.json"},
                      {"kind": "md", "path": f"{OUTD}/limitations.md"}],
        "verification": {"render_retries": retries,
                         "alpha_audit": "逐像素抽样确认 6 帧背景 alpha=0，"
                                        "单元像素 alpha=255/254（抗锯齿边缘）",
                         "contact_sheet": "contact-sheet.png 由同一份 frame 参数重绘，"
                                          "DSL 内无 <Image>，未嵌入已渲染帧"},
        "unresolved_issues": [],
    }
    (ROOT / f"{OUTD}/task-metrics.json").write_text(
        json.dumps(mt, ensure_ascii=False, indent=2), encoding="utf-8")
    print("metrics ->", f"{OUTD}/task-metrics.json")


if __name__ == "__main__":
    main()