import os
import re

p = r'tmp\20261004-182918\A23\log_a23.py'
s = open(p, encoding='utf-8').read()
tmp = r'tmp\20261004-182918\A23'
out = r'outputs\20261004-182918\A23'

bad = []
for m in re.finditer(r'draft\("([^"]+)"\)', s):
    f = os.path.join(tmp, 'drafts', m.group(1))
    if not os.path.exists(f):
        bad.append(f)
for m in re.finditer(r'os\.path\.join\(DRAFTS, "([^"]+)"\)', s):
    f = os.path.join(tmp, 'drafts', m.group(1))
    if not os.path.exists(f):
        bad.append(f)
for m in re.finditer(r'os\.path\.join\(PREVIEW, "([^"]+)"\)', s):
    f = os.path.join(tmp, 'preview', m.group(1))
    if not os.path.exists(f):
        bad.append(f)
print('missing dsl refs:', bad if bad else 'NONE')

miss2 = []
for m in re.finditer(r'png\("([^"]+)"\)', s):
    f = os.path.join(out, m.group(1))
    if not os.path.exists(f):
        miss2.append(f)
for m in re.finditer(r'prev\("([^"]+)"\)', s):
    f = os.path.join(tmp, 'preview', m.group(1))
    if not os.path.exists(f):
        miss2.append(f)
print('missing img refs:', miss2 if miss2 else 'NONE')

body = s.replace('def draft(', '')
print('draft() helper still referenced:', 'draft("' in body)
print('PREVIEW defined:', 'PREVIEW = ' in s)
