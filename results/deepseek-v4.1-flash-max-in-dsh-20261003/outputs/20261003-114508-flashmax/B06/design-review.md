# B06 design review — what actually improved, and what is only claimed

Task: ten everyday information problems, one work each. Run `20261003-114508-flashmax`.
Output: `D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\B06` · temp: `D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\B06`.

## Method
Every piece was rendered by the live service and then opened with `read_image` at full size; the
observations in this file come from those opens, not from inspecting the DSL. Where a claim could be
checked arithmetically it was put in `tools/b06_data.py` and printed by that script (the electricity
waterfall balances to the penny, the tax split sums to gross, the fare grid is exhaustive over
15 journey counts and 5 travel-year lengths).

## Observable improvements (verifiable on the images)
| Problem | Before | What the new piece makes observable |
|---|---|---|
| Medicine timing | rules spread across five boxes | one 24-hour band; both clashes named with the gap and the requirement, and a repaired schedule beside it |
| Blood results | twelve numbers against ranges | direction of travel from the hollow-to-filled markers; six rows promoted out of the normal ones |
| Electricity bill | one kWh figure | a waterfall whose four causes sum to the increase, with weather named as the cause |
| Payslip | ordered list of deductions | proportions visible as bar widths and percentages; what each deduction buys |
| Insurance | exclusions in prose | 18 situations sorted by verdict with the reason on each |
| Nutrition label | percentages against a 45 g serving | two bowls drawn to the portion: 36 % of a free-sugar day against 64 % |
| Connection | a timetable | a minute-by-minute budget against 8 minutes, with four explicit delay outcomes |
| Fares | five products described separately | a cost surface where every cell names its cheapest option |
| Recycling | rules by material | nine objects, one verdict each, plus the fallback rule |
| Laundry | programme names | cost per wash, cost per year and the hygiene limit on the same card |

## What is NOT verified
- **No user testing.** "Readable at a glance", "findable in seconds" and "a non-sailor can repeat
  the escalation" are my judgements from opening the images, not measured results.
- **No field measurement.** The 80 g bowl, the 8-minute connection, the walking times and the
  appliance consumption figures are typical published values or invented but plausible ones; none
  was measured for this portfolio.
- **No real documents were reproduced.** The policy, the tariff, the council's rules and the
  laboratory report are invented in structure and values, though the reference ranges, tax bands
  and nutrient budgets are standard published numbers.
- **Sample size one.** Each piece answers one concrete instance of its problem, not the range of
  cases a real service would have to handle (for example, a patient on eight medicines, or a
  household with a heat pump).

## What the images changed in the design
The single biggest corrections came from looking rather than from planning: the medicine poster's
clash brackets destroyed its own axis labels and had to become numbered badges; the nutrition
poster's bowls read as fences until the fill level was tied to the portion; the payslip's ribbons
swamped the page until the flow was compressed; the fare grid pushed its own conclusions off the
canvas. Each of those is recorded with its request IDs in `D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\B06\iterations.jsonl`.

## Remaining weak points I would fix next
1. Case-08's grid is information-dense by design; at 1500 px wide the smallest cells are the
   hardest thing in the portfolio to read on a laptop.
2. Case-02 shows two results; a third would make the direction of travel a trend rather than an
   arrow, at the cost of density.
3. Case-06 argues about portion size without showing the bowl sizes in a familiar unit; a
   teaspoon count is given, but a side-by-side with a standard 30 g cereal serving would be
   stronger.
