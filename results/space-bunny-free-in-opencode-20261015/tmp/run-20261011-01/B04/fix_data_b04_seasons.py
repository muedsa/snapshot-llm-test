#!/usr/bin/env python
"""修 data_b04.py：删掉首版拍错行数的四季长列表，改为从 seasons_b04.parse() 读入。

首版把 DJF/MAM/JJA/SON 拍成「一行十个数」的长列表，行数分别是 137/136/126/136，
少了 9–20 个值，肉眼数不出来。seasons_b04.py 改成一行一年、脚本校验行数与
字段数，且它的 J-D 列与本文件的 JDN 逐位一致（已断言），因此以它为准。
"""
from pathlib import Path

p = Path(__file__).with_name("data_b04.py")
s = p.read_text(encoding="utf-8")

start = s.index("# ══════════════ [S1] 四条季节序列")
end = s.index("# ══════════════ [S2] NOAA CO₂")
new = '''# ══════════════ [S1] 四条季节序列（DJF/MAM/JJA/SON）
# 逐行录入在 seasons_b04.py，理由与校验方式见那里；这里只做校验后转出。
import seasons_b04 as _s  # noqa: E402

_Y, _JDN, DJF, MAM, JJA, SON = _s.parse()
assert _JDN == JDN, "seasons_b04 的 J-D 必须与本文件的 JDN 逐位一致"
assert _Y == YEARS

'''
s = s[:start] + new + s[end:]
p.write_text(s, encoding="utf-8")
print("data_b04.py 四季序列改为从 seasons_b04 读入")