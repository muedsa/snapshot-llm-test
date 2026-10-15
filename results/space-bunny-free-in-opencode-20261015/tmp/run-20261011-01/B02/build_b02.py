#!/usr/bin/env python
# B02 生成器：十个触点各自一份完整 DSL。
# 启动基准：总任务根 (suite_root)。用法：python build_b02.py [all|1..10] [ver]
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/B02"))
from cases_b02_a import tp01, tp02, tp03, tp04, tp05
from cases_b02_b import tp06, tp07, tp08, tp09, tp10

DRAFTS = ROOT / "tmp/run-20261011-01/B02/drafts"

SIZES = {1: (1600, 600), 2: (1050, 600), 3: (1240, 1754), 4: (1400, 1980),
         5: (720, 1560), 6: (560, 1200), 7: (1200, 800), 8: (900, 1200),
         9: (1400, 900), 10: (1600, 1000)}


def main() -> None:
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    ver = sys.argv[2] if len(sys.argv) > 2 else "v1"
    DRAFTS.mkdir(parents=True, exist_ok=True)
    fns = [tp01, tp02, tp03, tp04, tp05, tp06, tp07, tp08, tp09, tp10]
    idx = range(10) if which == "all" else [int(which) - 1]
    for i in idx:
        p = DRAFTS / f"tp-{i + 1:02d}-{ver}.snapshot"
        p.write_text(fns[i](), encoding="utf-8")
        w, h = SIZES[i + 1]
        print(f"-> {p.name}  {w}x{h}  {p.stat().st_size} bytes")


if __name__ == "__main__":
    main()