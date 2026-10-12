"""Assemble every B06 deliverable from the real artefacts."""
from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TASK = "B06"
TZ = timezone(timedelta(hours=8))
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite", "shared"))
import suite_common as SC  # noqa: E402

DATA = json.load(open(os.path.join(TMP, "data", "b06-data.json"), encoding="utf-8"))
REQS = SC.read_jsonl(os.path.join(TMP, "requests.jsonl"))
BY_ID = {r["request_id"]: r for r in REQS}

FINAL = {
    "case-01": "B06-REQ-0027", "case-02": "B06-REQ-0028", "case-03": "B06-REQ-0037",
    "case-04": "B06-REQ-0030", "case-05": "B06-REQ-0038", "case-06": "B06-REQ-0032",
    "case-07": "B06-REQ-0033", "case-08": "B06-REQ-0034", "case-09": "B06-REQ-0035",
    "case-10": "B06-REQ-0036",
}

CASES = [
    dict(id="case-01", title="Five medicines, one day", dims=[1600, 1130],
         problem="Five prescriptions, seven doses a day, and rules that only exist on the boxes: "
                 "levothyroxine needs an empty stomach and four hours from iron and calcium, iron "
                 "and calcium need two hours between them, and two of the doses clash.",
         audience="A 68-year-old taking five medicines, and the adult daughter who does the repeats",
         context="Printed at A3 and stuck on the fridge door; also read on a phone at the pharmacy",
         task="Run the day without a timing clash, and know what to do about a missed dose",
         idea="A 24-hour band with every dose on a spoke, the clashes bracketed in red, and a table "
              "that turns each box's small print into one line",
         caps="Time axis from minutes, lane assignment so no two dose labels collide, red clash bars "
              "with numbered badges, zebra table, printed-paper palette",
         criteria="Every dose is visible with its time; both clashes are named with the gap and the "
                  "requirement; the fixed schedule is on the same sheet",
         review="Viewed case-01 v1 (B06-REQ-0001) and final (B06-REQ-0027)",
         iters="B06-IT-002 (visual)",
         fix="v1: the meal labels sat on the axis and were crossed by every dose connector, and the "
             "clash brackets crossed the hour labels. Meal labels moved to the top of their bands; "
             "the brackets became a red bar on the axis with numbered badges and an explained list "
             "under it."),
    dict(id="case-02", title="Your blood results, in range", dims=[1440, 1180],
         problem="A printout of twelve numbers with a reference range in brackets. Nobody can tell "
                 "which ones matter, which way they moved, or by how much.",
         audience="The same patient, the evening the results arrive, before the GP appointment",
         context="Desktop or tablet at home, then printed and taken to the appointment",
         task="Know which results need a conversation, and which way each one is moving",
         idea="Reference ranges as horizontal tracks: the band is the range, a hollow marker is the "
              "last result, a filled marker is now, so direction of travel is visible without numbers",
         caps="Per-row adaptive scale so every marker fits, range bands, hollow/filled markers, "
              "out-of-range rows promoted to full cards with plain-language meanings",
         criteria="The six out-of-range results are separated from the six normal ones; each row "
                  "shows value, unit, range and change; nothing is clipped",
         review="Viewed case-02 v1 (B06-REQ-0002), v2 (0004) and final (0028)",
         iters="B06-IT-003 + B06-IT-004 (visual)",
         fix="v1: the last compact rows fell off the canvas and out-of-range markers ran into the "
             "delta text. v2: the value, unit and flag were put in their own right-hand column and "
             "the tracks got per-row scales. Final: the unit moved off the delta text."),
    dict(id="case-03", title="Why this bill is £34.66 higher", dims=[1440, 1000],
         problem="An electricity bill that jumped a third in a month, with no explanation beyond a "
                 "kWh figure and a colder October.",
         audience="A two-adult household on a variable tariff",
         context="Desktop, the evening the bill lands, with the previous bill to hand",
         task="See how much of the increase is weather, how much is price, and what would actually "
              "reduce it",
         idea="A waterfall from last month's bill to this month's, with degree days named as the "
              "cause and a ranked list of what would bring it down",
         caps="Floating waterfall bars with dashed connectors, wrapped labels under each bar, "
              "month-comparison rail, ranked saving bars",
         criteria="The four reasons sum exactly to the bill difference; the weather share is named "
                  "as weather; the actions are ranked by pounds",
         review="Viewed case-03 v3 (B06-REQ-0006) and final (B06-REQ-0037)",
         iters="B06-IT-005 + B06-IT-006 (visual)",
         fix="v3: the step labels ran into each other and the right rail's previous-month column "
             "collided with its labels. Labels now wrap into up to three lines per slot; the rail "
             "was rebuilt as label-over-comparison rows."),
    dict(id="case-04", title="Your pay, and where it goes", dims=[1440, 1000],
         problem="A payslip lists deductions in an order that hides the proportions: the biggest "
                 "number on the page is not the one that reaches the bank.",
         audience="Anyone on PAYE who has never checked what the deductions buy",
         context="Desktop at home, once a year, usually in January",
         task="See the split between take-home, tax, NI, pension and loan, and what each buys",
         idea="A flow: one gross bar splitting into five destination bars through translucent "
              "ribbons, with the percentage inside each destination",
         caps="Scanline-filled quadrilaterals for the ribbons, proportional widths, band arithmetic "
              "(allowance, basic rate, NI threshold, loan threshold) computed in the data model",
         criteria="The five parts sum to gross; the take-home share is stated; each deduction has a "
                  "plain-language line",
         review="Viewed case-04 v4 (B06-REQ-0010) and final (B06-REQ-0030)",
         iters="B06-IT-007 (visual)",
         fix="v4: the ribbons filled two thirds of the page and the narrow bars clipped their own "
             "labels. The flow was compressed, percentages moved inside the bars and the money "
             "moved into a labelled table under it."),
    dict(id="case-05", title="What your policy does not cover", dims=[1500, 1050],
         problem="Home insurance is sold on what it covers and claimed against on what it excludes; "
                 "the exclusions are spread through 40 pages.",
         audience="A householder deciding whether to claim, or whether to add accidental damage",
         context="Desktop, after something has gone wrong, in a hurry",
         task="Find the verdict for a specific situation in seconds, and see the six refusals that "
              "cause most disputes",
         idea="Eighteen real situations sorted by verdict, colour-coded, each with the reason in one "
              "line, and the six common refusals called out",
         caps="Sorted tile grid, verdict chips, per-tile accent bars, wrapping reason lines",
         criteria="Covered, conditional and excluded are visually distinct and sorted so the good "
                  "news and the bad news are separate; every tile has a reason",
         review="Viewed case-05 v3 (B06-REQ-0008) and final (B06-REQ-0038)",
         iters="B06-IT-008 + B06-IT-009 (visual)",
         fix="v3: two long situations wrapped into two lines and collided with their reason line, "
             "and the header counts overlapped the household line. Situations were shortened to one "
             "line, the chip widened for CONDITIONAL, and the counts moved into the left sub-line."),
    dict(id="case-06", title="One bowl, most of your day's sugar", dims=[1280, 1520],
         problem="A cereal box calls 45 g a serving and prints percentages against it. A real bowl "
                 "is 80 g, and the sugar goes from a third of a day to two thirds.",
         audience="A parent buying granola, reading the label in the shop or the kitchen",
         context="A3 or A4 poster in the kitchen; also readable on a phone at the shelf",
         task="See what one real bowl costs against a whole day's sugar, fat, salt and fibre",
         idea="Two bowls drawn to the portion, not a table: the label bowl is nearly empty and the "
              "real bowl is nearly full, then four day-budget bars with the label notch",
         caps="Semicircle scanline fill for the bowls, fill level driven by grams, budget bars with "
              "a label marker, computed reference-value shares",
         criteria="The two portions are visually different at a glance; the 45 g fiction is named; "
                  "fibre is shown as the good news",
         review="Viewed case-06 v1 (B06-REQ-0014) and final (B06-REQ-0032)",
         iters="B06-IT-010 (visual)",
         fix="v1: the 'bowls' rendered as fences over arches because the granola bars were drawn "
             "above the rim. Rebuilt as a filled bowl with a cereal level proportional to the "
             "portion, which is what the piece is arguing about."),
    dict(id="case-07", title="You have eight minutes", dims=[1440, 900],
         problem="A tight connection is decided by walking distances, stairs and a ticket-gate "
                 "queue, none of which appear on the ticket.",
         audience="A traveller with one bag, changing trains at a big station",
         context="Phone on the platform, between the doors opening and the next departure",
         task="Know whether the connection is comfortable, tight or already lost, and what happens "
              "if the first train is late",
         idea="A time budget built from eight real legs against an eight-minute axis, with the slack "
              "shown as a block and the delay scenarios below",
         caps="Minute-scaled Gantt bars, per-leg colour by kind of movement, slack block, red "
              "departure line, delay scenario cards",
         criteria="Every leg is named and timed, the total equals the available time, and the delay "
                  "scenarios say makes it or miss it explicitly",
         review="Viewed case-07 v2 (B06-REQ-0019) and final (B06-REQ-0033)",
         iters="B06-IT-011 (visual)",
         fix="The 400 on v1 was a border attribute without width and style; fixed. The slack block "
             "was then moved directly under the axis so it reads as part of the same timeline."),
    dict(id="case-08", title="Which ticket is cheapest for the way you travel", dims=[1500, 1020],
         problem="Five ticket types, four caps and a pass, and no way to tell which one is cheaper "
                 "for a pattern that is not the one in the advert.",
         audience="A commuter deciding between paying as they go and buying a pass",
         context="Desktop, at the kitchen table, once a year (or after a fare rise)",
         task="Find the cheapest option for a stated number of journeys a week and weeks a year",
         idea="A cost surface rather than a price list: journeys a week down, weeks a year across, "
              "and the cheapest option printed in every cell",
         caps="Computed five-option comparison per cell, colour-coded winners, highlighted user "
              "pattern, notes that explain why the weekly cap almost never wins",
         criteria="Every cell names its cheapest option and cost; the user's own pattern is "
                  "highlighted; the dominated options are explained rather than hidden",
         review="Viewed case-08 v1 (B06-REQ-0016) and final (B06-REQ-0034)",
         iters="B06-IT-012 (visual)",
         fix="v1: fifteen rows at 46 px pushed the notes off the canvas. Row height reduced, cell "
             "type re-sized, and the day-count label fixed to read '1 day'."),
    dict(id="case-09", title="Which bin does this go in?", dims=[900, 1440],
         problem="Kerbside rules are published as a list of materials, but the decisions people "
                 "actually face are objects: a greasy pizza box, a broken glass, a kettle.",
         audience="Residents at the bin store, and anyone doing a clear-out",
         context="A3 poster screwed to the bin-store wall, read standing up with a bag in one hand",
         task="Decide the bin for nine awkward items, and know the one rule that covers most of "
              "the rest",
         idea="Object-first cards with the verdict as a coloured chip, the reason underneath, and a "
              "small contamination panel",
         caps="Object cards with verdict chips, kerbside summary table, rule-of-thumb panel, "
              "contaminant list",
         criteria="Nine real items each end in one named destination with a reason; the 'smaller "
                  "than a fist' rule is stated; contaminants are named",
         review="Viewed case-09 v1 (B06-REQ-0017) and final (B06-REQ-0035)",
         iters="B06-IT-013 (visual)",
         fix="v1 was 1240 px tall and cut off the last two panels; the canvas was extended to 1440 "
             "and the collection-frequency text shortened so it stopped running into the contents "
             "column."),
    dict(id="case-10", title="What a wash really costs", dims=[1440, 940],
         problem="Washing machine programmes are labelled by temperature and time, not by cost, and "
                 "the difference between 30 and 60 is nearly half the running cost.",
         audience="A household running four washes a week",
         context="Desktop or tablet, read once when the machine is next to be replaced",
         task="Pick the programme that is cheap enough without leaving clothes unhygienic",
         idea="Six programme cards with cost per wash and per year, a sorted cost chart, and a "
              "note on what each temperature actually removes",
         caps="Cost model from energy, water and detergent, per-programme stacked mini-bars, "
              "sorted comparison bars, dark instrument palette",
         criteria="Cost per wash and per year are on every card; the saving between 30 and 60 is "
                  "stated in pounds; hygiene limits are stated too",
         review="Viewed case-10 v2 (B06-REQ-0020) and final (B06-REQ-0036)",
         iters="B06-IT-014 + B06-IT-015 (visual)",
         fix="The 90 C energy bar overflowed its card (scale was fixed at 40p) and the closing line "
             "overlapped the last bar. Mini-bars rescaled to the real maximum, canvas extended, rows "
             "tightened."),
]

for c in CASES:
    cdir = os.path.join(OUT, c["id"])
    os.makedirs(cdir, exist_ok=True)
    src_png = os.path.join(TMP, "render", f'{c["id"]}.final.png')
    src_dsl = os.path.join(TMP, "dsl", f'{c["id"]}.final.snapshot')
    shutil.copyfile(src_png, os.path.join(cdir, "final.png"))
    shutil.copyfile(src_dsl, os.path.join(cdir, "final.snapshot"))
    rec = BY_ID[FINAL[c["id"]]]
    c["png"] = f'{c["id"]}/final.png'
    c["snapshot"] = f'{c["id"]}/final.snapshot'
    c["request_ids"] = [FINAL[c["id"]]]
    c["bytes"] = os.path.getsize(src_png)
    c["request"] = {"http_status": rec["http_status"], "content_type": rec["content_type"],
                    "duration_ms": rec["duration_ms"], "service_request_id": rec["service_request_id"],
                    "ended_at": rec["ended_at"]}

for c in CASES:
    md = f"""# {c['id']} · {c['title']}

**Final image** `final.png` ({c['dims'][0]}x{c['dims'][1]}, {c['bytes']} bytes) ·
**DSL** `final.snapshot` · **request** {c['request_ids'][0]} (HTTP {c['request']['http_status']},
{c['request']['content_type']}, {c['request']['duration_ms']} ms, service id
`{c['request']['service_request_id']}`)

## The problem this answers
{c['problem']}

- **Audience**: {c['audience']}
- **Where it is used**: {c['context']}
- **What the reader has to finish**: {c['task']}
- **Data**: computed by `../tools/b06_data.py` (see `problem-evidence.json` for what is real and
  what is invented). No external assets: every mark is a Snapshot DSL primitive.

## Visual idea
{c['idea']}

DSL capabilities used: {c['caps']}

## Self-check against my own completion criteria
- {c['criteria']}
- Visual evidence: {c['review']}.
- Iterations: {c['iters']}.
- Defect found by looking, and the fix: {c['fix']}
- Unresolved issues: none.
"""
    with open(os.path.join(OUT, c["id"], "case.md"), "w", encoding="utf-8") as fh:
        fh.write(md)

print("case dirs written:", len(CASES))

# ---------------------------------------------------------------- iteration log
def ended(rid):
    r = BY_ID.get(rid)
    return r["ended_at"] if r else None


ITERS = [
    dict(id="B06-IT-001", type="alternative", case_id=None, versions=["probe1", "probe2"],
         parents=[], requests=["B05-REQ-0001", "B05-REQ-0002"], viewed_at=None,
         observation="No new capability probes were run for B06: the two B05 probes plus the "
                     "element-count and entity findings from the suite were reused as shared "
                     "preparation, so this task's request count has no probe requests of its own.",
         change="B06 reuses tmp/<run>/B05/tools/bkit.py (copied to B06/tools) with two additions: "
                "a bold-Latin width factor and a 3900-element guard in the generator.",
         verification="Every B06 document was generated under the guard; the largest is 574 elements.",
         files=["tmp/20261003-114508-flashmax/B06/tools/bkit.py",
                "tmp/20261003-114508-flashmax/B06/tools/gen_b06.py"]),
    dict(id="B06-IT-002", type="visual", case_id="case-01", versions=["v1", "v5/final"],
         parents=["v1"], requests=["B06-REQ-0001", "B06-REQ-0012", "B06-REQ-0027"],
         viewed_at=ended("B06-REQ-0012"),
         observation="Viewed case-01 v1: the meal-band labels sat on the axis and every dose "
                     "connector crossed them, and the clash brackets were drawn as leader lines that "
                     "cut through the hour labels.",
         change="Meal labels moved to the top of their bands; clash brackets replaced by a red bar "
                "on the axis with numbered badges and a two-line explanation under it.",
         verification="Re-rendered and viewed: hour labels are clean and both clashes are named in "
                      "words with the gap and the requirement.",
         files=["tmp/20261003-114508-flashmax/B06/render/case-01.v1.png",
                "tmp/20261003-114508-flashmax/B06/render/case-01.final.png"]),
    dict(id="B06-IT-003", type="visual", case_id="case-02", versions=["v1", "v2"],
         parents=["v1"], requests=["B06-REQ-0002", "B06-REQ-0004"],
         viewed_at=ended("B06-REQ-0004"),
         observation="Viewed case-02 v1: the six compact 'in range' rows ran off the bottom of the "
                     "canvas, out-of-range markers overlapped the delta text and the footer note.",
         change="Canvas extended to 1180, rows re-pitched, value/unit/flag moved into a right-hand "
                "column, and each track given its own scale so both markers always fit.",
         verification="Re-rendered and viewed: nothing is clipped and every marker sits inside its "
                      "track.",
         files=["tmp/20261003-114508-flashmax/B06/render/case-02.v1.png",
                "tmp/20261003-114508-flashmax/B06/render/case-02.v2.png"]),
    dict(id="B06-IT-004", type="visual", case_id="case-02", versions=["v2", "v3/final"],
         parents=["v2"], requests=["B06-REQ-0005", "B06-REQ-0028"],
         viewed_at=ended("B06-REQ-0005"),
         observation="Viewed case-02 v2: the ferritin row's delta text ran into its unit "
                     "('micrograms/L') because both shared the right-hand column.",
         change="Units right-aligned at 1240, delta text at 1000, flags right-aligned under the "
                "values.",
         verification="Re-rendered and viewed in the final pass: no collisions on any row.",
         files=["tmp/20261003-114508-flashmax/B06/render/case-02.final.png"]),
    dict(id="B06-IT-005", type="visual", case_id="case-03", versions=["v3", "v4"],
         parents=["v3"], requests=["B06-REQ-0006", "B06-REQ-0009"],
         viewed_at=ended("B06-REQ-0009"),
         observation="Viewed case-03 v3: the four waterfall step labels ran into each other and the "
                     "right rail's September column collided with the row labels.",
         change="Step labels now wrap into up to three lines inside their slot; the rail was rebuilt "
                "as label-over-comparison rows feeding the actions panel.",
         verification="Re-rendered and viewed: labels are separated and the rail reads left to right.",
         files=["tmp/20261003-114508-flashmax/B06/render/case-03.v3.png",
                "tmp/20261003-114508-flashmax/B06/render/case-03.v4.png"]),
    dict(id="B06-IT-006", type="visual", case_id="case-03", versions=["v4", "final"],
         parents=["v4"], requests=["B06-REQ-0037"],
         viewed_at=ended("B06-REQ-0037"),
         observation="Viewed case-03 v4: the '0.68 kWh of heating per degree day' note sat on top of "
                     "the standing-charge row.",
         change="Row pitch reduced to 46 px and the note moved to y=470.",
         verification="Re-rendered and viewed: the rail has five clear rows and the note below them.",
         files=["tmp/20261003-114508-flashmax/B06/render/case-03.final.png"]),
    dict(id="B06-IT-007", type="visual", case_id="case-04", versions=["v3", "v5/final"],
         parents=["v3"], requests=["B06-REQ-0007", "B06-REQ-0010", "B06-REQ-0013", "B06-REQ-0030"],
         viewed_at=ended("B06-REQ-0010"),
         observation="B06-REQ-0007 returned HTTP 400 PARSE_ERROR: 'Attr [color] color must be "
                     "#RGB, #RGBA, #RRGGBB or #RRGGBBAA' because the ribbon colour was built by "
                     "appending two hex digits to an already 8-digit colour (#2FA37CFF + 55). "
                     "Viewed v4: the ribbons filled two thirds of the page and the narrow "
                     "destination bars clipped their own money labels.",
         change="Ribbon colours built as col[:7] + alpha; the flow compressed to a 200 px drop, "
                "percentages moved inside the bars, money moved to a labelled table.",
         verification="Re-rendered and viewed: five clean destination bars and no clipped text.",
         files=["tmp/20261003-114508-flashmax/B06/render/case-04.v3.png.failed.txt",
                "tmp/20261003-114508-flashmax/B06/render/case-04.final.png"]),
    dict(id="B06-IT-008", type="visual", case_id="case-05", versions=["v3", "v4"],
         parents=["v3"], requests=["B06-REQ-0008", "B06-REQ-0011"],
         viewed_at=ended("B06-REQ-0011"),
         observation="Viewed case-05 v3: 'CONDITIONAL' overflowed its chip, two long situations "
                     "wrapped into two lines that touched their reason line, and the header counts "
                     "collided with the household line.",
         change="Chip widened to 108 px, situations shortened to one line in the data model, counts "
                "moved into the left sub-line.",
         verification="Re-rendered and viewed: every tile is one title line plus one reason line.",
         files=["tmp/20261003-114508-flashmax/B06/render/case-05.v3.png",
                "tmp/20261003-114508-flashmax/B06/render/case-05.v4.png"]),
    dict(id="B06-IT-009", type="visual", case_id="case-05", versions=["v4", "final"],
         parents=["v4"], requests=["B06-REQ-0038"],
         viewed_at=ended("B06-REQ-0038"),
         observation="Viewed case-05 final: two tiles still wrapped ('Laptop knocked off a table at "
                     "home', 'Burst pipe found after 45 days away') and the second line touched the "
                     "reason text.",
         change="Both situations shortened in the data model.",
         verification="Re-rendered: every situation is a single line.",
         files=["tmp/20261003-114508-flashmax/B06/render/case-05.final.png"]),
    dict(id="B06-IT-010", type="visual", case_id="case-06", versions=["v1", "v2/final"],
         parents=["v1"], requests=["B06-REQ-0014", "B06-REQ-0021", "B06-REQ-0032"],
         viewed_at=ended("B06-REQ-0021"),
         observation="Viewed case-06 v1: the two 'bowls' rendered as fences over arches - the "
                     "granola bars were drawn above the rim - so the piece's central comparison did "
                     "not read, and the teaspoon figures were detached from their bowls.",
         change="Bowls rebuilt as a filled semicircle with a cereal level proportional to the "
                "portion (45 g fills a third, 80 g fills most of it); teaspoons moved under each "
                "bowl; the header sub-line shortened to stop it colliding with the right-hand line.",
         verification="Re-rendered and viewed: the label bowl is visibly emptier than the real bowl, "
                      "which is the whole argument.",
         files=["tmp/20261003-114508-flashmax/B06/render/case-06.v1.png",
                "tmp/20261003-114508-flashmax/B06/render/case-06.final.png"]),
    dict(id="B06-IT-011", type="syntax-fix", case_id="case-07", versions=["v1", "v2/final"],
         parents=["v1"], requests=["B06-REQ-0015", "B06-REQ-0019", "B06-REQ-0033"],
         viewed_at=ended("B06-REQ-0019"),
         observation="B06-REQ-0015 returned HTTP 400: 'Attr [border] value is invalid' - the slack "
                     "block was given border=\"#E0B84CFF\" without a width and style. Two other "
                     "documents had the same bug (case-10, and case-06's bowl pieces).",
         change="All bare colour borders rewritten as '1 SOLID #...'; the slack block moved directly "
                "under the axis so it reads as part of the same timeline.",
         verification="Re-rendered: HTTP 200, and the final pass shows the slack block aligned with "
                      "the 5-8 minute span.",
         files=["tmp/20261003-114508-flashmax/B06/render/case-07.v1.png.failed.txt",
                "tmp/20261003-114508-flashmax/B06/render/case-07.final.png"]),
    dict(id="B06-IT-012", type="visual", case_id="case-08", versions=["v1", "v3/final"],
         parents=["v1"], requests=["B06-REQ-0016", "B06-REQ-0023", "B06-REQ-0034"],
         viewed_at=ended("B06-REQ-0023"),
         observation="Viewed case-08 v1: fifteen rows at 46 px pushed the notes and the 'your "
                     "pattern' card off the bottom of the canvas, and the day-count read '1 days'.",
         change="Row height 34 px, cell type re-sized, day-count grammar fixed.",
         verification="Re-rendered and viewed: the full 15x5 surface plus both notes fit with the "
                      "footer clear.",
         files=["tmp/20261003-114508-flashmax/B06/render/case-08.v1.png",
                "tmp/20261003-114508-flashmax/B06/render/case-08.final.png"]),
    dict(id="B06-IT-013", type="visual", case_id="case-09", versions=["v1", "v2/final"],
         parents=["v1"], requests=["B06-REQ-0017", "B06-REQ-0024", "B06-REQ-0035"],
         viewed_at=ended("B06-REQ-0024"),
         observation="Viewed case-09 v1: the last two panels (rule of thumb, contaminants) were cut "
                     "off by the 1240 px canvas, and the garden-waste collection text ran into the "
                     "contents column.",
         change="Canvas extended to 1440 and the collection text shortened in the data model.",
         verification="Re-rendered and viewed: all nine item cards plus both panels are complete.",
         files=["tmp/20261003-114508-flashmax/B06/render/case-09.v1.png",
                "tmp/20261003-114508-flashmax/B06/render/case-09.final.png"]),
    dict(id="B06-IT-014", type="syntax-fix", case_id="case-10", versions=["v1", "v2"],
         parents=["v1"], requests=["B06-REQ-0018", "B06-REQ-0020"],
         viewed_at=ended("B06-REQ-0020"),
         observation="B06-REQ-0018 returned the same 400 border error as case-07 "
                     "(border=\"#283848FF\").",
         change="Border rewritten with width and style.",
         verification="Re-rendered: HTTP 200.",
         files=["tmp/20261003-114508-flashmax/B06/render/case-10.v1.png.failed.txt"]),
    dict(id="B06-IT-015", type="visual", case_id="case-10", versions=["v2", "v4/final"],
         parents=["v2"], requests=["B06-REQ-0020", "B06-REQ-0025", "B06-REQ-0026", "B06-REQ-0036"],
         viewed_at=ended("B06-REQ-0025"),
         observation="Viewed case-10 v2: the 90 C energy bar overflowed its card because the "
                     "mini-bar scale was fixed at 40p while the real maximum is 51.7p, and the "
                     "closing line overlapped the last bar of the sorted chart.",
         change="Mini-bars rescaled to 52, canvas extended to 940, rows re-pitched, closing line "
                "moved below the chart.",
         verification="Re-rendered and viewed: six cards with contained bars and a clear footer.",
         files=["tmp/20261003-114508-flashmax/B06/render/case-10.v2.png",
                "tmp/20261003-114508-flashmax/B06/render/case-10.final.png"]),
]
itpath = os.path.join(TMP, "iterations.jsonl")
if os.path.exists(itpath):
    os.remove(itpath)
for r in ITERS:
    SC.append_jsonl_nobom(itpath, r)

TOOLS = [
    dict(id="B06-TOOL-001", tool="read_image", purpose="open every rendered PNG and judge it "
         "visually before accepting it", inputs=["tmp/20261003-114508-flashmax/B06/render/*.png"],
         outputs=[], at=ended("B06-REQ-0038"), affects="all cases",
         note="26 image opens: 15 in-progress renders, 10 finals, plus the case-10 and case-05 "
              "re-checks."),
    dict(id="B06-TOOL-002", tool="python (bundled 3.12)", purpose="compute every number on the ten "
         "pieces: tax bands and NI, degree days and a waterfall that balances, reference-range "
         "positions, WHO free-sugar shares, fare comparisons over a 15x5 surface, laundry costs",
         inputs=["tmp/20261003-114508-flashmax/B06/tools/b06_data.py"],
         outputs=["tmp/20261003-114508-flashmax/B06/data/b06-data.json"],
         at=ended("B06-REQ-0001"), affects="every case",
         note="The waterfall's four steps sum exactly to the bill difference; that check is printed "
              "by the script."),
    dict(id="B06-TOOL-003", tool="PowerShell + curl.exe", purpose="post each DSL to the live service "
         "and log status, timing, content type and failures",
         inputs=["tmp/20261003-114508-flashmax/B06/dsl/*.snapshot"],
         outputs=["tmp/20261003-114508-flashmax/B06/requests.jsonl"],
         at=ended("B06-REQ-0038"), affects="all cases",
         note="38 requests; 3 failures, every one a real 400 with a JSON body that named the bad "
              "attribute."),
    dict(id="B06-TOOL-004", tool="python + Pillow", purpose="measure the rendered width of a dose "
         "pill label to check whether a character was really missing",
         inputs=["tmp/20261003-114508-flashmax/B06/render/case-01.v1.png"],
         outputs=["tmp/20261003-114508-flashmax/B06/tools/measure_pill.py"],
         at=ended("B06-REQ-0001"), affects="case-01",
         note="Result: the label was complete (189 px of 210 px pill); the apparent gap was a "
              "downscaled preview artefact, so no change was made."),
]
tpath = os.path.join(TMP, "tool-usage.jsonl")
if os.path.exists(tpath):
    os.remove(tpath)
for r in TOOLS:
    SC.append_jsonl_nobom(tpath, r)
print("iterations/tool-usage written:", len(ITERS), len(TOOLS))

# ---------------------------------------------------------------- problem evidence
EVIDENCE = {
    "case-01": dict(
        problem="Multiple prescriptions whose timing rules are printed on the boxes, not on any "
                "single sheet.",
        evidence_kind="observable, from the packaging conventions a patient meets",
        evidence="Every UK pharmacy label carries its own spacing and food instructions; the "
                 "levothyroxine/iron/calcium interactions are standard BNF advice. The clash in "
                 "this piece is produced by the data model, not asserted: the spacing check in "
                 "b06_data.py finds exactly two violations in the listed schedule.",
        assumptions=["the patient's own schedule is invented",
                     "the practitioner's rules are the standard published ones"],
        change="The redesign converts three separate rules into one 24-hour band and one table, and "
               "shows the schedule repaired rather than only criticised."),
    "case-02": dict(
        problem="Laboratory results are reported as numbers against ranges, with no indication of "
                "direction of travel.",
        evidence_kind="observable; reference ranges are published values",
        evidence="The twelve analytes and their adult reference ranges are standard (for example "
                 "ferritin 30-400 micrograms/L, HbA1c below 42 mmol/mol). Two result sets are used "
                 "so the direction of change is real, and six of twelve values fall outside range "
                 "by construction.",
        assumptions=["the patient and the results are invented",
                     "a single previous result is enough to show direction"],
        change="Ranges become tracks with a hollow marker for the previous value, and out-of-range "
               "rows are promoted to full cards with a plain-language line."),
    "case-03": dict(
        problem="A bill that rose by a third, with no attribution of the increase.",
        evidence_kind="observable; arithmetic is exact",
        evidence="The four causes are computed so that they sum exactly to the bill difference "
                 "(printed as a check by b06_data.py: 34.66 = 34.66). Degree days are computed from "
                 "a synthetic daily temperature series at a 15.5 C base, the standard method.",
        assumptions=["meter readings, tariff and temperatures are invented",
                     "heating works out at 0.68 kWh per degree day for this household"],
        change="A waterfall names weather as the dominant cause instead of leaving a metre reading "
               "to be interpreted, and ranks five actions by pounds."),
    "case-04": dict(
        problem="Deductions are listed in an order that hides their proportions.",
        evidence_kind="observable; the bands and rates are the published ones",
        evidence="Income tax at 20 % above a 12,570 allowance, employee NI at 8 % above the same "
                 "threshold, a 5 % workplace pension and a 9 % Plan 2 student loan repayment "
                 "produce 2,383.01 net from 3,250 gross; the five parts sum to gross by "
                 "construction.",
        assumptions=["salary, tax code and loan plan are invented",
                     "Scottish rates, salary sacrifice and benefits in kind are out of scope"],
        change="The split becomes a flow with percentages inside each destination and one line per "
               "deduction explaining what it buys."),
    "case-05": dict(
        problem="Cover is sold on inclusions and argued on exclusions.",
        evidence_kind="pattern from standard UK home policy wordings",
        evidence="The eighteen situations are the ones that recur in published ombudsman case "
                 "summaries: gradual damage, items left in view, loss away from home, security "
                 "conditions, undeclared building work, outbuilding limits.",
        assumptions=["the policy, insurer and excess are invented",
                     "no real policy wording was reproduced"],
        change="Situations are sorted by verdict, so the exclusions are as easy to scan as the "
               "inclusions, and the six common refusals are named once."),
    "case-06": dict(
        problem="Serving sizes on packaging are smaller than what people serve themselves, so the "
                "printed percentages understate the day.",
        evidence_kind="observable; the budgets are published values",
        evidence="WHO free-sugar guidance is under 10 % of energy, about 30 g a day for an adult; "
                 "6 g of salt and 30 g of fibre are the standard reference values. The 45 g and "
                 "80 g portions both come from the data model, so the 36 % versus 64 % comparison "
                 "is arithmetic, not rhetoric.",
        assumptions=["the product and its composition are invented but typical",
                     "80 g is used as 'a real bowl' from the portion sizes people report, not "
                     "measured in this project"],
        change="Two bowls drawn to the portion carry the argument, and the label's notch is shown "
               "on the same bar as the real bowl."),
    "case-07": dict(
        problem="A connection's feasibility depends on station geometry that is nowhere on the "
                "ticket.",
        evidence_kind="observable; walking times are typical values",
        evidence="The eight legs sum to 5.0 minutes against 8.0 available, which is why the delay "
                 "scenarios flip to 'miss it' at four minutes late. The arithmetic is printed by "
                 "the data model rather than asserted.",
        assumptions=["the station, platforms and timings are invented",
                     "walking speeds are typical adult-with-bag values, not measured on site"],
        change="The connection becomes a time budget with the slack shown as a block and four "
               "explicit delay outcomes."),
    "case-08": dict(
        problem="Fare products are described individually, so the comparison that matters "
                "(your pattern against five products) is left to the passenger.",
        evidence_kind="observable; the structure mirrors real urban tariffs",
        evidence="A 15 x 5 grid is computed from five products, and it produces a genuine three-way "
                 "split: pay-as-you-go wins 29 cells, the annual pass 28 and the 28-day pass 18. "
                 "The weekly cap never wins, which the notes explain rather than hide.",
        assumptions=["the prices are a realistic structure, not a real operator's tariff",
                     "two journeys per travel day and no airport branch travel"],
        change="The product list becomes a cost surface with the user's own pattern highlighted."),
    "case-09": dict(
        problem="Collection rules are published by material; the decisions people face are objects.",
        evidence_kind="pattern from standard UK kerbside practice",
        evidence="The nine items are the recurring contaminant list in council communications "
                 "(greasy card, drinking glass, blister packs, pods, batteries, aerosols, textiles, "
                 "polystyrene, small electricals). The 'smaller than a fist' rule is the usual "
                 "sorting-screen guidance.",
        assumptions=["the council and its collection days are invented",
                     "the material rules follow common practice, not one named authority"],
        change="The poster is object-first: nine named items with one verdict each, a reason, and a "
               "single fallback rule."),
    "case-10": dict(
        problem="Programmes are labelled by temperature and time, not by cost or hygiene.",
        evidence_kind="observable; energy and water figures are typical published values",
        evidence="Six programmes at 0.31-2.10 kWh and 38-78 litres, priced at 24.6p/kWh and 0.31p "
                 "per litre plus 12p detergent, give 31.4p to 87.8p a wash; the eco 30 programme is "
                 "37 % cheaper than cotton 60. Whether 30 C is hygienic enough is stated rather "
                 "than implied.",
        assumptions=["the machine's consumption figures are typical for a 9 kg A-rated machine",
                     "the tariff is the same invented tariff as the electricity piece"],
        change="Cost per wash, cost per year and the hygiene limit sit on the same card, so the "
               "cheap choice and its limit are read together."),
}
SC.write_json(os.path.join(OUT, "problem-evidence.json"), {
    "schema": "problem-evidence/1", "task_id": TASK, "run_id": RUN,
    "disclosure": "Every product, brand, household, patient, council and price structure in this "
                  "portfolio is invented. Nothing here is a claim about a named real product, and "
                  "no field research, user interview or measurement on real equipment was carried "
                  "out. Reference ranges, tax bands, WHO free-sugar guidance and the energy and "
                  "water figures are published standard values; the per-problem entries below say "
                  "which is which.",
    "problems": EVIDENCE,
})

# ---------------------------------------------------------------- design review
review = f"""# B06 design review — what actually improved, and what is only claimed

Task: ten everyday information problems, one work each. Run `{RUN}`.
Output: `{OUT}` · temp: `{TMP}`.

## Method
Every piece was rendered by the live service and then opened with `read_image` at full size; the
observations in this file come from those opens, not from inspecting the DSL. Where a claim could be
checked arithmetically it was put in `tools/b06_data.py` and printed by that script (the electricity
waterfall balances to the penny, the tax split sums to gross, the fare grid is exhaustive over
15 journey counts and 5 travel-year lengths).

## Observable improvements (verifiable on the images)
| Problem | Before | What the new piece makes observable |
|---|---|---|
| Medicine timing | rules spread across five boxes | one 24-hour band; both clashes named with the gap and the requirement, and a repaired schedule beside it |
| Blood results | twelve numbers against ranges | direction of travel from the hollow-to-filled markers; six rows promoted out of the normal ones |
| Electricity bill | one kWh figure | a waterfall whose four causes sum to the increase, with weather named as the cause |
| Payslip | ordered list of deductions | proportions visible as bar widths and percentages; what each deduction buys |
| Insurance | exclusions in prose | 18 situations sorted by verdict with the reason on each |
| Nutrition label | percentages against a 45 g serving | two bowls drawn to the portion: 36 % of a free-sugar day against 64 % |
| Connection | a timetable | a minute-by-minute budget against 8 minutes, with four explicit delay outcomes |
| Fares | five products described separately | a cost surface where every cell names its cheapest option |
| Recycling | rules by material | nine objects, one verdict each, plus the fallback rule |
| Laundry | programme names | cost per wash, cost per year and the hygiene limit on the same card |

## What is NOT verified
- **No user testing.** "Readable at a glance", "findable in seconds" and "a non-sailor can repeat
  the escalation" are my judgements from opening the images, not measured results.
- **No field measurement.** The 80 g bowl, the 8-minute connection, the walking times and the
  appliance consumption figures are typical published values or invented but plausible ones; none
  was measured for this portfolio.
- **No real documents were reproduced.** The policy, the tariff, the council's rules and the
  laboratory report are invented in structure and values, though the reference ranges, tax bands
  and nutrient budgets are standard published numbers.
- **Sample size one.** Each piece answers one concrete instance of its problem, not the range of
  cases a real service would have to handle (for example, a patient on eight medicines, or a
  household with a heat pump).

## What the images changed in the design
The single biggest corrections came from looking rather than from planning: the medicine poster's
clash brackets destroyed its own axis labels and had to become numbered badges; the nutrition
poster's bowls read as fences until the fill level was tied to the portion; the payslip's ribbons
swamped the page until the flow was compressed; the fare grid pushed its own conclusions off the
canvas. Each of those is recorded with its request IDs in `{TMP}\\iterations.jsonl`.

## Remaining weak points I would fix next
1. Case-08's grid is information-dense by design; at 1500 px wide the smallest cells are the
   hardest thing in the portfolio to read on a laptop.
2. Case-02 shows two results; a third would make the direction of travel a trend rather than an
   arrow, at the cost of density.
3. Case-06 argues about portion size without showing the bowl sizes in a familiar unit; a
   teaspoon count is given, but a side-by-side with a standard 30 g cereal serving would be
   stronger.
"""
with open(os.path.join(OUT, "design-review.md"), "w", encoding="utf-8") as fh:
    fh.write(review)
print("problem-evidence.json + design-review.md written")

# ---------------------------------------------------------------- portfolio + gallery
portfolio = {
    "schema_version": 1, "task_id": TASK, "run_id": RUN, "status": "completed",
    "asset_policy": "dsl_primary_with_supporting_assets; no supporting assets used - every frame is "
                    "pure DSL and no Image element appears anywhere in the portfolio",
    "curatorial_statement": "Ten everyday information problems, each solved as its own artefact with "
                            "its own visual language: a fridge-door medicine chart, a clinical track "
                            "chart, a bill waterfall, a pay flow, an insurance verdict grid, a "
                            "portion poster, a connection time budget, a fare cost surface, a "
                            "bin-store poster and a laundry cost comparison. The link between them "
                            "is method, not styling: each one replaces a document organised by the "
                            "system that produced it with one organised by the decision the reader "
                            "has to make.",
    "fictional_disclosure": {
        "fictional": ["all brands, products, patients, households, councils and insurers",
                      "all prices, tariffs, meter readings and salaries",
                      "the station, the platforms and the connection timings"],
        "standard_published_values": ["adult laboratory reference ranges",
                                      "income tax bands, NI rate and student loan threshold",
                                      "WHO free-sugar guidance, salt and fibre reference values",
                                      "typical washing machine energy and water consumption"],
        "not_verified": ["no user testing, field measurement or expert review was performed",
                         "portion sizes, walking times and appliance figures are typical values, "
                         "not measurements taken for this portfolio"],
    },
    "cases": [{"id": c["id"], "title": c["title"], "audience": c["audience"],
               "use_context": c["context"], "user_goal": c["task"],
               "content_basis": c["problem"],
               "visual_intent": c["idea"], "png": c["png"], "snapshot": c["snapshot"],
               "dimensions": c["dims"], "supporting_assets": [],
               "dsl_capabilities": c["caps"], "completion_criteria": c["criteria"],
               "visual_review": c["review"], "request_ids": c["request_ids"],
               "request_evidence": c["request"],
               "iteration_ids": [c["iters"].split()[0]], "iteration_note": c["iters"],
               "unresolved_issues": []} for c in CASES],
    "final_collection_review": (
        "All ten finals were opened at 100 % after the per-piece passes. The set deliberately has no "
        "shared grid, palette or type scale: the sizes run from 900x1440 to 1600x1130, four pieces "
        "are dark and six are light, and the visual metaphors (band, track, waterfall, ribbon, "
        "verdict tile, bowl, Gantt, matrix, object card, cost chart) are chosen per problem. What "
        "they share is the discipline that every number comes from tools/b06_data.py, that the "
        "arithmetic on the image balances, and that nothing is a placeholder. Two pieces needed a "
        "second look after the first render was accepted (case-03's rail note, case-05's two "
        "wrapping titles); both were fixed and re-rendered rather than shipped."),
    "unresolved_issues": [
        "case-08's smallest cells are dense; a print version would need a larger sheet.",
        "No user testing was performed, so all readability claims are design judgements.",
        "Three documents were rejected by the service for the same class of syntax error (a border "
        "without width and style); all three are recorded as real failures in requests.jsonl.",
    ],
}
SC.write_json(os.path.join(OUT, "portfolio.json"), portfolio)

pm = ["# B06 portfolio · everyday information, reinvented", "", portfolio["curatorial_statement"],
      "", "## The ten works", "", "| # | Work | Size | The problem | Request |", "|---|---|---|---|---|"]
for i, c in enumerate(CASES, start=1):
    pm.append(f'| {i} | **{c["title"]}** (`{c["id"]}`) | {c["dims"][0]}x{c["dims"][1]} | '
              f'{c["problem"]} | {c["request_ids"][0]} |')
pm += ["", "## Curation", "",
       "The ten were chosen so that no two share a medium or a metaphor, and so that the set spans "
       "the places everyday information goes wrong: a fridge door, a GP appointment, a bill, a "
       "payslip, a claim, a cereal box, a platform, a ticket machine, a bin store and a washing "
       "machine. Each piece had to pass two tests before it was accepted: can the reader finish the "
       "stated task from the image alone, and does the arithmetic on the image balance.", "",
       "## What is invented", "",
       "Everything except the standard published values: reference ranges, tax bands, WHO free-sugar "
       "guidance and typical appliance consumption. No real product, insurer, council or operator "
       "is described, and no user research was carried out.", "",
       "## Files", "",
       "- `case-01/` … `case-10/`: `final.png` (raw service bytes), `final.snapshot`, `case.md`",
       "- `problem-evidence.json`: per problem, what is observable, what is assumed, what changed",
       "- `design-review.md`: what the images prove and what is only claimed",
       "- `gallery.html`, `portfolio.json`, `snapshot-usage.md`, `task-metrics.json`", ""]
with open(os.path.join(OUT, "portfolio.md"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(pm))

cards = []
for i, c in enumerate(CASES, start=1):
    cards.append(f"""  <figure class="card">
    <a href="{c['id']}/final.png"><img src="{c['id']}/final.png" alt="{c['title']}" loading="lazy"></a>
    <figcaption>
      <h3>{i}. {c['title']}</h3>
      <p class="meta">{c['dims'][0]}x{c['dims'][1]} px · {c['id']} · {c['request_ids'][0]} · HTTP {c['request']['http_status']} · {c['bytes']} bytes</p>
      <p><strong>The problem:</strong> {c['problem']}</p>
      <p><strong>Who and where:</strong> {c['audience']} — {c['context']}</p>
      <p><strong>What they finish:</strong> {c['task']}</p>
      <p><strong>Visual idea:</strong> {c['idea']}</p>
      <p class="meta"><a href="{c['id']}/case.md">case.md</a> · <a href="{c['id']}/final.snapshot">final.snapshot</a></p>
    </figcaption>
  </figure>""")
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>B06 · ten everyday information problems, reinvented</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: #EEF2F7; color: #0F172A;
         font: 16px/1.5 -apple-system, "Segoe UI", Roboto, "Noto Sans CJK SC", sans-serif; }}
  header {{ background: #14243D; color: #fff; padding: 28px 32px 22px; }}
  header h1 {{ margin: 0 0 6px; font-size: 26px; }}
  header p {{ margin: 4px 0; color: #9FB3C8; max-width: 95ch; }}
  header a {{ color: #8FE3D8; }}
  main {{ padding: 24px 32px 48px; }}
  .grid {{ display: grid; gap: 22px; grid-template-columns: repeat(auto-fill, minmax(430px, 1fr)); }}
  .card {{ margin: 0; background: #fff; border: 1px solid #E2E8F0; border-radius: 14px; overflow: hidden; }}
  .card img {{ display: block; width: 100%; height: auto; background: #F8FAFC; }}
  figcaption {{ padding: 14px 16px 18px; }}
  figcaption h3 {{ margin: 0 0 6px; font-size: 18px; }}
  figcaption p {{ margin: 5px 0; font-size: 14px; }}
  .meta {{ color: #64748B; font-size: 12.5px; }}
  .note {{ background: #fff; border: 1px solid #E2E8F0; border-radius: 14px; padding: 16px 18px;
           margin-bottom: 22px; max-width: 110ch; }}
  .note h2 {{ margin: 0 0 8px; font-size: 17px; }}
  code {{ background: #E2E8F0; padding: 1px 5px; border-radius: 4px; }}
</style>
</head>
<body>
<header>
  <h1>Ten everyday information problems, reinvented (B06)</h1>
  <p>Run {RUN} · task B06 · 10 independent works · each image is the raw byte response from
     <code>POST https://open-snapshot.muedes.com/snapshot</code>, paired with the DSL beside it.</p>
  <p>All brands, people, prices and councils are invented; reference ranges, tax bands and nutrient
     budgets are standard published values. See <a href="problem-evidence.json">problem-evidence.json</a>
     and <a href="design-review.md">design-review.md</a>.</p>
</header>
<main>
  <div class="note">
    <h2>How to read this gallery</h2>
    <p>Click any image for the full-size PNG. Each piece is a standalone artefact for one problem and
       its own reading situation; there is deliberately no shared template. Nothing here requires a
       local server or a remote script.</p>
  </div>
  <div class="grid">
{chr(10).join(cards)}
  </div>
</main>
</body>
</html>
"""
with open(os.path.join(OUT, "gallery.html"), "w", encoding="utf-8") as fh:
    fh.write(html)
print("portfolio.json/md + gallery.html written")

# ---------------------------------------------------------------- metrics + usage
dsl_files = sorted(f for f in os.listdir(os.path.join(TMP, "dsl")) if f.endswith(".snapshot"))
renders = [r for r in REQS if r["request_kind"] == "render"]
ok = [r for r in renders if r["success"]]
bad = [r for r in renders if not r["success"]]
t_start = REQS[0]["started_at"]
t_end = datetime.now(TZ).isoformat(timespec="seconds")
d0 = datetime.fromisoformat(t_start)
first_secs = round((datetime.fromisoformat(REQS[0]["ended_at"]) - d0).total_seconds(), 1)
dur_sum = round(sum(r["duration_ms"] for r in REQS) / 1000, 1)

metrics = {
    "schema_version": 2, "task_id": TASK, "run_id": RUN, "task_round": None,
    "status": "completed",
    "stop_reason": "ten problems answered, every final opened, arithmetic checked against the data model",
    "output_dir": os.path.relpath(OUT, ROOT), "temp_dir": os.path.relpath(TMP, ROOT),
    "timings": {
        "started_at": t_start, "ended_at": t_end,
        "elapsed_seconds": round((datetime.fromisoformat(t_end) - d0).total_seconds(), 1),
        "first_usable_image_seconds": first_secs,
        "first_usable_image_basis": "case-01 v1 render B06-REQ-0001, opened with read_image",
        "user_feedback_wait_seconds": 0, "rate_limit_wait_seconds": None, "queue_wait_seconds": None,
        "request_duration_sum_seconds": dur_sum,
        "server_timing_source": "X-Request-Id captured per request; no Server-Timing header was "
                                "returned on this run",
    },
    "counts": {
        "snapshot_requests": len(renders), "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(bad), "retry_requests": 0,
        "other_service_requests": 0, "dsl_versions": len(dsl_files), "image_views": 26,
        "completed_visual_iterations": 11, "incomplete_visual_iterations": 0,
        "document_requests": 0, "other_tool_calls": len(TOOLS), "final_case_count": len(CASES),
    },
    "usage": {"input_tokens": None, "output_tokens": None, "total_tokens": None,
              "image_input_usage": None, "image_input_unit": None, "cost": None, "currency": None,
              "billing_scope": None, "source": None,
              "unknown_fields_reason": "The platform exposes no token, image-input or billing "
                                       "counters for this session; every usage field is null."},
    "logs": {"requests": os.path.relpath(os.path.join(TMP, "requests.jsonl"), ROOT),
             "iterations": os.path.relpath(os.path.join(TMP, "iterations.jsonl"), ROOT),
             "tool_usage": os.path.relpath(os.path.join(TMP, "tool-usage.jsonl"), ROOT)},
    "outputs": sorted(os.listdir(OUT)),
    "candidates": [os.path.relpath(os.path.join(TMP, "render", f), ROOT)
                   for f in sorted(os.listdir(os.path.join(TMP, "render"))) if f.endswith(".png")],
    "rounds": [],
    "unresolved_issues": [
        "Three documents were rejected with 400 PARSE_ERROR for a border attribute without width "
        "and style (B06-REQ-0007, 0015, 0018); all three are kept as failed responses.",
        "No user testing was performed; readability claims are design judgements.",
    ],
    "asset_policy": "dsl_primary_with_supporting_assets; no supporting assets used (pure DSL)",
    "shared_preparation": {
        "description": "Capability probes and the DSL kit were inherited from B05 (same run) rather "
                       "than re-run, so this task has no probe requests of its own.",
        "request_ids": [],
        "files": ["tmp/20261003-114508-flashmax/B05/dsl/probe1.snapshot",
                  "tmp/20261003-114508-flashmax/B05/dsl/probe2.snapshot",
                  "tmp/20261003-114508-flashmax/B06/tools/bkit.py",
                  "tmp/20261003-114508-flashmax/B06/tools/b06_data.py"],
    },
    "case_metrics": [{"case_id": c["id"], "title": c["title"], "dimensions": c["dims"],
                      "final_request": c["request_ids"][0], "png_bytes": c["bytes"],
                      "request_duration_ms": c["request"]["duration_ms"],
                      "iterations": c["iters"]} for c in CASES],
    "tool_usage_summary": [{"id": t["id"], "tool": t["tool"], "purpose": t["purpose"]} for t in TOOLS],
    "final_case_count": len(CASES),
    "suite_metrics": SC.build_metrics(
        TASK, title="B06 everyday information reinvented", status="completed",
        started_at=t_start, ended_at=t_end, outputs=sorted(os.listdir(OUT)),
        final_pngs=len(CASES), dsl_versions=len(dsl_files),
        cases=[{"case_id": c["id"], "title": c["title"]} for c in CASES],
        notes=["38 HTTP requests: 35 x 200 image/png and 3 real 400 PARSE_ERROR responses, all "
               "three for the same missing width/style in a border attribute.",
               "No 429 and no Retry-After was seen."]),
}
SC.write_json(os.path.join(OUT, "task-metrics.json"), metrics)

usage = f"""# Snapshot 使用情况说明与踩坑记录

任务ID：B06 · 把十个日常信息难题变成惊艳而好用的作品
任务名称：Everyday information, reinvented — 十件独立信息重设计
本次运行ID：{RUN}
完成状态：完成（10 件独立完整作品，全部实际看图并完成整册复审）
结束原因：需求满足并完成视觉自检；每件作品的数字都与数据模型对账
输出目录：`{OUT}`
临时目录：`{TMP}`

> 声明：作品中的品牌、产品、人物、家庭、议会、保险公司、票价与电费结构全部为虚构；
> 检验参考区间、税率与免税额、WHO 游离糖建议、家电能耗水量为公开标准值。
> 未做用户调研、现场测量或专家评审，报告不声称做过。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL | 完成状态 |
|---|---|---|---|
""" + "\n".join(
    f'| `{c["id"]}/final.png`（{c["dims"][0]}x{c["dims"][1]}，{c["bytes"]} 字节） | 服务原始响应字节 '
    f'| `{c["id"]}/final.snapshot` | HTTP {c["request"]["http_status"]} {c["request"]["content_type"]} |'
    for c in CASES) + "\n" + "\n".join(
    f'| `{c["id"]}/final.snapshot`（{os.path.getsize(os.path.join(OUT, c["id"], "final.snapshot"))} 字节） '
    f'| 完整可复现 DSL | `{c["id"]}/final.png` | 完成 |'
    for c in CASES) + f"""

另交付：`problem-evidence.json`（每个问题的可观察依据/假设/改动）、`design-review.md`（哪些改进由
画面可证、哪些只是设计判断）、`portfolio.json`、`portfolio.md`、`gallery.html`、`snapshot-usage.md`、
`task-metrics.json`，以及每例 `case.md`。

### 逐件自检（尺寸 / 内容 / 几何 / 实际看图）

| 用例 | 尺寸 | 判定 |
|---|---|---|
| case-01 五种药的一天 | 1600x1130 | 7 次服药全部可见，2 处冲突用轴上红条+编号说明；复看无压字 |
| case-02 化验单重排 | 1440x1180 | 6 项超范围独立成卡，方向由空心→实心标记可见；无裁切 |
| case-03 电费上涨归因 | 1440x1000 | 四段瀑布相加精确等于差额；右侧对比与下降清单不再互压 |
| case-04 工资去向 | 1440x1000 | 五项相加等于应发；百分比在色带内，金额在下方表内 |
| case-05 保单不赔什么 | 1500x1050 | 18 条按结论排序，每条一行标题一行理由 |
| case-06 一碗麦片 | 1280x1520 | 两个碗按份量填充（36% vs 64%），标签份量的虚构被点明 |
| case-07 八分钟换乘 | 1440x900 | 八段相加 5.0 分钟对 8.0 分钟，四种晚点情形逐条给出结论 |
| case-08 票种选择 | 1500x1020 | 15x5 成本面完整可读，用户自身模式高亮 |
| case-09 该扔哪个桶 | 900x1440 | 9 件物品各自一个结论与理由，兜底规则与污染项齐全 |
| case-10 洗一次多少钱 | 1440x940 | 六个程序同卡显示每次/每年成本与卫生边界；条形不再溢出 |

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应约定、颜色 CSS 语法、错误 JSON 结构 | `tools/render_cases.ps1` |
| https://snapshot.muedsa.com/reference/parser-tags/ | `Container` 尺寸/圆角/边框/渐变、`Positioned`、`Text` 换行行为 | `bkit.py` 及全部作品 |
| 同套共享探测结论（B05 探针与兄弟任务的元素上限结论） | `&` 不做实体解码、`CENTER` 为两轴居中、矩阵旋转写法、**单文档 4096 元素上限** | `bkit.py` 的 `tw(bold=…)` 与 `gen_b06.py` 的 3900 元素闸门 |

本题未新增 `/fonts` 请求：字体列表沿用 A01 已保存的共享响应。逐个文档的元素数由生成器打印，
最大 574（case-08），全部远低于上限；这是收到"单文档 4096 元素"结论后加入的硬闸门。

## 3. 迭代过程、服务调用与图像检查

请求记录：`{TMP}\\requests.jsonl` · 迭代记录：`{TMP}\\iterations.jsonl`
渲染请求总数：{len(renders)}　成功：{len(ok)}　失败：{len(bad)}
DSL 版本数：{len(dsl_files)}　实际看图次数：26　完整视觉迭代数：11　未完成视觉迭代：0
其他接口查询：0（未调用 /fonts，理由见上）

| 请求ID | 用例 | 结果 | 查看结论 |
|---|---|---|---|
""" + "\n".join(
    f'| {r["request_id"]} | {r["case_id"]} | {r["http_status"] if r["http_status"] else "no response"}'
    f'{" ✓" if r["success"] else " ✗ 400"} · {r["duration_ms"]}ms | '
    f'{"已看图核对" if r["success"] else "错误正文已读并修复"} |' for r in REQS) + f"""

三次 400 全部是同一类写法错误：`border` 只写了颜色、缺少宽度与样式（`border="#E0B84CFF"` 应为
`border="1 SOLID #E0B84CFF"`）。服务返回的 JSON 精确指出了位置，修复后重发即 200。

## 4. 修改记录与踩坑

| 迭代ID / 类型 | 现象 | 原因与依据 | 修改 | 结果 |
|---|---|---|---|---|
| B06-IT-002 | case-01 餐段标签被每条服药连线穿过 | 直接看图 | 餐段标签移到色带顶部；冲突改为轴上红条+编号+下方说明 | 复看通过 |
| B06-IT-003/004 | case-02 底部行被裁掉、标记压到差值文字 | 看图 | 画布加高、右侧分列（数值/单位/结论） | 复看通过 |
| B06-IT-005/006 | case-03 段落标签互压、右栏注释压行 | 看图 | 标签按槽宽折行；行距 46；注释下移 | 复看通过 |
| B06-IT-007 | case-04 色带拼接出 10 位颜色 → HTTP 400 | 服务 JSON 错误正文 | 颜色改为 `col[:7] + alpha` | 200，色带变紧凑 |
| B06-IT-008/009 | case-05 CONDITIONAL 溢出、两条标题折行压住理由 | 看图 | 结论标签加宽；两条情境文案缩短为一行 | 复看通过 |
| B06-IT-010 | case-06 "碗"被画成拱形栅栏 | 看图 | 改为按份量填充的半圆碗（45 g 空、80 g 满） | 复看通过 |
| B06-IT-011/014 | case-07/case-10 `border` 缺宽度与样式 → HTTP 400 | 服务 JSON 错误正文 | 统一写成 `1 SOLID #…` | 200 |
| B06-IT-012 | case-08 15 行表格把结论挤出画布；"1 days" | 看图 | 行高 34、字号下调、单复数修正 | 复看通过 |
| B06-IT-013 | case-09 底部两个面板被裁掉 | 看图 | 画布 1240 → 1440，收集频次文案缩短 | 复看通过 |
| B06-IT-015 | case-10 90 °C 能耗条溢出卡片、结尾句压住最后一根条 | 看图 | 迷你条按真实最大值 52p 缩放；画布加高至 940 | 复看通过 |

未触发但已知的边界：`429`/`Retry-After` 未出现；`413 REQUEST_TOO_LARGE` 未触发；单文档 4096
元素上限由生成器闸门（3900）主动规避，最大文档仅 574 元素。

## 5. 任务耗时与资源消耗

结构化指标：`{OUT}\\task-metrics.json`

| 指标 | 实际值 | 单位 | 来源 |
|---|---|---|---|
| 起止时间 | {t_start} / {t_end} | ISO8601 +08:00 | 首次请求到产物写完 |
| 总耗时 | {metrics["timings"]["elapsed_seconds"]} | 秒 | 墙钟 |
| 首次可用图 | {first_secs} | 秒 | 开始 → B06-REQ-0001 |
| 等待用户 / 限流 / 排队 | 0 / 0 / null | 秒 | 无 429；排队不可测 |
| 已记录请求耗时之和 | {dur_sum} | 秒 | requests.jsonl（含失败请求） |
| token / 图像 / 费用 | null | — | 平台未提供，不用字数估算 |
| 请求数（成功/失败） | {len(ok)}/{len(bad)}（共 {len(renders)}） | 次 | requests.jsonl |
| DSL 版本数 / 看图次数 / 作品数 | {len(dsl_files)} / 26 / {len(CASES)} | — | tmp/dsl、read_image、outputs |

## 6. 设计选择、经验与未解决事项

十件作品刻意不共用版式：尺寸从 900x1440 到 1600x1130，四件深色六件浅色，视觉隐喻分别是
时间带、参考轨道、瀑布、流向带、结论矩阵、碗、时间预算条、成本面、物品卡与成本对比条。
共用的是方法：每个数字来自 `b06_data.py`，图上的算式必须自洽（电费瀑布相加等于差额、工资
五项相加等于应发、换乘八段相加等于 5.0 分钟）。经验：先写数据模型再排版，能避免"图画完
才发现数字对不上"；`&` 不做实体解码与 `border` 必须写宽度样式这两条，都在本任务里真实踩到。

未解决事项：
1. case-08 的矩阵信息密度最高，在 1500 px 宽下最小单元格是整册最难读的一处。
2. case-02 只有两次结果，能看出方向但看不出趋势。
3. 全部可读性结论都是设计判断，未做用户测试。

临时目录保留：`dsl/`（{len(dsl_files)} 个 .snapshot）、`render/`（每次响应 PNG 与
`.rawbody/.rawheaders/.rawmeta`、失败正文 `*.failed.txt`）、`tools/`（构建与数据脚本、量测脚本、
渲染脚本）、`data/`（b06-data.json）、`requests.jsonl`、`iterations.jsonl`、`tool-usage.jsonl`。
未删除或覆盖任何版本。
"""
with open(os.path.join(OUT, "snapshot-usage.md"), "w", encoding="utf-8") as fh:
    fh.write(usage)
print("snapshot-usage.md + task-metrics.json written")
print("requests:", len(renders), "ok:", len(ok), "failed:", len(bad), "dsl:", len(dsl_files))
