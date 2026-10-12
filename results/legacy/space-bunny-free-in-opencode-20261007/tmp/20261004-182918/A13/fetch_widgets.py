# -*- coding: utf-8 -*-
"""A13: fetch the widget catalogue + painting guide, list Text widget doc URL."""
import io
import os
import re
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import state as S  # noqa: E402

TASK = "A13"
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), os.path.join(S.TMP_ROOT, TASK))

for url, name in [("https://snapshot.muedsa.com/guides/widgets/", "widgets-guide.html"),
                  ("https://snapshot.muedsa.com/guides/painting/", "painting-guide.html"),
                  ("https://snapshot.muedsa.com/reference/parser-tags/", "parser-tags.html")]:
    st, path = snapkit.fetch_doc(url, name, "document")
    print("fetch", st, name)
    if st == 200 and path:
        s = io.open(path, encoding="utf-8").read()
        hrefs = sorted(set(re.findall(r'href="(/[^"#]+)"', s)))
        for h in hrefs:
            if "widget" in h:
                print("   ", h)