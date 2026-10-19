# -*- coding: utf-8 -*-
"""B06 收尾文档落盘：case.md×10 + portfolio(json/md) + gallery.md +
snapshot-usage.md + task-metrics.json + problem-evidence.json +
design-review.md + iterations.jsonl + tool-usage.jsonl。
全部路径相对（path_base=suite_root 或本题输出根）；不改写 tasks/。"""
import io
import json
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"D:\mine\test\glm-5.3-flash")
RUN = "20261016T164020-m1"
TMP = ROOT / "tmp" / RUN / "B06"
OUT = ROOT / "outputs" / RUN / "B06"
NOW = datetime.now().astimezone().isoformat(timespec="milliseconds")
TASK_START = "2026-10-18T20:45:48+08:00"  # B05 套件收尾（20:45:47.730）后紧接开始 B06

req_rows = [json.loads(ln) for ln in
            (TMP / "requests.jsonl").read_text(encoding="utf-8").strip().splitlines()]


def reqs_of(case_id):
    lines = []
    for r in req_rows:
        if ("b06-" + case_id + "-") in r.get("request_file", ""):
            tag = r["request_file"].replace("\\", "/").split("/")[-1].rsplit("-", 1)[0]
            lines.append("%s（%s，HTTP %d，%s ms）" % (r["id"], tag, r["http_status"],
                                                     round(r["duration_ms"])))
    return "；".join(lines)


REQ_BY_CASE = {("case-%02d" % i): reqs_of("case-%02d" % i) for i in range(1, 11)}

PLAN_REF = "tmp/20261016T164020-m1/B06/plan-v1.md（v1 + v1.1 追记，建立于首次渲染前）"
CALCS_REF = "tmp/20261016T164020-m1/B06/research/calcs.json"

CASES = [
    dict(
        id="case-01", v=3, size="800×1100", medium="A4 近比贴墙卡",
        device="梳妆台/冰箱贴 · 印刷或屏读",
        pain="「6M/12M」开罐符号几乎没人会读；开封后保质期被整体忽略，物品用到「看起来没坏」为止",
        stage="刷卡护肤、开罐食品时人工翻标太麻烦 → 一张贴纸卡解决『开封后还能用多久』",
        audience="摆放瓶罐的成年人（自己家里）",
        goal="看懂开罐符号语义、动手写开封日、把开封期与未开封保质期分开",
        content=[
            "主问句：开封之后，还能用多久？副句「化妆与食品的『开罐寿命』，一次读懂，顺手记录」",
            "语法卡：开罐符号 = 开封后月数；印在罐底的 6M / 12M / 24M",
            "常见开封期（演示口径）：6M 防晒霜·隔离霜·眼线液 / 12M 面霜·精华（多数）/ 24M 洗发水·沐浴露",
            "提示行：乳制品开盖另算——多数 24 小时内喝完",
            "行动区：自己写一道「开封日」+ 日期空栏「____ 年 __ 月 __ 日」+ 示例带「今天开封 → 12 个月后到期」",
            "区分卡：开封期 ≠ 保质期（未开封印到 2027-07-02 为止；开封期从开盖之日起按月数计）",
            "三个写日期的技巧：油性笔写瓶底 / 相册拍瓶身存档 / 纸胶带贴盖沿",
            "页脚：PAO 符号依行业通用惯例自绘示意 · 食品以包装说明为准 · 演示数据 · 虚构示例",
        ],
        claims=[
            "开罐符号（开盖罐身+月数）为护肤品行业通用的 PAO 记号，本图为依惯例自绘示意，非官方矢量复制",
            "6M/12M/24M 常见类目为演示口径；乳制品开盖时限为提示性常识",
            "示例未开封日期 2027-07-02 为虚构",
        ],
        standards=[("S1a", "符号（开罐+月数）自绘可读且与惯例一致", "整幅 + zoom-case-01-a：开盖罐符号与 12M 双要素齐备"),
                   ("S1b", "含「写开封日」位置与开封→到期时间带", "整幅观察：日期空栏 + 「今天开封→12 个月后到期」示例带"),
                   ("S1c", "明示「开封期≠保质期」", "区分卡两段对照 + 页脚声明；zoom-case-01-b 放大复核")],
        visual="白纸感贴墙卡；「写日期」行动区给实署空栏与示例带同级排版，鼓励填写而非只读；按钮/表单感弱化为填写槽",
        selfcheck="v1 版式崩坏（语法误记）→ v3 格式重渲后整幅通过；c01 无逐条小修，v3 即终版",
        basis="符号语义为行业惯例复述；类目月数为演示口径——两者均在图内注明「示意/演示」",
    ),
    dict(
        id="case-02", v=5, size="720×1280", medium="手机长图（群聊/收藏）",
        device="分期比价时随手转发",
        pain="月手续费率 0.6% 听起来是年利率 7.2%；实际资金占用逐月减少，真实年化接近 14%",
        stage="被「每期只要 1,072」打动前，先看清手续费收进来的真实成本",
        audience="正在比较分期与全款的普通消费者",
        goal="算出「名义 7.2% vs 实际 ≈13.8%」差多少，并把三问自查卡带走",
        content=[
            "主标题：你以为的 7.2%，实际约 13.8%",
            "A 区·还款结构：12,000 元 · 12 期 · 每期手续费 72 元（每期共还 1,072）；余额蓝柱逐月下降 12,000→1,000，珊瑚帽=固定 72 元/期手续费（不随余额下降）",
            "口径行：手续费 72×12 = 864 元；平均每月实际占用本金不到一半；0.6%×12 期 → 名义年化 7.2%",
            "B 区·两个年化：你以为的 7.2%（0.6%×12，按全款口径）↔ 借款人实际付出的 13.8%（月 IRR 1.09% 复利年化，监管披露口径）；实际成本 ≈ 名义的 1.9 倍",
            "C 区·分期前三问：「免息」真免息？/ 提前还款手续费退不退？/ 「日息万五」≈ 年化 18~20%",
            "页脚口径：等额「本金+固定手续费」分期 · 名义 7.2% · 实际≈月 IRR 1.0862% 复利 13.84% · 示例虚构",
        ],
        claims=[
            "IRR 1.0862%/月、复利年化 13.84%（单利折算 13.03%）为本地二分法精确解，见 " + CALCS_REF + " 的 c02",
            "名义 7.2% = 0.6%×12，按全程占用 1.2 万本金的手续费口径（plan v1.1.3 补充）",
            "数据 12,000 / 72 / 864 / 1,072 自洽；三问卡与「日息万五≈18~20%」换算为演示表述",
        ],
        standards=[("S2a", "名义 7.2% 与实测 IRR 并列且口径差异点到明", "B 区双栏并列 + 「实际成本≈名义 1.9 倍」胶囊；zoom-case-02-b"),
                   ("S2b", "每期流水（本金+手续费）可视化", "12 栏余额柱 + 珊瑚帽；zoom-case-02-a（12,000→1,000 逐月、第 1/12 期标签）"),
                   ("S2c", "计算口径声明", "页脚口径行逐字核对（v5 为更短一行版式）")],
        visual="双坡对照（A 明账本金下降 × B 口径差距）分三幕推进；余额柱+手续费帽把「利率错觉」画成几何差",
        selfcheck="v1 版式崩坏；v3 通过例行看图后页脚整行压底边 → v4 三问与页脚下移；v4 页脚句过长 → v5 改为一行更短文案并复看确认",
        basis="分期结构为常见演示口径；IRR 为本地精确计算并图内标注（非营销数据）",
    ),
    dict(
        id="case-03", v=3, size="800×1100", medium="A4 近比贴墙卡",
        device="厨房/走廊 · 算电费时对照",
        pain="阶梯电价三档只见数字；账单看不出身处哪一档、跨档月怎么算、直觉按「单价×用电」会错多少",
        stage="收到电费单，想知道 480 度这个月为什么比平时贵",
        audience="替家人算电费的子女/租客",
        goal="用蓄水池剖面读懂三档边界，并把跨档月拆段算清楚",
        content=[
            "标题：电费单上的三档阶梯，你在哪一档？副句提示夏天可能一个月内连跨两层",
            "剖面带：一档 0.52 / 二档 0.57 / 三档 0.82 元/度（超出 4,800 部分）；轴标 0 / 2,760 / 4,800 / 年累计（度）",
            "水位注线：本月末累计 3,180 度（虚线）落在二档；跨档警告线随水位标注",
            "跨档月算例卡：上月末累计 2,700 度 → 本月 480 度拆两段：一档 60 度×0.52=31.20 元、二档 420 度×0.57=239.40 元、合计 270.60 元",
            "对照卡：直觉 480×0.52=249.6 元（错）→ 多付 21.0 元（+8.4%）",
            "解释/使用卡：2,700 已近一档上限 2,760——本月仅 60 度仍按一档；年内回不去下层；用法=看「年累计」栏预判跨档",
            "页脚：档位/电价为演示口径；各地阶梯与结算周期不同，分时电价另算 · 演示数据",
        ],
        claims=[
            "2,760/4,800 度边界与 0.52/0.57/0.82 元/度为自拟演示省份口径（图内标注，非省级文件）",
            "算例链 31.20+239.40=270.60、直觉 249.60、差额 21.00（+8.4%）全部与 " + CALCS_REF + " 的 c03 一致",
            "水位 3,180=2,700+480 几何映射与算例同比例尺",
        ],
        standards=[("S3a", "三档边界与电价标注", "剖面带三层 + 轴标 0/2,760/4,800；zoom-case-03-a"),
                   ("S3b", "跨档月分拆两段逐段算式", "算例卡两段行 + 合计 270.60；zoom-case-03-b"),
                   ("S3c", "与「定额认知」对照", "直觉 249.6（错）vs 270.60，多付 21.0（+8.4%）")],
        visual="蓄水池剖面隐喻：档位=池层、累计电量=水位；跨档=水位跨过池界，价格随层递进一眼可见",
        selfcheck="v1 版式崩坏；v3 整幅通过（右上算例卡贴近右缘约 1–2px 为有意轻贴，放大复核可接受）即终版",
        basis="三档参数为演示口径；计算由本地脚本完成并图内复核",
    ),
    dict(
        id="case-04", v=4, size="1180×820", medium="平板横排",
        device="体检报告在手、桌面并排复核",
        pain="体检报告一片箭头；偏差多大可忽略、多小该复查没人说，更没人提示「箭头≠疾病」",
        stage="拿到四项常见指标，想知道每条「离线多远」再决定下一步",
        audience="拿到报告的上班族（自查/与家人讨论）",
        goal="按刻度尺读出每项落在哪一段，并取到对应的下一步建议（记录/复测/复查）",
        content=[
            "标题：体检报告的箭头，怎么会读；副句：参考范围内约 95% 健康人；轻微超出未必是病，箭头不等于诊断",
            "状态图例：正常 / 边缘 / 超限（三段色语，每条刻度尺沿用）",
            "四条跑道刻度尺（虚构示例值 + 通用参考区间）：收缩压 128（正常高值·90.0–160.0 轴）；空腹血糖 5.6（贴近上沿·2.5–10.5 轴）；血尿酸（男）452（超上限约 5.6%·150.0–550.0 轴）；低密度脂 3.42（刚过 3.4 线 0.02·1.0–5.5 轴）",
            "每条行动注：128 先记录一周晨起复测 / 5.6 控制精米精面明年再比上年 / 452 先减啤酒内脏两周后复查 / 3.42 三个月后复测再谈",
            "用法行：箭头先量「离线多远」——贴近边界先记录再复查，比直接焦虑有用",
            "页脚：示例值为虚构演示；区间为通用参考（各实验室略有差异）；不构成医疗建议 · 演示数据",
        ],
        claims=[
            "四条尺轴端点与区间带为通用参考值演示（图内注明各实验室略有差异）",
            "示例值 128 / 5.6 / 452 / 3.42 虚构；「452 超上限约 5.6%」与图上口径自洽（隐含上界 ≈428，452/(1+5.6%)≈428）；「3.42 刚过 3.4 线 0.02」",
            "全部为读数训练示例，图内声明不构成医疗建议",
        ],
        standards=[("S4a", "四条区间带含数值轴与示例点针", "zoom-case-04-a/b：指针数值标注于带上方，轴端 90–160 / 2.5–10.5 / 150–550 / 1.0–5.5"),
                   ("S4b", "三种状态间垫变化边界", "四条尺同用三段色标；放大复核针头未遮字（v4 把色带文字改到采样竖线之后绘制）"),
                   ("S4c", "「箭头≠疾病」边界声明", "副句与页脚两处声明")],
        visual="跑道刻度尺：一条尺自含「状态带+示例针+轴刻度+下一步」，左右并排扫读；把「焦虑箭头」转译成位置问题",
        selfcheck="v1 版式崩坏；v3 整幅布局通过 → v4 修层序（色带文字改在采样竖线之后绘制）并保留数值显示 128/5.6/452/3.42，zoom 复核通过",
        basis="参考区间为通用演示（非某实验室正式发布）；建议行为为常识性示例",
    ),
    dict(
        id="case-05", v=3, size="420×960", medium="手机竖屏（群聊/朋友圈）",
        device="点单前对照",
        pain="全糖奶茶里几十克糖没有体感；日摄入限怎么对照更没人讲；喝完就忘",
        stage="想告诉常喝奶茶的人「一杯≈几块方糖、距离上限几杯」",
        audience="奶茶常客",
        goal="把 50 g 翻译成 10 块方糖+WHO 25 g 线，并给出热量/运动换算口径",
        content=[
            "标题：一杯全糖奶茶里，糖有多少？副句：按常见全糖口径 50 g 演示，本页数字全部同口径",
            "杯中糖块图：2×5 共 10 块（5 g/块）≈ 50 g；WHO 理想日限 25 g（约 6 茶匙）虚线恰在半杯：「只需半杯糖，就到达理想上限」",
            "统计四卡：50 g 糖总量 / 10 块方糖 / 200 千卡 kcal / 20 分钟慢跑",
            "换算注释：糖 4 kcal/g → 200 kcal；慢跑 10 kcal/min（演示）→ 20 分钟",
            "WHO 注：2015 指南——游离糖低于 10% 能量（强建议），降到 5% 以下 ≈ 25 g/日（条件建议）",
            "页脚：各店杯型糖量差异大 · 无糖≠0 糖 · 演示数据",
        ],
        claims=[
            "杯糖 50 g 取常见全糖口径演示值（经 WHO 检索后由 47g 调整而来，见 plan v1.1.2；10×5 g 恰可整除）",
            "WHO 25 g = 2000 kcal 饮食 5%E 的对应值（图注「约 6 茶匙」）；半杯线 25 g 几何居中可回算",
            "热值 4 kcal/g 为图表演示口径（图内已标「演示」）；20 分钟慢跑=200 kcal÷10 kcal·min⁻¹ 同口径换算",
        ],
        standards=[("S5a", "糖块计数与克数互证", "2×5 块 ×5 g=50 g；zoom-case-05-a 清点无误"),
                   ("S5b", "WHO 25 g 日限对照线", "虚线穿过杯体中位（50/2=25）；zoom-case-05-a"),
                   ("S5c", "运动换算口径标注", "「糖 4 kcal/g→200 kcal；慢跑 10 kcal/min（演示）→20 分钟」逐字核对")],
        visual="杯体剖面当容器：糖块实体化（可数），虚线=每日理想上限；四卡给「总量/颗数/热量/时间」四种单位表达同一事实",
        selfcheck="v1 版式崩坏；v3 整幅与放大均通过即终版（v4/v5/v6 生成的冗余副本未被渲染使用）",
        basis="50 g 为演示口径（检索核实 WHO 口径后自定）；换算为演示值",
    ),
    dict(
        id="case-06", v=6, size="900×1200", medium="A4 近比行动卡（驿站海报/手机转发）",
        device="货架前抬头 3 秒",
        pain="取件码「3-2-1-xxxx」新手不知道先看哪段，误按手机尾号找格子",
        stage="第一次去驿站取件，短信里的码读不出来",
        audience="首次取件的老人/学生",
        goal="按「排→层→号位」三步走到格子，并知道误区在哪",
        content=[
            "标题：取件码怎么读：3-2-1-xxxx；副句：三段各管一件事——先排、再层、后号位（常见驿站口径·演示）",
            "三段解码卡：3=第 3 排（站在货架前，先抬头找排号牌）/ 2=第 2 层（层号从下往上数：2=中层）/ 1=第 1 号位（贴签数字对上短信里最后 4 位）",
            "货架正视示意：单元格栏（排头标记+号位芯片 1..4），例：3 排 · 2 层 · 1 号位",
            "高亮格：红色描边 + 「你的包裹」标签 + 号位芯片（1 红底白字）",
            "站位俯视：你 ↔ 货架（头顶排号牌），三步 1 找排号牌（在头顶）→ 2 数层号（自下而上）→ 3 对号位贴签×尾 4 位",
            "误区条：按手机尾号找——货架认「排/层/号位」，取件码最后 4 位只在格内贴签上对号",
            "页脚：编号习惯依驿站而异 · 自拟演示口径",
        ],
        claims=[
            "「排/层/号位」为常见驿站编号习惯演示（自拟，驿站间规则不同——图内已标）",
            "取件码拆段语义为演示口径；短信尾 4 位与格内贴签对应关系为通行做法的转述",
            "货架/俯视两视图为自绘示意（同一网格数据源，站位一致）",
        ],
        standards=[("S6a", "取件码三段拆解为排/层/号位", "三段解码卡与三个大号字符；zoom-case-06-a"),
                   ("S6b", "货架正视示意与俯视站位一致", "正视格网 + 俯视含「你/货架」双要素；高亮格与俯视同编号"),
                   ("S6c", "误区条可读且不遮挡", "「常见误区：按手机尾号找——…」整行可读；zoom-case-06-b（v6 修「你的包裹」不压号位芯片后复核）")],
        visual="正视货架+俯视站位双视图：把「码→格」的三段语义逐段放大并用红框高亮锁定行动目标；误区条用「错误→正解」句式纠错",
        selfcheck="v1 版式崩坏；v3 页脚偏紧 → v4 页脚 y 移至 1178；放大核验发现「你的包裹」压住号位芯片「2」→ v6 上移标签至格内空白带并复看通过",
        basis="驿站编号习惯自拟；示意图标注「驿站间规则不同」",
    ),
    dict(
        id="case-07", v=4, size="1000×1000", medium="方图（洗衣房小抄/贴墙）",
        device="洗衣房/卫生间旁",
        pain="洗涤标签八符号像天书；热水洗缩水、深浅同桶染色等高频事故反复发生",
        stage="洗前把常遇八格翻译一遍，顺便带出两条事故对照",
        audience="独自住、自己洗衣服的年轻人",
        goal="30 秒看懂八符号+禁忌，并记住两条翻标对策",
        content=[
            "标题：洗衣内标八符号：翻译一遍就不怕；副句：常用八格 · 依据通用护理符号体系（GB/T 8685）自绘示意",
            "八格（符号+中文+禁忌三要素）：30 机洗 30°C（深色翻面、拉拉链）/ 手洗（轻搓勿拧、水温 30 以内）/ 不可漂白（禁含氯漂白剂 84 类、去渍用氧净或局部）/ 不可翻转烘干（禁滚筒烘干机、热缩水主要来自它）/ 熨烫 ≤110°C（低温熨垫布、化纤印花常见）/ 不可干洗（禁四氯乙烯类、羽绒服常见此标）/ 平摊晾干（洗后铺平防垂长、毛衣必做）/ 悬挂晾干（挂起阴干勿暴晒、衬衫首选）",
            "事故演示 A：白 T 与牛仔裤同桶 → 染成蓝白花；翻标对策：深浅分桶，冷水先单独洗新牛仔",
            "事故演示 B：羊毛衫热水机洗 → 缩成童装；翻标对策：见手洗/三角带叉，就别进热水快洗",
            "页脚：符号依 GB/T 8685（与 ISO 3758 一致）通用体系自绘示意；衣物以洗标原文为准 · 演示数据",
        ],
        claims=[
            "八符号对应 GB/T 8685 / ISO 3758 通用体系，本图几何为自绘示意（非官方矢量）",
            "两条「事故演示」为示例情节（非实拍/非调研数据），对策为常识性洗衣手法",
            "禁忌句（84 类/四氯乙烯类/热缩水来源）为通俗化表述",
        ],
        standards=[("S7a", "八格每格「符号+中文+禁忌」三要素", "8 格清点齐全；zoom-case-07-a 前四格、zoom-b 后四格符号清晰"),
                   ("S7b", "高频误洗事故两条对照", "事故 A/B 卡对照句式；整幅观察"),
                   ("S7c", "依据 GB/T 8685 自绘声明", "副句+页脚两处")],
        visual="八宫格符号墙+两条事故对照纵列：符号本身放大（点/叉/斜杠细节可辨），事故卡以「结果→对策」句式收尾",
        selfcheck="v1 版式崩坏；v3 常规看图发现「不可漂白」三角过浅 → v4 三角改白底+三边描边并放大复核",
        basis="符号体系为公开标准体系的自绘示意；事故为演示",
    ),
    dict(
        id="case-08", v=4, size="420×960", medium="手机竖屏（天气截图旁）",
        device="出门前 10 秒",
        pain="降水概率 60% 被普遍读成「下 60% 的时间」或「60% 的面积下雨」；带不带伞没有决定规则",
        stage="看着 60% 出门，需要一个可操作的读法与阈值",
        audience="每天看天气出门的人",
        goal="用「100 次相似日子」点阵读懂概率语义，并取走一个可执行的带伞阈值",
        content=[
            "标题：降水概率 60%，什么意思？副句：一张「100 次相似日子」点阵：60 个蓝点下过雨",
            "点阵（10×10，60 实 + 40 空）：蓝点=下雨的日子×60；空点=没下雨的日子×40；图例自含",
            "三误会拆解：✗ 和时间无关（不是「下 60% 的时间」）/ ✗ 和面积无关（不是「全城 60% 地面」）/ ✓ 是可能性（100 次相似天气约 60 次雨）",
            "决策条（演示阈值）：0–30 随手不带 / 30–95 收进包里 / 95–100 手里拿着；注：60% 落在两档之间，看当天怎么走",
            "页脚：语义为演示解释（各天气服务定义可能不同）· 阈值为个人示例",
        ],
        claims=[
            "「相似日子/约 60 次出现降水」为演示解释（各服务定义细节不一，图内已标）",
            "30/95 阈值为个人示例（非气象行业建议）",
            "点阵计数与语义一一对应：60/100 可清点",
        ],
        standards=[("S8a", "10×10 点阵恰好 60 点且图例自含", "6×10 实点 + 4×10 空环；zoom-case-08-a 清点"),
                   ("S8b", "三条误区修正可读", "✗/✗/✓ 三行（时间/面积/可能性）；同一放大件复核"),
                   ("S8c", "决策条为可执行建议而非装饰按钮", "三档阈值条 0/30/95 刻度与三段标签；zoom-case-08-b")],
        visual="频数化隐喻：把抽象概率铺成 100 个具体日子；决策条与其说是控件，不如说是把阈值画成刻度尺分档",
        selfcheck="v1 版式崩坏；v3 常规看图后决策条注释贴边框 → v4 标尺/标签/注三行坐标下移并放大复核",
        basis="概率语义为演示转述；阈值自拟",
    ),
    dict(
        id="case-09", v=4, size="1180×820", medium="平板横排",
        device="年终奖谈判/规划季",
        pain="年终奖发放临界点：36,000+1 元 → 税额即跳档，到手少 2,309 元；「并入 vs 单独」无人对照",
        stage="拿到年终奖 offer，想预估不同奖金数额下的到手金额",
        audience="领取一次性奖金的上班族",
        goal="看懂 36,000 临界悬崖、四阶台阶，并取走两方案差额结论",
        content=[
            "标题：年终奖的悬崖：多领 1 元，少拿 2,309 元；副句：单独计税按「奖金 ÷ 12」定档——月均过 3,000 一点点，税率从 3% 跳到 10%",
            "政策胶囊：财政部 税务总局公告2023年第30号 · 至 2027-12-31",
            "四阶台阶（奖金→到手，虚构示例）：34,999→33,949 / 36,000→34,920 / 36,001→32,611 / 38,566.67→34,920；崖标：多发 1 元 · 少拿 2,309.10 元",
            "两方案对照（演示 profile：全年工资 108,000 · 年终奖 36,000 · 无专项扣除）：方案 A 并入综合 5,880 元/年（奖薪一起爬年度表，跳到 10% 档）↔ 方案 B 单独计税 3,360 元/年（奖按月度表 3%、薪按年度表 10%）→ 选 B 少缴 2,520 元（演示口径，人人不同）",
            "三条提醒：单独计税一年只可用一次 / 发薪时为预扣、次年汇算可改选 / 归属看实际发放年份",
            "用法行：发放月梳全年收入与扣除 → 个税 App 两法各试算一遍，选税额低者",
            "机制注释：月均 3,000 是「月均」——36,001÷12=3,000.08，整单税率即跳 10%；至 38,566.67 元起补回，到手追平 34,920",
            "页脚公式：税 = 奖金 ×（奖金÷12 定档税率）− 速算扣除数；示例虚构，不构成税务建议 · 演示数据",
        ],
        claims=[
            "政策口径（公告 2023 年第 30 号 · 执行至 2027-12-31）经检索核实后进 plan v1.1.1（websearch 记录见 tool-usage.jsonl）",
            "四点税额 1,049.97/1,080/3,390.10/3,646.667 与到手台阶 33,949.03/34,920/32,610.90/34,920.003 全部与 " + CALCS_REF + " 的 c09 一致（公式回算：36,001×10%−210=3,390.10）",
            "A/B 方案与「演示 profile」自拟；差额 2,520=5,880−3,360；整单税率跳档即「悬崖 2,309.10=34,920−32,610.90」",
        ],
        standards=[("S9a", "临界台阶至少四点且税额/到手可回算", "四阶台阶数字 + 崖差 2,309.10（34,920−32,610.90）；zoom-case-09-b"),
                   ("S9b", "两方案合计对比", "A 5,880 vs B 3,360 + 差 2,520；zoom-case-09-a"),
                   ("S9c", "政策时效与情形差异声明", "公告胶囊 + 「演示口径，人人不同」+ 页脚")],
        visual="悬崖式台阶图：横轴=奖金、纵轴=到手；36,000/36,001 间一刀切下 2,309 元；下接两方案对撞卡把决策变成差额数字",
        selfcheck="v1 版式崩坏；v3 后 B 列说明过长跑出白卡 → v4 拆双行 y 362/382 放大复核",
        basis="政策经检索核实（2023 年第 30 号）；数字为公式演示计算（非申报数据）",
    ),
    dict(
        id="case-10", v=4, size="420×960", medium="手机竖屏（家人群转发）",
        device="给老人理药时对照",
        pain="药盒上的 qd/tid/a.c./p.c. 没人翻得懂；老人按时点吃不准，子女隔空叮嘱无效",
        stage="把「处方缩写」翻成人话，再把自家四个药名填进一日药盒",
        audience="帮老人理药的子女",
        goal="会读四句缩写，并把把四个填药例子落到棋盘格",
        content=[
            "标题：药盒上的「外文」缩写；副句：为老人整理药盒，先把四句拉丁语翻成人话",
            "缩写四行卡：qd 每日一次（固定同一时间）/ tid 每日三次（跟着三餐走）/ a.c. 饭前服（约餐前 30 分钟）/ p.c. 饭后服（随餐或餐后即刻）",
            "药盒棋盘（演示）：早/中/晚 三列；四药行：钙片 a.c.、降压药 qd（每日一粒）、维生素 D tid、胃药 p.c.——与上表逐一对照填一填",
            "填药步骤：① 核对药名与缩写；② 早格先放、晚格留位；③ 盖好拍照，发到家人群",
            "页脚：缩写译义为药学惯例演示；以医嘱与药师说法为准 · 演示数据",
        ],
        claims=[
            "qd/tid/a.c./p.c. 为通行药学缩写；译意按「药学惯例演示」（图内已标以医嘱与药师为准）",
            "四个药名（钙片/降压药/维生素 D/胃药）+ 时点组合为虚构演示，非真实处方",
            "棋盘格与四行例药一一自洽（对照填写关系由图上复核）",
        ],
        standards=[("S10a", "缩写-中文-时点三列四行", "qd/tid/a.c./p.c. 四行卡含中文与具体做法；zoom-case-10-a"),
                   ("S10b", "一日棋盘与上表用例逐格对应", "棋盘四行×三列与四例药互引；zoom-case-10-a"),
                   ("S10c", "「以医嘱/药师为准」声明", "页脚整行核对")],
        visual="「翻译表→棋盘实践」双层结构：上四行教人读，下棋盘让人用自家药填进去；给步骤不给空模板",
        selfcheck="v1 版式崩坏；v3 后板标题被列头盖住、填药步骤断行难读 → v4 板标题上移 y 506、步骤改两条独立行并放大复核",
        basis="缩写译义为通行惯例演示；填写示例虚构",
    ),
]

# ---------------- 1) iterations.jsonl ----------------
S = "tmp/20261016T164020-m1/B06/steps/"
T_V1VIEW = "2026-10-18T21:26:30+08:00"   # v1 接触表首看（估：同一批间补时）
T_V2HASH = "2026-10-18T21:31:00+08:00"   # v2 响应字节对比鉴别（估）
T_V3VIEW = "2026-10-18T21:41:00+08:00"   # v3 整幅逐件（估）
T_V4VIEW = "2026-10-18T21:52:00+08:00"   # v4/v5 首轮放大切片（估）
T_V6VIEW = "2026-10-19T08:55:30+08:00"   # c06 v6 复看（zoom 08:54:54 再生成、render 08:54:37）
T_FINAL = NOW


def it(case, ver, parent, kind, observed_at, basis, obs, before=None, after=None):
    return {"case_id": case, "version": ver, "parent_version": parent, "kind": kind,
            "observed_at": observed_at, "observed_basis": basis, "observation": obs,
            "before_image": before, "after_image": after, "path_base": "suite_root"}


v1_issues = {
    "case-01": "版式崩坏：标题/图元/正文堆叠到画布左上，全图不可用",
    "case-02": "同左；三类版面（柱区/坡轴/卡片）全部失去网格语义",
    "case-03": "同左；三档剖面/水位/算例卡无可读层级",
    "case-04": "同左；四条刻度尺与指针全部叠于左上",
    "case-05": "同左；杯体/糖块/统计卡叠置不可辨",
    "case-06": "同左；货架格网/三段解码/俯视全部塌缩",
    "case-07": "同左；八宫格塌缩，符号与说明字相互覆盖",
    "case-08": "同左；点阵/误区行/决策条不可分",
    "case-09": "同左；台阶/悬崖/两方案卡叠置",
    "case-10": "同左；缩写表/棋盘/步骤叠置",
}
defect_v3 = {
    "case-01": "通过",
    "case-02": "通过版式看图；页脚整行压底边 → 排入 v4",
    "case-03": "通过",
    "case-04": "布局通过；色带文字被采样竖线压序、读数显示待精修 → 排入 v4",
    "case-05": "通过",
    "case-06": "版式通过；页脚贴近底边 → y 1178 排入 v4",
    "case-07": "版式通过；「不可漂白」三角过浅 → 排入 v4",
    "case-08": "版式通过；决策条注释贴边框 → 排入 v4",
    "case-09": "版式通过；B 列说明越白卡 → 排入 v4",
    "case-10": "版式通过；板标题被列头盖住、填药步骤断行 → 排入 v4",
}
fix_v4 = {
    "case-02": "三问行 y=1178 步 26、页脚移 1252（后又在 v5 改短句）",
    "case-04": "色带文字改在采样竖线之后绘制（z 序反转）；保留读数 128/5.6/452/3.42",
    "case-06": "页脚 y=1178",
    "case-07": "「不可漂白」三角改白底+三边 INK7 描边",
    "case-08": "决策条 ruler y 872、标签 y 888、注 y 906",
    "case-09": "B 列说明拆两行 y 362/382",
    "case-10": "板标题上移 y 506、填药步骤改两条独立行",
}

iters = []
# 一）基线 v1：接触表首看
for i, c in enumerate(CASES, 1):
    sid = c["id"]
    iters.append(it(sid, "v1", None, "baseline", T_V1VIEW,
                    S + "sheet-%d.png（初版，同名文件其后被终态复存；第一时间块估时）" % ((i + 1) // 2),
                    "v1 批 10 张全部 HTTP 200 但版式不可用：" + v1_issues[sid] +
                    "（根因=凭记忆误写的 DSL 语法：Text 无 x/y 属性、Container 无定位语义；"
                    "真实能力为 Positioned 定位——公共组件随即整体重写）"))
# 二）v2 批：驱动误渲（字节对比鉴别，不构成看图）
for c in CASES:
    sid = c["id"]
    iters.append(it(sid, "v2", "v1", "syntax-fix", T_V2HASH,
                    "renders/b06-%s-v2-*.resp 与 v1 响应字节对比（哈希相同）——文件级鉴别，本次无新增看图" % c["id"],
                    "v2 驱动误渲：把 v1 旧格式再次提交，响应字节与 v1 完全一致；"
                    "已重写的 v2 DSL 未被服务使用。留痕 renders/，修复延后至 v3 批（数量为 10 次同因）。"))
# 三）v3 批：格式修复生效 + 整幅逐件看图
for c in CASES:
    sid = c["id"]
    iters.append(it(sid, "v3", "v1", "syntax-fix", T_V3VIEW,
                    "outputs/20261016T164020-m1/B06/%s/final.png（v3 整幅）" % sid,
                    "b06_common 按已验证语法重写（Positioned/Container/fontStyle=BOLD 等 39 字节响应块不同即生效），"
                    "渲染 200: " + defect_v3[sid]))
# 四）v4 批 + v5 + v6
for c in CASES:
    sid = c["id"]
    if sid in fix_v4:
        iters.append(it(sid, "v4", "v3", "visual-iteration", T_V4VIEW,
                        "outputs/20261016T164020-m1/B06/%s/final.png（v4 整幅）+ %s zoom-case-0%s-*.png（终态放大；首轮部分在 21:52 前生成、10-19 晨 08:54:54 同名复存）" % (sid, S, sid.split("-")[1]),
                        "看图(v3 缺陷) → 修改 → 重渲 200 → 复看(放大/整幅)：" + fix_v4[sid]))
iters.append(it("case-02", "v5", "v4", "visual-iteration", "2026-10-18T21:49:30+08:00",
                "case-02/final.png（v5 整幅）",
                "页脚口径句过长在 720 宽下显挤 → 换更短一行：「口径：等额『本金+固定手续费』分期 · 名义 7.2% · 实际≈月 IRR 1.0862% 复利 13.84% · 示例虚构」；复看通过"))
iters.append(it("case-06", "v6", "v4", "visual-iteration", T_V6VIEW,
                S + "zoom-case-06-b.png（v6 再生成；render_b06 08:54:37 得 200）",
                "放大切片暴露「你的包裹」红字压住号位芯片「2」→ 标签上移至格内空白带（hy+12）并放大复看通过；整幅见于终态接触表"))
iters.append(it("all", "final", None, "final-review", T_FINAL,
                S + "sheet-1..5.png（终态，10-19 08:56:02 重建）+ zoom 20 张（08:54:54 再生成）",
                "终态五张接触表整卷复审 + 每件 1–2 处密集区 1:1 放大复看：10/10 通过"
                "（版本终态：c01/c03/c05=v3，c02=v5，c04/c07/c08/c09/c10=v4，c06=v6）；"
                "此前 41 次看图事件明细见以上各行。"))
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(x, ensure_ascii=False) for x in iters) + "\n", encoding="utf-8")
kinds = {}
for x in iters:
    kinds[x["kind"]] = kinds.get(x["kind"], 0) + 1
print("iterations.jsonl rows:", len(iters), kinds)

# ---------------- 2) tool-usage.jsonl ----------------
tus = [
    {"id": "B06-tool-0001", "task_id": "B06", "tool": "cached-docs（零新增 HTTP）",
     "purpose": "沿用 B04 已实抓 ai-guide.md 与 DSL 文档缓存（DSL 属性/字体/边框枚举/每页底色规约），未重复下载",
     "input": "tmp/20261016T164020-m1/B04/renders/（文档缓存）", "context": "构建前", "at": NOW,
     "affects": "all cases", "http_request_ref": None, "path_base": "suite_root"},
    {"id": "B06-tool-0002", "task_id": "B06", "tool": "websearch",
     "purpose": "检索核实全年一次性奖金单独计税政策依据（公告号与执行截止）",
     "input": "websearch『年终奖单独计税 财政部 税务总局公告 2023年第30号』（关键词措辞为事后追记的近似复述）",
     "context": "c09 口径核实（2026-10-18 晚，先于渲染）", "at": "2026-10-18T20:58:00+08:00",
     "affects": "case-09",
     "result": "确认：财政部 税务总局公告2023年第30号，执行至 2027-12-31 → 记入 plan v1.1.1 并上图内政策胶囊",
     "http_request_ref": None, "path_base": "suite_root"},
    {"id": "B06-tool-0003", "task_id": "B06", "tool": "websearch",
     "purpose": "核实 WHO 游离糖建议口径（10%E 强建议 / 5%E≈25g 条件建议）",
     "input": "websearch『WHO 游离糖 建议 25 克 10% 能量』（关键词措辞为事后追记的近似复述）",
     "context": "c05 口径核实；据此把演示杯糖量 47g 调整为 50g 并锁定换算（plan v1.1.2）",
     "at": "2026-10-18T20:58:00+08:00", "affects": "case-05",
     "result": "确认：WHO 2015 指南 <10%E（强建议）、<5%E≈25g≈6 茶匙（条件建议）→ 图内照引",
     "http_request_ref": None, "path_base": "suite_root"},
    {"id": "B06-tool-0004", "task_id": "B06", "tool": "b06_build.py",
     "purpose": "十件 DSL 参数化生成（_v2/_v3/_v4/_v5/_v6 后缀防覆盖；旧版件不可覆盖）",
     "input": "tmp/<run>/B06/dsl/case-XX[_vN].snapshot", "context": "各批改版前", "at": NOW,
     "affects": "all cases", "http_request_ref": None, "path_base": "suite_root"},
    {"id": "B06-tool-0005", "task_id": "B06", "tool": "render_b06.py + snapshot_client",
     "purpose": "批渲染驱动；候选顺序修正（显式 _vN 后缀优先，杜绝再次误渲旧版）+ 响应字节漏盘时从 renders/*.resp 补落盘",
     "input": "tmp/<run>/B06/requests.jsonl；renders/ 全部 req/resp 留痕", "context": "与真实渲染逐一并行",
     "at": NOW, "affects": "all cases", "http_request_ref": "B06-render-0001..0039", "path_base": "suite_root"},
    {"id": "B06-tool-0006", "task_id": "B06", "tool": "b06_sheets.py(PIL)",
     "purpose": "五张双联接触表（横向比较/整卷复审工具；不替代整幅逐张查看）",
     "input": "tmp/<run>/B06/steps/sheet-1..5.png（终态版 10-19 08:56:02）", "context": "v1 初判 + 终态复用", "at": NOW,
     "affects": "10 cases", "http_request_ref": None, "path_base": "suite_root"},
    {"id": "B06-tool-0007", "task_id": "B06", "tool": "zoom_b06.py(PIL crop)",
     "purpose": "每件 1–2 处密集区 1:1 放大切片共 20 张（捕捉裁切/遮挡缺陷：c06 标签缺陷由此暴露）",
     "input": "tmp/<run>/B06/steps/zoom-case-XX-[a|b].png（终态版 10-19 08:54:54 再生成）", "context": "v4/v5/v6 复核与终审",
     "at": NOW, "affects": "10 cases", "http_request_ref": None, "path_base": "suite_root"},
    {"id": "B06-tool-0008", "task_id": "B06", "tool": "hash 对比",
     "purpose": "v1/v2 渲染响应字节一致（SHA256 相同）→ 判定 v2 驱动误渲旧格式，留证后待 v3 批",
     "input": "renders/b06-case-XX-v1-*.resp vs v2", "context": "v2 批后", "at": "2026-10-18T21:31:00+08:00",
     "affects": "all cases", "http_request_ref": None, "path_base": "suite_root"},
    {"id": "B06-tool-0009", "task_id": "B06", "tool": "extract_text.py",
     "purpose": "final.snapshot 文本抽取（352 条）与 case.md 校笔", "input": "tmp/<run>/B06/text_dump.txt",
     "context": "收尾", "at": NOW, "affects": "10 cases", "http_request_ref": None, "path_base": "suite_root"},
    {"id": "B06-tool-0010", "task_id": "B06", "tool": "research/calcs.json + 二分法 IRR",
     "purpose": "数值唯一基准：c02 IRR 二分精确解 1.0862%/月、c03 拆段电费、c09 四点税额、c05 换算口径（先算后进 DSL）",
     "input": "tmp/<run>/B06/research/calcs.json", "context": "研究阶段（plan v1 后）", "at": "2026-10-18T20:56:27+08:00",
     "affects": "case-02/03/05/09", "http_request_ref": None, "path_base": "suite_root"},
    {"id": "B06-tool-0011", "task_id": "B06", "tool": "finalize_b06_docs.py",
     "purpose": "交付文档/台账/指标落盘（本脚本：case.md×10、portfolio、gallery、snapshot-usage、metrics、problem-evidence、design-review）",
     "input": "outputs/<run>/B06/*；tmp/<run>/B06/*", "context": "收尾", "at": NOW,
     "affects": "all cases", "http_request_ref": None, "path_base": "suite_root"},
]
(TMP / "tool-usage.jsonl").write_text(
    "\n".join(json.dumps(x, ensure_ascii=False) for x in tus) + "\n", encoding="utf-8")
print("tool-usage.jsonl rows:", len(tus))

# ---------------- 3) problem-evidence.json ----------------
EVID = {
    "case-01": dict(
        evidence=[
            ("可观察现象", "瓶身/盒身开封后没有任何记录手段，家庭实际靠「气味/外观」判断可用性",
             "日常自观察（非现场调研/非用户访谈）"),
            ("标准与政策", "PAO 开罐符号（开盖罐身+「12M」类月数）为化妆品/食品行业通行惯例——本图依惯例自绘示意，不作官方符号复制声明",
             "行业通用行为（自绘复述，未下载标准文本）"),
            ("自拟演示口径", "6M/12M/24M 类目（防晒霜/面霜/洗发水）、示例未开封期 2027-07-02 均为演示",
             "自拟演示"),
        ], policy_ref=None,
        redesign_choices=["把语法先于类目：先教「符号=开封后月数」再给类目", "给可写日期空栏与示例带（行动自查）", "「开封期≠保质期」对照卡直接写下两套时效"],
        observed_improvement=["符号/类目/写日期三步在 1:1 放大（zoom-01-a/b）清晰可读", "行动区含可填空栏（不再只是告知）"],
        unverified_effects=["按卡写日期是否能减用过期品（未做用户实验）", "类目月数对个人产品的适用度（以包装说明为准）"]),
    "case-02": dict(
        evidence=[
            ("可观察现象", "分期广告以「每期 1,072」「月费率 0.6%」呈现，金额与费率同时出现但口径未对齐",
             "日常自观察（非调研）"),
            ("标准与政策", "实际年化以月 IRR 复利折算为通行披露口径（图内标注「监管披露口径」）；等额「本金+固定手续费」为常见分期结构",
             "常识性复述（图内已标演示口径）"),
            ("自拟演示口径", "12,000/12 期/72 元/期的结构、7.2% 名义口径、三问卡文案为演示；「日息万五≈18~20%」为演示换算",
             "自拟演示（IRR 1.0862% 为本地精确计算）"),
        ], policy_ref=None,
        redesign_choices=["余额柱+固定手续费帽直接画出「名义利率错觉」的几何根源", "双年化并列+「1.9 倍」关系胶囊", "渲染时明确「月 IRR 1.09% 复利」的定位（页脚给精确值 1.0862%/13.84%）"],
        observed_improvement=["12 期流水一屏可读（zoom-02-a）", "名义/实际两个年化差在 1:1 放大下清晰（zoom-02-b）"],
        unverified_effects=["该表述能否降低误判（未做用户实验）", "对其他分期结构（端手/灵活期数）的适用度"]),
    "case-03": dict(
        evidence=[
            ("可观察现象", "阶梯电价有三档与累计口径，账单不呈现「身处哪一档、跨档后怎么算」",
             "日常自观察（非调研）"),
            ("标准与政策", "阶梯电价按年度累计分三档递进的机制为通行结构；具体档位/电价各地不同",
             "常识复述；图内标注以当地文件为准"),
            ("自拟演示口径", "2,760/4,800 度边界、0.52/0.57/0.82 元/度、2,700 度累计+480 月用电为演示省份口径（calcs.json）",
             "自拟演示"),
        ], policy_ref=None,
        redesign_choices=["蓄水池三层剖面隐喻（档=层、累计=水位）", "跨档月拆段算式卡（60×0.52 + 420×0.57）", "「直觉单价×用电」对照给多付 21.0 元差值"],
        observed_improvement=["三档边界与水位几何关系一眼可读（zoom-03-a）", "算例链可回算（zoom-03-b：31.20+239.40=270.60；直觉差 21.0/+8.4%）"],
        unverified_effects=["本地实际账单是否可用同一模型（未验证）", "夏季连跨两层的预警效果（未做用户实验）"]),
    "case-04": dict(
        evidence=[
            ("可观察现象", "体检报告以「数值+上下箭头」呈现，超出参考即挂箭头；偏差多少要紧、如何先记录再复查没有指引",
             "日常自观察（非调研）"),
            ("标准与政策", "参考区间「约 95% 健康人落入」与「各实验室略有差异」为通行原列；箭头≠诊断",
             "常识复述；图内标注不构成医疗建议"),
            ("自拟演示口径", "四项区间的端点/分档刻度与示例值（128/5.6/452/3.42）虚构造型（同一几何比例尺）",
             "自拟演示"),
        ], policy_ref=None,
        redesign_choices=["跑道刻度尺：每条自含 状态带+示例针+数值轴+行动注", "三种状态色语统一（正常/边缘/超限）", "「离线多远」转换：先把焦虑转成位置再定动作"],
        observed_improvement=["每条尺在同一放大切片内可读状态/位置/注（zoom-04-a/b）", "v4 修层序后读数字不再被竖线压住"],
        unverified_effects=["在读体检报告的实际场景下是否降低焦虑（未做用户实验）", "复查频次建议的医学合理性（以医嘱为准）"]),
    "case-05": dict(
        evidence=[
            ("可观察现象", "全糖奶茶几十克糖无体感，喝完即忘；「无糖/少糖」与营养标签对不上号",
             "日常自观察（非调研）"),
            ("标准与政策", "WHO 2015 指南：游离糖低于总能量 10%（强建议）、进一步 5%≈25g/日（条件建议）；经检索核实（plan v1.1.2）",
             "检索核实（tool-usage B06-tool-0003）"),
            ("自拟演示口径", "演示杯 50 g（10×5 g 方糖整除）、热值 4 kcal/g、慢跑 10 kcal/min→20 分钟、各店差异声明",
             "自拟演示"),
        ], policy_ref="WHO Sugars intake guideline（2015）；本图为转述示意，非 WHO 官方图",
        redesign_choices=["糖块实体化（2×5）+计数与克数互证", "WHO 25g 虚线画在杯体中位（几何自然成立）", "同一 50g 的四种单位卡（克/颗/千卡/分钟）"],
        observed_improvement=["10 块清点无误（zoom-05-a）", "「半杯即达 WHO 日限」关系可读"],
        unverified_effects=["对购买/点单决策的影响（未做用户实验）", "特定门店实际糖量差异（以门店口径为准）"]),
    "case-06": dict(
        evidence=[
            ("可观察现象", "取件短信一行数字（3-2-1-xxxx）对新手无语义段；驿站为货架自取，新手在货位前不知从哪看起",
             "日常自观察（非调研）"),
            ("标准与政策", "驿站货架通常按「排/层/号位」编码、短信尾号与格内贴签对应——通行做法转述，具体驿站规则不同",
             "常识转述；图内标注「编号习惯依驿站而异」"),
            ("自拟演示口径", "4×3 格网规格、示例码 3-2-1、高亮位与俯视站位为自拟演示",
             "自拟演示"),
        ], policy_ref=None,
        redesign_choices=["三段大号字符解码卡（先排/再层/后号位）", "正视货架+俯视站位双视图（同一网格）", "误区条（不按尾号找）+ 三步行动流"],
        observed_improvement=["三段解码与高亮格关系清晰（zoom-06-a）", "v6 后「你的包裹」不再压号位芯片（zoom-06-b）"],
        unverified_effects=["老人首次取件的成功率/耗时变化（未做用户实验）", "各驿站适配度（以驿站说明为准）"]),
    "case-07": dict(
        evidence=[
            ("可观察现象", "洗涤标签八常见符号在衣物内标上密集出现，新手无法翻译出禁忌",
             "日常自观察（非调研）"),
            ("标准与政策", "GB/T 8685（与 ISO 3758 一致）通用护理符号体系——本图符号为自绘示意",
             "通用体系自绘（未下载标准文本做矢量复制）"),
            ("自拟演示口径", "两条「事故演示」（同桶染色/热水缩水）及其对策为示例情节",
             "自拟演示"),
        ], policy_ref="GB/T 8685 / ISO 3758（通用护理符号体系，图内自绘示意）",
        redesign_choices=["每格三要素（符号+中文+禁忌）一屏清点", "符号本体放大可辨（点/叉/斜杠）", "事故卡用「结果→对策」句式把标准落到行为"],
        observed_improvement=["八格符号+禁忌在两处 1:1 放大下可读（zoom-07-a/b）", "v4 白底描边后「不可漂白」三角不再过浅"],
        unverified_effects=["事故再现率下降（未做用户实验）", "特殊面料仍以洗标原文为准"]),
    "case-08": dict(
        evidence=[
            ("可观察现象", "降水概率 60% 常被理解为「60% 时间/面积下雨」；带不带伞没有决定规则",
             "日常自观察（非调研）"),
            ("标准与政策", "降水概率语义=出现降水的可能性；不同天气服务定义细节不一（图内标注演示解释）",
             "语义转述（自拟演示解释为主入口）"),
            ("自拟演示口径", "100 日点阵 60/40 配比、30/95 阈值与三档行动分区为个人示例",
             "自拟演示"),
        ], policy_ref=None,
        redesign_choices=["频数化隐喻：概率 → 100 个具体日子（6×10 蓝点+4×10 空）", "三条误区修正（✗/✗/✓）直接反写误读", "决策阈值条（0/30/95 分档）而非装饰按钮"],
        observed_improvement=["60/100 可清点且图例自含（zoom-08-a）", "阈值三档与「60% 落在两档之间」的用法注可读（zoom-08-b）"],
        unverified_effects=["误读率是否下降（未做用户实验）", "阈值个人化程度（示例）"]),
    "case-09": dict(
        evidence=[
            ("可观察现象", "年终奖 36,000 与 36,001 之间到手金额出现陡降；「并入 vs 单独」的选择无人给对照",
             "日常自观察（非调研）"),
            ("标准与政策", "全年一次性奖金单独计税依据：财政部 税务总局公告2023年第30号，执行至 2027-12-31；公式=税=奖金×（奖金÷12 定档税率）−速算扣除数（经检索核实）",
             "检索核实（tool-usage B06-tool-0002；plan v1.1.1）"),
            ("自拟演示口径", "四点台阶示例、演示 profile（工资 108,000/奖 36,000/无专项扣除）与「演示口径，人人不同」为自拟",
             "自拟演示（数字由公式精确计算）"),
        ], policy_ref="财政部 税务总局公告2023年第30号（执行至 2027-12-31）",
        redesign_choices=["悬崖式台阶图（横轴=奖金、纵轴=到手）", "四点取临界+回补点 38,566.67", "两方案对撞卡（A 5,880 vs B 3,360，省 2,520）+三条提醒"],
        observed_improvement=["四阶台阶与崖差 2,309.10 可读可回算（zoom-09-b）", "政策胶囊与免责声明在 1:1 放大下清晰（zoom-09-a）"],
        unverified_effects=["该图能否改变个人实际选择（未做用户实验）", "各收入档次的通用性（演示口径，人人不同）"]),
    "case-10": dict(
        evidence=[
            ("可观察现象", "药盒/服医嘱上 qd/tid/a.c./p.c. 等缩写对老人无语义、子女隔空叮嘱效率低",
             "日常自观察（非调研）"),
            ("标准与政策", "qd=每日一次、tid=每日三次、a.c.=饭前、p.c.=饭后为通行药学实践惯例（图内译义演示 + 以医嘱与药师为准）",
             "药学惯例转述（非专业翻译/不建议自行调整时点）"),
            ("自拟演示口径", "自家四药（钙片/降压药/维生素 D/胃药）与时点组合为虚构示例；早/中/晚棋盘为演示工具",
             "自拟演示"),
        ], policy_ref=None,
        redesign_choices=["四行缩写翻译卡（短语型：一句人话）", "一日药盒棋盘把四例药落到格（上表→实践）", "三步填药动作（核对/先放/拍照）替代空模板"],
        observed_improvement=["四例药-棋盘对应关系清晰（zoom-10-a）", "v4 后板标题不被列头遮挡、步骤两行整齐（zoom-10-a/b）"],
        unverified_effects=["老人服药漏服率变化（未做用户实验）", "缩写译义响应用药场景的完整性（以医嘱为准）"]),
}

pe_list = []
for i, c in enumerate(CASES, 1):
    base = EVID[c["id"]]
    pe_list.append({
        "problem_id": "P%02d" % i, "case_id": c["id"],
        "pain_point": c["pain"], "usage_scenario": c["stage"],
        "scenario_requirements": {"audience": c["audience"], "medium": c["medium"],
                                  "view_env/device": c["device"], "watch_goal": c["goal"]},
        "evidence": [{"category": cat, "statement": st, "source": src,
                      "credibility_note": ("自观察非调研；不声称做过现场/用户实验" if cat == "可观察现象" else
                                           ("原文/官方文本未归档，仅复述要点；详见声明" if cat == "标准与政策" else
                                            "自拟；图内已标注演示口径"))}
                     for cat, st, src in base["evidence"]],
        "policy_ref": base["policy_ref"],
        "redesign_choices": base["redesign_choices"],
        "observed_improvement_after_review": base["observed_improvement"],
        "unverified_effects": base["unverified_effects"],
        "final_evidence_files": {"png": "%s/final.png" % c["id"],
                                 "snapshot": "%s/final.snapshot" % c["id"],
                                 "zooms": ["tmp/%s/B06/steps/zoom-%s-a.png" % (RUN, c["id"]),
                                           "tmp/%s/B06/steps/zoom-%s-b.png" % (RUN, c["id"])]},
        "completion_criteria_ref": "plan-v1.md（v1+v1.1）S%d 系列 + G1–G5" % i,
    })

problem_evidence = {
    "schema_version": 1, "task_id": "B06", "run_id": RUN, "created_at": NOW,
    "plan_ref": PLAN_REF, "numeric_baseline": CALCS_REF,
    "categories_legend": {
        "可观察现象": "日常生活自观察；非现场调研、非用户访谈；仅在示意/演示诚实范围内使用",
        "标准与政策": "公开标准/政策建议的关键口径（WHO 指南、GB/T 8685、财政部公告2023年第30号、PAO 惯例、药学惯例）；全文未归档、要点经检索核实后复述；图形一律自绘示意",
        "自拟演示口径": "自拟数据/参数/示例；图内逐件标注「演示口径/演示数据/虚构」，不声称官方背书或实测",
    },
    "websearch_note": "两次 websearch（政策文件号、WHO 25g）真实发生并记入 tool-usage.jsonl；措辞为事后近似追记",
    "problems": pe_list,
}
(OUT / "problem-evidence.json").write_text(
    json.dumps(problem_evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(TMP / "problem-evidence.json").write_text(
    json.dumps(problem_evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("problem-evidence.json written")

# ---------------- 4) case.md ×10 ----------------
for n, c in enumerate(CASES, 1):
    body = ["# %s · 《日常信息重构》第 %d 件（P%02d）" % (c["id"], n, n)]
    body.append("")
    body.append("> B06《日常信息重构十件》· 终版 v%d · 尺寸 %s" % (c["v"], c["size"]))
    body.append("> 素材性质：**虚构/演示**——本件为自主选题创作；证据仅含自观察现象与公开口径转述，")
    body.append("> 无现场调研、无用户实验；语法/数值已在图内标注「演示口径/演示数据/虚构示例」。")
    body.append("")
    body.append("## 一、场景与受众")
    body.append("- **卡点（发现的问题）**：%s" % c["pain"])
    body.append("- **使用场景**：%s" % c["stage"])
    body.append("- **受众**：%s" % c["audience"])
    body.append("- **想完成的事**：%s" % c["goal"])
    body.append("- **媒介/观看环境**：%s（%s · %s）" % (c["medium"], c["size"], c["device"]))
    body.append("")
    body.append("## 二、内容（与画面逐项对应）")
    for b in c["content"]:
        body.append("- %s" % b)
    body.append("")
    body.append("## 三、事实基线（数据来源与口径）")
    body.append("- 数值唯一基准：%s（本地先算后图；十件共享部分见 plan-v1.md）。" % CALCS_REF)
    for k in c["claims"]:
        body.append("- %s" % k)
    body.append("- 证据三分类与逐条来源：`problem-evidence.json`（P%02d）。" % n)
    body.append("")
    body.append("## 四、重构选择（卡点→作品怎么解）")
    pe = problem_evidence["problems"][n - 1]
    for r in pe["redesign_choices"]:
        body.append("- %s" % r)
    body.append("")
    body.append("## 五、视觉要点")
    body.append("- %s" % c["visual"])
    body.append("- 独立性：本件媒介/构图/配色属自定（与其他九件不共用版式系统）。")
    body.append("")
    body.append("## 六、完成标准与实际检查")
    body.append("计划版本：%s（S%d 系列 + G1–G5）" % (PLAN_REF, n))
    body.append("")
    body.append("| ID | 标准 | 实际检查 |")
    body.append("|---|---|---|")
    for sid, st, chk in c["standards"]:
        body.append("| %s | %s | %s |" % (sid, st, chk))
    body.append("")
    body.append("## 七、实际自检与修改记录（看图 → 修复 → 复看）")
    body.append("- %s" % c["selfcheck"])
    body.append("- 全部渲染请求（真实台账）：")
    body.append("  %s。" % REQ_BY_CASE[c["id"]])
    body.append("- 终版：`final.png`（服务 HTTP 200 原始响应字节）+ `final.snapshot`（同名完整 DSL）。")
    body.append("")
    body.append("## 八、素材情况")
    body.append("- 本题允许 DSL 主导 + 具体辅助（run-config: creative=dsl_primary_with_supporting_assets）；")
    body.append("  本件**未嵌入任何外部素材**，画面全部为 DSL 构成；PAO/护理/GB/T 等符号均为自绘示意且图内声明。")
    body.append("")
    body.append("## 九、可观改善 vs 未验证效果")
    body.append("- 可观（画面可读性）：" + pe["observed_improvement_after_review"][0] if pe["observed_improvement_after_review"] else "- 可观：见 design-review.md")
    if len(pe["observed_improvement_after_review"]) > 1:
        body.append("  " + pe["observed_improvement_after_review"][1] + "。")
    for u in pe["unverified_effects"]:
        body.append("- 未验证（未做用户实验）：%s" % u)
    body.append("")
    body.append("## 十、复现")
    body.append("- 最终 DSL：`final.snapshot`；生成脚本 `tmp/20261016T164020-m1/B06/`：`b06_build.py` + `b06_cases_a.py`/`b06_cases_b.py` + 组件 `b06_common.py`（渲染驱动 `render_b06.py`）。")
    body.append("- 渲染：共享客户端 `tmp/20261016T164020-m1/_suite/snapshot_client.py` POST `/snapshot`（2026-10-18/19 实跑，无密钥；明细见 requests.jsonl）。")
    (OUT / c["id"] / "case.md").write_text("\n".join(body) + "\n", encoding="utf-8")
print("case.md x10 written")

# ---------------- 5) portfolio.json / portfolio.md ----------------
titles = {
    "case-01": "开封保质期 PAO 贴纸卡", "case-02": "名义 vs IRR 分期成本长图",
    "case-03": "阶梯电价蓄水池卡", "case-04": "体检参考区间跑道尺",
    "case-05": "一杯奶茶的糖·方块图", "case-06": "取件码驿站行动卡",
    "case-07": "洗涤八符号翻译方图", "case-08": "降水概率点阵图",
    "case-09": "年终奖临界悬崖对照", "case-10": "药盒缩写翻译+棋盘",
}
cases_meta = []
for n, c in enumerate(CASES, 1):
    rows = [r for r in req_rows if ("b06-" + c["id"] + "-") in r.get("request_file", "")]
    cases_meta.append({
        "case_id": c["id"], "problem_id": "P%02d" % n, "title": titles[c["id"]],
        "final_version": "v%d" % c["v"], "size_px": c["size"],
        "medium": c["medium"], "device_context": c["device"],
        "usage_scene": c["stage"], "audience": c["audience"], "watch_goal": c["goal"],
        "pain_point": c["pain"],
        "final_files": {"png": "%s/final.png" % c["id"], "snapshot": "%s/final.snapshot" % c["id"],
                        "md": "%s/case.md" % c["id"]},
        "render_requests": len(rows),
        "render_ok": len([r for r in rows if r["http_status"] == 200]),
        "render_fail": len([r for r in rows if r["http_status"] != 200]),
        "dsl_capabilities": [
            "Positioned/Container 分块纸感构图与网格几何", "CJK Noto + Inter 数字双字体（txt/num 分离）",
            "stadium 胶囊与右对齐数字列", "网格枚举（点阵/格位/棋盘）与 n×m 逐笔摆件",
            "line_thick 多段折线（水位虚线/阈值刻度）", "pill 自估宽、状态色语（正常/边缘/超限、✗/✓）",
        ],
        "plan_standard_results": [{"id": sid, "standard": st, "met": True, "evidence": chk}
                                  for sid, st, chk in c["standards"]],
        "selfcheck_summary": c["selfcheck"],
        "asset_note": "纯 DSL，无嵌入素材；PAO/护理符号为自绘示意并在图内声明",
        "fiction_notice_shown": True,
    })
portfolio = {
    "schema_version": 1, "run_id": RUN, "task_id": "B06", "created_at": NOW,
    "plan_ref": PLAN_REF,
    "asset_policy": "dsl_primary_with_supporting_assets（本题按零嵌入素材执行：全部画面主体为 DSL）",
    "fiction_notice": "十件全部为自主选题、自拟演示口径；无现场调研、无用户实验；政策类口径经检索核实后转述",
    "product": {"name": "日常信息重构十件", "track": "把日常信息难题变成作品（B06）"},
    "cases": cases_meta,
    "curator_note": "十件按「读对一条符号/口径/阈值」为单元组织：符号语法（c01/c07）、价格与概率语义（c02/c03/c08/c09）、体感转译（c05）、行为卡（c06/c10）、读数训练（c04）；媒介与视觉系统逐件独立（贴墙卡/长图/手机屏/平板对照/方图）。",
    "completion_criteria_ref": "plan-v1.md「完成标准」G1–G5 + S1–S10 逐件条目；结果见各 case.md 第六节与 portfolio.plan_standard_results",
    "view_evidence": "共 41 次真实图像查看（5 初版接触表 + 10 件 v3 整幅 + 21 zoom 切片含 c06 复看 + 5 终态接触表）；明细 iterations.jsonl",
    "numeric_baseline": CALCS_REF,
}
(OUT / "portfolio.json").write_text(json.dumps(portfolio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

notes = {
    "case-01": "把 PAO 符号读懂并当场写下开封日",
    "case-02": "0.6% 月费率 ≠ 7.2% 真年化；IRR 13.8%",
    "case-03": "蓄水池三档 + 跨档月 270.60 vs 直觉 249.60",
    "case-04": "四条参考区间跑道尺：把箭头读成「离线多远」",
    "case-05": "50 g=10 块方糖；WHO 25 g 线恰在半杯",
    "case-06": "3-2-1-xxxx → 排/层/号位三步；误区条纠错",
    "case-07": "八符号三要素 + 两条事故翻标对策",
    "case-08": "60% = 100 日里 60 天下雨；带伞阈值条",
    "case-09": "36,001 少拿 2,309；A/B 方案省 2,520",
    "case-10": "qd/tid/a.c./p.c. → 一日药盒棋盘填格",
}
pmd = ["# B06 作品集 · 《日常信息重构》十件（自主选题/演示口径）", "",
       "策展逻辑：十件独立、自成单元，每组解决一类「难理解/难比较/难找到/难行动」的日常信息",
       "——符号语法（c01 PAO / c07 洗涤）· 价格与概率语义（c02 分期 / c03 阶梯电价 / c08 降水 / c09 年终奖）",
       "· 体感转译（c05 糖）· 行为行动卡（c06 取件 / c10 药盒）· 读数训练（c04 体检尺）。",
       "视觉/媒介逐件独立：贴墙卡（A4 近比）×3、手机长图 1、手机竖屏 ×3、平板对照 ×2、方图 1。", "",
       "**证据与声明**：全部为自主选题；证据只含自观察与公开口径转述（无现场调研/用户实验）；",
       "数值经本地计算（研究文件 tmp/20261016T164020-m1/B06/research/calcs.json）；政策口径经检索核实（财政部公告2023年第30号、WHO 2015）后转述。", "",
       "| # | 作品 | 预览 | 要点 |", "|---|---|---|---|"]
for i, c in enumerate(CASES, 1):
    pmd.append("| %d | [%s](%s/final.png) · [DSL](%s/final.snapshot) · [md](%s/case.md) | ![%s](%s/final.png) | %s |" % (
        i, titles[c["id"]], c["id"], c["id"], c["id"], c["id"], c["id"], notes[c["id"]]))
pmd += ["", "逐件说明见各 case.md；证据三分类与「可观改善 vs 未验证效果」见 problem-evidence.json 与 design-review.md。"]
(OUT / "portfolio.md").write_text("\n".join(pmd) + "\n", encoding="utf-8")
print("portfolio.json/md written")

# ---------------- 6) gallery.md ----------------
g = ["# B06 案例画廊 · 十件终图（日常信息重构）", "",
     "自主选题的十个日常信息难题，各做出一件独立完整作品。全部为演示口径（图内自含声明），",
     "无现场调研/用户实验；数字均出自本地计算文件 %s。" % "tmp/20261016T164020-m1/B06/research/calcs.json", ""]
for i, c in enumerate(CASES, 1):
    g += ["## %d · %s（P%02d · %s）" % (i, titles[c["id"]], i, c["size"]), "",
          "![%s](%s/final.png)" % (c["id"], c["id"]), "",
          "- 难题/卡点：%s" % c["pain"],
          "- 媒介/场景：%s · %s" % (c["medium"], c["device"]),
          "- 说明见 [case.md](%s/case.md) · DSL：[%s/final.snapshot](%s/final.snapshot)" % (c["id"], c["id"], c["id"]),
          ""]
(OUT / "gallery.md").write_text("\n".join(g) + "\n", encoding="utf-8")
print("gallery.md written")

# ---------------- 7) snapshot-usage.md ----------------
ok_rows = [r for r in req_rows if r["http_status"] == 200]
fail_rows = [r for r in req_rows if r["http_status"] != 200]
su = ["# B06 Snapshot 使用与留痕", "",
      "## 文档与能力应用（真实取用）",
      "- 本题未新增 HTTP 文档/字体请求（0 条）。ai-guide.md 与 DSL 文档在 B04 期间已实抓（缓存",
      "  `tmp/20261016T164020-m1/B04/renders/`），规约沿用：DSL XML 属性、CJK/Inter 双字体纪律",
      "  （仅纯 ASCII 用 Inter；CJK 用 Noto Sans CJK SC；禁裸 `<`）、每 canvas 首笔全幅底色。",
      "- **本题踩坑（核心）**：v1 按「凭记忆的语法」写成——给 `<Text>` 想象了 x/y/boxWidth 属性、给",
      "  `<Container>` 想象了 left/top/backgroundColor：10 张响应 200 但全部塌左上（不可用化）。",
      "  复核后以 B05 已验证格式重写公共组件（`<Positioned left top width height>` 包",
      "  `<Container width height color borderRadius border>`；`fontStyle=\"BOLD\"`；胶囊字宽估算）。教训入 iterations。",
      "- 组件能力：Positioned/Container/Stack、Text（对齐/加粗/box_w）、Transform matrix（4×4 列主序）、",
      "  line_thick 折线、poly/网格枚举、stadium 胶囊、pill 自估宽、状态色语。", "",
      "## 服务调用",
      "- 渲染 POST /snapshot：39 次（39×200 + 0×失败）。v1（10，版式崩坏留证）→ v2（10，驱动误渲旧格式、",
      "  响应字节与 v1 相同——哈希对比鉴别，不入看图数）→ v3（10，真实语法修复）→ v4（7）→ v5（c02）→ v6（c06）= 39。",
      "- 无字体查询；无 429/超时/Retry-After；密钥零写入。逐请求明细 `tmp/<run>/B06/requests.jsonl`（39 行，",
      "  Server-Timing/requestId 全采）。除渲染 HTTP 外的 2 次 websearch（政策号/WHO 口径）在 tool-usage.jsonl 记录，不重复计请求。", "",
      "## 逐件看图与修改（全部真实打开观察）",
      "**看图 41 次**：5（v1 接触表初判——发现版式崩坏）→ 10（v3 整幅逐件）→ 21（20 张 1:1 放大切片 +",
      " c06 修复后重看 zoom-b）→ 5（终态接触表整卷复审）。",
      "- **修复汇总**：语法格式重写（全件）；c02 三问/页脚下移→再改短句（v4/v5）；c04 层序反转+读数保留（v4）；",
      "  c06 页脚移位→「你的包裹」不压芯片（v4/v6）；c07 三角白底描边（v4）；c08 决策条三行下移（v4）；",
      "  c09 B 列双行（v4）；c10 板标题/步骤两行（v4）。",
      "- **未声称修改**：c01/c03/c05 自 v3 起无缺陷改型（整幅+放大复核通过，避免无意义迭代）。",
      "- 做法依据 B06 AGENTS「看图、迭代与最终审查」：每次成功响应实际打开判断；接触表与放大为工具，不替代整幅查看。", "",
      "## 数值与检索（真实发生）",
      "- 数值唯一基准 `" + CALCS_REF + "`（c02 IRR 月 1.0862%、c03 拆段 270.60、c09 四点税额、c05 50g 换算），本地先算后图。",
      "- 两次 websearch 真实执行（2026-10-18 晚）：政策文件号（财政部/SAT2023-30→2027-12-31）与 WHO 25g；",
      "  核实意见先记 plan v1.1，随后入图。无其他外部检索。", "",
      "## 复现条件",
      "- 生成：`python b06_build.py <后缀>`（如 `_v4`）→ `tmp/<run>/B06/dsl/case-XX[_vN].snapshot`（不可覆盖旧版）。",
      "- 渲染：`python tmp/<run>/_suite/snapshot_client.py render B06 <dsl> <tag> <outdir>`，环境变量",
      "  SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID；响应 200 字节直存 final.png，无后处理。",
      "- 校验：十张终图与本处 events/checkpoints 追加式留痕全齐（events 下一编号由行数推导，不覆盖）。", "",
      "## 最终审查",
      "- 逐件：整幅（v3 起）+ 密集区 1:1 放大 + 终态接触表整卷 + 352 条画面文本抽取校笔（text_dump.txt）。",
      "- G1–G5 与 S1–S10 对照全部通过（明细见各 case.md 第六节、design-review.md）。",
      "- 遗留：无未决缺陷；未验证效果（用户实验类）已在 design-review.md/problem-evidence.json 如实单列；",
      "  asset-sources.json 不设（零嵌入素材，无外部资产引用）。"]
(OUT / "snapshot-usage.md").write_text("\n".join(su) + "\n", encoding="utf-8")
print("snapshot-usage.md written")

# ---------------- 8) design-review.md ----------------
dr = ["# B06 设计复盘（design-review）—— 可观改善 vs 未验证效果", "",
      "> 复查时间口径：**%s**（终态接触表 + 放大切片 + case.md 校笔后收束的固定表述）。" % NOW,
      "> 路径基准：本文位于 `outputs/<run>/B06/`，图片/DSL 链接相对本文目录（例：`case-01/final.png`）；",
      "> 步骤留痕用相对仓库根的 `tmp/...` 路径（遵循 PATHS.md）。",
      "",
      "## 一、逐件判定表（泛观 + 看图后收束）", "",
      "| # | 作品 | 用户原卡在哪（问题的诚实还原） | 重构选择 | **画面可观的可读性改善** | **未经用户实验验证的效果** |", "|---|---|---|---|---|---|"]
judge_rows = [
    ("case-01", "没人教过「6M/12M」是罐底开封期；保质期与开封期被混为一谈", "空间上句→语法卡→可写日期空栏→开封期≠保质期对照",
     "开罐符号+「12M」语义一次读懂；行动区含可填空栏与示例带（[case-01/final.png](case-01/final.png)、zoom-01-a/b）",
     "「写日期习惯能否减用过期品」；月数类目对个人产品的适用度"),
    ("case-02", "0.6% 月费率被直读成 7.2% 年化；余额逐月下降未反映到利率口径",
     "余额柱+固定手续费帽画几何根源；双年化并列（7.2%↔13.8%）+「1.9 倍」胶囊；三问自查卡",
     "12 期流水一屏可读；两个年化差与口径差写在同一图（zoom-02-a/b）",
     "该图能否降低误判；对其他分期结构（不同期数/贴息）不直接适用"),
    ("case-03", "账单看不出身处哪档；跨档月直觉按「单价×用电」算",
     "蓄水池三档剖面（档=层、累计=水位）；算例卡按 60+420 两段拆；直觉 249.6 vs 270.60 对照",
     "三档边界与水位几何可读；算例链可回算（31.20+239.40；差 21.0/+8.4%）",
     "对真实账单是否以同一模型计价（各省不同）；预警效果未验证"),
    ("case-04", "箭头=焦虑；偏差多大要紧无指引", "跑道刻度尺：状态带+示例针+轴+行动注一体；「先量离线多远再记录复查」",
     "四条尺在 1:1 放大下状态/位置/注均清晰；v4 修层序后针不再压字",
     "复查建议的医学合理性；焦虑下降未验证"),
    ("case-05", "几十克糖无体感；WHO 25g 日限无从对照", "杯体糖块实体化（2×5）；WHO 25g 虚线恰在半杯；克/块/千卡/分钟四单位同卡",
     "10 块清点无误；「半杯即达日限」关系直读", "点单决策影响未验证；各店糖量差异以门店为准"),
    ("case-06", "取件码三段语义不明；新手按尾号在货架上找不到格子",
     "三段大号解码卡（排/层/号位）；正视+俯视双视图；误区条+三步行动流",
     "码→格语义与高亮格对应清晰；v6 后「你的包裹」不压芯片（zoom-06-a/b）",
     "首次取件成功率/耗时改善未验证；驿站规则差异以现场为准"),
    ("case-07", "八符号被直译为「小图形」，禁忌（漂白/烘干/干洗）看不出",
     "八格三要素（符号+中文+禁忌）；符号本体放大；两条事故卡（结果→对策）",
     "八格符号+禁忌可读（zoom-07-a/b）；v4 三角描边后深浅对比足够",
     "事故再现率变化未验证；特殊面料仍以洗标原文为准"),
    ("case-08", "降水概率 60% 误读为时间/面积占比；带伞与否凭感觉",
     "100 日点阵（60 蓝+40 空）频数化；三误会修正；0/30/95 阈值决策条",
     "60/100 可清点；三档阈值与用法注可读（zoom-08-a/b）",
     "误读率是否下降未验证；阈值为个人示例"),
    ("case-09", "年终奖临界跳档（36,000/36,001）无人对照；并入 vs 单独没有直给差额",
     "悬崖台阶图（四点+回补点 38,566.67）；两方案对撞卡（5,880 vs 3,360，省 2,520）；口径/时效/差异三重声明",
     "崖差 2,309.10 与两方案差额直读；政策胶囊与免责在图内（zoom-09-a/b）",
     "能否影响实际选择未验证；各档通用性「演示口径，人人不同」"),
    ("case-10", "qd/tid/a.c./p.c. 老人读不懂；隔空叮嘱无效",
     "四行翻译卡（缩写+人话+做法）；一日药盒棋盘（自家四例药入格）；给三步动作不空模板",
     "表格→棋盘对应关系清晰；v4 后板标题/步骤不再被遮断（zoom-10-a/b）",
     "漏服率变化未验证；译义以医嘱与药师为准"),
]
for row in judge_rows:
    dr.append("| %s | %s | %s | %s | %s | %s |" % (
        row[0], titles[row[0]], row[1], row[2], row[3], row[4]))
dr += ["",
       "## 二、全局判定（G1–G5）", "",
       "- **G1 卡点→重构自含**：十件每件内既有「为什么会读错」，又有「拿起怎么用」（写日期/三问/算例/读法/对策），整幅+放大逐件核对通过。",
       "- **G2 数字可复核**：IRR 1.0862%、阶梯 270.60、四点税额、50g 等均由本地脚本先算后图，图上回算一致（calcs.json；text_dump 校笔）。",
       "- **G3 来源与口径内标**：每件页脚「演示数据/演示口径」+ 证据不越权（逐条对照 problem-evidence.json）。",
       "- **G4 目标尺寸可读**：手机件（420/720 宽）以原尺寸/2× 放大切片复核；贴墙件（800/900/1000）以整幅 1:1 复核。",
       "- **G5 十件互独立**：问题/媒介/构图/配色各不相同（接触表横向比较，5 张终态表整卷查看）；同版式仅换字=0。",
       "",
       "## 三、诚实清单",
       "- **不声称做过**：现场调研、用户访谈、A/B 实验、真实部署——任何「有效/降低误读」的断言均未验证。",
       "- **演示口径**：逐件自含（图内声明）；政策/惯例类仅作关键要点转述，未归档完整原文。",
       "- **已接受的轻贴**：c03 算例卡右侧、c09 悬崖注签与容器边缘的丝边距（≤2px，放大确认不裁切）。",
       "- **留证**：v1 全套（200 但版式崩坏）与 v2 驱动误渲响应**未删除**，`tmp/<run>/B06/renders/` 全部保留为过程证据。",
       "",
       "## 四、评审用链接",
       "- 十件索引：[portfolio.md](portfolio.md) · [gallery.md](gallery.md) · 逐件证据：[problem-evidence.json](problem-evidence.json)",
       "- 服务与看图：[snapshot-usage.md](snapshot-usage.md) · [task-metrics.json](task-metrics.json)",
       ]
(OUT / "design-review.md").write_text("\n".join(dr) + "\n", encoding="utf-8")
print("design-review.md written")

# ---------------- 9) task-metrics.json ----------------
first_ok = "2026-10-18T21:22:01+08:00"  # B06-render-0001（case-01 v1 200，started_at）
serve_ms = round(sum(r["duration_ms"] for r in req_rows), 1)
metrics = {
    "schema_version": 1, "task_id": "B06", "run_id": RUN, "created_at": NOW,
    "path_base": "suite_root",
    "wall_clock": {
        "started_at": TASK_START,
        "updated_at": NOW,
        "first_usable_image_at": first_ok,
        "overnight_gap_note": "2026-10-18 21:58（会话暂止）→ 2026-10-19 08:54（用户继续「继续」）的夜间暂停为同一 run 的连续执行断点；末件 c06-v6 于次日晨重渲并复看。墙钟含真实暂停，请求耗时之和不等于总墙钟",
        "last_render_at": req_rows[-1]["ended_at"],
    },
    "requests": {
        "total": len(req_rows), "ok_200": len(ok_rows), "fail": len(fail_rows), "fail_detail": [],
        "serve_ms_total": serve_ms,
        "doc_access": 0, "font_query": 0, "retry_after_wait_ms": 0,
        "websearch_other_tools": 2,
        "note": "v1×10（版式崩坏留证）+ v2×10（驱动误渲、字节与 v1 相同）+ v3×10（语法修复）+ v4×7 + v5×1 + v6×1 = 39，全 200",
    },
    "iterations": {"rows": len(iters), "baseline": kinds.get("baseline", 0),
                   "syntax_fix": kinds.get("syntax-fix", 0),
                   "visual_iteration": kinds.get("visual-iteration", 0),
                   "requirement_change": kinds.get("requirement-change", 0),
                   "final_review": kinds.get("final-review", 0),
                   "note": "syntax_fix 20 行 = v2 无效批 10（字节哈希鉴别、不含看图）+ v3 修复生效批 10（含整幅看图）；"
                           "所有看图时刻尽量锚定文件 mtime/请求台账，同名复存处已在 basis 注明"},
    "image_views": 41,
    "view_ledger": "5（v1 接触表）+ 10（v3 整幅）+ 21（zoom 切片；其中 c06 修复后重看一次）+ 5（终态接触表）；iterations.jsonl 逐行 observed_at/basis",
    "final_cases": 10,
    "final_versions": {c["id"]: "v%d" % c["v"] for c in CASES},
    "cases": [{"case_id": m["case_id"], "render_requests": m["render_requests"],
               "render_ok": m["render_ok"], "render_fail": m["render_fail"]}
              for m in cases_meta],
    "parallel_span": None, "waiting_unknown": None,
    "unfinished": [],
    "suite_handoff": {"final_images_to_suite": 10, "render_quality": "39/39 HTTP 200；整幅+放大+接触表三层复核通过",
                      "problem_evidence": "outputs/<run>/B06/problem-evidence.json",
                      "design_review": "outputs/<run>/B06/design-review.md"},
}
(OUT / "task-metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("task-metrics.json written")
print("DONE finalize_b06_docs")
