# -*- coding: utf-8 -*-
"""B03 case-02 · 江城地铁换乘示意图 (1800x1000).

user_goal: 规划最快换乘——线路、换乘站、步行分钟、末班车对得上。
technique: 强制直角几何——所有线段非水平/垂直即精确45°(|dx|=|dy|断言);
           换乘站=双环白心药丸; 站点钉在线上(点-线距离断言)。
数据: 3线/12站/2换乘枢纽(去重计数断言); 步行2/3分; 末班车≥22:30(解析断言)。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_common as C  # noqa: E402

W, H = 1800, 1000

NAVY = "#14213D"
RED = "#C1502E"      # 1号线
BLUE = "#1B6B9E"     # 2号线
GREEN = "#2E7D4F"    # 4号线
DOT_EDGE = "#333333"
PAPER = "#FCFBF7"

L1 = [(120, 200), (560, 200), (660, 300), (1240, 300), (1340, 200), (1680, 200)]
L2 = [(950, 120), (950, 620), (1050, 720), (1500, 720)]
L4 = [(160, 560), (950, 560), (1150, 560), (1250, 460), (1620, 460)]

# station -> (line, point); IA/IB listed on both lines (dedup-asserted)
STATIONS = {
    "东港": [("1", (120, 200))],
    "老码头": [("1", (560, 200))],
    "人民广场": [("1", (950, 300)), ("2", (950, 300))],
    "文昌门": [("1", (1240, 300))],
    "机场路": [("1", (1680, 200))],
    "江城北": [("2", (950, 120))],
    "南浦": [("2", (950, 560)), ("4", (950, 560))],
    "云栖": [("2", (1500, 720))],
    "西码头": [("4", (160, 560))],
    "双桥": [("4", (620, 560))],
    "荔园": [("4", (1150, 560))],
    "东郊": [("4", (1620, 460))],
}
TERMINALS = {"东港", "机场路", "江城北", "云栖", "西码头", "东郊"}
INTER = {
    "人民广场": {"pt": (950, 300), "lines": ("1", "2"), "walk": 3,
                 "orient": "H"},
    "南浦": {"pt": (950, 560), "lines": ("2", "4"), "walk": 2,
             "orient": "V"},
}
LAST = {  # line: [(direction-terminal, HH:MM), ...]
    "1": [("机场路", "22:55"), ("东港", "23:10")],
    "2": [("云栖", "23:05"), ("江城北", "23:20")],
    "4": [("东郊", "22:40"), ("西码头", "23:00")],
}

LINEPTS = {"1": L1, "2": L2, "4": L4}
LINECOL = {"1": RED, "2": BLUE, "4": GREEN}
LINEFULL = {"1": "东港—机场路", "2": "江城北—云栖", "4": "西码头—东郊"}


def seg_ok(pts):
    """every segment must be horizontal, vertical or exact 45°."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        assert dx == 0 or dy == 0 or dx == dy, (pts, (x0, y0), (x1, y1))


def on_line(pt, pts):
    x, y = pt
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        ex, ey = x1 - x0, y1 - y0
        L2_ = ex * ex + ey * ey
        t = 0.0 if L2_ == 0 else max(0.0, min(1.0, ((x - x0) * ex + (y - y0) * ey) / L2_))
        px, py = x0 + ex * t, y0 + ey * t
        if abs(px - x) < 1e-9 and abs(py - y) < 1e-9:
            return True
    return False


def hhmm_min(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def facts():
    for pts in LINEPTS.values():
        seg_ok(pts)
    # stations on their lines
    for name, occ in STATIONS.items():
        for ln, pt in occ:
            assert on_line(pt, LINEPTS[ln]), (name, ln, pt)
    # 12 distinct stations, 2 interchanges
    assert len(STATIONS) == 12, len(STATIONS)
    assert set(INTER) == {"人民广场", "南浦"}
    for nm, it in INTER.items():
        assert tuple(sorted(l for l, p in STATIONS[nm])) == tuple(sorted(it["lines"]))
        assert it["pt"] == STATIONS[nm][0][1]
    assert sorted(it["walk"] for it in INTER.values()) == [2, 3]
    # last trains: all >= 22:30, terminals match line terminals
    for ln, rows in LAST.items():
        for term, t in rows:
            assert hhmm_min(t) >= 22 * 60 + 30, (ln, t)
            assert term in TERMINALS, (ln, term)
    # each line's last-train directions = its two terminals
    line_terms = {}
    for nm, occ in STATIONS.items():
        if nm in TERMINALS:
            line_terms[nm] = occ[0][0]
    for ln, rows in LAST.items():
        got = sorted(t for t, _ in rows)
        want = sorted(nm for nm in TERMINALS if line_terms[nm] == ln)
        assert got == want, (ln, got, want)
    return True


def polyline(pts, color, width=12):
    return C.poly(pts, width, color, radius=width / 2)


def dot(pt, color, r=8):
    x, y = pt
    return C.circle(x, y, r, "#FFFFFF", border=color, border_w=4)


def term_bar(pt, ln, horiz):
    x, y = pt
    if horiz:
        return C.box(x - 6, y - 22, 12, 44, DOT_EDGE, radius=3)
    return C.box(x - 22, y - 6, 44, 12, DOT_EDGE, radius=3)


def pill(pt, orient, gap=15, r=13):
    x, y = pt
    if orient == "H":
        a, b = (x - gap, y), (x + gap, y)
    else:
        a, b = (x, y - gap), (x, y + gap)
    return (C.circle(a[0], a[1], r, "#FFFFFF", border=DOT_EDGE, border_w=3.5)
            + C.circle(b[0], b[1], r, "#FFFFFF", border=DOT_EDGE, border_w=3.5)
            + C.circle(a[0], a[1], r - 4.5, "#FFFFFF")
            + C.circle(b[0], b[1], r - 4.5, "#FFFFFF"))


def badge(x, y, ln, size=48, fs=26):
    return (C.box(x, y, size, size, LINECOL[ln], radius=12)
            + C.text(x, y + (size - fs) / 2 - 2, size, fs + 4, ln, fs,
                     "#FFFFFF", bold=True, align="CENTER"))


def main():
    facts()
    els = [C.box(0, 0, W, H, "#EDEAE0")]
    # header
    els.append(C.box(0, 0, W, 90, NAVY))
    els.append(C.text(48, 14, 700, 44, "江城地铁 · 换乘示意图", 36, "#F6F3EA",
                      bold=True))
    els.append(C.text(48, 56, 900, 28,
                      "1 / 2 / 4 号线 · 12 座车站 · 2 座换乘枢纽 · "
                      "全图仅水平/垂直/45° 走线", 18, "#A9BBD8"))
    els.append(C.text(1300, 22, 452, 30, "JIANGCHENG METRO", 20, "#7E96BC",
                      align="RIGHT", letter_space=5))
    els.append(C.text(1300, 54, 452, 24, "虚构演示网络 · 站名时刻均为演示数据",
                      15, "#A9BBD8", align="RIGHT"))

    # map card
    els.append(C.box(40, 110, 1720, 670, PAPER, radius=14, border="#CFC8B6",
                     border_w=2))

    # lines (draw order: 2, 4, 1 — thinner visual hierarchy via dots on top)
    els.append(polyline(L2, BLUE))
    els.append(polyline(L4, GREEN))
    els.append(polyline(L1, RED))

    # terminal bars (perpendicular tick at each line end)
    for nm, (ln, pt) in [(n, v[0]) for n, v in STATIONS.items() if n in TERMINALS]:
        # terminal tick perpendicular to local direction
        nxt = dict((n, v[0][1]) for n, v in STATIONS.items())
        pts = LINEPTS[ln]
        i = pts.index(pt)
        if i == 0:
            p0, p1 = pts[0], pts[1]
        else:
            p0, p1 = pts[-2], pts[-1]
        horiz = p0[1] == p1[1]
        els.append(term_bar(pt, ln, horiz))

    # station dots
    for nm, occ in STATIONS.items():
        if nm in INTER:
            continue
        ln, pt = occ[0]
        els.append(dot(pt, LINECOL[ln]))
    # interchange pills on top
    for nm, it in INTER.items():
        els.append(pill(it["pt"], it["orient"]))

    # labels
    labels = [
        ("东港", 60, 216, 140, "LEFT"), ("老码头", 500, 152, 160, "LEFT"),
        ("人民广场", 780, 252, 160, "RIGHT"), ("文昌门", 1150, 318, 160, "LEFT"),
        ("机场路", 1540, 140, 180, "RIGHT"), ("江城北", 758, 112, 170, "RIGHT"),
        ("南浦", 758, 520, 170, "RIGHT"), ("云栖", 1420, 738, 160, "LEFT"),
        ("西码头", 100, 578, 150, "LEFT"), ("双桥", 560, 512, 140, "LEFT"),
        ("荔园", 1090, 578, 140, "LEFT"), ("东郊", 1520, 414, 150, "LEFT"),
    ]
    for nm, lx, ly, lw, al in labels:
        bold = nm in TERMINALS or nm in INTER
        els.append(C.text(lx, ly, lw, 30, nm, 23, "#1D2634", bold=bold,
                          align=al))
    # interchange sub-notes (right of pills, clear of lines)
    els.append(C.text(975, 252, 170, 26, "换乘 1 ↔ 2", 16, "#5A6B80"))
    els.append(C.text(975, 520, 170, 26, "换乘 2 ↔ 4", 16, "#5A6B80"))
    # walk-time chips
    els.append(C.box(700, 330, 172, 28, "#14213D", radius=14))
    els.append(C.text(700, 333, 172, 24, "步行 3 分", 16, "#FFFFFF",
                      bold=True, align="CENTER"))
    els.append(C.box(700, 592, 172, 28, "#14213D", radius=14))
    els.append(C.text(700, 595, 172, 24, "步行 2 分", 16, "#FFFFFF",
                      bold=True, align="CENTER"))

    # line badges
    els.append(badge(44, 138, "1"))
    els.append(badge(974, 122, "2"))
    els.append(badge(44, 534, "4"))

    # legend
    els.append(C.box(60, 624, 320, 152, "#FFFFFFE8", radius=10,
                     border="#CFC8B6"))
    els.append(C.text(76, 634, 280, 26, "图例", 17, NAVY, bold=True))
    ly = 666
    for ln in ("1", "2", "4"):
        els.append(C.box(78, ly + 6, 34, 10, LINECOL[ln], radius=5))
        els.append(C.text(124, ly, 240, 24,
                          "%s号线 %s" % (ln, LINEFULL[ln]), 15, "#333333"))
        ly += 26
    els.append(C.circle(88, 748, 8, "#FFFFFF", border=DOT_EDGE, border_w=2.5))
    els.append(C.circle(98, 748, 8, "#FFFFFF", border=DOT_EDGE, border_w=2.5))
    els.append(C.text(118, 736, 250, 24, "双环=换乘枢纽 · 端点标记=终点站",
                      14, "#333333"))

    # last-train panel
    els.append(C.box(40, 800, 1720, 150, "#FFFFFF", radius=14,
                     border="#CFC8B6"))
    els.append(C.text(70, 812, 500, 30, "末班车（虚构演示时刻）", 21, NAVY,
                      bold=True))
    xs = {"1": 70, "2": 640, "4": 1210}
    for ln, x0 in xs.items():
        els.append(badge(x0, 858, ln, size=36, fs=20))
        els.append(C.text(x0 + 46, 862, 140, 28, "%s号线" % ln, 19,
                          LINECOL[ln], bold=True))
        for j, (term, t) in enumerate(LAST[ln]):
            els.append(C.text(x0 + 180, 856 + j * 32, 260, 28,
                              "往 %s  %s" % (term, t), 18, "#2E2A25"))
    els.append(C.footnote(40, 958, 1720,
                          "江城地铁为虚构演示网络；线路走向、站名与时刻均为演示数据，"
                          "不作为实际出行依据",
                          align="CENTER"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "drafts", "case-02-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg="#EDEAE0")
    print("facts ok: 12 stations, 45°-grid lines, last trains >=22:30")


if __name__ == "__main__":
    main()
