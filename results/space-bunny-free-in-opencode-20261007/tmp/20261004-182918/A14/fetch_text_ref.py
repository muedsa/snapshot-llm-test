import os, sys, re
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A14"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
snapkit.configure(TASK, OUT, TMP)
for url, name in [
    ("https://snapshot.muedsa.com/widgets/text/", "ref-text-widget.html"),
    ("https://snapshot.muedsa.com/reference/enums/", "ref-enums.html"),
]:
    st, path = snapkit.fetch_doc(url, name, "document")
    print(st, os.path.getsize(path) if os.path.exists(path) else -1, url)

def totext(html):
    s = re.sub(r"(?s)<script.*?</script>", " ", html)
    s = re.sub(r"(?s)<style.*?</style>", " ", s)
    s = re.sub(r"(?s)<svg.*?</svg>", " ", s)
    s = re.sub(r"<[^>]+>", "\n", s)
    for a, b in [("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&"), ("&quot;", '"'),
                 ("&#39;", "'"), ("&nbsp;", " ")]:
        s = s.replace(a, b)
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n", s).strip()

for name in ("ref-text-widget.html", "ref-enums.html"):
    p = os.path.join(TMP, "docs", name)
    if os.path.exists(p):
        t = totext(open(p, encoding="utf-8").read())
        open(p[:-5] + ".txt", "w", encoding="utf-8", newline="\n").write(t)
        print("txt", name, len(t))