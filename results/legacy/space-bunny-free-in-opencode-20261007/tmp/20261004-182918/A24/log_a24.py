# -*- coding: utf-8 -*-
"""A24 wrap-up: log the visual iterations, build task-metrics.json, update suite state."""
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import wrapup  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A24")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A24")
DRAFTS = os.path.join(TMP, "drafts")


def draft(base, n):
    return os.path.join(DRAFTS, "%s-v%02d.snapshot" % (base, n))


ITERATIONS = [
    # ---------------- execution board
    ("A24-v01", "none", "baseline", draft("execution-board", 1),
     os.path.join(TMP, "preview", "execution-board.png"), "2026-10-05T00:41:12+08:00",
     "baseline never rendered: the service rejected gradientColors as a list, so there was "
     "no image to look at. Warnings also flagged seven single-line Texts whose measured "
     "width exceeded their box",
     "none (first request, no image yet)", False),
    ("A24-v02", "A24-v01", "syntax-fix", draft("execution-board", 2),
     os.path.join(TMP, "preview", "execution-board.png"), "2026-10-05T00:42:20+08:00",
     "no image: gradientColors must be a comma separated string and gradientBegin/End take "
     "named alignments; border then failed with 'value is invalid' because it needs "
     "'<width> SOLID <colour>'",
     "fixed the gradient string form and normalised every border through theme.bd()", False),
    ("A24-v03", "A24-v02", "syntax-fix", draft("execution-board", 3),
     os.path.join(TMP, "preview", "execution-board.png"), "2026-10-05T00:43:35+08:00",
     "no image: bare-colour borders on the lane cards and tiles produced the same "
     "PARSE_ERROR",
     "rewrote the remaining bare-colour border arguments", False),
    ("A24-v04", "A24-v03", "baseline", draft("execution-board", 4),
     os.path.join(TMP, "preview", "execution-board.png"), "2026-10-05T00:44:48+08:00",
     "first real image: swimlanes, axis, buffer bands and idle markers all rendered, but "
     "inside narrow blocks the 6-7 character Chinese labels were silently dropped "
     "(warnings: 6 text boxes needing ~2 lines but holding 1) and the mono clock ranges "
     "were clipped at the last glyph",
     "guarded every in-block label with a measured width check, added theme.mw() for "
     "monospace width, and widened the footnote box", False),
    ("A24-v05", "A24-v04", "visual", draft("execution-board", 5),
     os.path.join(TMP, "preview", "execution-board.png"), "2026-10-05T00:47:05+08:00",
     "monospace clocks now complete, but the lane annotations collided: the task-name "
     "band and the clock band each had their own two-row stagger and row 1 of one landed "
     "on row 0 of the other; the '决定链' tag inside blocks also sat on top of the "
     "'前置 R04·R05' line; the dependency index overran the legend row",
     "split the annotations into two non-overlapping fixed bands, moved 决定链 out of the "
     "block body, and re-laid the dependency index into three columns", False),
    ("A24-v06", "A24-v05", "visual", draft("execution-board", 6),
     os.path.join(TMP, "preview", "execution-board.png"), "2026-10-05T00:49:30+08:00",
     "index/legend no longer overlap, but D.warnings() still reported two fact lines that "
     "needed two lines inside one-line boxes, and one label inside narrow blocks (R03, R05) "
     "shared a y with the duration",
     "split the idle-gap facts into separate short lines and gave narrow blocks three "
     "stacked lines (id / label / duration)", False),
    ("A24-v07", "A24-v06", "visual", draft("execution-board", 7),
     os.path.join(TMP, "preview", "execution-board.png"), "2026-10-05T00:51:10+08:00",
     "lane heights were still sized for the old two-band layout, so the idle strip and the "
     "bottom section were tight; the two-row stagger could not hold the six design "
     "annotations, forcing two of them into an occupied row",
     "rebuilt the lane geometry: 300px lanes, name band at +20/+48, clock band at +80/+108, "
     "block band at +146, idle strip at +258", False),
    ("A24-v08", "A24-v07", "visual", draft("execution-board", 8),
     os.path.join(TMP, "preview", "execution-board.png"), "2026-10-05T00:53:02+08:00",
     "annotations no longer collide; remaining issues were the two fact lines that still "
     "needed two lines each and the legend sitting on the dependency index",
     "split the two long facts into four shorter lines and moved the legend and footnote "
     "down", False),
    ("A24-v09", "A24-v08", "visual", draft("execution-board", 9),
     os.path.join(TMP, "preview", "execution-board.png"), "2026-10-05T00:55:20+08:00",
     "2.4x zoom of the left block run showed R01/R04/R07 legible but the engineering lane "
     "still had a collision: narrow blocks drew the duration and the label on the same "
     "line (R03 '数据清洗' over '40 分', R05 '文案审校' over '30 分')",
     "branched the in-block layout on measured width: wide blocks keep id+duration on the "
     "first line then label then deps; narrow blocks stack id / label / duration one line "
     "each and drop the dependency line", False),
    ("A24-v10", "A24-v09", "visual", draft("execution-board", 10),
     os.path.join(TMP, "preview", "execution-board.png"), "2026-10-05T00:57:44+08:00",
     "block interiors are correct at 2.4x (R01 '25 分', R04 '60 分 / 视觉系统 / 前置 R01', "
     "R07 '70 分 / 主海报构建 / 前置 R04·R05', R09/R10/R12 all readable); the last defect was "
     "the ninth fact line overlapping the footnote",
     "trimmed the fact list to seven lines and shortened the monotone-search claim", False),
    ("A24-v11", "A24-v10", "visual", draft("execution-board", 11),
     os.path.join(TMP, "preview", "execution-board.png"), "2026-10-05T00:59:30+08:00",
     "no collisions left; 2.0x zoom of the bottom-right '排程依据' block and the legend "
     "confirmed all seven fact lines and five legend chips render completely",
     "changed 200000 to 20 万 for legibility", True),
    # ---------------- decision brief
    ("A24-v12", "A24-v11", "baseline", draft("decision-brief", 1),
     os.path.join(TMP, "preview", "decision-brief.png"), "2026-10-05T01:06:40+08:00",
     "first brief never rendered: a DAG connector was emitted with a negative height "
     "('minHeight must be between 0 and maxHeight'); twelve warnings also showed the "
     "seven-character Chinese labels did not fit 152px node interiors and that four "
     "single-line boxes needed two lines",
     "none possible until the service accepts the DSL", False),
    ("A24-v12b", "A24-v12", "syntax-fix", draft("decision-brief", 2),
     os.path.join(TMP, "preview", "decision-brief.png"), "2026-10-05T01:08:55+08:00",
     "the connector height was still negative (height=-13.5) because the sub-channel was "
     "derived from the channel height instead of the number of edges sharing it, so the "
     "third edge of a channel fell below the target row",
     "divided the channel by len(pairs) and clamped the connector y inside the channel",
     False),
    ("A24-v13", "A24-v12b", "visual", draft("decision-brief", 3),
     os.path.join(TMP, "preview", "decision-brief.png"), "2026-10-05T01:11:30+08:00",
     "first real brief image: header, six KPI tiles, layered dependency graph and the risk "
     "cards all rendered, but the column-based DAG could not hold seven-character labels at "
     "24px inside 176px nodes, node labels were clipped at the bottom edge, the KPI caption "
     "ran into the section title, and the DAG note overlapped the risk heading",
     "replaced the column DAG with a row-layered flow (300px nodes, right-margin bypass "
     "lane for the two multi-layer edges), raised the node height to 66, made the caption "
     "and note layout dynamic", False),
    ("A24-v14", "A24-v13", "visual", draft("decision-brief", 4),
     os.path.join(TMP, "preview", "decision-brief.png"), "2026-10-05T01:14:02+08:00",
     "row DAG readable end to end (six layers, 12 nodes, 16 edges, bypass lane on the "
     "right), but the measured content bottom was 1648.6px on a 1600px canvas, so the "
     "footer would be cut off, and the trailing U+3000 hanging indent was rendered "
     "zero-width by Inter",
     "compacted the KPI row, shortened the caption, made the rationale lines explicitly "
     "two lines each, and expressed the hanging indent as an x offset", False),
    ("A24-v15", "A24-v14", "visual", draft("decision-brief", 5),
     os.path.join(TMP, "preview", "decision-brief.png"), "2026-10-05T01:16:20+08:00",
     "content bottom fell to 1564.4px (inside 1600) but the DAG note still sat 2px from "
     "the risk heading",
     "pushed the risk block down by 10px", False),
    ("A24-v16", "A24-v15", "visual", draft("decision-brief", 6),
     os.path.join(TMP, "preview", "decision-brief.png"), "2026-10-05T01:18:48+08:00",
     "1.6x zoom of the rationale block confirmed the hanging indent now works and all eight "
     "rationale lines plus the two footer lines are complete; nothing further to change",
     "none needed", True),
    # ---------------- action card
    ("A24-v17", "A24-v16", "baseline", draft("action-card", 1),
     os.path.join(TMP, "preview", "action-card.png"), "2026-10-05T01:23:15+08:00",
     "first card never rendered: RENDER_ERROR renderBox.parentData must be "
     "StackParentData, because theme.chip() nested a Positioned inside its Container",
     "none possible until the service accepts the DSL", False),
    ("A24-v18", "A24-v17", "syntax-fix", draft("action-card", 2),
     os.path.join(TMP, "preview", "action-card.png"), "2026-10-05T01:25:05+08:00",
     "card rendered, but the three risk blocks ran into the footer lines (canvas bottom "
     "1280) and the vertical spine overlapped the per-row team dots",
     "none yet, layout review pending", False),
    ("A24-v19", "A24-v18", "visual", draft("action-card", 3),
     os.path.join(TMP, "preview", "action-card.png"), "2026-10-05T01:27:33+08:00",
     "12 rows read cleanly (time / id chip / label / team / duration / risk badge, CP rows "
     "marked), but the third risk block overlapped the '完成 13:20 · 缓冲 160 分' footer and "
     "the bottom source line sat on the canvas edge",
     "reduced the row pitch from 66 to 60 and re-flowed the risk and footer blocks",
     False),
    ("A24-v20", "A24-v19", "visual", draft("action-card", 4),
     os.path.join(TMP, "preview", "action-card.png"), "2026-10-05T01:30:12+08:00",
     "all twelve rows and the three risk blocks are separated; the last footer line was "
     "still only 2px above the canvas edge",
     "raised the footer block by 10px and added the legend note that the magenta marker "
     "means 决定链", True),
    # ---------------- final delivery renders (rendered into outputs/20261004-182918/A24)
    ("A24-v21", "A24-v20", "visual", draft("execution-board", 17),
     os.path.join(OUT, "execution-board.png"), "2026-10-05T01:44:05+08:00",
     "pixel probing of the delivered PNG found a real defect the eye had missed: the "
     "green 13:20 finish line and the red 16:00 deadline line were drawn BEFORE the lane "
     "cards, so the lane backgrounds covered them (sampled colour at x=1876 was white "
     "instead of #DC2626). verify_board_pixels.py reproduced it",
     "re-drew both markers after the lanes and moved their captions into the 772..812 "
     "gutter; pushed the bottom strip from y=782 to y=812 so the captions have their own "
     "row; re-rendered and re-probed", True),
    ("A24-v22", "A24-v21", "visual", draft("decision-brief", 12),
     os.path.join(OUT, "decision-brief.png"), "2026-10-05T01:44:26+08:00",
     "the accepted brief layout re-rendered for delivery; diff against v06 shows the "
     "hanging indent moved from a U+3000 prefix to an x offset, the wrap points of lines "
     "①②③④ changed accordingly, and the risk block sits 8px higher",
     "re-rendered into the output directory, D.warnings() = 0; 1.6x crop confirmed the "
     "indent and all wrap points, measured content bottom 1564.4px inside the 1600px "
     "canvas, PNG bytes are the raw service response and the delivered .snapshot is "
     "byte-identical to this draft", True),
    ("A24-v23", "A24-v22", "visual", draft("action-card", 6),
     os.path.join(OUT, "action-card.png"), "2026-10-05T01:44:38+08:00",
     "the accepted card re-rendered for delivery; diff against v04 is empty, i.e. the "
     "delivered design is the accepted one with no further edit",
     "re-rendered into the output directory, D.warnings() = 0; re-checked at full size: "
     "twelve rows in time order with team, start-end, duration and K badges, three risk "
     "blocks, footer inside the canvas (content bottom 1268px of 1280px); PNG bytes are "
     "the raw service response and the delivered .snapshot is byte-identical to this "
     "draft", True),
]

m = wrapup.wrapup(
    "A24",
    "2026-10-05T00:39:30+08:00",   # task started (first entry in requests.jsonl)
    "2026-10-05T00:44:48+08:00",   # first usable image (execution-board v04)
    "2026-10-05T01:48:10+08:00",   # task ended (after the pixel re-verification)
    iterations=[(a, b, c, d, e, f, g, h, i) for (a, b, c, d, e, f, g, h, i) in ITERATIONS],
    artifacts=["execution-board.png", "execution-board.snapshot",
               "decision-brief.png", "decision-brief.snapshot",
               "action-card.png", "action-card.snapshot",
               "schedule.json", "schedule-audit.json", "content-map.json",
               "snapshot-usage.md", "task-metrics.json"],
    visual_evidence=[
        "every rendered PNG was opened with the read tool: execution-board v04-v17, "
        "decision-brief v03-v12, action-card v02-v06",
        "2.4x crop of execution-board blocks-left (R01/R04/R07/R09) and blocks-right "
        "(R09/R10/R12) to confirm ids, durations, labels and dependency lines are not "
        "clipped",
        "2.0x crop of the execution-board '排程依据' facts block and legend",
        "1.6x crop of the decision-brief rationale and footer block (hanging indent and "
        "wrap points)",
        "whole-image review of all three delivered PNGs in outputs/20261004-182918/A24",
        "verify_board_pixels.py: every block edge re-measured on the delivered PNG against "
        "316 + minute * 3.7143 px, widths against input minutes, fill against the assigned "
        "team colour, the deciding-chain border against the magenta, both idle markers, both "
        "reserve bands and both vertical markers - all pass, script exits 0",
    ],
    unresolved=[
        "execution-board: the engineering idle-gap caption ('空档 5 分 · 等 R09 完成（不可抢占）') "
        "extends rightwards into the green reserve band; it stays readable and no value is "
        "affected, left as is",
        "dsllib.est_width() underestimates lowercase Inter advance widths, so a few long "
        "latin strings had to be shortened manually; theme.mw() compensates for the "
        "monospace stack only",
        "the input carries no rework/retry allowance, so K3's rework can only be absorbed "
        "by the 160-minute tail reserve and K1's rate-limit retries are not modelled as "
        "schedule time",
    ],
    notes="Two-team constrained release plan solved by exhaustive DFS over all legal "
          "(task order x chosen team) schedules: makespan 260 min (13:20), buffer 160 min, "
          "resource-free critical path 255 min, workload lower bound ceil(485/2)=243 min. "
          "260 is proved optimal by the exhaustive search and cross-checked by 200k "
          "randomised samples; 255 is shown as an unattainable lower bound with a written "
          "contradiction proof. All three figures (1920x1080 board, 1200x1600 brief, "
          "720x1280 card) are generated from one PLAN dict so no value can disagree.",
)
print(json.dumps(m["counts"], ensure_ascii=False, indent=1))
print("failures:", len(m["failures"]))
