const fs=require('fs'),path=require('path');
const p=path.join(__dirname,'prepare-final-set-v001.cjs'),t=path.join(__dirname,'prepare-final-set-v002.cjs');
let source=fs.readFileSync(p,'utf8').replace('production/brand-system-draft-v001.json','production/brand-system-reviewed-draft-v002.json');
source=source.replace("const root=JSON.parse", "if(audit.all_hard_constraints_pass!==true)throw Error('Independent hard constraints must pass');\nconst root=JSON.parse");
source=source.replace("write('brand-system-reviewed-v002.json',brand);", "brand.alpha_exception_summary={exact_alpha_array_equal:false,support_equal:false,alpha_difference_pixels:154,max_alpha_delta:1,support_difference_0vs1_pixels:8,opaque_mask_equal:true,threshold128_mask_equal:true,max_distance_to_analytic_edge_px:0.6175884698832999,aa_allowed_by_task:true};\nwrite('brand-system-reviewed-v002.json',brand);");
source=source.replace('原失败判定保留；该精确字节条件', '差值最大1，含8处0→1抗锯齿边缘；154差点距实际DSL圆角边界≤0.617588px，无alpha255差异、alpha≥128轮廓一致。原失败判定保留；该精确字节条件');
source=source.replace('精确alpha不同保留false及原audit，', '独立alpha脚本首次因else0缺空格发生本地SyntaxError，v002修复后测量成功，原失败保存，非HTTP失败、不新增渲染。精确alpha不同保留false及原audit，');
source=source.replace("root_review_ids:root.images.map", "local_analysis_script_failures:1,root_review_ids:root.images.map");
fs.writeFileSync(t,source,{flag:'wx'});console.log(t);
