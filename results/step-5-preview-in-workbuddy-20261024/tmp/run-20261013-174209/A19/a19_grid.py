"""A19 网格场景生成器：8x8 / 64 对象 -> DSL -> 真实服务渲染。

布局：1600x1600，每格 200x200，主体居中，ID 标签在格左上（主体外）。
形状：圆（直径=尺寸）/ 方（边长=尺寸）/ 圆环（外径=尺寸、内径=一半，
用 Container border 实现，边框绘于框内）/ 圆角方（外接边长=尺寸、圆角 12）。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))

from a19_data import (CANVAS, GRID, CELL, COLORS, RRECT_RADIUS, build_scene,
                      check_constraints, cell_box)
from render import Log, render, suite_root

ROOT = suite_root()
RUN_ID = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN_ID / "A19"
OUT = ROOT / "outputs" / RUN_ID / "A19"
TMP.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

GRID_LINE = "#E2E8F0"
ID_INK = "#64748B"
FAM = "Noto Sans CJK SC"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def subject_node(o: dict) -> str:
    cx, cy = o["center"]
    size = o["size"]
    color = o["color_hex"]
    shape = o["shape"]
    if shape == "ring":
        bw = size // 4                      # 边框宽 = 尺寸/4 -> 内孔 = 尺寸/2
        return (f'<Positioned left="{cx - size / 2:.2f}" top="{cy - size / 2:.2f}" '
                f'width="{size}" height="{size}">'
                f'<Container width="{size}" height="{size}" color="transparent" '
                f'shape="CIRCLE" border="{bw} SOLID {color}"/></Positioned>')
    if shape == "rounded-square":
        return (f'<Positioned left="{cx - size / 2:.2f}" top="{cy - size / 2:.2f}" '
                f'width="{size}" height="{size}">'
                f'<Container width="{size}" height="{size}" color="{color}" '
                f'borderRadius="{RRECT_RADIUS}"/></Positioned>')
    if shape == "square":
        return (f'<Positioned left="{cx - size / 2:.2f}" top="{cy - size / 2:.2f}" '
                f'width="{size}" height="{size}">'
                f'<Container width="{size}" height="{size}" color="{color}"/></Positioned>')
    # circle
    return (f'<Positioned left="{cx - size / 2:.2f}" top="{cy - size / 2:.2f}" '
            f'width="{size}" height="{size}">'
            f'<Container width="{size}" height="{size}" color="{color}" '
            f'shape="CIRCLE"/></Positioned>')


def label_node(o: dict) -> str:
    x0, y0, x1, y1 = o["id_label_box"]
    return (f'<Positioned left="{x0:.2f}" top="{y0:.2f}" width="{x1 - x0:.2f}" '
            f'height="{y1 - y0:.2f}">'
            f'<Container color="transparent" alignment="TOP_LEFT">'
            f'<Text fontSize="20" fontFamily="{FAM}" fontStyle="NORMAL" '
            f'color="{ID_INK}" textAlign="LEFT" softWrap="false" maxLines="1">'
            f'{esc(o["id"])}</Text>'
            f'</Container></Positioned>')


def grid_lines() -> list[str]:
    out = []
    for i in range(1, GRID):
        p = i * CELL
        out.append(f'<Positioned left="{p}" top="0" width="1" height="{CANVAS}">'
                   f'<Container width="1" height="{CANVAS}" color="{GRID_LINE}"/>'
                   f'</Positioned>')
        out.append(f'<Positioned left="0" top="{p}" width="{CANVAS}" height="1">'
                   f'<Container width="{CANVAS}" height="1" color="{GRID_LINE}"/>'
                   f'</Positioned>')
    return out


def build_dsl(objs: list[dict]) -> str:
    nodes = [f'<Positioned left="0" top="0" width="{CANVAS}" height="{CANVAS}">'
             f'<Container width="{CANVAS}" height="{CANVAS}" color="#FFFFFF"/>'
             f'</Positioned>']
    nodes += grid_lines()
    for o in objs:
        nodes.append(subject_node(o))
    for o in objs:
        nodes.append(label_node(o))
    return (f'<Snapshot type="png" background="#FFFFFF">'
            f'<Container width="{CANVAS}" height="{CANVAS}">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
            + "\n".join(nodes) + "</Stack></Container></Snapshot>")


def main() -> None:
    objs = build_scene()
    probs = check_constraints(objs)
    print(f"[data] 64 objects, constraint problems: {len(probs)}")
    for p in probs:
        print("  !", p)
    if probs:
        sys.exit(1)

    dsl = build_dsl(objs)
    dsl_path = TMP / "grid-scene.snapshot"
    dsl_path.write_text(dsl, encoding="utf-8")
    print(f"[dsl] {dsl_path.relative_to(ROOT).as_posix()}  {len(dsl.encode('utf-8'))} bytes")

    log = Log(ROOT, RUN_ID, "A19")
    out_png = OUT / "grid-scene.png"
    r = render(dsl_path, out_png, ROOT, log, label="A19-grid-scene")
    rec = r["record"]
    print(f"[render] status={rec['status']} http={rec['http_status']} "
          f"request_id={rec.get('request_id')} elapsed={rec.get('elapsed_s')}s")
    if rec["status"] != "ok":
        print("[render] FAILED:", rec.get("error"))
        sys.exit(1)

    # 同步 DSL 到输出目录（同名完整 .snapshot）
    (OUT / "grid-scene.snapshot").write_text(dsl, encoding="utf-8")
    print(f"[out] {out_png.relative_to(ROOT).as_posix()} "
          f"{out_png.stat().st_size} bytes")


if __name__ == "__main__":
    main()
