"""Correct the complete_visual_iteration flag for A06-v05 (byte-identical DSL -> not a
new visual cycle) and regenerate task-metrics.json + the suite task record.

iterations.jsonl is append-only in normal use; this is a one-off correction of a flag
written minutes ago in the same session, applied in place and logged as an event.
Nothing is deleted: the correction is recorded in the record itself.
"""
import io
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import finalize  # noqa: E402
import state as S  # noqa: E402
import snapkit  # noqa: E402

IT = os.path.join(S.TMP_ROOT, "A06", "iterations.jsonl")
rows = [json.loads(l) for l in io.open(IT, encoding="utf-8") if l.strip()]
changed = []
for r in rows:
    if r["iteration_id"] == "A06-v05":
        r["complete_visual_iteration"] = False
        r["note"] = ("DSL is byte-identical to A06-v04 (sha256 prefix 13b6f7f47932426b), so "
                     "this re-render is a provenance record for the delivered PNG, not a new "
                     "visual iteration")
        changed.append(r["iteration_id"])
with io.open(IT, "w", encoding="utf-8", newline="\n") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print("flag corrected for:", changed)

m = finalize.build('A06', '2026-10-04T22:05:00+08:00', '2026-10-04T22:09:00+08:00',
                   '2026-10-04T22:41:00+08:00')
S.finish_task(
    'A06', 'completed',
    artifacts=['dependency-map.png', 'dependency-map.snapshot', 'graph-audit.json',
               'snapshot-usage.md', 'task-metrics.json'],
    visual_evidence=[
        'dependency-map.png whole-image review after every render (v01, v02, v03, v04, v05 '
        '= 5 full-image views)',
        'crops/dependency-map-n08-feedback.png - 2.6x zoom of the N08 junction that exposed '
        'the inverted arrowheads and the two merged feedback arrow tips',
        'crops/dependency-map-n01-fork.png - 2.2x zoom of the N01/N02 fork: both outgoing '
        'arrowheads and the N02->N04 vertical confirmed',
        'crops/dependency-map-n06-converge.png - 2.6x zoom confirming N05->N06 and N03->N06 '
        'enter N06 on separate ports without crossing',
        'crops/dependency-map-f1-loop.png - 3.0x zoom confirming the F1 left-pointing tip '
        'enters the N08 right border and the leader meets its channel',
        'crops/dependency-map-n13-arrive.png - 2.8x zoom that showed the N04->N13 arrowhead '
        '11px short of the N13 border (fixed in v03)',
        'crops/dependency-map-direct-label.png then -direct-label2.png - 3.0x zooms of the '
        '直接校验 label before and after the leader/label separation fix',
        'crops/dependency-map-layer-panel.png then -panel-bottom.png - 2.6x / 3.0x zooms that '
        'exposed then verified the panel bottom overflow',
        'crops/dependency-map-header.png and -footer.png - 1.6x zooms verifying title, '
        'subtitle, right-hand note, two-row legend, both explanation cards, both footnotes',
    ],
    unresolved=[
        'the class-DOM DSL exposes no line/path primitive, so edges are runs of small '
        'rectangles; the steepest diagonal (N06->N08, 380px across 24px) shows a faint '
        'staircase at 2.6x zoom. It changes no direction, endpoint, layer or count claim. '
        'Presumed cause: no CustomPaint/path tag is exposed (I stayed inside the capability '
        'list in the handbook instead of guessing tag names)',
        'arrowheads are stacks of shrinking rectangles, so their sloped sides have ~1px steps '
        'at 3x zoom - same underlying limitation',
        'shallow diagonals into a node top (N03->N06, N05->N06, N12->N13) end in a small '
        'vertical down-arrowhead rather than a rotated one; Transform/matrix was not used '
        'because the handbook flags unverified semantics as needing a probe image first, and '
        'the direction reading is unambiguous without it',
        'the "直接校验：数据不经过渲染回路" label sits beside the x=160 corridor rather than next '
        'to N13, chosen because it makes the detour itself legible; deliberate trade-off',
        'token counts, image input usage, cost and server-side queue time are not exposed by '
        'the service and are recorded as null; they were never estimated',
        'no 429/503 occurred, so rate_limit_or_queue_wait_seconds is null rather than 0',
    ],
    rounds=['round-01'],
    cases=[],
    notes='11 topological layers laid out vertically so all 16 prerequisite edges strictly '
          'descend and none can point back to an earlier layer (asserted per edge). Longest '
          'prerequisite path = 11 nodes / 10 edges with 2 equal-length solutions, both listed. '
          'Zero geometric crossings by giving every same-source / same-target pair its own '
          'port; F1 uses the right channel x=950 and F2 the left channel x=560. '
          'graph-audit.json carries the layering, per-node in/out neighbours, longest path and '
          'the pixel geometry of each feedback edge. Counting note: 6 render requests '
          '(1 syntax 400, 5 images), 5 versions viewed, 3 complete visual iterations '
          '(v01>v02, v02>v03, v03>v04); v05 re-rendered a byte-identical DSL only to tie the '
          'delivered PNG to the run that produced the computed audit JSON, so it is logged '
          'as viewed but not as a new visual iteration.')
print(json.dumps(m['counts'], ensure_ascii=False, indent=1))
S.event('a06_iteration_flag_corrected', {'iteration_id': 'A06-v05',
                                         'reason': 'byte-identical DSL, not a new visual cycle'})
