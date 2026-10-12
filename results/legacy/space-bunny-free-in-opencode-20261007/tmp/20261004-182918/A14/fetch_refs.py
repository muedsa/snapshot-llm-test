"""A14 step 0b: fetch the DSL reference pages actually used by this task."""
import os
import re
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A14"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402

snapkit.configure(TASK, OUT, TMP)

PAGES = [
    ("https://snapshot.muedsa.com/reference/parser-tags/", "ref-parser-tags.html"),
    ("https://snapshot.muedsa.com/guides/media-text/", "guide-media-text.html"),
    ("https://snapshot.muedsa.com/guides/layout/", "guide-layout.html"),
    ("https://snapshot.muedsa.com/guides/painting/", "guide-painting.html"),
    ("https://snapshot.muedsa.com/guides/parser/", "guide-parser.html"),
    ("https://snapshot.muedsa.com/openapi.yaml", "openapi.yaml"),
]
for url, name in PAGES:
    st, path = snapkit.fetch_doc(url, name, "document")
    size = os.path.getsize(path) if os.path.exists(path) else -1
    print(st, size, url)


def totext(html):
    s = re.sub(r"(?s)<script.*?</script>", " ", html)
    s = re.sub(r"(?s)<style.*?</style>", " ", s)
    s = re.sub(r"(?s)<svg.*?</svg>", " ", s)
    s = re.sub(r"<[^>]+>", "\n", s)
    s = re.sub(r"&lt;", "<", s)
    s = re.sub(r"&gt;", ">", s)
    s = re.sub(r"&amp;", "&", s)
    s = re.sub(r"&quot;", '"', s)
    s = re.sub(r"&#39;", "'", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


for name in ("ref-parser-tags.html", "guide-media-text.html"):
    p = os.path.join(TMP, "docs", name)
    if os.path.exists(p):
        t = totext(open(p, encoding="utf-8").read())
        out = p[:-5] + ".txt"
        open(out, "w", encoding="utf-8", newline="\n").write(t)
        print("text ->", out, len(t))