#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重试 A21 第三轮去文字辅助渲染（对比度审计的背景来源）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))

from render import Log, render, suite_root
from a21_layout import build

RUN_ID = "run-20261013-174209"
ROOT = suite_root()
TMP = ROOT / "tmp" / RUN_ID / "A21"
log = Log(ROOT, RUN_ID, "A21")
for size in ("portrait", "wide"):
    sc = build(3, size, no_text=True)
    p = TMP / f"r3-{size}-notext.snapshot"
    p.write_text(sc.dsl(), encoding="utf-8")
    r = render(p, TMP / f"r3-{size}-notext.png", ROOT, log,
               label=f"A21-r3-{size}-notext")
    print(f"[{size}-notext] status={r['record']['status']} "
          f"req={r['record']['request_id']} "
          f"elapsed={r['record']['elapsed_s']}s "
          f"dsl={len(sc.dsl().encode('utf-8'))}B err={r['record']['error']}")
