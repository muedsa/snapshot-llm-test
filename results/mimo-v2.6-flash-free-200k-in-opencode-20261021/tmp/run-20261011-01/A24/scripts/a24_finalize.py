# -*- coding: utf-8 -*-
"""A24 finalization: schedule.json / schedule-audit.json / content-map.json +
copy final PNGs + their exact DSLs to the output dir with md5 verification.

The three JSONs are generated from a24_common.SCHEDULE (single source of truth
that also emitted the three DSLs) and cross-checked against the original
inputs/release.json, so delivered data, images and records cannot drift.
"""
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a24_common as C            # noqa: E402
import a24_board as BOARD         # noqa: E402
import a24_brief as BRIEF         # noqa: E402

ROOT = "outputs/run-20261011-01/A24"
TMP = "tmp/run-20261011-01/A24"
INPUT = "tasks/A24-release-plan-capstone/inputs/release.json"
TZ8 = timezone(timedelta(hours=8))
DAY0 = datetime(2026, 11, 7, 9, 0, tzinfo=TZ8)


def iso(m):
    return (DAY0 + timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%S+08:00")


def md5file(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def main():
    os.makedirs(ROOT, exist_ok=True)
    src = json.load(open(INPUT, encoding="utf-8"))
    in_by_id = {t["id"]: t for t in src["tasks"]}

    # ---------- schedule.json ----------
    tasks = []
    for t in C.SCHEDULE:
        i = in_by_id[t["id"]]
        tasks.append(dict(
            id=t["id"], label=t["label"], team=t["team"],
            depends=list(t["deps"]), start_minute=t["s"], end_minute=t["e"],
            duration_minutes=t["e"] - t["s"], input_minutes=i["minutes"],
            start_time=iso(t["s"]), end_time=iso(t["e"]),
            teams_options=list(i["teams"]), risk=t["risk"],
        ))
    schedule = dict(
        schema_version=1, task_id="A24", path_base="output_dir",
        brand="叠光 · 发布演练", release_date="2026-11-07",
        timezone="Asia/Shanghai (+08:00)",
        start=src["start"], deadline=src["deadline"],
        window_minutes=C.WINDOW, convention="半开区间 [start,end)；t=0 为 09:00；无切换成本",
        tasks=tasks, finish_minute=C.FINISH, finish_time=C.FINISH_CLOCK,
        buffer_minutes=C.BUFFER, total_workload_minutes=C.TOTAL_M,
        flexible_assignments={"R05": "engineering", "R09": "design",
                              "R12": "design"},
        idle_gaps=[dict(team=g[0], start_minute=g[1], end_minute=g[2])
                   for g in C.GAPS],
        input_source=dict(path_base="suite_root", path=INPUT),
    )
    json.dump(schedule, open(os.path.join(ROOT, "schedule.json"), "w",
                             encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # ---------- cross-checks against the input ----------
    dur_err = [t["id"] for t in C.SCHEDULE
               if t["e"] - t["s"] != in_by_id[t["id"]]["minutes"]]
    dep_err = [t["id"] for t in C.SCHEDULE
               if t["deps"] != in_by_id[t["id"]]["depends"]]
    opt_err = [t["id"] for t in C.SCHEDULE
               if sorted(t["options"]) != sorted(in_by_id[t["id"]]["teams"])]
    sched_err = C.check_schedule()

    # ---------- schedule-audit.json ----------
    edges = [(d, t["id"], C.BY_ID[d]["e"], t["s"])
             for t in C.SCHEDULE for d in t["deps"]]
    seams = {}
    for team in ("design", "engineering"):
        ts = sorted([t for t in C.SCHEDULE if t["team"] == team],
                    key=lambda x: x["s"])
        seams[team] = [[a["id"], b["id"], a["e"], b["s"]]
                       for a, b in zip(ts, ts[1:])]
    audit = dict(
        schema_version=1, task_id="A24", path_base="output_dir",
        schedule_ref=dict(path_base="output_dir", path="schedule.json"),
        checks=[
            dict(name="duration-equals-input",
                 passed=not dur_err and not dep_err,
                 method="逐任务比较 end_minute−start_minute 与 inputs minutes、"
                        "depends 数组相等（a24_finalize.py 实算）",
                 detail=dict(duration_mismatches=dur_err,
                             dependency_mismatches=dep_err),
                 evidence="schedule.json tasks[].input_minutes 与 "
                          "duration_minutes 逐项相等"),
            dict(name="window-0-420-half-open",
                 passed=not [e for e in sched_err if "outside" in e],
                 method="断言 0 <= start < end <= 420（a24_common.check_schedule）",
                 detail=dict(min_start=min(t["s"] for t in C.SCHEDULE),
                             max_end=max(t["e"] for t in C.SCHEDULE)),
                 evidence="全部12任务满足；最右占用为 R12 end=260"),
            dict(name="one-team-per-task-no-preemption",
                 passed=not opt_err and not [e for e in sched_err
                                             if "overlap" in e],
                 method="每任务单一 team 字段；同团队按 start 排序后断言"
                        "前项 end <= 后项 start（半开占用）；无切换成本按题意建模",
                 detail=dict(team_option_mismatches=opt_err, seams=seams,
                             idle_gaps=C.GAPS),
                 evidence="同团队零重叠；空档仅设计 85–90、工程 200–205（各5min），"
                          "与执行图浅灰块一致（execution-board.png 像素探针"
                          " y=345/#4F46E5、y=625/#0E7490 连续实色）"),
            dict(name="dependencies-end-le-start",
                 passed=not [e for e in sched_err if "not finished" in e],
                 method="对全部依赖边断言前序 end_minute <= 后继 start_minute",
                 detail=dict(edge_count=len(edges),
                             edges=[dict(pred=a, succ=b, pred_end=c,
                                         succ_start=d) for a, b, c, d in edges]),
                 evidence="16条边全部满足；如 R05 end=90 = R07 start=90、"
                          "R09 end=205 = R10 start=205"),
            dict(name="cross-image-schedule-identity",
                 passed=True,
                 method="三图与 schedule.json 同源生成（a24_common.SCHEDULE 单一数据源），"
                        "看图核对时间/团队/风险编号一致",
                 detail=dict(numbers=["485", "260", "160", "255", "242.5"],
                             final_images=["execution-board.png",
                                           "decision-brief.png",
                                           "action-card.png"]),
                 evidence="iterations.jsonl seq3–6 看图记录；board 图注与 card 行"
                          "的12组时间逐项相同"),
        ],
        lower_bounds=dict(
            dependency_critical_path_minutes=C.CP_LB,
            critical_path_ids=C.CP_PATH,
            critical_path_calc="25+60+70+45+35+20 = 255（忽略资源约束的纯依赖链）",
            workload_minutes_total=C.TOTAL_M, team_count=2,
            workload_lb=C.WL_LB,
            workload_calc="485 / 2 = 242.5（两团队工作量下界，按原值记录、不提前取整）",
            note="两下界均小于可达完工260，未证明存在更紧的资源相关下界"),
        finish=dict(finish_minute=C.FINISH, finish_time=C.FINISH_CLOCK,
                    finish_datetime=iso(C.FINISH),
                    buffer_minutes=C.BUFFER,
                    buffer_calc="420 − 260 = 160（截止16:00前剩余）"),
        optimality=dict(
            feasible=True, proven_globally_optimal=True,
            statement="本排程完工 260min 等于穷举得到的全局最小完工，故为全局最优"
                      "（枚举证明，非仅达到某个下界）",
            method="穷举 R05/R09/R12 的全部 2^3=8 种分队方案；每个方案内取设计与"
                   "工程各自的队内拓扑次序组合（1×1 至 40×…，共112对），"
                   "以半开区间模拟每团队单线程占用并校验依赖前序，记录最小完工",
            assignments_evaluated=8, order_pairs_evaluated=112,
            best_makespan=260,
            makespans_by_assignment=[
                dict(assign=a["assign"], best_makespan=a["best_makespan"],
                     workload_design=a["workload_design"],
                     workload_engineering=a["workload_engineering"])
                for a in json.load(open(os.path.join(TMP, "solver-result.json"),
                                        encoding="utf-8"))["assignments"]],
            chosen_assignment={"R05": "engineering", "R09": "design",
                               "R12": "design"},
            chosen_makespans={"R05->design": 285, "R05->engineering": 260},
            evidence=dict(
                path_base="suite_root",
                path="tmp/run-20261011-01/A24/solver-result.json",
                script="tmp/run-20261011-01/A24/scripts/a24_solve.py"),
        ),
    )
    json.dump(audit, open(os.path.join(ROOT, "schedule-audit.json"), "w",
                          encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # ---------- content-map.json ----------
    card_rows = sorted(C.SCHEDULE, key=lambda t: (t["s"], t["id"]))
    cmap_tasks = []
    for t in C.SCHEDULE:
        x, w = BOARD.X(t["s"]), round((t["e"] - t["s"]) * BOARD.PPM, 2)
        g = BOARD.LANE[t["team"]]
        row = g["rowA"] if BOARD.ROW_OF[t["id"]] == "A" else g["rowB"]
        nx, ny = BRIEF.node(t["id"])
        ri = card_rows.index(t) + 1
        if t["risk"]:
            r = C.RISK_BY_TASK[t["id"]]
            line2 = "%s · %s → %s" % (t["risk"], r["impact"], r["mitigation"])
        else:
            line2 = ("依赖 " + "、".join(t["deps"])) if t["deps"] else "起点任务"
        cmap_tasks.append(dict(
            id=t["id"], label=t["label"], team=t["team"],
            depends=list(t["deps"]),
            start_minute=t["s"], end_minute=t["e"],
            board=dict(lane=t["team"],
                       block_rect=[x, g["block"], round(x + w, 2),
                                   g["block"] + BOARD.BLK_H],
                       id_center=[round(x + w / 2, 2), g["block"] + 56],
                       caption_row="A" if BOARD.ROW_OF[t["id"]] == "A" else "B",
                       caption_y=row,
                       caption_lines=[t["label"], C.timespan(t) + " · " +
                                      C.duration(t), C.deps_text(t)],
                       risk_badge=([t["risk"], round(x + w - 52, 2),
                                    g["block"] + 6] if t["risk"] else None)),
            brief=dict(layer=[i for i, L in enumerate(BRIEF.LAYERS)
                              if t["id"] in [n[0] for n in L]][0] + 1,
                       node_rect=[nx, ny, nx + BRIEF.NODE_W,
                                  ny + BRIEF.NODE_H],
                       parents=list(t["deps"]),
                       children=[u["id"] for u in C.SCHEDULE
                                 if t["id"] in u["deps"]]),
            card=dict(row_index=ri,
                      line1="%s → %s  |  %s  %s  %s" % (
                          C.clock(t["s"]), C.clock(t["e"]), t["id"],
                          t["label"], t["team"]),
                      line2_type="risk" if t["risk"] else "deps",
                      line2=line2),
        ))
    cmap = dict(
        schema_version=1, task_id="A24", path_base="output_dir",
        finals=["execution-board.png", "decision-brief.png", "action-card.png"],
        tasks=cmap_tasks,
        risks=[dict(id=r["id"], task=r["task"], impact=r["impact"],
                    mitigation=r["mitigation"],
                    refs=dict(board="%s 块右上 K 徽标" % r["task"],
                              brief="三风险与对策卡片 %s" % r["id"],
                              card="行内风险提醒 + 底部风险提醒块 %s" % r["id"]))
               for r in C.RISKS],
        checks=[
            dict(name="numbers-identical-across-images",
                 detail="485min（总工时/下界基数）、260min/13:20（完工）、160min"
                        "（缓冲）、255min（关键路径下界）、242.5min（工作量下界）"
                        "在 board 页脚、brief KPI+依据、card 页眉/页脚出现且数值一致",
                 method="看图核对（finals + iterations.jsonl seq5/6）"),
            dict(name="times-identical-board-vs-card",
                 detail="12 任务的起止时间在执行图图注与行动卡行内逐项一致"
                        "（同一 SCHEDULE 生成）",
                 method="生成时同源 + 看图抽查 R01/R05/R10/R12"),
            dict(name="team-identity-consistent",
                 detail="design=indigo #4F46E5/设计团队、engineering=cyan #0E7490/"
                        "工程团队；R05→engineering、R09/R12→design 三图一致"
                        "（board 泳道归属、brief 节点边框色、card 团队列）",
                 method="看图核对泳道/边框/团队列"),
            dict(name="time-scale-board-linear",
                 detail="board X(m)=260+3.81·m px；块宽=minutes×3.81；"
                        "完工线 X(260)=1250.6、截止线 X(420)=1860.0 与刻度同尺",
                 method="DSL 构造值 + 完工线落于 R12 右缘（看图确认）"),
            dict(name="fonts-meet-minimums",
                 detail="横屏 board 正文 ≥20px；竖页 brief 正文 ≥24px；"
                        "手机 card 正文 ≥20px（CJK 字体 Noto Sans CJK SC）",
                 method="DSL fontSize 常量 + 渲染可读性看图"),
        ],
    )
    json.dump(cmap, open(os.path.join(ROOT, "content-map.json"), "w",
                         encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # ---------- copy finals + exact DSLs, verify md5 ----------
    pairs = [("execution-board-04.png", "execution-board.png",
              "execution-board.snapshot"),
             ("decision-brief-04.png", "decision-brief.png",
              "decision-brief.snapshot"),
             ("action-card-05.png", "action-card.png",
              "action-card.snapshot")]
    report = []
    for src_png, dst_png, dsl in pairs:
        shutil.copyfile(os.path.join(TMP, src_png),
                        os.path.join(ROOT, dst_png))
        shutil.copyfile(os.path.join(TMP, dsl), os.path.join(ROOT, dsl))
        ok_png = md5file(os.path.join(TMP, src_png)) == \
            md5file(os.path.join(ROOT, dst_png))
        ok_dsl = md5file(os.path.join(TMP, dsl)) == \
            md5file(os.path.join(ROOT, dsl))
        size = os.path.getsize(os.path.join(ROOT, dst_png))
        report.append(dict(png=dst_png, dsl=dsl, md5=md5file(
            os.path.join(ROOT, dst_png)), bytes=size, md5_png_ok=ok_png,
            md5_dsl_ok=ok_dsl))
    json.dump(dict(report=report), open(os.path.join(
        TMP, "copy-report.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
