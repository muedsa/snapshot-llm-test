"""A09 finaliser: geometry-audit.json + output copies + iteration/tool logs."""
from __future__ import annotations

import json
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared"))
from suite_common import task_out, append_jsonl_nobom, now  # noqa: E402

TASK_DIR = os.path.join(ROOT, "tasks", "A09-transform-atlas")
STAMP = json.load(open(os.path.join(TASK_DIR, "inputs", "stamp.json"), encoding="utf-8"))
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v2"

OPSEM = {
    "rotate_clockwise_deg": "A = [[cos t, -sin t], [sin t, cos t]]，t 为角度；像素 y 向下，因此这是图像方向的顺时针",
    "mirror_horizontal": "A = [[-1, 0], [0, 1]]，关于过枢轴的竖轴左右镜像",
    "mirror_vertical": "A = [[1, 0], [0, -1]]，关于过枢轴的横轴上下镜像",
    "scale_uniform": "A = s·I",
    "scale_xy": "A = diag(sx, sy)",
}


def main() -> None:
    geo = json.load(open(os.path.join(HERE, f"geometry-data.{VERSION}.json"), encoding="utf-8"))
    chk = json.load(open(os.path.join(HERE, f"pixel-check.{VERSION}.json"), encoding="utf-8"))
    chk_by_id = {c["id"]: c for c in chk["cells"]}
    flat = json.load(open(os.path.join(TASK_DIR, "inputs", "transforms.json"), encoding="utf-8"))
    ops_by_id = {t["id"]: t["operations"] for t in flat}

    out = {
        "task": "A09",
        "image": "transform-atlas.png",
        "canvas": geo["canvas"],
        "grid": geo["grid"],
        "stamp": {"size": geo["stamp_size"], "pivot": geo["pivot"],
                  "rectangles": STAMP["rectangles"], "dot": STAMP["dot"]},
        "matrix_convention": {
            "order": "column-major",
            "flat_order": "(a,b,0,0,c,d,0,0,0,0,1,0,tx,ty,0,1)",
            "meaning": "local x 轴映射到画布向量 (a,b)，local y 轴映射到 (c,d)，平移为 (tx,ty)；"
                       "画布点 = A·u + t，A = [[a, c], [b, d]]",
            "composition": "操作按 transforms.json 列表顺序依次作用，每步围绕本地枢轴 (60,60)："
                           "A = A_n·…·A_1，t = 格中心 − A·(60,60)。枢轴因此是复合变换的不动点，"
                           "必然落在格的几何中心 (ox+150, oy+125)。",
            "operation_semantics": OPSEM,
            "shape_source": "四枚图元的宽高与本地坐标逐字取自 inputs/stamp.json，"
                            "未在任何地方按最终位置手改形状坐标；一个 Transform 承载整格复合矩阵。",
        },
        "cells": [],
        "verification": {
            "requirement": "±1.5 像素的视觉/像素核对（反走样边缘例外）",
            "tolerance_px": chk["tolerance_px"],
            "method": [
                "1) 预测栅格：按 A、t 把 stamp 的四枚图元在 4×超采样网格上分类（叠加顺序 R1、R2、R3、圆点，"
                "后画者覆盖先画者），降采样得到每像素的预测类别（背景/红/蓝/黄/圆点）。",
                "2) 类别一致性：预测为某图元颜色的像素必须真的是该 RGB；预测为卡片背景的像素不得出现任何"
                "图元颜色。例外只有反走样带——与预测类别边界相距 ≤1.5px 的像素（3×3 邻域内存在类别变化）。",
                "3) 亚像素边缘：对每一对相邻的“图元像素 / 纯白卡片像素”，用两像素的颜色覆盖率反解真实边缘"
                "位置（像素中心位于 index+0.5，覆盖率线性模型 s = 0.5 + α_q），与预测模型给出的穿越位置比较，"
                "偏差必须 ≤1.5px。",
                "核对区域：每格卡片内部 x∈[ox+2, ox+298]、y∈[oy+42, oy+208]，已避开标题、脚注、圆角与刻度。",
            ],
            "pixels_checked": chk["pixels_checked"],
            "mismatch_pixels_outside_band": chk["mismatch_pixels_outside_band"],
            "subpixel_edge_pairs": chk["subpixel_edge_pairs"],
            "subpixel_max_delta_px": chk["subpixel_max_delta_px"],
            "exceptions": "反走样边缘（预测类别边界 ±1.5px 内）不参与颜色一致性判定；"
                          "纯白判定阈值为每通道 ≤6，因此 25px 淡格线/十字线不进入亚像素样本。",
            "verdict": chk["verdict"],
        },
    }
    for c in geo["cells"]:
        r = chk_by_id[c["id"]]
        m = c["matrix_16"]
        out["cells"].append({
            "id": c["id"],
            "index": c["index"], "col": c["col"], "row": c["row"],
            "operations": ops_by_id[c["id"]],
            "short_name": c["short_name"],
            "cell_origin": c["origin"], "cell_size": [300, 250],
            "cell_center": c["center"],
            "matrix_column_major_16": m,
            "matrix_2x2": [[m[0], m[4]], [m[1], m[5]]],
            "translation": [m[12], m[13]],
            "pivot_canvas": c["center"],
            "scale_xy": [float(np.hypot(m[0], m[1])), float(np.hypot(m[4], m[5]))],
            "determinant": float(m[0] * m[5] - m[4] * m[1]),
            "rectangles": [{"index": r2["index"], "color": r2["color"], "local_xywh": r2["xywh"],
                            "corners_canvas": [[round(v, 3) for v in p] for p in r2["corners"]]}
                           for r2 in c["rects"]],
            "dot": {"color": STAMP["dot"]["color"], "local_center": c["dot"]["source_center"],
                    "local_radius": c["dot"]["source_radius"],
                    "center_canvas": [round(v, 3) for v in c["dot"]["center"]],
                    "ellipse_semi_axes": [round(v, 3) for v in c["dot"]["radius_xy"]]},
            "transformed_bbox": [round(v, 3) for v in c["bbox"]],
            "transformed_bbox_size": [round(v, 3) for v in c["bbox_size"]],
            "pixel_check": {
                "pixels_checked": r["pixels_checked"],
                "antialias_band_pixels": r["band_pixels"],
                "mismatch_pixels_outside_band": r["mismatch_pixels_outside_band"],
                "subpixel_edge_pairs": r["subpixel_edge_pairs"],
                "subpixel_max_delta_px": r["subpixel_max_delta_px"],
                "subpixel_mean_delta_px": r["subpixel_mean_delta_px"],
            },
        })
    # T07 / T08 order evidence
    t07 = next(c for c in out["cells"] if c["id"] == "T07")
    t08 = next(c for c in out["cells"] if c["id"] == "T08")
    a7 = np.array(t07["matrix_2x2"])
    a8 = np.array(t08["matrix_2x2"])
    out["order_evidence_T07_T08"] = {
        "claim": "两格操作顺序相反，复合矩阵不同：A(T08) = −A(T07)，因此两枚标本互为 180° 旋转",
        "A_T07": a7.tolist(), "A_T08": a8.tolist(),
        "A_T08_plus_A_T07_is_zero": bool(np.allclose(a8, -a7)),
        "dot_center_T07": t07["dot"]["center_canvas"], "dot_center_T08": t08["dot"]["center_canvas"],
        "pixel_check_both_zero_outside_band":
            t07["pixel_check"]["mismatch_pixels_outside_band"] == 0
            and t08["pixel_check"]["mismatch_pixels_outside_band"] == 0,
    }
    od = task_out("A09")
    with open(os.path.join(od, "geometry-audit.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    shutil.copyfile(os.path.join(HERE, f"transform-atlas.{VERSION}.png"),
                    os.path.join(od, "transform-atlas.png"))
    shutil.copyfile(os.path.join(HERE, f"transform-atlas.{VERSION}.snapshot"),
                    os.path.join(od, "transform-atlas.snapshot"))
    print("wrote geometry-audit.json and final png/snapshot",
          json.dumps(out["verification"], ensure_ascii=False)[:200])


if __name__ == "__main__":
    main()
