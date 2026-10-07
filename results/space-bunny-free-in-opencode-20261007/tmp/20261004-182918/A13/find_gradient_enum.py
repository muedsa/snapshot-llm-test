# -*- coding: utf-8 -*-
"""A13: find the real gradient alignment enum spelling."""
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

for url, name in [("https://snapshot.muedsa.com/reference/enums/", "enums.html"),
                  ("https://snapshot.muedsa.com/widgets/layout/container/", "container2.html")]:
    st, path = snapkit.fetch_doc(url, name, "document")
    print("fetch", st, name)
    if st == 200 and path:
        s = io.open(path, encoding="utf-8").read()
        for m in re.finditer(r"[A-Za-z_]*gradient[A-Za-z_]*", s):
            pass
        hits = sorted(set(re.findall(r"\b(?:TOP_CENTER|BOTTOM_CENTER|CENTER_LEFT|CENTER_RIGHT|TOP_LEFT|TOP_RIGHT|BOTTOM_LEFT|BOTTOM_RIGHT|CENTER|Alignment\.?[A-Z_]*)\b", s)))
        print("  alignment-ish tokens:", hits)
        idx = s.find("gradientBegin")
        if idx > 0:
            frag = re.sub(r"(?s)<[^>]+>", " ", s[max(0, idx - 2500):idx + 2500])
            frag = re.sub(r"\s+", " ", frag)
            print("  fragment:", frag[-1800:])