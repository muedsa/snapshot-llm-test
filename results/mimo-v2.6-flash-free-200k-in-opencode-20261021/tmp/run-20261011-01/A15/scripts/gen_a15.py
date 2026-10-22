# -*- coding: utf-8 -*-
"""A15 reconstruction DSL generator.

Builds reconstructed.snapshot (1440x900) from constants measured off the
public reference.png (reference-measured.json / detail-measured*.json /
texts-reference.json). Text boxes are positioned from reference glyph
targets plus optional calibration offsets (calib.json) produced by
compare_texts.py after a render+measure cycle.

Usage:
  python gen_a15.py --dsl <path> [--calib <json>]
"""
import argparse
import json
import pathlib

ROOT = pathlib.Path(".")
TMP = ROOT / "tmp" / "run-20261011-01" / "A15"

W, H = 1440, 900

BG = "#F3F6FB"
SIDEBAR = "#14233C"
NAV_PILL = "#294467"
WS_CARD = "#233954"
GREEN_MINT = "#64DBB6"      # logo / selected dot / workspace label (100,219,182)
DOT_SLATE = "#7791B3"       # nav unselected dot (119,145,179)
NAV_TEXT = "#BECADD"        # nav unselected text (190,202,221)
WS_MUTED = "#B8CADD"        # workspace manage line (184,202,221)
DARK = "#18283F"            # headings / values / row projects (24,40,63)
MUTED = "#63748F"           # secondary text (99,116,143)
GREEN_TXT = "#168267"       # positive change (22,130,103)
BLUE = "#245CE4"            # primary blue (36,92,228)
CARD_BORDER = "#E2E8F1"     # (226,232,241)
GRID = "#E7EDF5"            # (231,237,245)
SEPARATOR = "#EBEFF5"       # (235,239,245)
FOOTER_TXT = "#7B8BA3"      # (123,139,163)
AMBER = "#EAAF40"           # (234,175,64)
PILL_PROGRESS_BG, PILL_PROGRESS_FG = "#E7EFFF", "#245CE4"
PILL_REVIEW_BG, PILL_REVIEW_FG = "#FFF3D7", "#9D6613"
PILL_DONE_BG, PILL_DONE_FG = "#DCF5EC", "#168267"

CARD_BORDER_ATTR = f"1 SOLID {CARD_BORDER}"


def rect(x, y, w, h, color, radius=0, border=None):
    a = f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">' \
        f'<Container color="{color}"'
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    return a + "/></Positioned>"


# ---------------------------------------------------------------- shapes
def shapes():
    s = [rect(0, 0, W, H, BG)]
    # sidebar + logo + nav
    s.append(rect(0, 0, 220, H, SIDEBAR))
    s.append(rect(30, 33, 28, 28, GREEN_MINT, radius=8))
    s.append(rect(37, 40, 13, 13, SIDEBAR, radius=4))
    s.append(rect(18, 116, 184, 48, NAV_PILL, radius=7))
    s.append(rect(34, 128, 12, 12, GREEN_MINT, radius=6))
    for dy in (192, 256, 320):
        s.append(rect(34, dy, 12, 12, DOT_SLATE, radius=6))
    # workspace card
    s.append(rect(22, 752, 176, 116, WS_CARD, radius=10))
    # header button
    s.append(rect(1184, 43, 216, 48, BLUE, radius=7))
    # KPI cards
    for left in (260, 644, 1028):
        s.append(rect(left, 138, 356, 144, "#FFFFFF", radius=11,
                      border=CARD_BORDER_ATTR))
    # chart / activity / table cards
    s.append(rect(260, 310, 742, 286, "#FFFFFF", radius=11,
                  border=CARD_BORDER_ATTR))
    s.append(rect(1030, 310, 370, 286, "#FFFFFF", radius=11,
                  border=CARD_BORDER_ATTR))
    s.append(rect(260, 624, 1140, 218, "#FFFFFF", radius=11,
                  border=CARD_BORDER_ATTR))
    # table band + separators
    s.append(rect(284, 688, 1090, 34, BG, radius=8))
    s.append(rect(284, 760, 1090, 1, SEPARATOR))
    s.append(rect(284, 795, 1090, 1, SEPARATOR))
    # chart gridlines (y = 405/441/477/513/549; x 333..969)
    for gy in (405, 441, 477, 513, 549):
        s.append(rect(333, gy, 637, 1, GRID))
    # bars: y = 549 - value*1.2, bottom pixel 548; Jun/Sep use the
    # reference's rounded-up tops (474/420) to match measured strict-blue
    for x, top in ((357, 484), (458, 463), (559, 474),
                   (660, 441), (761, 452), (862, 420)):
        s.append(rect(x, top, 54, 549 - top, BLUE, radius=6))
    # status pills
    s.append(rect(1028, 729, 148, 28, PILL_PROGRESS_BG, radius=6))
    s.append(rect(1028, 764, 148, 28, PILL_REVIEW_BG, radius=6))
    s.append(rect(1028, 799, 148, 28, PILL_DONE_BG, radius=6))
    # activity dots
    s.append(rect(1054, 397, 10, 10, AMBER, radius=5))
    s.append(rect(1054, 457, 10, 10, BLUE, radius=5))
    s.append(rect(1054, 517, 10, 10, GREEN_TXT, radius=5))
    return s


# ---------------------------------------------------------------- texts
# weight: reg -> Inter, sb -> Inter Semi Bold, bold -> Inter + fontStyle BOLD
TEXT_SPECS = {
    "northstar":     ("NORTHSTAR", 19, "#FFFFFF", "bold"),
    "nav_overview":  ("Overview", 19, "#FFFFFF", "bold"),
    "nav_projects":  ("Projects", 19, NAV_TEXT, "reg"),
    "nav_analytics": ("Analytics", 19, NAV_TEXT, "reg"),
    "nav_settings":  ("Settings", 19, NAV_TEXT, "reg"),
    # weights after visual crops: reference uses BOLD (not Semi Bold) for
    # KPI labels, table headers, row project names, pill labels and the
    # workspace eyebrow line. Inter Bold has the same glyph advances as
    # Semi Bold at the same size (bbox width unchanged, strokes heavier).
    "ws1":           ("PRO WORKSPACE", 13, GREEN_MINT, "bold"),
    "ws2":           ("12 team members", 16, "#FFFFFF", "reg"),
    "ws3":           ("Manage access  \u2192", 14, WS_MUTED, "reg"),
    "title":         ("Workspace Overview", 32, DARK, "bold"),
    "subtitle":      ("Saturday, 07 November 2026", 18, MUTED, "reg"),
    "button":        ("Export report", 18, "#FFFFFF", "sb"),
    "kpi1_label":    ("REVENUE", 14, MUTED, "bold"),
    "kpi1_value":    ("\u00a5128,400", 32, DARK, "bold"),
    "kpi1_change":   ("+12.4%", 16, GREEN_TXT, "bold"),
    "kpi2_label":    ("ORDERS", 14, MUTED, "bold"),
    "kpi2_value":    ("426", 32, DARK, "bold"),
    "kpi2_change":   ("+8.1%", 16, GREEN_TXT, "bold"),
    "kpi3_label":    ("REFUND RATE", 14, MUTED, "bold"),
    "kpi3_value":    ("3.2%", 32, DARK, "bold"),
    "kpi3_change":   ("\u22120.8 pp", 16, GREEN_TXT, "bold"),
    "chart_title":   ("Net revenue", 22, DARK, "bold"),
    "chart_period":  ("Apr \u2013 Sep", 17, MUTED, "reg"),
    "unit":          ("\u00a5 thousand", 13, MUTED, "reg"),
    "tick_120":      ("120", 13, MUTED, "reg"),
    "tick_90":       ("90", 13, MUTED, "reg"),
    "tick_60":       ("60", 13, MUTED, "reg"),
    "tick_30":       ("30", 13, MUTED, "reg"),
    "tick_0":        ("0", 13, MUTED, "reg"),
    "month_Apr":     ("Apr", 13, MUTED, "reg"),
    "month_May":     ("May", 13, MUTED, "reg"),
    "month_Jun":     ("Jun", 13, MUTED, "reg"),
    "month_Jul":     ("Jul", 13, MUTED, "reg"),
    "month_Aug":     ("Aug", 13, MUTED, "reg"),
    "month_Sep":     ("Sep", 13, MUTED, "reg"),
    "activity_title": ("Team activity", 22, DARK, "bold"),
    "act_t1":        ("Design review", 18, DARK, "sb"),
    "act_time1":     ("08:40", 14, MUTED, "reg"),
    "act_t2":        ("Dataset updated", 18, DARK, "sb"),
    "act_time2":     ("09:15", 14, MUTED, "reg"),
    "act_t3":        ("Render complete", 18, DARK, "sb"),
    "act_time3":     ("10:05", 14, MUTED, "reg"),
    "table_title":   ("Recent projects", 22, DARK, "bold"),
    "th_project":    ("PROJECT", 12, MUTED, "bold"),
    "th_owner":      ("OWNER", 12, MUTED, "bold"),
    "th_status":     ("STATUS", 12, MUTED, "bold"),
    "th_due":        ("DUE", 12, MUTED, "bold"),
    "r1_project":    ("Atlas / Visual system", 16, DARK, "bold"),
    "r1_owner":      ("Lin Chuan", 16, MUTED, "reg"),
    "r1_due":        ("Nov 09", 16, MUTED, "reg"),
    "r2_project":    ("Pulse / Dashboard", 16, DARK, "bold"),
    "r2_owner":      ("Zhou He", 16, MUTED, "reg"),
    "r2_due":        ("Nov 11", 16, MUTED, "reg"),
    "r3_project":    ("Orbit / Launch", 16, DARK, "bold"),
    "r3_owner":      ("Su Yan", 16, MUTED, "reg"),
    "r3_due":        ("Nov 12", 16, MUTED, "reg"),
    "pill_progress": ("In progress", 13, PILL_PROGRESS_FG, "bold"),
    "pill_review":   ("Review", 13, PILL_REVIEW_FG, "bold"),
    "pill_done":     ("Done", 13, PILL_DONE_FG, "bold"),
    "footer":        ("All data is fictional \u00b7 Snapshot benchmark",
                      13, FOOTER_TXT, "reg"),
}


def family(weight):
    if weight == "bold":
        return "Inter", "BOLD"
    if weight == "sb":
        return "Inter Semi Bold", None
    return "Inter", None


def build_texts(ref_targets, calib):
    lines = []
    for key, (text, fs, color, weight) in TEXT_SPECS.items():
        ref = ref_targets[key]["box"]
        anchor = ref_targets[key]["anchor"]
        dx, dy = calib.get(key, [0, 0])
        left = ref[0] - 1 + dx
        top = ref[1] - round(0.24 * fs) + dy
        width = (ref[2] - ref[0]) + 170
        height = 2 * fs + 8
        fam, style = family(weight)
        a = (f'<Positioned left="{left}" top="{top}" width="{width}" '
             f'height="{height}"><Text fontSize="{fs}" color="{color}" '
             f'fontFamily="{fam}"')
        if style:
            a += f' fontStyle="{style}"'
        a += f' text="{text}"/></Positioned>'
        lines.append(a)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsl", required=True)
    ap.add_argument("--calib", default=None)
    args = ap.parse_args()

    ref = json.loads((TMP / "texts-reference.json").read_text("utf-8"))
    calib = {}
    if args.calib:
        calib = json.loads(pathlib.Path(args.calib).read_text("utf-8"))

    parts = ['<Snapshot type="png" background="%s">' % BG,
             '  <SizedBox width="%d" height="%d">' % (W, H),
             '    <Stack alignment="TOP_LEFT" clipBehavior="NONE">']
    parts += ["    " + ln for ln in shapes()]
    parts += ["    " + ln for ln in build_texts(ref, calib)]
    parts += ["    </Stack>", "  </SizedBox>", "</Snapshot>", ""]

    out = pathlib.Path(args.dsl)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {out.as_posix()} ({len(shapes())} shapes, "
          f"{len(TEXT_SPECS)} texts, calib keys={len(calib)})")


if __name__ == "__main__":
    main()
