#!/usr/bin/env python3
"""B02 'Stitch' repair cafe: ten touchpoints from one design system."""
import math, os, html
from pathlib import Path
SCRIPT=Path(__file__).resolve(); SUITE=Path(os.environ.get("SNAPSHOT_TASK_ROOT",SCRIPT.parents[4])); RUN=SCRIPT.parents[2].name
OUT=SUITE/'outputs'/RUN/'B02'; OUT.mkdir(parents=True,exist_ok=True)
CREAM="#F4EFE6"; GREEN="#1F4D3A"; TERRA="#C2410C"; INK="#16211B"; SAND="#E6DCCB"; MINT="#DCEFE3"
def esc(s): return html.escape(str(s),quote=False)
def T(txt,size,color=INK,bold=False,extra="",fam="Noto Sans CJK SC"):
    st=' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="{fam}" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'
def rect(x,y,w,h,color,r=0,border=None):
    b=f' border="{border}"' if border else ""
    return f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Container width="{w}" height="{h}" color="{color}" borderRadius="{r}"{b}/></Positioned>'
def seg(x1,y1,x2,y2,color,w=3):
    L=math.hypot(x2-x1,y2-y1); a=math.atan2(y2-y1,x2-x1); c,s=math.cos(a),math.sin(a)
    mat=f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
    return f'<Positioned left="{x1:.1f}" top="{y1-w/2:.1f}"><Transform matrix="{mat}" origin="(0,0)"><Container width="{L:.1f}" height="{w}" color="{color}" borderRadius="{w/2}"/></Transform></Positioned>'
def stitch(x1,y1,x2,y2,color=TERRA,w=3,dash=12,gap=9):
    out=[]; L=math.hypot(x2-x1,y2-y1); ux,uy=(x2-x1)/L,(y2-y1)/L; t=0
    while t<L:
        e=min(t+dash,L); out.append(seg(x1+ux*t,y1+uy*t,x1+ux*e,y1+uy*e,color,w)); t=e+gap
    return "".join(out)
def spool(cx,cy,r,line=GREEN,label=True):
    p=[f'<Positioned left="{cx-r}" top="{cy-r}" width="{2*r}" height="{2*r}"><Container width="{2*r}" height="{2*r}" color="{line}" shape="CIRCLE"/></Positioned>']
    p.append(f'<Positioned left="{cx-r*0.45}" top="{cy-r*0.45}" width="{r*0.9}" height="{r*0.9}"><Container width="{r*0.9}" height="{r*0.9}" color="{CREAM}" shape="CIRCLE"/></Positioned>')
    p.append(stitch(cx-r*1.5,cy,cx+r*1.5,cy,TERRA,3,10,8))
    return "".join(p)
def case_dsl(W,H,bg,body):
    return f'<Snapshot background="{bg}" type="png"><Container width="{W}" height="{H}"><Stack alignment="TOP_LEFT"><Container width="{W}" height="{H}" color="{bg}"/>{body}</Stack></Container></Snapshot>'
cases=[]
# 1 identity
W,H=1080,1080; b=[]
b.append(spool(300,420,150))
b.append(f'<Positioned left="540" top="330"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("缝补站",72,GREEN,True)+T("STITCH",36,TERRA,True,' letterSpacing="8"')+T("把还能用的东西，再留久一点。",24,INK)+'</Column></Positioned>')
b.append(stitch(80,720,1000,720,TERRA,3,14,10))
b.append(f'<Positioned left="80" top="780"><Row crossAxisAlignment="CENTER">'+T("维修 / 改造 / 教学",24,GREEN,True)+'<SizedBox width="24"/>'+T("社区修补空间 · 周六 10:00–16:00",20,INK)+'</Row></Positioned>')
cases.append((1,"identity",W,H,"缝补站 · 品牌标识","社区修补空间的身份卡：线轴圆 + 虚线缝合，暖纸色与墨绿。",b))
# 2 program poster
W,H=1080,1350; b=[]
b.append('<Positioned left="60" top="60"><Row crossAxisAlignment="CENTER">'+T("STITCH / 十月",18,TERRA,True,' letterSpacing="3"')+'</Row></Positioned>')
b.append('<Positioned left="60" top="100" width="960">'+T("这个月，\n把坏掉的东西带回来。",48,GREEN,True)+'</Positioned>')
b.append('<Positioned left="60" top="290" width="960">'+T("三场主题工位 · 免费 · 需预约",22,INK)+'</Positioned>')
sessions=[("10.12","电器","小家电检测 / 换线 / 安全用电"),("10.19","衣物","补洞 / 改衣 / 拉链更换"),("10.26","家具","榫卯加固 / 上油 / 小修")]
for i,(d,k,desc) in enumerate(sessions):
    y=400+i*250
    b.append(rect(60,y,960,210,CREAM,18,f"1 SOLID {SAND}"))
    b.append(f'<Positioned left="84" top="{y+24}">'+T(d,34,TERRA,True)+'</Positioned>')
    b.append(f'<Positioned left="280" top="{y+26}">'+T(k,30,GREEN,True)+'</Positioned>')
    b.append(f'<Positioned left="280" top="{y+80}" width="700">'+T(desc,22,INK)+'</Positioned>')
    b.append(stitch(84,y+170,1000,y+170,TERRA,2,10,8))
b.append('<Positioned left="60" top="1200">'+T("云构社区中心 2F · 每人限带 1 件 · 缝补站不收取零件费",18,INK)+'</Positioned>')
cases.append((2,"program",W,H,"十月缝补站 · 场次海报","告诉居民这个月能修什么、什么时候来。",b))
# 3 app home
W,H=390,844; b=[]
b.append(rect(0,0,390,844,CREAM))
b.append('<Positioned left="24" top="42">'+T("缝补站",22,GREEN,True)+'</Positioned>')
b.append('<Positioned right="24" top="44">'+T("10.12 周六",15,TERRA,True)+'</Positioned>')
b.append(rect(24,96,342,210,GREEN,18))
b.append('<Positioned left="44" top="118">'+T("下一场 · 电器工位",15,MINT,True)+'</Positioned>')
b.append('<Positioned left="44" top="146">'+T("还剩 4 个工位",28,"#FFFFFF",True)+'</Positioned>')
b.append('<Positioned left="44" top="196">'+T("10.12 · 10:00–16:00 · 2F",16,MINT)+'</Positioned>')
b.append('<Positioned left="44" top="238"><Container width="140" height="44" color="#FFFFFF" borderRadius="22" alignment="CENTER">'+T("预约",18,GREEN,True)+'</Container></Positioned>')
cats=[("电器","换线 / 小家电"),("衣物","补洞 / 改衣"),("家具","加固 / 上油")]
for i,(k,d) in enumerate(cats):
    y=340+i*94
    b.append(rect(24,y,342,80,CREAM,14,f"1 SOLID {SAND}"))
    b.append(f'<Positioned left="44" top="{y+14}">'+T(k,20,GREEN,True)+'</Positioned>')
    b.append(f'<Positioned left="44" top="{y+44}">'+T(d,15,INK)+'</Positioned>')
    b.append(f'<Positioned right="44" top="{y+26}">'+T("→",22,TERRA,True)+'</Positioned>')
b.append(rect(24,680,342,90,INK,16))
b.append('<Positioned left="44" top="700">'+T("我的修补记录",17,MINT,True)+'</Positioned>')
b.append('<Positioned left="44" top="728">'+T("3 件物品 · 延长使用 2.4 年",15,"#FFFFFF"))
b.append('</Positioned>')
cases.append((3,"app-home",W,H,"App 首页 · 下一场与分类","手机上的第一屏：先看到下一场余位，再选类别。",b))
# 4 booking
W,H=390,844; b=[rect(0,0,390,844,CREAM)]
b.append('<Positioned left="24" top="40">'+T("← 返回",16,TERRA,True)+'</Positioned>')
b.append('<Positioned left="24" top="86">'+T("预约工位",30,GREEN,True)+'</Positioned>')
b.append('<Positioned left="24" top="128">'+T("10.12 周六 · 电器工位",17,INK)+'</Positioned>')
slots=["10:00","11:00","13:00","14:00"]
for i,s in enumerate(slots):
    x=24+i*86; active=i==1
    b.append(f'<Positioned left="{x}" top="170"><Container width="76" height="52" color="{GREEN if active else "#FFFFFF"}" borderRadius="12" border="1 SOLID {GREEN if active else SAND}" alignment="CENTER">'+T(s,16,"#FFFFFF" if active else INK,True)+'</Container></Positioned>')
b.append(rect(24,250,342,250,"#FFFFFF",16,f"1 SOLID {SAND}"))
b.append('<Positioned left="44" top="270">'+T("要修什么？",17,GREEN,True)+'</Positioned>')
b.append('<Positioned left="44" top="302" width="300">'+T("台灯不亮，插头附近有轻微焦味。",16,INK)+'</Positioned>')
b.append('<Positioned left="44" top="354">'+T("品牌/型号（选填）",14,TERRA)+'</Positioned>')
b.append('<Positioned left="44" top="380" width="300" height="40"><Container width="300" height="40" color="{CREAM}" borderRadius="8"/></Positioned>'.replace("{CREAM}",CREAM))
b.append('<Positioned left="44" top="440">'+T("安全提示：请勿带电拆机。",14,TERRA)+'</Positioned>')
b.append(rect(24,530,342,110,MINT,16))
b.append('<Positioned left="44" top="550">'+T("预约摘要",16,GREEN,True)+'</Positioned>')
b.append('<Positioned left="44" top="580">'+T("10.12 11:00 · 电器工位 · 免费",16,INK)+'</Positioned>')
b.append(f'<Positioned left="24" top="690"><Container width="342" height="56" color="{GREEN}" borderRadius="28" alignment="CENTER">'+T("确认预约",20,"#FFFFFF",True)+'</Container></Positioned>')
b.append('<Positioned left="24" top="766">'+T("可提前 24 小时取消；迟到 15 分钟视为放弃。",13,INK)+'</Positioned>')
cases.append((4,"booking",W,H,"预约 · 时段与物品描述","让居民用三步完成预约，并看到安全提示。",b))
# 5 volunteer board
W,H=1200,800; b=[rect(0,0,1200,800,CREAM)]
b.append('<Positioned left="48" top="40">'+T("STITCH / VOLUNTEERS",16,TERRA,True,' letterSpacing="2"')+'</Positioned>')
b.append('<Positioned left="48" top="76">'+T("周六值班表",40,GREEN,True)+'</Positioned>')
b.append('<Positioned left="48" top="132">'+T("10.12 · 10:00–16:00 · 2F 工坊",18,INK)+'</Positioned>')
shifts=[("10:00–12:00","接待 / 登记","林川","A 台"),("10:00–13:00","电器检测","周禾","B 台"),("11:00–14:00","衣物缝补","苏言","C 台"),("13:00–16:00","家具加固","许宁","D 台"),("14:00–16:00","收尾 / 归档","孟澄","A 台")]
for i,(t,role,name,desk) in enumerate(shifts):
    y=190+i*105
    b.append(rect(48,y,1104,88,"#FFFFFF",14,f"1 SOLID {SAND}"))
    b.append(f'<Positioned left="68" top="{y+16}">'+T(t,20,GREEN,True)+'</Positioned>')
    b.append(f'<Positioned left="300" top="{y+16}">'+T(role,20,INK)+'</Positioned>')
    b.append(f'<Positioned left="760" top="{y+16}">'+T(name,20,TERRA,True)+'</Positioned>')
    b.append(f'<Positioned left="980" top="{y+18}" width="150" alignment="CENTER_RIGHT">'+T(desk,16,INK)+'</Positioned>')
b.append('<Positioned left="48" top="748">'+T("空档：12:00–13:00 午休；如缺岗请联系值班协调。",16,INK)+'</Positioned>')
cases.append((5,"shifts",W,H,"志愿者值班板","让协调者一眼看到时段、角色、人员与工位。",b))
# 6 door sign
W,H=1080,1350; b=[rect(0,0,1080,1350,GREEN)]
b.append('<Positioned left="80" top="80">'+T("STITCH / 缝补站",24,MINT,True,' letterSpacing="3"')+'</Positioned>')
b.append('<Positioned left="80" top="360" width="920">'+T("REPAIR\nCAFÉ",96,"#FFFFFF",True)+'</Positioned>')
b.append('<Positioned left="80" top="650" width="920">'+T("把坏掉的东西带上来。",32,MINT)+'</Positioned>')
b.append(stitch(80,760,1000,760,TERRA,4,16,12))
b.append('<Positioned left="80" top="830"><Row crossAxisAlignment="CENTER">'+T("2F",140,"#FFFFFF",True)+'<SizedBox width="24"/>'+T("↑ 电梯左转",30,MINT)+'</Row></Positioned>')
b.append('<Positioned left="80" top="1080">'+T("周六 10:00–16:00 · 每人限带 1 件",24,"#FFFFFF")+'</Positioned>')
b.append('<Positioned left="80" top="1130">'+T("云构社区中心 · 免费",20,MINT)+'</Positioned>')
cases.append((6,"door-sign",W,H,"入口导视 · 2F","从街边看见就能知道：修东西、上二楼、周六。",b))
# 7 repair record
W,H=800,1200; b=[rect(0,0,800,1200,CREAM)]
b.append('<Positioned left="60" top="60">'+T("STITCH / REPAIR RECORD",15,TERRA,True,' letterSpacing="2"')+'</Positioned>')
b.append('<Positioned left="60" top="96">'+T("修补记录",32,GREEN,True)+'</Positioned>')
b.append('<Positioned left="60" top="150">'+T("No. S-2026-1012-07",15,INK)+'</Positioned>')
b.append(stitch(60,190,740,190,TERRA,2,10,8))
rows=[("物品","台灯 / IKEA 工作灯"),("问题","电源线破损，接触不良"),("处理","更换电源线与插头"),("零件","2×0.75mm² 线 · 插头"),("工时","45 分钟"),("收费","¥ 0（零件由捐赠箱提供）"),("保修","30 天内同类问题免费复查")]
for i,(k,v) in enumerate(rows):
    y=230+i*90
    b.append(f'<Positioned left="60" top="{y}">'+T(k,16,TERRA,True)+'</Positioned>')
    b.append(f'<Positioned left="220" top="{y}" width="520">'+T(v,20,INK)+'</Positioned>')
b.append(rect(60,900,680,150,MINT,14))
b.append('<Positioned left="80" top="920">'+T("下一次保养建议",16,GREEN,True)+'</Positioned>')
b.append('<Positioned left="80" top="950" width="620">'+T("检查插头温度；避免与取暖器共用插座。",18,INK)+'</Positioned>')
b.append('<Positioned left="60" top="1100">'+T("维修志愿者：周禾 · 2026.10.12",14,INK)+'</Positioned>')
cases.append((7,"repair-record",W,H,"修补记录 / 回执","给物主一张能带走的记录：问题、处理、零件与保修。",b))
# 8 social post
W,H=1080,1080; b=[rect(0,0,1080,1080,GREEN)]
b.append('<Positioned left="72" top="72">'+T("STITCH / MONTHLY",16,MINT,True,' letterSpacing="3"')+'</Positioned>')
b.append('<Positioned left="72" top="150" width="900">'+T("14 kg",120,"#FFFFFF",True)+'</Positioned>')
b.append('<Positioned left="72" top="310" width="900">'+T("这个月被留下的物品重量",30,MINT)+'</Positioned>')
stats=[("23","件物品修好"),("9","位志愿者"),("31","小时开放")]
for i,(v,k) in enumerate(stats):
    x=72+i*310
    b.append(f'<Positioned left="{x}" top="440"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T(v,52,"#FFFFFF",True)+T(k,20,MINT)+'</Column></Positioned>')
b.append(stitch(72,680,1008,680,TERRA,4,18,12))
b.append('<Positioned left="72" top="740" width="900">'+T("下一场 10.12 · 电器工位 · 还有 4 个位置",26,"#FFFFFF",True)+'</Positioned>')
b.append('<Positioned left="72" top="800" width="900">'+T("带一件坏掉的东西来，我们看看还能不能留下它。",20,MINT)+'</Positioned>')
cases.append((8,"social",W,H,"月度社交卡 · 14kg","用一个重量数字，把“维修”从情怀变成可感的成果。",b))
# 9 loyalty card
W,H=1080,640; b=[rect(0,0,1080,640,CREAM)]
b.append('<Positioned left="60" top="50">'+T("STITCH / 修补里程",16,TERRA,True,' letterSpacing="2"')+'</Positioned>')
b.append('<Positioned left="60" top="86">'+T("再来一次，换一节缝纫课。",28,GREEN,True)+'</Positioned>')
for i in range(6):
    x=60+i*160; filled=i<5
    b.append(f'<Positioned left="{x}" top="180"><Container width="120" height="120" color="{GREEN if filled else "#FFFFFF"}" shape="CIRCLE" border="2 SOLID {GREEN}" alignment="CENTER">'+T("✓" if filled else str(i+1),40,"#FFFFFF" if filled else GREEN,True)+'</Container></Positioned>')
b.append('<Positioned left="60" top="340">'+T("已修补 5 件 · 第 6 件完成后可预约基础缝纫课",18,INK)+'</Positioned>')
b.append('<Positioned left="60" top="420"><Row crossAxisAlignment="CENTER">'+T("持卡人：林川",16,INK)+'<SizedBox width="40"/>'+T("S-0042",16,TERRA,True)+'</Row></Positioned>')
b.append(stitch(60,500,1020,500,TERRA,2,10,8))
b.append('<Positioned left="60" top="530">'+T("不可兑换现金 · 仅限本人使用 · 有效期 12 个月",14,INK)+'</Positioned>')
cases.append((9,"loyalty",W,H,"修补里程卡","把多次维修累积成一节缝纫课，鼓励回访。",b))
# 10 impact report
W,H=1440,900; b=[rect(0,0,1440,900,CREAM)]
b.append('<Positioned left="48" top="40">'+T("STITCH / IMPACT 2026",15,TERRA,True,' letterSpacing="2"')+'</Positioned>')
b.append('<Positioned left="48" top="76">'+T("一年之后：留下来的东西",36,GREEN,True)+'</Positioned>')
kpis=[("168","件物品修复"),("96","kg 避免丢弃"),("42","位志愿者"),("11","场教学")]
for i,(v,k) in enumerate(kpis):
    x=48+i*330
    b.append(f'<Positioned left="{x}" top="150"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T(v,46,GREEN,True)+T(k,18,INK)+'</Column></Positioned>')
b.append(rect(48,270,900,500,"#FFFFFF",16,f"1 SOLID {SAND}"))
b.append('<Positioned left="72" top="292">'+T("每月修复件数",18,GREEN,True)+'</Positioned>')
vals=[12,18,15,22,25,28,20,28]
for i,v in enumerate(vals):
    h=v/30*320; x=100+i*100
    b.append(f'<Positioned left="{x}" top="{550-h:.1f}" width="56" height="{h:.1f}"><Container width="56" height="{h:.1f}" color="{GREEN if i%2==0 else "#6B8F7E"}" borderRadiusTopLeft="6" borderRadiusTopRight="6"/></Positioned>')
    b.append(f'<Positioned left="{x-16}" top="560" width="88"><Container width="88" alignment="CENTER">'+T(str(i+1),14,INK)+'</Container></Positioned>')
b.append(rect(980,270,412,240,GREEN,16))
b.append('<Positioned left="1004" top="294">'+T("志愿者说",16,MINT,True)+'</Positioned>')
b.append('<Positioned left="1004" top="330" width="364">'+T("“很多人不是不会修，是不知道去哪里修。”",22,"#FFFFFF")+'</Positioned>')
b.append('<Positioned left="1004" top="430">'+T("— 周禾 · 电器组",15,MINT)+'</Positioned>')
b.append(rect(980,530,412,240,CREAM,16,f"1 SOLID {SAND}"))
b.append('<Positioned left="1004" top="550">'+T("资金去向",16,TERRA,True)+'</Positioned>')
b.append('<Positioned left="1004" top="586" width="364">'+T("零件 48% · 工具 27% · 场地 18% · 教学 7%",18,INK)+'</Positioned>')
cases.append((10,"impact",W,H,"年度影响报告页","用修复件数、避免丢弃重量与志愿者声音，说明项目的真实产出。",b))
for cid,slug,W,H,title,desc,body in cases:
    d=OUT/f"case-{cid:02d}"; d.mkdir(parents=True,exist_ok=True)
    (d/'final.snapshot').write_text(case_dsl(W,H,CREAM,"".join(body)),encoding='utf-8')
    (d/'case.md').write_text(f"# {title}\n\n- 场景：缝补站 / Stitch\n- 用途：{desc}\n- 主图：final.png（{W}×{H}）；DSL：final.snapshot\n- 内容为自拟演示。\n",encoding='utf-8')
print('B02 wrote',len(cases))
