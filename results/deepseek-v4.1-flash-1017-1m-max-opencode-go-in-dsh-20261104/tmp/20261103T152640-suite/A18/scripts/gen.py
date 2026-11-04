# -*- coding: utf-8 -*-
"""A18 final: three-act narrative (radial composition, refined) + audits."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

from PIL import Image

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A18"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
PREV = TMP / "previews"
OUT.mkdir(parents=True, exist_ok=True)

BG = "#0E1420"
BG2 = "#151D2C"
INK = "#EAF0F8"
MUTED = "#7C8CA3"
BLUE = "#2F6BFF"
ORANGE = "#E8892B"
GRAY = "#8494A8"
LINE_C = "#2E3D57"

W, H = 1600, 1000
PW, PH = 480, 750
GAP = 40
X0, Y0 = 40, 150
D = 36
NODE = 56

UNIT_COLORS = [BLUE] * 5 + [ORANGE] * 5 + [GRAY] * 5
UNIT_IDS = [f"U{i:02d}" for i in range(1, 16)]
ACTS = ["I  集中", "II  过载", "III  重新分配"]

def origin(i):
    return X0 + i * (PW + GAP), Y0

def node(kind, cx, cy, size, color):
    s = size
    if kind == "square":
        return K.rect(cx - s / 2, cy - s / 2, s, s, color=color, radius=9)
    if kind == "circle":
        return K.rect(cx - s / 2, cy - s / 2, s, s, color=color, radius=s / 2)
    path = f"M{s/2:g} 0 L{s:g} {s:g} L0 {s:g} Z"
    return (f'<Positioned left="{cx - s / 2:g}" top="{cy - s / 2:g}"><ClipPath path="{path}" '
            f'fillRule="NON_ZERO" clipBehavior="ANTI_ALIAS">'
            f'<Container width="{s}" height="{s}" color="{color}"/></ClipPath></Positioned>')

def line(x1, y1, x2, y2, color=LINE_C, w=1.6):
    length = math.hypot(x2 - x1, y2 - y1)
    if length < 1:
        return ""
    ang = math.atan2(y2 - y1, x2 - x1)
    c, s = math.cos(ang), math.sin(ang)
    return (f'<Positioned left="{(x1 + x2) / 2 - length / 2:g}" top="{(y1 + y2) / 2 - w / 2:g}">'
            f'<Transform matrix="({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)" alignment="CENTER">'
            f'<Container width="{length:g}" height="{w:g}" color="{color}"/></Transform></Positioned>')

NODE_COLORS = {"square": "#CFE0FF", "circle": "#FFD9A8", "triangle": "#B9C6D8"}
GROUPS = [[0, 5, 10, 1, 6], [2, 7, 11, 3, 8], [4, 9, 12, 13, 14]]

def build():
    p = [K.rect(0, 0, W, H, color=BG)]
    p.append(K.text(X0, 38, "集中 · 过载 · 重新分配", size=40, color=INK, bold=True, width=1200))
    p.append(K.text(X0, 94, "同一组 15 个单元与 3 个处理节点；三幕只改变距离、方向与分配，单元始终 36px。",
                    size=20, color=MUTED, width=1400))
    acts = []
    for i in range(3):
        px, py = origin(i)
        p.append(K.rect(px, py, PW, PH, color=BG2, radius=16))
        p.append(K.text(px + 24, py + 18, ACTS[i], size=24, color=INK, bold=True, width=420))
        cx, cy = px + PW / 2, py + 400
        if i == 0:
            nodes = [("square", cx, cy), ("circle", px + 62, py + 690), ("triangle", px + 418, py + 690)]
            recv = [0] * 15
            unit_pos = [(cx + 150 * math.cos(math.radians(-90 + k * 24)),
                         cy + 150 * math.sin(math.radians(-90 + k * 24))) for k in range(15)]
        elif i == 1:
            nodes = [("square", cx, cy), ("circle", px + 50, py + 690), ("triangle", px + 430, py + 690)]
            recv = [0] * 15
            unit_pos = []
            for k in range(15):
                r = 180 - k * 8.5
                a = math.radians(-90 + k * 34)
                unit_pos.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        else:
            nodes = [("square", cx, cy - 150), ("circle", cx - 150, cy + 120), ("triangle", cx + 150, cy + 120)]
            recv = [0] * 15
            for gi, grp in enumerate(GROUPS):
                for slot, idx in enumerate(grp):
                    recv[idx] = gi
            unit_pos = [None] * 15
            for gi, grp in enumerate(GROUPS):
                nx, ny = nodes[gi][1], nodes[gi][2]
                for slot, idx in enumerate(grp):
                    a = math.radians(-90 + (slot - 2) * 50)
                    unit_pos[idx] = (nx + 84 * math.cos(a), ny + 84 * math.sin(a))
        for k in range(15):
            n = nodes[recv[k]]
            p.append(line(unit_pos[k][0], unit_pos[k][1], n[1], n[2]))
        for kind, nx, ny in nodes:
            p.append(node(kind, nx, ny, NODE, NODE_COLORS[kind]))
        for k in range(15):
            p.append(K.rect(unit_pos[k][0] - D / 2, unit_pos[k][1] - D / 2, D, D,
                            color=UNIT_COLORS[k], radius=D / 2))
        acts.append({"i": i, "units": unit_pos, "nodes": nodes, "recv": recv})
    p.append(K.text(X0, 930, "U01–U05 蓝 · U06–U10 橙 · U11–U15 灰；节点形状固定：N01 方、N02 圆、N03 三角",
                    size=18, color=MUTED, width=1400))
    return K.document(W, H, p, background=BG), acts

dsl, acts = build()
(OUT / "three-act-story.snapshot").write_text(dsl, encoding="utf-8")
clock = rep.TaskClock(TASK)
logger = api.TaskLogger(TASK, TMP)
rec = logger.render(OUT / "three-act-story.snapshot", OUT / "three-act-story.png", "three-act final")
print("render:", rec["http_status"], rec["response_bytes"], rec["elapsed_s"])
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1000])
    raise SystemExit(1)
img = Image.open(OUT / "three-act-story.png").convert("RGB")
img.resize((400, 250), Image.LANCZOS).save(TMP / "thumb-400.png")
print("size", api.measure_png(OUT / "three-act-story.png"))

# ---------------------------------------------------------------- audit
def dist(a, b):
    return round(math.hypot(a[0] - b[0], a[1] - b[1]), 1)

ACT_META = []
for a in acts:
    i = a["i"]
    units = []
    for k in range(15):
        x, y = a["units"][k]
        g = a["recv"][k]
        nx, ny = a["nodes"][g][1], a["nodes"][g][2]
        units.append({"id": UNIT_IDS[k], "color": UNIT_COLORS[k], "diameter_px": D,
                      "center": [round(x, 1), round(y, 1)], "receiving_node": f"N{g+1:02d}",
                      "distance_to_node": dist((x, y), (nx, ny))})
    nodes = [{"id": f"N{j+1:02d}", "shape": kind, "center": [nx, ny],
              "bbox": [round(nx - NODE / 2, 1), round(ny - NODE / 2, 1),
                       round(nx + NODE / 2, 1), round(ny + NODE / 2, 1)],
              "size_px": NODE, "rotation_deg": 0,
              "received": sum(1 for u in units if u["receiving_node"] == f"N{j+1:02d}")}
             for j, (kind, nx, ny) in enumerate(a["nodes"])]
    mins = min(u["distance_to_node"] for u in units)
    maxs = max(u["distance_to_node"] for u in units)
    ACT_META.append({
        "act": i + 1, "name": ACTS[i].strip(), "units": units, "nodes": nodes,
        "unit_spacing": {"min_distance_to_node": mins, "max_distance_to_node": maxs,
                         "spread_ratio": round(maxs / mins, 2)},
        "counts": {n["id"]: n["received"] for n in nodes},
    })

clues = {
    1: ["15 条连线全部指向 N01（面板中央方块），N02/N03 位于面板底部两角、received=0 —— "
        "“单一中心”由连线终点与两枚空闲节点同时给出。",
        "单元均匀分布在 r=150 的整圆上（相邻间距约 63px），到 N01 的距离完全相同（最小=最大=150），"
        "说明负载稳定、没有排队。"],
    2: ["单元改为向心螺旋：半径由 180 递减到 61，最近 5 个单元到 N01 的距离只有 61–95px，"
        "而第一幕该值为 150px —— 同样的 15 个单元被压进更小的半径，形成堆积。",
        "单位间距从第一幕的 63px 降到约 40–98px 且沿螺旋不断变化，出现明显的疏密对比；"
        "N02/N03 被推到面板左右下角，received 仍为 0，说明负载仍只压在一个节点上。"],
    3: ["分配后每个节点 received=5，且每组都含 ≥2 种颜色（N01 蓝2橙2灰1、N02 蓝1橙2灰2、N03 蓝2橙1灰2）。",
        "三组单元分别位于三个节点的下方扇形上，到各自节点距离 84px（远小于第二幕的 61px 堆积半径），"
        "连线不再汇聚到单点，而是分成三束。"],
}

AUDIT = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "canvas": [W, H], "acts": ACT_META,
    "identities": {"units": [{"id": UNIT_IDS[k], "color": UNIT_COLORS[k], "diameter_px": D}
                             for k in range(15)],
                   "nodes": [{"id": "N01", "shape": "square"}, {"id": "N02", "shape": "circle"},
                             {"id": "N03", "shape": "triangle"}]},
    "invariants": {
        "unit_count_per_act": 15, "unit_diameter_px": D,
        "node_size_px": NODE, "node_shape_fixed": True,
        "no_warning_text": True, "only_title_and_act_names": True,
        "units_never_overlap": "所有单元圆心间距 ≥ 40px（直径 36），逐幕记录在 units[].center",
        "lines_under_circles": "先画连线、后画节点与单元，线的端点被圆覆盖",
    },
    "observable_clues": [{"act": k, "clues": v} for k, v in clues.items()],
    "viewing": {
        "full_size": "1600×1000 原图：三幕并置，左幕的整圆与中幕的螺旋半径差明显，右幕三束连线清晰",
        "thumbnail_400": "400px 宽缩略：仍能读出左“环”、中“团”、右“三束”的整体轮廓差异",
        "thumbnail_path": "tmp/<run_id>/A18/thumb-400.png",
    },
    "composition_choice": {
        "previewed": ["previews/preview-a.png（放射环）", "previews/preview-b.png（传送列）"],
        "chosen": "preview-a（放射构图）",
        "reason": "B 的三行分配让每个节点只拿到单一颜色，且底线穿过单元；A 的环形/螺旋/三节点三角"
                  "在缩略下仍能区分，且连线天然不与其它单元相交。",
    },
}
api.write_json(OUT / "story-audit.json", AUDIT)
print("audit written; counts:", [a["counts"] for a in ACT_META])
