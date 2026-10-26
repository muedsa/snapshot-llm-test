import re
from pathlib import Path

dsl = Path("tmp/run-20261013-174209/A09/transform-atlas.snapshot").read_text(encoding="utf-8")
i = dsl.find("旋转 90°")
j = dsl.find("<Stack", i)
# 打印从外层 Container 到该 Stack 的祖先链
seg = dsl[:j]
# 找最近的几个开标签
opens = re.findall(r'<(Snapshot|Container|Stack|Positioned)\b[^>]*>', seg)
print("ancestor-ish tags (last 8 before body Stack):")
for t in opens[-8:]:
    print("   ", t[:120])
print()
print("body stack tag:", dsl[j:j+220])
