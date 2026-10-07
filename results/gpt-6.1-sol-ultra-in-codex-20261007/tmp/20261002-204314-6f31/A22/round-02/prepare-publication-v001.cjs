const fs=require('node:fs'),path=require('node:path'),rd=__dirname,d=path.dirname(rd),save=(f,t)=>fs.writeFileSync(path.join(rd,f),t,{flag:'wx'});
const report=`# A22 第二轮 · 财务更正与负利润回归

第一轮已完整归档后才实际读取第二轮要求；第三轮尚未读取。预置连续模式，未来需求可访问，不声称隐藏反馈盲测。最终1600×1000原PNG已root实际查看，数值/内容/负柱与区域回归通过。

原始更正只两项：2026-08退款15048→25048，2026-09经营成本138000→208000。其余原始值全保持。8月净收入173052→163052、利润41052→31052、退款率8.00%→13.32%；9月净收入202368保持、利润64368→−5632。总净918624→908624，总利润262124→182124；总订单3045、sessions27300、总体转化率11.15%保持。总退款66426、总成本726500、总收入975050，总退款率6.81%。每月净/利润/两率、总量/KPI、对应表单元/柱高/标题结论均传播。

原plot[156,452,670,272]内设统一−50000至250000轴，零线y678.6667，9月负利润5.1063px向零线下方绘制至y683.7730；负号标签完整，未裁掉/画成正柱，其他11柱/7刻度按同尺度重算。画布与全部主区域边界0px移动（要求±2px），主字体/字号/色/视觉系统保持。六个未改区域528172个真实原PNG RGBA像素与首轮0差：标题、订单/转化卡、表头/前四行、图表标题/图例、口径页脚。源字段/未改内容及实际对比见[变更审计](change-audit.json)，[计算](computed-data.json)与[布局](layout-map.json)留存完整。

真实3次200 PNG渲染，3次root完整图查看，1requirement-change+2完整视觉迭代，0失败/重试。先真实看财务修订图，删除结论不准确的“仍”（原轮9月最高，修后7月最高）；再根据实际已看文案与独立内容复核，将“净收入减少10000”明确为“净收入较更正前少10000”，避免误述8月环比（实际比7月+1932）。最终图实际完整查看，两结论清楚完整，图表/表格数据保持；req3→req5除两结论盒外全部像素0差。所有中间图/DSL/报告版本、脚本、命令输出、数值分数/像素回归、真实查看与变化证据保存，未覆首轮。

独立原值更正精算和真实最终DSL/负柱/内容/区域审查见[独立审计](round-audit.json)。纯DSL、无Image/外部素材；真实共享guide/parser/font缓存复用，新HTTP文档0。Node字符串构造/精算，Python/Pillow/NumPy只读实际原PNG回归，不修改final字节。真实token/图像输入/费用未知null；墙钟/请求耗时/等待分别见[本轮指标](task-metrics.json)，墙钟含未单独测量的运行间隔，不作为活跃CPU时间。未解决事项无。
`;
save('report-round-v001.md',report);
fs.writeFileSync(path.join(d,'report-cumulative-round02-v001.md'),`# A22 · 真实数据更正与局部回归

首轮完整归档，第二轮最终图/数值/负柱/区域回归已实际完成，正在归档；第三轮尚未读取。预置连续模式/nonblind，前轮归档后再读下一轮。

[第一轮](round-01/snapshot-usage.md) · [第二轮](round-02/snapshot-usage.md) · [题级指标](task-metrics.json)

首轮净918624/利润262124/订单3045/总体11.15%，两render/三view/一visual修复caption。第二轮仅8月refund+10000/9月cost+70000，净908624/利润182124，9月利润−5632实际下向负柱；原plot内扩负轴、主区域0px移动、六未变区域528172真实像素0差。第二轮三render/三view/一requirement-change/二visual修正结论副词和比较基准。共5render均200，6view，3visual；本地脚本/核验误报/包装子进程EPERM均保留并恢复，不计服务失败。两轮旧版/计算/map/change/报告/真实独立指标留存，未知消耗null，墙钟与请求耗时分开。全题in_progress，待第三轮实际执行并归档及整题审查。
`,{flag:'wx'});
const manifest={finals:[{meta_path:'../requests/A22-request-000005/render-result.json',stem:'round-02/dashboard',title:'经营驾驶舱 · 第二轮财务更正',independent_case:false,details:{root_view_id:'A22-view-000006'}}],additional_files:[['computed-data-v001.json','computed-data.json'],['layout-map-v003.json','layout-map.json'],['change-audit-final-v002.json','change-audit.json'],['report-round-v001.md','snapshot-usage.md'],['independent-analysis/final-audit-v001.json','round-audit.json']].map(([source,f])=>({source,relative_output:'round-02/'+f})),report_from:'../report-cumulative-round02-v001.md',metrics_extra:{execution_mode:'preloaded_sequential',blind_feedback:false}};
save('publish-manifest-v001.json',JSON.stringify(manifest,null,2)+'\n');
