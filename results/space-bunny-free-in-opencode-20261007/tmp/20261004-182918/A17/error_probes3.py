"""A17 step 1c: hunt the unbounded-root case with DSL texts that genuinely leave
the layout infinite, so handbook page 2 can quote a response that was really
observed rather than a remembered one.
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

CASES = [
    ("i-col-container-nowidth", '<Snapshot type="png">\n  <Column>\n'
                                '    <Container height="40" color="#38BDF8FF" />\n'
                                '  </Column>\n</Snapshot>\n'),
    ("i-row-height-only", '<Snapshot type="png">\n  <Row>\n'
                          '    <Container width="40" color="#38BDF8FF" />\n'
                          '  </Row>\n</Snapshot>\n'),
    ("i-width-only", '<Snapshot type="png">\n'
                     '  <Container width="400" color="#38BDF8FF" />\n</Snapshot>\n'),
    ("i-stack-nested", '<Snapshot type="png">\n  <Column>\n    <Row>\n'
                       '      <Container color="#38BDF8FF" />\n    </Row>\n  </Column>\n</Snapshot>\n'),
    ("i-padding-only", '<Snapshot type="png">\n  <Container padding="24">\n'
                       '    <Text fontSize="20" color="#0F172AFF">x</Text>\n'
                       '  </Container>\n</Snapshot>\n'),
    ("i-positioned-only", '<Snapshot type="png">\n'
                          '  <Positioned left="10" top="10" width="100" height="40">\n'
                          '    <Container color="#38BDF8FF" />\n  </Positioned>\n</Snapshot>\n'),
]
out = {}
for tag, dsl in CASES:
    r = snapkit.render(dsl, tag + ".png", tag + ".snapshot", final=False, out_dir=PROBE)
    out[tag] = {"status": r.get("status"), "ok": r.get("ok"),
                "content_type": r.get("content_type"), "error": r.get("error"),
                "dsl": "tmp/%s/A17/probe/%s.snapshot" % (RUN, tag)}
    print("%-24s %s %-16s %s" % (tag, out[tag]["status"], out[tag]["content_type"],
                                 (out[tag]["error"] or "")[:150]))

from PIL import Image  # noqa: E402
for tag in out:
    p = os.path.join(PROBE, tag + ".png")
    if os.path.exists(p):
        out[tag]["image_size"] = list(Image.open(p).size)
        print("   size", out[tag]["image_size"])

json.dump(out, open(os.path.join(PROBE, "errors3.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("WARN", D.warnings())