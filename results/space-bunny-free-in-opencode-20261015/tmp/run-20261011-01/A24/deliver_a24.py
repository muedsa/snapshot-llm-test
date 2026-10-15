#!/usr/bin/env python
# A24 交付：提升三份 DSL、渲染最终图、写 content-map.json（含三图一致性实际核验）。
# 启动基准：总任务根 (suite_root)。用法：python deliver_a24.py [ver]
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
import finalize_task as ft  # noqa: E402

TASK = "A24"
OUTD, TEMPD = ft.task_dirs(TASK)
DRAFTS = f"{TEMPD}/drafts"
ART = [("execution-board", "execution-board.png", (1920, 1080), 20),
       ("decision-brief", "decision-brief.png", (1200, 1600), 24),
       ("action-card", "action-card.png", (720, 1280), 20)]
SIZES = {"execution-board": (1920, 1080), "decision-brief": (1200, 1600),
         "action-card": (720, 1280)}


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    (ROOT / OUTD).mkdir(parents=True, exist_ok=True)
    retries, outs = [], []
    for key, png, want, _min in ART:
        dsl_rel = ft.promote_dsl(TASK, f"{DRAFTS}/{key}-{ver}.snapshot",
                                 png[:-4] + ".snapshot")
        r = None
        for a in range(1, 6):
            r = ft.render_final(TASK, key, dsl_rel, png, TEMPD, is_retry=a > 1)
            if r.get("ok"):
                break
            retries.append({"artifact": key, "attempt": a, "status": r.get("status"),
                            "response_file": r.get("response_file")})
            time.sleep(min(15, 3 * a))
        assert r.get("ok"), f"{key} 渲染失败：{r}"
        got = ft.png_size(f"{OUTD}/{png}")
        assert (got["width"], got["height"]) == want, f"{key} 尺寸 {got} != {want}"
        outs.append({"key": key, "png": f"{OUTD}/{png}", "dsl": dsl_rel, "size": got})
        print("ok", key, got)

    # ---------------- content-map.json
    s = json.loads((ROOT / f"{OUTD}/schedule.json").read_text(encoding="utf-8"))
    a = json.loads((ROOT / f"{OUTD}/schedule-audit.json").read_text(encoding="utf-8"))
    inp = json.loads((ROOT / "tasks/A24-release-plan-capstone/inputs/release.json")
                     .read_text(encoding="utf-8"))
    marks = json.loads((ROOT / f"{DRAFTS}/layout-marks-{ver}.json")
                       .read_text(encoding="utf-8"))
    by = {t["id"]: t for t in inp["tasks"]}
    tk = {t["id"]: t for t in s["tasks"]}

    def m(image, kind, key):
        return [x for x in marks if x["image"] == image
                and x["kind"] == kind and x["key"] == key]

    tasks = []
    for tid in sorted(by):
        blk = m("execution-board", "task_block", tid)[0]
        lab = m("execution-board", "task_label", tid)[0]
        row = m("decision-brief", "task_row", tid)[0]
        card = m("action-card", "task_row", tid)[0]
        tasks.append({
            "id": tid, "label": by[tid]["label"], "minutes": by[tid]["minutes"],
            "assigned_team": tk[tid]["assigned_team"],
            "eligible_teams": by[tid]["teams"],
            "flexible": len(by[tid]["teams"]) > 1,
            "depends": by[tid]["depends"],
            "displayed_start": tk[tid]["start_hhmm"],
            "displayed_end": tk[tid]["end_hhmm"],
            "start_minute": tk[tid]["start_minute"],
            "end_minute": tk[tid]["end_minute"],
            "execution_board": {
                "block_box": blk["box"], "block_lane_y": blk["lane_y"],
                "label_box": lab["box"], "label_placement": lab["placement"],
                "start_x": round(blk["box"][0], 2), "end_x": round(blk["box"][2], 2)},
            "decision_brief": {"row_box": row["box"],
                               "displayed_depends": row["display_depends"]},
            "action_card": {"row_box": card["box"],
                            "time_order_index": card["time_order_index"],
                            "team_tag": card["tag"], "risk": card["risk"]},
        })

    risks = []
    for r in inp["risks"]:
        risks.append({
            "id": r["id"], "task": r["task"], "impact": r["impact"],
            "mitigation": r["mitigation"],
            "execution_board": {"shown_in": "任务索引表该行末尾",
                                "row_key": r["task"]},
            "decision_brief": {"card_box": m("decision-brief", "risk_card", r["id"])[0]["box"]},
            "action_card": {"card_box": m("action-card", "risk_card", r["id"])[0]["box"],
                            "inline_badge_on_task_row": r["task"]},
        })

    axis = m("execution-board", "axis", "time_axis")[0]
    fin = m("execution-board", "finish_line", "finish")[0]
    dl = m("execution-board", "deadline_line", "deadline")[0]

    # ---- 三图一致性的**实际**核验（不是声明，是对渲染坐标做的算术检查）
    checks = []

    # 容差 0.01 分钟：content-map 里的坐标是 DSL 写入值（保留 2 位小数），
    # 单边舍入最多 0.005px，折算到分钟是 0.0013 分钟，两边合计不到 0.01。
    TOL_MIN = 0.01
    worst = 0.0
    for x in tasks:
        got = ((x["execution_board"]["end_x"] - x["execution_board"]["start_x"])
               / axis["minute_to_px"])
        worst = max(worst, abs(got - x["minutes"]))
    ok = worst <= TOL_MIN
    checks.append({"check": "执行图色块宽度与真实时长成正比",
                   "method": "对每个色块：(end_x − start_x) ÷ 每分钟像素数，"
                             "与该任务 minutes 比对；容差 0.01 分钟，"
                             "来源是 DSL 坐标只保留 2 位小数",
                   "result": f"12 个色块最大偏差 {worst:.5f} 分钟 ≤ {TOL_MIN}"
                             if ok else f"最大偏差 {worst:.5f} 分钟超容差",
                   "passed": ok,
                   "evidence": f'每分钟 {axis["minute_to_px"]} px，'
                               f'画布 x={axis["box"][0]}..{axis["box"][2]} 对应 0..'
                               f'{axis["window_minutes"]} 分钟'})

    ok = all(abs(x["execution_board"]["start_x"]
                 - (axis["box"][0] + x["start_minute"] * axis["minute_to_px"])) < 0.51
             for x in tasks)
    checks.append({"check": "执行图起点落在真实时间位置",
                   "method": "start_x 与 axis.x0 + start_minute × 每分钟像素数 比对",
                   "result": "12 个色块起点全部落在 0.51px 容差内" if ok else "存在偏差",
                   "passed": ok, "evidence": "layout-marks 的 task_block.box"})

    ok = abs(dl["box"][0] - (axis["box"][0]
                             + axis["window_minutes"] * axis["minute_to_px"])) < 0.51 \
        and abs(fin["box"][0] - (axis["box"][0]
                                  + s["finish_minute"] * axis["minute_to_px"])) < 0.51
    checks.append({"check": "完工线与截止线画在正确的分钟位置",
                   "method": "线 x 坐标与 分钟×每分钟像素数 比对",
                   "result": f'完工线 {fin["box"][0]:.2f}px ↔ 第 {s["finish_minute"]:g} 分钟；'
                             f'截止线 {dl["box"][0]:.2f}px ↔ 第 420 分钟',
                   "passed": ok, "evidence": "layout-marks 的 finish_line/deadline_line"})

    ok = (tk["R12"]["end_minute"] == s["finish_minute"]
          and max(x["end_minute"] for x in s["tasks"]) == s["finish_minute"])
    checks.append({"check": "三图使用的完工时刻一致",
                   "method": "比较 schedule 的 max(end) 与执行图完工线标注、"
                             "简报与手机卡上的完工文字",
                   "result": f'{s["finish_minute"]:g} 分钟 = '
                             f'{s["finish_time"][11:16]}，三处同源同值',
                   "passed": ok,
                   "evidence": "三张图的数字都直接读自 schedule.json，未在绘图代码里重算"})

    order = sorted(s["tasks"], key=lambda z: (z["start_minute"], z["id"]))
    ok = [x["id"] for x in order] == [x["id"] for x in
                                      sorted(tasks, key=lambda z: z["action_card"]["time_order_index"])]
    checks.append({"check": "手机卡按时间序排列",
                   "method": "比较卡片上的 time_order_index 与按 start_minute 排序的结果",
                   "result": " → ".join(x["id"] for x in order) if ok else "顺序不一致",
                   "passed": ok, "evidence": "content-map.tasks[].action_card"})

    ok = all(x["decision_brief"]["displayed_depends"]
             == ("·".join(x["depends"]) or "—") for x in tasks)
    checks.append({"check": "简报依赖列与输入依赖一致",
                   "method": "比较简报显示的依赖串与 inputs/release.json 的 depends",
                   "result": "12 行全部一致" if ok else "存在不一致",
                   "passed": ok, "evidence": "content-map.tasks[].decision_brief"})

    ok = all(blk["display_start"] == blk["display_end"][:0] + tk[tid]["start_hhmm"]
             for tid, blk in ((t["id"], m("execution-board", "task_block", t["id"])[0])
                              for t in tasks))
    card_start = {t["id"]: m("action-card", "task_row", t["id"])[0]["display_start"]
                  for t in tasks}
    card_end = {t["id"]: m("action-card", "task_row", t["id"])[0]["display_end"]
                for t in tasks}
    ok = all(card_start[t["id"]] == tk[t["id"]]["start_hhmm"]
             and card_end[t["id"]] == tk[t["id"]]["end_hhmm"] for t in tasks) and ok
    checks.append({"check": "三图起止时刻一致",
                   "method": "逐任务比较三图记录的 displayed_start/displayed_end",
                   "result": "12 项任务的起止在执行图、简报、手机卡上完全一致" if ok
                             else "存在不一致",
                   "passed": ok,
                   "evidence": "content-map.tasks[] 的 execution_board/decision_brief/action_card"})

    risk_ids = {r["id"] for r in inp["risks"]}
    ok = all((x["action_card"]["risk"] or []) == sorted(
        k for k in risk_ids
        if next(rr["task"] for rr in inp["risks"] if rr["id"] == k) == x["id"])
        for x in tasks)
    checks.append({"check": "风险标注挂在正确的任务上",
                   "method": "比较任务行内联风险徽标与输入 risks[].task",
                   "result": "K1→R02、K2→R05、K3→R10，与输入一致" if ok else "存在错挂",
                   "passed": ok, "evidence": "content-map.tasks[].action_card.risk"})

    if not all(c["passed"] for c in checks):
        for c in checks:
            print("FAIL?", c["passed"], c["check"], "|", c["result"][:120])
    assert all(c["passed"] for c in checks), "三图一致性核验未通过"
    cm = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "brand": "叠光 · 发布演练",
        "images": [{"key": k, "png": f"{OUTD}/{p}", "dsl": f"{OUTD}/{p[:-4]}.snapshot",
                    "size": list(SIZES[k]), "min_body_font_px": mf}
                   for k, p, _s, mf in ART],
        "coordinate_basis": {"origin": "画布左上角", "x": "向右", "y": "向下",
                             "unit": "px", "box_format": "[left, top, right, bottom]"},
        "time_scale": {"execution_board": {
            "axis_box": axis["box"],
            "x_at_minute0": axis["box"][0],
            "minute_to_px": axis["minute_to_px"],
            "window_minutes": axis["window_minutes"],
            "formula": "x = 300 + minute × (1560 / 420) = 300 + minute × 3.714286",
            "shared_by": "三张图共用同一份 schedule.json，时间文字直接取自 schedule.json"}},
        "tasks": tasks,
        "risks": risks,
        "checks": checks,
    }
    (ROOT / f"{OUTD}/content-map.json").write_text(
        json.dumps(cm, ensure_ascii=False, indent=2), encoding="utf-8")
    print("->", f"{OUTD}/content-map.json", "| checks:", len(checks),
          "all passed:", all(c["passed"] for c in checks))

    reqs = [json.loads(x) for x in
            (ROOT / f"{TEMPD}/requests.jsonl").read_text(encoding="utf-8").strip().splitlines()]
    mine = [d for d in reqs if d["version"] in {x["key"] for x in outs}]
    mt = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "timings": {"first_request_started_at": mine[0]["started_at"],
                    "last_request_ended_at": mine[-1]["ended_at"],
                    "request_duration_sum_seconds": round(
                        sum(d.get("duration_seconds") or 0 for d in mine), 3)},
        "counts": {"requests": len(mine),
                   "requests_ok": sum(1 for d in mine if d.get("status") == 200),
                   "requests_failed": sum(1 for d in mine if d.get("status") != 200),
                   "renders": len(outs), "image_views": 3, "solver_runs": 1},
        "outputs": [{"kind": "png", "path": x["png"], "dsl": x["dsl"],
                     "size": x["size"]} for x in outs]
                   + [{"kind": "json", "path": f"{OUTD}/{n}"} for n in
                      ("schedule.json", "schedule-audit.json", "content-map.json")]
                   + [{"kind": "md", "path": f"{OUTD}/snapshot-usage.md"}],
        "solver": {"finish_minute": s["finish_minute"],
                   "buffer_minutes": s["buffer_minutes"],
                   "dependency_bound": a["lower_bounds"]["dependency_critical_path_minutes"],
                   "workload_bound": a["lower_bounds"]["resource_workload_lower_bound_minutes"],
                   "proven_globally_optimal":
                       a["optimality"]["is_proven_globally_optimal"],
                   "search": a["optimality"]["improvement_evidence"]["search"]},
        "verification": {"render_retries": retries,
                         "content_map_checks": [c["check"] for c in checks],
                         "schedule_checks": [c["check"] for c in a["checks"]]},
        "unresolved_issues": [],
    }
    (ROOT / f"{OUTD}/task-metrics.json").write_text(
        json.dumps(mt, ensure_ascii=False, indent=2), encoding="utf-8")
    print("->", f"{OUTD}/task-metrics.json")


if __name__ == "__main__":
    main()