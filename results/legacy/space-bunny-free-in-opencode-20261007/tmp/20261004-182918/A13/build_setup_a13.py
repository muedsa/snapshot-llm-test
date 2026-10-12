# -*- coding: utf-8 -*-
"""A13 setup: configure paths, start the suite task, fetch real service docs + fonts."""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import state as S  # noqa: E402

TASK = "A13"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
S.start_task(TASK)
print("OUT", OUT)
print("TMP", TMP)
print("started at", S.now_iso())

FETCH = [
    ("https://open-snapshot.muedsa.com/ai-guide.md", "ai-guide.md", "document"),
    ("https://open-snapshot.muedsa.com/openapi.yaml", "openapi.yaml", "document"),
    ("https://snapshot.muedsa.com/", "index.html", "document"),
    ("https://snapshot.muedsa.com/widgets/layout/container/", "container.html", "document"),
    ("https://snapshot.muedsa.com/widgets/basic/text/", "text.html", "document"),
    ("https://snapshot.muedsa.com/widgets/layout/transform/", "transform.html", "document"),
]
for url, name, kind in FETCH:
    st, path = snapkit.fetch_doc(url, name, kind)
    print("fetch", st, os.path.basename(str(path)))

st, path = snapkit.fetch_doc(snapkit.BASE + "/fonts", "fonts.txt", "font_list")
print("fonts", st, path)
with open(path, encoding="utf-8") as fh:
    fonts = [f.strip() for f in fh if f.strip()]
print("font families:", len(fonts))
for f in fonts:
    print("   ", f)