# case-06 · On-water glance display

**Final image** `final.png` (1180x820, 108577 bytes) ·
**DSL** `final.snapshot` · **request** B05-REQ-0036 (HTTP 200,
image/png, 2089 ms, service id
`148f41f1-5991-4bc3-aeec-86df9f866178`)

## Scenario
- **Audience**: The skipper at the helm, wet hands, gloves, bright sunlight, engine idling on a drift
- **Where and when**: Tablet on a RAM mount at the console, 1180x820, read from 1 m in direct sun
- **What the user is trying to finish**: Know speed, depth, the bank gate countdown and the fuel state without reading a menu
- **Content basis**: Position, time, depth and fuel state consistent with the day plan; gate state from the harmonic model at 11:05; fuel burn from the fuel model
  Everything is fictional except the formulas: see `../product-brief.md` and `../journey.json`.

## Visual choices
Glanceable instrument: four big tiles, 104 px numerals, one loud red CLOSED card, compass tape across the top

DSL capabilities used: Compass ribbon generated from the heading (1 deg = 3 px), huge numerals, progress bar, colour-coded state cards

## Self-check against my own completion criteria
- Every value is readable at a glance in sunlight; the CLOSED gate is unambiguous; the return plan is on the same screen
- Visual evidence: Viewed case-06.v2 (B05-REQ-0017) and case-06.v4 (0036).
- Iterations: B05-IT-009 (visual).
- Defects found by looking and the fix applied: v2: the fuel tile put the 84 px value on top of its own unit line and bar; the tile was re-laid out (value 72 px with the unit line, bar and note stacked below).
- Unresolved issues: none

## Assets
No external or photographic assets: the whole frame is built from Snapshot DSL primitives
(`Container`, `Stack`/`Positioned`, `Transform`, `ClipOval`/`ClipRRect`, gradients, `Text`).
