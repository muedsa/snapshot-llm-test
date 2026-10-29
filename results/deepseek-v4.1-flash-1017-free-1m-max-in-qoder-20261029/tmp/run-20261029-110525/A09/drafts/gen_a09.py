#!/usr/bin/env python3
"""A09 transform atlas: 12 stamps via Transform.matrix, 4x3 grid, geometry audit."""
import json, os, math, html
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A09"
OUT.mkdir(parents=True, exist_ok=True)
TASK = SUITE_ROOT / "tasks/A09-transform-atlas"

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#0B1220", bold=False, extra=""):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

stamp = json.loads((TASK / "inputs/stamp.json").read_text(encoding="utf-8"))
transforms = json.loads((TASK / "inputs/transforms.json").read_text(encoding="utf-8"))
PIVOT = stamp["pivot"]
SHORT = {"T01": "原始", "T02": "R90°", "T03": "R180°", "T04": "R270°", "T05": "水平镜像", "T06": "垂直镜像",
         "T07": "镜像→R90", "T08": "R90→镜像", "T09": "缩放 0.75", "T10": "缩放 1.25×0.75", "T11": "R30°", "T12": "镜像→R30"}

def mm(A, B):
    a, b, c, d, e, f = A; a2, b2, c2, d2, e2, f2 = B
    return (a * a2 + c * b2, b * a2 + d * b2,
            a * c2 + c * d2, b * c2 + d * d2,
            a * e2 + c * f2 + e, b * e2 + d * f2 + f)

def apply(M, x, y):
    a, b, c, d, e, f = M
    return (a * x + c * y + e, b * x + d * y + f)

def op_matrix(op):
    name, val = op
    px, py = PIVOT
    if name == "rotate_clockwise_deg":
        t = math.radians(val); cs, sn = math.cos(t), math.sin(t)
        return (cs, sn, -sn, cs, px - cs * px + sn * py, py - sn * px - cs * py)
    if name == "mirror_horizontal":
        return (-1, 0, 0, 1, 2 * px, 0)
    if name == "mirror_vertical":
        return (1, 0, 0, -1, 0, 2 * py)
    if name == "scale_uniform":
        return (val, 0, 0, val, px * (1 - val), py * (1 - val))
    if name == "scale_xy":
        sx, sy = val
        return (sx, 0, 0, sy, px * (1 - sx), py * (1 - sy))
    raise ValueError(name)

def combined(ops):
    M = (1, 0, 0, 1, 0, 0)
    for op in ops:
        M = mm(op_matrix(op), M)
    return M

def mstr(M):
    a, b, c, d, e, f = M
    return f"({a:.9f},{b:.9f},0,0,{c:.9f},{d:.9f},0,0,0,0,1,0,{e:.9f},{f:.9f},0,1)"

W, H = 1600, 1200
CW, CH, GAP = 300, 250, 32
GX, GY = 152, 260

parts = ['<Snapshot background="#F6F7FB" type="png">', '<Container width="1600" height="1200"><Stack alignment="TOP_LEFT"><Container width="1600" height="1200" color="#F6F7FB"/>']
parts.append('<Positioned left="40" top="34"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("TRANSFORM ATLAS / MATRIX STUDY", 14, "#2563EB", True, ' letterSpacing="2"') + T("十二个非对称图形变换标本", 40, "#0B1220", True) + T("所有局部坐标以印章左上角为原点；每步围绕 (60,60)；格内十字与 50px 刻度用于核对", 20, "#56637A") + '</Column></Positioned>')
# legend stamp preview
parts.append('<Positioned right="40" top="34"><Row crossAxisAlignment="CENTER"><Container width="120" height="120" color="#FFFFFF" border="1 SOLID #DCE3EE" borderRadius="10"><Stack alignment="TOP_LEFT" clipBehavior="NONE"><Container width="120" height="120" color="#FFFFFF"/>')
for r in stamp["rectangles"]:
    x, y, w, h = r["xywh"]
    parts.append(f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Container width="{w}" height="{h}" color="{r["color"]}"/></Positioned>')
d = stamp["dot"]
parts.append(f'<Positioned left="{d["center"][0]-d["radius"]}" top="{d["center"][1]-d["radius"]}" width="{d["radius"]*2}" height="{d["radius"]*2}"><Container width="{d["radius"]*2}" height="{d["radius"]*2}" color="{d["color"]}" shape="CIRCLE"/></Positioned>')
parts.append('</Stack></Container><SizedBox width="14"/><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("原始印章", 20, "#0B1220", True) + T("120 × 120 · 透明底", 18, "#64748B"))
for r in stamp["rectangles"]:
    parts.append('<Row crossAxisAlignment="CENTER"><Container width="10" height="10" color="' + r["color"] + '" borderRadius="2" margin="(0,2,6,0)"/>' + T(r["color"], 16, "#64748B") + '</Row>')
parts.append('</Column></Row></Positioned>')
# cells
audit_cells = []
for i, tr in enumerate(transforms):
    col, row = i % 4, i // 4
    left, top = GX + col * (CW + GAP), GY + row * (CH + GAP)
    M = combined(tr["operations"])
    parts.append(f'<Positioned left="{left}" top="{top}"><Container width="{CW}" height="{CH}" color="#FFFFFF" borderRadius="14" border="1 SOLID #E1E7F0"><Stack alignment="TOP_LEFT" clipBehavior="NONE"><Container width="{CW}" height="{CH}" color="#FFFFFF"/>')
    # frame crosshair and ticks
    parts.append(f'<Positioned left="20" top="125" width="260" height="1"><Container width="260" height="1" color="#EDF1F7"/></Positioned>')
    parts.append(f'<Positioned left="150" top="46" width="1" height="180"><Container width="1" height="180" color="#EDF1F7"/></Positioned>')
    for t in range(0, 301, 50):
        if t <= 300:
            parts.append(f'<Positioned left="{t}" top="42" width="1" height="6"><Container width="1" height="6" color="#CBD5E1"/></Positioned>')
            parts.append(f'<Positioned left="{t}" top="224" width="1" height="6"><Container width="1" height="6" color="#CBD5E1"/></Positioned>')
    # header
    parts.append(f'<Positioned left="12" top="8" width="276"><Row crossAxisAlignment="CENTER">' + T(tr["id"], 22, "#2563EB", True) + '<SizedBox width="10"/>' + T(SHORT[tr["id"]], 20, "#334155") + '</Row></Positioned>')
    # stamp
    parts.append(f'<Positioned left="90" top="65" width="120" height="120"><Transform matrix="{mstr(M)}" origin="(0,0)"><Stack alignment="TOP_LEFT" clipBehavior="NONE"><Container width="120" height="120" color="transparent"/>')
    for r in stamp["rectangles"]:
        x, y, w, h = r["xywh"]
        parts.append(f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Container width="{w}" height="{h}" color="{r["color"]}"/></Positioned>')
    parts.append(f'<Positioned left="{d["center"][0]-d["radius"]}" top="{d["center"][1]-d["radius"]}" width="{d["radius"]*2}" height="{d["radius"]*2}"><Container width="{d["radius"]*2}" height="{d["radius"]*2}" color="{d["color"]}" shape="CIRCLE"/></Positioned>')
    parts.append('</Stack></Transform></Positioned>')
    parts.append('</Stack></Container></Positioned>')
    # audit geometry
    rects = []
    for r in stamp["rectangles"]:
        x, y, w, h = r["xywh"]
        corners = [apply(M, x, y), apply(M, x + w, y), apply(M, x + w, y + h), apply(M, x, y + h)]
        rects.append({"xywh": [x, y, w, h], "color": r["color"],
                      "corners_local": [[round(px, 3), round(py, 3)] for px, py in corners],
                      "corners_canvas": [[round(left + 90 + px, 3), round(top + 65 + py, 3)] for px, py in corners]})
    allpts = [p for rr in rects for p in rr["corners_local"]]
    dcenter = apply(M, d["center"][0], d["center"][1])
    allpts += [(dcenter[0] - d["radius"], dcenter[1] - d["radius"]), (dcenter[0] + d["radius"], dcenter[1] + d["radius"])]
    bbox = [min(p[0] for p in allpts), min(p[1] for p in allpts), max(p[0] for p in allpts), max(p[1] for p in allpts)]
    audit_cells.append({"id": tr["id"], "operations": tr["operations"], "matrix_column_major": list(M),
                        "matrix_dsl": mstr(M), "rectangles": rects,
                        "dot_center_local": [round(dcenter[0], 3), round(dcenter[1], 3)],
                        "dot_center_canvas": [round(left + 90 + dcenter[0], 3), round(top + 65 + dcenter[1], 3)],
                        "bbox_local": [round(v, 3) for v in bbox],
                        "cell_origin": [left, top], "stamp_box_origin": [left + 90, top + 65]})

parts.append('<Positioned left="152" top="190"><Container width="1296"><Row crossAxisAlignment="CENTER">' + T("读法：4×3 按 T01→T12；局部原点 = 印章左上；十字 = 枢轴 (60,60)；短刻度 = 50px；x 向右 / y 向下。", 18, "#64748B") + '</Row></Container></Positioned>')
parts.append('</Stack></Container></Snapshot>')
dsl = "\n".join(parts)
(OUT / "transform-atlas.snapshot").write_text(dsl, encoding="utf-8")

audit = {
    "schema_version": 1, "task_id": "A09", "path_base": "output_dir",
    "canvas": [W, H], "grid": {"cols": 4, "rows": 3, "cell": [CW, CH], "gap": GAP,
                                "first_cell_origin": [GX, GY],
                                "formula": "left=152+col*332, top=300+row*282"},
    "coordinate_system": {"origin": "stamp top-left", "x": "right", "y": "down",
                          "pivot": PIVOT, "clock_direction": "as seen on image (y down)"},
    "stamp": stamp,
    "transforms": audit_cells,
    "pixel_check": {
        "method": "渲染 PNG 按格解码；对每格非白、非网格像素求外接框，与 matrix 计算的 bbox_canvas 比较四边；允许 ±1.5px（抗锯齿边缘例外）。",
        "tolerance_px": 1.5,
        "edge_exception": "抗锯齿半透明边缘不计入主体边缘，取 alpha>200 的像素",
        "note": "T07/T08 的矩阵不同，外接框与可视朝向不同，证明顺序差异。"
    }
}
(OUT / "geometry-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote A09", len(dsl))
for c in audit_cells:
    print(c["id"], c["matrix_dsl"], c["bbox_local"])
