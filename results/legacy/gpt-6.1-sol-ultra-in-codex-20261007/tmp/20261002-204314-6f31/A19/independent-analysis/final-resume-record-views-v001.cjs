'use strict';
const fs = require('node:fs');
const path = require('node:path');
const s = require('../../_suite/suite.cjs');
const base = path.resolve(__dirname, '..');
const specs = [
  ['A19-request-000001','occlusion-A','原始800遮挡A实际查看：CASE01/02两不透明板完整，无遮挡泄漏、虚线或隐藏标签；六可见V标签清楚，V02/V05为方，V06为圆角方。'],
  ['A19-request-000002','occlusion-B','原始800遮挡B实际查看：和A的可见布局与图形完全相同；两完整遮挡板无边缘泄漏，六V对象与标签清楚。'],
  ['A19-request-000003','grid','原始1600网格实际查看：8×8主体和G01–G64按行清楚完整，坐标/尺寸/原点图例可读；标签全在主体下方，圆环内孔、圆角方和方形可区分。']
];
const records=[];
for(const [request,case_id,observation] of specs){
  const meta=JSON.parse(fs.readFileSync(path.join(base,'requests',request,'render-result.json'),'utf8'));
  records.push(s.view('A19',meta.image_path,{tool:'functions.view_image',version_id:meta.version_id,case_id,reviewer:'/root/a19_audit_resume',view_detail:request==='A19-request-000003'?'original':'high',review_scope:'Independent resumed final review of actual original service PNG',observation}));
}
const quadObservations=[
  'Q1局部原像素实际查看：G01–04/G09–12/G17–20/G25–28全部完整，ID清楚；G10/G11/G20/G27环内孔完整，圆角方与方形明确，最小48px主体可辨。',
  'Q2局部原像素实际查看：G05–08/G13–16/G21–24/G29–32全部完整，ID清楚；G23/G24/G30/G31环，G07/G16/G13/G21/G23/G24/G31/G32为80px，与48/64明显区分。',
  'Q3局部原像素实际查看：G33–36/G41–44/G49–52/G57–60全部完整，ID清楚；Q02锚点G42绿色环和相邻目标G43橙方可见，G59尺寸80的绿方清楚。',
  'Q4局部原像素实际查看：G37–40/G45–48/G53–56/G61–64全部完整，ID清楚；G48紫色小环、G55蓝圆、G61紫小方与所有环孔清楚。'
];
for(let i=1;i<=4;i++)records.push(s.view('A19',path.join(base,'grid-production',`grid-Q${i}-qa-v001.png`),{tool:'functions.view_image',version_id:'A19-grid-v001',case_id:'grid',reviewer:'/root/a19_audit_resume',view_detail:'original',review_scope:'Independent resumed native-pixel quadrant review; QA crop only, final PNG unchanged',quadrant:`Q${i}`,source_service_png:path.join(base,'requests','A19-request-000003','response.png'),observation:quadObservations[i-1]}));
const target=path.join(__dirname,'final-resume-actual-views-v001.json');
fs.writeFileSync(target,JSON.stringify({task_id:'A19',reviewer:'/root/a19_audit_resume',recorded_at:new Date().toISOString(),actual_visual_calls:7,records},null,2)+'\n',{flag:'wx'});
process.stdout.write(JSON.stringify({view_ids:records.map(v=>v.id),record_file:target})+'\n');
