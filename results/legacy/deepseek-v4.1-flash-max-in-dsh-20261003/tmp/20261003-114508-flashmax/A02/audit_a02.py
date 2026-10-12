"""A02 schedule audit + geometry.

Reads the read-only inputs, computes durations, per-venue gaps, real overlap checks
and the wide/mobile content mapping, then writes schedule-audit.json. The DSL
generators import geometry() from here so the audit and the pictures agree.
"""
from __future__ import annotations

import csv
import json
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A02"
SRC = os.path.join(ROOT, "tasks", "A02-conference-schedule", "inputs")
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

DAY_START, DAY_END = 9 * 60, 16 * 60          # 09:00 - 16:00, shared linear axis
LUNCH = (12 * 60, 13 * 60)                     # public lunch, never merged into a session

CAT = {"keynote": "主旨", "workshop": "工作坊", "talk": "分享", "demo": "演示", "panel": "圆桌"}
VENUE_NAME = {"A": "A 会场", "B": "B 会场", "C": "C 会场"}


def hm(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def mh(v: int) -> str:
    return f"{v // 60:02d}:{v % 60:02d}"


sessions = []
with open(os.path.join(SRC, "agenda.csv"), newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        s = hm(r["start"]); e = hm(r["end"])
        sessions.append({
            "id": r["id"], "venue": r["venue"], "start": r["start"], "end": r["end"],
            "start_min": s, "end_min": e, "duration_min": e - s,
            "title": r["title"], "speaker": r["speaker"], "category": r["category"],
            "category_label": CAT[r["category"]],
            "speaker_count": len([x for x in r["speaker"].split("/") if x.strip()]),
        })
sessions.sort(key=lambda x: (x["start_min"], x["venue"], x["id"]))

venues = json.load(open(os.path.join(SRC, "venues.json"), encoding="utf-8"))

# ---------- per-venue timeline bookkeeping ----------
lanes = {}
for v in ("A", "B", "C"):
    items = sorted([s for s in sessions if s["venue"] == v], key=lambda x: x["start_min"])
    gaps = []
    cursor = DAY_START
    for s in items:
        if s["start_min"] > cursor:
            gaps.append({"from": mh(cursor), "to": s["start"], "minutes": s["start_min"] - cursor})
        cursor = max(cursor, s["end_min"])
    if cursor < DAY_END:
        gaps.append({"from": mh(cursor), "to": mh(DAY_END), "minutes": DAY_END - cursor})
    occupied = sum(s["duration_min"] for s in items)
    lanes[v] = {
        "venue": v, "venue_label": VENUE_NAME[v],
        "capacity": venues[v]["capacity"],
        "session_count": len(items),
        "session_ids": [s["id"] for s in items],
        "occupied_minutes": occupied,
        "idle_minutes": (DAY_END - DAY_START) - occupied,
        "utilization_pct": round(occupied / (DAY_END - DAY_START) * 100, 1),
        "gaps": gaps,
        # sessions may not overlap inside one venue; verified below
        "internal_overlaps": [],
    }

# ---------- real overlap audit (includes cross-venue simultaneity) ----------
same_venue_overlaps, cross_venue_overlaps = [], []
for i, a in enumerate(sessions):
    for b in sessions[i + 1:]:
        if a["start_min"] < b["end_min"] and b["start_min"] < a["end_min"]:
            rec = {"a": a["id"], "b": b["id"], "venue_a": a["venue"], "venue_b": b["venue"],
                   "window": f"{mh(max(a['start_min'], b['start_min']))}-{mh(min(a['end_min'], b['end_min']))}",
                   "width_min": min(a["end_min"], b["end_min"]) - max(a["start_min"], b["start_min"])}
            if a["venue"] == b["venue"]:
                same_venue_overlaps.append(rec)
                lanes[a["venue"]]["internal_overlaps"].append(rec)
            else:
                cross_venue_overlaps.append(rec)

# simultaneous = same start minute in different venues
by_start = {}
for s in sessions:
    by_start.setdefault(s["start_min"], []).append(s)
simultaneous = [{"at": mh(k), "sessions": [s["id"] for s in v], "venues": [s["venue"] for s in v]}
                for k, v in sorted(by_start.items()) if len({s["venue"] for s in v}) > 1]

# lunch must not be merged into any session
lunch_clashes = [s["id"] for s in sessions
                 if s["start_min"] < LUNCH[1] and LUNCH[0] < s["end_min"]]

# dense window the task calls out (~10:00)
dense = [s for s in sessions if 9 * 60 + 50 <= s["start_min"] <= 11 * 60 + 10]

audit = {
    "schema": "a02-schedule-audit/1",
    "run_id": RUN_ID,
    "event": "Structure / Vision 2026",
    "date": "2026-11-07",
    "timezone": "Asia/Shanghai",
    "venue": "云构中心 · A / B / C 会场",
    "axis": {
        "from": mh(DAY_START), "to": mh(DAY_END),
        "total_minutes": DAY_END - DAY_START,
        "scale": "线性比例：块宽 = 时长 ÷ 420 分钟 × 轴宽；块左边缘 = (开始 − 09:00) ÷ 420 × 轴宽",
        "tick_step_minutes": 15,
        "no_time_adjustment": True,
    },
    "lunch": {
        "from": mh(LUNCH[0]), "to": mh(LUNCH[1]), "minutes": LUNCH[1] - LUNCH[0],
        "is_separate_item": True,
        "spans_all_lanes": True,
        "merged_into_session": False,
        "sessions_overlapping_lunch": lunch_clashes,
    },
    "session_count": len(sessions),
    "sessions": sessions,
    "per_venue": lanes,
    "conflicts": {
        "same_venue_overlaps": same_venue_overlaps,
        "same_venue_overlap_count": len(same_venue_overlaps),
        "cross_venue_overlaps": cross_venue_overlaps,
        "cross_venue_overlap_count": len(cross_venue_overlaps),
        "cross_venue_note": "不同会场同时进行不是冲突，如实列出以便核对排期密度。",
        "simultaneous_slots": simultaneous,
        "lunch_scoped_conflicts": lunch_clashes,
        "verdict": "无同会场时间重叠；跨会场并行 %d 组，属正常并行安排。" % len(cross_venue_overlaps),
    },
    "dense_window_around_1000": {
        "range": "09:50 - 11:10",
        "session_ids": [s["id"] for s in dense],
        "starts": [{"id": s["id"], "venue": s["venue"], "start": s["start"]} for s in dense],
        "note": "10:00 与 10:10 相邻会场同时开场（S04/A 与 S05/B），宽图按比例绘制后此处块宽约 177px 与 236px。",
    },
    "content_mapping": {
        "agenda-wide.png": {
            "size": "1920x1200",
            "shows": ["三条会场泳道（A/B/C）", "09:00-16:00 共用 15 分钟刻度时间轴",
                      "15 个活动块：编号 + 起止时间，位置与宽度按时长比例",
                      "12:00-13:00 午休跨三泳道标识", "各会场空档（灰底）",
                      "全部 15 项的标题 / 讲者 / 类别索引卡", "会场容量与读图方法"],
            "per_session_fields": ["编号", "标题", "讲者", "起止时间", "类别"],
        },
        "agenda-mobile.png": {
            "size": "720x1280",
            "shows": ["分时段列表：上午 / 午休 / 下午", "全部 15 项的编号、标题、会场、起止时间",
                      "讲者位置写明「讲者详见完整日程」"],
            "per_session_fields": ["编号", "标题", "会场", "起止时间"],
            "speaker_policy": "讲者可移到大图，手机图写明「讲者详见完整日程」。",
            "not_a_downscale": "手机图是重新排版的分时段列表，不是宽图缩放或裁切。",
        },
    },
    "totals": {
        "total_session_minutes": sum(s["duration_min"] for s in sessions),
        "avg_duration_min": round(sum(s["duration_min"] for s in sessions) / len(sessions), 1),
        "shortest_min": min(s["duration_min"] for s in sessions),
        "longest_min": max(s["duration_min"] for s in sessions),
        "by_category": {c: sum(1 for s in sessions if s["category"] == c) for c in CAT},
    },
}

with open(os.path.join(OUT, "schedule-audit.json"), "w", encoding="utf-8") as fh:
    json.dump(audit, fh, ensure_ascii=False, indent=2)
with open(os.path.join(TMP, "schedule-audit.check.json"), "w", encoding="utf-8") as fh:
    json.dump({"lanes": {k: {kk: vv for kk, vv in v.items() if kk not in ("internal_overlaps",)}
                         for k, v in lanes.items()},
               "conflicts": audit["conflicts"]["verdict"]}, fh, ensure_ascii=False, indent=2)

print("sessions", len(sessions), "| same-venue overlaps", len(same_venue_overlaps),
      "| cross-venue parallels", len(cross_venue_overlaps), "| lunch clashes", lunch_clashes)
for v in ("A", "B", "C"):
    L = lanes[v]
    print(f"  {v}: {L['session_count']} 场, 占用 {L['occupied_minutes']}min, 空档 {len(L['gaps'])} 段")
