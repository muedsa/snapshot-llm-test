"""A18 守恒对象三幕视觉叙事 — 几何与 DSL 构建模块。

守恒对象：15 个信息单元（5 蓝 / 5 橙 / 5 灰，直径 36）+ 3 个处理节点（基准 112x112）。
三幕：集中 → 过载 → 重新分配。全部几何由本模块计算，DSL 由程序生成。
"""
from __future__ import annotations
import math

# ---------- 调色 ----------
BG = "#FFFFFF"
INK = "#0F172A"
MUTED = "#475569"
SEP = "#E8EDF3"
NODE_ACTIVE = "#0F172A"
NODE_GLYPH_ACTIVE = "#FFFFFF"
NODE_IDLE = "#F1F5F9"
NODE_GLYPH_IDLE = "#0F172A"
LINE_C = "#8A97A8"
U_BLUE = "#2563EB"
U_ORANGE = "#EA580C"
U_GRAY = "#94A3B8"

# ---------- 守恒常量 ----------
UNIT_D = 36
UNIT_R = UNIT_D / 2
NODE_SIZE = 112          # 三节点基准尺寸（外包框边长）
NODE_HALF = NODE_SIZE / 2
NODE_RADIUS = 14
GLYPH = 44               # 标识字形基准尺寸

# 15 个单元的固定身份：U01-U05 蓝，U06-U10 橙，U11-U15 灰（三幕完全一致）
UNIT_COLORS = {}
for _i in range(1, 16):
    UNIT_COLORS[f"U{_i:02d}"] = U_BLUE if _i <= 5 else (U_ORANGE if _i <= 10 else U_GRAY)
UNIT_COLOR_NAME = {U_BLUE: "blue", U_ORANGE: "orange", U_GRAY: "gray"}

NODE_IDS = ["N01", "N02", "N03"]


# ---------- 基础几何 ----------
def dist_point_rect(px: float, py: float, x0: float, y0: float, x1: float, y1: float) -> float:
    """点到轴对齐矩形的距离（内部为 0）。"""
    dx = max(x0 - px, px - x1, 0.0)
    dy = max(y0 - py, py - y1, 0.0)
    return math.hypot(dx, dy)


def ray_rect_t(cx: float, cy: float, hx: float, hy: float, ux: float, uy: float) -> float:
    """从矩形中心沿单位方向 (ux,uy) 到矩形边界的距离。"""
    cands = []
    if abs(ux) > 1e-9:
        cands.append(hx / abs(ux))
    if abs(uy) > 1e-9:
        cands.append(hy / abs(uy))
    return min(cands) if cands else 0.0


# ---------- DSL 构件 ----------
def circle(cx: float, cy: float, d: float, color: str) -> str:
    return (f'<Positioned left="{cx - d / 2:.2f}" top="{cy - d / 2:.2f}" width="{d}" height="{d}">'
            f'<Container width="{d}" height="{d}" color="{color}" shape="CIRCLE"/></Positioned>')


def rrect(x: float, y: float, w: float, h: float, color: str, r: float,
          border: str | None = None) -> str:
    bd = f' border="{border}"' if border else ""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container width="{w:.2f}" height="{h:.2f}" color="{color}" borderRadius="{r}"{bd}/>'
            f'</Positioned>')


def _glyph(kind: str, color: str, size: int = GLYPH) -> str:
    """节点内部标识字形：N01 实心圆 / N02 圆角方 / N03 菱形（45° 旋转方）。
    三幕之间只换颜色，不换形状 —— 身份由形状承载。"""
    if kind == "N01":
        return (f'<Container width="{size}" height="{size}" color="{color}" shape="CIRCLE"/>')
    if kind == "N02":
        return (f'<Container width="{size}" height="{size}" color="{color}" '
                f'borderRadius="10"/>')
    # N03：菱形 = 32x32 方绕中心旋转 45°
    s = int(round(size * 32 / 44))
    m = "(0.707107,0.707107,0,0,-0.707107,0.707107,0,0,0,0,1,0,0,0,0,1)"
    box = int(round(size * 1.10))
    off = (box - s) / 2
    return (f'<Container width="{box}" height="{box}" color="transparent" alignment="CENTER">'
            f'<Transform matrix="{m}" alignment="CENTER">'
            f'<Container width="{s}" height="{s}" color="{color}"/></Transform></Container>')


def node(cx: float, cy: float, kind: str, w: float = NODE_SIZE, h: float = NODE_SIZE,
         active: bool = True) -> str:
    """处理节点：外包框 + 标识字形。active 只改填充状态，不改形状与尺寸基准。"""
    fill = NODE_ACTIVE if active else NODE_IDLE
    glyph_c = NODE_GLYPH_ACTIVE if active else NODE_GLYPH_IDLE
    x, y = cx - w / 2, cy - h / 2
    border = None if active else f"2 SOLID {NODE_ACTIVE}"
    out = [rrect(x, y, w, h, fill, NODE_RADIUS, border)]
    g = _glyph(kind, glyph_c)
    gw = GLYPH if kind != "N03" else int(round(GLYPH * 1.10))
    out.append(f'<Positioned left="{cx - gw / 2:.2f}" top="{cy - gh_h(kind) / 2:.2f}" '
               f'width="{gw}" height="{gh_h(kind)}">'
               f'<Container width="{gw}" height="{gh_h(kind)}" color="transparent" '
               f'alignment="CENTER">{g}</Container></Positioned>')
    return "".join(out)


def gh_h(kind: str) -> int:
    return GLYPH if kind != "N03" else int(round(GLYPH * 1.10))


def line_seg(x1: float, y1: float, x2: float, y2: float, w: float = 3,
             color: str = LINE_C) -> str:
    """任意角度线段：薄 Container + Transform 旋转矩阵（列主序 4x4）。"""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return ""
    ux, uy = dx / L, dy / L
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    m = f"({ux:.6f},{uy:.6f},0,0,{-uy:.6f},{ux:.6f},0,0,0,0,1,0,0,0,0,1)"
    return (f'<Positioned left="{mx - L / 2:.2f}" top="{my - w / 2:.2f}" '
            f'width="{L:.2f}" height="{w}">'
            f'<Transform matrix="{m}" alignment="CENTER">'
            f'<Container width="{L:.2f}" height="{w}" color="{color}"/></Transform>'
            f'</Positioned>')


def connector(ucx: float, ucy: float, ncx: float, ncy: float, nhx: float, nhy: float,
              inset: float = 1.5, w: float = 3) -> tuple[str, dict]:
    """单元 → 节点 的连线：从单元圆界外 inset 处起，到矩形节点边界外 inset 处止，
    保证线不遮圆、不遮节点。返回 (DSL, 几何记录)。"""
    dx, dy = ncx - ucx, ncy - ucy
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    sx, sy = ucx + ux * (UNIT_R + inset), ucy + uy * (UNIT_R + inset)
    t = ray_rect_t(ncx, ncy, nhx, nhy, -ux, -uy)
    ex, ey = ncx - ux * (t + inset), ncy - uy * (t + inset)
    rec = {"from": [round(sx, 2), round(sy, 2)], "to": [round(ex, 2), round(ey, 2)],
           "length": round(math.hypot(ex - sx, ey - sy), 2)}
    return line_seg(sx, sy, ex, ey, w), rec


def text_node(s: str, cx: float, y: float, w: float, size: int, bold: bool = True,
              color: str = INK, align: str = "CENTER", h: int | None = None) -> str:
    hh = h if h else int(size * 1.5)
    st = "BOLD" if bold else "NORMAL"
    fam = "Noto Sans CJK SC"
    return (f'<Positioned left="{cx - w / 2:.2f}" top="{y:.2f}" width="{w:.2f}" height="{hh}">'
            f'<Container color="transparent" alignment="TOP_LEFT">'
            f'<Text fontSize="{size}" fontFamily="{fam}" fontStyle="{st}" color="{color}" '
            f'textAlign="{align}" softWrap="false" maxLines="1">{s}</Text>'
            f'</Container></Positioned>')


def snapshot(nodes: list[str], w: int = 1600, h: int = 1000) -> str:
    return (f'<Snapshot type="png" background="{BG}">'
            f'<Container width="{w}" height="{h}">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
            + "".join(nodes) + "</Stack></Container></Snapshot>")


# ---------- 环形布点 ----------
def ring(n: int, r: float, cx: float, cy: float, phase: float = 0.0) -> list[tuple[float, float]]:
    """n 个点均匀分布在半径 r 的圆上，返回 [(x,y), ...]。"""
    step = 360.0 / n
    return [(cx + r * math.cos(math.radians(phase + i * step)),
             cy + r * math.sin(math.radians(phase + i * step))) for i in range(n)]


def pentagon(r: float, cx: float, cy: float, phase: float = 18.0) -> list[tuple[float, float]]:
    """5 个点均匀分布在半径 r 的圆上（与 ring 同公式，n=5）。"""
    return ring(5, r, cx, cy, phase=phase)
