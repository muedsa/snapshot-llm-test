"""B01 case-08 - 叠光夏季夜间地表温度分布图（城市热岛, 1600x1000）.

Scenario: a planning / public-health working meeting choosing where to put shade and cool
roofs. The whole plate - raster bands, isolines, hotspot callouts, the A-B transect
profile, the statistics - is evaluated from one analytic temperature field on a 64x36
grid, so no number on the page can disagree with the picture. The field is synthetic
(Gaussian heat sources minus water/park cooling); this is stated on the plate.

Run:  python tmp/<run_id>/B01/case08_heat.py
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
W, H = 1600, 1000
PAPER, FRAME = "#EFE9DC", "#DCCFB8"
INK, INK2, INK3 = "#23252C", "#40434E", "#5A5E69"
RED, BLUE = "#A83224", "#2F5DA8"

# plan area
MX, MY, MW, MH = 132, 196, 1010, 470
NX, NY = 64, 36                      # grid cells
KM_W, KM_H = 12.8, 6.3               # kilometres covered
BASE = 28.6
HOT_MIN = 35.0
HOT = [(22, 14, 7.7, 7.4, "老城区"), (40, 10, 6.0, 5.2, "枢纽站场"),
       (52, 20, 6.7, 6.8, "工业东区"), (30, 25, 4.7, 4.4, "商圈天台"),
       (14, 28, 3.8, 4.2, "物流堆场")]
LAKE = (46.5, 30.5, 5.2, 3.4)        # cx, cy, rx, ry  (grid units)
PARKS = [(9.5, 8.5, 4.6, 3.2, "西岭公园"), (35.5, 33, 5.4, 2.6, "南湖绿地")]
BANDS = [(28.0, "#2B4F7E"), (30.0, "#2E7E96"), (32.0, "#4FA07E"), (34.0, "#C6B24A"),
         (36.0, "#DE8C39"), (37.5, "#C4502C"), (99.0, "#93251F")]
LEVELS = [30.0, 33.0, 36.0]
TRANSECT = ((4, 5), (60, 31))


def field(gx, gy):
    t = BASE + 0.022 * gx                       # mild inland warming eastwards
    for cx, cy, amp, sig, _ in HOT:
        d2 = ((gx - cx) / sig) ** 2 + ((gy - cy) / (sig * 0.78)) ** 2
        t += amp * math.exp(-d2)
    river = 8.0 + 0.34 * gx + 4.2 * math.sin(gx / 9.5)
    dr = abs(gy - river)
    if dr < 2.4:
        t -= 3.0 * math.cos(min(dr / 2.4, 1.0) * math.pi / 2) ** 2
    lx, ly, lrx, lry = LAKE
    dl = ((gx - lx) / lrx) ** 2 + ((gy - ly) / lry) ** 2
    if dl < 1.0:
        t -= 3.3 * (1 - dl)
    for px, py, prx, pry, _ in PARKS:
        dp = ((gx - px) / prx) ** 2 + ((gy - py) / pry) ** 2
        if dp < 1.0:
            t -= 1.8 * (1 - dp)
    return t


GRID = [[field(i, j) for i in range(NX + 1)] for j in range(NY + 1)]
PX, PY = 1.0, 1.0


def px(gx):
    return MX + gx / NX * MW


def py(gy):
    return MY + gy / NY * MH


def band_of(v):
    for i, (hi, col) in enumerate(BANDS):
        if v < hi:
            return i, col
    return len(BANDS) - 1, BANDS[-1][1]


def cell_value(i, j):
    return (GRID[j][i] + GRID[j][i + 1] + GRID[j + 1][i] + GRID[j + 1][i + 1]) / 4


def raster():
    """Row-wise run-length merge of equal bands: far fewer nodes than one rect per cell."""
    runs = []
    for j in range(NY):
        i = 0
        while i < NX:
            b = band_of(cell_value(i, j))[0]
            k = i
            while k < NX and band_of(cell_value(k, j))[0] == b:
                k += 1
            runs.append((i, j, k - i, BANDS[b][1]))
            i = k
    return runs


def marching(level):
    """Classic marching squares on the node grid; returns merged polylines in grid units."""
    segs = []
    for j in range(NY):
        for i in range(NX):
            v = [GRID[j][i], GRID[j][i + 1], GRID[j + 1][i + 1], GRID[j + 1][i]]
            c = [x >= level for x in v]
            if all(c) or not any(c):
                continue
            pts = []

            def t(a, b):                      # crossing fraction along the edge
                return 0.5 if a == b else (level - a) / (b - a)

            if c[0] != c[1]:                  # top:    node(i,j)   -> node(i+1,j)
                pts.append((i + t(v[0], v[1]), float(j)))
            if c[1] != c[2]:                  # right:  node(i+1,j) -> node(i+1,j+1)
                pts.append((float(i + 1), j + t(v[1], v[2])))
            if c[2] != c[3]:                  # bottom: node(i,j+1) -> node(i+1,j+1)
                pts.append((i + t(v[3], v[2]), float(j + 1)))
            if c[3] != c[0]:                  # left:   node(i,j)   -> node(i,j+1)
                pts.append((float(i), j + t(v[0], v[3])))
            if len(pts) == 2:
                segs.append((pts[0], pts[1]))
            elif len(pts) == 4:
                segs.append((pts[0], pts[1]))
                segs.append((pts[2], pts[3]))
    chains, used = [], [False] * len(segs)
    key = lambda p: (round(p[0], 3), round(p[1], 3))
    ends = {}
    for n, (a, b) in enumerate(segs):
        ends.setdefault(key(a), []).append(n)
        ends.setdefault(key(b), []).append(n)
    for n in range(len(segs)):
        if used[n]:
            continue
        used[n] = True
        chain = [list(segs[n][0]), list(segs[n][1])]
        for grow_head in (True, False):
            while True:
                tip = key(chain[0] if grow_head else chain[-1])
                nxt = next((m for m in ends.get(tip, []) if not used[m]), None)
                if nxt is None:
                    break
                used[nxt] = True
                a, b = segs[nxt]
                add = b if key(a) == tip else a
                chain = [list(add)] + chain if grow_head else chain + [list(add)]
        chains.append(chain)
    return chains


def transect_profile(n=56):
    (x0, y0), (x1, y1) = TRANSECT
    out = []
    for k in range(n + 1):
        f = k / n
        gx, gy = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        out.append((f, math.hypot((x1 - x0) * KM_W / NX, (y1 - y0) * KM_H / NY) * f,
                    field(gx, gy)))
    return out


def build():
    vals = [cell_value(i, j) for j in range(NY) for i in range(NX)]
    vmax, vmin = max(vals), min(vals)
    mean = sum(vals) / len(vals)
    hot_area = sum(1 for v in vals if v >= HOT_MIN) / len(vals) * KM_W * KM_H
    prof = transect_profile()
    pmax, pmin = max(p[2] for p in prof), min(p[2] for p in prof)
    s = Sheet(W, H, min_font=20, bg=PAPER)
    s.text("brand", "叠光城市气候观测组 · URBAN CLIMATE PLATE 08", 56, 40, 22, BLUE,
           bold=True, font=MONO)
    s.text("title", "夏季夜间地表温度与热岛强度分布", 56, 72, 40, INK, bold=True)
    s.text("sub", f"8 月 12 日 02:10 · 12.8 km × 6.3 km · 网格 {NX}×{NY} · "
                  f"基准（郊野）{vmin:.1f} ℃ · 合成演示场，非实测", 56, 140, 22, INK3)

    # frame + km ticks
    s.rect(MX, MY, MW, MH, "#F6F2E8", border="2 SOLID " + INK)
    s.text("unit", "km", MX + MW + 10, MY + MH + 12, 20, INK3, font=MONO)
    for k in range(0, 13, 2):
        x = MX + k / KM_W * MW
        s.line(x, MY + MH, x, MY + MH + 8, INK3, 1)
        s.text("tx", f"{k}", x, MY + MH + 12, 20, INK3, align="center", font=MONO)
    for k in range(0, 7, 1):
        y = MY + k / KM_H * MH
        s.line(MX - 8, y, MX, y, INK3, 1)
        s.text("ty", f"{k} km", MX - 14, y - 10, 20, INK3, align="right", font=MONO)

    # raster bands
    for i, j, n, col in raster():
        s.rect(px(i), py(j), n / NX * MW + 0.6, MH / NY + 0.6, col)
    # water and parks on top of the raster
    river_pts = [(gx, 8.0 + 0.34 * gx + 4.2 * math.sin(gx / 9.5))
                 for gx in [i * 2 for i in range(0, NX // 2 + 1)]]
    for (ax, ay), (bx, by) in zip(river_pts, river_pts[1:]):
        s.line(px(ax), py(ay), px(bx), py(by), "#3E7FB8", 7)
    lx, ly, lrx, lry = LAKE
    s.rect(px(lx - lrx), py(ly - lry), (2 * lrx) / NX * MW, (2 * lry) / NY * MH,
           "#3E7FB8", shape="CIRCLE")
    s.text("lake", "镜湖", px(lx), py(ly) - 10, 20, "#F6F2E8", bold=True, align="center")
    for gx, gy, rx, ry, name in PARKS:
        s.rect(px(gx - rx), py(gy - ry), (2 * rx) / NX * MW, (2 * ry) / NY * MH,
               "#5E8C5A", radius=6)
        s.text("park", name, px(gx), py(gy) - 10, 20, "#F6F2E8", bold=True, align="center")

    mapocc = [(px(cx) - 10, py(cy) - 10, px(cx) + 10, py(cy) + 10)
              for cx, cy, *_ in HOT]          # keep chips off the hotspot dots
    # isolines
    chains_by_level = {lv: marching(lv) for lv in LEVELS}
    for n, lv in enumerate(LEVELS):
        for chain in chains_by_level[lv]:
            for (ax, ay), (bx, by) in zip(chain, chain[1:]):
                s.line(px(ax), py(ay), px(bx), py(by), "#2A2C33", 1.6)
        if chains_by_level[lv]:
            # label each isoline where there is map room: nearest vertex to a spread anchor
            anchor = MX + MW * (0.18 + 0.29 * n)
            allpts = [q for ch in chains_by_level[lv] for q in ch]
            gx, gy = min(allpts, key=lambda q: (px(q[0]) - anchor) ** 2
                         + (py(q[1]) - (MY + MH * 0.45)) ** 2)
            chip(s, min(max(px(gx), MX + 52), MX + MW - 52),
                 min(max(py(gy), MY + 26), MY + MH - 26), f"{lv:.0f}℃", INK,
                 occ=mapocc)

    # hotspot callouts
    for cx, cy, amp, sig, name in HOT:
        v = field(cx, cy)
        s.dot(px(cx), py(cy), 6, "#FFFFFF", ring="#2A2C33", ring_w=2)
        chip(s, min(max(px(cx) + 66, MX + 96), MX + MW - 96),
             min(max(py(cy) - 28, MY + 26), MY + MH - 26),
             f"{name} {v:.1f}℃", INK, occ=mapocc)

    # transect line
    (x0, y0), (x1, y1) = TRANSECT
    s.line(px(x0), py(y0), px(x1), py(y1), "#FFFFFF", 3)
    for f in (0.0, 0.25, 0.5, 0.75, 1.0):
        gx, gy = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        s.dot(px(gx), py(gy), 4, "#FFFFFF")
    chip(s, px(x0) + 22, py(y0) - 26, "A", INK, occ=mapocc)
    chip(s, px(x1) - 22, py(y1) + 30, "B", INK, occ=mapocc)

    # north arrow + scale bar
    s.arrow(MX + MW - 40, MY + 74, MX + MW - 40, MY + 26, INK, 2, 8)
    s.text("n", "N", MX + MW - 40, MY + 8, 22, INK, bold=True, align="center", font=MONO)
    sb = 2 / KM_W * MW
    s.rect(MX + 16, MY + MH - 68, sb + 16, 50, "#F6F2E8", radius=4,
           border=f"1 SOLID {INK3}")
    s.rect(MX + 24, MY + MH - 58, sb, 8, INK)
    s.rect(MX + 24, MY + MH - 58, sb / 2, 8, "#F6F2E8", border=f"1.5 SOLID {INK}")
    s.text("sb", "0      1      2 km", MX + 24 + sb / 2, MY + MH - 44, 20, INK3,
           align="center", font=MONO)

    # ---- right column: legend + statistics
    rx = 1180
    s.text("lh", "色带（℃）", rx, 196, 22, INK, bold=True)
    yy = 228
    lo = 0.0
    for hi, col in BANDS:
        label = (f"＜ {hi:.1f}" if lo == 0 else
                 (f"{lo:.1f} – {hi:.1f}" if hi < 90 else f"≥ {lo:.1f}"))
        s.rect(rx, yy, 26, 22, col, border=f"1 SOLID {INK3}")
        s.text("lb", label, rx + 36, yy, 20, INK2, font=MONO)
        lo = hi
        yy += 30
    s.line(rx, yy + 6, 1544, yy + 6, FRAME, 1)
    stats = [("最高", f"{vmax:.1f} ℃"), ("郊野基准", f"{vmin:.1f} ℃"),
             ("均值", f"{mean:.1f} ℃"), ("热岛强度 ΔT", f"{vmax - vmin:.1f} ℃"),
             (f"≥{HOT_MIN:.0f} ℃ 面积", f"{hot_area:.1f} km²"), ("断面 A–B 温差", f"{pmax - pmin:.1f} ℃")]
    yy += 20
    for k, v in stats:
        s.text("sk", k, rx, yy, 20, INK2)
        s.text("sv", v, 1544, yy, 20, INK, bold=True, align="right", font=MONO)
        yy += 30

    # ---- transect profile strip
    gy0 = 736
    s.text("ph", "断面 A–B：沿线的地表温度", 56, gy0 - 28, 24, INK, bold=True)
    gx0, gw, gh = 132, 1010, 130
    s.rect(gx0, gy0, gw, gh, "#F6F2E8", border=f"1.5 SOLID {INK3}")
    tmin, tmax = math.floor(pmin) - 0.5, math.ceil(pmax) + 0.5
    for k in range(int(tmin), int(tmax) + 1, 2):
        y = gy0 + gh - (k - tmin) / (tmax - tmin) * gh
        s.line(gx0, y, gx0 + gw, y, "#E2D9C6", 1)
        s.text("py", f"{k}℃", gx0 - 8, y - 10, 20, INK3, align="right", font=MONO)
    profocc = []
    pts = [(gx0 + f * gw, gy0 + gh - (v - tmin) / (tmax - tmin) * gh)
           for f, km, v in prof]
    body = [(gx0, gy0 + gh)] + pts + [(gx0 + gw, gy0 + gh)]
    d = "M " + " L ".join(f"{x - gx0:.1f} {y - gy0:.1f}" for x, y in body) + " Z"
    s.path(gx0, gy0, gw, gh, d, "#DE8C39", opacity=0.55)
    for (x, y), (f, km, v) in list(zip(pts, prof))[4::8]:
        if gx0 + 60 <= x <= gx0 + gw - 40:
            chip(s, x, max(y - 24, gy0 + 16), f"{v:.1f}", INK, occ=profocc)
    s.text("px", "0 km", gx0, gy0 + gh + 8, 20, INK3, font=MONO)
    total_km = prof[-1][1]
    s.text("px2", f"{total_km:.1f} km", gx0 + gw, gy0 + gh + 8, 20, INK3, align="right",
           font=MONO)
    s.text("px3", "沿断面水平距离", gx0 + gw / 2, gy0 + gh + 8, 20, INK3, align="center")

    notes = [f"读图：色带为网格单元均值分档，等值线取自同一网格的线性插值（"
             + "、".join(f"{l:.0f}℃" for l in LEVELS) + "），ΔT 相对郊野基准 "
             + f"{vmin:.1f}℃。",
             "数据说明：温度场由 5 个高斯热源减去水体与绿地降温合成，仅演示制图方法，非实测。"]
    ny = gy0 + gh + 32
    for n in notes:
        assert tw(n, 20) <= 1488, n
        s.text("fn", n, 56, ny, 20, INK3)
        ny += 30
    assert ny <= H - 8, ny
    return s, {"vmin": vmin, "vmax": vmax, "mean": mean, "hot_area_km2": hot_area,
               "transect": {"max": pmax, "min": pmin, "length_km": total_km,
                            "samples": [[round(f, 3), round(km, 2), round(v, 2)]
                                        for f, km, v in prof]},
               "levels": LEVELS, "bands": BANDS, "grid": [NX, NY],
               "isoline_chains": {str(l): len(marching(l)) for l in LEVELS},
               "raster_runs": len(raster())}


def chip(s, x, y, text, colour, occ=None, dark=True):
    """Label chip; nudges vertically until it clears every chip already placed in occ."""
    w = tw(text, 20, True) + 14
    for n in range(0, 9):
        dy = 0 if n == 0 else (32 * ((n + 1) // 2)) * (1 if n % 2 else -1)
        top, bot = y + dy - 4, y + dy + 24
        if not occ or all(top >= b[3] or bot <= b[1] or x - w / 2 >= b[2] or x + w / 2 <= b[0]
                          for b in occ):
            y += dy
            break
    if occ is not None:
        occ.append((x - w / 2, y - 4, x + w / 2, y + 24))
    s.rect(x - w / 2, y - 4, w, 28, "#F6F2E8" if dark else colour, radius=4,
           border=f"1 SOLID {INK3}")
    s.text("chip", text, x, y + 1, 20, INK if dark else PAPER, align="center", font=MONO)


if __name__ == "__main__":
    s, data = build()
    (TMP / "case08.snapshot").write_text(s.dsl(), encoding="utf-8")
    (TMP / "case08-data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(json.dumps(s.audit(margin=40), ensure_ascii=False))
    print(json.dumps({k: data[k] for k in ("vmin", "vmax", "mean", "hot_area_km2",
                                           "raster_runs", "isoline_chains")},
                     ensure_ascii=False))
