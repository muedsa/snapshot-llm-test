# A22 round-02 independent correction arithmetic

Arithmetic: PASS. Producer source/visual audit is still pending; all_writes_finished=false.

Only original input changes: 2026-08 refund_amount 15,048→25,048; 2026-09 operating_cost 138,000→208,000. Original month strings and all other raw fields are retained.

| Month | Net revenue | Profit | Refund | Conversion |
|---|---:|---:|---:|---:|
| 2026-04 | 119,700 | 37,700 | 5.00% | 12.00% |
| 2026-05 | 135,470 | 41,970 | 5.00% | 11.22% |
| 2026-06 | 126,914 | 27,914 | 8.00% | 10.60% |
| 2026-07 | 161,120 | 49,120 | 5.00% | 11.28% |
| 2026-08 | 163,052 | 31,052 | 13.32% | 10.96% |
| 2026-09 | 202,368 | -5,632 | 4.00% | 11.07% |

KPIs: **908,624 net; 182,124 profit; 3,045 orders; 11.15% overall conversion**. Corrected total refund=66,426, cost=726,500, gross=975,050, sessions=27,300, aggregate refund=6.81%.

Exact rational percentages are rounded half up only at the final two-decimal percent display. Overall conversion remains 3,045/27,300 =29/260.

Safe conclusion: “9月净收入达202,368，经营利润转负为−5,632。” July has the highest corrected profit49,120. August refund rises to13.32%; June remains8.00%. Old September-profit-maximum and equal June/August-refund claims no longer hold.

Suggested unchanged plot[156,452,670,272], shared domain−50,000…250,000: scale=0.0009066666666666666px/unit; zeroY=678.6666666666666. September profit−5,632 must extend **down** 5.106346666666666px to y=683.7730133333333. This recommendation is not evidence of actual producer geometry.

8 archived first-round files have immutable SHA256 preservation evidence. Original primary bounds/styles are recorded for the ±2px regression check. No future requirement reads, HTTP, render, view, state or producer modifications.

Full exact data, propagation, per-bar/tick suggested geometry, source hashes and checks: `correction-arithmetic-v001.json`. Actual calculation script: `calculate-correction-v001.cjs`.
