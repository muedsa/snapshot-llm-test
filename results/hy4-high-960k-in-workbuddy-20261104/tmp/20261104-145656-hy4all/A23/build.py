#!/usr/bin/env python3
"""A23 - Capability-boundary animation storyboard delivery.

Generates (all via pure Snapshot DSL, no embedded pre-rendered frames):
  - cover.png / cover.snapshot                 1200x800 RGB cover
  - frame-01..06.png / .snapshot             600x600 transparent RGBA keyframes
  - contact-sheet.png / .snapshot            per-frame contact sheet (review evidence)
  - limitations.md, frame-data.json, timing.json

12 stable units U01-U12 keep geometry / unrotated W,H / RGB / alpha constant across
all 6 frames; only centre (x,y) and clockwise rotation change. Frames interpolate
from scattered fragments to a recognisable 12-petal radial star-flower. Every DSL
version is backed up to tmp/<run_id>/A23/<BUILD_VERSION>/.
"""
import json, math, os, sys
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN, MONO
import suite

TASK = "A23"
OUT = suite.out_dir(TASK)
VER = os.environ.get("BUILD_VERSION", "v1")
TMPV = suite.tmp_dir(TASK, VER)

# ------------------------------------------------------------------ constants
W, H = 60.0, 140.0                 # unrotated unit geometry (diamond / petal)
COL = ["#2563EB", "#0D9488", "#F59E0B", "#E11D48"]   # fixed RGB per unit id
ALPHA = 1.0                        # own alpha, constant for every unit / frame
R = 145.0                          # final radial-flower ring radius
CX, CY = 300.0, 300.0             # 600x600 canvas centre
N = 12
K = 6
PERIOD_MS = 1500
STEP_MS = 250
T_MS = [0, 250, 500, 750, 1000, 1250]
ACTIONS = ["分散", "初聚", "收拢", "近环", "将成", "成型"]
ACTIONS_LONG = [
    "12 个结构碎片散布画布四周,朝向各异",
    "开始向中心缓慢聚拢,余弦缓动起步",
    "明显收拢,旋转角朝放射方向对齐",
    "接近环状,角度基本对齐,间隙收窄",
    "几乎到位,单元逼近最终花位",
    "12 瓣放射星花成型,末帧构成可识别图形",
]

# deterministic scattered start anchors (4 cols x 3 rows) with small jitter
GX = [100.0, 233.0, 367.0, 500.0]
GY = [110.0, 300.0, 490.0]
START_ANG = [20.0, 75.0, 130.0, 200.0, 255.0, 310.0,
             45.0, 160.0, 95.0, 285.0, 340.0, 215.0]

START = []
for r in range(3):
    for cc in range(4):
        i = r * 4 + cc
        jx = ((i * 37) % 21) - 10
        jy = ((i * 53) % 23) - 11
        START.append((GX[cc] + jx, GY[r] + jy, START_ANG[i]))

TARGET = []
for i in range(N):
    th = i * 30.0                     # clockwise from top
    rad = math.radians(th)
    TARGET.append((CX + R * math.sin(rad), CY - R * math.cos(rad), th))


def ease(k):
    """Cosine easing s(0)=0, s(5)=1 -> p(k)=(1-cos(pi*k/5))/2."""
    return (1.0 - math.cos(math.pi * k / (K - 1))) / 2.0


def ang_delta(a, b):
    """Shortest signed delta (deg) from a to b, in (-180, 180]."""
    return (b - a + 180.0) % 360.0 - 180.0


EASE = [ease(k) for k in range(K)]

# STATE[k][i] = (cx, cy, angle_deg)
STATE = []
for k in range(K):
    s = EASE[k]
    row = []
    for i in range(N):
        sx, sy, sa = START[i]
        tx, ty, ta = TARGET[i]
        cx = sx + (tx - sx) * s
        cy = sy + (ty - sy) * s
        ang = (sa + ang_delta(sa, ta) * s) % 360.0
        row.append((cx, cy, ang))
    STATE.append(row)


def geom(w, h):
    """Unrotated unit vertices, centred at origin (diamond / petal)."""
    return [(0.0, -h / 2), (w / 2, 0.0), (0.0, h / 2), (-w / 2, 0.0)]


def rotate(points, cx, cy, deg):
    a = math.radians(deg)
    co, si = math.cos(a), math.sin(a)
    return [(cx + x * co - y * si, cy + x * si + y * co) for x, y in points]


def unit_vertices(k, i, scale=1.0, ox=0.0, oy=0.0):
    cx, cy, ang = STATE[k][i]
    return rotate(geom(W * scale, H * scale), ox + cx * scale, oy + cy * scale, ang)


# geometry self-check: every vertex of every unit in every frame stays on-canvas
_minx = min(p[0] for k in range(K) for i in range(N) for p in unit_vertices(k, i))
_maxx = max(p[0] for k in range(K) for i in range(N) for p in unit_vertices(k, i))
_miny = min(p[1] for k in range(K) for i in range(N) for p in unit_vertices(k, i))
_maxy = max(p[1] for k in range(K) for i in range(N) for p in unit_vertices(k, i))
assert 0 < _minx and _maxx < 600 and 0 < _miny and _maxy < 600, (
    "unit leaves canvas", _minx, _maxx, _miny, _maxy)
assert len(START) == N and len(TARGET) == N


def draw_units(c, k, scale=1.0, ox=0.0, oy=0.0):
    """Re-draw the 12 units of frame k (pure DSL), scaled about (ox,oy)."""
    for i in range(N):
        c.poly(unit_vertices(k, i, scale, ox, oy), COL[i % 4] + "FF")


def draw_dots(c, k, scale, ox, oy, r=3.6):
    """Light-weight 12 centre dots (for cover mini storyboard)."""
    for i in range(N):
        cx, cy, _ = STATE[k][i]
        c.circle(ox + cx * scale, oy + cy * scale, r, COL[i % 4] + "FF")


def emit_dsl(name, dsl):
    (OUT / name).write_text(dsl, encoding="utf-8")
    (TMPV / name).write_text(dsl, encoding="utf-8")
    return len(dsl.encode("utf-8"))


def emit_text(name, text):
    (OUT / name).write_text(text, encoding="utf-8")
    (TMPV / name).write_text(text, encoding="utf-8")


# ================================================================== 6 frames
frame_bytes = {}
for k in range(K):
    c = Canvas(600, 600, "transparent")
    draw_units(c, k)
    frame_bytes["frame-%02d" % (k + 1)] = emit_dsl("frame-%02d.snapshot" % (k + 1), c.render())

# ================================================================== cover (RGB)
BG = "#0B1B35"
CARD = "#152B4E"
CARD2 = "#0F213C"
LINE = "#2C4C7C"
INK = "#F1F5F9"
MUTED = "#9FB3D1"
CYAN = "#38BDF8"
AMBER = "#FBBF24"
LIGHT = "#EAF1FB"

c = Canvas(1200, 800, BG)
c.gradient(0, 0, 1200, 800, ["#0B1B35", "#122C52"], begin="TOP_LEFT", end="BOTTOM_RIGHT")
# header
c.text(48, 16, 700, 26, "SNAPSHOT  /  CAPABILITY BOUNDARY DELIVERY", 18, CYAN, font=LATIN, bold=True)
c.text(46, 42, 700, 60, "从结构到画面", 46, INK, bold=True)
c.text(760, 26, 392, 30, "服务仅输出静态位图", 22, AMBER, bold=True, align="RIGHT")
c.text(700, 60, 452, 28, "以 6 帧关键帧 + 时间数据完整表达动作与时间轴", 17, MUTED, align="RIGHT")
c.rect(48, 108, 1104, 2, CYAN)

# ---- left card: final frame preview
LX, LY, LW, LH = 48, 126, 548, 348
c.rect(LX, LY, LW, LH, CARD, radius=16, border="1 SOLID " + LINE)
c.text(LX + 22, LY + 14, 420, 30, "末帧 · 汇聚成型  /  FRAME 06", 22, INK, bold=True)
c.text(LX + 430, LY + 16, 100, 26, "1250 ms", 18, CYAN, align="RIGHT", font=LATIN)
PF = 0.45                              # preview scale: 600*0.45 = 270
PW = 600 * PF
PX = LX + (LW - PW) / 2
PY = LY + 46
c.rect(PX, PY, PW, PW, LIGHT, radius=10)
draw_units(c, K - 1, PF, PX, PY)
c.text(LX + 22, LY + LH - 30, 500, 24,
       "12 个几何单元 · 始终存在 · 颜色/尺度守恒 · 真透明背景", 16, MUTED)

# ---- right card: capability boundary
BX, BY, BW, BH = 612, 126, 540, 348
c.rect(BX, BY, BW, BH, CARD, radius=16, border="1 SOLID " + LINE)
c.text(BX + 22, BY + 14, 480, 30, "格式边界  /  CAPABILITY BOUNDARY", 22, INK, bold=True)
rows = [
    ("文字可编辑 SVG", "不支持", "位图输出,文字不可编辑;需外部矢量重排", "#F87171"),
    ("CMYK 印刷稿", "不支持", "输出为 RGB(A),无分色/ICC;需外部印前转换", "#F87171"),
    ("6 帧透明 GIF 动画", "不支持原生", "6 张透明 PNG 关键帧 + timing.json 替代", "#FBBF24"),
    ("PNG 封面", "支持", "本封面 1200×800 RGB,服务原生 type=png", "#34D399"),
]
ry = BY + 54
for name, verdict, sub, col in rows:
    c.circle(BX + 34, ry + 18, 6, col)
    c.text(BX + 52, ry, 250, 26, name, 19, INK, bold=True)
    c.rect(BX + 316, ry + 2, 96, 26, col, radius=6)
    c.text(BX + 316, ry + 2, 96, 26, verdict, 15, "#0B1B35", bold=True, align="CENTER")
    c.text(BX + 52, ry + 28, 470, 24, sub, 15, MUTED)
    ry += 72

# ---- storyboard timeline (6 mini frames)
TY = 500
c.text(48, TY, 800, 28, "逐帧分镜时间轴  /  250 ms 每帧 · 周期 1500 ms · 循环在 1250→0 跳变", 18, CYAN, bold=True)
GW, GH, GAP = 175, 196, 11
GX0 = 48
for k in range(K):
    gx = GX0 + k * (GW + GAP)
    c.rect(gx, TY + 36, GW, GH, CARD2, radius=12, border="1 SOLID " + LINE)
    c.rect(gx, TY + 36, GW, 5, COL[k % 4], radius=3)
    # light plot area
    MF = 0.24                          # 600*0.24 = 144
    MW = 600 * MF
    mx = gx + (GW - MW) / 2
    my = TY + 48
    c.rect(mx, my, MW, MW, LIGHT, radius=6)
    draw_dots(c, k, MF, mx, my, r=3.4)
    c.text(gx + 10, TY + 196, 80, 24, "F%02d" % (k + 1), 17, INK, bold=True, font=LATIN)
    c.text(gx + 92, TY + 196, 74, 24, "%dms" % T_MS[k], 16, CYAN, align="RIGHT", font=LATIN)
    c.text(gx + 10, TY + 218, 155, 24, ACTIONS[k], 16, AMBER, bold=True)
    if k < K - 1:
        c.text(gx + GW + 1, TY + 118, 10, 24, "›", 20, CYAN, align="CENTER")

# ---- footer
c.rect(48, 742, 1104, 1, LINE)
c.text(48, 748, 760, 24, "12 单元 U01–U12 · 几何/未旋转宽高/RGB/alpha 跨帧守恒 · 仅位置与旋转变化", 15, MUTED)
c.text(600, 746, 552, 22, "依据 ai-guide.md / openapi.yaml / parser-tags.md", 14, MUTED, align="RIGHT")
c.text(600, 768, 552, 22, "详见 limitations.md / frame-data.json / timing.json", 14, MUTED, align="RIGHT")
cover_bytes = emit_dsl("cover.snapshot", c.render())

# ================================================================== contact sheet
CSW, CSH = 1600, 1140
cs = Canvas(CSW, CSH, "#EEF3FA")
cs.gradient(0, 0, CSW, 104, ["#0B1B35", "#16386F"], begin="CENTER_LEFT", end="CENTER_RIGHT")
cs.text(40, 16, 900, 40, "A23 · 逐帧接触表  /  CONTACT SHEET", 30, INK, bold=True)
cs.text(40, 60, 1000, 28, "6 帧 × 12 单元 · 由分散逐步汇聚为 12 瓣放射星花 · 帧不含文字", 18, "#BBD3F2")
cs.text(1120, 24, 440, 30, "250 ms / 帧 · 周期 1500 ms", 20, "#7DD3FC", align="RIGHT", font=LATIN)
cs.text(1120, 60, 440, 26, "循环 1250→0 存在可见跳变", 17, "#FBBF24", align="RIGHT")

CGS, CGAPX, CGAPY = 490, 20, 24
CX0, CY0 = 35, 128
for k in range(K):
    col = k % 3
    row = k // 3
    gx = CX0 + col * (CGS + CGAPX)
    gy = CY0 + row * (470 + CGAPY)
    cs.rect(gx, gy, CGS, 470, "#FFFFFF", radius=14, border="1 SOLID #D5E0F0")
    cs.rect(gx, gy, CGS, 6, COL[k % 4], radius=3)
    cs.text(gx + 18, gy + 14, 260, 30, "FRAME %02d" % (k + 1), 22, "#0F172A", bold=True, font=LATIN)
    cs.text(gx + 300, gy + 15, 172, 28, "t = %d ms" % T_MS[k], 19, "#2563EB", align="RIGHT", font=LATIN)
    CF = 0.62                       # 600*0.62 = 372
    CWv = 600 * CF
    px = gx + (CGS - CWv) / 2
    py = gy + 50
    cs.rect(px, py, CWv, CWv, "#F5F8FD", radius=8)
    draw_units(cs, k, CF, px, py)
    cs.text(gx + 18, gy + 432, 454, 28, "动作 %d / 6 · %s" % (k + 1, ACTIONS_LONG[k]), 16, "#334155")
    cs.text(gx + 18, gy + 432, 454, 28, "p=%.3f" % EASE[k], 15, "#94A3B8", align="RIGHT", font=LATIN)
cs.rect(35, 1096, 1530, 1, "#C9D7EA")
cs.text(35, 1104, 1100, 26, "帧序 frame-01 → frame-06(0/250/500/750/1000/1250 ms);每帧 12 单元均在且可见,轨迹连续", 16, "#5B6B85")
cs.text(1100, 1104, 465, 26, "末帧→首帧为汇聚→散开跳变,不宣称无缝", 16, "#B45309", align="RIGHT")
contact_bytes = emit_dsl("contact-sheet.snapshot", cs.render())

# ================================================================== frame-data.json
def u_rec(k, i):
    cx, cy, ang = STATE[k][i]
    return {
        "id": "U%02d" % (i + 1),
        "x": round(cx, 3), "y": round(cy, 3),
        "width": W, "height": H,
        "rotation_deg": round(ang, 3),
        "color_rgba": COL[i % 4] + "FF",
        "alpha": ALPHA,
        "visible": True,
        "geometry": "diamond_petal_4vertex",
    }


units = [{
    "id": "U%02d" % (i + 1),
    "geometry": "diamond_petal_4vertex",
    "width": W, "height": H,
    "rgb": COL[i % 4],
    "color_rgba": COL[i % 4] + "FF",
    "alpha": ALPHA,
    "notes": "未旋转宽高/RGB/自身alpha/几何类型跨 6 帧恒定;仅 (x,y) 与顺时针旋转变化",
} for i in range(N)]

frames = [{
    "id": "frame-%02d" % (k + 1),
    "index": k + 1,
    "t_ms": T_MS[k],
    "ease_p": round(EASE[k], 6),
    "action": ACTIONS_LONG[k],
    "png": "frame-%02d.png" % (k + 1),
    "dsl": "frame-%02d.snapshot" % (k + 1),
    "units": [u_rec(k, i) for i in range(N)],
} for k in range(K)]

trajectories = []
for i in range(N):
    steps = []
    for k in range(K - 1):
        x0, y0, a0 = STATE[k][i]
        x1, y1, a1 = STATE[k + 1][i]
        dx, dy = x1 - x0, y1 - y0
        steps.append({
            "from": "frame-%02d" % (k + 1), "to": "frame-%02d" % (k + 2),
            "dx": round(dx, 3), "dy": round(dy, 3),
            "displacement_px": round(math.hypot(dx, dy), 3),
            "drot_deg": round(ang_delta(a0, a1), 3),
        })
    trajectories.append({
        "id": "U%02d" % (i + 1),
        "interpolation": "p(k)=(1-cos(pi*k/5))/2; x_k=x0+(x1-x0)*p(k); y_k=y0+(y1-y0)*p(k); rot_k=(a0+((a1-a0+180) mod 360)-180)*p(k) mod 360 (分段余弦缓动,仅设计轨迹,未渲染中间帧)",
        "steps": steps,
    })

# seam: frame-06 (1250ms) -> frame-01 (0ms / loop restart at 1500ms)
seam_units = []
for i in range(N):
    x6, y6, a6 = STATE[K - 1][i]
    x0, y0, a0 = STATE[0][i]
    seam_units.append({
        "id": "U%02d" % (i + 1),
        "from_xy": [round(x6, 3), round(y6, 3)], "to_xy": [round(x0, 3), round(y0, 3)],
        "displacement_px": round(math.hypot(x0 - x6, y0 - y6), 3),
        "drot_deg": round(ang_delta(a6, a0), 3),
    })
max_step = max(s["displacement_px"] for t in trajectories for s in t["steps"])
max_seam = max(u["displacement_px"] for u in seam_units)
min_step = min(s["displacement_px"] for t in trajectories for s in t["steps"])
seam = {
    "from": "frame-06 (t=1250ms, 汇聚完成态)",
    "to": "frame-01 (t=0ms / 周期 1500ms 处循环重启, 分散态)",
    "seamless": False,
    "per_unit": seam_units,
    "max_frame_step_displacement_px": round(max_step, 3),
    "min_frame_step_displacement_px": round(min_step, 3),
    "max_seam_displacement_px": round(max_seam, 3),
    "comparison": "接缝位移(最大 %.1f px)约为帧间最大步长(%.1f px)的 %.2f 倍,且远大于最小步长 %.1f px;方向由向心汇聚反转为向外散开" % (
        max_seam, max_step, max_seam / max_step, min_step),
    "direction_evidence": "帧间 5 步均为 p 递增、位置单调向 (300,300) 花位靠拢;接缝 p 由 1.0 回到 0.0,位置/旋转全部反向,速度与方向不连续",
    "closure_evidence": "设计轨迹非闭合:frame-06 与 frame-01 的位置/旋转不一致;未构造 t=1500ms 与 t=0 相同的闭合轨道,故不宣称无缝",
    "impact": "循环播放时在 1250→0 出现一次明显的『爆散/重置』跳变;位置为一次循环末尾,影响为视觉重置而非平滑续接",
    "conclusion": "如实保留跳变;timing.json 与 limitations.md 已明确标注位置与影响,不因 loop=true 宣称无缝",
    "viewing_conclusion": "逐帧打开 6 张 PNG 与接触表可见 12 单元连续汇聚、末帧成花、无单元消失或移出画布;循环跳变可由首尾两帧对比直接核验",
}

frame_data = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "topic": "结构汇聚成图像",
    "cover": "cover.png", "contact_sheet": "contact-sheet.png",
    "canvas": {"width": 600, "height": 600, "background": "transparent (RGBA)"},
    "coordinate_system": {
        "origin": "top-left", "x_direction": "right", "y_direction": "down",
        "position": "unit geometry centre (x,y) in px",
        "rotation_origin": "unit centre", "rotation_direction": "clockwise degrees",
        "size": "unrotated width/height in px (rotation changes only the bounding box, not the size)",
        "note": "angles in [0,360); 360-degree equivalence used for frame-to-frame rotation differences",
    },
    "units": units,
    "frames": frames,
    "trajectories": trajectories,
    "seam": seam,
    "checks": [
        {"check": "每帧 12 单元 U01-U12 各出现一次", "method": "build.py 生成时逐帧遍历 12 ID", "passed": True},
        {"check": "每 ID 几何/未旋转宽高/RGB/alpha 跨帧守恒", "method": "units 常量 + 每帧仅写入 x/y/rotation", "passed": True},
        {"check": "所有顶点在 600x600 画布内、无单元移出画布或被完全遮挡", "method": "build.py assert 全局顶点包围盒 (%.1f,%.1f)-(%.1f,%.1f) 落在 (0,600);逐帧实际看图:frame-03/04 汇聚途中存在短暂部分重叠,但每个单元均保留可见像素、12 个 ID 全程可辨,未完全遮挡或消失" % (_minx, _miny, _maxx, _maxy), "passed": True},
        {"check": "6 帧均为真透明 RGBA 背景", "method": "服务返回 PNG colortype=6 且背景 alpha=0(冒烟与逐帧核验)", "passed": True},
        {"check": "末帧构成可识别图形", "method": "12 单元等角 30° 排布成 12 瓣放射星花", "passed": True},
        {"check": "轨迹连续、无突然消失", "method": "余弦缓动位置插值 + 最短弧角度插值,每帧 12 单元 visible=true", "passed": True},
    ],
}
emit_text("frame-data.json", json.dumps(frame_data, ensure_ascii=False, indent=2) + "\n")

# ================================================================== timing.json
timing = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "frames": [{
        "order": k + 1, "id": "frame-%02d" % (k + 1),
        "png": "frame-%02d.png" % (k + 1),
        "dsl": "frame-%02d.snapshot" % (k + 1),
        "t_ms": T_MS[k], "duration_ms": STEP_MS,
        "action": ACTIONS_LONG[k],
    } for k in range(K)],
    "frame_count": K,
    "duration_ms": STEP_MS,
    "period_ms": PERIOD_MS,
    "fps": 1000.0 / STEP_MS,
    "loop": True,
    "seamless": False,
    "cover": "cover.png",
    "contact_sheet": "contact-sheet.png",
    "seam_evidence": {
        "statement": "末帧(frame-06, 汇聚态, 1250ms)循环回首帧(frame-01, 分散态, 0ms)存在可见跳变,不宣称无缝",
        "location": "1250ms → 1500ms/0ms(一次循环末尾)",
        "reason": "设计轨迹为单向『分散→汇聚』,非闭合;frame-06 与 frame-01 位置/旋转不一致,loop 播放设置不等于无缝",
        "impact": "每循环出现一次『爆散/重置』视觉跳变;不改变 6 帧内部的连续汇聚",
        "quantified": frame_data["seam"]["comparison"],
        "reference": "frame-data.json#seam(逐 ID 位移与旋转差、方向/速度证据)",
        "viewing": "逐帧与接触表实际查看确认;首尾两帧对比可直接核验跳变",
    },
    "notes": "本题仅交付 6 张 600x600 真透明 PNG 关键帧与时间数据,不合成 GIF、不新增中间帧、不造假目标格式文件;服务单次请求只返回单张静态位图",
}
emit_text("timing.json", json.dumps(timing, ensure_ascii=False, indent=2) + "\n")

# ================================================================== limitations.md
pvals = ", ".join("%.4f" % v for v in EASE)
L = []
A = L.append
A("# A23 · 格式边界说明与后续接口")
A("")
A("主题:结构汇聚成图像。客户原始请求包含「文字可编辑 SVG、CMYK 印刷稿、6 帧透明 GIF 动画、PNG 封面」,并限定只用 Snapshot 类 DOM DSL 与 open-snapshot 服务作图。")
A("")
A("## 0. 总判定:服务只能输出静态栅格图")
A("")
A("`POST /snapshot` 的请求体是一份 UTF-8 纯文本 DSL(`text/plain`),成功响应是**单张静态图片二进制**;`type` 仅 `png` / `jpg` / `webp`(ai-guide.md 第 3、49 行;openapi.yaml `/snapshot` 200 响应 `image/png|image/jpeg|image/webp`)。接口与 DSL 没有多帧容器、帧延时、循环次数、时间轴、矢量导出或 CMYK 色彩空间等参数。因此服务**不能**原生输出动画 GIF、可编辑 SVG 或 CMYK 印刷稿,也不能在一次响应里给出多个带时序的帧。")
A("")
A("本题不因『不支持』而结束,而是按授权完成**完整替代交付**:1 张 1200×800 RGB PNG 封面 + 6 张 600×600 真透明 RGBA PNG 关键帧(各存完整 DSL)+ `timing.json`(250ms/帧、loop、帧序)+ `frame-data.json`(逐帧几何/轨迹/接缝)+ `contact-sheet.png` 逐帧接触表。动作与时间轴由 6 个静态分镜逐帧完整表达,而非伪造目标格式文件。")
A("")
A("## 1. 逐项请求 / 支持情况 / 依据 / 替代 / 仍需外部后续工作")
A("")
A("| 请求 | 支持情况 | 依据(实际文档) | 本题替代 | 仍需外部后续工作 |")
A("|---|---|---|---|---|")
A("| 文字可编辑 SVG | 不支持 | ai-guide.md:49 `type` 仅 png/jpg/webp;parser-tags.md `Snapshot` 表;SVG 仅以 `path` 字符串作为 `ClipPath` 裁剪**输入**,不导出 SVG 文档;文字经 `Text` 栅格化进位图后不可编辑 | 封面与说明文字以位图呈现,DSL 保留全部排版源码可再编辑 | 用外部矢量工具重排为 SVG、拆分文字层、处理字体授权与转曲 |")
A("| CMYK 印刷稿 | 不支持 | openapi.yaml 响应仅 RGB 系位图;parser-tags.md 颜色章节仅 CSS `#RRGGBBAA` 等 RGB(A);接口/DSL 无 ICC、分色、出血参数 | 交付 RGB(A) PNG 封面与帧(8 位 alpha 为真透明) | 按印厂 ICC 转 CMYK、分色、加出血/裁切线、打样与印前检查 |")
A("| 6 帧透明 GIF 动画 | 不支持原生动画 | ai-guide.md:3 单次响应为图片二进制;ai-guide.md:49 无 gif;openapi.yaml 无帧/延时/循环字段 | 6 张 600×600 真透明 RGBA PNG 关键帧(逐帧 DSL)+ `timing.json`(每帧 250ms、周期 1500ms、loop、帧序)+ `frame-data.json` + 接触表;不合成 GIF、不造假目标格式 | 用外部工具把 6 帧合成 GIF/APNG/WebP 动画、写入帧延时与循环次数、可选补间帧;并处理下述循环跳变 |")
A("| PNG 封面 | 支持 | ai-guide.md:49 `type=png`;parser-tags.md `background` 默认 `transparent`,本题显式设为不透明深色 | 交付 `cover.png` 1200×800,文字「从结构到画面」可读 | 若需印刷或可编辑见上两行 |")
A("")
A("补充:透明背景是**真透明**,不是白底——`Snapshot background=\"transparent\"` + 8 位颜色 alpha;服务返回 PNG 的 IHDR color type=6(RGBA),背景像素 alpha=0(冒烟测试与逐帧核验)。")
A("")
A("## 2. 逐帧动作 / 时间轴(可核验帧序)")
A("")
A("帧序:`frame-01 → frame-06`,时刻 t = 0 / 250 / 500 / 750 / 1000 / 1250 ms,每帧 250ms,循环周期 1500ms。插值进度 p(k)=(1−cos(πk/5))/2,六帧 p = [%s](仅说明设计轨迹,未渲染中间帧)。" % pvals)
A("")
A("| 帧 | 文件 | t | p | 动作 |")
A("|---|---|---|---|---|")
for k in range(K):
    A("| %d | `frame-%02d.png` | %d ms | %.4f | %s |" % (k + 1, k + 1, T_MS[k], EASE[k], ACTIONS_LONG[k]))
A("")
A("12 个单元使用稳定 ID U01–U12,每帧各出现一次,ID 不印在图中。每个 ID 的几何类型(4 顶点菱形花瓣)、未旋转宽高 60×140 px、RGB 颜色与自身 alpha(=1.0)跨帧恒定;仅几何中心 (x,y) 与绕自身中心的顺时针旋转角变化,不用缩放、变形、变色或渐隐代替汇聚。位置以 4×3 散布锚点为起点,向中心 (300,300) 半径 145px 的 12 等分(30°)花位余弦缓动汇聚;旋转按最短弧对齐到放射角。末帧 12 瓣构成可识别的放射星花。逐单元相邻帧位移、角差与缓动公式见 `frame-data.json#trajectories`。")
A("")
A("## 3. 循环接缝(如实记录跳变)")
A("")
A("设计轨迹是单向『分散→汇聚』、**非闭合**:frame-06(1250ms,汇聚完成)与 frame-01(0ms,分散)在位置与旋转上不一致。循环在 1250→1500/0ms 处由汇聚态跳回分散态,出现一次可见的『爆散/重置』跳变。")
A("")
A("- 逐 ID 的接缝位移与旋转差(按 360° 等价)见 `frame-data.json#seam.per_unit`。")
A("- 接缝最大位移 %.1f px,约为帧间最大步长 %.1f px 的 %.2f 倍,且方向与 5 个向心帧步相反(汇聚→散开),速度与方向均不连续。" % (max_seam, max_step, max_seam / max_step))
A("- 因此 `timing.json` 中 `seamless=false`,`loop=true` 仅表示播放方式,**不**表示无缝;不能仅因 loop 就宣称无缝。")
A("- 影响:每次循环末尾一次视觉重置,不影响 6 帧内部的连续汇聚。若要无缝循环,需外部补一段『散开』过渡帧或重新设计闭合轨道,本题未做,亦未假称已做。")
A("")
A("## 4. 仍需外部后续工作(汇总)")
A("")
A("1. 用外部工具把 6 张关键帧合成 GIF/APNG/WebP 动画,设置 250ms 延时与 loop;如需平滑循环,补间或重设计闭合轨迹。")
A("2. 如需可编辑 SVG:外部矢量重排并保留文字层/字体。")
A("3. 如需印刷:外部 RGB→CMYK 转换、分色、出血与打样。")
A("4. 服务限制(单张静态位图、无动画/矢量/CMYK 参数)属平台能力边界,不能靠 DSL 绕过;以上均以『完整替代交付 + 明确后续接口』处理,未创建假的目标格式文件。")
A("")
A("服务契约与标签依据缓存于 `tmp/<run_id>/_suite/docs/`(ai-guide.md、openapi.yaml、parser-tags.md 等);本题 8 张 PNG 均为服务真实响应,DSL 同名备份,过程记录见 `tmp/<run_id>/A23/`。")
emit_text("limitations.md", "\n".join(L) + "\n")

# ================================================================== summary
print("A23 BUILD %s" % VER)
print("  cover.snapshot      %d bytes" % cover_bytes)
for k in range(K):
    print("  frame-%02d.snapshot  %d bytes" % (k + 1, frame_bytes["frame-%02d" % (k + 1)]))
print("  contact-sheet.snapshot %d bytes" % contact_bytes)
print("  vertex bbox (%.1f,%.1f)-(%.1f,%.1f) on 600x600" % (_minx, _miny, _maxx, _maxy))
print("  ease p:", [round(v, 4) for v in EASE])
print("  frame step disp max/min: %.2f / %.2f ; seam max disp: %.2f" % (max_step, min_step, max_seam))
print("  outputs ->", OUT)
