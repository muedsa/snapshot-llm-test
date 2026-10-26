#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A23 · 封面文字实测宽度（渲染透明底文字后统计墨迹范围），用于回填安全盒。

每个测量都是一次独立的 /snapshot 渲染请求，类型记为 measure（与渲染分开统计）。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))
from render import Log, suite_root  # noqa: E402
from a23_net import send  # noqa: E402
import a23_gen as G  # noqa: E402

ROOT = suite_root()
RUN_ID = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN_ID / "A23"


def measure(text, size, style, family):
    dsl = (
        '<Snapshot type="png" background="transparent">'
        '<Container alignment="TOP_LEFT">'
        f'<Text fontSize="{size}" fontFamily="{family}" fontStyle="{style}" '
        f'textAlign="LEFT" softWrap="false" maxLines="1">'
        f'{G.esc(text)}</Text></Container></Snapshot>'
    )
    p = TMP / f"_measure-{abs(hash((text, size, style))) % 10 ** 8}.snapshot"
    p.write_text(dsl, encoding="utf-8")
    return p, dsl


def main():
    from PIL import Image
    import numpy as np
    log = Log(ROOT, RUN_ID, "A23")
    out = []
    for (tid, s, l, t, w, h, size, color, style) in G.cover_texts():
        if tid in ("rule",) or not s:
            continue
        fam = G.MONO if tid.startswith("chip") else G.SANS
        p, dsl = measure(s, size, style, fam)
        outpng = TMP / f"measure-{tid}.png"
        r = send(p, outpng, ROOT, log, req_type="measure",
                 label=f"A23-measure-{tid}")
        rec = r["record"]
        if rec["status"] != "ok":
            print(f"[{tid}] FAILED {rec['error']}")
            continue
        arr = np.asarray(Image.open(outpng))
        nz = arr[:, :, 3] > 8
        if not nz.any():
            print(f"[{tid}] empty ink")
            continue
        ys, xs = nz.nonzero()
        iw = int(xs.max() - xs.min() + 1)
        ih = int(ys.max() - ys.min() + 1)
        out.append({"id": tid, "text": s, "size": size, "style": style,
                    "box_w": w, "ink_w": iw, "ink_h": ih,
                    "ink_left": int(xs.min()), "ink_top": int(ys.min()),
                    "fits": iw <= w})
        print(f"[{tid}] size={size} ink={iw}x{ih} box_w={w} "
              f"{'OK' if iw <= w else 'OVERFLOW'}  req={rec['request_id']}")
    (TMP / "text-measures.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
