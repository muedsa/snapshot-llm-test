# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = 'tmp/20261016T164020-m1/A07/build_a07.py'
t = open(p, encoding='utf-8').read()
subs = [
  # 1) ribbon 站名：盒心对齐站点（原 left=x 使文字中心右偏 bw/2，末站溢出面板/卡片）
  ('''        bw = max(step - 8, estw(f"{i+1:02d} {nm}", name_size) + 8)
        S.append(text(x, axis + 18, nm, name_size, INK, family=FAM_MIX, bold=True,
                      align="CENTER", box_w=bw))''',
   '''        bw = max(step - 8, estw(nm, name_size) + 12)
        S.append(text(x - bw / 2, axis + 18, nm, name_size, INK, family=FAM_MIX, bold=True,
                      align="CENTER", box_w=bw))'''),
  # 2) S05 东桥标签移到站点下左空区（红线 NW 斜线不再穿过文字）
  ('label_map("S05", "R", 594, 610); label_map("S06", "C", 760, 694)',
   'label_map("S05", "R", 612, 692); label_map("S06", "C", 760, 694)'),
  # 3) 卡二无障碍替代带收窄 600→592，末站名 634..678 不越卡片边缘 688
  ('xs3 = ribbon(S2, 64, 776, 600, ac2, 20.0, chips=True, status=True)',
   'xs3 = ribbon(S2, 64, 776, 592, ac2, 20.0, chips=True, status=True)'),
]
for a, b in subs:
    assert t.count(a) == 1, ('MISS', a[:60])
    t = t.replace(a, b)
open(p, 'w', encoding='utf-8').write(t)
print('v03 patched, chars', len(t))
