# A22 round-01 independent final-source audit

Result: PASS for `A22-round-01-dashboard-v002` (`A22-request-000002`).

Audited the actual submitted source and original PNG bytes, final layout map, baseline parameters, producer computed data, and the independently recomputed six-row CSV. This review does not itself perform an image view or certify later rounds. Parent image evidence: `A22-view-000003` in `root-review-v001.json`.

- Four KPIs: net revenue **918,624**; operating profit **262,124**; orders **3,045**; overall conversion **11.15%** = 3,045 / 27,300.
- Six original month strings in chart and table; all **30 table cells** agree with exact independent arithmetic. Percentages use final-only exact half-up rounding.
- All **12 bars** use common zero y=724, scale 272/250000 pixels per unit, maximum 250,000, and correct labels; six axis ticks are 0 through 250,000 at 50,000 intervals.
- All 83 submitted text elements and 46 shapes match final-map content, bounds and styles. Minimum text font size is 22. Region and table/card geometry reconcile with parameters.
- The numeric conclusion is supported: September has maximum net revenue/profit; June profit is 27,914, down 14,056 (33.49%) from May; June/August refund rates both 8.00%. No unsupported currency is asserted.
- The only source change from actual v001 is chart-unit left 64→156 and width 744→670. Other source bytes are unchanged. Caption/top tick boxes now have 16px horizontal separation; parent owns the actual raster confirmation.
- PNG signature/IHDR and response digest confirm 1600×1000; 254995 original bytes; sha256 `7816e88ac8274a4d883858930b2501a91020f074d8890118ae8aca2f642894e8`. Actual source digest matches successful 200 response metadata.

Audit JSON includes hashes, 34 assertion groups, per-text/shape/cell/bar/axis evidence, and exact map/source regression. `all_writes_finished=true`. New HTTP/render/view counts are all 0. Future requirement files read: none.

Unresolved source/data issues: none.

Script: `audit-final-v001.cjs`; machine evidence: `final-audit-v001.json`.
