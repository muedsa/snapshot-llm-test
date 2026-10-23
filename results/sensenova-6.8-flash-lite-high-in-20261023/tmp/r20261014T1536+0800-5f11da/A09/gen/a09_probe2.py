"""A09 探针 2：用 12 个真实变换逐一验证「以盒中心为轴」的矩阵形式。

背景：
  * 探针 1 暴露出布局脚本自身的坐标双重偏移（内部 Positioned 又加了一次格原点），
    导致 4 个格其实落在窗口外，NO_INK 不是渲染结论；
  * 本地复测 A03 交付件（注意其根 Container 带 padding="(32,32)"）后确认：
    <Transform matrix> 配 alignment="CENTER" 的作用原点是**子盒中心**，
    实测卡片外接框 (1076,660,1239,734) 与「绕盒中心旋转 −8°」的预测
    (1074.88,659.13,1241.12,736.87) 逐轴偏差 ≤3 px。
  * 印章轴心恰为局部 (60,60) = 盒中心，故矩阵只写 2x2 线性部分、平移项置 0，
    轴心即自动固定。

本探针把 inputs/transforms.json 的 12 个变换全部按该形式渲染一次，逐形状量出
外接框与预测值比较，既验证渲染语义，也提前验证最终图谱的每一格。
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
CW, CH = 1160.0, 1010.0
ORIGIN = (70.0, 60.0)
CW_CELL, CH_CELL = 260.0, 300.0
BOX = G.SIZE
CX_OFF, CY_OFF = 130.0, 178.0      # 盒中心在格内的偏移（框区 y∈[78,278]，文字 y≤66）
FRAME = 200.0
# 每轮探针用不同后缀，保留全部尝试，不覆盖上一次记录
TAG = os.environ.get("PROBE_TAG", "probe2")

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
    "① mirror_horizontal → ② rotate 90°",
    "① rotate 90° → ② mirror_horizontal",
    "scale_uniform 0.75", "scale_xy 1.25 × 0.75",
    "rotate 30°",
    "① mirror_vertical → ② rotate 30°",
]


def box_canvas_origin(i: int):
    """第 i 格印章盒左上角的画布坐标（cell() 用格内偏移、main() 用画布坐标，两者必须一致）。"""
    cx, cy = ORIGIN[0] + (i % 4) * CW_CELL, ORIGIN[1] + (i // 4) * CH_CELL
    return (cx + CX_OFF - BOX / 2.0, cy + CY_OFF - BOX / 2.0)


def cell(i: int, tid: str, note: str, matrix_str: str) -> str:
    """一格：内部 Positioned 坐标一律相对格原点（父 Positioned 已带 cx,cy）。

    格内偏移：参考框中心在 (CX_OFF, CY_OFF)，印章盒中心与之重合。
    文字在框上方（y ≤ 66），测量窗（参考框区域 y ∈ [78,278]）内没有文字。
    """
    cx, cy = ORIGIN[0] + (i % 4) * CW_CELL, ORIGIN[1] + (i // 4) * CH_CELL
    bx, by = CX_OFF - BOX / 2.0, CY_OFF - BOX / 2.0
    layers = [
        # 200×200 参考框（未变换的印章外框范围），浅灰描边
        P.pos(CX_OFF - FRAME / 2.0, CY_OFF - FRAME / 2.0, FRAME, FRAME,
              P.container(FRAME, FRAME, color="transparent",
                         border="1 SOLID " + P.FRAME)),
        # 轴心十字（2 px，浅灰）
        P.hline(CX_OFF - 14, CX_OFF + 14, CY_OFF, 2, P.FRAME),
        P.vline(CX_OFF, CY_OFF - 14, CY_OFF + 14, 2, P.FRAME),
        P.txt(8, 12, 244, 28, tid, 24),
        P.txt(8, 44, 244, 22, note, 15, color=P.INK3, bold=False),
        P.pos(bx, by, BOX, BOX, P.transform_box(matrix_str)),
    ]
    return P.pos(cx, cy, CW_CELL, CH_CELL, P.stack(*layers))


def build_dsl() -> str:
    head = P.canvas_open(CW, CH)
    head += P.txt(24, 20, 1112, 34,
                  "A09 " + TAG + "：12 个变换矩阵（以盒中心为轴，平移项为 0）逐格验证", 24)
    body = []
    for i, op in enumerate(OPS):
        m = G.compose([op] if isinstance(op, dict) else op)
        mlin = G.linear_of(m)
        body.append(cell(i, "T%02d" % (i + 1), NOTE[i], G.mat_str(mlin)))
    return head + "".join(body) + P.canvas_close()


def main() -> None:
    dsl = build_dsl()
    assert '""' not in dsl, "DSL 出现连续双引号，属性值会解析失败"
    dsl_path = HERE.parent / "dsl" / (TAG + "-transform.linear.snapshot")
    dsl_path.write_text(dsl, encoding="utf-8")
    rid = "req-a09-" + TAG + "-linear-" + uuid.uuid4().hex[:6]
    status, body, meta = S.snapshot_request(TASK, dsl, rid, kind="probe")
    S.log_request(TASK, {
        "request_id": rid, "task_id": TASK, "kind": "probe",
        "purpose": "用 12 个 transforms.json 的变换逐一验证「alignment=CENTER 以盒中心为轴、"
                   "矩阵只写 2x2 线性部分」的语义，并提前验证最终图谱每格",
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
        png = HERE.parent / "preview" / (TAG + "-transform.linear.png")
        png.write_bytes(body)
        print("OK", rid, len(body), "bytes ->", S.rel(png))
    else:
        print("FAIL", rid, status, S.error_summary(body))
    meta_out = {"run_id": RID, "request_id": rid, "http_status": status,
                "png": "tmp/%s/A09/preview/%s-transform.linear.png" % (RID, TAG),
                "cells": []}
    for i, op in enumerate(OPS):
        m = G.compose([op] if isinstance(op, dict) else op)
        bx, by = box_canvas_origin(i)
        # 与 cell() 内部的格内偏移 + 格原点保持一致，否则又会出现坐标双重偏移
        assert (bx, by) == (ORIGIN[0] + (i % 4) * CW_CELL + (CX_OFF - BOX / 2.0),
                            ORIGIN[1] + (i // 4) * CH_CELL + (CY_OFF - BOX / 2.0))
        meta_out["cells"].append({
            "id": "T%02d" % (i + 1), "note": NOTE[i],
            "ops": op if isinstance(op, list) else [op],
            "affine": [round(v, 7) for v in m],
            "matrix_linear": G.mat_flat(G.linear_of(m)),
            "box_origin": [bx, by],
            "box_center": [bx + BOX / 2.0, by + BOX / 2.0],
            "matrix_str": G.mat_str(G.linear_of(m)),
        })
    (HERE.parent / (TAG + "-meta.json")).write_text(
        json.dumps(meta_out, ensure_ascii=False, indent=2), encoding="utf-8")
    for c in meta_out["cells"]:
        print(f"  {c['id']} {c['note']:44s} box=({c['box_origin'][0]},{c['box_origin'][1]}) "
              f"matrix={c['matrix_str']}")


if __name__ == "__main__":
    main()
