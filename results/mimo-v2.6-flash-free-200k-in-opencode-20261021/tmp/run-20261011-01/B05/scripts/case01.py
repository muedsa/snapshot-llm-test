# -*- coding: utf-8 -*-
"""B05 case-01 · 首页 · 城市水情总览 (phone 780x1688).

User goal: 出门前 30 秒判断全市积水与自身风险。Persona 通勤族·林岚.
Layout: status bar / header / orange warning banner (REAL CMA text) /
4 stat counts / water-point list (forbidden first) / bottom nav.
"""
import os
import sys
from b05_common import box, circle, text, esc, tw, r2
from b05_ui import (BG, BG2, CARD, STROKE, STROKE_HI, INK, SUB, MUTED, AQUA,
                    AQUA_HI, R_SAFE, R_CAUTION, R_DETOUR, R_BLOCK,
                    F_BODY, F_NUM, F_MONO, status_bar, tab_bar, home_indicator,
                    card, chip, risk_pill, mini_depth, button)
from b05_data import (POINTS, PMAP, risk_of, risk_color, prisk, depth, pname,
                      pdistrict, ptrend, ptime, TREND_TXT, TREND_ARROW,
                      n_blocked, n_detour, n_caution, n_open, RAIN_WARN,
                      CITY, NOW, NOW_DATE_CN, USER, RISK_DEMO_NOTE, HERO)

W, H = 780, 1688
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "drafts"))

TAB_ITEMS = [("概", "水情"), ("图", "地图"), ("报", "上报"), ("铃", "提醒"),
             ("我", "我的")]


def build():
    el = []
    # ---- background ----
    el.append(box(0, 0, W, H, BG))

    # ---- status bar ----
    sb, sbh = status_bar(W, dark=True)
    el.append(sb)

    # ---- header ----
    hy = 76
    el.append(text(44, hy, 400, 56, CITY + " · 水情", 40, INK, bold=True))
    el.append(text(44, hy + 58, 400, 34, "早高峰通勤 · " + NOW_DATE_CN + " " + NOW,
                   24, MUTED, font=F_MONO))
    # refresh pill
    pw = 150
    el.append(box(W - 44 - pw, hy + 6, pw, 56, CARD, radius=28,
                  border=STROKE, border_w=1.5))
    el.append(text(W - 44 - pw, hy + 18, pw, 40, "刚刚更新", 22, AQUA,
                   align="CENTER", bold=True))

    # ---- orange warning banner (REAL) ----
    by = 172
    bh = 190
    el.append(box(44, by, W - 88, bh, R_DETOUR + "1A", radius=24,
                  border=R_DETOUR, border_w=2))
    # left color spine
    el.append(box(44, by, 10, bh, R_DETOUR, radius=5))
    el.append(chip(72, by + 24, RAIN_WARN["grade"] + "预警", "#2A1600",
                   R_DETOUR, size=24, padx=18, h=44)[0])
    el.append(text(72 + 200, by + 28, 300, 40, "暴雨 · 实时生效", 24,
                   "#F6D8B0", bold=True))
    el.append(text(72, by + 80, W - 148, 74,
                   "3小时内降雨量将达50毫米以上，\n或已达50毫米以上且降雨可能持续",
                   23, INK, bold=True, line_h=1.30))
    el.append(text(72, by + 152, W - 148, 30,
                   "来源：" + RAIN_WARN["source"], 18, "#C9A87A"))

    # ---- stat row: 4 counts ----
    sy = by + bh + 22
    sh = 122
    counts = [("禁止通行", n_blocked(), R_BLOCK), ("建议绕行", n_detour(), R_DETOUR),
              ("谨慎", n_caution(), R_CAUTION), ("可通行", n_open(), R_SAFE)]
    gap = 16
    cw = (W - 88 - gap * 3) / 4.0
    for i, (lab, num, colr) in enumerate(counts):
        cx = 44 + i * (cw + gap)
        el.append(card(cx, sy, cw, sh, CARD))
        el.append(circle(cx + cw - 24, sy + 24, 6, colr))
        el.append(text(cx, sy + 16, cw, 56, str(num), 44, INK, bold=True,
                       align="CENTER", font=F_NUM))
        el.append(text(cx, sy + 78, cw, 34, lab, 21, SUB, align="CENTER"))
    el.append(text(44, sy + sh + 8, W - 88, 28,
                   "演示风险分级规则（产品自定，非官方标准）· 共 " +
                   str(len(POINTS)) + " 处监测点", 17, MUTED))

    # ---- section header ----
    ry = sy + sh + 44
    el.append(text(44, ry, 400, 44, "积水点", 30, INK, bold=True))
    el.append(text(W - 44 - 260, ry + 8, 260, 32, "按风险排序 · " + str(len(POINTS)) + " 处",
                   21, MUTED, align="RIGHT"))

    # ---- point list (forbidden first) ----
    ly = ry + 50
    row_h = 140
    gapv = 12
    # sort: risk level desc, then depth desc
    ordered = sorted(POINTS, key=lambda p: (-prisk(p[0])[1], -depth(p[0])))
    for idx, p in enumerate(ordered):
        pid = p[0]
        d = depth(pid)
        label, level, colr = prisk(pid)
        ry2 = ly + idx * (row_h + gapv)
        el.append(card(44, ry2, W - 88, row_h, CARD))
        # left color bar
        el.append(box(44, ry2, 8, row_h, colr, radius=4))
        # ---- left column: name / district / trend / sensor ----
        el.append(text(72, ry2 + 14, 340, 40, pname(pid), 26, INK, bold=True))
        el.append(text(72, ry2 + 50, 240, 30, pdistrict(pid), 19, MUTED))
        ta = TREND_ARROW[ptrend(pid)]
        tc = R_BLOCK if ptrend(pid) == "rising" else (
            R_SAFE if ptrend(pid) == "falling" else MUTED)
        el.append(text(72, ry2 + 78, 260, 30,
                       ta + " " + TREND_TXT[ptrend(pid)] + " · " + ptime(pid),
                       19, tc, bold=True))
        el.append(text(72, ry2 + 108, 300, 26, p[6] + " · 众包 " + str(p[7]) + " 条",
                       16, MUTED, font=F_MONO))
        # ---- right column: risk pill (top) / depth number / mini bar ----
        rp, pw2 = chip(0, ry2 + 12, label, colr, colr + "26", size=20,
                       padx=16, h=38)
        el.append(box(712 - pw2, ry2 + 12, pw2, 38, colr + "26", radius=19))
        el.append(text(712 - pw2, ry2 + 19, pw2, 30, label, 20, colr,
                       bold=True, align="CENTER"))
        el.append(text(360, ry2 + 52, 304, 50, "%.0f" % d, 38, INK, bold=True,
                       align="RIGHT", font=F_NUM))
        el.append(text(668, ry2 + 66, 52, 28, "cm", 19, SUB))
        el.append(mini_depth(430, ry2 + 108, 282, 11, d))

    # ---- bottom nav ----
    tb, tbh = tab_bar(W, H - 130, TAB_ITEMS, active_idx=0, dark=True)
    el.append(tb)
    el.append(home_indicator(W, H - 26, dark=True))
    # generation-time guard: last row must clear the tab bar
    _last_end = ly + len(ordered) * (row_h + gapv) - gapv
    assert _last_end <= H - 130, "list overflows tab bar: %d > %d" % (
        _last_end, H - 130)
    return "".join(el)


def main(ver="v1"):
    body = build()
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "case-01-%s.snapshot" % ver)
    doc = ('<Snapshot type="png" background="%s">\n'
           '<SizedBox width="%d" height="%d">\n'
           '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n%s\n'
           '</Stack>\n</SizedBox>\n</Snapshot>\n' % (BG, W, H, body))
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    print("written", path, len(doc), "chars")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
