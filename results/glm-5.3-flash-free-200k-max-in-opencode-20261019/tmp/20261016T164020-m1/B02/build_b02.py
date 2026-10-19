# -*- coding: utf-8 -*-
"""B02 顶层构建：导入十件并落盘 DSL。"""
import json
import os
from b02_common import CASES, BASE
import b02_cases_a  # noqa: registers case-01..05
import b02_cases_b  # noqa: registers case-06..10


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    plan = []
    seen = set()
    for mark, w, h, fn in CASES:
        d = BASE / mark
        d.mkdir(exist_ok=True)
        dsl = fn()
        (d / "final.snapshot").write_text(dsl, encoding="utf-8")
        plan.append({"id": mark, "w": w, "h": h, "bytes": len(dsl.encode("utf-8"))})
        if mark in seen:
            raise SystemExit(f"duplicate {mark}")
        seen.add(mark)
    if len(plan) != 10:
        raise SystemExit(f"expect 10 cases, got {len(plan)}")
    tdir = TASK_ROOT / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "B02"
    tdir.mkdir(parents=True, exist_ok=True)
    with open(tdir / "dsl-plan.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)
    for p in plan:
        print(p["id"], p["w"], "x", p["h"], p["bytes"])


from b02_common import TASK_ROOT  # noqa: E402
if __name__ == "__main__":
    main()
