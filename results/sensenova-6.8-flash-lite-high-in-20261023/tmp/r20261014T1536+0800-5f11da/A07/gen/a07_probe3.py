"""A07 能力探针 3：Container transform 的 CENTER 对齐 + 线段接头连续性。

探针 2 已确认 `Container transform=` 属性真的旋转，且用 transformAlignment=
TOP_LEFT 时远端落点误差 <1px。但 A07 的线网要用「盒中心 = 段中点」的 CENTER 对齐：
这样两端的端点都精确落在预测位置，接头处中心线连续，不需要按 lw/2 做垂直偏移。
本题只用一个对角方向（NE，θ=-45°）与水平/竖直段拼接，所以这里重点量：

  1. CENTER 下 NE 段的两端落点误差（画布上放灰色十字靶标）
  2. CENTER 下 SE 段（θ=+45°）复核符号约定
  3. 水平段接 NE 斜段、竖直段接 SE 斜段：接缝处中心线是否连续、有无台阶

线宽与最终示意图一致：14px，圆头 borderRadius=7。

用法：python -I tmp/<rid>/A07/gen/a07_probe3.py
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
CLR = {
    "NE": "#DC2626", "SE": "#2563EB",
    "JA": "#16A34A", "JB": "#7C3AED",
}
TARGET = "#94A3B8"      # 十字靶标
BOX = "#FFFFFF"
EDGE = "#CBD5E1"


def _n(v: float) -> str:
    s = f"{v:.6f}".rstrip("0").rstrip(".")
    return s if s else "0"


def mat(theta_deg: float) -> str:
    """列主序 4×4 flat，16 个逗号分隔浮点，无空格。"""
    t = math.radians(theta_deg)
    c, s = math.cos(t), math.sin(t)
    return (f"({_n(c)},{_n(s)},0,0,{_n(-s)},{_n(c)},0,0,"
            f"0,0,1,0,0,0,0,1)")


def rotseg_c(cx, cy, dx, dy, color, theta: float) -> str:
    """CENTER 对齐：盒中心固定在 (cx,cy)，两端精确落在 (cx±dx/2, cy±dy/2)。"""
    W = math.hypot(dx, dy)
    return (f'<Positioned left="{_n(cx)}" top="{_n(cy)}">'
            f'<Container width="{_n(W)}" height="{_n(LW)}" color="{color}" '
            f'borderRadius="{_n(LW / 2)}" transform="{mat(theta)}" '
            f'transformAlignment="CENTER"></Container></Positioned>')


def hrect(px, py, w, h, color, radius=0, border=None) -> str:
    r = f' borderRadius="{_n(radius)}"' if radius else ""
    b = f' border="{border}"' if border else ""
    return (f'<Positioned left="{_n(px)}" top="{_n(py)}" width="{_n(w)}" '
            f'height="{_n(h)}"><Container width="{_n(w)}" height="{_n(h)}" '
            f'color="{color}"{r}{b}></Container></Positioned>')


def txt(left, top, s, size=18, color="#0F172A", bold=False) -> str:
    st = ' fontStyle="BOLD"' if bold else ""
    return (f'<Positioned left="{_n(left)}" top="{_n(top)}"><Text text="{s}" '
            f'fontSize="{size}"{st} color="{color}" {FA}></Text></Positioned>')


def crosshair(tx, ty, color=TARGET, arm=10) -> list[str]:
    """十字靶标：2px 粗，用于目视与像素级定位端点。"""
    return [
        hrect(tx - arm, ty - 1, arm * 2, 2, color),
        hrect(tx - 1, ty - arm, 2, arm * 2, color),
    ]


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    W, H = 960, 620
    L: list[str] = []
    add = L.append
    add('<Snapshot background="#F8FAFC" type="png">')
    add(f'<Container width="{W}" height="{H}" color="#F8FAFC">')
    add('<Stack fit="EXPAND" clipBehavior="NONE">')

    add(txt(24, 12, "A07 探针 3 · transformAlignment=CENTER 的端点落点与接头连续性",
            size=22, bold=True))
    add(hrect(24, 46, 912, 1, "#E2E8F0"))

    # ---- 区 1：CENTER 下两个对角方向，灰色十字标出理论端点 ----
    add(hrect(24, 56, 912, 300, BOX, 8, "1 SOLID " + EDGE))
    add(txt(36, 66, "1 CENTER 对齐：盒中心 = 段中点，两端理论落点标灰十字",
            size=20))
    OX, OY = 480, 240
    HALF = 160 * 0.7071067811865476          # 113.137
    # NE: θ = -45°
    n1, n2 = (OX - HALF, OY + HALF), (OX + HALF, OY - HALF)
    for el in crosshair(*n1):
        add(el)
    for el in crosshair(*n2):
        add(el)
    add(rotseg_c(OX, OY, 2 * HALF, -2 * HALF, CLR["NE"], -45.0))
    add(txt(n1[0] - 150, n1[1] + 14, f"NE 近端 ({n1[0]:.1f},{n1[1]:.1f})",
            size=17, color="#475569"))
    add(txt(n2[0] - 60, n2[1] - 30, f"NE 远端 ({n2[0]:.1f},{n2[1]:.1f})",
            size=17, color="#475569"))
    add(txt(OX + 10, OY - 18, f"中心 ({OX},{OY}) · 盒宽 {2 * HALF:.3f} = 160√2",
            size=17, color="#475569"))
    # SE: θ = +45°
    s1, s2 = (OX - HALF, OY - HALF), (OX + HALF, OY + HALF)
    for el in crosshair(*s1):
        add(el)
    for el in crosshair(*s2):
        add(el)
    add(rotseg_c(OX, OY, 2 * HALF, 2 * HALF, CLR["SE"], 45.0))
    add(txt(s1[0] - 150, s1[1] - 30, f"SE 近端 ({s1[0]:.1f},{s1[1]:.1f})",
            size=17, color="#475569"))
    add(txt(s2[0] - 60, s2[1] + 30, f"SE 远端 ({s2[0]:.1f},{s2[1]:.1f})",
            size=17, color="#475569"))

    # ---- 区 2：接头连续性 ----
    add(hrect(24, 372, 912, 232, BOX, 8, "1 SOLID " + EDGE))
    add(txt(36, 382, "2 接头：水平段接 NE 斜段、竖直段接 SE 斜段（14px 圆头）",
            size=20))
    # 接头 A：水平 (100,480)→(300,480) 接 NE 斜段 (300,480)→(414.14,365.86)
    A1, A2 = (100.0, 480.0), (300.0, 480.0)
    A3 = (300.0 + HALF, 480.0 - HALF)
    add(hrect(A1[0], A1[1] - LW / 2, A2[0] - A1[0], LW, CLR["JA"], LW / 2))
    add(rotseg_c((A2[0] + A3[0]) / 2, (A2[1] + A3[1]) / 2,
                 A3[0] - A2[0], A3[1] - A2[1], CLR["JA"], -45.0))
    add(txt(A1[0], 500, "水平 → NE：接缝在 (300,480)，中心线应连续无台阶",
            size=17, color="#475569"))
    # 接头 B：竖直 (640,410)→(640,510) 接 SE 斜段 (640,510)→(754.14,624.14)
    B1, B2 = (640.0, 410.0), (640.0, 510.0)
    B3 = (640.0 + HALF, 510.0 + HALF)
    add(hrect(B1[0] - LW / 2, B1[1], LW, B2[1] - B1[1], CLR["JB"], LW / 2))
    add(rotseg_c((B2[0] + B3[0]) / 2, (B2[1] + B3[1]) / 2,
                 B3[0] - B2[0], B3[1] - B2[1], CLR["JB"], 45.0))
    add(txt(B1[0] + 20, 452, "竖直 → SE：接缝在 (640,510)",
            size=17, color="#475569"))

    add("</Stack>")
    add("</Container>")
    add("</Snapshot>")
    dsl = "\n".join(L) + "\n"
    print(f"DSL {len(dsl)} 字符, {dsl.count('<Positioned')} Positioned")

    rec = IO.submit(dsl, label="A07 探针3 · CENTER 端点落点与接头连续性",
                    rid="req-a07-probe3-center", dsl_version="probe3-center",
                    kind="draft")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"])
    if rec["error_summary"]:
        print("ERROR", rec["error_summary"])
        print((rec.get("_error_json") or "")[:900])
        return

    src = IO.dirs()[1] / "responses" / f"{rec['request_id']}.body"
    dst = IO.dirs()[1] / "preview" / "probe3-center.png"
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

    print("\n---- CENTER 端点落点实测（靶标坐标 vs 像素极值）----")
    for key, hexc, p_near, p_far, dx, dy in (
            ("NE", CLR["NE"], n1, n2, 2 * HALF, -2 * HALF),
            ("SE", CLR["SE"], s1, s2, 2 * HALF, 2 * HALF)):
        m = mask(hexc)
        ys, xs = np.where(m)
        if not len(xs):
            print(f"  {key}: 无像素")
            continue
        ux, uy = dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)
        px, py = -uy, ux
        rel_x, rel_y = xs - OX, ys - OY
        along = rel_x * ux + rel_y * uy
        perp = rel_x * px + rel_y * py
        i_far = int(np.argmax(along))
        i_near = int(np.argmin(along))
        print(f"  {key} {hexc}  {len(xs)} px")
        print(f"    远端 像素 ({xs[i_far]},{ys[i_far]}) vs 理论 "
              f"({p_far[0]:.2f},{p_far[1]:.2f})  "
              f"Δ=({xs[i_far] - p_far[0]:+.2f},{ys[i_far] - p_far[1]:+.2f})")
        print(f"    近端 像素 ({xs[i_near]},{ys[i_near]}) vs 理论 "
              f"({p_near[0]:.2f},{p_near[1]:.2f})  "
              f"Δ=({xs[i_near] - p_near[0]:+.2f},{ys[i_near] - p_near[1]:+.2f})")
        print(f"    沿向范围 {along.min():+.2f}..{along.max():+.2f} "
              f"（期望 ±{HALF:.2f}）  垂直厚度 {perp.min():+.2f}..{perp.max():+.2f}"
              f"（期望 ±{LW / 2:.2f}）")

    print()
    print("---- 接头连续性：沿接缝点取样，看两段是否覆盖同一像素 ----")
    for key, hexc, jx, jy, ux, uy, name in (
            ("JA", CLR["JA"], 300.0, 480.0, 1.0 / math.sqrt(2), -1.0 / math.sqrt(2),
             "水平+NE"),
            ("JB", CLR["JB"], 640.0, 510.0, 1.0 / math.sqrt(2), 1.0 / math.sqrt(2),
             "竖直+SE")):
        m = mask(hexc)
        lo, hi = -30, 31
        miss = []
        for k in range(lo, hi + 1):
            cx = int(round(jx + k * ux))
            cy = int(round(jy + k * uy))
            # 该点沿线段方向 ±4px 内应有像素
            hit = False
            for ox in range(-4, 5):
                for oy in range(-4, 5):
                    yy, xx = cy + oy, cx + ox
                    if 0 <= yy < m.shape[0] and 0 <= xx < m.shape[1] and m[yy, xx]:
                        hit = True
                        break
                if hit:
                    break
            if not hit:
                miss.append((cx, cy))
        print(f"  {name} {hexc}: 接缝点 ({jx},{jy}) 两侧 {abs(lo)}..{hi} 步 "
              f"缺失 {len(miss)} 个（0 = 中心线连续）")
    print("preview →", dst.relative_to(IO.ROOT))


if __name__ == "__main__":
    main()
