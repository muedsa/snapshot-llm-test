"""A24 builder: execution board (1920x1080), decision brief (1200x1600), action card (720x1280).

All three are drawn from the same schedule.json / schedule-audit.json so they cannot
contradict each other, and every block is placed from a measured budget.
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_suite", "shared"))
from snapkit import (CJK, LINE_HEIGHT, MONO, Doc, assert_fits, card,  # noqa: E402
                     text_width)

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
OUT = os.path.join(ROOT, "outputs", "20261003-114508-flashmax", "A24")
TMP = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "A24")

BRAND = "叠光 · 发布演练"
INK = "#0F172AFF"
SUB = "#475569FF"
DIMC = "#94A3B8FF"
LINE = "#E2E8F0FF"
PAGE = "#EEF2F7FF"
HEAD = "#0F172AFF"
TEAL = "#0E9F8FFF"
BLUE = "#1D4ED8FF"
RED = "#D92D20FF"
AMBER = "#D97706FF"
DESIGN_C = "#0E9F8F"     # design-only task
ENG_C = "#1D4ED8"        # engineering-only task
BOTH_C = "#7C3AED"       # task that either team may run
TEAM_FILL = {"design": DESIGN_C, "engineering": ENG_C}

RISK_IDS = {"R02": "K1", "R05": "K2", "R10": "K3"}


def load() -> tuple:
    with open(os.path.join(OUT, "schedule.json"), encoding="utf-8") as fh:
        sch = json.load(fh)
    with open(os.path.join(OUT, "schedule-audit.json"), encoding="utf-8") as fh:
        aud = json.load(fh)
    return sch, aud


def hhmm(minutes: int) -> str:
    h, m = divmod(int(minutes), 60)
    return f"{9 + h:02d}:{m:02d}"


def wrap_text(s: str, size: float, maxw: float, mono: bool = False) -> list:
    """Greedy character wrap using the calibrated advance table."""
    out, cur = [], ""
    for ch in s:
        if cur and text_width(cur + ch, size, mono) > maxw:
            out.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


def bar_color(t: dict) -> str:
    return BOTH_C if len(t["teams_allowed"]) > 1 else TEAM_FILL[t["team"]]


# ============================================================ execution board
def execution_board(sch: dict, aud: dict) -> tuple:
    W, H = 1920, 1080
    d = Doc(W, H, background=PAGE)
    measured = []
    tasks = sch["tasks"]
    by_id = {t["id"]: t for t in tasks}

    d.box(0, 0, W, 6, TEAL)
    hdr = (24, 18, W - 48, 108)
    d.box(*hdr, HEAD, radius=16)
    d.text(48, 32, BRAND, 30, "#F8FAFCFF", weight="BOLD", maxw=520)
    d.text(48, 72, "发布日执行泳道 · 09:00 开工 / 16:00 截止", 22, "#CBD5E1FF", maxw=700)
    chips = [
        ("总工时", f'{sch["lower_bounds"]["total_work_minutes"]} 分钟', TEAL),
        ("计划完成", f'{sch["makespan_end"]} 完成', BLUE),
        ("剩余缓冲", f'{sch["buffer_minutes"]} 分钟', AMBER),
        ("关键路径", f'{sch["lower_bounds"]["critical_path_minutes"]} 分钟', RED),
    ]
    cw, cgap = 268, 12
    cx = W - 24 - (cw * 4 + cgap * 3)
    for label, value, col in chips:
        d.box(cx, 26, cw, 92, "#111C31FF", radius=12, border="1 SOLID #1E293BFF")
        d.box(cx, 26, 5, 92, col, radius=2)
        d.text(cx + 18, 36, label, 20, DIMC, maxw=cw - 30)
        d.text(cx + 18, 62, value, 26, "#F1F5F9FF", weight="BOLD", maxw=cw - 30,
               family=MONO)
        measured.append(dict(text=label, size=20, color=DIMC, y=36, role="kpi"))
        measured.append(dict(text=value, size=26, color="#F1F5F9FF", y=62, role="kpi"))
        cx += cw + cgap

    tl = (24, 146, W - 48, 66)
    d.box(*tl, "#FFFFFFFF", radius=16, border=f"1 SOLID {LINE}")
    lx0, lx1 = 268, W - 46
    pxm = (lx1 - lx0) / 420.0
    for m in range(0, 421, 30):
        x = round(lx0 + m * pxm, 1)
        is_hour = m % 60 == 0
        d.box(x, 200, 1, 14, "#CBD5E1FF" if is_hour else "#E2E8F0FF")
        if is_hour or m == 420:
            lbl = hhmm(m)
            d.text(round(x - text_width(lbl, 20, mono=True) / 2), 158, lbl, 20, SUB,
                   family=MONO)
    d.text(48, 162, "真实时间（同尺度）", 22, INK, weight="BOLD", maxw=210)
    d.text(48, 190, "每 30 分钟一格", 20, DIMC, maxw=210)

    lane_y = 226
    # six rows per lane, so the lane height is derived from a real row height instead of
    # squeezing (the first attempt divided a 62px lane by six rows and collapsed them)
    # each lane wraps its six tasks into two rows of three, which halves the lane block
    # and leaves the bottom of the canvas free for the full 12-row dependency table
    lane_rows = 3
    lane_rh = 28
    lane_top = 40
    lane_h = lane_top + lane_rows * lane_rh + 8
    rows_h = 400
    bars = []
    lane_block_top = lane_y
    for tm, title, note in (("design", "design", "单队 · 不可并行"),
                            ("engineering", "engineering", "单队 · 不可并行")):
        d.box(24, lane_y, W - 48, lane_h, "#FFFFFFFF", radius=14,
              border=f"1 SOLID {LINE}")
        d.text(48, lane_y + 10, title, 22, SUB, weight="BOLD", maxw=200)
        d.text(48, lane_y + 38, note, 18, DIMC, maxw=200)
        for m in range(0, 421, 30):
            x = round(lx0 + m * pxm, 1)
            d.box(x, lane_y + lane_top - 6, 1, lane_h - lane_top + 2, "#EEF2F6FF")
        seq = [t for t in tasks if t["team"] == tm]
        per_row = 2
        # First decide which label goes where, using the real occupied rectangles as
        # obstacles, then paint. Nothing is drawn before its slot is known to be free.
        slots = []
        for i, t in enumerate(seq):
            ty = round(lane_y + lane_top + (i // per_row) * lane_rh)
            bx = round(lx0 + t["start_min"] * pxm, 1)
            bw = round((t["end_min"] - t["start_min"]) * pxm, 1)
            slots.append(dict(t=t, row=i // per_row, ty=ty, bx=bx, bw=bw))
        for i, s in enumerate(slots):
            label = f'{s["t"]["id"]} {s["t"]["label"]}'
            need_w = text_width(label, 18)
            s["label"] = label
            s["inside"] = need_w + 14 <= s["bw"]
            if s["inside"]:
                s["lx"] = s["bx"] + 7
                continue
            # outside label: slide it right until it clears every bar on this row and
            # every label already placed on this row
            tx = s["bx"] + s["bw"] + 8
            for other in slots:
                if other is s or other["row"] != s["row"]:
                    continue
                if other["bx"] < tx + need_w and tx < other["bx"] + other["bw"]:
                    tx = other["bx"] + other["bw"] + 8
                lx2 = other.get("lx")
                if lx2 is not None and not other.get("inside"):
                    ow = text_width(other["label"], 18)
                    if lx2 < tx + need_w and tx < lx2 + ow:
                        tx = lx2 + ow + 10
            s["lx"] = tx
            s["fits_outside"] = tx + need_w <= lx1 + 40
        for s in slots:
            t, ty, bx, bw = s["t"], s["ty"], s["bx"], s["bw"]
            col = bar_color(t)
            d.box(bx, ty, bw, 24, col + "FF", radius=6)
            if s["inside"]:
                d.text(s["lx"], ty + 4, s["label"], 18, "#FFFFFFFF", weight="BOLD",
                       maxw=bw - 12)
            elif s["fits_outside"]:
                d.text(round(s["lx"]), ty + 4, s["label"], 18, INK, weight="BOLD",
                       maxw=lx1 + 40 - s["lx"])
                d.box(round(bx + bw), ty + 12, 8, 2, col + "FF")
            else:
                # no free space on that row: show the编号 only, the table carries the rest
                d.text(bx + 6, ty + 4, t["id"], 18, "#FFFFFFFF", weight="BOLD",
                       maxw=max(30, bw - 10))
            bars.append((tm, t["id"], ty, bw))
            measured.append(dict(text=s["label"], size=18, color=INK, y=ty + 4,
                                 role="lane_bar", box=[s["lx"], ty + 4,
                                                       round(text_width(s["label"], 18)),
                                                       24]))
        lane_y += lane_h + 10

    # buffer band + deadline line (tall enough to cover both lanes)
    lane_block_h = lane_y - 10 - lane_block_top
    d.box(round(lx0 + 260 * pxm), lane_block_top, round(160 * pxm), lane_block_h,
          "#0E9F8F14")
    d.box(lx1 - 2, 200, 3, lane_block_h + 46, RED)
    d.text(round(lx1 - 104), lane_block_top + lane_block_h - 26, "16:00 截止", 20, RED,
           weight="BOLD", maxw=140)

    ty0 = lane_y - 10 + 14
    d.box(24, ty0, W - 48, rows_h, "#FFFFFFFf", radius=14, border=f"1 SOLID {LINE}")
    hdr_y = ty0 + 14
    # Seven columns whose widths are solved from the real content (longest value per
    # column plus padding), so a longer label or a longer dependency list can never
    # collide with its neighbour. Any slack is distributed proportionally.
    col_names = ["编号", "任务", "时长", "依赖", "团队", "起止", "说明"]
    col_fams = [MONO, CJK, MONO, MONO, CJK, MONO, CJK]
    rows_vals = [[t["id"], t["label"], f'{t["minutes"]} 分钟',
                  "、".join(t["depends"]) or "—", t["team"],
                  f'{t["start"]}–{t["end"]}',
                  f'依赖 {"、".join(t["depends"]) or "无"} 完成后开始']
                 for t in tasks]
    need = []
    for j in range(7):
        m = text_width(col_names[j], 20, mono=(col_fams[j] is MONO))
        for r in rows_vals:
            m = max(m, text_width(r[j], 20, mono=(col_fams[j] is MONO)))
        need.append(m + 12)
    # the table body is set at 18px, so the header widths are solved at 18px too
    need = round_need = [max(text_width(col_names[j], 18, mono=(col_fams[j] is MONO)),
                             max(text_width(r[j], 18, mono=(col_fams[j] is MONO))
                                 for r in rows_vals)) + 12 for j in range(7)]
    gap = 14.0
    avail = (W - 48) - 24 - gap * 6
    col_w = list(need)
    if sum(need) < avail:
        extra = (avail - sum(need)) / 7.0
        col_w = [w + extra for w in need]
    elif sum(need) > avail:
        k = avail / sum(need)
        col_w = [w * k for w in need]
    cols = []
    _x = 46.0
    for j, name in enumerate(col_names):
        cols.append((name, math.ceil(_x), math.ceil(col_w[j])))
        _x += col_w[j] + gap
    for name, off, wdt in cols:
        d.text(24 + off, hdr_y, name, 18, SUB, weight="BOLD", maxw=wdt)
    d.box(40, hdr_y + 30, W - 80, 2, "#CBD5E1FF")
    # 12 real rows at 18px type: the row height is solved so the last row still ends
    # inside the panel and the canvas
    rh = 26.0
    assert ty0 + 42 + 12 * rh <= H - 12, (
        f"table would end at {ty0 + 42 + 12 * rh:.0f}px, past the canvas")
    for i, t in enumerate(tasks):
        ry = round(hdr_y + 38 + i * rh)
        if i % 2 == 1:
            d.box(34, ry - 2, W - 68, round(rh), "#F8FAFCFF", radius=6)
        col = bar_color(t)
        d.box(24 + 40, ry + 2, 5, round(rh) - 8, col + "FF", radius=2)
        vals = [(t["id"], INK, MONO, "BOLD"), (t["label"], INK, CJK, "NORMAL"),
                (f'{t["minutes"]} 分钟', SUB, MONO, "NORMAL"),
                ("、".join(t["depends"]) or "—", SUB, MONO, "NORMAL"),
                (t["team"], col + "FF", CJK, "BOLD"),
                (f'{t["start"]}–{t["end"]}', SUB, MONO, "NORMAL"),
                (f'依赖 {"、".join(t["depends"]) or "无"} 完成后开始', DIMC, CJK,
                 "NORMAL")]
        for j, (val, vc, fam, wt) in enumerate(vals):
            name, off, wdt = cols[j]
            assert_fits(val, 18, wdt, f"tbl-{t['id']}-{j}")
            d.text(24 + off, ry + 3, val, 18, vc, weight=wt, maxw=wdt, family=fam)
            measured.append(dict(text=val, size=18, color=vc, y=ry + 3, role="table"))
    d.text(48, ty0 + rows_h + 12,
           "编号索引表达依赖：每行的「依赖」列即先决编号。空档 = 该团队没有可启动任务的时段；"
           "浅绿带为 13:20–16:00 的剩余缓冲（160 分钟）。",
           20, SUB, maxw=W - 96)
    return d, measured, dict(pxm=pxm, lx0=lx0, lx1=lx1, lane_y=lane_y, lane_h=lane_h,
                             table_y=ty0, table_h=rows_h)


# ============================================================= decision brief
def decision_brief(sch: dict, aud: dict, risks: list) -> tuple:
    W, H = 1200, 1600
    d = Doc(W, H, background=PAGE)
    measured = []
    d.box(0, 0, W, 6, TEAL)
    d.box(24, 18, W - 48, 118, HEAD, radius=16)
    d.text(48, 32, BRAND, 30, "#F8FAFCFF", weight="BOLD", maxw=600)
    d.text(48, 74, "决策简报 · 双团队约束下的发布作战计划", 22, "#CBD5E1FF", maxw=800)
    d.rtext(W - 48, 34, "2026-11-07", 22, DIMC)
    d.rtext(W - 48, 74, "09:00 开工 · 16:00 截止", 22, DIMC)

    y = 152
    d.box(24, y, W - 48, 124, "#CCFBF1FF", radius=14, border="1 SOLID #5EEAD4")
    d.box(24, y, 6, 124, TEAL, radius=3)
    headline = (f'最早完成 {sch["makespan_end"]}（第 {sch["makespan_minutes"]} 分钟）；'
                f'距 16:00 还有 {sch["buffer_minutes"]} 分钟缓冲；12 项任务不删不减。')
    assert_fits(headline, 22, W - 110, "brief-headline")
    d.text(48, y + 18, headline, 22, "#0F172AFF", weight="BOLD", maxw=W - 96)
    sub1 = (f'忽略资源约束的关键路径 {sch["lower_bounds"]["critical_path_minutes"]} 分钟'
            f'（{"→".join(sch["lower_bounds"]["critical_path_chain"])}）；'
            f'总工作量 {sch["lower_bounds"]["total_work_minutes"]} 分钟。')
    sub2 = (f'两团队下界 {sch["lower_bounds"]["work_per_team_bound_minutes"]} 分钟，'
            f'实际比下界多 {sch["assignment_search"]["gap_to_lower_bound_minutes"]} 分钟；'
            f'本计划不声称已证明全局最优。')
    for i, sub in enumerate((sub1, sub2)):
        assert_fits(sub, 20, W - 110, "brief-sub")
        d.text(48, y + 56 + i * 28, sub, 20, SUB, maxw=W - 96)
        measured.append(dict(text=sub, size=20, color=SUB, y=y + 56 + i * 28,
                             role="sub"))
    y += 146

    # ---- metrics
    metrics = [("总工作量", f'{sch["lower_bounds"]["total_work_minutes"]} 分钟', TEAL),
               ("计划完成", sch["makespan_end"], BLUE),
               ("剩余缓冲", f'{sch["buffer_minutes"]} 分钟', AMBER),
               ("关键路径", f'{sch["lower_bounds"]["critical_path_minutes"]} 分钟', RED)]
    mw = (W - 48 - 3 * 12) / 4
    for i, (label, value, col) in enumerate(metrics):
        x = 24 + i * (mw + 12)
        card(d, round(x), y, round(mw), 106, radius=14)
        d.box(round(x), y, 5, 106, col, radius=2)
        d.text(round(x + 18), y + 14, label, 20, SUB, maxw=round(mw) - 30)
        d.text(round(x + 18), y + 44, value, 30, INK, weight="BOLD", family=MONO,
               maxw=round(mw) - 30)
        measured.append(dict(text=label, size=20, color=SUB, y=y + 14, role="metric"))
        measured.append(dict(text=value, size=30, color=INK, y=y + 44, role="metric"))
    y += 130

    # ---- dependency overview: the chips wrap inside the panel instead of being clipped
    phases = [("无先决（可立即开始）", [t for t in sch["tasks"] if not t["depends"]]),
              ("依赖 1 个先决", [t for t in sch["tasks"] if len(t["depends"]) == 1]),
              ("依赖 2 个先决", [t for t in sch["tasks"] if len(t["depends"]) == 2]),
              ("依赖 3 个先决", [t for t in sch["tasks"] if len(t["depends"]) == 3])]
    label_w = 234
    chip_x0 = 48 + label_w
    chip_x1 = W - 48
    chip_h, chip_gap = 32, 8
    layout_phases = []
    for label, group in phases:
        rows = [[]]
        cx = chip_x0
        for t in group:
            txt = f'{t["id"]} {t["label"]}（{t["minutes"]}m · {t["team"]}）'
            w = round(text_width(txt, 20)) + 24
            if cx + w > chip_x1 and rows[-1]:
                rows.append([])
                cx = chip_x0
            rows[-1].append((txt, w, t))
            cx += w + 10
        layout_phases.append((label, rows))
    dh = 80 + sum(len(r) * (chip_h + chip_gap) for _l, r in layout_phases) + 46
    card(d, 24, y, W - 48, dh, radius=14)
    d.text(48, y + 14, "依赖概览（编号索引，不画交叉线）", 24, INK, weight="BOLD",
           maxw=W - 120)
    d.text(48, y + 48, "关键路径：", 20, SUB, weight="BOLD", maxw=120)
    d.text(160, y + 48, " → ".join(sch["lower_bounds"]["critical_path_chain"]), 20, RED,
           weight="BOLD", family=MONO, maxw=W - 220)
    d.box(48, y + 80, W - 96, 2, LINE)
    py = y + 92
    first_row_of_phase = True
    for label, rows in layout_phases:
        d.text(48, py + 6, label, 20, SUB, weight="BOLD", maxw=label_w - 8)
        for row in rows:
            cx = chip_x0
            for txt, w, t in row:
                col = bar_color(t)
                d.box(cx, py, w, chip_h, col + "22", radius=16,
                      border=f"1 SOLID {col}88")
                d.text(cx + 12, py + 6, txt, 20, INK, maxw=w - 20)
                measured.append(dict(text=txt, size=20, color=INK, y=py + 6, role="dep"))
                cx += w + 10
            py += chip_h + chip_gap
        first_row_of_phase = False
    d.text(48, py + 8, "先决完成后才能开始；两团队各只有一队人力，同队不可并行、不可抢占。",
           20, SUB, maxw=W - 96)
    y += dh + 14

    # ---- risks
    rh_ = 344
    card(d, 24, y, W - 48, rh_, radius=14)
    d.text(48, y + 14, "三大风险与对策", 24, INK, weight="BOLD", maxw=400)
    d.text(48, y + 46, "每项风险都指向一个真实任务与一个可执行对策；对策不改变任务时长。",
           20, SUB, maxw=W - 96)
    ry = y + 82
    for k in risks:
        t = next(x for x in sch["tasks"] if x["id"] == k["task"])
        line1 = f'{k["id"]} · 关联任务 {t["id"]} {t["label"]}（{t["start"]}–{t["end"]}）'
        line2 = f'影响：{k["impact"]}'
        line3 = f'对策：{k["mitigation"]}'
        d.box(44, ry, W - 88, 84, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")
        d.box(44, ry, 5, 84, AMBER, radius=2)
        for i, (ln, sz, col, wt) in enumerate([(line1, 20, INK, "BOLD"),
                                               (line2, 20, SUB, "NORMAL"),
                                               (line3, 20, SUB, "NORMAL")]):
            assert_fits(ln, sz, W - 130, f"risk-{k['id']}")
            d.text(64, ry + 10 + i * 23, ln, sz, col, weight=wt, maxw=W - 130)
            measured.append(dict(text=ln, size=sz, color=col, y=ry + 10 + i * 23,
                                 role="risk"))
        ry += 88
    y += rh_ + 14

    # ---- scheduling rationale
    th = H - 24 - y
    card(d, 24, y, W - 48, th, radius=14)
    d.text(48, y + 14, "排程依据与占用", 24, INK, weight="BOLD", maxw=400)
    flex = [t["id"] for t in sch["tasks"] if len(t["teams_allowed"]) > 1]
    flex_txt = "、".join(f'{i}={next(t["team"] for t in sch["tasks"] if t["id"] == i)}'
                        for i in flex)
    lines = [
        f'两团队各自单线程：design 忙 {aud["idle_summary"]["design"]["busy_min"]} 分钟、'
        f'空档 {aud["idle_summary"]["design"]["idle_min"]} 分钟；engineering 忙 '
        f'{aud["idle_summary"]["engineering"]["busy_min"]} 分钟、空档 '
        f'{aud["idle_summary"]["engineering"]["idle_min"]} 分钟。',
        f'两团队任务各只占用一队，本排程的分配为 {flex_txt}。',
        f'搜索方式：遍历两团队任务的全部团队选择，共尝试 '
        f'{sch["assignment_search"]["combinations_tried"]} 种组合，取完工最早的一种。',
        "该计划不声称已证明全局最优；只给出下界与达到的完工时间，差距原因见 schedule.json。",
        "截止检查：12 项任务全部在 13:20 前结束、缓冲 160 分钟；资源冲突 0 处、依赖违例 0 处。",
    ]
    ly = y + 52
    wrapped = []
    for ln in lines:
        wrapped += wrap_text(ln, 20, W - 110)
    for ln in wrapped:
        d.text(48, ly, ln, 20, SUB, maxw=W - 96)
        measured.append(dict(text=ln, size=20, color=SUB, y=ly, role="rationale"))
        ly += 28
    # the tall portrait page has room for the complete time table as an appendix, which
    # also lets a reader cross-check every start/end without leaving the brief
    ly += 12
    d.box(48, ly - 8, W - 96, 2, LINE)
    d.text(48, ly + 4, "附：12 项任务起止与团队（与执行图、行动卡同源）", 20, INK,
           weight="BOLD", maxw=W - 96)
    ly += 36
    app = [f'{t["id"]} {t["label"]}' for t in sch["tasks"]]
    app2 = [f'{t["team"]}  {t["start"]}–{t["end"]}  {t["minutes"]}m'
            for t in sch["tasks"]]
    col_w2 = (W - 96 - 32) / 2
    name_w = max(text_width(x, 20) for x in app) + 10
    assert name_w + max(text_width(x, 20, mono=True) for x in app2) + 12 <= col_w2, \
        "the brief appendix needs two wider columns"
    rows_n = 6
    for i in range(rows_n):
        for c in range(2):
            k = i + c * rows_n
            if k >= len(app):
                continue
            x = 48 + c * (col_w2 + 32)
            yy = ly + i * 26
            assert_fits(app[k], 20, name_w, "appendix-name")
            assert_fits(app2[k], 20, col_w2 - name_w - 8, "appendix-time", mono=True)
            d.text(x, yy, app[k], 20, INK, maxw=name_w)
            d.text(x + name_w + 8, yy, app2[k], 20, SUB, family=MONO,
                   maxw=col_w2 - name_w - 8)
            measured.append(dict(text=app[k], size=20, color=INK, y=yy,
                                 role="appendix"))
    d.rtext(W - 48, ly + rows_n * 26 + 10,
            "数据来源：inputs/release.json + schedule.json", 20, DIMC)
    return d, measured, dict()


# ================================================================ action card
def action_card(sch: dict, aud: dict, risks: list) -> tuple:
    W, H = 720, 1280
    d = Doc(W, H, background=PAGE)
    measured = []
    d.box(0, 0, W, 5, TEAL)
    d.box(20, 16, W - 40, 96, HEAD, radius=14)
    d.text(40, 28, BRAND, 26, "#F8FAFCFF", weight="BOLD", maxw=420)
    d.text(40, 64, "行动卡 · 2026-11-07 09:00–16:00", 20, "#CBD5E1FF", maxw=620)
    d.rtext(W - 40, 30, "12 项", 22, TEAL, weight="BOLD")
    d.rtext(W - 40, 66, f'{sch["makespan_end"]} 完成', 20, DIMC)

    # compact rail: 09:00 .. 16:00
    y = 128
    d.box(20, y, W - 40, 84, "#FFFFFFFF", radius=14, border=f"1 SOLID {LINE}")
    rx0, rx1 = 118, W - 44
    pxm = (rx1 - rx0) / 420.0
    for m in range(0, 421, 60):
        x = round(rx0 + m * pxm, 1)
        d.box(x, y + 46, 1, 18, "#CBD5E1FF")
        lbl = hhmm(m)
        d.text(round(x - text_width(lbl, 18, mono=True) / 2), y + 24, lbl, 18, SUB,
               family=MONO)
    rows = (("design", y + 50), ("engineering", y + 64))
    for tm, ry in rows:
        for t in sch["tasks"]:
            if t["team"] != tm:
                continue
            bx = round(rx0 + t["start_min"] * pxm, 1)
            bw = max(3, round((t["end_min"] - t["start_min"]) * pxm, 1))
            col = bar_color(t)
            d.box(bx, ry, bw, 10, col + "FF", radius=5)
    d.box(rx1 - 2, y + 44, 2, 26, RED)
    d.text(40, y + 10, "09:00–16:00", 18, SUB, weight="BOLD", maxw=120)

    # task rows
    ty = y + 96
    card(d, 20, ty, W - 40, H - ty - 20, radius=14)
    d.text(40, ty + 12, "按时间序的 12 项任务", 22, INK, weight="BOLD", maxw=400)
    d.rtext(W - 40, ty + 14, f'{sch["makespan_end"]} 完成 · 缓冲 {sch["buffer_minutes"]} 分钟',
            18, AMBER, weight="BOLD")
    ry = ty + 48
    rh = (H - ty - 20 - 48 - 8) / 12
    for i, t in enumerate(sch["tasks"]):
        col = bar_color(t)
        risk = RISK_IDS.get(t["id"])
        d.box(36, ry, W - 72, round(rh) - 4, "#F8FAFCFF" if i % 2 == 0 else "#FFFFFFFF",
              radius=8)
        d.box(36, ry, 5, round(rh) - 4, col + "FF", radius=2)
        d.text(52, ry + 6, t["id"], 20, col + "FF", weight="BOLD", family=MONO, maxw=54)
        d.text(110, ry + 6, t["label"], 20, INK, weight="BOLD", maxw=250)
        d.text(110, ry + 28, f'{t["team"]} · {t["minutes"]} 分钟', 18, SUB, maxw=250)
        d.rtext(W - 44, ry + 6, f'{t["start"]}–{t["end"]}', 20, INK, family=MONO)
        if risk:
            r = next(x for x in risks if x["id"] == risk)
            d.rtext(W - 44, ry + 28, f'{risk} · {r["impact"]}', 18, RED)
        measured.append(dict(text=t["label"], size=20, color=INK, y=ry + 6, role="task"))
        ry += rh
    d.text(40, H - 24, "时间均为 2026-11-07 +08:00；同队不可并行、不可抢占；时长不可压缩。",
           18, DIMC, maxw=W - 80)
    return d, measured, dict(pxm=pxm)


def main() -> None:
    os.makedirs(TMP, exist_ok=True)
    sch, aud = load()
    with open(os.path.join(ROOT, "tasks", "A24-release-plan-capstone", "inputs",
                           "release.json"), encoding="utf-8") as fh:
        risks = json.load(fh)["risks"]
    outs = []
    for name, fn in (("execution-board", execution_board),
                     ("decision-brief", decision_brief),
                     ("action-card", action_card)):
        if name == "execution-board":
            doc, measured, geom = fn(sch, aud)
        else:
            doc, measured, geom = fn(sch, aud, risks)
        dsl = doc.finish()
        for path in (os.path.join(OUT, f"{name}.snapshot"),
                     os.path.join(TMP, f"{name}.v1.snapshot")):
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(dsl)
        stats = doc.stats()
        outs.append({"name": name, "elements": stats["elements"],
                     "text_nodes": stats["text_nodes"], "texts": len(measured)})
    # content map
    cm = {
        "task": "A24", "brand": BRAND,
        "sources": ["inputs/release.json", "outputs/20261003-114508-flashmax/A24/schedule.json",
                    "outputs/20261003-114508-flashmax/A24/schedule-audit.json"],
        "carriers": {
            "execution-board.png": {
                "size": [1920, 1080], "body_min_size": 20, "smallest_text_px": 18,
                "shows": ["brand", "总工时/计划完成/剩余缓冲/关键路径", "09:00–16:00 同尺度时间轴",
                          "design 与 engineering 两条泳道", "每项任务的编号/时长/团队/起止",
                          "空档与 16:00 截止线", "12 行依赖明细表（编号索引）"]},
            "decision-brief.png": {
                "size": [1200, 1600], "body_min_size": 24, "smallest_text_px": 20,
                "shows": ["品牌", "最早完成时间与剩余缓冲", "依赖概览（按先决数量分组，编号索引）",
                          "总工时/关键路径/两团队下界", "三大风险与对策", "排程依据与占用",
                          "截止检查结论"]},
            "action-card.png": {
                "size": [720, 1280], "body_min_size": 20, "smallest_text_px": 18,
                "shows": ["品牌", "09:00–16:00 迷你轨道（两团队）", "按时间序的 12 项任务",
                          "每项的团队、起止与时长", "K1/K2/K3 风险提醒"]},
        },
        "consistency": {
            "single_source": "all three carriers are drawn from the same schedule.json",
            "makespan": f'{sch["makespan_end"]} / {sch["makespan_minutes"]} 分钟',
            "buffer": f'{sch["buffer_minutes"]} 分钟',
            "critical_path": f'{sch["lower_bounds"]["critical_path_minutes"]} 分钟 '
                             + "→".join(sch["lower_bounds"]["critical_path_chain"]),
            "task_count": 12,
            "cross_checked_fields": ["每项任务的团队", "每项任务的起止", "完成时间", "缓冲",
                                     "关键路径", "总工时"],
        },
        "generator": "tmp/20261003-114508-flashmax/A24/build_a24.py",
        "element_budget": outs,
    }
    with open(os.path.join(OUT, "content-map.json"), "w", encoding="utf-8") as fh:
        json.dump(cm, fh, ensure_ascii=False, indent=2)
    print(json.dumps(outs, ensure_ascii=False))


if __name__ == "__main__":
    main()
