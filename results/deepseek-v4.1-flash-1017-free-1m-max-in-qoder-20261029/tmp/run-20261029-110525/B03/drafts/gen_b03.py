#!/usr/bin/env python3
"""B03 ten creative-frontier pieces, each technique serving a real scenario."""
import math, os, html
from pathlib import Path
SCRIPT=Path(__file__).resolve(); SUITE=Path(os.environ.get("SNAPSHOT_TASK_ROOT",SCRIPT.parents[4])); RUN=SCRIPT.parents[2].name
OUT=SUITE/'outputs'/RUN/'B03'; OUT.mkdir(parents=True,exist_ok=True)
def esc(s): return html.escape(str(s),quote=False)
def T(txt,size,color,bold=False,extra="",fam="Noto Sans CJK SC"):
    st=' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="{fam}" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'
def rect(x,y,w,h,color,r=0,border=None):
    b=f' border="{border}"' if border else ""
    return f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Container width="{w}" height="{h}" color="{color}" borderRadius="{r}"{b}/></Positioned>'
def seg(x1,y1,x2,y2,color,w=3):
    L=math.hypot(x2-x1,y2-y1); a=math.atan2(y2-y1,x2-x1); c,s=math.cos(a),math.sin(a)
    mat=f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
    return f'<Positioned left="{x1:.1f}" top="{y1-w/2:.1f}"><Transform matrix="{mat}" origin="(0,0)"><Container width="{L:.1f}" height="{w}" color="{color}" borderRadius="{w/2}"/></Transform></Positioned>'
def matrot(deg,scale=1.0,tx=0,ty=0):
    a=math.radians(deg); c,s=math.cos(a)*scale,math.sin(a)*scale
    return f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,{tx},{ty},0,1)"
def page(W,H,bg,body):
    return f'<Snapshot background="{bg}" type="png"><Container width="{W}" height="{H}"><Stack alignment="TOP_LEFT"><Container width="{W}" height="{H}" color="{bg}"/>{body}</Stack></Container></Snapshot>'
cases=[]
# 1 afterglow concert
W,H=1080,1350; bg="#0B0B10"; b=[]
for i in range(9):
    r=180+i*42
    b.append(f'<Positioned left="{540-r}" top="{520-r}" width="{2*r}" height="{2*r}"><Container width="{2*r}" height="{2*r}" color="transparent" shape="CIRCLE" border="{2 if i%2 else 1} SOLID #F59E0B{ "AA" if i%2 else "55"}"/></Positioned>')
b.append('<Positioned left="80" top="70">'+T("AFTERGLOW / LIVE",16,"#F59E0B",True,' letterSpacing="3"')+'</Positioned>')
b.append('<Positioned left="80" top="150" width="920">'+T("Afterglow",96,"#FFF7ED",True)+'</Positioned>')
b.append('<Positioned left="80" top="300" width="920">'+T("一场关于余辉、回声与夜行的现场。",28,"#FDE68A")+'</Positioned>')
b.append('<Positioned left="80" top="1050">'+T("2026.11.21 · 20:00",28,"#FFFFFF",True)+'</Positioned>')
b.append('<Positioned left="80" top="1100">'+T("云构 Livehouse · 站席 · ¥180",20,"#A1A1AA")+'</Positioned>')
cases.append(dict(id=1,slug="afterglow",W=W,H=H,bg=bg,title="Afterglow 演出海报",desc="九层同心圆用边框/透明度叠出余辉，不靠图片。",body="".join(b)))
# 2 tide atlas book cover
W,H=1080,1350; bg="#062A3A"; b=[]
for k in range(18):
    pts=[]
    for i in range(0,101):
        t=i/100; x=60+t*960; y=500+math.sin(t*2*math.pi*1.5+k*0.35)*70+k*9
        pts.append((x,y))
    for i in range(len(pts)-1): b.append(seg(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],"#38BDF8" if k%3==0 else "#0E7490",1 if k%3 else 2))
b.append('<Positioned left="60" top="60">'+T("TIDE ATLAS / 潮汐图集",15,"#7DD3FC",True,' letterSpacing="2"')+'</Positioned>')
b.append('<Positioned left="60" top="130" width="960">'+T("Tide Atlas",80,"#ECFEFF",True)+'</Positioned>')
b.append('<Positioned left="60" top="240">'+T("海岸线、月相与 24 小时的呼吸",24,"#BAE6FD")+'</Positioned>')
b.append('<Positioned left="60" top="1160">'+T("FIELD NOTES  /  2026",18,"#7DD3FC",True)+'</Positioned>')
b.append('<Positioned left="60" top="1200">'+T("18 条潮位曲线 · 一座虚构海岸",18,"#94A3B8")+'</Positioned>')
cases.append(dict(id=2,slug="tide-atlas",W=W,H=H,bg=bg,title="Tide Atlas 书封",desc="18 条参数化正弦线叠成海岸的“呼吸”。",body="".join(b)))
# 3 signal report cover
W,H=1080,1350; bg="#F2EEE6"; b=[]
for i in range(14):
    x=60+i*70; y=200+(i%5)*120; b.append(rect(x,y,140,240,"#1D4ED8" if i%3==0 else ("#F59E0B" if i%3==1 else "#0F766E"),0).replace('color="','color="').replace('"/>','" />'))
# add opacity via colors
b=[]
for i in range(14):
    x=60+i*70; y=180+(i%5)*130
    c=["#1D4ED866","#F59E0B66","#0F766E66"][i%3]
    b.append(rect(x,y,150,260,c))
b.append('<Positioned left="60" top="70">'+T("SIGNAL / 2026 RESEARCH",15,"#1D4ED8",True,' letterSpacing="3"')+'</Positioned>')
b.append('<Positioned left="60" top="900" width="960">'+T("噪音里的信号",72,"#0B1220",True)+'</Positioned>')
b.append('<Positioned left="60" top="990" width="860">'+T("一份关于信息过载的年度研究：14 个重叠图层，哪些仍然可读？",24,"#334155")+'</Positioned>')
b.append('<Positioned left="60" top="1090">'+T("RESEARCH REPORT · 128 PAGES",18,"#1D4ED8",True)+'</Positioned>')
cases.append(dict(id=3,slug="signal",W=W,H=H,bg=bg,title="Signal 研究报告封面",desc="14 层半透明矩形叠出“噪音”，标题落在干净区域。",body="".join(b)))
# 4 cut-here ticket (ClipPath)
W,H=1200,800; bg="#F4EFE6"; b=[]
path="M0 0 H1200 V300 Q1160 340 1200 380 V800 H0 V380 Q40 340 0 300 Z"
b.append(f'<Positioned left="0" top="0" width="1200" height="800"><ClipPath path="{path}" viewBox="0 0 1200 800" fit="FILL"><Container width="1200" height="800" color="#7C2D12"/></ClipPath></Positioned>')
b.append('<Positioned left="80" top="60">'+T("ZINE FAIR / 入场券",18,"#FED7AA",True,' letterSpacing="3"')+'</Positioned>')
b.append('<Positioned left="80" top="160" width="1040">'+T("把纸折成入口",52,"#FFF7ED",True)+'</Positioned>')
b.append('<Positioned left="80" top="270">'+T("2026.11.08 · 11:00–18:00 · 云构仓库",24,"#FED7AA")+'</Positioned>')
b.append('<Positioned left="80" top="560">'+T("NO. 042",40,"#FFF7ED",True)+'</Positioned>')
b.append('<Positioned left="80" top="620">'+T("一券一人 · 可折 · 不可复制",18,"#FED7AA")+'</Positioned>')
b.append('<Positioned right="80" top="560">'+T("¥30",48,"#FFF7ED",True)+'</Positioned>')
cases.append(dict(id=4,slug="ticket",W=W,H=H,bg=bg,title="Zine Fair 入场券",desc="ClipPath 切出两侧弧形缺口，券面仍是完整可读的矩形信息区。",body="".join(b)))
# 5 bloom exhibition
W,H=1080,1350; bg="#F7F1F4"; b=[]
for i in range(12):
    ang=i*30; b.append(f'<Positioned left="460" top="350" width="160" height="420"><Transform matrix="{matrot(ang)}" origin="(80,210)"><Container width="160" height="420" color="{"#BE185D" if i%3==0 else ("#F59E0B" if i%3==1 else "#7C3AED")}{"55" if i%2 else "88"}" borderRadius="80"/></Transform></Positioned>')
b.append('<Positioned left="70" top="60">'+T("BLOOM / 植物与几何",15,"#BE185D",True,' letterSpacing="2"')+'</Positioned>')
b.append('<Positioned left="70" top="1120" width="940">'+T("花瓣是旋转的圆。",52,"#3B0764",True)+'</Positioned>')
b.append('<Positioned left="70" top="1200">'+T("2026.11.14–12.20 · 云构温室 · 免费",22,"#6B21A8")+'</Positioned>')
cases.append(dict(id=5,slug="bloom",W=W,H=H,bg=bg,title="Bloom 展览海报",desc="12 个旋转半透明圆形叠出花瓣，文字落在留白底部。",body="".join(b)))
# 6 static magazine
W,H=1080,1350; bg="#0F172A"; b=[]
for i in range(28):
    y=80+i*44; off=(i%4)*60
    b.append(rect(0+off,y,1080-off,18,"#38BDF8" if i%4==0 else ("#F472B6" if i%4==1 else "#1E293B")))
b.append('<Positioned left="80" top="520" width="920"><Container width="920" height="70" color="#0F172A"/></Positioned>')
b.append('<Positioned left="80" top="530">'+T("STATIC",110,"#F8FAFC",True)+'</Positioned>')
b.append('<Positioned left="86" top="660">'+T("STATIC",110,"#F472B6",True)+'</Positioned>')
b.append('<Positioned left="60" top="782" width="960" height="60"><Container width="960" height="60" color="#0F172A"/></Positioned>')
b.append('<Positioned left="80" top="800" width="920">'+T("关于噪点、偏移与仍然可读的版面。",26,"#CBD5E1")+'</Positioned>')
b.append('<Positioned left="40" top="1160" width="1000" height="70"><Container width="1000" height="70" color="#0F172A"/></Positioned>')
b.append('<Positioned left="80" top="1180">'+T("ISSUE 06 / WINTER 2026 · ¥48",18,"#94A3B8",True)+'</Positioned>')
cases.append(dict(id=6,slug="static",W=W,H=H,bg=bg,title="Static 杂志封面",desc="偏移条纹与双色错位标题，模拟印刷错版但不牺牲可读性。",body="".join(b)))
# 7 depth photo festival
W,H=1080,1350; bg="#111827"; b=[]
for i in range(4):
    b.append(f'<Positioned left="{80+i*40}" top="{260+i*50}" width="920" height="420"><ImageFiltered sigmaX="{4+i*3}" sigmaY="{4+i*3}"><Container width="920" height="420" color="{"#1E3A8A" if i%2==0 else "#7C2D12"}" borderRadius="24"/></ImageFiltered></Positioned>')
b.append('<Positioned left="80" top="70">'+T("DEPTH / PHOTO FESTIVAL",15,"#FBBF24",True,' letterSpacing="3"')+'</Positioned>')
b.append('<Positioned left="80" top="820" width="920">'+T("Depth of Field",72,"#F9FAFB",True)+'</Positioned>')
b.append('<Positioned left="80" top="920" width="900">'+T("四层高斯模糊，一层清晰标题。",26,"#D1D5DB")+'</Positioned>')
b.append('<Positioned left="80" top="1180">'+T("2026.11.05–11.30 · 云构影像中心",20,"#FBBF24")+'</Positioned>')
cases.append(dict(id=7,slug="depth",W=W,H=H,bg=bg,title="Depth 摄影节海报",desc="四层不同 sigma 的 ImageFiltered 叠出景深，标题保持清晰。",body="".join(b)))
# 8 orbit science card
W,H=1080,1350; bg="#07121F"; b=[]
for i,(ang,rx,ry,col) in enumerate([(0,360,180,"#38BDF8"),(60,300,220,"#A78BFA"),(120,380,150,"#34D399")]):
    b.append(f'<Positioned left="140" top="260" width="800" height="600"><Transform matrix="{matrot(ang)}" origin="(400,300)"><Container width="800" height="600" color="transparent" borderRadius="400" border="2 SOLID {col}88"/></Transform></Positioned>')
    b.append(f'<Positioned left="{540+rx*math.cos(math.radians(ang))-10:.1f}" top="{560+ry*math.sin(math.radians(ang))-10:.1f}" width="20" height="20"><Container width="20" height="20" color="{col}" shape="CIRCLE"/></Positioned>')
b.append('<Positioned left="70" top="70">'+T("ORBIT / SCIENCE SERIES",15,"#38BDF8",True,' letterSpacing="3"')+'</Positioned>')
b.append('<Positioned left="70" top="120" width="940">'+T("三颗星的轨道",56,"#F8FAFC",True)+'</Positioned>')
b.append('<Positioned left="70" top="1090">'+T("2026.12.03 · 19:30 · 云构天文台",22,"#CBD5E1")+'</Positioned>')
b.append('<Positioned left="70" top="1140">'+T("公开讲座 · 需预约",18,"#38BDF8")+'</Positioned>')
cases.append(dict(id=8,slug="orbit",W=W,H=H,bg=bg,title="Orbit 科学讲座卡",desc="三条旋转椭圆环（Transform）与轨道点，数据关系用几何表达。",body="".join(b)))
# 9 fold architecture
W,H=1080,1350; bg="#EFEAE1"; b=[]
for i in range(5):
    x=80+i*190; b.append(f'<Positioned left="{x}" top="{300+i*40}" width="220" height="520"><Transform matrix="{matrot(-12+i*6)}" origin="(110,260)"><Container width="220" height="520" color="{"#1F2937" if i%2==0 else "#9A3412"}{"CC" if i%2==0 else "AA"}" borderRadius="6"/></Transform></Positioned>')
b.append('<Positioned left="70" top="70">'+T("FOLD / ARCHITECTURE LECTURE",15,"#9A3412",True,' letterSpacing="2"')+'</Positioned>')
b.append('<Positioned left="70" top="140" width="940">'+T("折一次，空间就变了。",52,"#1F2937",True)+'</Positioned>')
b.append('<Positioned left="70" top="1090">'+T("2026.11.28 · 14:00 · 云构展厅",22,"#374151")+'</Positioned>')
b.append('<Positioned left="70" top="1140">'+T("主讲：结构工作室 / 免费",18,"#9A3412")+'</Positioned>')
cases.append(dict(id=9,slug="fold",W=W,H=H,bg=bg,title="Fold 建筑讲座海报",desc="五块旋转面板用 Transform 叠出折叠空间，文字落在空白区。",body="".join(b)))
# 10 weave market
W,H=1080,1350; bg="#F6F1E7"; b=[]
for i in range(18):
    x=60+i*56; col=["#1D4ED8","#F59E0B","#0F766E"][i%3]
    b.append(rect(x,200,36,740,col+"77" if i%2 else col+"AA"))
for j in range(9):
    y=260+j*80; b.append(rect(60,y,960,18,"#FFFFFFAA"))
b.append('<Positioned left="60" top="70">'+T("WEAVE / TEXTILE MARKET",15,"#0F766E",True,' letterSpacing="2"')+'</Positioned>')
b.append('<Positioned left="60" top="1000" width="960">'+T("经纬市场",56,"#0B1220",True)+'</Positioned>')
b.append('<Positioned left="60" top="1090">'+T("18 位织作者 · 36 种纹理 · 11.22–11.23",22,"#334155")+'</Positioned>')
b.append('<Positioned left="60" top="1150">'+T("云构中庭 · 免费入场",18,"#0F766E")+'</Positioned>')
cases.append(dict(id=10,slug="weave",W=W,H=H,bg=bg,title="Weave 织物市集海报",desc="18 条竖线与 9 条横向白线叠成织物结构，信息区留在底部。",body="".join(b)))
notes={1:"同心圆环：9 个 Container 圆环，边框宽度与透明度交替；不依赖图片。",2:"参数化正弦：18 条 100 段折线，相位与振幅按索引变化。",3:"半透明叠层：14 个矩形以 40% alpha 叠加，标题放在无覆盖区。",4:"ClipPath：一个矩形路径加两侧 Q 曲线缺口，子容器仍是完整券面。",5:"旋转叠加：12 个圆形容器以 30° 步进旋转，alpha 混合出花瓣。",6:"错版条纹：条纹与双色标题偏移，背景块保证标题局部干净。",7:"ImageFiltered：4 层不同 sigma 的色彩块制造景深，标题在滤镜外。",8:"轨道环：Transform 旋转 3 个椭圆边框，轨道点用三角函数定位。",9:"折叠面板：5 个容器以不同角度旋转，形成空间折面。",10:"织物网格：18 竖条 + 9 横条，透明度与颜色按位置变化。"}
for c in cases:
    d=OUT/f"case-{c['id']:02d}"; d.mkdir(parents=True,exist_ok=True)
    (d/'final.snapshot').write_text(page(c['W'],c['H'],c['bg'],c['body']),encoding='utf-8')
    (d/'case.md').write_text(f"# {c['title']}\n\n- 场景：{c['desc']}\n- 手法：{notes[c['id']]}\n- 主图：final.png（{c['W']}×{c['H']}）；DSL：final.snapshot\n",encoding='utf-8')
print('B03 wrote',len(cases))
