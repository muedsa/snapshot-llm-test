# -*- coding: utf-8 -*-
"""A13 方向一定稿预览：层间留负空间 + 光点贴合顶层。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RUN_ID / "A13"
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))
import render as R  # noqa: E402

S = 512


def pill(x, y, w, h, color, r=None):
    r = r if r is not None else h / 2
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
            f'<Container color="{color}" borderRadius="{r}"/></Positioned>')


def dot(cx, cy, d, color):
    return (f'<Positioned left="{cx - d / 2}" top="{cy - d / 2}" width="{d}" height="{d}">'
            f'<Container color="{color}" borderRadius="{d / 2}"/></Positioned>')


# 定稿几何（方向一：叠层，4 构件）
GEO = {
    "pills": [
        (128, 116, 256, 72, "#2563EB"),   # 前层（最深）
        (112, 220, 272, 72, "#60A5FA"),   # 中层
        (96, 324, 304, 72, "#BFDBFE"),    # 后层（最浅）
    ],
    "dot": (408, 152, 48, "#F59E0B"),     # 光点：贴前层右端
}

nodes = "".join(pill(*p) for p in GEO["pills"]) + dot(*GEO["dot"])
dsl = (f'<Snapshot type="png" background="transparent">'
       f'<Container width="{S}" height="{S}">'
       f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
       + nodes + "</Stack></Container></Snapshot>")
(TMP / "preview-dir1-v2.snapshot").write_text(dsl, encoding="utf-8")
log = R.Log(ROOT, RUN_ID, "A13")
res = R.render(TMP / "preview-dir1-v2.snapshot", TMP / "preview-dir1-v2.png", ROOT, log,
               label="A13-preview-dir1-v2")
print(res["record"]["status"], res["record"].get("error"))
