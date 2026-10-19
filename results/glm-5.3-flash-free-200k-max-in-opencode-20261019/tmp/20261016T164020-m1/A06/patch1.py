import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = 'tmp/20261016T164020-m1/A06/build_a06.py'
t = open(p, encoding='utf-8').read()
old = '''CARD = "#FFFFFF"; BORD = "1 SOLID #E3EAF4"; GRID = "#E1E8F3"
PHASE = {'''
new = '''CARD = "#FFFFFF"; BORD = "1 SOLID #E3EAF4"; GRID = "#E1E8F3"

S = [f'<SizedBox width="{W}" height="{H}" />']
GEO = {}
PHASE = {'''
assert t.count(old) == 1, t.count(old)
open(p, 'w', encoding='utf-8').write(t.replace(old, new))
print('patched')
