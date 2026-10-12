'use strict';
const fs=require('node:fs'),path=require('node:path');
const s=require('../_suite/suite.cjs'),d=s.taskDirs('A06');
const meta=path.join(d.temp,'requests/A06-request-000002/render-result.json');
const r=JSON.parse(fs.readFileSync(meta,'utf8'));
const before=fs.readFileSync(path.join(d.temp,'views.jsonl'),'utf8').trim().split('\n').map(JSON.parse).find(v=>v.version_id==='A06-v001'&&v.actor==='graph_producer');
const view=s.view('A06',r.image_path,{tool:'view_image',version_id:'A06-v002',actor:'graph_producer',observation:'Actual final full image: all 14 ID/label pairs complete; 16 teal solid edges have distinct arrowheads on future layers, including direct left bypass N04→N13 and skipped-layer N03→N06. Two orange dashed tracks independently originate at N09/N10 and return to two right-side ports of N08, with explicit F1/F2 explanations. Rank labels 02 and 09 are now clear left of bypass; node/annotation/footer text has no clipping. Parallel branches visibly merge at N08; no extraneous connection dots.'});
s.iteration('A06',{type:'visual',version_id:'A06-v002',parent_version:'A06-v001',completed:true,image_path:r.image_path,before_view_id:before.id,after_view_id:view.id,changes:'Shift rank labels left from x468 to x412 to avoid the N04→N13 horizontal bypass legs.',comparison:'Compared with actual v001 image, labels 02 and 09 are no longer struck through; node geometry, all solid/feedback endpoints and full text remain unchanged and clear.'});
const final=s.acceptFinal('A06','dependency-map',meta,{title:'从需求到可复现交付',visual_review_evidence:[view.id],content_counts:{nodes:14,solid_edges:16,feedback_edges:2}});
fs.copyFileSync(path.join(d.temp,'graph-audit-v002.json'),path.join(d.output,'graph-audit.json'),fs.constants.COPYFILE_EXCL);
const report=`# A06 · 十四节点依赖图与反馈回路

本题作品已制作并由生产者实际视觉审查，等待根代理独立审查与关闭状态。运行编号为 20261002-204314-6f31；输出位于本报告所在目录，全部尝试在 [临时目录](${d.temp.replaceAll('\\','/')}) 保留。

## 交付与数据核验

- [dependency-map.png](dependency-map.png) 与 [完整 DSL](dependency-map.snapshot)：真实服务 PNG 原始字节，1600×1000，未后处理。
- [graph-audit.json](graph-audit.json)：输入全部14节点、16先决边、2反馈边逐项列出；附各节点入/出邻居、0–10拓扑层、全部边路由及两条最长先决路径。
- 最长路径按节点数为11。例如 N01 → N02 → N05 → N06 → N08 → N09 → N10 → N11 → N12 → N13 → N14。另一个等长解经 N04、N07；反馈不参与排序或路径长度计算。
- 输入唯一来源为任务提供的 inputs/graph.json。程序以先决邻居计算拓扑层与动态规划最长路径，反馈单独保存；未制造依赖。

## 设计与实际看图

采用自上而下的11层，68px层间节距。14节点的编号23px、标签24px；全部注释至少18px。白色并行准备节点汇合为浅青色构建/检查链。每条先决边以实线箭头终止在后继节点边界，所有先决路由的y坐标不递减；N03→N06绕开内容规划，N04→N13沿左侧独立通道直接进入产物校验。反馈分别用右侧x1384与x1450的橙色虚线通道返回N08，并解释“失败后回到构建”“检查发现问题后修复”。图例明确交叉线无连接点，不构成新依赖。

已用真实 view_image 打开基线及最终服务图片。基线 ${before.id} 检查发现N04→N13首尾横段穿过层号02/09；v002把全部层号从x468移至x412。最终 ${view.id} 比较确认02/09完整、所有节点文字无裁切、18箭头及两个反馈目标清楚。生产者审查未发现其他剩余问题，根代理还将独立看最终图。

## 文档与工具实际应用

完整读取本题TASK.md、AGENTS.md、task.json、run-config.json及graph.json，并读取总run-config。实际复用并阅读共享真实缓存的服务指南 shared-doc-000001-response.txt、注册标签参考 shared-doc-000004-readable.txt 和 dsl-README.md；无重复HTTP文档请求。采用UTF-8纯文本POST /snapshot、真PNG响应检查及已查证的Inter/Noto Sans CJK SC字体。主体全部由Snapshot的Container、Stack、Positioned、Text/Raw、Transform生成；箭头与虚线为DSL几何，未使用外部素材或Image整图嵌入。

Node程序用于图计算、位置与路由、生成完整DSL；真实服务负责渲染，view_image负责实际视觉审查。所有脚本、DSL版本、原始响应、headers、请求与查看/迭代日志保存在临时目录。输入未改写。v001脚本输出了过大的结果摘要（含响应字节数组），v002改为仅打印小结果元数据；不影响原始图片/日志留存，也未把此记录计为渲染失败。

## 实际消耗与未解决项

两次真实渲染均HTTP200；2个DSL版本，2次生产者实际看图，1次完整视觉迭代，0语法修复/重试/渲染失败。无固定迭代上限；本次最终审查未发现继续修改的视觉问题。真实响应Server-Timing与请求耗时见 [task-metrics.json](task-metrics.json) 及临时requests.jsonl；总墙钟与服务请求时长分开。平台未提供本题模型token、图像输入或账单费用，均保留null，未按字符或请求数推算。

待根代理独立审查最终图片与文件后更新题级completed。\n`;
s.report('A06',report);
const m=s.writeTaskMetrics('A06',{validation:{producer_visual_review_passed:true,root_visual_review_pending:true,node_count:14,solid_edge_count:16,feedback_edge_count:2,topological_layer_count:11,longest_prerequisite_path_nodes:11,no_prerequisite_edges_backwards:true,final_version:'A06-v002',producer_views:[before.id,view.id]}});
console.log(JSON.stringify({final,view_id:view.id,metrics_counts:m.counts,resources:m.resources},null,2));
