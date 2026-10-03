"""Validate and zip the single-root sequential task suite; no task execution.

Checks public requirements, input availability, automatic rounds, unified directories,
manifests and exact archive bytes. task-suite is the canonical source directory.
Use --refresh-manifest after intentionally editing published inputs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'task-suite'
EVAL=ROOT/'evaluation'/'task-suite'
checks=[]


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def check(name,passed,detail=None):
    checks.append({'check':name,'passed':bool(passed),'detail':detail})


def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def published_files():
    return [p for p in sorted(PACK.rglob('*')) if p.is_file()
            and p.name!='manifest.json'
            and not {'outputs','tmp'} & set(p.relative_to(PACK).parts)]


def refresh_manifest():
    manifest=load(PACK/'manifest.json')
    manifest['files']=[{'path':p.relative_to(PACK).as_posix(),
                        'size_bytes':p.stat().st_size,
                        'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                       for p in published_files()]
    dump(PACK/'manifest.json',manifest)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-manifest',action='store_true',
                        help='Refresh input hashes after intentional task-suite edits.')
    args=parser.parse_args()
    catalog=load(PACK/'catalog.json')
    config=load(PACK/'run-config.json')
    expected=[f'A{i:02}' for i in range(1,25)]+[f'B{i:02}' for i in range(1,7)]
    check('default all thirty tasks in order',catalog['task_count']==30 and catalog['task_order']==expected and config['default_profile']=='all' and config['profiles']['all']==expected)
    check('minimum 124 final PNGs',sum(t['minimum_final_pngs'] for t in catalog['tasks'])==catalog['minimum_final_pngs']==124)
    check('six creative tasks at least sixty cases',sum(t.get('minimum_independent_cases',0) for t in catalog['tasks'])==60)
    check('no per-task confirmation',config['requires_per_task_user_confirmation'] is False)
    check('sequential automatic three-round mode',config['execution_mode']=='sequential' and config['round_execution']=='preloaded_sequential')
    check('unlimited render and visual iteration',config['max_render_requests'] is None and config['max_visual_iterations'] is None)
    check('required root entries',all((PACK/p).is_file() for p in ['AGENTS.md','TASKS.md','START-PROMPT.txt','README.md','catalog.json','run-config.json','templates/suite-state-template.json','templates/suite-metrics-template.json']))
    state=load(PACK/'templates'/'suite-state-template.json')
    check('state template contains unexecuted complete roster',[t['id'] for t in state['tasks']]==expected and state['status']=='not_started' and all(t['status']=='pending' for t in state['tasks']))
    root_agents=(PACK/'AGENTS.md').read_text(encoding='utf-8')
    check('shared preparation and deduplication explicit','不再把同题round/case明细重复相加' in root_agents)
    check('persistent state and real resume supported','checkpoints/state-000001.json' in root_agents and '从未完成处继续' in root_agents)
    check('completion requires complete suite audit','30题全部满足才最终回复全套完成' in root_agents)
    for task in catalog['tasks']:
        folder=PACK/task['directory']
        spec=load(PACK/task['task_spec'])
        local_config=load(folder/'run-config.json')
        for name in ['AGENTS.md','TASK.md','task.json','run-config.json','templates/task-metrics-template.json','templates/snapshot-usage-template.md']+spec['inputs']:
            check(task['id']+' local input '+name,(folder/name).is_file())
        check(task['id']+' metadata and order identity',spec['id']==task['id'] and spec['execution_mode']=='sequential_suite')
        check(task['id']+' unified output template',spec['output_dir_template']==f"outputs/{{run_id}}/{task['id']}/" and spec['temp_dir_template']==f"tmp/{{run_id}}/{task['id']}/")
        check(task['id']+' suite config inherited',(folder/local_config['suite_config']).resolve()==(PACK/'run-config.json').resolve())
        check(task['id']+' suite instructions inherited',(folder/spec['suite_instructions_file']).resolve()==(PACK/'AGENTS.md').resolve())
        prose=(folder/'TASK.md').read_text(encoding='utf-8')
        check(task['id']+' explicitly continues suite','单题完成后继续总清单下一题' in prose)
        for image in spec.get('required_outputs',[]):
            check(task['id']+' same-stem snapshot '+image['filename'],Path(image['filename']).with_suffix('.snapshot').as_posix()==image['dsl'])
            check(task['id']+' supported dimensions '+image['filename'],0<image['width']<=4096 and 0<image['height']<=4096)
        if task['id'] in ['A21','A22']:
            check(task['id']+' three rounds available',task['round_count']==3 and len(spec['rounds'])==3 and spec['round_execution']=='preloaded_sequential' and spec['blind_feedback'] is False)
            check(task['id']+' no waiting in adapted prompt',all(term not in spec['prompt'] for term in ['等待评测者','当前只完成第一轮','等评测者发送','接收下一轮反馈即可']))
            check(task['id']+' prompt synchronized',spec['prompt'].strip() in prose)
            for rnd in spec['rounds']:
                check(task['id']+' round requirement '+str(rnd['round']),(folder/rnd['requirements_file']).is_file())
                check(task['id']+' round output prefix '+str(rnd['round']),all(x['filename'].startswith(rnd['output_subdirectory']+'/') and x['dsl'].startswith(rnd['output_subdirectory']+'/') for x in rnd['required_outputs']))
                if rnd['round']>1:
                    requirement=folder/rnd['requirements_file']
                    check(task['id']+' nonempty feedback text '+str(rnd['round']),requirement.is_file() and bool(requirement.read_text(encoding='utf-8').strip()))
            check(task['id']+' all round output count',len(spec['required_outputs'])==task['minimum_final_pngs'])
        if task['track']=='creative':
            check(task['id']+' at least ten independent cases',spec['minimum_independent_cases']==local_config['minimum_independent_cases']==10)
            check(task['id']+' unrestricted subject/style/dimensions',all(spec[k] is None for k in ['preassigned_scenarios','preassigned_style','fixed_canvas_dimensions']))
    # Links may cross from a child to the suite root; they may not depend on the repo outside it.
    for path in [p for p in published_files() if p.suffix=='.md']:
        for match in re.finditer(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            target=match.group(1).split('#',1)[0]
            if not target or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target):continue
            dest=(path.parent/target).resolve()
            check('local link '+str(path.relative_to(PACK))+' → '+target,dest.is_file() and dest.is_relative_to(PACK.resolve()))
    json_count=0
    for path in [p for p in published_files() if p.suffix=='.json']:
        try:load(path);json_count+=1
        except Exception as exc:check('JSON '+str(path.relative_to(PACK)),False,str(exc))
    forbidden={'evaluation','checklists','references','fixtures','solutions','scoring.json','author-data-002.json','source-inputs.json'}
    check('no evaluator material/answers in suite',not any(forbidden & set(p.relative_to(PACK).parts) for p in published_files()))
    if args.refresh_manifest and all(x['passed'] for x in checks):
        refresh_manifest()
    manifest=load(PACK/'manifest.json')
    actual={p.relative_to(PACK).as_posix() for p in published_files()}
    check('manifest exact published inventory',actual=={entry['path'] for entry in manifest['files']})
    for entry in manifest['files']:
        path=PACK/entry['path'];data=path.read_bytes()
        check('manifest integrity '+entry['path'],len(data)==entry['size_bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256'])
        check('safe manifest path '+entry['path'],not Path(entry['path']).is_absolute() and '..' not in Path(entry['path']).parts)
    failed=[x for x in checks if not x['passed']]
    if failed:
        dump(EVAL/'authoring-validation.json',{'status':'failed','checks':checks,'errors':failed,'full_suite_trial':False})
        raise SystemExit(json.dumps(failed,ensure_ascii=False))
    archive=ROOT/'dist'/'snapshot-task-suite.zip'
    archive.parent.mkdir(exist_ok=True)
    files=[entry['path'] for entry in manifest['files']]+['manifest.json']
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for file in files:z.write(PACK/file,'task-suite/'+file)
    with zipfile.ZipFile(archive) as z:
        check('archive CRC and exact inventory',z.testzip() is None and set(z.namelist())=={'task-suite/'+f for f in files})
        for file in files:check('archive exact payload '+file,z.read('task-suite/'+file)==(PACK/file).read_bytes())
    summary={'checked_at':datetime.now(timezone.utc).isoformat(),
        'status':'passed' if all(x['passed'] for x in checks) else 'failed',
        'tasks':30,'minimum_final_pngs':124,'canonical_task_root':'task-suite',
        'preloaded_round_tasks':['A21','A22'],'published_input_files':len(manifest['files']),
        'json_files_checked':json_count,'check_count':len(checks),'checks':checks,
        'archive':str(archive),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
        'full_suite_trial':False,'scope':'全套根目录、流程、输入与分发检查；没有执行30题。'}
    dump(EVAL/'authoring-validation.json',summary)
    dump(ROOT/'dist'/'snapshot-task-suite.json',{k:v for k,v in summary.items() if k!='checks'})
    print(json.dumps({k:v for k,v in summary.items() if k!='checks'},ensure_ascii=False))
    if summary['status']!='passed':raise SystemExit(1)


if __name__=='__main__':main()
