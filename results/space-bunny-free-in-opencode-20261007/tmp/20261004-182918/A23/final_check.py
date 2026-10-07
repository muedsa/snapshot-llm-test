"""A23 final gate: verify every TASK.md / task.json deliverable from the files on disk."""
from __future__ import annotations

import hashlib
import json
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A23")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A23")
TASKJSON = json.load(open(os.path.join(ROOT, "tasks", "A23-capability-delivery", "task.json"),
                           encoding="utf-8"))
fails = []


def ck(cond, label, detail=""):
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", label,
                           ("  -- " + detail) if detail else ""))
    if not cond:
        fails.append(label)


print("=== 1. required_outputs from task.json ===")
for spec in TASKJSON["required_outputs"]:
    png_p = os.path.join(OUT, spec["filename"])
    dsl_p = os.path.join(OUT, spec["dsl"])
    ok_png = os.path.exists(png_p)
    ok_dsl = os.path.exists(dsl_p)
    ck(ok_png and ok_dsl, "%s + %s exist" % (spec["filename"], spec["dsl"]))
    if not ok_png:
        continue
    im = Image.open(png_p)
    ck([im.width, im.height] == [spec["width"], spec["height"]],
       "  %s is %dx%d" % (spec["filename"], spec["width"], spec["height"]),
       "actual %dx%d" % (im.width, im.height))
    ck(im.format == "PNG", "  %s is a real PNG" % spec["filename"], im.format)
    ck(open(dsl_p, encoding="utf-8").read().lstrip().startswith("<Snapshot"),
       "  %s is Snapshot DSL" % spec["dsl"])

print("\n=== 2. additional_outputs + common_outputs ===")
for name in TASKJSON["additional_outputs"] + TASKJSON["common_outputs"]:
    p = os.path.join(OUT, name)
    ck(os.path.exists(p) and os.path.getsize(p) > 0, "%s exists and non-empty" % name,
       "%d B" % (os.path.getsize(p) if os.path.exists(p) else 0))

print("\n=== 3. no fake target-format files ===")
forbidden = [".gif", ".svg", ".webp", ".tif", ".tiff", ".pdf", ".jpg", ".jpeg", ".apng"]
bad = [f for f in os.listdir(OUT) if os.path.splitext(f)[1].lower() in forbidden]
ck(not bad, "no .gif/.svg/.webp/.tif/.pdf/.jpg/.apng in the delivery", str(bad))

print("\n=== 4. transparency / opacity ===")
im = Image.open(os.path.join(OUT, "cover.png")).convert("RGBA")
ck(all(im.getpixel(p)[3] == 255 for p in
       [(0, 0), (1199, 0), (0, 799), (1199, 799)]),
   "cover.png corners fully opaque (RGB cover)")
for k in range(1, 7):
    im = Image.open(os.path.join(OUT, "frame-%02d.png" % k)).convert("RGBA")
    corners = [im.getpixel(p)[3] for p in
               [(0, 0), (599, 0), (0, 599), (599, 599)]]
    ck(all(a == 0 for a in corners), "frame-%02d.png four corners alpha=0" % k, str(corners))

print("\n=== 5. frame invariants (from the delivered DSL) ===")
geo, units, texts, images, bboxes = set(), [], [], [], []
for k in range(1, 7):
    t = open(os.path.join(OUT, "frame-%02d.snapshot" % k), encoding="utf-8").read()
    units.append(t.count("borderRadius="))
    texts.append(t.count("<Text"))
    images.append(t.count("<Image"))
    geo.add(tuple(sorted(set(__import__("re").findall(
        r'<Container width="([\d.]+)" height="([\d.]+)"', t)))))
    im = Image.open(os.path.join(OUT, "frame-%02d.png" % k)).convert("RGBA")
    bboxes.append(im.getchannel("A").getbbox())
ck(units == [12] * 6, "exactly 12 unit nodes in every frame", str(units))
ck(texts == [0] * 6, "no Text node in any frame", str(texts))
ck(images == [0] * 6, "no Image node in any frame", str(images))
ck(len(geo) == 1, "unit geometry identical across all 6 frames", str(sorted(geo)[0]))
ck(all(bboxes[i][2] - bboxes[i][0] < bboxes[i - 1][2] - bboxes[i - 1][0] for i in range(1, 6)),
   "non-transparent bbox width shrinks every frame",
   " ".join("%d" % (b[2] - b[0]) for b in bboxes))
ck(all(bboxes[i][3] - bboxes[i][1] < bboxes[i - 1][3] - bboxes[i - 1][1] for i in range(1, 6)),
   "non-transparent bbox height shrinks every frame",
   " ".join("%d" % (b[3] - b[1]) for b in bboxes))

print("\n=== 6. timing.json contract ===")
tm = json.load(open(os.path.join(OUT, "timing.json"), encoding="utf-8"))
ck(tm["playback"]["duration_per_frame_ms"] == 250, "250 ms per frame")
ck(tm["playback"]["total_duration_ms"] == 1500, "total 1500 ms")
ck(tm["playback"]["playback_mode"] == "loop", "loop playback declared")
ck(len(tm["playback"]["frame_order"]) == 6, "6 frames in order",
   str(tm["playback"]["frame_order"]))
ck(tm["loop_seam"]["seamless"] is False, "seam honestly declared non-seamless")
ck(len(tm["loop_seam"]["why_a_seamless_loop_is_impossible_here"]) > 0,
   "seamlessness impossibility argued")
ck(all(f["duration_ms"] == 250 for f in tm["per_frame_timing"]), "every frame 250 ms")

print("\n=== 7. frame-data.json ===")
fd = json.load(open(os.path.join(OUT, "frame-data.json"), encoding="utf-8"))
ck(len(fd["frames"]) == 6, "6 frame records")
ck(all(len(f["units"]) == 12 for f in fd["frames"]), "12 units recorded per frame")
REQUIRED_UNIT_KEYS = ["unit_id", "role", "color_hex", "size_w_h", "center_x", "center_y",
                      "positioned_left", "positioned_top", "rotation_matrix_deg",
                      "distance_from_canvas_center", "step_from_previous_frame_px",
                      "rotation_step_from_previous_deg", "start_center", "end_center",
                      "path_control_point", "path_bend_factor"]
missing = {k for f in fd["frames"] for u in f["units"] for k in REQUIRED_UNIT_KEYS
           if k not in u}
ck(not missing, "each unit records coordinates + rotation + state",
   "missing keys: %s" % sorted(missing))
ck(all("step_from_previous_frame_px" in u for f in fd["frames"] for u in f["units"]),
   "every unit has a per-frame step field")
ck(fd["invariants_held_in_every_frame"]["unit_geometry_identical_across_all_frames"],
   "frame-data asserts scale consistency")

print("\n=== 8. limitations.md ===")
lm = open(os.path.join(OUT, "limitations.md"), encoding="utf-8").read()
for kw in ["文字可编辑 SVG", "CMYK", "GIF", "PNG 封面", "不支持", "替代",
           "仍需外部后续工作", "PARSE_ERROR"]:
    ck(kw in lm, "limitations.md mentions %r" % kw)
ck("gif" not in [os.path.splitext(f)[1].lower() for f in os.listdir(OUT)],
   "no .gif produced")

print("\n=== 9. every PNG has a same-named DSL and vice versa ===")
pngs = sorted(os.path.splitext(f)[0] for f in os.listdir(OUT) if f.endswith(".png"))
dsls = sorted(f[:-len(".snapshot")] for f in os.listdir(OUT) if f.endswith(".snapshot"))
ck(pngs == dsls, "PNG stems == DSL stems", str(set(pngs) ^ set(dsls)))
DRAFTS = os.path.join(TMP, "drafts")
draft_files = [f for f in os.listdir(DRAFTS) if f.endswith(".snapshot")]
for stem in pngs:
    matches = [f for f in draft_files if f.endswith("-%s.snapshot" % stem)]
    if not matches:
        ck(False, "a draft exists for %s" % stem)
        continue
    a = open(os.path.join(DRAFTS, matches[0]), "rb").read()
    b = open(os.path.join(OUT, stem + ".snapshot"), "rb").read()
    ck(a == b, "draft == delivered DSL for %s" % stem)

print("\n=== 10. trace files ===")
for f in ["requests.jsonl", "iterations.jsonl", "probe_format.py", "probe_semantics.py",
          "build_a23.py", "emit_a23.py", "log_a23.py", "fonts-list.txt",
          "drafts/README.md"]:
    ck(os.path.exists(os.path.join(TMP, f)), "temp file %s" % f)
ck(len([f for f in os.listdir(os.path.join(TMP, "docs"))]) == 6, "6 fetched documents")
ck(len([f for f in os.listdir(os.path.join(TMP, "responses"))]) == 4,
   "4 failed responses preserved",
   str(len(os.listdir(os.path.join(TMP, "responses")))))
n_drafts = len([f for f in os.listdir(DRAFTS) if f.endswith(".snapshot")])
ck(n_drafts == 9, "9 numbered drafts (v00 reconstructed + v01..v08)", str(n_drafts))
m = json.load(open(os.path.join(OUT, "task-metrics.json"), encoding="utf-8"))
ck(m["usage"]["input_tokens"] is None and m["usage"]["cost"] is None,
   "token/cost honestly null")
ck(m["wall_clock_seconds_total"] > m["sum_of_request_durations_seconds"],
   "wall clock != sum of request durations")
ck(m["counts"]["final_pngs"] >= 7, "at least the 7 required PNGs")

print("\n" + "=" * 62)
print("RESULT: %s   (%d checks failed)" % ("ALL PASS" if not fails else "FAILURES", len(fails)))
for f in fails:
    print("  FAILED:", f)
sys.exit(1 if fails else 0)
