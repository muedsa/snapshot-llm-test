# -*- coding: utf-8 -*-
"""核查 v3 DSL 三处修正是否生效。"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
d = Path(r"D:\mine\test\glm-5.3-flash\tmp\20261016T164020-m1\B06\dsl")
c02 = (d / "case-02_v3.snapshot").read_text(encoding="utf-8")
c03 = (d / "case-03_v3.snapshot").read_text(encoding="utf-8")
c09 = (d / "case-09_v3.snapshot").read_text(encoding="utf-8")

# c03: 二档 13px 粗体的 y 应为 395.75（pb-lv+14）
i = c03.find("二档 0.57")
seg = c03[max(0, i - 220):i]
print("c03 二段上下文含 top:")
for tok in seg.split("<Positioned")[-1:]:
    print(" ", tok[:120])
print("c09 新箭头 left=330 top=252:", 'left="330" top="252"' in c09)
print("c09 胶囊 left=210 top=218:", 'left="210" top="218"' in c09)
print("c02 页脚含 自拟案例分析:", "自拟案例分析" in c02)
print("c02 页脚 box_w=680:", 'width="680"' in c02[c02.find("自拟案例分析") - 400: c02.find("自拟案例分析")])
