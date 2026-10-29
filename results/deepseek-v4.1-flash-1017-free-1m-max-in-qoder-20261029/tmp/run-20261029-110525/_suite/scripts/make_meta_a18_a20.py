#!/usr/bin/env python3
import json
from pathlib import Path
RUN='run-20261029-110525'
def write(t,m):
    p=Path(f'tmp/{RUN}/{t}/drafts/meta.json'); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8'); print('meta',t)
docs=[{"url":"https://open-snapshot.muedsa.com/ai-guide.md","knowledge":"渲染接口与错误","used_in":"渲染"},
      {"url":"https://snapshot.muedsa.com/reference/parser-tags.md","knowledge":"Container/Stack/Positioned/Transform","used_in":"全部布局"}]
write('A18',{
 'task_id':'A18','title':'守恒对象的三幕视觉叙事','status':'completed','stop_reason':'需求满足并完成视觉自检',
 'design':'三幕并置 1600×1000：15 个 U01–U15 单元（蓝/橙/灰各 5、直径 36）与 3 个同形节点 N01–N03。第一幕三层环围绕 N01，第二幕挤压成 3×5 块且 N01 纵向 0.82 形变，第三幕三组各 5 个、每组混色。先做 A/B 两版 1600×1000 实际预览，看图选 A；连线先画、圆点后画，避免线遮圆。',
 'requirements':[
  {'text':'三幕各同一组 15 单元与 3 节点、ID 稳定','evidence':'story-audit.json U01–U15 / N01–N03；每幕 15+3'},
  {'text':'单元直径 36、不重叠、线不遮圆','evidence':'最小圆心距 40/49.79px；线在圆下绘制；审计计算'},
  {'text':'第三幕每节点 5 个且至少两色','evidence':'N01/N02/N03 各 5；组色 3/3/2 种'},
  {'text':'仅幕名与总标题；过载不用警告文字','evidence':'图中文字只有标题与 I/II/III 幕名'},
  {'text':'两版预览并选择','evidence':'tmp preview-a/b 均渲染查看；rationale 记录'},
  {'text':'400px 缩略仍可读','evidence':'thumb-400.png 已查看'}],
 'files':[{'file':'three-act-story.snapshot','purpose':'1600×1000 DSL','dsl':'three-act-story.png','status':'完成'},{'file':'three-act-story.png','purpose':'最终图','dsl':'three-act-story.snapshot','status':'完成'},{'file':'story-audit.json','purpose':'三幕坐标/接收/几何审计','dsl':'-','status':'完成'},{'file':'rationale.md','purpose':'叙事与选择说明','dsl':'-','status':'完成'}],
 'reviews':[{'image':f'tmp/{RUN}/A18/preview-a.png','at':'2026-10-29T04:10:08+0800','result':'三环/挤压/三分三幕清晰'},
            {'image':f'tmp/{RUN}/A18/preview-b.png','at':'2026-10-29T04:10:08+0800','result':'单环/单列/三角，第二幕过长'},
            {'image':f'outputs/{RUN}/A18/three-act-story.png','at':'2026-10-29T04:10:50+0800','result':'三幕完整、第三幕混色；通过'},
            {'image':f'tmp/{RUN}/A18/thumb-400.png','at':'2026-10-29T04:10:57+0800','result':'400px 宽仍能分辨三种构图'}],
 'iterations':[{'id':'A18-v1','type':'baseline','parent':None,'dsl':f'tmp/{RUN}/A18/drafts/gen_a18.py','image':f'tmp/{RUN}/A18/preview-a.png','at':'2026-10-29T04:10:08+0800','problem':'预览坐标错位','change':'卡片内坐标减去原点','result':'通过'},
             {'id':'A18-v2','type':'visual','parent':'A18-v1','dsl':f'outputs/{RUN}/A18/three-act-story.snapshot','image':f'outputs/{RUN}/A18/three-act-story.png','at':'2026-10-29T04:10:50+0800','problem':'第三幕按色分组','change':'改为混色五元组','result':'通过'}],
 'issues':[{'type':'visual','problem':'预览只显示第一幕','cause':'幕内绝对坐标未减卡片原点','fix':'改为卡片局部坐标','verify':'三幕完整','evidence':f'outputs/{RUN}/A18/three-act-story.png'},
           {'type':'logical','problem':'第三幕各组单色','cause':'按 ID 顺序切成三组','fix':'GIDS 混色分组','verify':'每组≥2色','evidence':f'outputs/{RUN}/A18/story-audit.json'}],
 'notes':'守恒叙事用同一组 ID/尺寸，先画线后画圆保证线不遮圆；过载用间距与节点形变表达，不用文字。','docs':docs})
write('A19',{
 'task_id':'A19','title':'构造可核验的视觉题场','status':'completed','stop_reason':'需求满足并完成视觉自检',
 'design':'8×8 网格 64 对象，固定种子 0 的平衡分配：4 色×4 形各 16、16 组合全覆盖、每色/每形含 48/64/80、每行≥3 色≥3 形；圆环内径为外径一半。另做 800×800 遮挡 A/B：可见前景相同，隐藏内容不同且完全被不透明板覆盖，两 PNG 像素数组完全相同。12+2 题与答案/方法/坐标容差写入 JSON。',
 'requirements':[
  {'text':'1600×1600、8×8、G01–G64、每格一个主体','evidence':'grid-scene.png；64 对象'},
  {'text':'4 色/4 形各 16、全组合覆盖、每色每形三尺寸','evidence':'scene-data.json 频数与组合'},
  {'text':'每行≥3 色≥3 形、圆环内径一半、编号外置','evidence':'scene-data rows；ring 厚度 0.25×外径'},
  {'text':'12 题覆盖复合/关系/距离/排序/包围框/计数，≥4 两步','evidence':'questions.json Q1–Q12'},
  {'text':'遮挡 A/B 可见相同、隐藏不同、不能虚线泄漏','evidence':'equivalence.json 像素差 0；隐藏位于不透明板内'},
  {'text':'2 道遮挡题，至少 1 题答案“无法确定”','evidence':'OQ1 无法确定；OQ2 可见橙圆 1'},
  {'text':'scene/questions/answers/equivalence 四 JSON','evidence':'四文件完整'}],
 'files':[{'file':'grid-scene.snapshot','purpose':'网格 DSL','dsl':'grid-scene.png','status':'完成'},{'file':'grid-scene.png','purpose':'1600×1600 题场','dsl':'grid-scene.snapshot','status':'完成'},
          {'file':'occlusion.snapshot','purpose':'遮挡 A DSL','dsl':'occlusion.png','status':'完成'},{'file':'occlusion.png','purpose':'800×800 A','dsl':'occlusion.snapshot','status':'完成'},
          {'file':'occlusion-alternative.snapshot','purpose':'遮挡 B DSL','dsl':'occlusion-alternative.png','status':'完成'},{'file':'occlusion-alternative.png','purpose':'800×800 B','dsl':'occlusion-alternative.snapshot','status':'完成'},
          {'file':'scene-data.json','purpose':'种子/频数/几何','dsl':'-','status':'完成'},{'file':'questions.json','purpose':'14 题','dsl':'-','status':'完成'},{'file':'answers.json','purpose':'答案与方法','dsl':'-','status':'完成'},{'file':'equivalence.json','purpose':'遮挡像素等价','dsl':'-','status':'完成'}],
 'reviews':[{'image':f'outputs/{RUN}/A19/grid-scene.png','at':'2026-10-29T04:12:19+0800','result':'形状被网格原点偏移，部分格子空'},
            {'image':f'outputs/{RUN}/A19/grid-scene.png','at':'2026-10-29T04:12:47+0800','result':'64 对象归位、圆环内径一半；通过'},
            {'image':f'outputs/{RUN}/A19/occlusion.png','at':'2026-10-29T04:12:19+0800','result':'可见前景完整、遮挡板不透明'},
            {'image':f'outputs/{RUN}/A19/occlusion-alternative.png','at':'2026-10-29T04:12:53+0800','result':'与 A 像素完全相同；通过'}],
 'iterations':[{'id':'A19-v1','type':'baseline','parent':None,'dsl':f'tmp/{RUN}/A19/drafts/gen_a19.py','image':f'outputs/{RUN}/A19/grid-scene.png','at':'2026-10-29T04:12:19+0800','problem':'形状偏移 160px','change':'shape 坐标减网格原点','result':'通过'},
             {'id':'A19-v2','type':'visual','parent':'A19-v1','dsl':f'outputs/{RUN}/A19/grid-scene.snapshot','image':f'outputs/{RUN}/A19/grid-scene.png','at':'2026-10-29T04:12:47+0800','problem':'圆环内径不是一半','change':'环厚 0.25×外径','result':'通过'}],
 'issues':[{'type':'visual','problem':'64 对象错位/空格','cause':'形状使用页面坐标放入网格 Stack','fix':'减网格原点','verify':'64 格全部有对象','evidence':f'outputs/{RUN}/A19/grid-scene.png'},
           {'type':'visual','problem':'圆环内径不为一半','cause':'环厚 18%','fix':'25% 外径','verify':'内径=外径/2','evidence':f'outputs/{RUN}/A19/grid-scene.png'}],
 'notes':'遮挡等价要做到可见层与渲染参数完全一致、隐藏层不外溢；同字节 PNG 是更强证据但不是要求。','docs':docs})
write('A20',{
 'task_id':'A20','title':'二十四密集点的无重叠标注','status':'completed','stop_reason':'需求满足并完成视觉自检',
 'design':'1600×1100 示意地图，24 点严格按 px=280+10.4×x、py=920−7.6×y 映射。标签按 x 中位数分左右两侧，各 12 个、180×40、行距 56；引导线从点圆周连到自身标签边。审计计算：标签间距最小 16px、线穿标签 0、线穿非本点 0、引导线交叉 1（M21/M07，≤3）、边界通过；最高 3 个 M10 93 / M08 91 / M23 90 用金环。中心 6 点放大检查。',
 'requirements':[
  {'text':'1600×1100、主图 1040×760、24 点 d12 精确映射','evidence':'label-layout.json anchor_px 与公式'},
  {'text':'每点 ID/name/value 可读、标签不遮点','evidence':'24 标签 20px；线穿点 0；标签在外侧'},
  {'text':'标签盒间距≥4、线不穿标签；>24px 有引导线','evidence':'最小间距 16px；线穿标签 0；全部>24'},
  {'text':'引导线交叉≤3、不连错点','evidence':'1 处交叉 M21/M07；端点各自身标签'},
  {'text':'坐标轴/范围/单位/最高3','evidence':'0–100 轴、指数、金环 M10/M08/M23'},
  {'text':'放大中心 6 点与整体查看','evidence':'zoom-center.png 与全图已查看'}],
 'files':[{'file':'annotated-map.snapshot','purpose':'1600×1100 DSL','dsl':'annotated-map.png','status':'完成'},{'file':'annotated-map.png','purpose':'最终图','dsl':'annotated-map.snapshot','status':'完成'},{'file':'label-layout.json','purpose':'锚点/标签盒/引导线','dsl':'-','status':'完成'},{'file':'layout-audit.json','purpose':'几何审计','dsl':'-','status':'完成'}],
 'reviews':[{'image':f'outputs/{RUN}/A20/annotated-map.png','at':'2026-10-29T04:14:25+0800','result':'轴标签缺失、点/标签偏移'},
            {'image':f'outputs/{RUN}/A20/annotated-map.png','at':'2026-10-29T04:14:45+0800','result':'24 标签/线/轴完整；1 处交叉'},
            {'image':f'tmp/{RUN}/A20/zoom-center.png','at':'2026-10-29T04:14:58+0800','result':'中心 6 点清楚、线不穿圆、标签不遮点'}],
 'iterations':[{'id':'A20-v1','type':'baseline','parent':None,'dsl':f'tmp/{RUN}/A20/drafts/gen_a20.py','image':f'outputs/{RUN}/A20/annotated-map.png','at':'2026-10-29T04:14:25+0800','problem':'轴标签被裁剪、点偏移','change':'轴与覆盖层改页面坐标','result':'通过'}],
 'issues':[{'type':'visual','problem':'x/y 轴标签缺失','cause':'在 Map Stack 外溢被裁剪','fix':'页面级重绘刻度','verify':'0–100 双轴完整','evidence':f'outputs/{RUN}/A20/annotated-map.png'},
           {'type':'visual','problem':'点与标签偏移','cause':'页面坐标放入 Map Stack','fix':'Map 只画网格，覆盖层页面级','verify':'锚点对齐','evidence':f'outputs/{RUN}/A20/label-layout.json'}],
 'notes':'侧栏标签+直线引导在本题点分布下仅 1 处交叉；标签行距 56、盒高 40 保证 16px 间距。','docs':docs})
