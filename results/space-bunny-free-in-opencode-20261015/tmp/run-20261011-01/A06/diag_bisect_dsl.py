#!/usr/bin/env python
"""A06 渲染错误二分定位：把生成 DSL 的顶层 Positioned 逐段截断重渲，找到首个失败片段。"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
SRC = ROOT / "tmp/run-20261011-01/A06/drafts/a06-v3.snapshot"
OUT = ROOT / "tmp/run-20261011-01/A06/drafts/_bisect.snapshot"

text = SRC.read_text(encoding="utf-8-sig")
head, body, tail = text.partition('<Stack fit="EXPAND">\n')
marker = "\n</Stack>\n</Container>\n</Snapshot>"
idx = tail.rindex(marker)
inner = tail[:idx]
rest = tail[idx:]

# 按顶层子节点切分（保持括号平衡）
parts, depth, cur = [], 0, ""
i = 0
while i < len(inner):
    ch = inner[i]
    if ch == "<" and i + 1 < len(inner) and inner[i + 1] != "/":
        j = inner.index(">", i)
        if inner[j - 1] != "/":
            depth += 1
        cur += inner[i:j + 1]
        i = j + 1
        continue
    if ch == "<" and inner.startswith("</", i):
        j = inner.index(">", i)
        depth -= 1
        cur += inner[i:j + 1]
        i = j + 1
        if depth == 0:
            parts.append(cur)
            cur = ""
        continue
    cur += ch
    i += 1
if cur.strip():
    parts.append(cur)

print("segments:", len(parts))
lo, hi = 0, len(parts)


def render(k):
    dsl = head + '<Stack fit="EXPAND">' + "".join(parts[:k]) + "</Stack>" + rest
    OUT.write_text(dsl, encoding="utf-8")
    p = subprocess.run([sys.executable, str(ROOT / "tmp/run-20261011-01/_suite/scripts/snapshot_render.py"),
                        "--task", "A06", "--version", "bisect", "--dsl",
                        "tmp/run-20261011-01/A06/drafts/_bisect.snapshot",
                        "--out", "tmp/run-20261011-01/A06/preview/_bisect.png",
                        "--log", "tmp/run-20261011-01/A06/requests.jsonl",
                        "--responses-dir", "tmp/run-20261011-01/A06/responses"],
                       capture_output=True, text=True, cwd=str(ROOT))
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])["ok"]
    except Exception:
        return False


while lo < hi:
    mid = (lo + hi) // 2
    ok = render(mid + 1)
    print(f"k={mid + 1} ok={ok}")
    if ok:
        lo = mid + 1
    else:
        hi = mid
print("first failing segment index:", lo)
print(parts[lo][:400] if lo < len(parts) else "(none)")