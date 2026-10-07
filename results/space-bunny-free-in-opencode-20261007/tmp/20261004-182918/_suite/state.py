"""Suite-level progress/checkpoint manager for run 20261004-182918."""
from __future__ import annotations

import json
import os
import shutil
import time
from datetime import datetime, timezone, timedelta

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT_ROOT = os.path.join(ROOT, "outputs", RUN)
TMP_ROOT = os.path.join(ROOT, "tmp", RUN)
SUITE_OUT = os.path.join(OUT_ROOT, "_suite")
SUITE_TMP = os.path.join(TMP_ROOT, "_suite")
STATE_PATH = os.path.join(SUITE_OUT, "suite-state.json")
EVENTS = os.path.join(SUITE_TMP, "events.jsonl")
CKPT_DIR = os.path.join(SUITE_TMP, "checkpoints")
CST = timezone(timedelta(hours=8))

IDS = ["A%02d" % i for i in range(1, 25)] + ["B%02d" % i for i in range(1, 7)]
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
    "B04": "自主研究一个真实主题并制作十件视觉特辑",
    "B05": "从零构想产品并设计十个关键使用画面",
    "B06": "把十个日常信息难题变成惊艳而好用的作品",
}
MIN_PNGS = {"A01": 1, "A02": 2, "A03": 1, "A04": 1, "A05": 1, "A06": 1, "A07": 2,
            "A08": 1, "A09": 1, "A10": 1, "A11": 2, "A12": 4, "A13": 4, "A14": 8,
            "A15": 1, "A16": 1, "A17": 8, "A18": 1, "A19": 3, "A20": 1, "A21": 6,
            "A22": 3, "A23": 7, "A24": 3, "B01": 10, "B02": 10, "B03": 10,
            "B04": 10, "B05": 10, "B06": 10}


def now_iso() -> str:
    return datetime.now(CST).isoformat(timespec="milliseconds")


def load() -> dict:
    with open(STATE_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def save(state: dict) -> None:
    state["updated_at"] = now_iso()
    with open(STATE_PATH, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)


def _lock(timeout=40.0):
    """Cross-process lock so parallel task workers cannot clobber suite-state.json."""
    os.makedirs(SUITE_TMP, exist_ok=True)
    path = os.path.join(SUITE_TMP, "suite-state.lock")
    deadline = time.time() + timeout
    while True:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return path
        except FileExistsError:
            if time.time() > deadline:
                try:
                    os.remove(path)
                except OSError:
                    pass
                continue
            time.sleep(0.15)


def _unlock(path):
    try:
        os.remove(path)
    except OSError:
        pass


def mutate(fn):
    """Run fn(state) under the lock and persist the result."""
    lock = _lock()
    try:
        st = load()
        result = fn(st)
        save(st)
        return result
    finally:
        _unlock(lock)


def init() -> dict:
    if os.path.exists(STATE_PATH):
        return load()
    state = {
        "schema_version": 1,
        "suite_version": "1.0.0",
        "run_id": RUN,
        "profile": "all",
        "status": "in_progress",
        "started_at": now_iso(),
        "updated_at": now_iso(),
        "current_task": None,
        "current_round": None,
        "current_case": None,
        "last_checkpoint": None,
        "notes": "resume_run_id was null in run-config.json, so a fresh run_id was created.",
        "tasks": [
            {"id": t, "title": TITLES[t], "status": "pending", "started_at": None,
             "ended_at": None, "output_dir": os.path.join(OUT_ROOT, t),
             "temp_dir": os.path.join(TMP_ROOT, t),
             "completed_rounds": [], "completed_cases": [], "artifacts": [],
             "visual_review_evidence": [], "unresolved_issues": [],
             "resume_notes": None, "min_final_pngs": MIN_PNGS[t]}
            for t in IDS
        ],
    }
    os.makedirs(CKPT_DIR, exist_ok=True)
    save(state)
    event("suite_initialised", {"run_id": RUN, "profile": "all"})
    return state


def event(kind: str, data: dict) -> None:
    os.makedirs(SUITE_TMP, exist_ok=True)
    with open(EVENTS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": now_iso(), "event": kind, "run_id": RUN,
                             "data": data}, ensure_ascii=False) + "\n")


def task(task_id: str) -> dict:
    for t in load()["tasks"]:
        if t["id"] == task_id:
            return t
    raise KeyError(task_id)


def start_task(task_id: str) -> None:
    def fn(st):
        for t in st["tasks"]:
            if t["id"] == task_id:
                t["status"] = "in_progress"
                t["started_at"] = now_iso()
                t["ended_at"] = None
        st["current_task"] = task_id
        st["current_round"] = None
        st["current_case"] = None
    mutate(fn)
    event("task_started", {"task_id": task_id, "output_dir": os.path.join(OUT_ROOT, task_id)})


def finish_task(task_id: str, status: str, artifacts: list, visual_evidence: list,
                unresolved: list | None = None, rounds: list | None = None,
                cases: list | None = None, notes: str | None = None) -> None:
    def fn(st):
        for t in st["tasks"]:
            if t["id"] == task_id:
                t["status"] = status
                t["ended_at"] = now_iso()
                t["artifacts"] = artifacts
                t["visual_review_evidence"] = visual_evidence
                t["unresolved_issues"] = unresolved or []
                t["completed_rounds"] = rounds or t["completed_rounds"]
                t["completed_cases"] = cases or t["completed_cases"]
                t["resume_notes"] = notes
    mutate(fn)
    event("task_finished", {"task_id": task_id, "status": status,
                            "artifacts": len(artifacts)})
    checkpoint("after-" + task_id)


def set_current(task_id: str | None = None, round_id: str | None = None,
                case: str | None = None) -> None:
    def fn(st):
        st["current_task"] = task_id if task_id is not None else st["current_task"]
        st["current_round"] = round_id
        st["current_case"] = case
    mutate(fn)


def checkpoint(label: str) -> str:
    os.makedirs(CKPT_DIR, exist_ok=True)
    lock = _lock()
    try:
        n = max([int(f[6:12]) for f in os.listdir(CKPT_DIR)
                 if f.startswith("state-") and f.endswith(".json")] or [0]) + 1
        name = "state-%06d.json" % n
        st = load()
        st["last_checkpoint"] = name
        save(st)
        with open(os.path.join(CKPT_DIR, name), "w", encoding="utf-8") as fh:
            json.dump(st, fh, ensure_ascii=False, indent=2)
    finally:
        _unlock(lock)
    event("checkpoint", {"name": name, "label": label})
    return name


if __name__ == "__main__":
    init()
    print("state ready:", STATE_PATH)