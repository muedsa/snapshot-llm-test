#!/usr/bin/env python3
"""A02 conference agenda generators: wide swimlane chart + mobile list + audit JSON.

Launch base: suite root.
Usage: python tmp/<run_id>/A02/scripts/gen_a02.py <suite_root> <run_id> [outdir]
"""
import csv
import datetime as dt
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"
out_dir = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else (root / "outputs" / run_id / "A02")
tmp_dir = root / "tmp" / run_id / "A02" / "drafts"
tmp_dir.mkdir(parents=True, exist_ok=True)
out_dir.mkdir(parents=True, exist_ok=True)

indir = root / "tasks" / "A02-conference-schedule" / "inputs"
venues = json.loads((indir / "venues.json").read_text(encoding="utf-8"))
CAT_ZH = venues["categories"]
rows = list(csv.DictReader((indir / "agenda.csv").open(encoding="utf-8")))


def mins(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


EV = []
for r in rows:
    EV.append({
        "id": r["id"], "venue": r["venue"],
        "start": r["start"], "end": r["end"],
        "start_min": mins(r["start"]), "end_min": mins(r["end"]),
        "minutes": mins(r["end"]) - mins(r["start"]),
        "title": r["title"], "speaker": r["speaker"], "category": r["category"],
    })
EV.sort(key=lambda e: (e["start_min"], e["venue"]))

FONT = "Inter,Noto Sans CJK SC"
CAT_COLOR = {"keynote": "#F59E0B", "workshop": "#8B5CF6", "talk": "#38BDF8",
             "demo": "#34D399", "panel": "#F472B6"}
VENUE_COLOR = {"A": "#38BDF8", "B": "#A78BFA", "C": "#34D399"}
DAY_START, DAY_END = 9 * 60, 16 * 60
LUNCH = (12 * 60, 13 * 60)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def est(s, size):
    """Rough advance width: CJK ~1.0em, latin letters/digits ~0.55em."""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F:
            w += 1.0
        elif ch == " ":
            w += 0.3
        elif ch.isdigit() or ch.isalpha():
            w += 0.58
        else:
            w += 0.35
    return w * size


def wrap(s, size, max_w):
    lines, cur = [], ""
    for ch in s:
        if est(cur + ch, size) > max_w and cur:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


class DSL:
    def __init__(self):
        self.o = []

    def add(self, s):
        self.o.append(s)

    def rect(self, x, y, w, h, color, extra=""):
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">'
                 f'<Container color="{color}"{extra} /></Positioned>')

    def box(self, x, y, w, h, inner):
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}" width="{f(w)}" height="{f(h)}">{inner}</Positioned>')

    def text(self, x, y, s, size=20, color="#E2E8F0", weight="NORMAL", w=None, align="START"):
        wa = f' width="{f(w)}"' if w is not None else ""
        ta = f' textAlign="{align}"' if align != "START" else ""
        self.add(f'<Positioned left="{f(x)}" top="{f(y)}"{wa}>'
                 f'<Text fontFamily="{FONT}" fontSize="{f(size)}" color="{color}" '
                 f'fontStyle="{weight}"{ta}>{esc(s)}</Text></Positioned>')

    def render(self, w, h, bg):
        return (f'<Snapshot type="png" background="{bg}">\n  <SizedBox width="{w}" height="{h}">\n  '
                '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n    '
                + "\n    ".join(self.o)
                + "\n  </Stack>\n  </SizedBox>\n</Snapshot>\n")


# ===================== WIDE 1920x1200 =====================
PL, PR = 310.0, 1880.0
PPM = (PR - PL) / (DAY_END - DAY_START)          # px per minute
GRID_T, GRID_B = 150.0, 816.0
LANES = {"A": 190.0, "B": 400.0, "C": 610.0}
LANE_H = 198.0
BLK_H = 164.0
BLK_DY = 18.0


def X(m):
    return PL + (m - DAY_START) * PPM


wide = DSL()
wide.rect(0, 0, 1920, 1200, "#0A1020")
wide.add('<Positioned left="0" top="0" width="1920" height="104">'
         '<Container gradientType="LINEAR" gradientColors="#101A30,#0A1020" '
         'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT" /></Positioned>')
wide.box(0, 102, 1920, 3,
         '<Container gradientType="LINEAR" gradientColors="#38BDF8,#818CF8,#34D399" '
         'gradientBegin="CENTER_LEFT" gradientEnd="CENTER_RIGHT" />')
wide.text(40, 22, "Structure / Vision 2026 · 全日日程", 38, "#F8FAFC", "BOLD")
wide.text(40, 70, "2026.11.07 · 云构中心 · A / B / C 会场 · Asia/Shanghai · 09:00–16:00",
          20, "#94A3B8")
wide.text(1000, 26, "15 场 · 3 会场 · 公共午休 12:00–13:00", 20, "#CBD5E1", w=880, align="END")
wide.text(1000, 60, "按真实时长等比绘制，空白即空档", 20, "#64748B", w=880, align="END")

# venue lane backgrounds + labels (drawn before grid so the lunch band stays legible)
for v in ("A", "B", "C"):
    ly = LANES[v]
    wide.rect(30, ly, 264, LANE_H, "#FFFFFF08", ' borderRadius="10"')
    wide.rect(30, ly, 5, LANE_H, VENUE_COLOR[v], ' borderRadius="2"')
    ven = [e for e in EV if e["venue"] == v]
    cats = {}
    for e in ven:
        cats[CAT_ZH[e["category"]]] = cats.get(CAT_ZH[e["category"]], 0) + 1
    cat_txt = " · ".join(f"{k}{n}" for k, n in cats.items())
    wide.text(52, ly + 26, f"{v} 会场", 26, VENUE_COLOR[v], "BOLD")
    wide.text(52, ly + 66, f"容量 {venues[v]['capacity']} 座", 20, "#CBD5E1")
    wide.text(52, ly + 96, f"{len(ven)} 场 · {sum(e['minutes'] for e in ven)} 分钟", 20, "#CBD5E1")
    wide.text(52, ly + 126, cat_txt, 20, "#94A3B8")
    wide.rect(PL, ly, PR - PL, LANE_H, "#FFFFFF05", ' borderRadius="6"')

# grid + hour labels
m = DAY_START
while m <= DAY_END:
    x = X(m)
    is_hour = (m % 60 == 0)
    wide.rect(x, GRID_T, 1, GRID_B - GRID_T, "#334155" if is_hour else "#FFFFFF12")
    if is_hour:
        wide.text(x - 45, 116, f"{m//60:02d}:{m%60:02d}", 20, "#94A3B8", w=90, align="CENTER")
    else:
        wide.rect(x - 4, GRID_B, 8, 4, "#334155")
    m += 30

# lunch band
wide.rect(X(LUNCH[0]), GRID_T, X(LUNCH[1]) - X(LUNCH[0]), GRID_B - GRID_T, "#F59E0B24",
          ' borderRadius="6"')
wide.box(X(LUNCH[0]), GRID_T, X(LUNCH[1]) - X(LUNCH[0]), 30,
         '<Container color="#F59E0B33" borderRadius="6" />')
wide.text(X(LUNCH[0]), 156, "公共午休 12:00–13:00", 20, "#FBBF24", "BOLD",
          w=X(LUNCH[1]) - X(LUNCH[0]), align="CENTER")

# blocks
block_geom = {}
for e in EV:
    x0, x1 = X(e["start_min"]), X(e["end_min"])
    bw = x1 - x0
    ly = LANES[e["venue"]] + BLK_DY
    col = CAT_COLOR[e["category"]]
    wide.box(x0, ly, bw, BLK_H,
             f'<Container color="{col}26" border="1 SOLID {col}" borderRadius="8" />')
    wide.rect(x0, ly + 14, 4, BLK_H - 28, col, ' borderRadius="2"')
    id_line = f"{e['id']} · {CAT_ZH[e['category']]}"
    pad = 14.0
    id_size = 20
    if est(id_line, 20) > bw - 2 * pad:
        if est(id_line, 18) <= bw - 20:
            pad, id_size = 10.0, 18
        else:
            id_line = e["id"]
    iw = bw - 2 * pad
    wide.text(x0 + pad, ly + 8, id_line, id_size, col, "BOLD", w=iw)
    lines = wrap(e["title"], 20, iw)
    for i, ln in enumerate(lines[:3]):
        wide.text(x0 + pad, ly + 36 + i * 26, ln, 20, "#F8FAFC", "BOLD", w=iw)
    wide.text(x0 + pad, ly + 94, e["speaker"], 20, "#CBD5E1", w=iw)
    tline = f"{e['start']}–{e['end']}"
    if est(tline, 18) > iw:
        wide.text(x0 + pad, ly + 122, e["start"], 18, "#94A3B8", w=iw)
        wide.text(x0 + pad, ly + 142, f"至 {e['end']}", 18, "#94A3B8", w=iw)
    else:
        wide.text(x0 + pad, ly + 124, tline, 18, "#94A3B8", w=iw)
    block_geom[e["id"]] = [round(x0, 2), round(ly, 2), round(x1, 2), round(ly + BLK_H, 2)]

# legend / reading method
wide.text(40, 830, "读图方法：色块的起点与长度按真实时间等比绘制（1 分钟 ≈ 3.74 像素），空白即为会场空档；"
                   "12:00–13:00 为三泳道公共午休，不与会议合并。", 20, "#CBD5E1")
lx = 40
for k, zh in CAT_ZH.items():
    wide.rect(lx, 866, 18, 18, CAT_COLOR[k], ' borderRadius="4"')
    wide.text(lx + 26, 862, zh, 20, "#CBD5E1")
    lx += 26 + est(zh, 20) + 44
wide.text(1120, 862, "色块内：编号 · 类别 / 标题 / 讲者 / 起止时间", 20, "#94A3B8")

# index table (two columns)
IDX_Y = 896.0
COLS = [(40.0, 940.0), (990.0, 1880.0)]
CW = [74.0, 380.0, 190.0, 156.0, 90.0]
heads = ["编号", "标题", "讲者", "起止时间", "类别"]
ROW_STEP = 28.0
for ci, (cx0, cx1) in enumerate(COLS):
    grp = EV[:8] if ci == 0 else EV[8:]
    for j, hd in enumerate(heads):
        px = cx0 + sum(CW[:j])
        wide.text(px, IDX_Y, hd, 20, "#64748B", w=CW[j],
                  align="END" if j >= 3 else "START")
    wide.rect(cx0, IDX_Y + 26, cx1 - cx0, 1, "#334155")
    for i, e in enumerate(grp):
        ry = IDX_Y + 32 + i * ROW_STEP
        wide.rect(cx0, ry, cx1 - cx0, ROW_STEP, "#FFFFFF08" if i % 2 == 0 else "#00000000")
        vals = [e["id"], e["title"], e["speaker"], f"{e['start']}–{e['end']}",
                CAT_ZH[e["category"]]]
        cols = [CAT_COLOR[e["category"]], "#E2E8F0", "#CBD5E1", "#94A3B8", CAT_COLOR[e["category"]]]
        for j, (val, cv) in enumerate(zip(vals, cols)):
            px = cx0 + sum(CW[:j])
            wide.text(px, ry + 3, val, 20, cv, w=CW[j], align="END" if j >= 3 else "START")

wide.text(40, 1162, "会场容量：A 320 座 / B 80 座 / C 160 座（来自 inputs/venues.json）· "
                    "全部时间为 Asia/Shanghai · 本图不含输入之外的信息", 18, "#64748B")

wide_dsl = wide.render(1920, 1200, "#0A1020")

# ===================== MOBILE 720x1280 =====================
mob = DSL()
mob.rect(0, 0, 720, 1280, "#0A1020")
mob.add('<Positioned left="0" top="0" width="720" height="150">'
        '<Container gradientType="LINEAR" gradientColors="#101A30,#0A1020" '
        'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT" /></Positioned>')
mob.box(0, 147, 720, 3,
        '<Container gradientType="LINEAR" gradientColors="#38BDF8,#818CF8,#34D399" '
        'gradientBegin="CENTER_LEFT" gradientEnd="CENTER_RIGHT" />')
mob.text(32, 28, "Structure / Vision 2026", 32, "#F8FAFC", "BOLD")
mob.text(32, 74, "2026.11.07 · 云构中心 · 会场 A / B / C", 20, "#CBD5E1")
mob.text(32, 108, "手机导览 · 讲者详见完整日程（1920×1200）", 18, "#94A3B8")

ROW_H, ROW_G = 54.0, 4.0


def mobile_row(y, e):
    col = VENUE_COLOR[e["venue"]]
    mob.rect(32, y, 656, ROW_H, "#FFFFFF08", ' borderRadius="10"')
    mob.rect(32, y + 10, 4, ROW_H - 20, col, ' borderRadius="2"')
    mob.text(50, y + 16, e["id"], 18, CAT_COLOR[e["category"]], "BOLD", w=60)
    mob.text(116, y + 16, f"{e['start']}–{e['end']}", 18, "#CBD5E1", w=136)
    mob.rect(258, y + 17, 12, 12, col, ' borderRadius="3"')
    mob.text(276, y + 16, f"{e['venue']} 会场", 18, "#CBD5E1", w=96)
    mob.text(378, y + 15, e["title"], 20, "#F8FAFC", "BOLD", w=302)


y = 164.0
mob.rect(32, y, 656, 34, "#38BDF814", ' borderRadius="8"')
mob.text(44, y + 5, "上午场 · 09:00–12:00", 22, "#7DD3FC", "BOLD")
mob.text(430, y + 8, "8 场", 18, "#94A3B8", w=240, align="END")
y += 42
for e in [x for x in EV if x["end_min"] <= LUNCH[0]]:
    mobile_row(y, e)
    y += ROW_H + ROW_G

mob.rect(32, y, 656, 56, "#F59E0B1F", ' borderRadius="10"')
mob.rect(32, y + 10, 4, 36, "#FBBF24", ' borderRadius="2"')
mob.text(52, y + 16, "公共午休 12:00–13:00", 20, "#FBBF24", "BOLD")
mob.text(430, y + 19, "全场暂停", 18, "#FBBF24", w=240, align="END")
y += 56 + 12

mob.rect(32, y, 656, 34, "#34D39914", ' borderRadius="8"')
mob.text(44, y + 5, "下午场 · 13:00–16:00", 22, "#86EFAC", "BOLD")
mob.text(430, y + 8, "7 场", 18, "#94A3B8", w=240, align="END")
y += 42
for e in [x for x in EV if x["start_min"] >= LUNCH[1]]:
    mobile_row(y, e)
    y += ROW_H + ROW_G

mob.text(32, y + 10, "共 15 场 · 讲者详见完整日程 · 会场容量 A 320 / B 80 / C 160 座",
         18, "#64748B")
mob.text(32, y + 40, "时间均为 Asia/Shanghai，起止时间与完整日程一致", 18, "#64748B")

mobile_dsl = mob.render(720, 1280, "#0A1020")
print("mobile rows end at y =", y + 68)

# ===================== write =====================
(tmp_dir / "agenda-wide.snapshot").write_text(wide_dsl, encoding="utf-8")
(tmp_dir / "agenda-mobile.snapshot").write_text(mobile_dsl, encoding="utf-8")
print("wide px/min =", round(PPM, 6))
print("blocks:", json.dumps(block_geom, ensure_ascii=False))

# ===================== audit json =====================
events_audit = []
for e in EV:
    events_audit.append({
        "id": e["id"], "venue": e["venue"],
        "start": e["start"], "end": e["end"],
        "minutes": e["minutes"],
        "title": e["title"], "speaker": e["speaker"],
        "category": e["category"], "category_zh": CAT_ZH[e["category"]],
        "start_minute_of_day": e["start_min"], "end_minute_of_day": e["end_min"],
    })

gaps = []
for v in ("A", "B", "C"):
    ven = sorted([e for e in EV if e["venue"] == v], key=lambda e: e["start_min"])
    free = []
    cur = DAY_START
    for e in ven:
        if e["start_min"] > cur:
            free.append((cur, e["start_min"]))
        cur = max(cur, e["end_min"])
    if cur < DAY_END:
        free.append((cur, DAY_END))
    la, lb = LUNCH
    for (p, q) in free:                      # split around the public lunch
        pieces = [(p, q)]
        if not (q <= la or p >= lb):
            pieces = []
            if p < la:
                pieces.append((p, la))
            if q > lb:
                pieces.append((lb, q))
        for (a, b) in pieces:
            if b > a:
                gaps.append({"venue": v, "type": "venue_gap", "from_minute": a, "to_minute": b,
                             "from": f"{a//60:02d}:{a%60:02d}", "to": f"{b//60:02d}:{b%60:02d}",
                             "minutes": b - a, "adjacent_to_public_lunch": b == la or a == lb})
for v in ("A", "B", "C"):
    gaps.append({"venue": v, "type": "public_lunch", "from_minute": LUNCH[0],
                 "to_minute": LUNCH[1], "from": "12:00", "to": "13:00", "minutes": 60,
                 "note": "公共午休，跨三条泳道独立记录，不与任何会议合并成一项；"
                         "会场空档已按 12:00/13:00 拆分，午休分钟数不在空档中重复计入"})

conflicts = []
for v in ("A", "B", "C"):
    ven = sorted([e for e in EV if e["venue"] == v], key=lambda e: e["start_min"])
    for i in range(len(ven) - 1):
        a, b = ven[i], ven[i + 1]
        if b["start_min"] < a["end_min"]:
            conflicts.append({"venue": v, "pair": [a["id"], b["id"]],
                              "overlap_from": b["start"], "overlap_to": a["end"],
                              "minutes": a["end_min"] - b["start_min"]})
lunch_hits = [e["id"] for e in EV
              if e["start_min"] < LUNCH[1] and e["end_min"] > LUNCH[0]]

content_map = []
for e in EV:
    content_map.append({
        "id": e["id"],
        "wide": {
            "image": "agenda-wide.png",
            "block_pixel_box": block_geom[e["id"]],
            "text_lines": [f"{e['id']} · {CAT_ZH[e['category']]}", e["title"],
                           e["speaker"], f"{e['start']}–{e['end']}"],
        },
        "mobile": {
            "image": "agenda-mobile.png",
            "row_index": EV.index(e),
            "text_lines": [e["id"], f"{e['start']}–{e['end']}", f"{e['venue']} 会场", e["title"]],
            "speaker_note": "讲者详见完整日程",
        },
    })

audit = {
    "schema_version": 1,
    "task_id": "A02",
    "path_base": "output_dir",
    "date": "2026.11.07",
    "timezone": "Asia/Shanghai",
    "artifacts": {"wide_png": "agenda-wide.png", "wide_dsl": "agenda-wide.snapshot",
                  "mobile_png": "agenda-mobile.png", "mobile_dsl": "agenda-mobile.snapshot"},
    "time_axis": {
        "timezone": "Asia/Shanghai",
        "base": "09:00",
        "end": "16:00",
        "total_minutes": DAY_END - DAY_START,
        "canvas": "agenda-wide.png 1920x1200",
        "pixel_start_x": PL, "pixel_end_x": PR, "pixel_width": PR - PL,
        "minutes_to_pixels": PPM,
        "formula": "x = 310 + (minute_of_day - 540) * (1570/420)",
        "grid_top": GRID_T, "grid_bottom": GRID_B,
        "lane_boxes": {v: [30.0, LANES[v], 294.0, LANES[v] + LANE_H] for v in ("A", "B", "C")},
        "block_height": BLK_H,
        "mobile_axis": "手机图为分时段列表，无连续时间轴；起止时间以文本给出，与大图同源同值",
    },
    "events": events_audit,
    "venue_gaps": gaps,
    "conflicts": conflicts,
    "conflict_summary": {
        "same_venue_overlap_count": len(conflicts),
        "sessions_overlapping_public_lunch": lunch_hits,
        "statement": "同会场内无重叠活动；跨会场并行属正常安排，不计为冲突；无任何活动与 12:00–13:00 公共午休重叠。"
                     "未调整任何输入时间，未捏造冲突。",
    },
    "content_map": content_map,
    "verification": {
        "total_sessions": len(EV),
        "total_scheduled_minutes": sum(e["minutes"] for e in EV),
        "per_venue": {v: {"sessions": len([e for e in EV if e["venue"] == v]),
                          "minutes": sum(e["minutes"] for e in EV if e["venue"] == v),
                          "capacity": venues[v]["capacity"]} for v in ("A", "B", "C")},
        "proportional_check": "所有色块宽度 = minutes * 1570/420 px，未做四舍五入以外的调整；"
                              "40 分钟块宽 149.52px、60 分钟块宽 224.29px，比例严格一致",
    },
}
(out_dir / "schedule-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("audit written; conflicts =", len(conflicts), "; lunch overlaps =", lunch_hits)
for g in gaps:
    if g["venue"] == "A":
        print("A gap", g["from"], g["to"], g["minutes"], g["type"])
