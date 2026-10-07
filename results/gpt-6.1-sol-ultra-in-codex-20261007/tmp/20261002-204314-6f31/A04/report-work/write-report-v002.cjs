'use strict';
const fs=require('fs'),path=require('path');const s=require('../../_suite/suite.cjs');
const dirs=s.taskDirs('A04'),reportFile=path.join(dirs.output,'snapshot-usage.md'),info=s.countsFor('A04'),rootView=info.views.find(v=>v.id==='A04-view-000003'&&v.observer==='root');if(!rootView)throw new Error('Root review not yet recorded');
let report=fs.readFileSync(reportFile,'utf8');
report=report.replace(/报告时间：[^。]+。状态：[^\n]+/,'报告时间：'+new Date().toISOString()+'。状态：最终作品、分析、生产者自检和主执行者实际视觉复审均已通过；任务状态和最终计时由主执行者统一关闭。');
report=report.replace('2次已登记真实查看','3次已登记真实查看');
report=report.replace('主执行者随后进行额外真实复审，其查看与最终统计另追加记录。',`主执行者独立完整查看也已记录为${rootView.id}，时间${rootView.viewed_at}：四个分组率、530px等长构成、508px的0–100%轴、总体26/16.6、四原始行、两公式和页脚限制均正确可读。总计生产者2次加主执行者1次真实查看；主执行者结束任务时更新最终指标。`);
report=report.replace('生产者未记录未解决事项；尚待主执行者追加最终复审/状态关闭。','生产者与主执行者复审均未记录未解决事项；最终状态与结束时间由主执行者统一写入套件和指标。');
const output=s.report('A04',report);fs.writeFileSync(path.join(__dirname,'report-v002.md'),report,{flag:'wx'});console.log(JSON.stringify({report:output,views:info.counts.image_views,root_view_id:rootView.id,links:s.inspectLinks(output).issues}));
