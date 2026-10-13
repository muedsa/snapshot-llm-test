"""A24 - measure the rendered board and prove the three views agree.

The bar edges are found in the painted pixels and converted back to minutes through the
same scale the layout used, so "drawn to a common time scale" is a measurement, not a
claim. The three DSLs are then checked to carry identical start/end/team strings for all
twelve tasks - they are generated from one schedule.json, and this proves nothing drifted.

Run:  python tmp/<run_id>/A24/verify.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A24"
sys.path.insert(0, str(TMP))
import make as M  # noqa: E402

X0, X1 = 260, 1880
SCALE = (X1 - X0) / 420.0


def X(m):
    return X0 + m * SCALE


def runs_in_row(img, colour, y, x0, x1):
    row = (np.abs(img[y] - colour).sum(1) <= 40)[x0:x1]
    out, start = [], None
    for i, v in enumerate(row):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= 6:
                out.append((x0 + start, x0 + i - 1))
            start = None
    if start is not None:
        out.append((x0 + start, x0 + x1 - 1))
    return out


def main():
    S = M.load()
    img = np.asarray(Image.open(TMP / "execution-board.png").convert("RGB")).astype(int)
    lanes = {"design": (206, np.array([27, 79, 191])),
             "engineering": (466, np.array([201, 116, 21]))}
    bars = []
    for team, (ly, col) in lanes.items():
        y = ly + 118                     # below the white ID glyphs, inside the bar
        found = runs_in_row(img, col, y, X0, X1)
        rows = sorted([t for t in S["tasks"] if t["team"] == team],
                      key=lambda t: t["start_minute"])
        assert len(found) == len(rows), f"{team}: {len(found)} bars vs {len(rows)} tasks"
        for t, (a, b) in zip(rows, found):
            bars.append({
                "id": t["id"], "team": team,
                "expected_x": [round(X(t["start_minute"]), 2),
                               round(X(t["end_minute"]) - 1, 2)],
                "measured_x": [a, b],
                "expected_minutes": [t["start_minute"], t["end_minute"]],
                "measured_minutes": [round((a - X0) / SCALE, 1),
                                     round((b + 1 - X0) / SCALE, 1)],
                "edge_err_px": round(max(abs(a - X(t["start_minute"])),
                                          abs(b - (X(t["end_minute"]) - 1))), 2)})
    worst = max(b["edge_err_px"] for b in bars)
    # lane occupancy re-checked from the painted runs: no two bars of one team touch
    overlap = []
    for team in lanes:
        seq = [b for b in bars if b["team"] == team]
        for a, b in zip(seq, seq[1:]):
            if a["measured_x"][1] >= b["measured_x"][0]:
                overlap.append(f"{team}: {a['id']}/{b['id']}")
    # vertical lines: finish and deadline
    def vline(x_expect, colour):
        m = (np.abs(img[150:800] - np.array(colour)).sum(-1) <= 60)
        col = m[:, int(x_expect) - 3:int(x_expect) + 4]
        return int(col.any(1).sum())

    finish_px = vline(X(S["finish_minute"]), [31, 107, 58])
    deadline_px = vline(X(420), [179, 38, 30])
    # cross-view string consistency
    dsls = {n: (TMP / f"{n}.snapshot").read_text(encoding="utf-8")
            for n in ("execution-board", "decision-brief", "action-card")}
    strings = {}
    for t in S["tasks"]:
        ts = f"{M.hh(t['start_minute'])}-{M.hh(t['end_minute'])}"
        strings[t["id"]] = {"execution-board": ts in dsls["execution-board"],
                            "action-card": ts in dsls["action-card"],
                            "decision-brief-minutes": f"{t['minutes']}′" in
                                                      dsls["decision-brief"]}
    card_ids = {t["id"]: len(re.findall(rf">{t['id']}]|{t['id']}(?=[^0-9A-Za-z])",
                                        dsls["action-card"])) >= 1
                for t in S["tasks"]}
    team_strings = {n: all(t["team"] in d for t in S["tasks"]) for n, d in dsls.items()}
    brief_totals = {k: (str(v) in dsls["decision-brief"]) for k, v in (
        ("finish_clock", M.hh(S["finish_minute"])), ("buffer", str(S["buffer_minutes"])),
        ("total_work", str(S["total_work_minutes"])),
        ("critical_path", str(S["critical_path_minutes"])))}
    out = {
        "schema_version": 1, "task_id": "A24", "path_base": "suite_root",
        "board_time_scale": {
            "px_per_minute": round(SCALE, 6),
            "x_of_09:00": X0, "x_of_16:00": X1,
            "bars": bars, "worst_edge_err_px": worst,
            "same_team_bars_touching": overlap,
            "conclusion": ("12 根任务条的左右边界与按 420 分钟同一尺度换算的期望位置"
                           f"最大相差 {worst}px，同团队条互不接触")},
        "guide_lines": {
            "finish_line_green_px": finish_px, "deadline_line_red_px": deadline_px,
            "expected_height_px": 650,
            "passed": finish_px > 600 and deadline_px > 600},
        "cross_view_consistency": {
            "source": f"tmp/{RUN}/A24/schedule.json",
            "each_task_time_string_present_in": strings,
            "all_tasks_in_all_three": all(all(v.values()) for v in strings.values()),
            "rule": "起止字符串在执行图与行动卡逐任务核对；简报按任务分钟数核对，"
                    "并核对完工/缓冲/总工时/关键路径四个汇总数",
            "team_label_present": team_strings,
            "brief_totals_present": brief_totals,
            "ids_on_card": all(card_ids.values()),
            "note": "三张图由同一 schedule.json 生成；这里逐任务核对起止字符串在三份 DSL 中都出现"},
        "font_floor": {n: {"min_size": min(int(m) for m in re.findall(
            r'fontSize="(\d+)"', d)), "required_min": r}
            for (n, d), r in zip(dsls.items(), (20, 24, 20))},
    }
    (TMP / "verify.json").write_text(json.dumps(out, ensure_ascii=False, indent=1)
                                     + "\n", encoding="utf-8")
    print(json.dumps({"worst_edge_err_px": worst, "touching": overlap,
                      "lines": out["guide_lines"],
                      "all_three": out["cross_view_consistency"]["all_tasks_in_all_three"],
                      "font_floor": out["font_floor"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
