import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_suite", "shared"))
from renderer import render  # noqa: E402

jobs = [{"dsl": "tmp/20261003-114508-flashmax/A21/probe-border.snapshot",
         "out": "tmp/20261003-114508-flashmax/A21/probe-border.png",
         "task": "A21", "prefix": "A21-REQ", "round": "setup", "case": "border-probe",
         "phase": "capability-probe"}]
print(json.dumps(render(jobs, "A21", "probe-border"), ensure_ascii=False))
