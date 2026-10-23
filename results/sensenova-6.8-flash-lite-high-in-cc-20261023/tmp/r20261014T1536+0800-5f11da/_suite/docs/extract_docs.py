"""把缓存的 DSL 文档 HTML 抽成干净 UTF-8 文本，便于 Read 工具直接读。

只保留 <main> 内的正文：去 script/style/nav，标签转纯文本，压缩空白。
输出同名 .md.txt 到同目录。
"""
from __future__ import annotations
import html as H
import re
import sys
from pathlib import Path

D = Path(__file__).resolve().parent


def main() -> None:
    for f in sorted(D.glob("*.html")) + sorted((D / "dsl").glob("*.html")):
        t = f.read_text(encoding="utf-8", errors="replace")
        # 去脚本/样式/侧栏/脚本类噪声
        t = re.sub(r"<script[^>]*>.*?</script>", " ", t, flags=re.S | re.I)
        t = re.sub(r"<style[^>]*>.*?</style>", " ", t, flags=re.S | re.I)
        t = re.sub(r"<nav[^>]*>.*?</nav>", " ", t, flags=re.S | re.I)
        t = re.sub(r"<(aside|footer|header)[^>]*>.*?</\1>", " ", t,
                   flags=re.S | re.I)
        m = re.search(r"<main[^>]*>(.*?)</main>", t, flags=re.S | re.I)
        if m:
            t = m.group(1)
        # 代码块保留换行，其余标签换行
        t = re.sub(r"</(p|div|li|tr|dt|dd|h[1-6]|pre)>", "\n", t, flags=re.I)
        t = re.sub(r"<br\s*/?>", "\n", t, flags=re.I)
        t = re.sub(r"<[^>]+>", " ", t)
        t = H.unescape(t)
        t = re.sub(r"[ \t]+", " ", t)
        t = re.sub(r"\n{3,}", "\n\n", t).strip()
        out = f.with_suffix(f.suffix + ".md.txt")
        out.write_text(t + "\n", encoding="utf-8")
        print(f"{f.name} -> {out.name}  {len(t)} chars")


if __name__ == "__main__":
    main()
