'use strict';
const fs=require('fs'),path=require('path');const {P,txt,arc,phone,button,foot,card,check}=require('../ui.cjs');
const dir=__dirname,started=new Date().toISOString();
function write(name,v){fs.writeFileSync(path.join(dir,name),v,{flag:'wx'});}
function save(id,c,meta){write(id+'-v001.snapshot',c.toString());write(id+'-metadata-v001.json',JSON.stringify({id,...meta,audience:'北院宿舍住户',dimensions:[720,1440],device:'Phone, 360×720 logical pixels at 2× raster density',content_basis:'全部机器、费用、日期、状态与凭证为自拟演示；没有真实传感器、支付、预约或用户调研。',source_ids:[],supporting_assets:[],creative_started_at:started,created_at:new Date().toISOString(),checks:{logical_consistency:'checked against product-plan-v001.json',body_font_px_min:28,button_height_px:88,rendered:false,visual_passed:null},completion_criteria:['720×1440，正文至少28px，按钮88px','同一洗序产品及北院C2情景一致','状态、费用、时段与下一步清楚','真实服务PNG实际查看后才能判断可读性','静态原型与演示数据声明完整']},null,2)+'\n');}
function washer(c,x,y,r,color=P.teal){c.rect(x-r,y-r,r*2,r*2,'#FFFFFF',{radius:r*.3,border:'2 SOLID '+color});c.circle(x,y+6,r*.55,'#E7F3EF',{border:'3 SOLID '+color});arc(c,x,y+6,r*.38,.2,2.9,color,3);c.circle(x-r*.5,y-r*.58,3,color);c.line(x-r*.12,y-r*.58,x+r*.53,y-r*.58,color,3);}
// 02: Six-machine availability overview with one tentative selection.
{
const c=phone('02 / 10','把空闲放进\n自己的时间里','北院1层洗衣房 · 状态更新于18:20','18:20');
txt(c,40,402,640,44,'先选机器，再确定洗衣周期',29,P.ink,true);
const machines=[{id:'C1',kind:'洗衣',state:'使用中',extra:'18:40可用',fill:P.white,col:P.muted},{id:'C2',kind:'洗衣',state:'可约 · 已选',extra:'18:30–19:10',fill:P.mint,col:P.teal},{id:'C3',kind:'洗衣',state:'运行中',extra:'暂不可约',fill:P.white,col:P.muted},{id:'C4',kind:'洗衣',state:'维护中',extra:'暂不可约',fill:'#F3DED3',col:P.coral},{id:'D1',kind:'干衣',state:'使用中',extra:'至19:15',fill:P.white,col:P.muted},{id:'D2',kind:'干衣',state:'空闲',extra:'可在现场使用',fill:P.white,col:P.teal}];
for(let i=0;i<6;i++){let m=machines[i],x=i%2?372:40,y=464+Math.floor(i/2)*178;card(c,x,y,308,164,m.fill);if(i===1)c.rect(x,y,308,164,'#00000000',{radius:26,border:'3 SOLID '+P.teal});txt(c,x+20,y+17,205,46,m.id+' · '+m.kind,30,P.ink,true);washer(c,x+266,y+43,25,m.col);txt(c,x+20,y+69,266,39,m.state,28,m.col,true);txt(c,x+20,y+111,268,41,m.extra,28,P.ink);}
card(c,40,1023,640,95,'#E3EAE3');txt(c,62,1038,597,45,'当前选择：C2 · 18:30开始',30,P.ink,true);txt(c,63,1080,594,38,'标准40分钟时段可约',28,P.muted);
button(c,1150,'选 C2 · 下一步');button(c,1250,'返回，换一间洗衣房',true);foot(c);
save('case-02',c,{title:'把空闲放进自己的时间里',journey_state:'availability',current_time:'2026-10-08T18:20:00+08:00',use_context:'到洗衣房前，住户在手机上查看六台设备的当时状态',user_goal:'从机器状态与可约时段判断选择C2进入周期选择',visual_intent:'机器状态以六张2列卡片聚合；同一种简化滚筒几何和真实文字状态并置，薄荷填色只突出选中C2；下方清楚落到选定时间而非只展示机器照片',journey_next:'case-03',demonstration_values:{room:'北院1层洗衣房',selected_machine:'C2',selected_slot:'18:30–19:10',C1:'使用中，18:40可用',C3:'运行中',C4:'维护中',D1:'使用至19:15',D2:'空闲'},assumptions:['D2空闲状态为演示；未承诺锁定干衣机','当前选择不是已确认预约','真实设备状态和时段锁定尚未实现']});
}
// 03: Cycle choice: standard fits the already selected 40-minute slot.
{
const c=phone('03 / 10','选40分钟\n这一次','北院1层 · C2 · 今日18:30开始','18:21');
txt(c,40,406,640,44,'洗衣周期',30,P.ink,true);
card(c,40,465,640,272,P.mint);c.rect(40,465,640,272,'#00000000',{radius:26,border:'3 SOLID '+P.teal});
c.circle(624,515,23,P.teal);check(c,605,503,P.white);txt(c,66,490,488,54,'标准洗衣',36,P.ink,true);txt(c,65,559,366,71,'40 分钟',48,P.teal,true);txt(c,454,559,179,71,'¥4',48,P.teal,true);c.line(65,644,654,644,'#97C7B4',2);txt(c,65,664,589,47,'18:30开始 · 19:10结束',30,P.ink);
card(c,40,762,640,252,P.white);c.circle(624,815,23,P.white,{border:'3 SOLID '+P.line});txt(c,66,788,488,53,'加长洗衣',36,P.ink,true);txt(c,65,850,366,68,'60 分钟',43,P.ink,true);txt(c,453,850,179,68,'¥6',43,P.ink,true);txt(c,65,936,588,49,'需另选60分钟空档',28,P.muted);
txt(c,42,1051,637,75,'已选标准 · 本次¥4\n预约不扣费，现场开始时付款。',28,P.ink);
button(c,1150,'确认标准 · 预约时段');button(c,1250,'返回机器列表',true);foot(c);
save('case-03',c,{title:'选40分钟这一次',journey_state:'cycle-choice',current_time:'2026-10-08T18:21:00+08:00',use_context:'手机上选择洗衣周期，准备提交C2预约',user_goal:'比较标准40分钟¥4与加长60分钟¥6，确认当前40分钟空档对应的标准周期',visual_intent:'两种周期采用大小不同的比较板；选中方案用薄荷底、清楚勾选和起止时刻，次方案保持白底并标明需另选60分钟空档；费用与选择同时可读',journey_next:'case-04',demonstration_values:{machine:'C2',chosen_cycle:'标准洗衣',chosen_duration_min:40,chosen_fee_cny:4,chosen_slot:'18:30–19:10',alternative_duration_min:60,alternative_fee_cny:6},assumptions:['加长周期为演示选项；现有40分钟空档不可直接运行60分钟','不提供布料、医疗、清洁或安全建议','费用在现场确认开始时才扣费']});
}
// 04: Confirmed original booking; original code will later be invalidated by fault.
{
const c=phone('04 / 10','预约留住\n一个时段','预约成功。到洗衣房现场确认后再开始。','18:22');
card(c,40,416,640,430,P.white);c.circle(616,478,31,P.mint);check(c,598,465,P.teal);txt(c,66,440,504,51,'北院1层 · C2',36,P.ink,true);txt(c,65,514,594,64,'18:30–19:10',47,P.ink,true);txt(c,66,589,587,46,'10月8日 · 标准40分钟 · ¥4',28,P.muted);c.line(65,650,655,650,P.line,2);txt(c,65,671,592,47,'现场取用码',28,P.muted);txt(c,66,716,588,98,'4261',75,P.teal,true);
txt(c,40,874,640,49,'订单 WL-1008-026',30,P.ink,true);
card(c,40,945,640,171,'#E5EAE3');txt(c,65,964,592,48,'免费取消截止 18:25',30,P.ink,true);txt(c,65,1024,592,68,'目前未扣费。\n在现场确认开始时支付¥4。',28,P.muted);
button(c,1150,'查看位置 · 准时到场');button(c,1250,'取消预约',true);foot(c);
save('case-04',c,{title:'预约留住一个时段',journey_state:'original-confirmed',current_time:'2026-10-08T18:22:00+08:00',use_context:'预约后住户在手机上核对机器、时段、现场凭证和取消规则',user_goal:'保存C2预约信息，理解未扣费与18:25免费取消截止，准备18:30到场',visual_intent:'预约信息排成克制的电子凭证，顶部成功勾选与大时刻明确预约结果，取用码作为独立视觉焦点；规则卡紧邻主操作解释费用发生时点',journey_next:'case-05',demonstration_values:{order_id:'WL-1008-026',machine:'C2',slot:'18:30–19:10',code:'4261',free_cancel_until:'18:25',paid_cny:0,start_fee_cny:4},assumptions:['取用码是演示凭证','静态画面未真正创建或取消预约','免费取消截止后的规则需另行定义，未臆造费用','现场位置查询是未实现的原型操作']});
}
write('production-notes-v001.json',JSON.stringify({task_id:'B05',producer:'/root/b04_cases_02_04',created_at:started,actual_reads:['B05/source-evidence/read-000001/command-output.txt (all task sources and inputs)','B05/product-plan-v001.json','B05/ui.cjs'],shared_document_application:['Guide: UTF-8 Snapshot text/plain and real PNG only','Parser: Container decoration, Positioned/Stack, Text Raw and explicit heights, Transform line geometry','Available fonts reused: Inter,Noto Sans CJK SC'],new_http_requests:0,images_viewed:0,files:['case-02-v001.snapshot','case-03-v001.snapshot','case-04-v001.snapshot'],status:'Local candidate DSL; final quality needs real root render and view'},null,2)+'\n');
console.log(JSON.stringify({started,dir,cases:['case-02','case-03','case-04']}));
