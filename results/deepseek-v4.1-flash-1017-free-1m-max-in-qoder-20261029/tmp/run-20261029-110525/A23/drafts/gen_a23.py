#!/usr/bin/env python3
"""A23 capability delivery: cover + 6 transparent keyframes + timing/frame data."""
import json, os, math, html
from pathlib import Path
SCRIPT=Path(__file__).resolve(); SUITE=Path(os.environ.get("SNAPSHOT_TASK_ROOT",SCRIPT.parents[4])); RUN=SCRIPT.parents[2].name
OUT=SUITE/'outputs'/RUN/'A23'; OUT.mkdir(parents=True,exist_ok=True)
def esc(s): return html.escape(str(s),quote=False)
def T(txt,size,color="#0B1220",bold=False,extra=""):
    st=' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'
COL={'B':'#2563EB','O':'#F59E0B','G':'#10B981','P':'#8B5CF6'}
units=[]
for i in range(12):
    color=list(COL)[i%4]; shape=['circle','square','ring'][i//4]; size=46 if shape!='ring' else 50
    units.append({'id':f'U{i+1:02d}','color':color,'shape':shape,'w':size,'h':size,'alpha':1.0,
                  'rot0':[0,30,60][i%3]})
final=[(270,220),(330,220),(210,320),(270,320),(330,320),(390,320),(150,420),(210,420),(270,420),(330,420),(390,420),(450,420)]
CX,CY=300,320
SCALE=1.75
disp=[(CX+(fx-CX)*SCALE, CY+(fy-CY)*SCALE) for fx,fy in final]
FRAMES=[]
for f in range(6):
    t=f/5
    e=t*t*(3-2*t)  # smoothstep
    out=[]
    for i,u in enumerate(units):
        x=disp[i][0]+(final[i][0]-disp[i][0])*e
        y=disp[i][1]+(final[i][1]-disp[i][1])*e
        rot=u['rot0']*(1-e)
        out.append({'id':u['id'],'x':round(x,3),'y':round(y,3),'rotation':round(rot,3),
                    'w':u['w'],'h':u['h'],'color':u['color'],'shape':u['shape'],'alpha':u['alpha']})
    FRAMES.append(out)
def shape_dsl(u,x,y,rot):
    w,h=u['w'],u['h']; c=COL[u['color']]
    if u['shape']=='circle':
        base=f'<Container width="{w}" height="{h}" color="{c}" shape="CIRCLE"/>'
    elif u['shape']=='square':
        base=f'<Container width="{w}" height="{h}" color="{c}"/>'
    else:
        base=f'<Container width="{w}" height="{h}" color="transparent" shape="CIRCLE" border="12 SOLID {c}"/>'
    c_,s_=math.cos(math.radians(rot)),math.sin(math.radians(rot))
    mat=f"({c_:.6f},{s_:.6f},0,0,{-s_:.6f},{c_:.6f},0,0,0,0,1,0,0,0,0,1)"
    return f'<Positioned left="{x-w/2:.2f}" top="{y-h/2:.2f}" width="{w}" height="{h}"><Transform matrix="{mat}" origin="({w/2},{h/2})">{base}</Transform></Positioned>'
for fi,fr in enumerate(FRAMES,1):
    p=['<Snapshot background="transparent" type="png"><Container width="600" height="600"><Stack alignment="TOP_LEFT"><Container width="600" height="600" color="transparent"/>']
    for u in fr:
        p.append(shape_dsl(u,u['x'],u['y'],u['rotation']))
    p.append('</Stack></Container></Snapshot>')
    (OUT/f'frame-{fi:02d}.snapshot').write_text('\n'.join(p),encoding='utf-8')
# cover
p=['<Snapshot background="#0B1220" type="png"><Container width="1200" height="800"><Stack alignment="TOP_LEFT"><Container width="1200" height="800" color="#0B1220"/>']
p.append('<Positioned left="-160" top="-200" width="700" height="700"><Container width="700" height="700" gradientType="RADIAL" gradientColors="#1D4ED84D,#0B122000" gradientCenter="CENTER" gradientRadius="0.5" borderRadius="999"/></Positioned>')
p.append('<Positioned left="60" top="60"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("LAYERLIGHT / MOTION STUDY",18,"#38BDF8",True,' letterSpacing="2"')+T("从结构到画面",64,"#F8FAFC",True)+T("12 个几何单元 · 6 帧 · 250 ms/帧 · 循环 1500 ms",24,"#CBD5E1")+'</Column></Positioned>')
# final composition on cover, scaled/shifted into right panel
for i,u in enumerate(FRAMES[-1]):
    x=final[i][0]*1.35+380; y=final[i][1]*1.35+120
    p.append(shape_dsl(u,x,y,0))
p.append('<Positioned left="60" bottom="54">'+T("叠光 · Layerlight · 结构汇聚成图像",20,"#94A3B8")+'</Positioned>')
p.append('</Stack></Container></Snapshot>')
(OUT/'cover.snapshot').write_text('\n'.join(p),encoding='utf-8')
# frame data
fd={'schema_version':1,'task_id':'A23','path_base':'output_dir','canvas':[600,600],
 'units':[{k:u[k] for k in ('id','shape','w','h','color','alpha')} for u in units],
 'frames':[],'interpolation':{'position':'smoothstep e=3t²-2t³ between dispersed (t=0) and final (t=1)','rotation':'linear from rot0 to 0, same e for position','rendered_intermediate':False},
 'seam':{}}
for fi,fr in enumerate(FRAMES,1):
    prev=FRAMES[fi-2] if fi>1 else None
    rec={'index':fi,'t_ms':(fi-1)*250,'png':f'frame-{fi:02d}.png','dsl':f'frame-{fi:02d}.snapshot','units':fr,'deltas':[]}
    if prev:
        for a,b in zip(prev,fr):
            rec['deltas'].append({'id':a['id'],'dx':round(b['x']-a['x'],3),'dy':round(b['y']-a['y'],3),'dpos':round(math.hypot(b['x']-a['x'],b['y']-a['y']),3),'drot':round(b['rotation']-a['rotation'],3)})
    fd['frames'].append(rec)
seam=[]
for a,b in zip(FRAMES[-1],FRAMES[0]):
    d=math.hypot(b['x']-a['x'],b['y']-a['y']); seam.append({'id':a['id'],'dpos':round(d,3),'drot':round(b['rotation']-a['rotation'],3)})
fd['seam']={'from_frame':6,'to_frame':1,'deltas':seam,'max_dpos':max(s['dpos'] for s in seam),'note':'末帧到首帧为跳变；循环播放会在接缝处跳回分散构图，非无缝。'}
(OUT/'frame-data.json').write_text(json.dumps(fd,ensure_ascii=False,indent=2),encoding='utf-8')
timing={'schema_version':1,'task_id':'A23','path_base':'output_dir','frames':[{'index':i+1,'t_ms':i*250,'duration_ms':250,'file':f'frame-{i+1:02d}.png'} for i in range(6)],
        'loop_period_ms':1500,'playback':'6 frames at 250ms each, loop','seam':'frame-6 → frame-1 jump; see frame-data.seam and limitations.md','seamless':False}
(OUT/'timing.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'limitations.md').write_text("""# 格式边界与替代交付

| 客户请求 | 实际支持 | 依据 | 本次替代 | 仍需外部工作 |
|---|---|---|---|---|
| 文字可编辑 SVG | Snapshot 只输出位图（png/jpg/webp），无 SVG 导出/文字对象 | open-snapshot ai-guide / parser-tags `Snapshot.type` | 1200×800 RGB PNG 封面 + 完整 DSL | 用设计工具或 SVG 生成器重排文字为可编辑对象 |
| CMYK 印刷稿 | 只支持 sRGB 光栅输出，无 CMYK 色彩空间/ICC 参数 | 同上；服务未提供色彩空间参数 | RGB PNG 封面 | 印前转换与打样 |
| 6 帧透明 GIF | 服务只出静态图片，无动画编码/帧时间 | 同上 | 6 张 600×600 透明 PNG + timing.json | 用 GIF 编码器按 timing 合成 |
| PNG 封面 | 原生支持 png | 同上 | cover.png | 无 |

未编造动画、SVG 路径或 CMYK 参数；`type` 只声明 png。帧间轨迹用 frame-data.json 表达，未渲染中间帧。末帧到首帧为跳变，timing.json 与 frame-data.seam 已明确标注，不宣称无缝。
""",encoding='utf-8')
print('A23 written; max seam',fd['seam']['max_dpos'])
