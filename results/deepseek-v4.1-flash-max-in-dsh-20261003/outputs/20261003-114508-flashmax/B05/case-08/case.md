# case-08 · Fuel and range planner

**Final image** `final.png` (1180x820, 169248 bytes) ·
**DSL** `final.snapshot` · **request** B05-REQ-0033 (HTTP 200,
image/png, 3414 ms, service id
`a03b5eae-1a9c-48f0-ac31-04f50f92543f`)

## Scenario
- **Audience**: The skipper deciding how much fuel to take and what to do if the wind gets up on the return leg
- **Where and when**: Tablet at home or on the boat before slipping, dark instrument panel
- **What the user is trying to finish**: See where 36 L goes in three scenarios, and know the range at each speed before committing to a long drift
- **Content basis**: Burn 8.2 L/h at 12 kn and 1.1 L/h drifting with a 20 % reserve, computed per leg and per drift minute by tools/b05_data.py
  Everything is fictional except the formulas: see `../product-brief.md` and `../journey.json`.

## Visual choices
A ladder rather than a pie: one stacked bar per scenario, so the reserve is visibly the part you never plan to touch

DSL capabilities used: Stacked segment bars with in-segment labels, horizontal range bars, scenario table, amber recommendation card

## Self-check against my own completion criteria
- The 12 kn headwind case and its margin are the most prominent numbers; range by speed shows the slow-down option; no column overflows its card
- Visual evidence: Viewed case-08.v1 (B05-REQ-0019) and v2/final (0021, 0033).
- Iterations: B05-IT-012 (visual).
- Defects found by looking and the fix applied: v1: the ladder footnote and the margin column ran past their panels and the recommendation bullets wrapped into each other; text shortened, columns re-spaced, margin shown as L / nm.
- Unresolved issues: none

## Assets
No external or photographic assets: the whole frame is built from Snapshot DSL primitives
(`Container`, `Stack`/`Positioned`, `Transform`, `ClipOval`/`ClipRRect`, gradients, `Text`).
