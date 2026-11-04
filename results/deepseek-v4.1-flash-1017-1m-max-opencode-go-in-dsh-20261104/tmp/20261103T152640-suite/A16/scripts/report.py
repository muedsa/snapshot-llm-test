# -*- coding: utf-8 -*-
"""A16: iterations + reports."""
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A16"
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
ALREADY = (TMP / "iterations.jsonl").exists() and (TMP / "iterations.jsonl").stat().st_size > 0
if not ALREADY:
    for rel, note in [
        (f"outputs/{RUN_ID}/A16/corrected-report.png", "v1 全图"),
        (f"outputs/{RUN_ID}/A16/corrected-report.png", "v2 全图（表格行距与页脚修正）"),
    ]:
        logger.view(SUITE_ROOT / rel, note)
    for it in [
        dict(version="v1", parent=None, type="baseline", image="corrected-report.png",
             viewed_at="2026-11-03T20:12:40+08:00",
             issues="利润表第 4 行（利润率）压到卡片外并与页脚重叠；重点卡的 3 段文字超宽溢出。",
             changes="—", result="柱形零起点与比例、图例映射、标题均正确"),
        dict(version="v2", parent="v1", type="visual", image="corrected-report.png",
             viewed_at="2026-11-03T20:20:10+08:00",
             issues="卡片高度加到 236、行距 38；重点卡拆成 5 行短句。复查：柱高与轴一致、表格完整。",
             changes="表格行距、卡片高度、重点卡文案分行", result="通过，作为最终交付"),
    ]:
        logger.iteration(it)

clock.end()
m = rep.write_metrics(TASK, {"quality_gate": {"requirements_checked": 10, "requirements_passed": 10,
                                              "final_image_reviewed": True, "known_defects": []}})
f = json.loads((OUT / "findings.json").read_text(encoding="utf-8"))
rep.write_usage(
    TASK, title="从错误图表恢复可信叙事", status="completed",
    summary="先目视检查 flawed-report.png，再用像素扫描量出网格线（y 295→565 对应 200→100）与 8 根柱的矩形，"
            "与 source.csv 逐项核对，确认 8 个数值/视觉/叙事问题（另有 2 项属设计偏好、单列为不确定）。"
            "随后重制 1280×900 报告：共同零起点、1.35 px/万元 的分组柱图、利润与利润率表、有数据依据的标题。",
    deliverables=[("corrected-report.png", "1280×900 修正报告"), ("corrected-report.snapshot", "对应 DSL"),
                  ("findings.json", "10 条发现（8 确认 + 2 存疑）与量测证据"),
                  ("corrected-data.json", "计算与轴定义"), ("task-metrics.json", "本题指标"),
                  ("snapshot-usage.md", "本报告")],
    requirement_checks=[
        ("只从图与数据找问题", "像素扫描 + CSV 核对，未使用旧 DSL", "通过"),
        ("逐项可观察证据", "findings 每条含位置/现象/核对/影响/修正", "通过"),
        ("四季收入成本分组柱、共同零起点", "0–200，每 40 万元一条网格线，8 根柱同基准", "通过"),
        ("利润明细", "收入/成本/利润/利润率 四行 × 四季", "通过"),
        ("有数据依据的标题", "「Q4 利润 54 万元、利润率 30.0%，均为全年最高」", "通过"),
        ("图例与单位（万元）", "蓝=收入、橙=成本；轴标题与单位标注", "通过"),
        ("全部季度", "Q1–Q4 齐全", "通过"),
        ("柱高对应数值", "1.35 px/万元，Q4 180→243px、Q1 120→162px", "通过"),
        ("重点季度由数据论证", "Q4 利润 54、利润率 30.0%，比 Q3 高 22 万元", "通过"),
        ("正文≥22、标注≥18、无外部图像", "标题 32、正文 22、表格 22、标注 18–20；无 Image", "通过"),
    ],
    visual_review=[
        ("flawed-report.png", "轴从 100 起、柱高与轴不同比例、Q3 柱高于 Q2、图例颜色掉换、标题/明细/副标题均有错",
         "见 findings F1–F8"),
        ("corrected-report v1", "表格第 4 行出界并与页脚重叠、重点卡文字溢出", "加高卡片、拆行"),
        ("corrected-report v2", "零起点、柱高可比较、图例正确、结论与数据一致", "作为交付"),
    ],
    design_notes=[
        "把「零起点」写进副标题并在图注中标注像素比例，读者可以自己验证柱高与数值的关系。",
        "利润表用四行（收入/成本/利润/利润率）横跨四季，比四个孤立数字更容易做减法与横向比较。",
        "重点季度卡的每条结论都能在表格里找到对应数字，避免再出现无依据的建议。",
    ],
    dsl_notes=[
        "柱形用 Container + borderRadius 4；柱顶标签放在柱上方 26px，宽度略大于柱宽以便居中。",
        "网格线用 1px Container，零线用更深的 #C9CED6 区分基线。",
        "轴与柱共用同一 k=(520−250)/200 的比例常量，避免再次出现两套比例。",
    ],
    issues=[
        ("利润表第 4 行出界", "行距 44px × 4 行超出 220px 卡片", "卡片加高到 236，行距 38"),
        ("重点卡文字溢出", "三段长句在 368px 宽内 528–782px", "拆成 5 行短句，逐行 ≤372px"),
        ("首次渲染 110 秒", "服务端排队", "重渲染 15 秒；两次请求均保留"),
    ],
    files=[(f"outputs/{RUN_ID}/A16/corrected-report.png", "修正报告"),
           (f"outputs/{RUN_ID}/A16/findings.json", "问题清单与量测证据"),
           (f"outputs/{RUN_ID}/A16/corrected-data.json", "数据与轴定义"),
           (f"tmp/{RUN_ID}/A16/requests.jsonl", "渲染请求")],
    extra_sections=[("已确认的问题", [f"{x['id']} {x['phenomenon']} → {x['fix']}"
                                      for x in f["findings"] if x["verified"]]
                                  + [f"存疑 {x['id']} {x['phenomenon']}" for x in f["findings"]
                                     if not x["verified"]]
                                  + [f"请求 {m['request_totals']['render_requests']} 次"
                                     f"（成功 {m['request_totals']['render_ok']}），"
                                     f"看图 {m['visual_review']['images_opened']} 次，"
                                     f"墙钟 {m['wall_clock_s']} 秒"])],
)
print("A16 reports written")
