# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = 'tmp/20261016T164020-m1/A07/build_a07.py'
t = open(p, encoding='utf-8').read()
subs = [
  ('gl2 = "未设无障碍 · 仅乘车通过"\nfit("图例noacc", gl2, 20, 230)',
   'gl2 = "未设无障碍 · 仅乘车通过"\nfit("图例noacc", gl2, 20, 240)'),
  ('S1.append(text(980, 172, corner, 20, FAINT, family=FAM_MIX, align="END", box_w=290))',
   'S1.append(text(990, 172, corner, 20, FAINT, family=FAM_MIX, align="END", box_w=300))'),
  ('acc_note_1 = "可无障碍乘坐：沿同一路径；换乘站 中心 已设设施"\nfit("卡注1", acc_note_1, 20, 420)',
   'acc_note_1 = "可无障碍乘坐（换乘站 中心 已设设施）"\nfit("卡注1", acc_note_1, 20, 420)'),
  ('a3 = "可无障碍乘坐：沿同一路径；换乘站 工坊 已设设施"\nfit("卡注3", a3, 20, 420)',
   'a3 = "可无障碍乘坐（换乘站 工坊 已设设施）"\nfit("卡注3", a3, 20, 420)'),
]
for a, b in subs:
    assert t.count(a) == 1, ('MISS', a[:40])
    t = t.replace(a, b)
open(p, 'w', encoding='utf-8').write(t)
print('fitx patched')
