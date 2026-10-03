# case-03 · Depth

**Reader question this work answers**: How little ozone is left inside the hole?

- **Final render**: `final.png`, raw bytes of a 200 `image/png` response, from `tmp/20261003-114508-flashmax/B04/renders/case-03.v4.png`
- **DSL**: `final.snapshot` — version `v4`, complete and self-contained, no embedded images
- **Structure**: plumb lines hanging from the 220 DU threshold, inverted axis
- **Reported size**: 1800×1140 px
- **Data basis**: annual minimum daily column ozone 1979-2025; bar length is 220 DU minus that value, computed here and labelled as derived
- **Illustrative or modelled elements**: none — inputs are published, the derived quantity is stated on the sheet
- **Sources cited on the sheet**: S1, S2 (full records in `../sources.json`)
- **Visual review**: v1 and v2 plotted the raw minimum as a polyline, which read as a picket fence; v3 switched to the plumb-line encoding; v4 fixed the threshold label collision and drew the threshold rule after the bars so it stays visible
- **Rejected attempts kept**: none
- **Fictional content**: the only invented elements are the special's masthead name, issue number and editor byline, both declared in `../editorial-note.md`. No data, quote or figure on this sheet is invented: every number is either transcribed from the cited source or computed from it in `scripts/ozone.py`, and derived quantities are labelled as derived.
- **Supporting assets**: none. The artwork is pure DSL.
