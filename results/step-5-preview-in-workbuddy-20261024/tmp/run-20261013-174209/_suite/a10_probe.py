# -*- coding: utf-8 -*-
"""A10 probe: isolate the parentData error by rendering cells individually."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RUN_ID / "A10"
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))
import render as R  # noqa: E402

full = (TMP / "compositing-lab.snapshot").read_text(encoding="utf-8")
# 切出外层 Stack 的顶层子节点
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
print("top-level children:", len(parts))
# 只渲染单个 cell 的组合（cell 内元素 + 说明文字）
for k in range(1, 7):
    # 找该 cell 的元素：包含 'left="{ox}"' 的 Positioned
    pass

# 简化：逐个加元素直到出错
log = R.Log(ROOT, RUN_ID, "A10")
for n in [31, 32, 33, 34, 35, 36, 37, 38]:
    sub = (f'<Snapshot type="png" background="#EEF2F6">'
           f'<Container width="1440" height="1100">'
           f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
           + "".join(parts[:n]) + "</Stack></Container></Snapshot>")
    p = TMP / f"slice-{n}.snapshot"
    p.write_text(sub, encoding="utf-8")
    res = R.render(p, TMP / f"slice-{n}.png", ROOT, log, req_type="probe",
                   label=f"A10-slice-{n}")
    print(f"n={n}: {res['record']['status']} http={res['record']['http_status']} "
          f"{(res['record'].get('error') or '')[:90]}")
