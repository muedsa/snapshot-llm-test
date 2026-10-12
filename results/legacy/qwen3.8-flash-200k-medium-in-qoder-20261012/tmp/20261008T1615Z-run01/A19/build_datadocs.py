"""A19 · 生成 scene-data.json 与 equivalence.json（全部数值来自真实几何与真实位图）。"""
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "A19"))
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
import gen_occlusion as G  # noqa: E402
import gen_scene as GS  # noqa: E402
from gen_scene import CELL, COLORS, SHAPES, SIZES, SEED  # noqa: E402

TMP = root / "tmp" / rid / "A19"
OUT = root / "outputs" / rid / "A19"
O = json.loads((TMP / "layouts" / "scene-objects.json").read_text(encoding="utf-8"))


rebuilt, attempt, used_seed = GS.build_scene()
assert rebuilt == O, "重放的种子几何与已交付位图所用几何不一致，种子记录不可信"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def size(o):
    return o["size"]


rows = {}
for r in range(1, 9):
    items = [o for o in O if o["row"] == r]
    rows[r] = {"colors": sorted({o["color_key"] for o in items}),
               "shapes": sorted({o["shape"] for o in items}),
               "color_count": len({o["color_key"] for o in items}),
               "shape_count": len({o["shape"] for o in items})}
cols = {}
for c in range(1, 9):
    cols[c] = [o["id"] for o in sorted((o for o in O if o["col"] == c), key=lambda o: o["row"])]

scene_data = {
    "path_base": "suite_root",
    "task_id": "A19",
    "generated_by": "tmp/%s/A19/gen_scene.py, tmp/%s/A19/gen_occlusion.py" % (rid, rid),
    "grid_scene": {
        "png": "outputs/%s/A19/grid-scene.png" % rid,
        "snapshot": "outputs/%s/A19/grid-scene.snapshot" % rid,
        "pixel_size": [1600, 1600],
        "png_sha256": sha(OUT / "grid-scene.png"),
        "dsl_sha256": sha(OUT / "grid-scene.snapshot"),
        "seed_base": SEED,
        "seed_used": used_seed,
        "seed_attempt": attempt,
        "seed_note": "从 seed_base 起每次失败自增，第 attempt 次同时满足全部约束",
        "cell_px": CELL,
        "grid": [8, 8],
        "numbering": "G01–G64，行优先：从左到右、从上到下；id = (row-1)*8 + col",
        "coordinate_origin": "画布左上角，x 向右、y 向下，单位像素",
        "subject_center_formula": "cx = col*200 - 100；cy = row*200 - 112（每格主体中心上移 12 px 以容纳格内编号标签）",
        "label_placement": "编号标签位于主体下方、同一格内，左边界 gx0+20、宽 160、高 26，不计入主体",
        "palette": COLORS,
        "shapes": SHAPES,
        "sizes": SIZES,
        "size_semantics": "圆与圆环按外径/直径，方与圆角方按边长；圆环内径为外径一半",
        "objects": O,
        "constraints": {
            "color_totals": {c: sum(1 for o in O if o["color_key"] == c) for c in COLORS},
            "shape_totals": {s: sum(1 for o in O if o["shape"] == s) for s in SHAPES},
            "size_totals": {s: sum(1 for o in O if o["size"] == s) for s in SIZES},
            "per_row_diversity": rows,
            "column_ids": cols,
            "one_subject_per_cell": len({(o["row"], o["col"]) for o in O}) == 64,
            "all_rows_have_ge_3_colors": all(v["color_count"] >= 3 for v in rows.values()),
            "all_rows_have_ge_3_shapes": all(v["shape_count"] >= 3 for v in rows.values()),
        },
        "bitmap_audit": json.loads((TMP / "layouts" / "grid-bitmap-audit.json")
                                   .read_text(encoding="utf-8")),
    },
    "occlusion_scene": {
        "pixel_size": [800, 800],
        "plate_bbox": list(G.PLATE_BOX) and [G.PLATE_BOX[0], G.PLATE_BOX[1],
                                             G.PLATE_BOX[0] + G.PLATE_BOX[2],
                                             G.PLATE_BOX[1] + G.PLATE_BOX[3]],
        "plate_color": G.PLATE,
        "plate_opaque": True,
        "hidden_leakage": "无：最终图中遮挡板区域只有板色与两行说明文字，无虚线、无半透明、无轮廓泄漏",
        "visible_objects": [{"id": v[0], "shape": v[1], "x": v[2], "y": v[3],
                             "size": v[4], "color": v[5]} for v in G.VISIBLE],
        "hidden_variants": {k: [{"shape": h[0], "x": h[1], "y": h[2], "size": h[3],
                                 "color": h[4], "tag": h[5]} for h in v]
                            for k, v in G.HIDDEN.items()},
        "hidden_count_note": "隐藏对象数量只作为构造证据；questions.json 中没有任何一题以隐藏数量为标准答案。",
    },
}
(OUT / "scene-data.json").write_text(json.dumps(scene_data, ensure_ascii=False, indent=2) + "\n",
                                     encoding="utf-8", newline="\n")

# ---------------- equivalence.json：真实位图对比 ----------------
PREV = TMP / "preview"


def load(name):
    path = PREV / name
    im = Image.open(path)
    return im, np.asarray(im.convert("RGB")).astype(np.int16)


def compare(a, b):
    ia, A = load(a)
    ib, B = load(b)
    d = np.abs(A - B)
    mask = d.max(axis=2) > 0
    ys, xs = np.where(mask)
    return {
        "left": "tmp/%s/A19/preview/%s" % (rid, a),
        "right": "tmp/%s/A19/preview/%s" % (rid, b),
        "size_left": list(ia.size), "size_right": list(ib.size),
        "sha256_left": sha(PREV / a), "sha256_right": sha(PREV / b),
        "bytes_identical": sha(PREV / a) == sha(PREV / b),
        "differing_pixels": int(mask.sum()),
        "total_pixels": ia.size[0] * ia.size[1],
        "differing_fraction": round(float(mask.mean()), 6),
        "max_channel_difference": int(d.max()),
        "difference_bbox": None if not mask.any() else [int(xs.min()), int(ys.min()),
                                                        int(xs.max()), int(ys.max())],
    }


eq = {
    "path_base": "suite_root",
    "task_id": "A19",
    "claim": "两份隐藏内容完全不同的完整 DSL，经真实服务渲染后得到像素级一致的最终图片",
    "method": "对两次真实服务响应的原始 PNG 做 sha256 与 numpy 逐像素（RGB 三通道）差值比较",
    "primary_pair": compare("occlusion-v02.png", "occlusion-alternative-v02.png"),
    "dsls": {
        "occlusion": {"snapshot": "outputs/%s/A19/occlusion.snapshot" % rid,
                      "png": "outputs/%s/A19/occlusion.png" % rid,
                      "dsl_bytes": (OUT / "occlusion.snapshot").stat().st_size,
                      "dsl_sha256": sha(OUT / "occlusion.snapshot"),
                      "png_sha256": sha(OUT / "occlusion.png"),
                      "hidden_subjects": len(G.HIDDEN["occlusion"])},
        "occlusion-alternative": {
            "snapshot": "outputs/%s/A19/occlusion-alternative.snapshot" % rid,
            "png": "outputs/%s/A19/occlusion-alternative.png" % rid,
            "dsl_bytes": (OUT / "occlusion-alternative.snapshot").stat().st_size,
            "dsl_sha256": sha(OUT / "occlusion-alternative.snapshot"),
            "png_sha256": sha(OUT / "occlusion-alternative.png"),
            "hidden_subjects": len(G.HIDDEN["occlusion-alternative"])},
    },
    "hidden_content_differs": {
        "subject_counts": {"occlusion": len(G.HIDDEN["occlusion"]),
                           "occlusion-alternative": len(G.HIDDEN["occlusion-alternative"])},
        "shape_multiset_left": sorted(h[0] for h in G.HIDDEN["occlusion"]),
        "shape_multiset_right": sorted(h[0] for h in G.HIDDEN["occlusion-alternative"]),
        "dsl_bytes_equal": (OUT / "occlusion.snapshot").read_bytes() ==
                           (OUT / "occlusion-alternative.snapshot").read_bytes(),
    },
    "control_removed_plate": {
        "note": "同一批 DSL 去掉遮挡板后的诊断渲染（仅留痕于临时目录，不是交付图），"
                "用来证明两者隐藏内容确实不同，且差异像素完全落在板的包围框内。",
        "hidden_a_vs_hidden_b": compare("occlusion-noplate-v02.png",
                                        "occlusion-alternative-noplate-v02.png"),
        "a_covered_vs_a_exposed": compare("occlusion-v02.png", "occlusion-noplate-v02.png"),
        "b_covered_vs_b_exposed": compare("occlusion-alternative-v02.png",
                                          "occlusion-alternative-noplate-v02.png"),
    },
}
prim = eq["primary_pair"]
eq["conclusion"] = {
    "final_images_pixel_identical": prim["differing_pixels"] == 0 and prim["bytes_identical"],
    "hidden_layers_actually_differ": eq["control_removed_plate"]["hidden_a_vs_hidden_b"]
                                     ["differing_pixels"] > 0,
    "hidden_difference_confined_to_plate":
        eq["control_removed_plate"]["hidden_a_vs_hidden_b"]["difference_bbox"] is not None
        and eq["control_removed_plate"]["hidden_a_vs_hidden_b"]["difference_bbox"][0] >= 200
        and eq["control_removed_plate"]["hidden_a_vs_hidden_b"]["difference_bbox"][1] >= 210
        and eq["control_removed_plate"]["hidden_a_vs_hidden_b"]["difference_bbox"][2] <= 599
        and eq["control_removed_plate"]["hidden_a_vs_hidden_b"]["difference_bbox"][3] <= 609,
    "no_leakage_of_hidden_content": prim["differing_pixels"] == 0,
}
(OUT / "equivalence.json").write_text(json.dumps(eq, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8", newline="\n")
print(json.dumps(eq["conclusion"], ensure_ascii=False, indent=1))
print("scene-data objects", len(O), "hidden", {k: len(v) for k, v in G.HIDDEN.items()})
