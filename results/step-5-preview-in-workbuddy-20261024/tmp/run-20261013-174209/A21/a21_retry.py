#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重试 A21 指定轮次/尺寸的渲染（上一次网络超时）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))

from render import Log, render, suite_root, rel
from a21_layout import build

RUN_ID = "run-20261013-174209"
ROOT = suite_root()
TMP = ROOT / "tmp" / RUN_ID / "A21"
OUTBASE = ROOT / "outputs" / RUN_ID / "A21"
SIZES = {"portrait": (1080, 1350), "wide": (1440, 810)}

rnd = int(sys.argv[1])
only = sys.argv[2] if len(sys.argv) > 2 else None
log = Log(ROOT, RUN_ID, "A21")
outdir = OUTBASE / f"round-{rnd:02d}"
for size, (w, h) in SIZES.items():
    if only and size != only:
        continue
    sc = build(rnd, size)
    dsl_path = TMP / f"r{rnd}-{size}.snapshot"
    dsl_path.write_text(sc.dsl(), encoding="utf-8")
    r = render(dsl_path, outdir / f"launch-{size}.png", ROOT, log,
               label=f"A21-r{rnd}-{size}")
    (outdir / f"launch-{size}.snapshot").write_text(sc.dsl(), encoding="utf-8")
    print(f"[r{rnd} {size}] status={r['record']['status']} "
          f"http={r['record']['http_status']} "
          f"req={r['record']['request_id']} "
          f"elapsed={r['record']['elapsed_s']}s "
          f"dsl={len(sc.dsl().encode('utf-8'))}B err={r['record']['error']}")
