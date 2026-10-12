import json, hashlib, datetime, math, xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
root=Path.cwd();run='20261002-204314-6f31';base=root/'tmp'/run/'B05';private=base/'audit-independent-v001'
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
selection=load(base/'root'/'selection-v004.json');plan=load(base/'product-plan-v001.json');journey=load(root/'outputs'/run/'B05'/'journey.json')
views=load(private/'actual-views-v001.json')['actual_views'];issues=[];checks=[];seen=set();trees={};texts={};cases=[]
def check(name,ok,detail=None):
 checks.append({'check':name,'passed':bool(ok),'detail':detail})
 if not ok:issues.append({'check':name,'detail':detail})
for c in selection['cases']:
 r=load(c['render_meta']);m=load(c['metadata']);f=Path(r['image_path']);d=Path(r['dsl_path']);data=d.read_text(encoding='utf-8-sig')
 check(c['id']+':service200PNG',r['ok'] and r['http_status']==200 and r['content_type']=='image/png')
 check(c['id']+':raw_response_SHA',sha(f)==r['response_sha256'] and sha(r['response_file'])==sha(f))
 check(c['id']+':submitted_body_version_SHA',sha(d)==r['body_sha256'] and sha(r['input_file'])==sha(d))
 with Image.open(f) as im:im.load();dim=list(im.size)
 check(c['id']+':PNG_dimensions',dim==[r['expected_width'],r['expected_height']],dim)
 md=m['dimensions'];md=[md['width'],md['height']] if isinstance(md,dict) else md
 check(c['id']+':metadata_dimensions',dim==md,md)
 check(c['id']+':unique_main_image',sha(f) not in seen);seen.add(sha(f))
 tree=ET.fromstring(data);trees[c['id']]=tree;text='\n'.join(''.join(x.itertext()) for x in tree.iter('Raw'));texts[c['id']]=text
 check(c['id']+':DSL_complete_png_root',tree.tag=='Snapshot' and tree.get('type')=='png')
 check(c['id']+':DSL_no_Image_or_external_asset',not list(tree.iter('Image')) and not m.get('supporting_assets'))
 check(c['id']+':scenario_metadata',all(m.get(k) for k in ['title','audience','use_context','user_goal','content_basis','completion_criteria']))
 boxes=[]
 for el in tree.iter('Positioned'):
  if not list(el.iter('Text')):continue
  a=el.attrib
  if all(k in a for k in ['left','top','width','height']):
   x,y,w,h=(float(a[k]) for k in ['left','top','width','height']);boxes.append({'left':x,'top':y,'width':w,'height':h})
 check(c['id']+':text_boxes_inside_canvas',all(x['left']>=0 and x['top']>=0 and x['left']+x['width']<=dim[0]+.01 and x['top']+x['height']<=dim[1]+.01 for x in boxes),len(boxes))
 check(c['id']+':demo_notice_on_art','静态概念原型' in text and '演示' in text)
 check(c['id']+':time_matches_journey',c['at'] in text and next(x['at'] for x in journey['screens'] if x['id']==c['id'])==c['at'])
 check(c['id']+':actual_independent_original_view',any(v['case_id']==c['id'] and v['image_path']==r['image_path'] and v['tool']=='view_image' and v['viewed_at'] and v['observation'] for v in views))
 if c['id']!='case-07':
  p=private/(c['id']+'-360.png')
  with Image.open(p) as im:im.load();pdim=list(im.size)
  check(c['id']+':actual_logical_phone_preview',pdim==[360,720] and any(v['image_path']==str(p) for v in views))
  buttons=[p for p in tree.iter('Positioned') if p.get('width')=='640' and p.get('height')=='88' and any(x.tag=='Container' and x.get('borderRadius')=='22' for x in p)]
  check(c['id']+':primary_action_visual_height44logical',len(buttons)>=1,{'raster_height':88,'logical_height':44,'buttons':len(buttons),'actual_hit_targets_implemented':False})
 cases.append({'case_id':c['id'],'request_id':r['id'],'dimensions':dim,'response_sha256':sha(f),'dsl_sha256':sha(d),'metadata':c['metadata'],'original_view':next(v for v in views if v['case_id']==c['id'] and v['scope']=='original service response')})
check('10_distinct_states',len(selection['cases'])==10 and len({x['state'] for x in selection['cases']})==10)
check('plan_journey_scenario_agrees',journey['shared_state']==plan['scenario'])
check('ordered_journey_links',all(x['previous']==(journey['screens'][i-1]['id'] if i else None) and x['next']==(journey['screens'][i+1]['id'] if i<9 else None) for i,x in enumerate(journey['screens'])))
required={
 'case-01':['北院','1层','预约不扣费','到场核验'],
 'case-02':['C1','C2','C3','C4','D1','D2','18:40','18:30–19:10','标准40分钟'],
 'case-03':['40 分钟','¥4','18:30开始','19:10结束','60 分钟','¥6','另选60分钟空档','现场开始时付款'],
 'case-04':['C2','18:30–19:10','4261','WL-1008-026','免费取消截止 18:25','目前未扣费','支付¥4'],
 'case-05':['C2故障','自动取消','原预约未扣费','WL-1008-026','旧取用码4261已失效','C1','18:40–19:20','¥4'],
 'case-06':['C1','5372','WL-1008-027','18:40–19:20','当前未扣费','WL-1008-026已取消','旧码4261已失效'],
 'case-07':['5372已核验','C1','待开始','18:40–19:20','40分钟','¥4','WL-1008-027','当前未扣费','返回，不扣费','确认付款 ¥4 并开始'],
 'case-08':['18:58','开始18:40','预计结束19:20','22','已运行18 / 40分钟','已付款 ¥4','WL-1008-027','计划估计'],
 'case-09':['结束于19:20','已支付¥4','自行晾晒','不加费','D1干衣','¥3','19:25–19:55','30分钟','现场确认开始时才支付干衣费'],
 'case-10':['19:55','WL-1008-027','C1标准洗衣','¥4','18:40–19:20','已付款18:40','D1干衣','¥3','19:25–19:55','已付款19:25','¥7','原C2故障预约已取消，未产生费用','确认已取走衣物','反馈本次使用问题']
}
for cid,terms in required.items():check(cid+':visible_transaction_content',all(term.replace(' ','') in texts[cid].replace(' ','') for term in terms),{'missing':[term for term in terms if term.replace(' ','') not in texts[cid].replace(' ','')]})
def minutes(v):a,b=map(int,v.split(':'));return a*60+b
a=journey['arithmetic_checks'];check('time_and_fee_arithmetic',a=={'wash_minutes':40,'elapsed_at_1858_minutes':18,'remaining_minutes':22,'progress_fraction':.45,'dry_minutes':30,'handoff_gap_minutes':5,'paid_cny':7} and minutes('19:20')-minutes('18:40')==40 and minutes('18:58')-minutes('18:40')==18 and minutes('19:20')-minutes('18:58')==22 and minutes('19:55')-minutes('19:25')==30 and minutes('19:25')-minutes('19:20')==5 and 4+3==7)
check('explicit_unpictured_payment_events',len(journey['unpictured_events'])==2 and all('付款' in x['event'] or '支付' in x['event'] for x in journey['unpictured_events']))
check('branch_payment_not_silently_claimed',len(journey['alternatives'])==4 and 'case-09只提供未扣费选择' in journey['unpictured_events'][1]['result'])
# Inspect actual 22px DSL arc centers, excluding logo and duplicated endpoints.
centers=[]
for p in trees['case-08'].iter('Positioned'):
 if p.get('width')=='22' and p.get('height')=='22' and any(x.tag=='Container' and x.get('shape')=='CIRCLE' and x.get('color')=='#176B68' for x in p):
  centers.append((float(p.get('left'))+11,float(p.get('top'))+11))
centers=list(dict.fromkeys(centers));angles=[(math.degrees(math.atan2(y-640,x-360))+90)%360 for x,y in centers];radii=[math.hypot(x-360,y-640) for x,y in centers]
check('case-08:actual_DSL_ring_45percent_sweep',len(centers)>2 and abs(min(angles))<1e-5 and abs(max(angles)-162)<1e-4 and all(abs(r-190)<1e-4 for r in radii),{'unique_centers':len(centers),'angle_min':min(angles),'angle_max':max(angles),'sweep_fraction':max(angles)/360,'radius_min':min(radii),'radius_max':max(radii)})
sources=load(base/'research'/'source-manifest-v001.json')
for s in sources:check('source:'+s['id'],s['ok'] and s['http_status']==200 and Path(s['raw_response']).exists() and sha(s['raw_response'])==s['sha256'] and Path(s['readable_file']).exists())
result={'schema_version':1,'task_id':'B05','run_id':run,'reviewer':'/root/suite_integrity_audit','selection':str(base/'root'/'selection-v004.json'),'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'issues':issues,'passed':not issues,'cases':cases,'full_research_texts_actually_read':[s['readable_file'] for s in sources],'candidate_scope':'All selected original response PNGs and version DSLs, metadata, plan, brief and journey. Final output copies are published by root after this candidate audit; no claim to have verified copies yet.'}
with (private/'candidate-structural-v002.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'passed':not issues,'checks':len(checks),'issues':issues,'cases':len(cases),'arc':checks[-3],'report':str(private/'candidate-structural-v002.json')},ensure_ascii=False,indent=2))
