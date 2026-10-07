"""Exact read-only RGBA and byte comparison of genuine service outputs."""
from pathlib import Path
from PIL import Image, ImageChops
import hashlib, json
from datetime import datetime, timezone

root = Path(__file__).resolve().parent
records = [json.loads((root / f'{stem}-render-result-v001.json').read_text(encoding='utf-8')) for stem in ('occlusion', 'occlusion-alternative')]
paths = [Path(r['response_file']) for r in records]
raw = [p.read_bytes() for p in paths]
ims = [Image.open(p).convert('RGBA') for p in paths]
if ims[0].size != (800, 800) or ims[1].size != (800, 800):
    raise ValueError('Unexpected image dimensions')
diff = ImageChops.difference(ims[0], ims[1])
extrema = diff.getextrema()
# Explicit RGBA tuples avoid Pillow's alpha-only getbbox default, which could
# otherwise hide RGB differences when both source alpha channels are opaque.
tuples = zip(ims[0].getdata(), ims[1].getdata())
different_count = sum(1 for p, q in tuples if p != q)
max_channel_abs = max(hi for lo, hi in extrema)
hashes = [hashlib.sha256(b).hexdigest() for b in raw]
scenes = json.loads((root / 'scene-data-occlusion-v001.json').read_text(encoding='utf-8'))
result = {
    'schema_version': 1, 'task_id': 'A19', 'run_id': '20261002-204314-6f31',
    'compared_at': datetime.now(timezone.utc).isoformat(),
    'comparison_scope': 'All 640000 original-service pixels, decoded RGBA; original PNG bytes also compared. No final image rewriting or conversion saved.',
    'original_service_pngs': [
        {'variant': variant, 'path': str(p), 'sha256': h, 'bytes': len(b), 'request_id': r['id'], 'service_request_id': r['request_id'], 'http_status': r['http_status'], 'content_type': r['content_type'], 'render_metadata': r['meta_path']}
        for variant, p, h, b, r in zip(('A', 'B'), paths, hashes, raw, records)
    ],
    'dimensions': [800, 800], 'decoded_mode': 'RGBA', 'compared_pixels': 640000,
    'pixel_difference_count': different_count,
    'maximum_channel_absolute_difference': max_channel_abs,
    'per_channel_difference_extrema': extrema,
    'rgba_pixel_equal': different_count == 0 and max_channel_abs == 0,
    'original_png_byte_equal': raw[0] == raw[1], 'original_png_sha256_equal': hashes[0] == hashes[1],
    'hidden_content_differs': scenes['scene_variants'][0]['hidden_objects'] != scenes['scene_variants'][1]['hidden_objects'],
    'two_distinct_fully_covered_cases': [
        {'case_id': case_id,
         'hidden_counts_A_B': [v['hidden_counts_by_case'][case_id] for v in scenes['scene_variants']],
         'all_hidden_bboxes_in_opaque_safe_rect': all(o['fully_inside_cover_safe_rect'] for v in scenes['scene_variants'] for o in v['hidden_objects'] if o['case_id'] == case_id)}
        for case_id in ('CASE01', 'CASE02')
    ],
    'visible_source_layer_shared': True,
    'visible_subject_ids': [o['id'] for o in scenes['visible_objects']],
    'method': 'Pillow load each original; explicit RGBA tuple equality for every pixel, ImageChops per-channel difference extrema, SHA256 and byte equality. Hidden bbox safety checked from scene geometry.',
    'does_not_replace_visual_tool_review': True
}
if not result['rgba_pixel_equal'] or not result['hidden_content_differs']:
    raise ValueError('Equivalence condition not satisfied')
destination = root / 'equivalence-v001.json'
with destination.open('x', encoding='utf-8') as handle:
    json.dump(result, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
print(json.dumps({'saved': str(destination), 'rgba_difference_count': different_count, 'sha_equal': hashes[0] == hashes[1], 'png_sha': hashes[0]}, ensure_ascii=False))
