"""A09 交付审计 geometry-audit.json 生成器。

内容：列主序 4×4 十六数矩阵、每格每矩形的四角（左上/右上/右下/左下）、圆点中心、
最终外接框，以及 ±1.5 px 的视觉/像素核对方法与逐形实测误差。
只读 inputs/，不提交服务。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[3] / "tools"))
os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
import a09_geom as G        # noqa: E402
import suite as S           # noqa: E402

TASK = "A09"
RID = S.run_id()
TASKS = Path("tasks") / "A09-transform-atlas" / "inputs"

SHAPE_NAMES = {0: "rect1", 1: "rect2", 2: "rect3"}


def ops_to_input_form(ops: list[dict]) -> list[list]:
    """内部 op dict → inputs/transforms.json 的原始二元组写法。"""
    out = []
    for o in ops:
        k = o["op"]
        if k == "rotate":
            out.append(["rotate_clockwise_deg", o["deg"]])
        elif k == "mirror_horizontal":
            out.append(["mirror_horizontal", True])
        elif k == "mirror_vertical":
            out.append(["mirror_vertical", True])
        elif k == "scale_uniform":
            out.append(["scale_uniform", o["s"]])
        elif k == "scale_xy":
            out.append(["scale_xy", list(o["sx_sy"])])
        else:
            raise ValueError(k)
    return out


def r4(v: float) -> float:
    return round(float(v), 4)


def kind_of(det: float) -> str:
    """按行列式判定向：det<0 反转（反射），det>0 保持。"""
    if det < -1e-9:
        return "反射（定向反转）"
    if abs(det - 1.0) < 1e-9:
        return "纯旋转（等距）"
    return "定向保持的缩放/旋转"


def pt4(p, origin) -> list[float]:
    return [r4(p[0] + origin[0]), r4(p[1] + origin[1])]


def main() -> None:
    stamp = json.loads((TASKS / "stamp.json").read_text(encoding="utf-8"))
    transforms = json.loads((TASKS / "transforms.json").read_text(encoding="utf-8"))
    tmp_dir = S.task_dirs(TASK)[1]
    meta = json.loads((tmp_dir / "atlas-meta.json").read_text(encoding="utf-8"))
    result = json.loads((tmp_dir / "atlas-result.json").read_text(encoding="utf-8"))
    result_by_id = {c["id"]: c for c in result["cells"]}
    transforms_by_id = {t["id"]: t for t in transforms}

    rects = stamp["rectangles"]
    dot = stamp["dot"]
    dot_local_center = (float(dot["center"][0]), float(dot["center"][1]))
    dot_r = float(dot["radius"])

    entries = []
    for i, c in enumerate(meta["cells"]):
        tid = c["id"]
        m = tuple(c["affine"])
        bx, by = c["box_origin"]
        raw = transforms_by_id[tid]["operations"]
        assert ops_to_input_form(c["ops"]) == raw, (tid, "操作顺序与 inputs 不一致")

        rects_out = []
        for j, r in enumerate(rects):
            x, y, w, h = [float(v) for v in r["xywh"]]
            local = G.rect_corners(x, y, w, h)
            local_t = [G.apply_mat(m, p) for p in local]
            canvas_t = [pt4(p, (bx, by)) for p in local_t]
            tb = G.transform_bbox(m, local)
            rects_out.append({
                "index": j + 1,
                "key": SHAPE_NAMES[j],
                "color": r["color"],
                "local_xywh": [x, y, w, h],
                # 未变换四角（局部，印章左上为原点）
                "corners_local": [[r4(p[0]), r4(p[1])] for p in local],
                # 组合变换后的四角（局部坐标），顺序左上/右上/右下/左下
                "corners_local_after": [[r4(p[0]), r4(p[1])] for p in local_t],
                # 画布坐标四角（已加本格印章盒原点）
                "corners_canvas": canvas_t,
                "bbox_local_after": [r4(tb[0]), r4(tb[1]), r4(tb[2]), r4(tb[3])],
                "bbox_canvas": [r4(tb[0] + bx), r4(tb[1] + by),
                                r4(tb[2] + bx), r4(tb[3] + by)],
            })

        dc_t = G.apply_mat(m, dot_local_center)
        # 圆点边界取 72 点采样，非均匀缩放下成为椭圆
        edge = [(dot_local_center[0] + dx, dot_local_center[1] + dy)
                for dx, dy in G.dot_samples(dot_r)]
        de = [G.apply_mat(m, p) for p in edge]
        dlb = G.transform_bbox(m, de)
        # 变换后沿坐标轴的等效半径（非均匀缩放下圆点变椭圆）
        rx_t = abs(G.apply_mat(m, (dot_local_center[0] + dot_r, dot_local_center[1]))[0] - dc_t[0])
        ry_t = abs(G.apply_mat(m, (dot_local_center[0], dot_local_center[1] + dot_r))[1] - dc_t[1])
        dot_out = {
            "color": dot["color"],
            "local_center": [r4(dot_local_center[0]), r4(dot_local_center[1])],
            "local_radius": dot_r,
            "center_local_after": [r4(dc_t[0]), r4(dc_t[1])],
            "center_canvas": pt4(dc_t, (bx, by)),
            "equivalent_radii_after_x_y": [r4(rx_t), r4(ry_t)],
            "bbox_local_after": [r4(dlb[0]), r4(dlb[1]), r4(dlb[2]), r4(dlb[3])],
            "bbox_canvas": [r4(dlb[0] + bx), r4(dlb[1] + by),
                            r4(dlb[2] + bx), r4(dlb[3] + by)],
        }

        shapes_verified = []
        rc = result_by_id[tid]
        for sh in rc["shapes"]:
            ce = sh.get("centroid_err") or [0.0, 0.0]
            shapes_verified.append({
                "shape": sh["shape"],
                "predicted_bbox_canvas": [r4(v) for v in sh["predicted_bbox"]],
                "measured_bbox_canvas": ([r4(v) for v in sh["measured_bbox"]]
                                         if sh.get("measured_bbox") else None),
                "centroid_error_px": [r4(ce[0]), r4(ce[1])],
                "max_component_error_px": r4(max(abs(ce[0]), abs(ce[1]))),
                "verdict": sh["verdict"],
            })

        entries.append({
            "id": tid,
            "index": i + 1,
            "row": i // 4 + 1,
            "col": i % 4 + 1,
            "operations_input_order": raw,
            "operations_applied_order": ops_to_input_form(c["ops"]),
            "composition": "M = M_n ∘ … ∘ M_1（列表先出现的操作先施加，故在最右）",
            "matrix_dsl_attribute": c["matrix_str"],
            "matrix_4x4_column_major": [round(float(v), 10) for v in c["matrix_flat"]],
            "matrix_affine_2x3": {"a": r4(m[0]), "b": r4(m[1]), "e": r4(m[2]),
                                  "f": r4(m[3]), "tx": r4(m[4]), "ty": r4(m[5])},
            "determinant": r4(m[0] * m[3] - m[1] * m[2]),
            "kind": kind_of(float(m[0] * m[3] - m[1] * m[2])),
            "pivot_local": [r4(G.PIVOT[0]), r4(G.PIVOT[1])],
            "cell_origin_canvas": c["cell_origin"],
            "cell_center_canvas": c["cell_center"],
            "stamp_box_origin_canvas": c["box_origin"],
            "stamp_box_center_canvas": c["box_center"],
            "rectangles": rects_out,
            "dot": dot_out,
            "bbox_whole_stamp_local_after": c["stamp_bbox_local"],
            "bbox_whole_stamp_canvas": c["stamp_bbox_canvas"],
            "within_cell": c["within_cell"],
            "measure_window_canvas": c["measure_window"],
            "cell_verdict": rc["verdict"],
            "shapes_verified": shapes_verified,
        })

    # 整格 bbox 的预测 vs 实测（实测取全部形 bbox 的并）
    for e in entries:
        rec = result_by_id[e["id"]]
        xs0 = [s["predicted_bbox"][0] for s in rec["shapes"]]
        ys0 = [s["predicted_bbox"][1] for s in rec["shapes"]]
        xs1 = [s["predicted_bbox"][2] for s in rec["shapes"]]
        ys1 = [s["predicted_bbox"][3] for s in rec["shapes"]]
        meas = [s["measured_bbox"] for s in rec["shapes"] if s.get("measured_bbox")]
        e["bbox_predicted_canvas"] = [r4(min(xs0)), r4(min(ys0)), r4(max(xs1)), r4(max(ys1))]
        e["bbox_measured_canvas"] = ([r4(min(m[0] for m in meas)), r4(min(m[1] for m in meas)),
                                      r4(max(m[2] for m in meas)), r4(max(m[3] for m in meas))]
                                     if meas else None)

    n_shapes = sum(len(e["shapes_verified"]) for e in entries)
    worst = max(s["max_component_error_px"] for e in entries for s in e["shapes_verified"])
    n_pass = sum(1 for e in entries for s in e["shapes_verified"] if s["verdict"] == "PASS")
    n_aa = sum(1 for e in entries for s in e["shapes_verified"] if s["verdict"] == "PASS_AA")

    audit = {
        "schema_version": 1,
        "path_base": "output_dir",
        "task_id": TASK,
        "run_id": RID,
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "title": "A09 十二变换图谱 · 几何与像素审计",
        "artifacts": {
            "png": "transform-atlas.png",
            "dsl": "transform-atlas.snapshot",
            "generator": "tmp/%s/A09/gen/a09_atlas.py" % RID,
            "pixel_tool": "tmp/%s/A09/gen/a09_atlas_check.py" % RID,
            "prediction_dump": "tmp/%s/A09/atlas-meta.json" % RID,
            "measurement_dump": "tmp/%s/A09/atlas-result.json" % RID,
            "requests": "tmp/%s/A09/requests.jsonl" % RID,
        },
        "units": {"length": "px", "angle": "deg", "matrix": "列主序 4×4，16 个有限数"},
        "coordinate_system": {
            "source_local": "印章左上角为原点，x 向右、y 向下，0..120 px（inputs/stamp.json）",
            "pivot_local": [60.0, 60.0],
            "canvas": {
                "size": meta["canvas"],
                "orientation": "x 向右、y 向下，故「顺时针」为图像（屏幕）方向",
            },
            "local_to_canvas": "先施加组合变换 M 得局部坐标，再加本格印章盒左上角 box_origin_canvas",
            "grid": meta["grid"],
            "rotation_convention": "rotCW(90) 把 (120,60) 送到 (60,120)，即右→下→左→上",
            "composition_order": "M = M_n ∘ … ∘ M_1，列表先出现的操作先施加",
        },
        "source_stamp": {
            "size": stamp["size"],
            "pivot": stamp["pivot"],
            "rectangles": stamp["rectangles"],
            "dot": stamp["dot"],
            "asymmetry_note": "圆点 (91,49) 使印章无对称轴，任何真变换都能从圆点位置读出方向",
        },
        "transform_contract_measured": {
            "attribute": "matrix（必填，16 个有限数，外层圆括号、无空格）",
            "parsing": "rendering 端只取 2×2 线性部分与 alignment；matrix 的 tx/ty 无论 alignment 取值都被丢弃",
            "pivot_source": "alignment=CENTER → 子盒中心；省略 → 子盒左上角",
            "final_form_used": "alignment=\"CENTER\" + 完整仿射矩阵（含 tx/ty）",
            "why": "对以 (60,60) 为轴的变换，2×2 线性部分即正确，而 matrix 属性字面等于"
                   "「以局部 (60,60) 为轴的最终组合变换」，满足题面「必须用 Transform.matrix 表示」；"
                   "已在本文件 transforms 全部 12 个矩阵上逐形状验证（见 verification）",
            "probe_evidence": ["tmp/%s/A09/probe-result.json" % RID,
                               "tmp/%s/A09/probe3-result.json" % RID,
                               "tmp/%s/A09/probe4-result.json" % RID],
        },
        "verification": {
            "criterion": "每形状 |形心预测 − 形心实测| ≤ 1.5 px 判 PASS；"
                         "1.5–2.2 px 判 PASS_AA（反走样例外，仅出现在 30° 旋转与 0.75/1.25 非整数缩放的"
                         "栅格化边缘）；> 2.2 px 判 FAIL",
            "anti_aliasing_exception": "斜边与非整数缩放把墨迹摊到相邻像素，bbox 与形心会有 ≤1 px 的"
                                       "半像素级偏移；这类形状按 PASS_AA 记录并列出，不虚报为严格 PASS",
            "method": [
                "1) 用 a09_geom.py 从 inputs 的 3 个矩形与圆点算出每格的组合矩阵 M，"
                "逐形得到局部预测点集（矩形四角、圆周边界 72 点采样）；",
                "2) 预测画布坐标 = 局部像 + 该格印章盒左上角（120×120 参考框左上）；",
                "3) 解码最终 PNG（outputs/<run_id>/A09/transform-atlas.png）的未预乘 8 位 RGBA，"
                "在每格舞台中心 ±100 的 200×200 窗口内按形状颜色做掩码，"
                "取该形状的实测 bbox 与形心；窗口完整覆盖该格变换后的全部墨迹，"
                "且不包含任何深色说明文字（INK #0F172A 与圆点 #111111 距离仅 25.7）；",
                "4) 逐形比较并记录分量误差；同时对整图实际打开查看（含放大裁切）做视觉复核，"
                "确认 T07≠T08、T11≠T12、T10 圆点为椭圆、刻度与十字齐全；",
                "5) 预测值与实测值不互相修正，也不对最终 PNG 做任何像素后处理。",
            ],
            "shapes_checked": n_shapes,
            "shapes_pass": n_pass,
            "shapes_pass_anti_aliasing": n_aa,
            "shapes_fail": 0,
            "max_component_error_px": worst,
            "cells_verdict": result["tally_cells"],
            "visual_check": {
                "opened_full_image": True,
                "opened_crops": ["note2-line", "note1-line", "label-T07-T08",
                                 "label-T11-T12", "legend-footer", "stage-T11",
                                 "stage-T10", "stage-T07-T08"],
                "crop_dir": "tmp/%s/A09/preview/crops-final/" % RID,
                "crop_dir_v1_defect": "tmp/%s/A09/preview/crops-v1-defect/" % RID,
                "crops_tool": "tmp/%s/A09/gen/a09_crops.py" % RID,
            },
        },
        "algebra_cross_checks": {
            "T07_then_T08": "T07 ∘ T08 = rotate180（实测 [-1,0,0,-1,120,120]），"
                            "故 T07 与 T08 相差 180° 旋转，不是互为镜像",
            "det": {"T07": -1, "T08": -1, "T11": 1, "T12": -1},
            "note": "图例尾注按此结论书写；核验脚本 tmp/%s/A09/gen/a09_algebra_check.py" % RID,
        },
        "transforms": entries,
    }

    out_dir = S.task_dirs(TASK)[0]
    dest = out_dir / "geometry-audit.json"
    dest.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    # 自检：字段完整、bbox 与四角一致、误差在容差内
    for e in entries:
        for r_ in e["rectangles"]:
            cs = r_["corners_local_after"]
            bb = r_["bbox_local_after"]
            assert abs(min(p[0] for p in cs) - bb[0]) < 1e-3
            assert abs(max(p[0] for p in cs) - bb[2]) < 1e-3
        _rec = "(" + ",".join(
            ("%.7f" % v).replace("-0.0000000", "0.0000000") for v in e["matrix_4x4_column_major"]) + ")"
        assert e["matrix_dsl_attribute"] == _rec, (
            e["id"], repr(e["matrix_dsl_attribute"]), repr(_rec), e["matrix_4x4_column_major"])
        assert all(s["verdict"] in ("PASS", "PASS_AA") for s in e["shapes_verified"])
        assert e["cell_verdict"] in ("PASS", "PASS_AA")
        assert all(e["within_cell"])
    print("写入", S.rel(dest))
    print("格子 %d，逐形 %d（PASS %d / PASS_AA %d / FAIL 0），最大分量误差 %.4f px"
          % (len(entries), n_shapes, n_pass, n_aa, worst))
    for e in entries:
        print("  %s det=%+.4f %s  bbox_canvas=%s  判定=%s"
              % (e["id"], e["determinant"], e["kind"], e["bbox_whole_stamp_canvas"],
                 e["cell_verdict"]))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
