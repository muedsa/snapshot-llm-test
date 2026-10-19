# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = 'tmp/20261016T164020-m1/A07/build_a07.py'
t = open(p, encoding='utf-8').read()
subs = [
  ('BLOCK = [(32, 148, 656, 268), (32, 432, 656, 404), (32, 852, 656, 268)]',
   'BLOCK = [(32, 148, 656, 272), (32, 432, 656, 452), (32, 900, 656, 252)]'),
  ('xs1 = card_rows(0, BLOCK[0], 232)', 'xs1 = card_rows(0, BLOCK[0], 258)'),
  ('S2.extend(dot_at(64, 350, 6, OKC))', 'S2.extend(dot_at(64, 378, 6, OKC))'),
  ('S2.append(text(80, 340, acc_note_1, 20, OKC, family=FAM_MIX))',
   'S2.append(text(80, 368, acc_note_1, 20, OKC, family=FAM_MIX))'),
  ('S2.append(text(464, 340, p1, 20, SUB, family=FAM_MIX, align="END", box_w=200))',
   'S2.append(text(464, 368, p1, 20, SUB, family=FAM_MIX, align="END", box_w=200))'),
  ('xs2 = card_rows(1, BLOCK[1], 512)', 'xs2 = card_rows(1, BLOCK[1], 542)'),
  ('S2.extend(diamond_ring(64, 624, 8, NOC, 2.2, CARD))',
   'S2.extend(diamond_ring(64, 662, 8, NOC, 2.2, CARD))'),
  ('S2.append(text(80, 614, w1, 20, NOC, family=FAM_MIX))',
   'S2.append(text(80, 652, w1, 20, NOC, family=FAM_MIX))'),
  ('S2.append(quad((56, 652), (664, 652), DIV, 2))', 'S2.append(quad((56, 686), (664, 686), DIV, 2))'),
  ('S2.append(text(56, 668, "无障碍旅程（同样 6 区间 · 换乘 2）", 22, INK, family=FAM_MIX, bold=True))',
   'S2.append(text(56, 700, "无障碍旅程（同样 6 区间 · 换乘 2）", 22, INK, family=FAM_MIX, bold=True))'),
  ('xs3 = ribbon(S2, 64, 736, 600, ac2, 20.0, chips=True, status=True)',
   'xs3 = ribbon(S2, 64, 776, 600, ac2, 20.0, chips=True, status=True)'),
  ('S2.extend(dot_at(64, 802, 6, OKC))', 'S2.extend(dot_at(64, 848, 6, OKC))'),
  ('S2.append(text(80, 792, "换乘 工坊（G→B）与 中心（B→R）均设无障碍设施", 20, OKC, family=FAM_MIX))',
   'S2.append(text(80, 838, "换乘 工坊（G→B）与 中心（B→R）均设无障碍设施", 20, OKC, family=FAM_MIX))'),
  ('S2.append(text(464, 792, p2, 20, SUB, family=FAM_MIX, align="END", box_w=200))',
   'S2.append(text(464, 838, p2, 20, SUB, family=FAM_MIX, align="END", box_w=200))'),
  ('"rows": ["普通 @512", "无障碍 @736"],', '"rows": ["普通 @542", "无障碍 @776"],'),
  ('xs4 = card_rows(2, BLOCK[2], 932)', 'xs4 = card_rows(2, BLOCK[2], 1010)'),
  ('S2.extend(dot_at(64, 1084, 6, OKC))', 'S2.extend(dot_at(64, 1130, 6, OKC))'),
  ('S2.append(text(80, 1074, a3, 20, OKC, family=FAM_MIX))',
   'S2.append(text(80, 1120, a3, 20, OKC, family=FAM_MIX))'),
  ('S2.append(text(464, 1074, p3, 20, SUB, family=FAM_MIX, align="END", box_w=200))',
   'S2.append(text(464, 1120, p3, 20, SUB, family=FAM_MIX, align="END", box_w=200))'),
  ('"ribbon_y_px": 932})', '"ribbon_y_px": 1010})'),
  ('S2.append(text(32, 1140, "换乘 = 改乘线路（首次乘车不计）；按（区间数，换乘数）取最优。", 20, SUB, family=FAM_MIX))',
   'S2.append(text(32, 1164, "换乘 = 改乘线路（首次乘车不计）；按（区间数，换乘数）取最优。", 20, SUB, family=FAM_MIX))'),
  ('S2.append(text(32, 1168, "无障碍约束：起点/终点/换乘站须设设施；未设站可乘车通过。", 20, SUB, family=FAM_MIX))',
   'S2.append(text(32, 1190, "无障碍约束：起点/终点/换乘站须设设施；未设站可乘车通过。", 20, SUB, family=FAM_MIX))'),
  ('S2.append(text(32, 1196, "线网 16 站 = 红 7 + 蓝 6 + 绿 6 − 共享 3；数据源自 inputs/network.json。", 20, SUB, family=FAM_MIX))',
   'S2.append(text(32, 1216, "线网 16 站 = 红 7 + 蓝 6 + 绿 6 − 共享 3；数据源自 inputs/network.json。", 20, SUB, family=FAM_MIX))'),
  ('S2.append(text(32, 1224, "站序/区间/换乘判定与两图坐标证据 见 routes.json。", 20, FAINT, family=FAM_MIX))',
   'S2.append(text(32, 1242, "站序/区间/换乘判定与两图坐标证据 见 routes.json。", 20, FAINT, family=FAM_MIX))'),
]
for a, b in subs:
    assert t.count(a) == 1, ('MISS', a[:50])
    t = t.replace(a, b)
open(p, 'w', encoding='utf-8').write(t)
print('rhythm patched, chars', len(t))
