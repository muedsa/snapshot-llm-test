# -*- coding: utf-8 -*-
"""A24 decision brief (1200x1600): KPIs, dependency DAG, rationale, risks.

Fixes vs baseline: DAG edges are explicit polylines routed through node-free
corridors (the old elbow helper drew horizontals straight through R07/R09);
rationale is 8 short lines (4 items x 2) because a 24px line longer than
1120px wraps and a 36px-high box clips the tail (observed in board-02/brief-02).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a24_common as C  # noqa: E402

W, H = 1200, 1600
P = C.PAL

# DAG node boxes: layer -> [(id, left), ...]; node height 54, pitch 74
NODE_W, NODE_H, PITCH, TOP0 = 270, 54, 74, 398
LAYERS = [
    [("R01", 150), ("R02", 720)],
    [("R04", 110), ("R05", 420), ("R03", 780)],
    [("R07", 250), ("R06", 780)],
    [("R09", 250), ("R08", 640)],
    [("R10", 250), ("R11", 640)],
    [("R12", 440)],
]


def node(tid):
    for li, layer in enumerate(LAYERS):
        for nid, x in layer:
            if nid == tid:
                return x, TOP0 + li * PITCH
    raise KeyError(tid)


def cx(tid):
    return node(tid)[0] + NODE_W / 2.0


def bot(tid):
    x, y = node(tid)
    return y + NODE_H


def top(tid):
    return node(tid)[1]


def polyline(pts, color="#94A3B2", thick=2):
    """Orthogonal path through explicit points + diamond head at the end."""
    els = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if abs(x1 - x2) < 0.01:
            els.append(C.line_v(x1, min(y1, y2), max(y1, y2), color, thick))
        else:
            els.append(C.line_h(min(y1, y2), min(x1, x2), max(x1, x2),
                                color, thick))
    hx, hy = pts[-1]
    els.append(C.diamond_el(hx, hy + 2, 11, color))
    return "".join(els)


def arrow(pid, cid, elbow=None, detour_x=None, detour_y=None):
    """Parent bottom -> child top. detour_x/y: corridor route for skip-layer
    edges so the path never crosses an intermediate node box."""
    px, pb = cx(pid), bot(pid)
    ct, ccx = top(cid), cx(cid)
    if detour_x is not None:
        y1 = elbow if elbow is not None else pb + 10
        y2 = detour_y
        pts = [(px, pb), (px, y1), (detour_x, y1), (detour_x, y2),
               (ccx, y2), (ccx, ct - 6)]
    elif abs(px - ccx) < 0.01:
        pts = [(px, pb), (px, ct - 6)]
    else:
        e = elbow if elbow is not None else (pb + ct) / 2.0
        pts = [(px, pb), (px, e), (ccx, e), (ccx, ct - 6)]
    return polyline(pts)


def emit():
    els = [C.rect_at(0, 0, W, H, P["bg_brief"]),
           # ---- header ----
           C.rect_at(0, 0, W, 170, P["head"]),
           C.text_el(60, 30, 420, 34, "叠光 · 发布演练", 24, P["head_brand"]),
           C.text_el(60, 62, 800, 64, "发布作战 · 决策简报", 46, P["white"],
                     bold=True),
           C.text_el(60, 124, 700, 34,
                     "2026-11-07 · 09:00 开工 · 16:00 截止 · 双团队单线程", 24,
                     P["head_soft"]),
           C.text_el(760, 124, 380, 34, "与执行图/行动卡同一排程", 24,
                     "#6EE7B7", align="RIGHT")]
    # ---- KPI row ----
    kpis = [("总工时", "485 min", "12 任务合计"),
            ("完工时间", "13:20", "窗口第 260 分钟"),
            ("剩余缓冲", "160 min", "占窗口 38.1%"),
            ("任务纳入", "12 / 12", "全在 420min 内")]
    for i, (lab, val, sub) in enumerate(kpis):
        x = 40 + i * 276
        els.append(C.rect_at(x, 190, 262, 140, P["white"], 12, P["line"], 2))
        els.append(C.text_el(x + 18, 204, 226, 32, lab, 24, P["muted"]))
        els.append(C.text_el(x + 18, 238, 226, 52, val, 40, P["ink"], bold=True))
        els.append(C.text_el(x + 18, 294, 226, 30, sub, 24, P["faint"]))
    # ---- dependency DAG ----
    els.append(C.text_el(40, 346, 900, 44, "依赖概览（编号索引 · 无跨线遮挡）",
                         32, P["ink"], bold=True))
    for layer in LAYERS:
        for tid, x in layer:
            t = C.BY_ID[tid]
            ny = node(tid)[1]
            els.append(C.rect_at(x, ny, NODE_W, NODE_H, P["white"], 10,
                                 C.TEAM_BORDER[t["team"]], 2))
            els.append(C.rect_at(x + 14, ny + 19, 16, 16,
                                 C.TEAM_COLOR[t["team"]], 4))
            els.append(C.text_el(x + 40, ny + 10, 220, 36,
                                 "%s %s" % (tid, t["label"]), 24, P["ink"],
                                 bold=True))
    # edges: (parent, child, elbow, detour_x, detour_y)
    # corridor gaps: L1-L2 452..472 (462), L2-L3 526..546 (536),
    # L3-L4 600..620 (610), L4-L5 674..694 (684), L5-L6 748..768 (758)
    edges = [
        ("R01", "R04", 462, None, None), ("R01", "R05", 462, None, None),
        ("R02", "R03", 462, None, None), ("R03", "R06", None, None, None),
        ("R04", "R07", 536, None, None), ("R05", "R07", 536, None, None),
        ("R06", "R08", 610, None, None),
        ("R04", "R08", 610, None, None),   # long: down x=245 (clear of R07
        #                                   at 250), across y=610 under R07
        ("R07", "R09", None, None, None),
        ("R07", "R10", 606, 70, 678),       # skip-layer via left margin
        ("R09", "R10", None, None, None),
        ("R08", "R10", 684, None, None),
        ("R09", "R11", 684, None, None),
        ("R08", "R11", None, None, None),
        ("R10", "R12", 758, None, None), ("R11", "R12", 758, None, None),
    ]
    for pid, cid, el, dx, dy in edges:
        els.append(arrow(pid, cid, elbow=el, detour_x=dx, detour_y=dy))
    els.append(C.text_el(40, 832, 1120, 30,
                         "图例：indigo 边框 = design · cyan 边框 = engineering "
                         "· 箭头 = 先决完成 → 后继开始",
                         24, P["muted"]))
    # ---- rationale: 4 items x 2 lines (each line < 1100px at 24px) ----
    els.append(C.text_el(40, 876, 900, 44, "排程依据（可核验最优）", 32,
                         P["ink"], bold=True))
    rationale = [
        "① 下界（忽略资源约束）：依赖关键路径 255min"
        "（R01→R04→R07→R09→R10→R12）",
        "总工作量 485/2 = 242.5min（两团队工作量下界，按原值记录、不提前取整）。",
        "② 关键抉择 R05（可任选一队）：归设计则设计串行 ≥115min 才起 R07，"
        "全案 ≥285min；",
        "归工程（10:00–10:30）则 R07 提前至 10:30 起，是全案最早的可行起点。",
        "③ 穷举 8 种分队方案 × 112 组队内拓扑次序（半开占用 + 依赖前序校验）：",
        "最小完工 = 260min；本排程达成 260min ⇒ 即为可核验的全局最优值。",
        "④ 空档仅 2 段 × 5min（设计 10:25–10:30、工程 12:20–12:25）；",
        "缓冲 160min 供 K3 返工与归档；R05→工程、R09/R12→设计（各选一队）。",
    ]
    for i, ln in enumerate(rationale):
        item, sub = divmod(i, 2)
        y = 928 + item * 72 + sub * 32
        els.append(C.text_el(40 if sub == 0 else 76, y, 1120 if sub == 0 else 1084,
                             30, ln, 24, P["muted"]))
    # ---- risks ----
    els.append(C.text_el(40, 1220, 900, 44, "三风险与对策", 32, P["ink"],
                         bold=True))
    for i, r in enumerate(C.RISKS):
        y = 1270 + i * 74
        els.append(C.rect_at(40, y, 1120, 66, P["white"], 10, P["line"], 2))
        els.append(C.rect_at(40, y, 6, 66, P["bad"], 3))
        els.append(C.chip_el(60, y + 13, 56, 40, P["bad_soft"], r["id"], 24,
                             P["bad"], radius=8, border=P["bad_border"],
                             border_w=1))
        els.append(C.text_el(130, y + 6, 1010, 30,
                             "%s（%s）· %s" % (r["task"],
                                               C.BY_ID[r["task"]]["label"],
                                               r["impact"]), 24, P["ink2"]))
        els.append(C.text_el(130, y + 36, 1010, 30,
                             "对策 → %s" % r["mitigation"], 24, P["muted"]))
    # ---- footer ---- (line1 is ~1000px: full width, brand lives in header)
    els.append(C.rect_at(40, 1508, 1120, 2, P["line"]))
    els.append(C.text_el(40, 1520, 1120, 34,
                         "三图同源：execution-board / decision-brief / "
                         "action-card ← 同一 schedule.json", 24, P["faint"]))
    els.append(C.text_el(40, 1554, 1120, 34,
                         "缓冲 = 420 − 260 = 160min；完工 13:20 ≤ 截止 16:00；"
                         "全部 end−start 严格等于输入 minutes", 24, P["faint"]))
    return C.wrap_el("".join(els), W, H, P["bg_brief"])


if __name__ == "__main__":
    errs = C.check_schedule()
    assert not errs, errs
    dsl = emit()
    out = "tmp/run-20261011-01/A24/decision-brief.snapshot"
    open(out, "w", encoding="utf-8").write(dsl)
    print("brief dsl written:", out, len(dsl), "chars,",
          len(dsl.encode("utf-8")), "bytes")
