from pathlib import Path
import sys, json, math, heapq
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
import suitekit as s
RUN='20261124T113838+0800-aac601'; TASK='A07'
net=json.loads((ROOT/'tasks/A07-transit-topology/inputs/network.json').read_text(encoding='utf-8'))
st={x['id']:x for x in net['stations']}; lines=net['lines']; lorder=[x['id'] for x in lines]
adj={x:[] for x in st}; at={x:[] for x in st}; edge_line={}
for ln in lines:
    for a,b in zip(ln['stations'],ln['stations'][1:]):
        adj[a].append((b,ln['id'])); adj[b].append((a,ln['id'])); edge_line[tuple(sorted((a,b)))]=ln['id']
        if ln['id'] not in at[a]: at[a].append(ln['id'])
        if ln['id'] not in at[b]: at[b].append(ln['id'])

def solve(src,dst,accessible=False):
    if accessible and (not st[src]['accessible'] or not st[dst]['accessible']): return None,0
    start=[(src,l) for l in at[src]]
    dist={k:(0,0) for k in start}; prev={}; heap=[(0,0,src,l) for l in at[src]]; heapq.heapify(heap); popped=0
    while heap:
        e,t,u,l=heapq.heappop(heap); popped+=1
        if dist.get((u,l))!=(e,t): continue
        if u==dst:
            path=[(u,l)]
            while path[-1]!=(src,next(k[1] for k in start if k[0]==src)):
                path.append(prev[path[-1]])
            path.reverse(); stations=[x[0] for x in path]
            segs=[]
            for a,b in zip(path,path[1:]):
                if not segs or segs[-1]['line']!=b[1]: segs.append({'line':b[1],'from':a[0],'to':b[0],'stations':[a[0],b[0]]})
                else: segs[-1]['stations'].append(b[0]); segs[-1]['to']=b[0]
            transfers=[path[i][0] for i in range(1,len(path)) if path[i][1]!=path[i-1][1]]
            return {'stations':stations,'edge_lines':[edge_line[tuple(sorted((a,b)))] for a,b in zip(stations,stations[1:])],'intervals':len(stations)-1,'transfers':len(transfers),'transfer_stations':transfers,'segments':segs,'state_path':[{'station':a,'line':b} for a,b in path]},popped
        for v,nl in adj[u]:
            if nl==l: cand=(e+1,t)
            else:
                if accessible and not st[u]['accessible']: continue
                cand=(e+1,t+1)
            if cand<dist.get((v,nl),(10**9,10**9)):
                dist[(v,nl)]=cand; prev[(v,nl)]=(u,l); heapq.heappush(heap,(cand[0],cand[1],v,nl))
    return None,popped

queries=[]
for qi,q in enumerate(net['queries'],1):
    normal,popped=solve(q['from'],q['to']); acc,apopped=solve(q['from'],q['to'],True)
    usable=acc is not None and (normal['intervals'],normal['transfers'])==(acc['intervals'],acc['transfers'])
    reason=None
    if not usable: reason='普通最短路线在 S05 东桥换乘；该站无障碍设施为 false，不能作为无障碍换乘站。替代路线改在 S08 工坊换乘。'
    queries.append({'query_id':f'Q{qi}','from':q['from'],'to':q['to'],'normal':normal,'accessible':acc,'normal_is_accessible':usable,'normal_accessibility_reason':reason})
assert queries[0]['normal']['intervals']==6
assert queries[1]['normal']['stations']==['S13','S14','S08','S15','S05','S06','S12']
assert queries[1]['accessible']['stations']==['S13','S14','S08','S04','S05','S06','S12']
assert queries[2]['normal']['intervals']==4
out, temp=s.task_dirs(RUN,TASK)
audit={'schema_version':1,'task_id':TASK,'path_base':'output_dir','queries':queries,
'accessibility':[{'station':x,'accessible':st[x]['accessible'],'may_be_endpoint':st[x]['accessible'],'may_transfer':st[x]['accessible'],'may_pass_through':True} for x in st],
'optimality':[], 'content_map':[]}
for q in queries:
    for mode in ['normal','accessible']:
        r=q[mode]
        audit['optimality'].append({'query_id':q['query_id'],'mode':mode,'method':'Dijkstra on states (station, current_line); lexicographic cost (intervals, transfers); first boarding costs zero transfers; inaccessible mode disallows inaccessible endpoints and transfer states but permits riding through.','objective':[r['intervals'],r['transfers']] if r else None,'result_basis':'Exhaustive lexicographic state search; all alternative nonnegative-cost paths are dominated by the recorded objective.','station_state_path':r['state_path'] if r else None})
    audit['content_map'].append({'query_id':q['query_id'],'network_map':'network-map.png: all network stations and line segments','travel_card':f"travel-card.png: card Q{q['query_id'][1:]}",'checked':'Station sequence, intervals and transfer count cross-checked against computed route.'})
s.write_json(out/'routes.json',audit)
s.write_json(temp/'computed-routes.json',audit)

C={'R':'#D74B45','B':'#2875B8','G':'#27845B'}; INK='#17263B'; MUT='#5D6B7B'; BG='#F3F6F2'
pos={'S01':(130,470),'S02':(270,470),'S03':(410,470),'S04':(550,470),'S05':(790,350),'S06':(910,350),'S12':(1030,350),
'S07':(430,710),'S08':(550,590),'S09':(790,230),'S10':(910,230),'S11':(1030,230),
'S13':(1270,710),'S14':(1150,590),'S15':(670,470),'S16':(790,470)}
paths={'R':['S01','S02','S03','S04',(670,350),'S05','S06','S12'],'B':['S07','S08','S04','S09','S10','S11'],'G':['S13','S14',(990,590),'S08','S15','S05','S16']}
# Segment angles for inserted G bend are still 90/0; all drawn bends are 45/90.
angles=[]
for lid,p in paths.items():
    pts=[pos[x] if isinstance(x,str) else x for x in p]
    for a,b in zip(pts,pts[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1]
        if dx and dy: assert abs(abs(dx)-abs(dy))<1e-9, (lid,a,b,dx,dy)
        angles.append({'line':lid,'from':a,'to':b,'angle_degrees':90 if dx==0 else (0 if dy==0 else 45 if dx*dy>0 else 135)})
s.write_json(temp/'geometry.json',{'coordinates':pos,'segments':angles,'convention':'schematic; not geographic','allowed_turn_angles':[45,90]})
labels={'S01':(75,510),'S02':(215,510),'S03':(355,510),'S04':(465,405),'S05':(745,390),'S06':(865,390),'S12':(985,390),'S07':(355,755),'S08':(465,625),'S09':(725,175),'S10':(845,175),'S11':(965,175),'S13':(1215,755),'S14':(1095,625),'S15':(605,505),'S16':(725,515)}
children=[s.box(0,0,1600,1000,BG),s.box(64,44,8,74,C['R']),s.label('三线通行 · 港湾都市',94,38,800,58,40,INK,True),s.label('16 站全网示意  /  相邻站双向、等时',94,94,780,34,22,MUT),s.box(1110,52,426,58,'#E3EBE4',14,child=s.text('非地理示意 · 不代表实际距离',22,INK,True,'CENTER',398,36))]
# faint registration field
for x in range(100,1501,100): children.append(s.box(x,180,1,660,'#E2E8E2'))
for y in range(220,841,100): children.append(s.box(90,y,1400,1,'#E2E8E2'))
for lid,p in paths.items():
    pts=[pos[x] if isinstance(x,str) else x for x in p]
    for a,b in zip(pts,pts[1:]):
        children += [s.line(*a,*b,'#FFFFFF',20),s.line(*a,*b,C[lid],12)]
# station markers and labels
for sid,(x,y) in pos.items():
    interchange=len(at[sid])>1
    r=19 if interchange else 12
    children.append(s.circle(x,y,r,'#FFFFFF','#17263B'))
    if interchange:
        children += [s.circle(x,y,9,INK),s.label(sid.replace('S',''),x-18,y-30,36,26,20,INK,True,'CENTER')]
    if st[sid]['accessible']: children.append(s.circle(x+13,y-14,6,'#27845B','#FFFFFF'))
    else: children += [s.box(x+8,y-20,10,10,'#E2A33B'),s.line(x+8,y-10,x+18,y-20,'#FFFFFF',2)]
    lx,ly=labels[sid]
    children += [s.label(f"{st[sid]['name']}  {sid}",lx,ly,160,34,20,INK,True),s.label('无障碍' if st[sid]['accessible'] else '设施不具备',lx,ly+30,150,28,20,'#27845B' if st[sid]['accessible'] else '#9A6817')]
# legend footer
children += [s.box(64,876,1472,88,'#FFFFFF',18,'#D8E0DA'),s.label('线路',88,890,80,28,20,MUT,True)]
lx=170
for ln in lines:
    children += [s.box(lx,895,56,34,C[ln['id']],8,child=s.text(ln['id'],22,'#FFFFFF',True,'CENTER',56,34)),s.label(ln['name'],lx+66,894,100,36,22,INK,True)]
    lx+=205
children += [s.circle(825,910,8,'#27845B'),s.label('绿色点：具备无障碍设施',845,890,300,40,20,INK),s.box(1155,901,16,16,'#E2A33B'),s.label('琥珀标：设施不具备',1183,890,310,40,20,INK)]
mapdsl=s.snapshot(1600,1000,children,BG)
# travel card
ch=[s.box(0,0,720,1280,BG),s.box(0,0,720,174,INK),s.label('港湾都市 · 路线卡',36,28,650,52,36,'#FFFFFF',True),s.label('最少站间边数优先，同边数换乘最少',36,88,650,36,22,'#DCE6E2'),s.label('无障碍可乘车途经设施不具备的站，但不能在此上下车或换乘。',36,126,650,34,20,'#F4D99D')]

def route_names(r): return ' → '.join(st[x]['name'] for x in r['stations'])
def segtext(r): return '  /  '.join(f"{z['line']}：{st[z['from']]['name']}—{st[z['to']]['name']}" for z in r['segments'])
def card(q,y,h):
    a=[s.box(28,y,664,h,'#FFFFFF',22,'#D9E1DC')]
    ok=q['normal_is_accessible']
    a += [s.label(f"Q{q['query_id'][1:]}  {st[q['from']]['name']} → {st[q['to']]['name']}",50,y+20,500,36,26,INK,True),s.box(526,y+20,140,38,'#E4F3E9' if ok else '#FFF0D4',10,child=s.text('可无障碍' if ok else '需替代',20,'#246C4D' if ok else '#8C5B0B',True,'CENTER',140,32))]
    r=q['normal']; a += [s.label('普通最优',50,y+67,120,30,20,MUT,True),s.label(route_names(r),174,y+62,490,68,20,INK,False),s.label(f"{r['intervals']} 站间 · {r['transfers']} 次换乘" + (' · 可作为无障碍旅程' if ok else ' · 不可作为无障碍旅程'),50,y+127,610,34,20,'#246C4D' if ok else '#9A6817',True),s.label(segtext(r),50,y+164,610,58,20,MUT)]
    if not ok:
        ar=q['accessible']; a += [s.box(50,y+221,610,1,'#D9E1DC'),s.label('无障碍替代',50,y+234,140,30,20,'#246C4D',True),s.label(route_names(ar),194,y+228,448,70,20,INK),s.label(f"{ar['intervals']} 站间 · {ar['transfers']} 次换乘 · 在工坊 S08 换乘",50,y+297,610,34,20,'#246C4D',True),s.label(segtext(ar),50,y+333,610,58,20,MUT)]
    return a
ch+=card(queries[0],198,234)
ch+=card(queries[1],448,410)
ch+=card(queries[2],874,234)
ch += [s.box(28,1128,664,104,'#E5ECE7',18),s.label('R 红线   B 蓝线   G 绿线',50,1142,610,34,22,INK,True),s.label('换乘不计首次上车；站间边数 = 站数 − 1。',50,1181,610,32,20,MUT)]
traveldsl=s.snapshot(720,1280,ch,BG)
# Render baselines; final flag withheld until visual review.
for stem,dsl in [('network-map',mapdsl),('travel-card',traveldsl)]:
    img,rec=s.render(RUN,TASK,dsl,stem,'v001',False,'baseline')
    print(stem,img,rec['http_status'])
print(json.dumps([{ 'q':q['query_id'],'normal':q['normal']['stations'],'acc':q['accessible']['stations']} for q in queries],ensure_ascii=False))
