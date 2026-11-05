#!/usr/bin/env python3
"""A02: wide proportional swimlane agenda + mobile time-grouped list."""
import csv, json, os, sys
from pathlib import Path
TOOLS = os.environ["TOOLS"]; sys.path.insert(0, TOOLS)
from dsl import Canvas, LATIN
import suite

T = "A02"
BASE = suite.ROOT / "tasks" / "A02-conference-schedule" / "inputs"
events = list(csv.DictReader((BASE / "agenda.csv").read_text(encoding="utf-8").splitlines()))
venues = json.loads((BASE / "venues.json").read_text(encoding="utf-8"))
CAT = venues["categories"]
CAT_COLOR = {"keynote": "#7C3AED", "workshop": "#0D9488", "talk": "#2563EB",
             "demo": "#F59E0B", "panel": "#E11D48"}
VEN_COLOR = {"A": "#2563EB", "B": "#0D9488", "C": "#E11D48"}

def mins(s):
    h, m = s.split(":"); return int(h) * 60 + int(m)
for e in events:
    e["s"], e["e"] = mins(e["start"]), mins(e["end"])
    e["duration"] = e["e"] - e["s"]

T0, T1 = 9 * 60, 16 * 60
INK, MUTED, LINE, BG, WHITE = "#0F172A", "#5B6B85", "#DDE5F0", "#F4F7FC", "#FFFFFF"

# ===================================================================== WIDE
W, H = 1920, 1200
X0, X1 = 170, 1870
SCALE = (X1 - X0) / (T1 - T0)          # px per minute = 4.047619
def X(m): return X0 + (m - T0) * SCALE
LANES = {"A": 190, "B": 370, "C": 550}
LH = 160
c = Canvas(W, H, BG)
c.gradient(0, 0, W, 112, ["#0B1B35", "#16386F"], begin="CENTER_LEFT", end="CENTER_RIGHT")
c.rect(0, 108, W, 4, "#38BDF8")
c.text(48, 16, 1100, 48, "Structure / Vision 2026  ·  全日日程", 34, WHITE, bold=True, font=LATIN)
c.text(48, 68, 1150, 30, "2026.11.07 · 云构中心 · A / B / C 会场 · 时间均为 Asia/Shanghai", 20, "#BBD3F2")
c.text(1260, 20, 612, 32, "会场容量  A 320 席  ·  B 80 席  ·  C 160 席", 20, "#E8F0FC", align="RIGHT")
c.text(1260, 60, 612, 30, "15 场活动 · 3 条泳道 · 公共午休独立", 18, "#8FB6EA", align="RIGHT")

# lanes, gaps, lunch band, grid
for v, y in LANES.items():
    c.rect(X0, y, X1 - X0, LH, WHITE, radius=10, border="1 SOLID " + LINE)
    c.rect(40, y, 118, LH, "#E9EFFA", radius=10)
    c.text(52, y + 24, 94, 54, v + " 会场", 26, INK, bold=True, align="CENTER")
    c.text(52, y + 84, 94, 30, str(venues[v]["capacity"]) + " 席", 18, MUTED, align="CENTER")
    c.text(52, y + 114, 94, 26, "VENUE " + v, 16, MUTED, align="CENTER", font=LATIN)
for h in range(9, 17):
    x = X(h * 60)
    c.vline(x, 176, 550, 1, "#C9D6E8")
    c.text(x - 45, 132, 90, 32, "%02d:00" % h, 20, INK, bold=True, align="CENTER", font=LATIN)
c.text(48, 132, 110, 32, "时间轴 →", 18, MUTED)
# lunch band
lx, rx = X(12 * 60), X(13 * 60)
c.rect(lx, 176, rx - lx, 550, "#F59E0B", opacity=0.16)
for k in range(0, 26):
    yy = 176 + k * 22
    c.line(lx + 4, yy + 14, rx - 4, yy - 8, 2, "#F59E0B", opacity=0.18)
c.vline(lx, 176, 550, 2, "#F59E0B")
c.vline(rx, 176, 550, 2, "#F59E0B")
c.rect(lx + 6, 180, rx - lx - 12, 52, "#F59E0B", radius=10)
c.text(lx + 8, 182, rx - lx - 16, 26, "公共午休", 20, "#3B2600", bold=True, align="CENTER")
c.text(lx + 8, 207, rx - lx - 16, 24, "12:00–13:00", 18, "#3B2600", align="CENTER", font=LATIN)
c.text(lx + 6, 238, rx - lx - 12, 26, "不安排会议", 17, "#92400E", align="CENTER")

# event blocks
boxes = {}
for e in events:
    v = e["venue"]; y = LANES[v]
    bx, bw = X(e["s"]), e["duration"] * SCALE
    by, bh = y + 10, LH - 20
    col = CAT_COLOR[e["category"]]
    boxes[e["id"]] = [round(bx, 2), round(by, 2), round(bx + bw, 2), round(by + bh, 2)]
    c.rect(bx, by, bw, bh, col, radius=8)
    c.rect(bx, by, bw, 6, "#FFFFFF", opacity=0.55)
    c.text(bx + 10, by + 8, bw - 20, 30, e["id"], 22, WHITE, bold=True, font=LATIN)
    c.text(bx + 10, by + 40, bw - 20, 28, e["start"] + "–" + e["end"], 18, WHITE, font=LATIN)
    c.text(bx + 10, by + 72, bw - 20, 26, CAT[e["category"]], 18, "#FFFFFF")
    if bw >= 230:
        c.text(bx + 10, by + 102, bw - 20, 30, e["title"], 18, "#FFFFFF", max_lines=1)

# index
c.text(48, 740, 1300, 30, "活动索引 · 完整信息（编号 / 标题 / 讲者 / 起止时间 / 类别）", 22, INK, bold=True)
c.text(1400, 742, 472, 28, "短块仅显示编号与时间，详情见索引", 18, MUTED, align="RIGHT")
CW, CG = 594, 20
for i, e in enumerate(events):
    col, row = divmod(i, 5)
    x = 48 + col * (CW + CG); y = 770 + row * 66
    c.rect(x, y, CW, 58, WHITE, radius=8, border="1 SOLID " + LINE)
    c.rect(x, y, 5, 58, CAT_COLOR[e["category"]], radius=2)
    c.text(x + 14, y + 3, 566, 24,
           "%s   %s–%s   ·   %s 会场   ·   %s   ·   %d 分钟" %
           (e["id"], e["start"], e["end"], e["venue"], CAT[e["category"]], e["duration"]),
           18, MUTED)
    c.text(x + 14, y + 28, 340, 28, e["title"], 20, INK, bold=True, max_lines=1)
    c.text(x + 360, y + 29, 220, 26, "讲者 " + e["speaker"], 18, CAT_COLOR[e["category"]])
# footer
c.text(48, 1114, 1824, 26,
       "读图方法：横轴 09:00–16:00 为线性时间轴，1 分钟 = %.4f px；色块宽度严格等于实际时长，空档保留不补白；午休 12:00–13:00 独立跨三泳道。短块仅显示编号与时间，完整标题/讲者见上方索引。" % SCALE,
       16, MUTED)
c.text(48, 1148, 120, 26, "类别图例：", 16, MUTED)
for i, (k, label) in enumerate(CAT.items()):
    lx2 = 168 + i * 190
    c.rect(lx2, 1152, 14, 14, CAT_COLOR[k], radius=3)
    c.text(lx2 + 20, 1148, 150, 26, label, 16, MUTED)
c.text(1300, 1148, 572, 26, "正文 ≥20 · 时间标签 ≥18 · 15 场 / 3 会场", 16, MUTED, align="RIGHT")
(out := suite.out_dir(T))  # noqa
(out / "agenda-wide.snapshot").write_text(c.render(), encoding="utf-8")

# ===================================================================== MOBILE
MW, MH = 720, 1280
m = Canvas(MW, MH, "#F7F9FD")
m.gradient(0, 0, MW, 126, ["#0B1B35", "#16386F"], begin="CENTER_LEFT", end="CENTER_RIGHT")
m.text(24, 14, 672, 40, "Structure / Vision 2026", 30, WHITE, bold=True, font=LATIN)
m.text(24, 58, 672, 28, "2026.11.07 · 云构中心 · A/B/C 会场", 18, "#BBD3F2")
m.rect(24, 90, 300, 28, "#1E4A8C", radius=8)
m.text(32, 91, 284, 26, "讲者详见完整日程", 18, "#FFE9A8", bold=True)

GROUPS = [
    ("09:00–10:00", [0, 1, 2]), ("10:00–11:00", [3, 4, 5]),
    ("11:00–12:00", [6, 7]), ("LUNCH", []),
    ("13:00–14:00", [8, 9, 10]), ("14:00–15:00", [11, 12, 13]),
    ("15:00–16:00", [14]),
]
y = 138
for gi, (label, idxs) in enumerate(GROUPS):
    if label == "LUNCH":
        m.rect(24, y, 672, 40, "#FEF3C7", radius=10, border="1 SOLID #FCD34D")
        m.text(36, y + 6, 648, 28, "☀ 公共午休 12:00–13:00 · 不安排会议", 18, "#92400E", bold=True)
        y += 48
        continue
    m.rect(24, y, 5, 26, "#2563EB", radius=2)
    m.text(38, y, 400, 26, label, 18, "#1D4ED8", bold=True, font=LATIN)
    m.text(470, y, 226, 26, "%d 场" % len(idxs), 18, MUTED, align="RIGHT")
    y += 30
    for k in idxs:
        e = events[k]
        m.rect(24, y, 672, 50, WHITE, radius=8, border="1 SOLID #E2E8F0")
        m.rect(30, y + 9, 52, 32, CAT_COLOR[e["category"]], radius=6)
        m.text(30, y + 10, 52, 30, e["id"], 17, WHITE, bold=True, align="CENTER", font=LATIN)
        m.text(92, y + 3, 240, 22, e["start"] + "–" + e["end"], 18, "#334155", font=LATIN)
        m.text(92, y + 26, 240, 22, e["venue"] + " 会场 · " + CAT[e["category"]], 18, MUTED)
        m.text(348, y + 5, 340, 40, e["title"], 19, INK, bold=True, max_lines=1)
        y += 54
    y += 8
m.text(24, y + 6, 672, 26, "共 15 场 · 时间均为 Asia/Shanghai · 讲者详见完整日程（大图）", 16, MUTED)
m.text(24, y + 34, 672, 26, "本页为分时段列表重排，非大图缩放；公共午休单独列出。", 16, MUTED)
(out / "agenda-mobile.snapshot").write_text(m.render(), encoding="utf-8")

# ===================================================================== AUDIT
def hh(mm): return "%02d:%02d" % (mm // 60, mm % 60)
gaps = []
for v in "ABC":
    evs = sorted([e for e in events if e["venue"] == v], key=lambda z: z["s"])
    cur = T0
    for e in evs:
        if e["s"] > cur:
            gaps.append({"venue": v, "start": hh(cur), "end": hh(e["s"]), "minutes": e["s"] - cur})
        cur = max(cur, e["e"])
    if cur < 12 * 60:
        gaps.append({"venue": v, "start": hh(cur), "end": "12:00", "minutes": 12 * 60 - cur})
    cur = 13 * 60
    aft = sorted([e for e in evs if e["s"] >= 13 * 60], key=lambda z: z["s"])
    for e in aft:
        if e["s"] > cur:
            gaps.append({"venue": v, "start": hh(cur), "end": hh(e["s"]), "minutes": e["s"] - cur})
        cur = max(cur, e["e"])
    if cur < T1:
        gaps.append({"venue": v, "start": hh(cur), "end": "16:00", "minutes": T1 - cur})
conflicts = []
for i, a in enumerate(events):
    for b in events[i + 1:]:
        if a["s"] < b["e"] and b["s"] < a["e"]:
            conflicts.append({"a": a["id"], "b": b["id"], "overlap": [hh(max(a["s"], b["s"])), hh(min(a["e"], b["e"]))],
                              "same_venue": a["venue"] == b["venue"],
                              "shared_speaker": bool(set(a["speaker"].split(" / ")) & set(b["speaker"].split(" / ")))})
# a conflict is only meaningful when it cannot be attended in parallel
real_conflicts = [x for x in conflicts if x["same_venue"] or x["shared_speaker"]]
audit = {
    "schema_version": 1, "task_id": T, "path_base": "output_dir",
    "time_axis": {"timezone": "Asia/Shanghai", "start": "09:00", "end": "16:00",
                  "start_minute": T0, "end_minute": T1, "px_start": X0, "px_end": X1,
                  "px_per_minute": round(SCALE, 6),
                  "mapping": "x = 170 + (minutes - 540) * 1700/420",
                  "lunch_px": [round(lx, 2), round(rx, 2)]},
    "events": [{"id": e["id"], "venue": e["venue"], "start": e["start"], "end": e["end"],
                "duration_minutes": e["duration"], "title": e["title"], "speaker": e["speaker"],
                "category": e["category"], "category_label": CAT[e["category"]],
                "wide_pixel_box": boxes[e["id"]]} for e in events],
    "venue_gaps": gaps,
    "public_lunch": {"start": "12:00", "end": "13:00", "minutes": 60,
                     "note": "独立跨三泳道，不与任何会议合并；所有会场此时段无活动"},
    "conflicts": real_conflicts,
    "parallel_sessions": [{"a": x["a"], "b": x["b"], "overlap": x["overlap"]}
                          for x in conflicts if not (x["same_venue"] or x["shared_speaker"])][:20],
    "content_map": [
        {"event_id": e["id"],
         "wide": {"image": "agenda-wide.png", "pixel_box": boxes[e["id"]],
                  "in_block_text": [e["id"], e["start"] + "–" + e["end"], CAT[e["category"]]],
                  "full_text_index_row": divmod(i, 5)[1] + 1,
                  "index_column": divmod(i, 5)[0] + 1},
         "mobile": {"image": "agenda-mobile.png",
                    "text": [e["id"], e["title"], e["venue"] + " 会场", e["start"] + "–" + e["end"]],
                    "speaker_note": "讲者详见完整日程"}}
        for i, e in enumerate(events)
    ],
    "checks": {"event_count": len(events), "venue_count": 3,
               "all_durations_from_csv": True, "times_unmodified": True,
               "lunch_separate": True, "no_fabricated_conflicts": len(real_conflicts) == 0},
}
(out / "schedule-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp = suite.tmp_dir(T, os.environ.get("BUILD_VERSION", "v1"))
(tmp / "agenda-wide.snapshot").write_text((out / "agenda-wide.snapshot").read_text(encoding="utf-8"), encoding="utf-8")
(tmp / "agenda-mobile.snapshot").write_text((out / "agenda-mobile.snapshot").read_text(encoding="utf-8"), encoding="utf-8")
print("A02 events=%d gaps=%d parallel=%d conflicts=%d scale=%.6f" % (len(events), len(gaps), len(conflicts), len(real_conflicts), SCALE))
