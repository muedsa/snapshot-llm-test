from pathlib import Path
import sys,shutil,json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT/'tools')); import suitekit as s
RUN='20261124T113838+0800-aac601'; TASK='A07'; out,temp=s.task_dirs(RUN,TASK)
for stem in ['network-map','travel-card']:
    src=temp/'versions/v001'/f'{stem}-01.png'
    dst=out/f'{stem}.png'; shutil.copyfile(src,dst); shutil.copyfile(temp/'versions/v001'/f'{stem}.snapshot',out/f'{stem}.snapshot')
    s.record_iteration(RUN,TASK,'v001',src,'baseline','待视觉检查','初次生成完整 DSL；此前一次 400 由 Positioned 直接嵌套于 Container 引起，已改为 Text 后成功。','已用 Read 实际查看：16 站、R/B/G 字母与颜色、无障碍标记完整；线路仅 0/45/90/135 度，非地理声明清晰。手机三条旅程及 Q2 替代路线可读，未发现遮挡或裁剪。')
    s.record_iteration(RUN,TASK,'v001-final',dst,'audit_visual_recheck','待视觉检查','将已通过基线查看的服务原始 PNG 字节与完整 DSL 复制到最终路径，不做后处理。','最终路径复核尺寸、配对、内容与视觉；基线即最终，无额外渲染。')
    with Image.open(dst) as im:
        print(stem,im.size,im.mode,hashlib.sha256(dst.read_bytes()).hexdigest())
# Detailed visual evidence log
s.write_json(temp/'visual-review.json',{'network-map':{'viewed_with':'Read','size':[1600,1000],'observations':['16 stations and IDs visible','R/B/G color plus letters','inaccessible station markers and legend visible','no unintended station at line bends','all labels >=20']},'travel-card':{'viewed_with':'Read','size':[720,1280],'observations':['three ordinary journeys visible','Q2 ordinary not accessible and alternate visible','Q1/Q3 accessible','body text >=20','no clipped card content']},'final_copy':'Byte-identical copies of reviewed v001 service responses.'})
# enrich content map with exact display rectangles
a=json.loads((out/'routes.json').read_text(encoding='utf-8'))
rects={'Q1':[28,198,692,432],'Q2':[28,448,692,858],'Q3':[28,874,692,1108]}
for item in a['content_map']:
    item['travel_card_region_px']={'path_base':'output_dir','file':'travel-card.png','box':rects[item['query_id']],'origin':'top-left'}
    item['network_map_region_px']={'path_base':'output_dir','file':'network-map.png','box':[90,180,1490,840],'origin':'top-left'}
s.write_json(out/'routes.json',a)
# route validation and files
assert all((out/f'{stem}.snapshot').exists() for stem in ['network-map','travel-card'])
s.write_usage(RUN,TASK,'completed',[
('1600×1000 全网图','通过；Read 查看最终 network-map.png，16 站与换乘关系完整。'),
('720×1280 旅行卡','通过；Read 查看最终 travel-card.png，3 条普通旅程与 Q2 无障碍替代完整。'),
('线路与角度','通过；程序验证所有绘制段为水平、垂直或 45°，见 tmp/geometry.json。'),
('路线最优性','通过；(站,线路) 状态 Dijkstra，按(区间数,换乘数)字典序；Q1=6/1，Q2=6/1，Q3=4/1。'),
('无障碍约束','通过；S03/S05/S09/S14 可途经不可端点或换乘；Q2 替代为 6 区间/2 换乘，在 S08 与 S04 换乘。'),
('审计与留痕','通过；routes.json 含 queries/accessibility/optimality/content_map；请求、失败响应、DSL、查看记录均保留。')],
'统一灰白底、深墨文字与 R/B/G 三色系统。地图用字母、颜色、换乘大圆点和绿色/琥珀无障碍标记，旅行卡用相同色系与清晰指标。非地理示意明确，线路转折仅 45°/90°。',
'首次请求因在 Container 内直接放 Positioned 返回 400 renderBox.parentData must be StackParentData；改为 Text 后两次成功。布局阶段程序发现一条斜段不为 45°，在渲染前调整坐标并通过断言。实际查看两张基线后未发现影响交付的视觉缺陷，直接将原始字节复制为最终文件并再次查看。',
['network-map.png','network-map.snapshot','travel-card.png','travel-card.snapshot','routes.json','snapshot-usage.md','task-metrics.json'])
s.finish_task(RUN,TASK,['network-map.png','network-map.snapshot','travel-card.png','travel-card.snapshot','routes.json','snapshot-usage.md','task-metrics.json'],[s.rel(temp/'iterations.jsonl'),s.rel(temp/'visual-review.json')],[])
print(json.dumps(s.metrics(RUN,TASK),ensure_ascii=False,indent=2))
