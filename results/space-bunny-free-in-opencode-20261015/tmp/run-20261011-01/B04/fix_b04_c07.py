#!/usr/bin/env python
# B04-07 修正 —— 一处**数据错误**，不是版面问题：
#   CO2_RECENT 从 2024-07 起排，索引 0..24。2025-07 在索引 **12**，
#   原代码却写了 CO2_RECENT[6]，那是 2025-01（426.01）。
#   后果有两处，都出在图上：
#     ① 「同比 2025-07」那一栏显示 426.01，实际 2025-07 是 424.09；
#     ② 「月均比一年前高 0.09 ppm」按 426.10−426.01 算，
#        正确的同比是 426.10−424.09 = **2.01 ppm**。
#   → 索引改为 12；顺带把那条派生文案改成按同一数据算，避免两处口径不一致。
#   另外副标题超宽被静默裁掉（停在「黑线是扣除季节循环后」），已缩短到盒宽内。
# 启动基准：总任务根 (suite_root)。用法：python fix_b04_c07.py
from pathlib import Path

p = Path(__file__).parent / "build_b04.py"
s = p.read_text(encoding="utf-8")

subs = [
    # CO2_RECENT 里 2025-07 的正确索引是 12，不是 6（6 是 2025-01）
    ('            ("同比 2025-07", D.CO2_RECENT[6][2], "ppm", COOL))):',
     '            # CO2_RECENT 起于 2024-07，故 2025-07 的索引是 12；\n'
     '            # 原先写 [6] 拿到的是 2025-01，连带把同比算成了 0.09 ppm。\n'
     '            ("同比 2025-07", D.CO2_RECENT[12][2], "ppm", COOL))):'),
    ('    b.append(txt(f"月均比一年前高 {last[2] - D.CO2_RECENT[6][2]:.2f} ppm，"\n'
     '                 f"约合每天增加 {(last[2] - D.CO2_RECENT[6][2]) / 365:.3f} ppm。",\n'
     '                 PX + 28, PY + PH + 190, 900, None, 18, INKD))',
     '    # 与上面那一栏同源，��用索引 12（2025-07），两处口径一致\n'
     '    yoy = last[2] - D.CO2_RECENT[12][2]\n'
     '    b.append(txt(f"与 2025 年 7 月同月相比高 {yoy:.2f} ppm，"\n'
     '                 f"约合每天增加 {yoy / 365:.4f} ppm。",\n'
     '                 PX + 28, PY + PH + 190, 900, None, 18, INKD))'),
    ('"NOAA GML 全球月均 CO₂（ppm）最近 25 个月：红线是原始月均，能看到夏末的下凹；"\n'
     '             "黑线是扣除季节循环后的 trend。",',
     '# 原副标题超宽被静默裁掉（停在「黑线是扣除季节循环后」），缩短到盒宽内\n'
     '             "NOAA GML 全球月均 CO₂ 最近 25 个月。红线为原始月均（可见夏末下凹），"\n'
     '             "黑线为扣除季节循环后的 trend。",'),
]
for a, bb in subs:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, bb)
p.write_text(s, encoding="utf-8")

# 自检：确认索引 12 确实是 2025-07
import sys
sys.path.insert(0, str(Path(__file__).parent))
import data_b04 as D
assert D.CO2_RECENT[12][0] == 2025 and D.CO2_RECENT[12][1] == 7, D.CO2_RECENT[12]
assert abs((D.CO2_RECENT[-1][2] - D.CO2_RECENT[12][2]) - 2.01) < 0.005
print("c07 fixed; index12 =", D.CO2_RECENT[12], " yoy =",
      round(D.CO2_RECENT[-1][2] - D.CO2_RECENT[12][2], 2))