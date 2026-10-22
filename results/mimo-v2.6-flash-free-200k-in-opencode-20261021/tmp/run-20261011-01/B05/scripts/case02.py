# -*- coding: utf-8 -*-
"""B05 case-02 · 水点详情 · 滨江路下穿隧道 (phone 780x1688).

Signature screen: the DepthRuler (vertical water-level gauge) as hero, showing
32cm and geometrically-proportional water. Trend sparkline, dual source
(sensor WL-BJ-001 + crowd), pass verdict, alternative (P4 8cm).
Persona 通勤族·林岚 tapping a point from the home list.
"""
import os
import sys
from b05_common import box, circle, text, seg
from b05_ui import (BG, BG2, CARD, STROKE, INK, SUB, MUTED, AQUA, R_SAFE,
                    R_CAUTION, R_DETOUR, R_BLOCK, F_BODY, F_NUM, F_MONO,
                    status_bar, home_indicator, card, chip, depth_ruler,
                    sparkline, mini_depth, button)
from b05_data import (depth, pname, pdistrict, ptrend, ptime, psensor, pcrowd,
                      prisk, TREND_TXT, TREND_ARROW, risk_color, HERO, POINTS,
                      ptime)

W, H = 780, 1688
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "drafts"))

# 24h depth history for the hero point (rising to 32) — demo series
HIST = [2, 3, 5, 8, 11, 14, 19, 23, 27, 30, 32]


def build():
    pid = HERO
    d = depth(pid)
    label, level, colr = prisk(pid)
    el = []
    el.append(box(0, 0, W, H, BG))
    sb, sbh = status_bar(W, dark=True)
    el.append(sb)

    # ---- nav header ----
    hy = 72
    el.append(text(44, hy, 60, 56, "‹", 46, AQUA, bold=True))
    el.append(text(108, hy + 8, 420, 44, "积水点详情", 26, SUB))
    el.append(text(W - 44 - 160, hy + 10, 160, 40, "收藏 ☆", 24, MUTED,
                   align="RIGHT"))

    # ---- title block ----
    ty = hy + 64
    el.append(text(44, ty, 520, 56, pname(pid), 40, INK, bold=True))
    el.append(text(44, ty + 58, 300, 36, pdistrict(pid) + " · 下穿隧道", 24, MUTED))
    # risk pill (top-right)
    rp_w = 168
    el.append(box(W - 44 - rp_w, ty + 4, rp_w, 56, colr + "26", radius=28))
    el.append(text(W - 44 - rp_w, ty + 18, rp_w, 34, label, 26, colr,
                   bold=True, align="CENTER"))

    # ---- hero: DepthRuler + readout card ----
    hy2 = ty + 118
    hh = 560
    el.append(card(44, hy2, W - 88, hh, CARD))
    # the ruler (left)
    el.append(depth_ruler(76, hy2 + 30, 250, hh - 60, d, max_cm=50.0,
                          label_side="right", big=True))
    # right side: verdict + trend
    rx = 356
    rw = W - 44 - rx - 28
    # big number
    el.append(text(rx, hy2 + 40, rw, 90, "%.0f" % d, 84, INK, bold=True,
                   font=F_NUM))
    el.append(text(rx + 150, hy2 + 78, 120, 44, "cm", 34, SUB))
    # trend row
    ta = TREND_ARROW[ptrend(pid)]
    tc = R_BLOCK if ptrend(pid) == "rising" else MUTED
    el.append(text(rx, hy2 + 140, rw, 40, ta + " " + TREND_TXT[ptrend(pid)] +
                   " · 近1小时 +9cm", 26, tc, bold=True))
    # trend sparkline
    el.append(text(rx, hy2 + 196, rw, 32, "近 12 小时水位", 20, MUTED))
    el.append(sparkline(rx, hy2 + 230, rw, 150, HIST, color=colr,
                        line_thick=4))
    el.append(text(rx, hy2 + 384, rw, 30, "02:00", 17, MUTED, font=F_MONO))
    el.append(text(rx, hy2 + 384, rw, 30, "08:00", 17, MUTED, align="RIGHT",
                   font=F_MONO))
    # pass verdict badge
    vy = hy2 + 434
    el.append(box(rx, vy, rw, 88, R_BLOCK + "1F", radius=18, border=R_BLOCK,
                  border_w=2))
    el.append(text(rx + 20, vy + 14, rw - 40, 40, "禁止通行", 30, R_BLOCK,
                   bold=True))
    el.append(text(rx + 20, vy + 52, rw - 40, 30, "水深超过小车安全通过阈值",
                   19, SUB))

    # ---- dual source ----
    sy = hy2 + hh + 24
    sh = 168
    half = (W - 88 - 16) / 2.0
    el.append(card(44, sy, half, sh, CARD))
    el.append(text(64, sy + 20, half - 40, 34, "实测传感器", 22, AQUA, bold=True))
    el.append(text(64, sy + 62, half - 40, 44, psensor(pid), 30, INK,
                   bold=True, font=F_MONO))
    el.append(text(64, sy + 110, half - 40, 32, "超声波 · 更新 " + ptime(pid),
                   19, MUTED, font=F_MONO))
    el.append(card(44 + half + 16, sy, half, sh, CARD))
    el.append(text(64 + half + 16, sy + 20, half - 40, 34, "众包上报", 22, AQUA,
                   bold=True))
    el.append(text(64 + half + 16, sy + 62, half - 40, 44, str(pcrowd(pid)) +
                   " 条", 30, INK, bold=True, font=F_NUM))
    el.append(text(64 + half + 16, sy + 110, half - 40, 32, "近1小时 · 已交叉核验",
                   19, MUTED))

    # ---- alternative suggestion ----
    ay = sy + sh + 24
    ah = 200
    el.append(card(44, ay, W - 88, ah, R_SAFE + "14", border=R_SAFE))
    el.append(box(44, ay, 10, ah, R_SAFE, radius=5))
    el.append(text(72, ay + 22, 400, 38, "附近可通行替代", 24, R_SAFE, bold=True))
    alt = "P4"   # 解放路地道 8cm
    el.append(text(72, ay + 72, 460, 44, pname(alt), 30, INK, bold=True))
    el.append(text(72, ay + 120, 460, 34, pdistrict(alt) + " · " + ptime(alt),
                   20, MUTED, font=F_MONO))
    el.append(text(72, ay + 156, 520, 34, "绕行约 1.2km · 多 4 分钟", 21, SUB))
    el.append(text(528, ay + 84, 150, 12, "", 12, SUB))
    el.append(mini_depth(520, ay + 84, 150, 12, depth(alt)))
    el.append(text(520, ay + 38, 150, 40, "%.0f" % depth(alt), 34, INK,
                   bold=True, align="RIGHT", font=F_NUM))
    el.append(text(674, ay + 52, 52, 28, "cm", 18, SUB))
    el.append(text(520, ay + 108, 150, 32, prisk(alt)[0], 22, R_SAFE,
                   bold=True, align="RIGHT"))

    # ---- why forbidden: demo rule + vehicle clearance (transparency) ----
    wy = ay + ah + 24
    wh = 250
    el.append(card(44, wy, W - 88, wh, CARD))
    el.append(text(72, wy + 22, 500, 38, "为何判定「禁止通行」", 26, INK,
                   bold=True))
    # demo risk band legend (compact)
    bx = 72
    bw_total = W - 144
    seg_w = bw_total / 4.0
    bands = [("＜10 可通行", R_SAFE), ("10~20 谨慎", R_CAUTION),
             ("20~30 绕行", R_DETOUR), ("＞30 禁止", R_BLOCK)]
    for i, (lab, cc) in enumerate(bands):
        xx = bx + i * seg_w
        el.append(box(xx, wy + 74, seg_w - 8, 16, cc, radius=8))
        el.append(text(xx, wy + 96, seg_w - 8, 28, lab, 17,
                       INK if i == 3 else MUTED, bold=(i == 3)))
    # vehicle clearance comparison
    el.append(text(72, wy + 136, 300, 32, "当前 32cm 对小车离地间隙", 21, MUTED))
    cy = wy + 176
    el.append(mini_depth(72, cy, 300, 16, 32.0, max_cm=40.0))
    el.append(text(392, cy - 6, 120, 34, "32cm", 24, R_BLOCK, bold=True,
                   font=F_NUM))
    el.append(box(72 + 300 * (14.0 / 40.0) - 2, cy - 8, 4, 32, INK))
    el.append(text(72, cy + 26, 460, 30, "小车安全通过阈值约 14cm（演示规则）",
                   18, MUTED))
    el.append(text(W - 44 - 260, wy + 200, 236, 30, "演示分级 · 非官方标准", 17,
                   MUTED, align="RIGHT"))

    # ---- bottom CTA ----
    byy = H - 150
    el.append(button(44, byy, 320, 76, "改走替代路线", fill=AQUA, fg="#04222B",
                     size=26))
    el.append(button(400, byy, W - 444, 76, "上报新情况", outline=STROKE,
                     fg=INK, size=26))
    el.append(home_indicator(W, H - 26, dark=True))

    # generation guard: alternative must be actually passable & different point
    assert alt != pid
    assert prisk(alt)[1] == 0
    return "".join(el)


def main(ver="v1"):
    body = build()
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "case-02-%s.snapshot" % ver)
    doc = ('<Snapshot type="png" background="%s">\n'
           '<SizedBox width="%d" height="%d">\n'
           '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n%s\n'
           '</Stack>\n</SizedBox>\n</Snapshot>\n' % (BG, W, H, body))
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    print("written", path, len(doc), "chars")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
