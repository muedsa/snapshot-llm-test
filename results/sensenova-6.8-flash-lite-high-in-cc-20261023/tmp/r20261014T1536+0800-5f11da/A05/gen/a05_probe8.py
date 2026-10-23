"""A05 探针 8：句点缺失到底是「字号」还是「Container 容器」造成的。

两个探针已经把范围夹住了：
  探针 7：裸 <Text> 18px，「19.2」列剖面 4 段 [8|8|3|8] —— 句点在（3px 宽）；
          16..26px 全部都有句点，所以不是字号阈值问题。
  v2-preview：表格单元格与纵轴刻度用的是 txt_box =
          Positioned > Container(width,height,color=transparent,alignment) > Text，
          容器高度恰好等于字号 18。像素实测「19.2」在 "9" 与 "2" 之间、
          「18.0」在 "8" 与 "0" 之间全为纯白 —— 句点丢失。
所以嫌疑是「容器」这个包装层。本探针固定同一串「19.2」，只变容器高度 /
对齐方式 / 有无 alignment / 有无 fontFeatures。

版式刻意做成「标签一行、样本独占下一行」，避免长标签与样本文字重叠污染剖面：
  量像素时只取样本行的 cols 20..260。

启动基准：总任务根（cwd）。用法：python a05_probe8.py <version>
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO  # noqa: E402

PW, PH = 1000, 1230
FONTSRC = "Noto Sans CJK SC"
TN = "+tnum=2"
S = "19.2"
DY = 27          # 样本行相对标签行的下移量


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size=18, color="#0F172A", feat=True):
    ff = f' fontFeatures="{TN}"' if feat else ""
    return (f'<Positioned left="{x}" top="{y}"><Text text="{esc(s)}" '
            f'fontSize="{size}"{ff} color="{color}" '
            f'fontFamily="{FONTSRC}"></Text></Positioned>')


def box(x, y, w, h, size=18, align=None, feat=True):
    """Positioned > Container(w,h,color=transparent[,alignment]) > Text —— 与 txt_box 一致。"""
    ff = f' fontFeatures="{TN}"' if feat else ""
    al = f' alignment="{align}"' if align else ""
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
            f'<Container width="{w}" height="{h}" color="transparent"{al}>'
            f'<Text text="{esc(S)}" fontSize="{size}"{ff} color="#0F172A" '
            f'fontFamily="{FONTSRC}"></Text></Container></Positioned>')


# (标签, 渲染函数(y) -> Positioned 字符串)
CASES = [
    ("A  裸 Text 18px（无容器）",
     lambda y: txt(30, y, S)),
    ("B  容器 130×18  BOTTOM_RIGHT  18px   ← 报告现状",
     lambda y: box(30, y, 130, 18, 18, "BOTTOM_RIGHT")),
    ("C  容器 130×18  BOTTOM_LEFT   18px",
     lambda y: box(30, y, 130, 18, 18, "BOTTOM_LEFT")),
    ("D  容器 130×18  CENTER        18px",
     lambda y: box(30, y, 130, 18, 18, "CENTER")),
    ("E  容器 130×18  无 alignment  18px",
     lambda y: box(30, y, 130, 18, 18, None)),
    ("F  容器 130×20  BOTTOM_RIGHT  18px",
     lambda y: box(30, y, 130, 20, 18, "BOTTOM_RIGHT")),
    ("G  容器 130×22  BOTTOM_RIGHT  18px",
     lambda y: box(30, y, 130, 22, 18, "BOTTOM_RIGHT")),
    ("H  容器 130×26  BOTTOM_RIGHT  18px",
     lambda y: box(30, y, 130, 26, 18, "BOTTOM_RIGHT")),
    ("I  容器 130×30  BOTTOM_RIGHT  18px",
     lambda y: box(30, y, 130, 30, 18, "BOTTOM_RIGHT")),
    ("J  容器 60×18   BOTTOM_RIGHT  18px（窄容器）",
     lambda y: box(30, y, 60, 18, 18, "BOTTOM_RIGHT")),
    ("K  容器 130×18  BOTTOM_RIGHT  19px",
     lambda y: box(30, y, 130, 18, 19, "BOTTOM_RIGHT")),
    ("L  容器 130×22  BOTTOM_RIGHT  19px",
     lambda y: box(30, y, 130, 22, 19, "BOTTOM_RIGHT")),
    ("M  容器 130×18  BOTTOM_RIGHT  18px  无 tnum",
     lambda y: box(30, y, 130, 18, 18, "BOTTOM_RIGHT", feat=False)),
    ("N  容器 130×20  BOTTOM_RIGHT  18px  无 tnum",
     lambda y: box(30, y, 130, 20, 18, "BOTTOM_RIGHT", feat=False)),
]


L: list[str] = []
add = L.append
add('<Snapshot background="#F8FAFC" type="png">')
add(f'<Container width="{PW}" height="{PH}" color="#F8FAFC">')
add('<Stack fit="EXPAND" clipBehavior="NONE">')

add(txt(30, 20, "A05 探针 8：句点缺失 —— 字号还是容器？", 28, "#0F172A"))
add(txt(30, 58, "每个案例标签占一行，样本「19.2」独占下一行（避免标签污染剖面）；"
                "16..26px 裸 Text 句点均在，故本探针只变容器", 20, "#64748B"))
add(txt(30, 86, "判据：量样本行像素列剖面，有句点应为 4 段墨迹（1 / 9 / . / 2）",
        20, "#64748B"))

y = 122
row_h = 64
meta = []
for label, fn in CASES:
    add(txt(30, y, label, 19, "#475569"))
    add(fn(y + DY))
    meta.append((label, y + DY))
    y += row_h

add(txt(30, y + 8, f"注：样本行 y = 标签行 y + {DY}；样本容器左端固定 x=30", 20,
        "#94A3B8"))

add("</Stack>")
add("</Container>")
add("</Snapshot>")

DSL = "\n".join(L) + "\n"
ROWS = meta


if __name__ == "__main__":
    ver = sys.argv[1] if len(sys.argv) > 1 else "v8-preview"
    rec = IO.submit(DSL, label="A05 探针 8：句点缺失归因",
                    rid="req-a05-probe8-box", dsl_version=ver, kind="probe")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"])
    if rec.get("error_summary"):
        print("ERROR", rec["error_summary"])
    else:
        prev = IO.dirs()[1] / "preview" / f"{ver}.png"
        prev.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(IO.dirs()[1] / "responses" / f"{rec['request_id']}.body",
                        prev)
        print("preview →", prev.relative_to(IO.ROOT))
    print("\n样本行元数据（左端 x=30）：")
    for label, sy in ROWS:
        print(f"  top={sy:4d}  {label}")
