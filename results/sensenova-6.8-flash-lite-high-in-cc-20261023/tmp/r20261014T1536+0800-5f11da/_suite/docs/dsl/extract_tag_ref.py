"""把 parser-tags 参考页里指定标签的属性表抽成可读文本。

用法：python extract_tag_ref.py Transform Container Text Snapshot Stack Opacity
输出同名 .txt 到同目录。
"""
from __future__ import annotations

import html as H
import re
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
SRC = D / "reference-parser-tags.html"


def clean(s: str) -> str:
    s = re.sub(r"<script[^>]*>.*?</script>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<style[^>]*>.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"</(tr|p|li|div|h[1-6]|td|th|dt|dd)>", "\n", s, flags=re.I)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = H.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def main() -> None:
    names = sys.argv[1:] or ["Transform"]
    t = SRC.read_text(encoding="utf-8", errors="replace")
    out = []
    for nm in names:
        # 该标签的章节：从 "TagName" 一级标题到下一个同级标题
        pat = re.compile(rf"<h[12][^>]*>\s*{re.escape(nm)}\s*</h[12]>(.*?)"
                         r"(?=<h[12][^>]*>\s*[A-Z][A-Za-z0-9 ]*\s*</h[12]>|</main>)",
                         re.S)
        m = pat.search(t)
        out.append(f"===== <{nm}> =====")
        out.append(clean(m.group(1))[:6000] if m else "（未找到章节）")
        out.append("")
        # 属性表行（表格里首列就是属性名）
        rows = re.findall(rf"<td[^>]*>\s*<code[^>]*>\s*{re.escape(nm)}\s*</code>.*?</tr>",
                          t, flags=re.S)
        for r in rows[:3]:
            out.append("  ROW: " + clean(r)[:500])
    (D / f"tagref-{'-'.join(names)}.txt").write_text("\n".join(out) + "\n",
                                                    encoding="utf-8")


if __name__ == "__main__":
    main()
