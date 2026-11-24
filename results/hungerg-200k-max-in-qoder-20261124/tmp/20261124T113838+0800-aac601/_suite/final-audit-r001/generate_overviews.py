from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

RUN = sk.init_suite()[0]
RUN_OUT = ROOT / sk.CONFIG["output_root"] / RUN
SUITE_OUT = RUN_OUT / "_suite"
CATALOG = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
STATE = json.loads((SUITE_OUT / "suite-state.json").read_text(encoding="utf-8"))
TASKS = {item["id"]: item for item in CATALOG["tasks"]}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = ["msyhbd.ttc", "msyh.ttc", "simhei.ttf"] if bold else ["msyh.ttc", "simhei.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


items = []
for entry in STATE["tasks"]:
    task_id = entry["id"]
    output = RUN_OUT / task_id
    spec = json.loads((ROOT / TASKS[task_id]["task_spec"]).read_text(encoding="utf-8"))
    titles = {}
    if task_id.startswith("B"):
        portfolio = json.loads((output / "portfolio.json").read_text(encoding="utf-8"))
        titles = {case["png"]: case["title"] for case in portfolio["cases"]}
    if spec.get("required_outputs"):
        paths = [output / item["filename"] for item in spec["required_outputs"]]
    else:
        portfolio = json.loads((output / "portfolio.json").read_text(encoding="utf-8"))
        paths = [output / case["png"] for case in portfolio["cases"]]
    for path in paths:
        assert path.is_file(), path
        relative = path.relative_to(output).as_posix()
        with Image.open(path) as image:
            assert image.format == "PNG"
            dimensions = list(image.size)
        items.append({
            "task_id": task_id,
            "task_title": TASKS[task_id]["title"],
            "group": path.parent.relative_to(output).as_posix() if path.parent != output else "final",
            "case_id": path.parent.name if task_id.startswith("B") else None,
            "title": titles.get(relative, path.stem.replace("-", " ").replace("_", " ")),
            "png": sk.rel(path),
            "snapshot": sk.rel(path.with_suffix(".snapshot")),
            "dimensions": dimensions,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })

assert len(items) == CATALOG["minimum_final_pngs"], len(items)
sk.write_json(BASE / "final-inventory-r001.json", {
    "schema_version": 1,
    "run_id": RUN,
    "path_base": "suite_root",
    "created_at": sk.iso(),
    "count": len(items),
    "advanced_count": sum(not item["task_id"].startswith("B") for item in items),
    "creative_count": sum(item["task_id"].startswith("B") for item in items),
    "items": items,
})

inspection = BASE / "inspection"
inspection.mkdir(parents=True, exist_ok=True)
manifest = []
for sheet_index, start in enumerate(range(0, len(items), 16), 1):
    subset = items[start:start + 16]
    columns = 4
    rows = (len(subset) + columns - 1) // columns
    tile_w, tile_h = 460, 340
    sheet = Image.new("RGB", (columns * tile_w, 70 + rows * tile_h), "#DCE3EA")
    draw = ImageDraw.Draw(sheet)
    draw.text((22, 17), f"Snapshot suite final overview {sheet_index:02d} / items {start + 1:02d}-{start + len(subset):02d}", font=font(28, True), fill="#172B42")
    for local_index, item in enumerate(subset):
        x = (local_index % columns) * tile_w
        y = 70 + (local_index // columns) * tile_h
        draw.rounded_rectangle((x + 8, y + 8, x + tile_w - 8, y + tile_h - 8), radius=12, fill="#F7F9FC", outline="#C4CED8", width=2)
        with Image.open(ROOT / item["png"]) as source:
            source = source.convert("RGB")
            source.thumbnail((420, 252), Image.Resampling.LANCZOS)
            px = x + (tile_w - source.width) // 2
            py = y + 18 + (252 - source.height) // 2
            sheet.paste(source, (px, py))
        caption = f"{item['task_id']} · {item['group']} · {item['title']}"
        if item["case_id"]:
            caption = f"{item['case_id']} · {item['title']}"
        draw.text((x + 20, y + 282), caption[:38], font=font(19, True), fill="#172B42")
        draw.text((x + 20, y + 309), f"{item['dimensions'][0]}×{item['dimensions'][1]} · {item['png']}", font=font(15), fill="#43556A")
    name = f"suite-contact-sheet-{sheet_index:02d}.png"
    path = inspection / name
    sheet.save(path)
    manifest.append({
        "path": sk.rel(path),
        "item_start": start + 1,
        "item_end": start + len(subset),
        "items": [item["png"] for item in subset],
        "viewed": False,
    })
sk.write_json(BASE / "overview-review-manifest-r001.json", {
    "schema_version": 1,
    "run_id": RUN,
    "created_at": sk.iso(),
    "purpose": "全套最终构图的整体浏览；不替代逐件最终服务原图查看。",
    "sheets": manifest,
    "unviewed_count": len(manifest),
})
sk.append_jsonl(ROOT / sk.CONFIG["temp_root"] / RUN / "_suite/events.jsonl", {
    "event_id": f"{RUN}-suite-overview-generated-{sk.iso()}",
    "at": sk.iso(),
    "event": "suite_overview_generated",
    "inventory": sk.rel(BASE / "final-inventory-r001.json"),
    "sheets": [item["path"] for item in manifest],
    "status": "pending_visual_review",
})
print(json.dumps({"items": len(items), "sheets": len(manifest), "inspection": sk.rel(inspection)}, ensure_ascii=False))
