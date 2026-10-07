import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A18"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402

snapkit.configure(TASK, OUT, TMP)

BASE = "https://snapshot.muedsa.com"
jobs = [
    (BASE + "/guides/painting/", "doc-painting.html", "document"),
    (BASE + "/guides/layout/", "doc-layout.html", "document"),
    (BASE + "/reference/parser-tags/", "doc-parser-tags.html", "document"),
    (BASE + "/guides/widgets/", "doc-widgets.html", "document"),
]
for url, name, kind in jobs:
    st, path = snapkit.fetch_doc(url, name, kind)
    print(st, url, "->", path)