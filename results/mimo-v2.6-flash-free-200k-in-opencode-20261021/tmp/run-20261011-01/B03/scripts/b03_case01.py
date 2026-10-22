# -*- coding: utf-8 -*-
"""B03 case-01 · 青禾岭登山等高线路线图 (1200x1600).

user_goal: 选路线并估算时间——两条路线的距离/爬升/用时对得上等高线。
technique: 程序化等高线（同心椭圆环带，高程→半径映射，计曲线加粗）
           + 路线折线（旋转矩阵短线段首尾相接）。
数据: 峰顶782m，等高距40m，10条首曲线含2条计曲线；山门380m；
      用时 = 距离/4.5km/h + 爬升/400m/h（脚本内断言）。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_common as C  # noqa: E402

W, H = 1200, 1600

PEAK = 782          # m
CONT = 40           # contour interval
RING_TOP = 740      # highest drawn contour
RINGS = 10          # plan claim: 10 条
TRAILHEAD_E = 380   # m (outside lowest ring)
INDEX_E = [740, 540]
FLAT_KMH = 4.5
CLIMB_MH = 400

CX, CY = 600, 660   # summit / ring center (canvas coords)
R0, DR, RATIO = 90.0, 42.0, 1.35   # rx = R0 + idx*DR ; ry = rx/RATIO

TRAIL_A = [(560, 1120), (430, 1020), (540, 950), (420, 860), (520, 790),
           (560, 720), (600, 660)]
TRAIL_B = [(560, 1120), (780, 1128), (960, 1090), (1060, 1010), (1040, 900),
           (950, 820), (850, 760), (720, 710), (640, 680), (600, 660)]
SUPPLY_A = (420, 860)   # 补给亭 = TRAIL_A[3]
SUPPLY_B = (1040, 900)  # 溪谷泉 = TRAIL_B[4]


def plen(pts):
    return sum(math.hypot(pts[i + 1][0] - pts[i][0],
                          pts[i + 1][1] - pts[i][1])
               for i in range(len(pts) - 1))


def ring_rx(elev):
    idx = (RING_TOP - elev) / float(CONT)
    return R0 + idx * DR


def facts():
    a_px, b_px = plen(TRAIL_A), plen(TRAIL_B)
    scale = 4200.0 / a_px                 # m per px, A pinned to 4.2 km
    km_a = a_px * scale / 1000.0
    km_b = b_px * scale / 1000.0
    climb = PEAK - TRAILHEAD_E            # 402 m
    t_a = km_a / FLAT_KMH * 60 + climb / CLIMB_MH * 60
    t_b = km_b / FLAT_KMH * 60 + climb / CLIMB_MH * 60
    grade_a = 100.0 * climb / (km_a * 1000)
    grade_b = 100.0 * climb / (km_b * 1000)
    # assertions (plan numeric_claims)
    radii = [ring_rx(RING_TOP - i * CONT) for i in range(RINGS)]
    # plan claim: 环半径随高程单调递减（高处环更小）
    assert all(radii[i] < radii[i + 1] for i in range(RINGS - 1)), radii
    assert ring_rx(740) < ring_rx(540) < ring_rx(380)
    assert all((e - RING_TOP) % 200 == 0 for e in INDEX_E)
    assert TRAIL_A[0] == TRAIL_B[0] and TRAIL_A[-1] == TRAIL_B[-1] == (CX, CY)
    assert round(t_a) == 116, t_a            # 4.2/4.5h + 402/400h = 116.3
    assert 6.5 <= km_b <= 7.0, km_b
    assert km_b > km_a * 1.5 and grade_a > grade_b
    # plan claim: 两线各穿越全部 10 条等高线 — verify by sampling
    def crossed(pts):
        n = 0
        for i in range(RINGS):
            rx = ring_rx(RING_TOP - i * CONT)
            ry = rx / RATIO
            inside = outside = False
            for k in range(len(pts) - 1):
                x0, y0 = pts[k]
                x1, y1 = pts[k + 1]
                steps_n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 3))
                for s in range(steps_n + 1):
                    px = x0 + (x1 - x0) * s / steps_n
                    py = y0 + (y1 - y0) * s / steps_n
                    v = ((px - CX) / rx) ** 2 + ((py - CY) / ry) ** 2
                    if v <= 1:
                        inside = True
                    else:
                        outside = True
            if inside and outside:
                n += 1
        return n
    assert crossed(TRAIL_A) == 10 and crossed(TRAIL_B) == 10, "crossings"
    return dict(km_a=km_a, km_b=km_b, climb=climb, t_a=t_a, t_b=t_b,
                grade_a=grade_a, grade_b=grade_b, scale=scale,
                mpp=scale,
                steps="{:,}".format(int(round(climb / 0.175))))


def main():
    f = facts()
    els = []
    els.append(C.box(0, 0, W, H, "#EFE9DA"))

    # ---------------- header ----------------
    els.append(C.box(0, 0, W, 132, "#1B3A6B"))
    els.append(C.text(48, 30, 760, 62, "青禾岭 · 登山等高线路线图", 44,
                      "#F6F1E4", bold=True))
    els.append(C.text(48, 92, 780, 30,
                      "峰顶 782m · 等高距 40m · 两线自同一山门（380m）登顶",
                      20, "#B8C7E2"))
    els.append(C.text(900, 36, 252, 34, "QINGHE RIDGE", 22, "#8FA8CE",
                      align="RIGHT", letter_space=4))
    els.append(C.text(900, 74, 252, 30, "登山口图板 · 虚构演示", 16, "#B8C7E2",
                      align="RIGHT"))

    # ---------------- map card ----------------
    els.append(C.box(48, 150, 1104, 1000, "#FBF8EF", radius=14,
                     border="#C9BFA6", border_w=2))

    # contours (drawn outer -> inner)
    for i in range(RINGS - 1, -1, -1):
        e = RING_TOP - i * CONT
        rx = ring_rx(e)
        ry = rx / RATIO
        is_index = e in INDEX_E
        els.append(C.ellipse(CX, CY, rx, ry, "#00000000",
                             border="#A98F63",
                             border_w=3 if is_index else 1.4))
    # elevation notes on index contours; the 740 note goes LEFT of its ring
    # (right side is occupied by the summit label block)
    for e in INDEX_E:
        rx = ring_rx(e)
        lx = (CX - rx - 32) if e == RING_TOP else (CX + rx - 30)
        els.append(C.box(lx, CY - 12, 62, 22, "#FBF8EF"))
        els.append(C.text(lx, CY - 12, 62, 22, "%d" % e, 15,
                          "#7A5B35", bold=True, align="CENTER"))
    # outer contour note
    rx_o = ring_rx(TRAILHEAD_E)
    els.append(C.box(CX + rx_o - 30, CY - 12, 62, 22, "#FBF8EF"))
    els.append(C.text(CX + rx_o - 30, CY - 12, 62, 22, "380", 15, "#7A5B35",
                      bold=True, align="CENTER"))

    # summit marker
    els.append(C.circle(CX, CY, 7, "#B3261E"))
    els.append(C.text(CX + 14, CY - 34, 160, 30, "青禾峰 782", 19, "#B3261E",
                      bold=True))

    # trails: A red solid, B green solid (polyline via segs)
    els.append(C.poly(TRAIL_B, 7, "#2E7D4F", radius=3))
    els.append(C.poly(TRAIL_A, 7, "#C1502E", radius=3))
    # supply points
    for (px, py), name, dy in ((SUPPLY_A, "补给亭 480m", -34),
                               (SUPPLY_B, "溪谷泉 460m", -34)):
        els.append(C.circle(px, py, 9, "#FFFFFF", border="#1B3A6B",
                            border_w=3))
        els.append(C.box(px - 52, py + dy, 130, 24, "#1B3A6B", radius=12))
        els.append(C.text(px - 52, py + dy, 130, 24, name, 13, "#FFFFFF",
                          bold=True, align="CENTER"))
    # trailhead gate
    hx, hy = TRAIL_A[0]
    els.append(C.circle(hx, hy, 11, "#1B3A6B"))
    els.append(C.text(hx + 18, hy - 36, 120, 24, "山门 380m", 14, "#1B3A6B",
                      bold=True))
    els.append(C.text(TRAIL_A[1][0] - 74, TRAIL_A[1][1] - 14, 60, 24, "A", 20,
                      "#C1502E", bold=True, align="CENTER"))
    els.append(C.text(TRAIL_B[3][0] + 12, TRAIL_B[3][1] - 40, 60, 24, "B", 20,
                      "#2E7D4F", bold=True, align="CENTER"))

    # legend (top-left, clear of rings: nearest ring x>=296 at y=400)
    els.append(C.box(70, 190, 208, 210, "#FFFFFFE8", radius=10,
                     border="#C9BFA6"))
    els.append(C.text(84, 200, 180, 26, "图例", 17, "#1B3A6B", bold=True))
    leg = [("#A98F63", 1.4, "首曲线 40m"),
           ("#A98F63", 3, "计曲线 200m"),
           ("#C1502E", 6, "A 石阶道"),
           ("#2E7D4F", 6, "B 溪谷道")]
    ly = 234
    for cc, ww, lb in leg:
        els.append(C.box(86, ly + (18 - ww) / 2, 34, ww if ww > 2 else 1.5,
                         cc))
        els.append(C.text(128, ly, 144, 24, lb, 14, "#333333"))
        ly += 30
    els.append(C.circle(103, ly + 14, 7, "#FFFFFF", border="#1B3A6B",
                        border_w=2.5))
    els.append(C.text(128, ly + 2, 144, 24, "补给点", 14, "#333333"))

    # north arrow (top-right of map)
    els.append(C.box(1058, 178, 62, 96, "#FFFFFFE8", radius=8,
                     border="#C9BFA6"))
    els.append(C.poly([(1089, 194), (1075, 232), (1089, 224), (1103, 232),
                       (1089, 194)], 3, "#1B3A6B"))
    els.append(C.text(1058, 238, 62, 30, "N", 20, "#1B3A6B", bold=True,
                      align="CENTER"))

    # scale bar (500 m = 500/mpp px)
    bar = 500.0 / f["mpp"]
    sx, sy = 70, 1088
    els.append(C.box(sx, sy, bar, 10, "#1B3A6B"))
    els.append(C.box(sx + bar, sy, bar, 10, "#FFFFFF", border="#1B3A6B",
                     border_w=1))
    els.append(C.text(sx - 6, sy - 26, 60, 24, "0", 14, "#333333"))
    els.append(C.text(sx + bar - 24, sy - 26, 60, 24, "500", 14, "#333333"))
    els.append(C.text(sx + 2 * bar - 24, sy - 26, 60, 24, "1km", 14,
                      "#333333"))
    els.append(C.text(sx, sy + 16, 300, 24, "比例尺 1px ≈ 5.7m", 14,
                      "#333333"))

    # ---------------- route table ----------------
    ty = 1180
    els.append(C.box(48, ty, 1104, 240, "#FFFFFF", radius=14,
                     border="#C9BFA6"))
    els.append(C.text(72, ty + 18, 400, 34, "路线用时表（上行）", 24, "#1B3A6B",
                      bold=True))
    cols = [72, 320, 470, 620, 790, 940]
    heads = ["路线", "距离", "爬升", "平均坡度", "用时", "备注"]
    colw = [240, 140, 140, 160, 140, 196]
    hy2 = ty + 66
    els.append(C.box(64, hy2 - 6, 1072, 40, "#EDE6D6", radius=6))
    for cx0, hd, cwd in zip(cols, heads, colw):
        els.append(C.text(cx0, hy2, cwd, 30, hd, 17, "#5B4A2E", bold=True))
    rows = [
        ("A 石阶道（实线·红）", f["km_a"], f["climb"], f["grade_a"],
         f["t_a"], "近而陡，石阶约 %s 级" % f["steps"]),
        ("B 溪谷道（实线·绿）", f["km_b"], f["climb"], f["grade_b"],
         f["t_b"], "绕东坡，坡缓亲水"),
    ]
    ry2 = hy2 + 44
    for name, km, climb, grade, tmin, note in rows:
        hh = "%d 小时 %02d 分" % (int(tmin) // 60, round(tmin) % 60)
        vals = [name, "%.1f km" % km, "%d m" % climb, "%.1f%%" % grade, hh,
                note]
        for cx0, v, cwd in zip(cols, vals, colw):
            els.append(C.text(cx0, ry2, cwd, 30, v, 17, "#2E2A25",
                              bold=(cx0 == cols[0])))
        ry2 += 46
    els.append(C.text(72, ty + 196, 1040, 30,
                      "用时 = 距离 ÷ 4.5km/h + 爬升 ÷ 400m/h；"
                      "坡度 = 爬升 ÷ 水平距。下山按上行 ×0.8 估算。",
                      15, "#7A7264"))

    # ---------------- tips ----------------
    ey = 1444
    els.append(C.box(48, ey, 1104, 84, "#E8EFD8", radius=12))
    els.append(C.text(72, ey + 14, 1050, 30,
                      "提示：两线各穿越 10 条等高线；认准计曲线（粗）判断已爬高度。",
                      18, "#2E5A38", bold=True))
    els.append(C.text(72, ey + 48, 1050, 30,
                      "雨天溪谷道泥泞，改走石阶道；日落前 1.5h 须过补给点。",
                      17, "#33553D"))
    els.append(C.footnote(48, H - 52, 1104,
                          "青禾岭为虚构演示山脉；路线、里程与用时均为示意估算，"
                          "不作为实际登山依据",
                          align="CENTER"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-01-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg="#EFE9DA")
    print("km_a=%.2f km_b=%.2f gradeA=%.1f%% gradeB=%.1f%% tA=%d tB=%d"
          % (f["km_a"], f["km_b"], f["grade_a"], f["grade_b"],
             round(f["t_a"]), round(f["t_b"])))


if __name__ == "__main__":
    main()
