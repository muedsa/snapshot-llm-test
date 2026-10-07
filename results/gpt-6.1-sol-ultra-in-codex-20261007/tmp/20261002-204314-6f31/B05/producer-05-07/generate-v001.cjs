const fs=require('node:fs'),path=require('node:path');
const {P,Canvas,txt,arc,logo,phone,button,foot,card,check}=require('../ui.cjs');
const DIR=__dirname,started='2026-10-06T11:13:45Z';
function save(id,c,m){fs.mkdirSync(DIR,{recursive:true});fs.writeFileSync(path.join(DIR,id+'-v001.snapshot'),c.toString(),{flag:'wx'});fs.writeFileSync(path.join(DIR,id+'-metadata-v001.json'),JSON.stringify({case_id:id,dimensions:[c.width,c.height],creative_started_at:started,creative_started_at_source:'clock tool at actual B05 production start',created_at:new Date().toISOString(),content_basis:{type:'fictional_static_demo',description:'洗序产品、北院宿舍/机器/费用/订单/取用码/状态全部自拟，静态概念界面，未部署、未连接传感器或支付、未做真实用户验证'},checks:{visual_verified:false,service_request_by_this_agent:false,visual_review_owner:'root',static_data_consistency:'matches B05 product-plan-v001 scenario'},supporting_assets:[],...m},null,2),{flag:'wx'});}
// 05: fail safely, explain what happened before suggesting a replacement.
{
 const c=phone('05','C2故障，\n预约已自动取消','原预约未扣费。\n可以换一台，或结束这次预约。','18:29');
 card(c,40,424,640,289,'#F9E2D7');
 c.rect(76,463,137,139,'#FFF9F0',{radius:16,border:'2 SOLID #CBA69B'});c.rect(90,477,105,17,'#E3C8BC',{radius:4});c.circle(144,549,39,'#EBCEC0',{border:'3 SOLID '+P.coral});c.line(116,521,171,576,P.coral,6,{roundCaps:true});c.line(116,576,171,521,P.coral,6,{roundCaps:true});
 txt(c,245,449,403,50,'原预约 · C2',31,P.ink,true);
 txt(c,245,513,403,45,'18:30–19:10',30,P.ink,true);
 txt(c,245,575,403,44,'WL-1008-026',28,P.muted);
 txt(c,76,645,570,43,'旧取用码4261已失效',28,P.ink,true);
 txt(c,40,745,640,42,'为你找到一个替代时段',30,P.ink,true);
 c.card(40,805,640,253,P.white,{radius:26,border:'2 SOLID '+P.teal});
 c.circle(88,860,17,P.mint,{border:'2 SOLID '+P.teal});c.circle(88,860,7,P.teal);
 txt(c,123,833,506,49,'C1 · 标准40分钟',33,P.ink,true);
 txt(c,76,898,568,66,'18:40–19:20',43,P.ink,true);
 txt(c,76,981,568,44,'¥4 · 现场确认开始时扣费',28,P.muted);
 button(c,1097,'改约 C1 · 18:40');
 button(c,1219,'退出本次预约',true);
 foot(c);
 save('case-05',c,{title:'机器故障之后，先讲清发生什么',audience:'已预约宿舍洗衣但收到设备故障通知的住户',use_context:'2026-10-08 18:29手机故障恢复选择页，720×1440按360逻辑像素2倍设计',user_goal:'确认旧预约自动取消且未扣费，识别旧码失效，决定改约C1或退出',visual_intent:'先以柔和故障色解释旧状态，随后用单个清楚的替代时段和两个真实决策操作降低不确定感',completion_criteria:['C2故障与原订单WL-1008-026取消/未扣费清楚','旧码4261失效明示','C1标准40分钟18:40–19:20，4元现场开始才扣费','改约或退出两种下一步明确，正文≥28px/按钮88px'],journey_state:'fault-recovery-choice',current_time:'2026-10-08T18:29:00+08:00',actions:{primary:{label:'改约 C1 · 18:40',next_case:'case-06',effect:'用C1 18:40–19:20替代原故障预约，生成新订单和新码；仍未扣费'},secondary:{label:'退出本次预约',effect:'结束本次预约流程，原故障订单已取消且未扣费'}},money_state:{charged_cny:0,refunded_cny:0,reservation_fee_cny:0,pay_at_start_cny:4}});
}
// 06: a new credential is the centre; no premature start action on phone.
{
 const c=phone('06','新的预约，\n新的开始码','C1已预约。\n到18:40，再在现场确认付款开始。','18:30');
 card(c,40,422,640,324);
 check(c,592,461);
 txt(c,76,452,480,44,'新的取用码',30,P.muted,true);
 txt(c,76,504,568,152,'5372',112,P.teal,true);
 txt(c,76,683,568,43,'新预约 WL-1008-027',28,P.ink);
 card(c,40,788,640,190,P.mint);
 txt(c,76,812,568,48,'C1 · 18:40–19:20',35,P.ink,true);
 txt(c,76,881,568,43,'标准40分钟 · ¥4',30,P.ink,true);
 txt(c,76,930,568,40,'当前未扣费',28,P.ink);
 card(c,40,1012,640,128,'#E5E7DF');
 txt(c,70,1034,580,81,'旧预约WL-1008-026已取消\n旧码4261已失效，请使用新码。',28,P.muted);
 button(c,1180,'复制取用码 5372');
 txt(c,40,1291,640,42,'现场输入5372；请勿提前启动。',28,P.muted);
 foot(c);
 save('case-06',c,{title:'新的预约，新的开始码',audience:'选择替代洗衣时段后需要保存新凭证的宿舍住户',use_context:'2026-10-08 18:30手机预约成功页，720×1440按360逻辑像素2倍设计',user_goal:'保存5372，核对新C1订单/时段与未扣费状态，知道18:40到现场才能开始',visual_intent:'巨大高对比新码形成记忆锚，时段薄荷卡与灰色旧码告知分离，减少误用旧凭证',completion_criteria:['WL-1008-027/5372/C1新预约准确','18:40–19:20标准40分4元与未扣费状态一致','WL-1008-026与4261失效清楚','现场确认付款开始和禁止提前启动提示完整','复制操作解释明确，正文≥28px/按钮88px'],journey_state:'recovery-confirmed',current_time:'2026-10-08T18:30:00+08:00',actions:{copy_code:{label:'复制取用码 5372',effect:'把本次新码5372复制到剪贴板，复制成功反馈由实际产品实现；静态画面显示复制前状态'},arrival:{next_case:'case-07',precondition:'18:40抵达北院1层，现场输入5372并核验'}},credential:{current_code:'5372',current_order:'WL-1008-027',invalid_code:'4261',invalid_order:'WL-1008-026'},money_state:{charged_cny:0,pay_at_start_cny:4}});
}
// 07: large shared-room machine touchscreen, credential already checked.
{
 const c=new Canvas(1600,1100,{background:P.bg});
 logo(c,81,65);txt(c,126,39,650,50,'洗序 · 现场启动',34,P.ink,true);txt(c,1060,49,475,39,'2026.10.08  18:40',27,P.muted);
 txt(c,64,126,1472,80,'核对这一轮，然后开始',56,P.ink,true);
 txt(c,64,221,1472,50,'取用码5372已核验 · 北院1层洗衣房',30,P.muted);
 card(c,64,307,594,576,P.ink);
 txt(c,100,329,247,96,'C1',77,P.mint,true);c.circle(495,373,10,P.mint);txt(c,518,350,128,47,'待开始',28,P.mint,true);
 c.rect(105,442,508,24,'#415861',{radius:8});c.rect(119,448,148,11,'#7A9296',{radius:5});c.circle(581,454,5,P.mint);
 c.circle(360,668,171,'#274650',{border:'12 SOLID #526F76'});c.circle(360,668,142,'#D2E8E1',{border:'5 SOLID #92B8AF'});c.circle(360,668,126,'#739B9A');
 c.polyline([[247,694],[270,674],[298,689],[326,670],[354,685],[382,670],[410,688],[438,675],[470,694]],'#C7EAE0',15,{roundCaps:true});
 c.polyline([[264,725],[286,707],[313,725],[340,707],[367,725],[396,707],[426,725],[451,709]],'#B6D6CE',10,{roundCaps:true});
 txt(c,100,845,521,39,'衣物已放入？请确认舱门关闭。',27,'#D3E4E4');
 card(c,720,307,816,491);
 txt(c,754,335,746,59,'C1 · 标准洗',42,P.ink,true);
 txt(c,754,415,746,74,'18:40–19:20',47,P.ink,true);
 txt(c,754,507,746,46,'本轮40分钟 · 预计19:20结束',30,P.muted);
 c.line(754,574,1501,574,P.line,2);
 txt(c,754,603,346,48,'确认后支付',30,P.muted);
 txt(c,1190,583,283,115,'¥4',85,P.ink,true);
 txt(c,754,697,746,48,'订单 WL-1008-027 · 当前未扣费',28,P.muted);
 c.card(720,841,816,111,P.teal,{radius:24});txt(c,750,867,755,66,'确认付款 ¥4 并开始',36,P.white,true);
 c.card(64,929,594,101,P.white,{radius:24,border:'2 SOLID '+P.line});txt(c,96,953,530,61,'返回，不扣费',33,P.ink,true);
 txt(c,748,982,758,54,'确认后机器启动，预计19:20结束。',27,P.muted);
 c.line(64,1046,1536,1046,P.line,1);txt(c,64,1063,1472,34,'静态概念原型 · 全部机器/状态/订单/费用均为演示',20,P.muted);
 save('case-07',c,{title:'在现场确认，才真正开始',audience:'已到达洗衣房并在现场输入新码的住户',use_context:'2026-10-08 18:40现场触屏1600×1100，近距阅读；新码5372已核验，无登录步骤',user_goal:'核对C1标准40分钟和预计结束时间，确认付4元并开始，或返回而不扣费',visual_intent:'左边清晰的机器门与状态形成现场对应，右边价格/周期/订单作最后核对，独立的大按钮将扣费与启动绑定',completion_criteria:['5372已核验明示','C1标准40分，18:40–19:20预计结束准确','WL-1008-027及当前未扣费明示','确认支付4元并开始与返回不扣费两种操作准确','没有多余登录或未解释装饰按钮，机器状态待开始'],journey_state:'kiosk-start-confirm',current_time:'2026-10-08T18:40:00+08:00',actions:{primary:{label:'确认付款 ¥4 并开始',effect:'支付本轮4元并启动C1标准40分钟，下一状态case-08为运行中',next_case:'case-08'},secondary:{label:'返回，不扣费',effect:'退出本次付款确认页面，尚未扣费或启动机器'}},machine_state:{machine:'C1',code_verified:'5372',order:'WL-1008-027',cycle:'标准洗',duration_minutes:40,expected_end:'19:20',door_note:'示意提示检查舱门；没有接入真实门传感器'},money_state:{charged_cny_before_confirm:0,charge_on_confirm_cny:4,charge_on_return_cny:0}});
}
fs.writeFileSync(path.join(DIR,'source-application-v001.json'),JSON.stringify({task_id:'B05',producer:'05-07',read_at:new Date().toISOString(),actual_task_sources:['source-evidence/read-000001/command-output.txt: TASK.md,AGENTS.md,task.json,run-config.json,inputs/README.md','product-plan-v001.json','ui.cjs'],shared_cache_reused:['shared-doc-000001-response.txt service guide','shared-doc-000004-readable.txt Snapshot/Container/Stack/Positioned/Transform/Text/Raw','shared-fonts-000001-readable.txt Inter,Noto Sans CJK SC','dsl.cjs/dsl-README.md'],new_http_requests:0,real_image_viewing:'pending root real renders and view'},null,2),{flag:'wx'});
console.log(JSON.stringify({generated:['case-05','case-06','case-07'],directory:DIR}));
