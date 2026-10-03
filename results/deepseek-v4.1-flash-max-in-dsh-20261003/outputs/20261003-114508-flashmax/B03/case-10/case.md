# case-10 · First-position fingering chart · violin

- **Final render**: `final.png` (raw bytes of a 200 `image/png` response), from `tmp/20261003-114508-flashmax/B03/renders/case-10.v3.png`
- **DSL**: `final.snapshot` — version `v3`, self-contained, no external assets
- **Audience**: A violin teacher and a beginner pupil
- **Use context**: A printed handout (A3 or A4) on a music stand
- **User goal**: Find the note for each finger on each string and see the D major scale
- **Content basis**: 4 strings × 5 finger positions with note names and semitone offsets, the D major scale, and a hand-shape diagram; frequencies are equal-temperament values computed in the generator
- **Visual intent**: Bright paper, blue positions, a ruled staff with engraved-style note heads, a shaded hand/neck diagram
- **DSL capabilities used**: drawn music staff with rotated note heads and stems, accidentals from crossed bars, outlined circles for finger rings (cheaper than ring-of-bars)
- **Completion criteria (self-set)**: the grid is readable at A3 and A4; note positions match the grid; nothing runs past the right margin
- **Visual review evidence**: v1 the finger rings cost ~190 elements each and the chart hit 6434 elements; v2 replaced them with outlined circles and rebuilt the staff; v3 scaled the staff, simplified the clef and kept the hand diagram inside the canvas
- **Fictional-data note**: the subjects, brands, people, places and numbers in this work are invented demo content for a DSL study. No real client, organisation, person or measurement is depicted or implied.
- **Supporting assets**: none. The artwork is pure DSL; no photograph, bitmap or embedded `Image` is used, and no post-processing was applied to the returned PNG.
- **Rejected attempts kept**: none
- **Unresolved issues**: none
