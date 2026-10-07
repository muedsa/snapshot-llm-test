"""A19 step 0: real fetch of the service guide, the DSL tag/attribute reference and
the live font list. Everything is logged into <temp>/requests.jsonl via snapkit.

No credentials are used or stored; the public endpoint answers anonymously.
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A19"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import state as S  # noqa: E402

snapkit.configure(TASK, OUT, TMP)
S.start_task(TASK)

JOBS = [
    ("https://open-snapshot.muedsa.com/ai-guide.md", "ai-guide.md", "document"),
    ("https://snapshot.muedsa.com/reference/parser-tags/", "parser-tags.html", "document"),
    ("https://open-snapshot.muedsa.com/fonts", "fonts-list.txt", "font_list"),
]
for url, name, kind in JOBS:
    st, path = snapkit.fetch_doc(url, name, kind)
    print(st, url, "->", path)