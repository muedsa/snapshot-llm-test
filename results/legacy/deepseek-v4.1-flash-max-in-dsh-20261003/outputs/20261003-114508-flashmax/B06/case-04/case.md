# case-04 · Your pay, and where it goes

**Final image** `final.png` (1440x1000, 158744 bytes) ·
**DSL** `final.snapshot` · **request** B06-REQ-0030 (HTTP 200,
image/png, 2742 ms, service id
`23b56926-d3d0-4ca3-b25e-0b3c5f5d9cbc`)

## The problem this answers
A payslip lists deductions in an order that hides the proportions: the biggest number on the page is not the one that reaches the bank.

- **Audience**: Anyone on PAYE who has never checked what the deductions buy
- **Where it is used**: Desktop at home, once a year, usually in January
- **What the reader has to finish**: See the split between take-home, tax, NI, pension and loan, and what each buys
- **Data**: computed by `../tools/b06_data.py` (see `problem-evidence.json` for what is real and
  what is invented). No external assets: every mark is a Snapshot DSL primitive.

## Visual idea
A flow: one gross bar splitting into five destination bars through translucent ribbons, with the percentage inside each destination

DSL capabilities used: Scanline-filled quadrilaterals for the ribbons, proportional widths, band arithmetic (allowance, basic rate, NI threshold, loan threshold) computed in the data model

## Self-check against my own completion criteria
- The five parts sum to gross; the take-home share is stated; each deduction has a plain-language line
- Visual evidence: Viewed case-04 v4 (B06-REQ-0010) and final (B06-REQ-0030).
- Iterations: B06-IT-007 (visual).
- Defect found by looking, and the fix: v4: the ribbons filled two thirds of the page and the narrow bars clipped their own labels. The flow was compressed, percentages moved inside the bars and the money moved into a labelled table under it.
- Unresolved issues: none.
