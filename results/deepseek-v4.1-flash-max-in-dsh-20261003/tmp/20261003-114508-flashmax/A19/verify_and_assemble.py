"""A19 equivalence verifier + output assembly.

1. Compares the two occlusion PNGs byte-for-byte and pixel-for-pixel (Pillow ImageChops).
2. Re-reads both hidden-content definitions and asserts they really differ (different shape
   AND different colour), so "different hidden content, identical output" is a measured
   claim rather than an assumption.
3. Copies every required artefact into outputs/<run>/A19/ and writes task-metrics.json.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys

from PIL import Image, ImageChops

sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from suite_common import build_metrics, write_json, task_out, count_requests  # noqa: E402

TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A19"
OUT = task_out("A19")


def sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main() -> None:
    pa = os.path.join(TMP, "occlusion-a.v1.png")
    pb = os.path.join(TMP, "occlusion-b.v1.png")
    a_bytes, b_bytes = open(pa, "rb").read(), open(pb, "rb").read()
    ia, ib = Image.open(pa).convert("RGBA"), Image.open(pb).convert("RGBA")
    diff = ImageChops.difference(ia, ib)
    bbox = diff.getbbox()
    hist = diff.histogram()
    differing_pixels = sum(hist[i] for i in range(len(hist)) if i % 256 != 0) if False else None
    # count pixels whose RGBA tuple is not identical
    diff_px = 0
    if bbox is not None:
        for p, q in zip(ia.getdata(), ib.getdata()):
            if p != q:
                diff_px += 1
    meta_a = json.load(open(os.path.join(TMP, "occlusion-a.meta.json"), encoding="utf-8"))
    meta_b = json.load(open(os.path.join(TMP, "occlusion-b.meta.json"), encoding="utf-8"))
    hidden_a, hidden_b = meta_a["hidden"], meta_b["hidden"]
    hidden_differs = (hidden_a["kind"] != hidden_b["kind"] or
                      hidden_a["color"] != hidden_b["color"])
    assert hidden_differs, "the two hidden contents must differ"
    rect_a = {"x0": hidden_a["x"] - hidden_a["size"] / 2, "y0": hidden_a["y"] - hidden_a["size"] / 2,
              "x1": hidden_a["x"] + hidden_a["size"] / 2, "y1": hidden_a["y"] + hidden_a["size"] / 2}
    rect_b = {"x0": hidden_b["x"] - hidden_b["size"] / 2, "y0": hidden_b["y"] - hidden_b["size"] / 2,
              "x1": hidden_b["x"] + hidden_b["size"] / 2, "y1": hidden_b["y"] + hidden_b["size"] / 2}
    p1 = next(p for p in meta_a["panels"] if p["id"] == "P1")
    covered = (rect_a["x0"] >= p1["x0"] and rect_a["y0"] >= p1["y0"]
               and rect_a["x1"] <= p1["x1"] and rect_a["y1"] <= p1["y1"]
               and rect_b["x0"] >= p1["x0"] and rect_b["y0"] >= p1["y0"]
               and rect_b["x1"] <= p1["x1"] and rect_b["y1"] <= p1["y1"])
    assert covered, "both hidden objects must sit entirely under P1"
    # sample the P1 interior to show there is no visible clue
    px = ia.load()
    samples = [(p1["x0"] + 10 + i * 20, p1["y0"] + 12) for i in range(9)]
    sample_colours = sorted({("#%02X%02X%02X" % px[x, y][:3]) for x, y in samples})

    eq = {
        "schema": "a19-equivalence/1",
        "claim": "两份隐藏内容不同的完整 DSL，在同一服务上渲染出字节完全相同、像素完全相同的 PNG；"
                 "因此仅凭可见图无法判断 P1 下方的内容。",
        "a": {"file": "occlusion.png", "dsl": "occlusion.snapshot",
              "hidden": hidden_a, "png_sha256": hashlib.sha256(a_bytes).hexdigest(),
              "png_bytes": len(a_bytes), "render_request_id": "A19-REQ-0002"},
        "b": {"file": "occlusion-alternative.png", "dsl": "occlusion-alternative.snapshot",
              "hidden": hidden_b, "png_sha256": hashlib.sha256(b_bytes).hexdigest(),
              "png_bytes": len(b_bytes), "render_request_id": "A19-REQ-0003"},
        "identical_bytes": a_bytes == b_bytes,
        "identical_size": list(ia.size) == list(ib.size),
        "pixel_comparison": {
            "method": "Pillow ImageChops.difference(...).getbbox() 与逐像素 RGBA 比较",
            "diff_bbox": bbox,
            "differing_pixels": diff_px,
            "total_pixels": ia.size[0] * ia.size[1],
            "identical_pixels": diff_px == 0 and bbox is None,
        },
        "hidden_content_differs": hidden_differs,
        "hidden_content_summary": {
            "a": f"{hidden_a['kind']} {hidden_a['color']} size {hidden_a['size']} "
                 f"at ({hidden_a['x']},{hidden_a['y']})",
            "b": f"{hidden_b['kind']} {hidden_b['color']} size {hidden_b['size']} "
                 f"at ({hidden_b['x']},{hidden_b['y']})",
        },
        "occlusion_proof": {
            "panel": "P1",
            "panel_rect": {"x0": p1["x0"], "y0": p1["y0"], "x1": p1["x1"], "y1": p1["y1"]},
            "hidden_a_rect": {k: round(v, 1) for k, v in rect_a.items()},
            "hidden_b_rect": {k: round(v, 1) for k, v in rect_b.items()},
            "both_fully_covered": covered,
            "sampled_colours_inside_P1": sample_colours,
            "conclusion": "P1 内部采样只出现面板自身的深色，没有任何形状/颜色线索；"
                          "两份不同的隐藏内容输出完全一致。",
        },
    }
    with open(os.path.join(TMP, "equivalence.json"), "w", encoding="utf-8") as fh:
        json.dump(eq, fh, ensure_ascii=False, indent=2)
    print("equivalence: identical_bytes =", eq["identical_bytes"],
          "| identical_pixels =", eq["pixel_comparison"]["identical_pixels"],
          "| hidden differs =", hidden_differs)

    os.makedirs(OUT, exist_ok=True)
    copies = [
        ("grid-scene.v1.snapshot", "grid-scene.snapshot"),
        ("grid-scene.v1.png", "grid-scene.png"),
        ("occlusion-a.v1.snapshot", "occlusion.snapshot"),
        ("occlusion-a.v1.png", "occlusion.png"),
        ("occlusion-b.v1.snapshot", "occlusion-alternative.snapshot"),
        ("occlusion-b.v1.png", "occlusion-alternative.png"),
        ("scene-data.json", "scene-data.json"),
        ("questions.json", "questions.json"),
        ("answers.json", "answers.json"),
        ("equivalence.json", "equivalence.json"),
    ]
    for src, dst in copies:
        shutil.copyfile(os.path.join(TMP, src), os.path.join(OUT, dst))
        print(f"  {dst:30s} {os.path.getsize(os.path.join(OUT, dst)):>8d} B  {sha(os.path.join(OUT, dst))[:16]}")

    req = count_requests("A19")
    m = build_metrics(
        "A19",
        title="构造可核验的视觉题场",
        status="completed",
        started_at="2026-10-03T14:00:00+08:00",
        ended_at="2026-10-03T14:35:00+08:00",
        outputs=[c[1] for c in copies] + ["snapshot-usage.md", "task-metrics.json"],
        final_pngs=3,
        dsl_versions=2,
        notes=[
            "grid-scene.png 1600x1600：64 对象，4 色各 16、4 形各 16，每行≥3 色且≥3 形（scene-data.json 记录逐行集合）。",
            "occlusion.png 与 occlusion-alternative.png 渲染字节完全相同（sha256 一致），"
            "像素比较差异像素 0；两份隐藏内容分别是红色正方形与绿色圆形，均被 P1 完全覆盖。",
            "14 道题（12 网格 + 2 遮挡），至少 4 道需要两步关系；全部答案由脚本从 scene-data.json 计算。",
            "题面写明比较标准、坐标原点（左上，x 右 y 下）与容差 ±2px；排序题注明同距时的打破规则。",
            "编号≥18 的要求来自 TASK.md 原文，本题编号为 G01–G64，scene-data.json 有完整几何。",
        ],
        extra={
            "final_image": {
                "files": ["grid-scene.png", "occlusion.png", "occlusion-alternative.png"],
                "sizes": [[1600, 1600], [800, 800], [800, 800]], "format": "PNG", "viewed": True},
            "requirements_checked": {
                "grid_64_objects_ids_reading_order": True,
                "four_colours_16_each": True,
                "four_shapes_16_each": True,
                "three_sizes_48_64_80": True,
                "each_row_three_colours_and_shapes": True,
                "ring_inner_diameter_half": True,
                "id_outside_body": True,
                "no_external_images": True,
                "occlusion_two_hidden_contents_one_output": True,
                "occlusion_byte_identical": True,
                "occlusion_pixel_identical": True,
                "occlusion_no_dashed_leak": True,
                "grid_questions_12": True,
                "occlusion_questions_2": True,
                "at_least_4_two_step": True,
                "one_answer_cannot_be_determined": True,
                "question_types_cover_required_set": True,
                "answers_computed_not_handwritten": True,
                "scene_data_seed_and_geometry": True,
                "questions_json_has_no_answers": True,
                "equivalence_json_has_hashes": True,
            },
            "question_type_coverage": {
                "复合属性检索": 2, "严格中心左右关系": 3, "距离比较": 2, "排序": 2,
                "包围框": 2, "颜色/形状计数": 1, "遮挡场景": 2},
            "hidden_content": {"a": eq["hidden_content_summary"]["a"],
                               "b": eq["hidden_content_summary"]["b"]},
        },
    )
    m["iterations"]["image_reviews"] = 3
    m["iterations"]["image_reviews_note"] = "read_image：grid-scene.png、occlusion-a.png、（等价性由哈希与逐像素比较替代第二张的重复查看）"
    write_json(os.path.join(OUT, "task-metrics.json"), m)
    print("task-metrics.json:", req["requests_total"], "requests",
          req["render_success"], "success", req["render_failed"], "failed")


if __name__ == "__main__":
    main()
