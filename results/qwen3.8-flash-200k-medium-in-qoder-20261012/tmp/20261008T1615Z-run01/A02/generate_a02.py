"""A02 generator: 1920x1200 three-venue swimlane agenda + 720x1280 mobile guide.

All geometry is derived from inputs/agenda.csv; nothing is re-timed by hand.
Previews go to the temp directory; only the promoted version is copied to outputs/.
"""
import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
from dslkit import Doc, GRAD_NIGHT, minutes  # noqa: E402

TASK = "A02"
IN_DIR = ROOT / "tasks" / "A02-conference-schedule" / "inputs"
TEMP = ROOT / "tmp" / RID / TASK
OUT = ROOT / "outputs" / RID / TASK
VERSION = os.environ.get("DSL_VERSION", "v01")

DAY_START, DAY_END = minutes("09:00"), minutes("16:00")
LUNCH = (minutes("12:00"), minutes("13:00"))

CAT_LABEL = {"keynote": "主旨", "workshop": "工作坊", "talk": "分享",
             "demo": "演示", "panel": "圆桌"}
CAT_COLOR = {"keynote": "#FBBF24", "workshop": "#38BDF8", "talk": "#A78BFA",
             "demo": "#34D399", "panel": "#F472B6"}


def load():
    with open(IN_DIR / "agenda.csv", encoding="utf-8-sig", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("id")]
    venues = json.loads((IN_DIR / "venues.json").read_text(encoding="utf-8"))
    for r in rows:
        r["s"], r["e"] = minutes(r["start"]), minutes(r["end"])
        r["dur"] = r["e"] - r["s"]
    rows.sort(key=lambda r: (r["s"], r["venue"]))
    return rows, venues


def audit(rows, venues):
    by_venue = {}
    for r in rows:
        by_venue.setdefault(r["venue"], []).append(r)
    conflicts, venues_out = [], {}
    for v in sorted(by_venue):
        items = sorted(by_venue[v], key=lambda r: r["s"])
        gaps = []
        for a, b in zip(items, items[1:]):
            if b["s"] < a["e"]:
                conflicts.append({"venue": v, "pair": [a["id"], b["id"]],
                                  "overlap_minutes": a["e"] - b["s"]})
            elif b["s"] > a["e"]:
                g = {"from": a["end"], "to": b["start"],
                     "minutes": b["s"] - a["e"]}
                if a["e"] < LUNCH[0] and b["s"] > LUNCH[1]:
                    g["spans_lunch"] = True
                elif a["e"] < LUNCH[0] and b["s"] >= LUNCH[1]:
                    g["includes_lunch"] = True
                gaps.append(g)
        free = []
        if items[0]["s"] > DAY_START:
            free.append({"from": "09:00", "to": items[0]["start"],
                         "minutes": items[0]["s"] - DAY_START})
        if items[-1]["e"] < DAY_END:
            free.append({"from": items[-1]["end"], "to": "16:00",
                         "minutes": DAY_END - items[-1]["e"]})
        venues_out[v] = {
            "capacity": venues[v]["capacity"],
            "session_count": len(items),
            "session_minutes": sum(i["dur"] for i in items),
            "first_start": items[0]["start"],
            "last_end": items[-1]["end"],
            "gaps_between_sessions": gaps,
            "idle_before_first": free[0] if free and free[0]["to"] == items[0]["start"] else None,
            "idle_after_last": free[-1] if free and free[-1]["from"] == items[-1]["end"] else None,
        }
    return {
        "date": "2026-11-07",
        "timezone": "Asia/Shanghai",
        "venue_group": "云构中心 · A / B / C 会场",
        "timeline": {"axis_start": "09:00", "axis_end": "16:00",
                     "axis_minutes": DAY_END - DAY_START},
        "public_lunch": {"start": "12:00", "end": "13:00", "minutes": 60,
                         "rendering": "cross-lane band, never merged into a session",
                         "sessions_overlapping_lunch": [r["id"] for r in rows
                                                        if r["s"] < LUNCH[1] and r["e"] > LUNCH[0]]},
        "sessions": [{
            "id": r["id"], "venue": r["venue"], "start": r["start"], "end": r["end"],
            "duration_minutes": r["dur"], "title": r["title"], "speaker": r["speaker"],
            "category": r["category"], "category_label": CAT_LABEL[r["category"]],
            "axis_offset_minutes": r["s"] - DAY_START,
            "wide_block_px": round(r["dur"] * PX_PER_MIN, 1),
            "narrow_block": r["dur"] * PX_PER_MIN < 150,
        } for r in rows],
        "venues": venues_out,
        "conflict_check": {
            "same_venue_overlaps": conflicts,
            "method": "sorted by start within each venue; overlap if next.start < prev.end",
            "conclusion": ("no same-venue overlap in inputs" if not conflicts
                           else f"{len(conflicts)} overlap(s) found in inputs"),
            "parallel_sessions_max": max_parallel(rows),
        },
        "image_content_mapping": {
            "agenda-wide.png": {
                "canvas": "1920x1200",
                "carries": ["swimlane blocks (position+width strictly proportional to real times)",
                            "hour axis 09:00-16:00", "visible gaps",
                            "public lunch cross-lane band",
                            "numbered index of all 15 sessions (id/title/venue/time/category/speaker)",
                            "venue capacities", "reading instructions"],
                "text_floor_px": 18,
            },
            "agenda-mobile.png": {
                "canvas": "720x1280",
                "layout": "time-segmented vertical list, not a scaled/cropped wide chart",
                "segments": {"morning": "09:00-12:00", "public_lunch": "12:00-13:00",
                             "afternoon": "13:00-16:00"},
                "carries": ["all 15 session ids", "titles", "venue", "start-end",
                            "category", "duration", "public lunch entry",
                            "explicit note that speakers live in the wide chart"],
                "omits": ["speaker names"],
                "omit_note_rendered": "讲者详见完整日程",
                "text_floor_px": 18,
            },
            "shared_ids": sorted(r["id"] for r in rows),
            "lunch_in_both": True,
            "duration_source_identical": True,
        },
    }


def max_parallel(rows):
    marks = []
    for r in rows:
        marks.append((r["s"], 1))
        marks.append((r["e"], -1))
    marks.sort()
    cur = best = 0
    for _, d in marks:
        cur += d
        best = max(best, cur)
    return best


# ---------------------------------------------------------------- wide layout
W, H = 1920, 1200
LX, RX = 300.0, 1860.0
PX_PER_MIN = (RX - LX) / (DAY_END - DAY_START)
LANE_TOP = 208.0
LANE_H = 178.0
LANE_GAP = 4.0
VIEWS = ["A", "B", "C"]
LANE_COLOR = {"A": "#38BDF8", "B": "#FBBF24", "C": "#34D399"}
IDX_Y, IDX_H, ROW_H = 758.0, 380.0, 60.0
NARROW_PX = 150.0


def tx(t):
    return LX + (t - DAY_START) * PX_PER_MIN


def build_wide(rows, venues):
    d = Doc(W, H, palette={"band": "#16233D"})
    lane_bot = LANE_TOP + 3 * LANE_H + 2 * LANE_GAP
    # header
    d.label(40, 20, 900, 40, "Structure / Vision 2026 · 全日日程", "#F1F5F9", 34, "BOLD")
    d.label(40, 62, 900, 24, "2026.11.07 星期六 · 云构中心 A / B / C 会场 · 时间均为 Asia/Shanghai",
            "#A9B8D0", 20)
    d.rect(1500, 22, 380, 60, "#0E183088", 12)
    d.label(1516, 30, 348, 22, "15 场活动 · 3 会场 · 09:00–16:00 线性轴", "#38BDF8", 18, "BOLD")
    d.label(1516, 54, 348, 22, "块宽 = 实际时长 × 3.714 px/min", "#7A8AA6", 18)
    d.rect(40, 90, 1840, 2, "#1E2E4F")

    # reading instructions (one line each, no wrap collision)
    d.label(40, 98, 200, 26, "读图方法", "#F1F5F9", 20, "BOLD")
    d.label(150, 98, 1730, 26,
            "横向 09:00–16:00 线性时间轴：块的左右位置与宽度按 agenda.csv 真实起止时间等比例绘制，未为塞字放大任何时段。",
            "#A9B8D0", 20)
    d.label(40, 126, 1840, 24,
            "纵向三条泳道 = A/B/C 会场；同泳道相邻块之间的空白即真实空档。灰蓝色整高横带是 12:00–13:00 公共午休，跨三泳道、独立成带，不并入任何会议。",
            "#8FA3C0", 18)
    d.label(40, 150, 1840, 24,
            "空白中的灰色数字 = 该空档分钟数（≥20 分钟标注，跨午休空档按午休前后分段计）；块左侧竖色条与编号底色表示类别；"
            "30–35 分钟短场的完整编号、标题、会场、起止、类别与讲者见下方“编号索引”。",
            "#8FA3C0", 18)

    # axis
    ay = 176
    for t in range(DAY_START, DAY_END + 1, 60):
        x = tx(t)
        d.label(x - 42, ay, 84, 24, f"{t // 60:02d}:00", "#94A3B8", 18, align="CENTER")
        d.line(x, 204, x, lane_bot + 4, 1, "#1E2E4F")
    d.rect(LX, ay + 26, RX - LX, 2, "#3A4C70")

    # lane header cards
    for i, v in enumerate(VIEWS):
        top = LANE_TOP + i * (LANE_H + LANE_GAP)
        items = sorted([r for r in rows if r["venue"] == v], key=lambda r: r["s"])
        gaps = [(a["e"], b["s"]) for a, b in zip(items, items[1:]) if b["s"] > a["e"]]
        if items[0]["s"] > DAY_START:
            gaps.insert(0, (DAY_START, items[0]["s"]))
        if items[-1]["e"] < DAY_END:
            gaps.append((items[-1]["e"], DAY_END))
        gap_min = sum(b - a for a, b in gaps)
        d.rect(40, top, 244, LANE_H, "#0E1830", 12)
        d.rect(40, top, 6, LANE_H, LANE_COLOR[v], 3)
        d.label(58, top + 12, 210, 32, f"{v} 会场", "#F1F5F9", 26, "BOLD")
        d.label(58, top + 48, 210, 22, f"容量 {venues[v]['capacity']} 人", "#A9B8D0", 18)
        d.label(58, top + 72, 210, 22,
                f"{len(items)} 场 · 共 {sum(r['dur'] for r in items)} 分钟", "#7A8AA6", 18)
        d.label(58, top + 96, 210, 22, f"空档 {len(gaps)} 段 · {gap_min} 分钟",
                "#6B7E9C", 18)
        d.label(58, top + 122, 210, 22,
                f"{items[0]['start']} 起 · {items[-1]['end']} 止", "#5C6E8C", 18)

    # public lunch band (behind blocks, spans all three lanes)
    lx0, lx1 = tx(LUNCH[0]), tx(LUNCH[1])
    d.rect(lx0, LANE_TOP, lx1 - lx0, lane_bot - LANE_TOP, "#243450", 10)
    d.rect(lx0, LANE_TOP, lx1 - lx0, 3, "#94A3B8")
    d.rect(lx0, lane_bot - 3, lx1 - lx0, 3, "#94A3B8")
    d.label(lx0, LANE_TOP + 6, lx1 - lx0, 30, "公共午休", "#F1F5F9", 24, "BOLD", align="CENTER")
    d.label(lx0, LANE_TOP + 36, lx1 - lx0, 24, "12:00–13:00 · 60 分钟", "#CBD5E1", 20,
            align="CENTER")
    d.label(lx0, LANE_TOP + 62, lx1 - lx0, 24, "跨 A / B / C 三泳道", "#94A3B8", 18,
            align="CENTER")
    d.label(lx0, LANE_TOP + 86, lx1 - lx0, 24, "独立时段，不并入会议", "#94A3B8", 18,
            align="CENTER")

    # gap annotations (a gap that crosses the public lunch is split around it)
    def split_around_lunch(g0, g1):
        if g0 >= LUNCH[1] or g1 <= LUNCH[0]:
            return [(g0, g1)]
        out = []
        if g0 < LUNCH[0]:
            out.append((g0, min(g1, LUNCH[0])))
        if g1 > LUNCH[1]:
            out.append((max(g0, LUNCH[1]), g1))
        return [(a, b) for a, b in out if b > a]

    for i, v in enumerate(VIEWS):
        top = LANE_TOP + i * (LANE_H + LANE_GAP)
        items = sorted([r for r in rows if r["venue"] == v], key=lambda r: r["s"])
        pairs = [(None, items[0])] + list(zip(items, items[1:])) + [(items[-1], None)]
        for a, b in pairs:
            g0 = DAY_START if a is None else a["e"]
            g1 = DAY_END if b is None else b["s"]
            for s0, s1 in split_around_lunch(g0, g1):
                if s1 - s0 < 20:
                    continue
                x0, gw = tx(s0), (s1 - s0) * PX_PER_MIN
                d.label(x0 + gw / 2 - 40, top + LANE_H / 2 - 12, 80, 24,
                        f"{s1 - s0} 分", "#4E6080", 18, align="CENTER")

    # session blocks
    for r in rows:
        i = VIEWS.index(r["venue"])
        top = LANE_TOP + i * (LANE_H + LANE_GAP)
        x0, bw = tx(r["s"]), r["dur"] * PX_PER_MIN
        c = CAT_COLOR[r["category"]]
        narrow = bw < NARROW_PX
        o = d.origin(x0, top)
        o.rect(0, 8, bw, LANE_H - 16, "#12203A", 10)
        o.rect(0, 8, 5, LANE_H - 16, c, 2)
        o.pos(0, 8, bw, LANE_H - 16, d.box(bw, LANE_H - 16, radius=10,
                                          border=f"1 SOLID {c}66"))
        o.chip(12, 14 if narrow else 20, 50, 26, r["id"], "#060B18", c, 18)
        cat = CAT_LABEL[r["category"]]
        if bw - 78 >= len(cat) * 18 + 4:
            o.label(68, 14 if narrow else 20, bw - 78, 26, cat, c, 18, "BOLD")
        if narrow:
            o.label(12, 44, bw - 20, 22, r["start"], "#E2E8F0", 18, "BOLD", valign="TOP")
            o.label(12, 66, bw - 20, 22, f"– {r['end']}", "#E2E8F0", 18, "BOLD", valign="TOP")
            ty = 92
        else:
            o.label(12, 52, bw - 20, 24, f"{r['start']}–{r['end']}", "#E2E8F0", 19, "BOLD",
                    valign="TOP")
            ty = 82
        o.label(12, ty, bw - 20, 52, r["title"], "#F1F5F9", 20, maxlines=2, valign="TOP")
        sp = f"{r['speaker']} · {r['dur']}min" if bw >= 190 else r["speaker"]
        o.label(12, LANE_H - 32, bw - 20, 24, sp, "#8FA3C0", 18)

    # numbered index
    iy = IDX_Y
    d.rect(40, iy, 1840, IDX_H, "#0C162C", 14)
    d.label(60, iy + 12, 500, 26, "编号索引 · 15 场活动全量信息", "#F1F5F9", 22, "BOLD")
    d.label(60, iy + 40, 1760, 22,
            "S 编号对应泳道块；此表保证短场同样完整可读，不因块宽不足而省略标题、起止、类别或讲者。",
            "#7A8AA6", 18)
    colw, x0i, y0i = 606.0, 60, iy + 70
    for idx, r in enumerate(sorted(rows, key=lambda r: r["id"])):
        col, row = idx // 5, idx % 5
        x = x0i + col * colw
        y = y0i + row * ROW_H
        c = CAT_COLOR[r["category"]]
        d.rect(x, y + 3, 586, 50, "#101D36", 8)
        d.rect(x, y + 3, 4, 50, c, 2)
        d.label(x + 12, y + 6, 54, 22, r["id"], c, 18, "BOLD")
        d.label(x + 66, y + 6, 130, 22, f"{r['start']}–{r['end']}", "#E2E8F0", 18)
        d.label(x + 198, y + 6, 60, 22, f"{r['venue']} 会场", "#A9B8D0", 18)
        d.label(x + 258, y + 6, 90, 22, CAT_LABEL[r["category"]], c, 18)
        d.label(x + 350, y + 6, 236, 22, f"{r['dur']} 分钟", "#7A8AA6", 18, align="END")
        d.label(x + 12, y + 28, 350, 22, r["title"], "#F1F5F9", 19)
        d.label(x + 370, y + 28, 216, 22, r["speaker"], "#8FA3C0", 18, align="END")

    # legend + footer
    fy = 1148
    d.label(40, fy + 4, 120, 22, "类别图例", "#F1F5F9", 18, "BOLD")
    lx = 160
    for k in ["keynote", "workshop", "talk", "demo", "panel"]:
        d.rect(lx, fy + 8, 18, 14, CAT_COLOR[k], 4)
        d.label(lx + 24, fy + 2, 76, 24, CAT_LABEL[k], "#A9B8D0", 18)
        lx += 106
    d.label(lx + 10, fy + 2, 760, 24,
            "数据源 tasks/A02-conference-schedule/inputs/agenda.csv（时间与场地未修改）",
            "#5C6E8C", 18)
    d.label(1500, fy + 2, 380, 24, "A02 · agenda-wide · 1920×1200", "#7A8AA6", 18,
            align="END")
    return d.dsl(GRAD_NIGHT)


# -------------------------------------------------------------- mobile layout
MW, MH = 720, 1280


def build_mobile(rows, venues):
    d = Doc(MW, MH, palette={})
    d.rect(0, 0, MW, 92, "#0C1730")
    d.label(24, 12, 470, 32, "Structure / Vision 2026", "#F1F5F9", 26, "BOLD")
    d.label(24, 48, 470, 22, "手机导览 · 分时段日程", "#A9B8D0", 19)
    d.rect(500, 14, 196, 64, "#101D36", 10)
    d.label(508, 22, 180, 20, "2026.11.07", "#38BDF8", 18, "BOLD", align="CENTER")
    d.label(508, 46, 180, 20, "Asia/Shanghai", "#7A8AA6", 18, align="CENTER")
    d.rect(0, 92, MW, 2, "#1E2E4F")
    d.label(24, 100, 400, 22, "云构中心 A / B / C 会场", "#A9B8D0", 18)
    d.label(300, 100, 396, 22, "讲者详见完整日程", "#FBBF24", 18, align="END")

    def seg(y, label, sub):
        d.rect(24, y, MW - 48, 30, "#0E1830", 8)
        d.rect(24, y, 4, 30, "#38BDF8", 2)
        d.label(38, y + 3, 260, 24, label, "#F1F5F9", 19, "BOLD")
        d.label(290, y + 3, 398, 24, sub, "#7A8AA6", 18, align="END")
        return y + 38

    def item(y, r):
        c = CAT_COLOR[r["category"]]
        d.rect(24, y, MW - 48, 56, "#101D36", 10)
        d.rect(24, y, 5, 56, c, 2)
        d.chip(36, y + 7, 48, 22, r["id"], "#060B18", c, 18)
        d.label(90, y + 3, 150, 24, f"{r['start']}–{r['end']}", "#E2E8F0", 19, "BOLD")
        d.label(240, y + 3, 100, 24, f"{r['venue']} 会场", "#A9B8D0", 18)
        d.label(338, y + 3, 180, 24, f"{r['dur']} 分钟", "#7A8AA6", 18)
        d.label(524, y + 3, 164, 24, CAT_LABEL[r["category"]], c, 18, "BOLD", align="END")
        d.label(36, y + 28, 652, 26, r["title"], "#F1F5F9", 20)
        return y + 62

    y = seg(132, "上午 09:00–12:00", "8 场 · 09:00 起")
    for r in rows:
        if r["s"] < LUNCH[0]:
            y = item(y, r)
    d.rect(24, y, MW - 48, 46, "#243450", 10)
    d.rect(24, y, 5, 46, "#94A3B8", 2)
    d.label(38, y + 4, 220, 22, "公共午休", "#F1F5F9", 20, "BOLD")
    d.label(38, y + 24, 220, 20, "12:00–13:00 · 60 分", "#CBD5E1", 18)
    d.label(266, y + 11, 422, 24, "独立时段，不与会议合并", "#94A3B8", 18, align="END")
    y += 54
    y = seg(y, "下午 13:00–16:00", "7 场 · 16:00 止")
    for r in rows:
        if r["s"] >= LUNCH[1]:
            y = item(y, r)

    d.rect(24, y + 4, MW - 48, 2, "#1E2E4F")
    d.label(24, y + 12, 672, 22,
            "列表按 agenda.csv 真实起止时间分时段排列，15 场全部保留。", "#7A8AA6", 18)
    d.label(24, y + 34, 672, 22,
            f"会场容量 A {venues['A']['capacity']} / B {venues['B']['capacity']} / "
            f"C {venues['C']['capacity']} 人。", "#7A8AA6", 18)
    assert y + 56 <= MH, f"mobile content overflows canvas: bottom={y + 56}"
    return d.dsl()


def main():
    rows, venues = load()
    audit_json = audit(rows, venues)
    TEMP.mkdir(parents=True, exist_ok=True)
    (OUT / "schedule-audit.json").parent.mkdir(parents=True, exist_ok=True)
    dsl_w = build_wide(rows, venues)
    dsl_m = build_mobile(rows, venues)
    (TEMP / f"{VERSION}-wide.snapshot").write_text(dsl_w, encoding="utf-8")
    (TEMP / f"{VERSION}-mobile.snapshot").write_text(dsl_m, encoding="utf-8")
    (TEMP / "computed-sessions.json").write_text(
        json.dumps({"sessions": rows, "venues": venues}, ensure_ascii=False,
                   indent=2, default=str), encoding="utf-8")
    (OUT / "schedule-audit.json").write_text(
        json.dumps(audit_json, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wide={len(dsl_w)} mobile={len(dsl_m)} -> {VERSION}")


if __name__ == "__main__":
    main()
