# case-09 · Which bin does this go in?

**Final image** `final.png` (900x1440, 212707 bytes) ·
**DSL** `final.snapshot` · **request** B06-REQ-0035 (HTTP 200,
image/png, 1942 ms, service id
`93845e53-bee0-43ea-b367-8a2e23db1dc8`)

## The problem this answers
Kerbside rules are published as a list of materials, but the decisions people actually face are objects: a greasy pizza box, a broken glass, a kettle.

- **Audience**: Residents at the bin store, and anyone doing a clear-out
- **Where it is used**: A3 poster screwed to the bin-store wall, read standing up with a bag in one hand
- **What the reader has to finish**: Decide the bin for nine awkward items, and know the one rule that covers most of the rest
- **Data**: computed by `../tools/b06_data.py` (see `problem-evidence.json` for what is real and
  what is invented). No external assets: every mark is a Snapshot DSL primitive.

## Visual idea
Object-first cards with the verdict as a coloured chip, the reason underneath, and a small contamination panel

DSL capabilities used: Object cards with verdict chips, kerbside summary table, rule-of-thumb panel, contaminant list

## Self-check against my own completion criteria
- Nine real items each end in one named destination with a reason; the 'smaller than a fist' rule is stated; contaminants are named
- Visual evidence: Viewed case-09 v1 (B06-REQ-0017) and final (B06-REQ-0035).
- Iterations: B06-IT-013 (visual).
- Defect found by looking, and the fix: v1 was 1240 px tall and cut off the last two panels; the canvas was extended to 1440 and the collection-frequency text shortened so it stopped running into the contents column.
- Unresolved issues: none.
