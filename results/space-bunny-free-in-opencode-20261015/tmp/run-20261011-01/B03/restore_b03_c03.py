#!/usr/bin/env python
# c03 重建（改用「直接执行 fix 脚本」的方式，避免手工解析 subs 列表）：
#   c03b 的 new 块 → c03c 的 13 条版面修正 → c03d 的图例缩短。
# 执行时把 fix 脚本里的文件读写换成内存变量，改动照样落到字符串上。
# 启动基准：总任务根 (suite_root)。用法：python restore_b03_c03.py
from pathlib import Path
import math
import re

HERE = Path(__file__).parent
BUILD = HERE / "build_b03.py"

b = (HERE / "fix_b03_c03b.py").read_text(encoding="utf-8")
body = b[b.index("new = '''") + len("new = '''"):b.index("'''\ns = s[:start]")]
body = body.strip("\n")

HEAD = '''def c03():
    """真实场景：海滨城市的每日潮汐预报卡。

    手法：`gradientType="RADIAL"` 把每小时潮位映射成从中心向外的半径，
    半径越长潮越高，渐变把高潮与低潮自然分开。

    渐变 Container 是不透明的，必须画在**所有数据之前**——首版把它 append 在
    最后，840×840 的方块把标题、24 个潮位点、页脚全盖住了。
    """
'''


def apply(script: str, text: str) -> str:
    """在内存里跑一遍 fix 脚本的替换逻辑，取回结果。"""
    src = (HERE / script).read_text(encoding="utf-8")
    src = src.replace('p = Path(__file__).with_name("build_b03.py")', 'p = _P')
    src = src.replace('s = p.read_text(encoding="utf-8")', 's = _S')
    src = re.sub(r"^print\(", "_noop(", src, flags=re.M)
    scratch = HERE / f"_scratch_{script}.txt"
    ns = {"_P": scratch, "_S": text, "Path": Path, "math": math,
          "__file__": str(HERE / script), "_noop": lambda *a, **k: None}
    exec(compile(src, script, "exec"), ns)
    # 有些脚本写成 p.write_text(s.replace(old, new))，直接把结果落到 scratch
    return scratch.read_text(encoding="utf-8")


text = apply("fix_b03_c03c.py", HEAD + "\n" + body + "\n")
text = apply("fix_b03_c03d.py", text)

src = BUILD.read_text(encoding="utf-8")
i = src.index("def c03():")
j = src.index("def c04():")
BUILD.write_text(src[:i] + text + "\n\n" + src[j:], encoding="utf-8")

out = BUILD.read_text(encoding="utf-8")
print("defs:", re.findall(r"^def (c\d\d|_mat)", out, re.M))
print("sizes:", re.findall(r"^def (c\d\d)\(\):\n(?:.*\n)*?    W, H = (\d+) x (\d+)",
                            out, re.M))