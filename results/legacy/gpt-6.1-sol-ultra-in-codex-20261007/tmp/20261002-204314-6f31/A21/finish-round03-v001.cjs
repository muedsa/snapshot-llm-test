const fs=require('node:fs'),path=require('node:path'),s=require('../_suite/suite.cjs');
const d=s.taskDirs('A21').temp,r=path.join(d,'round-03');
const contrast=JSON.parse(fs.readFileSync(path.join(r,'contrast-production/contrast-audit-v001.json'),'utf8'));
if(!contrast.hard_constraints_pass||contrast.images.length!==2)throw Error('Contrast failure');
for(const im of contrast.images){if(im.texts.length!==10||s.sha256(fs.readFileSync(im.image_path))!==im.PNG_sha256||s.sha256(fs.readFileSync(im.source_DSL_path))!==im.source_DSL_sha256)throw Error('Contrast evidence mismatch');}
const report=`# A21 第三轮 · 浅色主题与完整可读性

本轮两张真实服务PNG已实际查看，第三轮全部内容、几何、回归与对比度专项审查通过。预置连续执行，第二轮完成并归档后才读取第三轮；未来需求可提前访问，不声称隐藏反馈盲测。

浅色渐变背景为#F7FAF6→#E8F0EA，文字使用不透明#1D3435/#215E52/#42585B。保留第二轮全部九项文案，新增24px“Clarity through structure”于网址上方。中文48px两行，未变形；两图十项正文无重叠/裁切，赞助完整保留。四个−18°圆角光片及原渐变完全保留其DSL/几何，浅底改变抗锯齿背景，因此不要求第三轮整光片PNG与暗底相同。

root实际查看A21-view-000005/000006，原图分别1080×1350/1440×810。独立内容/几何审查0issues；前两轮18个正式文件哈希保持。对比度核20Text/200处原PNG背景样本，整Text框保守最差6.5456167376:1，全部普通文字均≥4.5。正确sRGB线性化，背景按渐变等投影格移到空白边缘直接取实际PNG，不仅估算端点，排除前景污染；详见[对比度证据](contrast-audit.json)及[独立审查](round-audit.json)。

本轮2次真实200 PNG渲染、2次root原图查看、2次requirement-change，0视觉迭代/失败/重试。首版实际合格，无需人为修改。无外部图片，纯DSL；复用已读真实服务指南/parser/font缓存，新增文档HTTP0。所有原始请求/响应、DSL、脚本、查看/变化日志及对比度像素证据保留于临时目录。真实token/图像输入/费用平台未提供，null；轮次真实时间及请求耗时另见[指标](task-metrics.json)。未解决事项无。
`;
fs.writeFileSync(path.join(r,'report-round-v001.md'),report,{flag:'wx'});
const cumulative=`# A21 · 真实需求变更：双尺寸发布物

三轮6张原PNG/完整DSL及独立审查已实际完成，正在完成第三轮归档与整题文件核验。预置需求连续执行，前轮归档后才读取下一轮；未来需求可提前访问，不声称隐藏反馈盲测。

[第一轮](round-01/snapshot-usage.md) · [第二轮](round-02/snapshot-usage.md) · [第三轮](round-03/snapshot-usage.md) · [题级指标](task-metrics.json)

第一轮分别构图1080×1350与1440×810，建立四光片/主青品牌，预留顶部与底部真实空间。第二轮替换48px两行长标题、加入赞助及免费字段，保持活动内容与主色，原光片区域423108像素与第一轮0差。第三轮切换浅色主题，保留全部第二轮文案，新增24px英语位于网址上方，20项文本对真实PNG背景最差对比度6.5456:1，超过4.5。四光片source/几何/渐变保持。前两轮18个正式文件保持原哈希。

真实6次render均200，2baseline+4requirement-change，6次root原图查看，0完整视觉迭代/HTTP失败/重试。每轮首版实际合格，未制造改动。纯DSL无外部素材，真实共享guide/parser/font缓存复用，不重复计HTTP。全部请求原字节、版本、查看/比较、脚本/数据/独立审查保留于统一临时目录；轮报告、token/map/指标完整归档。真实token/图像输入/费用未知为null，墙钟和请求耗时分开统计。最终状态以整题关闭及指标为准；当前没有未解决内容或视觉问题。
`;
fs.writeFileSync(path.join(d,'report-cumulative-round03-v001.md'),cumulative,{flag:'wx'});
const manifest={finals:[5,6].map((n,i)=>({meta_path:`../requests/A21-request-${String(n).padStart(6,'0')}/render-result.json`,stem:`round-03/launch-${i?'wide':'portrait'}`,title:`叠光发布 · 第三轮${i?'横屏':'竖海报'}`,independent_case:false,details:{root_view_id:`A21-view-${String(n).padStart(6,'0')}`}})),additional_files:[['design-tokens-final-v001.json','design-tokens.json'],['content-map-final-v001.json','content-map.json'],['report-round-v001.md','snapshot-usage.md'],['independent-analysis/round-audit-v001.json','round-audit.json'],['contrast-production/contrast-audit-v001.json','contrast-audit.json']].map(([source,f])=>({source,relative_output:`round-03/${f}`})),report_from:'../report-cumulative-round03-v001.md',metrics_extra:{execution_mode:'preloaded_sequential',blind_feedback:false,contrast_minimum:6.5456167376,contrast_text_regions:20}};
fs.writeFileSync(path.join(r,'publish-manifest-v001.json'),JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({contrast_validated:true,regions:contrast.images.map(i=>i.texts.length),manifest:path.join(r,'publish-manifest-v001.json')}));
