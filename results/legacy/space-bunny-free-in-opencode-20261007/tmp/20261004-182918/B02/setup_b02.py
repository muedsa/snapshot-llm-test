# -*- coding: utf-8 -*-
"""B02 setup: paths, suite task start, real service doc + font fetches."""
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import state as S  # noqa: E402

TASK = "B02"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
S.start_task(TASK)
print("OUT", OUT)
print("TMP", TMP)
print("started_at", S.now_iso())
with open(os.path.join(TMP, "b02-start.json"), "w", encoding="utf-8") as fh:
    json.dump({"started_at": S.now_iso(), "out": OUT, "tmp": TMP}, fh, ensure_ascii=False, indent=2)

FETCH = [
    ("https://open-snapshot.muedsa.com/ai-guide.md", "ai-guide.md", "document"),
    ("https://open-snapshot.muedsa.com/openapi.yaml", "openapi.yaml", "document"),
    ("https://snapshot.muedsa.com/", "index.html", "document"),
    ("https://snapshot.muedsa.com/widgets/basic/text/", "text.html", "document"),
    ("https://snapshot.muedsa.com/widgets/layout/container/", "container.html", "document"),
]
for url, name, kind in FETCH:
    st, path = snapkit.fetch_doc(url, name, kind)
    print("fetch", st, name, "->", str(path)[:90])

st, path = snapkit.fetch_doc(snapkit.BASE + "/fonts", "fonts.txt", "font_list")
print("fonts", st, path)
with open(path, encoding="utf-8") as fh:
    fonts = [f.strip() for f in fh if f.strip()]
print("font families:", len(fonts))
for f in fonts:
    print("   ", f)
