const fs=require('fs');const path=require('path');const crypto=require('crypto');
const root='D:/workspaces/gpt-6.1-sol-ultra', run='20261002-204314-6f31';
const sourceFiles=['AGENTS.md','TASKS.md','catalog.json','run-config.json','tasks/B01-ten-real-world-showcases/TASK.md','tasks/B01-ten-real-world-showcases/AGENTS.md','tasks/B01-ten-real-world-showcases/task.json','tasks/B01-ten-real-world-showcases/run-config.json','tasks/B01-ten-real-world-showcases/inputs/README.md','tasks/B01-ten-real-world-showcases/templates/portfolio-template.json','tasks/B01-ten-real-world-showcases/templates/task-metrics-template.json','tasks/B01-ten-real-world-showcases/templates/snapshot-usage-template.md'];
const data={schema_version:1,task_id:'B01',run_id:run,audit_kind:'independent_requirement_review',created_at:new Date().toISOString(),reviewer:'b01_independent_audit',source_files:sourceFiles.map(file=>({file,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file))).digest('hex')})),requirements:[
 {id:'B01-R01',requirement:'至少10件独立完整作品，解决实质不同的实际使用任务和视觉想法',basis:'TASK.md创作任务；AGENTS.md自主选择与完整用例',checks:['逐案例实际受众、场景、用户目标明确','不能将同版换字/换色、缩放、裁切、放大或迭代计成独立件','内容足以帮助用户执行目标，不只是概念卡片']},
 {id:'B01-R02',requirement:'自拟品牌、数据允许，但必须标明演示/虚构，不宣称实际客户部署',basis:'TASK.md创作任务；AGENTS.md自主选择与完整用例',checks:['portfolio及case.md有内容性质说明','未核实统计、引语、背书不得标为事实','可用行动文案与图形/数据映射一致']},
 {id:'B01-R03',requirement:'最终作品由完整、自包含.snapshot通过真实Snapshot服务返回，主体排版/图形/信息由DSL构成，保留原PNG字节',basis:'AGENTS.md文档、DSL、服务与各种工具',checks:['PNG与DSL同名配对','最终PNG哈希等于对应服务响应','正确请求与成功响应可追溯','DSL不依赖任务外部文件或以整图Image替代主体']},
 {id:'B01-R04',requirement:'每张成功响应实际打开查看、按视觉反馈完善、完成整个作品集审查',basis:'AGENTS.md看图、迭代与最终审查',checks:['逐张root真实查看证据','baseline和visual分类准确','接触表不能代替原图查看','本独立脚本检查不能替代root视觉判断']},
 {id:'B01-R05',requirement:'每用例case-NN/final.png、final.snapshot、case.md；输出根portfolio.json/md、gallery.html、snapshot-usage.md、task-metrics.json',basis:'TASK.md交付；task.json',checks:['全部规定文件存在','portfolio逐件尺寸按PNG读取，来源、DSL能力、完成标准和检查证据齐全','gallery包含所有主作品且为相对本地链接、无远程脚本','模板说明字段及占位符已去除']},
 {id:'B01-R06',requirement:'保留计划、脚本、草稿、请求响应、失败及追加日志，不删除或覆盖历史',basis:'AGENTS.md输出目录、临时目录和复现',checks:['requests/iterations/tool-usage.jsonl有效','每事件归属case或shared','记录真实时间和过程、错误分类、版本父关系']},
 {id:'B01-R07',requirement:'消耗按真实平台指标，未知为null，墙钟与并行请求/案例耗时分开，共享请求不重复统计',basis:'AGENTS.md迭代、工具与消耗记录；总AGENTS.md',checks:['顶层和case_metrics对应','未测token/费用不猜算','实际等待0与未知队列null区分']},
 {id:'B01-R08',requirement:'沿用run_id和统一输出/临时目录，B01完成后继续B02，最终全套审查前不能标全套完成',basis:'总AGENTS.md',checks:['run_id一致','输出归属B01','不写题库','root控制suite-state与公共日志']}
],planned_case_checks:[
 {id:'case-01',task:'铁路出行确认',checks:['出发/到达跨日标注','检票时间早于发车且合理','站台及乘车步骤无歧义']},
 {id:'case-02',task:'展馆90分钟导览',checks:['路线连通且场次地点对应','顺序/步行/参观时间总量合理','入口/出口可辨']},
 {id:'case-03',task:'植物今日照护',checks:['明确优先检查对象','用观察条件决定动作，不能不看土况固定浇水','多植物状态及动作对应']},
 {id:'case-04',task:'咖啡点单',checks:['饮品完整名称/价格/规格','组合及加料价格算术正确','限制/可选项清楚']},
 {id:'case-05',task:'港口作业调度',checks:['时间/泊位/容量状态一致','各泊位或资源不冲突','作业顺序及下一步可判定']},
 {id:'case-06',task:'剧场选座',checks:['舞台方向/座位行列清晰','推荐相邻座真实连续且可选','状态图例与座位实际配色一致','入场早于开演']},
 {id:'case-07',task:'户外路线计划',checks:['分段距离总和匹配6.2km或最终总量','分段时间含停留总量匹配目标','补水点/停留点位置映射','虚构线路标记']},
 {id:'case-08',task:'两人份一锅意面',checks:['食材单位数量完整','4+9+2分钟或实际分段合计匹配总时间','步骤按顺序且完成标准可判断','自拟食谱/时间参考说明']},
 {id:'case-09',task:'骑行前60秒检查',checks:['四项15秒/实际分配和总时间一致','轮胎压力按胎侧范围，不能虚构通用数值','刹车/快拆或轴固定/传动检查可执行']},
 {id:'case-10',task:'90分钟学习计划',checks:['14:00-15:30合计90分钟','14:38已38/剩52','15+60+15阶段和时间边界一致','90刻度/进度几何与显示值一致','明确静态演示']}
],limitations:['目前无生产作品到位；此文件只核要求与预设审查点，不能作为作品完成证据','独立审计不负责渲染或更新公共日志/state','只有实际读取后才据最终DSL/数据/图片形成通过或失败结论']};
fs.mkdirSync(__dirname,{recursive:true});fs.writeFileSync(path.join(__dirname,'requirements-v001.json'),JSON.stringify(data,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({file:path.join(__dirname,'requirements-v001.json'),requirements:data.requirements.length,planned_cases:data.planned_case_checks.length}));
