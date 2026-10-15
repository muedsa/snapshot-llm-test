#!/usr/bin/env python
"""A18 构件探针：六边形处理节点、Connect 线、有限形变、线不遮圆的裁剪算法。

启动基准：总任务根 (suite_root)。探针失败不阻塞后续：逐个独立 DSL。
"""
from __future__ import annotations

import math
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
D = BASE / "tmp/run-20261011-01/A18/drafts"
R = "tmp/run-20261011-01/_suite/scripts/snapshot_render.py"

HEX = ("<ClipPath><Polygon points=\"{pts}\" fill=\"#1D4ED8\"/></ClipPath>")


def hexagon(cx, cy, r, color="#1D4ED8"):
    pts = " ".join(f"{cx + r*math.cos(math.radians(a)):.1f},"
                   f"{cy + r*math.sin(math.radians(a)):.1f}"
                   for a in range(-90, 270, 60))
    return (f'<Positioned left="{cx-r:.1f}" top="{cy-r:.1f}" width="{2*r}" height="{2*r}">'
            f'{HEX.format(pts=pts)}</Positioned>').replace("#1D4ED8", color)


def link(x1, y1, x2, y2, color, w=3):
    """从两点连一条细线；两端按调用方给定的内缩量裁短，保证不压到圆与节点。"""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(dy, dx))
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    return (f'<Positioned left="{cx-L/2:.1f}" top="{cy-w/2:.1f}" width="{L:.1f}" height="{w}">'
            f'<Transform matrix="({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)" '
            f'alignment="CENTER"><Container width="{L:.1f}" height="{w}" color="{color}" '
            f'borderRadius="{w/2:.1f}"/></Transform></Positioned>')


def ring_unit(cx, cy, color, d=36):
    return (f'<Positioned left="{cx-d/2:.1f}" top="{cy-d/2:.1f}" width="{d}" height="{d}">'
            f'<ClipOval><Container width="{d}" height="{d}" color="{color}"/></ClipOval>'
            f'</Positioned>')


CASES = {
    # 六边形节点 + 圆 + 连接线
    "p-a-hex": '''<Snapshot type="png">
<Container width="400" height="240" color="#F8FAFC">
<Stack fit="EXPAND">
''' + link(90, 120, 200, 120, "#94A3B8")
    + ring_unit(70, 120, "#2563EB") + ring_unit(90, 60, "#EA7C2D")
    + hexagon(260, 120, 48) + ring_unit(330, 60, "#94A3B8")
    + f'''<Positioned left="150" top="180" width="120" height="30"><Text fontSize="16" color="#0F172A" fontFamily="Inter" text="hex + links"/></Positioned></Positioned>
</Stack>
</Container>
</Snapshot>
''',
    # 有限形变：同一个六边形换成 宽扁 的外包框
    "p-b-deform": '''<Snapshot type="png">
<Container width="400" height="240" color="#F8FAFC">
<Stack fit="EXPAND">
''' + hexagon(110, 120, 48) + hexagon(290, 120, 48).replace(
        f'left="{290-48:.1f}" top="{120-48:.1f}" width="96" height="96"',
        'left="236" top="72" width="108" height="72"')
    + f'''<Positioned left="60" top="200" width="120" height="30"><Text fontSize="16" color="#0F172A" fontFamily="Inter" text="base 96"/></Positioned>
<Positioned left="240" top="200" width="130" height="30"><Text fontSize="16" color="#0F172A" fontFamily="Inter" text="stretched"/></Positioned></Positioned>
</Stack>
</Container>
</Snapshot>
''',
    # 线裁剪：圆心 (60,60) 半径 18 → 连到 (200,200)，两端各内缩
    "p-c-trim": '''<Snapshot type="png">
<Container width="400" height="240" color="#F8FAFC">
<Stack fit="EXPAND">
''' + ring_unit(60, 60, "#2563EB")
    + link(60 + 24, 60 + 24, 200 - 54, 200 - 54, "#64748B")
    + hexagon(200, 200, 48)
    + f'''<Positioned left="40" top="150" width="200" height="30"><Text fontSize="16" color="#0F172A" fontFamily="Inter" text="trimmed link"/></Positioned></Positioned>
</Stack>
</Container>
</Snapshot>
''',
}


def main() -> None:
    D.mkdir(parents=True, exist_ok=True)
    for name, dsl in CASES.items():
        p = D / f"{name}.snapshot"
        p.write_text(dsl, encoding="utf-8")
        r = subprocess.run(
            [sys.executable, R, "--task", "A18", "--version", name, "--dsl", p.as_posix(),
             "--out", f"tmp/run-20261011-01/A18/preview/{name}.png",
             "--log", "tmp/run-20261011-01/A18/requests.jsonl",
             "--responses-dir", "tmp/run-20261011-01/A18/responses"],
            capture_output=True, text=True, encoding="utf-8")
        last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]
        ok = '"ok": true' in last
        print(f"[{name}] ok={ok} {'' if ok else last[:220]}")


if __name__ == "__main__":
    main()