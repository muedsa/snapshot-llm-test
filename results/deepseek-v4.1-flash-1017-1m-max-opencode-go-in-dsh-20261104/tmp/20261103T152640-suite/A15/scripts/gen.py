# -*- coding: utf-8 -*-
"""A15: reconstruct the reference dashboard at 1440x900."""
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

TASK = "A15"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)
C = json.loads((SUITE_ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "content.json")
               .read_text(encoding="utf-8"))

SIDEBAR = "#14233C"
SIDE_SEL = "#1E3352"
MAIN = "#F3F6FB"
CARD = "#FFFFFF"
INK = "#0F172A"
INK2 = "#334155"
MUTED = "#64748B"
BLUE = "#2563EB"
GREEN = "#059669"
LINE = "#E2E8F0"
FONT = "Inter,Noto Sans CJK SC"
W, H = 1440, 900

p: list[str] = []
p.append(K.rect(0, 0, W, H, color=MAIN))
p.append(K.rect(0, 0, 220, H, color=SIDEBAR))

# ---------------- sidebar
p.append(K.rect(26, 26, 32, 32, color="#34D399", radius=8))
p.append(K.rect(33, 33, 18, 18, color=SIDEBAR, radius=4))
p.append(K.text(72, 32, C["brand"], size=22, color="#FFFFFF", bold=True, width=140))
p.append(K.rect(16, 117, 186, 44, color=SIDE_SEL, radius=10))
p.append(K.text(34, 130, "●", size=16, color="#34D399", width=20))
p.append(K.text(58, 128, "Overview", size=17, color="#FFFFFF", bold=True, width=130))
for i, item in enumerate(C["navigation"][1:]):
    y = 190 + i * 62
    p.append(K.text(34, y + 4, "●", size=16, color="#64748B", width=20))
    p.append(K.text(58, y, item, size=17, color="#CBD5E1", width=140))
p.append(K.rect(16, 753, 186, 120, color="#1B2E49", radius=12))
p.append(K.text(38, 770, C["workspace_info"][0], size=12, color="#34D399", bold=True, width=150))
p.append(K.text(38, 794, C["workspace_info"][1], size=15, color="#E2E8F0", width=150))
p.append(K.text(38, 826, C["workspace_info"][2], size=13, color="#94A3B8", width=150))

# ---------------- header
p.append(K.text(261, 33, C["title"], size=32, color=INK, bold=True, width=720))
p.append(K.text(261, 84, C["subtitle"], size=16, color=MUTED, width=520))
p.append(K.rect(1186, 44, 212, 44, color=BLUE, radius=6))
p.append(K.text(1186, 55, C["button"], size=16, color="#FFFFFF", bold=True, width=212, align="CENTER"))

# ---------------- KPI cards
KPI = [(261, 614), (645, 998), (1029, 1382)]
for (x0, x1), kpi in zip(KPI, C["kpis"]):
    p.append(K.rect(x0, 139, x1 - x0, 141, color=CARD, radius=10, border=f"1 SOLID {LINE}"))
    p.append(K.text(x0 + 18, 158, kpi["label"], size=12, color=MUTED, bold=True, width=240))
    p.append(K.text(x0 + 18, 188, kpi["value"], size=32, color=INK, bold=True, width=320))
    color = GREEN if kpi["change"].startswith("+") else GREEN
    p.append(K.text(x0 + 18, 244, kpi["change"], size=14, color=color, bold=True, width=200))

# ---------------- chart card
CX0, CX1, CY0, CY1 = 261, 998, 312, 593
p.append(K.rect(CX0, CY0, CX1 - CX0, CY1 - CY0, color=CARD, radius=10, border=f"1 SOLID {LINE}"))
p.append(K.text(CX0 + 18, 328, C["chart_title"], size=20, color=INK, bold=True, width=300))
p.append(K.text(CX1 - 130, 332, C["chart_period"], size=14, color=MUTED, width=112, align="RIGHT"))
p.append(K.text(CX0 + 18, 368, C["chart_unit"], size=11, color=MUTED, width=120))
AX_L, AX_R = 330, 980
BASE_Y, TOP_Y = 548, 405
for tick in C["chart_ticks"]:
    ty = BASE_Y - (tick / 120) * (BASE_Y - TOP_Y)
    p.append(K.rect(AX_L, round(ty), AX_R - AX_L, 1, color="#E7EDF5"))
    p.append(K.text(288, round(ty) - 8, str(tick), width=42, size=11, color=MUTED, align="RIGHT"))
BAR_W = 54
scale = (BASE_Y - TOP_Y) / 120
for i, (month, val) in enumerate(zip(C["months"], C["chart_values"])):
    bx = 357 + i * 101
    bh = val * scale
    p.append(K.rect(bx, round(BASE_Y - bh), BAR_W, round(bh), color=BLUE, radius=6))
    p.append(K.text(bx - 20, 558, month, width=BAR_W + 40, size=12, color=MUTED, align="CENTER"))

# ---------------- activity card
AX0, AX1, AY0, AY1 = 1029, 1398, 312, 593
p.append(K.rect(AX0, AY0, AX1 - AX0, AY1 - AY0, color=CARD, radius=10, border=f"1 SOLID {LINE}"))
p.append(K.text(AX0 + 18, 328, C["activity_title"], size=20, color=INK, bold=True, width=320))
DOTS = ["#F59E0B", "#2563EB", "#059669"]
for i, (label, when) in enumerate(C["activity"]):
    y = 386 + i * 60
    p.append(K.rect(AX0 + 20, y + 6, 10, 10, color=DOTS[i], radius=5))
    p.append(K.text(AX0 + 36, y, label, size=15, color=INK2, bold=True, width=300))
    p.append(K.text(AX0 + 36, y + 26, when, size=13, color=MUTED, width=200))

# ---------------- table card
TX0, TX1, TY0, TY1 = 261, 1398, 626, 839
p.append(K.rect(TX0, TY0, TX1 - TX0, TY1 - TY0, color=CARD, radius=10, border=f"1 SOLID {LINE}"))
p.append(K.text(TX0 + 18, 640, C["table_title"], size=20, color=INK, bold=True, width=400))
p.append(K.rect(TX0 + 18, 682, TX1 - TX0 - 36, 32, color="#F1F5F9", radius=4))
for label, lx in zip(C["table_columns"], (296, 776, 1040, 1226)):
    p.append(K.text(lx, 690, label, size=11, color=MUTED, bold=True, width=180))
PILL = {"In progress": ("#E7EFFF", "#245CE4"), "Review": ("#FFF3D7", "#9D6613"),
        "Done": ("#DCF5EC", "#0F7A5A")}
for i, row in enumerate(C["rows"]):
    y = 725 + i * 35
    p.append(K.text(296, y + 9, row[0], size=14, color=INK, bold=True, width=420))
    p.append(K.text(776, y + 9, row[1], size=14, color=INK2, width=220))
    bg, fg = PILL[row[2]]
    p.append(K.rect(1028, y + 4, 148, 28, color=bg, radius=14))
    p.append(K.text(1028, y + 10, row[2], size=12, color=fg, bold=True, width=148, align="CENTER"))
    p.append(K.text(1226, y + 9, row[3], size=14, color=MUTED, width=140))
    if i < 2:
        p.append(K.rect(296, y + 31, TX1 - TX0 - 70, 1, color="#F1F5F9"))

p.append(K.text(261, 856, C["footer"], size=12, color=MUTED, width=600))

dsl = K.document(W, H, p, background=MAIN)
snap = OUT / "reconstructed.snapshot"
snap.write_text(dsl, encoding="utf-8")
warn = K.drain_warnings()
logger = api.TaskLogger(TASK, TMP)
rec = logger.render(snap, OUT / "reconstructed.png", "reconstruction v1")
print("render:", rec["http_status"], rec["response_bytes"], rec["elapsed_s"])
for w in warn:
    print("  ", w)
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1200])
    raise SystemExit(1)
print(api.measure_png(OUT / "reconstructed.png"))
