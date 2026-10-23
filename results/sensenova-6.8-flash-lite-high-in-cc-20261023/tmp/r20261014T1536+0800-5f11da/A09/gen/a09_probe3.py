"""A09 探针 3：确定 Transform 省略 alignment 时的作用原点。

文档（缓存 dsl/reference-parser-tags.html.md.txt）：
  * Transform 属性表：matrix 必填；origin 否 "…，变换原点偏移"；
    alignment 否 **未设置**，"相对于子节点尺寸的变换对齐点"；
  * guides-painting：「alignment 决定变换中心」；
  * Alignment 合法值 TOP_LEFT … BOTTOM_RIGHT，以及 "(x,y)"。
推断：省略 alignment 时作用原点为子盒左上角 (0,0)，此时
    canvas = box_origin + M · p_local
且 M 就是「以局部 (60,60) 为轴的最终组合变换」本身 —— 这样 matrix 属性
就是题面要求的「最终组合变换」，无需拆掉平移项。

本探针用 6 格交叉验证：
  P0 单位矩阵 / P1 rotCW90 / P3 scale_xy / P4 mirror_h / P5 复合
      均用完整仿射 + **省略 alignment**；
  P2 rotCW90 完整仿射 + alignment="CENTER" 作为对照（预期偏移）。
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
CW, CH = 1000.0, 640.0
ORIGIN = (60.0, 70.0)
CW_CELL, CH_CELL = 300.0, 250.0
BOX = G.SIZE
CX_OFF, CY_OFF = 150.0, 150.0
FRAME = 200.0
TAG = os.environ.get("PROBE_TAG", "probe3")

PROBES = [
    ("P0 identity / 无 alignment", G.mat_identity(), False),
    ("P1 rotCW90 / 无 alignment", G.mat_rotate_cw(90.0), False),
    ("P2 rotCW90 / alignment=CENTER（对照）", G.mat_rotate_cw(90.0), True),
    ("P3 scale_xy 1.25×0.75 / 无 alignment", G.mat_scale_xy(1.25, 0.75), False),
    ("P4 mirror_horizontal / 无 alignment", G.mat_mirror_h(), False),
    ("P5 mv→rot30 / 无 alignment", G.compose([{"op": "mirror_vertical"},
                                              {"op": "rotate", "deg": 30}]), False),
]


def cell(i: int, tid: str, note: str, m_full, with_align: bool) -> str:
    """格内 Positioned 坐标一律相对格原点。"""
    cx, cy = ORIGIN[0] + (i % 3) * CW_CELL, ORIGIN[1] + (i // 3) * CH_CELL
    bx, by = CX_OFF - BOX / 2.0, CY_OFF - BOX / 2.0
    layers = [
        P.pos(CX_OFF - FRAME / 2.0, CY_OFF - FRAME / 2.0, FRAME, FRAME,
              P.container(FRAME, FRAME, color="transparent", border="1 SOLID " + P.FRAME)),
        P.hline(CX_OFF - 14, CX_OFF + 14, CY_OFF, 2, P.FRAME),
        P.vline(CX_OFF, CY_OFF - 14, CY_OFF + 14, 2, P.FRAME),
        P.txt(8, 12, 284, 28, tid, 24),
        P.txt(8, 44, 284, 22, note, 15, color=P.INK3, bold=False),
        P.pos(bx, by, BOX, BOX, P.transform_box(G.mat_str(m_full),
                                                with_alignment=with_align)),
    ]
    return P.pos(cx, cy, CW_CELL, CH_CELL, P.stack(*layers))


def box_canvas_origin(i: int):
    cx, cy = ORIGIN[0] + (i % 3) * CW_CELL, ORIGIN[1] + (i // 3) * CH_CELL
    return (cx + CX_OFF - BOX / 2.0, cy + CY_OFF - BOX / 2.0)


def build_dsl() -> str:
    head = P.canvas_open(CW, CH)
    head += P.txt(24, 18, 952, 34,
                  "A09 " + TAG + "：省略 alignment 时的作用原点（完整仿射矩阵）", 24)
    body = []
    for i, (label, m, wa) in enumerate(PROBES):
        body.append(cell(i, "P%d" % i, label.split(" / ")[1], m, wa))
    return head + "".join(body) + P.canvas_close()


def main() -> None:
    dsl = build_dsl()
    assert '""' not in dsl
    dsl_path = HERE.parent / "dsl" / (TAG + "-transform.noalignment.snapshot")
    dsl_path.write_text(dsl, encoding="utf-8")
    rid = "req-a09-" + TAG + "-noalignment-" + uuid.uuid4().hex[:6]
    status, body, meta = S.snapshot_request(TASK, dsl, rid, kind="probe")
    S.log_request(TASK, {
        "request_id": rid, "task_id": TASK, "kind": "probe",
        "purpose": "验证省略 Transform.alignment 时作用原点为子盒左上角，"
                   "从而使 matrix 属性直接等于以局部(60,60)为轴的最终组合变换",
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
        png = HERE.parent / "preview" / (TAG + "-transform.noalignment.png")
        png.write_bytes(body)
        print("OK", rid, len(body), "bytes ->", S.rel(png))
    else:
        print("FAIL", rid, status, S.error_summary(body))
    meta_out = {"run_id": RID, "request_id": rid, "http_status": status,
                "png": "tmp/%s/A09/preview/%s-transform.noalignment.png" % (RID, TAG),
                "cells": []}
    for i, (label, m, wa) in enumerate(PROBES):
        bx, by = box_canvas_origin(i)
        meta_out["cells"].append({
            "id": "P%d" % i, "label": label, "with_alignment": wa,
            "affine": [round(v, 7) for v in m],
            "matrix_flat": G.mat_flat(m),
            "box_origin": [bx, by], "box_center": [bx + BOX / 2.0, by + BOX / 2.0],
            "matrix_str": G.mat_str(m),
        })
    (HERE.parent / (TAG + "-meta.json")).write_text(
        json.dumps(meta_out, ensure_ascii=False, indent=2), encoding="utf-8")
    for c in meta_out["cells"]:
        print(f"  {c['id']} {c['label']:36s} box=({c['box_origin'][0]},{c['box_origin'][1]})")


if __name__ == "__main__":
    main()
