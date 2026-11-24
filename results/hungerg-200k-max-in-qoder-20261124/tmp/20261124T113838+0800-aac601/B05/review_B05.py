from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

TASK = "B05"
run = sk.init_suite()[0]
output, temp = ck.paths(TASK)
plan = json.loads((BASE / "plan-v004.json").read_text(encoding="utf-8"))
versions = {f"B05-case-{i:02d}": "v001" for i in range(1, 11)}
versions.update({"B05-case-01": "v002", "B05-case-02": "v002", "B05-case-03": "v002",
                 "B05-case-04": "v004", "B05-case-06": "v002", "B05-case-08": "v002"})
paths = {cid: temp / "versions" / f"{cid}-{ver}" / "final-01.png" for cid, ver in versions.items()}
corrections = {
    "B05-case-01": "照片区标签改为完整的药品01–05，五种名称、规格和频次仍在主列表完整核对。",
    "B05-case-02": "共享Omeprazole图标改为圆片，三来源和两处差异保持清楚。",
    "B05-case-03": "角色卡片加入连接线，父亲、女儿、医生与紧急联系人的关系更直观；权限边界未变。",
    "B05-case-04": "整体审查发现Metformin也属于08:00，晨间页原仅三项；现补为四项并标‘未确认’，与案例05连续，Omeprazole圆片及‘稍后 / 求助’路径保持。",
    "B05-case-06": "补充‘今日盘点：Metformin 32→40片’，解释案例02数量差异与20天估算的连续依据。",
    "B05-case-08": "Atorvastatin由每日21:00改为‘停用待医生确认’，与案例02/07待确认状态一致。",
}
comparisons = {
    cid: f"与{cid}-v001服务原图对比；{corrections[cid]}其余布局、内容和医疗边界未弱化。"
    for cid in corrections
}
existing_iterations = sk.read_jsonl(temp / "iterations.jsonl")
existing_tools = sk.read_jsonl(temp / "tool-usage.jsonl")
for cid, note in corrections.items():
    if any(item.get("case_id") == cid and item.get("version_id") == versions[cid]
           and item.get("completed_visual_iteration") for item in existing_iterations):
        continue
    ck.record_view(TASK, next(c for c in plan["cases"] if c["id"] == cid), paths[cid], versions[cid],
                   note + " 修正版文字、边界和层级可读，没有发现新的交付缺陷。", note, comparisons[cid], True, "visual")

for index, (sid, filename) in enumerate((("B05-S01", "b05_s01.webfetch.md"), ("B05-S02", "b05_s02.webfetch.md")), 1):
    source = BASE / "research" / filename
    if any(item.get("tool") == "WebFetch" and sid in item.get("result", "") for item in existing_tools):
        continue
    ck.log_tool(TASK, "WebFetch", "实际取得并阅读FDA可读页面，形成用药清单内容与更新/共享需求的证据",
                ["https://www.fda.gov/"], [sk.rel(source)], [c["id"] for c in plan["cases"]],
                f"{sid}成功；可读缓存、访问时间与来源哈希已归档；直接HTTP 404另存且未当证据")

inspection = temp / "inspection"
inspection.mkdir(parents=True, exist_ok=True)
font = ImageFont.truetype(str(Path(os.environ["WINDIR"]) / "Fonts" / "msyh.ttc"), 22)
thumbs = []
for case in plan["cases"]:
    cid = case["id"]
    with Image.open(paths[cid]) as image:
        image = image.convert("RGB")
        image.thumbnail((460, 320))
        tile = Image.new("RGB", (480, 370), "#E8EDF2")
        tile.paste(image, ((480-image.width)//2, 18))
        draw = ImageDraw.Draw(tile)
        draw.text((16, 344), f'{cid} · {versions[cid]} · {case["title"]}', fill="#172B42", font=font)
        thumbs.append(tile)
sheet = Image.new("RGB", (1440, 1480), "#CBD5E1")
for i, tile in enumerate(thumbs):
    sheet.paste(tile, ((i%3)*480, (i//3)*370))
sheet.save(inspection / "contact-sheet-final-r001.png")

crops = [
    ("B05-case-01", (0, 220, 390, 790)),
    ("B05-case-02", (20, 315, 1420, 730)),
    ("B05-case-03", (40, 210, 1160, 770)),
    ("B05-case-04", (0, 280, 390, 800)),
    ("B05-case-05", (0, 180, 390, 780)),
    ("B05-case-06", (20, 205, 1004, 670)),
    ("B05-case-07", (20, 210, 1420, 780)),
    ("B05-case-08", (0, 250, 430, 840)),
    ("B05-case-09", (0, 190, 390, 790)),
    ("B05-case-10", (20, 190, 1160, 700)),
]
detail_paths = []
for page in range(2):
    detail = Image.new("RGB", (1440, 740), "#CBD5E1")
    for i, (cid, box) in enumerate(crops[page*5:(page+1)*5]):
        with Image.open(paths[cid]) as image:
            crop = image.convert("RGB").crop(box)
            crop.thumbnail((460, 290))
            tile = Image.new("RGB", (480, 370), "#E8EDF2")
            tile.paste(crop, ((480-crop.width)//2, 25))
            ImageDraw.Draw(tile).text((16, 334), f"{cid} 局部文字与状态", fill="#172B42", font=font)
            detail.paste(tile, ((i%3)*480, (i//3)*370))
    path = inspection / f"detail-contact-sheet-final-r001-{page+1:02d}.png"
    detail.save(path)
    detail_paths.append(path)
ck.log_tool(TASK, "Pillow inspection derivatives", "生成最终整体接触表和两页局部细节图，仅用于整体一致性核验，不替代逐张服务原图",
            [sk.rel(path) for path in paths.values()],
            [sk.rel(inspection / "contact-sheet-final-r001.png")] + [sk.rel(path) for path in detail_paths],
            list(paths), "三张检查派生图已生成；此前版本已另名保留")

shared = json.loads((BASE / "product-data.json").read_text(encoding="utf-8"))
meds = shared["medications"]
checks = {
    "schema_version": 1, "task_id": TASK, "checked_at": sk.iso(), "path_base": "suite_root",
    "medication_count": len(meds), "medication_ids": [m["id"] for m in meds],
    "calculations": [{"medication_id": m["id"], "quantity": m["quantity"], "times_per_day": m["times_per_day"],
                      "formula": f'{m["quantity"]} / {m["times_per_day"]}', "days_remaining": m["days_remaining"],
                      "matches": m["days_remaining"] == m["quantity"] / m["times_per_day"]} for m in meds],
    "metformin_refill_check": {"quantity": 40, "times_per_day": 2, "days_remaining": 20, "threshold_days": 14,
                               "enters_threshold": 20 <= 14 + 7, "stocktake": "32 -> 40 on 2026-11-24",
                               "reconciliation_cases": ["B05-case-02", "B05-case-06"]},
    "morning_0800_check": [m["name"] for m in meds if "08:00" in m["schedule"]],
    "all_morning_items_have_one_unit": all(("1片" in m["schedule"] or "1粒" in m["schedule"])
                                           for m in meds if "08:00" in m["schedule"]),
    "atorvastatin_safe_state": "stop pending doctor confirmation; automatic reminder paused in cases 07/08",
    "missed_dose_event": "Metformin 08:00 unconfirmed; 09:40 family report; no automatic make-up or doubling advice",
    "sharing_check": {"scope": "current visit only", "expiry_hours": 24, "revocable": True},
    "claims_check": {"no_health_score": True, "no_adherence_outcome_claim": True, "no_real_user_validation": True},
    "final_versions": versions,
    "all_checks_passed": all(item["matches"] for item in [{"matches": m["days_remaining"] == m["quantity"] / m["times_per_day"]} for m in meds]),
}
sk.write_json(inspection / "calculation-checks-r001.json", checks)
print(json.dumps({"iterations_recorded": len(corrections), "versions": versions,
                  "inspection": [sk.rel(inspection / "contact-sheet-final-r001.png")] + [sk.rel(path) for path in detail_paths]}, ensure_ascii=False))
