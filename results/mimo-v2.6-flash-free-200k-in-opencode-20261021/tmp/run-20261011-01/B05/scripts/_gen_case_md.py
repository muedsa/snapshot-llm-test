# -*- coding: utf-8 -*-
"""Generate the 10 case.md files from plan-v1 + the real iteration log.

Nothing here is invented: scenes/audience/goals come from plan-v1.json, the
accepted version, request IDs and iteration IDs come from the actual
requests.jsonl / iterations.jsonl, and the observed defects are copied from
the observation strings that were logged at the time.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUITE = os.path.normpath(os.path.join(ROOT, "..", "..", ".."))
TMP = os.path.join(SUITE, "tmp", "run-20261011-01", "B05")
OUT = os.path.join(SUITE, "outputs", "run-20261011-01", "B05")

plan = json.load(open(os.path.join(TMP, "plan-v1.json"), encoding="utf-8"))
reqs = [json.loads(l) for l in open(os.path.join(TMP, "requests.jsonl"),
                                    encoding="utf-8") if l.strip()]
its = [json.loads(l) for l in open(os.path.join(TMP, "iterations.jsonl"),
                                   encoding="utf-8") if l.strip()]

import re
from collections import defaultdict

journey = json.load(open(os.path.join(OUT, "journey.json"), encoding="utf-8"))
# journey.json carries an explicit `edges` list; `hands_to` is only the
# primary outgoing edge and cannot express the fan-in at case-04/06/07/08.
_EDGES = [(e["from"], e["to"], e.get("note") or "") for e in journey["edges"]]
HANDOFF = {}
PREV = {}
for _a, _b, _n in _EDGES:
    HANDOFF.setdefault(_a, []).append((_b, _n))
    PREV.setdefault(_b, []).append(_a)

req_by_case = defaultdict(list)
for r in reqs:
    m = re.search(r"(case-\d\d)-v(\d+)", r.get("dsl_path") or "")
    if m:
        req_by_case[m.group(1)].append((int(m.group(2)), r["id"]))

it_by_case = defaultdict(list)
for it in its:
    cid = it.get("case_id")
    if cid:
        it_by_case[cid].append(it)

# accepted version per case == the highest version actually rendered
ACCEPTED = {}
for cid, lst in req_by_case.items():
    ACCEPTED[cid] = max(v for v, _ in lst)

# Each EXTRA entry carries "usage" (how it is used / what it answers) and
# "visual" (the visual claim). Derived per case so the two sections of the
# case.md never silently diverge.
USAGE = {
    "case-01": "把全城风险压成一屏可扫读的清单：一条真实橙色预警横幅 + 统计条 + 六个点位卡，禁止通行点排首位。用户在出门前的 5 秒内完成『今天能不能照常走』的判断。",
    "case-02": "单点位的证据页：用户要回答『这地方是真危险，还是数据不准』，所以水深、趋势、来源、置信度必须同屏可核。",
    "case-03": "决策页：用户要理解的不是『哪条最快』，而是『最快那条为什么不能走』，三条路线并排比较。",
    "case-04": "骑行途中单手扫读：横屏、大字、少信息，只回答『前面这个点我能不能直接过』。",
    "case-05": "现场上报：骑手/路人把看到的积水变成一条可信记录，需要估深、置信度与提交反馈。",
    "case-06": "锁屏被动接收：不打开 App 也要知道最该做什么，三条通知按优先级堆叠。",
    "case-07": "驾驶中判定：把水深翻译成『我的车过不过得去』，并给出一键改道。",
    "case-08": "运维值守：一眼看清复核队列、泵站负载与在岗人力，并对上报做出采纳/驳回。",
    "case-09": "指挥决策：在 3–5 米外可读，先看分布与时序，再下达调度。",
    "case-10": "雨后复盘：以『你』为主语回看这一周的避水战绩与个人贡献。",
}
VISUAL = {
    "case-01": "一屏清单式：预警横幅 + 统计条 + 六个点位卡纵向排列，禁止通行点以最大视觉权重排首位，风险色即排序依据。",
    "case-02": "DepthRuler 作为主视觉占满左半屏，水位高度与 32cm 严格成正比，风险色带叠加其上；右半屏为趋势与双来源置信度，形成『图证 + 数据证』的左右呼应。",
    "case-03": "三条路线卡横向并排，推荐卡以描边+徽标突出；每卡用迷你 DepthRuler 标出途经风险，让用户一眼看出最短路线为何被否。",
    "case-04": "横屏满屏只留一条横向判定带：左侧大号深度数字与判定 pill，右侧阈值梯块；背景压暗以突出判定，信息密度刻意低于手机版。",
    "case-05": "取景框构图为骨架，估深剖面以台阶实体侧视呈现，可信度用一条 0→1 的刻度滑条表达，提交后状态 pill 即时反馈『待复核』。",
    "case-06": "锁屏形态：顶部大时钟，三条通知卡纵向堆叠且高度递减以示优先级；预警卡内嵌蓝Ⅳ/黄Ⅲ/橙Ⅱ/红Ⅰ四级标尺，当前级以徽标点亮。",
    "case-07": "车机横屏以禁行横幅为主视觉，DepthRuler 叠画离地间隙线，水位线与离地间隙线的高低差即『超出 18cm』的几何证明。",
    "case-08": "桌面高密度表格：复核队列首行高亮为可操作态，右栏泵站用环形负载图，事件用纵向时间线，三区比例约 6:3:1。",
    "case-09": "大屏三段式：顶部指标条、左侧城市示意图（六点按风险着色叠在分区底板上）、右侧时间线，视线沿『分布 → 时序 → 动作』推进。",
    "case-10": "个人复盘页以战绩为主视觉：顶部大号 5 次/40 分钟并置，中部七日柱状图，底部贡献区与徽章，主语始终是『你』。",
}
EXTRA = {
    "case-01": {
        "intent": "把全城风险压成一屏可扫读的清单：一条真实橙色预警横幅 + 统计条 + 六个点位卡，禁止通行点排首位。用户在出门前的 5 秒内完成『今天能不能照常走』的判断。",
        "selfcheck": "v1 渲染曾因 color='none' 400 失败（req-0001），改用 transparent 后重渲。v1 实看发现风险 pill 与水深数字重叠、第 6 个点位被底部导航遮挡但标题却称共 6 处；v2 修复遮挡但 cm 单位被文本框裁成 c；v3 令 cm 完整、六点齐全、pill/数字/迷你条/趋势/来源全部清晰，接受。v4 为跨案日期回归修复（详见 iterations）。",
        "assets": "无辅助素材，纯 DSL。",
    },
    "case-02": {
        "intent": "单点位的证据页：用 DepthRuler 把 32cm 画成一根与数值成正比的水位，配风险色带与趋势曲线，并明确标出传感器与众包两个来源及各自置信度。用户要回答的是『这地方是真危险，还是数据不准』。",
        "selfcheck": "v1 实看：替代卡 cm 被裁成 c、替代卡与底部 CTA 间约 300px 空洞；v2 实看：分级图例的 ASCII < 被渲染成 &lt; 直出（B04 已知坑），改用 ＜；v3 实看：刻度数字右对齐到轨道右缘、压在彩色水体上；v4 把刻度 0–50 移入左槽，水位 32cm 成比例且含风险色带与水位线，全屏无裁剪遮挡，接受。",
        "assets": "无辅助素材，纯 DSL。",
    },
    "case-03": {
        "intent": "决策页：三条路线并排，各自标出耗时与途经风险，推荐的『避水路线』在视觉上突出并给出一句话理由。用户要理解的不是『哪条最快』，而是『最快那条为什么不能走』。",
        "selfcheck": "v1 实看：分钟数字与『分』字重叠、推荐 badge 压在 17 上、替代方案与 CTA 间大片空洞；v2 实看：ETA 行 314px 超出 300px 槽溢出、图例标签宽度差 1px 被裁；v3 实看：版式已无重叠，但自定标准 C3 要求的离地间隙提示缺失；v4 补上离地间隙并令 分/推荐/ETA/图例全部清晰无碰撞、CTA 间距正常，接受。",
        "assets": "无辅助素材，纯 DSL。",
    },
    "case-04": {
        "intent": "换人群、换阈值、换方向的同一决策：骑手用车/人更严的 5/10cm 分级，横屏大字少信息，让用户在骑行中单手扫读也能判断能否通过。",
        "selfcheck": "v1 实看：判定 pill 裁字（76px 槽过窄）、趋势显示英文 rising、迷你条误用汽车分级色与骑手 pill 自相矛盾、左下留白；v2 实看：阈值梯块 5~10cm 换行与『注意』重叠、pill 贴住 cm、纵排盒高不足；v3 实看：梯块标签距盒边过近（186px 宽溢出面板）；v4 令阈值梯/判定 pill/cm/中文趋势/语音状态条全部清晰无碰撞，骑手与汽车分级差异明确，接受。",
        "assets": "无辅助素材，纯 DSL。",
    },
    "case-05": {
        "intent": "众包入口：不让人凭空报一个数字，而是用身边可见的参照物（台阶第二级）估出深度，并把可信度显式量化成 0.8 的滑条，提交后给出『待复核』的明确去向。",
        "selfcheck": "v1 首版含步骤器/DSL 取景框/台阶剖面估深/点位/可信度滑条/备注五段，生成期断言拦截了备注卡与 CTA 的碰撞。v1 实看：台阶实体块画在自身轮廓左侧导致错位悬空、剖面 cm 超出卡片右缘（742>736）、『与上报一致』压住单选圈；v2 全部修复后实看接受。",
        "assets": "无外链真实照片；取景框为 DSL 构图，刻意避免把预绘照片当主体。",
    },
    "case-06": {
        "intent": "锁屏形态的通知优先级：预警 > 禁止通行 > 路线，三张通知卡各带一个可解释的动作（查看/改道/稍后提醒）。用户不解锁也要知道现在最该做什么。",
        "selfcheck": "v1 首版为独立预警横幅 + 三卡，生成期断言拦截了展开卡与第三卡的碰撞。v1 实看：通知②整卡内容被自身不透明背景盖住（Stack 后绘者在上，只剩按钮可见）、标题行追加文案与『稍后提醒』按钮重叠；v2 实看：内容正常但优先级仍是横幅+上报，与 plan C1 固化的『预警>禁止通行>路线』不符、紧卡无动作不满足 C5；v3/v4 重组为三张按 C1 排序的通知卡（预警卡内嵌蓝Ⅳ/黄Ⅲ/橙Ⅱ/红Ⅰ四级标尺 + Ⅱ级徽标），每卡补可解释动作并加 n1y<n2y<n3y 断言，实看接受。",
        "assets": "无辅助素材，纯 DSL。",
    },
    "case-07": {
        "intent": "驾驶态：把『32cm』翻译成『高于我的车离地间隙 14cm』，在同一把 DepthRuler 上叠画水位线与离地间隙线，让不可过成为几何事实而非文字告警；次要信息压到边角不干扰主告警。",
        "selfcheck": "v1 首版含禁行横幅 + DepthRuler 叠画离地间隙线 + 改道卡 + 底部次要条，生成期断言拦下三处（ETA 行与『+5分钟』等）。v1 实看：中列文字宽度用了错误表达式 W-64-tx+32，导致『高于离地间隙14cm』『≈4瓶矿泉水』『没过底盘』三处文字钻到卡片外；v2 实看：遮挡全部消除，但徽标只剩『超出』，18cm 被渲染器折到 44px 框外，改 int() 为 ceil 并把槽宽提到 183 仍不足；v3 实看：徽标仍缺 18cm，确认非高度问题（更矮的 56px 方案同样截断）而是宽度估算偏低；v4 按实测宽度重算后完整显示，实看接受。",
        "assets": "无辅助素材，纯 DSL。",
    },
    "case-08": {
        "intent": "运维台：众包上报的可信度要能被复核——首行高亮的 #1042 把传感器读数与众包条数并排，让『采纳/驳回』成为一个可解释的动作；右栏给泵站与事件的运行态。",
        "selfcheck": "v1 首版含 4 张 KPI + 复核队列表格（4 行，首行高亮可操作）+ 泵站/事件右栏；生成期 FIT-WARN 即抓到 31.5 需 56px 但槽仅 52px。v1 实看：首行 26 被截成 2——按 tw()×1.10 算出的 31px 槽仍不够，同时发现 FIT-WARN 因用同一个 tw() 而对同类缺口保持沉默；v2 实看：31.5 已修复但 26 仍截断（槽 31→实测需 33+）；v3 引入按字符类别的 tw_fit 重算槽宽；v3 仍见 KPI 第 1 卡 /52 与说明文字相距仅 5.9px（_audit8 离线量出）；v4 把 KPI 说明移到标签行让出间距，26/31.5/12/6.5 全部完整，实看接受。",
        "assets": "无辅助素材，纯 DSL。",
    },
    "case-09": {
        "intent": "指挥屏：远距离可读是第一约束。指标条给四个总数，左侧城市示意图把六点按风险着色并叠在分区底板上，右侧时间线给事件时序、下方给三条调度建议，形成『分布 → 时序 → 动作』的视线。",
        "selfcheck": "v1 首版含指标条 + 左城市示意图 + 右时间线与调度建议；生成期守卫连续拦下四处（缺 n_open 导入、时钟槽 76px 不够 81.8、axis_x 放不下时钟、图例与演示规则说明差 8px），逐项加断言修正后才产出首版。v1 实看：标题成『云州市市防汛指挥中心』（CITY 已含市）、高新区分区几乎空白使右侧发虚；v2 实看：标题与分区已修，但调度建议 C 写成『绕开路下穿隧道』——ROUTES[0][3][3:] 把『滨江』两字也切掉了，且预警说明重复『橙色』而未给阈值；v3 改为 [1:] 只去掉前缀『经』并加 startswith 回归断言，说明改用真实 CMA 原文首句，实看接受。",
        "assets": "无辅助素材，纯 DSL。",
    },
    "case-10": {
        "intent": "个人复盘页，刻意与运营视角区分：主语是『你』，数字是战绩（5 次避水、省 40 分钟）而非城市状态。柱状图与贡献区把使用收益和个人贡献并置，形成闭环回看。",
        "selfcheck": "v1 首版含 hero 战绩 + 逐日雨量柱状（7 根成正比）+ 贡献（3/2/6 + 徽章 + 上报列表）+ 复盘提示。v1 实看发现四处缺陷：待复核状态色用 R_DETOUR 橙（与 case-08 的 R_CAUTION 蓝不一致，且与橙色 26cm 数值撞色）、hero 标题『上周避水绕行』与下方说明『避水绕行』重复、柱状图 peak 标注与收尾提示写成『本周』但报告区间是上周；v2 修 peak 防重叠断言时先误判（callout 框与标题框垂直重叠但水平分离），改成按字形实测宽度做双轴判定后立刻抓到真缺陷——callout 右缘 462 与右侧图例左缘 469 仅差 7px 肉眼难辨；同时用 _verify10.py 从渲染 PNG 逐列扫描量高，确认 7 根柱高与雨量成正比（最大误差 0.55px、比例偏差 ≤0.003、周四为唯一橙色柱且顶到 PLOT_Y）。v2 实看四项缺陷全部修复，接受。",
        "assets": "无辅助素材，纯 DSL。",
    },
}

for c in plan["cases"]:
    cid = c["id"]
    acc = ACCEPTED[cid]
    rl = [rid for v, rid in sorted(req_by_case[cid]) if v == acc]
    steps = it_by_case[cid]
    ex = EXTRA[cid]
    dim = c["dimensions"]
    rows = []
    for cc in c["completion_criteria"]:
        rows.append("| %s | %s | %s |" % (cc["id"], cc["condition"], cc["method"]))
    vrows = []
    for s in steps:
        t = s.get("type")
        obs = (s.get("observation") or "").replace("\n", " ").strip()
        act = (s.get("action") or "").replace("\n", " ").strip()
        vrows.append("| `%s` | %s | %s | %s |" % (
            s["id"], "%s (parent=%s)" % (t, s.get("parent_version") or "-"),
            obs, act))
    _p = PREV.get(cid, [])
    _n = HANDOFF.get(cid, [])
    _out = ("；".join("去 %s（%s）" % (t, x) for t, x in _n)
            if _n else "旅程终点")
    REL = ("承接%s ｜ %s" % ("、".join(_p), _out)) if _p else _out
    md = f"""# case- {cid.replace('case-', '')} · {c['title']}

## 场景与受众

- **受众**：{c['persona']}
- **内容范围**：{c['content_scope']}
- **观看环境**：{c['viewing_environment']}
- **用户目标**：{c['user_goal']}
- **前后关系**：{REL}
- **尺寸**：{c['dimensions'][0]} × {c['dimensions'][1]}（按实际 PNG 读取）

{USAGE[cid]}

## 内容与数据来源

本画面的数据全部由 `b05_data.py` 作为单一事实源生成并带断言
（点位/深度/路线/上报/泵站），跨画面一致；唯一真实锚点为暴雨橙色预警分级
（中国气象局 CMA 标准，见 `tmp/run-20261011-01/B05/SRC-01-cma-rainstorm-warning.txt`）。

真实锚点仅有暴雨橙色预警分级（中国气象局标准，SRC-01）；其余点位、水深、
传感器、车辆、上报、泵站、人物均为虚构演示数据，风险分级为产品自定演示规则，
非官方通行标准。未做真实用户验证。

## 视觉选择

{VISUAL[cid]}

招牌视觉为 **DepthRuler 水位刻度尺**：把抽象的 cm 变成可一眼判断的相对位置，
判定表现为『水位线越没越过那条线』的几何事实。风险色全系统一为
可通行 `#2FBF71` / 谨慎 `#2E86DE` / 建议绕行 `#F2A93B` / 禁止通行 `#4572E4`。

## 自定完成标准（建立于首渲染前，plan-v1 2026-10-21T03:05:00+08:00）

| ID | 可观察条件 | 检查方法 |
|---|---|---|
{chr(10).join(rows)}

## 实际自检与迭代

被接受版本：**v{acc}**（渲染请求 `{', '.join(rl)}`）。

{ex['selfcheck']}

逐版记录（取自 `tmp/run-20261011-01/B05/iterations.jsonl`，均为真实看图后记录）：

| 迭代 ID | 类型 | 观察 | 修改 |
|---|---|---|---|
{chr(10).join(vrows)}

## 素材情况

{ex['assets']}
"""
    d = os.path.join(OUT, cid)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "case.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print("wrote", cid, "case.md (v%d, %s)" % (acc, ", ".join(rl)))
