#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DSL 自检：实体泄漏 / 标签内换行 / matrix 格式。"""
import re
import sys
from pathlib import Path

PAT = re.compile(r'^\((-?[01]\.\d{10})(,-?[01]\.\d{10}){15}\)$')


def check(path: str) -> bool:
    t = Path(path).read_text(encoding='utf-8')
    ents = len(re.findall(r'&(gt|lt|amp);', t))
    bad_nl = len(re.findall(r'<[\r\n]', t))
    ms = re.findall(r'matrix="([^"]*)"', t)
    bad_m = [m for m in ms if not PAT.match(m)]
    ok = not ents and not bad_nl and not bad_m
    print(f"{Path(path).name}: nodes={t.count('<Positioned')} matrices={len(ms)} "
          f"entities={ents} bad_nl={bad_nl} bad_matrix={len(bad_m)} "
          f"{'OK' if ok else 'FAIL'}")
    if bad_m:
        print('  sample bad:', bad_m[:2])
    return ok


if __name__ == "__main__":
    sys.exit(0 if all(check(p) for p in sys.argv[1:]) else 1)
