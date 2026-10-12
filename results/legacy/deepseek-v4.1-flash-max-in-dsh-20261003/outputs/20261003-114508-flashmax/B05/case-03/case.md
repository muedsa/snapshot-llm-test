# case-03 · Passage plan (A4, laminated)

**Final image** `final.png` (1240x1754, 350753 bytes) ·
**DSL** `final.snapshot` · **request** B05-REQ-0028 (HTTP 200,
image/png, 2833 ms, service id
`0a85f2da-2f75-471c-8cbd-4f0aec44825c`)

## Scenario
- **Audience**: Skipper and crew in the cockpit; also the shore contact who reads the same plan
- **Where and when**: A4 portrait, printed and laminated, read in daylight and spray
- **What the user is trying to finish**: Fly the route: legs, bearings, ETAs, tide at each arrival, abort criteria and the escape route if the bank gate fails
- **Content basis**: Leg bearings and distances from real geodesy on fictional waypoints; ETAs from the day plan; tide at arrival from the harmonic model
  Everything is fictional except the formulas: see `../product-brief.md` and `../journey.json`.

## Visual choices
A working document, not a poster: dense leg table, a chart sketch with the escape route, then the abort and emergency blocks

DSL capabilities used: Scanline-filled coastline polygon, lat/lon graticule, dashed escape route, arrow heads, zebra table rows, per-row gate colouring

## Self-check against my own completion criteria
- Every leg has bearing, distance, ETA and arrival height; the bank-crossing rows are marked; the escape route is drawn; no two blocks overlap
- Visual evidence: Viewed case-03.v1 (B05-REQ-0008), v2 (0011) and v3/final (0012, 0028).
- Iterations: B05-IT-004 + B05-IT-005 (visual, v1 -> v2 -> v3/final).
- Defects found by looking and the fix applied: v1: Old Keel Bank straddled the coastline, sections E/F overlapped section C/D, arrival times did not match the day plan and the gate marker sat on the wrong rows. v2: coastline redrawn north of every waypoint, sections re-flowed, ETAs and gate rows corrected. v3: shortened the fuel footnote that ran past the page edge.
- Unresolved issues: none

## Assets
No external or photographic assets: the whole frame is built from Snapshot DSL primitives
(`Container`, `Stack`/`Positioned`, `Transform`, `ClipOval`/`ClipRRect`, gradients, `Text`).
