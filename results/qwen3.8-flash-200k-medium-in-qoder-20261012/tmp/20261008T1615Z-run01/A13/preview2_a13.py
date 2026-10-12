"""A13 round-2 previews: direction A with the node/invisibility problem fixed.

Three questions the first sheet raised, each answered by a render rather than by opinion:
  A2  thicker stroke (0.070 S) + node in the red accent — does the centre survive on night?
  A3  thicker stroke, no node at all — is the node load-bearing or decoration?
  A4  thicker stroke + node in the blue primary — is the fix about the node or about red
      competing with the top-right frame?
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "A13"))
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
import plan_a13 as P  # noqa: E402

PREVIEW = ROOT / "tmp" / RID / "A13" / "preview"
VARIANTS = {
    "A2": {"stroke": 0.070, "node": P.PALETTE["red"]},
    "A3": {"stroke": 0.070, "node": "none"},
    "A4": {"stroke": 0.070, "node": P.PALETTE["blue"]},
}
sizes = {}
for tag, cfg in VARIANTS.items():
    P.A["stroke"] = cfg["stroke"]
    for size in (512, 32):
        doc = P.Doc(size, size, bg="transparent", font=P.FONT)
        S = size / (1 + 2 * P.CLEAR_SPACE)
        P.icon(doc, size / 2, size / 2, S, "A", "color", node_color=cfg["node"])
        name = f"alt-{tag}-{size}"
        (PREVIEW / f"{name}.snapshot").write_text(doc.dsl(), encoding="utf-8")
        sizes[name] = size
print(json.dumps(sizes))
