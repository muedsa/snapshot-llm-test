# -*- coding: utf-8 -*-
"""A13 品牌图标：两个几何方向预览（各 512×512 透明 PNG）。

方向一「叠层」：三枚错位胶囊（信息分层）+ 右上光点；母形以圆角矩形/圆为主，
        线性层叠构图，层间负空间表达"叠加后仍然清晰"。
方向二「光环」：圆环（EVEN_ODD 镂空）+ 横向光束 + 中心核点；母形以圆/圆环为主，
        径向构图，表达"光穿透叠加层"。

两个方向均 ≤6 个主要几何构件，几何参数集中在本文件，供后续
symbol/banner/poster 共用同一生成规则。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A13"
OUT_DIR = ROOT / "outputs" / RUN_ID / TASK
TMP_DIR = ROOT / "tmp" / RUN_ID / TASK
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))
import render as R  # noqa: E402

# ---------- 品牌色板 ----------
PALETTE = {
    "ink": "#0F172A",
    "blue_deep": "#1D4ED8",
    "blue": "#2563EB",
    "blue_mid": "#60A5FA",
    "blue_light": "#BFDBFE",
    "amber": "#F59E0B",
    "amber_deep": "#D97706",
}

S = 512  # 图标画布


def pill(x, y, w, h, color, r=None):
    r = r if r is not None else h / 2
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
            f'<Container color="{color}" borderRadius="{r}"/></Positioned>')


def dot(cx, cy, d, color):
    return (f'<Positioned left="{cx - d / 2}" top="{cy - d / 2}" width="{d}" height="{d}">'
            f'<Container color="{color}" borderRadius="{d / 2}"/></Positioned>')


def ring(cx, cy, d_out, d_in, color):
    """圆环：ClipPath + EVEN_ODD 双轮廓镂空。"""
    r1, r2 = d_out / 2, d_in / 2
    x0, x1 = cx - r1, cx + r1
    y0, y1 = cy - r1, cy + r1
    ix0, ix1 = cx - r2, cx + r2
    iy0, iy1 = cy - r2, cy + r2
    path = (f"M {x0} {cy} A {r1} {r1} 0 1 1 {x1} {cy} A {r1} {r1} 0 1 1 {x0} {cy} Z "
            f"M {ix0} {cy} A {r2} {r2} 0 1 1 {ix1} {cy} A {r2} {r2} 0 1 1 {ix0} {cy} Z")
    return (f'<Positioned left="0" top="0" width="{S}" height="{S}">'
            f'<ClipPath path="{path}" fillRule="EVEN_ODD" clipBehavior="ANTI_ALIAS">'
            f'<Container width="{S}" height="{S}" color="{color}"/>'
            f'</ClipPath></Positioned>')


# ---------- 方向一：叠层（3 胶囊 + 1 光点 = 4 构件） ----------
D1 = {
    "pills": [
        # (x, y, w, h, color)
        (112, 300, 288, 76, PALETTE["blue_light"]),
        (96, 224, 288, 76, PALETTE["blue_mid"]),
        (112, 148, 256, 76, PALETTE["blue"]),
    ],
    "light_dot": (400, 108, 48, PALETTE["amber"]),
}


def d1_nodes():
    n = [pill(*p) for p in D1["pills"]]
    cx, cy, d, c = D1["light_dot"]
    n.append(dot(cx, cy, d, c))
    return "".join(n)


# ---------- 方向二：光环（圆环 + 光束 + 核点 = 3 构件） ----------
D2 = {
    "ring": (256, 256, 300, 180, PALETTE["blue"]),
    "beam": (256, 256, 400, 56, PALETTE["amber"]),
    "core": (256, 256, 76, PALETTE["blue_deep"]),
}


def d2_nodes():
    n = [ring(*D2["ring"])]
    cx, cy, w, h, c = D2["beam"]
    n.append(pill(cx - w / 2, cy - h / 2, w, h, c))
    n.append(dot(*D2["core"]))
    return "".join(n)


def wrap(nodes):
    return (f'<Snapshot type="png" background="transparent">'
            f'<Container width="{S}" height="{S}">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
            + nodes + "</Stack></Container></Snapshot>")


for name, fn in (("preview-dir1-layers", d1_nodes), ("preview-dir2-ring", d2_nodes)):
    dsl = wrap(fn())
    (TMP_DIR / f"{name}.snapshot").write_text(dsl, encoding="utf-8")
    log = R.Log(ROOT, RUN_ID, TASK)
    res = R.render(TMP_DIR / f"{name}.snapshot", TMP_DIR / f"{name}.png", ROOT, log,
                   label=f"A13-{name}")
    print(name, res["record"]["status"], res["record"].get("error"))
print("done")
