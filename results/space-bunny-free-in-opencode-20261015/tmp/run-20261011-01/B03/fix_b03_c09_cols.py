#!/usr/bin/env python
# c09 修正（看图发现）：百分比文本 txt(..., xs[3]+244, w=90) 占 884–974，
# 而状态徽章 rect(xs[4]=900, w=120) 盖住 900–1020，**后画的徽章把数字切掉**，
# 渲染出来是「9:」「7:」「10」「6」「8」「9」——百分比这一列等于废了。
# 重新分配：条 640–870 → 百分比 880–944 → 徽章 960–1070 → 岗位 1086–1316。
# 表头「状态」同步移到 960。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c09_cols.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
subs = [
    ("    xs = [56, 200, 380, 640, 900]", "    xs = [56, 200, 380, 640, 960]"),
    ('        b.append(txt(f"{pct}%", xs[3] + 244, y + 18, 90, None, 22, col))',
     '        # 百分比独占 880–944；徽章从 960 起，两者不再相交（否则会被后画的\n'
     '        # 徽章切掉数字，图上显示成「9:」）\n'
     '        b.append(txt(f"{pct}%", xs[3] + 240, y + 18, 64, None, 22, col))'),
    ('        b.append(rect(xs[4], y + 16, 120, 32, ("#E8F2E4" if ok else "#FBEEE0"), 16))\n'
     '        b.append(txt(st, xs[4], y + 22, 120, None, 20, "#4A7A32" if ok else "#A85A28",\n'
     '                     W600, align="CENTER"))\n'
     '        b.append(txt(f"岗位：{\'灯光组\' if grp == \'灯光\' else grp + \'组\'}",\n'
     '                     xs[4] + 140, y + 20, 300, None, 20, "#8A857A"))',
     '        b.append(rect(xs[4], y + 16, 110, 32, ("#E8F2E4" if ok else "#FBEEE0"), 16))\n'
     '        b.append(txt(st, xs[4], y + 22, 110, None, 20, "#4A7A32" if ok else "#A85A28",\n'
     '                     W600, align="CENTER"))\n'
     '        b.append(txt(f"岗位：{\'灯光组\' if grp == \'灯光\' else grp + \'组\'}",\n'
     '                     xs[4] + 126, y + 20, 230, None, 20, "#8A857A"))'),
]
missing = [a for a, _ in subs if a not in s]
for a, bb in subs:
    s = s.replace(a, bb)
p.write_text(s, encoding="utf-8")
print("applied", len(subs) - len(missing), "of", len(subs))
if missing:
    print("MISSING:", repr(missing[0][:100]))