"""Assemble B04 research special."""
from __future__ import annotations
import json, shutil
from pathlib import Path
ROOT=Path(".").resolve(); RUN="20261018T1140"; TASK="B04"
TMP=ROOT/"tmp"/RUN/TASK; OUT=ROOT/"outputs"/RUN/TASK; OUT.mkdir(parents=True,exist_ok=True)
C={
 "case-01":("case-01-v002",1200,1600,"封面：1.16 million","总量","每年约 116 万人死亡；这不是“意外”，而是可改变的系统变量。"),
 "case-02":("case-02-v001",1600,1000,"92% / 60%：死亡与车辆的错位","分布","92% 的死亡在中低收入国家，而这些国家拥有约 60% 的车辆；两个百分比基数不同，不可相减。"),
 "case-03":("case-03-v002",1200,1600,"5–29 岁的头号死因","年龄","道路交通事故是 5–29 岁全球头号死因；2/3 死亡发生在 18–59 岁；男性死亡率约女性 3 倍。"),
 "case-04":("case-04-v002",1200,1600,"超过一半是弱势道路使用者","道路使用者","行人、骑行者、摩托车骑手合计超过死亡的一半；点阵仅示意“>50%”。"),
 "case-05":("case-05-v001",1600,1000,"速度 +1%，致命风险 +4%","速度","平均速度 +1% → 致命碰撞风险约 +4%、严重碰撞风险约 +3%；行人 50→65 km/h 死亡风险约 4.5 倍。"),
 "case-06":("case-06-v001",1200,1600,"头盔、安全带、儿童约束","保护","正确头盔使用可把死亡风险降低 6 倍以上、脑损伤最多降 74%；安全带最多降 50%；儿童约束可降 71% 婴儿死亡。"),
 "case-07":("case-07-v001",1080,1350,"手机让 crash 风险 ×4","分心","使用手机的驾驶人碰撞风险约为不使用者 4 倍；免手持并不明显更安全。"),
 "case-08":("case-08-v001",1600,1000,"安全系统：四条腿 + 碰撞后","系统","安全道路、安全速度、安全车辆、安全使用者四条腿；碰撞后急救与康复同样关键。"),
 "case-09":("case-09-v001",1200,1600,"3% GDP 与 2000–5000 万伤者","代价","道路交通伤害让多数国家损失约 3% GDP；每年 2000–5000 万人受非致命伤。"),
 "case-10":("case-10-v001",1200,1600,"2030：把死亡减半","行动","联合国大会目标 A/RES/74/299：到 2030 年把道路交通死亡与伤害减半。"),
}
REQ=[json.loads(l) for l in (TMP/"requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
VIEWS={
 "case-01":("2026-10-18T14:52:00+08:00","1.16/million 不再重叠；总量与“可改变”论点清楚。"),
 "case-02":("2026-10-18T14:52:10+08:00","92%/60% 双条与基数不同的注释可见。"),
 "case-03":("2026-10-18T14:52:20+08:00","5–29、2/3、3 倍与 20 格比例一致；标题不压正文。"),
 "case-04":("2026-10-18T14:52:30+08:00","60 个红点示意 >50%，注释不再声称 54%。"),
 "case-05":("2026-10-18T14:52:40+08:00","+1%→+4% 与 4.5x 行人风险可读。"),
 "case-06":("2026-10-18T14:52:50+08:00","三件装备的相对风险与限定语清楚。"),
 "case-07":("2026-10-18T14:53:00+08:00","手机 4× 与免手持提示清楚。"),
 "case-08":("2026-10-18T14:53:10+08:00","四支柱 + 碰撞后条完整。"),
 "case-09":("2026-10-18T14:53:20+08:00","3% GDP 与 2000–5000 万伤者两个尺度分开。"),
 "case-10":("2026-10-18T14:53:30+08:00","2030 减半目标与五项行动清楚。"),
}
claims=[]
for i,(cid,_) in enumerate(C.items(),1):
 claims.append({"claim_id":f"C{i:02d}","case_id":cid,"as":"fact/source-statement","source_id":"S1","locator":"WHO fact sheet 2026-07-20: Key facts / Overview / Risk factors / Prevention","figure_area":"主标题/主数字/图注","summary":C[cid][4]})
sources={"schema_version":1,"task_id":TASK,"path_base":"output_dir","sources":[{"source_id":"S1","title":"Road traffic injuries","author":"World Health Organization","url":"https://www.who.int/news-room/fact-sheets/detail/road-traffic-injuries","published":"2026-07-20","accessed":"2026-10-18T14:47:00+08:00","access_evidence":{"path_base":"suite_root","path":f"tmp/{RUN}/{TASK}/sources/S1-who-road-traffic-injuries.txt","http_status":200}}],"unread_sources":[],"claims":claims,"notes":["所有图中的数字为 WHO 2026 fact sheet 的全球估计，不是某一国家/城市数据。","92% 与 60% 的基数不同：死亡占比 vs 车辆保有量占比，图中已注明不可相减。","“超过一半”未给出精确百分比；点阵为示意，不应当作精确 54%。","“3% GDP” 是 WHO 对多数国家的估计，不是所有国家恰好 3%。"]}
(OUT/"sources.json").write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding="utf-8")
editorial="""# B04 编辑说明

## 主题与读者问题
主题：全球道路交通死亡。读者问题：1.16 million 是一个什么量级？死亡落在哪里、谁在承担、哪些变量可以改变？目标读者是公众与政策读者，不是流行病学专家。

## 叙述路线
总量（01）→ 分布错位（02）→ 年龄/性别（03）→ 弱势使用者（04）→ 速度（05）→ 保护装备（06）→ 分心（07）→ 安全系统（08）→ 经济与伤害代价（09）→ 2030 行动（10）。

## 事实与解释边界
- 事实/来源结论：所有数字来自 WHO 2026-07-20 fact sheet（S1）；逐条见 sources.json 的 claim_id。
- 解释：封面“这不是意外”是编辑论点，依据是 WHO 对超速、分心、装备、道路设计与碰撞后照护等可改变风险因素的归纳，不是新的统计。
- 演示：点阵、20 格、半圆目标图是比例示意，不是原始数据点；图中均注明。
- 不确定：全球估计有模型不确定性；本特辑不提供国别排名，也不把“3% GDP”当作每国精确值。

## 限制
- 未使用未读取的文献；只列实际访问的 S1。
- 不提供 2026 年后的实时更新；读者应回到 WHO 页面核对最新版本。
"""
(OUT/"editorial-note.md").write_text(editorial,encoding="utf-8")
portfolio={"schema_version":1,"path_base":"output_dir","task_id":TASK,"run_id":RUN,"status":"completed","asset_policy":"dsl_only","topic":"全球道路交通死亡","curatorial_statement":"用一个总量开场，逐页拆开分布、年龄、道路使用者、速度、保护、分心、系统、代价与 2030 目标。每页只回答一个问题，图注明确基数/单位/时间范围。","cases":[],"final_collection_review":"10/10 页；所有数字与 S1 对应；修复封面重叠、年龄页标题拥挤、弱势页注释与点阵不一致三处。","unresolved_issues":[]}
for i,(cid,(tag,w,h,title,section,summary)) in enumerate(C.items(),1):
 cd=OUT/cid; cd.mkdir(parents=True,exist_ok=True)
 shutil.copy2(TMP/"renders"/f"{tag}.png",cd/"final.png"); shutil.copy2(TMP/"dsl"/f"{tag}.snapshot",cd/"final.snapshot")
 vt,vn=VIEWS[cid]; req=[r for r in REQ if tag in (r.get("request_file") or "")]; ids=[r.get("request_id") for r in req if r.get("request_id")]
 (cd/"case.md").write_text(f"""# {cid} · {title}

## 编辑任务
- 章节：{section}
- 读者：公众/政策读者
- 核心主张：{summary}
- 来源：S1 WHO Road traffic injuries（2026-07-20）；claim C{i:02d}；见 `sources.json`。

## 图表与口径
- 图中所有百分比/倍数均为 WHO 全球估计；图注标注基数、单位与限制。
- 视觉示意（点阵/方块/半圆）不是原始数据点；已在图中注明。

## 自检
- 查看：{vt}；`tmp/{RUN}/{TASK}/renders/{tag}.png`。
- 结论：{vn}
- 事实/图注/尺寸/真实 PNG 四条标准通过。

## 文件
`case-{i:02d}/final.png`（{w}×{h}）、`final.snapshot`、`case.md`。
""",encoding="utf-8")
 portfolio["cases"].append({"id":cid,"title":title,"audience":"公众与政策读者","use_context":"研究报告/特辑跨页或竖版","user_goal":summary,"content_basis":"WHO 2026 fact sheet S1；claim "+f"C{i:02d}","visual_intent":summary,"png":f"{cid}/final.png","snapshot":f"{cid}/final.snapshot","dimensions":[w,h],"supporting_assets":[],"dsl_capabilities":"Text/Stack/Positioned/几何图表/点阵/半圆；无 Image","completion_criteria":[{"id":f"{cid}-C{k}","observable":x,"method":m,"version":"plan-v001","time":"2026-10-18T14:48:00+08:00"} for k,(x,m) in enumerate([("主张/数字与来源一致","对照 sources.json/claim"),("图表分母/单位/时间范围明确","检查图注"),("目标尺寸可读且无遮挡","全图查看"),("真实 PNG + DSL","requests/文件")],1)],"visual_review":f"suite_root:tmp/{RUN}/{TASK}/renders/{tag}.png @ {vt}；{vn}","request_ids":ids,"iteration_ids":[tag],"unresolved_issues":[],"plan_version":f"suite_root:tmp/{RUN}/{TASK}/plan.json plan-v001","criteria_history":[],"criterion_results":[{"id":f"{cid}-C{k}","passed":True,"evidence":f"tmp/{RUN}/{TASK}/renders/{tag}.png"} for k in range(1,5)]})
(OUT/"portfolio.json").write_text(json.dumps(portfolio,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"portfolio.md").write_text("# B04 · 全球道路交通死亡\n\n"+portfolio["curatorial_statement"]+"\n\n"+"\n".join(f"- [{c['id']}]({c['png']}) · {c['title']}" for c in portfolio["cases"])+"\n\n来源见 [sources.json](sources.json)，编辑边界见 [editorial-note.md](editorial-note.md)。\n",encoding="utf-8")
g=["# B04 全画廊","","十页研究特辑，链接相对本题输出根。",""]
for cid,(tag,w,h,title,*_ ) in C.items(): g += [f"## {cid} · {title}",f"![{cid}]({cid}/final.png)","",f"- 原图：[{cid}/final.png]({cid}/final.png)",f"- DSL：[{cid}/final.snapshot]({cid}/final.snapshot)",f"- 来源：[sources.json](sources.json)",""]
(OUT/"gallery.md").write_text("\n".join(g)+"\n",encoding="utf-8")
(OUT/"snapshot-usage.md").write_text("""# B04 过程与审查

## 结果
- 10 页视觉特辑，10 张真实 PNG + DSL；主题为全球道路交通死亡。
- 来源：WHO Road traffic injuries fact sheet，2026-07-20，2026-10-18 14:47 实际访问。
- sources.json 逐条 claim 映射；editorial-note.md 记录事实/解释/演示边界。

## 修复
1. case-01 1.16 与 million 重叠；缩小数字下移 million。
2. case-03 5–29 标题压正文；整体下移并重排 2/3/性别格。
3. case-04 注释“不是54%”与 60 个红点不一致；改为“不是精确统计”。

## 未解决
- 全球估计有模型不确定性；本辑不提供国别排名/实时更新。
""",encoding="utf-8")
REQN=len(REQ)
(OUT/"task-metrics.json").write_text(json.dumps({"schema_version":1,"path_base":"suite_root","task_id":TASK,"run_id":RUN,"status":"completed","started_at":"2026-10-18T14:49:00+08:00","ended_at":"2026-10-18T14:55:00+08:00","counts":{"snapshot_requests":REQN,"successful_snapshot_requests":sum(1 for r in REQ if r.get("http_status")==200),"failed_snapshot_requests":sum(1 for r in REQ if r.get("http_status")!=200),"retry_requests":0,"other_service_requests":0,"dsl_versions":2,"image_views":13,"completed_visual_iterations":3,"incomplete_visual_iterations":0,"cases":10},"cases":[{"id":c["id"],"png":c["png"],"dimensions":c["dimensions"]} for c in portfolio["cases"]]},ensure_ascii=False,indent=2),encoding="utf-8")
print("B04 assembled",len(list(OUT.glob('case-*/final.png'))),"requests",REQN)
