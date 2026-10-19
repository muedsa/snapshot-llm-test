# -*- coding: utf-8 -*-
"""A22 round-01 收尾：usage/metrics + suite 事件/检查点（补记 task-started）。"""
import json
import os
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
RUN = "20261016T164020-m1"
R1 = f"outputs/{RUN}/A22/round-01"
TMP = f"tmp/{RUN}/A22"
nows = lambda: datetime.now(TZ).isoformat(timespec="seconds")
mt = lambda pp: datetime.fromtimestamp(os.path.getmtime(pp), TZ)
iso = lambda pp: mt(pp).isoformat(timespec="milliseconds")

reqs = [json.loads(l) for l in open(f"{TMP}/requests.jsonl", encoding="utf-8")]
r1reqs = [r for r in reqs if r["response_file"].split("/")[-1].startswith("a22-r01-dash")]
ok = [r for r in r1reqs if r["http_status"] == 200]
fail = [r for r in r1reqs if r["http_status"] != 200]
dur = sum(float((r.get("server_timing") or "0").split("total;dur=")[-1] or 0)
          for r in ok if (r.get("server_timing") or "").count("dur=") >= 2)
started = min(r["started_at"] for r in r1reqs)
end = nows()
first_usable = (datetime.fromisoformat(iso(f"{TMP}/renders/a22-r01-dash-121544311.resp")) -
                datetime.fromisoformat(started)).total_seconds()

metrics = {
    "schema_version": 1, "path_base": "output_dir", "task_id": "A22", "round": 1,
    "run_id": RUN, "status": "completed", "output_dir": "round-01/",
    "timings": {
        "started_at": started, "ended_at": end,
        "elapsed_seconds": round((datetime.fromisoformat(end) -
                                  datetime.fromisoformat(started)).total_seconds(), 1),
        "first_usable_image_seconds": round(first_usable, 1),
        "user_feedback_wait_seconds": None, "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(dur / 1000, 4),
        "server_timing_source": "snapshot_client 自动留痕（X-Server-Timing total）",
    },
    "counts": {
        "snapshot_requests": len(r1reqs),
        "successful_snapshot_requests": len(ok), "failed_snapshot_requests": len(fail),
        "retry_requests": 0, "other_service_requests": 0, "dsl_versions": 2,
        "image_views": 5, "completed_visual_iterations": 1,
        "incomplete_visual_iterations": 0, "final_images": 1,
    },
    "logs": {
        "requests": f"tmp/{RUN}/A22/requests.jsonl（a22-r01-dash 全部 {len(r1reqs)} 条）",
        "iterations": f"tmp/{RUN}/A22/iterations.jsonl",
    },
    "outputs": [
        {"name": n, "path_base": "output_dir", "path": n}
        for n in ("dashboard.png", "dashboard.snapshot", "computed-data.json",
                  "layout-map.json", "snapshot-usage.md", "task-metrics.json")
    ],
    "candidates": [],
    "unresolved_issues": [],
    "notes": "v1 基线查出 KPI 副文与脚注超出卡/行宽被裁 → 缩短文案 v2 通过；"
             "数据与几何未变（次数依据 r1-v2 放大核验 5 列×6 行与柱标签）。",
}
with open(f"{R1}/task-metrics.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=1)

usage = """# A22 round-01 · snapshot-usage

## 状态
completed。round-01/dashboard.png/.snapshot（1600×1000）为服务 200 真实响应（v2），
computed-data.json / layout-map.json / 本报告 / 指标就位；生成脚本
tmp/20261016T164020-m1/A22/build_a22_r01.py（参数与未舍入计算在内）。

## 数据与口径（TASK.md"
共同计算与显示口径"执行）
- 净收入=收入−退款；利润=净收入−经营成本；月退款率=退款÷退款前收入；
  月转化率=订单÷访问；总体转化率=3,045÷27,300（非月均）。
- 展示：金额整数元（KPI/表/结论），柱图按万元两位小数，比率两位小数；
  计算与 JSON 保留原整数与未舍入值，先算后舍。
- 期间合计（2026-04..09）：收入 975,050 / 退款 56,426 / 成本 656,500 /
  净收入 918,624 / 利润 262,124 / 订单 3,045 / 访问 27,300 / 转化率 11.15%。

## 画面结构（与 layout-map.json 同源）
- R-title 36px；R-kpi 四卡（label 22/body 34 值/副文 22）；
- R-chart 全宽面板（28,240,1572,660）：净收入/利润共轴零起点柱图，轴 0–24 万、
  网格 [0,6,12,18,24]、y=598−(v/24)×300、组中心 x=112+(i+0.5)×239.333、
  双柱宽 58+10 间隙、柱顶两位小数标签、月份轴 22px；
- R-table（28,676,1572,886）五列（月份/净收入/经营利润/退款率/转化率）×6 行
  （行高 29.333 未舍入），退款率 ≥7.5% 标红（2026-06/08 8.00%）；
- R-conclusion 22px 两行 + R-footnote 22px 口径行；全图正文最小 22px。

## 标签能力与踩坑
- 沿用 A21 期验证的根 Snapshot>Stack+SizedBox、panel() Container+Stack 定界、
  Text maxLines=1 overflow=CLIP、Inter+CJK 混排；shape="CIRCLE" 图例点。
- v1→v2 修复：KPI 副文与脚注 22px 文本超宽被裁 → 缩短文案；未更动数据/几何
  与主区域边界（layout-map.comparison 基准）。

## 未解决事项
无。rounds/round-02.md 预置需求下一轮生效（2026-08 退款 25,048；2026-09
成本 208,000 → 9 月利润 −5,632，柱图需负轴范围）。
"""
with open(f"{R1}/snapshot-usage.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(usage)

iters = [
    {"id": "A22-r01-baseline-v01", "parent": None, "type": "baseline",
     "image": "steps/r1-half.png", "viewed_at": iso(f"{TMP}/steps/r1-half.png"),
     "images": ["steps/r1-half.png"],
     "observable_issues": ["KPI 卡第 1/2/3/4 卡副文 22px 超出 371px 卡宽尾部被裁；"
                           "脚注行右端被 1600 边缘裁切"],
     "changes": "", "recheck": "触发 visual-v02", "seq": 1},
    {"id": "A22-r01-visual-v02", "parent": "A22-r01-baseline-v01", "type": "visual",
     "image": "steps/r1-v2-half.png", "viewed_at": nows(),
     "images": ["steps/r1-v2-half.png", "steps/r1-v2-kpi.png", "steps/r1-v2-chart.png",
                "steps/r1-v2-table.png"],
     "observable_issues": [],
     "changes": "KPI 副文改短（总退款/经营成本/总访问/3,045÷27,300）；"
                "口径脚注删去『（非月均）』尾链与长尾句",
     "recheck": "v2 放大核验：卡内副文完整、脚注含句号收尾；柱图轴/标签与表格"
                "5×6 数值逐项与 computed-data 一致", "seq": 2},
]
with open(f"{TMP}/iterations.jsonl", "w", encoding="utf-8", newline="\n") as f:
    f.writelines(json.dumps(o, ensure_ascii=False) + "\n" for o in iters)

# ---- suite 状态 ----
SP = f"outputs/{RUN}/_suite/suite-state.json"
st = json.load(open(SP, encoding="utf-8"))
for t in st["tasks"]:
    if t["id"] == "A22":
        t["status"] = "in_progress"
        t["started_at"] = started
        t["completed_rounds"] = [1]
        t["artifacts"] = ["round-01/dashboard.png", "round-01/dashboard.snapshot",
                          "round-01/computed-data.json", "round-01/layout-map.json",
                          "round-01/snapshot-usage.md", "round-01/task-metrics.json"]
        t["visual_review_evidence"] = [
            "r1: v1 half 发现 KPI/脚注溢出 → v2 缩文案重渲通过；v2 half/kpi/chart/table"
            " 5 次查看（2 渲染请求均 200）"]
        t["resume_notes"] = "round-01 完成；round-02 更正 2026-08 refund=25048、" \
                            "2026-09 cost=208000，需负柱轴，区域边界 ±2px。"
st["current_round"] = 2
st["updated_at"] = end
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

ev = f"tmp/{RUN}/_suite/events.jsonl"
with open(ev, "a", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps({"id": "SUITE-ev-000043", "at": started, "kind": "task-started",
                        "task_id": "A22",
                        "detail": "三轮预置；r1 六个月驾驶舱（4 KPI+全宽共轴柱图+5×6 表）"},
                       ensure_ascii=False) + "\n")
    f.write(json.dumps({"id": "SUITE-ev-000044", "at": end, "kind": "round-completed",
                        "task_id": "A22", "round": 1,
                        "detail": "r1 完成：dash v2 通过（1 视觉迭代修复文字溢出）；"
                                  "computed/layout 交付"},
                       ensure_ascii=False) + "\n")
cp = {"at": nows(), "run_id": RUN, "action": "round-complete", "task_id": "A22",
      "round": 1,
      "summary": "r1 六个月驾驶舱 v2 达标（KPI/柱图/表格/结论，正文≥22）；"
                 "下一轮 r2 更正两笔数据并加负轴，边界 ±2px。"}
with open(f"tmp/{RUN}/_suite/checkpoints/state-000042.json", "w",
          encoding="utf-8", newline="\n") as f:
    json.dump(cp, f, ensure_ascii=False, indent=1)
st["last_checkpoint"] = f"tmp/{RUN}/_suite/checkpoints/state-000042.json"
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("r1 finalized:", end, "| reqs", len(r1reqs), "dur", round(dur / 1000, 4),
      "| elapsed", metrics["timings"]["elapsed_seconds"])
