import re
from pathlib import Path

dsl = Path("tmp/run-20261013-174209/A09/transform-atlas.snapshot").read_text(encoding="utf-8")
print("total length:", len(dsl))
print("Positioned count:", dsl.count("<Positioned"))
print("Stack count:", dsl.count("<Stack"))
print("Container count:", dsl.count("<Container"))
print("transform count:", dsl.count("transform="))
# 检查根结构是否闭合
print("ends with:", dsl[-80:])
# 检查是否有未闭合
opens = len(re.findall(r"<(Positioned|Stack|Container|Snapshot)\b", dsl))
closes = len(re.findall(r"</(Positioned|Stack|Container|Snapshot)>", dsl))
print("opens:", opens, "closes:", closes)
