# -*- coding: utf-8 -*-
"""Second INTERNAL_ERROR hunt for case-02: radii>size, boxShadow alpha, zero-size."""
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


def probe(name, inner, w=1100, h=620):
    dsl = ('<Snapshot type="png" background="#D9D3C6FF">\n'
           '  <Container width="%d" height="%d">\n    <Stack fit="EXPAND">\n'
           '      <Positioned left="30" top="10" width="%d" height="%d">\n%s\n'
           '      </Positioned>\n    </Stack>\n  </Container>\n</Snapshot>\n'
           % (w, h, w - 60, h - 20, inner))
    with open(os.path.join(PREV, name + ".snapshot"), "w", encoding="utf-8") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=False,
                       out_dir=PREV, max_attempts=1)
    print("%-34s ok=%s %s" % (name, r.get("ok"), str(r.get("error"))[:100]))


probe("t1_radii_gt_height",
      '<Container color="#B98A2EFF" borderRadiusTopLeft="14" borderRadiusTopRight="14" '
      'width="1040" height="6" />')
probe("t2_radii_le_height",
      '<Container color="#B98A2EFF" borderRadiusTopLeft="3" borderRadiusTopRight="3" '
      'width="1040" height="6" />')
probe("t3_radius_gt_half_height",
      '<Container color="#B98A2EFF" borderRadius="14" width="1040" height="6" />')
probe("t4_shadow_alpha_hex",
      '<Container color="#22384AFF" borderRadius="14" boxShadow="0 10 26 0 #1B222A3A" '
      'width="1040" height="600" />')
probe("t5_shadow_nonzero_spread",
      '<Container color="#22384AFF" borderRadius="14" boxShadow="0 10 26 3 #1B222A3A" '
      'width="1040" height="600" />')
probe("t6_zero_size",
      '<Container color="#C0B8A6FF" borderRadius="0" width="0" height="0" />')
probe("t7_border_lt_radius_ok",
      '<Container border="1 SOLID #DCD5C6FF" borderRadius="8" width="1008" height="568" />')
probe("t8_shadow_rounding",
      '<Container color="#22384AFF" borderRadius="14" boxShadow="ELEVATION_4" '
      'width="1040" height="600" />')
