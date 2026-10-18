"""B05 · Harbor care coordination product, ten static screens."""
from __future__ import annotations
import math, os, sys
from pathlib import Path
ROOT=Path(os.environ.get("SNAPSHOT_TASK_ROOT",".")).resolve(); RUN=os.environ["SNAPSHOT_RUN_ID"]; TASK="B05"
VERSION=sys.argv[1] if len(sys.argv)>1 else "v001"; TMP=ROOT/"tmp"/RUN/TASK
sys.path.insert(0,str(ROOT/"tmp"/RUN/"_suite"/"scripts")); sys.path.insert(0,str(ROOT/"tmp"/RUN/"B02"/"scripts"))
from dsl import C, Pos, SizedBox, Stack, T  # noqa: E402
from b02_build import rot, seg, dot, base  # noqa: E402
F="Inter,Noto Sans CJK SC"; S="Noto Serif CJK SC,Noto Sans CJK SC"; M="Noto Sans Mono CJK SC,Inter"
TEAL="#0E3B3A"; CORAL="#E76F51"; CREAM="#F6F1E7"; MINT="#7BC4B0"; INK="#17211F"; MUT="#6E7C76"


def mark(x,y,s=1.0,dark=False):
    c=CORAL if not dark else CREAM
    return [Pos(x,y,C(width=30*s,height=30*s,color="transparent",border=f"3 SOLID {c}",borderRadius=6*s)),
            Pos(x+9*s,y+9*s,C(width=12*s,height=12*s,color=TEAL if not dark else CREAM,borderRadius=6*s))]


def shell(w,h,bg,nodes,title=None,back=True):
    n=[Pos(0,0,C(width=w,height=h,color=bg)),
       Pos(28,20,T("9:41",size=13,color=INK,weight="BOLD",family=M)),
       Pos(w-92,20,T("●●● 100%",size=10,color=INK,family=M))]
    if title:
        n += [Pos(28,58,T("‹" if back else "",size=30,color=INK,family=F)),
              Pos(56,64,T(title,size=20,color=INK,weight="BOLD",family=F))]
    n += nodes
    return base(w,h,bg,n)


def nav(y=860,active="today"):
    items=[("今日","today"),("用药","meds"),("记录","log"),("家人","family")]
    n=[Pos(0,y,C(width=430,height=72,color="#FFFFFF")),Pos(0,y,C(width=430,height=1,color="#E2D9C9"))]
    for i,(lab,key) in enumerate(items):
        x=54+i*108; c=CORAL if key==active else "#98A39E"
        n += [dot(x,y+24,20,c),Pos(x-22,y+44,T(lab,size=11,color=c,family=F))]
    return n


def case01():
    W,H=430,932; n=mark(28,60,1.0)+[Pos(70,64,T("港湾 Harbor",size=22,color=TEAL,weight="BOLD",family=F)),
        Pos(28,140,T("谁在照顾？",size=34,color=INK,weight="BOLD",family=S)),
        Pos(28,192,T("先选你的角色，之后可以邀请家人。",size=15,color=MUT,family=F))]
    roles=[("我是主要照护者","日常安排/用药/就诊",CORAL),("我是轮班家人","查看/交班/记录",MINT),("我是本人","看自己的计划",TEAL),("专业人员","只读摘要",MUT)]
    for i,(a,b,c) in enumerate(roles):
        y=240+i*118
        n += [Pos(28,y,C(width=374,height=100,color="#FFFFFF",borderRadius=14,border="1 SOLID #E2D9C9")),
              dot(54,y+50,16,c),Pos(84,y+22,T(a,size=18,color=INK,weight="BOLD",family=F)),
              Pos(84,y+50,T(b,size=13,color=MUT,family=F)),Pos(360,y+38,T("›",size=26,color=c,family=F))]
    n += [Pos(28,736,C(width=374,height=54,color=TEAL,borderRadius=27)),
          Pos(150,752,T("继续",size=18,color=CREAM,weight="BOLD",family=F)),
          Pos(28,810,T("隐私：只有你邀请的家人才能看到照护记录；\n可随时撤销。",size=12,color=MUT,family=F,height="1.5"),w=370,h=50)]
    return shell(W,H,CREAM,n)


def case02():
    W,H=430,932; n=[Pos(0,0,C(width=W,height=210,color=TEAL)),
        Pos(28,60,T("早上好，林岚",size=26,color=CREAM,weight="BOLD",family=F)),
        Pos(28,100,T("妈妈今天 3 件事 · 已完成 1 件",size=14,color="#BFD8D0",family=F)),
        Pos(28,140,T("血压 138/82",size=30,color=CREAM,weight="BOLD",family=M)),
        Pos(220,148,T("07:30 测量",size=12,color="#BFD8D0",family=M))]
    tasks=[("08:00","氨氯地平 5mg","已服",True,CORAL),("10:00","楼下散步 20 分钟","待完成",False,MINT),("14:00","给张医生打电话","待完成",False,"#D9A441")]
    for i,(t,a,s,done,c) in enumerate(tasks):
        y=240+i*106
        n += [Pos(20,y,C(width=390,height=90,color="#FFFFFF",borderRadius=14,border="1 SOLID #E2D9C9")),
              Pos(36,y+16,T(t,size=13,color=MUT,family=M)),
              Pos(36,y+40,T(a,size=18,color=INK,weight="BOLD",family=F)),
              Pos(36,y+66,T(s,size=12,color=c,family=F)),
              dot(372,y+44,24,"#FFFFFF",f"3 SOLID {c}"), (dot(372,y+44,10,c) if done else "")]
    n += [Pos(20,570,C(width=390,height=120,color="#EAF3EE",borderRadius=14)),
          Pos(38,588,T("今日提醒",size=12,color=TEAL,weight="BOLD",family=F)),
          Pos(38,612,T("下午有雨，散步改到地下车库；\n记得带她喜欢的帽子。",size=14,color=INK,family=F,height="1.5"),w=340,h=60),
          Pos(20,710,C(width=390,height=100,color="#FFFFFF",borderRadius=14,border="1 SOLID #E2D9C9")),
          Pos(38,728,T("下一位",size=12,color=MUT,family=F)),Pos(38,750,T("林川 · 18:00 接班",size=16,color=INK,weight="BOLD",family=F)),
          Pos(300,742,T("交班 →",size=13,color=CORAL,family=F))]
    n += nav()
    return shell(W,H,CREAM,n)


def case03():
    W,H=430,932; n=[Pos(0,0,C(width=W,height=8,color=CORAL))]
    n += [Pos(28,60,T("用药",size=28,color=INK,weight="BOLD",family=S)),Pos(300,66,T("剩余 12 天",size=12,color=MUT,family=F))]
    groups=[("早上 08:00","氨氯地平 5mg","1 片 · 饭后","已服",True),("晚上 21:00","阿托伐他汀 20mg","1 片 · 睡前","待服",False)]
    for i,(t,dose,note,status,done) in enumerate(groups):
        y=120+i*230
        n += [Pos(20,y,C(width=390,height=190,color="#FFFFFF",borderRadius=16,border="1 SOLID #E2D9C9")),
              Pos(38,y+16,T(t,size=13,color=CORAL,weight="BOLD",family=M)),
              Pos(38,y+44,T(dose,size=22,color=INK,weight="BOLD",family=F)),
              Pos(38,y+76,T(note,size=13,color=MUT,family=F)),
              Pos(38,y+106,T(status,size=14,color=MINT if done else "#D9A441",weight="BOLD",family=F)),
              Pos(300,y+52,C(width=86,height=36,color=TEAL,borderRadius=18)),
              Pos(318,y+62,T("记录" if not done else "已记录",size=12,color=CREAM,family=F))]
    n += [Pos(20,600,C(width=390,height=130,color="#FBE9E3",borderRadius=14,border="1 SOLID #E7B4A6")),
          Pos(38,618,T("需要注意",size=12,color=CORAL,weight="BOLD",family=F)),
          Pos(38,642,T("两种药无已知相互作用；若出现明显头晕，\n先坐下并记录血压，不要自行停药。",size=13,color=INK,family=F,height="1.5"),w=340,h=70),
          Pos(20,750,T("本周服药率 92% · 漏服 1 次（11.12 晚）",size=12,color=MUT,family=F))]
    n += nav(active="meds")
    return shell(W,H,CREAM,n)


def case04():
    W,H=430,932; n=[Pos(0,0,C(width=W,height=150,color=TEAL))]
    n += [Pos(28,56,T("就诊准备",size=26,color=CREAM,weight="BOLD",family=F)),
          Pos(28,96,T("11.18 周三 09:30 · 社区医院 张医生",size=13,color="#BFD8D0",family=F)),
          Pos(28,126,T("还有 2 天",size=14,color="#F2C46B",weight="BOLD",family=F))]
    qs=["最近头晕两次，分别在什么时间？","血压早上高还是晚上高？","阿托伐他汀需要继续吗？","下次复查哪些项目？"]
    n += [Pos(20,176,T("要问的问题",size=13,color=MUT,weight="BOLD",family=F))]
    for i,q in enumerate(qs):
        y=204+i*62
        n += [Pos(20,y,C(width=390,height=50,color="#FFFFFF",borderRadius=10,border="1 SOLID #E2D9C9")),
              dot(42,y+25,18,"#FFFFFF",f"2 SOLID {CORAL}"),Pos(62,y+14,T(q,size=13,color=INK,family=F))]
    n += [Pos(20,480,C(width=390,height=140,color="#FFFFFF",borderRadius=14,border="1 SOLID #E2D9C9")),
          Pos(38,498,T("要带",size=12,color=MUT,family=F)),
          Pos(38,522,T("医保卡 · 用药清单 · 最近 7 天血压\n上次化验单 · 交通卡",size=14,color=INK,family=F,height="1.5"),w=330,h=80),
          Pos(20,640,C(width=390,height=80,color="#EAF3EE",borderRadius=14)),
          Pos(38,656,T("交通",size=12,color=MUT,family=F)),Pos(38,678,T("地铁 2 号线 B 口 → 医院西门 · 轮椅坡道",size=13,color=INK,family=F)),
          Pos(20,750,C(width=390,height=52,color=CORAL,borderRadius=26)),
          Pos(150,765,T("生成陪诊清单",size=16,color="#FFFFFF",weight="BOLD",family=F))]
    return shell(W,H,CREAM,n)


def case05():
    W,H=430,932; n=[Pos(0,0,C(width=W,height=8,color=MINT))]
    n += [Pos(28,58,T("症状与血压",size=26,color=INK,weight="BOLD",family=S)),Pos(300,64,T("近 7 天",size=12,color=MUT,family=F))]
    # BP bars
    vals=[(132,84),(140,86),(136,82),(146,88),(138,82),(142,84),(138,82)]
    for i,(s,d) in enumerate(vals):
        x=32+i*54; h=(s-100)*2.2
        n += [Pos(x,360-h,C(width=20,height=h,color=CORAL,borderRadius=6)),Pos(x,360-d/2,C(width=20,height=d/2,color=MINT,borderRadius=6)),
              Pos(x-2,376,T(["一","二","三","四","五","六","日"][i],size=10,color=MUT,family=F))]
    n += [Pos(28,130,T("138/82",size=40,color=INK,weight="BOLD",family=M)),Pos(240,146,T("mmHg · 07:30",size=12,color=MUT,family=M)),
          Pos(28,190,T("收缩压 / 舒张压",size=11,color=MUT,family=F)),
          Pos(28,420,T("头晕记录",size=13,color=MUT,weight="BOLD",family=F))]
    events=[("11.16 15:20","起身后头晕，坐下 5 分钟缓解","已记录"),("11.12 09:10","早餐后轻微头晕","已记录")]
    for i,(t,e,st) in enumerate(events):
        y=450+i*100
        n += [Pos(20,y,C(width=390,height=84,color="#FFFFFF",borderRadius=12,border="1 SOLID #E2D9C9")),
              Pos(36,y+12,T(t,size=11,color=CORAL,family=M)),Pos(36,y+34,T(e,size=14,color=INK,family=F)),
              Pos(300,y+30,T(st,size=11,color=MINT,family=F))]
    n += [Pos(20,620,C(width=390,height=90,color="#EAF3EE",borderRadius=12)),
          Pos(38,636,T("给医生看",size=12,color=TEAL,weight="BOLD",family=F)),
          Pos(38,708,T("两次头晕都在起身后；血压波动不大。",size=13,color=INK,family=F)),
          Pos(20,790,C(width=390,height=52,color=TEAL,borderRadius=26)),
          Pos(150,805,T("+ 记录一次",size=16,color=CREAM,weight="BOLD",family=F))]
    n += nav(active="log")
    return shell(W,H,CREAM,n)


def case06():
    W,H=430,932; n=[Pos(0,0,C(width=W,height=150,color=TEAL))]
    n += [Pos(28,56,T("交班给林川",size=26,color=CREAM,weight="BOLD",family=F)),
          Pos(28,96,T("今天 18:00 · 夜班",size=13,color="#BFD8D0",family=F))]
    n += [Pos(20,174,T("今天的重点",size=12,color=MUT,weight="BOLD",family=F))]
    checks=[("血压 138/82，晚上再测一次",True),("氨氯地平已服，晚上他汀 21:00",True),("头晕两次，起身慢一点",True),("明天陪诊 09:30，带医保卡",False)]
    for i,(t,done) in enumerate(checks):
        y=202+i*62
        n += [Pos(20,y,C(width=390,height=50,color="#FFFFFF",borderRadius=10,border="1 SOLID #E2D9C9")),
              dot(42,y+25,18,"#FFFFFF",f"2 SOLID {MINT if done else '#D9A441'}"),
              (dot(42,y+25,8,MINT) if done else ""),Pos(62,y+14,T(t,size=13,color=INK,family=F))]
    n += [Pos(20,480,T("留一句话",size=12,color=MUT,weight="BOLD",family=F)),
          Pos(20,506,C(width=390,height=140,color="#FFFFFF",borderRadius=12,border="1 SOLID #E2D9C9")),
          Pos(38,526,T("妈今天心情不错，午饭后走了 15 分钟。\n晚上提醒她泡脚，别说“你又忘了”。",size=14,color=INK,family=F,height="1.5"),w=340,h=90),
          Pos(20,680,C(width=390,height=52,color=CORAL,borderRadius=26)),
          Pos(152,695,T("发送交班",size=16,color="#FFFFFF",weight="BOLD",family=F)),
          Pos(20,760,T("林川 · 已读 17:42",size=11,color=MUT,family=F))]
    return shell(W,H,CREAM,n)


def case07():
    W,H=430,932; n=[Pos(0,0,C(width=W,height=8,color=CORAL))]
    n += [Pos(28,58,T("家人与权限",size=26,color=INK,weight="BOLD",family=S)),Pos(28,98,T("只有被邀请的人能看到记录。",size=13,color=MUT,family=F))]
    people=[("林岚","主要照护者","全部权限",CORAL),("林川","轮班家人","可看/可记录",MINT),("林溪","远居家人","只读摘要",TEAL),("张医生","专业人员","只读 30 天",MUT)]
    for i,(name,role,perm,c) in enumerate(people):
        y=136+i*118
        n += [Pos(20,y,C(width=390,height=100,color="#FFFFFF",borderRadius=14,border="1 SOLID #E2D9C9")),
              dot(54,y+50,44,"#EAF3EE"),Pos(44,y+38,T(name[0],size=18,color=TEAL,weight="BOLD",family=F)),
              Pos(88,y+20,T(name,size=18,color=INK,weight="BOLD",family=F)),
              Pos(88,y+48,T(role,size=12,color=MUT,family=F)),
              Pos(88,y+68,T(perm,size=12,color=c,family=F)),
              Pos(340,y+34,C(width=50,height=28,color=c if i<3 else "#D8D0C2",borderRadius=14)),
              dot(376 if i<3 else 350,y+48,20,"#FFFFFF")]
    n += [Pos(20,620,C(width=390,height=96,color="#EAF3EE",borderRadius=12)),
          Pos(38,636,T("邀请家人",size=12,color=TEAL,weight="BOLD",family=F)),
          Pos(38,658,T("发送一次性链接；对方接受后才能查看。",size=12,color=INK,family=F)),
          Pos(20,736,C(width=390,height=52,color=TEAL,borderRadius=26)),
          Pos(150,751,T("+ 邀请",size=16,color=CREAM,weight="BOLD",family=F))]
    n += nav(active="family")
    return shell(W,H,CREAM,n)


def case08():
    W,H=430,932; n=[Pos(0,0,C(width=W,height=220,color="#A9332B")),
        Pos(28,56,T("紧急卡",size=26,color="#FFFFFF",weight="BOLD",family=F)),
        Pos(28,96,T("王秀兰",size=36,color="#FFFFFF",weight="BOLD",family=F)),
        Pos(28,144,T("78 岁 · 高血压 · 轻度认知障碍",size=14,color="#FFE1DA",family=F)),
        Pos(28,174,T("青霉素过敏",size=16,color="#FFFFFF",weight="BOLD",family=F))]
    n += [Pos(20,240,C(width=390,height=130,color="#FFFFFF",borderRadius=14,border="1 SOLID #E2D9C9")),
          Pos(38,258,T("正在服用",size=12,color=MUT,family=F)),
          Pos(38,282,T("氨氯地平 5mg 每日 1 次（早）\n阿托伐他汀 20mg 每晚 1 次",size=14,color=INK,family=F,height="1.5"),w=340,h=80),
          Pos(20,390,C(width=390,height=150,color="#FFFFFF",borderRadius=14,border="1 SOLID #E2D9C9")),
          Pos(38,408,T("联系人",size=12,color=MUT,family=F)),
          Pos(38,432,T("林岚（女儿）138 0000 1234",size=15,color=INK,weight="BOLD",family=F)),
          Pos(38,464,T("林川（儿子）139 0000 5678",size=14,color=INK,family=F)),
          Pos(38,496,T("张医生 · 社区医院 6688",size=13,color=MUT,family=F)),
          Pos(20,570,C(width=390,height=150,color="#FBE9E3",borderRadius=14)),
          Pos(38,588,T("如果走失 / 跌倒",size=12,color=CORAL,weight="BOLD",family=F)),
          Pos(38,612,T("先确认呼吸与意识；不要强行扶起。\n拨打 120，告知年龄/用药/过敏。",size=14,color=INK,family=F,height="1.5"),w=340,h=80),
          Pos(20,750,C(width=390,height=58,color="#A9332B",borderRadius=29)),
          Pos(120,766,T("拨打 120",size=20,color="#FFFFFF",weight="BOLD",family=F)),
          Pos(20,820,T("此卡不替代病历；急救人员以现场判断为准。",size=11,color=MUT,family=F))]
    return shell(W,H,CREAM,n)


def case09():
    W,H=1024,768; n=[Pos(0,0,C(width=W,height=H,color=CREAM)),
        Pos(0,0,C(width=W,height=8,color=TEAL)),
        Pos(40,32,T("港湾 Harbor / 一周总结",size=14,color=CORAL,weight="BOLD",family=M,spacing=2)),
        Pos(40,64,T("王秀兰 · 11.10–11.16",size=34,color=INK,weight="BOLD",family=S)),
        Pos(40,114,T("给全家与张医生的一页摘要",size=15,color=MUT,family=F))]
    stats=[("92%","服药率","7 天 / 14 次，漏 1 次"),("128/78","平均血压","7 次家庭测量"),("2","头晕记录","均在起身后")]
    for i,(num,lab,sub) in enumerate(stats):
        x=40+i*310
        n += [Pos(x,160,C(width=290,height=150,color="#FFFFFF",borderRadius=14,border="1 SOLID #E2D9C9")),
              Pos(x+20,178,T(num,size=44,color=TEAL,weight="BOLD",family=M)),
              Pos(x+20,234,T(lab,size=15,color=INK,weight="BOLD",family=F)),
              Pos(x+20,262,T(sub,size=12,color=MUT,family=F))]
    # BP chart
    n += [Pos(40,350,C(width=620,height=300,color="#FFFFFF",borderRadius=14,border="1 SOLID #E2D9C9")),
          Pos(60,368,T("血压趋势",size=15,color=INK,weight="BOLD",family=F))]
    vals=[(132,84),(140,86),(136,82),(146,88),(138,82),(142,84),(138,82)]
    for i,(s,d) in enumerate(vals):
        x=80+i*76; h=(s-100)*4.5
        n += [Pos(x,610-h,C(width=22,height=h,color=CORAL,borderRadius=6)),Pos(x,610-d/2,C(width=22,height=d/2,color=MINT,borderRadius=6)),
              Pos(x-2,624,T(["一","二","三","四","五","六","日"][i],size=10,color=MUT,family=F))]
    n += [Pos(700,350,C(width=284,height=300,color="#FFFFFF",borderRadius=14,border="1 SOLID #E2D9C9")),
          Pos(720,368,T("下周待办",size=15,color=INK,weight="BOLD",family=F)),
          Pos(720,400,T("□ 11.18 09:30 陪诊\n□ 每晚测血压 1 次\n□ 周五补充氨氯地平\n□ 把头晕记录给医生",size=14,color=INK,family=F,height="1.75"),w=240,h=200)]
    n += [Pos(40,680,T("签名：林岚 · 生成 11.16 20:10 · 数据来自家庭记录，不是诊断。",size=11,color=MUT,family=F))]
    return base(W,H,CREAM,n)


def case10():
    W,H=1200,1600; n=[Pos(0,0,C(width=W,height=H,color="#FFFFFF")),
        Pos(0,0,C(width=W,height=12,color=TEAL)),
        Pos(48,36,T("港湾 Harbor / 就诊一页纸",size=12,color=CORAL,weight="BOLD",family=M,spacing=2)),
        Pos(48,70,T("王秀兰 · 78 岁",size=38,color=INK,weight="BOLD",family=S)),
        Pos(48,124,T("高血压 · 轻度认知障碍 · 青霉素过敏",size=17,color="#5C6A64",family=F)),
        Pos(900,74,T("11.18 就诊",size=15,color=CORAL,weight="BOLD",family=M))]
    n += [Pos(48,190,C(width=1104,height=2,color=INK))]
    n += [Pos(48,220,T("用药",size=14,color=MUT,weight="BOLD",family=F)),
          Pos(48,248,T("氨氯地平 5mg",size=22,color=INK,weight="BOLD",family=F)),Pos(520,252,T("每日 1 次 · 早上 · 已服 13/14",size=15,color="#5C6A64",family=F)),
          Pos(48,292,T("阿托伐他汀 20mg",size=22,color=INK,weight="BOLD",family=F)),Pos(520,296,T("每晚 1 次 · 已服 13/14",size=15,color="#5C6A64",family=F)),
          Pos(48,350,T("近 7 天血压（家庭测量）",size=14,color=MUT,weight="BOLD",family=F))]
    vals=[(132,84),(140,86),(136,82),(146,88),(138,82),(142,84),(138,82)]
    for i,(s,d) in enumerate(vals):
        x=80+i*140; h=(s-100)*3
        n += [Pos(x,720-h,C(width=34,height=h,color=CORAL,borderRadius=8)),Pos(x,720-d,C(width=34,height=d/2,color=MINT,borderRadius=8)),
              Pos(x-4,736,T(["11.10","11.11","11.12","11.13","11.14","11.15","11.16"][i],size=10,color=MUT,family=F))]
    n += [Pos(80,760,T("平均 128/78 mmHg；最高 146/88（11.13 早）",size=15,color="#5C6A64",family=F))]
    n += [Pos(48,820,T("症状/事件",size=14,color=MUT,weight="BOLD",family=F)),
          Pos(48,848,T("11.16 15:20 起身后头晕，坐下 5 分钟缓解；\n11.12 09:10 早餐后轻微头晕。两次均无跌倒。",size=16,color=INK,family=F,height="1.5"),w=1000,h=80)]
    n += [Pos(48,960,T("要问医生",size=14,color=MUT,weight="BOLD",family=F)),
          Pos(48,988,T("1. 两次头晕是否与血压波动/药物时间有关？\n2. 阿托伐他汀是否继续？下次血脂复查何时？\n3. 需要增加哪类居家安全评估？",size=16,color=INK,family=F,height="1.6"),w=1000,h=110)]
    n += [Pos(48,1160,C(width=1104,height=2,color="#D8D0C2")),
          Pos(48,1180,T("家庭记录 · 林岚 / 林川 / 林溪 · 生成 11.16 20:10",size=12,color=MUT,family=F)),
          Pos(48,1210,T("本页为家庭自述与设备记录，不是诊断；急症拨 120。",size=11,color=MUT,family=F)),
          Pos(900,1500,T("Harbor / page 1 of 1",size=11,color=MUT,family=M))]
    return base(W,H,"#FFFFFF",n)


B={"case-01":(case01,430,932),"case-02":(case02,430,932),"case-03":(case03,430,932),"case-04":(case04,430,932),
   "case-05":(case05,430,932),"case-06":(case06,430,932),"case-07":(case07,430,932),"case-08":(case08,430,932),
   "case-09":(case09,1024,768),"case-10":(case10,1200,1600)}


def main():
    (TMP/"dsl").mkdir(parents=True,exist_ok=True); (TMP/"renders").mkdir(parents=True,exist_ok=True)
    for cid,(fn,w,h) in B.items(): (TMP/"dsl"/f"{cid}-{VERSION}.snapshot").write_text(fn(),encoding="utf-8")
    print("B05",VERSION,"built",len(B)); return 0


if __name__=="__main__": raise SystemExit(main())
