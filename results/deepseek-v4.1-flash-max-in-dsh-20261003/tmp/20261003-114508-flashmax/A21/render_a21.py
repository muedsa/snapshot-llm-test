"""A21 rendering driver: archives the current DSL per round, renders, and logs."""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_suite", "shared"))
from renderer import log_iteration, render  # noqa: E402
from suite_common import ROOT, now  # noqa: E402

R = "outputs/20261003-114508-flashmax/A21"
T = "tmp/20261003-114508-flashmax/A21"
NAMES = ("launch-portrait", "launch-wide")
PHASE = {1: "baseline", 2: "requirement-change", 3: "requirement-change"}


def archive(rnd: int) -> None:
    for nm in NAMES:
        src = os.path.join(ROOT, R, f"round-{rnd:02d}", f"{nm}.snapshot")
        dst = os.path.join(ROOT, T, f"{nm}.r{rnd}.v1.snapshot")
        shutil.copyfile(src, dst)


def main() -> None:
    rnds = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "1,2,3").split(",")]
    jobs = []
    for rnd in rnds:
        archive(rnd)
        for nm in NAMES:
            jobs.append({"dsl": f"{R}/round-{rnd:02d}/{nm}.snapshot",
                         "out": f"{R}/round-{rnd:02d}/{nm}.png",
                         "task": "A21", "prefix": "A21-REQ", "round": f"round-{rnd:02d}",
                         "case": None, "phase": PHASE[rnd]})
    res = render(jobs, "A21", f"jobs-r{'-'.join(str(r) for r in rnds)}")
    for r, j in zip(res, jobs):
        log_iteration("A21", {
            "iteration_id": f"A21-R{j['round']}-{os.path.basename(j['dsl'])[:-9]}",
            "parent": None if j["round"] == "round-01" else "previous round DSL",
            "type": PHASE[int(j["round"][-1])], "round": j["round"],
            "dsl": j["dsl"], "image": j["out"], "request_id": r["request_id"],
            "http_status": r["status"], "success": r["ok"], "bytes": r["bytes"],
            "duration_ms": r["ms"], "viewed_at": now() if r["ok"] else None,
            "observed": "rendered and opened with read_image" if r["ok"] else r["error"],
            "changes": "see snapshot-usage.md", "verified": None,
        })
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
