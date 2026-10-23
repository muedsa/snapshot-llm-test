"""A07 能力探针 2：Container 的 transform 属性画 45° 段。

探针 1 的结论（看图 + 逐像素确认）：
  * `<ClipPath path=...>` + 彩色 Container 子节点 —— 三格全部空白，不填充路径区域。
  * `<Transform matrix=...>` 标签 —— 依然只画平移，旋转静默失效（复核 A05）。
  * **`<Container transform="(...)">` + `transformAlignment` —— 真的旋转了**，
    N 格里画出了一条清晰的 45° 斜线。这是本题 45° 折线的实现方式。

本次要量清三件事：
  1. 四种对角方向各自的矩阵符号（NE / SE / SW / NW）
  2. 远端端点是否落在预测位置（决定 model 能否直接算端点）
  3. borderRadius 做圆头 + 旋转后是否保持（地铁线路的接头观感）
另加一次 ClipPath 尝试：把 ClipPath 放进 Container 里，而不是直接挂在 Positioned 下。

矩阵约定（列主序 4×4，外层括号、逗号分隔、无空格）：
  flat = (cosθ, sinθ, 0, 0, -sinθ, cosθ, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
  θ=+45°  → 右下(SE)；θ=-45° → 右上(NE)；θ=+135° → 左下(SW)；θ=+225° → 左上(NW)
  盒宽 W = hypot(dx, dy)，盒高 = 线宽；旋转中心为盒左上角，因此盒左上角固定在
  Positioned 坐标处，远端角 (W,0) 正好落在目标点。

用法：python -I tmp/<rid>/A07/gen/a07_probe2.py
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
C45 = 0.7071067811865476

# 方向 → (角度, 目标偏移)
DIRS = {
    "NE": (-45.0, (160, -160)),
    "SE": (45.0, (160, 160)),
    "SW": (135.0, (-160, 160)),
    "NW": (225.0, (-160, -160)),
}
CLR = {
    "NE": "#DC2626", "SE": "#2563EB", "SW": "#16A34A", "NW": "#7C3AED",
    "CAP": "#D97706", "CLIP": "#1D4ED8", "AX": "#0891B2",
}


def _n(v: float) -> str:
    s = f"{v:.6f}".rstrip("0").rstrip(".")
    return s if s else "0"


def mat(theta_deg: float, tx: float = 0.0, ty: float = 0.0) -> str:
    t = math.radians(theta_deg)
    c, s = math.cos(t), math.sin(t)
    return (f"({_n(c)},{_n(s)},0,{_n(tx)},{_n(-s)},{_n(c)},0,{_n(ty)},"
            f"0,0,1,0,0,0,0,1)")


def rotseg(px, py, dx, dy, lw, color, theta: float, radius=0) -> str:
    """在 (px,py) 处画一条宽 lw、指向 (px+dx, py+dy) 的旋转线段。"""
    W = math.hypot(dx, dy)
    r = f' borderRadius="{_n(radius)}"' if radius else ""
    return (f'<Positioned left="{_n(px)}" top="{_n(py)}">'
            f'<Container width="{_n(W)}" height="{_n(lw)}" color="{color}"{r} '
            f'transform="{mat(theta)}" '
            f'transformAlignment="TOP_LEFT"></Container></Positioned>')


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


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    W, H = 1000, 700
    L: list[str] = []
    add = L.append
    add('<Snapshot background="#F8FAFC" type="png">')
    add(f'<Container width="{W}" height="{H}" color="#F8FAFC">')
    add('<Stack fit="EXPAND" clipBehavior="NONE">')

    add(txt(24, 14, "A07 探针 2 · Container transform 画 45° 段（端点/厚度/圆头）",
            size=24, bold=True))
    add(hrect(24, 52, 952, 1, "#E2E8F0"))

    # ---- 区 1：从同一起点出发的四个对角方向 ----
    OX, OY = 500, 330          # 共同起点
    add(hrect(24, 62, 952, 480, "#FFFFFF", 8, "1 SOLID #CBD5E1"))
    add(txt(34, 74, "1 四个对角方向：同一端点出发，盒宽 160√2 = 226.27，宽 10",
            size=20))
    for k, (th, (dx, dy)) in DIRS.items():
        add(rotseg(OX, OY, dx, dy, 10, CLR[k], theta=th))
        # 目标点标记（十字）
        tx, ty = OX + dx, OY + dy
        add(hrect(tx - 9, ty - 1, 18, 2, "#94A3B8"))
        add(hrect(tx - 1, ty - 9, 2, 18, "#94A3B8"))
        add(txt(tx - 22, ty + 14, f"{k} 端点 ({tx},{ty})", size=16,
                color="#64748B"))
    add(hrect(OX - 1, OY - 1, 2, 2, "#0F172A"))
    add(txt(OX + 8, OY - 22, f"起点 ({OX},{OY})", size=16, color="#0F172A"))

    # ---- 区 2：圆头 ----
    y0 = 560
    add(txt(34, y0 - 26, "2 圆头：borderRadius = 线宽/2，旋转后是否仍为圆头",
            size=20))
    add(rotseg(60, y0 + 80, 200, -200, 16, CLR["CAP"], radius=8,
               theta=-45.0))
    add(txt(70, y0 + 100, "旋转 NE 段，圆头（左端应圆）", size=16,
            color="#64748B"))
    add(hrect(60, y0 + 40, 200, 16, CLR["CAP"], 8))
    add(txt(70, y0 + 62, "轴对齐对照：pill 形，两端圆", size=16,
            color="#64748B"))

    # ---- 区 3：轴对齐段（不需要 transform） ----
    add(hrect(520, y0 + 40, 220, 10, CLR["AX"]))
    add(txt(520, y0 + 60, "轴对齐水平段（直接矩形，无需 transform）",
            size=16, color="#64748B"))
    add(hrect(560, y0 + 84, 10, 60, CLR["AX"]))
    add(txt(580, y0 + 96, "轴对齐竖直段", size=16, color="#64748B"))

    # ---- 区 4：ClipPath 再试一次（放进 Container 里） ----
    y1 = 640
    add(hrect(24, 606, 952, 76, "#FFFFFF", 8, "1 SOLID #CBD5E1"))
    add(txt(34, y1 - 24, "3 ClipPath 重试：包在 Container 里而非直接挂在 Positioned",
            size=20))
    path = ("M60 690 L200 690 L200 698 L60 698 Z M60 690 L150 600 L158 608 "
            "L68 698 Z")
    add(f'<Positioned left="0" top="0" width="{W}" height="{H}">'
        f'<Container width="{W}" height="{H}">'
        f'<ClipPath path="{path}" clipBehavior="ANTI_ALIAS">'
        f'<Container width="{W}" height="{H}" color="{CLR["CLIP"]}">'
        f'</Container></ClipPath></Container></Positioned>')
    add(txt(230, 676, "（若此格空白则 ClipPath 在本服务下不填充）", size=16,
            color="#64748B"))

    add("</Stack>")
    add("</Container>")
    add("</Snapshot>")
    dsl = "\n".join(L) + "\n"
    print(f"DSL {len(dsl)} 字符, {dsl.count('<Positioned')} Positioned")

    rec = IO.submit(dsl, label="A07 探针2 · Container transform 45° 段",
                    rid="req-a07-probe2-rot", dsl_version="probe2-rot",
                    kind="draft")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"])
    if rec["error_summary"]:
        print("ERROR", rec["error_summary"])
        print((rec.get("_error_json") or "")[:900])
        return

    src = IO.dirs()[1] / "responses" / f"{rec['request_id']}.body"
    dst = IO.dirs()[1] / "preview" / "probe2-rot.png"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
    im = np.asarray(Image.open(dst).convert("RGB")).astype(float)

    v = 255.0 - im
    for k, hexc in CLR.items():
        c = np.array([int(hexc[1:3], 16), int(hexc[3:5], 16), int(hexc[5:7], 16)])
        w = 255.0 - c
        t = np.clip(np.sum(v * w, axis=2) / float(np.dot(w, w)), 0, 1)
        resid = np.linalg.norm(v - t[..., None] * w, axis=2)
        mask = (np.linalg.norm(v, axis=2) > 60) & (t >= 0.6) & (resid < 25)
        n = int(mask.sum())
        if n:
            ys, xs = np.where(mask)
            print(f"  {k:<5} {hexc}  {n:7d} px   "
                  f"x {xs.min():4d}..{xs.max():4d}  y {ys.min():4d}..{ys.max():4d}")
        else:
            print(f"  {k:<5} {hexc}  {n:7d} px   （未渲染）")

    print()
    print("---- 四个方向的端点与垂直厚度实测 ----")
    for k, (th, (dx, dy)) in DIRS.items():
        hexc = CLR[k]
        c = np.array([int(hexc[1:3], 16), int(hexc[3:5], 16), int(hexc[5:7], 16)])
        w = 255.0 - c
        t = np.clip(np.sum(v * w, axis=2) / float(np.dot(w, w)), 0, 1)
        mask = (np.linalg.norm(v - t[..., None] * w, axis=2) < 25) \
            & (np.linalg.norm(v, axis=2) > 60) & (t >= 0.6)
        ys, xs = np.where(mask)
        if len(xs) == 0:
            print(f"  {k}: 无像素")
            continue
        # 端点：沿该对角方向的最远点
        ux, uy = dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)
        proj = xs * ux + ys * uy
        far = int(np.argmax(proj))
        # 垂直方向厚度：把像素投影到垂直轴
        px, py = -uy, ux
        perp = (xs - OX) * px + (ys - OY) * py
        # 端点沿主方向的投影范围
        along = (xs - OX) * ux + (ys - OY) * uy
        print(f"  {k}: 起点端沿向 {along.min():+.2f}px  "
              f"远端 {along.max():+.2f}px（期望 {math.hypot(dx, dy):.2f}）"
              f"  垂直厚度 {perp.min():+.2f}..{perp.max():+.2f} "
              f"（期望 ±5.0，10px 宽）")
    print("preview →", dst.relative_to(IO.ROOT))


if __name__ == "__main__":
    main()
