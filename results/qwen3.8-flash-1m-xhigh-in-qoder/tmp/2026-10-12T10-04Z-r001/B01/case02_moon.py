"""B01 case-02 - 叠光天文台 2026 月相历 (1200x1600, night sky).

Scenario: an observatory open-night planner picking dates by moonlight. Every phase is
computed from the mean synodic month (no hand-typed dates): age = (JD - 2451550.1) mod
29.530588853, lit fraction k = (1 - cos 2*pi*phase) / 2, and each disc is drawn as a
two-arc lune with ClipPath arcs. The approximation and its error are printed on the card.

Run:  python tmp/<run_id>/B01/case02_moon.py
"""
from __future__ import annotations

import calendar
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import MONO, SANS, Sheet, f, tw  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B01"
W, H = 1200, 1600
BG = "#0B1026"
INK, INK2, INK3 = "#EEF3FF", "#A9B7DC", "#6E7FA8"
MOON, MOON_DIM = "#F5E6C0", "#2A3358"
YEAR = 2026
SYNODIC = 29.530588853
EPOCH_JD = 2451550.1        # 2000-01-06 18:14 UTC, a mean new moon


def julian_day(y, m, d):
    a = (14 - m) // 12
    yy = y + 4800 - a
    mm = m + 12 * a - 3
    jdn = d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045
    return jdn + 0.5 - 0.0075        # local noon, roughly


def syn_age(y, m, d):
    return (julian_day(y, m, d) - EPOCH_JD) % SYNODIC


def phase(y, m, d):
    return syn_age(y, m, d) / SYNODIC


def events_in_month(y, m):
    """New moon = the day the synodic age wraps to 0; full moon = the day it crosses
    half a synodic month. Detecting the crossing gives one date per event instead of
    flagging the two days on either side of a tolerance window."""
    import datetime
    days = calendar.monthrange(y, m)[1]
    new, full = [], []
    for d in range(1, days + 1):
        prev = datetime.date(y, m, d) - datetime.timedelta(days=1)
        a0 = syn_age(prev.year, prev.month, prev.day)
        a1 = syn_age(y, m, d)
        if a1 < a0:
            new.append(d)
        half = SYNODIC / 2
        if a0 < half <= a1:
            full.append(d)
    return new, full


def moon_path(cx, cy, r, p):
    """Lit-region path for phase p in [0,1): 0 new, .25 first quarter, .5 full."""
    t = math.cos(2 * math.pi * p)                 # 1 new -> -1 full
    right = p < 0.5                               # which limb is lit
    x0, ytop, ybot = cx, cy - r, cy + r
    sweep_out = 1 if right else 0
    # terminator ellipse: semi-minor axis shrinks with |t|, its bulge flips at quarter
    rx = abs(t) * r
    sweep_term = 1 if (t > 0) == right else 0
    if abs(rx) < 0.6:
        return (f"M {f(x0)} {f(ytop)} A {f(r)} {f(r)} 0 0 {sweep_out} {f(x0)} {f(ybot)} "
                f"L {f(x0)} {f(ytop)} Z")
    return (f"M {f(x0)} {f(ytop)} A {f(r)} {f(r)} 0 0 {sweep_out} {f(x0)} {f(ybot)} "
            f"A {f(rx)} {f(r)} 0 0 {sweep_term} {f(x0)} {f(ytop)} Z")


PHASE_NAMES = ["新月", "娥眉月", "上弦月", "盈凸月", "满月", "亏凸月", "下弦月", "残月"]


def phase_name(p):
    return PHASE_NAMES[int(((p + 0.0625) % 1.0) * 8) % 8]


def build():
    s = Sheet(W, H, min_font=20, bg=BG)
    s.text("brand", "叠光天文台 · SHUANGUANG OBSERVATORY", 56, 40, 22, "#8FB2FF",
           bold=True, font=MONO)
    s.text("title", "2026 月相历", 56, 72, 46, INK, bold=True)
    s.text("sub", "按平朔望月 29.530588853 天计算 · 每日 12:00 取样 · 观测排期用",
           56, 142, 22, INK3)

    # 12 month cards, 3 columns x 4 rows
    cw, ch, gx, gy = 356, 280, 20, 12
    x0, y0 = 56, 186
    marks = {}
    for m in range(1, 13):
        col, row = (m - 1) % 3, (m - 1) // 3
        cx = x0 + col * (cw + gx)
        cy = y0 + row * (ch + gy)
        s.rect(cx, cy, cw, ch, "#121A38", radius=14)
        p1 = phase(YEAR, m, 1)
        s.rect(cx + 16, cy + 16, 44, 44, MOON_DIM, shape="CIRCLE")
        s.path(cx + 16, cy + 16, 44, 44, moon_path(22, 22, 21, p1), MOON)
        s.text("mo", f"{m} 月", cx + 70, cy + 20, 26, INK, bold=True)
        s.text("ph", f"1 日 {phase_name(p1)} · 亮面 {int(round((1 - math.cos(2 * math.pi * p1)) / 2 * 100))}%",
               cx + 70, cy + 50, 20, INK3)
        # day grid: 7 columns, weeks as rows
        new_days, full_days = events_in_month(YEAR, m)
        cal = calendar.Calendar(firstweekday=0).monthdayscalendar(YEAR, m)
        for i, wd in enumerate("一二三四五六日"):
            s.text("wd", wd, cx + 40 + i * 44, cy + 80, 20, INK3, align="center")
        for r_, week in enumerate(cal):
            for c_, day in enumerate(week):
                if not day:
                    continue
                x = cx + 26 + c_ * 44
                y = cy + 112 + r_ * 26
                p = phase(YEAR, m, day)
                k = (1 - math.cos(2 * math.pi * p)) / 2
                new = day in new_days
                full = day in full_days
                if new or full:
                    # the marker sits behind the number so the date is still readable
                    s.rect(x, y - 2, 22, 22, "#16224A" if new else MOON, shape="CIRCLE")
                    if new:
                        s.rect(x - 1, y - 3, 24, 24, "#00000000",
                               border="2 SOLID #8FB2FF", shape="CIRCLE")
                    marks.setdefault("new" if new else "full", []).append((m, day))
                    s.text("d", str(day), x + 11, y - 4, 20,
                           "#CFE0FF" if new else "#1B1400", align="center", bold=True)
                elif abs(p - 0.25) < 0.03 or abs(p - 0.75) < 0.03:
                    s.rect(x, y - 2, 22, 22, "#232E55", shape="CIRCLE")
                    s.text("d", str(day), x + 11, y - 4, 20, INK, align="center")
                else:
                    s.text("d", str(day), x + 11, y - 4, 20,
                           INK2 if 0.15 < k < 0.85 else INK3, align="center")
    # legend / method panel
    py = y0 + 4 * (ch + gy) + 8
    s.rect(56, py, 1088, 196, "#121A38", radius=14)
    s.text("lg_h", "八相", 80, py + 18, 24, INK, bold=True)
    for i in range(8):
        p = i / 8.0
        x = 96 + i * 62
        s.rect(x, py + 52, 40, 40, MOON_DIM, shape="CIRCLE")
        if i != 0:
            s.path(x, py + 52, 40, 40, moon_path(20, 20, 19, p), MOON)
        s.text("lgn", PHASE_NAMES[i], x + 20, py + 100, 20, INK3, align="center")
    fy = py + 26
    fy = s.para("formula", "age=(JD−2451550.1) mod 29.5306 · k=(1−cos 2π·phase)/2",
               600, fy, 20, INK2, 520, font=MONO) + 6
    fy = s.para("err", "平朔与真实朔望最多相差约 ±0.5 天；蓝环＝新月、亮底＝满月、"
                       "灰点＝上下弦。示例机构，非真实天文台发布。", 600, fy, 20, INK3,
                520) + 6
    fulls, news = marks.get("full", []), marks.get("new", [])
    pick = f"全年 {len(news)} 次新月 / {len(fulls)} 次满月 · 首满月 {fulls[0][0]}.{fulls[0][1]}"
    assert tw(pick, 20) <= 520, (round(tw(pick, 20)), pick)
    s.para("pick", pick, 600, fy, 20, "#8FB2FF", 520)
    return s


if __name__ == "__main__":
    s = build()
    (TMP / "case02.snapshot").write_text(s.dsl(), encoding="utf-8")
    print(__import__("json").dumps(s.audit(), ensure_ascii=False))
