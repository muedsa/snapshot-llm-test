# case-04 · Five-morning weather windows

**Final image** `final.png` (1600x1000, 238844 bytes) ·
**DSL** `final.snapshot` · **request** B05-REQ-0029 (HTTP 200,
image/png, 3170 ms, service id
`af8f26bd-7dd9-4c60-87a4-aa6d2720bc1a`)

## Scenario
- **Audience**: The skipper deciding which of the next five mornings to take off work for
- **Where and when**: Desktop, 1600x1000, read the evening before with the family calendar open
- **What the user is trying to finish**: Pick the safest morning window and know what would cancel it
- **Content basis**: Hand-authored three-model window table consistent with the tide gates and the route; model names Nimbus-HR / Pelagic-9 / Coastal-Meso are invented
  Everything is fictional except the formulas: see `../product-brief.md` and `../journey.json`.

## Visual choices
A comparison matrix where colour carries the verdict and dots carry model agreement, with the three Saturday wind curves plotted underneath

DSL capabilities used: Grid of filled cells with per-cell accent bars, small-multiple polyline chart, agreement dots, decision band

## Self-check against my own completion criteria
- The best and worst windows are obvious at a glance, the reason is stated in words, and model disagreement is visible rather than hidden
- Visual evidence: Viewed case-04.v1 (400 error, B05-REQ-0013) and v2/final (0014, 0015, 0029).
- Iterations: B05-IT-006 (syntax-fix) + B05-IT-007 (visual).
- Defects found by looking and the fix applied: v1 failed with PARSE_ERROR 400 because the forecast colours came out of the data model as bare hex without '#'; fixed in b05_data.py. v2 then needed the model legend moved below the axis labels and one bullet shortened to stay inside its card.
- Unresolved issues: none

## Assets
No external or photographic assets: the whole frame is built from Snapshot DSL primitives
(`Container`, `Stack`/`Positioned`, `Transform`, `ClipOval`/`ClipRRect`, gradients, `Text`).
