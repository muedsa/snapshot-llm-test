# -*- coding: utf-8 -*-
"""A20 收尾：requests/iterations/task-metrics/complete-payload/snapshot-usage + suite 事件与指针。"""
import io, sys, json, os, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

RUN = "20261016T164020-m1"
D = f"outputs/{RUN}/A20"; TD = f"tmp/{RUN}/A20"; SD = f"tmp/{RUN}/_suite"
SS = f"outputs/{RUN}/_suite"
STARTED = "2026-10-17T18:48:34+08:00"
ended = datetime.datetime.now().astimezone()
ended_s = ended.isoformat(timespec="seconds")
el = round((ended - datetime.datetime.fromisoformat(STARTED)).total_seconds(), 1)
def mt(p):
    return datetime.datetime.fromtimestamp(os.path.getmtime(p)).astimezone().isoformat(timespec="milliseconds")

# ── requests.jsonl ──
reqs = [
    {"id": "A20-render-0001", "task_id": "A20", "path_base": "suite_root", "request_type": "render",
     "url": "https://open-snapshot.muedsa.com/snapshot", "service_base": "https://open-snapshot.muedsa.com",
     "started_at": mt(f"{TD}/renders/a20-map-193307791.req.snapshot"),
     "ended_at": mt(f"{TD}/renders/a20-map-193307791.resp"),
     "duration_ms": 1070.0, "http_status": 400, "content_type": "application/json",
     "request_file": f"{TD}/renders/a20-map-193307791.req.snapshot",
     "response_file": f"{TD}/renders/a20-map-193307791.resp",
     "request_id": "deaaae17-63e5-49e7-ad95-9ab1c5b3ad30", "server_timing": None,
     "retry_after": None,
     "error_summary": "PARSE_ERROR: First tag must be 'Snapshot', got 'Canvas' — DSL 根标签误写 Canvas/Scene, 改为 Snapshot/Stack 后重试成功"},
    {"id": "A20-render-0002", "task_id": "A20", "path_base": "suite_root", "request_type": "render",
     "url": "https://open-snapshot.muedsa.com/snapshot", "service_base": "https://open-snapshot.muedsa.com",
     "started_at": mt(f"{TD}/renders/a20-map-193347702.req.snapshot"),
     "ended_at": mt(f"{TD}/renders/a20-map-193347702.resp"),
     "duration_ms": 1324.0, "http_status": 200, "content_type": "image/png",
     "request_file": f"{TD}/renders/a20-map-193347702.req.snapshot",
     "response_file": f"{TD}/renders/a20-map-193347702.resp",
     "request_id": "8da4d605-689b-482a-b483-caf6aa00c6f5",
     "server_timing": "render;dur=1317.1, total;dur=1324.0",
     "retry_after": None, "error_summary": None},
    {"id": "A20-render-0003", "task_id": "A20", "path_base": "suite_root", "request_type": "render",
     "url": "https://open-snapshot.muedsa.com/snapshot", "service_base": "https://open-snapshot.muedsa.com",
     "started_at": mt(f"{TD}/renders/a20-map-193939114.req.snapshot"),
     "ended_at": mt(f"{TD}/renders/a20-map-193939114.resp"),
     "duration_ms": 451.0, "http_status": 200, "content_type": "image/png",
     "request_file": f"{TD}/renders/a20-map-193939114.req.snapshot",
     "response_file": f"{TD}/renders/a20-map-193939114.resp",
     "request_id": "c07bc8e6-acd8-498f-8177-bff5c1e1e2b6",
     "server_timing": "render;dur=440.7, total;dur=451.0",
     "retry_after": None, "error_summary": None},
]
with open(f"{TD}/requests.jsonl", "w", encoding="utf-8") as f:
    for r in reqs:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

# ── iterations.jsonl ──
It = [
    {"id": "A20-map-v01", "type": "baseline", "image": "steps/a20-half.png",
     "viewed_at": "2026-10-17T19:39:44+08:00",
     "images": ["steps/a20-half.png", "steps/a20-zoom-pocket.png", "steps/a20-zoom-margin.png",
                "steps/a20-zoom-m15line.png", "steps/a20-zoom-m09line.png", "steps/a20-zoom-bottom.png"],
     "observable_issues": ["M08 单行金框标签文本溢出底板右缘(TOP2 的 P2 越出边框, est 少算“值”字与加粗字宽)"],
     "changes": ["重算 est: 前导加粗拉丁 12.9→13.6、普通拉丁 11.8→12.1；单行文本按完整渲染串(含“值”)估宽 → M08 盒宽 253→283、M04 182→211"],
     "seq": 1},
    {"id": "A20-map-v02", "type": "baseline", "image": "steps/a20-half.png",
     "viewed_at": "2026-10-17T19:41:10+08:00",
     "images": ["steps/a20-half.png", "steps/a20-zoom-pocket.png", "steps/a20-zoom-margin.png",
                "steps/a20-zoom-m15line.png", "steps/a20-zoom-m09line.png", "steps/a20-zoom-bottom.png"],
     "observable_issues": [],
     "changes": ["复检通过: 24 标签文本全部在底板内; M08/M10/M23 金框与 TOP1–3 完整; 中心六点与引导线放大核对; 右栏槽位与导轨正常"],
     "seq": 2},
]
with open(f"{TD}/iterations.jsonl", "w", encoding="utf-8") as f:
    for r in It:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

# ── task-times.json ──
json.dump({"started_at": STARTED, "ended_at": ended_s},
          open(f"{TD}/task-times.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ── task-metrics.json ──
metrics = {
    "schema_version": 1, "path_base": "suite_root", "task_id": "A20", "run_id": RUN,
    "task_round": None, "status": "completed", "stop_reason": None,
    "output_dir": f"outputs/{RUN}/A20/", "temp_dir": f"tmp/{RUN}/A20/",
    "timings": {
        "started_at": STARTED, "ended_at": ended_s, "elapsed_seconds": el,
        "first_usable_image_seconds": None, "user_feedback_wait_seconds": None,
        "rate_limit_wait_seconds": None, "queue_wait_seconds": None,
        "request_duration_sum_seconds": 1.775,
        "server_timing_source": "X-Server-Timing captured per request in requests.jsonl (200 状态请求标头值)"},
    "counts": {
        "snapshot_requests": 3, "successful_snapshot_requests": 2, "failed_snapshot_requests": 1,
        "retry_requests": 0, "other_service_requests": 0, "dsl_versions": 0,
        "image_views": 2, "completed_visual_iterations": 2, "incomplete_visual_iterations": 0,
        "layout_solver_runs": 7, "layout_solver_passing_configs": 3,
        "final_images": 1, "labels_placed": 24, "leader_lines": 3,
        "line_crossings_total": 1, "line_crossing_limit": 3},
    "logs": {"requests": f"tmp/{RUN}/A20/requests.jsonl", "iterations": f"tmp/{RUN}/A20/iterations.jsonl"},
    "outputs": [
        {"name": "annotated-map.png", "path_base": "output_dir", "path": "annotated-map.png"},
        {"name": "annotated-map.snapshot", "path_base": "output_dir", "path": "annotated-map.snapshot"},
        {"name": "label-layout.json", "path_base": "output_dir", "path": "label-layout.json"},
        {"name": "layout-audit.json", "path_base": "output_dir", "path": "layout-audit.json"}],
    "candidates": [], "rounds": [], "unresolved_issues": [],
}
json.dump(metrics, open(f"{D}/task-metrics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(metrics, open(f"{TD}/task-metrics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("requests/iterations/times/metrics written; elapsed:", el)

usage = """# A20 · snapshot-usage

## 状态
completed。指定最终图 1 张：`annotated-map.png`(1600×1100, 服务 200 真实响应) +
同名完整 `.snapshot`。程序化生成双审计：`label-layout.json`（24 标签的逻辑坐标/未舍入
像素锚点/标签盒/折线/字号/避让规则）与 `layout-audit.json`(全对通过)。

## 数据与几何契约
- markers.json 24 点 (x/y∈0–100, value, name)；像素锚点 = (280+10.4x, 920−7.6y)，
  逻辑原点左下、y 向上，先翻转再映射，未取整（label-layout 保留原始浮点）。
- 点径统一 12px（#1D4ED8）；24 点两两最小点心距 >12px，mathematically 无点-点重叠，
  未启用缩径（audit shrunk_points.count=0）。
- 求解器（tmp build_a20.py）：以布设顺序 M21/M10/M11/M12/M06/M07/M08/M09/M13/M04/M05/
  普通点组依次试 2 行(H60) → 1 行(H36) → 右外栏槽位(cy=194+60k, 按锚 y 最近优先)。
  22 个贴邻 + 3 个外栏(M09/M15/M18)。盒距 ≥4px；盒与任何非本点圆盘净距 >0
  （净距=盒到盘心距−半径，1.5px 宁可余量）；不遮本点盘；家具(轴数值/标题)距离 ≥4px；
  不骑主图框线。锚距 >24px 必须引导线（efectivamente 引导 3 条，全部满足）。

## 引导折线（线宽 2px #7A8698, 端点从圆周出发）
- M09：北上出线 → y380 走廊（M07 标签下 25px / M13 标签上 16px）→ 导轨 x1336 → 槽位 554。
- M15：东缘上行 → y587 走廊（M08 牌底 21px / M12 牌顶与盘距 ≥2.5px）→ x858 下折 →
  y614 东行（M19 盘距 17.2px）→ 导轨 x1330 → 槽位 674。
- M18：默认东行 y593.2 → 导轨 x1333 → 槽位 434。
- 线不入任何标签盒内部、不穿文字、不误连他点（盘净距 ≥ r+2.5 = 8.5px 阈值一律满足）；
  线线交叉 1 处 (M09×M18 @ (1336,434)) ≤ 3 上限；无共线正长重合。

## TOP3 标注
M10(93,TOP1)/M08(91,TOP2)/M23(90,TOP3)：金边 2px #B7791F 底板 + 值行含 TOPn 文本；
其余 1px #D7DBE2；点体未缩放、不加点环。

## 逐图自检（实际看图）
- v01：整图 + 中心口袋(M06/M08/M09/M10/M11/M12)+右栏+M15/M09 线廊+底部放大×6：
  发现 M08 单行金框文本溢出底板（“TOP2”的 P2 越界）→ est 重标定（加粗 13.6/普通 12.1、
  单行含“值”全串）后重渲染。
- v02：同位放大×6 复检：全部 24 标签文本在底板内，金框/TOP 标注/轴/单位“指数”完整，
  引导线无遮字、无数值/标签违规。

## DSL 能力与踩坑
- 根标签必须是 `<Snapshot background type="png"><Stack>`（Canvas/Scene 会被 400 拒绝，
  已留失败请求留痕）；`<Raw>` 可在 Text 内分段着色/加粗；NBSP 防裁剪；
  Container border 制造金框/白底标签牌。

## 过程留痕
- requests.jsonl: 3（1 失败为 400 根标签解析错误，证据完整）；
  iterations.jsonl: 2 轮看图（v01 发现缺陷→修复，v02 复检通过）；
  布局求解 7 次运行中 3 次违规清零（阈值修正前后）；放大查看 6 幅 + 整图 1 幅 × 两轮。
## 未解决事项
- 无。
"""
open(f"{D}/snapshot-usage.md", "w", encoding="utf-8", newline="\n").write(usage)

# ── complete-payload.json ──
pay = {
    "task_id": "A20", "status": "completed",
    "artifacts": ["annotated-map.png", "annotated-map.snapshot", "label-layout.json",
                  "layout-audit.json", "snapshot-usage.md", "task-metrics.json"],
    "summary": "24 点密集标注地图：程序化求解器布设 24 标签（21 贴邻 + 3 右外栏）+ 精确几何审计"
               "(盒距≥4、盒-盘面净距>0、家具≥4、不遮点、锚距>24 必引导线)、3 条轴对齐引导折线、"
               "1 处合法线交叉(≤3)、全文本内联、TOP3 金框；layout-audit 全对通过 + 两轮看图复检。",
    "renders": {"total": 3, "ok": 2, "fail": 1},
    "views": 12, "iterations": 2,
    "time": {"started_at": STARTED, "ended_at": ended_s},
}
json.dump(pay, open(f"{TD}/complete-payload.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ── suite 事件 + 指针 + 检查点 ──
ss_path = f"{SS}/suite-state.json"
st = json.load(open(ss_path, encoding="utf-8"))
tasks = {t["id"]: t for t in st["tasks"]}
a20 = tasks["A20"]
a20["status"] = "completed"
a20["started_at"] = STARTED
a20["ended_at"] = ended_s
a20["artifacts"] = ["annotated-map.png", "annotated-map.snapshot", "label-layout.json",
                    "layout-audit.json", "snapshot-usage.md", "task-metrics.json"]
a20["visual_review_evidence"] = [f"tmp/{RUN}/A20/iterations.jsonl v01/v02 (6+6 缩放查看: 整图/中心口袋/右栏/M15线廊/M09线廊/底部)"]
a20["unresolved_issues"] = []
a20["resume_notes"] = ("24 点求解布局：21 贴邻+3 外栏；3 条引导折线；1 合法交叉(≤3)；"
                       "layout-audit 0 违规全过；v01 修复 M08 单行溢出(est 重标定)后 v02 复检通过。")
st["current_task"] = "A21"; st["current_round"] = None; st["current_case"] = None
st["updated_at"] = ended.isoformat(timespec="milliseconds")
json.dump(st, open(ss_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

ck = {"at": ended.isoformat(timespec="milliseconds"), "run_id": RUN, "action": "complete",
      "task_id": "A20",
      "summary": "A20 完成: annotated-map.png/snapshot + label-layout.json + layout-audit.json 全对"
                 "(0 违规, 1 交叉≤3, 24 标签, 3 引导线), est 重标定修复 M08 溢出, v02 复检通过; next A21 三轮。"}
with open(f"{SD}/events.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(ck, ensure_ascii=False) + "\n")
json.dump(ck, open(f"{SD}/checkpoints/state-000037.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("suite state updated; checkpoint state-000037.json written")
