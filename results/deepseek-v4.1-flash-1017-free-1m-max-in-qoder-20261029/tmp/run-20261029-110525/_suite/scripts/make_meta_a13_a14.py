#!/usr/bin/env python3
import json
from pathlib import Path
RUN = 'run-20261029-110525'
def write(t, m):
    p = Path(f'tmp/{RUN}/{t}/drafts/meta.json'); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding='utf-8'); print('meta', t)
docs = [{"url": "https://open-snapshot.muedsa.com/ai-guide.md", "knowledge": "POST /snapshot、图片响应、错误处理", "used_in": "渲染"},
        {"url": "https://snapshot.muedsa.com/reference/parser-tags.md", "knowledge": "Container/Stack/Transform/ClipPath/border/圆角", "used_in": "全部 DSL"},
        {"url": "https://snapshot.muedsa.com/reference/parser-text.md", "knowledge": "fontSize/fontStyle/Raw/CDATA 与文本行高", "used_in": "文字排版"}]
write('A13', {
    'task_id': 'A13', 'title': '品牌标志到完整活动应用', 'status': 'completed', 'stop_reason': '需求满足并完成视觉自检',
    'design': '先做两个 512×512 透明预览：A 三交叠圆环+中心点，B 三错位实心方片+负空间。实际查看后选 A；4 个主要构件（3 环+1 点），环宽 44、点 r34，32px 下仍保留三环轮廓。最终用同一几何生成彩色/纯黑图标、1200×400 横幅与 1080×1350 纵向海报；海报为独立构图，不是横幅缩放。',
    'requirements': [
        {'text': '两个真正不同的预览并选择', 'evidence': 'tmp previews A/B 均渲染查看；rationale 记录选择'},
        {'text': '彩色与纯黑 512 透明、几何相同、黑版 RGB=0', 'evidence': '两图同几何；黑版 alpha>0 像素 R=G=B=0，违规 0'},
        {'text': '图标≤6 主要构件、32×32 可识别', 'evidence': '4 构件；32px 预乘 Lanczos 预览与 4× 放大查看'},
        {'text': '横幅与海报指定文案、海报独立构图', 'evidence': '叠光/Layerlight/口号/日期/OPEN BETA/网址齐全'},
        {'text': '不能把图标 PNG 嵌进应用', 'evidence': '横幅与海报均由同一 icon 几何在 DSL 中重绘'},
        {'text': 'brand-system.json 与 rationale≤300 字', 'evidence': '两文件完整'}
    ],
    'files': [
        {'file': 'symbol-color.snapshot', 'purpose': '彩色图标 DSL', 'dsl': 'symbol-color.png', 'status': '完成'},
        {'file': 'symbol-color.png', 'purpose': '512 透明彩色', 'dsl': 'symbol-color.snapshot', 'status': '完成'},
        {'file': 'symbol-black.snapshot', 'purpose': '纯黑图标 DSL', 'dsl': 'symbol-black.png', 'status': '完成'},
        {'file': 'symbol-black.png', 'purpose': '512 透明纯黑', 'dsl': 'symbol-black.snapshot', 'status': '完成'},
        {'file': 'brand-banner.snapshot', 'purpose': '横幅 DSL', 'dsl': 'brand-banner.png', 'status': '完成'},
        {'file': 'brand-banner.png', 'purpose': '1200×400 横幅', 'dsl': 'brand-banner.snapshot', 'status': '完成'},
        {'file': 'launch-poster.snapshot', 'purpose': '海报 DSL', 'dsl': 'launch-poster.png', 'status': '完成'},
        {'file': 'launch-poster.png', 'purpose': '1080×1350 海报', 'dsl': 'launch-poster.snapshot', 'status': '完成'},
        {'file': 'brand-system.json', 'purpose': '品牌系统', 'dsl': '-', 'status': '完成'},
        {'file': 'rationale.md', 'purpose': '方向说明', 'dsl': '-', 'status': '完成'}
    ],
    'reviews': [
        {'image': f'tmp/{RUN}/A13/previews/preview-a.png', 'at': '2026-10-29T11:52:53+0800', 'result': '三环辨识度高'},
        {'image': f'tmp/{RUN}/A13/previews/preview-b.png', 'at': '2026-10-29T11:52:53+0800', 'result': '三实心方片在小尺寸易糊'},
        {'image': f'outputs/{RUN}/A13/brand-banner.png', 'at': '2026-10-29T11:53:19+0800', 'result': '图标被裁成四分之一'},
        {'image': f'outputs/{RUN}/A13/brand-banner.png', 'at': '2026-10-29T11:54:47+0800', 'result': '图标完整、文案齐全；通过'},
        {'image': f'outputs/{RUN}/A13/launch-poster.png', 'at': '2026-10-29T11:54:47+0800', 'result': '纵向构图完整；通过'},
        {'image': f'tmp/{RUN}/A13/previews/preview-sheet-32.png', 'at': '2026-10-29T11:54:52+0800', 'result': '32px 实际尺寸与 4× 放大均检查；轮廓保留'}
    ],
    'iterations': [
        {'id': 'A13-v1', 'type': 'baseline', 'parent': None, 'dsl': f'tmp/{RUN}/A13/drafts/gen_a13.py', 'image': f'outputs/{RUN}/A13/brand-banner.png', 'at': '2026-10-29T11:53:19+0800', 'problem': '图标被 Positioning 约束裁切', 'change': '按目标尺寸直接生成几何，不用 Transform 缩放', 'result': '通过'}
    ],
    'issues': [
        {'type': 'visual', 'problem': '横幅/海报图标只显示四分之一', 'cause': 'Transform 子节点受 268 紧约束后再缩放', 'fix': 'icon 生成时按 size/512 缩放', 'verify': '图标完整', 'evidence': f'outputs/{RUN}/A13/brand-banner.png'}
    ],
    'notes': '品牌几何用参数化 size 生成，避免对 512 图标做 Transform 缩放；32px 预览用预乘 Lanczos，黑版纯黑逐像素检查。',
    'docs': docs
})
cards = json.loads(Path('tasks/A14-content-stress-batch/inputs/cards.json').read_text(encoding='utf-8'))
write('A14', {
    'task_id': 'A14', 'title': '八组文案压力测试与批量生成', 'status': 'completed', 'stop_reason': '需求满足并完成视觉自检',
    'design': '同一参数化规则生成 8 张 1200×630 深色讲座卡：标题按字符宽度从 64 自适应到 36、最多 3 行；讲者 24；时间 72；状态用颜色+符号+文字三重编码（开放●绿/满额■琥珀/候补◐蓝/取消×红）。取消场仍显示完整标题与时间，并另加“本场取消”。所有位置固定，不通过整体缩小适配长标题。',
    'requirements': [
        {'text': '8 张 1200×630、统一主色/标题区/日期/品牌/状态', 'evidence': '8 张 PNG 尺寸一致；同一版式'},
        {'text': '原始标题/讲者/时间/状态逐字保留', 'evidence': 'batch-audit.json 与输入一致'},
        {'text': '标题≥36、最多3行、讲者≥22、无碰撞', 'evidence': '字号 36–64、行数≤2；状态徽标在标题上方'},
        {'text': '状态颜色+文字/符号、取消仍完整', 'evidence': '四种状态符号与颜色；K06 标题/时间完整并注“本场取消”'},
        {'text': '批量规则、不逐条硬改', 'evidence': '一个生成器；title_fit 按长度选字号'},
        {'text': 'batch-audit.json 逐卡记录并查看', 'evidence': '8 卡均实际查看并写入 audit'}
    ],
    'files': [{'file': f'card-{c["id"]}.snapshot', 'purpose': '卡 DSL', 'dsl': f'card-{c["id"]}.png', 'status': '完成'} for c in cards]
             + [{'file': f'card-{c["id"]}.png', 'purpose': '1200×630 最终图', 'dsl': f'card-{c["id"]}.snapshot', 'status': '完成'} for c in cards]
             + [{'file': 'batch-audit.json', 'purpose': '逐卡审计', 'dsl': '-', 'status': '完成'}],
    'reviews': [{'image': f'outputs/{RUN}/A14/card-{c["id"]}.png', 'at': '2026-10-29T11:56:43+0800', 'result': '标题/讲者/时间/状态完整可读'} for c in cards],
    'iterations': [
        {'id': 'A14-v1', 'type': 'baseline', 'parent': None, 'dsl': f'tmp/{RUN}/A14/drafts/gen_a14.py', 'image': f'outputs/{RUN}/A14/card-K06.png', 'at': '2026-10-29T11:56:49+0800', 'problem': 'K06 取消条过宽', 'change': '宽度 500→180', 'result': '通过'}
    ],
    'issues': [
        {'type': 'visual', 'problem': '取消说明条宽度过大', 'cause': '固定 500 宽', 'fix': '按文字宽度 180', 'verify': 'K06 紧凑', 'evidence': f'outputs/{RUN}/A14/card-K06.png'}
    ],
    'notes': '批量卡先按字符宽度选字号，再固定标题区与讲者/时间位置；状态必须三重编码，取消不应删内容。',
    'docs': docs
})
