"""B03 收尾交付物生成：portfolio.json / portfolio.md / gallery.md /
technique-notes.md / snapshot-usage.md。

数据来源全部是真实留痕：case-info.json（build_closeout.py 从 case.md、final.png、
final.snapshot、requests/iterations/tool-usage jsonl 读取）、requests.jsonl、
iterations.jsonl，以及 tmp/<run>/_suite/docs/ 下已抓取的文档缓存（引用前逐条 grep 校验，
校验不过的引用不写进文档）。META 里每件的受众/情境/目标/完成标准是我在开题时定下、
并写在各 case.md 中的判断，这里按 case.md 原文压缩成结构化字段。

用法（总任务根执行）：
  export SNAPSHOT_TASK_ROOT=... SNAPSHOT_RUN_ID=...
  python tmp/<run>/B03/build_portfolio.py
"""
import datetime
import glob
import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RID / "B03"
DOCS = ROOT / "tmp" / RID / "_suite" / "docs"
OUT = ROOT / "outputs" / RID / "B03"
SUITE_OUT = "outputs/%s" % RID
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

CI = json.loads((TMP / "case-info.json").read_text(encoding="utf-8"))
MET = json.loads((OUT / "task-metrics.json").read_text(encoding="utf-8"))
REQ = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()]
ITR = [json.loads(l) for l in (TMP / "iterations.jsonl").read_text(encoding="utf-8").splitlines()]
CASES = sorted(CI)

# 每件的结构化策展字段（内容与各 case.md 一致，此处只是拆成可机读的格）
META = {
 "case-01": dict(
   slug="夜航班门头霓虹效果图 + 施工标注",
   audience="招牌店主与夜间施工方",
   use_context="店门口用平板或打印 A3 图纸对照安装，横向双栏 2400×1200",
   user_goal="一次读完成品效果与安装参数：灯管颜色与色温、字位与灯位、变压器负载与回路分配",
   content_basis="虚构演示品牌「夜航班 / NIGHT FERRY」；灯管型号、色温、功率密度、变压器容量是行业量级演示取值；灯管长度与全部标注尺寸由画面几何按 PX_TO_MM=6 换算，页脚注明以现场复核为准",
   visual_intent="左效果图、右施工标注，一张图同时满足「看效果」和「照着装」",
   capabilities=["ImageFiltered 三层高斯模糊做霓虹芯与辉光（12 处）", "ClipOval 层叠剪月牙（遮挡圆取色自天空分带插值）",
                 "RADIAL 两端透明渐变做圆形光晕", "Container transform 2D 仿射斜切画雨棚",
                 "Positioned 网格 617 处 + Text 46 处", "textShadow 与描边字对比试验后弃用"],
   criteria="右侧标注数字与左侧几何一一对应（改字高即全表跟变）；五版均 200；TextFit 25 检 0 警；整图 5 次＋局部 8 次看图后 v05 定稿"),
 "case-02": dict(
   slug="「秋声」双日音乐节 Riso 双色海报",
   audience="街头行人（3 秒）＋印厂分色核对",
   use_context="灯箱与海报墙竖幅 1080×1528；印厂按 841mm 幅宽分两色上墨",
   user_goal="行人看懂「秋声／两日／10.24—10.25／造船厂」并扫码抢票；印厂核对哪些格只上 A、哪些只上 B、哪些两色同落",
   content_basis="节庆名称、届数、艺人名单、演出时段、地址、票价、二维码全部为虚构演示数据（人名刻意避开真实艺人），图内页脚、阵容栏右上、票价标题三处标注",
   visual_intent="两色分版并置＋叠印色标，让「分色关系」本身成为画面结构",
   capabilities=["显式乘算双色叠印（b03kit.overprint，逐格算第三色）", "双色分色栏：上墨面积率、叠印格数、叠色色值、网屏规格",
                 "描边字与实心字混排（foregroundMode STROKE）", "Positioned 889 处程序化排版，无外部素材"],
   criteria="两色版与叠印区在图上可逐格核对；分色栏数值与画面像素统计同源；八版迭代全部看图"),
 "case-03": dict(
   slug="AX-3 手电轴测拆解评审图版",
   audience="工业设计评审会成员（次要：打样工程师）",
   use_context="评审会投影或 841mm 幅宽打印（图上写明按此幅宽即 1:1），横版 1600×1000",
   user_goal="不看实物即回答：零件叫什么、按什么顺序装、装完多长多重、重心落在哪",
   content_basis="AX-3 手电的零件名、材料、工序、评审意见均为虚构演示数据，页脚声明不代表任何真实在售产品；材料密度（铝合金 2.70、光学 PC 1.20、无氧铜 8.96、FR-4 1.85、不锈钢 7.85、丁腈橡胶 1.05 g/cm³）与线胀系数量级为真实常数",
   visual_intent="纯 2D 仿射拼出的轴测爆炸体＋与序号一一对应的零件表，遮挡关系靠层序而非贴图",
   capabilities=["Transform 2D 仿射（行主序 6 元组）拼轴测体", "ClipOval 12 处切圆柱端面",
                 "SWEEP/RADIAL 渐变表现金属高光", "序号引线由几何换算，零件表与图形同源"],
   criteria="总长、总重、重心由零件表算出并可手核；轴测体前后遮挡可分辨；十版迭代含两次断言失败留证"),
 "case-04": dict(
   slug="唱片店本周黑胶选碟牌",
   audience="站在试听机前、手里拿着两张碟的顾客",
   use_context="店内方幅灯箱 1400×1400，停留几十秒",
   user_goal="判断这张碟一面装了多少分钟、每首多长、能不能听完、值不值这个价，并按四步流程试听",
   content_basis="曲目名、时长、年份、厂牌、价格、店名全部为虚构演示数据，完整写入 data.json 并在页脚与容量表下方标注；「12\" 33⅓ ≈22 分／12\" 45 ≈14 分／7\" 45 ≈5 分」是刻纹线速度的经验口径，图上写明为演示口径",
   visual_intent="一圈＝一面、弧长＝时长：SWEEP 渐变硬色标画扇区，容量占用条直接读「装不装得下」",
   capabilities=["SWEEP 渐变＋成对硬色标构造扇区（无矢量路径下的饼图）", "gradientStartAngle 非负弧度定位起始",
                 "起播时刻累加并 assert 校验", "容量占用＝面秒数/经验上限，逐面算出"],
   criteria="8 面 28 首 6862 秒＝1:54:22 与合计 ¥1,720 可由 data.json 复算；扇区与曲目一一对应；五版迭代定稿"),
 "case-05": dict(
   slug="独立书店月度书单目录页",
   audience="站在书架旁阅读椅上的读者（手持这期纸质书单样张）",
   use_context="纸质样张／平板阅读，竖幅 1200×1600，两分钟内查检",
   user_goal="回答「这本在哪个栏目、评论从第几页开始、多少钱、现在能不能买到」",
   content_basis="书名、作者、出版社、年份、页数、定价、库存状态、评论版面页数均为虚构演示数据，data.json.note 与页脚同时声明；派生数字（页码累加、码洋 ¥1,866、均价 ¥78、中位价 ¥70、精装 9／平装 15、现货 13／预订 6／停印 5、出现最多的出版社「城市观察 3 种」）全部由脚本算出",
   visual_intent="引导线的线型本身即库存状态：点线＝现货、虚线＝需预订、双线＝已停印",
   capabilities=["三段线型引导点（重复 Container 精确定位）", "三级层次：栏目→条目→页码/定价/库存",
                 "右栏承接左栏字母编号的跨栏排版", "Text 148 处，全篇无外部素材"],
   criteria="图例与每条目线型一致；统计口径与 data.json 复算一致；v01 未单独看图，其余各版看图后修改"),
 "case-06": dict(
   slug="咖啡馆柜台季节菜单",
   audience="柜台前平均停留 30 秒的顾客",
   use_context="柜台立牌 1080×1350，一眼扫完三类信息",
   user_goal="一次看清点什么、这杯咖啡因强不强、有没有自己会过敏的东西",
   content_basis="品名、价格、配比、热量、批次与烘焙日期为虚构演示数据；咖啡因模型（10.2mg/g 与器具萃取率）在 data.json 显式写出，属演示口径而非实测；派生数字（12 杯均价 ¥36、区间 ¥22–52、16 项合计 ¥527、最高 176mg／最低 66mg、强度分布 0:1 1:1 2:8 3:2、点心合计 1300 kcal、素食 14/16、过敏原 A7 B2 C3 D2、季节 61 天）由脚本算出",
   visual_intent="风险信息全部行内呈现而不是脚注：过敏原角标走行内，价格右对齐成一列",
   capabilities=["WidgetSpan 内嵌带 Text 的 Container 做行内角标（探针 08 证实成立）",
                 "四区分两栏的层级排版", "行内方块基线对齐的手工补偿", "渐变与色块表达季节带"],
   criteria="每个品项的角标与过敏原表一致；价格列对齐；五版迭代，v03 为截断响应留证未看图"),
 "case-07": dict(
   slug="徒步手册·环线剖面字符画",
   audience="出发前一晚摊开手册的徒步者",
   use_context="手册跨页 1600×1000，桌面阅读后决定出发时间与水量",
   user_goal="判断爬升集中在哪几公里、哪一段最陡、哪里还能补水、来回要多久",
   content_basis="路线、地名、高程、补水点全部为虚构演示数据，data.json.note 与页脚「徒步手册演示数据（航点为虚构）」声明；派生数字（累计上升＝下降＝808m、最高 1480m／最低 720m、6 段分段表、最陡段 20.8%（396m/1.9km）、Naismith 行进 5.39h＋30 分休息＝5.9h、3 处补水点、最后补水 10.7km、每格 110m 水平／43m 垂直、纵向放大 4.3 倍）由脚本算出",
   visual_intent="整幅山体由等宽块字符的密度画出：█ 路面、▓ 表层、▒ 深层、░ 岩体与天空——字符浓淡＝海拔",
   capabilities=["等宽块字符（█▓▒░）逐格排版成剖面", "按颜色切段的 <Raw> 多色行定位",
                 "块字符前进宽实测 0.60em 的行／列网格换算", "分段表与剖面共用同一数据源"],
   criteria="逐格读数与分段表一致（每格 110m／43m 可核）；最陡段与无水源段被单独括注；五版迭代，v03 为截断响应留证未看图"),
 "case-08": dict(
   slug="观星 App·夜空取景器界面稿",
   audience="夜里在户外举起手机的观测者",
   use_context="手机横屏界面稿 1920×1080，现场对天读取",
   user_goal="当场读出目标现在多高、朝哪个方位、还能看多久、值不值得现在过去架望远镜",
   content_basis="亮星／北斗的赤经赤纬与视星等为真实星表值；高度、方位、时角、过中天、没入时间、月相、银道面位置均由 astro8.py 算出（GMST 直式＋Meeus 低精度月球级数，精度约 ±0.5°，未做折光、章动与视差改正）；背景星 430 颗、山脊剪影与地平线灯光为程序化模拟（种子 20261010），不是星表或地理数据；海拔、GPS 星数、罗盘偏差为演示值",
   visual_intent="不是星空贴图，而是一帧可逐格复核读数的投影：星名、高度标尺、方位罗盘带、角距标尺与 HUD 档案卡互相咬合",
   capabilities=["天球坐标→等距方位柱面投影→Positioned 落位（19.05px/°）",
                 "BackdropFilter 2 处做 HUD 毛玻璃", "IndexedStack 1 处表达档案卡分页",
                 "ClipOval 16 处剪视场与月相", "<Raw> 44 处做刻度与罗盘带"],
   criteria="指极星延长落点与北极星差 2.94° 已写在画面上；self_checks 记录事实校核；五版迭代＋九张局部裁图核对"),
 "case-09": dict(
   slug="《裁》文化季刊封面·纸张尺寸特辑",
   audience="报刊亭在一米外扫过封面的读者",
   use_context="杂志封面 1080×1440（3:4），先被抓一下、走近再读要目",
   user_goal="读出特辑标题、开本表与要目，并判断这本讲「纸张尺寸」的杂志值不值得翻",
   content_basis="刊名《裁》/CAI CULTURE QUARTERLY、2026 秋季号·总第 037 期、定价 48.00 元、邮发代号 80-317、ISSN 2026-0037、五篇要目与页码、底部条码（图上明写「非可扫描编码」）均为设计示意，不是真实出版物，清单见 data.json.fictional；开本尺寸、面积、克重、字数与 √2 作图由 ISO 216 与本页面版式模型算出（版心模型四边 20mm、字号 10.5pt、行距 1.6 倍）",
   visual_intent="拼贴＝ISO 216 的裁半序列本身：A0→A6 七级沿长边裁半走成风车螺旋，每块色板就是对应开本的纸",
   capabilities=["ClipRRect 7 处逐窗口遮罩（不改变坐标，可逐级 assert）", "ClipOval 同心环挖出 √2 作图圆环",
                 "Container transform 七级各绕中心旋转 ±0.7–1.5° 模拟套准偏差",
                 "foregroundMode STROKE 描边行与实心行混排形成灰度带", "多级 Stack 嵌套（9 处）"],
   criteria="七级矩形与 ISO 216 标准表逐级比对通过；标签 7/7 完整落在本级板内；√2 三要素齐备；七版迭代，两处运行时断言失败留证"),
 "case-10": dict(
   slug="品牌字系统 Type Specimen·排版参数实测页",
   audience="带着三个问题来交付的客户设计师",
   use_context="字系统交付文档的一页 1080×1920，可照着复现",
   user_goal="得出这套品牌字能用到哪几个字重、字距/词距/行高改到多少才真的有效果、文档里写的高级特性在这台渲染器上生不生效",
   content_basis="页头「品牌字系统」为示例抬头，非真实客户；本页不含虚构数据，31 条实测值由 case10_measure.py 用 PIL 扫描上一版成品 PNG 得到，「预期」列按字宽模型（CJK 1.0em／拉丁 0.55em／等宽 0.60em）估算，两列之差与模型偏差都印在页面上",
   visual_intent="页面即量具：每个样本独占一条测量带，结论来自像素扫描而不是肉眼断言",
   capabilities=["测量带坐标写入 data.json → 扫描成品 PNG → 实测值印回下一版（渲染/扫描/再渲染闭环）",
                 "height 五栏并列证明行距＝字号×倍数（默认档 1.22em≠1.45em）",
                 "letterSpacing 四档／wordSpacing 三档证明线性与「只对空格生效」",
                 "未安装字族回退探针（两行同 186px）", "fontFeatures 四组并排证明只解析不应用"],
   criteria="31 条测量带全部实测并印回；TextFit 161 检 0 警；运行时断言（标签不超框、窗口在带内）通过；七版迭代含一次流程错误留证"),
}

# 技法 → 文档依据候选（引用前用 grep 在已抓取的文档缓存里校验关键词，校验不过就不写）
DOC_CITES = {
 "case-01": [("image-filtered.html.txt", "sigmaX", "ImageFiltered 固定高斯模糊并按 sigma 自动外扩边界（辉光不被文字盒子截断的依据）"),
             ("painting.html.txt", "boxShadow", "boxShadow 属性能写在哪些绘制装饰上（实测其模糊不跟随 borderRadius）"),
             ("transform.html.txt", "transform", "transform 矩阵写法与 transformAlignment")],
 "case-02": [("color-filtered.html.txt", "ColorFiltered", "ColorFiltered 只过滤子树自身像素、不与背景混合（因此双色叠印必须显式乘算）"),
             ("parser-tags.html.txt", "foregroundMode", "描边字属性在标签/属性总表里的定义"),
             ("parser-tags.html.txt", "STROKE", "foregroundMode 的枚举取值")],
 "case-03": [("transform.html.txt", "transform", "2D 仿射矩阵与分量解释"),
             ("clip-rect.html.txt", "ClipRect", "可用的矩形遮罩标签（无 ClipPath 时的替代）"),
             ("painting.html.txt", "gradientType", "SWEEP/RADIAL 渐变的取值与语义")],
 "case-04": [("parser-tags.html.txt", "gradientStops", "硬色标写法（扇区图的构造基础）"),
             ("parser-tags.html.txt", "gradientStartAngle", "起始角属性（用非负弧度最稳）"),
             ("parser-errors.html.txt", "Attr", "400 报文里 Attr [...] 类错误的形态与含义（gradientRadius 对 SWEEP 无效那次）")],
 "case-05": [("text.html.txt", "letterSpacing", "文本属性表（行内字距与引导线间距反算）"),
             ("layout.html.txt", "Row", "行/列布局能力边界，决定用 Positioned 逐段铺引导点"),
             ("positioned.html.txt", "Positioned", "绝对定位属性")],
 "case-06": [("rich-text.html.txt", "WidgetSpan", "行内嵌入 widget 的合法性依据"),
             ("widgets.html.txt", "WidgetSpan", "widget 清单中的行内组件"),
             ("text.html.txt", "textAlign", "价格右对齐与多栏文本对齐")],
 "case-07": [("fonts.txt", "DejaVu Sans Mono", "渲染服实际安装字族（等宽块字符可行性依据）"),
             ("parser-tags.html.txt", "fontFamily", "字族回退写法"),
             ("parser.html.txt", "CDATA", "块字符与符号需要 CDATA 包裹的原因")],
 "case-08": [("backdrop-filter.html.txt", "BackdropFilter", "HUD 毛玻璃标签与属性"),
             ("container.html.txt", "IndexedStack", "IndexedStack 作为分页容器的依据"),
             ("container.html.txt", "borderRadius", "圆形遮罩与端面的圆角半径"),
             ("positioned.html.txt", "Positioned", "把投影坐标逐点落位")],
 "case-09": [("container.html.txt", "clipBehavior", "Container 自带裁剪属性（实测对整幅子树 400 Check failed）"),
             ("clip-rect.html.txt", "ClipRect", "可用遮罩标签清单，最终改用 ClipRRect/ClipOval"),
             ("container.html.txt", "transformAlignment", "各窗口绕自身中心旋转的属性来源"),
             ("enums.html.txt", "CENTER", "transformAlignment 枚举取值")],
 "case-10": [("text.html.txt", "height", "行高属性（实测＝字号×倍数）"),
             ("text.html.txt", "letterSpacing", "字距属性定义"),
             ("text.html.txt", "wordSpacing", "词距属性（实测只对空格生效）"),
             ("text.html.txt", "fontFeatures", "高级字体特性（实测只解析不应用）"),
             ("fonts.txt", "Inter", "服务端实际 27 族清单，含 Inter 各字重")],
}
VERIFIED, DROPPED = [], []
for c, cites in DOC_CITES.items():
    for fn, term, note in cites:
        p = DOCS / fn
        ok = p.exists() and (term in p.read_text(encoding="utf-8", errors="ignore"))
        (VERIFIED if ok else DROPPED).append((c, fn, term, note))
DOC_BY_CASE = {}
for c, fn, term, note in VERIFIED:
    DOC_BY_CASE.setdefault(c, []).append((fn, term, note))


def reqs_of(prefix):
    return [r for r in REQ if r["request_id"].startswith(prefix)]


def iters_of(case):
    n = case.split("-")[1]
    return [i for i in ITR if i["version"].startswith("case-%s-" % n)]


def previews(case):
    return sorted(p.name for p in (OUT / case).glob("v*-preview.png"))


def strip_md(t):
    return t.replace("`", "").replace("**", "")


CURATORIAL = (
    "十件作品按「真实使用者＋真实可核对的数字」两条线选：夜航班门头、音乐节海报、手电评审图版、"
    "黑胶选碟牌、书店书单、柜台菜单、徒步剖面、观星取景器、季刊封面、品牌字 specimen。"
    "共同点不是风格，而是每张图都把自己怎么算出来的写在图上：灯管长度由像素反算、扇区弧长由曲目秒数占、"
    "字符浓淡对应海拔、坐标由赤经赤纬投影、拼贴就是 ISO 216 的裁半序列、字距结论来自成品像素扫描。"
    "手法全部落在服务真实支持的构造上——无矢量路径就用渐变与块字符逼近，无 ClipPath 就用 ClipRRect/ClipOval，"
    "回退字族不可见就用同宽探针把它变成可证伪实验；不成立的地方保留 400/500 报文，改实现而不是后处理冒充。")

COLLECTION_REVIEW = dict(
    reviewed_at=NOW,
    method="逐件打开 outputs/<run>/B03/case-NN/final.png 全图核对，再对照同名 final.snapshot 的节点计数、"
           "requests.jsonl 的响应指纹与 case.md 的迭代表；QA 裁图只作观察且全部留在 tmp 下",
    independence="十个触点的媒介、尺寸、方向、数据模型与主手法互不重复：2400×1200 至 1080×1920 六种幅面，"
                 "效果图／海报／图版／牌示／目录页／菜单／剖面／界面稿／封面／specimen 十类",
    shared_assets="跨件复用的只有自研构件（b03kit 的 tlab/TextFit 闸门、overprint、skew、neon_if）与探针结论，"
                  "没有任何一件复用另一件的成品图；十件 DSL 的 <Image> 计数均为 0",
    remaining="服务无矢量 path 导致曲线仍是折线逼近；fontFeatures 只解析不应用；等宽块字符前进宽与文档初测不一致（已实测校正为 0.60em）")

# ---------------------------------------------------------------- portfolio.json
cases_json = []
for c in CASES:
    v, m = CI[c], META[c]
    rq = reqs_of("B03-%s-" % c)
    it = iters_of(c)
    cases_json.append(dict(
        id=c, title=strip_md(v["title"]), audience=m["audience"], use_context=m["use_context"],
        user_goal=m["user_goal"], content_basis=m["content_basis"], visual_intent=m["visual_intent"],
        png="%s/final.png" % c, snapshot="%s/final.snapshot" % c,
        dimensions=v["dimensions"], png_bytes=v["png_bytes"], png_md5=v["png_md5"],
        dsl_chars=v["dsl_chars"], dsl_nodes=v["nodes"],
        data_file="%s/data.json" % c if v["has_data_json"] else None,
        case_report="%s/case.md" % c,
        supporting_assets=[],
        dsl_capabilities=m["capabilities"],
        completion_criteria=m["criteria"],
        visual_review=dict(
            whole_image_views=sum(1 for i in it if i.get("image_viewed")),
            version_previews=previews(c),
            qa_crops=v["qa_crops"],
            note="整幅看图 %d 次%s；QA 裁图 %d 张在 tmp 下，只用于观察，不作为交付物"
                 % (sum(1 for i in it if i.get("image_viewed")),
                    "（其中 %d 次为局部裁切放大）" % sum(1 for i in it if i.get("image_view_scope"))
                    if any(i.get("image_view_scope") for i in it) else "",
                    len(v["qa_crops"])),
            per_case=[dict(version=i["version"], viewed=bool(i.get("image_viewed")),
                           scope=i.get("image_view_scope") or "整幅",
                           request_id=i.get("request_id")) for i in it]),
        request_ids=[r["request_id"] for r in rq],
        promoted_request=v["promoted_from"], promoted_server_timing=v["server_timing"],
        iteration_ids=[i["iteration_id"] for i in it],
        versions=v["versions"], tool_usage=sorted(set(v["tool_usage"])),
        unresolved_issues=[strip_md(x)[:220] for x in v["boundaries"][:3]] or ["见 case.md 已知失真与演示值"],
    ))
PORT = dict(schema_version=1, path_base="output_dir", task_id="B03", run_id=RID,
            task_name="用十件作品探索 DSL 的创意边界", status="completed",
            asset_policy=MET["asset_policy"], curatorial_statement=CURATORIAL,
            cases=cases_json, final_collection_review=COLLECTION_REVIEW,
            unresolved_issues=MET["unresolved_issues"])
(OUT / "portfolio.json").write_text(json.dumps(PORT, ensure_ascii=False, indent=1), encoding="utf-8")

# ---------------------------------------------------------------- portfolio.md
L = ["# B03 · 十件作品作品集（portfolio.md）",
     "",
     "任务：`B03` ｜ run_id：`%s` ｜ 状态：**completed**（10/10 件定稿） ｜ 路径基准：本文相对 "
     "`outputs/%s/B03/`；tmp 证据相对总任务根并显式写出 `tmp/%s/…`。" % (RID, RID, RID),
     "",
     "## 策展说明",
     "",
     CURATORIAL,
     "",
     "## 一览",
     "",
     "| 触点 | 作品 | 幅面 | 主手法（一句话） | 定稿请求 |",
     "| --- | --- | --- | --- | --- |",
     ]
FIRST_TECH = {c: strip_md(CI[c]["techniques"][0]).split("。")[0][:64] for c in CASES}
for c in CASES:
    v = CI[c]
    L.append("| %s | [%s](%s/final.png) | %d×%d | %s | `%s` |" % (
        c, META[c]["slug"], c, v["dimensions"][0], v["dimensions"][1],
        FIRST_TECH[c], v["promoted_from"]))
L += ["", "## 逐件说明", ""]
for c in CASES:
    v, m = CI[c], META[c]
    L += ["### %s · %s" % (c, m["slug"]), "",
          "- **受众**：%s" % m["audience"],
          "- **使用情境**：%s（%d×%d）" % (m["use_context"], v["dimensions"][0], v["dimensions"][1]),
          "- **使用者要做的事**：%s" % m["user_goal"],
          "- **视觉主张**：%s" % m["visual_intent"],
          "- **内容依据**：%s" % m["content_basis"],
          "- **实际用到的 DSL 能力**：%s" % "；".join(m["capabilities"]),
          "- **节点构成**：Positioned %d／Container %d／Text %d／Stack %d／ClipRRect %d／ClipOval %d／"
          "ImageFiltered %d／Image %d，DSL %s 字符" % (
              v["nodes"]["Positioned"], v["nodes"]["Container"], v["nodes"]["Text"], v["nodes"]["Stack"],
              v["nodes"]["ClipRRect"], v["nodes"]["ClipOval"], v["nodes"]["ImageFiltered"], v["nodes"]["Image"],
              format(v["dsl_chars"], ",")),
          "- **辅助素材**：无（`<Image>` 计数 0，画面全部由 DSL 构造）" if v["nodes"]["Image"] == 0
          else "- **辅助素材**：见 data.json",
          "- **完成标准与自检**：%s" % m["criteria"],
          "- **定稿**：`%s/final.png`（%s 字节，md5 `%s`）↔ `%s/final.snapshot`，提升自 `%s`" % (
              c, format(v["png_bytes"], ","), v["png_md5"], c, v["promoted_from"]),
          "- **预览与看图**：%s；QA 裁图 %d 张（tmp 下，只作观察）" % (
              "、".join(previews(c)) or "无", len(v["qa_crops"])),
          "- **报告**：`%s/case.md`%s" % (c, "｜数据：`%s/data.json`" % c if v["has_data_json"] else ""),
          ""]
L += ["## 合集层面的审查", "",
      "- 方法：%s" % COLLECTION_REVIEW["method"],
      "- 独立性：%s" % COLLECTION_REVIEW["independence"],
      "- 复用边界：%s" % COLLECTION_REVIEW["shared_assets"],
      "- 遗留：%s" % COLLECTION_REVIEW["remaining"], "",
      "## 未解决事项", ""] + ["- %s" % x for x in MET["unresolved_issues"]] + [
      "",
      "机器可读版本见 `portfolio.json`；逐图预览见 `gallery.md`；手法与文档依据见 `technique-notes.md`；"
      "服务使用与踩坑见 `snapshot-usage.md`；指标见 `task-metrics.json`。"]
(OUT / "portfolio.md").write_text("\n".join(L) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- gallery.md
G = ["# B03 · 作品画廊（gallery.md）",
     "",
     "10 件定稿作品，全部为 open-snapshot 服务真实响应的 PNG，且每张有同名完整 DSL。",
     "图片与文件链接相对本文件所在的 `outputs/%s/B03/`；tmp 下的证据另以 `../../../tmp/%s/B03/` 开头。" % (RID, RID),
     ""]
for c in CASES:
    v, m = CI[c], META[c]
    G += ["## %s · %s（%d×%d）" % (c, m["slug"], v["dimensions"][0], v["dimensions"][1]),
          "",
          "![%s 定稿图：%s](%s/final.png)" % (c, m["slug"], c),
          "",
          "- 定稿图：[`%s/final.png`](%s/final.png)（%s 字节，md5 `%s`）" % (
              c, c, format(v["png_bytes"], ","), v["png_md5"]),
          "- 同名主体 DSL：[`%s/final.snapshot`](%s/final.snapshot)（%s 字符）" % (
              c, c, format(v["dsl_chars"], ",")),
          "- 单件报告：[`%s/case.md`](%s/case.md)%s" % (
              c, c, "｜数据：[`%s/data.json`](%s/data.json)" % (c, c) if v["has_data_json"] else ""),
          "- 渲染请求：`%s`（服务端头 %s）" % (v["promoted_from"], v["server_timing"] or "未记录"),
          "- 版本预览：%s" % ("".join(
              ["[`%s`](%s/%s) " % (p, c, p) for p in previews(c)]) or "无"),
          ""]
G += ["## 全部版本一览（过程留痕，非交付物）", "",
      "| 触点 | 提交过的版本 | 成功响应 | 失败/异常响应 |", "| --- | --- | --- | --- |"]
for c in CASES:
    v = CI[c]
    G.append("| %s | %s | %d | %d |" % (c, " ".join(v["versions"]), v["renders_ok"], v["renders_failed"]))
G += ["",
      "过程留痕统计见 `task-metrics.json`：%s。" % MET["counts"]["final_image_note"],
      "预览图与各次真实响应同源；探针图与 QA 裁图留在 `../../../tmp/%s/B03/` 下，属过程证据，不计入作品。" % RID]
(OUT / "gallery.md").write_text("\n".join(G) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- technique-notes.md
T = ["# B03 · 手法笔记（technique-notes.md）",
     "",
     "逐件记录：独到手法 → 实际文档依据 → 试验与看图证据 → 应用价值 → 已确认的边界。",
     "文档依据是 `tmp/%s/_suite/docs/` 里真实抓取的页面缓存，生成本文前逐条 grep 校验关键词，" % RID,
     "校验不通过的引用已删除（共删除 %d 条，见文末）。探针与请求 ID 可在 `tmp/%s/B03/requests.jsonl` 复查。"
     % (len(DROPPED), RID), ""]
VALUE = {
 "case-01": "效果图与施工标注同图，省掉一次「效果图转施工图」的返工；辉光不靠素材贴图，改字号即改灯管长度，参数化到能直接报价。",
 "case-02": "把 Riso 分色核对从「印厂自己猜叠印结果」变成图上可读的事实；行人层与印厂层共用一张图，减少一版物料。",
 "case-03": "评审会现场能直接按零件表逐条过装配关系，重心与总重的算式写在图边，质疑时可当场复算，不依赖实物。",
 "case-04": "把「这面装不装得下」变成弧长与占用条两眼看齐，顾客自己就能决定哪张上机；数据改动即整牌重算，适合每周换。",
 "case-05": "线型承载库存状态，读者顺着引导线找页码时已经把「能不能买到」读完了，省一遍小字；书店每期可直接套模板。",
 "case-06": "过敏原与咖啡因行内呈现，30 秒停留内不需要翻到脚注，是食品安全信息真正被读到的前提。",
 "case-07": "剖面与分段表同源，徒步者按格读数就能决定出发时间与背水量；块字符画法让「图」和「文」在同一个数据模型上。",
 "case-08": "读数链条（星表→投影→标尺→档案卡）全部可复核，界面稿即为算法验收件，避免设计与算法两份真相。",
 "case-09": "封面主题（纸张尺寸的秩序）由几何本身承担，色板即开本；读者起疑时可以在图上直接核算 √2 与面积比。",
 "case-10": "把字系统交付里最容易被含糊过去的三个参数（字重上限、字距/行高生效量、高级特性可用性）变成实测结论，客户拿到的是一页可复现的验收记录。",
}
for c in CASES:
    v, m = CI[c], META[c]
    T += ["## %s · %s" % (c, m["slug"]), "", "### 独到手法", ""]
    for i, t in enumerate(v["techniques"], 1):
        T.append("%d. %s" % (i, strip_md(t)))
    T += ["", "### 实际文档依据（已 grep 校验的缓存页）", ""]
    for fn, term, note in DOC_BY_CASE.get(c, []):
        T.append("- `tmp/%s/_suite/docs/%s` 命中关键词 `%s`：%s" % (RID, fn, term, note))
    if not DOC_BY_CASE.get(c):
        T.append("- 本件没有可校验的文档条文，结论全部来自探针请求实测（见下）")
    text = v["review_evidence"] + " " + " ".join(v["techniques"]) + " " + v["truth"]
    probes = sorted({m_ for m_ in re.findall(r"B03-probe-[A-Za-z0-9-]+", text)})
    T += ["", "### 试验与看图证据", "",
          "- 本件报告中点名的探针请求：%s" % ("、".join("`%s`" % p for p in probes)
                                     or "未点名（探针结论汇总见 `tmp/%s/B03/PLAN.md` 与 probe/ 目录）" % RID),
          "- 定稿看图证据：整幅 %d 次（`%s`），局部裁图 %d 张（`%s`）" % (
              sum(1 for i in iters_of(c) if i.get("image_viewed")),
              "、".join(previews(c)) or "见 %s/final.png" % c,
              len(v["qa_crops"]), "、".join(os.path.basename(x) for x in v["qa_crops"]) or "无"),
          "- 单件迭代表：`%s/case.md` 的「迭代」小节（本机记录 %d 条迭代）" % (c, v["iteration_records"]),
          "", "### 应用价值", "", VALUE[c], "", "### 已确认的边界", ""]
    if v["boundaries"]:
        T += ["- %s" % strip_md(b) for b in v["boundaries"]]
    else:
        T += ["- %s" % strip_md(x) for x in v["truth"].split("\n\n")[:2]]
    T.append("")
T += ["## 跨件经验（十件做完才看得见的）", "",
      "- 服务没有矢量路径与 ClipPath：曲线只能靠 SWEEP/RADIAL 硬色标、逐段矩形和块字符逼近。"
      "这条约束决定了 case-04 的扇区、case-03 的端面、case-07 的山体是三种不同做法，而不是一个「画图组件」。",
      "- `Container` 的 `clipBehavior` 对整幅子树会 400（`Check failed`，10 次留证），可用遮罩只有 ClipRRect/ClipOval/ClipRect；"
      "遮罩只裁像素不改坐标，所以 case-09 能逐级 assert 窗口边界。",
      "- 文本是这套服务最贵也最脆的部分：`<`、`>` 不解析实体会让整份 DSL 400，必须走 CDATA；"
      "估算器（TextFit）偏保守会误报，但漏报代价是图上截断，所以「带警不提交」比放宽阈值便宜。",
      "- 默认行距由字族 metrics 决定：Inter @17px 实测 1.22em，而不是套件先前用的 1.45em 估算常数——"
      "同一套估算跨字族不通用，凡按行距定位的排版都应实测（case-10）。",
      "- 未安装字族不是「回退不可知」：两条未安装族都得到 186px，说明回退到同一平台默认字体，"
      "这可以用一个宽度探针证伪，比猜字族清单可靠。",
      "- `fontFeatures`（tnum/lnum smcp/liga）四组实测与基准全等：只被解析、不被应用；"
      "需要等宽数字时靠等宽字族或版式兜底。",
      "- 传输层故障（curl 28/56、Content-Length 截断）与 DSL 无关，重试即可；但提升脚本必须按"
      "「同名记录里最后一次 200」取件，否则会误提失败响应（case-09 踩到并修）。",
      "", "### 未能校验因而删除的引用（%d 条）" % len(DROPPED), ""]
T += ["- %s：`%s` 中未出现 `%s`（未写入本文）" % (c, fn, term) for c, fn, term, _ in DROPPED] or ["- 无"]
(OUT / "technique-notes.md").write_text("\n".join(T) + "\n", encoding="utf-8")

(TMP / "portfolio-meta.json").write_text(
    json.dumps(META, ensure_ascii=False, indent=1), encoding="utf-8")
(TMP / "doc-cites.json").write_text(json.dumps(
    dict(verified=VERIFIED, dropped=DROPPED), ensure_ascii=False, indent=1), encoding="utf-8")
print("portfolio.json cases", len(cases_json), "| verified doc cites", len(VERIFIED),
      "| dropped", len(DROPPED))
for c, fn, term, note in DROPPED:
    print("  DROP", c, fn, term)
