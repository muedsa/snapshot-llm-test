'use strict';
const fs=require('fs'),path=require('path');const s=require('../../_suite/suite.cjs');
const dirs=s.taskDirs('A04'),notes=JSON.parse(fs.readFileSync(path.join(dirs.temp,'producer-notes-v001.json'),'utf8')),a=JSON.parse(fs.readFileSync(path.join(dirs.output,'analysis.json'),'utf8')),info=s.countsFor('A04'),state=s.readState(),task=state.tasks.find(t=>t.id==='A04');
if(!notes.producer_complete)throw new Error('No completed producer evidence');
const evidenceFiles=fs.readdirSync(__dirname).filter(f=>/^final-check-\d+\.json$/.test(f)).sort(),evidenceFile=path.join(__dirname,evidenceFiles.at(-1)),evidence=JSON.parse(fs.readFileSync(evidenceFile,'utf8'));if(!evidence.passed)throw new Error('Independent checks have not passed');
const link=(name,file)=>`[${name}](${path.relative(dirs.output,file).replace(/\\/g,'/').split('/').map(encodeURIComponent).join('/')})`;
const shared=path.join(s.createSuite().tempSuite),request=info.requests.find(r=>r.id===notes.request_id),time=new Date().toISOString();
const report=`# A04 · 分组改善与总体下降的数据解释

运行 ID：20261002-204314-6f31。报告时间：${time}。状态：最终作品与分析已交付，生产者完成实际图片自检；主执行者随后追加最终复审和结束计时。

输出目录：${dirs.output}。临时目录：${dirs.temp}。本题使用总配置的 https://open-snapshot.muedsa.com；全部主体由 Snapshot DSL 构造，无外部素材或 Image 嵌入。

## 产物与可核验结论

|文件|内容及结果|
|---|---|
|${link('conversion-story.png',notes.accepted_final.image_path)} / ${link('conversion-story.snapshot',notes.accepted_final.dsl_path)}|真实原始服务 PNG，1600×1000；同名完整自包含 DSL|
|${link('analysis.json',path.join(dirs.output,'analysis.json'))}|4 原始行、精确分数、访问权重、显示率、加权公式、变化、结论依据、几何与真实服务/查看映射|
|${link('task-metrics.json',path.join(dirs.output,'task-metrics.json'))}|任务计时、请求/版本/看图/迭代、实测文件资源与未知消耗；主执行者结束任务后更新|

任务数据是唯一业务输入。直接访问为前期2400/8000=3/10=30%，后期700/2000=7/20=35%；推广访问为200/2000=1/10=10%，后期960/8000=3/25=12%。两组分别改善5、2个百分点，而总体为2600/10000=13/50=26%，后期1660/10000=83/500=16.6%，下降9.4个百分点。

前期访问权重80%/20%，后期20%/80%。总体严格采用总成交/总访问，并展示等价恒等式：80%×30%+20%×10%=26%；20%×35%+80%×12%=16.6%。推广访问的分组率较低而后期权重较高，因此分组与总体方向相反；图中明确写“不能由该数据证明因果”，不推断构成改变的原因或渠道因果效果。

分组与总体率条共用0–100%尺度和508px有效轴宽；四分组条长度152.4、177.8、50.8、60.96px，总体132.08、84.328px。两期访问构成条均530px，真实分段424/106与106/424px。原始四行计数和期名/渠道均列于22px表格；正文22px以上，图注最低18px。证据图表和小表先呈现，结论与限制随后出现。

报告核验者已把最终 analysis 与原 CSV、独立 Node 算术及另一执行者的 PowerShell审查交叉比较，并把率条/构成几何匹配到实际提交 DSL；${link('独立最终检查',evidenceFile)}保留结果。此文件检查不代替视觉判断。最终 PNG 为${evidence.image_bytes} bytes，SHA-256 ${evidence.image_sha256}；与保留原响应逐字节相同，最终 DSL 与实际请求体逐字节相同。

## 实际文档与能力应用

这些资料是已真实取得并实际阅读的共享缓存；A04复用它们，新增文档/字体 HTTP请求为0，不在本题重复累计共享请求。

|实际来源|本题应用|
|---|---|
|${link('guide / shared-doc-000001',path.join(shared,'shared-doc-000001-response.txt'))}，https://open-snapshot.muedsa.com/ai-guide.md|UTF-8纯文本POST /snapshot；实际核对200、image/png及PNG签名，保留服务原字节；未用errorImage|
|${link('parser-tags / shared-doc-000004',path.join(shared,'shared-doc-000004-readable.txt'))}，https://snapshot.muedsa.com/reference/parser-tags/|Snapshot、固定根Container、Stack/Positioned、颜色/圆角/边框、Text/Raw CDATA、Transform网格线；未臆造属性|
|${link('parser / shared-doc-000003',path.join(shared,'shared-doc-000003-readable.txt'))} 与 ${link('layout / shared-doc-000005',path.join(shared,'shared-doc-000005-readable.txt'))}|报告核验者确认标签大小写、单根、有限布局约束与布局/绘制裁剪区别；核对最终几何结构|
|${link('fonts / shared-fonts-000001',path.join(shared,'shared-fonts-000001-response.txt'))}|真实字体列表包括Inter、Noto Sans CJK SC；最终DSL采用Inter,Noto Sans CJK SC，无字体名称空格误写|

直接访问用青绿色、推广访问用橙色，贯穿分组率和访问构成；总体用中性深蓝，期别用行位置与文本区分。四面板分别承载分组率、访问构成、总体率和原始计数，使同渠道编码保持稳定。

## 真实请求、看图与迭代

截至本报告：${info.counts.snapshot_requests}次渲染、${info.counts.successful_snapshot_requests}成功、${info.counts.failed_snapshot_requests}失败、${info.counts.retry_requests}重试、${info.counts.dsl_versions}个DSL版本、${info.counts.image_views}次已登记真实查看、${info.counts.completed_visual_iterations}次完整视觉迭代、${info.counts.incomplete_visual_iterations}次未完视觉迭代。初次生成与查看为基线，最终路径再次查看不被算作改进迭代。

请求${request.id}，版本${notes.version_id}；${request.started_at}至${request.ended_at}，${request.duration_seconds.toFixed(6)}秒；HTTP ${request.http_status}，${request.content_type}。服务requestId ${request.request_id}；Server-Timing为“${request.server_timing}”。${link('请求记录',path.join(dirs.temp,'requests.jsonl'))}、${link('版本记录',path.join(dirs.temp,'versions.jsonl'))}、${link('迭代记录',path.join(dirs.temp,'iterations.jsonl'))}及${link('查看记录',path.join(dirs.temp,'views.jsonl'))}均保留。

生产者${notes.baseline_view_id}在${info.views.find(v=>v.id===notes.baseline_view_id).viewed_at}实际打开1600×1000原尺寸基线，看到30/35和10/12、两条等长构成、26/16.6总体、原始分子分母及加权公式完整；无文字碰撞、截字或漏项。${notes.final_view_id}在${info.views.find(v=>v.id===notes.final_view_id).viewed_at}再次实际打开输出目录final PNG，确认标题、表格、底部因果限制未裁切，结果与基线一致。详细观察来自生产者实际查看记录，报告作者没有冒称自己执行该查看。

生产者未发现需要修复的实际缺陷，故保留一次合格基线，未制造修改或视觉迭代；本题无已确认服务错误、语法修复、重试或方案失败。生成脚本、初稿DSL、原响应、分析初版、最终版本、独立核验和完整日志均保留。主执行者随后进行额外真实复审，其查看与最终统计另追加记录。

## 消耗、限制与恢复

任务起点${task.started_at}；结束时间由主执行者taskEnd锁定，当前报告不预填结束。已记录请求耗时合计${request.duration_seconds.toFixed(6)}秒，与总墙钟分开；服务端render ${request.server_timing}只代表服务观测，不代替任务耗时。未发生用户等待或限流重试；服务器排队时间不可测为null。

实测渲染响应${info.resources.render_response_bytes} bytes，交付原PNG ${info.resources.delivered_final_png_bytes} bytes，归档DSL版本${info.resources.archived_dsl_version_bytes} bytes；这些是实际文件大小，不是计费代理。平台未提供实际token、图像输入或费用数据，结构化记录为null，不能据字数、字符数、文件大小估造。

生产者未记录未解决事项；尚待主执行者追加最终复审/状态关闭。任务输入与templates未改写，所有版本与过程保留，同一run_id继续后续任务。数据限制仅支持加权描述，不能证明因果。
`;
const f=s.report('A04',report);fs.writeFileSync(path.join(__dirname,'report-v001.md'),report,{flag:'wx'});console.log(JSON.stringify({report:f,producer_counts:info.counts,independent_checks:evidenceFile,local_links:s.inspectLinks(f)}));
