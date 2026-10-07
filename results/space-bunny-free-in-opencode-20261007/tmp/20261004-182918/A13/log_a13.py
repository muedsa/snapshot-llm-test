# -*- coding: utf-8 -*-
"""A13 wrap-up: log the real iteration chain, build task-metrics.json and update
the suite state.  Timestamps and image paths are pulled from requests.jsonl so
nothing here is invented."""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import state as S  # noqa: E402
import wrapup  # noqa: E402

TASK = "A13"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
CST = timezone(timedelta(hours=8))

rows = [json.loads(l) for l in open(os.path.join(TMP, "requests.jsonl"), encoding="utf-8")
        if l.strip()]
renders = [r for r in rows if r["request_type"] == "render"]


def by_dsl(fragment, rid=None):
    """Resolve the render request for an iteration entry, by request id when
    given, otherwise by the request file path fragment."""
    if rid:
        for r in renders:
            if r["request_id"] == rid:
                return r
        raise KeyError(rid)
    for r in renders:
        rf = (r.get("request_file") or "").replace("\\", "/")
        if rf.endswith(fragment):
            return r
    raise KeyError(fragment)


def img(abs_path):
    return abs_path


def ts(r):
    return r["started_at"] if r else None


# (version, parent, kind, dsl fragment, viewed image, observed, changes, complete,
#  explicit request id when the same DSL text was submitted more than once)
CHAIN = [
    ("A13-v01", None, "baseline", "probes/probe-alpha.snapshot", None,
     None,
     "probe 1: 512-grid transparent canvas with a rounded rect, ClipOval circle, "
     "shape=CIRCLE, a TOP_CENTER gradient and a ClipRRect - to prove the alpha "
     "channel and the shape/gradient spellings before drawing the mark",
     False, "A13-req-016"),
    ("A13-v02", "A13-v01", "syntax-fix", "probes/probe-alpha.snapshot",
     None,
     "service returned 400 PARSE_ERROR 'Attr [gradientBegin] value format error'; "
     "the guessed value CENTER_TOP does not exist",
     "read reference/enums/ and switched to TOP_CENTER / BOTTOM_CENTER; re-rendered",
     False, "A13-req-016"),
    ("A13-v03", "A13-v02", "baseline", "probes/probe-alpha.snapshot",
     "probe-alpha.png",
     "alpha range is a real 0..255 channel (corner alpha=0), all five primitives "
     "render: rounded rect, ClipOval circle, shape=CIRCLE circle, vertical "
     "gradient, ClipRRect",
     "transparent background is usable with background=#00000000; proceed to the "
     "two direction previews", False, "A13-req-019"),
    ("A13-v04", "A13-v03", "alternative", "preview/direction-A.snapshot",
     "preview/direction-A.png",
     "direction A (交叠光核): two rounded plates offset on the diagonal, the "
     "overlap redrawn as a lit core. Reads as a distinctive layered block",
     "kept both previews in the temp dir as TASK.md requires", False),
    ("A13-v05", "A13-v04", "alternative", "preview/direction-B.snapshot",
     "preview/direction-B.png",
     "direction B (阶光栅): three parallel bars crossed by a vertical beam. On "
     "looking at it, it reads as a menu icon plus a stray bar; the beam does not "
     "actually pass through the layers",
     "chose A; B kept as the documented alternative in brand-system.json", False),
    ("A13-v06", "A13-v05", "visual", "preview/v03-amber/symbol-color.snapshot",
     "preview/v03-amber/symbol-color.png",
     "first refinement of A: solid amber core, r86, o92. Strong triad, but the core "
     "is invisible in the mono version",
     "kept the amber core for the colour variant, moved on to test the mono version",
     False),
    ("A13-v07", "A13-v06", "alternative", "preview/v04b-inset/symbol-color.snapshot",
     "preview/v04b-inset/symbol-color.png",
     "inset the core by 20 with its own radius 44 to create a clearing channel; "
     "on looking at it the core floats and the cyan ring around it is uneven - "
     "rejected",
     "returned to an exact (A u B) - square decomposition", False),
    ("A13-v08", "A13-v07", "visual", "preview/v05-void/symbol-color.snapshot",
     "preview/v05-void/symbol-color.png",
     "core turned into a void: 6 rects, void keeps the overlap's own TL/BR arcs. "
     "The two quarter-disc fillers read as odd floating quarter moons",
     "dropped the fillers and used a sharp square window", False),
    ("A13-v09", "A13-v08", "visual", "preview/v06-sharpvoid/symbol-color.snapshot",
     "preview/v06-sharpvoid/symbol-color.png",
     "sharp square void (4 rects) reads clean, but with o92 the void is 53% of the "
     "ink span and the mark looks like a generic window frame",
     "increased the offset so the plates cross less and the void shrinks", False),
    ("A13-v10", "A13-v09", "alternative", "preview/candidates.snapshot",
     "preview/candidates.png",
     "rendered six candidate geometries in one sheet and compared them side by "
     "side instead of guessing; C3 (r60, o150) keeps a readable window while "
     "reading clearly as two crossing sheets",
     "froze plate=300, radius=60, offset=150, origin=6, sharp square void", False),
    ("A13-v11", "A13-v10", "visual", "preview/v08-c3/symbol-color.snapshot",
     "preview/v08-c3/symbol-color.png",
     "frozen geometry rendered; alpha scan found a 1px seam at the leg junction "
     "(alpha 193/255) and the measured ink was 451px instead of 398 - emit() was "
     "recomputing its own scale instead of using the one fitted() returned",
     "fixed emit() to take k from fitted()", False),
    ("A13-v12", "A13-v11", "visual", "preview/v09-fixed/symbol-color.snapshot",
     "preview/v09-fixed/symbol-color.png",
     "ink bbox now 400x398 with 56/57px clearspace; the scan at y=400 still shows "
     "an unfixed junction on the lower leg",
     "added a 1-device-pixel pad to the lower leg as well", False),
    ("A13-v13", "A13-v12", "visual", "preview/v10-noseam/symbol-black.snapshot",
     "preview/v10-noseam/magnified/svc-check-black-32x32.png",
     "no seams left on any scanned line; the 32x32 mono render now shows the "
     "silhouette and the ~9px window, so the mark works in one ink",
     "promoted this geometry to the delivered mark", False),
    ("A13-v14", "A13-v13", "visual", "A13/symbol-color.snapshot",
     "symbol-color.png",
     "delivered 512 colour and mono symbols re-rendered from the frozen geometry; "
     "alpha masks differ in 91px with max delta 1, mono RGB is 0 wherever alpha>0",
     "accepted as the final symbols", True),
    ("A13-v15", "A13-v14", "visual", "A13/brand-banner.snapshot",
     "brand-banner.png",
     "banner rendered; the mono-on-dark mark on the violet panel shows the panel "
     "through its window, both required strings are present and nothing collides",
     "accepted", True),
    ("A13-v16", "A13-v15", "visual", "A13/launch-poster.snapshot",
     "launch-poster.png",
     "first poster render; 叠光 and Layerlight were only ~15px apart and the "
     "capability row crowded the tagline",
     "moved the wordmark stack down and rebalanced the lower third", False),
    ("A13-v17", "A13-v16", "visual", "A13/launch-poster.snapshot",
     "launch-poster.png",
     "re-rendered poster: the stack now breathes, all three required strings are "
     "present, and the three mark instances (52/420/96) read correctly",
     "accepted as the final poster", True),
    ("A13-v18", "A13-v17", "visual", "preview/final/checksize/thumb-color-32x32.snapshot",
     "preview/final/thumb32-check.png",
     "final check sheet: the delivered 512 files downscaled to 32 and the mark "
     "rendered directly at 32 are indistinguishable in silhouette and window",
     "task complete", True),
]

iters = []
for entry in CHAIN:
    v, par, kind, frag, viewed_img, obs, chg, complete = entry[:8]
    rid = entry[8] if len(entry) > 8 else None
    r = by_dsl(frag, rid)
    imgp = None
    if viewed_img:
        imgp = viewed_img if os.path.isabs(viewed_img) else os.path.normpath(
            os.path.join(OUT, viewed_img)) if viewed_img.startswith("..") else \
            os.path.normpath(os.path.join(TMP, viewed_img))
    dslp = (r or {}).get("request_file")
    iters.append((v, par, kind, dslp, imgp, ts(r), obs, chg, complete))

started = rows[0]["started_at"] if rows else None
first_img = next((r["started_at"] for r in renders
                  if (r.get("content_type") or "").startswith("image/")), None)
ended = datetime.now(CST).isoformat(timespec="milliseconds")


def rel(p):
    return os.path.relpath(p, OUT) if p else None


artifacts = [
    "symbol-color.png (512x512 RGBA, 4883 bytes, service response bytes verbatim)",
    "symbol-color.snapshot (1229 bytes, the exact DSL submitted for that PNG)",
    "symbol-black.png (512x512 RGBA, 3576 bytes, service response bytes verbatim)",
    "symbol-black.snapshot (1229 bytes, the exact DSL submitted for that PNG)",
    "brand-banner.png (1200x400 RGBA, 35307 bytes, service response bytes verbatim)",
    "brand-banner.snapshot (2592 bytes, the exact DSL submitted for that PNG)",
    "launch-poster.png (1080x1350 RGBA, 71945 bytes, service response bytes verbatim)",
    "launch-poster.snapshot (6893 bytes, the exact DSL submitted for that PNG)",
    "brand-system.json (15430 bytes, generated from layerlight.MARK + verify/report.json)",
    "rationale.md (299 non-whitespace characters, CJK 200)",
    "snapshot-usage.md",
    "task-metrics.json",
]

visual_evidence = [
    "probes/probe-alpha.png 看过：确认真实 alpha 通道与 5 种图元写法",
    "preview/direction-A.png 与 preview/direction-B.png 都实际打开看过，据此选定 A",
    "preview/candidates.png 一次渲染 6 个候选几何并逐个对比后冻结参数",
    "preview/v03-amber / v04b-inset / v05-void / v06-sharpvoid / v08-c3 / v09-fixed / "
    "v10-noseam 的 symbol-color.png 与放大后的 32x32 单色图都实际看过",
    "zoom-center.png（512 彩色图标中心 2× 放大）确认无发丝缝",
    "outputs/A13/symbol-color.png、symbol-black.png、brand-banner.png、launch-poster.png "
    "四张最终图全部用 read 工具实际打开看过",
    "crops/brand-banner-banner-mark.png（3×）与 crops/launch-poster-poster-hero.png、"
    "poster-topbar.png（4×）、poster-card.png（2.6×）局部放大核对",
    "preview/final/thumb32-check.png：32x32 服务端直渲 vs 交付图缩略，14× 放大实际看过",
    "verify/report.json：16 项像素级检查全部 PASS（含 alpha 遮罩一致性、黑版 RGB=0、"
    "跨应用 void/ink 比例、留白、必需文案、无 <Image>）",
]

unresolved = [
    "彩色与黑版的 alpha 遮罩有 91px、最大差 1 的差异，来自 Skia 两次独立光栅化的舍入，"
    "不是设计差异；容差与数字已写入 verify/report.json。",
    "token / 费用 / 图像输入用量：服务未提供任何计量接口，本次也没有可信平台数据，"
    "全部保持 null，未按字数或字节估算。",
    "rate_limit_or_queue_wait_seconds 记 null：本次响应头未出现 queue 段，无法确认为 0。",
    "只验证到 32px；低于 32px 未测试，也未在交付物中声称可用。",
    "D.warnings() 全程为空，属主动用 est_width() 预留宽度后的规避，未验证静默溢出行为。",
]

notes = ("方向选择与两次关键修正（emit() 缩放 bug、同色腿 1px 缝）都有真实证据；"
         "标志几何由 layerlight.build_mark()/emit() 单一来源生成，4 个交付件与所有检查图"
         "共用同一套 4 腿分解，无任何外部图片嵌入。")

# iterations.jsonl is generated by this script. The first wrapup call wrote one
# entry (v03) whose DSL lookup missed the successful re-render of the same DSL
# text, leaving dsl_file/viewed_at null. Regenerate the whole chain once so the
# log has no null fields; requests.jsonl keeps the untouched request trace.
IPATH = os.path.join(TMP, "iterations.jsonl")
if os.path.exists(IPATH):
    import json as _json
    lines = [_json.loads(l) for l in open(IPATH, encoding="utf-8") if l.strip()]
    if all(l.get("task_id") == TASK for l in lines):
        with open(os.path.join(TMP, "iterations-regenerated.json"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write("the first wrapup run of A13 produced these lines; they were\n"
                     "regenerated by log_a13.py on the next run because entry v03\n"
                     "had a null dsl_file/viewed_at (DSL lookup missed the successful\n"
                     "re-render of the identical DSL text, request A13-req-019).\n\n")
            for l in lines:
                fh.write(json.dumps(l, ensure_ascii=False) + "\n")
        os.remove(IPATH)
        print("archived the first iterations.jsonl to iterations-regenerated.json")
    else:
        raise SystemExit("iterations.jsonl holds foreign entries; refusing to touch it")

m = wrapup.wrapup(TASK, started, first_img, ended, iters, artifacts, visual_evidence,
                  unresolved=unresolved, notes=notes, status="completed",
                  rounds=["round-01"])
print(json.dumps({"iterations": len(iters),
                  "render_requests": m["counts"]["render_requests"],
                  "successful_renders": m["counts"]["successful_render_requests"],
                  "failed_renders": m["counts"]["failed_render_requests"],
                  "image_views": m["counts"]["image_views"],
                  "complete_visual_iterations": m["counts"]["completed_visual_iterations"],
                  "final_pngs": m["counts"]["final_pngs"],
                  "wall_clock_seconds_total": m["wall_clock_seconds_total"],
                  "sum_of_request_durations_seconds": m["sum_of_request_durations_seconds"],
                  "token": m["usage"]["input_tokens"],
                  "cost": m["usage"]["cost"]}, ensure_ascii=False, indent=2))
print("metrics ->", os.path.join(OUT, "task-metrics.json"))