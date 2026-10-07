"""A17 step 1b: more real error probes.

The first batch produced three identical "Layout size is empty" bodies, which
does not match the suite handbook's note about "Layout size is infinite".  These
variants find DSL texts that actually trigger the infinite case, so the page
only quotes responses that were really observed.
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

snapkit.configure(TASK, OUT, TMP)
PROBE = os.path.join(TMP, "probe")
os.makedirs(PROBE, exist_ok=True)

CASES = [
    ("e-bare-container", '<Snapshot type="png">\n  <Container color="#38BDF8FF" />\n</Snapshot>\n'),
    ("e-row-expanded", '<Snapshot type="png">\n  <Row>\n'
                       '    <Expanded flex="2"><Container color="#38BDF8FF" /></Expanded>\n'
                       '  </Row>\n</Snapshot>\n'),
    ("e-column-text", '<Snapshot type="png">\n  <Column>\n'
                      '    <Text fontSize="20" color="#0F172AFF">hi</Text>\n'
                      '  </Column>\n</Snapshot>\n'),
    ("e-bad-hex", '<Snapshot type="png">\n'
                  '  <Container width="200" height="80" color="#38BDF866FF" />\n</Snapshot>\n'),
    ("e-bad-borderstyle", '<Snapshot type="png">\n'
                          '  <Container width="200" height="80" border="2 DASHED #FFF" />\n</Snapshot>\n'),
    ("e-unknown-attr", '<Snapshot type="png">\n'
                       '  <Container width="200" height="80" colour="#38BDF8FF" />\n</Snapshot>\n'),
    ("e-two-roots", '<Snapshot type="png">\n'
                    '  <Container width="200" height="80" color="#38BDF8FF" />\n'
                    '  <Container width="100" height="40" color="#F87171FF" />\n</Snapshot>\n'),
    ("e-text-in-row", '<Snapshot type="png">\n'
                      '  <Container width="300" height="120">\n'
                      '    raw text not allowed\n'
                      '  </Container>\n</Snapshot>\n'),
]
out = {}
for tag, dsl in CASES:
    r = snapkit.render(dsl, tag + ".png", tag + ".snapshot", final=False, out_dir=PROBE)
    out[tag] = {"status": r.get("status"), "ok": r.get("ok"),
                "content_type": r.get("content_type"),
                "error": r.get("error"),
                "response_file": (r.get("response_file") or "")
                .replace(ROOT + "\\", "").replace("\\", "/"),
                "dsl": "tmp/%s/A17/probe/%s.snapshot" % (RUN, tag),
                "server_timing": r.get("server_timing")}
    print("%-18s %s %-18s %s" % (tag, out[tag]["status"], out[tag]["content_type"],
                                 (out[tag]["error"] or "")[:200]))

json.dump(out, open(os.path.join(PROBE, "errors2.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

# keep only successful probe PNGs around; failures stay as recorded JSON
for tag in CASES[0:0]:
    pass
print("WARN", D.warnings())