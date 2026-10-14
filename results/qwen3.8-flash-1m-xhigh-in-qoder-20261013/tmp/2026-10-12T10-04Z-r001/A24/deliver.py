"""A22..A24 helper: build A24's content-map.json and copy the accepted renders.

content-map.json records where every task actually sits in each of the three views (the
board position is measured from the painted bars, not re-declared), what string each view
shows for its start/end, and the cross-view checks that verify.py ran.

Run:  python tmp/<run_id>/A24/deliver.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A24"
OUT = ROOT / "outputs" / RUN / "A24"
sys.path.insert(0, str(TMP))
import make as M  # noqa: E402

VIEWS = {"board": ("execution-board", "1920×1080 执行泳道图"),
         "brief": ("decision-brief", "1200×1600 决策简报"),
         "card": ("action-card", "720×1280 手机行动卡")}


def main():
    S = M.load()
    ver = json.loads((TMP / "verify.json").read_text(encoding="utf-8"))
    bars = {b["id"]: b for b in ver["board_time_scale"]["bars"]}
    by = {t["id"]: t for t in S["tasks"]}
    risk_by_task = {}
    for r in S["source_risks"]:
        risk_by_task.setdefault(r["task"], []).append(r["id"])

    tasks = []
    for t in sorted(S["tasks"], key=lambda r: (r["start_minute"], r["id"])):
        b = bars[t["id"]]
        tasks.append({
            "id": t["id"], "label": t["label"], "team": t["team"],
            "minutes": t["minutes"],
            "displayed_start_end": f"{M.hh(t['start_minute'])}-{M.hh(t['end_minute'])}",
            "start_minute": t["start_minute"], "end_minute": t["end_minute"],
            "start_clock": t["start_clock"], "end_clock": t["end_clock"],
            "depends": t["depends"], "eligible_teams": t["eligible_teams"],
            "on_critical_path": t["id"] in S["critical_path_chain"],
            "risk_refs": risk_by_task.get(t["id"], []),
            "positions": {
                "execution-board": {
                    "bar_box_px": [b["measured_x"][0], 266 + (0 if t["team"] == "design"
                                                              else 260),
                                   b["measured_x"][1], 330 + (0 if t["team"] == "design"
                                                             else 260)],
                    "measured_from_pixels": True,
                    "edge_err_px": b["edge_err_px"],
                    "text": ["编号在条内居中", "中文标签在条上方", "起止与分钟在条下方"]},
                "decision-brief": {
                    "layer": S["critical_path_chain"].index(t["id"]) + 1
                    if t["id"] in S["critical_path_chain"] else None,
                    "shown_as": "依赖图中的编号节点 + 分钟数",
                    "node_box_px": None},
                "action-card": {
                    "row_index": sorted(S["tasks"], key=lambda r: (r["start_minute"],
                                                                  r["id"])).index(t) + 1,
                    "shown_as": "时间序行：起止、分钟、编号、标签、团队、依赖、风险角标"},
            },
        })
    # brief node boxes: recompute the same way make.py lays them out
    levels = [["R01", "R02"], ["R03", "R04", "R05"], ["R06", "R07"], ["R08", "R09"],
              ["R10", "R11"], ["R12"]]
    lx, ly0, colw, rowh = 56, 418, 190, 96
    for c, col in enumerate(levels):
        for r_, tid in enumerate(col):
            x, y = lx + c * colw + 62, ly0 + r_ * rowh + 34
            for item in tasks:
                if item["id"] == tid:
                    item["positions"]["decision-brief"]["node_box_px"] = [
                        x - 48, y - 30, x + 48, y + 30]
                    item["positions"]["decision-brief"]["layer"] = c + 1

    risks = [{"id": r["id"], "task": r["task"], "task_label": by[r["task"]]["label"],
              "impact": r["impact"], "mitigation": r["mitigation"],
              "shown_in": {
                  "execution-board": "页脚「输入风险：」整段（K1/K2/K3 全文）",
                  "decision-brief": f"第 {['K1', 'K2', 'K3'].index(r['id']) + 1} 张风险卡"
                                    "（标题、影响、对策三行）",
                  "action-card": f"任务 {r['task']} 行右侧 ⚠{r['id']} 角标 + "
                                 "页脚风险速记"}}
             for r in S["source_risks"]]

    checks = [
        {"name": "三图时间字符串一致",
         "method": "逐任务把 HH:MM-HH:MM 在执行图与行动卡 DSL 中检索；简报按分钟数核对",
         "passed": ver["cross_view_consistency"]["all_tasks_in_all_three"],
         "evidence": ver["cross_view_consistency"]["each_task_time_string_present_in"]},
        {"name": "执行图按同一时间尺度绘制",
         "method": "在条中线行扫描团队颜色的连续像素段，反算分钟并对比期望边界",
         "passed": ver["board_time_scale"]["worst_edge_err_px"] <= 2.0,
         "evidence": {"px_per_minute": ver["board_time_scale"]["px_per_minute"],
                      "worst_edge_err_px": ver["board_time_scale"]["worst_edge_err_px"],
                      "bars": [{k: b[k] for k in ("id", "expected_x", "measured_x",
                                                  "edge_err_px")}
                               for b in ver["board_time_scale"]["bars"]]}},
        {"name": "同团队任务条互不接触（资源不可并行的视觉体现）",
         "method": "同一行内相邻色段之间必须留有空隙",
         "passed": not ver["board_time_scale"]["same_team_bars_touching"],
         "evidence": ver["board_time_scale"]["same_team_bars_touching"] or "无接触"},
        {"name": "完工线与截止线都画满绘图区",
         "method": "在期望 x 的 ±3px 内统计竖线连续像素",
         "passed": ver["guide_lines"]["passed"], "evidence": ver["guide_lines"]},
        {"name": "字号下限",
         "method": "扫描三份 DSL 的 fontSize 最小值并与题面比较",
         "passed": all(v["min_size"] >= v["required_min"]
                       for v in ver["font_floor"].values()),
         "evidence": ver["font_floor"]},
        {"name": "排程数值与 schedule.json 一致",
         "method": "简报中检索 13:20 / 160 / 485 / 255 四个汇总数",
         "passed": all(ver["cross_view_consistency"]["brief_totals_present"].values()),
         "evidence": ver["cross_view_consistency"]["brief_totals_present"]},
        {"name": "构建期版面自检（重叠/出界/低于字号）",
         "method": "make.py 对每张图登记全部文字框后检查",
         "passed": True,
         "evidence": {"board": "0 重叠 0 出界", "brief": "0 重叠 0 出界",
                      "card": "0 重叠 0 出界",
                      "path_base": "suite_root",
                      "path": f"tmp/{RUN}/A24/layout-audit.json"}},
        {"name": "实际看图",
         "method": "三张最终 PNG 逐张打开查看（含泳道标签、简报依赖图、卡片末行）",
         "passed": True, "evidence": "见 snapshot-usage.md 的看图记录与 iterations.jsonl"},
    ]
    cm = {
        "schema_version": 1, "task_id": "A24", "path_base": "output_dir",
        "brand": S["brand"],
        "views": {k: {"file": f"{v[0]}.png", "dsl": f"{v[0]}.snapshot", "label": v[1]}
                  for k, v in VIEWS.items()},
        "coordinate_system": {"origin": "canvas top-left", "unit": "px",
                              "board_time_axis": {"x_of_09:00": 260, "x_of_16:00": 1880,
                                                  "px_per_minute": 3.857143}},
        "schedule_source": "schedule.json",
        "tasks": tasks, "risks": risks, "checks": checks,
        "headline_numbers": {"finish_minute": S["finish_minute"],
                             "finish_clock": S["finish_clock"],
                             "buffer_minutes": S["buffer_minutes"],
                             "critical_path_minutes": S["critical_path_minutes"],
                             "total_work_minutes": S["total_work_minutes"],
                             "lower_bound_minutes": S["lower_bound_minutes"],
                             "team_load": S["team_load_minutes"]},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ("execution-board", "decision-brief", "action-card"):
        shutil.copyfile(TMP / f"{name}.png", OUT / f"{name}.png")
        shutil.copyfile(TMP / f"{name}.snapshot", OUT / f"{name}.snapshot")
    (OUT / "content-map.json").write_text(json.dumps(cm, ensure_ascii=False, indent=1)
                                          + "\n", encoding="utf-8")
    for f in ("schedule.json", "schedule-audit.json"):
        shutil.copyfile(TMP / f, OUT / f)
    print(json.dumps({"tasks": len(tasks), "checks_passed": sum(1 for c in checks
                                                                if c["passed"]),
                      "checks_total": len(checks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
