#!/usr/bin/env python
# A24 三张图：1920×1080 执行泳道、1200×1600 决策简报、720×1280 手机行动卡。
# 三张图读同一份 schedule.json，任何数字都不在这里重新计算。
# 启动基准：总任务根 (suite_root)。用法：python build_a24.py [ver]
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
OUTD = ROOT / "outputs/run-20261011-01/A24"
DRAFTS = ROOT / "tmp/run-20261011-01/A24/drafts"

BRAND = "叠光 · 发布演练"
WINDOW = 420.0

# 版面留痕：三张图里每个关键元素的实际坐标都记在这里，
# 供 content-map.json 的「三图位置」字段直接引用，而不是事后估一个数。
MARKS = []


def mark(image, kind, key, box, **extra):
    MARKS.append({"image": image, "kind": kind, "key": key,
                  "box": [round(v, 2) for v in box], **extra})
C_BG = "#0B1020"
C_PANEL = "#131C31"
C_PANEL2 = "#1A2540"
C_LINE = "#2A3550"
C_INK = "#F1F5F9"
C_SUB = "#94A3B8"
C_DIM = "#64748B"
C_DESIGN = "#38BDF8"
C_ENG = "#FBBF24"
C_OK = "#34D399"
C_WARN = "#FB7185"
C_ACC = "#A78BFA"

# ---- 字宽系数（A14 实测标定）：用来判断文字是否放得进色块
EM = {"space": 0.28, ".": 0.40, ",": 0.40, "-": 0.56, "/": 0.40, ":": 0.42,
      "%": 0.90, "(": 0.40, ")": 0.40, "+": 0.70, "·": 1.00, "–": 1.00,
      "→": 1.00, "←": 1.00, "—": 1.00}
UP = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
LO = set("abcdefghijklmnopqrstuvwxyz")
DIG = set("0123456789")


def em_width(s: str, size: float) -> float:
    w = 0.0
    for ch in s:
        if ch == " ":
            w += EM["space"]
        elif ch in EM:
            w += EM[ch]
        elif ord(ch) > 0x2E80:
            w += 1.0
        elif ch in DIG:
            w += 0.53
        elif ch in UP:
            w += 0.70
        elif ch in LO:
            w += 0.60
        else:
            w += 0.56
    return w * size


def rect(x, y, w, h, color, radius=0, border=None):
    b = f' border="{border}"' if border else ""
    c = "" if color is None else f' color="{color}"'
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container width="{w:.2f}" height="{h:.2f}"{c} borderRadius="{radius}"{b}/>'
            f'</Positioned>')


def txt(t, x, y, w, h, size, color, weight="Inter Medium", align=None):
    q = "'" if '"' in t else '"'
    a = f' textAlign="{align}"' if align else ""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Text{a} fontSize="{size}" color="{color}" '
            f'fontFamily="{weight},Inter,Noto Sans CJK SC" text={q}{t}{q}/></Positioned>')


def wrap(text: str, size: float, width: float):
    """按实测字宽把文本切成不超过 width 的行。

    不依赖服务端的自动换行：服务端会把溢出盒子的行**静默裁掉**，
    所以这里自己排版、每行一个 Text，行高固定，行数由代码决定。
    CJK 可逐字断行；连续的 ASCII 词（如 Retry-After）尽量不拆。
    """
    lines, cur, cur_w = [], "", 0.0
    tokens, buf = [], ""
    for ch in text:
        if ord(ch) > 0x2E80 or ch == " ":
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(ch)
        else:
            buf += ch
    if buf:
        tokens.append(buf)
    for tk in tokens:
        w = em_width(tk, size)
        if cur and cur_w + w > width:
            lines.append(cur)
            cur, cur_w = tk, w
        else:
            cur += tk
            cur_w += w
    if cur:
        lines.append(cur)
    # CJK 悬挂标点：收尾的「。，、；：？！」等标点允许挂在上行末，
    # 否则会独占一行，首版「…而非产能。」的句号就被挤成了单独一行。
    hang = "。，、；：？！」』）】"
    merged = []
    for ln in lines:
        if merged and ln and ln[0] in hang:
            merged[-1] += ln[0]
            ln = ln[1:]
            if not ln:
                continue
        merged.append(ln)
    return merged


def bullets_dsl(b, items, x, y, w, size, line_h, gap, color, dot):
    """逐行渲染要点；返回下一行的 y。

    换行按 w−34 计算，但 Text 盒子给到 w−6：
    悬挂标点最多比换行宽度多出一个字（24px），盒子必须容得下它，
    否则服务端会把行尾标点静默裁掉。
    """
    for bl in items:
        for i, ln in enumerate(wrap(bl, size, w - 34)):
            if i == 0:
                b.append(rect(x + 2, y + 12, 8, 8, dot, 4))
            b.append(txt(ln, x + 26, y, w - 6, line_h, size,
                         color if i == 0 else C_INK))
            y += line_h
        y += gap
    return y


def load():
    s = json.loads((OUTD / "schedule.json").read_text(encoding="utf-8"))
    a = json.loads((OUTD / "schedule-audit.json").read_text(encoding="utf-8"))
    inp = json.loads((ROOT / "tasks/A24-release-plan-capstone/inputs/release.json")
                     .read_text(encoding="utf-8"))
    return s, a, inp


# ══════════════════════════════════════════════ 1) 执行泳道 1920×1080
def board_dsl(s, a, inp):
    W, H = 1920, 1080
    b = [rect(0, 0, W, H, C_BG)]
    tasks = {t["id"]: t for t in s["tasks"]}
    risks = {r["id"]: r for r in inp["risks"]}

    b.append(txt(BRAND, 56, 44, 700, 34, 26, C_ACC))
    b.append(txt("发布作战计划 · 执行泳道", 56, 84, 900, 58, 44, C_INK,
                 weight="Inter Semi Bold"))
    b.append(txt("发布日 2026-11-07 · 09:00 开工 · 16:00 截止 · design 与 engineering 各一个团队",
                 56, 148, 1200, 32, 22, C_SUB))
    b.append(txt("真实时间同尺度绘制；依赖以编号索引表达，未画交叉连线",
                 1160, 148, 704, 32, 22, C_DIM, align="END"))

    # KPI 条
    fin = s["finish_minute"]
    buf = s["buffer_minutes"]
    cp = a["lower_bounds"]["dependency_critical_path_minutes"]
    work = a["lower_bounds"]["total_work_minutes"]
    kpis = [("完工", s["finish_time"][11:16], C_OK, f'完工分钟 {fin:g}'),
            ("剩余缓冲", f"{buf:g} 分钟", C_ACC, f'420 − {fin:g}'),
            ("总工时", f"{work:g} 分钟", C_ENG, f'8 小时 05 分'),
            ("依赖关键路径", f"{cp:g} 分钟", C_DESIGN, "下界，未达")]
    kx = 56
    for i, (k, v, col, sub) in enumerate(kpis):
        x = kx + i * 458
        b.append(rect(x, 208, 434, 96, C_PANEL, 14))
        b.append(rect(x, 208, 6, 96, col, 3))
        b.append(txt(k, x + 24, 224, 240, 28, 22, C_SUB))
        b.append(txt(v, x + 24, 252, 280, 40, 30, col, weight="Inter Semi Bold"))
        b.append(txt(sub, x + 250, 258, 168, 30, 20, C_DIM, align="END"))

    # 时间轴与泳道
    # AX 取 352：KPI 卡在 208–304，轴标签在 AX−34 = 318，两者必须错开，
    # 否则「09:00…16:00」会压在 KPI 卡底边上。
    PX0, PX1 = 300, 1860
    PW = PX1 - PX0
    PPM = PW / WINDOW
    AX = 352                      # 轴标尺 y
    LY = {"design": 362, "engineering": 522}
    LANE_H = 140
    BLOCK_Y = 26                  # 色块相对泳道顶部的偏移
    BLOCK_H = 92

    for m in range(0, 421, 30):
        x = PX0 + m * PPM
        major = m % 60 == 0
        b.append(rect(x, AX, 2 if major else 1, 316, C_LINE if major else "#1E293B"))
        if major:
            hh = 9 + m // 60
            b.append(txt(f"{hh:02d}:00", x - 46, AX - 34, 92, 30, 20, C_SUB,
                         align="CENTER"))

    # 每个泳道先收集「标签放不进色块」的项，再统一决定标签位置：
    # 默认画在色块正上方的条带里（左对齐，允许向右溢出）；
    # 若与前一个条带标签相撞，就改画在本色块右侧的空档里。
    # 绝不在条带里画「+N 分钟偏移」——它会和相邻色块的条带标签抢位置。
    lane_items = {}
    for team in ("design", "engineering"):
        items = []
        for r in sorted(a["team_timelines"][team], key=lambda z: z["start_minute"]):
            t = tasks[r["id"]]
            bw = (r["end_minute"] - r["start_minute"]) * PPM
            need = em_width(t["label"], 20) + 20
            items.append({"t": t, "r": r, "x0": PX0 + r["start_minute"] * PPM,
                          "bw": bw, "external": need > bw, "need": need})
        lane_items[team] = items

    for team, color in (("design", C_DESIGN), ("engineering", C_ENG)):
        y = LY[team]
        b.append(rect(PX0, y, PW, LANE_H, C_PANEL, 12))
        b.append(txt(team, 56, y + 34, 210, 36, 26, color, weight="Inter Semi Bold"))
        tl = a["team_timelines"][team]
        mins = sum(x["end_minute"] - x["start_minute"] for x in tl)
        b.append(txt(f"{len(tl)} 项 · 占用 {mins:g} 分钟", 56, y + 76, 230, 28, 20, C_DIM))
        idle = [w for w in a["idle_windows"] if w["team"] == team and w.get("tail")]
        if idle:
            tail = idle[0]
            x0 = PX0 + tail["from_minute"] * PPM
            b.append(rect(x0, y + 10, (PX1 - x0), LANE_H - 20, "#0F172A99", 8))
            # 右对齐到泳道右端：靠左放会压住 R12 这类「标签画在色块右侧」的标签
            idle_txt = f'空档 {tail["minutes"]:g} 分钟'
            iw = em_width(idle_txt, 22) + 24
            b.append(txt(idle_txt, PX1 - 20 - iw, y + 56, iw, 32, 22, C_DIM,
                         align="END"))

        items = lane_items[team]
        strip = []                       # 已占用的条带区间 [(x0, x1)]
        for k, it in enumerate(items):
            t, r = it["t"], it["r"]
            x0, bw = it["x0"], it["bw"]
            flex = len(t["eligible_teams"]) > 1
            bc = C_ACC if flex else color
            by = y + BLOCK_Y
            b.append(rect(x0, by, bw, BLOCK_H, C_PANEL2, 10, border=f'2 SOLID {bc}'))
            b.append(rect(x0, by, bw, 5, bc, 2))
            mark("execution-board", "task_block", t["id"],
                 (x0, by, x0 + bw, by + BLOCK_H), team=team, lane_y=y,
                 display_start=r["start_hhmm"], display_end=r["end_hhmm"],
                 start_minute=r["start_minute"], end_minute=r["end_minute"],
                 minutes=t["minutes"], flexible=flex)
            b.append(txt(t["id"], x0 + 12, by + 16, bw - 24, 30, 22, bc,
                         weight="Inter Semi Bold"))
            if not it["external"]:
                b.append(txt(t["label"], x0 + 12, by + 50, bw - 24, 28, 20, C_INK))
                mark("execution-board", "task_label", t["id"],
                     (x0 + 12, by + 50, x0 + bw - 12, by + 78), placement="in_block")
            else:
                nxt = items[k + 1]["x0"] if k + 1 < len(items) else PX1
                fits_strip = all(x0 + it["need"] <= p0 or x0 >= p1 for p0, p1 in strip)
                if fits_strip:
                    b.append(txt(t["label"], x0, y + 2, it["need"], 28, 20, C_INK))
                    strip.append((x0, x0 + it["need"]))
                    mark("execution-board", "task_label", t["id"],
                         (x0, y + 2, x0 + it["need"], y + 30),
                         placement="above_block_strip")
                elif x0 + bw + 8 + it["need"] <= nxt:
                    lx = x0 + bw + 8          # 放到色块右侧的空档里
                    b.append(txt(t["label"], lx, by + 32, it["need"], 28, 20, C_INK))
                    mark("execution-board", "task_label", t["id"],
                         (lx, by + 32, lx + it["need"], by + 60),
                         placement="right_of_block")
                else:
                    b.append(txt(t["label"], x0, y + 2, it["need"], 28, 20, C_INK))
                    strip.append((x0, x0 + it["need"]))
                    mark("execution-board", "task_label", t["id"],
                         (x0, y + 2, x0 + it["need"], y + 30),
                         placement="above_block_strip")

    # 完工线与截止线
    fx = PX0 + fin * PPM
    b.append(rect(fx, AX, 3, 316, C_OK))
    mark("execution-board", "finish_line", "finish", (fx, AX, fx + 3, AX + 316),
         finish_minute=fin, display=s["finish_time"][11:16])
    b.append(txt(f'完工 {s["finish_time"][11:16]}', fx - 120, AX + 322, 240, 30, 22,
                 C_OK, align="CENTER"))
    dx = PX1
    b.append(rect(dx, AX - 8, 4, 332, C_WARN))
    mark("execution-board", "deadline_line", "deadline", (dx, AX - 8, dx + 4, AX + 324),
         deadline="16:00", minute=WINDOW)
    # 截止标签放在底部行，避免和轴上的「16:00」标注重叠
    b.append(txt("截止 16:00", dx - 200, AX + 322, 200, 30, 22, C_WARN, align="END"))
    mark("execution-board", "axis", "time_axis", (PX0, AX, PX1, AX + 316),
         minute_to_px=round(PPM, 6), window_minutes=WINDOW)

    # 任务索引表（编号索引表达依赖）
    b.append(txt("任务索引 · 编号索引表达依赖", 56, 712, 700, 34, 24, C_INK,
                 weight="Inter Semi Bold"))
    b.append(txt("紫色描边 = 双选任务（design / engineering 均可）· 标签在色块内放不下时画在色块上方的条带里",
                 620, 714, 1244, 30, 20, C_DIM, align="END"))
    order = sorted(s["tasks"], key=lambda z: z["id"])
    for i, r in enumerate(order):
        col_i, row_i = i // 6, i % 6
        x = 56 + col_i * 906
        y = 758 + row_i * 50
        t = tasks[r["id"]]
        dep = "、".join(r["depends"]) if r["depends"] else "无"
        risk = [k for k, v in risks.items() if v["task"] == r["id"]]
        line = (f'{r["id"]} · {t["label"]} · {r["assigned_team"]} · '
                f'{r["start_hhmm"]}–{r["end_hhmm"]} · {r["minutes"]:g} 分钟 · 前置 {dep}')
        if len(t["eligible_teams"]) > 1:
            line += " · 双选"
        if risk:
            line += f' · 风险 {"、".join(risk)}'
        b.append(rect(x, y, 884, 44, C_PANEL, 8))
        b.append(rect(x, y, 5, 44, C_ACC if risk else C_LINE, 2))
        b.append(txt(line, x + 16, y + 8, 856, 28, 20,
                     C_WARN if risk else C_INK))
    return (f'<Snapshot type="png">\n<Container width="{W}" height="{H}" color="{C_BG}">'
            f'<Stack fit="EXPAND">{"".join(b)}</Stack></Container>\n</Snapshot>\n')


# ══════════════════════════════════════════════ 2) 决策简报 1200×1600
def brief_dsl(s, a, inp):
    W, H = 1200, 1600
    M = 48
    CW = W - 2 * M
    b = [rect(0, 0, W, H, C_BG)]
    fin = s["finish_minute"]
    buf = s["buffer_minutes"]
    lb = a["lower_bounds"]
    work = lb["total_work_minutes"]
    cp = lb["dependency_critical_path_minutes"]
    wb = lb["resource_workload_lower_bound_minutes"]

    b.append(txt(BRAND, M, 38, 800, 30, 24, C_ACC))
    b.append(txt("发布作战决策简报", M, 72, CW, 58, 44, C_INK,
                 weight="Inter Semi Bold"))
    b.append(txt("2026-11-07 · 09:00–16:00（420 分钟）· 双团队串行执行", M, 136,
                 CW, 32, 24, C_SUB))

    stats = [("完工时刻", s["finish_time"][11:16], f'第 {fin:g} 分钟', C_OK),
             ("剩余缓冲", f"{buf:g} 分钟", "占窗口 38.1%", C_ACC),
             ("总工时", f"{work:g} 分钟", "8 小时 05 分", C_ENG),
             ("关键路径下界", f"{cp:g} 分钟", "纯依赖，与资源无关", C_DESIGN)]
    for i, (k, v, sub, col) in enumerate(stats):
        x = M + i * (CW / 4)
        b.append(rect(x, 180, CW / 4 - 14, 146, C_PANEL, 14))
        b.append(rect(x, 180, CW / 4 - 14, 5, col, 2))
        b.append(txt(k, x + 20, 198, CW / 4 - 54, 28, 24, C_SUB))
        b.append(txt(v, x + 20, 230, CW / 4 - 54, 44, 34, col,
                     weight="Inter Semi Bold"))
        # 子标签放在 278、盒高 32，卡片加高到 326：24px 字的行高约 31px，
        # 首版 304+26 的盒子贴着 336 的卡底，实图上把下半截切掉了。
        b.append(txt(sub, x + 20, 278, CW / 4 - 40, 32, 24, C_DIM))

    # 依赖概览
    y = 352
    b.append(txt("一、依赖概览", M, y, CW, 40, 30, C_INK, weight="Inter Semi Bold"))
    b.append(txt("最后一列为前置任务编号，— 表示无前置；时长单位为分钟", M, y + 46,
                 CW, 30, 24, C_SUB))
    y += 90
    for i, t in enumerate(inp["tasks"]):
        col_i, row_i = i // 6, i % 6
        x = M + col_i * (CW / 2 + 6)
        yy = y + row_i * 54
        dep = "·".join(t["depends"]) if t["depends"] else "—"
        team = next(r["assigned_team"] for r in s["tasks"] if r["id"] == t["id"])
        col = C_DESIGN if team == "design" else C_ENG
        b.append(rect(x, yy, CW / 2 - 14, 50, C_PANEL, 10))
        b.append(rect(x, yy, 5, 50, col, 2))
        b.append(txt(t["id"], x + 16, yy + 10, 62, 30, 24, col,
                     weight="Inter Semi Bold"))
        b.append(txt(t["label"], x + 82, yy + 10, 200, 30, 24, C_INK))
        b.append(txt(f'{t["minutes"]:g}′', x + 288, yy + 10, 62, 30, 24, C_SUB))
        # 依赖列宽 176px：最宽的 "R07·R08·R09" 按实测字宽约 150px，放得下
        b.append(txt(dep, x + 352, yy + 10, 176, 30, 24, C_DIM))
        mark("decision-brief", "task_row", t["id"], (x, yy, x + CW / 2 - 14, yy + 50),
             display_depends=dep, minutes=t["minutes"], team=team)
    y += 6 * 54 + 16

    # 排程依据 + 最优性
    b.append(txt("二、排程依据与最优性", M, y, CW, 40, 30, C_INK,
                 weight="Inter Semi Bold"))
    y += 52
    y = bullets_dsl(b, [
        f'两个下界：依赖关键路径 {cp:g} 分钟，资源工作量下界 {wb:g} 分钟'
        f'（{work:g} ÷ 2）；约束来自依赖而非产能。',
        f'本排程完工 {fin:g} 分钟（{s["finish_time"][11:16]}），比依赖下界多 {fin - cp:g} 分钟。',
        '差距原因：R05 依赖 R01，design 在 25–85 已被 R04 占满，R05 只能给 engineering；'
        'engineering 按 R02→R05→R03→R06→R08 串行，R08 最早第 205 分钟结束，R10 与 R12 顺延。',
        '最优性：R05/R09/R12 的归属共 8 种，逐类做完备分支定界搜索，'
        '8 类最优 260/260/285/285/285/285/300/300，最小 260。',
        f'故 {fin:g} 分钟是可证明的全局最优：存在完工 {fin:g} 的可行解，且无更早的可行解。',
        '未改依赖、未缩时、未删环节；12 项任务、16 条依赖、485 分钟与输入逐项一致。',
    ], M, y, CW, 24, 34, 6, C_INK, C_ACC)
    y += 2

    # 风险与对策
    b.append(txt("三、风险与对策", M, y, CW, 40, 30, C_INK, weight="Inter Semi Bold"))
    y += 50
    assert y + 3 * 118 <= H - M, f"风险卡片超出画布：{y + 3 * 118} > {H - M}"
    for r in inp["risks"]:
        col = C_WARN
        mark("decision-brief", "risk_card", r["id"], (M, y, M + CW, y + 110),
             task=r["task"], impact=r["impact"], mitigation=r["mitigation"])
        # 24px 字的行高约 31px：三行从 y+10 / y+44 / y+70 排，末行到 y+101，
        # 卡片必须到 110 才容得下；首版 104 高的卡片把脚注下缘切掉了。
        b.append(rect(M, y, CW, 110, C_PANEL, 12))
        b.append(rect(M, y, 6, 110, col, 3))
        b.append(txt(f'{r["id"]} · {r["task"]} · {r["impact"]}', M + 24, y + 10,
                     CW - 48, 32, 24, col, weight="Inter Semi Bold"))
        b.append(txt(f'对策：{r["mitigation"]}', M + 24, y + 44, CW - 48, 32, 24, C_INK))
        b.append(txt("风险只用于解释缓冲可能被消耗到什么程度，未加进任何任务时长",
                     M + 24, y + 70, CW - 48, 30, 24, C_DIM))
        y += 118
    return (f'<Snapshot type="png">\n<Container width="{W}" height="{H}" color="{C_BG}">'
            f'<Stack fit="EXPAND">{"".join(b)}</Stack></Container>\n</Snapshot>\n')


# ══════════════════════════════════════════════ 3) 手机行动卡 720×1280
def card_dsl(s, a, inp):
    W, H = 720, 1280
    M = 32
    CW = W - 2 * M
    b = [rect(0, 0, W, H, C_BG)]
    tasks = {t["id"]: t for t in inp["tasks"]}
    risks = {}
    for r in inp["risks"]:
        risks.setdefault(r["task"], []).append(r)

    b.append(rect(0, 0, W, 146, C_PANEL, 0))
    b.append(txt(BRAND, M, 22, 400, 28, 22, C_ACC))
    b.append(txt("发布日行动卡", M, 54, CW, 44, 32, C_INK,
                 weight="Inter Semi Bold"))
    fin = s["finish_minute"]
    b.append(txt(f'09:00–16:00 · 完工 {s["finish_time"][11:16]} · '
                 f'缓冲 {s["buffer_minutes"]:g} 分钟', M, 106, CW, 26, 22, C_SUB))

    y = 162
    b.append(txt("按时间序的 12 项任务", M, y, CW, 36, 26, C_INK,
                 weight="Inter Semi Bold"))
    y += 42
    risk_ids = {k: [x["id"] for x in v] for k, v in risks.items()}
    for k, r in enumerate(sorted(s["tasks"], key=lambda z: (z["start_minute"], z["id"]))):
        t = tasks[r["id"]]
        col = C_DESIGN if r["assigned_team"] == "design" else C_ENG
        has_risk = r["id"] in risks
        b.append(rect(M, y, CW, 54, C_PANEL, 12))
        b.append(rect(M, y, 6, 54, col, 3))
        b.append(txt(r["id"], M + 18, y + 5, 64, 26, 22, col,
                     weight="Inter Semi Bold"))
        b.append(txt(t["label"], M + 86, y + 5, 260, 26, 22, C_INK))
        b.append(txt(f'{r["start_hhmm"]}–{r["end_hhmm"]}', M + 350, y + 5, 306, 26,
                     22, C_INK, align="END"))
        tag = "双选" if len(t["teams"]) > 1 else r["assigned_team"]
        b.append(txt(tag, M + 86, y + 29, 116, 24, 20, col))
        if has_risk:
            # 风险放在第二行右侧：首版放在第一行，与任务名重叠并被截断
            b.append(txt(f'⚠ {risks[r["id"]][0]["impact"]}', M + 200, y + 29,
                         440, 24, 20, C_WARN, align="END"))
        mark("action-card", "task_row", r["id"], (M, y, M + CW, y + 54),
             display_start=r["start_hhmm"], display_end=r["end_hhmm"],
             team=r["assigned_team"], tag=tag, risk=risk_ids.get(r["id"]),
             time_order_index=k + 1)
        y += 54

    y += 14
    b.append(txt("风险提醒", M, y, CW, 34, 26, C_INK, weight="Inter Semi Bold"))
    y += 44
    assert y + 3 * 88 <= H - M, f"风险卡超出画布：{y + 3 * 88} > {H - M}"
    for r in inp["risks"]:
        mark("action-card", "risk_card", r["id"], (M, y, M + CW, y + 80),
             task=r["task"], impact=r["impact"], mitigation=r["mitigation"])
        b.append(rect(M, y, CW, 80, C_PANEL, 12))
        b.append(rect(M, y, 6, 80, C_WARN, 3))
        b.append(txt(f'{r["id"]} · {r["task"]} · {r["impact"]}', M + 18, y + 10,
                     CW - 36, 28, 22, C_WARN, weight="Inter Semi Bold"))
        b.append(txt(f'对策：{r["mitigation"]}', M + 18, y + 44, CW - 36, 26, 20, C_SUB))
        y += 88
    return (f'<Snapshot type="png">\n<Container width="{W}" height="{H}" color="{C_BG}">'
            f'<Stack fit="EXPAND">{"".join(b)}</Stack></Container>\n</Snapshot>\n')


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    DRAFTS.mkdir(parents=True, exist_ok=True)
    s, a, inp = load()
    MARKS.clear()
    (DRAFTS / f"execution-board-{ver}.snapshot").write_text(
        board_dsl(s, a, inp), encoding="utf-8")
    (DRAFTS / f"decision-brief-{ver}.snapshot").write_text(
        brief_dsl(s, a, inp), encoding="utf-8")
    (DRAFTS / f"action-card-{ver}.snapshot").write_text(
        card_dsl(s, a, inp), encoding="utf-8")
    (DRAFTS / f"layout-marks-{ver}.json").write_text(
        json.dumps(MARKS, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"3 dsl + {len(MARKS)} marks | finish {s['finish_minute']} "
          f"buffer {s['buffer_minutes']}")


if __name__ == "__main__":
    main()
