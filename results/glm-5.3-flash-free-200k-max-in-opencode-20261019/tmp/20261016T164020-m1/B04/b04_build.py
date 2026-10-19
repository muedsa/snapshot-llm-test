# -*- coding: utf-8 -*-
"""B04 构建：十件 DSL 生成。"""
from pathlib import Path
import b04_cases_a  # noqa: F401  (注册案例)
import b04_cases_b  # noqa: F401
from b04_common import CASES, wrap_dsl, CREAM, NAVY

DARK = {"case-02", "case-05", "case-06", "case-07"}
OUT = Path("dsl")
OUT.mkdir(exist_ok=True)

for mark, w, h, fn in CASES:
    s = []
    fn(s)
    bg = NAVY if mark in DARK else CREAM
    dsl = wrap_dsl(w, h, s, bg)
    p = OUT / f"{mark}.snapshot"
    p.write_text(dsl, encoding="utf-8")
    print(mark, w, h, len(dsl))
