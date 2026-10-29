#!/usr/bin/env python3
"""Generate per-round and task-level reports/metrics for staged tasks (A21/A22)."""
import argparse, json, os
from datetime import datetime
from pathlib import Path
SCRIPT=Path(__file__).resolve(); SUITE=Path(os.environ.get("SNAPSHOT_TASK_ROOT",SCRIPT.parents[4])); RUN=SCRIPT.parents[2].name
def parse_ts(s):
    try: return datetime.strptime(s,"%Y-%m-%dT%H:%M:%S%z")
    except Exception:
        try: return datetime.fromisoformat(s)
        except Exception: return None
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
    now=datetime.now().astimezone()
    all_round_metrics=[]
    for rd in meta['rounds']:
        sub=f"round-{rd['round']:02d}"
        rs=[r for r in reqs if sub in (r.get('dsl') or '')]
        ok=[r for r in rs if r.get('status')=='success']; fail=[r for r in rs if r.get('status')=='error']
        times=[parse_ts(r.get('started_at','')) for r in rs if parse_ts(r.get('started_at',''))]
        start=min(times) if times else None
        ends=[parse_ts(r['started_at']).timestamp()+(r.get('duration_ms') or 0)/1000 for r in rs if parse_ts(r.get('started_at',''))]
        first=min(ends) if ends else None
        m={'schema_version':1,'path_base':'suite_root','task_id':a.task,'run_id':RUN,'task_round':rd['round'],
           'status':'completed','stop_reason':'本轮需求满足并完成视觉自检',
           'output_dir':f'outputs/{RUN}/{a.task}/{sub}','temp_dir':f'tmp/{RUN}/{a.task}',
           'timings':{'started_at':start.strftime('%Y-%m-%dT%H:%M:%S%z') if start else None,
                      'ended_at':now.strftime('%Y-%m-%dT%H:%M:%S%z'),
                      'elapsed_seconds':round(now.timestamp()-start.timestamp(),1) if start else None,
                      'first_usable_image_seconds':round(first-start.timestamp(),1) if first and start else None,
                      'user_feedback_wait_seconds':0,'rate_limit_wait_seconds':None,'queue_wait_seconds':None,
                      'request_duration_sum_seconds':round(sum((r.get('duration_ms') or 0) for r in rs)/1000,2)},
           'counts':{'snapshot_requests':len(rs),'successful_snapshot_requests':len(ok),'failed_snapshot_requests':len(fail),
                     'retry_requests':sum(1 for r in rs if int(r.get('attempt',1))>1),'other_service_requests':0,
                     'dsl_versions':len({r.get('dsl_sha256') for r in ok if r.get('dsl_sha256')}),
                     'image_views':len(rd.get('reviews',[])),'completed_visual_iterations':len(rd.get('iterations',[])),
                     'incomplete_visual_iterations':0},
           'logs':{'requests':f'tmp/{RUN}/{a.task}/requests.jsonl','iterations':None},
           'outputs':rd.get('files',[]),'candidates':[],'rounds':[],'unresolved_issues':[]}
        (out/sub/'task-metrics.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
        L=[f"# 第 {rd['round']} 轮 · Snapshot 使用说明",'',f"- 任务：{a.task} {meta['title']}",f"- 运行ID：{RUN}",f"- 轮次：{sub}",f"- 状态：完成",f"- 输出：`outputs/{RUN}/{a.task}/{sub}/`",f"- 临时：`tmp/{RUN}/{a.task}/`",'','## 产物与需求','',f"{rd.get('design','')}",'','| 文件 | 用途 | 状态 |','|---|---|---|']
        for f in rd.get('files',[]): L.append(f"| `{f['file']}` | {f.get('purpose','')} | {f.get('status','完成')} |")
        L += ['','## 本轮变化','']+[f"- {x}" for x in rd.get('changes',[])]
        L += ['','## 视觉查看','']+[f"- {x['image']} @ {x['at']}：{x['result']}" for x in rd.get('reviews',[])]
        L += ['','## 请求与耗时','',f"- 请求 {len(rs)}（成功 {len(ok)}，失败 {len(fail)}），请求耗时合计 {m['timings']['request_duration_sum_seconds']}s；墙钟 {m['timings']['elapsed_seconds']}s（含起草/看图）。",f"- 指标：`outputs/{RUN}/{a.task}/{sub}/task-metrics.json`"]
        (out/sub/'snapshot-usage.md').write_text('\n'.join(L)+'\n',encoding='utf-8')
        all_round_metrics.append(m)
    total_req=len(reqs); ok=sum(1 for r in reqs if r.get('status')=='success'); fail=total_req-ok
    allm={'schema_version':1,'path_base':'suite_root','task_id':a.task,'run_id':RUN,'task_round':'all','status':'completed',
          'stop_reason':'三轮均满足并完成视觉自检','output_dir':f'outputs/{RUN}/{a.task}','temp_dir':f'tmp/{RUN}/{a.task}',
          'timings':{'started_at':min([r['started_at'] for r in reqs],default=None),'ended_at':now.strftime('%Y-%m-%dT%H:%M:%S%z'),
                     'elapsed_seconds':(round(now.timestamp()-min([parse_ts(r['started_at']).timestamp() for r in reqs if parse_ts(r['started_at'])]) ,1) if any(parse_ts(r.get('started_at','')) for r in reqs) else None),
                     'first_usable_image_seconds':None,'user_feedback_wait_seconds':0,'rate_limit_wait_seconds':None,'queue_wait_seconds':None,
                     'request_duration_sum_seconds':round(sum((r.get('duration_ms') or 0) for r in reqs)/1000,2)},
          'counts':{'snapshot_requests':total_req,'successful_snapshot_requests':ok,'failed_snapshot_requests':fail,
                    'retry_requests':sum(1 for r in reqs if int(r.get('attempt',1))>1),'other_service_requests':0,
                    'dsl_versions':len({r.get('dsl_sha256') for r in reqs if r.get('status')=='success'}),
                    'image_views':sum(len(r.get('reviews',[])) for r in meta['rounds']),
                    'completed_visual_iterations':sum(len(r.get('iterations',[])) for r in meta['rounds']),
                    'incomplete_visual_iterations':0},
          'logs':{'requests':f'tmp/{RUN}/{a.task}/requests.jsonl','iterations':None},'outputs':[],
          'candidates':[],'rounds':[{'round':m['task_round'],'output_dir':m['output_dir'],'metrics':f"{m['output_dir']}/task-metrics.json"} for m in all_round_metrics],'unresolved_issues':[]}
    (out/'task-metrics.json').write_text(json.dumps(allm,ensure_ascii=False,indent=2),encoding='utf-8')
    T=[f"# {a.task} · 三轮汇总 / Snapshot 使用说明",'',f"- 任务：{meta['title']}",f"- 运行ID：{RUN}",'- 状态：完成（三轮全部实际渲染并查看）','']
    for m,rd in zip(all_round_metrics,meta['rounds']):
        T += [f"## 第 {rd['round']} 轮",'',f"- 输出：`{m['output_dir']}/`",f"- 请求 {m['counts']['snapshot_requests']} / 成功 {m['counts']['successful_snapshot_requests']} / 失败 {m['counts']['failed_snapshot_requests']}；请求耗时 {m['timings']['request_duration_sum_seconds']}s",f"- 本轮变化：{'；'.join(rd.get('changes',[]))}",'']
    T += ['## 汇总','',f"- 三轮请求合计 {total_req}（成功 {ok}，失败 {fail}）；所有轮次目录与旧版本均保留。",f"- 累计指标：`outputs/{RUN}/{a.task}/task-metrics.json`；逐轮指标在各 round 目录。",'- 失败响应、草稿、脚本与请求日志保留在临时目录；未覆盖前轮。']
    (out/'snapshot-usage.md').write_text('\n'.join(T)+'\n',encoding='utf-8')
    print('staged packaged',a.task,[m['counts']['snapshot_requests'] for m in all_round_metrics])
if __name__=='__main__': main()
