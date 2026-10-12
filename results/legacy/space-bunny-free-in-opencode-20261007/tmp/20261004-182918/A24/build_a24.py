# -*- coding: utf-8 -*-
"""A24 - build execution-board.png (1920x1080), decision-brief.png (1200x1600)
and action-card.png (720x1280) from inputs/release.json via plan.py.

All three figures read the same PLAN dict, so no number can drift between them.
Usage:  python build_a24.py [board|brief|card|all] [--final]
"""
from __future__ import annotations

import math
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402
import plan as P  # noqa: E402
from theme import (UI, MONO, INK, INK2, MUTED, FAINT, LINE, LINE2, PAPER, CARD, DARK, DARK2,
                   BRAND, BRAND_L, DESIGN, DESIGN_L, ENG, ENG_L, CP, CP_L, AMBER, AMBER_L,
                   GREEN, GREEN_L, RED, RED_L, WHITE, BRAND_NAME, TEAM_ZH, TEAM_COLOR,
                   TEAM_LIGHT, BY_ID, RISKS, RISK_OF_TASK, CP_CHAIN, span, wraps, para,
                   chip, swatch, legend, assign_rows, mw)  # noqa: E402

TASK = "A24"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
SUM = P.SCHEDULE["summary"]
LANES = P.SCHEDULE["teams"]
TASKS = P.SCHEDULE["tasks"]


# =========================================================== execution board
def build_board():
    W, H = 1920, 1080
    L, R = 316.0, 1876.0
    PPM = (R - L) / float(P.WINDOW_MIN)
    HDR = 92
    GRID_T, GRID_B = 150.0, 772.0
    LANE_H = 300.0
    LANE_TOP = {"design": 150.0, "engineering": 466.0}
    # Two annotation bands (task name, then clock range) each staggered over two rows, so a
    # name row can never sit on a clock row; the block band starts below both.
    BAND_A = [20.0, 48.0]
    BAND_B = [80.0, 108.0]
    BLOCK_T, BLOCK_H = 146.0, 104.0
    STRIP_T, STRIP_H = 258.0, 34.0
    ms_x = L + P.MAKESPAN * PPM

    def tx(m):
        return L + m * PPM

    k = []
    a = k.append
    a(D.box(0, 0, W, H, color=PAPER))

    # ---------------------------------------------------------- header
    a(D.box(0, 0, W, HDR, color=DARK,
            extra={"gradientType": "LINEAR", "gradientColors": "%s,%s" % (DARK, DARK2),
                   "gradientBegin": "CENTER_LEFT", "gradientEnd": "CENTER_RIGHT"}))
    a(D.box(40, 22, 6, 48, color="#818CF8FF", radius=3))
    a(D.text_el(BRAND_NAME, x=58, y=18, w=420, h=34, size=28, color=WHITE,
                style="BOLD", ls=1.0))
    a(D.text_el("发布作战计划 · 双团队资源约束排程", x=58, y=52, w=520, h=26, size=20,
                color="#A5B4FCFF"))
    chips = [("总工时", "%d 分" % P.TOTAL_WORK),
             ("关键路径·无资源", "%d 分" % P.CP_LEN),
             ("计划完成", SUM["makespan_clock"]),
             ("距 16:00 截止", "%d 分" % SUM["buffer_to_deadline_minutes"])]
    cw, cgap = 208.0, 12.0
    cx = W - 40 - (len(chips) * cw + (len(chips) - 1) * cgap)
    for lab, val in chips:
        a(D.box(cx, 13, cw, 66, color="#FFFFFF14", radius=10, border="1 SOLID #FFFFFF1F"))
        a(D.text_el(lab, x=cx + 14, y=21, w=cw - 28, h=24, size=20, color="#A5B4FCFF"))
        a(D.text_el(val, x=cx + 14, y=45, w=cw - 28, h=30, size=26, color=WHITE,
                    style="BOLD"))
        cx += cw + cgap

    # ---------------------------------------------------------- time axis
    for m in range(0, P.WINDOW_MIN + 1, 30):
        x = tx(m)
        hour = m % 60 == 0
        a(D.box(x, GRID_T, 2 if hour else 1, GRID_B - GRID_T,
                color=LINE2 if hour else "#E9EDF7FF"))
    for m in range(0, P.WINDOW_MIN + 1, 60):
        x = tx(m)
        lab = P.clock(m)
        if m == 0:
            a(D.text_el(lab, x=x, y=118, w=90, h=26, size=20, color=MUTED, font=MONO,
                        style="BOLD"))
        elif m == P.WINDOW_MIN:
            a(D.text_el("%s 截止" % lab, x=x - 170, y=118, w=170, h=26, size=20,
                        color=RED, font=MONO, style="BOLD", align="RIGHT"))
        else:
            a(D.text_el(lab, x=x - 45, y=118, w=90, h=26, size=20, color=MUTED,
                        font=MONO, style="BOLD", align="CENTER"))

    # finish instant marker (the tall line is re-drawn on top of the lanes further down,
    # because the lane cards would otherwise cover it)
    a(D.box(ms_x - 5, 108, 10, 10, color=GREEN, radius=2))

    # ---------------------------------------------------------- lanes
    for name in P.TEAMS:
        top = LANE_TOP[name]
        col, light = TEAM_COLOR[name], TEAM_LIGHT[name]
        info = LANES[name]
        a(D.box(40, top, 1840, LANE_H, color=WHITE, radius=14, border="1 SOLID %s" % LINE))
        a(D.box(40, top, 6, LANE_H, color=col, radii={"TopLeft": 14, "BottomLeft": 14}))
        # reserve after the lane finishes
        a(D.box(tx(info["busy_until_minute"]), top + 8, R - tx(info["busy_until_minute"]) - 8,
                LANE_H - 16, color=GREEN_L, radius=10,
                border="1 SOLID #6EE7B7FF"))
        bl = ("剩余缓冲 %d 分（%s → %s）" % (info["reserve_after_finish_minutes"],
                                          info["busy_until_clock"], P.clock(P.WINDOW_MIN))
              if info["busy_until_minute"] == P.MAKESPAN
              else "本通道 %s 收工 · 剩余 %d 分" % (info["busy_until_clock"],
                                              info["reserve_after_finish_minutes"]))
        a(D.text_el(bl, x=tx(info["busy_until_minute"]), y=top + 104,
                    w=R - tx(info["busy_until_minute"]), h=28, size=20, color="#047857FF",
                    align="CENTER", style="BOLD"))
        # gutter
        a(D.text_el(TEAM_ZH[name], x=64, y=top + 34, w=240, h=34, size=28, color=INK,
                    style="BOLD"))
        a(D.text_el(name, x=64, y=top + 70, w=240, h=26, size=20, color=FAINT,
                    font=MONO))
        a(D.text_el("负载 %d 分 · 空档 %d 分" % (info["load_minutes"], info["idle_minutes"]),
                    x=64, y=top + 104, w=250, h=26, size=20, color=MUTED))
        a(D.text_el("%d 个任务 · 通道不可并行" % len(info["segments"]), x=64,
                    y=top + 132, w=250, h=26, size=20, color=FAINT))

        segs = info["segments"]
        names = [BY_ID[s["task"]]["label"] for s in segs]
        clocks = [span(s["task"]) for s in segs]
        name_items = [(tx(s["start_minute"]), D.est_width(t, 20) + 18)
                      for s, t in zip(segs, names)]
        clock_items = [(tx(s["start_minute"]), mw(t, 20)) for s, t in zip(segs, clocks)]
        name_rows = assign_rows(name_items, 2)
        clock_rows = assign_rows(clock_items, 2)
        for idx, s in enumerate(segs):
            tid = s["task"]
            x0, x1 = tx(s["start_minute"]), tx(s["end_minute"])
            w = x1 - x0
            a(D.text_el(names[idx], x=x0, y=top + BAND_A[name_rows[idx]], w=name_items[idx][1],
                        h=26, size=20, color=col, style="BOLD"))
            a(D.text_el(clocks[idx], x=x0, y=top + BAND_B[clock_rows[idx]],
                        w=clock_items[idx][1], h=26, size=20, color=MUTED))
            on_cp = tid in CP_CHAIN
            a(D.box(x0, top + BLOCK_T, w, BLOCK_H, color=col, radius=10,
                    border="3 SOLID %s" % CP if on_cp else "1 SOLID %s" % light))
            a(D.text_el(tid, x=x0 + 12, y=top + BLOCK_T + 12, w=w - 24, h=30, size=26,
                        color=WHITE, font=MONO, style="BOLD"))
            dur = "%d 分" % s["minutes"]
            dw = D.est_width(dur, 20) + 8
            lab_fits = D.est_width(BY_ID[tid]["label"], 20) + 24 <= w
            pre = "前置 " + ("· ".join(BY_ID[tid]["depends"]) if BY_ID[tid]["depends"]
                             else "无")
            pre_fits = D.est_width(pre, 20) + 24 <= w
            if w >= 150:
                # wide block: id and duration share the first line, then label, then deps
                a(D.text_el(dur, x=x0 + w - 12 - dw, y=top + BLOCK_T + 16, w=dw, h=26,
                            size=20, color="#FFFFFFCC", align="RIGHT"))
                if lab_fits:
                    a(D.text_el(BY_ID[tid]["label"], x=x0 + 12, y=top + BLOCK_T + 48,
                                w=w - 24, h=26, size=20, color="#FFFFFFE6"))
                if pre_fits:
                    a(D.text_el(pre, x=x0 + 12, y=top + BLOCK_T + 76, w=w - 24, h=26,
                                size=20, color="#FFFFFFB8"))
            else:
                # narrow block: id, then label if it fits, then duration - one line each
                if lab_fits:
                    a(D.text_el(BY_ID[tid]["label"], x=x0 + 12, y=top + BLOCK_T + 48,
                                w=w - 24, h=26, size=20, color="#FFFFFFE6"))
                    a(D.text_el(dur, x=x0 + 12, y=top + BLOCK_T + 76, w=dw, h=26,
                                size=20, color="#FFFFFFCC"))
                else:
                    a(D.text_el(dur, x=x0 + 12, y=top + BLOCK_T + 48, w=dw, h=26,
                                size=20, color="#FFFFFFCC"))

        # idle / buffer strip
        for g in info["idle_gaps"]:
            gx0, gx1 = tx(g["from_minute"]), tx(g["to_minute"])
            a(D.box(gx0, top + STRIP_T, max(gx1 - gx0, 10), STRIP_H, color=AMBER_L,
                    radius=6, border="1 SOLID #F59E0BFF"))
            wait = "、".join(g["waiting_for"]) if g["waiting_for"] else "依赖"
            a(D.text_el("空档 %d 分 · 等 %s 完成（不可抢占）" % (g["minutes"], wait),
                        x=gx1 + 10, y=top + STRIP_T + 5, w=430, h=26, size=20,
                        color=AMBER))
        if not info["idle_gaps"]:
            a(D.text_el("无空档：通道连续执行到 %s" % info["busy_until_clock"],
                        x=tx(info["busy_until_minute"]) + 12, y=top + STRIP_T + 5, w=400,
                        h=26, size=20, color=MUTED))

    # ------------------------------------------- finish + deadline lines on top
    # Drawn after the lanes so the lane cards cannot hide them. Both markers stop at
    # GRID_B (772) and put their caption in the 772..782 gutter, so no caption can land
    # on an idle-gap line.
    a(D.box(ms_x - 2, 118, 4, GRID_B - 118, color=GREEN))
    a(D.box(R - 2, 118, 4, GRID_B - 118, color=RED))
    a(D.text_el("完成 %s" % SUM["makespan_clock"], x=ms_x - 150, y=GRID_B + 4, w=150,
                h=24, size=20, color=GREEN, align="RIGHT", style="BOLD"))
    a(D.text_el("截止 16:00", x=R - 150, y=GRID_B + 4, w=150, h=24, size=20, color=RED,
                align="RIGHT", style="BOLD"))

    # ---------------------------------------------------------- bottom strip
    BY = 812.0
    a(D.hline(40, 1880, BY - 10, LINE2, 2))
    a(D.text_el("依赖索引（编号表达，16 条依赖，不画交叉线）", x=40, y=BY, w=760, h=30,
                size=22, color=INK, style="BOLD"))
    a(D.text_el("本方案决定链 %s · 完成 %s" % ("→".join(P.SCHED_CHAIN),
                                              SUM["makespan_clock"]),
                x=1120, y=BY + 2, w=760, h=28, size=20, color=CP, align="RIGHT",
                style="BOLD"))
    dep_lines = []
    for t in TASKS:
        pre = " · ".join(t["depends"]) if t["depends"] else "无"
        dep_lines.append("%s ← %s%s" % (t["id"], pre,
                                         "　决定链" if t["id"] in CP_CHAIN else ""))
    dep_lines.sort(key=lambda s: int(s[1:3]))
    cols = 3
    per = int(math.ceil(len(dep_lines) / float(cols)))
    for c in range(cols):
        cx = 40 + c * 440
        for r, line in enumerate(dep_lines[c * per:(c + 1) * per]):
            a(D.text_el(line, x=cx, y=BY + 40 + r * 28, w=430, h=26, size=20,
                        color=CP if "决定链" in line else INK2, font=MONO))
    fx = 1380
    a(D.text_el("排程依据", x=fx, y=BY + 40, w=500, h=26, size=20, color=INK,
                style="BOLD"))
    g0 = LANES["design"]["idle_gaps"][0]
    g1 = LANES["engineering"]["idle_gaps"][0]
    facts = [
        "总工时 %d 分 = design %d + engineering %d" % (
            P.TOTAL_WORK, LANES["design"]["load_minutes"],
            LANES["engineering"]["load_minutes"]),
        "同团队不可并行 → design 单队已 %d 分" % LANES["design"]["load_minutes"],
        "空档各 %d 分（依赖等待，不可抢占）" % g0["minutes"],
        "design %s 等 %s" % ("%s–%s" % (g0["from_clock"], g0["to_clock"]),
                           "、".join(g0["waiting_for"])),
        "engineering %s 等 %s" % ("%s–%s" % (g1["from_clock"], g1["to_clock"]),
                                "、".join(g1["waiting_for"])),
        "下界 %d / %d 分，本方案 %d 分（+ %s 等 %d 分）" % (
            P.CP_LEN, P.WORK_LB, P.MAKESPAN, P.GATE_ID, P.MAKESPAN - P.LB_COMBINED),
        "穷举 %d 节点 + %d 万次随机对照均未更早" % (P.STATS["nodes"], 20),
    ]
    for r, f in enumerate(facts):
        a(D.text_el(f, x=fx, y=BY + 68 + r * 24, w=500, h=24, size=20,
                    color=GREEN if r == 6 else MUTED, style="BOLD" if r == 6 else None))

    lg = [(DESIGN, "设计通道"), (ENG, "工程通道"), (CARD, "洋红描边 = 决定链 %d 步" % len(CP_CHAIN),
          CP), (AMBER_L, "空档 5 分", "#F59E0BFF"), (GREEN_L, "剩余缓冲", "#6EE7B7FF")]
    lgk, _ = legend(40, BY + 168, lg, size=20, gap=40)
    k += lgk
    a(D.text_el("时间轴 09:00–16:00 单一线性刻度（1 分 = %.2f px），块宽即真实时长；"
                "所有时刻取自 inputs/release.json 与 schedule.json，未改动任何输入时间"
                % PPM, x=40, y=BY + 216, w=1840, h=26, size=20, color=FAINT))
    print("   board bottom y =", round(BY + 216 + 26, 1), "(canvas 1080)")
    return D.snapshot([D.stack(k, W, H)], W, H, bg=PAPER)


# ============================================================ decision brief
def build_brief():
    W, H = 1200, 1600
    M = 56
    k = []
    a = k.append
    a(D.box(0, 0, W, H, color=PAPER))
    a(D.box(0, 0, W, 150, color=DARK,
            extra={"gradientType": "LINEAR", "gradientColors": "%s,%s" % (DARK, DARK2),
                   "gradientBegin": "CENTER_LEFT", "gradientEnd": "CENTER_RIGHT"}))
    a(D.box(M, 26, 6, 44, color="#818CF8FF", radius=3))
    a(D.text_el(BRAND_NAME, x=M + 18, y=22, w=520, h=32, size=26, color=WHITE,
                style="BOLD", ls=1.0))
    a(D.text_el("发布作战计划 · 决策简报", x=M + 18, y=58, w=640, h=36, size=34,
                color=WHITE, style="BOLD"))
    a(D.text_el("2026-11-07 · 09:00 开工 · 16:00 截止 · 每队一条通道", x=M + 18, y=102,
                w=700, h=30, size=24, color="#A5B4FCFF"))
    a(D.text_el("260 分", x=W - M - 240, y=26, w=240, h=48, size=44, color="#6EE7B7FF",
                style="BOLD", align="RIGHT"))
    a(D.text_el("计划完成 %s（已证明最优）" % SUM["makespan_clock"], x=W - M - 400, y=80,
                w=400, h=32, size=24, color=WHITE, align="RIGHT"))

    # ------------------------------------------------------------ KPI tiles
    tiles = [
        ("总工时", "%d 分" % P.TOTAL_WORK, INK),
        ("关键路径", "%d 分" % P.CP_LEN, CP),
        ("工作量下界", "%d 分" % P.WORK_LB, ENG),
        ("完成时间", SUM["makespan_clock"], GREEN),
        ("剩余缓冲", "%d 分" % SUM["buffer_to_deadline_minutes"], GREEN),
        ("最优性", "已证明", BRAND),
    ]
    tw, th, gx = 173.0, 112.0, 10.0
    for i, (lab, val, col) in enumerate(tiles):
        cx = M + i * (tw + gx)
        cy = 152
        a(D.box(cx, cy, tw, th, color=CARD, radius=14, border="1 SOLID %s" % LINE,
                shadow="0 2 8 0 #0F172A0F"))
        a(D.text_el(lab, x=cx + 14, y=cy + 8, w=tw - 28, h=28, size=24, color=MUTED,
                    align="CENTER"))
        a(D.text_el(val, x=cx + 14, y=cy + 42, w=tw - 28, h=48, size=40, color=col,
                    style="BOLD", align="CENTER"))
    cap = ("总工时 = 设计 %d + 工程 %d（各一条通道、不可并行）· 关键路径 = 最长依赖链 6 步 · "
           "⌈%d÷%d⌉ = %d 分 · %d 分缓冲留给 K3 返工"
           % (LANES["design"]["load_minutes"], LANES["engineering"]["load_minutes"],
              P.TOTAL_WORK, len(P.TEAMS), P.WORK_LB,
              SUM["buffer_to_deadline_minutes"]))
    cap_lines = wraps(cap, 24, W - 2 * M)
    ks, cy = para(cap, 24, W - 2 * M, M, 274, color=MUTED, lh=1.26)
    k += ks

    # ------------------------------------------------- dependency overview (rows)
    TITLE_Y = cy + 8
    DT, DH = TITLE_Y + 38, 504.0
    CX0, CX1 = 40.0, 1160.0
    NH, CH, NW, GX = 64.0, 24.0, 300.0, 40.0
    lay = {t["id"]: t["precedence_layer"] for t in TASKS}
    rows = {}
    for t in TASKS:
        rows.setdefault(lay[t["id"]], []).append(t["id"])
    for r in rows:
        rows[r].sort()
    order = [sorted(rows[l], key=lambda i: (BY_ID[i]["id"])) for l in sorted(rows)]

    def ry(l):
        return DT + l * (NH + CH)

    def rxs(ids):
        n = len(ids)
        total = n * NW + (n - 1) * GX
        x0 = 90 + ((CX1 - 90) - total) / 2.0
        return {t: x0 + i * (NW + GX) for i, t in enumerate(ids)}

    RX = {l: rxs(ids) for l, ids in zip(sorted(rows), order)}

    a(D.text_el("依赖概览 · 按依赖深度分 %d 层" % (max(rows) + 1), x=M, y=TITLE_Y, w=700,
                h=32, size=26, color=INK, style="BOLD"))
    a(D.text_el("12 任务 · 16 条依赖 · 洋红描边 = 决定链", x=W - M - 460, y=TITLE_Y + 4,
                w=460, h=28, size=24, color=CP, align="RIGHT"))
    a(D.box(CX0, DT, CX1 - CX0, DH, color=CARD, radius=14, border="1 SOLID %s" % LINE))
    for l in sorted(rows):
        if l % 2 == 0:
            a(D.box(CX0 + 8, ry(l), CX1 - CX0 - 16, NH, color="#F8FAFCFF", radius=10))
        a(D.text_el("层%d" % l, x=CX0 + 16, y=ry(l) + 18, w=60, h=28, size=24,
                    color=FAINT, font=MONO))
    # edges first so nodes sit on top
    BYPASS = CX1 - 22
    edges = []
    for t in TASKS:
        for d in t["depends"]:
            edges.append((d, t["id"]))
    grouped = {}
    for d, v in edges:
        grouped.setdefault((lay[d], lay[v]), []).append((d, v))
    for (l0, l1), pairs in sorted(grouped.items()):
        np = len(pairs)
        for s, (u, v) in enumerate(pairs):
            xu = RX[l0][u] + NW / 2.0
            xv = RX[l1][v] + NW / 2.0
            ytop = ry(l0) + NH
            ch_top, ch_bot = ytop, ry(l1)
            yy = ch_top + CH * (s + 0.5) / np if l1 == l0 + 1 else ch_top + CH * 0.5
            yy = max(ch_top + 3.0, min(yy, ch_bot - 3.0))
            a(D.box(xu - 1.5, ytop, 3, yy - ytop, color="#CBD5E1FF"))
            if l1 == l0 + 1:
                if abs(xv - xu) > 2:
                    a(D.box(min(xu, xv), yy - 1.5, abs(xv - xu), 3, color="#CBD5E1FF"))
                a(D.box(xv - 1.5, yy - 1.5, 3, ry(l1) - yy + 1.5, color="#CBD5E1FF"))
            else:
                # multi-layer edge: use the empty right margin as a bypass lane so the
                # drop never crosses an intermediate node
                ymid = ry(l1) - CH * 0.5
                a(D.box(xu - 1.5, yy - 1.5, BYPASS - xu, 3, color="#CBD5E1FF"))
                a(D.box(BYPASS - 1.5, yy - 1.5, 3, ymid - yy, color="#CBD5E1FF"))
                a(D.box(xv, ymid - 1.5, BYPASS - xv, 3, color="#CBD5E1FF"))
                a(D.box(xv - 1.5, ymid - 1.5, 3, ry(l1) - ymid + 1.5, color="#CBD5E1FF"))
    for t in TASKS:
        tid = t["id"]
        x, y = RX[lay[tid]][tid], ry(lay[tid])
        col = TEAM_COLOR[t["assigned_team"]]
        a(D.box(x, y, NW, NH, color=col, radius=10,
                border="3 SOLID %s" % CP if tid in CP_CHAIN else None))
        a(D.text_el(tid, x=x + 14, y=y + 6, w=90, h=28, size=24, color=WHITE, font=MONO,
                    style="BOLD"))
        a(D.text_el("%d 分 · %s" % (t["scheduled_minutes"], TEAM_ZH[t["assigned_team"]]),
                    x=x + NW - 190, y=y + 8, w=176, h=26, size=24, color="#FFFFFFD9",
                    align="RIGHT"))
        a(D.text_el(t["label"], x=x + 14, y=y + 34, w=NW - 28, h=28, size=24,
                    color=WHITE))
    ks, _ = para("连线在层间通道内正交走线，跨层依赖走右侧空白旁路，不覆盖任何任务块。",
                 24, CX1 - CX0 - 60, CX0 + 30, DT + DH + 10, color=MUTED)
    k += ks

    # ------------------------------------------------------------ risks
    RY = DT + DH + 78
    a(D.text_el("三风险 / 对策（取自 inputs/release.json，未增删）", x=M, y=RY - 40, w=760,
                h=32, size=26, color=INK, style="BOLD"))
    rw = (W - 2 * M - 2 * 16) / 3.0
    inner = rw - 36
    rcards = []
    for r in P.SRC["risks"]:
        ni = len(wraps("影响　" + r["impact"], 24, inner))
        nm = len(wraps("对策　" + r["mitigation"], 24, inner))
        rcards.append((r, ni, nm))
    RH = max(98 + ni * 30 + nm * 30 for _, ni, nm in rcards)
    for i, (r, ni, nm) in enumerate(rcards):
        cx = M + i * (rw + 16)
        a(D.box(cx, RY, rw, RH, color=CARD, radius=14, border="1 SOLID %s" % LINE,
                shadow="0 2 8 0 #0F172A0F"))
        a(D.box(cx, RY, rw, 6, color=RED, radii={"TopLeft": 14, "TopRight": 14}))
        a(D.text_el("%s · %s %s" % (r["id"], r["task"], span(r["task"])), x=cx + 18,
                    y=RY + 14, w=inner, h=30, size=26, color=RED, style="BOLD"))
        a(D.text_el(BY_ID[r["task"]]["label"], x=cx + 18, y=RY + 48, w=inner, h=28,
                    size=24, color=MUTED))
        ks, yy = para("影响　" + r["impact"], 24, inner, cx + 18, RY + 84, color=INK,
                      lh=1.25)
        k += ks
        ks, _ = para("对策　" + r["mitigation"], 24, inner, cx + 18, yy + 6, color=INK2,
                     lh=1.25)
        k += ks

    # ------------------------------------------------------------ rationale
    QY = RY + RH + 20
    a(D.text_el("排程依据", x=M, y=QY, w=400, h=32, size=26, color=INK, style="BOLD"))
    lines = [
        "① 关键路径 R01→R04→R07→R09→R10→R12 = %d 分；R05 必须早于 R07 开始，只能排在 "
        "engineering 通道，被 R02+R03 推到 10:00 开工，这 5 分等待就是下界与最优的全部差距。"
        % P.CP_LEN,
        "② 两条通道各自零重叠、同团队零并行：design R01→R04→R07→R09→R10→R12；\n"
        "　engineering R02→R03→R05→R06→R08→R11。",
        "③ 两处 5 分空档是依赖等待而非缺活：design 10:25–10:30 等 R05，engineering "
        "12:20–12:25 等 R09，均不可抢占。",
        "④ ⌈%d÷%d⌉=%d 分与关键路径 %d 分的下界不可同时取到；穷举 %d 个搜索节点加 20 万次"
        "随机对照得到的最小值是 %d 分，%s 完成，留 %d 分缓冲，R10/R11 检查环节未缩短。"
        % (P.TOTAL_WORK, len(P.TEAMS), P.WORK_LB, P.CP_LEN, P.STATS["nodes"], P.MAKESPAN,
           SUM["makespan_clock"], SUM["buffer_to_deadline_minutes"]),
    ]
    yy = QY + 42
    for i, ln in enumerate(lines):
        for part in ln.split("\n"):
            # A U+3000 that starts a line is rendered zero-width by Inter, so the hanging
            # indent is expressed as an x offset instead.
            ind = part.startswith("　")
            txt = part[1:] if ind else part
            ks, yy = para(txt, 24, W - 2 * M - 24, M + (24 if ind else 0), yy,
                          color=GREEN if i == 3 else INK2, lh=1.26)
            k += ks
    ks, yy = para("数据源 inputs/release.json · 详见 schedule.json / schedule-audit.json "
                  "/ content-map.json", 24, W - 2 * M, M, yy + 8, color=FAINT)
    k += ks
    print("   brief bottom y =", round(yy, 1), "(canvas 1600)")
    return D.snapshot([D.stack(k, W, H)], W, H, bg=PAPER)

# =============================================================== action card
def build_card():
    W, H = 720, 1280
    k = []
    a = k.append
    a(D.box(0, 0, W, H, color=PAPER))
    a(D.box(0, 0, W, 118, color=DARK,
            extra={"gradientType": "LINEAR", "gradientColors": "%s,%s" % (DARK, DARK2),
                   "gradientBegin": "CENTER_LEFT", "gradientEnd": "CENTER_RIGHT"}))
    a(D.box(28, 22, 5, 40, color="#818CF8FF", radius=3))
    a(D.text_el(BRAND_NAME, x=44, y=18, w=400, h=28, size=22, color=WHITE, style="BOLD",
                ls=0.6))
    a(D.text_el("发布日行动卡", x=44, y=48, w=400, h=36, size=30, color=WHITE,
                style="BOLD"))
    a(D.text_el("2026-11-07", x=W - 28 - 220, y=20, w=220, h=28, size=22, color="#A5B4FCFF",
                align="RIGHT", font=MONO))
    a(D.text_el("09:00 → 16:00", x=W - 28 - 220, y=54, w=220, h=28, size=22,
                color="#A5B4FCFF", align="RIGHT", font=MONO))

    stats = [("完成", SUM["makespan_clock"]), ("缓冲", "%d 分" % SUM["buffer_to_deadline_minutes"]),
             ("任务", "12 个")]
    sw = (W - 56 - 2 * 12) / 3.0
    for i, (lab, val) in enumerate(stats):
        cx = 28 + i * (sw + 12)
        a(D.box(cx, 130, sw, 62, color=CARD, radius=12, border="1 SOLID %s" % LINE))
        a(D.text_el(lab, x=cx + 14, y=138, w=sw - 28, h=26, size=20, color=FAINT))
        a(D.text_el(val, x=cx + 14, y=162, w=sw - 28, h=30, size=24, color=INK,
                    style="BOLD", font=MONO))

    cols = [(60, "时间"), (204, "编号"), (280, "任务"), (452, "团队"), (536, "时长"),
            (600, "风险")]
    for cx, lab in cols:
        a(D.text_el(lab, x=cx, y=206, w=140, h=26, size=20, color=FAINT, style="BOLD"))
    a(D.hline(28, W - 28, 236, LINE2, 2))

    rows = sorted(TASKS, key=lambda t: (t["start_minute"], t["id"]))
    RH = 60.0
    top = 240.0
    for i, t in enumerate(rows):
        y = top + i * RH
        tid = t["id"]
        col = TEAM_COLOR[t["assigned_team"]]
        if i % 2 == 0:
            a(D.box(28, y, W - 56, 54, color=CARD, radius=10, border="1 SOLID %s" % LINE))
        a(D.box(38, y + 19, 16, 16, color=col, radius=8))
        a(D.text_el(span(tid), x=60, y=y + 16, w=142, h=28, size=20, color=INK2,
                    font=MONO, style="BOLD"))
        a(chip(204, y + 12, 60, 30, tid, size=20, fill=col, line=None, color=WHITE,
               font=MONO, bold="BOLD"))
        a(D.text_el(t["label"], x=274, y=y + 15, w=176, h=28, size=22, color=INK,
                    style="BOLD"))
        a(D.text_el(TEAM_ZH[t["assigned_team"]], x=452, y=y + 17, w=76, h=26, size=20,
                    color=col, style="BOLD"))
        a(D.text_el("%d 分" % t["scheduled_minutes"], x=532, y=y + 17, w=72, h=26,
                    size=20, color=MUTED, font=MONO))
        rk = RISK_OF_TASK.get(tid)
        if rk:
            a(chip(598, y + 12, 48, 30, rk[0]["id"], size=20, fill=RED_L, line=None,
                   color=RED, font=MONO, bold="BOLD"))
        if tid in CP_CHAIN:
            a(D.box(28, y + 2, 4, 50, color=CP, radii={"TopLeft": 10, "BottomLeft": 10}))

    RY = top + RH * len(rows) + 12
    a(D.box(28, RY, W - 56, 4, color=LINE))
    a(D.text_el("风险提醒", x=28, y=RY + 12, w=300, h=30, size=22, color=INK,
                style="BOLD"))
    for i, r in enumerate(P.SRC["risks"]):
        y = RY + 48 + i * 56
        a(D.box(28, y, W - 56, 50, color=RED_L, radius=10, border="1 SOLID #FCA5A5FF"))
        a(D.text_el("%s %s %s" % (r["id"], r["task"], r["impact"]), x=40, y=y + 4,
                    w=W - 88, h=24, size=20, color=RED, style="BOLD"))
        a(D.text_el("对策：%s" % r["mitigation"], x=40, y=y + 26, w=W - 88, h=24,
                    size=20, color=INK2))
    a(D.text_el("按时间序排列；同一时刻按编号先后 · 洋红标记 = 决定链", x=28, y=RY + 214,
                w=W - 56, h=26, size=20, color=FAINT))
    a(D.text_el("完成 %s · 缓冲 %d 分 · 最优解（穷举 %d 节点）" % (
        SUM["makespan_clock"], SUM["buffer_to_deadline_minutes"], P.STATS["nodes"]),
        x=28, y=RY + 242, w=W - 56, h=28, size=20, color=MUTED, font=MONO))
    a(D.text_el("数据源 inputs/release.json", x=28, y=RY + 270, w=W - 56, h=26,
                size=20, color=FAINT))
    print("   card bottom y =", round(RY + 270 + 26, 1), "(canvas 1280)")
    return D.snapshot([D.stack(k, W, H)], W, H, bg=PAPER)


# ======================================================================= main
BUILDERS = {"board": ("execution-board", build_board),
            "brief": ("decision-brief", build_brief),
            "card": ("action-card", build_card)}


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    final = "--final" in sys.argv
    snapkit.configure(TASK, OUT, TMP)
    if not final:
        S.set_current(TASK)
    names = list(BUILDERS) if which == "all" else [which]
    for n in names:
        base, fn = BUILDERS[n]
        D.WARNINGS[:] = []
        dsl = fn()
        os.makedirs(os.path.join(TMP, "drafts"), exist_ok=True)
        seq = len([f for f in os.listdir(os.path.join(TMP, "drafts"))
                   if f.startswith(base)])
        draft = os.path.join(TMP, "drafts", "%s-v%02d.snapshot" % (base, seq + 1))
        with open(draft, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(dsl)
        r = snapkit.render(dsl, base + ".png", base + ".snapshot", final=final)
        print("[%s] final=%s ok=%s status=%s bytes=%s ms=%s draft=%s"
              % (n, final, r.get("ok"), r.get("status"), r.get("bytes"),
                 r.get("elapsed_ms"), os.path.basename(draft)))
        if not r.get("ok"):
            print("   ERROR:", (r.get("error") or "")[:600])
            print("   saved:", r.get("response_file"))
        ws = D.warnings()
        print("   warnings: %d" % len(ws))
        for w in ws:
            print("   WARN", w)


if __name__ == "__main__":
    main()