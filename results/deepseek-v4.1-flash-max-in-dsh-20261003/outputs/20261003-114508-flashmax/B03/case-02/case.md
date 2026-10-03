# case-02 · Sourdough fermentation schedule

- **Final render**: `final.png` (raw bytes of a 200 `image/png` response), from `tmp/20261003-114508-flashmax/B03/renders/case-02.v7.png`
- **DSL**: `final.snapshot` — version `v7`, self-contained, no external assets
- **Audience**: Bakery team (4 people) at a fictional neighbourhood bakery
- **Use context**: A4 sheet pinned above the bench, also read on a phone
- **User goal**: Follow today's steps and know what the dough should look like at each stage
- **Content basis**: 24 h dough and room temperature series and an 8 row step table; all values illustrative for a fictional bakery
- **Visual intent**: Warm linen paper, serif display type, hairline rules, filled dough band with a dashed room curve, on-curve annotation tags
- **DSL capabilities used**: rotated-bar polylines with round joins, stacked 2px area band, dashed line generator, measured text fitting, callout boxes clamped to the plot
- **Completion criteria (self-set)**: curve never leaves the plot frame; callouts never cross the curve; table columns align
- **Visual review evidence**: v1/v2 the dough curve read as disconnected dashes (abutting rotated bars only meet at corners on steep joints); v3 added joins and a filled band; v4/v5 nested clip layer re-based every child (abandoned, documented); v6 removed the alpha seam stripes and smoothed the series
- **Fictional-data note**: the subjects, brands, people, places and numbers in this work are invented demo content for a DSL study. No real client, organisation, person or measurement is depicted or implied.
- **Supporting assets**: none. The artwork is pure DSL; no photograph, bitmap or embedded `Image` is used, and no post-processing was applied to the returned PNG.
- **Rejected attempts kept**: none
- **Unresolved issues**: A true clip layer could not be used: nesting a Stack inside a clipped Container shifted every absolute child by the layer origin, so the series is clamped numerically instead.
