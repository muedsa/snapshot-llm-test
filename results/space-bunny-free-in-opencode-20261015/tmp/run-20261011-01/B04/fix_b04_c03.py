#!/usr/bin/env python
# B04-03 修正（看图发现两处叠字）：
#   ① 图例排在 PY−54 / PY−28，即 198 / 224，而报头的来源行就在 202（16px，末到约 220），
#     「DJF 冬 / MAM 春…」四个图例直接盖在来源文字上。
#   ② 底部三段互相压：x 轴刻度在 PY+PH+12=764，标题 808，卡片 844–940，
#     而脚注又在 H−44=896 —— 脚注横线正好切过四张卡片里的数值。
#   → 画布 940→1000，PY 252→286、PH 500→430，图例/刻度/标题/卡片依次下移并拉开，
#     脚注落到 H−52。三段的纵向顺序固定为 286(顶) / 716(底) / 728 / 766 / 800–896 / 948。
# 启动基准：总任务根 (suite_root)。用法：python fix_b04_c03.py
from pathlib import Path

p = Path(__file__).parent / "build_b04.py"
s = p.read_text(encoding="utf-8")

subs = [
    ("def c03():\n    W, H = 1240, 940", "def c03():\n    W, H = 1240, 1000"),
    ("    PX, PY, PW, PH = 96, 252, 1080, 500\n    LO, HI = -0.6, 1.4",
     "    # PY 从 252 下移到 286，让图例（PY−54/PY−28 = 232/258）避开\n"
     "    # 报头来源行（202–220）；PH 500→430，给底部三段让出空间。\n"
     "    PX, PY, PW, PH = 96, 286, 1080, 430\n    LO, HI = -0.6, 1.4"),
]
for a, bb in subs:
    assert s.count(a) == 1, a[:40]
    s = s.replace(a, bb)
p.write_text(s, encoding="utf-8")
print("c03 fixed")