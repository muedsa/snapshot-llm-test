"""B01 作品计划：10 个独立用例的 case_id、受众、场景、内容范围、观看环境与完成标准。

计划是首次渲染前的承诺，不是终点。每条完成标准给出可观察条件与检查方法，
portfolio.json 逐条回填真实结果与证据。计划可修订，修订须追加保留旧/新标准、
理由、依据与生效版本，不倒填。

路径基准：suite_root（总任务根）。本文件写在 tmp/<run_id>/B01/。
"""
import datetime as dt
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
TMP = ROOT / "tmp" / RUN_ID / "B01"
TZ = dt.timezone(dt.timedelta(hours=8))
NOW = dt.datetime.now(TZ).replace(microsecond=0).isoformat(timespec="seconds")

# 两个版本的时间固定下来：plan.json 可重复生成，v1 的创建时间不能跟着漂。
V1_AT = "2026-10-21T21:26:19+08:00"
V2_AT = "2026-10-22T14:32:00+08:00"

CASES = [
    {
        "id": "case-01",
        "title": "急诊三十分钟 · 分诊降级倒计时",
        "audience": "急诊分诊护士与急诊组长",
        "use_context": "急诊大厅墙面显示屏，暗光、远距离、每 2 分钟扫一眼",
        "user_goal": "不用逐个问，一眼看出谁在接下来 30 分钟内会跨过更高等级",
        "content_basis": "自拟演示数据：14 名在院患者，ESI 1-5 分级、到院分钟、"
                         "降级触发条件。非真实病人、不宣称实际部署",
        "visual_intent": "把「还剩多久变严重」从表格变成一个环形倒计时刻度：弧长=剩余时间，"
                         "颜色=当前等级，弧末端指向危险区。整屏只有两个动作：读弧、读名字",
        "dimensions": [1920, 1080],
        "orientation": "landscape",
        "min_font_px": 18,
        "data_computed": "每患者剩余时间 = 到院分钟 + 观测时长 - 已等待分钟；"
                         "弧半径与剩余时间成反比由固定刻度表映射",
        "independence": "与其余用例无共享布局；独立的环形刻度系统",
    },
    {
        "id": "case-02",
        "title": "阳台七日 · 灌溉窗口与露点",
        "audience": "阳台党、都市家庭菜园丁",
        "use_context": "出门上班前在手机上 20 秒扫完，7 天后回头看",
        "user_goal": "决定今天几点浇水、明天要不要浇、哪几盆要挪到室内",
        "content_basis": "自拟演示数据：7 天预报（最高/最低温、露点、风速、降水概率）"
                         "+ 8 盆植物（耐旱性、盆径、朝向）。非真实气象数据",
        "visual_intent": "七日不是七张卡片，而是一条「浇水窗口带」：上下两条温度曲线之间"
                         "标出露点，只有「最低温低于露点」的日子才需要傍晚浇。"
                         "把判断规则画进图里，而不是只给结论",
        "dimensions": [1080, 1350],
        "orientation": "portrait",
        "min_font_px": 15,
        "data_computed": "浇水判据：Tmin < 露点 + 风速 > 12 km/h 需要浇；"
                         "每盆需水量 = 盆径^3 × 0.02 L，按 7 天分配到窗内日",
        "independence": "与 case-04 的天气用法不同（这里做决策规则可视化，不是路径图）",
    },
    {
        "id": "case-03",
        "title": "金杯 · 手冲咖啡克重时间螺旋",
        "audience": "家里有一台电子秤、想稳定复现同一杯的手冲爱好者",
        "use_context": "吧台上竖立的 A5 卡片，边冲边看，手是湿的所以字要大",
        "user_goal": "冲一杯 1:16 的咖啡时，知道现在该加到多少克、总共花了几秒",
        "content_basis": "自拟示例参数：15 g 粉、240 g 水、92°C、四段注水。"
                         "克重比是公开常识、时间分配为示例",
        "visual_intent": "用一条等距（阿基米德）螺旋把两个变量折进一条线：半径=累计克重、"
                         "转角=累计时间。比例对了螺旋就落在金色靶心上——"
                         "把「比例正确」变成一个几何事件（v2 修订，见 revision_log）",
        "dimensions": [1080, 1440],
        "orientation": "portrait",
        "min_font_px": 18,
        "data_computed": "r(m) = R_IN + (m ÷ M)·(R_OUT − R_IN)，"
                         "θ(t) = −π/2 + (t ÷ T)·2.4π；R_IN=42、R_OUT=264、M=240 g、T=240 s。"
                         "四段注水点由 (累计时间, 累计克重) 直接落在螺旋上；"
                         "每段速率 = 本段水量 ÷ 本段时长",
        "independence": "唯一使用极坐标的用例；螺旋几何由代码生成",
    },
    {
        "id": "case-04",
        "title": "雪线一日 · 山区徒步窗口预报",
        "audience": "带队向导与队伍成员",
        "use_context": "山门口集合时用大幅海报讲一次，之后队员拍照带走",
        "user_goal": "判断今天能不能上、哪段最危险、几点必须开始下撤",
        "content_basis": "自拟示例路线：海拔剖面 1820 m → 3140 m，8 段；"
                         "雪线 2400 m 起。非真实地形与真实预报",
        "visual_intent": "真实海拔剖面 + 一条斜切画面的「雪线带」。"
                         "危险不是标注出来的，是剖面穿进雪线带的几何事实",
        "dimensions": [1080, 1500],
        "orientation": "portrait",
        "min_font_px": 17,
        "data_computed": "剖面 9 个控制点线性插值成 120 段折线；"
                         "雪线带高度随时间线性下降（每小时 25 m）；"
                         "危险段 = 剖面高度 < 雪线高度的区间",
        "independence": "唯一以真实海拔尺度作纵轴的用例；剖面几何由代码生成",
    },
    {
        "id": "case-05",
        "title": "街区噪音 · 早八点与晚十点",
        "audience": "社区居民委员会与街道办",
        "use_context": "社区议事会会议室投影，讨论「施工时段该往哪挪」",
        "user_goal": "指出具体哪几条街区在哪个时段超标、搬施工时段能救下多少户",
        "content_basis": "自拟演示数据：12×8 街区网格，6 个声源（工地、物流、"
                         "夜市、地铁、学校、餐厅）。非真实监测值",
        "visual_intent": "同一张街区图画两次，左早右晚，声场用反距离衰减的等值圈"
                         "叠加出。差异一眼可读：哪片街区从绿变红就是施工时段挪走能救的",
        "dimensions": [1600, 900],
        "orientation": "landscape",
        "min_font_px": 16,
        "data_computed": "逐源衰减 Li(x) = L0i − 20·log10(max(d_i,10) ÷ 10)；"
                         "多源叠加按非相干声能相加 L(x) = 10·log10( Σ_active 10^(Li÷10) )，"
                         "不是 dB 线性相加（后者会得到约 200 dB 的非物理值）；"
                         "网格逐格求和后按 55/60/65 dB 分级；"
                         "两时段差值用于「可改善户数」统计",
        "independence": "唯一使用衰减场叠加的用例；双时相对比结构独此一件",
    },
    {
        "id": "case-06",
        "title": "疫苗年纪梯 · 一张贴在冰箱上的到龄表",
        "audience": "学龄前孩子的家长，以及儿童保健门诊候诊区",
        "use_context": "A4 打印贴在冰箱上；门诊候诊区墙贴放大版",
        "user_goal": "一眼看出孩子接下来 12 个月该打什么、已经打过的不用再查",
        "content_basis": "自拟示意排期，按常见免疫规划年份结构编排但已标注为示意，"
                         "不作为医疗建议；不宣称与实际免疫规划一致",
        "visual_intent": "纵向「年龄梯」：每年一级台阶，疫苗是挂在台阶上的旗。"
                         "孩子已完成的旗点亮，未来 12 个月的旗子放大并标日期。"
                         "整张图没有表格线",
        "dimensions": [1200, 1697],
        "orientation": "portrait",
        "min_font_px": 19,
        "data_computed": "7 级台阶按年份等距；每旗子 y = 台阶高度 - 序号×18 px；"
                         "未来 12 个月 = 今天 + 0..365 天落在排期区间内的项",
        "independence": "唯一面向纸质打印与低认知负担场景的用例",
    },
    {
        "id": "case-07",
        "title": "自检印张 · 印刷车间的印刷质量校样页",
        "audience": "印厂印前与开机操作员",
        "use_context": "A3 打印贴在机台上，开机前对一次、每两小时复对一次",
        "user_goal": "在不打开电脑的情况下判断这台机器的灰度、套色和网点是否达标",
        "content_basis": "自拟校样内容：10 级灰阶、12 色块、5 种网点、"
                         "套色十字标记与文字可辨识度区",
        "visual_intent": "这一张的炫酷在于它自己就是被校的对象——"
                         "它用印出来的灰阶和网点告诉你印刷本身对不对。"
                         "把「校样」做成一次自我指涉的检查",
        "dimensions": [1600, 1200],
        "orientation": "landscape",
        "min_font_px": 17,
        "data_computed": "灰阶 10 级按 L=94→6 线性；色块 12 个来自同一套经过色盲校验的"
                         "调色板；网点 5 种按 12/25/37.5/50/62.5% 密度手工排点",
        "independence": "唯一自我指涉的校样页；网点由程序逐点排布",
    },
    {
        "id": "case-08",
        "title": "补给带 · 山地马拉松每站物资配置单",
        "audience": "赛事后勤志愿者与补给站站长",
        "use_context": "凌晨 5 点在帐篷里对着打印单发物资，光差、要快",
        "user_goal": "在 3 分钟内知道自己这站该发多少瓶、多少根香蕉、多少卷绷带",
        "content_basis": "自拟示例赛事：62 km 山地赛、1400 名完赛、5 个补给站。"
                         "消耗系数为常见运营经验值，已标注为示例",
        "visual_intent": "一条真实的赛道丝带（按累计距离与爬升折成曲线），"
                         "补给站是丝带上竖起的旗。每站下方不是数字表，"
                         "而是一个按瓶数排开的瓶阵——数量本身就是图形",
        "dimensions": [1750, 1120],
        "orientation": "landscape",
        "min_font_px": 18,
        "data_computed": "每站人数 = 1400 × 该站通过比例；"
                         "瓶装 = 人数 × 0.85 瓶/人；香蕉根 = 人数 × 0.4；"
                         "瓶阵每行 20 瓶，行数 = ceil(瓶数/20)",
        "independence": "唯一用「数量排布即图形」的用例；赛道丝带几何由爬升生成",
    },
    {
        "id": "case-09",
        "title": "七天药格 · 低视力长者的用药塔",
        "audience": "75 岁以上、低视力、需要长期服药的住户",
        "use_context": "老年公寓居室冰箱门，白天光线一般，看的人戴老花镜",
        "user_goal": "早上起来不看说明书、不打电话，就知道今天早中晚各吃哪几颗",
        "content_basis": "自拟示例用药：7 种药，7 天排期。明确标注为示例，"
                         "不含真实药品名与剂量建议",
        "visual_intent": "这是整套里最不炫的一张，也是最难的一张。"
                         "炫的地方是「让一个看不清的人不需要思考」："
                         "超大符号、只有一种强调色、每天一格、"
                         "每格最多三行字。可读性就是视觉语言",
        "dimensions": [1080, 1620],
        "orientation": "portrait",
        "min_font_px": 26,
        "data_computed": "7 天 × 3 餐网格，格高 = 1560/21 ≈ 74 px；"
                         "药名字号按 26 px 下限，对比度按 WCAG AA 4.5:1 手工校验",
        "independence": "唯一以无障碍为首要目标的用例；字号与对比度是唯一约束",
    },
    {
        "id": "case-10",
        "title": "静默带 · 播客节目节奏与死空气诊断",
        "audience": "两人播客的剪辑与制作",
        "use_context": "剪辑软件旁边开一张对照图，发布前过一遍",
        "user_goal": "找出哪几分钟太静、哪几分钟两个人同时说话，直接跳到那儿修",
        "content_basis": "自拟示例：一集 42 分钟双人访谈，按 5 分钟分段统计"
                         "说话占比、重叠占比、死空气时长。非真实节目",
        "visual_intent": "不用波形——波形在剪辑软件里已经能看到了。"
                         "画一条「静默带」：每段的高度是死空气秒数，"
                         "颜色是重叠占比。让剪辑者看到剪软件里看不到的形状",
        "dimensions": [1920, 1080],
        "orientation": "landscape",
        "min_font_px": 18,
        "data_computed": "9 段 × 5 分钟；死空气 = 段时长 - 说话时长；"
                         "带高按 0-150 s 映射到 0-260 px；"
                         "重叠占比按 0-30% 映射到四档颜色",
        "independence": "唯一针对音频元数据的用例；不用波形是最核心的视觉选择",
    },
]

PLAN = {
    "schema_version": 1,
    "plan_version": "v6",
    "created_at": V1_AT,
    "regenerated_at": NOW,
    "timezone": "Asia/Shanghai (UTC+08:00)",
    "task_id": "B01",
    "run_id": RUN_ID,
    "path_base": "suite_root",
    "brand": "折光 · 十张日常",
    "brand_note": "自拟作品集品牌名，用于作品集封面与逐件署名；不是实际客户",
    "curatorial_statement": "十件用例各自来自一个真实的工作现场：急诊墙、阳台、吧台、"
                            "山门口、议事会、冰箱、印台、帐篷、老年居室、剪辑台。"
                            "共同点是每张都在替某个人省掉一次思考——"
                            "判断规则被画进图里、数量被排成图形、危险被几何表达出来，"
                            "而不是靠读者自己算。炫的地方各不相同："
                            "降级倒计时用环形刻度、灌溉规则用窗口带、咖啡比例用等距螺旋、"
                            "雪线用斜切带、噪音用反距离衰减场、疫苗用年龄梯、"
                            "校样页自我指涉、补给用瓶阵、药格用极端可读性、"
                            "播客用静默带。",
    "asset_policy": "dsl_only 实际执行（run-config 允许 dsl_primary_with_supporting_assets，"
                    "但本套十件全部由 DSL 构造，不使用外部素材，"
                    "因此不产生 asset-sources.json）",
    "shared_conventions": {
        "font": "Noto Sans CJK SC,Inter（逗号后无空格）",
        "color_syntax": "仅 #RRGGBB / #RRGGBBAA；透明用 8 位带 A",
        "text_height": "1.0（行高倍数，不是像素）",
        "text_layout": "全部文字用左锚点 x + 本地宽度估算（CJK 1em / ASCII 0.56em / "
                       "空格 0.3em）；居中与右对齐由 tw() 反推 x",
        "line_pitch": "fs × 1.2",
        "no_overflow_reliance": "尺寸全部算术算出，不依赖 overflow 裁切",
        "colorblind": "每个用例的类别色对经过色盲可分性自检（deutan / tritan ΔE），"
                      "warning 与 danger 一律带文字标签",
        "rendering": "真实服务 POST /snapshot；PNG 保留服务原始字节，不做后处理",
        "dry_run": "每次渲染前跑门禁：画布内、同层不重叠、字号下限、"
                   "以及每件的专项几何断言；失败即拒绝渲染",
    },
    "independence_note": "十件用例的受众、观看环境、尺寸朝向、视觉系统两两不同；"
                         "没有同版式换色、简单缩放裁切或局部放大。"
                         "共享的只有字体、颜色语法与文字排版规则——这些是技术约定不是视觉复述",
    "data_disclosure": "全部数据为自拟演示数据，每件 case.md 与本计划的 content_basis "
                       "都标明；不宣称真实客户、真实部署或真实监测值",
    "cases": CASES,
    "completion_criteria_common": [
        {"id": "G-01", "condition": "final.png 的 IHDR 尺寸等于 case 声明的 dimensions",
         "method": "读 PNG 头 13-20 字节的宽高字段"},
        {"id": "G-02", "condition": "final.png 字节等于服务 200 响应的原始字节",
         "method": "sha256(final.png) == sha256(tmp 下同名响应)"},
        {"id": "G-03", "condition": "final.snapshot 可被当前构建器重建（换行归一化后逐字节一致）",
         "method": "规范化 CRLF→LF 后与 doc.build() 的 UTF-8 编码哈希比对"},
        {"id": "G-04", "condition": "正文字号不低于 case 声明的 min_font_px",
         "method": "遍历 doc.texts 取 min(fs)"},
        {"id": "G-05", "condition": "所有文字与矩形在画布内、同层不相互重叠",
         "method": "干跑门禁 hit() 两两检测"},
        {"id": "G-06", "condition": "图上标注的数值与 case.md 声明的数据源算术一致",
         "method": "从 schedule/data 文件复算，不靠目测"},
        {"id": "G-07", "condition": "受众与使用场景、用户目标、内容来源在 case.md 中写明，"
                                   "且自拟数据明确标注为演示",
         "method": "文本核对"},
        {"id": "G-08", "condition": "最终 PNG 实际打开看过，记录了看到的层级、对齐、"
                                   "可读性、遮挡与裁剪",
         "method": "viewing-evidence 记录实际观察文本"},
    ],
    "revision_log": [
        {"version": "v1", "at": V1_AT,
         "note": "首次渲染前的原始计划，未修订。v1 原文另存 plan-v1.json"},
        {"version": "v2", "at": V2_AT, "scope": "case-03",
         "effective_version": "v2",
         "old": ("case-03.data_computed = "
                 "\"r(θ) = r0·e^(bθ)，四段注水点按累计克重反解 θ\"；"
                 "case-03.visual_intent = \"用一条对数螺旋…\""),
         "new": ("改等距（阿基米德）螺旋：r(m) = R_IN + (m ÷ M)·(R_OUT − R_IN)，"
                 "θ(t) = −π/2 + (t ÷ T)·2.4π；R_IN=42、R_OUT=264、M=240 g、"
                 "T=240 s。四段注水点由 (累计时间, 累计克重) 直接落在螺旋上，"
                 "半径即克重刻度、外圈 264 仍是 240 g 金标"),
         "reason": ("对数半径 r(θ)=r0·e^(bθ) 的圈间距随 θ 指数放大，把中段"
                    "（闷蒸到第一段之间，0:45 前后）压到几乎重叠，而那段正是节奏"
                    "最要紧、最容易做错的注水段；同时克重刻度失去可反读性，"
                    "「落在金标靶心」这个几何事件仍成立却变得不可校验。"
                    "等距半径让半径与累计克重成正比，螺旋上任一点都能直接反读克重"),
         "evidence": ("门禁 case-03-c07 断言半径映射单调且 r(0)=42、r(240)=264；"
                      "case-03-c09 断言采样端点落在金标半径上与节点 4 重合；"
                      "case-03-c01 / -c02 断言四段水量与时间合计仍为 240 g / 240 s；"
                      "门禁文件 case-03/case-03-gates-005.json 记录 19 条全部通过"),
         "unchanged": ("其余 9 件用例的计划、全部通用标准 G-01..G-08、"
                       "各件受众/使用目标/内容范围/目标观看环境与完成标准均未改动；"
                       "不回填 v1 文本")},
        {"version": "v3", "at": "2026-10-22T15:44:00+08:00",
         "scope": "all cases（仅门禁编号命名约定，不涉及计划内容）",
         "effective_version": "v3",
         "note": ("干跑门禁 dry_run() 产出的编号是 case-NN-01..-06（画布内、同层不重叠、"
                  "字号下限、片段预算、形状越界、无 < > &），与各件自定义门禁"
                  "case-NN-01.. 的编号在同一轮次文件里撞号，导致同一条目 ID 出现两次、"
                  "阅读门禁 JSON 时无法区分是哪一条。约定改为：自定义门禁用 -cNN 命名空间"
                  "（case-NN-c01..），dry_run 保持 -01..-06，色盲校验保持 -cbr。"),
         "effect": ("case-03 与 case-04 的门禁已按新约定落盘"
                    "（case-03-gates-005.json、case-04-gates-003.json）。"
                    "case-01 与 case-02 的历史门禁 JSON 保持原样不改写"
                    "（失败与旧版尝试记录一律不覆盖）；这两件 case.md 中出现的"
                    "case-01-NN / case-02-NN 是当时同一编号下两条门禁的合并记法，"
                    "阅读时按 check 文本区分专项门禁与干跑门禁。"),
         "evidence": ("case-03/case-03-gates-005.json 19 条 ID 无重复；"
                      "case-04/case-04-gates-003.json 21 条 ID 无重复")},
        {"version": "v4", "at": "2026-10-22T16:40:00+08:00",
         "scope": "case-05",
         "effective_version": "v4",
         "old": ("case-05.data_computed = "
                 "\"L(x) = Σ L0i - 20·log10(d/10)；网格逐格求和后按 55/60/65 dB 分级；"
                 "两时段差值用于「可改善户数」统计\""),
         "new": ("逐源先算 Li(x) = L0i − 20·log10(max(d_i,10) ÷ 10)，"
                 "多源叠加改为非相干声能相加 "
                 "L(x) = 10·log10( Σ_active 10^(Li÷10) )，再按 55/60/65 dB 分级。"
                 "求和符号 Σ 的含义从「dB 相加」更正为「线性声能相加」"),
         "reason": ("声压级是 log 标度，不能直接相加。把 6 个 80-88 dB 的源做 dB "
                    "线性求和会得到约 500 dB 的荒谬结果；即使只加两三个源，"
                    "线性相加也比正确的能量相加每多加一个同强度源多算 10 dB 左右"
                    "（正确值只多 3 dB）。这会同时夸大超标范围和分级的可靠性，"
                    "而分级正是这件作品要拿去开议事会的依据。"
                    "写公式时 Σ 前没有写 log10，容易被读成线性相加，"
                    "属于计划里的实际缺陷，不是措辞偏好"),
         "evidence": ("b01_case05.py 的 src_level() 实现 "
                      "10·log10(Σ 10^(Li/10))，门禁 case-05-c02 用"
                      "「等强度源每多一个多 3 dB」的解析性质做独立校验："
                      "assert abs(L(3 个 80 dB 源) − (80 + 10·log10(3))) < 1e-6，"
                      "并与线性相加结果对比确认二者不同"),
         "unchanged": ("其余 9 件用例的计划、全部通用标准 G-01..G-08、"
                       "case-05 的受众/使用场景/用户目标/内容范围/尺寸/字号与"
                       "独立性声明均未改动；不回填 v1、v2、v3 文本")},
        {"version": "v5", "at": "2026-10-22T17:05:00+08:00",
         "scope": "case-05（记录更正，无任何完成标准变更）",
         "effective_version": "v5",
         "note": ("两项更正，都不涉及完成标准本身：\n"
                  "① v4 的 evidence 字段把「非相干能量相加」的独立校验误指到"
                  "门禁 case-05-c05。case-05-c05 实际断言的是四档分级边界单调，"
                  "能量相加校验在 case-05-c02（3 个 80 dB 源 = 80 + 10·log10(3) = 84.77 dB，"
                  "线性相加 240 dB 被拒绝，差 155.2 dB）。已把 v4 的引用更正为 -c02，"
                  "不删除 v4 条目。\n"
                  "② case-05 首版渲染后按 G-08 实际看图，发现两个视觉缺陷并在第二版修复："
                  "65 dB 环线原先画在格值文字之上，横切笔画使 66 / 67 在投影距离下被读作 65，"
                  "已把环线移到格值文字之下并新增门禁 case-05-c15 断言绘制顺序；"
                  "图例文字「65 dB 为夜间限值（示意）」是对法规的错误陈述"
                  "（65 dB 是 GB 3096-2008 中 3 类声环境区的昼间限值，不是任何区的夜间限值），"
                  "已改为「示例阈值统一取 ≥65 dB，非实际限值」。"),
         "evidence": ("门禁文件 case-05/case-05-gates-002.json 记录 -c02 与 -c05 两条"
                      "各自的 check 文本，可核对二者分工；"
                      "case-05-gates-005.json 记录第二版 22 条门禁全部通过（含新增 -c15）；"
                      "第二版渲染 req-b01-case-05-street-noise-* 的 final.png 中环线"
                      "在数字下方，66 / 67 无笔画被切"),
         "unchanged": ("十件用例的计划、全部通用标准 G-01..G-08、case-05 的"
                       "受众/使用场景/用户目标/内容范围/尺寸/字号/独立性声明、"
                       "以及 case-05 的全部完成标准均未改动；声场计算、分级阈值、"
                       "网格几何与户数统计零改动；不回填 v1、v2、v3、v4 文本")},
        {"version": "v6", "at": "2026-10-22T21:30:00+08:00",
         "scope": "case-05（环线画法：打断→遮罩）",
         "effective_version": "v6",
         "note": ("第六版把 65 dB 影响半径环线的画法从「按数字框角度段打断」"
                  "改为「画整圈 + 数字遮罩」，并记录 v1→v6 六次看图各查出的真实缺陷：\n"
                  "① 首版环线画在格值文字之上，横切笔画使 66 / 67 在投影距离下被读作 65；\n"
                  "② 环线芯 #5C3D18 对格值文字色 #2A2014 的对比只有 1.62:1，"
                  "环线压到数字时线与字同色（审计：学校环线 336 个采样点中 335 个与文字同色）；\n"
                  "③ 衬底比芯宽 3.5 px，只断芯不断衬底时衬底仍探到数字框外沿，"
                  "衬底色 #FFF6E8 对 CL3 白色数字 #FFFFFF 的对比只有 1.07:1，白字丢边；\n"
                  "④ 数字框一直用 K.pitch(16)=19.2 px 的行高，比 Noto Sans 实测墨迹高 7.2 px"
                  "（b01_case05_glyph_probe.py 量 192 个格值，墨迹 17×12 px、"
                  "墨心在行高框中心上方 2.5 px），环线被多打断一圈——"
                  "学校环线只剩 35% 圆周、分成 4 段短括弧，读不出是影响半径；\n"
                  "⑤ 即便用实测墨迹框收紧断口，打断的环仍只剩 47% 圆周（夜市 R=38 px 最窄，"
                  "12% 一段），4 段短括弧在投影距离下读不出是 65 dB 影响半径。\n"
                  "根因：声源在格子角落（路口），相邻 4 个格中心距声源 0.5×CELL×√2=36.4 px；"
                  "R < 36.4 px 时环线落在 4 个数字框内部，每框挡约 48°，打断后只剩 4 段短笔头。\n"
                  "第六版修法：环线画整圈 0→2π 不打断，数字底下压一块与格子底色同色的遮罩"
                  "（INK_W×INK_H 墨迹框外扩 MASK_PAD=HALO_OUT+1=2.75 px），"
                  "把环在数字底下的部分盖住而不是删掉——环是连续圆，遮罩只是把数字底下的环盖住，"
                  "读者看到的是带小凹口的完整圆而不是散落的笔头；"
                  "遮罩比第四版按衬底半带宽打断时少挡 GAP_PAD+half−MASK_PAD=2.75 px。"
                  "单一颜色无法满足「对 CL3 底 ≥3.0 且对白字 ≥3.0」（需要亮度既 ≥0.343 又 ≤0.300），"
                  "所以衬底与芯两层都在。门禁 c15 加断遮罩层夹在环线与格值之间，"
                  "c16 改为断言遮罩外扩 ≥ 衬底外沿且 192 块遮罩盖住全部靠框环带采样点，"
                  "c17 改为断言每源一整圈连续环（衬底与芯各一段 0→2π，芯径向落在衬底带内）。"),
         "evidence": ("门禁文件 case-05/case-05-gates-019.json 记录第六版 24 条门禁全部通过"
                      "（含新增遮罩层序 c15、遮罩覆盖 c16、连续整圈 c17）；"
                      "b01_case05_glyph_probe.py 实测 192 个格值字形墨迹 17×12 px、"
                      "墨心偏移 INK_DY=-2.5 px，与 b01_case05.py 的 INK_W/INK_H/INK_DY 一致；"
                      "b01_case05_ring_audit.py 第四版审计查出衬底探到数字框外沿的具体像素数，"
                      "第五版审计查出打断后最窄环只剩 47% 圆周、4 段短括弧"),
         "unchanged": ("十件用例的计划、全部通用标准 G-01..G-08、case-05 的"
                       "受众/使用场景/用户目标/内容范围/尺寸/字号/独立性声明、"
                       "以及 case-05 的全部完成标准均未改动；声场计算、分级阈值、"
                       "网格几何与户数统计零改动；不回填 v1、v2、v3、v4、v5 文本")},
    ],
}


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    TMP.mkdir(parents=True, exist_ok=True)
    (TMP / "plan.json").write_text(
        json.dumps(PLAN, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("plan.json  %s  %d 件用例  通用标准 %d 条  created_at=%s  "
          "修订 %d 次"
          % (PLAN["plan_version"], len(CASES),
             len(PLAN["completion_criteria_common"]), PLAN["created_at"],
             len(PLAN["revision_log"])))
    for c in CASES:
        print("  %-8s %4d×%-5d %s" % (c["id"], c["dimensions"][0], c["dimensions"][1],
                                       c["title"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
