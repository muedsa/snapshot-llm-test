"""A20 渲染脚本：按 layout-draft.json 生成 annotated-map DSL 并请求真实服务渲染。

层次（从下到上）：主图区底板 -> 网格线 -> 刻度 -> 注解文字 -> 引导线 -> 点圆 ->
标签底板 -> 标签文字。引导线位于标签底板下层，避免描边遮文字。
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))

from render import Log, render, suite_root
from a20_layout import (ANNOTATIONS, CW, CH, MAP, MX0, MY0, MW, MH, MX1, MY1,
                        DISK_R, FS, PAD_X, PAD_Y, load, text_width, annot_box)

ROOT = suite_root()
RUN_ID = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN_ID / "A20"
OUT = ROOT / "outputs" / RUN_ID / "A20"

FAM = "Noto Sans CJK SC"
GRID_LINE = "#E2E8F0"
MAP_FILL = "#F8FAFC"
MAP_BORDER = "#94A3B8"
TICK = "#475569"
LEADER_C = "#64748B"
POINT_C = "#2563EB"
TOP_C = "#DC2626"
PLATE_B = "#CBD5E1"
INK = "#0F172A"
TOP_INK = "#B91C1C"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def positioned(left, top, w, h, inner):
    return (f'<Positioned left="{left:.2f}" top="{top:.2f}" width="{w:.2f}" '
            f'height="{h:.2f}">{inner}</Positioned>')


def text_node(s, left, top, w, h, size, color=INK, align="LEFT", style="NORMAL"):
    return positioned(left, top, w, h,
                      f'<Container color="transparent" alignment="TOP_LEFT">'
                      f'<Text fontSize="{size}" fontFamily="{FAM}" fontStyle="{style}" '
                      f'color="{color}" textAlign="{align}" softWrap="false" '
                      f'maxLines="1">{esc(s)}</Text></Container>')


def line_seg(x1, y1, x2, y2, w=2.0, color=LEADER_C):
    """任意角度线段：薄 Container + Transform 旋转矩阵（列主序 4x4，A18 实测结构：
    Transform 为 Positioned 的直接子节点并带 alignment=CENTER）。"""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return ""
    ux, uy = dx / L, dy / L
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    m = f"({ux:.6f},{uy:.6f},0,0,{-uy:.6f},{ux:.6f},0,0,0,0,1,0,0,0,0,1)"
    return (f'<Positioned left="{mx - L / 2:.2f}" top="{my - w / 2:.2f}" '
            f'width="{L:.2f}" height="{w:.2f}">'
            f'<Transform matrix="{m}" alignment="CENTER">'
            f'<Container width="{L:.2f}" height="{w:.2f}" color="{color}"/>'
            f'</Transform></Positioned>')


def build(ms, layout):
    nodes = []
    # 1 主图区底板（边框绘于框内 1px）
    nodes.append(positioned(MX0, MY0, MW, MH,
                            f'<Container width="{MW}" height="{MH}" color="{MAP_FILL}" '
                            f'border="1 SOLID {MAP_BORDER}"/>'))
    # 2 网格线（每 10 逻辑单位）
    for k in range(1, 10):
        gx = MX0 + MW * k / 10.0
        nodes.append(positioned(gx, MY0 + 1, 1, MH - 2,
                                f'<Container width="1" height="{MH - 2}" color="{GRID_LINE}"/>'))
        gy = MY1 - MH * k / 10.0
        nodes.append(positioned(MX0 + 1, gy, MW - 2, 1,
                                f'<Container width="{MW - 2}" height="1" color="{GRID_LINE}"/>'))
    # 3 刻度线
    for k in range(11):
        tx = MX0 + MW * k / 10.0
        nodes.append(positioned(tx, MY1, 1, 6,
                                f'<Container width="1" height="6" color="{TICK}"/>'))
        ty = MY1 - MH * k / 10.0
        nodes.append(positioned(MX0 - 8, ty, 8, 1,
                                f'<Container width="8" height="1" color="{TICK}"/>'))
    # 4 注解文字
    for name, text, left, top, size, align in ANNOTATIONS:
        _, box = annot_box(name, text, left, top, size, align)
        if align == "CENTER":
            cont_l = box[0] - 10
            cont_w = (box[2] - box[0]) + 20
        else:
            cont_l = box[0]
            cont_w = (box[2] - box[0]) + 20
        nodes.append(text_node(text, cont_l, box[1], cont_w, size * 1.5, size,
                               color=INK, align=align))
    # 5 刻度标签
    for k in range(11):
        tx = MX0 + MW * k / 10.0
        nodes.append(text_node(str(k * 10), tx - 30, 928, 60, 30, FS,
                               color=TICK, align="CENTER"))
        ty = MY1 - MH * k / 10.0
        nodes.append(text_node(str(k * 10), 196, ty - 15, 72, 30, FS,
                               color=TICK, align="RIGHT"))
    # 6 引导线（先于点与标签）
    for m in ms:
        ld = layout[m["id"]]["leader"]
        if not ld:
            continue
        for i in range(len(ld) - 1):
            nodes.append(line_seg(ld[i][0], ld[i][1], ld[i + 1][0], ld[i + 1][1]))
    # 7 点圆
    for m in ms:
        ax, ay = m["anchor"]
        c = TOP_C if m["top"] else POINT_C
        nodes.append(positioned(ax - DISK_R, ay - DISK_R, 2 * DISK_R, 2 * DISK_R,
                                f'<Container width="{2 * DISK_R}" height="{2 * DISK_R}" '
                                f'color="{c}" shape="CIRCLE"/>'))
    # 8 标签底板 + 文字
    for m in ms:
        box = layout[m["id"]]["box"]
        w, h = box[2] - box[0], box[3] - box[1]
        border = f'2 SOLID {TOP_C}' if m["top"] else f'1 SOLID {PLATE_B}'
        nodes.append(positioned(box[0], box[1], w, h,
                                f'<Container width="{w:.2f}" height="{h:.2f}" '
                                f'color="#FFFFFF" borderRadius="8" border="{border}"/>'))
        nodes.append(text_node(m["text"], box[0] + PAD_X, box[1] + PAD_Y,
                               w - 2 * PAD_X, FS * 1.5, FS,
                               color=TOP_INK if m["top"] else INK))
    return (f'<Snapshot type="png" background="#FFFFFF">'
            f'<Container width="{CW}" height="{CH}">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
            + "\n".join(nodes) + "</Stack></Container></Snapshot>")


def main():
    ms, top3 = load()
    layout = json.loads((TMP / "layout-draft.json").read_text(encoding="utf-8"))
    dsl = build(ms, layout)
    dsl_path = TMP / "annotated-map.snapshot"
    dsl_path.write_text(dsl, encoding="utf-8")
    print(f"[dsl] {dsl_path.relative_to(ROOT).as_posix()}  {len(dsl.encode('utf-8'))} bytes")

    log = Log(ROOT, RUN_ID, "A20")
    out_png = OUT / "annotated-map.png"
    r = render(dsl_path, out_png, ROOT, log, label="A20-annotated-map")
    rec = r["record"]
    print(f"[render] status={rec['status']} http={rec['http_status']} "
          f"request_id={rec.get('request_id')} elapsed={rec.get('elapsed_s')}s")
    if rec["status"] != "ok":
        print("[render] FAILED:", rec.get("error"))
        sys.exit(1)
    (OUT / "annotated-map.snapshot").write_text(dsl, encoding="utf-8")
    print(f"[out] {out_png.relative_to(ROOT).as_posix()} {out_png.stat().st_size} bytes")


if __name__ == "__main__":
    main()
