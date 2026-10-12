# case-05 · Float plan and shore watch

**Final image** `final.png` (500x1060, 130798 bytes) ·
**DSL** `final.snapshot` · **request** B05-REQ-0030 (HTTP 200,
image/png, 1974 ms, service id
`52250aba-bf0c-44d2-bb7a-4718f8e113e0`)

## Scenario
- **Audience**: The shore contact (a family member ashore) and the skipper filing the plan
- **Where and when**: Phone, mid-morning at home, no specialist knowledge
- **What the user is trying to finish**: Understand exactly when to expect contact, what happens if it does not come, and what to do at each escalation step
- **Content basis**: Check-in ladder and escalation times derived from the day plan and the drift model; shore-contact view derived from the same route and position data
  Everything is fictional except the formulas: see `../product-brief.md` and `../journey.json`.

## Visual choices
Quiet, light, reassuring: one navy filing card, then a ladder with times and a red escalation block that is impossible to misread

DSL capabilities used: Light card stack, timeline with connector line, inline mini-chart of the route (filled coastline plus polyline), status pills

## Self-check against my own completion criteria
- A non-sailor can say what happens at 15:38, 16:08 and 16:38 without help; the number of check-ins is explicit
- Visual evidence: Viewed case-05.v2 (B05-REQ-0016) and case-05.final (0030).
- Iterations: B05-IT-008 (visual).
- Defects found by looking and the fix applied: v2: the mini chart's town label landed on top of the 'Petrel' summary text and the closing sentence ran off the canvas; the town label is now drawn only on the full chart and the sentence was shortened.
- Unresolved issues: none

## Assets
No external or photographic assets: the whole frame is built from Snapshot DSL primitives
(`Container`, `Stack`/`Positioned`, `Transform`, `ClipOval`/`ClipRRect`, gradients, `Text`).
