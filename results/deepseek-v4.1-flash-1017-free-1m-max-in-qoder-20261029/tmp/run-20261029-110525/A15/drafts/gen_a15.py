#!/usr/bin/env python3
"""A15 reference reconstruction: 1440x900 NORTHSTAR dashboard."""
import json, os, html
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A15"
OUT.mkdir(parents=True, exist_ok=True)
C = json.loads((SUITE_ROOT / "tasks/A15-reference-reconstruction/inputs/content.json").read_text(encoding="utf-8"))

def esc(s): return html.escape(str(s), quote=False)
FS = 0.78

def T(txt, size, color="#0B1220", bold=False, extra=""):
    st = ' fontStyle="BOLD"' if bold else ""
    sz = max(1, round(size * FS))
    return f'<Text fontFamily="Inter,Noto Sans CJK SC" fontSize="{sz}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

BG = "#F3F6FB"; INK = "#0B1220"; MUT = "#64748B"; BLUE = "#245CE4"; SIDE = "#14233C"; CARD = "#FFFFFF"; BORDER = "#E3E9F1"
W, H = 1440, 900
p = ['<Snapshot background="#F3F6FB" type="png">', f'<Container width="{W}" height="{H}"><Stack alignment="TOP_LEFT"><Container width="{W}" height="{H}" color="{BG}"/>']
# sidebar
p.append('<Positioned left="0" top="0" width="220" height="900"><Container width="220" height="900" color="#14233C"/></Positioned>')
p.append('<Positioned left="26" top="31" width="28" height="28"><Container width="28" height="28" color="#64DBB6" borderRadius="8"><Container width="14" height="14" color="#14233C" borderRadius="3" margin="(7,7,7,7)"/></Container></Positioned>')
p.append('<Positioned left="64" top="35">' + T("NORTHSTAR", 20, "#FFFFFF", True, ' letterSpacing="1.5"') + '</Positioned>')
# nav
p.append('<Positioned left="18" top="116" width="184" height="48"><Container width="184" height="48" color="#294467" borderRadius="10"/></Positioned>')
p.append('<Positioned left="35" top="129" width="10" height="10"><Container width="10" height="10" color="#64DBB6" shape="CIRCLE"/></Positioned>')
p.append('<Positioned left="63" top="124">' + T("Overview", 20, "#FFFFFF", True) + '</Positioned>')
for i, (name, y) in enumerate([("Projects", 182), ("Analytics", 250), ("Settings", 318)]):
    p.append(f'<Positioned left="35" top="{y+5}" width="10" height="10"><Container width="10" height="10" color="#64748B" shape="CIRCLE"/></Positioned>')
    p.append(f'<Positioned left="63" top="{y}">' + T(name, 20, "#B0BAC7") + '</Positioned>')
# workspace card
p.append('<Positioned left="18" top="748" width="184" height="130"><Container width="184" height="130" color="#1B2A43" borderRadius="10"/></Positioned>')
p.append('<Positioned left="36" top="764">' + T("PRO WORKSPACE", 12, "#64DBB6", True, ' letterSpacing="1.2"') + '</Positioned>')
p.append('<Positioned left="36" top="788">' + T(C["workspace_info"][1], 18, "#FFFFFF", True) + '</Positioned>')
p.append('<Positioned left="36" top="818">' + T(C["workspace_info"][2], 16, "#B0BAC7") + '</Positioned>')
# main header
p.append('<Positioned left="261" top="32">' + T(C["title"], 41, INK, True, ' letterSpacing="-0.1"') + '</Positioned>')
p.append('<Positioned left="261" top="82">' + T(C["subtitle"], 22, MUT) + '</Positioned>')
p.append('<Positioned left="1184" top="43" width="216" height="47"><Container width="216" height="47" color="#245CE4" borderRadius="8" alignment="CENTER">' + T(C["button"], 20, "#FFFFFF", True) + '</Container></Positioned>')
# KPI cards
kpis = C["kpis"]
for i, k in enumerate(kpis):
    x = [261, 645, 1029][i]; w = [354, 353, 353][i]
    p.append(f'<Positioned left="{x}" top="139"><Container width="{w}" height="141" color="{CARD}" borderRadius="12" border="1 SOLID {BORDER}"><Stack alignment="TOP_LEFT"><Container width="{w}" height="141" color="{CARD}"/>')
    p.append(f'<Positioned left="24" top="22">' + T(k["label"], 14, "#64748B", True, ' letterSpacing="1.2"') + '</Positioned>')
    p.append(f'<Positioned left="24" top="53">' + T(k["value"], 41, INK, True) + '</Positioned>')
    p.append(f'<Positioned left="24" top="109">' + T(k["change"], 18, "#16A34A", True) + '</Positioned>')
    p.append('</Stack></Container></Positioned>')
# chart card
p.append('<Positioned left="261" top="311"><Container width="739" height="283" color="#FFFFFF" borderRadius="12" border="1 SOLID #E3E9F1"><Stack alignment="TOP_LEFT"><Container width="739" height="283" color="#FFFFFF"/>')
p.append('<Positioned left="24" top="20">' + T(C["chart_title"], 24, INK, True) + '</Positioned>')
p.append('<Positioned left="539" top="24" width="176"><Container width="176" alignment="CENTER_RIGHT">' + T(C["chart_period"], 18, "#94A3B8") + '</Container></Positioned>')
p.append('<Positioned left="24" top="56">' + T(C["chart_unit"], 14, "#94A3B8") + '</Positioned>')
plot_l, plot_r = 73, 659  # card-local
zero_y, top_y = 237, 95   # card-local; 120 at 95
def yv(v): return zero_y - v / 120 * (zero_y - top_y)
for tick in C["chart_ticks"]:
    gy = yv(tick)
    p.append(f'<Positioned left="0" top="{gy-9:.1f}" width="60"><Container width="60" alignment="CENTER_RIGHT">' + T(str(tick), 14, "#94A3B8") + '</Container></Positioned>')
    p.append(f'<Positioned left="{plot_l}" top="{gy:.1f}" width="{plot_r-plot_l}" height="1"><Container width="{plot_r-plot_l}" height="1" color="{"#CBD5E1" if tick == 0 else "#E8EDF4"}"/></Positioned>')
centers = [122.5 + 101 * i for i in range(6)]
for i, (m, v) in enumerate(zip(C["months"], C["chart_values"])):
    cx = centers[i]; bw = 54; bh = v / 120 * (zero_y - top_y)
    p.append(f'<Positioned left="{cx-bw/2:.1f}" top="{zero_y-bh:.1f}" width="{bw}" height="{bh:.1f}"><Container width="{bw}" height="{bh:.1f}" color="#245CE4" borderRadiusTopLeft="6" borderRadiusTopRight="6"/></Positioned>')
    p.append(f'<Positioned left="{cx-40:.1f}" top="{zero_y+14}" width="80"><Container width="80" alignment="CENTER">' + T(m, 18, "#475569") + '</Container></Positioned>')
p.append('</Stack></Container></Positioned>')
# activity card
p.append('<Positioned left="1031" top="311"><Container width="367" height="283" color="#FFFFFF" borderRadius="12" border="1 SOLID #E3E9F1"><Stack alignment="TOP_LEFT"><Container width="367" height="283" color="#FFFFFF"/>')
p.append('<Positioned left="24" top="20">' + T(C["activity_title"], 24, INK, True) + '</Positioned>')
cols = ["#F6B94A", "#245CE4", "#16A34A"]
for i, (name, tm) in enumerate(C["activity"]):
    y = 78 + i * 57
    p.append(f'<Positioned left="24" top="{y}" width="10" height="10"><Container width="10" height="10" color="{cols[i]}" shape="CIRCLE"/></Positioned>')
    p.append(f'<Positioned left="48" top="{y-8}">' + T(name, 20, INK, True) + '</Positioned>')
    p.append(f'<Positioned left="48" top="{y+18}">' + T(tm, 16, "#94A3B8") + '</Positioned>')
p.append('</Stack></Container></Positioned>')
# table card
p.append('<Positioned left="261" top="625"><Container width="1137" height="215" color="#FFFFFF" borderRadius="12" border="1 SOLID #E3E9F1"><Stack alignment="TOP_LEFT"><Container width="1137" height="215" color="#FFFFFF"/>')
p.append('<Positioned left="24" top="18">' + T(C["table_title"], 24, INK, True) + '</Positioned>')
p.append('<Positioned left="24" top="63" width="1089" height="34"><Container width="1089" height="34" color="#F3F6FB" borderRadius="4"/></Positioned>')
for label, x in [("PROJECT", 32), ("OWNER", 509), ("STATUS", 752), ("DUE", 979)]:
    p.append(f'<Positioned left="{x}" top="70">' + T(label, 12, "#64748B", True, ' letterSpacing="1"') + '</Positioned>')
chip_bg = ["#E7EFFF", "#FFF3D7", "#DCF5EC"]; chip_fg = ["#245CE4", "#9D6613", "#168267"]
for i, row in enumerate(C["rows"]):
    y = 97 + i * 35
    p.append(f'<Positioned left="24" top="{y+33}" width="1089" height="1"><Container width="1089" height="1" color="#EEF2F7"/></Positioned>')
    p.append(f'<Positioned left="32" top="{y+9}">' + T(row[0], 20, INK, True) + '</Positioned>')
    p.append(f'<Positioned left="509" top="{y+9}">' + T(row[1], 18, "#475569") + '</Positioned>')
    p.append(f'<Positioned left="767" top="{y+7}" width="148" height="28"><Container width="148" height="28" color="{chip_bg[i]}" borderRadius="6" alignment="CENTER">' + T(row[2], 16, chip_fg[i], True) + '</Container></Positioned>')
    p.append(f'<Positioned left="979" top="{y+9}">' + T(row[3], 18, "#64748B") + '</Positioned>')
p.append('</Stack></Container></Positioned>')
p.append('<Positioned left="261" top="864">' + T(C["footer"], 16, "#94A3B8") + '</Positioned>')
p.append('</Stack></Container></Snapshot>')
dsl = "\n".join(p)
(OUT / "reconstructed.snapshot").write_text(dsl, encoding="utf-8")
print("wrote A15", len(dsl))
