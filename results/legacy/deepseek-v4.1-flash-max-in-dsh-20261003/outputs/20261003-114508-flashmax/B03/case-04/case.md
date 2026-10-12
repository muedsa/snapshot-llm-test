# case-04 · Dot-matrix departure board · Halloway Station

- **Final render**: `final.png` (raw bytes of a 200 `image/png` response), from `tmp/20261003-114508-flashmax/B03/renders/case-04.v4.png`
- **DSL**: `final.snapshot` — version `v4`, self-contained, no external assets
- **Audience**: Passengers on platforms 3–4 of a fictional station
- **Use context**: A 1560 px LED board, also rendered small on a phone
- **User goal**: Find the next departure, its platform and its status in under two seconds
- **Content basis**: 5 departures with destinations, platforms and states, plus a notice; the station, operator and timetable are invented
- **Visual intent**: Near-black board, amber/white/red LED cells, a hand-built 5x7 bitmap font, row banding, a status swatch legend
- **DSL capabilities used**: bitmap font emitted as square LED cells, per-status colour keys, monospaced column alignment, element budget management
- **Completion criteria (self-set)**: every glyph legible; columns never collide; the board fits the element budget without dropping rows
- **Visual review evidence**: v1 was rejected: 7381 elements against the 4096 cap; v2 revealed the local counter had under-reported by 2x (each Container is an element too); v3 fixed a column overlap; v4 tightened the panel
- **Fictional-data note**: the subjects, brands, people, places and numbers in this work are invented demo content for a DSL study. No real client, organisation, person or measurement is depicted or implied.
- **Supporting assets**: none. The artwork is pure DSL; no photograph, bitmap or embedded `Image` is used, and no post-processing was applied to the returned PNG.
- **Rejected attempts kept**: `case-04.v1.png.failed.txt`
- **Unresolved issues**: none
