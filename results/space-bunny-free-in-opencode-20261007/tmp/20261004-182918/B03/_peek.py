import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
s = io.open('drafts/v001-case-10.snapshot', encoding='utf-8').read()
print([m.group(1) for m in re.finditer(r'width="22" height="([-0-9.]+)"', s)])