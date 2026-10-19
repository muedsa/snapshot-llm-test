# -*- coding: utf-8 -*-
"""B06 文本抽取（与 case.md 校笔用）：从十个 final.snapshot 按顺序提取 Text 内容。
仅读交付文件，不改动任何留痕。"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(r"D:\mine\test\glm-5.3-flash")
RUN = "20261016T164020-m1"
OUT = ROOT / "outputs" / RUN / "B06"

pat = re.compile(r"<Text\b[^>]*>(.*?)</Text>", re.S)
ent = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&apos;": "'"}

lines = []
for i in range(1, 11):
    p = OUT / ("case-%02d" % i) / "final.snapshot"
    xml = p.read_text(encoding="utf-8")
    lines.append("=" * 12 + " case-%02d " % i + "=" * 12)
    raws = pat.findall(xml)
    for raw in raws:
        t = raw
        for k, v in ent.items():
            t = t.replace(k, v)
        t = re.sub(r"\s+", " ", t).strip()
        if not t:
            # 自闭合/空文本：保留占位，便于发现
            t = raw.strip() or "(empty)"
        lines.append(t)
    lines.append("")

dump = OUT.parent.parent.parent / "tmp" / RUN / "B06" / "text_dump.txt"
dump.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("written", dump.relative_to(ROOT), "texts per case:",
      len([l for l in lines if l and not l.startswith("=")]))
