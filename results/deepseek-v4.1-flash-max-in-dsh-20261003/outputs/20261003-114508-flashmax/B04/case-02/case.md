# case-02 · The 47-year record

**Reader question this work answers**: Did the hole stop growing?

- **Final render**: `final.png`, raw bytes of a 200 `image/png` response, from `tmp/20261003-114508-flashmax/B04/renders/case-02.v3.png`
- **DSL**: `final.snapshot` — version `v3`, complete and self-contained, no embedded images
- **Structure**: 46-column chart with a five-year trailing mean and a treaty rail
- **Reported size**: 1900×1180 px
- **Data basis**: maximum daily hole area for every year 1979-2025 from NASA Ozone Watch; 5-year mean computed here; 2000-2025 mean as a reference rule
- **Illustrative or modelled elements**: none — every plotted value is published
- **Sources cited on the sheet**: S1, S4 (full records in `../sources.json`)
- **Visual review**: v1 lost the end of its standfirst under the kicker and put the 2000 callout over the header; v2 moved it and fixed the clipped mean label; v3 moved the amber legend into the plot and stopped the 1995 tick colliding with the gap label
- **Rejected attempts kept**: none
- **Fictional content**: the only invented elements are the special's masthead name, issue number and editor byline, both declared in `../editorial-note.md`. No data, quote or figure on this sheet is invented: every number is either transcribed from the cited source or computed from it in `scripts/ozone.py`, and derived quantities are labelled as derived.
- **Supporting assets**: none. The artwork is pure DSL.
