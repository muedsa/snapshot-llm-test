import json
import sys

sys.path.insert(0, r'tmp\20261004-182918\_suite')
import wrapup  # noqa: E402

m = wrapup.wrapup(
    'A06', '2026-10-04T22:05:00+08:00', '2026-10-04T22:09:00+08:00', '2026-10-04T22:41:00+08:00',
    iterations=[
        # --- pre-baseline: the only service error, no image produced ---
        ('A06-v00', 'none', 'syntax-fix', 'build-a06.snapshot', None,
         None,
         'no image yet: HTTP 400 PARSE_ERROR "Attr [color] color must be #RGB, #RGBA, '
         '#RRGGBB or #RRGGBBAA at position 187057" - the phase-3 node tint was written as '
         'the 10-digit #ECFDF5FFFF',
         'shortened it to the 8-digit CSS form #ECFDF5FF (RRGGBBAA)', False),
        # --- baseline: first real image ---
        ('A06-v01', 'A06-v00', 'baseline', 'build-a06.snapshot', 'dependency-map.png',
         '2026-10-04T22:09:00+08:00',
         'whole-image review: (1) every arrowhead triangle was inverted - the widest row sat '
         'at the tip, so the vertical spine edges rendered as diamonds/kites instead of '
         'arrows; (2) both red feedback arrowheads entered the left border of N08 only 12px '
         'apart and merged into one blob; (3) the "直接校验" leader line at y=509 ran straight '
         'through its own label text and read like a strikethrough; (4) the left layer-gutter '
         'background stopped 24px short of row L11; (5) the single legend row consumed 1499px '
         'of the 1536px available and overlapped the right-aligned note',
         'none (baseline render)', False),
        # --- visual iteration 1 ---
        ('A06-v02', 'A06-v01', 'visual', 'build-a06.snapshot', 'dependency-map.png',
         '2026-10-04T22:16:00+08:00',
         '2.6x zoom of the N08 junction confirmed the arrows now point correctly but was read '
         'before this fix; 2.6x zoom of the left corridor showed the "直接校验" leader still '
         'looking like an em-dash because it touched the first glyph; 2.8x zoom of the N13 '
         'junction showed the N04->N13 arrowhead stopping 11px short of N13 left border '
         '(x=1119 vs border 1130) because the route point was short of the border',
         'rewrote tri_down/tri_right so the widest row sits at the base and added tri_left; '
         'moved F1 to the right-hand channel (x=950, enters N08 right border, tip points left) '
         'and kept F2 on the left-hand channel (x=560, enters N08 left border, tip points '
         'right) so the two returns can never cross each other or the solid flow; pushed the '
         'label to x=234 and lengthened its leader to x=163 leaving an 8px gap; gutter height '
         '600->636 so it covers L11; split the legend into two rows of three items (915px '
         'used); footnote colour #94A3B8->#64748B', False),
        # --- visual iteration 2 ---
        ('A06-v03', 'A06-v02', 'visual', 'build-a06.snapshot', 'dependency-map.png',
         '2026-10-04T22:24:00+08:00',
         '2.6x zoom of the right-hand 拓扑分层 panel showed "11 节点 / 10 边" overhanging the '
         'panel bottom border by 2px; 1.6x zoom of the footer showed the "圆点" legend swatch '
         'too small to read as a dot',
         'layer panel height 372->384 so the last line has 10px bottom padding; dot legend '
         'swatch radius 3.4->5; extended the N04->N13 route end to x=1130 so the arrowhead '
         'touches the N13 border; footnote line 2 now also states the x=160 corridor', False),
        # --- visual iteration 3: accepted ---
        ('A06-v04', 'A06-v03', 'visual', 'build-a06.snapshot', 'dependency-map.png',
         '2026-10-04T22:32:00+08:00',
         '3.0x zoom of the left corridor (direct-label2) confirmed the leader and label are '
         'now cleanly separated; 3.0x zoom of the panel bottom confirmed "11 节点 / 10 边" '
         'sits inside the panel; whole-image review counted all 18 arrowheads pointing the '
         'right way, all 14 node cards present, zero geometric crossings and no text overflow',
         'none needed - accepted', True),
        # --- final re-render with identical DSL, Python-side JSON only ---
        ('A06-v05', 'A06-v04', 'retry-equivalent', 'build-a06.snapshot', 'dependency-map.png',
         '2026-10-04T22:38:00+08:00',
         'final whole-image review of the delivered PNG: identical to v04 (byte-identical '
         'DSL, sha256 prefix 13b6f7f47932426b); 14/14 nodes, 18/18 directed arrowheads, '
         'both dashed feedback loops, layer bands L1-L11, legend, two explanation cards and '
         'both footnotes all render correctly',
         'no DSL change; this render exists because graph-audit.json was switched from '
         'hard-coded to genuinely computed values (layering convergence flag, real BFS '
         'reachability, per-edge feedback layer deltas, direction derived from the route)',
         True),
    ],
    artifacts=['dependency-map.png', 'dependency-map.snapshot', 'graph-audit.json',
               'snapshot-usage.md', 'task-metrics.json'],
    visual_evidence=[
        'dependency-map.png whole-image review after every render (v01, v02, v03, v04, v05 '
        '= 5 full-image views)',
        'tmp/20261004-182918/A06/crops/dependency-map-n08-feedback.png - 2.6x zoom of the N08 '
        'junction that exposed the inverted arrowheads and the two merged feedback tips',
        'tmp/20261004-182918/A06/crops/dependency-map-n01-fork.png - 2.2x zoom of the N01/N02 '
        'fork confirming both outgoing arrowheads and the N02->N04 vertical',
        'tmp/20261004-182918/A06/crops/dependency-map-n06-converge.png - 2.6x zoom confirming '
        'N05->N06 and N03->N06 enter N06 on separate ports without crossing',
        'tmp/20261004-182918/A06/crops/dependency-map-f1-loop.png - 3.0x zoom confirming the '
        'F1 left-pointing tip enters the N08 right border and the leader meets its channel',
        'tmp/20261004-182918/A06/crops/dependency-map-n13-arrive.png - 2.8x zoom that '
        'showed the N04->N13 arrowhead 11px short of the N13 border (fixed in v03)',
        'tmp/20261004-182918/A06/crops/dependency-map-direct-label.png and -direct-label2.png - '
        '3.0x zooms of the 直接校验 label before and after the leader/label separation fix',
        'tmp/20261004-182918/A06/crops/dependency-map-layer-panel.png and -panel-bottom.png - '
        '2.6x / 3.0x zooms that exposed and then verified the panel bottom overflow',
        'tmp/20261004-182918/A06/crops/dependency-map-header.png and -footer.png - 1.6x zooms '
        'verifying title, subtitle, right-hand note, two-row legend, both explanation cards '
        'and both footnotes are fully legible and unclipped',
    ],
    unresolved=[
        'the class-DOM DSL exposes no line/path primitive, so edges are runs of small '
        'rectangles; the steepest diagonal (N06->N08, 380px across 24px) shows a faint '
        'staircase at 2.6x zoom. It changes no direction, endpoint, layer or count claim. '
        'Presumed cause: no CustomPaint/path tag is exposed (I stayed inside the capability '
        'list in the handbook rather than guessing tag names)',
        'arrowheads are stacks of shrinking rectangles, so their sloped sides have ~1px steps '
        'at 3x zoom - same underlying limitation',
        'shallow diagonals into a node top (N03->N06, N05->N06, N12->N13) end in a small '
        'vertical down-arrowhead rather than a rotated one; I did not use Transform/matrix '
        'because the handbook flags unknown semantics as needing a probe image first and the '
        'direction reading is unambiguous without it',
        'the "直接校验：数据不经过渲染回路" label sits beside the x=160 corridor rather than next '
        'to N13, chosen because it makes the detour itself legible; deliberate trade-off, not '
        'a defect',
        'token counts, image input usage, cost and server-side queue time are not exposed by '
        'the service and are recorded as null; they were never estimated',
        'no 429/503 occurred, so rate_limit_or_queue_wait_seconds is null rather than 0',
    ],
    notes='11 topological layers laid out vertically so all 16 prerequisite edges strictly '
          'descend and no prerequisite edge can point back to an earlier layer (asserted per '
          'edge in the generator). Longest prerequisite path = 11 nodes / 10 edges with 2 '
          'equal-length solutions, both listed. Zero geometric crossings by giving every '
          'same-source / same-target pair its own port; F1 uses the right channel x=950 and F2 '
          'the left channel x=560. graph-audit.json carries the layering, per-node in/out '
          'neighbours, longest path and the pixel geometry of each feedback edge.'
          )
print(json.dumps(m['counts'], ensure_ascii=False, indent=1))
print('failures:', len(m['failures']))
for f in m['failures']:
    print('  ', f['http_status'], f['error'][:120])
