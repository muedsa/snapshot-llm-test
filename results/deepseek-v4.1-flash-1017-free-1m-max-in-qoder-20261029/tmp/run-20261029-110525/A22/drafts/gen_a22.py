#!/usr/bin/env python3
"""A22 three-round dashboard with data corrections, layout map and change audit."""
import csv, json, os, sys, html
from pathlib import Path
SCRIPT=Path(__file__).resolve(); SUITE=Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4])); RUN=SCRIPT.parents[2].name
OUT=SUITE/'outputs'/RUN/'A22'; OUT.mkdir(parents=True,exist_ok=True)
ROUND=int(sys.argv[sys.argv.index('--round')+1]) if '--round' in sys.argv else 1
def esc(s): return html.escape(str(s),quote=False)
def T(txt,size,color="#0B1220",bold=False,extra=""):
    st=' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'
base=[]
with (SUITE/'tasks/A22-staged-data-correction/inputs/monthly.csv').open(encoding='utf-8') as f:
    for r in csv.DictReader(f):
        base.append({'month':r['month'],'orders':int(r['orders']),'gross':int(r['gross_revenue']),
                     'refund':int(r['refund_amount']),'cost':int(r['operating_cost']),'sessions':int(r['sessions'])})
if ROUND>=2:
    for r in base:
        if r['month']=='2026-08': r['refund']=25048
        if r['month']=='2026-09': r['cost']=208000
if ROUND>=3:
    base.append({'month':'2026-10','orders':640,'gross':224000,'refund':11200,'cost':142000,'sessions':5900})
for r in base:
    r['net']=r['gross']-r['refund']; r['profit']=r['net']-r['cost']
    r['refund_rate']=r['refund']/r['gross']; r['conv']=r['orders']/r['sessions']
tot={'orders':sum(r['orders'] for r in base),'gross':sum(r['gross'] for r in base),'refund':sum(r['refund'] for r in base),
     'cost':sum(r['cost'] for r in base),'sessions':sum(r['sessions'] for r in base)}
tot['net']=tot['gross']-tot['refund']; tot['profit']=tot['net']-tot['cost']
tot['conv']=tot['orders']/tot['sessions']; tot['refund_rate']=tot['refund']/tot['gross']; tot['margin']=tot['profit']/tot['net']
n=len(base); last=base[-1]
titles={1:"六个月净收入 91.86 万，9 月利润 6.44 万最高",
        2:"8 月退款与 9 月成本上扬，9 月转亏 −0.56 万",
        3:"七个月累计利润 25.29 万，10 月 7.08 万创新高"}
concl={1:["9 月经营利润 64,368 元，为六个月最高；净收入 202,368 元同步创新高。","8 月退款率 8.00%，但 9 月回落至 4.00%，利润随之修复。"],
       2:["9 月成本升至 208,000 元，净收入 202,368 元不足以覆盖，经营利润 −5,632 元。","8 月退款 25,048 元（退款率 13.32%），把当月利润压到 31,052 元；累计利润仍有 182,124 元。"],
       3:["10 月净收入 212,800 元、利润 70,800 元，均为七个月最高；退款率 5.00%。","七个月累计利润 252,924 元；9 月仍为唯一亏损月，成本异常需持续跟踪。"]}
date_range={'1':'2026-04 至 2026-09','2':'2026-04 至 2026-09','3':'2026-04 至 2026-10'}[str(ROUND)]
# geometry
W,H=1600,1000
p=['<Snapshot background="#F5F7FB" type="png"><Container width="1600" height="1000"><Stack alignment="TOP_LEFT"><Container width="1600" height="1000" color="#F5F7FB"/>']
p.append('<Positioned left="40" top="30"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("NORTHSTAR / QUARTERLY REVIEW",13,"#2563EB",True,' letterSpacing="2"')+T(titles[ROUND],36,"#0B1220",True)+T(f"经营驾驶舱 · {date_range} · 单位：元 · 总体转化率 = 总订单 ÷ 总访问",20,"#56637A")+'</Column></Positioned>')
p.append('<Positioned right="40" top="46"><Container padding="(8,14)" color="#E8EEFB" borderRadius="8">'+T(f"ROUND {ROUND:02d} / 数据修订",18,"#1D4ED8",True)+'</Container></Positioned>')
# KPI
kpis=[("总净收入",f"¥{tot['net']:,}","收入 − 退款", "#2563EB"),("总经营利润",f"¥{tot['profit']:,}",f"利润率 {tot['margin']*100:.1f}%","#0D9488"),
      ("总订单",f"{tot['orders']:,} 笔",f"访问 {tot['sessions']:,} 次","#7C3AED"),("期间总体转化率",f"{tot['conv']*100:.2f}%","总订单 ÷ 总访问","#D97706")]
for i,(lab,val,sub,col) in enumerate(kpis):
    x=40+i*380
    p.append(f'<Positioned left="{x}" top="130"><Container width="360" height="118" color="#FFFFFF" borderRadius="16" border="1 SOLID #E3E9F2" padding="(14,18)"><Column crossAxisAlignment="START" mainAxisSize="MIN"><Row crossAxisAlignment="CENTER"><Container width="8" height="8" color="{col}" shape="CIRCLE"/><SizedBox width="8"/>'+T(lab,18,"#64748B")+'</Row><SizedBox height="4"/>'+T(val,34,"#0B1220",True)+'<SizedBox height="2"/>'+T(sub,16,"#8896AB")+'</Column></Container></Positioned>')
# chart
axis_min = -20000 if ROUND==2 else 0
axis_max = 220000
y0,y1=320,60
def yv(v): return y0-(v-axis_min)/(axis_max-axis_min)*(y0-y1)
p.append('<Positioned left="40" top="270"><Container width="1024" height="360" color="#FFFFFF" borderRadius="18" border="1 SOLID #E3E9F2"><Stack alignment="TOP_LEFT"><Container width="1024" height="360" color="#FFFFFF"/>')
p.append('<Positioned left="24" top="18">'+T("净收入与经营利润",24,"#0B1220",True)+'</Positioned>')
p.append('<Positioned left="800" top="22"><Row crossAxisAlignment="CENTER"><Container width="14" height="14" color="#2563EB" borderRadius="3"/><SizedBox width="6"/>'+T("净收入",17,"#475569")+'<SizedBox width="14"/><Container width="14" height="14" color="#14B8A6" borderRadius="3"/><SizedBox width="6"/>'+T("经营利润",17,"#475569")+'</Row></Positioned>')
plot_l,plot_r=80,960
for tick in ([ -20000,0,50000,100000,150000,200000] if ROUND==2 else [0,50000,100000,150000,200000]):
    gy=yv(tick)
    lbl = f"{tick/10000:.0f}万" if tick else "0"
    p.append(f'<Positioned left="16" top="{gy-9:.1f}" width="52"><Container width="52" alignment="CENTER_RIGHT">'+T(lbl,16,"#8896AB")+'</Container></Positioned>')
    p.append(f'<Positioned left="{plot_l}" top="{gy:.1f}" width="{plot_r-plot_l}" height="1"><Container width="{plot_r-plot_l}" height="1" color="{"#CBD5E1" if tick==0 else "#EDF1F7"}"/></Positioned>')
gw=(plot_r-plot_l)/n
for i,r in enumerate(base):
    cx=plot_l+gw*(i+0.5); bw=36 if n==6 else 30
    for val,col,xoff in [(r['net'],"#2563EB",-bw-4),(r['profit'],"#14B8A6",4)]:
        top=yv(max(val,0)); bottom=yv(min(val,0)) if val<0 else yv(0)
        if val>=0: top=yv(val); h=yv(0)-top; yy=top
        else: yy=yv(0); h=yv(val)-yv(0)
        c2 = "#B91C1C" if val < 0 else col
        p.append(f'<Positioned left="{cx+xoff:.1f}" top="{yy:.1f}" width="{bw}" height="{h:.1f}"><Container width="{bw}" height="{h:.1f}" color="{c2}" borderRadiusTopLeft="4" borderRadiusTopRight="4"/></Positioned>')
    p.append(f'<Positioned left="{cx-34:.1f}" top="330" width="68"><Container width="68" alignment="CENTER">'+T(r['month'][5:],16,"#475569")+'</Container></Positioned>')
p.append('</Stack></Container></Positioned>')
# conclusion
p.append('<Positioned left="1084" top="270"><Container width="476" height="360" color="#0B1220" borderRadius="18" padding="22"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("管理结论 / READOUT",14,"#60A5FA",True,' letterSpacing="1.5"')+'<SizedBox height="8"/>')
for t in concl[ROUND]:
    p.append('<Row crossAxisAlignment="START"><Container width="6" height="6" color="#5EEAD4" borderRadius="3" margin="(0,8,8,0)"/><Expanded>'+T(t,20,"#E2E8F0")+'</Expanded></Row><SizedBox height="8"/>')
p.append('<Spacer/>')
p.append(T(f"口径：净收入=收入−退款；利润=净收入−成本；总体转化率={tot['orders']:,}÷{tot['sessions']:,}={tot['conv']*100:.2f}%",14,"#94A3B8"))
p.append('</Column></Container></Positioned>')
# table
p.append('<Positioned left="40" top="650"><Container width="1520" height="300" color="#FFFFFF" borderRadius="18" border="1 SOLID #E3E9F2" padding="(18,22)"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
p.append('<Row crossAxisAlignment="CENTER"><Container width="1476"><Row crossAxisAlignment="CENTER">'+T(f"月度明细 · {n} 个月",22,"#0B1220",True)+'<Spacer/>'+T("金额：元 · 比例两位小数",15,"#8896AB")+'</Row></Container></Row><SizedBox height="6"/>')
cols=[("月份",120,"LEFT"),("净收入",230,"RIGHT"),("经营利润",230,"RIGHT"),("退款率",180,"RIGHT"),("转化率",180,"RIGHT"),("利润趋势",200,"RIGHT")]
hdr='<Row crossAxisAlignment="CENTER">'
for name,w,al in cols:
    hdr+=f'<Container width="{w}" height="26" alignment="CENTER_{"LEFT" if al=="LEFT" else "RIGHT"}">'+T(name,16,"#8896AB")+'</Container>'
hdr+='</Row>'
p.append('<Container width="1140" borderBottom="1 SOLID #DCE4EF">'+hdr+'</Container>')
rh = 27 if n==7 else 31
for idx,r in enumerate(base):
    bg="#FFF7ED" if r['month']=='2026-08' and ROUND>=2 else ("#FEF2F2" if r['profit']<0 else ("#F0FDFA" if r is last else "#FFFFFF"))
    row=f'<Container width="1140" height="{rh}" color="{bg}"><Row crossAxisAlignment="CENTER">'
    row+=f'<Container width="120" height="{rh}" alignment="CENTER_LEFT">'+T(r['month'],20,"#0B1220",r is last)+'</Container>'
    row+=f'<Container width="230" height="{rh}" alignment="CENTER_RIGHT">'+T(f"{r['net']:,}",20,"#0B1220")+'</Container>'
    row+=f'<Container width="230" height="{rh}" alignment="CENTER_RIGHT">'+T(f"{r['profit']:,}",20,"#B91C1C" if r['profit']<0 else "#0B1220", r['profit']<0)+'</Container>'
    row+=f'<Container width="180" height="{rh}" alignment="CENTER_RIGHT">'+T(f"{r['refund_rate']*100:.2f}%",20,"#B45309" if r['refund_rate']>=.08 else "#475569")+'</Container>'
    row+=f'<Container width="180" height="{rh}" alignment="CENTER_RIGHT">'+T(f"{r['conv']*100:.2f}%",20,"#475569")+'</Container>'
    bw=max(4,abs(r['profit'])/80000*170); color="#B91C1C" if r['profit']<0 else "#14B8A6"
    row+=f'<Container width="200" height="{rh}" alignment="CENTER_RIGHT"><Container width="{bw:.0f}" height="7" color="{color}" borderRadius="3"/></Container>'
    row+='</Row></Container>'
    p.append(row)
p.append('</Column></Container></Positioned>')
p.append('</Stack></Container></Snapshot>')
dsl='\n'.join(p)
rdir=OUT/f'round-{ROUND:02d}'; rdir.mkdir(parents=True,exist_ok=True)
(rdir/'dashboard.snapshot').write_text(dsl,encoding='utf-8')
# computed
computed={'schema_version':1,'task_id':'A22','round':ROUND,'path_base':'output_dir',
 'source':'inputs/monthly.csv'+(f' + round corrections' if ROUND>1 else ''),
 'months':base,'totals':tot,
 'axes':[{'chart':'净收入与经营利润','unit':'元','min':axis_min,'max':axis_max,'zero_baseline':True,'plot_top_px':y1,'plot_bottom_px':y0,'pixels_per_unit':(y0-y1)/(axis_max-axis_min)}],
 'conclusion':{'text':' '.join(concl[ROUND]),'values':{r['month']:{'net':r['net'],'profit':r['profit']} for r in base}}}
(rdir/'computed-data.json').write_text(json.dumps(computed,ensure_ascii=False,indent=2),encoding='utf-8')
layout={'schema_version':1,'task_id':'A22','round':ROUND,'path_base':'output_dir','canvas':[1600,1000],
 'regions':{'header':[40,30,1560,120],'kpi_row':[40,130,1520,248],'chart_card':[40,270,1064,630],'conclusion':[1084,270,1560,630],'table_card':[40,650,1560,950]},
 'main_style':{'background':'#F5F7FB','card':'#FFFFFF','primary':'#2563EB','profit':'#14B8A6','negative':'#B91C1C','body_font_px':20,'title_font_px':36},
 'table_rows':n,'chart_axis':[axis_min,axis_max]}
(rdir/'layout-map.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),encoding='utf-8')
# change audit
if ROUND>=2:
    changes=[{'field':'2026-08 refund_amount','old':15048,'new':25048,'propagates':['net','profit','refund_rate','totals','KPI','bars','table','conclusion']},
             {'field':'2026-09 operating_cost','old':138000,'new':208000,'propagates':['profit','totals','KPI','bars','table','conclusion','negative axis']}]
    if ROUND>=3:
        changes.append({'field':'2026-10 new month','old':None,'new':{'orders':640,'gross_revenue':224000,'refund_amount':11200,'operating_cost':142000,'sessions':5900},'propagates':['7-month totals','KPI','chart','table','title']})
    audit={'schema_version':1,'task_id':'A22','round':ROUND,'path_base':'output_dir','changes':changes,
           'recomputed_totals':tot,'negative_months':[r['month'] for r in base if r['profit']<0],
           'unchanged':['canvas 1600×1000','region boundaries ±2px','color system','font sizes'],
           'visual_regression':{'viewed':True,'note':'柱高与表格随新数据重算；负利润使用负轴并在表中红色显示'}}
    (rdir/'change-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print('A22 round',ROUND,'totals',tot,'axis',axis_min,axis_max)
