#!/usr/bin/env python3
"""A24 release plan: schedule search result, three views, audits."""
import json, os, math, html
from datetime import datetime, timedelta, timezone
from pathlib import Path
SCRIPT=Path(__file__).resolve(); SUITE=Path(os.environ.get("SNAPSHOT_TASK_ROOT",SCRIPT.parents[4])); RUN=SCRIPT.parents[2].name
OUT=SUITE/'outputs'/RUN/'A24'; OUT.mkdir(parents=True,exist_ok=True)
data=json.loads((SUITE/'tasks/A24-release-plan-capstone/inputs/release.json').read_text(encoding='utf-8'))
tasks={t['id']:t for t in data['tasks']}
SCHED={'R01':('design',0,25),'R02':('engineering',0,20),'R03':('engineering',20,60),'R04':('design',25,85),
       'R05':('engineering',60,90),'R06':('engineering',90,135),'R07':('design',90,160),'R08':('engineering',135,200),
       'R09':('design',160,205),'R10':('design',205,240),'R11':('engineering',205,235),'R12':('design',240,260)}
def esc(s): return html.escape(str(s),quote=False)
def T(txt,size,color="#0B1220",bold=False,extra=""):
    st=' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'
def hhmm(m):
    t=datetime.fromisoformat(data['start'])+timedelta(minutes=m); return t.strftime('%H:%M')
TCOL={'design':'#2563EB','engineering':'#0D9488'}
# schedule json
sched={'schema_version':1,'task_id':'A24','path_base':'output_dir','timezone':'+08:00',
 'window':{'start':data['start'],'deadline':data['deadline'],'minutes':420},
 'makespan_minutes':260,'finish_time':hhmm(260),'buffer_minutes':160,
 'tasks':[{'id':tid,'label':tasks[tid]['label'],'team':SCHED[tid][0],'start_min':SCHED[tid][1],'end_min':SCHED[tid][2],
           'start_time':hhmm(SCHED[tid][1]),'end_time':hhmm(SCHED[tid][2]),'minutes':tasks[tid]['minutes'],
           'depends':tasks[tid]['depends']} for tid in sorted(SCHED)]}
(OUT/'schedule.json').write_text(json.dumps(sched,ensure_ascii=False,indent=2),encoding='utf-8')
# audit
def intervals(team):
    return sorted((SCHED[t][1],SCHED[t][2],t) for t in SCHED if SCHED[t][0]==team)
conf=[]
for team in data['teams']:
    iv=intervals(team)
    for a,b in zip(iv,iv[1:]):
        if b[0]<a[1]: conf.append({'team':team,'a':a[2],'b':b[2]})
depbad=[]
for tid,(team,s,e) in SCHED.items():
    for d in tasks[tid]['depends']:
        if SCHED[d][2]>s: depbad.append({'task':tid,'dep':d})
def lp(tid): return tasks[tid]['minutes']+max([lp(d) for d in tasks[tid]['depends']],default=0)
cp=max(lp(t) for t in tasks); work=sum(t['minutes'] for t in data['tasks'])
audit={'schema_version':1,'task_id':'A24','path_base':'output_dir',
 'resource_conflicts':conf,'dependency_violations':depbad,
 'duration_check':all(SCHED[t][2]-SCHED[t][1]==tasks[t]['minutes'] for t in tasks),
 'within_window':all(SCHED[t][1]>=0 and SCHED[t][2]<=420 for t in tasks),
 'makespan_minutes':260,'buffer_minutes':160,'critical_path_minutes':cp,'total_work_minutes':work,
 'work_over_two_teams_lower_bound':work/2,'best_known_lower_bound':max(cp,work/2),
 'proven_optimal':False,'optimality_note':'260 分钟为可行排程，距依赖关键路径下界 255 分钟差 5 分钟；未做全局最优证明，不称最优。',
 'team_intervals':{team:[{'id':t,'start':a,'end':b} for a,b,t in intervals(team)] for team in data['teams']},
 'risk_notes':data['risks']}
(OUT/'schedule-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
# content map
cm={'schema_version':1,'task_id':'A24','path_base':'output_dir','canvases':{
 'execution-board':{'canvas':[1920,1080],'regions':{'header':[40,30,1880,130],'design_lane':[240,220,1840,430],'engineering_lane':[240,450,1840,660],'index':[40,690,1880,1030]}},
 'decision-brief':{'canvas':[1200,1600],'regions':{'header':[48,48,1152,300],'kpi':[48,320,1152,500],'critical_path':[48,530,1152,640],'dependencies':[48,660,1152,1100],'risks':[48,1130,1152,1430]}},
 'action-card':{'canvas':[720,1280],'regions':{'header':[36,30,684,180],'list':[36,190,684,1160],'footer':[36,1170,684,1250]}}}}
(OUT/'content-map.json').write_text(json.dumps(cm,ensure_ascii=False,indent=2),encoding='utf-8')
# execution board
W,H=1920,1080
p=['<Snapshot background="#F4F6FA" type="png"><Container width="1920" height="1080"><Stack alignment="TOP_LEFT"><Container width="1920" height="1080" color="#F4F6FA"/>']
p.append('<Positioned left="40" top="30"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("叠光 · 发布演练 / RELEASE WAR ROOM",14,"#2563EB",True,' letterSpacing="2"')+T("发布作战计划 · 2026.11.07",36,"#0B1220",True)+T("09:00 开工 · 16:00 截止 · 12 任务 · 双团队 · 计划完成 13:20 · 缓冲 160 分钟",22,"#56637A")+'</Column></Positioned>')
p.append('<Positioned left="40" top="140"><Container width="1880" height="1" color="#CBD5E1"/></Positioned>')
X0,X1=240,1840; scale=(X1-X0)/420
for h in range(9,17):
    x=X0+(h-9)*60*scale
    p.append(f'<Positioned left="{x-30:.1f}" top="160" width="60"><Container width="60" alignment="CENTER">'+T(f"{h:02d}:00",18,"#475569",True)+'</Container></Positioned>')
    p.append(f'<Positioned left="{x:.1f}" top="185" width="1" height="480"><Container width="1" height="480" color="#E3E9F2"/></Positioned>')
for team,y,label in [('design',220,'设计 / design'),('engineering',450,'工程 / ENG')]:
    p.append(f'<Positioned left="40" top="{y}"><Container width="180" height="210" color="#FFFFFF" borderRadius="14" border="1 SOLID #E1E7F0" padding="14"><Column crossAxisAlignment="START" mainAxisSize="MIN"><Row crossAxisAlignment="CENTER"><Container width="10" height="10" color="{TCOL[team]}" borderRadius="3"/><SizedBox width="8"/>'+T(label,20,"#0B1220",True)+'</Row>'+T("单团队串行",15,"#64748B")+'</Column></Container></Positioned>')
    p.append(f'<Positioned left="{X0}" top="{y}" width="{X1-X0}" height="210"><Container width="{X1-X0}" height="210" color="#FFFFFF" borderRadius="14" border="1 SOLID #E1E7F0"/></Positioned>')
for tid,(team,s,e) in SCHED.items():
    x=X0+s*scale; w=(e-s)*scale; y=220 if team=='design' else 450
    p.append(f'<Positioned left="{x+2:.1f}" top="{y+20}" width="{w-4:.1f}" height="170"><Container width="{w-4:.1f}" height="170" color="{TCOL[team]}" borderRadius="8" padding="10"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T(tid,20,"#FFFFFF",True)+(T(f"{hhmm(s)}–{hhmm(e)}",18,"#FFFFFFDD") if w>110 else (T(hhmm(s),16,"#FFFFFFDD")+T(hhmm(e),16,"#FFFFFFDD"))))
    if w>150: p.append(T(tasks[tid]['label'],18,"#FFFFFF",True,' maxLines="2"'))
    p.append('</Column></Container></Positioned>')
p.append(f'<Positioned left="{X1-1}" top="180" width="2" height="490"><Container width="2" height="490" color="#DC2626"/></Positioned>')
p.append('<Positioned left="1758" top="672">'+T("16:00 截止",18,"#DC2626",True)+'</Positioned>')
# buffer band
bx=X0+261*scale+6
p.append(f'<Positioned left="{bx:.1f}" top="220" width="{X1-bx:.1f}" height="440"><Container width="{X1-bx:.1f}" height="440" color="#DCFCE7" borderRadius="10" border="1 SOLID #86EFAC"/></Positioned>')
p.append(f'<Positioned left="{bx+20:.1f}" top="320" width="{X1-bx-40:.1f}"><Container width="{X1-bx-40:.1f}" alignment="CENTER">'+T("缓冲 160 分钟 / 420 − 260",22,"#166534",True)+'</Container></Positioned>')
# index 2x6
p.append('<Positioned left="40" top="700"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("任务索引 / DEPENDENCIES",18,"#2563EB",True,' letterSpacing="1.5"')+'<SizedBox height="8"/>')
for row in range(2):
    p.append('<Row crossAxisAlignment="CENTER">')
    for col in range(6):
        tid=sorted(SCHED)[row*6+col]
        team,s,e=SCHED[tid]; deps=", ".join(tasks[tid]['depends']) or "—"
        p.append(f'<Container width="300" height="140" color="#FFFFFF" borderRadius="10" border="1 SOLID #E1E7F0" padding="10" margin="(0,0,10,10)"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
        p.append('<Row crossAxisAlignment="CENTER">'+T(tid,20,"#0B1220",True)+'<SizedBox width="8"/>'+T(tasks[tid]['label'],18,"#334155",True)+'</Row>')
        p.append(T(f"{team} · {hhmm(s)}–{hhmm(e)} · {tasks[tid]['minutes']} min",18,"#64748B"))
        p.append(T(f"依赖：{deps}",18,"#8896AB"))
        p.append('</Column></Container>')
    p.append('</Row>')
p.append('</Column></Positioned>')
p.append('</Stack></Container></Snapshot>')
(OUT/'execution-board.snapshot').write_text('\n'.join(p),encoding='utf-8')
# decision brief
W,H=1200,1600
b=['<Snapshot background="#F6F7FB" type="png"><Container width="1200" height="1600"><Stack alignment="TOP_LEFT"><Container width="1200" height="1600" color="#F6F7FB"/>']
b.append('<Positioned left="48" top="44"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("LAYERLIGHT / RELEASE DECISION BRIEF",14,"#2563EB",True,' letterSpacing="2"')+T("发布决策简报",44,"#0B1220",True)+T("2026.11.07 · 09:00–16:00 · +08:00",22,"#56637A")+'</Column></Positioned>')
stats=[("总工作量",f"{work} min"),("计划完成",f"13:20 / 260 min"),("剩余缓冲",f"160 min"),("下界",f"255 min")]
for i,(lab,val) in enumerate(stats):
    x=48+i*277
    b.append(f'<Positioned left="{x}" top="176"><Container width="265" height="120" color="#FFFFFF" borderRadius="14" border="1 SOLID #E1E7F0" padding="18"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T(lab,18,"#64748B")+T(val,30,"#0B1220",True)+'</Column></Container></Positioned>')
b.append('<Positioned left="48" top="300">'+T("依赖概览 / CRITICAL PATH",18,"#2563EB",True,' letterSpacing="1.5"')+'</Positioned>')
chain=['R01','R04','R07','R09','R10','R12']
for i,tid in enumerate(chain):
    x=48+i*180
    b.append(f'<Positioned left="{x}" top="352"><Container width="160" height="54" color="#E0E7FF" borderRadius="8" alignment="CENTER">'+T(f"{tid} {tasks[tid]['minutes']}′",20,"#3730A3",True)+'</Container></Positioned>')
    if i<len(chain)-1: b.append(f'<Positioned left="{x+162}" top="372">'+T("→",20,"#94A3B8",True)+'</Positioned>')
b.append('<Positioned left="48" top="420">'+T("关键路径 255 min；计划完工 260 min，仅多 5 min；资源下界 242.5 min。未证明全局最优。",20,"#334155")+'</Positioned>')
# dependency table 2 cols x6
b.append('<Positioned left="48" top="470"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("12 任务与依赖 / TASKS AND DEPENDENCIES",18,"#2563EB",True,' letterSpacing="1.5"')+'<SizedBox height="10"/>')
for row in range(6):
    b.append('<Row crossAxisAlignment="START">')
    for col in range(2):
        tid=sorted(SCHED)[row*2+col]; team,s,e=SCHED[tid]; deps=", ".join(tasks[tid]['depends']) or "—"
        b.append(f'<Container width="540" height="92" color="#FFFFFF" borderRadius="10" border="1 SOLID #E1E7F0" padding="10" margin="(0,0,12,2)"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
        b.append('<Row crossAxisAlignment="CENTER">'+T(tid,20,"#0B1220",True)+'<SizedBox width="8"/>'+T(tasks[tid]['label'],22,"#334155",True)+'</Row>')
        b.append(T(f"{team} · {hhmm(s)}–{hhmm(e)} · {tasks[tid]['minutes']} min · 依赖 {deps}",20,"#64748B"))
        b.append('</Column></Container>')
    b.append('</Row>')
b.append('</Column></Positioned>')
# risks
b.append('<Positioned left="48" top="1096">'+T("三项风险与对策",18,"#2563EB",True,' letterSpacing="1.5"')+'</Positioned>')
for i,r in enumerate(data['risks']):
    y=1136+i*120
    b.append(f'<Positioned left="48" top="{y}"><Container width="1104" height="100" color="#FFFFFF" borderRadius="12" border="1 SOLID #E1E7F0" padding="14"><Column crossAxisAlignment="START" mainAxisSize="MIN"><Row crossAxisAlignment="CENTER">'+T(f"{r['id']} · {r['task']}",20,"#B45309",True)+'<SizedBox width="10"/>'+T(r['impact'],22,"#0B1220")+'</Row>'+T("对策："+r['mitigation'],20,"#475569")+'</Column></Container></Positioned>')
b.append('<Positioned left="48" top="1510">'+T("排程依据：同团队串行、依赖满足、固定时长；R09/R05/R12 选择团队以使完工尽早。缓冲用于返工/等待，不加入固定时长。",18,"#64748B")+'</Positioned>')
b.append('</Stack></Container></Snapshot>')
(OUT/'decision-brief.snapshot').write_text('\n'.join(b),encoding='utf-8')
# action card
W,H=720,1280
a=['<Snapshot background="#F4F6FA" type="png"><Container width="720" height="1280"><Stack alignment="TOP_LEFT"><Container width="720" height="1280" color="#F4F6FA"/>']
a.append('<Positioned left="32" top="24"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("LAYERLIGHT / LAUNCH DAY",13,"#2563EB",True,' letterSpacing="2"')+T("发布行动卡",30,"#0B1220",True)+T("09:00–16:00 · 按开始时间排序",20,"#56637A")+'</Column></Positioned>')
order=sorted(SCHED,key=lambda t:(SCHED[t][1],t))
riskmap={r['task']:r['id'] for r in data['risks']}
for i,tid in enumerate(order):
    team,s,e=SCHED[tid]; y=140+i*82
    a.append(f'<Positioned left="24" top="{y}"><Container width="672" height="74" color="#FFFFFF" borderRadius="10" border="1 SOLID #E1E7F0" padding="(8,12)"><Row crossAxisAlignment="CENTER"><Container width="92"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T(hhmm(s),20,"#0B1220",True)+T(hhmm(e),15,"#8896AB")+'</Column></Container>')
    a.append(f'<Container width="46"><Container width="34" height="34" color="{TCOL[team]}22" borderRadius="8" alignment="CENTER">'+T(tid,15,TCOL[team],True)+'</Container></Container>')
    a.append('<Expanded>'+T(tasks[tid]['label'],20,"#0B1220",False,' maxLines="1"')+'</Expanded>')
    a.append(f'<Container width="66" alignment="CENTER_RIGHT">'+T(team[:3].upper(),15,TCOL[team],True)+'</Container>')
    if tid in riskmap: a.append(f'<Container padding="(2,6)" color="#FEF3C7" borderRadius="6">'+T(riskmap[tid],14,"#92400E",True)+'</Container>')
    a.append('</Row></Container></Positioned>')
a.append('<Positioned left="32" top="1150"><Container width="656" height="100" color="#0B1220" borderRadius="10" padding="(12,16)"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("风险提醒：R02 服务限流 · R05 长文案 · R10 视觉回归；缓冲 160 分钟，不加入固定时长。",20,"#E2E8F0")+'</Column></Container></Positioned>')
a.append('</Stack></Container></Snapshot>')
(OUT/'action-card.snapshot').write_text('\n'.join(a),encoding='utf-8')
print('A24 written', 'conf',conf,'depbad',depbad,'cp',cp,'work',work)
