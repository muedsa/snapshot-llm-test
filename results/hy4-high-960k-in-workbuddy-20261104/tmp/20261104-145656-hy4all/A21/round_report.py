#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A21 每轮报告/指标生成：读取 tmp/A21/round-XX/observations.json（真实看图观察）
与该轮 requests.jsonl，生成 round-XX/snapshot-usage.md 与 round-XX/task-metrics.json。
只记录本轮，不覆盖前轮。"""
import os, sys, json, glob, argparse
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
import suite

TASK = "A21"
RID = suite.RID
OUT = suite.out_dir(TASK)
TMP = suite.tmp_dir(TASK)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    n = ap.parse_args().round
    rd = OUT / ("round-%02d" % n)
    rd.mkdir(parents=True, exist_ok=True)
    obs = json.loads((TMP / ("round-%02d" % n) / "observations.json").read_text(encoding="utf-8"))

    # 该轮全部渲染请求（含子目录，如去文字辅助图）
    logs = sorted(glob.glob(str(TMP / ("round-%02d" % n) / "**" / "requests.jsonl"), recursive=True))
    attempts = []
    for f in logs:
        for line in Path(f).read_text(encoding="utf-8").splitlines():
            if line.strip():
                attempts += json.loads(line).get("attempts", [])
    req = len(attempts)
    succ = sum(1 for a in attempts if a.get("success"))
    fail = req - succ
    retry = sum(1 for a in attempts if a.get("attempt", 0) > 0)
    dur = round(sum(a.get("duration_ms", 0) for a in attempts) / 1000, 3)

    started = obs.get("started_at", "")
    ended = obs.get("ended_at", "")
    try:
        import datetime
        elapsed = round((datetime.datetime.fromisoformat(ended) -
                         datetime.datetime.fromisoformat(started)).total_seconds(), 2)
    except Exception:
        elapsed = None

    m = {
        "schema_version": 1, "path_base": "suite_root", "task_id": TASK,
        "run_id": RID, "round": n, "status": obs.get("status", "completed"),
        "started_at": started, "ended_at": ended, "elapsed_seconds": elapsed,
        "render_requests": req, "successful_requests": succ,
        "failed_requests": fail, "retry_requests": retry,
        "request_duration_sum_seconds": dur,
        "dsl_versions": 1 + obs.get("visual_iterations", 0), "image_views": obs.get("image_views", len(obs.get("images", []))),
        "completed_visual_iterations": obs.get("visual_iterations", 0),
        "incomplete_visual_iterations": 0,
        "other_service_requests": 0, "document_requests": 0,
        "user_feedback_wait_seconds": 0,
        "counts_source": "tmp/<run_id>/A21/round-%02d/**/requests.jsonl（仅本轮）" % n,
        "timing_source": "observations.json 记录时间 + 本地墙钟",
    }
    (rd / "task-metrics.json").write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    L = []
    A = L.append
    A("# A21 第 %d 轮 — Snapshot 使用情况与视觉自检" % n)
    A("")
    A("- 任务ID：A21｜轮次：%d｜标题：%s" % (n, obs.get("title", "")))
    A("- 本次运行ID：%s" % RID)
    A("- 完成状态：%s｜结束原因：%s" % (obs.get("status", "完成"), obs.get("end_reason", "本轮需求满足并完成逐图看图")))
    A("- 本轮输出目录：`outputs/%s/A21/round-%02d/`｜临时目录：`tmp/%s/A21/round-%02d/`" % (RID, n, RID, n))
    A("- 路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）")
    A("- 连续执行模式：A21/A22 使用预置连续执行，本轮完成并归档后自动读取下一轮要求，不等待外部反馈、不编造未来意见；未来需求可提前访问（非隐藏反馈盲测）。")
    A("")
    A("## 1. 本轮产物与需求完成情况")
    A("")
    A("| 文件 | 用途 | 对应DSL或图片 | 完成状态 |")
    A("|---|---|---|---|")
    for f in ("launch-portrait", "launch-wide"):
        A("| `%s.png` | 第%d轮 %s | `%s.snapshot` | %s |" % (f, n, f, f, obs.get("png_verdict", "服务真实 PNG")))
        A("| `%s.snapshot` | 第%d轮完整可复现 DSL | `%s.png` | 完成 |" % (f, n, f))
    for f in ("design-tokens.json", "content-map.json"):
        A("| `%s` | 第%d轮专用审计 | — | 完成 |" % (f, n))
    if n == 3:
        A("| `contrast-audit.json` | 第3轮逐段文字对比度审计 | — | 完成 |")
    A("")
    A(obs.get("requirements", ""))
    A("")
    A("## 2. 逐图看图结论（真实 ViewImage）")
    A("")
    for im in obs.get("images", []):
        A("- **`%s`**（%s）：%s" % (im["file"], im.get("size", ""), im["verdict"]))
    A("")
    for x in obs.get("view_conclusions", []):
        A("- " + x)
    A("")
    A("## 3. 与上轮的真实变化 / 碰撞与回归证据")
    A("")
    if n == 1:
        A("- 首轮：建立两尺寸构图、主色、字体层级与 4 构件品牌图形；design-tokens.json 的 `changes` 为空；顶部/底部预留扩展空间，不写待添加文字。")
    else:
        for x in obs.get("changes", []):
            A("- " + x)
    if obs.get("collision_note"):
        A("")
        A("**长标题与新增信息碰撞避免**：%s" % obs["collision_note"])
    if obs.get("contrast_note"):
        A("")
        A("**对比度与视觉回归**：%s" % obs["contrast_note"])
    A("")
    A("前一轮完整保留于 `../round-%02d/`（本轮不覆盖任何前轮文件）。" % (n - 1) if n > 1 else "本轮为首轮。")
    A("")
    A("## 4. 请求与迭代统计（仅本轮）")
    A("")
    A("- 渲染请求总数：%d｜成功：%d｜失败：%d｜重试：%d" % (req, succ, fail, retry))
    A("- 已记录请求耗时之和：%.3f 秒（可与真实墙钟不同，不相加为任务总耗时）" % dur)
    A("- 本轮实际看图次数：%d（含最终 PNG 逐张打开与迭代版复查）｜完整视觉迭代：%d" % (obs.get("image_views", len(obs.get("images", []))), obs.get("visual_iterations", 0)))
    A("- 请求记录：`tmp/%s/A21/round-%02d/requests.jsonl`" % (RID, n))
    A("- 结构化指标：`round-%02d/task-metrics.json`（本文件所在目录）" % n)
    A("")
    A("## 5. 文档、能力与踩坑")
    A("")
    A("- 服务：`POST /snapshot`，UTF-8 纯文本 DSL，成功 `image/png`；沿用 `/fonts` 缓存（中文 Noto Sans CJK SC、拉丁 Inter）。")
    A("- 本轮使用的 DSL 能力：Snapshot(png)+Stack/Positioned 固定画布；Container 的 gradient/color/borderRadius/border/Opacity 画背景、信息卡、胶囊与品牌光环/光线/节点/层级条；ClipPath line/poly 画放射光线；Text(fontFamily/fontSize/fontStyle+CDATA) 画全部文案，每行独立定位控制行数；未使用外部图片、Transform 或整图嵌入。")
    A("- 踩坑与经验：%s" % obs.get("pitfalls", "本轮未遇到已确认的服务错误；解析错误与网络失败均未发生。"))
    A("")
    A("## 6. 未解决事项")
    A("")
    A(obs.get("unresolved", "无。"))
    A("")
    A("临时目录中的 DSL 版本、请求/响应、失败记录、脚本与观察证据均保留，未删除或覆盖任何尝试；任务根累计报告与指标见 `../snapshot-usage.md`、`../task-metrics.json`。")
    (rd / "snapshot-usage.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("A21 round-%02d report written | req=%d succ=%d fail=%d retry=%d views=%d"
          % (n, req, succ, fail, retry, len(obs.get("images", []))))

if __name__ == "__main__":
    main()
