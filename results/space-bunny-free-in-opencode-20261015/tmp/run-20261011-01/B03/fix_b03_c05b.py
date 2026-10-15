#!/usr/bin/env python
# B03 第 05 件重做。首版三处硬伤，全部是看图才发现的：
#   ① ImageFiltered 里包的是一个 color="#1B2A4500" 的**全透明 Container**，
#      底层那 26 个圆是它的兄弟节点而不是子节点 → 滤镜里根本没有可模糊的内容，
#      渲染出来背景圆是**清晰的**，完全没模糊。technique-notes 当时写的是
#      「作用在同一份 DSL 里真实存在的底层图元上」，与图不符。
#      → 把 26 个圆作为 ImageFiltered 的子节点放进去。
#   ② 「接下来 12 小时」排在 y=366，卡片底边 380，字高 26 → 溢出卡片，悬在外面。
#      → 卡片加高到 312，标签提到柱子上方。
#   ③ 数值列 txt("68mm", 584, w=64) 装不下 5 个字符，**溢出被静默裁掉**，
#      图上显示成「68m」「81mm」不一致。→ 左移到 556、宽度给到 92。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c05b.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
start = s.index('    W, H = 720, 1400')
end = s.index('# ══════════════ 06 ColorFiltered 叠印')
new = '''    W, H = 720, 1400
    b = [rect(0, 0, W, H, "#1B2A45")]
    # ① 背景 26 个圆必须是 ImageFiltered 的**子节点**。
    #    首版把它们放在滤镜外面，而滤镜里只裹了一个全透明 Container，
    #    结果什么都没模糊——这是「滤镜只作用于自身子树」的又一例。
    bg = "".join(circle(40 + (i * 137) % 700, 30 + (i * 211) % 1200,
                        60 + (i % 5) * 70,
                        ["#2E4470", "#38527F", "#243A5E"][i % 3])
                 for i in range(26))
    b.append('<Positioned left="0" top="0" width="720" height="1400">'
             '<ImageFiltered sigmaX="26" sigmaY="26" tileMode="CLAMP">'
             f'<Stack fit="EXPAND">{bg}</Stack>'
             '</ImageFiltered></Positioned>')

    b.append(rect(40, 80, 640, 312, "#0E1A2ECC", 24))
    b.append(txt("降水强度", 72, 112, 400, None, 26, "#8FB3E8"))
    b.append(txt("中雨", 72, 156, 400, None, 64, INK, W600))
    b.append(txt("未来一小时 4.2 mm", 72, 246, 400, None, 28, "#8FB3E8"))
    b.append(txt("接下来 12 小时", 72, 288, 400, None, 22, "#8FB3E8"))
    for i in range(12):
        h = 16 + int(40 * math.sin(i / 12 * math.pi) * (1 - i / 18))
        b.append(rect(72 + i * 50, 358 - h, 30, h, "#4C8DA8", 6))

    b.append(rect(40, 424, 640, 420, "#0E1A2ECC", 24))
    b.append(txt("分区预报", 72, 460, 400, None, 26, "#8FB3E8"))
    zones = [("城东", 68, "#4C8DA8"), ("城西", 42, "#3B6E85"),
             ("江北", 25, "#2E5570"), ("临港", 81, "#E2683C"),
             ("老城", 37, "#3B6E85"), ("开发区", 12, "#24455C")]
    for i, (nm, mm, col) in enumerate(zones):
        y = 512 + i * 52
        b.append(txt(nm, 72, y, 160, None, 24, INK))
        b.append(rect(240, y + 8, 296, 14, "#1E3350", 7))
        b.append(rect(240, y + 8, 296 * mm / 100, 14, col, 7))
        b.append(txt(f"{mm} mm", 552, y, 96, None, 22, "#8FB3E8", align="END"))

    b.append(rect(40, 880, 640, 300, "#0E1A2ECC", 24))
    b.append(txt("出门带伞", 72, 916, 500, None, 40, INK, W600))
    b.append(txt("降水将在 14:20 前后达到峰值，之后逐步减弱。",
                 72, 976, 576, None, 26, "#8FB3E8"))
    b.append(txt("全天累计 11.8 mm", 72, 1022, 576, None, 26, "#8FB3E8"))
    b.append(rect(72, 1080, 576, 66, "#4C8DA8", 33))
    b.append(txt("查看逐小时", 72, 1100, 576, None, 26, INK, W600,
                 align="CENTER"))
    footer(b, 40, H - 84, 640, "界面稿；降水量为示例数据")
    return canvas(W, H, "".join(b), "#1B2A45")


'''
s = s[:start] + new + s[end:]
p.write_text(s, encoding="utf-8")
print("c05 rebuilt")