"""A24 driver: render the three carriers and log iterations."""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_suite", "shared"))
from renderer import log_iteration, render  # noqa: E402
from suite_common import ROOT, now  # noqa: E402

R = "outputs/20261003-114508-flashmax/A24"
T = "tmp/20261003-114508-flashmax/A24"


def main() -> None:
    jobs = []
    for name in ("execution-board", "decision-brief", "action-card"):
        shutil.copyfile(os.path.join(ROOT, R, f"{name}.snapshot"),
                        os.path.join(ROOT, T, f"{name}.v1.snapshot"))
        jobs.append({"dsl": f"{R}/{name}.snapshot", "out": f"{R}/{name}.png",
                     "task": "A24", "prefix": "A24-REQ", "round": None,
                     "case": name, "phase": "baseline"})
    res = render(jobs, "A24", "jobs-all")
    for r in res:
        log_iteration("A24", {
            "iteration_id": "A24-" + os.path.basename(r["dsl"])[:-9],
            "parent": None, "type": "baseline", "round": None,
            "case_id": os.path.basename(r["dsl"])[:-9],
            "dsl": r["dsl"], "image": r["out"], "request_id": r["request_id"],
            "http_status": r["status"], "success": r["ok"], "bytes": r["bytes"],
            "duration_ms": r["ms"], "viewed_at": now() if r["ok"] else None,
            "observed": "rendered and opened with read_image" if r["ok"] else r["error"],
        })
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
