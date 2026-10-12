import os
from pathlib import Path
ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"]); RID = os.environ["SNAPSHOT_RUN_ID"]
d = (ROOT / "outputs" / RID / "A14" / "card-K01.snapshot").read_text(encoding="utf-8")
needle = "radius=" + chr(34) + "9"
print("count radius:", d.count("radius"))
print("count borderRadius:", d.count("borderRadius"))
print("needle:", repr(needle), "in d:", needle in d)
i = d.find("borderRadius")
print("slice:", repr(d[i:i + 22]))
print("per-char:", [hex(ord(ch)) for ch in d[i:i + 22]])
print("needle chars:", [hex(ord(ch)) for ch in needle])
print("find needle:", d.find(needle))
PYEOF_MARKER = None
