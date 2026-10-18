import json, os, zstandard
from pathlib import Path
from collections import Counter
base=Path(os.environ['USERPROFILE'])/'.dsh'/'sessions'/'--D-mine-test-ds--'
def load(sid):
 with open(base/sid/'session.v4.jsonl.zstd','rb') as f: text=zstandard.ZstdDecompressor().stream_reader(f).read().decode('utf-8')
 return [json.loads(x) for x in text.splitlines() if x.strip()]
root=load('session-4fc04984-a367-4c82-a2e8-5ad13719bf66')
fork=load('session-8b17c06a-2535-42d1-8f74-8e1faa9a58c0')
def rows(evs):
 out=[]
 for e in evs:
  if e.get('type')!='assistant/message': continue
  d=e.get('data') or {}; u=d.get('usage')
  if not u: continue
  m=d.get('message') or {}; mid=m.get('id') or e.get('id') or f"seq-{e.get('seq')}"
  out.append((str(mid),e.get('seq'),e.get('time'),u,d.get('source')))
 return out
r=rows(root); f=rows(fork)
print('root rows',len(r),'unique',len({x[0] for x in r}))
print('fork rows',len(f),'unique',len({x[0] for x in f}))
print('root first',r[0][:4], 'source',r[0][4])
print('fork first',f[0][:4], 'source',f[0][4])
rid={x[0] for x in r}; fid={x[0] for x in f}
print('fork unique not root',len(fid-rid),'root not fork',len(rid-fid),'common',len(rid&fid))
print('fork new sample',[(x[0],x[1]) for x in f if x[0] not in rid][:5])
print('root source variants',Counter(json.dumps(x[4],ensure_ascii=False)[:200] if x[4] else None for x in r).most_common(3))
print('root assistant event no source sample', next((e for e in root if e.get('type')=='assistant/message' and (e.get('data') or {}).get('usage') and not (e.get('data') or {}).get('source')),None))
# sum incremental
def tot(x):
 u=x[3]; return sum(int(u.get(k) or 0) for k in ('inputTokens','outputTokens','cacheReadTokens','cacheWriteTokens'))
new=[x for x in f if x[0] not in rid]
print('new sums',sum(tot(x) for x in new),[(x[0],tot(x)) for x in new[:20]])
