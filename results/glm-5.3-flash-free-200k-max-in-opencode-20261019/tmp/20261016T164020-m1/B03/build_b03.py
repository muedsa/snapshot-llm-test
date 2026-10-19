# -*- coding: utf-8 -*-
"""B03 顶层构建：十件落盘。"""
import json
import os
from b03_common import CASES, BASE, TASK_ROOT
import b03_cases_a  # noqa
import b03_cases_b  # noqa


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    plan = []
    seen = set()
    for mark, w, h, fn in CASES:
        d = BASE / mark
        d.mkdir(exist_ok=True)
        dsl = fn()
        (d / "final.snapshot").write_text(dsl, encoding="utf-8")
        if mark in seen:
            raise SystemExit(f"duplicate {mark}")
        seen.add(mark)
        plan.append({"id": mark, "w": w, "h": h, "bytes": len(dsl.encode("utf-8"))})
    if len(plan) != 10:
        raise SystemExit(f"expect 10, got {len(plan)}")
    tdir = TASK_ROOT / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "B03"
    tdir.mkdir(parents=True, exist_ok=True)
    with open(tdir / "dsl-plan.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)
    for p in plan:
        print(p["id"], p["w"], "x", p["h"], p["bytes"])


if __name__ == "__main__":
    main()
