"""A19 step 1 - build and render the three delivered images + the four JSON files.

Order of work:
  1. gen_objects(seed) -> hard-asserted 8x8 scene
  2. grid_dsl(scene)   -> grid-scene.snapshot  -> POST /snapshot -> grid-scene.png
  3. occ_dsl(...)     -> the two occlusion DSLs -> POST /snapshot -> two PNGs
  4. write scene-data.json / questions.json / answers.json / equivalence.json
  5. print every D.warnings() entry
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A19"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import a19_scene as A  # noqa: E402

CST = timezone(timedelta(hours=8))
DRAFTS = os.path.join(TMP, "drafts")
PREVIEW = os.path.join(TMP, "preview")


def draft(name: str, text: str) -> str:
    os.makedirs(DRAFTS, exist_ok=True)
    p = os.path.join(DRAFTS, name)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return p


def jdump(name: str, obj) -> str:
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return p


def main() -> None:
    snapkit.configure(TASK, OUT, TMP)
    os.makedirs(PREVIEW, exist_ok=True)
    for f in (D.WARNINGS,):
        del f[:]

    # ---------------------------------------------------------------- grid ---
    objs = A.gen_objects()
    scene = A.build_scene_data(objs, "")
    grid_text = A.grid_dsl(scene)
    scene = A.build_scene_data(objs, grid_text)
    draft("grid-scene.snapshot", grid_text)
    print("grid DSL bytes:", len(grid_text.encode("utf-8")))
    r1 = snapkit.render(grid_text, "grid-scene.png", "grid-scene.snapshot", final=True)
    print("grid render:", r1.get("ok"), r1.get("status"), r1.get("bytes"), r1.get("elapsed_ms"))

    # ---------------------------------------------------------- occlusion ---
    occ_a_text, tech_a = A.occ_dsl(A.O_HIDDEN_A, "overdraw")
    occ_b_text, tech_b = A.occ_dsl(A.O_HIDDEN_B, "clip")
    draft("occlusion-A1-overdraw.snapshot", occ_a_text)
    draft("occlusion-B1-clip.snapshot", occ_b_text)
    print("occA DSL bytes:", len(occ_a_text.encode("utf-8")),
          "occB DSL bytes:", len(occ_b_text.encode("utf-8")))
    r2 = snapkit.render(occ_a_text, "occlusion.png", "occlusion.snapshot", final=True)
    print("occ A render:", r2.get("ok"), r2.get("status"), r2.get("bytes"))
    r3 = snapkit.render(occ_b_text, "occlusion-alternative.png",
                        "occlusion-alternative.snapshot", final=True)
    print("occ B render:", r3.get("ok"), r3.get("status"), r3.get("bytes"))

    # ------------------------------------------------------------- JSON -----
    jdump("scene-data.json", scene)
    jdump("occlusion-scene-data.json", A.occ_scene_data(occ_a_text, occ_b_text))

    questions, answers = A.compute_questions(scene)
    jdump("questions.json", questions)
    jdump("answers.json", answers)

    eq = build_equivalence(occ_a_text, occ_b_text, tech_a, tech_b)
    jdump("equivalence.json", eq)

    print("\n--- D.warnings() : %d ---" % len(D.warnings()))
    for w in D.warnings():
        print("WARN", w)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def build_equivalence(dsl_a: str, dsl_b: str, tech_a: dict, tech_b: dict) -> dict:
    from PIL import Image, ImageChops

    pa = os.path.join(OUT, "occlusion.png")
    pb = os.path.join(OUT, "occlusion-alternative.png")
    da = os.path.join(OUT, "occlusion.snapshot")
    db = os.path.join(OUT, "occlusion-alternative.snapshot")

    ia = Image.open(pa)
    ib = Image.open(pb)
    ia.load()
    ib.load()
    same_size = ia.size == ib.size
    diff = ImageChops.difference(ia.convert("RGB"), ib.convert("RGB"))
    bbox = diff.getbbox()
    hist = diff.convert("L").histogram()
    nonzero = sum(hist[1:])
    max_delta = max(i for i, v in enumerate(hist) if v > 0) if nonzero else 0
    ba = open(pa, "rb").read()
    bb = open(pb, "rb").read()

    diff_path = os.path.join(TMP, "crops", "occlusion-pixel-diff.png")
    os.makedirs(os.path.dirname(diff_path), exist_ok=True)
    ImageChops.difference(ia.convert("RGB"), ib.convert("RGB")).save(diff_path)

    return {
        "schema_version": 1, "task_id": "A19", "artifact": "occlusion",
        "claim": "两份完整 DSL 的隐藏内容不同、遮挡做法不同，但最终 PNG 的每一个像素都相同。",
        "images": {
            "A": {"png": "occlusion.png", "dsl": "occlusion.snapshot",
                  "mechanism": tech_a,
                  "hidden_bodies": [{"label": h[0], "shape": h[1], "size": h[2],
                                     "color": h[5],
                                     "nominal_bbox": {"x_min": h[3], "y_min": h[4],
                                                       "x_max": h[3] + h[2],
                                                       "y_max": h[4] + h[2]}}
                                    for h in A.O_HIDDEN_A],
                  "hidden_body_count": len(A.O_HIDDEN_A)},
            "B": {"png": "occlusion-alternative.png", "dsl": "occlusion-alternative.snapshot",
                  "mechanism": tech_b,
                  "hidden_bodies": [{"label": h[0], "shape": h[1], "size": h[2],
                                     "color": h[5],
                                     "emitted_bbox": {"x_min": A.O_PARK_X, "y_min": h[4],
                                                      "x_max": A.O_PARK_X + h[2],
                                                      "y_max": h[4] + h[2]},
                                     "nominal_bbox": {"x_min": h[3], "y_min": h[4],
                                                       "x_max": h[3] + h[2],
                                                       "y_max": h[4] + h[2]}}
                                    for h in A.O_HIDDEN_B],
                  "hidden_body_count": len(A.O_HIDDEN_B)},
        },
        "hidden_content_differs": {
            "counts": [len(A.O_HIDDEN_A), len(A.O_HIDDEN_B)],
            "per_position": [
                {"cover": "遮挡物 1",
                 "A": [{"shape": h[1], "size": h[2], "color": h[5]}
                       for h in A.O_HIDDEN_A if h[4] < 380],
                 "B": [{"shape": h[1], "size": h[2], "color": h[5]}
                       for h in A.O_HIDDEN_B if h[4] < 380]},
                {"cover": "遮挡物 2",
                 "A": [{"shape": h[1], "size": h[2], "color": h[5]}
                       for h in A.O_HIDDEN_A if h[4] >= 380],
                 "B": [{"shape": h[1], "size": h[2], "color": h[5]}
                       for h in A.O_HIDDEN_B if h[4] >= 380]},
            ],
            "summary": "A 有 5 个隐藏主体、B 有 6 个；每个位置的形状、尺寸、颜色与"
                       "场景中的名义位置都不同；遮挡做法一个是绘制顺序覆盖，一个是裁剪移除。",
        },
        "hashes": {
            "occlusion.png": {"sha256": hashlib.sha256(ba).hexdigest(),
                              "bytes": len(ba),
                              "mode": ia.mode, "size": list(ia.size)},
            "occlusion-alternative.png": {"sha256": hashlib.sha256(bb).hexdigest(),
                                          "bytes": len(bb),
                                          "mode": ib.mode, "size": list(ib.size)},
            "png_sha256_equal": hashlib.sha256(ba).hexdigest() == hashlib.sha256(bb).hexdigest(),
            "occlusion.snapshot": {"sha256": sha256_file(da),
                                   "bytes": os.path.getsize(da)},
            "occlusion-alternative.snapshot": {"sha256": sha256_file(db),
                                               "bytes": os.path.getsize(db)},
        },
        "pixel_comparison": {
            "method": "PIL ImageChops.difference on the two raw service responses "
                      "(no resizing, no colour management, no post-processing)",
            "same_dimensions": same_size,
            "dimensions": list(ia.size),
            "total_pixels": ia.size[0] * ia.size[1],
            "differing_pixels": nonzero,
            "differing_pixel_ratio": nonzero / float(ia.size[0] * ia.size[1]),
            "max_channel_delta": max_delta,
            "difference_bbox": bbox,
            "difference_image": os.path.relpath(diff_path, ROOT).replace("\\", "/"),
            "pixel_identical": bool(same_size and nonzero == 0),
        },
        "dsl_difference": {
            "dsl_sha256_equal": sha256_file(da) == sha256_file(db),
            "dsl_bytes": [os.path.getsize(da), os.path.getsize(db)],
            "why_they_differ": "隐藏主体列表、绘制顺序与遮挡机制都不同（见 images.A/B.mechanism）",
        },
        "proof_obligation": [
            "A1：若任一遮挡矩形没有完全覆盖其下的隐藏主体，残留像素会让 A 与 B 不同。",
            "B1：隐藏主体在 Stack 中排在最后；若无 ClipRect 生效，它们会盖在遮挡物上，"
            "A 与 B 必然不同。",
            "两图逐字节相同 ⇒ 覆盖完整且裁剪生效，两种遮挡做法都成立。",
        ],
        "hidden_counts_not_used_as_answers": True,
        "generated_at": datetime.now(CST).isoformat(timespec="seconds"),
    }


if __name__ == "__main__":
    main()