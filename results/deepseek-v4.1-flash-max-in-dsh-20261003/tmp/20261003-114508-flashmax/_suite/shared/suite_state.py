"""Suite progress bookkeeping: suite-state.json + events.jsonl + numbered checkpoints.

Usage:
    python suite_state.py init
    python suite_state.py start A02 --temp-dir tmp/.../A02 --output-dir outputs/.../A02
    python suite_state.py update A02 --status in_progress --current-round round-01 ...
    python suite_state.py done A02 --artifacts a.png,b.snapshot --evidence "viewed final png"
    python suite_state.py checkpoint
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from suite_common import (ROOT, RUN_ID, OUT_ROOT, TMP_ROOT, SUITE_OUT, SUITE_TMP,  # noqa: E402
                          now, write_json, append_jsonl_nobom, read_jsonl)

STATE = os.path.join(SUITE_OUT, "suite-state.json")
EVENTS = os.path.join(SUITE_TMP, "events.jsonl")
CKPT = os.path.join(SUITE_TMP, "checkpoints")

TASK_ORDER = ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10",
              "A11", "A12", "A13", "A14", "A15", "A16", "A17", "A18", "A19", "A20",
              "A21", "A22", "A23", "A24", "B01", "B02", "B03", "B04", "B05", "B06"]
TITLES = {
    "A01": "六个月经营诊断驾驶舱", "A02": "三会场密集会议日程", "A03": "多层语义故障恢复",
    "A04": "分组改善与总体下降的数据解释", "A05": "不规则采样与缺测的仪表报告",
    "A06": "十四节点依赖图与反馈回路", "A07": "三线换乘图与路线核验",
    "A08": "网格导览与两条可走路线", "A09": "十二个非对称图形变换标本",
    "A10": "透明合成与滤镜语义实验板", "A11": "文字保真与跨页结算单",
    "A12": "四断点完整内容视觉系统", "A13": "品牌标志到完整活动应用",
    "A14": "八组文案压力测试与批量生成", "A15": "复杂界面视觉复刻",
    "A16": "从错误图表恢复可信叙事", "A17": "四页可实践的DSL入门手册",
    "A18": "守恒对象的三幕视觉叙事", "A19": "构造可核验的视觉题场",
    "A20": "二十四密集点的无重叠标注", "A21": "真实需求变更：双尺寸发布物",
    "A22": "真实数据更正与局部回归", "A23": "格式边界下的动画分镜交付",
    "A24": "双团队约束下的发布作战计划", "B01": "十张真实场景的炫酷用例",
    "B02": "为一个自选项目设计完整视觉生态", "B03": "用十件作品探索DSL的创意边界",
    "B04": "自主研究一个真实主题并制作十件视觉特辑", "B05": "从零构想产品并设计十个关键使用画面",
    "B06": "把十个日常信息难题变成惊艳而好用的作品",
}
TRACK = {t: ("creative" if t.startswith("B") else "advanced") for t in TASK_ORDER}
MIN_PNG = {"A01": 1, "A02": 2, "A03": 1, "A04": 1, "A05": 1, "A06": 1, "A07": 2, "A08": 1,
           "A09": 1, "A10": 1, "A11": 2, "A12": 4, "A13": 4, "A14": 8, "A15": 1, "A16": 1,
           "A17": 8, "A18": 1, "A19": 3, "A20": 1, "A21": 6, "A22": 3, "A23": 7, "A24": 3,
           "B01": 10, "B02": 10, "B03": 10, "B04": 10, "B05": 10, "B06": 10}
ROUNDS = {"A21": 3, "A22": 3}


def blank_task(tid: str) -> dict:
    return {
        "id": tid, "title": TITLES[tid], "track": TRACK[tid],
        "status": "pending", "started_at": None, "ended_at": None,
        "output_dir": os.path.relpath(os.path.join(OUT_ROOT, tid), ROOT),
        "temp_dir": os.path.relpath(os.path.join(TMP_ROOT, tid), ROOT),
        "round_count": ROUNDS.get(tid, 1),
        "minimum_final_pngs": MIN_PNG[tid],
        "completed_rounds": [], "completed_cases": [],
        "artifacts": [], "visual_review_evidence": [],
        "unresolved_issues": [], "resume_notes": None,
    }


def load() -> dict:
    if os.path.exists(STATE):
        return json.load(open(STATE, encoding="utf-8"))
    raise SystemExit("suite-state.json missing; run init")


def save(st: dict) -> None:
    st["updated_at"] = now()
    write_json(STATE, st)


def event(kind: str, **kw) -> None:
    append_jsonl_nobom(EVENTS, dict(at=now(), run_id=RUN_ID, kind=kind, **kw))


def cmd_init() -> None:
    os.makedirs(SUITE_OUT, exist_ok=True)
    os.makedirs(CKPT, exist_ok=True)
    st = {
        "schema_version": 1, "suite_version": "1.0.0", "run_id": RUN_ID,
        "profile": "all", "status": "in_progress",
        "started_at": now(), "updated_at": now(),
        "current_task": None, "current_round": None, "current_case": None,
        "last_checkpoint": None,
        "task_count": len(TASK_ORDER), "minimum_final_pngs": 124,
        "output_root": os.path.relpath(OUT_ROOT, ROOT),
        "temp_root": os.path.relpath(TMP_ROOT, ROOT),
        "tasks": [blank_task(t) for t in TASK_ORDER],
    }
    save(st)
    event("suite_init", output_root=st["output_root"], temp_root=st["temp_root"])
    print("initialised", STATE)


def find(st: dict, tid: str) -> dict:
    for t in st["tasks"]:
        if t["id"] == tid:
            return t
    raise SystemExit(f"unknown task {tid}")


def cmd_start(a) -> None:
    st = load()
    t = find(st, a.task)
    t["status"] = "in_progress"
    t["started_at"] = t["started_at"] or now()
    if a.temp_dir:
        t["temp_dir"] = a.temp_dir
    if a.output_dir:
        t["output_dir"] = a.output_dir
    st["current_task"] = a.task
    st["current_round"] = None
    st["current_case"] = None
    save(st)
    event("task_start", task_id=a.task, title=t["title"])
    print("started", a.task)


def cmd_update(a) -> None:
    st = load()
    t = find(st, a.task)
    if a.status:
        t["status"] = a.status
    if a.current_round:
        st["current_round"] = a.current_round
    if a.current_case:
        st["current_case"] = a.current_case
    if a.add_round and a.add_round not in t["completed_rounds"]:
        t["completed_rounds"].append(a.add_round)
    if a.add_case and a.add_case not in t["completed_cases"]:
        t["completed_cases"].append(a.add_case)
    if a.artifact:
        for x in a.artifact.split(","):
            x = x.strip()
            if x and x not in t["artifacts"]:
                t["artifacts"].append(x)
    if a.evidence:
        t["visual_review_evidence"].append({"at": now(), "evidence": a.evidence})
    if a.issue:
        t["unresolved_issues"].append(a.issue)
    if a.resume_notes:
        t["resume_notes"] = a.resume_notes
    st["current_task"] = a.task if t["status"] == "in_progress" else st.get("current_task")
    save(st)
    event("task_update", task_id=a.task, status=t["status"],
          current_round=st.get("current_round"), current_case=st.get("current_case"))
    print("updated", a.task, t["status"])


def cmd_done(a) -> None:
    st = load()
    t = find(st, a.task)
    t["status"] = a.status
    t["ended_at"] = now()
    if a.artifact:
        for x in a.artifact.split(","):
            x = x.strip()
            if x and x not in t["artifacts"]:
                t["artifacts"].append(x)
    if a.evidence:
        t["visual_review_evidence"].append({"at": now(), "evidence": a.evidence})
    if a.issue:
        t["unresolved_issues"].append(a.issue)
    if a.resume_notes:
        t["resume_notes"] = a.resume_notes
    st["current_task"] = None
    st["current_round"] = None
    st["current_case"] = None
    done = [x for x in st["tasks"] if x["status"] == "completed"]
    st["status"] = "completed" if len(done) == len(st["tasks"]) else "in_progress"
    save(st)
    event("task_done", task_id=a.task, status=a.status,
          completed=len(done), total=len(st["tasks"]))
    cmd_checkpoint(silent=True)
    print("done", a.task, a.status, f"{len(done)}/{len(st['tasks'])}")


def cmd_checkpoint(silent: bool = False) -> None:
    os.makedirs(CKPT, exist_ok=True)
    n = len([f for f in os.listdir(CKPT) if f.startswith("state-")]) + 1
    st = load()
    st["last_checkpoint"] = f"checkpoints/state-{n:06d}.json"
    write_json(STATE, st)
    dst = os.path.join(CKPT, f"state-{n:06d}.json")
    shutil.copyfile(STATE, dst)
    event("checkpoint", file=os.path.relpath(dst, ROOT))
    if not silent:
        print("checkpoint", dst)


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    s = sub.add_parser("start")
    s.add_argument("task")
    s.add_argument("--temp-dir"); s.add_argument("--output-dir")
    u = sub.add_parser("update")
    u.add_argument("task")
    u.add_argument("--status"); u.add_argument("--current-round"); u.add_argument("--current-case")
    u.add_argument("--add-round"); u.add_argument("--add-case")
    u.add_argument("--artifact"); u.add_argument("--evidence"); u.add_argument("--issue")
    u.add_argument("--resume-notes")
    d = sub.add_parser("done")
    d.add_argument("task")
    d.add_argument("--status", default="completed")
    d.add_argument("--artifact"); d.add_argument("--evidence"); d.add_argument("--issue")
    d.add_argument("--resume-notes")
    sub.add_parser("checkpoint")
    a = ap.parse_args()
    if a.cmd == "init":
        cmd_init()
    elif a.cmd == "start":
        cmd_start(a)
    elif a.cmd == "update":
        cmd_update(a)
    elif a.cmd == "done":
        cmd_done(a)
    elif a.cmd == "checkpoint":
        cmd_checkpoint()


if __name__ == "__main__":
    main()
