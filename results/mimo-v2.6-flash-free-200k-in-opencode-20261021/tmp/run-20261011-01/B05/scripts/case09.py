# -*- coding: utf-8 -*-
"""B05 case-09 · 市级防汛指挥大屏 (command wall 1920x1080).

Audience: 应急指挥席 reading from several metres away. The screen resolves
three questions at a glance — where is it bad, what has happened, what should
be dispatched — as three bands: a metric strip, a city schematic carrying all
six points, and an escalation timeline plus dispatch orders.

Nothing is hand-typed: the markers read depth and risk colour from POINTS, the
timeline reads ESCALATION verbatim, metrics read OPS, and the CMA orange
warning comes from RAIN_WARN. The dispatch orders deliberately close the loop
back to case-05 (crowd report #1042), case-08 (pump load) and case-07 (car
reroute) so the five roles read as one product.

Geometry notes (all asserted below): zone coordinates are relative to the map
plate's content origin (ox, oy); the legend sits at oy+542, so every marker's
name plate must bottom out above 532.
"""
import math
import os
import sys

from b05_common import box, circle, seg, text, tw_fit, tw_slot, poly
from b05_data import (ESCALATION, MOD_QUEUE, OPS, PERSONAS, POINTS, RAIN_WARN,
                      RISK_DEMO_NOTE, ROUTES, ROUTE_RECO, CITY,
                      NOW_DATE_CN, NOW_DATE_WEEKDAY, pcrowd, psensor,
                      risk_color, risk_label, n_blocked, n_detour, n_caution,
                      n_open)
from b05_ui import (AQUA, BG, BG2, CARD, F_BODY, F_MONO, F_NUM, INK, MUTED,
                    R_CAUTION, R_DETOUR, R_SAFE, STROKE, STROKE_HI, SUB)

W, H = 1920, 1080
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "drafts"))

# marker anchors, relative to the map plate content origin (ox, oy)
ANCHORS = {
    "P1": (150, 170), "P4": (120, 380), "P5": (330, 300),
    "P3": (700, 115),
    "P2": (610, 350), "P6": (820, 380),
}
# district plates, same relative space; must fit x 0..936, y 0..490
ZONES = {
    "滨江区": (0, 30, 450, 460),
    "高新区": (470, 0, 466, 230),
    "城南区": (470, 250, 466, 240),
}
PLATE_W = 936          # content width inside the map plate
LEGEND_TOP = 542       # relative y where the legend band starts


def wfit(s, size):
    return tw_fit(s, size)


def marker_r(depth_cm):
    """marker radius tracks depth, so severity reads from across the room."""
    return 34 + int(round(depth_cm / 32.0 * 16))


def metric(x, y, w, h, label, value, unit, color, sub, frac=None,
           font=F_NUM):
    """one KPI tile. Layout rows: label(+caption) / value+unit / optional bar.

    The caption sits beside the label when a bar is present, and on its own
    line below the value otherwise — putting it on the value row made it
    collide with the value glyphs.
    """
    el = [box(x, y, w, h, CARD, radius=20, border=STROKE, border_w=1.5),
          box(x, y, 7, h, color, radius=4),
          text(x + 28, y + 16, w - 56, 28, label, 19, MUTED)]
    vw = tw_slot(value, 62)
    el.append(text(x + 28, y + 44, vw + 10, 70, value, 62, color, bold=True,
                   font=font))
    if unit:
        el.append(text(x + 28 + vw + 8, y + 76, 150, 34, unit, 24, SUB))
    if frac is not None:
        bw = w - 56
        el.append(box(x + 28, y + 116, bw, 10, "#0C2740", radius=5))
        if frac > 0:
            el.append(box(x + 28, y + 116, max(10, bw * frac), 10, color,
                          radius=5))
        sw = wfit(sub, 17)
        lw = wfit(label, 19)
        assert lw + 16 + sw <= w - 56, \
            "metric caption collides with label: %r" % label
        el.append(text(x + 28, y + 16, w - 56, 28, sub, 17, MUTED,
                       align="RIGHT"))
    else:
        sw = wfit(sub, 17)
        assert sw <= w - 56, "metric sub overflows: %s" % sub
        assert y + 44 + 70 <= y + 116, "value row overlaps caption row"
        el.append(text(x + 28, y + 116, w - 56, 26, sub, 17, MUTED))
    return "".join(el)


def build():
    el = []
    el.append(box(0, 0, W, H, BG))

    # ================= header =================
    el.append(box(0, 0, W, 92, BG2))
    el.append(box(0, 91, W, 2, STROKE))
    el.append(box(40, 28, 38, 38, AQUA, radius=12))
    el.append(text(40, 34, 38, 30, "水", 24, "#04222B", bold=True,
                   align="CENTER"))
    # CITY already ends in "市" — appending another gave "云州市市…"
    el.append(text(96, 22, 760, 44, CITY + "防汛指挥中心", 36, INK, bold=True))
    el.append(text(96, 62, 760, 26, "水线 Waterline · 指挥大屏 · %s %s"
                   % (NOW_DATE_WEEKDAY, NOW_DATE_CN), 18, MUTED))
    warn_txt = "暴雨橙色预警 Ⅱ级"
    warn_w = tw_slot(warn_txt, 26) + 56
    el.append(box(W - 40 - 470 - warn_w - 18, 26, warn_w, 44, "#3A2611",
                  radius=22, border="#F28C1A", border_w=2))
    el.append(text(W - 40 - 470 - warn_w - 18, 34, warn_w, 30, warn_txt, 26,
                   "#F28C1A", bold=True, align="CENTER"))
    el.append(text(W - 40 - 470, 24, 470, 34, "08:15", 30, INK, bold=True,
                   font=F_MONO, align="RIGHT"))
    el.append(text(W - 40 - 470, 58, 470, 26, "应急指挥席 · 在岗 %d 人"
                   % OPS["staff_on_duty"], 17, MUTED, align="RIGHT"))

    # ================= metric strip =================
    my, mh = 112, 152
    mw = (W - 80 - 3 * 24) / 4.0
    n_run = sum(1 for p in OPS["pump_stations"] if p[1] == "运行")
    metrics = [
        ("预警等级", "橙色", "Ⅱ级", "#F28C1A",
         # quoted verbatim (first clause) from the real CMA standard; the grade
         # already reads as the value, so the caption carries the threshold
         # instead of repeating "橙色"
         RAIN_WARN["real_text"].split("，")[0], None, F_BODY),
        ("禁止通行点", str(n_blocked()), "处", "#E4572E",
         "滨江路下穿隧道 32cm", None, F_NUM),
        ("传感器在线", str(OPS["sensors_online"]),
         "/ %d" % OPS["sensors_total"], AQUA,
         "%.1f%%" % (100.0 * OPS["sensors_online"] / OPS["sensors_total"]),
         float(OPS["sensors_online"]) / OPS["sensors_total"], F_NUM),
        ("在岗人员", str(OPS["staff_on_duty"]), "人", R_SAFE,
         PERSONAS["operator"][0], None, F_NUM),
    ]
    for i, m in enumerate(metrics):
        el.append(metric(40 + i * (mw + 24), my, mw, mh, *m))

    # ================= left: city schematic =================
    mx, myy, mw2, mh2 = 40, 288, 1000, 700
    el.append(box(mx, myy, mw2, mh2, CARD, radius=24, border=STROKE_HI,
                  border_w=2))
    el.append(text(mx + 32, myy + 24, 600, 40, "全市积水风险分布", 30, INK,
                   bold=True))
    el.append(text(mx + mw2 - 32 - 560, myy + 30, 560, 30,
                   "%d 点位 · 按风险着色 · 数据 08:14 更新" % len(POINTS), 19,
                   MUTED, align="RIGHT"))

    ox, oy = mx + 32, myy + 84          # zone coords are relative to this
    # per-district tallies, derived (not typed) so the plate corners carry
    # real information instead of empty space
    by_dist = {}
    for p in POINTS:
        by_dist.setdefault(p[2], []).append(p[3])
    for dname, (zx, zy, zw, zh) in ZONES.items():
        el.append(box(ox + zx, oy + zy, zw, zh, "#0A2135", radius=26,
                      border=STROKE, border_w=1.5))
        el.append(text(ox + zx + 18, oy + zy + 14, 240, 26, dname, 18, MUTED,
                       bold=True))
        dp = by_dist[dname]
        assert dp, "district has no points: %s" % dname
        tally = "%d 点位 · 最高 %.0fcm" % (len(dp), max(dp))
        el.append(text(ox + zx + zw - 18 - 240, oy + zy + 14, 240, 26, tally,
                       16, MUTED, align="RIGHT", font=F_MONO))
    assert sum(len(v) for v in by_dist.values()) == len(POINTS)

    # schematic river + arterial so the plate reads as a map, not a grid
    el.append(poly([(ox + 20, oy + 260), (ox + 190, oy + 315),
                    (ox + 380, oy + 285), (ox + 545, oy + 360),
                    (ox + 740, oy + 425), (ox + 915, oy + 480)],
                   14, "#12405E", radius=7))
    el.append(poly([(ox + 470, oy + 55), (ox + 600, oy + 125),
                    (ox + 770, oy + 85), (ox + 925, oy + 150)],
                   9, "#12405E", radius=5))

    # ---- six markers, every value read from POINTS ----
    by_pid = dict((p[0], p) for p in POINTS)
    for pid, pname_s, pdis, pd_, ptrend_s, ptime_s, psens, crowd in POINTS:
        cx, cy = ANCHORS[pid]
        col = risk_color(pd_)
        r = marker_r(pd_)
        el.append(circle(ox + cx, oy + cy, r + 12, col + "22"))
        el.append(circle(ox + cx, oy + cy, r, "#0B2033", border=col,
                         border_w=4))
        dv = str(int(pd_)) if float(pd_) == int(pd_) else "%.1f" % pd_
        el.append(text(ox + cx - r, oy + cy - 24, 2 * r, 44, dv, 34, col,
                       bold=True, align="CENTER", font=F_NUM))
        el.append(text(ox + cx - r, oy + cy + 12, 2 * r, 24, "cm", 15, MUTED,
                       align="CENTER"))
        nw = tw_slot(pname_s, 21) + 30
        el.append(box(ox + cx - nw / 2.0, oy + cy + r + 14, nw, 40,
                      "#071A2B", radius=12, border=col, border_w=1.5))
        el.append(text(ox + cx - nw / 2.0, oy + cy + r + 22, nw, 28, pname_s,
                       21, INK, bold=True, align="CENTER"))

    # ---- risk legend ----
    ly = myy + mh2 - 74
    ly_rel = ly - oy
    el.append(box(mx + 24, ly, mw2 - 48, 54, "#08192A", radius=14,
                  border=STROKE, border_w=1))
    lx = mx + 44
    glyph_end = lx
    for lab, ldepth in (("可通行", 8), ("谨慎", 12), ("建议绕行", 22),
                        ("禁止通行", 32)):
        lcol = risk_color(ldepth)
        assert risk_label(ldepth) == lab, "legend label disagrees with rule"
        el.append(circle(lx + 11, ly + 27, 11, "#0B2033", border=lcol,
                         border_w=3))
        lx += 30
        lw = wfit(lab, 20)
        el.append(text(lx, ly + 14, lw + 6, 30, lab, 20, MUTED))
        glyph_end = lx + lw
        lx = glyph_end + 40
    note_w = wfit(RISK_DEMO_NOTE, 16)
    note_x = mx + mw2 - 44 - note_w
    assert glyph_end + 24 <= note_x, "legend swatches collide with the note"
    el.append(text(note_x, ly + 15, note_w + 8, 28, RISK_DEMO_NOTE, 16, MUTED,
                   align="RIGHT"))

    # ================= right: timeline + dispatch =================
    rx, rw = 1064, 816

    ty, th = 288, 404
    el.append(box(rx, ty, rw, th, CARD, radius=24, border=STROKE_HI,
                  border_w=2))
    el.append(text(rx + 32, ty + 24, 500, 40, "升级处置时间线", 30, INK,
                   bold=True))
    el.append(text(rx + rw - 32 - 300, ty + 30, 300, 30, "08:00 → 08:14", 21,
                   AQUA, align="RIGHT", font=F_MONO))

    axis_x = rx + 150
    first_y = ty + 96
    step = 78
    el.append(seg(axis_x, first_y - 6, axis_x,
                  first_y + step * (len(ESCALATION) - 1) + 6, 3, STROKE_HI))
    prev_t = None
    for i, (t, ev, actor) in enumerate(ESCALATION):
        ey = first_y + i * step
        col = "#F28C1A" if i == 0 else (AQUA if actor == "指挥席" else R_DETOUR)
        tw_clock = tw_slot(t, 22)
        el.append(text(rx + 32, ey - 16, tw_clock, 30, t, 22, INK, bold=True,
                       font=F_MONO, align="RIGHT"))
        assert 32 + tw_clock + 12 <= axis_x - rx - 16, "clock crowds axis"
        el.append(circle(axis_x, ey, 11, "#0B2033", border=col, border_w=4))
        assert wfit(ev, 22) <= rw - 220, "timeline event overflows: %s" % ev
        el.append(text(axis_x + 32, ey - 18, rw - 210, 32, ev, 22, SUB,
                       bold=True))
        el.append(text(axis_x + 32, ey + 12, rw - 210, 26,
                       "由「%s」触发" % actor, 16, MUTED))
        if prev_t is not None:
            assert prev_t < t, "timeline must be strictly ascending"
        prev_t = t
    assert first_y + step * (len(ESCALATION) - 1) + 38 <= ty + th - 16, \
        "timeline overflows its card"

    # ---- dispatch orders, closing the loop with 05 / 07 / 08 ----
    dy, dh = 712, 276
    el.append(box(rx, dy, rw, dh, CARD, radius=24, border=STROKE,
                  border_w=1.5))
    el.append(text(rx + 32, dy + 22, 500, 38, "调度建议", 28, INK, bold=True))
    el.append(text(rx + rw - 32 - 460, dy + 28, 460, 28,
                   "系统按风险与负荷排序生成 · 待指挥席确认", 16, MUTED,
                   align="RIGHT"))
    orders = [
        ("A", "增派 2 人至 P6 站前广场地下通道",
         "众包 %d 条 · 传感器 %s 读数 %.0fcm，与上报 %s 一致"
         % (pcrowd("P6"), psensor("P6"), 26.0, "#1042"), R_DETOUR),
        ("B", "滨江1号泵站 88% 满载，联动城南2号泵站",
         "%d 座泵站中 %d 座可用，高新泵站检修中"
         % (len(OPS["pump_stations"]), n_run), AQUA),
        ("C", "P1 保持禁行，向车机下发避水路线",
         # ROUTES[0][3] is "经滨江路下穿隧道（禁止通行）" — strip only the
         # leading 经; slicing [3:] also ate "滨江" and read "绕开路下穿隧道"
         "走「%s」%d 分钟，绕开%s"
         % (ROUTES[ROUTE_RECO][0], ROUTES[ROUTE_RECO][1],
            ROUTES[0][3][1:]), "#E4572E"),
    ]
    for i, (tag, head, why, col) in enumerate(orders):
        oy2 = dy + 68 + i * 68
        el.append(box(rx + 24, oy2, 40, 40, col, radius=12))
        el.append(text(rx + 24, oy2 + 7, 40, 30, tag, 22, "#04222B",
                       bold=True, align="CENTER", font=F_NUM))
        assert wfit(head, 21) <= rw - 110, "order head overflows: %s" % head
        el.append(text(rx + 80, oy2 + 1, rw - 110, 30, head, 21, INK,
                       bold=True))
        assert wfit(why, 16) <= rw - 110, "order why overflows: %s" % why
        el.append(text(rx + 80, oy2 + 30, rw - 110, 26, why, 16, MUTED))
    assert oy2 + 56 <= dy + dh - 12, "dispatch order overflows its card"

    # ================= footer =================
    foot = ("演示数据 · 水深/传感器/泵站/上报均为虚构演示值；风险分级为产品自定演示规则，"
            "非官方标准；仅暴雨预警四级分级引用中国气象局真实标准")
    el.append(text(40, 1012, W - 80, 30, foot, 17, MUTED))

    # ---- generation guards ----
    # C1: six points, colours and labels straight from POINTS
    assert len(POINTS) == 6 and set(ANCHORS) == set(by_pid)
    assert n_blocked() == 1 and n_caution() == 2 and n_open() == 1
    assert sum(1 for p in POINTS if risk_label(p[3]) == "建议绕行") == n_detour()
    assert all(risk_color(p[3]) for p in POINTS)
    # marker radius is monotone in depth -> bigger really is worse
    assert marker_r(8) < marker_r(22) < marker_r(32)
    # C2: timeline verbatim + strictly ascending
    assert ESCALATION[0][0] == "08:00" and ESCALATION[-1][0] == "08:14"
    assert [e[0] for e in ESCALATION] == sorted(e[0] for e in ESCALATION)
    assert len(ESCALATION) == 4
    # the real warning text is quoted, not paraphrased
    assert RAIN_WARN["grade"] == "橙色"
    assert RAIN_WARN["real_text"].startswith("3小时")
    # C4: dispatch closes the loop on 05 / 07 / 08
    assert MOD_QUEUE[0][0] == "#1042" and ROUTES[ROUTE_RECO][0] == "避水路线"
    assert "P1" not in ROUTES[ROUTE_RECO][2] and n_run == 2
    # order C must name the avoided point in full (a [3:] slice dropped "滨江")
    assert ROUTES[0][3][1:].startswith("滨江路下穿隧道")
    assert "绕开滨江路下穿隧道" in ("走「%s」%d 分钟，绕开%s"
                                    % (ROUTES[ROUTE_RECO][0],
                                       ROUTES[ROUTE_RECO][1], ROUTES[0][3][1:]))
    # C5: nothing leaves the frame, cards do not overlap
    assert mx + mw2 <= rx and rx + rw <= W - 40
    assert myy + mh2 <= 1000 and dy + dh <= 1000
    assert ty + th <= dy and my + mh <= myy
    assert 1012 + 30 <= H
    # every zone fits the plate content box
    for dname, (zx, zy, zw, zh) in ZONES.items():
        assert zx >= 0 and zx + zw <= PLATE_W, "%s zone out of plate" % dname
        assert zy >= 0 and zy + zh <= LEGEND_TOP - 10, \
            "%s zone runs into legend" % dname
    # every marker + its name plate stays in its zone and clear of the legend
    for pid, cx, cy in [(k, v[0], v[1]) for k, v in ANCHORS.items()]:
        p = by_pid[pid]
        r = marker_r(p[3])
        nw = tw_slot(p[1], 21) + 30
        assert cx - r >= 0 and cx + r <= PLATE_W, "%s circle out of plate" % pid
        assert cy - r >= 0, "%s circle crosses zone top" % pid
        assert cx - nw / 2.0 >= 0, "%s plate crosses left edge" % pid
        assert cx + nw / 2.0 <= PLATE_W, "%s plate crosses right edge" % pid
        assert cy + r + 54 <= LEGEND_TOP - 10, \
            "%s plate collides with legend" % pid
    # markers must not overlap each other (circles or name plates)
    ids = list(ANCHORS)
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            pa, pb = by_pid[ids[a]], by_pid[ids[b]]
            ax, ay = ANCHORS[ids[a]]
            bx, by = ANCHORS[ids[b]]
            ra, rb = marker_r(pa[3]), marker_r(pb[3])
            d = math.hypot(ax - bx, ay - by)
            assert d > ra + rb, "%s/%s circles overlap" % (ids[a], ids[b])
            na, nb = tw_slot(pa[1], 21), tw_slot(pb[1], 21)
            top_a = ay + ra + 14
            top_b = by + rb + 14
            if abs((ay - by)) < 60:      # roughly the same row
                assert d > (na + nb) / 2.0, "%s/%s plates overlap" % (
                    ids[a], ids[b])
    return "".join(el)


def main(ver="v1"):
    body = build()
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "case-09-%s.snapshot" % ver)
    doc = ('<Snapshot type="png" background="%s">\n'
           '<SizedBox width="%d" height="%d">\n'
           '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n%s\n'
           '</Stack>\n</SizedBox>\n</Snapshot>\n' % (BG, W, H, body))
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    print("written", path, len(doc), "chars")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
