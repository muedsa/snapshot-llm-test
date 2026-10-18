"""B06 · ten everyday information redesigns."""
from __future__ import annotations
import math, os, sys
from pathlib import Path
ROOT=Path(os.environ.get("SNAPSHOT_TASK_ROOT",".")).resolve(); RUN=os.environ["SNAPSHOT_RUN_ID"]; TASK="B06"
VERSION=sys.argv[1] if len(sys.argv)>1 else "v001"; TMP=ROOT/"tmp"/RUN/TASK
sys.path.insert(0,str(ROOT/"tmp"/RUN/"_suite"/"scripts")); sys.path.insert(0,str(ROOT/"tmp"/RUN/"B02"/"scripts"))
from dsl import C, Pos, SizedBox, Stack, T  # noqa: E402
from b02_build import rot, seg, dot, base  # noqa: E402
F="Inter,Noto Sans CJK SC"; S="Noto Serif CJK SC,Noto Sans CJK SC"; M="Noto Sans Mono CJK SC,Inter"


def case01():
    W,H=900,1200; bg="#F7F2E4"; ink="#18332A"; green="#3C7A5A"; red="#B84A3A"
    n=[Pos(0,0,C(width=W,height=H,color=bg)),Pos(0,0,C(width=W,height=14,color=green)),
       Pos(40,40,T("处方药 · 重做标签",size=13,color=green,weight="BOLD",family=M,spacing=2)),
       Pos(40,78,T("氨氯地平 5mg",size=50,color=ink,weight="BOLD",family=S)),
       Pos(40,144,T("降压药 · 每天 3 次 · 每次 1 片",size=19,color="#53665C",family=F)),
       Pos(40,210,T("一天怎么吃",size=22,color=ink,weight="BOLD",family=F))]
    times=[("08:00","早","随餐","1 片",green),("13:00","中","随餐","1 片","#C68A2E"),("20:00","晚","空腹","1 片","#3E6E8E")]
    for i,(t,lab,meal,dose,c) in enumerate(times):
        x=40+i*280
        n += [Pos(x,250,C(width=260,height=270,color="#FFFFFF",borderRadius=14,border="1 SOLID #DDD3C2")),
              Pos(x+20,270,T(lab,size=18,color=c,weight="BOLD",family=F)),Pos(x+20,300,T(t,size=44,color=ink,weight="BOLD",family=M)),
              Pos(x+20,360,T(meal,size=22,color=ink,family=F)),Pos(x+20,396,T(dose,size=22,color=ink,family=F)),
              dot(x+220,300,26,"#FFFFFF",f"3 SOLID {c}"),(dot(x+220,300,10,c) if i==0 else "")]
    n += [Pos(40,560,C(width=820,height=140,color="#FBEAE5",borderRadius=14,border="1 SOLID #E4B7A9")),
          Pos(60,580,T("漏服怎么办",size=17,color=red,weight="BOLD",family=F)),
          Pos(60,610,T("想起时距下次服药 >6 小时：补 1 片；≤6 小时：跳过。\n不要一次吃两片。",size=18,color=ink,family=F,height="1.5"),w=760,h=70),
          Pos(40,740,T("这盒还剩",size=15,color="#53665C",family=F)),
          Pos(40,766,T("18 片 / 21 片",size=38,color=green,weight="BOLD",family=M)),
          Pos(40,830,C(width=820,height=2,color="#D7CCB9")),
          Pos(40,860,T("什么时候找医生",size=17,color=ink,weight="BOLD",family=F)),
          Pos(40,892,T("脚踝明显水肿 · 头晕站不稳 · 血压 <90/60 · 心跳很慢",size=18,color=ink,family=F)),
          Pos(40,960,T("不要因为“感觉好了”自行停药。",size=18,color=red,family=F)),
          Pos(40,1080,T("演示药盒 · 非真实处方 · 用药请遵医嘱",size=12,color="#8A8578",family=M))]
    return base(W,H,bg,n)


def case02():
    W,H=1200,1600; bg="#FFFFFF"; ink="#1B2A33"; blue="#2F6F8F"; coral="#D05A3F"
    n=[Pos(0,0,C(width=W,height=H,color=bg)),Pos(0,0,C(width=W,height=12,color=blue)),
       Pos(56,44,T("NORTHSTAR POWER / 11 月账单",size=13,color=blue,weight="BOLD",family=M,spacing=2)),
       Pos(56,80,T("本月电费",size=30,color="#5E6D76",family=F)),
       Pos(56,120,T("¥286.40",size=86,color=ink,weight="BOLD",family=M)),
       Pos(56,230,T("比上月多 ¥38.20",size=24,color=coral,weight="BOLD",family=F)),
       Pos(56,270,T("主要因为取暖用电增加 62 kWh；单价未变。",size=18,color="#5E6D76",family=F))]
    # usage bars
    n += [Pos(56,340,T("用电量（kWh）",size=15,color="#5E6D76",family=F))]
    for i,(m,v) in enumerate([("9月",210),("10月",238),("11月",300)]):
        x=80+i*300; h=v*1.2
        n += [Pos(x,800-h,C(width=160,height=h,color="#A9CFDE" if i<2 else blue,borderRadius=10)),
              Pos(x,820,T(m,size=17,color=ink,family=F)),Pos(x,846,T(str(v),size=20,color=ink,weight="BOLD",family=M))]
    # line items
    n += [Pos(56,900,T("钱花在哪",size=20,color=ink,weight="BOLD",family=F)),
          Pos(56,940,C(width=1088,height=1,color="#DDE3E5"))]
    rows=[("电费 300 kWh × ¥0.82",246.00),("电网输送费",28.40),("政府附加费",12.00)]
    y=960
    for lab,val in rows:
        n += [Pos(56,y,T(lab,size=18,color=ink,family=F)),Pos(980,y,T(f"¥{val:.2f}",size=18,color=ink,family=M))]
        y+=42
    n += [Pos(56,1100,C(width=1088,height=2,color=ink)),
          Pos(56,1120,T("合计",size=22,color=ink,weight="BOLD",family=F)),Pos(940,1118,T("¥286.40",size=26,color=ink,weight="BOLD",family=M)),
          Pos(56,1190,T("如果想少付",size=20,color=coral,weight="BOLD",family=F)),
          Pos(56,1226,T("把恒温器调低 1°C，预计每月省 6–8%；\n或申请分时电价（22:00 后洗衣/充电）。",size=18,color=ink,family=F,height="1.5"),w=1000,h=80),
          Pos(56,1340,T("客服 6688 · 账单异议 30 天内提出",size=14,color="#5E6D76",family=F)),
          Pos(56,1480,T("演示账单 · 非真实供电合同",size=11,color="#8A969C",family=M))]
    return base(W,H,bg,n)


def case03():
    W,H=1200,1600; bg="#F3ECDF"; ink="#2A2118"; rust="#A64B2A"
    n=[Pos(0,0,C(width=W,height=H,color=bg)),
       Pos(48,40,T("RENT / ONE-PAGE LEASE",size=13,color=rust,weight="BOLD",family=M,spacing=2)),
       Pos(48,78,T("租约一页纸",size=48,color=ink,weight="BOLD",family=S)),
       Pos(48,144,T("先看钱、日期、维修、退出；其他条款再慢慢读。",size=19,color="#655746",family=F))]
    blocks=[("钱",["月租 ¥4,200","押金 ¥8,400（2 个月）","涨租：每年 ≤5%","水电燃气：租客付"],rust),
            ("日期",["起租 2026.12.01","退租通知：提前 30 天","续租答复：到期前 60 天","每年 3 月年检"],"#2E6B5A"),
            ("维修",["24h 内报修漏水/断电","非人为损坏：房东修","换锁/养宠：书面同意","紧急维修可先修后报"],"#3E5F7A"),
            ("退出",["押金 14 天内退","扣款需列明细","转租：书面同意","提前解约：1 个月租金"],"#9A6A2E")]
    for i,(t,items,c) in enumerate(blocks):
        x=48+(i%2)*550; y=220+(i//2)*330
        n += [Pos(x,y,C(width=510,height=290,color="#FFFFFF",borderRadius=12,border="1 SOLID #D8CBB6")),
              Pos(x,y,C(width=8,height=290,color=c,borderRadius=4)),
              Pos(x+24,y+18,T(t,size=34,color=c,weight="BOLD",family=S))]
        for j,it in enumerate(items):
            n += [dot(x+34,y+78+j*48,8,c),Pos(x+52,y+68+j*48,T(it,size=17,color=ink,family=F))]
    n += [Pos(48,920,T("关键日期",size=20,color=rust,weight="BOLD",family=F))]
    dates=[("12.01","起租/交钥匙"),("02.01","第一次涨租告知"),("10.31","续租答复截止"),("11.01","退租通知最后一天")]
    for i,(d,lab) in enumerate(dates):
        x=90+i*270
        n += [dot(x,990,14,rust),Pos(x-30,1012,T(d,size=17,color=ink,weight="BOLD",family=M)),Pos(x-30,1042,T(lab,size=15,color="#655746",family=F))]
        if i<3: n.append(seg(x+8,990,x+262,990,"#C8B9A3",2))
    n += [Pos(48,1120,T("签字前拍照",size=18,color=ink,weight="BOLD",family=F)),
          Pos(48,1152,T("墙面/地板/家电现有瑕疵 + 水表电表读数；\n把口头承诺写进补充条款。",size=18,color="#655746",family=F,height="1.5"),w=1000,h=80),
          Pos(48,1460,T("演示租约摘要 · 非法律意见；以正式合同为准",size=11,color="#8A7B66",family=M))]
    return base(W,H,bg,n)


def case04():
    W,H=1200,1600; bg="#F5F7F5"; ink="#182521"; blue="#2E5C7A"; green="#3C7A5A"; coral="#C24E3A"
    n=[Pos(0,0,C(width=W,height=H,color=bg)),Pos(0,0,C(width=W,height=12,color=blue)),
       Pos(56,44,T("INSURANCE / EXPLANATION OF BENEFITS",size=12,color=blue,weight="BOLD",family=M,spacing=2)),
       Pos(56,82,T("医院收 ¥1,280",size=46,color=ink,weight="BOLD",family=S)),
       Pos(56,146,T("保险付 ¥960 · 你付 ¥100",size=30,color=green,weight="BOLD",family=F))]
    # stacked bar
    n += [Pos(56,230,C(width=1088,height=74,color="#E4E9E6",borderRadius=10)),
          Pos(56,230,C(width=985,height=74,color=blue,borderRadius=10)),
          Pos(1041,230,C(width=103,height=74,color=coral,borderRadius=10)),
          Pos(80,252,T("保险 ¥960",size=20,color="#FFFFFF",weight="BOLD",family=M)),
          Pos(1050,252,T("你 ¥100",size=15,color="#FFFFFF",weight="BOLD",family=M))]
    rows=[("医院原价",1280,""),("网络内折扣",-220,"保险谈下来的"),("保险允许金额",1060,""),("保险支付",-960,""),("你的自付",100,"允许金额 − 保险支付")]
    y=350
    for lab,val,note in rows:
        n += [Pos(56,y,T(lab,size=19,color=ink,family=F)),
              Pos(760,y,T(("−" if val<0 else "")+f"¥{abs(val):,}",size=19,color=blue if val<0 else ink,weight="BOLD",family=M)),
              Pos(940,y,T(note,size=14,color="#6D7A73",family=F))]
        y+=62
    n += [Pos(56,780,C(width=1088,height=2,color=ink)),
          Pos(56,800,T("合计你付",size=22,color=ink,weight="BOLD",family=F)),
          Pos(820,796,T("¥100",size=38,color=coral,weight="BOLD",family=M)),
          Pos(56,880,T("如果不对",size=20,color=coral,weight="BOLD",family=F)),
          Pos(56,916,T("1  核对服务日期/项目是否实际发生\n2  问清“网络内”与“免赔额”\n3  60 天内提交申诉，附账单与病历",size=19,color=ink,family=F,height="1.65"),w=1000,h=140),
          Pos(56,1100,C(width=1088,height=120,color="#EAF0EC",borderRadius=12)),
          Pos(80,1120,T("一句话",size=13,color=green,weight="BOLD",family=F)),
          Pos(80,1146,T("“保险允许金额”不是医院原价；你付的是允许金额 − 保险支付，\n不是简单的 10% × 1,280。",size=18,color=ink,family=F,height="1.5"),w=1000,h=70),
          Pos(56,1480,T("演示 EOB · 非真实保单；以保险公司正式文件为准",size=11,color="#8A9690",family=M))]
    return base(W,H,bg,n)


def case05():
    W,H=1200,1600; bg="#E9F0E6"; ink="#1D3324"; green="#2E6B4A"; amber="#C68A2E"
    n=[Pos(0,0,C(width=W,height=H,color=bg)),Pos(0,0,C(width=W,height=14,color=green)),
       Pos(56,44,T("TRANSIT / FARE BY ORIGIN–DESTINATION",size=12,color=green,weight="BOLD",family=M,spacing=2)),
       Pos(56,82,T("从 A 到 B，多少钱？",size=46,color=ink,weight="BOLD",family=S)),
       Pos(56,146,T("不用先研究分区；选起终点，直接看票价。",size=19,color="#4E6355",family=F))]
    stops=["北门","市场","河湾","东站"]
    n += [Pos(56,230,T("起 \\ 终",size=15,color="#4E6355",family=F))]
    for j,s in enumerate(stops): n.append(Pos(300+j*210,230,T(s,size=17,color=ink,weight="BOLD",family=F)))
    fares=[[2,2,3,4],[2,2,2,3],[3,2,2,2],[4,3,2,2]]
    for i,s in enumerate(stops):
        y=280+i*150
        n.append(Pos(56,y+34,T(s,size=19,color=ink,weight="BOLD",family=F)))
        for j,f in enumerate(fares[i]):
            c="#FFFFFF" if i!=j else "#DCE8D8"
            n += [Pos(280+j*210,y,C(width=180,height=90,color=c,borderRadius=10,border="1 SOLID #C4D6C0")),
                  Pos(280+j*210+58,y+26,T("—" if i==j else f"¥{f}",size=26,color=green if i!=j else "#8A9C8C",weight="BOLD",family=M))]
    n += [Pos(56,900,C(width=1088,height=150,color="#FFFFFF",borderRadius=12)),
          Pos(80,920,T("90 分钟内换乘",size=18,color=amber,weight="BOLD",family=F)),
          Pos(80,952,T("同方向连续乘坐只算一次；跨方向重新计费。",size=17,color=ink,family=F)),
          Pos(80,986,T("儿童 <1.2m 免费 · 刷卡/手机同价",size=15,color="#4E6355",family=F)),
          Pos(56,1100,T("为什么原来的分区图难用",size=18,color=green,weight="BOLD",family=F)),
          Pos(56,1134,T("因为你要同时看颜色、边界、换乘线和“跨区加价”。\n重做后，只保留起点 × 终点。",size=18,color=ink,family=F,height="1.5"),w=1000,h=70),
          Pos(56,1480,T("演示票价 · 非真实运营方",size=11,color="#8A9C8C",family=M))]
    return base(W,H,bg,n)


def case06():
    W,H=1200,1600; bg="#F6EDDD"; ink="#33251A"; red="#B84A35"; green="#4F7A4A"
    n=[Pos(0,0,C(width=W,height=H,color=bg)),Pos(0,0,C(width=W,height=14,color=red)),
       Pos(56,44,T("RECIPE / 15 MINUTES",size=13,color=red,weight="BOLD",family=M,spacing=2)),
       Pos(56,82,T("番茄鸡蛋面",size=50,color=ink,weight="BOLD",family=S)),
       Pos(56,150,T("2 人份 · 15 分钟 · 一口锅 + 一个碗",size=19,color="#6B5948",family=F))]
    steps=[("0–3","烧水 / 切番茄","水 1.2L 煮沸；番茄切块，鸡蛋打散。",red),
           ("3–7","炒蛋 / 出汁","油热下蛋，凝固即盛出；番茄炒到出汁。",green),
           ("7–11","煮面 / 合锅","面煮 3 分钟；把蛋回锅，加盐/糖。","#C68A2E"),
           ("11–15","装碗 / 收尾","尝咸淡；葱花/香油可选。关火再盛。","#3E5F7A")]
    for i,(t,title,body,c) in enumerate(steps):
        y=230+i*210
        n += [Pos(56,y,C(width=1088,height=180,color="#FFFFFF",borderRadius=12,border="1 SOLID #DCCDB8")),
              Pos(56,y,C(width=10,height=180,color=c,borderRadius=5)),
              Pos(84,y+20,T(t,size=18,color=c,weight="BOLD",family=M)),
              Pos(84,y+52,T(title,size=26,color=ink,weight="BOLD",family=F)),
              Pos(84,y+94,T(body,size=18,color="#6B5948",family=F))]
    n += [Pos(56,1120,T("食材",size=18,color=red,weight="BOLD",family=F)),
          Pos(56,1152,T("面条 200g · 番茄 2 个 · 鸡蛋 2 个\n盐 2g · 糖 3g · 油 10g · 葱花少许",size=19,color=ink,family=F,height="1.6"),w=1000,h=80),
          Pos(56,1270,T("别烧糊",size=18,color=red,weight="BOLD",family=F)),
          Pos(56,1302,T("水开后转中火；面下锅后设 3 分钟计时。\n番茄出汁前不要加盐。",size=18,color=ink,family=F,height="1.5"),w=1000,h=80),
          Pos(56,1480,T("演示菜谱 · 可按口味调整",size=11,color="#8A7B66",family=M))]
    return base(W,H,bg,n)


def case07():
    W,H=1600,1000; bg="#F4F0E5"; ink="#1D2B26"; blue="#2E5C7A"; coral="#C24E3A"; green="#2E6B4A"
    n=[Pos(0,0,C(width=W,height=H,color=bg)),Pos(0,0,C(width=W,height=12,color=blue)),
       Pos(40,32,T("RIVERSIDE SCHOOL / FAMILY CALENDAR",size=12,color=blue,weight="BOLD",family=M,spacing=2)),
       Pos(40,68,T("两个孩子的关键日期",size=42,color=ink,weight="BOLD",family=S)),
       Pos(40,124,T("先看红线，再看灰字；不需要逐条读通知。",size=18,color="#5C6A62",family=F))]
    months=["9","10","11","12","1","2","3","4","5","6"]
    n += [Pos(40,180,T("孩子",size=13,color="#5C6A62",family=F))]
    for i,m in enumerate(months): n.append(Pos(300+i*122,180,T(m+"月",size=15,color=ink,weight="BOLD",family=F)))
    rows=[("小满 · 三年级",["开学","","考试","","寒假","","春游","","考试",""]),
          ("小禾 · 一年级",["","缴费","","演出","寒假","","体检","","","放假"])]
    for r,(name,events) in enumerate(rows):
        y=220+r*260
        n += [Pos(40,y+90,T(name,size=18,color=ink,weight="BOLD",family=F)),
              Pos(40,y+122,T("家长会 / 缴费 / 放假",size=13,color="#5C6A62",family=F))]
        for i,e in enumerate(events):
            x=300+i*122
            n.append(Pos(x,y,C(width=112,height=230,color="#FFFFFF" if (i%2==0) else "#FAF7EE",borderRadius=8,border="1 SOLID #DDD4C3")))
            if e:
                c=coral if e in ("考试","缴费","家长会") else green
                n += [Pos(x+10,y+14,C(width=92,height=40,color=c,borderRadius=6)),
                      Pos(x+18,y+24,T(e,size=15,color="#FFFFFF",weight="BOLD",family=F))]
    n += [Pos(40,780,T("图例",size=14,color="#5C6A62",weight="BOLD",family=F)),
          Pos(80,806,C(width=18,height=18,color=coral)),Pos(106,806,T("考试/缴费",size=14,color=ink,family=F)),
          Pos(220,806,C(width=18,height=18,color=green)),Pos(246,806,T("活动/假期",size=14,color=ink,family=F)),
          Pos(40,880,T("RIVERSIDE SCHOOL · 2026–27 演示校历 · 以学校正式通知为准",size=11,color="#8A8578",family=M))]
    return base(W,H,bg,n)


def case08():
    W,H=900,1200; bg="#1E2A32"; ink="#F4F1E8"; green="#3FAE6A"; red="#D9534F"; amber="#E0A93B"
    n=[Pos(0,0,C(width=W,height=H,color=bg)),
       Pos(40,36,T("PARKING / NOW",size=13,color=amber,weight="BOLD",family=M,spacing=2)),
       Pos(40,74,T("现在能停吗？",size=48,color=ink,weight="BOLD",family=S)),
       Pos(40,140,T("周二 14:00 · 北门路 12 号",size=20,color="#B9C5CC",family=F))]
    n += [Pos(40,210,C(width=820,height=180,color=green,borderRadius=16)),
          Pos(70,232,T("可以停",size=58,color="#FFFFFF",weight="BOLD",family=F)),
          Pos(70,306,T("剩余 1 小时 30 分 · 2 元/30 分钟",size=20,color="#E7F5EC",family=F)),
          Pos(690,246,T("P",size=100,color="#FFFFFF",weight="BOLD",family=M))]
    rules=[("周一至周五","07:00–19:00","收费 2 元/30 分；无居民证限停 2 小时",amber),
           ("周六","09:00–13:00","免费 2 小时；之后 3 元/小时",green),
           ("周日/法定假日","全天","免费；禁止货车停放",green),
           ("任何时间","消防通道/斑马线","禁止停车，拖车",red)]
    n += [Pos(40,430,T("规则",size=18,color=amber,weight="BOLD",family=F))]
    for i,(when,time,rule,c) in enumerate(rules):
        y=470+i*120
        n += [Pos(40,y,C(width=820,height=100,color="#2A383F",borderRadius=12,border="1 SOLID #40515A")),
              Pos(60,y+16,T(when,size=18,color=ink,weight="BOLD",family=F)),
              Pos(300,y+16,T(time,size=16,color=c,family=M)),
              Pos(60,y+54,T(rule,size=16,color="#C4D0D5",family=F))]
    n += [Pos(40,980,T("为什么原来的牌子难读",size=15,color=amber,weight="BOLD",family=F)),
          Pos(40,1010,T("五个箭头、三种例外、两个“除外”，要站在路边做逻辑题。\n先给结论，再给条件。",size=16,color="#C4D0D5",family=F,height="1.5"),w=800,h=60),
          Pos(40,1120,T("演示停车牌 · 非真实路段",size=11,color="#7C8C94",family=M))]
    return base(W,H,bg,n)


def case09():
    W,H=900,1200; bg="#FFFFFF"; ink="#1D2A22"; red="#C24E3A"; amber="#C68A2E"; green="#2E6B4A"
    n=[Pos(0,0,C(width=W,height=H,color=bg)),
       Pos(40,36,T("NUTRITION / FRONT OF PACK",size=12,color=green,weight="BOLD",family=M,spacing=2)),
       Pos(40,74,T("整包吃下去，\n到底多少？",size=42,color=ink,weight="BOLD",family=S,height="1.25"),w=700,h=110),
       Pos(40,210,T("每份 40g · 整包 3 份",size=20,color="#55655B",family=F))]
    # two columns
    cols=[("每份 40g","1 份",["能量 190 kcal","糖 6 g","添加糖 4 g","钠 180 mg","蛋白质 4 g"],"#F4F1E8"),
          ("整包 120g","3 份",["能量 570 kcal","糖 18 g","添加糖 12 g","钠 540 mg","蛋白质 12 g"],"#FBEAE5")]
    for i,(head,sub,items,c) in enumerate(cols):
        x=40+i*420
        n += [Pos(x,270,C(width=390,height=330,color=c,borderRadius=14,border="1 SOLID #DDD3C2")),
              Pos(x+20,288,T(head,size=22,color=ink,weight="BOLD",family=F)),
              Pos(x+20,320,T(sub,size=13,color="#55655B",family=F))]
        for j,it in enumerate(items):
            n += [Pos(x+20,352+j*44,T(it,size=17,color=ink,family=F))]
    n += [Pos(40,640,T("一眼看懂",size=18,color=green,weight="BOLD",family=F))]
    flags=[("糖 18g","一份 6g × 3","amber"),("添加糖 12g","占每日上限 24%","red"),("钠 540mg","占每日上限 27%","amber")]
    for i,(v,lab,c) in enumerate(flags):
        y=680+i*100
        n += [Pos(40,y,C(width=820,height=80,color="#F7F4EC",borderRadius=10)),
              dot(84,y+40,42,red if c=="red" else amber),Pos(120,y+14,T(v,size=22,color=ink,weight="BOLD",family=F)),
              Pos(120,y+46,T(lab,size=13,color="#55655B",family=F))]
    n += [Pos(40,1040,T("每日参考上限：添加糖 50g / 钠 2000mg（成人，演示）",size=14,color="#55655B",family=F)),
          Pos(40,1100,T("重做：先给整包，再给每份；不靠小字 %DV。",size=14,color=green,family=F)),
          Pos(40,1140,T("演示营养标签 · 非真实产品",size=11,color="#8A8578",family=M))]
    return base(W,H,bg,n)


def case10():
    W,H=1200,1600; bg="#F5F3EA"; ink="#1E2B25"; blue="#2E5C7A"; green="#2E6B4A"; coral="#C24E3A"
    n=[Pos(0,0,C(width=W,height=H,color=bg)),Pos(0,0,C(width=W,height=12,color=blue)),
       Pos(56,44,T("TAX / FIRST-TIME FILER",size=12,color=blue,weight="BOLD",family=M,spacing=2)),
       Pos(56,82,T("先回答 5 个问题",size=46,color=ink,weight="BOLD",family=S)),
       Pos(56,148,T("不用先读 40 页说明；答案会决定你填哪张表。",size=19,color="#5E6D62",family=F))]
    qs=[("1","去年有工作收入吗？","有 / 没有 → 是否需要工资单"),("2","有房租/房贷利息吗？","有 → 准备年度利息单"),("3","有孩子/赡养老人吗？","有 → 可能需要家庭扣除"),("4","有自由职业/平台收入吗？","有 → 记录流水与成本"),("5","去年买过医保吗？","有 → 准备保费凭证")]
    for i,(num,q,a) in enumerate(qs):
        y=220+i*150
        n += [Pos(56,y,C(width=1088,height=120,color="#FFFFFF",borderRadius=12,border="1 SOLID #D9D2C3")),
              dot(94,y+60,40,blue),Pos(82,y+46,T(num,size=18,color="#FFFFFF",weight="BOLD",family=M)),
              Pos(140,y+18,T(q,size=21,color=ink,weight="BOLD",family=F)),
              Pos(140,y+54,T(a,size=16,color="#5E6D62",family=F))]
    n += [Pos(56,1000,T("带什么",size=18,color=green,weight="BOLD",family=F)),
          Pos(56,1032,T("身份证 · 工资单/银行流水 · 房租或房贷利息单\n医保保费凭证 · 子女/赡养信息",size=18,color=ink,family=F,height="1.6"),w=1000,h=80),
          Pos(56,1130,C(width=1088,height=100,color="#FBEAE5",borderRadius=12)),
          Pos(80,1150,T("截止：2027.04.30（演示）",size=20,color=coral,weight="BOLD",family=F)),
          Pos(80,1180,T("先填 5 问，再按提示收材料；不要把所有票据都打印。",size=16,color=ink,family=F)),
          Pos(56,1480,T("演示报税流程 · 非税务建议；以当地税局为准",size=11,color="#8A8578",family=M))]
    return base(W,H,bg,n)


B={"case-01":(case01,900,1200),"case-02":(case02,1200,1600),"case-03":(case03,1200,1600),"case-04":(case04,1200,1600),
   "case-05":(case05,1200,1600),"case-06":(case06,1200,1600),"case-07":(case07,1600,1000),"case-08":(case08,900,1200),
   "case-09":(case09,900,1200),"case-10":(case10,1200,1600)}


def main():
    (TMP/"dsl").mkdir(parents=True,exist_ok=True); (TMP/"renders").mkdir(parents=True,exist_ok=True)
    for cid,(fn,w,h) in B.items(): (TMP/"dsl"/f"{cid}-{VERSION}.snapshot").write_text(fn(),encoding="utf-8")
    print("B06",VERSION,"built",len(B)); return 0


if __name__=="__main__": raise SystemExit(main())
