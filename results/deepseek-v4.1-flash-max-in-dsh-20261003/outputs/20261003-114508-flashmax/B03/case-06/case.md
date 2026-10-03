# case-06 · Monitor wall · 24 channels

- **Final render**: `final.png` (raw bytes of a 200 `image/png` response), from `tmp/20261003-114508-flashmax/B03/renders/case-06.v3.png`
- **DSL**: `final.snapshot` — version `v3`, self-contained, no external assets
- **Audience**: A mix engineer and a producer in a control room
- **Use context**: A 1760 px screen and a printed reference sheet
- **User goal**: Compare channel levels and spot the channels that risk clipping
- **Content basis**: 24 named channels with levels and peak holds on a real dB scale; the session, names and levels are invented
- **Visual intent**: Dark console palette, 2.4 dB segments coloured by zone, white peak-hold caps with numeric values, a zone key
- **DSL capabilities used**: dB-to-pixel scale mapping, segmented bars, computed peak caps, dense monospace labelling
- **Completion criteria (self-set)**: bar length is comparable across channels; every peak label is readable; no bar overlaps its neighbour
- **Visual review evidence**: v1/v2 printed "&amp;" and "&lt;" in the zone key because entities are not decoded by the parser; v3 moved the legend to minus-sign wording and restored the true values
- **Fictional-data note**: the subjects, brands, people, places and numbers in this work are invented demo content for a DSL study. No real client, organisation, person or measurement is depicted or implied.
- **Supporting assets**: none. The artwork is pure DSL; no photograph, bitmap or embedded `Image` is used, and no post-processing was applied to the returned PNG.
- **Rejected attempts kept**: none
- **Unresolved issues**: none
