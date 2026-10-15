#!/usr/bin/env python
# 续 restore_b03_c04_c07.py：fix_*.py 里的 new = '''…''' 只包含**函数体**
# （从 `    W, H = …` 起），`def cNN():` 与文档字符串在原文件里，已被误删的切片
# 一起丢了。这里把三段函数体各自补回头。
# 启动基准：总任务根 (suite_root)。用法：python restore_b03_headers.py
from pathlib import Path

HERE = Path(__file__).parent
BUILD = HERE / "build_b03.py"

HEADS = {
    "C05": '''def c05():
    """真实场景：天气 App 的「降水强度」浮层卡。

    手法：`ImageFiltered` 对**同一份 DSL 里真实存在的底层图元**做高斯模糊。
    那些图元必须是滤镜的**子节点**——首版把它们放在滤镜外面，
    滤镜里只裹了一个全透明 Container，结果什么都没模糊。

    手法之外还顺带记了两条纯排版边界：数值列宽度不够会被静默裁字，
    以及卡片内元素排到卡片底边之外会挂出去。
    """

''',
    "C06": '''def c06():
    """真实场景：独立书店海报的丝网印刷套色校样。

    手法：`ColorFiltered` + Skia `blendMode="MULTIPLY"` 模拟**油墨叠印**，
    交叠处自然变深。blendMode 是在**滤镜自身边界内**与背板混合的，
    所以整块版区都会上墨——这恰好等于丝印的整版上墨。

    版内图元一律用相对坐标，两个版本各自装进自己的 Positioned；
    用画布绝对坐标会二次偏移。
    """

''',
    "C07": '''def c07():
    """真实场景：住宅方案的日照分析图（平面）。

    手法：用 `Transform` 的 2D 旋转把**投影带**绕楼体中心摆成四个真实太阳
    方位角（135°/157.5°/202.5°/225°），影长按等效楼高 30 m 与冬至日高度角
    （18°/30°/30°/18°）换算。

    平面日照图里入射光线与投影**共线**，都沿太阳反方向；
    首版把日照条以圆心为原点向两侧摆，结果被楼体整个盖住，等于没做。
    """

''',
}

s = BUILD.read_text(encoding="utf-8")
for key, head in HEADS.items():
    marker = f"# {key} = block("
    i = s.index("    W, H = ") if key != "C07" else None
# 逐个：找到对应函数体的第一行 W, H = ，在它前面插入 def 头
ANCHORS = [
    ('    W, H = 720, 1400', "C05"),
    ('    W, H = 1000, 1300', "C06"),
    ('    W, H = 1200, 900', "C07"),
]
for marker, key in ANCHORS:
    assert s.count(marker) == 1, (marker, s.count(marker))
    s = s.replace(marker, HEADS[key] + marker)
BUILD.write_text(s, encoding="utf-8")

import re
print("defs:", re.findall(r"^def (c\d\d|_mat)", s, re.M))