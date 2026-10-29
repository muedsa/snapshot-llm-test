#!/usr/bin/env python3
"""A02 conference schedule: wide 1920x1200 + mobile 720x1280 + audit json."""
import csv, json, os, html
from pathlib import Path
from datetime import datetime, timedelta

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
TASK = "A02"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
TASK_ROOT = SUITE_ROOT / "tasks/A02-conference-schedule"

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size=20, color="#0B1220", bold=False, extra=""):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

rows = []
with (TASK_ROOT / "inputs/agenda.csv").open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s = datetime.strptime(r["start"], "%H:%M")
        e = datetime.strptime(r["end"], "%H:%M")
        d = (e - s).seconds // 60
        rows.append({**r, "sm": s.hour * 60 + s.minute, "em": e.hour * 60 + e.minute, "minutes": d})
venues = json.loads((TASK_ROOT / "inputs/venues.json").read_text(encoding="utf-8"))
CAT = venues["categories"]
COL = {"keynote": "#1D4ED8", "workshop": "#6D28D9", "talk": "#0F766E", "demo": "#B45309", "panel": "#BE185D"}
VCOL = {"A": "#2563EB", "B": "#7C3AED", "C": "#0D9488"}

# ---------------- wide 1920x1200 ----------------
W, H = 1920, 1200
x0, x1 = 250, 1880
t0, t1 = 540, 960          # 09:00 .. 16:00 in minutes
scale = (x1 - x0) / (t1 - t0)
lane_y = {"A": 225, "B": 435, "C": 645}
LANE_H = 200
BLOCK_H = 168

def xa(minutes): return x0 + (minutes - t0) * scale

parts = ['<Snapshot background="#F5F6FA" type="png">', f'<Container width="{W}" height="{H}"><Stack alignment="TOP_LEFT"><Container width="{W}" height="{H}" color="#F5F6FA"/>']
# header
parts.append('<Positioned left="50" top="36"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
parts.append(T("STRUCTURE / VISION 2026", 40, "#0B1220", True, ' letterSpacing="1.5"'))
parts.append('<SizedBox height="4"/>')
parts.append(T("全日日程 · 2026.11.07 · 云构中心 A / B / C 会场 · Asia/Shanghai", 22, "#56637A"))
parts.append('</Column></Positioned>')
parts.append('<Positioned right="50" top="42"><Row crossAxisAlignment="CENTER"><Column crossAxisAlignment="END" mainAxisSize="MIN">')
parts.append(T("09:00 — 16:00", 32, "#0B1220", True))
parts.append(T("三会场并行 · 15 场活动", 18, "#56637A"))
parts.append('</Column></Row></Positioned>')
# legend
parts.append('<Positioned left="50" top="128"><Row crossAxisAlignment="CENTER">')
for v in "ABC":
    parts.append(f'<Container width="14" height="14" color="{VCOL[v]}" borderRadius="4" margin="(0,0,8,0)"/>' + T(f"{v} 会场 · {venues[v]['capacity']} 人", 19, "#334155") + '<SizedBox width="18"/>')
parts.append('</Row></Positioned>')
parts.append('<Positioned left="620" top="128"><Row crossAxisAlignment="CENTER">')
for k in ["keynote", "workshop", "talk", "demo", "panel"]:
    parts.append(f'<Container width="12" height="12" color="{COL[k]}" shape="CIRCLE" margin="(0,0,6,0)"/>' + T(CAT[k], 18, "#56637A") + '<SizedBox width="14"/>')
parts.append('</Row></Positioned>')
parts.append('<Positioned right="50" top="128">' + T("块宽 = 实际时长 · 40 分钟 ≠ 60 分钟 · 编号对应下方索引", 18, "#56637A") + '</Positioned>')
# hour labels + grid
for h in range(9, 17):
    x = xa(h * 60)
    parts.append(f'<Positioned left="{x-36:.1f}" top="184" width="72"><Container width="72" alignment="CENTER">' + T(f"{h:02d}:00", 20, "#334155", True) + '</Container></Positioned>')
# half-hour ticks
for h in range(9, 16):
    x = xa(h * 60 + 30)
    parts.append(f'<Positioned left="{x:.1f}" top="852" width="1" height="8"><Container width="1" height="8" color="#C3CBD9"/></Positioned>')
# lane labels and tracks
for v in "ABC":
    y = lane_y[v]
    items = [r for r in rows if r["venue"] == v]
    cats = sorted(set(r["category"] for r in items))
    parts.append(f'<Positioned left="50" top="{y}"><Container width="180" height="{LANE_H}" color="#FFFFFF" borderRadius="16" border="1 SOLID #E1E6F0" padding="16"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
    parts.append(f'<Row crossAxisAlignment="CENTER"><Container width="26" height="26" color="{VCOL[v]}" borderRadius="8" alignment="CENTER">' + T(v, 18, "#FFFFFF", True) + '</Container><SizedBox width="8"/>' + T(f"{v} 会场", 25, "#0B1220", True) + '</Row>')
    parts.append('<SizedBox height="2"/>')
    parts.append(T(f"{venues[v]['capacity']} 人 · {len(items)} 场", 18, "#56637A"))
    parts.append(T(" · ".join(CAT[c] for c in cats), 16, "#8896AB"))
    parts.append('</Column></Container></Positioned>')
    parts.append(f'<Positioned left="{x0}" top="{y}" width="{x1-x0}" height="{LANE_H}"><Container width="{x1-x0}" height="{LANE_H}" color="#FFFFFF" borderRadius="16" border="1 SOLID #E1E6F0"/></Positioned>')
# grid lines above lane backgrounds
for h in range(9, 17):
    x = xa(h * 60)
    color = "#D9DFEA" if h == 9 else "#E7EBF3"
    parts.append(f'<Positioned left="{x:.1f}" top="212" width="1" height="648"><Container width="1" height="648" color="{color}"/></Positioned>')
# lunch band above lanes, below blocks
lx, lw = xa(720), (60 * scale)
parts.append(f'<Positioned left="{lx:.1f}" top="206" width="{lw:.1f}" height="654"><Container width="{lw:.1f}" height="654" color="#FFF3D6" borderLeft="1 SOLID #E9C46A" borderRight="1 SOLID #E9C46A" padding="10"><Column crossAxisAlignment="CENTER" mainAxisAlignment="CENTER">' + T("公共午休", 19, "#8A5A00", True) + T("12:00–13:00", 18, "#8A5A00") + T("三会场同步", 15, "#A97B2B") + '</Column></Container></Positioned>')

# blocks
for r in sorted(rows, key=lambda r: (r["venue"], r["sm"])):
    bx = xa(r["sm"]); bw = r["minutes"] * scale
    by = lane_y[r["venue"]] + 16
    c = COL[r["category"]]
    pad = 10
    parts.append(f'<Positioned left="{bx+2:.1f}" top="{by}" width="{bw-4:.1f}" height="{BLOCK_H}"><Container width="{bw-4:.1f}" height="{BLOCK_H}" color="{c}" borderRadius="10" padding="{pad}"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
    if bw - 4 < 160:
        parts.append(f'<Container padding="(1,7)" color="#FFFFFF2E" borderRadius="5" alignment="CENTER">' + T(r["id"], 14, "#FFFFFF", True) + '</Container>')
        parts.append('<SizedBox height="2"/>')
        parts.append(T(f'{r["start"]}–{r["end"]}', 18, "#FFFFFFDD"))
    else:
        parts.append(f'<Row crossAxisAlignment="CENTER"><Container padding="(1,7)" color="#FFFFFF2E" borderRadius="5">' + T(r["id"], 14, "#FFFFFF", True) + '</Container><SizedBox width="5"/>' + T(f'{r["start"]}–{r["end"]}', 18, "#FFFFFFDD") + '</Row>')
    parts.append('<SizedBox height="4"/>')
    parts.append(T(r["title"], 20, "#FFFFFF", True, ' maxLines="2" overflow="ELLIPSIS"' if bw - 4 < 160 else ' maxLines="3" overflow="ELLIPSIS"'))
    if bw - 4 >= 160:
        parts.append('<Spacer/>')
        parts.append(T(r["speaker"], 18, "#FFFFFFDD", False, ' maxLines="1" overflow="ELLIPSIS"'))
        parts.append('<SizedBox height="2"/>')
        parts.append(T(CAT[r["category"]], 14, "#FFFFFFAA"))
    parts.append('</Column></Container></Positioned>')
# index
IY = 858
parts.append(f'<Positioned left="50" top="{IY}"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
parts.append('<Row crossAxisAlignment="END"><' + 'Container>' + T("编号索引 / PROGRAM INDEX", 24, "#0B1220", True) + '</Container>' + '<SizedBox width="16"/>' + T("短场次文字放在索引中；讲者、类别与完整起止时间均可核对", 17, "#8896AB") + '</Row>')
parts.append('<SizedBox height="8"/>')
ordered = sorted(rows, key=lambda r: (r["sm"], r["venue"]))
half = 8
parts.append('<Row crossAxisAlignment="START">')
for col in range(2):
    items = ordered[col * half:(col + 1) * half]
    parts.append(f'<Container width="880" margin="(0,0,30,0)"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
    for i, r in enumerate(items):
        bg = "#FFFFFF" if i % 2 == 0 else "#EEF1F7"
        parts.append(f'<Container width="880" height="34" color="{bg}" padding="(0,10)"><Row crossAxisAlignment="CENTER">')
        parts.append(f'<Container width="42">' + T(r["id"], 17, COL[r["category"]], True) + '</Container>')
        parts.append(f'<Container width="330">' + T(r["title"], 19, "#0B1220", False, ' maxLines="1" overflow="ELLIPSIS"') + '</Container>')
        parts.append(f'<Container width="160">' + T(r["speaker"], 18, "#475569") + '</Container>')
        parts.append(f'<Container width="170">' + T(f'{r["start"]}–{r["end"]}', 18, "#475569") + '</Container>')
        parts.append(f'<Container width="80">' + T(CAT[r["category"]], 18, COL[r["category"]]) + '</Container>')
        parts.append(f'<Container width="80" alignment="CENTER_RIGHT">' + T(r["venue"] + " 场", 18, "#8896AB") + '</Container>')
        parts.append('</Row></Container>')
    parts.append('</Column></Container>')
parts.append('</Row>')
parts.append('</Column></Positioned>')
parts.append('</Stack></Container></Snapshot>')
wide = "\n".join(parts)
(OUT / "agenda-wide.snapshot").write_text(wide, encoding="utf-8")

# ---------------- mobile 720x1280 ----------------
MW, MH = 720, 1280
m = ['<Snapshot background="#F5F6FA" type="png">', f'<Container width="{MW}" height="{MH}"><Column crossAxisAlignment="START" mainAxisSize="MIN">']
m.append('<Container width="720" height="14" color="#0B1220"/>')
m.append('<Container width="720" padding="(24,20)"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
m.append(T("STRUCTURE / VISION", 26, "#2563EB", True, ' letterSpacing="1"'))
m.append('<SizedBox height="2"/>')
m.append(T("2026 全日导览", 30, "#0B1220", True))
m.append('<SizedBox height="4"/>')
m.append(T("2026.11.07 · 云构中心 A/B/C · Asia/Shanghai", 18, "#56637A"))
m.append('<SizedBox height="8"/>')
m.append('<Row crossAxisAlignment="CENTER"><Container padding="(4,10)" color="#E8EEFB" borderRadius="6">' + T("15 场 · 3 会场", 18, "#1D4ED8") + '</Container><SizedBox width="8"/><Container padding="(4,10)" color="#FFF3D6" borderRadius="6">' + T("午休 12:00–13:00", 18, "#8A5A00") + '</Container></Row>')
m.append(T("讲者详见完整日程 · 编号与日程大图一致", 18, "#8896AB"))
m.append('</Column></Container>')

def mobile_item(r):
    c = COL[r["category"]]
    s = f'<Container width="672" height="52" color="#FFFFFF" borderRadius="10" padding="(0,10)" borderLeft="4 SOLID {c}"><Row crossAxisAlignment="CENTER">'
    s += f'<Container width="126">' + T(f'{r["start"]}–{r["end"]}', 18, "#334155", True) + '</Container>'
    s += f'<Container width="38"><Container width="28" height="28" color="{c}22" borderRadius="8" alignment="CENTER">' + T(r["id"][1:], 16, c, True) + '</Container></Container>'
    s += f'<Expanded>' + T(r["title"], 20, "#0B1220", False, ' maxLines="1" overflow="ELLIPSIS"') + '</Expanded>'
    s += f'<Container width="80" alignment="CENTER_RIGHT"><Row crossAxisAlignment="CENTER"><Container width="8" height="8" color="{VCOL[r["venue"]]}" borderRadius="4"/><SizedBox width="5"/>' + T(r["venue"] + " 场", 18, "#334155") + '</Row></Container>'
    s += '</Row></Container>'
    return s

morning = [r for r in ordered if r["sm"] < 720]
afternoon = [r for r in ordered if r["sm"] >= 780]
m.append('<Container width="720" padding="(24,12)"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
m.append('<Row crossAxisAlignment="CENTER"><Container width="8" height="8" color="#2563EB" shape="CIRCLE"/>' + '<SizedBox width="6"/>' + T("上午 09:00–12:00", 21, "#1E293B", True) + '<SizedBox width="8"/>' + T(f"{len(morning)} 场", 17, "#8896AB") + '</Row>')
m.append('<SizedBox height="6"/>')
for r in morning:
    m.append(mobile_item(r)); m.append('<SizedBox height="4"/>')
m.append('</Column></Container>')
m.append('<Container width="672" height="54" color="#FFF3D6" borderRadius="12" margin="(0,0,0,0)" alignment="CENTER" padding="(0,24)"><Row crossAxisAlignment="CENTER">' + T("公共午休", 20, "#8A5A00", True) + '<SizedBox width="10"/>' + T("12:00–13:00 · 三会场同步", 18, "#8A5A00") + '</Row></Container>')
m.append('<Container width="720" padding="(24,14)"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
m.append('<Row crossAxisAlignment="CENTER"><Container width="8" height="8" color="#0D9488" shape="CIRCLE"/>' + '<SizedBox width="6"/>' + T("下午 13:00–16:00", 21, "#1E293B", True) + '<SizedBox width="8"/>' + T(f"{len(afternoon)} 场", 17, "#8896AB") + '</Row>')
m.append('<SizedBox height="6"/>')
for r in afternoon:
    m.append(mobile_item(r)); m.append('<SizedBox height="4"/>')
m.append('</Column></Container>')
m.append('<Spacer/>')
m.append('</Container></Snapshot>')
mobile = "\n".join(m)
(OUT / "agenda-mobile.snapshot").write_text(mobile, encoding="utf-8")

# ---------------- audit ----------------
def hhmm(minutes): return f"{minutes//60:02d}:{minutes%60:02d}"
events = []
for r in rows:
    events.append({"id": r["id"], "venue": r["venue"], "title": r["title"], "speaker": r["speaker"],
                   "category": r["category"], "category_label": CAT[r["category"]],
                   "start": r["start"], "end": r["end"], "start_minutes": r["sm"],
                   "end_minutes": r["em"], "duration_minutes": r["minutes"],
                   "wide": {"left_px": round(xa(r["sm"]), 2), "width_px": round(r["minutes"] * scale, 2),
                            "lane_top_px": lane_y[r["venue"]], "scale_px_per_minute": round(scale, 6)}})
gaps = {}
for v in "ABC":
    items = sorted([r for r in rows if r["venue"] == v], key=lambda r: r["sm"])
    g = []
    cursor = t0
    for r in items:
        if r["sm"] > cursor:
            g.append({"from": hhmm(cursor), "to": r["start"], "minutes": r["sm"] - cursor})
        cursor = max(cursor, r["em"])
    if cursor < t1:
        g.append({"from": hhmm(cursor), "to": hhmm(t1), "minutes": t1 - cursor})
    gaps[v] = g
conflicts = []
for v in "ABC":
    items = sorted([r for r in rows if r["venue"] == v], key=lambda r: r["sm"])
    for a, b in zip(items, items[1:]):
        if b["sm"] < a["em"]:
            conflicts.append({"venue": v, "a": a["id"], "b": b["id"]})
lunch_cover = all(not (r["sm"] < 780 and r["em"] > 720) for r in rows)
audit = {
    "schema_version": 1, "task_id": "A02", "path_base": "output_dir",
    "event_date": "2026-11-07", "timezone": "Asia/Shanghai",
    "venue_capacities": {v: venues[v]["capacity"] for v in "ABC"},
    "categories": CAT,
    "events": events,
    "gaps_by_venue": gaps,
    "conflicts": conflicts,
    "lunch": {"start": "12:00", "end": "13:00", "shared_across_venues": True,
              "merged_into_event": False, "no_event_overlap": lunch_cover,
              "wide_band": {"left_px": round(xa(720), 2), "width_px": round(60 * scale, 2),
                            "top_px": 206, "height_px": 654}},
    "wide_mapping": {"canvas": [W, H], "track_x_px": [x0, x1], "time_range": ["09:00", "16:00"],
                     "scale_px_per_minute": round(scale, 6), "block_height_px": BLOCK_H,
                     "min_duration_px": round(40 * scale, 2),
                     "rule": "left=250+(start-540)*scale, width=duration*scale"},
    "mobile_mapping": {"canvas": [MW, MH], "order": "start time then venue",
                       "items": [r["id"] for r in ordered], "speaker_location": "wide only",
                       "note": "讲者详见完整日程", "groups": {"morning": [r["id"] for r in morning], "afternoon": [r["id"] for r in afternoon]}},
    "content_mapping": [{"id": r["id"], "wide": "lane block + index", "mobile": "grouped list row"} for r in rows],
    "checks": {
        "all_15_events_in_wide": len(events) == 15,
        "all_15_events_in_mobile": len(ordered) == 15,
        "duration_proportional": all(abs(e["wide"]["width_px"] - e["duration_minutes"] * scale) < 0.01 for e in events),
        "conflict_count": len(conflicts),
        "lunch_not_merged": not any(r["sm"] < 780 and r["em"] > 720 for r in rows),
        "timezone_declared": "Asia/Shanghai",
    },
}
(OUT / "schedule-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote wide", len(wide), "mobile", len(mobile), "events", len(events))
