import re
s = open('outputs/run-20261011-01/A10/compositing-lab.snapshot', encoding='utf-8').read()
tags = sorted(set(re.findall(r'<([A-Za-z]+)', s)))
attrs = sorted(set(re.findall(r'([A-Za-z]+)="', s)))
print('tags:', tags)
print('attrs:', attrs)
print(s[:1500])
