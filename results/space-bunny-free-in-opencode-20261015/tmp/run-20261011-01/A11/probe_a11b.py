#!/usr/bin/env python
"""A11 第二轮探针：text 属性（裸字符）+ Raw 空格 + 富文本基线 + 右对齐定点数。

启动基准：总任务根 (suite_root)。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
from snapkit import C  # noqa: E402

DRAFTS = "tmp/run-20261011-01/A11/drafts"
W, H = 1200, 620
F_INTER = "Inter"
F_SB = "Inter Semi Bold"
F_NUM = "Inter Medium"
F_SC = "Noto Sans CJK SC"
F_JP = "Noto Sans CJK JP"


def row(y, label, body, h=56):
    return (f'<Positioned left="40" top="{y}" width="300" height="{h}">'
            f'<Text fontSize="22" color="#64748B" fontFamily="{F_SC}">{label}</Text></Positioned>'
            f'<Positioned left="360" top="{y}" width="{W - 400}" height="{h}">'
            f'<Container width="{W - 400}" height="{h}" color="#F8FAFC" borderRadius="8" '
            f'border="1 SOLID #E2E8F0"><Stack fit="EXPAND">'
            f'<Positioned left="14" top="4" width="{W - 432}" height="{h - 8}">{body}'
            f'</Positioned></Stack></Container></Positioned>')


def main() -> None:
    P = []
    A = P.append
    A(f'<Container width="{W}" height="{H}" color="#FFFFFF"><Stack fit="EXPAND">')
    A(f'<Positioned left="0" top="0" width="{W}" height="{H}">'
      f'<Container width="{W}" height="{H}" color="#FFFFFF"/></Positioned>')
    A(f'<Positioned left="40" top="20" width="700" height="44">'
      f'<Text fontSize="34" color="#0F172A" fontFamily="{F_SB},{F_SC}">A11 探针 2</Text></Positioned>')

    A(row(84, "text 属性 + 裸尖括号/&",
          f'<Text fontSize="34" fontFamily="{F_NUM}" color="#0F172A" text="A &lt; B &amp; C &gt; D"/>'))
    A(row(148, "text 属性 + SKU 混淆样本",
          f'<Text fontSize="34" fontFamily="{F_SB}" color="#0F172A" '
          f'text="O0-I1-B8   A&lt;B&amp;C&gt;D   R-07   SP-2"/>'))
    A(row(212, "text 属性 + 批次行双空格",
          f'<Text fontSize="34" fontFamily="{F_INTER},{F_SC}" color="#0F172A" '
          f'text="\u6279\u6b21\uff1a  A  07"/>'))
    A(row(276, "text 属性 + 反斜杠路径",
          f'<Text fontSize="34" fontFamily="{F_NUM}" color="#0F172A" '
          f'text="Path: C:\\work\\cards\\v2"/>'))
    A(row(340, "嵌套 Text + Raw 空格",
          f'<Text fontSize="44" fontFamily="{F_SB},{F_SC}">'
          f'<Text color="#059669">PAID</Text><Raw> </Raw>'
          f'<Text color="#94A3B8">/</Text><Raw> </Raw>'
          f'<Text color="#0F172A">\u5df2\u7ed3\u7b97</Text></Text>'))
    A(row(404, "嵌套 Text + Raw 双空格",
          f'<Text fontSize="44" fontFamily="{F_SB},{F_SC}">'
          f'<Text color="#059669">PAID</Text><Raw>  </Raw>'
          f'<Text color="#94A3B8">/</Text><Text color="#0F172A">\u5df2\u7ed3\u7b97</Text></Text>'))
    # 右对齐定点数：整数部分右对齐贴小数点左侧，小数点固定 x，小数部分左对齐
    A(row(468, "定点数（小数点列对齐）",
          f'<Container width="{W - 432}" height="52"><Stack fit="EXPAND">'
          f'<Positioned left="0" top="0" width="260" height="46">'
          f'<Container width="260" height="46"><Row mainAxisAlignment="END">'
          f'<Text fontSize="36" fontFamily="{F_NUM}" color="#0F172A" text="4,124"/>'
          f'<Text fontSize="36" fontFamily="{F_NUM}" color="#0F172A" text="."/>'
          f'<Text fontSize="36" fontFamily="{F_NUM}" color="#0F172A" text="30"/>'
          f'</Row></Container></Positioned>'
          f'<Positioned left="280" top="0" width="260" height="46">'
          f'<Text fontSize="36" fontFamily="{F_NUM}" color="#0F172A" '
          f'textAlign="RIGHT" text="3,905.50"/></Positioned>'
          f'</Stack></Container>'))

    A("</Stack></Container>")
    dsl = f'<Snapshot type="png">\n{"".join(P)}\n</Snapshot>\n'
    p = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")) / DRAFTS
    p.mkdir(parents=True, exist_ok=True)
    (p / "probe-text2.snapshot").write_text(dsl, encoding="utf-8")
    print("bytes:", len(dsl.encode()))


if __name__ == "__main__":
    main()