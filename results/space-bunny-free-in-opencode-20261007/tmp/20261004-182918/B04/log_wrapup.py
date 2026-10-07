"""B04: required final step — record the iteration log already written, generate
task-metrics.json, and update the suite state with cases=[case-01..case-10].
"""
import io
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "B04")
OUT = os.path.join(ROOT, "outputs", RUN, "B04")
sys.path.insert(0, r"tmp\%s\_suite" % RUN)
import wrapup  # noqa: E402

CST = timezone(timedelta(hours=8))
END = datetime.now(CST).isoformat(timespec="seconds")

cases = ["case-%02d" % i for i in range(1, 11)]
summary = json.load(io.open(os.path.join(TMP, "render-summary.json"),
                            encoding="utf-8"))
artifacts = []
for c in cases:
    s = summary[c]
    artifacts += ["outputs/%s/B04/%s/final.png" % (RUN, c),
                  "outputs/%s/B04/%s/final.snapshot" % (RUN, c),
                  "outputs/%s/B04/%s/case.md" % (RUN, c)]
artifacts += ["outputs/%s/B04/%s" % (RUN, f) for f in
              ("portfolio.json", "portfolio.md", "gallery.html", "sources.json",
               "editorial-note.md", "snapshot-usage.md", "task-metrics.json")]

evidence = [
    "每件用 read 工具实际打开 PNG 查看：case-01..10 共 28 次整图查看，"
    "记录在 tmp/%s/B04/iterations.jsonl 的 observed 字段" % RUN,
    "局部放大核对 4 次：crops/final-c02-fillcheck.png（2×，确认半透明填充条带消失）、"
    "crops/final-c01-toc.png（1×，十格阅读顺序与编号一致）、"
    "crops/final-c03-top.png（1×，对数竖尺刻度与插图标签）、"
    "crops/final-c09-bottom.png（1×，NOAA 局限面板三行文字）",
    "跨件一致性复核：1750 pH 8.19 / 2010 pH 8.07 在 case-03/04/05/06 一致；"
    "2100 SSP1-1.9 8.06 与 SSP5-8.5 7.68 在 case-04/05/06 一致；"
    "Ωarag 2010 全球 3.0 / 热带 3.4–3.6 / 极地 1.5–1.9、2100 2.9 与 1.6 "
    "在 case-06 与 case-07 一致",
    "数据溯源复核：case-01 与 case-02 的 67 个数据点全部由下载的 "
    "research/gml-co2-annmean-mlo.txt 解析，端点 315.98 / 427.35 与文件一致",
    "诚实性复核：SSP2-4.5 与 SSP3-7.0 的 2100 端点在 case-06 标注「未取」且无任何线条相连；"
    "case-09 有五行标注「未取」并在页脚说明「未取不是 NOAA 的分类」；"
    "case-05 的「恢复需要多久」为画布上有意留空的紫色面板",
    "语法修复复核：8 次 400 PARSE_ERROR 的响应原文保留在 tmp/%s/B04/responses/" % RUN,
]

unresolved = [
    "四篇核心文献（Jiang 2023 / Kroeker 2013 / Bednaršek 2014 / IPCC SROCC 第5章）"
    "只取得 websearch 检索摘要，未直接抓取全文",
    "pmc.ncbi.nlm.nih.gov/PMC6901524 返回 reCAPTCHA 质询页，已排除出已读来源",
    "NOAA Ocean Today 页抓取超时，仅保留摘要，只支撑一条来源结论级判定",
    "pmel.noaa.gov 两个页面 HTTP 404，相关事实改由 NOAA 可访问页面提供",
    "化学式用 ASCII 记法而非下标（DejaVu Sans Mono 下标字符未在本任务验证）",
    "case-05「恢复需要多久」为有意的空缺；case-09 五行「未取」为本任务的记录状态",
    "元素个数按标签计数，是上界估计而非服务精确值（414–988，远低于 4096）",
]

# wrapup re-writes task-metrics.json from the logs; the hand-enriched version is
# written afterwards by write_metrics.py, so run wrapup FIRST here and then
# re-apply the enriched metrics.
res = wrapup.wrapup(
    task_id="B04",
    started="2026-10-05T18:48:00+08:00",
    first_image="2026-10-05T19:22:00+08:00",
    ended=END,
    iterations=[],          # already appended by log_iterations.py
    artifacts=artifacts,
    visual_evidence=evidence,
    unresolved=unresolved,
    notes=("十件独立完整主作品，全部为 POST /snapshot 的真实响应字节，纯 DSL 构造，"
           "无 <Image>、无外部素材。自选主题「海洋酸化」，13 条来源全部记录取得方式"
           "（含 3 处降级与 2 处 404）。35 成功渲染 / 8 次 400 / 0 重试 / 32 次看图。"),
    status="completed",
    rounds=["round-01"],
    cases=cases,
)
print("wrapup done ->", os.path.join(OUT, "task-metrics.json"))
print("wall_clock_seconds_total =", res.get("wall_clock_seconds_total"))
st = S_state = None
sys.path.insert(0, r"tmp\%s\_suite" % RUN)
import state as S  # noqa: E402
t = S.task("B04")
print("suite status:", t["status"], "| cases:", len(t["completed_cases"]),
      "| artifacts:", len(t["artifacts"]))
