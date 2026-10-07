"""Validate the single-root sequential task suite; no task execution.

Checks public requirements, input availability, automatic rounds, unified directories
and manifests. task-suite is the canonical source directory. No ZIP is created by default.
Use --refresh-manifest after intentional input edits; --archive explicitly requests a ZIP.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'task-suite'
EVAL=ROOT/'evaluation'/'task-suite'
checks=[]
RUNTIME_CACHE_DIRS={'__pycache__','.pytest_cache','.mypy_cache','.ruff_cache'}


def portable_path(value, allow_environment=True):
    """Accept relative filesystem paths on both Windows and POSIX hosts."""
    if not isinstance(value,str) or not value.strip():return False
    if not allow_environment and re.search(r'%[^%]+%|\$(?:[A-Za-z_]|\{)',value):return False
    if ':' in value:
        environment_root=re.match(r'^\$env:[A-Za-z_][A-Za-z0-9_]*(?=$|[\\/])',value) if allow_environment else None
        if environment_root is None or ':' in value[environment_root.end():]:return False
    windows=PureWindowsPath(value)
    return not windows.drive and not windows.root and not PurePosixPath(value).is_absolute() and not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',value)


def suite_input(base,value):
    return portable_path(value,allow_environment=False) and (base/value).resolve().is_relative_to(PACK.resolve())


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def check(name,passed,detail=None):
    checks.append({'check':name,'passed':bool(passed),'detail':detail})


def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def published_files():
    return [p for p in sorted(PACK.rglob('*')) if p.is_file()
            and p.name!='manifest.json' and p!=PACK/'.gitignore'
            and p.suffix not in {'.pyc','.pyo'}
            and not ({'outputs','tmp'} | RUNTIME_CACHE_DIRS) & set(p.relative_to(PACK).parts)]


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
    parser.add_argument('--archive',action='store_true',help='Also create and verify a distribution ZIP.')
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
    check('required root entries',all((PACK/p).is_file() for p in ['AGENTS.md','PATHS.md','TASKS.md','START-PROMPT.txt','README.md','catalog.json','run-config.json','templates/suite-state-template.json','templates/suite-metrics-template.json','templates/gitignore-template.txt']))
    check('portable root directories',all(portable_path(config.get(key)) for key in ['output_root','temp_root']))
    policy=config.get('path_policy',{})
    check('portable path policy covers documents scripts and artifacts',policy=={
        'artifact_paths':'relative_to_suite_root_or_environment_variable',
        'config_paths':'relative_to_config_file_or_environment_variable',
        'document_links':'relative_to_document',
        'script_paths':'relative_to_declared_base_or_environment_variable',
        'hardcoded_machine_paths':False})
    state=load(PACK/'templates'/'suite-state-template.json')
    check('state and suite metrics paths relative to suite root',state.get('path_base')=='suite_root' and load(PACK/'templates'/'suite-metrics-template.json').get('path_base')=='suite_root')
    check('state template contains unexecuted complete roster',[t['id'] for t in state['tasks']]==expected and state['status']=='not_started' and all(t['status']=='pending' for t in state['tasks']))
    cache_policy=config.get('runtime_cache_policy',{})
    check('runtime cache policy requires root gitignore and preserves evidence',cache_policy=={
        'create_root_gitignore':True,
        'gitignore_template':'templates/gitignore-template.txt',
        'runtime_caches_are_evidence':False,
        'archive_runtime_caches':False,
        'preserve_process_evidence':True})
    ignore_template=PACK/'templates'/'gitignore-template.txt'
    ignore_rules=[line.strip() for line in ignore_template.read_text(encoding='utf-8').splitlines() if line.strip() and not line.lstrip().startswith('#')] if ignore_template.is_file() else []
    check('runtime cache template has only narrow default rules',ignore_rules==['__pycache__/','*.pyc','*.pyo','.pytest_cache/','.mypy_cache/','.ruff_cache/'])
    root_agents=(PACK/'AGENTS.md').read_text(encoding='utf-8')
    check('root gitignore creation and evidence boundaries explicit',all(term in root_agents for term in ['在总任务根创建','.gitignore','templates/gitignore-template.txt','不属于过程留痕','已下载文档缓存','最终审查确认文件存在']))
    check('portable paths and script policy explicit','[PATHS.md](PATHS.md)' in root_agents and '程序脚本' in root_agents and '相对路径' in root_agents)
    check('shared preparation and deduplication explicit','不再把同题round/case明细重复相加' in root_agents)
    check('persistent state and real resume supported','checkpoints/state-000001.json' in root_agents and '从未完成处继续' in root_agents)
    check('completion requires complete suite audit','30题全部满足才最终回复全套完成' in root_agents)
    suite_artifacts=['index.md','gallery.md','snapshot-usage.md','task-metrics.json','suite-state.json']
    check('suite deliverables include Markdown gallery',config.get('suite_required_artifacts')==suite_artifacts)
    check('suite artifacts state starts empty',state.get('suite_artifacts')==[])
    check('suite deliverables documented',all('- '+name+'：' in root_agents for name in suite_artifacts))
    check('Markdown gallery covers all images with relative PNG and DSL links',all(text in root_agents for text in ['索引全套最终图、A21/A22所有轮次和B类全部作品','Markdown图片预览','原PNG链接','对应.snapshot链接','相对本文件所在的_suite/目录']))
    check('Markdown gallery required for completion','画廊缺失、漏图或链接失效时继续修正' in root_agents)
    for name in ['START-PROMPT.txt','README.md','TASKS.md']:
        prose=(PACK/name).read_text(encoding='utf-8')
        check('Markdown gallery explicit in '+name,'gallery.md' in prose)
        check('portable paths explicit in '+name,'PATHS.md' in prose and '相对路径' in prose)
        check('root runtime cache ignore explicit in '+name,'.gitignore' in prose and '运行时缓存' in prose)
    for task in catalog['tasks']:
        catalog_fields=['directory','entry','task_spec','output_dir_template','temp_dir_template']
        valid_catalog=all(suite_input(PACK,task.get(key)) for key in catalog_fields)
        check(task['id']+' portable catalog paths',valid_catalog)
        if not valid_catalog:continue
        folder=PACK/task['directory']
        spec=load(PACK/task['task_spec'])
        local_config=load(folder/'run-config.json')
        input_values=spec['inputs']+[spec['instructions_file'],spec['suite_instructions_file'],local_config['suite_config']]+[rnd['requirements_file'] for rnd in spec.get('rounds',[])]
        valid_inputs=all(suite_input(folder,value) for value in input_values)
        check(task['id']+' portable input and inherited paths',valid_inputs)
        if not valid_inputs:continue
        check(task['id']+' portable configured directories',all(portable_path(local_config.get(key)) for key in ['output_root','temp_root','output_dir_template','temp_dir_template']))
        output_values=[spec['output_dir_template'],spec['temp_dir_template']]+spec.get('additional_outputs',[])+spec.get('common_outputs',[])
        output_values += [value for image in spec.get('required_outputs',[]) for value in [image['filename'],image['dsl']]]
        output_values += spec.get('case_artifacts',[])+spec.get('log_files',[])
        output_values += [rnd['output_subdirectory'] for rnd in spec.get('rounds',[])]
        output_values += [value for rnd in spec.get('rounds',[]) for image in rnd['required_outputs'] for value in [image['filename'],image['dsl']]]
        check(task['id']+' portable output names',all(portable_path(value,allow_environment=False) for value in output_values))
        agents=(folder/'AGENTS.md').read_text(encoding='utf-8')
        report=(folder/'templates'/'snapshot-usage-template.md').read_text(encoding='utf-8')
        check(task['id']+' portable script and report policy','../../PATHS.md' in agents and '程序脚本' in agents and '绝对路径' not in agents and '实际绝对路径' not in report and '../../../PATHS.md' in report)
        check(task['id']+' runtime cache exception and root gitignore inherited',all(term in agents for term in ['总任务根','.gitignore','__pycache__/','../../templates/gitignore-template.txt']) and all(term in report for term in ['.gitignore','运行时缓存不要求留痕','不列为产物或自检证据']))
        check(task['id']+' configured path base explicit','相对本配置文件所在目录' in local_config.get('directory_resolution',''))
        metrics=load(folder/'templates'/'task-metrics-template.json')
        check(task['id']+' metrics paths relative to suite root',metrics.get('path_base')=='suite_root')
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
            check(task['id']+' portfolio paths relative to task output',load(folder/'templates'/'portfolio-template.json').get('path_base')=='output_dir')
            agents=(folder/'AGENTS.md').read_text(encoding='utf-8')
            check(task['id']+' Markdown gallery delivery','gallery.md' in spec['common_outputs'] and 'gallery.md' in prose and all(text in agents for text in ['gallery.md','Markdown图片预览','原PNG和对应.snapshot链接']))
            check(task['id']+' at least ten independent cases',spec['minimum_independent_cases']==local_config['minimum_independent_cases']==10)
            check(task['id']+' unrestricted subject/style/dimensions',all(spec[k] is None for k in ['preassigned_scenarios','preassigned_style','fixed_canvas_dimensions']))
    # Links may cross from a child to the suite root; they may not depend on the repo outside it.
    for path in [p for p in published_files() if p.suffix=='.md']:
        for match in re.finditer(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            target=match.group(1).split('#',1)[0]
            if not target or re.match(r'^(?:https?://|mailto:)',target,re.IGNORECASE):continue
            relative=portable_path(target,allow_environment=False)
            check('portable local link '+str(path.relative_to(PACK))+' → '+target,relative)
            if not relative:continue
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
        value=entry['path']
        safe=portable_path(value,allow_environment=False) and '..' not in PureWindowsPath(value).parts and '..' not in PurePosixPath(value).parts
        check('safe manifest path '+value,safe)
        if not safe:continue
        path=PACK/value
        exists=path.is_file() and path.resolve().is_relative_to(PACK.resolve())
        check('manifest file exists '+value,exists)
        if not exists:continue
        data=path.read_bytes()
        check('manifest integrity '+value,len(data)==entry['size_bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256'])
    failed=[x for x in checks if not x['passed']]
    if failed:
        dump(EVAL/'authoring-validation.json',{'status':'failed','checks':checks,'errors':failed,'full_suite_trial':False})
        raise SystemExit(json.dumps(failed,ensure_ascii=False))
    archive=None
    if args.archive:
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
        'suite_required_artifacts':suite_artifacts,
        'archive':archive.relative_to(ROOT).as_posix() if archive else None,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest() if archive else None,
        'full_suite_trial':False,'scope':'全套根目录、流程、输入、交付约定与可选分发检查；没有执行30题。'}
    dump(EVAL/'authoring-validation.json',summary)
    if archive:
        dump(ROOT/'dist'/'snapshot-task-suite.json',{k:v for k,v in summary.items() if k!='checks'})
    print(json.dumps({k:v for k,v in summary.items() if k!='checks'},ensure_ascii=False))
    if summary['status']!='passed':raise SystemExit(1)


if __name__=='__main__':main()
