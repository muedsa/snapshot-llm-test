# A18 · final audit

run_id `run-20261002-220723-mimo` · task A18 three-act-story · 审计脚本 `tmp/run-20261002-220723-mimo/A18/check-a18.ps1`

**problems = 0 · notes = 55**

## Checks

- PASS  deliverable present: three-act-story.png
- PASS  deliverable present: three-act-story.snapshot
- PASS  deliverable present: story-audit.json
- PASS  deliverable present: rationale.md
- PASS  deliverable present: snapshot-usage.md
- PASS  deliverable present: task-metrics.json
- PASS  PNG signature valid (97982 bytes)
- PASS  dimensions 1600x1000 as required
- PASS  delivered PNG is byte-identical to the preview that was viewed (preview-a-v06.png)
- PASS  delivered DSL is byte-identical to the DSL that produced the PNG
- PASS  DSL is BOM free
- PASS  DSL decodes cleanly as UTF-8
- PASS  DSL is 742 lines
- PASS  exactly 4 <Text> elements
- PASS  text 1 verbatim: 同一系统的三幕演化
- PASS  text 2 verbatim: 第一幕 · 集中
- PASS  text 3 verbatim: 第二幕 · 过载
- PASS  text 4 verbatim: 第三幕 · 重新分配
- PASS  draw order links(29499) < nodes(29743) < units(32647) < text(40129): no stroke can cover a circle
- PASS  story-audit problems = 0
- PASS  story-audit recorded 4 text elements
- PASS  act 1: 15 units d36, 5 blue / 5 orange / 5 grey
- PASS  act 1: 3 equal nodes of 64px
- PASS  act 1: min unit-unit centre distance 56.97 >= 36
- PASS  act 1: min unit-node gap 24.07 px, no overlap
- PASS  act 2: 15 units d36, 5 blue / 5 orange / 5 grey
- PASS  act 2: 3 equal nodes of 64px
- PASS  act 2: min unit-unit centre distance 38.58 >= 36
- PASS  act 2: min unit-node gap 8.2 px, no overlap
- PASS  act 3: 15 units d36, 5 blue / 5 orange / 5 grey
- PASS  act 3: 3 equal nodes of 64px
- PASS  act 3: min unit-unit centre distance 105.8 >= 36
- PASS  act 3: min unit-node gap 34.2 px, no overlap
- PASS  act 3 N1: 5 units, 3 colours
- PASS  act 3 N2: 5 units, 3 colours
- PASS  act 3 N3: 5 units, 3 colours
- PASS  act 1: all 15 units route to the single centre node N2
- PASS  act 1: both idle nodes receive nothing (zero links, by construction)
- PASS  act 2: all 15 units route to the single centre node N2
- PASS  act 2: both idle nodes receive nothing (zero links, by construction)
- PASS  rationale narrative is 233 characters (<= 300)
- PASS  composition preview retained in temp: preview-a-v01.png
- PASS  composition preview retained in temp: preview-b-v01.png
- PASS  composition B DSL retained in temp as preview-b.snapshot (rendered once as preview-b-v01.png and never regenerated)
- PASS  requests.jsonl has 12 rows (9 x 200, 3 x 400)
- PASS  iterations.jsonl has 21 rows
- PASS  iterations log present in temp
- PASS  17 logged view events
- PASS  the delivered PNG was opened 4 time(s) with a real image tool
- PASS  3 400px thumbnail view event(s) logged
- PASS  13 visual iterations
- PASS  every failed response body is retained
- PASS  task-metrics request count matches the log
- PASS  task-metrics iteration count matches the log
- PASS  unknown cost recorded as null, not guessed

## Deliverables

- `final-audit.md` (4090 B)
- `rationale.md` (2290 B)
- `snapshot-usage.md` (9828 B)
- `story-audit.json` (35862 B)
- `task-metrics.json` (23434 B)
- `three-act-story.png` (97982 B)
- `three-act-story.snapshot` (40989 B)

## Temp artefacts retained

- 12 `.snapshot` DSL files (4 probes, composition A v01-v06, composition B v01, the recovered v01)
- 14 PNG files (8 composition/refinement previews + 1 probe + 5 thumbnails)
- `geom-a.json` / `geom-a-v01.json` / `geom-b.json`, `gen.ps1`, `gen-v01.ps1`, `mk-audit.ps1`, `thumb.ps1`
- 3 failure response bodies under `failures/`

## Known residuals

- At 400px the three act labels are present, correctly placed and the three bands read as three distinct states, but their dense CJK strokes are about 7px tall and need magnification to read character by character. They are 30px and fully legible at full size, and were grown from 26px to 32px specifically to close this gap.
- The act-2 centre node capsule port splits the node white ring into two bars at 400px; this is a thumbnail artefact of a deliberate full-size feature.
- Token and cost figures were never observed and remain null.
