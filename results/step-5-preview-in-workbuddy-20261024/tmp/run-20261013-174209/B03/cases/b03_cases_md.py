#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B03 · 十件作品元数据与逐件完成标准（供 case.md / portfolio 交付复用）。"""
from __future__ import annotations

RUN_ID = "run-20261013-174209"

# 每件：title/canvas/audience/scenario/goal/visual/basis/technique/
#       criteria[(id, condition, status, evidence)] / rounds / views
CASES = {
    "case-01": {
        "title": "霓虹演出海报",
        "canvas": "1080×1440（3:4 社交竖版）",
        "audience": "独立音乐与夜场文化受众",
        "scenario": "社交平台传播的 livehouse 夜场演出海报",
        "goal": "3 秒内传递乐队名、巡演站次、日期场地与购票入口",
        "visual": "三层渐变夜空 + 霓虹管标题 + 旋转光束 + 星晕 + 剪影人群收底",
        "basis": "虚构独立乐队「北极星信号 Polaris Signal」冬夜巡演第三站 · "
                 "潮汐 Livehouse；乐队、场次、票价均为虚构演示内容，不宣称实际演出",
        "technique": "三层渐变夜空 + RADIAL 星晕 + Container transform 矩阵旋转光束 + "
                     "多层 textShadow 霓虹辉光 + Text STROKE 空心管描边 + 剪影收底",
        "criteria": [
            ("C01-1", "霓虹辉光可辨：标题为空心管 + 多层辉光，非实心字",
             "met",
             "dsl：STROKE 描边 2.2px（v02 加粗，1.2px 在 108px 下过细）+ 三层 textShadow 辉光；"
             "view-zoom：整图 + 标题分区放大，管芯空心与内外辉光层次清晰可辨"),
            ("C01-2", "光束与星晕为矩阵旋转构造，角度经计算",
             "met",
             "dsl：Container transform=matrix 旋转 -90° 纵向巡演锁扣 + 旋转光束；"
             "pixel：分区放大实测光束角度与矩阵 deg 一致；带环行星双弧 ring_segment"),
            ("C01-3", "构图均衡：左上不留大面积空区",
             "met",
             "view-zoom：v02 新增行星 + 纵向 TOUR 锁扣填充左上（原 y 100–460 空区），"
             "与右侧极星光束形成对角平衡；整图复核通过"),
            ("C01-4", "演出信息四要素齐全无裁切",
             "met",
             "dsl：T() 宽度自检 0 警告；view-zoom：乐队名/日期 12.24 / 场地 / CTA 均完整"),
        ],
        "rounds": "v01 修 T() 漏传 nodes=n 致 10 处文本缺失；v02 描边加粗 + 左上构图配重",
        "views": ["整图", "标题区", "左上行星锁扣区", "信息卡与 CTA 区", "人群剪影收底"],
    },
    "case-02": {
        "title": "毛玻璃天气行程卡",
        "canvas": "1080×1920（9:16 手机）",
        "audience": "计划前往鹭洲湿地公园的访客",
        "scenario": "出行 App「今日行程」底部三层面板浮层",
        "goal": "一屏读完天气、当日行程与行动入口，面板浮动于实景之上",
        "visual": "渐变天色 + 毛玻璃三层面板 + 柔化云层 + 渐变 CTA + Flex 时间轴",
        "basis": "虚构出行 App「云图 Weather」；服务对象为鹭洲湿地公园访客（B02 规范数据："
                 "开放 旺季 08:30–20:00 / 淡季 09:00–17:00、周二闭园、咨询 0512-6688-0000），"
                 "天气与行程为演示数据",
        "technique": "frosted() 三层面板（ClipRRect + BackdropFilter 高斯毛玻璃）+ "
                     "ImageFiltered 柔化云层 + 渐变天色 + 渐变 CTA + Flex 时间轴",
        "criteria": [
            ("C02-1", "毛玻璃真实：背后内容被模糊且圆角裁剪",
             "met",
             "dsl：frosted() = Positioned→ClipRRect(r28)→BackdropFilter(sigma14)→Container；"
             "view-zoom：面板分区放大，背后条纹/山形被高斯模糊 + 圆角边框齐整"),
            ("C02-2", "三层面板垂直预算精确，无重叠无溢出",
             "met",
             "dsl：场景 0–1080 / 面板一 1096–1436 / 面板二 1452–1852 / 面板三 1860–1916；"
             "pixel：分区实测各面板边界与预算一致"),
            ("C02-3", "底部行动条贴画布底边，仅上圆角",
             "met",
             "dsl：ClipPath 自定义路径（M 28,0 L 956,0 Q 984,0 984,28…）仅上两角 r28；"
             "pixel：v02 修复后底条下缘与画布底边 0 缝隙（v01 曾有 4px 缝）"),
            ("C02-4", "云层柔化与天色渐变分层可辨",
             "met",
             "dsl：ImageFiltered sigma 柔化云组 + 三段渐变天色；view-zoom：云层边缘虚化过渡自然"),
        ],
        "rounds": "v01 渲染前自检拦截 6 处 += 字符展开；v02 修底条 4px 缝隙贴边",
        "views": ["整图", "天色与云层区", "天气面板", "行程面板", "底部行动条"],
    },
    "case-03": {
        "title": "剪纸风国家公园导览图",
        "canvas": "1920×1080（16:9 横版壁画）",
        "audience": "游客中心内全体访客（含亲子与长者）",
        "scenario": "游客中心大幅墙面导览图",
        "goal": "远距离识别园区格局，近距离读取动线、观测点与规范信息",
        "visual": "剪纸风分层剪影 + EVEN_ODD 镂空纹样 + 日月环 + 云纹滚边",
        "basis": "鹭洲湿地公园游客中心导览图；数据用 B02 项目规范（862 公顷 / 287 种鸟 / "
                 "426 种植物、开放时间、票价、电话、地址），园区为虚构演示项目",
        "technique": "ClipPath EVEN_ODD 多轮廓镂空剪纸（团花/云朵卷曲/鱼鳞/亭窗/芦苇中缝/"
                     "烛穗环/船帆月牙）+ 分层剪影 + ClipOval 日月 + 云纹滚边",
        "criteria": [
            ("C03-1", "镂空纹样正确：EVEN_ODD 仅镂空实体内部子路径",
             "met",
             "dsl：卷曲子路径回到剪影体内（v02 修复：云朵 bump 上凸、卷曲内嵌）；"
             "view-zoom：7 分区逐个核对团花六瓣、芦苇中缝、烛穗环、鱼鳞、亭窗、船帆月牙全部为真镂空"),
            ("C03-2", "剪纸分层可辨：前景/中景/远景层次分明",
             "met",
             "view-zoom：天空加深为 #C7DAD2 托出白云剪影（v02），远近山影/水岸/船只分层清晰"),
            ("C03-3", "导览信息可读：动线、观测点、规范数据齐全",
             "met",
             "dsl：三条动线 + 观测点编号 + 开放时间/票价/电话/统计数；"
             "pixel：抽测文字对比度达标；数据与 B02 跨用例规范一致"),
            ("C03-4", "曲线全部采样为 M/L 折线（不依赖未探测的 Q/C）",
             "met",
             "dsl：所有路径为 M/L 折线段；view-zoom：放大部分路径边缘平滑无断点"),
        ],
        "rounds": "v02 修云朵 bump 角度（下半圆→上凸）与卷曲越界致整朵云只剩 4 个白点",
        "views": ["整图", "云朵与团花区", "芦苇中缝", "烛穗环与鱼鳞", "亭窗与船帆", "日月环", "图板滚边"],
    },
    "case-04": {
        "title": "双色马拉松数据海报",
        "canvas": "1080×1350（4:5 社交竖版）",
        "audience": "完赛选手与跑步社群",
        "scenario": "赛事官方社交账号完赛数据海报",
        "goal": "一张图传递赛事规模与个人完赛数据，适合转发",
        "visual": "冷暖双色调赛照 + Flex 大数字排版 + 成绩分布条形图 + 偏移框破版",
        "basis": "虚构赛事「2026 鹭洲湿地半程马拉松」（2026-10-25 周日）；"
                 "参赛人数、成绩分布等均为虚构演示数据（case.md 已注明）",
        "technique": "ColorFiltered 嵌套双色调（内层 SCREEN 靛蓝映射暗部 × 外层 MULTIPLY "
                     "暖黄映射亮部，作用于 PIL 生成灰度赛照 dataUri）+ Flex 大数字 + 偏移框破版",
        "criteria": [
            ("C04-1", "双色调斜坡成立：暗部偏冷、亮部偏暖",
             "met",
             "pixel：v03 按 Skia 混合数学重配后采样——最暗 (36,47,57) 冷蓝 slate → "
             "中调 (114,112,95) 暖灰 → 最亮 (240,216,157) 暖奶油；v01 曾单一暖褐（最暗仅 102,103,89）"),
            ("C04-2", "完赛数据自洽：大数字与分布图同源",
             "met",
             "dsl：人数/完赛率/平均成绩/ PB 四大数字 + 成绩分布条形图；"
             "calc：分布各组人数合计 = 参赛人数（复算一致）"),
            ("C04-3", "dataUri 图片合法嵌入且注明用途",
             "met",
             "dsl：PIL 生成灰度赛照 → PNG base64 dataUri（合法用途：双色调映射底图）；"
             "渲染 HTTP 200 无 IMAGE_LOAD_ERROR"),
            ("C04-4", "Flex 大数字行对齐：四数字基线一致、分隔线等长",
             "met",
             "dsl：Row/Expanded/Column 结构 + 等比分隔线；view-zoom：分区放大实测四数字基线对齐"),
        ],
        "rounds": "v01→v03 重配双色调两端（暖端提亮 #F6DEA0、冷端 MULTIPLY #16294F 穿透）",
        "views": ["整图", "双色调主图", "Flex 数据行", "成绩分布图", "偏移框与距离带"],
    },
    "case-05": {
        "title": "自适应信息亭界面设计稿",
        "canvas": "1920×1080（16:10 设计稿纸）",
        "audience": "园区触摸屏信息亭的界面设计评审者",
        "scenario": "同一信息架构在三种屏宽下的呈现（设计提案稿）",
        "goal": "证明一套 Flex 结构在 1000/480/260 三档宽度均成立",
        "visual": "三台信息亭并列 + 注释卡片 + 主轴分布点阵对比 + 约束构件的像素标注",
        "basis": "鹭洲湿地公园触摸屏信息亭 V2 设计稿（虚构项目演示）；"
                 "磁贴内容取自 B02 规范数据",
        "technique": "Flex 弹性布局（Row/Column/Expanded/Flexible/Spacer + "
                     "SPACE_BETWEEN/AROUND/EVENLY + crossAxisAlignment=STRETCH）+ "
                     "AspectRatio / FractionallySizedBox / ConstrainedBox 约束构件",
        "criteria": [
            ("C05-1", "三种宽度布局全部成立且磁贴数随宽度变化",
             "met",
             "view-zoom：宽 1000 一行四磁贴 / 中 480 2×2 / 窄 260 纵排；"
             "pixel：各磁贴边界与 Column flex 分配（620-60-29-3×10=501）一致"),
            ("C05-2", "约束构件按标注渲染：AspectRatio/FSB/ConstrainedBox",
             "met",
             "pixel：AspectRatio 2.5 → 150×60；FSB .55×.6 → 橙块 121×36 居中；"
             "ConstrainedBox → 240×40（v02 修复：紧约束父级下 maxWidth 失效，改 Align 松约束父级，probe5 实证）"),
            ("C05-3", "主轴分布点阵对比可见：三种 SPACE_* 分布直观可辨",
             "met",
             "view-zoom：注释卡三点阵（BETWEEN/AROUND/EVENLY）间距差异清晰"),
            ("C05-4", "全部尺寸为像素浮点（服务端不接受百分比）",
             "met",
             "dsl：v01 的 width=\"100%\" 等 7 处 PARSE_ERROR 后全部改 px；"
             "dsl_check 矩阵/实体/标签换行复检 0 问题"),
        ],
        "rounds": "v01 渲染前拦截 7 处百分比尺寸；v02 修 ConstrainedBox 紧约束失效（probe5 实证）",
        "views": ["整图", "宽屏磁推行", "中屏 2×2", "窄屏纵排", "注释卡 A/B/C", "主轴点阵对比"],
    },
    "case-06": {
        "title": "活版印刷书展海报「活字」",
        "canvas": "1240×1754（A2 竖版）",
        "audience": "独立书店与阅读爱好者",
        "scenario": "独立书展现场张贴的复古印刷海报",
        "goal": "传递书展届次、主题、日期场地与讲座名单",
        "visual": "三层套印错版主标题 + 做旧纸纹 + 齿孔 + 套印十字标 + 衬线排版",
        "basis": "虚构「临州独立书展 · 第七回」（临州市图书馆场地为虚构信息）；"
                 "42 家书店名单与讲座信息为虚构演示内容",
        "technique": "Text STROKE 套印错版（青 +8 / 橙 +16 偏移）+ textShadow 压印 + "
                     "decoration 装饰线 + letterSpacing 字距 + height 行距 + 衬线排版；"
                     "纸纹/齿孔/十字标/晕墨全部用 DSL 图元构造",
        "criteria": [
            ("C06-1", "套印错版三层可辨：青边、橙边、墨黑实心",
             "met",
             "dsl：青 +8px STROKE 空心 + 橙 +16px STROKE 空心 + 墨黑实心 + 硬凹痕 shadow「3 3 0 #221E1A2E」；"
             "view-zoom：标题分区放大三层错版边缘清晰"),
            ("C06-2", "42 家书店三列全数入列无溢出",
             "met",
             "dsl：字号 13、行高 1.55（14 行 ≈282px）、盒高 290（1362–1644）；"
             "view-zoom：v02 修复后末两行不再压色条（v01 溢出约 61px）"),
            ("C06-3", "印刷语汇完整：纸纹/齿孔/十字标/做旧晕墨",
             "met",
             "dsl：36/44px 细线纸纹 + 齿孔圆 + 套印十字标 + RADIAL 晕墨三角；"
             "view-zoom：分区放大逐项核对在位"),
            ("C06-4", "讲座信息层级清晰：编号 + 主题 + 讲者",
             "met",
             "dsl：讲座编号壹贰叁肆 + OVERLINE 标签三列；view-zoom：信息栏分区可读"),
        ],
        "rounds": "v02 修书店名单第三列溢出（行高/盒高重算）",
        "views": ["整图", "套印主标题", "LIVE TYPE 区", "书店名单三列", "信息栏", "齿孔与纸纹", "底部印记"],
    },
    "case-07": {
        "title": "智能家居能量环中控屏",
        "canvas": "1600×1000（16:10 横屏墙装屏）",
        "audience": "家庭能源管理者（墙装中控屏旁观者）",
        "scenario": "客厅墙面常驻能源中控界面",
        "goal": "远距离一眼读取总功率与能源结构，近距离看房间分布",
        "visual": "能量进度环 + 刻度环 + 内环电量条 + 三能源卡 + 四房间条 + 流向条",
        "basis": "虚构产品「栖居 OS · 能源」中控界面；功耗数据为演示数据但内部自洽",
        "technique": "SWEEP 环形能量进度 + RADIAL 光晕 + 60 根矩阵旋转刻度 + ClipOval 环带嵌套",
        "criteria": [
            ("C07-1", "进度弧起止与渐变完全可控（SWEEP 语义不可控的替代方案）",
             "met",
             "dsl：47 根渐变色旋转条拼成 0–280.8° 弧（probe6/7 实证服务端 SWEEP 亮区恒从 12 点起、"
             "渐变反向映射、endAngle 非线性后放弃 SWEEP 做进度）；pixel：弧端角度与颜色逐根复核"),
            ("C07-2", "刻度环亮暗分界与进度一致",
             "met",
             "pixel：60 根刻度 47 亮/13 暗，分界 280.8°；游标菱形位于 (280°, r286)；"
             "v02 曾因 deg 误加 90° 致游标飞右上，已删"),
            ("C07-3", "能源数据自洽：来源合计 = 总功率 = 负载合计",
             "met",
             "calc：太阳能 1.2 + 储能放电 0.6 + 电网 0.6 = 2.4 kW；"
             "房间 0.86+0.52+0.31+0.71 = 2.40 kW；环心显示 2.4"),
            ("C07-4", "2px 级细条不被圆角吞没",
             "met",
             "dsl：短刻度 2px→3px（v02 修复：borderRadius 1.5 吞没 2px 条）；"
             "pixel：分区放大 3px 刻度清晰可数"),
        ],
        "rounds": "v01–v07 七版：助手误用修正 → SWEEP 标定放弃 → 旋转条拼弧 → 游标/刻度/采样半径修正",
        "views": ["整图", "进度环", "刻度环", "游标", "内环电量", "三能源卡", "四房间条", "流向条"],
    },
    "case-08": {
        "title": "儿童 App 启动页景深插画",
        "canvas": "1080×1920（9:16）",
        "audience": "3–8 岁儿童及其家长",
        "scenario": "自然认知 App 冷启动页",
        "goal": "2 秒内建立自然认知品牌印象并等待加载",
        "visual": "四层景深林间场景 + 雾带过渡 + 叶形徽标 + loading 三点",
        "basis": "虚构产品「叶子 · 自然认知」儿童自然认知 App 启动页",
        "technique": "ImageFiltered 分层景深（sigma 14/8/3/0 四层）+ Opacity 层间雾带 + "
                     "Stack 层次 + ClipPath 叶形徽标",
        "criteria": [
            ("C08-1", "四层景深虚化层次分明",
             "met",
             "dsl：blurred() 助手（children 包 Stack + ImageFiltered 全画布盒）sigma 14/8/3/0；"
             "view-zoom：远景柔散、中景渐清、近景锐利、前景叶完全清晰"),
            ("C08-2", "树冠不越画布（旋转/圆形包围盒核算）",
             "met",
             "dsl：树簇右界收进 1080（x ≤ 1075-1.95r，v01 曾 1215>1080）；"
             "pixel：分区实测最右树冠墨迹止于画布内"),
            ("C08-3", "前景叶旋转包围盒反解正确（28° 旋转不出画布）",
             "met",
             "dsl：300×460 旋 28° → 481×547 包围盒反解盒位；rotate 内手写 ClipPath inner；"
             "view-zoom：前景叶双叶完整压角不出画布"),
            ("C08-4", "徽标组件完整：白卡圆角 + 叶形 + 高光 + 投影",
             "met",
             "dsl：ClipRRect 白卡 + ClipPath 叶形 + 高光条 + boxShadow；view-zoom：徽标分区放大四要素齐全"),
        ],
        "rounds": "v01 修 ImageFiltered 多子级（包 Stack）、树冠越界、前景叶旋转包围盒",
        "views": ["整图", "远景林冠", "中景树干", "前景双叶", "雾带过渡", "徽标"],
    },
    "case-09": {
        "title": "杂志跨页破版特辑",
        "canvas": "1754×1240（√2 横版跨页）",
        "audience": "生活方式杂志读者",
        "scenario": "秋迁观鸟特辑跨页编辑设计",
        "goal": "以破版构图传达「人潮与候鸟同潮」的特辑主题",
        "visual": "跨栏出血主图 + 逐字破版标题 + 跨栏圆月 + 通栏色带 + 数据条 + 双栏正文",
        "basis": "虚构生活方式杂志特辑「追潮汐的人」；观鸟数据引用 B02 规范（287 种鸟等）",
        "technique": "ClipRect 硬边裁切出血 + SizedOverflowBox 破界 + Positioned 跨栏压图",
        "criteria": [
            ("C09-1", "标题逐字跨中缝，无压缩无丢失",
             "met",
             "dsl：170px SERIF 每字 185px，第 5 字 820–1010 越中缝 877 进入右页；"
             "（v01 SOB 内 Text 被盒压缩止于 714、「人」字丢失——重要边界：SOB 内 Text 不溢出）；"
             "view-zoom：中缝分区放大 5 字完整压缝线"),
            ("C09-2", "通栏色带跨中缝无断开",
             "met",
             "dsl：SOB 1700×50 横贯 40–1740；view-zoom：色带分区实测中缝处连续无断点"),
            ("C09-3", "ClipRect 出血主图六要素齐全",
             "met",
             "dsl：scene 包 Stack 后入 ClipRect（v01 多子级 PARSE_ERROR 修复）；"
             "view-zoom：天空/远山/湖面/波光/渔船/树/飞鸟全部在位"),
            ("C09-4", "跨页版式数据自洽：左右页分栏与页脚位置正确",
             "met",
             "calc：左页 40–877 / 右页 877–1714；正文两栏 + 竖排刊名 + 页脚右移避让跨栏字区；"
             "view-zoom：整图复核"),
        ],
        "rounds": "v02 修 ClipRect 多子级 + SOB 文字压缩（改逐字 Positioned 跨栏）",
        "views": ["整图", "中缝跨栏字", "跨栏圆月", "通栏色带", "出血主图", "数据条", "双栏正文"],
    },
    "case-10": {
        "title": "产品发布电子邀请函",
        "canvas": "1080×1080（1:1 方卡）",
        "audience": "受邀嘉宾（邮件/社交分发）",
        "scenario": "「秋迁观鸟季」启幕仪式电子邀请函",
        "goal": "一卡传递活动名、日期时间地点与 RSVP 入口",
        "visual": "夜蓝卡纸 + 双线金框 + 叶形徽标 + 92px 衬线主标题 + 渐变 RSVP 按钮",
        "basis": "虚构「秋迁观鸟季」启幕仪式邀请函；鹭洲湿地公园科普馆露台、"
                 "回复截止等均为虚构演示信息（日期 2026-11-20 周五经 datetime 实算）",
        "technique": "WidgetSpan 行内嵌件（日期徽章/序号徽章/菱形分隔）+ 嵌套 Span 混排"
                     "（SERIF/INTER 数字/金色强调）+ Noto Color Emoji + decoration 层级",
        "criteria": [
            ("C10-1", "WidgetSpan 行内嵌件与文本混排正确",
             "met",
             "dsl：三段 rich_text——圆形「4」徽章（30×30）行内居中对齐、日期徽章（56×56）、"
             "菱形分隔（10×10）；view-zoom：徽章分区放大，序号圆与文字行距协调；"
             "日期徽章 v02 缩至 56px 后圆-文中心错位从 19px 降至 10.5px"),
            ("C10-2", "嵌套 Span 颜色/字体混排可辨",
             "met",
             "dsl：GOLD SERIF 活动名 + ORANGE INTER 数字（287/1/16:00–17:30）；"
             "view-zoom：正文分区放大混排层级清晰"),
            ("C10-3", "Emoji 彩色渲染（Noto Color Emoji）",
             "met",
             "dsl：fontFamily=\"Noto Color Emoji\" + emoji 字符；"
             "pixel：🦢🍂🦆/🦆 三彩渲染实测（非单色字形）"),
            ("C10-4", "STROKE 空心副题 + UNDERLINE 组合正确",
             "met",
             "dsl：92px SERIF STROKE 1.8 + UNDERLINE 橙色；"
             "pixel：下划线实测 y466–470、x90–497 正落「启幕仪式」四字下方"),
        ],
        "rounds": "v01 修 textShadow 5 令牌 PARSE_ERROR + 日期徽章 72→56px；v02 定稿",
        "views": ["整图", "主标题区", "顶部 Emoji", "行内徽章", "日期徽章 v01/v02", "RSVP 区", "页眉"],
    },
}

FINAL_VER = {"case-01": "v01", "case-02": "v02", "case-03": "v02",
             "case-04": "v03", "case-05": "v02", "case-06": "v02",
             "case-07": "v07", "case-08": "v01", "case-09": "v02",
             "case-10": "v02"}
ALL_VER = {"case-01": ["v01", "v02"], "case-02": ["v01", "v02"],
           "case-03": ["v01", "v02"], "case-04": ["v01", "v02", "v03"],
           "case-05": ["v01", "v02"], "case-06": ["v01", "v02"],
           "case-07": ["v01", "v02", "v03", "v04", "v05", "v06", "v07"],
           "case-08": ["v01"], "case-09": ["v01", "v02"],
           "case-10": ["v01", "v02"]}

# 渲染记录中的最终成功请求（request_id 前缀/耗时/DSL 字节），交付时核验
LAST_OK = {"case-01": ("622a4062", 5.531, 96086),
           "case-02": ("161dc6c8", 5.812, 31960),
           "case-03": ("b492edb0", 4.422, 63837),
           "case-04": ("fb847e99", 3.531, 24110),
           "case-05": ("4adb21e0", 2.969, 24364),
           "case-06": ("0a33f455", 3.218, 33629),
           "case-07": ("f64ee132", 7.766, 151458),
           "case-08": ("4ac94d10", 10.703, 24592),
           "case-09": ("4b4d4b00", 3.204, 15952),
           "case-10": ("9c18a2b5", 8.453, 13722)}
