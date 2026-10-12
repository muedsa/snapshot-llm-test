"""把 log_b05.py 里 add() 的第 4 个参数（手写的 parent）统一改成 None。

改造原因：iteration_id 现在由 add() 内部顺序编号，parent 也由它按序号推导，
所以调用处手写的 "B05-v13" 之类父版本号是多余的，且不同 case 会撞号
（实测导致 B05-v13 出现 5 次、B05-v14 出现 2 次）。
"""
import io
import re

P = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\B05\log_b05.py"

s = io.open(P, encoding="utf-8").read()
pat = re.compile(r'(add\("[a-z0-9-]+", "[a-z-]+", "\d+", )"B05-v\d+", ')
s2, n = pat.subn(r"\1None, ", s)

io.open(P, "w", encoding="utf-8", newline="\n").write(s2)
print("rewrote %d hand-written parent arguments" % n)