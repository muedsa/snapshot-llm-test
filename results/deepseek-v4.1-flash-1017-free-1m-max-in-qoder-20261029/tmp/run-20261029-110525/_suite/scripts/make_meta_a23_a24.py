#!/usr/bin/env python3
import json
from pathlib import Path
RUN='run-20261029-110525'
def T(t,m):
    p=Path(f'tmp/{RUN}/{t}/drafts/meta.json'); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8'); print('meta',t)
docs=[{'url':'https://open-snapshot.muedsa.com/ai-guide.md','knowledge':'渲染接口/type 仅 png/jpg/webp','used_in':'A23/A24'},{'url':'https://snapshot.muedsa.com/reference/parser-tags.md','knowledge':'Container/Stack/Positioned/Transform','used_in':'全部布局'}]
frames_snap=[{'file':f'frame-{i:02d}.snapshot','purpose':f'帧{i} DSL','dsl':f'frame-{i:02d}.png','status':'完成'} for i in range(1,7)]
frames_png=[{'file':f'frame-{i:02d}.png','purpose':f'600×600 透明帧{i}','dsl':f'frame-{i:02d}.snapshot','status':'完成'} for i in range(1,7)]
frame_reviews=[{'image':f'outputs/{RUN}/A23/frame-0{i}.png','at':'2026-10-29T04:21:46+0800','result':'逐帧检查：12 单元、间距、透明背景与汇聚连续'} for i in range(1,7)]
T('A23',{'task_id':'A23','title':'格式边界下的动画分镜交付','status':'completed','stop_reason':'需求满足并完成视觉自检',
'design':'先依据指南确认服务只输出静态 png/jpg/webp，无 SVG/CMYK/GIF 参数。按授权交付 1200×800 RGB 封面与 6 张 600×600 透明关键帧：12 个单元（4 圆/4 方/4 环）属性跨帧守恒，沿各自径向轨迹从 1.75× 大三角汇聚到最终三角；250ms/帧、1500ms 循环，末帧→首帧为跳变并在 timing/frame-data/limitations 中明确。',
'requirements':[
 {'text':'判定格式支持并写 limitations','evidence':'limitations.md 四项请求/依据/替代/后续'},
 {'text':'1200×800 封面文字可读','evidence':'“从结构到画面”64px，实图可读'},
 {'text':'6 张透明 PNG、12 单元每帧、属性守恒','evidence':'frame-data.json；角 alpha=0；尺寸/颜色/alpha 不变'},
 {'text':'轨迹连续、末帧成可识别三角','evidence':'径向 smoothstep；6 帧间距 105→60，未重叠'},
 {'text':'250ms/帧、循环 1500ms、帧序','evidence':'timing.json'},
 {'text':'循环接缝说明','evidence':'seam max 135.2px；标注跳变，不称无缝'}],
'files':[{'file':'cover.snapshot','purpose':'封面 DSL','dsl':'cover.png','status':'完成'},{'file':'cover.png','purpose':'1200×800 封面','dsl':'cover.snapshot','status':'完成'}]+frames_snap+frames_png+
 [{'file':'limitations.md','purpose':'格式边界','dsl':'-','status':'完成'},{'file':'frame-data.json','purpose':'逐帧/轨迹/接缝','dsl':'-','status':'完成'},{'file':'timing.json','purpose':'帧时序','dsl':'-','status':'完成'}],
'reviews':[{'image':f'outputs/{RUN}/A23/cover.png','at':'2026-10-29T04:20:55+0800','result':'封面文字与三角构图完整'}]+frame_reviews+
 [{'image':f'tmp/{RUN}/A23/contact-sheet.png','at':'2026-10-29T04:21:32+0800','result':'3×2 接触表：三角形逐步收缩汇聚；末帧可识别'}],
'iterations':[{'id':'A23-v1','type':'baseline','parent':None,'dsl':f'tmp/{RUN}/A23/drafts/gen_a23.py','image':f'tmp/{RUN}/A23/contact-sheet.png','at':'2026-10-29T04:20:55+0800','problem':'线性路径中段碰撞','change':'改径向缩放轨迹','result':'通过'}],
'issues':[{'type':'visual','problem':'帧中段单元重叠','cause':'分散点到终点直线路径交叉','fix':'终点三角形按 1.75× 径向放大作为起点','verify':'最小中心距 60px；全部可见','evidence':f'outputs/{RUN}/A23/frame-data.json'}],
'notes':'动画格式不支持时按授权改为关键帧+timing；循环接缝必须如实标注，不能用 loop 掩饰跳变。','docs':docs})
T('A24',{'task_id':'A24','title':'双团队约束下的发布作战计划','status':'completed','stop_reason':'需求满足并完成视觉自检',
'design':'对 12 任务做 2 团队资源约束搜索：同团队串行、依赖满足、允许 R05/R09/R12 选队；得到 09:00 起、13:20 完成（260min），缓冲 160min，关键路径 255min、资源下界 242.5min。三图共用同一排程：1920×1080 泳道、1200×1600 决策简报、720×1280 行动卡；依赖以编号索引展示，不画满交叉线。',
'requirements':[
 {'text':'可行且尽早排程，12 任务完整时长','evidence':'schedule.json；conflicts=[], depbad=[], duration check True'},
 {'text':'依赖/团队/起止可读，空档与截止线','evidence':'泳道图与索引；16:00 截止线、缓冲带'},
 {'text':'关键路径与工作量下界；不称最优','evidence':'审计 255/242.5/260；proven_optimal false'},
 {'text':'三图一致、横屏≥20/竖页≥24/手机≥20','evidence':'同一 schedule；主要正文 20/22+'},
 {'text':'brief 风险/对策/依据','evidence':'K1-K3 + 排程依据'},
 {'text':'audit/content-map','evidence':'schedule-audit.json / content-map.json'}],
'files':[{'file':'execution-board.snapshot','purpose':'1920×1080 DSL','dsl':'execution-board.png','status':'完成'},{'file':'execution-board.png','purpose':'泳道执行图','dsl':'execution-board.snapshot','status':'完成'},
         {'file':'decision-brief.snapshot','purpose':'1200×1600 DSL','dsl':'decision-brief.png','status':'完成'},{'file':'decision-brief.png','purpose':'决策简报','dsl':'decision-brief.snapshot','status':'完成'},
         {'file':'action-card.snapshot','purpose':'720×1280 DSL','dsl':'action-card.png','status':'完成'},{'file':'action-card.png','purpose':'手机行动卡','dsl':'action-card.snapshot','status':'完成'},
         {'file':'schedule.json','purpose':'精确排程','dsl':'-','status':'完成'},{'file':'schedule-audit.json','purpose':'资源/依赖/下界审计','dsl':'-','status':'完成'},{'file':'content-map.json','purpose':'三图区域映射','dsl':'-','status':'完成'}],
'reviews':[{'image':f'outputs/{RUN}/A24/execution-board.png','at':'2026-10-29T04:25:11+0800','result':'泳道/缓冲/截止线完整；短块时间已改双行'},
           {'image':f'outputs/{RUN}/A24/decision-brief.png','at':'2026-10-29T04:25:11+0800','result':'KPI/关键路径/12 任务/风险完整；通过'},
           {'image':f'outputs/{RUN}/A24/action-card.png','at':'2026-10-29T04:23:17+0800','result':'12 任务时序、团队、风险徽标完整；通过'}],
'iterations':[{'id':'A24-v1','type':'baseline','parent':None,'dsl':f'tmp/{RUN}/A24/drafts/gen_a24.py','image':f'outputs/{RUN}/A24/execution-board.png','at':'2026-10-29T04:22:49+0800','problem':'缓冲带盖块、简报 KPI 压标题、短块时间断行','change':'重排缓冲/简报间距/短块时间双行','result':'通过'}],
'issues':[{'type':'visual','problem':'缓冲带覆盖 R12 边缘','cause':'绘制顺序','fix':'缓冲带先画并右移','verify':'R12 完整','evidence':f'outputs/{RUN}/A24/execution-board.png'},
           {'type':'visual','problem':'简报 KPI 压住章节标题；&amp; 实体','cause':'间距/转义','fix':'下移 KPI 与章节、改写标题','verify':'无重叠/无实体','evidence':f'outputs/{RUN}/A24/decision-brief.png'}],
'notes':'用搜索而非手排得到 260min 方案，并明确它不是已证明最优；三图共用一份 schedule。','docs':docs})
