# -*- coding: utf-8 -*-
"""B05 case-07 · 车机 · 驾驶避水提醒 (head unit 1280x720).

Audience: 林岚 driving her own car (140mm ground clearance) in the rain. The
screen must be readable in a glance: one huge block verdict, one explainable
reason line, one reroute confirmation with an ETA that matches case-03, and a
muted secondary strip that never competes with the alert.

The depth-vs-clearance comparison is the signature DepthRuler with the car's
clearance drawn on as a reference line. Water height and the clearance line are
both derived from the same centimetre scale, so the 18cm overhang the driver is
being warned about is a measured distance, not a decoration.
"""
import math
import os
import sys
from b05_common import box, circle, seg, text, tw
from b05_ui import (BG, BG2, CARD, STROKE, STROKE_HI, INK, SUB, MUTED, AQUA,
                    R_SAFE, R_CAUTION, R_DETOUR, R_BLOCK, F_BODY, F_NUM,
                    F_MONO, depth_ruler, risk_color, risk_label)
from b05_data import (HERO, depth, pname, ptime, ptrend, TREND_TXT,
                      TREND_ARROW, CAR_CLEAR_MM, car_passable, ROUTES,
                      ROUTE_RECO, WEEK, OPS)

W, H = 1280, 720
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "drafts"))

NOW = 8 * 60 + 15                       # shared demo clock, matches case-03
CLEAR_CM = CAR_CLEAR_MM / 10.0          # 14.0cm
RULER_MAX = 50.0


def _eta(mins):
    """arrival clock time from NOW (08:15) + mins — same rule as case-03."""
    base = NOW + mins
    return "%02d:%02d" % (base // 60, base % 60)


def ruler_y(y, h, cm):
    """pixel y of a depth on the shared ruler scale (mirrors depth_ruler)."""
    top, bot = y + 18, y + h - 18
    return bot - (cm / RULER_MAX) * (bot - top)


def build():
    el = []
    el.append(box(0, 0, W, H, BG))

    # ---- header ----
    el.append(box(0, 0, W, 70, BG2))
    el.append(box(0, 69, W, 1.5, STROKE))
    el.append(box(32, 20, 30, 30, AQUA, radius=9))
    el.append(text(32, 24, 30, 24, "水", 19, "#04222B", bold=True,
                   align="CENTER"))
    el.append(text(74, 20, 340, 30, "水线 · 车机导航", 21, SUB, bold=True))
    el.append(text(420, 24, 300, 26, "08:15  周三 10月21日", 18, MUTED,
                   font=F_MONO))
    el.append(text(W - 44 - 300, 22, 300, 30, "暴雨橙色预警 · Ⅱ级", 20,
                   R_DETOUR, bold=True, align="RIGHT"))

    # ---- block banner: the verdict, readable across the cabin ----
    by, bh = 86, 150
    el.append(box(32, by, W - 64, bh, "#2A1420", radius=22, border=R_BLOCK,
                  border_w=2.5))
    el.append(box(32, by, 12, bh, R_BLOCK, radius=6))
    el.append(text(72, by + 22, 460, 96, "禁止通行", 78, R_BLOCK, bold=True))
    el.append(text(72, by + 108, 520, 32, "已为你改道 · 无需操作", 22, SUB))
    # right: point + distance
    el.append(text(W - 44 - 480, by + 26, 460, 42, pname(HERO), 34, INK,
                   bold=True, align="RIGHT"))
    el.append(text(W - 44 - 480, by + 78, 460, 34,
                   "前方 320m · 下穿隧道", 24, MUTED, align="RIGHT"))
    d = depth(HERO)
    el.append(text(W - 44 - 480, by + 112, 460, 30,
                   "水深 %.0fcm · %s%s" % (d, TREND_TXT[ptrend(HERO)],
                                           TREND_ARROW[ptrend(HERO)]),
                   22, R_BLOCK, bold=True, align="RIGHT", font=F_MONO))

    # ---- left: depth vs clearance, one shared centimetre scale ----
    ly, lh = 252, 300
    ry, rh = ly + 16, lh - 32
    el.append(depth_ruler(56, ry, 200, rh, d, max_cm=RULER_MAX))
    # clearance reference line at 14cm, drawn on the same track
    rtrack_x0, rtrack_x1 = 56 + 14 + 40, 56 + 200 - 14 - 60
    cy = ruler_y(ry, rh, CLEAR_CM)
    el.append(box(rtrack_x0 - 10, cy - 2.5, (rtrack_x1 - rtrack_x0) + 20, 5,
                  INK))
    el.append(circle(rtrack_x0 - 10, cy, 8, INK))
    # leader out to the label, clear of the ruler body
    el.append(box(rtrack_x1 + 12, cy - 1.5, 96, 3, INK))
    el.append(box(rtrack_x1 + 100, cy - 22, 128, 44, "#13314A", radius=12,
                  border=INK, border_w=1.5))
    el.append(text(rtrack_x1 + 100, cy - 17, 128, 22, "离地间隙", 17, MUTED,
                   align="CENTER"))
    el.append(text(rtrack_x1 + 100, cy + 2, 128, 24, "%.0fmm" % CAR_CLEAR_MM,
                   20, INK, bold=True, align="CENTER", font=F_NUM))

    # ---- left: the one-sentence reason + the measured overhang ----
    # width is bounded by the reroute card, never allowed to run under it
    tx = 440
    mw = W - 44 - 400 - tx - 24
    assert tx > rtrack_x1 + 100 + 128, "reason column collides with clearance chip"
    el.append(text(tx, ly + 20, mw, 40, "为何不可通行", 26, MUTED, bold=True))
    el.append(text(tx, ly + 64, mw, 96,
                   "水深 %.0fcm\n高于离地间隙 %.0fcm" % (d, CLEAR_CM), 32, INK,
                   bold=True, line_h=44))
    # overhang callout: measured, not decorative.
    # tw() UNDER-estimates real rendered width by ~4-5% (it assumes 0.56em for
    # Latin, but Inter Bold's advances are wider) — calibrated by probe: the
    # string "超出 18cm" at 38px needs ~190px yet tw() reports 182.4, so a
    # 183px slot clipped it to "超出". Apply an explicit safety factor.
    _txt = "超出 %.0fcm" % (d - CLEAR_CM)
    _fit = tw(_txt, 38) * 1.10
    ow = int(math.ceil(_fit)) + 56
    assert ow + 16 < mw, "overhang badge overflows the reason column"
    el.append(box(tx, ly + 160, ow, 64, "#2A1420", radius=16, border=R_BLOCK,
                  border_w=2))
    el.append(text(tx + 28, ly + 170, ow - 56, 44, _txt, 38, R_BLOCK,
                   bold=True, font=F_NUM))
    assert _fit <= ow - 56, "overhang text would wrap inside its badge"
    el.append(text(tx, ly + 232, mw, 26,
                   "≈ %d 瓶矿泉水的高度" % round((d - CLEAR_CM) / 5), 19, MUTED))
    el.append(text(tx, ly + 264, mw, 28,
                   "隧道积水仍在%s，绕行仅多 %d 分钟" %
                   (TREND_TXT[ptrend(HERO)],
                    ROUTES[ROUTE_RECO][1] - ROUTES[0][1]), 20, SUB))

    # ---- right: reroute confirmation ----
    cx, cw = W - 44 - 400, 400
    el.append(box(cx, ly, cw, lh, CARD, radius=20, border=AQUA, border_w=2))
    el.append(circle(cx + 40, ly + 42, 18, AQUA))
    el.append(text(cx + 27, ly + 30, 26, 26, "✓", 22, "#04222B", bold=True,
                   align="CENTER"))
    el.append(text(cx + 70, ly + 24, 300, 38, "已自动改道", 30, AQUA,
                   bold=True))
    # route name + minutes, digits and unit in separate slots
    rt = ROUTES[ROUTE_RECO][0]
    mins = ROUTES[ROUTE_RECO][1]
    el.append(text(cx + 32, ly + 80, 240, 44, rt, 32, INK, bold=True))
    el.append(text(cx + cw - 32 - 150, ly + 72, 110, 56, str(mins), 46, AQUA,
                   bold=True, align="RIGHT", font=F_NUM))
    el.append(text(cx + cw - 32 - 40, ly + 96, 40, 30, "分", 22, SUB))
    el.append(box(cx + 32, ly + 136, cw - 64, 1.5, STROKE))
    # ETA left, delta right — kept on one row so the buttons stay inside the card
    el.append(text(cx + 32, ly + 152, 170, 32, "预计 %s 到达" % _eta(mins), 19,
                   SUB))
    el.append(text(cx + cw - 32 - 150, ly + 152, 150, 32, "较最短 +%d 分钟" %
                   (mins - ROUTES[0][1]), 19, MUTED, align="RIGHT"))
    el.append(text(cx + 32, ly + 192, cw - 64, 30,
                   "避开 %s" % ROUTES[0][3], 19, MUTED))
    assert 32 + 160 + 12 < cw - 32 - 150, "ETA row collides with delta"
    # two glanceable actions
    el.append(box(cx + 32, ly + 232, 200, 52, AQUA, radius=14))
    el.append(text(cx + 32, ly + 244, 200, 30, "知道了", 22, "#04222B",
                   bold=True, align="CENTER"))
    el.append(box(cx + 248, ly + 232, 120, 52, "transparent", radius=14,
                  border=STROKE, border_w=1.5))
    el.append(text(cx + 248, ly + 244, 120, 30, "取消", 22, SUB, bold=True,
                   align="CENTER"))

    # ---- bottom: secondary strip, deliberately quiet (C5) ----
    sy, sh = 568, 104
    tiles = [("橙色预警 · Ⅱ级", "3小时 50mm 以上", R_DETOUR),
             ("沿途最低点", "高新桥下 15cm 谨慎", R_CAUTION),
             ("今日上报", "3 条 · 采纳 2", AQUA),
             ("数据更新", "%s · 传感器 46/52" % ptime(HERO), MUTED)]
    tw3 = (W - 64 - 3 * 20) / 4.0
    for i, (h1, h2, col) in enumerate(tiles):
        x = 32 + i * (tw3 + 20)
        el.append(box(x, sy, tw3, sh, "#0C1E2E", radius=14, border=STROKE,
                      border_w=1))
        el.append(box(x, sy, 6, sh, col, radius=3))
        el.append(text(x + 24, sy + 20, tw3 - 40, 28, h1, 19, MUTED))
        el.append(text(x + 24, sy + 52, tw3 - 40, 34, h2, 21, SUB))
    el.append(text(32, sy + sh + 12, W - 64, 26,
                   "演示数据 · 水深与车辆离地间隙均为虚构演示值，"
                   "风险判定为产品自定规则，非官方标准", 16, MUTED))

    # ---- generation guards ----
    # C1: the verdict is the shared rule, not a hand-typed string
    assert car_passable(d) is False, "32cm must fail the 140mm clearance rule"
    assert car_passable(depth("P4")) is True, "8cm must pass the same rule"
    assert not (car_passable(d) and car_passable(depth("P4")))
    # the overhang the callout shows is a real subtraction on one scale
    assert abs((d - CLEAR_CM) - 18.0) < 1e-6
    # both the fill and the clearance line are placed by the same formula;
    # depth_ruler insets 18px top AND bottom, so the track spans rh - 36
    track_h = rh - 36
    assert abs((ruler_y(ry, rh, CLEAR_CM) - ruler_y(ry, rh, d)) -
               (track_h * (d - CLEAR_CM) / RULER_MAX)) < 1e-6
    assert ruler_y(ry, rh, d) < ruler_y(ry, rh, CLEAR_CM), \
        "water line must sit above the clearance line"
    # C3: ETA and the +minute delta follow case-03's rule
    assert _eta(ROUTES[ROUTE_RECO][1]) == "08:32"
    assert ROUTES[ROUTE_RECO][1] - ROUTES[0][1] == 5
    assert ROUTES[ROUTE_RECO][2] and "P1" not in ROUTES[ROUTE_RECO][2], \
        "the recommended route must not contain the blocked point"
    # C5: the quiet strip stays below the alert band
    assert sy > by + bh, "secondary strip must not sit inside the banner"
    assert sy + sh + 38 <= H, "footer overflows the frame"
    assert cx + cw <= W - 32, "reroute card overflows the frame"
    return "".join(el)


def main(ver="v1"):
    body = build()
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "case-07-%s.snapshot" % ver)
    doc = ('<Snapshot type="png" background="%s">\n'
           '<SizedBox width="%d" height="%d">\n'
           '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n%s\n'
           '</Stack>\n</SizedBox>\n</Snapshot>\n' % (BG, W, H, body))
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    print("written", path, len(doc), "chars")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
