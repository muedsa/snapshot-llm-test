"""B06 data model - one function per everyday-information problem.

Every number that appears on the ten B06 works is computed here (tax bands, degree days,
waterfall deltas, reference-range positions, fare break-evens, laundry costs), so the
screens cannot contradict their own arithmetic. Product/brand names, the patient, the
household and the council are fictional; the formulas and the reference ranges are the
real ones a reader would meet.

Writes tmp/<run>/B06/data/b06-data.json
"""
from __future__ import annotations

import json
import math
import os
from datetime import datetime, timedelta, timezone

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TMP = os.path.join(ROOT, "tmp", RUN, "B06")
os.makedirs(os.path.join(TMP, "data"), exist_ok=True)
TZ = timezone(timedelta(hours=8))
out: dict = {"meta": {
    "fictional": True,
    "note": "All products, brands, people, households and the local council in this portfolio are "
            "invented. Reference ranges, tax bands, WHO free-sugar guidance, energy arithmetic and "
            "geodesy/timing arithmetic are the real formulas a reader would meet.",
    "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
}}

# ============================================================ 1. five medicines, one day
MEDS = [
    {"name": "Levothyroxine", "dose": "75 micrograms", "form": "tablet",
     "times": ["07:00"], "food": "empty stomach, 30 min before breakfast",
     "why": "thyroid replacement", "colour": "#7C3AEDFF",
     "rules": ["30 min before food", "4 h away from iron", "4 h away from calcium",
               "same time every day"],
     "missed": "Take it as soon as you remember if it is more than 4 hours before your next iron or "
               "calcium dose; otherwise skip that day and carry on. Never double up.",
     "repeat_due": "2026-11-04", "supply_days": 32},
    {"name": "Ramipril", "dose": "5 mg", "form": "capsule",
     "times": ["08:00"], "food": "with or without food",
     "why": "blood pressure", "colour": "#1D4ED8FF",
     "rules": ["avoid potassium supplements", "stand up slowly for the first week"],
     "missed": "Take it when you remember on the same day. If it is nearly time for the next dose, "
               "skip the missed one.",
     "repeat_due": "2026-10-21", "supply_days": 18},
    {"name": "Ferrous fumarate", "dose": "210 mg", "form": "tablet",
     "times": ["12:00", "20:00"], "food": "1 hour before food, with water or juice",
     "why": "iron - low ferritin", "colour": "#B45309FF",
     "rules": ["2 h away from calcium", "4 h away from levothyroxine",
               "orange juice helps, tea and milk block it"],
     "missed": "If you miss a dose, take it at least 2 hours away from your calcium tablets. Do not "
               "take two doses closer together than 6 hours.",
     "repeat_due": "2026-10-14", "supply_days": 11},
    {"name": "Calcium carbonate", "dose": "1.25 g", "form": "chewable tablet",
     "times": ["13:00", "21:00"], "food": "with food",
     "why": "bone protection", "colour": "#0E9F8FFF",
     "rules": ["2 h away from iron", "4 h away from levothyroxine", "take with food"],
     "missed": "Take it with your next meal. Keep it at least 2 hours away from the iron tablets.",
     "repeat_due": "2026-11-11", "supply_days": 39},
    {"name": "Atorvastatin", "dose": "20 mg", "form": "tablet",
     "times": ["21:00"], "food": "any time, same time each day",
     "why": "cholesterol", "colour": "#D92D20FF",
     "rules": ["avoid grapefruit juice", "tell any prescriber about muscle pain"],
     "missed": "Take it when you remember unless it is already the next day - then just carry on.",
     "repeat_due": "2026-10-28", "supply_days": 25},
]
# spacing checks: which pairs must be separated, and by how much (minutes)
SPACING = [("Levothyroxine", "Ferrous fumarate", 240),
           ("Levothyroxine", "Calcium carbonate", 240),
           ("Ferrous fumarate", "Calcium carbonate", 120)]
PROPOSED = {"Levothyroxine": ["07:00"], "Ramipril": ["08:00"], "Ferrous fumarate": ["11:30", "19:30"],
            "Calcium carbonate": ["14:00", "22:00"], "Atorvastatin": ["21:00"]}


def build_doses(times_by_med):
    ds = []
    for m in MEDS:
        for t in times_by_med.get(m["name"], m["times"]):
            h, mi = (int(x) for x in t.split(":"))
            ds.append({"time": t, "minutes": h * 60 + mi, "medicine": m["name"],
                       "dose": m["dose"], "colour": m["colour"]})
    return sorted(ds, key=lambda d: d["minutes"])


def check_spacing(ds):
    res = []
    for a, b, gap in SPACING:
        for da in [d for d in ds if d["medicine"] == a]:
            for db in [d for d in ds if d["medicine"] == b]:
                delta = abs(da["minutes"] - db["minutes"])
                delta = min(delta, 1440 - delta)
                res.append({"a": a, "b": b, "a_time": da["time"], "b_time": db["time"],
                            "gap_min": delta, "need_min": gap, "ok": delta >= gap})
    return res


doses = build_doses({m["name"]: m["times"] for m in MEDS})
conflicts = check_spacing(doses)
proposed_doses = build_doses(PROPOSED)
proposed_conflicts = check_spacing(proposed_doses)
out["medicines"] = {
    "patient": "R. A. Whitlock, 68 (fictional)", "carer": "daughter, J. Whitlock (fictional)",
    "listed_by": "Brindlemouth Group Practice (fictional)",
    "medicines": MEDS, "doses": doses, "spacing_checks": conflicts,
    "conflict_count": sum(1 for c in conflicts if not c["ok"]),
    "proposed_doses": proposed_doses, "proposed_spacing_checks": proposed_conflicts,
    "proposed_conflict_count": sum(1 for c in proposed_conflicts if not c["ok"]),
    "dose_count": len(doses),
    "next_repeat": min(m["repeat_due"] for m in MEDS),
    "supply_alert": [{"medicine": m["name"], "days": m["supply_days"], "due": m["repeat_due"]}
                     for m in sorted(MEDS, key=lambda m: m["supply_days"])[:2]],
}

# ============================================================ 2. blood panel
PANEL = [
    ("Haemoglobin", "g/L", 130, 180, 141, 128, "Oxygen carrier in red cells"),
    ("Ferritin", "micrograms/L", 30, 400, 55, 18, "Iron store; falls long before haemoglobin does"),
    ("TSH", "mIU/L", 0.4, 4.0, 3.1, 4.8, "Thyroid-stimulating hormone; high means under-treated"),
    ("Free T4", "pmol/L", 9, 23, 13.0, 12.1, "Active thyroid hormone"),
    ("Total cholesterol", "mmol/L", 0, 5.0, 5.9, 6.4, "All cholesterol carried in the blood"),
    ("HDL cholesterol", "mmol/L", 1.0, 3.0, 1.2, 1.3, "Protective fraction"),
    ("LDL cholesterol", "mmol/L", 0, 3.0, 3.8, 4.3, "The fraction that drives plaque"),
    ("HbA1c", "mmol/mol", 20, 42, 39, 41, "Three-month average blood glucose"),
    ("Creatinine", "micromol/L", 60, 110, 92, 88, "Muscle waste cleared by the kidneys"),
    ("eGFR", "mL/min/1.73m2", 90, 130, 94, 92, "Filtering rate; falls slowly with age"),
    ("ALT", "U/L", 10, 50, 31, 34, "Liver enzyme"),
    ("Vitamin D", "nmol/L", 50, 150, 44, 38, "Low in winter without supplements"),
]
panel = []
for name, unit, low, high, prev, now, meaning in PANEL:
    span = high - low
    pos = (now - low) / span if span else 0.5
    flag = "low" if now < low else ("high" if now > high else "in range")
    panel.append({"name": name, "unit": unit, "low": low, "high": high, "previous": prev,
                  "value": now, "meaning": meaning, "flag": flag,
                  "position": round(max(0.0, min(1.4, pos)), 3),
                  "delta": round(now - prev, 1),
                  "pct_of_range": round(100 * (now - low) / span, 0) if span else None,
                  "prev_position": round(max(0.0, min(1.4, (prev - low) / span)), 3) if span else 0.5})
out["panel"] = {"patient": "R. A. Whitlock (fictional)", "taken": "2026-09-29 08:10",
                "previous": "2026-03-14", "lab": "Brindlemouth General (fictional)",
                "results": panel,
                "out_of_range": [p["name"] for p in panel if p["flag"] != "in range"],
                "improved": [p["name"] for p in panel if
                             (p["flag"] == "in range" and
                              abs(p["value"] - p["low"]) > abs(p["previous"] - p["low"]))]}

# ============================================================ 3. electricity bill
# synthetic daily mean temperatures for two billing months
def month_temps(start_day, days, base):
    return [round(base - 7.2 * math.sin(math.pi * (i / days)) + 1.7 * math.cos(i * 1.1), 1)
            for i in range(days)]


BASE_TEMP = 15.5
prev_temps = month_temps(0, 30, 14.6)
this_temps = month_temps(30, 31, 9.4)
def degree_days(temps):
    return round(sum(max(0.0, BASE_TEMP - t) for t in temps), 1)

prev_kwh, this_kwh = 271.0, 402.0
unit_rate = 24.6      # pence per kWh
standing = 53.8       # pence per day
prev_days, this_days = 30, 31
prev_dd, this_dd = degree_days(prev_temps), degree_days(this_temps)
base_use_prev = 168.0                             # cooking, lights, appliances, hot water
base_use_this = 186.0                             # darker evenings, more tumble drying
price_prev = 23.9
prev_bill = prev_days * standing / 100 + prev_kwh * price_prev / 100
this_bill = this_days * standing / 100 + this_kwh * unit_rate / 100
heat_prev, heat_this = prev_kwh - base_use_prev, this_kwh - base_use_this
steps = [
    ("Colder weather (113 kWh more heating)", (heat_this - heat_prev) * unit_rate / 100),
    ("Darker evenings, tumble dryer, appliances (18 kWh)", (base_use_this - base_use_prev) * unit_rate / 100),
    ("Unit price 0.7p higher on last month's units", prev_kwh * (unit_rate - price_prev) / 100),
    ("One more day of standing charge", (this_days - prev_days) * standing / 100),
]
total_delta = sum(s[1] for s in steps)
out["bill"] = {
    "household": "a two-adult household in Brindlemouth (fictional)",
    "supplier": "Coastline Energy (fictional)",
    "previous": {"month": "September", "days": prev_days, "kwh": prev_kwh,
                 "degree_days": prev_dd, "bill_gbp": round(prev_bill, 2),
                 "base_use_kwh": base_use_prev, "heating_kwh": heat_prev},
    "current": {"month": "October", "days": this_days, "kwh": this_kwh,
                "degree_days": this_dd, "bill_gbp": round(this_bill, 2),
                "base_use_kwh": base_use_this, "heating_kwh": heat_this},
    "delta_gbp": round(this_bill - prev_bill, 2),
    "steps": [{"label": l, "gbp": round(v, 2)} for l, v in steps],
    "steps_sum_gbp": round(total_delta, 2),
    "rounding_note": round(this_bill - prev_bill - total_delta, 2),
    "unit_rate_p": unit_rate, "standing_p_per_day": standing, "price_prev_p": price_prev,
    "kwh_per_degree_day": round((heat_this - heat_prev) / (this_dd - prev_dd), 2) if this_dd != prev_dd else None,
    "what_changes_it": [
        ("Thermostat down 1 degree C", -8.40),
        ("Shorter showers (4 days a week)", -3.10),
        ("Dry washing on a line", -11.20),
        ("Fridge off the sunny wall", -1.30),
        ("Wash at 30, not 60", -4.60),
    ],
}

# ============================================================ 4. payslip
gross_year = 39000.0
personal_allowance = 12570.0
basic_limit = 50270.0
ni_threshold = 12570.0
ni_rate = 0.08
pension_employee = 0.05
pension_employer = 0.03
loan_threshold = 27295.0
loan_rate = 0.09
taxable = max(0.0, gross_year - personal_allowance)
tax_year = 0.20 * min(taxable, basic_limit - personal_allowance)
ni_year = ni_rate * max(0.0, min(gross_year, basic_limit) - ni_threshold)
pension_year = pension_employee * gross_year
loan_year = loan_rate * max(0.0, gross_year - loan_threshold)
net_year = gross_year - tax_year - ni_year - pension_year - loan_year
m = 12
income_tax = tax_year / m
ni = ni_year / m
pension = pension_year / m
loan = loan_year / m
net = net_year / m
out["payslip"] = {
    "employer": "Harbour Analytics Ltd (fictional)", "employee": "M. Ellery (fictional)",
    "period": "September 2026", "tax_code": "1257L", "ni_category": "A",
    "annual": {"gross": gross_year, "income_tax": round(tax_year, 2), "ni": round(ni_year, 2),
               "pension": round(pension_year, 2), "student_loan": round(loan_year, 2),
               "net": round(net_year, 2),
               "effective_tax_rate_pct": round(100 * (tax_year + ni_year) / gross_year, 1),
               "employer_pension": round(pension_employer * gross_year, 2),
               "total_reward": round(gross_year + pension_employer * gross_year, 2)},
    "monthly": {"gross": round(gross_year / m, 2), "income_tax": round(income_tax, 2),
                "ni": round(ni, 2), "pension": round(pension, 2),
                "student_loan": round(loan, 2), "net": round(net, 2),
                "take_home_pct": round(100 * net / (gross_year / m), 1)},
    "bands": {"personal_allowance": personal_allowance, "basic_rate_limit": basic_limit,
              "basic_rate_pct": 20, "ni_threshold": ni_threshold, "ni_pct": 8,
              "loan_threshold": loan_threshold, "loan_pct": 9},
    "buys": [("Income tax", "schools, roads, the coastguard and the NHS", round(income_tax, 2)),
             ("National Insurance", "your state pension record and contributory benefits", round(ni, 2)),
             ("Workplace pension", "yours, plus 3 % from the employer", round(pension, 2)),
             ("Student loan", "repaid only while you earn above the threshold", round(loan, 2))],
}

# ============================================================ 5. insurance cover
COVER = [
    ("Escape of water from a burst pipe", "covered", "Sudden and accidental escape is the core risk."),
    ("Storm damage to a fence panel", "covered", "Storm is covered; wear and tear is not."),
    ("Laptop knocked off a table", "covered", "Accidental damage must be added to the policy."),
    ("Bike stolen from a locked shed", "conditional", "Covered only if the shed lock meets the grade in the schedule."),
    ("Phone dropped in a lake", "excluded", "Loss or damage away from the home is not covered."),
    ("Laptop left on a car seat overnight", "excluded", "Cover requires the item not to be left in view."),
    ("Burst pipe found after 45 days", "conditional", "Unoccupied over 30 days needs the water off and a weekly check."),
    ("Freezer breakdown spoils food", "conditional", "Covered for food spoilage only if the freezer is under 10 years old."),
    ("Dog biting a visitor", "excluded", "Pet liability sits on your pet policy, not contents."),
    ("Slow leak from a shower tray", "excluded", "Gradual deterioration is maintenance, not an insured event."),
    ("Burglary via an unlocked window", "conditional", "Cover depends on the security conditions listed in the schedule."),
    ("Mould in a cold bedroom", "excluded", "Condensation and poor ventilation are maintenance."),
    ("Keys lost and locks replaced", "covered", "Covered up to the limit in the schedule."),
    ("A tile cracked by a falling branch", "covered", "Storm or falling object is covered."),
    ("Contents in a garden shed", "conditional", "A separate limit applies, usually a few hundred pounds."),
    ("Accidental damage by a toddler", "covered", "Family accidental damage is included on this policy."),
    ("Wear to a carpet in a doorway", "excluded", "Wear and tear is never an insured event."),
    ("Damage during building work", "conditional", "Requires the works to be declared; structural work usually excluded."),
]
out["insurance"] = {
    "policy": "Home contents plus buildings, Coastline Mutual (fictional)",
    "holder": "the Whitlock household (fictional)",
    "excess_gbp": 150, "cover_limit_gbp": 75000,
    "items": [{"situation": s, "verdict": v, "why": w} for s, v, w in COVER],
    "counts": {"covered": sum(1 for _, v, _ in COVER if v == "covered"),
               "conditional": sum(1 for _, v, _ in COVER if v == "conditional"),
               "excluded": sum(1 for _, v, _ in COVER if v == "excluded")},
    "top_refusals": ["Gradual damage (wear, mould, a slow leak)",
                     "Anything left in view in a vehicle",
                     "Loss away from the home",
                     "Security conditions not met (locks, alarms)",
                     "Damage during undeclared building work",
                     "Items in a shed above the outbuilding limit"],
}

# ============================================================ 6. nutrition label
per100 = {"energy_kcal": 452, "sugar": 24.0, "sat_fat": 6.1, "salt": 0.42, "fibre": 7.4,
          "protein": 9.8}
serving_listed = 45.0        # grams the pack calls one serving
serving_actual = 80.0        # grams a bowl usually holds
pack_g = 375.0
nrvs = {"energy_kcal": 2000, "sugar": 30.0, "sat_fat": 20.0, "salt": 6.0, "fibre": 30.0,
        "protein": 50.0}
def scale(g):
    return {k: round(v * g / 100, 2) for k, v in per100.items()}
out["nutrition"] = {
    "product": "Fruit and nut granola, 375 g box (fictional brand Northmill)",
    "per_100g": per100, "per_listed_serving": scale(serving_listed),
    "per_actual_bowl": scale(serving_actual), "per_pack": scale(pack_g),
    "servings_listed": round(pack_g / serving_listed, 1),
    "bowls_actual": round(pack_g / serving_actual, 1),
    "daily_budget": nrvs,
    "share_of_day_listed": {k: round(100 * scale(serving_listed)[k] / nrvs[k], 0) for k in nrvs},
    "share_of_day_actual": {k: round(100 * scale(serving_actual)[k] / nrvs[k], 0) for k in nrvs},
    "sugar_teaspoons_listed": round(scale(serving_listed)["sugar"] / 4.0, 1),
    "sugar_teaspoons_actual": round(scale(serving_actual)["sugar"] / 4.0, 1),
    "equivalents": [
        ("Sugar in one real bowl (19.2 g)", "4.8 teaspoons, or 64 % of the WHO free-sugar day"),
        ("Salt in one real bowl (0.34 g)", "about 6 % of the 6 g adult maximum"),
        ("Fibre in one real bowl (5.9 g)", "20 % of the 30 g daily target - the good news"),
        ("Energy in one real bowl (362 kcal)", "18 % of a 2 000 kcal day, before the milk"),
    ],
}

# ============================================================ 7. train connection
conn = {
    "station": "Brindlemouth Central (fictional)", "arrival": "08:12", "arrival_platform": 4,
    "departure": "08:20", "departure_platform": 9, "available_min": 8.0,
    "legs": [("Step off and clear the doorway", 0.5, "door"),
             ("Platform 4 to the footbridge stairs", 0.8, "walk"),
             ("Up the stairs with a case", 0.5, "stairs"),
             ("Footbridge to the ticket gate", 0.7, "walk"),
             ("Ticket gate queue at 08:14", 0.5, "queue"),
             ("Concourse to platform 9", 1.0, "walk"),
             ("Down the ramp to the platform", 0.5, "walk"),
             ("Find the coach and board", 0.5, "board")],
    "delay_scenarios": [("On time", 0, 8.0), ("Two minutes late", 2, 6.0),
                        ("Four minutes late", 4, 4.0), ("Six minutes late", 6, 2.0)],
}
conn["needed_min"] = round(sum(l[1] for l in conn["legs"]), 2)
conn["slack_min"] = round(conn["available_min"] - conn["needed_min"], 2)
conn["with_luggage_extra"] = 1.5
conn["next_train"] = "08:48 (platform 2, change at Carrow Junction, 34 min later)"
out["connection"] = conn

# ============================================================ 8. fares
single = 2.80
day_cap = 8.10
week_cap = 40.70
month_price = 156.00
annual_price = 1624.00
weeks_per_month = 52 / 12
rows = []
WEEKS = [52, 48, 44, 40, 34]
for trips in range(2, 31, 2):        # journeys per week
    days = min(7, math.ceil(trips / 2))
    cells = []
    for weeks in WEEKS:
        payg = trips * single * weeks
        day_capped = min(trips * single, day_cap * days) * weeks
        week_capped = min(trips * single, week_cap) * weeks
        passes = math.ceil(weeks / weeks_per_month)
        monthly = passes * month_price
        annual = annual_price
        options = {"Pay as you go": payg, "Day cap": day_capped, "Weekly cap": week_capped,
                   "28-day pass": monthly, "Annual pass": annual}
        best = min(options, key=options.get)
        cells.append({"weeks": weeks, "costs": {k: round(v, 2) for k, v in options.items()},
                      "best": best, "best_cost": round(options[best], 2),
                      "saving_vs_payg": round(payg - options[best], 2)})
    rows.append({"trips_per_week": trips, "days": days, "cells": cells})
wins: dict = {}
for r in rows:
    for cell in r["cells"]:
        wins[cell["best"]] = wins.get(cell["best"], 0) + 1
out["fares"] = {"single_gbp": single, "day_cap_gbp": day_cap, "week_cap_gbp": week_cap,
                "month_price_gbp": month_price, "annual_price_gbp": annual_price,
                "weeks_per_month": round(weeks_per_month, 2), "weeks_options": WEEKS,
                "rows": rows, "win_counts": wins,
                "your_pattern": {"trips_per_week": 16, "weeks": 48},
                "notes": [
                    "The day cap only helps on a day with three or more journeys: 3 x 2.80 = 8.40 "
                    "against a cap of 8.10.",
                    "The weekly cap is dominated by the 28-day pass for anyone who travels every "
                    "week, which is why so few people buy it.",
                    "An annual pass only wins if you travel nearly every week of the year; buy it in "
                    "March, not in December.",
                ],
                "not_covered": "Travelling before 06:30, or on the airport branch, is charged separately."}

# ============================================================ 9. recycling
ITEMS = [
    ("Greasy pizza box", "Food waste + recycling", "Tear it: the clean lid is cardboard, the greasy "
     "base is food waste. Never put the greasy half in recycling.", "#D97706FF"),
    ("Broken drinking glass", "General waste", "Drinking glass melts at a different temperature "
     "from bottles and jars. Wrap it and bin it.", "#D92D20FF"),
    ("Blister packs for tablets", "Recycling centre", "Foil and plastic are fused. Kerbside cannot "
     "split them; the pharmacy takes them back.", "#1D4ED8FF"),
    ("Coffee pods", "Recycling centre", "Aluminium pods go in the metals bank, loose, not in a bag.", "#1D4ED8FF"),
    ("Batteries", "Recycling centre", "Never in any kerbside bin: they start fires in the lorry.", "#D92D20FF"),
    ("Aerosol cans, empty", "Recycling", "Empty is fine. Do not pierce them.", "#0E9F8FFF"),
    ("Clothes and shoes", "Textile bank", "Paired shoes, bagged. Wet textiles are rejected.", "#7C3AEDFF"),
    ("Polystyrene packaging", "General waste", "No kerbside market. Supermarket front-of-store "
     "schemes take some.", "#D92D20FF"),
    ("A broken electric kettle", "Recycling centre", "Small electricals bank, or the kerbside "
     "small-appliance collection if booked.", "#0E9F8FFF"),
]
OUTCOMES = ["Recycling", "Food waste", "General waste", "Recycling centre", "Textile bank"]
out["recycling"] = {
    "council": "Brindlemouth District Council (fictional)",
    "kerbside": [("Recycling", "fortnightly, Tuesday", "card, paper, tins, foil, plastic bottles and pots"),
                 ("Food waste", "weekly, Tuesday", "all cooked and uncooked food, including meat"),
                 ("General waste", "fortnightly, Tuesday", "anything the other two cannot take"),
                 ("Garden waste", "fortnightly, Wednesday", "grass, prunings, no soil")],
    "items": [{"item": i, "bin": b, "why": w, "colour": c} for i, b, w, c in ITEMS],
    "outcomes": OUTCOMES,
    "rule_of_thumb": "If it is smaller than a fist, it goes in the general waste - small items fall "
                     "through the sorting screens and contaminate the recycling.",
    "top_contaminants": ["Bagged recycling", "Greasy card", "Nappies in recycling",
                         "Batteries in any bin", "Wet textiles"],
}

# ============================================================ 10. laundry
energy_p = 24.6      # pence per kWh (same tariff as the bill)
water_p = 0.31       # pence per litre
detergent_p = 12.0   # pence per wash
PROGS = [
    ("Quick 20 C", 0.31, 38, 30, "Lightly worn clothes, no stains", 1),
    ("Eco 30 C", 0.62, 42, 195, "Everyday mixed load - the sweet spot", 2),
    ("Cotton 40 C", 0.86, 55, 160, "Towels and bed linen", 3),
    ("Eco 40-60 C", 0.94, 50, 210, "Mixed load with some stains", 3),
    ("Cotton 60 C", 1.32, 62, 170, "Underwear, sick or soiled linen", 4),
    ("Cotton 90 C", 2.10, 78, 150, "Only for illness in the house", 5),
]
progs = []
for name, kwh, litres, mins, best, temp_score in PROGS:
    cost = kwh * energy_p + litres * water_p + detergent_p
    progs.append({"programme": name, "kwh": kwh, "water_l": litres, "minutes": mins, "best_for": best,
                  "temp_score": temp_score, "energy_p": round(kwh * energy_p, 1),
                  "water_p": round(litres * water_p, 1), "detergent_p": detergent_p,
                  "cost_p": round(cost, 1), "cost_gbp": round(cost / 100, 3),
                  "annual_gbp": round(cost / 100 * 4 * 52, 2)})
ref = progs[4]  # cotton 60
for p in progs:
    p["pct_vs_60"] = round(100 * p["cost_p"] / ref["cost_p"], 0)
out["laundry"] = {
    "tariff_energy_p": energy_p, "tariff_water_p": water_p, "detergent_p": detergent_p,
    "washes_per_week": 4, "programmes": progs,
    "ref": "Cotton 60 C",
    "saving_30_vs_60": round(ref["cost_p"] - progs[1]["cost_p"], 1),
    "saving_30_vs_60_pct": round(100 * (ref["cost_p"] - progs[1]["cost_p"]) / ref["cost_p"], 0),
    "annual_if_all_60": round(ref["cost_gbp"] * 4 * 52, 2),
    "annual_if_all_eco30": round(progs[1]["cost_gbp"] * 4 * 52, 2),
    "notes": ["Most of the cost is heating the water, not running the drum.",
              "A half load uses about 70 % of the energy of a full one - fill it instead.",
              "Washing at 30 C with a good detergent removes most everyday soiling, but not germs: "
              "use 60 C for illness, underwear and cloths."],
}

with open(os.path.join(TMP, "data", "b06-data.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)

print("medicines: doses", out["medicines"]["dose_count"], "conflicts",
      out["medicines"]["conflict_count"])
print("panel: out of range", out["panel"]["out_of_range"])
print("bill: prev", out["bill"]["previous"]["bill_gbp"], "now", out["bill"]["current"]["bill_gbp"],
      "delta", out["bill"]["delta_gbp"], "steps sum", out["bill"]["steps_sum_gbp"],
      "degree days", out["bill"]["previous"]["degree_days"], "->", out["bill"]["current"]["degree_days"])
print("payslip: net/month", out["payslip"]["monthly"]["net"], "take home %",
      out["payslip"]["monthly"]["take_home_pct"])
print("insurance:", out["insurance"]["counts"])
print("nutrition: bowls", out["nutrition"]["bowls_actual"], "sugar/bowl",
      out["nutrition"]["per_actual_bowl"]["sugar"], "share",
      out["nutrition"]["share_of_day_actual"]["sugar"], "%")
print("connection: needed", conn["needed_min"], "slack", conn["slack_min"])
print("fares wins:", out["fares"]["win_counts"])
print("laundry: eco30", progs[1]["cost_p"], "p, 60C", ref["cost_p"], "p, save",
      out["laundry"]["saving_30_vs_60_pct"], "%")
