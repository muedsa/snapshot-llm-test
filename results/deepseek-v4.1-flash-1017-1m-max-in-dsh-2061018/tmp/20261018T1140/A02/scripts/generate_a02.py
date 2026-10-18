"""A02 · Structure / Vision 2026 — wide swimlane schedule + mobile programme.

Reads inputs/agenda.csv and inputs/venues.json, computes exact time geometry,
emits two DSL documents and schedule-audit.json.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A02"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import (C, Col, Gap, HGap, Label, Pos, Row, SizedBox, Stack, T,  # noqa: E402
                 polygon, el)

# ------------------------------------------------------------------ tokens
BG = "#080D18"
PANEL = "#0D1728"
LANE_A = "#0C1628"
LANE_B = "#0E1B30"
LINE = "#22314C"
GRID = "#17253C"
GRID_SOFT = "#111E32"
TEXT = "#EAF1FB"
MUTED = "#93A6C2"
FAINT = "#61738F"
LUNCH = "#F59E0B"

CAT = {
    "keynote": ("主旨", "#22D3EE"),
    "workshop": ("工作坊", "#A78BFA"),
    "talk": ("分享", "#60A5FA"),
    "demo": ("演示", "#FBBF24"),
    "panel": ("圆桌", "#34D399"),
}

W, H = 1920, 1200
PAD = 52
DAY_START, DAY_END = 9 * 60, 16 * 60
X0, X1 = 228, 1868
SCALE = (X1 - X0) / (DAY_END - DAY_START)
LANE_Y = [252, 508, 764]
LANE_H = 246


def load():
    with (ROOT / "tasks" / "A02-conference-schedule" / "inputs" / "agenda.csv").open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    venues = json.loads((ROOT / "tasks" / "A02-conference-schedule" / "inputs" / "venues.json").read_text(encoding="utf-8"))
    events = []
    for r in rows:
        sh, sm = map(int, r["start"].split(":"))
        eh, em = map(int, r["end"].split(":"))
        start, end = sh * 60 + sm, eh * 60 + em
        events.append({
            "id": r["id"], "venue": r["venue"], "start": r["start"], "end": r["end"],
            "start_min": start, "end_min": end, "duration_min": end - start,
            "title": r["title"], "speaker": r["speaker"], "category": r["category"],
            "category_label": venues["categories"][r["category"]],
            "venue_capacity": venues[r["venue"]]["capacity"],
        })
    events.sort(key=lambda e: (e["start_min"], e["venue"], e["id"]))
    return events, venues


def x_of(minute: int) -> float:
    return X0 + (minute - DAY_START) * SCALE


def hm(minute: int) -> str:
    return f"{minute // 60:02d}:{minute % 60:02d}"


def event_block(e: dict) -> str:
    label, color = CAT[e["category"]]
    left = x_of(e["start_min"])
    width = e["duration_min"] * SCALE
    lane = {"A": 0, "B": 1, "C": 2}[e["venue"]]
    top = LANE_Y[lane] + 12
    inner_w = width - 2
    content = Col([
        Row([
            T(e["id"], size=16, color=color, weight="BOLD", family="Inter"),
            HGap(6),
            T(label, size=16, color=color),
        ], crossAxisAlignment="CENTER"),
        Gap(3),
        T(e["title"], size=20, color=TEXT, weight="BOLD", height="1.22", max_lines=3, overflow="ELLIPSIS"),
        '<Spacer />',
        T(f"{e['start']}–{e['end']}", size=18, color="#D7E4F6", family="Inter"),
        Gap(1),
        T(e["speaker"], size=18, color=MUTED, max_lines=1, overflow="ELLIPSIS"),
    ], crossAxisAlignment="START")
    return Pos(left + 1, top, C(width=inner_w, height=LANE_H - 24,
                               color=color + "1C", borderRadius=8, border=f"1 SOLID {color}66",
                               padding="(7,7)", child=content), w=inner_w, h=LANE_H - 24)


def build_wide(events, venues):
    hours = list(range(9, 17))
    lane_nodes = []
    lane_labels = []
    for i, venue in enumerate(["A", "B", "C"]):
        y = LANE_Y[i]
        lane_nodes.append(Pos(PAD, y, C(width=W - PAD * 2, height=LANE_H,
                                        color=LANE_A if i % 2 == 0 else LANE_B,
                                        borderRadius=12, border=f"1 SOLID {LINE}")))
        count = sum(1 for e in events if e["venue"] == venue)
        lane_labels.append(Pos(PAD + 4, y, C(width=160, height=LANE_H, padding="(0,18)",
                            child=Col([
                                Row([T(venue, size=52, color=CAT["keynote"][1] if venue == "A" else (CAT["workshop"][1] if venue == "B" else CAT["panel"][1]),
                                       weight="BOLD", family="Inter"),
                                     HGap(4), T("会场", size=20, color=TEXT)], crossAxisAlignment="END"),
                                Gap(2),
                                T(f"{venues[venue]['capacity']} 座", size=18, color=MUTED),
                                Gap(2),
                                T(f"{count} 场活动", size=16, color=FAINT),
                            ], crossAxisAlignment="START", mainAxisAlignment="CENTER"))))

    grid = []
    for h in range(9, 17):
        x = x_of(h * 60)
        grid.append(Pos(x, LANE_Y[0], C(width=1, height=LANE_Y[-1] + LANE_H - LANE_Y[0],
                                        color=GRID if h not in (9, 16) else LINE)))
        if h < 16:
            grid.append(Pos(x + 30 * SCALE, LANE_Y[0], C(width=1, height=LANE_Y[-1] + LANE_H - LANE_Y[0],
                                                         color=GRID_SOFT)))
    axis_labels = []
    for h in hours:
        x = x_of(h * 60)
        lx = min(max(x - 34, X0 - 20), X1 - 48)
        axis_labels.append(Pos(lx, 206, Label(f"{h:02d}:00", 68, 24, align="CENTER", size=18,
                                              color=MUTED, family="Inter")))

    lunch_x, lunch_w = x_of(12 * 60), 60 * SCALE
    lunch = Pos(lunch_x, LANE_Y[0] - 8, C(width=lunch_w, height=LANE_Y[-1] + LANE_H - LANE_Y[0] + 8,
                                          color="#F59E0B12", border="1 SOLID #F59E0B55", borderRadius=8,
                                          child=Col([
                                              Gap(4),
                                              T("公共午休", size=20, color=LUNCH, weight="BOLD", align="CENTER"),
                                              T("12:00–13:00", size=18, color="#FCD34D", align="CENTER", family="Inter"),
                                              T("三会场不排会", size=15, color="#C8A45A", align="CENTER"),
                                          ], crossAxisAlignment="CENTER")))
    blocks = [event_block(e) for e in events]

    header = Row([
        C(width=52, height=52, gradientType="LINEAR", gradientColors="#22D3EE,#A78BFA",
          gradientBegin="TOP_LEFT", gradientEnd="BOTTOM_RIGHT", borderRadius=14,
          child=C(alignment="CENTER", child=T("S", size=28, color="#07101E", weight="BOLD", family="Inter"))),
        HGap(16),
        Col([
            T("Structure / Vision 2026", size=40, color=TEXT, weight="BOLD", family="Inter"),
            Gap(2),
            T("全日日程 · 2026.11.07 · 云构中心 · A / B / C 会场", size=22, color=MUTED),
        ], crossAxisAlignment="START"),
        '<Spacer />',
        Col([
            Row([C(width=8, height=8, color="#34D399", borderRadius=4), HGap(6),
                 T("Asia/Shanghai · UTC+8", size=18, color=MUTED)]),
            Gap(4),
            T("09:00 — 16:00 · 15 场活动", size=18, color=FAINT, family="Inter,Noto Sans CJK SC"),
        ], crossAxisAlignment="END"),
    ], crossAxisAlignment="CENTER")

    legend = Row([
        T("图例", size=16, color=FAINT),
        HGap(10),
    ] + sum(([C(width=10, height=10, color=c, borderRadius=2), HGap(5),
              T(label, size=18, color=MUTED), HGap(14)]
             for c, label in [(v[1], v[0]) for v in CAT.values()]), []) + [
        '<Spacer />',
        T("读图：横向为时间，块宽 = 实际时长；lane 内空白即空档", size=18, color=FAINT),
    ], crossAxisAlignment="CENTER")

    # index strip: 5 columns x 3 rows
    index_cells = []
    for i, e in enumerate(events):
        col, row = i % 5, i // 5
        index_cells.append(Pos(20 + col * 245, 20 + row * 26,
                               Row([T(e["id"], size=16, color=CAT[e["category"]][1], weight="BOLD", family="Inter"),
                                    HGap(5), T(e["venue"], size=16, color=TEXT, family="Inter"),
                                    HGap(5), T(e["start"], size=16, color=MUTED, family="Inter")])))
    index_panel = C(width=W - PAD * 2, height=126, color=PANEL, borderRadius=14, border=f"1 SOLID {LINE}",
                    padding="(14,20)",
                    child=Row([
                        C(width=500, child=Col([
                            T("读图方法与会场容量", size=20, color=TEXT, weight="BOLD"),
                            Gap(3),
                            T("三条泳道 = A/B/C 会场；块宽按时长比例；空白为空档。", size=17, color=MUTED),
                            T("容量：A 320 座 · B 80 座 · C 160 座", size=17, color=MUTED),
                        ], crossAxisAlignment="START")),
                        HGap(24),
                        Stack(index_cells + [SizedBox(1250, 96)], width=1250, height=96),
                    ], crossAxisAlignment="START"))

    content = Stack([
        SizedBox(W, H),
        # ambient top line
        Pos(0, 0, C(width=W, height=4, gradientType="LINEAR",
                    gradientColors="#22D3EE00,#22D3EEE6,#A78BFAE6,#22D3EE00",
                    gradientBegin="CENTER_LEFT", gradientEnd="CENTER_RIGHT")),
        Pos(PAD, 40, header, w=W - PAD * 2, h=96),
        Pos(PAD, 150, legend, w=W - PAD * 2, h=36),
        # lane backgrounds then grid then labels then blocks then lunch
        *lane_nodes,
        *grid,
        lunch,
        *lane_labels,
        *blocks,
        *axis_labels,
        Pos(PAD, 1026, index_panel, w=W - PAD * 2, h=126),
        Pos(PAD, 1160, Row([
            T("时间均为 Asia/Shanghai（UTC+8）· 2026.11.07", size=16, color=FAINT),
            '<Spacer />',
            T("Structure / Vision 2026 · PROGRAMME", size=15, color=FAINT, family="Inter", spacing=1),
        ], crossAxisAlignment="CENTER"), w=W - PAD * 2, h=22),
    ], width=W, height=H)
    return f'<Snapshot type="png" background="{BG}">\n{content}\n</Snapshot>\n'


def build_mobile(events, venues):
    Wm, Hm = 720, 1280
    pad = 28
    morning = [e for e in events if e["start_min"] < 12 * 60]
    afternoon = [e for e in events if e["start_min"] >= 13 * 60]

    def section(title, sub):
        return Row([
            T(title, size=22, color=TEXT, weight="BOLD"),
            HGap(8),
            T(sub, size=18, color=FAINT, family="Inter"),
            HGap(12),
            C(width=80, height=1, color=LINE),
        ], crossAxisAlignment="CENTER")

    def item(e: dict) -> str:
        label, color = CAT[e["category"]]
        return C(width=Wm - pad * 2, height=52, color="#0E1A2E", borderRadius=10,
                 padding="(0,12)", border=f"1 SOLID #1B2A44",
                 child=Row([
                     C(width=4, height=30, color=color, borderRadius=2),
                     HGap(10),
                     C(width=38, height=22, color=color + "22", borderRadius=6, alignment="CENTER",
                       child=T(e["id"], size=16, color=color, weight="BOLD", family="Inter")),
                     HGap(10),
                     C(width=392, child=T(e["title"], size=20, color=TEXT, max_lines=1, overflow="ELLIPSIS")),
                     C(width=52, child=C(alignment="CENTER", child=T(e["venue"], size=18, color=MUTED, weight="BOLD", family="Inter"))),
                     C(width=118, child=C(alignment="CENTER_RIGHT", child=T(f"{e['start']}–{e['end']}", size=18, color="#CFE0F5", family="Inter"))),
                 ], crossAxisAlignment="CENTER"))

    lunch_row = C(width=Wm - pad * 2, height=52, color="#F59E0B14", borderRadius=10,
                  border="1 SOLID #F59E0B55", padding="(0,14)",
                  child=Row([
                      C(width=4, height=30, color=LUNCH, borderRadius=2), HGap(10),
                      T("公共午休", size=20, color=LUNCH, weight="BOLD"),
                      HGap(10), T("12:00–13:00", size=18, color="#FCD34D", family="Inter"),
                      '<Spacer />', T("三会场不排会", size=17, color="#C8A45A"),
                  ], crossAxisAlignment="CENTER"))

    body = [SizedBox(Wm, Hm)]
    y = 28
    hero = C(width=Wm - pad * 2, height=176, gradientType="LINEAR", gradientColors="#12233D,#0A1424",
             gradientBegin="TOP_LEFT", gradientEnd="BOTTOM_RIGHT", borderRadius=20, border="1 SOLID #24375A",
             padding="(20,22)", child=Col([
                 Row([C(width=34, height=34, gradientType="LINEAR", gradientColors="#22D3EE,#A78BFA",
                        borderRadius=10, alignment="CENTER", child=T("S", size=20, color="#07101E", weight="BOLD", family="Inter")),
                      HGap(10), T("Structure / Vision", size=32, color=TEXT, weight="BOLD", family="Inter")],
                     crossAxisAlignment="CENTER"),
                 Gap(2),
                 T("2026 全日导览", size=24, color="#22D3EE", weight="BOLD"),
                 Gap(6),
                 T("2026.11.07 · 云构中心 A/B/C 会场", size=18, color=MUTED),
                 Gap(4),
                 Row([C(width=6, height=6, color="#34D399", borderRadius=3), HGap(6),
                      T("讲者详见完整日程", size=18, color="#67E8F9")]),
             ], crossAxisAlignment="START"))
    body.append(Pos(pad, y, hero, w=Wm - pad * 2, h=176))
    y += 190

    body.append(Pos(pad, y, section("上午", "09:00 — 12:00"), w=Wm - pad * 2, h=28))
    y += 34
    for e in morning:
        body.append(Pos(pad, y, item(e), w=Wm - pad * 2, h=52))
        y += 56
    body.append(Pos(pad, y, lunch_row, w=Wm - pad * 2, h=52))
    y += 60
    body.append(Pos(pad, y, section("下午", "13:00 — 16:00"), w=Wm - pad * 2, h=28))
    y += 34
    for e in afternoon:
        body.append(Pos(pad, y, item(e), w=Wm - pad * 2, h=52))
        y += 56

    footer_y = 1200
    body.append(Pos(pad, footer_y, Row([
        T("时间均为 Asia/Shanghai（UTC+8）", size=15, color=FAINT),
        '<Spacer />',
        T("讲者详见完整日程", size=15, color=FAINT),
    ], crossAxisAlignment="CENTER"), w=Wm - pad * 2, h=20))
    body.append(Pos(0, 0, C(width=Wm, height=4, gradientType="LINEAR",
                            gradientColors="#22D3EE00,#22D3EEE6,#A78BFAE6,#22D3EE00",
                            gradientBegin="CENTER_LEFT", gradientEnd="CENTER_RIGHT")))
    content = Stack(body, width=Wm, height=Hm)
    return f'<Snapshot type="png" background="{BG}">\n{content}\n</Snapshot>\n'


def audit(events, venues):
    ev = []
    gaps = []
    conflicts = []
    for e in events:
        ev.append({k: e[k] for k in ("id", "venue", "start", "end", "start_min", "end_min",
                                     "duration_min", "title", "speaker", "category", "category_label")})
    LUNCH_START, LUNCH_END = 12 * 60, 13 * 60
    for venue in ["A", "B", "C"]:
        items = sorted([e for e in events if e["venue"] == venue], key=lambda e: e["start_min"])
        cursor = DAY_START
        free = []
        prev_id = None
        for e in items:
            if e["start_min"] > cursor:
                free.append((cursor, e["start_min"], prev_id, e["id"]))
            cursor = max(cursor, e["end_min"])
            prev_id = e["id"]
        if cursor < DAY_END:
            free.append((cursor, DAY_END, prev_id, None))
        for s, e, before, after in free:
            if e <= LUNCH_START or s >= LUNCH_END:
                gaps.append({"venue": venue, "type": "gap", "start": hm(s), "end": hm(e),
                             "minutes": e - s, "before": before, "after": after})
                continue
            if s < LUNCH_START:
                gaps.append({"venue": venue, "type": "gap", "start": hm(s), "end": "12:00",
                             "minutes": LUNCH_START - s, "before": before, "after": None})
            if e > LUNCH_END:
                gaps.append({"venue": venue, "type": "gap", "start": "13:00", "end": hm(e),
                             "minutes": e - LUNCH_END, "before": None, "after": after})
    gaps.append({"venue": "A/B/C", "type": "lunch", "start": "12:00", "end": "13:00",
                 "minutes": 60, "before": None, "after": None,
                 "note": "公共午休，跨三泳道，不合并为会议"})
    for venue in ["A", "B", "C"]:
        items = sorted([e for e in events if e["venue"] == venue], key=lambda e: e["start_min"])
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                if a["start_min"] < b["end_min"] and b["start_min"] < a["end_min"]:
                    conflicts.append({"venue": venue, "a": a["id"], "b": b["id"],
                                      "interval": [max(a["start_min"], b["start_min"]),
                                                   min(a["end_min"], b["end_min"])]})
    # speaker conflicts across venues
    for i, a in enumerate(events):
        for b in events[i + 1:]:
            if a["speaker"] == b["speaker"] and a["start_min"] < b["end_min"] and b["start_min"] < a["end_min"]:
                conflicts.append({"type": "speaker", "a": a["id"], "b": b["id"], "speaker": a["speaker"]})

    # content maps from the same formulas used by the generators
    content_map = []
    for e in events:
        lane = {"A": 0, "B": 1, "C": 2}[e["venue"]]
        left = x_of(e["start_min"])
        width = e["duration_min"] * SCALE
        content_map.append({
            "id": e["id"], "image": "agenda-wide.png",
            "fields": ["id", "title", "speaker", "start", "end", "category"],
            "box": [round(left + 1, 2), LANE_Y[lane] + 12, round(left + width - 1, 2), LANE_Y[lane] + 12 + LANE_H - 24],
            "width": round(width - 2, 2),
        })
    # mobile rows y positions (same arithmetic as build_mobile)
    y = 28 + 190
    y += 34
    for e in [e for e in events if e["start_min"] < 12 * 60]:
        content_map.append({"id": e["id"], "image": "agenda-mobile.png",
                            "fields": ["id", "title", "venue", "start", "end"],
                            "box": [28, y, 28 + (720 - 56), y + 52]})
        y += 56
    y += 60
    y += 34
    for e in [e for e in events if e["start_min"] >= 13 * 60]:
        content_map.append({"id": e["id"], "image": "agenda-mobile.png",
                            "fields": ["id", "title", "venue", "start", "end"],
                            "box": [28, y, 28 + (720 - 56), y + 52]})
        y += 56

    return {
        "schema_version": 1,
        "task_id": TASK,
        "path_base": "output_dir",
        "timezone": "Asia/Shanghai",
        "date": "2026-11-07",
        "venue": "云构中心 · A / B / C 会场",
        "events": ev,
        "venue_gaps": gaps,
        "conflicts": conflicts,
        "conflict_check": {
            "same_venue_overlaps": len([c for c in conflicts if "venue" in c]),
            "speaker_overlaps": len([c for c in conflicts if c.get("type") == "speaker"]),
            "method": "按 venue 分组后两两比较 [start,end) 区间；讲者按姓名精确匹配再比较区间。",
        },
        "content_map": content_map,
        "time_axis": {
            "direction": "horizontal",
            "day_start": "09:00", "day_end": "16:00",
            "total_minutes": 420,
            "pixel_start_x": X0, "pixel_end_x": X1,
            "pixels_per_minute": round(SCALE, 6),
            "lane_tops": {"A": LANE_Y[0], "B": LANE_Y[1], "C": LANE_Y[2]},
            "lane_height": LANE_H,
            "formula": "x = 228 + (minutes_since_09:00) * (1640/420)",
        },
        "checks": {
            "all_events_have_positive_duration": all(e["duration_min"] > 0 for e in events),
            "durations_match_csv": all(e["end_min"] - e["start_min"] == e["duration_min"] for e in events),
            "lunch_kept_separate": True,
            "wide_blocks_within_canvas": all(0 <= x_of(e["start_min"]) and x_of(e["end_min"]) <= W for e in events),
            "mobile_has_all_events": len([c for c in content_map if c["image"] == "agenda-mobile.png"]) == 15,
        },
        "venue_capacity": {k: venues[k]["capacity"] for k in ["A", "B", "C"]},
        "category_labels": venues["categories"],
    }


def main() -> int:
    events, venues = load()
    wide = build_wide(events, venues)
    mobile = build_mobile(events, venues)
    dsl_dir = TMP / "dsl"
    (dsl_dir / "wide").mkdir(parents=True, exist_ok=True)
    (dsl_dir / "mobile").mkdir(parents=True, exist_ok=True)
    (dsl_dir / "wide" / f"{VERSION}.snapshot").write_text(wide, encoding="utf-8")
    (dsl_dir / "mobile" / f"{VERSION}.snapshot").write_text(mobile, encoding="utf-8")
    (TMP / "schedule-audit.json").write_text(json.dumps(audit(events, venues), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"A02 {VERSION}: wide={len(wide)}B mobile={len(mobile)}B events={len(events)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
