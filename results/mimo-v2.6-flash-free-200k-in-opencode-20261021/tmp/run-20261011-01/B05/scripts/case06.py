# -*- coding: utf-8 -*-
"""B05 case-06 · 锁屏与通知中心 (phone 780x1688).

Audience: anyone glancing at a locked phone during the rainstorm. Screen shows
the lock screen with three stacked notifications (water point / route / report)
and the route one expanded in place — the "expanded notification centre" state.

The meteorological warning band is the ONLY real-sourced content here: 暴雨预警
信号四级 and the 橙色 definition come from SRC-01 (中国气象局 standard). Every
depth, route, sensor reading and the clearance rule stay labelled 演示.
"""
import os
import sys
from b05_common import box, circle, text, tw
from b05_ui import (BG, BG2, CARD, STROKE, STROKE_HI, INK, SUB, MUTED, AQUA,
                    R_SAFE, R_CAUTION, R_DETOUR, R_BLOCK, F_BODY, F_NUM,
                    F_MONO, home_indicator)
from b05_data import (ALERTS, MOD_QUEUE, HERO, ROUTES, ROUTE_RECO, depth,
                      pname, prisk, ptime, ptrend, TREND_TXT, risk_color,
                      risk_label, CAR_CLEAR_MM, RISK_DEMO_NOTE)

W, H = 780, 1688
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "drafts"))

NOTIF_BG = "#12283B"
# meteorological warning palette — deliberately distinct from the product's
# depth-risk colours so a warning level is never read as a depth verdict
LV = [(4, "蓝", "#3B82F6", "12小时"), (3, "黄", "#EAB308", "6小时"),
      (2, "橙", "#F28C1A", "3小时"), (1, "红", "#EF4444", "3小时·100mm")]
WARN = "#F28C1A"
CURRENT = 2                      # 橙色 Ⅱ 级

CLEAR_CM = CAR_CLEAR_MM / 10.0   # 14.0cm, demo rule shared with case-01/07
CMP_ROWS = [("滨江路下穿隧道", depth("P1"), risk_color(depth("P1"))),
            ("解放路地道", depth("P4"), risk_color(depth("P4")))]


def depth_compare(x, y, w, h):
    """Cross-point depth compare with the vehicle-clearance marker."""
    el = []
    el.append(box(x, y, w, h, BG2, radius=16, border=STROKE, border_w=1))
    el.append(text(x + 20, y + 12, 320, 30, "深度对比 · 演示数据", 19, MUTED))
    bar_x, bar_w = x + 190, w - 190 - 104
    top = y + 58
    for i, (lab, d, col) in enumerate(CMP_ROWS):
        yy = top + i * 46
        el.append(text(x + 20, yy - 4, 164, 30, lab, 18, SUB))
        el.append(box(bar_x, yy, bar_w, 20, "#0C2740", radius=10))
        el.append(box(bar_x, yy, max(10, bar_w * d / 40.0), 20, col,
                      radius=10))
        el.append(text(bar_x + bar_w + 12, yy - 5, 84, 30, "%.0fcm" % d, 20,
                       col, bold=True, font=F_NUM))
    # vehicle clearance marker across both rows
    mx = bar_x + bar_w * (CLEAR_CM / 40.0)
    el.append(box(mx - 1.5, top - 16, 3, 46 * len(CMP_ROWS) + 8, INK))
    el.append(text(mx - 110, top + 46 * len(CMP_ROWS) + 4, 220, 26,
                   "车辆离地间隙 14cm", 17, MUTED, align="CENTER"))
    el.append(text(x + w - 220, y + 12, 200, 28,
                   "演示判定 · 非实测", 17, MUTED, align="RIGHT"))
    return "".join(el), y + h


def notif_compact(x, y, w, h, app, title, body, badge, bcol, action=None):
    el = [box(x, y, w, h, NOTIF_BG, radius=20, border=STROKE, border_w=1)]
    el.append(box(x + 20, y + 20, 46, 46, AQUA, radius=12))
    el.append(text(x + 20, y + 28, 46, 32, "水", 24, "#04222B", bold=True,
                   align="CENTER"))
    el.append(text(x + 78, y + 20, 300, 28, app, 19, MUTED))
    el.append(text(x + 78, y + 46, w - 200, 30, title, 23, INK, bold=True))
    el.append(text(x + 20, y + 88, w - 40, 32, body, 21, SUB))
    if badge:
        bw = int(tw(badge, 19)) + 28
        el.append(box(x + w - 20 - bw, y + 18, bw, 38, bcol + "26", radius=19,
                      border=bcol, border_w=1.5))
        el.append(text(x + w - 20 - bw, y + 25, bw, 28, badge, 19, bcol,
                       bold=True, align="CENTER"))
    if action:
        el.append(text(x + 20, y + h - 46, w - 40, 30, action + "  ›", 20,
                       bcol, bold=True))
    return "".join(el)


def build():
    el = []
    el.append(box(0, 0, W, H, BG))

    # ---- lock header: date + oversized time ----
    el.append(text(0, 96, W, 40, "10月21日 星期三", 26, MUTED, align="CENTER"))
    el.append(text(0, 146, W, 172, "08:15", 132, INK, bold=True,
                   align="CENTER", font=F_NUM))
    el.append(text(0, 322, W, 32, "暴雨橙色预警 · 云州市", 22, WARN,
                   bold=True, align="CENTER"))

    # ---- notification stack (priority 预警 > 禁止通行 > 路线 — plan C1) ----
    el.append(text(44, 380, 400, 32, "锁定屏幕通知", 20, MUTED))
    el.append(text(336, 382, W - 44 - 336, 28, "3 条 · 按紧急度排序", 19,
                   MUTED, align="RIGHT"))

    # ① real meteorological warning — highest priority, drawn before its own
    # content so the card body cannot paint over it
    n1y, n1h = 430, 250
    el.append(box(44, n1y, W - 88, n1h, NOTIF_BG, radius=20, border=WARN,
                  border_w=2))
    el.append(box(44, n1y, 10, n1h, WARN, radius=5))
    el.append(box(64, n1y + 20, 46, 46, WARN, radius=12))
    el.append(text(64, n1y + 26, 46, 36, "!", 30, "#04222B", bold=True,
                   align="CENTER"))
    el.append(text(122, n1y + 20, 340, 28, ALERTS[0][1], 19, MUTED))
    el.append(text(122, n1y + 46, 300, 32, ALERTS[0][0], 24, WARN, bold=True))
    # level badge
    bw = int(tw("Ⅱ级", 19)) + 30
    el.append(box(W - 44 - 24 - bw, n1y + 44, bw, 36, WARN + "26", radius=18,
                  border=WARN, border_w=1.5))
    el.append(text(W - 44 - 24 - bw, n1y + 51, bw, 26, "Ⅱ级", 19, WARN,
                   bold=True, align="CENTER"))
    el.append(text(64, n1y + 92, W - 128, 34, ALERTS[0][2], 23, INK, bold=True))
    # real four-level scale, current level highlighted
    sx, sw, gp = 64, 148, 14
    for i, (lvl, ch, col, _span) in enumerate(LV):
        cx = sx + i * (sw + gp)
        on = (lvl == CURRENT)
        el.append(box(cx, n1y + 136, sw, 40, col if on else "transparent",
                      radius=12, border=col, border_w=1.5))
        el.append(text(cx, n1y + 143, sw, 28,
                       "%s %s" % (ch, {4: "Ⅳ", 3: "Ⅲ", 2: "Ⅱ", 1: "Ⅰ"}[lvl]),
                       20, "#04222B" if on else col, bold=True, align="CENTER"))
    assert sx + 3 * (sw + gp) + sw <= W - 44 - 24, "level scale overflows"
    el.append(text(64, n1y + 192, W - 128, 30, "了解暴雨预警分级  ›", 20, WARN,
                   bold=True))

    # ② blocked water point — actionable reroute
    n2y, n2h = n1y + n1h + 16, 190
    p1 = HERO
    d1 = depth(p1)
    el.append(notif_compact(44, n2y, W - 88, n2h,
                            "水线 · 现在",
                            "%s %s" % (pname(p1), risk_label(d1)),
                            "水深 %.0fcm · %s · %s" % (
                                d1, TREND_TXT[ptrend(p1)], ptime(p1)),
                            risk_label(d1), risk_color(d1),
                            action=ALERTS[1][2]))

    # ③ route — expanded in place (the "notification centre" state)
    # depth_compare() returns its bottom edge; call it FIRST so the card can be
    # sized and painted before its own content (Stack paints later on top).
    n3y = n2y + n2h + 16
    dc_y = n3y + 136
    dc, dc_bottom = depth_compare(64, dc_y, W - 128, 206)
    ay = dc_bottom + 20
    n3h = (ay + 60) - n3y + 20
    el.append(box(44, n3y, W - 88, n3h, NOTIF_BG, radius=20, border=AQUA,
                  border_w=2))
    el.append(box(44, n3y, 10, n3h, AQUA, radius=5))
    el.append(box(64, n3y + 20, 46, 46, AQUA, radius=12))
    el.append(text(64, n3y + 28, 46, 32, "水", 24, "#04222B", bold=True,
                   align="CENTER"))
    el.append(text(122, n3y + 20, 300, 28, "水线 · 现在", 19, MUTED))
    # route duration lives in the header row — the action row is only buttons
    _rt = "%s · %d分" % (ROUTES[ROUTE_RECO][0], ROUTES[ROUTE_RECO][1])
    el.append(text(W - 44 - 260 - 24, n3y + 20, 240, 28, _rt, 19, AQUA,
                   align="RIGHT", font=F_MONO, bold=True))
    el.append(text(122, n3y + 46, W - 44 - 142, 32, ALERTS[2][0], 25, INK,
                   bold=True))
    el.append(text(64, n3y + 92, W - 128, 32, ALERTS[2][1], 21, SUB))
    el.append(dc)
    # actions
    el.append(box(64, ay, 300, 60, AQUA, radius=16))
    el.append(text(64, ay + 14, 300, 34, "查看路线", 22, "#04222B", bold=True,
                   align="CENTER"))
    el.append(box(380, ay, 220, 60, "transparent", radius=16, border=STROKE,
                  border_w=1.5))
    el.append(text(380, ay + 14, 220, 34, "稍后提醒", 22, SUB, bold=True,
                   align="CENTER"))
    assert 380 + 220 <= W - 44 - 24, "action buttons overflow the card"

    # ---- lock shortcuts + home indicator ----
    sy = 1400
    for cx, lab in ((140, "手电"), (W - 140, "相机")):
        el.append(circle(cx, sy + 48, 48, NOTIF_BG))
        el.append(text(cx - 60, sy + 34, 120, 30, lab, 20, INK, bold=True,
                       align="CENTER"))
    el.append(text(0, sy + 124, W, 28, RISK_DEMO_NOTE, 17, MUTED,
                   align="CENTER"))
    el.append(home_indicator(W, H - 26, dark=True))

    # ---- generation guards ----
    # the warning card carries the real standard, quoted verbatim from SRC-01
    assert ALERTS[0][3] == "real" and ALERTS[0][2].startswith("3小时")
    assert len(LV) == 4 and [lv[1] for lv in LV] == ["蓝", "黄", "橙", "红"]
    assert [lv[0] for lv in LV] == [4, 3, 2, 1], "levels must run Ⅳ→Ⅰ"
    # clearance marker must land left of the blocked point and right of the
    # passable one — that is the whole point of the comparison
    assert CLEAR_CM < depth("P1") and CLEAR_CM > depth("P4")
    # plan C1: notification priority 预警 > 禁止通行 > 路线, strictly stacked
    assert ALERTS[1][3] == "point" and ALERTS[2][3] == "route"
    assert n1y < n2y < n3y, "notifications are not in priority order"
    assert n2y + n2h <= n3y, "blocked-point card collides with route card"
    # plan C5: every card exposes an explainable action
    assert "›" in ALERTS[1][2] or ALERTS[1][2]
    assert ay + 60 + 20 <= n3y + n3h, "route actions overflow their card"
    assert sy >= n3y + n3h + 16, "lock shortcuts collide with route card"
    assert sy + 152 <= H - 26, "shortcut/footer collides with home bar"
    return "".join(el)


def main(ver="v1"):
    body = build()
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "case-06-%s.snapshot" % ver)
    doc = ('<Snapshot type="png" background="%s">\n'
           '<SizedBox width="%d" height="%d">\n'
           '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n%s\n'
           '</Stack>\n</SizedBox>\n</Snapshot>\n' % (BG, W, H, body))
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    print("written", path, len(doc), "chars")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
