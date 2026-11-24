from pathlib import Path
import sys,shutil,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT/'tools')); import suitekit as s
RUN='20261124T113838+0800-aac601'; TASK='A08'; out,temp=s.task_dirs(RUN,TASK)
v1=temp/'versions/v001/wayfinding-01.png'; v2=temp/'versions/v002/wayfinding-01.png'
shutil.copyfile(v2,out/'wayfinding.png'); shutil.copyfile(temp/'versions/v002/wayfinding.snapshot',out/'wayfinding.snapshot')
s.record_iteration(RUN,TASK,'v001',v1,'baseline','图例只写 S/E 边界门洞，未明确显示“入口/出口”名称。','初版路线、网格和共享通道已生成。','实际 Read 整图后发现门洞名称可更明确，计划修改图例。')
s.record_iteration(RUN,TASK,'v002',v2,'visual','无影响交付的问题。','图例改为“S 入口 / E 出口”，其余几何与路线不变。','Read 整图确认 26×16 网格、44px 方格、双路线、地标、坐标和比例尺完整。')
for stem in ['entry-shared','exit-shared','landmarks']:
    s.record_iteration(RUN,TASK,'v002-'+stem,temp/'versions/v002'/f'{stem}.png','audit_visual_recheck','待视觉检查','从真实服务 PNG 生成 2 倍最近邻检查预览；最终图不后处理。','已实际 Read 放大预览：共享段两种线型与方向箭头均可追踪，地标遮挡处两侧接续清楚。')
a=json.loads((out/'paths.json').read_text(encoding='utf-8'))
for item in a['audit']:
    if item['check']=='image_review':
        item['passed']=True; item['method']='Read full service image and 2x nearest-neighbor crops of entry shared run, exit shared run and landmarks; previews are inspection-only.'
        item['evidence']={'path_base':'suite_root','paths':[s.rel(temp/'versions/v002/entry-shared.png'),s.rel(temp/'versions/v002/exit-shared.png'),s.rel(temp/'versions/v002/landmarks.png')]}
a['research_note']=' Preliminary hint that both routes might be 47 steps was tested and rejected: BFS gives R1=35 steps/70m and R2=47 steps/94m. Both have unique shortest solutions and share the entry and exit runs, not a fabricated branch.'
s.write_json(out/'paths.json',a); s.write_json(temp/'computed-paths.json',a)
s.write_usage(RUN,TASK,'completed',[
('1560×1080 与网格','通过；26×16 全部显示，单格 44px，原点(72,220)，阻挡格与门洞保留。'),
('路线计算','通过；BFS 唯一最短：R1=35步/70米，R2=47步/94米；R2分段19+16+12。研究提示“均47”经程序验证不成立，已如实记录。'),
('共享通道','通过；入馆9步、离馆8步；同中心青绿实线+洋红虚线，0px偏移，方向箭头错边排布。'),
('地标与文字','通过；S/E/A–D固定在格心，名称在侧栏/图例，正文22、图例20、坐标16。'),
('实际看图','通过；Read 整图及两个共享段、地标放大预览，未见路线穿墙、覆盖文字或追踪中断。'),
('审计交付','通过；paths.json 删除 field_guide，包含完整序列、分段、共享段、坐标/绘制和计算依据。')],
'深墨墙体、白色通道与黄色门洞形成清晰展馆结构。R1 青绿实线、R2 洋红虚线使用颜色加线型；共享段保留双层可辨身份，白色雪佛龙箭头在起点、转弯、合流及共享段交错出现。右侧栏集中呈现路线与地标，底部保留图例和比例尺。',
'初次实际查看发现 S/E 只标为边界门洞，缺少明确入口/出口名称；v002 将图例改为“S 入口 / E 出口”并重新渲染查看。计算阶段否定了外部研究提示中的“两路线均47步”：真实 BFS 为 R1 35步、R2 47步，未为迎合提示修改输入或路径。',
['wayfinding.png','wayfinding.snapshot','paths.json','snapshot-usage.md','task-metrics.json'])
with Image.open(out/'wayfinding.png') as im: print(im.size,im.mode)
print(json.dumps(s.metrics(RUN,TASK),ensure_ascii=False,indent=2))
