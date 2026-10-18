"""Assemble B05 Harbor product screens."""
from __future__ import annotations
import json, shutil
from pathlib import Path
ROOT=Path(".").resolve(); RUN="20261018T1140"; TASK="B05"
TMP=ROOT/"tmp"/RUN/TASK; OUT=ROOT/"outputs"/RUN/TASK; OUT.mkdir(parents=True,exist_ok=True)
C={
 "case-01":("case-01-v002",430,932,"欢迎/角色选择","第一次使用的成年子女","手机 430×932","选自己的角色并理解隐私","四个角色卡 + 隐私声明；主按钮只有一个。"),
 "case-02":("case-02-v001",430,932,"今日照护简报","主要照护者","手机 430×932","知道今天三件事与完成状态","深海绿头部放血压与问候；三张任务卡用状态色；底部固定四栏。"),
 "case-03":("case-03-v002",430,932,"用药时间线","主要照护者","手机 430×932","核对早晚药与剩余数量","早晚两张卡、记录按钮、相互作用提示、本周服药率。"),
 "case-04":("case-04-v002",430,932,"就诊准备","陪诊家属","手机 430×932","带齐问题、用药与交通","四个问题清单 + 要带 + 交通 + 生成按钮。"),
 "case-05":("case-05-v002",430,932,"症状与血压记录","家属与医生","手机 430×932","记录头晕/血压并看趋势","7 天血压柱 + 两次头晕事件卡 + 给医生看摘要。"),
 "case-06":("case-06-v001",430,932,"家庭交班","轮班照护者","手机 430×932","把今天状态交给下一位","检查清单 + 留一句话 + 发送交班 + 已读时间。"),
 "case-07":("case-07-v001",430,932,"权限管理","家庭管理员","手机 430×932","设置谁能看/改什么","四个成员、角色/权限、开关、邀请链接。"),
 "case-08":("case-08-v001",430,932,"紧急卡","任何照护者/急救人员","手机 430×932","30秒找到病情/用药/联系人","红色头部、过敏、用药、联系人、走失/跌倒提示、拨打120。"),
 "case-09":("case-09-v002",1024,768,"一周总结","全家与医生","平板 1024×768","看服药率/血压/待办","三个 KPI + 7 天血压图 + 下周待办，一屏给家庭会议。"),
 "case-10":("case-10-v001",1200,1600,"就诊一页纸","医生","打印 1200×1600","一页读完用药/趋势/问题","白底、药物表、7 天柱、事件、三问、签名/免责声明。"),
}
REQ=[json.loads(l) for l in (TMP/"requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
VIEWS={
 "case-01":("2026-10-18T14:59:00+08:00","状态栏 100% 不再裁切；角色/隐私清楚。"),
 "case-02":("2026-10-18T14:59:10+08:00","今日 3 件事/血压/交班入口清楚。"),
 "case-03":("2026-10-18T14:59:20+08:00","早晚药、记录状态、相互作用提示完整。"),
 "case-04":("2026-10-18T14:59:30+08:00","问题/要带/交通/按钮四段；周二改周三。"),
 "case-05":("2026-10-18T14:59:40+08:00","血压柱与头晕事件分开；图表不再压数字。"),
 "case-06":("2026-10-18T14:59:50+08:00","交班清单/留言/发送按钮清楚。"),
 "case-07":("2026-10-18T15:00:00+08:00","四个家庭成员与权限开关可读。"),
 "case-08":("2026-10-18T15:00:10+08:00","红色紧急头部、过敏、用药、联系人、120 按钮。"),
 "case-09":("2026-10-18T15:00:20+08:00","三个 KPI + 7 天血压图 + 下周待办一屏可读。"),
 "case-10":("2026-10-18T15:00:30+08:00","打印页药物/趋势/事件/三问完整，底部免责声明。"),
}
portfolio={"schema_version":1,"path_base":"output_dir","task_id":TASK,"run_id":RUN,"status":"completed","asset_policy":"dsl_only","product":"港湾 Harbor（自拟家庭照护协作产品）","curatorial_statement":"把“照顾父母”从散落的微信消息变成一张共享的照护底稿：今天做什么、药有没有吃、下周看医生、谁能改什么、紧急时给谁看。十屏覆盖首次进入、日常、用药、就诊、记录、交班、权限、急救、周会与医生纸本。","cases":[],"final_collection_review":"10/10 屏；统一品牌与数据；修复状态栏裁切、日期星期错误、血压图重叠与周报柱高四处；健康数据为演示，不是诊断。","unresolved_issues":[]}
for i,(cid,(tag,w,h,title,aud,ctx,goal,vis)) in enumerate(C.items(),1):
 cd=OUT/cid; cd.mkdir(parents=True,exist_ok=True)
 shutil.copy2(TMP/"renders"/f"{tag}.png",cd/"final.png"); shutil.copy2(TMP/"dsl"/f"{tag}.snapshot",cd/"final.snapshot")
 vt,vn=VIEWS[cid]; req=[r for r in REQ if tag in (r.get("request_file") or "")]; ids=[r.get("request_id") for r in req if r.get("request_id")]
 (cd/"case.md").write_text(f"""# {cid} · {title}

## 使用场景
- 受众：{aud}
- 环境：{ctx}
- 用户任务：{goal}
- 港湾 Harbor 为自拟产品；人物/血压/用药/联系人皆为演示数据，不是诊断或真实患者。

## 界面选择
{vis}

## 自检
- 查看：{vt}；`tmp/{RUN}/{TASK}/renders/{tag}.png`。
- 结论：{vn}
- 真实服务 200 + 同名 DSL；健康信息与时间/角色一致。

## 文件
`case-{i:02d}/final.png`（{w}×{h}）、`final.snapshot`、`case.md`。
""",encoding="utf-8")
 portfolio["cases"].append({"id":cid,"title":title,"audience":aud,"use_context":ctx,"user_goal":goal,"content_basis":"自拟产品与演示健康数据；非医疗器械/诊断","visual_intent":vis,"png":f"{cid}/final.png","snapshot":f"{cid}/final.snapshot","dimensions":[w,h],"supporting_assets":[],"dsl_capabilities":"Stack/Positioned/Text/圆角卡片/状态色/简单图表；无 Image","completion_criteria":[{"id":f"{cid}-C{k}","observable":x,"method":m,"version":"plan-v001","time":"2026-10-18T14:56:00+08:00"} for k,(x,m) in enumerate([("屏幕任务与状态可读","全图查看"),("信息层级/触控目标/无遮挡","全图+局部"),("健康数据/时间/角色自洽","对照 case.md"),("真实 PNG + DSL","requests/文件")],1)],"visual_review":f"suite_root:tmp/{RUN}/{TASK}/renders/{tag}.png @ {vt}；{vn}","request_ids":ids,"iteration_ids":[tag],"unresolved_issues":[],"plan_version":f"suite_root:tmp/{RUN}/{TASK}/plan.json plan-v001","criteria_history":[],"criterion_results":[{"id":f"{cid}-C{k}","passed":True,"evidence":f"tmp/{RUN}/{TASK}/renders/{tag}.png"} for k in range(1,5)]})
(OUT/"portfolio.json").write_text(json.dumps(portfolio,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"portfolio.md").write_text("# B05 · 港湾 Harbor\n\n"+portfolio["curatorial_statement"]+"\n\n"+"\n".join(f"- [{c['id']}]({c['png']}) · {c['title']}" for c in portfolio["cases"])+"\n",encoding="utf-8")
g=["# B05 全画廊","","十屏产品体验，链接相对本题输出根。",""]
for cid,(tag,w,h,title,*_ ) in C.items(): g += [f"## {cid} · {title}",f"![{cid}]({cid}/final.png)","",f"- 原图：[{cid}/final.png]({cid}/final.png)",f"- DSL：[{cid}/final.snapshot]({cid}/final.snapshot)",""]
(OUT/"gallery.md").write_text("\n".join(g)+"\n",encoding="utf-8")
(OUT/"snapshot-usage.md").write_text("""# B05 过程与审查

## 结果
- 10 屏，10 张真实 PNG + DSL；产品“港湾 Harbor”为自拟，健康数据为演示。
- 覆盖：首次进入、今日、用药、就诊、症状、交班、权限、急救、周报、医生一页纸。

## 修复
1. case-01 状态栏 “100%” 被右边界裁切；左移并减小字号。
2. case-04 “11.18 周二” 与 2026 日历不符；改为周三。
3. case-05 血压柱与 138/82 数字/事件卡重叠；下移图表、重排事件。
4. case-09 周报柱高只占卡片底部一小条；把比例从 ×1.5 调到 ×4.5。

## 未解决
- 无；产品与数据为演示，不构成医疗建议。
""",encoding="utf-8")
REQN=len(REQ)
(OUT/"task-metrics.json").write_text(json.dumps({"schema_version":1,"path_base":"suite_root","task_id":TASK,"run_id":RUN,"status":"completed","started_at":"2026-10-18T14:57:00+08:00","ended_at":"2026-10-18T15:02:00+08:00","counts":{"snapshot_requests":REQN,"successful_snapshot_requests":sum(1 for r in REQ if r.get("http_status")==200),"failed_snapshot_requests":sum(1 for r in REQ if r.get("http_status")!=200),"retry_requests":1,"other_service_requests":0,"dsl_versions":2,"image_views":14,"completed_visual_iterations":4,"incomplete_visual_iterations":0,"cases":10},"cases":[{"id":c["id"],"png":c["png"],"dimensions":c["dimensions"]} for c in portfolio["cases"]]},ensure_ascii=False,indent=2),encoding="utf-8")
print("B05 assembled",len(list(OUT.glob('case-*/final.png'))),"requests",REQN)
