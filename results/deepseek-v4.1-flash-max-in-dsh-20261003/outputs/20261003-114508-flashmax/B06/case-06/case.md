# case-06 · One bowl, most of your day's sugar

**Final image** `final.png` (1280x1520, 202084 bytes) ·
**DSL** `final.snapshot` · **request** B06-REQ-0032 (HTTP 200,
image/png, 3741 ms, service id
`d2d90e68-1e14-4d5c-8fcd-556adc9091e3`)

## The problem this answers
A cereal box calls 45 g a serving and prints percentages against it. A real bowl is 80 g, and the sugar goes from a third of a day to two thirds.

- **Audience**: A parent buying granola, reading the label in the shop or the kitchen
- **Where it is used**: A3 or A4 poster in the kitchen; also readable on a phone at the shelf
- **What the reader has to finish**: See what one real bowl costs against a whole day's sugar, fat, salt and fibre
- **Data**: computed by `../tools/b06_data.py` (see `problem-evidence.json` for what is real and
  what is invented). No external assets: every mark is a Snapshot DSL primitive.

## Visual idea
Two bowls drawn to the portion, not a table: the label bowl is nearly empty and the real bowl is nearly full, then four day-budget bars with the label notch

DSL capabilities used: Semicircle scanline fill for the bowls, fill level driven by grams, budget bars with a label marker, computed reference-value shares

## Self-check against my own completion criteria
- The two portions are visually different at a glance; the 45 g fiction is named; fibre is shown as the good news
- Visual evidence: Viewed case-06 v1 (B06-REQ-0014) and final (B06-REQ-0032).
- Iterations: B06-IT-010 (visual).
- Defect found by looking, and the fix: v1: the 'bowls' rendered as fences over arches because the granola bars were drawn above the rim. Rebuilt as a filled bowl with a cereal level proportional to the portion, which is what the piece is arguing about.
- Unresolved issues: none.
