import re
from pathlib import Path

dsl = Path("tmp/run-20261013-174209/A09/transform-atlas.snapshot").read_text(encoding="utf-8")
# 找出所有 Stack（主体）
stacks = re.findall(r'<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE"(?: transform="[^"]*")?[^>]*>', dsl)
print("Stack count:", len(stacks))
for i, s in enumerate(stacks):
    has = "transform=" in s
    print(i, "HAS_TRANSFORM" if has else "NO_TRANSFORM", s[:130])
