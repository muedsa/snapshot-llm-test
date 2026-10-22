# -*- coding: utf-8 -*-
"""B05 case-03 · 避水路线规划 (phone 780x1688).

User goal: 比较最短/避水/辅路三条路线，选一条不涉禁止通行点的路。
Persona 通勤族·林岚. Shows 3 route cards with cross points + risk, a
recommendation, and the +time tradeoff. Recommended avoids blocked P1.
"""
import os
import sys
from b05_common import box, circle, text, seg
from b05_ui import (BG, CARD, STROKE, INK, SUB, MUTED, AQUA, R_SAFE, R_CAUTION,
                    R_DETOUR, R_BLOCK, F_BODY, F_NUM, F_MONO, status_bar,
                    home_indicator, card, chip, button)
from b05_data import (ROUTES, ROUTE_RECO, pname, depth, prisk, risk_color,
                      CAR_CLEAR_MM, car_passable, HERO)

HERO_P = HERO

W, H = 780, 1688
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "drafts"))


def route_risk_max(pids):
    return max(prisk(p)[1] for p in pids)


def _eta(mins):
    """arrival clock time from NOW (08:15) + mins — demo schedule."""
    base = 8 * 60 + 15 + mins
    return "%02d:%02d" % (base // 60, base % 60)


def build():
    el = []
    el.append(box(0, 0, W, H, BG))
    sb, sbh = status_bar(W, dark=True)
    el.append(sb)

    # header
    hy = 72
    el.append(text(44, hy, 60, 56, "‹", 46, AQUA, bold=True))
    el.append(text(108, hy + 8, 520, 44, "路线规划", 30, INK, bold=True))
    el.append(text(44, hy + 62, 600, 34, "滨江家园 → 滨江CBD · 现在出发", 23, MUTED))

    # origin/destination strip
    oy = hy + 118
    oh = 132
    el.append(card(44, oy, W - 88, oh, CARD))
    el.append(circle(84, oy + 44, 9, AQUA))
    el.append(box(82, oy + 52, 4, 34, STROKE))
    el.append(circle(84, oy + 92, 9, R_BLOCK))
    el.append(text(112, oy + 26, 560, 40, "滨江家园 3 号门", 26, INK, bold=True))
    el.append(text(112, oy + 74, 560, 40, "滨江CBD · 通勤打卡 09:00", 26, INK,
                   bold=True))
    el.append(text(W - 44 - 140, oy + 46, 120, 40, "8.4km", 26, SUB,
                   align="RIGHT", font=F_NUM))

    # route cards
    ry = oy + oh + 24
    # sort so recommended is visually highlighted; keep data order but mark
    for i, (rname, mins, pids, reason) in enumerate(ROUTES):
        reco = (i == ROUTE_RECO)
        ch = 298 if reco else 278
        colr = AQUA if reco else CARD
        border = AQUA if reco else STROKE
        el.append(card(44, ry, W - 88, ch, CARD if not reco else "#0E3A4A",
                       border=border, border_w=2 if reco else 1))
        # left color spine by max risk
        mr = route_risk_max(pids)
        spine = R_BLOCK if mr >= 3 else (R_DETOUR if mr == 2 else (
            R_CAUTION if mr == 1 else R_SAFE))
        el.append(box(44, ry, 10, ch, spine, radius=5))
        # name + time (clear right slot: digits end at 660, unit 666..712)
        nw = tw_local(rname, 32)
        el.append(text(72, ry + 24, 400, 48, rname, 32, INK, bold=True))
        if reco:
            bx0 = 72 + nw + 18
            el.append(box(bx0, ry + 30, 96, 40, AQUA, radius=20))
            el.append(text(bx0, ry + 37, 96, 30, "推荐", 22, "#04222B",
                           bold=True, align="CENTER"))
        el.append(text(500, ry + 20, 160, 56, str(mins), 44,
                       AQUA if reco else INK, bold=True, align="RIGHT",
                       font=F_NUM))
        el.append(text(666, ry + 40, 46, 30, "分", 20, SUB))
        # cross points as chips
        cxx = 72
        cyy = ry + 92
        el.append(text(72, ry + 84, 200, 30, "途经", 20, MUTED))
        cxx = 150
        for pid in pids:
            plab, plvl, pcol = prisk(pid)
            lbl = pname(pid) + " " + ("%.0f" % depth(pid)) + "cm"
            pw = int(tw_local(lbl, 20)) + 32
            el.append(box(cxx, cyy, pw, 42, pcol + "26", radius=21,
                          border=pcol, border_w=1.5))
            el.append(text(cxx, cyy + 8, pw, 30, lbl, 20, pcol, bold=True,
                           align="CENTER"))
            cxx += pw + 12
        # reason + ETA
        el.append(text(72, ry + 148, W - 132, 36, reason, 23, SUB))
        eta = _eta(mins)
        el.append(text(72, ry + 188, 420, 32, "预计 " + eta + " 到达 · 打卡 09:00",
                       21, MUTED, font=F_MONO))
        # bottom verdict line
        vy = ry + ch - 52
        if mr >= 3:
            vt = "含禁止通行点 · 不建议"
            vc = R_BLOCK
        elif mr == 2:
            vt = "含绕行点 · 需谨慎"
            vc = R_DETOUR
        else:
            vt = "全程无禁止/绕行点 · 安全"
            vc = R_SAFE
        el.append(text(72, vy, W - 132, 36, vt, 23, vc, bold=True))
        ry += ch + 18

    # tradeoff footer
    fy = ry + 6
    el.append(card(44, fy, W - 88, 140, AQUA + "14", border=AQUA))
    el.append(text(72, fy + 18, W - 148, 36, "为何绕行值得", 24, AQUA, bold=True))
    el.append(text(72, fy + 56, W - 148, 36,
                   "避水路线多 5 分钟，但避开 1 处禁止通行点（32cm）", 23, INK))
    el.append(text(72, fy + 96, W - 148, 34,
                   "小车离地间隙 140mm ＜ 32cm 水深 · 确不可过", 21, R_BLOCK,
                   bold=True))

    # risk legend strip (unified product language)
    ly2 = fy + 154
    el.append(text(44, ly2, 300, 30, "通行分级图例", 20, MUTED))
    el.append(text(360, ly2 + 2, W - 44 - 360, 28,
                   "演示分级规则 · 与首页/详情/车机一致", 17, MUTED,
                   align="RIGHT"))
    leg = [(R_SAFE, "＜10 可通行"), (R_CAUTION, "10~20 谨慎"),
           (R_DETOUR, "20~30 绕行"), (R_BLOCK, "＞30 禁止")]
    lx = 44
    for cc, lab in leg:
        lw = int(tw_local(lab, 19)) + 54
        el.append(box(lx, ly2 + 36, lw, 42, cc + "1F", radius=21,
                      border=cc, border_w=1.5))
        el.append(circle(lx + 22, ly2 + 57, 8, cc))
        el.append(text(lx + 38, ly2 + 45, lw - 44, 30, lab, 19, INK))
        lx += lw + 10
    assert lx - 10 <= W - 44, "legend overflows: %d" % (lx - 10)

    # bottom CTA
    byy = H - 150
    assert ly2 + 78 <= byy - 8, "legend collides with CTA: %d > %d" % (
        ly2 + 78, byy - 8)
    el.append(button(44, byy, W - 88, 78, "用避水路线开始导航", fill=AQUA,
                     fg="#04222B", size=28))
    el.append(home_indicator(W, H - 26, dark=True))

    # generation guards: recommended avoids blocked point; times ascending
    reco_pids = ROUTES[ROUTE_RECO][2]
    assert all(prisk(p)[1] < 3 for p in reco_pids), "reco route hits blocked pt"
    assert ROUTES[0][1] < ROUTES[ROUTE_RECO][1] < ROUTES[2][1]
    # recommended is the one with no blocked point and lowest max-risk among
    # non-blocked options
    assert route_risk_max(reco_pids) <= 2
    # clearance claim must match the shared demo rule (C3)
    assert car_passable(depth(HERO_P)) is False, "32cm must exceed 140mm"
    assert CAR_CLEAR_MM == 140
    return "".join(el)


def tw_local(s, size):
    w = 0.0
    for ch in s:
        w += 1.0 if ord(ch) >= 0x2E80 else 0.56
    return w * size


def main(ver="v1"):
    body = build()
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "case-03-%s.snapshot" % ver)
    doc = ('<Snapshot type="png" background="%s">\n'
           '<SizedBox width="%d" height="%d">\n'
           '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n%s\n'
           '</Stack>\n</SizedBox>\n</Snapshot>\n' % (BG, W, H, body))
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    print("written", path, len(doc), "chars")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
