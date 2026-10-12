const fs=require('node:fs'),path=require('node:path');
const rd=__dirname,old=JSON.parse(fs.readFileSync(path.join(rd,'publish-manifest-v001.json'),'utf8'));
const rootCheck=JSON.parse(fs.readFileSync(path.join(rd,'root-source-check-v002.json'),'utf8')),independent=JSON.parse(fs.readFileSync(path.join(rd,'independent-analysis/baseline-arithmetic-v001.json'),'utf8'));
if(!rootCheck.pass)throw Error('Root quantitative check not passed');
const report=fs.readFileSync(path.join(rd,'report-round-v001.md'),'utf8').replace('精确计算与独立真实DSL审查见[审计](round-audit.json)','原值独立精确计算见[算数审计](arithmetic-audit.json)，root实际提交DSL审查见[审计](round-audit.json)')+'\n\n过程补充：root源检查v001曾误判默认START对齐，v002更正为接受省略或显式START，实际83个Text全通过。旧检查及更正原因保留，作品未改；专项代理补充审查仍可在临时目录继续，不作为完成声明的前提。\n';
fs.writeFileSync(path.join(rd,'report-round-v002.md'),report,{flag:'wx'});
old.additional_files=old.additional_files.filter(a=>!['round-01/round-audit.json','round-01/snapshot-usage.md'].includes(a.relative_output));
old.additional_files.push({source:'report-round-v002.md',relative_output:'round-01/snapshot-usage.md'},{source:'root-source-check-v002.json',relative_output:'round-01/round-audit.json'},{source:'independent-analysis/baseline-arithmetic-v001.json',relative_output:'round-01/arithmetic-audit.json'});
fs.writeFileSync(path.join(rd,'publish-manifest-v002.json'),JSON.stringify(old,null,2)+'\n',{flag:'wx'});
