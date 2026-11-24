import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw
import prepare_A15 as p

parser = argparse.ArgumentParser()
parser.add_argument("--version", default="v004")
args = parser.parse_args()
version = args.version
source = p.HERE / "versions" / version / "reconstructed-01.png"
out = p.HERE / "final-inspection" / version
out.mkdir(parents=True, exist_ok=False)
reference = Image.open(p.INPUT / "reference.png").convert("RGBA")
final = Image.open(source).convert("RGBA")
assert reference.size == final.size == (1440, 900)

thumb_ref = reference.resize((720, 450), Image.Resampling.LANCZOS)
thumb_final = final.resize((720, 450), Image.Resampling.LANCZOS)
thumb_ref.save(out / "reconstructed-thumbnail.png")
side = Image.new("RGBA", (1464, 450), "#E5E7EB")
side.alpha_composite(thumb_ref, (0, 0))
side.alpha_composite(thumb_final, (744, 0))
side.save(out / "side-by-side-thumbnails.png")

regions = {
    "sidebar": (0, 0, 240, 900),
    "header-kpis": (240, 20, 1410, 300),
    "chart": (250, 300, 1010, 610),
    "activity": (1010, 300, 1410, 610),
    "table": (250, 615, 1410, 850),
}
for name, box in regions.items():
    crop = final.crop(box)
    crop.resize((crop.width * 2, crop.height * 2), Image.Resampling.NEAREST).save(out / f"reconstructed-{name}-2x.png")

swatches = Image.new("RGBA", (760, 40 + len(p.COLOR_SITES) * 86), "#E5E7EB")
draw = ImageDraw.Draw(swatches)
draw.text((24, 12), "REFERENCE", fill="#172033")
draw.text((404, 12), "RECONSTRUCTED", fill="#172033")
color_samples = []
for index, (name, site) in enumerate(p.COLOR_SITES.items()):
    y = 40 + index * 86
    point = tuple(site["point"])
    ref_rgba = reference.getpixel(point)
    final_rgba = final.getpixel(point)
    draw.text((24, y + 4), name, fill="#172033")
    draw.rectangle((24, y + 24, 344, y + 72), fill=ref_rgba, outline="#94A3B8", width=1)
    draw.rectangle((404, y + 24, 724, y + 72), fill=final_rgba, outline="#94A3B8", width=1)
    color_samples.append({"site": name, "point": list(point), "reference_rgba": ref_rgba, "final_rgba": final_rgba})
swatches.save(out / "color-comparison.png")

_, ref_anchors = p.measure(p.INPUT / "reference.png")
_, final_anchors = p.measure(source)
bar_data = []
for index, (month, value) in enumerate(zip(p.CONTENT["months"], p.CONTENT["chart_values"])):
    x = 357 + index * 101
    ref_box = p.component_bbox(reference, p.BLUE, (x - 8, 380, x + 70, 560))
    final_box = p.component_bbox(final, p.BLUE, (x - 8, 380, x + 70, 560))
    assert ref_box and final_box
    bar_data.append({"month": month, "value": value, "reference_bbox": ref_box, "final_bbox": final_box,
                     "reference_height": ref_box[3] - ref_box[1], "final_height": final_box[3] - final_box[1],
                     "top_error": abs(ref_box[1] - final_box[1]),
                     "height_error": abs((ref_box[3] - ref_box[1]) - (final_box[3] - final_box[1])),
                     "scale_px_per_thousand": 1.2})

grid = []
for tick in (0, 30, 60, 90, 120):
    y = round(549 - tick * 1.2)
    row = {}
    for label, image in (("reference", reference), ("final", final)):
        xs = [x for x in range(300, 990) if image.getpixel((x, y))[:3] == (231, 237, 245)]
        row[label] = {"y": y, "left": min(xs), "right": max(xs), "visible_pixels": len(xs)}
    grid.append({"tick": tick, **row})

badges = []
for index, (row, color) in enumerate(zip(p.CONTENT["rows"], ("#E7EFFF", "#FFF3D7", "#DCF5EC"))):
    ref_box = p.component_bbox(reference, color, (1000, 720 + index * 35, 1220, 790 + index * 35))
    final_box = p.component_bbox(final, color, (1000, 720 + index * 35, 1220, 790 + index * 35))
    badges.append({"row": index + 1, "project": row[0], "owner": row[1], "status": row[2], "due": row[3],
                   "reference_bbox": ref_box, "final_bbox": final_box})

measurement = {"version": version, "source": p.rp(source, p.ROOT), "size": [1440, 900],
               "anchors": {"reference": ref_anchors, "final": final_anchors},
               "chart_bars": bar_data, "chart_grid": grid, "table_badges": badges,
               "color_samples": color_samples,
               "derivatives": {path.name: p.rp(path, p.ROOT) for path in sorted(out.glob("*.png"))}}
p.sk.write_json(out / "measurement.json", measurement)
print(json.dumps(measurement, ensure_ascii=False, indent=2))
