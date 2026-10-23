"""A05 探针 7：小数点「.」在哪个字号阈值以下不再被画出。

探针 6 的标签写的是 18px，但 CASES 实际都传了 size=26，所以那次没有真正测到 18px。
v2-preview 的像素实测（18px，表格 "19.2"）：
  列 560..624 / 行 755..765 的灰度图显示 "1" / "9" / "2" 三段墨迹，
  而 "9"（列 602–609）与 "2"（列 617–622）之间的列 610–616 为纯白 255，
  即 18px 下句点完全缺失，"19.2" 被画成了 "192"。
探针 6 在 26px 下句点存在（列剖面里 (40,42) / (105,107) 这样的 3px 短段）。
所以阈值在 18 与 26 之间。本探针把 16..26 逐个字号各画一次，并与
「带 tnum=2 / 不带 tnum」交叉，右侧用像素剖面判定句点是否存在。

启动基准：总任务根（cwd）。用法：python a05_probe7.py <version>
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO  # noqa: E402

PW, PH = 1000, 1500
FONTSRC = "Noto Sans CJK SC"

SAMPLES = [("19.2", "T=19.2"), ("−0.8", "P=−0.8"), ("0.5", "P=0.5")]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size, color="#0F172A", feat="", bold=False, fa=FONTSRC):
    st = ' fontStyle="BOLD"' if bold else ""
    ff = f' fontFeatures="{feat}"' if feat else ""
    return (f'<Positioned left="{x}" top="{y}"><Text text="{esc(s)}" '
            f'fontSize="{size}"{st}{ff} color="{color}" '
            f'fontFamily="{fa}"></Text></Positioned>')


def nm(v):
    f = float(v)
    return str(int(round(f))) if abs(f - round(f)) < 1e-9 else f"{f:.2f}"


L: list[str] = []
add = L.append
add('<Snapshot background="#F8FAFC" type="png">')
add(f'<Container width="{PW}" height="{PH}" color="#F8FAFC">')
add('<Stack fit="EXPAND" clipBehavior="NONE">')

add(txt(30, 20, "A05 探针 7：句点渲染的字号阈值", 28, "#0F172A", feat="+tnum=2",
        bold=True))
add(txt(30, 58, "每行右侧同一串文字（19.2 / −0.8 / 0.5），仅改 fontSize 与 fontFeatures；"
                "左侧标签写明真实字号", 20, "#64748B"))
add(txt(30, 86, "判定方法：量该行像素列剖面，「19.2」应有 4 段墨迹（1 / 9 / . / 2）；"
                "只有 3 段即句点缺失", 20, "#64748B"))

# 尺寸扫描：真实字号，逐个测
SIZES = [16, 17, 18, 19, 20, 21, 22, 23, 24, 26]
FEATS = [("+tnum=2", "tnum=2"), ("", "无 tnum")]

y = 128
row_h = 56
row_meta = []
for size in SIZES:
    for feat, fname in FEATS:
        add(txt(30, y + (26 - size) // 2 + 2, f"fontSize={size}  {fname}", 20,
                "#64748B"))
        for j, (s, _) in enumerate(SAMPLES):
            add(txt(500 + j * 150, y, s, size, "#0F172A", feat=feat))
        row_meta.append((size, fname, y))
        y += row_h

add(txt(30, y + 10, "参照：18px 句点位置若缺失，整行读作 192 / −08 / 05", 20,
        "#94A3B8"))

add("</Stack>")
add("</Container>")
add("</Snapshot>")

DSL = "\n".join(L) + "\n"

# 供量像素脚本复用的行元数据：(字号, 变体名, 文本顶部像素)
ROW_META = row_meta


if __name__ == "__main__":
    ver = sys.argv[1] if len(sys.argv) > 1 else "v7-preview"
    rec = IO.submit(DSL, label="A05 探针 7：句点字号阈值",
                    rid="req-a05-probe7-size", dsl_version=ver, kind="probe")
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
    print("\n行元数据（x0=500，每个样本间隔 150）：")
    for size, fname, ty in ROW_META:
        print(f"  size={size:2d} {fname:8s} top={ty}")
