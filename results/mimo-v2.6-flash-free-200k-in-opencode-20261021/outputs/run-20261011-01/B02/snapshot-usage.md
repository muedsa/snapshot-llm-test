# B02 Snapshot 使用记录

## 文档与能力
- 复用套件缓存文档（suite_root 基准 tmp/run-20261011-01/_suite/docs/）：  ai-guide.md（POST /snapshot 提交、颜色、尺寸约束）、parser 源码  （ContainerParser.kt 确认 Container 属性边界）、字体清单。  B02 未新增文档 HTTP 请求（0 次）。- 实际应用的标签能力：Positioned/SizedBox/Stack/Transform(matrix)  （45° 圆角菱形叶标记）、Container gradientType/gradientBegin/End、  DecoratedBox（borderRadius/boxShadow/border SOLID）、Text  （fontSize/textAlign/lineHeight/fontStyle）、Opacity 视觉均真实渲染验证。- 字体全程使用服务端已确认的 Noto Sans CJK SC。
## 服务调用
- 渲染 25 次（requests.jsonl，ID B02-cNN-vNN）：20 次 status 200，  5 次 400 语法失败（均为确定性 DSL 语法，修复后重渲，0 次 429/503 重试）；  生成期失败 3 次未发请求（drafts 目录缺失 ×2、GRID 断言 ×1）。- final.png 均为服务原始响应字节（copy-report.json md5 双向核对）；  final.snapshot 与渲染输入逐字节一致，IHDR 尺寸与计划逐件核对。
## 逐件看图与迭代
- 20 次成功渲染全部实际打开整图查看（11 件终版各至少 1 次）；  9 次完整视觉迭代（c01/c02/c04/c05/c07/c08/c09/c10×2），  c03/c06/c11 首版达标直接交付，未制造无意义迭代。- 看图→修改→重渲→再看的观察、修改与比较逐条记于 iterations.jsonl。
## 踩坑与对策
1. XML 声明被拒：`<?xml ...?>` 首字符 400 PARSE_ERROR（c01/c02 各 1 次）。
   emit 不带声明。
2. Snapshot 只能一个子节点：平铺多子节点 400；必须 Snapshot>SizedBox>Stack
   (alignment=TOP_LEFT, clipBehavior=NONE)（复用 B01 已证嵌套）。
3. Container 无 x/y：读 _suite/docs 的 ContainerParser.kt 源码确认其只解析
   minWidth/maxWidth 等约束，绝对定位一律 Positioned 包装（读源码避免臆造）。
4. gradientBegin 词汇表无 LEFT_CENTER（c10 400）：合法值 CENTER_LEFT/…，
   服务错误响应 diagnostic.allowedValues 直接给正解，按其修正一次通过。
5. 大字号多行 Text 行距不受 line_h 约束：56px 文本实测行距≈85px，三行文案
   连续两版被裁（c10 v1b/v2）；最终改两行对称四字并按实测留高。
6. 图层顺序：后画的行底/条带会盖住先前的高亮带与标签（c07）；行底先画、
   标签裁剪到可见跨度。
7. 单元格密度碰撞：3 枚 chip + 容量条在 148px 格高重叠（c05）；格高与步距
   按内容数重算。
8. 生成期断言拦数据错误：GRID 写成 17 格断言失败未发请求（c05）。
9. tw()/fit() 对含 \n 整串估宽产生误报（c06/c08/c10）：逐行核对后放行，
   保留告警作记录。

## 复现条件
- python tmp/run-20261011-01/B02/scripts/b02_caseNN.py <ver> 生成 DSL；- python tmp/run-20261011-01/_suite/scripts/snap_render.py --dsl <dsl>  --out <png> --log tmp/run-20261011-01/B02/requests.jsonl --rid <rid> 渲染；- python tmp/run-20261011-01/B02/scripts/b02_finalize.py 汇总交付。
## 最终审查
- 11 件终版逐张实际查看：内容完整、无截断/遮挡、层级清晰、目标观看  距离（0.4m–8m 分档）可读；跨件共享事实对账一致（assert_facts）。- 作品集独立性：11 种媒介/任务/数据结构，无版式复制（touchpoint-map.json）。- portfolio.json 逐件逐标准（G1–G8）记录结果与证据，无未满足项。
## 未解决事项
- 无。
