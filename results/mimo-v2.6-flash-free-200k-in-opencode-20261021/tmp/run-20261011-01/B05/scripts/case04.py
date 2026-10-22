# -*- coding: utf-8 -*-
"""B05 case-04 · 骑行横屏导航 (landscape phone 1688x780).

Audience: 外卖骑手·阿杰 (e-bike). Mounted on handlebar -> landscape, huge type,
few elements, high contrast, glanceable while riding.
Uses PED thresholds (5/10cm) from b05_data, NOT the vehicle rule — this is the
screen's distinct job vs case-01/02/03. ETA + voice-broadcast state bar included.
"""
import os
import sys
from b05_common import box, circle, text, seg, arc, tw as tw_of
from b05_ui import (BG, BG2, CARD, STROKE, INK, SUB, MUTED, AQUA, R_SAFE,
                    R_CAUTION, R_DETOUR, R_BLOCK, F_BODY, F_NUM, F_MONO,
                    status_bar, card, button, mini_depth)
from b05_data import (POINTS, ped_risk_of, depth, pname, prisk, TREND_TXT,
                      TREND_ARROW, ptrend, ptime, RISK_DEMO_NOTE)

W, H = 1688, 780
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "drafts"))

# forward-looking waypoints for the rider (order matters: next first)
LEG = ["P3", "P4"]      # 高新桥下 15cm, 解放路地道 8cm
VOICE = "语音播报：前方高新桥下积水，注意慢行"


def build():
    el = []
    el.append(box(0, 0, W, H, BG))

    # ---- top status strip (wide) ----
    sb, sbh = status_bar(W, dark=True)
    el.append(sb)

    # ---- left panel: next waypoint big verdict ----
    lw = 640
    el.append(box(0, 60, lw, H - 60, BG2))

    pid = LEG[0]
    d = depth(pid)
    plab, plvl, pcol = ped_risk_of(d)

    el.append(text(48, 96, 340, 40, "骑行导航 · 电动车", 26, AQUA, bold=True))
    el.append(text(340, 100, lw - 388, 34,
                   "更新 " + ptime(pid) + " · " + TREND_TXT[ptrend(pid)], 21,
                   MUTED, align="RIGHT", font=F_MONO))
    el.append(text(48, 150, lw - 96, 44, "下一个积水点", 30, MUTED))

    # huge depth readout
    el.append(text(48, 210, 300, 150, "%.0f" % d, 132, INK, bold=True, font=F_NUM))
    el.append(text(360, 268, 120, 60, "cm", 46, SUB))
    el.append(text(48, 366, lw - 96, 56, pname(pid), 44, INK, bold=True))

    # pedestrian verdict (big, glanceable)
    vy = 450
    el.append(box(48, vy, lw - 96, 120, plcol_bg(pcol), radius=24, border=pcol,
                  border_w=3))
    el.append(text(48, vy + 20, lw - 96, 56, plab, 48, pcol, bold=True,
                   align="CENTER"))
    el.append(text(48, vy + 76, lw - 96, 34,
                   ped_advice(d), 24, INK, align="CENTER"))

    # ---- pedestrian threshold ladder (fills lower-left, explains the rule) ----
    ty0 = 596
    el.append(text(48, ty0, lw - 96, 32,
                   "行人/电动车阈值 · 当前点 15cm → 绕行", 21, R_DETOUR,
                   bold=True))
    steps = [(R_SAFE, "0~5", "通行"), (R_CAUTION, "5~10", "注意"),
             (R_DETOUR, "10+", "绕行")]
    sx = 48
    for cc, rng, lab in steps:
        sw = 174
        el.append(box(sx, ty0 + 44, sw, 64, cc + "1F", radius=16,
                      border=cc, border_w=2 if lab == "绕行" else 1.5))
        el.append(circle(sx + 24, ty0 + 60, 7, cc))
        el.append(text(sx + 40, ty0 + 48, sw - 50, 30, rng + "cm", 20, INK,
                       font=F_NUM, bold=True))
        el.append(text(sx + 40, ty0 + 76, sw - 50, 28, lab, 20, cc, bold=True))
        sx += sw + 11
    assert sx - 11 <= lw - 48, "threshold ladder overflows: %d" % (sx - 11)
    el.append(text(48, ty0 + 116, lw - 96, 32,
                   "与汽车分级不同（汽车 10/20/30cm）· 演示规则", 20, MUTED))

    # ---- right panel: route legs + arrival + voice ----
    rx = lw + 40
    rw = W - rx - 48

    # arrival / efficiency card
    el.append(card(rx, 96, rw, 150, CARD))
    el.append(text(rx + 32, 116, 320, 40, "预计送达", 26, SUB))
    el.append(text(rx + 32, 158, 340, 70, "09:04", 60, INK, bold=True, font=F_NUM))
    el.append(text(rx + 300, 176, 160, 40, "还剩 2.3km", 26, AQUA, bold=True))
    # efficiency
    el.append(box(rx + rw - 360, 120, 320, 100, R_SAFE + "1F", radius=18,
                  border=R_SAFE, border_w=1.5))
    el.append(text(rx + rw - 360, 134, 320, 40, "避水 · +0 分钟", 30, R_SAFE,
                   bold=True, align="CENTER"))
    el.append(text(rx + rw - 360, 176, 320, 34,
                   "绕开 20~30cm 绕行点", 21, SUB, align="CENTER"))

    # waypoint legs list
    ly = 274
    el.append(text(rx, ly, 400, 40, "沿途积水点", 28, INK, bold=True))
    rowh = 150
    for i, pid2 in enumerate(LEG):
        yy = ly + 54 + i * (rowh + 20)
        d2 = depth(pid2)
        l2, v2, c2 = ped_risk_of(d2)
        el.append(card(rx, yy, rw, rowh, CARD))
        el.append(box(rx, yy, 10, rowh, c2, radius=5))
        # step number
        el.append(circle(rx + 62, yy + rowh / 2.0, 34, "transparent", border=c2,
                         border_w=3))
        el.append(text(rx + 28, yy + rowh / 2.0 - 30, 68, 60, str(i + 1), 44,
                       c2, bold=True, align="CENTER", font=F_NUM))
        # name + depth
        el.append(text(rx + 128, yy + 26, 480, 44, pname(pid2), 30, INK,
                       bold=True))
        el.append(text(rx + 128, yy + 76, 480, 36,
                       "更新 " + ptime(pid2) + " · " + TREND_TXT[ptrend(pid2)],
                       21, MUTED, font=F_MONO))
        # depth (number -> cm -> pill, laid out right-to-left, no touching)
        pw = int(tw_of(l2, 22)) + 30
        px0 = rx + rw - 32 - pw
        cm_x = px0 - 58
        num_x = cm_x - 172
        el.append(text(num_x, yy + 34, 160, 60, "%.0f" % d2, 46, INK,
                       bold=True, align="RIGHT", font=F_NUM))
        el.append(text(cm_x, yy + 56, 44, 34, "cm", 24, SUB))
        # ped verdict pill (width fits the label)
        el.append(box(px0, yy + 44, pw, 62, c2 + "26", radius=16))
        el.append(text(px0, yy + 56, pw, 40, l2, 22, c2, bold=True,
                       align="CENTER"))
        # progress bar for the whole leg (ped color, agrees with the pill)
        el.append(mini_depth(rx + 128, yy + 120, rw - 190, 12, d2, max_cm=20.0,
                             color=c2))

    # ---- voice broadcast state bar (bottom, full width right panel) ----
    by = H - 96
    el.append(box(rx, by, rw, 72, AQUA + "1F", radius=20, border=AQUA,
                  border_w=2))
    # speaker glyph
    el.append(box(rx + 28, by + 26, 16, 22, AQUA, radius=3))
    el.append(arc(rx + 46, by + 37, 16, -55, 55, 4, AQUA, step=6.0))
    el.append(arc(rx + 46, by + 37, 30, -55, 55, 4, AQUA, step=6.0))
    el.append(text(rx + 96, by + 18, rw - 260, 40, VOICE, 26, INK, bold=True))
    el.append(box(rx + rw - 140, by + 16, 112, 40, AQUA, radius=20))
    el.append(text(rx + rw - 140, by + 22, 112, 30, "已开启", 21, "#04222B",
                   bold=True, align="CENTER"))

    # generation guards
    l0, v0, _ = ped_risk_of(depth("P3"))
    assert v0 == 2, "P3 15cm should be 绕行 under ped rule"
    l1, v1, _ = ped_risk_of(depth("P4"))
    assert v1 == 1, "P4 8cm should be 注意 under ped rule"
    assert all(ped_risk_of(depth(p))[1] < 3 for p in LEG)
    # ped rule differs from vehicle rule for the same point (proves rule switch)
    assert ped_risk_of(depth("P4"))[1] != prisk("P4")[1]
    return "".join(el)


def plcol_bg(c):
    return c + "26"


def ped_advice(d):
    l, v, _ = ped_risk_of(d)
    if v >= 2:
        return "下车推行绕行 · 避免涉水"
    if v == 1:
        return "减速慢行 · 保持车距"
    return "可正常通行"


def main(ver="v1"):
    body = build()
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "case-04-%s.snapshot" % ver)
    doc = ('<Snapshot type="png" background="%s">\n'
           '<SizedBox width="%d" height="%d">\n'
           '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n%s\n'
           '</Stack>\n</SizedBox>\n</Snapshot>\n' % (BG, W, H, body))
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    print("written", path, len(doc), "chars")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
