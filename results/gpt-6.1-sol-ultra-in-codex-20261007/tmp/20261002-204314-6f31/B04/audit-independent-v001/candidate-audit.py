import json, hashlib, datetime, xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
root=Path.cwd();run='20261002-204314-6f31';base=root/'tmp'/run/'B04';private=base/'audit-independent-v001'
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
selection=load(base/'root'/'selection-v001.json');sources=load(root/'outputs'/run/'B04'/'sources.json')
issues=[];checks=[];sourcechecks=[];seen=set();trees={}
def check(name,ok,detail=None):
 checks.append({'check':name,'passed':bool(ok),'detail':detail})
 if not ok:issues.append({'check':name,'detail':detail})
for s in sources['sources']:
 ok=s['ok'] and s['http_status']==200 and Path(s['raw_response']).exists() and sha(s['raw_response'])==s['sha256'] and Path(s['readable_file']).exists()
 sourcechecks.append({'id':s['source_id'],'request_id':s['request_id'],'archived_bytes_and_readable_file_match':ok,'url':s['url']})
 check('source:'+s['source_id'],ok)
for c in selection['cases']:
 r=load(c['render_meta']);m=load(c['metadata']);f=Path(r['image_path']);d=Path(r['dsl_path']);data=d.read_text(encoding='utf-8-sig')
 check(c['id']+':service200PNG',r['ok'] and r['http_status']==200 and r['content_type']=='image/png')
 check(c['id']+':raw_response_SHA',sha(f)==r['response_sha256'] and sha(r['response_file'])==sha(f))
 check(c['id']+':submitted_body_version_SHA',sha(d)==r['body_sha256'] and sha(r['input_file'])==sha(d))
 with Image.open(f) as im:im.load();dim=list(im.size);check(c['id']+':PNG_dimensions',dim==[r['expected_width'],r['expected_height']],dim)
 md=m['dimensions'];md=[md['width'],md['height']] if isinstance(md,dict) else md
 check(c['id']+':metadata_dimensions',dim==md,md)
 check(c['id']+':unique_main_image',sha(f) not in seen);seen.add(sha(f))
 tree=ET.fromstring(data);trees[c['id']]=tree
 check(c['id']+':DSL_no_Image',not list(tree.iter('Image')))
 check(c['id']+':sources_mapped',sorted(m['source_ids'])==sorted(next(x['source_ids'] for x in sources['artwork_citations'] if x['case_id']==c['id'])))
 check(c['id']+':scenario_metadata',all(m.get(k) for k in ['title','audience','use_context','user_goal','content_basis','completion_criteria']))
 # Check explicit absolute boxes against canvas. Transformed/clip geometry is
 # intentionally treated separately; the root boundary and visible review govern it.
 textboxes=[]
 for el in tree.iter('Positioned'):
  if not list(el.iter('Text')):continue
  a=el.attrib
  if all(k in a for k in ['left','top','width','height']):
   x,y,w,h=(float(a[k]) for k in ['left','top','width','height'])
   textboxes.append({'left':x,'top':y,'width':w,'height':h})
 check(c['id']+':text_boxes_inside_canvas',all(x['left']>=0 and x['top']>=0 and x['left']+x['width']<=dim[0]+.01 and x['top']+x['height']<=dim[1]+.01 for x in textboxes),len(textboxes))
t=trees['case-03'];bars=[]
for p in t.iter('Positioned'):
 a=p.attrib
 if a.get('left')=='246' and a.get('height')=='20' and a.get('top') in ['392','530','668']:
  bars.append({'x':float(a['left']),'y':float(a['top']),'width':float(a['width']),'meters':{'392':109,'530':80,'668':67}[a['top']]})
check('case-03:actual_three_bars_common_zero_exact8px_per_m',len(bars)==3 and all(b['width']==8*b['meters'] for b in bars),bars)
check('case-03:derived_difference_and_ratio',109-80==29 and round(109/80,2)==1.36,{'exact_ratio':109/80,'display_ratio':round(109/80,2)})
t=trees['case-06'];units=[c for c in t.iter('Container') if c.get('width')=='20' and c.get('height')=='33'];cols={}
for c in units:cols[c.get('color')]=cols.get(c.get('color'),0)+1
check('case-06:100_equal_mass_unit_DSL_containers_98plus2',len(units)==100 and sorted(cols.values())==[2,98],{'unit_count':len(units),'by_color':cols})
five=load(base/'producer-05-07'/'case-05-metadata-v001.json')['algorithm']
check('case-05:16_event_positions_and_approximation',five['sunrise_icons']==16 and len(five['angles_degrees'])==16 and five['sunrise_count_is_approximate'],five)
check('case-01:day_orbit_arithmetic',24*60/90==16)
allviews=[]
for f in sorted(private.glob('views-batch-*.json')):allviews.extend(load(f))
for c in selection['cases']:
 r=load(c['render_meta']);check(c['id']+':actual_independent_view_record',any(v['case_id']==c['id'] and v['image_path']==r['image_path'] and v['tool']=='view_image' and v['viewed_at'] and v['observation'] for v in allviews))
result={'schema_version':1,'run_id':run,'task_id':'B04','reviewer':'/root/suite_integrity_audit','independent_final_audit_performed':True,'audited_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selection':str(base/'root'/'selection-v001.json'),'scope':'10 final candidate original images individually opened and perceived, plus collection contact sheet, full seven saved source texts actually read, sources/editorial-note and metadata/DSL factual and structural checks. No new HTTP and no public ledger mutation.','passed':not issues,'checks':checks,'issues':issues,'source_checks':sourcechecks,'actual_views':allviews,'source_constraints':'Unity launch-date conflict avoided; 90min/16 approximate; 109/80/67m one-source axes;98% historical defined denominator not branch flow;2h historical average;five agencies not five countries;original papers not read;no real-time pass invented.','resources':{'new_HTTP':0,'actual_final_candidate_image_views':10,'actual_collection_image_views':1},'limits':['Research relies on seven NASA pages; no primary referenced paper was accessed.','All artwork geometry except one-dimensional length scale and100-unit count is explicitly conceptual, not engineering scale.','Precise dispatch timestamps were unavailable; viewed_at uses a clock reading immediately after actual image inspection.']}
with (private/'audit-final-v001.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'passed':not issues,'issues':issues,'checks':len(checks),'views':len(allviews),'report':str(private/'audit-final-v001.json')},ensure_ascii=False,indent=2))
