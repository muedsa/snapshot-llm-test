"""A05 探针：确认用 Transform 旋转矩形画斜线段、空心圆标记、alpha 半透明填色的可行性。

A05 的三张趋势图必须由 DSL 构造折线，而文档里的 39 个标签没有 Path/Line/Polyline
（ClipPath 只做裁剪不做描边），所以斜线段用「Transform 旋转的细矩形」实现。
本探针把每一段的预期几何写进 label，渲染后逐条量像素验证：

    P1→P2：矩形 left/top = (x1, y1 - w/2)，width = len，height = w，
           Transform matrix 列主序 4×4 =
             (cosA, sinA, 0, x1, -sinA, cosA, 0, y1, 0, 0, 1, 0, 0, 0, 0, 1)
           其中 A = atan2(y2-y1, x2-x1)。矩阵必须恰好 16 个值。

启动基准：总任务根（cwd）。用法：python a05_probe.py [preview|final]
"""

from __future__ import annotations

import math
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO  # noqa: E402

PW, PH = 1000, 1040
FA = 'fontFamily="Noto Sans CJK SC"'


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


def rect(x, y, w, h, color, r=0, border=None, radius="0"):
    b = f' border="{border}"' if border else ""
    rr = f' borderRadius="{radius}"' if radius and radius != "0" else ""
    return (f'<Positioned left="{nm(x)}" top="{nm(y)}" width="{nm(w)}" '
            f'height="{nm(h)}"><Container width="{nm(w)}" height="{nm(h)}" '
            f'color="{color}"{rr}{b}></Container></Positioned>')


def line(x1, y1, x2, y2, w=2.0, color="#2563EB"):
    """用 Transform 旋转的矩形画一条精确线段（含端点）。"""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    A = math.atan2(dy, dx)
    c, s = math.cos(A), math.sin(A)
    # 列主序 4×4：(cos, sin, 0, tx, -sin, cos, 0, ty, 0, 0, 1, 0, 0, 0, 0, 1)
    m = (f"({c:.6f},{s:.6f},0,{x1:.3f},{-s:.6f},{c:.6f},0,{y1:.3f},"
         f"0,0,1,0,0,0,0,1)")
    return (f'<Positioned left="0" top="0"><Container width="{nm(L)}" '
            f'height="{nm(w)}"><Transform matrix="{m}"><Container '
            f'width="{nm(L)}" height="{nm(w)}" color="{color}"></Container>'
            f'</Transform></Container></Positioned>')


L: list[str] = []
add = L.append

add(f'<Snapshot background="#F8FAFC" type="png">')
add(f'<Container width="{PW}" height="{PH}" color="#F8FAFC">')
add('<Stack fit="EXPAND" clipBehavior="NONE">')

add(rect(20, 20, PW - 40, PH - 40, "#FFFFFF", radius="12",
         border="1 SOLID #E2E8F0"))
add(txt(40, 36, "A05 探针：Transform 旋转矩形画斜线 / 空心圆 / alpha 填色",
        22, "#0F172A", bold=True))
add(txt(40, 66, "每段 label 写出预期端点；渲染后逐段量像素验证", 20, "#64748B"))

# ---- 1) 水平参考线 1px：left=60 top=110 width=200 height=1
add(txt(40, 100, "① 水平 1px：60,110 → 260,110", 20, "#475569"))
add(line(60, 110, 260, 110, 1.0, "#2563EB"))

# ---- 2) 斜向上 2px：60,200 → 260,160（dx=200 dy=-40）
add(txt(40, 150, "② 斜向上 2px：60,200 → 260,160", 20, "#475569"))
add(line(60, 200, 260, 160, 2.0, "#2563EB"))

# ---- 3) 斜向下 3px：60,260 → 300,320（dx=240 dy=60）
add(txt(40, 250, "③ 斜向下 3px：60,260 → 300,320", 20, "#475569"))
add(line(60, 260, 300, 320, 3.0, "#DB2777"))

# ---- 4) 陡 2px：60,360 → 160,420（dx=100 dy=60）
add(txt(40, 350, "④ 陡 2px：60,360 → 160,420", 20, "#475569"))
add(line(60, 360, 160, 420, 2.0, "#0F766E"))

# ---- 5) 极陡 1.5px：60,460 → 130,520（dx=70 dy=60）
add(txt(40, 450, "⑤ 极陡 1.5px：60,460 → 130,520", 20, "#475569"))
add(line(60, 460, 130, 520, 1.5, "#DC2626"))

# ---- 6) 空心圆（color=transparent + border + borderRadius 大）
add(txt(40, 560, "⑥ 空心圆 12px：圆心 72,586（transparent + 2 SOLID）", 20, "#475569"))
add(rect(66, 580, 12, 12, "transparent", border="2 SOLID #2563EB", radius="10"))
add(txt(120, 574, "实心对照 12px", 20, "#475569"))
add(rect(250, 580, 12, 12, "#2563EB", radius="10"))
# ---- 7) 虚线：5 段 8px 短矩形，间距 6px，起点 400,586
add(txt(40, 620, "⑦ 虚线：400,586 → 448,586（5×8px，间隔 6px）", 20, "#475569"))
for i in range(5):
    add(rect(400 + i * 14, 585, 8, 2, "#64748B"))

# ---- 8) 8 位十六进制 alpha 填色 #DC262614（约 7.8%）铺在白卡上
add(txt(40, 660, "⑧ alpha 填色 #DC262614（7.8% 红）压在白底上：400×60", 20, "#475569"))
add(rect(400, 656, 400, 60, "#DC262614"))
add(txt(410, 726, "期望像素约 (254,238,238)，量得多少见 inspect", 20, "#64748B"))

# ---- 9) alpha 描边 #DC262640
add(txt(40, 770, "⑨ alpha 描边 #DC262640：2 SOLID，矩形 400×40", 20, "#475569"))
add(rect(400, 766, 400, 40, "transparent", border="2 SOLID #DC262640"))

# ---- 10) 长而平缓 2px：60,880 → 940,860（dx=880 dy=-20）
add(txt(40, 830, "⑩ 长缓 2px：60,880 → 940,860", 20, "#475569"))
add(line(60, 880, 940, 860, 2.0, "#2563EB"))

# ---- 11) 三条折线段连成折线（模拟趋势：60,960 → 300,930 → 540,952）
add(txt(40, 900, "⑪ 折线两段：60,960 → 300,930 → 540,952（应可见拐点）", 20, "#475569"))
add(line(60, 960, 300, 930, 2.0, "#2563EB"))
add(line(300, 930, 540, 952, 2.0, "#2563EB"))
add(rect(294, 924, 12, 12, "transparent", border="2 SOLID #2563EB", radius="10"))

# ---- 12) 1px 与 2px 网格线对照（1800 长竖线，模拟共享时间轴）
add(txt(40, 940, "⑫ 竖线 1px #CBD5E1 与 2px #334155 对照，长 80px", 20, "#475569"))
add(line(700, 936, 700, 1016, 1.0, "#CBD5E1"))
add(line(760, 936, 760, 1016, 2.0, "#334155"))
add(line(820, 936, 820, 1016, 1.0, "#EEF2F7"))

add("</Stack>")
add("</Container>")
add("</Snapshot>")

DSL = "\n".join(L) + "\n"

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "v1-preview"
    ver = mode.split("-")[0]
    rec = IO.submit(DSL, label="A05 探针：旋转矩形斜线 / 空心圆 / alpha",
                    rid="req-a05-probe-line", dsl_version=ver, kind="probe")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"])
    if rec.get("error_summary"):
        print("ERROR", rec["error_summary"])
    else:
        prev = IO.dirs()[1] / "preview" / f"{ver}.png"
        prev.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(IO.dirs()[1] / "responses" / f"{rec['request_id']}.body", prev)
        print("preview →", prev.relative_to(IO.ROOT))
