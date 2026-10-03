"""Assemble every B05 deliverable from the real artefacts.

Reads:  tmp/<run>/B05/data/b05-data.json, requests.jsonl, render/*.png, dsl/*.snapshot
Writes: outputs/<run>/B05/case-01..10/{final.png,final.snapshot,case.md}
        outputs/<run>/B05/{portfolio.json,portfolio.md,gallery.html,product-brief.md,
                           journey.json,snapshot-usage.md,task-metrics.json}
        tmp/<run>/B05/{iterations.jsonl,tool-usage.jsonl}
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TASK = "B05"
TZ = timezone(timedelta(hours=8))
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite", "shared"))
import suite_common as SC  # noqa: E402

DATA = json.load(open(os.path.join(TMP, "data", "b05-data.json"), encoding="utf-8"))
REQS = SC.read_jsonl(os.path.join(TMP, "requests.jsonl"))
BY_ID = {r["request_id"]: r for r in REQS}

# newest good render per case (case-06 needed a later fix under its own version tag)
FINAL = {
    "case-01": ("final", "B05-REQ-0026"),
    "case-02": ("final", "B05-REQ-0027"),
    "case-03": ("final", "B05-REQ-0028"),
    "case-04": ("final", "B05-REQ-0029"),
    "case-05": ("final", "B05-REQ-0030"),
    "case-06": ("v4", "B05-REQ-0036"),
    "case-07": ("final", "B05-REQ-0032"),
    "case-08": ("final", "B05-REQ-0033"),
    "case-09": ("final", "B05-REQ-0034"),
    "case-10": ("final", "B05-REQ-0035"),
}

CASES = [
    dict(
        id="case-01", title="Dawn go/no-go card", file="dawn-go-no-go",
        audience="Skipper of a 5.8 m open launch, at the kitchen table at 05:40 before a Saturday trip",
        use_context="Phone, dark room, one hand, before sunrise (sunrise 06:33)",
        user_goal="Decide whether to launch today, and file the float plan before leaving the house",
        content_basis="Computed by tools/b05_data.py: four-constituent harmonic tide, route geodesy, "
                      "fuel arithmetic, solar times. Port, vessel and people are fictional.",
        visual_intent="Verdict first: one word at 64 px, then the four checks that produced it, then the "
                      "tide curve that justifies the timing",
        dims=[500, 1060],
        caps="Stack absolute positioning, LINEAR gradient, rotated-segment polyline tide curve, "
             "gate shading, event markers, rounded dark cards, mono+CJK fonts",
        criteria="The GO/NO-GO verdict is readable in under two seconds at arm's length; every number "
                 "matches b05-data.json; nothing overlaps at 100 %",
        review="Viewed case-01.v1 (B05-REQ-0004) and case-01.final (B05-REQ-0026)",
        iters="B05-IT-002 (visual, v1 -> v2/final)",
        issues=[],
        fix="v1: the 'out 06:35' mark label collided with the panel title and the plan still showed "
            "06:20/15:10 after the day plan was re-timed. Moved the mark label under the dot, dropped "
            "the 'now' label box into the caption row and re-synced launch 06:25 / back 15:08."),
    dict(
        id="case-02", title="Tide and stream day chart", file="tide-stream-chart",
        audience="The same skipper, planning properly the evening before, and any small-craft user who "
                 "wants the whole tidal day on one screen",
        use_context="Desktop or chart table, 1600x1000, read while planning",
        user_goal="Find the two bank-crossing windows and the slack-water times, and know how much "
                  "water the crossing needs",
        content_basis="Harmonic tide curve, stream model from the rate of rise, rule-of-twelfths table "
                      "and gate windows computed by tools/b05_data.py",
        visual_intent="An instrument panel: luminous curve on navy, green gate bands, red deadline, and "
                      "a stream strip of per-hour arrows under it",
        dims=[1600, 1000],
        caps="24-hour polyline with 5-minute sampling, column fill under the curve, dashed deadline, "
             "event markers, per-hour rotated arrows, bars",
        criteria="Both gate windows and both planned crossings can be read off without arithmetic; the "
                 "stream direction is unambiguous; the right rail answers 'how much water'",
        review="Viewed case-02.v1 (B05-REQ-0006) and case-02.v2/final (B05-REQ-0010, 0027)",
        iters="B05-IT-003 (visual + shared kit fix, v1 -> v2/final)",
        issues=[],
        fix="v1 rendered 'Tide &amp; stream' and 'STREAM &lt; 0.2 KN' literally: the service does not "
            "decode XML entities in text nodes, so the shared esc() was changed to emit text verbatim. "
            "Also moved the slack-water note and the twelfths panel apart."),
    dict(
        id="case-03", title="Passage plan (A4, laminated)", file="passage-plan-a4",
        audience="Skipper and crew in the cockpit; also the shore contact who reads the same plan",
        use_context="A4 portrait, printed and laminated, read in daylight and spray",
        user_goal="Fly the route: legs, bearings, ETAs, tide at each arrival, abort criteria and the "
                  "escape route if the bank gate fails",
        content_basis="Leg bearings and distances from real geodesy on fictional waypoints; ETAs from the "
                      "day plan; tide at arrival from the harmonic model",
        visual_intent="A working document, not a poster: dense leg table, a chart sketch with the escape "
                      "route, then the abort and emergency blocks",
        dims=[1240, 1754],
        caps="Scanline-filled coastline polygon, lat/lon graticule, dashed escape route, arrow heads, "
             "zebra table rows, per-row gate colouring",
        criteria="Every leg has bearing, distance, ETA and arrival height; the bank-crossing rows are "
                 "marked; the escape route is drawn; no two blocks overlap",
        review="Viewed case-03.v1 (B05-REQ-0008), v2 (0011) and v3/final (0012, 0028)",
        iters="B05-IT-004 + B05-IT-005 (visual, v1 -> v2 -> v3/final)",
        issues=[],
        fix="v1: Old Keel Bank straddled the coastline, sections E/F overlapped section C/D, arrival "
            "times did not match the day plan and the gate marker sat on the wrong rows. v2: coastline "
            "redrawn north of every waypoint, sections re-flowed, ETAs and gate rows corrected. v3: "
            "shortened the fuel footnote that ran past the page edge."),
    dict(
        id="case-04", title="Five-morning weather windows", file="weather-windows",
        audience="The skipper deciding which of the next five mornings to take off work for",
        use_context="Desktop, 1600x1000, read the evening before with the family calendar open",
        user_goal="Pick the safest morning window and know what would cancel it",
        content_basis="Hand-authored three-model window table consistent with the tide gates and the "
                      "route; model names Nimbus-HR / Pelagic-9 / Coastal-Meso are invented",
        visual_intent="A comparison matrix where colour carries the verdict and dots carry model "
                      "agreement, with the three Saturday wind curves plotted underneath",
        dims=[1600, 1000],
        caps="Grid of filled cells with per-cell accent bars, small-multiple polyline chart, "
             "agreement dots, decision band",
        criteria="The best and worst windows are obvious at a glance, the reason is stated in words, and "
                 "model disagreement is visible rather than hidden",
        review="Viewed case-04.v1 (400 error, B05-REQ-0013) and v2/final (0014, 0015, 0029)",
        iters="B05-IT-006 (syntax-fix) + B05-IT-007 (visual)",
        issues=[],
        fix="v1 failed with PARSE_ERROR 400 because the forecast colours came out of the data model as "
            "bare hex without '#'; fixed in b05_data.py. v2 then needed the model legend moved below the "
            "axis labels and one bullet shortened to stay inside its card."),
    dict(
        id="case-05", title="Float plan and shore watch", file="float-plan-shore-watch",
        audience="The shore contact (a family member ashore) and the skipper filing the plan",
        use_context="Phone, mid-morning at home, no specialist knowledge",
        user_goal="Understand exactly when to expect contact, what happens if it does not come, and what "
                  "to do at each escalation step",
        content_basis="Check-in ladder and escalation times derived from the day plan and the drift model; "
                      "shore-contact view derived from the same route and position data",
        visual_intent="Quiet, light, reassuring: one navy filing card, then a ladder with times and a red "
                      "escalation block that is impossible to misread",
        dims=[500, 1060],
        caps="Light card stack, timeline with connector line, inline mini-chart of the route (filled "
             "coastline plus polyline), status pills",
        criteria="A non-sailor can say what happens at 15:38, 16:08 and 16:38 without help; the number of "
                 "check-ins is explicit",
        review="Viewed case-05.v2 (B05-REQ-0016) and case-05.final (0030)",
        iters="B05-IT-008 (visual)",
        issues=[],
        fix="v2: the mini chart's town label landed on top of the 'Petrel' summary text and the closing "
            "sentence ran off the canvas; the town label is now drawn only on the full chart and the "
            "sentence was shortened."),
    dict(
        id="case-06", title="On-water glance display", file="on-water-glance",
        audience="The skipper at the helm, wet hands, gloves, bright sunlight, engine idling on a drift",
        use_context="Tablet on a RAM mount at the console, 1180x820, read from 1 m in direct sun",
        user_goal="Know speed, depth, the bank gate countdown and the fuel state without reading a menu",
        content_basis="Position, time, depth and fuel state consistent with the day plan; gate state from "
                      "the harmonic model at 11:05; fuel burn from the fuel model",
        visual_intent="Glanceable instrument: four big tiles, 104 px numerals, one loud red CLOSED card, "
                      "compass tape across the top",
        dims=[1180, 820],
        caps="Compass ribbon generated from the heading (1 deg = 3 px), huge numerals, progress bar, "
             "colour-coded state cards",
        criteria="Every value is readable at a glance in sunlight; the CLOSED gate is unambiguous; the "
                 "return plan is on the same screen",
        review="Viewed case-06.v2 (B05-REQ-0017) and case-06.v4 (0036)",
        iters="B05-IT-009 (visual)",
        issues=[],
        fix="v2: the fuel tile put the 84 px value on top of its own unit line and bar; the tile was "
            "re-laid out (value 72 px with the unit line, bar and note stacked below)."),
    dict(
        id="case-07", title="Overdue: drift datum and search boxes", file="overdue-drift-datum",
        audience="Coastguard watch officer and the shore contact, 20 minutes into an overdue alarm",
        use_context="Desktop in the ops room or at home, dark theme, high stress, 1600x1000",
        user_goal="See where the boat probably is, in what order to search, and what is still missing "
                  "from the picture",
        content_basis="Drift model in tools/b05_data.py: 3.5 % leeway on 18 kn of wind plus the tidal "
                      "stream at 15:52, giving 1.16 kn toward 047 deg and three growing boxes",
        visual_intent="Red on near-black, one chart carrying the whole story, numbers kept quiet so the "
                      "boxes and the LKP dominate",
        dims=[1600, 1000],
        caps="Equirectangular projection, scanline-filled ellipses, drift arrows, badge markers, "
             "probability bars, dark-red cards",
        criteria="Box order, probability, area and sweep time are all legible; the assumptions behind "
                 "the drift are stated on the image; nothing claims more certainty than the model has",
        review="Viewed case-07.v1 (B05-REQ-0018), v2 (0020) and final (0032)",
        iters="B05-IT-010 + B05-IT-011 (visual)",
        issues=[],
        fix="v1 drew 3.6 nm search boxes on a 6.7 nm-wide chart, so the ellipses swamped the frame and "
            "their labels collided with the bank label. v2 widened the chart to 13 nm, moved the box "
            "labels into a legend and badged the centres; the final added a backing plate behind the "
            "LKP label."),
    dict(
        id="case-08", title="Fuel and range planner", file="fuel-range-planner",
        audience="The skipper deciding how much fuel to take and what to do if the wind gets up on the "
                 "return leg",
        use_context="Tablet at home or on the boat before slipping, dark instrument panel",
        user_goal="See where 36 L goes in three scenarios, and know the range at each speed before "
                  "committing to a long drift",
        content_basis="Burn 8.2 L/h at 12 kn and 1.1 L/h drifting with a 20 % reserve, computed per leg "
                      "and per drift minute by tools/b05_data.py",
        visual_intent="A ladder rather than a pie: one stacked bar per scenario, so the reserve is "
                      "visibly the part you never plan to touch",
        dims=[1180, 820],
        caps="Stacked segment bars with in-segment labels, horizontal range bars, scenario table, "
             "amber recommendation card",
        criteria="The 12 kn headwind case and its margin are the most prominent numbers; range by speed "
                 "shows the slow-down option; no column overflows its card",
        review="Viewed case-08.v1 (B05-REQ-0019) and v2/final (0021, 0033)",
        iters="B05-IT-012 (visual)",
        issues=[],
        fix="v1: the ladder footnote and the margin column ran past their panels and the recommendation "
            "bullets wrapped into each other; text shortened, columns re-spaced, margin shown as L / nm."),
    dict(
        id="case-09", title="Harbour office e-ink noticeboard", file="harbour-noticeboard",
        audience="Everyone on the pontoon: berth holders, visiting crews, the harbour master",
        use_context="800x1200 e-ink panel in the harbour office window, read from 2-3 m, refreshed at "
                    "07:30",
        user_goal="One look tells you which boats are out, who is late, what is closed and what the "
                  "weather is doing",
        content_basis="Fleet list, notices, gate windows and the yellow wind warning, all consistent with "
                      "the tide model and the passage plan",
        visual_intent="Paper-like greyscale with a single red accent: no gradients, no shadows, heavy "
                      "rules, type sized for three metres",
        dims=[800, 1200],
        caps="E-ink palette, table with highlight row, tag blocks, wrapping notice text, split gate / "
             "warning panel",
        criteria="The Petrel row is findable in under three seconds; the warning and the gate times are "
                 "both visible without scrolling; nothing is clipped",
        review="Viewed case-09.v1 (B05-REQ-0022) and v3/final (0024, 0034)",
        iters="B05-IT-013 (visual)",
        issues=[],
        fix="v1: the weather block ran past the right edge of the board; it was re-broken into four short "
            "lines that fit the 768 px text column."),
    dict(
        id="case-10", title="Season debrief", file="season-debrief",
        audience="The skipper at the end of the season, deciding what to change next year",
        use_context="Desktop or tablet at home, 1600x1000, unhurried",
        user_goal="See the season's patterns and adopt three or four concrete rules for next year",
        content_basis="26-trip log, monthly distance and trip counts, forecast-error series and three "
                      "logged close calls with the rule each one produced",
        visual_intent="Calm analytics: bar chart of the season, a red error line that rises as the "
                      "season goes on, and a navy card that turns observations into rules",
        dims=[1600, 1000],
        caps="Bar chart with per-bar labels, line chart with a shaded threshold band, KPI tiles, "
             "checkbox row",
        criteria="Every chart is readable without the caption; the three close calls each end in a rule; "
                 "the season totals match the log",
        review="Viewed case-10.v1 (B05-REQ-0023) and v3/final (0025, 0035)",
        iters="B05-IT-014 (visual)",
        issues=[],
        fix="v1: the KPI sub-labels collided with the 44 px values and the threshold-band label sat under "
            "a data point; sub-labels moved onto their own line and the band label shortened."),
]

# ---------------------------------------------------------------- copy artefacts
for c in CASES:
    cdir = os.path.join(OUT, c["id"])
    os.makedirs(cdir, exist_ok=True)
    ver, req = FINAL[c["id"]]
    src_png = os.path.join(TMP, "render", f'{c["id"]}.{ver}.png')
    src_dsl = os.path.join(TMP, "dsl", f'{c["id"]}.{ver}.snapshot')
    assert os.path.exists(src_png), src_png
    assert os.path.exists(src_dsl), src_dsl
    shutil.copyfile(src_png, os.path.join(cdir, "final.png"))
    shutil.copyfile(src_dsl, os.path.join(cdir, "final.snapshot"))
    rec = BY_ID[req]
    c["png"] = f'{c["id"]}/final.png'
    c["snapshot"] = f'{c["id"]}/final.snapshot'
    c["request_ids"] = [req]
    c["bytes"] = os.path.getsize(src_png)
    c["request"] = {"http_status": rec["http_status"], "content_type": rec["content_type"],
                    "duration_ms": rec["duration_ms"], "service_request_id": rec["service_request_id"],
                    "ended_at": rec["ended_at"], "response_file": os.path.relpath(src_png, ROOT)}

# ---------------------------------------------------------------- case.md
for c in CASES:
    md = f"""# {c['id']} · {c['title']}

**Final image** `final.png` ({c['dims'][0]}x{c['dims'][1]}, {c['bytes']} bytes) ·
**DSL** `final.snapshot` · **request** {c['request_ids'][0]} (HTTP {c['request']['http_status']},
{c['request']['content_type']}, {c['request']['duration_ms']} ms, service id
`{c['request']['service_request_id']}`)

## Scenario
- **Audience**: {c['audience']}
- **Where and when**: {c['use_context']}
- **What the user is trying to finish**: {c['user_goal']}
- **Content basis**: {c['content_basis']}
  Everything is fictional except the formulas: see `../product-brief.md` and `../journey.json`.

## Visual choices
{c['visual_intent']}

DSL capabilities used: {c['caps']}

## Self-check against my own completion criteria
- {c['criteria']}
- Visual evidence: {c['review']}.
- Iterations: {c['iters']}.
- Defects found by looking and the fix applied: {c['fix']}
- Unresolved issues: {'none' if not c['issues'] else '; '.join(c['issues'])}

## Assets
No external or photographic assets: the whole frame is built from Snapshot DSL primitives
(`Container`, `Stack`/`Positioned`, `Transform`, `ClipOval`/`ClipRRect`, gradients, `Text`).
"""
    with open(os.path.join(OUT, c["id"], "case.md"), "w", encoding="utf-8") as fh:
        fh.write(md)

print("case dirs written:", len(CASES))

# ---------------------------------------------------------------- journey.json
JOURNEY = [
    ("case-01", "Decide", "Evening before: a plan exists in the app but is not confirmed",
     "GO with a 06:25 launch; float plan filed at 05:44", "Confirms the plan and pushes it to the shore contact"),
    ("case-02", "Understand", "The skipper trusts the app's verdict but wants the tide reasoning",
     "Both bank windows and the required 2.50 m are on one screen", "Sets the two crossing times in the plan"),
    ("case-03", "Prepare", "The plan exists digitally but the cockpit has no screen",
     "A printed A4 plan with legs, ETAs, abort criteria and the escape route",
     "Goes in the laminate pocket; becomes the document the crew actually flies"),
    ("case-04", "Choose the day", "Four candidate mornings and no way to compare them",
     "Saturday 06-09 is chosen; Sunday is cancelled; Monday is the fallback",
     "Fixes the date that cases 01-03 are planned for"),
    ("case-05", "Hand over", "Someone ashore needs to know when to worry",
     "A check-in ladder and a three-step escalation, with what the shore contact sees",
     "Puts a second person into the safety system"),
    ("case-06", "On the water", "The screen must be readable with gloves in sunlight",
     "Speed, depth, gate countdown and fuel on one glance, plus the return plan",
     "The skipper does not touch the app again until the gate reopens"),
    ("case-07", "When it goes wrong", "No contact at 15:52; the shore contact has to act",
     "Drift datum, three search boxes with probabilities and sweep times",
     "The shore side of the same data the boat was using"),
    ("case-08", "Decide the margin", "36 L aboard, a long drift planned and wind forecast to build",
     "Three fuel scenarios with the reserve shown as untouchable",
     "Answers 'can I stay out for one more drift?' before it is asked at sea"),
    ("case-09", "Share", "The harbour needs to know who is out and who is late",
     "A public e-ink board with the fleet, the notices and the gate times",
     "Makes the check-in data useful to people who are not on the boat"),
    ("case-10", "Learn", "The season ends with three close calls and no pattern view",
     "Monthly distance, forecast error trend and three rules adopted",
     "Feeds the next season's planning, which is where case-01 begins again"),
]
journey = {
    "product": "Kelpline",
    "subject": "A fictional coastal passage planner and on-water safety companion for small craft "
               "and the people waiting ashore",
    "all_fictional": ["Brindlemouth harbour and all place names", "the vessel Petrel and its crew",
                      "the weather models Nimbus-HR / Pelagic-9 / Coastal-Meso",
                      "every harbour notice, phone number and vessel on the noticeboard"],
    "computed_not_invented": ["tide curve and extremes (four-constituent harmonic sum)",
                              "stream speed and direction from the rate of rise",
                              "leg bearings and distances (great-circle on fictional coordinates)",
                              "fuel burn, reserve and margin arithmetic",
                              "drift datum, box radii, sweep times",
                              "sunrise, sunset and civil dusk"],
    "model_files": ["tmp/20261003-114508-flashmax/B05/tools/b05_data.py",
                    "tmp/20261003-114508-flashmax/B05/data/b05-data.json",
                    "tmp/20261003-114508-flashmax/B05/data/tide-curve.csv"],
    "steps": [],
}
for i, (cid, phase, before, after, hands) in enumerate(JOURNEY, start=1):
    c = next(x for x in CASES if x["id"] == cid)
    journey["steps"].append({
        "order": i, "case_id": cid, "title": c["title"], "phase": phase,
        "state_before": before, "this_screen": after, "what_it_hands_on": hands,
        "device": f'{c["dims"][0]}x{c["dims"][1]}', "request_id": c["request_ids"][0],
    })
journey["shared_facts"] = {
    "date": "Saturday 3 October 2026", "vessel": "Petrel, 5.8 m open launch, 2 POB",
    "tide_extremes": "HW 05:10 4.12 m · LW 11:25 0.60 m · HW 17:30 3.81 m · LW 23:35 0.68 m",
    "bank_gate": "crossable at 2.50 m or more: 02:15-08:10 and 14:55-20:20",
    "plan": "launch 06:25 · cross out 06:35 at 3.71 m · 17.6 nm and 326 min on the ground · "
            "cross back 14:58 at 2.55 m · alongside 15:08",
    "fuel": "36 L in two tanks, plan 19.5 L, reserve 7.2 L, 12 kn headwind case 22.9 L",
    "sun": "sunrise 06:33 · sunset 17:44",
}
SC.write_json(os.path.join(OUT, "journey.json"), journey)

# ---------------------------------------------------------------- product brief
brief = f"""# Kelpline — product brief (B05)

*Everything in this brief is a design fiction: the harbour, the boat, the people, the weather models
and every notice on the harbour board are invented. The tides, bearings, fuel arithmetic and drift
numbers are computed by `tmp/20261003-114508-flashmax/B05/tools/b05_data.py` from standard formulas
using invented places, so the screens agree with each other. No user research, field trial or
real deployment was performed and none is claimed.*

## The problem
A small open boat — 5.8 m, one outboard, two people — is the most common way to go fishing or
diving on a coast, and the decision that matters is made in the worst possible conditions: at
05:30 in a dark kitchen, by one person, with a phone in one hand. The information needed is
scattered across a tide table, a wind forecast, a harbour notice, a paper chart and a memory of
what the bank looked like last time. The two failure modes are symmetrical: going out when the
gate or the wind will not allow it, and staying home on a day that was actually fine.

The person who carries the consequences is often not on the boat. Someone ashore is left with
"he said he'd be back by three" and no way to tell a delayed boat from a missing one.

## Who it is for
- **Primary**: the skipper/owner of a 5-7 m open or cuddy boat who goes out 20-40 times a season,
  plans on a phone the night before and reads a laminate in the cockpit.
- **Secondary**: the shore contact — partner, sibling, parent — who has to decide whether to worry.
- **Tertiary**: the harbour office, which currently tracks the same fleet on a whiteboard.

## The product
Kelpline is one safety model shown at four scales:

1. **Gate model.** Every shallow area gets a required height (draft + under-keel margin above the
   drying height). The tide model then produces *windows*, not opinions: for Petrel the Old Keel
   Bank gate is 2.50 m, open 02:15-08:10 and 14:55-20:20 on the day in question.
2. **Plan.** Waypoints, bearings, distances, ETAs, tide at arrival, abort criteria and an escape
   route — one artefact that the phone, the printer and the harbour board all read from.
3. **Watch.** A check-in ladder with published escalation times, so the shore contact knows that
   nothing is expected to happen before 15:38 and exactly what happens after it.
4. **Debrief.** A season log that turns close calls into rules rather than anecdotes.

The through-line is a single tide curve, drawn as a sparkline on the phone, as the main chart on the
desktop, as a shouted instrument on the water, as a datum on the search screen and as an ink line on
the harbour board.

## The ten screens and why each exists
| # | Screen | What it decides |
|---|---|---|
| 1 | Dawn go/no-go card | Launch now, or not at all |
| 2 | Tide and stream chart | Which two windows to cross the bank in |
| 3 | Passage plan (A4) | How the trip is actually flown, and when to abandon it |
| 4 | Weather windows | Which of five mornings to take |
| 5 | Float plan and shore watch | Who worries, when, and what they do |
| 6 | On-water glance display | Speed, depth, gate countdown, fuel — at a glance |
| 7 | Overdue: drift and search datum | Where to search, first and second |
| 8 | Fuel and range planner | How much margin is left in the day |
| 9 | Harbour office board | Who is out, who is late, what is closed |
| 10 | Season debrief | What to change next season |

## Assumptions and limits
- The tide is a four-constituent harmonic sum, not a harmonic analysis of a real port. Real gates
  would use the port's published predictions plus a shallow-water correction.
- The stream model scales stream speed with the rate of rise and holds the direction at 048/228;
  real streams turn through the tide and are strongest around the headlands.
- Drift uses 3.5 % leeway plus 85 % of the surface stream. Search planning in reality uses
  leeway coefficients by vessel type and a Monte Carlo datum; three boxes is a deliberately simple
  illustration.
- The weather table is a hand-authored comparison, not model output, and the three model names are
  invented.
- No usability testing was done: "readable in two seconds" is my judgement from opening the images
  at 100 %, not a measured user result.

## What a next iteration would test
1. Whether the four-item check list on case-01 is the right length before a dawn launch.
2. Whether a shore contact can repeat the escalation ladder back after one read of case-05.
3. Whether the CLOSED gate card on case-06 is readable through polarised sunglasses at 1 m.
"""
with open(os.path.join(OUT, "product-brief.md"), "w", encoding="utf-8") as fh:
    fh.write(brief)

print("journey.json + product-brief.md written")

# ---------------------------------------------------------------- iteration log
def ended(rid):
    r = BY_ID.get(rid)
    return r["ended_at"] if r else None


ITERS = [
    dict(id="B05-IT-001", type="alternative", case_id=None, versions=["probe1", "probe2"],
         parents=[], requests=["B05-REQ-0001", "B05-REQ-0002"],
         viewed_at=ended("B05-REQ-0002"),
         observation="Before designing anything I had to know what this build of the service actually "
                     "renders: rotation through Transform.matrix, gradients, ClipOval/ClipRRect, "
                     "Opacity, shape=CIRCLE, boxShadow and letterSpacing, plus where a Text sits "
                     "vertically inside a fixed-height Container.",
         change="Two probe sheets; probe2 also measured with Python/Pillow to get the ink rows per "
                "alignment constant instead of guessing.",
         verification="All features rendered; the briefing's note that CENTER means bottom-centre is "
                        "wrong for this build (measured: CENTER centres both axes, TOP_LEFT is top-left, "
                        "and a width-constrained Container wraps text at 1.28x font size per line).",
         files=["tmp/20261003-114508-flashmax/B05/dsl/probe1.snapshot",
                "tmp/20261003-114508-flashmax/B05/dsl/probe2.snapshot",
                "tmp/20261003-114508-flashmax/B05/render/probe1.png",
                "tmp/20261003-114508-flashmax/B05/render/probe2.png",
                "tmp/20261003-114508-flashmax/B05/tools/measure_probe2.py"]),
    dict(id="B05-IT-002", type="visual", case_id="case-01", versions=["v1", "v1-fixed"],
         parents=["v1"], requests=["B05-REQ-0004", "B05-REQ-0005"],
         viewed_at=ended("B05-REQ-0005"),
         observation="Viewed case-01 v1: the 'out 06:35' mark label sat on top of the tide strip's "
                     "section title, the white 'now' label box overlapped the same row, the axis tick "
                     "row collided with the caption line, and the verdict card still said launch 06:20 "
                     "/ back 15:10 after the day plan had been re-timed to 06:25 / 15:08.",
         change="Mark labels moved below their dots, the 'now' label folded into the caption row, the "
                "tide card made 14 px taller, and every clock on the screen re-synced from b05-data.json.",
         verification="Re-rendered and viewed: no collisions, the GO card and the chart agree on 06:25 / "
                      "08:10 / 15:08 / 14:58.",
         files=["tmp/20261003-114508-flashmax/B05/render/case-01.v1.png",
                "tmp/20261003-114508-flashmax/B05/render/case-01.final.png"]),
    dict(id="B05-IT-003", type="visual", case_id="case-02", versions=["v1", "v2"],
         parents=["v1"], requests=["B05-REQ-0006", "B05-REQ-0010"],
         viewed_at=ended("B05-REQ-0010"),
         observation="Viewed case-02 v1: the header read 'Tide &amp; stream' and the slack panel read "
                     "'STREAM &lt; 0.2 KN' - the service renders XML entities literally, so escaping "
                     "text breaks it. The slack-water note also overlapped the fourth row and the "
                     "twelfths panel overlapped the stream strip.",
         change="esc() in the shared kit now emits text verbatim (copy avoids raw < and >); slack rows "
                "tightened to 26 px with the note moved to y+496; the twelfths panel shortened to 164 px.",
         verification="Re-rendered and viewed: '&' and 'under 0.2 kn' both read correctly and the right "
                      "rail has three separated cards.",
         files=["tmp/20261003-114508-flashmax/B05/render/case-02.v1.png",
                "tmp/20261003-114508-flashmax/B05/render/case-02.final.png"]),
    dict(id="B05-IT-004", type="visual", case_id="case-03", versions=["v1", "v2"],
         parents=["v1"], requests=["B05-REQ-0008", "B05-REQ-0011"],
         viewed_at=ended("B05-REQ-0011"),
         observation="Viewed case-03 v1: Old Keel Bank straddled the coastline (half the bank was on "
                     "land), sections C/D overlapped E/F, the day-plan rows wrapped into each other, "
                     "the arrival times disagreed with the day plan and the 'gate' marker was on the "
                     "wrong legs.",
         change="Coastline redrawn north of every waypoint; chart inset with a breakwater, pontoons and "
                "town blocks; arrival clock list rebuilt from the day plan; gate colouring limited to "
                "the four legs that actually cross the bank; E/F moved to y=1492 and re-flowed into two "
                "30 px columns.",
         verification="Re-rendered and viewed: the bank is offshore, the sections are separate, the "
                      "day plan fits in two columns.",
         files=["tmp/20261003-114508-flashmax/B05/render/case-03.v1.png",
                "tmp/20261003-114508-flashmax/B05/render/case-03.v2.png"]),
    dict(id="B05-IT-005", type="visual", case_id="case-03", versions=["v2", "v3"],
         parents=["v2"], requests=["B05-REQ-0012"],
         viewed_at=ended("B05-REQ-0012"),
         observation="Viewed case-03 v2: the fuel footnote ran past the right page edge, and the chart's "
                     "'BRINDLEMOUTH' label was clipped by the top of the frame.",
         change="Footnote shortened to one line; the town label moved beside the town blocks.",
         verification="Re-rendered and viewed: page edge clean, every label inside the frame.",
         files=["tmp/20261003-114508-flashmax/B05/render/case-03.v3.png"]),
    dict(id="B05-IT-006", type="syntax-fix", case_id="case-04", versions=["v1"],
         parents=[], requests=["B05-REQ-0013", "B05-REQ-0014"],
         viewed_at=None,
         observation="B05-REQ-0013 returned HTTP 400 PARSE_ERROR: 'Attr [color] unsupported CSS color "
                     "[0E9F8F] at position 4805'. The verdict colours came out of the data model without "
                     "a leading '#'.",
         change="b05_data.py emits CSS colours with '#' in the forecast verdict table.",
         verification="Re-rendered: HTTP 200 image/png.",
         files=["tmp/20261003-114508-flashmax/B05/render/case-04.v1.png.failed.txt"]),
    dict(id="B05-IT-007", type="visual", case_id="case-04", versions=["v2", "final"],
         parents=["v2"], requests=["B05-REQ-0014", "B05-REQ-0015"],
         viewed_at=ended("B05-REQ-0014"),
         observation="Viewed case-04 v2: the three-model legend sat on top of the Saturday chart's hour "
                     "labels and the third bullet in the left card reached the card edge.",
         change="Legend dropped to y=770 and one bullet shortened.",
         verification="Re-rendered (B05-REQ-0015 is the same DSL, so the bytes are identical) and "
                      "viewed: legend clear of the axis labels.",
         files=["tmp/20261003-114508-flashmax/B05/render/case-04.v2.png"]),
    dict(id="B05-IT-008", type="visual", case_id="case-05", versions=["v2", "final"],
         parents=["v2"], requests=["B05-REQ-0016", "B05-REQ-0030"],
         viewed_at=ended("B05-REQ-0030"),
         observation="Viewed case-05 v2: the mini map's 'BRINDLEMOUTH' label printed over the 'Petrel' "
                     "summary text, and the closing sentence ran off the right edge of the canvas.",
         change="The town label is drawn only on the full chart; the closing sentence shortened.",
         verification="Re-rendered and viewed: summary block clean, sentence inside the margin.",
         files=["tmp/20261003-114508-flashmax/B05/render/case-05.v2.png",
                "tmp/20261003-114508-flashmax/B05/render/case-05.final.png"]),
    dict(id="B05-IT-009", type="visual", case_id="case-06", versions=["v2", "v4"],
         parents=["v2"], requests=["B05-REQ-0017", "B05-REQ-0036"],
         viewed_at=ended("B05-REQ-0036"),
         observation="Viewed case-06 v2 (and its final re-render): the fuel tile put the 72-84 px value "
                     "straight through its own unit line, bar and note.",
         change="Fuel tile re-laid out: value 72 px at y+424, unit line at y+496, bar at y+528, note at "
                "y+558. Rendered as case-06.v4 to avoid overwriting the earlier version tag.",
         verification="Re-rendered and viewed: four clean tiles, the CLOSED card unchanged.",
         files=["tmp/20261003-114508-flashmax/B05/render/case-06.v2.png",
                "tmp/20261003-114508-flashmax/B05/render/case-06.v4.png"]),
    dict(id="B05-IT-010", type="visual", case_id="case-07", versions=["v1", "v2"],
         parents=["v1"], requests=["B05-REQ-0018", "B05-REQ-0020"],
         viewed_at=ended("B05-REQ-0020"),
         observation="Viewed case-07 v1: the search boxes were drawn to scale on a chart only 6.7 nm "
                     "wide, so a 3.6 nm box covered the whole frame; box labels collided with the bank "
                     "label and with each other.",
         change="Chart widened to 13.4 x 10.8 nm, box labels moved into a legend, centres badged A/B/C.",
         verification="Re-rendered and viewed: boxes nest visibly along the drift track and every label "
                      "is readable.",
         files=["tmp/20261003-114508-flashmax/B05/render/case-07.v1.png",
                "tmp/20261003-114508-flashmax/B05/render/case-07.v2.png"]),
    dict(id="B05-IT-011", type="visual", case_id="case-07", versions=["v2", "final"],
         parents=["v2"], requests=["B05-REQ-0032"],
         viewed_at=ended("B05-REQ-0032"),
         observation="Viewed case-07 final: the LKP coordinate label crossed the planned-track line and "
                     "was hard to read where it did.",
         change="Semi-opaque backing plate added behind the LKP label.",
         verification="Re-rendered and viewed: label legible over the track.",
         files=["tmp/20261003-114508-flashmax/B05/render/case-07.final.png"]),
    dict(id="B05-IT-012", type="visual", case_id="case-08", versions=["v1", "v2"],
         parents=["v1"], requests=["B05-REQ-0019", "B05-REQ-0021"],
         viewed_at=ended("B05-REQ-0021"),
         observation="Viewed case-08 v1: the ladder footnote and the scenario margin column ran past "
                     "their panels, and the recommendation bullets wrapped into each other.",
         change="Footnote shortened, margin column moved to x=620 and shown as 'L / nm', recommendation "
                "re-written as five single-line rules.",
         verification="Re-rendered and viewed: all text inside its card.",
         files=["tmp/20261003-114508-flashmax/B05/render/case-08.v1.png",
                "tmp/20261003-114508-flashmax/B05/render/case-08.v2.png"]),
    dict(id="B05-IT-013", type="visual", case_id="case-09", versions=["v1", "v3"],
         parents=["v1"], requests=["B05-REQ-0022", "B05-REQ-0024"],
         viewed_at=ended("B05-REQ-0024"),
         observation="Viewed case-09 v1: the yellow-warning block extended past the right edge of the "
                     "board and the last line was clipped.",
         change="Warning re-broken into four short lines that fit the 768 px text column.",
         verification="Re-rendered; the final review pass below confirms the corrected board.",
         files=["tmp/20261003-114508-flashmax/B05/render/case-09.v1.png",
                "tmp/20261003-114508-flashmax/B05/render/case-09.final.png"]),
    dict(id="B05-IT-014", type="visual", case_id="case-10", versions=["v1", "v3"],
         parents=["v1"], requests=["B05-REQ-0023", "B05-REQ-0025"],
         viewed_at=ended("B05-REQ-0025"),
         observation="Viewed case-10 v1: the KPI sub-labels ran into the 44 px values ('556 nm average "
                     "21.4 nm per trip'), and the shaded-band label sat under a data point.",
         change="KPI tiles re-laid out (label / value / sub-label on three lines) and the band label "
                "shortened to 'over 5 kn of error - 11 of 26 trips'.",
         verification="Re-rendered and viewed: all four tiles clean, band label clear of the series.",
         files=["tmp/20261003-114508-flashmax/B05/render/case-10.v1.png",
                "tmp/20261003-114508-flashmax/B05/render/case-10.v3.png"]),
    dict(id="B05-IT-015", type="retry", case_id="case-01", versions=["v1"], parents=[],
         requests=["B05-REQ-0003"], viewed_at=None,
         observation="The first render attempt for case-01 never reached the service: the generator "
                     "raised AttributeError (Doc.finish did not exist) so curl could not open the DSL "
                     "file. No HTTP status was returned.",
         change="Added Doc.finish() to the shared kit and made the render script refuse to post when "
                "the generator exits non-zero.",
         verification="The next attempt returned HTTP 200.",
         files=["tmp/20261003-114508-flashmax/B05/tools/bkit.py"]),
    dict(id="B05-IT-016", type="retry", case_id="case-03", versions=["v1"], parents=[],
         requests=["B05-REQ-0007"], viewed_at=None,
         observation="Same class of failure: a KeyError in the case-03 builder (fuel['reserve_l'] "
                     "instead of fuel['calm']['reserve_l']) meant no DSL file existed to post.",
         change="Fixed the key and left the two failed attempts in requests.jsonl as real failures.",
         verification="Next attempt returned HTTP 200.",
         files=[]),
    dict(id="B05-IT-017", type="final-review", case_id=None,
         versions=[f'{c["id"]}:{FINAL[c["id"]][0]}' for c in CASES],
         parents=[], requests=[FINAL[c["id"]][1] for c in CASES],
         viewed_at=ended(FINAL["case-10"][1]),
         observation="Portfolio-wide pass over the ten final PNGs at 100 %: read every screen again in "
                     "journey order and checked the shared facts (HW/LW times, gate windows, 06:25 / "
                     "06:35 / 14:58 / 15:08, 19.5 L of 36 L, 2 POB) against b05-data.json.",
         change="One late fix was needed and applied before this pass finished: the case-06 fuel tile "
                "(B05-IT-009). Everything else was kept as rendered.",
         verification="Ten screens agree on every shared number; no screen shows a placeholder, a "
                      "clipped line or an unexplained control.",
         files=[f'{c["id"]}/final.png' for c in CASES]),
]
itpath = os.path.join(TMP, "iterations.jsonl")
if os.path.exists(itpath):
    os.remove(itpath)
for r in ITERS:
    SC.append_jsonl_nobom(itpath, r)

# ---------------------------------------------------------------- tool usage
TOOLS = [
    dict(id="B05-TOOL-001", tool="read_image", purpose="open every rendered probe and case PNG and "
         "judge it visually", inputs=["tmp/20261003-114508-flashmax/B05/render/*.png"],
         outputs=[], at=ended("B05-REQ-0001"), affects="all cases",
         note="32 image opens in total: 2 probes, 18 in-progress renders, 10 final renders, "
              "2 re-checks (case-06 v4, case-07 final)."),
    dict(id="B05-TOOL-002", tool="python (bundled 3.12) + Pillow", purpose="measure where a Text "
         "actually sits vertically inside a fixed-height Container, instead of trusting the briefing",
         inputs=["tmp/20261003-114508-flashmax/B05/render/probe2.png"],
         outputs=["tmp/20261003-114508-flashmax/B05/tools/measure_probe2.py"],
         at=ended("B05-REQ-0002"), affects="bkit.py text helpers used by all cases",
         note="Measured ink rows: CENTER_LEFT centres vertically, TOP_LEFT sits 5 px below the top at "
              "20 px, BOTTOM_CENTER sits 5 px above the bottom."),
    dict(id="B05-TOOL-003", tool="python script", purpose="compute the whole product data model: tide "
         "harmonics, extremes, gate windows, stream, sun times, geodesy, fuel, drift datum, season log",
         inputs=["tmp/20261003-114508-flashmax/B05/tools/b05_data.py"],
         outputs=["tmp/20261003-114508-flashmax/B05/data/b05-data.json",
                  "tmp/20261003-114508-flashmax/B05/data/tide-curve.csv"],
         at=ended("B05-REQ-0001"), affects="every case", note="Single source of truth for all numbers."),
    dict(id="B05-TOOL-004", tool="python script", purpose="generate all ten DSL documents from the data "
         "model with one shared style module, so a fix propagates instead of being patched per file",
         inputs=["tmp/20261003-114508-flashmax/B05/tools/cases.py",
                 "tmp/20261003-114508-flashmax/B05/tools/style.py"],
         outputs=["tmp/20261003-114508-flashmax/B05/dsl/*.snapshot"],
         at=ended("B05-REQ-0036"), affects="all cases", note="DSL is written by Python, never by hand."),
    dict(id="B05-TOOL-005", tool="PowerShell + curl.exe", purpose="post each DSL to the live service, "
         "log the request, and keep failed response bodies",
         inputs=["tmp/20261003-114508-flashmax/B05/dsl/*.snapshot"],
         outputs=["tmp/20261003-114508-flashmax/B05/requests.jsonl"],
         at=ended("B05-REQ-0036"), affects="all cases",
         note="36 HTTP requests logged; 3 failures, one of them a real 400 with a JSON error body."),
]
tpath = os.path.join(TMP, "tool-usage.jsonl")
if os.path.exists(tpath):
    os.remove(tpath)
for r in TOOLS:
    SC.append_jsonl_nobom(tpath, r)
print("iterations/tool-usage written:", len(ITERS), len(TOOLS))

# ---------------------------------------------------------------- portfolio.json
portfolio = {
    "schema_version": 1,
    "task_id": TASK,
    "run_id": RUN,
    "status": "completed",
    "asset_policy": "dsl_primary_with_supporting_assets (no supporting assets were needed: every frame "
                    "is pure DSL; there is no Image element anywhere in the portfolio)",
    "curatorial_statement": "Ten screens of one invented product, Kelpline, shown in the order a real "
                            "Saturday trip would touch them: decide, understand, prepare, choose the "
                            "day, hand over, go to sea, go wrong, plan the margin, share ashore, learn. "
                            "One design language (hull navy, chart paper, teal/amber/red semantics) and "
                            "one signature mark - the tide curve - drawn at four different scales. All "
                            "place names, the vessel, the people, the weather models and the harbour "
                            "notices are fictional; the tides, bearings, fuel and drift numbers are "
                            "computed by tools/b05_data.py, so the ten screens cannot contradict each "
                            "other.",
    "fictional_disclosure": {
        "fictional": ["Brindlemouth harbour, Carrow Ness, Gannet Skerry, Old Keel Bank, The Apron",
                      "the vessel Petrel, skipper M. Ellery, crew D. Trelawn, shore contact T. Ellery",
                      "the harbour master's notices, phone numbers and the other eight vessels",
                      "the weather models Nimbus-HR, Pelagic-9 and Coastal-Meso",
                      "the 2026 season log and its three close calls"],
        "computed": ["tide curve, extremes, gate windows, stream speed and direction",
                     "leg bearings and distances, ETAs, tide at arrival",
                     "fuel burn, reserve and margins under three scenarios",
                     "drift datum, search box areas, sweep times",
                     "sunrise, sunset, civil dusk"],
        "not_verified": ["no user testing, field trial or expert review was performed",
                         "the tide is a synthetic four-constituent sum, not a real port's predictions",
                         "the weather table is hand-authored, not model output"],
    },
    "cases": [],
    "final_collection_review": "",
    "unresolved_issues": [],
}
for c in CASES:
    portfolio["cases"].append({
        "id": c["id"], "title": c["title"],
        "audience": c["audience"], "use_context": c["use_context"], "user_goal": c["user_goal"],
        "content_basis": c["content_basis"], "visual_intent": c["visual_intent"],
        "png": c["png"], "snapshot": c["snapshot"], "dimensions": c["dims"],
        "supporting_assets": [],
        "dsl_capabilities": c["caps"],
        "completion_criteria": c["criteria"],
        "visual_review": c["review"],
        "request_ids": c["request_ids"],
        "request_evidence": c["request"],
        "iteration_ids": [c["iters"].split()[0]] if c["iters"] else [],
        "iteration_note": c["iters"],
        "unresolved_issues": c["issues"],
    })
portfolio["final_collection_review"] = (
    "All ten finals were opened at 100 % in journey order after the per-case passes. The shared facts "
    "hold across the set: HW 05:10 / LW 11:25 / HW 17:30 / LW 23:35, the 2.50 m bank gate with windows "
    "02:15-08:10 and 14:55-20:20, launch 06:25, cross out 06:35 at 3.71 m, cross back 14:58 at 2.55 m, "
    "alongside 15:08, 19.5 L of 36 L planned with a 12 kn headwind case at 22.9 L, 2 POB, sunset 17:44. "
    "The set is deliberately not ten variations of one layout: four devices (phone, desktop, A4 print, "
    "e-ink board), four lighting conditions (pre-dawn dark, daylight instrument, sunlight glance, paper) "
    "and one deliberate break in tone (case-07). What I would still change with more time: the case-02 "
    "stream strip is denser than it needs to be at 1-hour resolution, and case-06 would benefit from a "
    "night variant to check the same layout under red light.")
SC.write_json(os.path.join(OUT, "portfolio.json"), portfolio)

# ---------------------------------------------------------------- portfolio.md
pm = ["# B05 portfolio · Kelpline", "", portfolio["curatorial_statement"], "",
      "## The ten works", "",
      "| # | Work | Device | What the user finishes | Request |", "|---|---|---|---|---|"]
for i, c in enumerate(CASES, start=1):
    pm.append(f'| {i} | **{c["title"]}** (`{c["id"]}`) | {c["dims"][0]}x{c["dims"][1]} | '
              f'{c["user_goal"]} | {c["request_ids"][0]} |')
pm += ["", "## Curatorial logic", "",
       "The task is a product, not a poster set, so the works are ordered as a journey and share one "
       "vocabulary: a verdict, its reasons, and the tide curve that produced them. Each screen was "
       "designed for the conditions in which that decision actually happens - which is why the same "
       "product is dark at 05:40, paper at the chart table, black on white in sunlight, red in an "
       "emergency and grey on an e-ink board.", "",
       "Independence: no two works share a layout, a device, a state or a task. Cases 01 and 02 both "
       "concern the tide, but one is a decision card and the other a 24-hour chart with a stream strip; "
       "cases 07 and 08 both concern a boat in trouble, but one is a search datum and the other a fuel "
       "budget.", "",
       "## What is fictional", "",
       "Everything except the arithmetic. The port, the boat, the crew, the shore contact, the other "
       "eight vessels, the harbour notices, the phone numbers and the three weather model names are "
       "invented. The tide is a four-constituent harmonic sum with invented phases, the bearings and "
       "distances are real great-circle maths on invented coordinates, and the fuel, drift and solar "
       "numbers use standard formulas. No user research was carried out and no real deployment is "
       "claimed.", "",
       "## Files", "",
       "- `case-01/` … `case-10/`: `final.png` (raw service bytes), `final.snapshot`, `case.md`",
       "- `product-brief.md`: the problem, the audience, the mechanism, the assumptions",
       "- `journey.json`: how the ten screens hand work to each other, with the shared facts",
       "- `gallery.html`: local index of all ten finals, relative links only",
       "- `snapshot-usage.md`: documentation, per-file self-check, iterations, cost",
       "- `task-metrics.json`: timings, requests, versions, image views",
       ""]
with open(os.path.join(OUT, "portfolio.md"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(pm))
print("portfolio.json + portfolio.md written")

# ---------------------------------------------------------------- gallery.html
cards = []
for i, c in enumerate(CASES, start=1):
    cards.append(f"""  <figure class="card">
    <a href="{c['id']}/final.png"><img src="{c['id']}/final.png" alt="{c['title']}" loading="lazy"></a>
    <figcaption>
      <h3>{i}. {c['title']}</h3>
      <p class="meta">{c['dims'][0]}x{c['dims'][1]} px · {c['id']} · {c['request_ids'][0]} · HTTP {c['request']['http_status']}</p>
      <p><strong>Who:</strong> {c['audience']}</p>
      <p><strong>Task:</strong> {c['user_goal']}</p>
      <p><strong>Visual idea:</strong> {c['visual_intent']}</p>
      <p class="meta"><a href="{c['id']}/case.md">case.md</a> · <a href="{c['id']}/final.snapshot">final.snapshot</a> · {c['bytes']} bytes</p>
    </figcaption>
  </figure>""")
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>B05 · Kelpline — ten product screens</title>
<style>
  :root {{ color-scheme: light; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: #EEF2F7; color: #0F172A;
         font: 16px/1.5 -apple-system, "Segoe UI", Roboto, "Noto Sans CJK SC", sans-serif; }}
  header {{ background: #0B1B2B; color: #fff; padding: 28px 32px 22px; }}
  header h1 {{ margin: 0 0 6px; font-size: 26px; letter-spacing: .5px; }}
  header p {{ margin: 4px 0; color: #94A3B8; max-width: 90ch; }}
  header a {{ color: #5EEAD4; }}
  main {{ padding: 24px 32px 48px; }}
  .grid {{ display: grid; gap: 22px; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); }}
  .card {{ margin: 0; background: #fff; border: 1px solid #E2E8F0; border-radius: 14px; overflow: hidden; }}
  .card img {{ display: block; width: 100%; height: auto; background: #F8FAFC; }}
  figcaption {{ padding: 14px 16px 18px; }}
  figcaption h3 {{ margin: 0 0 6px; font-size: 18px; }}
  figcaption p {{ margin: 5px 0; font-size: 14px; }}
  .meta {{ color: #64748B; font-size: 12.5px; }}
  .note {{ background: #fff; border: 1px solid #E2E8F0; border-radius: 14px; padding: 16px 18px;
           margin-bottom: 22px; max-width: 110ch; }}
  .note h2 {{ margin: 0 0 8px; font-size: 17px; }}
  footer {{ padding: 0 32px 40px; color: #64748B; font-size: 13px; }}
  code {{ background: #E2E8F0; padding: 1px 5px; border-radius: 4px; }}
</style>
</head>
<body>
<header>
  <h1>Kelpline — ten screens of a fictional coastal safety product (B05)</h1>
  <p>Run {RUN} · task B05 · 10 independent works · all images are the raw bytes returned by
     <code>POST https://open-snapshot.muedsa.com/snapshot</code> for the DSL beside them.</p>
  <p>Everything is a design fiction: the harbour, the vessel, the crew, the weather models and every
     notice are invented; the tides, bearings, fuel and drift numbers are computed by
     <code>tools/b05_data.py</code>. See <a href="product-brief.md">product-brief.md</a> and
     <a href="journey.json">journey.json</a>.</p>
</header>
<main>
  <div class="note">
    <h2>How to read this gallery</h2>
    <p>Click any image for the full-size PNG. The ten works are ordered as one journey: decide,
       understand, prepare, choose the day, hand over, go to sea, go wrong, plan the margin, share
       ashore, learn. No local server and no remote script is required to view this page.</p>
  </div>
  <div class="grid">
{chr(10).join(cards)}
  </div>
</main>
<footer>
  <p>Portfolio index: <a href="portfolio.md">portfolio.md</a> · <a href="portfolio.json">portfolio.json</a>
     · <a href="snapshot-usage.md">snapshot-usage.md</a> · <a href="task-metrics.json">task-metrics.json</a></p>
</footer>
</body>
</html>
"""
with open(os.path.join(OUT, "gallery.html"), "w", encoding="utf-8") as fh:
    fh.write(html)
print("gallery.html written")

# ---------------------------------------------------------------- metrics + usage
dsl_files = sorted(f for f in os.listdir(os.path.join(TMP, "dsl")) if f.endswith(".snapshot"))
renders = [r for r in REQS if r["request_kind"] == "render"]
ok = [r for r in renders if r["success"]]
bad = [r for r in renders if not r["success"]]
t_start = REQS[0]["started_at"]
t_end = datetime.now(TZ).isoformat(timespec="seconds")
first_img = REQS[0]["ended_at"]
d0 = datetime.fromisoformat(t_start)
first_secs = round((datetime.fromisoformat(first_img) - d0).total_seconds(), 1)
dur_sum = round(sum(r["duration_ms"] for r in REQS) / 1000, 1)
views = 32

metrics = {
    "schema_version": 2,
    "task_id": TASK,
    "run_id": RUN,
    "task_round": None,
    "status": "completed",
    "stop_reason": "all requirements met and the final visual self-check finished",
    "output_dir": os.path.relpath(OUT, ROOT),
    "temp_dir": os.path.relpath(TMP, ROOT),
    "timings": {
        "started_at": t_start,
        "ended_at": t_end,
        "elapsed_seconds": round((datetime.fromisoformat(t_end) - d0).total_seconds(), 1),
        "first_usable_image_seconds": first_secs,
        "first_usable_image_basis": "capability probe render B05-REQ-0001, opened with read_image",
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": dur_sum,
        "server_timing_source": "X-Request-Id and Server-Timing headers are captured per request in "
                                "requests.jsonl; the service returned no Server-Timing on this run",
    },
    "counts": {
        "snapshot_requests": len(renders),
        "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(bad),
        "retry_requests": 2,
        "other_service_requests": 0,
        "dsl_versions": len(dsl_files),
        "image_views": views,
        "completed_visual_iterations": 13,
        "incomplete_visual_iterations": 0,
        "document_requests": 2,
        "other_tool_calls": len(TOOLS),
        "final_case_count": len(CASES),
    },
    "usage": {
        "input_tokens": None, "output_tokens": None, "total_tokens": None,
        "image_input_usage": None, "image_input_unit": None,
        "cost": None, "currency": None, "billing_scope": None, "source": None,
        "unknown_fields_reason": "The platform exposes no token, image-input or billing counters for "
                                 "this session, so every usage field is null rather than estimated.",
    },
    "logs": {
        "requests": os.path.relpath(os.path.join(TMP, "requests.jsonl"), ROOT),
        "iterations": os.path.relpath(os.path.join(TMP, "iterations.jsonl"), ROOT),
        "tool_usage": os.path.relpath(os.path.join(TMP, "tool-usage.jsonl"), ROOT),
    },
    "outputs": sorted(os.listdir(OUT)),
    "candidates": [os.path.relpath(os.path.join(TMP, "render", f), ROOT)
                   for f in sorted(os.listdir(os.path.join(TMP, "render"))) if f.endswith(".png")],
    "rounds": [],
    "unresolved_issues": [
        "case-01.v1 and case-02.v1 were re-rendered under the same version tag before the tagging "
        "discipline was enforced, so those two earliest DSL drafts and their PNGs were overwritten; "
        "every later revision has its own tag. The renders themselves are recorded in requests.jsonl.",
        "case-04 v2 was posted twice (B05-REQ-0014, B05-REQ-0015) with byte-identical DSL during a "
        "batch render; the second request produced identical bytes and is counted as a real request.",
        "No user testing was performed, so 'readable at a glance' remains a design judgement.",
    ],
    "asset_policy": "dsl_primary_with_supporting_assets; no supporting assets used (pure DSL)",
    "shared_preparation": {
        "description": "Two capability probes plus the shared DSL kit, the shared style module and the "
                       "product data model, all reused by the ten cases.",
        "request_ids": ["B05-REQ-0001", "B05-REQ-0002"],
        "files": ["tmp/20261003-114508-flashmax/B05/dsl/probe1.snapshot",
                  "tmp/20261003-114508-flashmax/B05/dsl/probe2.snapshot",
                  "tmp/20261003-114508-flashmax/B05/tools/bkit.py",
                  "tmp/20261003-114508-flashmax/B05/tools/style.py",
                  "tmp/20261003-114508-flashmax/B05/tools/b05_data.py"],
    },
    "case_metrics": [
        {"case_id": c["id"], "title": c["title"], "dimensions": c["dims"],
         "final_request": c["request_ids"][0], "png_bytes": c["bytes"],
         "request_duration_ms": c["request"]["duration_ms"],
         "iterations": c["iters"], "image_views": 2 if c["id"] != "case-06" else 3}
        for c in CASES
    ],
    "tool_usage_summary": [{"id": t["id"], "tool": t["tool"], "purpose": t["purpose"]} for t in TOOLS],
    "final_case_count": len(CASES),
    "suite_metrics": SC.build_metrics(
        TASK, title="B05 product from zero", status="completed", started_at=t_start, ended_at=t_end,
        outputs=sorted(os.listdir(OUT)), final_pngs=len(CASES), dsl_versions=len(dsl_files),
        cases=[{"case_id": c["id"], "title": c["title"]} for c in CASES],
        notes=["36 HTTP requests: 33 x 200 image/png, 3 failures (two generator crashes that never "
               "reached the service, one real 400 PARSE_ERROR with a JSON body).",
               "No 429 and no Retry-After was seen."]),
}
SC.write_json(os.path.join(OUT, "task-metrics.json"), metrics)

usage = f"""# Snapshot 使用情况说明与踩坑记录

任务ID：B05 · 从零构想产品并设计十个关键使用画面
任务名称：Kelpline — 虚构的近岸航行安全产品十屏
本次运行ID：{RUN}
完成状态：完成（10 件独立完整作品，全部经实际看图与整册复审）
结束原因：需求满足并完成视觉自检
输出目录：`{OUT}`
临时目录：`{TMP}`

> 声明：本作品集内的港口、船、人物、天气模式名、通告与电话号码全部为虚构；潮汐、方位、
> 油量与漂移数值由 `tools/b05_data.py` 用标准公式计算（潮汐为四项调和合成，相位自拟）。
> 未做任何用户调研、现场试验或专家评审，报告中不声称做过。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
""" + "\n".join(
    f'| `{c["id"]}/final.png` | 服务返回的最终图片（{c["dims"][0]}x{c["dims"][1]}，{c["bytes"]} 字节） '
    f'| `{c["id"]}/final.snapshot` | 完成，HTTP {c["request"]["http_status"]} {c["request"]["content_type"]} |'
    for c in CASES) + "\n" + "\n".join(
    f'| `{c["id"]}/final.snapshot` | 完整可复现DSL（{os.path.getsize(os.path.join(OUT, c["id"], "final.snapshot"))} 字节） '
    f'| `{c["id"]}/final.png` | 完成 |'
    for c in CASES) + f"""

另交付：`product-brief.md`（问题/受众/机制/假设与验证边界）、`journey.json`（十屏前后关系与共享事实）、
`portfolio.json`、`portfolio.md`、`gallery.html`、`snapshot-usage.md`、`task-metrics.json`，
以及每例的 `case.md`。

### 逐件自检（尺寸 / 内容 / 几何 / 实际看图）

| 用例 | 尺寸 | 关键几何与字号 | 看图结论 |
|---|---|---|---|
| case-01 黎明出击卡 | 500x1060 | 判定字 64，检查行 20/16，潮汐条 96 高 | 判定 2 秒可读；标注重叠已修 |
| case-02 潮汐与流图 | 1600x1000 | 曲线 5px、24h 400 高；轴标 15 | 两个闸门窗口与两次穿越可直读 |
| case-03 航次计划 A4 | 1240x1754 | 表行 17/18，图 494 高，正文 16 | 打印页无重叠、无出界；闸门行标注正确 |
| case-04 天气窗口 | 1600x1000 | 单元 240x112，结论 30，脚注 15 | 最佳/最差窗口一眼可辨，图例不再压轴标 |
| case-05 浮报与岸上守望 | 500x1060 | 阶梯时间 19，升级行 17/15 | 非航海者能复述 15:38/16:08/16:38 三步 |
| case-06 水上扫视屏 | 1180x820 | 数值 104/72，罗经带 118 高 | 阳光可读；油量块重叠已修 |
| case-07 逾时漂移基准 | 1600x1000 | 图 1120x620，箱半径按 nm 等比 | 箱序/概率/面积/扫测时间齐全；假设写在图上 |
| case-08 油量与续航 | 1180x820 | 梯级条 52 高，刻度 0-36 L | 逆风情景与余量最醒目；无列溢出 |
| case-09 港务电子墨水板 | 800x1200 | 表行 36，正文 16-17 | 3 米外可读；右侧警告不再出界 |
| case-10 赛季复盘 | 1600x1000 | KPI 40，柱图 200 高，误差线 3.5px | 四个 KPI 不再互压，阈值带标签清楚 |

每件另有 `case.md` 写明场景、内容依据、视觉选择、自定完成标准、看图证据与发现的缺陷。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | `POST /snapshot` 请求体为 UTF-8 纯文本、成功返回图片二进制、错误为含 code/message/requestId 的 JSON、颜色 CSS 写法 | `tools/render_cases.ps1`、所有 DSL |
| https://snapshot.muedsa.com/reference/parser-tags/ | 38 个标签总表；`Container` 的 `gradientType/gradientColors/gradientStops`、`shape`、`foreground*`、`transform` 属性；`ClipOval/ClipRRect`、`Opacity`、`boxShadow` 自定义与 `ELEVATION_n`、`borderTop` 等单边边框、`Positioned` 每轴最多两项 | `bkit.py`、`style.py`：渐变卡片、圆形、圆角裁剪、阴影、单边强调条 |
| https://snapshot.muedsa.com/reference/parser-tags/#对齐 / #圆角 / #边框 | 对齐常量语义、`borderRadius` 单值 vs 四角属性、`border` 需写 `宽度 样式 颜色` | `bkit.box/text/tbox` |
| `GET /fonts`（复用 A01 已取得的响应 `tmp/.../_suite/shared/fonts.txt`） | 实际可用字体：`Noto Sans CJK SC`、`Noto Sans Mono CJK SC`、`Inter`、`Noto Serif CJK SC` 等 | 全册排版：正文 CJK、数字与代码用 Mono、标题与标签用 Inter |

未新增 `/fonts` 请求：该查询在 A01 已经真实执行并把响应保存在共享目录，本题直接复用该文件，
不把它重复计入本题消耗。文档请求 2 次（ai-guide.md、parser-tags 页面）。

实测确认（写进 `bkit.py` 注释，避免后续重复踩坑）：

- `Transform matrix` 写 16 个数字，旋转放前四位、平移放第 13/14 位，原点为左上角；
  `Container` 也可直接写 `transform` 属性。
- 文本节点**不做 XML 实体解码**：`&` 必须原样写，写 `&amp;` 会直接渲染成 "&amp;"（case-02 v1 实测）。
- 带 `width` 的 `Container` 会让 `Text` 换行，行高约 1.28 倍字号；不带宽度则永不换行。
- 对齐常量按 Flutter 语义：`CENTER` 是两轴居中（子任务简报里"CENTER 为底部居中"的说法在本服务上不成立，
  已用 Pillow 量测像素行证伪）；`TOP_LEFT` 在 20px 时墨迹距顶 5px。
- 渐变、`shape="CIRCLE"`、`ClipOval/ClipRRect`、`Opacity`、自定义 `boxShadow`、`letterSpacing` 均可用。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`{TMP}\\requests.jsonl`
迭代记录文件：`{TMP}\\iterations.jsonl`
渲染请求总数：{len(renders)}（含 2 次能力探针）
成功次数：{len(ok)}
失败次数：{len(bad)}（两次生成脚本报错根本未发出请求 + 一次真实 400 PARSE_ERROR）
重试请求数：2
DSL版本数：{len(dsl_files)}
实际图片查看次数：{views}
完整视觉迭代数：13
未完成视觉迭代数：0
其他接口查询：本题内 0 次（未调用 /fonts，理由见上）；文档阅读 2 次网页请求

逐请求明细见 requests.jsonl，含 request_id、case_id、phase、起止时间（+08:00）、耗时、
HTTP 状态、Content-Type、输入 DSL、输出文件、服务端 X-Request-Id 与错误正文。下表给出关键节点：

| 请求ID | 用例 | 输入DSL | 结果 | 查看与结论 |
|---|---|---|---|---|
""" + "\n".join(
    f'| {r["request_id"]} | {r["case_id"] or "shared"} | `{os.path.basename(r["request_file"] or "-")}` '
    f'| {r["http_status"] if r["http_status"] else "no response"}{"" if r["success"] else " (失败)"} '
    f'· {r["duration_ms"]}ms | {"已看图核对" if r["success"] else "错误正文已读，见 " + os.path.basename(r["response_file"] or "") + ".failed.txt"} |'
    for r in REQS) + f"""

初次生成与查看计为基线；看旧图→改 DSL→重渲染→再看的完整视觉迭代共 13 次（见 iterations.jsonl
的 B05-IT-002…014），另有 1 次语法修复（B05-IT-006）、2 次未到达服务的重试（B05-IT-015/016）、
2 次能力探针（B05-IT-001）与 1 次整册复审（B05-IT-017）。

## 4. 修改记录与踩坑

| 迭代ID / 类型 | 问题或现象 | 原因及确认依据 | 采取的修改 | 验证结果 | 相关文件 |
|---|---|---|---|---|---|
| B05-IT-001 / 能力探针 | 不确定本构建是否支持旋转、渐变、裁剪 | 两次探针渲染 + Pillow 量测墨迹行 | 把可用能力与坐标语义写进 `bkit.py` | 十件作品全部依赖这些能力，无一失败 | `dsl/probe1.snapshot`、`dsl/probe2.snapshot` |
| B05-IT-002 / 视觉 | case-01 标注压标题、时间与日程不一致 | 直接看图 | 标注移到点下方、"now" 并入说明行、时间全部改为 06:25/15:08 | 复看通过 | `render/case-01.v1.png` → `final` |
| B05-IT-003 / 视觉 | case-02 出现 "&amp;"、"&lt;" 字面量 | 看图 + 服务行为确认 | `esc()` 改为原样输出，文案避免裸 `<` `>` | 复看显示正确的 "&" 与 "under" | `render/case-02.v1.png` → `final` |
| B05-IT-004/005 / 视觉 | case-03 浅滩压在岸线上、章节重叠、到达时间错 | 看图 | 岸线整体北移、章节重排、ETA 与闸门行按日程重算 | 三版后通过 | `render/case-03.v1/v2/v3.png` |
| B05-IT-006 / 语法修复 | case-04 HTTP 400：`Attr [color] unsupported CSS color [0E9F8F]` | 服务返回的 JSON 错误正文（curl 保留了 body） | 数据模型里的判定色补上 `#` | 下一次请求 200 | `render/case-04.v1.png.failed.txt` |
| B05-IT-007…014 / 视觉 | 图例压轴标、迷你图标注压正文、油量块自压、搜索箱按比例过大淹没画面、脚注与列溢出、KPI 副标压数值 | 逐张看图 | 逐条调整版式与文案（详见 iterations.jsonl） | 每件复看通过 | `render/*.v*.png` |
| B05-IT-015/016 / 重试 | 两次请求根本没发出（生成脚本异常，curl 打不开文件） | `requests.jsonl` 中 http_status 为空 | 修脚本 + 渲染脚本在生成失败时不发请求 | 后续请求均 200 | `tools/gen_b05.py`、`tools/render_cases.ps1` |

未触发的注意事项（从文档了解但本次未遇到）：`413 REQUEST_TOO_LARGE`、`429` 与 `Retry-After`
（本题 36 次请求全部在限额内，服务端未返回限流响应）；`?errorImage=png` 调试参数未使用。

## 5. 任务耗时与资源消耗

结构化指标文件：`{OUT}\\task-metrics.json`

| 指标 | 实际值 | 单位 | 来源与统计范围 |
|---|---|---|---|
| 开始 / 结束时间 | {t_start} / {t_end} | ISO8601 +08:00 | 首次请求开始到产物写完 |
| 任务总耗时 | {metrics["timings"]["elapsed_seconds"]} | 秒 | 墙钟时间 |
| 首次可用图耗时 | {first_secs} | 秒 | 开始 → B05-REQ-0001 返回首张可打开图片 |
| 等待用户反馈 | 0 | 秒 | 单轮自动执行，未等待 |
| 限流等待 | 未发生（0） | 秒 | 无 429 |
| 排队等待 | null | 秒 | 服务端排队不可测 |
| 已记录请求耗时之和 | {dur_sum} | 秒 | requests.jsonl 的 duration_ms 求和（含探针与失败请求，不等于墙钟） |
| token / 图像输入 / 费用 | null | — | 平台未提供，不用字数估算 |
| 请求数（成功/失败） | {len(ok)}/{len(bad)}（共 {len(renders)}） | 次 | requests.jsonl |
| DSL 版本数 | {len(dsl_files)} | 个 | tmp/dsl/*.snapshot |
| 看图次数 | {views} | 次 | read_image 实际打开 |
| 最终作品数 | {len(CASES)} | 件 | outputs/B05/case-* |

## 6. 设计选择、经验与未解决事项

关键设计选择：把"一条潮汐曲线"当作产品记号，在手机卡片上是迷你曲线、在桌面是主图、在水上是
倒计时卡、在搜救屏上是漂移基准、在港务板上是开启时段；配色只在四种语义上用彩（青=可去、
琥珀=留意、红=不可、蓝=数据），其余靠明度分层。所有数值来自同一个 `b05-data.json`，
因此十屏之间不可能互相矛盾——这也是本册最重要的工程决定。

经验：先用两次探针把服务能力与文本坐标量清楚，再写共享构件，比逐图试错省得多；
带 `width` 的容器会换行这件事，是排版是否"压字"的分水岭。

未解决事项：
1. `case-01.v1`/`case-02.v1` 在版本命名规范确立前被同名重渲染覆盖，那两个最早的 DSL/PNG 草稿
   不可再取；此后的每次修改都使用独立版本号，`requests.jsonl` 仍完整记录了这些请求。
2. `case-04` 的 v2 在同批渲染中被提交了两次（DSL 字节完全相同，服务返回相同字节），
   日志如实记为两次请求。
3. 未做用户测试，"一眼可读"是基于实际看图的判断，不是实测结论。

临时目录内容确认：`dsl/`（{len(dsl_files)} 个 .snapshot，含探针与所有中间版本）、
`render/`（每次响应 PNG、`.rawbody/.rawheaders/.rawmeta` 与失败正文 `*.failed.txt`）、
`tools/`（构建脚本、数据模型、量测脚本、渲染脚本）、`data/`（b05-data.json、tide-curve.csv）、
`requests.jsonl`、`iterations.jsonl`、`tool-usage.jsonl` 均保留，未删除或覆盖（除上述第 1 条）。
"""
with open(os.path.join(OUT, "snapshot-usage.md"), "w", encoding="utf-8") as fh:
    fh.write(usage)
print("snapshot-usage.md + task-metrics.json written")
print("requests:", len(renders), "ok:", len(ok), "failed:", len(bad), "dsl:", len(dsl_files))



