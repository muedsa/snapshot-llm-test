"""A09 最终交付：十二变换图谱（1600×1200，4×3 格，每格 300×250，格距 32）。

硬约束落实：
  * 各格主体用 <Transform matrix="..."> 表示最终组合变换 —— matrix 属性是
    完整 2×3 仿射（列主序 4×4 十六数），字面等于「以局部 (60,60) 为轴的组合变换」；
    配 alignment="CENTER" 令作用原点为子盒中心，印章轴心恰与盒中心重合
    （探针 4 已在全部 12 个变换上逐形状验证，形心误差 ≤0.12 px）。
  * 圆点随同变换（T10 非均匀缩放下呈椭圆）。
  * 编号、操作短名、刻度辅助线（120×120 参考框 + 轴心十字 + 四边 0/60/120 短刻度）齐全。
  * 变换后的主体不被裁剪：Stack clipBehavior="NONE" 全链贯穿，且已逐格核算最远延伸。
  * 标签字号全部 ≥20 px。
  * 本脚本只提交一次最终版渲染。

几何：网格宽 4×300+3×32=1296、高 3×250+2×32=814；
      水平居中：左右留白各 (1600−1296)/2 = 152；
      垂直居中：上边界 (1200−814)/2 = 193，下边界 1007；
      列 x 152/484/816/1148，列中心 302/634/966/1298；
      行 y 193/475/757，行中心 318/600/882；
      标题带 0..178，图例 1015..1195（网格之外）。
格内：编号徽章 (10,12,58,32) + 操作短名 (76,17,214,28) 20px；
      舞台中心 (150,150)；120×120 参考框；四边 0/60/120 短刻度；轴心十字 30px。
最远延伸：T11 局部 x'∈[−4.03,124.03] → 格内 [85.97,214.03]，全在 300 内。
"""

from __future__ import annotations

import json
import os
import re
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

# ---- 画布与网格（水平、垂直均居中）----
CW, CH = 1600.0, 1200.0
CELL_W, CELL_H = 300.0, 250.0
GAP = 32.0
GRID_W = 4 * CELL_W + 3 * GAP          # 1296
GRID_H = 3 * CELL_H + 2 * GAP          # 814
GRID_OX = (CW - GRID_W) / 2.0          # 152
GRID_OY = (CH - GRID_H) / 2.0          # 193
# ---- 标题带（0..178）----
TITLE_Y, NOTE1_Y, NOTE2_Y, RULE_Y = 16.0, 70.0, 100.0, 177.0
# ---- 图例（网格之外）----
LEG_X, LEG_Y = GRID_OX, 1015.0
LEG_W, LEG_H = GRID_W, 180.0
LEG_COL = (LEG_W - 36.0) / 4.0         # 315 每列
LEG_PAD = 18.0
LEG_TITLE_Y, LEG_ROW_Y, LEG_ROW_H = 10.0, 48.0, 34.0
LEG_FOOT_Y = 148.0
# ---- 格内布局 ----
BADGE = (10.0, 12.0, 58.0, 32.0)
OPBOX = (76.0, 17.0, 214.0, 28.0)
STAGE_C = (150.0, 150.0)               # 印章盒中心＝格中心
FRAME = 120.0                          # 未变换的印章外框
TICK = 8.0
TICK_POS = (0.0, 60.0, 120.0)
CROSS = 30.0
WIN = 200.0                            # 像素量测窗口（含全部变换后主体）
TICKC = "#94A3B8"

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
OP_SHORT = [
    "rotate 0°", "rotate 90°", "rotate 180°", "rotate 270°",
    "mirror H", "mirror V",
    "①mirror H→②rot 90°",
    "①rot 90°→②mirror H",
    "scale 0.75", "scale 1.25×0.75",
    "rotate 30°",
    "①mirror V→②rot 30°",
]
LEG_TEXT = [
    "T01  rotate 0°",
    "T02  rotate 90°",
    "T03  rotate 180°",
    "T04  rotate 270°",
    "T05  mirror H（左右镜像）",
    "T06  mirror V（上下镜像）",
    "T07  ①mirror H → ②rot 90°",
    "T08  ①rot 90° → ②mirror H",
    "T09  scale_uniform 0.75",
    "T10  scale_xy (1.25, 0.75)",
    "T11  rotate 30°",
    "T12  ①mirror V → ②rot 30°",
]


def cell_origin(i: int):
    return (GRID_OX + (i % 4) * (CELL_W + GAP), GRID_OY + (i // 4) * (CELL_H + GAP))


def ops_of(op) -> list:
    return op if isinstance(op, list) else [op]


def stamp_box_cell(i: int):
    """第 i 格印章盒左上角（画布坐标）。盒中心＝格中心。"""
    cx, cy = cell_origin(i)
    return (cx + STAGE_C[0] - G.SIZE / 2.0, cy + STAGE_C[1] - G.SIZE / 2.0)


def measure_window_cell(i: int):
    """像素量测窗口：舞台中心 ±100，含全部变换后主体，且不含深色文字。"""
    cx, cy = cell_origin(i)
    x, y = cx + STAGE_C[0] - WIN / 2.0, cy + STAGE_C[1] - WIN / 2.0
    return (int(x), int(y), int(x + WIN), int(y + WIN))


def build_cell(i: int, tid: str, op_short: str, matrix_str: str) -> str:
    """一格内容。内部 Positioned 坐标一律相对格原点（父 Positioned 已带 cx,cy）。"""
    bx, by = STAGE_C[0] - G.SIZE / 2.0, STAGE_C[1] - G.SIZE / 2.0
    fx, fy = STAGE_C[0] - FRAME / 2.0, STAGE_C[1] - FRAME / 2.0
    layers = [
        # 格底
        P.pos(0, 0, CELL_W, CELL_H,
              P.container(CELL_W, CELL_H, color=P.CELLBG, radius=10,
                         border="1 SOLID " + P.EDGE)),
        # 编号
        P.pos(BADGE[0], BADGE[1], BADGE[2], BADGE[3],
              P.container(BADGE[2], BADGE[3], color=P.INK, radius=8, align="CENTER",
                         inner='<Text fontFamily="' + P.FONT + '" fontSize="22" '
                               'fontStyle="BOLD" color="#FFFFFF">' + tid + "</Text>")),
        # 操作短名（≥20 px）
        P.pos(OPBOX[0], OPBOX[1], OPBOX[2], OPBOX[3],
              P.container(OPBOX[2], OPBOX[3], align="CENTER_LEFT",
                         inner='<Text fontFamily="' + P.FONT + '" fontSize="20" '
                               'color="' + P.INK2 + '">' + P.esc(op_short) + "</Text>")),
        # 120×120 参考框（未变换的印章外框）
        P.pos(fx, fy, FRAME, FRAME,
              P.container(FRAME, FRAME, color=P.PANEL, border="1 SOLID " + P.FRAME)),
    ]
    # 四边 0/60/120 短刻度（刻度辅助线）
    for v in TICK_POS:
        lx, ly = fx + v, fy + v
        layers.append(P.vline(lx, fy - TICK, fy, 2, TICKC))
        layers.append(P.vline(lx, fy + FRAME, fy + FRAME + TICK, 2, TICKC))
        layers.append(P.hline(fx - TICK, fx, ly, 2, TICKC))
        layers.append(P.hline(fx + FRAME, fx + FRAME + TICK, ly, 2, TICKC))
    # 轴心十字（未变换，标记 pivot）
    layers.append(P.hline(STAGE_C[0] - CROSS / 2, STAGE_C[0] + CROSS / 2,
                          STAGE_C[1], 2, TICKC))
    layers.append(P.vline(STAGE_C[0], STAGE_C[1] - CROSS / 2,
                          STAGE_C[1] + CROSS / 2, 2, TICKC))
    # 主体：Transform.matrix 施加最终组合变换
    layers.append(P.pos(bx, by, G.SIZE, G.SIZE, P.transform_box(matrix_str)))
    cx, cy = cell_origin(i)
    return P.pos(cx, cy, CELL_W, CELL_H, P.stack(*layers))


def build_legend() -> str:
    parts = [
        P.pos(LEG_X, LEG_Y, LEG_W, LEG_H,
              P.container(LEG_W, LEG_H, color=P.PANEL, radius=10,
                         border="1 SOLID " + P.EDGE)),
        P.txt(LEG_X + LEG_PAD, LEG_Y + LEG_TITLE_Y, LEG_W - 2 * LEG_PAD, 28,
              "图例 · 编号 / 操作顺序（H＝左右镜像，V＝上下镜像；"
              "列主序 16 数完整矩阵与各形坐标见 geometry-audit.json）", 22),
    ]
    for i in range(12):
        ex = LEG_X + LEG_PAD + (i % 4) * LEG_COL
        ey = LEG_Y + LEG_ROW_Y + (i // 4) * LEG_ROW_H
        parts.append(P.txt(ex, ey, LEG_COL - 8, LEG_ROW_H - 4, LEG_TEXT[i], 22))
    parts.append(P.txt(LEG_X + LEG_PAD, LEG_Y + LEG_FOOT_Y, LEG_W - 2 * LEG_PAD, 24,
                       "刻度＝0 / 60 / 120 px；十字＝轴心 (60, 60)；"
                       "T07 与 T08 顺序不同，结果相差 180° 旋转；T11 det=+1 纯旋转，T12 det=−1 反射。",
                       20, color=P.INK3, bold=False))
    return P.stack(*parts)


def build_dsl() -> str:
    head = P.canvas_open(CW, CH)
    head += P.txt(40, TITLE_Y, 1520, 46,
                  "A09 · 十二变换图谱（Transform.matrix · 120×120 印章）", 38)
    head += P.txt(40, NOTE1_Y, 1520, 26,
                  "像素坐标 x 向右、y 向下，「顺时针」为图像（屏幕）方向；每步都围绕局部中心 (60, 60) 施加，"
                  "按 ①→② 顺序依次施加，故组合矩阵 M = M₂ ∘ M₁。", 20, color=P.INK2, bold=False)
    head += P.txt(40, NOTE2_Y, 1520, 26,
                  "浅框＝未变换的 120×120 印章框，十字＝轴心 (60, 60)，四边短刻度＝0 / 60 / 120 px；"
                  "各格主体由 Transform.matrix 施加最终组合变换，圆点随同变换。",
                  20, color=P.INK3, bold=False)
    head += P.hline(40, 1560, RULE_Y, 2, P.EDGE)
    body = []
    for i, op in enumerate(OPS):
        m = G.compose(ops_of(op))
        body.append(build_cell(i, "T%02d" % (i + 1), OP_SHORT[i], G.mat_str(m)))
    return head + "".join(body) + build_legend() + P.canvas_close()


def within_cell_local(cb) -> list:
    """格内是否裁切：把局部 bbox 换算成相对本格原点的坐标再比 300×250。

    印章盒相对格原点的偏移固定为 (90, 90)，不能用画布坐标直接比 300/250。
    """
    ox, oy = STAGE_C[0] - G.SIZE / 2.0, STAGE_C[1] - G.SIZE / 2.0
    lx0, ly0, lx1, ly1 = cb[0] + ox, cb[1] + oy, cb[2] + ox, cb[3] + oy
    return [lx0 >= 0.0, lx1 <= CELL_W, ly0 >= 0.0, ly1 <= CELL_H]


def collect_meta() -> dict:
    cells = []
    for i, op in enumerate(OPS):
        m = G.compose(ops_of(op))
        bx, by = stamp_box_cell(i)
        cx, cy = cell_origin(i)
        cb = G.transform_bbox(m, G.stamp_outline())
        cells.append({
            "id": "T%02d" % (i + 1),
            "ops": ops_of(op),
            "op_full": LEG_TEXT[i][4:].strip(),
            "op_short": OP_SHORT[i],
            "affine": [round(v, 7) for v in m],
            "matrix_flat": [round(v, 7) for v in G.mat_flat(m)],
            "matrix_str": G.mat_str(m),
            "cell_origin": [cx, cy],
            "cell_center": [cx + CELL_W / 2, cy + CELL_H / 2],
            "box_origin": [bx, by], "box_center": [bx + G.SIZE / 2, by + G.SIZE / 2],
            "stamp_bbox_local": [round(v, 4) for v in cb],
            "stamp_bbox_canvas": [round(cb[0] + bx, 4), round(cb[1] + by, 4),
                                  round(cb[2] + bx, 4), round(cb[3] + by, 4)],
            "measure_window": list(measure_window_cell(i)),
            "within_cell": within_cell_local(cb),
        })
    return {
        "run_id": RID,
        "canvas": [CW, CH],
        "grid": {"origin": [GRID_OX, GRID_OY], "cell": [CELL_W, CELL_H], "gap": GAP,
                 "cols": 4, "rows": 3, "width": GRID_W, "height": GRID_H,
                 "margin_left": GRID_OX, "margin_right": CW - GRID_OX - GRID_W,
                 "margin_top": GRID_OY, "margin_bottom": CH - GRID_OY - GRID_H,
                 "col_centers": [GRID_OX + c * (CELL_W + GAP) + CELL_W / 2
                                  for c in range(4)],
                 "row_centers": [GRID_OY + r * (CELL_H + GAP) + CELL_H / 2
                                 for r in range(3)]},
        "layout": {"title": [40, TITLE_Y, 1520, 46], "note1": [40, NOTE1_Y, 1520, 26],
                   "note2": [40, NOTE2_Y, 1520, 26], "rule": [40, 1560, RULE_Y, 2],
                   "badge": list(BADGE), "opbox": list(OPBOX),
                   "stage_center_cell": list(STAGE_C), "frame": FRAME,
                   "tick_len": TICK, "tick_pos": list(TICK_POS), "cross_len": CROSS,
                   "measure_window": WIN,
                   "legend": [LEG_X, LEG_Y, LEG_W, LEG_H]},
        "cells": cells,
    }


def preflight(meta: dict) -> None:
    """提交前的离线核对：不依赖服务响应。"""
    assert meta["grid"]["margin_left"] == meta["grid"]["margin_right"], "网格未水平居中"
    assert meta["grid"]["margin_top"] == meta["grid"]["margin_bottom"], "网格未垂直居中"
    assert meta["grid"]["width"] == 1296.0 and meta["grid"]["height"] == 814.0
    for c in meta["cells"]:
        x0, y0, x1, y1 = c["stamp_bbox_canvas"]
        assert x0 >= 0 and y0 >= 0 and x1 <= CW and y1 <= CH, c["id"]
        assert x0 >= c["cell_origin"][0], (c["id"], "主体超出本格左界")
        assert x1 <= c["cell_origin"][0] + CELL_W, (c["id"], "主体超出本格右界")
        assert y0 >= c["cell_origin"][1], (c["id"], "主体超出本格上界")
        assert y1 <= c["cell_origin"][1] + CELL_H, (c["id"], "主体超出本格下界")
        w, h = c["measure_window"][2] - c["measure_window"][0], c["measure_window"][3] - c["measure_window"][1]
        assert w == WIN and h == WIN
        # 窗口必须完整覆盖该格变换后的主体（否则边缘墨迹会被静默截断）
        wx0, wy0, wx1, wy1 = c["measure_window"]
        cx, cy = c["cell_origin"]
        assert wx0 <= x0 and wx1 >= x1, (c["id"], "窗口未覆盖主体 x 范围")
        assert wy0 <= y0 and wy1 >= y1, (c["id"], "窗口未覆盖主体 y 范围")
        # 窗口须覆盖 120×120 参考框
        assert wy0 <= cy + STAGE_C[1] - FRAME / 2, (c["id"], "窗口未覆盖参考框上界")
        assert wy1 >= cy + STAGE_C[1] + FRAME / 2, (c["id"], "窗口未覆盖参考框下界")
        # 深色文字不得落入量测窗口（INK 与圆点色 #111111 距离仅 25.7）
        assert wy0 > cy + OPBOX[1] + OPBOX[3], (c["id"], "量测窗口进入标题行文字区")
        assert wy1 <= cy + CELL_H and wx1 <= cx + CELL_W, (c["id"], "量测窗口越出本格")
    print("preflight OK：网格双向居中、12 格主体均在本格内、量测窗口几何一致")


def main() -> None:
    meta = collect_meta()
    preflight(meta)
    # --meta-only：只重算离线元数据（几何预测），不提交服务、不改写交付 DSL/PNG
    if "--meta-only" in sys.argv:
        out_dir, tmp_dir = S.task_dirs(TASK)
        (tmp_dir / "atlas-meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print("meta-only：未提交请求，已刷新", tmp_dir / "atlas-meta.json")
        return
    dsl = build_dsl()
    assert '""' not in dsl, "DSL 出现连续双引号，属性值会解析失败"
    out_dir, tmp_dir = S.task_dirs(TASK)   # outputs/<run_id>/A09, tmp/<run_id>/A09
    out = out_dir / "transform-atlas.snapshot"
    out.write_text(dsl, encoding="utf-8")
    rid = "req-a09-atlas-final-" + uuid.uuid4().hex[:6]
    status, body, meta_resp = S.snapshot_request(TASK, dsl, rid, kind="deliver")
    S.log_request(TASK, {
        "request_id": rid, "task_id": TASK, "kind": "deliver",
        "purpose": "A09 最终交付：4×3 十二变换图谱；各格主体由 Transform.matrix"
                   "（列主序 4×4，16 个有限数）施加最终组合变换，含编号/操作短名/刻度辅助线",
        "dsl_path": S.rel(out),
        "started_at": meta_resp["started_at"], "ended_at": meta_resp["ended_at"],
        "timezone": S.TZ_NAME, "elapsed_ms": meta_resp["elapsed_ms"],
        "http_status": status, "content_type": meta_resp["content_type"],
        "response_bytes": len(body),
        "server_timing": meta_resp["headers"].get("server-timing"),
        "request_id_header": meta_resp["headers"].get("x-request-id"),
    })
    (tmp_dir / "responses" / (rid + ".body")).write_bytes(body)
    (tmp_dir / "responses" / (rid + ".headers.txt")).write_text(
        "".join(f"{k}: {v}\n" for k, v in meta_resp["headers"].items()), encoding="utf-8")
    if status == 200:
        png = out_dir / "transform-atlas.png"
        png.write_bytes(body)
        meta["png"] = S.rel(png)
        meta["png_bytes"] = len(body)
        print("OK", rid, len(body), "bytes ->", S.rel(png))
    else:
        meta["error"] = S.error_summary(body)
        print("FAIL", rid, status, meta["error"])
    meta["request_id"] = rid
    meta["http_status"] = status
    (tmp_dir / "atlas-meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    for c in meta["cells"]:
        print(f"  {c['id']} {c['op_short']:22s} bbox_canvas={c['stamp_bbox_canvas']} "
              f"window={c['measure_window']}")


if __name__ == "__main__":
    main()
