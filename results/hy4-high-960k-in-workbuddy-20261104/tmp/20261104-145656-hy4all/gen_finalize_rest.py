#!/usr/bin/env python3
"""Write finalize.json for A16/A17/A18 from real observations."""
import datetime, json, os
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RID


def started(task):
    d = TMP / task
    files = [f for f in d.rglob("*") if f.is_file()]
    mt = min(f.stat().st_mtime for f in files)
    return datetime.datetime.fromtimestamp(mt).astimezone().isoformat(timespec="seconds")


def write(task, spec):
    spec["started_at"] = started(task)
    (TMP / task / "finalize.json").write_text(
        json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote", task, "started_at", spec["started_at"])


DOC_NOTE = (
    "实际阅读并在本题中应用：服务 ai-guide.md（POST /snapshot、text/plain、image/png、"
    "错误处理、字体查询）、openapi.yaml、guides/parser.md（根 Snapshot、CDATA、Stack/Positioned）、"
    "reference/parser-tags.md（Container/Text/Expanded/ClipPath/ImageFiltered 等属性与枚举）、"
    "reference/parser-text.md、guides/examples.md、guides/fonts.md、guides/media-text.md，"
    "缓存于 tmp/<run_id>/_suite/docs/。字体统一 Inter（拉丁/数字）+ Noto Sans CJK SC（中文回退）。")

# ================================================================= A16
write("A16", {
    "task": "A16", "title": "从错误图表恢复可信叙事",
    "status": "完成", "end_reason": "需求满足并完成逐图视觉自检",
    "outputs": [
        {"file": "corrected-report.png", "dsl": "corrected-report.snapshot",
         "purpose": "1280×900 修正后的可信季度复盘报告",
         "verdict": "完成；服务真实 PNG 191201 字节；v2 复查通过"}
    ],
    "extra_outputs": [
        {"file": "findings.json", "purpose": "7 项可观察错误（图片位置/现象/源数据核对/影响/修正/最终查看结果）+ 3 项不确定事项"},
        {"file": "corrected-data.json", "purpose": "四季计算值、共同零起点轴定义、8 根柱位置/高度、结论引用字段与数值"},
    ],
    "requirements": (
        "先用 ViewImage 实际打开 flawed-report.png 逐项诊断，只依据图片与 source.csv，不臆造常见坑。"
        "重制 1280×900 可信报告：四季收入/成本分组柱图（共同零起点 0–200 万元、柱高=数值×1.25px）、"
        "利润明细（30/27/32/54 万元）、一条有数据依据的标题「季度复盘 · Q4 收入与利润均创新高」、"
        "图例（蓝=收入/橙=成本）、单位「万元」、全部 Q1–Q4；保持「季度复盘」主题；"
        "重点季度 Q4 由数据论证。附 findings.json 与 corrected-data.json，"
        "并在报告底部以「原图勘误」逐条说明原图错在哪里。正文≥22、标注≥18、无外部图像。"),
    "self_check": (
        "用 ViewImage 打开 flawed-report.png 整体一次，并用 ffmpeg 转 raw 逐像素核对网格线"
        "（y=295/349/403/457/511/565，2.7px/万元，最下为 100 线）与柱高"
        "（蓝 150/172/198/246px、橙 110/135/128/165px），据此确认 7 项可观察错误。"
        "v1 修正报告打开一次，发现「重点季度」卡内两段长文字重叠、被裁切；v2 把该卡加宽至 576px、"
        "缩窄利润卡、文案拆成三行独立文本框后重新渲染并再次打开：三行各占一行、完整无裁切。"
        "最终图复查：图例颜色与系列对应正确、8 根柱顶标签 120/90/135/108/128/96/180/126 与 source.csv 一致、"
        "Q3 收入柱低于 Q2、Q4 最高、利润明细 30/27/32/54、底部勘误三行完整、字号满足正文≥22/标注≥18。"
        "PNG 文件头 89 50 4E 47 校验通过。"),
    "dsl_capabilities": (
        "Snapshot 根节点 + 固定尺寸 Container；Stack + Positioned 绝对定位；"
        "Container 的 color/borderRadius/border/alignment 实现卡片、图例色块、状态条与柱体"
        "（顶部圆角用 borderRadiusTopLeft/TopRight 原生片段）；Text 的 fontFamily/fontSize/"
        "fontStyle/color/textAlign/letterSpacing 与 CDATA 文本；rect/hline 绘制网格线、零线与分隔线。"
        "全部主体与图表由 DSL 构造，flawed-report.png 仅用于观察，未嵌入。"),
    "fonts_note": "中文用 Noto Sans CJK SC、数字与单位用 Inter（服务 /fonts 列表，缓存 docs/fonts.txt）。",
    "iterations": [
        {"id": "v1", "parent": None, "type": "baseline",
         "image": "outputs/<run_id>/A16/corrected-report.png (v1)",
         "observed": "首版主图/利润明细/勘误均正确，但「重点季度」卡（412px 宽）内两段长正文换行后互相重叠并被卡片底部裁切。",
         "cause": "卡片过窄、两段文本框高度不足且 22 号正文自动换行",
         "change": "生成首版基线并实际打开全图查看",
         "result": "确认 1 项版式缺陷，进入视觉迭代", "complete": True},
        {"id": "v2", "parent": "v1", "type": "visual",
         "image": "outputs/<run_id>/A16/corrected-report.png (v2)",
         "observed": "重点季度卡文字重叠溢出；利润明细卡与重点卡比例失衡",
         "cause": "实际渲染图观察：576px 宽度不足以容纳原两段 38/30 字文案",
         "change": "利润明细卡收窄为 592px（列距 130）、重点卡加宽为 576px；重点卡文案拆成三行独立 22 号文本框（Q4 双高 / 较 Q3 增利 22 万 / Q3 回落 7 万），各占一行",
         "result": "重新渲染并再次打开实际 PNG 复查：三行各占一行、无重叠无裁切；利润明细四列与 Q4 高亮完整；主图柱高、图例、勘误条全部正确，数据核对一致",
         "complete": True},
    ],
    "pitfalls": (
        "踩坑：Y 轴从 100 起截断是原图最易被忽略的误导，必须用像素测量确认柱底在 100 线；"
        "图例颜色与系列对调不能只改文字，要核对柱顶数值到底属于收入还是成本；"
        "长中文正文在窄卡片里自动换行且可溢出容器边界，应拆成独立短行文本框而非依赖自动换行；"
        "正文≥22 的硬约束下不能靠缩小字号塞进文字。未遇到解析错误；服务渲染 2 次均成功。"),
    "design": (
        "以 source.csv 为唯一数据源，利润=收入−成本。主图 0–200 万元共同零起点、零线 y=500、"
        "1.25px/万元，四组左收入右成本，柱顶标注真实数值；底部左右分置利润明细与重点季度卡，"
        "再加一条原图勘误把「错在哪里」直接留在报告里，使叙事与勘误自洽。"
        "标题由 Q4 收入 180、利润 54 双最高论证，重点卡给出较 Q3 增利 22 万与 Q3 回落 7 万的数据依据。"),
    "closing": (
        "最终实际图片已打开检查：四季分组柱图共用零起点且柱高对应数值、图例与单位正确、"
        "利润明细 30/27/32/54 万元、有数据依据的标题、Q4 重点论证与底部 6 条勘误均完整可读；"
        "findings.json 7 项问题与 3 项不确定项、corrected-data.json 的轴定义与计算值均已核对，"
        "据此标为完成。"),
    "visual_review_evidence": [
        "flawed-report.png opened via ViewImage (full 1280x900) with pixel measurement",
        "v1 corrected-report.png opened via ViewImage; focus-card text overlap recorded",
        "v2 corrected-report.png opened via ViewImage; all defects resolved, final accepted",
    ],
    "unresolved": "3 项不确定事项已独立记录在 findings.json 的 uncertainties（审美偏好、页脚稿件标注、数字标签与系列对调合并），未混作数值错。",
    "unresolved_issues": [],
    "metrics_extra": {"image_views": 3,
                      "counts_note": "实际 ViewImage 打开 3 次：错误原图 1 + v1 报告 1 + v2 最终报告 1"},
})

# ================================================================= A17
pngs = [{"file": "handbook-%02d.png" % i, "dsl": "handbook-%02d.snapshot" % i,
         "purpose": "1200×1600 教学第 %d 页" % i, "verdict": "完成；服务真实 PNG，v2 复查通过"} for i in range(1, 5)]
pngs += [{"file": "example-%02d.png" % i, "dsl": "example-%02d.snapshot" % i,
          "purpose": "400×240 第 %d 页可运行示例" % i, "verdict": "完成；服务真实 PNG，实际打开检查通过"} for i in range(1, 5)]
write("A17", {
    "task": "A17", "title": "四页可实践的 DSL 入门手册",
    "status": "完成", "end_reason": "需求满足并逐图视觉自检",
    "outputs": pngs,
    "extra_outputs": [
        {"file": "sources.md", "purpose": "每条关键技术结论指向实际阅读页面与对应示例"},
        {"file": "examples.json", "purpose": "4 个完整示例的 DSL/PNG 路径、核心子树与教学页定位、允许包装差异、印刷源码 1-based 行号与逐字原文、技术结论与实际响应/查看证据"},
    ],
    "requirements": (
        "四张 1200×1600 教学页（第1页调用契约/输入/输出/错误响应，第2页根尺寸与有界 Row/Column/Expanded 及 Stack 定位对照，"
        "第3页 Raw/CDATA/富文本与尾部 alpha 误解，第4页背景/子树滤镜、视觉自检与可复现交付），"
        "每页 8–18 行逐字 DSL 示例与由同一 DSL 构件直接绘制的教学插图（不嵌入预渲染整图）；"
        "另交付 4 个 400×240 独立真实渲染示例，示例必须能真实解析、代码印刷与独立运行是同一套；"
        "核心子树在教学页与独立示例中文字/属性/子节点顺序/效果范围/相对几何一致、1:1 比例；"
        "正文≥24、代码≥20、安全边距 48、明确页码/章节；附 sources.md 与 examples.json；手册与 4 示例都要实际查看。"),
    "self_check": (
        "用 ViewImage 逐张打开 4 个独立示例（POST 卡 / 蓝橙 2:1 与 Stack 圆点 / a<b && c>d CDATA 与半透明对照 / ImageFiltered 模糊块与锐利字），"
        "全部完整清晰、示例 DSL 真实解析成功。手册页 v1 打开第 1、2 页，发现两处缺陷："
        "教学插图与底部两条说明文字重叠、说明被遮挡；第 2 页导语第二行「对定位」被裁切。"
        "v2 把插图改为右置、说明左置并排，导语框加高到 78px、代码块压缩到 420px、页脚上移，"
        "重新渲染 4 页后逐页打开复查：4 页导语、4 条要点、代码块（12/11/11/12 行）、"
        "省略提示、1:1 教学插图、左侧说明与页脚均完整、无重叠无裁切，安全边距 48 满足。"
        "核对 examples.json：印刷片段对应完整示例 DSL 的 1-based 行范围与逐字原文，"
        "核心子树在两处 XML 逐字一致，独立渲染与教学插图效果一致。8 张 PNG 文件头均为 89 50 4E 47。"),
    "dsl_capabilities": (
        "教学页：Snapshot 根 + 1200×1600 固定 Container + Stack/Positioned 绝对排版，"
        "Container 圆角/边框/描边、Text 的 fontFamily(Noto Sans Mono CJK SC 代码 / Noto Sans CJK SC 正文)/"
        "fontSize/fontStyle/color/textAlign/letterSpacing 与 CDATA 印刷 XML 源码，"
        "c.add 把同一核心子树原样放入 400×240 Positioned。"
        "示例：Snapshot + 400×240 Container + Stack/Positioned、Row+Expanded、嵌套 Text Span、"
        "8 位颜色 #245CE480、ImageFiltered sigmaX/sigmaY。全部由 DSL 构造，无 Image 嵌入。"),
    "fonts_note": "正文 Noto Sans CJK SC（≥24）、代码 Noto Sans Mono CJK SC（≥20）、页码与拉丁 Inter；服务 /fonts 列表缓存 docs/fonts.txt。",
    "iterations": [
        {"id": "v1", "parent": None, "type": "baseline",
         "image": "outputs/<run_id>/A17/handbook-01.png / handbook-02.png (v1)",
         "observed": "4 个独立示例全部正确；手册页第 1、2 页的教学插图（y=1310..1550）与底部说明文字（y=1400 起）重叠，说明被深色插图遮挡；第 2 页导语第二行「对定位」被裁切。",
         "cause": "插图居中且与说明共用同一垂直区间；导语文本框 60px 不足以容纳 2 行 26 号中文",
         "change": "生成首版基线，逐张打开 4 示例 + 第 1/2 页手册查看",
         "result": "确认 2 项版式缺陷，进入视觉迭代", "complete": True},
        {"id": "v2", "parent": "v1", "type": "visual",
         "image": "outputs/<run_id>/A17/handbook-01..04.png (v2)",
         "observed": "上述 2 项缺陷；4 页共用同一版式，第 3/4 页同样受影响",
         "cause": "实际渲染图观察与几何核对（插图 400×240 与两条说明的 y 区间相交）",
         "change": "插图右置 x=740、说明左置并排；导语框加高 60→78px；代码块 468→420px 并内缩边距；省略提示/插图标题/页脚整体上移重排；缩短第 1 页首条要点避免孤字成行",
         "result": "重新渲染 4 页手册并逐页打开复查：插图与说明完全不重叠、导语完整、代码块 12/11/11/12 行逐行可读、页脚与安全边距合格；4 个独立示例未改动且已通过，两版示例内容一致",
         "complete": True},
    ],
    "pitfalls": (
        "踩坑：Text 会把 XML 源码里的 < > 原样显示需靠 CDATA 包裹印刷文本（dsl.cdata 已处理）；"
        "长中文正文在固定高度文本框里自动换行会溢出边界，不能依赖 softWrap 自动排版；"
        "教学插图与说明必须错开垂直区间；含 <![CDATA[…]]> 的印刷行放进 CDATA 时需处理内层 ]]>（dsl.cdata 已转义）。"
        "服务层面：v2 第 3 页首次请求遇到一次读取超时（status=0），自动重试成功，失败响应保留在临时目录。"),
    "design": (
        "四页统一版式：页眉/页码/章节 → 大标题 → 导语 → 4 条编号要点 → 深色代码块（逐字印出 DSL 关键 8–18 行）→ "
        "独立省略提示 → 1:1 教学插图（右）与读图要点（左）→ 页脚。"
        "每个示例的完整 DSL 与手册页共享同一个 <Stack>…</Stack> 核心子树（逐字相同、400×240 逻辑区域），"
        "只在两种包装（独立 Snapshot+Container / 手册页 Positioned 平移）上不同，"
        "examples.json 记录 1-based 行号范围与逐字原文，可核对三者一致。"),
    "closing": (
        "8 张最终图片均已逐张打开检查：4 页手册正文/代码/插图/页脚完整无遮挡，4 个独立示例真实渲染且与教学插图一致；"
        "正文≥24、代码≥20、安全边距 48 满足；sources.md 把每条技术结论指向实际阅读页面，"
        "examples.json 记录示例一致性、印刷源码与实际响应/查看证据，据此标为完成。"),
    "visual_review_evidence": [
        "example-01..04.png opened via ViewImage (4 standalone 400x240 renders, all accepted)",
        "handbook-01.png / handbook-02.png v1 opened via ViewImage; 2 layout defects recorded",
        "handbook-01..04.png v2 opened via ViewImage (4 pages); all defects resolved",
    ],
    "unresolved": "无。",
    "unresolved_issues": [],
    "metrics_extra": {"image_views": 10, "independent_cases": 4,
                      "counts_note": "实际 ViewImage 打开 10 次：4 独立示例 + v1 手册 2 页 + v2 手册 4 页"},
})

# ================================================================= A18
write("A18", {
    "task": "A18", "title": "守恒对象的三幕视觉叙事",
    "status": "完成", "end_reason": "需求满足并完成全图与 400px 缩略视觉自检",
    "outputs": [
        {"file": "three-act-story.png", "dsl": "three-act-story.snapshot",
         "purpose": "1600×1000 三幕「集中 → 过载 → 重新分配」视觉叙事",
         "verdict": "完成；服务真实 PNG 103109 字节；全图与 400px 缩略均实际打开通过"}
    ],
    "extra_outputs": [
        {"file": "story-audit.json", "purpose": "U01–U15 稳定颜色/36px、N01–N03 稳定身份与基准几何、逐幕坐标/接收节点/节点几何与负载、叙事证据、守恒检查、预览对比与整图/缩略查看结论"},
        {"file": "rationale.md", "purpose": "≤300 字，根据看图说明三幕叙事如何被感知（实测 298 字）"},
    ],
    "requirements": (
        "1600×1000 三幕表达「集中 → 过载 → 重新分配」。每幕完全相同的 15 个信息单元"
        "（5 蓝/5 橙/5 灰，直径 36）与同一组 3 个处理节点（大小一致、形状身份可辨）；"
        "第一幕单一中心吸引、第二幕同一系统过载、第三幕重新分配到 3 节点（每节点 5 单元且至少两色）。"
        "不得增删/缩小单元、不得用警告文字或让内容不可读；仅靠距离、连线、构图、方向与有限形变表达；"
        "单元不重叠、线不遮圆；关系不能只靠颜色推断；图中文字仅限总标题与三个幕名。"
        "先提出两种叙事构图各制作 1600×1000 实际预览（存临时），选一完善；"
        "附 story-audit.json 与 rationale.md≤300 字；观看全图与 400px 宽缩略。"),
    "self_check": (
        "先生成 preview-A / preview-B 两张 1600×1000 实际预览并用 ViewImage 打开对比："
        "A 的「宽松弧 → 40px 紧密队列」对比强烈、三幕无越界；B 的幕 1/幕 2 同为环形围绕、过载差异弱，"
        "且幕 3 部分单元越出面板右/上边界，故选 A。基于 A 完善：加深第二幕连线（#9AAEC6、3px）、"
        "N01 有限形变 1.25→1.30、第三幕连线略加深，守恒参数与节点身份不变。"
        "最终图打开一次：三幕各 15 圆与 3 节点完整在框内，幕 1 连线全指向唯一 N01，"
        "幕 2 紧密队列且 N01 拉伸，幕 3 三束分流每节点 5 圆至少两色，连线在圆下层未遮圆，"
        "除总标题与三个幕名外无其它文字。另生成 400px 宽缩略并打开：三面板与幕名仍可辨、"
        "集中/过载/分流对比仍可感知、圆仍可辨为独立点，三幕仍可读。"
        "story-audit.json 守恒检查逐项通过（每幕 U01–U15、颜色/直径守恒、最小中心距 61.96/40/48px ≥36、"
        "幕 3 每节点 5 单元且≥2 色）；rationale.md 去空白 298 字 ≤300；PNG 文件头校验通过。"),
    "dsl_capabilities": (
        "Snapshot 根 + 1600×1000 固定 Container + Stack/Positioned 绝对定位；"
        "Container 的圆角矩形实现 N01 及三幕面板，ClipPath SVG 多边形（c.poly）实现 N02 菱形与 N03 六边形"
        "（外深内浅两层形成描边）；circle 绘制 36px 单元；line（ClipPath 四边形）绘制单元→节点的连线，"
        "起点取圆边缘、终点取节点外接半径，且连线先于圆绘制，保证线不遮圆；"
        "Text 仅用于总标题与三个幕名。有限形变只改 N01 的纵向尺寸参数。无外部图像。"),
    "fonts_note": "总标题与幕名用 Noto Sans CJK SC（服务 /fonts 列表，缓存 docs/fonts.txt）。",
    "iterations": [
        {"id": "v1", "parent": None, "type": "baseline",
         "image": "tmp/<run_id>/A18/v1/preview-A.png / preview-B.png (v1 两构图预览)",
         "observed": "构图 A 三幕横向并列、节点下方一字排开，幕1 两层宽松弧汇聚单节点、幕2 40px 紧密队列、幕3 三簇分流；构图 B 节点居中、单元环绕，幕1/幕2 同为环形围绕导致过载对比弱，且幕3 部分圆越出面板边界。",
         "cause": "两种构图各制作 1600×1000 实际服务预览并打开对比；A 的间距对比与分流方向更清晰",
         "change": "生成两版预览并实际查看，选定构图 A，记录未选 B 的原因",
         "result": "选出 A 作为最终构图；同时发现 A 的第二幕连线在缩略尺寸下偏淡、单节点形变可再强化，进入完善",
         "complete": True},
        {"id": "v2", "parent": "v1", "type": "visual",
         "image": "outputs/<run_id>/A18/three-act-story.png (v2 最终) + tmp/<run_id>/A18/v2/thumb-400.png",
         "observed": "预览 A 的第二幕连线偏淡、N01 形变 1.25 略弱；其余守恒与叙事成立",
         "cause": "预览全图与缩略观察，缩略下细连线易被弱化",
         "change": "第二幕连线改为 #9AAEC6 / 3px、第三幕 #B7C6DA、第一幕 #CBD7E6；N01 纵向拉伸 1.25→1.30；单元坐标、颜色、直径与节点身份全部不变",
         "result": "重新渲染最终图并打开全图与 400px 缩略：三幕 15 圆/3 节点守恒、幕1 单中心汇聚、幕2 紧密队列与形变、幕3 三束分流均清楚，连线不遮圆、无多余文字、三幕无越界；缩略仍可读三幕",
         "complete": True},
    ],
    "pitfalls": (
        "踩坑：ClipPath 全画布多边形与 Positioned 混用时坐标必须是绝对画布坐标；"
        "连线必须先于圆绘制并从圆边缘起笔，否则会盖住单元；"
        "构图 B 的环形排布在第三幕容易把圆送出面板，需在生成时校验边界；"
        "「过载」不能靠增删/缩小圆或警示文字，只能用间距压缩、连线密度与有限形变；"
        "rationale.md 需压到 ≤300 字（首版 356 字已精简为 298 字）。"
        "服务渲染 3 次（2 预览 + 1 最终）均成功。"),
    "design": (
        "三幕横向并列，每幕 3 个节点固定为下排一字（N02 左菱形 / N01 中圆角方 / N03 右六边形）。"
        "幕1 用两层同心弧（R=180/320）让 15 圆宽松环绕，15 条连线全指向唯一 N01，另两节点空置；"
        "幕2 保持同一 N01，但把中心距压到 40px 成 5×3 密集队列、连线加粗变深、N01 纵向拉伸 1.30；"
        "幕3 把单元分三组（间距 160px）分别连向 N02/N01/N03，每节点 5 圆且至少两色。"
        "颜色只是辅助，关系由连线方向、空间分组与间距变化承担；ID 仅存在 story-audit.json，不写入图中。"),
    "closing": (
        "最终实际图片已打开全图与 400px 宽缩略检查：三幕各 15 单元与 3 节点守恒、幕 1 集中、幕 2 过载、"
        "幕 3 重新分配均可读，单元不重叠、线不遮圆、无多余文字、无越界；"
        "story-audit.json 的守恒/不重叠/第三幕 5 单元两色/有限形变参数与逐幕叙事证据齐全，"
        "rationale.md 298 字 ≤300，两张预览及选择依据保留在临时目录，据此标为完成。"),
    "visual_review_evidence": [
        "preview-A.png opened via ViewImage (1600x1000 layout A)",
        "preview-B.png opened via ViewImage (1600x1000 layout B, not selected)",
        "three-act-story.png opened via ViewImage (final full image)",
        "thumb-400.png opened via ViewImage (400px wide thumbnail)",
    ],
    "unresolved": "无。",
    "unresolved_issues": [],
    "metrics_extra": {"image_views": 4,
                      "counts_note": "实际 ViewImage 打开 4 次：预览 A、预览 B、最终全图、400px 缩略"},
})
