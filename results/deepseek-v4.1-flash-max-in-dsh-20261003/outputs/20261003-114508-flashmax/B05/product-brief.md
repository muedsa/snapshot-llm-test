# Kelpline — product brief (B05)

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
