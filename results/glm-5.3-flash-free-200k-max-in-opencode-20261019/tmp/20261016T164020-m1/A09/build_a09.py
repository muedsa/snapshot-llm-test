# -*- coding: utf-8 -*-
"""A09 · 十二个非对称图形变换标本。
stamp.json 印章（原值子坐标）+ transforms.json 依序复合为单一列主序 4×4 矩阵；
每格 <Transform matrix alignment=TOP_LEFT> 包裹 120×120 Stack（矩形/圆点原始局部坐标）。
产出 transform-atlas.snapshot + geometry-audit.json（矩阵/四角/圆心/外接框）。
"""
import io, sys, json, os, math

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "outputs", "20261016T164020-m1", "A09")
os.makedirs(OUT, exist_ok=True)
IN = os.path.join(ROOT, "tasks", "A09-transform-atlas", "inputs")

stamp = json.load(open(os.path.join(IN, "stamp.json"), encoding="utf-8"))
ops_list = json.load(open(os.path.join(IN, "transforms.json"), encoding="utf-8"))
PX0_, PY0_ = stamp["pivot"]                         # 局部枢轴 (60,60)
RECTS = stamp["rectangles"]
DOT = stamp["dot"]

# ---------------- 布局 ----------------
W, H = 1600, 1200
COLS, ROWS = 4, 3
CW, CH = 300, 250
GAP = 32
GX0 = (W - (COLS * CW + (COLS - 1) * GAP)) // 2     # 152
GY0 = (H - (ROWS * CH + (ROWS - 1) * GAP)) // 2     # 193

BG = "#F3F6FA"; CARD = "#FFFFFF"; BORDER = "#E3EAF4"
INK = "#0F172A"; SUB = "#55657F"; FAINT = "#94A3B8"
GUIDE = "#E7EDF5"; TICK = "#C9D4E3"; PIVOT = "#9FB0C6"
FAM = "Inter,Noto Sans CJK SC"

WARN = []
def fnum(v):
    s = f"{v:.7f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"
def estw(s, size):
    t = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F: t += size * 1.0
        elif ch in "0123456789": t += size * 0.6
        elif ch == " ": t += size * 0.30
        elif ch.isupper(): t += size * 0.70
        elif ch in "·—（）()→=.,+×:/°": t += size * 0.5
        else: t += size * 0.54
    return t
def fit(tag, s, size, box):
    w = estw(s, size)
    if w > box:
        WARN.append(f"{tag} estw {w:.0f} > {box}: {s}")
def text(x, y, s, size, color, bold=False, align="START", box_w=None):
    sty = f' fontSize="{fnum(size)}" color="{color}" fontFamily="{FAM}" maxLines="1" overflow="CLIP"'
    if bold: sty += ' fontWeight="BOLD"'
    if align != "START": sty += f' textAlign="{align}"'
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if box_w is None:
        return f'<Positioned left="{fnum(x)}" top="{fnum(y)}"><Text{sty}>{s}</Text></Positioned>'
    return (f'<Positioned left="{fnum(x)}" top="{fnum(y)}" width="{fnum(box_w)}">'
            f'<Text{sty}>{s}</Text></Positioned>')
def rect(x, y, w2, h2, color, radius=None, border=None):
    a = f'width="{fnum(w2)}" height="{fnum(h2)}"' + (f' color="{color}"' if color else "")
    if radius: a += f' borderRadius="{fnum(radius)}"'
    if border: a += f' border="{border}"'
    return f'<Positioned left="{fnum(x)}" top="{fnum(y)}"><Container {a} /></Positioned>'
def polygon(pts, color):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0_, y0_ = min(xs), min(ys); w2 = max(xs) - x0_; h2 = max(ys) - y0_
    if w2 < 0.5 or h2 < 0.5:
        WARN.append(f"polygon 太小 {pts}"); return None
    d = "M " + " L ".join(f"{fnum(px - x0_)} {fnum(py - y0_)}" for px, py in pts) + " Z"
    return (f'<Positioned left="{fnum(x0_)}" top="{fnum(y0_)}" width="{fnum(w2)}" height="{fnum(h2)}">'
            f'<SizedBox width="{fnum(w2)}" height="{fnum(h2)}">'
            f'<ClipPath path="{d}"><Container color="{color}" /></ClipPath>'
            f'</SizedBox></Positioned>')
def quad(p1, p2, color, t):
    x1, y1 = p1; x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 0.5: return None
    nx, ny = dy / L, -dx / L
    h = t / 2
    return polygon([(x1 + nx*h, y1 + ny*h), (x2 + nx*h, y2 + ny*h),
                    (x2 - nx*h, y2 - ny*h), (x1 - nx*h, y1 - ny*h)], color)

# ---------------- 矩阵复合 ----------------
def opmat(op, arg):
    if op == "rotate_clockwise_deg":
        t = math.radians(float(arg)); c, sn = math.cos(t), math.sin(t)
        return [[c, -sn], [sn, c]]                       # y 向下坐标系的屏幕顺时针
    if op == "mirror_horizontal": return [[-1.0, 0.0], [0.0, 1.0]]
    if op == "mirror_vertical":   return [[1.0, 0.0], [0.0, -1.0]]
    if op == "scale_uniform":     return [[float(arg), 0.0], [0.0, float(arg)]]
    if op == "scale_xy":          return [[float(arg[0]), 0.0], [0.0, float(arg[1])]]
    raise ValueError(op)
def mulm(A, B):
    return [[A[i][0] * B[0][j] + A[i][1] * B[1][j] for j in range(2)] for i in range(2)]
I2 = [[1.0, 0.0], [0.0, 1.0]]

SHORT = {"rotate_clockwise_deg": "顺转", "mirror_horizontal": "镜像H",
         "mirror_vertical": "镜像V", "scale_uniform": "等比×", "scale_xy": "缩放"}
def op_short(op, arg):
    if op == "rotate_clockwise_deg": return f"顺转{int(arg)}°"
    if op == "scale_uniform": return f"等比×{arg:g}"
    if op == "scale_xy": return f"缩放({arg[0]:g},{arg[1]:g})"
    return SHORT[op]

def rnd(m):
    """按写入 DSL 的 7 位小数回读，保证预测值与渲染矩阵一致"""
    def r(v): return float(f"{v:.7f}")
    return [[r(m[0][0]), r(m[0][1])], [r(m[1][0]), r(m[1][1])]]

def apply(K, p, C):
    """canvas = C + K·(p − pivot)"""
    return (C[0] + K[0][0] * (p[0] - PX0_) + K[0][1] * (p[1] - PY0_),
            C[1] + K[1][0] * (p[0] - PX0_) + K[1][1] * (p[1] - PY0_))

transforms_meta, geometry_rows = [], []
S1 = []
# 背景
S1.append(rect(0, 0, W, H, BG))
# 标题带
s_title = "十二个非对称图形变换标本"
s_badge = "4 列 × 3 行 · 格 300×250 · 间距 32"
fit("badge", s_badge, 20, 460)
S1.append(text(GX0, 40, s_title, 34, INK, bold=True))
S1.append(text(GX0 + CW * COLS + GAP * (COLS - 1) - 460, 48, s_badge, 20, SUB, align="END", box_w=460))
s_sub = "印章 120×120（三矩形 + 一墨点，原值）· 每步绕局部 (60,60) · 操作依列表顺序复合为单一列主序 4×4 矩阵 · y 向下，顺时针为屏幕方向"
fit("sub", s_sub, 20, 1296)
S1.append(text(GX0, 104, s_sub, 20, SUB))
S1.append(quad((GX0, 168), (GX0 + COLS * CW + (COLS - 1) * GAP, 168), BORDER, 1.5))

for idx, spec in enumerate(ops_list):
    tid = spec["id"]
    col, row = idx % COLS, idx // COLS
    x0_, y0_ = GX0 + col * (CW + GAP), GY0 + row * (CH + GAP)
    C = (x0_ + CW / 2, y0_ + CH / 2)

    K = I2
    for op, arg in spec["operations"]:
        K = mulm(opmat(op, arg), K)
    Kr = rnd(K)
    A = (C[0] - PX0_, C[1] - PY0_)                     # anchor：印章局部 (0,0) 未变换时的画布位
    # 矩阵平移分量 = 局部平移 t = p0 − K·p0（使含枢轴点满足 canvas = A + K·p + t = C + K·(p−p0)）
    TLX = fnum(PX0_ - (Kr[0][0] * PX0_ + Kr[0][1] * PY0_))
    TLY = fnum(PY0_ - (Kr[1][0] * PX0_ + Kr[1][1] * PY0_))
    mat16 = f"({fnum(Kr[0][0])},{fnum(Kr[1][0])},0,0,{fnum(Kr[0][1])},{fnum(Kr[1][1])},0,0,0,0,1,0,{TLX},{TLY},0,1)"
    chain = "→".join(op_short(op, arg) for op, arg in spec["operations"])
    fit("chain:" + tid, chain, 20, CW - 16)

    # 几何预测（ corners; 角序 源左上/右上/右下/左下 ）
    rects_geo = []
    pts_all = []
    for rc in RECTS:
        x, y, w2, h2 = rc["xywh"]
        src = [(x, y), (x + w2, y), (x + w2, y + h2), (x, y + h2)]
        cn = [apply(Kr, p, C) for p in src]
        pts_all += cn
        rects_geo.append({"color": rc["color"], "src_xywh": rc["xywh"], "corners_canvas": [[fnum(px), fnum(py)] for px, py in cn]})
    dc = apply(Kr, (DOT["center"][0], DOT["center"][1]), C)
    # 圆点映射为椭圆：x/y 半径 = |K 行元素|·r
    rx = math.hypot(Kr[0][0], Kr[0][1]) * DOT["radius"]
    ry = math.hypot(Kr[1][0], Kr[1][1]) * DOT["radius"]
    pts_all += [(dc[0] - rx, dc[1]), (dc[0] + rx, dc[1]), (dc[0], dc[1] - ry), (dc[0], dc[1] + ry)]
    bb = [min(p[0] for p in pts_all), min(p[1] for p in pts_all),
          max(p[0] for p in pts_all), max(p[1] for p in pts_all)]
    geometry_rows.append({
        "id": tid, "operations": [[op, arg] for op, arg in spec["operations"]],
        "matrix2x2_rowmajor": [[Kr[0][0], Kr[0][1]], [Kr[1][0], Kr[1][1]]],
        "matrix44_colmajor_used": mat16,
        "cell": {"col": col, "row": row, "rect_px": [x0_, y0_, x0_ + CW, y0_ + CH], "center_px": [C[0], C[1]]},
        "order_label": chain,
        "rects": rects_geo,
        "dot": {"src_center": DOT["center"], "src_radius": DOT["radius"], "center_canvas": [fnum(dc[0]), fnum(dc[1])],
                "mapped_radius": {"x": fnum(rx), "y": fnum(ry)}, "shape": "椭圆（由矩阵行范数缩放）"},
        "bbox_canvas": [fnum(bb[0]), fnum(bb[1]), fnum(bb[2]), fnum(bb[3])],
    })

    # ---- DSL：格卡 ----
    S1.append(rect(x0_, y0_, CW, CH, CARD, radius=14, border=f"1 SOLID {BORDER}"))
    cx_, cy_ = C
    S1.append(quad((cx_ - 118, cy_), (cx_ + 118, cy_), GUIDE, 1))
    S1.append(quad((cx_, cy_ - 100), (cx_, cy_ + 100), GUIDE, 1))
    for off in (-60, -30, 30, 60):
        S1.append(quad((cx_ + off, cy_ - 4), (cx_ + off, cy_ + 4), TICK, 1))
        S1.append(quad((cx_ - 4, cy_ + off), (cx_ + 4, cy_ + off), TICK, 1))
    S1.append(rect(cx_ - 5, cy_ - 5, 10, 10, None, border=f"1.5 SOLID {PIVOT}"))
    # ---- 主体：单一 Transform.matrix 承载组合变换 ----
    stamp_children = [
        f'<SizedBox width="{stamp["size"][0]}" height="{stamp["size"][1]}" />']
    for rc in RECTS:
        x, y, w2, h2 = rc["xywh"]
        stamp_children.append(f'<Positioned left="{x}" top="{y}" width="{w2}" height="{h2}">'
                              f'<Container width="{w2}" height="{h2}" color="{rc["color"]}" /></Positioned>')
    sx, sy = DOT["center"]; rr = DOT["radius"]
    stamp_children.append(f'<Positioned left="{sx - rr}" top="{sy - rr}" width="{2*rr}" height="{2*rr}">'
                          f'<Container width="{2*rr}" height="{2*rr}" color="{DOT["color"]}" borderRadius="{rr}" /></Positioned>')
    S1.append(f'<Positioned left="{fnum(A[0])}" top="{fnum(A[1])}" width="{stamp["size"][0]}" height="{stamp["size"][1]}">'
              f'<Transform matrix="{mat16}" alignment="TOP_LEFT"><Stack>'
              + "".join(stamp_children) + "</Stack></Transform></Positioned>")
    # ---- 标注 ----
    S1.append(text(x0_ + 14, y0_ + 10, tid, 22, INK, bold=True))
    ordn = f"{len(spec['operations'])} 步"
    S1.append(text(x0_ + CW - 64, y0_ + 13, ordn, 20, FAINT, align="END", box_w=48))
    S1.append(text(x0_, y0_ + CH - 32, chain, 20, SUB, align="CENTER", box_w=CW))
    transforms_meta.append({
        "id": tid, "operations": spec["operations"], "order_label": chain,
        "matrix2x2_rowmajor": [[Kr[0][0], Kr[0][1]], [Kr[1][0], Kr[1][1]]],
        "matrix44_colmajor_used": mat16,
        "cell": {"col": col, "row": row, "rect_px": [x0_, y0_, x0_ + CW, y0_ + CH], "center_px": [C[0], C[1]]},
    })

# ---- 图例（底部 193px） ----
lg_y = GY0 + ROWS * CH + (ROWS - 1) * GAP          # 1007
S1.append(text(GX0, lg_y + 22, "图例与读法", 22, INK, bold=True))
r1 = lg_y + 58
S1.append(rect(GX0, r1, 18, 18, RECTS[0]["color"], radius=3))
S1.append(text(GX0 + 26, r1 - 1, "矩形① (8,8) 28×92", 20, SUB))
S1.append(rect(GX0 + 300, r1, 18, 18, RECTS[1]["color"], radius=3))
S1.append(text(GX0 + 326, r1 - 1, "矩形② (36,72) 68×28", 20, SUB))
S1.append(rect(GX0 + 640, r1, 18, 18, RECTS[2]["color"], radius=3))
S1.append(text(GX0 + 666, r1 - 1, "矩形③ (64,8) 40×28", 20, SUB))
S1.append(rect(GX0 + 960 + 3, r1 + 4, 12, 12, DOT["color"], radius=6))
S1.append(text(GX0 + 986, r1 - 1, "圆点 (91,49) r8（随阵变换）", 20, SUB))
s_l2 = "辅助线：过格中心十字 · ±30/±60 刻度 · 枢轴方框（画布像素，1:1 对位未变换格 T01）"
fit("l2", s_l2, 20, 900)
S1.append(text(GX0, r1 + 34, s_l2, 20, SUB))
s_l3 = "T07 镜像H→顺转90° 与 T08 顺转90°→镜像H 结果不同（墨点一在东北、一在西北）——操作顺序差异可见；矩阵逐格见 geometry-audit.json"
fit("l3", s_l3, 20, 1296)
S1.append(text(GX0, r1 + 64, s_l3, 20, SUB))

dsl = f'<Snapshot background="{BG}" type="png"><Stack><SizedBox width="{W}" height="{H}" />\n' + "\n".join(S1) + "\n</Stack></Snapshot>"
open(os.path.join(OUT, "transform-atlas.snapshot"), "w", encoding="utf-8").write(dsl)

audit = {
    "schema_version": 1, "task_id": "A09", "path_base": "output_dir",
    "coordinate_system": {
        "stamp_local": {"origin": "印章左上角 (0,0)", "size_px": stamp["size"],
                        "pivot": [PX0_, PY0_], "x_direction": "右", "y_direction": "下",
                        "rotation_positive": "顺时针（屏幕方向，y 向下）"},
        "canvas": {"origin": "画布左上", "unit": "px", "positive": "x 右 / y 向下"},
        "cell_map": f"格(col,row) 左上 = ({GX0} + col*{CW + GAP}, {GY0} + row*{CH + GAP})；格心 = 左上 + (150,125)",
        "mapping": "canvas_point = cell_center + K·(p − pivot)；K = 依列表顺序左乘复合的两维矩阵",
        "matrix44": "列主序 16 数：(a,b,0,0, c,d,0,0, 0,0,1,0, t.x,t.y,0,1)，线性部分 K、平移 t = (60,60) − K·(60,60)（使局部枢轴点固定）；<Positioned> 锚位 A = 格心 − (60,60)；渲染 canvas = A + M·p_local = 格心 + K·(p − pivot)；alignment=TOP_LEFT → 变换原点=子盒左上",
        "rcw_formula": "rotate_clockwise_deg θ → [[cosθ,−sinθ],[sinθ,cosθ]]（y 向下）",
        "mirror_note": "mirror_horizontal/vertical 以枢轴 (60,60) 为轴，与印章中线重合",
    },
    "transforms": transforms_meta,
    "geometry": geometry_rows,
    "verification": [],
}
open(os.path.join(OUT, "geometry-audit.json"), "w", encoding="utf-8").write(json.dumps(audit, ensure_ascii=False, indent=1))

print("audit transforms:", len(transforms_meta), "geometry:", len(geometry_rows))
for g in geometry_rows[:3]:
    print(g["id"], "K=", g["matrix2x2_rowmajor"], "dot=", g["dot"]["center_canvas"], "bb=", g["bbox_canvas"])
print("WARN:", len(WARN))
for w in WARN: print(" -", w)
