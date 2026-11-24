import json
from pathlib import Path
from PIL import Image, ImageDraw
import prepare_A16 as p

version = "v001"
source = p.HERE / "versions" / version / "corrected-report-01.png"
out = p.HERE / "final-inspection" / version
out.mkdir(parents=True, exist_ok=True)
final = Image.open(source).convert("RGBA")
flawed = Image.open(p.FLAWED).convert("RGBA")
assert final.size == flawed.size == (1280, 900)
thumb = final.resize((640, 450), Image.Resampling.LANCZOS)
thumb.save(out / "corrected-thumbnail.png")
side = Image.new("RGBA", (1304, 450), "#E5E7EB")
side.alpha_composite(flawed.resize((640, 450), Image.Resampling.LANCZOS), (0, 0))
side.alpha_composite(thumb, (664, 0))
side.save(out / "side-by-side-thumbnails.png")
for name, box in {"chart": (56, 170, 880, 750), "details": (904, 170, 1224, 750), "conclusion": (56, 774, 1224, 900)}.items():
    crop = final.crop(box)
    crop.resize((crop.width * 2, crop.height * 2), Image.Resampling.NEAREST).save(out / f"corrected-{name}-2x.png")
measurement = p.final_measurement(source, version)
p.sk.write_json(out / "measurement.json", measurement)
print(json.dumps(measurement, ensure_ascii=False, indent=2))
