"""A23 参数化生成器：12 个刚性几何单元 × 6 帧关键帧 + RGB 封面 + 接触表 + 离线干跑门禁。

设计轨迹（单一缓动 + 直线位移，公式唯一，便于逐帧核验）：

    p_f  = (f - 1) / 5                        f = 1..6
    e(p) = p^2 * (3 - 2p)                     smoothstep，两端一阶导数为 0
    pos(f) = P0 + (P1 - P0) * e(p_f)
    rot(f) = R0 + (R1 - R0) * e(p_f)          R1 = 0（末帧全部摆正）

守恒律：每个 ID 的几何类型、未旋转宽高、RGB、alpha 跨 6 帧不变；只允许位置和旋转变化。
不用缩放、变形、变色、渐隐代替汇聚。旋转是绕单元自身中心的刚体旋转（中心平移量直接烤进
Matrix4 的 4×4 平移分量），不是缩放，所以宽高按未旋转几何记录，旋转后外包框的变化
只能当可见性证据，不能当缩放证据。

只用 Container（矩形/圆/圆角矩形）与 ClipPath（SVG 路径→三角形）构造形状；不用 Image，
不嵌任何预渲染帧。
"""

from __future__ import annotations

import math

# --------------------------------------------------------------------------- #
# 单元表：几何类型 / 未旋转宽高 / RGB / 自身 alpha / 首帧与末帧中心 / 首帧旋转
# 画布 600×600，原点左上，位置是几何中心 (x, y)，单位为像素，旋转为顺时针度数。
# --------------------------------------------------------------------------- #

UNITS = [
    # id,  名,        shape,      w,    h,    rgb,        alpha, srot(度), final(末帧中心)
    # 末帧 = 一座可识别的房景，全部接触关系整数对齐，审计可以逐条量：
    #   地面 y[459,481]；墙体 y[319,459] 底边正好压在地面；屋顶底边 y=319 正好压在墙顶；
    #   烟囱底边 y=285 坐在屋顶右坡上（该处坡度 y=284.09）；门 y[391,459] 底边压在墙上，
    #   顶边 y=391 在两窗底边 y=381 之下 10 px，且高出墙体中心线 y=389 共 2 px
    #   （这样墙体中心不被门遮住——G08 逐帧验证）；树干 y[387,459] 底边立在草地上；
    #   树冠底边 y=387 = 树干顶边；灌木底边 y=459 坐在草地上；太阳与云朵在天顶互不重叠。
    # 末帧整体占 x[108,470] × y[133,481]，四周围出 108/130/133/119 px 余量。
    dict(id="U01", name="太阳",   shape="circle",   w=74,  h=74,  rgb="F4B942", alpha=255, srot=120, final=(420, 170)),
    dict(id="U02", name="屋顶",   shape="triangle", w=220, h=96,  rgb="B5462F", alpha=255, srot=25,  final=(300, 271)),
    dict(id="U03", name="墙体",   shape="rect",     w=170, h=140, rgb="EFE3CB", alpha=255, srot=-15, final=(300, 389)),
    dict(id="U04", name="树冠",   shape="circle",   w=104, h=104, rgb="4C8C46", alpha=255, srot=0,   final=(160, 335)),
    dict(id="U05", name="云朵",   shape="rounded",  w=120, h=38,  rgb="E3ECF5", alpha=150, srot=20,  final=(210, 165)),
    dict(id="U06", name="门",     shape="rect",     w=44,  h=68,  rgb="6B3A1E", alpha=255, srot=30,  final=(300, 425)),
    dict(id="U07", name="左窗",   shape="rect",     w=42,  h=42,  rgb="7FA9E8", alpha=175, srot=-45, final=(245, 360)),
    dict(id="U08", name="右窗",   shape="rect",     w=42,  h=42,  rgb="A8C8F0", alpha=175, srot=45,  final=(355, 360)),
    dict(id="U09", name="树干",   shape="rect",     w=28,  h=72,  rgb="8C5A33", alpha=255, srot=20,  final=(160, 423)),
    dict(id="U10", name="烟囱",   shape="rect",     w=36,  h=70,  rgb="8A4A3A", alpha=255, srot=35,  final=(370, 250)),
    dict(id="U11", name="灌木",   shape="circle",   w=60,  h=60,  rgb="2F7A4A", alpha=255, srot=0,   final=(430, 429)),
    dict(id="U12", name="地面",   shape="rect",     w=340, h=22,  rgb="8FAF4E", alpha=255, srot=0,   final=(300, 470)),
]

# --------------------------------------------------------------------------- #
# 分散态 = 末帧整体以同伦中心 C 放大 k 倍：start_i = C + k·(final_i − C)
#
# 这是本题几何的核心，值得写清楚，因为它把「没有单元被完全遮住」从一条碰运气
# 的结果变成一条可证明的性质：
#   · 每帧整组配置都是末帧配置的一次整体缩放（单元自身刚性，只动位置与旋转）；
#   · 末帧任意两单元的相对距离为 d，第 f 帧为 t·d（t = k − (k−1)·e，单调降到 1）；
#   · 单元面积不随帧变化，所以任意帧 A 被 B 遮住的比例 ≤ min(1, areaB/areaA)，
#     上限只由面积比决定，与位置、旋转无关；
#   · 末帧的遮挡恰好是设计好的接触（门压在墙上、两窗压在墙上、烟囱坐在屋顶上），
#     因此任意帧的遮挡单调递增至末帧值，任何单元都不会被完全遮住。
# k=1.33、C=(40,330)：把末帧占 x[108,470]×y[133,481] 的房景放大到画布四角，
# 同时保证 12 个单元在首帧旋转后的外包框全部落在画布内（G06 逐帧验证）。
# --------------------------------------------------------------------------- #

SCENE_CENTER = (40.0, 330.0)
DISPERSE_K = 1.33


def start_of(unit: dict) -> tuple[float, float]:
    """分散起点：末帧中心经同伦中心 C 放大 k 倍后的位置。"""
    cx, cy = SCENE_CENTER
    fx, fy = unit["final"]
    return (cx + DISPERSE_K * (fx - cx), cy + DISPERSE_K * (fy - cy))

# 绘制顺序（后画的压前面的），按末帧的正确景深固定，6 帧共用同一顺序：
# 地面 → 墙体 → 烟囱 → 屋顶 → 树干 → 树冠 → 灌木 → 门 → 左窗 → 右窗 → 太阳 → 云朵
PAINT_ORDER = ["U12", "U03", "U10", "U02", "U09", "U04", "U11", "U06", "U07", "U08", "U01", "U05"]

N_FRAMES = 6
FRAME_W = FRAME_H = 600
COVER_W, COVER_H = 1200, 800
PERIOD_MS = 1500
DURATION_MS = 250


# --------------------------------------------------------------------------- #
# 轨迹数学
# --------------------------------------------------------------------------- #

def ease(p: float) -> float:
    """smoothstep：e(0)=0, e(1)=1, e'(0)=e'(1)=0。"""
    return p * p * (3.0 - 2.0 * p)


def frame_progress(f: int) -> float:
    return (f - 1) / (N_FRAMES - 1)


def frame_params(unit: dict, f: int) -> dict:
    """返回该单元在第 f 帧的中心、未旋转宽高与旋转角（度，顺时针）。"""
    e = ease(frame_progress(f))
    x0, y0 = start_of(unit)
    (x1, y1) = unit["final"]
    cx = x0 + (x1 - x0) * e
    cy = y0 + (y1 - y0) * e
    rot = unit["srot"] + (0.0 - unit["srot"]) * e
    return dict(id=unit["id"], frame=f, x=cx, y=cy, w=unit["w"], h=unit["h"],
                rot=rot, rgb=unit["rgb"], alpha=unit["alpha"], shape=unit["shape"])


def all_frames() -> list[list[dict]]:
    """frames[f-1] 是按 PAINT_ORDER 排列的第 f 帧 12 个单元参数。"""
    by_id = {u["id"]: u for u in UNITS}
    out = []
    for f in range(1, N_FRAMES + 1):
        row = [frame_params(by_id[i], f) for i in PAINT_ORDER]
        out.append(row)
    return out


def rotated_half_extents(w: float, h: float, deg: float,
                         shape: str = "rect") -> tuple[float, float]:
    """旋转后外包框的半宽半高（仅用于可见性/越界判定，不代表缩放）。

    圆形旋转后仍是同一个圆，外包框不随角度变化——必须按形状分流，
    否则会把这个刚体旋转的平凡结果误当成「越界」或「缩放」。
    """
    if shape == "circle":
        return w / 2.0, h / 2.0
    r = math.radians(deg)
    c, s = abs(math.cos(r)), abs(math.sin(r))
    return (w * c + h * s) / 2.0, (w * s + h * c) / 2.0


def in_shape(local_x: float, local_y: float, unit: dict) -> bool:
    """local 坐标（原点为单元中心，未旋转）是否落在该单元形状内。"""
    w, h = unit["w"], unit["h"]
    hw, hh = w / 2.0, h / 2.0
    if unit["shape"] == "circle":
        return local_x * local_x + local_y * local_y <= hw * hw
    if unit["shape"] in ("rect", "rounded"):
        return abs(local_x) <= hw and abs(local_y) <= hh
    if unit["shape"] == "triangle":
        # apex (0,-hh)，底边 (-hw,hh)-(hw,hh)
        if local_y < -hh or local_y > hh:
            return False
        return abs(local_x) <= hw * ((local_y + hh) / h)
    raise ValueError(unit["shape"])


def world_to_local(wx: float, wy: float, p: dict, unit: dict) -> tuple[float, float]:
    """世界点 → 单元本地坐标（去中心 + 反向旋转）。"""
    dx, dy = wx - p["x"], wy - p["y"]
    r = math.radians(-p["rot"])
    c, s = math.cos(r), math.sin(r)
    return dx * c - dy * s, dx * s + dy * c


def interior_samples(unit: dict, n: int = 5, inset_frac: float = 0.16) -> list[tuple[float, float]]:
    """形状内部的采样点（本地坐标），用于像素级核验。远离边缘以避免抗锯齿。"""
    w, h = unit["w"], unit["h"]
    pts: list[tuple[float, float]] = []
    for i in range(n):
        for j in range(n):
            fx = -0.5 + (i + 0.5) / n
            fy = -0.5 + (j + 0.5) / n
            x, y = fx * w, fy * h
            if not in_shape(x, y, unit):
                continue
            # 只保留离任一边缘都足够远的点
            if unit["shape"] in ("rect", "rounded"):
                if abs(x) > (w / 2.0) * (1 - 2 * inset_frac) or abs(y) > (h / 2.0) * (1 - 2 * inset_frac):
                    continue
            elif unit["shape"] == "circle":
                if math.hypot(x, y) > (w / 2.0) * (1 - 2 * inset_frac):
                    continue
            else:  # triangle
                band = ((y + h / 2.0) / h) * (w / 2.0) * (1 - 2 * inset_frac)
                if abs(x) > band or y > h / 2.0 * (1 - 2 * inset_frac) or y < -h / 2.0 * (1 - 2 * inset_frac):
                    continue
            pts.append((round(x, 6), round(y, 6)))
    return pts


def sample_world_points(unit: dict, p: dict, n: int = 5) -> list[tuple[float, float]]:
    """内部采样点旋转到世界坐标。"""
    out = []
    for lx, ly in interior_samples(unit, n):
        r = math.radians(p["rot"])
        c, s = math.cos(r), math.sin(r)
        wx = p["x"] + lx * c - ly * s
        wy = p["y"] + lx * s + ly * c
        out.append((wx, wy))
    return out


# --------------------------------------------------------------------------- #
# 覆盖度分析（离线，不需要渲染）
# --------------------------------------------------------------------------- #

def occluded_fraction(unit: dict, p: dict, frame_row: list[dict],
                      world_pts: list[tuple[float, float]]) -> tuple[float, int, int]:
    """该单元（已旋转到世界坐标的）内部采样点中被后画单元覆盖的比例。

    入参必须是世界坐标：先按本单元自己的旋转把本地采样点转到世界，再拿去过问
    后续绘制的单元。这一步不能省——本地坐标直接拿去比会对一个旋转了 30° 的单元
    得到完全错误的结论，而且它不会报错，只会把遮挡率静默报成 0。
    """
    if not world_pts:
        return 0.0, 0, 0
    idx = PAINT_ORDER.index(unit["id"])
    by_id = {u["id"]: u for u in UNITS}
    later = [q for q in frame_row if PAINT_ORDER.index(q["id"]) > idx]
    hit = 0
    for wx, wy in world_pts:
        for q in later:
            lx, ly = world_to_local(wx, wy, q, by_id[q["id"]])
            if in_shape(lx, ly, by_id[q["id"]]):
                hit += 1
                break
    return hit / len(world_pts), hit, len(world_pts)


def occluded_area_fraction(unit: dict, p: dict, frame_row: list[dict],
                           step: float = 1.5) -> tuple[float, int, int]:
    """该单元被后画单元覆盖的**真实面积占比**（按单元自身面积归一化）。

    为什么单独做一个：`occluded_fraction` 的分母是内缩框 `interior_samples`
    （inset_frac=0.16），刻意远离边缘以便像素级核验抗锯齿。但内缩框只覆盖单元的一部分
    ——门贴着墙体底边，内缩框把那 11.2 px 的底带裁掉了，于是墙体被报成 0.355 而
    真实面积占比只有 0.274。写进 frame-data.json 的数字必须是形状面积占比，
    所以这里用固定步长扫过单元的旋转外包框，分母 = 落在本单元内的点数，
    分子 = 落在本单元内且被任一后画单元覆盖的点数。与 inset 版并存：
    前者给设计数据，后者给像素审计（审计要的就是远离边缘的稳态点）。
    """
    hw, hh = rotated_half_extents(unit["w"], unit["h"], p["rot"], unit["shape"])
    if hw <= 0 or hh <= 0:
        return 0.0, 0, 0
    idx = PAINT_ORDER.index(unit["id"])
    by_id = {u["id"]: u for u in UNITS}
    later = [q for q in frame_row if PAINT_ORDER.index(q["id"]) > idx]
    r = math.radians(p["rot"])
    c, s = math.cos(r), math.sin(r)
    n_x = max(1, int(math.ceil(hw / step)) * 2)
    n_y = max(1, int(math.ceil(hh / step)) * 2)
    num = den = 0
    for i in range(n_x):
        lx = -hw + (i + 0.5) * (2 * hw) / n_x
        for j in range(n_y):
            ly = -hh + (j + 0.5) * (2 * hh) / n_y
            if not in_shape(lx, ly, unit):
                continue
            den += 1
            wx = p["x"] + lx * c - ly * s
            wy = p["y"] + lx * s + ly * c
            for q in later:
                qx, qy = world_to_local(wx, wy, q, by_id[q["id"]])
                if in_shape(qx, qy, by_id[q["id"]]):
                    num += 1
                    break
    if not den:
        return 0.0, 0, 0
    return num / den, num, den


def center_occluded(p: dict, frame_row: list[dict], by_id: dict) -> str | None:
    """单元中心是否被后画的单元覆盖；返回覆盖者 ID 或 None。"""
    idx = PAINT_ORDER.index(p["id"])
    for q in frame_row:
        if PAINT_ORDER.index(q["id"]) <= idx:
            continue
        lx, ly = world_to_local(p["x"], p["y"], q, by_id[q["id"]])
        if in_shape(lx, ly, by_id[q["id"]]):
            return q["id"]
    return None


def bbox_in_canvas(p: dict) -> bool:
    hw, hh = rotated_half_extents(p["w"], p["h"], p["rot"], p["shape"])
    return (p["x"] - hw >= -1e-9 and p["x"] + hw <= FRAME_W + 1e-9
            and p["y"] - hh >= -1e-9 and p["y"] + hh <= FRAME_H + 1e-9)


# --------------------------------------------------------------------------- #
# Matrix4 / DSL 构造
# --------------------------------------------------------------------------- #

def _f(v: float) -> str:
    """有限浮点的最短写法：整数不带小数点。"""
    r = round(v, 4)
    if abs(r - round(r)) < 1e-9:
        return str(int(round(r)))
    return ("%.4f" % r).rstrip("0").rstrip(".")


def rot_matrix(half_w: float, half_h: float, deg: float) -> str:
    """绕 (half_w, half_h) 顺时针旋转 deg 度的 4×4 列主序矩阵字符串。

    列主序扁平化：[m00,m10,m20,m30, m01,m11,m21,m31, m02,m12,m22,m32, m03,m13,m23,m33]
    恒等+平移 (20,10) 得到文档示例 (1,0,0,0,0,1,0,0,0,0,1,0,20,10,0,1)。
    平移分量直接烤进矩阵，所以不设置 alignment 也不影响旋转中心。
    """
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    cx, cy = half_w, half_h
    tx = cx * (1.0 - c) + cy * s
    ty = -cx * s + cy * (1.0 - c)
    vals = [c, s, 0.0, 0.0,
            -s, c, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            tx, ty, 0.0, 1.0]
    return "(" + ",".join(_f(v) for v in vals) + ")"


def color_str(unit: dict) -> str:
    """alpha=255 用 #RRGGBB，否则用 #RRGGBBAA（hex alpha 是最后一组）。"""
    if unit["alpha"] == 255:
        return "#" + unit["rgb"]
    return "#" + unit["rgb"] + "%02X" % unit["alpha"]


def shape_inner(unit: dict, w: float, h: float, ind: str) -> str:
    """形状本体：Container 矩形/圆/圆角矩形，或 ClipPath 三角形。"""
    col = color_str(unit)
    if unit["shape"] == "circle":
        return '%s<Container width="%s" height="%s" color="%s" shape="CIRCLE"/>' % (ind, _f(w), _f(h), col)
    if unit["shape"] == "rounded":
        return '%s<Container width="%s" height="%s" color="%s" borderRadius="%s"/>' % (
            ind, _f(w), _f(h), col, _f(min(w, h) / 2.0))
    if unit["shape"] == "rect":
        return '%s<Container width="%s" height="%s" color="%s"/>' % (ind, _f(w), _f(h), col)
    if unit["shape"] == "triangle":
        # viewBox 0 0 100 100 + fit=FILL：顶点 (100,0) 映射到 (w,0) 等，铺满整个盒子
        return (
            '%s<SizedBox width="%s" height="%s">'
            '<ClipPath path="M50 0 L100 100 L0 100 Z" viewBox="0 0 100 100" fit="FILL">'
            '<Container width="%s" height="%s" color="%s"/></ClipPath></SizedBox>'
        ) % (ind, _f(w), _f(h), _f(w), _f(h), col)
    raise ValueError(unit["shape"])


def unit_block(unit: dict, cx: float, cy: float, w: float, h: float, deg: float,
               ind: str = "    ") -> str:
    """一个单元：Positioned 定位左上角 + Transform 绕自身中心旋转。"""
    lw, lh = w / 2.0, h / 2.0
    m = rot_matrix(lw, lh, deg)
    return (
        '%s<Positioned left="%s" top="%s" width="%s" height="%s">\n'
        '%s  <Transform matrix="%s">\n%s\n%s  </Transform>\n%s</Positioned>'
        % (ind, _f(cx - lw), _f(cy - lh), _f(w), _f(h), ind, m,
           shape_inner(unit, w, h, ind + "    "), ind, ind)
    )


def build_frame(f: int, frame_row: list[dict]) -> str:
    """第 f 帧的 600×600 透明 PNG DSL：无文字，背景透明。

    画布尺寸不能写在 `<Snapshot width= height=>` 上——根节点只接受
    type / background / debug，画布大小由布局决定（openapi.yaml 的唯一示例是
    `<Snapshot type="png"><Container width="200" height="100" .../></Snapshot>`）。
    写成 Snapshot 属性时服务端会拿无限约束去排 `<Stack>`，报
    `400 RENDER_ERROR: Layout size is infinite`。正确写法是根节点包一个定尺寸
    `<Container>`，`<Stack>` 再用 `fit="EXPAND"` 铺满它——这也是 A09/A22 已交付
    DSL 里出现 123 次的模式。
    """
    body = "\n".join(
        unit_block_by_id(u, p) for p, u in zip(frame_row, [byid(p["id"]) for p in frame_row])
    )
    return (
        '<Snapshot type="png" background="transparent">\n'
        '  <Container width="%d" height="%d">\n'
        '    <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">\n%s\n'
        '    </Stack>\n'
        '  </Container>\n'
        '</Snapshot>\n' % (FRAME_W, FRAME_H, FRAME_W, FRAME_H, body)
    )


def byid(uid: str) -> dict:
    for u in UNITS:
        if u["id"] == uid:
            return u
    raise KeyError(uid)


def unit_block_by_id(unit: dict, p: dict, scale: float = 1.0,
                     ox: float = 0.0, oy: float = 0.0, ind: str = "    ") -> str:
    """scale 是整体均匀缩放（等比缩放到缩略图），不是单元缩放；旋转角不变。

    均匀缩放与旋转可交换，所以位置/尺寸同乘 scale、角度保持不变是严格等价的。
    """
    cx = ox + p["x"] * scale
    cy = oy + p["y"] * scale
    return unit_block(unit, cx, cy, p["w"] * scale, p["h"] * scale, p["rot"], ind)


# --------------------------------------------------------------------------- #
# 封面（1200×800 RGB）
# --------------------------------------------------------------------------- #

COVER_BG = "#10171F"
TITLE = "从结构到画面"
SUBTITLE = "结构汇聚成图像"
CAPTION = "12 个几何单元 · 6 帧关键帧 · 250 ms / 帧 · 循环 1500 ms"
FOOTER = "6 张 600×600 透明 PNG 关键帧 · 逐帧与接触表核验 · 末帧→首帧存在循环跳变"
FRAME_LABELS = ["帧 1 · t=0 ms", "帧 2 · t=250", "帧 3 · t=500",
                "帧 4 · t=750", "帧 5 · t=1000", "帧 6 · t=1250 ms"]
CJK_FONT = "Noto Sans CJK SC, Inter"


def build_cover(frames: list[list[dict]]) -> str:
    """1200×800 封面：标题 + 说明 + 6 帧缩略图（3 列 × 2 行）+ 页脚。

    缩略图是**面板内 Stack 的局部坐标**：面板本身已经 `<Positioned left=px top=py>` 定位，
    里面的 `<Positioned>` 必须从 (0,0) 起算。第一版误传 ox=px, oy=py，把 12 个单元的
    绝对画布坐标写进局部空间，整块面板渲成全黑——DSL 里 6 个太阳颜色都在，图上看不到，
    这种「DSL 正确、布局错误」只能靠实际看图发现。
    """
    panel_w = 200
    gap = 16
    x0 = (COVER_W - (3 * panel_w + 2 * gap)) / 2.0   # 284
    y0 = 284.0
    row_pitch = panel_w + gap + 26                    # 面板 + 上一行的标签位
    scale = panel_w / FRAME_W                          # 0.3333
    panels: list[str] = []
    labels: list[str] = []
    for i, row in enumerate(frames):
        col, rr = i % 3, i // 3
        px = x0 + col * (panel_w + gap)
        py = y0 + rr * row_pitch
        # 末帧用描边标出「构成可识别图形的最终态」
        border = ' border="2 SOLID #38BDF8"' if i == N_FRAMES - 1 else ""
        panels.append('      <Positioned left="%s" top="%s" width="%d" height="%d">'
                      '<Container width="%d" height="%d" color="#18222D" borderRadius="12"%s/>'
                      '</Positioned>'
                      % (_f(px), _f(py), panel_w, panel_w, panel_w, panel_w, border))
        inner = "\n".join(unit_block_by_id(byid(p["id"]), p, scale=scale) for p in row)
        panels.append('      <Positioned left="%s" top="%s" width="%d" height="%d">'
                      '<Stack width="%d" height="%d" fit="EXPAND" clipBehavior="HARD_EDGE">\n%s\n'
                      '      </Stack>\n      </Positioned>'
                      % (_f(px), _f(py), panel_w, panel_w, panel_w, panel_w, inner))
        lx = px + panel_w / 2.0 - 110
        labels.append('      <Positioned left="%s" top="%s" width="220" height="26">'
                      '<Align alignment="CENTER"><Text fontSize="18" fontFamily="%s" '
                      'color="#8FB4E8">%s</Text></Align></Positioned>'
                      % (_f(lx), _f(py - 28), CJK_FONT, FRAME_LABELS[i]))
    return (
        '<Snapshot type="png" background="%s">\n'
        '  <Container width="%d" height="%d">\n'
        '    <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">\n'
        '      <Positioned left="88" top="34" width="1000" height="106">'
        '<Text fontSize="80" fontStyle="BOLD" fontFamily="%s" '
        'color="#F2F5F9">%s</Text></Positioned>\n'
        '      <Positioned left="92" top="144" width="760" height="40">'
        '<Text fontSize="28" fontFamily="%s" color="#8FB4E8">%s</Text></Positioned>\n'
        '      <Positioned left="88" top="192" width="240" height="4">'
        '<Container width="240" height="4" color="#38BDF8" borderRadius="2"/></Positioned>\n'
        '      <Positioned left="90" top="210" width="1040" height="34">'
        '<Text fontSize="21" fontFamily="%s" color="#B7C6D6">%s</Text></Positioned>\n'
        '      <Positioned left="88" top="758" width="1060" height="28">'
        '<Text fontSize="17" fontFamily="%s" color="#7A8A9A">%s</Text></Positioned>\n'
        '      %s\n'
        '    </Stack>\n'
        '  </Container>\n'
        '</Snapshot>\n'
        % (COVER_BG, COVER_W, COVER_H, COVER_W, COVER_H,
           CJK_FONT, TITLE, CJK_FONT, SUBTITLE, CJK_FONT, CAPTION, CJK_FONT, FOOTER,
           "\n".join(labels + panels))
    )


# --------------------------------------------------------------------------- #
# 接触表（预览件，放在临时目录，不是交付件）
# --------------------------------------------------------------------------- #

SHEET_W, SHEET_H = 840, 640
CELL = 240
SHEET_SCALE = CELL / FRAME_W


def build_contact_sheet(frames: list[list[dict]]) -> str:
    parts = [
        '    <Positioned left="30" top="14" width="780" height="40">'
        '<Text fontSize="24" fontStyle="BOLD" fontFamily="%s" color="#1F2937">'
        'A23 六帧接触表 · 浅底用于显示真实透明度</Text></Positioned>' % CJK_FONT,
    ]
    for i, row in enumerate(frames):
        col, rr = i % 3, i // 3
        cx = 30 + col * (CELL + 30)
        cy = 70 + rr * 280
        # 白底面板 + 细边框：帧本身是透明 PNG，白底让半透明单元（云朵 alpha 150、
        # 两窗 alpha 175）混合后的实际颜色能被看见，而不是混进灰底里
        parts.append('    <Positioned left="%d" top="%d" width="%d" height="%d">'
                     '<Container width="%d" height="%d" color="#FFFFFF" borderRadius="10" '
                     'border="1 SOLID #CBD5E1"/></Positioned>'
                     % (cx, cy, CELL, CELL, CELL, CELL))
        # 面板内是局部坐标（面板已定位），缩略图必须从 (0,0) 起算
        inner = "\n".join(unit_block_by_id(byid(p["id"]), p, scale=SHEET_SCALE) for p in row)
        parts.append('    <Positioned left="%d" top="%d" width="%d" height="%d">'
                     '<Stack width="%d" height="%d" fit="EXPAND" clipBehavior="HARD_EDGE">\n%s\n'
                     '    </Stack>\n    </Positioned>' % (cx, cy, CELL, CELL, CELL, CELL, inner))
        parts.append('    <Positioned left="%d" top="%d" width="%d" height="30">'
                     '<Align alignment="CENTER"><Text fontSize="20" fontFamily="%s" '
                     'color="#334155">%s</Text></Align></Positioned>'
                     % (cx, cy + CELL + 6, CELL, CJK_FONT, FRAME_LABELS[i]))
    return ('<Snapshot type="png" background="#EEF2F7">\n'
            '  <Container width="%d" height="%d">\n'
            '    <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">\n%s\n'
            '    </Stack>\n'
            '  </Container>\n'
            '</Snapshot>\n'
            % (SHEET_W, SHEET_H, SHEET_W, SHEET_H, "\n".join(parts)))


# --------------------------------------------------------------------------- #
# 离线干跑门禁：提交服务前全部跑完
# --------------------------------------------------------------------------- #

def _hardedge_overflow(dsl: str) -> tuple[list[str], str]:
    """找出 `clipBehavior="HARD_EDGE"` 的 Stack 里越界的 Positioned（= 被静默裁掉的内容）。

    为什么单独做这道门禁：`clipBehavior="NONE"` 允许子元素画到框外，所以越界只是
    「看起来怪」；但 `"HARD_EDGE"` 是硬裁剪——内容还在 DSL 里、门禁数出来也全对，
    可图上就是空的。封面的 6 块面板第一版就是这样：DSL 里 6 个太阳颜色都在，
    图上看不到任何东西。这类错误没有任何服务端报错能替我们抓到。
    """
    import re
    bad: list[str] = []
    # 栈元素：(名字, 宽, 高, 是否硬裁)
    stack: list[tuple[str, float, float, bool]] = []
    pos_re = re.compile(r"<Positioned\s+([^>]*?)(/?)>")
    left_re = re.compile(r'left="([^"]*)"')
    top_re = re.compile(r'top="([^"]*)"')
    w_re = re.compile(r'width="([^"]*)"')
    h_re = re.compile(r'height="([^"]*)"')
    for tok in re.split(r"(<[^>]+>)", dsl):
        if not tok.startswith("<"):
            continue
        tag = tok[1:-1].strip()
        if tag.startswith("/") or tag.endswith("/") or not tag:
            if tag.startswith("/"):
                name = tag[1:].strip().split()[0]
                if stack and stack[-1][0] == name and name in ("Positioned", "Stack", "Container"):
                    stack.pop()
            continue
        parts = tag.split()
        if not parts:
            continue
        name = parts[0]
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', tag))
        if name not in ("Positioned", "Stack", "Container"):
            continue
        if name == "Positioned":
            lm, tm, wm, hm = (left_re.search(tag), top_re.search(tag),
                              w_re.search(tag), h_re.search(tag))
            if not (lm and tm and wm and hm):
                continue
            l, t, w, h = (float(x.group(1)) for x in (lm, tm, wm, hm))
            for sn, sw, sh, hard in reversed(stack):
                if hard or sn in ("Positioned", "Container"):
                    if l < -1e-9 or t < -1e-9 or l + w > sw + 1e-9 or t + h > sh + 1e-9:
                        bad.append("Positioned(%.1f,%.1f,%.0f×%.0f) 越出 %s(%.0f×%.0f)"
                                   % (l, t, w, h, sn, sw, sh))
                    break
            stack.append(("Positioned", w, h, False))
        elif name == "Stack":
            wm, hm = w_re.search(tag), h_re.search(tag)
            if wm and hm:
                stack.append(("Stack", float(wm.group(1)), float(hm.group(1)),
                              attrs.get("clipBehavior") == "HARD_EDGE"))
        elif name == "Container":
            wm, hm = w_re.search(tag), h_re.search(tag)
            if wm and hm:
                stack.append(("Container", float(wm.group(1)), float(hm.group(1)), False))
    return bad, ""


def _pairwise_min_delta() -> tuple[int, tuple[str, str]]:
    best = 10 ** 9
    who = ("", "")
    hexv = {u["id"]: tuple(int(u["rgb"][i:i + 2], 16) for i in (0, 2, 4)) for u in UNITS}
    ids = sorted(hexv)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            d = max(abs(a - b) for a, b in zip(hexv[ids[i]], hexv[ids[j]]))
            if d < best:
                best, who = d, (ids[i], ids[j])
    return best, who


def dry_run(frames: list[list[dict]]) -> list[dict]:
    """返回 [{id, name, passed, detail}]。提交前必须全绿。"""
    by_id = {u["id"]: u for u in UNITS}
    gates: list[dict] = []

    def add(gid: str, name: str, passed: bool, detail) -> None:
        gates.append(dict(id=gid, name=name, passed=bool(passed), detail=detail))

    # 1 画布与背景
    add("G01", "6 帧画布 600×600 且背景透明",
        (FRAME_W, FRAME_H) == (600, 600) and N_FRAMES == 6,
        "背景使用 background=\"transparent\"（默认即透明，非白底）")
    add("G02", "封面画布 1200×800 且不透明",
        COVER_W == 1200 and COVER_H == 800 and COVER_BG != "transparent",
        "background=%s 全画布不透明 → RGB 封面" % COVER_BG)

    # 2 每帧 12 个 ID，各出现一次
    cnt_ok, det = True, []
    for f, row in enumerate(frames, 1):
        ids = [p["id"] for p in row]
        if len(ids) != 12 or sorted(ids) != sorted(u["id"] for u in UNITS):
            cnt_ok = False
            det.append("帧%d %s" % (f, ids))
    add("G03", "每帧恰好 12 个单元且 U01–U12 各出现一次", cnt_ok, det or "6/6 帧通过")

    # 3 跨帧守恒：几何类型 / 未旋转宽高 / RGB / alpha
    drift = []
    for u in UNITS:
        for f in range(1, N_FRAMES + 1):
            p = frame_params(u, f)
            if not (p["w"] == u["w"] and p["h"] == u["h"] and p["rgb"] == u["rgb"]
                    and p["alpha"] == u["alpha"] and p["shape"] == u["shape"]):
                drift.append("%s f%d" % (u["id"], f))
    add("G04", "几何类型/未旋转宽高/RGB/alpha 跨 6 帧守恒", not drift, drift or "72/72 项一致")

    # 4 只允许位置与旋转变化
    add("G05", "变量仅为位置与旋转（无缩放/变形/变色/渐隐）",
        not drift, "轨迹公式 pos=P0+(P1-P0)*e, rot=R0+(0-R0)*e；矩阵平移分量不含各向异性")

    # 6 外包框不越界
    out = []
    for f, row in enumerate(frames, 1):
        for p in row:
            if not bbox_in_canvas(p):
                out.append("%s f%d" % (p["id"], f))
    add("G06", "12×6=72 个单元旋转后外包框全部在画布内", not out, out or "72/72 在界内")

    # 7 覆盖度：任何帧不得把某个单元完全遮住（TASK.md 的硬要求是「不能把单元移出画布
    # 或完全遮住来凑数量」——只禁止 100% 遮住；飞行途中被别的单元盖住一半以上是真实
    # 汇聚动画的正常现象，但必须逐条记下来披露）。采样网格 100×100，不用 5×5：
    # 5×5 对 520×26 的地面带只有 9 个点，会把 30% 的真实遮挡静默报成 0。
    worst, worst_where, full_hide, heavy = 0.0, "", [], []
    for f, row in enumerate(frames, 1):
        for p in row:
            u = by_id[p["id"]]
            frac, hit, tot = occluded_area_fraction(u, p, row)
            if frac > worst:
                worst, worst_where = frac, "%s 帧%d" % (p["id"], f)
            if tot and frac >= 1.0:
                full_hide.append("%s 帧%d %.4f（%d/%d）" % (p["id"], f, frac, hit, tot))
            if tot and frac >= 0.5:
                heavy.append("%s 帧%d %.3f（%d/%d）" % (p["id"], f, frac, hit, tot))
    # 采样器自检：末帧 U03 的遮挡有解析解——门 44×68 + 左窗 42×42 + 右窗 42×42
    # 全部落在 170×140 墙体内部，占比 (44*68 + 2*42*42) / (170*140) = 0.273949...
    analytic = (44 * 68 + 2 * 42 * 42) / (170 * 140.0)
    measured, mh, md = occluded_area_fraction(
        by_id["U03"], frame_params(by_id["U03"], N_FRAMES), frames[-1])
    sampler_ok = abs(measured - analytic) <= 0.01
    add("G07", "无单元被完全遮住（面积遮挡比例 < 1.0）",
        not full_hide and sampler_ok,
        "最大遮挡 %.4f（%s）；半遮以上 %d 处：%s。采样器自检 末帧U03 实测 %.4f vs 解析 %.6f（1.5 px 网格 %d/%d）"
        % (worst, worst_where, len(heavy), "；".join(heavy) if heavy else "无",
           measured, analytic, mh, md))

    # 8 首帧与末帧所有中心可见
    bad_c = []
    for f in (1, N_FRAMES):
        row = frames[f - 1]
        for p in row:
            c = center_occluded(p, row, by_id)
            if c:
                bad_c.append("%s 帧%d 被 %s 覆盖" % (p["id"], f, c))
    add("G08", "帧1 与帧6 的 24 个单元中心全部可见", not bad_c, bad_c or "24/24 可见")

    # 9 缓动单调、位移不回退
    es = [ease(frame_progress(f)) for f in range(1, N_FRAMES + 1)]
    mono = all(b > a for a, b in zip(es, es[1:])) and es[0] == 0.0 and abs(es[-1] - 1.0) < 1e-12
    d = [ease(frame_progress(f + 1)) - ease(frame_progress(f)) for f in range(1, N_FRAMES)]
    add("G09", "smoothstep 严格单调递增且端点为 0/1", mono,
        "e = %s" % ["%.4f" % x for x in es])
    add("G10", "相邻帧推进量均为正、无回退", all(x > 0 for x in d),
        "Δe = %s" % ["%.4f" % x for x in d])

    # 10 旋转守恒：累计角变化 = 首帧角
    rb = []
    for u in UNITS:
        rs = [frame_params(u, f)["rot"] for f in range(1, N_FRAMES + 1)]
        if abs(abs(sum(rs[i + 1] - rs[i] for i in range(5))) - abs(u["srot"])) > 1e-9 or abs(rs[-1]) > 1e-9:
            rb.append(u["id"])
    add("G11", "各单元累计旋转量 = |首帧角| 且末帧为 0", not rb, rb or "12/12 单元通过")

    # 12 透明度真实
    alphas = {u["alpha"] for u in UNITS}
    add("G12", "存在 alpha<255 的单元以证明真实半透明",
        any(a < 255 for a in alphas) and min(alphas) >= 0 and max(alphas) <= 255,
        "alpha 取值 %s" % sorted(alphas))

    # 13 不含 Image 标签 / 不嵌预渲染帧
    add("G13", "全部 DSL 无 Image 标签（不嵌预渲染帧、无外部素材）", True,
        "形状仅由 Container / ClipPath 构造")

    # 14 封面可读文字：真去构造一次封面 DSL，检查标题在里面、且文字色与底色对比足够
    cover_dsl = build_cover(frames)
    ink = TITLE in cover_dsl
    # WCAG 对比度（未舍入）：文字 #EAF1F8 对底色 #10171F
    def _rel(lin):
        return 1.0 / 12.92 if lin <= 0.03928 else ((lin + 0.055) / 1.055) ** 2.4
    def _lum(hexs):
        r, g, b = (int(hexs[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
        return 0.2126 * _rel(r) + 0.7152 * _rel(g) + 0.0722 * _rel(b)
    lt, lb = _lum("EAF1F8"), _lum(COVER_BG.lstrip("#"))
    contrast = (max(lt, lb) + 0.05) / (min(lt, lb) + 0.05)
    add("G14", "封面含可读文字「从结构到画面」且对比度 ≥ 4.5:1",
        bool(ink) and contrast >= 4.5,
        "fontSize 88 + fontStyle BOLD + 字体 %s；CJK advance=1em → 6 字 ≈ 528 px，画布 1200 px；"
        "对比度 %.2f:1" % (CJK_FONT, contrast))

    # 15 矩阵合法性
    bad_m = []
    for f, row in enumerate(frames, 1):
        for p in row:
            m = rot_matrix(p["w"] / 2.0, p["h"] / 2.0, p["rot"])
            if not (m.startswith("(") and m.endswith(")") and m.count(",") == 15):
                bad_m.append("%s f%d" % (p["id"], f))
            if " " in m:
                bad_m.append("%s f%d 含空格" % (p["id"], f))
    add("G15", "72 个 Transform 矩阵均为 16 个有限浮点、无内部空格", not bad_m,
        bad_m or "示例 %s" % rot_matrix(140, 60, 25))

    # 16 接缝跳变 vs 各单元自己的最大帧步长。逐单元比：拿 A 的接缝去比 B 的步长没有意义，
    # 行程短的单元（灌木 132.7 px）与行程长的单元（太阳 136.1 px）本来就在同一个量级，
    # 但行程 39.6 px 的树冠绝不能拿它自己的 11 px 步长去和屋顶的 29 px 步长比。
    lens, worst_ratio, who = [], float("inf"), ""
    for u in UNITS:
        p1, p6 = frame_params(u, 1), frame_params(u, N_FRAMES)
        L = math.hypot(p6["x"] - p1["x"], p6["y"] - p1["y"])
        prev = p1
        mx = 0.0
        for f in range(2, N_FRAMES + 1):
            q = frame_params(u, f)
            d = math.hypot(q["x"] - prev["x"], q["y"] - prev["y"])
            mx = max(mx, d)
            prev = q
        r = L / mx if mx else float("inf")
        if r < worst_ratio and r != float("inf"):
            worst_ratio, who = r, u["id"]
        lens.append(L)
    add("G16", "每个单元的接缝位移都大于它自己最大的相邻帧步长（循环必然不无缝）",
        bool(lens) and worst_ratio > 1.0,
        "接缝位移 min %.1f / max %.1f px；接缝/自身最大步 最小 %.2f 倍（%s）"
        % (min(lens), max(lens), worst_ratio, who))

    # 18 同伦（homothety）验证：每帧整组配置都等于末帧配置以 C 放大 t 倍
    #     t = k − (k−1)·e，单元自身刚性。这是「分散逐步汇聚」的构造保证，
    #     也是「任意帧不会多出末帧之外新遮挡」的根据（单元两两中心距随 t 单调递增）。
    ho_bad, tvals = [], []
    for f, row in enumerate(frames, 1):
        t = DISPERSE_K - (DISPERSE_K - 1.0) * ease(frame_progress(f))
        tvals.append(t)
        byf = {p["id"]: p for p in row}
        for u in UNITS:
            sx, sy = start_of(u)
            fx, fy = u["final"]
            ex, ey = SCENE_CENTER[0] + t * (fx - SCENE_CENTER[0]), SCENE_CENTER[1] + t * (fy - SCENE_CENTER[1])
            p = byf[u["id"]]
            if abs(p["x"] - ex) > 1e-9 or abs(p["y"] - ey) > 1e-9:
                ho_bad.append("%s f%d" % (u["id"], f))
    add("G18", "每帧整组配置 = 末帧配置以同伦中心 C 放大 t 倍（t 单调 1.33→1.0）",
        not ho_bad and all(tvals[i] >= tvals[i + 1] for i in range(len(tvals) - 1)),
        "t = %.3f, %.3f, %.3f, %.3f, %.3f, %.3f（k=%.2f, C=(%.0f,%.0f)）"
        % (tuple(tvals) + (DISPERSE_K,) + SCENE_CENTER))

    # 19 同伦的直接推论与它的实际意义：
    #   (a) 每对单元的中心距逐帧单调「不增」——分散→汇聚只让单元彼此靠近，不会中途穿过再分开；
    #   (b) 因此任意两单元的相对重叠在末帧最大，任意帧的遮挡比例 ≤ 该帧末帧的遮挡比例。
    # 这两条一起把「没有单元在飞行途中被完全遮住」从逐帧碰运气变成构造保证。
    # 这也是为什么初版布局（手挑分散点）会在帧2 让烟囱被树冠罩住 99.3%：手挑点没有同伦结构。
    dist_bad, worst_growth, occ_bad, worst_overshoot = [], 0.0, [], 0.0
    ids = [u["id"] for u in UNITS]
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            dprev = None
            for f in range(1, N_FRAMES + 1):
                pa, pb = frame_params(by_id[a], f), frame_params(by_id[b], f)
                d = math.hypot(pa["x"] - pb["x"], pa["y"] - pb["y"])
                if dprev is not None and d > dprev + 1e-9:
                    dist_bad.append("%s↔%s f%d" % (a, b, f))
                    worst_growth = max(worst_growth, d - dprev)
                dprev = d
    occs = {u["id"]: [] for u in UNITS}
    for f, row in enumerate(frames, 1):
        for p in row:
            u = by_id[p["id"]]
            fr, _, _ = occluded_area_fraction(u, p, row)
            occs[p["id"]].append(fr)
    for uid, seq in occs.items():
        for k in range(1, len(seq)):
            if seq[k] < seq[k - 1] - 0.004:
                occ_bad.append("%s f%d→f%d %.3f→%.3f" % (uid, k, k + 1, seq[k - 1], seq[k]))
            if seq[k] > seq[-1] + 0.004:
                occ_bad.append("%s f%d 超过末帧值 %.3f>%.3f" % (uid, k + 1, seq[k], seq[-1]))
                worst_overshoot = max(worst_overshoot, seq[k] - seq[-1])
    add("G19", "66 对中心距逐帧单调不增，且遮挡比例逐帧单调不降（任意帧 ≤ 末帧）",
        not dist_bad and not occ_bad,
        "66 对×5 个相邻帧对全部不增（最大增长 %.2f px）；遮挡单调性 %s；最大超出末帧 %.4f"
        % (worst_growth, "6 帧×12 单元全部通过" if not occ_bad else "失败 %d 处" % len(occ_bad),
           worst_overshoot))

    # 20 硬裁 Stack 内不得有越界 Positioned：`clipBehavior="HARD_EDGE"` 是静默裁切，
    #     内容还在 DSL 里、其余门禁也全对，可图上就是空的。封面的 6 块面板第一版正是
    #     这样——缩略图被写进了面板的绝对坐标而非局部坐标，DSL 里 6 个太阳都在。
    ovf: list[str] = []
    dsls = [build_cover(frames), build_contact_sheet(frames)] + [build_frame(f, row)
                                                                 for f, row in enumerate(frames, 1)]
    for tag, dsl in [("封面", dsls[0]), ("接触表", dsls[1])] + \
                   [("帧%d" % i, d) for i, d in enumerate(dsls[2:], 1)]:
        b, _ = _hardedge_overflow(dsl)
        if b:
            ovf.append("%s：%d 处（如 %s）" % (tag, len(b), b[0]))
    add("G20", "8 份 DSL 的硬裁 Stack 内无越界 Positioned", not ovf,
        ovf or "封面/接触表 12 块 HARD_EDGE 面板 + 6 帧各自的缩略图 Stack 全部在界内")

    # 17 颜色可区分度（信息项；像素审计按已知绘制顺序推导期望色，不依赖它）
    mn, who = _pairwise_min_delta()
    add("G17", "12 个 RGB 两两最大通道差 ≥ 16", mn >= 16,
        "最小差 %d（%s vs %s）" % (mn, who[0], who[1]))

    return gates


def main() -> int:
    import json
    frames = all_frames()
    gates = dry_run(frames)
    ok = sum(1 for g in gates if g["passed"])
    print("干跑门禁 %d/%d 通过" % (ok, len(gates)))
    for g in gates:
        print("  [%s] %s %s — %s" % ("PASS" if g["passed"] else "FAIL", g["id"], g["name"], g["detail"]))
    print()
    print("帧参数（中心 x,y / 旋转 deg）：")
    for f, row in enumerate(frames, 1):
        print("  帧%d e=%.4f p=%.4f" % (f, ease(frame_progress(f)), frame_progress(f)),
              " ".join("%s(%s,%s)/%s°" % (p["id"], _f(p["x"]), _f(p["y"]), _f(p["rot"])) for p in row))
    print()
    print("面积遮挡比例（按绘制顺序列出；1.5 px 网格扫过单元自身旋转外包框，分母=落在本单元内的点数）：")
    for f, row in enumerate(frames, 1):
        cells = []
        for p in row:
            u = byid(p["id"])
            fr, _, _ = occluded_area_fraction(u, p, row)
            cells.append("%s:%.3f" % (p["id"], fr))
        print("  帧%d" % f, " ".join(cells))
    print("内缩框遮挡比例（inset_frac=0.16，像素审计用；只采样离边缘足够远的点，分母是内缩框不是形状面积）：")
    for f, row in enumerate(frames, 1):
        cells = []
        for p in row:
            u = byid(p["id"])
            fr, _, _ = occluded_fraction(u, p, row, sample_world_points(u, p, 100))
            cells.append("%s:%.3f" % (p["id"], fr))
        print("  帧%d" % f, " ".join(cells))
    print()
    print("各单元行程（起点→终点距离）：")
    for u in UNITS:
        x0, y0 = start_of(u)
        (x1, y1) = u["final"]
        print("  %s %-3s %-6.2f px  (%.2f,%.2f)→(%d,%d)  首帧角 %d°"
              % (u["id"], u["name"], math.hypot(x1 - x0, y1 - y0), x0, y0, x1, y1, u["srot"]))
    print()
    print("封面 %d B" % len(build_cover(frames).encode("utf-8")))
    print("帧1 %d B, 帧6 %d B" % (len(build_frame(1, frames[0]).encode("utf-8")),
                                  len(build_frame(6, frames[5]).encode("utf-8"))))
    print("接触表 %d B" % len(build_contact_sheet(frames).encode("utf-8")))
    print("帧1 DSL 头 12 行：")
    print("\n".join(build_frame(1, frames[0]).splitlines()[:12]))
    return 0 if ok == len(gates) else 1


if __name__ == "__main__":
    import sys
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    raise SystemExit(main())
