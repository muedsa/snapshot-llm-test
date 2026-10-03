# case-08 · Which ticket is cheapest for the way you travel

**Final image** `final.png` (1500x1020, 225615 bytes) ·
**DSL** `final.snapshot` · **request** B06-REQ-0034 (HTTP 200,
image/png, 2856 ms, service id
`bec593d4-7dc5-4d84-b669-dfda0e5358f5`)

## The problem this answers
Five ticket types, four caps and a pass, and no way to tell which one is cheaper for a pattern that is not the one in the advert.

- **Audience**: A commuter deciding between paying as they go and buying a pass
- **Where it is used**: Desktop, at the kitchen table, once a year (or after a fare rise)
- **What the reader has to finish**: Find the cheapest option for a stated number of journeys a week and weeks a year
- **Data**: computed by `../tools/b06_data.py` (see `problem-evidence.json` for what is real and
  what is invented). No external assets: every mark is a Snapshot DSL primitive.

## Visual idea
A cost surface rather than a price list: journeys a week down, weeks a year across, and the cheapest option printed in every cell

DSL capabilities used: Computed five-option comparison per cell, colour-coded winners, highlighted user pattern, notes that explain why the weekly cap almost never wins

## Self-check against my own completion criteria
- Every cell names its cheapest option and cost; the user's own pattern is highlighted; the dominated options are explained rather than hidden
- Visual evidence: Viewed case-08 v1 (B06-REQ-0016) and final (B06-REQ-0034).
- Iterations: B06-IT-012 (visual).
- Defect found by looking, and the fix: v1: fifteen rows at 46 px pushed the notes off the canvas. Row height reduced, cell type re-sized, and the day-count label fixed to read '1 day'.
- Unresolved issues: none.
