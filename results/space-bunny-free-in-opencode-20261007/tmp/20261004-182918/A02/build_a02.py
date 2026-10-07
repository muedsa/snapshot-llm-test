"""A02 - Structure/Vision 2026 wide swimlane schedule + mobile guide."""
from __future__ import annotations

import csv
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "A02"
BASE = os.path.join(ROOT, "tasks", "A02-conference-schedule", "inputs")
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
S.start_task(TASK)

VENUES = json.load(open(os.path.join(BASE, "venues.json"), encoding="utf-8"))
CAP = VENUES
CATS = VENUES["categories"]

sessions = []
with open(os.path.join(BASE, "agenda.csv"), newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        sh, sm = (int(x) for x in r["start"].split(":"))
        eh, em = (int(x) for x in r["end"].split(":"))
        s, e = sh * 60 + sm, eh * 60 + em
        sessions.append({
            "id": r["id"], "num": int(r["id"][1:]), "venue": r["venue"],
            "start": r["start"], "end": r["end"], "start_min": s, "end_min": e,
            "duration_min": e - s, "title": r["title"], "speaker": r["speaker"],
            "category": r["category"], "category_zh": CATS[r["category"]],
        })
sessions.sort(key=lambda s: (s["venue"], s["start_min"]))

DAY_START, DAY_END = 9 * 60, 16 * 60
LUNCH = (12 * 60, 13 * 60)


def m2t(m):
    return "%02d:%02d" % (m // 60, m % 60)


gaps = {}
for v in ("A", "B", "C"):
    ss = sorted([s for s in sessions if s["venue"] == v], key=lambda s: s["start_min"])
    g, cur = [], DAY_START
    for s in ss:
        if s["start_min"] > cur:
            g.append({"from": m2t(cur), "to": m2t(s["start_min"]),
                      "minutes": s["start_min"] - cur,
                      "kind": "lunch" if (cur, s["start_min"]) == LUNCH else "free"})
        cur = max(cur, s["end_min"])
    if cur < DAY_END:
        g.append({"from": m2t(cur), "to": m2t(DAY_END), "minutes": DAY_END - cur,
                  "kind": "free"})
    gaps[v] = g

conflicts = []
for v in ("A", "B", "C"):
    ss = sorted([s for s in sessions if s["venue"] == v], key=lambda s: s["start_min"])
    for a, b in zip(ss, ss[1:]):
        if b["start_min"] < a["end_min"]:
            conflicts.append({"type": "same_venue_overlap", "venue": v,
                              "a": a["id"], "b": b["id"]})
lunch_overlaps = [s["id"] for s in sessions
                  if s["start_min"] < LUNCH[1] and s["end_min"] > LUNCH[0]]
parallel = []
for i, a in enumerate(sessions):
    for b in sessions[i + 1:]:
        if b["start_min"] < a["end_min"] and a["start_min"] < b["end_min"]:
            parallel.append({"a": a["id"], "b": b["id"],
                             "venues": [a["venue"], b["venue"]]})

CAT_COLOR = {"keynote": "#7C3AED", "workshop": "#0D9488", "talk": "#2563EB",
             "demo": "#EA580C", "panel": "#BE123C"}
INK, MUTED, FAINT, LINE, CARD = "#0F172A", "#475569", "#7C8CA0", "#E2E8F0", "#FFFFFF"


def tint(hexc, amount):
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    f = lambda v: int(round(v + (255 - v) * amount))  # noqa: E731
    return "#%02X%02X%02X" % (f(r), f(g), f(b))


def wrap(s, size, maxw, maxlines):
    toks, cur = [], ""
    for ch in s:
        if ord(ch) > 0x2E80 or ch in "，。、：；！？（）《》“”·—…":
            if cur:
                toks.append(cur)
                cur = ""
            toks.append(ch)
        elif ch == " ":
            if cur:
                toks.append(cur)
                cur = ""
            toks.append(" ")
        else:
            cur += ch
    if cur:
        toks.append(cur)
    lines, line = [], ""
    for t in toks:
        cand = line + t
        if D.est_width(cand, size) <= maxw or not line:
            line = cand
        else:
            lines.append(line.rstrip())
            line = "" if t == " " else t
    if line.strip():
        lines.append(line.rstrip())
    if len(lines) > maxlines:
        keep = lines[:maxlines]
        while keep and D.est_width(keep[-1] + "…", size) > maxw:
            keep[-1] = keep[-1][:-1]
        keep[-1] = keep[-1] + "…"
        return keep
    return lines


# ================================================================== WIDE
W, H = 1920, 1200
HDR = 88
LEG_Y = 96
AX_Y = 150
PL_X0, PL_X1 = 198, 1888
PL_W = PL_X1 - PL_X0
LANE_Y, LANE_H, LANE_GAP = 186, 224, 8
LANES_TOP = LANE_Y
LANES_BOT = LANE_Y + 3 * LANE_H + 2 * LANE_GAP
PPM = PL_W / float(DAY_END - DAY_START)
LBL_W = 150


def tx(m):
    return PL_X0 + (m - DAY_START) * PPM


kids = [
    D.box(0, 0, W, HDR, color="#0F172AFF"),
    D.text_el("Structure / Vision 2026 · 全日日程", x=40, y=16, w=900, h=42,
              size=32, style="BOLD", color="#F8FAFCFF"),
    D.text_el("2026.11.07（周六） · 云构中心 · A / B / C 会场 · 时间均为 Asia/Shanghai",
              x=40, y=56, w=1000, h=24, size=19, color="#9FB0C4FF"),
    D.text_el("15 场活动 · 3 条会场泳道 · 09:00–16:00 共用线性时间轴",
              x=W - 40 - 660, y=34, w=660, h=26, size=19, color="#7DD3FCFF",
              align="RIGHT"),
    D.text_el("类别", x=40, y=LEG_Y + 10, w=70, h=24, size=19, color=MUTED),
]
lx = 112
for cat, zh in CATS.items():
    n = sum(1 for s in sessions if s["category"] == cat)
    label = "%s %s ×%d" % (zh, cat, n)
    tw = D.est_width(label, 18) + 36
    kids += [
        D.box(lx, LEG_Y + 6, tw, 32, color=tint(CAT_COLOR[cat], 0.86), radius=16,
              border="1 SOLID " + tint(CAT_COLOR[cat], 0.55)),
        D.box(lx + 11, LEG_Y + 17, 10, 10, color=CAT_COLOR[cat], radius=3),
        D.text_el(label, x=lx + 27, y=LEG_Y + 14, w=tw - 36, h=24, size=18, color=INK),
    ]
    lx += tw + 10
kids.append(D.text_el("会场容量：A %d 位 · B %d 位 · C %d 位" % (
    CAP["A"]["capacity"], CAP["B"]["capacity"], CAP["C"]["capacity"]),
    x=W - 40 - 470, y=LEG_Y + 12, w=470, h=24, size=18, color=MUTED, align="RIGHT"))

kids.append(D.box(40, AX_Y - 6, W - 80, 2, color="#CBD5E1FF"))
t = DAY_START
while t <= DAY_END:
    major = (t % 60 == 0)
    lx0 = min(max(tx(t) - 45, 44), W - 40 - 90)
    kids.append(D.text_el(m2t(t), x=lx0, y=AX_Y + 6, w=90, h=24, size=18,
                          style=("BOLD" if major else "NORMAL"),
                          color=(INK if major else FAINT), align="CENTER"))
    t += 30

for i, v in enumerate(("A", "B", "C")):
    ly = LANE_Y + i * (LANE_H + LANE_GAP)
    kids += [
        D.box(40, ly, W - 80, LANE_H, color=CARD, radius=14, border="1 SOLID #E2E8F0FF",
              shadow="0 1 6 0 #0F172A0D"),
        D.box(40, ly, LBL_W - 8, LANE_H, color="#F1F5F9FF"),
        D.text_el("%s 会场" % v, x=54, y=ly + 20, w=LBL_W - 30, h=34, size=28,
                  style="BOLD", color=INK),
        D.text_el("容量 %d 位" % CAP[v]["capacity"], x=54, y=ly + 58, w=LBL_W - 26,
                  h=24, size=18, color=MUTED),
    ]
    n = sum(1 for s in sessions if s["venue"] == v)
    mins = sum(s["duration_min"] for s in sessions if s["venue"] == v)
    kids += [
        D.text_el("%d 场活动" % n, x=54, y=ly + 86, w=LBL_W - 26, h=24, size=18,
                  color=FAINT),
        D.text_el("合计 %d 分钟" % mins, x=54, y=ly + 110, w=LBL_W - 26, h=22, size=16,
                  color=FAINT),
    ]
    g = DAY_START
    while g <= DAY_END:
        kids.append(D.vline(tx(g), ly + 4, ly + LANE_H - 4,
                            "#CBD5E1FF" if g % 60 == 0 else "#EEF2F6FF", 1))
        g += 30

placed = []
for s in sessions:
    ly = LANE_Y + "ABC".index(s["venue"]) * (LANE_H + LANE_GAP)
    bx, bw = tx(s["start_min"]), s["duration_min"] * PPM
    by, bh = ly + 8, LANE_H - 16
    col = CAT_COLOR[s["category"]]
    kids += [
        D.box(bx, by, bw, bh, color=tint(col, 0.90), radius=10,
              border="1 SOLID " + tint(col, 0.45)),
        D.box(bx, by, 5, bh, color=col, radii={"TopLeft": "10", "BottomLeft": "10"}),
    ]
    pad_l, pad_r, pad_t = 13, 9, 8
    inner = bw - pad_l - pad_r
    head1 = "%02d · %s–%s" % (s["num"], s["start"], s["end"])
    head2a = "%02d · %s" % (s["num"], s["start"])
    head2b = "→ %s" % s["end"]
    if D.est_width(head1, 18) <= inner:
        kids.append(D.text_el(head1, x=bx + pad_l, y=by + pad_t, w=inner, h=24,
                              size=18, style="BOLD", color=col))
        ty = by + pad_t + 26
    elif (D.est_width(head2a, 18) <= inner and D.est_width(head2b, 18) <= inner):
        kids += [
            D.text_el(head2a, x=bx + pad_l, y=by + pad_t, w=inner, h=24, size=18,
                      style="BOLD", color=col),
            D.text_el(head2b, x=bx + pad_l, y=by + pad_t + 22, w=inner, h=24, size=18,
                      style="BOLD", color=col),
        ]
        ty = by + pad_t + 48
    else:
        kids += [
            D.text_el("%02d" % s["num"], x=bx + pad_l, y=by + pad_t, w=inner, h=24,
                      size=18, style="BOLD", color=col),
            D.text_el("%s–%s" % (s["start"], s["end"]), x=bx + pad_l, y=by + pad_t + 22,
                      w=inner, h=24, size=18, style="BOLD", color=col),
        ]
        ty = by + pad_t + 48
    for ln in wrap(s["title"], 20, inner, 3):
        kids.append(D.text_el(ln, x=bx + pad_l, y=ty, w=inner, h=26, size=20, color=INK))
        ty += 25
    sp = wrap("讲者 " + s["speaker"], 18, inner, 2)
    if ty + 24 <= by + bh - 30:
        for ln in sp:
            kids.append(D.text_el(ln, x=bx + pad_l, y=ty, w=inner, h=22, size=18,
                                  color=MUTED))
            ty += 22
    if bw >= 140:
        tag = s["category_zh"]
        tw = D.est_width(tag, 16) + 18
        kids += [
            D.box(bx + bw - 8 - tw, by + bh - 8 - 24, tw, 24, color=col, radius=12),
            D.text_el(tag, x=bx + bw - 8 - tw, y=by + bh - 8 - 20, w=tw, h=20, size=16,
                      color="#FFFFFFFF", align="CENTER"),
        ]
    if bw >= 176:
        kids.append(D.text_el("%d 分钟" % s["duration_min"], x=bx + pad_l,
                              y=by + bh - 8 - 22, w=inner, h=22, size=18, color=FAINT))
    placed.append({"id": s["id"], "x": round(bx, 2), "y": round(by, 2),
                   "w": round(bw, 2), "h": round(bh, 2),
                   "start_min": s["start_min"], "duration_min": s["duration_min"]})

lx0, lx1 = tx(LUNCH[0]), tx(LUNCH[1])
midx = (lx0 + lx1) / 2.0
midy = (LANES_TOP + LANES_BOT) / 2.0
kids.append(D.box(lx0, LANES_TOP, lx1 - lx0, LANES_BOT - LANES_TOP, color="#0F172A12"))
stripe = lx0
while stripe < lx1 - 6:
    kids.append(D.box(stripe, LANES_TOP, 4, LANES_BOT - LANES_TOP, color="#0F172A18"))
    stripe += 14
kids.append(D.vline(lx0, LANES_TOP, LANES_BOT, "#475569FF", 2))
kids.append(D.vline(lx1, LANES_TOP, LANES_BOT, "#475569FF", 2))
kids += [
    D.box(midx - 108, midy - 40, 216, 38, color="#0F172AFF", radius=19),
    D.text_el("公共午休 12:00–13:00", x=midx - 108, y=midy - 34, w=216, h=26, size=20,
              style="BOLD", color="#F8FAFCFF", align="CENTER"),
    D.text_el("跨三泳道 · 独立时段", x=midx - 105, y=midy + 4, w=210, h=24,
              size=18, color="#475569FF", align="CENTER"),
    D.text_el("不与任何会议合并", x=midx - 105, y=midy + 26, w=210, h=24,
              size=18, color="#475569FF", align="CENTER"),
]

IX = 40
IY = LANES_BOT + 14
IDX_PITCH = 70
kids.append(D.text_el("编号索引 · 全部 15 项（编号 / 起止时间 / 时长 / 标题 / 讲者 / 类别）",
                      x=IX, y=IY, w=1200, h=26, size=20, style="BOLD", color=INK))
COLW = (W - 80) / 5.0
for k, s in enumerate(sessions):
    c, r = k // 3, k % 3
    x, y = IX + c * COLW, IY + 34 + r * IDX_PITCH
    col = CAT_COLOR[s["category"]]
    kids += [
        D.box(x, y, COLW - 14, 64, color="#F8FAFCFF", radius=10),
        D.box(x, y, 4, 64, color=col, radii={"TopLeft": "10", "BottomLeft": "10"}),
        D.text_el("%02d · %s · %s–%s · %d 分钟" % (
            s["num"], s["venue"], s["start"], s["end"], s["duration_min"]),
            x=x + 14, y=y + 4, w=COLW - 34, h=22, size=18, style="BOLD", color=col),
        D.text_el(s["title"], x=x + 14, y=y + 24, w=COLW - 34, h=24, size=20, color=INK),
        D.text_el("讲者 %s · %s" % (s["speaker"], s["category_zh"]), x=x + 14, y=y + 44,
                  w=COLW - 34, h=20, size=18, color=MUTED),
    ]

readme = ("读图方法：横轴 09:00–16:00 为三泳道共用的线性时间轴，每格 30 分钟；块宽 = 实际时长比例，"
          "块高固定，故 30 分钟的活动不会被画成 60 分钟；泳道内空白即真实空档（各会场空档见 "
          "schedule-audit.json）；12:00–13:00 为跨三泳道的公共午休，独立标识、不与任何会议合并；"
          "块内省略的讲者与类别标签见下方编号索引。")
rl = wrap(readme, 18, W - 80, 3)
for i, ln in enumerate(rl):
    kids.append(D.text_el(ln, x=IX, y=H - 14 - 24 * (len(rl) - i), w=W - 80, h=24,
                          size=18, color=FAINT))

wide_dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#F1F5F9FF")
with open(os.path.join(TMP, "build-a02-wide.snapshot"), "w", encoding="utf-8",
          newline="\n") as fh:
    fh.write(wide_dsl)
rw = snapkit.render(wide_dsl, "agenda-wide.png", "agenda-wide.snapshot", final=True)
print("wide ok=%s status=%s" % (rw.get("ok"), rw.get("status")))
if not rw.get("ok"):
    print(rw.get("error"))

# ================================================================== MOBILE
MW, MH = 720, 1280
M = 24
SLOTS = [("上午场 09:00–12:00", lambda s: s["start_min"] < LUNCH[0]),
         ("午休 12:00–13:00", None),
         ("下午前段 13:00–14:30", lambda s: LUNCH[1] <= s["start_min"] < 14 * 60 + 30),
         ("下午后段 14:30–16:00", lambda s: s["start_min"] >= 14 * 60 + 30)]
mk = [
    D.box(0, 0, MW, 92, color="#0F172AFF"),
    D.text_el("Structure / Vision 2026", x=M, y=10, w=MW - 2 * M, h=32, size=26,
              style="BOLD", color="#F8FAFCFF"),
    D.text_el("2026.11.07 · 云构中心 A / B / C 会场 · 讲者详见完整日程", x=M, y=44,
              w=MW - 2 * M, h=24, size=18, color="#9FB0C4FF"),
    D.text_el("按时段浏览全部 15 项 · 时间均为 Asia/Shanghai", x=M, y=66, w=MW - 2 * M,
              h=22, size=18, color="#7DD3FCFF"),
]
y = 100
for title, pred in SLOTS:
    rows = [None] if pred is None else [s for s in sessions if pred(s)]
    mk += [
        D.text_el(title, x=M, y=y, w=MW - 2 * M, h=26, size=20, style="BOLD", color=INK),
        D.hline(M, MW - M, y + 28, "#CBD5E1FF", 1.5),
    ]
    y += 34
    for s in rows:
        if s is None:
            mk += [
                D.box(M, y, MW - 2 * M, 46, color="#0F172A14", radius=12,
                      border="1 SOLID #CBD5E1FF"),
                D.text_el("公共午休 12:00–13:00 · 跨三会场 · 不排任何活动", x=M + 14,
                          y=y + 12, w=MW - 2 * M - 28, h=24, size=18, color=INK,
                          align="CENTER"),
            ]
            y += 54
            continue
        col = CAT_COLOR[s["category"]]
        mk += [
            D.box(M, y, MW - 2 * M, 56, color="#FFFFFF", radius=12,
                  border="1 SOLID #E2E8F0FF", shadow="0 1 4 0 #0F172A0F"),
            D.box(M, y, 5, 56, color=col, radii={"TopLeft": "12", "BottomLeft": "12"}),
            D.text_el("%02d · %s 会场 · %s–%s" % (s["num"], s["venue"], s["start"],
                                                  s["end"]),
                      x=M + 16, y=y + 5, w=MW - 2 * M - 32 - 76, h=24, size=18,
                      style="BOLD", color=col),
            D.text_el(s["category_zh"], x=MW - M - 16 - 70, y=y + 5, w=70, h=24,
                      size=18, color=MUTED, align="RIGHT"),
            D.text_el(s["title"], x=M + 16, y=y + 28, w=MW - 2 * M - 32, h=26,
                      size=20, color=INK),
        ]
        y += 60
    y += 6
mk.append(D.text_el("共 15 场 · 会场容量 A %d 位 / B %d 位 / C %d 位 · 讲者详见完整日程"
                    % (CAP["A"]["capacity"], CAP["B"]["capacity"], CAP["C"]["capacity"]),
                    x=M, y=MH - 30, w=MW - 2 * M, h=24, size=18, color=FAINT))

mobile_dsl = D.snapshot([D.stack(mk, MW, MH)], MW, MH, bg="#F1F5F9FF")
with open(os.path.join(TMP, "build-a02-mobile.snapshot"), "w", encoding="utf-8",
          newline="\n") as fh:
    fh.write(mobile_dsl)
rm = snapkit.render(mobile_dsl, "agenda-mobile.png", "agenda-mobile.snapshot", final=True)
print("mobile ok=%s status=%s" % (rm.get("ok"), rm.get("status")))
if not rm.get("ok"):
    print(rm.get("error"))

by_id = {p["id"]: p for p in placed}
audit = {
    "task": TASK,
    "event": "Structure / Vision 2026",
    "date": "2026-11-07",
    "timezone": "Asia/Shanghai",
    "venues": CAP,
    "day_window": {"from": "09:00", "to": "16:00", "minutes": DAY_END - DAY_START,
                   "shared_linear_axis_across_all_venues": True,
                   "pixels_per_minute_wide": round(PPM, 4)},
    "sessions": [
        {"id": s["id"], "number": s["num"], "venue": s["venue"], "start": s["start"],
         "end": s["end"], "duration_min": s["duration_min"], "title": s["title"],
         "speaker": s["speaker"], "category": s["category"],
         "category_zh": s["category_zh"], "wide_block_rect_px": by_id[s["id"]]}
        for s in sessions],
    "durations_minutes": {s["id"]: s["duration_min"] for s in sessions},
    "duration_note": "block width in agenda-wide.png equals duration_min * %.4f px/min, so a "
                     "30-minute block is exactly half the width of a 60-minute block on the "
                     "same lane; block height is constant per lane" % PPM,
    "lunch": {"from": "12:00", "to": "13:00", "minutes": 60,
              "drawn_as": "one band spanning all three lanes, never merged into a session",
              "session_ids_overlapping_lunch": lunch_overlaps},
    "venue_gaps": gaps,
    "gap_note": "gaps are reported exactly as drawn; no input time was moved or resized. The "
                "12:00-13:00 window is labelled kind=lunch rather than free.",
    "conflicts": {
        "same_venue_overlaps": conflicts,
        "same_venue_conflict_count": len(conflicts),
        "lunch_conflicts": lunch_overlaps,
        "parallel_sessions_different_venues": parallel,
        "note": "the input contains no same-venue overlap, so no conflict was invented; "
                "cross-venue parallelism is normal for a conference and is not a conflict",
    },
    "content_mapping_between_images": {
        "agenda-wide.png": {
            "size": [W, H],
            "carries": ["id", "start", "end", "duration", "title",
                        "speaker (all 15 blocks carry it)", "category (accent colour + tag "
                        "pill where the block is wide enough)", "venue", "gaps", "lunch band",
                        "venue capacity", "reading instructions"],
            "role": "proportional swimlane schedule"},
        "agenda-mobile.png": {
            "size": [MW, MH],
            "carries": ["id", "title", "venue", "start", "end", "category",
                        "time-slot grouping", "lunch row", "venue capacity"],
            "speaker": "moved to the wide image; the mobile header and footer both state "
                       "讲者详见完整日程",
            "role": "time-slot list; NOT a scaled or cropped copy of the wide image"},
        "one_to_one": {
            s["id"]: {"wide_block_rect_px": by_id[s["id"]],
                      "mobile_slot": next(t for t, pr in SLOTS
                                          if pr is not None and pr(s))}
            for s in sessions},
    },
    "render_geometry": {
        "wide": {"canvas": [W, H], "plot_x": [PL_X0, PL_X1], "plot_width_px": PL_W,
                 "px_per_minute": round(PPM, 4), "lane_y": LANE_Y, "lane_height": LANE_H,
                 "lane_gap": LANE_GAP, "venue_label_width": LBL_W,
                 "lanes_top": LANES_TOP, "lanes_bottom": LANES_BOT,
                 "lunch_band_x": [round(lx0, 2), round(lx1, 2)],
                 "index_pitch_px": IDX_PITCH},
        "mobile": {"canvas": [MW, MH], "margin": M, "row_height": 56, "row_pitch": 60,
                   "slot_header_height": 34},
    },
}
with open(os.path.join(OUT, "schedule-audit.json"), "w", encoding="utf-8") as fh:
    json.dump(audit, fh, ensure_ascii=False, indent=2)
print("audit written; same-venue conflicts=%d lunch_overlaps=%s parallel_pairs=%d"
      % (len(conflicts), lunch_overlaps, len(parallel)))
for wn in D.warnings()[:14]:
    print("WARN", wn)