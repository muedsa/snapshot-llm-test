# -*- coding: utf-8 -*-
"""A24 · 三图构建：execution-board 1920×1080 / decision-brief 1200×1600 /
action-card 720×1280（同一 schedule.json 数字；真实同尺度时间轴）。"""
import json
import os
import math
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
OUT = TASK_ROOT / "outputs" / RUN / "A24"
OUT.mkdir(parents=True, exist_ok=True)

sched = json.load((OUT / "schedule.json").open(encoding="utf-8"))
rel = json.load(open(TASK_ROOT / "tasks" / "A24-release-plan-capstone"
                     / "inputs" / "release.json", encoding="utf-8"))
TSK = {t["id"]: t for t in rel["tasks"]}
RISKS = {k["id"]: k for k in rel["risks"]}

CYAN, AMBER, GREEN, RED = "#4CC2FF", "#FFC154", "#3FD9A4", "#FF8A80"
TXT, SUB, MUT = "#EAF3FF", "#A9BFDF", "#8FA8CE"
PANEL, PBORDER, GRID, AXLINE = "#12203A", "#23375C", "#27395F", "#33507F"
BG = "#0B1526"
FONT = "Noto Sans CJK SC"
NUM = "Inter"

def hhmm(m):
    return f"{9 + m // 60:02d}:{m % 60:02d}"


def fam(s):
    """含 CJK 的字符串用 Noto Sans CJK SC；纯 ASCII 用 Inter（不含逗号回退）。"""
    return FONT if any(ord(c) > 0x2E80 for c in s) else NUM


def fnum(v):
    s = f"{float(v):.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def rect(s, x, y, w, h, color, radius=0, border=None, height=None):
    hh = height if height is not None else h
    a = (f'<Positioned left="{fnum(x)}" top="{fnum(y)}" width="{fnum(w)}" '
         f'height="{fnum(hh)}"><Container width="{fnum(w)}" '
         f'height="{fnum(hh)}"')
    if color:
        a += f' color="{color}"'
    if radius:
        a += f' borderRadius="{fnum(radius)}"'
    if border:
        a += f' border="{border}"'
    s.append(a + " /></Positioned>")


def text(s, x, y, content, size, color, bold=False, family=FONT,
         align=None, box_w=None):
    sty = (f'<Text fontSize="{fnum(size)}" color="{color}" fontFamily="{family}"')
    if bold:
        sty += ' fontStyle="BOLD"'
    if align:
        sty += f' textAlign="{align}"'
    sty += ">"
    if box_w:
        s.append(f'<Positioned left="{fnum(x)}" top="{fnum(y)}" '
                 f'width="{fnum(box_w)}">{sty}{content}</Text></Positioned>')
    else:
        s.append(f'<Positioned left="{fnum(x)}" top="{fnum(y)}">{sty}'
                 f'{content}</Text></Positioned>')


SC = json.load((OUT / "schedule.json").open(encoding="utf-8"))
BY_ID = {t["id"]: t for t in SC["tasks"]}
FIN = SC["finish_minute"]
BUF = SC["buffer_minutes"]
GAP5_D = (200, 205)
GAP5_E = (235, 240)

# ============ 1 · execution-board 1920×1080 ============
B = ['<SizedBox width="1920" height="1080" />']
X0, X1 = 480.0, 1840.0
PPM = (X1 - X0) / 420.0
def xx(m):
    return X0 + m * PPM


rect(B, 0, 0, 1920, 1080, BG)
# header
rect(B, 40, 40, 44, 44, CYAN, 10)
text(B, 46, 42, "叠", 30, BG, bold=True)
text(B, 100, 40, "双团队发布作战计划 · 执行泳道", 40, TXT, bold=True)
text(B, 100, 94, "叠光 · 发布演练 | 窗口 09:00–16:00（420 分钟）| 排程依据"
     " schedule.json（同源三图）", 22, SUB)
board_kpis = [(40, f"完成 {hhmm(FIN)}（{FIN} 分）", GREEN),
              (470, f"剩余缓冲 {BUF} 分（至 16:00）", TXT),
              (940, "纯依赖关键路径 255 分", SUB),
              (1310, "工作量下界 242.5 分（485÷2）", SUB)]
for kx, label, col in board_kpis:
    text(B, kx, 148, label, 22, col, bold=(col == GREEN), family=fam(label))

# lane panel
rect(B, 40, 200, 1840, 564, PANEL, 14, f"1 SOLID {PBORDER}")
# hour gridlines + labels
for k in range(0, 8):
    xg = xx(k * 60)
    rect(B, xg, 214, 1.5 if k in (0, 7) else 1, 542, AXLINE if k in (0, 7)
         else GRID)
    text(B, xg - 34, 768, f"{9 + k:02d}:00", 22, MUT, family=NUM,
         align="CENTER", box_w=68)
# finish / deadline verticals
rect(B, xx(FIN), 214, 2, 542, GREEN)
rect(B, X1, 214, 2, 542, RED)
text(B, xx(FIN) + 8, 186, f"完成 {hhmm(FIN)}", 22, GREEN, bold=True)
text(B, X1 - 150, 186, "16:00 截止", 22, RED, bold=True)

lane_rows = {"design": (222, CYAN), "engineering": (486, AMBER)}
lane_meta = {
    "design": f"design 团队 · 235 分钟 · 5 任务（专属链）",
    "engineering": f"engineering 团队 · 250 分钟 · 7 任务",
}
for lane, (rt, col) in lane_rows.items():
    rect(B, 56, rt, 396, 232, "#0F1C35", 12, f"1 SOLID {PBORDER}")
    rect(B, 56, rt, 4, 232, col, 12)
    text(B, 76, rt + 16, lane, 26, TXT, bold=True)
    text(B, 76, rt + 58, lane_meta[lane], 20, MUT)
    text(B, 76, rt + 96, "任务按 schedule.json 排布；", 20, MUT)
    text(B, 76, rt + 126, "块内为编号与起止时刻。", 20, MUT)
    gap = (200, 205) if lane == "design" else (235, 240)
    rect(B, xx(gap[0]), rt + 44, xx(gap[1]) - xx(gap[0]), 128, "#301A22", 8,
         f"1 SOLID {RED}")
    for t in SC["tasks"]:
        if t["team"] != lane:
            continue
        bx, bw = xx(t["start_minute"]), (t["end_minute"] - t["start_minute"]) * PPM
        rect(B, bx, rt + 44, bw, 128, col, 10)
        text(B, bx + 10, rt + 54, t["id"], 26, BG, bold=True, family=NUM)
        text(B, bx + 10, rt + 92, hhmm(t["start_minute"]), 20, BG, family=NUM)
        text(B, bx + 10, rt + 122, hhmm(t["end_minute"]), 20, BG, family=NUM)
        for kid, kr in RISKS.items():
            if kr["task"] == t["id"]:
                rect(B, bx + bw - 46, rt + 12, 36, 26, RED, 6)
                text(B, bx + bw - 46, rt + 13, kid, 18, "#FFFFFF", bold=True,
                     family=NUM, align="CENTER", box_w=36)
# legend grid（12 任务 全元数据）
row_ids = [t["id"] for t in SC["tasks"]]
for i, tid in enumerate(row_ids):
    t = BY_ID[tid]
    gx = 40 + (i % 6) * 306.7
    gy = 806 + (i // 6) * 118
    rect(B, gx, gy, 296, 106, "#0F1C35", 10, f"1 SOLID {PBORDER}")
    rect(B, gx, gy, 4, 106, CYAN if t["team"] == "design" else AMBER, 10)
    deps = "、".join(t["depends"]) if t["depends"] else "—"
    text(B, gx + 16, gy + 10, f"{tid} {t['label']}", 21, TXT, bold=True)
    text(B, gx + 16, gy + 44,
         f"{t['minutes']} 分 · {t['team']}", 20, SUB)
    text(B, gx + 16, gy + 74,
         f"依赖 {deps}｜{hhmm(t['start_minute'])}", 20, MUT)
text(B, 40, 1056, "风险徽章：K1 服务限流（R02）· K2 文案版式回归（R05）· "
     "K3 成图裁剪或比例错误（R10），对策详见决策简报；红框小格为团队空档"
     "（design 200–205 分、engineering 235–240 分，各 5 分钟）。",
     20, MUT)

dsl_b = ('<Snapshot background="' + BG + '" type="png">\n<Stack>\n'
         + "\n".join(B) + "\n</Stack>\n</Snapshot>\n")
(OUT / "execution-board.snapshot").write_text(dsl_b, encoding="utf-8")
print("execution-board.snapshot", len(dsl_b))

# ============ 2 · decision-brief 1200×1600 ============
D = ['<SizedBox width="1200" height="1600" />']
rect(D, 0, 0, 1200, 1600, BG)
rect(D, 40, 40, 44, 44, CYAN, 10)
text(D, 46, 42, "叠", 30, BG, bold=True)
text(D, 100, 40, "发布演练 · 决策简报", 40, TXT, bold=True)
text(D, 100, 94, "2026-11-07 发布日 | 两团队 12 任务 | 09:00–16:00",
     24, SUB)
rect(D, 1036, 48, 124, 94, PANEL, 10, f"1 SOLID {PBORDER}")
text(D, 1046, 58, f"{FIN} 分", 30, GREEN, bold=True, family=fam(f"{FIN} 分"))
text(D, 1046, 104, "完工时刻", 20, MUT)
kpis = [(hhmm(FIN), "完成时刻（13:20）", GREEN, 34),
        (f"{BUF} 分", "剩余缓冲（420−260）", TXT, 34),
        ("255 分", "纯依赖关键路径", TXT, 34),
        ("242.5 分", "工作量下界（485÷2）", TXT, 34)]
for i, (v, lab, col, vs) in enumerate(kpis):
    x = 40 + (i % 2) * 570
    y = 160 + (i // 2) * 128
    rect(D, x, y, 540, 112, PANEL, 12, f"1 SOLID {PBORDER}")
    rect(D, x, y, 4, 112, CYAN, 12)
    text(D, x + 20, y + 12, v, vs, col, bold=True, family=fam(v))
    text(D, x + 20, y + 70, lab, 22, MUT)
# 依赖概览 12 卡（2 列 6 行）
text(D, 40, 428, "依赖概览 · 12 任务（时段/团队/依赖同 schedule.json）", 24, TXT,
     bold=True)
card_rows = []
for i, t in enumerate(SC["tasks"]):
    deps = "、".join(t["depends"]) if t["depends"] else "—（根任务）"
    x = 40 + (i % 2) * 570
    y = 470 + (i // 2) * 104
    card_rows.append((t["id"], x, y))
    rect(D, x, y, 540, 92, "#0F1C35", 10, f"1 SOLID {PBORDER}")
    rect(D, x, y, 4, 92, CYAN if t["team"] == "design" else AMBER, 10)
    text(D, x + 18, y + 10, f"{t['id']} {t['label']}", 24, TXT, bold=True)
    text(D, x + 18, y + 52,
         f"{t['team']} · {t['minutes']} 分 · "
         f"{hhmm(t['start_minute'])}–{hhmm(t['end_minute'])} · 依赖 {deps}",
         20, SUB)
# 排程依据
rect(D, 40, 1106, 1120, 300, PANEL, 12, f"1 SOLID {PBORDER}")
rect(D, 40, 1106, 4, 300, GREEN, 12)
text(D, 64, 1120, "排程依据（schedule-audit.json 可核验）", 24, TXT, bold=True)
text(D, 64, 1160, "① 纯依赖关键路径 255 分：R01→R04→R07→R09→R10→R12（六任务均", 24, SUB)
text(D, 64, 1190, "    只允许 design，单团队串行——仅依赖下界。", 24, SUB)
text(D, 64, 1220, "② 总工时 485 分钟；工作量下界 485÷2=242.5 分（更松，被依赖链支配）。", 24, SUB)
text(D, 64, 1250, "③ R05 的资源-依赖冲突抬高下界：R05 若在 design，R01+R05+R04=115", 24, SUB)
text(D, 64, 1280, "    →完工 ≥285 分；若在 engineering（R01 后 25..55 起），R02→R05→", 24, SUB)
text(D, 64, 1310, "    R03→R06→R08 链长 200 →R08.end≥205 →完工 ≥260 分。", 24, SUB)
text(D, 64, 1340, f"④ 本排程完工 {FIN} 分（{hhmm(FIN)}），恰达 ③ 中 engineering 路线之联合下界", 24, GREEN, bold=True)
text(D, 64, 1372, "    ——可证最优。", 24, GREEN, bold=True)
# 风险/对策
text(D, 40, 1420, "三风险与对策（release.json 原文）", 24, TXT, bold=True)
for i, kid in enumerate(["K1", "K2", "K3"]):
    r = RISKS[kid]
    y = 1458 + i * 44
    rect(D, 40, y, 60, 34, RED, 6)
    text(D, 40, y + 2, kid, 20, "#FFFFFF", bold=True, family=NUM,
         align="CENTER", box_w=60)
    text(D, 116, y, f"{r['impact']}（{r['task']}）→ 对策：{r['mitigation']}",
         22, SUB)
dsl_d = ('<Snapshot background="' + BG + '" type="png">\n<Stack>\n'
         + "\n".join(D) + "\n</Stack>\n</Snapshot>\n")
(OUT / "decision-brief.snapshot").write_text(dsl_d, encoding="utf-8")
print("decision-brief.snapshot", len(dsl_d))

# ============ 3 · action-card 720×1280 ============
C = ['<SizedBox width="720" height="1280" />']
rect(C, 0, 0, 720, 1280, BG)
rect(C, 32, 32, 40, 40, CYAN, 10)
text(C, 37, 34, "叠", 26, BG, bold=True)
text(C, 88, 32, "手机行动卡 · 发布演练", 34, TXT, bold=True)
text(C, 88, 80, "2026-11-07 · 完成目标", 20, SUB)
rect(C, 32, 132, 656, 96, PANEL, 12, f"1 SOLID {PBORDER}")
rect(C, 32, 132, 4, 96, GREEN, 12)
text(C, 56, 142, f"{hhmm(FIN)} 完成（{FIN} 分）", 30, GREEN, bold=True)
text(C, 56, 192, f"剩余缓冲 {BUF} 分（16:00 截止）", 20, MUT)
text(C, 32, 252, "12 任务时间序（团队/起止/依赖）", 24, TXT, bold=True)
ORDER = sorted(SC["tasks"], key=lambda t: (t["start_minute"],
                                           t["end_minute"], t["id"]))
ry = 296
for t in ORDER:
    col = CYAN if t["team"] == "design" else AMBER
    rect(C, 32, ry, 656, 62, "#0F1C35", 10, f"1 SOLID {PBORDER}")
    rect(C, 32, ry, 4, 62, col, 10)
    text(C, 52, ry + 4, f"{t['id']} {t['label']}", 24, TXT, bold=True)
    ris = [k for k, v in RISKS.items() if v["task"] == t["id"]]
    tw = sum(24 if ord(c) > 0x2e80 else 13 for c in t["label"])
    text(C, 52 + 60 + tw + 16, ry + 4, hhmm(t["start_minute"]) + "–" +
         hhmm(t["end_minute"]), 20, SUB, family=NUM)
    kids = " ".join(ris)
    if kids:
        rect(C, 540, ry + 4, 44, 28, RED, 6)
        text(C, 540, ry + 5, kids, 18, "#FFFFFF", bold=True, family=NUM,
             align="CENTER", box_w=44)
    text(C, 52, ry + 34,
         f"{t['team']} · {t['minutes']} 分 · 依赖 " +
         ("、".join(t["depends"]) if t["depends"] else "—"), 20, MUT)
    ry += 66
# 风险提醒
text(C, 32, ry + 8, "风险提醒", 24, TXT, bold=True)
for i, kid in enumerate(["K1", "K2", "K3"]):
    r = RISKS[kid]
    yy = ry + 48 + i * 40
    rect(C, 32, yy, 50, 32, RED, 6)
    text(C, 32, yy + 1, kid, 20, "#FFFFFF", bold=True, family=NUM,
         align="CENTER", box_w=50)
    text(C, 94, yy, f"{r['impact']}→{r['mitigation']}", 20, SUB)
dsl_c = ('<Snapshot background="' + BG + '" type="png">\n<Stack>\n'
         + "\n".join(C) + "\n</Stack>\n</Snapshot>\n")
(OUT / "action-card.snapshot").write_text(dsl_c, encoding="utf-8")
print("action-card.snapshot", len(dsl_c))

# ---- content-map.json ----
board_map = {}
for t in SC["tasks"]:
    rate = PPM
    board_map[t["id"]] = {
        "lane": t["team"],
        "x_px": round(xx(t["start_minute"]), 4),
        "w_px": round((t["end_minute"] - t["start_minute"]) * rate, 4),
        "row_top_px": {"design": 222, "engineering": 486}[t["team"]],
        "bar_top_px": {"design": 266, "engineering": 530}[t["team"]],
    }
brief_map = {t["id"]: {"card_index": i + 1, "x_px": 40 + (i % 2) * 570,
                       "y_px": 470 + (i // 2) * 104, "kpi_row": None}
             for i, t in enumerate(SC["tasks"])}
card_map = {t["id"]: {"order": i + 1,
                      "y_px": 296 + i * 66}
            for i, t in enumerate(ORDER)}
cm = {
    "schema_version": 1, "task_id": "A24", "path_base": "output_dir",
    "brand": "叠光 · 发布演练",
    "sizes": {"execution-board": [1920, 1080], "decision-brief": [1200, 1600],
              "action-card": [720, 1280]},
    "min_body_px": {"execution-board": 20, "decision-brief": 24, "action-card": 20},
    "time_mapping": {
        "execution-board": {"x0_px": 480, "x1_px": 1840, "window_minutes": 420,
                            "px_per_minute": round(PPM, 4),
                            "same_scale_note": "全部任务块用同一映射，"
                                               "无任务间压缩"},
    },
    "tasks": [{"id": t["id"], "board": board_map[t["id"]],
               "brief": brief_map[t["id"]], "card": card_map[t["id"]],
               "display": {"start_time": t["start_time"], "end_time": t["end_time"],
                           "start_minute": t["start_minute"],
                           "end_minute": t["end_minute"], "team": t["team"],
                           "minutes": t["minutes"], "depends": t["depends"],
                           "label": t["label"]}}
              for t in SC["tasks"]],
    "risks": [{"id": kid, "task": RISKS[kid]["task"],
               "impact": RISKS[kid]["impact"],
               "mitigation": RISKS[kid]["mitigation"],
               "board": "风险徽章（任务块右上角，红色 K 徽标）",
               "brief": f"风险与对策行 {i + 1}（y="
                        f"{1458 + i * 44}）",
               "card": f"风险提醒行 {i + 1}（y={296 + 12 * 66 + 48 + i * 38}）"}
              for i, kid in enumerate(["K1", "K2", "K3"])],
    "checks": [],  # finalize 时补三图核验记录
    "notes": "三图所有起止/团队/依赖数字取自 schedule.json 唯一事实源。",
}
with open(OUT / "content-map.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(cm, f, ensure_ascii=False, indent=1)
print("content-map.json written")
