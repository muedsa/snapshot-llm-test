"""A07 能力探针 1：地铁线路的 45°/90° 折线到底怎么画。

背景（A05 已量清，矩阵格式复核过）：
  * `<Transform matrix="(16 个逗号分隔浮点)">` 是文档规定的格式；A05 用的正是这个格式，
    2×2 部分非单位时（旋转/错切/缩放）整块子树静默不输出像素。
  * DSL 标签表里没有 Path / Line / Polyline。
  * `ClipPath` 文档只说"裁剪"，A05 因此推断它不能画线——但文档示例里 ClipPath 的唯一
    子节点是一个带颜色的 `<Container>`，也就是说 ClipPath 会把路径**填充区域**涂成
    子节点的颜色。若成立，一整条地铁线（含 45° 段）就是一个多轮廓路径，一个元素画完。
    这是本题架构的关键假设，必须先量出来。

测试格（每格一色，按像素统计判定谁真的画出来）：
  J  ClipPath 单条 45° 平行四边形 + 彩色 Container —— 是否填充？厚度与斜率？
  K  ClipPath 多轮廓：1 条水平 + 1 条竖直 + 1 条 45°，同一元素、同一颜色
  K2 ClipPath 模拟真实线路：水平-45°-水平 的折线，中间在"车站"处留缺口
  L  Transform 括号格式 45° 旋转（复核 A05 的静默失效结论）
  N  Container 直接写 transform / transformAlignment 属性
  G  实心圆 borderRadius = d/2（车站标记对照）
  H  圆环：白圆 + 内缩彩心（换乘站标记候选）
  D  45° 阶梯：小矩形沿对角步进（退路）
  E  45° 圆点串（退路）

用法：python -I tmp/<rid>/A07/gen/a07_probe1.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a07_io as IO  # noqa: E402

from PIL import Image  # noqa: E402

FA = 'fontFamily="Noto Sans CJK SC"'

C = {
    "J": "#DC2626",   # ClipPath 单条 45°
    "K": "#2563EB",   # ClipPath 多轮廓
    "K2": "#16A34A",  # ClipPath 折线含缺口
    "L": "#7C3AED",   # Transform 旋转复核
    "N": "#0891B2",   # Container transform 属性
    "G": "#DB2777",   # 实心圆
    "H": "#1D4ED8",   # 圆环
    "D": "#D97706",   # 阶梯
    "E": "#475569",   # 圆点串
}


def _n(v: float) -> str:
    """坐标格式：去掉无意义尾零，但不写科学计数法。"""
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def box(left, top, w, h, color, r=0, border=None) -> str:
    b = f' border="{border}"' if border else ""
    rr = f' borderRadius="{r}"' if r else ""
    return (f'<Positioned left="{_n(left)}" top="{_n(top)}" width="{_n(w)}" '
            f'height="{_n(h)}"><Container width="{_n(w)}" height="{_n(h)}" '
            f'color="{color}"{rr}{b}></Container></Positioned>')


def txt(left, top, s, size=18, color="#0F172A", bold=False) -> str:
    st = ' fontStyle="BOLD"' if bold else ""
    return (f'<Positioned left="{_n(left)}" top="{_n(top)}"><Text text="{s}" '
            f'fontSize="{size}"{st} color="{color}" {FA}></Text></Positioned>')


def clip(left, top, w, h, path, color, fit=None, fillrule=None) -> str:
    """Path A：ClipPath + 彩色 Container 子节点，看是否填充路径区域。"""
    f = f' fit="{fit}"' if fit else ""
    fr = f' fillRule="{fillrule}"' if fillrule else ""
    return (f'<Positioned left="{_n(left)}" top="{_n(top)}" width="{_n(w)}" '
            f'height="{_n(h)}"><ClipPath path="{path}" clipBehavior="ANTI_ALIAS"{f}{fr}>'
            f'<Container width="{_n(w)}" height="{_n(h)}" color="{color}">'
            f'</Container></ClipPath></Positioned>')


def seg_path(p1, p2, t=10.0) -> str:
    """把线段 P1→P2 变成宽度 t 的平行四边形 SVG 子路径（用于 45°/90°/0° 段）。"""
    import math
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dy)
    if L < 1e-9:
        return ""
    ux, uy = dx / L, dy / L
    px, py = -uy, ux          # 垂直方向
    h = t / 2.0
    a = (p1[0] + px * h, p1[1] + py * h)
    b = (p2[0] + px * h, p2[1] + py * h)
    c = (p2[0] - px * h, p2[1] - py * h)
    d = (p1[0] - px * h, p1[1] - py * h)
    return (f"M{_n(a[0])} {_n(a[1])} L{_n(b[0])} {_n(b[1])} "
            f"L{_n(c[0])} {_n(c[1])} L{_n(d[0])} {_n(d[1])} Z")


def sub(a, b, c) -> str:
    """三点的 90° 折线（a→b→c），拆成两条共享拐点的宽段拼一起。"""
    return seg_path(a, b) + " " + seg_path(b, c)


def main() -> None:
    try:  # python -I 下 PYTHONIOENCODING 无效，显式改回 UTF-8
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    W, H = 1000, 706
    L: list[str] = []
    add = L.append
    add('<Snapshot background="#F8FAFC" type="png">')
    add(f'<Container width="{W}" height="{H}" color="#F8FAFC">')
    add('<Stack fit="EXPAND" clipBehavior="NONE">')

    add(txt(24, 16, "A07 探针 1 · 45°/90° 折线的实现方式（每格一色）",
            size=24, bold=True))
    add(box(24, 54, 952, 1, "#E2E8F0"))

    cols, ox, oy, cw, ch = 3, 24, 64, 314, 204
    add(box(ox, oy, 952, 624, "#FFFFFF", 8, "1 SOLID #CBD5E1"))

    def cell(i: int) -> tuple[float, float]:
        r, c = divmod(i, cols)
        return ox + 8 + c * (cw + 5), oy + 8 + r * (ch + 5)

    def head(i: int, title: str) -> None:
        x, y = cell(i)
        add(box(x, y, cw, ch, "#FFFFFF", 6, "1 SOLID #EEF2F7"))
        add(txt(x + 10, y + 6, f"{title} {C.get(title.split()[0], '')}",
                size=17))

    # ---- J：ClipPath 单条 45° 平行四边形 ----
    head(0, "J ClipPath 单条 45°")
    x, y = cell(0)
    add(clip(x + 10, y + 40, 294, 118,
             seg_path((x + 24, y + 140), (x + 194, y + 50), 10), C["J"]))
    add(txt(x + 10, y + 162, "期望：一条宽 10 的 45° 色带", size=15, color="#64748B"))

    # ---- K：ClipPath 多轮廓（1 水平 + 1 竖直 + 1 斜） ----
    head(1, "K ClipPath 多轮廓")
    x, y = cell(1)
    p = (seg_path((x + 18, y + 62), (x + 240, y + 62), 8)
         + " " + seg_path((x + 240, y + 62), (x + 240, y + 150), 8)
         + " " + seg_path((x + 22, y + 150), (x + 120, y + 86), 8))
    add(clip(x + 10, y + 40, 294, 118, p, C["K"]))
    add(txt(x + 10, y + 162, "期望：3 条独立段同色同时出现", size=15, color="#64748B"))

    # ---- K2：ClipPath 模拟真实线路：水平-45°-水平，车站处留缺口 ----
    head(2, "K2 ClipPath 线路折线")
    x, y = cell(2)
    A, B, Cq, D = ((x + 16, y + 110), (x + 90, y + 110),
                   (x + 140, y + 60), (x + 288, y + 60))
    gap = 13.0                      # 车站标记半径附近的缺口半宽
    add(clip(x + 10, y + 40, 294, 118,
             seg_path(A, (B[0] + gap, B[1]), 8)
             + " " + seg_path((B[0] - gap, B[1]), (Cq[0] - 8, Cq[1] - 8), 8)
             + " " + seg_path((Cq[0] + 8, Cq[1] - 8), (D[0], D[1]), 8),
             C["K2"]))
    add(txt(x + 10, y + 162, "期望：45° 转角处连续，缺口处断开", size=15, color="#64748B"))

    # ---- L：Transform 括号格式 45° 旋转（复核 A05） ----
    head(3, "L Transform 旋转")
    x, y = cell(3)
    c45, s45 = 0.7071068, 0.7071068
    m = (f"({c45},{s45},0,{x + 260},{-s45},{c45},0,{y + 100},0,0,1,0,0,0,0,1)")
    add(f'<Positioned left="0" top="0"><Transform matrix="{m}">'
        f'<Container width="150" height="8" color="{C["L"]}"></Container>'
        f'</Transform></Positioned>')
    # 未变换对照
    add(box(x + 210, y + 76, 8, 88, C["L"]))
    add(txt(x + 10, y + 162, "旋转若生效左侧应是斜条；右侧竖条为对照",
            size=15, color="#64748B"))

    # ---- N：Container 的 transform 属性 ----
    head(4, "N Container transform")
    x, y = cell(4)
    add(f'<Positioned left="{x + 20}" top="{y + 60}">'
        f'<Container width="150" height="8" color="{C["N"]}" '
        f'transform="({_n(c45)},{_n(s45)},0,0,{_n(-s45)},{_n(c45)},0,0,0,0,1,0,'
        f'0,0,0,1)" transformAlignment="TOP_LEFT"></Container></Positioned>')
    add(box(x + 210, y + 76, 8, 88, C["N"]))
    add(txt(x + 10, y + 162, "若左侧是斜条说明属性写在 Container 上有效",
            size=15, color="#64748B"))

    # ---- G：实心圆 ----
    head(5, "G 实心圆")
    x, y = cell(5)
    for k, d in enumerate([44, 32, 22, 14]):
        add(box(x + 18 + k * 64, y + 74, d, d, C["G"], d / 2))
    add(txt(x + 10, y + 162, "borderRadius = d/2，d = 44/32/22/14", size=15, color="#64748B"))

    # ---- H：圆环（换乘站候选） ----
    head(6, "H 圆环标记")
    x, y = cell(6)
    for k, d in enumerate([46, 38, 30]):
        pad = 5 if d == 46 else 4
        add(box(x + 20 + k * 82, y + 72, d, d, "#FFFFFF", d / 2,
                "1 SOLID #CBD5E1"))
        add(box(x + 20 + k * 82 + pad, y + 72 + pad, d - 2 * pad, d - 2 * pad,
                C["H"], (d - 2 * pad) / 2))
    add(txt(x + 10, y + 162, "外环颜色 + 内缩实心圆（换乘双圈候选）", size=15, color="#64748B"))

    # ---- D：45° 阶梯 ----
    head(7, "D 45° 阶梯")
    x, y = cell(7)
    for k in range(15):
        add(box(x + 22 + k * 6, y + 70 + k * 6, 12, 12, C["D"], 2))
    add(txt(x + 10, y + 162, "矩形沿对角步进 +6/+6（退路）", size=15, color="#64748B"))

    # ---- E：45° 圆点串 ----
    head(8, "E 45° 圆点串")
    x, y = cell(8)
    for k in range(14):
        add(box(x + 22 + k * 7, y + 70 + k * 7, 12, 12, C["E"], 6))
    add(txt(x + 10, y + 162, "圆点沿对角步进 +7/+7（退路）", size=15, color="#64748B"))

    add("</Stack>")
    add("</Container>")
    add("</Snapshot>")
    dsl = "\n".join(L) + "\n"
    print(f"DSL {len(dsl)} 字符, {dsl.count('<Positioned')} Positioned")

    rec = IO.submit(dsl, label="A07 探针1 · ClipPath 填充与 45° 方案",
                    rid="req-a07-probe1-clip", dsl_version="probe1-clip",
                    kind="draft")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"])
    if rec["error_summary"]:
        print("ERROR", rec["error_summary"])
        print((rec.get("_error_json") or "")[:900])
        return

    src = IO.dirs()[1] / "responses" / f"{rec['request_id']}.body"
    dst = IO.dirs()[1] / "preview" / "probe1-clip.png"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
    im = np.asarray(Image.open(dst).convert("RGB")).astype(float)
    print("canvas", im.shape[1], "x", im.shape[0])

    v = 255.0 - im                      # 偏离白底
    for k, hexc in C.items():
        c = np.array([int(hexc[1:3], 16), int(hexc[3:5], 16), int(hexc[5:7], 16)])
        w = 255.0 - c
        t = np.clip(np.sum(v * w, axis=2) / float(np.dot(w, w)), 0, 1)
        resid = np.linalg.norm(v - t[..., None] * w, axis=2)
        mask = np.all(v >= -1, axis=2) & (np.linalg.norm(v, axis=2) > 12) \
            & (resid < 12)
        n = int(mask.sum())
        if n:
            ys, xs = np.where(mask)
            print(f"  {k:<2} {hexc}  {n:7d} px   "
                  f"x {xs.min()}..{xs.max()}  y {ys.min()}..{ys.max()}")
        else:
            print(f"  {k:<2} {hexc}  {n:7d} px   （未渲染）")

    # J / K2 的斜率与厚度实测：逐列取色带中心 y
    for k, col in (("J", C["J"]), ("K2", C["K2"])):
        c = np.array([int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16)])
        w = 255.0 - c
        t = np.clip(np.sum(v * w, axis=2) / float(np.dot(w, w)), 0, 1)
        mask = (np.linalg.norm(v - t[..., None] * w, axis=2) < 12) \
            & (np.linalg.norm(v, axis=2) > 12)
        runs: list[tuple[int, float, int]] = []
        for xi in range(im.shape[1]):
            col_y = np.where(mask[:, xi])[0]
            if len(col_y) >= 2 and col_y.max() - col_y.min() <= 26:
                runs.append((xi, (col_y.min() + col_y.max()) / 2,
                             int(col_y.max() - col_y.min() + 1)))
        if len(runs) >= 2:
            xs = np.array([r[0] for r in runs], float)
            cy = np.array([r[1] for r in runs], float)
            thr = np.array([r[2] for r in runs], float)
            dx = xs[-1] - xs[0]
            slope = (cy[-1] - cy[0]) / dx if abs(dx) > 1 else float("nan")
            print(f"  {k} 斜率 dx={dx:.0f} → Δy/dx = {slope:+.3f}  "
                  f"垂直厚度 {thr.mean():.1f}px"
                  f"（8px 宽 45° 段期望 ≈ 11.3）")
        else:
            print(f"  {k} 逐列采样不足（{len(runs)} 列）")

    print("preview →", dst.relative_to(IO.ROOT))


if __name__ == "__main__":
    main()
