# -*- coding: utf-8 -*-
"""Build A23 deliverables frame-data.json + timing.json with real evidence.

argv: viewed_at view_note
Reads: tmp/.../design.json (poses/trajectories/seam from a23_common),
       tmp/.../verify-report.json (c-series pixel visibility, real PNGs).
Writes: outputs/run-20261011-01/A23/{frame-data.json,timing.json}
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a23_common as C  # noqa: E402

VIEWED_AT = sys.argv[1]
VIEW_NOTE = sys.argv[2]

TMP = "tmp/run-20261011-01/A23"
OUT = "outputs/run-20261011-01/A23"
SHEET = dict(path_base="suite_root",
             path="tmp/run-20261011-01/A23/contact-sheet.png",
             viewed_at=VIEWED_AT,
             note="6帧棋盘格接触表+逐帧600×600整图+" + VIEW_NOTE)
REPORT = dict(path_base="suite_root",
              path="tmp/run-20261011-01/A23/verify-report.json")

design = json.load(open(TMP + "/design.json", encoding="utf-8"))
verify = json.load(open(TMP + "/verify-report.json", encoding="utf-8"))
seam_rows = design["seam"]

# ---- frame-data.json ----
units_meta = []
for u in C.UNITS:
    units_meta.append(dict(
        id=u["id"], name=u["name"],
        geometry=dict(type="rect" if u["shape"] == "rect" else "circle",
                      width=u["w"], height=u["h"],
                      border_radius=u["radius"]),
        color_rgb=u["color"], alpha=1.0,
        final_pose=dict(x=u["fx"], y=u["fy"], rotation_deg=0.0),
        scatter_pose_f1=dict(x=u["sx"], y=u["sy"],
                             rotation_deg=float(u["srot"])),
        invariants=("type/width/height/color/alpha 跨帧守恒；仅位置与旋转变化；"
                    "圆形旋转恒为0（旋转对圆无视觉效果）")))

frames = []
for k in range(6):
    vr = verify["frames"][k]
    st = design["frames"][k]["state"]
    fu = []
    for u in C.UNITS:
        cx, cy, rot = st[u["id"]]
        v = vr["units"][u["id"]]
        fu.append(dict(id=u["id"], x=cx, y=cy, rotation_deg=rot,
                       width=u["w"], height=u["h"],
                       color=u["color"], alpha=1.0, visible=True,
                       pure_color_pixels=v["pure_pixels"],
                       frac_of_nominal=v["frac_of_nominal"]))
    frames.append(dict(
        id="F%d" % (k + 1), index=k + 1, t_ms=k * 250,
        png="frame-%02d.png" % (k + 1), dsl="frame-%02d.snapshot" % (k + 1),
        background="transparent", transparent_area_fraction=vr[
            "transparent_area_fraction"],
        corner_alpha0=vr["corners_alpha0"], units=fu))

trajectories = []
for t in design["trajectories"]:
    uid = t["id"]
    steps = [dict(from_frame="F%d" % s["from_frame"],
                  to_frame="F%d" % s["to_frame"],
                  dx=s["dx"], dy=s["dy"],
                  displacement_px=s["displacement_px"],
                  d_rotation_deg=s["d_rotation_deg"])
             for s in t["steps"]]
    trajectories.append(dict(
        id=uid,
        easing=("p(u) = p_final + (p_scatter − p_final)·(1−u)^1.35 ; "
                "θ(u) = θ_scatter·(1−u)^1.35 ; u = k/5, k=0..5 "
                "(ease-out 汇聚减速；关键帧采样 u=0,0.2,0.4,0.6,0.8,1.0)"),
        steps=steps,
        total_path_px=round(sum(s["displacement_px"] for s in steps), 2),
        note=("相邻关键帧之间无跳变；插值规则仅描述设计轨迹，"
              "本交付未渲染任何中间帧")))

seam_per_id = []
for r in seam_rows:
    seam_per_id.append(dict(
        id=r["id"], displacement_px=r["displacement_px"],
        rotation_diff_deg=r["rotation_diff_deg"],
        last_step_px_F5_F6=r["last_step_px"],
        ratio_vs_last_step=r["ratio_vs_last_step"],
        direction="汇聚 → 发散（方向反转）"))
mean_d = round(sum(r["displacement_px"] for r in seam_rows) / 12.0, 2)
max_d = max(r["displacement_px"] for r in seam_rows)
min_d = min(r["displacement_px"] for r in seam_rows)
mean_ratio = round(sum(r["ratio_vs_last_step"] for r in seam_rows) / 12.0, 2)

frame_data = dict(
    schema_version=1, task_id="A23", path_base="output_dir",
    canvas=dict(width=600, height=600, background="transparent"),
    coordinate_system=dict(
        origin="画布左上角像素 (0,0)", x_axis="向右", y_axis="向下",
        unit="px", position="几何中心 (x,y)",
        rotation="绕自身中心顺时针度数（正=顺时针；探针 A23-probe-01 实测："
                 "+45° 矩阵使端点标记落到右下）",
        size="未旋转几何的宽高（旋转后的外包框变化不是缩放）"),
    units=units_meta, frames=frames, trajectories=trajectories,
    seam=dict(
        window="t=1250ms (F6) → t=1500ms ≡ 0ms (F1，循环重启)",
        per_id=seam_per_id,
        closed=False, seamless=False,
        discontinuity_type="位置 + 旋转双重跳变",
        stats=dict(mean_displacement_px=mean_d, max_displacement_px=max_d,
                   min_displacement_px=min_d,
                   mean_ratio_vs_last_step=mean_ratio,
                   step_duration_ms=250),
        direction_velocity_evidence=(
            "接缝步（同为250ms）覆盖的位移为常规末步 F5→F6 的均值 %.2f 倍，"
            "速度突增且方向由向心汇聚反转为离心发散；旋转接缝差 10°–30°"
            "（末步旋转仅 %.1f°–%.1f°）" % (
                mean_ratio,
                min(abs(u["srot"]) for u in C.UNITS if u["srot"]) * 0.1139,
                max(abs(u["srot"]) for u in C.UNITS) * 0.1139)),
        actual_viewing_conclusion=(
            "实看接触表与逐帧：F6 为完整相机成图；循环回到 F1 时 12 个单元"
            "同时从成图位置跳回分散位置，跳变明显可见。不宣称无缝；"
            "建议 ping-pong 播放或末帧停留后重置。"),
        evidence=SHEET),
    verification=dict(
        bounds_check=("12单元×6帧旋转外包框全部位于画布内（margin≥8px，"
                      "生成期断言）"),
        min_visible_frac_overall=min(
            v["frac_of_nominal"] for fr in verify["frames"]
            for v in fr["units"].values()),
        color_conservation=("6帧均含且仅含12个单元纯色（纯色像素计数>0，"
                            "颜色集合逐帧一致）"),
        background_alpha=("四角 alpha=0；各帧透明面积占比 0.62–0.74；"
                          "PNG 实测 RGBA"),
        rendered_intermediates=0,
        report=REPORT))

# ---- timing.json ----
timing = dict(
    schema_version=1, task_id="A23", path_base="output_dir",
    theme="结构汇聚成图像",
    frames=[dict(index=k + 1, id="F%d" % (k + 1),
                 png="frame-%02d.png" % (k + 1),
                 dsl="frame-%02d.snapshot" % (k + 1),
                 t_ms=k * 250, duration_ms=250) for k in range(6)],
    loop=dict(
        enabled=True, period_ms=1500,
        seamless=False, seam_ref="frame-data.json#/seam",
        restart_behavior=("t=1500ms 硬切回 frame-01：12单元位置跳变均值 "
                          "%.1fpx（最大 %.1fpx、最小 %.1fpx），旋转跳变10°–30°"
                          % (mean_d, max_d, min_d)),
        impact=("循环播放时每 1.5s 出现一次明显重置跳变；前6帧内部轨迹连续、"
                "单元无突然消失或出现")),
    interpolation=dict(
        keyframe_sampling=("关键帧为设计轨迹 s(u)=(1−u)^1.35 在 "
                           "u=0,0.2,0.4,0.6,0.8,1.0 的采样，对应 t=0…1250ms"),
        between_keyframes=("若下游需要补中间帧，按相邻关键帧对位置与角度做"
                           "线性插值（设计轨迹的分段线性近似）"),
        rendered_intermediates=0,
        note="插值仅描述设计轨迹，不代表已渲染帧；交付物只有6张关键帧PNG"),
    fps_effective=4, frame_count=6,
    playback_order="frame-01 → frame-02 → … → frame-06 → (loop) frame-01",
    playback_recommendations=[
        "每帧 250ms、周期 1500ms 循环播放（frame-01…frame-06 顺序）",
        "如需避免循环跳变：ping-pong（1→6→1）或末帧停留后手动重置",
        "如需真正无缝循环：需重新设计闭合轨迹并给出 t=1500ms 位移=0 的"
        "证据（本版本未采用）"],
    evidence=SHEET)

os.makedirs(OUT, exist_ok=True)
with open(OUT + "/frame-data.json", "w", encoding="utf-8") as fh:
    json.dump(frame_data, fh, ensure_ascii=False, indent=1)
with open(OUT + "/timing.json", "w", encoding="utf-8") as fh:
    json.dump(timing, fh, ensure_ascii=False, indent=1)

print("frame-data.json: %d units, %d frames, %d trajectories, seam ids %d"
      % (len(frame_data["units"]), len(frame_data["frames"]),
         len(frame_data["trajectories"]), len(seam_per_id)))
print("timing.json: %d frames, loop period %dms seamless=%s"
      % (len(timing["frames"]), timing["loop"]["period_ms"],
         timing["loop"]["seamless"]))
print("min visible frac overall:", frame_data["verification"][
    "min_visible_frac_overall"])
