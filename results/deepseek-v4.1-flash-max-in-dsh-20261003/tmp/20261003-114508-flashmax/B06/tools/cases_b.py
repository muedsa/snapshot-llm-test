"""B06 case builders 06-10: everyday information, reinvented (second half)."""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bkit import Doc, CJK, MONO, INTER, tw  # noqa: E402

INK = "#101820FF"
MUTED = "#5B6B7FFF"
LINE = "#DCE3EAFF"


def _fill(d, pts, color, step=5):
    ys = [p[1] for p in pts]
    y = min(ys)
    while y <= max(ys):
        xs = []
        n = len(pts)
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            if (y1 <= y < y2) or (y2 <= y < y1):
                t = (y - y1) / (y2 - y1)
                xs.append(x1 + t * (x2 - x1))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            if xs[i + 1] - xs[i] > 0.5:
                d.box(xs[i], y, xs[i + 1] - xs[i], step, color)
        y += step


# =====================================================================  case-06
def case06(D, ver="v1") -> str:
    """One bowl, most of your day's sugar - 1280x1520 poster."""
    W, H = 1280, 1520
    d = Doc(W, H, "#FFFDF7FF")
    nut = D["nutrition"]
    AMBER = "#C2740AFF"
    RED = "#B3261EFF"
    TEAL = "#0E8A72FF"
    d.box(0, 0, W, 168, "#2B2118FF")
    d.box(0, 164, W, 4, AMBER)
    d.text(48, 26, "One bowl. Most of your day's sugar.", 38, "#FFFFFFFF", "BOLD", CJK)
    d.text(48, 88, f'{nut["product"]}', 19, "#D9C9B4FF", "NORMAL", CJK)
    d.rtext(W - 48, 34, 30, "SERVING SIZE, REWRITTEN", 16, "#E8C87AFF", weight="BOLD", family=INTER)
    d.rtext(W - 48, 74, 28, "the label's serving on the left, what you actually pour on the right",
            15, "#D9C9B4FF")

    # ---- two bowls: the fill level is the portion, so the picture carries the argument
    def bowl(cx, cy, r, grams, fill_col, label, sub, pct, teas):
        s = max(0.02, 1 - (grams / 100.0) * 0.95)
        a0 = math.asin(min(0.999, s))
        pts = [(cx + r * math.cos(a0 + (math.pi - 2 * a0) * i / 26),
                cy + r * math.sin(a0 + (math.pi - 2 * a0) * i / 26)) for i in range(27)]
        _fill(d, pts, fill_col, step=4)
        d.arc(cx, cy, r, 0, 180, "#B9C4D0FF", 5)
        d.box(cx - r - 10, cy - 4, 2 * r + 20, 8, "#B9C4D0FF", radius=4)
        lvl = cy + r * s
        for i in range(7):
            gx = cx - r * 0.62 + i * (r * 0.21)
            d.box(gx, lvl - 9, 14, 9, fill_col, radius=3, border="1 SOLID #FFFFFFAA")
        d.ctext(cx, cy + r + 26, 34, label, 24, INK, "BOLD", CJK, pad=10)
        d.ctext(cx, cy + r + 62, 26, sub, 16, MUTED, "NORMAL", CJK, pad=10)
        d.ctext(cx, cy + r + 94, 30, pct, 20, fill_col, "BOLD", CJK, pad=10)
        d.ctext(cx, cy + r + 124, 26, teas, 15, MUTED, "NORMAL", CJK, pad=10)
    d.box(60, 210, 1160, 430, "#FFFFFFFF", radius=18, border=f"1 SOLID {LINE}")
    d.text(84, 232, "SAME CEREAL, TWO DIFFERENT DAYS", 14, MUTED, "BOLD", INTER, spacing=1)
    bowl(360, 372, 104, 45, "#9AA7B4FF", f'{nut["per_listed_serving"]["sugar"]:g} g sugar',
         f'the label serving: {nut["servings_listed"]} bowls in the box',
         f'{nut["share_of_day_listed"]["sugar"]:.0f}% of a 30 g free-sugar day',
         f'{nut["sugar_teaspoons_listed"]} teaspoons of sugar')
    bowl(920, 372, 148, 80, AMBER, f'{nut["per_actual_bowl"]["sugar"]:g} g sugar',
         f'a real bowl: {nut["bowls_actual"]} bowls in the box',
         f'{nut["share_of_day_actual"]["sugar"]:.0f}% of a 30 g free-sugar day',
         f'{nut["sugar_teaspoons_actual"]} teaspoons of sugar')

    # ---- budget bars
    d.box(60, 664, 1160, 420, "#FFFFFFFF", radius=18, border=f"1 SOLID {LINE}")
    d.text(84, 684, "HOW MUCH OF A WHOLE DAY ONE BOWL USES UP", 14, MUTED, "BOLD", INTER, spacing=1)
    keys = [("sugar", "Free sugars", "30 g is the WHO free-sugar day", AMBER),
            ("sat_fat", "Saturated fat", "20 g is the reference daily amount", RED),
            ("salt", "Salt", "6 g is the adult maximum", "#8A5A2BFF"),
            ("fibre", "Fibre", "30 g is the daily target - this is the good news", TEAL)]
    for i, (k, name, note, col) in enumerate(keys):
        y = 730 + i * 88
        d.text(84, y, name, 19, INK, "BOLD", CJK)
        d.text(84, y + 24, note, 14, MUTED, "NORMAL", CJK)
        track_x, track_w = 460, 640
        d.box(track_x, y + 8, track_w, 22, "#EDF1F5FF", radius=11)
        a = nut["share_of_day_listed"][k] / 100
        b = nut["share_of_day_actual"][k] / 100
        d.box(track_x, y + 8, max(4, track_w * min(1.0, b)), 22, col, radius=11)
        d.box(track_x, y + 8, max(2, track_w * min(1.0, a)), 22, "#FFFFFFAA", radius=11)
        d.box(track_x + track_w * min(1.0, a) - 2, y + 2, 4, 34, "#33404EFF")
        d.text(track_x + track_w + 20, y + 4, f'{nut["share_of_day_actual"][k]:.0f}%', 22, col,
               "BOLD", MONO)
        d.text(track_x + track_w + 84, y + 9, f'label {nut["share_of_day_listed"][k]:.0f}%', 14,
               MUTED, "NORMAL", CJK)
    d.text(84, 1046, "The filled bar is a real 80 g bowl. The white notch is what the label's 45 g "
                     "serving would use. Nobody eats 45 g of granola.", 15, "#33404EFF", "NORMAL", CJK)

    # ---- equivalents
    d.box(60, 1104, 1160, 340, "#F4F8F6FF", radius=18, border="1 SOLID #CBE3DAFF")
    d.text(84, 1124, "WHAT THAT MEANS IN THE KITCHEN", 14, TEAL, "BOLD", INTER, spacing=1)
    for i, (k, v) in enumerate(nut["equivalents"]):
        y = 1160 + i * 68
        d.box(84, y, 6, 52, TEAL, radius=3)
        d.text(108, y - 2, k, 19, INK, "BOLD", CJK)
        d.text(108, y + 24, v, 15, "#3C5348FF", "NORMAL", CJK)
    d.text(60, 1470, "Nutrition figures are computed from a typical granola composition; the daily "
                     "budgets are the standard reference values. Not dietary advice.", 13, MUTED,
           "NORMAL", CJK)
    return d.finish()


# =====================================================================  case-07
def case07(D, ver="v1") -> str:
    """You have eight minutes - 1440x900 time budget."""
    W, H = 1440, 900
    d = Doc(W, H, "#F4F6F9FF")
    c = D["connection"]
    NAVY = "#12233AFF"
    OK = "#1C8C63FF"
    RED = "#C0392BFF"
    d.box(0, 0, W, 130, NAVY)
    d.box(0, 126, W, 4, "#3E7BB6FF")
    d.text(44, 24, f'You have {int(c["available_min"])} minutes to make this connection', 32,
           "#FFFFFFFF", "BOLD", CJK)
    d.text(44, 76, f'{c["station"]} · arrive {c["arrival"]} on platform {c["arrival_platform"]} · '
                   f'depart {c["departure"]} from platform {c["departure_platform"]} · '
                   f'{c["with_luggage_extra"]} min extra with a case', 18, "#9FB3C8FF", "NORMAL", CJK)
    d.rtext(W - 44, 34, 30, f'{c["needed_min"]:.0f} min needed · {c["slack_min"]:.0f} min spare',
            20, "#8FE3D8FF", weight="BOLD", family=CJK)

    x0, x1 = 330, 1180
    scale = (x1 - x0) / c["available_min"]

    def X(m):
        return x0 + m * scale
    d.text(44, 160, "MINUTE BY MINUTE, FROM THE MOMENT THE DOORS OPEN", 14, MUTED, "BOLD", INTER,
           spacing=1)
    t = 0.0
    for i, (label, mins, kind) in enumerate(c["legs"]):
        y = 194 + i * 50
        col = {"walk": "#3E7BB6FF", "stairs": "#7C5CC4FF", "queue": "#C2740AFF",
               "door": "#5B6B7FFF", "board": "#1C8C63FF"}[kind]
        d.text(44, y + 8, label, 16, INK, "NORMAL", CJK)
        d.box(X(t), y, max(3, mins * scale), 34, col, radius=6)
        d.text(X(t) + 8, y + 7, f"{mins:g}", 15, "#FFFFFFFF", "BOLD", MONO)
        t += mins
    yb = 194 + len(c["legs"]) * 50
    d.box(x0, yb + 6, x1 - x0, 3, "#B9C4D0FF")
    for m in range(0, int(c["available_min"]) + 1, 2):
        d.box(X(m), 176, 1, yb - 170, "#E3E9EFFF")
        d.ctext(X(m), yb + 74, 20, f"{m}", 12, MUTED, "NORMAL", MONO, pad=4)
    d.text(x0, yb + 96, "minutes after the doors open", 13, MUTED, "NORMAL", CJK)
    if c["slack_min"] > 0:
        d.box(X(c["needed_min"]), yb + 16, max(4, c["slack_min"] * scale), 30, "#FFF1C9FF", radius=6,
              border="1 SOLID #E0B84CFF")
        d.ctext(X(c["needed_min"]) + c["slack_min"] * scale / 2, yb + 20, 26,
                f'{c["slack_min"]:.0f} min spare', 15, "#8A6410FF", "BOLD", CJK, pad=8)
        d.box(X(c["needed_min"]), yb + 10, 3, 42, "#8A97A6FF")
    d.box(X(c["available_min"]), 176, 3, yb - 168, RED)
    d.text(X(c["available_min"]) - 4, 152, "", 12, RED)

    # ---- delay scenarios
    d.box(44, yb + 110, W - 88, 132, "#FFFFFFFF", radius=14, border=f"1 SOLID {LINE}")
    d.text(68, yb + 126, "WHAT HAPPENS IF THE FIRST TRAIN IS LATE", 14, MUTED, "BOLD", INTER,
           spacing=1)
    for i, (name, delay, avail) in enumerate(c["delay_scenarios"]):
        x = 68 + i * 336
        ok = avail >= c["needed_min"]
        d.box(x, yb + 156, 312, 62, "#EFF7F2FF" if ok else "#FDF0EEFF", radius=10,
              border=f'1 SOLID {OK if ok else RED}')
        d.text(x + 16, yb + 166, name, 17, INK, "BOLD", CJK)
        d.text(x + 16, yb + 190, f'{avail:.0f} min left against {c["needed_min"]:.0f} min needed',
               14, MUTED, "NORMAL", CJK)
        d.text(x + 226, yb + 172, "makes it" if ok else "miss it", 17, OK if ok else RED, "BOLD", CJK)
    d.text(44, yb + 260, f'If you miss it: {c["next_train"]}. Walking times are typical for an adult '
                         f'with one bag; the lift instead of the stairs saves about 30 seconds.',
           14, MUTED, "NORMAL", CJK)
    return d.finish()


# =====================================================================  case-08
def case08(D, ver="v1") -> str:
    """Which ticket is cheapest for the way you travel - 1500x1020 cost surface."""
    W, H = 1500, 1020
    d = Doc(W, H, "#FFFFFF")
    f = D["fares"]
    COLS = {"Pay as you go": "#6B7785FF", "Day cap": "#C2740AFF", "Weekly cap": "#7C5CC4FF",
            "28-day pass": "#3E7BB6FF", "Annual pass": "#0E8A72FF"}
    d.box(0, 0, W, 128, "#14243DFF")
    d.box(0, 124, W, 4, "#0E8A72FF")
    d.text(44, 22, "Which ticket is cheapest for the way you actually travel", 30, "#FFFFFFFF",
           "BOLD", CJK)
    d.text(44, 74, f'single £{f["single_gbp"]:.2f} · day cap £{f["day_cap_gbp"]:.2f} · weekly cap '
                   f'£{f["week_cap_gbp"]:.2f} · 28-day pass £{f["month_price_gbp"]:.0f} · annual pass '
                   f'£{f["annual_price_gbp"]:,.0f}', 18, "#9FB3C8FF", "NORMAL", CJK)
    d.rtext(W - 44, 34, 30, "cheapest option per cell", 18, "#8FE3D8FF", weight="BOLD", family=CJK)

    gx, gy, cw, ch = 250, 196, 246, 34
    d.text(44, 158, "JOURNEYS A WEEK", 13, MUTED, "BOLD", INTER, spacing=1)
    for j, wk in enumerate(f["weeks_options"]):
        d.ctext(gx + j * cw + cw / 2, 158, 24, f"{wk} weeks a year", 14, MUTED, "BOLD", INTER, pad=8)
    for i, r in enumerate(f["rows"]):
        y = gy + i * ch
        d.text(44, y + 8, f'{r["trips_per_week"]}', 17, INK, "BOLD", MONO)
        day_word = "day" if r["days"] == 1 else "days"
        d.text(86, y + 11, f'{r["days"]} {day_word}', 12.5, MUTED, "NORMAL", CJK)
        for j, cell in enumerate(r["cells"]):
            x = gx + j * cw
            col = COLS[cell["best"]]
            d.box(x + 2, y + 2, cw - 8, ch - 5, col[:7] + "1F", radius=7,
                  border=f"1 SOLID {col[:7]}40")
            d.text(x + 12, y + 3, f'£{cell["best_cost"]:,.0f}', 16, INK, "BOLD", MONO)
            d.text(x + 12, y + 20, cell["best"], 11.5, col, "BOLD", INTER)
    box_y = gy + len(f["rows"]) * ch + 6
    d.box(250, box_y, 5 * cw - 8, 2, "#B9C4D0FF")

    d.box(44, box_y + 20, 700, 150, "#F4F7FAFF", radius=14, border=f"1 SOLID {LINE}")
    d.text(68, box_y + 36, "THE THREE RULES BEHIND THE GRID", 14, MUTED, "BOLD", INTER, spacing=1)
    for i, t in enumerate(f["notes"]):
        d.circle(74, box_y + 72 + i * 34, 4, "#3E7BB6FF")
        d.para(90, box_y + 62 + i * 34, 630, t, 14, "#33404EFF")
    d.box(766, box_y + 20, 690, 150, "#EFFAF5FF", radius=14, border="1 SOLID #9FD6C2FF")
    d.text(790, box_y + 36, "YOUR PATTERN", 14, "#0B6B54FF", "BOLD", INTER, spacing=1)
    yp = f["your_pattern"]
    mine = next(r for r in f["rows"] if r["trips_per_week"] == yp["trips_per_week"])
    cell = next(cc for cc in mine["cells"] if cc["weeks"] == yp["weeks"])
    d.text(790, box_y + 64, f'{yp["trips_per_week"]} journeys a week, {yp["weeks"]} weeks a year',
           20, INK, "BOLD", CJK)
    d.text(790, box_y + 96, f'Cheapest: {cell["best"]} at £{cell["best_cost"]:,.0f} a year — '
                            f'£{cell["saving_vs_payg"]:,.0f} less than paying for every journey.',
           16, "#0B6B54FF", "BOLD", CJK)
    d.text(790, box_y + 126, "Buy it in the week you actually start travelling, not in January.",
           14, "#3C5348FF", "NORMAL", CJK)
    d.text(44, H - 40, f'{f["not_covered"]} Prices are a realistic structure for one city network, '
                       f'not a real tariff.', 13, MUTED, "NORMAL", CJK)
    return d.finish()


# =====================================================================  case-09
def case09(D, ver="v1") -> str:
    """Which bin does this go in - 900x1440 bin-store poster."""
    W, H = 900, 1440
    d = Doc(W, H, "#F7F6F1FF")
    rec = D["recycling"]
    GREEN = "#1F7A4DFF"
    RED = "#B3261EFF"
    BLUE = "#2A5C9AFF"
    d.box(0, 0, W, 150, "#1B3A2AFF")
    d.box(0, 146, W, 5, "#C9A227FF")
    d.text(40, 24, "Which bin does this go in?", 34, "#FFFFFFFF", "BOLD", CJK)
    d.text(40, 78, f'{rec["council"]} · kerbside rules · if in doubt, the general waste bin', 17,
           "#A8C4B4FF", "NORMAL", CJK)
    d.rtext(W - 40, 100, 26, "BIN STORE POSTER", 14, "#E8C87AFF", weight="BOLD", family=INTER)

    d.box(40, 176, W - 80, 168, "#FFFFFFFF", radius=14, border=f"1 SOLID {LINE}")
    d.text(64, 192, "WHAT COMES WHEN", 14, MUTED, "BOLD", INTER, spacing=1)
    for i, (name, when, what) in enumerate(rec["kerbside"]):
        y = 222 + i * 30
        d.box(64, y + 3, 10, 10, [GREEN, "#8A5A2BFF", "#5B6B7FFF", "#4C7A3AFF"][i], radius=3)
        d.text(84, y, name, 16, INK, "BOLD", CJK)
        d.text(212, y + 1, when, 14, MUTED, "NORMAL", CJK)
        d.text(452, y + 1, what, 13.5, "#3C4A58FF", "NORMAL", CJK)

    d.text(40, 368, "THE ITEMS PEOPLE GET WRONG", 14, MUTED, "BOLD", INTER, spacing=1)
    for i, it in enumerate(rec["items"]):
        y = 396 + i * 86
        col = {"Recycling": GREEN, "Food waste": "#8A5A2BFF", "General waste": RED,
               "Recycling centre": BLUE, "Textile bank": "#7C5CC4FF",
               "Food waste + recycling": "#8A5A2BFF"}.get(it["bin"], "#5B6B7FFF")
        d.box(40, y, W - 80, 74, "#FFFFFFFF", radius=12, border=f"1 SOLID {LINE}")
        d.box(40, y, 7, 74, col, tl=12, bl=12)
        d.text(64, y + 10, it["item"], 19, INK, "BOLD", CJK)
        d.box(W - 300, y + 10, 224, 26, col, radius=6)
        d.tbox(W - 300, y + 10, 224, 26, it["bin"].upper(), 13, "#FFFFFFFF", "CENTER", "BOLD", INTER)
        d.para(64, y + 38, W - 140, it["why"], 14, "#3C4A58FF")

    yb = 396 + len(rec["items"]) * 86 + 8
    d.box(40, yb, W - 80, 84, "#FFF6E5FF", radius=12, border="1 SOLID #E8C87AFF")
    d.text(64, yb + 12, "THE ONE RULE THAT COVERS MOST OF IT", 14, "#8A6410FF", "BOLD", INTER,
           spacing=1)
    d.para(64, yb + 38, W - 140, rec["rule_of_thumb"], 16, "#4A3A16FF", weight="BOLD")
    yc = yb + 100
    d.box(40, yc, W - 80, 96, "#FDF0EEFF", radius=12, border="1 SOLID #E7BDB8FF")
    d.text(64, yc + 12, "WHAT RUINS A WHOLE LORRY LOAD", 14, RED, "BOLD", INTER, spacing=1)
    for i, t in enumerate(rec["top_contaminants"]):
        x = 64 + (i % 3) * 270
        yy = yc + 40 + (i // 3) * 24
        d.circle(x + 4, yy + 8, 3.5, RED)
        d.text(x + 16, yy, t, 14, "#5C2320FF", "NORMAL", CJK)
    d.text(40, H - 34, "Rules summarised from a typical district council service; check your own "
                       "council's list before a big clear-out.", 12.5, MUTED, "NORMAL", CJK)
    return d.finish()


# =====================================================================  case-10
def case10(D, ver="v1") -> str:
    """What a wash really costs - 1440x900 programme comparison."""
    W, H = 1440, 940
    d = Doc(W, H, "#0F1720FF")
    L = D["laundry"]
    TEAL = "#37B58BFF"
    AMBER = "#D9A02BFF"
    RED = "#D9603BFF"
    d.grad(0, 0, W, 120, "#0F1720FF,#1B2634FF", kind="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT")
    d.text(44, 22, "What a wash really costs", 32, "#FFFFFFFF", "BOLD", CJK)
    d.text(44, 74, f'energy {L["tariff_energy_p"]}p per kWh · water {L["tariff_water_p"]}p per litre '
                   f'· detergent {L["detergent_p"]:.0f}p a wash · {L["washes_per_week"]} washes a week',
           18, "#93A6B8FF", "NORMAL", CJK)
    d.rtext(W - 44, 32, 30, f'save {L["saving_30_vs_60_pct"]:.0f}% with the eco 30 programme', 19,
            "#8FE3D8FF", weight="BOLD", family=CJK)

    for i, p in enumerate(L["programmes"]):
        x = 40 + i * 232
        y = 148
        best = p["programme"].startswith("Eco 30")
        d.box(x, y, 212, 400, "#16302AFF" if best else "#18222EFF", radius=14,
              border=f'1 SOLID {TEAL if best else "#283848FF"}')
        d.text(x + 18, y + 16, p["programme"], 19, "#FFFFFFFF", "BOLD", CJK)
        d.text(x + 18, y + 44, f'{p["minutes"]} min', 14, "#93A6B8FF", "NORMAL", MONO)
        d.text(x + 18, y + 84, f'{p["cost_p"]:.1f}p', 40, TEAL if best else "#FFFFFFFF", "BOLD", MONO)
        d.text(x + 18, y + 132, "per wash", 13, "#93A6B8FF", "NORMAL", CJK)
        d.text(x + 18, y + 162, f'£{p["annual_gbp"]:.2f}', 22, "#FFFFFFFF", "BOLD", MONO)
        d.text(x + 18, y + 190, "a year at 4 a week", 12.5, "#93A6B8FF", "NORMAL", CJK)
        bars = [("energy", p["energy_p"], AMBER), ("water", p["water_p"], "#3E7BB6FF"),
                ("detergent", p["detergent_p"], "#7C5CC4FF")]
        for j, (nm, v, col) in enumerate(bars):
            yy = y + 226 + j * 30
            d.text(x + 18, yy, nm, 12.5, "#93A6B8FF", "NORMAL", INTER)
            d.rtext(x + 194, yy - 1, 18, f'{v:.1f}p', 12.5, "#D6E0EAFF", weight="BOLD", family=MONO)
            d.box(x + 18, yy + 16, 176 * v / 52, 5, col, radius=2.5)
        d.para(x + 18, y + 330, 180, p["best_for"], 13, "#B9C7D4FF")
        if best:
            d.box(x + 18, y + 366, 130, 22, TEAL, radius=6)
            d.tbox(x + 18, y + 366, 130, 22, "THE SWEET SPOT", 11, "#0F1720FF", "CENTER", "BOLD",
                   INTER)

    d.box(40, 570, 900, 316, "#18222EFF", radius=14, border="1 SOLID #283848FF")
    d.text(64, 586, "COST PER WASH, SORTED", 14, "#93A6B8FF", "BOLD", INTER, spacing=1)
    mx = max(p["cost_p"] for p in L["programmes"])
    for i, p in enumerate(L["programmes"]):
        y = 620 + i * 38
        d.text(64, y + 2, p["programme"], 15, "#D6E0EAFF", "NORMAL", CJK)
        d.box(280, y, 460 * p["cost_p"] / mx, 20,
              TEAL if p["programme"].startswith("Eco 30")
              else ("#3E7BB6FF" if "60" not in p["programme"] else RED), radius=10)
        d.rtext(904, y - 2, 24, f'{p["cost_p"]:.1f}p · {p["pct_vs_60"]:.0f}%', 14, "#93A6B8FF",
                weight="BOLD", family=MONO)
    d.text(64, 858, f'Doing everything at 30 C instead of 60 C saves £'
                    f'{L["annual_if_all_60"] - L["annual_if_all_eco30"]:.2f} a year at four washes a '
                    f'week.', 15, "#8FE3D8FF", "BOLD", CJK)

    d.box(966, 570, 434, 316, "#18222EFF", radius=14, border="1 SOLID #283848FF")
    d.text(990, 586, "WORTH KNOWING", 14, "#93A6B8FF", "BOLD", INTER, spacing=1)
    for i, t in enumerate(L["notes"]):
        d.circle(996, 628 + i * 74, 4, TEAL)
        d.para(1012, 614 + i * 74, 366, t, 15, "#C7D3DFFF")
    d.text(44, 908, "Energy, water and detergent figures are typical for a 9 kg A-rated machine at "
                    "the stated tariff; your machine's manual wins.", 12.5, "#6C7C8CFF", "NORMAL",
           CJK)
    return d.finish()
