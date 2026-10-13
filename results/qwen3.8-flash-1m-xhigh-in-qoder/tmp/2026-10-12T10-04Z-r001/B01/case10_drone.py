"""B01 case-10 - 巡线无人机 光伏电场巡检航线与风场图 (1600x900, 平板强光阅读).

Scenario: a pilot and an operations lead do the last check before take-off on a tablet in
daylight: does the serpentine route cover every array, and does the battery survive the
headwind legs plus the return? The wind field, the route, the per-segment energy, the
remaining charge and the go / no-go colour are all produced by one calculation.

Run:  python tmp/<run_id>/B01/case10_drone.py
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import MONO, SANS, Sheet, tw  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B01"
W, H = 1600, 900
BG = "#EEF2F4"
INK, INK2, INK3 = "#1D2530", "#4A5462", "#6B7683"
RED, GREEN, AMBER, BLUE = "#B23A2E", "#2E7D5B", "#C97A16", "#2F5DA8"
ARRAY, ARRAY_EDGE, GROUND = "#3A6EA5", "#25507E", "#E3E9EC"

PX0, PY0, PW, PH = 150, 196, 940, 500
SCAN_DY = -28                        # the drone flies above the array centreline
M_PER_PX = 2.2                       # plan scale
ROWS = 4                             # array rows
PER_ROW = 8                          # panels per row
CAPACITY = 296.0                     # Wh, 6S 8000 mAh
CHARGE = 0.93                        # state of charge at the pad
BASE_WH_M = 0.0215                   # Wh per metre in still air
HEAD_K = 0.055                       # extra share of power per m/s of headwind
WP_HOVER = 1.9                       # Wh spent slowing at each waypoint
RESERVE = 0.10                       # required landing reserve, share of capacity
NOFLY = (670, 300, 40)               # 箱变 / 禁飞区：圆心（px）与半径（px）
CRUISE = 9.0                         # m/s


def wind(gx, gy):
    """Return (speed m/s, direction degrees the air flows TOWARDS, screen frame)."""
    sp = 5.4 + 2.3 * math.sin(gx / 210) + 1.6 * math.cos(gy / 170)
    dr = 214 + 26 * math.sin(gx / 260) + 14 * math.cos(gy / 190)
    return sp, dr


def headwind(a, b):
    """Component of the wind against the a->b heading, sampled at the midpoint."""
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    sp, dr = wind(mx, my)
    seg = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    return sp * math.cos(math.radians(dr - seg)), sp, dr


def row_y(r):
    return PY0 + 74 + r * ((PH - 150) / (ROWS - 1))


def route():
    pad = (PX0 + 40, PY0 + PH - 46)
    wps = [pad]
    for r in range(ROWS):
        y = row_y(r) + SCAN_DY
        x0, x1 = PX0 + 96, PX0 + PW - 96
        west, east = (x0, y), (x1, y)
        wps += ([west, (x0 + (x1 - x0) * 0.5, y), east] if r % 2 == 0
                else [east, (x0 + (x1 - x0) * 0.5, y), west])
    wps.append(pad)
    return wps


def plan():
    wps = route()
    segs, used = [], 0.0
    for a, b in zip(wps, wps[1:]):
        dist_px = math.hypot(b[0] - a[0], b[1] - a[1])
        dist_m = dist_px * M_PER_PX
        hw, sp, dr = headwind(a, b)
        e = dist_m * BASE_WH_M * (1 + HEAD_K * max(hw, 0.0))
        used += e
        segs.append({"a": a, "b": b, "m": dist_m, "head": hw, "wind": sp, "dir": dr,
                     "wh": e})
    used += WP_HOVER * (len(wps) - 2)
    avail = CAPACITY * CHARGE
    # return leg is already the last segment; landing reserve is a share of capacity
    landing = used + segs[-1]["m"] * BASE_WH_M * (1 + HEAD_K * max(segs[-1]["head"], 0))
    remain = avail - used
    margin = remain / CAPACITY
    verdict = ("可以起飞", GREEN) if margin >= RESERVE + 0.05 else (
        ("裕度偏低", AMBER) if margin >= RESERVE else ("电量不足", RED))
    return wps, segs, used, avail, remain, margin, verdict


def coverage():
    """Every array panel must sit under a scan line within 40 px."""
    wps = route()
    lines = []
    for r in range(ROWS):
        lines.append((PX0 + 96, row_y(r) + SCAN_DY, PX0 + PW - 96))
    hit = 0
    for r in range(ROWS):
        for c in range(PER_ROW):
            cx, cy = panel_xy(r, c)
            if any(abs(cy - y) <= 40 and x0 - 20 <= cx <= x1 + 20 for x0, y, x1 in lines):
                hit += 1
    return hit, ROWS * PER_ROW


def panel_xy(r, c):
    x = PX0 + 96 + c * ((PW - 192) / (PER_ROW - 1))
    y = PY0 + 74 + r * ((PH - 150) / (ROWS - 1))
    return x, y


def build():
    wps, segs, used, avail, remain, margin, verdict = plan()
    hit, total = coverage()
    assert hit == total, (hit, total)
    dist_km = sum(s["m"] for s in segs) / 1000
    fly_min = sum(s["m"] for s in segs) / CRUISE / 60
    worst = max(segs[:-1], key=lambda s: s["head"])
    def seg_dist(a, b, q):
        ax, ay = a
        dx, dy = b[0] - ax, b[1] - ay
        L2 = dx * dx + dy * dy
        k = 0.0 if L2 == 0 else max(0.0, min(1.0, ((q[0] - ax) * dx + (q[1] - ay) * dy) / L2))
        return math.hypot(ax + k * dx - q[0], ay + k * dy - q[1])

    nfly_m = (min(seg_dist(s["a"], s["b"], NOFLY[:2]) for s in segs) - NOFLY[2]) * M_PER_PX
    assert nfly_m > 20, nfly_m
    s = Sheet(W, H, min_font=20, bg=BG)
    s.text("brand", "巡线电力 · 光伏电场无人机巡检 PLAN 10", 56, 44, 22, BLUE, bold=True,
           font=MONO)
    s.text("title", "蛇形航线、风场与电量核算", 56, 74, 38, INK, bold=True)
    s.text("sub", f"北塔山二期 · {ROWS} 排 × {PER_ROW} 组 ＝ {total} 组阵列 · "
                  f"1 px ＝ {M_PER_PX} m · 巡航 {CRUISE:.0f} m/s · 起飞电量 "
                  f"{CHARGE * 100:.0f}%", 56, 134, 22, INK3)
    stat = (f"里程 {dist_km:.2f} km · 航时 {fly_min:.0f} min · 耗电 {used:.0f} Wh · "
            f"剩余 {remain:.0f} Wh（{margin * 100:.0f}%）· {verdict[0]}")
    assert tw(stat, 22) <= 1034, tw(stat, 22)
    s.text("stat", stat, 56, 162, 22, verdict[1], bold=True)

    # ---- plan area
    s.rect(PX0, PY0, PW, PH, GROUND, radius=8, border=f"1.5 SOLID {INK3}")
    cx0, cy0, _ = NOFLY
    s.dot(cx0, cy0, NOFLY[2], "#D8C9C5", ring=RED, ring_w=2)
    s.text("nf", "箱变禁飞区", cx0, cy0 - 12, 20, RED, align="center", bold=True)
    s.text("nf2", f"r {NOFLY[2] * M_PER_PX:.0f} m", cx0, cy0 + 12, 20, RED, align="center",
           font=MONO)
    for r in range(ROWS):
        for c in range(PER_ROW):
            x, y = panel_xy(r, c)
            w, h = (PW - 192) / (PER_ROW - 1) * 0.74, 34
            s.rect(x - w / 2, y - h / 2, w, h, ARRAY, radius=3)
            s.line(x - w / 2, y - h / 2 + 6, x + w / 2, y - h / 2 + 6, ARRAY_EDGE, 1.2)
            s.line(x - w / 2, y + h / 2 - 6, x + w / 2, y + h / 2 - 6, ARRAY_EDGE, 1.2)
        s.text("rn", f"第 {r + 1} 排", PX0 - 12, row_y(r) - 10, 20, INK3, align="right")

    # wind field
    for i in range(9):
        for j in range(6):
            gx, gy = PX0 + 60 + i * ((PW - 120) / 8), PY0 + 46 + j * ((PH - 92) / 5)
            sp, dr = wind(gx, gy)
            ln = max(12.0, 6 + (sp - 1.5) * 6.0)
            t = math.radians(dr)
            dx, dy = math.cos(t) * ln, math.sin(t) * ln
            col = "#7FA8C9" if sp < 5.5 else ("#C9A227" if sp < 7 else "#B23A2E")
            s.arrow(gx - dx / 2, gy - dy / 2, gx + dx / 2, gy + dy / 2, col, 1.8, 5)
    s.text("wl", "风场箭头＝风的去向，长度与颜色＝风速", PX0 + PW - 8, PY0 + PH - 28, 20,
           INK3, align="right")

    s.text("rl2", f"航线颜色＝该段逆风分量：蓝 ＜3 · 橙 3–6 · 红 ＞6 m/s",
           PX0 + PW - 8, PY0 + 6, 20, INK3, align="right")
    # route
    for k, seg in enumerate(segs):
        a, b = seg["a"], seg["b"]
        col = RED if seg["head"] > 6 else (AMBER if seg["head"] > 3 else BLUE)
        s.line(a[0], a[1], b[0], b[1], col, 3.4)
    for k, p in enumerate(wps[:-1]):
        s.dot(p[0], p[1], 9, "#FFFFFF", ring=INK, ring_w=2)
        s.text("wp", "P" if k == 0 else str(k), p[0], p[1] - 10, 20, INK,
               align="center", font=MONO, bold=True)
    s.dot(wps[-1][0], wps[-1][1], 9, "#FFFFFF", ring=INK, ring_w=2)
    pad = wps[0]
    s.text("pad", "起飞点 / 返航点", pad[0] + 6, pad[1] + 26, 20, INK2)
    mx = (worst["a"][0] + worst["b"][0]) / 2
    my = (worst["a"][1] + worst["b"][1]) / 2
    s.line(mx, my - 14, mx, my - 30, RED, 1.5)
    s.text("hd", f"最逆风 {worst['head']:+.1f} m/s", mx, my - 52, 20, RED, align="center",
           font=MONO, bold=True)

    # ---- right column: segment ledger
    rx = 1130
    s.text("th", "逐段核算", rx, PY0 - 26, 24, INK, bold=True)
    cols = [rx, rx + 50, rx + 118, rx + 176, rx + 234, rx + 296]
    for c, lab in zip(cols, ["段", "长 m", "逆风", "Wh", "累计", "剩 %"]):
        s.text("ch", lab, c, PY0 + 2, 20, INK3, bold=True)
    s.line(rx, PY0 + 26, 1544, PY0 + 26, "#C9D3D9", 1)
    yy, acc = PY0 + 34, 0.0
    for k, seg in enumerate(segs):
        acc += seg["wh"] + (WP_HOVER if k < len(segs) - 1 else 0)
        pct = (avail - acc) / CAPACITY * 100
        vals = [f"{k + 1}", f"{seg['m']:.0f}", f"{seg['head']:+.1f}", f"{seg['wh']:.1f}",
                f"{acc:.0f}", f"{pct:.0f}"]
        for c, v in zip(cols, vals):
            s.text("sv", v, c, yy, 20,
                   RED if (c == cols[5] and pct < RESERVE * 100) else
                   (AMBER if (c == cols[2] and seg["head"] > 6) else INK2),
                   font=MONO, bold=(c == cols[5]))
        yy += 27
    s.line(rx, yy + 2, 1544, yy + 2, "#C9D3D9", 1)
    yy += 12
    for k, v in ((f"合计 {len(segs)} 段", f"{used:.0f} Wh"),
                 (f"最逆风段 第 {segs.index(worst) + 1} 段", f"{worst['head']:+.1f} m/s"),
                 ("禁飞区最近距离", f"{nfly_m:.0f} m")):
        assert tw(k, 20) + tw(v, 20, True) < 414, k
        s.text("tt", k, rx, yy, 20, INK2)
        s.text("tv", v, 1544, yy, 20, INK, bold=True, align="right", font=MONO)
        yy += 28

    # ---- battery bar
    s.text("bh", "电量核算", rx, yy + 6, 24, INK, bold=True)
    by = yy + 40
    s.rect(rx, by, 414, 34, "#DCE4E8", radius=6)
    s.rect(rx, by, 414 * CHARGE, 34, "#8FBF9F", radius=6)
    s.rect(rx + 414 * CHARGE, by, 414 * (1 - CHARGE), 34, "#C7D0D5", radius=6)
    s.rect(rx, by, 414 * (used / CAPACITY), 34, BLUE, radius=6)
    s.rect(rx + 414 * (used / CAPACITY), by, 414 * (remain / CAPACITY), 34,
           verdict[1], radius=6)
    red_x = rx + 414 * ((avail - RESERVE * CAPACITY) / CAPACITY)
    s.line(red_x, by - 6, red_x, by + 40, RED, 2.5)
    s.text("bl", f"已用 {used / CAPACITY * 100:.0f}% · 剩余 {margin * 100:.0f}%",
           rx, by + 42, 20, INK2, font=MONO)
    s.text("rl", f"红线＝剩余 {RESERVE * 100:.0f}% 线", 1544, by + 42, 20, RED,
           align="right")
    s.text("vd", f"判定：{verdict[0]}（要求剩余 ≥{RESERVE * 100:.0f}%）", rx, by + 76, 24,
           verdict[1], bold=True)
    assert by + 102 <= 858, by

    # ---- footer
    s.line(56, 774, 1100, 774, "#C9D3D9", 1)
    notes = [f"耗电模型：Wh＝长度 m × {BASE_WH_M} × (1＋{HEAD_K}×逆风分量)＋每个航点 "
             f"{WP_HOVER} Wh 减速。",
             "逆风分量取航段中点风速在航向上的投影；风场与电量为演示数据，非实测。",
             f"覆盖核算：{total} 组阵列全部落在扫描线 ±40 px 内（{hit}/{total}）；"
             "禁飞区按航段到圆心的最短距离核算。"]
    fy = 782
    for n in notes:
        assert tw(n, 20) <= 1044, (n, tw(n, 20))
        s.text("fn", n, 56, fy, 20, INK3)
        fy += 26
    assert fy - 26 + 21.2 <= 858, fy
    return s, {"segments": [{k: (round(v, 2) if isinstance(v, float) else v)
                             for k, v in seg.items()} for seg in segs],
               "energy_wh": round(used, 1), "available_wh": round(avail, 1),
               "remaining_wh": round(remain, 1), "margin": round(margin, 3),
               "verdict": verdict[0], "distance_km": round(dist_km, 3),
               "flight_min": round(fly_min, 1), "coverage": [hit, total],
               "nofly_clearance_m": round(nfly_m, 1),
               "worst_headwind": round(worst["head"], 2),
               "params": {"capacity_wh": CAPACITY, "charge": CHARGE,
                          "base_wh_per_m": BASE_WH_M, "headwind_k": HEAD_K,
                          "wp_hover_wh": WP_HOVER, "reserve": RESERVE,
                          "m_per_px": M_PER_PX, "cruise_m_s": CRUISE}}


if __name__ == "__main__":
    s, data = build()
    (TMP / "case10.snapshot").write_text(s.dsl(), encoding="utf-8")
    (TMP / "case10-data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(json.dumps(s.audit(margin=40), ensure_ascii=False))
    print(json.dumps({k: data[k] for k in ("energy_wh", "remaining_wh", "margin",
                                           "verdict", "distance_km", "coverage",
                                           "nofly_clearance_m")}, ensure_ascii=False))
