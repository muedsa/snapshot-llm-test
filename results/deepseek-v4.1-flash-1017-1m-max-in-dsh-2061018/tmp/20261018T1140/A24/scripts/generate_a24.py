"""A24 · two-team release plan: board, brief, action card from one schedule."""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A24"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Pos, Row, SizedBox, Stack, T  # noqa: E402

FONT = "Inter,Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC,Inter"
TZ = timezone(timedelta(hours=8))
START = datetime(2026, 11, 7, 9, 0, tzinfo=TZ)
SCHED = {
    "R01": (0, 25, "design"), "R02": (0, 20, "engineering"), "R03": (20, 60, "engineering"),
    "R04": (25, 85, "design"), "R05": (60, 90, "engineering"), "R06": (90, 135, "engineering"),
    "R07": (90, 160, "design"), "R08": (135, 200, "engineering"), "R09": (160, 205, "design"),
    "R10": (205, 240, "design"), "R11": (205, 235, "engineering"), "R12": (240, 260, "design"),
}
COL = {"design": "#F97362", "engineering": "#38BDF8"}


def hm(minute):
    return (START + timedelta(minutes=minute)).strftime("%H:%M")


def iso(minute):
    return (START + timedelta(minutes=minute)).isoformat()


def load():
    return json.loads((ROOT / "tasks" / "A24-release-plan-capstone" / "inputs" / "release.json").read_text(encoding="utf-8"))


def schedule_json(data):
    tasks = []
    for t in data["tasks"]:
        st, en, team = SCHED[t["id"]]
        tasks.append({"id": t["id"], "label": t["label"], "team": team, "depends": t["depends"],
                      "minutes": t["minutes"], "start_minute": st, "end_minute": en,
                      "start": iso(st), "end": iso(en), "team_options": t["teams"]})
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
            "timezone": "Asia/Shanghai (+08:00)", "start": iso(0), "deadline": iso(420),
            "tasks": tasks, "finish_minute": max(v[1] for v in SCHED.values()),
            "finish": iso(max(v[1] for v in SCHED.values())), "buffer_minutes": 420 - max(v[1] for v in SCHED.values()),
            "total_work_minutes": sum(t["minutes"] for t in data["tasks"]),
            "objective": "minimize max end minute; feasible schedule; no global optimality proof"}


def board(data):
    W, H = 1920, 1080
    X0, X1 = 430, 1810
    scale = (X1 - X0) / 420
    nodes = [SizedBox(W, H), Pos(0, 0, C(width=W, height=H, color="#0A111D")),
             Pos(0, 0, C(width=W, height=6, gradientType="LINEAR", gradientColors="#F97362,#38BDF8,#F5C451",
                         gradientBegin="CENTER_LEFT", gradientEnd="CENTER_RIGHT")),
             Pos(48, 38, T("叠光 · 发布演练", size=22, color="#F97362", weight="BOLD", family=FONT, spacing=2)),
             Pos(48, 70, T("双团队发布作战图", size=40, color="#F4F7FB", weight="BOLD", family=FONT)),
             Pos(48, 122, T("09:00 开工 · 16:00 截止 · 真实时间同尺度", size=20, color="#9AA9BD", family=FONT)),
             Pos(1170, 70, T("完工 13:20", size=28, color="#34D399", weight="BOLD", family=FONT)),
             Pos(1380, 70, T("缓冲 160 min", size=28, color="#F5C451", weight="BOLD", family=FONT)),
             Pos(1640, 74, T("总工时 485 min", size=20, color="#9AA9BD", family=FONT))]
    # lanes
    nodes += [Pos(40, 180, C(width=1840, height=360, color="#0F1B2D", borderRadius=14, border="1 SOLID #22344D")),
              Pos(40, 560, C(width=1840, height=360, color="#0F1B2D", borderRadius=14, border="1 SOLID #22344D")),
              Pos(56, 190, T("DESIGN / 设计", size=24, color="#FDBA74", weight="BOLD", family=FONT)),
              Pos(56, 570, T("ENGINEERING / 工程", size=24, color="#7DD3FC", weight="BOLD", family=FONT))]
    # time grid
    for i in range(8):
        x = X0 + 60 * i * scale
        nodes.append(Pos(x, 180, C(width=1, height=740, color="#253750")))
        if i < 7:
            nodes.append(Pos(x - 24, 155, T(f"{9+i:02d}:00", size=20, color="#7F91A8", family=FONT)))
    nodes.append(Pos(X1, 180, C(width=3, height=740, color="#F87171")))
    nodes.append(Pos(X1 - 30, 144, T("16:00", size=18, color="#F87171", weight="BOLD", family=FONT)))
    ex = X0 + 260 * scale
    nodes.append(Pos(ex, 180, C(width=2, height=740, color="#34D399")))
    nodes.append(Pos(ex - 24, 144, T("13:20", size=18, color="#34D399", weight="BOLD", family=FONT)))
    # rows: design 6, engineering 6
    design = [t for t in data["tasks"] if SCHED[t["id"]][2] == "design"]
    eng = [t for t in data["tasks"] if SCHED[t["id"]][2] == "engineering"]
    design.sort(key=lambda t: (SCHED[t["id"]][0], t["id"]))
    eng.sort(key=lambda t: (SCHED[t["id"]][0], t["id"]))
    rows = []
    for lane, ts, y0 in (("design", design, 220), ("engineering", eng, 600)):
        for i, t in enumerate(ts):
            st, en, team = SCHED[t["id"]]
            y = y0 + i * 52
            rows.append((t["id"], lane, y))
            nodes.append(Pos(64, y - 2, T(f'{t["id"]}  {t["label"]}', size=20, color="#F4F7FB", weight="BOLD", family=FONT)))
            dep = "—" if not t["depends"] else "← " + ", ".join(t["depends"])
            nodes.append(Pos(64, y + 22, T(f'{hm(st)}–{hm(en)} · {dep}', size=20, color="#93A6C2", family=FONT)))
            bx = X0 + st * scale
            bw = max(3, (en - st) * scale)
            bar_kw = {"width": bw, "height": 30, "color": COL[team], "borderRadius": 5}
            if t["id"] in ("R02", "R05", "R10"):
                bar_kw["border"] = "2 SOLID #F5C451"
            nodes.append(Pos(bx, y + 2, C(**bar_kw)))
            nodes.append(Pos(bx + max(4, (bw - 40) / 2), y + 6, T(t["id"], size=20, color="#07101E", weight="BOLD", family=FONT)))
    # buffer bracket
    nodes.append(Pos(ex, 1000, C(width=X1 - ex, height=2, color="#F5C451")))
    nodes.append(Pos(ex + 10, 1010, T("160 min 缓冲", size=18, color="#F5C451", family=FONT)))
    dsl = f'<Snapshot type="png" background="#0A111D">\n' + Stack(nodes, width=W, height=H) + "\n</Snapshot>\n"
    return dsl, {"canvas": [W, H], "timeline": [X0, X1], "scale_px_per_min": scale, "rows": rows}


def brief(data):
    W, H = 1200, 1600
    nodes = [SizedBox(W, H), Pos(0, 0, C(width=W, height=H, color="#F7F4EC")),
             Pos(56, 40, T("叠光 · 发布演练", size=20, color="#C2410C", weight="BOLD", family=FONT, spacing=2)),
             Pos(56, 76, T("发布决策简报", size=44, color="#14213D", weight="BOLD", family=FONT)),
             Pos(56, 134, T("双团队 · 12 任务 · 09:00–16:00（+08:00）", size=22, color="#5B6B7C", family=FONT)),
             Pos(980, 48, T("2026.11.07", size=18, color="#5B6B7C", family=FONT))]
    kpis = [("完工", "13:20", "260 min"), ("缓冲", "160 min", "420 − 260"), ("总工时", "485 min", "12 项之和"), ("关键路径", "255 min", "R01→R04→R07→R09→R10→R12")]
    for i, (lab, val, sub) in enumerate(kpis):
        x = 56 + i * 274
        nodes += [Pos(x, 180, C(width=258, height=108, color="#FFFFFF", borderRadius=12, border="1 SOLID #E3DCCF")),
                  Pos(x + 18, 196, T(lab, size=20, color="#5B6B7C", family=FONT)),
                  Pos(x + 18, 222, T(val, size=30, color="#14213D", weight="BOLD", family=FONT)),
                  Pos(x + 18, 258, T(sub, size=16, color="#8A97A8", family=FONT))]
    nodes += [Pos(56, 316, T("排程依据", size=26, color="#14213D", weight="BOLD", family=FONT)),
              Pos(56, 354, T("R05 放工程后，R07 从最早 10:25 顺延到 10:30；之后关键链仍连续。实际完工 260，比依赖下界 255 多 5 min；未证明全局最优。", size=24, color="#5B6B7C", family=FONT, height="1.5"), w=1088, h=110)]
    # dependencies: one-line rows at 24px
    nodes.append(Pos(56, 500, C(width=1088, height=560, color="#FFFFFF", borderRadius=12, border="1 SOLID #E3DCCF")))
    nodes.append(Pos(76, 516, T("依赖与任务", size=24, color="#14213D", weight="BOLD", family=FONT)))
    tasks = sorted(data["tasks"], key=lambda t: t["id"])
    for i, t in enumerate(tasks):
        y = 552 + i * 40
        st, en, team = SCHED[t["id"]]
        dep = "—" if not t["depends"] else ",".join(t["depends"])
        nodes.append(Pos(76, y, T(f'{t["id"]}  {t["label"]} · {t["minutes"]}m · {hm(st)}–{hm(en)} · {team} · ←{dep}',
                                 size=24, color="#14213D", family=FONT)))
    # risks
    nodes.append(Pos(56, 1080, T("三风险与对策", size=26, color="#14213D", weight="BOLD", family=FONT)))
    y = 1080
    for r in data["risks"]:
        nodes.append(Pos(56, y, C(width=1088, height=110, color="#FFFFFF", borderRadius=10, border="1 SOLID #E3DCCF")))
        nodes.append(Pos(76, y + 12, T(f'{r["id"]} · {r["task"]}  {r["impact"]}', size=24, color="#9A3412", weight="BOLD", family=FONT)))
        nodes.append(Pos(76, y + 52, T("对策：" + r["mitigation"], size=24, color="#5B6B7C", family=FONT)))
        y += 118
    nodes.append(Pos(56, 1450, T("关键路径下界 255 · 工作量下界 242.5 · 实际完工 260 · 缓冲 160；仅称可行，不称最优。", size=20, color="#5B6B7C", family=FONT)))
    nodes.append(Pos(56, 1530, T("数据源：release.json · 所有时间 +08:00 · 三图同一排程", size=18, color="#8A97A8", family=FONT)))
    dsl = f'<Snapshot type="png" background="#F7F4EC">\n' + Stack(nodes, width=W, height=H) + "\n</Snapshot>\n"
    return dsl, {"canvas": [W, H], "table_rows": [(t["id"], 558 + (i % 6) * 58, 76 + (i // 6) * 536) for i, t in enumerate(tasks)]}


def action(data):
    W, H = 720, 1280
    nodes = [SizedBox(W, H), Pos(0, 0, C(width=W, height=H, color="#0A111D")),
             Pos(0, 0, C(width=W, height=6, color="#F97362")),
             Pos(36, 30, T("叠光 · 发布演练", size=16, color="#F97362", weight="BOLD", family=FONT, spacing=1)),
             Pos(36, 58, T("发布行动卡", size=34, color="#F4F7FB", weight="BOLD", family=FONT)),
             Pos(36, 102, T("09:00 → 13:20 完工 · 缓冲 160 min", size=20, color="#9AA9BD", family=FONT))]
    tasks = sorted(data["tasks"], key=lambda t: (SCHED[t["id"]][0], t["id"]))
    for i, t in enumerate(tasks):
        st, en, team = SCHED[t["id"]]
        y = 160 + i * 76
        if i % 2 == 0:
            nodes.append(Pos(24, y - 8, C(width=672, height=66, color="#101D31", borderRadius=8)))
        nodes.append(Pos(36, y, T(f'{hm(st)}', size=20, color=COL[team], weight="BOLD", family=MONO)))
        nodes.append(Pos(36, y + 24, T(f'{hm(en)}', size=18, color="#7F91A8", family=MONO)))
        nodes.append(Pos(150, y, T(f'{t["id"]}  {t["label"]}', size=20, color="#F4F7FB", weight="BOLD", family=FONT)))
        nodes.append(Pos(150, y + 25, T(("设计" if team == "design" else "工程") + " · " + ("风险关注" if t["id"] in ("R02", "R05", "R10") else "按计划"),
                                     size=20, color="#F5C451" if t["id"] in ("R02", "R05", "R10") else "#93A6C2", family=FONT)))
    nodes.append(Pos(36, 1108, T("截止 16:00 · 当前排程 13:20 · 余 160 min", size=20, color="#F5C451", family=FONT)))
    nodes.append(Pos(36, 1160, T("R02 限流 · R05 长文案 · R10 回归：按对策保留缓冲，不跳过看图。", size=18, color="#93A6C2", family=FONT), w=648, h=50))
    nodes.append(Pos(36, 1240, T("schedule.json / schedule-audit.json / 三图一致", size=16, color="#6E819B", family=FONT)))
    dsl = f'<Snapshot type="png" background="#0A111D">\n' + Stack(nodes, width=W, height=H) + "\n</Snapshot>\n"
    return dsl, {"canvas": [W, H], "rows": [(t["id"], 160 + i * 76) for i, t in enumerate(tasks)]}


def main() -> int:
    data = load()
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    (TMP / "renders").mkdir(parents=True, exist_ok=True)
    sched = schedule_json(data)
    (TMP / "schedule.json").write_text(json.dumps(sched, ensure_ascii=False, indent=2), encoding="utf-8")
    b, bm = board(data); br, brm = brief(data); a, am = action(data)
    (TMP / "dsl" / f"execution-board-{VERSION}.snapshot").write_text(b, encoding="utf-8")
    (TMP / "dsl" / f"decision-brief-{VERSION}.snapshot").write_text(br, encoding="utf-8")
    (TMP / "dsl" / f"action-card-{VERSION}.snapshot").write_text(a, encoding="utf-8")
    # audit
    checks = []
    for t in data["tasks"]:
        st, en, team = SCHED[t["id"]]
        checks.append({"check": "duration_" + t["id"], "passed": en - st == t["minutes"], "expected": t["minutes"], "actual": en - st})
        checks.append({"check": "window_" + t["id"], "passed": 0 <= st < en <= 420, "start": st, "end": en})
        checks.append({"check": "team_allowed_" + t["id"], "passed": team in t["teams"], "team": team})
        for p in t["depends"]:
            checks.append({"check": f"dep_{p}_{t['id']}", "passed": SCHED[p][1] <= st, "pred_end": SCHED[p][1], "start": st})
    # resource overlaps
    for team in ("design", "engineering"):
        ts = sorted([(SCHED[t["id"]][0], SCHED[t["id"]][1], t["id"]) for t in data["tasks"] if SCHED[t["id"]][2] == team])
        for a1, b1 in zip(ts, ts[1:]):
            checks.append({"check": f"resource_{team}_{a1[2]}_{b1[2]}", "passed": a1[1] <= b1[0], "end": a1[1], "next_start": b1[0]})
    finish = max(v[1] for v in SCHED.values())
    audit = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
             "timezone": "Asia/Shanghai (+08:00)", "checks": checks,
             "lower_bounds": {"critical_path_minutes": 255,
                              "critical_path": ["R01", "R04", "R07", "R09", "R10", "R12"],
                              "critical_path_calc": "25+60+70+45+35+20=255",
                              "work_minutes": 485, "two_team_work_bound": 242.5,
                              "work_calc": "485/2=242.5"},
             "finish": {"finish_minute": finish, "finish": iso(finish), "buffer_minutes": 420 - finish,
                        "buffer": "420−260=160"},
             "optimality": {"feasible": True, "claim": "feasible 260; not proven globally optimal",
                            "gap_to_critical_path": 5,
                            "note": "R05 must be on engineering after R03, pushing R07 5 min; DFS found 260; no exhaustive optimality proof."},
             "schedule_source": "schedule.json"}
    (TMP / "schedule-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    # content map
    cm = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
          "tasks": [], "risks": [], "checks": []}
    for t in data["tasks"]:
        st, en, team = SCHED[t["id"]]
        cm["tasks"].append({"id": t["id"], "label": t["label"], "team": team, "start": hm(st), "end": hm(en),
                            "depends": t["depends"],
                            "board": {"bar": [round(430 + st * (1380 / 420), 2), 0, round(430 + en * (1380 / 420), 2), 0], "row": t["id"]},
                            "brief": {"row": t["id"]}, "action": {"row": t["id"]}})
    for r in data["risks"]:
        cm["risks"].append({"id": r["id"], "task": r["task"], "impact": r["impact"], "mitigation": r["mitigation"],
                            "images": ["execution-board", "decision-brief", "action-card"]})
    cm["checks"] = [{"check": "same_schedule_three_images", "passed": True, "method": "all generated from SCHED dict"},
                    {"check": "timeline_scale", "passed": True, "method": "board x=430+minute*(1380/420), width proportional"},
                    {"check": "task_count", "passed": len(cm["tasks"]) == 12, "count": len(cm["tasks"])},
                    {"check": "risk_count", "passed": len(cm["risks"]) == 3}]
    (TMP / "content-map.json").write_text(json.dumps(cm, ensure_ascii=False, indent=2), encoding="utf-8")
    (TMP / "layout-meta.json").write_text(json.dumps({"board": bm, "brief": brm, "action": am}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("A24", VERSION, "finish", finish, "buffer", 420 - finish, "checks", sum(1 for c in checks if c["passed"]), "/", len(checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
