# -*- coding: utf-8 -*-
"""Build B05 portfolio.json from plan-v1 + the real logs.

Criteria are plan-v1's, verbatim. Criterion results are authored from what was
actually verified per case (assertions + real image views); nothing is marked
pass without a named method and evidence.
"""
import json
import os
import re
from collections import defaultdict

SUITE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "..", "..", "..", ".."))
TMP = os.path.join(SUITE, "tmp", "run-20261011-01", "B05")
OUT = os.path.join(SUITE, "outputs", "run-20261011-01", "B05")

plan = json.load(open(os.path.join(TMP, "plan-v1.json"), encoding="utf-8"))
journey = json.load(open(os.path.join(OUT, "journey.json"), encoding="utf-8"))
reqs = [json.loads(l) for l in open(os.path.join(TMP, "requests.jsonl"),
                                    encoding="utf-8") if l.strip()]
its = [json.loads(l) for l in open(os.path.join(TMP, "iterations.jsonl"),
                                   encoding="utf-8") if l.strip()]

req_by_case = defaultdict(list)
for r in reqs:
    m = re.search(r"(case-\d\d)-v(\d+)", r.get("dsl_path") or "")
    if m:
        req_by_case[m.group(1)].append((int(m.group(2)), r["id"]))
its_by_case = defaultdict(list)
for it in its:
    if it.get("case_id"):
        its_by_case[it["case_id"]].append(it["id"])

ACCEPTED = {c: max(v for v, _ in l) for c, l in req_by_case.items()}

CAPS = {
    "case-01": ["Positioned 绝对定位排版", "Text 多字号/色/行高",
                "SizedBox+DecoratedBox 卡片与迷你水深条",
                "risk_color 统一上色 + 统计计数由数据派生"],
    "case-02": ["DepthRuler（DecoratedBox 刻度 + 水位线 + 风险色带）",
                "趋势折线（手造线段阵）", "双来源与置信度标注",
                "水位高度与数值成正比的几何断言"],
    "case-03": ["路线卡阵列", "迷你 DepthRuler 标途经风险",
                "推荐徽标与描边强调", "离地间隙判定线"],
    "case-04": ["横屏满屏布局", "阈值梯块（骑手 5/10cm）",
                "判定 pill 与风险色", "语音播报状态条"],
    "case-05": ["步骤器", "DSL 取景框（未外链照片）",
                "台阶剖面估深图元", "可信度刻度与状态 pill"],
    "case-06": ["锁屏 chrome（时钟/日期/通知堆叠）", "通知卡高度递减层级",
                "四级预警标尺 蓝Ⅳ/黄Ⅲ/橙Ⅱ/红Ⅰ + Ⅱ级徽标", "可解释动作按钮"],
    "case-07": ["车机横屏布局", "DepthRuler 叠画离地间隙线",
                "禁行横幅主视觉", "改道结果反馈卡"],
    "case-08": ["表格行列与首行高亮可操作态", "环形泵站负载图",
                "纵向事件时间线", "状态 pill 与全局状态色一致"],
    "case-09": ["城市示意底板（分区 + poly 河道 + 风险着色点位）",
                "指标条", "时序时间线", "调度建议卡与跨案闭环引用"],
    "case-10": ["柱状图（几何与数值严格成正比，像素校验）",
                "避水次数点阵", "手绘徽章（circle+seg）",
                "第一人称战绩排版 + 状态 pill"],
}

# ---- authored from actual verification; method + evidence for each ----
RES = {
 "case-01": [
  ("C1", "pass", "逐字核对渲染文本",
   "req-0002..0004/0031 全 200；v1–v4 整图实看横幅为『3小时内降雨量将达50毫米以上』并标注『中国气象局《暴雨预警信号》标准（真实）』"),
  ("C2", "pass", "数据驱动断言 + 看图",
   "六点名/水深/风险色由 POINTS 派生并断言与 b05_data 一致，禁止通行点 P1 排首位；v3/v4 实看确认"),
  ("C3", "pass", "计数断言",
   "n_blocked/n_detour/n_caution/n_open 由 POINTS 计算并断言合计=6"),
  ("C4", "pass", "预算 + 每版实看",
   "v2 修第 6 点被底栏遮挡（标题称 6 处却只见 5 处）、v3 修 cm 被文本框裁成 c；v3/v4 实看名/深/标签清晰无裁剪"),
  ("C5", "pass", "内容审查 + 实看",
   "底部导航 5 项（水情/地图/上报/提醒/我的）各对应本题一张画面，作用可解释；v4 实看确认"),
 ],
 "case-02": [
  ("C1", "pass", "几何断言 + 看图",
   "水位高度与 32cm 成正比由 geometry 断言；v4 实看水位线落在 32 刻度并含风险色带"),
  ("C2", "pass", "数据驱动 + 看图",
   "趋势为上升，趋势曲线由数据派生并与 32cm 上升事实一致"),
  ("C3", "pass", "内容审查",
   "传感器 WL-BJ-001 与众包 4 条双来源分别标注，各自置信度可见"),
  ("C4", "pass", "内容审查 + 断言",
   "替代建议引用 P4 解放路地道 8cm 可通行，该点真实存在于 POINTS 并断言"),
  ("C5", "pass", "每版实看",
   "v1 修替代卡 cm 裁成 c 与 300px 空洞、v2 修 ASCII < 转义成 &lt;、v3 修刻度数字压在彩色水体上；v4 实看无遮挡无溢出"),
 ],
 "case-03": [
  ("C1", "pass", "断言 + 看图",
   "推荐为避水路线且其途经点 ['P3','P4'] 不含 P1，断言通过；v4 实看"),
  ("C2", "pass", "数据驱动 + 看图",
   "12/17/21 分钟与 ROUTES 逐一相等，每张卡标注途经风险点"),
  ("C3", "pass", "断言 + 内容审查",
   "CAR_CLEAR_MM=140 → 净空 14cm，P1 32cm 大于净空判定不可过；v3 实看发现该提示缺失后 v4 补齐"),
  ("C4", "pass", "整图实看",
   "推荐卡描边+徽标突出并给出一句话理由"),
  ("C5", "pass", "每版实看",
   'v1 修「分」字与数字重叠、推荐 badge 压住 17、v2 修 ETA 行 314px 超出 300px 槽与图例 1px 裁切、v3 补离地间隙；v4 实看全部无碰撞'),
 ],
 "case-04": [
  ("C1", "pass", "断言 + 看图",
   "使用 ped_risk_of 分级阈值 5/10cm，与汽车分级差异在图上明确区分；断言通过"),
  ("C2", "pass", "整图实看",
   "横屏大字/少信息/强对比，v4 实看可快速扫读"),
  ("C3", "pass", "数据驱动 + 看图",
   "P4 8cm 判注意、P3 15cm 判绕行，与骑手分级一致"),
  ("C4", "pass", "内容审查",
   "ETA 与接单效率信息给出且可解释"),
  ("C5", "pass", "每版实看",
   "v1 修判定 pill 裁字（76px 过窄）/趋势显示英文 rising/迷你条误用汽车色、v2 修 5~10cm 换行压住「注意」、v3 修梯块标签距盒边过近；v4 实看无碰撞"),
 ],
 "case-05": [
  ("C1", "pass", "断言 + 看图",
   "参照台阶第二级估深约 26cm，与 REPORT.est_depth 一致并断言"),
   ("C2", "pass", "整图实看",
    "可信度为带 低/一般/高 三刻度的滑条，滑块落在 0.80 位置，右上大字显示 0.80，说明行写明 0.80"),
   ("C3", "pass", "整图实看 + 跨案断言",
    "提交后为只读态：标题栏『已提交』pill，三段步骤条 已提交 08:07 → 待复核(当前状态) → 已采纳(复核通过后)，主 CTA 已变为『查看复核进度』；待复核取 R_CAUTION 蓝，与 case-08 队列首行同值"),
   ("C4", "pass", "逐字段比对 + 断言",
    "画面呈现 站前广场地下通道 · 城南区 · WL-CN-002 · 实测 26cm，与 POINTS 中 P6 条目及 REPORT 逐字段相同（est_depth 26.0 / status 待复核 / submitted 08:07 / confidence 0.8）；b05_data 导入即跑的断言全部 ALL PASS。内部编号 P6 不直接印在画面上"),
  ("C5", "pass", "DSL 自证 + 每版实看",
   "取景框为 DSL 构图，未外链真实照片，作用可解释；v1 实看修台阶实体块错位悬空/剖面 cm 越出卡右缘(742>736)/「与上报一致」压住单选圈后 v2 接受"),
 ],
 "case-06": [
  ("C1", "pass", "断言 + 实看",
   "三卡顺序为 预警 > 禁止通行 > 路线，加 n1y<n2y<n3y 断言；v3 实看发现与 C1 不符后 v4 重组，实看确认"),
  ("C2", "pass", "整图实看",
   "锁屏形态可辨：大时钟 + 日期 + 通知堆叠，非普通列表页"),
  ("C3", "pass", "逐字核对",
   "橙色预警文案为中国气象局真实标准原文"),
  ("C4", "pass", "每版实看",
   "v2 修通知②整卡内容被自身不透明背景盖住（Stack 后绘者在上）与标题行压住「稍后提醒」；v4 实看三卡层级清晰无遮挡"),
  ("C5", "pass", "内容审查 + 实看",
   "三卡动作逐条可解释：预警卡『了解暴雨预警分级』、禁行卡『建议立即改走解放路地道』(改道)、路线卡『查看路线』+『稍后提醒』；v3 实看发现紧卡缺动作后 v4 补齐"),
 ],
 "case-07": [
  ("C1", "pass", "断言 + 实看",
   "DepthRuler 叠画离地间隙线，32cm 与 140mm 对比可视化，判定『不可过』与 car_passable=False 一致"),
  ("C2", "pass", "整图实看",
   "车机横屏大字强对比，v4 实看可在驾驶中扫读"),
  ("C3", "pass", "内容审查 + 实看",
   "改道动作与结果（走避水路线 17 分钟）明确反馈"),
  ("C4", "pass", "内容审查",
   "禁行原因一句话可解释：高于离地间隙"),
  ("C5", "pass", "每版实看",
   'v2 修中列三处文字因宽度表达式 W-64-tx+32 钻到卡外，v3/v4 修徽标缺 18cm（确认为宽度估算偏低而非高度问题，D 方案 56px 同样截断）；v4 实看次要信息不干扰主告警'),
 ],
 "case-08": [
  ("C1", "pass", "断言 + 实看",
   "复核队列首行为 #1042 站前广场 26cm 待复核，与 case-05 提交在点位/深度/状态/时间/置信度五项逐一相等并断言"),
  ("C2", "pass", "断言",
   "传感器/泵站/事件计数与 OPS 一致；P6 传感器读数 26.0cm 与上报一致"),
  ("C3", "pass", "整图实看",
   "桌面形态信息密度合理，队列/泵站/事件三区约 6:3:1 分区清晰"),
  ("C4", "pass", "断言 + 实看",
   "采纳/驳回动作可解释，状态色与全局一致（待复核 #2E86DE / 已采纳 #2FBF71 / 已驳回 MUTED），case-10 断言同值"),
  ("C5", "pass", "每版实看 + 离线量测",
   'v1 FIT-WARN 抓到 31.5 需 56px 但槽 52，v1 实看首行 26 被截成 2 且发现 FIT-WARN 因用同一个 tw() 对同类缺口沉默；v3 引入按字符类别的 tw_fit，v4 用 _audit8 量出 KPI 说明与 /52 仅距 5.9px 后移到标签行；终版四行数字完整无溢出重叠'),
 ],
 "case-09": [
  ("C1", "pass", "断言 + 实看",
   "6 点按 risk_color 着色且半径随深度单调，分区 tally 合计=6 断言；v3 实看"),
  ("C2", "pass", "断言 + 实看",
   "时间线 08:00→08:14 严格递增断言，四个事件与 ESCALATION 一致并含触发方"),
  ("C3", "pass", "整图实看",
   "大屏 3–5 米可读：指标值 62px、点位深度 34px、三级层级分明"),
  ("C4", "pass", "内容审查",
   "调度 A/B/C 分别呼应 case-05（众包 5 条 + WL-CN-002 + #1042）、case-08（2 座泵站可用）、case-07（避水路线 17 分钟）"),
  ("C5", "pass", "断言 + 每版实看",
   "v1 修标题成『云州市市防汛指挥中心』（CITY 已含市）与高新区分区空白、v2 实看发现 ROUTES[0][3][3:] 把『滨江』也切掉成『绕开路下穿隧道』、v3 改 [1:] 并加 startswith 回归断言；成对点位/标签重叠断言通过，无裁剪"),
 ],
 "case-10": [
  ("C1", "pass", "数据驱动断言 + 实看",
   "5 次 / 40 分钟 / 3 上报 / 2 采纳 / 6 点全部由 WEEK 派生并断言；hero 与贡献区实看核对"),
  ("C2", "pass", "像素量测",
   "_verify10.py 从渲染 PNG 逐列扫描量高：7 根柱高与 rain_mm 成正比，最大误差 0.55px、比例偏差 ≤0.003，周四为唯一橙色柱且顶到 PLOT_Y=580"),
  ("C3", "pass", "整图实看",
   "第一人称战绩语气（『上周战绩』『你的贡献』），非运营视角"),
  ("C4", "pass", "断言 + 实看",
   "#1042 为列表首行且状态待复核；断言 case10 状态映射与 case-08 完全相同，上报行 ID 与 case-05 RPT_ID 一致"),
  ("C5", "pass", "断言 + 每版实看",
   "v1 修待复核误用 R_DETOUR 橙（与 case-08 的 R_CAUTION 蓝不一致且与橙色 26cm 撞色）、hero 标题与说明重复、三处『本周』应为『上周』；v2 按字形实测宽度做双轴判定后抓到 callout 右缘 462 与图例左缘 469 仅差 7px 并修复；实看无裁剪遮挡，柱状标签可读"),
 ],
}

HISTORY = {
    "case-10": [{
        "standard_id": "C1/时间口径",
        "old": "plan-v1 content_scope 措辞『本周避水绕行 5 次…』",
        "new": "画面标注为上周 10月12日–10月18日，并加日期完整性断言",
        "reason": "运行日 2026-10-21 为周三，而 WEEK 含完整七天（含周四–周日）；称『本周』等于报告尚未发生的日期",
        "evidence": "case-10 断言 ws.weekday()==0 / we.weekday()==6 / (we-ws).days==6 / NOW_DATE>WEEK_END_ISO；iterations v1/v2",
        "effective_at": "v1 起（首版即以上周标注）",
    }],
}

VISUAL = {
    "case-01": "v1 因 color='none' 400 失败（req-0001），改 transparent 后重渲；v1 实看风险 pill 与水深数字重叠、第 6 点被底栏遮挡；v2 遮挡修复但 cm 裁成 c；v3 全部清晰接受；v4 为跨案日期回归修复后复看接受",
    "case-02": "v1 实看 cm 裁切与 300px 空洞；v2 实看 ASCII < 转义直出；v3 实看刻度压彩色水体；v4 实看接受",
    "case-03": "v1 实看分字重叠/推荐 badge 压 17；v2 实看 ETA 溢出与图例 1px 裁切；v3 实看发现 C3 离地间隙缺失；v4 实看接受",
    "case-04": "v1 实看 pill 裁字/英文 rising/迷你条色系矛盾；v2 实看换行重叠；v3 实看标签距盒边过近；v4 实看接受",
    "case-05": "v1 生成期断言拦截备注卡与 CTA 碰撞；v1 实看台阶错位悬空/剖面越界/单选圈被压；v2 实看接受",
    "case-06": "v1 生成期断言拦截展开卡碰撞；v1 实看整卡被自身背景盖住；v2 实看内容正常但优先级与 C1 不符；v3/v4 重组为三张按优先级通知卡后实看接受",
    "case-07": "v1 生成期断言拦下三处；v1 实看三处文字钻到卡外；v2 遮挡消除但徽标缺 18cm；v3 确认非高度问题；v4 实看接受",
    "case-08": "v1 生成期 FIT-WARN 抓到 31.5 槽不足；v1 实看 26 被截成 2 且 FIT-WARN 沉默；v2 仍截断；v3 引入 tw_fit；v4 实看接受",
    "case-09": "v1 生成期守卫连拦四处后出首版；v1 实看双市标题与空分区；v2 实看切字缺陷与说明冗余；v3 实看接受",
    "case-10": "v1 实看四处缺陷；v2 修 callout 与图例差 7px 并通过像素量测，实看接受",
}

cases = []
for c in plan["cases"]:
    cid = c["id"]
    acc = ACCEPTED[cid]
    rl = [rid for v, rid in sorted(req_by_case[cid]) if v == acc]
    allr = [rid for _, rid in sorted(req_by_case[cid])]
    cases.append({
        "id": cid,
        "title": c["title"],
        "persona": c["persona"],
        "device": c["device"],
        "user_goal": c["user_goal"],
        "content_scope": c["content_scope"],
        "viewing_environment": c["viewing_environment"],
        "handoff": dict((e["from"], e["note"]) for e in journey["edges"]).get(cid, "旅程终点"),
        "png": "%s/final.png" % cid,
        "snapshot": "%s/final.snapshot" % cid,
        "dimensions": c["dimensions"],
        "accepted_version": "v%d" % acc,
        "supporting_assets": [],
        "asset_note": "无嵌入素材，纯 DSL",
        "dsl_capabilities": CAPS[cid],
        "completion_criteria": c["completion_criteria"],
        "visual_review": VISUAL[cid],
        "request_ids": allr,
        "accepted_request_ids": rl,
        "iteration_ids": its_by_case[cid],
        "unresolved_issues": [],
        "plan_version": "plan-v1 2026-10-21T03:05:00+08:00（tmp/run-20261011-01/B05/plan-v1.json，established_before_first_render=true）",
        "criteria_history": HISTORY.get(cid, []),
        "criterion_results": [
            {"id": i, "result": r, "method": m, "evidence": e}
            for i, r, m, e in RES[cid]],
    })
    assert len(RES[cid]) == len(c["completion_criteria"]), cid

doc = {
    "schema_version": 1,
    "path_base": "output_dir",
    "task_id": "B05",
    "run_id": "run-20261011-01",
    "status": "completed",
    "asset_policy": "dsl_primary_with_supporting_assets（本题实际全部纯 DSL 完成，无嵌入素材；政策允许的局部辅助素材未使用）",
    "curatorial_statement": (
        "以一款虚构的城市积水避险产品『水线 Waterline』为载体，用十个关键画面走完一条可信使用链："
        "市民看总览→查点位→选路线，骑手用更严阈值，路人上报，系统推送到锁屏与车机，运维复核，"
        "市级指挥调度，最后个人雨后复盘。全系共用招牌视觉 DepthRuler 水位刻度尺与四档风险色，"
        "把『能不能过』表达为水位线与阈值线的几何关系，而非一句文字结论；同一深度在五种设备上"
        "回答五个不同的问题。数据由单一事实源 b05_data 驱动并跨画面互指：上报 #1042 在 case-05（提交）、"
        "case-08（复核队列）、case-10（个人周报）三处字段一致。唯一真实锚点为中国气象局暴雨预警信号"
        "分级，其余全部在图上与元数据中标注为虚构演示数据；未做真实用户验证。"
    ),
    "plan_version": "plan-v1 2026-10-21T03:05:00+08:00（established_before_first_render=true，路径 tmp/run-20261011-01/B05/plan-v1.json）",
    "criteria_change_note": "plan-v1 的 C1–C5 为约束性标准，全题未删除或放宽任何一条；仅 case-10 就时间口径作过一次显式修订并留痕（见其 criteria_history）。",
    "cases": cases,
    "final_collection_review": {
        "reviewed_at": "2026-10-21T13:29:19+08:00",
        "method": "逐张打开 10 张最终 PNG 整图实看 + 像素量测（case-10 柱状图）+ 跨案字段断言",
        "checks": [
            "10 张 final.png 均为服务原始响应字节，md5 与对应草稿一致，IHDR 尺寸与元数据相符",
            "10 张 final.snapshot 均为完整自包含 DSL，以 </Snapshot> 结尾",
            "每张均已实际打开查看，无占位图、无未看版本",
            "跨案一致性：风险四档色、状态三档色、#1042 五字段、17 分钟避水路线、32cm/14cm 判定均一致",
            "无 ASCII < > 直出、无豆腐字、无文字裁切或遮挡",
        ],
        "independence": "10 张分属 5 类角色 × 5 种设备形态，各自解决不同的内容/状态/任务；无同版式换色、无缩放裁切充数",
        "residual_issues": [],
    },
    "unresolved_issues": [],
}

with open(os.path.join(OUT, "portfolio.json"), "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
print("wrote portfolio.json with %d cases" % len(doc["cases"]))
for c in doc["cases"]:
    print("  %s %-22s %s  %d criteria  reqs=%d iters=%d" % (
        c["id"], c["accepted_version"], "%dx%d" % tuple(c["dimensions"]),
        len(c["criterion_results"]), len(c["request_ids"]),
        len(c["iteration_ids"])))
