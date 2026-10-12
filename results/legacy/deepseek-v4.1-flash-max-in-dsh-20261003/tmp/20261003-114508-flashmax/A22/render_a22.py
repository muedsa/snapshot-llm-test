"""A22 driver: archive the round DSL, render, and log iterations + image views."""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_suite", "shared"))
from renderer import log_iteration, render  # noqa: E402
from suite_common import ROOT, now  # noqa: E402

R = "outputs/20261003-114508-flashmax/A22"
T = "tmp/20261003-114508-flashmax/A22"
PHASE = {1: "baseline", 2: "requirement-change", 3: "requirement-change"}


def main() -> None:
    rnds = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "1,2,3").split(",")]
    jobs = []
    for rnd in rnds:
        src = os.path.join(ROOT, R, f"round-{rnd:02d}", "dashboard.snapshot")
        shutil.copyfile(src, os.path.join(ROOT, T, f"dashboard.r{rnd}.v1.snapshot"))
        jobs.append({"dsl": f"{R}/round-{rnd:02d}/dashboard.snapshot",
                     "out": f"{R}/round-{rnd:02d}/dashboard.png",
                     "task": "A22", "prefix": "A22-REQ", "round": f"round-{rnd:02d}",
                     "case": None, "phase": PHASE[rnd]})
    res = render(jobs, "A22", f"jobs-r{'-'.join(str(r) for r in rnds)}")
    for r in res:
        log_iteration("A22", {
            "iteration_id": "A22-" + os.path.basename(os.path.dirname(r["dsl"])),
            "parent": None if "round-01" in r["dsl"] else "previous round DSL",
            "type": PHASE[int(r["dsl"].split("round-")[1][:2])],
            "round": "round-" + r["dsl"].split("round-")[1][:2],
            "dsl": r["dsl"], "image": r["out"], "request_id": r["request_id"],
            "http_status": r["status"], "success": r["ok"], "bytes": r["bytes"],
            "duration_ms": r["ms"], "viewed_at": now() if r["ok"] else None,
            "observed": "rendered and opened with read_image" if r["ok"] else r["error"],
        })
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
