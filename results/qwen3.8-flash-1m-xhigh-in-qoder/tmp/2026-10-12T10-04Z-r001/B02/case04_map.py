"""B02 case-04 - 沿江街区内涝风险与避难可达性 (1600x1000 制图板).

Touchpoint: the wall-sized plate used in the planning meeting. The risk index, the colour
bands, the isolines, the shelter walk-isochrones, the A-B transect and every statistic come
from data.py's field, so the map and the numbers on the poster, the app and the report are
the same numbers. Plan scale is isotropic: 1 px = 3.64 m.

Run:  python tmp/<run_id>/B02/case04_map.py
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "B02"))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
import data  # noqa: E402
import tide  # noqa: E402
from bkit import MONO, SANS, tw  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B02"
W, H = 1600, 1000
MX, MY, MW, MH = 150, 216, 800, 500
M_PER_PX = data.KM_W * 1000 / MW
NX, NY = data.NX, data.NY
CX, CY = MW / NX, MH / NY


def px(gx):
    return MX + gx * MW


def py(gy):
    return MY + gy * MH


def runs():
    """Row-wise run-length merge of equal risk classes."""
    out = []
    for j in range(NY):
        i = 0
        while i < NX:
            c = data.risk_class(data.GRID[j][i]) if hasattr(data, "GRID") else None
            c = data.risk_class(data.risk_value((i + .5) / NX, (j + .5) / NY))
            k = i
            while k < NX and data.risk_class(
                    data.risk_value((k + .5) / NX, (j + .5) / NY)) == c:
                k += 1
            out.append((i, j, k - i, c))
            i = k
    return out


def marching(level):
    g = [[data.risk_value((i + .5) / NX, (j + .5) / NY) for i in range(NX)]
         for j in range(NY)]
    segs = []
    for j in range(NY - 1):
        for i in range(NX - 1):
            v = [g[j][i], g[j][i + 1], g[j + 1][i + 1], g[j + 1][i]]
            c = [x >= level for x in v]
            if all(c) or not any(c):
                continue

            def t(a, b):
                return 0.5 if a == b else (level - a) / (b - a)
            pts = []
            if c[0] != c[1]:
                pts.append((i + t(v[0], v[1]), j))
            if c[1] != c[2]:
                pts.append((i + 1.0, j + t(v[1], v[2])))
            if c[2] != c[3]:
                pts.append((i + t(v[3], v[2]), j + 1.0))
            if c[3] != c[0]:
                pts.append((i, j + t(v[0], v[3])))
            if len(pts) >= 2:
                segs.append((pts[0], pts[1]))
                if len(pts) == 4:
                    segs.append((pts[2], pts[3]))
    return segs


def build():
    grid = [[data.risk_value((i + .5) / NX, (j + .5) / NY) for i in range(NX)]
            for j in range(NY)]
    flat = [v for row in grid for v in row]
    st = data.risk_stats()
    prof = data.transect()
    tide.assert_contrast([(tide.INK_2, tide.PAPER, "body"), (tide.INK_3, tide.PAPER, "meta")],
                         4.5)
    s = tide.sheet(W, H, min_font=20)
    tide.lockup(s, 56, 40, 64, tide.INK, latin=False)
    s.text("title", "沿江街区内涝风险与避难可达性", 56, 112, 34, tide.INK, bold=True)
    s.text("sub", f"设计降雨 {data.RAIN_MM:.0f} mm / 3 h · 风险指数＝低洼度 × 雨量 ÷ 管网余量 · "
                  f"网格 {NX}×{NY} · 1 px ＝ {M_PER_PX:.1f} m", 56, 156, 22, tide.INK_3)
    s.text("stat", f"最高 {st['max']:.0f} · 均值 {st['mean']:.0f} · ≥60 面积 {st['area_high_km2']} km² · "
                   f"集合点 5 处（开放 {sum(1 for x in data.SHELTERS if x[6])}）",
           56, 182, 22, tide.INK, bold=True)

    # ---- plan frame and km ticks
    s.rect(MX, MY, MW, MH, "#F6F2E8", border=f"2 SOLID {tide.INK}")
    for k in range(0, 31, 5):
        x = MX + k / 32 * MW
        s.line(x, MY + MH, x, MY + MH + 7, tide.INK_3, 1)
        s.text("tx", f"{k / 10:.1f}", x, MY + MH + 15, 20, tide.INK_3, align="center",
               font=MONO)
    for k in range(0, 21, 5):
        y = MY + k / 20 * MH
        s.line(MX - 7, y, MX, y, tide.INK_3, 1)
        s.text("ty", f"{k / 10:.1f} km" if k == 20 else f"{k / 10:.1f}", MX - 12, y - 10,
               20, tide.INK_3, align="right", font=MONO)
    s.text("ux", "km", MX + MW - 4, MY + MH + 15, 20, tide.INK_3, align="right",
           font=MONO)

    # ---- risk raster
    for i, j, n, c in runs():
        s.rect(px(i / NX), py(j / NY), n * CX + 0.6, CY + 0.6, data.RISK_COLOURS[c])
    # river channel line
    ch = [(gx / NX, data.CHANNEL(gx / NX)) for gx in
          [k * 2 / NX * 10 for k in range(0, NX * 10 // 20 + 1)]]
    for (ax, ay), (bx, by) in zip(ch, ch[1:]):
        s.line(px(ax), py(ay), px(bx), py(by), "#5E8FA8", 5)

    # ---- isolines
    for lv in (20, 40, 60, 80):
        for a, b in marching(lv):
            s.line(px(a[0] / NX), py(a[1] / NY), px(b[0] / NX), py(b[1] / NY),
                   "#3A3F47", 1.4)
        segs = marching(lv)
        if segs:
            anchor = MX + MW * (0.2 + 0.2 * (lv // 20 - 1))
            a = min((s0 for seg in segs for s0 in seg), key=lambda q: abs(px(q[0] / NX) - anchor))
            tide_chip(s, px(a[0] / NX), py(a[1] / NY), f"{lv}", INK=tide.INK)

    # ---- shelters + clipped isochrones + gate
    rpx = data.SHELTER_RADIUS_M / (data.KM_W * 1000 / MW)
    for code, nm, fx, fy, cap, storey, opened in data.SHELTERS:
        cx, cy = px(fx), py(fy)
        col = tide.SAFE if opened else tide.ALARM
        n = 96
        for k in range(n):
            a0 = 2 * math.pi * k / n
            a1 = 2 * math.pi * (k + 1) / n
            x0, y0 = cx + rpx * math.cos(a0), cy + rpx * math.sin(a0)
            x1, y1 = cx + rpx * math.cos(a1), cy + rpx * math.sin(a1)
            if MX <= x0 <= MX + MW and MY <= y0 <= MY + MH                     and MX <= x1 <= MX + MW and MY <= y1 <= MY + MH:
                s.line(x0, y0, x1, y1, col, 1.8)
        s.dot(cx, cy, 13, col)
        s.text("sh", code.split("-")[1].lstrip("0"), cx, cy - 10, 20, tide.PAPER,
               align="center", font=MONO, bold=True)
    gx, gy = px(data.GATE[0]), py(data.GATE[1])
    s.rect(gx - 9, gy - 9, 18, 18, tide.INK, radius=3)
    s.text("gt", "社区出入口", gx, gy + 16, 20, tide.INK, align="center", bold=True)
    for code, nm, fx, fy, cap, storey, opened in data.SHELTERS:
        s.line(gx, gy, px(fx), py(fy), "#B9AFA0", 1.4)

    # ---- right column
    tops = sorted(((data.risk_value(cx2, cy2), cx2, cy2)
                   for cx2 in [k / 8 for k in range(1, 8)]
                   for cy2 in [k / 6 for k in range(1, 6)]), reverse=True)[:5]
    rx = 990
    s.text("lh", "风险指数分级", rx, 190, 24, tide.INK, bold=True)
    yy = 224
    lo = 0.0
    for (hi, name), c2 in zip(data.RISK_LEVELS, data.RISK_COLOURS):
        label = f"{lo:.0f} – {hi:.0f}" if hi < 1e8 else f"≥ {lo:.0f}"
        share = sum(1 for v in flat if lo <= v < hi) / len(flat) * 100
        s.rect(rx, yy, 26, 24, c2, border=f"1 SOLID {tide.INK_3}")
        s.text("lb", label, rx + 36, yy + 2, 20, tide.INK_2, font=MONO)
        s.text("lbn", name, rx + 140, yy + 2, 20, tide.INK)
        s.text("lbs", f"{share:.0f}%", rx + 540, yy + 2, 20, tide.INK_3, align="right",
               font=MONO)
        lo = hi
        yy += 30
    s.line(rx, yy + 4, 1560, yy + 4, tide.LINE, 1)
    yy += 20
    s.text("shh", "集合点与步行可达（自社区出入口）", rx, yy, 22, tide.INK, bold=True)
    yy += 34
    for code, nm, fx, fy, cap, storey, opened in data.SHELTERS:
        dist, mins = data.shelter_reach(code)
        s.dot(rx + 12, yy + 11, 11, tide.SAFE if opened else tide.ALARM)
        s.text("sn2", code.split("-")[1].lstrip("0"), rx + 12, yy + 2, 20, tide.PAPER,
               align="center", bold=True, font=MONO)
        s.text("sn", nm, rx + 32, yy + 2, 20, tide.INK)
        mid = f"{cap} 人 · {storey}"
        s.text("sr", mid, rx + 236, yy + 2, 20, tide.INK_2, font=MONO)
        s.text("sw", f"{dist / 1000:.1f} km · {mins} 分", 1560, yy + 2, 20,
               tide.INK_2 if opened else tide.ALARM, align="right", font=MONO)
        assert tw(nm, 20) <= 190 and tw(mid, 20, True) <= 150, (nm, mid)
        assert rx + 236 + tw(mid, 20, True) < 1560 - tw(f"{dist / 1000:.1f} km · {mins} 分",
                                                       20, True)
        yy += 30
    s.line(rx, yy + 4, 1560, yy + 4, tide.LINE, 1)
    yy += 20
    s.text("bh", "风险最高的 5 个采样点", rx, yy, 22, tide.INK, bold=True)
    yy += 32
    for i, (v, cx2, cy2) in enumerate(tops):
        s.text("bi", f"{i + 1}", rx, yy, 20, tide.INK_3, font=MONO)
        s.text("bn", f"({cx2 * data.KM_W:.1f}, {cy2 * data.KM_H:.1f}) km", rx + 26, yy, 20,
               tide.INK_2, font=MONO)
        s.text("bv", f"{v:.0f}", 1560, yy, 20, data.RISK_COLOURS[data.risk_class(v)],
               bold=True, align="right", font=MONO)
        yy += 28
    s.line(rx, yy + 4, 1560, yy + 4, tide.LINE, 1)
    yy += 20
    blind = sum(1 for x in data.SHELTERS if not x[6])
    uncovered = sum(1 for v in flat if v >= 60) / len(flat)
    send = s.para("note", f"≥60 的高风险面约占 {uncovered * 100:.0f}%；未开放集合点 {blind} 处。"
                          f"步行 {data.WALK_MIN} 分钟圈按 {data.SHELTER_RADIUS_M:.0f} m 画，"
                          "超出图幅的部分已裁掉。", rx, yy, 20, tide.INK_3, width=570)
    assert send - 15 <= 900, send
    # ---- transect profile
    ty0 = 772
    s.text("ph", "断面", 56, ty0 + 14, 22, tide.INK, bold=True)
    s.text("ph1b", "A–B", 56, ty0 + 44, 22, tide.INK, bold=True)
    s.text("ph2", "指数", 56, ty0 + 78, 20, tide.INK_3)
    gx0, gw, gh = MX, MW, 100
    s.rect(gx0, ty0, gw, gh, "#F6F2E8", border=f"1.5 SOLID {tide.INK_3}")
    for k in (0, 25, 50, 75, 100):
        y = ty0 + gh - k / 100 * gh
        s.line(gx0, y, gx0 + gw, y, "#E4DECD", 1)
        s.text("py", f"{k}", gx0 - 12, y - 10, 20, tide.INK_3, align="right", font=MONO)
    pts = [(gx0 + gw * f, ty0 + gh - min(v, 100) / 100 * gh) for f, km, v in
            [(x, x * data.KM_W, v) for x, v in prof]]
    body = [(gx0, ty0 + gh)] + pts + [(gx0 + gw, ty0 + gh)]
    d = "M " + " L ".join(f"{p[0] - gx0:.1f} {p[1] - ty0:.1f}" for p in body) + " Z"
    s.path(gx0, ty0, gw, gh, d, "#E39B45", opacity=0.55)
    for (x, y), (xx, v) in list(zip(pts, prof))[6::9]:
        tide_chip(s, x, y - 22, f"{v:.0f}", tide.INK)
    for lab, (ax, ay) in (("A", TRAN_A), ("B", TRAN_B)):
        s.dot(px(ax), py(ay), 7, tide.PAPER, ring=tide.INK, ring_w=2)
        s.text("tl", lab, px(ax) - 26 if lab == "A" else px(ax) + 14, py(ay) - 12, 22,
               tide.INK, bold=True, font=MONO)
    s.text("tx2", "0 km", gx0, ty0 + gh + 8, 20, tide.INK_3, font=MONO)
    s.text("tx3", f"{data.KM_W:.1f} km", gx0 + gw, ty0 + gh + 8, 20, tide.INK_3,
           align="right", font=MONO)
    s.text("tx4", "沿断面水平距离", gx0 + gw / 2, ty0 + gh + 8, 20, tide.INK_3, align="center")
    notes = [f"口径：指数为 0–100 相对值，非水深；色带与等值线（20/40/60/80）取自同一网格线性插值。",
             "演示数据：地形、管网与集合点均为虚构示例，用于说明制图方法，不代表任何真实城市。"]
    ny = ty0 + gh + 36
    for n in notes:
        assert tw(n, 20) <= W - 112, n
        s.text("fn", n, 56, ny, 20, tide.INK_3)
        ny += 28
    assert ny - 28 + 21.2 <= H - 20, ny
    return s, {"stats": st, "class_share": share_report(flat), "top5": [
                   {"xy_km": [round(v[1] * data.KM_W, 2), round(v[2] * data.KM_H, 2)],
                    "index": round(v[0], 1)} for v in tops],
               "shelters": [[c[0], c[1], *data.shelter_reach(c[0]), c[4], c[5], c[6]]
                            for c in data.SHELTERS],
               "transect": [[round(x, 3), round(v, 1)] for x, v in prof],
               "isolines": {str(l): len(marching(l)) for l in (20, 40, 60, 80)},
               "raster_runs": len(runs())}


TRAN_A, TRAN_B = data.TRANSECT


def tide_chip(s, x, y, text, INK=tide.INK):
    w = tw(text, 20, True) + 14
    s.rect(x - w / 2, y - 4, w, 28, tide.PAPER, radius=4, border=f"1 SOLID {tide.INK_3}")
    s.text("chip", text, x, y + 1, 20, INK, align="center", font=MONO)


def share_report(flat):
    out, lo = {}, 0.0
    for (hi, name) in data.RISK_LEVELS:
        out[name] = round(sum(1 for v in flat if lo <= v < hi) / len(flat) * 100, 1)
        lo = hi
    return out


if __name__ == "__main__":
    s, d = build()
    (TMP / "case04.snapshot").write_text(s.dsl(), encoding="utf-8")
    (TMP / "case04-data.json").write_text(json.dumps(d, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(json.dumps(s.audit(margin=40), ensure_ascii=False))
    print(json.dumps({k: d[k] for k in ("stats", "class_share", "raster_runs",
                                        "isolines")}, ensure_ascii=False))
