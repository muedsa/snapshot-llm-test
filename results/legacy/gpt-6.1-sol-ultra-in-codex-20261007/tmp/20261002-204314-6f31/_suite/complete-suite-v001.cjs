const fs=require('node:fs'),path=require('node:path'),s=require('./suite.cjs'),d=s.taskDirs('shared'),J=x=>JSON.stringify(x,null,2)+'\n',wx=(p,v)=>fs.writeFileSync(p,v,{flag:'wx'});
const gates=[
 'root-final-review-v001.json',
 'final-integrity-v002/state-metrics-preclose-v002.json',
 'final-integrity-v002/integrity-30-v004.json',
 'final-integrity-v002/raster-audit-v002.json',
 'final-document-audit-v001/audit-final-v002.json'
].map(rel=>{const file=path.join(d.temp,rel),r=JSON.parse(fs.readFileSync(file,'utf8'));if(r.passed!==true)throw Error('Actual final gate did not pass: '+rel);return {file,sha256:s.sha256(fs.readFileSync(file)),passed:true};});
const rootReview=JSON.parse(fs.readFileSync(gates[0].file,'utf8'));if(rootReview.visual_audit_passed!==true)throw Error('Actual suite visual review missing');
const before=s.inspectAudit();wx(path.join(d.temp,'root-pre-completion-audit-v001.json'),J(before));if(!before.passed)throw Error(J(before.issues));
if(s.readState().status==='completed')throw Error('Already completed; do not overwrite completion chronology');
const state=s.suiteEnd('completed',{visual_audit_passed:true,final_review_file:gates[0].file,final_file_audit:path.join(d.temp,'root-pre-completion-audit-v001.json'),independent_evidence:gates,unresolved_issues:[],resume_notes:'All30 tasks and124 formal original service PNGs complete;60 creative cases; sequential preset rounds, real original-image and full-suite overview reviews and final integrity/state/metrics/document audits passed.'});
const currentMetrics=JSON.parse(fs.readFileSync(path.join(d.output,'task-metrics.json'),'utf8'));
const sources=JSON.parse(fs.readFileSync(path.join(s.taskDirs('B04').output,'sources.json'),'utf8'));
currentMetrics.additional_tool_consumption={native_search_calls:sources.search.native_tool_calls,source:path.join(s.taskDirs('B04').output,'sources.json'),internal_http_requests:null,network_response_bytes:null,model_or_service_billing:null,scope:'Three real B04 native search tool calls, separately recorded. Not added to the225 known direct HTTP log events or measured raw HTTP entity bytes.',archival_result_paths:sources.search.raw_results_available.map(x=>path.join(s.taskDirs('B04').temp,x)),exact_second_result_text:sources.search.exact_result_text.native_tool_json_text_exact};
currentMetrics.timings.wall_clock_limitation='Elapsed wall includes multi-day platform interruptions and resumes. No active-model-time estimate is claimed; request duration sum is measured independently.';
wx(path.join(d.temp,'aggregate-history/native-tool-scope-final-v001.json'),J(currentMetrics));fs.writeFileSync(path.join(d.output,'task-metrics.json'),J(currentMetrics));
const after=s.inspectAudit();wx(path.join(d.temp,'root-post-completion-audit-v001.json'),J(after));if(!after.passed)throw Error(J(after.issues));
s.writeSuiteReport({audit_result:after,audit_file:path.join(d.temp,'root-post-completion-audit-v001.json'),visual_audit_statement:'全套最终审查通过，30题 completed、124张正式原服务PNG及完整同名DSL、60件新增B类独立作品。各题内容、数据、几何、效果与实际完整原图审查有逐题/轮次/用例证据；root又实际查看全124图六页总览。A21/A22各三轮顺序归档、教学示例、全图链接、过程与失败、字节/尺寸/数值汇总全部通过。参见 [final-audit.md](final-audit.md)。无未解决事项。自动文件核验与实际视觉结论分别说明范围。',lessons:[{task_id:'B04',observed:'第二次搜索原结果当时未单独保存',change:'从同会话原始工具输出恢复正文与完整选中call/output事件，另保存无附加LF的exact工具JSON文本',verification:'原调用ID、时间、SHA与LF存档差别保留，0新搜索/HTTP；内部网络数和费用未知'},{task_id:'B05',observed:'case09/10导入查看用途复制case08字样',change:'保留旧日志并追加tool-purpose-correction-v001.json，更正现行报告',verification:'真实req14/view12、req15/view13对应，0新增看图/迭代'},{task_id:'shared',observed:'最终文件审查发现B01–B05缺Markdown画廊',change:'补五份全十件PNG/DSL/case索引，原失败审查保留',verification:'新编号30/124审查及六份B画廊追加审查通过'}],remaining_issues:[]});
let report=fs.readFileSync(path.join(d.output,'snapshot-usage.md'),'utf8');
const corrections=JSON.parse(fs.readFileSync(path.join(s.taskDirs('B05').temp,'tool-purpose-correction-v001.json'),'utf8')).corrections;
for(const c of corrections){const lines=report.split('\n');for(let i=0;i<lines.length;i++)if(lines[i].startsWith('- B05/')&&lines[i].includes('证据 ID '+c.tool_id+'。'))lines[i]=`- B05/${c.case_id}：既有生产者实际查看记录导入；${c.purpose}；证据 ID ${c.tool_id}，实际 ${c.request_id}/${c.view_id}；原日志复制字样按不可覆盖更正文件修正，0新增查看。`;report=lines.join('\n');}
report=report.replace('所有题状态均为 completed；是否全套可最终交付仍需总审查记录与实际视觉审查结论支持。','全部30题及全套最终审查已完成；当前套件状态completed。全套完成结论由实际视觉审查、逐题需求/数据/几何/效果证据及独立完整性/汇总审查共同支持，剩余事项0项。');
s.report('shared',report+'\n\n原生搜索另外有B04三次真实工具调用，内部HTTP/网络字节与计费未提供，保持null；不混入201渲染+23文档+1其他=225条已知HTTP或35,587,104响应实体字节。第二次原结果恢复有exact原工具JSON文本与末尾LF归档版，未新搜索、未重构。原请求、失败、版本、局部预览、查看/比较与不可覆盖检查点在统一临时目录保留。\n');
const finalMd=path.join(d.output,'final-audit.md'),prior=fs.readFileSync(finalMd,'utf8');wx(path.join(d.temp,'final-audit-before-completion-v001.md'),prior);
fs.writeFileSync(finalMd,prior.replace('本记录在套件状态完成转换前建立；最终状态以[suite-state.json](suite-state.json)为准。',`最终结论：completed。结束时间${state.ended_at}；全部30题、124图、60件开放作品及总审查通过，剩余事项0项。[当前进度](suite-state.json) · [消耗指标](task-metrics.json)。\n\n[完成后文件审查](${path.relative(d.output,path.join(d.temp,'root-post-completion-audit-v001.json')).split(path.sep).join('/')})已通过；独立汇总对最终完成状态另作核验并保存新编号。`));
const record={run_id:state.run_id,status:state.status,ended_at:state.ended_at,completed_tasks:30,final_pngs:124,independent_cases:60,visual_audit_passed:true,unresolved_issues:[],gates,counts:currentMetrics.counts,resources:currentMetrics.resources,timings:currentMetrics.timings,actual_model_or_image_cost:currentMetrics.usage,checkpoint:state.last_checkpoint,closure_audit:path.join(d.temp,'root-post-completion-audit-v001.json')};
wx(path.join(d.temp,'suite-completion-v001.json'),J(record));
const final=s.inspectAudit();wx(path.join(d.temp,'root-completed-entry-audit-v001.json'),J(final));if(!final.passed)throw Error(J(final.issues));
console.log(J(record));
