#!/usr/bin/env python3
"""B01 ten real-world showcase pieces; each in case-NN/final.snapshot."""
import math, os, html
from pathlib import Path
SCRIPT=Path(__file__).resolve(); SUITE=Path(os.environ.get("SNAPSHOT_TASK_ROOT",SCRIPT.parents[4])); RUN=SCRIPT.parents[2].name
OUT=SUITE/'outputs'/RUN/'B01'; OUT.mkdir(parents=True,exist_ok=True)
def esc(s): return html.escape(str(s),quote=False)
def T(txt,size,color,bold=False,extra="",fam="Noto Sans CJK SC"):
    st=' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="{fam}" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'
def rect(x,y,w,h,color,r=0,border=None):
    b=f' border="{border}"' if border else ""
    return f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Container width="{w}" height="{h}" color="{color}" borderRadius="{r}"{b}/></Positioned>'
def seg(x1,y1,x2,y2,color,w=4):
    L=math.hypot(x2-x1,y2-y1); a=math.atan2(y2-y1,x2-x1); c,s=math.cos(a),math.sin(a)
    mat=f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
    return f'<Positioned left="{x1:.1f}" top="{y1-w/2:.1f}"><Transform matrix="{mat}" origin="(0,0)"><Container width="{L:.1f}" height="{w}" color="{color}" borderRadius="{w/2}"/></Transform></Positioned>'
def is_dark(c):
    h=c.lstrip('#'); r,g,b=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    def lin(x): return x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4
    return 0.2126*lin(r)+0.7152*lin(g)+0.0722*lin(b)<0.15

def shell(W,H,bg,accent,title,sub,brand,body,foot):
    fg = "#F8FAFC" if is_dark(bg) else "#0B1220"
    subc = "#A9B8CC" if is_dark(bg) else "#5B6B80"
    p=[f'<Snapshot background="{bg}" type="png"><Container width="{W}" height="{H}"><Stack alignment="TOP_LEFT"><Container width="{W}" height="{H}" color="{bg}"/>']
    p.append(f'<Positioned left="48" top="40"><Row crossAxisAlignment="CENTER"><Container width="10" height="10" color="{accent}" shape="CIRCLE"/><SizedBox width="8"/>'+T(brand,15,accent,True,' letterSpacing="2"')+'</Row></Positioned>')
    p.append(f'<Positioned left="48" top="76" width="{W-96}">'+T(title,44,fg,True)+'</Positioned>')
    p.append(f'<Positioned left="48" top="136" width="{W-96}">'+T(sub,20,subc)+'</Positioned>')
    p.append(body)
    p.append(f'<Positioned left="48" bottom="34">'+T(foot,14,"#8896AB")+'</Positioned>')
    p.append('</Stack></Container></Snapshot>')
    return "\n".join(p)
cases=[]
# 1 coffee
W,H=1080,1350; bg="#F3EEE4"; acc="#9A3412"
b=[f'<Positioned left="48" top="200"><Container width="300" height="300" color="#9A3412" borderRadius="150" alignment="CENTER"><Column crossAxisAlignment="CENTER" mainAxisSize="MIN">'+T("300g",52,"#FFF7ED",True)+T("/ 3:00",24,"#FED7AA")+'</Column></Container></Positioned>']
steps=[("00:00","闷蒸 60g","30s"),("00:30","注水至 140g","25s"),("00:55","注水至 220g","25s"),("01:20","注水至 300g","30s"),("01:50","滴滤完成","70s")]
for i,(t,a,d) in enumerate(steps):
    y=560+i*130
    b.append(f'<Positioned left="420" top="{y}"><Container width="14" height="14" color="{acc}" shape="CIRCLE"/></Positioned>')
    if i<4: b.append(seg(427,y+14,427,y+116,acc,2))
    b.append(f'<Positioned left="460" top="{y-10}">'+T(t,22,acc,True)+'</Positioned>')
    b.append(f'<Positioned left="620" top="{y-10}">'+T(a,22,"#2B2118")+'</Positioned>')
    b.append(f'<Positioned left="900" top="{y-10}">'+T(d,18,"#7A6A58")+'</Positioned>')
cases.append(dict(id=1,slug="brew",W=W,H=H,title="Pour-over, without the guesswork",sub="Brew guide · 15g 中细研磨 · 92°C · 一人份",brand="BREW / POUR GUIDE",body="".join(b),foot="Brew guide 01 · 时间与注水量按实际冲煮顺序",palette=[bg,acc]))
# 2 cycling
W,H=1200,800; bg="#0A1626"; acc="#38BDF8"
prof=[(90,560),(190,500),(280,530),(390,420),(480,450),(600,330),(700,360),(830,250),(950,300),(1090,210)]
b=[f'<Positioned left="48" top="200"><Container width="1104" height="400" color="#0F2138" borderRadius="18" border="1 SOLID #1E3A5F"/></Positioned>']
b.append(f'<Positioned left="80" top="220">'+T("RIDGE LINE / 42 km",18,"#93C5FD",True)+'</Positioned>')
for i in range(len(prof)-1):
    b.append(seg(prof[i][0]+40,prof[i][1]+40,prof[i+1][0]+40,prof[i+1][1]+40,acc,4))
for x,y in prof:
    b.append(f'<Positioned left="{x+35}" top="{y+35}" width="10" height="10"><Container width="10" height="10" color="#E0F2FE" shape="CIRCLE" border="2 SOLID {acc}"/></Positioned>')
stats=[("42.0","km 距离"),("+1,180","m 爬升"),("2:35","预计时间"),("4","补给点")]
for i,(v,l) in enumerate(stats):
    x=80+i*270
    b.append(f'<Positioned left="{x}" top="620"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T(v,38,"#F8FAFC",True)+T(l,18,"#94A3B8")+'</Column></Positioned>')
b.append(f'<Positioned left="80" top="700">'+T("起点 07:00 · 山顶风大，建议带防风层 · 下坡限速 35 km/h",18,"#93C5FD")+'</Positioned>')
cases.append(dict(id=2,slug="ridge",W=W,H=H,title="Ridgeline loop · 42 km",sub="骑行路线卡 · 海拔剖面按 1:1 距离比例绘制",brand="RIDGE / RIDE CARD",body="".join(b),foot="Route card 02 · 演示数据",palette=[bg,acc]))
# 3 energy dashboard
W,H=1440,900; bg="#F4F6FA"; acc="#16A34A"
b=[]
vals=[12.4,10.8,14.2,9.6,11.3,8.9,7.4]; days=["一","二","三","四","五","六","日"]
b.append(rect(60,300,1320,300,"#FFFFFF",18,"1 SOLID #E1E7F0"))
for i,v in enumerate(vals):
    h=v/16*150; x=110+i*150
    b.append(f'<Positioned left="{x}" top="{540-h:.1f}" width="86" height="{h:.1f}"><Container width="86" height="{h:.1f}" color="{"#16A34A" if v<9 else "#94A3B8"}" borderRadiusTopLeft="8" borderRadiusTopRight="8"/></Positioned>')
    b.append(f'<Positioned left="{x-10}" top="552" width="106"><Container width="106" alignment="CENTER">'+T(days[i],18,"#64748B")+'</Container></Positioned>')
    b.append(f'<Positioned left="{x-10}" top="{540-h-20:.1f}" width="106"><Container width="106" alignment="CENTER">'+T(f"{v:.1f}",16,"#475569")+'</Container></Positioned>')

b.append(f'<Positioned left="88" top="320">'+T("本周用电 · kWh",22,"#0B1220",True)+'</Positioned>')
kpis=[("本周 74.6","kWh · 较上周 −8.2%"),("峰值 14.2","周三 19:00"),("目标 80","低于目标 5.4")]
for i,(v,l) in enumerate(kpis):
    x=60+i*440
    b.append(f'<Positioned left="{x}" top="160"><Container width="400" height="110" color="#FFFFFF" borderRadius="16" border="1 SOLID #E1E7F0" padding="18"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T(v,30,"#0B1220",True)+T(l,17,"#64748B")+'</Column></Container></Positioned>')
b.append(f'<Positioned left="60" top="620"><Container width="1320" height="220" color="#0B1220" borderRadius="16" padding="22"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("省电建议 / 3 个动作",17,"#86EFAC",True,' letterSpacing="1"')+T("周三 19:00 峰值来自烘干机，改到周末白天可削掉 2.1 kWh。",22,"#E2E8F0")+T("待机负载占 9%：电视与路由器夜间断电，预计每周省 0.8 kWh。",22,"#E2E8F0")+T("空调每调高 1°C，本周可再省约 4.3 kWh。",22,"#E2E8F0")+'</Column></Container></Positioned>')
cases.append(dict(id=3,slug="watt",W=W,H=H,title="Watt · 本周家庭用电",sub="面向租户的省电复盘 · 7 天真实读数（演示数据）",brand="WATT / HOME ENERGY",body="".join(b),foot="Energy recap 03 · 演示数据",palette=[bg,acc]))
# 4 tide
W,H=1080,1350; bg="#082F49"; acc="#7DD3FC"
b=[f'<Positioned left="48" top="200"><Container width="984" height="360" color="#0C4A6E" borderRadius="18"/></Positioned>']
pts=[]
for i in range(0,101):
    t=i/100; x=80+t*920; y=420-140*math.sin(t*2*math.pi+0.6)
    pts.append((x,y))
for i in range(len(pts)-1): b.append(seg(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],acc,4))
b.append(f'<Positioned left="80" top="560">'+T("00:00",16,"#BAE6FD")+'</Positioned><Positioned left="800" top="560">'+T("24:00",16,"#BAE6FD")+'</Positioned>')
tide=[("03:10","1.8 m 高"),("09:25","0.4 m 低"),("15:40","1.7 m 高"),("21:50","0.5 m 低")]
for i,(t,v) in enumerate(tide):
    y=600+i*80
    b.append(f'<Positioned left="48" top="{y}"><Container width="300" height="60" color="#0C4A6E" borderRadius="10" padding="(8,16)"><Row crossAxisAlignment="CENTER">'+T(t,20,"#E0F2FE",True)+'<SizedBox width="12"/>'+T(v,20,"#BAE6FD")+'</Row></Container></Positioned>')
b.append(f'<Positioned left="400" top="600"><Container width="632" height="300" color="#0C4A6E" borderRadius="18" padding="22"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("安全下水窗 / SAFE WINDOW",17,"#7DD3FC",True,' letterSpacing="1"')+T("09:40–11:20 · 潮位 0.4–0.9 m",26,"#F0F9FF",True)+T("避开 12:30–14:10 的快速涨潮；岸边礁石在 0.8 m 以下露出。",20,"#BAE6FD")+'</Column></Container></Positioned>')
b.append('<Positioned left="400" top="960"><Container width="632" height="260" color="#0C4A6E" borderRadius="18" padding="22"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("读法 / HOW TO READ",17,"#7DD3FC",True,' letterSpacing="1"')+T("曲线是 24 小时潮位，不是游泳安全线。",20,"#E0F2FE")+T("两个低潮之间的窗口更适合新手；涨潮速度快于退潮。",20,"#BAE6FD")+T("礁石区在 0.8 m 以下露出，请留出回岸时间。",20,"#BAE6FD")+'</Column></Container></Positioned>')
cases.append(dict(id=4,slug="tide",W=W,H=H,title="Tide window · 西岸今天",sub="潮汐卡 · 曲线为演示潮位，高/低潮时刻可对照",brand="TIDE / SHORE NOTES",body="".join(b),foot="Tide card 04 · 演示数据，非航行依据",palette=[bg,acc]))
# 5 pantry
W,H=1080,1350; bg="#FAF5EC"; acc="#B45309"
items=[("燕麦","2 天"),("酸奶","3 天"),("菠菜","4 天"),("鸡蛋","8 天"),("豆腐","5 天"),("面包","1 天"),("番茄","6 天"),("牛奶","2 天"),("鹰嘴豆","20 天"),("米","180 天"),("咖啡豆","14 天"),("冷冻豌豆","60 天")]
b=[]
for i,(n,d) in enumerate(items):
    col=i%3; row=i//3; x=48+col*336; y=200+row*210
    days=int(''.join(ch for ch in d if ch.isdigit()))
    color="#B91C1C" if days<=3 else ("#B45309" if days<=7 else "#15803D")
    b.append(f'<Positioned left="{x}" top="{y}"><Container width="312" height="190" color="#FFFFFF" borderRadius="16" border="1 SOLID #E7DCCB" padding="16"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T(n,24,"#2B2118",True))
    b.append(T(f"剩余 {d}",20,color,True))
    b.append(f'<SizedBox height="12"/>')
    bw=min(280,days/180*280)
    b.append(f'<Container width="280" height="8" color="#F1E8DA" borderRadius="4"><Container width="{bw:.0f}" height="8" color="{color}" borderRadius="4"/></Container>')
    b.append('</Column></Container></Positioned>')
b.append('<Positioned left="48" top="1060"><Container width="984" height="140" color="#B45309" borderRadius="16" padding="20"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("本周优先 / EAT FIRST",16,"#FFEDD5",True,' letterSpacing="1"')+T("面包 1 天、燕麦 2 天、牛奶 2 天；先做早餐，再把菠菜与豆腐安排进两顿正餐。",22,"#FFFFFF")+'</Column></Container></Positioned>')
cases.append(dict(id=5,slug="shelf",W=W,H=H,title="Shelf · 冰箱里还有什么",sub="按剩余天数排序的 12 件食材，先吃左边红色",brand="SHELF / PANTRY",body="".join(b),foot="Pantry board 05 · 演示库存",palette=[bg,acc]))
# 6 transfer
W,H=1200,800; bg="#0F172A"; acc="#F59E0B"
b=[f'<Positioned left="60" top="220"><Container width="1080" height="380" color="#111C31" borderRadius="18" border="1 SOLID #24344D"/></Positioned>']
steps=[("T-120","值机 + 托运","T1 · 3F"),("T-75","安检","T1 · 2F"),("T-40","捷运 8 分钟","T1 → T2"),("T-25","登机口","T2 · B12"),("T-0","起飞","09:40")]
for i,(t,a,l) in enumerate(steps):
    x=110+i*195
    b.append(f'<Positioned left="{x}" top="280"><Container width="46" height="46" color="{acc}" shape="CIRCLE" alignment="CENTER">'+T(str(i+1),20,"#0F172A",True)+'</Container></Positioned>')
    if i<4: b.append(seg(x+46,303,x+195,303,"#475569",3))
    b.append(f'<Positioned left="{x-8}" top="346" width="190">'+T(t,18,acc,True)+'</Positioned>')
    b.append(f'<Positioned left="{x-8}" top="374" width="190">'+T(a,18,"#F8FAFC",True)+'</Positioned>')
    b.append(f'<Positioned left="{x-8}" top="402" width="190">'+T(l,16,"#94A3B8")+'</Positioned>')
b.append(f'<Positioned left="110" top="470">'+T("步行 6 分钟 · 全程约 1.2 km · 最晚 08:20 到达 T1",20,"#CBD5E1")+'</Positioned>')
b.append(f'<Positioned left="60" top="620"><Container width="1080" height="120" color="#F59E0B" borderRadius="14" padding="18"><Row crossAxisAlignment="CENTER">'+T("登机口 B12",26,"#0F172A",True)+'<Spacer/>'+T("09:40 起飞 · 08:20 前通过安检",20,"#0F172A")+'</Row></Container></Positioned>')
cases.append(dict(id=6,slug="transfer",W=W,H=H,title="T1 → T2 · 08:20 前到",sub="转机行动卡 · 时间为演示航班",brand="AIR / TRANSFER GUIDE",body="".join(b),foot="Transfer card 06 · 演示航班，不作为实际出行依据",palette=[bg,acc]))
# 7 concert
W,H=1080,1350; bg="#0B0B0F"; acc="#EF4444"
b=[f'<Positioned left="48" top="200"><Container width="500" height="500" color="#EF4444" shape="CIRCLE"/></Positioned><Positioned left="320" top="380"><Container width="360" height="360" color="#0B0B0F" shape="CIRCLE"/></Positioned>']
songs=[("01","Static Bloom","4:12"),("02","Night Bus","3:48"),("03","Low Tide","4:01"),("04","Paper City","3:22"),("05","Half Light","5:10"),("06","Afterimage","4:44"),("07","Signal Lost","3:59"),("08","Encore: Home","6:20")]
for i,(n,tm,d) in enumerate(songs):
    y=780+i*60
    b.append(f'<Positioned left="48" top="{y}"><Row crossAxisAlignment="CENTER">'+T(n,18,"#EF4444",True)+'<SizedBox width="16"/>'+T(tm,22,"#F8FAFC")+'<SizedBox width="14"/>'+T(d,16,"#94A3B8")+'</Row></Positioned>')
b.append(f'<Positioned left="620" top="780"><Container width="412" height="180" color="#1F1F27" borderRadius="14" padding="18"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("DOORS 19:00",20,"#EF4444",True)+T("SHOW 20:00",30,"#FFFFFF",True)+T("云构 Livehouse · 站席",18,"#A1A1AA")+'</Column></Container></Positioned>')
cases.append(dict(id=7,slug="aria",W=W,H=H,title="ARIA · Afterimage Tour",sub="2026.11.07 · 20:00 · 云构 Livehouse",brand="ARIA / SETLIST",body="".join(b),foot="Concert setlist 07 · 虚构演出",palette=[bg,acc]))
# 8 recipe
W,H=1080,1080; bg="#F2F7F1"; acc="#15803D"
b=[f'<Positioned left="48" top="200"><Container width="984" height="140" color="#15803D" borderRadius="18" padding="20"><Row crossAxisAlignment="CENTER"><Container width="150" height="100" color="#F2F7F1" borderRadius="12" alignment="CENTER">'+T("520",34,"#15803D",True)+'</Container><SizedBox width="20"/><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("kcal / 碗",18,"#DCFCE7")+T("高蛋白 · 20 分钟",26,"#FFFFFF",True)+'</Column></Row></Container></Positioned>']
macros=[("蛋白 34g",0.38,"#15803D"),("碳水 58g",0.42,"#84CC16"),("脂肪 18g",0.20,"#F59E0B")]
x=48
for lab,frac,col in macros:
    w=984*frac
    b.append(f'<Positioned left="{x:.1f}" top="370" width="{w:.1f}" height="46"><Container width="{w:.1f}" height="46" color="{col}" alignment="CENTER">'+T(lab,18,"#FFFFFF",True)+'</Container></Positioned>')
    x+=w
ing=["鹰嘴豆 200g","菠菜 80g","番茄 1 个","橄榄油 1 勺","柠檬汁 半个","孜然 少许"]
for i,it in enumerate(ing):
    b.append(f'<Positioned left="48" top="{460+i*54}">'+T("· "+it,22,"#2B3A2B")+'</Positioned>')
steps=["鹰嘴豆沥干，与孜然、橄榄油拌匀。","200°C 烤 12 分钟至边缘微焦。","菠菜与番茄切好，拌入柠檬汁。","趁热组合，撒一点盐。"]
for i,s in enumerate(steps):
    b.append(f'<Positioned left="520" top="{460+i*78}" width="500"><Row crossAxisAlignment="CENTER">'+T(f"0{i+1}",18,acc,True)+'<SizedBox width="10"/>'+T(s,20,"#334155")+'</Row></Positioned>')
b.append('<Positioned left="48" top="830"><Container width="984" height="120" color="#15803D" borderRadius="14" padding="20"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("搭配建议 / PAIR IT",15,"#DCFCE7",True,' letterSpacing="1"')+T("一份绿叶菜 + 柠檬水；若要更低脂，把橄榄油减半。",22,"#FFFFFF")+'</Column></Container></Positioned>')
cases.append(dict(id=8,slug="plate",W=W,H=H,title="Chickpea bowl · 一碗就够",sub="食谱卡 · 营养按每碗估算",brand="PLATE / RECIPE",body="".join(b),foot="Recipe card 08 · 自拟配方与营养估算",palette=[bg,acc]))
# 9 finance
W,H=1440,900; bg="#F7F4EE"; acc="#0F766E"
b=[f'<Positioned left="60" top="180"><Container width="620" height="160" color="#0B1220" borderRadius="18" padding="22"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("本月可用余额",18,"#94A3B8")+T("¥ 8,420.60",46,"#FFFFFF",True)+T("较上月 +¥ 1,240",18,"#5EEAD4")+'</Column></Container></Positioned>']
cats=[("居住",3200,0.72,"#0F766E"),("餐饮",1180,0.27,"#F59E0B"),("交通",420,0.10,"#2563EB"),("订阅",168,0.04,"#8B5CF6"),("其他",610,0.14,"#94A3B8")]
for i,(n,v,frac,col) in enumerate(cats):
    y=350+i*80
    b.append(f'<Positioned left="60" top="{y}">'+T(n,20,"#334155",True)+'</Positioned>')
    b.append(f'<Positioned left="160" top="{y+4}" width="{frac*700:.1f}" height="18"><Container width="{frac*700:.1f}" height="18" color="{col}" borderRadius="9"/></Positioned>')
    b.append(f'<Positioned left="900" top="{y}">'+T(f"¥ {v:,}",20,"#0B1220",True)+'</Positioned>')
b.append(f'<Positioned left="720" top="150"><Container width="660" height="640" color="#FFFFFF" borderRadius="18" border="1 SOLID #E7E1D7" padding="22"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("最近交易",22,"#0B1220",True))
tx=[("11.06","房租 −3,200","居住"),("11.06","超市 −186.40","餐饮"),("11.05","地铁充值 −100","交通"),("11.04","音乐订阅 −38","订阅"),("11.03","咖啡 −32","餐饮")]
for d,t,c in tx:
    b.append(f'<Row crossAxisAlignment="CENTER"><Container width="90">'+T(d,18,"#8896AB")+'</Container><Container width="360">'+T(t,20,"#334155")+'</Container><Container width="100">'+T(c,18,"#64748B")+'</Container></Row>')
b.append('</Column></Container></Positioned>')
cases.append(dict(id=9,slug="north",W=W,H=H,title="North · 十一月前三周",sub="个人现金流复盘 · 演示数据",brand="NORTH / MONEY",body="".join(b),foot="Money recap 09 · 演示数据",palette=[bg,acc]))
# 10 plant care
W,H=1080,1350; bg="#F2F6EF"; acc="#4D7C0F"
b=[]
weeks=["W1","W2","W3","W4","W5","W6","W7","W8","W9","W10","W11","W12"]
plants=[("龟背竹","💧 土干 3cm 浇透","明亮散射光"),("琴叶榕","💧 每周 1 次","旋转 90°"),("虎尾兰","💧 两周 1 次","耐阴")]
for pi,(name,water,light) in enumerate(plants):
    y=220+pi*280
    b.append(f'<Positioned left="48" top="{y}"><Container width="984" height="240" color="#FFFFFF" borderRadius="16" border="1 SOLID #DDE7D5" padding="20"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T(name,26,"#1F2A1A",True)+T(water+" · "+light,18,"#5B6B52")+'</Column></Container></Positioned>')
    for wi in range(12):
        x=80+wi*78; yy=y+100
        due=(wi+pi)%2==0
        b.append(f'<Positioned left="{x}" top="{yy}"><Container width="56" height="56" color="{"#4D7C0F" if due else "#EEF4E8"}" shape="CIRCLE" alignment="CENTER">'+T(weeks[wi],13,"#FFFFFF" if due else "#7A8A6F",True)+'</Container></Positioned>')
        if due: b.append(f'<Positioned left="{x+18}" top="{yy+58}"><Container width="20" height="8" color="#84CC16" borderRadius="4"/></Positioned>')
b.append('<Positioned left="48" top="1080">'+T("绿色圆 = 浇水周 · 圆点在一次浇透后 3 天检查土壤；冬季减半。",18,"#5B6B52")+'</Positioned>')
cases.append(dict(id=10,slug="bloom",W=W,H=H,title="Bloom · 十二周浇水卡",sub="三盆室内植物的轮换节奏 · 自拟养护建议",brand="BLOOM / PLANT CARE",body="".join(b),foot="Plant calendar 10 · 自拟养护建议",palette=[bg,acc]))
for c in cases:
    p=shell(c['W'],c['H'],c['palette'][0],c['palette'][1],c['title'],c['sub'],c['brand'],c['body'],c['foot'])
    d=OUT/f"case-{c['id']:02d}"; d.mkdir(parents=True,exist_ok=True)
    (d/'final.snapshot').write_text(p,encoding='utf-8')
    (d/'case.md').write_text(f"# {c['title']}\n\n- 场景：{c['brand']}\n- 受众/用途：见 portfolio.json\n- 主图：final.png（{c['W']}×{c['H']}），DSL：final.snapshot\n- 内容为自拟演示；数据/文案按画面一致。\n",encoding='utf-8')
print('B01 wrote',len(cases))
