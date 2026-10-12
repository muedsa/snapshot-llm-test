# case-01 · Five medicines, one day

**Final image** `final.png` (1600x1130, 252554 bytes) ·
**DSL** `final.snapshot` · **request** B06-REQ-0027 (HTTP 200,
image/png, 3933 ms, service id
`1b1b4a6a-76fb-49c0-974d-4857460bfa1b`)

## The problem this answers
Five prescriptions, seven doses a day, and rules that only exist on the boxes: levothyroxine needs an empty stomach and four hours from iron and calcium, iron and calcium need two hours between them, and two of the doses clash.

- **Audience**: A 68-year-old taking five medicines, and the adult daughter who does the repeats
- **Where it is used**: Printed at A3 and stuck on the fridge door; also read on a phone at the pharmacy
- **What the reader has to finish**: Run the day without a timing clash, and know what to do about a missed dose
- **Data**: computed by `../tools/b06_data.py` (see `problem-evidence.json` for what is real and
  what is invented). No external assets: every mark is a Snapshot DSL primitive.

## Visual idea
A 24-hour band with every dose on a spoke, the clashes bracketed in red, and a table that turns each box's small print into one line

DSL capabilities used: Time axis from minutes, lane assignment so no two dose labels collide, red clash bars with numbered badges, zebra table, printed-paper palette

## Self-check against my own completion criteria
- Every dose is visible with its time; both clashes are named with the gap and the requirement; the fixed schedule is on the same sheet
- Visual evidence: Viewed case-01 v1 (B06-REQ-0001) and final (B06-REQ-0027).
- Iterations: B06-IT-002 (visual).
- Defect found by looking, and the fix: v1: the meal labels sat on the axis and were crossed by every dose connector, and the clash brackets crossed the hour labels. Meal labels moved to the top of their bands; the brackets became a red bar on the axis with numbered badges and an explained list under it.
- Unresolved issues: none.
