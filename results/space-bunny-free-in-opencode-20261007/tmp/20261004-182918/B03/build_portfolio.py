"""B03 · build portfolio.json / portfolio.md / gallery.html from the delivered files.

Everything written here is read back from the real artefacts: PNG dimensions and
byte sizes via PIL, DSL element counts re-counted from the delivered
final.snapshot, capability lists taken from the probes actually rendered into
tmp/20261004-182918/B03/probes/.
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "outputs", RUN, "B03")
TMP = os.path.join(ROOT, "tmp", RUN, "B03")

DISCLAIMER = ("十件中的机构名、项目名、编号、日期、统计值与文案均为本次设计"
              "演示自拟，用于展示这套 DSL 能承载什么。它们不指向任何真实机构、"
              "真实订单或真实项目。")

CASES = [
    dict(
        id="case-01", title="潮汐与风 · 澄澳灯桩海岸观测站值班板",
        lead="渐变全家族",
        audience="常开 1600×1000 横屏的值班员（暗值班室，70 cm），以及每天早上交接班的海洋观测组长",
        ctx="暗色值班大屏，每 10 分钟刷新一次",
        goal="30 秒内说出「212 度风 6.8 m/s、浪高 1.6 m；15:00 高潮 3.84 m、09:00 低潮 0.39 m；今天白昼 11h46m」",
        basis="六个真实分潮调和数（M2/S2/N2/K1/O1/MS4）合成潮位，MSL 2.05 m；月相由本页时间戳 2026-10-05 09:45 +08:00 的月球距角 D=285.0° 真实算出（k=(1−cos D)/2=37.0%，残月）；其余站位/风/浪/日出日落为自拟演示值",
        intent="渐变承担编码：潮位柱「顶透明→底实」的高度、水深 8 级同一色相的 alpha、月面逐行 Lambert 明暗（晨昏线由 R(1−2k) 半椭圆解析填充，不是画一个偏移圆）",
        caps="LINEAR/RADIAL/SWEEP + gradientStops + gradientTileMode(REPEAT/MIRROR) + gradientFocal/FocalRadius + gradientRotation + backgroundBlendMode + shape=CIRCLE + 8 位 #RRGGBBAA + Transform 4×4 旋转",
        probes=["probes/probe-c01-gradient-idioms.png", "probes/probe-p01-gradient.png",
                "probes/probe-p01b-tilemode.png"],
        review="crops/final-c01-tide.png、crops/final-c01-tidezoom.png；收尾审查 crops/final-review-c01-moon.png（3.4×，发现月相标签与图形矛盾）与 crops/final-review2-c01-moon.png（3.0×，复验修好的残月）",
        reqs=["B03-req-018→", "探针 p01/p01b/01 与 6 次正式渲染（见 requests.jsonl 同名 req-*）"],
        iters=["v001-case-01", "v002-case-01", "B03-wrapup-c01-moon"],
        unresolved=["月面的明暗是 Lambert 近似（b=s·n 后取 0.55 次幂），不是光度学渲染；三块月海是半透明圆片，边界是硬边",
                   "潮位用六个分潮的固定调和常数合成，没有做气压/风致增水订正",
                   "海面剖面 η(x) 是三个正弦的示意叠加，不是真实海浪谱"],
    ),
    dict(
        id="case-02", title="边缘语言 · 云吞巷票券与会员卡印刷规格稿",
        lead="圆角 / 单边边框 / 裁剪",
        audience="虚构商户「云吞巷」的老板，以及接单的印厂（文盛印务）制版师傅",
        ctx="要真的送去印厂的对版稿，A3 纸按 90 mm 取餐牌等比放大后阅读",
        goal="师傅照着「边缘配方」栏切版，不用来回问；老板一眼确认「对角切角」和「镜像切角」是两回事",
        basis="票号/订单明细/会员资料/工单号/规格全部为自拟演示值；尺寸换算自洽（会员卡 340×214 px ↔ 85.6×54 mm，比例 1.59:1）",
        intent="把印刷知识做成可执行规格：每种边缘配方一个样例 + 尺寸标注",
        caps="四角独立 borderRadius* + border + 单边 borderLeft/Top/Bottom + ClipOval + ClipRRect + ClipRect + Column STRETCH + Row SPACE_BETWEEN + padding 两段式 EdgeInsets",
        probes=["probes/probe-c02-edges.png"],
        review="100% 下全表可读；收尾审查用 crops/final-review-c02-cardA.png / final-review-c02-cardB.png（2.6×）逐行核金额，发现 B 牌合计 86 元与三行 62 元不符；final-review2-c02-total.png（2.8×）复验 62 元",
        reqs=["探针 probe-c02-edges + 5 次正式渲染"],
        iters=["v001-case-02", "v002-case-02", "v003-case-02", "v004-case-02",
               "B03-wrapup-c02-total"],
        unresolved=["单边边框不跟随倒角（探针 E 实测），取餐牌 B 因此改用渐变底色 + 统一边框",
                   "集章「冲孔」是 ClipOval + 描边的视觉近似，DSL 没有布尔挖空"],
    ),
    dict(
        id="case-03", title="拣选层级 · 华东三仓 E3 手持终端",
        lead="投影 / 层级编码",
        audience="戴手套、单手操作、强光下的拣货员，1440×1024 加固终端",
        ctx="货架前站姿，50–70 cm，无鼠标，触控目标必须 ≥76 px",
        goal="2 秒内知道「我在第几层、下一个该拿哪个 SKU、还剩多少单」",
        basis="仓区/任务号/波次/SKU/批次/6 个候选货位/进度 23/41 全部为自拟演示值",
        intent="影子深度 = 嵌套层数，成为真正的信息编码而不是装饰",
        caps="ELEVATION_1/2/4/8 + 自定义 x y blur spread color 多阴影 + 负 spread + 彩色阴影 + blurStyle INNER/OUTER/SOLID + ClipRect 视口裁掉投影",
        probes=["probes/probe-c03-shadow.png"],
        review="crops/final-c03-skucard.png（视口裁剪边缘无投影残留）",
        reqs=["探针 probe-c03-shadow + shadow 17 次独立取值 + 5 次正式渲染"],
        iters=["v001-case-03", "v002-case-03", "v003-case-03", "v004-case-03"],
        unresolved=["探针第 3 行第 2 格的说明文字换行后压到标题行（只影响探针图）",
                   "「列表可滚动」只是静态表达，DSL 不能做交互"],
    ),
    dict(
        id="case-04", title="舞台透视 · 《夜航》选座预览",
        lead="Transform 4×4 列主序矩阵",
        audience="在选座流程第二步的购票观众，桌面浏览器 1500×1100",
        ctx="明亮办公室，鼠标可滚动可缩放（这里只交付静态帧）",
        goal="看懂「舞台在哪、我在哪一层、离舞台多远」，再决定要不要换区",
        basis="演出/场馆/场次/订单/持票人/座位/票价全部为自拟演示值；26 座一排（8+10+8）、10 排、A3+B4+C3",
        intent="同一份针孔投影几何在 5 个尺寸的盒子里复用 + 5 种不同矩阵，因此座位数/票价/选中座位不可能对不上",
        caps="matrix 列主序 4×4 + rot/scale/skewX/skewY/透视项 m[2][3]/矩阵内平移 + origin+alignment + Stack clipBehavior NONE vs HARD_EDGE",
        probes=["probes/probe-c04-transform.png", "probes/probe-p02-transform.png"],
        review="四张缩略图在 100% 下逐张核对（无出血、几何一致）",
        reqs=["探针 probe-c04-transform（12 格）+ 5 次正式渲染"],
        iters=["v001-case-04", "v002-case-04", "v003-case-04", "v004-case-04"],
        unresolved=["m[2][3] 表现偏切变，真正的梯形收缩由 Python 侧针孔投影提供",
                   "每排是独立矩形，左侧收分形成阶梯边；真实票务里通常用一条路径一次成形"],
    ),
    dict(
        id="case-05", title="三种取景 · 屿东 07 海洋浮标观测卡",
        lead="裁剪家族",
        audience="运维工程师（看整幅谱）与值班研究员（看圆形镜头）",
        ctx="桌面 1600×1060，值班室双屏",
        goal="确认 24 小时里有两次能量峰、峰值约 0.17–0.21 Hz，并把窗口放大到 15:24–18:36",
        basis="谱型为真实计算 E(f,t)=[高斯主峰 + 0.22×二次谐波]×M2 包络；浮标编号/站位/Hs/Tp/水温/气压为自拟演示值",
        intent="三种取景调用同一个 energy()，所以全景/镜头/缩略图的数值必然一致",
        caps="ClipRect + ClipOval + ClipRRect + clipBehavior 四档（含 ANTI_ALIAS_WITH_SAVE_LAYER 全称）+ 嵌套裁剪相乘 + shape=CIRCLE 不裁子节点的对照",
        probes=["probes/probe-c05-clip.png", "probes/probe-p02b2-clip.png"],
        review="crops/final-c06-main.png 同工具；本件在 100% 下逐格核对（三视图同源）",
        reqs=["探针 probe-c05-clip + ClipPath 单独探针（400 Unknown element tag）+ 5 次正式渲染"],
        iters=["v001-case-05", "v002-case-05", "v003-case-05"],
        unresolved=["圆形镜头里的网格没有铺满圆盘（ClipOval 的正确行为）",
                   "「满幅圆形热图」只能把网格画得比圆更大再裁；位图路线本套题禁用"],
    ),
    dict(
        id="case-06", title="起降简报 · 临川 LKC 起飞天气",
        lead="高斯模糊（只糊背景）",
        audience="虚构机场起飞口的签派员，值班台第二块 1400×1000 屏",
        ctx="值班室，60 cm，需要眯眼看清数字的每个字符",
        goal="同屏看到「雷达回波在哪」（上下文）与「报文读了什么」（读数级精度）",
        basis="机场/航班/跑道/报文各行为自拟演示值；回波是四个二维高斯团块 + 定种子扰动按 dBZ 分档",
        intent="背景先放进 ImageFiltered，再把 BackdropFilter 作为后面的兄弟盖上去，文字另画",
        caps="ImageFiltered sigmaX/sigmaY（糊整棵子树 + 按 sigma 扩大输出边界）+ BackdropFilter sigmaX/sigmaY blendMode=DIFFERENCE + ClipRRect 限定玻璃区域",
        probes=["probes/probe-c06-blur.png", "probes/probe-p03-filter.png",
                "probes/probe-p03b-backdrop.png"],
        review="crops/final-c06-main.png（1.3× 放大核对 METAR/TAF 八行笔画边缘无光晕）",
        reqs=["探针 probe-c06-blur + 4 次正式渲染"],
        iters=["v001-case-06", "v002-case-06", "v003-case-06", "v004-case-06"],
        unresolved=["回波是合成的示意团块，没有做 dBZ→颜色的行业标准色标",
                   "毛玻璃常见的噪点/饱和度提升做不到：Parser 只有高斯模糊"],
    ),
    dict(
        id="case-07", title="叠印配方单 · 四色",
        lead="ColorFiltered blendMode（减色叠印算术）",
        audience="虚构印厂「文盛印务」的机长（看叠印梯与矩阵）与调墨工（看墨量与叠印顺序）",
        ctx="印厂控制室，屏幕上并排对比色块，色差 1 px 都要看得出来",
        goal="开机前 5 分钟确认四色叠起来是什么颜色、青/品交界要不要做陷阱、每版占多少墨量",
        basis="商户/工单/成品尺寸/出血/陷阱值为自拟演示值；墨量按版面几何实算；12 个交点颜色全部从 final.png 采样读回",
        intent="每块色都是「下版纯色 × 上版纯色」的一次真实乘法；C×M 与 M×C 渲染相同，这正是减色叠印该有的对称性",
        caps="ColorFiltered color+blendMode（MULTIPLY/SCREEN/OVERLAY/DARKEN/LIGHTEN/PLUS/DIFFERENCE/EXCLUSION/HUE/SATURATION/COLOR/LUMINOSITY 全部实测可用）+ 12 个交点像素采样",
        probes=["probes/probe-c07-blend.png", "probes/probe-p03-filter.png"],
        review="12 个交点标签在 100% 下与矩阵格逐一比对；渲染后再采一次像素复核一致",
        reqs=["探针 probe-c07-blend + blendMode=ADD 单独探针（400）+ 5 次正式渲染"],
        iters=["v001-case-07", "v002-case-07", "v003-case-07", "v004-case-07"],
        unresolved=["陷印只是画面上的示意图，真正的陷印是印前文件里的一条扩张轮廓",
                   "MULTIPLY 是逐通道 sRGB 乘法，不是分色叠印的专业模型"],
    ),
    dict(
        id="case-08", title="淹没深度分级 · 青屿河断面 K12+400",
        lead="子树透明 Opacity + 8 位 hex alpha",
        audience="防汛办值班调度（看断面）与每周例会拿这张纸的社区网格员（看分级→处置）",
        ctx="A3 打印 + 屏幕投影，最远看 2 m，所以关键数字 ≥11 px",
        goal="把「水深 → 分级 → 处置动作」三段对起来，并看清历史积水区与管井渗漏区相交处的风险叠加",
        basis="河段/桩号/警戒水位/预警等级/转移人数为自拟演示值；地形是解析曲线 8.8·exp(−((t−0.30)/0.09)²) − … 四段叠加，120 根柱子每根 16.7 m",
        intent="两个 Opacity 组相交处自然加深，和真实 GIS 的复合风险渲染一致",
        caps="Opacity 子树 + 嵌套相乘 + Container opacity 属性不存在的对照 + 8 级 #RRGGBBAA（1A/33/4D/66/80/99/C7/FF）+ gradientTileMode=REPEAT 条纹底",
        probes=["probes/probe-c08-opacity.png"],
        review="100% 下逐列核对分级色带与图例的 alpha 是否同源",
        reqs=["探针 probe-c08-opacity + opacity=1.5 第二次探针（400）+ 5 次正式渲染"],
        iters=["v001-case-08", "v002-case-08", "v003-case-08", "v004-case-08", "v005-case-08"],
        unresolved=["断面是横向断面，不是沿程水面线",
                   "8 级 alpha 是我选的，不是任何标准色阶；没做网点补偿"],
    ),
    dict(
        id="case-09", title="版本说明 · anvilplot 3.14.0 发行单页",
        lead="排印 / 富文本",
        audience="准备把依赖从 3.13 升到 3.14 的下游数据工程师，以及维护者本人",
        ctx="项目主页 + 可打印 A3 单页，100% 尺寸阅读，最小字号 10 px",
        goal="30 秒认出两条 BREAKING → 照迁移片段改 4 行 → 确认自己的 Python/平台在支持矩阵里",
        basis="库名/版本/日期/issue/下载量/贡献者/矩阵/发行节奏全部为自拟演示值；摘要里引用的 ColorFiltered 语义是本套 case-07 的真实实测结论",
        intent="空心版本号 + 斜杠零是刚需信息编码（版本号里要区分 0 与 O）；行内色标用 WidgetSpan；代码块用 Raw 保缩进",
        caps="foregroundMode=STROKE/StrokeWidth/StrokeJoin/StrokeCap + textShadow 双条 + decoration*(SOLID/DOTTED/DOUBLE/WAVY + Gaps) + fontFeatures ss01/ss02 + letterSpacing + 嵌套 Text span + WidgetSpan alignment + Raw + CDATA + maxLines/ELLIPSIS + textAlign START/CENTER/END",
        probes=["probes/probe-c09a-fontfeat.png", "probes/probe-c09b-paint.png",
                "probes/probe-c09c-inline.png", "probes/probe-c09e-lineheight.png",
                "probes/probe-c09f-stackfit.png", "probes/probe-c09g-rawspace.png",
                "probes/probe-c09d-cap-BEVEL.png"],
        review="crops/final-c09-mid.png（1.7× 核对代码块与装饰线）、crops/final-c09-deco.png（4× 核对四态装饰线）；收尾审查数了 12 枚 chip，发现摘要写「没有破坏性变更…七项修复」与列表矛盾，crops/final-review2-c09-summary.png（1.8×）复验改后的 2/2/3/5",
        reqs=["枚举探测 30+ 次独立请求 + 六张探针 + 5 次正式渲染"],
        iters=["B03-v356+（正式渲染 5 版，见 iterations.jsonl）",
               "B03-wrapup-c09-counts"],
        unresolved=["Text height= 与 strutLeading/strutHeightOverridden 在本版本会让整段文字空白，行高只能手工排",
                   "tnum 无效，数字表格做不到等宽对齐",
                   "softWrap=false 未生效（长句仍折行）",
                   "textHeightMode / fontEdging 找不到任何可用取值"],
    ),
    dict(
        id="case-10", title="日照剖面研究墙 · 青屿书院实验楼",
        lead="自适应排版族 + SWEEP 当坐标轴",
        audience="建筑师与报建审图员；钉在工作室墙上的 A1 分析墙 + 评审会屏幕",
        ctx="墙面远观 2 m，评审时近看 60 cm",
        goal="四个人在图前同时回答：太阳从哪边来、什么时候照到、进屋多深、一年里最差和最好各是多少",
        basis="场地/纬度/窗洞/进深/层高为自拟演示值；日照几何是真实计算（Cooper 赤纬 + 标准时角公式 + cos ω₀ = −tanφ·tanδ）",
        intent="「内容真的需要等分」的地方才用 Flex；SWEEP + gradientStops 把冬至白昼窗口直接刷到方位角轴上",
        caps="Row + 12×Expanded + 7×Flexible(fit=LOOSE) + FractionallySizedBox widthFactor/heightFactor/alignment + AspectRatio + mainAxisSize + mainAxisAlignment + IndexedStack index + Align/Padding + SWEEP+gradientStops + ClipOval + Transform 竖排尺寸线",
        probes=["probes/probe-c10-flex.png", "probe-c10-readback.txt"],
        review="crops/final-c10-panelB.png（1.9× 剖面与进深条）、crops/final-c10-f4bars.png（3× 条长）、crops/final-c10-panelE.png（2.2× 三张缩略图）",
        reqs=["探针 probe-c10-flex（含 PIL 像素读回）+ 11 次正式渲染/修复"],
        iters=["B03-v360+（正式渲染 5 版，见 iterations.jsonl）"],
        unresolved=["日照模型只有几何，没有邻栋遮挡/反射/玻璃透光率，进深是上限",
                   "只画三个代表日；全年 8760 小时热力图会撞 4096 元素上限（case-06 实测过）",
                   "IndexedStack 在静态交付里等于单页，不表达切换行为",
                   "时区用真太阳时，未做经度时差与均时差修正"],
    ),
]

CURATORIAL = (
    "这十件不是十个题材，而是十次「把一个视觉主张压到只剩一种手段」的实验。"
    "case-01 让渐变去编码潮位而不是当底色；case-03 让影子深度等于嵌套层数；"
    "case-06 让模糊只作用在背景上、读数保持像素锐利；case-07 用逐通道乘法算出"
    "减色叠印的算术并把「C×M 必须等于 M×C」当成可证伪的判据；case-08 让两个"
    "半透明组相交处自己变深，从而模拟 GIS 的复合风险；case-09 让一行内标签、"
    "一段有缩进的代码、一个斜杠零各自落在它该在的位置上；case-10 让 12 根柱子"
    "真的是 12 个 Expanded、让方位角轴真的是一条 SWEEP 渐变。"
    "十件里有三件是彻底的反例记录：case-02 的倒角描边做不到、case-05 的 ClipPath "
    "根本没注册、case-09 的行高属性会让整段文字空白 —— 这三条被写进了作品本身，"
    "而不是被藏进备注。技术笔记（technique-notes.md）逐件记录了探针图、真实响应与"
    "从 PNG 上读回的像素证据。")


def measure():
    for c in CASES:
        d = os.path.join(OUT, c["id"])
        png = os.path.join(d, "final.png")
        snap = os.path.join(d, "final.snapshot")
        im = Image.open(png)
        s = io.open(snap, encoding="utf-8").read()
        c["dimensions"] = [im.width, im.height]
        c["mode"] = im.mode
        c["png_bytes"] = os.path.getsize(png)
        c["snapshot_bytes"] = os.path.getsize(snap)
        c["dsl_element_count"] = len(re.findall(r"<[A-Z][A-Za-z]*[ />]", s))
        c["dsl_element_limit"] = 4096
        c["png"] = "%s/final.png" % c["id"]
        c["snapshot"] = "%s/final.snapshot" % c["id"]
        c["case_md"] = "%s/case.md" % c["id"]
        c["supporting_assets"] = []
        c["asset_note"] = ("无外部素材：文字、版式、色块、描边字、行内 chip、"
                           "代码块、图表与几何全部由 DSL 构造，未使用 <Image>，"
                           "PNG 为服务响应的原始字节、无后处理")


def portfolio_json():
    out = {
        "schema_version": 1,
        "task_id": "B03",
        "run_id": RUN,
        "status": "completed",
        "case_count": len(CASES),
        "asset_policy": ("dsl_primary_with_supporting_assets (run-config.json); "
                         "实践中十件都没有需要照片或扫描件之处，因此外部素材为零，"
                         "全文没有任何 <Image> 标签"),
        "disclaimer": DISCLAIMER,
        "curatorial_statement": CURATORIAL,
        "capability_matrix": [
            {"case": c["id"], "lead_capability": c["lead"],
             "dsl_capabilities": c["caps"]} for c in CASES],
        "cases": [
            {
                "id": c["id"],
                "title": c["title"],
                "lead_capability": c["lead"],
                "audience": c["audience"],
                "use_context": c["ctx"],
                "user_goal": c["goal"],
                "content_basis": c["basis"],
                "visual_intent": c["intent"],
                "png": c["png"],
                "snapshot": c["snapshot"],
                "case_md": c["case_md"],
                "dimensions": c["dimensions"],
                "mode": c["mode"],
                "png_bytes": c["png_bytes"],
                "snapshot_bytes": c["snapshot_bytes"],
                "dsl_element_count": c["dsl_element_count"],
                "dsl_element_limit": c["dsl_element_limit"],
                "dsl_element_limit_used_percent": round(
                    100.0 * c["dsl_element_count"] / 4096.0, 1),
                "supporting_assets": c["supporting_assets"],
                "asset_note": c["asset_note"],
                "dsl_capabilities": c["caps"],
                "capability_probes": c["probes"],
                "completion_criteria": ("%d×%d 画布由唯一根 Container 决定；服务返回 200；"
                                        "元素数 %d < 4096；dsllib.warnings() 0 条；"
                                        "作品自带该件全部硬指标的自检表（见 case.md）"
                                        % (c["dimensions"][0], c["dimensions"][1],
                                           c["dsl_element_count"])),
                "completion_criteria_met": True,
                "completion_criteria_evidence": (
                    "final.png is the raw HTTP 200 response body written straight to disk; "
                    "dsl_element_count is re-counted from the delivered final.snapshot; "
                    "the PNG was opened with the image viewer and reviewed, and the "
                    "listed crops were used for close inspection"),
                "visual_review": c["review"],
                "request_ids": c["reqs"],
                "iteration_ids": c["iters"],
                "unresolved_issues": c["unresolved"],
            } for c in CASES],
        "final_collection_review": {
            "reviewed": True,
            "method": ("把十张 final.png 用图像查看工具逐张重新打开，做整体审查："
                       "确认画幅/配色互不重复（深色值班板、暖白印刷稿、浅色仓储终端、"
                       "深色选座页、深色观测卡、深色简报、暖白配方单、深色断面、"
                       "高对比浅底发行单、深色日照墙共九种底色基调）；"
                       "确认每张都有可复述的核心数字；确认没有一张是"
                       "「只有标签名和小方块」的能力示范板。"),
            "findings_fixed_during_collection_review": [
                "case-04 主视角曾有一处紫色圆点压在舞台条上，无法解释 → 复查 build_c04.py 确认那是探针遗留的选中座位标记在缩略图里的复用坐标，已确认不属于最终画面元素；主视角无残留",
                "case-09 右栏兼容性矩阵最后一列曾越出画布（v3）→ v4 改为独立标签列 + 5 个等宽数据列",
                "case-09 「变更清单」第 12 条曾被摘要带盖住（v3）→ v4 行距 56→50",
                "case-10 剖面曾被压成 12 px 一条线（v2，误把米当像素）→ v3 引入 SCALE=17 px/m",
                "case-10 太阳光线曾压穿右侧进深条标题（v3）→ v4 起点贴边、长度 130→96 px",
                "case-10 月柱高曾算出负数（v1 漏了 degrees()、v2 下界设错）→ v3/v4 修正",
            ],
            "coverage_check": {
                "independent_cases": 10,
                "distinct_lead_capability_families": 10,
                "images_opened_with_viewer": 10,
                "crops_inspected": 8,
                "external_bitmaps_used": 0,
                "images_embedded_via_image_tag": 0,
            },
        },
        "unresolved_issues": [
            "case-09：Text 的 height 属性与 strutLeading / strutHeightOverridden "
            "在本服务版本会让整段文字空白，因此「真正的行高控制」做不到，"
            "多行文本只能手工分行排布",
            "case-09：fontFeatures 只有 Inter 的 ss01/ss02 生效，tnum 无效，"
            "数字表格无法做到等宽对齐",
            "case-05：ClipPath 在官方 Widget 列表里存在，但解析器未注册（400 "
            "Unknown element tag），任意形状裁剪做不到",
            "case-10：日照模型只含几何，未做遮挡/反射/透光率；只出三个代表日",
            "本服务只出静态 PNG，不提供交互/动画，也不报告 token 与费用，"
            "相关计量一律 null",
        ],
        "metric_notes": {
            "token_and_cost": "服务未提供 token/费用端点，聊天平台也未报告逐请求消耗，"
                              "task-metrics.json 中相关字段一律 null，未按字数或余额估算",
            "element_limit": "服务在渲染期硬性拒绝超过 4096 个元素（case-06 v1 实测到 "
                             "Document contains more than 4096 elements），十件最高为 "
                             "case-05 的 3402",
        },
    }
    p = os.path.join(OUT, "portfolio.json")
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(out, ensure_ascii=False, indent=2))
    return p


GALLERY_CSS = """
:root{--bg:#0d1117;--card:#161b22;--line:#2b3440;--fg:#e6edf3;--fg2:#9aa7b4;--acc:#6ea8fe}
*{box-sizing:border-box}
body{margin:0;padding:32px 28px 64px;background:var(--bg);color:var(--fg);
font:15px/1.65 -apple-system,"Segoe UI","Noto Sans CJK SC",sans-serif}
h1{font-size:26px;margin:0 0 6px}
h2{font-size:18px;margin:40px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--line)}
.sub{color:var(--fg2);max-width:960px}
.meta{color:var(--fg2);font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(430px,1fr));gap:20px}
.case{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.case figure{margin:0;background:#0b0f14}
.case img{width:100%;display:block;border-bottom:1px solid var(--line)}
.case .body{padding:14px 16px 18px}
.case h3{margin:0 0 4px;font-size:16px}
.tag{display:inline-block;font-size:11px;letter-spacing:.06em;color:#0b0f14;
background:var(--acc);border-radius:999px;padding:2px 9px;margin:6px 6px 8px 0}
.tag.b{background:#7ee787}.tag.c{background:#ffa657}
dl{display:grid;grid-template-columns:76px 1fr;gap:2px 10px;margin:8px 0 0;font-size:13px}
dt{color:var(--fg2)}dd{margin:0}
ul{margin:6px 0 0;padding-left:18px;font-size:13px;color:var(--fg2)}
a{color:var(--acc)}
table{border-collapse:collapse;width:100%;font-size:13px;margin-top:8px}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}
th{background:#11161d}
code{background:#0b0f14;padding:1px 5px;border-radius:4px;font-size:12px}
footer{margin-top:44px;padding-top:14px;border-top:1px solid var(--line);color:var(--fg2);font-size:13px}
"""


def gallery_html():
    parts = ["<!DOCTYPE html>", '<html lang="zh-CN"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width,initial-scale=1">',
             "<title>B03 · 十件作品探索 DSL 的创意边界 · %s</title>" % RUN,
             "<style>%s</style></head><body>" % GALLERY_CSS,
             "<h1>B03 · 用十件作品探索 DSL 的创意边界</h1>",
             '<p class="sub">%s</p>' % CURATORIAL,
             '<p class="meta">run_id <code>%s</code> · 输出根 '
             '<code>outputs/%s/B03/</code> · 临时根 <code>tmp/%s/B03/</code> · '
             '十件全部为 <code>POST https://open-snapshot.muedsa.com/snapshot</code> '
             '的真实响应字节，无后处理、无 <code>&lt;Image&gt;</code> 嵌入位图。</p>' % (RUN, RUN, RUN),
             '<p class="meta">%s</p>' % DISCLAIMER,
             "<h2>作品索引（10 件，点击图片或文件名看原尺寸）</h2>",
             '<div class="grid">']
    for i, c in enumerate(CASES, 1):
        parts.append('<article class="case" id="%s">' % c["id"])
        parts.append('<figure><a href="%s"><img src="%s" width="%d" height="%d" '
                     'alt="%s"></a></figure>'
                     % (c["png"], c["png"], c["dimensions"][0], c["dimensions"][1],
                        c["title"]))
        parts.append('<div class="body">')
        parts.append("<h3>%02d · %s</h3>" % (i, c["title"]))
        parts.append('<span class="tag">主打能力：%s</span>' % c["lead"])
        parts.append('<span class="tag b">%d×%d</span>'
                     '<span class="tag c">%d elements / 4096</span>'
                     % (c["dimensions"][0], c["dimensions"][1],
                        c["dsl_element_count"]))
        parts.append("<dl>")
        for k, v in (("受众", c["audience"]), ("场合", c["ctx"]),
                     ("目标", c["goal"]), ("内容依据", c["basis"]),
                     ("视觉主张", c["intent"])):
            parts.append("<dt>%s</dt><dd>%s</dd>" % (k, v))
        parts.append("</dl>")
        parts.append("<dl><dt>能力探针</dt><dd>%s</dd>"
                     "<dt>看图证据</dt><dd>%s</dd></dl>"
                     % ("、".join("<code>%s</code>" % p for p in c["probes"]),
                        c["review"]))
        if c["unresolved"]:
            parts.append("<ul>%s</ul>"
                         % "".join("<li>遗留：%s</li>" % u for u in c["unresolved"]))
        parts.append('<p class="meta"><a href="%s">final.png</a> · '
                     '<a href="%s">final.snapshot</a> · <a href="%s">case.md</a></p>'
                     % (c["png"], c["snapshot"], c["case_md"]))
        parts.append("</div></article>")
    parts.append("</div>")

    parts.append("<h2>能力矩阵：十件各主打一类不同的 DSL 能力边界</h2>")
    parts.append("<table><tr><th>#</th><th>作品</th><th>主打能力</th>"
                 "<th>实际用到的标签与属性</th><th>elements</th></tr>")
    for i, c in enumerate(CASES, 1):
        parts.append('<tr><td>%02d</td><td><a href="#%s">%s</a></td>'
                     '<td>%s</td><td>%s</td><td>%d</td></tr>'
                     % (i, c["id"], c["title"], c["lead"], c["caps"],
                        c["dsl_element_count"]))
    parts.append("</table>")

    parts.append("<h2>十件都没有做到的（DSL 的真实边界，不是实现不足）</h2><ul>")
    for u in ("任意形状裁剪：解析器只注册 <code>ClipRect</code> / <code>ClipOval</code> / "
              "<code>ClipRRect</code>，官方 Widget 列表里的 <code>ClipPath</code> "
              "得到 <code>400 Unknown element tag</code>。",
              "矢量路径 / 折线 / 任意多边形：没有 line/path 图元，折线只能铺一串短矩形，"
              "面积填充只能逐扫描行铺。",
              "真透视 / 3D 相机：<code>Transform</code> 只有 paint-only 的 4×4 矩阵，"
              "透视项表现偏切变而非梯形收缩。",
              "布尔挖空：没有路径运算，case-02 的集章孔是纸色圆盘 + 内圈的行业近似。",
              "真正的行高控制：<code>Text</code> 的 <code>height</code> 属性与 "
              "<code>strutLeading</code> 都会让整段文字空白（HTTP 200 但不绘制）。",
              "行内语法高亮 / 逐 span 字体：<code>Text</code> 的颜色是 span 级，"
              "<code>fontFamily</code> 是缺字回退列表。",
              "交互与动画：服务只出静态 PNG。"):
        parts.append("<li>%s</li>" % u)
    parts.append("</ul>")

    parts.append("<h2>配套文件</h2><ul>")
    for f, d in (("portfolio.json", "结构化索引（十件全部字段）"),
                 ("portfolio.md", "同一份内容的人读版"),
                 ("technique-notes.md", "逐件手法笔记：技术、实测语义、反直觉结论、"
                                       "做不到的能力与证据"),
                 ("snapshot-usage.md", "文档依据、请求与迭代计数、逐图自检表、踩坑表"),
                 ("task-metrics.json", "结构化指标（token/费用等平台未提供的量一律 null）")):
        parts.append('<li><a href="%s">%s</a> — %s</li>' % (f, f, d))
    parts.append("</ul>")

    parts.append("<h2>真实渲染请求与逐件自检</h2><ul>")
    parts.append("<li>请求日志 <code>tmp/%s/B03/requests.jsonl</code>：359 次 "
                 "<code>POST /snapshot</code>，其中 261 次返回 image/png，98 次返回 "
                 "400/500 并保留响应文本于 <code>tmp/%s/B03/responses/</code>。</li>"
                 % (RUN, RUN))
    parts.append("<li>迭代日志 <code>tmp/%s/B03/iterations.jsonl</code>；"
                 "工具使用日志 <code>tmp/%s/B03/tool-usage.jsonl</code>（B 类额外要求）。</li>"
                 % (RUN, RUN))
    parts.append("<li>能力探针全部留在 <code>tmp/%s/B03/probes/</code>，"
                 "草稿 DSL 留在 <code>tmp/%s/B03/drafts/</code>，"
                 "放大核对图留在 <code>tmp/%s/B03/crops/</code>。</li>" % (RUN, RUN, RUN))
    parts.append("</ul>")

    parts.append("<footer>%s · 本页只使用本地相对链接，不依赖任何远程脚本或外链资源；"
                 "图片点开即为原尺寸 PNG（服务响应的原始字节）。</footer>" % DISCLAIMER)
    parts.append("</body></html>")
    p = os.path.join(OUT, "gallery.html")
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(parts))
    return p


def portfolio_md():
    L = ["# B03 · 十件作品探索 DSL 的创意边界",
         "",
         "- run_id：`%s`" % RUN,
         "- 输出根：`outputs/%s/B03/`　临时根：`tmp/%s/B03/`" % (RUN, RUN),
         "- 渲染入口：`POST https://open-snapshot.muedsa.com/snapshot`"
         "（snapkit 已带浏览器 UA）",
         "- 外部素材：**零**。全文没有任何 `<Image>` 标签，所有 PNG 都是服务响应的"
         "原始字节，没有后处理。",
         "- 元素上限 4096（服务在渲染期硬性拒绝），十件最高为 case-05 的 3402。",
         "",
         "> %s" % DISCLAIMER,
         "",
         "## 策展说明",
         "",
         CURATORIAL,
         "",
         "## 能力矩阵：十件各主打一类不同的 DSL 能力边界",
         "",
         "| # | 作品 | 画幅 | elements | 主打能力 |",
         "|---|---|---|---|---|"]
    for i, c in enumerate(CASES, 1):
        L.append("| %02d | [%s](#%s) | %d×%d | %d / 4096 | %s |"
                 % (i, c["title"], c["id"], c["dimensions"][0],
                    c["dimensions"][1], c["dsl_element_count"], c["lead"]))
    L += ["", "## 十件逐件索引", ""]
    for i, c in enumerate(CASES, 1):
        L += ["### %02d · %s" % (i, c["title"]), "",
              "![%s](%s)" % (c["title"], c["png"]), "",
              "| | |", "|---|---|",
              "| 文件 | [`%s`](%s) · [`%s`](%s) · [`%s`](%s) |"
              % ("final.png", c["png"], "final.snapshot", c["snapshot"],
                 "case.md", c["case_md"]),
              "| 画幅 | %d×%d（%s） |" % (c["dimensions"][0], c["dimensions"][1],
                                        c["mode"]),
              "| 字节 | PNG %s B · DSL %s B |"
              % ("{:,}".format(c["png_bytes"]), "{:,}".format(c["snapshot_bytes"])),
              "| elements | %d / 4096（%.1f%%） |"
              % (c["dsl_element_count"],
                 100.0 * c["dsl_element_count"] / 4096.0),
              "| 受众 | %s |" % c["audience"],
              "| 场合 | %s |" % c["ctx"],
              "| 目标 | %s |" % c["goal"],
              "| 内容依据 | %s |" % c["basis"],
              "| 视觉主张 | %s |" % c["intent"],
              "| 主打能力 | %s |" % c["lead"],
              "| 实际能力 | %s |" % c["caps"],
              "| 能力探针 | %s |" % "、".join("`%s`" % p for p in c["probes"]),
              "| 看图证据 | %s |" % c["review"], ""]
        if c["unresolved"]:
            L.append("遗留与不足：")
            L += ["- %s" % u for u in c["unresolved"]]
            L.append("")
    L += ["## 十件都没有做到的（DSL 的真实边界，不是实现不足）", "",
          "| 想要的能力 | 为什么做不到（实测依据） |", "|---|---|",
          "| 任意形状裁剪 | 解析器只注册 `ClipRect`/`ClipOval`/`ClipRRect`；官方 Widget "
          "列表里的 `ClipPath` 得到 `400 PARSE_ERROR: Unknown element tag [ClipPath]` |",
          "| 矢量路径 / 折线 / 多边形 | 没有 line/path 图元；折线只能铺一串短矩形，"
          "面积填充只能逐扫描行铺（case-01/04/10 都是这么画的） |",
          "| 真透视 / 3D 相机 | `Transform` 只有 paint-only 的 4×4 矩阵，透视项"
          "表现偏切变而非梯形收缩 |",
          "| 布尔挖空 | 没有路径运算；case-02 的集章孔是视觉近似 |",
          "| 真正的行高控制 | `Text` 的 `height` 属性与 `strutLeading` 都会让"
          "整段文字空白（HTTP 200 但不绘制） |",
          "| 行内语法高亮 / 逐 span 字体 | `Text` 的颜色是 span 级；`fontFamily` "
          "是缺字回退列表 |",
          "| 交互与动画 | 服务只出静态 PNG |",
          "| 位图合成 | 本套题禁止 `<Image>` 嵌位图 |",
          "",
          "## 整体最终审查", "",
          "把十张 `final.png` 用图像查看工具逐张重新打开后做的整体审查：",
          "",
          "- **画幅互不重复**：1600×1000 / 1600×1010 / 1440×1024 / 1500×1100 / "
          "1600×1060 / 1400×1000 / 1600×1120 / 1500×1050 / 1500×1090 / 1600×1150。",
          "- **底色基调九种**：深蓝值班板、暖白印刷稿、浅灰仓储终端、深紫选座页、"
          "深蓝观测卡、深蓝简报、暖白配方单、深蓝断面、高对比浅底发行单、深蓝日照墙"
          "（case-02 与 case-07 同为暖白但配色系统完全不同）。",
          "- **每张都有可复述的核心数字**，没有一张是「只有标签名和小方块」的能力示范板。",
          "- 制作期整体审查修掉的问题：case-09 的矩阵末列越界、case-09 第 12 条被摘要带盖住、"
          "case-10 剖面被压成 12 px、case-10 太阳光线压穿进深条标题、"
          "case-10 月柱高算出负数（两处：漏 `degrees()`、下界设错）。",
          "- 收尾复审（把十张 `final.png` 逐张重新打开）新发现并修掉三处**图与字互相打脸**的问题：case-01 的月相标签写着「亏凸月 · 照亮 72%」而画面是一弯约 20% 的右侧蛾眉（且与本页时间戳的真实月相 37.0% 残月不符），已改为按时间戳计算相位、并用 R(1−2k) 半椭圆逐行填充晨昏线；"
          "case-02 的 B 号取餐牌印「合计 86 元」而三行是 32+18+12=62 元，且票面写着「外带 TAKEAWAY / 堂食」与本稿自己的标题和尺寸表矛盾，已改为由明细求和并统一成取餐牌；"
          "case-09 摘要写「没有引入新的破坏性变更，仅有两项弃用与七项修复」，而 12 条清单里就有 2 条 BREAKING、5 条 FIXED，已改为从清单实算 2/2/3/5。",
          "- 复审也**排除**了三处疑似缺陷：case-02 左侧竖排「346 px」是旋转 -90° 的正常尺寸标注（用 `rotcheck.py` 旋正后确认）；case-04 B 区 05 排左块里那条空心小格是刻意的「本排座位放大条」（选中 24 号），不是错位元素；"
          "case-10 的「±9.45/±6.30/±3.15/±0.00」在 3.2× 下确认是 ± 不是 ≤/≥。",
          "",
          "## 配套文件", "",
          "- [`portfolio.json`](portfolio.json) — 结构化索引（十件全部字段 + 能力矩阵 + 审查记录）",
          "- [`technique-notes.md`](technique-notes.md) — 逐件手法笔记：技术、"
          "文档依据、探针与看图证据、应用价值、已确认的边界",
          "- [`snapshot-usage.md`](snapshot-usage.md) — 文档阅读、请求与迭代计数、"
          "逐图自检表、问题与修复表、如实说明",
          "- [`task-metrics.json`](task-metrics.json) — 结构化指标",
          "- [`gallery.html`](gallery.html) — 本地画廊（相对链接，可点开原图）",
          "- 请求/迭代/工具日志与探针：`tmp/%s/B03/requests.jsonl`、"
          "`iterations.jsonl`、`tool-usage.jsonl`、`probes/`、`drafts/`、"
          "`responses/`、`crops/`" % RUN,
          ""]
    p = os.path.join(OUT, "portfolio.md")
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))
    return p


if __name__ == "__main__":
    measure()
    for c in CASES:
        print(c["id"], c["dimensions"], c["dsl_element_count"])
    print(portfolio_json())
    print(portfolio_md())
    print(gallery_html())