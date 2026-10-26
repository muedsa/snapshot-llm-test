#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A24 · 三张成品图的 DSL 生成器。

execution-board 1920×1080：双团队泳道执行图（同尺度时间轴、空档、截止线、依赖索引）
decision-brief  1200×1600：决策简报（KPI、依赖概览 DAG、排程总览、风险、依据）
action-card      720×1280：手机行动卡（按时间序 12 任务、团队、起止、风险提醒）

三图全部读取 a24_common 的同一份排程（selected()），保证不互相矛盾。
所有几何由参数计算，文字宽度用 text_w 估算排版预算，成图后必须实际查看。
"""
from __future__ import annotations

import a24_common as C

W_BOARD, H_BOARD = 1920, 1080
W_BRIEF, H_BRIEF = 1200, 1600
W_CARD, H_CARD = 720, 1280

# =============================================================== 执行图
BX0, BX1 = 310.0, 1868.0          # 时间轴左右端（09:00 / 16:00）
BS = (BX1 - BX0) / C.WINDOW       # px / 分钟


def bx(minute: float) -> float:
    return BX0 + minute * BS


def board_dsl() -> str:
    S = C.sched_map()
    TM = C.task_map()
    lanes = [("design", 218.0), ("engineering", 490.0)]
    lane_h = 256.0
    nodes: list[str] = []

    # ---- 顶部品牌与标题
    nodes.append(C.rect(0, 0, 960, 8, C.DESIGN))
    nodes.append(C.rect(960, 0, 960, 8, C.ENG))
    nodes.append(C.text_node(C.BRAND, 44, 26, 560, 32, 24, C.DESIGN, style="BOLD"))
    nodes.append(C.text_node(C.TITLE_BOARD, 44, 58, 900, 52, 40, C.INK, style="BOLD"))
    nodes.append(C.text_node(
        f"{C.DATE_LINE} · 420 分钟连续窗口 · 双团队各一、同团队不可并行",
        44, 116, 1150, 30, 22, C.MUTED))

    # ---- 右上指标 pills
    pills = [("完工 13:20 · 260 分钟", C.DONE, C.DONE_L),
             ("剩余缓冲 160 分钟", C.DONE, C.DONE_L),
             ("关键路径 255 分钟", C.DESIGN, C.DESIGN_L),
             ("总工作量 485 分钟", C.DESIGN, C.DESIGN_L)]
    px = 1876.0
    for row in (0, 1):
        py = 30.0 + row * 50.0
        cx = px
        for text, fg, bg in reversed(pills[row * 2:row * 2 + 2]):
            w = C.text_w(text, 22) + 36
            cx -= w
            nodes.append(C.rect(cx, py, w, 42, bg, 21))
            nodes.append(C.text_node(text, cx, py + 8, w, 30, 22, fg,
                                     align="CENTER", style="BOLD"))
            cx -= 12

    # ---- 时间轴
    nodes.append(C.hline(BX0, 182, BX1 - BX0, "#CBD5E1", 2))
    for m in range(0, C.WINDOW + 1, 30):
        x = bx(m)
        if m % 60 == 0:
            nodes.append(C.vline(x, 172, 10, "#94A3B8", 2))
            lab = C.hhmm(m)
            if m == C.WINDOW:
                nodes.append(C.text_node(lab, x - 108, 188, 108, 28, 20,
                                         C.DEAD, align="RIGHT", style="BOLD"))
            else:
                nodes.append(C.text_node(lab, x - 50, 188, 100, 28, 20, C.MUTED,
                                         align="CENTER"))
        else:
            nodes.append(C.vline(x, 176, 6, "#CBD5E1", 1.5))
    nodes.append(C.text_node("13:20 完工", bx(C.MAKESPAN) - 278, 754, 268, 28,
                             20, C.DONE, align="RIGHT", style="BOLD"))
    nodes.append(C.text_node("16:00 截止线", BX1 - 268, 754, 268, 28, 20, C.DEAD,
                             align="RIGHT", style="BOLD"))

    # ---- 两个泳道
    for team, ly in lanes:
        nodes.append(C.rect(44, ly, 1832, lane_h, C.BORDER, 14))
        nodes.append(C.rect(46, ly + 2, 1828, lane_h - 4, C.PANEL, 12))
        # 左侧团队标签列
        nodes.append(C.text_node(team, 70, ly + 26, 200, 36, 26,
                                 C.TEAM_COLOR[team], style="BOLD"))
        nodes.append(C.text_node(C.TEAM_CN[team], 70, ly + 64, 200, 30, 22, C.INK2))
        load = sum(TM[t]["minutes"] for t in TM if S[t]["team"] == team)
        cnt = sum(1 for t in TM if S[t]["team"] == team)
        nodes.append(C.text_node(f"{cnt} 项 · {load} 分钟", 70, ly + 96, 210, 28,
                                 20, C.MUTED))
        nodes.append(C.vline(280, ly + 18, 162, C.BORDER, 1.5))
        # 网格线
        for m in range(0, C.WINDOW + 1, 30):
            nodes.append(C.vline(bx(m), ly + 10, 236,
                                 C.GRID if m % 60 == 0 else C.GRID_MINOR, 1.5))
        # 空档带（团队空闲区间）
        iv = sorted((S[t]["start_minute"], S[t]["end_minute"]) for t in TM
                    if S[t]["team"] == team)
        prev = 0
        gaps = []
        for s, e in iv:
            if s > prev:
                gaps.append((prev, s))
            prev = max(prev, e)
        if prev < C.WINDOW:
            gaps.append((prev, C.WINDOW))
        for gs, ge in gaps:
            nodes.append(C.rect(bx(gs) + 0.75, ly + 10.75, bx(ge) - bx(gs) - 1.5,
                                234.5, C.IDLE, 8))
        # 尾部空档标签
        tail = gaps[-1] if gaps and gaps[-1][1] == C.WINDOW else None
        if tail:
            label = (f"完工后缓冲 {C.BUFFER} 分钟"
                     if team == "design"
                     else f"R11 后空闲至截止 · {C.WINDOW - tail[0]} 分钟")
            nodes.append(C.text_node(label, bx(tail[0]), ly + 116,
                                     bx(tail[1]) - bx(tail[0]), 30, 20, C.MUTED,
                                     align="CENTER"))
        # 任务块 + 上下交替callout
        tl = sorted([t for t in TM if S[t]["team"] == team],
                    key=lambda t: (S[t]["start_minute"], t))
        bar_y = ly + 112
        for i, tid in enumerate(tl):
            t = TM[tid]
            s0, e0 = S[tid]["start_minute"], S[tid]["end_minute"]
            x, w = bx(s0), (e0 - s0) * BS
            nodes.append(C.rect(x, bar_y, w, 64, C.TEAM_COLOR[team], 10))
            nodes.append(C.text_node(tid, x, bar_y + 16, w, 34, 25, "#FFFFFF",
                                     align="CENTER", style="BOLD"))
            # callout
            flex = "（柔性）" if len(t["teams"]) > 1 else ""
            l1 = f"{tid} {t['label']}{flex}"
            l2 = f"{C.hhmm(s0)}–{C.hhmm(e0)} · {t['minutes']} 分钟"
            cx = x + w / 2
            w1 = C.text_w(l1, 20) + 16
            w2 = C.text_w(l2, 20) + 16
            if i % 2 == 0:
                ty = ly + 22
                nodes.append(C.vline(cx, ty + 52, bar_y - (ty + 52),
                                     C.TEAM_BORDER[team], 1.5))
            else:
                ty = ly + 190
                nodes.append(C.vline(cx, bar_y + 64, ty - (bar_y + 64),
                                     C.TEAM_BORDER[team], 1.5))
            nodes.append(C.text_node(l1, cx - w1 / 2, ty, w1, 28, 20, C.INK,
                                     align="CENTER", style="BOLD"))
            nodes.append(C.text_node(l2, cx - w2 / 2, ty + 28, w2, 26, 20,
                                     C.MUTED, align="CENTER"))

    # ---- 完工线 / 截止线（泳道之后绘制，避免被泳道面板遮盖）
    nodes.append(C.vline(bx(C.MAKESPAN), 170, 746 - 170, C.DONE, 2.5))
    nodes.append(C.vline(BX1, 170, 746 - 170, C.DEAD, 3))

    # ---- 依赖索引
    nodes.append(C.text_node("依赖索引", 44, 770, 130, 36, 26, C.INK, style="BOLD"))
    nodes.append(C.text_node("以编号表达依赖，不画交叉线，避免遮盖时间块", 172, 776,
                             760, 28, 20, C.MUTED))
    cw = (1832 - 5 * 14) / 6
    for i, tid in enumerate(sorted(TM)):
        col, row = i % 6, i // 6
        x = 44 + col * (cw + 14)
        y = 812 + row * 80
        team = S[tid]["team"]
        nodes.append(C.rect(x, y, cw, 68, C.BORDER, 10))
        nodes.append(C.rect(x + 1, y + 1, cw - 2, 66, C.PANEL, 9))
        nodes.append(C.rect(x + 10, y + 12, 6, 44, C.TEAM_COLOR[team], 3))
        nodes.append(C.text_node(f"{tid} {TM[tid]['label']}", x + 24, y + 9,
                                 cw - 34, 28, 20, C.INK, style="BOLD"))
        nodes.append(C.text_node(C.dep_text(tid), x + 24, y + 37, cw - 34, 26,
                                 20, C.MUTED))

    # ---- 图例与说明
    ly = 976
    lx = 44
    items = [(C.DESIGN, "design 设计团队 · 255 分钟"),
             (C.ENG, "engineering 工程团队 · 230 分钟"),
             (C.IDLE, "团队空档（含 5 分钟衔接等待）")]
    for color, text in items:
        nodes.append(C.rect(lx, ly + 4, 20, 20, color, 5))
        nodes.append(C.text_node(text, lx + 28, ly, 460, 28, 20, C.INK2))
        lx += 28 + C.text_w(text, 20) + 34
    nodes.append(C.vline(lx, ly + 2, 24, C.DEAD, 3))
    nodes.append(C.text_node("16:00 截止线", lx + 10, ly, 180, 28, 20, C.INK2))
    lx += 10 + C.text_w("16:00 截止线", 20) + 34
    nodes.append(C.vline(lx, ly + 2, 24, C.DONE, 2.5))
    nodes.append(C.text_node("13:20 完工线", lx + 10, ly, 180, 28, 20, C.INK2))
    nodes.append(C.text_node(
        "R05 · R09 · R12 为双团队可选项（本排程：R05→engineering，R09/R12→design）；"
        "design 12:20–12:25 等 R08、engineering 09:20–09:25 等 R01，各空档 5 分钟",
        44, 1012, 1832, 28, 20, C.MUTED))
    nodes.append(C.text_node("叠光 · 发布演练 · 发布作战执行图 · 排程来源 schedule.json",
                             44, 1046, 900, 28, 20, C.FAINT))
    nodes.append(C.text_node("与 decision-brief / action-card 使用同一排程，时间同尺度",
                             984, 1046, 892, 28, 20, C.FAINT, align="RIGHT"))
    return C.snapshot(W_BOARD, H_BOARD, nodes)


# =============================================================== 决策简报
# 垂直预算（1200x1600）：
#   0-156 头部 | 170-294 KPI | 308-732 依赖概览（6 层行式 DAG）
#   752-936 排程总览 | 956-1304 风险与对策 | 1324-1544 排程依据 | 1558 页脚
DAG_COL_X = [48.0, 408.0, 768.0]      # 3 列，列宽 340，列间通道 20px
DAG_NW, DAG_NH = 340.0, 46.0
DAG_ROW_Y = [386.0 + i * 60.0 for i in range(6)]
DAG_LAYERS = [["R01", "R02"], ["R04", "R05", "R03"], ["R07", "R06"],
              ["R09", "R08"], ["R10", "R11"], ["R12"]]
# 手工布线：垂直段走列间/左侧通道，水平段走行间空隙；仅 1 处箭头相交
DAG_EDGES = {
    ("R01", "R04"): [(178, 432), (178, 446)],
    ("R01", "R05"): [(258, 432), (258, 442), (578, 442), (578, 446)],
    ("R02", "R03"): [(530, 432), (530, 438), (938, 438), (938, 446)],
    ("R04", "R07"): [(178, 492), (178, 506)],
    ("R05", "R07"): [(530, 492), (530, 505), (310, 505), (310, 506)],
    ("R03", "R06"): [(938, 492), (938, 500), (626, 500), (626, 506)],
    ("R04", "R08"): [(258, 492), (258, 504), (398, 504), (398, 560),
                     (478, 560), (478, 566)],
    ("R06", "R08"): [(578, 552), (578, 566)],
    ("R07", "R09"): [(218, 552), (218, 566)],
    ("R07", "R10"): [(178, 552), (178, 556), (28, 556), (28, 604),
                     (120, 604), (120, 626)],
    ("R08", "R10"): [(520, 612), (520, 618), (310, 618), (310, 626)],
    ("R08", "R11"): [(640, 612), (640, 626)],
    ("R09", "R10"): [(218, 612), (218, 626)],
    ("R09", "R11"): [(258, 612), (258, 622), (578, 622), (578, 626)],
    ("R10", "R12"): [(218, 672), (218, 686)],
    ("R11", "R12"): [(578, 672), (578, 678), (310, 678), (310, 686)],
}


def _dag_nodes() -> list[str]:
    """分层行式 DAG：层为行、每层最多 3 列，节点单行 "ID 标签" 24px。"""
    S = C.sched_map()
    TM = C.task_map()
    out: list[str] = []
    pos: dict[str, tuple[float, float]] = {}
    for li, layer in enumerate(DAG_LAYERS):
        for ci, tid in enumerate(layer):
            pos[tid] = (DAG_COL_X[ci], DAG_ROW_Y[li])
    # 先画线（在节点下层）
    for (a, b), pts in DAG_EDGES.items():
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if abs(x0 - x1) < 0.01:
                out.append(C.rect(x0 - 0.75, min(y0, y1), 1.5, abs(y1 - y0),
                                  "#B6C2D4"))
            else:
                out.append(C.rect(min(x0, x1), y0 - 0.75, abs(x1 - x0), 1.5,
                                  "#B6C2D4"))
        ex, ey = pts[-1]
        out.append(C.rect(ex - 4, ey - 4, 8, 8, "#8FA3C0", 4))
    # 再画节点
    for tid, (x, y) in pos.items():
        team = S[tid]["team"]
        out.append(C.rect(x, y, DAG_NW, DAG_NH, C.TEAM_LIGHT[team], 10))
        out.append(C.rect(x, y + 7, 6, DAG_NH - 14, C.TEAM_COLOR[team], 3))
        out.append(C.text_node(f"{tid} {TM[tid]['label']}", x + 16, y + 8,
                               DAG_NW - 30, 30, 24, C.INK, style="BOLD"))
    return out


def brief_dsl() -> str:
    S = C.sched_map()
    TM = C.task_map()
    nodes: list[str] = []
    nodes.append(C.rect(0, 0, 600, 8, C.DESIGN))
    nodes.append(C.rect(600, 0, 600, 8, C.ENG))

    # ---- 头部
    nodes.append(C.text_node(C.BRAND, 48, 32, 600, 32, 24, C.DESIGN, style="BOLD"))
    nodes.append(C.text_node(C.TITLE_BRIEF, 48, 66, 900, 54, 42, C.INK, style="BOLD"))
    nodes.append(C.text_node(
        f"{C.DATE_LINE} · design / engineering 双团队 · 12 项任务",
        48, 126, 1050, 30, 24, C.MUTED))
    badge = "完工 13:20 · 260 分钟"
    bw = C.text_w(badge, 24) + 40
    nodes.append(C.rect(1152 - bw, 36, bw, 50, C.DONE_L, 25))
    nodes.append(C.text_node(badge, 1152 - bw, 48, bw, 32, 24, C.DONE,
                             align="CENTER", style="BOLD"))

    # ---- KPI 卡（副文控制在 224px 内，避免裁切）
    kpis = [("完工时间", "13:20", "09:00 起 260 分钟"),
            ("剩余缓冲", "160 分钟", "至 16:00 截止"),
            ("关键路径", "255 分钟", "仅依赖 · 不含资源"),
            ("总工作量", "485 分钟", "两团队合计")]
    kw = (1104 - 3 * 16) / 4
    for i, (lab, val, sub) in enumerate(kpis):
        x = 48 + i * (kw + 16)
        nodes.append(C.rect(x, 170, kw, 124, C.BORDER, 14))
        nodes.append(C.rect(x + 1, 171, kw - 2, 122, C.PANEL, 13))
        nodes.append(C.text_node(lab, x + 20, 186, kw - 40, 28, 24, C.MUTED))
        nodes.append(C.text_node(val, x + 20, 216, kw - 40, 44, 36, C.INK,
                                 style="BOLD"))
        nodes.append(C.text_node(sub, x + 20, 266, kw - 40, 28, 24, C.MUTED))

    # ---- 依赖概览（分层行式 DAG）
    nodes.append(C.text_node("依赖概览", 48, 308, 400, 38, 30, C.INK, style="BOLD"))
    nodes.append(C.text_node("12 项任务依赖关系；节点按执行团队着色，"
                             "R05 / R09 / R12 可双团队执行", 48, 346, 1050, 28,
                             24, C.MUTED))
    nodes.extend(_dag_nodes())

    # ---- 排程总览（迷你甘特，同一比例）
    nodes.append(C.text_node("排程总览", 48, 752, 400, 36, 28, C.INK, style="BOLD"))
    nodes.append(C.text_node("与执行图同一排程、同一时间比例（09:00–16:00 共 420 分钟）",
                             48, 788, 1050, 28, 24, C.MUTED))
    MX0, MX1 = 216.0, 1152.0
    MS = (MX1 - MX0) / C.WINDOW

    def mx(m: float) -> float:
        return MX0 + m * MS

    for m in range(0, C.WINDOW + 1, 60):
        nodes.append(C.vline(mx(m), 812, 90, C.GRID, 1.5))
    nodes.append(C.rect(mx(C.MAKESPAN), 812, MX1 - mx(C.MAKESPAN), 90, C.IDLE))
    nodes.append(C.vline(mx(C.MAKESPAN), 812, 90, C.DONE, 2))
    nodes.append(C.vline(MX1, 812, 90, C.DEAD, 2.5))
    for team, ly in (("design", 816.0), ("engineering", 858.0)):
        nodes.append(C.text_node(team, 48, ly + 6, 158, 28, 24,
                                 C.TEAM_COLOR[team], style="BOLD"))
        for tid in sorted(TM, key=lambda t: (S[t]["start_minute"], t)):
            if S[tid]["team"] != team:
                continue
            s0, e0 = S[tid]["start_minute"], S[tid]["end_minute"]
            x, w = mx(s0), (e0 - s0) * MS
            nodes.append(C.rect(x, ly, w, 36, C.TEAM_COLOR[team], 8))
            nodes.append(C.text_node(tid, x, ly + 4, w, 28, 24, "#FFFFFF",
                                     align="CENTER", style="BOLD"))
    for m in range(0, C.WINDOW + 1, 60):
        lab = C.hhmm(m)
        if m == C.WINDOW:
            nodes.append(C.text_node(f"{lab} 截止", mx(m) - 150, 908, 150, 28, 24,
                                     C.DEAD, align="RIGHT", style="BOLD"))
        else:
            nodes.append(C.text_node(lab, mx(m) - 50, 908, 100, 28, 24, C.MUTED,
                                     align="CENTER"))
    # 完工标签放入完工线右侧空档带，避免与 14:00 刻度重叠
    nodes.append(C.text_node("13:20 完工", mx(C.MAKESPAN) + 12, 824, 220, 28, 24,
                             C.DONE, style="BOLD"))

    # ---- 风险与对策
    nodes.append(C.text_node("风险与对策", 48, 956, 400, 36, 28, C.INK, style="BOLD"))
    fl = C.floats()
    risks = [
        ("K1", "R02", "服务限流导致等待", "保留响应并依据 Retry-After 重试",
         f"本排程浮动 {fl['R02']} 分钟"),
        ("K2", "R05", "长文案导致版式回归", "冻结文案后再完成适配",
         f"本排程浮动 {fl['R05']} 分钟"),
        ("K3", "R10", "实际图像暴露裁剪或比例错误", "预留返工缓冲，不跳过看图",
         "本排程浮动 0 分钟，返工将顺延完工"),
    ]
    for i, (kid, tid, impact, mit, note) in enumerate(risks):
        y = 1000 + i * 102
        nodes.append(C.rect(48, y, 1104, 100, C.BORDER, 12))
        nodes.append(C.rect(49, y + 1, 1102, 98, C.PANEL, 11))
        nodes.append(C.rect(48, y + 10, 6, 80, C.AMBER_B, 3))
        nodes.append(C.text_node(
            f"{kid} · {tid} {TM[tid]['label']} · {impact}", 74, y + 8, 1060, 30,
            24, C.INK, style="BOLD"))
        nodes.append(C.text_node(f"对策：{mit}", 74, y + 42, 1060, 30, 24, C.INK2))
        nodes.append(C.text_node(note, 74, y + 72, 1060, 26, 24, C.MUTED))

    # ---- 排程依据
    nodes.append(C.text_node("排程依据", 48, 1324, 400, 34, 28, C.INK, style="BOLD"))
    bullets = [
        "关键路径 255 分钟（仅依赖与时长，不含资源约束）：R01→R04→R07→R09→R10→R12",
        "资源工作量下界 242.5 分钟 = 总工作量 485 分钟 ÷ 2 个团队",
        "完工 260 分钟（13:20）优于两下界较大者 255 分钟仅 5 分钟；260 已由状态穷举证明为最优",
        "R05 交 engineering 在 R01 后立即执行以保住 design 关键链；R09、R12 归 design",
        "12 项均按题面完整时长执行；design 255 · engineering 230，两团队无并行占用",
        "总浮动 95 分钟；K1/K2 各 35 分钟、K3 对应 R10 浮动 0，以 160 分钟缓冲兜底",
    ]
    for i, b in enumerate(bullets):
        y = 1364 + i * 30
        nodes.append(C.rect(52, y + 12, 8, 8, C.DESIGN, 4))
        nodes.append(C.text_node(b, 74, y, 1070, 30, 24, C.INK2))

    nodes.append(C.text_node(
        "叠光 · 发布演练 · 发布日决策简报 · 与另两图同一 schedule.json",
        48, 1558, 1104, 28, 24, C.FAINT, align="CENTER"))
    return C.snapshot(W_BRIEF, H_BRIEF, nodes)


# =============================================================== 手机行动卡
def card_dsl() -> str:
    S = C.sched_map()
    TM = C.task_map()
    nodes: list[str] = []
    nodes.append(C.rect(0, 0, 360, 8, C.DESIGN))
    nodes.append(C.rect(360, 0, 360, 8, C.ENG))
    nodes.append(C.text_node(C.BRAND, 24, 26, 500, 32, 24, C.DESIGN, style="BOLD"))
    nodes.append(C.text_node(C.TITLE_CARD, 24, 60, 560, 50, 38, C.INK, style="BOLD"))
    nodes.append(C.text_node(C.DATE_LINE, 24, 116, 672, 28, 20, C.MUTED))

    stats = [("完工时间", "13:20"), ("剩余缓冲", "160 分钟"), ("任务总量", "12 项 · 485 分钟")]
    sw = (672 - 2 * 10) / 3
    for i, (lab, val) in enumerate(stats):
        x = 24 + i * (sw + 10)
        nodes.append(C.rect(x, 152, sw, 56, C.BORDER, 12))
        nodes.append(C.rect(x + 1, 153, sw - 2, 54, C.PANEL, 11))
        nodes.append(C.text_node(val, x, 160, sw, 26, 22, C.INK, align="CENTER",
                                 style="BOLD"))
        nodes.append(C.text_node(lab, x, 186, sw, 20, 20, C.MUTED, align="CENTER"))

    order = sorted(TM, key=lambda t: (S[t]["start_minute"], t))
    risk_of = {"R02": "K1", "R05": "K2", "R10": "K3"}
    y = 224.0
    for tid in order:
        t = TM[tid]
        s0, e0 = S[tid]["start_minute"], S[tid]["end_minute"]
        team = S[tid]["team"]
        risk = risk_of.get(tid)
        h = 94.0 if risk else 70.0
        nodes.append(C.rect(24, y, 672, h, C.BORDER, 12))
        nodes.append(C.rect(25, y + 1, 670, h - 2, C.PANEL, 11))
        nodes.append(C.rect(24, y + 8, 6, h - 16, C.TEAM_COLOR[team], 3))
        nodes.append(C.text_node(f"{tid} · {t['label']}", 44, y + 8, 460, 30, 24,
                                 C.INK, style="BOLD"))
        chip = "design" if team == "design" else "engineering"
        cw = C.text_w(chip, 20) + 28
        nodes.append(C.rect(696 - cw, y + 10, cw, 30, C.TEAM_LIGHT[team], 8))
        nodes.append(C.text_node(chip, 696 - cw, y + 14, cw, 24, 20,
                                 C.TEAM_COLOR[team], align="CENTER", style="BOLD"))
        nodes.append(C.text_node(
            f"{C.hhmm(s0)}–{C.hhmm(e0)} · {t['minutes']} 分钟 · {C.dep_text(tid)}",
            44, y + 40, 620, 26, 20, C.MUTED))
        if risk:
            nodes.append(C.rect(44, y + 64, 48, 28, C.AMBER_L, 6))
            nodes.append(C.text_node(risk, 44, y + 68, 48, 22, 20, C.AMBER,
                                     align="CENTER", style="BOLD"))
            nodes.append(C.text_node(
                _risk_text(risk), 102, y + 66, 590, 26, 20, C.INK2))
        y += h + 6

    nodes.append(C.text_node("叠光 · 发布演练 · 与执行图 / 简报使用同一排程", 24,
                             1240, 672, 28, 20, C.FAINT, align="CENTER"))
    return C.snapshot(W_CARD, H_CARD, nodes)


def _risk_text(kid: str) -> str:
    for r in C.release()["risks"]:
        if r["id"] == kid:
            return f"{r['impact']}；对策：{r['mitigation']}"
    return ""


if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    out = {
        "execution-board": board_dsl(),
        "decision-brief": brief_dsl(),
        "action-card": card_dsl(),
    }
    if which != "all":
        out = {which: out[which]}
    for name, dsl in out.items():
        p = C.TMP / f"{name}.snapshot"
        p.write_text(dsl, encoding="utf-8")
        print(f"{name}: {len(dsl.encode('utf-8'))} bytes -> {p}")
