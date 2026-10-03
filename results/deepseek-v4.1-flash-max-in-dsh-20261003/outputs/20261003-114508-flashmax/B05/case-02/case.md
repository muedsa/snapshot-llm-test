# case-02 · Tide and stream day chart

**Final image** `final.png` (1600x1000, 206610 bytes) ·
**DSL** `final.snapshot` · **request** B05-REQ-0027 (HTTP 200,
image/png, 3057 ms, service id
`e1a37d1d-3a58-4e14-8659-935c146e894e`)

## Scenario
- **Audience**: The same skipper, planning properly the evening before, and any small-craft user who wants the whole tidal day on one screen
- **Where and when**: Desktop or chart table, 1600x1000, read while planning
- **What the user is trying to finish**: Find the two bank-crossing windows and the slack-water times, and know how much water the crossing needs
- **Content basis**: Harmonic tide curve, stream model from the rate of rise, rule-of-twelfths table and gate windows computed by tools/b05_data.py
  Everything is fictional except the formulas: see `../product-brief.md` and `../journey.json`.

## Visual choices
An instrument panel: luminous curve on navy, green gate bands, red deadline, and a stream strip of per-hour arrows under it

DSL capabilities used: 24-hour polyline with 5-minute sampling, column fill under the curve, dashed deadline, event markers, per-hour rotated arrows, bars

## Self-check against my own completion criteria
- Both gate windows and both planned crossings can be read off without arithmetic; the stream direction is unambiguous; the right rail answers 'how much water'
- Visual evidence: Viewed case-02.v1 (B05-REQ-0006) and case-02.v2/final (B05-REQ-0010, 0027).
- Iterations: B05-IT-003 (visual + shared kit fix, v1 -> v2/final).
- Defects found by looking and the fix applied: v1 rendered 'Tide &amp; stream' and 'STREAM &lt; 0.2 KN' literally: the service does not decode XML entities in text nodes, so the shared esc() was changed to emit text verbatim. Also moved the slack-water note and the twelfths panel apart.
- Unresolved issues: none

## Assets
No external or photographic assets: the whole frame is built from Snapshot DSL primitives
(`Container`, `Stack`/`Positioned`, `Transform`, `ClipOval`/`ClipRRect`, gradients, `Text`).
