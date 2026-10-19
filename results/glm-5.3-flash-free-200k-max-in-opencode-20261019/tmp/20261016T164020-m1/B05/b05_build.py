# -*- coding: utf-8 -*-
"""B05 构建：把十屏 DSL 写入 tmp/<run>/B05/dsl/case-XX.snapshot（不覆盖旧版）。"""
import os
import sys
from pathlib import Path
from b05_common import CASES, wrap_dsl

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ.get("SNAPSHOT_RUN_ID", "20261016T164020-m1")
DSL_DIR = TASK_ROOT / "tmp" / RUN / "B05" / "dsl"
DSL_DIR.mkdir(parents=True, exist_ok=True)

import b05_cases_a  # noqa: F401,E402
import b05_cases_b  # noqa: F401,E402

made = []
suffix = sys.argv[1] if len(sys.argv) > 1 else ""
if not suffix and (DSL_DIR / "case-01.snapshot").exists():
    suffix = "_new"  # 防覆盖旧版
for mark, w, h, fn in CASES:
    body = []
    fn(body)
    path = DSL_DIR / (mark + suffix + ".snapshot")
    if path.exists():  # 不可覆盖旧版
        path = DSL_DIR / (mark + suffix + "_dup.snapshot")
    path.write_text(wrap_dsl(w, h, body, "#FFFFFF"), encoding="utf-8")
    made.append((mark, w, h, path.name))

print("cases:", len(made))
for m in made:
    print(" ", m)
