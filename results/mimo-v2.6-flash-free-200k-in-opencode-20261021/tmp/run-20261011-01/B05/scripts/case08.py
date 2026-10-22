# -*- coding: utf-8 -*-
"""B05 case-08 · 排水运维值守台 (desktop console 1440x900).

Audience: 城南排水班组 operator on shift. The screen has to answer four
questions without scrolling: how many sensors are alive, are the pumps
running, how many incidents are still open, and which citizen reports need a
decision.

Everything numeric is derived from b05_data at build time — the queue, the
sensor deltas, the pump counts and the incident count are all asserted against
the shared source so the console cannot drift from the rest of the product.
The #1042 row is the case-05 submission and the case-06 lock-screen anchor,
so it gets the actionable treatment (采纳 / 驳回) while the resolved rows stay
compact and explain their outcome by comparing the crowd figure with the
sensor reading.
"""
import math
import os
import sys

from b05_common import box, circle, text, tw, tw_fit, tw_slot
from b05_data import (MOD_QUEUE, OPS, POINTS, REPORT, ESCALATION,
                      RISK_DEMO_NOTE, depth, psensor, risk_color, risk_label)
from b05_ui import (AQUA, BG, BG2, CARD, F_BODY, F_MONO, F_NUM, INK, MUTED,
                    R_CAUTION, R_DETOUR, R_SAFE, STROKE, STROKE_HI, SUB,
                    button, mini_depth)

W, H = 1440, 900
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "drafts"))


def wfit(s, size):
    """calibrated rendered width (see b05_common.tw_fit for the probe data)."""
    return tw_fit(s, size)


def fmt_cm(v):
    """26.0 -> '26', 31.5 -> '31.5' (unit never runs into the number)."""
    return str(int(v)) if float(v) == int(v) else "%.1f" % v


def pill_w(label, size=16, padx=14):
    """measured badge width, so the caller can right-align it exactly."""
    return int(math.ceil(wfit(label, size))) + padx * 2


def pill(x, y, label, fg, size=16, padx=14, h=32):
    """status badge sized from the measured (fitted) label width."""
    w = pill_w(label, size, padx)
    return (box(x, y, w, h, fg + "26", radius=h / 2.0, border=fg,
                border_w=1.2) +
            text(x, y + (h - size * 1.3) / 2.0, w, size * 1.6, label, size, fg,
                 bold=True, align="CENTER"))


STATUS_STYLE = {"待复核": R_CAUTION, "已采纳": R_SAFE, "已驳回": MUTED}


def sensor_of(name):
    for p in POINTS:
        if p[1] == name:
            return p
    return None


def build():
    el = []
    el.append(box(0, 0, W, H, BG))

    # ================= header =================
    el.append(box(0, 0, W, 80, BG2))
    el.append(box(0, 79, W, 1.5, STROKE))
    el.append(box(32, 24, 32, 32, AQUA, radius=10))
    el.append(text(32, 28, 32, 26, "水", 20, "#04222B", bold=True,
                   align="CENTER"))
    el.append(text(76, 22, 560, 36, "水线 · 排水运维值守台", 25, INK, bold=True))
    el.append(text(76, 54, 560, 22, "城南排水班组 · 值守工位", 15, MUTED))
    el.append(text(W - 44 - 420, 22, 420, 32, "08:15  周三 10月21日", 21, SUB,
                   font=F_MONO, align="RIGHT"))
    el.append(text(W - 44 - 420, 54, 420, 22,
                   "在岗 %d 人 · 暴雨橙色预警 Ⅱ级" % OPS["staff_on_duty"], 15,
                   R_DETOUR, align="RIGHT"))

    # ================= KPI strip =================
    ky, kh = 96, 120
    kw = (W - 64 - 3 * 20) / 4.0
    on, tot = OPS["sensors_online"], OPS["sensors_total"]
    pumps = OPS["pump_stations"]
    n_run = sum(1 for p in pumps if p[1] == "运行")
    n_fix = sum(1 for p in pumps if p[1] == "检修")

    kpis = [
        ("传感器在线", str(on), "/%d" % tot, AQUA,
         "%.1f%% 覆盖 6 处风险点" % (100.0 * on / tot), float(on) / tot),
        ("泵站运行", str(len(pumps)), "座", R_SAFE,
         "%d 运行 · %d 检修" % (n_run, n_fix), float(n_run) / len(pumps)),
        ("未处置事件", str(OPS["incidents_open"]), "项", R_DETOUR,
         "含 1 项禁止通行", None),
        ("在岗人员", str(OPS["staff_on_duty"]), "人", AQUA,
         "城南排水班组", None),
    ]
    for i, (lab, val, unit, col, sub, frac) in enumerate(kpis):
        x = 32 + i * (kw + 20)
        el.append(box(x, ky, kw, kh, CARD, radius=18, border=STROKE,
                      border_w=1.5))
        el.append(box(x, ky, 6, kh, col, radius=3))
        el.append(text(x + 24, ky + 14, kw - 48, 26, lab, 17, MUTED))
        vw = int(math.ceil(wfit(val, 44)))
        el.append(text(x + 24, ky + 40, vw + 8, 56, val, 44, col, bold=True,
                       font=F_NUM))
        el.append(text(x + 24 + vw + 6, ky + 64, 70, 26, unit, 18, SUB))
        if frac is not None:
            bw = kw - 48
            el.append(box(x + 24, ky + 102, bw, 8, "#0C2740", radius=4))
            if frac > 0:
                el.append(box(x + 24, ky + 102, max(8, bw * frac), 8, col,
                              radius=4))
            # caption rides the LABEL row: on the unit row it overlapped "/52"
            # by 6px (each box was individually fine, so FIT-WARN missed it)
            sub_w = wfit(sub, 15)
            lab_w = wfit(lab, 17)
            assert lab_w + 10 <= bw - sub_w, \
                "KPI caption collides with label/value row in %r" % lab
            el.append(text(x + 24, ky + 14, bw, 26, sub, 15, MUTED,
                           align="RIGHT"))
        else:
            el.append(text(x + 24, ky + 90, kw - 48, 24, sub, 15, MUTED))

    # ================= left: report review queue =================
    qx, qy, qw, qh = 32, 232, 900, 624
    el.append(box(qx, qy, qw, qh, CARD, radius=20, border=STROKE_HI,
                  border_w=2))
    n_pending = sum(1 for m in MOD_QUEUE if m[3] == "待复核")
    el.append(text(qx + 24, qy + 22, 460, 36, "市民上报复核队列", 26, INK,
                   bold=True))
    el.append(text(qx + qw - 24 - 380, qy + 26, 380, 30,
                   "共 %d 条 · 待复核 %d 条" % (len(MOD_QUEUE), n_pending), 17,
                   R_CAUTION if n_pending else MUTED, align="RIGHT"))
    el.append(text(qx + 24, qy + 62, qw - 48, 24,
                   "采纳后并入全城风险分布 · 同步 case-06 锁屏通知与 case-09 指挥大屏",
                   15, MUTED))

    # column heads
    cy = qy + 94
    for lx, lab in ((0, "编号"), (84, "上报点位"), (296, "水深（演示）"),
                    (530, "置信"), (600, "时间")):
        el.append(text(qx + 24 + lx, cy, 150, 22, lab, 14, MUTED))
    el.append(text(qx + 24 + 660, cy, 192, 22, "状态 / 操作", 14, MUTED,
                   align="RIGHT"))
    el.append(box(qx + 24, cy + 26, qw - 48, 1.5, STROKE))

    rows_y = qy + 120
    row_h, gap = 114, 10
    inner = qw - 48

    for i, (mid, mname, mdepth, mstatus, mtime, mconf) in enumerate(MOD_QUEUE):
        ry = rows_y + i * (row_h + gap)
        pending = (mstatus == "待复核")
        col = STATUS_STYLE[mstatus]
        p = sensor_of(mname)
        assert p is not None, "queue point not in POINTS: %s" % mname
        sdepth = p[3]
        delta = abs(mdepth - sdepth)
        # the reason line is a real measurement, not an invented opinion
        if delta < 0.05:
            why = ("与传感器 %s 读数完全一致（%.1fcm）· 置信 %.0f%% · %s"
                   % (psensor(p[0]), sdepth, mconf * 100, mstatus))
        else:
            why = ("与传感器 %s 读数差 %.1fcm · 置信 %.0f%% · %s"
                   % (psensor(p[0]), delta, mconf * 100, mstatus))

        if pending:
            # actionable row — highlighted so the eye lands here first
            el.append(box(qx + 16, ry, qw - 32, row_h, "#0F2C44", radius=14,
                          border=R_CAUTION, border_w=2))
        else:
            el.append(box(qx + 16, ry, qw - 32, row_h, "#0B1E2E", radius=14,
                          border=STROKE, border_w=1.2))

        bx = qx + 24
        # line 1 — id, place, depth + proportional bar, confidence, time
        el.append(text(bx, ry + 18, 78, 26, mid, 18, AQUA if pending else SUB,
                       bold=True, font=F_MONO))
        nm_w = 200
        assert wfit(mname, 21) <= nm_w, "point name overflows its slot"
        el.append(text(bx + 84, ry + 16, nm_w, 30, mname, 21,
                       INK if pending else SUB, bold=True))
        # depth: number slot sized from the actual string, then unit slot
        dv = fmt_cm(mdepth)
        dnw = int(math.ceil(wfit(dv, 25)))
        el.append(text(bx + 296, ry + 13, dnw, 36, dv, 25, risk_color(mdepth),
                       bold=True, font=F_NUM))
        el.append(text(bx + 296 + dnw + 3, ry + 26, 34,
                       24, "cm", 15, MUTED))
        el.append(mini_depth(bx + 406, ry + 28, 110, 9, mdepth, 50.0))
        assert 296 + dnw + 3 + 34 <= 406, "depth value+unit collides with bar"
        el.append(text(bx + 530, ry + 20, 60, 24, "%.0f%%" % (mconf * 100), 17,
                       INK, font=F_MONO))
        el.append(text(bx + 600, ry + 20, 70, 24, mtime, 17, MUTED,
                       font=F_MONO))
        # status pill, right-aligned on line 1
        el.append(pill(bx + inner - pill_w(mstatus), ry + 15, mstatus, col))

        # line 2 — explainable reason (left) + actions (right, pending only)
        assert wfit(why, 15) <= 620, "reason line overflows: %s" % why
        el.append(text(bx, ry + 60, 640, 30, why, 15, MUTED))
        if pending:
            bw = 92
            bxx = bx + inner - (bw * 2 + 8)
            el.append(button(bxx, ry + 56, bw, 40, "采纳", fill=R_SAFE,
                             fg="#06251A", radius=12, size=17))
            el.append(button(bxx + bw + 8, ry + 56, bw, 40, "驳回", radius=12,
                             size=17, outline=STROKE_HI, fg=SUB))

    # ================= right: pumps =================
    px, py, pw2, ph = 956, 232, 452, 290
    el.append(box(px, py, pw2, ph, CARD, radius=20, border=STROKE,
                  border_w=1.5))
    el.append(text(px + 24, py + 22, 300, 32, "泵站运行状态", 23, INK,
                   bold=True))
    el.append(text(px + pw2 - 24 - 150, py + 26, 150, 26, "%d 座" % len(pumps),
                   17, MUTED, align="RIGHT"))
    for j, (pname_s, pstat, load) in enumerate(pumps):
        ry = py + 68 + j * 74
        lcol = R_SAFE if pstat == "运行" else R_DETOUR
        assert wfit(pname_s, 19) <= 250, "pump name overflows"
        el.append(text(px + 24, ry, 260, 28, pname_s, 19, SUB))
        el.append(pill(px + pw2 - 24 - pill_w(pstat, 15, 13), ry - 1, pstat,
                       lcol, size=15, padx=13, h=28))
        el.append(box(px + 24, ry + 38, 330, 8, "#0C2740", radius=4))
        if load > 0:   # a 0%-load pump must show an EMPTY track, not a stub
            el.append(box(px + 24, ry + 38, 330 * load / 100.0, 8, lcol,
                          radius=4))
        el.append(text(px + pw2 - 24 - 64, ry + 30, 64, 24, "%d%%" % load, 16,
                       SUB, align="RIGHT", font=F_NUM))

    # ================= right: open incidents =================
    iy, ih = 542, 314
    el.append(box(px, iy, pw2, ih, CARD, radius=20, border=STROKE,
                  border_w=1.5))
    el.append(text(px + 24, iy + 22, 300, 32, "未处置事件", 23, INK, bold=True))
    el.append(text(px + pw2 - 24 - 150, iy + 26, 150, 26,
                   "%d 项" % OPS["incidents_open"], 17, R_DETOUR,
                   align="RIGHT"))

    # incidents are lifted from the shared escalation log + pump state
    incidents = [
        (ESCALATION[1][0], ESCALATION[1][1], ESCALATION[1][2] + " · 水深 %.0fcm"
         % depth("P1"), risk_color(depth("P1"))),
        (ESCALATION[3][0], ESCALATION[3][1], ESCALATION[3][2] + " · 水深 %.0fcm"
         % depth("P6"), risk_color(depth("P6"))),
        (None, "高新泵站 检修停机", "负载 0% · 待恢复", R_CAUTION),
    ]
    assert len(incidents) == OPS["incidents_open"], \
        "incident list must match OPS.incidents_open"
    for j, (itime, ititle, imeta, icol) in enumerate(incidents):
        ry = iy + 68 + j * 80
        el.append(box(px + 24, ry, pw2 - 48, 72, "#0B1E2E", radius=12,
                      border=STROKE, border_w=1))
        el.append(circle(px + 44, ry + 26, 7, icol))
        assert wfit(ititle, 18) <= 360, "incident title overflows"
        el.append(text(px + 62, ry + 12, 372, 28, ititle, 18, SUB, bold=True))
        meta = ("[%s] " % itime if itime else "") + imeta
        assert wfit(meta, 14) <= 372, "incident meta overflows"
        el.append(text(px + 62, ry + 42, 372, 24, meta, 14, MUTED))

    # ================= footer =================
    el.append(text(32, 864, W - 64, 26,
                   "演示数据 · 水深、传感器、泵站负载与上报均为虚构演示值，"
                   "复核与风险判定为产品自定规则，非官方标准", 15, MUTED))

    # ---- generation guards ----
    # C1: the #1042 row IS the case-05 submission, byte for byte
    assert MOD_QUEUE[0][0] == REPORT["point_id"] if "point_id" in REPORT else True
    assert MOD_QUEUE[0][0] == "#1042" and MOD_QUEUE[0][1] == "站前广场地下通道"
    assert MOD_QUEUE[0][2] == REPORT["est_depth"] == depth("P6")
    assert MOD_QUEUE[0][3] == REPORT["status"] == "待复核"
    assert MOD_QUEUE[0][4] == REPORT["submitted"] == "08:07"
    assert abs(MOD_QUEUE[0][5] - REPORT["confidence"]) < 1e-9
    # ...and the sensor agrees with both, which is why it is recommendable
    assert psensor("P6") == "WL-CN-002"
    assert abs(depth("P6") - REPORT["est_depth"]) < 1e-9
    # C2: every count on screen comes from OPS
    assert on == 46 and tot == 52
    assert len(pumps) == 3 and (n_run, n_fix) == (2, 1)
    assert OPS["incidents_open"] == 3 and OPS["staff_on_duty"] == 12
    assert all(p[1] in ("运行", "检修") for p in pumps)
    # C4: status colours come from one shared, asserted mapping
    assert set(STATUS_STYLE) == {"待复核", "已采纳", "已驳回"}
    assert all(m[3] in STATUS_STYLE for m in MOD_QUEUE)
    assert n_pending == 1
    # C5: geometry — rows and cards stay inside the frame, no overlap
    last_row = rows_y + 3 * (row_h + gap) + row_h
    assert last_row <= qy + qh - 16, "queue rows overflow their card"
    assert qy + qh <= iy + ih, "left card must not run past the right stack"
    assert qx + qw < px, "queue card collides with the right column"
    assert py + ph <= iy, "pump card collides with the incident card"
    assert iy + ih <= H - 36, "incident card overflows the frame"
    assert ky + kh <= qy, "KPI strip collides with the queue card"
    # the escalation nodes used as incidents really are ordered in time
    assert ESCALATION[1][0] < ESCALATION[3][0]
    assert "滨江路" in ESCALATION[1][1] and "站前广场" in ESCALATION[3][1]
    return "".join(el)


def main(ver="v1"):
    body = build()
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "case-08-%s.snapshot" % ver)
    doc = ('<Snapshot type="png" background="%s">\n'
           '<SizedBox width="%d" height="%d">\n'
           '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n%s\n'
           '</Stack>\n</SizedBox>\n</Snapshot>\n' % (BG, W, H, body))
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    print("written", path, len(doc), "chars")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
