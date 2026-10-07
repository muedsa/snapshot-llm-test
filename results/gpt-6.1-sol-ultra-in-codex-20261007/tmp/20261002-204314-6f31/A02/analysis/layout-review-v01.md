# A02 independent data and layout review

Read A02 TASK.md, AGENTS.md, task.json, run-config.json and inputs agenda.csv, venues.json, README.md. Root suite rules and same run_id apply. This subagent did not render or view a PNG.

## Input audit

15 sessions: A6, B4, C5. Meeting totals A265min, B245min, C210min. Full09:00–16:00 axis420min. Public lunch is separate12:00–13:00,60min per venue. Ordinary non-lunch idle minutes: A95, B115, C150. No venue overlaps, shared-speaker overlaps, or lunch overlaps. Different-room simultaneous talks are allowed; do not report them as conflicts.

| ID | Venue | Time | Duration/min | Category |
|---|---|---|---:|---|
| S01 | A | 09:00–09:40 | 40 | 主旨 |
| S02 | B | 09:00–09:55 | 55 | 工作坊 |
| S03 | C | 09:15–10:00 | 45 | 分享 |
| S04 | A | 10:00–10:45 | 45 | 分享 |
| S05 | B | 10:10–11:10 | 60 | 工作坊 |
| S06 | C | 10:15–10:50 | 35 | 演示 |
| S07 | A | 11:00–11:50 | 50 | 圆桌 |
| S08 | C | 11:05–11:45 | 40 | 分享 |
| S09 | A | 13:00–13:50 | 50 | 分享 |
| S10 | B | 13:00–14:15 | 75 | 工作坊 |
| S11 | C | 13:20–14:00 | 40 | 分享 |
| S12 | A | 14:10–15:00 | 50 | 分享 |
| S13 | C | 14:20–15:10 | 50 | 圆桌 |
| S14 | B | 14:35–15:30 | 55 | 工作坊 |
| S15 | A | 15:30–16:00 | 30 | 主旨 |

Raw gaps (including lunch when a meeting gap spans it): A09:40–10:00/10:45–11:00/11:50–13:00/13:50–14:10/15:00–15:30. B09:55–10:10/11:10–13:00/14:15–14:35/15:30–16:00. C09:00–09:15/10:00–10:15/10:50–11:05/11:45–13:20/14:00–14:20/15:10–16:00. An audit may retain raw gaps with includes_public_lunch or split into ordinary gaps plus separate lunch; do not double-count.

## Wide arrangement, 1920×1200

Use horizontal time x200–1840, width1640,09:00–16:00(420min), so3.9047619048px/min. Three lanes may be y246/390/534 with116px activity height. Header and capacity labels remain outside blocks. Lunch spans x902.8571429–1137.1428571 across all3lanes; label explicitly12:00–13:00公共午休. Retain15-minute initial C gap and end gaps; each block exact start/end.

Blocks contain ID and readable time/duration only. Full title/speaker/category/venue/time is in the linked ID index below the timeline. At width1640, the30min shortest block is117.142857px; a Chinese title cannot fit at body20 without distorting length. An external complete index solves this honestly.

Full index: x64/668/1272,width584,5 entries per column. Title at22px, metadata+speaker20px (time may18px). Rows start748 and repeat80px, final box bottom1148. A3×5 index covers all15 IDs; assigning sequential S01–S05/S06–S10/S11–S15 avoids unequal per-venue row counts. Add reading method above or below chart: “横向位置与块长对应时间；留白为空档；编号检索下方标题与讲者。” This text body20 or larger. Capacities A320人/B80人/C160人.

10:00 dense-area exact geometry using proposed x-axis: S03 C ends at434.285714; S04 A starts434.285714, width175.714286; S05 B starts473.333333,width234.285714; S06 C starts492.857143,width136.666667. They are in different lanes; neither overlap nor need time correction. Keep outside callouts confined to their own lane/index, with no connector crossing another lane's labels.

## Mobile arrangement, 720×1280

Reorder into chronological list; do not shrink/crop wide output. Margin24 gives672px text width. Header y24–136: name28,date/location18–20,timezone18. Morning heading y150–176;8rows starting184,60px each through664. Separate lunch y674–722. Afternoon heading y734–760;7rows starting766,60px each through1186. Footer y1214–1250 must include exact “讲者详见完整日程”.

Each activity row has title line20px: `S01 开场：结构如何成为画面`; metadata line18px: `09:00–09:40 · A会场 · 主旨`. Full15 titles,IDs,venues,start/end retained. No speaker required on mobile because footer provides full-schedule reference. Display timezone/location/date completely. Keep lunch independent betweenS08 andS09. All mobile body≥18; headings≥20.

## Required actual visual acceptance

Producer/root must inspect both real service PNGs at native size, especially timeline near10:00, shortestS15 andS06 blocks, lunch boundary, final16:00 tick, entire15-item index and phone finalS15/footer. Static audit does not verify font wrapping/clipping. Actual chosen axis coordinates must replace advisory geometry in delivered schedule-audit.json.
