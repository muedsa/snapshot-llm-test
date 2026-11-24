import json
from collections import Counter
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "tasks/A16-visual-data-forensics/inputs/flawed-report.png"
OUT = HERE / "flawed-inspection"
OUT.mkdir(parents=True, exist_ok=True)
image = Image.open(SOURCE).convert("RGBA")
assert image.size == (1280, 900)
image.resize((640, 450), Image.Resampling.LANCZOS).save(OUT / "flawed-thumbnail.png")
for name, box in {"chart": (56, 170, 928, 730), "details": (56, 750, 1224, 850), "header": (40, 30, 1240, 150)}.items():
    crop = image.crop(box)
    crop.resize((crop.width * 2, crop.height * 2), Image.Resampling.NEAREST).save(OUT / f"flawed-{name}-2x.png")


def components(color, box, minimum=100):
    target = tuple(bytes.fromhex(color.lstrip("#")))
    x0, y0, x1, y1 = box
    seen = set()
    found = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if (x, y) in seen or image.getpixel((x, y))[:3] != target:
                continue
            stack = [(x, y)]
            seen.add((x, y))
            points = []
            while stack:
                a, b = stack.pop()
                points.append((a, b))
                for u, v in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                    if x0 <= u < x1 and y0 <= v < y1 and (u, v) not in seen and image.getpixel((u, v))[:3] == target:
                        seen.add((u, v))
                        stack.append((u, v))
            if len(points) >= minimum:
                found.append({
                    "bbox": [min(a for a, b in points), min(b for a, b in points), max(a for a, b in points) + 1, max(b for a, b in points) + 1],
                    "pixels": len(points),
                })
    return sorted(found, key=lambda item: item["bbox"][0])


colors = Counter(image.crop((56, 170, 928, 730)).getdata()).most_common(20)
blue = components("#245CE4", (80, 240, 1100, 700))
orange = components("#E88E35", (80, 240, 1100, 700))
grid_candidates = []
for y in range(280, 660):
    count = sum(image.getpixel((x, y))[:3] == (229, 231, 235) for x in range(120, 1100))
    if count > 250:
        grid_candidates.append({"y": y, "matching_pixels": count})
card_border_candidates = []
for x in range(900, 960):
    count = sum(image.getpixel((x, y))[:3] == (229, 231, 235) for y in range(190, 720))
    if count > 450:
        card_border_candidates.append({"x": x, "matching_pixels": count})
axis_rows = []
for value, y in zip((200, 180, 160, 140, 120, 100), (295, 349, 403, 457, 511, 565)):
    xs = [x for x in range(120, 900) if image.getpixel((x, y))[:3] == (229, 231, 235)]
    axis_rows.append({"tick": value, "y": y, "left": min(xs), "right": max(xs), "visible_pixels": len(xs)})
bar_checks = []
for series, values, fills in (("blue_labeled_cost", (120, 135, 128, 180), blue), ("orange_labeled_revenue", (90, 108, 96, 126), orange)):
    for index, (value, fill) in enumerate(zip(values, fills), 1):
        inferred = 200 - (fill["bbox"][1] - 295) / 2.7
        bar_checks.append({"quarter": f"Q{index}", "series": series, "label_value": value, "bbox": fill["bbox"], "axis_inferred_value": round(inferred, 2), "difference": round(inferred - value, 2)})
measurement = {
    "source": "tasks/A16-visual-data-forensics/inputs/flawed-report.png",
    "size": [1280, 900],
    "dominant_chart_colors": [{"rgba": rgba, "pixels": count} for rgba, count in colors],
    "blue_components": blue,
    "orange_components": orange,
    "grid_candidates": grid_candidates,
    "card_border_candidates": card_border_candidates,
    "axis_rows": axis_rows,
    "bar_axis_checks": bar_checks,
    "derivatives": {path.name: path.relative_to(ROOT).as_posix() for path in sorted(OUT.glob("*.png"))},
}
(OUT / "measurement.json").write_text(json.dumps(measurement, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(measurement, ensure_ascii=False, indent=2))
