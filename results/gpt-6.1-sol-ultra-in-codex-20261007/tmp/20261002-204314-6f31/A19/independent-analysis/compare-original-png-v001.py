import argparse, hashlib, json, pathlib
from datetime import datetime, timezone
from PIL import Image, ImageChops

p = argparse.ArgumentParser()
p.add_argument('a')
p.add_argument('b')
p.add_argument('output')
args = p.parse_args()
a_path, b_path, out = (pathlib.Path(x).resolve() for x in (args.a, args.b, args.output))
if out.exists():
    raise FileExistsError(out)
a_bytes, b_bytes = a_path.read_bytes(), b_path.read_bytes()
with Image.open(a_path) as src_a, Image.open(b_path) as src_b:
    a, b = src_a.convert('RGBA'), src_b.convert('RGBA')
    formats = [src_a.format, src_b.format]
    source_modes = [src_a.mode, src_b.mode]
if a.size != b.size:
    raise ValueError('Image dimensions differ')
diff = ImageChops.difference(a, b)
changed_pixels = sum(any(ch != 0 for ch in rgba) for rgba in diff.getdata())
max_channel_difference = max(extreme[1] for extreme in diff.getextrema())
result = {
    'task_id': 'A19',
    'reviewer': '/root/a17_auditor',
    'reviewed_at': datetime.now(timezone.utc).isoformat(),
    'image_paths': [str(a_path), str(b_path)],
    'original_PNG_SHA256': [hashlib.sha256(a_bytes).hexdigest(), hashlib.sha256(b_bytes).hexdigest()],
    'original_bytes': [len(a_bytes), len(b_bytes)],
    'original_formats': formats,
    'source_color_modes': source_modes,
    'decoded_size': list(a.size),
    'compared_RGBA_pixels': a.width * a.height,
    'changed_RGBA_pixels': changed_pixels,
    'maximum_RGBA_channel_difference': max_channel_difference,
    'RGBA_difference_channel_extrema': diff.getextrema(),
    'original_PNG_bytes_identical': a_bytes == b_bytes,
    'all_RGBA_pixels_equivalent': changed_pixels == 0 and max_channel_difference == 0,
    'method': 'Read-only Pillow convert(RGBA), ImageChops.difference, enumerate every RGBA tuple; no PNG rewriting or visual view claim.'
}
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
