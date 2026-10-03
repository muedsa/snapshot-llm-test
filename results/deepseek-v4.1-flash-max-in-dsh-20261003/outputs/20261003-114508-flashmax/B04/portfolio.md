# B04 · The Antarctic ozone hole: what the 47-year record actually shows

A ten-work visual special. Every `final.png` is the raw byte stream of a live HTTP 200 `image/png` response from `https://open-snapshot.muedsa.com/snapshot`; the matching `final.snapshot` is the exact text that produced it.

## Curatorial logic

Ten works about one real subject, edited so that each answers a different question a reader would actually ask: what counts as the hole, did it stop growing, how deep is it, did the season move, why there, what was agreed, what happens when a banned gas comes back, what did it do for the climate, what did it prevent, and what is still open. The style is deliberately unified — one masthead, one palette family, one source-footer convention — because this is a single issue of one publication, and the independence that matters here is independence of question and of chart form, not of look. The ten structures are: annotated cross-section, column chart with a treaty rail, plumb-line depth chart on an inverted axis, calendar strip matrix, four-panel process strip, alternating chronology, case file, paired-claim ledger, cost/benefit ledger with big-number panels, and an uncertainty ledger.

## The works

| # | Work | Question it answers | Structure | Size | Sources |
|---|---|---|---|---|---|
| 01 | What the hole is | What actually counts as the ozone hole? | annotated atmospheric cross-section + definition panels | 1240×1754 | S2, S3 |
| 02 | The 47-year record | Did the hole stop growing? | 46-column chart with a five-year trailing mean and a treaty rail | 1900×1180 | S1, S4 |
| 03 | Depth | How little ozone is left inside the hole? | plumb lines hanging from the 220 DU threshold, inverted axis | 1800×1140 | S1, S2 |
| 04 | One hole per year | Did the season move, or only the size? | calendar strip: one row per year, marker at the peak date, bar for the peak area | 1700×1480 | S1, S2 |
| 05 | Four stages | Why does this happen over one pole, in one season? | four-panel process strip, identical geometry in every panel | 1880×1080 | S2, S3 |
| 06 | The treaty rail | What was actually agreed, and in what order? | horizontal chronology with alternating decision cards + outcome strip | 1880×940 | S5, S4, S6 |
| 07 | The rogue emitter | What happened when a banned gas stopped falling? | case file: finding, cost, what it demonstrates, what is not shown | 1360×1310 | S5 |
| 08 | The climate side-effect | What did an ozone treaty do about warming? | four paired claims with the counterfactual named beneath | 1840×1120 | S4, S5 |
| 09 | The health ledger | What is the treaty credited with preventing? | ledger: three modelled health totals, then cost against benefit | 1600×1150 | S4 |
| 10 | What is still open | What does the assessment still not settle? | six-item uncertainty ledger with editorial confidence chips | 1840×1180 | S5 |

## Research trail

Six sources were fetched and read on 2026-10-03, each recorded in [sources.json](sources.json) with its URL, access time, HTTP status and exactly what it contributes:

- **S1** — [NASA Ozone Watch — Annual Records (Antarctic)](https://ozonewatch.gsfc.nasa.gov/meteorology/annual_data.html) (NASA Goddard Space Flight Center), used by case-02, case-03, case-04
- **S2** — [NASA Ozone Watch — What is the Ozone Hole?](https://ozonewatch.gsfc.nasa.gov/facts/hole_SH.html) (NASA Goddard Space Flight Center), used by case-01, case-03, case-04, case-05
- **S3** — [NASA Ozone Watch — What is Ozone?](https://ozonewatch.gsfc.nasa.gov/facts/SH.html) (NASA Goddard Space Flight Center), used by case-01, case-05
- **S4** — [Facts and figures on ozone protection](https://ozone.unep.org/facts-and-figures-ozone-protection) (UN Environment Programme, Ozone Secretariat), used by case-02, case-06, case-08, case-09
- **S5** — [Scientific Assessment of Ozone Depletion: 2022 — Executive Summary](https://www.csl.noaa.gov/assessments/ozone/2022/executivesummary/) (WMO/UNEP Scientific Assessment Panel, GAW Report No. 278 (hosted by NOAA Chemical Sciences Laboratory)), used by case-02, case-06, case-07, case-08, case-10
- **S6** — [The Kigali Amendment: An overview](https://ozone.unep.org/kigali-amendment-overview) (UNEP Ozone Secretariat), used by case-06

## What is not data

The masthead name, issue number and editor byline are invented cover furniture. Nothing else is invented: every figure is transcribed from a source, computed from it, or printed as a published estimate with that label. The two schematic works (01, 05) say on the artwork that they plot no measured values. Full declaration in [editorial-note.md](editorial-note.md).

## Review

Reviewed all ten at full size and as a contact sheet. Every figure printed was checked against scripts/ozone.py or the source notes in research/ before the sheet was accepted. Defects found and fixed after looking: a broken radial calendar (case-04 v1), a picket-fence polyline (case-03 v1-v2), a masthead standfirst overprinted by the kicker (case-02 v1, shared helper fix), a clipped list label (case-02 v2), annotation boxes over the header (case-02 v1), unit labels colliding with their values (case-06 v1), benefit labels running off the canvas (case-09 v1-v2), implied-but-meaningless bar scales (case-08 v1) and two half-empty canvases (case-06, case-07). Known limits: only six secondary sources were read, the Arctic is covered only where the sources compare it, and the CFC-11 episode is reported without its emissions series.

## Known limits

- No measurement-level CFC-11 series was obtained, so that episode is reported qualitatively with only the assessment's delay estimates as numbers.
- The Kigali party count differs between two Secretariat pages (over 160 as of October 2024; more than 170 as of February 2026); the newer figure is printed and the discrepancy is recorded in sources.json.
- Arctic ozone is covered only where the sources compare it with the Antarctic; no Arctic-specific chart is drawn.
