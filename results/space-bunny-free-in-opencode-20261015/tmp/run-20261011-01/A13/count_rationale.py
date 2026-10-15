import re
import pathlib

t = pathlib.Path('outputs/run-20261011-01/A13/rationale.md').read_text(encoding='utf-8')
body = re.sub(r'`[^`]*`', '', t)          # 去掉反引号里的文件路径
body = re.sub(r'[#*]', '', body)
cn = len(re.findall(r'[\u4e00-\u9fff]', t))
print('汉字数 =', cn)
print('非空白字符总数(含标点/拉丁, 去掉代码路径) =', len(re.sub(r'\s', '', body)))
print('文件总字符数(含空白/换行) =', len(t))