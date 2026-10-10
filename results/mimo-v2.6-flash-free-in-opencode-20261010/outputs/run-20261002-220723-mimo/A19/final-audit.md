# A19 · final audit

Generated: 2026-10-05T09:09:35+08:00 (UTC+08:00)

**problems = 0**

## Problems

None.

## Checks passed (87)

- present: grid-scene.png
- present: grid-scene.snapshot
- present: occlusion.png
- present: occlusion.snapshot
- present: occlusion-alternative.png
- present: occlusion-alternative.snapshot
- present: scene-data.json
- present: questions.json
- present: answers.json
- present: equivalence.json
- grid-scene.png is 1600x1600
- occlusion.png is 800x800
- occlusion-alternative.png is 800x800
- grid-scene.png carries the PNG magic bytes
- occlusion.png carries the PNG magic bytes
- occlusion-alternative.png carries the PNG magic bytes
- delivered grid-scene.png == service/authoring original grid-v03.png
- delivered grid-scene.snapshot == service/authoring original grid-v03.snapshot
- delivered occlusion.png == service/authoring original occ-a-v02.png
- delivered occlusion.snapshot == service/authoring original occ-a-v02.snapshot
- delivered occlusion-alternative.png == service/authoring original occ-b-v02.png
- delivered occlusion-alternative.snapshot == service/authoring original occ-b-v02.snapshot
- delivered scene-data.json == service/authoring original scene-v03.json
- delivered questions.json == service/authoring original questions-v03.json
- delivered answers.json == service/authoring original answers-v03.json
- grid-scene.snapshot rooted at <Snapshot
- grid-scene.snapshot closed with </Snapshot>
- grid-scene.snapshot embeds no external <Image> (A-track pure DSL)
- grid-scene.snapshot has no dashed / semi-transparent leak construct
- occlusion.snapshot rooted at <Snapshot
- occlusion.snapshot closed with </Snapshot>
- occlusion.snapshot embeds no external <Image> (A-track pure DSL)
- occlusion.snapshot has no dashed / semi-transparent leak construct
- occlusion-alternative.snapshot rooted at <Snapshot
- occlusion-alternative.snapshot closed with </Snapshot>
- occlusion-alternative.snapshot embeds no external <Image> (A-track pure DSL)
- occlusion-alternative.snapshot has no dashed / semi-transparent leak construct
- scene-data.json holds exactly 64 objects
- IDs run G01..G64 left-to-right / top-to-bottom
- one and only one subject in each of the 64 cells
- each of the 4 colours occurs exactly 16 times (orange=16 blue=16 purple=16 green=16)
- each of the 4 shapes occurs exactly 16 times (ring=16 rounded-square=16 circle=16 square=16)
- only the sizes 48/64/80 occur (
- every row has >= 3 distinct colours (min 3) and >= 3 distinct shapes (min 3)
- every ring has inner diameter = outer/2
- all 64 ID labels lie outside their subject bounding box
- questions.json holds 14 questions (12 grid + 2 occlusion)
- 12 grid questions
- 2 occlusion questions
- questions.json contains no answer field
- 5 questions require a two-step relation (>= 4)
- category covered: 复合属性检索
- category covered: 严格中心左右关系
- category covered: 距离
- category covered: 排序
- category covered: 包围框
- category covered: 颜色/形状计数
- every question states both the coordinate origin and the comparison standard
- answers.json holds 14 answers
- every answer carries answer / method / coordinate_tolerance / visibility_basis / uniqueness_check
- 1 answer(s) are 无法确定 (>= 1)
- Q13 (hidden object count) answers 无法确定
- the hidden-object-count question is not answered with a count; it answers: 无法确定
- no other answer is derived from anything behind the occlusion panel
- every object-id answer exists in scene-data.json
- questions.json carries a numbering block
- numbered entities = 84 (>= 18): 64 G-ids + 6 V-ids + 14 question ids
- numbering.meets_18 = true
- answers.json numbering block also >= 18
- equivalence.json verdict = EQUIVALENT
- pixel comparison: 0 of 640000 pixels differ
- pixel_comparison.identical = true
- the two DSL hidden blocks differ (different hidden content)
- DSL shared prefix and suffix are byte-identical
- the two occlusion PNGs are byte-identical (same SHA-256)
- equivalence.json records the delivered occlusion.png SHA-256
- equivalence.json records the delivered occlusion-alternative.png SHA-256
- the two occlusion DSLs differ (they must: hidden content differs)
- the two occlusion DSLs hide different numbers of fully-covered objects (A=3, B=4)
- equivalence.json states exactly what differs behind the panel
- fully-covered counts A=2, B=3 agree with answers.json Q13 (which states 2 and 3)
- process log present: requests.jsonl
- process log present: iterations.jsonl
- requests.jsonl: 7 render requests, 5 x 200, 2 x failure, request duration sum 22670.8 ms
- iterations.jsonl: 6 rows (baseline 1, visual 3, syntax-fix 2); 4 rows carry a rendered image
- present: snapshot-usage.md
- present: task-metrics.json

## Deliverables

| file | bytes | sha256 (first 16) |
|---|---|---|
| `grid-scene.png` | 97172 | 51D7738920ED3DDC |
| `grid-scene.snapshot` | 27611 | E4D85B10173333B9 |
| `occlusion.png` | 55304 | 12FE65E604ABDFE3 |
| `occlusion.snapshot` | 4863 | B5CE07313209B24C |
| `occlusion-alternative.png` | 55304 | 12FE65E604ABDFE3 |
| `occlusion-alternative.snapshot` | 5191 | DB34906E1475F919 |
| `scene-data.json` | 67917 | 6272D373E6EE3C68 |
| `questions.json` | 14155 | 32B1F223F28DA5D0 |
| `answers.json` | 20715 | 1A99FF6AF6679622 |
| `equivalence.json` | 8101 | BCC99E8E21DBD719 |
| `snapshot-usage.md` | 13816 | 2E860CB261293CD6 |
| `task-metrics.json` | 11829 | 7033D7FC1176D859 |
