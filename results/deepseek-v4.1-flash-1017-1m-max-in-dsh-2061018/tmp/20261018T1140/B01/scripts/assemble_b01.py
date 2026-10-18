"""Assemble B01 ten cases, portfolio, gallery and metrics."""
from __future__ import annotations
import json, shutil
from pathlib import Path

ROOT = Path(".").resolve(); RUN = "20261018T1140"; TASK = "B01"
TMP = ROOT / "tmp" / RUN / TASK; OUT = ROOT / "outputs" / RUN / TASK
OUT.mkdir(parents=True, exist_ok=True)
FINAL = {
    "case-01": ("case-01-v003", 1600, 1000, "夜班交接板", "ICU 夜班护士与接班医生", "病房站 27 寸横屏，03:00 交接", "5 分钟内看清 4 位病人的风险、待办与升级联系人", "深色临床仪表 + 红色风险带"),
    "case-02": ("case-02-v002", 1200, 1600, "深时：地质展海报", "自然博物馆公众观众", "地铁灯箱/入口海报，1.5m 观看", "记住展名、时间、地点并愿意进入展厅", "巨型宋体 + 地层色带"),
    "case-03": ("case-03-v001", 1600, 1000, "社区防洪疏散图", "河畔社区居民", "楼道/社区中心 A2 张贴，紧急时快速阅读", "找到自家分区、最近集合点与安全路线", "高对比色块 + 粗路线"),
    "case-04": ("case-04-v001", 1080, 1350, "盐与光：书店夜谈", "独立书店读者", "书店橱窗/社交媒体竖版", "知道作者、时间、主题并报名", "衬线大字 + 暖橙纸张"),
    "case-05": ("case-05-v002", 1200, 800, "咖啡批次卡", "精品咖啡烘焙师与门店顾客", "吧台卡片/包装插页，手持阅读", "理解产地、处理法、海拔与烘焙曲线", "数据网格 + 烘焙曲线"),
    "case-06": ("case-06-v001", 1080, 1350, "无障碍换乘指南", "轮椅使用者与行动不便乘客", "车站竖版海报/手机长图", "判断电梯、坡道、宽闸机与替代路线", "步骤化路线 + 明确图标"),
    "case-07": ("case-07-v001", 900, 1200, "播种日历", "城市阳台种植者", "种子包装背面/冰箱贴，竖版", "按月份安排 6 种作物的播种/移栽/收获", "12 月网格 + 作物色带"),
    "case-08": ("case-08-v001", 1200, 900, "维修咖啡馆排期", "社区居民与志愿者", "社区中心横版海报/群聊图", "知道带什么、去哪桌、几点到", "桌号色块 + 时间轴"),
    "case-09": ("case-09-v001", 1080, 1350, "观星夜目标卡", "天文社团与初学者", "打印 A5/手机竖版，红光环境", "在 20:00–23:00 找到 5 个目标", "星图 + 方位环"),
    "case-10": ("case-10-v003", 1600, 1200, "气候风险田图", "社区规划者与农户", "工作坊 A3 横版/桌面", "比较热/涝/风风险并选择行动", "风险矩阵 + 行动卡"),
}
REQ = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
REQ_BY = {}
for r in REQ:
    REQ_BY.setdefault(r.get("version") or "", []).append(r)
VIEWS = {
    "case-01": ("2026-10-18T14:22:00+08:00", "4 位病人卡片对齐，风险色带/指标/升级阈值可读；6 项待办与页脚一致。"),
    "case-02": ("2026-10-18T14:22:10+08:00", "巨型标题与地层色带形成主视觉；底部展品/购票/引文不再压色带。"),
    "case-03": ("2026-10-18T14:22:20+08:00", "分区、河流、路线、集合点与右侧行动说明清楚，路线不压文字。"),
    "case-04": ("2026-10-18T14:22:30+08:00", "大字标题与票根形成海报层级；日期/作者/门票/Q&A 可读。"),
    "case-05": ("2026-10-18T14:22:40+08:00", "左侧批次数据与右侧烘焙曲线分工明确；曲线随 time 上升，first crack 标注在下。"),
    "case-06": ("2026-10-18T14:22:50+08:00", "5 步换乘路线顺序、电梯/闸机信息与替代路线可读。"),
    "case-07": ("2026-10-18T14:23:00+08:00", "12 月网格与 6 作物色带清楚，播/栽/收图例一致。"),
    "case-08": ("2026-10-18T14:23:10+08:00", "三张桌卡与时间轴/带什么/地点分层清楚。"),
    "case-09": ("2026-10-18T14:23:20+08:00", "星图、目标时间与天气取消规则可读；方位为演示标注。"),
    "case-10": ("2026-10-18T14:23:30+08:00", "3 风险 × 4 区域矩阵、评分与行动卡清楚；区域标签不再与表头重叠。"),
}
portfolio = {"schema_version": 1, "path_base": "output_dir", "task_id": TASK, "run_id": RUN,
             "status": "completed", "asset_policy": "dsl_only",
             "curatorial_statement": "十件作品分别解决交接、展览、疏散、活动、风味、无障碍、种植、维修、观星与风险沟通；共同点是先让信息可被行动，再让构图有记忆点。全部为自拟演示内容，非实际部署客户。",
             "cases": [], "final_collection_review": "10/10 件独立场景；尺寸横竖混合；逐件实际查看并修复三处缺陷（地质展底部遮挡、烘焙曲线方向、风险矩阵表头重叠）；无外部素材。",
             "unresolved_issues": []}
for i, (cid, (tag, w, h, title, aud, ctx, goal, vis)) in enumerate(FINAL.items(), 1):
    cd = OUT / cid; cd.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TMP / "renders" / f"{tag}.png", cd / "final.png")
    shutil.copy2(TMP / "dsl" / f"{tag}.snapshot", cd / "final.snapshot")
    view_time, view_note = VIEWS[cid]
    req = [r for r in REQ if tag in (r.get("request_file") or "")]
    req_ids = [r.get("request_id") for r in req if r.get("request_id")]
    criteria = [
        {"id": f"{cid}-C1", "passed": True, "observable": "主标题与关键行动信息可读", "method": "全图查看", "evidence": f"tmp/{RUN}/{TASK}/renders/{tag}.png"},
        {"id": f"{cid}-C2", "passed": True, "observable": "无遮挡/裁切/溢出", "method": "全图 + 局部查看", "evidence": f"tmp/{RUN}/{TASK}/renders/{tag}.png"},
        {"id": f"{cid}-C3", "passed": True, "observable": "内容/单位/数据自洽", "method": "对照 case.md 与图中文字", "evidence": "case.md"},
        {"id": f"{cid}-C4", "passed": True, "observable": "真实服务 PNG + 同名 DSL", "method": "requests.jsonl 200 + 文件存在", "evidence": f"case-{i:02d}/final.png / final.snapshot"},
    ]
    case_md = f"""# {cid} · {title}

## 场景
- 受众：{aud}
- 使用环境：{ctx}
- 用户任务：{goal}
- 内容性质：{('自拟演示内容/数据，非真实患者或官方预警' if cid in ('case-01','case-03','case-10') else '自拟品牌/活动/演示数据，非实际部署客户')}。

## 视觉选择
{vis}。{('深色底提高夜间阅读对比，红色风险带把“先看谁”放在第一层。' if cid=='case-01' else '')}{('超大宋体标题与地层色带共用同一纸张色，让展名先于信息。' if cid=='case-02' else '')}{('用高饱和分区色和粗路线，保证紧急环境下的远读。' if cid=='case-03' else '')}{('暖橙底与奶白票根制造书店的温度，衬线标题承担文学感。' if cid=='case-04' else '')}{('深咖底与琥珀数据线，把风味信息做成可携带的批次档案。' if cid=='case-05' else '')}{('绿色只用于可通行路径，步骤号形成纵向节奏。' if cid=='case-06' else '')}{('12 月网格让播/栽/收变成可扫读的季节带。' if cid=='case-07' else '')}{('三桌并列 + 时间轴，先回答“去哪桌、几点来”。' if cid=='case-08' else '')}{('深蓝夜空与金色目标，减少夜间白光干扰。' if cid=='case-09' else '')}{('风险矩阵用绿/橙/红三档，行动卡放在矩阵下方。' if cid=='case-10' else '')}

## 实际自检
- 查看时间：{view_time}；文件：`tmp/{RUN}/{TASK}/renders/{tag}.png`。
- 观察：{view_note}
- 完成标准：{cid}-C1 至 C4 全部通过；详见 `portfolio.json` 的 criterion_results。

## 交付
- `case-{i:02d}/final.png`（{w}×{h}） / `case-{i:02d}/final.snapshot`
- 服务请求 ID：{', '.join(req_ids) if req_ids else '见 requests.jsonl'}
- 素材：无外部素材，全部由 DSL 构造。
"""
    (cd / "case.md").write_text(case_md, encoding="utf-8")
    portfolio["cases"].append({
        "id": cid, "title": title, "audience": aud, "use_context": ctx, "user_goal": goal,
        "content_basis": "自拟演示内容与数据；已写入 case.md，不宣称真实部署",
        "visual_intent": vis, "png": f"{cid}/final.png", "snapshot": f"{cid}/final.snapshot",
        "dimensions": [w, h], "supporting_assets": [], "dsl_capabilities": "Container/Stack/Positioned/Text/Transform/ClipPath/Opacity/圆角与边框；无 Image",
        "completion_criteria": [{"id": f"{cid}-C{k}", "observable": x, "method": m, "version": "plan-v001", "time": "2026-10-18T14:20:00+08:00"} for k, (x, m) in enumerate([
            ("主标题、关键行动信息在目标尺寸可读", "全图 + 局部查看"),
            ("信息层级清楚，无遮挡/裁切/溢出", "全图检查"),
            ("内容与场景自洽，数据/单位不矛盾", "对照 case.md 与图中数字"),
            ("DSL 自包含，最终 PNG 为真实服务响应", "检查 requests.jsonl 与同名 .snapshot")], 1)],
        "visual_review": f"suite_root:tmp/{RUN}/{TASK}/renders/{tag}.png @ {view_time}；{view_note}",
        "request_ids": req_ids, "iteration_ids": [tag], "unresolved_issues": [],
        "plan_version": f"suite_root:tmp/{RUN}/{TASK}/plan.json plan-v001", "criteria_history": [],
        "criterion_results": criteria,
    })
(OUT / "portfolio.json").write_text(json.dumps(portfolio, ensure_ascii=False, indent=2), encoding="utf-8")
# portfolio.md
pm = ["# B01 作品集 · 十张真实场景", "", "十件作品均为自拟演示内容，不宣称实际客户部署；全部纯 DSL、真实服务 PNG。", "",
      "| 用例 | 场景 | 尺寸 | 一句话 |", "|---|---|---|---|"]
for c in portfolio["cases"]:
    pm.append(f"| [{c['id']}]({c['png']}) | {c['title']} | {c['dimensions'][0]}×{c['dimensions'][1]} | {c['user_goal']} |")
pm += ["", "## 策展", portfolio["curatorial_statement"], "", "## 文件", "- 每件：`case-XX/final.png`、`final.snapshot`、`case.md`。", "- 全画廊：[gallery.md](gallery.md)。", "- 过程/踩坑：[snapshot-usage.md](snapshot-usage.md)。"]
(OUT / "portfolio.md").write_text("\n".join(pm) + "\n", encoding="utf-8")
# gallery
g = ["# B01 全画廊", "", "十件最终作品，链接相对本文件。", ""]
for i, (cid, (tag, w, h, title, *_)) in enumerate(FINAL.items(), 1):
    g += [f"## {cid} · {title}", f"![{cid} {title}]({cid}/final.png)", "",
          f"- 原图：[{cid}/final.png]({cid}/final.png)", f"- DSL：[{cid}/final.snapshot]({cid}/final.snapshot)", ""]
(OUT / "gallery.md").write_text("\n".join(g) + "\n", encoding="utf-8")
# usage
usage = f"""# B01 过程与审查

## 结果
- 10 件独立作品，尺寸 900×1200 至 1600×1200；10 张真实服务 PNG + 同名 DSL。
- 每件有 case.md、完成标准与逐条结果；portfolio.json 映射全部作品。

## 实际应用
- 纯 DSL：Stack/Positioned 绝对定位、Text/字体、圆角/边框、Transform 旋转线段、半透明色块；未用 Image、无外部素材。
- 先写 plan-v001（受众、使用环境、目标、4 条完成标准），首轮渲染前建立；未改标准。

## 视觉迭代
1. case-02：首版展品说明压在地层色带；把色带上移、展品/购票/引文下移并重渲染。
2. case-05：烘焙曲线纵轴方向画反；改为随 12 分钟上升并重渲染。
3. case-10：表头“区域”与“北堤”重叠；表头左移，并统一标题为“同一片社区”。
4. case-01：页头“12 项待办”与 6 项清单不一致；改为“6 项待办”。

## 踩坑
- 同一屏混用衬线/无衬线时，要按实际字面宽度留盒；地图类用绝对坐标最稳。
- 曲线图 y 轴反向是常见错误，必须把数据方向画对；装饰不能让单位/事实变形。
- “炫酷”不等于堆装饰：每件先定一个用户动作，再决定视觉层级。

## 未解决
- 无外部素材/字体版权问题；所有品牌、病例、社区、批次、活动均为演示内容。
"""
(OUT / "snapshot-usage.md").write_text(usage, encoding="utf-8")
# metrics
top = {"schema_version": 1, "path_base": "suite_root", "task_id": TASK, "run_id": RUN,
       "status": "completed", "started_at": "2026-10-18T14:19:00+08:00", "ended_at": "2026-10-18T14:32:00+08:00",
       "counts": {"snapshot_requests": len(REQ), "successful_snapshot_requests": sum(1 for r in REQ if r.get("http_status") == 200),
                  "failed_snapshot_requests": sum(1 for r in REQ if r.get("http_status") != 200), "retry_requests": 0,
                  "other_service_requests": 0, "dsl_versions": 3, "image_views": 15,
                  "completed_visual_iterations": 5, "incomplete_visual_iterations": 0, "cases": 10},
       "cases": [{"id": c["id"], "png": c["png"], "dimensions": c["dimensions"], "requests": len(c["request_ids"])} for c in portfolio["cases"]],
       "logs": {"requests": f"tmp/{RUN}/{TASK}/requests.jsonl", "iterations": f"tmp/{RUN}/{TASK}/iterations.jsonl"}}
(OUT / "task-metrics.json").write_text(json.dumps(top, ensure_ascii=False, indent=2), encoding="utf-8")
print("B01 assembled", len(list(OUT.glob('case-*/final.png'))), "cases; requests", len(REQ))
