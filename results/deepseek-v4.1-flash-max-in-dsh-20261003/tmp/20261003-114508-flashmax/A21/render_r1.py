import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_suite", "shared"))
from renderer import render  # noqa: E402

R = "outputs/20261003-114508-flashmax/A21"
jobs = []
for name in ("launch-portrait", "launch-wide"):
    jobs.append({"dsl": f"{R}/round-01/{name}.snapshot", "out": f"{R}/round-01/{name}.png",
                 "task": "A21", "prefix": "A21-REQ", "round": "round-01",
                 "case": None, "phase": "baseline"})
print(json.dumps(render(jobs, "A21", "jobs-r1"), ensure_ascii=False))
