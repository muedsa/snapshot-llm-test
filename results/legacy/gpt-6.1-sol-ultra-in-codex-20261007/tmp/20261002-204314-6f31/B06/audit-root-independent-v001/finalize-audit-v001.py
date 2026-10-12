import json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
root=Path(r'D:\workspaces\gpt-6.1-sol-ultra'); run='20261002-204314-6f31'; tmp=root/'tmp'/run/'B06'; p=tmp/'audit-root-independent-v001'
checks=json.loads((p/'checks-final-v001.json').read_text(encoding='utf-8'))
ledger=[json.loads(s) for s in (p/'private-views.jsonl').read_text(encoding='utf-8').splitlines()]
for v in ledger:
    if 'sha256' not in v: v['sha256']=hashlib.sha256(Path(v['image_path']).read_bytes()).hexdigest()
artifact=next(a for a in checks['artifacts'] if a['case_id']=='case-04')
tree=ET.parse(artifact['dsl_path']); lines=[]
for n in tree.iter('Positioned'):
    tr=n.find('Transform'); con=tr.find('Container') if tr is not None else None
    if con is not None and float(n.attrib.get('height','0'))==4:
        lines.append({'x':float(n.attrib['left']),'y':float(n.attrib['top']),'length':float(n.attrib['width']),'color':con.attrib['color'],'matrix':tr.attrib['matrix']})
def eq(a,b):return abs(a-b)<1e-4
def line_exists(x,y,length):return any(eq(v['x'],x) and eq(v['y'],y) and eq(v['length'],length) for v in lines)
geometry=[]
for key in ['A','B']:
    points=[100+min(m,6)*39+max(m-6,0)*79 if key=='A' else m*69 for m in range(25)]
    ok=all(line_exists(150+m*36,810-points[m]*.26,36) and line_exists(150+(m+1)*36,810-points[m]*.26,(points[m+1]-points[m])*.26) for m in range(24))
    geometry.append({'check':f'04 DSL all24 horizontal and24 vertical {key} steps reproduce exact cumulative values at36px/month and0.26px/yuan','passed':ok})
checks['checks'].extend(geometry)
actual_final={v['case_id']:v for v in ledger if v.get('stage')=='Independent final selection review'}
checks['checks'].append({'check':'Ten independently opened full final selected images and final collection contact review','passed':len(actual_final)==10 and all(v['passed'] for v in actual_final.values()) and any(v['stage']=='Independent final collection contact review' and v['passed'] for v in ledger)})
checks['checks'].append({'check':'Six actually opened half-scale nearread previews all passed','passed':sum(v['stage']=='Independent half-scale near-read preview' and v['passed'] for v in ledger)==6})
case_judgments={k:v['observation'] for k,v in actual_final.items()}
contact=next(v for v in ledger if v['stage']=='Independent final collection contact review')
report={'task_id':'B06','run_id':run,'reviewer':'/root/b06_final_audit_resume','checked_at':datetime.now(timezone.utc).isoformat(),'passed':all(c['passed'] for c in checks['checks']),'status':'passed_selected_artifacts_pending_publication_integrity','scope':'Ten final selected original service PNGs/DSLs, actual full-image visual review plus collection and nearread, all authored problem evidence and design review. Public final-file/report/gallery integrity is a follow-up after publisher writes those files.','selection_path':str(tmp/'root'/'selection-v002.json'),'check_count':len(checks['checks']),'checks':checks['checks'],'artifacts':checks['artifacts'],'case_judgments':case_judgments,'collection_judgment':contact['observation'],'actual_views':ledger,'actual_view_count':len(ledger),'actual_views_by_stage':{'pre_final_full_baselines':4,'final_full_selected_images':10,'final_collection_contact':1,'half_scale_nearread_previews':6},'known_resolved_issues':[{'case_id':'case-04','issue':'x-axis month-end title overlapped rightmost24 tick','old_actual_view':ledger[0]['id'],'new_actual_view':actual_final['case-04']['id'],'resolution':'Actual new full PNG and800px preview show units/24 tick separated. Exact geometry unchanged.'},{'case_id':'case-08','issue':'General plan could imply5minute check needed for already storedT03','resolution':'Finalplanv002/evidence/metadata and actual image explicitly limit return check toT01/T02;T03 in-store registration then14:10 pickup.'},{'case_id':'case-04','issue':'final-v001 metadata retained stale pending-render fields','resolution':'Selection-v002 reads metadata-final-v002; PNG/DSL unaffected. Publisher will finalize passed state.'}],'local_failed_attempts':[str(p/'local-failure-v001.json')],'new_service_requests_from_auditor':0,'new_token_or_cost_measurements':None,'limitations':['All ten problems and operational data are authored realistic hypothetical demonstrations; no fieldwork/user study/real service integration.','Full original images and half-size nearread previews were judged visually. Physical printing, hardware display, distance viewing, color vision and accessibility compliance were not tested.','Previous B05 integrity report decoded/checks files and existing evidence; did not add any new B05 image-view claim.'],'unresolved_issues':[],'pending_after_publication':['Verify published final PNG/DSL hashes match selected originals','Root/case reports and gallery relative links']}
(p/'audit-final-v001.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(p/'views-for-import-v001.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'checks':report['check_count'],'actual_views':len(ledger),'stage':report['status']},ensure_ascii=False))
