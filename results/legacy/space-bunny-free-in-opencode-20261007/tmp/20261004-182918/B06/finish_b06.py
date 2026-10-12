import json
import os
import sys

sys.path.insert(0, r'tmp\20261004-182918\_suite')
import wrapup  # noqa: E402

CASES = ['case-%02d' % i for i in range(1, 11)]
m = wrapup.wrapup(
    'B06', '2026-10-05T19:40:00+08:00', '2026-10-05T20:12:00+08:00', '2026-10-05T21:30:00+08:00',
    iterations=[],
    artifacts=[('%s/final.png, %s/final.snapshot, %s/case.md' % (c, c, c)) for c in CASES] + [
        'portfolio.json', 'portfolio.md', 'gallery.html', 'problem-evidence.json',
        'design-review.md', 'snapshot-usage.md', 'task-metrics.json'],
    visual_evidence=[
        'all 10 final.png opened one by one with the image reader',
        'case-08 opened after the layout rebuild: both the net-amount curve (right axis) and the '
        'net-ratio curve (left axis) are visible and agree with the printed tax table',
        'case-01 opened to confirm the unit-price ruler metaphor and the real Consumer Council '
        'figures match what is printed'],
    unresolved=[
        'the session context was interrupted several times; iterations.jsonl was converted from '
        'the retained iteration-notes.jsonl (26 rows, 17 complete visual iterations)',
        'draft version numbers restart per process, so a few intermediate drafts were overwritten '
        'and cannot be restored verbatim; requests.jsonl / responses/ remain complete',
        'token / image input usage / cost are null - the service and platform expose no metrics',
        'gallery.html was not opened in a real browser (no browser in the sandbox); it was '
        'verified to use only relative paths, zero remote references and zero script tags'],
    cases=CASES,
    notes='10 everyday information problems, each researched first and rendered as a full sheet; '
          'no external bitmaps at all; every printed figure comes from the same script that '
          'produced problem-evidence.json')
print(json.dumps(m['counts'], ensure_ascii=False, indent=1))