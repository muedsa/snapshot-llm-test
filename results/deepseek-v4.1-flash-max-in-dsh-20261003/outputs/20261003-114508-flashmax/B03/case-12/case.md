# case-12 · Tide & light planner · Halloway Rowing Club

- **Final render**: `final.png` (raw bytes of a 200 `image/png` response), from `tmp/20261003-114508-flashmax/B03/renders/case-12.v4.png`
- **DSL**: `final.snapshot` — version `v4`, self-contained, no external assets
- **Audience**: A coastal rowing club's coxswains and coaches
- **Use context**: A wall sheet in the boathouse, read before an outing
- **User goal**: Choose the day and the hour: enough water, enough light, high water inside daylight
- **Content basis**: 7 day tide curves, 28 high/low water entries, daylight windows and moon phases; all predictions come from a two-constituent harmonic generator and are explicitly not for navigation
- **Visual intent**: Deep-water dark palette, one row per day, an area-filled tide curve, an aligned high/low table, daylight bars with twilight hatch, moon discs
- **DSL capabilities used**: one generator driving curves and the derived table, area fill from stacked columns, aligned multi-column matrix, moon phase from overlapping discs
- **Completion criteria (self-set)**: curves and table always agree; seven rows stay visually separate; the daylight bars fit the sheet
- **Visual review evidence**: v1 daylight bars ran to x=1850 on a 1700 px sheet and the curve scalloped at a 4 px step; v2 re-measured every column and halved the step; v3 added row banding and a baseline rule so the seven rows read separately
- **Fictional-data note**: the subjects, brands, people, places and numbers in this work are invented demo content for a DSL study. No real client, organisation, person or measurement is depicted or implied.
- **Supporting assets**: none. The artwork is pure DSL; no photograph, bitmap or embedded `Image` is used, and no post-processing was applied to the returned PNG.
- **Rejected attempts kept**: none
- **Unresolved issues**: none
