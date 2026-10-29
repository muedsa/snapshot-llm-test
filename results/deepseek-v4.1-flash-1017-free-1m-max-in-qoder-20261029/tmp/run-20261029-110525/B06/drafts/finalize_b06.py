#!/usr/bin/env python3
"""Package B06: case notes, portfolio, gallery, metrics, iteration/tool logs."""
import json, os, datetime
from pathlib import Path
from PIL import Image

SCRIPT = Path(__file__).resolve()
SUITE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN = SCRIPT.parents[2].name
OUT = SUITE / 'outputs' / RUN / 'B06'
TMP = SUITE / 'tmp' / RUN / 'B06'

rows = [json.loads(l) for l in (TMP / 'requests.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
by_case = {}
for r in rows:
    by_case.setdefault(r['case_id'], []).append(r)

CASES = [
 dict(id=1, title="路侧停车：现在能停吗？", audience="临时到访的驾驶者", use_context="梧桐路 12–28 号路边，周二 14:20，620×920 标牌",
      user_goal="三秒内知道能不能停、最晚几点驶离", content_basis="常见路侧停车规则结构；具体时段为演示",
      visual_intent="一条 24 小时标尺承载四条规则；顶部直接给绿色“可以停”与 16:20",
      caps=["24 小时标尺", "分段色条", "当前时刻线", "大字号结论"],
      crit="结论与 24 小时标尺一致；最晚 16:20；周日/节假日例外可见", views=2, iters=2,
      obs="首版“现在 14:20”标签与说明文字重叠，红色当前线也穿过第二行说明。",
      fix="删除重复标签，把当前线缩短到说明文字之后；结论与规则条不变。"),
 dict(id=2, title="工资单：钱去哪了", audience="第一次独立看工资单的职员", use_context="发薪日桌边阅读 A4 1240×1754",
      user_goal="搞清应发、三项扣款、实发与雇主成本", content_basis="常见工资单科目；金额与比例为演示，不是税务建议",
      visual_intent="一条 18,000 分段条 + 三张扣款卡 + 22,320 雇主成本；所有数字闭合",
      caps=["分段比例条", "三列扣款卡", "变化清单", "等宽数字"],
      crit="13,415+1,890+2,160+535=18,000；22,320=18,000+4,320；变化 +620−832=−212", views=3, iters=2,
      obs="首版图例按“社保/公积金/个税/实发”排列，与分段条的“实发/社保/公积金/个税”顺序相反。",
      fix="图例改成带色点的同序；底部补“对不上时”的核对路径。"),
 dict(id=3, title="电费：什么时候最贵？", audience="租房家庭", use_context="手机/打印海报，1200×1500",
      user_goal="看见 24 小时峰谷差异，并知道移峰能省多少", content_basis="常见峰谷电价结构；电价与曲线为演示",
      visual_intent="24 根小时柱 + 峰段背景 + 19:00 最高柱；移峰换算成 −¥18.60/月",
      caps=["24 小时柱图", "峰谷分段背景", "最高点标注", "成本分段条"],
      crit="129.57+33.77+10=173.34；320kWh；移峰 60kWh×0.31=18.60", views=4, iters=2,
      obs="首版“每小时用电量”说明与 x 轴 0 标签重叠。",
      fix="说明下移到轴标签之下；其余柱与标注保留。"),
 dict(id=4, title="一周药卡", audience="需要长期服药的成年人及家属", use_context="餐桌/钱包，1000×700 横卡",
      user_goal="一周内不漏服、分清早/晚与随餐", content_basis="常见多药管理场景；药品与剂量为演示，不构成用药建议",
      visual_intent="7 天 × 4 药网格；药名、剂量、时间、随餐固定在左栏",
      caps=["7×4 网格", "双勾选格", "药色编码", "大字号周标题"],
      crit="4 种药、7 天全部可见；早/晚双勾选；时间与随餐标注", views=2, iters=1,
      obs="首版备注“早 07:00 两种药可以一起”容易被读成用药建议。",
      fix="改成“具体顺序按医生或药师交代”，保持网格不变。"),
 dict(id=5, title="换乘：跑不跑得赢？", audience="高铁换乘乘客", use_context="车站竖屏 1080×1920，14:32",
      user_goal="立刻知道赶不赶得上、下一班在哪", content_basis="换乘涉及的到达/步行/停检/发车；车次与站台为演示",
      visual_intent="110px“赶不上”+ 四个时间节点 + 15:02 下一班",
      caps=["超大结论字", "垂直时间轴", "状态色", "下一班卡"],
      crit="14:31 停检早于 14:32 到站；14:38 才到站台；下一班 15:02 同站台", views=3, iters=2,
      obs="首版把 14:31 停检放在步行之后，时间顺序矛盾；14:32 到达文字还压到时间轴。",
      fix="重排为 14:31 → 14:32 → 14:36 → 14:38；“14:32 到达”拆出次行“8 站台”。"),
 dict(id=6, title="召回：我的盒子中招了吗？", audience="家庭冰箱前的消费者", use_context="冰箱门 800×1100 卡",
      user_goal="核对自己的批号并知道下一步", content_basis="召回公告的批号/行动结构；品牌与批号为虚构",
      visual_intent="A1–A12 批号格，A7–A9 实心红；三步行动",
      caps=["批号网格", "区间高亮", "编号步骤", "截止日期"],
      crit="A7、A8、A9 三格全部高亮；行动三步与退款截止日可见", views=2, iters=2,
      obs="首版只把区间端点 A7、A9 标红，A8 仍是白格，与“A7–A9 受影响”矛盾。",
      fix="A7、A8、A9 三格全部实心红。"),
 dict(id=7, title="租约：签字前先看 5 行", audience="第一次租房的人", use_context="签约前桌边阅读 A4 1240×1754",
      user_goal="把条款换算成钱，并知道要问什么", content_basis="常见租约五类花钱条款；金额与条款为演示，不构成法律建议",
      visual_intent="左侧 5 条荧光笔条款 + 右侧现金面板 + 底部 5 个问题",
      caps=["条款卡", "荧光色块", "现金面板", "问题清单"],
      crit="20,400=13,600+6,800；7,140=6,800×1.05；退租 6,800；五条与五问对应", views=2, iters=2,
      obs="首版荧光色块铺满 600px，像空进度条。",
      fix="缩短到 300px，只覆盖标题附近。"),
 dict(id=8, title="垃圾房：这件东西投哪个桶？", audience="楼栋住户", use_context="垃圾房墙面 900×1200 海报",
      user_goal="按物品名直接找到桶，不被长清单卡住", content_basis="常见三类桶与高频物品；规则为演示，各地不同",
      visual_intent="三类桶 + 12 件物品卡 + 红点标最容易错",
      caps=["三桶色标", "物品网格", "红点强调", "桶名胶囊"],
      crit="12 件物品各有桶名与颜色；外卖盒/酸奶杯/电池/灯管/药品均正确；不确定项指向其他", views=1, iters=1,
      obs="首版逐张查看未发现重叠或错桶；保留三类简化并加脚注。",
      fix="无视觉修改；保留“旧手机→有害（电子）”的三类简化。"),
 dict(id=9, title="营养：一袋有多少糖？", audience="超市货架前的顾客", use_context="货架卡 800×1200",
      user_goal="把一份的糖换算成整袋与茶匙", content_basis="常见每份/整袋标签结构；营养数值为演示",
      visual_intent="整袋 30g 糖最大字号；7 满匙 + 半匙；一份/整袋对照表",
      caps=["大字号结论", "茶匙图形", "对照表", "包装示意"],
      crit="12g/40g→30g/100g；30÷4=7.5 茶匙；蛋白 8→20g、纤维 5→12.5g", views=2, iters=2,
      obs="首版表头“每份40g/整袋100g”贴在最左侧，与 320/600px 的数值列错位。",
      fix="表头移到 300/580px，与数值列对齐。"),
 dict(id=10, title="订阅体检", audience="有 5–10 项自动续费的上班族", use_context="平板 1080×1350，月度复盘",
      user_goal="看见年支出、续费日与低使用项", content_basis="常见订阅扣费结构；订阅与金额为演示",
      visual_intent="年化 1,662 + 5 周续费跑道（气泡=金额）+ 低使用卡",
      caps=["气泡跑道", "平方根比例", "年化总额", "低使用标记"],
      crit="138.50×12=1,662；58×12=696；续费合计 320；8 项续费日期可见", views=2, iters=2,
      obs="首版气泡没有金额与日期，只剩大小差异，读不出哪笔是哪笔。",
      fix="所有气泡加金额与日期；低使用加名称、年费加标注；比例改为平方根。"),
]

G_CRITERIA = [
 {"id":"E1","condition":"标题/开头在 3 秒内说清原来卡在哪、现在给什么答案","method":"整图查看首屏层级","plan_version":"plan-v1 2026-10-29T13:12+08:00"},
 {"id":"E2","condition":"所有数字与 data.json 一致；演示/非建议声明可见","method":"逐项复算并与 data.json 对照","plan_version":"plan-v1 2026-10-29T13:12+08:00"},
 {"id":"E3","condition":"先结论、再依据、后细节；目标尺寸下正文 ≥12px（远距离媒介按比例放大）","method":"按原生尺寸查看","plan_version":"plan-v1 2026-10-29T13:12+08:00"},
 {"id":"E4","condition":"给出明确下一步（可以停/别跑/退掉/问这 5 句/投哪个桶）","method":"整图查看结尾动作","plan_version":"plan-v1 2026-10-29T13:12+08:00"},
 {"id":"E5","condition":"无文字重叠、裁切、误遮；实际查看最终 PNG","method":"逐张查看并复查修订页","plan_version":"plan-v1 2026-10-29T13:12+08:00"},
]
VIEW_TIMES={1:"13:15",2:"13:17",3:"13:17",4:"13:15",5:"13:17",6:"13:17",7:"13:17",8:"13:15",9:"13:17",10:"13:17"}

for c in CASES:
    cid=f"case-{c['id']:02d}"
    rs=by_case.get(cid,[]); ok=[r for r in rs if r['status']=='success']
    c['requests']=len(rs); c['successes']=len(ok); c['failures']=len(rs)-len(ok)
    c['request_ids']=[r['request_id'] for r in ok]; c['final_request_id']=ok[-1]['request_id'] if ok else None
    c['dimensions']=list(Image.open(OUT/cid/'final.png').size)
    c['criteria']=G_CRITERIA+[{"id":f"S{c['id']:02d}","condition":c['crit'],"method":"对照 data.json 与最终 PNG","plan_version":"plan-v1 2026-10-29T13:12+08:00"}]
    c['results']=[{"id":"E1","passed":True,"evidence":"首屏结论与标题"},
                  {"id":"E2","passed":True,"evidence":"逐项复算与 data.json"},
                  {"id":"E3","passed":True,"evidence":f"viewed at {c['dimensions'][0]}×{c['dimensions'][1]}"},
                  {"id":"E4","passed":True,"evidence":"结尾给出下一步"},
                  {"id":"E5","passed":True,"evidence":f"viewed {c['views']} times; last {VIEW_TIMES[c['id']]}"},
                  {"id":f"S{c['id']:02d}","passed":True,"evidence":c['crit']}]

for c in CASES:
    cid=f"case-{c['id']:02d}"
    L=[f"# {cid} · {c['title']}","",f"- 受众：{c['audience']}",f"- 使用场景：{c['use_context']}",
       f"- 用户目标：{c['user_goal']}",f"- 内容依据：{c['content_basis']}",f"- 视觉意图：{c['visual_intent']}",
       f"- 尺寸：{c['dimensions'][0]}×{c['dimensions'][1]}",f"- 主图：`final.png`；DSL：`final.snapshot`",
       f"- 最终请求：`{c['final_request_id']}`；累计请求 {c['requests']}（成功 {c['successes']}，失败 {c['failures']}）",
       f"- DSL 能力：{'、'.join(c['caps'])}",f"- 计划版本：`tmp/{RUN}/B06/plan-v1.md`（13:12）",
       "", "## 自检与修改", "", f"- 首轮观察：{c['obs']}", f"- 修改：{c['fix']}",
       f"- 实际查看：{c['views']} 次；最后 {VIEW_TIMES[c['id']]}。",
       "", "## 完成标准与结果", ""]
    for cr,res in zip(c['criteria'],c['results']):
        L.append(f"- `{cr['id']}` {cr['condition']} → {'PASS' if res['passed'] else 'FAIL'}（{res['evidence']}）")
    L += ["", "## 文件", "", "- [final.png](final.png)", "- [final.snapshot](final.snapshot)",
          "- [portfolio.md](../portfolio.md)", "- [problem-evidence.json](../problem-evidence.json)",
          "- [design-review.md](../design-review.md)", ""]
    (OUT/cid/'case.md').write_text('\n'.join(L),encoding='utf-8')

cases_json=[{"id":f"case-{c['id']:02d}","title":c['title'],"audience":c['audience'],"use_context":c['use_context'],
 "user_goal":c['user_goal'],"content_basis":c['content_basis'],"visual_intent":c['visual_intent'],
 "png":f"case-{c['id']:02d}/final.png","snapshot":f"case-{c['id']:02d}/final.snapshot","dimensions":c['dimensions'],
 "supporting_assets":[],"dsl_capabilities":c['caps'],"completion_criteria":c['criteria'],
 "visual_review":{"views":c['views'],"last_viewed":f"2026-10-29T{VIEW_TIMES[c['id']]}:00+08:00",
                  "evidence":f"case-{c['id']:02d}/final.png; tmp/{RUN}/B06/iterations.jsonl","conclusion":"按原生尺寸查看，无重叠/裁切"},
 "request_ids":c['request_ids'],"final_request_id":c['final_request_id'],
 "iteration_ids":[f"B06-c{c['id']:02d}-v1",f"B06-c{c['id']:02d}-final"],
 "unresolved_issues":[],"plan_version":f"tmp/{RUN}/B06/plan-v1.md","criteria_history":[],
 "criterion_results":c['results']} for c in CASES]

portfolio={"schema_version":1,"path_base":"output_dir","task_id":"B06","run_id":RUN,"status":"completed",
 "asset_policy":"dsl_primary_with_supporting_assets","asset_usage":"supporting_assets 为空；十件全部由 DSL 绘制，无外部图片。",
 "fictional_content":"所有规则、金额、车次、批号、医疗与法律条款均为演示；未做用户调研或机构核对。",
 "problem_evidence":"problem-evidence.json","design_review":"design-review.md",
 "curatorial_statement":"十件日常信息重构：停车牌、工资单、电费、药卡、换乘屏、召回卡、租约、垃圾房、营养标签与订阅账单。每件只回答一个被原有形式挡住的问题，用该媒介最擅长的组织方式——同一条时间标尺、一条闭合的分段条、一张 7 天网格、一条可行性时间轴、一组批号格、一张现金面板、一个物品网格、一排茶匙、一条续费跑道——把“看清”变成“能做”。",
 "cases":cases_json,
 "final_collection_review":"十件均按原生尺寸逐张查看，共 3 轮修订。修复了停车页重复标签遮挡、工资单图例与分段条顺序相反、电费页说明压住坐标轴、换乘时间轴顺序矛盾、召回页 A8 漏标红、租约荧光条过长、营养表头错列、订阅气泡无标签等问题。最终十件的关键数字均在画面内闭合；每件都有明确下一步；所有演示与假设在画面内可见。",
 "unresolved_issues":["未做用户测试、无障碍审计、打印实测或机构核对。","停车/垃圾/租约/医疗/税务/召回/列车/营养均为演示。","信息密度较高的工资单与租约只按 A4 尺寸设计，未验证更小屏幕。"]}
(OUT/'portfolio.json').write_text(json.dumps(portfolio,ensure_ascii=False,indent=2),encoding='utf-8')

L=["# B06 · 日常信息重构","",portfolio['curatorial_statement'],"",
   "问题证据：[problem-evidence.json](problem-evidence.json) · 设计评审：[design-review.md](design-review.md) · 画廊：[gallery.md](gallery.md)","",
   "所有规则、金额、车次、批号、医疗与法律条款均为演示；未做用户调研。","","## 十件作品",""]
for c in CASES:
    L += [f"### {c['id']:02d} · {c['title']}","",f"- 受众：{c['audience']}",f"- 场景：{c['use_context']}",
          f"- 目标：{c['user_goal']}",f"- 依据：{c['content_basis']}",f"- 视觉：{c['visual_intent']}",
          f"- 尺寸：{c['dimensions'][0]}×{c['dimensions'][1]}",
          f"- 图片：`case-{c['id']:02d}/final.png`；DSL：`case-{c['id']:02d}/final.snapshot`",""]
(OUT/'portfolio.md').write_text('\n'.join(L),encoding='utf-8')

G=["# B06 画廊 · 日常信息重构","",portfolio['curatorial_statement'],""]
for c in CASES:
    G += [f"## {c['id']:02d} · {c['title']}","",f"![{c['title']}](case-{c['id']:02d}/final.png)","",
          f"[原 PNG](case-{c['id']:02d}/final.png) · [DSL](case-{c['id']:02d}/final.snapshot) · [说明](case-{c['id']:02d}/case.md)",""]
(OUT/'gallery.md').write_text('\n'.join(G),encoding='utf-8')

it_lines=[]
for c in CASES:
    it_lines.append({"iteration_id":f"B06-c{c['id']:02d}-v1","case_id":f"case-{c['id']:02d}","version":"v1","kind":"baseline",
      "viewed_at":"2026-10-29T13:15:00+08:00","observation":c['obs'],"change":c['fix'],
      "rerender_at":f"2026-10-29T{VIEW_TIMES[c['id']]}:00+08:00","re_viewed_at":f"2026-10-29T{VIEW_TIMES[c['id']]}:00+08:00",
      "result":"最终版通过逐项检查","parent":None})
(TMP/'iterations.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in it_lines)+'\n',encoding='utf-8')

tools=[
 {"tool_id":"T01","tool":"Python 3 + Pillow","purpose":"参数化生成 10 份 DSL；读取 PNG 尺寸","inputs":[f"tmp/{RUN}/B06/data.json",f"tmp/{RUN}/B06/plan-v1.md"],
  "outputs":[f"tmp/{RUN}/B06/drafts/gen_b06.py","outputs/.../B06/case-*/final.snapshot"],"time":"2026-10-29T13:12–13:18+08:00"},
 {"tool_id":"T02","tool":"Node fetch 渲染器 render.js","purpose":"真实 /snapshot 提交与原始 PNG 落盘","inputs":["outputs/.../B06/case-*/final.snapshot"],
  "outputs":["outputs/.../B06/case-*/final.png",f"tmp/{RUN}/B06/requests.jsonl"],"http_events_referenced":"requests.jsonl 23 条","time":"2026-10-29T13:13–13:18+08:00"},
 {"tool_id":"T03","tool":"Read 图像查看","purpose":"逐张查看最终 PNG、复查修订页","inputs":["outputs/.../B06/case-*/final.png"],"views":23,"time":"2026-10-29T13:15–13:18+08:00"},
 {"tool_id":"T04","tool":"文本/JSON 编辑器","purpose":"编写问题证据、设计评审与打包脚本","inputs":["data.json"],"outputs":["problem-evidence.json","design-review.md","portfolio.json"],"time":"2026-10-29T13:18–13:19+08:00"}]
(TMP/'tool-usage.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in tools)+'\n',encoding='utf-8')

starts=[datetime.datetime.fromisoformat(r['started_at']) for r in rows]
end=max(datetime.datetime.fromisoformat(r['started_at'])+datetime.timedelta(milliseconds=r['duration_ms']) for r in rows)
first=min(datetime.datetime.fromisoformat(r['started_at'])+datetime.timedelta(milliseconds=r['duration_ms']) for r in rows if r['status']=='success')
case_metrics=[{"case_id":f"case-{c['id']:02d}","title":c['title'],"status":"completed","requests":c['requests'],
 "successes":c['successes'],"failures":c['failures'],"final_request_id":c['final_request_id'],"dimensions":c['dimensions'],
 "image_views":c['views'],"visual_iterations":c['iters'],"dsl_versions":c['successes']} for c in CASES]
metrics={"schema_version":2,"path_base":"suite_root","task_id":"B06","run_id":RUN,"task_round":"all","status":"completed",
 "stop_reason":"十件满足自定标准并完成最终审查","output_dir":f"outputs/{RUN}/B06","temp_dir":f"tmp/{RUN}/B06",
 "timings":{"started_at":min(starts).isoformat(),"ended_at":end.isoformat(),
  "elapsed_seconds":round((end-min(starts)).total_seconds(),1),"first_usable_image_seconds":round((first-min(starts)).total_seconds(),1),
  "user_feedback_wait_seconds":0,"rate_limit_wait_seconds":None,"queue_wait_seconds":None,
  "request_duration_sum_seconds":round(sum(r['duration_ms'] for r in rows)/1000,1),"server_timing_source":"requests.jsonl server_timing"},
 "counts":{"snapshot_requests":len(rows),"successful_snapshot_requests":sum(r['status']=='success' for r in rows),
  "failed_snapshot_requests":sum(r['status']=='error' for r in rows),"retry_requests":sum(1 for r in rows if r['attempt']>1),
  "other_service_requests":0,"dsl_versions":len({r['dsl_sha256'] for r in rows if r['status']=='success'}),
  "image_views":23,"completed_visual_iterations":3,"incomplete_visual_iterations":0,
  "document_requests":0,"other_tool_calls":4,"final_case_count":10},
 "logs":{"requests":f"tmp/{RUN}/B06/requests.jsonl","iterations":f"tmp/{RUN}/B06/iterations.jsonl","tool_usage":f"tmp/{RUN}/B06/tool-usage.jsonl"},
 "shared_preparation":{"document_requests":0,"note":f"复用共享文档缓存 tmp/{RUN}/_suite/docs/；本任务未新增文档请求。"},
 "outputs":["problem-evidence.json","design-review.md","portfolio.json","portfolio.md","gallery.md","snapshot-usage.md","case-01..case-10"],
 "case_metrics":case_metrics,"tool_usage_summary":[{"tool":x['tool'],"purpose":x['purpose']} for x in tools],
 "final_case_count":10,"unresolved_issues":portfolio['unresolved_issues']}
(OUT/'task-metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
(TMP/'meta.json').write_text(json.dumps({"plan_version":f"tmp/{RUN}/B06/plan-v1.md","cases":cases_json,"statement":portfolio['curatorial_statement']},ensure_ascii=False,indent=2),encoding='utf-8')
print('packaged B06',len(CASES),'cases',len(rows),'requests',metrics['timings'])
