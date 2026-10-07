import io, re, sys
p = sys.argv[1]
s = io.open(p, encoding='utf-8').read()
bad = sorted({m for m in re.findall(r'color="(#[0-9A-Za-z]*)"', s)
              if len(m.lstrip('#')) not in (3, 4, 6, 8)})
print("bad colours:", bad)
for b in bad:
    i = s.find('color="%s"' % b)
    print(repr(s[max(0, i - 200):i + 120]))