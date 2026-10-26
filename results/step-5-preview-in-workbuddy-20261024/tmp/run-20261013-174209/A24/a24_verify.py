#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A24 · 三图复测：DSL 层（字号下限、文本一致性）+ 像素层（任务块几何/时间比例/线条）。

执行图：泳道任务块按团队色检测，左右边界换算分钟与 schedule.json 比对；
简报：DAG 节点填充色 + 迷你甘特条带；行动卡：行卡团队色条。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import a24_common as C  # noqa: E402

ROOT = C.ROOT
OUT = C.OUT
S = C.sched_map()
TM = C.task_map()
REL = C.release()

HEX = {
    "DESIGN": C.DESIGN, "ENG": C.ENG, "DEAD": C.DEAD, "DONE": C.DONE,
    "DESIGN_L": C.DESIGN_L, "ENG_L": C.ENG_L, "IDLE": C.IDLE,
}


def rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def load(name: str) -> np.ndarray:
    return np.array(Image.open(OUT / f"{name}.png").convert("RGB")).astype(int)


def color_runs(row: np.ndarray, target: tuple[int, int, int],
               tol: int = 6) -> list[tuple[int, int]]:
    """一行中与 target 颜色相近（tol）的连续区间 [start, end)。"""
    m = (np.abs(row - np.array(target)).max(axis=1) <= tol)
    runs, s = [], None
    for i, v in enumerate(m):
        if v and s is None:
            s = i
        elif not v and s is not None:
            runs.append((s, i))
            s = None
    if s is not None:
        runs.append((s, len(m)))
    return runs


def longest_run(row: np.ndarray, target, tol: int = 6):
    runs = color_runs(row, target, tol)
    if not runs:
        return None
    return max(runs, key=lambda r: r[1] - r[0])


# --------------------------------------------------------------- DSL 层
def dsl_layer() -> list[dict]:
    problems: list[dict] = []
    # 1. 尺寸与字号下限
    req = {"execution-board": (1920, 1080, 20),
           "decision-brief": (1200, 1600, 24),
           "action-card": (720, 1280, 20)}
    for name, (w, h, minpx) in req.items():
        dsl = (OUT / f"{name}.snapshot").read_text(encoding="utf-8")
        sizes = [float(x) for x in re.findall(r'fontSize="([\d.]+)"', dsl)]
        if not sizes:
            problems.append({"check": f"{name}-fonts", "issue": "无 Text 节点"})
            continue
        mn = min(sizes)
        if mn < minpx - 1e-9:
            problems.append({"check": f"{name}-fonts",
                             "issue": f"最小字号 {mn} < {minpx}",
                             "sizes": sorted(set(sizes))})
        # 快照根尺寸
        m = re.search(r'<Container width="(\d+)" height="(\d+)">', dsl)
        if not m or (int(m.group(1)), int(m.group(2))) != (w, h):
            problems.append({"check": f"{name}-size",
                             "issue": f"DSL 根尺寸 {m.groups() if m else None}"
                                      f" ≠ {(w, h)}"})
    # 2. 三图关键文案一致
    keys = ["叠光 · 发布演练", "13:20", "160 分钟", "2026-11-07"]
    texts = {n: (OUT / f"{n}.snapshot").read_text(encoding="utf-8")
             for n in req}
    for k in keys:
        for n, t in texts.items():
            if k not in t:
                problems.append({"check": f"{n}-text", "issue": f"缺少关键文案 {k!r}"})
    # 3. 三图排程一致：每张图出现的 "HH:MM–HH:MM" 起止对均能在 schedule.json
    #    找到，或是同团队空档（页脚说明文字中的衔接等待）
    pat = re.compile(r"(\d{2}:\d{2})–(\d{2}:\d{2})")
    valid = {(C.hhmm(r["start_minute"]), C.hhmm(r["end_minute"])) for r in S.values()}
    gaps = set()
    for team in ("design", "engineering"):
        iv = sorted((S[t]["start_minute"], S[t]["end_minute"]) for t in TM
                    if S[t]["team"] == team)
        prev = 0
        for s, e in iv:
            if s > prev:
                gaps.add((C.hhmm(prev), C.hhmm(s)))
            prev = max(prev, e)
        if prev < C.WINDOW:
            gaps.add((C.hhmm(prev), C.hhmm(C.WINDOW)))
    allowed = valid | gaps | {("09:00", "16:00")}
    for n, t in texts.items():
        for a, b in set(pat.findall(t)):
            if (a, b) not in allowed:
                problems.append({"check": f"{n}-schedule",
                                 "issue": f"时间对 {a}–{b} 不在排程或空档中"})
    return problems


def line_visible(im: np.ndarray, x: float, y: int, colr: str,
                 tol: int = 40) -> bool:
    """在 (x±1, y) 窗口内是否存在与 colr 相近的像素（抗锯齿边缘容忍）。"""
    t = np.array(rgb(colr))
    xi = int(round(x))
    for dx in (-1, 0, 1):
        if xi + dx < 0 or xi + dx >= im.shape[1]:
            continue
        if np.abs(im[y, xi + dx] - t).max() <= tol:
            return True
    return False


# --------------------------------------------------------------- 执行图
BX0, BX1 = 310.0, 1868.0
BS = (BX1 - BX0) / C.WINDOW
LANES = {"design": 218.0, "engineering": 490.0}
BAR_H = 64.0


def bx(m: float) -> float:
    return BX0 + m * BS


def board_layer() -> list[dict]:
    problems: list[dict] = []
    im = load("execution-board")
    if im.shape[:2] != (1080, 1920):
        problems.append({"check": "board-dims",
                         "issue": f"实际尺寸 {im.shape[:2]}"})
        return problems
    # 任务块几何
    for team, ly in LANES.items():
        bar_y = ly + 112
        row = im[int(bar_y + 5)]
        tcol = rgb(HEX["DESIGN"] if team == "design" else HEX["ENG"])
        run = longest_run(row, tcol)
        if run is None:
            problems.append({"check": f"board-bar-{team}",
                             "issue": "未检测到任务块颜色"})
            continue
        # 逐任务：以期望中心定位，向两侧扩展到颜色边界
        for tid in sorted(TM, key=lambda t: S[t]["start_minute"]):
            r = S[tid]
            if r["team"] != team:
                continue
            cx = int(round(bx((r["start_minute"] + r["end_minute"]) / 2)))
            # 从中心向左/右找颜色边界
            yy = int(bar_y + 5)
            x = cx
            while x > 0 and np.abs(im[yy, x] - np.array(tcol)).max() <= 6:
                x -= 1
            left = x + 1
            x = cx
            while x < im.shape[1] - 1 and \
                    np.abs(im[yy, x] - np.array(tcol)).max() <= 6:
                x += 1
            right = x
            exp_l, exp_r = bx(r["start_minute"]), bx(r["end_minute"])
            tol = 3.0
            if abs(left - exp_l) > tol or abs(right - exp_r) > tol:
                problems.append({
                    "check": f"board-bar-{tid}",
                    "issue": f"块边界 [{left},{right}] 期望 "
                             f"[{exp_l:.1f},{exp_r:.1f}]",
                    "minutes_measured": ((left - BX0) / BS, (right - BX0) / BS),
                    "minutes_expected": (r["start_minute"], r["end_minute"])})
            # 块高：中心列垂直范围
            col = im[int(ly + 10):int(ly + 250), cx]
            idx = np.where(np.abs(col - np.array(tcol)).max(axis=1) <= 6)[0]
            if len(idx) and (abs((idx.max() - idx.min() + 1) - BAR_H) > 3):
                problems.append({"check": f"board-barh-{tid}",
                                 "issue": f"块高 {idx.max()-idx.min()+1} ≠ {BAR_H}"})
    # 完工线 / 截止线（跨泳道可见；采样点避开任务块与圆角）
    for name, x, colr in (("finish", bx(C.MAKESPAN), HEX["DONE"]),
                          ("deadline", BX1, HEX["DEAD"])):
        for y in (300, 600):
            if not line_visible(im, x, y, colr):
                problems.append({"check": f"board-line-{name}",
                                 "issue": f"x={x:.1f},y={y} 处无 {colr} 线"})
    # 空档：design 260-420、engineering 235-420 为 IDLE 色
    for team, gs in (("design", 300.0), ("engineering", 300.0)):
        ly = LANES[team]
        px = im[int(ly + 150), int(round(bx(gs)))]
        if np.abs(px - np.array(rgb(HEX["IDLE"]))).max() > 10:
            problems.append({"check": f"board-idle-{team}",
                             "issue": f"空档区颜色 {px.tolist()} 非 IDLE"})
    return problems


# --------------------------------------------------------------- 简报
MX0, MX1 = 216.0, 1152.0
MS = (MX1 - MX0) / C.WINDOW
GANTT_ROWS = {"design": 816.0, "engineering": 858.0}


def mx(m: float) -> float:
    return MX0 + m * MS


def brief_layer() -> list[dict]:
    problems: list[dict] = []
    im = load("decision-brief")
    if im.shape[:2] != (1600, 1200):
        problems.append({"check": "brief-dims", "issue": f"{im.shape[:2]}"})
        return problems
    # DAG 节点：期望中心点应为团队浅色填充
    layers = [["R01", "R02"], ["R04", "R05", "R03"], ["R07", "R06"],
              ["R09", "R08"], ["R10", "R11"], ["R12"]]
    col_x = [48.0, 408.0, 768.0]
    for li, layer in enumerate(layers):
        for ci, tid in enumerate(layer):
            y = 386.0 + li * 60.0
            x = col_x[ci]
            team = S[tid]["team"]
            fill = rgb(HEX["DESIGN_L"] if team == "design" else HEX["ENG_L"])
            px = im[int(y + 23), int(x + 300)]   # 节点右侧（避开文字与色条）
            if np.abs(px - np.array(fill)).max() > 10:
                problems.append({"check": f"brief-dag-{tid}",
                                 "issue": f"节点填充 {px.tolist()} 非 {fill}"})
    # 迷你甘特条带
    for team, ly in GANTT_ROWS.items():
        yy = int(ly + 33)
        tcol = rgb(HEX["DESIGN"] if team == "design" else HEX["ENG"])
        for tid in sorted(TM, key=lambda t: S[t]["start_minute"]):
            r = S[tid]
            if r["team"] != team:
                continue
            cx = int(mx((r["start_minute"] + r["end_minute"]) / 2))
            x = cx
            while x > 0 and np.abs(im[yy, x] - np.array(tcol)).max() <= 6:
                x -= 1
            left = x + 1
            x = cx
            while x < 1199 and np.abs(im[yy, x] - np.array(tcol)).max() <= 6:
                x += 1
            right = x
            exp_l, exp_r = mx(r["start_minute"]), mx(r["end_minute"])
            exp_c = (exp_l + exp_r) / 2
            exp_w = exp_r - exp_l
            meas_c = (left + right) / 2
            meas_w = right - left
            # 圆角半径 8 在扫描行（距底 3px）内缩约 1.8px/侧，另计抗锯齿
            if abs(meas_c - exp_c) > 2.5 or meas_w > exp_w + 2.5 \
                    or meas_w < exp_w - 7.0:
                problems.append({
                    "check": f"brief-gantt-{tid}",
                    "issue": f"中心 {meas_c:.1f}≠{exp_c:.1f}，"
                             f"宽 {meas_w:.1f}≠{exp_w:.1f}",
                    "minutes_measured": ((left - MX0) / MS, (right - MX0) / MS),
                    "minutes_expected": (r["start_minute"], r["end_minute"])})
    # 完工/截止线（采样点位于完工后空档区，避开条带与圆角）
    for name, x, colr in (("finish", mx(C.MAKESPAN), HEX["DONE"]),
                          ("deadline", MX1, HEX["DEAD"])):
        if not line_visible(im, x, 870, colr, tol=60):
            problems.append({"check": f"brief-line-{name}",
                             "issue": f"x={x:.1f} 处无 {colr} 线"})
    return problems


# --------------------------------------------------------------- 行动卡
def card_layer() -> list[dict]:
    problems: list[dict] = []
    im = load("action-card")
    if im.shape[:2] != (1280, 720):
        problems.append({"check": "card-dims", "issue": f"{im.shape[:2]}"})
        return problems
    order = sorted(TM, key=lambda t: (S[t]["start_minute"], t))
    risk_of = {"R02": "K1", "R05": "K2", "R10": "K3"}
    y = 224.0
    for tid in order:
        r = S[tid]
        h = 94.0 if tid in risk_of else 70.0
        team = r["team"]
        tcol = rgb(HEX["DESIGN"] if team == "design" else HEX["ENG"])
        px = im[int(y + h / 2), 27]
        if np.abs(px - np.array(tcol)).max() > 10:
            problems.append({"check": f"card-bar-{tid}",
                             "issue": f"团队色条 {px.tolist()} 非 {tcol}"})
        y += h + 6
    if y > 1240:
        problems.append({"check": "card-overflow",
                         "issue": f"行卡累计高度 {y} 超过页脚位置 1240"})
    return problems


def main() -> None:
    allp = {"dsl": dsl_layer(), "board": board_layer(),
            "brief": brief_layer(), "card": card_layer()}
    total = sum(len(v) for v in allp.values())
    for k, v in allp.items():
        print(f"[{k}] problems={len(v)}")
        for p in v:
            print("   ", json.dumps(p, ensure_ascii=False))
    (C.TMP / "verify-result.json").write_text(
        json.dumps({"problems": allp, "total": total},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print("TOTAL problems:", total)
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
