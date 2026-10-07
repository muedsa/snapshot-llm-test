import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
root=Path(r'D:\workspaces\gpt-6.1-sol-ultra'); run='20261002-204314-6f31'
private=root/'tmp'/run/'B06'/'audit-root-independent-v001'
plan_path=root/'tmp'/run/'B06'/'problem-plan-v001.json'
plan=json.loads(plan_path.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
cases={c['id']:c for c in plan['cases']}; checks=[]
def ck(s,v): checks.append({'check':s,'passed':bool(v)})
d=cases['case-01']['data']; ck('01 six boxes in three rooms',len(d['boxes'])==3 and sum(map(len,d['boxes'].values()))==6)
d=cases['case-02']['data']; ck('02 shared net and split',120-20+12==d['shared_net_cny']==112 and 112/4==d['shared_per_person']==28); ck('02 per person and overall closed', [28+n for n in d['personal_cny']]==d['final_cny'] and sum(d['final_cny'])==148 and sum(d['personal_cny'])==36)
d=cases['case-03']['data']; ck('03 walk/stay and whole 90 minutes',sum(d['legs_minutes'])==45 and sum(d['stay_minutes'])==45 and sum(d['legs_minutes'])+sum(d['stay_minutes'])==90); ck('03 date really Saturday',datetime.fromisoformat(d['date']).weekday()==5)
calc=json.loads((root/'tmp'/run/'B06'/'producer-02-04'/'case-04-calculation-v001.json').read_text(encoding='utf-8'))
ck('04 complete independent cumulative calculation',all(r['A']==100+min(r['month'],6)*39+max(r['month']-6,0)*79 and r['B']==r['month']*69 and r['A_minus_B']==r['A']-r['B'] for r in calc['month_end_cumulative_cny']))
ck('04 24 month totals and equal month14',calc['totals']=={'A':1756,'B':1656,'difference':100} and calc['month_end_cumulative_cny'][14]['A_minus_B']==0)
d=cases['case-05']['data']; ck('05 label dates in order', [i['label_date'] for i in d['items']]==['10月11日','10月12日','10月13日'])
d=cases['case-06']['data']; ck('06 three distinct conditional actions',[i['action'] for i in d['items']]==['归还','申请续借','取书'] and d['items'][1]['current_due']=='10月14日' and d['items'][1]['conditional_new_due']=='成功后10月28日')
d=cases['case-07']['data']; ck('07 24 doors and correct17 row3col5',d['rows']*d['cols']==24 and (d['target_row']-1)*d['cols']+d['target_col']==d['target_door']==17)
d=cases['case-09']['data']; ck('09 next day and two hour window',datetime.fromisoformat(d['event_date'])-datetime.fromisoformat(d['published'])==__import__('datetime').timedelta(days=1) and d['window']=='10:00–12:00' and d['duration_hours']==2)
d=cases['case-10']['data']; ck('10 capacity conservation before/after',sum(n for _,n in d['segments'])==64 and sum(n for _,n in d['segments'][:-1])==54 and 54-4==50 and 10+4==14)
source_paths=[root/'AGENTS.md',root/'TASKS.md',root/'catalog.json',root/'run-config.json']+[root/'tasks'/'B06-everyday-information-reinvented'/f for f in ['TASK.md','AGENTS.md','task.json','run-config.json','inputs/README.md']]+[plan_path]
report={'task_id':'B06','reviewer':'/root/b06_final_audit_resume','prepared_at':datetime.now(timezone.utc).isoformat(),'stage':'Preparation only; no real B06 image viewed yet. Final visual acceptance remains pending.','actual_read_sources':[{'path':str(p),'sha256':sha(p)} for p in source_paths],'numeric_prechecks':checks,'numeric_prechecks_passed':all(c['passed'] for c in checks),'case08_required_semantic_clarification':'T01/T02 returned tools receive five minute check before next handoff; T03 is already in store and may be handed over after administrator registration. Do not imply T03 is missing five minute return check. Root is handling.','image_views':[],'final_review_pending':['Actual full final B06 ten service PNGs','Contact sheet and intended reading-size previews','Final selection byte identity and full DSL','Required problem-evidence.json and design-review.md truthful boundaries','Root/case reports, all math/text/geometries and collection independence']}
(private/'preparation-v001.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'numeric_prechecks':len(checks),'passed':report['numeric_prechecks_passed'],'stage':report['stage']},ensure_ascii=False))
