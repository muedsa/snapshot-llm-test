const fs=require('fs'),path=require('path');
const s=require('../../_suite/suite.cjs');
const old=JSON.parse(fs.readFileSync(path.join(__dirname,'../map-geometry-v001.json'),'utf8'));
const next=JSON.parse(fs.readFileSync(path.join(__dirname,'../map-geometry-v002.json'),'utf8'));
const paths=JSON.parse(fs.readFileSync(path.join(__dirname,'../paths-v001.json'),'utf8'));
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const added=next.arrows.filter(a=>!old.arrows.some(b=>eq(a,b)));
const route=paths.routes.find(r=>r.id==='route-02').cell_centers;
const newChecks=added.map(a=>({source:a.source_cell,target:a.target_cell,purpose:a.purpose,
 on_route_in_correct_direction:route.slice(1).some((q,i)=>eq(route[i],a.source_cell)&&eq(q,a.target_cell)),
 vector_matches:a.target_cell[0]===a.source_cell[0]?a.tip[0]===a.tail[0]&&(a.tip[1]-a.tail[1])*(a.target_cell[1]-a.source_cell[1])>0:a.tip[1]===a.tail[1]&&(a.tip[0]-a.tail[0])*(a.target_cell[0]-a.source_cell[0])>0}));
const view=s.view('A08','D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/A08/requests/A08-request-000002/response.png',{
 tool:'view_image',reviewer:'graph_auditor',version_id:'A08-v002',
 observation:'实际查看v002最终响应全图：B支路新增向上箭头(11,4→11,3)及离开B向下箭头(12,3→12,4)清楚，未压B字母或墙；双路共享格心蓝底/橙虚线均可追踪，S/E/四区/坐标标尺/侧栏与图例无裁切。全部墙与门洞视觉保持，新增箭头未更改路径。'
});
const report={generated_at:new Date().toISOString(),task_id:'A08',cells_unchanged:eq(old.cells,next.cells),routes_unchanged:eq(old.routes,next.routes),
 baseline_full_geometry_review:'produced-geometry-review-v001.json',added_arrow_count:added.length,new_arrow_checks:newChecks,
 changed_geometry_passes:eq(old.cells,next.cells)&&eq(old.routes,next.routes)&&added.length===2&&newChecks.every(c=>c.on_route_in_correct_direction&&c.vector_matches),view_event:view};
fs.writeFileSync(path.join(__dirname,'final-geometry-visual-review-v002.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(report,null,2));
