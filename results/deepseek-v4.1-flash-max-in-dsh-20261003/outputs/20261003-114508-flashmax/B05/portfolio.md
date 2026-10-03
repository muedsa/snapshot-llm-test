# B05 portfolio · Kelpline

Ten screens of one invented product, Kelpline, shown in the order a real Saturday trip would touch them: decide, understand, prepare, choose the day, hand over, go to sea, go wrong, plan the margin, share ashore, learn. One design language (hull navy, chart paper, teal/amber/red semantics) and one signature mark - the tide curve - drawn at four different scales. All place names, the vessel, the people, the weather models and the harbour notices are fictional; the tides, bearings, fuel and drift numbers are computed by tools/b05_data.py, so the ten screens cannot contradict each other.

## The ten works

| # | Work | Device | What the user finishes | Request |
|---|---|---|---|---|
| 1 | **Dawn go/no-go card** (`case-01`) | 500x1060 | Decide whether to launch today, and file the float plan before leaving the house | B05-REQ-0026 |
| 2 | **Tide and stream day chart** (`case-02`) | 1600x1000 | Find the two bank-crossing windows and the slack-water times, and know how much water the crossing needs | B05-REQ-0027 |
| 3 | **Passage plan (A4, laminated)** (`case-03`) | 1240x1754 | Fly the route: legs, bearings, ETAs, tide at each arrival, abort criteria and the escape route if the bank gate fails | B05-REQ-0028 |
| 4 | **Five-morning weather windows** (`case-04`) | 1600x1000 | Pick the safest morning window and know what would cancel it | B05-REQ-0029 |
| 5 | **Float plan and shore watch** (`case-05`) | 500x1060 | Understand exactly when to expect contact, what happens if it does not come, and what to do at each escalation step | B05-REQ-0030 |
| 6 | **On-water glance display** (`case-06`) | 1180x820 | Know speed, depth, the bank gate countdown and the fuel state without reading a menu | B05-REQ-0036 |
| 7 | **Overdue: drift datum and search boxes** (`case-07`) | 1600x1000 | See where the boat probably is, in what order to search, and what is still missing from the picture | B05-REQ-0032 |
| 8 | **Fuel and range planner** (`case-08`) | 1180x820 | See where 36 L goes in three scenarios, and know the range at each speed before committing to a long drift | B05-REQ-0033 |
| 9 | **Harbour office e-ink noticeboard** (`case-09`) | 800x1200 | One look tells you which boats are out, who is late, what is closed and what the weather is doing | B05-REQ-0034 |
| 10 | **Season debrief** (`case-10`) | 1600x1000 | See the season's patterns and adopt three or four concrete rules for next year | B05-REQ-0035 |

## Curatorial logic

The task is a product, not a poster set, so the works are ordered as a journey and share one vocabulary: a verdict, its reasons, and the tide curve that produced them. Each screen was designed for the conditions in which that decision actually happens - which is why the same product is dark at 05:40, paper at the chart table, black on white in sunlight, red in an emergency and grey on an e-ink board.

Independence: no two works share a layout, a device, a state or a task. Cases 01 and 02 both concern the tide, but one is a decision card and the other a 24-hour chart with a stream strip; cases 07 and 08 both concern a boat in trouble, but one is a search datum and the other a fuel budget.

## What is fictional

Everything except the arithmetic. The port, the boat, the crew, the shore contact, the other eight vessels, the harbour notices, the phone numbers and the three weather model names are invented. The tide is a four-constituent harmonic sum with invented phases, the bearings and distances are real great-circle maths on invented coordinates, and the fuel, drift and solar numbers use standard formulas. No user research was carried out and no real deployment is claimed.

## Files

- `case-01/` … `case-10/`: `final.png` (raw service bytes), `final.snapshot`, `case.md`
- `product-brief.md`: the problem, the audience, the mechanism, the assumptions
- `journey.json`: how the ten screens hand work to each other, with the shared facts
- `gallery.html`: local index of all ten finals, relative links only
- `snapshot-usage.md`: documentation, per-file self-check, iterations, cost
- `task-metrics.json`: timings, requests, versions, image views
