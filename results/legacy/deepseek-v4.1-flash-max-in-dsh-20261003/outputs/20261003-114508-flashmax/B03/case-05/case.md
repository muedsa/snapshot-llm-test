# case-05 · Drum seismogram · station HLY

- **Final render**: `final.png` (raw bytes of a 200 `image/png` response), from `tmp/20261003-114508-flashmax/B03/renders/case-05.v2.png`
- **DSL**: `final.snapshot` — version `v2`, self-contained, no external assets
- **Audience**: A seismology duty officer reading an overnight record
- **Use context**: A wide sheet on a monitoring desk, also used as a print
- **User goal**: See the P-wave onset, judge the coda, and read the event parameters
- **Content basis**: three radial drum traces, a 3 line helicorder, an event summary; the event, station and magnitudes are invented
- **Visual intent**: Smoked-paper dark ground, concentric rings with hour marks, green/blue/amber traces, a red onset marker, a helicorder panel
- **DSL capabilities used**: parametric circular geometry, polar helpers, multi-series waveforms, radial tick labels, dash control
- **Completion criteria (self-set)**: the onset marker sits on the trace; no label collides; the helicorder shows quiet vs event
- **Visual review evidence**: v1 traces were dashed (2.1° steps) and the STATUS row collided with the HELICORDER heading; v2 halved the step to 1.55° and moved the panel
- **Fictional-data note**: the subjects, brands, people, places and numbers in this work are invented demo content for a DSL study. No real client, organisation, person or measurement is depicted or implied.
- **Supporting assets**: none. The artwork is pure DSL; no photograph, bitmap or embedded `Image` is used, and no post-processing was applied to the returned PNG.
- **Rejected attempts kept**: `case-05.v2.png.failed.txt`
- **Unresolved issues**: none
