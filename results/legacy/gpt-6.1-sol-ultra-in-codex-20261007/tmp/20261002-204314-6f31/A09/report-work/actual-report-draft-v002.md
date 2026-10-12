# A09 实际使用报告草案（root最终审计/归档前）

运行20261002-204314-6f31；本文件是tmp报告草案，不是完成状态。1600×1200候选A09-v001已真实渲染并由root和独立审查者实际完整看图，视觉基线合格。geometry-audit-v001的独立数字/像素±1.5px核验正在等待审计，root将完成后发布最终图/DSL/geometry-audit及刷新指标。

唯一真实渲染请求A09-request-000001，HTTP200 image/png，原始响应163169字节，2026-10-03T17:48:35.079Z→2026-10-03T17:48:40.156Z，耗时5.0769241秒；真实Server-Timing原值render;dur=2209.9, total;dur=2374.4。本时点1次成功、0失败、0重试、1DSL版本，未制造视觉修改（真实图合格）。实际查看总数以views.jsonl和最终task-metrics读取，独立full事件A09-view-000002。

设计为4×3卡，每卡300×250、间隙32，总网格1296×814居中(800,600)。每卡用原始120×120透明印章完整子树和Transform.matrix final组合绘制，3矩形/黑圆原局部坐标不改。列表操作后乘顺序按列向量后操作左乘，图像y向下顺时针；每步绕(60,60)，父Positioned仅放网格，不重复origin/center变换。真实DSL核验原stamp子树恰好复用12次，全部文字fontSize≥20，独立标签/刻度无裁切。

独立实际完整图A09-view-000002：顺时针四角/左右上下镜像正确，T07先左右镜像再90°与T08先90°再左右镜像明显不同，black dot相对中心(+11,-31)/(-11,+31)；T10非等比让圆点变成20×12横椭圆；T09等比缩小、T11/T12斜边/黑点完整。没有真实视觉问题，不为了迭代次数改图。

geometry-audit-v001列每样本实际DSL列主序4×4、本地/全局矩阵、父布局offset、原矩形四角与最终corners、dot中心/ellipse bounds、最终bbox，及像素中心坐标和反走样例外的方法。当前pixel_check为pending actual service PNG，最终报告不得提前写像素审计通过；root须待真实独立审计更新后引用实际结果。

实际复用shared-request-000002官方Transform页 https://snapshot.muedsa.com/widgets/layout/transform/：矩阵仅影响绘制不重布局、祖先clip影响变换溢出、origin/alignment不能重复已含pivot平移。本题无新增文档/fonts请求；UTF-8纯文本POST、原始PNG二进制、字体Inter,Noto Sans CJK SC来自shared真实指南/parser/fonts缓存。

输出使用outputs/20261002-204314-6f31/A09、临时tmp/20261002-204314-6f31/A09；所有脚本/DSL/真实响应/审计/看图记录保留。未知实际token/图像输入计费/费用为null，不能以字数或截图数量推算。

独立事实文件report-work/independent-review-v001.json；数值审计由independent-analysis负责，本草案不写最终报告/状态/指标，也不替代root最终归档/关闭检查。
