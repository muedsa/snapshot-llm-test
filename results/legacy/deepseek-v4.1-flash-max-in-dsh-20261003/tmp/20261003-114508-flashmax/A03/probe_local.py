"""A03: compare two ways of localising the frosted-card blur.

bleed-test  : flat Stack, strips + BackdropFilter + text (measured bleed observed)
local-test  : nested Stack, BackdropFilter wraps strips + card + text together
"""
from __future__ import annotations

import os

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TMP = os.path.join(ROOT, "tmp", RUN_ID, "A03")

FLAT = """<Snapshot background="#0B1220FF" type="png">
<Container width="1280" height="800" padding="32">
<Stack alignment="TOP_LEFT" fit="EXPAND">
<Positioned left="0" top="0"><Text fontSize="44" color="#FFFFFFFF" fontFamily="Noto Sans CJK SC" fontStyle="BOLD">Flat Stack Test</Text></Positioned>
<Positioned left="0" top="60"><Container width="372" height="100" color="#151E30FF" borderRadius="16" border="1 SOLID #2B3A55FF"/></Positioned>
<Positioned left="0" top="76"><Text fontSize="20" color="#2DD4BFFF" fontFamily="Noto Sans Mono CJK SC">KPI CARD BEFORE FILTER</Text></Positioned>
<Positioned left="230" top="292"><Container width="692" height="22" color="#0E9F8FCC"/></Positioned>
<Positioned left="230" top="330"><Container width="692" height="26" color="#F59E0BCC"/></Positioned>
<Positioned left="230" top="368"><Container width="692" height="22" color="#DB2777CC"/></Positioned>
<Positioned left="326" top="324"><BackdropFilter sigmaX="10" sigmaY="10"><Stack alignment="TOP_LEFT"><Container width="500" height="150" color="#FFFFFF33" borderRadius="24" border="1 SOLID #FFFFFF3D"/></Stack></BackdropFilter></Positioned>
<Positioned left="326" top="360"><Text fontSize="28" color="#FFFFFFFF" fontFamily="Noto Sans CJK SC" fontStyle="BOLD">Background-only blur</Text></Positioned>
</Stack>
</Container>
</Snapshot>
"""

LOCAL = """<Snapshot background="#0B1220FF" type="png">
<Container width="1280" height="800" padding="32">
<Stack alignment="TOP_LEFT" fit="EXPAND">
<Positioned left="0" top="0"><Text fontSize="44" color="#FFFFFFFF" fontFamily="Noto Sans CJK SC" fontStyle="BOLD">Local Stack Test</Text></Positioned>
<Positioned left="0" top="60"><Container width="372" height="100" color="#151E30FF" borderRadius="16" border="1 SOLID #2B3A55FF"/></Positioned>
<Positioned left="0" top="76"><Text fontSize="20" color="#2DD4BFFF" fontFamily="Noto Sans Mono CJK SC">KPI CARD BEFORE FILTER</Text></Positioned>
<Positioned left="230" top="292"><Container width="692" height="150" color="#00000000"/></Positioned>
<Positioned left="230" top="292"><BackdropFilter sigmaX="10" sigmaY="10"><Stack alignment="TOP_LEFT" fit="EXPAND">
<Positioned left="0" top="0"><Container width="692" height="22" color="#0E9F8FCC"/></Positioned>
<Positioned left="0" top="38"><Container width="692" height="26" color="#F59E0BCC"/></Positioned>
<Positioned left="0" top="76"><Container width="692" height="22" color="#DB2777CC"/></Positioned>
<Positioned left="96" top="0"><Container width="500" height="150" color="#FFFFFF33" borderRadius="24" border="1 SOLID #FFFFFF3D"/></Positioned>
<Positioned left="96" top="38"><Text fontSize="28" color="#FFFFFFFF" fontFamily="Noto Sans CJK SC" fontStyle="BOLD">Background-only blur</Text></Positioned>
</Stack></BackdropFilter></Positioned>
</Stack>
</Container>
</Snapshot>
"""

for name, body in (("bleed-test", FLAT), ("local-test", LOCAL)):
    p = os.path.join(TMP, f"{name}.snapshot")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    print(p)
