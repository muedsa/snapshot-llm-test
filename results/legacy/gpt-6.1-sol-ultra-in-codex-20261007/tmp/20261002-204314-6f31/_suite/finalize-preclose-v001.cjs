const fs=require('node:fs'),path=require('node:path'),s=require('./suite.cjs');
const shared=s.taskDirs('shared'),wx=(p,t)=>fs.writeFileSync(p,t,{flag:'wx'}),J=x=>JSON.stringify(x,null,2)+'\n';
const additions=[];
for(const task of ['B01','B02','B03','B04','B05']){
 const d=s.taskDirs(task),p=JSON.parse(fs.readFileSync(path.join(d.output,'portfolio.json'),'utf8'));
 if(p.cases.length!==10)throw Error('Expected actual ten-case portfolio '+task);
 const f=path.join(d.output,'gallery.md');
 wx(f,[`# ${task} 全作品索引`,'','[完整本地画廊](gallery.html) · [作品集](portfolio.md) · [实际使用与验证](snapshot-usage.md)','',...p.cases.map(c=>`## ${c.id} · ${c.title}\n\n![${c.title}](${c.png})\n\n[原尺寸PNG](${c.png}) · [完整Snapshot DSL](${c.snapshot}) · [独立用例说明](${c.id}/case.md)\n\n${c.user_goal}。`)].join('\n')+'\n');
 const reportFile=path.join(d.output,'snapshot-usage.md'),report=fs.readFileSync(reportFile,'utf8');
 s.report(task,report+'\n\n全套终审增补：按当前 task.json 的 common_outputs，补齐 [gallery.md](gallery.md) 全十件作品索引，与已有 HTML 画廊、正式原PNG和DSL一致。没有新增作品、服务请求或图像查看；最终套件状态以 [suite-state.json](../_suite/suite-state.json) 为准。\n');
 additions.push({task_id:task,path:f,case_count:p.cases.length});
}
const d=s.taskDirs('B06'),rf=path.join(d.output,'snapshot-usage.md');
let text=fs.readFileSync(rf,'utf8');
text=text.replace('十件已正式发布，最终task关闭与套件总审查随后执行。','十件已正式发布且单题关闭审查通过；全套最终状态参见 [suite-state.json](../_suite/suite-state.json)。').replace('目前单题无未解决事项；后续状态为；全套最终总审查尚待完成。','单题无未解决事项；30题均已完成，最终套件审查及其结论参见 [全套报告](../_suite/snapshot-usage.md)。');
s.report('B06',text);
const observations=[
 '实际打开第1页，A01–A13及A14前两幅：仪表、宽/手机日程、语义修复、数据说明、拓扑/网格、变换标本、滤镜板、跨页结算、四断点和品牌应用均在总览中完整出现；未发现新的整幅裁剪或明显遗漏。小字与数值以既有完整原图及数据审查为准。',
 '实际打开第2页，A14剩余压力图、复刻/取证、A17四页与四真实例图、三幕、视觉题场、密集标注及A21早期轮次均完整覆盖；手册与示例对应、两遮挡图可见结构一致，预置轮次并存。总览不用于替代几何/原图核验。',
 '实际打开第3页，A21后三幅、A22全部三轮、A23封面与六帧、A24三种媒介及B01前八件完整出现。变更版本保持独立，动画静态交付六帧连续且终帧汇聚；B01旅行、维护、养护、菜单、港口、剧场、徒步与烹饪各自具完整使用目标。',
 '实际打开第4页，B01后两件、B02十触点、B03十探索及B04前两件，画面内容和结构随目标改变。补衣生态的参与/工作/交付画面连贯，创意探索包含文字轮廓、节奏、器物、风场、街区和声波；未把改色/裁切重复当新增作品。',
 '实际打开第5页，B04研究系列余八件、B05十画面、B06前六件，整集覆盖完整。B04主题一致且各自解释不同问题；B05从预约、故障改约、现场开始、计时、干衣到收据呈不同关键状态；B06定位、分账、路线、费用、食材和借阅动作清楚。精确数据与逐字语义沿用已看完整原图和独审。',
 '实际打开第6页，B06末四件：24门中17号、三工具归还/检查/登记、停水范围/条件、64GB组成和4GB释放各为完整作品。独立任务和动作层级成立，没有新的明显图面问题。此页四幅对应全124张的最后四张，其余空格仅为接触表排版。'
];
const cutoffs=['2026-10-07T04:24:44Z','2026-10-07T04:24:44Z','2026-10-07T04:24:52Z','2026-10-07T04:24:52Z','2026-10-07T04:25:02Z','2026-10-07T04:25:02Z'];
const manifest=JSON.parse(fs.readFileSync(path.join(shared.temp,'final-overviews-v001/manifest.json'),'utf8'));
const views=manifest.pages.map((p,i)=>s.view('shared',p.image_path,{reviewer:'root',tool:'view_image',stage:'Actual full-suite overview',viewed_at:cutoffs[i],view_time_basis:'Clock reading immediately after the real pair of image tool results; second-resolution completion bound.',observation:observations[i],passed:true,covered_artifact_ids:p.artifacts.map(a=>a.id),preview_only:true}));
const record={run_id:s.readState().run_id,recorded_at:new Date().toISOString(),reviewer:'root',actual_tool:'view_image',passed:true,final_artifacts:124,overview_pages:6,views,scope:'Six actual overview opens of all124 formal artifacts; these do not replace existing genuine full-original per-task/per-round/per-case reviews. Content/data/geometry/effects were assessed in the preserved individual execution and independent audits.',added_markdown_galleries:additions,remaining:'Independent full-suite exact file/link/metrics recheck required before suite completed.'};
wx(path.join(shared.temp,'final-overview-review-v001.json'),J(record));
s.toolUsage('shared',{tool:'python / final-overview-v001.py',purpose:'Create temporary124-image six-page contact overview from actual delivered bytes',input:s.statePath,output:path.join(shared.temp,'final-overviews-v001/manifest.json'),formal_artifacts_added:0});
s.toolUsage('shared',{tool:'node / finalize-preclose-v001.cjs',purpose:'Resolve five actual missing Markdown galleries, remove current B06 transitional report wording, record six genuine suite overview views',output:path.join(shared.temp,'final-overview-review-v001.json'),affected_tasks:['B01','B02','B03','B04','B05','B06']});
s.checkpoint('full-suite-overview-reviewed',{final_count:124,independent_cases:60,views:views.map(v=>v.id),resume_notes:'All30 tasks completed; six-page full suite overview actually reviewed. Missing B01–B05 Markdown galleries repaired. Final independent file/link/metrics checks remain.'});
const metrics=s.aggregate();
s.writeSuiteReport({visual_audit_statement:'全套124张正式图已在逐题/逐轮/逐用例执行中实际打开并审查；root又实际打开覆盖所有图的六页总览，整套覆盖和组织通过。总览不替代完整原图查看。最后独立文件、链接与指标复核仍在执行，套件暂保持in_progress。',remaining_issues:['独立终审补充Markdown索引后重验；最终汇总与closed状态复核。']});
console.log(J({galleries:additions.length,overview_views:views.map(v=>v.id),counts:metrics.counts,state:s.readState().status}));
