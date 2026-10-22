# -*- coding: utf-8 -*-
"""A24 execution board (1920x1080): two-team swimlane Gantt, same-scale time.

Layout lessons from execution-board-02/03 renders:
- footer lines must fit one line in the 570px box (wrap+32px box clips);
- adjacent rounded blocks (r=10) leave a white "bowtie" channel at the seam
  (pixel-verified 5px at y=592) -> draw a team-colored seam cover per
  contiguous boundary;
- gridlines and the finish/deadline lines must be drawn AFTER the opaque lane
  bands (else hidden) and BEFORE blocks/captions (blocks cover them where
  they overlap, captions stay readable on top);
- 16:00 axis label is right-aligned so the red line does not cross it.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a24_common as C  # noqa: E402

W, H = 1920, 1080
P = C.PAL
X0, PPM = 260.0, 3.81          # time axis: minute 0 at x=260, 3.81 px/min


def X(m):
    return C.r2(X0 + m * PPM)


LANE = {"design": dict(band=300, block=308, rowA=392, rowB=476),
        "engineering": dict(band=580, block=588, rowA=672, rowB=756)}
BLK_H = 76
ROW_OF = {"R01": "A", "R04": "B", "R07": "A", "R09": "B", "R10": "A", "R12": "B",
          "R02": "A", "R03": "B", "R05": "A", "R06": "B", "R08": "A", "R11": "B"}


def emit():
    els = [C.rect_at(0, 0, W, H, P["bg"]),
           # ---- header ----
           C.rect_at(0, 0, W, 140, P["head"]),
           C.text_el(60, 24, 420, 34, "叠光 · 发布演练", 24, P["head_brand"]),
           C.text_el(60, 56, 900, 58, "发布日执行泳道 · 双团队作战计划", 42,
                     P["white"], bold=True),
           C.text_el(1160, 28, 700, 32,
                     "2026-11-07（周六）· 09:00–16:00 · +08:00",
                     24, P["head_soft"], align="RIGHT"),
           C.text_el(1000, 70, 860, 40,
                     "完工 13:20（第 260 分钟）· 截止缓冲 160 分钟", 26,
                     "#6EE7B7", bold=True, align="RIGHT"),
           # ---- time axis ----
           C.line_h(252, X(0), X(420) + 8, P["axis"], 2)]
    for h in range(0, 8):                       # hourly ticks 09:00..16:00
        m = h * 60
        els.append(C.line_v(X(m), 242, 252, P["axis"], 1.5))
        if h == 7:
            # keep 16:00 clear of the red deadline line at X(420)
            els.append(C.text_el(X(420) - 134, 258, 120, 30, C.clock(m), 20,
                                 P["muted"], align="RIGHT"))
        else:
            els.append(C.text_el(X(m) - 60, 258, 120, 30, C.clock(m), 20,
                                 P["muted"], align="CENTER"))
        if h < 7:
            els.append(C.line_v(X(m + 30), 246, 252, "#CBD5E1", 1.5))
    # finish / deadline marker chips (top zone, unaffected by lanes)
    els += [
        C.chip_el(X(260) - 74, 180, 148, 34, P["good"], "完工 13:20", 20,
                  P["white"], radius=8),
        C.chip_el(X(420) - 156, 180, 152, 34, P["bad"], "截止 16:00", 20,
                  P["white"], radius=8),
    ]
    # ---- lanes: bands, team chips, idle gaps ----
    for team in ("design", "engineering"):
        g = LANE[team]
        els.append(C.rect_at(250, g["band"], 1628, 260, P["white"], 14,
                             P["line"], 2))
        els.append(C.chip_el(46, g["band"] + 96, 196, 68, C.TEAM_SOFT[team],
                             "", 1, P["ink"], radius=12,
                             border=C.TEAM_BORDER[team]))
        els.append(C.text_el(46, g["band"] + 106, 196, 36, C.TEAM_CN[team], 26,
                             C.TEAM_COLOR[team], bold=True, align="CENTER"))
        els.append(C.text_el(46, g["band"] + 142, 196, 28, team, 20,
                             C.TEAM_COLOR[team], align="CENTER"))
        for gt, gs, ge in C.GAPS:
            if gt == team:
                els.append(C.rect_at(X(gs), g["block"], X(ge) - X(gs), BLK_H,
                                     P["gap"], 4, P["axis"], 1))
    # ---- gridlines + finish/deadline lines: AFTER bands (so visible), ----
    # ---- BEFORE blocks/captions (blocks cover, captions stay on top) ----
    for h in range(1, 8):
        els.append(C.line_v(X(h * 60), 296, 845, P["line"], 1))
    els.append(C.line_v(X(260), 178, 845, P["good"], 3))
    els.append(C.line_v(X(420), 178, 845, P["bad"], 3))
    # ---- pass 1: task blocks (+ seam covers at contiguous boundaries) ----
    for t in C.SCHEDULE:
        team = t["team"]
        g = LANE[team]
        x, w = X(t["s"]), C.r2((t["e"] - t["s"]) * PPM)
        els.append(C.rect_at(x, g["block"], w, BLK_H, C.TEAM_COLOR[team], 10))
        if any(u["team"] == team and u["e"] == t["s"] for u in C.SCHEDULE):
            # fill the white bowtie left by both blocks' rounded corners
            els.append(C.rect_at(C.r2(x - 11), g["block"], 22, BLK_H,
                                 C.TEAM_COLOR[team], 0))
        els.append(C.text_el(x, g["block"] + 40, w, 32, t["id"], 24,
                             P["white"], bold=True, align="CENTER"))
        if t["risk"]:
            els.append(C.chip_el(C.r2(x + w - 52), g["block"] + 6, 46, 28,
                                 P["bad_soft"], t["risk"], 20, P["bad"],
                                 radius=6, border=P["bad_border"]))
    # ---- pass 2: captions (drawn over gridlines/finish line) ----
    for t in C.SCHEDULE:
        g = LANE[t["team"]]
        x = X(t["s"])
        row = g["rowA"] if ROW_OF[t["id"]] == "A" else g["rowB"]
        els.append(C.text_el(x, row, 240, 30, t["label"], 20, P["ink2"],
                             bold=True))
        els.append(C.text_el(x, row + 26, 260, 30,
                             "%s · %s" % (C.timespan(t), C.duration(t)), 20,
                             P["muted"]))
        els.append(C.text_el(x, row + 52, 260, 30, C.deps_text(t), 20,
                             P["faint"]))
    # ---- footer cards: every line must fit one line inside 570px at 20px ----
    cards = [
        (40, "图例与标记", [
            "浅灰块 = 空档：设计 10:25–10:30、工程 12:20–12:25",
            "绿线 = 完工 13:20 · 红线 = 截止 16:00 · 时刻按同尺度真实绘制",
            "K 徽标 = 风险任务（K1 R02 / K2 R05 / K3 R10），见决策简报",
        ]),
        (660, "下界与最优性", [
            "关键路径下界 255min：R01→R04→R07→R09→R10→R12",
            "工作量下界 485/2 = 242.5min · 穷举 8 分队 × 112 组次序",
            "本排程 260min ⇒ 全局最优（枚举证明）· 缓冲 160min",
        ]),
        (1280, "约束与选择", [
            "半开区间 [start,end)；同团队不并行、不抢占、切换无耗时",
            "R05→工程 10:00–10:30 · R09/R12→设计（各选一队）",
            "依赖以块下方编号索引标注（不画跨线遮挡时间块）",
        ]),
    ]
    for cx, title, lines in cards:
        els.append(C.rect_at(cx, 862, 600 if cx < 1280 else 598, 176,
                             P["white"], 12, P["line"], 2))
        els.append(C.text_el(cx + 20, 878, 560, 34, title, 24, P["ink"],
                             bold=True))
        for i, ln in enumerate(lines):
            els.append(C.text_el(cx + 20, 916 + i * 34, 570, 32, ln, 20,
                                 P["muted"]))
    return C.wrap_el("".join(els), W, H, P["bg"])


if __name__ == "__main__":
    errs = C.check_schedule()
    assert not errs, errs
    dsl = emit()
    out = "tmp/run-20261011-01/A24/execution-board.snapshot"
    open(out, "w", encoding="utf-8").write(dsl)
    print("board dsl written:", out, len(dsl), "chars,",
          len(dsl.encode("utf-8")), "bytes")
