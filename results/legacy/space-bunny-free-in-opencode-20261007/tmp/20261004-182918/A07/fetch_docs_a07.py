"""A07 step 0: fetch the real service guide + DSL docs into the task temp dir."""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import state as S  # noqa: E402

TASK = "A07"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
S.start_task(TASK)
os.makedirs(TMP, exist_ok=True)
with open(os.path.join(TMP, "A07.started"), "w", encoding="utf-8") as fh:
    fh.write(snapkit.now_iso())

DOCS = [
    ("https://open-snapshot.muedsa.com/ai-guide.md", "ai-guide.md", "document"),
    ("https://snapshot.muedsa.com/", "dsl-docs-index.html", "document"),
]
for url, name, kind in DOCS:
    status, path = snapkit.fetch_doc(url, name, kind)
    size = os.path.getsize(path) if path and os.path.exists(str(path)) else None
    print("FETCH %s -> %s bytes=%s" % (url, status, size))
