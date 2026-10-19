# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = 'tmp/20261016T164020-m1/A06/build_a06.py'
lines = open(p, encoding='utf-8').read().splitlines()
# 找到尾部残留块起点：第一处“# 画布与节点布局”（第二次出现）
idxs = [i for i,l in enumerate(lines) if '# 画布与节点布局' in l]
assert len(idxs) == 1, idxs
del lines[idxs[0] - 1:]   # 连同其上面的空行一起删除
open(p, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('trimmed to', len(lines), 'lines')
