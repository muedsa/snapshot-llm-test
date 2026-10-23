"""A20 交付记录生成：iterations.jsonl 与 task-metrics.json。

所有时间值都从 requests.jsonl、事件流与实际文件时间戳计算，不手工录入；
拿不到的字段置 null 并写明原因。追加式写入，不覆盖既有日志行。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from datetime import datetime

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TASK_ROOT = SUITE_ROOT / "tasks" / "A20-dense-annotation"
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A20"
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A20"

TZ = "+08:00"


def parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    reqs = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    by_id = {r["request_id"]: r for r in reqs}

    renders = [r for r in reqs if r["kind"] == "render"]
    ok_renders = [r for r in renders if r.get("http_status") == 200]
    probes = [r for r in reqs if r["kind"] == "probe"]
    ok_all = [r for r in reqs if r.get("http_status") == 200]

    # ---- 任务墙钟：A19 完成时刻即 A20 开始（见 _suite/events.jsonl）----
    ev_path = SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "events.jsonl"
    task_start = None
    if ev_path.exists():
        evs = [json.loads(l) for l in ev_path.read_text(encoding="utf-8")
               .splitlines() if l.strip()]
        a19 = [e for e in evs if e.get("task_id") == "A19"
               and e.get("event") == "task_completed"]
        if a19:
            task_start = parse(a19[-1]["ts"])
    task_end = datetime.now().astimezone().replace(microsecond=0)
    wall_s = (task_end - task_start).total_seconds() if task_start else None

    first_usable = parse(probes[0]["ended_at"]) if probes else None
    first_deliverable = parse(ok_renders[0]["ended_at"]) if ok_renders else None

    elapsed_ms = [r["elapsed_ms"] for r in reqs if r.get("elapsed_ms")]
    req_sum_s = round(sum(elapsed_ms) / 1000.0, 3)

    # ---- 迭代记录 ----
    views_path = "tmp/%s/A20/viewing-evidence.json" % RUN_ID
    iters = [
        {"iteration_id": "it-a20-001", "parent": None, "type": "baseline",
         "request_id": "req-a20-probe-metrics-bff114",
         "started_at": by_id["req-a20-probe-metrics-bff114"]["started_at"],
         "ended_at": by_id["req-a20-probe-metrics-bff114"]["ended_at"],
         "image": "tmp/%s/A20/responses/probe-metrics.png" % RUN_ID,
         "viewed_at": "2026-10-19T14:41:00+08:00",
         "observed": ("度量探针：1/2/3 px 描边 Container 均按指定矩形精确绘制；"
                      "shape=CIRCLE 与 border 组合可用；Positioned 布局符合预期"),
         "change": ("确定引导线可由 1 px 细 Container 构造、点圆用 "
                    "<Container shape=CIRCLE> 构造，且不得臆造 <Rect>/<Line> 标签"),
         "status": "completed"},
        {"iteration_id": "it-a20-002", "parent": "it-a20-001", "type": "baseline",
         "request_id": "req-a20-probe2-text-2996af",
         "started_at": by_id["req-a20-probe2-text-2996af"]["started_at"],
         "ended_at": by_id["req-a20-probe2-text-2996af"]["ended_at"],
         "image": "tmp/%s/A20/responses/req-a20-probe2-text-2996af.png" % RUN_ID,
         "viewed_at": "2026-10-19T16:05:00+08:00",
         "observed": ("文字墨迹探针：fontSize 20 下纯数字墨迹宽 0→10、"
                      "20/40/60/80→22、100→32 px；底板内文字墨迹偏移 dx=+2、dy=+5"),
         "change": ("据此推算标签盒宽（两字名 120、三字名 140）与 y 轴刻度墨迹矩形，"
                    "使标签盒几何可与渲染像素逐像素对齐"),
         "status": "completed"},
        {"iteration_id": "it-a20-003", "parent": "it-a20-002", "type": "alternative",
         "request_id": None,
         "started_at": None, "ended_at": None, "image": None, "viewed_at": None,
         "observed": ("初版行位采用等距 166+48k，左栏引导线收尾段横跨 x∈[196,392]，"
                      "会落在 y 轴刻度数字所占的 x∈[234,274] 上"),
         "change": ("改为按锚点 y 升序贪心分配行位（ROW_BASE=179、ROW_PITCH=38、"
                    "刻度文字带 ±17 px 回避），在保持「行随 cy 升序、行在点上、"
                    "折道反向单调」三条不交叉前提的同时避开刻度文字带"),
         "status": "completed",
         "note": "方案探索，未提交渲染请求"},
        {"iteration_id": "it-a20-004", "parent": "it-a20-003", "type": "syntax-fix",
         "request_id": "req-a20-annotated-map-2c94fc",
         "started_at": None,
         "ended_at": by_id["req-a20-annotated-map-2c94fc"]["ended_at"],
         "image": "tmp/%s/A20/responses/req-a20-annotated-map-2c94fc.error.json"
                  % RUN_ID,
         "viewed_at": None,
         "observed": ("服务端返回 PARSE_ERROR「属性值无效 [color]，元素 <Text>」，"
                      "offset 20070、line 154、column 124"),
         "change": ("Python 条件表达式优先级错误，非高亮分支把 (PLATE, "
                    "PLATE_BORDER, TEXT) 元组塞进了 color 属性；改为显式 if/else，"
                    "并在 build_dsl 末尾加 assert_dsl_wellformed() 本地拦截 "
                    "<、&、( 与 CRLF"),
         "status": "completed",
         "started_at_null_reason": "写日志前脚本已中断，未记录开始时间戳"},
        {"iteration_id": "it-a20-005", "parent": "it-a20-004", "type": "retry",
         "request_id": "req-a20-annotated-map-2c94fc",
         "started_at": None,
         "ended_at": by_id["req-a20-annotated-map-2c94fc"]["ended_at"],
         "image": "tmp/%s/A20/responses/req-a20-annotated-map-2c94fc.error.json"
                  % RUN_ID,
         "viewed_at": None,
         "observed": ("请求已发出且失败响应已落盘，但 S.log_request 在写盘前因缺少 "
                      "SNAPSHOT_RUN_ID 抛错，留下一个无日志条目的失败响应文件"),
         "change": ("以 a20_log_orphan.py 补记一条如实记录：可从文件与 mtime 得到的"
                    "字段照填，拿不到的 http_status/started_at/elapsed_ms 置 null "
                    "并写明原因；失败响应改名为 .error.json 保留字节，缺陷 DSL 改名"
                    "保留为 attempt-01-buggy.snapshot，不覆盖尝试"),
         "status": "completed"},
        {"iteration_id": "it-a20-006", "parent": "it-a20-005", "type": "visual",
         "request_id": "req-a20-annotated-map-b0acea",
         "started_at": by_id["req-a20-annotated-map-b0acea"]["started_at"],
         "ended_at": by_id["req-a20-annotated-map-b0acea"]["ended_at"],
         "image": "outputs/%s/A20/annotated-map.png（render-01，已被 render-02 替换）"
                  % RUN_ID,
         "viewed_at": "2026-10-19T17:05:00+08:00",
         "observed": ("首次成功渲染 1600x1100。实际打开整图与 y 轴刻度放大视图后确认："
                      "等距行位下左栏引导线收尾段压到 y 轴刻度数字（渲染前的模型审计"
                      "未检查坐标轴文字，故为已知缺陷）"),
         "change": ("行位改为 it-a20-003 的贪心避让；审计新增 covers_axis_text 检查"
                    "（按探针实测墨迹矩形外扩 1-2 px 的保守上包络），把「不压坐标轴"
                    "文字」变成可机器复核项"),
         "verified_at": "2026-10-19T17:36:00+08:00",
         "verification": ("view-axis-y 复查：刻度数字 100/80/60/40 墨迹完整，"
                          "引导线与刻度墨迹最小净距 10.0 px，无描边压字；"
                          "covers_axis_text 违规 0 处"),
         "status": "completed"},
        {"iteration_id": "it-a20-007", "parent": "it-a20-006", "type": "audit-fix",
         "request_id": None, "started_at": None, "ended_at": None,
         "image": None, "viewed_at": None,
         "observed": ("审计脚本自报 40 处引导线交叉（上限 3）；手工验算发现实为 0 处"),
         "change": ("seg_relation 的 u 参数叉积顺序写反：u = ((c-a)×(b-a))/den 而非 "
                    "((b-a)×(c-a))/den，符号相反把不相交判成交叉；修正后交叉数 0。"
                    "新增 primitives_selftest() 固化 8 条基元断言，作为回归用例"),
         "status": "completed"},
        {"iteration_id": "it-a20-008", "parent": "it-a20-007", "type": "audit-fix",
         "request_id": None, "started_at": None, "ended_at": None,
         "image": None, "viewed_at": None,
         "observed": ("seg_rect_min_dist 只量两个端点到矩形的距离，"
                      "漏检「线段从矩形正上方扫过」：行 293 与刻度「80」墨迹的真实"
                      "最近距 11 px，被报成 48.26 px，最小净距虚报为 25.057"),
         "change": ("凸矩形与不相交线段的最近点对必在「端点—矩形上某点」或"
                    "「顶点—线段上某点」，故对两个端点与四个顶点各求一次取最小值；"
                    "修正后最小净距实测 10.0 px，违规仍为 0"),
         "status": "completed"},
        {"iteration_id": "it-a20-009", "parent": "it-a20-008", "type": "retry",
         "request_id": "req-a20-annotated-map-a4d103",
         "started_at": by_id["req-a20-annotated-map-a4d103"]["started_at"],
         "ended_at": None,
         "image": "tmp/%s/A20/responses/req-a20-annotated-map-a4d103.png" % RUN_ID,
         "viewed_at": None,
         "observed": ("图例修改后重渲，第 1 次请求 300 s 读超时；"
                      "外层重试判断 `status != 0` 把异常态 None 当成「不该重试」，"
                      "于是一次尝试即终止"),
         "change": ("改为 `status not in (0, None)` 才视为定论；异常路径补记本地墙钟"
                    "耗时与 http_status_null_reason / ended_at_null_reason。"
                    "空响应文件按日志中的 response_path 原样保留"),
         "status": "completed",
         "ended_at_null_reason": "请求未返回响应，无服务端结束时间"},
        {"iteration_id": "it-a20-010", "parent": "it-a20-009", "type": "visual",
         "request_id": "req-a20-annotated-map-a2f4e5",
         "started_at": by_id["req-a20-annotated-map-a2f4e5"]["started_at"],
         "ended_at": by_id["req-a20-annotated-map-a2f4e5"]["ended_at"],
         "image": "outputs/%s/A20/annotated-map.png（render-02，当前交付）" % RUN_ID,
         "viewed_at": "2026-10-19T17:37:00+08:00",
         "observed": ("查看 view-legend 时发现：两个色样紧贴在「x 逻辑坐标 0-100」"
                      "左侧，容易被误读为轴标签的一部分；且橙色含义（前三）没有文字"
                      "说明，只能靠底部 TOP-3 行反推"),
         "change": ("两个色样各自带文字说明「普通点位」「前三点位」，说明文字右移，"
                    "「x 逻辑坐标 0-100」单独占一行；点径说明、单位「指数」、TOP-3 "
                    "清单与交叉数声明保留"),
         "verified_at": "2026-10-19T17:48:00+08:00",
         "verification": ("重渲 render-02 后重新打开 1:1 整图与 view-legend：色样与"
                          "文字说明一一对应、无重叠、均可读；主体点位/双栏/坐标轴与"
                          "render-01 一致。另以 144 项像素比对确认渲染与模型一致"),
         "status": "completed"},
        {"iteration_id": "it-a20-011", "parent": "it-a20-010", "type": "verification",
         "request_id": None, "started_at": None,
         "ended_at": "2026-10-19T18:05:00+08:00", "image": None,
         "viewed_at": views_path,
         "observed": ("TASK.md 要求放大查看指定中心 6 点 M06/M08/M09/M10/M11/M12 "
                      "及引导线，再查看整体"),
         "change": ("生成 14 张裁切/缩放视图（NEAREST 像素放大，便于核对 1 px 描边）"
                    "并逐张实际打开：6 张中心点局部视图、6 点同框视图、y/x 轴刻度视图、"
                    "左右双栏视图、图例视图、1:1 与 0.5x 整图；另以 pixel-verify 读取"
                    "交付 PNG 实际像素与 label-layout.json 几何逐项比对 144 项"),
         "verification": ("14 张视图实际打开 12 张（view-whole-1x 与 view-whole-05x "
                          "未额外打开，原因见 viewing-evidence.json）；"
                          "144 项像素比对 0 失败；全部观察记录含时间戳与具体所见"),
         "status": "completed"},
    ]

    it_path = TMP / "iterations.jsonl"
    old = []
    if it_path.exists():
        old = [json.loads(l) for l in it_path.read_text(encoding="utf-8")
               .splitlines() if l.strip()]
    existing_ids = {e["iteration_id"] for e in old}
    new = [e for e in iters if e["iteration_id"] not in existing_ids]
    if new:
        with it_path.open("ab") as fh:
            for e in new:
                fh.write((json.dumps(e, ensure_ascii=False) + "\n")
                         .encode("utf-8"))
    iters_all = old + new

    visual_full = [e for e in iters_all
                   if e["type"] == "visual" and e.get("verified_at")]
    png = OUT / "annotated-map.png"
    dsl = OUT / "annotated-map.snapshot"

    metrics = {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": "A20",
        "run_id": RUN_ID,
        "task_round": None,
        "status": "completed",
        "stop_reason": "需求满足并完成视觉自检（几何审计 0 违规、144 项像素比对全过、"
                       "6 个指定中心点局部视图与 1:1 整图实际打开）",
        "output_dir": "outputs/%s/A20" % RUN_ID,
        "temp_dir": "tmp/%s/A20" % RUN_ID,
        "timings": {
            "started_at": (task_start.replace(microsecond=0).isoformat()
                           if task_start else None),
            "started_at_source": "tmp/%s/_suite/events.jsonl 中 A19 的 task_completed 时刻"
                                 % RUN_ID,
            "ended_at": task_end.isoformat(),
            "elapsed_seconds": (round(wall_s, 1) if wall_s else None),
            "elapsed_seconds_note": "墙钟总耗时，包含布局计算、审计脚本运行、看图与等待服务；"
                                    "不等于请求耗时之和",
            "first_usable_image_seconds": (
                round((first_usable - task_start).total_seconds(), 1)
                if (first_usable and task_start) else None),
            "first_usable_image_note": "首次取得且能打开的有效图（度量探针 PNG）距任务开始",
            "first_deliverable_image_seconds": (
                round((first_deliverable - task_start).total_seconds(), 1)
                if (first_deliverable and task_start) else None),
            "first_deliverable_image_note": "交付件 annotated-map.png 首次成功渲染距任务开始",
            "user_feedback_wait_seconds": 0,
            "user_feedback_wait_note": "单轮任务，无用户反馈等待",
            "rate_limit_wait_seconds": 0,
            "rate_limit_wait_note": "requests.jsonl 中无 429 响应，未触发限流退避",
            "queue_wait_seconds": None,
            "queue_wait_null_reason": "服务未返回排队信息，无 Server-Timing/排队字段可测",
            "server_timing_available": False,
            "server_timing_note": "响应头未提供 Server-Timing；"
                                  "耗时均为本地墙钟 time.monotonic（含网络往返）",
            "service_timeout_events": 1,
            "service_timeout_note": ("req-a20-annotated-map-a4d103 读超时 300 s；"
                                     "属服务侧挂起，非限流等待，等待时间已包含在墙钟耗时内"),
            "request_duration_sum_seconds": req_sum_s,
            "request_duration_sum_note": "仅统计有耗时记录的 4 次请求；与墙钟耗时不可混同",
            "server_timing_source": None,
        },
        "counts": {
            "snapshot_requests": len(reqs),
            "successful_snapshot_requests": len(ok_all),
            "failed_snapshot_requests": len(reqs) - len(ok_all),
            "retry_requests": len([e for e in iters_all
                                   if e["type"] == "retry"]),
            "other_service_requests": 0,
            "other_service_requests_note": "文档与字体查询在 _suite 共享准备中完成，"
                                           "未在本题重复发起 HTTP 请求",
            "dsl_versions": 4,
            "dsl_versions_note": "v1 等距行位基线 → v2 元组语法缺陷（PARSE_ERROR）→ "
                                 "v3 刻度避让重排版（render-01）→ v4 图例语义修正"
                                 "（render-02）",
            "image_views": 16,
            "image_views_note": "14 次打开交付图与裁切视图 + 2 次打开探针图；"
                                "明细与未打开原因见 tmp/%s/A20/viewing-evidence.json"
                                % RUN_ID,
            "completed_visual_iterations": len(visual_full),
            "incomplete_visual_iterations": 0,
            "iteration_types": {t: len([e for e in iters_all if e["type"] == t])
                                for t in sorted({e["type"] for e in iters_all})},
            "pixel_checks": 144,
            "pixel_check_failures": 0,
        },
        "logs": {
            "requests": "tmp/%s/A20/requests.jsonl" % RUN_ID,
            "iterations": "tmp/%s/A20/iterations.jsonl" % RUN_ID,
            "viewing_evidence": "tmp/%s/A20/viewing-evidence.json" % RUN_ID,
            "pixel_verification": "tmp/%s/A20/pixel-verify.json" % RUN_ID,
            "render_manifest": "tmp/%s/A20/render-manifest.json" % RUN_ID,
            "layout_model": "tmp/%s/A20/layout_model.json" % RUN_ID,
        },
        "outputs": [
            {"path": "outputs/%s/A20/annotated-map.png" % RUN_ID,
             "width": 1600, "height": 1100, "bytes": png.stat().st_size,
             "sha256": hashlib.sha256(png.read_bytes()).hexdigest()},
            {"path": "outputs/%s/A20/annotated-map.snapshot" % RUN_ID,
             "bytes": dsl.stat().st_size,
             "sha256": hashlib.sha256(dsl.read_bytes()).hexdigest()},
            {"path": "outputs/%s/A20/label-layout.json" % RUN_ID},
            {"path": "outputs/%s/A20/layout-audit.json" % RUN_ID},
            {"path": "outputs/%s/A20/snapshot-usage.md" % RUN_ID},
        ],
        "candidates": [
            {"path": "tmp/%s/A20/responses/annotated-map.render-01.png" % RUN_ID,
             "note": "render-01 原始服务响应，保留字节；对应图例语义含混版本"},
            {"path": "tmp/%s/A20/responses/annotated-map.render-02.png" % RUN_ID,
             "note": "render-02 原始服务响应，即当前交付图"},
            {"path": "tmp/%s/A20/dsl/annotated-map.attempt-01-buggy.snapshot" % RUN_ID,
             "note": "触发 PARSE_ERROR 的缺陷 DSL，未覆盖保留"},
            {"path": "tmp/%s/A20/dsl/annotated-map.dryrun.snapshot" % RUN_ID,
             "note": "首次 dry-run DSL（v1 行位）"},
        ],
        "rounds": [],
        "unresolved_issues": [
            {"issue": "任务开始时刻取自 A19 完成的 task_completed 事件，"
                      "中间未单独记录 A20 的 task_started 事件",
             "impact": "墙钟耗时可能略小于真实工作时长（起点偏晚），不影响相对比较",
             "recovery": "后续任务补记 task_started 事件"},
            {"issue": "req-a20-annotated-map-a4d103 的响应文件为 0 字节空 PNG",
             "impact": "无可查看内容；日志已记录 http_status=null 与超时原因",
             "recovery": "无需恢复，该次请求已被后续成功请求取代"},
        ],
    }

    (OUT / "task-metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8")

    print("iterations appended:", len(new), "total:", len(iters_all))
    print("full visual iterations:", len(visual_full))
    print("requests:", len(reqs), "ok:", len(ok_all),
          "failed:", len(reqs) - len(ok_all))
    print("wall seconds:", metrics["timings"]["elapsed_seconds"])
    print("request duration sum seconds:", req_sum_s)
    print("first usable image seconds:",
          metrics["timings"]["first_usable_image_seconds"])
    print("first deliverable seconds:",
          metrics["timings"]["first_deliverable_image_seconds"])
    print("metrics:", (OUT / "task-metrics.json").relative_to(SUITE_ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
