# -*- coding: utf-8 -*-
"""B05 收尾文档落盘：case.md×10 + portfolio(json/md) + product-brief.md +
journey.json + gallery.md + snapshot-usage.md + task-metrics.json +
iterations.jsonl + tool-usage.jsonl。全部路径相对（path_base=suite_root 或
本题输出根），不改写 tasks/。"""
import io
import json
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"D:\mine\test\glm-5.3-flash")
RUN = "20261016T164020-m1"
TMP = ROOT / "tmp" / RUN / "B05"
OUT = ROOT / "outputs" / RUN / "B05"
NOW = datetime.now().astimezone().isoformat(timespec="milliseconds")
TASK_START = "2026-10-18T19:33:58+08:00"  # B04 套件收尾时刻，B05 紧随开始

req_rows = [json.loads(ln) for ln in
            (TMP / "requests.jsonl").read_text(encoding="utf-8").strip().splitlines()]


def reqs_of(case_id):
    lines = []
    for r in req_rows:
        if ("b05-" + case_id + "-") in r.get("request_file", ""):
            tag = r["request_file"].replace("\\", "/").split("/")[-1].rsplit("-", 1)[0]
            lines.append("%s（%s，HTTP %d，%s）" % (r["id"], tag, r["http_status"], r["duration_ms"]))
    return "；".join(lines)


REQ_BY_CASE = {("case-%02d" % i): reqs_of("case-%02d" % i) for i in range(1, 11)}

CASES = [
    dict(
        id="case-01", v=3, size="420×960", device="手机 · 深夜（屏内 23:41）",
        scene="住院→居家过渡期，家人在深夜想起：夜里谁来管？能否在 20 秒内把这个担忧变成可执行的机制",
        audience="处于出院过渡期的成年子女（手机端，家人群的主角/协调人）",
        goal="理解「每人一晚，家里不塌」的轮值概念，愿意进入演示建立照护圈",
        content=[
            "品牌区：轮值 LUNZHI + 英文副题 family care, one night shift at a time",
            "夜景主标题：每人一晚 / 家里不塌；副句交代六个断档点",
            "三步概念卡：1 把人放上桌（四人一色码）2 夜晚只剩今晚（22:00 接岗，交接药/翻身/情绪）3 每周日复盘夜",
            "琥珀 CTA：进入演示 · 十屏旅程；页脚演示声明",
        ],
        claims=["深夜蓝底 + 左侧状态灯柱为全刊起始的视觉记忆点",
                "22:00 接岗与交接三件事在 c04/c05 重复出现",
                "每周日复盘夜与 c10「每周日 20:00 · 下次 10-26」一致"],
        standards=[("S1-1", "三步上手段落完整且分「谁/何时/做什么」", "整幅观察：三卡编号+成员口径完整"),
                   ("S1-2", "深夜氛围可感（渐深底+灯柱）", "整幅观察：两段深蓝底、灯柱取琥珀"),
                   ("S1-3", "入口 CTA 明确", "CTA 文案指向演示而非装饰按钮")],
        visual="夜色 v2 起副题固定三行断整句，电池改空心描边+电量块；v3 第 3 步标题改「每周日复盘夜」与 c10 复盘时刻一致",
        selfcheck="v1 看图发现副标断句（断/档跨行）与电池实心难辨 → v2 重排；旅程审查发现「每周一复盘夜」与 c10「每周日 20:00」矛盾 → v3 统一为周日",
        basis="照护协调属常识性家庭场景；机制为自创演示，无真实部署或用户验证",
    ),
    dict(
        id="case-02", v=4, size="420×960", device="手机 · 晨（屏内 09:12）",
        scene="出院翌日清晨，协调人把家人与帮手拉进同一本册子",
        audience="协调人（长子王桁视角）：建圈者，配齐角色与权限",
        goal="五人（患者+四名照护参与者）在一张卡上一眼看清角色、色码与加入状态",
        content=[
            "患者卡：伯 父亲 王伯 · 72 岁 · 髋部术后居家第 5 天（琥珀「康复期」章）",
            "成员四行（色条+圆徽+角色+状态）：王桁 主班 夜 22:00–06:00 已加入；王樾 副班 可改轮值表 已加入；王杳 远程 汇总与提醒 已加入；周阿姨 白班 08:00–20:00 待回执",
            "权限口径：改表 / 只读 / 日班任务；工具不提供医疗建议",
            "CTA：生成 14 天轮值表 →；副注「建圈的人默认为主班；可随时让位」",
        ],
        claims=["四人色码（青/珊瑚/琥珀/灰绿）与 c03/c04/c10 完全一致",
                "周阿姨状态为待回执 → 与其仅白班的分工呼应"],
        standards=[("S2-1", "四成员色码与全刊一致", "整幅对照 c03 图例、c04 夜码、c10 对比条"),
                   ("S2-2", "角色/权限差分可读", "整幅观察：主班/副班/远程/白班四行角色文案"),
                   ("S2-3", "邀请状态各异", "已加入×3 与待回执×1，色分绿/琥珀")],
        visual="v2 将状态胶囊移到行右上、角色缩句防重叠；患者卡姓名拆短；v4 头像改用名末字（伯/桁/樾/杳/周）避免三个「王」无区分",
        selfcheck="v1 看图发现姓名与「康复期」章重叠、成员行角色被胶囊压住 → v2 布局重排；v2 副题右缘截断 → v3 缩句；旅程审查发现头像全为「王」→ v4 改名末字",
        basis="五人全部虚构；医疗归属声明在画面内（工具不提供医疗建议）",
    ),
    dict(
        id="case-03", v=3, size="1180×820", device="平板横排 · 白天（今日 10-18 周六）",
        scene="出院小结（示例）被贴进工具，转译成 6 类任务 × 3 时段 × 责任人的照护分工表，全家在客厅一起过目",
        audience="全家（平板摆在客厅，谁都能看）",
        goal="确认每类任务在夜/日/晚三时段的责任人，理解「本页只做照护分工（演示）」",
        content=[
            "左栏：粘贴 → 分条 → 排上表 三步说明卡 + 「6 类任务 · 3 时段 · 1 按需」+ 同步口径",
            "任务矩阵（6 行）：服药（阿姨 08:00/王樾 21:30）、翻身（夜班 22·02/阿姨 10·14/王樾 18）、步走（阿姨 3 组/家人傍晚）、饮水（计/计/王杳统计）、皮肤（02/10/王杳视频）、情绪（夜班记/王杳电话）",
            "夜列深蓝底、日/晚浅米底；图例「色点=责任人 · 空格=该时段无安排」+ 四人色码",
        ],
        claims=["服药 08:00/21:30 与 c07 用药轴、c05 交接卡同源一致",
                "「演示口径」与「医疗行为交给医护」在画面内声明"],
        standards=[("S3-1", "至少 6 类任务 × 时段 × 责任人码", "矩阵整幅清点：6 行 × 3 时段列"),
                   ("S3-2", "医嘱转译标注演示口径", "卡内第四行与页脚演示声明"),
                   ("S3-3", "平板横排布局", "1180×820，表占右侧主宽")],
        visual="v2 右上日期标签抬高避让表头、左栏卡片重排、夜列统一深蓝底板；v3 修两处断词（自动分条/同步行）",
        selfcheck="v1 看图发现日期章压表头、左栏文字溢卡、细则两行溢出行底 → v2 结构重排；v3 收尾断词",
        basis="出院小结为虚构示例；不出现剂量与真实医嘱文本",
    ),
    dict(
        id="case-04", v=2, size="1180×820", device="平板横排 · 夜（屏内 23:05）",
        scene="今晚 22 点谁值夜？全家在轮值表页确认今晚与未来两晚",
        audience="确认排班的全家；今晚值夜的王桁清楚交接清单",
        goal="一眼确认「今晚 = 王桁（第 4 夜）」与 14 夜的整体分摊",
        content=[
            "顶栏：今晚 22:00–06:00 · 王桁（第 4 夜）+ 琥珀「已值 5 夜」计数",
            "14 夜码带（10-13..10-26）成员色字：桁/樾/杳；今日列珊瑚描边+TODAY；19、25 为双码（樾杳/桁樾）",
            "白班行：白班 5 格 + 周末「休」（周六日不排）",
            "日程周行 13(一)..26(日)，18(六) 珊瑚高亮",
            "今晚卡：王桁 第 4 夜 · 交接三件事（药 21:30 / 翻身 22·02 / 情绪 22:30 巡视）+ 次日 7:30 通勤与 02:00 小睡口径",
            "白班帮手卡：本月白班 5 天 · 周六日不排 · 下月续约排期待定 · 费用进入月度分摊",
        ],
        claims=["已值 5 夜（13..17）= 桁 3 + 樾 2，与 c10 实块总数一致",
                "双夜 19（樾+杳）与 25（桁+樾）逐一对应 v1.1 逐日表"],
        standards=[("S4-1", "14 天网格清晰且今日列高亮", "整幅：14 列码带 + TODAY + 珊瑚列框"),
                   ("S4-2", "夜班色带 22:00–06:00 与成员码一致", "码带用成员色字"),
                   ("S4-3", "周末双人班可视", "19/25 双码格"),
                   ("S4-4", "「今晚=王桁」与 c05 同步", "今晚卡与 c05 接班卡同文")],
        visual="v2 周末日带由「双岗+色条」改为「休」并撤条，与「周六日不排」一致；「排期 open」改「排期待定」",
        selfcheck="v1 看图发现周末日带写「双岗」与白班卡「周六日不排」矛盾 → v2 改为「休」并去色条",
        basis="14 夜逐日排班为虚构演示（plan v1.1 追记为唯一依据）",
    ),
    dict(
        id="case-05", v=2, size="420×960", device="手机 · 黄昏（屏内 18:42）",
        scene="傍晚 18:42，交接卡由白班视角汇总：已完成/超时转补/夜里三要素/接班提醒",
        audience="白天帮手与即将接夜的王桁",
        goal="22:00 前把三要素交接清楚，超时段有转补反馈",
        content=[
            "A 白班清单：钙剂（早餐随餐）✔周阿姨 / 步走 3 组×8 步 ✔周阿姨 / 翻身 ✘超时 → 王樾 19:44 接手；注「超时 1 项已转补：19:44 王樾接手」",
            "B 夜班交接三要素：药 · 21:30 抗凝（示例）床头盒已备 · 王樾衔接；翻身 · 22:00 与 02:00 两次各 5 分钟；情绪入睡 · 22:30 巡视记录一句后即熄灯",
            "C 接班卡（青描边）：王桁 · 22:00 接班 · 第 4 夜 · 提醒已送达 18:31",
        ],
        claims=["翻身 14:00 超时 → 19:44 王樾接手（c06 补位与其呼应）",
                "交接三件事与 c04 今晚卡逐字一致"],
        standards=[("S5-1", "今日三件待办状态互异（含 1 项超时）", "✔/✔/✘ 三态 + 珊瑚红环"),
                   ("S5-2", "夜班交接含药/翻身/情绪三要素", "B 卡三行"),
                   ("S5-3", "18:42 时间指示与状态栏同步", "状态栏与页首同为 18:42")],
        visual="v2 重写 task_row（右列时间/胶囊互斥防重叠）、A 卡行距重排、B 卡「标签:描述」单行制；全局组件层修复",
        selfcheck="v1 看图发现右列胶囊压标签、超时注记与第三行重叠、B 卡两行溢卡 → v2 全面重排并修共享组件",
        basis="转补行为与提醒时刻均为虚构演示数据",
    ),
    dict(
        id="case-06", v=2, size="420×960", device="手机 · 昼末（屏内 18:42）",
        scene="家人群里的照护动态：只增不改，谁补记都留痕（家人端视图）",
        audience="全部家庭成员，重点是补记的远程成员",
        goal="回看今天发生了什么：异常闭环、步走照片、远程统计、补货、接班提醒",
        content=[
            "警示条：17:12 皮肤观察 · 足跟压红 1 度（示例判定）17:14 拍照存档 · 18:00 复查确认消退 · 已闭环",
            "时间线 4 条：17:20 周阿姨 步走 2/3 组（照片卡：步走第 2 组/扶床 8 步/拍照 1 张 · 已入册）；18:05 王杳 远程统计：视频 2 次 ≥ 3 分钟；18:30 王樾 药房补货：钙剂 1 盒（库存已同步）；18:42 系统提醒 王桁 22:00 接班（第 4 夜）",
            "照片卡为 DSL 绘制示意（山形+人物剪影），标注「已入册」",
        ],
        claims=["18:05 王杳远程统计与 c08 待收款提醒同刻但事件互不打扰",
                "18:42 系统提醒与 18:31 送达（c05）同源闭环"],
        standards=[("S6-1", "时间线 ≥4 条且含照片式卡（DSL 绘制）", "4 条 + 照片卡"),
                   ("S6-2", "异常条目珊瑚标注且已闭环", "17:12 条珊瑚+「已闭环」绿点"),
                   ("S6-3", "王桁 22:00 接夜提醒与 c04/c05 一致", "第 4 夜同文")],
        visual="v2 缩短消息防换行溢出、照片卡右文改固定两行；异常条与时间线杆完整",
        selfcheck="v1 看图发现三条消息与下一行/胶囊重叠 → v2 逐一改句并调整纵向推进",
        basis="足跟压红 1 度为示例判定；照片为 DSL 自绘示意图，非实拍",
    ),
    dict(
        id="case-07", v=3, size="420×960", device="手机 · 昼末（屏内 18:42）",
        scene="用药轴：一次按时段的服用状态回看 + 库存倒计时与补货反馈",
        audience="当班家庭成员（谁在家谁核一遍）",
        goal="确认已服/未服，并知道库存还够几天、补货怎么办",
        content=[
            "时刻轴 06/08/12/18/22",
            "药品三行：08:00 钙剂（早餐随餐）已服 08:10 · 周阿姨确认（绿）；12:30 止痛（按需可选）日上限 3 次 · 今天未用（灰）；21:30 晚间抗凝（示例）待服 · 21:30 · 王樾协助（琥珀）",
            "库存卡：钙剂瓶中余 12 片 · 按当前医嘱示例支撑到 10-22；琥珀胶囊「王樾已补 1 盒 · 18:30」；绿点「购物清单 18:31 已自动更新」",
            "底注：补货提醒只跟时点，不写剂量数字",
        ],
        claims=["08:00 已服与 c03/c05 一致；王樾 18:30 补货与 c06 时间线同源",
                "全页无剂量数字（演示转译原则）"],
        standards=[("S7-1", "三次按时段排布且已服/未服分明", "三行绿/灰/琥珀"),
                   ("S7-2", "库存警示（10-22）有建议动作", "补货胶囊+清单更新行"),
                   ("S7-3", "不出现剂量数字", "整幅无剂量，仅「12 片」「1 盒」库存口径")],
        visual="v2 时刻列让位（药名 x150）、m3 归位「晚间抗凝（示例）」；v3 清单行改「18:31 已自动更新」",
        selfcheck="v1 看图发现时刻与药名粘连、m2 标签换行差 → v2 修正；复核发现「购物清单已同步（今晚 18:31）」语义不通 → v3 改述",
        basis="用药示例为虚构转译；非医疗建议（页首声明）",
    ),
    dict(
        id="case-08", v=4, size="1000×1260", device="手机长图 · 晚（屏内 19:02）",
        scene="月末前后清账：本月照护支出总额、四类分解、逐日流水、三人等额分摊与收款状态",
        audience="三名分摊子女（王桁/王樾/王杳）",
        goal="看清每笔钱去哪、谁已付、谁待提醒，导出账目图发群里",
        content=[
            "总额卡：十月合计 1,260 元 · 演示数字声明 · 阿姨不参与分摊",
            "分解条+图例：护理白班 5 天 × 160 = 800；辅具租借 180（助行器 120+防滑垫 60）；往返接送 2 次 × 60 = 120；药品与耗材自购 160",
            "本月流水 6 行：10-13 预付 2 天 320 已结；10-15 辅具 180 已结；10-16 接送 60 已结；10-17 自购 160 已结；10-18 其余白班 3 天合并计 480 已结；10-24 复诊接送 60 预记",
            "三人均摊 × 3 卡：各 420 元；王桁已收 10-16、王樾已收 10-17、王杳待收款 · 已提醒 18:05（琥珀描边）",
            "CTA 导出账目图 · 发到家人群；隐私注「群外不存账目截图」",
        ],
        claims=["1,260 = 800+180+120+160；流水 5 结 1 预合计对平",
                "已收 2 笔/待收 1 笔与分摊声明一致"],
        standards=[("S8-1", "总额与四类分解一致", "图上逐项及分解条观察"),
                   ("S8-2", "三人等摊 420 可视", "三卡数值"),
                   ("S8-3", "转账状态可视", "已结×2 与待收款描边")],
        visual="v2 把「元」移出 Inter 字体（num→txt）、数值列右对齐加框；v3 流水卡加高防裁切、下移分摊区；v4 头像改末字",
        selfcheck="v1 看图发现「元」混入 Inter 字体 → v2 拆分；放大核验发现流水第 6 行被卡底裁切 → v3 加高重排；旅程审查发现头像三个「王」→ v4 修正",
        basis="金额全部虚构演示；记账行为为示意",
    ),
    dict(
        id="case-09", v=5, size="900×1200", device="A4 纸印 · 白天",
        scene="10-24 拆线复诊前，家人打印 A4 出行卡贴冰箱：必带件、当天节奏、路线示意",
        audience="明早送诊的王樾 + 全家可见（冰箱贴/复印）",
        goal="出门一趟带齐清单，节奏不漏",
        content=[
            "虚撕线（锯齿）+ 四角磁贴 + 「出门时可撕下带走」",
            "标题：10-24 周五 · 拆线复诊 · 贴冰箱出行卡 · 复印给有需要的人",
            "必带清单 3/5 已备：照护本（出院小结+当前页）✔ / 医保卡 ✔ / 家属身份证 1 份 ✔ / 水杯+药盒（晚间抗凝示例）○ / 打印本页 ○",
            "预办节奏：07:50 王樾开车出门（油量已看）→ 08:10 楼下接父亲走无障碍坡道 → 09:40 骨科 B2 取号（提前 15 分钟）→ 10:10 拆线+复查建议 → 11:30 回程取钙剂（07 页清单）",
            "路线示意（顺序，非真实道路）：家（出门拍一览）→ 车（零拥挤上下车）→ 停 B2（无障碍电梯）→ 骨科 B2（提前 15 分取号）→ 回家（先躺 30 分钟）",
            "底条虚线段：轮值 · 打印这张卡 → 贴冰箱；医疗声明 + A4 比例（210×280 mm 版面）示意",
        ],
        claims=["11:30 回程取钙剂引用 07 用药页（跨屏跳转一致）",
                "停 B2 与骨科 B2 为科室楼层示意，非真实道路"],
        standards=[("S9-1", "清单含必带与预办两类", "左右两卡"),
                   ("S9-2", "路线/时间轴示意且不写真实道路", "显式声明非真实道路"),
                   ("S9-3", "A4 版面可打印（撕裂线+磁贴）", "锯齿撕线+四角磁贴")],
        visual="v2 border DASHED 语法改 SOLID 并以 18 段短线绘虚线感；v3 步骤句缩短、路线备注单行化；v4 修「复印给可以有需要的人」病句；v5 步骤行距收紧并上移出画磁贴、补「车」字",
        selfcheck="v1 渲染 400（border 不支持 DASHED）→ 语法修 v2；看图发现备注重叠、末步溢卡底 → v3/v5 处理；文案病句 → v4",
        basis="地名/楼层（B2）为示意；全部为演示出行",
    ),
    dict(
        id="case-10", v=3, size="1180×820", device="平板横排 · 夜（屏内 19:58）",
        scene="周日 20:00 前的深夜复盘：夜岗计数对比、谁太累、调班建议与确认流",
        audience="四名照护参与者（复盘检视会）",
        goal="15 分钟内看清夜岗是否偏累，确认或调换下周安排",
        content=[
            "对比条（14 天夜岗计划 · 已值/待值）：王桁 3 实 + 3 空 = x6；王樾 2 + 4 = x6；王杳 0 + 4 = x4（琥珀空框 · 远程）",
            "图例与口径行：实块=已值夜；空块=待值夜；王杳的 4 夜均为远程（视频陪聊+电话巡视）；周阿姨只排白班不计夜岗",
            "调班建议卡：观察（桁已值 3 夜 13/15/17，今晚第 4；22 与 25 还排 2 晚）→ 建议 10-25 双人夜改王樾+王杳，桁远程待命 → 夜数 6 → 5，周两头仍双人",
            "确认流：19:58 建议生成（琥珀）→ 已同步王桁（待确认，琥珀）→ 王樾 19:58 表态：可以（绿）",
            "底部三卡：每周日 20:00 自动生成下周表 / 复盘只 15 分钟 / 下次复盘 10-26（周日）20:00",
            "底注：复盘不改医嘱，只改『谁值夜』；改完立即推送本轮四人",
        ],
        claims=["实块总数 3+2=5 与 c04「已值 5 夜」一致",
                "建议生效后桁 5 / 樾 6 / 杳 5（v1.1 逐日表）"],
        standards=[("S10-1", "对比条已值/待值与 c04 计数一致", "实块 5 与页右「已值 5 夜」互证"),
                   ("S10-2", "调班给出明确交换对象", "樾+杳替桁，桁远程"),
                   ("S10-3", "确认流状态完整", "生成→同步→表态三步")],
        visual="v2 已值口径按 v1.1 修正（桁 3 实 + 今晚第 4），观察句同改；v3 修正王樾表态时序（19:56→19:58）与下次复盘日期（10-25 周六误 → 10-26 周日）",
        selfcheck="旅程审查发现「已值 4 夜」把今晚计入已值，与 c04/c05 矛盾 → v2 修正；复核发现王樾表态早于建议生成、下次复盘落在周六 → v3 双修",
        basis="复盘为演示流；周两头改调口径来自 v1.1 追记",
    ),
]

FOOTNOTE = "轮值 LUNZHI · 演示数据 · 虚构人物 · 仅示意照护协调"
PLAN_REF = "tmp/20261016T164020-m1/B05/plan-v1.md（v1 + v1.1 + v1.2 追记，建立于首次渲染前）"

# ---------------- 1) case.md ×10 ----------------
for c in CASES:
    body = ["# %s · 《轮值》第 %s 屏（屏序 %d/10）" % (c["id"], c["id"].split("-")[1], int(c["id"][5:]))]
    body.append("")
    body.append("> 《轮值 LUNZHI》家庭照护协调工具 · 虚构演示作品集之一 · 终版 v%d" % c["v"])
    body.append("> 素材性质：**虚构演示**——人物/日期/金额/用药均为示例，画面与平台不提供医疗建议；未做真实用户验证，不声称实际部署。")
    body.append("")
    body.append("## 一、场景与受众")
    body.append("- **受众**：%s" % c["audience"])
    body.append("- **使用场景**：%s" % c["scene"])
    body.append("- **希望用户完成的事**：%s" % c["goal"])
    body.append("- **观看环境/设备**：%s（像素 %s）" % (c["device"], c["size"]))
    body.append("")
    body.append("## 二、内容（与画面逐项对应）")
    for b in c["content"]:
        body.append("- %s" % b)
    body.append("")
    body.append("## 三、事实基线（claims 范围）")
    body.append("- 跨屏锚点（10-18 周六 · 居家第 5 天；已值 5 夜=桁3+樾2；今晚=王桁第 4 夜；费用 1,260=800+180+120+160 各摊 420；用药 08:00/12:30/21:30）统一见 %s。" % PLAN_REF)
    for k in c["claims"]:
        body.append("- %s" % k)
    body.append("- 本页不承载超出上述口径的引语/数据；页内已标「演示数据 · 虚构人物」。")
    body.append("")
    body.append("## 四、发布意图")
    body.append("作为十屏旅程的第 %d 屏参与完整演示叙事；单独转发亦可独立说明该环节机制，隐私口径（如 c08 群外不存图）与角色权限在画面内交代。" % int(c["id"][5:]))
    body.append("")
    body.append("## 五、视觉要点")
    body.append("- %s" % c["visual"])
    body.append("- 全刊视觉系统：深夜蓝/米白纸感昼夜交替 + 左侧状态灯柱 + 四人成员色码；页脚声明「%s」。" % FOOTNOTE)
    body.append("")
    body.append("## 六、完成标准与实际检查")
    body.append("计划版本：%s" % PLAN_REF)
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
    body.append("- 纯 DSL 构成（asset_policy=dsl_primary_with_supporting_assets；本题未嵌入任何外部素材，理由：全部画面主体为信息界面）。照片式占位（c06）与撕线/磁贴（c09）均为 DSL 绘制，图内如实标注示意。")
    body.append("")
    body.append("## 九、复现")
    body.append("- 最终 DSL：`final.snapshot`；生成脚本 `tmp/20261016T164020-m1/B05/`：`b05_build.py` + `b05_cases_a.py`/`b05_cases_b.py` + 组件库 `b05_common.py`。")
    body.append("- 渲染：共享客户端 `tmp/20261016T164020-m1/_suite/snapshot_client.py` POST `/snapshot`（2026-10-18 实跑，无密钥；明细见 requests.jsonl）。")
    (OUT / c["id"] / "case.md").write_text("\n".join(body) + "\n", encoding="utf-8")
print("case.md x10 written")

# ---------------- 2) journey.json ----------------
journey = {
    "schema_version": 1,
    "run_id": RUN,
    "task_id": "B05",
    "product": {"name": "轮值 LUNZHI",
                "one_liner": "住院→居家过渡期的家庭夜班轮值法：每人一晚，家里不塌",
                "fiction_notice": "全部人物/机构/日期/金额/用药为虚构演示；未做真实用户验证"},
    "actor_legend": {"王桁": "青 · 主班（长子）", "王樾": "珊瑚 · 副班", "王杳": "琥珀 · 远程",
                     "周阿姨": "灰绿 · 白班帮手", "王伯": "患者 72 岁",
                     "状态灯": "绿=完成/正常 · 琥珀=进行/待办 · 珊瑚=超时/需要关注"},
    "steps": [
        {"n": 1, "case_id": "case-01", "when": "过渡期深夜", "moment": "23:41",
         "article": "引入：把「谁值夜」装进一个机制", "entry": "独立转发可看；CTA 进演示",
         "next_transition": "点击「进入演示 · 十屏旅程」"},
        {"n": 2, "case_id": "case-02", "when": "出院后次日晨", "moment": "09:12",
         "article": "建圈：五个人的角色、权限与加入状态", "entry": "主班=建圈者，可让位",
         "next_transition": "点「生成 14 天轮值表」"},
        {"n": 3, "case_id": "case-03", "when": "出院小结到场", "moment": "白天",
         "article": "转译：医嘱（示例）→ 6 类任务 × 3 时段 × 责任人",
         "next_transition": "任务排上表后进入日常"},
        {"n": 4, "case_id": "case-04", "when": "每晚固定看板", "moment": "23:05",
         "article": "轮值表：今晚=王桁第 4 夜；14 夜与白班一张表",
         "next_transition": "22:00 前到 c05 完成交接"},
        {"n": 5, "case_id": "case-05", "when": "傍晚交接", "moment": "18:42",
         "article": "今日三件事 + 夜班交接三要素 + 接班提醒",
         "next_transition": "交接写入 c06 时间线"},
        {"n": 6, "case_id": "case-06", "when": "动态回看", "moment": "18:42",
         "article": "异常闭环/照片/远程统计/补货/系统提醒",
         "next_transition": "发现库存余量 → c07"},
        {"n": 7, "case_id": "case-07", "when": "用药核查", "moment": "18:42",
         "article": "服用状态三点位 + 库存 12 片 → 10-22 + 补货反馈",
         "next_transition": "月末清账 → c08"},
        {"n": 8, "case_id": "case-08", "when": "月度清账", "moment": "19:02",
         "article": "1,260 = 四类分解；三人各 420，2 已收 1 待收",
         "next_transition": "事件做准备 → c09 出行卡"},
        {"n": 9, "case_id": "case-09", "when": "复诊前夜备/当日出行", "moment": "白天",
         "article": "A4 撕下贴冰箱：必带 5 件 + 当天节奏 + 路线示意",
         "next_transition": "周日晚 20:00 → c10 复盘"},
        {"n": 10, "case_id": "case-10", "when": "周日复盘", "moment": "19:58",
         "article": "夜岗计数（桁3+3/樾2+4/杳0+4）→ 建议改 10-25 夜班 → 确认流",
         "next_transition": "确认后回到 c04 生效新表，闭环"},
    ],
    "consistency_anchors": [
        "今天 10-18（周六）· 居家第 5 天；入院 10-08 · 手术 10-09 · 出院 10-13",
        "已值 5 夜：桁 3（13/15/17）+ 樾 2（14/16）；今晚（18）王桁第 4 夜",
        "14 夜原排：桁 6 / 樾 6 / 杳 4（19、25 双人）；建议后桁 5 / 樾 6 / 杳 5",
        "费用 1,260=800+180+120+160；三兄妹各 420；已收 2 待收 1（杳，提醒 18:05）",
        "用药：08:00 钙剂已服 08:10（阿姨）；12:30 止痛按需未用；21:30 抗凝示例待服（王樾协助）；库存 12 片 → 10-22；18:30 王樾补 1 盒",
        "交接三件事：药 21:30 / 翻身 22·02 / 情绪 22:30（c04/c05 逐字一致）",
        "复盘：每周日 20:00；下次 10-26；只改『谁值夜』",
    ],
    "boundary": "journey 为演示叙事（无真实用户）；c09 为 A4 比例示意的物理产物入口",
}
(OUT / "journey.json").write_text(json.dumps(journey, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(TMP / "journey.json").write_text(json.dumps(journey, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("journey.json written (outputs + tmp)")

# ---------------- 3) product-brief.md ----------------
brief = ["# 《轮值 LUNZHI》产品简报（虚构演示）", "",
         "> 版本 v1 · 2026-10-18 · run：%s · 计划：%s" % (RUN, PLAN_REF),
         "> **素材性质**：产品、人物（王桁/王樾/王杳/周阿姨/父亲王伯）、日期、金额、用药条目全部虚构；",
         "> 页面与平台不提供医疗建议（各屏内含声明）；未做真实用户验证，不声称实际部署。", "",
         "## 1. 用户问题",
         "住院→居家的过渡期是家庭照护最容易断档的窗口：出院小结只写医嘱不写「今晚谁守夜」；",
         "家人群里接力发消息容易漏；白班阿姨的活和夜班的家看不见彼此；复查要带什么没人汇总；",
         "钱花在哪、谁该出一笔常常要起争执；一个月后「谁太累了」没人敢说。", "",
         "## 2. 产品方案（一句话）",
         "**「每人一晚，家里不塌」的夜班轮值法**：把六个断档点装进一本可比对的册子——",
         "建圈（谁在桌上）→ 转译（医嘱变任务）→ 轮值表（今晚是谁）→ 交接卡（三件事）→",
         "动态时间线（已发生）→ 用药轴（吃没吃+还剩几天）→ 费用分摊（谁付清）→",
         "出行卡（打印贴冰箱）→ 周日复盘（谁太累了，谁接上）。", "",
         "## 3. 十屏与旅程（前后关系）", "",
         "| # | case | 画面 | 时段 | 承接 → 推进 |", "|---|---|---|---|---|"]
tbl = [
    (1, "case-01", "着陆概念（夜）", "23:41", "— → 进入演示"),
    (2, "case-02", "建圈（晨）", "09:12", "演示入口 → 生成 14 天轮值表"),
    (3, "case-03", "出院照护转译表（平板·白天）", "10-18", "建圈后 → 任务排上表进日常"),
    (4, "case-04", "十四天轮值表（平板·夜）", "23:05", "每晚看板 → 22:00 前 c05 交接"),
    (5, "case-05", "今日交接卡（手机·黄昏）", "18:42", "交接 → 写入 c06 时间线"),
    (6, "case-06", "动态时间线（手机）", "18:42", "回看 → 发现库存余量 → c07"),
    (7, "case-07", "用药轴与库存（手机）", "18:42", "服用+余量 → 月度 c08"),
    (8, "case-08", "费用与分摊（长图）", "19:02", "清账 → 事件准备 c09"),
    (9, "case-09", "复诊出行卡（A4 印刷）", "白天", "出行 → 周日 c10 复盘"),
    (10, "case-10", "周报与调班（平板·夜）", "19:58", "确认调班 → 回到 c04 生效，闭环"),
]
brief += ["| %d | %s | %s | %s | %s |" % row for row in tbl]
brief += ["", "详图与逐步字段见 journey.json（steps/actor_legend/consistency_anchors）。", "",
          "## 4. 机制要点（为什么这套编排可信）",
          "- **夜里的事最需要「唯一责任人」**：14 夜每夜一个（或周末两个）明确人码，",
          "  交接只看三件事（药/翻身/情绪），降低交接成本。",
          "- **白班与远程同样可见**：阿姨只白班；杳远程（视频陪聊+电话巡视）也计入夜岗，复盘时「排进表里」才公平。",
          "- **状态有反馈**：超时 14:00 翻身 → 19:44 转补给王樾（c05 注记 + c06 补位）；收款待付 → 18:05 提醒（c08）。",
          "- **非医疗边界**：转译只到「何时/谁/重复」颗粒度；剂量不出现在任何屏。",
          "- **物理入口**：A4 出行卡是唯一非屏成果——因为复诊那天的厨房冰箱才是真实使用现场。", "",
          "## 5. 视觉系统",
          "- **昼夜交替**：深夜蓝（c01/c04/c10）与米白纸感（其余）随使用时段切换。",
          "- **左侧状态灯柱**：每屏 3px 色带（绿/琥珀/珊瑚）承担「这一屏给你什么状态」的第一眼语义。",
          "- **成员色码**：王桁 青 / 王樾 珊瑚 / 王杳 琥珀 / 周阿姨 灰绿，贯穿 c02..c10。",
          "- **核心物件**：轮值表在 c03（矩阵）/ c04（14 夜网格）/ c10（夜岗对比）三处延展同一信息。", "",
          "## 6. 假设与验证边界",
          "- 假设：四人家庭（三兄妹+阿姨）结构、出院髋部术后第 5 天、复盘周日 20:00 可达成共识。",
          "- 未做的事：没有真实用户访谈/可用性测试/A-B 对比；数字为口径自洽的演示数据。",
          "- 局限：屏际「自动同步」仅以画面叙述表达，未实现前端运行程序（TASK 允许静态呈示）。", "",
          "## 7. 画面与数据合规",
          "- 每屏页脚「轮值 LUNZHI · 演示数据 · 虚构人物 · 仅示意照护协调」。",
          "- c03/c07 明示「示例转译/非医疗建议」；c08 明示「演示数字」「群外不存账目截图」。", "",
          "## 8. 交付物与复现",
          "- 十屏最终图/DSL/说明：`case-01/`…`case-10/`（final.png + final.snapshot + case.md）。",
          "- 作品集：`portfolio.json` / `portfolio.md`；旅程：`journey.json`；画廊：`gallery.md`。",
          "- 服务与留痕：`snapshot-usage.md` / `task-metrics.json`；过程：`tmp/<run>/B05/`。"]
(OUT / "product-brief.md").write_text("\n".join(brief) + "\n", encoding="utf-8")
print("product-brief.md written")

# ---------------- 4) portfolio.json / portfolio.md ----------------
titles = {
    "case-01": "着陆概念「每人一晚，家里不塌」(420×960 夜)",
    "case-02": "建立照护圈：角色与权限", "case-03": "出院照护转译表",
    "case-04": "十四天轮值表(平板夜)", "case-05": "今日交接卡",
    "case-06": "照护动态时间线", "case-07": "用药轴与库存",
    "case-08": "十月费用与三人均摊", "case-09": "复诊出行卡(A4)",
    "case-10": "周报与调班复盘",
}
cases_meta = []
for c in CASES:
    rows = [r for r in req_rows if ("b05-" + c["id"] + "-") in r.get("request_file", "")]
    cases_meta.append({
        "case_id": c["id"], "title": titles[c["id"]], "final_version": "v%d" % c["v"],
        "size_px": c["size"], "device_context": c["device"],
        "usage_scene": c["scene"], "audience": c["audience"], "watch_goal": c["goal"],
        "final_files": {"png": "%s/final.png" % c["id"], "snapshot": "%s/final.snapshot" % c["id"],
                        "md": "%s/case.md" % c["id"]},
        "render_requests": len(rows),
        "render_ok": len([r for r in rows if r["http_status"] == 200]),
        "render_fail": len([r for r in rows if r["http_status"] != 200]),
        "dsl_capabilities": ["Positioned/Container 布局与分块底色", "CJK/Inter 双字体系统",
                             "line_thick/poly_rows（撕线、连线）", "hill_rows（照片示意）",
                             "task_row/statusbar/pill/lamp 组件化"],
        "plan_standard_results": [{"id": sid, "standard": st, "met": True, "evidence": chk}
                                  for sid, st, chk in c["standards"]],
        "selfcheck_summary": c["selfcheck"],
        "asset_note": "纯 DSL，无嵌入素材；c06 照片为 DSL 自绘示意并标注「示意照」",
        "fiction_notice_shown": True,
    })
portfolio = {
    "schema_version": 1, "run_id": RUN, "task_id": "B05", "created_at": NOW,
    "plan_ref": PLAN_REF,
    "asset_policy": "dsl_primary_with_supporting_assets（本题按零嵌素材执行：主体与全部构成均为 DSL）",
    "fiction_notice": "全部人物/机构/数据虚构；未做真实用户验证；医疗类内容为示例转译，不提供医疗建议",
    "product": {"name": "轮值 LUNZHI", "track": "从零构想产品（B05）"},
    "cases": cases_meta,
    "curator_note": "十屏按「引入→配置→日常循环(轮值/交接/动态/用药)→月度账→事件(出行)→复盘」编成一条可信的照护旅程；视觉以昼夜交替与成员色码统一。",
    "completion_criteria_ref": "plan-v1.md「完成标准」G1–G5 + S1–S10 逐屏条目（每屏 3–4 条），全部逐条对照实际图检查；结果见各 case.md 第六节与 cases.plan_standard_results",
    "view_evidence": "共 33 次真实图像查看（含终态五张接触表整卷复审、每屏整幅、密集区放大），明细见 iterations.jsonl",
}
(OUT / "portfolio.json").write_text(json.dumps(portfolio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

notes = {
    "case-01": "深夜着陆；三个上手段：把人放上桌 / 夜晚只剩今晚 / 每周日复盘夜",
    "case-02": "五人色码与权限差分；周阿姨待回执",
    "case-03": "医嘱（示例）→ 6 类任务 × 3 时段；夜列深底",
    "case-04": "14 夜网格定标；今晚=王桁第 4 夜；已值 5 夜",
    "case-05": "白班清单 ✔✔✘ + 夜班交接三要素 + 接班提醒",
    "case-06": "异常闭环（足跟压红）/照片卡/补货/提醒",
    "case-07": "08:00 已服 / 12:30 按需 / 21:30 待服 + 12 片 → 10-22",
    "case-08": "1,260 = 800+180+120+160；各 420；2 结 1 待",
    "case-09": "A4 撕角出行卡：必带 3/5 + 节奏 + 路线示意",
    "case-10": "夜岗对比条（桁3+3/樾2+4/杳0+4）+ 调班建议确认流",
}
pmd = ["# B05 作品集 · 《轮值》十屏（虚构演示）", "",
       "策展逻辑：十屏=一条照护旅程。引入(c01) → 建圈(c02) → 转译(c03) → 日常循环",
       "(c04 轮值表 / c05 交接 / c06 动态 / c07 用药) → 月度账(c08) → 事件出行(c09) →",
       "周复盘(c10) 回到轮值表，闭环。视觉记忆点：深夜蓝/米白纸感昼夜交替 + 左侧状态灯柱",
       "+ 四人成员色码（桁青/樾珊瑚/杳琥珀/阿姨灰绿）。", "",
       "**虚构声明**：人物、日期、金额、用药全部为演示；未做真实用户验证；不提供医疗建议。", "",
       "| # | 用例 | 成品预览 | 要点 |", "|---|---|---|---|"]
for i, c in enumerate(CASES, 1):
    pmd.append("| %d | [%s](%s/final.png) · [DSL](%s/final.snapshot) · [md](%s/case.md) | ![%s](%s/final.png) | %s |" % (
        i, titles[c["id"]], c["id"], c["id"], c["id"], c["id"], c["id"], notes[c["id"]]))
pmd += ["", "逐件说明见各 case.md；旅程与一致性锚点见 journey.json 与 product-brief.md。"]
(OUT / "portfolio.md").write_text("\n".join(pmd) + "\n", encoding="utf-8")
print("portfolio.json/md written")

# ---------------- 5) gallery.md ----------------
g = ["# B05 画廊 · 十屏终图（《轮值》昼夜书写）", "",
     "产品：《轮值 LUNZHI》家庭照护协调工具（虚构演示）。以下为十屏最终图，",
     "按使用旅程顺序排列。图内页脚均含「演示数据 · 虚构人物」声明。", "",
     "旅程与 journey 对应：c01 引入 → c02 建圈 → c03 转译 → c04/c05/c06/c07 日常循环",
     "→ c08 月度账 → c09 事件出行 → c10 复盘。", ""]
for i, c in enumerate(CASES, 1):
    g += ["## %d · %s" % (i, titles[c["id"]]), "",
          "![%s](%s/final.png)" % (c["id"], c["id"]), "",
          "- 尺寸/场景：%s · %s" % (c["size"], c["device"]),
          "- 说明见 [case.md](%s/case.md) · DSL：[%s/final.snapshot](%s/final.snapshot)" % (c["id"], c["id"], c["id"]),
          ""]
(OUT / "gallery.md").write_text("\n".join(g) + "\n", encoding="utf-8")
print("gallery.md written")

# ---------------- 6) snapshot-usage.md ----------------
su = ["# B05 Snapshot 使用与留痕", "",
      "## 文档与能力应用（真实取用）",
      "- 本题未新增 HTTP 文档/字体请求（0 条）。B04 期间已实抓 ai-guide.md 与 DSL 文档（缓存存于",
      "  `tmp/20261016T164020-m1/B04/renders/`，引用不重复计请求）；规约直接沿用：DSL XML 属性、",
      "  CJK/Inter 双字体纪律（仅纯 ASCII 用 Inter；CJK 用 Noto Sans CJK SC；禁裸 `<`）、",
      "  border 枚举仅 NONE/SOLID——本题 v1 再次实际踩坑（见下）、每 canvas 首笔全幅底色。",
      "- 组件能力：Positioned/Container、Text（对齐/加粗/box_w）、line_thick、poly_rows（锯齿撕线）、",
      "  hill_rows（c06 照片示意）、task_row/pill/lamp/statusbar（B04 已验证组件复用 + 本题扩展）。", "",
      "## 服务调用",
      "- 渲染 POST /snapshot：32 次（30×200 + 2×400）。400 均为 case-09 border `1.x DASHED`：",
      "  服务枚举只有 NONE/SOLID，与 B04 的 border 踩坑同因（枚举常量不会自动放行）。",
      "  失败响应原样留痕：`tmp/<run>/B05/renders/b05-case-09-v1-195341586.resp` 与",
      "  `b05-case-09-v2-195427607.resp`（后者为渲染驱动回退到旧版 DSL 所致，教训入 iterations）。",
      "- 无字体查询请求；无 429/超时；密钥零写入。逐请求明细 `tmp/<run>/B05/requests.jsonl`（32 行）。", "",
      "## 逐件看图与修改（全部真实打开观察）",
      "- 看图 33 次：v1 五张接触表（10 屏初判）→ v2 批重排（9 屏重渲+复看）→ 密集区放大 5 张 →",
      "  c02/c03/c10 微调 → c08 流水卡裁切（放大捕捉）→ v3 加高复看 → c02 v4/c08 v4 整幅 →",
      "  旅程级文案 4 屏修正（c01/c07/c09/c10）复看 → c09 v5 整幅 → 终态五张接触表整卷复审（旅程连贯性）。",
      "- 修复汇总：右列重叠（c02/c05）、消息纵向溢出（c06）、字体误植（c08 元字 inter）、",
      "  日期章压表头（c03）、周末口径矛盾（c04）、「元/分摊」流水对平（c08）、卡片裁切（c08/c09）、",
      "  出画磁贴与行距（c09）、跨屏一致性 6 处（复盘日 / 已值口径 / 表态时序 / 下次复盘日期 / 清单时间语义 / 复印病句）。",
      "- 做法依据 AGENTS.md「看图、迭代与最终审查」：每次成功响应实际打开判断，接触表仅工具不替代整幅查看。", "",
      "## 复现条件",
      "- 生成：`python b05_build.py <后缀>`（如 `_v2`）→ `tmp/<run>/B05/dsl/case-XX[-vN].snapshot`。",
      "- 渲染：`python tmp/<run>/_suite/snapshot_client.py render B05 <dsl> <tag> <outdir>`，",
      "  环境变量 SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID；响应 200 字节直存 final.png，无后处理。", "",
      "## 最终审查",
      "- 逐屏整幅 + 终版接触表双重过目；旅程连贯性（流程/时刻/色码/数据一致性）通过。",
      "- 遗留事项：无；asset-sources.json 不设（零外部素材）。"]
(OUT / "snapshot-usage.md").write_text("\n".join(su) + "\n", encoding="utf-8")
print("snapshot-usage.md written")

# ---------------- 7) iterations.jsonl ----------------
S = "tmp/20261016T164020-m1/B05/steps/"
T1 = "2026-10-18T19:57:00+08:00"   # v1 接触表复看（估：文件其后按同名复存）
T2 = "2026-10-18T20:10:07+08:00"   # v2 批接触表

def it(case, ver, parent, kind, observed, basis, obs, before=None, after=None):
    return {"case_id": case, "version": ver, "parent_version": parent, "kind": kind,
            "observed_at": observed, "observed_basis": basis, "observation": obs,
            "before_image": before, "after_image": after, "path_base": "suite_root"}

iters = []
# 基线（v1 首看，接触表）
iters += [
    it("case-01", "v1", None, "baseline", T1, S + "sheet-1.png（同名文件其后被 v2 复存）", "首版：副标断句跨行、电池实心难辨"),
    it("case-02", "v1", None, "baseline", T1, S + "sheet-1.png（同上）", "患者名与康复期章重叠；成员角色被胶囊压住"),
    it("case-03", "v1", None, "baseline", T1, S + "sheet-2.png（同上）", "日期章压表头；左栏溢卡；细则溢行底；夜列无底色"),
    it("case-04", "v1", None, "baseline", T1, S + "sheet-2.png（同上）", "周末日带「双岗」与「周六日不排」矛盾；排期 open 混杂"),
    it("case-05", "v1", None, "baseline", T1, S + "sheet-3.png（同上）", "task_row 右列压标签；超时注记重叠；三要素溢出"),
    it("case-06", "v1", None, "baseline", T1, S + "sheet-3.png（同上）", "消息两/三条与下一行重叠；照片右文断词"),
    it("case-07", "v1", None, "baseline", T1, S + "sheet-4.png（同上）", "时刻与药名粘连；m2 标签换行差"),
    it("case-08", "v1", None, "baseline", T1, S + "sheet-4.png（同上）", "「元」混入 Inter；数值列与灯位偏挤"),
    it("case-09", "v1", None, "syntax-fix", "2026-10-18T19:53:45+08:00", "requests.jsonl B05-render-0009", "渲染 400：border 值 DASHED 不在服务枚举（NONE/SOLID）"),
    it("case-10", "v1", None, "baseline", T1, S + "sheet-5.png（同上）", "版式通过；已值口径矛盾在旅程级阶段捕获"),
]
# c09 v2（语法修复 200）
iters.append(it("case-09", "v2", "v1", "syntax-fix", "2026-10-18T19:55:30+08:00",
                "requests.jsonl B05-render-0011(400 误用旧文件) / 0012(200)",
                "border 改 1.5 SOLID + 18 段短线绘虚线感；期间一次驱动回退旧 DSL 得 400，留痕后以 v2 文件重渲成功"))
# v2 批（9 条 visual：c01..c08 v2 + c09 v3 路线修复）
v2_notes = {
    "case-01": "副标改整句三行；电池改空心描边+电量块",
    "case-02": "患者卡名拆短+胶囊上位；成员角色缩句防重叠",
    "case-03": "日期章抬高避让表头；左栏四行制；夜列统一深色底板",
    "case-04": "周末改「休」并撤色条；排期 open → 排期待定",
    "case-05": "task_row 组件重写（右列互斥）；A/B/C 卡重排",
    "case-06": "照片右文固定两行；消息句子缩短防溢出",
    "case-07": "时刻列让位；标签单行制",
    "case-08": "「元」拆出 Inter；数值右对齐加框；流水补「其余白班 3 天合并计」对平",
}
for cs, note in v2_notes.items():
    iters.append(it(cs, "v3" if cs == "case-09" else "v2", "v1", "visual-iteration", T2,
                    S + "sheet-*.png（v2 批接触表）", "看图(v1/400) → 修改 → 重渲 → 复看(v2)：\n" + note))
# 放大核验与 v3/v4
iters += [
    it("case-02", "v3", "v2", "visual-iteration", "2026-10-18T20:16:22+08:00",
       S + "zoom-c02-member.png", "复看发现副题右缘截断 → 缩句「髋部术后居家第 5 天」", after=S + "zoom-c02-member.png"),
    it("case-03", "v3", "v2", "visual-iteration", "2026-10-18T20:17:30+08:00",
       S + "zoom-c03-left-v3.png", "「自动分条」/「改动同步」断词修除；matrix 放大核验夜列与色点（v2 态）", after=S + "zoom-c03-left-v3.png"),
    it("case-09", "v3", "v2", "visual-iteration", "2026-10-18T20:10:07+08:00",
       S + "sheet-5.png（v2 批）", "路线备注重叠与末步溢卡 → 缩句单行；放大核验通过"),
    it("case-08", "v3", "v2", "visual-iteration", "2026-10-18T20:16:22+08:00",
       S + "zoom-c08-posts.png", "放大发现流水第 6 行被卡底裁切 → 卡加高 210→236、分摊区下移 26px", after=S + "zoom-c08-posts-v3.png"),
    it("case-10", "v2", "v1", "requirement-change", "2026-10-18T20:17:30+08:00",
       S + "zoom-c10-bars-v2.png", "「已值 4 夜」与 c04/c05 矛盾（把今晚计入已值）→ 依 plan v1.1 改桁 3 实块 + 观察句同改", after=S + "zoom-c10-bars-v2.png"),
    it("case-02", "v4", "v3", "requirement-change", "2026-10-18T20:16:22+08:00",
       S + "zoom-c02-member-v4.png", "头像三名「王」无区分 → 改名末字（伯/桁/樾/杳/周）", after=S + "zoom-c02-member-v4.png"),
    it("case-08", "v4", "v3", "requirement-change", None, "case-08/final.png（v4 整幅）", "c08 同一头像问题 → 改末字；整幅复看通过", after="outputs/20261016T164020-m1/B05/case-08/final.png"),
]
# 旅程级文案审查（4 屏）+ c09 v5
jour = "旅程级整体审查（终态接触表整卷）"
iters += [
    it("case-01", "v3", "v2", "requirement-change", None, jour, "「每周一复盘夜」与 c10「每周日 20:00」矛盾 → 改周日；整幅复看通过"),
    it("case-07", "v3", "v2", "requirement-change", None, jour, "「购物清单已同步（今晚 18:31）」语义不通 → 改「18:31 已自动更新」；整幅复看通过"),
    it("case-09", "v4", "v3", "requirement-change", None, jour, "「复印给可以有需要的人」病句 → 改「复印给有需要的人」；复看通过"),
    it("case-10", "v3", "v2", "requirement-change", None, jour, "王樾表态 19:56 早于建议生成 19:58（因果倒置）；下次复盘 10-25 为周六 → 19:58 表态、10-26（周日）；整幅复看通过"),
    it("case-09", "v5", "v4", "visual-iteration", None, "case-09/final.png（v5 整幅）", "步骤行距 74→70 避让卡底边；底部磁贴 1164→1108 纠出画；路线补「车」字；整幅复看通过", after="outputs/20261016T164020-m1/B05/case-09/final.png"),
    it("all", "final", None, "final-review", NOW, S + "sheet-1..5.png（终态）",
       "终态五张接触表整卷复审（33 次看图收束）：旅程连贯、跨屏一致、无遮挡裁切；10/10 通过"),
]
(TMP / "iterations.jsonl").write_text(
    "\n".join(json.dumps(x, ensure_ascii=False) for x in iters) + "\n", encoding="utf-8")
kinds = {}
for x in iters:
    kinds[x["kind"]] = kinds.get(x["kind"], 0) + 1
print("iterations.jsonl rows:", len(iters), kinds)

# ---------------- 8) tool-usage.jsonl ----------------
tools = [
    ("py_compile", "b05_common/cases_a/cases_b/build/sheets 语法自查", "tmp/<run>/B05/*.py", "构建前", "all cases"),
    ("b05_build.py", "十屏 DSL 生成（v1 批与 _v2 批；后缀防覆盖旧版）", "tmp/<run>/B05/dsl/*", "两次批 + 若干定向小版本", "all cases"),
    ("snapshot_client.render/snapshot", "共享客户端真实服务渲染 + 请求/响应留痕", "tmp/<run>/B05/requests.jsonl, renders/", "32 次渲染", "all cases"),
    ("render_b05.py", "批渲染驱动（响应→输出 case 目录 final 落盘）", "tmp/<run>/B05/render_b05.py", "v1 批 + c09 v2", "all cases"),
    ("b05_sheets.py(PIL)", "五张双联接触表（看图工具；不替代整幅查看）", "tmp/<run>/B05/steps/sheet-*.png", "三轮生成", "10 cases"),
    ("PIL crop", "密集区局部放大 9 张（02/03/04/08×2/10×2）", "tmp/<run>/B05/steps/zoom-*.png", "放大核验与裁切捕捉", "c02/c03/c04/c08/c10"),
    ("extract_text.py", "final.snapshot 文本抽取（与 case.md 校笔）", "tmp/<run>/B05/text_dump.txt", "跨屏一致性审查", "10 cases"),
    ("finalize_b05_docs.py", "交付文档/指标/台账落盘（本脚本）", "outputs/<run>/B05/*", "收尾", "all cases"),
]
tus = [{"id": "B05-tool-%04d" % (i + 1), "task_id": "B05", "tool": name, "purpose": purpose,
        "input": inp, "context": ctx, "at": NOW, "affects": aff, "http_request_ref": None,
        "path_base": "suite_root"} for i, (name, purpose, inp, ctx, aff) in enumerate(tools)]
(TMP / "tool-usage.jsonl").write_text(
    "\n".join(json.dumps(x, ensure_ascii=False) for x in tus) + "\n", encoding="utf-8")
print("tool-usage.jsonl rows:", len(tus))

# ---------------- 9) task-metrics.json ----------------
first_ok = "2026-10-18T19:53:16+08:00"  # B05-render-0001（case-01 v1 200）
ok_rows = [r for r in req_rows if r["http_status"] == 200]
fail_rows = [r for r in req_rows if r["http_status"] != 200]
metrics = {
    "schema_version": 1, "task_id": "B05", "run_id": RUN, "created_at": NOW,
    "path_base": "suite_root",
    "wall_clock": {"started_at": TASK_START, "updated_at": NOW,
                   "first_usable_image_at": first_ok,
                   "note": "以 B04 套件收尾时刻为连续执行起点（同一 run 连续作业）；updated_at 随最终审查落盘；单题内各屏穿插进行，请求耗时之和不等于总墙钟"},
    "requests": {"total": len(req_rows), "ok_200": len(ok_rows), "fail": len(fail_rows),
                 "fail_detail": [{"id": r["id"], "status": r["http_status"],
                                  "tag": r["request_file"].replace("\\", "/").split("/")[-1].rsplit("-", 1)[0]}
                                 for r in fail_rows],
                 "serve_ms_total": round(sum(r["duration_ms"] for r in req_rows), 1),
                 "doc_access": 0, "font_query": 0, "retry_after_wait_ms": 0},
    "iterations": {"rows": len(iters),
                   "baseline": kinds.get("baseline", 0),
                   "visual_iteration": kinds.get("visual-iteration", 0),
                   "syntax_fix": kinds.get("syntax-fix", 0),
                   "requirement_change": kinds.get("requirement-change", 0),
                   "final_review": kinds.get("final-review", 0),
                   "note": "baseline=v1 接触表首看；同路径复看估时已标 basis；500 类无"},
    "image_views": 33,
    "view_ledger": "iterations.jsonl 之 observed_at；接触表同名复存导致早期 mtime 被 v2 覆盖，估时刻已在各行 basis 注明",
    "final_cases": 10,
    "final_versions": {c["id"]: "v%d" % c["v"] for c in CASES},
    "cases": [{"case_id": m["case_id"], "render_requests": m["render_requests"],
               "render_ok": m["render_ok"], "render_fail": m["render_fail"]}
              for m in cases_meta],
    "parallel_span": None,
    "waiting_unknown": None,
    "unfinished": [],
}
(OUT / "task-metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("task-metrics.json written")
print("DONE finalize_b05_docs")
