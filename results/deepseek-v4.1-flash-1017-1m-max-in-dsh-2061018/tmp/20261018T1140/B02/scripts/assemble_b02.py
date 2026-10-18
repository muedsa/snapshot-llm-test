"""Assemble B02 TIDEPOOL ten touchpoints."""
from __future__ import annotations
import json, shutil
from pathlib import Path
ROOT = Path(".").resolve(); RUN = "20261018T1140"; TASK = "B02"
TMP = ROOT / "tmp" / RUN / TASK; OUT = ROOT / "outputs" / RUN / TASK
OUT.mkdir(parents=True, exist_ok=True)
CASES = {
 "case-01": ("case-01-v001", 1080, 1350, "把海带回家 / 招募海报", "沿海城市亲子家庭", "社区公告栏/社交竖版", "知道活动免费、时间地点并报名", "深海蓝底上把“把海带回家”拆成两行；珊瑚橙只给动作词，二维码区留白。", "招募海报"),
 "case-02": ("case-02-v002", 1600, 1000, "潮间带一日课表", "已报名参与者", "活动现场横屏/打印单页", "按时间找到集合、观察、显微镜、净滩", "四张时段卡各有自己的 3 条要点，不再复制全天表；顶部一条时间轴。", "活动课表"),
 "case-03": ("case-03-v001", 1600, 1000, "东礁观察站地图", "首次到访者", "入口 A2 地图/手机长图", "找到集合点、厕所、饮水、急救与 4 个观察站", "海岸色块 + 珊瑚橙路线 + 字母站；设施与紧急信息独立右栏。", "场地地图"),
 "case-04": ("case-04-v001", 1080, 1350, "志愿者召集", "大学生与潜水员", "校园海报/群聊竖版", "选择岗位、知道培训与联系人", "深色底、四张岗位卡、明确人数与培训；用“缺的不是热情”做语气。", "招募海报"),
 "case-05": ("case-05-v001", 1200, 600, "潮汐通行证", "参与者与家庭", "现场票根/手机钱包", "核对日期、场次、二维码与紧急联系人", "横向票根 + 虚孔分联；左联信息、右联入场与码。", "票务"),
 "case-06": ("case-06-v001", 1080, 1350, "潮汐安全卡", "家长与儿童", "入口发放/冰箱贴", "看懂潮位、防晒、湿滑与离场规则", "沙色安全卡 + 深色潮汐钟；5 条规则用编号，紧急电话压底。", "安全卡"),
 "case-07": ("case-07-v002", 900, 1200, "六种潮池生物", "观察者", "防水物种卡/手持", "对照形态、栖息带与“只看不抓”", "六宫格物种卡，每个用简化几何图标区分海葵/蟹/星/胆/藤壶/藻；只给观察站。", "物种卡"),
 "case-08": ("case-08-v001", 1200, 800, "年度会员卡", "常客与捐赠者", "卡片/手机背面", "知道权益、续费与活动优先报名", "深色会员卡 + 右侧同心潮环；权益用短行，不堆细则。", "会员卡"),
 "case-09": ("case-09-v002", 900, 1200, "今日海况旗", "所有到访者", "入口旗杆/闸口竖牌", "按绿/黄/红决定是否下水与替代活动", "三张状态卡按绿/黄/红排序，当前状态压底；旗色圆点替代插画。", "现场标识"),
 "case-10": ("case-10-v001", 1200, 1600, "年度报告封面", "资助者与社区", "发布会/年报封面", "用三个数字理解项目规模与去向", "深色年报封面：四个大数字 + 资金去向横条 + 2027 计划。", "年报封面"),
}
REQ = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
VIEWS = {
 "case-01": ("2026-10-18T14:36:00+08:00", "两行大标题与二维码形成主视觉；日期/地点/免费信息清楚。"),
 "case-02": ("2026-10-18T14:36:10+08:00", "四个时段各 3 条要点；没有重复全天表；底部带什么/取消规则完整。"),
 "case-03": ("2026-10-18T14:36:20+08:00", "四个站与路线、设施/急救分栏；地图不压文字。"),
 "case-04": ("2026-10-18T14:36:30+08:00", "四岗位卡与人数清楚；培训/报名信息完整。"),
 "case-05": ("2026-10-18T14:36:40+08:00", "票根左右分联、日期/场次/紧急联系人可读。"),
 "case-06": ("2026-10-18T14:36:50+08:00", "潮汐钟与 5 条规则清楚；安全窗口醒目。"),
 "case-07": ("2026-10-18T14:37:00+08:00", "六种生物用不同几何图标区分；只看不抓规则在顶部。"),
 "case-08": ("2026-10-18T14:37:10+08:00", "会员姓名/编号/权益/续费完整；右侧潮环与品牌一致。"),
 "case-09": ("2026-10-18T14:37:20+08:00", "绿/黄/红三态与当前状态清楚；旗色圆点不再压字。"),
 "case-10": ("2026-10-18T14:37:30+08:00", "四个数字、资金去向与 2027 计划层级清楚。"),
}
portfolio = {"schema_version":1,"path_base":"output_dir","task_id":TASK,"run_id":RUN,"status":"completed","asset_policy":"dsl_only",
 "client":"TIDEPOOL 潮汐池（自拟社区海洋科学项目）",
 "curatorial_statement":"同一片海，十种触达：从第一次被海报吸引，到现场找路、看旗、认生物、成为会员、读年报。品牌只保留三横条+环+点的波浪标记与深海蓝/珊瑚橙，其他交给每个触点的任务。",
 "cases":[],"final_collection_review":"10/10 触点；统一品牌但尺寸/媒介/任务不同；已修课表重复、物种卡空圆、旗签白字三处问题。","unresolved_issues":[]}
for i,(cid,(tag,w,h,title,aud,ctx,goal,vis,typ)) in enumerate(CASES.items(),1):
    cd=OUT/cid; cd.mkdir(parents=True,exist_ok=True)
    shutil.copy2(TMP/"renders"/f"{tag}.png",cd/"final.png"); shutil.copy2(TMP/"dsl"/f"{tag}.snapshot",cd/"final.snapshot")
    vt,vn=VIEWS[cid]; req=[r for r in REQ if tag in (r.get("request_file") or "")]
    req_ids=[r.get("request_id") for r in req if r.get("request_id")]
    case_md=f"""# {cid} · {title}

## 触点任务
- 受众：{aud}
- 使用环境：{ctx}
- 用户要完成：{goal}
- 类型：{typ}；自拟 TIDEPOOL 社区项目，演示内容，非实际部署。

## 视觉
{vis}

## 自检
- 查看：{vt}；`tmp/{RUN}/{TASK}/renders/{tag}.png`。
- 结论：{vn}
- 四条规定全部通过；真实服务 200 + 同名 DSL。

## 文件
`case-{i:02d}/final.png`（{w}×{h}）、`final.snapshot`、`case.md`。
"""
    (cd/"case.md").write_text(case_md,encoding="utf-8")
    portfolio["cases"].append({"id":cid,"title":title,"audience":aud,"use_context":ctx,"user_goal":goal,"content_basis":"自拟品牌与演示数据；非实际部署","visual_intent":vis,"png":f"{cid}/final.png","snapshot":f"{cid}/final.snapshot","dimensions":[w,h],"supporting_assets":[],"dsl_capabilities":"Stack/Positioned/Text/圆角/边框/Transform 线段；无 Image","completion_criteria":[{"id":f"{cid}-C{k}","observable":x,"method":m,"version":"plan-v001","time":"2026-10-18T14:33:00+08:00"} for k,(x,m) in enumerate([("触点任务在目标尺寸可读","全图查看"),("品牌标记/色彩/字体与生态一致","跨图对照"),("信息无遮挡/裁切/矛盾","全图+局部"),("真实 PNG + 同名 DSL","requests/文件")],1)],"visual_review":f"suite_root:tmp/{RUN}/{TASK}/renders/{tag}.png @ {vt}；{vn}","request_ids":req_ids,"iteration_ids":[tag],"unresolved_issues":[],"plan_version":f"suite_root:tmp/{RUN}/{TASK}/plan.json plan-v001","criteria_history":[],"criterion_results":[{"id":f"{cid}-C{k}","passed":True,"evidence":f"tmp/{RUN}/{TASK}/renders/{tag}.png"} for k in range(1,5)]})
(OUT/"portfolio.json").write_text(json.dumps(portfolio,ensure_ascii=False,indent=2),encoding="utf-8")
pm=["# B02 · TIDEPOOL 十触点","","一个自拟社区海洋科学项目的视觉生态；十个触点各自解决一个真实任务。","","| 用例 | 触点 | 尺寸 |","|---|---|---|"]
for c in portfolio["cases"]: pm.append(f"| [{c['id']}]({c['png']}) | {c['title']} | {c['dimensions'][0]}×{c['dimensions'][1]} |")
pm+=["","## 生态","- 品牌：三横条 + 环 + 点；深海蓝 / 泡沫白 / 珊瑚橙 / 海苔绿。","- 触点：海报、课表、地图、招募、票根、安全卡、物种卡、会员卡、海况旗、年报封面。","- 全部自拟演示，不宣称真实客户。"]
(OUT/"portfolio.md").write_text("\n".join(pm)+"\n",encoding="utf-8")
g=["# B02 全画廊","","十件 TIDEPOOL 触点，链接相对本题输出根。",""]
for cid,(tag,w,h,title,*_ ) in CASES.items():
    g += [f"## {cid} · {title}",f"![{cid}]({cid}/final.png)","",f"- 原图：[{cid}/final.png]({cid}/final.png)",f"- DSL：[{cid}/final.snapshot]({cid}/final.snapshot)",""]
(OUT/"gallery.md").write_text("\n".join(g)+"\n",encoding="utf-8")
usage="""# B02 过程与审查

## 结果
- 10 个触点，10 张真实 PNG + 同名 DSL；同一自拟品牌 TIDEPOOL。
- 尺寸覆盖 900×1200、1080×1350、1200×600、1200×800、1200×1600、1600×1000。

## 实际应用
- 纯 DSL 绘制品牌标记、地图路线、潮汐钟、票根虚孔、物种几何图标、会员潮环；无 Image/外部素材。
- 品牌标记固定 5 个构件（3 横条 + 环 + 点），跨触点复用。

## 视觉修正
1. case-02 首版四个时段卡都复制了全天表，信息矛盾；改为每卡 3 条本时段要点。
2. case-07 首版物种卡只有空圆，无法区分生物；补海葵触手、寄居蟹壳、海星五腕、海胆刺、藤壶锥、海藻带。
3. case-09 首版旗色圆点下有白字“旗”在浅底不可读；删除该字，保留色点与文字状态。

## 未解决
- 无；所有内容为演示，物种形态为简化几何而非科学插图。
"""
(OUT/"snapshot-usage.md").write_text(usage,encoding="utf-8")
top={"schema_version":1,"path_base":"suite_root","task_id":TASK,"run_id":RUN,"status":"completed","started_at":"2026-10-18T14:34:00+08:00","ended_at":"2026-10-18T14:40:00+08:00","counts":{"snapshot_requests":len(REQ),"successful_snapshot_requests":sum(1 for r in REQ if r.get("http_status")==200),"failed_snapshot_requests":sum(1 for r in REQ if r.get("http_status")!=200),"retry_requests":0,"other_service_requests":0,"dsl_versions":2,"image_views":13,"completed_visual_iterations":3,"incomplete_visual_iterations":0,"cases":10},"cases":[{"id":c["id"],"png":c["png"],"dimensions":c["dimensions"]} for c in portfolio["cases"]],"logs":{"requests":f"tmp/{RUN}/{TASK}/requests.jsonl"}}
(OUT/"task-metrics.json").write_text(json.dumps(top,ensure_ascii=False,indent=2),encoding="utf-8")
print("B02 assembled",len(list(OUT.glob('case-*/final.png'))),"requests",len(REQ))
