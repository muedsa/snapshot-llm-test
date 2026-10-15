#!/usr/bin/env python
# B05-10 收尾：上一版补丁没匹配到原文，导致旧单行与新折行版**同时绘制**。
# 这里按实际文本精确处理：
#   ① 删掉「贴片 1 冷藏中层…」的旧单行（只保留折行版）
#   ② 「86 + 21 + 112 + 4 = 223…」改成折行
#   ③ 「贴片只通过蓝牙直连手机…」改成折行
# 启动基准：总任务根 (suite_root)。用法：python fix_b05_c10b.py
from pathlib import Path
import re

p = Path(__file__).parent / "cases_b05b.py"
s = p.read_text(encoding="utf-8")

# ① 删掉旧的「贴片 1 冷藏中层」单行（折行版已在它后面）
old = ('    b.append(txt("\u8d34\u7247 1 \u51b7\u85cf\u4e2d\u5c42 \u00b7 2 \u51b7\u85cf\u4e0b\u5c42 '
       '\u00b7 3 \u51b7\u51bb\u5ba4 \u2014\u2014 \u4e09\u679a\u5168\u90e8\u5728\u7ebf\uff0c"\n'
       '                 "\u4e0a\u6b21\u540c\u6b65 21:08", LX + 20, y3 + 440 - 30, '
       'LW - 40, None, 15, SUBD))\n')
assert s.count(old) == 1, s.count(old)
s = s.replace(old, "")

# ② 「86 + 21 + 112 + 4 = 223…」→ 折行
m = re.search(r'    b\.append\(txt\("86 \+ 21 \+ 112 \+ 4 = 223[^)]*\)\)\n', s)
assert m, "86+21+112+4 未找到"
s = s[:m.start()] + (
    '    for _i, _ln in enumerate(wrap("86 + 21 + 112 + 4 = 223\uff0c\u5360 239 '
    '\u4ef6\u6b21\u8bb0\u5f55\u4e2d\u7684 93%\uff08\u5176\u4f59\u4e3a\u9648\u53ef'
    '\u5f55\u5165\uff09\u3002", 15, LW - 40)):\n'
    '        b.append(txt(_ln, LX + 20, y + 172 + _i * 20, LW - 40, None, 15, SUB))\n'
) + s[m.end():]

# ③ 「贴片只通过蓝牙直连手机…」→ 折行
m2 = re.search(r'    b\.append\(txt\("\u8d34\u7247\u53ea\u901a\u8fc7\u84dd\u7259\u76f4\u8fde\u624b\u673a[^)]*\)\)\n',
               s, re.S)
assert m2, "蓝牙直连 未找到"
s = s[:m2.start()] + (
    '    for _i, _ln in enumerate(wrap("\u8d34\u7247\u53ea\u901a\u8fc7\u84dd\u7259\u76f4\u8fde'
    '\u624b\u673a\uff0c\u4e0d\u7ecf\u8fc7\u6211\u4eec\u7684\u670d\u52a1\u5668\uff1b'
    '\u5220\u6389\u8fd9\u4e2a\u51b0\u7bb1\u4f1a\u540c\u65f6\u5220\u6389\u5168\u90e8 '
    '239 \u6761\u8bb0\u5f55\u3002", 15, LW - 40)):\n'
    '        b.append(txt(_ln, RX + 20, _ry + _i * 20, LW - 40, None, 15, SUBD))\n'
) + s[m2.end():]

p.write_text(s, encoding="utf-8")
print("c10 三个段落均已折行，旧单行已移除")