import json
import sys

sys.path.insert(0, r'tmp\20261004-182918\_suite')
import wrapup  # noqa: E402

m = wrapup.wrapup(
    'A05', '2026-10-04T21:22:00+08:00', '2026-10-04T21:24:00+08:00', '2026-10-04T21:34:00+08:00',
    iterations=[
        ('A05-v01', 'none', 'baseline', 'build-a05.snapshot', 'sensor-report.png',
         '2026-10-04T21:24:00+08:00',
         'baseline: all three panels rendered but the per-panel title bands collided with the '
         'previous panel bottom tick labels, neighbouring value labels overlapped '
         '(19.2/19.6, 23.1/22.8, 41/40, 0.4/0.2), the zero-line caption fell outside the canvas '
         'and the last x-axis label overflowed the right edge',
         'none (first render)', False),
        ('A05-v02', 'A05-v01', 'visual', 'build-a05.snapshot', 'sensor-report.png',
         '2026-10-04T21:27:00+08:00',
         'plot area moved right to x=268 so the left gutter can host four label rows per panel; '
         'data labels now alternate above/below when neighbours are closer than 74px and clamp to '
         'the plot edges; the zero caption became a bold 0 kPa tick label; the x-axis label row is '
         'clamped inside the canvas',
         'all title/tick collisions and label overlaps gone; line breaks at 09:15, 11:40 (temp) '
         'and 09:40 (humidity) confirmed', False),
        ('A05-v03', 'A05-v02', 'visual', 'build-a05.snapshot', 'sensor-report.png',
         '2026-10-04T21:30:00+08:00',
         '2.6x zoom of the negative band showed the red band edges crossing the -0.2 / -0.8 / -0.3 '
         'value labels, and the two-line band caption sat on top of the 10:10 edge',
         'moved the band highlight and its edges to be drawn before the gridlines so lines, '
         'markers and labels all sit on top; nudged labels that land on a band edge by 24px; '
         'collapsed the band caption to one centred line in the gap above the pressure plot', False),
        ('A05-v04', 'A05-v03', 'visual', 'build-a05.snapshot', 'sensor-report.png',
         '2026-10-04T21:33:00+08:00',
         '2.6x zoom confirmed all three negative-sample labels are now clear of the band edges; '
         '1.9x zoom of the temperature panel confirmed the two missing-sample gaps are drawn as '
         'genuine breaks with no interpolation; the 12-row detail table and the legend are complete',
         'none needed', True),
    ],
    artifacts=['sensor-report.png', 'sensor-report.snapshot', 'normalized-data.json',
               'snapshot-usage.md', 'task-metrics.json'],
    visual_evidence=[
        'sensor-report.png whole-image review after each rebuild',
        '1.9x zoom of the temperature panel showing both missing-sample line breaks',
        '2.6x zoom of the negative pressure band before and after the draw-order fix'],
    unresolved=['lines are drawn as runs of short rectangles because the class-DOM DSL has no '
                'line primitive; the steepest segment (09:15->09:40, 1.3 to -0.2 kPa) shows a '
                'faint staircase when zoomed, which does not affect any value or interval claim'],
    notes='12 irregularly spaced samples on one shared real-time axis; 3/2/1 connected segments '
          'for temperature/humidity/pressure; the negative annotation is limited to the two '
          'segments whose endpoints are both negative, with the two zero-crossing segments called '
          'out separately')
print(json.dumps(m['counts'], ensure_ascii=False, indent=1))
print('failures:', len(m['failures']))