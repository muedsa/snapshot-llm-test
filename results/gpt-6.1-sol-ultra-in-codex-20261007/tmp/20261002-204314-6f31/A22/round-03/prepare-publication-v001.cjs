const fs=require('node:fs'),path=require('node:path'),rd=__dirname,d=path.dirname(rd),save=(f,t)=>fs.writeFileSync(path.join(rd,f),t,{flag:'wx'});
const report=`# A22 第三轮 · 七个月汇总与密度回归

第二轮全部归档后才实际读取第三轮，未来文件可提前访问，预置连续执行/nonblind。新增2026-10原行：orders640/gross224000/refund11200/cost142000/sessions5900；第二轮8月refund25048和9月cost208000继续，前六个月原字段/派生结果完整保持。

七个月四KPI为净收入1121424、利润252924、订单3685、总体转化率3685/33200=11.10%；总收入1199050、退款77626、经营成本868500，总退款率6.47%。10月净212800、利润70800、退款率5.00%、转化率10.85%，10月净/利润均为七个月最高，9月利润−5632保持为负。标题/时间区间/期间说明/KPI/7组14柱/7行35单元/结论均更新到2026-10；没有省略2026-04或恢复旧财务值。

画布1600×1000与主区域边界0px移动，字体族/字号/主配色保持，正文最小22px。plot保持[156,452,670,272]、−50000至250000共享轴和零y678.6667，全部14柱均分7组，每柱对应实际值/300000×272；9月负柱继续向下。表头44px、七行各40px，原表内完成，表正文23px/cell34px。真实5个不变区域177170像素与第二轮0差：图表标题/图例、图表口径、左轴刻度、表头、公式页脚。完整数值/map/变化传播及像素证据见[计算](computed-data.json)、[布局](layout-map.json)、[变更审计](change-audit.json)、[独立审查](round-audit.json)。

真实2次200 PNG，3次root查看（第一幅整图、290×340原像素crop、修正版整图），1requirement-change+1完整视觉迭代，0服务失败/重试。初图7组金额粗体22/92px造成9月202368末8裁切，月份贴近；真实看局部后将14金额保持22/family/color但bold→regular适配，七原月份22/height29在y735/756交错两行。重新真实生成并看全幅，所有金额/日期完整，无裁切/碰撞；shape/data/bar/axis/table没有因这次视觉修正变化。21处实际Text调整与两原图/完整DSL/命令/脚本/QA/查看记录全部留存，旧轮未覆盖。

纯DSL无外部图像，复用真实共享guide/parser/font缓存，新文档HTTP0；Node精算/字符串构造，Python/Pillow/NumPy只读QA/原像素回归。真实token/图像输入/费用未知null，真实边界墙钟与请求耗时另列，不推估活跃CPU或未测平台间隔。三轮最终图均实际看过，本轮归档后整题总核；无未解决内容/数据/视觉问题。
`;
save('report-round-v001.md',report);
fs.writeFileSync(path.join(d,'report-cumulative-round03-v001.md'),`# A22 · 真实数据更正与局部回归

三轮全部内容与最终原PNG实际制作/查看完成，正在第三轮归档与整题审查。预置连续/nonblind，各前轮归档后才读下一轮，旧轮保持不可覆盖。

[第一轮](round-01/snapshot-usage.md) · [第二轮](round-02/snapshot-usage.md) · [第三轮](round-03/snapshot-usage.md) · [题级指标](task-metrics.json)

首轮6月：918624/262124/3045/11.15%，共享0轴和六行原CSV，caption视觉修正1次。第二轮8月退款+10000/9月成本+70000：908624/182124/3045/11.15%，−5632下向负柱、原plot扩负轴，副词/比较基准真实修正2次，六未改区域528172原像素0差。第三轮加10月且两更正保持：1121424/252924/3685/11.10%，14柱/35表单元，七个月全覆盖，标签裁切/月份贴近真实修正1次，五不变区域177170原像素0差。全三轮画布/主区域0px移，主字体/字号/配色保持，正文>=22；所有原始值及率分数精确，结论仅基于输入。

题级真实7render均200、7DSL、9root查看、1baseline+2requirement-change+4完整visual，0服务失败/重试。初图和最终图、所有脚本/参数/计算/maps/change审查、像素QA、命令/请求/响应/查看/变化证据及本地失败保留。Node生成器括号错误、默认START误判、审计器舍入累加容差误报、包装子进程EPERM各自如实更正/恢复，不计HTTP失败。共享官方文档/font缓存复用，无外部素材；未知token/图像输入/费用null。轮真实墙钟包括未单独测量的运行间隔，单列真实请求耗时，不当作活跃计算。全部轮指标独立归档并嵌入题级detail，套件只加题级顶层。最终状态以整题文件检查和root-close为准；现无未解决内容/视觉问题。
`,{flag:'wx'});
const manifest={finals:[{meta_path:'../requests/A22-request-000007/render-result.json',stem:'round-03/dashboard',title:'经营驾驶舱 · 第三轮七个月汇总',independent_case:false,details:{root_view_id:'A22-view-000009'}}],additional_files:[['computed-data-v001.json','computed-data.json'],['layout-map-v002.json','layout-map.json'],['change-audit-final-v001.json','change-audit.json'],['report-round-v001.md','snapshot-usage.md'],['independent-analysis/final-audit-v001.json','round-audit.json']].map(([source,f])=>({source,relative_output:'round-03/'+f})),report_from:'../report-cumulative-round03-v001.md',metrics_extra:{execution_mode:'preloaded_sequential',blind_feedback:false}};
save('publish-manifest-v001.json',JSON.stringify(manifest,null,2)+'\n');
