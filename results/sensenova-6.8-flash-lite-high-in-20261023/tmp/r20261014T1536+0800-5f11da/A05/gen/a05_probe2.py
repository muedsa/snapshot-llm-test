"""A05 探针 2：定位为什么探针 1 里所有 Transform 旋转矩形没有画出来。

探针 1（req-a05-probe-line，v1）唯一一次成功渲染出图，但 6 条旋转线段一条都没出现，
画面上只看到 ⑥ 的空心圆/实心圆（12px 蓝点）和 ⑦ 的虚线段。三个嫌疑：
  A) 外层 Positioned 无 width/height → Transform 子树拿到无界约束
  B) 双层 Container 包一层多余
  C) matrix 该写在 Container 上（Container 文档表确有 transform 行），不该用 Transform 包一层

探针 2 画 5 个 200×12 的红块，每个变体只改一处、各占一行，再加一条不旋转的对照；
右上的空白对照区必须留白。渲染后量像素就知道哪一条链是有效的。

启动基准：总任务根（cwd）。用法：python a05_probe2.py <version>
"""

from __future__ import annotations

import math
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO  # noqa: E402

PW, PH = 1240, 1320
FA = 'fontFamily="Noto Sans CJK SC"'
X1, LEN, W = 200.0, 200.0, 12.0
ANG = math.atan2(-40.0, 200.0)
RED, BLUE, GREEN, GRAY, PINK = "#DC2626", "#2563EB", "#0F766E", "#64748B", "#DB2777"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def nm(v: float) -> str:
    f = float(v)
    return str(int(round(f))) if abs(f - round(f)) < 1e-9 else f"{f:.3f}"


def txt(x, y, s, size=20, color="#0F172A", bold=False):
    st = ' fontStyle="BOLD"' if bold else ""
    return (f'<Positioned left="{nm(x)}" top="{nm(y)}"><Text text="{esc(s)}" '
            f'fontSize="{size}"{st} color="{color}" {FA}></Text>'
            f'</Positioned>')


def box(x, y, w, h, color, radius=None, border=None):
    rr = f' borderRadius="{nm(radius)}"' if radius else ""
    b = f' border="{border}"' if border else ""
    return (f'<Positioned left="{nm(x)}" top="{nm(y)}" width="{nm(w)}" '
            f'height="{nm(h)}"><Container width="{nm(w)}" height="{nm(h)}" '
            f'color="{color}"{rr}{b}></Container></Positioned>')


def mat(y1: float, ang: float = ANG, x1: float = X1) -> str:
    """列主序 4×4：(cos, sin, 0, tx, -sin, cos, 0, ty, 0, 0, 1, 0, 0, 0, 0, 1)。"""
    c, s = math.cos(ang), math.sin(ang)
    return (f"({c:.6f},{s:.6f},0,{x1:.3f},{-s:.6f},{c:.6f},0,{y1:.3f},"
            f"0,0,1,0,0,0,0,1)")


def varA(y1):
    """Positioned(left,top) → Container → Transform → Container"""
    return (f'<Positioned left="0" top="0"><Container width="{nm(LEN)}" '
            f'height="{nm(W)}"><Transform matrix="{mat(y1)}"><Container '
            f'width="{nm(LEN)}" height="{nm(W)}" color="{RED}"></Container>'
            f'</Transform></Container></Positioned>')


def varB(y1):
    """Positioned(left,top,width,height) → Container → Transform → Container"""
    return (f'<Positioned left="0" top="0" width="{nm(LEN)}" '
            f'height="{nm(W)}"><Container width="{nm(LEN)}" '
            f'height="{nm(W)}"><Transform matrix="{mat(y1)}"><Container '
            f'width="{nm(LEN)}" height="{nm(W)}" color="{RED}"></Container>'
            f'</Transform></Container></Positioned>')


def varC(y1):
    """Positioned(left,top,width,height) → Transform → Container"""
    return (f'<Positioned left="0" top="0" width="{nm(LEN)}" '
            f'height="{nm(W)}"><Transform matrix="{mat(y1)}"><Container '
            f'width="{nm(LEN)}" height="{nm(W)}" color="{RED}"></Container>'
            f'</Transform></Positioned>')


def varD(y1):
    """matrix 直接写在 Container 上 + Positioned 带尺寸"""
    return (f'<Positioned left="0" top="0" width="{nm(LEN)}" '
            f'height="{nm(W)}"><Container width="{nm(LEN)}" '
            f'height="{nm(W)}" matrix="{mat(y1)}" color="{RED}"></Container>'
            f'</Positioned>')


def varE(y1):
    """matrix 直接写在 Container 上 + Positioned 不带尺寸"""
    return (f'<Positioned left="0" top="0"><Container width="{nm(LEN)}" '
            f'height="{nm(W)}" matrix="{mat(y1)}" color="{RED}"></Container>'
            f'</Positioned>')


def lineC(x1, y1, x2, y2, w, color):
    """用变体 C 画精确线段。"""
    L_ = math.hypot(x2 - x1, y2 - y1)
    m = mat(y1, math.atan2(y2 - y1, x2 - x1), x1)
    return (f'<Positioned left="0" top="0" width="{nm(L_)}" '
            f'height="{nm(w)}"><Transform matrix="{m}"><Container '
            f'width="{nm(L_)}" height="{nm(w)}" color="{color}"></Container>'
            f'</Transform></Positioned>')


L: list[str] = []
add = L.append
add('<Snapshot background="#F8FAFC" type="png">')
add(f'<Container width="{PW}" height="{PH}" color="#F8FAFC">')
add('<Stack fit="EXPAND" clipBehavior="NONE">')

add(box(20, 20, PW - 40, PH - 40, "#FFFFFF", radius=12,
        border="1 SOLID #E2E8F0"))
add(txt(40, 34, "A05 探针 2：Transform 变体定位（matrix 列主序 16 值）",
        22, "#0F172A", bold=True))
add(txt(40, 64, "5 个 200×12 红块，各占一行；期望位置 x 200→400、y 上抬 40",
        20, GRAY))
add(txt(40, 92, f"matrix = {mat(300.0)[:60]}…", 20, "#94A3B8"))

add(txt(40, 268, "A  Positioned(left,top) → Container → Transform → Container", 20, GRAY))
add(varA(300.0))
add(txt(40, 378, "B  Positioned(left,top,width,height) → Container → Transform → Container", 20, GRAY))
add(varB(420.0))
add(txt(40, 488, "C  Positioned(left,top,width,height) → Transform → Container", 20, GRAY))
add(varC(540.0))
add(txt(40, 598, "D  matrix 直接写在 Container 上 + Positioned 带尺寸", 20, GRAY))
add(varD(660.0))
add(txt(40, 708, "E  matrix 直接写在 Container 上 + Positioned 不带尺寸", 20, GRAY))
add(varE(780.0))
add(txt(40, 818, "F  对照：不旋转，同样 200×12 直接画在 (200,900)", 20, GREEN))
add(box(X1, 900 - W / 2, LEN, W, GREEN))

add(txt(40, 960, "空白对照区（700,300）460×300，必须保持纯白 #FFFFFF", 20, GRAY))
add(box(700, 300, 460, 300, "#FFFFFF", radius=8, border="1 SOLID #CBD5E1"))

add(txt(40, 1000, "G  变体 C 水平 2px：200,1050 → 400,1050", 20, GRAY))
add(txt(40, 1030, "H  变体 C 斜线 3px：200,1090 → 440,1150", 20, GRAY))
add(txt(40, 1060, "I  变体 C 竖线 1px #CBD5E1：700,1010 → 700,1090", 20, GRAY))
add(lineC(200, 1050, 400, 1050, 2.0, BLUE))
add(lineC(200, 1090, 440, 1150, 3.0, PINK))
add(lineC(700, 1010, 700, 1090, 1.0, "#CBD5E1"))

add(txt(40, 1160, "J  空心圆 12px（transparent + 2 SOLID + borderRadius 10）：圆心 72,1186", 20, GRAY))
add(box(66, 1180, 12, 12, "transparent", border="2 SOLID #2563EB", radius=10))
add(box(250, 1180, 12, 12, "#2563EB", radius=10))
add(txt(290, 1174, "实心对照", 20, GRAY))
add(txt(420, 1174, "虚线 5×8px 间隔 6px：420,1189", 20, GRAY))
for i in range(5):
    add(box(420 + i * 14, 1188, 8, 2, GRAY))

add(txt(40, 1210, "K  alpha 填色 #DC262614 铺白卡：700,1206 400×60（期望 ≈(254,238,238)）", 20, GRAY))
add(box(700, 1206, 400, 60, "#DC262614"))

add(txt(40, 1290, "L  alpha 描边 #DC262640：2 SOLID，矩形 400×40", 20, GRAY))
add(box(400, 1236, 400, 40, "transparent", border="2 SOLID #DC262640"))

add("</Stack>")
add("</Container>")
add("</Snapshot>")

DSL = "\n".join(L) + "\n"

if __name__ == "__main__":
    ver = sys.argv[1] if len(sys.argv) > 1 else "v2-preview"
    rec = IO.submit(DSL, label="A05 探针 2：Transform 变体定位",
                    rid="req-a05-probe2-line", dsl_version=ver, kind="probe")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"])
    if rec.get("error_summary"):
        print("ERROR", rec["error_summary"])
    else:
        prev = IO.dirs()[1] / "preview" / f"{ver}.png"
        prev.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(IO.dirs()[1] / "responses" / f"{rec['request_id']}.body", prev)
        print("preview →", prev.relative_to(IO.ROOT))
