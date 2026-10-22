#!/usr/bin/env python3
"""Suite bootstrap: initialize suite-state.json, events.jsonl and checkpoint 1.

Launch base: suite root.
"""
import datetime
import json
import pathlib
import sys

SUITE_ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
RUN_ID = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"

root = SUITE_ROOT.resolve()
tpl = json.loads((root / "templates/suite-state-template.json").read_text(encoding="utf-8"))
cat = json.loads((root / "catalog.json").read_text(encoding="utf-8"))

now = datetime.datetime.now().astimezone().isoformat(timespec="milliseconds")
tpl["run_id"] = RUN_ID
tpl["status"] = "in_progress"
tpl["started_at"] = now
tpl["updated_at"] = now
tpl["current_task"] = "A01"

by_id = {t["id"]: t for t in cat["tasks"]}
for t in tpl["tasks"]:
    entry = by_id[t["id"]]
    t["output_dir"] = entry["output_dir_template"].format(run_id=RUN_ID)
    t["temp_dir"] = entry["temp_dir_template"].format(run_id=RUN_ID)

out = root / "outputs" / RUN_ID / "_suite"
out.mkdir(parents=True, exist_ok=True)
(out / "suite-state.json").write_text(json.dumps(tpl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

events = root / "tmp" / RUN_ID / "_suite" / "events.jsonl"
with events.open("a", encoding="utf-8") as fh:
    fh.write(json.dumps({"seq": 1, "ts": now, "event": "suite_started", "run_id": RUN_ID,
                         "profile": "all", "task_count": 30, "path_base": "suite_root"},
                        ensure_ascii=False) + "\n")

cp = root / "tmp" / RUN_ID / "_suite" / "checkpoints" / "state-000001.json"
cp.write_text(json.dumps(tpl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("suite-state:", (out / "suite-state.json").relative_to(root).as_posix())
print("gitignore:", (root / ".gitignore").exists())
