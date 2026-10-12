"""A17 probe 8: reproduce the elision-row glyph pile-up seen on handbook-01.

The row rendered "⋯⋯ 印刷省略 第 9–42 行（共 34 行）；完整文档见 example-01.snapshot"
inside one Text and a cluster of glyphs came out superimposed.  This probe
renders the same string under several widths/fonts so the cause can be pinned
down instead of guessed.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A17"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
sys.path.insert(0, HERE)
import snapkit  # noqa: E402
import hb  # noqa: E402

snapkit.configure(TASK, OUT, TMP)
PROBE = os.path.join(TMP, "probe")

LABEL = "⋯⋯ 印刷省略 第 9–42 行（共 34 行）；完整文档见 example-01.snapshot"
print("label width @16 =", hb.text_w(LABEL, 16))

CASES = [
    ("ui16_w1006", LABEL, hb.UI, 16, 1006),
    ("ui16_w600", LABEL, hb.UI, 16, 600),
    ("ui16_nowidth", LABEL, hb.UI, 16, None),
    ("ui20_w1006", LABEL, hb.UI, 20, 1006),
    ("ui16_ascii", "printed omission lines 9-42 of 63 in example-01.snapshot",
     hb.UI, 16, 1006),
    ("ui16_cjkonly", "印刷省略第 9 至 42 行共 34 行完整文档见示例一", hb.UI, 16, 1006),
    ("ui16_nodash", "⋯⋯ 印刷省略 第 9-42 行（共 34 行）；完整文档见 example-01.snapshot",
     hb.UI, 16, 1006),
    ("ui16_notdot", "印刷省略 第 9–42 行（共 34 行）；完整文档见 example-01.snapshot",
     hb.UI, 16, 1006),
    ("ui16_nosemi", "⋯⋯ 印刷省略 第 9–42 行 (共 34 行) 完整文档见 example-01.snapshot",
     hb.UI, 16, 1006),
]

W = 1200
ROW = 44
H = 20 + len(CASES) * ROW
parts = [hb.rect(0, 0, W, H, fill=hb.C["code_bg"])]
y = 10
for label, text, font, size, w in CASES:
    parts.append(hb.ctext(label, 20, y + 12, 14, "#64748BFF", font=hb.MONO, w=150))
    parts.append(hb.ctext(text, 200, y + 10, size, "#E2E8F0FF", font=font, w=w))
    parts.append(hb.rect(200 + (w or 1000), y + 4, 2, 34, fill="#FACC15FF"))
    y += ROW

dsl = hb.stack_page(parts, W, H, background=hb.C["code_bg"])
r = snapkit.render(dsl, "elision.png", "elision.snapshot", final=False, out_dir=PROBE)
print("ok=", r.get("ok"), r.get("status"), (r.get("error") or "")[:200])
print("WARN", hb.warnings())