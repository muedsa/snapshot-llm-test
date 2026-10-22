# -*- coding: utf-8 -*-
"""B05 case-05 · 上报积水 · 参照物估深 (phone 780x1688).

Audience: 市民·林岚 reporting a spot she just passed. Screen shows the
POST-submission state (plan C3: 提交后状态『待复核』), tied to case-08 queue
(#1042). Sections: status stepper / DSL viewfinder (no external photo) /
step-reference cross-section that derives ~26cm geometrically / point select
matching world P6 / confidence slider 0.80 / field note / actions.
"""
import os
import sys
from b05_common import box, circle, text, seg, tw
from b05_ui import (BG, BG2, CARD, STROKE, STROKE_HI, INK, SUB, MUTED, AQUA,
                    R_SAFE, R_CAUTION, R_DETOUR, R_BLOCK, F_BODY, F_NUM,
                    F_MONO, status_bar, home_indicator, card, chip, button,
                    mini_depth)
from b05_data import (REPORT, MOD_QUEUE, pname, pdistrict, depth, prisk,
                      psensor, ptime, risk_color, risk_label)

W, H = 780, 1688
OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "drafts"))

RPT_ID = "#1042"
STEP_RISE = 15.0      # each step tread is 15cm high (demo reference object)
EST = REPORT["est_depth"]     # 26.0cm, between tread1 (15) and tread2 (30)


# ---------------------------------------------------------------- viewfinder
def viewfinder(x, y, w, h):
    """DSL-drawn camera preview: schematic steps + water, brackets, grid.
    Explicitly labelled 示意图（非实拍） — no external photo embedded."""
    el = []
    el.append(box(x, y, w, h, "#05121C", radius=16))
    el.append(box(x, y, w, h, "transparent", radius=16, border=STROKE_HI,
                  border_w=2))
    # rule-of-thirds grid (faint)
    for i in (1, 2):
        gx = x + w * i / 3.0
        el.append(box(gx, y + 8, 1.5, h - 16, "#2A5570"))
        gy = y + h * i / 3.0
        el.append(box(x + 8, gy, w - 16, 1.5, "#2A5570"))

    # --- schematic scene: steps + water (solid sits under its own tread) ---
    ground = y + h - 34
    ppc = 3.0                       # 30cm -> 90px
    t1 = ground - STEP_RISE * ppc   # first tread top (45px above ground)
    t2 = ground - 2 * STEP_RISE * ppc
    wtop = ground - EST * ppc       # 78px above ground = 26cm, between t1/t2
    # stair solid matching the outline below
    el.append(box(x + 60, t1, 290, ground - t1, "#16344A"))
    el.append(box(x + 350, t2, 200, ground - t2, "#16344A"))
    el.append(box(x + 60, ground, 490, 12, "#1B425C"))
    # water
    el.append(box(x + 40, wtop, 510, ground - wtop, "#2E86DE66"))
    # stair outline on top so the reference stays legible
    el.append(seg(x + 60, ground, x + 60, t1, 3, "#8FB6CE"))
    el.append(seg(x + 60, t1, x + 350, t1, 3, "#8FB6CE"))
    el.append(seg(x + 350, t1, x + 350, t2, 3, "#8FB6CE"))
    el.append(seg(x + 350, t2, x + 550, t2, 3, "#8FB6CE"))
    el.append(seg(x + 550, t2, x + 550, ground, 3, "#8FB6CE"))
    el.append(seg(x + 60, ground, x + 550, ground, 3, "#8FB6CE"))
    # waterline (risk color for 26cm)
    rc = risk_color(EST)
    el.append(box(x + 40, wtop - 2, 510, 4, rc))

    # corner brackets
    bl = 34
    for cx, cy, dx, dy in ((x + 14, y + 14, 1, 1), (x + w - 14, y + 14, -1, 1),
                           (x + 14, y + h - 14, 1, -1),
                           (x + w - 14, y + h - 14, -1, -1)):
        el.append(box(cx if dx > 0 else cx - bl, cy - 2, bl, 4, AQUA))
        el.append(box(cx - 2 if dx > 0 else cx - 4, cy if dy > 0 else cy - bl,
                      4, bl, AQUA))
    # centre crosshair
    ccx, ccy = x + w / 2.0, y + h / 2.0 - 26
    el.append(box(ccx - 16, ccy - 1.5, 32, 3, AQUA))
    el.append(box(ccx - 1.5, ccy - 16, 3, 32, AQUA))

    # overlays: REC + time (top-left), locate chip (top-right)
    el.append(circle(x + 30, y + 40, 8, R_BLOCK))
    el.append(text(x + 46, y + 26, 160, 32, "08:07", 21, INK, bold=True,
                   font=F_MONO))
    lc = "定位已获取"
    lw2 = int(tw(lc, 19)) + 30
    el.append(box(x + w - 24 - lw2, y + 24, lw2, 36, "#04222BAA", radius=18))
    el.append(text(x + w - 24 - lw2, y + 31, lw2, 26, lc, 19, AQUA,
                   align="CENTER", bold=True))
    # honesty label (bottom-right)
    hl = "示意图 · 非实拍"
    hw = int(tw(hl, 18)) + 24
    el.append(box(x + w - 20 - hw, y + h - 46, hw, 32, "#05121CCC", radius=16))
    el.append(text(x + w - 20 - hw, y + h - 41, hw, 26, hl, 18, MUTED,
                   align="CENTER"))
    return "".join(el)


# ------------------------------------------------- step-reference cross-section
def cross_section(x0, y0, w, ch):
    """Side-view of the actual reference object: derives 26cm geometrically."""
    el = []
    el.append(card(x0, y0, w, ch, CARD))
    # header: title + risk chip + big estimate
    el.append(text(x0 + 28, y0 + 16, 250, 40, "② 参照物估深", 26, INK, bold=True))
    rc = risk_color(EST)
    rl = risk_label(EST)
    lab = "%.0fcm · %s" % (EST, rl)
    cw = int(tw(lab, 21)) + 34
    el.append(box(x0 + 300, y0 + 14, cw, 44, rc + "26", radius=22,
                  border=rc, border_w=1.5))
    el.append(text(x0 + 300, y0 + 23, cw, 30, lab, 21, rc, bold=True,
                   align="CENTER"))
    el.append(text(x0 + w - 64 - 240, y0 + 10, 240, 54, "≈ %.0f" % EST, 42,
                   INK, bold=True, align="RIGHT", font=F_NUM))
    el.append(text(x0 + w - 60, y0 + 26, 40, 30, "cm", 20, SUB))

    # geometry
    ground = y0 + 276
    ppc = 5.8                       # 30cm -> 174px (proportional, asserted)
    t1 = ground - STEP_RISE * ppc
    t2 = ground - 2 * STEP_RISE * ppc
    wtop = ground - EST * ppc
    A, B, C, D = x0 + 42, x0 + 150, x0 + 300, x0 + 452

    # stair solid: blocks sit UNDER their own treads (left of riser = floor)
    el.append(box(B, t1, C - B, ground - t1, "#16344A"))
    el.append(box(C, t2, D - C, ground - t2, "#16344A"))
    el.append(box(A, ground, D - A + 6, 14, "#1B425C"))
    # water body (over the submerged part of the solid)
    el.append(box(A - 4, wtop, (D + 4) - (A - 4), ground - wtop, "#2E86DE66"))
    # step outline drawn over the water so the reference stays legible
    pts = [(A, ground), (B, ground), (B, t1), (C, t1), (C, t2), (D, t2),
           (D, ground), (A, ground)]
    for i in range(len(pts) - 1):
        el.append(seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                      4, "#9CC0D6"))
    # waterline (risk color for 26cm) — stops clear of the step guides
    el.append(box(A - 8, wtop - 2.5, (D + 8) - (A - 8), 5, rc))

    # --- labels: water on the left (air), step levels on the right ---
    lw2 = int(tw("水面 %.0fcm" % EST, 20)) + 26
    el.append(box(x0 + 40, wtop - 46, lw2, 36, rc + "33", radius=10))
    el.append(text(x0 + 40, wtop - 39, lw2, 30, "水面 %.0fcm" % EST, 20, rc,
                   bold=True, align="CENTER"))
    el.append(box(x0 + 40 + lw2 / 2.0 - 1.5, wtop - 10, 3, 10, rc))

    rlx, rtx = x0 + 478, x0 + 514
    for yv, txt in ((t2, "第二级 30cm"), (t1, "第一级 15cm"),
                    (ground, "地面 0cm")):
        el.append(box(rlx, yv - 1.5, rtx - 12 - rlx, 3, STROKE_HI))
        el.append(text(rtx, yv - 17, x0 + w - 28 - rtx, 34, txt, 20, SUB,
                       bold=True))

    # annotation (single line, clears the base slab)
    el.append(text(x0 + 28, y0 + 300, w - 56, 34,
                   "水面高于第一级 15cm、低于第二级 30cm → 估深约 26cm", 21,
                   INK))
    # proportionality guard (C1)
    assert abs((ground - t2) / ppc - 30.0) < 0.01
    assert abs((ground - wtop) / ppc - EST) < 0.01
    assert t2 < wtop < t1, "26cm must sit between the two treads"
    return "".join(el)


def build():
    el = []
    el.append(box(0, 0, W, H, BG))
    sb, sbh = status_bar(W, dark=True)
    el.append(sb)

    # ---- nav header ----
    hy = 72
    el.append(text(44, hy, 60, 56, "‹", 46, AQUA, bold=True))
    el.append(text(108, hy + 6, 360, 48, "上报积水", 32, INK, bold=True))
    # post-submit badge
    bb = "已提交"
    bw = int(tw(bb, 22)) + 34
    el.append(box(W - 44 - bw, hy + 8, bw, 44, R_SAFE + "26", radius=22,
                  border=R_SAFE, border_w=1.5))
    el.append(text(W - 44 - bw, hy + 16, bw, 30, bb, 22, R_SAFE, bold=True,
                   align="CENTER"))
    el.append(text(44, hy + 62, W - 88, 32,
                   "编号 " + RPT_ID + " · 提交于 " + REPORT["submitted"] +
                   " · " + pname(REPORT["point"]), 21, MUTED, font=F_MONO))

    # ---- status stepper (post-submit feedback, C3) ----
    sy = 186
    sh = 104
    el.append(card(44, sy, W - 88, sh, CARD))
    nodes = [(130, "已提交", R_SAFE, True, REPORT["submitted"]),
             (385, "待复核", R_DETOUR, False, "当前状态"),
             (640, "已采纳", MUTED, False, "复核通过后")]
    # connector lines
    el.append(box(nodes[0][0] + 24, sy + 36, nodes[1][0] - 24 - (nodes[0][0] + 24),
                  3, R_SAFE))
    el.append(box(nodes[1][0] + 24, sy + 36, nodes[2][0] - 24 - (nodes[1][0] + 24),
                  3, STROKE_HI))
    for i, (cx, lab, cc, done, sub) in enumerate(nodes):
        active = (i == 1)
        r = 15
        el.append(circle(cx, sy + 38, r, cc if done else "transparent",
                         border=cc, border_w=3))
        if active:
            el.append(circle(cx, sy + 38, 22, R_DETOUR + "33"))
            el.append(circle(cx, sy + 38, r, R_DETOUR))
            el.append(circle(cx, sy + 38, 6, BG))
        el.append(text(cx - 95, sy + 58, 190, 30, lab, 21,
                       cc if (done or active) else MUTED, bold=True,
                       align="CENTER"))
        el.append(text(cx - 95, sy + 82, 190, 24, sub, 16, MUTED,
                       align="CENTER", font=F_MONO))

    # ---- ① viewfinder ----
    vy = 314
    el.append(text(44, vy, 400, 34, "① 拍摄参照物", 24, INK, bold=True))
    el.append(text(W - 44 - 260, vy + 3, 260, 30, "已拍摄 · 可重拍", 19, MUTED,
                   align="RIGHT"))
    el.append(viewfinder(44, vy + 44, W - 88, 300))
    el.append(text(44, vy + 356, W - 88, 30,
                   "取景框为界面示意，未上传实拍照片", 18, MUTED))

    # ---- ② cross-section ----
    csy = 716
    el.append(cross_section(44, csy, W - 88, 360))

    # ---- ③ point select ----
    py = 1092
    ph = 136
    pid = REPORT["point"]
    el.append(card(44, py, W - 88, ph, CARD))
    el.append(box(44, py, 8, ph, R_DETOUR, radius=4))
    el.append(text(76, py + 18, 420, 40, "③ 上报点位", 24, INK, bold=True))
    # selected radio
    el.append(circle(W - 44 - 30, py + 34, 15, "transparent", border=AQUA,
                     border_w=3))
    el.append(circle(W - 44 - 30, py + 34, 8, AQUA))
    el.append(text(76, py + 62, 440, 40, pname(pid), 27, INK, bold=True))
    el.append(text(76, py + 104, 460, 26,
                   pdistrict(pid) + " · " + psensor(pid), 18, MUTED,
                   font=F_MONO))
    # cross-check vs world value (C4)
    d = depth(pid)
    el.append(text(W - 44 - 300, py + 66, 260, 34, "实测 %.0fcm" % d, 23, INK,
                   bold=True, align="RIGHT", font=F_NUM))
    el.append(mini_depth(W - 44 - 300, py + 106, 254, 10, d))
    ag = abs(d - EST) < 0.5
    el.append(text(W - 44 - 340, py + 24, 260, 30,
                   "与上报一致" if ag else "与上报不一致", 19,
                   R_SAFE if ag else R_DETOUR, bold=True, align="RIGHT"))
    assert W - 44 - 340 + 260 < W - 44 - 30 - 15, "consistency label hits radio"

    # ---- ④ confidence slider ----
    gy = 1244
    gh = 158
    el.append(card(44, gy, W - 88, gh, CARD))
    el.append(text(76, gy + 18, 300, 34, "④ 可信度", 24, INK, bold=True))
    conf = REPORT["confidence"]          # 0.8
    el.append(text(W - 44 - 200, gy + 12, 176, 50, "%.2f" % conf, 38, AQUA,
                   bold=True, align="RIGHT", font=F_NUM))
    tx0, tw2 = 76, W - 88 - 96
    ty = gy + 66
    el.append(box(tx0, ty, tw2, 14, "#0C2740", radius=7))
    el.append(box(tx0, ty, tw2 * conf, 14, AQUA, radius=7))
    kx = tx0 + tw2 * conf
    el.append(circle(kx, ty + 7, 17, AQUA))
    el.append(circle(kx, ty + 7, 7, CARD))
    for frac, lab in ((0.0, "低"), (0.5, "一般"), (1.0, "高")):
        px = tx0 + tw2 * frac
        el.append(box(px - 1, ty + 20, 2, 8, STROKE_HI))
        el.append(text(px - 50, ty + 28, 100, 26, lab, 18, MUTED,
                       align="CENTER"))
    el.append(text(76, gy + 124, W - 152, 28,
                   "有清晰参照物 + 定位准确 → 较高可信度（0.80）", 19, SUB))
    assert ty + 28 + 26 <= gy + 124, "tick labels collide with hint"
    assert gy + 124 + 28 <= gy + gh - 6, "hint overflows confidence card"

    # ---- ⑤ field note ----
    ny = 1418
    nh = 104
    el.append(card(44, ny, W - 88, nh, CARD))
    el.append(text(76, ny + 14, 300, 32, "⑤ 现场备注", 23, INK, bold=True))
    el.append(text(76, ny + 50, W - 152, 44,
                   "站前广场台阶已没过一半，行人改走东侧坡道。", 21, SUB))

    # ---- actions ----
    byy = H - 150
    el.append(button(44, byy, 430, 78, "查看复核进度", fill=AQUA, fg="#04222B",
                     size=27))
    el.append(button(490, byy, W - 44 - 490, 78, "编辑上报", outline=STROKE,
                     fg=INK, size=27))
    el.append(home_indicator(W, H - 26, dark=True))

    # ---- generation guards ----
    assert REPORT["point"] in ("P6",), "report point must be world P6"
    assert abs(depth("P6") - EST) < 0.5, "report depth must match world P6"
    assert MOD_QUEUE[0][1] == pname("P6"), "case-08 queue id tie"
    assert MOD_QUEUE[0][0] == RPT_ID and MOD_QUEUE[0][3] == "待复核"
    assert MOD_QUEUE[0][4] == REPORT["submitted"]
    assert 0.0 <= conf <= 1.0
    assert byy > ny + nh, "note card collides with actions"
    return "".join(el)


def main(ver="v1"):
    body = build()
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "case-05-%s.snapshot" % ver)
    doc = ('<Snapshot type="png" background="%s">\n'
           '<SizedBox width="%d" height="%d">\n'
           '<Stack alignment="TOP_LEFT" clipBehavior="NONE">\n%s\n'
           '</Stack>\n</SizedBox>\n</Snapshot>\n' % (BG, W, H, body))
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    print("written", path, len(doc), "chars")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
