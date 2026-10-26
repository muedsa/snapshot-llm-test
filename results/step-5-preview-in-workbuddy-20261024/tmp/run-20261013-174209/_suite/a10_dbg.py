# -*- coding: utf-8 -*-
"""Inspect A10 top-level element 31."""
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RUN_ID / "A10"

full = (TMP / "compositing-lab.snapshot").read_text(encoding="utf-8")
m = re.search(r'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">(.*)</Stack></Container></Snapshot>', full, re.S)
inner = m.group(1)


def split_top(s):
    parts, depth, start = [], 0, None
    i = 0
    while i < len(s):
        if s[i] == "<":
            j = s.find(">", i)
            if j == -1:
                break
            tag = s[i + 1:j]
            selfclose = tag.endswith("/")
            if not selfclose and not tag.startswith("/"):
                if depth == 0:
                    start = i
                depth += 1
            elif tag.startswith("/"):
                depth -= 1
                if depth == 0:
                    parts.append(s[start:j + 1])
            else:
                if depth == 0:
                    parts.append(s[i:j + 1])
            i = j + 1
        else:
            i += 1
    return parts


parts = split_top(inner)
for i in [29, 30, 31]:
    print(f"--- element {i+1} (len {len(parts[i])}) ---")
    print(parts[i][:600])
    print()
