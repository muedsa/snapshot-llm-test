import json
g = json.load(open(r'tmp\20261004-182918\A17\probe\glyphs.json', encoding='utf-8'))['glyphs']
keys = [" ", '"', "'", ",", "-", ".", "_", "`", "~", "A", "0", "M", "|", "/", ":", "="]
for c in keys:
    print(repr(c), g.get(c))
lat = [v.get('advance_em') for v in g.values() if v.get('kind') == 'latin' and v.get('advance_em')]
print('latin n', len(lat), 'max', max(lat))