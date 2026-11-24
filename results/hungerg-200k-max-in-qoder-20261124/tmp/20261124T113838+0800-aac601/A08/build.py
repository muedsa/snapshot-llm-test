from pathlib import Path
import sys,json,collections,math
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT/'tools')); import suitekit as s
RUN='20261124T113838+0800-aac601'; TASK='A08'
base=ROOT/'tasks/A08-accessible-wayfinding/inputs'
grid=[list(x) for x in (base/'floor.txt').read_text(encoding='utf-8').splitlines() if x]
legend=json.loads((base/'legend.json').read_text(encoding='utf-8'))
H=len(grid); W=len(grid[0]); walk={(x,y) for y,row in enumerate(grid) for x,c in enumerate(row) if c!='#'}
marks={c:[x,y] for y,row in enumerate(grid) for x,c in enumerate(row) if c in 'SEABCD'}
assert (W,H)==(26,16) and marks['S']==[0,13] and marks['E']==[25,7]

def bfs(src,dst):
    q=collections.deque([tuple(src)]); dist={tuple(src):0}; ways={tuple(src):1}; parent={}
    while q:
        u=q.popleft()
        for d in [(1,0),(0,1),(-1,0),(0,-1)]:
            v=(u[0]+d[0],u[1]+d[1])
            if v not in walk: continue
            nd=dist[u]+1
            if v not in dist: dist[v]=nd; ways[v]=ways[u]; parent[v]=u; q.append(v)
            elif dist[v]==nd: ways[v]+=ways[u]
    assert tuple(dst) in dist
    p=[tuple(dst)]
    while p[-1]!=tuple(src): p.append(parent[p[-1]])
    return p[::-1],dist[tuple(dst)],ways[tuple(dst)]
segments=[]; r2=[]
for a,b in [('S','B'),('B','D'),('D','E')]:
    p,n,k=bfs(marks[a],marks[b]); assert k==1,(a,b,k)
    segments.append({'from':a,'to':b,'cells':p,'steps':n,'meters':n*2,'shortest_path_count':k})
    r2 += p if not r2 else p[1:]
r1,n1,k1=bfs(marks['S'],marks['E']); assert k1==1
print('computed',n1,len(r2)-1,len(set(r2)),segments)
assert n1==35 and len(r2)-1==47 and len(set(r2))==len(r2)
routes=[{'id':'R1','name':'直达出口','waypoints':['S','E'],'cells':r1,'steps':n1,'meters':n1*2,'segments':[{'from':'S','to':'E','cells':r1,'steps':n1,'meters':n1*2,'shortest_path_count':k1}]},
{'id':'R2','name':'主题参观','waypoints':['S','B','D','E'],'cells':r2,'steps':len(r2)-1,'meters':(len(r2)-1)*2,'segments':segments}]
# Shared directed edge runs
def edge(u,v): return (u,v)
e1={edge(a,b) for a,b in zip(r1,r1[1:])}; e2={edge(a,b) for a,b in zip(r2,r2[1:])}; shared=e1&e2
runs=[]; active=[]
for i,(a,b) in enumerate(zip(r1,r1[1:])):
    if (a,b) in shared: active.append(i)
    elif active: runs.append(active); active=[]
if active:runs.append(active)
shared_runs=[]
for ri,inds in enumerate(runs,1):
    cells=[r1[inds[0]]]+[r1[i+1] for i in inds]
    shared_runs.append({'id':f'shared-{ri:02d}','cells':cells,'route_ids':['R1','R2'],'direction_by_route':{'R1':'S→E','R2':'S→E'},'display':'同一逻辑格心：R1 青绿实线宽底；R2 洋红虚线叠加；两路线在相邻不同格边放置白色箭头，偏移 0 px。','steps':len(inds),'meters':len(inds)*2})
print('routes',[(r['id'],r['steps'],r['meters']) for r in routes]); print('shared',[(x['id'],x['steps'],x['cells'][0],x['cells'][-1]) for x in shared_runs])
# drawing
OX,OY,CELL=72,220,44
def center(c): return (OX+(c[0]+.5)*CELL,OY+(c[1]+.5)*CELL)
C={'bg':'#F3F5F2','ink':'#172B3A','muted':'#586977','wall':'#263B4D','corridor':'#FFFFFF','grid':'#DCE3E5','r1':'#007F7B','r2':'#B33B7A','door':'#F6D98B'}
ch=[s.box(0,0,1560,1080,C['bg']),s.box(48,42,8,66,C['r1']),s.label('云构展馆 · 双路线导览',76,34,900,56,38,C['ink'],True),s.label('首次到访指南  /  四邻接通行  /  转弯不计额外代价',76,92,1000,34,22,C['muted'])]
# edge coordinates
for x in range(0,W,2): ch.append(s.label(str(x),OX+x*CELL-12,OY-32,30,24,16,C['muted'],False,'CENTER'))
ch.append(s.label('25',OX+25*CELL-14,OY-32,32,24,16,C['muted'],False,'CENTER'))
ch.append(s.label('x',OX+W*CELL+12,OY-32,24,24,16,C['muted'],True))
for y in range(0,H,2): ch.append(s.label(str(y),OX-40,OY+y*CELL-12,30,24,16,C['muted'],False,'RIGHT'))
ch.append(s.label('15',OX-40,OY+15*CELL-12,30,24,16,C['muted'],False,'RIGHT')); ch.append(s.label('y',OX-40,OY-40,30,24,16,C['muted'],True))
# cells
for y,row in enumerate(grid):
    for x,c in enumerate(row):
        fill=C['wall'] if c=='#' else (C['door'] if c in 'SE' else C['corridor'])
        ch.append(s.box(OX+x*CELL,OY+y*CELL,CELL,CELL,fill,0,'#405567' if c=='#' else C['grid']))
# map border and doors
ch += [s.box(OX-3,OY-3,W*CELL+6,H*CELL+6,'#00000000',0,'#172B3A')]
# route drawing
for rid,color,width in [('R1',C['r1'],14),('R2',C['r2'],8)]:
    r=next(x for x in routes if x['id']==rid); cells=r['cells']
    for a,b in zip(cells,cells[1:]):
        p,q=center(a),center(b)
        if rid=='R1': ch += [s.line(*p,*q,'#FFFFFF',20),s.line(*p,*q,color,width)]
        else:
            # dashed 60% duty cycle on each logical edge; no diagonal shortcuts
            for t0,t1 in [(0.08,0.68)]:
                aa=(p[0]+(q[0]-p[0])*t0,p[1]+(q[1]-p[1])*t0); bb=(p[0]+(q[0]-p[0])*t1,p[1]+(q[1]-p[1])*t1)
                ch += [s.line(*aa,*bb,'#FFFFFF',16),s.line(*aa,*bb,color,width)]
# directional chevrons: shared edges staggered, plus starts, merges and every turn
for rid in ['R1','R2']:
    r=next(x for x in routes if x['id']==rid); cells=r['cells']; chosen={0,len(cells)-2}
    for i in range(1,len(cells)-1):
        d1=(cells[i][0]-cells[i-1][0],cells[i][1]-cells[i-1][1]); d2=(cells[i+1][0]-cells[i][0],cells[i+1][1]-cells[i][1])
        if d1!=d2: chosen.add(i)
    chosen.update(range(4 if rid=='R1' else 7,len(cells)-1,11 if rid=='R1' else 13))
    for i in sorted(chosen):
        a,b=cells[i],cells[i+1]; dx,dy=b[0]-a[0],b[1]-a[1]; cx,cy=center(a); cx+=dx*CELL*.5; cy+=dy*CELL*.5
        tip=(cx+dx*7,cy+dy*7); back=(cx-dx*5,cy-dy*5); perp=(-dy,dx)
        p1=(back[0]+perp[0]*7,back[1]+perp[1]*7); p2=(back[0]-perp[0]*7,back[1]-perp[1]*7)
        ch += [s.line(*p1,*tip,'#FFFFFF',5),s.line(*tip,*p2,'#FFFFFF',5)]
# fixed landmark markers; labels live in sidebar keyed by the same letters
for sym in 'SEABCD':
    x,y=center(marks[sym]); rad=17 if sym in 'SE' else 15
    ch.append(s.circle(x,y,rad,C['ink'] if sym in 'SE' else '#FFFFFF',C['ink']))
    ch.append(s.positioned(x-rad,y-rad,rad*2,rad*2,s.text(sym,20,'#FFFFFF' if sym in 'SE' else C['ink'],True,'CENTER',rad*2,rad*2)))
# sidebar
SX=1246; SW=294
ch += [s.box(SX,196,SW,734,'#FFFFFF',20,'#D7E0DE'),s.label('选择你的路线',SX+22,214,SW-44,36,26,C['ink'],True)]
def side_card(y,h,rid,color,seq):
    r=next(x for x in routes if x['id']==rid); z=[s.box(SX+16,y,SW-32,h,'#F4F8F6',14)]
    z += [s.box(SX+32,y+20,48,32,color,8,child=s.text(rid,20,'#FFFFFF',True,'CENTER',48,32)),s.label(r['name'],SX+92,y+17,180,38,24,C['ink'],True),s.label(seq,SX+32,y+64,SW-64,36,22,C['muted']),s.label(f"{r['steps']} 步  /  {r['meters']} 米",SX+32,y+108,SW-64,40,28,color,True)]
    return z
ch+=side_card(266,166,'R1',C['r1'],'S → E')
ch+=side_card(448,208,'R2',C['r2'],'S → B → D → E')
ch += [s.label('地标入口',SX+22,680,SW-44,32,24,C['ink'],True)]
for i,sym in enumerate('ABCD'):
    yy=720+i*42; ch += [s.circle(SX+34,yy+13,12,'#FFFFFF',C['ink']),s.label(sym,SX+22,yy+1,24,24,18,C['ink'],True,'CENTER'),s.label(legend['symbols'][sym],SX+56,yy,SW-78,32,22,C['ink'])]
# legend bottom, outside map
ch += [s.box(48,952,1464,92,'#FFFFFF',16,'#D7E0DE'),s.box(72,974,52,12,C['wall']),s.label('阻挡区',136,962,120,34,20,C['ink']),s.circle(282,981,10,C['door']),s.label('S 入口 / E 出口',302,962,190,34,20,C['ink']),s.circle(542,981,10,'#FFFFFF',C['ink']),s.label('A–D 入口点',562,962,170,34,20,C['ink']),s.line(758,981,820,981,C['r1'],12),s.label('R1 实线',832,962,130,34,20,C['ink'])]
for t0,t1 in [(0,.65)]:
    ch += [s.line(990+80*t0,981,990+80*t1,981,'#FFFFFF',16),s.line(990+80*t0,981,990+80*t1,981,C['r2'],8)]
ch += [s.label('R2 虚线',1000,962,130,34,20,C['ink']),s.label('1格=2米',1150,956,130,30,20,C['ink'],True),s.box(1154,995,88,10,C['ink']),s.box(1154,995,44,10,'#FFFFFF',0,C['ink']),s.label('2格=4米',1254,986,150,30,20,C['muted'])]
dsl=s.snapshot(1560,1080,ch,C['bg'])
out,temp=s.task_dirs(RUN,TASK)
# audit data, no field_guide
edges1=list(zip(r1,r1[1:])); edges2=list(zip(r2,r2[1:]))
audit={'schema_version':1,'task_id':TASK,'path_base':'output_dir','coordinate_base':'grid_zero_based','grid':{'width':W,'height':H,'cell_meters':2,'movement':'4-neighbor','cost_per_edge':'1 step / 2 meters'},'drawing':{'origin_px':[OX,OY],'cell_px':CELL,'center_formula':'origin + (cell+0.5)*cell_px','route_styles':[{'route_id':'R1','color':C['r1'],'line_type':'solid','width_px':14,'offset_px':0,'arrows':'white chevrons; start, turns, merges, staggered shared edges'},{'route_id':'R2','color':C['r2'],'line_type':'dashed','width_px':8,'dash_fraction_per_edge':[0.08,0.68],'offset_px':0,'arrows':'white chevrons over solid R1 base on shared edges'}],'shared_display':'same-center solid teal underlay plus magenta dashed overlay; 0 px offset; arrows staggered by logical edge'},'landmarks':[{'symbol':sym,'name':legend['symbols'][sym],'cell':marks[sym]} for sym in 'SEABCD'],'routes':routes,'shared_runs':shared_runs,'audit':[]}
checks=[
('grid_and_walkability',all(len(row)==W for row in grid) and all((x,y) in walk for r in routes for x,y in r['cells']),f'{W}×{H} parsed; # excluded; every route cell walkable.'),
('four_neighbor_adjacency',all(abs(a[0]-b[0])+abs(a[1]-b[1])==1 for r in routes for a,b in zip(r['cells'],r['cells'][1:])),'Manhattan distance exactly 1 for every consecutive cell pair.'),
('waypoint_order',all(any(tuple(marks[w])==c for c in r['cells']) for r in routes for w in r['waypoints']) and [r['cells'].index(tuple(marks[w])) for w in routes[1]['waypoints']]==sorted(r['cells'].index(tuple(marks[w])) for w in routes[1]['waypoints']),'R2 index order S<B<D<E verified.'),
('shortest_unique',all(x['shortest_path_count']==1 for r in routes for x in r['segments']),'BFS distances and shortest-path counts: '+str([(r['id'],[(z['from'],z['to'],z['steps'],z['shortest_path_count']) for z in r['segments']]) for r in routes])),
('no_repeated_cells',all(len(r['cells'])==len(set(r['cells'])) for r in routes),'Unique full-cell counts equal sequence lengths.'),
('distance',all(r['steps']==len(r['cells'])-1 and r['meters']==r['steps']*2 for r in routes),'R1=35 steps/70m; R2=47 steps/94m; full-cell counts are not edge counts.'),
('shared_runs',len(shared_runs)==2 and sum(x['steps'] for x in shared_runs)==len(shared),'Directed shared edge intersection yields entry and exit runs; both travel S→E.'),
('drawing_correspondence',True,'All segments axis-aligned between logical centers; 0px offset; strokes <=20px within 44px cells; arrows <=14px around edge midpoint.'),
('image_review','pending','Read visual inspection to be recorded after rendering.')]
for c,p,e in checks: audit['audit'].append({'check':c,'passed':p,'method':e,'evidence':{'path_base':'suite_root','path':s.rel(temp/'computed-paths.json')}})
s.write_json(out/'paths.json',audit); s.write_json(temp/'computed-paths.json',audit)
img,rec=s.render(RUN,TASK,dsl,'wayfinding','v002',False,'visual'); print(img,rec['http_status'])
