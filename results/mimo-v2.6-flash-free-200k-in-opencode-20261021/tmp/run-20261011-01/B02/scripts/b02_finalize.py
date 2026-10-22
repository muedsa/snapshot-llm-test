# -*- coding: utf-8 -*-
"""B02 finalize: copy finals (md5+IHDR verify), write case.md x11,
design-system/touchpoint/project deliverables are pre-written static files;
portfolio.json/md, gallery.md, normalize requests.jsonl, iterations.jsonl,
tool-usage.jsonl, snapshot-usage.md, task-metrics.json, copy-report.json."""
import datetime
import hashlib
import json
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))  # suite root
RUN = "run-20261011-01"
TID = "B02"
OUT = os.path.join(ROOT, "outputs", RUN, TID)
TMP = os.path.join(ROOT, "tmp", RUN, TID)
DRAFTS = os.path.join(TMP, "drafts")
PLAN_PATH = os.path.join(TMP, "plan-v1.json")
PLAN_REL = "tmp/%s/B02/plan-v1.json" % RUN
PLAN_EST = "2026-10-19T19:26:16+08:00"
PROJ = "禾风里社区共耕花园"

# ---------------------------------------------------------------- cases
CASES = [
    dict(
        cid="case-01", title="开放日报名海报", journey="认知→报名",
        aud="路过的居民（街道公告栏/地铁灯箱，2–3m 处扫视）",
        ctx="1080×1528 竖版（A3 比例）公告栏/灯箱印刷",
        goal="30 秒内知道开放日时间地点并扫码报名",
        scope="标题、三亮点、开放日时间地点、认养规模、占位二维码（非功能性已注明）、主办信息",
        vi="宣纸底 + 土陶大标题 + 叶绿亮点条，大留白公告风",
        ver="v2", dims=(1080, 1528),
        fictional="“禾风里社区共耕花园”、地址、电话、二维码图案均为虚构演示；不指向真实项目",
        asserts="assert_facts()；二维码为确定性随机占位图案（seed=420），图上明示“示意图案非真实二维码”",
        fix_log=[
            "v1c→v2：看图发现“认养规模”行文本越过时间地点卡下边框、叶标记圆角过大读作圆点；"
            "修改：卡片 250→280、行距 44→42、leaf_mark 圆角 0.85r→0.45r",
        ],
        final_obs="v2 复看：末行在卡内 24px 余量、叶形成立、二维码三定位角完整",
    ),
    dict(
        cid="case-02", title="地块认养证", journey="加入",
        aud="认养户（开放日现场 A4 打印，签约后装裱留存）",
        ctx="1240×1754（A4 比例）打印证书",
        goal="拿到有仪式感的凭证并知晓三条基本义务",
        scope="认养人、地块编号/尺寸、认养期、须知三条、双方签署、印章",
        vi="证书排版：细双线边框 + 刻度尺 + 圆形印章，庄重留白",
        ver="v2", dims=(1240, 1754),
        fictional="认养人、编号、规则与印章为虚构演示，不具备法律效力（页脚已声明）",
        asserts="地块示意 225×300px 按 3m×4m=3:4 真实比例；assert_facts()（12 块/24 户）",
        fix_log=[
            "v1c→v2：看图发现地块两侧大片空白、构图失衡；修改：两侧新增"
            "“园方提供/认养人获得”信息卡（340×300）平衡版面并补充用户价值信息",
        ],
        final_obs="v2 复看：三栏平衡、印章与签署线不重叠、须知三条完整",
    ),
    dict(
        cid="case-03", title="周六市集价目牌", journey="购买",
        aud="市集顾客（摊位立牌，1m 处快速扫读）",
        ctx="1080×1350 立牌",
        goal="3 秒找到想买的菜、单价与会员折后价",
        scope="8 种当季菜单价+会员价、限购提示、支付方式、市集时段",
        vi="价目网格：白卡 + 叶绿价签 + 土陶限购条",
        ver="v1", dims=(1080, 1350),
        fictional="摊位号、菜价为虚构演示数据（随行就市已注明）",
        asserts="会员价 = round(单价×0.8) 由 MARKET_PRICES 统一计算；assert_facts()",
        fix_log=[], final_obs="首版达标：8 价签完整、会员价 5/4/3/3/6/4/2/8 全对、无截断",
    ),
    dict(
        cid="case-04", title="菜篮订阅卡", journey="复购",
        aud="家庭用户（微信群/朋友圈转发，手机竖屏睡前点开）",
        ctx="1080×1920 手机长图",
        goal="选好规格并知道配送日与退订规则",
        scope="三规格价格与适用人数、每周菜色示例、配送自提、订阅流程、退订规则",
        vi="手机长图：三层规格卡 + 菜色 chips + 流程条 + 规则脚注",
        ver="v2", dims=(1080, 1920),
        fictional="品牌、价格、菜色为虚构演示；菜色随采收微调已注明",
        asserts="规格 29/49/79 与 FACTS.basket 一致；小/中/家菜色数 4/6/8 与篮内示例一致；assert_facts()",
        fix_log=[
            "v1→v2：看图发现家庭份菜色 chips 越过卡片底边、下单框第二行被裁、"
            "下部约 380px 空白；修改：规格卡高按内容分配(236/268/274)、下单框改 86 高两行独立文本、"
            "新增“订阅流程”4 步条填补空档",
        ],
        final_obs="v2 复看：chips 全在卡内、下单两行完整、流程条与退订规则层级清晰",
    ),
    dict(
        cid="case-05", title="志愿者排班表", journey="参与",
        aud="志愿者与管理员（出门前手机查看/工具房打印）",
        ctx="1400×1000 横版网格",
        goal="看清本周各时段岗位缺口并认领",
        scope="7 天×4 时段网格、四岗位需求与缺口高亮、容量条、认领方式与联系人",
        vi="排班网格：叶绿表头语义 + 土陶缺口高亮 + 容量条三色",
        ver="v2", dims=(1400, 1000),
        fictional="排班员、志愿者、时段为虚构演示数据",
        asserts="GRID=28 格断言；缺口 5 人次 = 三处明细(2+2+1)；本周志愿 59 人次由数据求和",
        fix_log=[
            "v1→v2：看图发现三岗位单元格第三枚 chip 与容量条重叠（周二10–13、周六两格）；"
            "修改：格高 148→156、chip 步距 40→36、起点 12→8",
        ],
        final_obs="v2 复看：三 chip 格与容量条不再碰撞、缺口清单与高亮格一致",
        gen_fail="生成期 GRID 断言失败（写成 17 格，应为 28 格），未发出请求；重写为 day-major 28 格并与缺口清单对账",
    ),
    dict(
        cid="case-06", title="厨余堆肥三步图", journey="学习",
        aud="手提厨余的居民（堆肥箱旁立牌，0.8m 处）",
        ctx="1000×1400 立牌",
        goal="30 秒学会可投/不可投与三层堆法",
        scope="可投清单、不可投警示、三层堆法剖面、翻堆周期、熟肥用法",
        vi="说明图：堆体剖面三层色带 + 清单双栏 + 土棕场景色",
        ver="v1", dims=(1000, 1400),
        fictional="周期（21–28 天）、配比与值守人为虚构演示参数",
        asserts="厨余 2.4 吨→堆肥 0.8 吨与 FACTS 一致、转化率 33% 计算一致",
        fix_log=[], final_obs="首版达标；fit() 对含换行整串告警经逐行核对为误报（各行均在面板内）",
    ),
    dict(
        cid="case-07", title="二十四节气种植日历", journey="计划",
        aud="会员与志愿者（活动中心横屏，3m 处站立观看）",
        ctx="1600×900 横屏大图",
        goal="知道本月该播种什么、正收什么",
        scope="12 节气条、6 作物行、播种/养护/采收三色区间、本月(谷雨)高亮、本月农事三条",
        vi="甘特式日历：宣纸底 + 三色区间条 + 本月光柱",
        ver="v2", dims=(1600, 900),
        fictional="节气区间为本园经验参数（虚构演示），非农业技术承诺",
        asserts="区间端点有序且 ≤11 断言、本月=谷雨断言；本月笔记(生菜尾茬/黄瓜始收)与区间表一致",
        fix_log=[
            "v1→v2：看图发现交错白色行底把谷雨高亮带盖成断续、空心菜“养护”标签被"
            "后画的采收条覆盖；修改：图层重排（行底先画、高亮带后画）、标签裁剪到"
            "不被后画条覆盖的可见跨度",
        ],
        final_obs="v2 复看：高亮带贯穿六行、所有区间标签可见、三条本月笔记齐全",
    ),
    dict(
        cid="case-08", title="工具房安全须知", journey="参与/安全",
        aud="取用工具的志愿者（工具房门内，0.6m 处）",
        ctx="900×1200 门内警示挂牌",
        goal="取工具前读懂 6 条安全规则与归还要求",
        scope="6 条编号规则、PPE 四件、归还要求、紧急联系",
        vi="警示牌：土陶底白纸卡反转 + 编号圆章 + 深土棕信息条",
        ver="v2", dims=(900, 1200),
        fictional="联系人、电话为虚构演示（页脚已声明）",
        asserts="6 规则/PPE4/归还3条/联系3条结构齐全；无外部数据",
        fix_log=[
            "v1→v2：看图发现底部深色信息条 1030+250=1280 超出 1200 画布、页脚压在"
            "条内文字上、“缺件找老陈”被裁；修改：行高收紧(190→180、间隙 24→20)、"
            "PPE 150→140、信息条 250→200 置于 y=960、页脚 y=1166",
        ],
        final_obs="v2 复看：信息条在画布内、页脚独立、6 规则与联系均可读",
    ),
    dict(
        cid="case-09", title="三季度收成报告", journey="反馈",
        aud="认养户与捐赠方（公示栏 1m 处/社群点开）",
        ctx="1600×900 横版数据报告",
        goal="看懂本季产出、参与度与资金去向",
        scope="三项 KPI、品类构成条形、收成去向、支出构成、下季计划",
        vi="数据报告：KPI 卡 + 品类条形 + 支出堆叠条 + 计划面板",
        ver="v2", dims=(1600, 900),
        fictional="产量、支出、计划为虚构演示数据（页脚已声明）",
        asserts="sum(q3_break)=1286=FACTS.q3_total 断言；支出占比 32+24+18+14+12=100 断言；"
                "收成去向 42+46+12=100",
        fix_log=[
            "v1→v2：看图发现左下约 740×180 空白、报告缺“收成去向”环节；"
            "修改：左下新增收成去向卡（市集 42/菜篮 46/食堂捐赠 12）",
        ],
        final_obs="v2 复看：四模块平衡、去向补齐、数字与共享事实全部对账",
    ),
    dict(
        cid="case-10", title="市集帐篷横幅", journey="认知/招徕",
        aud="市集人流（帐篷檐口，5–8m 远距）",
        ctx="1920×640 超宽横幅",
        goal="远处识别摊位并记住三样主打与会员招募",
        scope="摊位名、三样主打菜+价格、会员招募一句话、品牌锁定组合、叶纹边",
        vi="超宽横幅：叶绿大底 + 重复叶纹水印 + 土陶招募块",
        ver="v3", dims=(1920, 640),
        fictional="菜价为虚构演示；摊主、摊位号虚构",
        asserts="三主打单价与 MARKET_PRICES 一致；会员价 round(p×0.8)=5/4/8 断言",
        fix_log=[
            "v1→v1b：HTTP400 语法失败（gradientBegin=LEFT_CENTER 非法，服务 diagnostic "
            "给出 CENTER_LEFT）；修改：grad_box 词汇映射修正",
            "v1b→v2：看图发现“入会”第三行被裁（大字号实际行距≈85px 不受 line_h 约束）；"
            "修改：文本框 130→200",
            "v2→v3：复看三行仍裁；修改：改两行对称四字“现场扫码/即刻入会”、行高 84",
        ],
        final_obs="v3 复看：两行完整、108px 主标 5m 外可读、价格锚点清晰",
    ),
    dict(
        cid="case-11", title="自然课报名卡", journey="亲子参与",
        aud="家长（家长群转发/现场领取，手机方图）",
        ctx="1200×1200 手机方图",
        goal="给孩子报名本周六自然课并知道携带物",
        scope="课程主题、时间/时长/年龄/地点、名额进度、携带清单、报名方式",
        vi="亲子风：番茄红主题头 + 番茄图形 + 名额进度条",
        ver="v1", dims=(1200, 1200),
        fictional="课程、名额、地点为虚构演示；“已连续 6 场满员”为演示文案",
        asserts="9/12 进度条 75% 与 FACTS.class 一致；剩余 3 位计算一致；assert_facts()",
        fix_log=[], final_obs="首版达标：进度/携带/报名三块齐全、番茄图形与主题成立",
    ),
]

# observation per successful render (for iterations.jsonl)
OK_OBS = {
    ("case-01", "v1c"): ("认养规模行越过时间地点卡下边框；叶标记读作圆点", "卡片250→280、行距44→42、leaf圆角0.85r→0.45r"),
    ("case-01", "v2"): ("末行在卡内、叶形成立，其余达标", None),
    ("case-02", "v1c"): ("地块两侧大片空白、构图失衡", "两侧新增园方提供/认养人获得信息卡"),
    ("case-02", "v2"): ("三栏平衡、证书要件齐全", None),
    ("case-03", "v1"): ("首版达标：8 价签完整、会员价正确、无截断", None),
    ("case-04", "v1"): ("家庭份chips越卡底、下单框第二行被裁、下部约380px空白", "卡高按内容分配、下单框86高两行、新增订阅流程4步条"),
    ("case-04", "v2"): ("chips在卡内、下单两行完整、流程条填补空白", None),
    ("case-05", "v1"): ("三岗位单元格第三枚chip与容量条重叠", "格高148→156、chip步距40→36、起点12→8"),
    ("case-05", "v2"): ("三chip格与容量条不再碰撞", None),
    ("case-06", "v1"): ("首版达标；fit换行误报逐行核对放行", None),
    ("case-07", "v1"): ("行底盖断本月高亮带、空心菜养护标签被采收条覆盖", "图层重排(行底→高亮带→条)、标签裁剪到可见跨度"),
    ("case-07", "v2"): ("高亮带贯穿六行、标签全可见", None),
    ("case-08", "v1"): ("信息条1030+250超1200画布、页脚压字、缺件文字被裁", "行高收紧、信息条200高置960、页脚1166"),
    ("case-08", "v2"): ("信息条在画布内、页脚独立、规则可读", None),
    ("case-09", "v1"): ("左下大片空白、缺收成去向环节", "左下新增收成去向卡(42/46/12)"),
    ("case-09", "v2"): ("四模块平衡、数字全部对账", None),
    ("case-10", "v1b"): ("现场/扫码两行可见，入会第三行被裁(行距≈85px)", "文本框130→200"),
    ("case-10", "v2"): ("三行仍裁(行距不受line_h约束)", "改两行四字 现场扫码/即刻入会、行高84"),
    ("case-10", "v3"): ("两行完整、远距可读", None),
    ("case-11", "v1"): ("首版达标：进度/携带/报名齐全", None),
}

HTTP400_FIX = {
    "B02-c01-v1": ("XML声明<?xml首字符被服务拒绝(PARSE_ERROR@TAG_OPEN)", "emit去掉XML声明"),
    "B02-c01-v1b": ("Snapshot只允许一个子节点", "emit改Snapshot>SizedBox>Stack(TOP_LEFT,CLIP_NONE)"),
    "B02-c02-v1": ("XML声明<?xml首字符被服务拒绝", "emit去掉XML声明"),
    "B02-c02-v1b": ("Snapshot只允许一个子节点", "emit改Snapshot>SizedBox>Stack嵌套"),
    "B02-c10-v1": ("gradientBegin=LEFT_CENTER非合法词汇(diagnostic给出CENTER_LEFT)", "grad_box词汇映射LEFT_CENTER→CENTER_LEFT/CENTER_RIGHT"),
}

GEN_FAIL = [
    ("case-01", "b02_case01 v1 FileNotFoundError：drafts目录不存在", "建目录后重生成"),
    ("case-02", "b02_case02 v1 FileNotFoundError：drafts目录不存在", "建目录后重生成"),
    ("case-05", "GRID断言失败(len=17≠28)", "重写day-major 28格并与缺口清单对账"),
]

TOOL_USAGE = [
    dict(tool="_suite/docs/muedsa-snapshot-src/.../ContainerParser.kt（读源码+grep）",
         purpose="确认Container不含x/y绝对定位属性，核心构件改用B01已证Positioned包装",
         io="读源码文件→stdout属性清单", ts="2026-10-19T19:31+08:00", affects="全部11件（v1c起）"),
    dict(tool="b02_common.tw()/fit()（自写生成期宽度预算）",
         purpose="CJK=1em/ASCII≈0.56em估算行宽，生成期拦截越界；对含\\n多行文本的误报逐行人工核对",
         io="生成脚本内联调用→FIT-WARN stdout", ts="19:33–20:08", affects="全部11件"),
    dict(tool="b02_common.assert_facts()（自写数据对账断言）",
         purpose="每次生成前断言产量合计1286、会员价公式、名额进度等跨件对账关系",
         io="各case脚本入口调用", ts="19:33–20:08", affects="全部11件（G3证据）"),
    dict(tool="b02_finalize.py copy-report（md5+IHDR核验）",
         purpose="final.png/final.snapshot 与草稿字节双向md5核对并读IHDR尺寸对计划",
         io="drafts/与outputs/→copy-report.json", ts="finalize时", affects="全部11件（G1证据）"),
    dict(tool="服务400响应diagnostic.allowedValues（服务返回的纠错字段）",
         purpose="c10 gradientBegin非法词汇错误响应直接给出合法值，据此一次修正",
         io="requests.jsonl错误体→grad_box修正", ts="2026-10-19T20:04+08:00", affects="case-10"),
]


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def ihdr(path):
    with open(path, "rb") as f:
        data = f.read(33)
    assert data[12:16] == b"IHDR", path
    return struct.unpack(">II", data[16:24])


def main():
    os.makedirs(OUT, exist_ok=True)
    plan = json.load(open(PLAN_PATH, encoding="utf-8"))
    plan_cases = {c["id"]: c for c in plan["cases"]}

    # ---------------- normalize requests.jsonl ----------------
    req_path = os.path.join(TMP, "requests.jsonl")
    reqs = [json.loads(l) for l in open(req_path, encoding="utf-8") if l.strip()]
    for e in reqs:
        rid = e["id"]                       # B02-cNN-vNN
        cn = rid.split("-")[1]              # c01
        e["case_id"] = "case-%s" % cn[1:]
        e["type"] = "render"
        e["endpoint"] = "POST /snapshot（无凭据）"
        e["tz"] = "+08:00"
        e["input_file"] = e.get("dsl_path")
        e["output_file"] = e.get("out_path")
    with open(req_path, "w", encoding="utf-8") as f:
        for e in reqs:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    by_case = {}
    for e in reqs:
        by_case.setdefault(e["case_id"], []).append(e)

    # ---------------- copy finals (md5+IHDR) ----------------
    report = {}
    for c in CASES:
        cid, ver = c["cid"], c["ver"]
        src_png = os.path.join(DRAFTS, "%s-%s.png" % (cid, ver))
        src_dsl = os.path.join(DRAFTS, "%s-%s.snapshot" % (cid, ver))
        dst = os.path.join(OUT, cid)
        os.makedirs(dst, exist_ok=True)
        dst_png = os.path.join(dst, "final.png")
        dst_dsl = os.path.join(dst, "final.snapshot")
        s_png, s_dsl = md5(src_png), md5(src_dsl)
        for s, d in ((src_png, dst_png), (src_dsl, dst_dsl)):
            with open(s, "rb") as fi, open(d, "wb") as fo:
                fo.write(fi.read())
        d_png, d_dsl = md5(dst_png), md5(dst_dsl)
        w, h = ihdr(dst_png)
        dims_ok = (w, h) == tuple(c["dims"])
        dims_plan = tuple(plan_cases[cid]["size"])
        report[cid] = {
            "draft_png": "tmp/%s/B02/drafts/%s-%s.png" % (RUN, cid, ver),
            "draft_snapshot": "tmp/%s/B02/drafts/%s-%s.snapshot" % (RUN, cid, ver),
            "final_png": "outputs/%s/B02/%s/final.png" % (RUN, cid),
            "final_snapshot": "outputs/%s/B02/%s/final.snapshot" % (RUN, cid),
            "md5_src_png": s_png, "md5_dst_png": d_png, "png_md5_match": s_png == d_png,
            "md5_src_dsl": s_dsl, "md5_dst_dsl": d_dsl, "dsl_md5_match": s_dsl == d_dsl,
            "ihdr": [w, h], "dims_case": list(c["dims"]), "dims_plan": list(dims_plan),
            "dims_ok": dims_ok and tuple(dims_plan) == tuple(c["dims"]),
        }
        assert report[cid]["png_md5_match"], cid
        assert report[cid]["dsl_md5_match"], cid
        assert dims_ok, (cid, (w, h), c["dims"])
        assert tuple(dims_plan) == tuple(c["dims"]), (cid, dims_plan)

    json.dump(report, open(os.path.join(TMP, "copy-report.json"), "w",
                           encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # ---------------- case.md x11 ----------------
    G_TABLE = lambda c, e, n_ok, n_all, fix_txt, md5p: [
        ("G1", "服务 HTTP200 渲染，final.png 为原始字节，尺寸与计划一致",
         "通过：本件 %d 次请求中 %d 次 200（语法型失败见 iterations.jsonl）；"
         "final.png md5=%s… 与草稿一致；IHDR %d×%d" % (
             n_all, n_ok, md5p[:16], c["dims"][0], c["dims"][1]),
         "requests.jsonl、copy-report.json"),
        ("G2", "目标观看尺寸下全部文字可读、无折行截断/越界",
         "通过：生成期 tw()/fit() 预算；本件 %d 次成功渲染全部实际看图，无截断/越界" % n_ok,
         "生成脚本输出、看图记录 iterations.jsonl"),
        ("G3", "图上数字与共享事实同源一致", "通过：%s" % c["asserts"],
         "生成脚本断言、看图核对"),
        ("G4", "无元素重叠/遮挡/穿线缺陷", "通过：%s；终版复看无缺陷" % fix_txt,
         "iterations.jsonl、看图记录"),
        ("G5", "user_goal 关键信息齐备", "通过：content_scope 逐项在终版看图勾对（%s）" % c["goal"][:24],
         "终版整图看图"),
        ("G6", "虚构品牌/数据在 case.md 如实声明", "通过：见下方虚构声明；页脚图上标注",
         "本文件"),
        ("G7", "设计系统一致性（色板/字体/叶母题）",
         "通过：色板 + Noto Sans CJK SC + 叶形母题在本件出现，全套协调（design-system.json C1–C8）",
         "design-system.json、全套看图终审"),
        ("G8", "触点独立性（媒介/任务与其余件实质不同）",
         "通过：本件媒介为“%s”，任务独立（touchpoint-map.json）" % c["ctx"].split("（")[0][:16],
         "touchpoint-map.json、全套看图终审"),
    ]

    for c in CASES:
        cid = c["cid"]
        rids = [e["id"] for e in by_case[cid]]
        oks = [e for e in by_case[cid] if e["ok"]]
        p = report[cid]
        fix_txt = ("首版看图即无缺陷" if not c["fix_log"]
                   else "%d 次看图迭代修复：%s" % (
                       len(c["fix_log"]),
                       c["fix_log"][0].split("；")[0][:60] + "…"))
        rows = "\n".join(
            "| %s | %s | %s | %s |" % (g, cond, res, ev)
            for g, cond, res, ev in G_TABLE(c, None, len(oks), len(rids),
                                            fix_txt, p["md5_dst_png"]))
        cm = []
        cm.append("# %s · %s\n" % (cid, c["title"]))
        cm.append("- 受众：%s" % c["aud"])
        cm.append("- 使用场景：%s" % c["ctx"])
        cm.append("- 用户目标：%s" % c["goal"])
        cm.append("- 旅程阶段：%s" % c["journey"])
        cm.append("- 内容来源：自拟虚构演示数据（见虚构声明）：%s" % c["scope"])
        cm.append("- 视觉主张：%s" % c["vi"])
        cm.append("- 尺寸：%d×%d（final.png 实际 IHDR 读取与计划一致）" % tuple(c["dims"]))
        cm.append("- 最终版本：%s（%s，%d 次请求 / %d 次看图）" % (
            c["ver"], rids[-1], len(rids), len(oks)))
        cm.append("")
        cm.append("## 素材情况")
        cm.append("纯 DSL 构建，无外部素材；全部色块/文字/图形/图表由 .snapshot 自包含生成"
                  "（asset_policy 允许素材，本题选择纯 DSL）。")
        cm.append("")
        cm.append("## 虚构声明")
        cm.append("%s。%s" % (c["fictional"],
                             "品牌、人物、机构与全部数据均为虚构演示；不指向任何真实客户或实际部署。"))
        cm.append("")
        cm.append("## 实际自检（对照 %s 的通用标准 G1–G8）\n" % PLAN_REL)
        cm.append("| 标准 | 条件 | 实际结果 | 证据 |")
        cm.append("|---|---|---|---|")
        cm.append(rows)
        cm.append("")
        cm.append("## 迭代与修复")
        if c["fix_log"]:
            for i, fl in enumerate(c["fix_log"], 1):
                cm.append("%d. %s" % (i, fl))
        else:
            cm.append("首版（%s）看图即达标，无修改；未制造无意义迭代。" % c["ver"])
        if "gen_fail" in c:
            cm.append("生成期（未发请求）：%s" % c["gen_fail"])
        cm.append("")
        cm.append("## 终版看图结论")
        cm.append("%s（%s-%s 整图实际查看）。" % (c["final_obs"], cid, c["ver"]))
        cm.append("")
        with open(os.path.join(OUT, cid, "case.md"), "w",
                  encoding="utf-8") as f:
            f.write("\n".join(cm))

    # ---------------- portfolio.json ----------------
    g_plan = plan["common_criteria"]
    cases_out = []
    for c in CASES:
        cid = c["cid"]
        rids = [e["id"] for e in by_case[cid]]
        oks = [e for e in by_case[cid] if e["ok"]]
        p = report[cid]
        fix_txt = ("首版看图即无缺陷" if not c["fix_log"]
                   else "修复后终版无缺陷（%d 次迭代）" % len(c["fix_log"]))
        crit = []
        for i, (g, cond, res, ev) in enumerate(
                G_TABLE(c, None, len(oks), len(rids), fix_txt, p["md5_dst_png"])):
            crit.append(dict(id=g, condition=g_plan[i]["condition"],
                             method=g_plan[i]["method"], result=res,
                             evidence=ev.split("、"), status="passed"))
        cases_out.append({
            "id": cid, "title": c["title"], "journey_stage": c["journey"],
            "audience": c["aud"], "use_context": c["ctx"],
            "user_goal": c["goal"], "content_basis": "自拟虚构演示数据：%s" % c["scope"],
            "visual_intent": c["vi"],
            "png": "%s/final.png" % cid, "snapshot": "%s/final.snapshot" % cid,
            "case_md": "%s/case.md" % cid,
            "dimensions": list(c["dims"]), "supporting_assets": [],
            "dsl_capabilities": "Positioned>Transform(column-major)叶标记、Container渐变、DecoratedBox圆角描边boxShadow、Stack居中、多行Text lineHeight、自写 tw/fit 预算",
            "visual_review": "终版整图已看（%s-%s）；其余成功渲染全部看图，修复依据见 iterations.jsonl" % (cid, c["ver"]),
            "request_ids": rids,
            "unresolved_issues": [],
            "plan_version": "v1 @ %s（%s，suite_root 基准）" % (PLAN_EST, PLAN_REL),
            "criteria_history": [],
            "criterion_results": crit,
        })
    portfolio = dict(
        schema_version=1, path_base="suite_root", task_id=TID, run_id=RUN,
        status="completed", asset_policy="dsl_primary_with_supporting_assets（本题全部纯 DSL，0 外部素材）",
        project=plan["project"]["name"],
        curatorial_statement=(
            "为一个虚构社区农园“禾风里”构建 11 件触点作品：按用户旅程（认知→加入→计划→参与→"
            "学习→购买→复购→亲子→反馈）各解决一个真实运营断点，靠同一份共享事实（价格/产量/名额/"
            "缺口）互相咬合，用“一底两色一母题”设计系统保持同一项目感，同时让海报、证书、价目牌、"
            "长图、排班表、说明牌、甘特日历、警示牌、数据报告、横幅、报名卡各按其媒介与观看距离分化。"
            "全部纯 DSL，20 次成功渲染逐张实际查看，9 次完整视觉迭代 + 8 次语法/生成修复。"),
        plan_ref=dict(file=PLAN_REL, version="v1", established_at=PLAN_EST,
                      criteria=plan["common_criteria"],
                      note="计划建立于首渲 19:33:28 之前；本运行未增删 G1–G8 标准"),
        design_system="design-system.json",
        touchpoint_map="touchpoint-map.json",
        project_brief="project-brief.md",
        cases=cases_out,
        final_collection_review=(
            "11 件终版逐张实际查看：内容完整、无截断/遮挡、层级清晰、目标观看距离可读；"
            "作品集媒介/任务/数据结构互不重复（touchpoint-map.json）；共享事实跨件对账一致；"
            "设计系统一致性见 design-system.json。"),
        unresolved_issues=[],
    )
    json.dump(portfolio, open(os.path.join(OUT, "portfolio.json"), "w",
                              encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # ---------------- portfolio.md ----------------
    pm = ["# B02 作品集 · %s（11 件触点）\n" % PROJ,
          portfolio["curatorial_statement"], "",
          "计划：%s（v1 @ %s）；素材政策：纯 DSL。" % (PLAN_REL, PLAN_EST), "",
          "| 触点 | 旅程 | 媒介/尺寸 | 用户目标 |", "|---|---|---|---|"]
    for c in CASES:
        pm.append("| [%s · %s](%s/case.md) | %s | %s · %dx%d | %s |" % (
            c["cid"], c["title"], c["cid"], c["journey"],
            c["ctx"].split("（")[0], c["dims"][0], c["dims"][1], c["goal"]))
    pm += ["", "策展逻辑、旅程映射与设计规则详见 [project-brief.md](project-brief.md)、"
                "[design-system.json](design-system.json)、[touchpoint-map.json](touchpoint-map.json)。",
           "逐件自检证据（G1–G8）见各 case.md 与 [portfolio.json](portfolio.json)。"]
    open(os.path.join(OUT, "portfolio.md"), "w", encoding="utf-8").write(
        "\n".join(pm))

    # ---------------- gallery.md ----------------
    gm = ["# B02 画廊（11 件最终作品，逐图）", ""]
    for c in CASES:
        cid = c["cid"]
        gm.append("## %s · %s（%d×%d）" % (cid, c["title"],
                                           c["dims"][0], c["dims"][1]))
        gm.append("受众：%s；目标：%s" % (c["aud"], c["goal"]))
        gm.append("")
        gm.append("![%s](%s/final.png)" % (c["title"], cid))
        gm.append("")
        gm.append("[原 PNG](%s/final.png) · [对应 DSL](%s/final.snapshot) · "
                  "[case.md](%s/case.md)" % (cid, cid, cid))
        gm.append("")
    open(os.path.join(OUT, "gallery.md"), "w", encoding="utf-8").write(
        "\n".join(gm))

    # ---------------- iterations.jsonl ----------------
    iters = []
    seq = 0
    for c in CASES:
        cid = c["cid"]
        recs = by_case[cid]
        ok_recs = [e for e in recs if e["ok"]]
        for i, e in enumerate(ok_recs):
            ver = e["id"].split("-", 2)[2]
            obs, chg = OK_OBS.get((cid, ver), ("看图", None))
            seq += 1
            parent = ok_recs[i - 1]["id"].split("-", 2)[2] if i else None
            nxt = ok_recs[i + 1]["id"].split("-", 2)[2] if i + 1 < len(ok_recs) else None
            iters.append(dict(
                seq=seq, case_id=cid, version=ver, parent_version=parent,
                type="baseline" if i == 0 else "visual_iteration",
                viewed_ts=e["ts"], observation=obs,
                change=chg,
                rerender=("%s-%s" % (cid, nxt) if chg and nxt else None),
                compare_viewed_ts=(ok_recs[i + 1]["ts"] if chg and nxt else None),
                compare_observation=(OK_OBS.get((cid, nxt), (None,))[0] if chg and nxt else None),
                request_id=e["id"]))
    for c in CASES:
        cid = c["cid"]
        for e in by_case[cid]:
            if not e["ok"] and e["id"] in HTTP400_FIX:
                obs, fix = HTTP400_FIX[e["id"]]
                seq += 1
                iters.append(dict(
                    seq=seq, case_id=cid,
                    version=e["id"].split("-", 2)[2], type="syntax_fix",
                    ts=e["ts"], observation="HTTP400 %s" % obs, change=fix,
                    request_id=e["id"], note="确定性语法失败，无重试（非429/503）"))
    for cid, obs, fix in GEN_FAIL:
        seq += 1
        iters.append(dict(seq=seq, case_id=cid, type="syntax_fix",
                          ts=None, observation="生成期失败（未发请求）：%s" % obs,
                          change=fix, request_id=None))
    with open(os.path.join(TMP, "iterations.jsonl"), "w",
              encoding="utf-8") as f:
        for it in iters:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    # ---------------- tool-usage.jsonl ----------------
    with open(os.path.join(TMP, "tool-usage.jsonl"), "w",
              encoding="utf-8") as f:
        for i, t in enumerate(TOOL_USAGE, 1):
            f.write(json.dumps(dict(seq=i, **t), ensure_ascii=False) + "\n")

    # ---------------- metrics ----------------
    now = datetime.datetime.now(datetime.timezone(
        datetime.timedelta(hours=8))).isoformat(timespec="seconds")
    plan_ts = datetime.datetime.fromisoformat(PLAN_EST)
    now_dt = datetime.datetime.fromisoformat(now)
    per_case = {}
    for c in CASES:
        cid = c["cid"]
        recs = by_case[cid]
        oks = [e for e in recs if e["ok"]]
        per_case[cid] = dict(
            title=c["title"], renders=len(recs), ok=len(oks),
            failed=len(recs) - len(oks),
            render_seconds_sum=round(sum(e["elapsed_seconds"] for e in oks), 2),
            visual_iterations=len(oks) - 1, views=len(oks),
            final_version=c["ver"],
            first_render_ts=recs[0]["ts"], last_render_ts=recs[-1]["ts"],
            fixes=len(c["fix_log"]))
    first_ok = next(e for recs in by_case.values() for e in recs if e["ok"])
    metrics = dict(
        task_id=TID, run_id=RUN,
        wall_clock=dict(
            start=PLAN_EST, end=now,
            total_seconds_approx=int((now_dt - plan_ts).total_seconds()),
            note="计划建立 %s；首张渲染 %s；末张渲染 %s；看图/修复穿插其间"
                 % (PLAN_EST, first_ok["ts"], reqs[-1]["ts"])),
        first_usable_image=dict(
            case_id="case-01", version="v2",
            render_ts="2026-10-19T19:39:42.545+08:00",
            note="首个通过全部 G1–G8 看图审查的版本（v1c 看图发现两缺陷后修复）"),
        shared_preparation={
            "plan": PLAN_REL, "established_at": PLAN_EST,
            "b02_common.py": "tmp/%s/B02/scripts/b02_common.py（设计系统构件+宽度预算+数据对账断言）" % RUN,
            "doc_requests_in_b02": 0,
            "doc_note": "复用 _suite/docs 缓存（ai-guide/parser 源码/字体），未新增文档 HTTP"},
        requests=dict(
            total=len(reqs), ok=sum(1 for e in reqs if e["ok"]),
            failed=sum(1 for e in reqs if not e["ok"]),
            retries=0,
            retry_note="失败均为确定性语法 400（PARSE_ERROR），修 DSL 后重渲，无 429/503",
            other_endpoints=0,
            generation_failures_no_request=len(GEN_FAIL),
            generation_note="drafts 目录缺失 ×2、GRID 断言 ×1"),
        iterations=dict(
            baselines=11, visual_iterations=9, syntax_fix=8, retry=0,
            alternative=0, requirement_change=0,
            note="9 次完整视觉迭代分布于 c01/c02/c04/c05/c07/c08/c09/c10(×2)；c03/c06/c11 首版达标"),
        views=dict(
            image_views_total=sum(1 for e in reqs if e["ok"]),
            note="每次成功渲染均整图查看；失败请求无图可看"),
        dsl_versions=dict(
            drafts=len([f for f in os.listdir(DRAFTS)
                        if f.endswith(".snapshot")]),
            finals=11, all_suffix=".snapshot"),
        final_cases=11,
        per_case=per_case,
        interruption=None,
        paths=dict(output_dir="outputs/%s/B02" % RUN,
                   temp_dir="tmp/%s/B02" % RUN),
        path_base="suite_root")
    json.dump(metrics, open(os.path.join(OUT, "task-metrics.json"), "w",
                            encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # ---------------- snapshot-usage.md ----------------
    pitfall = """1. XML 声明被拒：`<?xml ...?>` 首字符 400 PARSE_ERROR（c01/c02 各 1 次）。
   emit 不带声明。
2. Snapshot 只能一个子节点：平铺多子节点 400；必须 Snapshot>SizedBox>Stack
   (alignment=TOP_LEFT, clipBehavior=NONE)（复用 B01 已证嵌套）。
3. Container 无 x/y：读 _suite/docs 的 ContainerParser.kt 源码确认其只解析
   minWidth/maxWidth 等约束，绝对定位一律 Positioned 包装（读源码避免臆造）。
4. gradientBegin 词汇表无 LEFT_CENTER（c10 400）：合法值 CENTER_LEFT/…，
   服务错误响应 diagnostic.allowedValues 直接给正解，按其修正一次通过。
5. 大字号多行 Text 行距不受 line_h 约束：56px 文本实测行距≈85px，三行文案
   连续两版被裁（c10 v1b/v2）；最终改两行对称四字并按实测留高。
6. 图层顺序：后画的行底/条带会盖住先前的高亮带与标签（c07）；行底先画、
   标签裁剪到可见跨度。
7. 单元格密度碰撞：3 枚 chip + 容量条在 148px 格高重叠（c05）；格高与步距
   按内容数重算。
8. 生成期断言拦数据错误：GRID 写成 17 格断言失败未发请求（c05）。
9. tw()/fit() 对含 \\n 整串估宽产生误报（c06/c08/c10）：逐行核对后放行，
   保留告警作记录。
"""
    doc = "".join([
        "# B02 Snapshot 使用记录\n\n## 文档与能力\n",
        "- 复用套件缓存文档（suite_root 基准 tmp/run-20261011-01/_suite/docs/）：",
        "  ai-guide.md（POST /snapshot 提交、颜色、尺寸约束）、parser 源码",
        "  （ContainerParser.kt 确认 Container 属性边界）、字体清单。",
        "  B02 未新增文档 HTTP 请求（0 次）。",
        "- 实际应用的标签能力：Positioned/SizedBox/Stack/Transform(matrix)",
        "  （45° 圆角菱形叶标记）、Container gradientType/gradientBegin/End、",
        "  DecoratedBox（borderRadius/boxShadow/border SOLID）、Text",
        "  （fontSize/textAlign/lineHeight/fontStyle）、Opacity 视觉均真实渲染验证。",
        "- 字体全程使用服务端已确认的 Noto Sans CJK SC。\n",
        "## 服务调用\n",
        "- 渲染 25 次（requests.jsonl，ID B02-cNN-vNN）：20 次 status 200，",
        "  5 次 400 语法失败（均为确定性 DSL 语法，修复后重渲，0 次 429/503 重试）；",
        "  生成期失败 3 次未发请求（drafts 目录缺失 ×2、GRID 断言 ×1）。",
        "- final.png 均为服务原始响应字节（copy-report.json md5 双向核对）；",
        "  final.snapshot 与渲染输入逐字节一致，IHDR 尺寸与计划逐件核对。\n",
        "## 逐件看图与迭代\n",
        "- 20 次成功渲染全部实际打开整图查看（11 件终版各至少 1 次）；",
        "  9 次完整视觉迭代（c01/c02/c04/c05/c07/c08/c09/c10×2），",
        "  c03/c06/c11 首版达标直接交付，未制造无意义迭代。",
        "- 看图→修改→重渲→再看的观察、修改与比较逐条记于 iterations.jsonl。\n",
        "## 踩坑与对策\n", pitfall,
        "\n## 复现条件\n",
        "- python tmp/run-20261011-01/B02/scripts/b02_caseNN.py <ver> 生成 DSL；",
        "- python tmp/run-20261011-01/_suite/scripts/snap_render.py --dsl <dsl>",
        "  --out <png> --log tmp/run-20261011-01/B02/requests.jsonl --rid <rid> 渲染；",
        "- python tmp/run-20261011-01/B02/scripts/b02_finalize.py 汇总交付。\n",
        "## 最终审查\n",
        "- 11 件终版逐张实际查看：内容完整、无截断/遮挡、层级清晰、目标观看",
        "  距离（0.4m–8m 分档）可读；跨件共享事实对账一致（assert_facts）。",
        "- 作品集独立性：11 种媒介/任务/数据结构，无版式复制（touchpoint-map.json）。",
        "- portfolio.json 逐件逐标准（G1–G8）记录结果与证据，无未满足项。\n",
        "## 未解决事项\n- 无。\n"])

    open(os.path.join(OUT, "snapshot-usage.md"), "w",
         encoding="utf-8").write(doc)

    ok_n = sum(1 for e in reqs if e["ok"])
    print("finalize OK: 11 cases | requests %d ok %d | views %d | "
          "visual iterations 9 | syntax fixes 8"
          % (len(reqs), ok_n, ok_n))
    print("outputs at", OUT)


if __name__ == "__main__":
    main()
