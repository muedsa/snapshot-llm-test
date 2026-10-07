# Static review of A01 build.cjs, v001

Reviewed build.cjs against A01 task/agent requirements and independently calculated-review-v02.json. This checks source data, text, scales and geometric boxes only. It is not a PNG visual inspection.

## Actionable corrections

1. `mini()` tick label text uses `18` pixels. Task body text must be at least20px; chart tick labels are body information. Change these labels to20px.
2. The first mini data label and top tick-label rectangles intersect. Sessions: first value label x1029–1107, y313–341; top y-axis tick label x990–1056, y327–355. Intersection width27px, height14px. Conversion has the same horizontal intersection and y486–514 versus y500–528. Glyphs may or may not visibly collide, but source boxes do; avoid by increasing left inset of data centers (e.g. sx1090) and/or moving axis labels to x982 width66 ending1048. Keep at least8px between boxes at final font20.
3. Final mini value/month label boxes end at1518+39=1557,5px beyond panel right1552. Canvas bounds are safe, but panel spacing should be fixed: final center1508 and max label width70, or decrease plot width while preserving identical x centers across the two charts.
4. The conversion title says `总订单 ÷ 访问次数` although plotted points use per-month orders/sessions. Numbers are correct; clarify title to `月订单 ÷ 月访问次数` or simply `订单 ÷ 访问次数` so the chart does not imply six-month totals at every point.

## Verified correct

- Canvas1600×1000; left48/right1552 establishes48px external margin except minor last-mini overflow above.
- KPI totals are exactly918624元,262124元,3045笔,11.15%. Overall conversion calculates3045/27300, rather than average monthly ratios.
- Monthly net/profit/refund/conversion calculations and all six detail table entries match the input and review.
- Financial grouped bars share zero baseline578, height scale224/250000, domain0–250000元. Each bar's height/top is correct. Final group center848, bars810–842 and853–885, inside panel48–950. All values positive, so negative handling is unnecessary for these inputs.
- Financial ticks0/50k/100k/150k/200k/250k are distinct and headed元. Body text20. No mixing of money and percentage scales.
- Session scale0–6000, conversion scale0–0.14; separate units; same month centers1068/1158/1248/1338/1428/1518.
- Detail table header700–736, rows y743/776/809/842/875/908 with30px boxes; final content ends938 inside card ending952. Numeric columns right-aligned, amounts integer, ratios2 decimals, six months complete. Header/body20/22.
- Management evidence is correct:September profit64368 vs August41052, increase23316, growth56.7962584%→56.80%; September refund4%; April-to-September visits3500→5600, growth60.00%; orders420→620, growth47.6190476%→47.62%; conversion12.00%→11.0714286%→11.07%. Recommendation does not claim proven causality.
- Conclusion content blocks end918 inside conclusion card ending952; footnote16px at964–988 fits1000px canvas. KPI footnotes16 are permitted. Management label/body20 or larger.
- `computed-data-v001.json` contains all source fields, monthly values, totals, axis definitions and the numbers cited by the conclusion. Add exact mini x-centers to chart_axes if convenient for future mechanical checks; not a blocker.

## Root visual checks still required

Inspect actual server PNG: ensure Chinese fallback font loads, main title and dense conclusion first line fit their boxes, tick and mini value glyphs do not collide after correction, September labels remain within panel padding, bar legend colors correspond to series, and no unexpected text wrapping/clipping occurs. Static source checks cannot establish these facts.
