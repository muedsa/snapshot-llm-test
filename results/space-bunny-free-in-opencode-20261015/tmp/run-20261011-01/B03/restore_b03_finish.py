#!/usr/bin/env python
# 续上一步：上一次 assert 失败在写文件之前，所以 def 头一个都没补上。
# 这次按内容定位、一次性把 c05 的 def 头、c06 的整件、c07 的 def 头补齐。
# 注意 c06 的 new 块**不含** `    W, H = 1000, 1300`（它在原切片起点之前），
# 所以要单独补这一行。
# 启动基准：总任务根 (suite_root)。用法：python restore_b03_finish.py
from pathlib import Path
import re

HERE = Path(__file__).parent
BUILD = HERE / "build_b03.py"
lines = BUILD.read_text(encoding="utf-8").split("\n")


def block(script: str) -> str:
    txt = (HERE / script).read_text(encoding="utf-8")
    i = txt.index("new = '''") + len("new = '''")
    j = txt.index("'''\ns = s[:start]", i)
    return txt[i:j]


HEAD_C05 = '''def c05():
    """真实场景：天气 App 的「降水强度」浮层卡。

    手法：`ImageFiltered` 对**同一份 DSL 里真实存在的底层图元**做高斯模糊。
    那些图元必须是滤镜的**子节点**——首版把它们放在滤镜外面，滤镜里只裹了一个
    全透明 Container，结果什么都没模糊。

    同时记录两条纯排版边界：数值列宽度不够会被静默裁字；
    卡片内元素排到卡片底边之外会挂出去。
    """
'''
HEAD_C06 = '''def c06():
    """真实场景：独立书店海报的丝网印刷套色校样。

    手法：`ColorFiltered` + Skia `blendMode="MULTIPLY"` 模拟**油墨叠印**，
    交叠处自然变深。blendMode 是在**滤镜自身边界内**与背板混合的，
    所以整块版区都会上墨——这恰好等于丝印的整版上墨。

    版内图元一律用相对坐标，两个版本各自装进自己的 Positioned；
    用画布绝对坐标会二次偏移。
    """
'''
HEAD_C07 = '''def c07():
    """真实场景：住宅方案的日照分析图（平面）。

    手法：用 `Transform` 的 2D 旋转把**投影带**绕楼体中心摆成四个真实太阳
    方位角（135°/157.5°/202.5°/225°），影长按等效楼高 30 m 与冬至日高度角
    （18°/30°/30°/18°）换算。

    平面日照图里入射光线与投影**共线**，都沿太阳反方向；
    首版把日照条以圆心为原点向两侧摆，结果被楼体整个盖住，等于没做。
    """
'''

i5 = lines.index("    W, H = 720, 1400")
lines[i5:i5] = HEAD_C05.split("\n")

# c05 块尾 → 紧跟其后插入 c06 整件
i5ret = next(i for i in range(i5, len(lines))
             if lines[i].strip() == 'return canvas(W, H, "".join(b), "#1B2A45")')
C06 = (HEAD_C06 + "\n    W, H = 1000, 1300\n" + block("fix_b03_c06b.py").strip("\n")
       + '\n    return canvas(W, H, "".join(b), "#F2EDE2")\n')
lines[i5ret + 1:i5ret + 1] = C06.split("\n")

# c07 块体（第一个位于 c06 之后的 1200×900）
i6ret = next(i for i in range(i5ret, len(lines))
             if lines[i].strip() == 'return canvas(W, H, "".join(b), "#F2EDE2")')
i7 = next(i for i in range(i6ret, len(lines)) if lines[i] == "    W, H = 1200, 900")
lines[i7:i7] = HEAD_C07.split("\n")

BUILD.write_text("\n".join(lines), encoding="utf-8")
out = BUILD.read_text(encoding="utf-8")
print("defs:", re.findall(r"^def (c\d\d|_mat)", out, re.M))
for m in re.finditer(r"^def (c\d\d)\(\):\n(?:.*\n)*?    W, H = (\d+) x (\d+)",
                     out, re.M):
    print(" ", m.group(1), m.group(2) + "x" + m.group(3))