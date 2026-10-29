#!/usr/bin/env python3
"""B04 ten-plate explainer on Snapshot's text-to-image pipeline."""
import math, os, html
from pathlib import Path
SCRIPT=Path(__file__).resolve(); SUITE=Path(os.environ.get("SNAPSHOT_TASK_ROOT",SCRIPT.parents[4])); RUN=SCRIPT.parents[2].name
OUT=SUITE/'outputs'/RUN/'B04'; OUT.mkdir(parents=True,exist_ok=True)
BG="#F7F5F0"; INK="#15202B"; ACC="#0F766E"; SEC="#B45309"; MUT="#5B6B7A"
def esc(s): return html.escape(str(s),quote=False)
def T(txt,size,color=INK,bold=False,extra="",fam="Noto Sans CJK SC"):
    st=' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="{fam}" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'
def rect(x,y,w,h,color,r=0,border=None):
    b=f' border="{border}"' if border else ""
    return f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Container width="{w}" height="{h}" color="{color}" borderRadius="{r}"{b}/></Positioned>'
def seg(x1,y1,x2,y2,color=ACC,w=3):
    L=math.hypot(x2-x1,y2-y1); a=math.atan2(y2-y1,x2-x1); c,s=math.cos(a),math.sin(a)
    mat=f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"
    return f'<Positioned left="{x1:.1f}" top="{y1-w/2:.1f}"><Transform matrix="{mat}" origin="(0,0)"><Container width="{L:.1f}" height="{w}" color="{color}" borderRadius="{w/2}"/></Transform></Positioned>'
def arrow(x1,y1,x2,y2,color=ACC):
    ang=math.atan2(y2-y1,x2-x1); out=[seg(x1,y1,x2,y2,color,3)]
    for d in (28,-28):
        a=ang+math.radians(d); out.append(seg(x2-12*math.cos(a),y2-12*math.sin(a),x2,y2,color,3))
    return "".join(out)
def card(x,y,w,h,color="#FFFFFF",r=14):
    return rect(x,y,w,h,color,r,"1 SOLID #DCD3C4")
def chip(x,y,label,w=120,color=ACC):
    return f'<Positioned left="{x}" top="{y}"><Container width="{w}" height="40" color="{color}" borderRadius="8" alignment="CENTER">'+T(label,16,"#FFFFFF",True)+'</Container></Positioned>'
def chipc(x,y,label,w=150,color=ACC):
    st=' fontStyle="BOLD"'
    txt=f'<Text fontFamily="Noto Sans CJK SC" fontSize="16" color="#FFFFFF"{st}><![CDATA[{label}]]></Text>'
    return f'<Positioned left="{x}" top="{y}"><Container width="{w}" height="40" color="{color}" borderRadius="8" alignment="CENTER">'+txt+'</Container></Positioned>'
plates=[]
# diagrams (relative to 660,260)
def d1():
    b=[card(0,0,480,520)]
    b.append(rect(40,70,180,90,INK,10))
    b.append('<Positioned left="52" top="82" width="160"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("UTF-8 DSL",18,"#FFFFFF",True)+T("文本请求体",14,"#94A3B8")+'</Column></Positioned>')
    b.append(arrow(220,115,300,115))
    b.append(rect(300,60,140,110,ACC,10))
    b.append('<Positioned left="312" top="78" width="120"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("POST",18,"#FFFFFF",True)+T("/snapshot",14,"#CCFBF1")+'</Column></Positioned>')
    b.append(arrow(370,170,370,250))
    b.append(rect(290,250,160,100,SEC,10))
    b.append('<Positioned left="304" top="270" width="140"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("PNG",22,"#FFFFFF",True)+T("image/png",14,"#FDE68A")+'</Column></Positioned>')
    b.append('<Positioned left="40" top="400" width="400">'+T("失败时返回 {code, message, requestId}",16,MUT)+'</Positioned>')
    b.append('<Positioned left="40" top="450" width="400">'+T("429 / 503 参考 Retry-After；400 先改 DSL。",16,MUT)+'</Positioned>')
    return "".join(b)
def d2():
    b=[card(0,0,480,520)]
    b.append(chipc(30,50,"<Snapshot>",150)); b.append(chipc(200,50,"<Container>",150,INK)); b.append(chipc(360,50,"<Text>",110,SEC))
    b.append(seg(105,90,105,150)); b.append(seg(275,90,275,180)); b.append(seg(415,90,415,150))
    b.append(card(20,170,200,80,"#E8F5F1",8))
    b.append('<Positioned left="34" top="186" width="180"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("Element 树",18,ACC,True)+T("标签 + 属性 + 子节点",14,MUT)+'</Column></Positioned>')
    b.append(card(250,170,210,80,"#FDECEC",8))
    b.append('<Positioned left="264" top="186" width="190"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("Widget 树",18,SEC,True)+T("布局 + 绘制",14,MUT)+'</Column></Positioned>')
    b.append(arrow(120,250,120,330)); b.append(arrow(355,250,355,330))
    b.append(card(40,340,400,100,"#F0F4F8",10))
    b.append('<Positioned left="58" top="356" width="370"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("RenderBox → Skia 画布",18,INK,True)+T("约束向下，尺寸向上",14,MUT)+'</Column></Positioned>')
    b.append('<Positioned left="40" top="462" width="400">'+T("未知属性被忽略；未知标签直接报错。",15,MUT)+'</Positioned>')
    return "".join(b)
def d3():
    b=[card(0,0,480,520)]
    b.append(rect(40,40,400,330,"#FFFFFF",12,"2 SOLID #CBD5E1"))
    b.append(rect(70,70,340,270,"#E8F5F1",10)); b.append(rect(100,100,280,210,"#FDF3E4",8)); b.append(rect(130,130,220,150,"#E8EEFB",6))
    b.append('<Positioned left="40" top="396">'+T("有界主轴 → Expanded 可分配剩余",15,MUT)+'</Positioned>')
    b.append('<Positioned left="40" top="426">'+T("无界主轴 → Flex 无法确定剩余",15,MUT)+'</Positioned>')
    b.append('<Positioned left="40" top="456">'+T("画布尺寸来自根 Widget 的布局结果",15,MUT)+'</Positioned>')
    return "".join(b)
def d4():
    b=[card(0,0,480,520)]
    b.append('<Positioned left="40" top="60">'+T("Ag",140,INK,True)+'</Positioned>')
    for i,y in enumerate([130,160,190,220]):
        b.append(seg(40,y,440,y,"#CBD5E1" if i else SEC,1 if i else 3))
    b.append('<Positioned left="190" top="110">'+T("ascent",15,MUT)+'</Positioned>')
    b.append('<Positioned left="190" top="172">'+T("baseline",15,SEC)+'</Positioned>')
    b.append('<Positioned left="190" top="204">'+T("descent",15,MUT)+'</Positioned>')
    b.append('<Positioned left="40" top="300" width="400">'+T("字体从服务实际列表选择；缺字会回退，行高与基线随字体度量变化。",16,MUT)+'</Positioned>')
    return "".join(b)
def d5():
    b=[card(0,0,480,520)]
    sw=["#0F766E","#B45309","#2563EB","#7C3AED","#111827"]
    for i,c in enumerate(sw):
        b.append(rect(40+i*78,60,66,110,c,10))
    b.append('<Positioned left="40" top="192">'+T("gradientType=LINEAR · 3 stops",15,MUT)+'</Positioned>')
    b.append('<Positioned left="40" top="220" width="380" height="80"><Container width="380" height="80" borderRadius="12" gradientType="LINEAR" gradientColors="#0F766E,#2563EB,#7C3AED" gradientStops="0,0.55,1" gradientBegin="CENTER_LEFT" gradientEnd="CENTER_RIGHT"/></Positioned>')
    b.append('<Positioned left="40" top="340" width="400">'+T("8 位颜色：#RRGGBBAA，最后两位是 alpha；底色需显式设置。",16,MUT)+'</Positioned>')
    b.append('<Positioned left="40" top="410" width="400">'+T("渐变写在 Container 上，至少要两种颜色。",16,MUT)+'</Positioned>')
    return "".join(b)
def d6():
    b=[card(0,0,480,520)]
    b.append(rect(40,60,400,80,"#E8EEFB",8)); b.append(rect(40,160,400,80,"#E8F5F1",8)); b.append(rect(40,260,400,80,"#FDF3E4",8))
    b.append('<Positioned left="56" top="78" width="370"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("Row · 主轴水平",16,INK,True)+T("Expanded ×2",14,MUT)+'</Column></Positioned>')
    b.append('<Positioned left="56" top="178" width="370"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("Column · 主轴垂直",16,INK,True)+T("有界才有剩余空间",14,MUT)+'</Column></Positioned>')
    b.append('<Positioned left="56" top="278" width="370"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("Spacer",16,INK,True)+T("吸收剩余空间",14,MUT)+'</Column></Positioned>')
    b.append('<Positioned left="40" top="376">'+T("固定 120 + flex 份额 = 主轴 400",15,MUT)+'</Positioned>')
    b.append(rect(40,404,120,44,INK,6)); b.append(rect(160,404,93,44,ACC,6)); b.append(rect(253,404,187,44,SEC,6))
    b.append('<Positioned left="40" top="418">'+T("fixed",14,"#FFFFFF",True)+'</Positioned>')
    b.append('<Positioned left="160" top="418">'+T("flex 1",14,"#FFFFFF",True)+'</Positioned>')
    b.append('<Positioned left="253" top="418">'+T("flex 2",14,"#FFFFFF",True)+'</Positioned>')
    return "".join(b)
def d7():
    b=[card(0,0,480,520)]
    b.append(rect(60,60,360,340,"#E8EEFB",10))
    b.append(rect(80,90,180,140,"#0F766E",8)); b.append(rect(180,160,200,180,"#B45309",8))
    b.append('<Positioned left="40" top="420" width="400">'+T("Positioned 子节点按 left/top/right/bottom 定位",15,MUT)+'</Positioned>')
    b.append('<Positioned left="40" top="458" width="400">'+T("没有固定尺寸时，Stack 按最大子节点收缩。",15,MUT)+'</Positioned>')
    return "".join(b)
def d8():
    b=[card(0,0,480,520)]
    b.append('<Positioned left="120" top="120" width="200" height="200"><Transform matrix="(0.866025,0.5,0,0,-0.5,0.866025,0,0,0,0,1,0,0,0,0,1)" origin="(100,100)"><Container width="200" height="200" color="'+ACC+'" borderRadius="12"/></Transform></Positioned>')
    b.append('<Positioned left="120" top="360" width="360">'+T("matrix 为 16 个列主序浮点数；旋转/缩放/平移都可组合。",15,MUT)+'</Positioned>')
    b.append('<Positioned left="120" top="420" width="340">'+T("布局尺寸不变，越界部分可能被裁掉。",15,MUT)+'</Positioned>')
    return "".join(b)
def d9():
    b=[card(0,0,480,520)]
    cols=["#0F766E","#B45309","#2563EB","#7C3AED","#111827"]
    def band(x,y,w,h):
        step=w/len(cols)
        return "".join(rect(x+i*step,y,step+0.6,h,cols[i],0) for i in range(len(cols)))
    def bandn(x,y,w,h,n=20):
        step=w/n
        return "".join(rect(x+i*step,y,step+0.4,h,cols[i%len(cols)],0) for i in range(n))
    b.append('<Positioned left="40" top="34">'+T("原始条纹",15,MUT)+'</Positioned>')
    b.append(band(40,58,400,70))
    sharp=('<Positioned left="40" top="150" width="190" height="90"><ClipRRect borderRadius="10"><Stack alignment="TOP_LEFT">'
           '<Container width="190" height="90" color="#FFFFFF"/>'+band(0,0,190,90)+'</Stack></ClipRRect></Positioned>')
    blurred=('<Positioned left="250" top="150" width="190" height="90"><ClipRRect borderRadius="10"><ImageFiltered sigmaX="6" sigmaY="6">'
             '<Stack alignment="TOP_LEFT"><Container width="190" height="90" color="#FFFFFF"/>'+band(0,0,190,90)+'</Stack></ImageFiltered></ClipRRect></Positioned>')
    b.append(sharp); b.append(blurred)
    b.append('<Positioned left="40" top="248">'+T("原图",14,MUT)+'</Positioned>')
    b.append('<Positioned left="250" top="248">'+T("ImageFiltered sigma=6",14,ACC,True)+'</Positioned>')
    backdrop=('<Positioned left="40" top="300" width="400" height="100"><Stack alignment="TOP_LEFT">'
              '<Container width="400" height="100" color="#FFFFFF"/>'+bandn(0,0,400,100)+
              '<Positioned left="60" top="15" width="280" height="70"><ClipRRect borderRadius="12"><BackdropFilter sigmaX="8" sigmaY="8">'
              '<Container width="280" height="70" color="#FFFFFF22" borderRadius="12"/></BackdropFilter></ClipRRect></Positioned></Stack></Positioned>')
    b.append(backdrop)
    b.append('<Positioned left="40" top="412">'+T("BackdropFilter：只模糊面板下方已绘制背景",14,ACC,True)+'</Positioned>')
    b.append('<Positioned left="40" top="450" width="400">'+T("先裁剪，再滤镜；文字要画在滤镜之后才清晰。",15,MUT)+'</Positioned>')
    return "".join(b)
def d10():
    b=[card(0,0,480,520)]
    b.append(rect(40,50,400,150,INK,10))
    b.append('<Positioned left="56" top="66" width="380"><Column crossAxisAlignment="START" mainAxisSize="MIN">'+T("{",18,"#F8FAFC")+T('  "code": "PARSE_ERROR",',16,"#FCA5A5")+T('  "message": "...",',16,"#FCA5A5")+T('  "requestId": "..."',16,"#FCA5A5")+T("}",18,"#F8FAFC")+'</Column></Positioned>')
    b.append('<Positioned left="40" top="240" width="400">'+T("400 语法错误 / 422 布局错误：先读 code，再看 diagnostic。",16,MUT)+'</Positioned>')
    b.append('<Positioned left="40" top="300" width="400">'+T("保留失败响应与 X-Request-Id，交付时附 DSL 与最终图。",16,MUT)+'</Positioned>')
    b.append('<Positioned left="40" top="360" width="400">'+T("429 / 503 可参考 Retry-After；格式错误先修正。",16,MUT)+'</Positioned>')
    return "".join(b)
DG=[d1,d2,d3,d4,d5,d6,d7,d8,d9,d10]
plates_data=[
 ("请求：从文本到图片",["POST /snapshot 的请求体是 UTF-8 纯文本 DSL，不是 JSON。成功响应是图片二进制；失败响应是带 code、message、requestId 的 JSON。","先确认 Content-Type 与响应类型，再判断内容。语法错误先读 diagnostic 的 attributeName 与 position。"],["成功响应是 image/png 原始字节","失败响应与成功响应都要留档"],"https://open-snapshot.muedsa.com/ai-guide.md"),
 ("词法、元素树与组件树",["Tokenizer 把标签、属性、文本与注释切成 token；Parser 组装 Element 树，再创建 Widget 树。","标签名与属性名区分大小写；未知属性会被忽略，未知标签会报错。"],["Element 树保留源码结构","Widget 树负责布局与绘制"],"https://snapshot.muedsa.com/guides/parser.md"),
 ("约束与尺寸",["布局从根开始向下传约束，再从子节点向上回传尺寸。根 Canvas 的尺寸来自根 Widget 的布局结果，不是 HTML 视口。","Row/Column 只有在主轴有界时，Expanded 才能分配剩余空间；Spacer 也一样。"],["先给根一个有限尺寸","再用 Expanded/Spacer 组织弹性"],"https://snapshot.muedsa.com/reference/parser-tags.md"),
 ("文字与字体度量",["fontSize 是逻辑像素；行高与基线由字体度量决定。不同字体、缺字回退都会改变实际字形位置。","需要共享基线时用嵌套 Text 或 Row 的 BASELINE 对齐；不要把文字盒中心当基线。"],["字体必须来自服务实际列表","对齐看基线，不只看盒子"],"https://snapshot.muedsa.com/reference/parser-text.md"),
 ("装饰：颜色、圆角与渐变",["颜色支持 #RGB、#RRGGBBAA、rgb()/hsl() 等；8 位色的最后两位是 alpha。","Container 的 color 与 border/gradient 会合并成 BoxDecoration；底色需要显式设置。"],["半透明用 #RRGGBBAA","渐变至少两种颜色"],"https://snapshot.muedsa.com/reference/parser-tags.md"),
 ("Flex：剩余空间从哪来",["Flex 先排列固定子节点，再把剩余主轴空间按 flex 份额分配。没有有界主轴就没有“剩余”。","Expanded 强制填满份额；Flexible 允许子节点更小；Spacer 不绘制。"],["有界主轴是弹性布局前提","固定尺寸与弹性项混用最稳"],"https://snapshot.muedsa.com/reference/parser-tags.md"),
 ("Stack 与绝对定位",["Stack 允许子节点叠放，Positioned 是唯一可用四边定位的子节点类型，且必须是 Stack 的直接子节点。","Stack 默认按最大子节点尺寸收缩；需要固定画布时，用外层 Container 给尺寸。"],["Positioned 只能放在 Stack 下","固定画布 + 绝对定位适合仪表盘"],"https://snapshot.muedsa.com/reference/parser-tags.md"),
 ("Transform：矩阵而非角度",["Transform 需要 16 个列主序 4×4 浮点数。平移、旋转、缩放都可以写进同一矩阵。","旋转中心可用 origin 或 alignment 指定；矩阵不会改变布局尺寸，可能越界绘制。"],["矩阵是列主序","旋转后要检查裁剪与遮挡"],"https://snapshot.muedsa.com/reference/parser-tags.md"),
 ("滤镜与裁剪的语义",["ColorFiltered 改变子树的颜色；ImageFiltered 模糊整个子树；BackdropFilter 读取已绘制背景。","滤镜需要裁剪限定范围，否则模糊边缘会外溢；文字要画在滤镜之后才保持清晰。"],["先裁剪，再滤镜","背景模糊与子树模糊是两件事"],"https://snapshot.muedsa.com/reference/parser-tags.md"),
 ("错误、重试与可复现交付",["非成功响应通常是 JSON；code 是稳定分类，message 可能变化。每次请求可用 X-Request-Id 关联日志。","交付不是“请求成功”：要打开最终 PNG，保留同名 DSL、真实响应与失败记录，并能在同一服务复现。"],["先看 code，再看 message","最终图 + DSL + 日志一起交付"],"https://open-snapshot.muedsa.com/ai-guide.md"),
]
for i,(title,paras,bullets,src) in enumerate(plates_data,1):
    W,H=1200,1500
    b=[f'<Snapshot background="{BG}" type="png"><Container width="{W}" height="{H}"><Stack alignment="TOP_LEFT"><Container width="{W}" height="{H}" color="{BG}"/>']
    b.append('<Positioned left="64" top="48"><Row crossAxisAlignment="CENTER">'+T(f"PLATE {i:02d} / 10",14,ACC,True,' letterSpacing="2"')+'<SizedBox width="16"/>'+T("SNAPSHOT / FROM TEXT TO IMAGE",14,MUT,True,' letterSpacing="1"')+'</Row></Positioned>')
    b.append('<Positioned left="64" top="92" width="1072">'+T(title,44,INK,True)+'</Positioned>')
    b.append(seg(64,170,1136,170,"#D8CFC1",1))
    b.append('<Positioned left="64" top="210" width="540"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
    for p in paras:
        b.append(T(p,22,MUT)); b.append('<SizedBox height="14"/>')
    b.append('</Column></Positioned>')
    b.append('<Positioned left="660" top="210"><Stack alignment="TOP_LEFT"><Container width="480" height="520" color="transparent"/>'+DG[i-1]()+'</Stack></Positioned>')
    b.append(rect(64,800,1072,240,"#FFFFFF",14,"1 SOLID #DCD3C4"))
    b.append('<Positioned left="88" top="822">'+T("要点 / TAKEAWAYS",14,SEC,True,' letterSpacing="1.5"')+'</Positioned>')
    for j,bl in enumerate(bullets):
        b.append(f'<Positioned left="88" top="{860+j*58}">'+T("— "+bl,24,INK)+'</Positioned>')
    b.append(rect(64,1080,1072,160,"#E8F5F1",12))
    b.append('<Positioned left="88" top="1104">'+T("在真实服务上验证",16,ACC,True)+'</Positioned>')
    b.append('<Positioned left="88" top="1140" width="1020">'+T("术语与默认值以当前部署为准；静态文档只能作为起点，最终以请求响应和实际 PNG 核对。",20,MUT)+'</Positioned>')
    b.append('<Positioned left="64" top="1280">'+T("完整渲染示例见 B01–B03 的 DSL；本特辑不嵌入图片。",15,MUT)+'</Positioned>')
    b.append('<Positioned left="64" top="1350">'+T("来源："+src,13,MUT)+'</Positioned>')
    b.append(f'<Positioned left="64" top="1420">'+T(f"PLATE {i:02d} · 摘自实际阅读的官方文档",11,MUT)+'</Positioned>')
    b.append('</Stack></Container></Snapshot>')
    d=OUT/f"case-{i:02d}"; d.mkdir(parents=True,exist_ok=True)
    (d/'final.snapshot').write_text("\n".join(b),encoding='utf-8')
    (d/'case.md').write_text(f"# {title}\n\n- 来源：{src}\n- 用途：开发者向的视觉解释页，阅读顺序 01→10。\n- 主图：final.png（1200×1500）；DSL：final.snapshot。\n",encoding='utf-8')
print('B04 wrote 10')
