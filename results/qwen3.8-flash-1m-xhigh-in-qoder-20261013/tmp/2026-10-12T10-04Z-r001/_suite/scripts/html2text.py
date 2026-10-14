"""Convert downloaded Astro docs HTML into readable plain text.

Run from the probe directory: python html2text.py docs/<file>.html
Usage: python html2text.py <input.html> [output.txt]
"""
import sys
import re
from html.parser import HTMLParser
from pathlib import Path


class TextExtract(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "head"}
    BLOCK = {
        "p", "div", "section", "article", "li", "tr", "table", "h1", "h2", "h3",
        "h4", "h5", "h6", "ul", "ol", "br", "pre", "blockquote", "main", "nav",
        "header", "footer", "figure", "figcaption", "dt", "dd", "dl", "hr",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip_depth = 0
        self.in_pre = False
        self.cell = []
        self.in_row = False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag == "pre":
            self.in_pre = True
            self.out.append("\n```\n")
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.out.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "td" or tag == "th":
            self.cell.append("")
        elif tag == "tr":
            self.in_row = True
        elif tag in self.BLOCK:
            self.out.append("\n")
        elif tag == "code":
            self.out.append("`")

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if self.skip_depth:
            return
        if tag == "pre":
            self.in_pre = False
            self.out.append("\n```\n\n")
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.out.append("\n\n")
        elif tag in ("td", "th"):
            if self.cell:
                self.cell[-1] = self.cell[-1].strip().replace("\n", " ")
        elif tag == "tr":
            if self.cell:
                self.out.append(" | ".join(self.cell) + "\n")
            self.cell = []
            self.in_row = False
        elif tag == "code":
            self.out.append("`")
        elif tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if self.skip_depth:
            return
        if self.cell:
            self.cell[-1] += data
            return
        if not self.in_pre:
            data = re.sub(r"[ \t]+", " ", data)
            if data.strip() == "":
                if self.out and self.out[-1].endswith(" "):
                    return
                data = "\n" if not self.out[-1].endswith("\n") else ""
        self.out.append(data)


def main():
    src = Path(sys.argv[1])
    html = src.read_text(encoding="utf-8", errors="replace")
    # Keep only the main content region when present.
    m = re.search(r"<main\b.*?</main>", html, re.S | re.I)
    body = m.group(0) if m else html
    p = TextExtract()
    p.feed(body)
    text = "".join(p.out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".txt")
    dst.write_text(text.strip() + "\n", encoding="utf-8")
    print(f"{src.name} -> {dst.name}: {len(text)} chars")


if __name__ == "__main__":
    main()
