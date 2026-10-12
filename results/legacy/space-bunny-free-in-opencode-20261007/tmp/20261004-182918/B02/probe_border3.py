# -*- coding: utf-8 -*-
"""Confirm: Container with borderRadius + border fails when borderWidth > radius."""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapkit  # noqa: E402
import state as S  # noqa: E402

TASK = "B02"
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), TMP)
PREV = os.path.join(TMP, "probes")
os.makedirs(PREV, exist_ok=True)


def probe(name, bw, radius):
    inner = ('<Container color="#4E7391FF" borderRadius="%s" border="%s SOLID #4E7391FF" '
             'width="180" height="80" />' % (radius, bw))
    dsl = ('<Snapshot type="png" background="#16202AFF">\n'
           '  <Container width="240" height="120">\n    <Stack fit="EXPAND">\n'
           '      <Positioned left="20" top="20" width="180" height="80">\n%s\n'
           '      </Positioned>\n    </Stack>\n  </Container>\n</Snapshot>\n' % inner)
    with open(os.path.join(PREV, name + ".snapshot"), "w", encoding="utf-8") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=False,
                       out_dir=PREV, max_attempts=1)
    print("bw=%-6s radius=%-6s -> ok=%s" % (bw, radius, r.get("ok")))


probe("s-bw825_r10", "8.25", "10")
probe("s-bw825_r825", "8.25", "8.25")
probe("s-bw825_r8", "8.25", "8")
probe("s-bw825_r82", "8.25", "8.2")
probe("s-bw2_r10", "2", "10")
probe("s-bw2_r2", "2", "2")
probe("s-bw2_r15", "2", "1.5")
