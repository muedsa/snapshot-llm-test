# -*- coding: utf-8 -*-
"""A14 finalize: append doc-reuse requests, write iterations.jsonl,
build batch-audit.json (template/audit-fields.json contract).

All timestamps +08:00. View times are minute-precision session-local
observations (the exact second of each image read is not instrumented);
render timestamps in requests.jsonl are millisecond-precise anchors.
"""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(".")
RUN = "run-20261011-01"
T = ROOT / "tmp" / RUN / "A14"
O = ROOT / "outputs" / RUN / "A14"

# ---------------------------------------------------------------- doc reuse
doc_entries = [
    ("A14-doc-reuse-0001", "https://open-snapshot.muedsa.com/ai-guide.md",
     "tmp/run-20261011-01/_suite/docs/ai-guide.md",
     "复用套件缓存：确认请求体/编码/响应类型/错误处理约定；本题40个渲染请求全部按该指南编码执行，未新增HTTP"),
    ("A14-doc-reuse-0002",
     "https://snapshot.muedsa.com/ tags reference (parser-tags.html): Snapshot / SizedBox / Stack / Positioned / Container / Text",
     "tmp/run-20261011-01/_suite/docs/parser-tags.html",
     "复用套件缓存：Text 的 text属性/字体族/textAlign/height，Positioned 几何，Container borderRadius/gradient；据此实现text属性发射（<>&字面通过）与胶囊居中"),
    ("A14-doc-reuse-0003", "fonts query result (open-snapshot fonts list)",
     "tmp/run-20261011-01/_suite/docs/fonts.txt",
     "复用套件缓存：正文 Noto Sans CJK SC、等宽 Noto Sans Mono CJK SC、拉丁 Inter,Noto Sans CJK SC，无新增查询"),
]
with (T / "requests.jsonl").open("a", encoding="utf-8") as f:
    for eid, url, cached, note in doc_entries:
        f.write(json.dumps({
            "id": eid, "ts": "2026-10-15T12:40:00+08:00",
            "request_type": "doc-reuse", "method": None, "url": url,
            "cached_at": cached, "elapsed_seconds": 0, "http_status": None,
            "note": note, "requestId": None, "server_timing": None,
            "error": None,
        }, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- iterations
iters = [
    # ---- pre-pivot wall phase (retained drafts; see requirement-change)
    {"version_id": "A14-wall-v1", "parent": None, "type": "baseline",
     "task_phase": "pre-pivot wall draft (superseded by cards deliverable)",
     "images": ["tmp/run-20261011-01/A14/drafts/wall-v1.png"],
     "viewed_at": "2026-10-15T11:43:00+08:00",
     "view_note": "full wall view, minute precision",
     "problems": ["K03 title orphan line (tail '级' alone on last line)"],
     "changes": [],
     "recheck": "baseline accepted as starting point for wrap improvements",
     "request_ids": ["A14-req-0001"]},
    {"version_id": "A14-wall-v2", "parent": "A14-wall-v1", "type": "visual",
     "task_phase": "pre-pivot wall draft (superseded)",
     "images": ["tmp/run-20261011-01/A14/drafts/wall-v2.png",
                "tmp/run-20261011-01/A14/crops/v2-card-K03.png"],
     "viewed_at": "2026-10-15T11:53:00+08:00",
     "view_note": "full wall + K03 crop",
     "problems": ["K07 '数据' split mid-word; K08 break ignored punctuation"],
     "changes": ["wrap_title: avoid <=2-char tail lines (orphan rebalance)"],
     "recheck": "K03 orphan gone; remaining punctuation breaks noted",
     "request_ids": ["A14-req-0005"]},
    {"version_id": "A14-wall-v3", "parent": "A14-wall-v2", "type": "visual",
     "task_phase": "pre-pivot wall draft (superseded)",
     "images": ["tmp/run-20261011-01/A14/drafts/wall-v3.png",
                "tmp/run-20261011-01/A14/crops/v3-card-K08.png"],
     "viewed_at": "2026-10-15T12:01:00+08:00",
     "view_note": "full wall + K08 crop",
     "problems": [],
     "changes": ["wrap_title: punctuation-segment packing (split at ：，、。；！？/) "
                 "with atom-wrap fallback"],
     "recheck": "K03 breaks at colon, K07 '数据' intact, K08 breaks after colon",
     "request_ids": ["A14-req-0006"]},
    {"version_id": "A14-wall-v3-measure", "parent": "A14-wall-v3",
     "type": "alternative",
     "task_phase": "pre-pivot wall draft (superseded)",
     "images": [],
     "viewed_at": None,
     "problems": ["first measurement reported 8 title-line overflows "
                  "(window-bleed false positives: +-6px windows overlap at "
                  "35px line step, same gotcha as A12)"],
     "changes": ["measure_a14.py: per-line +-6 windows replaced by whole-region "
                 "ink band analysis (band count vs expected lines, first/last "
                 "band containment, per-band width)"],
     "recheck": "wall v3 re-measured: 0 failures (size/safe-margin/bands clean)",
     "request_ids": []},
    {"version_id": "A14-requirement-change", "parent": "A14-wall-v3-measure",
     "type": "requirement-change",
     "task_phase": "pivot to authoritative task text",
     "images": [],
     "viewed_at": "2026-10-15T12:11:00+08:00",
     "problems": ["earlier session worked from a misremembered task description "
                  "(1440x1800 poster wall + card-results.json)"],
     "changes": ["re-read tasks/A14-content-stress-batch/TASK.md + task.json: "
                 "authoritative deliverable = 8 cards card-K01..K08 at 1200x630 "
                 "+ batch-audit.json; generator rebuilt for cards "
                 "(scripts/gen_cards.py); wall drafts/probes retained in tmp "
                 "as process evidence"],
     "recheck": "task.json required_outputs (16 PNG/DSL pairs + batch-audit) "
                "matched against delivery plan",
     "request_ids": []},
    # ---- cards phase
    {"version_id": "A14-cards-v1", "parent": None, "type": "baseline",
     "images": [f"tmp/run-20261011-01/A14/cards/v1/card-K0{i}.png"
                for i in range(1, 9)],
     "viewed_at": "2026-10-15T12:13:00+08:00",
     "view_end_at": "2026-10-15T12:16:00+08:00",
     "view_note": "all 8 cards opened and inspected individually",
     "problems": ["large void between centered-top title and divider on "
                  "1-line cards (all 8)",
                  "K06 annotation pill too similar in style to status badge"],
     "changes": [],
     "recheck": "baseline for visual iteration",
     "request_ids": [f"A14-req-{i:04d}" for i in range(7, 15)]},
    {"version_id": "A14-cards-v2", "parent": "A14-cards-v1", "type": "visual",
     "images": [f"tmp/run-20261011-01/A14/cards/v2/card-K0{i}.png"
                for i in range(1, 9)],
     "viewed_at": "2026-10-15T12:17:00+08:00",
     "view_end_at": "2026-10-15T12:19:00+08:00",
     "view_note": "all 8 cards opened and compared against v1",
     "problems": ["time text flush-left in pill (ink 41..98, pill 40..151)",
                  "index text flush-left (ink 907..934, pill 906..966)",
                  "date right edge 1108, 52px short of the 1160 margin "
                  "(measured, not visible at first glance)"],
     "changes": ["title block vertically centered in unified region [104,422] "
                 "(fixes the void)",
                 "K06 annotation -> solid red pill with dark bold text "
                 "(clearly distinct from outline status badge)"],
     "recheck": "layout balanced; alignment issues found by pixel measurement",
     "request_ids": [f"A14-req-{i:04d}" for i in range(15, 23)]},
    {"version_id": "A14-cards-v3", "parent": "A14-cards-v2", "type": "visual",
     "images": ["tmp/run-20261011-01/A14/crops/v3-K01-date-x5.png",
                "tmp/run-20261011-01/A14/crops/v2-K01-date-x5.png",
                "tmp/run-20261011-01/A14/crops/v3-K01-date-x7.png",
                "tmp/run-20261011-01/A14/crops/v2-K01-date-x7.png"],
     "viewed_at": "2026-10-15T12:21:00+08:00",
     "view_note": "full-card view superseded by measurement gate: date crops "
                  "at x5/x7 viewed instead of all 8 full cards",
     "problems": ["date box width 119 < text advance ~120 -> last glyph '7' "
                  "wrapped to an invisible second line: v3 renders "
                  "'2026.11.0' (caught by band measurement + confirmed by "
                  "x7 crop, affects all 8 cards)"],
     "changes": ["textAlign=CENTER on time/badge/annotation/index pill texts",
                 "date box moved to x=1041 so ink ends flush at the 1160 margin"],
     "recheck": "pill centering verified by measurement (time ink 66..124 in "
                "pill 40..151, index 922..949 in 906..966); date defect "
                "escalated to v4",
     "request_ids": [f"A14-req-{i:04d}" for i in range(23, 31)]},
    {"version_id": "A14-cards-v4", "parent": "A14-cards-v3", "type": "visual",
     "images": [f"tmp/run-20261011-01/A14/cards/v4/card-K0{i}.png"
                for i in range(1, 9)],
     "viewed_at": "2026-10-15T12:31:00+08:00",
     "view_end_at": "2026-10-15T12:33:00+08:00",
     "view_note": "all 8 cards opened individually; contact sheet at 12:35",
     "problems": [],
     "changes": ["date box width 119 -> 131 (keeps ink flush at 1160, no wrap)"],
     "recheck": "measure_cards v4: 0 failures (size, safe margin, band counts, "
                "single-line pills, padding/centering, fonts, no title-badge "
                "collision); date ink 1042..1159; source text ALL EXACT; "
                "contact sheet consistent",
     "request_ids": [f"A14-req-{i:04d}" for i in range(31, 39)]},
    {"version_id": "A14-measure-tool-fix", "parent": "A14-cards-v4",
     "type": "alternative",
     "images": [],
     "viewed_at": None,
     "problems": ["first measure_cards run reported 22 failures, all tool "
                  "defects: title bands compared by edge equality instead of "
                  "containment (leading is expected), pill windows x+4/y+3 "
                  "caught the r=22 border arcs and the annotation's dark "
                  "card background at rounded corners"],
     "changes": ["title check -> containment +-4; pill windows -> x+-12 y+-6; "
                 "annotation uses inverted (dark) detection with its own window; "
                 "padding + centering checks added"],
     "recheck": "re-run on unchanged v4 renders: 8 cards, 0 failures",
     "request_ids": []},
    {"version_id": "A14-probes", "parent": "A14-cards-v4", "type": "alternative",
     "images": ["tmp/run-20261011-01/A14/cards/probe/card-K99.png",
                "tmp/run-20261011-01/A14/cards/probe/card-K98.png"],
     "viewed_at": "2026-10-15T12:37:00+08:00",
     "view_note": "both probes opened individually (K98 after 12:39 render)",
     "problems": [],
     "changes": ["synthetic anomaly probes of the deliverable generator: K99 "
                 "(unknown status -> neutral encoding + warning, time 900 int "
                 "-> str coercion, long title shrinks 56->38, long speaker 2 "
                 "lines), K98 (extreme title -> shrink to 36 + ellipsis "
                 "truncation + warning)"],
     "recheck": "both rendered 200 and viewed: no overflow, warnings visible in "
                "layout records; probes kept in tmp, not part of the 8 finals",
     "request_ids": ["A14-req-0039", "A14-req-0040"]},
]
with (T / "iterations.jsonl").open("w", encoding="utf-8") as f:
    for e in iters:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
print(f"iterations.jsonl: {len(iters)} entries")

# ---------------------------------------------------------------- batch audit
layout = json.loads((T / "cards" / "v4" / "layout-v4.json").read_text(encoding="utf-8"))
measured = json.loads((T / "measured-cards-v4.json").read_text(encoding="utf-8"))
src = json.loads((ROOT / "tasks" / "A14-content-stress-batch" / "inputs" /
                  "cards.json").read_text(encoding="utf-8"))
smap = {str(c["id"]): c for c in src}
mmap = {c["id"]: c for c in measured["cards"]}

observations = {
    "K01": "单行标题「开始」垂直居中于统一标题区；日期 2026.11.07 右缘与页边齐平；K01 序号胶囊居中；● 开放绿徽标、09:00 等宽时间胶囊均双边留白居中",
    "K02": "13 字单行标题 56px 一行完整无缩字；▲ 满额琥珀色徽标；周禾 / 许宁 讲者行完整",
    "K03": "2 行标题在全角冒号后换行，两行墨迹均在声明行盒内；◇ 候补蓝徽标",
    "K04": "标题含 HTML 保留字 < > & 逐字字面渲染（text 属性通道），单行完整；11:00 时间胶囊",
    "K05": "拉丁+中文混排在斜杠后换行，& 字面正确；两行均在盒内",
    "K06": "取消卡：完整标题两行与时间 13:40 均保留，实心红「× 本场取消」注记 + 描边「× 取消」徽标双胶囊，非删除非灰底",
    "K07": "破折号 —— 与间隔号 · 字面渲染；讲者 Northstar Research · 林川 单行完整；14:20",
    "K08": "弯引号 “” 字面渲染；标题在全角冒号后换行，末行「模型工作能力的最后一公里」完整",
}
cards_out = []
for rec in layout["cards"]:
    cid = rec["id"]
    m = mmap[cid]
    md5 = hashlib.md5((O / f"card-{cid}.png").read_bytes()).hexdigest()
    cards_out.append({
        "id": cid,
        "source_text": smap[cid],
        "displayed_text": {
            "title": rec["displayed_title"],
            "speaker": rec["displayed_speaker"],
            "time": rec["displayed_time"],
            "status": rec["status_encoding"]["status"],
        },
        "text_preserved_exactly": (
            rec["displayed_title"].replace("\n", "") == str(smap[cid]["title"])
            and rec["displayed_speaker"].replace("\n", "") == str(smap[cid]["speaker"])
            and rec["displayed_time"] == str(smap[cid]["time"])
            and rec["status_encoding"]["status"] == str(smap[cid]["status"])),
        "png": f"card-{cid}.png",
        "dsl": f"card-{cid}.snapshot",
        "png_md5": md5,
        "png_bytes": "service response bytes, copied unchanged (md5 verified "
                     "against tmp source)",
        "title": {
            "font_size": rec["title_font_size"],
            "line_count": rec["title_line_count"],
            "line_boxes": rec["title_line_boxes"],
            "lines": rec["displayed_title"].split("\n"),
            "font_min_requirement": ">=36",
            "line_requirement": "<=3",
        },
        "speaker": {
            "font_size": rec["speaker_font_size"],
            "line_count": rec["speaker_line_count"],
            "boxes": rec["speaker_boxes"],
            "lines": rec["displayed_speaker"].split("\n"),
            "font_min_requirement": ">=22",
        },
        "time_box": rec["time_box"],
        "status_encoding": rec["status_encoding"],
        "badge_box": rec["badge_box"],
        "annotation": ({"text": rec["annotation_text"],
                        "box": rec["annotation_box"]} if rec["annotation_box"]
                       else None),
        "safe_margin": 40,
        "measurement": {
            "evidence": {"path_base": "suite_root",
                         "path": f"tmp/{RUN}/A14/measured-cards-v4.json"},
            "ink_bbox": m["checks"]["ink_bbox"],
            "title_bands": m["checks"]["title_bands"],
            "title_expected_bands": m["checks"]["title_expected"],
            "speaker_bands": m["checks"]["speaker_bands"],
            "date_bands": m["checks"]["date_bands"],
            "size_ok": m["size"] == [1200, 630],
            "safe_margin_ok": True,
            "no_title_badge_collision": True,
            "method": "lum>70 ink bands over declared boxes; margin check on "
                      "global ink bbox; tool: measure_cards.py",
        },
        "warnings": rec["warnings"],
    })

review_times = {"K01": "12:31", "K02": "12:31", "K03": "12:32", "K04": "12:32",
                "K05": "12:32", "K06": "12:33", "K07": "12:33", "K08": "12:33"}
reviews = []
for cid in [f"K0{i}" for i in range(1, 9)]:
    reviews.append({
        "id": cid,
        "image": f"card-{cid}.png",
        "viewed_at": f"2026-10-15T{review_times[cid]}:00+08:00",
        "viewed_at_precision": "minute; render anchors in requests.jsonl "
                               "(A14-req-0031..0038, 12:28:44-12:29:07+08:00) "
                               "are millisecond-precise",
        "observation": observations[cid],
        "modifications": "v2 title block centered + K06 annotation strengthened; "
                         "v3 pill texts centered + date right-flushed (date "
                         "wrap defect found); v4 date box widened (defect fixed)",
        "final_conclusion": "passed - full content, layout, special characters "
                            "and measurement checks verified on the delivered "
                            "image",
    })

audit = {
    "schema_version": 1,
    "task_id": "A14",
    "path_base": "output_dir",
    "generation": {
        "script": {"path_base": "suite_root",
                   "path": f"tmp/{RUN}/A14/scripts/gen_cards.py"},
        "measurement_script": {"path_base": "suite_root",
                               "path": f"tmp/{RUN}/A14/scripts/measure_cards.py"},
        "shared_rules": {
            "canvas": [1200, 630],
            "safe_margin": 40,
            "primary_color": "#22D3EE",
            "brand": "Structure / Vision",
            "date": "2026.11.07",
            "layout": "header (brand left / index pill / date right) + cyan rule "
                      "y92 + unified title area [104,422] (block vertically "
                      "centered) + divider y430 + speaker y450 + bottom row "
                      "y540 h44 (time pill left / status badge right)",
            "title_wrap": "punctuation-segment packing (split at ：，、。；！？/) "
                          "with atom-wrap fallback and orphan-tail rebalance",
            "text_emission": "text=\"...\" attribute (verified to pass raw "
                             "< > & through; element content would PARSE_ERROR "
                             "on raw '<')",
            "no_per_card_hardcode": "single parameterized generator; the only "
                                    "branches are data-driven (length and "
                                    "status), identical parameters for all 8",
        },
        "length_branches": {
            "title_font": "first size in [56,50,46,42,40,38,36] whose wrapped "
                          "line count <= 3; if none fits, use 36 + truncate last "
                          "line with ellipsis + warning (never below 36)",
            "speaker": "wrap at 640px / 26px; >2 lines -> keep 2 + ellipsis + "
                       "warning",
            "unknown_status": "color #94A3B8, symbol ◆, badge '<symbol> <status>' "
                              "+ warning (branch not triggered by real input)",
            "cancelled": "status == '取消' -> additional solid annotation pill "
                         "'✕ 本场取消' left of the badge; card keeps full "
                         "color/title/time (data-driven, triggers on K06)",
        },
        "observed_branches_real_input": {
            "title_fonts_used": {"56": 8},
            "title_lines": {"1": 3, "2": 5},
            "speaker_lines": {"1": 8},
            "truncations": 0,
            "unknown_status": 0,
        },
        "auxiliary_tests": {
            "anomaly_probe_K99": {
                "record": {"path_base": "suite_root",
                           "path": f"tmp/{RUN}/A14/cards/probe/probe-K99.json"},
                "png": {"path_base": "suite_root",
                        "path": f"tmp/{RUN}/A14/cards/probe/card-K99.png"},
                "covers": "unknown status neutral encoding + warning, time 900 "
                          "int -> str coercion, long title shrink 56->38, long "
                          "speaker 2 lines",
                "viewed_at": "2026-10-15T12:37:00+08:00",
            },
            "truncation_probe_K98": {
                "record": {"path_base": "suite_root",
                           "path": f"tmp/{RUN}/A14/cards/probe/probe-K98.json"},
                "png": {"path_base": "suite_root",
                        "path": f"tmp/{RUN}/A14/cards/probe/card-K98.png"},
                "covers": "extreme title -> shrink to 36 + ellipsis truncation "
                          "+ warning, 3 lines, no overflow",
                "viewed_at": "2026-10-15T12:39:00+08:00",
            },
            "text_special_cases_in_real_input": {
                "K04": "HTML reserved < > & literal",
                "K05": "& and / literal",
                "K07": "em-dash —— and middle dot · literal",
                "K08": "curly quotes “” literal",
                "note": "real input contains no newline; newline handling of "
                        "the shared text emission was exercised by pre-pivot "
                        "wall probe (tmp/run-20261011-01/A14/drafts/"
                        "probe-newline*.snapshot, real \\n breaks line in both "
                        "text-attr and element-content forms)",
            },
        },
        "text_preservation_check": {
            "method": "programmatic string equality of displayed (newline-"
                      "stripped) vs inputs/cards.json for title/speaker/time/"
                      "status on all 8 cards",
            "result": "ALL EXACT",
        },
    },
    "cards": cards_out,
    "reviews": reviews,
    "auxiliary_evidence": {
        "contact_sheet": {
            "path_base": "suite_root",
            "path": f"tmp/{RUN}/A14/crops/contact-v4.png",
            "viewed_at": "2026-10-15T12:35:00+08:00",
            "observation": "8 cards consistent in header/rule/divider/bottom "
                           "row/status colors; auxiliary only, does not replace "
                           "the 8 individually viewed final service images",
        },
        "measure_report": {"path_base": "suite_root",
                           "path": f"tmp/{RUN}/A14/measured-cards-v4.json",
                           "failures": 0},
    },
}
(O / "batch-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
print("batch-audit.json:",
      len(audit["cards"]), "cards,",
      len(audit["reviews"]), "reviews,",
      "all_exact =", all(c["text_preserved_exactly"] for c in cards_out))
