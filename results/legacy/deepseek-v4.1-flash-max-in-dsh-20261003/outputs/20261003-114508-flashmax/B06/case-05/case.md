# case-05 · What your policy does not cover

**Final image** `final.png` (1500x1050, 194923 bytes) ·
**DSL** `final.snapshot` · **request** B06-REQ-0038 (HTTP 200,
image/png, 3504 ms, service id
`7e56d835-b662-4f7f-b16c-633782d9a19d`)

## The problem this answers
Home insurance is sold on what it covers and claimed against on what it excludes; the exclusions are spread through 40 pages.

- **Audience**: A householder deciding whether to claim, or whether to add accidental damage
- **Where it is used**: Desktop, after something has gone wrong, in a hurry
- **What the reader has to finish**: Find the verdict for a specific situation in seconds, and see the six refusals that cause most disputes
- **Data**: computed by `../tools/b06_data.py` (see `problem-evidence.json` for what is real and
  what is invented). No external assets: every mark is a Snapshot DSL primitive.

## Visual idea
Eighteen real situations sorted by verdict, colour-coded, each with the reason in one line, and the six common refusals called out

DSL capabilities used: Sorted tile grid, verdict chips, per-tile accent bars, wrapping reason lines

## Self-check against my own completion criteria
- Covered, conditional and excluded are visually distinct and sorted so the good news and the bad news are separate; every tile has a reason
- Visual evidence: Viewed case-05 v3 (B06-REQ-0008) and final (B06-REQ-0038).
- Iterations: B06-IT-008 + B06-IT-009 (visual).
- Defect found by looking, and the fix: v3: two long situations wrapped into two lines and collided with their reason line, and the header counts overlapped the household line. Situations were shortened to one line, the chip widened for CONDITIONAL, and the counts moved into the left sub-line.
- Unresolved issues: none.
