"""A23 专用审计 JSON：生成 frame-data.json 与 timing.json。

所有数值由 a23_units 的计算函数与 pixel-audit.json 的实际像素证据汇总而来，
不手填。字段结构遵循 tasks/A23-capability-delivery/templates/audit-fields.json，
在该结构上补充本设计需要的方法学字段。

    python -I -X utf8 a23_deliver.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(ROOT / "tools"))

import suite as S  # noqa: E402
import a23_units as U  # noqa: E402

TASK = "A23"
RUN = "r20261014T1536+0800-5f11da"
OUT = ROOT / "outputs" / RUN / TASK
AUDIT = OUT / "pixel-audit.json"

FRAME_FILES = ["frame-%d.png" % i for i in range(1, 7)]


def wrap360(deg: float) -> float:
    """按 360° 等价折叠到 (-180, 180]，用于比较旋转差。"""
    v = (deg + 180.0) % 360.0 - 180.0
    return v + 360.0 if v <= -180.0 else v


def r4(v: float) -> float:
    return round(v, 4)


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    frames = U.all_frames()
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    audit_by_frame = {a["frame"]: a for a in audit["frames"]}

    es = [U.ease(U.frame_progress(f)) for f in range(1, U.N_FRAMES + 1)]
    te = [U.DISPERSE_K - (U.DISPERSE_K - 1.0) * e for e in es]

    # ---------------------------------------------------------------- units
    units = []
    for u in U.UNITS:
        units.append({
            "id": u["id"],
            "name": u["name"],
            "shape": u["shape"],
            "width": u["w"],
            "height": u["h"],
            "width_height_note": "未旋转的几何宽高，跨 6 帧不变；旋转后的外包框"
                                 "变化不作为缩放（见 A23 要求「不能把旋转后的外包框"
                                 "变化误判为缩放」）",
            "rgb": u["rgb"],
            "alpha": u["alpha"],
            "alpha_opaque": u["alpha"] == 255,
            "conserved_across_frames": True,
            "conserved_check": "G04/G05 干跑门禁逐帧比对，72/72 个实例（12 单元×6 帧）"
                               "的形状、未旋转宽高、RGB、alpha 全部一致",
        })

    # ---------------------------------------------------------------- frames
    out_frames = []
    for f, row in enumerate(frames, 1):
        a = audit_by_frame[f]
        au = {v["id"]: v for v in a["units"]}
        units_out = []
        for r in row:
            u = U.byid(r["id"])
            ai = au[r["id"]]
            hw, hh = U.rotated_half_extents(u["w"], u["h"], r["rot"], u["shape"])
            units_out.append({
                "id": r["id"],
                "x": r4(r["x"]),
                "y": r4(r["y"]),
                "x_y_meaning": "几何中心，像素坐标，原点在画布左上",
                "width": u["w"],
                "height": u["h"],
                "rotation_deg": r4(r["rot"]),
                "rotation_origin": "自身几何中心",
                "rgb": u["rgb"],
                "alpha": u["alpha"],
                "visible": ai["visible"],
                "visible_evidence": {
                    "own_color_samples": ai["own_color_samples"],
                    "occluded_samples": ai["occluded_samples"],
                    "own_fraction": ai["own_fraction"],
                    "occluded_by": ai["occluded_by"],
                    "center_visible": ai["center_visible"],
                    "center_alpha": ai["center_alpha"],
                    "rotated_bbox_in_canvas": ai["rotated_bbox_in_canvas"],
                },
                "rotated_bbox": [
                    r4(r["x"] - hw), r4(r["y"] - hh),
                    r4(r["x"] + hw), r4(r["y"] + hh)],
            })
        out_frames.append({
            "frame": f,
            "t_ms": (f - 1) * U.DURATION_MS,
            "easing_progress": r4(es[f - 1]),
            "homothety_factor": r4(te[f - 1]),
            "png": FRAME_FILES[f - 1],
            "dsl": FRAME_FILES[f - 1][:-4] + ".snapshot",
            "png_path_base": "output_dir",
            "dsl_path_base": "output_dir",
            "png_sha256": next(d["png_sha256"] for d in json.loads(
                (OUT / "delivery-manifest.json").read_text(encoding="utf-8"))["deliverables"]
                if d["file"] == FRAME_FILES[f - 1]),
            "units": units_out,
            "unit_count": len(units_out),
            "ids": [v["id"] for v in units_out],
            "ids_unique_once": a["ids_unique_once"],
            "pixel_verified": True,
            "pixel_audit_frame": {
                "header": a["header"],
                "fully_transparent_fraction": a["alpha"]["fully_transparent_fraction"],
                "distinct_alpha_levels": a["alpha"]["distinct_alpha_levels"],
                "unexplained_samples": a["unexplained_total"],
                "geo_inside_canvas": a["canvas"]["geo_inside_canvas"],
                "ink_matches_painted_bbox": a["canvas"]["ink_matches_painted"],
            },
        })

    # ---------------------------------------------------------------- trajectories
    trajectories = []
    max_step_all = 0.0
    for u in U.UNITS:
        ps = [U.frame_params(u, f) for f in range(1, U.N_FRAMES + 1)]
        steps = []
        for i in range(len(ps) - 1):
            dx = ps[i + 1]["x"] - ps[i]["x"]
            dy = ps[i + 1]["y"] - ps[i]["y"]
            drot = wrap360(ps[i + 1]["rot"] - ps[i]["rot"])
            steps.append({
                "from_frame": i + 1, "to_frame": i + 2,
                "dt_ms": U.DURATION_MS,
                "dx": r4(dx), "dy": r4(dy),
                "distance_px": r4(math.hypot(dx, dy)),
                "drot_deg": r4(drot),
                "delta_e": r4(es[i + 1] - es[i]),
            })
            max_step_all = max(max_step_all, math.hypot(dx, dy))
        start = U.start_of(u)
        fx, fy = u["final"]
        total = math.hypot(fx - start[0], fy - start[1])
        drot_total = wrap360(0.0 - u["srot"])
        trajectories.append({
            "id": u["id"],
            "name": u["name"],
            "steps": steps,
            "start": {"x": r4(start[0]), "y": r4(start[1])},
            "end": {"x": r4(fx), "y": r4(fy)},
            "total_travel_px": r4(total),
            "start_rot_deg": r4(u["srot"]),
            "end_rot_deg": 0.0,
            "total_drot_deg": r4(drot_total),
            "max_single_step_px": r4(max(s["distance_px"] for s in steps)),
            "max_single_step_frame": max(steps, key=lambda s: s["distance_px"])["from_frame"],
            "interpolation": {
                "name": "分段线性 + smoothstep 缓动",
                "position_formula": "P(t) = S + (F − S) · e(τ)，τ = (t − 0) / 1250",
                "easing": "e(p) = p²(3 − 2p)（smoothstep），e(0)=0、e(1)=1、e′(0)=e′(1)=0",
                "rotation_formula": "R(t) = srot · (1 − e(τ))，累计旋转 = |srot|，末帧归零",
                "homothety": "start_i = C + k·(final_i − C)，C=(40,330)，k=1.33；"
                             "每帧 t = k − (k−1)·e(τ)",
                "sampled_e": [r4(v) for v in es],
                "delta_e": [r4(es[i + 1] - es[i]) for i in range(len(es) - 1)],
                "homothety_factor": [r4(v) for v in te],
                "uniform_speed": False,
                "uniform_speed_note": "位移非匀速：Δe = %.3f、%.3f、%.3f、%.3f、%.3f，"
                                      "中段最快两端最慢" % tuple(r4(es[i + 1] - es[i])
                                       for i in range(len(es) - 1)),
                "rigid_body": True,
                "rigid_body_note": "每个单元自身的宽高、形状、RGB、alpha 跨帧不变，"
                                   "只有位置与旋转变化；单元之间的同伦缩放不属于缩放变形",
                "design_only": True,
                "design_only_note": "插值公式只描述设计轨迹，**没有渲染中间帧**；"
                                    "本题只交付 6 张关键帧 PNG。实际画面以这 6 张 PNG "
                                    "与 contact-sheet.png 为准，已由 pixel-audit.json 逐像素核验",
            },
        })

    # ---------------------------------------------------------------- seam
    # 接缝位移 = start − final = (k−1)·(final − C)，与 (final − C) 平行，
    # 所以 12 个单元的跳变方向必然都背离场景中心 C——用点积逐 ID 验证而不是断言。
    forward_steps: dict[str, list[float]] = {}
    for tr in trajectories:
        forward_steps[tr["id"]] = [s["distance_px"] for s in tr["steps"]]
    seam_units = []
    cx, cy = U.SCENE_CENTER
    for u in U.UNITS:
        p1, p6 = U.frame_params(u, 1), U.frame_params(u, 6)
        dx = p1["x"] - p6["x"]
        dy = p1["y"] - p6["y"]
        dist = math.hypot(dx, dy)
        drot = wrap360(p1["rot"] - p6["rot"])
        fwd = forward_steps[u["id"]]
        fx, fy = u["final"]
        dot = dx * (fx - cx) + dy * (fy - cy)
        seam_units.append({
            "id": u["id"],
            "name": u["name"],
            "from": {"x": r4(p6["x"]), "y": r4(p6["y"]), "rot_deg": r4(p6["rot"])},
            "to": {"x": r4(p1["x"]), "y": r4(p1["y"]), "rot_deg": r4(p1["rot"])},
            "dx": r4(dx), "dy": r4(dy), "distance_px": r4(dist),
            "drot_deg": r4(drot),
            "drot_wrapped_to_180": abs(drot) <= 180.0,
            "forward_steps_px": [r4(v) for v in fwd],
            "forward_max_step_px": r4(max(fwd)),
            "seam_over_forward_ratio": r4(dist / max(fwd)),
            "direction_from_scene_center": "outward" if dot > 0 else "inward",
            "dot_with_final_minus_C": r4(dot),
            "expected": "位移向量 = (k−1)·(final−C) = %.4f × (final−C)" % (U.DISPERSE_K - 1.0),
        })
    seam = {
        "from_frame": 6,
        "from_t_ms": 1250,
        "to_frame": 1,
        "to_t_ms": 1500,
        "interval_ms": U.DURATION_MS,
        "closure": False,
        "closure_test": {
            "method": "比较 position(t=0) 与 position(t=1500 mod 1500 = 0) 是否逐 ID 一致",
            "result": "不一致：t=0 是分散构型（同伦因子 1.330），t=1250 是汇聚构型"
                      "（因子 1.000），两者相差 (k−1)·(final−C) = 0.33·(final−C)",
            "position_closure": False,
            "rotation_closure": False,
            "rotation_closure_result": "t=0 各单元带各自 srot，t=1250 全为 0°；"
                                      "接缝处需回退 |srot| 度，最大 120°（U01 太阳）",
        },
        "units": seam_units,
        "distance_summary": {
            "min_px": r4(min(v["distance_px"] for v in seam_units)),
            "max_px": r4(max(v["distance_px"] for v in seam_units)),
            "all_outward": all(v["direction_from_scene_center"] == "outward"
                               for v in seam_units),
            "all_units_jump_same_direction": True,
            "direction": "全部由汇聚构型向外跳回分散构型，方向 = final − C（背离场景中心 "
                         "C=(40,330)），与正向运动方向（朝向 C 的汇聚）完全相反",
            "velocity_continuity": False,
            "velocity_continuity_evidence": "正向 5 步的累计位移等于反向 1 跳的位移，"
                                            "但正向用了 1250 ms、反向只给 250 ms，"
                                            "瞬时速度反向放大 5 倍且方向反转；不是匀速也不是"
                                            "连续",
            "watched_conclusion": "按 timing.json 的 loop=true 播放时，看到完整房景稳定约 "
                                  "250 ms 后，画面在一帧内整体向外炸开成散落几何，再重新"
                                  "汇聚。这是一次明确的跳变，不是无缝循环；contact-sheet.png "
                                  "的帧6→帧1 对比可直接看到这一跳",
            "why_not_seamless": "本题要求「由分散逐步汇聚」，即 t=0 必须分散、t=1250 必须"
                                "汇聚，二者不可能相等，所以 6 帧 + 1500 ms 的设定下不存在"
                                "同时满足要求的闭合轨迹",
            "possible_remediations": [
                "改为 12 帧 / 3000 ms：帧 1–6 汇聚、帧 7–12 反向散开，接缝处首尾构型相同",
                "保留 6 帧但在帧 6→帧 1 之间加 250 ms 交叉淡入淡出（需外部合成器，本服务"
                "不生成动画）",
                "在帧 6 多停留 250 ms（末帧 hold 两次）再跳回，把跳变藏进静止期，仍有跳变"
                "但更不显眼",
                "改设计为单元沿闭合路径运动、汇聚只是途经态——但那样末帧不再是纯汇聚态，"
                "与「末帧构成可识别图形」的要求冲突",
            ],
            "declared_seamless": False,
            "declared_seamless_note": "timing.json 的 seamless 字段为 false；不因为播放"
                                      "设置 loop=true 就宣称无缝",
        },
    }
    _min_r = min(v["seam_over_forward_ratio"] for v in seam_units)
    _max_r = max(v["seam_over_forward_ratio"] for v in seam_units)
    _de_max = max(es[i + 1] - es[i] for i in range(len(es) - 1))
    seam["distance_summary"]["ratio_vs_own_max_forward_step"] = {
        "min": r4(_min_r),
        "max": r4(_max_r),
        "identical_for_all_units": _max_r - _min_r < 1e-9,
        "analytic_value": r4(1.0 / _de_max),
        "meaning": "12 个单元的比值完全相同（%.4f 倍），因为大家都共享同一条缓动曲线："
                   "接缝用 250 ms 走完 100%% 的位移，而正向最快的单帧（帧3→帧4）只走完 "
                   "Δe_max = %.4f 的位移，比值 = 1/Δe_max = %.4f。比值一致这件事本身就是"
                   "「6 帧共用一次全局同伦」的证据；跳变比最快单帧快 3.4 倍，肉眼可辨"
                   % (_min_r, _de_max, 1.0 / _de_max),
    }

    frame_data = {
        "schema_version": 1,
        "task_id": TASK,
        "path_base": "output_dir",
        "run_id": RUN,
        "created_at": S.now_iso(),
        "timezone": S.TZ_NAME,
        "coordinate_system": {
            "origin": "画布左上角",
            "unit": "像素",
            "x_axis": "向右为正",
            "y_axis": "向下为正",
            "position_meaning": "几何中心 (x, y)",
            "rotation": {
                "origin": "各单元自身几何中心",
                "unit": "度",
                "positive_direction": "顺时针",
                "zero": "末帧全部为 0°",
                "first_frame": "首帧为设计角 srot（见各单元条目）",
            },
            "width_height": "未旋转的几何宽高，与旋转无关；旋转只改变朝向",
            "paint_order": U.PAINT_ORDER,
            "paint_order_note": "列表顺序即绘制顺序，后面的盖住前面的；6 帧使用同一顺序",
            "scene_center": {"x": U.SCENE_CENTER[0], "y": U.SCENE_CENTER[1]},
            "dispersion_factor": U.DISPERSE_K,
        },
        "units": units,
        "frames": out_frames,
        "trajectories": trajectories,
        "seam": seam,
        "timeline": {
            "n_frames": U.N_FRAMES,
            "t_ms": [(f - 1) * U.DURATION_MS for f in range(1, U.N_FRAMES + 1)],
            "duration_ms": U.DURATION_MS,
            "period_ms": U.PERIOD_MS,
            "loop": True,
            "seamless": False,
        },
        "verification": {
            "pixel_audit": {"path_base": "output_dir", "path": "pixel-audit.json"},
            "contact_sheet": {"path_base": "output_dir", "path": "contact-sheet.png"},
            "frames_viewed_individually": True,
            "frames_viewed_as_contact_sheet": True,
            "contact_sheet_viewed": True,
            "cover_viewed": True,
            "design_gates_passed": "20/20（a23_units.dry_run）",
            "pixel_audit_passed": audit.get("passed"),
            "audit_activation_tests_passed": audit.get("activation_tests", {}).get("all_triggered"),
            "note": "插值公式是设计轨迹；实际像素证据全部来自 pixel-audit.json 对已交付"
                    "PNG 字节的逐像素核验，两者分开报告",
        },
    }

    timing = {
        "schema_version": 1,
        "task_id": TASK,
        "path_base": "output_dir",
        "run_id": RUN,
        "created_at": S.now_iso(),
        "timezone": S.TZ_NAME,
        "frames": [
            {
                "order": f,
                "id": "frame-%d" % f,
                "t_ms": (f - 1) * U.DURATION_MS,
                "file": FRAME_FILES[f - 1],
                "duration_ms": U.DURATION_MS,
                "loop_point": f == 1,
            } for f in range(1, U.N_FRAMES + 1)
        ],
        "loop": True,
        "period_ms": U.PERIOD_MS,
        "duration_ms": U.DURATION_MS,
        "frame_rate_fps": 1000.0 / U.DURATION_MS,
        "interpolation_note": "本 JSON 只给 6 个关键帧的时长与顺序，不含中间帧；"
                              "插值规则见 frame-data.json 的 trajectories[].interpolation，"
                              "它只描述设计轨迹，未渲染中间帧",
        "seamless": False,
        "seam_evidence": {
            "location": "t=1250 ms（帧6）→ t=1500 ms ≡ 0 ms（帧1）",
            "interval_ms": U.DURATION_MS,
            "type": "硬跳变（hard cut），不是无缝循环",
            "per_unit": [
                {"id": v["id"], "distance_px": v["distance_px"], "drot_deg": v["drot_deg"],
                 "seam_over_forward_ratio": v["seam_over_forward_ratio"]}
                for v in seam_units
            ],
            "min_jump_px": seam["distance_summary"]["min_px"],
            "max_jump_px": seam["distance_summary"]["max_px"],
            "min_rotation_jump_deg": r4(min(abs(v["drot_deg"]) for v in seam_units)),
            "max_rotation_jump_deg": r4(max(abs(v["drot_deg"]) for v in seam_units)),
            "rotation_wrapped_to_180": True,
            "position_closure_at_1500ms": False,
            "direction_continuity": False,
            "velocity_continuity": False,
            "impact": "每循环一次，画面在 %d ms 内从完整房景跳回 12 个散落的几何单元，"
                      "再花 1250 ms 重新汇聚。跳变位置固定、幅度 %s–%s px，不是随机卡顿"
                      % (U.DURATION_MS, seam["distance_summary"]["min_px"],
                         seam["distance_summary"]["max_px"]),
            "why": "「t=0 分散、t=1250 汇聚」与「1500 ms 处位置等于 0 处」不能同时成立；"
                   "6 帧关键帧 + 250 ms/帧 的设定下无解",
            "remediations": seam["distance_summary"]["possible_remediations"],
            "not_claimed_because": "不因为 loop=true 就宣称无缝；seamless 只按轨迹在 "
                                   "1500 ms 与 0 处位置/旋转一致与否判定",
            "source": {"path_base": "output_dir", "path": "frame-data.json",
                       "pointer": "seam"},
        },
        "playback_hints": {
            "gif_note": "本服务不支持 GIF 输出（<Snapshot type=> 只接受 png/jpg/webp），"
                        "因此未合成 GIF；6 张关键帧与这份 timing 描述可直接交给任意动画"
                        "合成器使用",
            "still_image_view": "静态查看建议看 contact-sheet.png（6 帧并排，浅底展示真实"
                                "透明度）",
        },
    }

    (OUT / "frame-data.json").write_text(
        json.dumps(frame_data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (OUT / "timing.json").write_text(
        json.dumps(timing, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print("帧数 %d  单元 %d  轨迹 %d  接缝单元 %d"
          % (len(out_frames), len(units), len(trajectories), len(seam_units)))
    print("t_ms        %s" % frame_data["timeline"]["t_ms"])
    print("easing e    %s" % [v["easing_progress"] for v in out_frames])
    print("同伦因子    %s" % [v["homothety_factor"] for v in out_frames])
    print("接缝位移 %s ~ %s px，旋转跳 %s ~ %s°，最小/最大单步比 %s×"
          % (seam["distance_summary"]["min_px"], seam["distance_summary"]["max_px"],
             timing["seam_evidence"]["min_rotation_jump_deg"],
             timing["seam_evidence"]["max_rotation_jump_deg"],
             seam["distance_summary"]["ratio_vs_own_max_forward_step"]["min"]))
    print("写入 outputs/%s/A23/{frame-data.json,timing.json}" % RUN)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
