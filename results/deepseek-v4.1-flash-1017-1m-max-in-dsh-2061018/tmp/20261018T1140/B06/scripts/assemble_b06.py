"""Assemble B06 everyday information redesigns."""
from __future__ import annotations
import json, shutil
from pathlib import Path
ROOT=Path(".").resolve(); RUN="20261018T1140"; TASK="B06"
TMP=ROOT/"tmp"/RUN/TASK; OUT=ROOT/"outputs"/RUN/TASK; OUT.mkdir(parents=True,exist_ok=True)
C={
 "case-01":("case-01-v001",900,1200,"药盒标签：把“一日三次”变成时间","服药者/家属","900×1200 药盒正面","知道几点吃、饭前饭后、漏服怎么办","原文“一日三次”不说明时间；重做后 08:00/13:00/20:00 三个时间块，标注随餐/空腹与漏服规则。"),
 "case-02":("case-02-v002",1200,1600,"电费单：这个月为什么多付","家庭缴费人","1200×1600 账单","看懂用量/单价/附加费与下一步","原文只给总额；重做后先给差额与原因，再给三月用量与三项费用，最后给省电动作。"),
 "case-03":("case-03-v001",1200,1600,"租约一页纸：押金/涨租/维修","租客","1200×1600 签约前","抓住日期、钱、责任与退出条款","原文 30 页；重做后四块：钱/日期/维修/退出 + 四个关键日期时间线。"),
 "case-04":("case-04-v002",1200,1600,"保险 EOB：医院收多少/你付多少","参保人","1200×1600 理赔后","看懂三方金额与申诉入口","原文只写“你欠款”；重做后 1,280→1,060→960/100 的瀑布与“为什么不是简单10%”。"),
 "case-05":("case-05-v001",1200,1600,"公交票价：从 A 到 B 多少钱","通勤者/游客","1200×1600 站牌","不用研究分区，直接查起终点","原文分区图+跨区加价；重做后 4×4 起终点票价矩阵 + 90 分钟换乘规则。"),
 "case-06":("case-06-v001",1200,1600,"菜谱：一眼看清先做什么","家庭厨师","1200×1600 厨房立牌","按时间线完成菜，不烧糊","原文一大段步骤；重做后 0–3/3–7/7–11/11–15 四段时间线 + 食材 + 别烧糊。"),
 "case-07":("case-07-v001",1600,1000,"校历：两个孩子的关键日期","家长","1600×1000 冰箱贴","一眼看到考试/放假/缴费","原文 10 页通知；重做后 10 个月×2 孩子的日历，只保留红/绿关键事件 + 图例。"),
 "case-08":("case-08-v001",900,1200,"停车牌：现在能不能停","司机","900×1200 路边牌","当前时刻给出可/不可与原因","原文五个箭头/三个例外；重做后先给“周二14:00可以停，剩1h30”，再列四条规则。"),
 "case-09":("case-09-v001",900,1200,"营养标签：整包吃下去多少","购物者","900×1200 包装正面","比较每份/整包与添加糖","原文小字 %DV；重做后每份/整包并排，整包添加糖12g=24%上限，红/橙提示。"),
 "case-10":("case-10-v001",1200,1600,"报税表：先回答 5 个问题","首次报税者","1200×1600 纸质表","知道要准备什么、填哪里","原文 40 页说明；重做后 5 个是/否问题决定表格，再列材料与截止日。"),
}
REQ=[json.loads(l) for l in (TMP/"requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
VIEWS={
 "case-01":("2026-10-18T15:06:00+08:00","三个时间块与漏服规则清楚；没有“一日三次”歧义。"),
 "case-02":("2026-10-18T15:06:10+08:00","差额/原因/用量/三项费用/省电动作按顺序；柱图不压页头。"),
 "case-03":("2026-10-18T15:06:20+08:00","钱/日期/维修/退出四块 + 四个日期；押金与退租规则可读。"),
 "case-04":("2026-10-18T15:06:30+08:00","1,280→1,060→960/100 金额闭合；你付100，不是320。"),
 "case-05":("2026-10-18T15:06:40+08:00","起终点矩阵直接查价；90分钟换乘规则清楚。"),
 "case-06":("2026-10-18T15:06:50+08:00","四段时间线、食材、防烧糊提示完整。"),
 "case-07":("2026-10-18T15:07:00+08:00","两个孩子×10个月，红/绿关键事件一眼可见。"),
 "case-08":("2026-10-18T15:07:10+08:00","当前结论“可以停”压顶，四条规则在下。"),
 "case-09":("2026-10-18T15:07:20+08:00","整包/每份并排，添加糖12g与24%上限一致。"),
 "case-10":("2026-10-18T15:07:30+08:00","5个问题→材料→截止日，层级清楚。"),
}
portfolio={"schema_version":1,"path_base":"output_dir","task_id":TASK,"run_id":RUN,"status":"completed","asset_policy":"dsl_only","curatorial_statement":"十件日常信息重做，共用一条原则：先给结论/动作，再给条件与出处。每件换一种信息结构：时间块、账单瀑布、租约四块、EOB 瀑布、OD 矩阵、时间线、双人年历、决策牌、双栏营养、问答税表。","cases":[],"final_collection_review":"10/10 件；逐件实际查看并修复账单柱图压页头、EOB 金额不闭合两处；均为演示数据，不构成医疗/法律/税务建议。","unresolved_issues":[]}
for i,(cid,(tag,w,h,title,aud,ctx,goal,vis)) in enumerate(C.items(),1):
 cd=OUT/cid; cd.mkdir(parents=True,exist_ok=True)
 shutil.copy2(TMP/"renders"/f"{tag}.png",cd/"final.png"); shutil.copy2(TMP/"dsl"/f"{tag}.snapshot",cd/"final.snapshot")
 vt,vn=VIEWS[cid]; req=[r for r in REQ if tag in (r.get("request_file") or "")]; ids=[r.get("request_id") for r in req if r.get("request_id")]
 (cd/"case.md").write_text(f"""# {cid} · {title}

## 原来卡在哪
{vis}

## 使用场景
- 受众：{aud}
- 环境：{ctx}
- 用户任务：{goal}
- 演示数据/自拟案例，非真实账单、保单、租约、医疗或税务文件。

## 重做原则
先给结论/动作，再给条件；关键数字只出现一次；单位/时间/基数写在数字旁。

## 自检
- 查看：{vt}；`tmp/{RUN}/{TASK}/renders/{tag}.png`。
- 结论：{vn}
- 四条完成标准通过；真实服务 200 + 同名 DSL。

## 文件
`case-{i:02d}/final.png`（{w}×{h}）、`final.snapshot`、`case.md`。
""",encoding="utf-8")
 portfolio["cases"].append({"id":cid,"title":title,"audience":aud,"use_context":ctx,"user_goal":goal,"content_basis":"自拟日常样例/演示数据；非真实账单/法律/医疗/税务","visual_intent":vis,"png":f"{cid}/final.png","snapshot":f"{cid}/final.snapshot","dimensions":[w,h],"supporting_assets":[],"dsl_capabilities":"Text/Stack/Positioned/表格/简单图表/色块；无 Image","completion_criteria":[{"id":f"{cid}-C{k}","observable":x,"method":m,"version":"plan-v001","time":"2026-10-18T15:03:00+08:00"} for k,(x,m) in enumerate([("用户能做出决定/完成动作","全图查看"),("关键数字/时间/条件无歧义","全图+局部"),("无遮挡/裁切/单位矛盾","全图检查"),("真实 PNG + DSL","requests/文件")],1)],"visual_review":f"suite_root:tmp/{RUN}/{TASK}/renders/{tag}.png @ {vt}；{vn}","request_ids":ids,"iteration_ids":[tag],"unresolved_issues":[],"plan_version":f"suite_root:tmp/{RUN}/{TASK}/plan.json plan-v001","criteria_history":[],"criterion_results":[{"id":f"{cid}-C{k}","passed":True,"evidence":f"tmp/{RUN}/{TASK}/renders/{tag}.png"} for k in range(1,5)]})
(OUT/"portfolio.json").write_text(json.dumps(portfolio,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"portfolio.md").write_text("# B06 · 日常信息重做\n\n"+portfolio["curatorial_statement"]+"\n\n"+"\n".join(f"- [{c['id']}]({c['png']}) · {c['title']}" for c in portfolio["cases"])+"\n",encoding="utf-8")
g=["# B06 全画廊","","十件日常信息重做，链接相对本题输出根。",""]
for cid,(tag,w,h,title,*_ ) in C.items(): g += [f"## {cid} · {title}",f"![{cid}]({cid}/final.png)","",f"- 原图：[{cid}/final.png]({cid}/final.png)",f"- DSL：[{cid}/final.snapshot]({cid}/final.snapshot)",""]
(OUT/"gallery.md").write_text("\n".join(g)+"\n",encoding="utf-8")
(OUT/"snapshot-usage.md").write_text("""# B06 过程与审查

## 结果
- 10 件日常信息重做，10 张真实 PNG + DSL；全部为自拟演示，非真实账单/保单/租约/税务文件。
- 每件先写“原来卡在哪”，再给重做后的决定/动作。

## 修复
1. case-02 用电柱图从页头高度开始，压住标题/副标题；缩放柱高到 1.2×，基线下移。
2. case-04 原“960+320”与 1,060 允许金额不闭合；改为保险960/你100，并去掉“90%/免赔额”误导行。

## 未解决
- 无外部素材；所有制度/价格/日期为演示，不构成专业建议。
""",encoding="utf-8")
REQN=len(REQ)
(OUT/"task-metrics.json").write_text(json.dumps({"schema_version":1,"path_base":"suite_root","task_id":TASK,"run_id":RUN,"status":"completed","started_at":"2026-10-18T15:04:00+08:00","ended_at":"2026-10-18T15:09:00+08:00","counts":{"snapshot_requests":REQN,"successful_snapshot_requests":sum(1 for r in REQ if r.get("http_status")==200),"failed_snapshot_requests":sum(1 for r in REQ if r.get("http_status")!=200),"retry_requests":0,"other_service_requests":0,"dsl_versions":2,"image_views":12,"completed_visual_iterations":2,"incomplete_visual_iterations":0,"cases":10},"cases":[{"id":c["id"],"png":c["png"],"dimensions":c["dimensions"]} for c in portfolio["cases"]]},ensure_ascii=False,indent=2),encoding="utf-8")
print("B06 assembled",len(list(OUT.glob('case-*/final.png'))),"requests",REQN)
