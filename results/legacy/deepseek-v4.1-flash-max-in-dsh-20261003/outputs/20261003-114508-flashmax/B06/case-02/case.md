# case-02 · Your blood results, in range

**Final image** `final.png` (1440x1180, 183456 bytes) ·
**DSL** `final.snapshot` · **request** B06-REQ-0028 (HTTP 200,
image/png, 2349 ms, service id
`4a8f7a83-819b-4057-bfd2-b9102e95989d`)

## The problem this answers
A printout of twelve numbers with a reference range in brackets. Nobody can tell which ones matter, which way they moved, or by how much.

- **Audience**: The same patient, the evening the results arrive, before the GP appointment
- **Where it is used**: Desktop or tablet at home, then printed and taken to the appointment
- **What the reader has to finish**: Know which results need a conversation, and which way each one is moving
- **Data**: computed by `../tools/b06_data.py` (see `problem-evidence.json` for what is real and
  what is invented). No external assets: every mark is a Snapshot DSL primitive.

## Visual idea
Reference ranges as horizontal tracks: the band is the range, a hollow marker is the last result, a filled marker is now, so direction of travel is visible without numbers

DSL capabilities used: Per-row adaptive scale so every marker fits, range bands, hollow/filled markers, out-of-range rows promoted to full cards with plain-language meanings

## Self-check against my own completion criteria
- The six out-of-range results are separated from the six normal ones; each row shows value, unit, range and change; nothing is clipped
- Visual evidence: Viewed case-02 v1 (B06-REQ-0002), v2 (0004) and final (0028).
- Iterations: B06-IT-003 + B06-IT-004 (visual).
- Defect found by looking, and the fix: v1: the last compact rows fell off the canvas and out-of-range markers ran into the delta text. v2: the value, unit and flag were put in their own right-hand column and the tracks got per-row scales. Final: the unit moved off the delta text.
- Unresolved issues: none.
