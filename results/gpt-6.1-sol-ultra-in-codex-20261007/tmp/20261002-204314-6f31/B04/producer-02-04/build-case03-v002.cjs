'use strict';
const fs=require('fs');const path=require('path');const {Canvas}=require('../../_suite/dsl.cjs');
const dir=__dirname;const started=new Date().toISOString();
const FONT='Inter,Noto Sans CJK SC';
function writeNew(name,data){const f=path.join(dir,name);fs.writeFileSync(f,data,{flag:'wx'});return f;}
function save(id,c,meta){let now=new Date().toISOString();writeNew(id+'-v002.snapshot',c.toString());writeNew(id+'-metadata-v002.json',JSON.stringify({case_id:id,...meta,dimensions:{width:c.width,height:c.height},creative_started_at:started,created_at:now,supporting_assets:[],render_status:'unrendered; root will render and visually review',checks:{factual_source_read:true,arithmetic_checked:true,visual_review_passed:null},documentation_reuse:['shared guide','parser Container/Text/Stack/Positioned/Transform','fonts Inter,Noto Sans CJK SC']},null,2)+'\n');}
function moduleIcon(c,x,y,w,h,color){c.rect(x,y,w,h,color,{radius:12,border:'2 SOLID #192F40'});c.rect(x-10,y+h*.28,10,h*.44,'#A4B4BE');c.rect(x+w,y+h*.28,10,h*.44,'#A4B4BE');for(let i=1;i<4;i++)c.line(x+w*i/4,y+4,x+w*i/4,y+h-4,'#192F4060',2);c.circle(x+w*.5,y+h*.5,h*.18,'#EAF0EC',{border:'2 SOLID #192F40'});}
function person(c,x,y,col,s=1){c.circle(x,y,12*s,col);c.line(x,y+17*s,x,y+53*s,col,9*s,{roundCaps:true});c.line(x,y+30*s,x-23*s,y+40*s,col,7*s,{roundCaps:true});c.line(x,y+30*s,x+23*s,y+40*s,col,7*s,{roundCaps:true});c.line(x,y+51*s,x-18*s,y+80*s,col,7*s,{roundCaps:true});c.line(x,y+51*s,x+18*s,y+80*s,col,7*s,{roundCaps:true});}
// 03: Precise lengths. Endpoints and bar lengths have exactly 8 px/m.
{
const c=new Canvas(1500,1120,{background:'#EAF0ED',font:FONT});const ink='#133A35',light='#70928A',gold='#BB693B',x0=246,scale=8;
c.rect(0,0,34,1120,ink);c.text(76,49,1300,35,'环绕地球的日常   /   ISS 视觉特辑 03',23,ink,{bold:true});
c.text(76,100,1280,103,'109米，究竟多长',72,ink,{bold:true});c.text(80,213,1280,45,'读长度，先对齐零点。下面三条标尺采用同一线性比例：8像素 = 1米。',25,ink);
c.rect(78,283,1350,471,'#F8FAF7',{radius:16,border:'1 SOLID #C5D6CD'});
const ys=[392,530,668],lengths=[109,80,67],colors=[ink,gold,light],labels=['ISS 太阳阵列翼展','Airbus A380 翼展','ISS 加压舱段主轴'];
for(let i=0;i<3;i++){let y=ys[i];c.text(102,y-17,130,75,labels[i],24,ink,{bold:i!==2,height:1.1});c.rect(x0,y,lengths[i]*scale,20,colors[i]);c.line(x0,y-18,x0,y+40,ink,2);c.line(x0+lengths[i]*scale,y-18,x0+lengths[i]*scale,y+40,colors[i],2);c.text(x0+lengths[i]*scale+16,y-24,192,68,String(lengths[i])+' m',42,colors[i],{bold:true});}
c.line(x0,321,x0,719,'#B0C3BB',1);for(let m=0;m<=110;m+=10){let xx=x0+m*scale;c.line(xx,719,xx,731,ink,2);c.text(xx-22,731,44,29,String(m),16,ink,{align:'CENTER'});}c.line(x0,719,x0+110*scale,719,ink,2);c.text(1172,723,155,34,'单位：米',19,ink);
c.text(92,786,475,68,'29米',44,gold,{bold:true});c.text(94,855,522,82,'两种翼展的差：109 − 80 = 29。\n空间站翼展约为 A380 的 1.36 倍。',24,ink,{height:1.3});
c.line(655,797,655,938,'#B5C5BD',2);c.text(694,797,640,45,'“长”必须说明量的是哪一轴',29,ink,{bold:true});c.text(696,855,639,91,'67米指加压舱段的主轴长度，\n不是109米太阳阵列翼展的另一种写法。',24,ink,{height:1.3});
c.rect(80,975,1347,66,ink,{radius:10});c.text(104,988,1299,45,'只比较一维长度；这里没有按面积、体积或质量绘制，更不是空间站与飞机的结构图。',23,'#F4F8F3');
c.text(84,1071,1320,27,'来源：NASA Station Facts（109m / 80m / 67m）  ·  读取 2026-10-06  ·  网页事实值，非实时测量  ·  1.36为四舍五入值',17,ink);
writeNew('case-03-geometry-v002.json',JSON.stringify({case_id:'case-03',units:'m',px_per_m:scale,origin_x:x0,bars:lengths.map((m,i)=>({label:labels[i],metres:m,start_x:x0,end_x:x0+m*scale,pixel_length:m*scale,y:ys[i]})),difference_m:109-80,exact_ratio:109/80,shown_ratio:1.36,verification:'Exact arithmetic checked in this script; final service PNG remains to be visually inspected'},null,2)+'\n');
save('case-03',c,{title:'109米，究竟多长',audience:'中学生、亲子科学读者',use_context:'科学馆尺寸解读展板，印刷或平板近读',user_goal:'使用一致零点和同一线性尺度比较ISS翼展、A380翼展，区分翼展和加压舱段主轴',content_basis:{kind:'真实尺寸事实与派生计算',facts:{iss_solar_array_wingspan_m:109,airbus_a380_wingspan_m:80,iss_pressurized_module_major_axis_m:67},calculations:{difference_m:29,ratio_exact:1.3625,ratio_display:1.36,px_per_m:8},limitations:['只显示一维长度，不显示物体轮廓、面积、体积或质量','来源网页尺寸口径，不宣称当前实时测量']},source_ids:['facts'],visual_intent:'统一零点的三条精确线性标尺，以留白与材料色把一维测量从工程轮廓误解中分离；低部展开比较逻辑',completion_criteria:['109/80/67m长度分别为872/640/536px','三条共用x=246零点','区分翼展和舱段主轴','显示29m与约1.36倍派生值','文字清晰且单位和限制显著','真实PNG实际查看后完成']});
}
