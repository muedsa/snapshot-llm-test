# -*- coding: utf-8 -*-
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
with io.open("tmp/run-20261011-01/B04/iterations.jsonl", encoding="utf-8") as f:
    for line in f:
        e = json.loads(line)
        print(e["id"], "|", e.get("case_id"), "|", e["ts"])
