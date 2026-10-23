"""A05 探针 5：确认矩阵是否支持旋转；同时验证「像素阶梯法」画斜线可行。

探针 4 的量像素结论（700×1000，目标框 140×60，蓝块 33202 px）：
  N1 整型负号平移            → 生效 (140,279)×(200,259)
  N2 全正浮点 + 旋转         → 完全不画（全图找不到蓝块）
  N3 正浮点平移 660.5/200.5  → 生效 (661,799)×(201,259)
  N4 负号浮点 + 旋转         → 完全不画
  N5 负号 + 浮点平移         → 生效 (400,538)×(420,478)
  N6 整型平移                → 生效 (660,799)×(420,479)
负号可用、浮点可用、平移可用；**唯一失败的都是带旋转（cos≠1 或 sin≠0）的矩阵**。

所以本探针分两部分：
  ① R1–R5 再验旋转（45°/90°/错行序/Container transform=），确认是不是根本不支持旋转；
  ② S1 用「像素阶梯法」（纯 Positioned + Container，1–3px 宽的竖条按 x 插值取 y 包络）
     画一条 300px 长、上升 40px 的斜线，验证不依赖旋转的替代方案。

启动基准：总任务根（cwd）。用法：python a05_probe5.py <version>
"""

from __future__ import annotations

import math
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO  # noqa: E402

PW, PH = 1000, 800
FA = 'fontFamily="Noto Sans CJK SC"'
BLUE, GRAY, GREEN = "#2563EB", "#64748B", "#0F766E"
BW, BH = 140, 60
S45 = 0.7071067811865476

CASES = [
    ("R1 45° 列主序",
     "0", "0",
     f"({S45},{S45},0,140,-{S45},{S45},0,200,0,0,1,0,0,0,0,1)", (140, 200)),
    ("R2 45° 行主序",
     "0", "0",
     f"({S45},-{S45},0,420,{S45},{S45},0,200,0,0,1,0,0,0,0,1)", (420, 200)),
    ("R3 90° 列主序",
     "0", "0",
     "(0,1,0,700,-1,0,0,200,0,0,1,0,0,0,0,1)", (700, 200)),
    ("R4 45° 列主序 + Container transform=",
     "0", "0",
     f"({S45},{S45},0,140,-{S45},{S45},0,420,0,0,1,0,0,0,0,1)", (140, 420)),
    ("R5 仅水平错切 shear",
     "0", "0",
     "(1,0,0,700,0.5,1,0,420,0,0,1,0,0,0,0,1)", (700, 420)),
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size=20, color="#0F172A", bold=False):
    st = ' fontStyle="BOLD"' if bold else ""
    return (f'<Positioned left="{x}" top="{y}"><Text text="{esc(s)}" '
            f'fontSize="{size}"{st} color="{color}" {FA}></Text>'
            f'</Positioned>')


def card(x, y, w, h, color, border, r=10):
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
            f'<Container width="{w}" height="{h}" color="{color}" '
            f'borderRadius="{r}" border="{border}"></Container></Positioned>')


def nm(v):
    f = float(v)
    return str(int(round(f))) if abs(f - round(f)) < 1e-9 else f"{f:.2f}"


def variant(pl, pt, m, via_container=False):
    if via_container:
        return (f'<Positioned left="{pl}" top="{pt}"><Container width="{BW}" '
                f'height="{BH}" transform="{m}" color="{BLUE}"></Container>'
                f'</Positioned>')
    return (f'<Positioned left="{pl}" top="{pt}"><Transform matrix="{m}">'
            f'<Container width="{BW}" height="{BH}" color="{BLUE}">'
            f'</Container></Transform></Positioned>')


def ladder(x1, y1, x2, y2, step=3, color="#0F766E"):
    """像素阶梯法：按 x 步进取斜线的 y 包络，用竖条拼出斜线。"""
    out = []
    n = max(1, int(math.ceil(abs(x2 - x1) / step)))
    for i in range(n):
        a = x1 + (x2 - x1) * i / n
        b = x1 + (x2 - x1) * (i + 1) / n
        ya, yb = y1 + (y2 - y1) * i / n, y1 + (y2 - y1) * (i + 1) / n
        top, h = min(ya, yb), abs(yb - ya)
        w = b - a
        out.append(f'<Positioned left="{nm(a)}" top="{nm(top - 1)}" '
                   f'width="{nm(w)}" height="{nm(h + 2)}">'
                   f'<Container width="{nm(w)}" height="{nm(h + 2)}" '
                   f'color="{color}"></Container></Positioned>')
    return out


L: list[str] = []
add = L.append
add('<Snapshot background="#F8FAFC" type="png">')
add(f'<Container width="{PW}" height="{PH}" color="#F8FAFC">')
add('<Stack fit="EXPAND" clipBehavior="NONE">')

add(card(20, 20, PW - 40, PH - 40, "#FFFFFF", "1 SOLID #E2E8F0", 12))
add(txt(40, 34, "A05 探针 5：矩阵是否支持旋转 + 阶梯法画斜线", 22,
        "#0F172A", bold=True))
add(txt(40, 64, "灰框为各变体期望落点（140×60）；旋转生效时框会略大或倾斜",
        20, GRAY))

for label, pl, pt, m, (tx, ty) in CASES:
    add(card(tx, ty, BW, BH, "#F1F5F9", "1 SOLID #CBD5E1"))
    add(txt(tx - 12, ty - 30, f"{label} → 目标 ({tx},{ty})", 20, GRAY))
for label, pl, pt, m, _ in CASES:
    add(variant(pl, pt, m, via_container=(label.startswith("R4"))))

add(txt(40, 560, "S1 阶梯法：(140,660) → (440,620)，3px 步进取 y 包络，绿色", 20, GREEN))
for s in ladder(140, 660, 440, 620):
    add(s)
add(txt(560, 560, "S2 阶梯法：(560,700) → (860,640)，45° 附近的陡线", 20, GREEN))
for s in ladder(560, 700, 860, 640):
    add(s)

add(txt(40, 740, "参照：矩阵元素顺序 (cos,sin,0,tx,-sin,cos,0,ty,0,0,1,0,0,0,0,1)",
        20, "#94A3B8"))

add("</Stack>")
add("</Container>")
add("</Snapshot>")

DSL = "\n".join(L) + "\n"

if __name__ == "__main__":
    ver = sys.argv[1] if len(sys.argv) > 1 else "v5-preview"
    rec = IO.submit(DSL, label="A05 探针 5：旋转支持与阶梯法",
                    rid="req-a05-probe5-rot", dsl_version=ver, kind="probe")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"])
    if rec.get("error_summary"):
        print("ERROR", rec["error_summary"])
    else:
        prev = IO.dirs()[1] / "preview" / f"{ver}.png"
        prev.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(IO.dirs()[1] / "responses" / f"{rec['request_id']}.body", prev)
        print("preview →", prev.relative_to(IO.ROOT))
