from pathlib import Path
import sys,json,hashlib,re
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT/'tools')); import suitekit as s
RUN='20261124T113838+0800-aac601'; TASK='A09'; out,temp=s.task_dirs(RUN,TASK)
raw=temp/'versions/v001/transform-atlas-01.png'; final=out/'transform-atlas.png'; dslp=out/'transform-atlas.snapshot'
assert raw.read_bytes()==final.read_bytes(); assert dslp.read_bytes()==(temp/'versions/v001/transform-atlas.snapshot').read_bytes()
im=Image.open(final); assert im.size==(1600,1200) and im.format=='PNG'
dsl=dslp.read_text(encoding='utf-8'); assert dsl.count('<Transform matrix=')==12; assert dsl.count('<Snapshot ')==1
mats=re.findall(r'<Transform matrix="([^"]+)"',dsl); assert all(len(m.split())==16 for m in mats)
sizes=[float(x) for x in re.findall(r'fontSize="([0-9.]+)"',dsl)]; assert sizes and min(sizes)>=20
a=json.loads((out/'geometry-audit.json').read_text(encoding='utf-8')); assert a['schema_version']==1 and a['task_id']==TASK and a['path_base']=='output_dir'; assert len(a['transforms'])==len(a['geometry'])==len(a['verification'])==12 and a['summary']['all_12_passed']
for r in a['geometry']:
    assert all(len(g['canvas_corners_tl_tr_br_bl'])==4 for g in r['rectangles']) and r['canvas_outer_bbox']
checks={'sha256_png':hashlib.sha256(final.read_bytes()).hexdigest(),'sha256_dsl':hashlib.sha256(dslp.read_bytes()).hexdigest(),'dimensions':list(im.size),'matrix_elements_per_transform':[len(m.split()) for m in mats],'minimum_label_font_px':min(sizes),'all_12_component_checks_passed':True,'original_service_bytes_preserved':True,'final_dsl_matches_rendered_dsl':True}
s.write_json(temp/'final-validation.json',checks)
notes={'task_id':TASK,'attempts':[{'kind':'local_build_error','detail':'operation short-name dictionary eagerly indexed a scalar scale value; fixed with explicit operation branches before any service call.'},{'kind':'service_parse_error','http_status':400,'detail':'multiple Positioned nodes were placed in a single-child Container. Replaced the stamp wrapper with Stack under Transform; failed request and response remain in requests.jsonl.'},{'kind':'successful_render','http_status':200,'detail':'real PNG response preserved byte-for-byte.'},{'kind':'audit_method_refinement','detail':'pixel color masks use component-local 3 px halos and 0.5 px pixel-edge expansion; broad whole-cell thresholds were rejected after detecting cross-color contamination. Final method gives max component error 1.25 px.'},{'kind':'preview_coordinate_fix','detail':'the first T07/T08 comparison crop selected neighboring cells; corrected reproducible crop to x=830..1430, y=470..742 and visually reopened it.'}],'unresolved_issues':[]}
s.write_json(temp/'process-notes.json',notes)
# Actual Read events: candidate, overview, corrected order pair, T10/T11/T12, final.
cand=temp/'versions/v001/transform-atlas-01.png'
s.record_iteration(RUN,TASK,'v001',cand,'syntax-fix','首个服务请求因单 child Container 中放入多个 Positioned 返回 HTTP 400；修正后的候选无影响交付的问题。','将印章子节点包装改为 Stack，保留全部源局部坐标，并仅通过最终 Transform.matrix 定位。','修复后真实服务返回 200；候选图已实际打开。')
s.record_iteration(RUN,TASK,'v001',cand,'baseline','无影响交付的问题。','首版合格，未制造无意义重渲染。','4×3 布局、十二个操作、矩阵变换结果与刻度辅助线均符合要求。')
for name,obs in [('inspect-overview.png','缩小总览中无裁切、无重叠，标签与图例可读。'),('inspect-order-pair.png','T07/T08 并列可见，操作顺序确实产生不同朝向。'),('inspect-T10.png','非均匀缩放后黑点呈横向椭圆，矩形比例同步改变。'),('inspect-T11.png','顺时针30°主体边缘与预测外接框一致。'),('inspect-T12.png','上下镜像后顺时针30°与T11不同，圆点位置正确。')]:
    s.record_iteration(RUN,TASK,'v001',temp/name,'visual',obs,'仅生成用于检查的局部预览，不修改最终 PNG。','局部预览已实际打开，与矩阵预测和 geometry-audit.json 一致。')
s.record_iteration(RUN,TASK,'v001',final,'audit_visual_recheck','无影响交付的问题；所有变换主体均未裁切，全部标签≥20。','无需进一步修改；最终 PNG 保持服务原始字节。','最终输出图已实际打开；逐格像素审计12/12通过，最大分量误差1.25px，角点探针最大1.414px。')
design='1600×1200 画布采用4×3网格，300×250单元格与32px间距；网格横向和纵向中心均为画布中心。每个标本在完整画布 Positioned 中使用一个列主序4×4 Transform.matrix，源印章坐标完全不改，圆点与三矩形共同变换。浅色十字、中心点和±60刻度提供局部坐标参照；卡片、标题与图例留在格外。图像坐标中顺时针旋转使用标准正角度矩阵。T07/T08通过先后顺序明确展示不可交换性，T10通过同一矩阵自然形成椭圆。'
issues='初次服务渲染的400解析错误已定位并修复，失败请求/响应完整保留。像素核验没有放宽几何容差：最终按分量检查左/上/右/下，最大误差1.25px，小于1.5px；角点诊断最大1.414px。审计脚本明确记录反走样边缘例外规则，未把任何超差探针用于掩盖主体误差。初版局部对比裁切坐标错误已修正，并重新实际查看正确的T07/T08并列图。无未解决问题。'
s.write_usage(RUN,TASK,'completed',[('真实服务与原始字节','2次渲染请求：1次400、1次200；最终PNG与版本PNG SHA-256完全一致。'),('布局与尺寸','1600×1200；4列×3行；300×250；间距32；网格中心(800,600)。'),('矩阵与源坐标','12个Transform.matrix，每个16个数；三矩形和圆点均从未修改源坐标的Stack变换。'),('变换数据','T01–T12按输入顺序围绕(60,60)组合；T07/T08线性部分不同；T10圆点椭圆半径[10,6]。'),('几何审计','12/12通过；逐矩形四角、圆点中心/椭圆、最终外接框齐全；最大分量误差1.25px≤1.5px。'),('可读性与视觉','全部文字20–38px；总览、T07/T08并列、T10/T11/T12局部及最终图均已实际打开。'),('文件与留痕','PNG/DSL配对，完整请求、失败响应、脚本、审计、预览与查看记录保留；无未解决事项。')],design,issues,['transform-atlas.png','transform-atlas.snapshot','geometry-audit.json','snapshot-usage.md','task-metrics.json'])
s.finish_task(RUN,TASK,['transform-atlas.png','transform-atlas.snapshot','geometry-audit.json','snapshot-usage.md','task-metrics.json'],[s.rel(cand),s.rel(temp/'inspect-overview.png'),s.rel(temp/'inspect-order-pair.png'),s.rel(temp/'inspect-T10.png'),s.rel(temp/'inspect-T11.png'),s.rel(temp/'inspect-T12.png'),s.rel(final)])
m=s.metrics(RUN,TASK); print(json.dumps(m,ensure_ascii=False))
