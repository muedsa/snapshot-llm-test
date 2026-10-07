import html
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8', errors='replace').read()
s = re.sub(r'(?is)<script.*?</script>', ' ', s)
s = re.sub(r'(?is)<style.*?</style>', ' ', s)
s = re.sub(r'(?is)<svg.*?</svg>', ' ', s)
s = re.sub(r'(?i)</(p|div|li|h1|h2|h3|h4|tr|pre|section)>', '\n', s)
s = re.sub(r'(?i)<br\s*/?>', '\n', s)
s = re.sub(r'<[^>]+>', ' ', s)
s = html.unescape(s)
s = ''.join(ch if (ch >= ' ' or ch in '\n\t') else ' ' for ch in s)
s = re.sub(r'[ \t]+', ' ', s)
s = re.sub(r'\n\s*\n+', '\n', s)
with open(dst, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write(s.strip())
print('wrote', dst, len(s))