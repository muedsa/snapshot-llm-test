const fs=require('node:fs'),path=require('node:path');
let t=fs.readFileSync(path.join(__dirname,'publish-portfolio.cjs'),'utf8');
t=t.replace("'所有自拟内容均为演示，未部署。'","m.content_disclosure??'所有自拟内容均为演示，未部署。'");
t=t.replace('目前单题无未解决事项；全套B02–B06及最终总审查尚待完成。','目前单题无未解决事项；后续状态为${s.readState().tasks.filter(t=>t.status!=="completed"&&t.id!==task).map(t=>t.id+":"+t.status).join("、")}；全套最终总审查尚待完成。');
t=t.replace("m.final_collection_review.statement,'','## 复现与剩余事项'","m.final_collection_review.statement,...(m.report_notes??[]),'','## 复现与剩余事项'");
fs.writeFileSync(path.join(__dirname,'publish-portfolio-v002.cjs'),t,{flag:'wx'});
