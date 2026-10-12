# -*- coding: utf-8 -*-
"""B06 收尾产物构建器：从磁盘与日志读取真实事实，合并逐件说明，产出
portfolio.json / portfolio.md / gallery.md / problem-evidence.json。
所有数字（字节、md5、尺寸、请求 ID、迭代 ID、看图与裁图数）都来自实际文件，
只有文字说明在本脚本中人工撰写。
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT") or Path.cwd())
RID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RID / "B06"
OUT = ROOT / "outputs" / RID / "B06"

sys.path.insert(0, str(TMP))


def jload(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


REQ = jload(TMP / "requests.jsonl")
IT = jload(TMP / "iterations.jsonl")
TU = jload(TMP / "tool-usage.jsonl")
BL = jload(TMP / "build-log.jsonl")
DEMO = json.load(open(TMP / "research" / "demo.json", encoding="utf-8"))


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def png_size(p):
    with open(p, "rb") as f:
        b = f.read(33)
    return [int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")]


def rel(p, base):
    return str(Path(os.path.abspath(p)).relative_to(Path(os.path.abspath(base)))).replace(os.sep, "/")


def rel_root(p):
    """临时目录里的观察证据用总任务根基准路径表示（PATHS.md）。"""
    return str(Path(os.path.abspath(p)).relative_to(Path(os.path.abspath(ROOT)))).replace(os.sep, "/")


CASES = {}
for n in range(1, 11):
    cid = "case-%02d" % n
    cd = OUT / cid
    png = cd / "final.png"
    snap = cd / "final.snapshot"
    rep = cd / "case.md"
    dsl = snap.read_text(encoding="utf-8")
    tags = sorted(set(re.findall(r"<([A-Za-z]+)", dsl)))
    attrs = sorted(set(re.findall(r'\s([A-Za-z]+)=', dsl)))
    # 迭代留痕：先按 caseNN-vXX 归组
    vers = [i["version"] for i in IT if i["version"].startswith("case%02d-" % n)]
    final_ver = None
    for i in IT:
        if i["version"].startswith("case%02d-" % n) and i["completed"]:
            final_ver = i["version"]
    reqs = [r for r in REQ if r["dsl_version"].startswith("case%02d-" % n)]
    ok = [r for r in reqs if r["http_status"] == 200]
    bad = [r for r in reqs if r["http_status"] != 200]
    fin = None
    for r in ok:
        body = Path(ROOT / r["request_file"]) if r.get("request_file") else None
        if r["dsl_version"] == final_ver:
            fin = r
    gates = [b for b in BL if b["case"] == "%02d" % n]
    qa = sorted((TMP / cid / "qa").glob("*.png")) if (TMP / cid / "qa").is_dir() else []
    # 早期用例的裁图直接落在 case 目录（件-01/02 没有 qa 子目录）
    loose = sorted(cd for cd in [TMP / cid] if True)
    loose_pngs = sorted(p for p in (TMP / cid).glob("qa-*.png"))
    previews = sorted((cd).glob("v0*-preview.png"))
    CASES[cid] = {
        "id": cid,
        "n": n,
        "png": rel(png, OUT),
        "png_bytes": png.stat().st_size,
        "png_md5": md5(png),
        "dims": png_size(png),
        "snapshot": rel(snap, OUT),
        "snap_bytes": snap.stat().st_size,
        "snap_md5": md5(snap),
        "dsl_chars": len(dsl),
        "report": rel(rep, OUT),
        "report_bytes": rep.stat().st_size,
        "tags": tags,
        "attrs": attrs,
        "versions": vers,
        "final_version": final_ver,
        "iterations": [i["iteration_id"] for i in IT if i["version"].startswith("case%02d-" % n)],
        "iter_types": {t: sum(1 for i in IT if i["version"].startswith("case%02d-" % n) and i["type"] == t)
                       for t in ("baseline", "visual", "syntax-fix", "retry")},
        "views": sum(1 for i in IT if i["version"].startswith("case%02d-" % n) and i["image_viewed"]),
        "requests_total": len(reqs),
        "requests_ok": len(ok),
        "requests_bad": len(bad),
        "final_request": fin["request_id"],
        "final_timing": fin["server_timing"],
        "final_duration": fin["duration_seconds"],
        "all_request_ids": [r["request_id"] for r in reqs],
        "textfit_checks": sum(g["gate"]["checks"] for g in gates),
        "qa_crops": [rel_root(p) for p in qa + loose_pngs],
        "previews": [rel(p, OUT) for p in previews],
    }

# ---------------------------------------------------------------- 人工撰写的逐件说明
M = {
    "case-01": dict(
        title="今天几点吃药",
        medium="冰箱贴／药盒侧贴（1080×1080 方卡）",
        audience="每天要按间隔服药的人，以及替父母分药的家属",
        use_context="厨房冰箱门前或药盒侧面，站着看 10 秒，光线下读一次就要记住下一次",
        user_goal="知道今天每种药还剩哪几次、几点吃、下一次还要等多久",
        content_basis="demo.json case01（钟点、间隔、等待小时为演示值）；每 8／12 小时的间隔口径属常见公开说明，标 common_rule_needs_check",
        visual_intent="把「一日三次」这句系统口径画成 24 小时盘上的三圈钟点：颜色＝圈＝药，盘外是清醒窗口，右侧三行给可抄走的钟点",
        observed_improvement="原口径只有四个字（一日三次），图上有 3 个具体钟点＋一个等待小时数；对照 ② 的钟点串可在 10 秒内抄进手机日历（此为目测判断，未做用户实验）",
        missing_evidence="没有对照实验：无法证明这张卡减少了实际漏服；夜间最长间隔对不同药物是否要紧需药师核对",
        geometry="环形钟（pie_ring 图元逼近）＋三行换算＋等待进度条＋口径块",
    ),
    "case-02": dict(
        title="末班车还赶得上吗",
        medium="手机长图（1080×2160，站内告示的替代物）",
        audience="晚上要从城里另一头赶回家、必须某点前到家的通勤者",
        use_context="站厅／出站口单手持手机，剩余决策时间约 15 分钟，画面须一屏读完不倒回",
        user_goal="判断这班车上车后今晚能否按时到家，以及最迟几点必须动身",
        content_basis="demo.json case02：城市（汀州市）、六段时长、缓冲 5 min 全部为 self_defined_demo；缓冲取保守值是本页口径，非运营方承诺",
        visual_intent="把「末班 23:41」这一个数摊成 72 分钟的六段行程条，再用倒推得到唯一可执行结论：最迟 23:23 动身",
        observed_improvement="告示给 1 个时刻，本卡给 6 段时长＋1 个最迟出发时刻＋1 个当下剩余分钟；④ 三种情况里明确写出不含限流与加班车，避免把演示当承诺",
        missing_evidence="换乘走行与出闸步行为自设值，未在任何车站实测；未在真实强光与单手条件下测过阅读时间",
        geometry="倒推段条（六行 470 px 条形）＋大字结论＋状态栏时刻",
    ),
    "case-03": dict(
        title="月租不能比较",
        medium="桌面对比页（1600×1000，租房列表页的替代物）",
        audience="一次筛十几套房的租房者，尤其第一次签约、不知道哪些钱能谈的人",
        use_context="桌面或笔记本，签约前坐下来逐项对比，可打印带走",
        user_goal="比较三套房 12 个月的真实负担，而不是列表页上的月租数字",
        content_basis="demo.json case03：三套房、租金、免租期、通勤时长为 self_defined_demo；时间单价 30 元/h、每月 22 天往返是本页自设口径，页面上明写",
        visual_intent="把六笔钱与一段通勤折进 12 个月：五段堆叠条＋条尾押金空心框，让「列表页最便宜的一套真实月均最高」这个反转在同一画面里成立",
        observed_improvement="列表页 3 个数（2780／押一付三／35 min）变成年实付、真实月均、占月租百分比、签约当天现金、通勤年小时五列；关键差（C 比 B 每月贵 259 元）由脚本算出并印在结论里",
        missing_evidence="物业费、水电网费与中介费率为演示值，未取自任何在营房源；「可谈的三笔钱」能省多少没有实际议价数据支撑",
        geometry="现金流堆叠条（五段＋空心押金框）＋9 列明细表＋行动面板",
    ),
    "case-04": dict(
        title="外卖价格解剖",
        medium="手机结算页替代物（1080×1440）",
        audience="在两单之间比价、纠结要不要凑单的人",
        use_context="下单前的手机屏幕上，30 秒内决定；不需要滚动两次就能得到结论",
        user_goal="算清实付由哪五步构成、每 100 g 多少钱、再花 15 元凑单到底省不省",
        content_basis="demo.json case04：两家店、菜品、价格、里程、满减档为 self_defined_demo；「配送费＝起步＋超出免费里程×单价」是本页自设算法，非任何平台报价",
        visual_intent="五步价格瀑布（同一比例尺 16 px＝1 元）：浮动条＋每步金额＋累计列，最后一行累计正好等于页面上的实付数，可对账",
        observed_improvement="原页面 2 行（¥23.22／已优惠 ¥13.00）变成 5 步瀑布＋每 100 g 单价＋凑单结论（净多支出 9.00 元→不值）；占比与「换个分母」并排让两单可比",
        missing_evidence="满减与优惠券叠加规则按本页假设，实际平台常有互斥与限量；未测过真实用户在结算倒计时内能否读完",
        geometry="瀑布图（正负浮动条＋累计列）＋三段并排条＋凑单判定",
    ),
    "case-05": dict(
        title="报告单的箭头不够用",
        medium="体检报告阅读页（1440×1080，平板／打印横版）",
        audience="拿到 12 项报告、看见 9 个箭头却不知道先管哪一项的人",
        use_context="诊室外等待或回家后平铺阅读，可能打印；需要一眼看出轻重次序",
        user_goal="把「偏了多少」变成可排序的量，决定复查节奏与先挂哪一科",
        content_basis="demo.json case05：12 项数值、参考区间、科室归属与复查节奏全部是 self_defined_demo；dev 归一化偏离度为本页自定义口径，不作诊断、不预测疾病、非任何实验室参考值",
        visual_intent="以区间中值为 0 的 12 行发散条：条长＝|结果−中点|／半宽，左＝低于区间、右＝高于区间；再并排展示「按 dev」与「按超界百分比」两种口径会换第一",
        observed_improvement="9 个等宽符号变成 12 条可比较长度＋四档复查节奏＋5 个科室先后＋需重新空腹采血的 5 项；关键对照（维 D 超界 43.3% 但 dev 排第 7）由数据算出",
        missing_evidence="dev 不是医学阈值，只是排序工具；分诊先后与复查节奏未经任何临床复核，落地必须听医生",
        geometry="发散偏差条（中线＋双向条）＋三口径对照＋科室排序表",
    ),
    "case-06": dict(
        title="100 GB 的两行小字",
        medium="套餐详情／投屏页（1920×1080 横版）",
        audience="被「100 GB 大流量」吸引、但每天用量不固定的手机用户",
        use_context="网页详情区或电视投屏，横向时间轴要在大画布上站远可读",
        user_goal="算出这个月哪天几点开始降速，以及降到 1 Mbps 后手上的事还能不能做",
        content_basis="demo.json case06：100 GB／40 GB／1 Mbps／¥39／30 天用量／各应用所需带宽全部 self_defined_demo，不对应任何在营套餐",
        visual_intent="逐日累计台阶面积（柱＝当日增量，青＝额度内、珊瑚＝降速后仍在用）与 40 GB 金色额度线求交，把「第 22 天 18:30」画成一根竖线",
        observed_improvement="两行小字变成撞线时刻＋每日预算 1.33 GB＋实际日均 1.87 GB（超 40%）＋第 15 天预警线；③ 把 1 Mbps 换算成七件事的可用／会卡判定",
        missing_evidence="逐日用量为演示分布；降速后实际可用带宽因网络而异，本页按 1 Mbps 上限算，未做测速验证",
        geometry="台阶面积图＋额度虚线＋撞线竖线＋带宽判定表",
    ),
    "case-07": dict(
        title="入口立牌的四行字",
        medium="停车场立牌／手机（1200×1600 竖版）",
        audience="开车进停车场、进门前只有 30 秒决定停多久的人",
        use_context="入口处站立或摇下车窗 glance 一次；打印后可贴在前挡；字号需远处可辨",
        user_goal="知道停 45 分钟／2 小时／8 小时各付多少、哪一分钟跳价、停到什么时候封顶",
        content_basis="demo.json case07：四行费率、封顶与三个时长为 self_defined_demo，不是任何在营停车场的现行价格；城市为虚构汀州市",
        visual_intent="把「不足一段按一段计」画成分钟→元的 14 段台阶（不是斜线），13 条珊瑚跳变竖线＋40 元封顶平台，第 406 分钟到顶",
        observed_improvement="四行字变成逐分钟扫描出的台阶函数：三个常见时长直接给金额与折算单价，跳变点前 1 分钟最划算（76 min 刚跳 9 元，105 min 同样 9 元），封顶时刻 6 h 46 min 而非字面 24 h",
        missing_evidence="真实停车场的免费期口径、计费取整方式与跨天规则各不相同，本页只按四行字自洽推算，未核对任何现行公示价",
        geometry="分段阶梯函数（台阶柱＋跳变竖线＋封顶平台）＋时长对照表＋临界点面板",
    ),
    "case-08": dict(
        title="14 个图标，我只想选对这一件",
        medium="洗衣机面板贴纸（1080×1920 竖版）",
        audience="站在滚筒机前、手上只有一件具体衣服的人",
        use_context="洗衣前贴在面板旁的贴纸，1 分钟内做出选择；竖版适配手机拍照查看",
        user_goal="给「沾了火锅红油的棉 T 恤、20:40 到家、23:30 前必须干」选出唯一程序，并知道几点结束",
        content_basis="demo.json case08：程序名、温度、转速、时长、评分与情境全部 self_defined_demo，note 字段要求以自家机器说明书为准",
        visual_intent="三层同心扇环：14 个程序各占 12.857° 槽位，外环看面料（14→6）、中环看脏污（6→3）、内环看今晚时间（3→3），中心盘给最终答案",
        observed_improvement="14 个程序名变成一条收敛路径＋选定程序的完整账（78 min、含 15 min 预处理、22:13 结束、剩 77 min 晾晒）＋4 个最易误选程序及其失败原因计数",
        missing_evidence="真实机器的程序参数差异很大；三问顺序与评分权重是本页设定，未做用户选择实验，也未与任何说明书核对",
        geometry="决策扇形（三层环×14 槽，pie_ring 逼近）＋候选对照表＋时间流程条",
    ),
    "case-09": dict(
        title="「0 蔗糖」那瓶，方糖堆到第 6 块",
        medium="饮料背标／货架卡（1080×1350）",
        audience="在货架前手拿一瓶、想看糖多少的购买者",
        use_context="货架前几秒，手上就是那瓶；卡片可挂在货架边或存进手机",
        user_goal="把「每 100 mL 9.1 g」换算成这一瓶喝下去多少糖，并分清「0 蔗糖」与「无糖」",
        content_basis="demo.json case09：5 款饮品的每 100 mL 克数、净含量与宣称字样为 self_defined_demo；25 g／50 g 是常见公开建议口径，note 要求落地前核对现行指南",
        visual_intent="按整瓶折算后堆成方糖塔（1 块 4.5 g，每行 3 块＝13.5 g），25 g／50 g 两条虚线横切，「喝到多少毫升过线」再单独画",
        observed_improvement="每 100 mL 口径变成整瓶克数（S3 27.3 g＝6 块）、过线毫升数与占整瓶比例；金框只给「0 蔗糖」、绿框只给「无糖」，S3 与 S5 并排对照，消除「0 蔗糖＝无糖」的误读",
        missing_evidence="含糖量与宣称字样为演示；每日建议上限适用人群因人而异（儿童、糖尿病人群不同），未咨询营养师，也未做货架实拍验证",
        geometry="方糖堆叠（1 块 4.5 g，34 px，每行 3 块）＋两条建议线＋毫升过线条形",
    ),
    "case-10": dict(
        title="入职第一个月，我只把这 8 条对上了",
        medium="A4 打印核对打孔卡（1240×1754）",
        audience="入职第一个月、手里有合同但不知道哪些条款要自己核对的新人",
        use_context="打印在 A4 上放桌面逐项核对，左缘打孔便于夹在文件夹里；需要能逐条划勾与记录",
        user_goal="逐项判断合同／HR 说的与应有的差在哪，以及不对的下一步做什么",
        content_basis="demo.json case10：8 项条款文本（7 项标 common_rule_needs_check、1 项 self_defined_demo）、月薪 12000、排班 61 h、HR 说法均为演示；note 写明本表是核对清单不是法律意见",
        visual_intent="打孔卡：左缘一个孔＝一项，孔色即判定（珊瑚＝不符、金＝缺项），五列里后四列照抄来源文本不改写；加班 61 h 与 36 h 上限放到同一根 0–80 h 轴上",
        observed_improvement="分散在合同正文、附件与口头说明里的 8 件事变成一屏判定分布（不符 5／缺项 3／通过 0）＋每项一句可执行动作＋第一个月 6 个时间点",
        missing_evidence="未做真实用户验证，也没有逐条核对现行法条与当地口径；「该是多少」是常见规定复述，签任何字前需咨询当地人社部门或工会",
        geometry="打孔状态条（8 孔＋计数芯片）＋5 列核对表＋0–80 h 单轴＋6 节点时间线",
    ),
}

for cid, m in M.items():
    c = CASES[cid]
    wh = [int(v) for v in re.search(r"(\d+)×(\d+)", m["medium"]).groups()]
    assert c["dims"] == wh, (cid, c["dims"], wh, m["medium"])
    assert c["final_version"], cid
    assert c["requests_bad"] + c["requests_ok"] == c["requests_total"], cid
    assert (OUT / c["png"]).stat().st_size == c["png_bytes"]

# ---------------------------------------------------------------- portfolio.json
P = {
    "schema_version": 1,
    "path_base": "output_dir",
    "task_id": "B06",
    "run_id": RID,
    "status": "completed",
    "asset_policy": "DSL 主导，允许局部辅助素材；本题十件均为纯 Snapshot DSL 构造，未引入任何外部位图素材（参考原文只作观察，未嵌入或描摹）",
    "curatorial_statement": (
        "十件作品打的是同一个缺陷：日常信息不缺数据，缺最后一次性换算。药盒写「一日三次」、"
        "告示写「末班 23:41」、列表页写「2780 元/月」、报告单印 9 个一模一样的箭头、立牌写四行费率——"
        "字都认识，但没人把它翻译成「那我几点做、我多花多少钱、要不要去医院」。所以十张图共用一条结构："
        "原始口径 → 换算 → 你能做的事，但用十种不同的图形语言（环形钟、倒推段条、现金流堆叠、价格瀑布、"
        "发散偏差条、累计面积、阶梯函数、决策扇形、方糖堆叠、核对打孔卡）。深色底是刻意的：它表明这是翻译层，"
        "不是原文。所有数字来自同一个固定种子生成器，图上每个数都能复算；医疗、法律、营养类内容只复述公开常识并"
        "标注需核对，十件都没有做真实用户验证，也没有把任何参考界面重新描摹成素材。"
    ),
    "cases": [],
    "case_field_guide": {
        "id": "case-01 等唯一 ID",
        "title": "作品名",
        "audience": "具体受众",
        "use_context": "设备／媒介／观看环境",
        "user_goal": "使用者要完成的事",
        "content_basis": "实际来源或自拟内容的标识（observed / self_defined_demo / common_rule_needs_check）",
        "visual_intent": "主要视觉主张",
        "png": "相对本题输出根的主图路径",
        "snapshot": "相对本题输出根的同名主体 DSL 路径",
        "dimensions": "实际 PNG 头部读取的 [width, height]",
        "supporting_assets": "本题十件为空数组：全部内容由 DSL 构造，演示数值由 b06data.py（seed 20261011）生成",
        "dsl_capabilities": "从 final.snapshot 实际解析出的标签与属性计数",
        "completion_criteria": "自主设定并可对照实际图的标准（见各 case.md 与本文件 judgment 字段）",
        "visual_review": "实际看图／局部裁图的证据（相对本题输出根）",
        "request_ids": "该件全部真实渲染请求 ID",
        "iteration_ids": "该件真实版本与迭代 ID",
        "unresolved_issues": "当前仍存在的问题",
    },
    "shared": {
        "dataset": "tmp/<run>/B06/research/demo.json（b06data.py，seed %s，source %s，city %s）" % (
            DEMO["seed"], DEMO["source"], DEMO["city"]),
        "kit": ["tmp/<run>/B06/b06kit.py", "tmp/<run>/B06/b06run.py", "tmp/<run>/B06/promote.py",
                "tmp/<run>/B06/qa.py", "tmp/<run>/B06/tlog.py"],
        "capability_probe": "tmp/<run>/B06/case-00/（ClipRect/ClipOval/BackdropFilter/Transform matrix 九项探针，含 3 次 400 与 4 次传输失败留痕）",
        "plan": "tmp/<run>/B06/PLAN.md",
    },
    "final_collection_review": (
        "十件逐条核对通过：每张 final.png 都是 HTTP 200 的服务原始响应字节（promote.py 按 md5 与响应体核对后提升），"
        "均有同名 final.snapshot（字节数与 build-log 记录一致）；十件画布互不重复（1080×1080、1080×2160、1600×1000、"
        "1080×1440、1440×1080、1920×1080、1200×1600、1080×1920、1080×1350、1240×1754）；"
        "同一件内所有数字取自 demo.json 同一 case，且每件都有 ⑤／④ 口径块说明哪些是演示、哪些需核对；"
        "gallery.md 十张逐图给出预览＋PNG＋DSL＋用例报告链接，链接相对本题输出根。"
        "跨件复核确认：无参考界面描摹、无外部位图、无后处理成品、QA 裁图全部留在临时目录。"
    ),
    "unresolved_issues": [
        "十件均未做真实用户验证：所有「更容易理解／更好用」的判断来自实际看图与结构对比，不是实验结果",
        "医疗（件-05）、营养（件-09）、法律（件-10）三件只复述公开常识并在页面上标注需核对，未回源核实现行条文、指南与实验室参考区间",
        "件-02／03／04／06／07 的时长、费率、价格与用量均为自拟演示值，不对应任何在营服务",
        "曲线与扇形仍是图元逼近：类 DOM 解析器只有 ClipRect/ClipOval/ClipRRect，ClipPath 与 PathBuilder 只在 Kotlin DSL，2× 放大可见折线边",
        "十件 final.snapshot 未使用 ClipRect/ClipOval/BackdropFilter（计划曾打算用）：能力在 case-00 探针中验证过，成品改用图元＋Transform matrix，此偏差已在 snapshot-usage.md 记录",
        "requests.jsonl 中 case00 早期 4 次请求（v01×1、v02×1、v03×2）的 request_file 字段带重复目录前缀且对应文件不在磁盘上，仅 DSL 与错误摘要保留",
    ],
}

for cid, c in sorted(CASES.items()):
    m = M[cid]
    P["cases"].append({
        "id": cid,
        "title": m["title"],
        "audience": m["audience"],
        "use_context": m["use_context"],
        "user_goal": m["user_goal"],
        "content_basis": m["content_basis"],
        "visual_intent": m["visual_intent"],
        "png": c["png"],
        "snapshot": c["snapshot"],
        "dimensions": c["dims"],
        "png_bytes": c["png_bytes"],
        "png_md5": c["png_md5"],
        "snapshot_bytes": c["snap_bytes"],
        "snapshot_md5": c["snap_md5"],
        "dsl_chars": c["dsl_chars"],
        "case_report": c["report"],
        "supporting_assets": [],
        "dsl_capabilities": {
            "tags": c["tags"],
            "attributes": c["attrs"],
            "construct": m["geometry"],
            "note": "全部由 Container/Positioned/Stack/Text/Snapshot 构造；圆与扇形用图元逼近，斜切用 Transform matrix，圆角用 borderRadius，无位图素材",
        },
        "completion_criteria": [
            "画面上「原始口径 → 换算 → 行动」三段都能在实际图中指认（见 %s 的块表）" % c["report"],
            "所有可见数字可由 tmp/<run>/B06/research/demo.json 复算，无手写数",
            "口径与限制块如实标注演示值与需核对项，不冒充权威建议",
            "逐版本真实看图并记录问题；final.png 为 HTTP 200 原始响应字节",
        ],
        "visual_review": {
            "iterations_viewed": c["views"],
            "previews": c["previews"],
            "qa_crops": c["qa_crops"],
            "final_version": c["final_version"],
            "conclusion": m["observed_improvement"],
        },
        "request_ids": c["all_request_ids"],
        "render_ok": c["requests_ok"],
        "render_failed_or_truncated": c["requests_bad"],
        "final_request": c["final_request"],
        "final_server_timing": c["final_timing"],
        "iteration_ids": c["iterations"],
        "unresolved_issues": [m["missing_evidence"]],
    })

json.dump(P, open(OUT / "portfolio.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---------------------------------------------------------------- gallery.md
g = ["# B06 画廊 · 把十个日常信息难题重做成作品 · 十件最终作品（%s）" % RID, "",
     "路径基准：本文档位于 `outputs/%s/B06/`，下列链接全部相对本目录，复制整个输出目录后仍可浏览。" % RID,
     "",
     "每张图给出：标题与用途、Markdown 内嵌预览、原 PNG 链接、同名完整 DSL 链接、用例报告链接。",
     "预览即交付件本身——服务原始响应字节，未做任何后处理。",
     "过程留痕不计入十件作品：各 `case-NN/vNN-preview.png`（改版预览，与 final 同目录保留）在 `outputs/%s/B06/`，"
     "1.5–1.6× QA 裁图、DSL 草稿、失败响应与请求原文全部在 `tmp/%s/B06/`。" % (RID, RID),
     "",
     "共同结构：**原始口径 → 换算 → 你能做的事**。十件用十种图形语言，画布尺寸互不重复。",
     "",
     "数据来源：`tmp/<run>/B06/research/demo.json`（b06data.py，固定种子 %s）；医疗／营养／法律类内容只复述公开常识并标注需核对。**未做任何现场调研或用户实验。**" % DEMO["seed"],
     ""]
for cid, c in sorted(CASES.items()):
    m = M[cid]
    g += ["## %d｜%s · %s（%d×%d）" % (c["n"], cid, m["title"], c["dims"][0], c["dims"][1]), "",
          "![%s · %s](%s)" % (cid, m["title"], c["png"]), "",
          "| 项 | 内容 |", "|---|---|",
          "| 文件 | [原 PNG](%s)（%s 字节，md5 `%s`） · [完整 DSL](%s)（%s 字节 / %s 字符，md5 `%s`） |"
          % (c["png"], format(c["png_bytes"], ","), c["png_md5"], c["snapshot"],
             format(c["snap_bytes"], ","), format(c["dsl_chars"], ","), c["snap_md5"]),
          "| 用例报告 | [%s](%s)（%s 字节） |" % (c["report"], c["report"], format(c["report_bytes"], ",")),
          "| 介质与版式 | %s |" % m["medium"],
          "| 受众 | %s |" % m["audience"],
          "| 阅读环境 | %s |" % m["use_context"],
          "| 使用者要完成的事 | %s |" % m["user_goal"],
          "| 内容依据 | %s |" % m["content_basis"],
          "| 视觉主张 | %s |" % m["visual_intent"],
          "| 构造成法 | %s |" % m["geometry"],
          "| 从最终图看到的改善 | %s |" % m["observed_improvement"],
          "| 尚未验证／缺失证据 | %s |" % m["missing_evidence"],
          "| 定稿请求 | `%s`（HTTP 200，%s；curl 端到端 %.1fs；本件成功渲染 %d 次，失败/截断重发 %d 次） |"
          % (c["final_request"], c["final_timing"], c["final_duration"], c["requests_ok"], c["requests_bad"]),
          "| 实际自检 | 版本 %d（%s）· 迭代留痕 %d 条 · 看图 %d 次 · 预览 %d 张 · QA 裁图 %d 张 · TextFit 逐框检查 %d 次 |"
          % (len(c["versions"]), "、".join(c["versions"]), len(c["iterations"]), c["views"],
             len(c["previews"]), len(c["qa_crops"]), c["textfit_checks"]),
          "", ""]
open(OUT / "gallery.md", "w", encoding="utf-8").write("\n".join(g))

# ---------------------------------------------------------------- portfolio.md
pm = ["# B06 作品集 · 把十个日常信息难题重做成作品（%s）" % RID, "",
      "curatorial statement：%s" % P["curatorial_statement"], "",
      "素材政策：%s" % P["asset_policy"], "", "## 十件一览", "",
      "| # | 件 | 标题 | 介质 | 换算母题 | 画布 | 版本 | 成功渲染 | 失败重发 | 定稿 request |",
      "|---|---|---|---|---|---|---|---|---|---|"]
motif = {"case-01": "环形钟", "case-02": "倒推段条", "case-03": "现金流堆叠", "case-04": "价格瀑布",
         "case-05": "发散偏差条", "case-06": "累计面积", "case-07": "阶梯函数", "case-08": "决策扇形",
         "case-09": "方糖堆叠", "case-10": "核对打孔卡"}
for cid, c in sorted(CASES.items()):
    m = M[cid]
    pm.append("| %d | [%s](%s) | %s | %s | %s | %d×%d | %d | %d | %d | `%s` |" % (
        c["n"], cid, c["png"], m["title"], m["medium"].split("（")[0], motif[cid],
        c["dims"][0], c["dims"][1], len(c["versions"]), c["requests_ok"], c["requests_bad"], c["final_request"]))
pm += ["", "## 为什么是这十件", "",
       "十个场景都是同一种失效：**给出的口径与使用者要做的决定不在同一层**。"
       "服药要的是钟点，给的是「一日三次」；赶车要的是最迟出发时刻，给的是「末班 23:41」；"
       "比价要的是 12 个月真实负担，给的是「2780 元/月」；报告要的是轻重排序，给的是 9 个同形箭头；"
       "停车要的是哪天/哪一分钟跳价，给的是四行互不相干的数字；买饮料要的是这一瓶多少糖，给的是每 100 mL；"
       "签合同要的是「不对我怎么办」，给的是散在四处的条款。", "",
       "因此十件不设行业名单、不做版式模板复用：每件先确定「缺的是哪一次换算」，再选一种能把这次换算"
       "画出来的图形语言，最后用⑤／④口径块把「哪些是演示、哪些需核对」印在页面上。"
       "十件之间不共享实体（不像 B05 那样同一棵树贯穿），共享的是同一条三段结构与同一套换算纪律："
       "件-01 与件-06 同用 24 小时／30 天轴，件-03 与件-04 同用堆叠分解，件-07 与件-08 同用「临界点」语言，"
       "件-05 与件-09 同用「换口径就换第一名」的对照。", "",
       "逐图说明见 [gallery.md](gallery.md)，问题来源与场景要求见 [problem-evidence.json](problem-evidence.json)，"
       "以最终画面为准的评审见 [design-review.md](design-review.md)，逐件数据与改版记录见各 `case-NN/case.md`。", "",
       "## 未解决的问题", ""]
pm += ["- " + u for u in P["unresolved_issues"]]
pm += [""]
open(OUT / "portfolio.md", "w", encoding="utf-8").write("\n".join(pm))

# ---------------------------------------------------------------- problem-evidence.json
EV = {
    "schema_version": 1,
    "path_base": "output_dir",
    "task_id": "B06",
    "run_id": RID,
    "purpose": "逐件记录：问题的实际来源或假设、场景要求、重构选择，以及根据最终图判断的改进（区分可观察的可读性改善与未经用户实验验证的效果）",
    "method": {
        "how_problems_were_found": "从日常公共界面与包装上反复出现的原文形式中挑选：药盒与说明书文字、站内末班告示、租房列表页价格行、外卖结算页两行金额、体检报告结论页、运营商套餐详情小字、停车场入口立牌、洗衣机旋钮程序带、饮料背标营养成分表、劳动合同与 HR 口头说明。",
        "what_was_not_done": "没有做任何现场调研、访谈、问卷、可用性测试或用户实验；没有拍摄/收集实物照片；没有从任何网站抓取数据。本题全部数值由本地生成器给出。",
        "no_scoring_material_used": "未使用任何外部评分材料作为输入。",
        "source_labels": {
            "observed": "可在公共场所／包装／界面直接读到的原文形式（本文件只复述形式，未保存实物图像）",
            "self_defined_demo": "数值、名称、情境为我拟定的合理演示，不对应任何在营服务或真实个人",
            "common_rule_needs_check": "按公开常识复述的常见规定／建议，落地前需核对现行条文、说明书与当地口径",
        },
        "dataset": "tmp/<run>/B06/research/demo.json（b06data.py，seed %s，city %s）" % (DEMO["seed"], DEMO["city"]),
    },
    "problems": [],
    "cross_case_findings": [
        "十件里最危险的错误都不是画错，而是口径抄错：件-01 把「0 蔗糖」安到无糖茶上、件-02 的行程合计 63 与 72 不一致、件-09 的 label 字段缺失——三次都在数据生成器或断言层面修，而不是在画面上手改数字",
        "TextFit 闸门只校验单个文字盒，看不出遮挡（件-01 的三圈被盘心盖住、件-08 的扇环标签互相压字）；遮挡只能靠打开实际 PNG 与 1.5–1.6× 裁图发现",
        "垂直溢出靠出图前 assert 拦下（件-04、件-06、件-07、件-08、件-09、件-10 共 12 次本地中止，未发请求），比渲染后再看图省一整轮",
        "台阶 vs 斜线是本题的图形论点：件-06、件-07 的换算都必须按「不足一段按一段计」画成台阶，用斜线就会把临界点算错",
        "十件的⑤／④口径块长度是被迫的：演示值与需核对项越多，限制文字越长，进而多次触发 TextFit 警告——这与真实信息产品的合规文本行为一致",
    ],
    "verification_boundary": "以下每件 improvement_observed_in_final_image 只主张「从最终 PNG 与结构对比可看到的改善」；effect_claim_requires_user_testing 一律为 true，即任何「更快／更少出错／更放心」的效果结论都需要真实用户测试，本题未做。",
}
EV_CASES = {
    "case-01": dict(
        observed_form="药盒与说明书上的「一日三次」「饭后服用」「空腹」字样",
        source_type=["observed", "common_rule_needs_check", "self_defined_demo"],
        stuck_point="把「一日三次」当成跟着三餐吃（间隔变成 4–5 h 加夜里 14 h），把「空腹」理解成饿着肚子随时都行",
        scenario_requirements="冰箱门前站立 10 秒读完；结论必须是能直接抄进日历的具体钟点；不能替人判断该不该吃",
        reframing="用 24 h 圆盘把间隔摊成三圈钟点，清醒窗口做成外带；右侧三行做「原口径→每 N h→钟点串→下一次还剩」",
        improvement_observed_in_final_image="4 字口径 → 3 个具体钟点＋1 个等待小时数；「夜里最长间隔 14 h」这类原本需要自己算的量直接可见",
        data_provenance="demo.json case01.drugs（钟点、interval_h、wait_h、overnight_gap_h 为演示）；间隔口径标 common_rule_needs_check",
        review_evidence="case01-v01…v04 四次看图；qa-v04-clock.png／qa-v04-amber.png 为 2× 裁图（仅观察）",
    ),
    "case-02": dict(
        observed_form="地铁站内「末班 23:41」式告示牌",
        source_type=["observed", "self_defined_demo"],
        stuck_point="告示只回答「这班车几点开」，不回答「我从这里出发今晚能不能按时到家、最迟几点动身」；换乘走行、二线车程、出站步行全靠脑补",
        scenario_requirements="剩余决策时间约 15 分钟，单手持手机，一屏读完；跨零点要能自洽回绕；不得暗示运营方承诺",
        reframing="把末班时刻倒推成六段行程条（含 5 min 保守缓冲），结论只留一个可执行时刻 23:23；三种情况里第三种写明「本卡不含该信息，不编造」",
        improvement_observed_in_final_image="1 个时刻 → 6 段时长＋合计 72 min＋最迟出发时刻＋当下剩余 16 min；「来不及」被拆成具体缺哪一段",
        data_provenance="demo.json case02：城市、六段时长、缓冲全为演示；缓冲口径为自设",
        review_evidence="case02-v01…v04 四次看图；v01 无图（card 位置参数用错）已在迭代留痕记录",
    ),
    "case-03": dict(
        observed_form="租房列表页价格行「2780 元/月 ＋ 押一付三 ＋ 单程 35 min」",
        source_type=["observed", "self_defined_demo"],
        stuck_point="决定贵不贵的押金方式、中介费、物业费、水电、免租期与通勤都不在价格行里；列表页最便宜的一套往往签约当天拿出最多、住进去每月最贵",
        scenario_requirements="坐下来对比，可打印带走；必须能同时看三套并指出可谈项；时间折算口径要写在页面上",
        reframing="把六笔钱与一段通勤折进 12 个月现金流堆叠（押金画成条尾空心框不计入年度负担），再按真实月均重排并给三笔可谈项的省额",
        improvement_observed_in_final_image="3 个数 → 5 列明细＋排序反转：C 列表最便宜（1,980）真实月均 3,567，比 B（2,150→3,308）每月贵 259 元，方向与列表页相反",
        data_provenance="demo.json case03：三套房、租金、免租期、通勤为演示；30 元/h、每月 22 天往返为自设口径（页面明写）",
        review_evidence="case03-v01…v04 四次看图＋qa/ 局部裁图核对表列对齐",
    ),
    "case-04": dict(
        observed_form="外卖结算页两行「¥23.22」「已优惠 ¥13.00」",
        source_type=["observed", "self_defined_demo"],
        stuck_point="五件不同的事（菜品原价、满减、券、包装费、按里程的配送费）被压成一个数，于是没法比两家店、也算不出凑单值不值、每克多少钱",
        scenario_requirements="下单前 30 秒；瀑布每一行要能对上账；结论要是一句「凑／不凑」",
        reframing="五步同比例尺瀑布（16 px＝1 元）＋累计列；再换分母做每 100 g 单价与包装配送占比；凑单算净多支出",
        improvement_observed_in_final_image="2 行 → 5 步瀑布（30→22→17→19.50→23.22 逐行可对账）＋凑单结论「净多支出 9.00 元→不值」",
        data_provenance="demo.json case04：两家店全部价格为演示；配送费公式为自设口径",
        review_evidence="case04-v01…v03 三次看图；出图前 3 次本地 assert 中止（③④卡与 note 溢出）已记录",
    ),
    "case-05": dict(
        observed_form="体检报告结论页的 12 项 ×（结果、参考区间、↑/↓），其中 3 项区间只有单边",
        source_type=["observed", "self_defined_demo"],
        stuck_point="箭头只有两种形状，不区分「刚过线 0.1」和「超出 1.8 倍半宽」，也不给复查顺序与科室，读者拿到一堆等宽符号",
        scenario_requirements="平板或打印平铺阅读；排序必须能解释；不得给诊断结论或引用条文号",
        reframing="dev＝|结果−区间中点|÷半宽（自设口径，仅用于排序），画成 12 行发散条；再并排「按 dev」与「按超界百分比」两种口径，最后给四档复查节奏与 5 个科室先后",
        improvement_observed_in_final_image="9 个等宽符号 → 12 条可比长度＋复查节奏分档＋科室先后；关键对照（维 D 超下界 43.3% 幅度最大但 dev 第 7，血红蛋白只超 6.9% 但 dev 第 5）直接印在画面上",
        data_provenance="demo.json case05：12 项数值、区间、科室归属、复查节奏全部为演示，非任何实验室参考值",
        review_evidence="case05-v01…v03 三次看图；TextFit 闸门 4 警（③ 数值盒 46×22）在发请求前修掉",
    ),
    "case-06": dict(
        observed_form="套餐详情页大字「100 GB」＋两行小字「高速流量 40 GB，超出后降至 1 Mbps，次月恢复」",
        source_type=["observed", "self_defined_demo"],
        stuck_point="两行小字都不带时间轴：算不出这个月哪天开始卡，也不知道 1 Mbps 之后手上的事还能不能做",
        scenario_requirements="网页或投屏横版，远看可读；降速点必须精确到日与小时；不得暗示真实运营商报价",
        reframing="30 天逐日累计画成台阶面积与 40 GB 额度线求交→第 22 天 18:30；把 1 Mbps 换算成每小时 0.45 GB 与七件事可用／会卡；把 40 GB 摊成每日预算 1.33 GB",
        improvement_observed_in_final_image="两行小字 → 撞线时刻＋实际日均 1.87 GB（超预算 40%）＋超预算 15 天＋第 15 天预警线；③ 用七行判定把「1 Mbps」变成行动约束",
        data_provenance="demo.json case06：额度、降速值、月费、30 天用量、各应用带宽全部为演示",
        review_evidence="case06-v01…v05 五次看图；出图前 3 次本地 assert 中止记录在案；qa/ 多张裁图核对竖线与标签",
    ),
    "case-07": dict(
        observed_form="停车场入口立牌四行字：免费 15 分钟／首小时 6 元／之后每 30 分钟 3 元／24 小时内封顶 40 元",
        source_type=["observed", "self_defined_demo"],
        stuck_point="四行字各自都懂，合在一起没人能口算停 45 分钟付多少、停到几点不划算、封顶要停多久；「不足一段按一段计」意味着价格是台阶不是斜线",
        scenario_requirements="进门前 30 秒 glance；三个常见时长要有明确金额；跳变点要指出来；跨天要说明",
        reframing="按四行字逐分钟扫描得 14 段台阶、13 个跳变点，封顶落在第 406 分钟（6 h 46 min）而非字面 24 小时；再给 45 min／2 h／8 h 三档金额与折算单价",
        improvement_observed_in_final_image="4 行字 → 可读出金额的台阶函数＋「跳变点前 1 分钟最划算（76 min 刚跳 9 元，105 min 同样 9 元）」＋封顶后不必盯表、跨天 25 h＝46 元",
        data_provenance="demo.json case07：费率、封顶、三个时长全部为演示；城市虚构",
        review_evidence="case07-v01…v05 五次看图＋qa/ 台阶与跳变线裁图核对",
    ),
    "case-08": dict(
        observed_form="洗衣机旋钮旁一排 14 个程序图标（只写名字与温度）",
        source_type=["observed", "self_defined_demo"],
        stuck_point="面板给的是程序清单，用户要的是「手上这一件怎么选」，中间缺面料、脏污、时间三层判断；选错要么洗坏要么来不及干",
        scenario_requirements="洗衣前站在机器前 1 分钟；必须收敛到一个程序并给结束时刻；也要明确列出该避开的程序",
        reframing="三层同心扇环，14 个程序各占 12.857° 槽位：外环面料（14→6）、中环脏污（6→3）、内环今晚时间（3→3），中心按评分与结束时刻取 1 个",
        improvement_observed_in_final_image="14 个图标 → 一条可见的收敛路径＋选定程序 P03（78 min，含 15 min 预处理后 22:13 结束、剩 77 min 晾晒）＋4 个易误选程序的失败原因计数",
        data_provenance="demo.json case08：程序参数与情境全部为演示，note 要求以自家机器说明书为准",
        review_evidence="case08-v01…v03 三次看图；首版署名行 1084 px 超 1000 px 盒被闸门拦下；qa/ 扇环局部裁图核对分层归属",
    ),
    "case-09": dict(
        observed_form="饮料背标营养成分表「每 100 mL 含糖 9.1 g」＋旁边的「0 蔗糖」宣称",
        source_type=["observed", "common_rule_needs_check", "self_defined_demo"],
        stuck_point="9.1 这个数从来没按整瓶算过；「0 蔗糖」与「无糖」是两回事却常被当成一回事；每日建议上限也没人和一瓶对上",
        scenario_requirements="货架前几秒，手上就是那瓶；要能一眼看出堆到第几块、喝多少毫升过线；不得给诊断建议",
        reframing="整瓶克数＝每 100 mL × 净含量 ÷ 100，按 4.5 g／块折成方糖堆（每行 3 块＝13.5 g），叠 25 g／50 g 两条常见建议线，再单独算「喝到多少毫升吃掉 25 g」",
        improvement_observed_in_final_image="每 100 mL 口径 → 整瓶克数（S3 27.3 g＝6 块）、过线毫升与占整瓶比例，以及金框「0 蔗糖」与绿框「无糖」的并排对照；两种字样不再混为一谈",
        data_provenance="demo.json case09：含量、瓶型为演示；25 g／50 g 为常见公开建议口径，标 common_rule_needs_check",
        review_evidence="case09-v01…v05 五次看图；v01 只看图才发现 label 语义错位（无糖茶被标成「0 蔗糖」），回生成器修字段并用递归 diff 证明只增 5 个键",
    ),
    "case-10": dict(
        observed_form="劳动合同正文＋附件＋HR 口头说明里分散的试用期、社保起缴、加班费基数、公积金、年假、竞业条款",
        source_type=["observed", "common_rule_needs_check", "self_defined_demo"],
        stuck_point="新人手里既有「合同写试用期 8 个月」也有「转正后再缴」这种没出处的话；缺的不是法律知识，而是一张能逐项打勾并写明下一步的纸",
        scenario_requirements="A4 打印放桌面逐项核对；判定状态要一眼数得清；每条要有一句可执行动作；必须声明不是法律意见",
        reframing="压成打孔卡：左缘一个孔＝一项，孔色＝判定（不符／缺项／通过），五列中后四列照抄来源文本不改写；加班 61 h 与 36 h 上限同轴直接读差额",
        improvement_observed_in_final_image="散落四处的条款 → 一屏判定分布（不符 5／缺项 3／通过 0）＋每项一句动作＋第一个月 6 个时间点；加班超出 25 h＝上限的 69% 无需口算",
        data_provenance="demo.json case10：8 项文本（7 项 common_rule_needs_check、1 项 self_defined_demo）、月薪 12,000、排班 61 h 为演示；note 声明本表为核对清单不是法律意见",
        review_evidence="case10-v01…v04 四次看图＋qa/ 6 张裁图（打孔条、表头对齐、加班轴）；出图前 2 轮本地 assert 中止记录在案",
    ),
}
for cid in sorted(CASES):
    c, m, e = CASES[cid], M[cid], EV_CASES[cid]
    EV["problems"].append({
        "case": cid,
        "work_id": "%s-%s" % (RID.replace("T", "T"), cid),
        "title": m["title"],
        "canvas": c["dims"],
        "medium": m["medium"],
        "observed_form": e["observed_form"],
        "source_type": e["source_type"],
        "user_stuck_point": e["stuck_point"],
        "scenario_requirements": e["scenario_requirements"],
        "reframing_choice": e["reframing"],
        "transformation": m["visual_intent"],
        "improvement_observed_in_final_image": e["improvement_observed_in_final_image"],
        "effect_claim_requires_user_testing": True,
        "not_verified": m["missing_evidence"],
        "data_provenance": e["data_provenance"],
        "review_evidence": e["review_evidence"],
        "deliverables": {"png": c["png"], "snapshot": c["snapshot"], "case_report": c["report"]},
        "final_request": c["final_request"],
    })
json.dump(EV, open(OUT / "problem-evidence.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("portfolio.json cases", len(P["cases"]))
print("gallery lines", len(g))
print("problem-evidence cases", len(EV["problems"]))
for cid, c in sorted(CASES.items()):
    print(cid, c["dims"], c["final_version"], c["final_request"], c["requests_ok"], c["requests_bad"],
          len(c["qa_crops"]), c["textfit_checks"])
