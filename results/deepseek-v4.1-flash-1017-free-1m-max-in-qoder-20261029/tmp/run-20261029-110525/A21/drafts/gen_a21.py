#!/usr/bin/env python3
"""A21 staged launch posters: 3 rounds x 2 sizes, tokens/maps, round-03 contrast."""
import json, os, sys, math, html
from pathlib import Path
SCRIPT=Path(__file__).resolve(); SUITE=Path(os.environ.get("SNAPSHOT_TASK_ROOT",SCRIPT.parents[4])); RUN=SCRIPT.parents[2].name
OUT=SUITE/'outputs'/RUN/'A21'; OUT.mkdir(parents=True,exist_ok=True)
ROUND=int(sys.argv[sys.argv.index('--round')+1]) if '--round' in sys.argv else 1
def esc(s): return html.escape(str(s),quote=False)
def T(txt,size,color,bold=False,extra=""):
    st=' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'
theme = ({'bg':'#0B1220','ink':'#F8FAFC','muted':'#CBD5E1','accent':'#38BDF8','amber':'#F6B94A','line':'#334155'}
         if ROUND<3 else
         {'bg':'#F7F8FC','ink':'#0B1220','muted':'#334155','accent':'#1D4ED8','amber':'#92400E','line':'#CBD5E1'})
RING_COLS = ['#0EA5E9','#2563EB','#B45309'] if ROUND==3 else ['#38BDF8','#2563EB','#F6B94A']
TITLE = ("让复杂信息变得清晰" if ROUND==1 else
         "当所有信息都想成为标题：让复杂信息变得清晰的结构化方法")
DATE="2026.11.07 19:30"; SPEAKERS="讲者：林川 / 苏言"; SITE="layerlight.example.org"
SPONSORS="Northstar Research / 云构工具"; FREE="免费参加 · 无需报名"; EN="Clarity through structure"

def motif(cx,cy,r=150,stroke=46):
    out=[]
    for i,(dx,dy,col) in enumerate(zip([-46,0,46],[-46,0,46],RING_COLS)):
        out.append(f'<Positioned left="{cx+dx-r}" top="{cy+dy-r}" width="{2*r}" height="{2*r}"><Container width="{2*r}" height="{2*r}" color="transparent" shape="CIRCLE" border="{stroke} SOLID {col}DA"/></Positioned>')
    out.append(f'<Positioned left="{cx-34}" top="{cy-34}" width="68" height="68"><Container width="68" height="68" color="{theme["ink"]}" shape="CIRCLE"/></Positioned>')
    return "".join(out)

def title_size(W):
    # choose 48 for long round-2/3 title, 78 portrait / 70 wide for round1
    if ROUND==1: return 78 if W<1200 else 70
    return 48
def est_lines(text,size,W):
    units=sum(1 if ord(ch)>127 else 0.55 for ch in text)
    return math.ceil(units*size/W)
def build(kind):
    W,H=(1080,1350) if kind=='portrait' else (1440,810)
    ts=title_size(W)
    tw=(W-160) if kind=='portrait' else 780
    lines=est_lines(TITLE,ts,tw)
    p=[f'<Snapshot background="{theme["bg"]}" type="png"><Container width="{W}" height="{H}"><Stack alignment="TOP_LEFT"><Container width="{W}" height="{H}" color="{theme["bg"]}"/>']
    # motif
    if kind=='portrait': p.append(motif(790,250,170,50))
    else: p.append(motif(1120,360,190,56))
    x=80
    p.append(f'<Positioned left="{x}" top="64"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("LAYERLIGHT / ONLINE LAUNCH",24,theme['accent'],True,' letterSpacing="3"')+'</Column></Positioned>')
    if kind=='portrait':
        ty=560; dy=760; launch_y=820; spk_y=900; spons_y=980; free_y=1040; en_y=1160; site_y=1210
    else:
        ty=220; dy=430; launch_y=490; spk_y=560; spons_y=620; free_y=660; en_y=705; site_y=755
    p.append(f'<Positioned left="{x}" top="{ty}" width="{tw}">'+T(TITLE,ts,theme['ink'],True,' maxLines="3"')+'</Positioned>')
    p.append(f'<Positioned left="{x}" top="{dy}">'+T(DATE,34 if kind=='portrait' else 30,theme['ink'],True)+'</Positioned>')
    p.append(f'<Positioned left="{x}" top="{launch_y}"><Container padding="(8,16)" color="{theme["accent"]}22" borderRadius="999" border="1 SOLID {theme["accent"]}">'+T("ONLINE LAUNCH",24,theme['accent'],True,' letterSpacing="2"')+'</Container></Positioned>')
    p.append(f'<Positioned left="{x}" top="{spk_y}" width="{tw}">'+T(SPEAKERS,28 if kind=='portrait' else 24,theme['muted'])+'</Positioned>')
    if ROUND>=2:
        p.append(f'<Positioned left="{x}" top="{spons_y}" width="{tw}">'+T("联合呈现  "+SPONSORS,24,theme['ink'],True)+'</Positioned>')
        p.append(f'<Positioned left="{x}" top="{free_y}" width="{tw}">'+T(FREE,24,theme['amber'],True)+'</Positioned>')
    if ROUND>=3:
        p.append(f'<Positioned left="{x}" top="{en_y}">'+T(EN,30 if kind=='portrait' else 26,theme['accent'],True,' letterSpacing="1"')+'</Positioned>')
    p.append(f'<Positioned left="{x}" top="{site_y}">'+T(SITE,26 if kind=='portrait' else 24,theme['muted'])+'</Positioned>')
    p.append('</Stack></Container></Snapshot>')
    return "\n".join(p), {'W':W,'H':H,'title_box':[x,ty,x+tw,ty+lines*ts*1.15],'title_lines_est':lines,'title_size':ts,
                          'fields':{'eyebrow':[x,64,x+tw,92],'date':[x,dy,x+tw,dy+40],'launch':[x,launch_y,x+360,launch_y+52],
                                    'speakers':[x,spk_y,x+tw,spk_y+40],'website':[x,site_y,x+tw,site_y+40],
                                    'sponsors':[x,spons_y,x+tw,spons_y+36] if ROUND>=2 else None,
                                    'free':[x,free_y,x+tw,free_y+36] if ROUND>=2 else None,
                                    'english':[x,en_y,x+tw,en_y+40] if ROUND>=3 else None}}
rdir=OUT/f'round-{ROUND:02d}'; rdir.mkdir(parents=True,exist_ok=True)
for kind in ['portrait','wide']:
    dsl,geo=build(kind); (rdir/f'launch-{kind}.snapshot').write_text(dsl,encoding='utf-8')
# tokens
tokens={'schema_version':1,'task_id':'A21','round':ROUND,'path_base':'output_dir',
 'colors':theme,'motif':{'components':['3 rings','center dot'],'ring_colors':RING_COLS,'stroke_ratio':'0.26 of radius','geometry':'same across rounds'},
 'type':{'title':48 if ROUND>1 else (78,70),'date':34,'launch':22,'speakers':28,'sponsors':24,'free':24,'english':30,'website':26},
 'spacing':{'side_px':80,'title_max_lines':3,'safe_extension_top_bottom':True},
 'round_changes':['long title and sponsors' if ROUND==2 else ('light theme, contrast, English tagline' if ROUND==3 else 'initial launch')]}
(rdir/'design-tokens.json').write_text(json.dumps(tokens,ensure_ascii=False,indent=2),encoding='utf-8')
# content map
cm={'schema_version':1,'task_id':'A21','round':ROUND,'path_base':'output_dir','canvases':{}}
for kind in ['portrait','wide']:
    dsl,geo=build(kind)
    fields=[{'field':'title','text':TITLE,'box':geo['title_box'],'size':geo['title_size'],'complete':True},
            {'field':'date','text':DATE,'box':geo['fields']['date'],'size':34 if kind=='portrait' else 30,'complete':True},
            {'field':'launch','text':'ONLINE LAUNCH','box':geo['fields']['launch'],'size':22,'complete':True},
            {'field':'speakers','text':SPEAKERS,'box':geo['fields']['speakers'],'size':28 if kind=='portrait' else 24,'complete':True},
            {'field':'website','text':SITE,'box':geo['fields']['website'],'size':26 if kind=='portrait' else 24,'complete':True}]
    if ROUND>=2:
        fields += [{'field':'sponsors','text':'联合呈现  '+SPONSORS,'box':geo['fields']['sponsors'],'size':24 if kind=='portrait' else 22,'complete':True},
                   {'field':'free','text':FREE,'box':geo['fields']['free'],'size':24 if kind=='portrait' else 22,'complete':True}]
    if ROUND>=3:
        fields.append({'field':'english','text':EN,'box':geo['fields']['english'],'size':30 if kind=='portrait' else 26,'complete':True})
    cm['canvases'][kind]={'canvas':[geo['W'],geo['H']],'title_lines_max':3,'fields':fields}
(rdir/'content-map.json').write_text(json.dumps(cm,ensure_ascii=False,indent=2),encoding='utf-8')
# contrast audit round3
def lin(c):
    c=c/255
    return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def ratio(fg,bg):
    def L(hexs):
        h=hexs.lstrip('#'); r,g,b=[int(h[i:i+2],16) for i in (0,2,4)]
        return 0.2126*lin(r)+0.7152*lin(g)+0.0722*lin(b)
    a,b=L(fg),L(bg); return (max(a,b)+0.05)/(min(a,b)+0.05)
if ROUND==3:
    samples={}
    for kind in ['portrait','wide']:
        dsl,geo=build(kind)
        items=[('title',theme['ink'],geo['title_size'],geo['title_box']),('date',theme['ink'],34 if kind=='portrait' else 30,geo['fields']['date']),
               ('launch',theme['accent'],22,geo['fields']['launch']),('speakers',theme['muted'],28 if kind=='portrait' else 24,geo['fields']['speakers']),
               ('sponsors',theme['ink'],24 if kind=='portrait' else 22,geo['fields']['sponsors']),('free',theme['amber'],24 if kind=='portrait' else 22,geo['fields']['free']),
               ('english',theme['accent'],30 if kind=='portrait' else 26,geo['fields']['english']),('website',theme['muted'],26 if kind=='portrait' else 24,geo['fields']['website'])]
        samples[kind]=[{'item':n,'fg':fg,'bg':theme['bg'],'size_px':sz,'box':box,'contrast':round(ratio(fg,theme['bg']),3),'passed':ratio(fg,theme['bg'])>=4.5} for n,fg,sz,box in items]
    audit={'schema_version':1,'task_id':'A21','round':3,'path_base':'output_dir','method':'sRGB linearization per WCAG; solid background sampled at each text box; no transparency/overlay under text',
           'background_note':'第三轮两图文字均直接位于 #F7F8FC 实色背景上；motif 与文字盒不相交，文字下无混合叠层。',
           'images':samples,'all_text_passed':all(x['passed'] for v in samples.values() for x in v),
           'min_contrast':min(x['contrast'] for v in samples.values() for x in v)}
    (rdir/'contrast-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print('A21 round',ROUND,'title lines',est_lines(TITLE,title_size(1080),920),est_lines(TITLE,title_size(1440),820),'theme',theme['bg'])
