# -*- coding: utf-8 -*-
"""Find the exact border-width rule that triggers INTERNAL_ERROR."""
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


def probe(name, bw, boxw=180, boxh=80, radius=None):
    rad = ' borderRadius="%s"' % radius if radius is not None else ""
    inner = ('<Container color="#4E7391FF"%s border="%s SOLID #4E7391FF" width="%d" height="%d" />'
             % (rad, bw, boxw, boxh))
    dsl = ('<Snapshot type="png" background="#16202AFF">\n'
           '  <Container width="%d" height="%d">\n    <Stack fit="EXPAND">\n'
           '      <Positioned left="20" top="20" width="%d" height="%d">\n%s\n'
           '      </Positioned>\n    </Stack>\n  </Container>\n</Snapshot>\n'
           % (boxw + 60, boxh + 60, boxw, boxh, inner))
    with open(os.path.join(PREV, name + ".snapshot"), "w", encoding="utf-8") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=False,
                       out_dir=PREV, max_attempts=1)
    print("%-28s bw=%-6s box=%sx%s r=%-5s ok=%s" % (name, bw, boxw, boxh, radius, r.get("ok")))


for bw in ["1", "2", "3", "4", "5", "6", "7", "8", "8.25", "9", "10"]:
    probe("r-bw-" + bw.replace(".", "_"), bw)
print("--- fractional ---")
for bw in ["1.5", "2.25", "7.5", "8.5", "8.75"]:
    probe("r-bf-" + bw.replace(".", "_"), bw)
print("--- width of box vs border ---")
probe("r-small-box-8", "8", 40, 24)
probe("r-small-box-10", "10", 40, 24)
probe("r-tiny-box-4", "4", 14, 10)
