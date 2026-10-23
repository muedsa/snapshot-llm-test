"""A10 六格实验板的共享 DSL 构件。

关键约束：③④ 与 ⑤⑥ 两对必须复用**同一份**基础场景（条纹颜色/宽度/间距/相位、
卡片底色/位置/文字/前景形状/绘制层次、以及 ⑤⑥ 的颜色/位置/阴影/滤镜参数），
仅改变「效果作用的层」。所以本模块把场景参数集中成常量，各格的差异只在最外层包住
哪个滤镜，绝不各写一份近似场景。

局部坐标：每个 320×240 实验区左上外边界为原点，x 向右、y 向下，单位 px。

--- 实测得到的 DSL 契约（都由渲染响应验证，不是文档写法）---

1. **8 位色是 #RRGGBBAA，不是 #AARRGGBB。** 诊断渲染实测：
   - `#B3FFFFFF` → 解码像素 (179,255,255,255)，即 R=0xB3、G=0xFF、B=0xFF、A=0xFF，
     是不透明的亮青色，完全盖住背后的模糊，让 ③ 看起来像一块纯色卡；
   - `#FFFFFFB3` → 深条处 (188,191,196)，与 0.70196×255 + 0.298×(30,41,59)
     = (187.9,191.2,196.6) 吻合，是真正的「白 70%」。
   ① 用 `#FF000080`/`#0000FF80` 恰好是 α 在后，所以那部分一直是对的。
   凡需要半透明的地方，本文件一律把 α 写在**最后一位**。
2. `ClipOval` 的直接子节点必须是 `Stack`（不能是 `Positioned`）。
3. `Positioned` 只能有一个子节点。
4. 平移模糊子树会改变 `ImageFiltered` 的输出边界与 `tileMode="CLAMP"` 取样，
   所以 ⑥ 是「原样子树放进偏移盒，再由 ClipOval 裁圆」，绝不平移场景本体。
"""

from __future__ import annotations

FONT = "Noto Sans CJK SC"
INK = "#0F172A"
INK2 = "#475569"
INK3 = "#64748B"
AREABG = "#FFFFFF"
AREAEDGE = "#CBD5E1"

AREA_W = 320.0
AREA_H = 240.0

# ---- ①② 用的两个矩形（局部坐标，蓝在上层）----
RECT_RED = {"x": 40.0, "y": 40.0, "w": 160.0, "h": 120.0}
RECT_BLUE = {"x": 120.0, "y": 80.0, "w": 160.0, "h": 120.0}
RED_50 = "#FF000080"      # ① 各矩形 50% alpha（128/255）
BLUE_50 = "#0000FF80"
RED_OPAQUE = "#FF0000"    # ② 组内不透明
BLUE_OPAQUE = "#0000FF"
GROUP_OPACITY = "0.5"
SAMPLE = (180.0, 100.0)   # 重叠内部采样点（局部）

# ---- ③④ 共享基础场景：条纹 + 圆角卡 ----
STRIPE = {"dark": "#1E293B", "light": "#FFFFFF", "bar": 14.0, "gap": 10.0}
STRIPE_PERIOD = STRIPE["bar"] + STRIPE["gap"]        # 24
CARD = {"x": 40.0, "y": 40.0, "w": 240.0, "h": 160.0, "r": 20.0,
        # 白 50%（α 在末位）：太不透明会把背面的模糊完全盖住，看不出「背景被模糊」；
        # 实测 σ=6 模糊把条纹对比压到约 39%，罩 50% 后卡内对比仍剩约 43，
        # 卡外保持 225——差异足够明显。深墨字在此罩上对比比约 9:1，仍可读。
        "fill": "#FFFFFF80", "text": "SHARP / BLUR", "size": 24.0,
        "text_color": "#0F172A"}
# 卡内前景形状（区域局部坐标）
CARD_FG = [
    {"xywh": [60.0, 116.0, 72.0, 44.0], "color": "#1E293B", "radius": 8.0},
    {"cx": 218.0, "cy": 138.0, "r": 18.0, "color": "#B91C1C"},
]
BLUR_SIGMA = "6"

# ---- ⑤⑥ 共享基础场景：深色矩形 + 透明间隙 + 阴影，MULTIPLY #F6B94A ----
FILTER_COLOR = "#F6B94A"
BLEND = "MULTIPLY"
SCENE56 = [
    {"xywh": [28.0, 40.0, 116.0, 160.0], "color": "#1E293B",
     "shadow": "0 6 10 0 #00000066 NORMAL"},
    {"xywh": [180.0, 28.0, 112.0, 84.0], "color": "#0F172A", "radius": 10.0},
    {"xywh": [150.0, 148.0, 140.0, 64.0], "color": "#334155B3"},
    {"xywh": [196.0, 168.0, 84.0, 32.0], "color": "#F8FAFC", "radius": 6.0},
]
CIRC = {"cx": 160.0, "cy": 120.0, "r": 100.0}


def n(v: float) -> str:
    """坐标/尺寸格式化：去尾零、不用科学计数法。"""
    s = f"{float(v):.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def esc(s: str) -> str:
    # DSL 渲染器不解码 HTML 实体：文本里不得出现 < > &
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pos(x, y, w, h, inner) -> str:
    return ('<Positioned left="' + n(x) + '" top="' + n(y) + '" width="' + n(w)
            + '" height="' + n(h) + '">' + inner + "</Positioned>")


def container(w, h, color=None, radius=0.0, border=None, align=None,
              shadow=None, inner="") -> str:
    s = '<Container width="' + n(w) + '" height="' + n(h) + '"'
    if color:
        s += ' color="' + color + '"'
    if radius:
        s += ' borderRadius="' + n(radius) + '"'
    if border:
        s += ' border="' + border + '"'
    if align:
        s += ' alignment="' + align + '"'
    if shadow:
        s += ' boxShadow="' + shadow + '"'
    if inner:
        return s + ">" + inner + "</Container>"
    return s + "></Container>"


def rect(x, y, w, h, color, radius=0.0, shadow=None) -> str:
    return pos(x, y, w, h, container(w, h, color=color, radius=radius, shadow=shadow))


def stack(*layers, w=None, h=None) -> str:
    s = "<Stack"
    if w is not None:
        s += ' width="' + n(w) + '" height="' + n(h) + '"'
    s += ' fit="EXPAND" clipBehavior="NONE">' + "".join(layers) + "</Stack>"
    return s


def hline(x1, x2, y, th, color) -> str:
    return rect(x1, y - th / 2.0, x2 - x1, th, color)


def vline(x, y1, y2, th, color) -> str:
    return rect(x - th / 2.0, y1, th, y2 - y1, color)


def area(x, y, *layers, border=True) -> str:
    """一个 320×240 实验区：白底 + 边框 + 内容层。局部坐标原点即区域左上外边界。"""
    bg = container(AREA_W, AREA_H, color=AREABG,
                   border=("1 SOLID " + AREAEDGE) if border else None)
    return pos(x, y, AREA_W, AREA_H, stack(bg, *layers, w=AREA_W, h=AREA_H))


def txt(x, y, w, h, s, size, color=INK, bold=True, align="CENTER_LEFT") -> str:
    b = ' fontStyle="BOLD"' if bold else ""
    t = ('<Text fontFamily="' + FONT + '" fontSize="' + n(size) + '"' + b
         + ' color="' + color + '">' + esc(s) + "</Text>")
    return pos(x, y, w, h, container(w, h, align=align, inner=t))


# ---------------------------------------------------------------- ① ②

def sample_marker() -> str:
    """采样点 (180,100) 的标记：只在距中心 14 px 处画四段短刻线。

    不能用十字或环线穿过中心——那会把采样点本身盖成标记色（第一次探针就是这样
    把 ①② 都采成了 #64748B 标记色）。四段刻线离中心最近的像素也在 14 px 之外。
    """
    cx, cy = SAMPLE
    t, o = 2.0, 14.0          # 刻线厚度、离中心的偏移
    return (rect(cx - 8.0, cy - o - t, 16.0, t, INK3)      # 上
            + rect(cx - 8.0, cy + o, 16.0, t, INK3)        # 下
            + rect(cx - o - t, cy - 8.0, t, 16.0, INK3)    # 左
            + rect(cx + o, cy - 8.0, t, 16.0, INK3))       # 右


def cell_alpha_layers() -> str:
    """① 两个矩形各自 50% alpha，直接叠在白底上，蓝在上层。"""
    return (rect(RECT_RED["x"], RECT_RED["y"], RECT_RED["w"], RECT_RED["h"], RED_50)
            + rect(RECT_BLUE["x"], RECT_BLUE["y"], RECT_BLUE["w"], RECT_BLUE["h"], BLUE_50)
            + sample_marker())


def cell_group_layers() -> str:
    """② 红蓝不透明，先在同一子树内合成，再由 Opacity 对整个子树施加 0.5。"""
    inner = stack(rect(RECT_RED["x"], RECT_RED["y"], RECT_RED["w"], RECT_RED["h"],
                       RED_OPAQUE),
                  rect(RECT_BLUE["x"], RECT_BLUE["y"], RECT_BLUE["w"], RECT_BLUE["h"],
                       BLUE_OPAQUE),
                  w=AREA_W, h=AREA_H)
    return ('<Opacity opacity="' + GROUP_OPACITY + '">' + inner + "</Opacity>"
            + sample_marker())


# ---------------------------------------------------------------- ③ ④

def stripes(x0: float, y0: float, w: float, h: float) -> str:
    """竖条纹：从 x0 起每隔 PERIOD 画一条 bar 宽的深色条。

    x0 决定相位。④ 在卡片局部坐标系里用 x0=-40 重画同一份条纹，
    从而与区域坐标系的相位完全一致（不能从 0 重新起算）。
    """
    out = []
    x = x0
    while x < x0 + w:
        bx = max(x, x0)
        bw = min(x + STRIPE["bar"], x0 + w) - bx
        if bw > 0.01:
            out.append(rect(bx, y0, bw, h, STRIPE["dark"]))
        x += STRIPE_PERIOD
    return "".join(out)


def card_text(x0: float, y0: float, w: float, h: float) -> str:
    return txt(x0 + CARD["x"] - x0, y0 + CARD["y"] + 14.0 - y0, CARD["w"] - 24.0, 34.0,
               CARD["text"], CARD["size"], color=CARD["text_color"], align="CENTER")


def card_text_local() -> str:
    """卡片局部坐标系（0,0 为卡片左上）内的文字。"""
    return txt(12.0, 14.0, CARD["w"] - 24.0, 34.0, CARD["text"], CARD["size"],
               color=CARD["text_color"], align="CENTER")


def card_fill_local() -> str:
    return container(CARD["w"], CARD["h"], color=CARD["fill"], radius=CARD["r"])


def card_fg_local() -> str:
    out = []
    for f in CARD_FG:
        if "xywh" in f:
            x, y, w, h = f["xywh"]
            out.append(rect(x - CARD["x"], y - CARD["y"], w, h, f["color"],
                            radius=f.get("radius", 0.0)))
        else:
            cx, cy, r = f["cx"] - CARD["x"], f["cy"] - CARD["y"], f["r"]
            out.append(rect(cx - r, cy - r, 2 * r, 2 * r, f["color"], radius=r))
    return "".join(out)


def card_scene_local() -> str:
    """卡片范围内的完整基础场景（白底 + 条纹 + 卡底 + 文字 + 前景），卡片局部坐标。

    ④ 直接把这整棵子树一起模糊；③ 只把它之外的背景单独模糊。

    两处必须与 ③ 的背面背景一致，否则「同一份基础场景」不成立：
    1. 白底。③ 被模糊的背面是「白底 + 条纹」不透明画面；若 ④ 的子树只有条纹、
       底层透明，模糊时透明像素会以 0 参与混合，同一位置算出的底色就不同
      （实测局部 (200,100) 反推：③ 的模糊底约 80，④ 只有 32）。
    2. 条纹宽度按整个实验区取。卡片在区域局部 (40,40)，卡片局部 x=0 对应区域 x=40，
       而区域条纹从 x=0 起算，所以卡片局部要画 -40..280（即区域 0..320）才能与
       ③ 的背景条纹同相位、同覆盖范围。只画 -40..200 的话卡片右侧 40 px 没有条纹。
    stack 用 HARD_EDGE 裁掉超出卡片的绘制，避免溢出到卡片之外。
    """
    return ('<Stack width="' + n(CARD["w"]) + '" height="' + n(CARD["h"])
            + '" fit="EXPAND" clipBehavior="HARD_EDGE">'
            + rect(-CARD["x"], 0.0, AREA_W, CARD["h"], "#FFFFFF")
            + stripes(-CARD["x"], 0.0, AREA_W, CARD["h"])
            + card_fill_local() + card_text_local() + card_fg_local()
            + "</Stack>")


def cell_backdrop_layers() -> str:
    """③ 仅卡片覆盖处的背景（条纹）用 BackdropFilter 模糊，卡内文字与前景保持清晰。"""
    blurred = ('<ClipRRect borderRadius="' + n(CARD["r"]) + '" clipBehavior="ANTI_ALIAS">'
               + "<BackdropFilter sigmaX=\"" + BLUR_SIGMA + '" sigmaY="' + BLUR_SIGMA
               + '" tileMode="CLAMP">'
               + container(CARD["w"], CARD["h"])
               + "</BackdropFilter></ClipRRect>")
    card = pos(CARD["x"], CARD["y"], CARD["w"], CARD["h"],
               stack(blurred, card_fill_local(), card_text_local(), card_fg_local(),
                     w=CARD["w"], h=CARD["h"]))
    return stripes(0.0, 0.0, AREA_W, AREA_H) + card


def cell_subtree_layers() -> str:
    """④ 同一份基础场景（条纹 + 卡底 + 文字 + 前景）整体做子树高斯模糊。"""
    blurred = ('<ClipRRect borderRadius="' + n(CARD["r"]) + '" clipBehavior="ANTI_ALIAS">'
               + '<ImageFiltered sigmaX="' + BLUR_SIGMA + '" sigmaY="' + BLUR_SIGMA
               + '" tileMode="CLAMP">' + card_scene_local() + "</ImageFiltered>"
               + "</ClipRRect>")
    card = pos(CARD["x"], CARD["y"], CARD["w"], CARD["h"],
               stack(blurred, w=CARD["w"], h=CARD["h"]))
    return stripes(0.0, 0.0, AREA_W, AREA_H) + card


# ---------------------------------------------------------------- ⑤ ⑥

def scene56_local() -> str:
    """⑤⑥ 共享基础场景（320×240，区域局部坐标）。"""
    out = []
    for s in SCENE56:
        x, y, w, h = s["xywh"]
        out.append(rect(x, y, w, h, s["color"], radius=s.get("radius", 0.0),
                        shadow=s.get("shadow")))
    return stack(*out, w=AREA_W, h=AREA_H)


def multiply_then_blur() -> str:
    """先 ColorFiltered(MULTIPLY #F6B94A)，再对结果做 sigma=6 子树高斯模糊。

    内层先施加、外层后施加：ColorFiltered 在内、ImageFiltered 在外。
    ⑤⑥ 都调用同一个函数、传同一份场景，保证两格在裁剪之前的结果逐像素相同。
    """
    return ('<ImageFiltered sigmaX="' + BLUR_SIGMA + '" sigmaY="' + BLUR_SIGMA
            + '" tileMode="CLAMP">'
            + '<ColorFiltered color="' + FILTER_COLOR + '" blendMode="' + BLEND + '">'
            + scene56_local() + "</ColorFiltered></ImageFiltered>")


def cell_multiply_layers() -> str:
    """⑤ MULTIPLY 后模糊，无额外裁剪。"""
    return pos(0.0, 0.0, AREA_W, AREA_H, multiply_then_blur())


def cell_clipped_layers() -> str:
    """⑥ 与 ⑤ 完全同样的结果，最外层再加圆形裁剪（圆心局部 (160,120)、半径 100）。

    两处实测契约：
    1. ClipOval 的直接子节点必须是 Stack，不能是 Positioned
       （否则 RENDER_ERROR: renderBox.parentData must be StackParentData）；
    2. 不能平移场景本体。把场景各矩形整体平移 (-60,-20) 会改变模糊子树的边界与
       CLAMP 取样，⑥ 就不再与 ⑤ 逐像素相同（实测局部 (230,70) 从 (15,17,13)
       变成 (107,84,37)）。正确做法是把原样的 320×240 子树放进
       Positioned(-60,-20)，再由 200×200 的 ClipOval 裁成内切圆。
    """
    bx = CIRC["cx"] - CIRC["r"]
    by = CIRC["cy"] - CIRC["r"]
    d = 2 * CIRC["r"]
    subtree = pos(-bx, -by, AREA_W, AREA_H, multiply_then_blur())
    return pos(bx, by, d, d,
               '<ClipOval clipBehavior="ANTI_ALIAS">'
               + stack(subtree, w=d, h=d) + "</ClipOval>")


# ---------------------------------------------------------------- 汇总

def all_areas(ox: float, oy: float, gap: float) -> str:
    """3 列 × 2 行布置六格。返回 DSL 片段（坐标为画布坐标）。"""
    cols, rows = 3, 2
    out = []
    builders = [cell_alpha_layers, cell_group_layers, cell_backdrop_layers,
                cell_subtree_layers, cell_multiply_layers, cell_clipped_layers]
    for i, build in enumerate(builders):
        ax = ox + (i % cols) * (AREA_W + gap)
        ay = oy + (i // cols) * (AREA_H + gap)
        out.append(area(ax, ay, build()))
    return "".join(out)


def area_origins(ox: float, oy: float, gap: float) -> list:
    cols = 3
    return [(int(ox + (i % cols) * (AREA_W + gap)),
             int(oy + (i // cols) * (AREA_H + gap))) for i in range(6)]
