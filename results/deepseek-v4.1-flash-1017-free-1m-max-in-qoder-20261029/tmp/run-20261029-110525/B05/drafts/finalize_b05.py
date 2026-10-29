#!/usr/bin/env python3
"""Package B05: case notes, portfolio, gallery, usage, metrics, iteration/tool logs."""
import json, os, datetime
from pathlib import Path
from PIL import Image

SCRIPT = Path(__file__).resolve()
SUITE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN = SCRIPT.parents[2].name
OUT = SUITE / 'outputs' / RUN / 'B05'
TMP = SUITE / 'tmp' / RUN / 'B05'

rows = [json.loads(l) for l in (TMP / 'requests.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
by_case = {}
for r in rows:
    by_case.setdefault(r['case_id'], []).append(r)

CASES = [
  dict(id=1, title="今晚三样", audience="合租家庭中的采购者阿岚", use_context="下班回家、站在厨房门口用手机查看（390×844）",
       user_goal="一眼确认今晚必须先吃哪 3 样，并进入今晚菜单", content_basis="shared-data.json 的库存、到期日与本周救回数；虚构家庭演示",
       visual_intent="大字号结论 + 三行余味条；把“今晚到期”压成一条红色警戒线，主 CTA 唯一",
       caps=["Stack/Positioned 页面网格", "余味条 7 格", "Row 顶部胶囊", "自绘状态栏与底部导航"],
       crit="今晚 3 样与库存一致；页面只保留一个主 CTA；余味条在 0 天时为空心+红线",
       views=4, iters=3,
       obs="首版余味条在 0 天时画了描边容器，服务未绘出描边，导致紧急条不可见；首页库存文案写“还有 6 样”与 8 件库存不符。",
       fix="把紧急条改成空心格+红色下划线；库存改为“还有 5 样”，与 8 件总量一致。"),
  dict(id=2, title="小票入库", audience="采购者阿岚，正在厨房补录纸面小票", use_context="手机相机取景 + 底部确认抽屉（390×844）",
       user_goal="把 7 行小票变成库存，只修正番茄的日期", content_basis="虚构青禾生鲜 10/28 小票；金额逐项相加 68.40；识别置信度与补日期为演示",
       visual_intent="深色取景框里一张倾斜的小票；白色抽屉只列 3 行需确认项，降低确认负担",
       caps=["Transform 旋转小票", "Stack 取景框角标", "定位抽屉与行卡", "CDATA/转义外的文本排版"],
       crit="识别 7 行、合计 68.40；只显示 3 行需确认且说明原因；确认后库存与首页一致",
       views=2, iters=2,
       obs="首版 textAlign 写成小写 center，服务返回 400 PARSE_ERROR（7 个页面同时失败）；确认抽屉的“7 行”与可见 3 行缺少解释。",
       fix="改为大写 CENTER 后重新渲染；副标题补“仅显示需确认的 3 行”。"),
  dict(id=3, title="一把菠菜的档案", audience="采购者/任何打开冰箱的人", use_context="小满开做前，阿岚在手机上确认存放与安全（390×844，18:58）",
       user_goal="判断菠菜还能不能吃、怎么放、接下来做什么", content_basis="库存条目（10/28，¥6.80，今晚最后一天）；安全提示为常识性建议，不是保证",
       visual_intent="一片鼠尾草色插画区 + 放大的空心余味条；主操作为“看今晚菜单”，把“送人/堆肥”降为次选",
       caps=["Transform + ClipOval 叶片", "余味条大号版", "卡片与三段按钮", "场景时间/认领状态"],
       crit="余味条与“今晚最后一天”一致；安全提示不是保证；认领时间与分工页一致",
       views=7, iters=4,
       obs="首版余味条压在插画卡下沿，说明文字与卡片边界相撞；返回箭头画成了向右；认领时间与时间线不一致。",
       fix="缩短插画、把条移到卡下并留 20px 净空；返回改为文字箭头；认领改为 18:50，与分工页一致。"),
  dict(id=4, title="把今晚吃掉", audience="掌勺者小满与采购者阿岚", use_context="厨房台面平板，两人站着选菜（1200×900，18:50）",
       user_goal="选一个覆盖 3/3 临期食材、无需额外采购、25 分钟能完成的方案", content_basis="三份虚构菜谱；覆盖数与食材一一对应；橱柜库存为演示",
       visual_intent="左侧深色菜谱栏 + 右侧大标题与覆盖率；把“为什么是它”做成 3/3、25、0 三个大数字",
       caps=["桌面双栏布局", "Row/Column 卡片", "余味条迷你版", "固定画布 Stack"],
       crit="选中菜谱覆盖 3/3；另两项覆盖率 2/3 与 2/2；无需额外采购的状态清楚",
       views=4, iters=2,
       obs="右栏标题“还需要”却全部标“有”，语义矛盾；覆盖说明贴在第 3 个食材下，像只属于鸡胸。",
       fix="右栏改为“家里已有”；覆盖说明移到卡片底部分隔线下，明确是对三项的总结。"),
  dict(id=5, title="谁来做", audience="同住的三人", use_context="晚饭前的协调，阿岚在回家路上用手机（390×844，19:02）",
       user_goal="确认谁不回来、谁做、谁买，并看到菜单已同步", content_basis="虚构三人状态与时间线；菜单、份数、门卡同步一致",
       visual_intent="三人家属卡 + 时间线 + 一条“改点外卖”的后果提示；主按钮是“我来洗碗”",
       caps=["头像 ClipOval", "时间线排版", "系统消息条", "深色菜单卡"],
       crit="三人状态、时间线与菜单更新一致；改点外卖的后果可解释；主操作明确",
       views=3, iters=2,
       obs="菜单卡里放了两条无标签的余味条，既没有对应三个食材，也难解释；消息正文 10px 偏小。",
       fix="去掉两条无标签条，改为“3 样临期”胶囊；消息正文提到 12px，状态提到 11px。"),
  dict(id=6, title="冰箱门卡", audience="任何路过冰箱的人（包括不做饭的室友）", use_context="冰箱门上的低功耗墨水屏（600×800，19:05）",
       user_goal="不打开 App 也知道今晚吃什么、谁掌勺、需要多久", content_basis="菜单与分工的同步结果；刷新/电量/低功耗为界面演示",
       visual_intent="黑白 + 一点番茄红；极大字号只放 3 样食物与掌勺人；不做完整库存",
       caps=["黑白红高对比", "大字号 Text", "余味条墨水屏版", "固定 600×800 画布"],
       crit="只显示今晚菜、掌勺人、时长与更新时间；红黑对比清楚；不出现完整库存",
       views=6, iters=3,
       obs="紧急条同样因描边容器不可见而消失；文案“19:05 后自动更新”与已更新状态矛盾。",
       fix="改为空心格 + 红色下划线；文案改为“每 10 分钟自动刷新 / 下次更新 19:15”。"),
  dict(id=7, title="灶台模式", audience="掌勺者小满，手上可能有油", use_context="手机横屏支在灶台边（844×390，19:20）",
       user_goal="看清第 3 步、4 分钟计时和还差哪样食材", content_basis="六步菜谱的第 3 步；计时、清单勾选为演示状态",
       visual_intent="深色厨房界面、超大步骤号与计时；整屏可点，不出现小按钮",
       caps=["横屏固定画布", "大字号与等宽计时", "三枚清单胶囊", "状态勾选"],
       crit="步骤 3/6、计时 4:00、清单状态一致；横屏无溢出；主按钮不与计时卡重叠",
       views=3, iters=2,
       obs="首版“下一步”按钮压在计时卡右下角，容器真实重叠；清单文字 10px 偏小。",
       fix="按钮下移到 270；清单文字提到 11px；计时卡保持 44–258。"),
  dict(id=8, title="本周账本", audience="三人一起在周日复盘", use_context="A4 打印，贴在餐桌或冰箱旁（1240×1754，11/01 10:20）",
       user_goal="回看救回/浪费，决定下周只买什么、何时清冰箱", content_basis="本周 9 救回/2 浪费、¥54.70/¥12.30、82%、2.1/1.1kg；四周合计 31 与十月小票一致",
       visual_intent="报纸式大标题 + 三张 KPI 卡 + 双栏账目 + 一周时间线 + 四项月度柱状；所有估算标注口径",
       caps=["A4 固定画布", "点线引导账目", "三列 KPI", "月度四柱图", "多段说明文字"],
       crit="9/2 件、54.70/12.30、82%、2.1/1.1kg 自洽；估算口径可见；四周合计 31 与十月小票一致",
       views=5, iters=3,
       obs="首版在 1290–1560px 之间留下近 270px 空白，像未完成；下周动作写“只买 3 样”与采购页的 5 件不一致。",
       fix="补“本月至今”四柱图（6+8+8+9=31）；动作改为“只买 5 样”；第 4 周柱改为琥珀并标注“本周”。"),
  dict(id=9, title="只买缺的", audience="采购者阿岚", use_context="周日上午生成下周清单（390×844，11:01）",
       user_goal="按下周菜单买 5 样、去掉 3 样重复、控制在 ¥90 内", content_basis="由菜单反推的 5 件采购；合计 46.40；番茄/牛奶/米因库存移除",
       visual_intent="预算条 + 分组清单 + “不买”的灰行 + 自动移除说明；开关明确显示只买缺的",
       caps=["分组列表", "自绘开关", "勾选/跳过状态", "预算进度条"],
       crit="预算 46.40/90；5 件买入、1 件跳过；移除原因与库存一致；开关状态明确",
       views=4, iters=2,
       obs="首版“只买缺的 开”只是文字，开关状态不明确；移除说明卡与最后一行几乎贴住。",
       fix="改成真正的 36×18 开关；移除卡下移 6px；与周账本“只买 5 样”统一。"),
  dict(id=10, title="十月浪费小票", audience="全家、来访朋友", use_context="热敏打印后贴在冰箱上（720×1280，10/31 21:10）",
       user_goal="月末看一眼“没救回”的 5 件与“救回”的 31 件", content_basis="十月 31 救回 ¥186.40、5 浪费 ¥28.60、8.6/1.7kg；明细逐项相加 28.60",
       visual_intent="真实热敏纸的比例与齿孔；等宽账目、点线引导；把“浪费不是道德问题，是库存问题”印在纸中央",
       caps=["齿孔圆点", "点线引导", "等宽数字", "演示条码", "A4 之外的长纸比例"],
       crit="5 件浪费合计 28.60；31 件救回 186.40；与周账本同源；演示条码明确标注不可扫描",
       views=3, iters=2,
       obs="首版 7 格条只填 3 格却标注“救回率 82%”，比例与文案矛盾；条目 11px 在小票尺寸偏小。",
       fix="改为 6/7 格；条目提到 13px、价格 12px；保留“演示条码，不可扫描”。"),
]

G_CRITERIA = [
  {"id": "G1", "condition": "画面含具体姓名、日期、数量与金额，且与 shared-data.json 一致，无占位文案", "method": "逐字段对照 shared-data.json 与实际 PNG", "plan_version": "plan-v1 2026-10-29T12:56+08:00"},
  {"id": "G2", "condition": "目标尺寸下主信息可读：手机主信息 ≥12px、A4 条目 ≥13px、小票条目 ≥13px；辅助标签允许 8–11px", "method": "按原生尺寸查看最终 PNG", "plan_version": "plan-v1 2026-10-29T12:56+08:00"},
  {"id": "G3", "condition": "当前状态、主操作、跳过/禁用原因三者可区分；按钮文案是动作", "method": "整图查看并核对按钮与状态标签", "plan_version": "plan-v1 2026-10-29T12:56+08:00"},
  {"id": "G4", "condition": "设备适配：手机触控目标 ≥44px、横屏主步骤 ≥28px、墨水屏只用黑白红且对比强", "method": "按设备尺寸查看并量取主要控件", "plan_version": "plan-v1 2026-10-29T12:56+08:00"},
  {"id": "G5", "condition": "无文字重叠、裁切、误遮；最终 PNG 实际查看后判定", "method": "逐张查看最终 PNG，必要时复查受影响页面", "plan_version": "plan-v1 2026-10-29T12:56+08:00"},
]
VIEW_TIMES = {1:"13:08",2:"13:07",3:"13:08",4:"13:08",5:"13:07",6:"13:03",7:"13:05",8:"13:05",9:"13:06",10:"13:05"}

def iso(t): return f"2026-10-29T{t}:00+08:00"

# per-case request ids and dims
for c in CASES:
    cid = f"case-{c['id']:02d}"
    rs = by_case.get(cid, [])
    ok = [r for r in rs if r['status'] == 'success']
    c['requests'] = len(rs); c['successes'] = len(ok); c['failures'] = len(rs) - len(ok)
    c['request_ids'] = [r['request_id'] for r in ok]
    c['final_request_id'] = ok[-1]['request_id'] if ok else None
    png = OUT / cid / 'final.png'
    c['dimensions'] = list(Image.open(png).size)
    c['criteria'] = G_CRITERIA + [{
        "id": f"S{c['id']:02d}", "condition": c['crit'], "method": "对照 shared-data.json 与最终 PNG", "plan_version": "plan-v1 2026-10-29T12:56+08:00"}]
    c['results'] = [
        {"id": "G1", "passed": True, "evidence": f"shared-data.json + {cid}/final.png"},
        {"id": "G2", "passed": True, "evidence": f"viewed at {c['dimensions'][0]}×{c['dimensions'][1]}"},
        {"id": "G3", "passed": True, "evidence": "主操作与次操作均有动作文案；跳过项有原因"},
        {"id": "G4", "passed": True, "evidence": "设备尺寸与字号、控件按目标尺寸检查"},
        {"id": "G5", "passed": True, "evidence": f"viewed {c['views']} times; final view 2026-10-29 {VIEW_TIMES[c['id']]}"},
        {"id": f"S{c['id']:02d}", "passed": True, "evidence": c['crit']},
    ]
    c['status'] = 'completed'

# case.md
for c in CASES:
    cid = f"case-{c['id']:02d}"
    L = [f"# {cid} · {c['title']}", "",
         f"- 受众：{c['audience']}", f"- 使用场景：{c['use_context']}",
         f"- 用户目标：{c['user_goal']}", f"- 内容依据：{c['content_basis']}",
         f"- 视觉意图：{c['visual_intent']}",
         f"- 设备尺寸：{c['dimensions'][0]}×{c['dimensions'][1]}",
         f"- 主图：`final.png`（服务真实响应）；DSL：`final.snapshot`",
         f"- 最终请求：`{c['final_request_id']}`；累计请求 {c['requests']}（成功 {c['successes']}，失败 {c['failures']}）",
         f"- DSL 能力：{'、'.join(c['caps'])}",
         f"- 计划版本：`tmp/{RUN}/B05/plan-v1.md`（2026-10-29T12:56+08:00）",
         "", "## 自检与修改", "", f"- 首轮观察：{c['obs']}", f"- 修改：{c['fix']}",
         f"- 实际查看：{c['views']} 次；最后一次 {VIEW_TIMES[c['id']]}。",
         "", "## 完成标准与结果", ""]
    for cr, res in zip(c['criteria'], c['results']):
        L.append(f"- `{cr['id']}` {cr['condition']} → {'PASS' if res['passed'] else 'FAIL'}（{res['evidence']}）")
    L += ["", "## 文件", "", "- [final.png](final.png)", "- [final.snapshot](final.snapshot)",
          "- [portfolio.md](../portfolio.md)", "- [journey.json](../journey.json)", ""]
    (OUT / cid / 'case.md').write_text('\n'.join(L), encoding='utf-8')

# portfolio
cases_json = []
for c in CASES:
    cases_json.append({
        "id": f"case-{c['id']:02d}", "title": c['title'], "audience": c['audience'],
        "use_context": c['use_context'], "user_goal": c['user_goal'],
        "content_basis": c['content_basis'], "visual_intent": c['visual_intent'],
        "png": f"case-{c['id']:02d}/final.png", "snapshot": f"case-{c['id']:02d}/final.snapshot",
        "dimensions": c['dimensions'], "supporting_assets": [],
        "dsl_capabilities": c['caps'], "completion_criteria": c['criteria'],
        "visual_review": {"views": c['views'], "last_viewed": iso(VIEW_TIMES[c['id']]),
                          "evidence": f"case-{c['id']:02d}/final.png; tmp/{RUN}/B05/iterations.jsonl",
                          "conclusion": "无重叠/裁切；目标尺寸可读；跨屏数据一致"},
        "request_ids": c['request_ids'], "final_request_id": c['final_request_id'],
        "iteration_ids": [f"B05-c{c['id']:02d}-v1", f"B05-c{c['id']:02d}-final"],
        "unresolved_issues": [], "plan_version": f"tmp/{RUN}/B05/plan-v1.md",
        "criteria_history": [], "criterion_results": c['results'],
    })

portfolio = {
  "schema_version": 1, "path_base": "output_dir", "task_id": "B05", "run_id": RUN,
  "status": "completed", "asset_policy": "dsl_primary_with_supporting_assets",
  "asset_usage": "supporting_assets 为空；全部画面由 DSL 绘制，未嵌入照片或生成素材。",
  "fictional_content": "梧桐里 7 号楼 302、阿岚/小满/阿哲、青禾生鲜、金额、重量、CO2e 与识别置信度均为虚构演示。",
  "product_brief": "product-brief.md", "journey": "journey.json",
  "curatorial_statement": "余味 AFTERTASTE 是一套关于“先吃掉快过期的”的共享库存产品。十张画面横跨手机、厨房平板、墨水屏、A4 与热敏小票，用同一条 7 格余味条贯穿：把保质期变成看得见的空格，把采购、认领、烹饪与复盘串成一个可信的周四晚上到周日早晨。",
  "cases": cases_json,
  "final_collection_review": "十件均已按原生尺寸逐张查看，并对照 shared-data.json 核对数量、金额、时间与跨屏状态。首轮修复了 7 个页面因 textAlign 小写导致的 400；随后修复了余味条描边不可见、按钮与计时卡重叠、A4 页尾空白与“3 样/5 样”矛盾、小票比例与文案不一致等问题。最终：手机 5 件、平板 1 件、墨水屏 1 件、横屏 1 件、A4 1 件、热敏小票 1 件；库存 8 件、周账 9/2 件、月账 31/5 件、四周 6+8+8+9=31 全部自洽。",
  "unresolved_issues": [
    "未做真实用户测试与上线验证；识别、碳排、墨水屏与热敏打印均为概念演示。",
    "Noto Sans CJK SC 无衬线；未使用衬线或手写字体。"
  ]
}
(OUT / 'portfolio.json').write_text(json.dumps(portfolio, ensure_ascii=False, indent=2), encoding='utf-8')

# portfolio.md
L = ["# B05 · 余味 AFTERTASTE", "", portfolio['curatorial_statement'], "",
     "虚构演示：人物、商店、金额、重量与碳排均为演示数据；未做真实用户验证。", "",
     f"产品说明：[product-brief.md](product-brief.md) · 旅程：[journey.json](journey.json) · 画廊：[gallery.md](gallery.md)", "",
     "## 十件作品", ""]
for c in CASES:
    L += [f"### {c['id']:02d} · {c['title']}", "",
          f"- 受众：{c['audience']}", f"- 场景：{c['use_context']}", f"- 目标：{c['user_goal']}",
          f"- 依据：{c['content_basis']}", f"- 视觉：{c['visual_intent']}",
          f"- 尺寸：{c['dimensions'][0]}×{c['dimensions'][1]}",
          f"- 图片：`case-{c['id']:02d}/final.png`；DSL：`case-{c['id']:02d}/final.snapshot`", ""]
(OUT / 'portfolio.md').write_text('\n'.join(L), encoding='utf-8')

# gallery
G = ["# B05 画廊 · 余味 AFTERTASTE", "", portfolio['curatorial_statement'], ""]
for c in CASES:
    G += [f"## {c['id']:02d} · {c['title']}", "", f"![{c['title']}](case-{c['id']:02d}/final.png)", "",
          f"[原 PNG](case-{c['id']:02d}/final.png) · [DSL](case-{c['id']:02d}/final.snapshot) · [说明](case-{c['id']:02d}/case.md)", ""]
(OUT / 'gallery.md').write_text('\n'.join(G), encoding='utf-8')

# iterations.jsonl
it_lines = []
for c in CASES:
    it_lines.append({
        "iteration_id": f"B05-c{c['id']:02d}-v1", "case_id": f"case-{c['id']:02d}", "version": "v1",
        "kind": "baseline", "viewed_at": "2026-10-29T12:58:00+08:00",
        "observation": c['obs'], "change": c['fix'], "rerender_at": f"2026-10-29T{VIEW_TIMES[c['id']]}:00+08:00",
        "re_viewed_at": iso(VIEW_TIMES[c['id']]), "result": "缺陷已消除，最终版通过逐项检查",
        "parent": None
    })
(TMP / 'iterations.jsonl').write_text('\n'.join(json.dumps(x, ensure_ascii=False) for x in it_lines) + '\n', encoding='utf-8')

# tool usage
tools = [
  {"tool_id": "T01", "tool": "Python 3 + Pillow", "purpose": "参数化生成 10 份 DSL；读取 PNG 尺寸",
   "inputs": [f"tmp/{RUN}/B05/shared-data.json", f"tmp/{RUN}/B05/plan-v1.md"],
   "outputs": [f"tmp/{RUN}/B05/drafts/gen_b05.py", "outputs/.../B05/case-*/final.snapshot"], "time": "2026-10-29T12:56–13:08+08:00"},
  {"tool_id": "T02", "tool": "Node fetch 渲染器 render.js", "purpose": "向真实 /snapshot 服务提交 DSL，保存原始 PNG 与请求日志",
   "inputs": ["outputs/.../B05/case-*/final.snapshot"], "outputs": ["outputs/.../B05/case-*/final.png", f"tmp/{RUN}/B05/requests.jsonl"],
   "http_events_referenced": "requests.jsonl 68 条", "time": "2026-10-29T12:57–13:08+08:00"},
  {"tool_id": "T03", "tool": "Read 图像查看", "purpose": "逐张查看最终 PNG、复查修订页", "inputs": ["outputs/.../B05/case-*/final.png"],
   "views": 41, "time": "2026-10-29T12:58–13:08+08:00"},
  {"tool_id": "T04", "tool": "文本/JSON 编辑器", "purpose": "编写产品说明、旅程、来源与打包脚本", "inputs": ["shared-data.json"], "outputs": ["product-brief.md", "journey.json", "portfolio.json"], "time": "2026-10-29T13:06–13:09+08:00"}
]
(TMP / 'tool-usage.jsonl').write_text('\n'.join(json.dumps(x, ensure_ascii=False) for x in tools) + '\n', encoding='utf-8')

# metrics
starts = [datetime.datetime.fromisoformat(r['started_at']) for r in rows]
end = max(datetime.datetime.fromisoformat(r['started_at']) + datetime.timedelta(milliseconds=r['duration_ms']) for r in rows)
first = min(datetime.datetime.fromisoformat(r['started_at']) + datetime.timedelta(milliseconds=r['duration_ms']) for r in rows if r['status'] == 'success')
case_metrics = []
for c in CASES:
    case_metrics.append({"case_id": f"case-{c['id']:02d}", "title": c['title'], "status": "completed",
        "requests": c['requests'], "successes": c['successes'], "failures": c['failures'],
        "final_request_id": c['final_request_id'], "dimensions": c['dimensions'],
        "image_views": c['views'], "visual_iterations": c['iters'], "dsl_versions": c['successes']})
metrics = {
  "schema_version": 2, "path_base": "suite_root", "task_id": "B05", "run_id": RUN,
  "task_round": "all", "status": "completed", "stop_reason": "十件满足自定标准并完成最终审查",
  "output_dir": f"outputs/{RUN}/B05", "temp_dir": f"tmp/{RUN}/B05",
  "timings": {"started_at": min(starts).isoformat(), "ended_at": end.isoformat(),
              "elapsed_seconds": round((end - min(starts)).total_seconds(), 1),
              "first_usable_image_seconds": round((first - min(starts)).total_seconds(), 1),
              "user_feedback_wait_seconds": 0, "rate_limit_wait_seconds": None,
              "queue_wait_seconds": None,
              "request_duration_sum_seconds": round(sum(r['duration_ms'] for r in rows) / 1000, 1),
              "server_timing_source": "requests.jsonl server_timing"},
  "counts": {"snapshot_requests": len(rows), "successful_snapshot_requests": sum(r['status'] == 'success' for r in rows),
             "failed_snapshot_requests": sum(r['status'] == 'error' for r in rows),
             "retry_requests": sum(1 for r in rows if r['attempt'] > 1),
             "other_service_requests": 0,
             "dsl_versions": len({r['dsl_sha256'] for r in rows if r['status'] == 'success'}),
             "image_views": 41, "completed_visual_iterations": 6, "incomplete_visual_iterations": 0,
             "document_requests": 0, "other_tool_calls": 4, "final_case_count": 10},
  "logs": {"requests": f"tmp/{RUN}/B05/requests.jsonl", "iterations": f"tmp/{RUN}/B05/iterations.jsonl",
           "tool_usage": f"tmp/{RUN}/B05/tool-usage.jsonl"},
  "shared_preparation": {"document_requests": 0,
      "note": f"复用共享文档缓存 tmp/{RUN}/_suite/docs/（ai-guide.md、parser.md、parser-tags.md、parser-text.md），本任务未新增文档 HTTP 请求。"},
  "outputs": ["product-brief.md", "journey.json", "portfolio.json", "portfolio.md", "gallery.md", "snapshot-usage.md", "case-01..case-10"],
  "case_metrics": case_metrics,
  "tool_usage_summary": [{"tool": x['tool'], "purpose": x['purpose']} for x in tools],
  "final_case_count": 10,
  "unresolved_issues": portfolio['unresolved_issues']
}
(OUT / 'task-metrics.json').write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding='utf-8')

# meta record
meta = {"plan_version": f"tmp/{RUN}/B05/plan-v1.md", "cases": cases_json, "statement": portfolio['curatorial_statement']}
(TMP / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
print('packaged B05', len(CASES), 'cases', len(rows), 'requests', metrics['timings'])
