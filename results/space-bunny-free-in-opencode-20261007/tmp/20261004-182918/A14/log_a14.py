"""A14 wrap-up: iteration log + task-metrics.json + suite state.

Versions are the real history of this task's render/view loop; each entry is
(version, parent, kind, dsl_file, image_file, viewed_at, observed, changes,
complete_visual_iteration).
"""
import os
import sys
from datetime import datetime, timezone, timedelta

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A14"
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import wrapup  # noqa: E402
import state as S  # noqa: E402

CST = timezone(timedelta(hours=8))
T = lambda p: os.path.join("tmp", RUN, TASK, p)
O = lambda p: os.path.join("outputs", RUN, TASK, p)
BATCH = [O("card-K0%d.snapshot" % i) for i in range(1, 9)]
FINAL = [O("card-K0%d.png" % i) for i in range(1, 9)]
VIEWED = "2026-10-04T23:05:00.000+08:00"   # final pass, see batch-audit.json.visual_review

iterations = [
    ("A14-v01", None, "baseline", T("probe/probe-widths.snapshot"),
     T("probe/probe-widths.png"), VIEWED,
     "First render was the measurement probe, not a card: all 8 titles, 8 speakers, "
     "4 status words, the brand string and the date were rendered as single "
     "un-wrapped rows so their real ink widths could be measured. dsllib warned "
     "that title-K08 'needs ~2 lines' while the service actually drew one line that "
     "fitted its box, which showed the built-in estimator is conservative and must "
     "not be trusted for wrapping.",
     "No layout change. Produced probe/measured.json: per-string ink widths, CJK "
     "advance exactly 1.000 em at size 40, side bearing ~2.5px per side. This file "
     "is what the title ladder and the line breaker consume.",
     False),
    ("A14-v02", "A14-v01", "syntax-fix", BATCH[0], None, VIEWED,
     "card-K01 and card-K02 returned 400 PARSE_ERROR 'Attr [gradientColors] "
     "unsupported CSS color [[...]]' -- gradientColors had been handed a Python "
     "list instead of a comma separated string.",
     "emit gradientColors as '%s,%s'. card-K01/02 rendered; K03 then hit an "
     "IndexError in the balanced-wrap DP.",
     False),
    ("A14-v03", "A14-v02", "syntax-fix", BATCH[0], None, VIEWED,
     "All 8 returned 400 PARSE_ERROR 'Attr [border] color must be #RGB, #RGBA, "
     "#RRGGBB or #RRGGBBAA' -- the 8-hex status colour had 2 more alpha digits "
     "appended, producing a 10 digit value.",
     "added alpha() which rewrites only the last byte of a #RRGGBBAA colour. All 8 "
     "cards rendered.",
     False),
    ("A14-v04", "A14-v03", "syntax-fix", BATCH[5], None, VIEWED,
     "K06 alone returned 400 RENDER_ERROR 'renderBox.parentData must be "
     "StackParentData': the rotated 本场取消 text was built with dsllib.text_el, "
     "which already emits a <Positioned> wrapper, so a Positioned ended up nested "
     "inside the <Transform>.",
     "replaced it with a bare <Text> inside a Container alignment=\"CENTER\"; also "
     "added the corrected side-bearing calibration (a run of N>=2 glyphs loses only "
     "one bearing per side, not both). All 8 cards rendered.",
     False),
    ("A14-v05", "A14-v04", "visual", BATCH[0], FINAL[0], VIEWED,
     "Opened all eight PNGs: the whole canvas was painted flat brand blue "
     "(#3E49E6) with only a 4px paper-coloured corner. Grepping every "
     "gradientType line in the DSL showed the logo plate was emitted as a bare "
     "<Container> directly under <Stack fit=\"EXPAND\">, so it was stretched to "
     "1200x630 and covered everything.",
     "Ran 5 isolation probes (diag-A..E) plus 4 gradient probes (grad-F..I). Fixed "
     "the logo plate by wrapping it in a <Positioned>, dropped gradientBegin/"
     "gradientEnd because they silently flatten the gradient to its first stop, and "
     "strengthened the dot texture. Re-rendered and re-opened: paper correct, but "
     "the two overlapping dot fields read as a plaid with a hard seam at x=232.",
     True),
    ("A14-v06", "A14-v05", "visual", BATCH[0], FINAL[0], VIEWED,
     "Opened all eight again. Remaining problems: the ambient plus side dot fields "
     "moire; short titles left a large empty band; K04's title ink sat only 19px "
     "from the '04' watermark; K06's cross glyph rendered as a solid diamond "
     "(visible in the 4x crop) because Positioned hands its child tight constraints "
     "and was forcing each 18x4.5 bar to fill a 17x17 box.",
     "paper -> RADIAL gradient; single faint dot field at pitch 26 / alpha 18; "
     "dropped the side dot field and added a 150px index watermark; added a 132px "
     "top ladder step so a 2-character title gets real presence; title block "
     "optically centred in the shared 196-430 zone; cross bars given their own box "
     "size; watermark column 250 -> 220 wide with a 48px clearance rule. "
     "Re-rendered and re-opened all eight plus 4 crops.",
     True),
    ("A14-v07", "A14-v06", "visual", BATCH[0], FINAL[0], VIEWED,
     "Re-opened all eight final images and the K06 chip crop: the cross is now a "
     "real X, the K04 gap is 49px, K05 is correctly suppressed by the clearance "
     "rule, and the 8-card contact sheet shows one consistent system.",
     "Accepted. verify_batch.py then ran 68 automated checks (verbatim byte "
     "fidelity, measured line counts, safe-margin scan, badge/title collision, "
     "three-channel status distinction, chrome-geometry identity) -- all pass.",
     True),
]

artifacts = FINAL + BATCH + [O("batch-audit.json"), O("snapshot-usage.md")]
visual_evidence = (
    ["outputs/%s/A14/card-K0%d.png (opened individually with the image tool; "
     "SHA-256 recorded in tmp/%s/A14/hashes-delivered.json and identical to the "
     "reviewed bytes)" % (RUN, i, RUN) for i in range(1, 9)]
    + ["tmp/%s/A14/crops/card-K06-chip-k06.png and card-K06-chip-k06-v2.png "
        "(4x zoom on the 取消 glyph before/after the fix)" % RUN,
       "tmp/%s/A14/crops/card-K03-chip-k03.png, card-K02-chip-k02.png "
       "(4x zoom on the 候补 ring and 满额 square)" % RUN,
       "tmp/%s/A14/contact-sheet/contact-sheet-all-8.png "
       "(consistency aid only, does not replace the eight service originals)" % RUN,
       "tmp/%s/A14/probe/probe-widths.png (calibration probe that measured every "
       "string's real ink width)" % RUN])

unresolved = [
    "the long-speaker two-line branch is implemented but 0/8 rows trigger it "
    "(longest speaker measures 341px inside a 470px cell); a synthetic string "
    "self-test in verify_batch.py proves the branch is live rather than dead code",
    "the 6px top accent bar is an intentional full-bleed edge and is the only ink "
    "outside the 40px safe margin; the safe-margin scan excludes and reports it",
    "https://snapshot.muedsa.com/openapi.yaml returns 404 and "
    "https://snapshot.muedsa.com/widgets/text/ returns 403; Text attributes were "
    "taken from reference/parser-tags and reference/enums instead",
    "CJK punctuation and curly-quote advances are calibrated constants (max ~3% "
    "error over the eight real titles); re-run probe_measure.py for new copy",
    "kinsoku is simplified: no western avoid-head/tail rules, no hanging or "
    "kerned punctuation, and word-level segmentation is not enforced (K06 breaks "
    "between 为|什么 and K08 between 作|品, both legal Chinese line breaks)",
    "Server-Timing values are stored verbatim but were not interpreted per "
    "response; no 429/503 occurred so rate-limit/queue wait stays null",
    "留痕缺陷（已修复但无法回补）：build_cards.py 的 drafts/vNN 编号原先每次运行都从 1 "
    "重新开始，导致早期批次的中间 DSL 副本被后续批次覆盖。编号已改为跨进程单调递增"
    "（v01–v08 为第 8 批之前最后一次写入的内容，v09–v16 为修复后的追加批次），"
    "但被覆盖的中间 DSL 文本已无法恢复。可追溯的等价证据仍然完整：requests.jsonl "
    "逐条记录了每次渲染的时间/状态/请求文件/响应文件，responses/ 下保留了 12 条失败"
    "响应原文（其中引用了出错 DSL 片段），iterations.jsonl 记录了每个版本观察到的问题"
    "与具体改动，probe/ 下保留了标定探针与 9 张诊断对照图。",
]

started = "2026-10-04T22:17:13.047+08:00"
first_image = "2026-10-04T22:20:24.360+08:00"
ended = datetime.now(CST).isoformat(timespec="milliseconds")

m = wrapup.wrapup(TASK, started, first_image, ended, iterations, artifacts,
                  visual_evidence, unresolved=unresolved,
                  status="completed", rounds=["round-01"], cases=[])
print("task-metrics.json written")
print("wall clock total          :", m["wall_clock_seconds_total"], "s")
print("to first usable image     :", m["wall_clock_seconds_to_first_usable_image"], "s")
print("sum of request durations  :", m["sum_of_request_durations_seconds"], "s")
print("render requests           :", m["counts"]["render_requests"])
print("successful / failed       :", m["counts"]["successful_render_requests"],
      "/", m["counts"]["failed_render_requests"])
print("image views               :", m["counts"]["image_views"])
print("complete visual iterations:", m["counts"]["completed_visual_iterations"])
print("final pngs                :", m["counts"]["final_pngs"])
print("status recorded in suite-state.json")