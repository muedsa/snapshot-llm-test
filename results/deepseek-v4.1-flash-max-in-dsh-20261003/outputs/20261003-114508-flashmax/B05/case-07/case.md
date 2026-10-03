# case-07 · Overdue: drift datum and search boxes

**Final image** `final.png` (1600x1000, 283752 bytes) ·
**DSL** `final.snapshot` · **request** B05-REQ-0032 (HTTP 200,
image/png, 3133 ms, service id
`b76eee91-a916-45aa-8fd9-63d7a4d86082`)

## Scenario
- **Audience**: Coastguard watch officer and the shore contact, 20 minutes into an overdue alarm
- **Where and when**: Desktop in the ops room or at home, dark theme, high stress, 1600x1000
- **What the user is trying to finish**: See where the boat probably is, in what order to search, and what is still missing from the picture
- **Content basis**: Drift model in tools/b05_data.py: 3.5 % leeway on 18 kn of wind plus the tidal stream at 15:52, giving 1.16 kn toward 047 deg and three growing boxes
  Everything is fictional except the formulas: see `../product-brief.md` and `../journey.json`.

## Visual choices
Red on near-black, one chart carrying the whole story, numbers kept quiet so the boxes and the LKP dominate

DSL capabilities used: Equirectangular projection, scanline-filled ellipses, drift arrows, badge markers, probability bars, dark-red cards

## Self-check against my own completion criteria
- Box order, probability, area and sweep time are all legible; the assumptions behind the drift are stated on the image; nothing claims more certainty than the model has
- Visual evidence: Viewed case-07.v1 (B05-REQ-0018), v2 (0020) and final (0032).
- Iterations: B05-IT-010 + B05-IT-011 (visual).
- Defects found by looking and the fix applied: v1 drew 3.6 nm search boxes on a 6.7 nm-wide chart, so the ellipses swamped the frame and their labels collided with the bank label. v2 widened the chart to 13 nm, moved the box labels into a legend and badged the centres; the final added a backing plate behind the LKP label.
- Unresolved issues: none

## Assets
No external or photographic assets: the whole frame is built from Snapshot DSL primitives
(`Container`, `Stack`/`Positioned`, `Transform`, `ClipOval`/`ClipRRect`, gradients, `Text`).
