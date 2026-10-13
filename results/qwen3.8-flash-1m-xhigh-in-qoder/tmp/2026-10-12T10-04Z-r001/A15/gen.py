"""A15 - reconstruct the 1440x900 reference UI from measured anchors.

Every geometry constant below is the value measure.py read off reference.png; the same
detector then runs on the reconstruction so the audit reports measured component errors
rather than impressions. content.json supplies the strings verbatim.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import C, Node, Positioned, Snapshot, Stack, hline, num  # noqa: E402

RUN = "2026-10-12T10-04Z-r001"
TASK = "A15"
SRC = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "content.json"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

d = json.loads(SRC.read_text(encoding="utf-8"))
W, H = 1440, 900

# measured from reference.png
SIDE_R = 220
MAIN_L, MAIN_R = 261, 1399
PAPER, SIDEBAR, CARD = "#F3F6FB", "#14233C", "#FFFFFF"   # sampled off reference.png
NAV_SEL, NAV_TEXT, NAV_DIM = "#294467", "#F2F6FC", "#9AA9BF"
BLUE, INK, INK2, INK3 = "#245CE4", "#18243C", "#42536E", "#7C8AA0"
BTN = "#2B54D8"
GRID = "#DCE3EE"
TEAL = "#3CCB9A"
GREEN = "#0C7860"   # all three reference deltas are this teal-green
LABEL_BG = {"In progress": "#DCE7FB", "Review": "#FBEBD2", "Done": "#D8F0E2"}
LABEL_FG = {"In progress": "#2454E4", "Review": "#9C600C", "Done": "#0C7860"}
ACT_DOT = ["#E8A33D", "#2F5BEA", "#2FA36B"]

SANS = "Inter,Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"

KPI = [(261, 139, 354, 142), (645, 139, 354, 142), (1029, 139, 354, 142)]
CHART = (261, 311, 740, 284)
ACT = (1031, 311, 368, 284)
TABLE = (261, 625, 1138, 216)
PILL = (18, 116, 184, 48)
BUTTON = (1184, 43, 216, 48)
ZERO_Y, UNIT = 549, (549 - 420) / 108          # measured baseline and px per ¥ thousand
PLOT_L, PLOT_R = 333, 970   # measured gridline extent on reference.png
BAR_W, BAR_PITCH, BAR_C0 = 46, 101, 384
COLS = [297, 780, 1035, 1230]
PILL3 = (1028, 799, 148, 28)

BOXES = []


def txt(x, y, text, size, colour, *, w=None, align="LEFT", bold=False, font=SANS,
        mono=False, ls=None, role=""):
    fam = MONO if mono else font
    if w is None:
        w = sum(size * (1.0 if ord(ch) > 0x2E80 else 0.60) for ch in text)
    if ls:
        w += ls * max(1, len(text) - 1)
    h = size * 1.30
    BOXES.append({"role": role or text[:18], "x": x, "y": y, "w": w, "h": h,
                  "size": size, "text": text[:24]})
    a = {"fontSize": num(size), "color": colour, "fontFamily": fam, "textAlign": align}
    if bold:
        a["fontStyle"] = "BOLD"
    if ls:
        a["letterSpacing"] = num(ls)
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


def build():
    els = [box(0, 0, SIDE_R, H, colour=SIDEBAR)]

    # brand
    els.append(box(28, 32, 30, 30, colour=TEAL, radius=9))
    els.append(box(37, 41, 12, 12, colour=SIDEBAR, radius=4))
    els.append(txt(70, 37, d["brand"], 20, NAV_TEXT, bold=True, mono=True, ls=1.2,
                   w=140, role="brand"))

    # navigation
    els.append(box(PILL[0], PILL[1], PILL[2], PILL[3], colour=NAV_SEL, radius=10))
    els.append(box(PILL[0] + 20, PILL[1] + 17, 14, 14, colour=TEAL, radius=7))
    els.append(txt(PILL[0] + 46, PILL[1] + 14, d["navigation"][0], 18, NAV_TEXT,
                   bold=True, role="nav0"))
    for i, item in enumerate(d["navigation"][1:], start=1):
        y = 196 + (i - 1) * 55
        els.append(box(36, y + 14, 12, 12, colour="#5A6E8C", radius=6))
        els.append(txt(56, y + 8, item, 18, "#C6D2E2", role=f"nav{i}"))

    # workspace card
    els.append(box(18, 750, 184, 118, colour="#1B2C4A", radius=10))
    els.append(txt(36, 768, d["workspace_info"][0], 12, TEAL, bold=True, mono=True,
                   ls=0.8, role="ws0"))
    els.append(txt(36, 796, d["workspace_info"][1], 16, NAV_TEXT, role="ws1"))
    els.append(txt(36, 828, d["workspace_info"][2], 14, NAV_DIM, role="ws2"))

    # header
    els.append(txt(MAIN_L, 31, d["title"], 36, INK, bold=True, role="title"))
    els.append(txt(MAIN_L, 82, d["subtitle"], 18, INK3, w=420, role="subtitle"))
    els.append(box(*BUTTON, colour=BTN, radius=8))
    bw = sum(20 * 0.60 for _ in d["button"])
    els.append(txt(BUTTON[0] + (BUTTON[2] - bw) / 2, BUTTON[1] + 14, d["button"], 20,
                   "#FFFFFF", bold=True, w=bw, align="CENTER", role="button"))

    # KPI cards
    for (x, y, w, h), k in zip(KPI, d["kpis"]):
        els.append(box(x, y, w, h, colour=CARD, radius=10, border=f"1 SOLID {GRID}"))
        # explicit inner widths: v001 sized these boxes to the estimated advance and
        # "426" / "3.2%" wrapped onto a second line, landing on the change row
        iw = w - 56
        els.append(txt(x + 28, y + 24, k["label"], 13, INK3, bold=True, mono=True, ls=1.0,
                       w=iw, role=f"kpi-{k['label']}"))
        els.append(txt(x + 28, y + 52, k["value"], 32, INK, bold=True, w=iw,
                       role=f"kpi-v-{k['label']}"))
        els.append(txt(x + 28, y + 104, k["change"], 16, GREEN, bold=True, w=iw,
                       role=f"kpi-c-{k['label']}"))

    # chart card
    cx, cy, cw, ch = CHART
    els.append(box(cx, cy, cw, ch, colour=CARD, radius=10, border=f"1 SOLID {GRID}"))
    els.append(txt(cx + 30, cy + 24, d["chart_title"], 20, INK, bold=True, role="chart-t"))
    els.append(txt(cx + cw - 130, cy + 28, d["chart_period"], 15, INK3, w=100,
                   align="RIGHT", role="chart-p"))
    els.append(txt(PLOT_L - 30, cy + 62, f"{d['chart_unit']}", 12, INK3, w=90,
                   role="chart-unit"))
    for t in d["chart_ticks"]:
        y = ZERO_Y - t * UNIT
        els.append(hline(PLOT_L, PLOT_R, y, 1, GRID if t else "#C4CDDE"))
        els.append(txt(PLOT_L - 44, y - 9, str(t), 12, INK3, w=36, align="RIGHT",
                       role=f"tick{t}"))
    for i, (m, v) in enumerate(zip(d["months"], d["chart_values"])):
        bx = BAR_C0 + i * BAR_PITCH - BAR_W / 2
        bh = v * UNIT
        els.append(box(bx, ZERO_Y - bh, BAR_W, bh, colour=BLUE, radius=4))
        els.append(txt(BAR_C0 + i * BAR_PITCH - 30, ZERO_Y + 10, m, 13, INK3, w=60,
                       align="CENTER", role=f"m{m}"))

    # activity card
    ax, ay, aw, ah = ACT
    els.append(box(ax, ay, aw, ah, colour=CARD, radius=10, border=f"1 SOLID {GRID}"))
    els.append(txt(ax + 30, ay + 24, d["activity_title"], 20, INK, bold=True,
                   role="act-title"))
    for i, (what, when) in enumerate(d["activity"]):
        y = ay + 78 + i * 60
        els.append(box(ax + 30, y + 5, 10, 10, colour=ACT_DOT[i], radius=5))
        els.append(txt(ax + 52, y, what, 16, INK, bold=True, role=f"act{i}"))
        els.append(txt(ax + 52, y + 26, when, 14, INK3, mono=True, role=f"actt{i}"))

    # table card
    tx, ty, tw, th = TABLE
    els.append(box(tx, ty, tw, th, colour=CARD, radius=10, border=f"1 SOLID {GRID}"))
    els.append(txt(tx + 30, ty + 20, d["table_title"], 20, INK, bold=True, role="tbl-t"))
    els.append(box(tx + 30, ty + 62, tw - 60, 30, colour="#F1F4F9", radius=6))
    for col, name in zip(COLS, d["table_columns"]):
        els.append(txt(col, ty + 68, name, 12, INK3, bold=True, mono=True, ls=0.8,
                       role=f"col{name}"))
    for r, row in enumerate(d["rows"]):
        y = ty + 104 + r * 35
        els.append(txt(COLS[0], y, row[0], 16, INK, bold=True, role=f"r{r}p"))
        els.append(txt(COLS[1], y, row[1], 16, INK2, role=f"r{r}o"))
        pw = sum(14 * (1.0 if ord(ch) > 0x2E80 else 0.62) for ch in row[2]) + 40
        px = COLS[2]
        els.append(box(px, y - 4, 148, 28, colour=LABEL_BG[row[2]], radius=6))
        els.append(txt(px, y + 1, row[2], 14, LABEL_FG[row[2]], bold=True, w=148,
                       align="CENTER", role=f"r{r}s"))
        els.append(txt(COLS[3], y, row[3], 16, INK2, mono=True, role=f"r{r}d"))
        if r:
            els.append(hline(tx + 30, tx + tw - 30, y - 12, 1, "#EDF0F6"))

    els.append(txt(MAIN_L, 862, d["footer"], 14, INK3, role="footer"))
    return els


ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
a = ap.parse_args()
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

doc = Snapshot(Stack(C(width=num(W), height=num(H), color=PAPER), *build(),
                     alignment="TOP_LEFT", clipBehavior="HARD_EDGE"),
               background=PAPER, type="png")
(TMP_DIR / f"{a.ver}-reconstructed.snapshot").write_text(doc.render() + "\n",
                                                         encoding="utf-8")
(TMP_DIR / f"{a.ver}-boxes.json").write_text(json.dumps(BOXES, ensure_ascii=False,
                                                        indent=1) + "\n",
                                             encoding="utf-8")
print(json.dumps({"ver": a.ver, "nodes": len(doc.render().split("\n")),
                  "text_nodes": len(BOXES)}, ensure_ascii=False))
