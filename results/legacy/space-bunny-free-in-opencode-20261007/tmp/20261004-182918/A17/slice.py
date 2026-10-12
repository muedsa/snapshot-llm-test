import re
t = open(r'outputs\20261004-182918\A17\handbook-01.snapshot', encoding='utf-8').read()
for kw in ['印刷', '省略', 'example-01.snapshot', 'CDATA[⋯', '475569']:
    print(kw, t.count(kw))
i = t.find('印刷')
out = t[max(0, i - 800):i + 600]
open(r'tmp\20261004-182918\A17\probe\slice.txt', 'w', encoding='utf-8').write(out)
print('slice written', i)