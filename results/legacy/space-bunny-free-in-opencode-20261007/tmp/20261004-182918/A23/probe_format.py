"""A23 step 1: real doc access + real format-boundary probes against open-snapshot.

Every claim written into limitations.md must come from one of:
  * a real fetched document (stored under A23 temp docs/),
  * a real service response logged in A23 temp requests.jsonl.
No guessing.
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import state as S  # noqa: E402

TASK = "A23"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
S.start_task(TASK)
print("OUTPUT_DIR =", OUT)
print("TEMP_DIR   =", TMP)

BASE = "https://open-snapshot.muedsa.com"

# ---------------------------------------------------------------- 1. documents
DOCS = [
    ("https://open-snapshot.muedsa.com/ai-guide.md", "ai-guide.md", "document"),
    (BASE + "/openapi.yaml", "openapi.yaml", "document"),
    ("https://snapshot.muedsa.com/guides/rendering/", "doc-rendering-output.html", "document"),
    ("https://snapshot.muedsa.com/reference/parser-tags/", "doc-parser-tags.html", "document"),
    ("https://snapshot.muedsa.com/guides/parser/", "doc-parser.html", "document"),
    ("https://snapshot.muedsa.com/guides/media-text/", "doc-media-text.html", "document"),
    (BASE + "/fonts", "fonts-list.txt", "font_list"),
]
print("\n=== document / font access ===")
for url, name, kind in DOCS:
    st, path = snapkit.fetch_doc(url, name, kind)
    print("  %-4s %-70s -> %s" % (st, url, os.path.basename(str(path))))

# ---------------------------------------------------------------- 2. probes
PROBES = [
    # name, dsl, note
    ("p01-type-png", '<Snapshot type="png"><Container width="40" height="24" color="#FF0000FF"/></Snapshot>',
     "control: documented type=png"),
    ("p02-type-webp", '<Snapshot type="webp"><Container width="40" height="24" color="#00FF00FF"/></Snapshot>',
     "documented type=webp"),
    ("p03-type-jpg", '<Snapshot type="jpg"><Container width="40" height="24" color="#0000FFFF"/></Snapshot>',
     "documented type=jpg"),
    ("p04-type-gif", '<Snapshot type="gif"><Container width="40" height="24" color="#FFFFFFFF"/></Snapshot>',
     "animated GIF probe"),
    ("p05-type-apng", '<Snapshot type="apng"><Container width="40" height="24" color="#FFFFFFFF"/></Snapshot>',
     "animated PNG probe"),
    ("p06-type-svg", '<Snapshot type="svg"><Container width="40" height="24" color="#FFFFFFFF"/></Snapshot>',
     "SVG probe"),
    ("p07-animation-attrs", '<Snapshot type="png" frames="6" frameDuration="250" loop="true" '
     'animated="true"><Container width="40" height="24" color="#FFFFFFFF"/></Snapshot>',
     "invented animation attributes (expect silently ignored)"),
    ("p08-cmyk-attrs", '<Snapshot type="png" colorSpace="CMYK" profile="ISO Coated v2"><Container '
     'width="40" height="24" color="#8040C0FF" cmyk="80,40,0,20"/></Snapshot>',
     "invented CMYK attributes (expect silently ignored)"),
    ("p09-vector-attrs", '<Snapshot type="png"><Container width="40" height="24" color="#8040C0FF" '
     'path="M0,0 L10,10" strokeWidth="2" vectorOutput="true"/></Snapshot>',
     "invented vector/path attributes (expect silently ignored)"),
    ("p10-transparent-default", '<Snapshot><Container width="120" height="60" color="#38BDF8FF"/></Snapshot>',
     "parser default background transparency check"),
]

print("\n=== format / capability probes (real POST /snapshot) ===")
results = []
for name, dsl, note in PROBES:
    r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=False)
    ct = r.get("content_type")
    print("  %-26s ok=%-5s status=%-4s ct=%-12s %s"
          % (name, r["ok"], r["status"], ct, note))
    if not r["ok"]:
        print("        error: %s" % (r.get("error") or "")[:220])
    results.append((name, note, r))

print("\n=== probe PNG real pixel inspection ===")
from PIL import Image  # noqa: E402
prev = os.path.join(TMP, "preview")
if os.path.isdir(prev):
    for f in sorted(os.listdir(prev)):
        if not f.lower().endswith(".png"):
            continue
        p = os.path.join(prev, f)
        im = Image.open(p)
        px = im.convert("RGBA").getpixel((im.width // 2, im.height // 2))
        print("  %-26s mode=%-5s size=%s format=%s center_rgba=%s"
              % (f, im.mode, im.size, im.format, px))

print("\n=== snapkit warnings ===")
print(snapkit.TASK_ID, os.path.isdir(OUT), os.path.isdir(TMP))
