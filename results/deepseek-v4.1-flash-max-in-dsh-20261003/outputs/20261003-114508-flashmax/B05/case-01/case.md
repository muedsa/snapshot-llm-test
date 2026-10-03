# case-01 · Dawn go/no-go card

**Final image** `final.png` (500x1060, 117918 bytes) ·
**DSL** `final.snapshot` · **request** B05-REQ-0026 (HTTP 200,
image/png, 3714 ms, service id
`2cdf985e-549f-462b-a853-0087c09c7e95`)

## Scenario
- **Audience**: Skipper of a 5.8 m open launch, at the kitchen table at 05:40 before a Saturday trip
- **Where and when**: Phone, dark room, one hand, before sunrise (sunrise 06:33)
- **What the user is trying to finish**: Decide whether to launch today, and file the float plan before leaving the house
- **Content basis**: Computed by tools/b05_data.py: four-constituent harmonic tide, route geodesy, fuel arithmetic, solar times. Port, vessel and people are fictional.
  Everything is fictional except the formulas: see `../product-brief.md` and `../journey.json`.

## Visual choices
Verdict first: one word at 64 px, then the four checks that produced it, then the tide curve that justifies the timing

DSL capabilities used: Stack absolute positioning, LINEAR gradient, rotated-segment polyline tide curve, gate shading, event markers, rounded dark cards, mono+CJK fonts

## Self-check against my own completion criteria
- The GO/NO-GO verdict is readable in under two seconds at arm's length; every number matches b05-data.json; nothing overlaps at 100 %
- Visual evidence: Viewed case-01.v1 (B05-REQ-0004) and case-01.final (B05-REQ-0026).
- Iterations: B05-IT-002 (visual, v1 -> v2/final).
- Defects found by looking and the fix applied: v1: the 'out 06:35' mark label collided with the panel title and the plan still showed 06:20/15:10 after the day plan was re-timed. Moved the mark label under the dot, dropped the 'now' label box into the caption row and re-synced launch 06:25 / back 15:08.
- Unresolved issues: none

## Assets
No external or photographic assets: the whole frame is built from Snapshot DSL primitives
(`Container`, `Stack`/`Positioned`, `Transform`, `ClipOval`/`ClipRRect`, gradients, `Text`).
