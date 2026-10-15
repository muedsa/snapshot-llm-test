import re
import sys
import pathlib

p = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "outputs/run-20261011-01/A18/rationale.md")
t = p.read_text(encoding="utf-8")
body = re.sub(r"`[^`]*`", "", t)
body = re.sub(r"[#*]", "", body)
cn = len(re.findall(r"[\u4e00-\u9fff]", t))
print("汉字数 =", cn)
print("非空白字符总数(含标点/拉丁) =", len(re.sub(r"\s", "", body)))
print("总字符数(含空白) =", len(t))