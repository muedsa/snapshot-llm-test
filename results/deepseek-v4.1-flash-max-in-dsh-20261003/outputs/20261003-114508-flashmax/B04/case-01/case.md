# case-01 · What the hole is

**Reader question this work answers**: What actually counts as the ozone hole?

- **Final render**: `final.png`, raw bytes of a 200 `image/png` response, from `tmp/20261003-114508-flashmax/B04/renders/case-01.v1.png`
- **DSL**: `final.snapshot` — version `v1`, complete and self-contained, no embedded images
- **Structure**: annotated atmospheric cross-section + definition panels
- **Reported size**: 1240×1754 px
- **Data basis**: 220 DU threshold, 90% of ozone between 10 and 50 km, 3 billion tonnes, peak near 32 km (NASA Ozone Watch)
- **Illustrative or modelled elements**: the cross-section profile, altitudes and vortex are labelled schematics
- **Sources cited on the sheet**: S2, S3 (full records in `../sources.json`)
- **Visual review**: v1 accepted on first look; the only fix was making the masthead wrap its standfirst so the kicker could not be overprinted (shared helper change)
- **Rejected attempts kept**: none
- **Fictional content**: the only invented elements are the special's masthead name, issue number and editor byline, both declared in `../editorial-note.md`. No data, quote or figure on this sheet is invented: every number is either transcribed from the cited source or computed from it in `scripts/ozone.py`, and derived quantities are labelled as derived.
- **Supporting assets**: none. The artwork is pure DSL.
