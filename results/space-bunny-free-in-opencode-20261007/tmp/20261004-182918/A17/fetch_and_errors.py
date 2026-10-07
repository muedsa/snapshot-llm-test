"""A17 step 1: fetch the official docs into this task's temp dir (logged through
snapkit so they land in requests.jsonl) and capture three *real* error
responses from POST /snapshot so handbook page 1 can quote actual bodies.

Nothing here is a delivery artifact; the final pages/sources.md/examples.json
cite these files.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A17"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

snapkit.configure(TASK, OUT, TMP)
S.start_task(TASK)
DOCS = os.path.join(TMP, "docs")
os.makedirs(DOCS, exist_ok=True)

DOC_URLS = [
    ("ai-guide.md", "https://open-snapshot.muedsa.com/ai-guide.md", "document"),
    ("openapi.yaml", "https://open-snapshot.muedsa.com/openapi.yaml", "document"),
    ("snapshot-parser.html", "https://snapshot.muedsa.com/guides/parser/", "document"),
    ("snapshot-layout.html", "https://snapshot.muedsa.com/guides/layout/", "document"),
    ("snapshot-media-text.html", "https://snapshot.muedsa.com/guides/media-text/", "document"),
    ("snapshot-painting.html", "https://snapshot.muedsa.com/guides/painting/", "document"),
    ("snapshot-parser-tags.html", "https://snapshot.muedsa.com/reference/parser-tags/", "document"),
    ("snapshot-enums.html", "https://snapshot.muedsa.com/reference/enums/", "document"),
]
for name, url, kind in DOC_URLS:
    st, path = snapkit.fetch_doc(url, name, kind=kind)
    print("%-32s %s %s" % (name, st, path))

st, path = snapkit.fetch_doc("https://open-snapshot.muedsa.com/fonts", "fonts.txt",
                             kind="font_list")
print("fonts", st, path)

# --------------------------------------------------------------- error probes
PROBE = os.path.join(TMP, "probe")
os.makedirs(PROBE, exist_ok=True)
ERRS = [
    ("err-parse", '<Snapshot type="png" background="#0F172AFF">\n'
                  '  <Container width="300" height="120" color="#2563EBFF" padding="24 32" />\n'
                  '</Snapshot>\n'),
    ("err-render", '<Snapshot type="png">\n'
                   '  <Column>\n'
                   '    <Row><Expanded flex="2"><Container color="#38BDF8FF" /></Expanded></Row>\n'
                   '  </Column>\n'
                   '</Snapshot>\n'),
    ("err-infinite", '<Snapshot type="png">\n'
                     '  <Column>\n'
                     '    <Container color="#38BDF8FF" />\n'
                     '  </Column>\n'
                     '</Snapshot>\n'),
    ("err-empty", ''),
]
out = {}
for tag, dsl in ERRS:
    p = os.path.join(PROBE, tag + ".snapshot")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, tag + ".png", tag + ".snapshot", final=False, out_dir=PROBE)
    out[tag] = {"status": r.get("status"), "ok": r.get("ok"),
                "error": r.get("error"), "content_type": r.get("content_type"),
                "response_file": r.get("response_file"), "dsl": p,
                "service_request_id": r.get("request_id"),
                "server_timing": r.get("server_timing"), "attempts": r.get("attempts")}
    print(tag, out[tag]["status"], out[tag]["content_type"], (out[tag]["error"] or "")[:220])

json.dump(out, open(os.path.join(PROBE, "errors.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("WARN", D.warnings())