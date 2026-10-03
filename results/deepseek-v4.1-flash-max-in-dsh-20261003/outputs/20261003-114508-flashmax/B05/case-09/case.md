# case-09 · Harbour office e-ink noticeboard

**Final image** `final.png` (800x1200, 180513 bytes) ·
**DSL** `final.snapshot` · **request** B05-REQ-0034 (HTTP 200,
image/png, 2636 ms, service id
`43b1f6bf-cdf0-4fd8-9c24-c529860b38e0`)

## Scenario
- **Audience**: Everyone on the pontoon: berth holders, visiting crews, the harbour master
- **Where and when**: 800x1200 e-ink panel in the harbour office window, read from 2-3 m, refreshed at 07:30
- **What the user is trying to finish**: One look tells you which boats are out, who is late, what is closed and what the weather is doing
- **Content basis**: Fleet list, notices, gate windows and the yellow wind warning, all consistent with the tide model and the passage plan
  Everything is fictional except the formulas: see `../product-brief.md` and `../journey.json`.

## Visual choices
Paper-like greyscale with a single red accent: no gradients, no shadows, heavy rules, type sized for three metres

DSL capabilities used: E-ink palette, table with highlight row, tag blocks, wrapping notice text, split gate / warning panel

## Self-check against my own completion criteria
- The Petrel row is findable in under three seconds; the warning and the gate times are both visible without scrolling; nothing is clipped
- Visual evidence: Viewed case-09.v1 (B05-REQ-0022) and v3/final (0024, 0034).
- Iterations: B05-IT-013 (visual).
- Defects found by looking and the fix applied: v1: the weather block ran past the right edge of the board; it was re-broken into four short lines that fit the 768 px text column.
- Unresolved issues: none

## Assets
No external or photographic assets: the whole frame is built from Snapshot DSL primitives
(`Container`, `Stack`/`Positioned`, `Transform`, `ClipOval`/`ClipRRect`, gradients, `Text`).
