import sys

sys.path.insert(0, r'tmp\20261004-182918\_suite')
import wrapup  # noqa: E402

m = wrapup.wrapup(
    'A20', '2026-10-04T21:52:00+08:00', '2026-10-04T21:56:00+08:00', '2026-10-04T22:06:00+08:00',
    iterations=[
        ('A20-v01', 'none', 'baseline', 'build-a20.snapshot', 'annotated-map.png',
         '2026-10-04T21:56:00+08:00',
         'first submission rejected: Attr [color] must be #RGB/#RGBA/#RRGGBB/#RRGGBBAA - the marker '
         'halo was built by concatenating a 8-digit colour with an alpha suffix (10 digits)',
         'none (service refused the document)', False),
        ('A20-v02', 'A20-v01', 'syntax-fix', 'build-a20.snapshot', 'annotated-map.png',
         '2026-10-04T21:58:00+08:00',
         'rendered, but the self-audit reported 4 leader-line crossings (limit 3) and the full '
         'image showed the y-axis tick labels half-covered by the left label column and the '
         'leader lines drawn as dotted runs',
         'halo colour given its own 8-digit value; search space widened from side-assignment '
         'only to side-assignment plus within-column adjacent swaps with 12 restarts (3672 '
         'evaluations) which drove crossings to 0; y tick labels moved inside the map rect; '
         'leader segments given slope-dependent box sizes so they join up',
         False),
        ('A20-v03', 'A20-v02', 'visual', 'build-a20.snapshot', 'annotated-map.png',
         '2026-10-04T22:01:00+08:00',
         '2.2x zoom of the dense centre showed the leaders still slightly dashed on shallow '
         'segments; a finer step (L/3) pushed the document past the service element cap',
         'service returned 400 RENDER_ERROR: Document contains more than 4096 elements - this '
         'cap had not been hit before, so the step was relaxed to L/5 giving 4065 elements',
         False),
        ('A20-v04', 'A20-v03', 'visual', 'build-a20.snapshot', 'annotated-map.png',
         '2026-10-04T22:05:00+08:00',
         '2.2x zoom of the dense centre confirmed the five 8px markers (M08-M12) are separated '
         'and every leader is continuous to its own anchor; full-image review confirmed 24 '
         'readable labels, zero box intersections, zero crossings, axis range, unit and the '
         'smallest three points all present',
         'none needed', True),
    ],
    artifacts=['annotated-map.png', 'annotated-map.snapshot', 'label-layout.json',
               'layout-audit.json', 'snapshot-usage.md', 'task-metrics.json'],
    visual_evidence=[
        'annotated-map.png whole-image review after each rebuild',
        '2.2x zoom of the dense centre (5 shrunk markers plus their leader lines)'],
    unresolved=['leader lines keep a faint staircase at 2.2x zoom because they are assembled '
                'from rectangles and the service caps documents at 4096 elements (4065 used); '
                'invisible at 1x'],
    notes='24 markers on a 0-100 logical map with a single y inversion; 0 label-box '
          'intersections, 0 leader crossings, 0 lines crossing other labels; the service 4096 '
          'element cap was discovered and documented')
print(m['counts'])