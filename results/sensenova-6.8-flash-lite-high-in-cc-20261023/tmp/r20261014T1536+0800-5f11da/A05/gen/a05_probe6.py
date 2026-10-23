"""A05 探针 6：小数点「.」为什么不被渲染。

v2-preview 的像素实测：表内 "19.2" 在列 604–610（"9" 与 "2" 之间）行 755–765
全部为纯白 255，即小数点字形完全缺失，"19.2" 被画成 "192"。
嫌疑：
  (a) fontFeatures="+tnum=2" 使 CJK 字体把 "." 当作不可见字形
  (b) 18px 下 "." 光栅化后低于可见阈值（但探针实测是纯白，不是浅灰）
  (c) 字符串里的 "." 被 DSL 解析层吃掉
本探针把三者分开：同一字符串、不同 fontFeatures / fontSize / 字体，各占一行，
右侧量像素列剖面判定哪一行真的画出了句点。

启动基准：总任务根（cwd）。用法：python a05_probe6.py <version>
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO  # noqa: E402

PW, PH = 1160, 1240
FA = 'fontFamily="Noto Sans CJK SC"'
FONTSRC = "Noto Sans CJK SC"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size, color="#0F172A", fa=FONTSRC, feat="", bold=False):
    st = ' fontStyle="BOLD"' if bold else ""
    ff = f' fontFeatures="{feat}"' if feat else ""
    return (f'<Positioned left="{x}" top="{y}"><Text text="{esc(s)}" '
            f'fontSize="{size}"{st}{ff} color="{color}" '
            f'fontFamily="{fa}"></Text></Positioned>')


L: list[str] = []
add = L.append
add('<Snapshot background="#FFFFFF" type="png">')
add(f'<Container width="{PW}" height="{PH}" color="#FFFFFF">')
add('<Stack fit="EXPAND" clipBehavior="NONE">')

add(txt(30, 20, "A05 探针 6：小数点 . 的渲染", 26, "#0F172A", feat="+tnum=2",
        bold=True))
add(txt(30, 58, "每行左侧文字相同（19.2 / 0.2 / −0.8），右侧量列剖面确认句点是否被画出",
        20, "#64748B"))

# (变体标签, 文字属性) —— 文字一律 "19.2   0.2   −0.8"
CASES = [
    ("A  18px + tnum=2（当前用法）",
     dict(size=26, feat="+tnum=2")),
    ("B  18px 不带 fontFeatures",
     dict(size=26, feat="")),
    ("C  18px + tnum=1",
     dict(size=26, feat="+tnum=1")),
    ("D  18px + tnum（无 =）",
     dict(size=26, feat="tnum")),
    ("E  22px + tnum=2",
     dict(size=30, feat="+tnum=2")),
    ("F  26px + tnum=2",
     dict(size=34, feat="+tnum=2")),
    ("G  34px + tnum=2",
     dict(size=44, feat="+tnum=2")),
    ("H  18px + tnum=2 粗体",
     dict(size=26, feat="+tnum=2", bold=True)),
    ("I  18px 半角句点 + 空格 padding 对照",
     dict(size=26, feat="+tnum=2")),
    ("J  18px 用全角句点．",
     dict(size=26, feat="+tnum=2")),
    ("K  18px 用全角逗号，",
     dict(size=26, feat="+tnum=2")),
    ("L  18px 用下标式写法 19⁄ 100 无效对照",
     dict(size=26, feat="+tnum=2")),
]
SAMPLE = "19.2     0.2     −0.8"
FULLW = "19．2     0．2     −0．8"
COMMA = "19，2     0，2     −0，8"

y = 104
for i, (label, kw) in enumerate(CASES):
    add(txt(30, y, label, 20, "#64748B"))
    s = SAMPLE
    if label.startswith("J"):
        s = FULLW
    elif label.startswith("K"):
        s = COMMA
    add(txt(430, y + (kw["size"] - 26) // 2, s, **kw))
    y += 78

add(txt(30, y + 8, "参照：无 fontFeatures 的 18px '19.2'", 20, "#94A3B8"))
add(txt(30, y + 40, "19.2", 26, "#DB2777"))
add(txt(30, y + 82, "参照：26px + tnum=2 '19.2'", 20, "#94A3B8"))
add(txt(30, y + 114, "19.2", 26, "#DB2777", feat="+tnum=2"))

add("</Stack>")
add("</Container>")
add("</Snapshot>")

DSL = "\n".join(L) + "\n"

if __name__ == "__main__":
    ver = sys.argv[1] if len(sys.argv) > 1 else "v6-preview"
    rec = IO.submit(DSL, label="A05 探针 6：小数点渲染",
                    rid="req-a05-probe6-dot", dsl_version=ver, kind="probe")
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
