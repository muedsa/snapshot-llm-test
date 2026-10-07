import io
p = 'build_a10.py'
s = io.open(p, encoding='utf-8').read()
bad = '\nkids.append(D.hline(48, 1392, 120, "#CBD5E1FF", 1.5))\n'
good = '\n    kids.append(D.hline(48, 1392, 120, "#CBD5E1FF", 1.5))\n'
print('found', s.count(bad))
s = s.replace(bad, good)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
import ast
ast.parse(io.open(p, encoding='utf-8').read())
print('syntax ok')