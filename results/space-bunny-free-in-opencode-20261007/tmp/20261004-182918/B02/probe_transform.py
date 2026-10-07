# -*- coding: utf-8 -*-
"""Bisect which construct breaks case-01: Transform/origin/alignment probe."""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402
import b02lib as G  # noqa: E402

TASK = "B02"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
PREV = os.path.join(TMP, "probes")
os.makedirs(PREV, exist_ok=True)

M = "(0.707107,-0.707107,0,0,0.707107,0.707107,0,0,0,0,1,0,0,0,0,1)"

TESTS = {}
TESTS["p1_transform_matrix"] = """
<Snapshot type="png" background="#16202AFF">
  <Container width="200" height="200">
    <Stack fit="EXPAND">
      <Positioned left="50" top="50" width="100" height="40">
        <Transform matrix="%s" origin="(0,0)" alignment="CENTER">
          <Container color="#B4552BFF" width="100" height="40"/>
        </Transform>
      </Positioned>
    </Stack>
  </Container>
</Snapshot>
""" % M

TESTS["p2_transform_no_origin"] = """
<Snapshot type="png" background="#16202AFF">
  <Container width="200" height="200">
    <Stack fit="EXPAND">
      <Positioned left="50" top="50" width="100" height="40">
        <Transform matrix="%s">
          <Container color="#B4552BFF" width="100" height="40"/>
        </Transform>
      </Positioned>
    </Stack>
  </Container>
</Snapshot>
""" % M

TESTS["p3_transform_no_align"] = """
<Snapshot type="png" background="#16202AFF">
  <Container width="200" height="200">
    <Stack fit="EXPAND">
      <Positioned left="50" top="50" width="100" height="40">
        <Transform matrix="%s" origin="(0,0)">
          <Container color="#B4552BFF" width="100" height="40"/>
        </Transform>
      </Positioned>
    </Stack>
  </Container>
</Snapshot>
""" % M

TESTS["p4_boxshadow_none"] = """
<Snapshot type="png" background="#16202AFF">
  <Container width="200" height="200">
    <Stack fit="EXPAND">
      <Positioned left="20" top="20" width="100" height="40">
        <Container color="#B4552BFF" width="100" height="40"/>
      </Positioned>
    </Stack>
  </Container>
</Snapshot>
"""

for name in sorted(TESTS):
    dsl = TESTS[name].strip() + "\n"
    with open(os.path.join(PREV, name + ".snapshot"), "w", encoding="utf-8") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=False,
                       out_dir=PREV, max_attempts=1)
    print("%-26s ok=%s status=%s err=%s" % (name, r.get("ok"), r.get("status"),
                                            str(r.get("error"))[:170]))
