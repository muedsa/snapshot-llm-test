#!/usr/bin/env python
"""A18 探针三：嵌套圆角方块「芯片」节点（Positioned → Container → Stack → Positioned）+ 圆 + 连线。"""
from __future__ import annotations

import math
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
D = BASE / "tmp/run-20261011-01/A18/drafts"
R = "tmp/run-20261011-01/_suite/scripts/snapshot_render.py"


def chip(x, y, w, h, fill="#1D3ED8", inner="#0B1736", bc="#7DA7F5", r=None, r2=None):
    r = r if r is not None else round(w * 0.229, 1)
    iw, ih = round(w * 0.42), round(h * 0.42)
    ix, iy = round((w - iw) / 2), round((h - ih) / 2)
    r2 = r2 if r2 is not None else round(min(iw, ih) * 0.233, 1)
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
            f'<Container width="{w}" height="{h}" color="{fill}" borderRadius="{r}">'
            f'<Stack fit="EXPAND">'
            f'<Positioned left="{ix}" top="{iy}" width="{iw}" height="{ih}">'
            f'<Container width="{iw}" height="{ih}" color="{inner}" borderRadius="{r2}" '
            f'border="3 SOLID {bc}"/></Positioned>'
            f'</Stack></Container></Positioned>')


def unit(cx, cy, color, d=36):
    return (f'<Positioned left="{cx-d/2:.1f}" top="{cy-d/2:.1f}" width="{d}" height="{d}">'
            f'<ClipOval><Container width="{d}" height="{d}" color="{color}"/></ClipOval>'
            f'</Positioned>')


def link(x1, y1, x2, y2, color, w=3):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 1:
        return ""
    ang = math.degrees(math.atan2(dy, dx))
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return (f'<Positioned left="{(x1+x2)/2-L/2:.1f}" top="{(y1+y2)/2-w/2:.1f}" '
            f'width="{L:.1f}" height="{w}">'
            f'<Transform matrix="({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)" '
            f'alignment="CENTER"><Container width="{L:.1f}" height="{w}" color="{color}" '
            f'borderRadius="{w/2:.1f}"/></Transform></Positioned>')


DSL = ('<Snapshot type="png">\n<Container width="400" height="240" color="#F8FAFC">\n'
       '<Stack fit="EXPAND">\n'
       + link(90, 70, 196, 104, "#94A3B8")
       + unit(70, 60, "#2563EB") + unit(70, 100, "#EA7C2D") + unit(70, 140, "#94A3B8")
       + chip(220, 40, 96, 96)
       + unit(300, 180, "#2563EB")
       + '<Positioned left="20" top="196" width="360" height="30">'
         '<Text fontSize="16" color="#0F172A" fontFamily="Inter" '
         'text="chip + circles + link"/></Positioned>'
         + '</Stack>\n</Container>\n</Snapshot>\n')


def main() -> None:
    D.mkdir(parents=True, exist_ok=True)
    p = D / "p-f-chip.snapshot"
    p.write_text(DSL, encoding="utf-8")
    r = subprocess.run(
        [sys.executable, R, "--task", "A18", "--version", "p-f-chip", "--dsl", p.as_posix(),
         "--out", "tmp/run-20261011-01/A18/preview/p-f-chip.png",
         "--log", "tmp/run-20261011-01/A18/requests.jsonl",
         "--responses-dir", "tmp/run-20261011-01/A18/responses"],
        capture_output=True, text=True, encoding="utf-8")
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]
    print("ok=", '"ok": true' in last, last[:220])


if __name__ == "__main__":
    main()