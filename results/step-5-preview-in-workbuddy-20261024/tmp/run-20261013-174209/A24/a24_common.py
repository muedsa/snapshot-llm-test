#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A24 · 共用数据与 DSL 助手。

数据来源：
  - tasks/A24-release-plan-capstone/inputs/release.json（题面输入，只读）
  - tmp/<run_id>/A24/optimal-schedules.json（a24_solve.py 穷举 + a24_enum.py 挑选）
三张图与三份 JSON 全部由本模块的同一份排程生成，保证不互相矛盾。
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN_ID = "run-20261013-174209"
TASK = "A24"
TMP = ROOT / "tmp" / RUN_ID / TASK
OUT = ROOT / "outputs" / RUN_ID / TASK
TASK_DIR = ROOT / "tasks" / "A24-release-plan-capstone"

TZ = dt.timezone(dt.timedelta(hours=8))
DAY = dt.date(2026, 11, 7)
BASE = dt.datetime(2026, 11, 7, 9, 0, 0, tzinfo=TZ)
WINDOW = 420
DEADLINE_MIN = 420
MAKESPAN = 260
BUFFER = 160
TOTAL_MINUTES = 485
CP_MINUTES = 255
CP_PATH = ["R01", "R04", "R07", "R09", "R10", "R12"]
WL_BOUND = 242.5

BRAND = "叠光 · 发布演练"
TITLE_BOARD = "发布作战执行图"
TITLE_BRIEF = "发布日决策简报"
TITLE_CARD = "发布日行动卡"
DATE_LINE = "2026-11-07（周六） · 09:00–16:00（+08:00）"

# ------------------------------------------------------------------ 排程数据
def release() -> dict:
    return json.loads((TASK_DIR / "inputs" / "release.json").read_text(encoding="utf-8"))


def selected() -> list[dict]:
    data = json.loads((TMP / "optimal-schedules.json").read_text(encoding="utf-8"))
    return data["selected"]


def floats() -> dict:
    data = json.loads((TMP / "optimal-schedules.json").read_text(encoding="utf-8"))
    return data["selected_floats"]


def tasks() -> list[dict]:
    return release()["tasks"]


def task_map() -> dict:
    return {t["id"]: t for t in tasks()}


def sched_map() -> dict:
    return {r["id"]: r for r in selected()}


def hhmm(minute: int) -> str:
    t = BASE + dt.timedelta(minutes=minute)
    return t.strftime("%H:%M")


def iso(minute: int) -> str:
    t = BASE + dt.timedelta(minutes=minute)
    return t.isoformat(timespec="seconds")


def team_of(tid: str) -> str:
    return sched_map()[tid]["team"]


TEAM_CN = {"design": "设计团队", "engineering": "工程团队"}

# ------------------------------------------------------------------ 配色
BG = "#F6F7FB"
PANEL = "#FFFFFF"
BORDER = "#E2E8F0"
GRID = "#E7ECF4"
GRID_MINOR = "#F0F4F9"
INK = "#0F172A"
INK2 = "#334155"
MUTED = "#5B6B84"
FAINT = "#8A99B0"
IDLE = "#EDF1F8"
DESIGN = "#4F46E5"
DESIGN_L = "#EEF2FF"
DESIGN_B = "#C7D2FE"
ENG = "#0F766E"
ENG_L = "#EFFCF9"
ENG_B = "#9BE3D8"
DEAD = "#DC2626"
DEAD_L = "#FEF2F2"
DONE = "#059669"
DONE_L = "#ECFDF5"
AMBER = "#B45309"
AMBER_L = "#FFFBEB"
AMBER_B = "#FCD34D"

TEAM_COLOR = {"design": DESIGN, "engineering": ENG}
TEAM_LIGHT = {"design": DESIGN_L, "engineering": ENG_L}
TEAM_BORDER = {"design": DESIGN_B, "engineering": ENG_B}

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

# ------------------------------------------------------------------ DSL 助手
def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_w(s: str, size: float) -> float:
    """文本宽度估计（CJK 1.0em、ASCII 0.56em、空格 0.32em），用于排版预算。"""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F:
            w += 1.0
        elif ch == " ":
            w += 0.32
        elif ch in "·—–":
            w += 0.6
        else:
            w += 0.56
    return w * size


def wrap(s: str, size: float, max_w: float) -> list[str]:
    """按估算宽度做中文/英文混排折行（不断词：CJK 任意处可断）。"""
    lines, cur, cur_w = [], "", 0.0
    for ch in s:
        cw = text_w(ch, size)
        if cur and cur_w + cw > max_w:
            lines.append(cur)
            cur, cur_w = ch, cw
        else:
            cur += ch
            cur_w += cw
    if cur:
        lines.append(cur)
    return lines


def text_node(s: str, left: float, top: float, w: float, h: float, size: float,
              color: str, align: str = "LEFT", style: str = "NORMAL",
              family: str = SANS) -> str:
    return (f'<Positioned left="{left:.2f}" top="{top:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}"><Container color="transparent">'
            f'<Text fontSize="{size}" fontFamily="{family}" fontStyle="{style}" '
            f'color="{color}" textAlign="{align}" softWrap="false" maxLines="1">'
            f'{esc(s)}</Text></Container></Positioned>')


def rect(left: float, top: float, w: float, h: float, color: str,
         radius: float = 0.0) -> str:
    br = f' borderRadius="{radius:.2f}"' if radius else ""
    return (f'<Positioned left="{left:.2f}" top="{top:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}"><Container width="{w:.2f}" height="{h:.2f}" '
            f'color="{color}"{br}/></Positioned>')


def hline(x: float, y: float, w: float, color: str, thick: float = 1.5) -> str:
    return rect(x, y, w, thick, color)


def vline(x: float, y: float, h: float, color: str, thick: float = 1.5) -> str:
    return rect(x, y, thick, h, color)


def snapshot(w: int, h: int, nodes: list[str], bg: str = BG) -> str:
    head = (f'<Snapshot type="png" background="{bg}">\n'
            f'<Container width="{w}" height="{h}">\n'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">\n')
    return head + "\n".join(nodes) + "\n</Stack>\n</Container>\n</Snapshot>\n"


def dep_text(tid: str) -> str:
    t = task_map()[tid]
    if not t["depends"]:
        return "无先决"
    return "依赖 " + " · ".join(t["depends"])
