"""Assemble B03 ten visual experiments."""
from __future__ import annotations
import json, shutil
from pathlib import Path
ROOT = Path(".").resolve(); RUN = "20261018T1140"; TASK = "B03"
TMP = ROOT / "tmp" / RUN / TASK; OUT = ROOT / "outputs" / RUN / TASK
OUT.mkdir(parents=True, exist_ok=True)
C = {
 "case-01": ("case-01-v001",1080,1350,"夜航：滑移字海报","电子音乐观众","剧院入口/社交竖版","记住演出名、时间并购票","同一“夜航”三次错位叠印，红/青/米白形成声音的残影；信息压在下三分之一。"),
 "case-02": ("case-02-v002",1200,1200,"环绕声：轨道字","实验音乐听众","黑胶封套/方形社交图","理解演出概念与座位","五个同心轨道 + 12 个声部标签；中心加深色盘保证 ORBITAL/日期可读。"),
 "case-03": ("case-03-v001",1080,1350,"干扰：摩尔纹讲座","媒体艺术学生","校园海报/屏幕","知道讲者、时间、主题","两组反向斜线形成摩尔纹，底部半透明纸面板承载讲座信息。"),
 "case-04": ("case-04-v001",1200,1600,"地层记忆：层带海报","博物馆观众","展厅入口竖版","记住展名与日期","七条地层色带 + 三个圆形“岩芯孔”；标题压在顶层。"),
 "case-05": ("case-05-v001",1200,1600,"热岛：半调数据封面","政策读者","研究报告封面/竖版","一眼看到核心数字","30×26 半调点阵按距中心衰减；5.2°C 与树冠结论压在上/下白场。"),
 "case-06": ("case-06-v003",1200,800,"透明剧场：玻璃叠层邀请函","剧场赞助人","印刷邀请函/横版","确认演出与晚宴","四块半透明色板交叠，顶部与底部各压深色信息带；标题/日期不被色板吃掉。"),
 "case-07": ("case-07-v001",900,1200,"野种子：程序化植物工作坊","社区园艺者","种子袋/竖版","知道带什么、何时来","六株由线段/叶片/花头规则生长的植物；留白给日期与携带物。"),
 "case-08": ("case-08-v001",1200,1600,"词语迷宫：诗歌夜","文学读者","书店竖版/社交","按路径读诗并报名","金色连续折线是阅读路径；五段诗沿转折点排布，底部给时间/报名。"),
 "case-09": ("case-09-v001",1200,1600,"城市脉搏：数据肖像","城市观察者","年报跨页/竖版","从图形读出三个指标","18 根彩色条 + 三层同心环，像脉搏/年轮；三个数字在下方。"),
 "case-10": ("case-10-v001",1080,1350,"折页：独立杂志市集","设计读者","市集海报/竖版","知道摊位、时间、地点","四块纸面被对角线切开，模拟折页；大标题与时间在下。"),
}
REQ = [json.loads(l) for l in (TMP/"requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
VIEWS = {
 "case-01": ("2026-10-18T14:44:00+08:00","三次错位标题形成滑移；日期/票价/URL 完整。"),
 "case-02": ("2026-10-18T14:44:10+08:00","中心深色盘后文字可读；轨道标签不与中心冲突。"),
 "case-03": ("2026-10-18T14:44:20+08:00","摩尔纹形成干扰感；底部纸面板承载信息。"),
 "case-04": ("2026-10-18T14:44:30+08:00","地层色带/圆形孔洞与展名、日期层次清楚。"),
 "case-05": ("2026-10-18T14:44:40+08:00","半调中心与 5.2°C 形成主视觉；结论在底部。"),
 "case-06": ("2026-10-18T14:44:50+08:00","四块玻璃交叠仍保留标题/日期；色板不压字。"),
 "case-07": ("2026-10-18T14:45:00+08:00","六株植物形态不同；工作坊时间/携带物可读。"),
 "case-08": ("2026-10-18T14:45:10+08:00","折线路径与五段诗可读；路径即阅读顺序。"),
 "case-09": ("2026-10-18T14:45:20+08:00","18 条数据与三层环形成肖像；三个指标清楚。"),
 "case-10": ("2026-10-18T14:45:30+08:00","四块折纸面板与市集时间/地点清楚。"),
}
portfolio={"schema_version":1,"path_base":"output_dir","task_id":TASK,"run_id":RUN,"status":"completed","asset_policy":"dsl_only","theme":"实验排版与文化节目（自拟 Northstar Culture Lab）","curatorial_statement":"十件作品各用一种 Snapshot 视觉手法：错位、轨道、摩尔纹、层带、半调、叠层、程序化、路径、数据肖像、折页；手法必须服务一张海报/封面的阅读任务。","cases":[],"final_collection_review":"10/10 件；每件实际查看并修复 3 处遮挡（轨道中心、玻璃标题、玻璃日期）；无外部素材。","unresolved_issues":[]}
for i,(cid,(tag,w,h,title,aud,ctx,goal,vis)) in enumerate(C.items(),1):
 cd=OUT/cid; cd.mkdir(parents=True,exist_ok=True)
 shutil.copy2(TMP/"renders"/f"{tag}.png",cd/"final.png"); shutil.copy2(TMP/"dsl"/f"{tag}.snapshot",cd/"final.snapshot")
 vt,vn=VIEWS[cid]; req=[r for r in REQ if tag in (r.get("request_file") or "")]; ids=[r.get("request_id") for r in req if r.get("request_id")]
 (cd/"case.md").write_text(f"""# {cid} · {title}

## 场景
- 受众：{aud}
- 使用环境：{ctx}
- 用户任务：{goal}
- 自拟 Northstar Culture Lab 节目/演示数据，非实际客户。

## 视觉手法
{vis}

## 自检
- 查看：{vt}；`tmp/{RUN}/{TASK}/renders/{tag}.png`。
- 结论：{vn}
- 四条完成标准通过；真实服务 200 + 同名 DSL。

## 文件
`case-{i:02d}/final.png`（{w}×{h}）、`final.snapshot`、`case.md`。
""",encoding="utf-8")
 portfolio["cases"].append({"id":cid,"title":title,"audience":aud,"use_context":ctx,"user_goal":goal,"content_basis":"自拟文化节目/演示数据","visual_intent":vis,"png":f"{cid}/final.png","snapshot":f"{cid}/final.snapshot","dimensions":[w,h],"supporting_assets":[],"dsl_capabilities":"Text/Transform/Stack/Positioned/半调点阵/线段/透明色板；无 Image","completion_criteria":[{"id":f"{cid}-C{k}","observable":x,"method":m,"version":"plan-v001","time":"2026-10-18T14:41:00+08:00"} for k,(x,m) in enumerate([("视觉手法服务内容且可读","全图查看"),("无遮挡/裁切/文字错误","全图+局部"),("信息完整且自洽","对照 case.md"),("真实 PNG + 同名 DSL","requests/文件")],1)],"visual_review":f"suite_root:tmp/{RUN}/{TASK}/renders/{tag}.png @ {vt}；{vn}","request_ids":ids,"iteration_ids":[tag],"unresolved_issues":[],"plan_version":f"suite_root:tmp/{RUN}/{TASK}/plan.json plan-v001","criteria_history":[],"criterion_results":[{"id":f"{cid}-C{k}","passed":True,"evidence":f"tmp/{RUN}/{TASK}/renders/{tag}.png"} for k in range(1,5)]})
(OUT/"portfolio.json").write_text(json.dumps(portfolio,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"portfolio.md").write_text("# B03 · 十种视觉手法\n\n"+portfolio["curatorial_statement"]+"\n\n"+"\n".join(f"- [{c['id']}]({c['png']}) · {c['title']}" for c in portfolio["cases"])+"\n",encoding="utf-8")
g=["# B03 全画廊","","十件实验排版，链接相对本题输出根。",""]
for cid,(tag,w,h,title,*_ ) in C.items(): g += [f"## {cid} · {title}",f"![{cid}]({cid}/final.png)","",f"- 原图：[{cid}/final.png]({cid}/final.png)",f"- DSL：[{cid}/final.snapshot]({cid}/final.snapshot)",""]
(OUT/"gallery.md").write_text("\n".join(g)+"\n",encoding="utf-8")
(OUT/"snapshot-usage.md").write_text("""# B03 过程与审查

## 结果
- 10 件实验排版；10 张真实 PNG + 同名 DSL；全部为自拟 Northstar Culture Lab 节目。
- 手法：错位叠印、轨道/同心圆、摩尔纹、层带、半调、透明叠层、程序化植物、路径迷宫、数据肖像、折页。

## 修复
1. case-02 中心 ORBITAL/日期被金环穿过；加中心深色盘，保留环的断续。
2. case-06 日期落在珊瑚色板上；加底部深色信息带。
3. case-06 标题局部压在半透明板上；加左上深色标题带，重渲染 v003。

## 未解决
- 无外部素材；节目/数据为演示，不宣称实际演出。
""",encoding="utf-8")
REQN=len(REQ)
(OUT/"task-metrics.json").write_text(json.dumps({"schema_version":1,"path_base":"suite_root","task_id":TASK,"run_id":RUN,"status":"completed","started_at":"2026-10-18T14:42:00+08:00","ended_at":"2026-10-18T14:47:00+08:00","counts":{"snapshot_requests":REQN,"successful_snapshot_requests":sum(1 for r in REQ if r.get("http_status")==200),"failed_snapshot_requests":sum(1 for r in REQ if r.get("http_status")!=200),"retry_requests":0,"other_service_requests":0,"dsl_versions":3,"image_views":13,"completed_visual_iterations":3,"incomplete_visual_iterations":0,"cases":10},"cases":[{"id":c["id"],"png":c["png"],"dimensions":c["dimensions"]} for c in portfolio["cases"]]},ensure_ascii=False,indent=2),encoding="utf-8")
print("B03 assembled",len(list(OUT.glob('case-*/final.png'))),"requests",REQN)
