#!/usr/bin/env python3
"""A20 label placement: side columns, straight leaders; compute constraints first."""
import json, math
from pathlib import Path
SUITE=Path(__file__).resolve().parents[4]
markers=json.loads((SUITE/'tasks/A20-dense-annotation/inputs/markers.json').read_text(encoding='utf-8'))
pts=[]
for m in markers:
    pts.append({**m,'px':280+10.4*m['x'],'py':920-7.6*m['y']})
pts_sorted=sorted(pts,key=lambda p:p['px'])
left=pts_sorted[:12]; right=pts_sorted[12:]
left.sort(key=lambda p:p['py']); right.sort(key=lambda p:p['py'])
LBOX=(48,40,180); RBOX=(1372,40,180)  # x,w,height
SLOT0=190; STEP=56
def seg_point_dist(a,b,p):
    ax,ay=a; bx,by=b; px,py=p
    dx,dy=bx-ax,by-ay
    if dx==dy==0: return math.hypot(px-ax,py-ay)
    t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy)))
    return math.hypot(px-(ax+t*dx),py-(ay+t*dy))
def seg_inter(a,b,c,d):
    def cr(o,p,q): return (p[0]-o[0])*(q[1]-o[1])-(p[1]-o[1])*(q[0]-o[0])
    d1,d2,d3,d4=cr(a,b,c),cr(a,b,d),cr(c,d,a),cr(c,d,b)
    if ((d1>0 and d2<0) or (d1<0 and d2>0)) and ((d3>0 and d4<0) or (d3<0 and d4>0)): return True
    return False
labels=[]
for side,group in [('L',left),('R',right)]:
    for i,p in enumerate(group):
        y=SLOT0+i*STEP
        if side=='L': box=[48,y,228,y+40]; end=(228,y+20); start=(p['px']-6,p['py'])
        else: box=[1372,y,1552,y+40]; end=(1372,y+20); start=(p['px']+6,p['py'])
        labels.append({'id':p['id'],'name':p['name'],'value':p['value'],'side':side,'slot':i,'box':box,
                       'start':start,'end':end,'anchor':[p['px'],p['py']]})
issues=[]
for i,l in enumerate(labels):
    for j,m in enumerate(labels):
        if i==j: continue
        b=m['box']
        # sample segment vs label rect
        for t in [k/20 for k in range(21)]:
            x=l['start'][0]+(l['end'][0]-l['start'][0])*t; y=l['start'][1]+(l['end'][1]-l['start'][1])*t
            if b[0]+2<x<b[2]-2 and b[1]+2<y<b[3]-2:
                issues.append(('line_in_label',l['id'],m['id'])); break
for l in labels:
    for p in pts:
        if p['id']==l['id']: continue
        if seg_point_dist(l['start'],l['end'],(p['px'],p['py']))<9:
            issues.append(('line_over_point',l['id'],p['id']))
cross=[]
for i in range(len(labels)):
    for j in range(i+1,len(labels)):
        if seg_inter(labels[i]['start'],labels[i]['end'],labels[j]['start'],labels[j]['end']):
            cross.append((labels[i]['id'],labels[j]['id']))
print('issues',len(issues),issues[:10])
print('crossings',len(cross),cross[:10])
print('left',[(l['id'],l['slot']) for l in labels if l['side']=='L'])
print('right',[(l['id'],l['slot']) for l in labels if l['side']=='R'])
for p in pts:
    if p['id'] in ('M06','M08','M09','M10','M11','M12'): print('center',p['id'],round(p['px'],1),round(p['py'],1))
