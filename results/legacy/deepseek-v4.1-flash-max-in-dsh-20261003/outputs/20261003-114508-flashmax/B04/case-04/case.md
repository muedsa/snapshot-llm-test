# case-04 · One hole per year

**Reader question this work answers**: Did the season move, or only the size?

- **Final render**: `final.png`, raw bytes of a 200 `image/png` response, from `tmp/20261003-114508-flashmax/B04/renders/case-04.v5.png`
- **DSL**: `final.snapshot` — version `v5`, complete and self-contained, no embedded images
- **Structure**: calendar strip: one row per year, marker at the peak date, bar for the peak area
- **Reported size**: 1700×1480 px
- **Data basis**: published peak date and peak area for every year; the 07 Sep - 13 Oct averaging window named in the source table
- **Illustrative or modelled elements**: none in the plot
- **Sources cited on the sheet**: S1, S2 (full records in `../sources.json`)
- **Visual review**: v1 was a radial calendar that failed on sight (arcs clustered in one quadrant, month spokes read as stray lines, the schematic profile looked like a caterpillar); v2 rebuilt it as a strip but overflowed the canvas and put the 1995 gap row on top of 1994; v3-v5 fixed the row model, restored the averaging band and gave the footer room
- **Rejected attempts kept**: none
- **Fictional content**: the only invented elements are the special's masthead name, issue number and editor byline, both declared in `../editorial-note.md`. No data, quote or figure on this sheet is invented: every number is either transcribed from the cited source or computed from it in `scripts/ozone.py`, and derived quantities are labelled as derived.
- **Supporting assets**: none. The artwork is pure DSL.
