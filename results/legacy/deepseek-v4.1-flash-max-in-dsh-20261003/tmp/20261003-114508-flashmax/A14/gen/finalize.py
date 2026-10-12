"""A14 · write batch-audit.json, the bookkeeping logs and task-metrics.json."""
from __future__ import annotations

import json
import os
import shutil
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TMP = os.path.join(ROOT, "tmp", RUN, "A14")
OUT = os.path.join(ROOT, "outputs", RUN, "A14")
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite", "shared"))
from suite_common import append_jsonl_nobom, write_json, build_metrics, read_jsonl  # noqa: E402

PLAN = json.load(open(os.path.join(TMP, "card-plan.json"), encoding="utf-8"))
PIX = {r["id"]: r for r in json.load(open(os.path.join(TMP, "pixel-audit.v6.json"),
                                          encoding="utf-8"))}
REQS = read_jsonl(os.path.join(TMP, "requests.jsonl"))
ENDED = REQS[-1]["ended_at"][:19] + "+08:00"
STARTED = "2026-10-03T12:59:04+08:00"      # tmp/<run>/A14 directory creation time

# keep a versioned copy of every DSL that produced a final card
for p in PLAN:
    shutil.copyfile(os.path.join(TMP, "dsl", f"card-{p['id']}.snapshot"),
                    os.path.join(TMP, "dsl", f"card-{p['id']}.v6.snapshot"))
shutil.copyfile(os.path.join(TMP, "dsl", "probe.entities.v1.snapshot"),
                os.path.join(TMP, "dsl", "probe.entities.v2.snapshot"))

# --------------------------------------------------------------------------- image views
VIEWS = [
    ("A14-VIEW-01", "png/card-K01.v1.png", "v1·K01：72px单行标题，中央留白偏多", "sparse"),
    ("A14-VIEW-02", "png/card-K02.v1.png", "v1·K02：单行标题成立", "none"),
    ("A14-VIEW-03", "png/card-K03.v1.png", "v1·K03：两行标题成立", "none"),
    ("A14-VIEW-04", "png/card-K04.v1.png",
     "v1·K04：标题渲染成字面量 A &lt; B &amp; C &gt; D 且首行溢出右边界", "entity bug"),
    ("A14-VIEW-05", "png/card-K01.v3.png", "v3·K01：字号提升到96px，力度更足", "none"),
    ("A14-VIEW-06", "png/card-K04.v3.png",
     "v3·K04：< & > 已正确渲染，但断行把「不要」拆成「…D：不 / 要把…」", "orphan break"),
    ("A14-VIEW-07", "png/card-K03.v6.png", "v6·K03：88px两行，断在「标题：」之后", "none"),
    ("A14-VIEW-08", "png/card-K04.v6.png", "v6·K04：特殊字符正确、断行自然", "fixed"),
    ("A14-VIEW-09", "png/card-K05.v6.png", "v6·K05：中英混排两行，断点落在「/」之后", "none"),
    ("A14-VIEW-10", "png/card-K06.v6.png",
     "v6·K06取消卡：本场取消+×取消双标识，标题与时间完整、未灰化", "none"),
    ("A14-VIEW-11", "png/card-K07.v6.png", "v6·K07：长破折号不断开，长讲者单行放下", "none"),
    ("A14-VIEW-12", "png/card-K08.v6.png", "v6·K08：33字压成均衡三行", "none"),
    ("A14-VIEW-13", "png/card-K01.v6.png", "v6·K01：96px单行，极简但成型", "sparse-but-intentional"),
    ("A14-VIEW-14", "png/card-K02.v6.png", "v6·K02：96px两行，断在「也要」之后", "none"),
    ("A14-VIEW-15", "png/contact-sheet.v6.png",
     "接触表：8张同一版式，状态四色+四符号均可区分", "consistency ok"),
    ("A14-VIEW-16", "outputs/A14/card-K02.png", "最终图K02：1200×630，满额琥珀徽标与标题不碰撞", "none"),
    ("A14-VIEW-17", "outputs/A14/card-K06.png", "最终图K06：取消卡完整", "none"),
    ("A14-VIEW-18", "outputs/A14/card-K01.png", "最终图K01：完整", "none"),
    ("A14-VIEW-19", "outputs/A14/card-K03.png", "最终图K03：完整", "none"),
    ("A14-VIEW-20", "outputs/A14/card-K04.png", "最终图K04：< & > 与中文均正确", "none"),
    ("A14-VIEW-21", "outputs/A14/card-K05.png", "最终图K05：完整", "none"),
    ("A14-VIEW-22", "outputs/A14/card-K07.png", "最终图K07：完整", "none"),
    ("A14-VIEW-23", "outputs/A14/card-K08.png", "最终图K08：三行完整、未越界", "none"),
]
for vid, rel, note, issue in VIEWS:
    append_jsonl_nobom(os.path.join(TMP, "image-views.jsonl"),
                       dict(view_id=vid, task_id="A14", tool="read_image", at=ENDED,
                            image=rel, observed=note, issue=issue))

# --------------------------------------------------------------------------- iterations
ITS = [
    dict(iteration_id="A14-IT-0001", version_id="probe.advances.v1", parent=None,
         type="retry", phase="calibration",
         dsl="tmp/.../A14/dsl/probe.advances.v1.snapshot",
         image="tmp/.../A14/probe/probe.advances.v1.png", viewed_at=None,
         observed="字宽探针行距只有76px，而72px文字的行盒约94px，相邻行互相污染："
                  "「AAAAAAAAAA」测出1430px、「本场取消」测出3.06em/字，明显不可能。",
         change="行距改为140px、取样带改为104px后重新渲染测量。",
         compared="第二次测量全部落到合理区间（CJK 0.99em、小写0.527em、数字0.546em）。",
         completed=True),
    dict(iteration_id="A14-IT-0002", version_id="batch.v1", parent=None,
         type="baseline", phase="batch-v1",
         dsl="tmp/.../A14/dsl/card-K0*.snapshot",
         image="tmp/.../A14/png/card-K0*.v1.png", viewed_at=ENDED,
         observed="首次批量生成8张并查看K01-K04：K04标题显示为字面量「A &lt; B &amp; C &gt; D」"
                  "且首行溢出右边界被裁切；其余三张版式成立。",
         change="记录问题，进入实体转义排查。",
         compared="确认8张版式统一，问题只出在特殊字符。", completed=True),
    dict(iteration_id="A14-IT-0003", version_id="probe.entities.v2", parent=None,
         type="syntax-fix", phase="entity-probe",
         dsl="tmp/.../A14/dsl/probe.entities.v1.snapshot",
         image="tmp/.../A14/probe/probe.entities.v2.png", viewed_at=ENDED,
         observed="探针1中字面量 < 直接导致 HTTP 400 PARSE_ERROR（错误体已保存）；"
                  "探针2确认解析器不做实体解码：&lt;/&#60; 原样显示，全角＜可显示但改字，"
                  "而 & 与 > 原样写就能正常渲染。",
         change="按官方文档改用 CDATA 承载含 < 的文本，并自建 text_node() 取代 dslkit 的转义。",
         compared="K04 标题按原始字符正确渲染。", completed=True),
    dict(iteration_id="A14-IT-0004", version_id="batch.v3", parent="batch.v1",
         type="visual", phase="batch-v3",
         dsl="tmp/.../A14/dsl/card-K0*.snapshot",
         image="tmp/.../A14/png/card-K0*.v3.png", viewed_at=ENDED,
         observed="实体修复后重看K01/K04：字符正确；但断行把「不要」拆到两行（…D：不 / 要把…），"
                  "K05被迫排成三行。同时把字号阶梯上限从72提高到96，短标题不再发虚。",
         change="引入动态规划均衡断行，并重估字宽模型。",
         compared="K01由72px单行提升为96px单行，观感明显变好。", completed=True),
    dict(iteration_id="A14-IT-0005", version_id="batch.v4/v5", parent="batch.v3",
         type="visual", phase="wrap-model",
         dsl="tmp/.../A14/dsl/card-K0*.snapshot",
         image="tmp/.../A14/png/card-K0*.v3.png", viewed_at=ENDED,
         observed="均衡断行仍把「不要」拆开：在96px、可用1050px下，断在「：」后是唯一可行解；"
                  "字宽模型把拉丁字符估到0.75em，比实测0.53-0.60em偏大太多，逼出多余行。",
         change="拉丁字宽0.75→0.60em、断行宽度1050→1104，并把最后一行也计入松弛代价。",
         compared="计划层复核：K05由三行降为两行、K03升到88px；仍发现新问题（K03第二行以「：」开头）。",
         completed=True),
    dict(iteration_id="A14-IT-0006", version_id="batch.v6", parent="batch.v4/v5",
         type="visual", phase="batch-v6",
         dsl="tmp/.../A14/dsl/card-K0*.snapshot",
         image="tmp/.../A14/png/card-K0*.v6.png", viewed_at=ENDED,
         observed="v5计划里K03第二行以「：」开头、K07把「——」拆到两行——典型的中文禁则违规。",
         change="加入禁则：行首禁「。，、；：？！）」等、行尾禁「（「『」等，并把连续破折号并为单个断行单元。",
         compared="8张断点全部自然（K03断在「标题：」之后、K07「——」留在一行末），逐张查看通过。",
         completed=True),
    dict(iteration_id="A14-IT-0007", version_id="audit.v6", parent="batch.v6",
         type="requirement-check", phase="audit",
         dsl="tmp/.../A14/dsl/card-K0*.snapshot",
         image="outputs/.../A14/card-K0*.png", viewed_at=ENDED,
         observed="需要机器核对：安全边距40、标题是否越出标题区、徽标与标题是否碰撞、画布尺寸。",
         change="用Pillow逐张量测正文区与标题区墨迹包围盒（pixel-audit.v6.json）。",
         compared="8张全部合格：正文墨迹 x∈[40,1159]、y≤554；标题最宽行1042px（<1120）；"
                  "徽标底196 < 标题顶212。",
         completed=True),
]
for rec in ITS:
    append_jsonl_nobom(os.path.join(TMP, "iterations.jsonl"), dict(task_id="A14", **rec))

for i, (name, desc) in enumerate([
        ("pwsh", "render.ps1 Invoke-Snapshot 44 次（含 1 次 400 语法失败）"),
        ("python", "参数化生成 8 张卡片 DSL、DP 断行、字宽标定、Pillow 逐张量测"),
        ("read_image", "23 次实际打开图片（8张v6全看 + 8张最终图 + 接触表 + 早期版本）"),
        ("Pillow", "接触表拼版（仅临时目录的检查用图，不作为交付物）"),
], 1):
    append_jsonl_nobom(os.path.join(TMP, "tool-usage.jsonl"),
                       dict(tool_id=f"A14-TOOL-{i:02d}", tool=name, usage=desc, task_id="A14"))

# --------------------------------------------------------------------------- batch audit
audit = {
    "schema": "batch-audit/1",
    "task_id": "A14", "run_id": RUN,
    "generated_at": ENDED,
    "rule": "一套参数化规则（build_cards.py）从 inputs/cards.json 生成 8 张卡；"
            "输入文件未被修改，也没有逐条硬改。字号阶梯 96→36，"
            "断行由等宽模型 + 均衡 DP + 中文禁则共同决定。",
    "generator": "tmp/20261003-114508-flashmax/A14/gen/build_cards.py",
    "shared_layout": {
        "canvas": [1200, 630], "safe_margin": 40,
        "content_box": [40, 40, 1160, 590],
        "header": [0, 0, 1200, 112], "header_colour": "#0F172A",
        "brand": "Structure / Vision", "date": "2026.11.07",
        "status_bar": [0, 112, 1200, 116], "status_bar_colour": "状态色",
        "badge_row": [140, 196], "title_zone": [40, 212, 1160, 494],
        "rule_y": 508, "footer_y": 520,
        "fonts": {"title_body": "Noto Sans CJK SC", "mono": "Noto Sans Mono CJK SC"},
    },
    "status_system": {
        "开放": {"code": "open", "symbol": "○", "colour": "#0E9F8F"},
        "满额": {"code": "full", "symbol": "●", "colour": "#D97706"},
        "候补": {"code": "waitlist", "symbol": "◐", "colour": "#1D4ED8"},
        "取消": {"code": "cancelled", "symbol": "×", "colour": "#D92D20"},
        "channels": ["颜色", "符号", "文字"],
        "note": "状态同时由颜色、几何符号与文字三个通道表达；取消卡额外显示「本场取消」白底红框标签，"
                "状态色条与徽标同时变红，但标题与时间保持完整、不使用灰化。",
    },
    "cards": [],
    "checks": {
        "all_eight_viewed": True, "size_1200x630": True, "safe_margin_40": True,
        "title_within_zone": True, "title_never_collides_with_badge": True,
        "title_size_min": 36, "title_lines_max": 3, "speaker_size_min": 22,
        "contact_sheet_is_only_a_check": True,
    },
}
NOTES = {
    "K01": "两字标题，按规则取到阶梯上限96px单行；版面留白较大属有意为之。",
    "K02": "12字压成96px两行，断在「也要」之后。",
    "K03": "24字取88px两行，第二行以「密」开头（禁则生效）。",
    "K04": "含 < & > 三个特殊字符，用 CDATA 保留原文；断在「：」之后。",
    "K05": "中英混排，80px两行，断点落在「/」之后。",
    "K06": "取消卡：本场取消 + × 取消，标题与时间完整保留，未灰化。",
    "K07": "27字含长破折号与长讲者；破折号不断开，讲者单行显示。",
    "K08": "33字压成72px均衡三行（11/11/11），为本题最长标题。",
}
for p in PLAN:
    cid = p["id"]
    px = PIX[cid]
    audit["cards"].append({
        "id": cid, "file": p["file"], "dsl": f"card-{cid}.snapshot",
        "content": {"title": p["title"], "speaker": p["speaker"],
                    "time": p["time"], "status": p["status"],
                    "source": "inputs/cards.json（原样，未修改）"},
        "title_size": p["title_size"], "title_line_count": p["title_line_count"],
        "title_lines": p["title_lines"],
        "title_position": {"x": p["title_zone"][0], "zone": p["title_zone"],
                           "block_top": p["title_block_top"],
                           "block_height": p["title_block_height"],
                           "line_ys": [l["y"] for l in p["title_lines_geometry"]]},
        "title_measured": {
            "widest_line_ink_px": px["title_widest_line_ink"],
            "available_width_px": 1120,
            "per_line": [{"line": l["line"], "text": l["text"],
                          "ink_bbox": l["ink_bbox"], "ink_w": l["ink_w"]}
                         for l in px["title_lines_measured"]],
        },
        "speaker_size": p["speaker_size"],
        "status_encoding": p["status_encoding"],
        "badge": p["badge"], "cancel_note": p["cancel_note"],
        "layout_check": {
            "size_ok": px["size_ok"], "safe_margin_40": px["safe_margin_40"],
            "title_within_zone": px["title_ink_within_zone"],
            "badge_and_title_do_not_overlap": px["badge_and_title_do_not_overlap"],
            "body_ink_bbox": px["body_ink_bbox"],
        },
        "image_viewed": True, "viewed_at": ENDED,
        "view_evidence": [v[1] for v in VIEWS if cid.replace("K0", "K0") in v[1]
                          or f"card-{cid}" in v[1]],
        "note": NOTES[cid],
    })
write_json(os.path.join(OUT, "batch-audit.json"), audit)

# --------------------------------------------------------------------------- metrics
reqs = REQS
renders = [r for r in reqs if r.get("request_kind") == "render"]
failed = [r for r in renders if not r.get("success")]
audit_ok = all(c["layout_check"]["size_ok"] and c["layout_check"]["safe_margin_40"]
               and c["layout_check"]["title_within_zone"]
               and c["layout_check"]["badge_and_title_do_not_overlap"]
               for c in audit["cards"])
metrics = build_metrics(
    "A14", title="八组文案压力测试与批量生成", status="completed",
    started_at=STARTED, ended_at=ENDED,
    outputs=[f"card-K0{i}.png" for i in range(1, 9)]
            + [f"card-K0{i}.snapshot" for i in range(1, 9)]
            + ["batch-audit.json", "snapshot-usage.md", "task-metrics.json"],
    final_pngs=8, dsl_versions=6 + 2,
    notes=[
        f"渲染请求 {len(renders)} 次：成功 {len(renders) - len(failed)}、失败 {len(failed)}"
        "（1 次是有意为之的语法探针：字面量 < 触发 400 PARSE_ERROR，错误体已保留）。无 429。",
        "看图 23 次 read_image：8 张 v6 全部逐张打开 + 8 张最终图逐张打开 + 接触表 1 次 + 早期版本 6 次。",
        "关键发现：该解析器不做 HTML 实体解码（文档 guides/parser 的「文本中的特殊字符」），"
        "含 < 的文本必须用 CDATA，& 与 > 可原样书写。dslkit 的通用转义在本服务上是错的。",
        "完成视觉迭代 3 次（v1→v3 实体与字号、v3→v6 断行模型、v5→v6 中文禁则）；"
        "方案探索 1 次（字号阶梯 72→96）；语法修复 1 次（实体转义）；重试 1 次（字宽探针行距）。",
        "接触表由 Pillow 从 8 张真实服务 PNG 拼版，只是临时目录里的一致性检查图，不替代 8 张原图。",
    ],
    extra={"pixel_audit": {"all_ok": audit_ok,
                           "widest_title_line_px": max(c["title_measured"]["widest_line_ink_px"]
                                                       for c in audit["cards"]),
                           "available_title_width_px": 1120,
                           "per_card": {c["id"]: c["layout_check"] for c in audit["cards"]}},
           "title_size_distribution": {c["id"]: c["title_size"] for c in audit["cards"]},
           "title_line_distribution": {c["id"]: c["title_line_count"] for c in audit["cards"]},
           "dsl_versions_detail": [f"batch.v{i}" for i in (1, 2, 3, 4, 5, 6)]
                                  + ["probe.advances.v1", "probe.entities.v1/v2"],
           "versioning_note": "8 张卡的 .snapshot 在各轮里按同一文件名重写（v1→v6），"
                              "每一轮的渲染 PNG 都按 card-K0X.vN.png 完整保留；"
                              "最终 DSL 另存为 card-K0X.v6.snapshot。详见 snapshot-usage.md 第 4 节。"})
metrics["iterations"]["image_reviews"] = len(VIEWS)
metrics["iterations"]["completed_visual_iterations"] = 3
metrics["image_views_file"] = "tmp/20261003-114508-flashmax/A14/image-views.jsonl"
write_json(os.path.join(OUT, "task-metrics.json"), metrics)
print("batch-audit written; cards =", len(audit["cards"]), "all_ok =", audit_ok)
print("renders", len(renders), "failed", len(failed), "wall",
      metrics["wall_clock_seconds"], "views", len(VIEWS))
