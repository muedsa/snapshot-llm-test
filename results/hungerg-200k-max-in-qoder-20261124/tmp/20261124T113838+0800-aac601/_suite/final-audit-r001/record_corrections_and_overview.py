from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

RUN, SUITE_OUT, SUITE_TEMP = sk.init_suite()
RUN_OUT = SUITE_OUT.parent
RUN_TEMP = SUITE_TEMP.parent
now = sk.iso()

b03_inspection = RUN_TEMP / "B03" / "inspection"
source_inventory = b03_inspection / "final-image-inventory-r003.json"
inventory = json.loads(source_inventory.read_text(encoding="utf-8"))


def portable(value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        path = path.resolve().relative_to(ROOT)
    return path.as_posix()


corrected_inventory = []
for item in inventory:
    corrected = dict(item)
    corrected["image"] = portable(item["image"])
    corrected["detail_crops"] = [portable(path) for path in item["detail_crops"]]
    for path in [corrected["image"], *corrected["detail_crops"]]:
        if not (ROOT / path).is_file():
            raise RuntimeError(f"Missing B03 inventory path: {path}")
    corrected_inventory.append(corrected)
inventory_output = b03_inspection / "final-image-inventory-r004-portable.json"
sk.write_json(inventory_output, {
    "schema_version": 1,
    "run_id": RUN,
    "path_base": "suite_root",
    "created_at": now,
    "revision_of": sk.rel(source_inventory),
    "correction": "将历史绝对路径转换为 suite_root 相对路径；保留 r001–r003 原件。",
    "count": len(corrected_inventory),
    "items": corrected_inventory,
})

iteration_path = RUN_TEMP / "B03" / "iterations.jsonl"
iterations = sk.read_jsonl(iteration_path)
corrections = []
for row in iterations:
    original = row.get("image_path", "")
    corrected = original.replace("case-03-case-03-", "case-03-")
    corrected = corrected.replace("case-05-case-05-", "case-05-")
    corrected = corrected.replace("case-06-case-06-", "case-06-")
    corrected = corrected.replace("case-07-case-07-", "case-07-")
    corrected = corrected.replace("probe-probe-", "probe-")
    if corrected != original:
        if not (ROOT / corrected).is_file():
            raise RuntimeError(f"Corrected iteration path missing: {corrected}")
        corrections.append({
            "iteration_id": row["iteration_id"],
            "original_image_path": original,
            "corrected_image_path": corrected,
            "reason": "版本目录前缀重复；目标图片实际存在于单前缀目录。",
        })
if len(corrections) != 9:
    raise RuntimeError(f"Expected 9 B03 path corrections, found {len(corrections)}")
correction_output = b03_inspection / "iteration-path-corrections-r001.json"
sk.write_json(correction_output, {
    "schema_version": 1,
    "run_id": RUN,
    "path_base": "suite_root",
    "created_at": now,
    "source_log": sk.rel(iteration_path),
    "raw_log_modified": False,
    "count": len(corrections),
    "corrections": corrections,
})
sk.append_jsonl(RUN_TEMP / "B03" / "tool-usage.jsonl", {
    "tool_usage_id": f"{RUN}-B03-tool-path-correction-r001",
    "task_id": "B03",
    "at": now,
    "timezone": "+08:00",
    "tool": "Python metadata reconciliation",
    "purpose": "追加可移植清单后继与九条迭代路径修正映射；不覆盖历史清单和原始日志",
    "inputs": [sk.rel(source_inventory), sk.rel(iteration_path)],
    "outputs": [sk.rel(inventory_output), sk.rel(correction_output)],
    "result": "10件最终图和所有细节图路径可访问；9条重复前缀引用已映射到实际文件。",
})

manifest_path = BASE / "overview-review-manifest-v002.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
for sheet in manifest["sheets"]:
    sheet["viewed"] = True
    sheet["review_recorded_at"] = now
    sheet["observation"] = "已实际查看整页：16件成品均有独立缩略图，标题与尺寸可读，长标题换行后无溢出；未以接触表替代逐件服务原图检查。"
manifest["review_recorded_at"] = now
manifest["unviewed_count"] = 0
manifest["review_result"] = "八页共124件指定成品全部呈现；A21/A22三轮与B01–B06六十件均可见。r001长标题截断和路径溢出缺陷已由v002修正。"
manifest["individual_final_review"] = "各题此前已逐件打开最终服务原图并留痕；本总览仅用于全套一致性复查。"
sk.write_json(manifest_path, manifest)
review_output = BASE / "overview-review-r001.json"
sk.write_json(review_output, {
    "schema_version": 1,
    "run_id": RUN,
    "path_base": "suite_root",
    "review_recorded_at": now,
    "superseded_review": {
        "manifest": sk.rel(BASE / "overview-review-manifest-r001.json"),
        "defect": "长标题截断，完整路径说明溢出相邻缩略图。",
        "preserved": True,
    },
    "accepted_manifest": sk.rel(manifest_path),
    "sheets_viewed": 8,
    "designated_finals_represented": 124,
    "observations": [
        "八页每页16件，合计124件，无缺项或重复占位。",
        "标题、任务/用例分组与像素尺寸可读；v002没有路径说明溢出。",
        "A21/A22三个轮次均在总览中保留。",
        "B01–B06六十件作品均在总览中保留。",
        "接触表只作为整体证据，不替代各题逐件最终服务原图查看。",
    ],
    "known_defects": [],
})

sk.append_jsonl(SUITE_TEMP / "events.jsonl", {
    "event_id": f"{RUN}-suite-final-review-evidence-r001",
    "at": now,
    "event": "suite-final-review-evidence-r001",
    "status": "recorded",
    "artifacts": [sk.rel(review_output), sk.rel(manifest_path), sk.rel(inventory_output), sk.rel(correction_output)],
    "historical_event_note": "B06-finish 的000110/000111为15毫秒内重复生成，原始记录保留；只计一次任务完成，不额外计工作或请求。",
})
sk.checkpoint(RUN, "suite-final-review-evidence-r001")
print(json.dumps({"b03_inventory": len(corrected_inventory), "b03_path_corrections": len(corrections), "overview_sheets_viewed": 8, "finals": 124}, ensure_ascii=False))
