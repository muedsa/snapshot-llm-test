#!/usr/bin/env python
# 修 build_b03.py 第 04 件：上一版替换把 b.append(...) 的左括号也吃掉了。
# 这次直接把整块 SWEEP 渐变的 6 行整体替换成正确写法。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_bytes2.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
lines = p.read_text(encoding="utf-8").split("\n")
start = next(i for i, l in enumerate(lines)
             if "gradientType=\"SWEEP\"" in l) - 1
end = next(i for i, l in enumerate(lines)
           if l.strip().startswith("gradientCenter=\"CENTER\" gradientTileMode"))
new = [
    "    b.append('<Positioned left=\"0\" top=\"0\" width=\"1000\" height=\"1000\">'",
    "             '<Container width=\"1000\" height=\"1000\" gradientType=\"SWEEP\" '",
    "             'gradientColors=\"#FF3B6B,#FFB03B,#4ADE80,#3BA7FF,#9B6BFF,#FF3B6B\" '",
    "             'gradientStartAngle=\"0\" gradientEndAngle=\"6.2832\" '",
    "             'gradientCenter=\"CENTER\" gradientTileMode=\"CLAMP\"/>'",
    "             '</Positioned>')",
]
lines[start:end + 1] = new
p.write_text("\n".join(lines), encoding="utf-8")
print("replaced lines", start, "-", end)