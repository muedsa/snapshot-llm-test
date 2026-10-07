'use strict';const fs=require('node:fs'),path=require('node:path');const s=require('../_suite/suite.cjs');
const meta=JSON.parse(fs.readFileSync(path.join(__dirname,'requests','A04-request-000001','render-result.json'),'utf8'));
const view=s.view('A04',meta.image_path,{tool:'view_image',version_id:meta.version_id,detail:'original',scope:'whole baseline realPNG1600x1000',observation:'实际查看：两个渠道的前后率30/35与10/12完整可见，两个分组率图与总体率图均0–100%且等宽508轴；总体26/16.6数值与长度一致。访问构成两条等长530，真实80/20到20/80分段；色彩在两图中一致。原始四行分子分母8,000/2,400、2,000/200、2,000/700、8,000/960及前后期/渠道都清楚，公式按访问加权。主结论置于图和表之后，不能由该数据证明因果限制完整。正文22、图注最低18，全部文字可读，没有观察到碰撞、截字或漏项。'});
s.iteration('A04',{type:'baseline',version_id:meta.version_id,parent_version:null,completed:true,image_path:meta.image_path,request_id:meta.id,after_view_id:view.id,observation:view.observation,comparison:'真实基线符合数据/几何/内容及视觉要求，无需制造修改或视觉迭代。'});
const final=s.acceptFinal('A04','conversion-story',meta,{title:'转化变化，为什么不能只看平均？',version_id:meta.version_id});
fs.writeFileSync(path.join(__dirname,'producer-accepted-v001.json'),JSON.stringify({meta,view,final},null,2)+'\n',{flag:'wx'});
s.taskCheckpoint('A04',{artifacts:[final],visual_review_evidence:[view.id],resume_notes:'A04 exact-data baseline accepted after real full image view; originalPNG and completeDSL published. Finalpathview and analysis finalize next.',checkpoint:'A04-baseline-published'});s.writeTaskMetrics('A04');
console.log(JSON.stringify({final_image:final.image_path,final_dsl:final.dsl_path,baseline_view_id:view.id}));
