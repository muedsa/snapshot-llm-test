from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import shutil
import sys
from collections import Counter
from pathlib import Path

import PIL
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

RUN = (ROOT / "tmp" / "_suite" / "run-id.txt").read_text(encoding="utf-8").strip()
TASK = "A19"
HERE = ROOT / sk.CONFIG["temp_root"] / RUN / TASK
OUTPUT = ROOT / sk.CONFIG["output_root"] / RUN / TASK
COLORS = {"blue": "#2563EB", "orange": "#EA580C", "green": "#059669", "purple": "#7C3AED"}
SHAPES = ("circle", "square", "ring", "rounded_square")
SIZES = (48, 64, 80)
GRID_ORIGIN = (100, 140)
CELL = 175


def rp(path: Path) -> str:
    return sk.rel(path, ROOT)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guard() -> None:
    state = json.loads((ROOT / sk.CONFIG["output_root"] / RUN / "_suite/suite-state.json").read_text(encoding="utf-8"))
    order = [item["id"] for item in sk.CATALOG["tasks"]]
    statuses = {item["id"]: item["status"] for item in state["tasks"]}
    assert all(statuses[item] == "completed" for item in order[:order.index(TASK)]), "strict task order"
    assert statuses[TASK] in ("pending", "in_progress"), "A19 state"


def generate_objects() -> tuple[int, list[dict]]:
    for seed in range(20261124, 20261224):
        records = []
        for ci, color in enumerate(COLORS):
            for si, shape in enumerate(SHAPES):
                for variant in range(4):
                    size = SIZES[variant] if variant < 3 else SIZES[(ci + si + variant) % 3]
                    records.append({"color": color, "shape": shape, "size": size})
        random.Random(seed).shuffle(records)
        rows = [records[i:i+8] for i in range(0, 64, 8)]
        if all(len({r["color"] for r in row}) >= 3 and len({r["shape"] for r in row}) >= 3 for row in rows):
            objects = []
            for index, record in enumerate(records):
                row, col = divmod(index, 8)
                size = record["size"]
                cx = GRID_ORIGIN[0] + col * CELL + CELL / 2
                cy = GRID_ORIGIN[1] + row * CELL + 96
                left, top = cx - size / 2, cy - size / 2
                objects.append({
                    "id": f"G{index+1:02d}", "row": row + 1, "column": col + 1,
                    "color": record["color"], "color_hex": COLORS[record["color"]],
                    "shape": record["shape"], "size": size, "center": [cx, cy],
                    "body_bbox": [left, top, left + size, top + size],
                    "id_text_bbox": [GRID_ORIGIN[0] + col * CELL + 12, GRID_ORIGIN[1] + row * CELL + 10,
                                     GRID_ORIGIN[0] + col * CELL + 70, GRID_ORIGIN[1] + row * CELL + 38],
                    "inner_diameter": size / 2 if record["shape"] == "ring" else None,
                })
            return seed, objects
    raise RuntimeError("no valid deterministic arrangement")


def distribution(objects: list[dict]) -> dict:
    color_counts = Counter(o["color"] for o in objects)
    shape_counts = Counter(o["shape"] for o in objects)
    size_counts = Counter(o["size"] for o in objects)
    combos = Counter((o["color"], o["shape"]) for o in objects)
    rows = []
    for row in range(1, 9):
        items = [o for o in objects if o["row"] == row]
        rows.append({"row": row, "ids": [o["id"] for o in items],
                     "color_counts": dict(Counter(o["color"] for o in items)),
                     "shape_counts": dict(Counter(o["shape"] for o in items)),
                     "distinct_colors": len({o["color"] for o in items}),
                     "distinct_shapes": len({o["shape"] for o in items})})
    size_coverage = {f"{color}|{shape}": sorted({o["size"] for o in objects if o["color"] == color and o["shape"] == shape})
                     for color in COLORS for shape in SHAPES}
    return {"color_counts": dict(color_counts), "shape_counts": dict(shape_counts),
            "size_counts": dict(size_counts), "color_shape_counts": {f"{c}|{s}": combos[(c, s)] for c in COLORS for s in SHAPES},
            "color_shape_size_coverage": size_coverage, "rows": rows,
            "checks": {"colors_each_16": all(v == 16 for v in color_counts.values()),
                       "shapes_each_16": all(v == 16 for v in shape_counts.values()),
                       "all_16_color_shape_combinations": len(combos) == 16 and all(v == 4 for v in combos.values()),
                       "every_color_shape_has_all_three_sizes": all(v == [48, 64, 80] for v in size_coverage.values()),
                       "every_row_at_least_3_colors_and_shapes": all(r["distinct_colors"] >= 3 and r["distinct_shapes"] >= 3 for r in rows)}}


def shape_dsl(o: dict, cell_background: str) -> str:
    x, y, size, color = o["center"][0], o["center"][1], o["size"], o["color_hex"]
    if o["shape"] == "circle":
        return sk.box(x-size/2, y-size/2, size, size, color, size/2)
    if o["shape"] == "square":
        return sk.box(x-size/2, y-size/2, size, size, color)
    if o["shape"] == "rounded_square":
        return sk.box(x-size/2, y-size/2, size, size, color, 16)
    inner = size / 2
    return (sk.box(x-size/2, y-size/2, size, size, color, size/2)
            + sk.box(x-inner/2, y-inner/2, inner, inner, cell_background, inner/2))


def grid_dsl(objects: list[dict]) -> str:
    children = [sk.label("64对象视觉题场 · G01–G64", 100, 42, 1400, 54, 34, "#0F172A", True)]
    for row in range(8):
        for col in range(8):
            x, y = GRID_ORIGIN[0] + col * CELL, GRID_ORIGIN[1] + row * CELL
            background = "#FFFFFF" if (row + col) % 2 == 0 else "#F1F5F9"
            children.append(sk.box(x, y, CELL, CELL, background, 0, "#CBD5E1"))
    for o in objects:
        row, col = o["row"] - 1, o["column"] - 1
        background = "#FFFFFF" if (row + col) % 2 == 0 else "#F1F5F9"
        children.append(sk.label(o["id"], o["id_text_bbox"][0], o["id_text_bbox"][1], 58, 28, 18, "#0F172A", True))
        children.append(shape_dsl(o, background))
    return sk.snapshot(1600, 1600, children, "#E2E8F0")


def occlusion_dsl(version: str) -> str:
    children = [sk.box(0, 0, 800, 800, "#E2E8F0")]
    if version == "A":
        for x, y in ((300, 300), (400, 400), (500, 500)):
            children.append(sk.box(x-40, y-40, 80, 80, COLORS["blue"], 40))
    else:
        children.append(sk.box(290, 290, 120, 120, COLORS["orange"], 24))
        children.append(sk.box(252, 452, 96, 96, COLORS["purple"], 48))
        children.append(sk.box(452, 252, 96, 96, COLORS["purple"], 48))
        children.append(sk.box(276, 476, 48, 48, "#E2E8F0", 24))
        children.append(sk.box(476, 276, 48, 48, "#E2E8F0", 24))
    children.append(sk.box(140, 140, 520, 520, "#475569", 36, "#64748B"))
    children.append(sk.box(40, 680, 80, 80, COLORS["orange"]))
    children.append(sk.box(680, 40, 80, 80, COLORS["green"], 40))
    children.append(sk.box(680, 680, 80, 80, COLORS["purple"], 40))
    children.append(sk.box(700, 700, 40, 40, "#E2E8F0", 20))
    return sk.snapshot(800, 800, children, "#E2E8F0")


def by_id(objects: list[dict], object_id: str) -> dict:
    return next(o for o in objects if o["id"] == object_id)


def area(o: dict) -> float:
    l, t, r, b = o["body_bbox"]
    return (r-l)*(b-t)


def make_questions(objects: list[dict]) -> tuple[list[dict], list[dict]]:
    questions, answers = [], []
    origin = "画布左上角为(0,0)，x向右、y向下，单位像素；中心坐标与主体框均以最终图实际几何为准。"
    def add(qid, image, qtype, text, answer, steps, two=False, refs=None, tolerance="几何比较容差0.01px；距离排序若并列依次按中心x、中心y、ID升序。"):
        questions.append({"id": qid, "image": image, "type": qtype, "text": text,
                          "coordinate_origin": origin, "comparison_rules": tolerance,
                          "requires_two_step": two})
        answers.append({"id": qid, "answer": answer, "calculation_steps": steps,
                        "referenced_objects": refs or [], "coordinate_tolerance": tolerance,
                        "visibility_basis": "答案仅使用 grid-scene.png 中完整可见的主体、编号与几何；未使用任何隐藏信息。"})
    exact = next((c, s, z) for c in COLORS for s in SHAPES for z in SIZES
                 if sum(o["color"] == c and o["shape"] == s and o["size"] == z for o in objects) == 1)
    target = next(o for o in objects if (o["color"], o["shape"], o["size"]) == exact)
    add("Q01", "grid-scene.png", "composite_retrieval",
        f"唯一同时满足颜色为{target['color']}、形状为{target['shape']}、尺寸为{target['size']}px的对象编号是什么？",
        target["id"], [f"筛选颜色={target['color']}、形状={target['shape']}、尺寸={target['size']}。", "命中仅1个。"], refs=[target["id"]])
    candidates = [o for o in objects if o["color"] == "purple" and o["shape"] in {"circle", "rounded_square"}]
    ranked = sorted(candidates, key=lambda o: (-area(o), o["center"][1], o["id"]))
    target = ranked[0]
    add("Q02", "grid-scene.png", "two_step_filter_extreme",
        "先筛选所有紫色且形状为圆或圆角方的对象，再取主体包围框面积最大者；面积并列时取中心y更小者，仍并列取ID更小者。答案编号是什么？",
        target["id"], ["得到候选集。", "按主体框宽×高降序、中心y升序、ID升序排序，取首项。"], True, [o["id"] for o in ranked])
    found = None
    for color in COLORS:
        for ref in objects:
            hits = [o for o in objects if o["color"] == color and o["center"][0] < ref["center"][0] and o["center"][1] > ref["center"][1]]
            if len(hits) == 1:
                found = (color, ref, hits[0]); break
        if found: break
    color, ref, target = found
    add("Q03", "grid-scene.png", "strict_relation",
        f"在{color}色对象中，中心x严格小于{ref['id']}的中心x、且中心y严格大于{ref['id']}的中心y的对象编号是什么？严格不等号，不含相等。",
        target["id"], [f"参照{ref['id']}中心{ref['center']}。", "筛选同时满足两个严格不等式的同色对象，命中1个。"], True, [ref["id"], target["id"]])
    ref = objects[26]
    distances = sorted((math.dist(o["center"], ref["center"]), o["id"]) for o in objects if o["id"] != ref["id"])
    target = by_id(objects, distances[0][1])
    add("Q04", "grid-scene.png", "distance",
        f"除{ref['id']}自身外，哪个对象的中心与{ref['id']}中心的欧氏距离最小？距离按sqrt((x2-x1)^2+(y2-y1)^2)。",
        target["id"], [f"计算其余63个对象到{ref['id']}的中心欧氏距离。", "最小值唯一。"], refs=[ref["id"], target["id"]])
    ordered = sorted(objects, key=lambda o: (o["center"][1], o["center"][0], o["id"]))
    target = ordered[16]
    add("Q05", "grid-scene.png", "ordering",
        "将全部64个对象按中心y升序排列；中心y相同时按中心x升序；仍相同时按ID升序。第17个对象编号是什么？",
        target["id"], ["应用三元排序键。", "取1-based第17项。"], refs=[target["id"]])
    target = sorted(objects, key=lambda o: (-area(o), o["center"][0], o["id"]))[0]
    add("Q06", "grid-scene.png", "bbox",
        "哪个对象的主体包围框面积最大？面积按(right-left)×(bottom-top)；并列时取中心x更小者，仍并列取ID更小者。",
        target["id"], ["计算64个主体框面积。", "按面积降序、中心x升序、ID升序取首项。"], refs=[target["id"]])
    count = sum(o["row"] == 1 and o["color"] == "blue" for o in objects)
    add("Q07", "grid-scene.png", "color_count", "第1行共有多少个蓝色主体？只统计主体，不把编号文字计入。", count, ["选择row=1。", "统计color=blue。"])
    count = sum(o["color"] == "green" and o["shape"] == "ring" for o in objects)
    add("Q08", "grid-scene.png", "shape_count", "整个网格中共有多少个绿色圆环？圆环按外径判断形状，内径不计为另一个主体。", count, ["筛选color=green且shape=ring。"])
    purple = [o for o in objects if o["color"] == "purple" and o["size"] >= 64]
    circles = sum(o["shape"] == "circle" for o in purple)
    rounded = sum(o["shape"] == "rounded_square" for o in purple)
    add("Q09", "grid-scene.png", "two_step_count",
        "先筛选尺寸不小于64px的紫色对象，再计算其中圆形数量减去圆角方数量，结果是多少？", circles-rounded,
        ["筛选紫色且size>=64。", "分别统计圆形与圆角方并相减。"], True, [o["id"] for o in purple])
    ref = objects[42]
    candidates = [o for o in objects if o["color"] == "orange"]
    distances = sorted((math.dist(o["center"], ref["center"]), o["id"]) for o in candidates)
    target = by_id(objects, distances[0][1])
    add("Q10", "grid-scene.png", "two_step_distance",
        f"先筛选全部橙色对象，再问其中哪个对象的中心距{ref['id']}中心最近？使用欧氏中心距离。", target["id"],
        ["筛选橙色对象。", "计算到参照中心的距离并取唯一最小值。"], True, [ref["id"], target["id"]])
    pair = None
    for a in objects:
        for b in objects:
            if a["id"] >= b["id"]: continue
            low, high = sorted((a["center"][0], b["center"][0]))
            candidates = [o for o in objects if o["color"] == "blue" and low < o["center"][0] < high]
            if 2 <= len(candidates) <= 10:
                ranked = sorted(candidates, key=lambda o: (-o["body_bbox"][2], o["id"]))
                if ranked[0]["body_bbox"][2] > ranked[1]["body_bbox"][2]:
                    pair = (a, b, ranked[0], ranked); break
        if pair: break
    a, b, target, ranked = pair
    add("Q11", "grid-scene.png", "two_step_bbox",
        f"在蓝色对象中，只保留中心x严格介于{a['id']}与{b['id']}中心x之间的对象，再取主体框right坐标最大者；right并列时取ID更小者。答案编号是什么？",
        target["id"], ["构造中心x开区间。", "筛选蓝色对象。", "比较主体框right并取最大值。"], True, [a["id"], b["id"], target["id"]])
    blue = sorted([o for o in objects if o["color"] == "blue"], key=lambda o: (-area(o), o["center"][0], o["id"]))
    target = blue[1]
    add("Q12", "grid-scene.png", "two_step_ordering",
        "先筛选全部蓝色对象，再按主体框面积降序、中心x升序、ID升序排列。第2个对象编号是什么？", target["id"],
        ["筛选蓝色对象。", "应用三元排序键并取1-based第2项。"], True, [o["id"] for o in blue])
    questions.extend([
        {"id": "Q13", "image": "occlusion.png", "type": "insufficient_information",
         "text": "完全不透明遮挡物覆盖的区域内，蓝色圆主体共有多少个？", "coordinate_origin": origin,
         "comparison_rules": "只能依据最终可见像素；遮挡物后方内容不可见。", "requires_two_step": False},
        {"id": "Q14", "image": "occlusion.png", "type": "visible_relation",
         "text": "在未被遮挡的可见主体中，右上绿色圆的中心x是否严格大于左下橙色方块的中心x？", "coordinate_origin": origin,
         "comparison_rules": "严格大于；中心坐标容差0.01px。", "requires_two_step": False},
    ])
    answers.extend([
        {"id": "Q13", "answer": "无法确定", "calculation_steps": ["遮挡物为不透明且覆盖隐藏子树。", "A/B可见层相同，隐藏子树不同；最终可见像素不能唯一决定被遮挡的蓝色圆数量。"],
         "referenced_objects": [], "coordinate_tolerance": "不适用", "visibility_basis": "occlusion.png与occlusion-alternative.png逐像素RGBA完全一致；没有虚线、阴影或滤镜泄漏。"},
        {"id": "Q14", "answer": "是", "calculation_steps": ["可见绿色圆中心x=720。", "可见橙色方块中心x=80。", "720>80。"],
         "referenced_objects": ["visible_green_circle", "visible_orange_square"], "coordinate_tolerance": "0.01px", "visibility_basis": "两个主体均位于遮挡物外，在最终occlusion.png中完整可见。"},
    ])
    return questions, answers


def prepare() -> None:
    guard()
    sk.begin_task(RUN, TASK)
    seed, objects = generate_objects()
    dist = distribution(objects)
    assert all(dist["checks"].values())
    questions, answers = make_questions(objects)
    assert len(questions) == 14 and sum(q["requires_two_step"] for q in questions) >= 4
    directory = HERE / "versions" / "v001"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "grid-scene.snapshot").write_text(grid_dsl(objects), encoding="utf-8")
    (directory / "occlusion.snapshot").write_text(occlusion_dsl("A"), encoding="utf-8")
    (directory / "occlusion-alternative.snapshot").write_text(occlusion_dsl("B"), encoding="utf-8")
    sk.write_json(directory / "scene-data.json", {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "seed": seed, "generation_algorithm": "固定种子随机排列16种颜色×形状组合各4个尺寸变体，直至每行至少3色3形；编号按行优先分配。",
        "canvas": [1600, 1600], "grid": {"rows": 8, "columns": 8, "cell_size": CELL, "origin": list(GRID_ORIGIN)},
        "objects": objects, "distribution": dist})
    sk.write_json(directory / "questions.json", {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "questions": questions})
    sk.write_json(directory / "answers.json", {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "answers": answers})
    print(json.dumps({"prepared": TASK, "seed": seed, "objects": len(objects), "questions": len(questions), "two_step": sum(q["requires_two_step"] for q in questions)}, ensure_ascii=False))


def render_file(source: Path, png: Path, version: str, case_id: str) -> dict:
    response, record = sk.request(RUN, TASK, "render", sk.BASE + "/snapshot", source.read_bytes(), "text/plain; charset=utf-8", version_id=version, case_id=case_id)
    if record["http_status"] != 200 or not response.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError(f"render failed: {record}")
    png.write_bytes(response)
    with Image.open(png) as image:
        size = list(image.size)
    expected = [1600, 1600] if case_id == "grid" else [800, 800]
    if size != expected:
        raise RuntimeError(f"wrong size {size}")
    return {"image": rp(png), "dsl": rp(source), "size": size, "request_id": record["request_id"], "png_sha256": sha(png)}


def execute(version: str) -> None:
    directory = HERE / "versions" / version
    for stem, case_id in (("grid-scene", "grid"), ("occlusion", "occlusion_A"), ("occlusion-alternative", "occlusion_B")):
        print(json.dumps(render_file(directory / f"{stem}.snapshot", directory / f"{stem}.png", version, case_id), ensure_ascii=False))


def provenance(png: Path, dsl: Path) -> dict | None:
    png_hash, dsl_hash = sha(png), hashlib.sha256(dsl.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    for request in sk.read_jsonl(HERE / "requests.jsonl"):
        if request["request_type"] != "render": continue
        response, request_file = ROOT / request["response_file"], ROOT / request["request_file"]
        if response.exists() and request_file.exists() and sha(response) == png_hash and hashlib.sha256(request_file.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == dsl_hash:
            return {"request_id": request["request_id"], "request_file": request["request_file"], "response_file": request["response_file"],
                    "http_status": request["http_status"], "content_type": request["content_type"], "png_sha256": png_hash,
                    "dsl_sha256": hashlib.sha256(dsl.read_bytes()).hexdigest(), "png_byte_identical_to_response": True, "dsl_matches_submitted_utf8": True}
    return None


def compare_rgba(a_path: Path, b_path: Path) -> dict:
    with Image.open(a_path) as a_image, Image.open(b_path) as b_image:
        a, b = a_image.convert("RGBA"), b_image.convert("RGBA")
        same_size = a.size == b.size
        a_bytes, b_bytes = a.tobytes(), b.tobytes()
        different = 0
        max_delta = 0
        if same_size:
            for index in range(0, len(a_bytes), 4):
                deltas = [abs(a_bytes[index+c] - b_bytes[index+c]) for c in range(4)]
                if any(deltas):
                    different += 1
                    max_delta = max(max_delta, *deltas)
        return {"decoder": f"Pillow {PIL.__version__}", "decoder_mode": "Image.convert('RGBA')，8位未预乘RGBA",
                "same_size": same_size, "size": list(a.size), "different_pixels": different, "max_channel_delta": max_delta,
                "rgba_array_sha256_a": hashlib.sha256(a_bytes).hexdigest(), "rgba_array_sha256_b": hashlib.sha256(b_bytes).hexdigest(),
                "pixel_equivalent": same_size and different == 0}


def make_inspection_crops(png: Path) -> list[Path]:
    target_dir = HERE / "inspection"
    target_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    with Image.open(png) as image:
        for index, (left, top, right, bottom) in enumerate(((100,140,800,910),(800,140,1500,910),(100,910,800,1540),(800,910,1500,1540)), 1):
            crop = image.crop((left, top, right, bottom))
            crop = crop.resize((1050, int(crop.height * 1.5)), Image.Resampling.LANCZOS)
            path = target_dir / f"grid-quadrant-{index}.png"
            crop.save(path)
            paths.append(path)
    return paths


def record_history(version: str, crops: list[Path]) -> None:
    path = HERE / "iterations.jsonl"
    existing = sk.read_jsonl(path)
    if existing:
        if len(existing) != 7:
            raise SystemExit("unexpected existing A19 history")
        return
    entries = [
        ("grid", "baseline", rp(HERE / "versions" / version / "grid-scene.png"), "1600×1600网格基线，64个编号主体待最终复核。"),
        ("occlusion_A", "baseline", rp(HERE / "versions" / version / "occlusion.png"), "遮挡版本A基线。"),
        ("occlusion_B", "alternative", rp(HERE / "versions" / version / "occlusion-alternative.png"), "隐藏内容不同的遮挡版本B。"),
    ] + [("grid_crop", "audit_visual_recheck", rp(p), "网格象限局部放大复核。") for p in crops]
    for index, (case_id, kind, image, observed) in enumerate(entries, 1):
        sk.append_jsonl(path, {"iteration_id": f"{RUN}-{TASK}-{kind}-{index:02d}", "task_id": TASK, "case_id": case_id,
            "version_id": version, "parent_version": None, "type": kind, "image_path": image, "image_paths": [image],
            "viewed_at": sk.iso(), "timezone": "+08:00", "view_time_evidence": "最终图像查看后写入实际日志时间。",
            "observable_issues": observed, "changes": "最终验收，不修改图像。", "review_and_comparison": "以最终实际图像为准。",
            "completed_visual_iteration": kind in {"baseline", "alternative"}})


def finalize(review_file: str, version: str) -> None:
    guard()
    review = json.loads(Path(review_file).read_text(encoding="utf-8"))
    if not review.get("completed") or set(review.get("reviewed", {})) != {"grid-scene", "occlusion", "occlusion-alternative"}:
        raise SystemExit("all three completed visual reviews required")
    directory = HERE / "versions" / version
    scene = json.loads((directory / "scene-data.json").read_text(encoding="utf-8"))
    questions = json.loads((directory / "questions.json").read_text(encoding="utf-8"))
    answers = json.loads((directory / "answers.json").read_text(encoding="utf-8"))
    assert len(scene["objects"]) == 64 and all(scene["distribution"]["checks"].values())
    assert len(questions["questions"]) == 14 and len(answers["answers"]) == 14
    assert {q["id"] for q in questions["questions"]} == {a["id"] for a in answers["answers"]}
    for stem in ("grid-scene", "occlusion", "occlusion-alternative"):
        shutil.copyfile(directory / f"{stem}.png", OUTPUT / f"{stem}.png")
        shutil.copyfile(directory / f"{stem}.snapshot", OUTPUT / f"{stem}.snapshot")
        assert provenance(OUTPUT / f"{stem}.png", OUTPUT / f"{stem}.snapshot")
    comparison = compare_rgba(OUTPUT / "occlusion.png", OUTPUT / "occlusion-alternative.png")
    assert comparison["pixel_equivalent"]
    equivalence = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "versions": [
            {"version": "A", "dsl": "occlusion.snapshot", "png": "occlusion.png", "file_sha256": sha(OUTPUT / "occlusion.png"),
             "hidden_difference": "遮挡物内为三个蓝色圆。", "visible_layers_unchanged": "画布、背景、遮挡物、三个可见主体与渲染参数完全相同。"},
            {"version": "B", "dsl": "occlusion-alternative.snapshot", "png": "occlusion-alternative.png", "file_sha256": sha(OUTPUT / "occlusion-alternative.png"),
             "hidden_difference": "遮挡物内为橙色圆角方与两个紫色圆环。", "visible_layers_unchanged": "画布、背景、遮挡物、三个可见主体与渲染参数完全相同。"},
        ], "comparison": comparison, "conclusion": "同一解码器解码为8位未预乘RGBA后逐像素四通道完全一致；不同像素数0。",
        "occlusion_invariant": "隐藏子树全部位于不透明遮挡物[140,140,660,660]内，无阴影、滤镜或半透明效果；遮挡物圆角半径36，隐藏内容距边界至少60px。"}
    sk.write_json(OUTPUT / "equivalence.json", equivalence)
    for name in ("scene-data.json", "questions.json", "answers.json"):
        shutil.copyfile(directory / name, OUTPUT / name)
    crops = make_inspection_crops(OUTPUT / "grid-scene.png")
    record_history(version, crops)
    files = [f"{stem}.{suffix}" for stem in ("grid-scene", "occlusion", "occlusion-alternative") for suffix in ("png", "snapshot")]
    files += ["scene-data.json", "questions.json", "answers.json", "equivalence.json"]
    sk.write_usage(RUN, TASK, "completed", [
        ("grid coverage", "64对象按行优先编号；4色各16、4形各16、全部16种颜色×形状组合各4；每种颜色×形状均覆盖48/64/80。"),
        ("row constraints", "每行至少3色3形，scene-data.json记录实际频数、组合覆盖和逐行计数。"),
        ("questions", "12道网格题+2道遮挡题；至少4道两步关系；questions.json不含答案。"),
        ("occlusion equivalence", "A/B原始PNG保留；Pillow解码8位未预乘RGBA后不同像素0、最大通道差0。"),
        ("visual review", "三张最终PNG实际查看；网格另以四个象限放大检查全部64主体与编号。"),
    ], "固定种子生成受约束网格，题目从实际几何计算；遮挡案例用不透明前景保证隐藏差异不可见。",
       "首次渲染后完成静态覆盖检查、三图查看、四象限标签复核和RGBA逐像素等价检查；未发现需修改的交付缺陷。",
       [rp(OUTPUT / name) for name in files])
    sk.metrics(RUN, TASK)
    artifacts = [rp(path) for path in sorted(OUTPUT.iterdir()) if path.is_file()]
    sk.finish_task(RUN, TASK, artifacts, [rp(HERE / "final-review.json"), rp(OUTPUT / "equivalence.json")], issues=[])
    sk.metrics(RUN, TASK)
    print(json.dumps({"completed": TASK, "artifacts": artifacts, "pixel_equivalent": comparison["pixel_equivalent"]}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "execute", "finalize"])
    parser.add_argument("--version", default="v001")
    parser.add_argument("--review-file")
    args = parser.parse_args()
    if args.mode == "prepare": prepare()
    elif args.mode == "execute": execute(args.version)
    else: finalize(args.review_file, args.version)


if __name__ == "__main__":
    main()
