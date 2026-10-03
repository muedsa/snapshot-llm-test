"""Re-run A01 metrics after cleaning a double-appended iterations.jsonl."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "_suite", "shared"))

TMP = os.path.join(HERE)
p = os.path.join(TMP, "iterations.jsonl")
os.remove(p)
print("removed iterations.jsonl, re-running writer")
exec(open(os.path.join(HERE, "write_metrics_a01.py"), encoding="utf-8").read())
