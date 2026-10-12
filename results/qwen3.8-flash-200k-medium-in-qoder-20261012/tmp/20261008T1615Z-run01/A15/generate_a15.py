"""A15 step 2 — build the Snapshot DSL reconstruction from the measured anchors.

Every coordinate below comes from tmp/<rid>/A15/measure-ref.json (projection segmentation of
reference.png) or from the follow-up single-feature probes recorded in measure-report.txt.
The reference image is never embedded or cropped: the whole scene is rebuilt from Containers,
Text and a few Transform-free primitives, so the geometry stays editable and measurable.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A15"
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
from dslkit import Doc, TextFit  # noqa: E402

M = json.loads((TEMP / "measure-ref.json").read_text(encoding="utf-8"))
C = M["colours"]

INK = "#18283F"
MUTED = "#63748F"
SOFT = "#7B8BA3"
BLUE = "#245CE4"
GREEN = "#168267"
AMBER = "#EAAF40"
BRAND = "#64DBB6"
SIDEBAR = C["sidebar"]
PILL_NAV = C["nav_selected_pill"]
PAGE = C["page_bg"]
CARD = C["card"]
WS = C["workspace_card"]
GRID = "#E7EDF5"
NAV_TXT = "#BECADD"
NAV_DARK = "#8FA3C0"
SHADOW = None            # reference cards are flat with a 1px hairline edge
EDGE = "#E2E8F1"

FAM = {"reg": "Inter,Noto Sans CJK SC",
       "med": "Inter Medium,Noto Sans CJK SC",
       "sem": "Inter Semi Bold,Noto Sans CJK SC"}

doc = Doc(1440, 900, bg=PAGE, font=FAM["reg"])
FIT = TextFit()


def txt(x, y, w, h, s, size, color=INK, fam="reg", align="START", valign="MIDDLE",
        spacing=None, maxlines=1):
    """fam "bol" = Inter + fontStyle BOLD; the reference is a bold-weight UI and
    Inter Semi Bold alone measured ~15% narrower per glyph run."""
    old = doc.font
    doc.font = FAM["reg"] if fam == "bol" else FAM[fam]
    try:
        doc.label(x, y, w, h, s, color=color, size=size, align=align, valign=valign,
                  spacing=spacing, maxlines=maxlines,
                  style="BOLD" if fam == "bol" else None)
    finally:
        doc.font = old
    FIT.check(f"{s[:14]}", s, size, w, h, lines=maxlines)


def rect(x, y, w, h, color, radius=None, shadow=None, edge=None):
    doc.pos(x, y, w, h, doc.box(w, h, color=color, radius=radius, shadow=shadow,
                        border=f"1 SOLID {edge}" if edge else None))


# ---------------------------------------------------------------- sidebar
rect(0, 0, 220, 900, SIDEBAR)
rect(30, 32, 28, 28, BRAND, radius=8)          # brand mark is a ring, not a solid chip
rect(39, 41, 10, 10, SIDEBAR, radius=3)
txt(68, 30, 150, 34, "NORTHSTAR", 17, "#FFFFFF", "bol", spacing=1.6)

NAV = [("Overview", 134.0), ("Projects", 199.0), ("Analytics", 263.0), ("Settings", 327.5)]
rect(18, 116, 184, 48, PILL_NAV, radius=10)
for i, (name, cy) in enumerate(NAV):
    doc.dot(40, cy, 11, BRAND if i == 0 else "#7494B4")
    txt(62, cy - 13, 140, 26, name, 19, "#FFFFFF" if i == 0 else NAV_TXT,
        "bol" if i == 0 else "med")

# workspace card inside the sidebar
WX, WY, WW, WH = 22, 752, 176, 116
rect(WX, WY, WW, WH, WS, radius=10)
txt(WX + 16, 764, WW - 28, 20, "PRO WORKSPACE", 12, BRAND, "bol", spacing=1.0)
txt(WX + 16, 798, WW - 28, 24, "12 team members", 15.5, "#FFFFFF", "bol")
txt(WX + 16, 831, WW - 28, 22, "Manage access  →", 13, "#B3C5D8", "med")

# ---------------------------------------------------------------- header
txt(260, 31, 400, 42, "Workspace Overview", 32, INK, "bol")
txt(260, 81, 300, 24, "Saturday, 07 November 2026", 18, MUTED, "reg")
rect(1184, 43, 216, 48, BLUE, radius=10)
txt(1184, 37, 216, 48, "Export report", 16, "#FFFFFF", "bol", align="CENTER")

# ---------------------------------------------------------------- kpis
KPI = [(260, "REVENUE", "¥128,400", "+12.4%"),
       (644, "ORDERS", "426", "+8.1%"),
       (1028, "REFUND RATE", "3.2%", "−0.8 pp")]
for x, label, value, delta in KPI:
    rect(x, 138, 356, 144, CARD, radius=12, edge=EDGE)
    txt(x + 25, 157, 300, 17, label, 12.5, MUTED, "bol", spacing=0.9)
    txt(x + 25, 192, 306, 38, value, 32, INK, "bol")
    txt(x + 25, 242, 300, 22, delta, 16, GREEN, "bol")

# ---------------------------------------------------------------- chart card
CX, CY, CW, CH = 260, 310, 742, 286
rect(CX, CY, CW, CH, CARD, radius=12, edge=EDGE)
txt(CX + 25, 330, 240, 24, "Net revenue", 22, INK, "bol")
txt(CX + 27, 371, 160, 16, "¥ thousand", 13, MUTED, "reg")
txt(700, 332, 273, 24, "Apr – Sep", 17, MUTED, "reg", align="END")

ZERO, SCALE, GX0, GX1 = 549, 1.2, 333, 969
for tick in [120, 90, 60, 30, 0]:
    y = ZERO - SCALE * tick
    doc.rect(GX0, int(round(y)), GX1 - GX0 + 1, 1, GRID)
    txt(270, y - 11, 52, 16, str(tick), 13, MUTED, "reg", align="END")

MONTHS = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"]
VALUES = [54, 72, 63, 90, 81, 108]
BX0, BW, PITCH = 357, 54, 101
for i, v in enumerate(VALUES):
    x = BX0 + i * PITCH
    top = round(ZERO - SCALE * v)
    doc.pos(x, top, BW, ZERO - top, doc.box(BW, ZERO - top, color=BLUE, radius=4))
    txt(x - 20, 556, 94, 20, MONTHS[i], 14, MUTED, "reg", align="CENTER")

# ---------------------------------------------------------------- activity card
AX, AY, AW, AH = 1030, 310, 370, 286
rect(AX, AY, AW, AH, CARD, radius=12, edge=EDGE)
txt(AX + 25, 331, 250, 24, "Team activity", 22, INK, "bol")
ACT = [("Design review", "08:40", AMBER), ("Dataset updated", "09:15", BLUE),
       ("Render complete", "10:05", GREEN)]
for i, (name, when, col) in enumerate(ACT):
    cy = 403 + 60 * i
    doc.dot(1058.5, cy - 1.5, 10, col)
    txt(1078, cy - 14, 300, 24, name, 17, INK, "bol")
    txt(1078, cy + 14, 300, 20, when, 14, MUTED, "reg")

# ---------------------------------------------------------------- table card
TX, TY, TW, TH_ = 260, 624, 1140, 218
rect(TX, TY, TW, TH_, CARD, radius=12, edge=EDGE)
txt(TX + 25, 641, 300, 26, "Recent projects", 22, INK, "bol")
rect(284, 689, 1090, 33, PAGE, radius=8)
COLS = [(299, "PROJECT", "START"), (783, "OWNER", "START"),
        (1034, "STATUS", "START"), (1231, "DUE", "START")]
for x, name, _ in COLS:
    txt(x, 692, 220, 20, name, 11, MUTED, "bol", spacing=0.8)

ROWS = [("Atlas / Visual system", "Lin Chuan", "In progress", "Nov 09",
         "#E7EFFF", BLUE),
        ("Pulse / Dashboard", "Zhou He", "Review", "Nov 11", "#FFF3D7", "#9D6613"),
        ("Orbit / Launch", "Su Yan", "Done", "Nov 12", "#DCF5EC", GREEN)]
for i, (proj, owner, status, due, pbg, ptxt) in enumerate(ROWS):
    cy = 742 + 34.5 * i
    if i:
        doc.rect(284, int(cy - 18), 1090, 1, "#EBEFF5")
    txt(299, cy - 14, 460, 24, proj, 16, INK, "bol")
    txt(783, cy - 13, 240, 22, owner, 16, MUTED, "reg")
    rect(1028, cy - 14, 148, 28, pbg, radius=8)
    txt(1028, cy - 14, 148, 28, status, 14, ptxt, "bol", align="CENTER")
    txt(1231, cy - 13, 140, 22, due, 16, MUTED, "reg")

txt(260, 862, 400, 22, "All data is fictional · Snapshot benchmark", 13, SOFT, "reg")

DSL_PATH = TEMP / "reconstructed.snapshot"
DSL_PATH.write_text(doc.dsl(), encoding="utf-8")
print("fit problems:", FIT.problems or "none")
print("bytes:", DSL_PATH.stat().st_size)
