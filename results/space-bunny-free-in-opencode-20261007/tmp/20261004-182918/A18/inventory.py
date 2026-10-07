import hashlib
import os

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A18")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A18")


def h(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


pairs = [
    (os.path.join(OUT, "three-act-story.snapshot"), os.path.join(TMP, "drafts", "three-act-story.snapshot")),
    (os.path.join(OUT, "three-act-story.snapshot"),
     os.path.join(TMP, "preview", "preview-concept-A-v04.snapshot")),
]
for a, b in pairs:
    print(os.path.basename(a), "==", b.split("A18" + os.sep)[-1], h(a) == h(b), h(a)[:16])
for f in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    print("%-28s %9d  %s" % (f, os.path.getsize(p), h(p)[:16]))
print("--- temp files ---")
for dirpath, _, files in os.walk(TMP):
    for f in sorted(files):
        p = os.path.join(dirpath, f)
        print("%-70s %9d" % (os.path.relpath(p, TMP), os.path.getsize(p)))