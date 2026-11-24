from __future__ import annotations

import json
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
OUT = BASE / "inspection"
OUT.mkdir(parents=True, exist_ok=True)
PLAN = json.loads((BASE / "plan-v001.json").read_text(encoding="utf-8"))
VERSIONS = {f"case-{i:02d}": "v002" for i in range(1, 11)}
VERSIONS.update({"case-02": "v003", "case-03": "v003", "case-05": "v003", "case-06": "v003", "case-07": "v005"})
REVIEW = "r003"


def source(case_id: str) -> Path:
    return BASE / "versions" / f"{case_id}-{VERSIONS[case_id]}" / "final-01.png"


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, "#D9DEE7")
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def crop2(case_id: str, name: str, box: tuple[int, int, int, int]) -> Path:
    with Image.open(source(case_id)) as image:
        crop = image.crop(box)
    crop = crop.resize((crop.width * 2, crop.height * 2), Image.Resampling.LANCZOS)
    path = OUT / f"{case_id}-{name}-{REVIEW}-200pct.png"
    crop.save(path)
    return path


CROPS = {
    "case-01": [("porthole-wave", (0, 40, 480, 540))],
    "case-02": [("route-joint", (640, 330, 1040, 610)), ("caution", (40, 1160, 1040, 1365))],
    "case-03": [("glass-foreground", (120, 240, 1640, 1120))],
    "case-04": [("wave-layers", (0, 340, 1080, 1140))],
    "case-05": [("portrait-overlap", (430, 240, 1130, 910))],
    "case-06": [("inline-steps", (70, 420, 1170, 825))],
    "case-07": [("tile-joins", (1140, 40, 1880, 650))],
    "case-08": [("gradient-sectors", (90, 60, 1310, 1330))],
    "case-09": [("cards-footer", (40, 210, 1710, 1190))],
    "case-10": [("orbital-overlap", (160, 280, 930, 1030))],
}

crop_paths = {}
for case_id, items in CROPS.items():
    crop_paths[case_id] = [crop2(case_id, name, box) for name, box in items]

with Image.open(BASE / "versions" / "probe-v003" / "capability-probe-01.png") as image:
    reference = image.crop((40, 100, 400, 380))
reference = reference.resize((720, 560), Image.Resampling.LANCZOS)
reference.save(OUT / f"case-01-flat-mask-service-reference-{REVIEW}-200pct.png")

font_path = Path(os.environ["WINDIR"]) / "Fonts" / "arial.ttf"
font = ImageFont.truetype(str(font_path), 22)
small = ImageFont.truetype(str(font_path), 18)
sheet = Image.new("RGB", (1280, 2540), "#EEF1F5")
draw = ImageDraw.Draw(sheet)
draw.text((40, 24), "B03 FINAL COLLECTION / 10 INDEPENDENT CASES", fill="#17233B", font=font)
for index, case in enumerate(PLAN["cases"]):
    col, row = index % 2, index // 2
    x, y = 40 + col * 620, 70 + row * 488
    draw.rounded_rectangle((x, y, x + 600, y + 470), radius=18, fill="#FFFFFF", outline="#C8D0DC", width=2)
    with Image.open(source(case["id"])) as image:
        preview = fit(image, (560, 360))
    sheet.paste(preview, (x + 20, y + 20))
    draw.text((x + 20, y + 394), f'{case["id"]} / {VERSIONS[case["id"]]} / {case["dimensions"][0]}x{case["dimensions"][1]}', fill="#17233B", font=small)
    draw.text((x + 20, y + 424), case["title"][:58], fill="#425169", font=small)
sheet.save(OUT / f"contact-sheet-final-{REVIEW}.png")

detail = Image.new("RGB", (1280, 2540), "#EEF1F5")
draw = ImageDraw.Draw(detail)
draw.text((40, 24), "B03 DETAIL REVIEW / 200% CROPS FROM FINAL SERVICE PNGs", fill="#17233B", font=font)
for index, case in enumerate(PLAN["cases"]):
    col, row = index % 2, index // 2
    x, y = 40 + col * 620, 70 + row * 488
    draw.rounded_rectangle((x, y, x + 600, y + 470), radius=18, fill="#FFFFFF", outline="#C8D0DC", width=2)
    paths = crop_paths[case["id"]]
    if len(paths) == 1:
        with Image.open(paths[0]) as image:
            panel = fit(image, (560, 360))
    else:
        panel = Image.new("RGB", (560, 360), "#D9DEE7")
        for j, path in enumerate(paths):
            with Image.open(path) as image:
                part = fit(image, (548, 168))
            panel.paste(part, (6, 6 + j * 178))
    detail.paste(panel, (x + 20, y + 20))
    draw.text((x + 20, y + 394), f'{case["id"]} / {VERSIONS[case["id"]]} / DETAIL', fill="#17233B", font=small)
    draw.text((x + 20, y + 424), case["technique"]["name"][:58], fill="#425169", font=small)
detail.save(OUT / f"detail-contact-sheet-final-{REVIEW}.png")

with Image.open(source("case-08")) as image:
    gray = ImageOps.grayscale(image).convert("RGB")
    gray.save(OUT / f"case-08-grayscale-review-{REVIEW}.png")
    low = ImageEnhance.Brightness(image.convert("RGB")).enhance(0.35)
    low.save(OUT / f"case-08-low-brightness-review-{REVIEW}.png")


def rgb(value: str) -> tuple[float, float, float]:
    return tuple(int(value[i:i + 2], 16) / 255 for i in (1, 3, 5))


def luminance(value: tuple[float, float, float]) -> float:
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in value]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def over(fg: str, bg: str, alpha: int) -> tuple[float, float, float]:
    f, b = rgb(fg), rgb(bg)
    a = alpha / 255
    return tuple(a * f[i] + (1 - a) * b[i] for i in range(3))


panel_checks = []
for bg in ("#89A77C", "#568565", "#2B6C55"):
    composite = over("#F5F1E5", bg, 0xD9)
    panel_checks.append({"background": bg, "panel_composite_rgb": [round(c * 255, 2) for c in composite],
                         "ink_contrast": round(contrast(rgb("#17233B"), composite), 2),
                         "muted_contrast": round(contrast(rgb("#657187"), composite), 2),
                         "glass_muted_contrast": round(contrast(rgb("#46566A"), composite), 2)})

points = [(182, 1022), (790, 916), (286, 734), (792, 566), (332, 408), (758, 382)]
segments = []
for index in range(len(points) - 1):
    x1, y1 = points[index]
    x2, y2 = points[index + 1]
    segments.append({"from": index + 1, "to": index + 2, "length": round(math.hypot(x2 - x1, y2 - y1), 3),
                     "angle_degrees": round(math.degrees(math.atan2(y2 - y1, x2 - x1)), 3),
                     "inside_map_panel": 58 <= min(x1, x2) and max(x1, x2) <= 1022 and 340 <= min(y1, y2) and max(y1, y2) <= 1102})

background = rgb("#11192D")
blue = rgb("#6D88D8")
gold = rgb("#F0B35E")
red = rgb("#D66C67")
group_blue = tuple(0.68 * blue[i] + 0.32 * background[i] for i in range(3))
red_layer = tuple(0.72 * red[i] + 0.28 * background[i] for i in range(3))
red_over_group = tuple(0.72 * red[i] + 0.28 * group_blue[i] for i in range(3))
calculations = {
    "case-03-panel-contrast": panel_checks,
    "case-02-route-geometry": segments,
    "case-10-alpha-composition": {
        "group_opacity": 0.68, "red_layer_opacity": 0.72,
        "blue_over_background_rgb": [round(c * 255, 2) for c in group_blue],
        "red_over_background_rgb": [round(c * 255, 2) for c in red_layer],
        "red_over_blue_group_rgb": [round(c * 255, 2) for c in red_over_group],
        "note": "Within the opacity group the second opaque oval covers the first; group alpha is then composited over the background. The separate red oval composites over that result.",
    },
    "case-09-reduced-probe": {"full": [1754, 1240], "reduced": [1200, 850], "width_scale": round(1200 / 1754, 6),
                              "font_scale": 0.78, "card_height_full": 264, "card_height_reduced": round(264 * 1200 / 1754, 3)},
}
(OUT / f"calculation-checks-{REVIEW}.json").write_text(json.dumps(calculations, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / f"final-image-inventory-{REVIEW}.json").write_text(json.dumps([
    {"case_id": case["id"], "version": VERSIONS[case["id"]], "image": str(source(case["id"])).replace("\\", "/"),
     "dimensions": list(Image.open(source(case["id"])).size), "detail_crops": [str(p).replace("\\", "/") for p in crop_paths[case["id"]]]}
    for case in PLAN["cases"]
], ensure_ascii=False, indent=2), encoding="utf-8")
print(OUT / f"contact-sheet-final-{REVIEW}.png")
print(OUT / f"detail-contact-sheet-final-{REVIEW}.png")
print(OUT / f"calculation-checks-{REVIEW}.json")
