from pathlib import Path
from collections import Counter
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
TEMP = Path(__file__).resolve().parent
SOURCE = ROOT / "tasks/A15-reference-reconstruction/inputs/reference.png"
OUT = TEMP / "reference-inspection"
OUT.mkdir(parents=True, exist_ok=True)
im = Image.open(SOURCE).convert("RGBA")
assert im.size == (1440, 900)
im.resize((720, 450), Image.Resampling.LANCZOS).save(OUT / "reference-thumbnail.png")
regions = {
    "sidebar": (0, 0, 240, 900),
    "header-kpis": (240, 20, 1410, 300),
    "chart": (250, 300, 1010, 610),
    "activity": (1010, 300, 1410, 610),
    "table": (250, 615, 1410, 850),
}
for name, box in regions.items():
    crop = im.crop(box)
    crop.resize((crop.width * 2, crop.height * 2), Image.Resampling.NEAREST).save(OUT / f"reference-{name}-2x.png")

samples = {
    "main_background": (900, 20),
    "sidebar": (10, 10),
    "selected_nav": (30, 125),
    "primary_blue_bar": (400, 500),
    "card": (300, 200),
    "status_in_progress": (1100, 742),
}
for name, point in samples.items():
    print(name, point, im.getpixel(point))

for name, box in [("full", (0, 0, 1440, 900)), ("table", (250, 615, 1410, 850)), ("chart", (250, 300, 1010, 610))]:
    colors = Counter(im.crop(box).getdata())
    print(name, "dominant", colors.most_common(15))

# Dark-pixel glyph extent in the title region; subtitle is below y=80.
pts = [(x, y) for y in range(20, 80) for x in range(240, 1000)
       if max(im.getpixel((x, y))[:3]) < 120]
print("title_glyph_bbox", [min(x for x, y in pts), min(y for x, y in pts),
                             max(x for x, y in pts) + 1, max(y for x, y in pts) + 1])

# Exact-color connected components for major solid fills and badges.
def components(color, box, minimum=40):
    target = tuple(bytes.fromhex(color.lstrip("#")))
    x0, y0, x1, y1 = box
    seen = set()
    found = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if (x, y) in seen or im.getpixel((x, y))[:3] != target:
                continue
            stack = [(x, y)]
            seen.add((x, y))
            points = []
            while stack:
                a, b = stack.pop()
                points.append((a, b))
                for u, v in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                    if x0 <= u < x1 and y0 <= v < y1 and (u, v) not in seen and im.getpixel((u, v))[:3] == target:
                        seen.add((u, v))
                        stack.append((u, v))
            if len(points) >= minimum:
                found.append({"bbox": [min(a for a, b in points), min(b for a, b in points),
                                       max(a for a, b in points) + 1, max(b for a, b in points) + 1],
                              "pixels": len(points)})
    return sorted(found, key=lambda item: item["pixels"], reverse=True)

for color, box in [("#294467", (0, 90, 220, 190)), ("#245CE4", (250, 380, 980, 570)),
                   ("#E7EFFF", (1000, 720, 1220, 790)), ("#FFF3D7", (1000, 750, 1220, 820)),
                   ("#DCF5EC", (1000, 780, 1220, 850))]:
    print(color, components(color, box))
print("inspection", OUT.relative_to(ROOT).as_posix())
