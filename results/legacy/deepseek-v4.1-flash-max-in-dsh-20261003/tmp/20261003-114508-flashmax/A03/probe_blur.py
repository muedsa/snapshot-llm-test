"""A03: probe how ImageFiltered vs BackdropFilter treat card text.

Builds two 1280x800 variants that differ only in the filter tag, so the choice for the
final 'System Pulse' card is based on an observed image, not on an assumption.
"""
from __future__ import annotations

import os

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TMP = os.path.join(ROOT, "tmp", RUN_ID, "A03")
os.makedirs(TMP, exist_ok=True)

BODY = """
      <Positioned left="280" top="256"><Container width="700" height="24" color="#0E9F8FAA"/></Positioned>
      <Positioned left="280" top="304"><Container width="700" height="26" color="#F59E0BAA"/></Positioned>
      <Positioned left="280" top="352"><Container width="700" height="22" color="#DB2777AA"/></Positioned>
      <Positioned left="280" top="424"><Container width="700" height="30" color="#7C3AEDAA"/></Positioned>
      <Positioned left="280" top="470"><Container width="700" height="36" color="#22D3EEAA"/></Positioned>
      <Positioned left="280" top="524"><Container width="700" height="44" color="#A3E635AA"/></Positioned>
      <Positioned left="390" top="368">
        <FILTER sigmaX="12" sigmaY="12"><Container width="500" height="150" color="#FFFFFF33" borderRadius="24"/></FILTER>
      </Positioned>
      <Positioned left="390" top="368"><Container width="500" height="150" alignment="CENTER">
        <Text fontSize="28" color="#FFFFFFFF" fontFamily="Noto Sans CJK SC" fontStyle="BOLD">Background-only blur</Text>
      </Container></Positioned>"""

for tag in ("ImageFiltered", "BackdropFilter"):
    dsl = f"""<Snapshot background="#0B1220FF" type="png">
  <Container width="1280" height="800" padding="(24,32)">
    <Stack alignment="TOP_LEFT">
      <Positioned left="0" top="0"><Text fontSize="44" color="#FFFFFFFF" fontFamily="Noto Sans CJK SC" fontStyle="BOLD">{tag} 变体</Text></Positioned>
{BODY.replace("FILTER", tag)}
    </Stack>
  </Container>
</Snapshot>
"""
    p = os.path.join(TMP, f"probe-blur-{tag}.snapshot")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dsl)
    print(p)
