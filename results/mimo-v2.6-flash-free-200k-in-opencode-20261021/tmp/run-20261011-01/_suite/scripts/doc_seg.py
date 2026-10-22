import re, pathlib, sys
h = pathlib.Path('tmp/run-20261011-01/_suite/docs/parser-tags.html').read_text(encoding='utf-8', errors='replace')

def clean(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    for a, b in [('&#x22;', '"'), ('&quot;', '"'), ('&#x3C;', '<'), ('&#x3E;', '>'),
                 ('&lt;', '<'), ('&gt;', '>'), ('&#x27;', "'"), ('&amp;', '&')]:
        s = s.replace(a, b)
    s = re.sub(r'\s+', ' ', s)
    return s

start = int(sys.argv[1])
end = int(sys.argv[2])
print(clean(h[start:end]))
