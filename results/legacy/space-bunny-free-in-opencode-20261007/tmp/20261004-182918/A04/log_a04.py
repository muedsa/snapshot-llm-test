import json
import os
import sys

sys.path.insert(0, r'tmp\20261004-182918\_suite')
import finalize  # noqa: E402
import state as S  # noqa: E402
import snapkit  # noqa: E402

TASK = 'A04'
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), os.path.join(S.TMP_ROOT, TASK))
ROWS = [
    ('A04-v01', 'none', 'baseline', 'build-a04.snapshot', 'conversion-story.png',
     '2026-10-04T20:52:00+08:00',
     'first submission rejected: BorderStyle has no DASHED constant, so the ghost-bar outline '
     'in panel 3 could not be expressed',
     'none (service refused the document)', False),
    ('A04-v02', 'A04-v01', 'syntax-fix', 'build-a04.snapshot', 'conversion-story.png',
     '2026-10-04T20:55:00+08:00',
     'rendered, but panel 1 bottom line was clipped, panel 2 period labels collided with the '
     'legend chips and the count line overflowed the card, and the composition subtitle read '
     'vaguely',
     'looked up reference/enums and confirmed BorderStyle is only NONE/SOLID, so the dash is now '
     'drawn as explicit rectangle segments; panel 1 delta line shortened to the two pp values; '
     'panel 2 period name and counts moved onto one line above each bar with the unit added to the '
     'subtitle', False),
    ('A04-v03', 'A04-v02', 'visual', 'build-a04.snapshot', 'conversion-story.png',
     '2026-10-04T21:00:00+08:00',
     '2x zoom of panel 2 showed the period name and the count line were half-covered by the bar, '
     'because the bar was appended after the text; the counterfactual in analysis.json also '
     'turned out to equal the overall rate itself, which proved the formula was wrong',
     'reordered so the bar is drawn first and lifted both text lines fully above the bar top; '
     'fixed the counterfactual to early-mix x late-rates = 30.40% and added the second one = 14.00%',
     False),
    ('A04-v04', 'A04-v03', 'visual', 'build-a04.snapshot', 'conversion-story.png',
     '2026-10-04T21:06:00+08:00',
     '2.4x zoom of the verification table bottom row confirmed the descenders were intact but sat '
     'very close to the card edge; panel 3 second legend chip nearly touched the card edge',
     'table row pitch 29->27 and start 614->610; panel 3 legend text shortened', True),
]
for v, par, kind, dsl, img, viewed, obs, chg, complete in ROWS:
    snapkit.log_iteration(
        version=v, parent=par, kind=kind, dsl_file=dsl, image_file=img, viewed_at=viewed,
        observed=obs, changes=chg,
        compared=('accepted' if complete else 'not accepted'), complete=complete)

m = finalize.build(TASK, '2026-10-04T20:50:00+08:00', '2026-10-04T20:55:00+08:00',
                   '2026-10-04T21:08:00+08:00')
print(json.dumps(m['counts'], ensure_ascii=False, indent=1))
print('failures:', len(m['failures']))
S.finish_task(TASK, 'completed',
              artifacts=['conversion-story.png', 'conversion-story.snapshot', 'analysis.json',
                         'snapshot-usage.md', 'task-metrics.json'],
              visual_evidence=[
                  'conversion-story.png whole-image review after each rebuild',
                  '2x zoom of the composition panel',
                  '2x zoom of the overall-comparison panel',
                  '2.4x zoom of the verification table bottom row'],
              unresolved=['the dashed connector between the two ghost average bars in panel 3 is '
                          'very faint; it is decorative only and the semantics are carried by the '
                          'grey outline, the legend wording and the table annotation'],
              rounds=['round-01'],
              notes='grouped rates + composition + overall on one 0-100% scale; overall always '
                    'total/total; Kitagawa decomposition +9.40pp identity checked')
print('A04 state updated')