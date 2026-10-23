"""A09 探针 4：完整仿射矩阵 + alignment="CENTER"，覆盖全部 12 个变换。

探针 3 已量出两种 pivot 语义（矩阵的平移项两者都不生效，只取 2×2 线性部分）：
  * 省略 alignment → 线性部分作用于子盒左上角 (0,0)：P1 rotCW90 实测局部
    x'∈[−40,−9]、rect3 [414,441] 与 L·p 完全一致，印章甩到参考框左侧；
  * alignment="CENTER" → 线性部分作用于子盒中心 (60,60)：P2 rotCW90 用完整
    仿射 (tx=120,ty=0) 预测为 (120−y, x)，实测逐形状零误差 PASS。
因此 alignment="CENTER" + 完整仿射矩阵 既能正确渲染，matrix 属性本身又
字面等于「以局部 (60,60) 为轴的最终组合变换」，符合题面要求。

本探针把该形式用在全部 12 个 transforms.json 变换上，另附 2 个纯平移单元
（Q13/Q14）把 renderer 对平移项的处理也一并钉住，供审计说明引用。
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[3] / "tools"))
os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
import a09_geom as G        # noqa: E402
import a09_parts as P       # noqa: E402
import suite as S           # noqa: E402

TASK = "A09"
RID = S.run_id()
CW, CH = 1160.0, 1140.0
ORIGIN = (100.0, 70.0)
CW_CELL, CH_CELL = 240.0, 250.0
BOX = G.SIZE
CX_OFF, CY_OFF = 120.0, 150.0
FRAME = 200.0
TAG = os.environ.get("PROBE_TAG", "probe4")

OPS = [
    {"op": "rotate", "deg": 0},
    {"op": "rotate", "deg": 90},
    {"op": "rotate", "deg": 180},
    {"op": "rotate", "deg": 270},
    {"op": "mirror_horizontal"},
    {"op": "mirror_vertical"},
    [{"op": "mirror_horizontal"}, {"op": "rotate", "deg": 90}],
    [{"op": "rotate", "deg": 90}, {"op": "mirror_horizontal"}],
    {"op": "scale_uniform", "s": 0.75},
    {"op": "scale_xy", "sx_sy": [1.25, 0.75]},
    {"op": "rotate", "deg": 30},
    [{"op": "mirror_vertical"}, {"op": "rotate", "deg": 30}],
]
NOTE = [
    "rotate 0°", "rotate 90°", "rotate 180°", "rotate 270°",
    "mirror_horizontal", "mirror_vertical",
    "①mirror_horizontal → ②rotate 90°",
    "①rotate 90° → ②mirror_horizontal",
    "scale_uniform 0.75", "scale_xy 1.25 × 0.75",
    "rotate 30°",
    "①mirror_vertical → ②rotate 30°",
]
# 额外两格：纯平移矩阵，确认 renderer 是否兑现矩阵的平移项
TRANSLATE = (1.0, 0.0, 0.0, 1.0, 20.0, 10.0)
EXTRA = [
    ("Q13 translate(20,10) 无 alignment", TRANSLATE, False),
    ("Q14 translate(20,10) alignment=CENTER", TRANSLATE, True),
]


def cell(i: int, tid: str, note: str, m_full, with_align: bool) -> str:
    """格内 Positioned 坐标一律相对格原点（父 Positioned 已带 cx,cy）。"""
    cx, cy = ORIGIN[0] + (i % 4) * CW_CELL, ORIGIN[1] + (i // 4) * CH_CELL
    bx, by = CX_OFF - BOX / 2.0, CY_OFF - BOX / 2.0
    layers = [
        P.pos(CX_OFF - FRAME / 2.0, CY_OFF - FRAME / 2.0, FRAME, FRAME,
              P.container(FRAME, FRAME, color="transparent", border="1 SOLID " + P.FRAME)),
        P.hline(CX_OFF - 14, CX_OFF + 14, CY_OFF, 2, P.FRAME),
        P.vline(CX_OFF, CY_OFF - 14, CY_OFF + 14, 2, P.FRAME),
        P.txt(10, 10, 220, 28, tid, 22),
        P.txt(10, 40, 220, 24, note, 15, color=P.INK3, bold=False),
        P.pos(bx, by, BOX, BOX, P.transform_box(G.mat_str(m_full),
                                                with_alignment=with_align)),
    ]
    return P.pos(cx, cy, CW_CELL, CH_CELL, P.stack(*layers))


def box_canvas_origin(i: int):
    cx, cy = ORIGIN[0] + (i % 4) * CW_CELL, ORIGIN[1] + (i // 4) * CH_CELL
    return (cx + CX_OFF - BOX / 2.0, cy + CY_OFF - BOX / 2.0)


def build_dsl() -> str:
    head = P.canvas_open(CW, CH)
    head += P.txt(24, 16, 1112, 34,
                  "A09 " + TAG + "：完整仿射矩阵 + alignment=CENTER（含 2 个纯平移对照）", 24)
    body = []
    for i, op in enumerate(OPS):
        m = G.compose([op] if isinstance(op, dict) else op)
        body.append(cell(i, "T%02d" % (i + 1), NOTE[i], m, True))
    for j, (label, m, wa) in enumerate(EXTRA):
        body.append(cell(12 + j, label.split(" ")[0], label.split(" ", 1)[1], m, wa))
    return head + "".join(body) + P.canvas_close()


def main() -> None:
    dsl = build_dsl()
    assert '""' not in dsl, "DSL 出现连续双引号，属性值会解析失败"
    dsl_path = HERE.parent / "dsl" / (TAG + "-transform.fullaffine.snapshot")
    dsl_path.write_text(dsl, encoding="utf-8")
    rid = "req-a09-" + TAG + "-fullaffine-" + uuid.uuid4().hex[:6]
    status, body, meta = S.snapshot_request(TASK, dsl, rid, kind="probe")
    S.log_request(TASK, {
        "request_id": rid, "task_id": TASK, "kind": "probe",
        "purpose": "用完整仿射矩阵 + alignment=CENTER 覆盖全部 12 个变换，"
                   "确认 matrix 属性字面等于最终组合变换且渲染正确；"
                   "另附 2 个纯平移对照钉住 renderer 对平移项的处理",
        "dsl_path": S.rel(dsl_path),
        "started_at": meta["started_at"], "ended_at": meta["ended_at"],
        "timezone": S.TZ_NAME, "elapsed_ms": meta["elapsed_ms"],
        "http_status": status, "content_type": meta["content_type"],
        "response_bytes": len(body),
        "server_timing": meta["headers"].get("server-timing"),
        "request_id_header": meta["headers"].get("x-request-id"),
    })
    (HERE.parent / "responses" / (rid + ".body")).write_bytes(body)
    (HERE.parent / "responses" / (rid + ".headers.txt")).write_text(
        "".join(f"{k}: {v}\n" for k, v in meta["headers"].items()), encoding="utf-8")
    if status == 200:
        png = HERE.parent / "preview" / (TAG + "-transform.fullaffine.png")
        png.write_bytes(body)
        print("OK", rid, len(body), "bytes ->", S.rel(png))
    else:
        print("FAIL", rid, status, S.error_summary(body))
    meta_out = {"run_id": RID, "request_id": rid, "http_status": status,
                "png": "tmp/%s/A09/preview/%s-transform.fullaffine.png" % (RID, TAG),
                "cells": []}
    for i, op in enumerate(OPS):
        m = G.compose([op] if isinstance(op, dict) else op)
        bx, by = box_canvas_origin(i)
        meta_out["cells"].append({
            "id": "T%02d" % (i + 1), "note": NOTE[i], "with_alignment": True,
            "ops": op if isinstance(op, list) else [op],
            "affine": [round(v, 7) for v in m],
            "matrix_flat": G.mat_flat(m),
            "box_origin": [bx, by], "box_center": [bx + BOX / 2.0, by + BOX / 2.0],
            "matrix_str": G.mat_str(m),
        })
    for j, (label, m, wa) in enumerate(EXTRA):
        bx, by = box_canvas_origin(12 + j)
        meta_out["cells"].append({
            "id": label.split(" ")[0], "note": label.split(" ", 1)[1],
            "with_alignment": wa, "ops": [{"op": "translate", "tx": 20, "ty": 10}],
            "affine": [round(v, 7) for v in m],
            "matrix_flat": G.mat_flat(m),
            "box_origin": [bx, by], "box_center": [bx + BOX / 2.0, by + BOX / 2.0],
            "matrix_str": G.mat_str(m),
        })
    (HERE.parent / (TAG + "-meta.json")).write_text(
        json.dumps(meta_out, ensure_ascii=False, indent=2), encoding="utf-8")
    for c in meta_out["cells"]:
        print(f"  {c['id']:4s} box=({c['box_origin'][0]:7.1f},{c['box_origin'][1]:7.1f})  "
              f"{c['note']}")


if __name__ == "__main__":
    main()
