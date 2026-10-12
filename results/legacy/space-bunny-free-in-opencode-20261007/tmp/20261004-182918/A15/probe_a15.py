"""A15 probe v00: calibrate DSL Text ink offsets + verify special glyphs.

Renders known strings at known box coords on white, then measure_probe.py reads the
PNG and reports ink bbox vs box origin so build_a15.py can place text by ink.
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402

TASK = "A15"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", TASK)
TMP = os.path.join(ROOT, "tmp", "20261004-182918", TASK)
snapkit.configure(TASK, OUT, TMP)

INTER = "Inter"
SEMI = "Inter Semi Bold"
MED = "Inter Medium"
BLACK = "Inter Black"

# (key, text, font, size, letterSpacing, x, y, w, h, color)
PROBES = [
    # size sweep on the page title (ref ink w=335 h=32, capTop=38, descBottom=69)
    ("title32", "Workspace Overview", SEMI, 32, 0, 40, 40, 700, 60, "#18283FFF"),
    ("title33", "Workspace Overview", SEMI, 33, 0, 40, 120, 700, 60, "#18283FFF"),
    ("title34", "Workspace Overview", SEMI, 34, 0, 40, 200, 700, 60, "#18283FFF"),
    ("title35", "Workspace Overview", SEMI, 35, 0, 40, 280, 700, 60, "#18283FFF"),
    # weights at 33
    ("t33inter", "Workspace Overview", INTER, 33, 0, 40, 350, 700, 60, "#18283FFF"),
    ("t33med", "Workspace Overview", MED, 33, 0, 40, 420, 700, 60, "#18283FFF"),
    # subtitle (ref ink w=246 h=18, top=85)
    ("sub16", "Saturday, 07 November 2026", INTER, 16, 0, 760, 40, 500, 40, "#63748FFF"),
    ("sub17", "Saturday, 07 November 2026", INTER, 17, 0, 760, 90, 500, 40, "#63748FFF"),
    # kpi label (ref ink w=65 h=12, top=160, uppercase)
    ("lbl13ls", "REVENUE", SEMI, 13, 0.6, 760, 140, 300, 30, "#63748FFF"),
    ("lbl13", "REVENUE", SEMI, 13, 0, 760, 180, 300, 30, "#63748FFF"),
    ("lbl14ls", "REVENUE", SEMI, 14, 0.6, 760, 220, 300, 30, "#63748FFF"),
    # kpi value (ref ink w=149 h=30, top=199)
    ("val30", "\u00a5128,400", SEMI, 30, 0, 760, 260, 400, 50, "#18283FFF"),
    ("val30i", "\u00a5128,400", INTER, 30, 0, 760, 320, 400, 50, "#18283FFF"),
    # kpi change (ref ink w=57 h=13, top=246)
    ("chg14", "+12.4%", MED, 14, 0, 40, 500, 300, 30, "#168267FF"),
    ("chg15", "+12.4%", MED, 15, 0, 40, 540, 300, 30, "#168267FF"),
    ("chg14s", "+12.4%", SEMI, 14, 0, 40, 580, 300, 30, "#168267FF"),
    # card titles (ref ink h=17 top=336, w: Net revenue 129)
    ("ct18s", "Net revenue", SEMI, 18, 0, 760, 390, 400, 40, "#18283FFF"),
    ("ct18", "Net revenue", INTER, 18, 0, 760, 440, 400, 40, "#18283FFF"),
    ("ct17s", "Net revenue", SEMI, 17, 0, 760, 490, 400, 40, "#18283FFF"),
    # period (ref ink w=78 h=17 top=337)
    ("pe15", "Apr \u2013 Sep", INTER, 15, 0, 40, 630, 400, 40, "#7E8CA2FF"),
    ("pe16", "Apr \u2013 Sep", INTER, 16, 0, 40, 680, 400, 40, "#7E8CA2FF"),
    # unit (ref ink w=70 h=11 top=375)
    ("un12", "\u00a5 thousand", INTER, 12, 0, 760, 630, 400, 30, "#929EB1FF"),
    ("un13", "\u00a5 thousand", INTER, 13, 0, 760, 670, 400, 30, "#929EB1FF"),
    # y tick (ref ink w=22 h=10)
    ("tk12", "120", INTER, 12, 0, 760, 710, 200, 30, "#63748FFF"),
    ("tk13", "120", INTER, 13, 0, 760, 750, 200, 30, "#63748FFF"),
    # month label (ref ink h=14, w Apr=23)
    ("mo13", "Apr", INTER, 13, 0, 760, 790, 200, 30, "#63748FFF"),
    ("mo14", "Apr", INTER, 14, 0, 40, 830, 200, 30, "#63748FFF"),
    # activity (ref title ink h? rows; time ink)
    ("at15", "Design review", SEMI, 15, 0, 760, 860, 400, 30, "#18283FFF"),
    ("tm13", "08:40", INTER, 13, 0, 40, 20, 200, 30, "#63748FFF"),
    # table
    ("tp18s", "Recent projects", SEMI, 18, 0, 300, 20, 400, 40, "#18283FFF"),
    ("ch11ls", "PROJECT", SEMI, 11, 0.7, 700, 20, 300, 30, "#63748FFF"),
    ("ch11", "PROJECT", SEMI, 11, 0, 700, 60, 300, 30, "#63748FFF"),
    ("rw14s", "Atlas / Visual system", SEMI, 14, 0, 700, 100, 400, 30, "#18283FFF"),
    ("rw14", "Atlas / Visual system", INTER, 14, 0, 700, 140, 400, 30, "#18283FFF"),
    ("ow14", "Lin Chuan", INTER, 14, 0, 700, 180, 300, 30, "#63748FFF"),
    # status pill text
    ("sp12", "In progress", SEMI, 12, 0, 1100, 20, 300, 30, "#245CE4FF"),
    ("sp12m", "In progress", MED, 12, 0, 1100, 60, 300, 30, "#245CE4FF"),
    # sidebar brand
    ("bn15", "NORTHSTAR", BLACK, 15, 1.0, 1100, 100, 300, 30, "#FFFFFFFF"),
    ("bn15s", "NORTHSTAR", SEMI, 15, 1.0, 1100, 140, 300, 30, "#FFFFFFFF"),
    # button text (ref ink w=110 h=17)
    ("bt15", "Export report", SEMI, 15, 0, 1100, 180, 300, 30, "#FFFFFFFF"),
    ("bt16", "Export report", SEMI, 16, 0, 1100, 220, 300, 30, "#FFFFFFFF"),
    # special glyph tests
    ("g_arrow", "Manage access  \u2192", INTER, 13, 0, 1100, 260, 400, 30, "#14233CFF"),
    ("g_minus", "\u22120.8 pp", MED, 14, 0, 1100, 300, 300, 30, "#168267FF"),
    ("g_yen", "\u00a5128,400", INTER, 30, 0, 1100, 340, 400, 50, "#14233CFF"),
    ("g_middot", "All data is fictional \u00b7 Snapshot benchmark", INTER, 12, 0, 1100, 400, 500, 30, "#63748FFF"),
    ("g_middot13", "All data is fictional \u00b7 Snapshot benchmark", INTER, 13, 0, 1100, 440, 500, 30, "#63748FFF"),
    ("g_navi", "Overview", SEMI, 15, 0, 1100, 480, 300, 30, "#14233CFF"),
    ("g_side1", "PRO WORKSPACE", SEMI, 11, 1.0, 1100, 520, 300, 30, "#5CCAABFF"),
    ("g_side2", "12 team members", INTER, 14, 0, 1100, 560, 300, 30, "#B0C2D6FF"),
    ("g_side3", "Lin Chuan", INTER, 14, 0, 1100, 600, 300, 30, "#B0C2D6FF"),
    ("g_done", "Done", SEMI, 12, 0, 1100, 640, 300, 30, "#168267FF"),
]

kids = []
meta = []
for key, text, font, size, ls, x, y, w, h, color in PROBES:
    extra = {}
    if ls:
        extra["letterSpacing"] = ls
    kids.append(D.text_el(text, x=x, y=y, w=w, h=h, color=color, size=size,
                          font=font, extra=extra or None, tag="Positioned"))
    meta.append({"key": key, "text": text, "font": font, "size": size,
                 "ls": ls, "box": [x, y, w, h], "color": color})

dsl = D.snapshot([D.stack(kids, 1440, 900)], 1440, 900, bg="#FFFFFFFF")
draft = os.path.join(TMP, "drafts", "v00-probe.snapshot")
os.makedirs(os.path.dirname(draft), exist_ok=True)
with open(draft, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)

import json  # noqa: E402
with open(os.path.join(TMP, "probe-meta.json"), "w", encoding="utf-8") as fh:
    json.dump(meta, fh, ensure_ascii=False, indent=1)

r = snapkit.render(dsl, "probe-v00.png", "probe-v00.snapshot",
                   final=False, out_dir=os.path.join(TMP, "probes"))
print("render", r.get("ok"), r.get("status"), r.get("error"), r.get("bytes"))
for w in D.warnings():
    print("WARN", w)
