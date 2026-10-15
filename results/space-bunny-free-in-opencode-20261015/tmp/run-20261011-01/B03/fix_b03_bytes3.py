#!/usr/bin/env python
# 修 build_b03.py 第 04 件：定位 b.append('...SWEEP...') 整块并整体替换。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_bytes3.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
lines = p.read_text(encoding="utf-8").split("\n")
start = next(i for i, l in enumerate(lines) if "b.append(t'<Positioned" in l)
end = next(i for i, l in enumerate(lines)
           if i > start and l.strip().startswith("'</Positioned>')"))
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
print("replaced", start, "-", end)