# case-07 · You have eight minutes

**Final image** `final.png` (1440x900, 116335 bytes) ·
**DSL** `final.snapshot` · **request** B06-REQ-0033 (HTTP 200,
image/png, 2296 ms, service id
`272706e4-1a8e-4e2a-a13e-c8066a03d9f1`)

## The problem this answers
A tight connection is decided by walking distances, stairs and a ticket-gate queue, none of which appear on the ticket.

- **Audience**: A traveller with one bag, changing trains at a big station
- **Where it is used**: Phone on the platform, between the doors opening and the next departure
- **What the reader has to finish**: Know whether the connection is comfortable, tight or already lost, and what happens if the first train is late
- **Data**: computed by `../tools/b06_data.py` (see `problem-evidence.json` for what is real and
  what is invented). No external assets: every mark is a Snapshot DSL primitive.

## Visual idea
A time budget built from eight real legs against an eight-minute axis, with the slack shown as a block and the delay scenarios below

DSL capabilities used: Minute-scaled Gantt bars, per-leg colour by kind of movement, slack block, red departure line, delay scenario cards

## Self-check against my own completion criteria
- Every leg is named and timed, the total equals the available time, and the delay scenarios say makes it or miss it explicitly
- Visual evidence: Viewed case-07 v2 (B06-REQ-0019) and final (B06-REQ-0033).
- Iterations: B06-IT-011 (visual).
- Defect found by looking, and the fix: The 400 on v1 was a border attribute without width and style; fixed. The slack block was then moved directly under the axis so it reads as part of the same timeline.
- Unresolved issues: none.
