"""A16 - corrected quarterly review, rebuilt from source.csv only.

Every number is computed from the CSV; the bar geometry comes from the same values, so a
label and its bar height can never disagree the way they do in the flawed draft.

Run from the suite task root:
  python tmp/<run_id>/A16/gen.py --ver v001
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import C, Node, Positioned, Snapshot, Stack, hline, num  # noqa: E402

RUN = "2026-10-12T10-04Z-r001"
TASK = "A16"
SRC = ROOT / "tasks" / "A16-visual-data-forensics" / "inputs" / "source.csv"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

W, H, M = 1280, 900, 40
RIGHT = W - M

rows = list(csv.DictReader(SRC.read_text(encoding="utf-8").splitlines()))
Q = [r["quarter"] for r in rows]
REV = [float(r["revenue_wan"]) for r in rows]
COST = [float(r["cost_wan"]) for r in rows]
PROFIT = [r - c for r, c in zip(REV, COST)]
MARGIN = [p / r * 100 for p, r in zip(PROFIT, REV)]
QOQ = [None] + [REV[i] - REV[i - 1] for i in range(1, len(REV))]
TOT_R, TOT_C, TOT_P = sum(REV), sum(COST), sum(PROFIT)
BEST = max(range(len(Q)), key=lambda i: PROFIT[i])
OTHERS = [j for j in range(len(Q)) if j != BEST]
RUNNER = max(OTHERS, key=lambda j: PROFIT[j])

INK, INK2, INK3 = "#16233A", "#42536E", "#78879C"
PAPER, CARD, LINE = "#F4F2EC", "#FFFFFF", "#E2E6EE"
REV_C, COST_C = "#2B5BD7", "#E0913B"
GOOD, BAD = "#0C7860", "#B3261E"
SANS = "Noto Sans CJK SC,Noto Sans CJK JP,Inter"
MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"

# chart geometry: one common zero baseline for both series
CX, CY, CW, CH = 40, 150, 700, 490
PLOT_L, PLOT_R = CX + 86, CX + CW - 26
BASE_Y, TOP_Y = CY + 420, CY + 100
AXIS_MAX = 200.0
K = (BASE_Y - TOP_Y) / AXIS_MAX
TICKS = [0, 40, 80, 120, 160, 200]
PITCH = (PLOT_R - PLOT_L) / len(Q)
BAR_W, BAR_GAP = 54, 14

def adv20(text):
    return sum(20 * (1.0 if ord(ch) > 0x2E80 else 0.62) for ch in text)


BOXES = []
CARDS = []


def txt(x, y, text, size, colour, *, w=None, align="LEFT", bold=False, font=SANS,
        mono=False, lh=1.3, role=""):
    fam = MONO if mono else font
    adv = lambda ch: size * (1.0 if ord(ch) > 0x2E80 else 0.62)
    if w is None:
        w = sum(adv(ch) for ch in text) + 2
    h = size * lh
    BOXES.append({"role": role or text[:20], "x": x, "y": y, "w": w, "h": h,
                  "size": size, "text": text[:28]})
    a = {"fontSize": num(size), "color": colour, "fontFamily": fam, "textAlign": align}
    if bold:
        a["fontStyle"] = "BOLD"
    return Node("Positioned", {"left": num(x), "top": num(y), "width": num(w)},
                [Node("Text", a, [], text)])


def box(x, y, w, h, *, colour=None, radius=None, border=None):
    a = {"width": num(w), "height": num(h)}
    if colour:
        a["color"] = colour
    if radius is not None:
        a["borderRadius"] = num(radius)
    if border:
        a["border"] = border
    return Positioned(C(**a), left=num(x), top=num(y))


def card(x, y, w, h, title, *, sub=None, title_w=None):
    CARDS.append([x, y, w, h])
    els = [box(x, y, w, h, colour=CARD, radius=14, border=f"1 SOLID {LINE}")]
    els.append(txt(x + 28, y + 22, title, 26, INK, bold=True,
                   w=title_w if title_w else w - 56, role="card-t"))
    if sub:
        els.append(txt(x + 28, y + 58, sub, 20, INK3, w=w - 56, role="card-s"))
    return els


def build():
    els = []
    els.append(txt(M, 40, "季度复盘：Q4 收入与利润均为全年最高", 40, INK,
                   w=RIGHT - M, bold=True, role="title", lh=1.2))
    els.append(txt(M, 96,
                   f"全年收入 {TOT_R:.0f} 万元、成本 {TOT_C:.0f} 万元、利润 {TOT_P:.0f} 万元；"
                   f"收入并非逐季上升，Q3 环比回落 {abs(REV[2] - REV[1]):.0f} 万元。",
                   22, INK2, w=RIGHT - M, role="subtitle"))

    els += card(CX, CY, CW, CH, "收入与成本对比", title_w=320,
               sub="单位：万元 · 两系列共用 0 起点 · 柱下为季度利润率")
    # legend
    lx = CX + CW - 260
    els.append(box(lx, CY + 26, 18, 18, colour=REV_C, radius=4))
    els.append(txt(lx + 26, CY + 22, "收入", 22, INK, w=60, role="lg1"))
    els.append(box(lx + 96, CY + 26, 18, 18, colour=COST_C, radius=4))
    els.append(txt(lx + 122, CY + 22, "成本", 22, INK, w=60, role="lg2"))
    # gridlines + tick labels
    for t in TICKS:
        y = BASE_Y - t * K
        els.append(hline(PLOT_L, PLOT_R, y, 1 if t else 2, LINE if t else "#B9C2D2"))
        els.append(txt(PLOT_L - 62, y - 13, f"{t}", 20, INK3, w=50, align="RIGHT",
                       mono=True, role=f"tick{t}"))
    # bars
    for i, q in enumerate(Q):
        cx = PLOT_L + PITCH * (i + 0.5)
        for off, val, col in ((-BAR_W - BAR_GAP / 2, REV[i], REV_C),
                              (BAR_GAP / 2, COST[i], COST_C)):
            bx, bh = cx + off, val * K
            els.append(box(bx, BASE_Y - bh, BAR_W, bh, colour=col, radius=4))
            els.append(txt(bx - 14, BASE_Y - bh - 30, f"{val:.0f}", 22, INK, w=BAR_W + 28,
                           align="CENTER", bold=True, mono=True, role=f"v{q}"))
        els.append(txt(cx - PITCH / 2, BASE_Y + 8, q, 22, INK2, w=PITCH, align="CENTER",
                       bold=True, role=f"q{q}"))
        els.append(txt(cx - PITCH / 2, BASE_Y + 38, f"利润率 {MARGIN[i]:.1f}%", 18, INK3,
                       w=PITCH, align="CENTER", role=f"pm{q}"))

    # profit detail
    PX, PY, PW, PH = CX + CW + 24, CY, RIGHT - (CX + CW + 24), 240
    els += card(PX, PY, PW, PH, "利润明细")
    els.append(txt(PX + 28, PY + 58, "季度 · 收入 − 成本 = 利润（利润率）", 20, INK3,
                   w=PW - 56, role="pt-h"))
    for i, q in enumerate(Q):
        y = PY + 92 + i * 32
        mark = "★" if i == BEST else " "
        els.append(txt(PX + 28, y, f"{mark} {q}", 22, INK if i == BEST else INK2,
                       w=70, mono=True, bold=(i == BEST), role=f"pd-q{q}"))
        els.append(txt(PX + 100, y, f"{REV[i]:.0f} − {COST[i]:.0f} = "
                                   f"{PROFIT[i]:.0f} 万元", 22,
                       INK if i == BEST else INK2, w=PW - 190, mono=True,
                       bold=(i == BEST), role=f"pd-{q}"))
        els.append(txt(PX + PW - 86, y, f"{MARGIN[i]:.1f}%", 22,
                       GOOD if i == BEST else INK3, w=58, align="RIGHT", mono=True,
                       bold=(i == BEST), role=f"pm-{q}"))

    # key observation
    KX, KY, KW, KH = PX, PY + PH + 22, PW, CH - PH - 22
    CARDS.append([KX, KY, KW, KH])
    els.append(box(KX, KY, KW, KH, colour="#FDF6E9", radius=14,
                   border=f"1 SOLID #E8D9BC"))
    els.append(txt(KX + 28, KY + 22, "重点观察 · Q4", 26, INK, bold=True, w=KW - 56,
                   role="key-t"))
    others = [j for j in range(len(Q)) if j != BEST]
    RUNNER = max(others, key=lambda j: PROFIT[j])
    lines = [
        f"利润 {PROFIT[BEST]:.0f} 万元，全年最高",
        f"比次高的 {Q[RUNNER]}（{PROFIT[RUNNER]:.0f} 万元）多 "
        f"{PROFIT[BEST] - PROFIT[RUNNER]:.0f} 万元",
        f"收入 {REV[BEST]:.0f} 万元，环比 {QOQ[BEST]:+.0f} 万元",
        f"利润率 {MARGIN[BEST]:.1f}%，同为四季最高",
        f"Q2 收入升 {REV[1] - REV[0]:.0f} 万元，利润率反降至 {MARGIN[1]:.1f}%",
        "故重点季度是 Q4，不是原稿的 Q3",
    ]
    y = KY + 62
    for j, s in enumerate(lines):
        els.append(box(KX + 28, y + 8, 6, 6, colour="#C9932F", radius=3))
        els.append(txt(KX + 46, y, s, 20, INK2, w=KW - 74, role=f"key{j}", lh=1.3))
        y += 26 * max(1, -(-adv20(s) // (KW - 74)))

    # corrections strip
    FX, FY, FW, FH = M, CY + CH + 24, RIGHT - M, 138
    CARDS.append([FX, FY, FW, FH])
    els.append(box(FX, FY, FW, FH, colour="#EDF1F8", radius=14,
                   border=f"1 SOLID {LINE}"))
    els.append(txt(FX + 24, FY + 16, "相对原稿的修正", 22, INK, bold=True, w=200,
                   role="fix-t"))
    fixes = [
        "纵轴由 100 起改为 0 起，柱高与数值成比例",
        "图例与柱色对应关系更正：蓝=收入、橙=成本",
        f"Q3 利润由 42 万元改为 {PROFIT[2]:.0f} 万元（128 − 96）",
        f"标题与重点季度由 Q3 改为 Q4（利润 {PROFIT[3]:.0f} 万元最高）",
        "副标题“收入持续上升”改为按环比如实描述",
        "补充利润率与收入环比，使结论可被数据检验",
    ]
    for i, s in enumerate(fixes):
        col, row = i % 2, i // 2
        els.append(txt(FX + 24 + col * (FW - 48) / 2, FY + 54 + row * 26, "· " + s,
                       18, INK2, w=(FW - 60) / 2, role=f"fix{i}"))

    els.append(txt(M, FY + FH + 22,
                   "数据来源：inputs/source.csv（唯一可信原始数据）· 单位为万元 · "
                   "本图为虚构经营数据的排版样张", 20, INK3, w=RIGHT - M, role="footer"))
    return els


def audit():
    problems = []
    for b in BOXES:
        if b["x"] < M - 1 or b["x"] + b["w"] > RIGHT + 1 or b["y"] < M - 1 \
                or b["y"] + b["h"] > H - M + 1:
            problems.append(f"margin {b['role']} {b['x']:.0f},{b['y']:.0f} "
                            f"{b['w']:.0f}x{b['h']:.0f}")
        if b["size"] < 18:
            problems.append(f"size<18 {b['role']} {b['size']}")
        inside = [c for c in CARDS if c[0] - 1 <= b["x"] and c[1] - 1 <= b["y"]
                  and c[0] + c[2] + 1 >= b["x"] + b["w"] and c[1] + c[3] + 1 >= b["y"] + b["h"]]
        touching = [c for c in CARDS if min(c[0] + c[2], b["x"] + b["w"]) - max(c[0], b["x"]) > 1
                    and min(c[1] + c[3], b["y"] + b["h"]) - max(c[1], b["y"]) > 1]
        if touching and not inside:
            problems.append(f"outside-card {b['role']} ({b['text']}) in "
                            f"{touching[0][0]},{touching[0][1]},{touching[0][2]}x{touching[0][3]}")
    for i in range(len(BOXES)):
        for j in range(i + 1, len(BOXES)):
            a, c = BOXES[i], BOXES[j]
            ox = min(a["x"] + a["w"], c["x"] + c["w"]) - max(a["x"], c["x"])
            oy = min(a["y"] + a["h"], c["y"] + c["h"]) - max(a["y"], c["y"])
            if ox > 1 and oy > 1:
                problems.append(f"overlap {a['role']}({a['text']}) x {c['role']}"
                                f"({c['text']}) {ox:.0f}x{oy:.0f}")
    for p in problems:
        print(p, file=sys.stderr)
    return len(problems)


ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
a = ap.parse_args()
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

els = build()
nprob = audit()
doc = Snapshot(Stack(C(width=num(W), height=num(H), color=PAPER), *els,
                     alignment="TOP_LEFT", clipBehavior="HARD_EDGE"),
               background=PAPER, type="png")
(TMP_DIR / f"{a.ver}-corrected-report.snapshot").write_text(doc.render() + "\n",
                                                            encoding="utf-8")

derived = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "source": {"file": "tasks/A16-visual-data-forensics/inputs/source.csv",
               "columns": ["quarter", "revenue_wan", "cost_wan"], "rows": len(rows),
               "unit": "万元"},
    "per_quarter": [{
        "quarter": Q[i], "revenue_wan": REV[i], "cost_wan": COST[i],
        "profit_wan": PROFIT[i], "profit_margin_pct": round(MARGIN[i], 4),
        "revenue_qoq_wan": QOQ[i],
        "revenue_qoq_pct": None if QOQ[i] is None else round(QOQ[i] / REV[i - 1] * 100, 4),
        "derivation": f"profit = revenue − cost = {REV[i]:.0f} − {COST[i]:.0f} = "
                      f"{PROFIT[i]:.0f}；margin = profit / revenue = "
                      f"{PROFIT[i]:.0f}/{REV[i]:.0f} = {MARGIN[i]:.4f}%"}
        for i in range(len(Q))],
    "totals": {"revenue_wan": TOT_R, "cost_wan": TOT_C, "profit_wan": TOT_P,
               "overall_margin_pct": round(TOT_P / TOT_R * 100, 4)},
    "headline": {
        "text": "季度复盘：Q4 收入与利润均为全年最高",
        "evidence": f"max(profit) = {PROFIT[BEST]:.0f} at {Q[BEST]}；"
                    f"max(revenue) = {max(REV):.0f} at {Q[REV.index(max(REV))]}；"
                    f"max(margin) = {max(MARGIN):.1f}% at {Q[MARGIN.index(max(MARGIN))]}",
        "rejected_alternative": "原稿标题“Q3利润最高”：Q3 利润 32 < Q4 利润 54，不成立"},
    "key_quarter": {"quarter": Q[BEST], "profit_wan": PROFIT[BEST],
                    "margin_pct": round(MARGIN[BEST], 4),
                    "runner_up": {"quarter": Q[RUNNER], "profit_wan": PROFIT[RUNNER]},
                    "argument": "Q4 在收入、利润绝对值与利润率三项上同时最高，"
                                "因此重点季度由数据指向 Q4 而非原稿的 Q3"},
    "axis_definition": {
        "series": ["revenue_wan", "cost_wan"],
        "shared_zero_baseline": True,
        "baseline_value": 0, "baseline_y_px": BASE_Y,
        "axis_max_value": AXIS_MAX, "axis_top_y_px": TOP_Y,
        "px_per_unit": round(K, 6),
        "ticks": TICKS,
        "tick_y_px": {str(t): BASE_Y - t * K for t in TICKS},
        "bar_height_formula": "height_px = value × 1.6（BASE_Y − value × K 为柱顶 y）",
        "plot_box_px": [PLOT_L, TOP_Y, PLOT_R, BASE_Y],
        "group_pitch_px": round(PITCH, 2), "bar_width_px": BAR_W,
        "bar_gap_px": BAR_GAP,
        "per_bar_geometry": [{"quarter": Q[i], "series": s, "value": v,
                              "x": PLOT_L + PITCH * (i + 0.5) + off,
                              "top_y": BASE_Y - v * K, "height": v * K}
                             for i in range(len(Q))
                             for s, v, off in (("revenue", REV[i], -BAR_W - BAR_GAP / 2),
                                               ("cost", COST[i], BAR_GAP / 2))],
    },
    "typography": {"body_min_px": 22, "annotation_min_px": 18,
                   "sizes_used_px": sorted({b["size"] for b in BOXES}),
                   "safe_margin_px": M},
    "layout_audit_problems": nprob,
    "no_external_images": "全部图形（卡片、柱、网格线、圆点、色块）由 DSL Container 构造，"
                          "未使用 Image 节点，也未嵌入 flawed-report.png",
}
(OUT_DIR / "corrected-data.json").write_text(
    json.dumps(derived, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(TMP_DIR / f"{a.ver}-boxes.json").write_text(json.dumps(BOXES, ensure_ascii=False,
                                                        indent=1) + "\n", encoding="utf-8")
print(json.dumps({"ver": a.ver, "problems": nprob, "boxes": len(BOXES),
                  "profit": PROFIT, "margin": [round(m, 1) for m in MARGIN],
                  "totals": [TOT_R, TOT_C, TOT_P], "best": Q[BEST],
                  "sizes": sorted({b["size"] for b in BOXES})}, ensure_ascii=False))
sys.exit(1 if nprob else 0)
