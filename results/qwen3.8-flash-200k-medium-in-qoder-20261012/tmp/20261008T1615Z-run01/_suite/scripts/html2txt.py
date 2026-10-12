"""Convert downloaded doc HTML to readable text for DSL study.

Run from suite root. Usage: python tmp/<run_id>/_suite/scripts/html2txt.py <file...>
Writes <file>.txt alongside.
"""
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

suite_root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
run_id = os.environ["SNAPSHOT_RUN_ID"]
docs = suite_root / "tmp" / run_id / "_suite" / "docs"


class Strip(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
        self.block_tags = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6",
                           "tr", "br", "section", "article", "pre", "table"}

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        if tag in self.block_tags:
            self.parts.append("\n")
        if tag == "li":
            self.parts.append("- ")
        if tag in ("h1", "h2", "h3", "h4"):
            self.parts.append("\n## ")
        if tag == "td" or tag == "th":
            self.parts.append(" | ")
        if tag == "code":
            self.parts.append("`")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self.skip = max(0, self.skip - 1)
        if tag == "code":
            self.parts.append("`")
        if tag in self.block_tags:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def convert(name):
    src = docs / name
    raw = src.read_text(encoding="utf-8", errors="replace")
    p = Strip()
    p.feed(raw)
    txt = "".join(p.parts)
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r" ?\n ?", "\n", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    out = src.with_suffix(src.suffix + ".txt")
    out.write_text(txt.strip(), encoding="utf-8")
    print(f"{out.relative_to(suite_root).as_posix()} {len(txt)} chars")


for n in sys.argv[1:]:
    convert(n)
