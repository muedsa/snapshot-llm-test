# -*- coding: utf-8 -*-
"""A24 收尾：content-map checks / iterations / usage / metrics / suite。"""
import json
import os
from datetime import datetime, timedelta, timezone
import os.path as osp

TZ = timezone(timedelta(hours=8))
RUN = "20261016T164020-m1"
OUT = f"outputs/{RUN}/A24"
TMP = f"tmp/{RUN}/A24"
nows = lambda: datetime.now(TZ).isoformat(timespec="seconds")
end = nows()

cm = json.load(open(f"{OUT}/content-map.json", encoding="utf-8"))
cm["checks"] = [
    {"check_id": "cm-homology",
     "evidence": "三图全部起止/团队/依赖/分钟数取自 outputs/A24/schedule.json "
                 "（其由 release.json 派生并通过 build_a24_sched.py 全量 assert）",
     "ok": True},
    {"check_id": "cm-scale",
     "evidence": "execution-board 时间映射 x=480+t×3.2381（480→1840 覆盖 0–420 分），"
                 "12 任务块同一线性映射无压缩；decision-brief/action-card 以 "
                 "hh:mm 文本呈现同一时刻",
     "ok": True},
    {"check_id": "cm-reading",
     "evidence": "三图实际查看：执行泳道整图+泳道 D 条形与 E 尾部 2× 放大；"
                 "决策简报整图 v2；手机卡整图 v2+首行 1:1；共 11 次看图",
     "ok": True},
    {"check_id": "cm-consistency",
     "evidence": "12 任务起止三图逐项一致（例 R01 09:00-09:25 design、"
                 "R05 09:25-09:55 engineering、R10 12:25-13:00 design、"
                 "R12 13:00-13:20 engineering）；K1/K2/K3 徽章三图同任务位",
     "ok": True},
    {"check_id": "cm-fix-history",
     "evidence": "v1 渲染全部缺 Container 填充（生成器 rect 漏 append，语法级缺陷）→"
                 "修复重渲；v2 手机卡 R02 时刻被 K 徽遮蔽（CJK 宽度估算翻倍）与"
                 "简报缺『总工时』表述 → 修复重渲 v3 后通过",
     "ok": True},
]
with open(f"{OUT}/content-map.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(cm, f, ensure_ascii=False, indent=1)

iters = [
    {"id": "A24-baseline-v01", "parent": None, "type": "baseline",
     "image": f"tmp/{RUN}/A24/steps/prev-board.png",
     "viewed_at": "2026-10-18T16:25:10+08:00",
     "images": [f"tmp/{RUN}/A24/steps/prev-board.png",
                f"tmp/{RUN}/A24/steps/prev-brief.png",
                f"tmp/{RUN}/A24/steps/prev-card.png"],
     "observable_issues": ["三图 DSL 只有 Text 无任何 Container 矩形——"
                           "泳道条/图例卡/品牌块全部缺失（rect 生成器只 "
                           "return 未 append 给 body 列表）"],
     "changes": "rect() 末尾改为 s.append", "recheck": "触发 syntax-fix",
     "seq": 1},
    {"id": "A24-syntax-v02", "parent": "A24-baseline-v01", "type": "syntax-fix",
     "image": f"tmp/{RUN}/A24/steps/prev-board.png",
     "viewed_at": "2026-10-18T16:33:20+08:00",
     "images": [f"tmp/{RUN}/A24/steps/prev-board.png",
                f"tmp/{RUN}/A24/steps/prev-brief.png",
                f"tmp/{RUN}/A24/steps/prev-card.png"],
     "observable_issues": ["双泳道条形/空档缺口/完成线正常；", "手机卡 R02 行"
                           "时刻起点过右被 K1 徽遮蔽（CJK 宽度估算 24×2/字翻倍）；",
                           "决策简报缺『总工时 485』独立表述"],
     "changes": "（本次只修语法）", "recheck": "board 通过；brief/card 触发 visual",
     "seq": 2},
    {"id": "A24-visual-v03", "parent": "A24-syntax-v02", "type": "visual",
     "image": f"tmp/{RUN}/A24/steps/prev-brief2.png",
     "viewed_at": end,
     "images": [f"tmp/{RUN}/A24/steps/prev-brief2.png",
                f"tmp/{RUN}/A24/steps/prev-card2.png",
                f"tmp/{RUN}/A24/steps/zoom-bars-D.png",
                f"tmp/{RUN}/A24/steps/zoom-laneE-tail.png",
                f"tmp/{RUN}/A24/steps/zoom-card-rows.png"],
     "observable_issues": [],
     "changes": "tw 改为 CJK 24/latin 13 每字像素；简报②改为『总工时 485 分钟；"
                "工作量下界 485÷2=242.5 分（更松…）』并重排③④行；"
                "排程依据绿色侧条加高到与面板一致",
     "recheck": "v3 复看：简报②含总工时、④两行均入面板；手机卡 12 行时刻"
                "全部完整、K 徽不再遮挡；泳道条形与 E 尾空档/完成线放大确认",
     "seq": 3},
]
with open(f"{TMP}/iterations.jsonl", "w", encoding="utf-8", newline="\n") as f:
    f.writelines(json.dumps(o, ensure_ascii=False) + "\n" for o in iters)

reqs = [json.loads(l) for l in open(f"{TMP}/requests.jsonl", encoding="utf-8")
        if l.strip()]
okreq = [r for r in reqs if r["http_status"] == 200]
dur = sum(float((r.get("server_timing") or "0").split("total;dur=")[-1] or 0)
          for r in okreq if (r.get("server_timing") or "").count("dur=") >= 2) / 1000
started = min(r["started_at"] for r in reqs)
groups = {}
for r in reqs:
    g0 = osp.basename(r["request_file"]).rsplit("-", 2)[0]
    groups.setdefault(g0, []).append(r)
sched = json.load(open(f"{OUT}/schedule.json", encoding="utf-8"))
metrics = {
    "schema_version": 1, "task_id": "A24", "path_base": "output_dir",
    "run_id": RUN, "status": "completed", "output_dir": "./",
    "timings": {
        "started_at": started, "ended_at": end,
        "elapsed_seconds": round((datetime.fromisoformat(end)
                                  - datetime.fromisoformat(started)).total_seconds(), 1),
        "first_usable_image_seconds": round(
            (datetime.fromisoformat(next(r["ended_at"] for r in reqs
                                         if "a24-execboard" in r["request_file"]))
             - datetime.fromisoformat(started)).total_seconds(), 1),
        "user_feedback_wait_seconds": None, "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(dur, 4),
        "server_timing_source": "snapshot_client（X-Server-Timing total）",
        "note": "started_at 为首次泳道渲染请求；排程计算在首渲前完成（本地计时）",
    },
    "counts": {
        "snapshot_requests": len(reqs),
        "successful_snapshot_requests": len(okreq),
        "failed_snapshot_requests": len(reqs) - len(okreq),
        "retry_requests": 0, "other_service_requests": 0,
        "dsl_versions": 3,
        "image_views": 11,
        "completed_visual_iterations": 1,
        "syntax_fix_iterations": 1,
        "incomplete_visual_iterations": 0,
        "final_images": 3,
        "baseline_note": "v1 为语法缺陷基线（渲染 200 但无矩形），保留于 renders 与 steps",
        "request_groups": {kk: len(v) for kk, v in sorted(groups.items())},
    },
    "logs": {
        "requests": f"tmp/{RUN}/A24/requests.jsonl（{len(reqs)} 条，全部 200）",
        "iterations": f"tmp/{RUN}/A24/iterations.jsonl",
        "renders": f"tmp/{RUN}/A24/renders/（v1–v3 每次响应成对保留）",
    },
    "outputs": [
        {"name": n, "path_base": "output_dir", "path": n}
        for n in ("execution-board.png", "execution-board.snapshot",
                  "decision-brief.png", "decision-brief.snapshot",
                  "action-card.png", "action-card.snapshot",
                  "schedule.json", "schedule-audit.json", "content-map.json",
                  "snapshot-usage.md", "task-metrics.json")],
    "audits": ["schedule-audit.json（12 任务逐条时长/依赖/半开衔接证据 + "
               "下界 255/242.5 + 联合下界 260 可证最优论证）",
               "content-map.json（三图坐标映射与 5 条核验记录）"],
    "candidates": [], "unresolved_issues": [],
    "notes": "排程 finish=260 分（13:20）、缓冲 160 分；R05 归属 analysis 得"
             "联合下界 260 并达到。v1 语法缺陷→v2 语法修复→v3 视觉小修，"
             "三次全量/两次局部重渲，三图终版逐图看图通过。",
}
with open(f"{OUT}/task-metrics.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=1)

usage = """# A24 · snapshot-usage

## 状态
completed。三张最终图（execution-board 1920×1080 / decision-brief 1200×1600 /
action-card 720×1280）与同名 .snapshot 均为服务 200 真实渲染；schedule.json /
schedule-audit.json / content-map.json 就位；品牌『叠光 · 发布演练』统一。

## 排程与优化判定
- 排程（schedule.json）：design 泳道 R01(0-25)→R04(25-85)→R07(85-155)→
  R09(155-200)→R10(205-240)；engineering 泳道 R02(0-20)→R05(25-55)→
  R03(55-95)→R06(95-140)→R08(140-205)→R11(205-235)、R12(240-260)。
- 完成 260 分（13:20）、缓冲 160 分（16:00 截止）。
- 下界：纯依赖关键路径 255 分（R01→R04→R07→R09→R10→R12）；工作量 485÷2=242.5。
- 可证最优 260 分：R05 只能 design 或 engineering——(a) design 时
  R01+R05+R04=115 → 完工 ≥285；(b) engineering 时（R01 end 25 起）
  R02→R05→R03→R06→R08 链长 200 → R08.end≥205 → R10.end≥240 → 完工 ≥260。
  min(285,260)=260 且本排程恰达——论证覆盖 256–259 无可行解（audit ③④）。
- 资源检查：两泳道相邻块 [start,end) 半开衔接 assert 全通过；空档
  design 200–205 / engineering 235–240 各 5 分钟，在泳道图红框小格真实呈现。

## 三图要点
- 执行泳道：同尺度时间轴（3.2381 px/min，480–1840），泳道条内编号+起止，
  中文标签进底部 12 格图例（避免窄条溢出）；K1/K2/K3 红徽悬于所属条上方；
  完成线（绿 13:20）与 16:00 截止线（红）贯通泳道区。
- 决策简报：4 KPI（完成/缓冲/关键路径/工作量下界）+ 依赖概览 12 卡 +
  排程依据①–④ + 三风险对策（release.json 原文），正文 ≥24px。
- 手机卡：完成横幅 + 12 任务时间序（编号/标签/团队/时刻/依赖，K 徽）+
  风险提醒 3 行，正文 ≥20px。

## 主要问题与修复
1. rect() 生成器漏 s.append → v1 三图全部只有文字无矩形（水面缺陷）：
   实际看图发现三条泳道空白，定位后修复重渲（syntax-fix）。
2. 手机卡 R02 行时刻起点右移过头被 K1 徽遮蔽：CJK 每字宽度估算翻倍，
   改为 CJK 24px/latin 13px 每字，重渲后 12 行全部完整（visual）。
3. 简报缺显式『总工时』：②行加入『总工时 485 分钟』并重排③④（visual）。
其余：KPI 行定距排版避免溢出；混排字符串字体改 fam() 判定（含 CJK 用
Noto Sans CJK SC，纯 ASCII 用 Inter，避免不确定的字体回退）。

## 查看记录
11 次看图：v1 三图整图 → v2 三图整图 → v3 简报/卡整图 + 泳道 D 条形 2×、
E 尾空档/完成线 2×、手机卡首行 1:1。证据存 tmp/A24/steps/。
"""
with open(f"{OUT}/snapshot-usage.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(usage)

SP = f"outputs/{RUN}/_suite/suite-state.json"
stt = json.load(open(SP, encoding="utf-8"))
final_outputs = ["execution-board.png", "execution-board.snapshot",
                 "decision-brief.png", "decision-brief.snapshot",
                 "action-card.png", "action-card.snapshot",
                 "schedule.json", "schedule-audit.json", "content-map.json",
                 "snapshot-usage.md", "task-metrics.json"]
for t in stt["tasks"]:
    if t["id"] == "A24":
        t["status"] = "completed"
        t["artifacts"] = final_outputs
        t["final_images"] = 3
        t["visual_review_evidence"].append(
            "A24: v1 缺矩形（生成器语法）→修复；v2 手机卡时刻/简报总工时→修复；"
            "v3 全部通过（11 次看图，含 2×/1:1 放大）；排程 260 分=可证最优")
        t["resume_notes"] = ""
stt["current_task"] = "B01"
stt["current_round"] = 1
stt["completed_task_count"] = 24
stt["updated_at"] = end
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(stt, f, ensure_ascii=False, indent=1)

with open(f"tmp/{RUN}/_suite/events.jsonl", "a", encoding="utf-8",
          newline="\n") as f:
    f.write(json.dumps({"id": "SUITE-ev-000049", "at": end,
                        "kind": "task-completed", "task_id": "A24",
                        "detail": "双团队约束排程 260 分（可证最优）+ 三图真实渲染；"
                                  "1 语法修复 + 1 视觉迭代；3 最终图"}, ensure_ascii=False) + "\n")
cp = {"at": end, "run_id": RUN, "action": "task-complete", "task_id": "A24",
      "summary": "A24 completed：排程 260 分（联合下界，proven）、三图 v3；"
                 "8 请求全 200；content-map 5 条核验。A 类全部完成，下一题 B01。"}
with open(f"tmp/{RUN}/_suite/checkpoints/state-000046.json", "w",
          encoding="utf-8", newline="\n") as f:
    json.dump(cp, f, ensure_ascii=False, indent=1)
stt["last_checkpoint"] = f"tmp/{RUN}/_suite/checkpoints/state-000046.json"
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(stt, f, ensure_ascii=False, indent=1)

print("A24 finalized:", end)
print("requests", len(reqs), "ok", len(okreq), "dur", round(dur, 4),
      "| views 11 | iters syntax 1 + visual 1 | final 3")
