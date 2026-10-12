import json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
root=Path(r'D:\workspaces\gpt-6.1-sol-ultra'); run='20261002-204314-6f31'
tmp=root/'tmp'/run/'B06'; out=root/'outputs'/run/'B06'; private=tmp/'audit-root-independent-v001'
sel=json.loads((tmp/'root'/'selection-v002.json').read_text(encoding='utf-8'))['cases']
state=json.loads((root/'outputs'/run/'_suite'/'suite-state.json').read_text(encoding='utf-8'))
reqs={r['id']:r for r in map(json.loads,(tmp/'requests.jsonl').read_text(encoding='utf-8').splitlines())}
vers={r['id']:r for r in map(json.loads,(tmp/'versions.jsonl').read_text(encoding='utf-8').splitlines())}
views={r['id']:r for r in map(json.loads,(tmp/'views.jsonl').read_text(encoding='utf-8').splitlines())}
evidence=json.loads((out/'problem-evidence.json').read_text(encoding='utf-8')); ev={c['id']:c for c in evidence['cases']}
checks=[]; trees={}; raws={}; metas={}; artifacts=[]
def ck(s,v):checks.append({'check':s,'passed':bool(v)})
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def eq(a,b):return abs(a-b)<1e-5
ck('Ten distinct final selected cases',len(sel)==10 and len(set(s['id'] for s in sel))==10)
prior_png={a['image_sha256'] for t in state['tasks'] if t['id'] in ['B01','B02','B03','B04','B05'] for a in t['artifacts']}
prior_dsl={a['dsl_sha256'] for t in state['tasks'] if t['id'] in ['B01','B02','B03','B04','B05'] for a in t['artifacts']}
for s in sel:
    case=s['id']; r=json.loads(Path(s['render_meta']).read_text(encoding='utf-8')); rq=reqs[r['id']]; v=vers[r['version_id']]
    p=Path(r['image_path']); d=Path(r['dsl_path']); m=json.loads(Path(s['metadata']).read_text(encoding='utf-8')); metas[case]=m
    with Image.open(p) as im: im.load(); dims=im.size; fmt=im.format
    ck(case+' complete service PNG decode/expected dimensions',fmt=='PNG' and list(dims)==m['dimensions'] and dims==(r['expected_width'],r['expected_height']))
    ck(case+' successful real Snapshot response',rq['type']=='render' and rq['http_status']==200 and rq['content_type']=='image/png' and rq['ok'])
    ck(case+' render metadata matches logged request',rq['response_sha256']==r['response_sha256'] and rq['body_sha256']==r['body_sha256'] and rq['case_id']==case)
    ck(case+' original PNG byte sha chain',sha(p)==r['response_sha256']==sha(rq['response_file']))
    ck(case+' complete DSL input and archived version sha chain',sha(d)==v['sha256']==r['body_sha256']==sha(rq['input_file'])==sha(v['path']))
    vw=views[s['view_id']]; ck(case+' existing root actual final view matches selected bytes',vw['sha256']==r['response_sha256'] and sha(vw['image_path'])==r['response_sha256'])
    tree=ET.parse(d); trees[case]=tree; text='\n'.join(n.text or '' for n in tree.iter('Raw')); raws[case]=text
    ck(case+' self-contained XML Snapshot and no raster substitution',tree.getroot().tag=='Snapshot' and not list(tree.iter('Image')) and not list(tree.iter('Include')))
    ck(case+' scene/audience/goal/criteria/source boundary supplied',all(m.get(k) for k in ['audience','use_context','user_goal','completion_criteria','content_basis']))
    ec=ev[case]; raw_source=(out/ec['source']['raw_material_path']).resolve(); ck(case+' raw source path resolves and source data matches evidence',raw_source.is_file() and json.loads(raw_source.read_text(encoding='utf-8'))['raw_data']==ec['source']['data'])
    ck(case+' no field/user experiment claims',ec['source']['field_observation'] is False and ec['source']['experiment'] is False and ec['validated_user_effects'] is None)
    ck(case+' evidence maps selected existing true review',ec['actual_view']==s['view_id'] and ec['final_image']==case+'/final.png')
    ck(case+' new PNG and DSL distinct from B01-B05 delivered work',r['response_sha256'] not in prior_png and r['body_sha256'] not in prior_dsl)
    artifacts.append({'case_id':case,'request_id':r['id'],'version_id':r['version_id'],'image_path':str(p),'dsl_path':str(d),'image_sha256':r['response_sha256'],'dsl_sha256':r['body_sha256'],'dimensions':list(dims)})
ck('Ten selected images and complete DSL all byte-distinct',len(set(a['image_sha256'] for a in artifacts))==10 and len(set(a['dsl_sha256'] for a in artifacts))==10)
ck('B06 extra required files present',all((out/n).is_file() and (out/n).stat().st_size>0 for n in ['problem-evidence.json','design-review.md']))
def rects(case):
    result=[]
    for p in trees[case].iter('Positioned'):
        c=p.find('Container')
        if c is not None: result.append({k:float(p.attrib[k]) for k in ['left','top','width','height']}|{'color':c.attrib.get('color')})
    return result
def match(r,x,y,w,h):return all(eq(r[k],n) for k,n in zip(['left','top','width','height'],[x,y,w,h]))
rs=rects('case-02'); ck('02 DSL proportional equal common and personal amount bars',all(any(match(r,x,803,28*6.4,29) for r in rs) for x in [86,462,838,1214]) and all(any(match(r,x,803,w,29) for r in rs) for x,w in [(265.2,18*6.4),(1017.2,12*6.4),(1393.2,6*6.4)]))
rs=rects('case-03'); expected=[(108,140),(248,140),(388,210),(598,210),(808,140),(948,280),(1228,140)]; ck('03 DSL seven segments exact14 px/minute and contiguous90-minute span',all(any(match(r,x,352,w,75) for r in rs) for x,w in expected) and 1368-108==90*14)
rs=rects('case-07'); ck('07 DSL complete regular4x6 door geometry',all(any(match(r,126+144*c,403+121*rw,126,101) for r in rs) for rw in range(4) for c in range(6)))
ck('07 DSL target door17 at row3/column5',any(match(r,702,645,126,101) and r['color']=='#FFD965' for r in rs))
rs=rects('case-08'); expected=[(505,371,375),(880,371,125),(1005,371,500),(505,546,750),(1255,546,125),(1380,546,125),(505,721,250),(755,721,750)]; ck('08 DSL exact25 px/minute and no interval overlaps',all(any(match(r,x,y,w,106) for r in rs) for x,y,w in expected))
ck('08 final evidence only returnedT01/T02 need5minute check','T01/T02' in ev['case-08']['source']['data']['rule'] and 'T03已在库' in ev['case-08']['source']['data']['rule'] and '无待归还检查时段' in raws['case-08'])
rs=rects('case-10'); vals=[10,18,6,12,8,10]; x=70; result=True
for n in vals: w=n*21.25; result=result and any(match(r,x,410,w,154) for r in rs); x+=w
ck('10 DSL exact21.25 px/GB complete64GB strip',result and eq(x,1430))
ck('10 capacity arithmetic before/after',sum(vals)==64 and sum(vals[:-1])==54 and 54-4==50 and 10+4==14)
ck('09 2026-10-11 really Sunday',datetime(2026,10,11).weekday()==6)
ck('05 label dates treated as demonstration not safety guarantee','不判断食品安全' in raws['case-05'] and '实际包装优先' in raws['case-05'])
ck('06 renewal conditional not completed','尚未申请' in raws['case-06'] and '成功后' in raws['case-06'] and '10月28日' in raws['case-06'])
ck('09 expected restoration requires notice','预计' in raws['case-09'] and '恢复公告' in raws['case-09'] and '延迟另行通知' in raws['case-09'])
ck('10 manual confirmation and no real device scan','手动' in raws['case-10'] and '不是实机扫描' in raws['case-10'])
prep=json.loads((private/'preparation-v001.json').read_text(encoding='utf-8')); checks.extend(prep['numeric_prechecks'])
report={'task_id':'B06','reviewer':'/root/b06_final_audit_resume','checked_at':datetime.now(timezone.utc).isoformat(),'scope':'Final selected service response artifacts before publication, not yet public final file integrity. Pure file/DSL/data checks; actual visual findings recorded separately.','passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,'artifacts':artifacts,'pending_after_publication':['Public final PNG/DSL byte chain, all root/case reports and gallery links']}
(private/'checks-final-v001.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['passed','check_count','scope']},ensure_ascii=False))
for case,target in [('case-02',800),('case-04',800),('case-08',800),('case-10',750),('case-05',600),('case-06',600)]:
    a=next(a for a in artifacts if a['case_id']==case)
    with Image.open(a['image_path']) as im:
        dims=(target,round(im.height*target/im.width)); im.resize(dims,Image.Resampling.LANCZOS).save(private/f'{case}-nearread-preview-v001.png')
print('Saved six half-scale near-read previews only; service final image bytes remain unmodified.')
