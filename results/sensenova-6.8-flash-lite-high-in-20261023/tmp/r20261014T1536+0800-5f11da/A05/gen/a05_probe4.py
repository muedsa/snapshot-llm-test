"""A05 探针 4：Transform 矩阵到底接受哪些数值写法。

探针 3 的量像素结论（900×1100，目标框 140×60）：
  V1 整型 matrix + Container 子 + origin + alignment → 生效，(600,739)×(200,259)
  V2 整型 matrix + Container 子 + 只 alignment       → 生效，(140,279)×(380,439)
  V3 整型 matrix + Container 子 + 都不给             → 生效，(600,739)×(380,439)
  V5 Container 属性名 transform=（整型）             → 生效，(600,739)×(560,619)
  V0 SizedBox 子节点                                  → 不生效
  V4 浮点矩阵（含 -0.196116）                          → 不生效
探针 2 的 5 个矩阵全部带负值（-0.196116），探针 3 里唯一带负值的 V4 也失败。
所以嫌疑集中在「负号」或「浮点写法」，本探针把两者分开验证。

启动基准：总任务根（cwd）。用法：python a05_probe4.py <version>
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO  # noqa: E402

PW, PH = 1000, 700
FA = 'fontFamily="Noto Sans CJK SC"'
BLUE, GRAY = "#2563EB", "#64748B"
BW, BH = 140, 60

# (标签, Positioned left, top, matrix, 目标左上角)
CASES = [
    ("N1 整型负号平移",
     "280", "400", "(1,0,0,0,0,1,0,0,0,0,1,0,-140,-200,0,1)", (140, 200)),
    ("N2 全正浮点 + 旋转",
     "0", "0",
     "(0.98,0.19,0,400,0,0.99,0,200,0,0,1,0,0,0,0,1)", (400, 200)),
    ("N3 正浮点平移",
     "0", "0", "(1,0,0,0,0,1,0,0,0,0,1,0,660.5,200.5,0,1)", (660, 200)),
    ("N4 负号浮点 + 旋转（探针 2 同款）",
     "0", "0",
     "(0.980581,-0.196116,0,140,0.196116,0.980581,0,420,0,0,1,0,0,0,0,1)",
     (140, 420)),
    ("N5 负号 + 浮点平移",
     "600", "620", "(1,0,0,0,0,1,0,0,0,0,1,0,-200.5,-200.5,0,1)", (400, 420)),
    ("N6 整型平移（对照）",
     "0", "0", "(1,0,0,0,0,1,0,0,0,0,1,0,660,420,0,1)", (660, 420)),
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


def variant(pl, pt, m):
    return (f'<Positioned left="{pl}" top="{pt}"><Transform matrix="{m}">'
            f'<Container width="{BW}" height="{BH}" color="{BLUE}">'
            f'</Container></Transform></Positioned>')


L: list[str] = []
add = L.append
add('<Snapshot background="#F8FAFC" type="png">')
add(f'<Container width="{PW}" height="{PH}" color="#F8FAFC">')
add('<Stack fit="EXPAND" clipBehavior="NONE">')

add(card(20, 20, PW - 40, PH - 40, "#FFFFFF", "1 SOLID #E2E8F0", 12))
add(txt(40, 34, "A05 探针 4：矩阵数值写法（负号 / 浮点 / 旋转）", 22,
        "#0F172A", bold=True))
add(txt(40, 64, "灰框为各变体期望落点（140×60）；蓝块出现即该写法生效，"
                "旋转变体框会略大于 140×60", 20, GRAY))

for label, pl, pt, m, (tx, ty) in CASES:
    add(card(tx, ty, BW, BH, "#F1F5F9", "1 SOLID #CBD5E1"))
    add(txt(tx - 12, ty - 30, f"{label} → 目标 ({tx},{ty})", 20, GRAY))
add(variant(CASES[0][1], CASES[0][2], CASES[0][3]))
add(variant(CASES[1][1], CASES[1][2], CASES[1][3]))
add(variant(CASES[2][1], CASES[2][2], CASES[2][3]))
add(variant(CASES[3][1], CASES[3][2], CASES[3][3]))
add(variant(CASES[4][1], CASES[4][2], CASES[4][3]))
add(variant(CASES[5][1], CASES[5][2], CASES[5][3]))

add(txt(40, 560, "matrix 均为列主序 16 值：(cos,sin,0,tx,-sin,cos,0,ty,0,0,1,0,0,0,0,1)",
        20, "#94A3B8"))

add("</Stack>")
add("</Container>")
add("</Snapshot>")

DSL = "\n".join(L) + "\n"

if __name__ == "__main__":
    ver = sys.argv[1] if len(sys.argv) > 1 else "v4-preview"
    rec = IO.submit(DSL, label="A05 探针 4：矩阵数值写法",
                    rid="req-a05-probe4-mat", dsl_version=ver, kind="probe")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"])
    if rec.get("error_summary"):
        print("ERROR", rec["error_summary"])
    else:
        prev = IO.dirs()[1] / "preview" / f"{ver}.png"
        prev.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(IO.dirs()[1] / "responses" / f"{rec['request_id']}.body", prev)
        print("preview →", prev.relative_to(IO.ROOT))
