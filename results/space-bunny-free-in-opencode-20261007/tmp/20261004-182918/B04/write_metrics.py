"""B04: build task-metrics.json from the real logs, then call wrapup."""
import io
import json
import os
import sys
from datetime import datetime

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "B04")
OUT = os.path.join(ROOT, "outputs", RUN, "B04")
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "B04"))
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import finalize  # noqa: E402
import state as S  # noqa: E402

START = "2026-10-05T18:48:00+08:00"
FIRST = "2026-10-05T19:22:00+08:00"
END = "2026-10-05T23:05:00+08:00"

m = finalize.build("B04", START, FIRST, END)

reqs = [json.loads(l) for l in io.open(os.path.join(TMP, "requests.jsonl"),
                                        encoding="utf-8") if l.strip()]
iters = [json.loads(l) for l in io.open(os.path.join(TMP, "iterations.jsonl"),
                                        encoding="utf-8") if l.strip()]
tools = [json.loads(l) for l in io.open(os.path.join(TMP, "tool-usage.jsonl"),
                                        encoding="utf-8") if l.strip()]
renders = [r for r in reqs if r["request_type"] == "render"]
others = [r for r in reqs if r["request_type"] != "render"]
summary = json.load(io.open(os.path.join(TMP, "render-summary.json"),
                            encoding="utf-8"))

import re
by_case = {}
for r in renders:
    m2 = re.search(r"[\\/]B04[\\/](case-\d\d)[\\/]", r.get("request_file") or "")
    if m2:
        by_case.setdefault(m2.group(1), []).append(r)
shared = [r for r in renders if not re.search(r"[\\/]B04[\\/]case-\d\d[\\/]",
                                              r.get("request_file") or "")]

case_metrics = []
for i in range(1, 11):
    cid = "case-%02d" % i
    rs = by_case[cid]
    ok = [r for r in rs if (r.get("content_type") or "").startswith("image/")]
    its = [x for x in iters if x.get("note", "").startswith(cid + " ")]
    png = os.path.join(OUT, cid, "final.png")
    case_metrics.append({
        "case_id": cid,
        "render_attempts": len(rs),
        "successful_renders": len(ok),
        "failed_renders": len(rs) - len(ok),
        "retry_requests": len([r for r in rs if (r.get("retry_attempt") or 0) > 0]),
        "request_ids": [r["request_id"] for r in rs],
        "final_request_id": ok[-1]["request_id"] if ok else None,
        "dsl_versions": len(ok),
        "dsl_bytes": summary[cid]["dsl_bytes"],
        "element_tags_estimate": summary[cid]["element_tags"],
        "iteration_records": len(its),
        "complete_visual_iterations": len([x for x in its
                                           if x.get("complete_visual_iteration")]),
        "baseline_and_non_visual_records": len([x for x in its
                                                if not x.get("complete_visual_iteration")]),
        "image_views_recorded": len([x for x in its if x.get("viewed_at")]),
        "final_png": "%s/final.png" % cid,
        "final_png_bytes": os.path.getsize(png),
        "dimensions": summary[cid]["dimensions"],
        "failed_request_ids": [r["request_id"] for r in rs if r not in ok],
    })

png_total = sum(c["final_png_bytes"] for c in case_metrics)
dsl_total = sum(c["dsl_bytes"] for c in case_metrics)

m["schema_version"] = 2
m["task_round"] = None
m["stop_reason"] = ("需求满足并完成视觉自检：十件全部实际看图并逐条核对完成标准，"
                    "跨件三组共享数字复核一致；不是达到某个请求或迭代次数。")
m["asset_policy"] = "dsl_primary_with_supporting_assets"
m["asset_policy_usage"] = ("本任务未使用任何辅助素材：十件均为纯 DSL 构造，"
                           "无 <Image> 节点、无外部图片文件。")
m["topic"] = "海洋酸化（ocean acidification）：「0.1」这个数字到底意味着什么"
m["counts"]["final_case_count"] = 10
m["counts"]["final_pngs"] = 10
m["counts"]["final_png_files"] = ["case-%02d/final.png" % i for i in range(1, 11)]
m["counts"]["image_views"] = len([x for x in iters if x.get("viewed_at")])
m["counts"]["image_views_note"] = (
    "含 4 次局部放大核对（crop.py 生成的 crops/*.png）："
    "final-c02-fillcheck 2×、final-c01-toc 1×、final-c03-top 1×、final-c09-bottom 1×。"
    "整图查看与局部放大的合计次数按本任务实际打开图像的次数计。")
m["counts"]["other_service_requests"] = len(others)
m["counts"]["document_requests"] = len([r for r in others
                                        if r["request_type"] == "document"])
m["counts"]["research_source_requests"] = len([r for r in others
                                               if r["request_type"]
                                               in ("research_source", "research_data")])
m["counts"]["other_tool_calls"] = len(tools)
m["counts"]["other_tool_calls_note"] = (
    "tool-usage.jsonl 记录 21 次非渲染工具事件：6 次 websearch、"
    "13 次真实 HTTP GET（含 3 次降级/失败）、以及 python 数据解析、算术推导、"
    "度量、PIL 放大与读尺寸、read 工具看图。HTTP 事件与 requests.jsonl 共享 ID，"
    "未重复计入请求消耗。")
m["counts"]["dsl_versions"] = len([r for r in renders
                                   if (r.get("content_type") or "").startswith("image/")])
m["rate_limit_or_queue_wait_seconds"] = None
m["rate_limit_or_queue_wait_note"] = (
    "全程无 429、无 503、无 Retry-After，因此没有限流等待；"
    "35 次成功响应均未返回 Server-Timing 头，可测的排队等待不存在可引用的数值，"
    "故记为未知而不是 0。")
m["user_feedback_wait_seconds"] = 0
m["user_feedback_wait_note"] = ("全程自驱视觉迭代：没有向用户请求反馈，也没有收到用户反馈。")
m["sum_of_request_durations_seconds"] = round(
    sum(r.get("duration_ms") or 0 for r in reqs) / 1000.0, 2)
m["note_on_wall_clock"] = (
    "墙钟 15420 秒包含研究、阅读来源、写脚本与反复看图；请求耗时之和只有约 112 秒，"
    "其余是本地时间与上下文推理时间。两者不应相加，也不能互相替代。")
m["usage"] = {
    "input_tokens": None,
    "output_tokens": None,
    "total_tokens": None,
    "image_input_usage": None,
    "image_input_unit": None,
    "cost": None,
    "currency": None,
    "billing_scope": None,
    "source": None,
    "unknown_fields_reason": (
        "open-snapshot 服务没有暴露任何 token / 计费指标接口，聊天平台也没有报告"
        "本任务的逐请求 token 或费用。因此全部记为 null，没有按字符数、响应字节数、"
        "请求次数或任何配额余量做估算。本任务未输入任何图像，故图像输入用量同样未知。"),
}
m["shared_preparation"] = {
    "render_requests": len(shared),
    "note": "共享准备不包含任何渲染请求：全部 43 次渲染都归属到具体 case。",
    "document_and_data_requests": [
        {"request_id": r["request_id"], "type": r["request_type"], "url": r["url"],
         "http_status": r["http_status"]} for r in others],
    "purpose": ("服务文档（ai-guide.md、snapshot 文档站）、服务字体列表（/fonts）、"
                "以及本特辑共用的 NOAA GML Mauna Loa 年均 CO2 数据文件与 "
                "NOAA / IPCC / Frontiers 四个研究页面。"),
}
m["case_metrics"] = case_metrics
m["tool_usage_summary"] = [
    {"tool": t["tool"], "purpose": t["purpose"], "affects": t["affects"],
     "at": t["ts"]} for t in tools]
m["outputs"] = ([{"path": "case-%02d/final.png" % i,
                   "dimensions": summary["case-%02d" % i]["dimensions"],
                   "bytes": summary["case-%02d" % i]["bytes"]} for i in range(1, 11)]
                + [{"path": "case-%02d/final.snapshot" % i,
                    "bytes": summary["case-%02d" % i]["dsl_bytes"]} for i in range(1, 11)]
                + [{"path": "case-%02d/case.md" % i} for i in range(1, 11)]
                + [{"path": "portfolio.json"}, {"path": "portfolio.md"},
                   {"path": "gallery.html"}, {"path": "sources.json"},
                   {"path": "editorial-note.md"}, {"path": "snapshot-usage.md"},
                   {"path": "task-metrics.json"}])
m["totals"] = {
    "final_png_bytes": png_total,
    "final_dsl_bytes": dsl_total,
    "final_svg_or_webp_count": 0,
    "external_assets_used": 0,
    "image_nodes_in_dsl": 0,
}
m["logs"] = {
    "requests": "tmp/%s/B04/requests.jsonl" % RUN,
    "iterations": "tmp/%s/B04/iterations.jsonl" % RUN,
    "tool_usage": "tmp/%s/B04/tool-usage.jsonl" % RUN,
    "render_summary": "tmp/%s/B04/render-summary.json" % RUN,
    "research_notes": "tmp/%s/B04/research-notes.md" % RUN,
    "failed_responses_dir": "tmp/%s/B04/responses" % RUN,
    "crops_dir": "tmp/%s/B04/crops" % RUN,
}
m["rounds"] = [{"round": "round-01", "scope": "全部十件，含 35 个 DSL 版本与 37 次看图"}]
m["unresolved_issues"] = [
    "四篇核心文献（Jiang 2023 / Kroeker 2013 / Bednaršek 2014 / IPCC SROCC 第5章）"
    "只取得 websearch 检索结果摘要，未直接抓取全文；case-06 / case-07 / case-08 "
    "的数值需按全文再核对一次口径。",
    "pmc.ncbi.nlm.nih.gov/articles/PMC6901524/ 返回 reCAPTCHA 质询页而非正文，"
    "已排除出已读来源，该文结论未用于任何作品。",
    "NOAA Ocean Today 页抓取超时（TimeoutError），仅保留检索摘要，"
    "只支撑 case-10 的一条「来源结论」级判定。",
    "pmel.noaa.gov 的两个页面 HTTP 404，相关事实改由 NOAA 可访问页面提供。",
    "化学式使用 ASCII 记法而非下标（DejaVu Sans Mono 的下标字符未在本任务验证）。",
    "case-05 的「恢复需要多久」为有意的空缺：来源只给定性判断，本任务未取得"
    "可引用的恢复模型结果。",
    "case-09 有五行标注「未取」，这是本任务的记录状态而非 NOAA 的数据缺失。",
    "元素个数按 <Positioned>+<Container>+<Text> 标签计数，是上界估计而非服务精确值；"
    "十件为 414–988，均远低于 4096 上限。",
]
m["final_case_count"] = 10

with io.open(os.path.join(OUT, "task-metrics.json"), "w", encoding="utf-8",
             newline="\n") as fh:
    json.dump(m, fh, ensure_ascii=False, indent=2)
print("task-metrics.json written:",
      json.dumps({k: m["counts"][k] for k in
                  ("render_requests", "successful_render_requests",
                   "failed_render_requests", "retry_requests", "image_views",
                   "completed_visual_iterations", "final_case_count")},
                 ensure_ascii=False))
print("png bytes", png_total, "dsl bytes", dsl_total)
print("wall", m["wall_clock_seconds_total"], "first", m["wall_clock_seconds_to_first_usable_image"],
      "reqsum", m["sum_of_request_durations_seconds"])
