from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT/'tools')); import suitekit as s
RUN='20261124T113838+0800-aac601'; TASK='A09'
base=ROOT/'tasks/A09-transform-atlas/inputs'; stamp=json.loads((base/'stamp.json').read_text(encoding='utf-8')); transforms=json.loads((base/'transforms.json').read_text(encoding='utf-8'))
P=stamp['pivot']; assert P==[60,60]
def ident(): return [[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
def mul(A,B): return [[sum(A[i][k]*B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
def trans(x,y): A=ident(); A[0][3]=x; A[1][3]=y; return A
def opmat(op):
    A=ident(); name=op[0]; val=op[1]
    if name=='rotate_clockwise_deg':
        a=math.radians(val); c=round(math.cos(a),15); sn=round(math.sin(a),15); A[0][0]=c; A[0][1]=-sn; A[1][0]=sn; A[1][1]=c
    elif name=='mirror_horizontal': A[0][0]=-1
    elif name=='mirror_vertical': A[1][1]=-1
    elif name=='scale_uniform': A[0][0]=A[1][1]=val
    elif name=='scale_xy': A[0][0],A[1][1]=val
    else: raise ValueError(name)
    return mul(trans(P[0],P[1]),mul(A,trans(-P[0],-P[1])))
def apply(M,p): return [M[0][0]*p[0]+M[0][1]*p[1]+M[0][3],M[1][0]*p[0]+M[1][1]*p[1]+M[1][3]]
def cm(M): return [M[0][0],M[1][0],M[2][0],M[3][0],M[0][1],M[1][1],M[2][1],M[3][1],M[0][2],M[1][2],M[2][2],M[3][2],M[0][3],M[1][3],M[2][3],M[3][3]]
def bbox(points): return [min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]
def short(op):
    n,v=op
    if n=='rotate_clockwise_deg': return f'顺时针{v}°'
    if n=='mirror_horizontal': return '左右镜像'
    if n=='mirror_vertical': return '上下镜像'
    if n=='scale_uniform': return f'等比{v}'
    if n=='scale_xy': return f'缩放({v[0]},{v[1]})'
    raise ValueError(n)
centers=[[302+332*c,318+282*r] for r in range(3) for c in range(4)]
records=[]
for t,cxcy in zip(transforms,centers):
    M=ident()
    for op in t['operations']: M=mul(opmat(op),M)
    F=mul(trans(cxcy[0]-60,cxcy[1]-60),M)
    rectgeo=[]
    for i,r in enumerate(stamp['rectangles']):
        x,y,w,h=r['xywh']; src=[[x,y],[x+w,y],[x+w,y+h],[x,y+h]]; pts=[apply(F,p) for p in src]
        rectgeo.append({'rectangle_index':i,'source_xywh':r['xywh'],'source_corners_tl_tr_br_bl':src,'canvas_corners_tl_tr_br_bl':pts,'canvas_bbox':bbox(pts),'color':r['color']})
    dotc=apply(F,stamp['dot']['center']); rad=stamp['dot']['radius']; rx=rad*math.hypot(F[0][0],F[0][1]); ry=rad*math.hypot(F[1][0],F[1][1]); dotbox=[dotc[0]-rx,dotc[1]-ry,dotc[0]+rx,dotc[1]+ry]
    allpts=[p for r in rectgeo for p in r['canvas_corners_tl_tr_br_bl']]+[[dotbox[0],dotbox[1]],[dotbox[2],dotbox[3]]]
    records.append({'id':t['id'],'operations':t['operations'],'operation_short_names':[short(op) for op in t['operations']],'matrix_column_major_4x4':cm(F),'cell_center':cxcy,'rectangles':rectgeo,'dot':{'source_center':stamp['dot']['center'],'source_radius':rad,'canvas_center':dotc,'canvas_bbox':dotbox,'ellipse_radii':[rx,ry],'is_ellipse':abs(rx-ry)>1e-8},'canvas_outer_bbox':bbox(allpts)})
assert abs(records[6]['matrix_column_major_4x4'][1]-records[7]['matrix_column_major_4x4'][1])>1
out,temp=s.task_dirs(RUN,TASK)
audit={'schema_version':1,'task_id':TASK,'path_base':'output_dir','coordinate_system':{'source_origin':'stamp top-left','pivot':P,'x_direction':'right','y_direction':'down','rotation_positive':'clockwise in image coordinates','cell_size_px':[300,250],'gap_px':32,'grid_origin_px':[152,193],'cell_centers':centers,'mapping':'canvas = Translate(cell_center - pivot) × combined_local_operations × source_point','matrix_order':'column-major 4x4; operations multiplied on the left in input order, so the first listed operation acts first on a point.'},'transforms':[{k:r[k] for k in ['id','operations','operation_short_names','matrix_column_major_4x4','cell_center']} for r in records],'geometry':records,'verification':[]}
s.write_json(out/'geometry-audit.json',audit); s.write_json(temp/'predicted-geometry.json',audit)
# DSL
BG='#F2F4F0'; INK='#172B3A'; MUT='#61717B'; GUIDE='#D6DEDA'
ch=[s.box(0,0,1600,1200,BG),s.box(64,42,8,66,'#2364DB'),s.label('变换图谱 · 十二个非对称标本',88,34,1000,56,38,INK,True),s.label('每步围绕局部 (60,60)  /  最终主体统一使用 Transform.matrix  /  图像坐标顺时针',88,94,1200,34,22,MUT)]
for idx,(r,(cx,cy)) in enumerate(zip(records,centers)):
    col=idx%4; row=idx//4; left=152+332*col; top=193+282*row
    ch += [s.box(left,top,300,250,'#FFFFFF',16,'#D5DFDA')]
    # center crosshair and +/-60 ticks
    ch += [s.line(left+22,cy,left+278,cy,GUIDE,1),s.line(cx,top+58,cx,top+222,GUIDE,1)]
    for d in [-60,0,60]:
        ch += [s.line(cx+d-4,cy-4,cx+d+4,cy+4,'#9EADA7',1),s.line(cx+d,cy-8,cx+d,cy+8,'#9EADA7',1),s.line(cx-8,cy+d,cx+8,cy+d,'#9EADA7',1),s.line(cx-4,cy+d-4,cx+4,cy+d+4,'#9EADA7',1)]
    ch += [s.label(r['id'],left+18,top+14,80,32,22,INK,True),s.label(' → '.join(r['operation_short_names']),left+18,top+208,264,30,20,MUT,False,'CENTER')]
    # one full-canvas positioned transform per specimen; child source coordinates remain unchanged
    body=['<Stack clipBehavior="NONE">']
    for rect in stamp['rectangles']:
        x,y,w,h=rect['xywh']; body.append(s.positioned(x,y,w,h,f'<Container width="{w}" height="{h}" color="{rect["color"]}" />'))
    d=stamp['dot']; body.append(s.circle(d['center'][0],d['center'][1],d['radius'],d['color'])); body.append('</Stack>')
    vals=' '.join(f'{v:.12g}' for v in r['matrix_column_major_4x4'])
    ch.append(s.positioned(0,0,1600,1200,f'<Transform matrix="{vals}">\n'+'\n'.join(body)+'\n</Transform>'))
# legend outside grid
ch += [s.label('图例',152,1050,80,32,22,INK,True),s.box(244,1054,34,22,'#E54B4B'),s.label('红 / 蓝 / 黄：源矩形',288,1048,300,34,20,MUT),s.circle(650,1065,8,'#111111'),s.label('黑点：方向基准；非均匀缩放后为椭圆',670,1048,470,34,20,MUT),s.label('十字与刻度：局部中心 / ±60',1160,1048,360,34,20,MUT)]
dsl=s.snapshot(1600,1200,ch,BG)
img,rec=s.render(RUN,TASK,dsl,'transform-atlas','v001',False,'baseline'); print(img,rec['http_status'])
