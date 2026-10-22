# -*- coding: utf-8 -*-
"""A24 action card (720x1280): 12 tasks in time order, team/times/risks.

Fixes vs baseline (action-card-02): row line-2 (risk text) used to overlap the
end-time text and cover the team name / K badge; deps text was clipped at the
old 110px column. New row layout: line1 = start -> end + ID chip + label +
team (540..676 col fits "engineering"); line2 = deps for plain rows, full-width
risk reminder + K badge for risk rows. Row h=66 (bg 60), lines at y+4 / y+36.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a24_common as C  # noqa: E402

W, H = 720, 1280
P = C.PAL
ROW_H = 66
LIST_Y = 166


def emit():
    els = [C.rect_at(0, 0, W, H, P["bg_card"]),
           # ---- header ----
           C.rect_at(0, 0, W, 150, P["head"]),
           C.text_el(36, 24, 400, 30, "叠光 · 发布演练", 20, P["head_brand"]),
           C.text_el(36, 52, 640, 54, "发布日 · 手机行动卡", 40, P["white"],
                     bold=True),
           C.text_el(36, 106, 640, 32,
                     "2026-11-07 · 完工 13:20 · 缓冲 160min", 22,
                     P["head_soft"]),
           C.text_el(430, 26, 254, 30, "12 任务 · 按时间序", 20,
                     "#6EE7B7", align="RIGHT")]
    rows = sorted(C.SCHEDULE, key=lambda t: (t["s"], t["id"]))
    for i, t in enumerate(rows):
        y = LIST_Y + i * ROW_H
        bg = P["white"] if i % 2 == 0 else "#F4F6FB"
        els.append(C.rect_at(30, y, 660, ROW_H - 6, bg, 10))
        # line 1: start -> end | ID chip | label | team
        els.append(C.text_el(46, y + 4, 70, 34, C.clock(t["s"]), 24,
                             P["ink"], bold=True))
        els.append(C.text_el(116, y + 8, 86, 30, "→ " + C.clock(t["e"]), 20,
                             P["muted"]))
        els.append(C.chip_el(210, y + 6, 56, 30, C.TEAM_COLOR[t["team"]],
                             t["id"], 20, P["white"], radius=8))
        els.append(C.text_el(278, y + 5, 250, 34, t["label"], 24, P["ink"]))
        els.append(C.text_el(540, y + 10, 136, 26, t["team"], 20,
                             C.TEAM_COLOR[t["team"]], align="RIGHT"))
        # line 2: deps (plain rows) or full-width risk reminder (risk rows);
        # risk rows put the K badge on line 1 after the label so line 2 has
        # room for the longest reminder (K3 measured ~595px at 20px)
        if t["risk"]:
            r = C.RISK_BY_TASK[t["id"]]
            bx = 278 + 24 * len(t["label"]) + 14   # labels are all CJK
            els.append(C.chip_el(bx, y + 6, 46, 30, P["bad_soft"], t["risk"],
                                 20, P["bad"], radius=6,
                                 border=P["bad_border"], border_w=1))
            els.append(C.text_el(46, y + 36, 630, 25,
                                 "%s · %s → %s" % (t["risk"], r["impact"],
                                                   r["mitigation"]), 20,
                                 "#B91C1C"))
        else:
            deps = ("依赖 " + "、".join(t["deps"])) if t["deps"] else "起点任务"
            els.append(C.text_el(46, y + 36, 578, 25, deps, 20, P["faint"]))
    # ---- risk reminder block ----
    ry = LIST_Y + 12 * ROW_H + 16          # 974
    els.append(C.rect_at(30, ry, 660, 190, P["white"], 12, P["line"], 2))
    els.append(C.rect_at(30, ry, 6, 190, P["bad"], 3))
    els.append(C.text_el(48, ry + 14, 620, 36, "风险提醒（返工将消耗缓冲）", 26,
                         P["ink"], bold=True))
    for i, r in enumerate(C.RISKS):
        els.append(C.text_el(48, ry + 58 + i * 34, 620, 30,
                             "%s · %s %s → %s" % (r["id"], r["task"],
                                                  r["impact"],
                                                  r["mitigation"]),
                             20, P["muted"]))
    els.append(C.text_el(48, ry + 160, 620, 26,
                         "缓冲 160min（13:20 完工）为 K3 返工预留", 20,
                         P["faint"]))
    # ---- footer ---- (must fit one line in 640px at 20px)
    els.append(C.rect_at(30, ry + 210, 660, 1.5, P["line"]))
    els.append(C.text_el(36, ry + 226, 640, 30,
                         "数据源 schedule.json（三图同源）· "
                         "半开区间 [start,end)", 20, P["faint"]))
    return C.wrap_el("".join(els), W, H, P["bg_card"])


if __name__ == "__main__":
    errs = C.check_schedule()
    assert not errs, errs
    dsl = emit()
    out = "tmp/run-20261011-01/A24/action-card.snapshot"
    open(out, "w", encoding="utf-8").write(dsl)
    print("card dsl written:", out, len(dsl), "chars,",
          len(dsl.encode("utf-8")), "bytes")
