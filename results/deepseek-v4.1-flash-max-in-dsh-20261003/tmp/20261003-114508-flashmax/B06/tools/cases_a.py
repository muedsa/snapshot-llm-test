"""B06 case builders 01-05: everyday information, reinvented.

Each piece has its own visual language on purpose - the task is ten different problems,
not one design system. Shared code is limited to geometry helpers.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bkit import Doc, CJK, MONO, INTER, tw  # noqa: E402

INK = "#101820FF"
MUTED = "#5B6B7FFF"
LINE = "#DCE3EAFF"
PAPER = "#FBF8F2FF"
TEAL = "#0E9F8FFF"
AMBER = "#C2740AFF"
RED = "#C0392BFF"
BLUE = "#1F5FA8FF"
VIOLET = "#6D4AAFFF"


def x_of(minutes, x0, x1):
    return x0 + (minutes / 1440.0) * (x1 - x0)


def hm(minutes):
    return f"{int(minutes)//60:02d}:{int(minutes)%60:02d}"


# =====================================================================  case-01
def case01(D, ver="v1") -> str:
    """Five medicines, one day - A3 fridge-door chart, 1600x1130."""
    W, H = 1600, 1130
    d = Doc(W, H, PAPER)
    med = D["medicines"]
    AX0, AX1 = 96, 1520
    NAVY = "#233043FF"

    d.box(0, 0, W, 132, NAVY)
    d.box(0, 128, W, 6, AMBER)
    d.text(48, 26, "Five medicines, one day", 40, "#FFFFFFFF", "BOLD", CJK)
    d.text(48, 80, f'{med["patient"]} · 5 medicines · {med["dose_count"]} doses · '
                   f'{med["conflict_count"]} timing clashes to fix', 20, "#C7D2E0FF", "NORMAL", CJK)
    d.rtext(W - 48, 32, 34, "FRIDGE DOOR CHART", 18, "#8FA3BBFF", weight="BOLD", family=INTER)
    d.rtext(W - 48, 60, 28, "print at A3, or A4 and stick it up", 15, "#8FA3BBFF")
    d.rtext(W - 48, 84, 28, f'next repeat due {med["next_repeat"]}', 15, "#F0C070FF")

    # ---- legend
    for i, m in enumerate(med["medicines"]):
        x = 48 + i * 306
        d.box(x, 152, 14, 14, m["colour"], radius=4)
        d.text(x + 24, 148, m["name"], 17, INK, "BOLD", CJK)
        d.text(x + 24, 170, f'{m["dose"]} · {", ".join(m["times"])}', 13, MUTED, "NORMAL", MONO)

    # ---- 24 hour band
    d.box(48, 202, W - 96, 396, "#FFFFFFFF", radius=16, border=f"1 SOLID {LINE}")
    # night + meal shading
    for a, b, col in [(0, 7 * 60, "#EDF0F7FF"), (22 * 60, 1440, "#EDF0F7FF")]:
        d.box(x_of(a, AX0, AX1), 250, x_of(b, AX0, AX1) - x_of(a, AX0, AX1), 190, col)
    for a, b, lab in [(7 * 60 + 30, 8 * 60 + 30, "breakfast"), (12 * 60 + 30, 13 * 60 + 30, "lunch"),
                      (18 * 60 + 30, 19 * 60 + 30, "dinner")]:
        d.box(x_of(a, AX0, AX1), 250, x_of(b, AX0, AX1) - x_of(a, AX0, AX1), 190, "#FBF0D8FF")
        d.ctext((x_of(a, AX0, AX1) + x_of(b, AX0, AX1)) / 2, 256, 20, lab, 13, "#9A7B3AFF",
                "BOLD", INTER, pad=8)
    # hour grid
    for h in range(25):
        x = x_of(h * 60, AX0, AX1)
        big = h % 2 == 0
        d.box(x, 440, 1.5, 14 if big else 8, "#B9C4D0FF")
        if big:
            d.ctext(x, 458, 22, f"{h:02d}", 15, MUTED, "BOLD" if h % 6 == 0 else "NORMAL", MONO, pad=6)
    d.box(AX0, 440, AX1 - AX0, 2, NAVY)
    d.text(AX0, 226, "A DAY IN 24 HOURS · dose times are the ones printed on the boxes today",
           14, MUTED, "BOLD", INTER, spacing=1)

    # dose markers, lane-assigned so nothing overlaps
    lanes: dict[int, int] = {}
    used: list[tuple[int, int]] = []
    for dose in med["doses"]:
        lane = 0
        while any(abs(dose["minutes"] - t) < 100 and l == lane for t, l in used):
            lane += 1
        used.append((dose["minutes"], lane))
        lanes[id(dose)] = lane
    for dose in med["doses"]:
        x = x_of(dose["minutes"], AX0, AX1)
        lane = lanes[id(dose)]
        ly = 402 - lane * 52
        d.box(x - 1.5, ly + 22, 3, 440 - ly - 22, dose["colour"])
        d.circle(x, 440, 8, dose["colour"], border="3 SOLID #FFFFFFFF")
        label = f'{dose["medicine"]} · {dose["time"]}'
        wpx = tw(label, 15, CJK) + 22
        d.box(x - wpx / 2, ly, wpx, 26, dose["colour"], radius=7)
        d.tbox(x - wpx / 2, ly, wpx, 26, label, 15, "#FFFFFFFF", "CENTER", "BOLD", CJK)

    # conflicts: a red segment on the axis plus a numbered badge, explained below the axis
    bad = [c for c in med["spacing_checks"] if not c["ok"]]
    for i, c in enumerate(bad):
        a = next(dd for dd in med["doses"] if dd["medicine"] == c["a"] and dd["time"] == c["a_time"])
        b = next(dd for dd in med["doses"] if dd["medicine"] == c["b"] and dd["time"] == c["b_time"])
        xa, xb = x_of(a["minutes"], AX0, AX1), x_of(b["minutes"], AX0, AX1)
        d.box(min(xa, xb) - 6, 434, abs(xb - xa) + 12, 12, RED, radius=6)
        bx = (xa + xb) / 2
        d.circle(bx, 440, 11, RED, border="3 SOLID #FFFFFFFF")
        d.ctext(bx, 428, 24, str(i + 1), 15, "#FFFFFFFF", "BOLD", INTER, pad=4)
        txt = f'{i + 1}.  {a["time"]} {c["a"].lower()} and {b["time"]} {c["b"].lower()}: ' \
              f'{c["gap_min"] // 60} h {c["gap_min"] % 60:02d} apart, but they need ' \
              f'{c["need_min"] // 60} h between them'
        d.circle(AX0 + 14, 508 + i * 32, 10, RED)
        d.ctext(AX0 + 14, 498 + i * 32, 20, str(i + 1), 13, "#FFFFFFFF", "BOLD", INTER, pad=4)
        d.text(AX0 + 34, 498 + i * 32, txt, 16, "#8E2A1EFF", "BOLD", CJK)

    # ---- medicines table
    d.text(48, 618, "WHAT EACH ONE NEEDS", 15, MUTED, "BOLD", INTER, spacing=1)
    cols = [(48, 250, "MEDICINE"), (312, 190, "WHEN"), (516, 300, "WITH FOOD"),
            (830, 320, "KEEP IT APART FROM"), (1164, 388, "IF YOU MISS ONE")]
    d.box(48, 644, W - 96, 34, "#E9EDF3FF", tl=10, tr=10)
    for x, w, name in cols:
        d.text(x + 12, 652, name, 14, MUTED, "BOLD", INTER)
    for i, m in enumerate(med["medicines"]):
        y = 682 + i * 74
        if i % 2 == 0:
            d.box(48, y, W - 96, 74, "#FFFFFFFF")
        d.box(48, y, 6, 74, m["colour"])
        d.text(70, y + 10, m["name"], 19, INK, "BOLD", CJK)
        d.text(70, y + 36, f'{m["dose"]} · {m["why"]}', 14, MUTED, "NORMAL", CJK)
        d.text(324, y + 18, " + ".join(m["times"]), 18, m["colour"], "BOLD", MONO)
        d.para(528, y + 12, 288, m["food"], 15, INK)
        d.para(842, y + 12, 306, "; ".join(m["rules"][:2]), 14, MUTED)
        d.para(1176, y + 12, 364, m["missed"], 14, INK)
    d.box(48, 1058, W - 96, 1, LINE)

    # ---- the fixed day
    d.box(48, 1074, 960, 40, "#E8F5F1FF", radius=10)
    d.text(64, 1084, "Fixed version: iron at 11:30 and 19:30, calcium at 14:00 and 22:00 "
                     "→ 0 clashes, same doses.", 15, "#0B5F52FF", "BOLD", CJK)
    d.rtext(W - 64, 1084, 24, "Source: the boxes and the practice's spacing rules (fictional patient)",
            13, MUTED)
    return d.finish()


# =====================================================================  case-02
def case02(D, ver="v1") -> str:
    """Blood results, in range - 1440x1180 clinical tracks."""
    W, H = 1440, 1180
    d = Doc(W, H, "#F7F9FBFF")
    panel = D["panel"]
    results = panel["results"]
    NAVY = "#12324FFF"
    TRACK0, TRACK1 = 380, 1000
    VAL_X, UNIT_X, DELTA_X = W - 60, 1240, 1000

    d.box(0, 0, W, 120, NAVY)
    d.box(0, 116, W, 4, "#3FA9A0FF")
    d.text(44, 22, "Your blood results, against the range they are judged by", 30, "#FFFFFFFF",
           "BOLD", CJK)
    d.text(44, 72, f'{panel["patient"]} · taken {panel["taken"]} · compared with {panel["previous"]} '
                   f'· {panel["lab"]}', 18, "#A8BDD4FF", "NORMAL", CJK)
    n_out = len(panel["out_of_range"])
    d.rtext(W - 44, 26, 30, f'{n_out} outside range', 20, "#FFD9A0FF", weight="BOLD", family=CJK)
    d.rtext(W - 44, 62, 30, f'{len(results) - n_out} inside range', 20, "#8FE3D8FF",
            weight="BOLD", family=CJK)

    def row(y, r, big):
        h = 96 if big else 46
        if big:
            d.box(40, y, W - 80, h, "#FFFFFFFF", radius=10, border=f"1 SOLID {LINE}")
        d.text(56, y + (16 if big else 12), r["name"], 19 if big else 16, INK, "BOLD", CJK)
        if big:
            d.para(56, y + 44, 284, r["meaning"], 13, MUTED)
        lo, hi = r["low"], r["high"]
        span = hi - lo
        pad = span * 0.22
        a = min(lo - pad, r["previous"], r["value"]) - span * 0.03
        b = max(hi + pad, r["previous"], r["value"]) + span * 0.03

        def X(v):
            return TRACK0 + (v - a) / (b - a) * (TRACK1 - TRACK0)
        ty = y + (40 if big else 20)
        d.box(X(lo), ty - 7, max(2, X(hi) - X(lo)), 14, "#DCEFE9FF", radius=7)
        d.box(X(lo), ty - 7, 2, 14, "#7FC9BCFF")
        d.box(X(hi) - 2, ty - 7, 2, 14, "#7FC9BCFF")
        d.text(X(lo) + 6, ty + (13 if big else 10), f"{lo:g}", 12, "#5B8C84FF", "NORMAL", MONO)
        d.rtext(X(hi) - 6, ty + (13 if big else 10), 22, f"{hi:g}", 12, "#5B8C84FF", family=MONO)
        col = {"in range": TEAL, "low": AMBER, "high": RED}[r["flag"]]
        if abs(X(r["value"]) - X(r["previous"])) > 3:
            d.seg(X(r["previous"]), ty, X(r["value"]), ty, "#B9C4D0FF", 2)
        d.circle(X(r["previous"]), ty, 6, "#FFFFFFFF", border="2 SOLID #8A97A6FF")
        d.circle(X(r["value"]), ty, 8, col, border="3 SOLID #FFFFFFFF")
        if big:
            arrow = "up" if r["delta"] > 0 else "down"
            worse = (r["flag"] == "high" and arrow == "up") or (r["flag"] == "low" and arrow == "down")
            d.text(DELTA_X, y + 18, ("up " if arrow == "up" else "down ") +
                   f'{abs(r["delta"]):g} since March', 14, RED if worse else MUTED, "BOLD", CJK)
            d.rtext(VAL_X + 4, y + 52, 24, {"low": "below range", "high": "above range",
                                            "in range": ""}[r["flag"]], 14, col,
                    weight="BOLD", family=CJK)
        d.rtext(UNIT_X, y + (16 if big else 10), 26, r["unit"], 13, MUTED, weight="NORMAL", family=MONO)
        d.rtext(VAL_X, y + (10 if big else 4), 26, f'{r["value"]:g}', 24 if big else 17,
                INK, weight="BOLD", family=MONO)

    d.text(44, 142, "NEEDS A CONVERSATION AT YOUR NEXT APPOINTMENT", 15, MUTED, "BOLD", INTER,
           spacing=1)
    y = 170
    for r in results:
        if r["flag"] != "in range":
            row(y, r, True)
            y += 96
    d.text(44, y + 20, "INSIDE RANGE - shown compactly, keep doing what you are doing", 15, MUTED,
           "BOLD", INTER, spacing=1)
    y += 50
    for r in results:
        if r["flag"] == "in range":
            row(y, r, False)
            y += 46
    d.text(44, 1104, "Hollow marker = the March result, filled marker = now, so the direction of "
                     "travel is visible without reading numbers.", 14, MUTED, "NORMAL", CJK)
    d.text(44, 1128, "Each track has its own scale, set so that both results and the whole reference "
                     "range fit.", 14, MUTED, "NORMAL", CJK)
    d.rtext(W - 44, 1104, 30, "Not a diagnosis: reference ranges vary by laboratory,", 14, MUTED)
    d.rtext(W - 44, 1128, 30, "and this panel is not a medical record.", 14, MUTED)
    return d.finish()


# =====================================================================  case-03
def case03(D, ver="v1") -> str:
    """Why this electricity bill is higher - 1440x1000 waterfall."""
    W, H = 1440, 1000
    d = Doc(W, H, "#F5F7F4FF")
    bill = D["bill"]
    prev, cur = bill["previous"], bill["current"]
    INKX = "#16221CFF"
    GREEN = "#2E7D5BFF"

    d.box(0, 0, W, 118, "#14261EFF")
    d.box(0, 114, W, 4, "#4CAF7DFF")
    d.text(44, 20, f'Why this bill is £{bill["delta_gbp"]:.2f} higher', 32, "#FFFFFFFF", "BOLD", CJK)
    d.text(44, 70, f'{bill["household"]} · {bill["supplier"]} · {prev["month"]} to {cur["month"]} '
                   f'· unit rate {bill["price_prev_p"]}p rising to {bill["unit_rate_p"]}p',
           18, "#9DBFACFF", "NORMAL", CJK)
    d.rtext(W - 44, 30, 30, f'£{prev["bill_gbp"]:.2f} → £{cur["bill_gbp"]:.2f}', 24, "#D8F3E4FF",
            weight="BOLD", family=MONO)

    # ---- waterfall
    x0, y0, y1 = 90, 190, 620
    lo, hi = 70.0, 125.0

    def Y(v):
        return y1 - (v - lo) / (hi - lo) * (y1 - y0)
    for v in range(70, 126, 10):
        d.box(x0 - 10, Y(v), 980 + 20, 1, "#D9E2DAFF")
        d.rtext(x0 - 18, Y(v) - 11, 22, f"£{v}", 13, "#7C8B80FF", weight="NORMAL", family=MONO)
    running = prev["bill_gbp"]
    bars = [("September bill", prev["bill_gbp"], prev["bill_gbp"], True)]
    for s in bill["steps"]:
        bars.append((s["label"], running, running + s["gbp"], False))
        running += s["gbp"]
    bars.append(("October bill", cur["bill_gbp"], cur["bill_gbp"], True))
    n = len(bars)
    slot = 980 / n
    bw = 128
    for i, (label, a, b, total) in enumerate(bars):
        cx = x0 + slot * i + slot / 2
        top, bot = min(Y(a), Y(b)), max(Y(a), Y(b))
        col = "#1F4D3AFF" if total else ("#C0392BFF" if b > a else GREEN)
        d.box(cx - bw / 2, top, bw, max(6, bot - top), col, radius=6)
        val = b if total else b - a
        txt = f'£{val:.2f}' if total else f'+£{val:.2f}'
        d.ctext(cx, top - 30, 26, txt, 17, col, "BOLD", MONO, pad=6)
        # connector to the next bar
        if i < n - 1:
            nxt = x0 + slot * (i + 1) + slot / 2
            d.dash(cx + bw / 2, Y(b), nxt - bw / 2, Y(b), "#A9B8ACFF", 1.5, 6, 5)
        words = label.split()
        lines, acc = [], ""
        for wd in words:
            trial = (acc + " " + wd).strip()
            if tw(trial, 13, CJK) < slot - 14:
                acc = trial
            else:
                if acc:
                    lines.append(acc)
                acc = wd
        if acc:
            lines.append(acc)
        for li, ln in enumerate(lines[:3]):
            d.ctext(cx, 638 + li * 19, 20, ln, 13, "#4A5A50FF",
                    "BOLD" if total else "NORMAL", CJK, pad=8)
    d.box(x0, y1, 980, 2, "#8FA396FF")
    d.text(x0, 700, "Left bar is last month's bill, right bar is this month's; the four bars between "
                    "them are the reasons, in order of size.", 15, "#4A5A50FF", "NORMAL", CJK)

    # ---- right rail: the two months
    d.box(1090, 190, 310, 300, "#FFFFFFFF", radius=14, border=f"1 SOLID {LINE}")
    d.text(1114, 206, "THE TWO MONTHS", 14, MUTED, "BOLD", INTER, spacing=1)
    rows = [("Electricity used", f'{prev["kwh"]:.0f}', f'{cur["kwh"]:.0f}', "kWh"),
            ("Heating degree days", f'{prev["degree_days"]:.0f}', f'{cur["degree_days"]:.0f}', ""),
            ("Base use, not heating", f'{prev["base_use_kwh"]:.0f}', f'{cur["base_use_kwh"]:.0f}', "kWh"),
            ("Unit rate", f'{bill["price_prev_p"]}', f'{bill["unit_rate_p"]}', "p/kWh"),
            ("Standing charge", "53.8", "53.8", "p/day")]
    for i, (k, a, b, unit) in enumerate(rows):
        y = 230 + i * 46
        d.text(1114, y, k, 14, MUTED, "NORMAL", CJK)
        d.text(1114, y + 20, f'{prev["month"][:3]}', 12, "#9AA79EFF", "NORMAL", INTER)
        d.text(1160, y + 19, a, 17, "#7C8B80FF", "BOLD", MONO)
        d.text(1230, y + 22, "→", 15, "#9AA79EFF", "NORMAL", INTER)
        d.text(1262, y + 19, b, 17, INKX, "BOLD", MONO)
        d.text(1330, y + 21, unit, 12, MUTED, "NORMAL", MONO)
    d.text(1114, 470, f'{bill["kwh_per_degree_day"]} kWh of heating per degree day',
           13, "#4A5A50FF", "NORMAL", CJK)

    # ---- what changes it
    d.box(1090, 508, 310, 252, "#E8F3ECFF", radius=14, border="1 SOLID #BBD9C7FF")
    d.text(1114, 524, "WHAT WOULD BRING IT DOWN", 14, GREEN, "BOLD", INTER, spacing=1)
    smax = max(abs(v) for _, v in bill["what_changes_it"])
    for i, (k, v) in enumerate(bill["what_changes_it"]):
        y = 556 + i * 40
        d.text(1114, y, k, 13, "#2C4638FF", "NORMAL", CJK)
        d.rtext(1380, y - 2, 20, f'£{v:.2f}', 13, GREEN, weight="BOLD", family=MONO)
        d.box(1114, y + 20, 250, 8, "#CDE3D5FF", radius=4)
        d.box(1114, y + 20, 250 * abs(v) / smax, 8, GREEN, radius=4)

    # ---- method
    d.box(90, 736, 980, 224, "#FFFFFFFF", radius=14, border=f"1 SOLID {LINE}")
    d.text(114, 752, "HOW THE FOUR REASONS WERE SPLIT", 14, MUTED, "BOLD", INTER, spacing=1)
    d.para(114, 780, 460,
           f'The meter read {cur["kwh"]:.0f} kWh this month against {prev["kwh"]:.0f} kWh last month, '
           f'and the month was one day longer. Heating is separated from everything else using degree '
           f'days: {prev["degree_days"]:.0f} in {prev["month"]} against {cur["degree_days"]:.0f} in '
           f'{cur["month"]}, at 15.5 °C as the base temperature. Everything that is not heating is '
           f'charged at the same rate in both months, so the difference is volume.', 15, "#33463BFF")
    d.para(600, 780, 446,
           f'The remaining split is arithmetic, not opinion: the four bars add up to '
           f'£{bill["steps_sum_gbp"]:.2f} against a bill difference of £{bill["delta_gbp"]:.2f} '
           f'(the {abs(bill["rounding_note"]):.2f} difference is rounding on the unit rate). '
           f'Weather is the reason this bill moved, so the honest answer to "what can I do" is the '
           f'list on the right, not a change of supplier.', 15, "#33463BFF")
    d.text(114, 920, "Prices and meter readings are invented for this household; the degree-day method "
                     "and the arithmetic are standard.", 13, MUTED, "NORMAL", CJK)
    return d.finish()


# =====================================================================  case-04
def case04(D, ver="v1") -> str:
    """Where your pay goes - 1440x1000 proportional flow."""
    W, H = 1440, 1000
    d = Doc(W, H, "#101418FF")
    ps = D["payslip"]
    gross = ps["monthly"]["gross"]
    parts = [("Take-home pay", ps["monthly"]["net"], "#2FA37CFF"),
             ("Income tax", ps["monthly"]["income_tax"], "#C0563BFF"),
             ("National Insurance", ps["monthly"]["ni"], "#B98A2EFF"),
             ("Workplace pension", ps["monthly"]["pension"], "#3E7BB6FF"),
             ("Student loan", ps["monthly"]["student_loan"], "#7C5CC4FF")]
    d.grad(0, 0, W, 132, "#101418FF,#1B2530FF", kind="LINEAR", begin="TOP_LEFT", end="BOTTOM_RIGHT")
    d.text(44, 24, f'Your £{gross:,.0f} this month, and where it goes', 32, "#FFFFFFFF", "BOLD", CJK)
    d.text(44, 76, f'{ps["employee"]} · {ps["employer"]} · {ps["period"]} · tax code {ps["tax_code"]} '
                   f'· NI category {ps["ni_category"]}', 18, "#93A6B8FF", "NORMAL", CJK)
    d.rtext(W - 44, 30, 30, f'{ps["monthly"]["take_home_pct"]}% reaches your account', 20,
            "#8FE3D8FF", weight="BOLD", family=CJK)

    bx0, bx1, by = 120, 1320, 176
    d.box(bx0, by, bx1 - bx0, 56, "#243040FF", radius=10)
    d.tbox(bx0, by, bx1 - bx0, 56, f'Gross pay  £{gross:,.2f} a month  ·  £{ps["annual"]["gross"]:,.0f} a year',
           21, "#FFFFFFFF", "CENTER", "BOLD", CJK)
    # destination bars
    dy, dh, gap = 420, 64, 22
    total_w = bx1 - bx0 - gap * (len(parts) - 1)
    x = bx0
    for name, val, col in parts:
        w = total_w * val / gross
        d.box(x, dy, w, dh, col, radius=8)
        d.ctext(x + w / 2, dy + 18, 26, f"{val / gross * 100:.0f}%", 17, "#0E1319FF", "BOLD", MONO,
                pad=6)
        x += w + gap
    # ribbons: filled quadrilaterals joining the gross bar to each destination bar
    sx = bx0
    dx = bx0
    for name, val, col in parts:
        sw = (bx1 - bx0) * val / gross
        w = total_w * val / gross
        pts = [(sx + 7, by + 56), (sx + sw - 7, by + 56), (dx + w, dy), (dx, dy)]
        _fill_poly(d, pts, col[:7] + "5A", step=5)
        sx += sw
        dx += w + gap
    d.text(44, 186, "GROSS", 13, "#93A6B8FF", "BOLD", INTER, spacing=2)
    explain = {
        "Take-home pay": "rent, food, travel and everything else",
        "Income tax": "schools, roads, the coastguard and the NHS",
        "National Insurance": "your state pension record and contributory benefits",
        "Workplace pension": "your retirement pot, plus 3 % added by the employer",
        "Student loan": "repaid only while you earn above the threshold",
    }
    d.text(44, 516, "WHERE EACH LINE GOES", 13, "#93A6B8FF", "BOLD", INTER, spacing=2)
    for i, (name, val, col) in enumerate(parts):
        y = 546 + i * 40
        d.box(44, y + 8, 16, 16, col, radius=4)
        d.text(70, y + 2, name, 17, "#E6EDF3FF", "BOLD", CJK)
        d.rtext(470, y - 2, 24, f'£{val:,.2f} a month', 16, "#FFFFFFFF", weight="BOLD", family=MONO)
        d.rtext(680, y - 2, 24, f'£{val * 12:,.0f} a year', 16, "#93A6B8FF", weight="NORMAL", family=MONO)
        d.text(710, y + 3, explain[name], 15, "#93A6B8FF", "NORMAL", CJK)
    d.box(44, 754, 1332, 172, "#1A2430FF", radius=14, border="1 SOLID #2C3B4CFF")
    d.text(70, 770, "WORTH KNOWING", 14, "#8FE3D8FF", "BOLD", INTER, spacing=1)
    facts = [f'Your effective rate on tax and NI together is {ps["annual"]["effective_tax_rate_pct"]}%.',
             f'The pension line is £{ps["monthly"]["pension"]:,.2f} of your money, and your employer adds '
             f'£{ps["annual"]["employer_pension"] / 12:,.2f} a month on top of it.',
             f'Total reward, including the employer pension: £{ps["annual"]["total_reward"]:,.0f} a year.',
             'The student loan stops the moment your pay drops below the threshold for the month.']
    for i, t in enumerate(facts):
        col = i % 2
        row = i // 2
        x = 70 + col * 670
        yy = 802 + row * 56
        d.circle(x + 5, yy + 8, 4, "#2FA37CFF")
        d.para(x + 20, yy - 2, 610, t, 15, "#C3D0DCFF")
    d.text(44, 946, "Salary, tax code and student loan plan are invented for this employee; the bands, "
                    "rates and thresholds are the standard ones.", 13, "#6C7C8CFF", "NORMAL", CJK)
    return d.finish()


def _fill_poly(d, pts, color, step=5):
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


# =====================================================================  case-05
def case05(D, ver="v1") -> str:
    """What the policy does not cover - 1500x1050 verdict matrix."""
    W, H = 1500, 1050
    d = Doc(W, H, "#FFFFFF")
    ins = D["insurance"]
    COV, COND, EXC = "#0E8A72FF", "#B57608FF", "#B3261EFF"
    vcol = {"covered": COV, "conditional": COND, "excluded": EXC}
    d.box(0, 0, W, 124, "#1B2A41FF")
    d.box(0, 120, W, 4, "#D9A02BFF")
    d.text(44, 22, "What your policy does not cover", 32, "#FFFFFFFF", "BOLD", CJK)
    d.text(44, 74, f'{ins["policy"]} · excess £{ins["excess_gbp"]} · contents limit '
                   f'£{ins["cover_limit_gbp"]:,} · {ins["counts"]["covered"]} covered · '
                   f'{ins["counts"]["conditional"]} conditional · {ins["counts"]["excluded"]} excluded',
           18, "#9FB3C8FF", "NORMAL", CJK)
    d.rtext(W - 44, 34, 30, "18 situations, sorted by verdict", 18, "#E8C87AFF", weight="BOLD",
            family=CJK)

    order = {"covered": 0, "conditional": 1, "excluded": 2}
    items = sorted(ins["items"], key=lambda x: order[x["verdict"]])
    tw_, th = 456, 116
    for i, it in enumerate(items):
        col = i % 3
        row = i // 3
        x = 40 + col * 480
        y = 152 + row * 126
        d.box(x, y, tw_, th, "#FBFCFDFF", radius=12, border=f"1 SOLID {LINE}")
        d.box(x, y, 8, th, vcol[it["verdict"]], tl=12, bl=12)
        d.para(x + 24, y + 20, tw_ - 168, it["situation"], 17, INK, weight="BOLD")
        d.box(x + tw_ - 126, y + 18, 108, 26, vcol[it["verdict"]], radius=6)
        d.tbox(x + tw_ - 126, y + 18, 108, 26, it["verdict"].upper(), 13, "#FFFFFFFF", "CENTER",
               "BOLD", INTER)
        d.para(x + 24, y + 60, tw_ - 44, it["why"], 14, MUTED)
    yb = 152 + 6 * 126 + 6
    d.box(40, yb, W - 80, 96, "#FDF3F2FF", radius=12, border=f"1 SOLID #F0C8C4FF")
    d.text(64, yb + 12, "THE SIX THINGS MOST OFTEN REFUSED", 14, EXC, "BOLD", INTER, spacing=1)
    for i, t in enumerate(ins["top_refusals"]):
        col = i % 3
        row = i // 3
        x = 64 + col * 480
        yy = yb + 38 + row * 24
        d.circle(x + 4, yy + 8, 3.5, EXC)
        d.text(x + 16, yy, t, 14, "#5C2320FF", "NORMAL", CJK)
    return d.finish()
