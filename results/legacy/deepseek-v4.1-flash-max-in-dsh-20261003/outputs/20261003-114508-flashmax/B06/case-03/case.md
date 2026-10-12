# case-03 · Why this bill is £34.66 higher

**Final image** `final.png` (1440x1000, 186889 bytes) ·
**DSL** `final.snapshot` · **request** B06-REQ-0037 (HTTP 200,
image/png, 4051 ms, service id
`46b19e7e-9e52-4a66-9ce1-591d0a51b510`)

## The problem this answers
An electricity bill that jumped a third in a month, with no explanation beyond a kWh figure and a colder October.

- **Audience**: A two-adult household on a variable tariff
- **Where it is used**: Desktop, the evening the bill lands, with the previous bill to hand
- **What the reader has to finish**: See how much of the increase is weather, how much is price, and what would actually reduce it
- **Data**: computed by `../tools/b06_data.py` (see `problem-evidence.json` for what is real and
  what is invented). No external assets: every mark is a Snapshot DSL primitive.

## Visual idea
A waterfall from last month's bill to this month's, with degree days named as the cause and a ranked list of what would bring it down

DSL capabilities used: Floating waterfall bars with dashed connectors, wrapped labels under each bar, month-comparison rail, ranked saving bars

## Self-check against my own completion criteria
- The four reasons sum exactly to the bill difference; the weather share is named as weather; the actions are ranked by pounds
- Visual evidence: Viewed case-03 v3 (B06-REQ-0006) and final (B06-REQ-0037).
- Iterations: B06-IT-005 + B06-IT-006 (visual).
- Defect found by looking, and the fix: v3: the step labels ran into each other and the right rail's previous-month column collided with its labels. Labels now wrap into up to three lines per slot; the rail was rebuilt as label-over-comparison rows.
- Unresolved issues: none.
