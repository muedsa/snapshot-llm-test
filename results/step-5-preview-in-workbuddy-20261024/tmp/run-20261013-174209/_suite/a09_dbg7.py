from pathlib import Path

dsl = Path("tmp/run-20261013-174209/A09/transform-atlas.snapshot").read_text(encoding="utf-8")
i = dsl.find("旋转 90°")
# 从 T02 编号文字往后，找第一个 width="120" 的 Positioned（主体容器）
j = dsl.find('width="120" height="120"', i)
print("found at", j)
print(dsl[j-160:j+520])
