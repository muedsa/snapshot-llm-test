import json
import re

p = r'tmp\20261004-182918\A23\log_a23.py'
s = open(p, encoding='utf-8').read()

rows = [json.loads(x) for x in
        open(r'tmp\20261004-182918\A23\requests.jsonl', encoding='utf-8') if x.strip()]
by_id = {r['request_id']: r['started_at'] for r in rows}

# iteration -> the real request that produced / followed it
M = {
    'A23-v01': 'A23-req-008',   # p01-type-png
    'A23-v02': 'A23-req-011',   # gif / apng / svg rejection
    'A23-v03': 'A23-req-014',   # animation attrs ignored
    'A23-v04': 'A23-req-015',   # cmyk attrs ignored
    'A23-v05': 'A23-req-016',   # vector attrs ignored
    'A23-v06': 'A23-req-017',   # q1 rotation
    'A23-v07': 'A23-req-018',   # q2 transparent
    'A23-v08': 'A23-req-020',   # q4 cjk
    'A23-v09': 'A23-req-021',   # frame set v1
    'A23-v10': 'A23-req-027',   # frame-06 after geometry fix
    'A23-v11': 'A23-req-028',   # frame set v2
    'A23-v12': 'A23-req-037',   # cover PARSE_ERROR
    'A23-v13': 'A23-req-038',   # cover fixed
    'A23-v14': 'A23-req-039',   # cover relaid out
    'A23-v15': 'A23-req-040',   # contact sheet
    'A23-v16': 'A23-req-047',   # final re-render batch
    'A23-v17': 'A23-req-057',   # post-draft-fix re-render
    'A23-v18': None,            # verification only, no new request
}
missing = [k for k, v in M.items() if v and v not in by_id]
if missing:
    raise SystemExit('unknown request ids: %s' % missing)

n = 0
for ver, rid in M.items():
    if rid is None:
        stamp = rows[-1]['ended_at']
    else:
        stamp = by_id[rid]
    # find the ts(...) call inside this iteration's tuple
    pat = re.compile(r'(\("' + ver + r'",.*?)\bts\(\d+, \d+, \d+\)', re.S)
    s2, k = pat.subn(lambda m: m.group(1) + '"%s"' % stamp, s, count=1)
    if k != 1:
        raise SystemExit('could not patch %s (k=%d)' % (ver, k))
    s = s2
    n += 1
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched %d iteration timestamps to real request times' % n)
for ver, rid in M.items():
    print('  %-9s %s' % (ver, rid or '(verification only)'))
