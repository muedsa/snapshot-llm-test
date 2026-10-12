# case-10 · Season debrief

**Final image** `final.png` (1600x1000, 239311 bytes) ·
**DSL** `final.snapshot` · **request** B05-REQ-0035 (HTTP 200,
image/png, 2665 ms, service id
`6011a663-752b-46ca-a421-af23648095af`)

## Scenario
- **Audience**: The skipper at the end of the season, deciding what to change next year
- **Where and when**: Desktop or tablet at home, 1600x1000, unhurried
- **What the user is trying to finish**: See the season's patterns and adopt three or four concrete rules for next year
- **Content basis**: 26-trip log, monthly distance and trip counts, forecast-error series and three logged close calls with the rule each one produced
  Everything is fictional except the formulas: see `../product-brief.md` and `../journey.json`.

## Visual choices
Calm analytics: bar chart of the season, a red error line that rises as the season goes on, and a navy card that turns observations into rules

DSL capabilities used: Bar chart with per-bar labels, line chart with a shaded threshold band, KPI tiles, checkbox row

## Self-check against my own completion criteria
- Every chart is readable without the caption; the three close calls each end in a rule; the season totals match the log
- Visual evidence: Viewed case-10.v1 (B05-REQ-0023) and v3/final (0025, 0035).
- Iterations: B05-IT-014 (visual).
- Defects found by looking and the fix applied: v1: the KPI sub-labels collided with the 44 px values and the threshold-band label sat under a data point; sub-labels moved onto their own line and the band label shortened.
- Unresolved issues: none

## Assets
No external or photographic assets: the whole frame is built from Snapshot DSL primitives
(`Container`, `Stack`/`Positioned`, `Transform`, `ClipOval`/`ClipRRect`, gradients, `Text`).
