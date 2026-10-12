"""A12 crop helper: 2x NEAREST magnifications of the delivered PNGs, so the 16pt phone body
and the mono footer line can actually be read on screen. Regions come from content-map.json
(the boxes the layout engine emitted), never from hand-picked pixel guesses.
"""
import json
import os
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
OUT, TEMP = ROOT / "outputs" / RID / "A12", ROOT / "tmp" / RID / "A12"
cmap = json.loads((TEMP / "content-map.json").read_text(encoding="utf-8"))
DEST = TEMP / "preview" / "crops-final"
DEST.mkdir(parents=True, exist_ok=True)

# named groups of fields whose union box is cropped, per canvas
GROUPS = {
    "mobile": [("hero", ["kicker", "title", "subtitle", "label_日期", "value_日期",
                         "label_时间", "value_时间", "label_地点", "value_地点", "cta"]),
               ("cards-C1-C2", ["card_title_C1", "card_detail_C1", "index_C1",
                                "card_title_C2", "card_detail_C2"]),
               ("footer", ["website"])],
    "tablet": [("hero-meta", ["label_日期", "value_时间", "label_地点", "value_地点"]),
               ("card-C6", ["index_C6", "card_title_C6", "card_detail_C6"])],
    "desktop": [("hero-line", ["label_日期", "value_时间", "label_地点", "value_地点", "cta"]),
                ("card-C3", ["index_C3", "card_title_C3", "card_detail_C3"])],
    "stage": [("hero-line", ["kicker", "title", "subtitle", "label_日期", "value_时间",
                             "label_地点", "value_地点", "cta"]),
              ("card-C4", ["index_C4", "card_title_C4", "card_detail_C4"]),
              ("footer", ["website"])],
}

manifest = []
for bp, groups in GROUPS.items():
    fields = cmap["fields"][bp]
    W, H = cmap["canvases"][bp]["size"]
    img = Image.open(OUT / f"{bp}.png").convert("RGBA")
    for name, keys in groups:
        boxes = [fields[k]["box"] for k in keys]
        x0 = max(0, min(b[0] for b in boxes) - 10)
        y0 = max(0, min(b[1] for b in boxes) - 10)
        x1 = min(W, max(b[0] + b[2] for b in boxes) + 10)
        y1 = min(H, max(b[1] + b[3] for b in boxes) + 10)
        crop = img.crop((int(x0), int(y0), int(x1), int(y1)))
        crop = crop.resize((crop.width * 2, crop.height * 2), Image.NEAREST)
        fn = f"{bp}-{name}.png"
        crop.save(DEST / fn)
        manifest.append({"file": f"tmp/{RID}/A12/preview/crops-final/{fn}",
                         "canvas": bp, "region": [x0, y0, x1 - x0, y1 - y0],
                         "fields": keys, "magnification": 2})
(DEST / "manifest.json").write_text(json.dumps(
    {"schema_version": 1, "path_base": "suite_root", "crops": manifest},
    ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps(manifest, ensure_ascii=False))
