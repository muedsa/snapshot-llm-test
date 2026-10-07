const fs=require('fs'),path=require('path'),s=require('../_suite/suite.cjs'),d=s.taskDirs('A12');
const f=path.join(d.output,'snapshot-usage.md');
s.report('A12',fs.readFileSync(f,'utf8')+'\n\n独立审计JSON组装另有4次真实本地命令/脚本失败（数字开头key、PowerShell行内转义、缺脚本），由审查者明确报告并在independent-analysis/assembly-failures-v001/v002等版本证据留存；修复后的最终JSON通过。它们不影响真实PNG、不计HTTP失败或视觉迭代，未删除旧尝试。共享publish-reviewed-set.cjs在本题首次实际用于4图及JSON发布，publication-result-v001.json保存实际结果；此前只做过--help。\n');
s.writeTaskMetrics('A12',{local_audit_assembly_failed_calls:4,local_failure_evidence_dir:path.join(d.temp,'independent-analysis'),publisher_used:'publish-reviewed-set.cjs'});
console.log('Preserved separate local audit failure disclosure; no request/view/iteration counts added.');
