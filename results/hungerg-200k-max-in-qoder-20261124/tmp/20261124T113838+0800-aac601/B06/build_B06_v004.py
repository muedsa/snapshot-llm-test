from __future__ import annotations
import argparse
import json
import math
import sys
from html import escape
from pathlib import Path
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk
TASK = "B06"
FONT = "Noto Sans CJK SC"
INK = "#142B33"
MUTED = "#5D7076"
PAPER = "#F4F0E7"
WHITE = "#FFFFFF"
GREEN = "#146B5D"
LIME = "#D8EE91"
ORANGE = "#E87545"
RED = "#B8473E"
BLUE = "#2879A8"
GOLD = "#D2A63D"
plan = json.loads((BASE / "plan-v001.json").read_text(encoding="utf-8"))
CASES = {c["id"]: c for c in plan["cases"]}

def text(value, size=20, color=INK, bold=False, align="LEFT", max_lines=None):
    attrs = [f'fontFamily="{FONT}"', f'fontSize="{size:g}"', f'color="{color}"', f'textAlign="{align}"',
             f'fontStyle="{"BOLD" if bold else "NORMAL"}"', 'softWrap="true"']
    if max_lines:
        attrs += [f'maxLines="{max_lines}"', 'overflow="ELLIPSIS"']
    return "<Text " + " ".join(attrs) + ">" + escape(str(value)) + "</Text>"

def lab(value, x, y, w, h, size=20, color=INK, bold=False, align="LEFT", max_lines=None):
    alignment = {"LEFT": "CENTER_LEFT", "CENTER": "CENTER", "RIGHT": "CENTER_RIGHT"}[align]
    return sk.positioned(x, y, w, h, f'<Container width="{w:g}" height="{h:g}" alignment="{alignment}">'
                          + text(value, size, color, bold, align, max_lines) + "</Container>")

def pill(value, x, y, w, bg=LIME, fg=INK, size=16, h=36):
    child = f'<Container width="{w:g}" height="{h:g}" alignment="CENTER">' + text(value, size, fg, True, "CENTER", 1) + "</Container>"
    return sk.box(x, y, w, h, bg, h/2, child=child)

def card(x, y, w, h, bg=WHITE, border=None, radius=22):
    return sk.box(x, y, w, h, bg, radius, border)

def arrow(x1, y1, x2, y2, color=GREEN, thickness=6):
    return [sk.line(x1, y1, x2, y2, color, thickness),
            sk.line(x2, y2, x2-14, y2-10, color, thickness), sk.line(x2, y2, x2-14, y2+10, color, thickness)]

def header(w, number, kicker, title, subtitle, bg=PAPER, accent=GREEN):
    return [sk.box(0, 0, w, 18, accent), lab("FIELD NOTES / EVERYDAY INFORMATION", 70, 54, 720, 30, 17, MUTED, True),
            pill(f"{number:02d} / 10", w-210, 50, 140, accent, WHITE, 16, 38),
            lab(kicker.upper(), 70, 118, w-140, 30, 18, accent, True),
            lab(title, 70, 158, w-140, 88, 56, INK, True, max_lines=2),
            lab(subtitle, 70, 258, w-140, 68, 23, MUTED, max_lines=2)]

def footer(w, h, note="Fictional demonstration · no field research or user testing"):
    return [sk.line(70, h-72, w-70, h-72, "#C9D0CA", 2), lab(note, 70, h-52, w-140, 28, 15, MUTED),
            lab("B06 · INFORMATION, REBUILT", w-390, h-52, 320, 28, 14, MUTED, True, "RIGHT")]

def case01():
    w, h = 1400, 1800
    n = header(w, 1, "Money / change attribution", "Why did the bill change?",
               "Start with the $38 difference. Only three lines moved; the chart separates a cause from a question.")
    n += [card(70, 360, 1260, 122, INK), lab("$104", 105, 380, 250, 58, 46, WHITE, True),
          lab("LAST MONTH", 105, 439, 250, 25, 14, "#B8CBC7", True), *arrow(385, 421, 585, 421, LIME, 5),
          lab("+$38", 625, 380, 250, 58, 46, LIME, True), lab("TOTAL CHANGE", 625, 439, 250, 25, 14, "#B8CBC7", True),
          lab("$142", 960, 380, 320, 58, 46, WHITE, True, "RIGHT"), lab("THIS MONTH", 960, 439, 320, 25, 14, "#B8CBC7", True, "RIGHT")]
    base, scale = 1360, 5.0
    for value in (0, 40, 80, 120):
        y = base-value*scale
        n += [sk.line(120, y, 1330, y, "#DADFD7", 2), lab(f"${value}", 72, y-15, 70, 30, 15, MUTED, align="RIGHT")]
    bars = [("Last month", 0, 104, "#7C9993"), ("Energy", 104, 34, ORANGE), ("Taxes", 138, 3, GOLD), ("Credit", 141, 1, GREEN), ("This month", 0, 142, INK)]
    xs = [180, 420, 660, 900, 1140]
    levels = [104, 138, 141, 142]
    for i, ((name, start, delta, color), x) in enumerate(zip(bars, xs)):
        top = base-(start+delta)*scale
        height = delta*scale
        n += [sk.box(x, top, 150, height, color, 10)]
        value = f"${delta}" if i in (0, 4) else f'+${delta}'
        if i < 2:
            n += [lab(value, x-25, top-54, 200, 44, 30, color if i == 1 else INK, True, "CENTER")]
        else:
            n += [lab(f"{name} · {value}", x-55, base+20, 260, 40, 18, color, True, "CENTER")]
        if i < 2:
            n += [lab(name, x-40, base+20, 230, 40, 20, INK, True, "CENTER")]
        if i < 4:
            level = levels[i]
            n += [sk.line(x+150, base-level*scale, xs[i+1], base-level*scale, "#91A39E", 3)]
    n += [lab("HOW TO READ", 120, 1445, 210, 28, 15, MUTED, True),
          lab("Floating bars show change, not the size of the whole bill.", 120, 1480, 1160, 40, 22, INK)]
    actions = [("+$34 ENERGY", "Check meter dates and unusual usage.", ORANGE),
               ("+$3 TAXES", "Ask which taxable charge changed.", GOLD),
               ("+$1 CREDIT", "Confirm whether the smaller credit expired.", GREEN)]
    for i, (title, body, color) in enumerate(actions):
        x = 70+i*430
        n += [card(x, 1545, 400, 165, WHITE), sk.box(x, 1545, 10, 165, color, 5),
              lab(title, x+30, 1567, 340, 32, 19, color, True), lab(body, x+30, 1609, 340, 76, 20, INK, max_lines=3)]
    return sk.snapshot(w, h, n+footer(w, h), PAPER)

def case02():
    w, h = 1600, 1000
    n = header(w, 2, "Transport / partial service", "Can I still get there?",
               "Yes — with a change at Market. The map keeps your journey visible while the disrupted rail segment drops out.")
    n += [card(70, 350, 1460, 116, INK), pill("YES", 98, 377, 120, LIME, INK, 24, 62),
          lab("Harbor → replacement bus → Market → train → Museum", 250, 374, 980, 40, 29, WHITE, True),
          lab("+12 min · fictional estimate, not live service information", 250, 420, 980, 26, 17, "#B8CBC7")]
    stations = [("Harbor", 150), ("Pier", 350), ("Market", 650), ("Civic", 950), ("Museum", 1330)]
    n += [sk.line(150, 565, 650, 565, "#D1D7D2", 16), sk.line(650, 565, 1330, 565, BLUE, 16)]
    for i in range(9):
        x = 150+i*62.5
        n += [sk.line(x, 550, x+30, 580, RED, 7)]
    n += [lab("CLOSED RAIL · HARBOR–MARKET", 180, 510, 420, 30, 18, RED, True)]
    for name, x in stations:
        n += [sk.circle(x, 565, 15, WHITE, BLUE if x >= 650 else RED), lab(name, x-90, 592, 180, 36, 21, INK, True, "CENTER")]
    n += [sk.line(150, 690, 650, 690, ORANGE, 18)] + arrow(615, 690, 675, 690, ORANGE, 5)
    n += [pill("REPLACEMENT BUS", 230, 650, 340, ORANGE, WHITE, 19, 54),
          lab("Board at Harbor · alight at Market", 230, 720, 500, 34, 18, MUTED)]
    n += [*arrow(650, 615, 650, 670, ORANGE, 5), *arrow(650, 700, 650, 585, BLUE, 5)]
    steps = [("01", "Stay on the bus", "The train skips Pier and the closed segment."),
             ("02", "Change at Market", "Use the same-platform signs in this demo."),
             ("03", "Continue to Museum", "Civic and Museum remain served by train.")]
    for i, (num, title, body) in enumerate(steps):
        x = 70+i*500
        n += [card(x, 800, 460, 120, WHITE), pill(num, x+20, 820, 62, LIME, INK, 17, 42),
              lab(title, x+100, 817, 330, 32, 21, INK, True), lab(body, x+100, 854, 330, 52, 16, MUTED, max_lines=2)]
    return sk.snapshot(w, h, n+footer(w, h), "#EDF2F4")

def case03():
    w, h = 1500, 1800
    n = header(w, 3, "Housing / total cost", "Which home is actually affordable?",
               "Compare recurring monthly cost first. Keep one-time entry fees separate so a deposit never masquerades as rent.")
    n += [pill("MONTHLY · ESTIMATED UTILITIES INCLUDED", 70, 350, 560, GREEN, WHITE, 16, 42),
          lab("Shared $0 baseline · stack height = total monthly cost", 720, 355, 710, 30, 18, MUTED, align="RIGHT")]
    base, scale = 1240, 0.36
    listings = [("A", "Maple Court", [("Rent",1450,"#315E57"),("Utilities*",180,"#73A294"),("Parking",35,"#B9D3C7")],1665,500),
                ("B", "Juniper Walk", [("Rent",1320,"#315E57"),("Utilities*",230,"#73A294"),("Laundry",60,"#B9D3C7")],1610,350),
                ("C", "Cedar House", [("Rent",1550,"#315E57"),("Utilities*",140,"#73A294"),("Parking",120,"#B9D3C7")],1810,600)]
    for i, (key, name, parts, total, entry) in enumerate(listings):
        x = 170+i*440
        top = base-total*scale
        n += [lab(f"HOME {key}", x, 405, 260, 28, 16, MUTED, True, "CENTER"), lab(name, x-20, 438, 300, 40, 24, INK, True, "CENTER"),
              lab(f"${total:,}", x-20, 485, 300, 52, 42, GREEN if key == "B" else INK, True, "CENTER")]
        y = base
        for part_index, (label, value, color) in enumerate(parts):
            height = value*scale
            y -= height
            n += [sk.box(x, y, 260, height, color)]
            if height >= 60:
                n += [lab(f"{label}  ${value:,}", x+10, y+height/2-16, 240, 32, 15, WHITE if color != "#B9D3C7" else INK, True, "CENTER", 1)]
            elif part_index == len(parts)-1:
                n += [sk.line(x+130, y, x+130, y-12, color, 2),
                      lab(f"{label}  ${value:,}", x-20, y-45, 300, 32, 15, GREEN if label == "Utilities*" else INK, True, "CENTER", 1)]
            else:
                n += [sk.line(x+260, y+height/2, x+274, y+height/2, color, 2),
                      lab(f"{label}  ${value:,}", x+280, y+height/2-16, 150, 32, 15, GREEN, True, "LEFT", 1)]
        n += [sk.line(x-40, base, x+300, base, "#98AAA4", 3)]
        n += [card(x-40, 1330, 340, 150, "#E5EBE4"), lab("ONE-TIME ENTRY", x-20, 1350, 300, 26, 14, MUTED, True, "CENTER"),
              lab(f"${entry:,}", x-20, 1382, 300, 46, 32, INK, True, "CENTER"), lab("not in monthly total", x-20, 1430, 300, 26, 14, MUTED, align="CENTER")]
    n += [card(70, 1530, 1360, 160, INK), lab("B has the lowest monthly total: $1,610", 105, 1555, 780, 40, 28, LIME, True),
          lab("That is a cost result, not an absolute recommendation. Compare location, space, lease terms and verified utility estimates before deciding.", 105, 1605, 1280, 62, 20, WHITE, max_lines=2),
          lab("* Utilities are fictional estimates. All prices are invented USD demonstration values.", 70, 1710, 1360, 28, 15, MUTED)]
    return sk.snapshot(w, h, n+footer(w, h), PAPER)

def case04():
    w, h = 1200, 1500
    n = header(w, 4, "Shopping / normalized price", "The better price per kilogram",
               "A wins on unit price, but costs more today and carries a longer use window.")
    packs = [("A", "850 g", "$5.10", "$6.00 / kg", "10 days", 600, ORANGE), ("B", "500 g", "$3.30", "$6.60 / kg", "5 days", 660, GREEN)]
    for i, (key, mass, price, unit, expiry, marker, color) in enumerate(packs):
        x = 80+i*560
        n += [card(x, 370, 480, 430, WHITE, "#D5DCD4"), pill(f"PACK {key}", x+28, 398, 130, color, WHITE, 17, 40),
              lab(mass, x+28, 465, 420, 70, 52, INK, True), lab(price, x+28, 548, 420, 58, 38, color, True),
              lab(unit, x+28, 630, 420, 48, 28, INK, True), lab(f"Use within {expiry} · demo", x+28, 700, 420, 34, 18, MUTED),
              lab("$5.10 ÷ 0.850 kg" if key == "A" else "$3.30 ÷ 0.500 kg", x+28, 746, 420, 28, 16, MUTED)]
    n += [lab("ONE COMMON RULER · PRICE PER KILOGRAM", 80, 850, 1040, 30, 17, MUTED, True),
          sk.line(140, 950, 1060, 950, INK, 6)]
    for value in range(0, 8):
        x = 140+value*(920/7)
        n += [sk.line(x, 936, x, 970, INK, 3), lab(f"${value}", x-30, 978, 60, 28, 16, MUTED, align="CENTER")]
    for marker, color, name in ((600, ORANGE, "A"), (660, GREEN, "B")):
        x = 140+(marker/100)*(920/7)
        n += [sk.circle(x, 950, 15, color), pill(name, x-28, 890, 56, color, WHITE, 17, 38)]
    n += [card(80, 1060, 1040, 260, INK), lab("A is $0.60/kg cheaper", 115, 1090, 960, 46, 32, LIME, True),
          lab("But A costs $1.80 more upfront.", 115, 1146, 960, 38, 24, WHITE, True),
          lab("Choose A if you will use 850 g within 10 days. Choose B if the smaller quantity is more likely to be finished before its 5-day demo expiry.", 115, 1196, 940, 90, 21, WHITE, max_lines=3),
          lab("Fictional product, prices and expiry windows · not nutrition advice", 80, 1360, 1040, 28, 16, MUTED)]
    return sk.snapshot(w, h, n+footer(w, h), "#F3EFE5")

def case05():
    w, h = 1400, 1800
    n = header(w, 5, "Study / dependencies", "What should I do first?",
               "The nearest deadline is not always the best starting point. Follow what unlocks the next task.")
    n += [card(70, 355, 1260, 116, GREEN), pill("START HERE", 98, 382, 190, LIME, INK, 18, 58),
          lab("Outline · 3 estimated hours · due Dec 02", 320, 378, 900, 40, 28, WHITE, True),
          lab("It unlocks the draft. Largest grade weight does not mean first action.", 320, 425, 900, 26, 17, "#D2E5DE")]
    stages = [("01", "Outline", "Dec 02", "20%", "3 h", "unlocks draft", GREEN),
              ("02", "Draft", "Dec 05", "30%", "6 h", "unlocks peer review", BLUE),
              ("03", "Peer review", "Dec 08", "10%", "2 h", "unlocks final", GOLD),
              ("04", "Final submission", "Dec 12", "40%", "5 h", "course complete", ORANGE)]
    for i, (num, title, due, weight, effort, unlock, color) in enumerate(stages):
        y = 535+i*270
        if i < 3:
            n += arrow(700, y+190, 700, y+258, color, 7)
        n += [card(300, y, 800, 190, WHITE), sk.box(300, y, 14, 190, color, 7), pill(num, 335, y+26, 66, color, WHITE, 16, 40),
              lab(title, 425, y+22, 410, 42, 30, INK, True), lab(unlock, 425, y+74, 410, 32, 18, MUTED),
              lab(due, 850, y+28, 210, 36, 22, color, True, "RIGHT"), lab(f"{weight} · {effort}", 850, y+76, 210, 34, 19, INK, True, "RIGHT"),
              lab("deadline", 335, y+132, 160, 26, 14, MUTED, True), lab("grade weight / effort", 755, y+132, 305, 26, 14, MUTED, True, "RIGHT")]
        n += [sk.line(1100, y+95, 1190, y+95, color, 4), sk.circle(1210, y+95, 20, color),
              lab(f"{effort}", 1180, y+130, 60, 26, 14, MUTED, align="CENTER")]
    n += [card(70, 1650, 1260, 80, "#E2E9DC"), lab("TOTAL · 100% grade weight · 16 estimated hours", 100, 1670, 1200, 38, 23, INK, True, "CENTER")]
    return sk.snapshot(w, h, n+footer(w, h), "#F2F0E8")

def case06():
    w, h = 1300, 1700
    n = header(w, 6, "Insurance / scenario path", "Is this kind of damage covered?",
               "A policy is arranged by legal section. Your question starts with an event. This guide connects the two without inventing a verdict.")
    n += [pill("FICTIONAL POLICY · NOT LEGAL ADVICE", 70, 350, 520, RED, WHITE, 16, 42)]
    n += [card(250, 430, 800, 180, INK), lab("EVENT", 285, 455, 730, 26, 15, "#BCD0CA", True),
          lab("A burst pipe damages the kitchen floor", 285, 495, 730, 72, 30, WHITE, True, "CENTER", 2)]
    n += [sk.line(650, 610, 650, 660, GREEN, 6), sk.line(350, 660, 950, 660, GREEN, 6),
          sk.line(350, 660, 350, 710, GREEN, 6), sk.line(950, 660, 950, 710, GREEN, 6)]
    n += [card(80, 710, 540, 260, WHITE), pill("SECTION TO READ", 110, 740, 220, LIME, INK, 15, 38),
          lab("Section 4", 110, 800, 480, 42, 30, INK, True), lab("Sudden accidental water escape", 110, 852, 480, 78, 24, GREEN, True, max_lines=2),
          card(680, 710, 540, 260, "#FFF0E8"), pill("EXCLUSION TO CHECK", 710, 740, 250, ORANGE, WHITE, 15, 38),
          lab("Gradual leakage", 710, 800, 480, 42, 30, INK, True), lab("When did signs first appear? Is any damage unrelated to the sudden escape?", 710, 852, 480, 88, 21, INK, max_lines=3)]
    n += [sk.line(350, 970, 350, 1030, GREEN, 6), sk.line(950, 970, 950, 1030, GREEN, 6), sk.line(350, 1030, 950, 1030, GREEN, 6),
          *arrow(650, 1030, 650, 1080, GREEN, 6)]
    n += [card(110, 1080, 1080, 300, "#E3ECE5"), lab("DOCUMENTS TO GATHER", 150, 1110, 1000, 32, 18, GREEN, True)]
    docs = [("01", "Photos", "before cleanup, if safe"), ("02", "Plumber report", "cause and repair scope"), ("03", "Receipts", "keep every related cost")]
    for i, (num, title, note) in enumerate(docs):
        x = 150+i*340
        n += [sk.circle(x+24, 1190, 24, GREEN), lab(num, x, 1172, 48, 36, 16, WHITE, True, "CENTER"),
              lab(title, x+62, 1166, 250, 34, 23, INK, True), lab(note, x+62, 1206, 250, 56, 17, MUTED, max_lines=2)]
    n += [card(110, 1420, 1080, 170, INK), pill("NEXT", 145, 1450, 110, LIME, INK, 17, 44),
          lab("Needs adjuster review", 285, 1444, 840, 42, 32, WHITE, True),
          lab("Ask: Which facts determine whether the gradual-leakage exclusion applies?", 285, 1498, 840, 60, 21, WHITE, max_lines=2),
          lab("No coverage decision is claimed. This is a reading aid for a fictional scenario, not a determination.", 110, 1610, 1080, 34, 16, MUTED)]
    return sk.snapshot(w, h, n+footer(w, h), PAPER)

def arc(cx, cy, radius, start, end, color, thickness=18, steps=50):
    nodes = []
    for i in range(steps+1):
        angle = math.radians(start+(end-start)*i/steps)
        nodes.append((cx+radius*math.cos(angle), cy+radius*math.sin(angle)))
    return [sk.line(*nodes[i], *nodes[i+1], color, thickness) for i in range(steps)]

def case07():
    w, h = 1400, 1600
    n = header(w, 7, "Repair / decision assumptions", "Repair it or replace it?",
               "Translate both options into cost per assumed year. Then check what the arithmetic leaves out.")
    n += [pill("WARRANTY GATE · EXPIRED", 70, 350, 390, ORANGE, WHITE, 17, 46),
          lab("Neither option is automatically covered by warranty in this demo.", 500, 357, 830, 32, 19, MUTED)]
    cx, cy = 700, 820
    n += arc(cx, cy, 410, 180, 360, "#DCE3DC", 34) + arc(cx, cy, 410, 180, 262.5, GREEN, 34) + arc(cx, cy, 300, 180, 326.25, BLUE, 30)
    n += [sk.circle(cx, cy, 205, INK), lab("REPAIR", cx-180, cy-115, 360, 32, 18, "#B9D4C9", True, "CENTER"),
          lab("$55", cx-180, cy-72, 360, 76, 62, LIME, True, "CENTER"), lab("per assumed year", cx-180, cy+4, 360, 32, 19, WHITE, align="CENTER"),
          lab("$220 ÷ 4 years", cx-180, cy+56, 360, 30, 17, "#B9D4C9", align="CENTER"),
          lab("REPLACE · $97.50 / assumed year", 260, 455, 880, 36, 24, BLUE, True, "CENTER"),
          lab("$780 ÷ 8 years", 430, 505, 540, 32, 19, MUTED, align="CENTER"),
          lab("Arc scale: $0–$120 per year", 470, 1120, 460, 30, 16, MUTED, align="CENTER")]
    n += [card(70, 1190, 610, 210, WHITE), lab("REPAIR NOW", 100, 1215, 550, 30, 16, GREEN, True),
          lab("$220 upfront", 100, 1255, 550, 44, 32, INK, True), lab("Assumes 4 more years. Cheaper per year under these assumptions.", 100, 1310, 550, 66, 20, MUTED, max_lines=2),
          card(720, 1190, 610, 210, WHITE), lab("REPLACE", 750, 1215, 550, 30, 16, BLUE, True),
          lab("$780 upfront", 750, 1255, 550, 44, 32, INK, True), lab("Assumes 8 years. A new unit is not guaranteed to last that long.", 750, 1310, 550, 66, 20, MUTED, max_lines=2),
          card(70, 1430, 1260, 90, "#E6EBE3"), lab("NOT IN THE MATH · energy use · disposal · installation · future failures", 100, 1455, 1200, 38, 21, INK, True, "CENTER")]
    return sk.snapshot(w, h, n+footer(w, h), "#F1EEE6")

def case08():
    w, h = 1400, 1800
    n = header(w, 8, "Recycling / condition and route", "Where does this actually go?",
               "Material is only the first question. Condition and preparation decide the route — especially for bags and batteries.")
    n += [pill("HARBOR CITY RULES ARE FICTIONAL", 70, 350, 540, RED, WHITE, 17, 44),
          lab("Do not use this poster as real local guidance.", 700, 357, 630, 30, 18, MUTED, align="RIGHT")]
    items = [("Clean paper", "clean and dry", "PAPER RECYCLING", GREEN), ("Greasy pizza box", "remove clean lid", "ORGANICS IF ACCEPTED", GOLD),
             ("Rigid plastic bottle", "empty · cap on", "PLASTICS RECYCLING", BLUE), ("Soft plastic bag", "not curbside", "STORE DROP-OFF", ORANGE),
             ("Battery", "tape terminals", "BATTERY DROP-OFF", RED), ("Glass jar", "rinse · no ceramics", "GLASS RECYCLING", GREEN)]
    for i, (item, prep, route, color) in enumerate(items):
        y = 440+i*205
        n += [card(70, y, 1260, 160, WHITE), sk.circle(125, y+80, 36, color), lab(f"{i+1:02d}", 89, y+58, 72, 44, 22, WHITE, True, "CENTER"),
              lab(item, 185, y+28, 360, 44, 26, INK, True), lab(prep, 185, y+84, 360, 36, 19, MUTED),
              sk.line(565, y+80, 875, y+80, color, 8)] + arrow(835, y+80, 895, y+80, color, 5)
        n += [card(920, y+28, 370, 104, color), lab(route, 940, y+45, 330, 62, 21, WHITE, True, "CENTER", 2)]
    n += [lab("SORTING LOGIC · item → condition/preparation → route", 70, 1648, 1260, 32, 19, MUTED, True, "CENTER")]
    return sk.snapshot(w, h, n+footer(w, h), "#F3F0E7")

def case09():
    w, h = 1600, 1200
    n = header(w, 9, "Civic / personal impact", "What decision affects my block?",
               "Four agenda items, reordered around place and people. Find the decision, the effect and the last day to comment.")
    n += [card(70, 350, 760, 690, "#E6ECE3"), lab("DISTRICT 4 · SCHEMATIC, NOT BOUNDARIES", 100, 375, 700, 30, 16, MUTED, True)]
    for x1,y1,x2,y2 in ((160,500,730,500),(160,690,730,690),(300,440,300,930),(570,440,570,930)):
        n += [sk.box(x1,y1,x2-x1,14,"#FFFFFF"), sk.box(x1,y1,14,y2-y1,"#FFFFFF")]
    n += [lab("Oak Street", 170, 465, 250, 30, 18, MUTED), lab("Cedar Court", 585, 655, 210, 30, 18, MUTED),
          lab("3rd Avenue", 300, 875, 250, 30, 18, MUTED), lab("Park", 585, 525, 170, 30, 18, GREEN, True)]
    nodes = [(335,570,GREEN,"School crossing"),(655,580,GOLD,"Park hours"),(335,805,BLUE,"Bus lane"),(610,780,ORANGE,"Tree removal")]
    for x,y,color,name in nodes:
        n += [sk.circle(x,y,22,color), lab(name,x-110,y+32,220,30,17,INK,True,"CENTER")]
    entries = [("School crossing timing", "Families on Oak Street", "Approve trial timing", "DEC 01", GREEN, (335,570)),
               ("Park hours", "Evening park users", "Extend closing to 22:00", "DEC 03", GOLD, (655,580)),
               ("Bus lane pilot", "Drivers and riders on 3rd Ave", "Approve six-month pilot", "DEC 04", BLUE, (335,805)),
               ("Tree removal request", "Residents near Cedar Court", "Approve or deny removal", "DEC 05", ORANGE, (610,780))]
    for i,(title,people,decision,deadline,color,(nx,ny)) in enumerate(entries):
        y = 350+i*180
        n += [sk.line(830, y+80, nx, ny, color, 3), card(880,y,650,155,WHITE), sk.box(880,y,12,155,color,6),
              lab(title,915,y+18,440,34,24,INK,True), lab(people,915,y+60,440,28,17,MUTED),
              lab(decision,915,y+96,440,32,19,color,True), pill(f"COMMENT BY {deadline}",1240,y+28,255,color,WHITE,14,42)]
    n += [card(70, 1050, 1460, 62, INK), lab("Participation is a chance to inform the decision — not a promise that the outcome will change.", 100, 1064, 1400, 34, 20, WHITE, True, "CENTER")]
    return sk.snapshot(w, h, n+footer(w, h), "#EEF1EC")

def case10():
    w, h = 1600, 1100
    n = header(w, 10, "Home network / test one change", "Fix the room, not the whole house",
               "Start with placement and one repeatable test. Add hardware only if the weak spot remains.")
    n += [card(70, 350, 930, 600, "#E4EAE2"), lab("FICTIONAL FLOOR PLAN · DEMO dBm READINGS", 100, 375, 850, 30, 16, MUTED, True)]
    rooms = [(100,430,410,230,"Living room","−42 dBm"),(510,430,460,230,"Kitchen","−72 dBm"),(100,660,410,250,"Bedroom","−58 dBm"),(510,660,460,250,"Hall","not sampled")]
    for x,y,rw,rh,name,value in rooms:
        n += [sk.box(x,y,rw,rh,WHITE,0,"#9FAFA6"), lab(name,x+24,y+22,rw-48,34,23,INK,True), lab(value,x+24,y+68,rw-48,34,21,RED if "72" in value else GREEN,True)]
    for radius,color in ((108,"#CFE0D2"),(72,"#B5D2BD")):
        n += [sk.positioned(305-radius,545-radius,radius*2,radius*2,f'<Container width="{radius*2}" height="{radius*2}" borderRadius="{radius}" border="3 SOLID {color}" />')]
    n += [sk.circle(305,545,18,GREEN), lab("ROUTER",250,580,110,28,15,GREEN,True,"CENTER"),
          sk.circle(740,545,25,ORANGE), lab("TEST HERE",665,590,150,30,17,ORANGE,True,"CENTER")]
    n += [lab("Contours are illustrative, not a measured signal survey.", 100, 900, 850, 28, 16, MUTED)]
    actions = [("01", "Move the router", "Higher and away from the microwave."), ("02", "Repeat the same test", "Stand in the same kitchen spot."), ("03", "Only then consider mesh", "If the weak spot still remains.")]
    for i,(num,title,body) in enumerate(actions):
        y = 350+i*200
        n += [card(1050,y,480,170,WHITE), pill(num,1075,y+24,62,GREEN,WHITE,17,42), lab(title,1155,y+22,340,36,24,INK,True),
              lab(body,1155,y+74,340,64,19,MUTED,max_lines=2)]
    n += [card(1050,960,480,80,INK), lab("No guaranteed fix. One change at a time.",1075,980,430,38,19,WHITE,True,"CENTER")]
    return sk.snapshot(w,h,n+footer(w,h),"#EFF1ED")

BUILDERS = {f"B06-case-{i:02d}": globals()[f"case{i:02d}"] for i in range(1,11)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--version", default="v001")
    args = parser.parse_args()
    selected = list(BUILDERS) if args.all else [args.case]
    assert all(cid in BUILDERS for cid in selected)
    results = []
    for cid in selected:
        case = CASES[cid]
        image, record = ck.render_case(TASK, case, BUILDERS[cid](), args.version)
        ck.record_view(TASK, case, image, args.version, "待视觉检查", "首次渲染；尚未作出通过判断。", "基线", False, "baseline")
        results.append({"case": cid, "version": args.version, "image": sk.rel(image), "request": record["request_id"]})
    print(json.dumps(results, ensure_ascii=False))

if __name__ == "__main__":
    main()
