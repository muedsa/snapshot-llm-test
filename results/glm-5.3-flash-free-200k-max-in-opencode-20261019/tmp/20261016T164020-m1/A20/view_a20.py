# -*- coding: utf-8 -*-
"""A20 查看辅助：整图 + 中心六点口袋 + 右栏 + M15/M09 引导走廊 + 底部金色标签。"""
from PIL import Image

D = "outputs/20261016T164020-m1/A20/"
S = "tmp/20261016T164020-m1/A20/steps/"

im = Image.open(D + "annotated-map.png")
print("size:", im.size)
im.resize((1120, 770), Image.LANCZOS).save(S + "a20-half.png")

# 中心口袋: M06/M08/M09/M10/M11/M12 锚点与标签 (x 620..1080, y 410..700)
im.crop((620, 410, 1080, 700)).resize((920, 580), Image.NEAREST).save(S + "a20-zoom-pocket.png")

# 右栏: M18/M09/M15 槽位标签 (x 1280..1600, y 160..740)
im.crop((1280, 160, 1600, 740)).resize((640, 1160), Image.NEAREST).save(S + "a20-zoom-margin.png")

# M15 引导走廊 (上行 y587 走廊 + 东移南下 + 导轨/入槽)
im.crop((560, 520, 1420, 830)).resize((1720, 620), Image.NEAREST).save(S + "a20-zoom-m15line.png")

# M09 北上走廊 (点顶→y380→导轨1336→槽554)
im.crop((700, 170, 1420, 640)).resize((1440, 940), Image.NEAREST).save(S + "a20-zoom-m09line.png")

# 底部: M23 金框 + M16/M17/M19/M22 标签与近邻
im.crop((660, 700, 1420, 880)).resize((1520, 360), Image.NEAREST).save(S + "a20-zoom-bottom.png")
print("views written")
