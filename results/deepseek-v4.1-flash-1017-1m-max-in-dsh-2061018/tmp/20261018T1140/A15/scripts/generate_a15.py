"""A15 · 1440×900 reference interface reconstruction (DSL only)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A15"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Label, Pos, Row, SizedBox, Stack, T  # noqa: E402

W, H = 1440, 900
SIDEBAR = "#14233C"
BG = "#F3F6FB"
CARD = "#FFFFFF"
BORDER = "#E1E7F0"
INK = "#18283F"
MUTED = "#5B6B84"
FAINT = "#7A8AA3"
BLUE = "#245CE4"
GREEN = "#168267"
GOLD = "#B45309"
NAV = "#294467"
NAVLINE = "#3A5A82"
LOGO = "#64DBB6"
FONT = "Inter,Noto Sans CJK SC"


def card(x, y, w, h, child=None, pad=0):
    return Pos(x, y, C(width=w, height=h, color=CARD, borderRadius=12, border=f"1 SOLID {BORDER}",
                       boxShadow="ELEVATION_1", padding=f"({pad},{pad})" if pad else None, child=child), w=w, h=h)


def kpi(x, w, item):
    return [card(x, 136, w, 145),
            Pos(x + 24, 156, T(item["label"], size=11, color=MUTED, weight="BOLD", family=FONT, spacing=1)),
            Pos(x + 24, 192, T(item["value"], size=32, color=INK, weight="BOLD", family=FONT)),
            Pos(x + 24, 242, T(item["change"], size=14, color=GREEN, weight="BOLD", family=FONT))]


def nav_item(y, label, selected=False):
    parts = [Pos(20, y, C(width=181, height=48, color=NAV if selected else "transparent", borderRadius=9,
                          border=f"1 SOLID {NAVLINE}" if selected else None))]
    parts.append(Pos(40, y + 19, C(width=9, height=9, color=LOGO if selected else "#6E819C", borderRadius=5)))
    parts.append(Pos(62, y + 13, T(label, size=16, color="#F5F8FC" if selected else "#C7D2E3",
                                    weight="BOLD" if selected else None, family=FONT)))
    return parts


def chart(content):
    nodes = [card(260, 311, 741, 285)]
    nodes += [
        Pos(286, 331, T(content["chart_title"], size=21, color=INK, weight="BOLD", family=FONT)),
        Pos(890, 335, T(content["chart_period"], size=14, color=MUTED, family=FONT)),
        Pos(286, 368, T(content["chart_unit"], size=12, color=MUTED, family=FONT)),
    ]
    ticks = [120, 90, 60, 30, 0]
    ys = [405, 441, 477, 513, 549]
    for v, y in zip(ticks, ys):
        nodes.append(Pos(325, y, C(width=645, height=1, color="#E7EDF5")))
        nodes.append(Pos(280, y - 8, Label(str(v), 36, 16, align="CENTER_RIGHT", size=11, color=FAINT, family=FONT)))
    bars = [54, 72, 63, 90, 81, 108]
    for i, (m, v) in enumerate(zip(content["months"], bars)):
        x = 357 + i * 101
        h = round(v * 1.2)
        nodes.append(Pos(x, 549 - h, C(width=54, height=h, color=BLUE, borderRadius=4)))
        nodes.append(Pos(x - 20, 555, Label(m, 94, 20, align="CENTER", size=14, color=MUTED, family=FONT)))
    return nodes


def activity(content):
    nodes = [card(1029, 311, 370, 285),
             Pos(1055, 332, T(content["activity_title"], size=21, color=INK, weight="BOLD", family=FONT))]
    colors = ["#EAAF40", BLUE, GREEN]
    for i, (label, t) in enumerate(content["activity"]):
        y = 390 + i * 44
        nodes.append(Pos(1048, y + 6, C(width=9, height=9, color=colors[i], borderRadius=5)))
        nodes.append(Pos(1078, y, T(label, size=16, color=INK, weight="BOLD", family=FONT)))
        nodes.append(Pos(1078, y + 23, T(t, size=13, color=FAINT, family=FONT)))
    return nodes


def table(content):
    nodes = [card(260, 624, 1139, 224),
             Pos(286, 642, T(content["table_title"], size=21, color=INK, weight="BOLD", family=FONT)),
             Pos(280, 688, C(width=1099, height=33, color=BG, borderRadius=4))]
    xs = [299, 784, 1028, 1232]
    for x, label in zip(xs, content["table_columns"]):
        nodes.append(Pos(x, 694, T(label, size=11, color=FAINT, weight="BOLD", family=FONT, spacing=1)))
    status_bg = {"In progress": ("#E7EFFF", BLUE), "Review": ("#FFF3D7", GOLD), "Done": ("#DCF5EC", GREEN)}
    for i, row in enumerate(content["rows"]):
        y = 722 + i * 35
        if i > 0:
            nodes.append(Pos(280, y, C(width=1099, height=1, color="#E1E7F0")))
        nodes.append(Pos(299, y + 9, T(row[0], size=15, color=INK, family=FONT)))
        nodes.append(Pos(784, y + 9, T(row[1], size=15, color=MUTED, family=FONT)))
        bg, fg = status_bg[row[2]]
        nodes.append(Pos(1028, y + 7, C(width=147, height=27, color=bg, borderRadius=6, alignment="CENTER",
                                        child=T(row[2], size=12, color=fg, weight="BOLD", family=FONT))))
        nodes.append(Pos(1232, y + 9, T(row[3], size=15, color=MUTED, family=FONT)))
    return nodes


def main() -> int:
    content = json.loads((ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "content.json").read_text(encoding="utf-8"))
    nodes = [SizedBox(W, H),
             Pos(0, 0, C(width=220, height=900, color=SIDEBAR)),
             Pos(30, 30, C(width=26, height=26, color="transparent", border=f"3 SOLID {LOGO}", borderRadius=7)),
             Pos(37, 37, C(width=12, height=12, color="transparent", border="3 SOLID #F5F8FC", borderRadius=2)),
             Pos(68, 38, T(content["brand"], size=17, color="#F5F8FC", weight="BOLD", family=FONT, spacing=2)),
             Pos(20, 748, C(width=180, height=128, color="#1B2E4A", borderRadius=10)),
             Pos(36, 766, T(content["workspace_info"][0], size=11, color=LOGO, weight="BOLD", family=FONT, spacing=1)),
             Pos(36, 790, T(content["workspace_info"][1], size=16, color="#F5F8FC", family=FONT)),
             Pos(36, 820, T(content["workspace_info"][2], size=13, color="#9FB0C8", family=FONT)),
             Pos(260, 32, T(content["title"], size=32, color=INK, weight="BOLD", family=FONT)),
             Pos(260, 80, T(content["subtitle"], size=16, color=MUTED, family=FONT)),
             Pos(1184, 45, C(width=216, height=44, color=BLUE, borderRadius=8, alignment="CENTER",
                             child=T(content["button"], size=15, color="#FFFFFF", weight="BOLD", family=FONT))),
             Pos(261, 863, T(content["footer"], size=12, color=FAINT, family=FONT))]
    for i, (label, y) in enumerate(zip(content["navigation"], [115, 183, 243, 303])):
        nodes += nav_item(y, label, i == 0)
    for i, k in enumerate(content["kpis"]):
        nodes += kpi([260, 643, 1028][i], [354, 356, 355][i], k)
    nodes += chart(content)
    nodes += activity(content)
    nodes += table(content)
    dsl = f'<Snapshot type="png" background="{BG}">\n' + Stack(nodes, width=W, height=H) + "\n</Snapshot>\n"
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    (TMP / "renders").mkdir(parents=True, exist_ok=True)
    (TMP / "dsl" / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
    print("A15", VERSION, "written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
