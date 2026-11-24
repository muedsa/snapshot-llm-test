from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

RUN, SUITE_OUT, SUITE_TEMP = sk.init_suite()
RUN_OUT = SUITE_OUT.parent
BACKUP = BASE / "metadata-backups"
BACKUP.mkdir(parents=True, exist_ok=True)

b04_output = RUN_OUT / "B04"
b04_temp = ROOT / sk.CONFIG["temp_root"] / RUN / "B04"
sources_path = b04_output / "sources.json"
backup_path = BACKUP / "B04-sources-before-path-base-correction.json"
assert not backup_path.exists()
shutil.copyfile(sources_path, backup_path)
sources = json.loads(sources_path.read_text(encoding="utf-8"))


def transform(value):
    if isinstance(value, dict):
        return {key: transform(item) for key, item in value.items()}
    if isinstance(value, list):
        return [transform(item) for item in value]
    if isinstance(value, str):
        if value.startswith("tmp/"):
            return "../../../" + value
        return value.replace("corrected suite_root-relative paths", "corrected output_dir-relative paths").replace(
            "authoritative suite_root-relative corrections to the initial fetch-results path omission",
            "authoritative output_dir-relative corrections to the initial fetch-results path omission",
        ).replace("authoritative suite_root-relative corrections", "authoritative output_dir-relative corrections")
    return value


sources = transform(sources)
sources["path_base"] = "output_dir"
sources["metadata_correction"] = {
    "corrected_at": sk.iso(),
    "reason": "B04 sources.json 模板要求 path_base=output_dir；证据路径已从 suite_root 基准转换为 output_dir 基准。",
    "previous_file": sk.rel(backup_path),
    "previous_path_base": "suite_root",
    "current_path_base": "output_dir",
    "path_rule": "tmp/... -> ../../../tmp/...；均相对 outputs/<run_id>/B04/。",
}
for failure in sources.get("unread_sources", []):
    if failure.get("source_id") == "B04-S15":
        failure["attempted_at_provenance"] = "unverified_hardcoded"
        failure["attempted_at_note"] = "该时间由 finalize_B04.py 硬编码；没有对应原始请求时间戳，不作为已验证访问时间。"
missing_paths = []
for source in sources.get("read_sources", []):
    for field in ("metadata", "raw_response", "readable_text"):
        evidence_path = b04_output / source[field]
        if not evidence_path.is_file():
            missing_paths.append(source[field])
if missing_paths:
    raise RuntimeError(f"证据路径校验失败: {missing_paths}")
sk.write_json(sources_path, sources)

state_path = SUITE_OUT / "suite-state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
for task_id in ("A21", "A22"):
    entry = next(item for item in state["tasks"] if item["id"] == task_id)
    metric_rel = sk.rel(RUN_OUT / task_id / "task-metrics.json")
    if metric_rel not in entry["artifacts"]:
        entry["artifacts"].append(metric_rel)

tool_path = b04_temp / "tool-usage.jsonl"
rows = sk.read_jsonl(tool_path)
sk.append_jsonl(tool_path, {
    "tool_usage_id": f"{RUN}-B04-tool-{len(rows) + 1:03d}",
    "task_id": "B04",
    "at": sk.iso(),
    "timezone": "+08:00",
    "tool": "Python metadata reconciliation",
    "purpose": "修正 sources.json 的 path_base 与证据路径基准，并标注 S15 硬编码 attempt 时间不可验证",
    "inputs": [sk.rel(backup_path)],
    "outputs": [sk.rel(sources_path)],
    "case_ids": [f"B04-case-{index:02d}" for index in range(1, 11)],
    "result": "模板元数据一致；全部已读来源的证据文件路径保持可访问；不改变研究内容或图片。",
})
sk.write_json(state_path, state)
sk.checkpoint(RUN, "suite-metadata-corrections-r001")
print(json.dumps({"b04_path_base": sources["path_base"], "state_artifacts_fixed": ["A21", "A22"]}, ensure_ascii=False))
