# B03 · Twelve works exploring the Snapshot DSL creative frontier

Run `20261003-114508-flashmax` · task `B03` · 12 independent finished works · pure DSL, no embedded images, no post-processing.

Every `final.png` is the raw byte stream of a live HTTP 200 `image/png` response from `https://open-snapshot.muedsa.com/snapshot`; the matching `final.snapshot` is the exact text that produced it.

## Curatorial logic

Twelve finished pieces, each built around a different *structure* rather than a different colour scheme: a night-possession time-space grid, a fermentation day curve, a generative botanical plate, an LED departure board, a circular seismograph drum, a 24-channel meter wall, a cross-stitch chart, a picture-book spread, a washi recipe card, a hand-engraved fingering chart, an ornamental playbill and a weekly tide matrix. The set is a study of what becomes possible once three measured DSL facts are known: the exact Transform placement rule, an honest text-width model, and the service's element/body/height budgets. Each piece also had to survive being looked at, so every work in this set carries at least one documented visual correction.

## The works

| # | Work | Structure | Size | DSL idea it proves |
|---|---|---|---|---|
| 01 | Night possession plan · Line 4 | time-space diagram (lanes × time) | 1800×1200 | flat Stack absolute layout |
| 02 | Sourdough fermentation schedule | single-day dual series + step table | 1240×1754 | rotated-bar polylines with round joins |
| 03 | Generative botanical plate · Crypteris hallowayensis | specimen plate with two insets | 1600×2100 | seeded PRNG geometry |
| 04 | Dot-matrix departure board · Halloway Station | character matrix / bitmap font | 1560×1020 | bitmap font emitted as square LED cells |
| 05 | Drum seismogram · station HLY | polar drum + helicorder | 1700×1500 | parametric circular geometry |
| 06 | Monitor wall · 24 channels | ranked bar matrix on a real dB scale | 1760×1180 | dB-to-pixel scale mapping |
| 07 | Counted cross-stitch sampler · Kestrel Junction 2026 | stitch chart with a key column | 1560×1650 | rotated square stitches at a computed pitch |
| 08 | The Paper Boat · picture-book spread | narrative spread (flat collage) | 1920×1200 | filled polygons for silhouettes |
| 09 | Recipe card · Tori shio ramen | vertical CJK card with a timeline | 1080×1720 | vertical CJK setting as one glyph per Text at a computed pitch |
| 10 | First-position fingering chart · violin | music engraving + teaching grid | 1700×1100 | drawn music staff with rotated note heads and stems |
| 11 | Playbill · Kestrel & the Long Tide | ornamental playbill | 1080×1560 | nested frame rules |
| 12 | Tide & light planner · Halloway Rowing Club | weekly multi-encoding matrix | 1700×1240 | one generator driving curves and the derived table |

## How to read a work

Each `case-NN/case.md` states audience, context, goal, content basis, visual intent, the DSL capabilities used, the completion criteria I set, the visual-review evidence, the rejected attempts kept in the temp directory, and any unresolved issue.

## Fictional-content disclosure

No work depicts a real client, organisation, dataset or measurement. Rail notices, bakery schedules, seismic events, sessions, samplers, recipes, plays, timetables and tide predictions are all invented demo content and are labelled as such on the sheet itself wherever a reader could mistake them for real data.

## Review

Twelve works reviewed at full size and as a contact sheet. Independence check: no two works share a layout skeleton, and the shared code is limited to primitives (text fitting, rotated bars, area fills, legends). Size range 1080x1520 to 1920x1200; colour languages differ per work by design (control-room navy, linen paper, cream museum plate, black LED, smoked paper, console charcoal, woven flax, paper-collage brights, washi, white music paper, cream playbill, deep-water dark). Defects found and fixed in review are listed per case. Remaining known limits: a true clip layer is unusable with absolute positioning (see case-02 and technique-notes.md), and the element budget of 4096 caps generative density.

## Known limits

- Clip layers cannot be combined with absolute positioning in this build: nesting a Stack inside a clipped Container re-bases every child by the layer origin.
- The 4096-element cap limits procedurally dense sheets; workarounds are coarser scanlines and fewer motifs, which is a real constraint on generative density.
- Text inside a width-constrained Container still wraps rather than truncating, so every string is measured before placement by design.
