# -*- coding: utf-8 -*-
"""Emit the three A19 DSL files + the raw scene JSON used by later steps.

Usage (launch base = suite root):
  python tmp/run-20261011-01/A19/scripts/build_a19.py

Writes into tmp/run-20261011-01/A19/gen/:
  grid-scene.snapshot, occlusion.snapshot, occlusion-alternative.snapshot,
  scene-raw.json (seed + objects + distribution, later shaped into
  scene-data.json after real-render measurement).
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import a19_scene as S  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[4]
GEN = ROOT / "tmp/run-20261011-01/A19/gen"


def main():
    seed, objs, dist = S.build_scene()
    GEN.mkdir(parents=True, exist_ok=True)

    grid = S.emit_grid(objs)
    (GEN / "grid-scene.snapshot").write_text(grid, encoding="utf-8")
    print("grid-scene.snapshot: %d bytes (%d objects)"
          % (len(grid.encode("utf-8")), len(objs)))

    for ver, fname in (("A", "occlusion.snapshot"),
                       ("B", "occlusion-alternative.snapshot")):
        dsl = S.emit_occlusion(ver)
        (GEN / fname).write_text(dsl, encoding="utf-8")
        print("%s: %d bytes (hidden=%s)" % (
            fname, len(dsl.encode("utf-8")), S.HIDDEN[ver]))

    raw = {
        "seed": seed,
        "seed_note": "洗牌种子；分布以 objects 实测为准（生成器断言全部通过）",
        "canvas": [S.CANVAS, S.CANVAS],
        "grid": {
            "rows": S.ROWS, "cols": S.COLS, "cell": [S.CELL, S.CELL],
            "id_order": "row-major (left->right, top->bottom)",
            "index_formula": "id = (row-1)*8 + col",
            "center_formula": "(200*col+100, 200*row+100)",
            "id_text_anchor": "cell左上角 + (10, 6)，主体外框从 cell+60 起，"
                              "ID 与主体必然分离",
        },
        "palette": {
            "colors": [{"name": n, "hex": h} for n, h in S.COLORS],
            "shapes": [
                {"name": "circle", "render": "直径=size，borderRadius=size/2"},
                {"name": "square", "render": "边长=size，无圆角"},
                {"name": "ring", "render": "外径=size，border=size/4（内径=size/2），"
                                           "borderRadius=size/2，无填充"},
                {"name": "rounded", "render": "边长=size，borderRadius=size/4"},
            ],
            "sizes": S.SIZES,
        },
        "objects": objs,
        "distribution": dist,
    }
    (GEN / "scene-raw.json").write_text(
        json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("scene-raw.json written; seed =", seed)


if __name__ == "__main__":
    main()
