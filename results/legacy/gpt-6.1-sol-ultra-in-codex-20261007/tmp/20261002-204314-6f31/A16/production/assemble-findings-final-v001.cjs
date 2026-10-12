'use strict';
const fs=require('node:fs'),path=require('node:path');const root=path.resolve(__dirname,'../../../..');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const src=path.join(root,'tmp/20261002-204314-6f31/A16/independent-analysis/findings-draft-v001.json');
const orig=read(src),review=read(path.join(__dirname,'producer-baseline-review-v001.json'));
const outcomes=[
['标题已显示“季度复盘：Q4利润54万元，全年最高”；与源四季利润比较一致。',[42,48,1232,100]],
['副标题明确Q3收入较Q2下降5.2%，未声称全季连续增长；Q4利润环比68.8%准确按68.75%四舍五入。',[42,106,1232,143]],
['最终图蓝色块标收入、橙色块标成本，与八柱色彩及数字一一对应。',[598,241,825,274]],
['最终纵轴可见0/50/100/150/200；八柱均从同一y560零线向上，无100截断基线。',[68,275,816,562]],
['实际图Q3蓝柱顶y387.2比Q2顶y377.75更低；八柱由源值×1.35px/万元构造，视觉顺序与比例正确。',[181,317,791,560]],
['最终利润四列30/27/32/54万元，Q3显示128−96=32，另显示全年利润143万元。',[64,665,812,823]],
['右侧重点改为Q4，利润54万元、利润率30.0%、较Q3多22万元及68.8%；只说明全年历史排名并注明历史表现不代表未来回报。',[864,170,1240,848]]
];
const findings=orig.findings.map((f,i)=>({...f,final_view_result:{passed:true,actual_view_id:review.view_id,image_path:review.actual_image_path,version_id:review.version_id,corrected_region_xyxy:outcomes[i][1],observation:outcomes[i][0],measurement_status:i===3||i===4?'Producer realimagevisualreviewplusDSLfloatingpointgeometry;independentpixelmeasurementreferencedwhenavailable.':'Produceractualimagevisuallychecked.'},verification_status:'corrected_actual_png_visually_verified'}));
const out={...orig,producer_reviewed_at:new Date().toISOString(),source_provenance:src,producer_source_view_id:'A16-view-000003',producer_final_view_id:review.view_id,final_png:review.actual_image_path,final_version:review.version_id,findings,uncertain:orig.uncertain.map(u=>({...u,final_disposition_verified_by_actual_view:review.view_id})),status:'producer_actual_final_png_verified;independent_final_geometry_review_pending'};
fs.writeFileSync(path.join(__dirname,'findings-final-draft-v001.json'),JSON.stringify(out,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({path:path.join(__dirname,'findings-final-draft-v001.json'),confirmed:findings.length,uncertain:out.uncertain.length,actual_final_view:review.view_id}));
