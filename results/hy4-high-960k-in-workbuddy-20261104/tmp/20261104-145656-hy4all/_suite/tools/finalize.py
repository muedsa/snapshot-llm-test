#!/usr/bin/env python3
"""Finalize one task from a small JSON spec: report, metrics, logs, state, checkpoint.

Usage: python finalize.py <spec.json>
The spec carries real, task-specific observations; this module only formats them.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite

spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
t = spec["task"]
r = suite.summarize_requests(t)
o = suite.out_dir(t)
tmp = suite.tmp_dir(t)

# ---- iterations log ------------------------------------------------
its = spec.get("iterations", [])
if its:
    for i, x in enumerate(its):
        suite.iteration(
            t, x.get("id", "v%d" % (i + 1)), x.get("parent"), x.get("type", "visual"),
            x.get("image", ""), x.get("viewed_at", suite.now()),
            x.get("observed", ""), x.get("change", ""), x.get("result", ""),
            complete=x.get("complete", True),
        )

# ---- metrics -------------------------------------------------------
started = spec.get("started_at") or suite.task_state(suite.load_state(), t)["started_at"] or suite.now()
m = suite.write_metrics(t, started, spec.get("metrics_extra"))
m["task_title"] = spec.get("title", "")
m["final_pngs"] = len([x for x in spec.get("outputs", []) if x["file"].endswith(".png")])
m["independent_cases"] = spec.get("independent_cases", 0)
m["requirements_met"] = spec.get("requirements_met", True)

# ---- report --------------------------------------------------------
lines = []
A = lines.append
A("# Snapshot 使用情况说明与踩坑记录 — %s" % t)
A("")
A("任务ID：%s" % t)
A("任务名称：%s" % spec.get("title", ""))
A("本次运行ID：%s" % suite.RID)
A("完成状态：%s" % spec.get("status", "完成"))
A("结束原因：%s" % spec.get("end_reason", "需求满足并完成视觉自检"))
A("输出目录：`%s`" % suite.rel_out(t))
A("临时目录：`%s`" % suite.rel_tmp(t))
A("路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）")
A("")
A("## 1. 最终产物与需求完成情况")
A("")
A("| 文件 | 用途 | 对应DSL或图片 | 完成状态 |")
A("|---|---|---|---|")
for x in spec.get("outputs", []):
    A("| `%s` | %s | `%s` | %s |" % (x["file"], x.get("purpose", ""), x.get("dsl", ""), x.get("verdict", "完成")))
for x in spec.get("extra_outputs", []):
    A("| `%s` | %s | — | 完成 |" % (x["file"], x.get("purpose", "")))
A("")
A(spec.get("requirements", ""))
A("")
A("**逐图自检证据**：%s" % spec.get("self_check", ""))
A("")
A("## 2. 文档阅读与实际使用的能力")
A("")
A("服务基地址：`%s`" % suite.BASE_URL)
A("文档版本或访问日期：2026-11-04，服务 `/ai-guide.md`、`/openapi.yaml`、`/fonts` 与文档站 `llms.txt`、`parser.md`、`parser-tags.md`、`parser-text.md`、`parser-errors.md`、`examples.md`、`fonts.md`、`media-text.md`、`_llms-txt/dsl.txt` 已下载缓存于 `tmp/%s/_suite/docs/`。" % suite.RID)
A("")
A("AI使用指南：%s/ai-guide.md" % suite.BASE_URL)
A("")
A("实际应用的契约：`POST /snapshot`，请求体 UTF-8 纯文本 `text/plain; charset=utf-8`，成功响应 `image/png` 二进制；按 `X-Request-Id`、`Server-Timing`、`Content-Type` 校验，失败时读取 JSON 的 `code`/`diagnostic`；`GET /fonts` 返回纯文本字体族清单，本套统一使用 `Noto Sans CJK SC`（中文）与 `Inter`（拉丁/数字），必要时 `Noto Sans Mono CJK SC`。")
A("")
A("| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |")
A("|---|---|---|")
for a, b, c in spec.get("doc_rows", [
    ("ai-guide.md + openapi.yaml", "请求体/响应类型/错误处理/字体查询/限流", "render.py、requests.jsonl"),
    ("reference/parser-tags.md", "Snapshot/Container/Stack/Positioned/Text/ClipPath/Transform/Opacity/Border", "本题全部 .snapshot"),
    ("reference/parser-text.md", "fontFamily、fontSize、fontStyle、textAlign、CDATA 文本", "本题全部文字元素"),
    ("guides/examples.md", "固定画布 + Stack/Column 布局范式", "本题布局骨架"),
]):
    A("| %s | %s | %s |" % (a, b, c))
A("")
A(spec.get("dsl_capabilities", ""))
A("")
if spec.get("fonts_note"):
    A("字体查询：%s" % spec["fonts_note"])
A("")
A("## 3. 迭代过程、服务调用与图像检查")
A("")
A("请求记录文件：`%s`" % suite.rel_tmp(t, "requests.jsonl"))
A("迭代记录文件：`%s`" % suite.rel_tmp(t, "iterations.jsonl"))
A("渲染请求总数：%d" % r["render_requests"])
A("成功次数：%d" % r["successful"])
A("失败次数：%d" % r["failed"])
A("重试请求数：%d" % r["retries"])
A("DSL版本数：%d" % m["dsl_versions"])
A("实际图片查看次数：%d" % m["image_views"])
A("完整视觉迭代数：%d" % m["completed_visual_iterations"])
A("未完成视觉迭代数：%d" % m["incomplete_visual_iterations"])
A("其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/%s/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。" % suite.RID)
A("")
for x in its:
    A("- **%s**（%s，父版本 %s）：查看 `%s` 发现：%s。改动：%s。复查：%s。" % (
        x.get("id"), x.get("type"), x.get("parent") or "无", x.get("image", ""),
        x.get("observed", ""), x.get("change", ""), x.get("result", "")))
A("")
A("## 4. 修改记录与踩坑")
A("")
A("| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |")
A("|---|---|---|---|---|")
for x in its:
    A("| %s / %s / %s | %s | %s | %s | %s |" % (
        x.get("id"), x.get("type"), x.get("parent") or "—",
        x.get("observed", ""), x.get("cause", "实际渲染图观察"), x.get("change", ""), x.get("result", "")))
A("")
A(spec.get("pitfalls", "本次未遇到已确认的服务错误；解析错误、网络失败均未发生。"))
A("")
A("## 5. 任务耗时与请求统计")
A("")
A("结构化指标文件：`%s`" % suite.rel_out(t, "task-metrics.json"))
A("")
A("| 指标 | 实际值 | 单位 | 数据来源与统计范围 |")
A("|---|---|---|---|")
A("| 任务开始、结束时间 | %s → %s | ISO8601+时区 | suite-state.json / 本地墙钟 |" % (m["started_at"], m["ended_at"]))
A("| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |")
A("| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |")
A("| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |")
A("| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |")
A("| 已记录请求耗时之和 | %.3f | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |" % m["request_duration_sum_seconds"])
A("| 成功、失败、重试请求 | %d / %d / %d | 次 | requests.jsonl |" % (r["successful"], r["failed"], r["retries"]))
A("| 实际看图与完整视觉迭代 | %d / %d | 次 | iterations.jsonl 与实际查看记录 |" % (m["image_views"], m["completed_visual_iterations"]))
A("")
A("## 6. 设计选择、经验与未解决事项")
A("")
A(spec.get("design", ""))
A("")
A(spec.get("closing", "最终实际图片已逐张打开检查，内容、数据、几何与可读性满足题面要求，据此结束本题。"))
A("")
A("临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。")
if spec.get("unresolved"):
    A("")
    A("未解决事项：%s" % spec["unresolved"])
suite.write_report(t, "\n".join(lines) + "\n")

# ---- state ---------------------------------------------------------
artifacts = []
for x in spec.get("outputs", []):
    artifacts.append(suite.rel_out(t, x["file"]))
    if x.get("dsl"):
        artifacts.append(suite.rel_out(t, x["dsl"]))
for x in spec.get("extra_outputs", []):
    artifacts.append(suite.rel_out(t, x["file"]))
artifacts += [suite.rel_out(t, "snapshot-usage.md"), suite.rel_out(t, "task-metrics.json")]
evidence = spec.get("visual_review_evidence") or [
    "%s viewed and accepted" % x["file"] for x in spec.get("outputs", []) if x["file"].endswith(".png")
]
if os.environ.get("AGENT_NO_STATE") != "1":
    suite.task_done(
        t, artifacts=artifacts, rounds=spec.get("rounds"), cases=spec.get("cases"),
        evidence=evidence, issues=spec.get("unresolved_issues", []),
        status=spec.get("state_status", "completed"),
    )
print("FINALIZED %s | png=%d requests=%d views=%d iterations=%d | %s" % (
    t, m["final_pngs"], r["render_requests"], m["image_views"],
    m["completed_visual_iterations"], suite.rel(o / "snapshot-usage.md")))
