const fs=require('node:fs'),path=require('node:path'),s=require('../../_suite/suite.cjs');
const read=n=>JSON.parse(fs.readFileSync(path.join(__dirname,n),'utf8')),write=(n,d)=>fs.writeFileSync(path.join(__dirname,n),d,{flag:'wx'});
const r=read('render-baseline-v001.json'),qa=read('qa-quadrant-provenance-v001.json');
// Real but incidental view is preserved separately; it is not grid review evidence.
const accidentalPath=path.resolve(__dirname,'../requests/A19-request-000001/response.png'),accidentalMetaPath=path.join(path.dirname(accidentalPath),'render-result.json');
const accidentalMeta=JSON.parse(fs.readFileSync(accidentalMetaPath,'utf8'));
const incidental=s.view('A19',accidentalPath,{tool:'view_image',viewer:'a19_grid_producer',version_id:accidentalMeta.version_id,case_id:accidentalMeta.case_id??'occlusion',review_scope:'incidental_wrong_request_path',passes_visual_check:null,observation:'真实打开了800×800遮挡图，显示CASE01/CASE02、深色遮挡板与V01–V06；此前view误用了并行请求000001路径。它不作为grid内容通过依据；已改为grid meta实际返回000003路径，真实另行看正确原图。'});
write('incidental-view-mispath-v001.json',JSON.stringify({actual_event:incidental.id,actual_path:accidentalPath,intended_grid_path:r.image_path,reason:'Assumed first request ID instead of taking returned concurrent-render metadata path.',correction:'Immediately opened true grid returned metadata response.png; preserve extra real view honestly.',HTTP_request:false,new_render:false,not_grid_review_evidence:true},null,2)+'\n');
const fullObservation='实际打开正确1600×1600 grid原PNG：8×8网格64主体，G01–G64行优先、24px编号全部在主体下方；中心x240…1360/y312…1432坐标轴、左上原点/x右y下和48/64/80尺寸定义清晰。蓝橙绿紫和圆/方/环/圆角方区别明确；最小48主体与最大80主体可辨，环孔居中、外内径2:1，与外置ID有留白，没有任何主体或编号裁切/相交。';
const full=s.view('A19',r.image_path,{tool:'view_image',viewer:'a19_grid_producer',version_id:r.version_id,case_id:'grid',observation:fullObservation,passes_visual_check:true});
const descriptions={
 Q1:'实际查看左上4×4：G01紫圆、G02橙圆角方、G03绿圆、G04绿圆角方；G09蓝圆角方、G10紫环、G11橙环、G12橙方；G17橙圆角方、G18紫圆角方、G19蓝圆角方、G20紫环；G25绿圆、G26蓝圆角方、G27橙环、G28橙方。16对象与ID逐项完整，小/中/大尺寸可辨；标签未靠主体或格线。',
 Q2:'实际查看右上4×4：G05蓝方、G06绿圆角方、G07蓝方、G08蓝圆；G13绿圆角方、G14绿方、G15橙圆、G16橙圆；G21橙圆角方、G22蓝圆、G23紫环、G24蓝环；G29紫圆角方、G30绿环、G31橙环、G32绿圆角方。16主体和编号逐项完整，三种尺寸及环孔明显，不裁切。',
 Q3:'实际查看左下4×4：G33橙圆角方、G34紫方、G35紫圆、G36绿环；G41蓝圆、G42绿环、G43橙方、G44紫方；G49蓝方、G50紫圆、G51蓝环、G52紫方；G57绿方、G58蓝方、G59绿方、G60橙圆。16主体/编号逐项检查，大小、方/圆角区别清楚，外置ID与主体/格线分离。',
 Q4:'实际查看右下4×4：G37绿圆、G38绿方、G39紫圆角方、G40橙环；G45蓝环、G46蓝圆角方、G47橙方、G48紫环；G53绿圆、G54橙圆、G55蓝圆、G56紫圆角方；G61紫方、G62绿环、G63蓝环、G64紫圆。16主体与ID逐项完整；底行留在画布/格内，环孔/三尺寸可辨，无叠压。'
};
const local=qa.quadrants.map(q=>s.view('A19',q.path,{tool:'view_image',viewer:'a19_grid_producer',version_id:r.version_id,case_id:'grid',view_kind:'quadrant_'+q.quadrant,reviewed_object_IDs:q.expected_objects.map(o=>o.id),observation:descriptions[q.quadrant],passes_visual_check:true}));
s.iteration('A19',{type:'baseline',version_id:r.version_id,parent_version:null,case_id:'grid',completed:true,after_view_id:full.id,additional_view_ids:local.map(v=>v.id),image_path:r.image_path,observation:'正确服务原图和4局部逐项检查全部64目标及外置24px标签通过，source数据/坐标冻结；一次基线合格，无需制造视觉修改。',passes_visual_check:true});
write('producer-grid-view-records-v001.json',JSON.stringify([full,...local],null,2)+'\n');
const checkedIDs=local.flatMap(v=>v.reviewed_object_IDs);if(checkedIDs.length!==64||new Set(checkedIDs).size!==64)throw Error('Local coverage incomplete');
write('visual-coverage-v001.json',JSON.stringify({correct_service_request:JSON.parse(fs.readFileSync(r.meta_path,'utf8')).id,full_view:full.id,quadrant_views:local.map(v=>({id:v.id,kind:v.view_kind,reviewed_object_IDs:v.reviewed_object_IDs})),all64_reviewed_once_in_quadrants:true,wrong_request_incidental_view_excluded:incidental.id,real_grid_visual_views:5,actual_extra_incidental_view:1,labels_font_size:24,visual_changes_needed:false,source_geometry_changed:false},null,2)+'\n');
console.log(JSON.stringify({full_view:full.id,quadrant_views:local.map(v=>v.id),incidental_view:incidental.id,reviewed_IDs:64}));
