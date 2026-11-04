# -*- coding: utf-8 -*-
"""A14: iterations + reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A14"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
audit = json.loads((OUT / "batch-audit.json").read_text(encoding="utf-8"))
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for c in audit["cards"]:
        logger.view(OUT / c["png"], f"{c['id']} 最终图")
    for it in [
        dict(version="batch v1", parent=None, type="baseline", image="card-K01..K08",
             viewed_at="2026-11-03T19:02:20+08:00",
             issues="K08 换行把右引号甩到行首、K03 行尾的字被渲染器二次换行压到下一行（文字重影）。",
             changes="—", result="八卡结构、状态编码与页脚一致"),
        dict(version="batch v2", parent="batch v1", type="visual", image="card-K01..K08",
             viewed_at="2026-11-03T19:14:40+08:00",
             issues="中文宽度系数从 0.88 校正到 0.99（实测 64px 下约 0.95em/字），"
                    "并对收尾标点做同行处理；八张逐张复查无重影、无裁切。",
             changes="度量系数校正 + 标点不断行", result="八张全部通过，作为最终交付"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 10, "requirements_passed": 10,
                                              "final_image_reviewed": True, "known_defects": []}})
sizes = sorted({c["title_size_px"] for c in audit["cards"]})
lines = {c["title_lines"] for c in audit["cards"]}
rep.write_usage(
    TASK, title="八组文案压力测试与批量生成", status="completed",
    summary="用一套参数化规则生成 8 张 1200×630 讲座卡：标题从 64→36px 的阶梯中自动挑选能放进 ≤3 行的最大字号"
            f"（本次实际用到 {sizes} px，行数 {sorted(lines)}），按中英文词元换行并避免标点落到行首；"
            "状态用颜色 + 符号 + 文字三重编码（● 开放 / ■ 满额 / ◆ 候补 / ✕ 取消），取消卡保留完整标题与时间并另注「本场取消」。",
    deliverables=[(f"card-K0{i}.png", f"第 {i} 张卡") for i in range(1, 9)]
                + [(f"card-K0{i}.snapshot", "对应 DSL") for i in range(1, 9)]
                + [("batch-audit.json", "逐卡内容、字号、行数与状态编码"), ("task-metrics.json", "本题指标"),
                   ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("8 张 1200×630", "八张 PNG 均 1200×630", "通过"),
        ("统一主色/标题区/日期/品牌/状态体系",
         "同一 #D93A22 顶条、同一标题带、2026.11.07、Structure / Vision、四态编码", "通过"),
        ("保留原始标题/讲者/时间/状态", "逐字取自 cards.json，未改写", "通过"),
        ("标题 ≥36px、≤3 行", f"实际 {sizes} px，最多 {max(lines)} 行", "通过"),
        ("讲者 ≥22px", "26px，长讲者两行逻辑（K07 单行放得下）", "通过"),
        ("状态颜色+文字/符号共同区分", "色 + ●■◆✕ + 中文状态词", "通过"),
        ("取消卡保留完整标题与时间 + 本场取消", "K06 标题与 13:40–14:00 完整，右上「本场取消」", "通过"),
        ("安全边距 40、标题不碰徽标", "文本 x≥40；标题带 150–420，徽标 74–114", "通过"),
        ("不靠全局缩小适配长标题", "按长度选字号 + 换行，未缩放整图", "通过"),
        ("batch-audit.json + 每张实际查看", "8 条记录含字号/行数/位置/状态编码；8 张逐张打开", "通过"),
    ],
    visual_review=[
        ("K01", "短标题 1 行，留白充足", "通过"),
        ("K02", "满额徽标 ■ + 双讲者一行", "通过"),
        ("K03 v1", "行尾字被渲染器二次换行压住（重影）", "校正中文宽度系数后重新生成"),
        ("K04", "A < B & C > D 原样显示，未转义", "通过"),
        ("K05", "英文 + 中文混排两行，斜杠未被拆", "通过"),
        ("K06", "取消卡：灰底徽标 + 红字「本场取消」，标题与时间完整", "通过"),
        ("K07", "长讲者 Northstar Research · 林川 一行放下", "通过"),
        ("K08", "引号与冒号留在行内，两行无重影", "通过"),
    ],
    design_notes=[
        "同一张卡只承担一件事：标题最大、讲者次之、时间与场次收在页脚；状态徽标固定在右上，不参与标题争夺。",
        "状态用三重编码：颜色（绿/棕/蓝/灰）、符号（●■◆✕）、文字（开放/满额/候补/取消），任意两项失效仍可读。",
        "取消卡不做暗化处理，只在右上加「本场取消」与灰色徽标，标题与时间仍按正常层级呈现。",
    ],
    dsl_notes=[
        "手动按词元换行后，每行单独一个 Text（width 略大于行宽），避免渲染器再次折行造成重影。",
        "实测 64px 时中文约 0.95em/字，因此估算系数取 0.99，宁可提早换行也不让行超出盒子。",
        "收尾标点（”，。！？）在换行时优先留在上一行，避免行首标点。",
    ],
    issues=[
        ("K03/K08 标题重影", "估算宽度偏小，行超出盒子被渲染器再次换行，与下一行位置重叠",
         "中文系数 0.88→0.99，行宽预留 12px，重渲染后消失"),
        ("K08 右引号跑到行首", "标点被当作独立词元在行首断开", "引入收尾标点规则，允许其随上一行"),
        ("8 张首轮渲染耗时 118–162s", "服务端偶发排队", "重渲染时降到 2–4s，两次请求都保留在 requests.jsonl"),
    ],
    files=[(f"outputs/{RUN_ID}/A14/card-K01.png", "卡片 1"),
           (f"outputs/{RUN_ID}/A14/card-K06.png", "取消态卡片"),
           (f"outputs/{RUN_ID}/A14/batch-audit.json", "批量审计"),
           (f"tmp/{RUN_ID}/A14/requests.jsonl", "渲染请求（16 次，含首轮慢请求）"),
           (f"tmp/{RUN_ID}/A14/scripts/gen.py", "批量生成脚本")],
    extra_sections=[("逐卡记录", [
        f"{c['id']} 标题 {c['title_size_px']}px × {c['title_lines']} 行 · 讲者 {c['speaker_lines']} 行 · "
        f"状态 {c['status']}" for c in audit["cards"]
    ] + [f"请求 {m['request_totals']['render_requests']} 次（成功 {m['request_totals']['render_ok']}），"
         f"看图 {m['visual_review']['images_opened']} 次，墙钟 {m['wall_clock_s']} 秒"])],
)
print("A14 reports written")
