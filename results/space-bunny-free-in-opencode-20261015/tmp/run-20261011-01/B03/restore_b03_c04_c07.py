#!/usr/bin/env python
# 事故恢复：fix_b03_c07b.py 用 s.index('    W, H = 1200, 900') 定位第 07 件，
# 但**第 03 件也是 1200×900**，index() 返回的是第一次出现的位置，
# 于是切片把 c04/c05/c06/c07 整段删掉了（c03 也被削掉一截）。
# 教训：定位用唯一锚点（例如函数注释首行或 def 名），不要用重复出现的数值字面量。
# 本脚本按 fix_b03_c04/c05b/c06b/c07b 中**已修正**的版本把四件原样补回。
# 启动基准：总任务根 (suite_root)。用法：python restore_b03_c04_c07.py
from pathlib import Path

HERE = Path(__file__).parent
BUILD = HERE / "build_b03.py"


def block(script: str, start: str, end: str) -> str:
    """从某个 fix_*.py 里取出 new = '''...''' 的内容。"""
    txt = (HERE / script).read_text(encoding="utf-8")
    i = txt.index(start)
    i = txt.index("'''", i) + 3
    j = txt.index("'''", i)
    return txt[i:j]


C05 = block("fix_b03_c05b.py", "new = '''", "\n    s = s[:start] + new + s[end:]")
C06 = block("fix_b03_c06b.py", "new = '''", "\n    s = s[:start] + new + s[end:]")
C07 = block("fix_b03_c07b.py", "new = '''", "\n    s = s[:start] + new + s[end:]")

# c04 没有整块重写脚本，按「原版 + fix_b03_c04.py 的 8 条替换 + 随后的 footer 修正」重建
C04 = '''def c04():
    """真实场景：独立厂牌的唱片封套（内页）。

    手法：`gradientType="SWEEP"` 画**扇形色盘**，再叠同心圆环模拟唱片沟槽。
    扇形渐变在其它标签上很难用到，这里正好对应黑胶旋转的视觉隐喻。
    """
    W, H = 1000, 1000
    b = [rect(0, 0, W, H, "#0E0E12")]
    b.append('<Positioned left="0" top="0" width="1000" height="1000">'
             '<Container width="1000" height="1000" gradientType="SWEEP" '
             'gradientColors="#FF3B6B,#FFB03B,#4ADE80,#3BA7FF,#9B6BFF,#FF3B6B" '
             'gradientStartAngle="0" gradientEndAngle="6.2832" '
             'gradientCenter="CENTER" gradientTileMode="CLAMP"/>'
             '</Positioned>')
    # 首版压了 #0E0E1244 的暗层，把扇形渐变压成灰扑扑的粉彩 → 减到 1A
    b.append(rect(0, 0, 1000, 1000, "#0E0E121A"))
    # SWEEP 的 gradientCenter 只能给对齐常量，所以唱片中心必须与画布正中重合
    for i in range(26):
        rr = 110 + i * 13
        b.append(circle(500, 500, rr * 2, None, border="1 SOLID #FFFFFF33"))
    b.append(circle(500, 500, 182, "#0E0E12"))
    b.append(circle(500, 500, 182, None, border="3 SOLID #FFFFFF88"))
    b.append(circle(500, 500, 22, "#FFFFFF33"))
    b.append(txt("SLOW", 380, 466, 240, None, 44, INK, W600, align="CENTER"))
    b.append(txt("ROTATION", 372, 518, 256, None, 22, "#9AA0AA", align="CENTER"))
    b.append(txt("厂牌 夜潮唱片", 80, 76, 500, None, 24, "#1A1A1E"))
    b.append(txt("慢转 · 33⅓", 80, 812, 600, None, 54, INK, W600))
    b.append(txt("NT-017 · 2026 夏", 80, 878, 600, None, 26, "#1A1A1EF0"))
    b.append(txt("12 吋 · 透明橙胶", 640, 880, 280, None, 22, "#1A1A1ED0",
                 align="END"))
    b.append(rect(80, 928, 840, 1, "#1A1A1E33"))
    b.append(txt("封套设计稿；厂牌与编号为示例", 80, 938, 840, None, 17, "#1A1A1EA6"))
    return canvas(W, H, "".join(b), "#0E0E12")


'''

ANCHOR = "# ══════════════ 08 ClipPath"
s = BUILD.read_text(encoding="utf-8")
assert "def c04(" not in s and "def c07(" not in s
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, C04 + C05 + C06 + C07 + ANCHOR)
BUILD.write_text(s, encoding="utf-8")
import re
print("restored:", re.findall(r"^def (c\d\d|_mat)", s, re.M))