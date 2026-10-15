#!/usr/bin/env python
"""A11 文字保真探针：内部双空格 / 尖括号与 & / 反斜杠 / 易混 SKU / 富文本共用基线。

启动基准：总任务根 (suite_root)。输出 tmp/run-20261011-01/A11/preview/probe-text.png。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import snapkit as sk  # noqa: E402
from snapkit import C  # noqa: E402

DRAFTS = "tmp/run-20261011-01/A11/drafts"
W, H = 1240, 860
F_NUM = "Inter Medium"
F_NUM_SB = "Inter Semi Bold"
F_MONO = "DejaVu Sans Mono"

ROWS = [
    ("A1  Text 内部双空格",
     '<Text fontSize="32" fontFamily="Inter,Noto Sans CJK SC" color="#0F172A">'
     '批次：  A  07</Text>'),
    ("A2  Text 单空格对照",
     '<Text fontSize="32" fontFamily="Inter,Noto Sans CJK SC" color="#0F172A">'
     '批次： A 07</Text>'),
    ("B1  Raw 内部双空格",
     '<Text fontSize="32" fontFamily="Inter,Noto Sans CJK SC" color="#0F172A">'
     '<Raw>批次：  A  07</Raw></Text>'),
    ("B2  Raw 前导与尾随空格",
     '<Text fontSize="32" fontFamily="Inter,Noto Sans CJK SC" color="#0F172A">'
     '<Raw>  批次：  A  07  </Raw></Text>'),
    ("C1  尖括号与 & （DSL 内写成 &lt; &amp; &gt;）",
     '<Text fontSize="32" fontFamily="DejaVu Sans Mono,Noto Sans CJK SC" color="#0F172A">'
     'A &lt; B &amp; C &gt; D</Text>'),
    ("C2  同串在注释里对照：DSL 源码若直接写 < 与 & 会被 XML 解析器拒绝",
     '<Text fontSize="32" fontFamily="DejaVu Sans Mono,Noto Sans CJK SC" color="#0F172A">'
     'A B C D  ← 这是 C1 去掉三个实体后的样子</Text>'),
    ("D   反斜杠路径",
     '<Text fontSize="32" fontFamily="DejaVu Sans Mono,Noto Sans CJK SC" color="#0F172A">'
     'Path: C:\\work\\cards\\v2</Text>'),
    ("E1  易混 SKU（Inter）",
     '<Text fontSize="32" fontFamily="Inter,Noto Sans CJK SC" color="#0F172A">'
     'O0-I1-B8   A&lt;B&amp;C&gt;D   R-07   SP-2</Text>'),
    ("E2  易混 SKU（DejaVu Sans Mono，0 带点或斜线便于区分）",
     '<Text fontSize="32" fontFamily="DejaVu Sans Mono,Noto Sans CJK SC" color="#0F172A">'
     'O0-I1-B8   A&lt;B&amp;C&gt;D   R-07   SP-2</Text>'),
    ("F1  富文本同字号共用基线",
     '<Text fontSize="40" fontFamily="Inter Semi Bold,Noto Sans CJK SC">'
     '<Text color="#059669">PAID</Text><Text color="#94A3B8"> / </Text>'
     '<Text color="#0F172A">已结算</Text></Text>'),
    ("F2  富文本混字号（验证基线是否仍对齐）",
     '<Text fontSize="40" fontFamily="Inter Semi Bold,Noto Sans CJK SC">'
     '<Text color="#059669" fontSize="30">PAID</Text><Text color="#94A3B8" fontSize="40"> / </Text>'
     '<Text color="#0F172A" fontSize="52">已结算</Text></Text>'),
    ("F3  三段独立 Text 并排（Row crossAxisAlignment=CENTER，作基线对照）",
     '<Row crossAxisAlignment="CENTER">'
     '<Text fontSize="40" color="#059669" fontFamily="Inter Semi Bold">PAID</Text>'
     '<Text fontSize="40" color="#94A3B8" fontFamily="Inter Semi Bold"> / </Text>'
     '<Text fontSize="40" color="#0F172A" fontFamily="Noto Sans CJK SC">已结算</Text></Row>'),
    ("G   日文（Noto Sans CJK JP）",
     '<Text fontSize="32" fontFamily="Noto Sans CJK JP,Noto Sans CJK SC" color="#0F172A">'
     'Northstar Research 株式会社 · 契約レビュー · 納品書</Text>'),
    ("H   数字定宽（DejaVu Sans Mono）",
     '<Text fontSize="32" fontFamily="DejaVu Sans Mono" color="#0F172A">'
     '0O1lI| 1,234.56  7,777.77</Text>'),
]


def main() -> None:
    P = []
    A = P.append
    A(f'<Container width="{W}" height="{H}" color="#FFFFFF"><Stack fit="EXPAND">')
    A(f'<Positioned left="0" top="0" width="{W}" height="{H}">'
      f'<Container width="{W}" height="{H}" color="#FFFFFF"/></Positioned>')
    A(sk.text("A11 文字保真探针", size=34, color=C.INK, family=sk.F_HEAD, left=40, top=24,
              width=800, height=44))
    y = 92
    for label, body in ROWS:
        A(sk.text(label, size=20, color=C.MUTED, family=sk.F_BODY,
                  left=40, top=y, width=460, height=26))
        A(f'<Positioned left="520" top="{y - 4}" width="{W - 560}" height="48">'
          f'<Container width="{W - 560}" height="48" color="#F8FAFC" borderRadius="8" '
          f'border="1 SOLID #E2E8F0"><Stack fit="EXPAND">'
          f'<Positioned left="14" top="4" width="{W - 592}" height="42">{body}'
          f'</Positioned></Stack></Container></Positioned>')
        y += 56
    A("</Stack></Container>")
    dsl = f'<Snapshot type="png">\n{"".join(P)}\n</Snapshot>\n'
    p = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")) / DRAFTS
    p.mkdir(parents=True, exist_ok=True)
    (p / "probe-text.snapshot").write_text(dsl, encoding="utf-8")
    print("probe bytes:", len(dsl.encode()))


if __name__ == "__main__":
    main()