# A09 · 十二个非对称图形变换标本

Final status: completed. Root actual image review and required-file audit both passed. Earlier production-stage notes are superseded by this closing result.

运行 20261002-204314-6f31。候选 A09-v001 已通过实际完整看图、独立矩阵核验和 ±1.5px 像素核验（允许并已实测的反走样边缘例外）。

## 交付与设计

transform-atlas.png 为服务原始 1600×1200 PNG，与 transform-atlas.snapshot 完整配对；geometry-audit.json 包含每套列主序4×4 local/global矩阵、实际DSL矩阵字面量、36矩形144四角、12圆点中心及椭圆轴、外接框和完整审查证据。4×3网格每格300×250，间32；总框1296×814从(152,193)起，居中(800,600)。所有标签≥20px，标题与图例位于格外。

原始120×120印章子树重复12次，不改原形坐标，不使用Image或外部素材。Transform.matrix 使用列向量、后操作左乘 M=op×previousM，每步绕局部(60,60)。屏幕y向下，顺时针矩阵为[[cos,-sin],[sin,cos]]。父Positioned仅加格位置；origin(0,0)，不再重复中心补偿。Stack clipBehavior NONE 保留T10/T11/T12越出原布局盒的完整绘制。

T07先左右镜像再顺时针90°，黑点相对中心(+11,-31)；T08顺序相反，点(-11,+31)，图像差异清楚。T10非等比缩放后圆点为20×12椭圆。

## 真实审查与边缘例外

Root实际全图查看 A09-view-000001；独立全图查看 A09-view-000002 与 A09-view-000003。12格内容、编号、刻度、黑点均完整无裁切，T07/T08顺序差异与30°斜边正确，未发现需视觉修改的问题。基线完成后未制造无意义迭代。

独立重新计算12组local/global矩阵和所有角点/圆点，误差小于1e-6，实际DSL的12个matrix字面量全部一致。真实PNG按色分割36矩形并核144角。圆点中心最大偏差0.098360px，整体主体外框最大偏差1.105118px；深内区错色及越多边形1.5px以外纯色像素均为0。

原始 pixel-review-v001.json 的 all_checks_pass=false 原样保留：T11金矩形纯色左界983，理论981.464102，偏差1.535898px。专项T11-gold-AA-exception-v001.json实测(981,863) RGB(251,240,215)，约20.38%金色覆盖，像素中心距理论角0.286865px；AA支持外框[981,839,1030,883]最大误差0.464102px，supported_bounds_pass与antialias_exception_confirmed均true。共15处AA角例外分列，未扩大1.5px容差，未改图或改原失败结论。最终按题目明确允许的已测AA边缘例外通过。

## 文档与工具应用

实际复用共享指南、parser、fonts及 shared-request-000002 官方Transform文档 https://snapshot.muedsa.com/widgets/layout/transform/ ：绘制变换不改变布局、祖先clip影响溢出、含pivot的矩阵不重复origin/alignment中心变换。Node计算/生成DSL；Python Pillow检查真实像素；view_image实际看图。新增HTTP只1次render，文档与fonts缓存复用不重复计请求。

## 请求、过程与消耗

A09-request-000001，2026-10-03T17:48:35.079Z→17:48:40.156Z，HTTP200 image/png，5.0769241秒，原始163169字节，requestId bbb51655-3dcc-4cd4-aedf-be2bb4231a52，Server-Timing render;dur=2209.9, total;dur=2374.4。1次成功、0失败、0重试、1DSL版本、0完整视觉迭代，实际3次看图；起止与墙钟以task-metrics.json为准。

输出 D:\workspaces\gpt-6.1-sol-ultra\outputs\20261002-204314-6f31\A09；临时 D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\A09。脚本、原DSL/请求/响应/headers、独立计算、原失败报告和AA专项、查看日志全部保留。实际token、图像输入用量、费用服务未提供，均null；文件字节不是计费估计。未解决事项无。


## Root final review

A09-view-000001: Root full1600×1200 actual baseline: all12 original asymmetric stamps centered on common cell centers,4×3 frames300×250 with32px gaps. CW90/180/270 and mirrors correct. T07 dotupper-right vsT08lower-left displays order difference; T10 horizontal ellipse and wider/shorter blocks; T11/T12 angled30deg marks intact unclipped.20px labels/ticks and outside title/legend readable, original red/blue/gold exact colors, no overlap or cutting. Await independent numeric/pixel check, no visual change needed.
