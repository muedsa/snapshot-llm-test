"""A05 探针 3：Transform 被解析成 16 值却不生效，定位是格式问题还是写法问题。

探针 2 的量像素结果：5 个 200×12 红块全部落在原点 (0,0)（2400 个像素 = 恰好 200×12 一块），
即 Transform matrix 被解析器接受（不再报「must contain 16 values」）却没有生效。
嫌疑：
  (1) 浮点写法 0.980581 / 200.000 不被接受 → 用整型矩阵验证
  (2) 子节点必须是 SizedBox（文档示例用的是 <SizedBox …/>）
  (3) 缺 origin / alignment 时 matrix 被当作恒等
  (4) Container 上的属性名是 transform= 不是 matrix=（文档表：Container 行写的是 transform）

7 个 140×60 色块各自有唯一的目标灰框（左列 140、右列 600；行 200/380/560/740），
量像素即可判定哪个变体真正生效。

启动基准：总任务根（cwd）。用法：python a05_probe3.py <version>
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO  # noqa: E402

PW, PH = 1100, 900
FA = 'fontFamily="Noto Sans CJK SC"'
BLUE, GRAY, GREEN = "#2563EB", "#64748B", "#0F766E"
BW, BH = 140, 60
COL = (140, 600)
ROW = (200, 380, 560, 740)
MINT = lambda x, y: f"(1,0,0,0,0,1,0,0,0,0,1,0,{x},{y},0,1)"     # 整型平移
MFLT = ("(0.980581,-0.196116,0,140.000,0.196116,0.980581,0,560.000,"
        "0,0,1,0,0,0,0,1)")                                        # 浮点 + 旋转


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


def v0():  # 整型 matrix + SizedBox 子 + origin + alignment
    return ('<Positioned left="0" top="0"><Transform matrix="%s" '
            'origin="(2,3)" alignment="CENTER"><SizedBox width="%d" height="%d" '
            'color="%s" /></Transform></Positioned>' % (MINT(*COL[0:1] + ROW[0:1]),
                                                        BW, BH, BLUE))


def v1():  # 整型 matrix + Container 子 + origin + alignment
    return ('<Positioned left="0" top="0"><Transform matrix="%s" '
            'origin="(2,3)" alignment="CENTER"><Container width="%d" height="%d" '
            'color="%s"></Container></Transform></Positioned>'
            % (MINT(COL[1], ROW[0]), BW, BH, BLUE))


def v2():  # 整型 matrix + Container 子 + 只 alignment
    return ('<Positioned left="0" top="0"><Transform matrix="%s" '
            'alignment="CENTER"><Container width="%d" height="%d" '
            'color="%s"></Container></Transform></Positioned>'
            % (MINT(COL[0], ROW[1]), BW, BH, BLUE))


def v3():  # 整型 matrix + Container 子 + origin/alignment 都不给
    return ('<Positioned left="0" top="0"><Transform matrix="%s">'
            '<Container width="%d" height="%d" color="%s"></Container>'
            '</Transform></Positioned>' % (MINT(COL[1], ROW[1]), BW, BH, BLUE))


def v4():  # 浮点矩阵（含旋转）+ Container 子 + origin + alignment
    return ('<Positioned left="0" top="0"><Transform matrix="%s" '
            'origin="(2,3)" alignment="CENTER"><Container width="%d" height="%d" '
            'color="%s"></Container></Transform></Positioned>'
            % (MFLT, BW, BH, BLUE))


def v5():  # Container 用 transform= 属性名
    return ('<Positioned left="0" top="0"><Container width="%d" height="%d" '
            'transform="%s" color="%s"></Container></Positioned>'
            % (BW, BH, MINT(COL[1], ROW[2]), BLUE))


def v6():  # 对照：Positioned 直接定位，无 Transform
    return ('<Positioned left="%d" top="%d" width="%d" height="%d">'
            '<Container width="%d" height="%d" color="%s"></Container>'
            '</Positioned>' % (COL[0], ROW[3], BW, BH, BW, BH, GREEN))


L: list[str] = []
add = L.append
add('<Snapshot background="#F8FAFC" type="png">')
add(f'<Container width="{PW}" height="{PH}" color="#F8FAFC">')
add('<Stack fit="EXPAND" clipBehavior="NONE">')

add(card(20, 20, PW - 40, PH - 40, "#FFFFFF", "1 SOLID #E2E8F0", 12))
add(txt(40, 34, "A05 探针 3：Transform 为何不生效（目标框 140×60）", 22,
        "#0F172A", bold=True))
add(txt(40, 64, "灰框是各变体的期望落点；蓝块 = Transform 生效，绿块 = V6 无 Transform 对照",
        20, GRAY))

# 目标灰框（先画，变体画在其上）
for x in COL:
    for y in ROW:
        add(card(x, y, BW, BH, "#F1F5F9", "1 SOLID #CBD5E1"))

add(txt(30, 168, "V0 整型 matrix + SizedBox 子 + origin + alignment", 20, GRAY))
add(txt(490, 168, "V1 整型 matrix + Container 子 + origin + alignment", 20, GRAY))
add(txt(30, 348, "V2 整型 matrix + Container 子 + 只给 alignment", 20, GRAY))
add(txt(490, 348, "V3 整型 matrix + Container 子 + 都不给", 20, GRAY))
add(txt(30, 528, "V4 浮点矩阵（含旋转）+ Container 子 + origin + alignment", 20, GRAY))
add(txt(490, 528, "V5 Container 属性名 transform=（不是 matrix=）", 20, GRAY))
add(txt(30, 708, "V6 对照：Positioned 直接定位，无 Transform（绿）", 20, "#0F766E"))

add(v0())
add(v1())
add(v2())
add(v3())
add(v4())
add(v5())
add(v6())

add(txt(30, 830, "M_INT=%s" % MINT(140, 200), 20, "#94A3B8"))
add(txt(30, 856, "M_FLT=%s" % MFLT, 20, "#94A3B8"))

add("</Stack>")
add("</Container>")
add("</Snapshot>")

DSL = "\n".join(L) + "\n"

if __name__ == "__main__":
    ver = sys.argv[1] if len(sys.argv) > 1 else "v3-preview"
    rec = IO.submit(DSL, label="A05 探针 3：Transform 生效条件定位",
                    rid="req-a05-probe3-tx", dsl_version=ver, kind="probe")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"])
    if rec.get("error_summary"):
        print("ERROR", rec["error_summary"])
    else:
        prev = IO.dirs()[1] / "preview" / f"{ver}.png"
        prev.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(IO.dirs()[1] / "responses" / f"{rec['request_id']}.body", prev)
        print("preview →", prev.relative_to(IO.ROOT))
