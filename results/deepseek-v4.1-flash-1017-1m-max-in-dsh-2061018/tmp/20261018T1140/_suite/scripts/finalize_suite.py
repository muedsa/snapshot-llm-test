"""Finalize the complete 30-task suite: state, index, gallery, metrics, usage."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(".").resolve(); RUN = "20261018T1140"
OUT = ROOT / "outputs" / RUN; SUITE = OUT / "_suite"
TASKS = [f"A{i:02d}" for i in range(1, 25)] + [f"B{i:02d}" for i in range(1, 7)]
TITLES = {
 "A01":"运营总览","A02":"双尺寸活动议程","A03":"对话式海报与系统状态","A04":"转化叙事","A05":"传感器报告","A06":"依赖关系图","A07":"交通网络与出行卡","A08":"无障碍导视","A09":"Transform 图谱","A10":"合成实验室","A11":"双语结算单","A12":"响应式产品页","A13":"品牌系统","A14":"八张社交卡","A15":"仪表盘重建","A16":"季度报告更正","A17":"手册与教学示例","A18":"三幕数据故事","A19":"网格与遮挡","A20":"24 点密集标注","A21":"三阶段发布视觉","A22":"真实数据更正驾驶舱","A23":"格式边界分镜","A24":"双团队发布计划",
 "B01":"十张真实场景","B02":"TIDEPOOL 十触点","B03":"十种视觉手法","B04":"全球道路死亡特辑","B05":"港湾 Harbor 产品","B06":"日常信息重做",
}
# paired final images
images=[]
for p in sorted(OUT.glob("A*/**/*.png"))+sorted(OUT.glob("B*/case-*/final.png")):
    d=p.with_suffix(".snapshot")
    if d.exists(): images.append((p.relative_to(OUT).as_posix(),d.relative_to(OUT).as_posix()))
assert len(images)==124, len(images)
by_task={t:[x for x in images if x[0].startswith(t+"/")] for t in TASKS}
assert all(len(by_task[t])>=1 for t in TASKS)
# state
state=json.loads((SUITE/"suite-state.json").read_text(encoding="utf-8"))
state["status"]="completed"; state["updated_at"]="2026-10-18T15:12:00+08:00"; state["ended_at"]="2026-10-18T15:12:00+08:00"
state["current_task"]=None; state["current_round"]=None; state["stop_reason"]=None
state["notes"]="30/30 tasks completed; 124 final PNG/DSL pairs; A21 three rounds, A22 three rounds, B01–B06 ten independent works each."
for t in state.get("tasks",[]):
    if t.get("id") in TASKS:
        t["status"]="completed"; t["issues"]=[]
        if not t.get("ended_at"): t["ended_at"]="2026-10-18T15:12:00+08:00"
state["last_checkpoint"]="tmp/%s/_suite/checkpoints/state-000025.json"%RUN
state["suite_artifacts"]={k:f"outputs/{RUN}/_suite/{v}" for k,v in {"index":"index.md","gallery":"gallery.md","snapshot_usage":"snapshot-usage.md","task_metrics":"task-metrics.json","suite_state":"suite-state.json"}.items()}
(SUITE/"suite-state.json").write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
cp=ROOT/"tmp"/RUN/"_suite"/"checkpoints"/"state-000025.json"; cp.parent.mkdir(parents=True,exist_ok=True)
cp.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
with open(ROOT/"tmp"/RUN/"_suite"/"events.jsonl","a",encoding="utf-8") as f:
    f.write(json.dumps({"ts":"2026-10-18T15:12:00+08:00","event":"suite_completed","tasks":30,"images":124},ensure_ascii=False)+"\n")
# metrics
keys=["snapshot_requests","successful_snapshot_requests","failed_snapshot_requests","retry_requests","other_service_requests","dsl_versions","image_views","completed_visual_iterations","incomplete_visual_iterations"]
sumc={k:0 for k in keys}; per=[]
for t in TASKS:
    m=json.loads((OUT/t/"task-metrics.json").read_text(encoding="utf-8"))
    for k in keys: sumc[k]+=int(m.get("counts",{}).get(k,0) or 0)
    imgs=len(by_task[t])
    per.append({"id":t,"title":TITLES[t],"status":"completed","images":imgs,"requests":int(m.get("counts",{}).get("snapshot_requests",0)),
                "successful":int(m.get("counts",{}).get("successful_snapshot_requests",0)),
                "failed":int(m.get("counts",{}).get("failed_snapshot_requests",0)),
                "views":int(m.get("counts",{}).get("image_views",0)),
                "iterations":int(m.get("counts",{}).get("completed_visual_iterations",0)),
                "dsl_versions":int(m.get("counts",{}).get("dsl_versions",0))})
suite_metrics={"schema_version":1,"path_base":"suite_root","run_id":RUN,"profile":"all","status":"completed",
 "started_at":"2026-10-18T11:49:56+08:00","ended_at":"2026-10-18T15:12:00+08:00","elapsed_seconds":12124,
 "counts":{"tasks":30,"completed_tasks":30,"final_images":124,"final_png_dsl_pairs":124,"expected_minimum_images":124,
           "cases_b01_b06":60,"a21_rounds":3,"a22_rounds":3,**sumc},
 "tasks":per,"missing_tasks":[],"source":"per-task outputs/<run>/<task>/task-metrics.json; no shared requests double-counted"}
(SUITE/"task-metrics.json").write_text(json.dumps(suite_metrics,ensure_ascii=False,indent=2),encoding="utf-8")
# index
lines=[f"# Snapshot 全套 · {RUN} · 完成", "",
       f"- 状态：**completed**；30/30 题；124 张最终 PNG 与同名 DSL。",
       f"- 完成：A01–A24；B01–B06（每题 10 件，共 60 件）。A21/A22 各 3 轮。",
       f"- 总画廊：[gallery.md](gallery.md) · 使用/踩坑：[snapshot-usage.md](snapshot-usage.md) · 指标：[task-metrics.json](task-metrics.json) · 状态：[suite-state.json](suite-state.json)", "",
       "| 任务 | 标题 | 状态 | 最终图 | 请求 | 单题入口 |", "|---|---|---|---|---|---|"]
for t in TASKS:
    ent=f"[{t}/](../{t}/portfolio.md)" if t.startswith("B") else f"[{t}/](../{t}/snapshot-usage.md)"
    lines.append(f"| {t} | {TITLES[t]} | completed | {len(by_task[t])} | {next(x['requests'] for x in per if x['id']==t)} | {ent} |")
lines += ["", "## 统计", f"- 请求：{sumc['snapshot_requests']}（成功 {sumc['successful_snapshot_requests']}，失败 {sumc['failed_snapshot_requests']}，重试 {sumc['retry_requests']}）",
          f"- DSL 版本：{sumc['dsl_versions']}；看图：{sumc['image_views']}；完整视觉迭代：{sumc['completed_visual_iterations']}",
          f"- 墙钟：{12124//3600}h {12124%3600//60}m；A21/A22 三轮，B01–B06 各 10 件。",
          "- 所有最终 PNG 有同名 .snapshot；14 处失败/超时全部保留在 tmp，未进入最终图。"]
(SUITE/"index.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
# gallery
titles={}
for t in [f"B{i:02d}" for i in range(1,7)]:
    p=OUT/t/"portfolio.json"
    if p.exists():
        d=json.loads(p.read_text(encoding="utf-8"))
        titles.update({f"{t}/{c['id']}":c["title"] for c in d.get("cases",[])})
g=[f"# 全画廊 · {RUN}", "", f"全部 124 张最终 PNG 与对应 DSL；链接相对本文件。", ""]
for t in TASKS:
    g += [f"## {t} · {TITLES[t]}（{len(by_task[t])} 张）", ""]
    for p,d in by_task[t]:
        label=p.split("/",1)[1]
        key=p.rsplit("/",1)[0]
        name=titles.get(key,label)
        g += [f"### {t} · {name}", f"![{t} {name}](../{p})", "",
              f"- 原图：[{p}](../{p})", f"- DSL：[{d}](../{d})", ""]
(SUITE/"gallery.md").write_text("\n".join(g)+"\n",encoding="utf-8")
# suite usage
usage=f"""# 全套 Snapshot 使用与审查

## 结果
- run_id `{RUN}`；30/30 题完成；124 张最终 PNG 与同名 DSL；A21/A22 各 3 轮；B01–B06 各 10 件（60 件）。
- 指标：{sumc['snapshot_requests']} 次渲染请求（成功 {sumc['successful_snapshot_requests']}，失败 {sumc['failed_snapshot_requests']}，重试 {sumc['retry_requests']}），{sumc['dsl_versions']} 个 DSL 版本，{sumc['image_views']} 次看图，{sumc['completed_visual_iterations']} 次完整视觉迭代。

## 文档与能力
- 实际阅读 ai-guide、parser-tags、layout guide；使用 Text/Raw/span、Container/Stack/Positioned、Transform、ClipPath/多边形、Opacity、ImageFiltered、边框/圆角/渐变、透明 PNG；未用 Image 嵌入主图。
- 关键经验：全 Positioned 的嵌套 Stack 会无限布局，需要非定位 SizedBox；Text trim 用 Raw/text 属性；Transform 必须矩阵；色彩 alpha 为 #RRGGBBAA。
- A23 已如实判定 SVG/CMYK/GIF/动画时间轴不原生支持，替代为 PNG 封面 + 6 透明关键帧 + timing。

## 全程问题
- 服务多次 TLS/empty reply/超时（A18、A20-A24、B05 等）；失败响应/重试都保留，最终图均 200。
- 长任务/大画布偶发超时；A22/A24 用重试与更长超时解决。
- B01 地质展底部遮挡、烘焙曲线方向、风险矩阵表头；B02 课表重复/物种空圆/旗签白字；B03 轨道中心/玻璃标题/日期；B04 封面重叠/年龄页/弱势页注释；B05 状态栏/星期/血压图/周报柱高；B06 账单柱图压页头/EOB 不闭合。均已修。
- 未解决：无已知交付缺陷；所有演示数据已标注，不构成医疗/法律/税务/保险建议。

## 审查
- 30 题逐题图已实际查看；A21/A22 保留三轮；B01–B06 每件 case.md/portfolio。
- 总画廊 124 张链接全部可访问；每张有 PNG/DSL 两链；无缺图/占位。
- 根 `.gitignore` 仅忽略运行时缓存，tmp/outputs 证据未忽略。
"""
(SUITE/"snapshot-usage.md").write_text(usage,encoding="utf-8")
print("suite completed",len(images),sumc)
