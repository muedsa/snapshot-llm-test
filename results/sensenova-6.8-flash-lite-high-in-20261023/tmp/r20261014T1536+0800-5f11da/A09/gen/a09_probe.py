"""A09 能力探针：确定 <Transform matrix> 的作用原点语义。

依据（本套已有证据，存在冲突，故必须实测）：
  * A03 交付件用列主序旋转矩阵 + alignment="CENTER" 成功绘出旋转卡片，
    实测外接框尺寸与「绕盒左上角旋转」的预测一致（164×75 vs 预测 166.2×77.7），
    但左上角比预测外移 (30.0, 44.3)；
  * A05 报告称「<Transform matrix> 只认纯平移，2×2 非单位矩阵时子树不画」。
两者矛盾。本探针在一张小画布上放 8 个真实印章，逐格量出实际外接框，
一次性判定：矩阵是否真的生效、作用原点是哪个点、alignment 是否引入偏移。

探针不是最终交付，只提交这一次；最终图谱另走一次提交。
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
import a09_geom as G          # noqa: E402
import suite as S             # noqa: E402

TASK = "A09"
RID = S.run_id()
FW, FH = 1000.0, 760.0       # 探针画布
CELL = 240.0
BOX = G.SIZE                 # 120
BOX_IN = (CELL - BOX) / 2    # 60，印章盒在格内的偏移
ORIGIN = (20.0, 20.0)
FONT = "Noto Sans CJK SC"
GRID = "#E2E8F0"
CELLBG = "#F8FAFC"
INK = "#0F172A"

def n(v: float) -> str:
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s else "0"

def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))

def txt(x, y, w, h, s, size, color=INK, bold=True, align="CENTER_LEFT"):
    """定位文本盒。alignment 取 Alignment 枚举名（LEFT/CENTER 等）。"""
    b = ' fontStyle="BOLD"' if bold else ""
    pos = '<Positioned left="{}" top="{}" width="{}" height="{}">'.format(
        n(x), n(y), n(w), n(h))
    box = '<Container width="{}" height="{}" alignment="{}">'.format(
        n(w), n(h), align)
    t = '<Text fontFamily="{}" fontSize="{}"{} color="{}">'.format(
        FONT, n(size), b, color)
    return pos + box + t + esc(s) + "</Text></Container></Positioned>"


def stamp_stack() -> str:
    """印章本体（局部坐标，120×120），含 3 个矩形与 1 个黑圆点。"""
    parts = []
    for r in G.STAMP["rectangles"]:
        x, y, w, h = r["xywh"]
        parts.append(f'<Positioned left="{n(x)}" top="{n(y)}" width="{n(w)}" '
                     f'height="{n(h)}"><Container width="{n(w)}" height="{n(h)}" '
                     f'color="{r["color"]}"></Container></Positioned>')
    cx, cy = G.STAMP["dot"]["center"]
    rad = G.STAMP["dot"]["radius"]
    parts.append(f'<Positioned left="{n(cx - rad)}" top="{n(cy - rad)}" '
                 f'width="{n(2 * rad)}" height="{n(2 * rad)}">'
                 f'<Container width="{n(2 * rad)}" height="{n(2 * rad)}" '
                 f'borderRadius="{n(rad)}" color="{G.STAMP["dot"]["color"]}">'
                 f'</Container></Positioned>')
    return f'<Stack width="{n(BOX)}" height="{n(BOX)}" fit="EXPAND" ' \
           f'clipBehavior="NONE">{"".join(parts)}</Stack>'

def transform_block(m, matrix_str, with_alignment):
    a = ' alignment="CENTER"' if with_alignment else ""
    return (f'<Transform matrix="{matrix_str}"{a}>'
            f'<Container width="{n(BOX)}" height="{n(BOX)}">'
            f'{stamp_stack()}</Container></Transform>')

# ---- 8 个探针 ----
M_ID = G.mat_identity()
M_R90 = G.mat_rotate_cw(90.0)
M_R90_NOT = (M_R90[0], M_R90[1], M_R90[2], M_R90[3], 0.0, 0.0)   # 去掉平移项
PROBES = [
    ("Q0", "identity + CENTER",            G.mat_str(M_ID),        True),
    ("Q1", "rotCW90 全矩阵 + CENTER",      G.mat_str(M_R90),       True),
    ("Q2", "mirror_h + CENTER",            G.mat_str(G.mat_mirror_h()), True),
    ("Q3", "scale0.75 + CENTER",           G.mat_str(G.mat_scale_uniform(0.75)), True),
    ("Q4", "rotCW90 去平移 + CENTER",      G.mat_str(M_R90_NOT),   True),
    ("Q5", "identity 无 alignment",        G.mat_str(M_ID),        False),
    ("Q6", "rotCW30 + CENTER",             G.mat_str(G.mat_rotate_cw(30.0)), True),
    ("Q7", "scale(1.25,0.75) + CENTER",    G.mat_str(G.mat_scale_xy(1.25, 0.75)), True),
]

def cell(c: int, r: int, tag: str, note: str, matrix_str: str, with_alignment: bool) -> str:
    lx, ly = ORIGIN[0] + c * CELL, ORIGIN[1] + r * CELL
    parts = [
        f'<Positioned left="0" top="0" width="{n(CELL)}" height="{n(CELL)}">'
        f'<Container width="{n(CELL)}" height="{n(CELL)}" color="{CELLBG}" '
        f'border="1 SOLID {GRID}"></Container></Positioned>',
        # 未变换的印章外框参考（不进入 Transform）
        f'<Positioned left="{n(BOX_IN)}" top="{n(BOX_IN)}" '
        f'width="{n(BOX)}" height="{n(BOX)}"><Container width="{n(BOX)}" '
        f'height="{n(BOX)}" color="transparent" '
        f'border="1 SOLID #CBD5E1"></Container></Positioned>',
        txt(lx + 12, ly + 10, 130, 26, tag, 22),
        txt(lx + 12, ly + 34, 216, 22, note, 13, color="#64748B", bold=False),
        f'<Positioned left="{n(lx + BOX_IN)}" top="{n(ly + BOX_IN)}">'
        + transform_block(None, matrix_str, with_alignment) + "</Positioned>",
    ]
    return (f'<Positioned left="{n(lx)}" top="{n(ly)}" width="{n(CELL)}" '
            f'height="{n(CELL)}"><Stack fit="EXPAND" clipBehavior="NONE">'
            + "".join(parts) + "</Stack></Positioned>")

def build_dsl() -> str:
    head = (f'<Snapshot type="png" background="#FFFFFF">'
            f'<Container width="{n(FW)}" height="{n(FH)}">'
            f'<Stack width="{n(FW)}" height="{n(FH)}" fit="EXPAND" '
            f'clipBehavior="NONE">')
    head += txt(20, 18, 900, 34, "A09 Transform.matrix 语义探针（8 例）", 24)
    body = []
    for i, (tag, note, mstr, wa) in enumerate(PROBES):
        body.append(cell(i % 4, i // 4, tag, note, mstr, wa))
    return head + "".join(body) + "</Stack></Container></Snapshot>"

def main() -> None:
    dsl = build_dsl()
    dsl_path = HERE.parent / "dsl" / "probe-transform.matrix.snapshot"
    dsl_path.write_text(dsl, encoding="utf-8")
    rid = f"req-a09-probe-transform-{uuid.uuid4().hex[:6]}"
    status, body, meta = S.snapshot_request(TASK, dsl, rid, kind="probe")
    S.log_request(TASK, {
        "request_id": rid, "task_id": TASK, "kind": "probe",
        "purpose": "判定 <Transform matrix> 是否生效、作用原点、alignment 偏移语义",
        "dsl_path": S.rel(dsl_path),
        "started_at": meta["started_at"], "ended_at": meta["ended_at"],
        "timezone": S.TZ_NAME, "elapsed_ms": meta["elapsed_ms"],
        "http_status": status, "content_type": meta["content_type"],
        "response_bytes": len(body),
        "server_timing": meta["headers"].get("server-timing"),
        "request_id_header": meta["headers"].get("x-request-id"),
    })
    (HERE.parent / "responses" / f"{rid}.body").write_bytes(body)
    (HERE.parent / "responses" / f"{rid}.headers.txt").write_text(
        "".join(f"{k}: {v}\n" for k, v in meta["headers"].items()), encoding="utf-8")
    if status == 200:
        png = HERE.parent / "preview" / "probe-transform.matrix.png"
        png.write_bytes(body)
        print("OK", rid, len(body), "bytes ->", S.rel(png))
    else:
        print("FAIL", rid, status, S.error_summary(body))
    print("矩阵列表：")
    for tag, note, mstr, wa in PROBES:
        print(f"  {tag} {note:32s} {mstr}")

if __name__ == "__main__":
    main()
