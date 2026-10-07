# -*- coding: utf-8 -*-
"""Narrow the INTERNAL_ERROR: radius>borderWidth? degenerate identity matrix?"""
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


def probe(name, inner):
    dsl = ('<Snapshot type="png" background="#16202AFF">\n'
           '  <Container width="240" height="120">\n'
           '    <Stack fit="EXPAND">\n'
           '      <Positioned left="20" top="20" width="180" height="80">\n'
           + inner +
           '\n      </Positioned>\n    </Stack>\n  </Container>\n</Snapshot>\n')
    with open(os.path.join(PREV, name + ".snapshot"), "w", encoding="utf-8") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=False,
                       out_dir=PREV, max_attempts=1)
    print("%-30s ok=%s %s" % (name, r.get("ok"), str(r.get("error"))[:120]))


probe("q1_radius_gt_border",
      '<Container color="#4E7391FF" borderRadius="4.5" border="8.25 SOLID #4E7391FF" width="180" height="80" />')
probe("q2_radius_lt_border",
      '<Container color="#4E7391FF" borderRadius="1" border="8.25 SOLID #4E7391FF" width="180" height="80" />')
probe("q3_radius_gt_border_smallw",
      '<Container color="#4E7391FF" borderRadius="4.5" border="2 SOLID #4E7391FF" width="180" height="80" />')
probe("q4_border_float_width",
      '<Container color="#4E7391FF" border="2.5 SOLID #4E7391FF" width="180" height="80" />')
probe("q5_border_8hex",
      '<Container color="#4E7391FF" border="2 SOLID #4E739180" width="180" height="80" />')
probe("q6_border_radius_0",
      '<Container color="#4E7391FF" borderRadius="0" border="2 SOLID #4E7391FF" width="180" height="80" />')
probe("q7_degenerate_identity_matrix",
      '<Transform matrix="(1.0,0.0,0,0,-0.0,1.0,0,0,0,0,1,0,0,0,0,1)" origin="(0,0)" alignment="CENTER">'
      '<Container color="#F4EFE6FF" width="60" height="8" /></Transform>')
probe("q8_exact_identity_matrix",
      '<Transform matrix="(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)" origin="(0,0)" alignment="CENTER">'
      '<Container color="#F4EFE6FF" width="60" height="8" /></Transform>')
probe("q9_zero_angle_thickness",
      '<Transform matrix="' + G.rot(0) + '" origin="(0,0)" alignment="CENTER">'
      '<Container color="#F4EFE6FF" width="60" height="8" /></Transform>')
