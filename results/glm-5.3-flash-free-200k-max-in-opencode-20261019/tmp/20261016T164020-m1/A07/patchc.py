# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = 'tmp/20261016T164020-m1/A07/build_a07.py'
t = open(p, encoding='utf-8').read()
subs = [
  # 1) 芯片字母垂直居中（原公式把 18px 字形按 18px 高定位，实际行盒更高，字母沉底被裁）
  ("    out.append(text(cx - box / 2, cy + (box - size) / 2 - size * 0.18, ch, size, fg,\n"
   "                    family=FN, bold=True, align=\"CENTER\", box_w=box))",
   "    out.append(text(cx - box / 2, cy - size * 0.73, ch, size, fg,\n"
   "                    family=FN, bold=True, align=\"CENTER\", box_w=box))"),
  # 2) 角标 END 盒错位：left 应为 690（右缘 990），原写 990 使盒子伸进面板
  ('S1.append(text(990, 172, corner, 20, FAINT, family=FAM_MIX, align="END", box_w=300))',
   'S1.append(text(690, 172, corner, 20, FAINT, family=FAM_MIX, align="END", box_w=300))'),
  # 3) 删除地图底部脚注（与 S07/S14/S15 标签重叠）
  ('S1.append(text(64, 930, "站序/线路依据 inputs/network.json · 几何核对见 routes.json",\n'
   '               20, FAINT, family=FAM_MIX))\n', ''),
  # 4) S03 书院标签移到站下方，避开 S02 标签与 45° 出线
  ('label_map("S03", "R", 368, 626); label_map("S04", "R", 474, 516)',
   'label_map("S03", "C", 380, 694); label_map("S04", "R", 474, 516)'),
  # 5) S07 终点 B 徽章贴到节点左侧（原位置悬空）
  ('"S07": (550, 880), "S11": (300, 202),',
   '"S07": (460, 886), "S11": (300, 202),'),
  # 6) 面板迷你旅程带收窄，最右站名不越过面板内缘（1560）
  ('    xs = ribbon(S1, 1044, gy + 46, 492, qn, 20.0, chips=False, status=False)',
   '    xs = ribbon(S1, 1052, gy + 46, 468, qn, 20.0, chips=False, status=False)'),
  # 7) 面板底部即被裁的长注改为两行
  ('S1.append(text(1044, ry + 12, "旅程分组卡片见交付二 travel-card；判据与坐标证据见 routes.json。",\n'
   '               20, FAINT, family=FAM_MIX))',
   'S1.append(text(1044, ry + 12, "旅程卡片为交付二 travel-card。", 20, FAINT, family=FAM_MIX))\n'
   'S1.append(text(1044, ry + 40, "判据与坐标证据见 routes.json。", 20, FAINT, family=FAM_MIX))'),
  # 8) 卡二底部两注相撞：左注缩短
  ('fit("卡注2b", "换乘 工坊（G→B）与 中心（B→R）均设无障碍设施", 20, 590)\n'
   'S2.extend(dot_at(64, 848, 6, OKC))\n'
   'S2.append(text(80, 838, "换乘 工坊（G→B）与 中心（B→R）均设无障碍设施", 20, OKC, family=FAM_MIX))',
   'fit("卡注2b", "换乘 工坊、中心均设无障碍设施 ✓", 20, 380)\n'
   'S2.extend(dot_at(64, 848, 6, OKC))\n'
   'S2.append(text(80, 838, "换乘 工坊、中心均设无障碍设施 ✓", 20, OKC, family=FAM_MIX))'),
]
for a, b in subs:
    assert t.count(a) == 1, ('MISS', a[:60])
    t = t.replace(a, b)
open(p, 'w', encoding='utf-8').write(t)
print('v02 patched, chars', len(t))
