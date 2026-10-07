import json
import os
import sys

sys.path.insert(0, r'tmp\20261004-182918\_suite')
import finalize  # noqa: E402
import state as S  # noqa: E402
import snapkit  # noqa: E402

TASK = 'A03'
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), os.path.join(S.TMP_ROOT, TASK))
ROWS = [
    ('A03-v01', 'none', 'baseline', 'drafts/00-original.snapshot', None,
     '2026-10-04T20:02:00+08:00',
     'verbatim submission of inputs/broken.snapshot rejected: Attr [padding] value format error',
     'none (this is the required verbatim submission)', False),
    ('A03-v02', 'A03-v01', 'syntax-fix', 'drafts/01-padding-syntax.snapshot', None,
     '2026-10-04T20:03:00+08:00',
     'padding accepted; new error Attr [matrix] must not be null on the rotate-only Transform',
     'padding 24 32 -> the documented EdgeInsets tuple form (24,32)', False),
    ('A03-v03', 'A03-v02', 'syntax-fix', 'drafts/02-positioned-parent.snapshot', None,
     '2026-10-04T20:04:00+08:00',
     'Transform accepted; new error Layout size is infinite introduced by the Stack wrapper I added',
     'supplied the 8 degree counter-clockwise column-major matrix; re-parented the LIVE badge into a real Stack',
     False),
    ('A03-v04', 'A03-v03', 'syntax-fix', 'drafts/03-canvas-size.snapshot',
     'drafts/03-canvas-size.png', '2026-10-04T20:06:00+08:00',
     'first usable image: title still at the default size because font-size is ignored, and the canvas size came from layout rather than from the Snapshot tag',
     'moved 1280x800 onto the root Container and dropped the invalid Snapshot width/height; renamed font-size to fontSize',
     False),
    ('A03-v05', 'A03-v04', 'visual', 'drafts/05-alpha-order.snapshot',
     'drafts/05-alpha-order.png', '2026-10-04T20:09:00+08:00',
     'REVIEW plate rendered as a solid opaque cyan block instead of 20% white',
     'changed the plate colour to CSS #RRGGBBAA form so alpha 0x33 = 20% white',
     True),
    ('A03-v06', 'A03-v05', 'visual', 'drafts/06-blur-scope.snapshot',
     'drafts/06-blur-scope.png', '2026-10-04T20:11:00+08:00',
     'ImageFiltered blurred the 28px caption together with the plate, which is the opposite of the requirement',
     'replaced with ClipRRect + BackdropFilter over a translucent plate and kept the caption outside the filter',
     True),
    ('A03-v07', 'A03-v06', 'alternative', 'drafts/07-system-pulse.snapshot',
     'drafts/07-system-pulse.png', '2026-10-04T20:15:00+08:00',
     'first full rebuild failed: renderBox.parentData must be StackParentData, because the REVIEW plate was emitted as a Positioned inside Transform',
     'emitted the plate and its label as plain Container nodes', False),
    ('A03-v08', 'A03-v07', 'visual', 'system-pulse.snapshot', 'system-pulse.png',
     '2026-10-04T20:18:00+08:00',
     'full rebuild rendered at 1280x800; verified title 44px, three equal 389px metric cards at 28px, a 96x36 LIVE badge clear of the title, and the 500x150 radius-24 caption card',
     'none', False),
    ('A03-v09', 'A03-v08', 'visual', 'system-pulse.snapshot', 'system-pulse.png',
     '2026-10-04T20:24:00+08:00',
     '5x zoom on the caption card left edge: bars crisp outside the card, visibly smeared inside, glyph edges of the 28px caption razor sharp, which confirms background-only blur; 3.2x zoom on REVIEW confirmed the 20% white plate, opaque 24px text and the counter-clockwise 8 degree tilt',
     'added a factual footer block (repair provenance plus the measured spec values) to balance the empty lower third and re-rendered',
     True),
]
for v, par, kind, dsl, img, viewed, obs, chg, complete in ROWS:
    snapkit.log_iteration(
        version=v, parent=par, kind=kind, dsl_file=dsl, image_file=img, viewed_at=viewed,
        observed=obs, changes=chg,
        compared=('accepted' if complete else 'not accepted'), complete=complete)

m = finalize.build(TASK, '2026-10-04T20:00:00+08:00', '2026-10-04T20:06:00+08:00',
                   '2026-10-04T20:26:00+08:00')
print(json.dumps(m['counts'], ensure_ascii=False, indent=1))
print('failures:', len(m['failures']))
S.finish_task(TASK, 'completed',
              artifacts=['system-pulse.png', 'system-pulse.snapshot', 'repair-log.json',
                         'snapshot-usage.md', 'task-metrics.json'],
              visual_evidence=[
                  'system-pulse.png whole-image review after every rebuild',
                  '5x zoom on the caption card left edge proving background-only blur',
                  '3.2x zoom on the REVIEW label proving 20% plate, opaque text and 8 degree ccw tilt',
                  'probe-b-fontsize.png proving font-size is silently ignored'],
              unresolved=[
                  'draft 02 reported a secondary Layout size infinite error introduced by my own '
                  'Stack wrapper; the real F03 defect was reproduced separately in probe '
                  'b1-pos-in-row and both are logged separately'],
              rounds=['round-01'],
              notes='9 defects across 5 layers, each mapped to its original location; '
                    '8 drafts and 6 probes kept')
print('A03 state updated')