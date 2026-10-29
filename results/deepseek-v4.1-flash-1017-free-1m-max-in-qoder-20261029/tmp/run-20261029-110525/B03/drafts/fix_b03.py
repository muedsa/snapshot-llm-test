#!/usr/bin/env python3
import re
from pathlib import Path
p = Path('tmp/run-20261029-110525/B03/drafts/gen_b03.py')
s = p.read_text(encoding='utf-8')
def repl(m):
    n, slug, title, desc = m.group(1), m.group(2), m.group(3), m.group(4)
    return f'cases.append(dict(id={n},slug="{slug}",W=W,H=H,bg=bg,title="{title}",desc="{desc}",body="".join(b)))'
s = re.sub(r'cases\.append\(\((\d+),"([^"]+)",W,H,"([^"]*)","([^"]*)"\)\)', repl, s)
tail = s.index('for cid,slug,W,H,title,desc in cases:')
s = s[:tail] + '''for c in cases:
    d=OUT/f"case-{c['id']:02d}"; d.mkdir(parents=True,exist_ok=True)
    (d/'final.snapshot').write_text(page(c['W'],c['H'],c['bg'],c['body']),encoding='utf-8')
    (d/'case.md').write_text(f"# {c['title']}\\n\\n- 场景：{c['desc']}\\n- 手法：{notes[c['id']]}\\n- 主图：final.png（{c['W']}×{c['H']}）；DSL：final.snapshot\\n",encoding='utf-8')
print('B03 wrote',len(cases))
'''
p.write_text(s, encoding='utf-8')
print('patched cases', s.count('cases.append(dict('))
