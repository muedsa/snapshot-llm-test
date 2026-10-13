"""B03 case-05 凸版诗句页 - letterpress micro-typography on one broadside.

Real use: a small letterpress studio's specimen broadside for the poetry collection
"潮汐" (the same book case-03 prints a cover proof for). The page has to answer the
questions a client actually asks about pressed type: how deep the bite is, how tight the
leading can go, whether figures stay in a column, and what the paper costs.

Capabilities: textShadow used as an emboss pair (light top-left, dark bottom-right),
letterSpacing / wordSpacing, height as the line multiplier on wrapped copy, WidgetSpan as
an inline rule, Raw spans for preserved indentation, fontFeatures="tnum" for the numbering
column.

Run: python tmp/<run_id>/B03/case05_letterpress.py
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import Sheet, MONO, SERIF, tw, f  # noqa: E402
from snap import C, Node, Positioned, Text  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"
W, H = 820, 1280
PAPER = "#EFE9DC"
INK = "#22201C"
INK2 = "#54504A"
INK3 = "#7C766D"
PRESS = "#8E3B27"          # the ink on the page
RULE = "#B7AF9F"

# the poem: eight lines, each short enough to sit on one measure at 34pt
POEM = [
    "潮水把未印的字", "退回纸的背面；", "铅字咬住纤维，", "像夜咬住港。",
    "我们数着留白", "一毫米，一毫米，", "等到墨色沉下去", "就成了岸。",
]
LEAD_TIGHT = 1.0
LEAD_LOOSE = 1.75
SIZE = 34
MEASURE = 470
X0 = 196                    # text block left edge (numbers live in the left margin)
Y0 = 300
COLOPHON = [
    ("机器", "Heidelberg KSB 三开"),
    ("版材", "树脂凸版 字高 2.48mm"),
    ("纸张", "阿波和纸 210gsm 纵丝缕"),
    ("油墨", "松烟 · PMS 4695 打底"),
    ("压力", "0.06mm 压痕，指腹可触"),
    ("字距", "标题 +0.14em，正文 0"),
    ("行距", f"紧 {LEAD_TIGHT} / 疏 {LEAD_LOOSE}"),
    ("编号", "tnum 行号个位对齐"),
]

s = Sheet(W, H, min_font=17, bg=PAPER)
s.rect(0, 0, W, H, PAPER)

# sheet edge: a hairline frame plus a deckle band so the page reads as paper, not a UI
s.rect(34, 34, W - 68, H - 68, "#00000000", border=f"1 SOLID {RULE}")
s.rect(34, 34, W - 68, 6, PRESS)

# header: pressed title, tracking open, emboss pair consistent across the page
EMB = "-3 -3 0 #FFFFFF, 2 3 0 #3A342B55"
s.rich("title", [("潮", {}), ("汐", {})], X0 - 136, 92, size=86, colour=PRESS,
       shadow=EMB, letterSpacing=10)
s.rich("title", [("TIDE", {"font": MONO})], X0 + 118, 132, size=30,
       colour=INK3, letterSpacing=14)
s.text("title", "凸版印刷样张 · 二〇二六年秋季", X0 - 136, 212, 22, INK2)
s.line(X0 - 136, 252, W - 74, 252, RULE, 1.0)
s.text("title", "《潮汐》诗集 · 第三首", X0 - 136, 262, 20, INK3)

# the poem, numbered in a tnum column, set tight
y = Y0
for i, line in enumerate(POEM):
    s.rich("num", [(f"{i + 1:02d}", {"font": MONO})], 74, y, size=20, colour=INK3,
           features="tnum")
    s.text("poem", line, X0, y, SIZE, INK, font=SERIF)
    y += SIZE * LEAD_TIGHT * 1.46
assert y < 700, y

# a rule that lives inside the line, not between blocks: WidgetSpan on the baseline
s.nodes.append(Positioned(Node("Text", {}, [
    Text("　", fontSize="20", color=PAPER),
    Node("WidgetSpan", {"alignment": "BASELINE", "baseline": "IDEOGRAPHIC"},
         [C(width="300", height="3", color=PRESS)]),
    Text(" 其三 · 终 ", fontSize="20", color=INK3, font=SERIF),
]), left="74", top=f(y + 4)))

# second setting of the same quatrain: two columns, only the line multiplier differs
s.text("spec", "同一段四行，行距倍率对照（左紧右疏）", 74, 742, 20, INK2)
s.rich("spec", [("height = 1.0", {"font": MONO, "size": 17, "colour": INK3})],
       74, 772, size=17)
s.rich("spec", [("height = 1.75", {"font": MONO, "size": 17, "colour": INK3})],
       430, 772, size=17)
for j, line in enumerate(POEM[:4]):
    s.text("tight", line, 74, 800 + j * 21 * LEAD_TIGHT * 1.46, 21, INK, font=SERIF)
for j, line in enumerate(POEM[:4]):
    s.text("loose", line, 430, 800 + j * 21 * LEAD_LOOSE * 1.46, 21, INK, font=SERIF)

# colophon: label column plus a Raw-preserved specimen line showing real indentation
s.line(74, 1042, W - 74, 1042, RULE, 1.0)
for i, (k, v) in enumerate(COLOPHON):
    x = 74 + (i % 2) * 350
    yy = 1062 + (i // 2) * 38
    s.text("colo", k, x, yy, 18, INK3, font=MONO)
    s.text("colo", v, x + 62, yy, 18, INK2)
s.nodes.append(Positioned(Node("Text", {}, [
    Text("排版记录", fontSize="18", color=INK3, font=MONO),
    Node("Raw", {"fontSize": "18", "color": INK2, "fontFamily": MONO}, None,
         "   咬口 6mm   规矩线 3mm   试印 4 张   "),
    Text("机压 2.1", fontSize="18", color=INK2, font=MONO),
]), left="74", top="1206"))

audit = s.audit()
print(json.dumps(audit, ensure_ascii=False))
assert audit["overlap_n"] == 0 and audit["outside_n"] == 0, audit
assert audit["below_min_font_n"] == 0, audit["below_min_font"]
# the two leading demonstrations must actually differ by the multiplier, not by eye
tight_pitch = 21 * LEAD_TIGHT * 1.46
loose_pitch = 21 * LEAD_LOOSE * 1.46
assert loose_pitch - tight_pitch > 12, (tight_pitch, loose_pitch)
dsl = s.dsl() + "\n"
(TMP / "case05-letterpress.snapshot").write_text(dsl, encoding="utf-8")
(TMP / "case05-data.json").write_text(json.dumps(
    {"poem_lines": len(POEM), "char_counts": [len(l) for l in POEM],
     "measure_px": MEASURE, "size_px": SIZE, "lead_tight": LEAD_TIGHT,
     "lead_loose": LEAD_LOOSE, "tight_pitch_px": round(tight_pitch, 2),
     "loose_pitch_px": round(loose_pitch, 2), "colophon_items": len(COLOPHON),
     "emboss": EMB, "elements": s.elements()},
    ensure_ascii=False, indent=2), encoding="utf-8")
print("poem bottom", round(y), "pitches", round(tight_pitch, 1), round(loose_pitch, 1),
      "elements", s.elements())
