# -*- coding: utf-8 -*-
"""B05 case-10 · 雨后个人周报 (personal weekly review, 780x1688).

Audience: 林岚 on a weekend sofa, not an operator. Everything on this screen
answers "what did I get out of using this", so the voice is first person and
the numbers are achievements (5 detours, 40 minutes saved) rather than city
state.

Two honesty notes that shaped the design:

1.  The screen is labelled 10月12日–10月18日, i.e. LAST week, not "本周". The
    run date is Wed 2026-10-21, and WEEK carries a full seven days including
    周四–周日. Claiming "this week" would mean reporting on days that have not
    happened. Asserted below: NOW_DATE must fall after the week it summarises.

2.  The rain bars have no "橙色预警阈值" line. That standard is 50mm in THREE
    HOURS; these are DAILY totals, so a shared threshold line would compare
    things that are not comparable. The peak day is highlighted instead.

Report provenance is derived, not typed: WEEK says 3 reports / 2 adopted, and
case-05 established that #1042 is 林岚's and is still 待复核. The only subset
of MOD_QUEUE consistent with both is {2 adopted} + {#1042}, so that is what is
shown — asserted, not assumed.
"""
import math
import os
import sys

from b05_common import box, circle, seg, text, tw_fit, tw_slot
from b05_data import (MOD_QUEUE, REPORT, WEEK, USER, risk_color,
                      NOW_DATE, NOW_DATE_CN)
from datetime import date
from b05_ui import (AQUA, BG, BG2, CARD, F_BODY, F_MONO, F_NUM, INK, MUTED,
                    R_CAUTION, R_SAFE, STROKE, STROKE_HI, SUB, status_bar,
                    tab_bar, home_indicator)

W, H = 780, 1688
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "drafts"))

# mobile chrome matches case-01: 44px gutters, tab bar anchored above the
# home indicator, "我的" is the personal tab.
MARGIN = 44
TAB_ITEMS = [("概", "水情"), ("图", "地图"), ("报", "上报"), ("铃", "提醒"),
             ("我", "我的")]
TAB_ACTIVE = 4

# the week this report summarises (the last COMPLETE week before NOW_DATE)
WEEK_START_CN = "10月12日"
WEEK_END_CN = "10月18日"
WEEK_END_ISO = "2026-10-18"
WEEK_START_ISO = "2026-10-12"  # the Monday before WEEK_END_ISO

# ---- chart geometry, exposed so the PNG can be pixel-verified afterwards ----
CHART_X = 68
CHART_W = 644
PLOT_Y = 580
PLOT_H = 200
PEAK_COLOR = "#F28C1A"      # the heaviest day, highlighted
DOT_COLOR = R_SAFE          # 避水 (a good thing) reads green, distinct from
                            # the blue rain bars and the orange peak


def wfit(s, size):
    return tw_fit(s, size)


def chart_geom():
    """bar rects for the rain series — the single source the renderer AND the
    pixel verifier both use, so they cannot drift apart."""
    max_mm = max(WEEK["rain_mm"])
    slot = CHART_W / 7.0
    bar_w = 56
    out = []
    for i, mm in enumerate(WEEK["rain_mm"]):
        h = mm / float(max_mm) * PLOT_H
        bx = CHART_X + i * slot + (slot - bar_w) / 2.0
        out.append({"i": i, "mm": mm, "day": WEEK["days"][i],
                    "avoided": WEEK["avoided"][i],
                    "x": bx, "w": bar_w, "y": PLOT_Y + PLOT_H - h, "h": h,
                    "cx": bx + bar_w / 2.0,
                    "color": PEAK_COLOR if mm == max_mm else AQUA})
    return out


def my_reports():
    """林岚's submissions, derived from MOD_QUEUE + the case-05 report."""
    # locate the MOD_QUEUE row that IS the case-05 submission (no id field on
    # REPORT, so match on the fields case-08 already proved identical)
    rep = [m for m in MOD_QUEUE
           if m[2] == REPORT["est_depth"] and m[4] == REPORT["submitted"]
           and m[3] == REPORT["status"]]
    assert len(rep) == 1, "case-05 report row not uniquely located"
    pending = rep[0]
    adopted = [m for m in MOD_QUEUE if m[3] == "已采纳"]
    # WEEK says 3 reports / 2 adopted. The only subset consistent with
    # "林岚 owns #1042 and it is not yet adopted" is adopted + {#1042}.
    assert len(adopted) == WEEK["adopted"], "adopted count disagrees with WEEK"
    assert len(adopted) + 1 == WEEK["reports"], "report count disagrees with WEEK"
    assert REPORT["reporter"] == USER
    return sorted(adopted + [pending], key=lambda m: m[4], reverse=True)


def build():
    el = []
    el.append(box(0, 0, W, H, BG))

    # ---- status bar ----
    sb, sbh = status_bar(W, dark=True)
    el.append(sb)

    # ================= header =================
    hy = 76
    el.append(text(MARGIN, hy, 420, 62, "雨后周报", 46, INK, bold=True))
    el.append(text(MARGIN, hy + 66, 520, 36,
                   "%s – %s · 上周复盘 · %s" % (WEEK_START_CN, WEEK_END_CN, USER),
                   20, MUTED, font=F_MONO))
    # share chip, opposite the title
    spw = 148
    el.append(box(W - MARGIN - spw, hy + 4, spw, 58, CARD, radius=29,
                  border=STROKE, border_w=1.5))
    el.append(text(W - MARGIN - spw, hy + 17, spw, 40, "分享周报", 22, AQUA,
                   align="CENTER", bold=True))

    # ================= hero: the two headline numbers =================
    hx, hy2, hw, hh = MARGIN, 192, W - 2 * MARGIN, 264
    el.append(box(hx, hy2, hw, hh, CARD, radius=24, border=STROKE_HI,
                  border_w=2))
    ix = hx + 24
    iw = hw - 48
    # top-left label: deliberately not "避水绕行", which is the caption for the
    # 5 sitting immediately below it
    el.append(text(ix, hy2 + 24, 380, 30, "上周战绩", 20, MUTED))
    sub = "%s – %s" % (WEEK_START_CN, WEEK_END_CN)
    el.append(text(ix + iw - 420, hy2 + 26, 420, 30, sub, 18, MUTED,
                   font=F_MONO, align="RIGHT"))

    # left: detours
    dv = str(WEEK["detours"])
    el.append(text(ix, hy2 + 60, tw_slot(dv, 88) + 12, 100, dv, 88, AQUA,
                   bold=True, font=F_NUM))
    el.append(text(ix + tw_slot(dv, 88) + 10, hy2 + 110, 90, 40, "次", 30, SUB))
    el.append(text(ix, hy2 + 166, 260, 34, "避水绕行", 22, MUTED))

    # divider
    el.append(box(390, hy2 + 56, 2, 140, STROKE))

    # right: minutes saved
    rv = str(WEEK["saved_min"])
    rx0 = 430
    el.append(text(rx0, hy2 + 60, tw_slot(rv, 88) + 12, 100, rv, 88, R_SAFE,
                   bold=True, font=F_NUM))
    el.append(text(rx0 + tw_slot(rv, 88) + 10, hy2 + 110, 140, 40, "分钟", 30,
                   SUB))
    el.append(text(rx0, hy2 + 166, 260, 34, "累计节省", 22, MUTED))

    # three supporting figures, laid out left to right with measured gaps
    facts = [("最长封控", "%d 分钟" % WEEK["longest_block_min"]),
             ("覆盖点位", "%d 点" % WEEK["points_covered"]),
             ("单周最大雨量", "%d 毫米" % max(WEEK["rain_mm"]))]
    fx = ix
    for k, (lab, val) in enumerate(facts):
        lw = wfit(lab, 18)
        vw = wfit(val, 18)
        assert lw + 6 + vw <= iw, "hero fact overflows: %s" % lab
        el.append(text(fx, hy2 + 214, lw + 6, 28, lab, 18, MUTED))
        el.append(text(fx + lw + 6, hy2 + 214, vw + 6, 28, val, 18, AQUA,
                       bold=True, font=F_NUM))
        fx += lw + 6 + vw
        if k < len(facts) - 1:
            sep_w = wfit(" · ", 18)
            el.append(text(fx, hy2 + 214, sep_w + 4, 28, "·", 18, MUTED))
            fx += sep_w + 4
    assert fx <= ix + iw + 4, "hero fact row overflows the card"

    # ================= chart: daily rain + detours =================
    cx, cy, cw, ch = MARGIN, 472, W - 2 * MARGIN, 418
    el.append(box(cx, cy, cw, ch, CARD, radius=24, border=STROKE, border_w=1.5))
    el.append(text(ix, cy + 24, 420, 40, "逐日雨量与避水", 28, INK, bold=True))
    el.append(text(ix + iw - 460, cy + 30, 460, 30,
                   "柱 = 雨量毫米 · 点 = 避水次数", 16, MUTED, align="RIGHT"))

    peak = max(WEEK["rain_mm"])
    peak_i = WEEK["rain_mm"].index(peak)
    for g in chart_geom():
        el.append(box(g["x"], g["y"], g["w"], max(g["h"], 2), g["color"],
                      radius=8))
        # value above the bar; slot is wide so it cannot collide
        el.append(text(g["cx"] - 46, g["y"] - 30, 92, 28, str(g["mm"]), 18,
                       g["color"], bold=True, font=F_NUM, align="CENTER"))
    el.append(box(CHART_X, PLOT_Y + PLOT_H, CHART_W, 2, STROKE_HI))
    # annotate the peak so it is not an unexplained colour change
    pg = chart_geom()[peak_i]
    el.append(text(pg["cx"] - 52, PLOT_Y + PLOT_H - pg["h"] - 62, 104, 26,
                   "上周峰值", 15, PEAK_COLOR, bold=True, align="CENTER"))

    # day labels + detour dots
    slot = CHART_W / 7.0
    for g in chart_geom():
        sx = CHART_X + g["i"] * slot
        el.append(text(sx, 790, slot, 30, g["day"], 18, MUTED,
                       align="CENTER"))
        n = g["avoided"]
        if n:
            total = n * 14 + (n - 1) * 8
            dx0 = sx + (slot - total) / 2.0
            for d in range(n):
                el.append(circle(dx0 + 7 + d * 22, 841, 7, DOT_COLOR))
        else:
            el.append(box(sx + slot / 2.0 - 12, 840, 24, 3, STROKE_HI,
                          radius=2))

    # ================= contribution =================
    qx, qy, qw, qh = MARGIN, 906, W - 2 * MARGIN, 430
    el.append(box(qx, qy, qw, qh, CARD, radius=24, border=STROKE, border_w=1.5))
    el.append(text(ix, qy + 24, 420, 40, "你的贡献", 28, INK, bold=True))
    el.append(text(ix + iw - 420, qy + 28, 420, 34,
                   "%d 上报 · %d 采纳" % (WEEK["reports"], WEEK["adopted"]), 20,
                   R_SAFE, align="RIGHT", bold=True))

    # three achievement tiles (the 3 / 2 / 6 the brief requires)
    tiles = [("上报", str(WEEK["reports"]), "次"),
             ("采纳", str(WEEK["adopted"]), "次"),
             ("覆盖", str(WEEK["points_covered"]), "点")]
    tw_ = (iw - 2 * 16) / 3.0
    for i, (lab, val, unit) in enumerate(tiles):
        tx = ix + i * (tw_ + 16)
        el.append(box(tx, qy + 74, tw_, 90, "#0B1E2E", radius=16,
                      border=STROKE, border_w=1.2))
        el.append(text(tx + 16, qy + 84, tw_ - 32, 26, lab, 16, MUTED))
        vw = tw_slot(val, 40)
        el.append(text(tx + 16, qy + 106, vw + 10, 56, val, 40, AQUA,
                       bold=True, font=F_NUM))
        el.append(text(tx + 16 + vw + 6, qy + 126, 60, 26, unit, 18, SUB))

    # the badge — medal drawn from primitives, tied back to case-05 / case-08
    el.append(box(ix, qy + 176, iw, 60, "#0B1E2E", radius=16, border=STROKE,
                  border_w=1.2))
    mcx, mcy, mr = ix + 30, qy + 206, 24
    el.append(circle(mcx, mcy, mr, "#3A2E12", border="#E8B54A", border_w=3))
    el.append(circle(mcx, mcy, mr - 7, "transparent", border="#E8B54A",
                     border_w=1.5))
    el.append(seg(mcx - 10, mcy, mcx - 3, mcy + 9, 5, "#E8B54A", radius=3))
    el.append(seg(mcx - 3, mcy + 9, mcx + 11, mcy - 9, 5, "#E8B54A", radius=3))
    el.append(text(ix + 70, qy + 180, 300, 30, "先锋上报徽章", 22, "#E8B54A",
                   bold=True))
    bsub = "%d 次采纳 · %d 次进入运维值守台复核队列（%s）" % (
        WEEK["adopted"], 1, my_reports()[0][0])
    assert wfit(bsub, 16) <= iw - 76, "badge caption overflows: %s" % bsub
    el.append(text(ix + 70, qy + 206, iw - 76, 26, bsub, 16, MUTED))

    # the three reports, most recent first — same status words/colours as the
    # ops queue in case-08 so the loop is visibly closed
    rows = my_reports()
    STATUS_STYLE = {"待复核": R_CAUTION, "已采纳": R_SAFE, "已驳回": MUTED}
    assert set(STATUS_STYLE) >= {m[3] for m in rows}, "unmapped report status"
    # identical mapping to case-08's ops queue, so the 待复核 pill means the
    # same thing on both ends of the loop; the orange risk colour must stay
    # reserved for the depth value itself
    assert STATUS_STYLE["待复核"] == R_CAUTION and STATUS_STYLE["已采纳"] == R_SAFE
    for i, (mid, mname, mdepth, mstatus, mtime, mconf) in enumerate(rows):
        ry = qy + 252 + i * 56
        el.append(box(ix, ry, iw, 48, "#0B1E2E", radius=12, border=STROKE,
                      border_w=1.2))
        el.append(text(ix + 16, ry + 13, 84, 26, mid, 18, SUB, bold=True,
                       font=F_MONO))
        assert wfit(mname, 20) <= 250, "report name overflows"
        el.append(text(ix + 104, ry + 12, 260, 30, mname, 20, INK, bold=True))
        dvv = str(int(mdepth)) if float(mdepth) == int(mdepth) else "%.1f" % mdepth
        dvw = tw_slot(dvv, 20)
        el.append(text(ix + 372, ry + 11, dvw + 8, 32, dvv, 20,
                       risk_color(mdepth), bold=True, font=F_NUM))
        el.append(text(ix + 372 + dvw + 3, ry + 20, 40, 24, "cm", 15, MUTED))
        col = STATUS_STYLE[mstatus]
        plab = mstatus
        pw = tw_slot(plab, 16) + 28
        el.append(box(ix + iw - 16 - pw, ry + 6, pw, 36, col + "26", radius=18,
                      border=col, border_w=1.2))
        el.append(text(ix + iw - 16 - pw, ry + 13, pw, 26, plab, 16, col,
                       bold=True, align="CENTER"))
        assert ix + iw - 16 - pw >= ix + 372 + dvw + 3 + 46, \
            "report row: status pill collides with depth"

    # ================= closing note =================
    ny = 1352
    el.append(box(MARGIN, ny, W - 2 * MARGIN, 116, CARD,
                  radius=20, border=STROKE, border_w=1.5))
    el.append(box(MARGIN, ny, 10, 116, AQUA, radius=5))
    el.append(text(MARGIN + 28, ny + 14, 300, 30, "复盘提示", 20, AQUA,
                   bold=True))
    el.append(text(MARGIN + 28, ny + 46, W - 2 * MARGIN - 56, 28,
                   "上周雨量峰值在%s（%d 毫米）" % (WEEK["days"][peak_i], peak),
                   18, SUB))
    el.append(text(MARGIN + 28, ny + 76, W - 2 * MARGIN - 56, 28,
                   "暴雨橙色预警时，锁屏会提前推送避水建议", 18, SUB))

    # ================= footer + chrome =================
    el.append(text(MARGIN, 1484, W - 2 * MARGIN, 48,
                   "演示数据 · 上周雨量/避水/上报为虚构演示值；风险分级为产品自定"
                   "规则，非官方标准", 15, MUTED))
    tb, tbh = tab_bar(W, H - 130, TAB_ITEMS, active_idx=TAB_ACTIVE, dark=True)
    el.append(tb)
    el.append(home_indicator(W, H - 26, dark=True))

    # ---------- generation guards ----------
    # C1: every headline number comes from WEEK
    assert WEEK["detours"] == 5 and WEEK["saved_min"] == 40
    assert WEEK["reports"] == 3 and WEEK["adopted"] == 2
    assert WEEK["points_covered"] == 6
    assert len(rows) == WEEK["reports"]
    assert sum(1 for m in rows if m[3] == "已采纳") == WEEK["adopted"]
    # the report shown as pending must be the case-05 one
    assert rows[0][0] == "#1042" and rows[0][1] == "站前广场地下通道"
    assert rows[0][2] == REPORT["est_depth"] and rows[0][3] == REPORT["status"]
    # avoided counts sum to the headline detour count
    assert sum(WEEK["avoided"]) == WEEK["detours"]
    # ---- date integrity: the labelled range must be a real Mon–Sun week that
    # actually ended before NOW_DATE, otherwise the chart would be reporting on
    # days that have not happened yet ----
    ws = date(*[int(p) for p in WEEK_START_ISO.split("-")])
    we = date(*[int(p) for p in WEEK_END_ISO.split("-")])
    assert ws.weekday() == 0, "report week must start on a Monday, got %s" % ws
    assert we.weekday() == 6, "report week must end on a Sunday, got %s" % we
    assert (we - ws).days == 6, "report week must span exactly 7 days"
    assert ws.strftime("%Y-%m-%d") == WEEK_START_ISO
    assert we.strftime("%Y-%m-%d") == WEEK_END_ISO
    assert WEEK_START_CN == "%d月%d日" % (ws.month, ws.day)
    assert WEEK_END_CN == "%d月%d日" % (we.month, we.day)
    assert NOW_DATE > WEEK_END_ISO, \
        "report week must be wholly in the past (%s vs %s)" % (NOW_DATE, WEEK_END_ISO)
    assert NOW_DATE_CN != WEEK_END_CN
    # the peak callout rides just above the tallest bar. It is a small centred
    # label, so it is only safe if it clears on at least one axis: either it
    # sits fully below the header row, or it is horizontally clear of both the
    # left-aligned chart title and the right-aligned legend.
    call_top = PLOT_Y + PLOT_H - max(b["h"] for b in chart_geom()) - 62
    call_bot = call_top + 26
    title_l, title_r = ix, ix + tw_fit("逐日雨量与避水", 28)
    # measure the callout's actual glyph width, not its 104px centred box
    call_half = tw_fit("上周峰值", 15) / 2.0
    call_l, call_r = pg["cx"] - call_half, pg["cx"] + call_half
    legend_l = ix + iw - tw_fit("柱 = 雨量毫米 · 点 = 避水次数", 16)
    header_bot = cy + 24 + 40
    clears_below = call_top >= header_bot
    clears_side = (call_r <= title_l) or (call_l >= title_r and call_r <= legend_l)
    assert clears_below or clears_side, (
        "peak callout collides with the chart header: box y %d-%d, title ends "
        "x %.0f, legend starts x %.0f" % (call_top, call_bot, title_r, legend_l))
    # the callout must also stay above the tallest bar's own value label
    assert call_bot <= PLOT_Y - 30, "peak callout collides with the bar value label"
    # C2: bar heights are exactly proportional to rain_mm
    g = chart_geom()
    max_mm = max(WEEK["rain_mm"])
    for bar in g:
        assert abs(bar["h"] - bar["mm"] / float(max_mm) * PLOT_H) < 1e-9
        assert abs(bar["y"] + bar["h"] - (PLOT_Y + PLOT_H)) < 1e-9, \
            "every bar must sit on the axis"
    for bar in g[1:]:
        r1 = g[0]["h"] / bar["h"]
        r2 = g[0]["mm"] / float(bar["mm"])
        assert abs(r1 - r2) < 1e-9, "bar ratio does not match rain ratio"
    # C5: nothing leaves the frame or its card
    assert hy2 + hh <= cy and cy + ch <= qy and qy + qh <= ny
    assert ny + 116 <= 1484 + 8 and 1484 + 48 <= H - 130
    assert MARGIN + (W - 2 * MARGIN) == W - MARGIN
    # the peak bar carries its own explanation, and only the peak is orange
    assert sum(1 for bar in g if bar["color"] == PEAK_COLOR) == 1
    return "".join(el)


def main(ver="v1"):
    body = build()
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "case-10-%s.snapshot" % ver)
    doc = ('<Snapshot type="png" background="%s">\n'
           '<SizedBox width="%d" height="%d">\n'
           '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n%s\n'
           '</Stack>\n</SizedBox>\n</Snapshot>\n' % (BG, W, H, body))
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    print("written", path, len(doc), "chars")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
