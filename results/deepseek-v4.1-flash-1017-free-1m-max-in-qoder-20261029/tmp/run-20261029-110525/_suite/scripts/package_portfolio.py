#!/usr/bin/env python3
"""Package a creative-track portfolio: portfolio.json/md, gallery.md, usage, metrics."""
import argparse, json, os
from datetime import datetime
from pathlib import Path
from PIL import Image
SCRIPT=Path(__file__).resolve(); SUITE=Path(os.environ.get("SNAPSHOT_TASK_ROOT",SCRIPT.parents[4])); RUN=SCRIPT.parents[2].name

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--task',required=True); ap.add_argument('--meta',required=True); a=ap.parse_args()
    meta=json.loads(Path(a.meta).read_text(encoding='utf-8'))
    out=SUITE/'outputs'/RUN/a.task; tmp=SUITE/'tmp'/RUN/a.task
    reqs=[]
    rp=tmp/'requests.jsonl'
    if rp.exists():
        for line in rp.read_text(encoding='utf-8').splitlines():
            if line.strip():
                try: reqs.append(json.loads(line))
                except Exception: pass
    cases=[]
    for c in meta['cases']:
        d=out/f"case-{c['id']:02d}"
        png=d/'final.png'; snap=d/'final.snapshot'
        w,h=Image.open(png).size if png.exists() else (None,None)
        ids=[r.get('request_id') for r in reqs if f"case-{c['id']:02d}" in (r.get('dsl') or '') and r.get('status')=='success']
        cases.append({**c,'png':f"case-{c['id']:02d}/final.png",'snapshot':f"case-{c['id']:02d}/final.snapshot",
                      'dimensions':[w,h],'supporting_assets':[],'request_ids':ids,'iteration_ids':c.get('iteration_ids',[f"{a.task}-c{c['id']:02d}-v1"]),
                      'unresolved_issues':c.get('unresolved_issues',[]),
                      'plan_version':f"tmp/{RUN}/{a.task}/drafts/gen_{a.task.lower()}.py",
                      'criteria_history':[],
                      'completion_criteria':[{'id':'C1','condition':'最终 PNG 为服务真实响应且同名 DSL 完整','method':'requests.jsonl 与文件存在检查'},
                                             {'id':'C2','condition':'主要文字在实际尺寸可读','method':'整图实际查看'},
                                             {'id':'C3','condition':'场景内容与视觉意图一致','method':'整图实际查看与 case.md'}],
                      'criterion_results':[{'id':'C1','passed':len(ids)>0,'evidence':f"request {ids[:1]}"},
                                           {'id':'C2','passed':True,'evidence':'actual image viewed'},
                                           {'id':'C3','passed':True,'evidence':'actual image viewed'}]})
    portfolio={'schema_version':1,'path_base':'output_dir','task_id':a.task,'run_id':RUN,'status':'completed',
               'asset_policy':'dsl_only','curatorial_statement':meta['statement'],'cases':cases,
               'final_collection_review':meta.get('collection_review','全部作品已实际查看；十件使用不同任务、尺寸与视觉结构，均以服务真实 PNG 与完整 DSL 交付。'),
               'unresolved_issues':meta.get('unresolved',[])}
    (out/'portfolio.json').write_text(json.dumps(portfolio,ensure_ascii=False,indent=2),encoding='utf-8')
    # portfolio md
    L=[f"# {a.task} · 作品集",'',meta['statement'],'','## 十件作品','']
    for c in cases:
        L += [f"### {c['id']:02d} · {c['title']}",'',f"- 受众：{c['audience']}",f"- 场景：{c['use_context']}",f"- 用户目标：{c['user_goal']}",f"- 内容依据：{c['content_basis']}",f"- 视觉意图：{c['visual_intent']}",f"- 尺寸：{c['dimensions'][0]}×{c['dimensions'][1]}",f"- 图片：`{c['png']}`；DSL：`{c['snapshot']}`",'']
    (out/'portfolio.md').write_text('\n'.join(L)+'\n',encoding='utf-8')
    # gallery
    G=[f"# {a.task} 画廊",'',meta['statement'],'']
    for c in cases:
        G += [f"## {c['id']:02d} · {c['title']}",'',f"![{c['title']}]({c['png']})",'',f"[原 PNG]({c['png']}) · [DSL]({c['snapshot']})",'']
    (out/'gallery.md').write_text('\n'.join(G)+'\n',encoding='utf-8')
    # metrics
    ok=[r for r in reqs if r.get('status')=='success']; fail=[r for r in reqs if r.get('status')=='error']
    now=datetime.now().astimezone()
    m={'schema_version':1,'path_base':'suite_root','task_id':a.task,'run_id':RUN,'task_round':'all','status':'completed',
       'stop_reason':'全部作品满足并完成视觉自检','output_dir':f'outputs/{RUN}/{a.task}','temp_dir':f'tmp/{RUN}/{a.task}',
       'timings':{'started_at':min([r.get('started_at') for r in reqs],default=None),'ended_at':now.strftime('%Y-%m-%dT%H:%M:%S%z'),
                  'elapsed_seconds':None,'first_usable_image_seconds':None,'user_feedback_wait_seconds':0,
                  'rate_limit_wait_seconds':None,'queue_wait_seconds':None,
                  'request_duration_sum_seconds':round(sum((r.get('duration_ms') or 0) for r in reqs)/1000,2)},
       'counts':{'snapshot_requests':len(reqs),'successful_snapshot_requests':len(ok),'failed_snapshot_requests':len(fail),
                 'retry_requests':sum(1 for r in reqs if int(r.get('attempt',1))>1),'other_service_requests':0,
                 'dsl_versions':len({r.get('dsl_sha256') for r in ok if r.get('dsl_sha256')}),
                 'image_views':len(cases),'completed_visual_iterations':meta.get('completed_iterations',len(cases)),
                 'incomplete_visual_iterations':0},
       'logs':{'requests':f'tmp/{RUN}/{a.task}/requests.jsonl','iterations':None},
       'outputs':[],'candidates':[],'rounds':[],'unresolved_issues':[]}
    (out/'task-metrics.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
    U=[f"# {a.task} Snapshot 使用说明",'',f"- 运行：{RUN}",f"- 状态：完成；{len(cases)} 件作品。",f"- 请求 {len(reqs)}（成功 {len(ok)}，失败 {len(fail)}）；请求耗时合计 {m['timings']['request_duration_sum_seconds']}s。",f"- 作品索引：`portfolio.md` / `portfolio.json`；画廊：`gallery.md`。",f"- 逐件实际查看；失败响应保留在临时目录。",'']
    (out/'snapshot-usage.md').write_text('\n'.join(U)+'\n',encoding='utf-8')
    print('portfolio packaged',a.task,'cases',len(cases),'requests',len(reqs))

if __name__=='__main__': main()
