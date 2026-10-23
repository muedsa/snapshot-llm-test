"""A04 探针：一次请求同时验证四件事，避免在 200 个元素上返工。

A) fontFamily="Noto Sans CJK SC" 能否渲染中文（不是豆腐块）
B) Text 的 textAlign 是否生效（Text 会 shrink-wrap，预期不生效）
C) Container alignment="RIGHT"/"CENTER" 是否把 Text 对齐到盒内
D) fontFeatures="+tnum=2" 是否被接受、且真的产生等宽数字

同时确认：<Snapshot> 必须是根标签；root Container 不给 padding 时，
Positioned 坐标等于画布坐标。

启动基准：总任务根（cwd）。用法：python a04_probe_font.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a04_io as IO  # noqa: E402

FAM = "Noto Sans CJK SC"
FA = 'fontFamily="' + FAM + '"'


def t(left: float, top: float, s: str, size: int, color: str,
      bold: bool = False, **extra) -> str:
    """一行绝对定位文本。"""
    style = ' fontStyle="BOLD"' if bold else ""
    attrs = " ".join(f'{k}="{v}"' for k, v in extra.items())
    return (f'<Positioned left="{left}" top="{top}">'
            f'<Text text="{s}" fontSize="{size}"{style} color="{color}" '
            f'{FA} {attrs}></Text></Positioned>')


def box(left, top, w, h, color, align=None, border=None):
    a = f' alignment="{align}"' if align else ""
    b = f' border="{border}"' if border else ""
    return (f'<Positioned left="{left}" top="{top}" width="{w}" height="{h}">'
            f'<Container width="{w}" height="{h}"{a} color="{color}"{b}'
            f' borderRadius="8"></Container></Positioned>')


def box_text(left, top, w, h, s, size, color, align, bg, bold=False):
    style = ' fontStyle="BOLD"' if bold else ""
    return (f'<Positioned left="{left}" top="{top}" width="{w}" height="{h}">'
            f'<Container width="{w}" height="{h}" alignment="{align}" '
            f'color="{bg}" borderRadius="8"><Text text="{s}" fontSize="{size}"'
            f'{style} color="{color}" {FA}></Text></Container></Positioned>')


LINES = [
    '<Snapshot background="#F8FAFC" type="png">',
    '<Container width="1200" height="580" color="#F8FAFC">',
    '<Stack fit="EXPAND" clipBehavior="NONE">',
    "",
    t(20, 14, "CJK 字体与对齐探针（fontFamily=Noto Sans CJK SC）",
      26, "#0F172A", bold=True),
    "",
    # --- A) 中文字形 ---
    t(20, 56, "中文：访问数 成交数 前期 后期 直接访问 推广访问 总体", 22, "#0F172A"),
    t(20, 88, "数字与单位：8,000 次 2,400 次 3/10 = 30.00%", 22, "#0F172A"),
    t(20, 120, "符号：① ② ③ Σ ÷ → − ↑ ↓ 「」＝ ≥ % pp · ×", 22, "#0F172A"),
    "",
    # --- B) Text textAlign（预期：Text shrink-wrap，对齐不生效）---
    t(20, 160, "B 组 Text textAlign（预期无效）", 19, "#64748B"),
    box(20, 186, 210, 40, "#F1F5F9"),
    t(26, 194, "左对齐", 22, "#0F172A"),
    box(245, 186, 210, 40, "#F1F5F9"),
    t(251, 194, "80.0%", 22, "#0F172A", textAlign="CENTER"),
    box(470, 186, 210, 40, "#F1F5F9"),
    t(476, 194, "35.00%", 22, "#0F172A", textAlign="RIGHT"),
    "",
    # --- C) Container alignment（预期：生效）---
    t(20, 244, "C 组 Container alignment（预期有效：文字贴右 / 贴中）", 19, "#64748B"),
    box_text(20, 270, 210, 40, "9,600", 22, "#0F172A", "CENTER_RIGHT", "#F1F5F9"),
    box_text(245, 270, 210, 40, "3/25", 22, "#0F172A", "CENTER", "#F1F5F9"),
    box_text(470, 270, 210, 40, "+5.00 pp", 22, "#059669", "CENTER_RIGHT",
             "#ECFDF5", bold=True),
    "",
    # --- D) fontFeatures tnum ---
    t(20, 328, "D 组 tnum：A 列两行末位 % 是否对齐；B 列为未加 tnum 对照",
      19, "#64748B"),
    t(40, 356, "A 11.1%", 26, "#0F172A", fontFeatures="+tnum=2"),
    t(40, 392, "A 11.9%", 26, "#0F172A", fontFeatures="+tnum=2"),
    t(250, 356, "B 11.1%", 26, "#0F172A"),
    t(250, 392, "B 11.9%", 26, "#0F172A"),
    t(430, 356, "A 2,000", 26, "#0F172A", fontFeatures="+tnum=2"),
    t(430, 392, "A 10,000", 26, "#0F172A", fontFeatures="+tnum=2"),
    "",
    # --- E) 结论区文案排版（22 号正文，验证实际换行宽度）---
    t(20, 448, "E 组 22 号正文实际宽度：两个渠道的转化率都在上升（直接访问 30.00% → 35.00%）",
      22, "#0F172A"),
    # 952 = 40 + 912，即主结论框内容宽 912px 的位置，红线右侧即溢出
    '<Positioned left="952" top="436" width="2" height="130"><Container width="2" height="130" color="#FCA5A5"></Container></Positioned>',
    t(20, 480, "总体转化率却从 26.00% 降到 16.60%（−9.40 pp），分组与总体不同向。",
      22, "#0F172A"),
    t(20, 512, "总体率 = 成交总数 ÷ 访问总数，不能对渠道比例取平均。",
      22, "#0F172A"),
    "",
    "</Stack>",
    "</Container>",
    "</Snapshot>",
]

DSL = "\n".join(LINES)

if __name__ == "__main__":
    rec = IO.submit(
        DSL, label="A04 字体/对齐/tnum 探针", rid="req-a04-probe-font",
        dsl_version="probe-font", kind="probe")
    print("HTTP", rec["http_status"], "bytes", rec["response_bytes"],
          "ct", rec["content_type"])
    if rec.get("error_summary"):
        print("ERROR", rec["error_summary"])
    else:
        prev = TMP / "preview" / "probe-font.png"
        prev.parent.mkdir(parents=True, exist_ok=True)
        (TMP / "responses" / f"{rec['request_id']}.body").copy(prev)
        print("preview →", prev.relative_to(IO.ROOT))
