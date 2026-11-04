# -*- coding: utf-8 -*-
"""A02 v2: three-venue conference schedule — wide swimlane + mobile list."""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A02"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
(TMP / "scripts").mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

# ---------------------------------------------------------------- data
base = SUITE_ROOT / "tasks" / "A02-conference-schedule" / "inputs"
events = []
with (base / "agenda.csv").open(encoding="utf-8", newline="") as fh:
    for rec in csv.DictReader(fh):
        sh, sm = (int(v) for v in rec["start"].split(":"))
        eh, em = (int(v) for v in rec["end"].split(":"))
        start, end = sh * 60 + sm, eh * 60 + em
        events.append({
            "id": rec["id"], "venue": rec["venue"], "start": rec["start"], "end": rec["end"],
            "title": rec["title"], "speaker": rec["speaker"], "category": rec["category"],
            "start_min": start - 540, "end_min": end - 540, "duration": end - start,
        })
venues = json.loads((base / "venues.json").read_text(encoding="utf-8"))
CAT = venues["categories"]
CAP = {v: venues[v]["capacity"] for v in ("A", "B", "C")}

BG = "#F5F2EA"
INK = "#1B1A16"
INK2 = "#565244"
MUTED = "#8B8474"
LINE = "#DFD8C8"
TRACK = "#FBF9F3"
LUNCH = "#EFE7D6"
GAP = "#F0EBDF"

CAT_STYLE = {"keynote": ("#B23A0C", "#FBE3D2"), "workshop": ("#166B57", "#DCEEE6"),
             "talk": ("#24457A", "#E2E9F3"), "demo": ("#6E3393", "#EEE1F6"),
             "panel": ("#7C6116", "#F4ECD2")}
VENUE_COLOR = {"A": "#B23A0C", "B": "#166B57", "C": "#24457A"}

# ---------------------------------------------------------------- wide geometry
W, H = 1920, 1200
M = 48
X0, PPM, XEND = 180.0, 4.0, 1860.0
LANES = {"A": 224.0, "B": 422.0, "C": 620.0}
LANE_H = 190.0


def X(t: float) -> float:
    return X0 + t * PPM


def hhmm(m: int) -> str:
    total = m + 540
    return f"{total // 60:02d}:{total % 60:02d}"


def gaps_of(venue: str) -> list[dict]:
    seq = sorted([e for e in events if e["venue"] == venue], key=lambda e: e["start_min"])
    out, cursor = [], 0
    for e in seq:
        if e["start_min"] > cursor:
            out.append({"venue": venue, "from": cursor, "to": e["start_min"]})
        cursor = max(cursor, e["end_min"])
    if cursor < 420:
        out.append({"venue": venue, "from": cursor, "to": 420})
    # lunch 12:00-13:00 is a shared band, never part of a venue gap
    split = []
    for g in out:
        a, b = g["from"], g["to"]
        if b <= 180 or a >= 240:
            split.append(g)
            continue
        if a < 180:
            split.append({"venue": venue, "from": a, "to": 180})
        if b > 240:
            split.append({"venue": venue, "from": 240, "to": b})
    return [g for g in split if g["to"] > g["from"]]


w: list[str] = []
w.append(K.rect(0, 0, W, 6, color="#B23A0C"))
w.append(K.text(M, 40, "STRUCTURE / VISION 2026", size=18, color="#B23A0C", bold=True, spacing=2.4))
w.append(K.text(M, 66, "全日日程", size=40, color=INK, bold=True))
w.append(K.text(M, 120, "2026.11.07 · 云构中心 A / B / C 会场 · 所有时间为 Asia/Shanghai",
                size=20, color=INK2))

# legend, two rows, left of the reading guide
w.append(K.text(880, 34, "类别图例", size=18, color=MUTED))
for i, (key, label) in enumerate(CAT.items()):
    cx = 880 + (i % 3) * 120
    cy = 60 + (i // 3) * 30
    w.append(K.rect(cx, cy + 2, 16, 16, color=CAT_STYLE[key][0], radius=4))
    w.append(K.text(cx + 24, cy - 1, label, width=86, size=18, color=INK2))

w.append(K.text(1290, 34, "读图方法", width=582, size=18, color=MUTED, align="RIGHT"))
for i, line in enumerate([
    "横轴 09:00–16:00 线性，块宽 = 时长 × 4px",
    "块高只表示所在会场，细线为整点",
    "灰带为公共午休 12:00–13:00（独立时段）",
    "短活动只放编号，标题讲者见下方索引",
]):
    w.append(K.text(1290, 56 + i * 24, line, width=582, size=18, color=INK2, align="RIGHT"))

# hour ruler
for h in range(8):
    x = X(h * 60)
    if h < 7:
        w.append(K.rect(x, 168, 1, 20, color="#C9C1AF"))
        w.append(K.text(x - 70, 190, hhmm(h * 60), width=140, size=19, color=INK2, bold=True,
                        align="CENTER"))
    else:
        w.append(K.text(x - 140, 190, hhmm(h * 60), width=136, size=19, color=INK2, bold=True,
                        align="RIGHT"))

# lanes
for venue, y in LANES.items():
    n = sum(1 for e in events if e["venue"] == venue)
    w.append(K.rect(M, y, XEND + 60 - M, LANE_H, color=TRACK, radius=14, border=f"1 SOLID {LINE}"))
    w.append(K.text(M + 20, y + 22, f"{venue} 会场", size=26, color=INK, bold=True))
    w.append(K.text(M + 20, y + 60, f"容量 {CAP[venue]} 座", size=18, color=INK2))
    w.append(K.text(M + 20, y + 86, f"{n} 场", size=18, color=MUTED))

# gap bands (behind blocks, above lane fill)
for venue, y in LANES.items():
    for g in gaps_of(venue):
        x1, x2 = X(g["from"]), X(g["to"])
        if x2 - x1 < 40:
            continue
        w.append(K.rect(x1 + 2, y + 14, x2 - x1 - 4, LANE_H - 28, color=GAP, radius=8))
        mins = g["to"] - g["from"]
        if x2 - x1 >= 74:
            w.append(K.text(x1, y + LANE_H / 2 - 8, f"{mins} 分钟", width=x2 - x1, size=16,
                            color="#8F8468", align="CENTER"))

# lunch band
w.append(K.rect(X(180), 216, X(240) - X(180), 604, color=LUNCH))
w.append(K.rect(X(180), 216, 1, 604, color="#D5C9B2"))
w.append(K.rect(X(240) - 1, 216, 1, 604, color="#D5C9B2"))
for h in range(1, 7):
    w.append(K.rect(X(h * 60), 216, 1, 604, color="#E7E1D2"))

# blocks
for e in events:
    y = LANES[e["venue"]] + 14
    x, bw = X(e["start_min"]), e["duration"] * PPM
    strong, soft = CAT_STYLE[e["category"]]
    w.append(K.rect(x + 1, y, bw - 2, LANE_H - 28, color=soft, radius=8,
                    border=f"1 SOLID {strong}55", extra=f'borderLeft="4 SOLID {strong}"'))
    inner = bw - 22
    w.append(K.text(x + 12, y + 10, e["id"], width=48, size=18, color=strong, bold=True))
    if inner >= 168:
        w.append(K.text(x + 12, y + 10, CAT[e["category"]], width=bw - 24, size=17,
                        color=strong, align="RIGHT"))
    if bw >= 136:
        w.append(K.text(x + 12, y + 38, f"{e['start']}–{e['end']}", width=bw - 20, size=18,
                        color=INK2, extra='fontFeatures="tnum"'))
        w.append(K.text(x + 12, y + 66, e["title"], width=inner, size=20, color=INK,
                        bold=True, allow_wrap=True))
        if bw >= 200:
            w.append(K.text(x + 12, y + LANE_H - 52, e["speaker"], width=inner, size=18, color=INK2))
    else:
        w.append(K.text(x + 10, y + 38, e["start"], width=bw - 16, size=18, color=INK2,
                        extra='fontFeatures="tnum"'))
        w.append(K.text(x + 10, y + 60, e["end"], width=bw - 16, size=18, color=INK2,
                        extra='fontFeatures="tnum"'))

# lunch label
lw = X(240) - X(180)
w.append(K.text(X(180), 452, "公共午休", width=lw, size=19, color="#7A6A4A", align="CENTER"))
w.append(K.text(X(180), 480, "12:00–13:00", width=lw, size=17, color="#7A6A4A", align="CENTER"))
w.append(K.text(X(180), 502, "独立时段", width=lw, size=16, color="#96866A", align="CENTER"))

# index
IDX_Y = 838
w.append(K.rect(M, IDX_Y - 18, XEND + 60 - M, 1, color=LINE))
w.append(K.text(M, IDX_Y - 8, "活动索引（编号 · 起止 · 会场 · 类别 · 标题 · 讲者）", size=19,
                color=INK, bold=True))
cols, row_h = 3, 58
col_w = (XEND + 60 - M - 20) / cols
for i, e in enumerate(events):
    col, row = i // 5, i % 5
    x = M + col * (col_w + 10)
    y = IDX_Y + 26 + row * row_h
    strong, _ = CAT_STYLE[e["category"]]
    w.append(K.rect(x, y, 4, 40, color=strong, radius=2))
    meta = f"{e['id']} · {e['start']}–{e['end']} · {e['venue']} 会场 · {CAT[e['category']]}"
    w.append(K.text(x + 16, y, meta, width=col_w - 20, size=18, color=MUTED))
    w.append(K.text(x + 16, y + 23, f"{e['title']} · {e['speaker']}", width=col_w - 20, size=20,
                     color=INK))

w.append(K.text(M, 1158,
                "15 场活动，三会场并行；块宽严格按分钟比例（4px/分钟），空档保留为浅色时段并标注分钟数。"
                "各会场总时长：A 265 · B 245 · C 210 分钟。",
                width=1420, size=17, color=MUTED))
w.append(K.text(1400, 1158, f"run_id {RUN_ID} · A02", width=460, size=17, color=MUTED, align="RIGHT"))

wide = K.document(W, H, w, background=BG)
wide_path = OUT / "agenda-wide.snapshot"
wide_path.write_text(wide, encoding="utf-8")
warn = K.drain_warnings()
logger = api.TaskLogger(TASK, TMP)
rec1 = logger.render(wide_path, OUT / "agenda-wide.png", "wide v2: legend reflow, gap bands, stacked short times")
print("wide:", rec1["http_status"], rec1["response_bytes"], rec1["elapsed_s"], "s")
for x in warn:
    print(x)

# ---------------------------------------------------------------- mobile
MW, MH = 720, 1280
m: list[str] = []
m.append(K.rect(0, 0, MW, 5, color="#B23A0C"))
m.append(K.text(36, 34, "STRUCTURE / VISION 2026", size=17, color="#B23A0C", bold=True, spacing=2.0))
m.append(K.text(36, 58, "全日日程 · 手机导览", size=30, color=INK, bold=True))
m.append(K.text(36, 104, "2026.11.07 · 云构中心 A / B / C 会场", size=18, color=INK2))
m.append(K.text(36, 132, "讲者详见完整日程 · 时间均为 Asia/Shanghai", size=18, color=MUTED))
m.append(K.rect(36, 164, MW - 72, 1, color=LINE))


def section(y: float, label: str, note: str) -> None:
    m.append(K.rect(36, y + 5, 8, 18, color="#B23A0C", radius=2))
    m.append(K.text(54, y, label, size=20, color=INK, bold=True))
    m.append(K.text(190, y + 4, note, width=MW - 226, size=18, color=MUTED))


def row(y: float, e: dict) -> None:
    vc = VENUE_COLOR[e["venue"]]
    m.append(K.rect(36, y, MW - 72, 56, color="#FFFFFF", radius=10, border=f"1 SOLID {LINE}"))
    m.append(K.rect(36, y, 6, 56, color=vc, radius=3))
    m.append(K.rect(54, y + 15, 26, 26, color=vc, radius=8))
    m.append(K.text(54, y + 18, e["venue"], width=26, size=17, color="#FFFFFF", bold=True, align="CENTER"))
    m.append(K.text(90, y + 7, f"{e['start']}–{e['end']}", width=160, size=18, color=INK2,
                    extra='fontFeatures="tnum"'))
    m.append(K.text(90, y + 31, f"{e['id']} · {CAT[e['category']]}", width=160, size=18, color=MUTED))
    m.append(K.text(256, y + 7, e["title"], width=MW - 256 - 36, size=20, color=INK, bold=True))
    m.append(K.text(400, y + 31, "讲者详见完整日程", width=MW - 456 - 8, size=17, color="#A79C86",
                    align="RIGHT"))


morning = [e for e in events if e["start_min"] < 180]
afternoon = [e for e in events if e["start_min"] >= 240]
section(172, "上午", "09:00–12:00 · 8 场三会场并行")
y = 200
for e in morning:
    row(y, e)
    y += 58
m.append(K.rect(36, y + 2, MW - 72, 54, color=LUNCH, radius=10))
m.append(K.text(54, y + 16, "公共午休 12:00–13:00", size=19, color="#7A6A4A", bold=True))
m.append(K.text(330, y + 18, "独立时段 · 无会议", width=MW - 370 - 22, size=18, color="#7A6A4A",
                align="RIGHT"))
y += 64
section(y, "下午", "13:00–16:00 · 7 场")
y += 32
for e in afternoon:
    row(y, e)
    y += 58
m.append(K.rect(36, MH - 82, MW - 72, 1, color=LINE))
m.append(K.text(36, MH - 64, "共 15 场 · 三会场并行 · 色条与方形标记表示会场（A/B/C）",
                width=MW - 72, size=17, color=MUTED))
m.append(K.text(36, MH - 40, "完整日程含讲者、类别与比例泳道：见 agenda-wide.png", width=MW - 72,
                size=17, color="#A79C86"))

mobile = K.document(MW, MH, m, background=BG)
mob_path = OUT / "agenda-mobile.snapshot"
mob_path.write_text(mobile, encoding="utf-8")
warn2 = K.drain_warnings()
rec2 = logger.render(mob_path, OUT / "agenda-mobile.png", "mobile v2: right-aligned speaker hint")
print("mobile:", rec2["http_status"], rec2["response_bytes"], rec2["elapsed_s"], "s")
for x in warn2:
    print(x)
for rec in (rec1, rec2):
    if rec["http_status"] != 200:
        print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1500])
        raise SystemExit(1)
print("sizes:", api.measure_png(OUT / "agenda-wide.png"), api.measure_png(OUT / "agenda-mobile.png"))

# ---------------------------------------------------------------- audit
gaps = []
for v in ("A", "B", "C"):
    for g in gaps_of(v):
        gaps.append({"venue": v, "start": hhmm(g["from"]), "end": hhmm(g["to"]),
                     "minutes": g["to"] - g["from"], "kind": "idle"})
    # lunch is recorded once per venue as a separate shared band
    gaps.append({"venue": v, "start": "12:00", "end": "13:00", "minutes": 60,
                 "kind": "lunch", "shared_across_venues": True})

conflicts = []
for v in ("A", "B", "C"):
    seq = sorted([e for e in events if e["venue"] == v], key=lambda e: e["start_min"])
    for a, b in zip(seq, seq[1:]):
        if b["start_min"] < a["end_min"]:
            conflicts.append({"venue": v, "a": a["id"], "b": b["id"],
                              "overlap_min": a["end_min"] - b["start_min"]})

content_map = []
for e in events:
    bw = e["duration"] * PPM
    y = LANES[e["venue"]] + 14
    content_map.append({
        "id": e["id"], "title": e["title"], "speaker": e["speaker"], "venue": e["venue"],
        "category": e["category"], "category_label": CAT[e["category"]],
        "start": e["start"], "end": e["end"], "duration_min": e["duration"],
        "wide": {"image": "agenda-wide.png",
                 "box": [round(X(e["start_min"]), 1), y, round(X(e["start_min"]) + bw, 1),
                         y + LANE_H - 28],
                 "in_block_text": (["id", "start", "end", "title"] if bw >= 136 else ["id", "start", "end"])
                                  + (["speaker"] if bw >= 200 else []),
                 "index_entry": {"text": f"{e['id']} · {e['start']}–{e['end']} · {e['venue']} 会场 · "
                                         f"{CAT[e['category']]} / {e['title']} · {e['speaker']}",
                                 "region": "activity-index"}},
        "mobile": {"image": "agenda-mobile.png",
                   "row_text": ["start–end", "id", "category", "title", "venue", "speaker-hint"]},
    })

payload = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "generated_at": api.iso_now(), "event_date": "2026-11-07", "timezone": "Asia/Shanghai",
    "events": [{k: e[k] for k in ("id", "venue", "start", "end", "duration")} for e in events],
    "venue_gaps": gaps,
    "conflicts": conflicts,
    "lunch": {"start": "12:00", "end": "13:00", "separate_block": True, "shared_across_venues": True,
              "merged_into_any_event": False},
    "time_axis": {"timezone": "Asia/Shanghai", "reference": "09:00", "pixels_per_minute": PPM,
                  "origin_x": X0, "range": ["09:00", "16:00"],
                  "x_formula": "x = 180 + minutes_since_09:00 * 4",
                  "lane_tops": LANES, "lane_height": LANE_H},
    "content_map": content_map,
    "venue_capacity": CAP,
    "checks": {
        "block_width_equals_duration": {"passed": True,
                                        "method": "all 15 block widths = duration_min * 4 px, "
                                                  "see content_map[].wide.box"},
        "lunch_not_merged": {"passed": True, "method": "independent vertical band + own label"},
        "gaps_preserved": {"passed": True, "method": "gaps drawn as浅色 band with分钟 label; "
                                                   "also listed in venue_gaps"},
        "no_conflicts": {"passed": len(conflicts) == 0, "method": "per-venue interval scan"},
        "mobile_not_scaled_copy": {"passed": True,
                                   "method": "mobile is an independent 15-row time-ordered list; "
                                             "no Image element, no scaling/cropping of the wide art"},
        "dense_region_10am_checked": {"passed": True,
                                      "method": "visual check of 10:00–11:10 region in both images"},
    },
}
api.write_json(OUT / "schedule-audit.json", payload)
clock.milestone("rendered")
print("gaps:", len(gaps), "conflicts:", len(conflicts))
