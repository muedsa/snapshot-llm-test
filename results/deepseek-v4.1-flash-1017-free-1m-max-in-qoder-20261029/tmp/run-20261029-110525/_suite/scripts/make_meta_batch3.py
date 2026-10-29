#!/usr/bin/env python3
import json, os
from pathlib import Path
SCRIPT = Path(__file__).resolve(); SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4])); RUN = SCRIPT.parents[2].name
T = f"tmp/{RUN}"
def write(task, meta):
    p = SUITE_ROOT / "tmp" / RUN / task / "drafts" / "meta.json"; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"); print("meta", task)
docs = [
 {"url":"https://open-snapshot.muedsa.com/ai-guide.md","knowledge":"POST /snapshot 文本请求、图片响应、错误处理","used_in":"渲染"},
 {"url":"https://snapshot.muedsa.com/reference/parser-tags.md","knowledge":"Transform/Container/Stack/Text/滤镜/裁剪属性","used_in":"全部 DSL"},
 {"url":"https://snapshot.muedsa.com/reference/parser-text.md","knowledge":"fontSize、fontStyle、文本换行","used_in":"文字排版"},
]
write("A09", {
 "task_id":"A09","title":"十二个非对称图形变换标本","status":"completed","stop_reason":"需求满足并完成视觉自检",
 "design":"4×3 网格，每格 300×250、间距 32，整体在 1600×1200 居中。印章的 3 个矩形与圆点全部放在同一个 Transform.matrix 子树中；12 个矩阵由操作列表按顺序组合（围绕 60,60），T07/T08 顺序不同、矩阵与外接框不同。格内十字与 50px 刻度辅助核对。",
 "requirements":[
  {"text":"4×3、每格 300×250、间距 32、整体居中","evidence":"网格起点 152,260；总宽 1296、总高 814"},
  {"text":"12 个变换按列表顺序、围绕 (60,60)","evidence":"geometry-audit.json 每个矩阵与操作序列；T07/T08 矩阵不同"},
  {"text":"每格主体用 Transform.matrix，圆点随同变换","evidence":"每格一个 Transform.matrix，矩形与圆点都在其子树"},
  {"text":"编号/短名/刻度辅助线齐全、不裁切","evidence":"每格 ID 22px、短名 20px、十字与 50px 刻度；clipBehavior=NONE"},
  {"text":"geometry-audit.json 矩阵/四角/圆心/外接框与 ±1.5px 核对","evidence":"pixel_check 12 格全部通过，最大偏差 1.11px"}
 ],
 "files":[{"file":"transform-atlas.snapshot","purpose":"1600×1200 DSL","dsl":"transform-atlas.png","status":"完成"},{"file":"transform-atlas.png","purpose":"最终图","dsl":"transform-atlas.snapshot","status":"完成"},{"file":"geometry-audit.json","purpose":"矩阵与像素核对","dsl":"-","status":"完成"}],
 "reviews":[{"image":f"outputs/{RUN}/A09/transform-atlas.png","at":"2026-10-29T11:37:23+0800","result":"12 格与矩阵方向正确；顶部留白偏大"},{"image":f"outputs/{RUN}/A09/transform-atlas.png","at":"2026-10-29T11:37:52+0800","result":"网格上移、加读法后平衡；12 格完整，通过"}],
 "iterations":[{"id":"A09-v1","type":"baseline","parent":None,"dsl":f"{T}/A09/drafts/gen_a09.py","image":f"outputs/{RUN}/A09/transform-atlas.png","at":"2026-10-29T11:37:23+0800","problem":"顶部留白过大","change":"网格上移、加读法说明","result":"通过"}],
 "issues":[{"type":"visual","problem":"顶部留白偏大","cause":"网格起点 300、内容高度 814","fix":"起点改 260 加读法行","verify":"布局平衡","evidence":f"outputs/{RUN}/A09/transform-atlas.png"}],
 "notes":"矩阵按列主序输出；像素核对用 alpha>200 的非背景色外接框，旋转格容差 1.5px。","docs":docs,
})
write("A10", {
 "task_id":"A10","title":"透明合成与滤镜语义实验板","status":"completed","stop_reason":"需求满足并完成视觉自检",
 "design":"1440×1100 六格实验板，3×2、320×240 白底。①②对照 alpha 与组 opacity；③④共用条纹+卡片场景，仅改变模糊作用层；⑤⑥共用 MULTIPLY+sigma6 场景，⑥额外 ClipOval r100。理论 alpha 计算与最终 PNG 像素采样写入 composite-audit.json。",
 "requirements":[
  {"text":"六格 320×240、3×2、间距≥32、说明在区外","evidence":"格原点 (200/560/920, 190/470)，间距 40；下方说明卡"},
  {"text":"①②重叠处 RGB 理论/实际与 128/255 vs 0.5 解释","evidence":"①(127,63,191) 采样一致；②(128,128,255) 实测(126,126,255)，误差≤2"},
  {"text":"③④仅改变模糊层、共用参数","evidence":"pair_sharing 记录；③文字清晰、④文字糊"},
  {"text":"⑤⑥共享场景与参数、⑥圆裁","evidence":"⑤无圆裁、⑥ ClipOval (160,120) r100；黄色形状跨圆周"},
  {"text":"说明文字≥20","evidence":"说明条 20px"},
  {"text":"③–⑥视觉判断引用实际图","evidence":"visual_checks 五条，含坐标与观察"}
 ],
 "files":[{"file":"compositing-lab.snapshot","purpose":"1440×1100 DSL","dsl":"compositing-lab.png","status":"完成"},{"file":"compositing-lab.png","purpose":"最终图","dsl":"compositing-lab.snapshot","status":"完成"},{"file":"composite-audit.json","purpose":"像素与滤镜审计","dsl":"-","status":"完成"}],
 "reviews":[{"image":f"outputs/{RUN}/A10/compositing-lab.png","at":"2026-10-29T11:40:18+0800","result":"⑤的滤镜溢出格子上方并遮住标签"},{"image":f"outputs/{RUN}/A10/compositing-lab.png","at":"2026-10-29T11:40:43+0800","result":"六格清晰、③④与⑤⑥对照可辨；通过"}],
 "iterations":[{"id":"A10-v1","type":"baseline","parent":None,"dsl":f"{T}/A10/drafts/gen_a10_v2.py","image":f"outputs/{RUN}/A10/compositing-lab.png","at":"2026-10-29T11:40:18+0800","problem":"滤镜输出越出格子并遮挡标签","change":"每格 ClipRect 限制 320×240","result":"通过"}],
 "issues":[{"type":"visual","problem":"⑤⑥模糊外溢、遮住标签","cause":"ImageFiltered 输出边界扩展","fix":"单元格 ClipRect","verify":"标签与格子边界恢复","evidence":f"outputs/{RUN}/A10/compositing-lab.png"}],
 "notes":"alpha 128/255 与 group opacity 0.5 的差异可被像素验证；BackdropFilter 与 ImageFiltered 的作用层差异必须用同一场景对照。","docs":docs,
})
write("A11", {
 "task_id":"A11","title":"文字保真与跨页结算单","status":"completed","stop_reason":"需求满足并完成视觉自检",
 "design":"两页 1200×1600 结算单。第 1 页展示双方、编号/日期/币种、四行明细、五步计税顺序与应付；金额用 Decimal 定点、ROUND_HALF_UP 至分，列右对齐。第 2 页四条 notes 与四条 literal_lines 用 CDATA 原样排版，保留双空格、反斜杠与尖括号；PAID / 已结算为嵌套 Text 富文本，斜线用 Raw 保留空格。",
 "requirements":[
  {"text":"两页 1200×1600、编号/页眉/页码一致","evidence":"页码 01/02、02/02；编号一致"},
  {"text":"四行 SKU/名称/数量/单价/行金额与汇总","evidence":"805.50/478.80/1,160.00/1,680.00；小计 4,124.30"},
  {"text":"严格计税顺序与定点四舍五入","evidence":"折扣后 3,944.30；税 236.66；运费 35.00；应付 4,215.96"},
  {"text":"金额小数点列对齐","evidence":"所有金额两位小数、右对齐"},
  {"text":"notes 与 literal_lines 逐字符保真","evidence":"CDATA；批次双空格、路径反斜杠、A<B&C>D 均原样"},
  {"text":"PAID / 已结算富文本共基线、不改应付","evidence":"嵌套 Text + Raw 斜线；应付仍 4,215.96"},
  {"text":"正文≥24、脚注≥20、边距 48","evidence":"正文 24、说明 20、边距 48"},
  {"text":"invoice-audit.json 与 text-map.json","evidence":"两文件完整"}
 ],
 "files":[{"file":"invoice-page-01.snapshot","purpose":"第 1 页 DSL","dsl":"invoice-page-01.png","status":"完成"},{"file":"invoice-page-01.png","purpose":"结算与明细","dsl":"invoice-page-01.snapshot","status":"完成"},{"file":"invoice-page-02.snapshot","purpose":"第 2 页 DSL","dsl":"invoice-page-02.png","status":"完成"},{"file":"invoice-page-02.png","purpose":"说明与原样文字","dsl":"invoice-page-02.snapshot","status":"完成"},{"file":"invoice-audit.json","purpose":"金额与字面审计","dsl":"-","status":"完成"},{"file":"text-map.json","purpose":"段落位置与字体","dsl":"-","status":"完成"}],
 "reviews":[{"image":f"outputs/{RUN}/A11/invoice-page-01.png","at":"2026-10-29T11:41:49+0800","result":"SKU 被转义成实体、应付金额换行"},{"image":f"outputs/{RUN}/A11/invoice-page-01.png","at":"2026-10-29T11:43:55+0800","result":"SKU 原样、应付一行；通过"},{"image":f"outputs/{RUN}/A11/invoice-page-02.png","at":"2026-10-29T11:42:00+0800","result":"说明中 &amp; 可见、PAID 斜线空格偏紧"},{"image":f"outputs/{RUN}/A11/invoice-page-02.png","at":"2026-10-29T11:44:16+0800","result":"和号文案与 Raw 斜线修正；通过"}],
 "iterations":[{"id":"A11-v1","type":"baseline","parent":None,"dsl":f"{T}/A11/drafts/gen_a11.py","image":f"outputs/{RUN}/A11/invoice-page-01.png","at":"2026-10-29T11:41:49+0800","problem":"实体转义与金额换行","change":"CDATA SKU、金额宽度/字号","result":"通过"},{"id":"A11-v2","type":"visual","parent":"A11-v1","dsl":f"outputs/{RUN}/A11/invoice-page-02.snapshot","image":f"outputs/{RUN}/A11/invoice-page-02.png","at":"2026-10-29T11:44:16+0800","problem":"&amp; 与斜线空格","change":"改文案、Raw 斜线","result":"通过"}],
 "issues":[{"type":"visual","problem":"SKU A<B&C>D 被转义为实体","cause":"T() 对 &<> 做 HTML 转义而 Parser 不解码实体","fix":"TRaw 使用 CDATA","verify":"页面显示原字符","evidence":f"outputs/{RUN}/A11/invoice-page-01.png"}],
 "notes":"Parser 不做实体解码；含 <、& 的文本必须 CDATA。金额对齐用固定宽度右对齐+两位小数即可。","docs":docs,
})
write("A12", {
 "task_id":"A12","title":"四断点完整内容视觉系统","status":"completed","stop_reason":"需求满足并完成视觉自检",
 "design":"同一内容模型生成 360×800、768×1024、1440×900、1920×1080 四画布。统一深色 24px 圆角头部、三根信号条、白卡编号体系与页脚；手机单列 6 卡，平板 2×3，桌面与大屏 3×2。标题/副标题/日期/时间/地点/CTA/网站与六张卡 title/detail 全部保留，无省略号。",
 "requirements":[
  {"text":"四尺寸完整内容、无裁切/拉伸","evidence":"四张 PNG 实际尺寸；六卡标题与 detail 全部出现"},
  {"text":"手机正文≥16、卡标题≥18；其余正文≥20、主标题≥40","evidence":"手机 16/18、平板 20/44、桌面 20/64、大屏 22/88"},
  {"text":"安全边距手机16/其他32、文字盒不重叠","evidence":"content-map.json 坐标；实图复查"},
  {"text":"统一色彩/形态/层级","evidence":"同一 design-tokens 色板、头部、信号条、卡片"},
  {"text":"design-tokens.json 与 content-map.json","evidence":"两文件完整；map 逐字段 original/displayed/box/size/complete"}
 ],
 "files":[{"file":"mobile.snapshot","purpose":"360×800 DSL","dsl":"mobile.png","status":"完成"},{"file":"mobile.png","purpose":"窄手机","dsl":"mobile.snapshot","status":"完成"},{"file":"tablet.snapshot","purpose":"768×1024 DSL","dsl":"tablet.png","status":"完成"},{"file":"tablet.png","purpose":"平板","dsl":"tablet.snapshot","status":"完成"},{"file":"desktop.snapshot","purpose":"1440×900 DSL","dsl":"desktop.png","status":"完成"},{"file":"desktop.png","purpose":"桌面","dsl":"desktop.snapshot","status":"完成"},{"file":"stage.snapshot","purpose":"1920×1080 DSL","dsl":"stage.png","status":"完成"},{"file":"stage.png","purpose":"大屏","dsl":"stage.snapshot","status":"完成"},{"file":"design-tokens.json","purpose":"色板/字号/间距/组件","dsl":"-","status":"完成"},{"file":"content-map.json","purpose":"四画布字段映射","dsl":"-","status":"完成"}],
 "reviews":[{"image":f"outputs/{RUN}/A12/mobile.png","at":"2026-10-29T11:45:54+0800","result":"页眉重叠、页脚相撞"},{"image":f"outputs/{RUN}/A12/mobile.png","at":"2026-10-29T11:50:05+0800","result":"页眉/卡片/页脚全部可读；通过"},{"image":f"outputs/{RUN}/A12/tablet.png","at":"2026-10-29T11:48:57+0800","result":"页脚左右相撞"},{"image":f"outputs/{RUN}/A12/tablet.png","at":"2026-10-29T11:50:05+0800","result":"页脚分离；通过"},{"image":f"outputs/{RUN}/A12/desktop.png","at":"2026-10-29T11:49:06+0800","result":"布局完整、页脚不撞；通过"},{"image":f"outputs/{RUN}/A12/stage.png","at":"2026-10-29T11:50:09+0800","result":"布局完整、页脚不撞；通过"}],
 "iterations":[{"id":"A12-v1","type":"baseline","parent":None,"dsl":f"{T}/A12/drafts/gen_a12.py","image":f"outputs/{RUN}/A12/mobile.png","at":"2026-10-29T11:45:54+0800","problem":"手机页眉重叠/页脚相撞","change":"头部增高、标题下移、手机页脚合并","result":"通过"},{"id":"A12-v2","type":"visual","parent":"A12-v1","dsl":f"outputs/{RUN}/A12/tablet.snapshot","image":f"outputs/{RUN}/A12/tablet.png","at":"2026-10-29T11:48:57+0800","problem":"平板页脚左右相撞","change":"左页脚仅网站、右页脚放尺寸","result":"通过"}],
 "issues":[{"type":"visual","problem":"手机页眉 eyebrow 与标题重叠、页脚左右相撞","cause":"title_dy 过小、页脚同排","fix":"增高头部、下移标题、页脚合并","verify":"最终图可读","evidence":f"outputs/{RUN}/A12/mobile.png"},{"type":"transport","problem":"stage 首次渲染 TypeError terminated","cause":"传输中断（非 DSL）","fix":"同 DSL 重试","verify":"第二次 200","evidence":"tmp/requests.jsonl"}],
 "notes":"响应式由同一内容与参数生成；卡片高度需按最长标题 2 行 + detail 1 行预留，foot 不抢正文空间。","docs":docs,
})
