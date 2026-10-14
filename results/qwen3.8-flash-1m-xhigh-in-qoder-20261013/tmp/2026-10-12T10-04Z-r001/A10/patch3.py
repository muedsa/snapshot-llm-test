"""A10 patch 3: make the ⑤/⑥ caption and evidence prose match what the scene now does.

v002's ⑤/⑥ scene filled the whole cell, so the text said "整片变橙". After patch 2 the
filtered subtree keeps its own bounds inside the cell, so the wording has to follow.
"""
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
p = ROOT / "tmp" / RUN / "A10" / "gen.py"
s = p.read_text(encoding="utf-8")
orig = s


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new, count)


rep('("⑤", "滤色 + 子树模糊", "MULTIPLY #F6B94A 后 sigma=6，可外溢", "C 组"),',
    '("⑤", "滤色 + 子树模糊", "MULTIPLY #F6B94A 后 sigma=6，间隙被填、边缘外溢", "C 组"),')
rep('("⑥", "再加圆形裁剪", "同样结果套上 r=100 圆裁，边界锐利", "C 组"),',
    '("⑥", "再加圆形裁剪", "同一结果套 r=100 圆裁，弧上锐利截断", "C 组"),')

rep('''                 "⑤ 乘色 #F6B94A 后整片变橙并 sigma=6 模糊，柔化边缘越出原形状与实验区外框，"
                 "在深色底上形成橙色外溢光晕；⑥ 同一结果套 r=100 圆裁后，圆周处出现锐利"
                 "截断线，跨过圆周的绿色矩形被整齐切掉，圆外不再有任何橙色扩散。",''',
    '''                 "⑤ 子树先乘色再 sigma=6 模糊：白卡变橙、形状之间的透明间隙被填成橙色，"
                 "模糊把场景外框边缘向外柔化约 18px，实验区白底与 1px 边框仍完整可见；"
                 "⑥ 同一结果最外层加 r=100 圆裁后，圆周处出现锐利截断线，跨圆的蓝条与红点"
                 "被整齐切掉，圆外回到纯白且不再有橙色扩散。",''')

assert s != orig
p.write_text(s, encoding="utf-8")
print("patched prose")
