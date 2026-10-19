# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
ROOT = Path("D:/mine/test/glm-5.3-flash")
RUN = "20261016T164020-m1"
st = json.loads((ROOT / "outputs" / RUN / "_suite" / "suite-state.json").read_text(encoding="utf-8"))
print("status:", st["status"], "| stop:", st.get("stop_reason"), "| completed:", st.get("completed_task_count"), "| current:", st.get("current_task"), "| last_ck:", st.get("last_checkpoint"))
print("audit sum:", sum(st.get("task_finals_disk_audit", {}).values()))
print("artifacts:", st.get("suite_artifacts"))
ev = (ROOT / "tmp" / RUN / "_suite" / "events.jsonl").read_text(encoding="utf-8").strip().splitlines()
print("events rows:", len(ev), "| last two:", [json.loads(x)["id"] + ":" + json.loads(x)["kind"] for x in ev[-2:]])
cks = sorted((ROOT / "tmp" / RUN / "_suite" / "checkpoints").glob("state-*.json"))
print("checkpoints:", len(cks), "| newest:", cks[-1].name)
print("root .gitignore exists:", (ROOT / ".gitignore").exists())
