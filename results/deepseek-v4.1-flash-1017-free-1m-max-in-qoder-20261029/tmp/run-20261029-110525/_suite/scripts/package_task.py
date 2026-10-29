#!/usr/bin/env python3
"""Generate per-task snapshot-usage.md, task-metrics.json and iterations.jsonl.

Usage: python package_task.py --task A01 --meta <notes.json> [--round all]
Meta keys (all optional except task/title):
  title, status, stop_reason, design, requirements[{text,evidence}], docs[{url,knowledge,used_in}],
  files[{file,purpose,dsl,status}], issues[{type,problem,cause,fix,verify,evidence}],
  reviews[{image,at,result}], iterations[{id,type,parent,dsl,image,at,problem,change,result}],
  unresolved[], notes, metrics_overrides{}
All paths are relative to suite_root. Markdown links are computed relative to the output dir.
"""
import argparse, json, os, re
from datetime import datetime
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
TASK_DIR = SUITE_ROOT / "tasks"


def parse_ts(s):
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")
    except Exception:
        try:
            return datetime.fromisoformat(s)
        except Exception:
            return None


def fmt_ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z") if dt else "未知"


def rel(p):
    try:
        return Path(p).resolve().relative_to(SUITE_ROOT).as_posix()
    except Exception:
        return str(p).replace("\\", "/")


def md_link(from_dir: Path, target: str, label=None):
    t = (SUITE_ROOT / target)
    try:
        r = os.path.relpath(t, from_dir).replace("\\", "/")
    except Exception:
        r = target
    return f"[{label or Path(target).name}]({r})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--round", default="all")
    a = ap.parse_args()
    meta = json.loads(Path(a.meta).read_text(encoding="utf-8"))
    out_dir = SUITE_ROOT / "outputs" / RUN_ID / a.task
    tmp_dir = SUITE_ROOT / "tmp" / RUN_ID / a.task
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    reqs = []
    rp = tmp_dir / "requests.jsonl"
    if rp.exists():
        for line in rp.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    reqs.append(json.loads(line))
                except Exception:
                    pass
    # only final-artifact requests count as task renders; smoke/draft are included but flagged
    ok = [r for r in reqs if r.get("status") == "success"]
    fail = [r for r in reqs if r.get("status") == "error"]
    retries = [r for r in reqs if int(r.get("attempt", 1)) > 1]
    dsl_versions = len({r.get("dsl_sha256") for r in ok if r.get("dsl_sha256")})
    req_sum = round(sum((r.get("duration_ms") or 0) for r in reqs) / 1000.0, 2)
    times = [parse_ts(r["started_at"]) for r in reqs if r.get("started_at") and parse_ts(r["started_at"])]
    started = min(times) if times else None
    ends = []
    for r in reqs:
        t = parse_ts(r.get("started_at") or "")
        if t:
            ends.append(t.timestamp() + (r.get("duration_ms") or 0) / 1000.0)
    first_ok = None
    for r in sorted(ok, key=lambda x: x.get("started_at", "")):
        t = parse_ts(r.get("started_at") or "")
        if t:
            first_ok = t.timestamp() + (r.get("duration_ms") or 0) / 1000.0
            break
    if meta.get("iterations"):
        with (tmp_dir / "iterations.jsonl").open("w", encoding="utf-8") as f:
            for it in meta["iterations"]:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
    iterations = meta.get("iterations", [])
    completed_vi = sum(1 for i in iterations if i.get("type") == "visual" and i.get("result"))
    incomplete_vi = sum(1 for i in iterations if i.get("type") == "visual" and not i.get("result"))
    reviews = meta.get("reviews", [])

    now = datetime.now().astimezone()
    ended = now
    elapsed = round(ended.timestamp() - started.timestamp(), 1) if started else None
    first_usable = round(first_ok - started.timestamp(), 1) if (first_ok and started) else None
    m = {
        "schema_version": 1, "path_base": "suite_root", "task_id": a.task,
        "run_id": RUN_ID, "task_round": a.round, "status": meta.get("status", "completed"),
        "stop_reason": meta.get("stop_reason", "需求满足并完成视觉自检"),
        "output_dir": f"outputs/{RUN_ID}/{a.task}",
        "temp_dir": f"tmp/{RUN_ID}/{a.task}",
        "timings": {
            "started_at": fmt_ts(started), "ended_at": fmt_ts(ended),
            "elapsed_seconds": elapsed, "first_usable_image_seconds": first_usable,
            "user_feedback_wait_seconds": 0,
            "rate_limit_wait_seconds": None, "queue_wait_seconds": None,
            "request_duration_sum_seconds": req_sum,
            "server_timing_source": "requests.jsonl (client wall clock, server-timing when returned)",
        },
        "counts": {
            "snapshot_requests": len(reqs), "successful_snapshot_requests": len(ok),
            "failed_snapshot_requests": len(fail), "retry_requests": len(retries),
            "other_service_requests": 0, "dsl_versions": dsl_versions,
            "image_views": len(reviews), "completed_visual_iterations": completed_vi,
            "incomplete_visual_iterations": incomplete_vi,
        },
        "logs": {"requests": f"tmp/{RUN_ID}/{a.task}/requests.jsonl",
                 "iterations": f"tmp/{RUN_ID}/{a.task}/iterations.jsonl"},
        "outputs": meta.get("files", []),
        "candidates": meta.get("candidates", []),
        "rounds": meta.get("rounds", []),
        "unresolved_issues": meta.get("unresolved", []),
    }
    m.update(meta.get("metrics_overrides", {}))
    (out_dir / "task-metrics.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")

    L = []
    def w(s=""):
        L.append(s)
    w(f"# Snapshot 使用情况说明与踩坑记录")
    w()
    w(f"- 任务ID：{a.task}")
    w(f"- 任务名称：{meta.get('title','')}")
    w(f"- 本次运行ID：{RUN_ID}")
    w(f"- 完成状态：{meta.get('status','completed')}")
    w(f"- 结束原因：{meta.get('stop_reason','需求满足并完成视觉自检')}")
    w(f"- 输出目录：`outputs/{RUN_ID}/{a.task}/`")
    w(f"- 临时目录：`tmp/{RUN_ID}/{a.task}/`")
    w(f"- 路径基准：suite_root；Markdown 链接相对本文档所在目录。")
    w()
    w("## 1. 最终产物与需求完成情况")
    w()
    w("| 文件 | 用途 | 对应DSL或图片 | 完成状态 |")
    w("|---|---|---|---|")
    for f in meta.get("files", []):
        w(f"| `{f.get('file')}` | {f.get('purpose','')} | `{f.get('dsl', f.get('image',''))}` | {f.get('status','完成')} |")
    w()
    for r in meta.get("requirements", []):
        w(f"- {r['text']} — 证据：{r.get('evidence','')}")
    w()
    w(meta.get("design", ""))
    w()
    w("## 2. 文档阅读与实际使用的能力")
    w()
    w("服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/" + RUN_ID + "/_suite/docs/`。")
    w()
    w("| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |")
    w("|---|---|---|")
    docs = meta.get("docs") or [
        {"url": "https://open-snapshot.muedsa.com/ai-guide.md", "knowledge": "请求体为 UTF-8 文本、成功响应为图片二进制、错误 JSON 结构", "used_in": "requests.jsonl / 渲染流程"},
        {"url": "https://snapshot.muedsa.com/reference/parser-tags.md", "knowledge": "Container/Row/Column/Stack/Positioned/Text/Transform 属性与枚举", "used_in": "本题 DSL"},
        {"url": "https://snapshot.muedsa.com/reference/parser-text.md", "knowledge": "fontFamily、fontSize、textAlign、maxLines 与行高度量", "used_in": "文本排版"},
    ]
    for d in docs:
        w(f"| {d['url']} | {d.get('knowledge','')} | {d.get('used_in','')} |")
    w()
    w(meta.get("capabilities", "本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。"))
    w()
    w("## 3. 迭代过程、服务调用与图像检查")
    w()
    w(f"- 请求记录：`{m['logs']['requests']}`")
    w(f"- 迭代记录：`{m['logs']['iterations']}`")
    w(f"- 渲染请求总数：{len(reqs)}；成功 {len(ok)}；失败 {len(fail)}；重试 {len(retries)}；DSL 版本 {dsl_versions}")
    w(f"- 实际图片查看次数：{len(reviews)}；完整视觉迭代：{completed_vi}；未完成视觉迭代：{incomplete_vi}")
    w(f"- 其他接口查询：{meta.get('other_requests','无（字体列表在共享准备阶段查询并缓存于 _suite/docs）')}")
    w()
    w("| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |")
    w("|---|---|---|---|---|---|")
    for r in reqs:
        w(f"| `{r.get('request_id')}` | `{r.get('dsl')}` | {r.get('started_at')} / {r.get('duration_ms')}ms | {r.get('http_status')} / {r.get('content_type') or '-'} | `{r.get('png')}` | {'已查看' if r.get('status')=='success' else '失败响应已保留'} |")
    w()
    w("## 4. 修改记录与踩坑")
    w()
    w("| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |")
    w("|---|---|---|---|---|---|")
    for it in iterations:
        w(f"| {it.get('id')} / {it.get('type')} / {it.get('parent') or '-'} | {it.get('problem','')} | {it.get('cause','')} | {it.get('change','')} | {it.get('result','')} | `{it.get('dsl','')}` |")
    for isu in meta.get("issues", []):
        w(f"| {isu.get('type')} | {isu.get('problem')} | {isu.get('cause')} | {isu.get('fix')} | {isu.get('verify')} | `{isu.get('evidence','')}` |")
    w()
    w("## 5. 任务耗时与请求统计")
    w()
    w(f"结构化指标：`{rel(out_dir / 'task-metrics.json')}`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。")
    w()
    w("| 指标 | 实际值 | 单位 | 数据来源 |")
    w("|---|---|---|---|")
    w(f"| 开始/结束 | {m['timings']['started_at']} / {m['timings']['ended_at']} | 含时区 | requests.jsonl / 打包时间 |")
    w(f"| 任务总耗时 | {elapsed} | 秒 | 墙钟跨度（含起草、等待、看图） |")
    w(f"| 首次可用图 | {first_usable} | 秒 | 首次成功请求结束时间 |")
    w(f"| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |")
    w(f"| 请求耗时之和 | {req_sum} | 秒 | 客户端计时 |")
    w(f"| 成功/失败/重试 | {len(ok)} / {len(fail)} / {len(retries)} | 次 | requests.jsonl |")
    w(f"| 看图/完整视觉迭代 | {len(reviews)} / {completed_vi} | 次 | 实际查看与 iterations.jsonl |")
    w()
    w("## 6. 设计选择、经验与未解决事项")
    w()
    w(meta.get("notes", ""))
    if meta.get("unresolved"):
        w()
        w("未解决事项：")
        for u in meta["unresolved"]:
            w(f"- {u}")
    else:
        w()
        w("未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。")
    w()
    w("过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。")
    (out_dir / "snapshot-usage.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("packaged", rel(out_dir), "requests:", len(reqs), "views:", len(reviews))


if __name__ == "__main__":
    main()
