const fs=require('node:fs'),path=require('node:path'),s=require('../../_suite/suite.cjs');
const d=s.taskDirs('A22'),rd=__dirname,save=(f,text)=>fs.writeFileSync(path.join(rd,f),text,{flag:'wx'});
const report=`# A22 第一轮 · 六个月经营驾驶舱

1600×1000真实服务最终PNG与配对完整DSL已root实际查看，KPI、柱图、表格与结论核对通过。第一轮完成前未读取第二/第三轮；预置连续模式，未来文件可提前访问，不声称隐藏反馈盲测。

四KPI：净收入918624、经营利润262124、订单3045、总体转化率3045/27300=11.15%。净收入=收入−退款，利润=净收入−经营成本，退款率=退款/收入，转化率=订单/sessions。逐月和总计用整数计算，百分比用BigInt精确分数最终四舍五入两位；不平均月率，不造币种。月字符串2026-04至2026-09原样保留，正文最小22px。

两系列12根柱共用0–250000轴，步50000，所有柱顶与value/250000×272匹配；六行月份/净收入/利润/退款率/转化率表值准确。9月净收入202368/利润64368均期内最高；6月利润27914较5月41970下降33.49%，6月与8月退款率同为8%。均仅以本输入数值成立，无外部原因归因。

真实两次200渲染，首图root完整查看，再实际打开480×135图表局部，发现口径说明与最高刻度贴近；仅将caption x64→156,width744→670后重新渲染并root查看，数值/其余DSL保持。第二图说明与刻度水平分开，所有KPI/表/柱/结论无裁切重叠。3次真实root查看，1baseline+1完整视觉迭代，0渲染失败/重试。生产v001 Node有本地括号语法失败，在v002修复并保存证据；该失败发生于DSL/HTTP前，不计服务失败或DSL syntax-fix。

纯DSL Container/Stack/Positioned/Text/Raw/Transform，Inter/Noto Sans CJK SC实际共享字体缓存复用；已读真实guide/parser缓存，无新文档HTTP。使用spreadsheets技能的CSV原值/分母/总量核验约定，未生成工作簿。临时目录保留实际源脚本、参数、计算数据、原响应、两DSL、cropQA、查看/变化日志、失败与命令输出。精确计算与独立真实DSL审查见[审计](round-audit.json)，KPI/chart/table/title边界/样式/元素ID见[映射](layout-map.json)。真实token/图像输入/费用未知null，真实轮边界及请求耗时见[指标](task-metrics.json)。未解决事项无。
`;
save('report-round-v001.md',report);
const cumulative=`# A22 · 真实数据更正与局部回归

第一轮实际制作和root查看完成，正在归档；第二/第三轮尚未读取。预置连续模式，前轮真实归档后再读下一轮，未来文件可提前访问，不声称隐藏反馈盲测。

[第一轮](round-01/snapshot-usage.md) · [题级指标](task-metrics.json)

首轮四KPI与六个月净收入/利润/两率表及12根共享0轴柱图对应原monthly.csv。root实际两原PNG及真实局部检查完成，1视觉迭代修正caption与最高刻度贴近，其余数据/内容保持。两200渲染、三root查看；本地生成器括号错误保留且在HTTP前修复，无服务失败。每轮实际指标独立归档，题级只累计顶层，后续继续真实读取更正、计算、修改、生成、查看和局部回归。纯DSL无外部素材；未知token/图像输入/费用null。当前全题in_progress，不冒称三轮完成。
`;
fs.writeFileSync(path.join(d.temp,'report-cumulative-round01-v001.md'),cumulative,{flag:'wx'});
const manifest={finals:[{meta_path:'../requests/A22-request-000002/render-result.json',stem:'round-01/dashboard',title:'经营驾驶舱 · 第一轮',independent_case:false,details:{root_view_id:'A22-view-000003'}}],additional_files:[['production/computed-data-v001.json','computed-data.json'],['production/layout-map-v002.json','layout-map.json'],['report-round-v001.md','snapshot-usage.md'],['independent-analysis/final-audit-v001.json','round-audit.json']].map(([source,f])=>({source,relative_output:'round-01/'+f})),report_from:'../report-cumulative-round01-v001.md',metrics_extra:{execution_mode:'preloaded_sequential',blind_feedback:false,body_min_font:22}};
save('publish-manifest-v001.json',JSON.stringify(manifest,null,2)+'\n');
