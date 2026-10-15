#!/usr/bin/env python
# c06 恢复后缺了结尾：说明行与页脚原本在 fix_b03_c06b.py 的 new 块**之后**
# （属于原文件的 s[end:] 部分），随误删一起没了。补回，并采用 c06c 定稿的文案
# （如实说明「整版上墨」）。
# 版区：py=168 与 608，各高 360 → 第二块底 968，分隔线 980，说明放 1010，
# 页脚 H-50=1250，互不相交。
# 启动基准：总任务根 (suite_root)。用法：python restore_b03_c06_tail.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
anchor = ('        b.append(rect(60, py + PH + 12, PW, 1, "#D8D0C0"))\n'
          '    return canvas(W, H, "".join(b), "#F2EDE2")')
new = ('        b.append(rect(60, py + PH + 12, PW, 1, "#D8D0C0"))\n'
       '    b.append(txt("上：单版墨蓝。下：朱红整版以 MULTIPLY 叠上去——滤镜在自身边界内"\n'
       '                 "与背板混合，所以满版上墨；文字与色块的交叠处叠了两层，颜色最深。",\n'
       '                 60, 1010, 880, None, 22, "#8A7F6B"))\n'
       '    footer(b, 60, H - 50, 880, "校样稿；配色为示例")\n'
       '    return canvas(W, H, "".join(b), "#F2EDE2")')
assert s.count(anchor) == 1, s.count(anchor)
p.write_text(s.replace(anchor, new), encoding="utf-8")
print("c06 tail restored")