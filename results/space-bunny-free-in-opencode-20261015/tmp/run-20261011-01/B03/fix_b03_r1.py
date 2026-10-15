#!/usr/bin/env python
# B03 首批渲染后的三处修正（依据见每条注释里的服务报错）：
#   03 gradientFocal 只接受 alignment 常量，不接受颜色 —— 焦点色改用第二段渐变色
#   05 「每/小」被写成了乱码替换字符
#   07 border 的样式枚举里没有 DASHED，只能 SOLID —— 虚线改成手动画线段
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_r1.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
subs = [
    # 03：gradientFocal 是 alignment（TOP_LEFT/CENTER/…），不是颜色；焦点色靠
    #     第二个 gradientStops 控制。doc 只写「显式设置半径时必须指定焦点」。
    ("             gradientCenter=\"CENTER\" '\n"
     "             f'gradientRadius=\"0.72\" gradientFocal=\"#9BE8F5\" '\n"
     "             f'gradientFocalRadius=\"0.22\"/></Positioned>')",
     "             gradientCenter=\"CENTER\" '\n"
     "             f'gradientRadius=\"0.72\" gradientStops=\"0,0.22,1\" '\n"
     "             f'gradientFocal=\"CENTER\" gradientFocalRadius=\"0.22\"/>'\n"
     "             f'</Positioned>')"),
    ("b.append(txt(\"���小时 4.2 mm\"", "b.append(txt(\"未来一小时 4.2 mm\""),
    # 07：BorderStyle 只有 SOLID 等，DASHED 会 400；虚线自己画线段
    ("b.append(circle(GX, GY, 380, None, border=\"1 DASHED #DED8CB\"))",
     "for _k in range(24):  # 原 border=\"1 DASHED\" 不被支持，改为手动画虚线\n"
     "        _a = _k / 24 * math.tau\n"
     "        _r1, _r2 = 372, 388\n"
     "        b.append(segment(GX + _r1 * math.sin(_a), GY - _r1 * math.cos(_a),\n"
     "                         GX + _r2 * math.sin(_a), GY - _r2 * math.cos(_a),\n"
     "                         \"#DED8CB\", 1))"),
]
missing = [a for a, _ in subs if a not in s]
for a, bb in subs:
    s = s.replace(a, bb)
p.write_text(s, encoding="utf-8")
print("applied", len(subs) - len(missing), "of", len(subs))
if missing:
    print("MISSING first:", repr(missing[0][:90]))