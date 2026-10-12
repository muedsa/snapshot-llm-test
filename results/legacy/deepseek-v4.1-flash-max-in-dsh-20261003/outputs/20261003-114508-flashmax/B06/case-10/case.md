# case-10 · What a wash really costs

**Final image** `final.png` (1440x940, 172321 bytes) ·
**DSL** `final.snapshot` · **request** B06-REQ-0036 (HTTP 200,
image/png, 2382 ms, service id
`6d0c8a39-8d3c-4495-8996-fa069c984bb9`)

## The problem this answers
Washing machine programmes are labelled by temperature and time, not by cost, and the difference between 30 and 60 is nearly half the running cost.

- **Audience**: A household running four washes a week
- **Where it is used**: Desktop or tablet, read once when the machine is next to be replaced
- **What the reader has to finish**: Pick the programme that is cheap enough without leaving clothes unhygienic
- **Data**: computed by `../tools/b06_data.py` (see `problem-evidence.json` for what is real and
  what is invented). No external assets: every mark is a Snapshot DSL primitive.

## Visual idea
Six programme cards with cost per wash and per year, a sorted cost chart, and a note on what each temperature actually removes

DSL capabilities used: Cost model from energy, water and detergent, per-programme stacked mini-bars, sorted comparison bars, dark instrument palette

## Self-check against my own completion criteria
- Cost per wash and per year are on every card; the saving between 30 and 60 is stated in pounds; hygiene limits are stated too
- Visual evidence: Viewed case-10 v2 (B06-REQ-0020) and final (B06-REQ-0036).
- Iterations: B06-IT-014 + B06-IT-015 (visual).
- Defect found by looking, and the fix: The 90 C energy bar overflowed its card (scale was fixed at 40p) and the closing line overlapped the last bar. Mini-bars rescaled to the real maximum, canvas extended, rows tightened.
- Unresolved issues: none.
