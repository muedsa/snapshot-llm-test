#!/usr/bin/env python
# 修 build_b03.py：第 04 件误用了 bytes 字面量前缀 b'...'，与其他 str 片段混排会报
# "cannot mix bytes and nonbytes literals"。统一改成普通字符串。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_bytes.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
lines = p.read_text(encoding="utf-8").split("\n")
# 第 04 件的 SWEEP 渐变块（0 起算的第 177..183 行）
for i in range(177, 184):
    if "b'" in lines[i] or 'b"' in lines[i]:
        lines[i] = lines[i].replace("b'", "'").replace('b"', '"')
p.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines[177:184]))