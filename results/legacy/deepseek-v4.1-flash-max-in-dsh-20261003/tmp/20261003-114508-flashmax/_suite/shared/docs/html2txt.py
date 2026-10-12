"""Convert the downloaded snapshot.muedsa.com doc pages to plain text (shared prep).

Strips the Starlight chrome (nav / sidebar / footer) and keeps the <main> content so
the DSL rules can be grepped quickly. Shared across A09-A12; not task-specific.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def strip(html: str) -> str:
    # keep only the main content column
    m = re.search(r"<main[\s\S]*?</main>", html)
    if m:
        html = m.group(0)
    html = re.sub(r"<(script|style|svg)[\s\S]*?</\1>", " ", html)
    html = re.sub(r"<br\s*/?>", "\n", html)
    html = re.sub(r"</(p|div|li|tr|h1|h2|h3|h4|pre|table|section)>", "\n", html)
    html = re.sub(r"</t[dh]>", " | ", html)
    html = re.sub(r"<[^>]+>", "", html)
    html = (html.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<")
                .replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'"))
    html = re.sub(r"[ \t]+", " ", html)
    html = re.sub(r"\n\s*\n+", "\n", html)
    return html.strip()


def main() -> None:
    names = sys.argv[1:] or [f[:-5] for f in os.listdir(HERE) if f.endswith(".html")]
    for n in names:
        src = os.path.join(HERE, n + ".html")
        if not os.path.exists(src):
            continue
        txt = strip(open(src, encoding="utf-8").read())
        out = os.path.join(HERE, n + ".txt")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(txt)
        print(f"{n}.txt {len(txt)} chars")


if __name__ == "__main__":
    main()
