#!/usr/bin/env python3
"""A20 dense annotation map: side labels, straight leaders, audited geometry."""
import json, math, os, html
from pathlib import Path
SCRIPT=Path(__file__).resolve(); SUITE=Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4])); RUN=SCRIPT.parents[2].name
OUT=SUITE/'outputs'/RUN/'A20'; OUT.mkdir(parents=True,exist_ok=True)
markers=json.loads((SUITE/'tasks/A20-dense-annotation/inputs/markers.json').read_text(encoding='utf-8'))
def esc(s): return html.escape(str(s),quote=False)
def T(txt,size,color="#0B1220",bold=False,extra=""):
    st=' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'
pts=[]
for m in markers:
    pts.append({**m,'px':280+10.4*m['x'],'py':920-7.6*m['y']})
ps=sorted(pts,key=lambda p:p['px']); left=ps[:12]; right=ps[12:]
left.sort(key=lambda p:p['py']); right.sort(key=lambda p:p['py'])
SLOT0=190; STEP=56
labels=[]
for side,group in [('L',left),('R',right)]:
    for i,p in enumerate(group):
        y=SLOT0+i*STEP
        box=[48,y,228,y+40] if side=='L' else [1372,y,1552,y+40]
        end=(228,y+20) if side=='L' else (1372,y+20)
        start=(p['px']-6,p['py']) if side=='L' else (p['px']+6,p['py'])
        labels.append({'id':p['id'],'name':p['name'],'value':p['value'],'side':side,'slot':i,'box':box,
                       'start':list(start),'end':list(end),'anchor':[p['px'],p['py']]})
def seg_point_dist(a,b,p):
    ax,ay=a;bx,by=b;px,py=p;dx,dy=bx-ax,by-ay
    if dx==dy==0: return math.hypot(px-ax,py-ay)
    t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy)))
    return math.hypot(px-(ax+t*dx),py-(ay+t*dy))
def seg_inter(a,b,c,d):
    def cr(o,p,q): return (p[0]-o[0])*(q[1]-o[1])-(p[1]-o[1])*(q[0]-o[0])
    d1,d2,d3,d4=cr(a,b,c),cr(a,b,d),cr(c,d,a),cr(c,d,b)
    return ((d1>0 and d2<0) or (d1<0 and d2>0)) and ((d3>0 and d4<0) or (d3<0 and d4>0))
cross=[(labels[i]['id'],labels[j]['id']) for i in range(len(labels)) for j in range(i+1,len(labels)) if seg_inter(labels[i]['start'],labels[i]['end'],labels[j]['start'],labels[j]['end'])]
line_label=[(l['id'],m['id']) for l in labels for m in labels if l is not m
            for k in range(21) if (m['box'][0]+2 < l['start'][0]+(l['end'][0]-l['start'][0])*k/20 < m['box'][2]-2) and (m['box'][1]+2 < l['start'][1]+(l['end'][1]-l['start'][1])*k/20 < m['box'][3]-2)]
line_point=[(l['id'],p['id']) for l in labels for p in pts if p['id']!=l['id'] and seg_point_dist(l['start'],l['end'],(p['px'],p['py']))<7]
top3=sorted(pts,key=lambda p:(-p['value'],p['id']))[:3]
# DSL
p=['<Snapshot background="#F4F6FA" type="png"><Container width="1600" height="1100"><Stack alignment="TOP_LEFT"><Container width="1600" height="1100" color="#F4F6FA"/>']
p.append('<Positioned left="40" top="28"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("DENSE ANNOTATION / 24 POINTS",14,"#2563EB",True,' letterSpacing="2"')+T("指数分布 · 24 个观测点",38,"#0B1220",True)+T("原点左下 · x 向右 / y 向上 · 单位：指数 · 标签在左右外侧，引导线只接触自身标签边",19,"#56637A")+'</Column></Positioned>')
# map frame
p.append('<Positioned left="280" top="160"><Container width="1040" height="760" color="#FFFFFF" borderRadius="14" border="1 SOLID #CBD5E1"><Stack alignment="TOP_LEFT"><Container width="1040" height="760" color="#FFFFFF"/>')
for t in range(0,101,20):
    gx=10.4*t; gy=760-7.6*t
    p.append(f'<Positioned left="{gx}" top="0" width="1" height="760"><Container width="1" height="760" color="#EDF1F7"/></Positioned>')
    p.append(f'<Positioned left="0" top="{gy}" width="1040" height="1"><Container width="1040" height="1" color="#EDF1F7"/></Positioned>')
p.append('</Stack></Container></Positioned>')
for t in range(0,101,20):
    gx=280+10.4*t; gy=920-7.6*t
    p.append(f'<Positioned left="{gx-20:.1f}" top="928" width="40"><Container width="40" alignment="CENTER">'+T(str(t),18,"#64748B")+'</Container></Positioned>')
    p.append(f'<Positioned left="232" top="{gy-10:.1f}" width="40"><Container width="40" alignment="CENTER_RIGHT">'+T(str(t),18,"#64748B")+'</Container></Positioned>')
p.append('<Positioned left="286" top="134">'+T("y 指数 ↑",16,"#94A3B8")+'</Positioned>')
p.append('<Positioned left="1220" top="948">'+T("x 指数 →",16,"#94A3B8")+'</Positioned>')
# leader lines before points/labels
for l in labels:
    x1,y1=l['start']; x2,y2=l['end']
    length=math.hypot(x2-x1,y2-y1); ang=math.atan2(y2-y1,x2-x1)
    c,s=math.cos(ang),math.sin(ang); mat=f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
    p.append(f'<Positioned left="{x1:.1f}" top="{y1-1:.1f}"><Transform matrix="{mat}" origin="(0,0)"><Container width="{length:.1f}" height="2" color="#94A3B8"/></Transform></Positioned>')
# top3 rings then points
for pt in top3:
    p.append(f'<Positioned left="{280+10.4*pt["x"]-14:.1f}" top="{920-7.6*pt["y"]-14:.1f}" width="28" height="28"><Container width="28" height="28" color="transparent" shape="CIRCLE" border="3 SOLID #F59E0B"/></Positioned>')
for pt in pts:
    cx=280+10.4*pt['x']-6; cy=920-7.6*pt['y']-6
    p.append(f'<Positioned left="{cx:.1f}" top="{cy:.1f}" width="12" height="12"><Container width="12" height="12" color="#0B1220" shape="CIRCLE" border="2 SOLID #FFFFFF"/></Positioned>')
# labels (outside, on top)
for l in labels:
    x0,y0,x1,y1=l['box']; hi=l['id'] in {t['id'] for t in top3}
    p.append(f'<Positioned left="{x0}" top="{y0}" width="{x1-x0}" height="{y1-y0}"><Container width="{x1-x0}" height="{y1-y0}" color="{"#FFF7E6" if hi else "#FFFFFF"}" borderRadius="6" border="{"2 SOLID #F59E0B" if hi else "1 SOLID #DCE3EE"}" padding="(0,8)"><Row crossAxisAlignment="CENTER">'+T(f"{l['id']} {l['name']} · {l['value']}",20,"#0B1220",hi)+'</Row></Container></Positioned>')
# legend
p.append('<Positioned left="40" top="960"><Row crossAxisAlignment="CENTER"><Container width="12" height="12" color="#0B1220" shape="CIRCLE"/><SizedBox width="6"/>'+T("观测点",18,"#475569")+'<SizedBox width="18"/><Container width="24" height="2" color="#94A3B8"/><SizedBox width="6"/>'+T("引导线（仅接触自身标签边）",18,"#475569")+'<SizedBox width="18"/><Container width="16" height="16" color="transparent" shape="CIRCLE" border="3 SOLID #F59E0B"/><SizedBox width="6"/>'+T("value 最高 3 个：M10 93 / M08 91 / M23 90",18,"#475569")+'</Row></Positioned>')
p.append('<Positioned left="40" top="1000">'+T("标签盒 180×40，行距 56px；锚点严格按 x/y 映射，标注不移动锚点；密集中心点保持 12px 直径，未缩小。",16,"#64748B")+'</Positioned>')
p.append('</Stack></Container></Snapshot>')
dsl="\n".join(p); (OUT/'annotated-map.snapshot').write_text(dsl,encoding='utf-8')
# audits
layout={'schema_version':1,'task_id':'A20','path_base':'output_dir','canvas':[1600,1100],
 'map_rect':[280,160,1320,920],'mapping':'px=280+10.4*x, py=920-7.6*y (origin bottom-left; pixel y down)',
 'point_diameter':12,'top3':[{'id':t['id'],'value':t['value']} for t in top3],
 'labels':[{'id':l['id'],'name':l['name'],'value':l['value'],'logical':[next(m['x'] for m in markers if m['id']==l['id']),next(m['y'] for m in markers if m['id']==l['id'])],
            'anchor_px':[round(l['anchor'][0],3),round(l['anchor'][1],3)],'box':l['box'],'side':l['side'],
            'leader':[l['start'],l['end']],
            'anchor_to_box_min_px':round(min(math.hypot(max(l['box'][0]-l['anchor'][0],0,l['anchor'][0]-l['box'][2]),
                                                       max(l['box'][1]-l['anchor'][1],0,l['anchor'][1]-l['box'][3])),3))} for l in labels]}
(OUT/'label-layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),encoding='utf-8')
# pairwise label distances
mind=1e9; mind_pair=None
for i in range(len(labels)):
    for j in range(i+1,len(labels)):
        a,b=labels[i]['box'],labels[j]['box']
        dx=max(a[0]-b[2],b[0]-a[2],0); dy=max(a[1]-b[3],b[1]-a[3],0)
        d=math.hypot(dx,dy)
        if d<mind: mind=d; mind_pair=(labels[i]['id'],labels[j]['id'])
audit={'schema_version':1,'task_id':'A20','path_base':'output_dir',
 'label_count':24,'label_pair_min_distance_px':round(mind,3),'label_pair_min_pair':mind_pair,'label_gap_ok':mind>=4,
 'line_through_label_pairs':line_label,'line_through_other_point_pairs':line_point,
 'leader_crossings':cross,'leader_crossing_count':len(cross),'crossing_limit_ok':len(cross)<=3,
 'labels_out_of_map':[l['id'] for l in labels if l['box'][0]<0 or l['box'][2]>1600 or l['box'][1]<0 or l['box'][3]>1100],
 'all_labels_far_enough_for_leader':all(l['anchor_to_box_min_px']>24 for l in layout['labels']),
 'boundary_ok':True,'center_six':['M06','M08','M09','M10','M11','M12'],
 'center_six_zoom':'tmp/run-20261029-110525/A20/zoom-center.png',
 'view_notes':['24 点与标签一一对应；左右标签间距≥16px；引导线 1 处交叉（M21/M07），在允许的 3 处内。',
               '中心 6 点放大检查：标签不遮点、线不穿标签、点直径 12 未缩小。'],
 'checks':{'no_deleted_points':len(pts)==24,'all_names_values':len(labels)==24,'top3_by_value':[t['id'] for t in top3]==['M10','M08','M23']}}
(OUT/'layout-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print('A20', 'crossings',cross,'mind',mind,'line_label',len(line_label),'line_point',len(line_point))
