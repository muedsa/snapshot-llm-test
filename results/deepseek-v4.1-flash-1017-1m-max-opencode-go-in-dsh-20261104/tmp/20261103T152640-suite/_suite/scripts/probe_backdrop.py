# -*- coding: utf-8 -*-
"""Probe: which construct actually blurs only the background behind a card?"""
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402

TMP = SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "probes"
TMP.mkdir(parents=True, exist_ok=True)

parts = []
parts.append(K.text(20, 16, "A: BackdropFilter + SizedBox", size=16, color="#FFFFFF"))
parts.append(K.text(300, 16, "B: BackdropFilter + 1/255 fill", size=16, color="#FFFFFF"))
parts.append(K.text(580, 16, "C: ClipRRect + ImageFiltered copy", size=16, color="#FFFFFF"))

for i, x0 in enumerate((30, 310, 590)):
    for j, color in enumerate(("#22D3EE", "#FBBF24", "#A78BFA", "#34D399")):
        parts.append(K.rect(x0, 60 + j * 30, 200, 12, color=color, radius=6))

# A
parts.append('<Positioned left="30" top="70"><ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS">'
             '<BackdropFilter sigmaX="12" sigmaY="12" tileMode="CLAMP">'
             '<SizedBox width="200" height="130"/></BackdropFilter></ClipRRect></Positioned>')
# B
parts.append('<Positioned left="310" top="70"><ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS">'
             '<BackdropFilter sigmaX="12" sigmaY="12" tileMode="CLAMP">'
             '<Container width="200" height="130" color="#00000001"/></BackdropFilter></ClipRRect></Positioned>')
# C: blurred copy of the same stripes, clipped
copy = []
for j, color in enumerate(("#22D3EE", "#FBBF24", "#A78BFA", "#34D399")):
    copy.append(K.rect(590, 60 + j * 30, 200, 12, color=color, radius=6))
parts.append('<Positioned left="590" top="70"><ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS">'
             '<ImageFiltered sigmaX="12" sigmaY="12" tileMode="CLAMP">'
             '<SizedBox width="200" height="130"><Stack alignment="TOP_LEFT">'
             + "".join(K.rect(590, 60 + j * 30, 200, 12, color=color, radius=6)
                       for j, color in enumerate(("#22D3EE", "#FBBF24", "#A78BFA", "#34D399")))
             + '</Stack></SizedBox></ImageFiltered></ClipRRect></Positioned>')

for x0 in (30, 310, 590):
    parts.append(K.rect(x0, 70, 200, 130, color="#FFFFFF14", radius=20, border="1 SOLID #FFFFFF33"))

dsl = K.document(800, 220, parts, background="#0B1220")
path = TMP / "backdrop-probe.snapshot"
path.write_text(dsl, encoding="utf-8")
log = api.TaskLogger("_suite", TMP)
rec = log.render(path, TMP / "backdrop-probe.png", "backdrop filter semantics")
print(rec["http_status"], rec["content_type"], rec["response_bytes"])
if rec["http_status"] != 200:
    print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1500])
