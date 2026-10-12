"""B03 用例完成后的状态登记：更新 suite-state.json、追加 events.jsonl、写检查点。

用法（在总任务根执行）：
  python tmp/<run_id>/B03/log_state.py --case case-07 --md5 <final png md5> \
      --next "case-08 …"
"""
import argparse
import datetime
import json
import os
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--case", required=True)
ap.add_argument("--md5", required=True)
ap.add_argument("--next", required=True, help="下一件的简要提示")
a = ap.parse_args()

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
done_n = int(a.case.split("-")[1])
suite = root / "outputs" / rid / "_suite"
p = suite / "suite-state.json"
st = json.loads(p.read_text(encoding="utf-8"))
b = next(t for t in st["tasks"] if t["id"] == "B03")
b["completed_cases"] = ["%d/10" % i for i in range(1, done_n + 1)]
b["resume_notes"] = f"{a.case} 已交付（final md5 {a.md5}）。下一件：{a.next}"
b["artifacts"] = [f"outputs/{rid}/B03/case-01..{done_n:02d}/"
                  "{final.png, final.snapshot, case.md, data.json}"]
b["updated_at"] = now
st["current_case"] = f"B03 {a.case.split('-')[1]} done, next {a.next.split(' ')[0]}"
st["updated_at"] = now
p.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")

with open(root / "tmp" / rid / "_suite" / "events.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps({"event": "case_completed", "task_id": "B03", "run_id": rid,
                        "case": a.case, "at": now, "status": "completed",
                        "final_png_md5": a.md5, "path_base": "suite_root"},
                       ensure_ascii=False) + "\n")

cp = root / "tmp" / rid / "_suite" / "checkpoints"
nums = sorted(int(x.stem.split("-")[1]) for x in cp.glob("state-*.json"))
nxt = nums[-1] + 1
(cp / ("state-%06d.json" % nxt)).write_text(json.dumps(st, ensure_ascii=False, indent=2),
                                            encoding="utf-8")
print("checkpoint", nxt, "| cases done", len(b["completed_cases"]))
