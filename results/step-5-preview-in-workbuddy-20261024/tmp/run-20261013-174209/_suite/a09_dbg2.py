import re
from pathlib import Path

dsl = Path("tmp/run-20261013-174209/A09/transform-atlas.snapshot").read_text(encoding="utf-8")
i = dsl.find("旋转 90°")
j = dsl.find("<Stack", i)
print(dsl[j:j + 700])
