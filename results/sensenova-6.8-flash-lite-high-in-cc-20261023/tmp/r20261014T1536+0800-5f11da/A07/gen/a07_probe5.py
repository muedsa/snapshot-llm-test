"""A07 能力探针 5：修正后的 45° 段构造 + Stack 绘制次序。

探针 4 的结论（看图 + 像素统计）：
  * `TOP_LEFT` + 无尺寸 Positioned 是**精确且可预测**的：盒的左上角固定，旋转后
    中心线相对 Positioned 原点偏移 (-sinθ·lw/2, cosθ·lw/2)。
    → 想让中心线过目标点 T，Positioned 应放在 T + (sinθ·lw/2, -cosθ·lw/2)。
  * `CENTER` + 显式尺寸 Positioned 会让 Container **填满** Positioned（226×226 实心
    方块，32260 px），而不是旋转自己的 width/height —— 不可用。
  * 探针 4 里 B 格只量到 782 px（期望 3168 px），且视觉上只露出红条之外的残段：
    怀疑 Stack 不是「后画的在上」，而是「先画的在上」。这直接决定示意图里
    站标记能否盖住线路，必须先定。

本探针做三件事：
  1) 绘制次序：同位置三块不透明色块按 1→2→3 画，最终留下哪块
  2) 修正后的 45° 段：中心线精确过两端靶点（用 lw/2 垂直预偏移）
  3) 肘形接头：水平接 45°、竖直接 45°，接头处中心线连续 + 站标记覆盖线路

线宽 14，圆头 borderRadius=7，与最终示意图一致。

用法：python -I tmp/<rid>/A07/gen/a07_probe5.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a07_io as IO  # noqa: E402

from PIL import Image  # noqa: E402

FA = 'fontFamily="Noto Sans CJK SC"'
LW = 14.0
CLR = {"P1": "#EF4444", "P2": "#10B981", "P3": "#3B82F6",
       "Q1": "#7C3AED", "JA": "#DC2626", "JB": "#2563EB"}
TARGET = "#94A3B8"
BOX = "#FFFFFF"
EDGE = "#CBD5E1"


def _n(v: float) -> str:
    s = f"{v:.6f}".rstrip("0").rstrip(".")
    return s if s else "0"


def mat(theta_deg: float) -> str:
    t = math.radians(theta_deg)
    c, s = math.cos(t), math.sin(t)
    return (f"({_n(c)},{_n(s)},0,0,{_n(-s)},{_n(c)},0,0,"
            f"0,0,1,0,0,0,0,1)")


def box(px, py, w, h, color, radius=0, border=None) -> str:
    r = f' borderRadius="{_n(radius)}"' if radius else ""
    b = f' border="{border}"' if border else ""
    return (f'<Positioned left="{_n(px)}" top="{_n(py)}" width="{_n(w)}" '
            f'height="{_n(h)}"><Container width="{_n(w)}" height="{_n(h)}" '
            f'color="{color}"{r}{b}></Container></Positioned>')


def txt(left, top, s, size=18, color="#0F172A", bold=False) -> str:
    st = ' fontStyle="BOLD"' if bold else ""
    return (f'<Positioned left="{_n(left)}" top="{_n(top)}"><Text text="{s}" '
            f'fontSize="{size}"{st} color="{color}" {FA}></Text></Positioned>')


def diag(p1, p2, color: str) -> str:
    """修正后的 45° 段：中心线精确过 p1 与 p2。

    角 θ = atan2(dy, dx)；Positioned 原点 = p1 + (sinθ·lw/2, -cosθ·lw/2)。
    仅支持 45° 的四个方向（|dx| == |dy|）。
    """
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    assert abs(abs(dx) - abs(dy)) < 1e-6, "本构造仅支持 45° 段"
    theta = math.degrees(math.atan2(dy, dx))
    t = math.radians(theta)
    ox = p1[0] + math.sin(t) * LW / 2
    oy = p1[1] - math.cos(t) * LW / 2
    W = math.hypot(dx, dy)
    return (f'<Positioned left="{_n(ox)}" top="{_n(oy)}">'
            f'<Container width="{_n(W)}" height="{_n(LW)}" color="{color}" '
            f'borderRadius="{_n(LW / 2)}" transform="{mat(theta)}" '
            f'transformAlignment="TOP_LEFT"></Container></Positioned>')


def hseg(x1, x2, cy, color):
    return box(min(x1, x2), cy - LW / 2, abs(x2 - x1), LW, color, LW / 2)


def vseg(y1, y2, cx, color):
    return box(cx - LW / 2, min(y1, y2), LW, abs(y2 - y1), color, LW / 2)


def cross(tx, ty, arm=11) -> list[str]:
    return [box(tx - arm, ty - 1, arm * 2, 2, TARGET),
            box(tx - 1, ty - arm, 2, arm * 2, TARGET)]


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    CW, CH = 940, 560
    L: list[str] = []
    add = L.append
    add('<Snapshot background="#F8FAFC" type="png">')
    add(f'<Container width="{CW}" height="{CH}" color="#F8FAFC">')
    add('<Stack fit="EXPAND" clipBehavior="NONE">')

    add(txt(24, 10, "A07 探针 5 · 绘制次序 与 修正后 45° 段的接头",
            size=22, bold=True))
    add(box(24, 44, 892, 1, "#E2E8F0"))

    # ---- 1) 绘制次序：三块 110×110 重叠 ----
    add(txt(30, 58, "1 绘制次序：同一位置按 1 → 2 → 3 画三块不透明色块",
            size=20))
    add(box(100, 96, 110, 110, CLR["P1"], 8, "2 SOLID #111827"))
    add(box(100, 96, 110, 110, CLR["P2"], 8, "2 SOLID #111827"))
    add(box(100, 96, 110, 110, CLR["P3"], 8, "2 SOLID #111827"))
    add(txt(104, 214, "三块同位置；最后画的是蓝色 P3", size=17, color="#475569"))
    add(txt(262, 116, "看到蓝 = 后画的在上", size=17, color="#475569"))
    add(txt(262, 146, "看到红 = 先画的在上", size=17, color="#475569"))

    # ---- 2) 修正后的 45° 段：两端靶点应正好落在端点 ----
    add(txt(30, 250, "2 修正后 45° 段：中心线精确过两端灰十字",
            size=20))
    d1, d2 = (110.0, 430.0), (279.71, 260.29)
    for el in cross(*d1) + cross(*d2):
        add(el)
    add(diag(d1, d2, CLR["Q1"]))
    add(txt(110, 448, f"端点 ({d1[0]:.0f},{d1[1]:.0f}) → ({d2[0]:.0f},{d2[1]:.0f}) "
                      f" 盒宽 {math.hypot(*[b - a for a, b in zip(d2, d1)]):.2f}",
            size=17, color="#475569"))

    # ---- 3) 肘形接头 A：水平 → 45° NE，接头处放站标记 ----
    add(txt(330, 250, "3 肘形接头 A：水平 → 45°，接头处站标记应盖住线路",
            size=20))
    j1, j2, j3 = (390.0, 430.0), (530.0, 430.0), (659.71, 300.29)
    for el in cross(*j1) + cross(*j2) + cross(*j3):
        add(el)
    add(hseg(j1[0], j2[0], j2[1], CLR["JA"]))
    add(diag(j2, j3, CLR["JA"]))
    # 站标记：换乘站（外圈 + 内缩无障碍状态圆）与单线站，画在线路之后
    # 边框用 #0F172A / #991B1B，与线路色不同，避免污染像素统计
    add(box(j2[0] - 15, j2[1] - 15, 30, 30, "#FFFFFF", 15, "3 SOLID #0F172A"))
    add(box(j2[0] - 6, j2[1] - 6, 12, 12, "#94A3B8", 6))
    add(box(j1[0] - 12, j1[1] - 12, 24, 24, "#FFFFFF", 12, "3 SOLID #991B1B"))
    add(txt(390, 452, "白心=无障碍   灰心=无无障碍设施", size=17, color="#475569"))

    # ---- 4) 肘形接头 B：竖直 → 45° SE ----
    add(txt(560, 250, "4 接头 B：竖直 → 45° SE", size=20))
    k1, k2, k3 = (700.0, 270.0), (700.0, 360.0), (789.71, 449.71)
    for el in cross(*k1) + cross(*k2) + cross(*k3):
        add(el)
    add(vseg(k1[1], k2[1], k1[0], CLR["JB"]))
    add(diag(k2, k3, CLR["JB"]))
    add(box(k2[0] - 12, k2[1] - 12, 24, 24, "#FFFFFF", 12, "3 SOLID #1E40AF"))

    add("</Stack>")
    add("</Container>")
    add("</Snapshot>")
    dsl = "\n".join(L) + "\n"
    print(f"DSL {len(dsl)} 字符, {dsl.count('<Positioned')} Positioned")

    rec = IO.submit(dsl, label="A07 探针5 · 绘制次序与修正后 45° 接头",
                    rid="req-a07-probe5-order", dsl_version="probe5-order",
                    kind="draft")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"])
    if rec["error_summary"]:
        print("ERROR", rec["error_summary"])
        print((rec.get("_error_json") or "")[:900])
        return

    src = IO.dirs()[1] / "responses" / f"{rec['request_id']}.body"
    dst = IO.dirs()[1] / "preview" / "probe5-order.png"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
    im = np.asarray(Image.open(dst).convert("RGB"))
    print("canvas", im.shape[1], "x", im.shape[0])

    v = 255.0 - im.astype(float)

    def mask(hexc: str) -> np.ndarray:
        c = np.array([int(hexc[1:3], 16), int(hexc[3:5], 16), int(hexc[5:7], 16)])
        w = 255.0 - c
        t = np.clip(np.sum(v * w, axis=2) / float(np.dot(w, w)), 0, 1)
        resid = np.linalg.norm(v - t[..., None] * w, axis=2)
        return (np.linalg.norm(v, axis=2) > 60) & (t >= 0.6) & (resid < 25)

    print("\n---- 绘制次序：三块重叠区中心像素的颜色 ----")
    for yy in (120, 148, 180):
        for xx in (130, 155, 180):
            r, g, b = im[yy, xx]
            print(f"    ({xx},{yy}) = #{int(r):02X}{int(g):02X}{int(b):02X}")

    print("\n---- 45° 段端点与厚度（期望沿向 ±84.85、垂直 ±7.00）----")
    for key, hexc, p1, p2 in (
            ("2·NE", CLR["Q1"], d1, d2),
            ("3·NE", CLR["JA"], j2, j3),
            ("4·SE", CLR["JB"], k2, k3)):
        m = mask(hexc)
        ys, xs = np.where(m)
        if not len(xs):
            print(f"  {key}: 无像素")
            continue
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        nrm = math.hypot(dx, dy)
        ux, uy = dx / nrm, dy / nrm
        px_, py_ = -uy, ux
        cx, cy = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        rx, ry = xs - cx, ys - cy
        along = rx * ux + ry * uy
        perp = rx * px_ + ry * py_
        i_far, i_near = int(np.argmax(along)), int(np.argmin(along))
        print(f"  {key} {hexc}  {len(xs):5d} px   "
              f"远端 Δ=({xs[i_far] - p2[0]:+.2f},{ys[i_far] - p2[1]:+.2f})  "
              f"近端 Δ=({xs[i_near] - p1[0]:+.2f},{ys[i_near] - p1[1]:+.2f})")
        print(f"       沿向 {along.min():+.2f}..{along.max():+.2f}  "
              f"（期望 ±{nrm / 2:.2f}）  垂直 {perp.min():+.2f}..{perp.max():+.2f}"
              f"（期望 ±{LW / 2:.2f}）")

    print("\n---- 接头中心线连续性：接头两侧各段沿自己的方向取样 ----")

    def coverage(hexc, jp, ux, uy, ks):
        m = mask(hexc)
        miss = []
        for k in ks:
            cx = int(round(jp[0] + k * ux))
            cy = int(round(jp[1] + k * uy))
            hit = any(m[cy + oy, cx + ox]
                      for oy in range(-5, 6) for ox in range(-5, 6)
                      if 0 <= cy + oy < m.shape[0] and 0 <= cx + ox < m.shape[1])
            if not hit:
                miss.append((cx, cy))
        return len(miss), len(ks)

    s2 = 1 / math.sqrt(2)
    # 接头 A：左侧水平段（方向 -x）+ 右侧 NE 斜段
    a1 = coverage(CLR["JA"], j2, -1.0, 0.0, range(-40, -20))
    a2 = coverage(CLR["JA"], j2, s2, -s2, range(20, 41))
    print(f"  水平+NE: 水平侧缺失 {a1[0]}/{a1[1]}  NE 侧缺失 {a2[0]}/{a2[1]}"
          f"（0 = 中心线连续穿过接头）")
    # 接头 B：上侧竖直段（方向 -y）+ 下侧 SE 斜段
    b1 = coverage(CLR["JB"], k2, 0.0, -1.0, range(-40, -20))
    b2 = coverage(CLR["JB"], k2, s2, s2, range(20, 41))
    print(f"  竖直+SE: 竖直侧缺失 {b1[0]}/{b1[1]}  SE 侧缺失 {b2[0]}/{b2[1]}"
          f"（0 = 中心线连续穿过接头）")
    print("preview →", dst.relative_to(IO.ROOT))


if __name__ == "__main__":
    main()
