"""B01 case-07 - 夜航影城 3 号厅选座图（建筑平面图风格, 1200x1500）.

Scenario: four friends buying tickets on a phone for the 19:40 screening; they want the
best four contiguous seats inside budget and want to know *why* a seat is a bad idea.
Every state on the plan - 受限 / 可选 / 已售 / 推荐 - and every number in the tables comes
from one geometry model of the hall (screen size, row distances, seat pitch) plus one
sold-seat dataset, so the recommendation cannot disagree with the drawn plan.

Run:  python tmp/<run_id>/B01/case07_cinema.py
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import MONO, SANS, Sheet, tw  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B01"
W, H = 1200, 1500
PAPER, PANEL = "#F4EFE6", "#E7DFD1"
INK, INK2, INK3 = "#22252E", "#3E4351", "#5A5F6D"
RED, BLUE, GOLD = "#A83224", "#2F5DA8", "#7A5A10"

ROWS = list("ABCDEFGHIJ")
N = 14
PITCH_M = 0.62                       # seat pitch, metres
BLOCKS = [(0, 4), (4, 10), (10, 14)]  # seat index ranges separated by the two aisles
SCREEN_W, SCREEN_H, SCREEN_BOTTOM, EYE = 12.0, 6.3, 1.8, 1.2
D0, DP = 8.5, 1.45                   # first-row distance and row pitch
LIM_H, LIM_V, LIM_O = 65.0, 35.0, 20.0  # max horizontal / vertical / oblique angle
PRICE = {0: 35, 1: 35, 2: 45, 3: 45, 4: 45, 5: 45, 6: 40, 7: 40, 8: 40, 9: 40}
ZONE = {0: "前区", 1: "前区", 2: "中区", 3: "中区", 4: "中区", 5: "中区",
        6: "后区", 7: "后区", 8: "后区", 9: "后区"}
GROUP_BOOKED = [("E", 4), ("E", 5), ("E", 6), ("E", 7), ("E", 8),   # a 5-seat block taken
                ("B", 6), ("B", 7),                                  # splits the front centre
                ("H", 0), ("H", 1), ("H", 12), ("H", 13)]
X0 = [275, 475, 775]                  # first seat centre of each block, px
Y0, YP = 340, 52                      # first row centre, row pitch px
R = 18                                # seat radius px


def dist(r):
    return D0 + ROWS.index(r) * DP


def off(i):
    return (i - (N - 1) / 2) * PITCH_M


def angles(r, i):
    d = dist(r)
    x = abs(off(i))
    horiz = 2 * math.degrees(math.atan((SCREEN_W / 2) / d))
    vert = math.degrees(math.atan((SCREEN_BOTTOM + SCREEN_H - EYE) / d))
    oblique = math.degrees(math.atan(x / d))
    return horiz, vert, oblique


def blocked(r, i):
    h, v, o = angles(r, i)
    why = []
    if h > LIM_H:
        why.append(f"水平视角 {h:.0f}°＞{LIM_H:.0f}°")
    if v > LIM_V:
        why.append(f"仰角 {v:.0f}°＞{LIM_V:.0f}°")
    if o > LIM_O:
        why.append(f"偏角 {o:.0f}°＞{LIM_O:.0f}°")
    return why


def seat_x(i):
    for (a, b), base in zip(BLOCKS, X0):
        if a <= i < b:
            return base + (i - a) * 50
    raise IndexError(i)


def seats():
    rng = random.Random(20261024)
    booked = set(GROUP_BOOKED)
    out = {}
    for r in ROWS:
        for i in range(N):
            if (r, i) in booked:
                state = "已售"
            elif blocked(r, i):
                state = "受限"
            elif rng.random() < 0.22:
                state = "已售"
            else:
                state = "可选"
            out[(r, i)] = {"state": state, "row_dist": dist(r), "off": off(i),
                           "angles": angles(r, i), "why": blocked(r, i)}
    return out


def windows(S):
    """All 4-seat contiguous free windows that do not straddle an aisle."""
    for r in ROWS:
        for a, b in BLOCKS:
            for i in range(a, b - 3):
                w = [(r, j) for j in range(i, i + 4)]
                if all(S[k]["state"] in ("可选", "受限") for k in w):
                    ok = all(not S[k]["why"] for k in w)
                    yield {"seats": w, "row": r, "from": i + 1, "to": i + 4,
                           "feasible": ok, "price": PRICE[ROWS.index(r)] * 4,
                           "horiz": S[(r, i)]["angles"][0],
                           "vert": S[(r, i)]["angles"][1],
                           "centre": sum(abs(S[(r, j)]["off"]) for j in range(i, i + 4)) / 4,
                           "label": f"{r} 区 {i + 1}-{i + 4} 座"}


def pick(S):
    feas = [w for w in windows(S) if w["feasible"]]
    assert feas, "no feasible block"
    best = min(feas, key=lambda w: (abs(w["horiz"] - 45) + 2.0 * w["centre"]))
    cheap = min(feas, key=lambda w: (w["price"], abs(w["horiz"] - 45)))
    near = min(feas, key=lambda w: w["centre"])
    return best, cheap, near, feas


def build():
    S = seats()
    best, cheap, near, feas = pick(S)
    free = sum(1 for v in S.values() if v["state"] == "可选")
    sold = sum(1 for v in S.values() if v["state"] == "已售")
    rest = sum(1 for v in S.values() if v["state"] == "受限")
    assert free + sold + rest == len(S)
    rec = [k for k in best["seats"]]
    s = Sheet(W, H, min_font=20, bg=PAPER)
    s.rect(0, 0, W, 8, INK)
    s.text("brand", "夜航影城 · 3 号厅 SEAT PLAN", 56, 44, 22, RED, bold=True, font=MONO)
    s.text("title", "19:40 场次选座图与四人推荐", 56, 76, 40, INK, bold=True)
    s.text("sub", "2026-10-24 周六 · 数字 2D · 中文字幕 · 140 座 · 银幕 12.0 m × 6.3 m",
           56, 144, 22, INK3)
    s.text("stat", f"可选 {free} · 已售 {sold} · 受限 {rest} · 推荐 {best['label']}",
           56, 178, 22, INK, bold=True)

    # screen band
    s.path(257, 218, 686, 80, "M 0 57 Q 343 5 686 57 L 686 69 Q 343 17 0 69 Z", INK)
    s.text("sc", "银 幕  SCREEN", 600, 210, 22, INK, bold=True, align="center")
    s.line(257, 306, 257, 288, INK3, 1)
    s.line(943, 306, 943, 288, INK3, 1)
    s.line(257, 304, 943, 304, INK3, 1)
    s.text("scw", f"{SCREEN_W:.1f} m", 600, 280, 20, INK3, align="center", font=MONO)

    # zone brackets
    for lo, hi, name, pr in ((0, 1, "前区", 35), (2, 5, "中区", 45), (6, 9, "后区", 40)):
        y0, y1 = Y0 + lo * YP - R - 6, Y0 + hi * YP + R + 6
        s.line(150, y0, 150, y1, INK3, 1)
        s.line(150, y0, 160, y0, INK3, 1)
        s.line(150, y1, 160, y1, INK3, 1)
        s.text("zn", name, 145, (y0 + y1) / 2 - 11, 20, INK2, align="right")
        s.text("zp", f"¥{pr}", 60, (y0 + y1) / 2 - 11, 20, GOLD if pr == 45 else INK2,
               font=MONO)

    # aisles
    for ax in (450, 750):
        s.line(ax, Y0 - R - 14, ax, Y0 + 9 * YP + R + 14, INK3, 1)
        for yy in range(Y0 - 20, Y0 + 9 * YP + 30, 26):
            s.line(ax - 7, yy, ax + 7, yy + 13, "#D8CFBE", 1)
        s.text("ais", "过道 1.1 m", ax, Y0 + 9 * YP + R + 34, 20, INK3, align="center")

    # seats
    for r in ROWS:
        y = Y0 + ROWS.index(r) * YP
        s.text("rl", r, 232, y - 11, 22, INK, bold=True, align="right", font=MONO)
        s.text("rd", f"{dist(r):.1f} m", 1000, y - 11, 20, INK3, font=MONO)
        s.line(950, y, 992, y, "#D8CFBE", 1)
        for i in range(N):
            v = S[(r, i)]
            x = seat_x(i)
            is_rec = (r, i) in rec
            if v["state"] == "已售":
                s.dot(x, y, R, "#4A4E5C")
            elif v["state"] == "受限":
                s.dot(x, y, R, PANEL, ring=INK3, ring_w=2)
                s.line(x - 11, y - 11, x + 11, y + 11, RED, 2)
                s.line(x - 11, y + 11, x + 11, y - 11, RED, 2)
            elif is_rec:
                s.dot(x, y, R, BLUE)
                s.dot(x, y, R + 5, "#00000000", ring=BLUE, ring_w=3)
            else:
                s.dot(x, y, R, "#FFFDF8", ring=INK3, ring_w=2)
            lab = str(i + 1)
            s.text("sn", lab, x, y - 10, 20,
                   "#FFFDF8" if (v["state"] == "已售" or is_rec) else INK2,
                   align="center", font=MONO)
    s.text("rl2", "排号 / 距银幕", 1000, Y0 - 46, 20, INK3)

    # legend
    ly = Y0 + 9 * YP + R + 76
    items = [("#FFFDF8", INK3, "可选"), ("#4A4E5C", None, "已售"),
             (PANEL, RED, "受限（画叉）"), (BLUE, None, "推荐 4 座")]
    x = 56
    for fill, ring, lab in items:
        s.dot(x + 12, ly + 11, 12, fill, ring=ring, ring_w=3 if ring == BLUE else 2)
        if lab.startswith("受限"):
            s.line(x + 4, ly + 3, x + 20, ly + 19, RED, 2)
            s.line(x + 4, ly + 19, x + 20, ly + 3, RED, 2)
        s.text("lg", lab, x + 32, ly, 22, INK2)
        x += 32 + tw(lab, 22) + 34
    s.text("lg2", f"推荐合计 ¥{best['price']}", 1144, ly, 22, BLUE, bold=True,
           align="right", font=MONO)

    # ---- panel 1: the recommendation, with its geometry
    py = ly + 56
    s.rect(56, py, 520, 340, PANEL, radius=6)
    s.rect(56, py, 520, 44, BLUE, radius=6)
    s.text("h1", f"推荐 · {best['label']}", 80, py + 10, 24, "#FFFDF8", bold=True)
    oblique_max = max(math.degrees(math.atan(abs(S[k]["off"]) / S[k]["row_dist"]))
                      for k in best["seats"])
    rows1 = [("水平视角", f"{best['horiz']:.1f}°", f"上限 {LIM_H:.0f}°"),
             ("仰角（银幕上沿）", f"{best['vert']:.1f}°", f"上限 {LIM_V:.0f}°"),
             ("最大偏角", f"{oblique_max:.1f}°", f"上限 {LIM_O:.0f}°"),
             ("距银幕", f"{dist(best['row']):.1f} m", f"末排 {dist('J'):.1f} m"),
             ("偏离中轴", f"{best['centre']:.2f} m", "越小越正"),
             ("票价合计", f"¥{best['price']}",
              f"{ZONE[ROWS.index(best['row'])]} ¥{PRICE[ROWS.index(best['row'])]}×4")]
    yy = py + 60
    for k, v, note in rows1:
        assert tw(v, 20, True) <= 150 and tw(note, 20) <= 150, (k, v, note)
        s.text("k", k, 80, yy, 20, INK2)
        s.text("v", v, 320, yy, 20, INK, bold=True, font=MONO)
        s.text("n", note, 552, yy, 20, INK3, align="right")
        yy += 28
    end1 = s.para("why1", f"评分＝|水平视角−45°|＋2×|偏离中轴|，在 {len(feas)} 个可行四连座中"
                          "取最小；四座连号、不跨过道。", 80, yy + 6, 20, INK3, width=472)
    assert end1 <= py + 336, end1

    # ---- panel 2: alternatives
    s.rect(608, py, 536, 340, PANEL, radius=6)
    s.rect(608, py, 536, 44, INK, radius=6)
    s.text("h2", "如果不想坐这一区", 632, py + 10, 24, "#FFFDF8", bold=True)
    alts = [("最省", cheap, f"省 ¥{best['price'] - cheap['price']}，视角 {cheap['horiz']:.0f}°"),
            ("最正", near, f"偏离中轴 {near['centre']:.2f} m，视角 {near['horiz']:.0f}°"),
            ("已订走", {"label": "E 区 5-9 座", "price": 45 * 5, "horiz": S[("E", 0)]["angles"][0],
                       "centre": 0.0}, "中轴最好的 5 连座已被整组订走")]
    yy = py + 60
    for tag, w, note in alts:
        s.text("at", tag, 632, yy, 20, RED if tag == "已订走" else BLUE, bold=True)
        s.text("al", w["label"], 700, yy, 20, INK)
        s.text("ap", f"¥{w['price']}", 900, yy, 20, INK2, font=MONO)
        assert tw(note, 20) <= 488, note
        s.text("an", note, 632, yy + 26, 20, INK3)
        yy += 62
    b_bad = sum(1 for i in range(N) if S[("B", i)]["why"])
    a_bad = sum(1 for i in range(N) if S[("A", i)]["why"])
    end2 = s.para("why2", f"A 排 {a_bad} 座全部标叉：水平视角 {S[('A', 0)]['angles'][0]:.0f}°、"
                  f"仰角 {S[('A', 0)]['angles'][1]:.0f}°，超过 {LIM_H:.0f}°/{LIM_V:.0f}° 上限；"
                  f"B 排只有两端 {b_bad} 座偏角超限",
                  632, yy + 2, 20, INK3, width=488)
    assert end2 <= py + 336, end2

    # ---- footer notes
    fy = py + 352
    s.line(56, fy, 1144, fy, "#CFC5B2", 1)
    notes = [f"口径：水平视角＝2·atan({SCREEN_W / 2:.1f}÷距离)；仰角＝atan("
             f"({SCREEN_BOTTOM:.1f}＋{SCREEN_H:.1f}−{EYE:.1f})÷距离)；偏角＝atan(|横向偏移|÷距离)。",
             f"排距 {DP:.2f} m、座距 {PITCH_M:.2f} m、银幕底高 {SCREEN_BOTTOM:.1f} m、"
             f"银幕高 {SCREEN_H:.1f} m、眼高 {EYE:.1f} m、末排距银幕 {dist('J'):.1f} m。",
             "座位状态为演示数据（整组预订＋seed 20261024 随机售出），不代表任何真实影院；"
             "品牌与场次均为自拟。"]
    for n in notes:
        assert tw(n, 20) <= 1088, (n, tw(n, 20))
        s.text("fn", n, 56, fy + 12, 20, INK3)
        fy += 34
    assert fy <= H - 20, fy
    return s, {"free": free, "sold": sold, "restricted": rest,
               "recommended": best, "cheapest": cheap, "nearest_centre": near,
               "feasible_windows": len(feas),
               "geometry": {"screen_w": SCREEN_W, "screen_h": SCREEN_H,
                            "row_distance_first": D0, "row_pitch": DP,
                            "seat_pitch_m": PITCH_M, "limits": [LIM_H, LIM_V, LIM_O]},
               "seats": {f"{r}{i + 1}": {"state": v["state"], "dist_m": round(v["row_dist"], 2),
                                         "offset_m": round(v["off"], 2),
                                         "horiz": round(v["angles"][0], 1),
                                         "vert": round(v["angles"][1], 1),
                                         "oblique": round(v["angles"][2], 1),
                                         "why": v["why"]}
                         for (r, i), v in S.items()}}


if __name__ == "__main__":
    s, data = build()
    (TMP / "case07.snapshot").write_text(s.dsl(), encoding="utf-8")
    (TMP / "case07-data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(json.dumps(s.audit(margin=40), ensure_ascii=False))
    print(json.dumps({k: data[k] for k in ("free", "sold", "restricted",
                                           "feasible_windows")}, ensure_ascii=False))
    print(json.dumps([data["recommended"]["label"], data["cheapest"]["label"],
                      data["nearest_centre"]["label"]], ensure_ascii=False))
