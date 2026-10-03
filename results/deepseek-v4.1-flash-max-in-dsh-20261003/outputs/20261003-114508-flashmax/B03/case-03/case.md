# case-03 · Generative botanical plate · Crypteris hallowayensis

- **Final render**: `final.png` (raw bytes of a 200 `image/png` response), from `tmp/20261003-114508-flashmax/B03/renders/case-03.v7.png`
- **DSL**: `final.snapshot` — version `v7`, self-contained, no external assets
- **Audience**: Readers of a natural-history plate (museum wall, field guide spread)
- **Use context**: A3 portrait print, read at 40 cm and at thumbnail size
- **User goal**: Show a plausible fern habit and its two magnified details with a proper specimen label block
- **Content basis**: procedurally generated frond, phyllotaxis inset (n=150, 137.5°), sporangia inset, collection data; the taxon is explicitly fictional
- **Visual intent**: Cream plate with a double frame, sepia serif type, one dominant organism, two circular insets, a scale bar and a caption
- **DSL capabilities used**: seeded PRNG geometry, log-spiral rachis, tapered pinnae from rotated bars, phyllotaxis from the golden angle, dashed guide ring, polygon-free circles
- **Completion criteria (self-set)**: the plate reads as botanical rather than diagrammatic; insets do not collide; the caption sits inside the frame
- **Visual review evidence**: v1 was rejected by the service twice (1 MiB body, then 4096 elements from rasterised pinnae); v2-v5 rebuilt the pinnae as rotated bars and moved the insets; v6 re-rendered after the entity fix so the collector line prints "R. Okonjo & T. Vasquez" instead of "&amp;"
- **Fictional-data note**: the subjects, brands, people, places and numbers in this work are invented demo content for a DSL study. No real client, organisation, person or measurement is depicted or implied.
- **Supporting assets**: none. The artwork is pure DSL; no photograph, bitmap or embedded `Image` is used, and no post-processing was applied to the returned PNG.
- **Rejected attempts kept**: `case-03.v1.png.failed.txt`
- **Unresolved issues**: none
