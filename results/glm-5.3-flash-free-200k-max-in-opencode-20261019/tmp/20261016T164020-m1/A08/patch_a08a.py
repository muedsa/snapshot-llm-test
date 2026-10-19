# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = "tmp/20261016T164020-m1/A08/build_a08.py"
t = open(p, encoding="utf-8").read()
subs = [
  ('fit("sub", s_sub, 20, 720)', 'fit("sub", s_sub, 20, 1420)'),
  ('fit("leg2c", s2c, 20, 200)', 'fit("leg2c", s2c, 20, 240)'),
  # R1 注拆两行
  ('prow(344, "底层通道直行（经 A 材料实验入口）", 20, FAINT)',
   'prow(344, "底层通道直行", 20, FAINT)\nprow(370, "经 A 材料实验入口", 20, FAINT)'),
  ('pdiv(384)', 'pdiv(408)'),
  # R2 块下移 + 文案换行
  ('S1.extend(chip_letter(PX0 + 15, 418, "R2", 14, 30, R2C, radius=8))',
   'S1.extend(chip_letter(PX0 + 15, 438, "R2", 14, 30, R2C, radius=8))'),
  ('S1.append(text(PX0 + 42, 406, "主题参观", 22, INK, bold=True))',
   'S1.append(text(PX0 + 42, 426, "主题参观", 22, INK, bold=True))'),
  ('prow(446, "必经：S → B → D → E", 22, SUB)', 'prow(468, "必经：S → B → D → E", 22, SUB)'),
  ('S1.append(text(PX0, 480, "47 步 · 94 米", 26, INK, bold=True))',
   'S1.append(text(PX0, 504, "47 步 · 94 米", 26, INK, bold=True))'),
  ('prow(524, "分段：S→B 19 · B→D 16 · D→E 12", 20, FAINT)',
   'prow(550, "分段 19 + 16 + 12 步", 20, FAINT)'),
  ('prow(550, "B 结构剧场入口 (10,4) · D 作品巡览入口 (20,6)", 20, FAINT)',
   'prow(576, "B 结构剧场入口 (10,4)", 20, FAINT)\nprow(602, "D 作品巡览入口 (20,6)", 20, FAINT)'),
  ('pdiv(590)', 'pdiv(638)'),
  ('S1.append(text(PX0, 606, "共享通道（同向重合）", 20, SUB, bold=True))',
   'S1.append(text(PX0, 654, "共享通道（同向重合）", 20, SUB, bold=True))'),
  ('prow(638, "入馆：S → 十字口 (6,10)，9 段", 20, INK)',
   'prow(686, "入馆：S → (6,10) 十字口 · 9 段", 20, INK)'),
  ('prow(664, "R2 北上 · R1 南下 —— 由此分岔", 20, SUB)',
   'prow(712, "R2 北上、R1 南下 → 分岔", 20, SUB)'),
  ('prow(694, "离馆：合流点 (20,10) → E，8 段", 20, INK)',
   'prow(742, "离馆：(20,10) → E · 8 段", 20, INK)'),
  ('prow(720, "R1 北上汇入 · R2 南下汇入，同向东行至 E", 20, SUB)',
   'prow(768, "两线于 (20,10) 合流，同向东行", 20, SUB)'),
  ('prow(752, "样式：R1 橙实线 8px 宽底线", 20, SUB)', 'prow(798, "样式：R1 橙实线 8px 宽底线", 20, SUB)'),
  ('prow(778, "R2 蓝虚线 4px 同中心叠加 · 偏移 0", 20, SUB)',
   'prow(824, "R2 蓝虚线 4px 叠加 · 偏移 0", 20, SUB)'),
  ('prow(808, "方向：沿线三角箭头 橙=R1 · 蓝=R2", 20, SUB)',
   'prow(852, "箭头示方向：橙=R1 · 蓝=R2", 20, SUB)'),
  ('prow(838, "共享段步数计入两线各自总里程", 20, SUB)',
   'prow(878, "共享段步数计入两线里程", 20, SUB)'),
  ('pdiv(868)', 'pdiv(906)'),
  ('S1.append(text(PX0, 886, "S 入口 (0,13) · E 出口 (25,7)", 20, SUB))',
   'S1.append(text(PX0, 924, "S (0,13) · E (25,7)", 20, SUB))'),
  ('S1.append(text(PX0, 914, "格心序列与检查证据", 20, SUB))',
   'S1.append(text(PX0, 952, "格心序列与检查证据", 20, SUB))'),
  ('S1.append(text(PX0, 940, "见 paths.json（同输出根）", 20, FAINT))',
   'S1.append(text(PX0, 978, "见 paths.json（同输出根）", 20, FAINT))'),
  ('S1.append(text(PX0, 968, "未指定的展区可以经过；A–D 为入口点", 20, FAINT))',
   'S1.append(text(PX0, 1004, "未指定展区可经过 · A–D 为入口点", 20, FAINT))'),
  ('S1.append(text(PX0, 994, "非展区边界 · 不推算步行分钟数", 20, FAINT))',
   ''),
]
for a, b in subs:
    assert t.count(a) >= 1, "MISS: " + a[:50]
    t = t.replace(a, b)
open(p, "w", encoding="utf-8").write(t)
print("panel/scale fits patched")
