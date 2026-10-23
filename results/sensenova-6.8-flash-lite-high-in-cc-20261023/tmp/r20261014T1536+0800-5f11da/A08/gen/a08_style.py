"""A08 导览图绘制原语（复用 A07 实测确认的标签契约）。

关键契约（均来自本套已完成的探针与 A01/A07 成品，见 tmp/<rid>/A07/gen/a07_probe*.py）：
  * ClipPath 只裁剪不描边，但子节点是带 color 的 <Container> 时会把路径**区域**涂满，
    故三角形箭头、精确多边形带都用 ClipPath 实现；
  * ClipPath 必须嵌在 <Container> 内，直接挂在 <Positioned> 下会静默不填充；
  * 路径坐标在 viewBox 空间内，viewBox 与盒尺寸取同一值即可 1:1 对齐（A01 实测）；
  * border="2 SOLID #E2E8F0"；boolean 属性必须显式字符串；
  * Stack 后画者在上，绘制顺序由组装顺序决定。

本文件只做"画什么"，不含路网数据；几何换算在 a08_build.py。
"""

from __future__ import annotations

import math

CW, CH = 1560.0, 1080.0        # 画布尺寸（题面指定）
FONT = "Noto Sans CJK SC"       # /fonts 实际可用；能渲染 CJK 与 ①②→＝ 等符号

# ---- 调色板（浅底高对比；两条路线的颜色与线型双编码）----
PAGE = "#EEF2F7"                # 画布底
CARD = "#FFFFFF"                # 面板白
WALL = "#D5DDE8"                # 阻挡区（墙体）
WALL_DEEP = "#C2CCDB"           # 阻挡区外框
AISLE = "#FFFFFF"               # 通道
GLINE = "#C6D0DE"               # 格线（仅落在通道上的浅线）
INK = "#0F172A"                 # 正文
INK2 = "#475569"                # 次要文字
INK3 = "#64748B"                # 说明文字
R1 = "#1D4ED8"                  # 路线1 直达出口（蓝 · 实线）
R1_PALE = "#DBEAFE"             # 路线1 淡底
R2 = "#E8590C"                  # 路线2 主题参观（橙 · 虚线）
R2_PALE = "#FFEDD5"             # 路线2 淡底
S_C = "#0F766E"                 # S 入口门格
E_C = "#BE123C"                 # E 出口门格
LM = "#7C3AED"                  # A–D 展区入口点
BADGE = "#334155"               # 共享通道编号章
NOTEBG = "#F8FAFC"              # 底注浅底
NOTEEDGE = "#CBD5E1"            # 底注描边
DOOR = "#94A3B8"                # 门洞切口提示


def n(v: float) -> str:
    """坐标/尺寸格式化：去尾零，不用科学计数法。"""
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s else "0"


def esc(s: str) -> str:
    """XML 文本/属性转义。"""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def tw(s: str, size: float) -> float:
    """文本宽度估算：CJK≈1.0em，拉丁≈0.56em，空格≈0.30em（排版预算用，最终以看图核验）。"""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o < 0x2000:
            w += 0.30 if ch == " " else (0.30 if ch in ",.:;!|'\"()" else 0.56)
        elif ch in "①②③④⑤⑥⑦⑧⑨":
            w += 1.0
        else:
            w += 1.02
    return w * size


def TH(size: float) -> float:
    """单行文本盒高度（留字形上下余量）。"""
    return size * 1.45


# ---- 画布骨架 ----

def canvas_open() -> str:
    return (f'<Snapshot type="png" background="{PAGE}">'
            f'<Container width="{n(CW)}" height="{n(CH)}">')


def canvas_close() -> str:
    return "</Container></Snapshot>"


# ---- 定位与形状 ----

def stack(*layers) -> str:
    return f'<Stack fit="EXPAND" clipBehavior="NONE">{"".join(layers)}</Stack>'


def box(px, py, w, h, color, radius=0.0, border=None) -> str:
    """绝对定位圆角矩形（含可选边框）。"""
    r = f' borderRadius="{n(radius)}"' if radius else ""
    b = f' border="{border}"' if border else ""
    return (f'<Positioned left="{n(px)}" top="{n(py)}" width="{n(w)}" '
            f'height="{n(h)}"><Container width="{n(w)}" height="{n(h)}" '
            f'color="{color}"{r}{b}></Container></Positioned>')


def layer_box(px, py, w, h, *layers, border=None) -> str:
    """把若干 ClipPath 图层放进一个定位盒（用于一次画整张网格）。"""
    b = f' border="{border}"' if border else ""
    return (f'<Positioned left="{n(px)}" top="{n(py)}" width="{n(w)}" '
            f'height="{n(h)}"><Container width="{n(w)}" height="{n(h)}"{b}>'
            f'<Stack fit="EXPAND" clipBehavior="NONE">{"".join(layers)}</Stack>'
            f'</Container></Positioned>')


def path_group(d: str, color: str) -> str:
    """整幅画布坐标空间内填充一条路径（viewBox = 画布尺寸，1:1 映射）。"""
    return (f'<ClipPath path="{d}" viewBox="0 0 {n(CW)} {n(CH)}" fit="FILL">'
            f'<Container width="{n(CW)}" height="{n(CH)}" color="{color}">'
            f'</Container></ClipPath>')


def line_h(x1, x2, y, w, color) -> str:
    return box(x1, y - w / 2, x2 - x1, w, color, radius=0)


def line_v(x, y1, y2, w, color) -> str:
    return box(x - w / 2, y1, w, y2 - y1, color, radius=0)


def poly(pts, color) -> str:
    """任意多边形（三角箭头、门洞切口等）。"""
    d = "M" + " L".join(f"{n(x)} {n(y)}" for x, y in pts) + " Z"
    return path_group(d, color)


def circle(cx, cy, r, color, border=None) -> str:
    """整圆标记。"""
    b = f' border="{border}"' if border else ""
    return (f'<Positioned left="{n(cx - r)}" top="{n(cy - r)}" width="{n(2 * r)}" '
            f'height="{n(2 * r)}"><Container width="{n(2 * r)}" height="{n(2 * r)}" '
            f'color="{color}" borderRadius="{n(r)}"{b}></Container></Positioned>')


# ---- 文本 ----

def txt(px, py, s, size=22, color=INK, bold=False) -> str:
    """左上角锚定的文本。"""
    st = ' fontStyle="BOLD"' if bold else ""
    return (f'<Positioned left="{n(px)}" top="{n(py)}" width="{n(CW)}" '
            f'height="{n(TH(size))}"><Container width="{n(CW)}" height="{n(TH(size))}">'
            f'<Text text="{esc(s)}" fontSize="{n(size)}"{st} color="{color}" '
            f'fontFamily="{FONT}"></Text></Container></Positioned>')


def txt_c(cx, cy, s, size=22, color=INK, bold=False) -> str:
    """几何中心锚定的文本（盒比字形大一圈，避免粗体字身被裁）。"""
    w = tw(s, size) + size * 0.9
    h = TH(size)
    return _box_text(cx - w / 2, cy - h / 2, w, h, s, size, color, bold, "CENTER")


def txt_r(px_right, cy, s, size=22, color=INK, bold=False) -> str:
    """右端对齐的文本（用于把刻度贴到网格左边）。"""
    w = tw(s, size) + size * 0.5
    return _box_text(px_right - w, cy - TH(size) / 2, w, TH(size),
                     s, size, color, bold, "CENTER_RIGHT")


def _box_text(px, py, w, h, s, size, color, bold, align) -> str:
    st = ' fontStyle="BOLD"' if bold else ""
    return (f'<Positioned left="{n(px)}" top="{n(py)}" width="{n(w)}" '
            f'height="{n(h)}"><Container width="{n(w)}" height="{n(h)}" '
            f'alignment="{align}"><Text text="{esc(s)}" fontSize="{n(size)}"{st} '
            f'color="{color}" fontFamily="{FONT}"></Text></Container></Positioned>')


def pill(left, top, s, size=22, fg="#FFFFFF", bg=LM, pad_x=14, pad_y=9) -> str:
    """胶囊标签：底色 + 居中白字。返回 (片段, 宽, 高)。"""
    w = tw(s, size) + pad_x * 2
    h = size * 1.35 + pad_y * 2
    return (box(left, top, w, h, bg, radius=h / 2)
            + _box_text(left, top, w, h, s, size, fg, True, "CENTER"), w, h)
