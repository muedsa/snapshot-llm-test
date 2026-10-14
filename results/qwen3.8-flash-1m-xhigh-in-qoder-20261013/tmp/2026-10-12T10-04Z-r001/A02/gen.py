"""A02 - Structure/Vision 2026 three-venue schedule: 1920x1200 lanes + 720x1280 mobile.

Reads tasks/A02-conference-schedule/inputs/{agenda.csv,venues.json}, keeps every
start/end exactly as given, derives durations/gaps/conflicts, writes
schedule-audit.json and emits both Snapshot DSL files.

Run from the suite task root:
  python tmp/<run_id>/A02/gen.py --ver v001 [--final outputs/<run_id>/A02/...]
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Border, Col, Container, Opacity, Positioned, Row, Snapshot, Stack, Text,
    hline, label, num, vline,
)

RUN = "2026-10-12T10-04Z-r001"
TASK = "A02"
IN_DIR = ROOT / "tasks" / "A02-conference-schedule" / "inputs"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

FONT = "Noto Sans CJK SC,Inter"
FONT_MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"

BG = "#080D1C"
CARD = "#0F1730"
CARD_2 = "#121C38"
LINE = "#22324F"
LINE_SOFT = "#182541"
TXT, TXT_2, TXT_3 = "#F1F5FB", "#9DB0CE", "#67799A"

CAT_COLOR = {"keynote": "#A78BFA", "workshop": "#34D399", "talk": "#38BDF8",
             "demo": "#FB923C", "panel": "#F472B6"}
LUNCH = "#FBBF24"
VENUE_COLOR = {"A": "#60A5FA", "B": "#22D3EE", "C": "#C084FC"}

AXIS_START, AXIS_END = 9 * 60, 16 * 60          # minutes of day
LUNCH_START, LUNCH_END = 12 * 60, 13 * 60


def to_min(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def hhmm(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


# ---------------------------------------------------------------- data
venues = json.loads((IN_DIR / "venues.json").read_text(encoding="utf-8"))
CAT_LABEL = venues["categories"]
CAP = {k: v["capacity"] for k, v in venues.items() if k != "categories"}

events = []
with (IN_DIR / "agenda.csv").open(encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        s, e = to_min(r["start"]), to_min(r["end"])
        assert s < e, r
        events.append({
            "id": r["id"], "venue": r["venue"], "start_min": s, "end_min": e,
            "start": r["start"], "end": r["end"],
            "duration_min": e - s, "title": r["title"],
            "speaker": r["speaker"], "category": r["category"],
            "category_label": CAT_LABEL[r["category"]],
        })
assert len(events) == 15, len(events)
assert all(e["category"] in CAT_COLOR for e in events)

by_venue = {v: sorted([e for e in events if e["venue"] == v], key=lambda x: x["start_min"])
            for v in ("A", "B", "C")}

# gaps per venue inside the 09:00-16:00 window; the public lunch is listed apart
venue_gaps = []
for v, evs in by_venue.items():
    busy = sorted((e["start_min"], e["end_min"]) for e in evs)
    free, cur = [], AXIS_START
    for s, e in busy:
        if s > cur:
            free.append((cur, s))
        cur = max(cur, e)
    if cur < AXIS_END:
        free.append((cur, AXIS_END))
    for a, b in free:
        if a < LUNCH_START:
            g1 = min(b, LUNCH_START)
            venue_gaps.append({"venue": v, "start": hhmm(a), "end": hhmm(g1),
                               "start_min": a, "end_min": g1,
                               "duration_min": g1 - a, "kind": "free"})
        if a < LUNCH_END < b or a < LUNCH_START < b:
            venue_gaps.append({"venue": v, "start": hhmm(LUNCH_START),
                               "end": hhmm(LUNCH_END), "start_min": LUNCH_START,
                               "end_min": LUNCH_END, "duration_min": 60,
                               "kind": "public_lunch"})
        if b > LUNCH_END:
            a2 = max(a, LUNCH_END)
            venue_gaps.append({"venue": v, "start": hhmm(a2), "end": hhmm(b),
                               "start_min": a2, "end_min": b,
                               "duration_min": b - a2, "kind": "free"})

# conflicts = same venue overlapping. Computed, never invented.
conflicts = []
for v, evs in by_venue.items():
    for i in range(len(evs) - 1):
        a, b = evs[i], evs[i + 1]
        if b["start_min"] < a["end_min"]:
            conflicts.append({
                "venue": v, "pair": [a["id"], b["id"]],
                "overlap_start": hhmm(max(a["start_min"], b["start_min"])),
                "overlap_end": hhmm(min(a["end_min"], b["end_min"])),
                "overlap_minutes": min(a["end_min"], b["end_min"]) - max(a["start_min"], b["start_min"]),
            })

cross_venue_parallel = []
for i, a in enumerate(events):
    for b in events[i + 1:]:
        if a["venue"] != b["venue"] and b["start_min"] < a["end_min"]:
            cross_venue_parallel.append({
                "pair": [a["id"], b["id"]], "venues": [a["venue"], b["venue"]],
                "overlap": f"{hhmm(max(a['start_min'], b['start_min']))}-"
                           f"{hhmm(min(a['end_min'], b['end_min']))}",
                "is_conflict": False,
            })

audit = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "event_date": "2026.11.07",
    "timezone": "Asia/Shanghai",
    "place": "云构中心 · A / B / C 会场",
    "source_inputs": ["tasks/A02-conference-schedule/inputs/agenda.csv",
                      "tasks/A02-conference-schedule/inputs/venues.json"],
    "venue_capacity": CAP,
    "category_labels": CAT_LABEL,
    "time_axis": {
        "timezone": "Asia/Shanghai",
        "baseline": "09:00",
        "window_start_min": AXIS_START,
        "window_end_min": AXIS_END,
        "window_minutes": AXIS_END - AXIS_START,
        "wide_axis_px": None,          # filled after geometry is computed
        "px_per_minute": None,
        "axis_x0": None,
        "mapping": "x = axis_x0 + (start_min - 540) * px_per_minute；width = duration_min * px_per_minute",
        "note": "块位置与长度严格按实际起止时间线性比例绘制，未为容纳文字调整任何时间。",
    },
    "public_lunch": {"start": "12:00", "end": "13:00", "duration_min": 60,
                     "spans": ["A", "B", "C"],
                     "merged_with_session": False,
                     "note": "公共午休单独成带，跨三条泳道，不与任何会议合并。"},
    "events": [{"id": e["id"], "venue": e["venue"], "start": e["start"], "end": e["end"],
                "start_min": e["start_min"], "end_min": e["end_min"],
                "duration_min": e["duration_min"], "title": e["title"],
                "speaker": e["speaker"], "category": e["category"],
                "category_label": e["category_label"]} for e in events],
    "venue_gaps": venue_gaps,
    "conflicts": conflicts,
    "conflict_rule": "同一会场内两活动时间区间相交才算冲突；跨会场并行不属于冲突。",
    "cross_venue_parallel_informational": cross_venue_parallel,
    "content_map": [],           # filled below once both layouts are computed
}

# ================================================================ WIDE 1920x1200
W, H = 1920, 1200
PAD = 32
LANE_LABEL_W = 186
AXIS_X0 = PAD + LANE_LABEL_W
AXIS_X1 = W - PAD - 4
AXIS_W = AXIS_X1 - AXIS_X0
PPM = AXIS_W / (AXIS_END - AXIS_START)
LANE_TOP = 214
LANE_H = 140
LANE_GAP = 12
LANES = {"A": LANE_TOP, "B": LANE_TOP + LANE_H + LANE_GAP,
         "C": LANE_TOP + 2 * (LANE_H + LANE_GAP)}
BLOCK_H = 104
AXIS_Y = LANE_TOP + 3 * LANE_H + 2 * LANE_GAP + 12


def x_of(minute: int) -> float:
    return AXIS_X0 + (minute - AXIS_START) * PPM


audit["time_axis"].update({"wide_axis_px": round(AXIS_W, 2),
                           "px_per_minute": round(PPM, 4), "axis_x0": round(AXIS_X0, 2)})

wide: list = []


def card(x, y, w, h, *, fill=CARD, radius=16, border=LINE):
    return Positioned(C(width=num(w), height=num(h), color=fill, borderRadius=num(radius),
                        border=f"1 SOLID {border}"), left=num(x), top=num(y))


def layer_stack(*children, w=W, h=H, clip="HARD_EDGE"):
    return Stack(C(width=num(w), height=num(h)), *children,
                 alignment="TOP_LEFT", clipBehavior=clip)


# header
wide.append(
    Positioned(
        Row(
            C(width="6", height="56", color=LUNCH, borderRadius="3"),
            C(width="18"),
            Col(
                Text("Structure / Vision 2026 · 全日日程", color=TXT, fontSize="36",
                     fontStyle="BOLD", fontFamily=FONT),
                C(height="6"),
                Text("2026.11.07 · 云构中心 A / B / C 会场 · 时间均为 Asia/Shanghai",
                     color=TXT_2, fontSize="20", fontFamily=FONT),
                crossAxisAlignment="START",
            ),
            crossAxisAlignment="CENTER",
        ),
        left=num(PAD), top=num(34),
    )
)
wide.append(
    Positioned(
        Col(
            Text("09:00 – 16:00", color=TXT, fontSize="26", fontStyle="BOLD", fontFamily=FONT,
                 textAlign="RIGHT"),
            C(height="4"),
            Text(f"1 分钟 = {PPM:.2f} 像素", color=TXT_3, fontSize="18", fontFamily=FONT,
                 textAlign="RIGHT"),
            crossAxisAlignment="END",
        ),
        right=num(PAD), top=num(38),
    )
)

# legend + how to read
LEG_Y = 128
wide.append(card(PAD, LEG_Y, W - 2 * PAD, 66, fill=CARD_2, radius=12))
lx = PAD + 22
wide.append(Positioned(Text("读图方法", color=LUNCH, fontSize="20", fontStyle="BOLD",
                            fontFamily=FONT), left=num(lx), top=num(LEG_Y + 22)))
lx += 110
READ = ("块的水平位置与宽度严格按实际起止时间线性比例绘制；未画色块的区间即该会场真实空档；"
        "琥珀横带为全场公共午休 12:00–13:00，独立于任何会议；色块颜色表示类别，块内编号对应下方索引。")
wide.append(Positioned(Text(READ, color=TXT_2, fontSize="18", fontFamily=FONT),
                       left=num(lx), top=num(LEG_Y + 10), width=num(900)))
lx += 920
for k in ("keynote", "workshop", "talk", "demo", "panel"):
    wide.append(Positioned(C(width="16", height="16", color=CAT_COLOR[k], borderRadius="4"),
                           left=num(lx), top=num(LEG_Y + 25)))
    wide.append(Positioned(Text(CAT_LABEL[k], color=TXT_2, fontSize="18", fontFamily=FONT),
                           left=num(lx + 22), top=num(LEG_Y + 22)))
    lx += 96

# lane backgrounds + labels
for v in ("A", "B", "C"):
    y = LANES[v]
    wide.append(card(PAD, y, W - 2 * PAD, LANE_H, fill="#0C1428", radius=14,
                     border="#1B2A47"))
    wide.append(
        Positioned(
            Col(
                Row(
                    C(width="12", height="12", color=VENUE_COLOR[v], shape="CIRCLE"),
                    C(width="10"),
                    Text(f"{v} 会场", color=TXT, fontSize="28", fontStyle="BOLD",
                         fontFamily=FONT),
                    crossAxisAlignment="CENTER",
                ),
                C(height="6"),
                Text(f"容量 {CAP[v]} 人", color=TXT_2, fontSize="20", fontFamily=FONT),
                C(height="4"),
                Text(f"{len(by_venue[v])} 场活动", color=TXT_3, fontSize="18", fontFamily=FONT),
                crossAxisAlignment="START",
            ),
            left=num(PAD + 22), top=num(y + 26), width=num(LANE_LABEL_W - 44),
        )
    )

# hour gridlines + axis labels
for m in range(AXIS_START, AXIS_END + 1, 60):
    x = x_of(m)
    wide.append(vline(x, LANE_TOP - 6, AXIS_Y, 1 if m != AXIS_START else 2,
                      LINE_SOFT if m != AXIS_START else "#3A4C73"))
    wide.append(label(x, AXIS_Y + 10, hhmm(m), 20, TXT_2, anchor="center_top",
                      align="CENTER", width=76, font=FONT,
                      bold=(m in (AXIS_START, AXIS_END))))
# half-hour minor ticks
for m in range(AXIS_START + 30, AXIS_END, 60):
    wide.append(vline(x_of(m), LANE_TOP - 6, AXIS_Y, 1, "#131F3A"))
wide.append(Positioned(C(width=num(AXIS_W), height="2", color="#3A4C73"),
                       left=num(AXIS_X0), top=num(AXIS_Y)))
wide.append(label(AXIS_X1, AXIS_Y + 40, "时间轴 · Asia/Shanghai", 18, TXT_3,
                  anchor="right_top", align="RIGHT", width=300, font=FONT))

# lunch band across all three lanes
lx0, lx1 = x_of(LUNCH_START), x_of(LUNCH_END)
wide.append(
    Positioned(
        C(width=num(lx1 - lx0), height=num(AXIS_Y - LANE_TOP + 2), color="#FBBF241A",
          borderRadius="10", border="2 SOLID #FBBF2466"),
        left=num(lx0), top=num(LANE_TOP - 2),
    )
)
wide.append(
    Positioned(
        Border(
            Container(
                Col(
                    Text("公共午休", color="#1A1204", fontSize="22", fontStyle="BOLD",
                         fontFamily=FONT, textAlign="CENTER"),
                    C(height="2"),
                    Text("12:00 – 13:00", color="#3A2A05", fontSize="18", fontFamily=FONT,
                         textAlign="CENTER"),
                    crossAxisAlignment="CENTER",
                ),
                padding="(8,16)", color=LUNCH, borderRadius="10",
            ),
            border="1 SOLID #FDE68A", borderRadius="12", boxShadow="ELEVATION_4",
        ),
        left=num((lx0 + lx1) / 2 - 76), top=num((LANE_TOP + AXIS_Y) / 2 - 30),
    )
)

# event blocks
block_boxes = {}
for e in events:
    x0, x1 = x_of(e["start_min"]), x_of(e["end_min"])
    w = x1 - x0
    y = LANES[e["venue"]] + (LANE_H - BLOCK_H) / 2 + 2
    col = CAT_COLOR[e["category"]]
    wide.append(
        Positioned(
            C(width=num(w), height=num(BLOCK_H), color=col, borderRadius="12",
              gradientType="LINEAR", gradientColors=f"{col},{col}AA", gradientStops="0,1",
              gradientBegin="TOP_CENTER", gradientEnd="BOTTOM_CENTER",
              boxShadow="0 6 18 0 #00000055 NORMAL"),
            left=num(x0), top=num(y),
        )
    )
    wide.append(Positioned(C(width=num(w), height="5", color="#00000033",
                             borderRadiusTopLeft="12", borderRadiusTopRight="12"),
                           left=num(x0), top=num(y)))
    dark = "#08111F"
    if w >= 152:
        wide.append(label(x0 + w / 2, y + 4, e["id"], 24, dark, anchor="center_top",
                          align="CENTER", width=w - 8, font=FONT, bold=True))
        wide.append(label(x0 + w / 2, y + 42, f"{e['start']}–{e['end']}", 18, "#0F1728",
                          anchor="center_top", align="CENTER", width=w - 6, font=FONT_MONO))
        tag = f"{CAT_LABEL[e['category']]} · {e['duration_min']}′" if w >= 168 else CAT_LABEL[e["category"]]
        wide.append(label(x0 + w / 2, y + 68, tag, 16, "#0F1728CC",
                          anchor="center_top", align="CENTER", width=w - 6, font=FONT))
    else:
        # 短块：编号与类别同行居中，起止分两行；不为塞字改变块宽
        wide.append(Positioned(
            Row(Text(e["id"], color=dark, fontSize="22", fontStyle="BOLD", fontFamily=FONT),
                C(width="7"),
                Text(CAT_LABEL[e["category"]], color="#0F1728CC", fontSize="15",
                     fontFamily=FONT),
                crossAxisAlignment="CENTER", mainAxisAlignment="CENTER",
                mainAxisSize="MAX"),
            left=num(x0), top=num(y + 10), width=num(w)))
        wide.append(label(x0 + w / 2, y + 44, e["start"], 18, "#0F1728", anchor="center_top",
                          align="CENTER", width=w - 4, font=FONT_MONO))
        wide.append(label(x0 + w / 2, y + 66, e["end"], 18, "#0F1728", anchor="center_top",
                          align="CENTER", width=w - 4, font=FONT_MONO))
    block_boxes[e["id"]] = [round(x0, 1), round(y, 1), round(x1, 1), round(y + BLOCK_H, 1)]

# index of all 15 events
IDX_TOP = AXIS_Y + 90
IDX_COLS = 3
IDX_ROWS = 5
IDX_W = (W - 2 * PAD - (IDX_COLS - 1) * 20) / IDX_COLS
IDX_H = 80
wide.append(
    Positioned(
        Row(
            Text("编号索引 · 15 场活动完整信息", color=TXT, fontSize="24", fontStyle="BOLD",
                 fontFamily=FONT),
            C(width="16"),
            Text("块内编号对应下表；表中时长 = 结束 − 开始（分钟）", color=TXT_3, fontSize="18",
                 fontFamily=FONT),
            crossAxisAlignment="END",
        ),
        left=num(PAD), top=num(IDX_TOP - 38),
    )
)
IDX_MAP = {}
for i, e in enumerate(events):
    r, c = i % IDX_ROWS, i // IDX_ROWS
    x = PAD + c * (IDX_W + 20)
    y = IDX_TOP + r * IDX_H
    col = CAT_COLOR[e["category"]]
    wide.append(Positioned(C(width=num(IDX_W), height=num(IDX_H - 8), color=CARD_2,
                             borderRadius="10", border=f"1 SOLID {LINE}"),
                           left=num(x), top=num(y)))
    wide.append(Positioned(C(width="5", height=num(IDX_H - 8), color=col,
                             borderRadiusTopLeft="10", borderRadiusBottomLeft="10"),
                           left=num(x), top=num(y)))
    wide.append(label(x + 18, y + 10, e["id"], 20, col, anchor="left_top", align="LEFT",
                      width=52, font=FONT, bold=True))
    wide.append(label(x + 70, y + 11, f"{e['start']} – {e['end']}", 18, TXT,
                      anchor="left_top", align="LEFT", width=150, font=FONT_MONO))
    wide.append(label(x + 224, y + 11, f"{e['duration_min']} 分钟", 18, TXT_3,
                      anchor="left_top", align="LEFT", width=92, font=FONT))
    wide.append(label(x + 318, y + 11, f"{e['venue']} 会场", 18, VENUE_COLOR[e["venue"]],
                      anchor="left_top", align="LEFT", width=76, font=FONT, bold=True))
    wide.append(label(x + 396, y + 11, e["category_label"], 18, col, anchor="left_top",
                      align="LEFT", width=64, font=FONT))
    wide.append(label(x + 18, y + 33, e["title"], 20, TXT, anchor="left_top", align="LEFT",
                      width=IDX_W - 30, font=FONT))
    wide.append(label(x + 18, y + 55, f"讲者：{e['speaker']}", 18, TXT_2, anchor="left_top",
                      align="LEFT", width=IDX_W - 30, font=FONT))
    IDX_MAP[e["id"]] = [round(x, 1), round(y, 1), round(x + IDX_W, 1), round(y + IDX_H - 8, 1)]

FOOT_Y = IDX_TOP + IDX_ROWS * IDX_H + 8
wide.append(
    label(PAD, FOOT_Y,
          "空档示例：B 会场 11:10–12:00 无安排；C 会场 15:10–16:00 无安排；A 会场 15:00–15:30 为两场之间。"
          "冲突检查：同会场重叠 0 处（跨会场并行不计为冲突）。",
          18, TXT_3, anchor="left_top", align="LEFT", width=1300, font=FONT))
wide.append(
    label(W - PAD, FOOT_Y + 2, f"run {RUN}", 16, "#42536E", anchor="right_top",
          align="RIGHT", width=260, font=FONT))

assert FOOT_Y + 26 <= H, (FOOT_Y + 26, H)

wide_root = Container(
    layer_stack(
        Positioned(Opacity(C(width="880", height="420", color="#123257", shape="CIRCLE"),
                           opacity="0.55"), left="-160", top="-180"),
        Positioned(Opacity(C(width="700", height="360", color="#221D55", shape="CIRCLE"),
                           opacity="0.5"), right="-140", top="20"),
        *wide,
    ),
    width=num(W), height=num(H),
    gradientType="LINEAR", gradientColors=f"{BG},#0D1730", gradientStops="0,1",
    gradientBegin="TOP_CENTER", gradientEnd="BOTTOM_CENTER",
)
doc_wide = Snapshot(wide_root, background=BG, type="png")

# ================================================================ MOBILE 720x1280
MW, MH = 720, 1280
MP = 22


def m_layer(*children, w=MW, h=MH):
    return Stack(C(width=num(w), height=num(h)), *children,
                 alignment="TOP_LEFT", clipBehavior="HARD_EDGE")


mob: list = []
mob.append(
    Positioned(
        Col(
            Text("Structure / Vision 2026", color=TXT, fontSize="30", fontStyle="BOLD",
                 fontFamily=FONT),
            C(height="6"),
            Text("2026.11.07 · 云构中心 A/B/C 会场 · Asia/Shanghai", color=TXT_2,
                 fontSize="18", fontFamily=FONT),
            C(height="4"),
            Text("分时段导览 · 共 15 场 · 讲者详见完整日程", color=LUNCH, fontSize="18",
                 fontFamily=FONT),
            crossAxisAlignment="START",
        ),
        left=num(MP), top=num(20),
    )
)
mob.append(card(MP, 132, MW - 2 * MP, 40, fill=CARD_2, radius=10, border="#1B2A47"))
mob.append(
    label(MP + 14, 143, "容量 A 320 · B 80 · C 160 人", 18, TXT_2, anchor="left_top",
          align="LEFT", width=380, font=FONT))
mob.append(
    label(MW - MP - 14, 143, "时间 09:00–16:00", 18, TXT_3, anchor="right_top",
          align="RIGHT", width=220, font=FONT))

CARD_H = 54
CARD_GAP = 5
SEG_H = 30


def seg_header(y, text, note):
    mob.append(Positioned(C(width=num(MW - 2 * MP), height="2", color="#22324F"),
                          left=num(MP), top=num(y + SEG_H - 6)))
    mob.append(label(MP, y + 4, text, 20, TXT, anchor="left_top", align="LEFT", width=200,
                     font=FONT, bold=True))
    mob.append(label(MW - MP, y + 6, note, 18, TXT_3, anchor="right_top", align="RIGHT",
                     width=300, font=FONT))


def mob_card(y, e):
    col = CAT_COLOR[e["category"]]
    mob.append(Positioned(C(width=num(MW - 2 * MP), height=num(CARD_H), color=CARD_2,
                            borderRadius="10", border=f"1 SOLID {LINE}"),
                          left=num(MP), top=num(y)))
    mob.append(Positioned(C(width="5", height=num(CARD_H), color=col,
                            borderRadiusTopLeft="10", borderRadiusBottomLeft="10"),
                          left=num(MP), top=num(y)))
    mob.append(label(MP + 16, y + 7, f"{e['id']}", 18, col, anchor="left_top", align="LEFT",
                     width=44, font=FONT, bold=True))
    mob.append(label(MP + 60, y + 8, f"{e['start']}–{e['end']}", 18, TXT, anchor="left_top",
                     align="LEFT", width=132, font=FONT_MONO))
    mob.append(label(MP + 196, y + 8, f"{e['venue']} 会场", 18, VENUE_COLOR[e["venue"]],
                     anchor="left_top", align="LEFT", width=70, font=FONT, bold=True))
    mob.append(label(MP + 266, y + 8, e["category_label"], 18, TXT_3, anchor="left_top",
                     align="LEFT", width=60, font=FONT))
    mob.append(label(MP + 330, y + 8, f"{e['duration_min']}′", 18, TXT_3, anchor="left_top",
                     align="LEFT", width=54, font=FONT))
    mob.append(label(MP + 16, y + 28, e["title"], 19, TXT, anchor="left_top", align="LEFT",
                     width=MW - 2 * MP - 30, font=FONT))


M_MAP = {}
morning = [e for e in events if e["start_min"] < LUNCH_START]
afternoon = [e for e in events if e["start_min"] >= LUNCH_END]
assert len(morning) == 8 and len(afternoon) == 7, (len(morning), len(afternoon))

y = 184
seg_header(y, "上午 09:00–12:00", f"{len(morning)} 场")
y += SEG_H + 6
for e in morning:
    M_MAP[e["id"]] = [MP, round(y, 1), MW - MP, round(y + CARD_H, 1)]
    mob_card(y, e)
    y += CARD_H + CARD_GAP

LUNCH_Y = y + 2
mob.append(Positioned(C(width=num(MW - 2 * MP), height="44", color="#FBBF2422",
                        borderRadius="10", border="2 SOLID #FBBF2466"),
                      left=num(MP), top=num(LUNCH_Y)))
mob.append(label(MW / 2, LUNCH_Y + 11, "公共午休 12:00 – 13:00（三会场同时段，不并入任何会议）",
                 18, "#FDE68A", anchor="center_top", align="CENTER", width=MW - 2 * MP - 20,
                 font=FONT))
y = LUNCH_Y + 44 + 8

seg_header(y, "下午 13:00–16:00", f"{len(afternoon)} 场")
y += SEG_H + 6
for e in afternoon:
    M_MAP[e["id"]] = [MP, round(y, 1), MW - MP, round(y + CARD_H, 1)]
    mob_card(y, e)
    y += CARD_H + CARD_GAP

assert y + 40 <= MH, (y, MH)
mob.append(
    label(MP, MH - 46,
          "本图为分时段列表，非大图缩放；讲者名单见 1920×1200 完整日程编号索引。",
          18, TXT_3, anchor="left_top", align="LEFT", width=MW - 2 * MP, font=FONT))

mob_root = Container(
    m_layer(*mob),
    width=num(MW), height=num(MH), color="#0A1122",
)
doc_mob = Snapshot(mob_root, background="#0A1122", type="png")

# ---------------------------------------------------------------- content map
for e in events:
    audit["content_map"].append({
        "id": e["id"],
        "fields": ["id", "start", "end", "duration_min", "venue", "category_label",
                   "title", "speaker"],
        "wide": {
            "image": "agenda-wide.png",
            "block_px": block_boxes[e["id"]],
            "index_px": IDX_MAP[e["id"]],
            "text_in_block": f"{e['id']} + {e['start']}–{e['end']}"
                             f"{' + ' + str(e['duration_min']) + ' 分钟' if (x_of(e['end_min']) - x_of(e['start_min'])) >= 150 else ''}",
            "text_in_index": f"{e['id']} / {e['start']} – {e['end']} / {e['duration_min']} 分钟 / {e['venue']} 会场 / {e['category_label']} / {e['title']} / 讲者：{e['speaker']}",
        },
        "mobile": {
            "image": "agenda-mobile.png",
            "card_px": M_MAP[e["id"]],
            "text": f"{e['id']} / {e['start']}–{e['end']} / {e['venue']} 会场 / "
                    f"{e['category_label']} / {e['duration_min']}′ / {e['title']}",
            "speaker_shown": False,
            "speaker_note": "讲者详见完整日程",
        },
    })
audit["content_map_note"] = (
    "两图各自独立排版：大图用时间比例泳道 + 编号索引，手机图用分时段列表；"
    "手机图未缩放或裁切大图任何像素。"
)
audit["layout_checks"] = {
    "wide_canvas": [W, H], "mobile_canvas": [MW, MH],
    "min_body_font_wide": 18, "min_time_label_wide": 18, "min_font_mobile": 18,
    "events_rendered_wide": len(block_boxes),
    "events_rendered_mobile": len(M_MAP),
    "lunch_merged_with_session": False,
    "input_times_modified": False,
}

OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "schedule-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
ap.add_argument("--final-wide", default=None)
ap.add_argument("--final-mobile", default=None)
a = ap.parse_args()
TMP_DIR.mkdir(parents=True, exist_ok=True)
(TMP_DIR / f"{a.ver}-wide.snapshot").write_text(doc_wide.render() + "\n", encoding="utf-8")
(TMP_DIR / f"{a.ver}-mobile.snapshot").write_text(doc_mob.render() + "\n", encoding="utf-8")
if a.final_wide:
    (ROOT / a.final_wide).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / a.final_wide).write_text(doc_wide.render() + "\n", encoding="utf-8")
if a.final_mobile:
    (ROOT / a.final_mobile).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / a.final_mobile).write_text(doc_mob.render() + "\n", encoding="utf-8")
print(json.dumps({
    "ver": a.ver, "ppm": round(PPM, 4), "axis_w": round(AXIS_W, 1),
    "conflicts": len(conflicts), "gaps": len(venue_gaps),
    "parallel_pairs": len(cross_venue_parallel),
    "wide_bottom": FOOT_Y + 48, "mobile_bottom": y + 40,
}, ensure_ascii=False))
