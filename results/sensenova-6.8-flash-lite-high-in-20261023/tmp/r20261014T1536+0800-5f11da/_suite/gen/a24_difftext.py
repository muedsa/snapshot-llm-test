"""提取两轮 decision-brief DSL 的文字集合，给出逐条差异。

只读：读取 tmp/<run>/A24/dsl/ 下两轮落盘的 .snapshot，用于重建 iterations.jsonl。
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
DSL = ROOT / "tmp" / RUN_ID / "A24" / "dsl"

RE_TEXT = re.compile(r'text="([^"]*)"')


def texts(path: pathlib.Path) -> list[str]:
    return RE_TEXT.findall(path.read_text(encoding="utf-8"))


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    old = texts(DSL / "req-a24-decision-brief-432409.snapshot")
    new = texts(DSL / "req-a24-decision-brief-c7590d.snapshot")
    print("round1 %d 段文字 / round2 %d 段文字" % (len(old), len(new)))
    co, cn = collections.Counter(old), collections.Counter(new)
    print("=== 只出现在 round1（被改掉） ===")
    for x, _ in (co - cn).most_common():
        print(" -", x)
    print("=== 只出现在 round2（新增/改写后） ===")
    for x, _ in (cn - co).most_common():
        print(" +", x)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
