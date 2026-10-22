# -*- coding: utf-8 -*-
"""Two evidence/path corrections in generators.

1. _gen_gallery.py: SRC-01 lives under tmp/.../B05/research/, not B05/.
2. _gen_portfolio.py: name case-06 card-1's action exactly as rendered.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def sub(path, old, new, must=True):
    p = os.path.join(HERE, path)
    s = io.open(p, encoding="utf-8").read()
    if old not in s:
        if must:
            sys.exit("MISSING in %s: %r" % (path, old))
        print("skip", path)
        return
    s = s.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    print("patched", path, "->", new[:40])


sub("_gen_gallery.py",
    "B05/SRC-01-cma-rainstorm-warning.txt",
    "B05/research/SRC-01-cma-rainstorm-warning.txt")

sub("_gen_portfolio.py",
    "每卡带可解释动作（查看/改道/稍后提醒）；v3 实看发现紧卡缺动作后 v4 补齐",
    "三卡动作逐条可解释：预警卡『了解暴雨预警分级』、禁行卡『建议立即改走解放路地道』(改道)、"
    "路线卡『查看路线』+『稍后提醒』；v3 实看发现紧卡缺动作后 v4 补齐")
