"""A19 wrap-up: log the real iteration sequence, build task-metrics.json, update suite state.

Every viewed_at timestamp is the wall-clock time of an image read that actually happened
in this session; every "observed issue" was seen in the image named in image_file.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A19"
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import wrapup  # noqa: E402

STARTED = "2026-10-05T02:09:22+08:00"
FIRST_IMAGE = "2026-10-05T02:31:41+08:00"
ENDED = "2026-10-05T03:12:40+08:00"


def p(*a):
    return os.path.join(TMP, *a)


def o(*a):
    return os.path.join(OUT, *a)


ITERS = [
    # ---- v01 baseline: first render of all three figures ------------------------
    ("A19-v01", None, "baseline",
     p("drafts", "grid-scene.snapshot"), o("grid-scene.png"),
     "2026-10-05T02:32:30+08:00",
     "首版三图全部渲染成功（A19-req-004/005/006）。grid-scene.png 整图查看：64 格、"
     "G01–G64 编号、图例、C1–C8 / R1–R8 行列标、四色四形三档都成立；"
     "occlusion.png 整图查看：两块遮挡物正常，但左下角大片空白，且没有任何「部分被遮挡」的"
     "主体，导致「完全可见」这个判据太容易、诊断价值不足。",
     "本版只做基线，不改构图；记录观察结果作为后续视觉迭代的对照。",
     True),
    # ---- v02: occlusion layout rework ------------------------------------------
    ("A19-v02", "A19-v01", "visual",
     p("drafts", "occlusion-A1-overdraw.snapshot"), o("occlusion.png"),
     "2026-10-05T02:45:30+08:00",
     "按 v01 的观察重排遮挡场景后查看：构图平衡了（V1/V2、V3/V4 两排可见主体 + 左下证据清单 + "
     "P1 与遮挡物 2 交界）。但 equivalence.json 报出 2801 个差异像素、"
     "difference_bbox=(350,458,390,548)，正落在 P1 区域——clip 变体里遮挡物排在可见主体之前，"
     "P1 被压住的右半截反而画在了遮挡物上面。",
     "工作区卡片 40,126,720,512；两块遮挡物改到 350,168 与 350,404，各 278×222；"
     "新增部分遮挡主体 P1（橙色圆环 96px，右侧 42px 在遮挡物 2 之下）；"
     "左下新增「可见证据清单」小卡；隐藏内容改为 A=5 个 / B=6 个。",
     False),
    # ---- v03: fix the clip variant's draw order --------------------------------
    ("A19-v03", "A19-v02", "syntax-fix",
     p("drafts", "occlusion-B1-clip.snapshot"), o("occlusion-alternative.png"),
     "2026-10-05T02:47:05+08:00",
     "把两个变体都改成「可见主体 → 遮挡物」在最后绘制，隐藏主体仍排在遮挡物之后（A19-req-012）。"
     "复验：differing_pixels=0、difference_bbox=None、两图 sha256 相同。"
     "同时 D.warnings() 报出 2 条文字溢出：证据清单第三行估算宽度 192.5px > 盒宽 186px。",
     "遮挡物在两个变体里都移到最后绘制（B1 的隐藏主体仍排在遮挡物之后，证明力更强）；"
     "证据清单第三行改写为「· P1 被遮挡物 2 压住 42 px」。",
     True),
    # ---- v04: warnings clean, occlusion final ---------------------------------
    ("A19-v04", "A19-v03", "visual",
     p("drafts", "occlusion-A1-overdraw.snapshot"), o("occlusion.png"),
     "2026-10-05T02:50:20+08:00",
     "重渲染后 D.warnings() 归零。整图查看 occlusion.png：V1–V4 完整可见、P1 被遮挡物 2 "
     "干净切断、证据清单三行可读、两块遮挡物内只有填充色与自己的标题；页面无虚线、无半透明。",
     "本版作为遮挡场景定稿；同时再渲一次 occlusion-alternative.png 确认两图仍逐字节相同。",
     True),
    # ---- v05: zoom inspection of the occlusion boundary ------------------------
    ("A19-v05", "A19-v04", "visual",
     o("occlusion.snapshot"), p("crops", "crop-p1.png"),
     "2026-10-05T02:52:40+08:00",
     "3× 放大 P1 与遮挡物 2 的交界：橙色圆环被干净利落地切断，交界处没有残影、没有半透明边、"
     "没有虚线轮廓，遮挡物内部像素均匀。",
     "本版无需改动；放大核对确认 P1 的 42px 覆盖量与 occlusion-scene-data.json 记录一致。",
     True),
    # ---- v06: grid detail crops -----------------------------------------------
    ("A19-v06", "A19-v01", "visual",
     o("grid-scene.snapshot"), p("crops", "crop-legend.png"),
     "2026-10-05T02:35:10+08:00",
     "2× 放大图例带：4 个色块 + 蓝/橙/绿/紫、4 个形状 + 圆/方/圆环/圆角方、"
     "尺寸说明 48/64/80 全部可读，没有压字。",
     "本版无需改动。",
     True),
    ("A19-v07", "A19-v06", "visual",
     o("grid-scene.snapshot"), p("crops", "crop-col8.png"),
     "2026-10-05T02:36:00+08:00",
     "2× 放大 C8 列：G08/G16/G24/G32 的形状与编号清晰，圆环内圈是纯白（不是半透明）。",
     "本版无需改动；圆环用格子底色挖内圈的做法在放大后依然干净。",
     True),
    ("A19-v08", "A19-v07", "visual",
     o("grid-scene.snapshot"), p("crops", "crop-bottom.png"),
     "2026-10-05T02:36:40+08:00",
     "1.6× 放大 R8 行与页脚：8 个主体、G57–G64 编号完整，页脚文字没有与最后一格打架。",
     "本版无需改动。",
     True),
    # ---- v09: negative controls prove the equivalence claim is load-bearing -----
    ("A19-v09", "A19-v04", "alternative",
     p("preview", "negative-control", "n1-cover-shrunk.snapshot"),
     p("preview", "negative-control", "n1-cover-shrunk.png"),
     "2026-10-05T03:02:10+08:00",
     "反证探针 N1：把 A1 的遮挡物 1 宽度减少 40px（覆盖失效）。查看后确认隐藏主体 H2/H3 "
     "的蓝/紫**露了出来**；difference_bbox=(402,168,628,390)。"
     "同时 occ_geometry_check() 对这个残缺几何直接抛 AssertionError。",
     "不改动交付图；该探针只落在 tmp/.../preview/negative-control/，"
     "用来证明「覆盖完整」这条论据不是空话。",
     True),
    ("A19-v10", "A19-v09", "alternative",
     p("preview", "negative-control", "n2-clip-widened.snapshot"),
     p("preview", "negative-control", "n2-clip-widened.png"),
     "2026-10-05T03:03:05+08:00",
     "反证探针 N2：把 B1 的 ClipRect 从 700px 放宽到 800px（裁剪失效）。查看后确认 6 个隐藏主体"
     "全部**被画了出来**（散落在遮挡物右侧的空白处）；difference_bbox=(705,196,795,612)。",
     "不改动交付图；证明「隐藏主体确实被 ClipRect 裁掉了」这条论据成立。",
     True),
    ("A19-v11", "A19-v10", "baseline",
     p("preview", "negative-control", "n3-control-overdraw-same.snapshot"),
     p("preview", "negative-control", "n3-control-overdraw-same.png"),
     "2026-10-05T03:04:20+08:00",
     "反证探针 N3：把与交付 A1 完全相同的 DSL 再渲染一次，ImageChops 差异 bbox 为 None，"
     "说明服务渲染是确定性的，「两张图相等」不是因为偶然。",
     "不改动交付图；记录渲染确定性这一前提。",
     True),
    # ---- v12: readability at thumbnail size ------------------------------------
    ("A19-v12", "A19-v08", "visual",
     o("grid-scene.snapshot"), p("thumbs", "grid-scene-800px.png"),
     "2026-10-05T03:08:15+08:00",
     "800px 缩略图查看：64 个编号 G01–G64 全部仍然可读，四色四形仍可区分，"
     "圆环与实心圆在小尺寸下也能分开——放进总画廊的缩略图里仍然可用。",
     "本版无需改动；确认网格图在缩略尺寸下仍然可作答题材料。",
     True),
    # ---- v13: programmatic verification ----------------------------------------
    ("A19-v13", "A19-v12", "requirement-change",
     o("grid-scene.snapshot"), o("verification.json"),
     "2026-10-05T03:10:05+08:00",
     "按 TASK.md「可核验」要求做最终收口：verify_a19.py 完全不读生成器内存状态，"
     "只读 4 份交付 JSON 重算 14 条答案并逐条比对；pixel_audit.py 直接在渲染出的 PNG 上"
     "量 64 个主体的 bbox、16 个圆环的内外径、64 个编号的存在与位置、两块遮挡物内部无泄漏像素。",
     "首轮 verify 有 4 条 FAIL（DSL 文本匹配假设错误）、pixel_audit 有 3 条 FAIL（探针位置与"
     "抗锯齿判定错误）；按真实输出格式重写匹配与探针后，118/118 与 28/28 全部通过。",
     True),
]

ARTIFACTS = [
    "grid-scene.png", "grid-scene.snapshot",
    "occlusion.png", "occlusion.snapshot",
    "occlusion-alternative.png", "occlusion-alternative.snapshot",
    "scene-data.json", "questions.json", "answers.json", "equivalence.json",
    "occlusion-scene-data.json", "verification.json",
    "snapshot-usage.md", "task-metrics.json",
]

VISUAL = [
    "full-figure read of outputs/20261004-182918/A19/grid-scene.png (v01 baseline: 64 cells, "
    "G01-G64 labels, legend, C/R headers, 4 colours x 4 shapes x 3 sizes)",
    "2.0x zoom crop A19/crops/crop-legend.png (legend band: 4 colour chips + 4 shape chips + "
    "size legend)",
    "2.0x zoom crop A19/crops/crop-col8.png (column C8: G08/G16/G24/G32, ring holes are pure white)",
    "1.6x zoom crop A19/crops/crop-bottom.png (row R8 plus footer, G57-G64 all legible)",
    "full-figure read of outputs/20261004-182918/A19/occlusion.png (v01: works but the lower-left "
    "is empty and no body is partially covered)",
    "full-figure read of outputs/20261004-182918/A19/occlusion.png (v02 after the layout rework; "
    "the 2801-pixel diff bbox pointed at P1)",
    "full-figure read of outputs/20261004-182918/A19/occlusion.png (v04 final: V1-V4 fully visible, "
    "P1 clipped, evidence checklist, no dashed or semi-transparent leakage)",
    "full-figure read of outputs/20261004-182918/A19/occlusion-alternative.png (final: visually "
    "identical to occlusion.png)",
    "3.0x zoom crop A19/crops/crop-p1.png (P1 / cover 2 boundary: clean cut, no ghosting)",
    "full-figure read of A19/preview/negative-control/n1-cover-shrunk.png (N1: hidden bodies leak "
    "out when the cover is 40px too narrow)",
    "full-figure read of A19/preview/negative-control/n2-clip-widened.png (N2: all six hidden bodies "
    "appear when the ClipRect is widened to 800px)",
    "full-figure read of A19/preview/negative-control/n3-control-overdraw-same.png (N3: re-rendering "
    "the identical A1 DSL reproduces the identical PNG)",
    "800px-wide thumbnail read of A19/thumbs/grid-scene-800px.png (all 64 ids still legible at "
    "gallery size)",
]

UNRESOLVED = [
    "token / image-input usage / cost are unknown: the anonymous open-snapshot service exposes "
    "no billing or usage endpoint and the chat platform reported no per-request figures, so "
    "every usage field in task-metrics.json is null instead of estimated",
    "rate-limit or queue wait is unknown (null): none of the 24 render responses reported a queue "
    "segment in Server-Timing (only render;dur and total;dur), so it is not recorded as 0",
    "TASK.md says 'the numbering must be >=18' while also asking for exactly 12 grid questions and "
    "2 occlusion questions (14 total). I read it as 'question ids start at 18' and numbered them "
    "Q18-Q31; the alternative reading ('at least 18 questions') would contradict the explicit "
    "12+2 instruction. Documented in snapshot-usage.md section 7",
    "the ring hole is drawn by filling the ring container with the opaque cell colour rather than "
    "by a real transparent hole (the service exposes no ring path / shape=CIRCLE+stroke combo); "
    "visually and geometrically indistinguishable because cells are flat #FFFFFF and a ring never "
    "overlaps anything, and the pixel audit confirms the hole centre is pure white",
    "Q29's x threshold of 900 sits only 15px from the nearest column centre (915). Column centres "
    "are on a 190px lattice so any reasonable measurement error is far below 15px, but this is the "
    "tightest of the seven comparison questions; the others have margins of 950 / 25.39 / 84.29 px "
    "or a total-order key",
    "occlusion-scene-data.json and verification.json are two extra JSON files beyond the four "
    "TASK.md names; they exist so a third party can re-check the hidden content and the 118+28 "
    "verification items, and they replace nothing",
    "no service error occurred at all: 24/24 renders returned 200 image/png, no 4xx, no 429, no "
    "retryable 503",
]

NOTES = ("A19 constructs its own verifiable test material. grid-scene.png (1600x1600) is an 8x8 grid "
         "of 64 numbered bodies G01-G64 generated from seed 20261004 with hard assertions on every "
         "TASK.md distribution rule (4 colours x16, 4 shapes x16, every row >=3 colours and >=3 "
         "shapes, ring outer=size / inner=size/2, id label outside the body). occlusion.png and "
         "occlusion-alternative.png are two byte-identical 800x800 renders (same sha256, 0/640000 "
         "differing pixels) whose DSLs hide 5 vs 6 bodies and use two different mechanisms: A1 "
         "overdraw (painted then covered by opaque rectangles) and B1 clip (bodies placed after the "
         "covers inside a 700px ClipRect, emitted at x=706, removed before rasterisation). Three "
         "negative-control renders prove the equivalence claim is load-bearing. 14 questions "
         "(Q18-Q31, 7 two-step) cover composite retrieval, strict centre left/right, distance, "
         "ordering, bounding box and colour/shape counting; Q31's ground truth is the literal string "
         "undeterminable, and the hidden body counts are never used as an answer. "
         "verify_a19.py re-derives all 14 answers from the delivered scene-data.json (118/118 checks) "
         "and pixel_audit.py measures the rendered PNGs (28/28 checks).")


def main():
    m = wrapup.wrapup(TASK, STARTED, FIRST_IMAGE, ENDED, ITERS, ARTIFACTS, VISUAL,
                      unresolved=UNRESOLVED, notes=NOTES, status="completed",
                      rounds=["round-01"], cases=[])
    print(json.dumps({k: m[k] for k in ("wall_clock_seconds_total",
                                        "wall_clock_seconds_to_first_usable_image",
                                        "counts", "failures")},
                     ensure_ascii=False, indent=2))
    # attach the A19-specific extras that finalize.py has no field for
    p = os.path.join(OUT, "task-metrics.json")
    with open(p, encoding="utf-8") as fh:
        d = json.load(fh)
    d["verification"] = {
        "json_and_dsl_checks": {"script": "tmp/20261004-182918/A19/verify_a19.py",
                                "passed": 118, "total": 118,
                                "report": "outputs/20261004-182918/A19/verification.json"},
        "pixel_checks": {"script": "tmp/20261004-182918/A19/pixel_audit.py",
                         "passed": 28, "total": 28,
                         "report": "tmp/20261004-182918/A19/pixel-audit.json"},
        "negative_controls": {
            "script": "tmp/20261004-182918/A19/negative_control.py",
            "report": "tmp/20261004-182918/A19/negative-control.json",
            "probes": 3, "all_behaved_as_claimed": True},
        "dsllib_text_warnings_per_render": 0,
        "note": "the two 2-item warnings during v03 were a text overflow in the occlusion evidence "
                "checklist and were fixed before the delivered renders; the delivered runs report 0",
    }
    d["questions"] = {
        "total": 14, "grid": 12, "occlusion": 2,
        "id_range": "Q18..Q31",
        "two_step_relations": 7,
        "types_covered": ["composite_attribute_retrieval", "strict_center_horizontal_relation",
                          "distance", "ordering", "bounding_box", "color_counting",
                          "shape_counting", "occlusion_visible_count",
                          "occlusion_information_insufficient"],
        "answers_undeterminable": 1,
        "hidden_body_count_used_as_an_answer": False,
    }
    d["artifacts_note"] = {
        "final_pngs": 3,
        "png_sha256": {},
    }
    import hashlib
    for n in ("grid-scene.png", "occlusion.png", "occlusion-alternative.png"):
        h = hashlib.sha256(open(os.path.join(OUT, n), "rb").read()).hexdigest()
        d["artifacts_note"]["png_sha256"][n] = h
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("task-metrics.json extended with verification/questions/artifacts blocks")


if __name__ == "__main__":
    main()
