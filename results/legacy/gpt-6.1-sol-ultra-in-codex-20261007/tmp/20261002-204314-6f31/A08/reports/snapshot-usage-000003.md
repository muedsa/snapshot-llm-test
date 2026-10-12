# A08 · 网格导览与两条可走路线

Final status: completed. Root actual image review and required-file audit both passed. Earlier production-stage notes are superseded by this closing result.

指定导览作品与全部数据/过程已完成制作及实际视觉审查，沿用run 20261002-204314-6f31。root将追加独立最终审查和题级关闭记录；当前无未解决的数据、几何或视觉问题。

## 交付

- [wayfinding.png](wayfinding.png) 与 [wayfinding.snapshot](wayfinding.snapshot)：1560×1080真实服务原始PNG及完整同名DSL，最终A08-v002，未后处理。
- [paths.json](paths.json)：26×18原始网格、全部特殊格、两路完整零基格心序列/实际像素与米制格心、每段步数/距离、BFS最短核验、邻接和全域连通性检查。
- [task-metrics.json](task-metrics.json)：真实请求/版本/看图/迭代、时间与可得字节消耗；未知token/费用为null。
- [全部临时过程](D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/A08)：脚本、全部DSL/原响应/headers、局部QA图、请求/迭代/查看日志及独立分析资料均保留。

## 源数据与路径

实际读取floor.txt和legend.json，18行均26列，共468格：131墙、331个普通可走“.”及S/E/A/B/C/D各1，共337可走格。题面“A/A/B/D”与实际两个输入冲突，是展区字母笔误；按真实floor和legend使用A/B/C/D，未改写源文件。S(2,2)、E(23,15)、A材料实验(4,6)、B结构剧场(12,3)、C光影工坊(22,6)、D作品巡览(12,13)。所有格坐标从0开始、原点在左上；每格2米、只准四邻移动。

|路线/段|格间步数|米数|
|---|---:|---:|
|路线一 S→E 最短|34|68|
|路线二 S→B 最短段|13|26|
|路线二 B→D 最短段|10|20|
|路线二 D→E 最短段|13|26|
|路线二 S→B→D→E 合计|36|72|

程序自行BFS计算，选取的每段步数等于独立最短距离，并与另一审查者结果一致。路线一选取同长最短解，经D格到出口，但D不是路线一必须经过点。路线二先B后D；S→B通过(11,3)左邻进入，再B(12,3)向下至(12,4)，以另一同13步最短解避免同一边反向折返。完整每格站序保留，绝不把序列点数当步数：路线一35格心/34步，路线二37格心/36步。所有相邻坐标曼哈顿距离1、所有经过格非墙。

门洞完全按源网格：竖墙x8仅y4/y12开口，x17仅y7/y14开口；横墙y9仅x3/x12/x22开放。外围整圈仍为墙，S/E位于内部，没有扩大门洞或为入口/出口开边界。全域从S可达337格，与可走格总数一致。网格原始字符、计算检查和物理格心规则都见paths。

## 设计与实际视觉自检

每格40px，网格左上像素(66,200)。墙完整深色填充，开放格白底、可见完整边界；S/E及四区颜色与字母标识均在实际格。上下0–25横尺、左0–17纵尺全部18px，特殊标识21px，侧栏与正文最小22px。边缘尺足以定位任意格，路线不覆盖尺号。

路线一宽8px蓝实线，路线二窄4px橙虚线。两条中心线均严格使用同一格心坐标；重合段用蓝边及橙虚隙同时追踪，没有偏移成两条平行轨，也没有用粗白底扩大门洞。路线箭头都在相邻可走格的中心连线；S/E/展区标识清楚，不被箭头压住。侧栏独立列两路数量、各段和四区全名/坐标；底部尺度160px代表8米，单格40px代表2米。

生产者实际打开基线A08-view-000002发现橙色B小绕入分支虽有侧栏说明却缺少局部方向箭头。v002补(11,4)→(11,3)北向和B→(12,4)南向橙箭头，不改路线、墙或标识。实际完整再看A08-view-000006，并看B局部裁片A08-view-000007，确认两个方向可见、B文字无挡、蓝直达短线与橙绕行同时清楚。完整地图、门洞、所有标识/说明无裁切；真正原PNG保留，QA裁片只在临时目录供观察，不计最终作品。

## 文档、工具与实际消耗

完整阅读本题TASK/AGENTS/task.json/config、floor与legend；服务/DSL用此前真实取得并实际读过的共享指南、parser-tags及Canvas helper文档，缓存复用不计新HTTP。使用已确认Inter,Noto Sans CJK SC；UTF-8纯文本POST /snapshot，成功为真正PNG二进制。主体只由Snapshot Container/Stack/Positioned/Text/Raw/Transform圆/线几何构造；无外部素材、无栅格主体或SVG嵌入。

Node实际完成BFS、字符计数、四邻/连通检查、格心坐标与完整DSL生成。真实服务渲染，view_image完整与局部实际看图；Pillow仅制作有source/crop记录的QA裁片，不改最终响应。各次请求原字节/headers与所有脚本/失败记录保留，本题没有真实请求或语法失败，不虚造错误。

当前2次渲染均成功、2个DSL版本、1次完整视觉迭代、7次已登记真实看图（独立/root可能继续追加）、1张最终PNG。无语法修复/重试/限流等待。请求时长、Server-Timing与真实字节统计由指标提供，任务墙钟与请求耗时分开。平台未提供实际模型token、图像输入或账单，均null并说明原因；不按字符或图数估造费用。


## Root final review

A08-view-000010: Root actually opened1560×1080v002 and compared baseline: complete26×18 grid, all original walls and one-cell gates intact, zero-based x0–25/y0–17 rulers, fourA/B/C/D full names/coordinates plusS/E and accurate2m scale. Trace blue34-step route through x8,y4; x12,y9; x17,y14 gates toE. Orange36-step route detours from(11,4) north then east intoB before south toD; new orange up/down arrowheads visibly clarify branch without touching B label/walls. Shared routes have visible blue flanks and orange dashed gaps on same centers. All path distances/13+10+13 segments match independent facts, no diagonal/wall crossing, all text/legend within canvas.
