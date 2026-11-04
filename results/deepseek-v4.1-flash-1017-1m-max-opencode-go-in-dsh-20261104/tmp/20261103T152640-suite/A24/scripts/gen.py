# -*- coding: utf-8 -*-
"""A24: three deliverables from the same schedule."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A24"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
SCH = json.loads((OUT / "schedule.json").read_text(encoding="utf-8"))
ROWS = SCH["tasks"]
BY = {r["id"]: r for r in ROWS}
REL = json.loads((SUITE_ROOT / "tasks" / "A24-release-plan-capstone" / "inputs" / "release.json")
                 .read_text(encoding="utf-8"))
RISK = {k["task"]: k for k in REL["risks"]}
MAKE = SCH["makespan_min"]
BUF = SCH["buffer_min"]
CP = 255

BG = "#0D141F"
PANEL = "#141E2C"
INK = "#EDF2F8"
INK2 = "#C3CEDC"
MUTED = "#7C8CA3"
ACCENT = "#F2B84B"
DES = "#2F6BFF"
ENG = "#16A34A"
WARN = "#E8892B"
LINE = "#22303F"
FONT = "Inter,Noto Sans CJK SC"

TXT = []
def T(page, key, x, y, text, w, size, color=INK, bold=False, align=None):
    TXT.append({"canvas": page, "key": key, "text": text, "box": [x, y, w], "size": size,
                "color": color, "bold": bold, "align": align or "LEFT"})
    return K.text(x, y, text, width=w, size=size, color=color, bold=bold, align=align, label=key)

COLOR = {"design": DES, "engineering": ENG}
SHORT = {"K1": "限流等待", "K2": "版式回归", "K3": "裁剪/比例"}

# ---------------------------------------------------------------- 1. execution board
def board():
    W, H = 1920, 1080
    p = [K.rect(0, 0, W, H, color=BG)]
    p.append(K.rect(0, 0, W, 6, color=ACCENT))
    p.append(T("board", "title", 40, 28, "叠光 · 发布演练 · 团队泳道执行图", 1100, 34, INK, True))
    p.append(T("board", "sub", 40, 76,
               f"2026-11-07 · 09:00 开工 → {SCH['makespan_clock']} 完成 · 截止 16:00 · "
               f"缓冲 {BUF} 分钟 · 全部 12 个任务", 1400, 20, MUTED))
    top, bottom = 200, 1010
    k = (bottom - top) / 420
    def y(m):
        return top + m * k
    # hour ticks
    for m in range(0, 421, 60):
        yy = round(y(m))
        p.append(K.rect(300, yy, 1580, 1, color=LINE))
        p.append(K.text(210, yy - 11, f"{9 + m // 60:02d}:00", width=84, size=18, color=MUTED,
                        align="RIGHT"))
    # lanes
    for i, (tm, col) in enumerate((("design", DES), ("engineering", ENG))):
        x = 320 + i * 790
        p.append(K.rect(x, top - 46, 760, bottom - top + 46, color=PANEL, radius=10))
        p.append(K.text(x + 16, top - 40, f"{tm.upper()} 团队", width=400, size=20, color=col,
                        bold=True))
    # deadline + makespan markers
    p.append(K.rect(300, bottom, 1580, 2, color="#E04B3A"))
    p.append(K.text(1600, bottom + 8, "16:00 截止", width=200, size=18, color="#E04B3A", bold=True))
    ym = round(y(MAKE))
    p.append(K.rect(300, ym, 1580, 1, color=ACCENT))
    p.append(K.text(1300, ym - 24, f"{SCH['makespan_clock']} 全部完成（{MAKE} 分钟）", width=380,
                    size=18, color=ACCENT, bold=True, align="RIGHT"))
    # gaps
    for tm in ("design", "engineering"):
        col = [r for r in ROWS if r["team"] == tm]
        col.sort(key=lambda r: r["start_min"])
        prev = 0
        for r in col:
            if r["start_min"] > prev:
                x = 320 + (0 if tm == "design" else 790)
                p.append(K.rect(x + 8, round(y(prev)), 744, max(2, round(y(r["start_min"]) - y(prev))),
                                color="#1B2635"))
                if r["start_min"] - prev >= 15:
                    p.append(K.text(x + 20, round(y(prev)) + 4, f"空档 {r['start_min'] - prev}′",
                                    width=300, size=16, color=MUTED))
            prev = max(prev, r["end_min"])
        if prev < MAKE:
            x = 320 + (0 if tm == "design" else 790)
            p.append(K.rect(x + 8, round(y(prev)), 744, max(2, round(y(MAKE) - y(prev))),
                            color="#1B2635"))
    # blocks
    for r in ROWS:
        x = 320 + (0 if r["team"] == "design" else 790)
        y0, y1 = y(r["start_min"]), y(r["end_min"])
        h = max(46, y1 - y0)
        col = COLOR[r["team"]]
        p.append(K.rect(x + 12, round(y0), 736, round(h), color=col + "26", radius=8,
                        border=f"1 SOLID {col}"))
        p.append(K.rect(x + 12, round(y0), 6, round(h), color=col, radius=3))
        p.append(T("board", f"block-{r['id']}-id", x + 28, round(y0) + 5, r["id"], 76, 20, col, True))
        p.append(T("board", f"block-{r['id']}-label", x + 100, round(y0) + 5, r["label"], 380, 20,
                   INK, True))
        dep = ("依赖 " + "、".join(r["deps"])) if r["deps"] else "无前置"
        if h >= 40:
            p.append(T("board", f"block-{r['id']}-meta", x + 28, round(y0) + 27,
                       f"{r['start']}–{r['end']} · {r['minutes']}′ · {dep}", 700, 15, INK2))
        if h > 92:
            p.append(T("board", f"block-{r['id']}-team", x + 32, round(y0) + 52,
                       f"执行团队：{r['team']}", 300, 16, MUTED))
        if r["id"] in RISK:
            p.append(T("board", f"block-{r['id']}-risk", x + 500, round(y0) + 27,
                       "风险 " + RISK[r["id"]]["id"], 120, 17, WARN, True))
    p.append(K.text(40, 1044, "同一服务区间 [start,end)；同团队不可并行；R05/R09/R12 可任选团队，"
                              "本排程 R05 归工程、R09/R12 归设计。", width=1500, size=18, color=MUTED))
    return K.document(W, H, p, background=BG)

# ---------------------------------------------------------------- 2. decision brief
def brief():
    W, H = 1200, 1600
    p = [K.rect(0, 0, W, H, color="#Fbfaf7")]
    p.append(K.rect(0, 0, W, 8, color=ACCENT))
    p.append(T("brief", "kicker", 48, 40, "叠光 · 发布演练 · 决策简报", 800, 22, "#B4451F", True))
    p.append(T("brief", "title", 48, 78, "12 个任务、2 个团队，260 分钟完成", 1100, 40, "#14181F", True))
    p.append(T("brief", "sub", 48, 132,
               "09:00 开工 → 13:20 交付，距 16:00 截止留有 160 分钟缓冲", 1100, 22, "#3C4552"))
    # KPI strip
    kpis = [("总工作量", "485 分钟"), ("关键路径", "255 分钟"), ("完工时间", "260 分钟"),
            ("剩余缓冲", "160 分钟")]
    for i, (a, b) in enumerate(kpis):
        x = 48 + i * 276
        p.append(K.rect(x, 186, 260, 92, color="#FFFFFF", radius=10, border="1 SOLID #E3E0D8"))
        p.append(T("brief", f"kpi-{i}-l", x + 16, 200, a, 220, 18, "#6B7686"))
        p.append(T("brief", f"kpi-{i}-v", x + 16, 226, b, 230, 28, "#14181F", True))
    # dependency overview
    p.append(T("brief", "dep-title", 48, 306, "依赖概览与排程", 600, 24, "#14181F", True))
    p.append(K.rect(48, 344, 1104, 560, color="#FFFFFF", radius=10, border="1 SOLID #E3E0D8"))
    hdr = [("任务", 68, 300), ("时长", 380, 100), ("前置", 490, 220), ("团队", 720, 180),
           ("起止", 910, 220)]
    for label, x, w in hdr:
        p.append(T("brief", f"h-{label}", x, 358, label, w, 18, "#6B7686", True))
    for i, r in enumerate(ROWS):
        y = 392 + i * 43
        p.append(T("brief", f"row-{r['id']}-id", 68, y, r["id"], 70, 20, "#14181F", True))
        p.append(T("brief", f"row-{r['id']}-label", 118, y, r["label"], 250, 20, "#14181F"))
        p.append(T("brief", f"row-{r['id']}-min", 380, y, f"{r['minutes']}′", 100, 20, "#3C4552"))
        p.append(T("brief", f"row-{r['id']}-dep", 490, y,
                   ("、".join(r["deps"]) if r["deps"] else "—"), 220, 19, "#3C4552"))
        p.append(T("brief", f"row-{r['id']}-team", 720, y, r["team"], 180, 19,
                   "#1D4ED8" if r["team"] == "design" else "#0F7A5A", True))
        p.append(T("brief", f"row-{r['id']}-time", 910, y, f"{r['start']}–{r['end']}", 220, 19,
                   "#3C4552"))
    p.append(T("brief", "cp-note", 48, 918,
               "关键链：R01 → R04 → R07 → R09 → R10 → R12 = 255 分钟；资源下界 = 485 / 2 = 242.5 分钟。",
               1100, 18, "#6B7686"))
    # risks
    p.append(T("brief", "risk-title", 48, 962, "三项风险与对策", 600, 24, "#14181F", True))
    for i, k in enumerate(REL["risks"]):
        y = 1000 + i * 96
        p.append(K.rect(48, y, 1104, 84, color="#FFF6E8", radius=10, border="1 SOLID #F0D9B5"))
        p.append(T("brief", f"risk-{k['id']}-t", 68, y + 10,
                   f"{k['id']} · {k['task']} {BY[k['task']]['label']}", 500, 20, "#8A4B12", True))
        p.append(T("brief", f"risk-{k['id']}-i", 68, y + 38, f"影响：{k['impact']}", 520, 18,
                   "#5A4632"))
        p.append(T("brief", f"risk-{k['id']}-m", 620, y + 38, f"对策：{k['mitigation']}", 520, 18,
                   "#5A4632"))
    # basis
    p.append(T("brief", "basis-title", 48, 1300, "排程依据", 600, 24, "#14181F", True))
    for i, line in enumerate([
        "1. 每个任务必须完整占用其 minutes（25–70 分钟），先决任务 end ≤ 后继 start。",
        "2. 同团队不可并行；R05/R09/R12 可任选团队，枚举 8 种组合后取 makespan 最小者。",
        "3. 本方案把 R05 交给工程（60–90），让设计连续做 R04→R07；R09、R12 留在设计。",
        f"4. 结果 {MAKE} 分钟，比关键路径下界 255 高 5 分钟；未做全局最优证明，只称可行且较优。",
    ]):
        p.append(T("brief", f"basis-{i}", 48, 1338 + i * 34, line, 1104, 19, "#3C4552"))
    p.append(T("brief", "foot", 48, 1540,
               "三张图使用同一份 schedule.json；单位：分钟，以 09:00 为 0。", 1104, 18, "#6B7686"))
    return K.document(W, H, p, background="#Fbfaf7")

# ---------------------------------------------------------------- 3. action card
def card():
    W, H = 720, 1280
    p = [K.rect(0, 0, W, H, color="#0D141F")]
    p.append(K.rect(0, 0, W, 6, color=ACCENT))
    p.append(T("card", "title", 32, 26, "发布日行动卡", 500, 30, INK, True))
    p.append(T("card", "sub", 32, 68, f"09:00 开工 · {SCH['makespan_clock']} 完成 · 缓冲 {BUF}′", 600,
               18, MUTED))
    p.append(K.rect(32, 100, 656, 1, color=LINE))
    for i, r in enumerate(ROWS):
        y = 112 + i * 84
        col = COLOR[r["team"]]
        p.append(K.rect(32, y, 656, 74, color="#141E2C", radius=8))
        p.append(K.rect(32, y, 5, 74, color=col, radius=2))
        p.append(T("card", f"{r['id']}-time", 48, y + 8, f"{r['start']}–{r['end']}", 150, 18, ACCENT,
                   True))
        p.append(T("card", f"{r['id']}-id", 200, y + 8, r["id"], 60, 18, col, True))
        p.append(T("card", f"{r['id']}-label", 258, y + 8, r["label"], 300, 18, INK, True))
        p.append(T("card", f"{r['id']}-team", 560, y + 8,
                   "设计" if r["team"] == "design" else "工程", 110, 17, col, align="RIGHT"))
        dep = ("前置 " + "、".join(r["deps"])) if r["deps"] else "首个任务"
        p.append(T("card", f"{r['id']}-meta", 48, y + 38, f"{r['minutes']} 分钟 · {dep}", 380, 16,
                   INK2))
        if r["id"] in RISK:
            p.append(T("card", f"{r['id']}-risk", 420, y + 38,
                       f"⚠ {RISK[r['id']]['id']} {SHORT[RISK[r['id']]['id']]}", 250, 16, WARN))
    p.append(T("card", "foot", 32, 1140,
               f"完成于 {SCH['makespan_clock']}，距 16:00 尚余 {BUF} 分钟；风险返工将消耗这段缓冲。",
               656, 17, MUTED))
    p.append(T("card", "foot2", 32, 1170, "时间单位：分钟，以 09:00 为 0；同团队不可并行。", 656, 16,
               MUTED))
    return K.document(W, H, p, background="#0D141F")

logger = api.TaskLogger(TASK, TMP)
for name, fn in (("execution-board", board), ("decision-brief", brief), ("action-card", card)):
    dsl = fn()
    (OUT / f"{name}.snapshot").write_text(dsl, encoding="utf-8")
    warn = K.drain_warnings()
    rec = logger.render(OUT / f"{name}.snapshot", OUT / f"{name}.png", name)
    print(name, rec["http_status"], rec["response_bytes"], rec["elapsed_s"])
    for w in warn:
        print("   ", w)
    if rec["http_status"] != 200:
        print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:800])
        raise SystemExit(1)
api.write_json(OUT / "content-map.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "schedule_source": "schedule.json（三图共用）",
    "canvases": {"execution-board": [1920, 1080], "decision-brief": [1200, 1600],
                 "action-card": [720, 1280]},
    "entries": TXT,
})
print("done", len(TXT))
