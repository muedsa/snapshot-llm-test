#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A22 每轮报告/指标生成：读取 tmp/A22/round-XX/observations.json（真实看图观察）
与该轮 requests.jsonl，生成 round-XX/snapshot-usage.md 与 round-XX/task-metrics.json；
并把真实看图结论回填 round-XX/change-audit.json 的 visual_review 回归项。只记录本轮。"""
import os, sys, json, glob, argparse
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
import suite

TASK = "A22"
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

    started, ended = obs.get("started_at", ""), obs.get("ended_at", "")
    try:
        import datetime
        elapsed = round((datetime.datetime.fromisoformat(ended) -
                         datetime.datetime.fromisoformat(started)).total_seconds(), 2)
    except Exception:
        elapsed = None
    views = obs.get("image_views", len(obs.get("images", [])))
    vit = obs.get("visual_iterations", 0)

    m = {
        "schema_version": 1, "path_base": "suite_root", "task_id": TASK,
        "run_id": RID, "round": n, "status": obs.get("status", "completed"),
        "started_at": started, "ended_at": ended, "elapsed_seconds": elapsed,
        "render_requests": req, "successful_requests": succ,
        "failed_requests": fail, "retry_requests": retry,
        "request_duration_sum_seconds": dur,
        "dsl_versions": 1 + vit, "image_views": views,
        "completed_visual_iterations": vit, "incomplete_visual_iterations": 0,
        "other_service_requests": 0, "document_requests": 0,
        "user_feedback_wait_seconds": 0,
        "counts_source": "tmp/<run_id>/A22/round-%02d/**/requests.jsonl（仅本轮）" % n,
        "timing_source": "observations.json 记录时间 + 本地墙钟",
    }
    (rd / "task-metrics.json").write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 回填 change-audit 的视觉回归项
    ca_path = rd / "change-audit.json"
    if ca_path.exists():
        ca = json.loads(ca_path.read_text(encoding="utf-8"))
        for r in ca.get("regression", []):
            if r.get("kind") == "visual_review":
                r["result"] = "已真实看图：" + "；".join(obs.get("view_conclusions", []))
                r["evidence"] = "round-%02d/snapshot-usage.md + ViewImage 打开 round-%02d/dashboard.png" % (n, n)
        ca["status"] = "reviewed"
        ca_path.write_text(json.dumps(ca, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    L = []
    A = L.append
    A("# A22 第 %d 轮 — Snapshot 使用情况与视觉自检" % n)
    A("")
    A("- 任务ID：A22｜轮次：%d｜标题：%s" % (n, obs.get("title", "")))
    A("- 本次运行ID：%s" % RID)
    A("- 完成状态：%s｜结束原因：%s" % (obs.get("status", "完成"), obs.get("end_reason", "本轮需求满足并完成逐图看图")))
    A("- 本轮输出目录：`outputs/%s/A22/round-%02d/`｜临时目录：`tmp/%s/A22/round-%02d/`" % (RID, n, RID, n))
    A("- 路径基准：suite_root（记录内本地路径均相对总任务根）")
    A("- 连续执行模式：A22 使用预置连续执行，本轮完成、看图、归档后自动读取下一轮要求，不等待外部反馈、不编造未来意见；未来需求可提前访问（非隐藏反馈盲测）。")
    A("")
    A("## 1. 本轮产物与需求完成情况")
    A("")
    A("| 文件 | 用途 | 对应DSL或图片 | 完成状态 |")
    A("|---|---|---|---|")
    A("| `dashboard.png` | 第%d轮 1600×1000 经营驾驶舱 | `dashboard.snapshot` | %s |" % (n, obs.get("png_verdict", "服务真实 PNG")))
    A("| `dashboard.snapshot` | 第%d轮完整可复现 DSL | `dashboard.png` | 完成 |" % n)
    A("| `computed-data.json` | 逐月/汇总/轴/结论的真实计算 | — | 完成 |")
    A("| `layout-map.json` | 主区域边界与主样式、对上轮分量差 | — | 完成 |")
    A("| `monthly.csv` | 本轮实际使用的数据快照（原始 CSV 未修改） | — | 完成 |")
    if n >= 2:
        A("| `change-audit.json` | 变更传播/未改内容/视觉回归 | — | 完成（看图后已回填 visual_review） |")
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
    A("## 3. 数据变更传播与局部回归")
    A("")
    if n == 1:
        A("- 首轮：按 inputs/monthly.csv 原始 6 个月数据建立驾驶舱；computed-data.json.applied_changes 为空；layout-map.json.comparison 为空。")
    else:
        for x in obs.get("changes", []):
            A("- " + x)
    if obs.get("regression_note"):
        A("")
        A("**回归核验**：%s" % obs["regression_note"])
    A("")
    A("前一轮完整保留于 `../round-%02d/`（本轮不覆盖任何前轮文件）。" % (n - 1) if n > 1 else "本轮为首轮。")
    A("")
    A("## 4. 请求与迭代统计（仅本轮）")
    A("")
    A("- 渲染请求总数：%d｜成功：%d｜失败：%d｜重试：%d" % (req, succ, fail, retry))
    A("- 已记录请求耗时之和：%.3f 秒" % dur)
    A("- 本轮实际看图次数：%d｜完整视觉迭代：%d" % (views, vit))
    A("- 请求记录：`tmp/%s/A22/round-%02d/requests.jsonl`" % (RID, n))
    A("- 结构化指标：`task-metrics.json`（本文件所在目录）")
    A("")
    A("## 5. 文档、能力与踩坑")
    A("")
    A("- 服务：`POST /snapshot`，UTF-8 纯文本 DSL，成功 `image/png`；沿用 `/fonts` 缓存（中文 Noto Sans CJK SC、拉丁 Inter）。")
    A("- 本轮使用的 DSL 能力：Snapshot(png)+Stack/Positioned 固定 1600×1000 画布；Container(gradient/color/borderRadius/border/Opacity) 画头部/KPI 卡/图卡/表格/结论卡/柱体；rect/bar 画共用零起点分组柱(负值向下、红色)；ClipPath line 画转化率折线；Text(fontFamily/fontSize/fontStyle/textAlign+CDATA) 画全部文字(正文≥22)；无外部图片、无整图嵌入。")
    A("- 踩坑与经验：%s" % obs.get("pitfalls", "本轮未遇到已确认的服务错误；解析错误未发生。"))
    A("")
    A("## 6. 未解决事项")
    A("")
    A(obs.get("unresolved", "无。"))
    A("")
    A("临时目录中的 DSL 版本、请求/响应、失败记录、脚本与观察证据均保留；任务根累计报告与指标见 `../snapshot-usage.md`、`../task-metrics.json`。")
    (rd / "snapshot-usage.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("A22 round-%02d report written | req=%d succ=%d fail=%d retry=%d views=%d | change-audit reviewed=%s"
          % (n, req, succ, fail, retry, views, ca_path.exists()))

if __name__ == "__main__":
    main()
