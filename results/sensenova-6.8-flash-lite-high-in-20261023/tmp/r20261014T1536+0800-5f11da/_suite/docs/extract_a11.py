"""抽取 A11 新增抓取的 4 个文本参考页，只处理 parser-text / text-layout / text-style / enums。

复用 extract_docs.py 的清洗逻辑，但按文件名过滤，不重写早期已提取的 *.md.txt
（那几份是 A01–A10 阶段的过程证据，不覆盖）。
"""
from __future__ import annotations
import html as H
import re
from pathlib import Path

D = Path(__file__).resolve().parent / "dsl"
TARGETS = ("parser-text", "text-layout", "text-style", "enums")


def clean(t: str) -> str:
    t = re.sub(r"<script[^>]*>.*?</script>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<style[^>]*>.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<nav[^>]*>.*?</nav>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<(aside|footer|header)[^>]*>.*?</\1>", " ", t, flags=re.S | re.I)
    m = re.search(r"<main[^>]*>(.*?)</main>", t, flags=re.S | re.I)
    if m:
        t = m.group(1)
    t = re.sub(r"</(p|div|li|tr|dt|dd|h[1-6]|pre)>", "\n", t, flags=re.I)
    t = re.sub(r"<br\s*/?>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = H.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


for f in sorted(D.glob("*.html")):
    if not any(f.name.startswith(t) for t in TARGETS):
        continue
    t = clean(f.read_text(encoding="utf-8", errors="replace"))
    out = f.with_suffix(f.suffix + ".md.txt")
    out.write_text(t + "\n", encoding="utf-8")
    print(f"{f.name} -> {out.name}  {len(t)} chars")
