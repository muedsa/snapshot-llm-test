import re, pathlib, sys
h = pathlib.Path('tmp/run-20261011-01/_suite/docs/parser-tags.html').read_text(encoding='utf-8', errors='replace')

def clean(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = s.replace('&#x22;', '"').replace('&quot;', '"')
    s = s.replace('&#x3C;', '<').replace('&#x3E;', '>').replace('&lt;', '<').replace('&gt;', '>').replace('&#x27;', "'")
    s = re.sub(r'\s+', ' ', s)
    return s

for kw in sys.argv[1:]:
    ms = [m.start() for m in re.finditer(kw, h)]
    print('#####', kw, len(ms))
    for m in ms[:6]:
        print('---', clean(h[max(0, m - 260):m + 420])[:640])
