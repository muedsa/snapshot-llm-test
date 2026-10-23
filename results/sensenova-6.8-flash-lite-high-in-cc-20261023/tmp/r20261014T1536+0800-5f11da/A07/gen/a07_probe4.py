"""A07 能力探针 4：把 45° 段定位方式一次量清。

探针 3 发现：`Positioned` 不写 width/height 时，`transformAlignment="CENTER"` 的
旋转中心并不是「无尺寸 Positioned 的点」——NE 段整体沿垂直方向偏移了约 160px。
而探针 2 里 `TOP_LEFT` 的远端落点是准的（误差 <1px）。这里在同一张图里复核两件事：

  A  TOP_LEFT + 无尺寸 Positioned（复核探针 2 的结论）
  B  TOP_LEFT + 无尺寸 Positioned，外加按 lw/2 做的垂直预偏移（真正想要的效果）
  C  CENTER + **显式尺寸** Positioned（旋转中心 = Positioned 几何中心）
  D  CENTER + 显式尺寸 Positioned，Positioned 尺寸略小于旋转后包围盒（溢出检查）

每格都画两个灰色十字标出理论端点；线宽 14，圆头 7，与最终示意图一致。

用法：python -I tmp/<rid>/A07/gen/a07_probe4.py
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
H = 160 * 0.7071067811865476          # 半长 113.137
CLR = {"A": "#DC2626", "B": "#2563EB", "C": "#16A34A", "D": "#7C3AED"}
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


def crosshair(tx, ty, arm=10, color=TARGET) -> list[str]:
    return [
        f'<Positioned left="{_n(tx - arm)}" top="{_n(ty - 1)}" width="{arm * 2}" '
        f'height="2"><Container width="{arm * 2}" height="2" color="{color}">'
        f'</Container></Positioned>',
        f'<Positioned left="{_n(tx - 1)}" top="{_n(ty - arm)}" width="2" '
        f'height="{arm * 2}"><Container width="2" height="{arm * 2}" '
        f'color="{color}"></Container></Positioned>',
    ]


def txt(left, top, s, size=18, color="#0F172A", bold=False) -> str:
    st = ' fontStyle="BOLD"' if bold else ""
    return (f'<Positioned left="{_n(left)}" top="{_n(top)}"><Text text="{s}" '
            f'fontSize="{size}"{st} color="{color}" {FA}></Text></Positioned>')


def hrect(px, py, w, h, color, radius=0, border=None) -> str:
    r = f' borderRadius="{_n(radius)}"' if radius else ""
    b = f' border="{border}"' if border else ""
    return (f'<Positioned left="{_n(px)}" top="{_n(py)}" width="{_n(w)}" '
            f'height="{_n(h)}"><Container width="{_n(w)}" height="{_n(h)}" '
            f'color="{color}"{r}{b}></Container></Positioned>')


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    CW, CH = 1000, 640
    L: list[str] = []
    add = L.append
    add('<Snapshot background="#F8FAFC" type="png">')
    add(f'<Container width="{CW}" height="{CH}" color="#F8FAFC">')
    add('<Stack fit="EXPAND" clipBehavior="NONE">')

    add(txt(24, 12, "A07 探针 4 · 45° 段定位：TOP_LEFT 复核 与 CENTER+显式尺寸",
            size=22, bold=True))
    add(hrect(24, 46, 952, 1, "#E2E8F0"))

    # 每格中心
    ROW = {"A": (500, 150), "B": (500, 300), "C": (500, 450), "D": (500, 590)}
    TITLES = {
        "A": "A  TOP_LEFT + 无尺寸 Positioned（复核探针 2）",
        "B": "B  TOP_LEFT + 无尺寸 + 垂直预偏移 (sin·lw/2, -cos·lw/2)",
        "C": "C  CENTER + 显式尺寸 Positioned（尺寸 = 160√2 × 14）",
        "D": "D  CENTER + 显式尺寸 Positioned（尺寸 236×24，略小于包围盒）",
    }
    for k, (ox, oy) in ROW.items():
        add(txt(30, oy - 74, TITLES[k], size=20))
        # 理论端点：从 ox,oy 向 NE（θ=-45°）走 2H
        p1 = (ox - H, oy + H)          # 近端（左下）
        p2 = (ox + H, oy - H)          # 远端（右上）
        for el in crosshair(*p1) + crosshair(*p2):
            add(el)

        W2 = 2 * H
        if k == "A":
            # Positioned 原点 = 近端
            add(f'<Positioned left="{_n(p1[0])}" top="{_n(p1[1])}">'
                f'<Container width="{_n(W2)}" height="{_n(LW)}" color="{CLR[k]}" '
                f'borderRadius="{_n(LW / 2)}" transform="{mat(-45.0)}" '
                f'transformAlignment="TOP_LEFT"></Container></Positioned>')
        elif k == "B":
            t = math.radians(-45.0)
            offx, offy = math.sin(t) * LW / 2, -math.cos(t) * LW / 2
            add(f'<Positioned left="{_n(p1[0] + offx)}" top="{_n(p1[1] + offy)}">'
                f'<Container width="{_n(W2)}" height="{_n(LW)}" color="{CLR[k]}" '
                f'borderRadius="{_n(LW / 2)}" transform="{mat(-45.0)}" '
                f'transformAlignment="TOP_LEFT"></Container></Positioned>')
        elif k == "C":
            S = W2                      # 尺寸取盒宽，能容纳旋转后包围盒（236×167）
            add(f'<Positioned left="{_n(ox - S / 2)}" top="{_n(oy - S / 2)}" '
                f'width="{_n(S)}" height="{_n(S)}">'
                f'<Container width="{_n(W2)}" height="{_n(LW)}" color="{CLR[k]}" '
                f'borderRadius="{_n(LW / 2)}" transform="{mat(-45.0)}" '
                f'transformAlignment="CENTER"></Container></Positioned>')
        else:
            S = 240
            add(f'<Positioned left="{_n(ox - S / 2)}" top="{_n(oy - S / 2)}" '
                f'width="{_n(S)}" height="{_n(S)}">'
                f'<Container width="{_n(W2)}" height="{_n(LW)}" color="{CLR[k]}" '
                f'borderRadius="{_n(LW / 2)}" transform="{mat(-45.0)}" '
                f'transformAlignment="CENTER"></Container></Positioned>')
        add(txt(p2[0] - 96, p2[1] - 26, f"远端 ({p2[0]:.1f},{p2[1]:.1f})",
                size=17, color="#475569"))
        add(txt(p1[0] - 96, p1[1] + 18, f"近端 ({p1[0]:.1f},{p1[1]:.1f})",
                size=17, color="#475569"))

    add("</Stack>")
    add("</Container>")
    add("</Snapshot>")
    dsl = "\n".join(L) + "\n"
    print(f"DSL {len(dsl)} 字符, {dsl.count('<Positioned')} Positioned")

    rec = IO.submit(dsl, label="A07 探针4 · 45° 段定位方式对照",
                    rid="req-a07-probe4-align", dsl_version="probe4-align",
                    kind="draft")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"])
    if rec["error_summary"]:
        print("ERROR", rec["error_summary"])
        print((rec.get("_error_json") or "")[:900])
        return

    src = IO.dirs()[1] / "responses" / f"{rec['request_id']}.body"
    dst = IO.dirs()[1] / "preview" / "probe4-align.png"
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

    print("\n---- 各方案端点落点与垂直厚度（θ=-45°，期望沿向 ±113.14、厚度 ±7.00）----")
    for k, (ox, oy) in ROW.items():
        m = mask(CLR[k])
        ys, xs = np.where(m)
        if not len(xs):
            print(f"  {k}: 无像素")
            continue
        ux, uy = 1 / math.sqrt(2), -1 / math.sqrt(2)     # 沿 NE 方向
        px, py = uy, -ux                                  # 垂直方向
        rx, ry = xs - ox, ys - oy
        along = rx * ux + ry * uy
        perp = rx * px + ry * py
        i_far = int(np.argmax(along))
        i_near = int(np.argmin(along))
        exp_far = (ox + H, oy - H)
        exp_near = (ox - H, oy + H)
        print(f"  {k} {CLR[k]}  {len(xs):5d} px  "
              f"远端 Δ=({xs[i_far] - exp_far[0]:+.2f},{ys[i_far] - exp_far[1]:+.2f}) "
              f"近端 Δ=({xs[i_near] - exp_near[0]:+.2f},{ys[i_near] - exp_near[1]:+.2f})")
        print(f"      沿向 {along.min():+.2f}..{along.max():+.2f}   "
              f"垂直 {perp.min():+.2f}..{perp.max():+.2f}   "
              f"沿向跨度 {along.max() - along.min():.2f}（期望 {2 * H:.2f}）")
    print("preview →", dst.relative_to(IO.ROOT))


if __name__ == "__main__":
    main()
