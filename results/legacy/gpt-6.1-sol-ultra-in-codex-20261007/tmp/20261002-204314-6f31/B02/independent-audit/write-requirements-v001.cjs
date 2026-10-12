const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root='D:/workspaces/gpt-6.1-sol-ultra',run='20261002-204314-6f31',task='tasks/B02-one-client-ten-touchpoints/';
const sources=['AGENTS.md','TASKS.md','catalog.json','run-config.json',...['TASK.md','AGENTS.md','task.json','run-config.json','inputs/README.md','templates/portfolio-template.json','templates/task-metrics-template.json','templates/snapshot-usage-template.md'].map(x=>task+x),'tmp/'+run+'/B02/plan-v001.json','tmp/'+run+'/B02/project-system-v001.cjs'];
const plan=JSON.parse(fs.readFileSync(path.join(root,'tmp',run,'B02','plan-v001.json'),'utf8'));
const data={schema_version:1,task_id:'B02',run_id:run,reviewer:'b01_independent_audit',created_at:new Date().toISOString(),scope:'B02要求、项目运营基线和十触点审计准备；非作品通过声明',source_files:sources.map(file=>({file,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file))).digest('hex')})),requirements:[
 {id:'B02-R01',requirement:'同一项目构成至少10件独立完整视觉作品，每触点有实际动作、适合观看环境而非换色海报',basis:'TASK.md创作任务',checks:['十件服务目标不同','品牌/运营/视觉规则一致','不复用B01已交付成品计为新件','小字阅读环境如实限定']},
 {id:'B02-R02',requirement:'自拟项目像真实项目一样明确服务对象、运作方式与使用需求，虚构/演示内容如实声明',basis:'TASK.md创作任务；AGENTS.md自主选择与完整用例',checks:['再线/RETHREAD主体一致','开放日、开门时段、地址、收费、流程跨作品一致','静态预约/库存/参与反馈不假称真实服务']},
 {id:'B02-R03',requirement:'另交project-brief.md、design-system.json、touchpoint-map.json',basis:'TASK.md；task.json.additional_outputs',checks:['brief说明项目问题和解决机制','design-system只写实际使用的颜色/字号/标记/布局/规则及例外','map映射完整十件用户情境、行为和产物路径']},
 {id:'B02-R04',requirement:'每件final.png、final.snapshot、case.md；输出根portfolio.json/md、gallery.html、snapshot-usage.md、task-metrics.json',basis:'TASK.md交付；AGENTS.md输出目录',checks:['图/DSL由原服务响应配对且字节可核','所有主作品在本地画廊完整索引，链接有效','模板说明/空占位清除']},
 {id:'B02-R05',requirement:'完整自包含DSL经真实服务，主体DSL构成；每次成功图真实打开，终审整个生态和复用组件',basis:'AGENTS.md文档、DSL、服务；看图、迭代与最终审查',checks:['真实HTTP200原PNG/输入hash链','root每候选实际工具查看','跨密度/比例审查实际看图','审计脚本不能代替视觉终审']},
 {id:'B02-R06',requirement:'同run统一目录，草稿失败脚本与追加日志保留；未知消耗null，指标归属不重复',basis:'总AGENTS.md；AGENTS.md迭代、工具与消耗',checks:['requests/iterations/tool-usage真实记录','baseline/visual/syntax-fix/retry区分','每case时间与共享准备不重算','root更新公共state/logs，独立审计只写私有目录']}
],operation_baseline:plan.operation,operation_arithmetic:{event_weekday_confirmed:new Date('2026-10-24T12:00:00Z').getUTCDay()===6,booking_minutes:45,check_in_lead_minutes:10,pickup_after_session_minutes:15,opening_minutes_per_day:480,volunteer_first_minutes:225,volunteer_second_minutes:315,handover_overlap_minutes:15},case_checks:plan.cases.map(c=>({id:c.id,title:c.title,user_task:c.task,dimensions:c.size,checks:({
 'case-01':['名称/活动日期/地点/开放时段/参与办法清楚，费用为基础体验而非全损伤包价'],
 'case-02':['10:30–11:15为45min，10:20签到，¥30含基础材料，复杂损伤评估；静态不真预约'],
 'case-03':['签到台→评估→工位路线和空间映射一致，入口/出口/工具区可识别'],
 'case-04':['工具清单、数量/状态、归位轮廓和对应位置一致，能检查缺件'],
 'case-05':['条件分支能区分基础修补与先评估，无不明确死路、不会无条件承诺修复'],
 'case-06':['四步针法次序/几何/图例一致，材料与最后检查完整'],
 'case-07':['取件编号/对象/费用/时间/凭证一致，11:30在示例体验之后，养护适用性限定'],
 'case-08':['每织物材质/尺寸/瑕疵齐全，清洁与交换规则明确，demo库存声明'],
 'case-09':['月度数据分母/求和/比例与图形一致，演示反馈不充当真实成效或环保减排事实'],
 'case-10':['9:30–13:15/13:00–18:15，交接15min覆盖10–18开放，岗位人员无时间冲突，日期一致']
 })[c.id]})),limitations:['当前仅实际读取任务/计划/组件规则，尚未审计生产作品','所有服务和root查看证据到位后另存门禁','额外代理真实看图若发生写私有事件供root计入实际消耗']};
fs.mkdirSync(__dirname,{recursive:true});fs.writeFileSync(path.join(__dirname,'requirements-v001.json'),JSON.stringify(data,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({file:'requirements-v001.json',requirements:data.requirements.length,cases:data.case_checks.length,operation_arithmetic:data.operation_arithmetic}));
