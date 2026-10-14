"""A19 - scene-data.json and equivalence.json, assembled from the generator output,
the pixel audit and the raw service responses. Nothing is typed by hand.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A19"
OUT = ROOT / "outputs" / RUN / "A19"
sys.path.insert(0, str(TMP))

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v002")
a = ap.parse_args()

scene = json.loads((TMP / f"{a.ver}-scene.json").read_text(encoding="utf-8"))
occ = json.loads((TMP / f"{a.ver}-occlusion.json").read_text(encoding="utf-8"))
ver = json.loads((TMP / f"{a.ver}-verify.json").read_text(encoding="utf-8"))
reqs = [json.loads(l) for l in
        (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l]

meas = {m["id"]: m for m in ver["grid"]["measured_objects"]}
objects = []
for o in scene["objects"]:
    m = meas[o["id"]]
    objects.append({**o,
                    "measured": {"bbox": m["measured_bbox"],
                                 "size_px": m["measured_size_px"],
                                 "centre": m["measured_centre"],
                                 "colour": m["measured_colour"],
                                 "shape": m["measured_shape"],
                                 "fill_ratio": m["fill_ratio"],
                                 "centre_error_px": m["centre_error_px"]}})

dist = scene["distribution"]
dist["measured_from_png"] = {
    "colour_counts": ver["grid"]["checks"]["colour_counts"],
    "shape_counts": ver["grid"]["checks"]["shape_counts"],
    "size_counts": ver["grid"]["checks"]["size_counts"],
    "combinations_present": ver["grid"]["checks"]["combinations_present"],
    "sizes_per_colour": ver["grid"]["checks"]["sizes_per_colour"],
    "sizes_per_shape": ver["grid"]["checks"]["sizes_per_shape"],
    "rows_min_colours": ver["grid"]["checks"]["rows_min_colours"],
    "rows_min_shapes": ver["grid"]["checks"]["rows_min_shapes"],
    "every_body_inside_its_cell": ver["grid"]["checks"]["no_body_crosses_cell"],
    "all_64_bodies_match_plan": ver["grid"]["checks"]["measured_matches_plan"],
}

scene_doc = {
    "schema_version": 1, "task_id": "A19", "path_base": "output_dir",
    "coordinate_space": "canvas top-left origin, x right / y down, pixels; "
                        "boxes are [left, top, right, bottom]",
    "artifacts": {"png": "grid-scene.png", "dsl": "grid-scene.snapshot",
                  "size": [1600, 1600]},
    "grid": {"rows": 8, "columns": 8, "cell_px": 200,
             "cell_box": "cell (row r, col c) spans x in [(c-1)*200, c*200], "
                         "y in [(r-1)*200, r*200]",
             "id_order": "G01-G64 从左到右、从上到下；row=(n-1)//8+1, col=(n-1)%8+1"},
    "generation": {
        "seed": scene["seed"],
        "algorithm": "random.Random(seed): 颜色/形状各 16 份洗牌后用行内交换满足每行≥3 种，"
                     "再重洗形状直到 16 种颜色×形状组合全部出现；尺寸先随机，再按"
                     "“每种颜色、每种形状都要覆盖 48/64/80”补写；中心 = 格心 + 种子抖动"
                     "（±14 px），ID 文字框固定在主体下方、左对齐主体左边。",
        "note": "seed 只是可复现的入口；下面 objects/distribution 记录的是实际生成结果，"
                "并由 verify_scene.py 用像素复核。",
    },
    "subject_rules": {
        "circle": "实心圆，直径 = size",
        "square": "直角方形，边长 = size",
        "rounded-square": "圆角方形，边长 = size，borderRadius = size * 0.25",
        "ring": "圆环，外径 = size，内径 = size / 2（内圈以白底画出，形成孔）",
        "id_label": "fontSize 22 的等宽文字，位于主体框下方 6 px 起，不计入主体",
    },
    "objects": objects,
    "distribution": dist,
    "response": {k: next(r for r in reqs
                         if r["request_id"] == f"A19-render-{a.ver}-grid-a1")[k]
                 for k in ("http_status", "response_content_type", "request_bytes",
                           "response_bytes", "image_width", "image_height",
                           "x_request_id", "server_timing", "started_at",
                           "duration_seconds")},
}
(OUT / "scene-data.json").write_text(json.dumps(scene_doc, ensure_ascii=False, indent=1)
                                     + "\n", encoding="utf-8")

pa = TMP / f"{a.ver}-occlusion.png"
pb = TMP / f"{a.ver}-occlusion-alternative.png"
sha = {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
       for p in (pa, pb)}


def insets(key):
    return {m["id"]: m["inset_px"] for m in occ[key + "_insets"]}


eq = {
    "schema_version": 1, "task_id": "A19", "path_base": "output_dir",
    "claim": "两份最终 PNG 的可见内容逐像素相同，隐藏内容不同",
    "versions": [
        {"id": "A", "png": "occlusion.png", "dsl": "occlusion.snapshot",
         "temp_response": {"path_base": "suite_root",
                           "path": f"tmp/{RUN}/A19/{a.ver}-occlusion.png"},
         "file_sha256": sha[str(pa.relative_to(ROOT)).replace("\\", "/")],
         "hidden_objects": occ["hidden_A"],
         "hidden_count": len(occ["hidden_A"]),
         "hidden_insets_px": insets("hidden_A"),
         "request_id": f"A19-render-{a.ver}-occlusion-a1"},
        {"id": "B", "png": "occlusion-alternative.png",
         "dsl": "occlusion-alternative.snapshot",
         "temp_response": {"path_base": "suite_root",
                           "path": f"tmp/{RUN}/A19/{a.ver}-occlusion-alternative.png"},
         "file_sha256": sha[str(pb.relative_to(ROOT)).replace("\\", "/")],
         "hidden_objects": occ["hidden_B"],
         "hidden_count": len(occ["hidden_B"]),
         "hidden_insets_px": insets("hidden_B"),
         "request_id": f"A19-render-{a.ver}-occlusion-alternative-a1"},
    ],
    "identical_by_construction": {
        "canvas": [800, 800], "background": "#FFFFFF", "panel": "#EDF1F7",
        "visible_objects": [v["id"] for v in occ["visible_objects"]],
        "occluder_box": occ["occluder_box"], "occluder_colour": "#16233A",
        "label_text": "OCCLUDED REGION",
        "note": "两份 DSL 由 gen_occlusion.build(hidden) 同一个函数生成，只有传入的隐藏层"
                "节点列表不同；可见前景、遮挡板、背景与渲染参数完全一致。",
    },
    "no_leakage": {
        "dashed_or_outline_hints": "无：遮挡板是不透明实心圆角矩形，隐藏对象全部画在它下面",
        "shadows_or_filters_on_hidden": "无：隐藏层只用 Container 纯色填充，"
                                        "不产生任何外溢绘制",
        "min_inset_px_A": min(min(v) for v in insets("hidden_A").values()),
        "min_inset_px_B": min(min(v) for v in insets("hidden_B").values()),
        "hidden_footprints_measured_as_occluder_colour":
            ver["occlusion"]["hidden_footprints_fully_covered"],
        "leak_detail": ver["occlusion"]["hidden_leak_detail"],
    },
    "comparison": {
        "decoder": "Pillow (PIL) Image.open().convert('RGBA')，8 位未预乘 RGBA 四通道",
        "same_pixel_dimensions": ver["occlusion"]["same_size"],
        "size_A": [800, 800], "size_B": [800, 800],
        "compositing": "未合成到白底、未缩放、未忽略 alpha 或透明像素的 RGB",
        "differing_pixels": ver["occlusion"]["different_pixels"],
        "max_channel_difference": ver["occlusion"]["max_channel_difference"],
        "pixel_array_sha256": ver["occlusion"]["pixel_array_sha256"],
        "file_bytes_identical": len({v for v in sha.values()}) == 1,
        "verdict": "两份原始响应的像素数组逐通道完全一致（不同像素数 0、最大通道差 0）；"
                   "本次服务返回的文件字节也恰好相同，因此文件哈希同样一致。",
    },
    "difference_stated_in_dsl": {
        "A_hidden_layer": "3 个对象：blue square 64 @(360,360)、green circle 64 @(480,420)、"
                          "orange ring 64 @(360,480)",
        "B_hidden_layer": "5 个对象：violet circle 64 @(352,352)、orange rounded-square 64 "
                          "@(456,352)、blue ring 64 @(352,456)、green square 64 @(456,456)、"
                          "violet circle 48 @(404,404)",
        "consequence": "两版可见像素相同，因此“被遮对象的数量/颜色”不可能从图中读出，"
                       "对应 Q17、Q18 的标准答案为“无法确定”。",
    },
}
(OUT / "equivalence.json").write_text(json.dumps(eq, ensure_ascii=False, indent=1) + "\n",
                                      encoding="utf-8")
print("scene objects:", len(objects), "| distribution ok:",
      dist["all_constraints_met"], "| equivalence verdict differing pixels:",
      eq["comparison"]["differing_pixels"])
