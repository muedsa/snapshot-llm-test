import json

iters = [
    {
        "version_id": "A13-iter-001", "parent": None, "type": "alternative",
        "dsl": ["tmp/run-20261011-01/A13/drafts/preview-a.snapshot",
                "tmp/run-20261011-01/A13/drafts/preview-b.snapshot"],
        "images": ["tmp/run-20261011-01/A13/drafts/preview-a.png",
                   "tmp/run-20261011-01/A13/drafts/preview-b.png"],
        "viewed_at": "2026-10-14T10:39:00+08:00",
        "problem_observed": "方案探索，无缺陷：方向A（三圆角横条对角错排）32px下最清晰但形态接近通用列表/堆叠图标；方向B（圆环+偏心透镜盘+光点）更独特、'光'意象强，环孔月牙负空间在32px仍保留，但v1预览的圆盘85%透明度压在环上使32px轮廓混色发糊、圆盘176偏大、光点48偏小",
        "change": "选择方向B并按32px检查结果完善：圆盘176→160并外移至(240,240)使45°处保留29.49单位残环、圆盘改为不透明、光点48→56、最小负空间间隙保持36.36单位",
        "recheck": "定稿四图渲染后逐张整图查看通过；32px实际尺寸查看环/盘/点/月牙均可辨认（iter-003确认）",
    },
    {
        "version_id": "A13-iter-002", "parent": "A13-iter-001", "type": "visual",
        "dsl": ["tmp/run-20261011-01/A13/drafts/symbol-color.snapshot",
                "tmp/run-20261011-01/A13/drafts/symbol-black.snapshot",
                "tmp/run-20261011-01/A13/drafts/brand-banner.snapshot",
                "tmp/run-20261011-01/A13/drafts/launch-poster.snapshot"],
        "images": ["tmp/run-20261011-01/A13/drafts/symbol-color-v1.png",
                   "tmp/run-20261011-01/A13/drafts/symbol-black-v1.png",
                   "tmp/run-20261011-01/A13/drafts/brand-banner-v1.png",
                   "tmp/run-20261011-01/A13/drafts/launch-poster-v1.png"],
        "viewed_at": "2026-10-14T10:42:30+08:00",
        "problem_observed": "定稿四图无新缺陷：彩版/黑版几何一致；横幅含叠光 Layerlight+口号+网址；海报为独立纵向构图并含2026.11.07 · ONLINE、OPEN BETA徽章、layerlight.example.org",
        "change": "无需再改，直接定稿（首版达标不制造迭代）",
        "recheck": "四张服务原始字节复制到输出目录，md5校验一致；交付前再次逐张打开输出目录最终图复查通过",
    },
    {
        "version_id": "A13-iter-003", "parent": "A13-iter-002", "type": "measurement",
        "dsl": None,
        "images": ["tmp/run-20261011-01/A13/thumbs/symbol-color-32-light.png",
                   "tmp/run-20261011-01/A13/thumbs/symbol-black-32-light.png",
                   "tmp/run-20261011-01/A13/thumbs/symbol-color-32-light-x8.png",
                   "tmp/run-20261011-01/A13/thumbs/symbol-black-32-light-x8.png"],
        "viewed_at": "2026-10-14T10:48:00+08:00",
        "problem_observed": "测量核验：纯黑检查0违规（alpha>0像素92549个全部RGB=0，alpha范围[1,255]为抗锯齿边缘）；两图标alpha通道542个像素差值，追加量化确认全部差值=1且全部位于形状边缘（紧邻两侧均有全不透明像素），alpha覆盖率相对差2.3e-5，判为抗锯齿舍入而非几何差异；alpha包围盒[56,56,455,455]与设计一致，四边留白56单位",
        "change": "无需修改：所有检查通过，32px原尺寸查看轮廓与关键负空间可辨认，×8放大确认边缘干净",
        "recheck": "检查结果写入tmp/run-20261011-01/A13/checks.json与checks-geometry-detail.json，并嵌入brand-system.json",
    },
]

with open("tmp/run-20261011-01/A13/iterations.jsonl", "a", encoding="utf-8") as f:
    for it in iters:
        f.write(json.dumps(it, ensure_ascii=False) + "\n")

adds = [
    {"id": "A13-doc-reuse-0001", "ts": "2026-10-14T10:34:00+08:00",
     "request_type": "doc-reuse", "method": None,
     "url": "https://open-snapshot.muedsa.com/ai-guide.md",
     "cached_at": "tmp/run-20261011-01/_suite/docs/ai-guide.md",
     "elapsed_seconds": 0, "http_status": None,
     "note": "复用套件缓存：请求结构、UA要求、/fonts端点；本题DSL按同一结构构造；不计新HTTP请求",
     "requestId": None, "server_timing": None, "error": None},
    {"id": "A13-doc-reuse-0002", "ts": "2026-10-14T10:35:00+08:00",
     "request_type": "doc-reuse", "method": None,
     "url": "https://snapshot.muedsa.com/ tags reference (parser-tags.html): Snapshot / Container (border, shape, gradient) / Text",
     "cached_at": "tmp/run-20261011-01/_suite/docs/parser-tags.html",
     "elapsed_seconds": 0, "http_status": None,
     "note": "复用并实际抽取：Snapshot background默认transparent（透明图标不设background属性）；Container border格式\"宽度 SOLID 颜色\"、shape=CIRCLE用于圆环；颜色#RRGGBBAA带alpha；TEXT属性表用于横幅海报文字",
     "requestId": None, "server_timing": None, "error": None},
    {"id": "A13-doc-reuse-0003", "ts": "2026-10-14T10:36:00+08:00",
     "request_type": "doc-reuse", "method": None,
     "url": "fonts query result (open-snapshot fonts list)",
     "cached_at": "tmp/run-20261011-01/_suite/docs/fonts.txt",
     "elapsed_seconds": 0, "http_status": None,
     "note": "复用字体清单：Inter+Noto Sans CJK SC（标题/正文）、Noto Sans Mono CJK SC（网址/日期/徽章）；不计新HTTP请求",
     "requestId": None, "server_timing": None, "error": None},
]

with open("tmp/run-20261011-01/A13/requests.jsonl", "a", encoding="utf-8") as f:
    for a in adds:
        f.write(json.dumps(a, ensure_ascii=False) + "\n")

print("iterations +3, doc-reuse +3")
