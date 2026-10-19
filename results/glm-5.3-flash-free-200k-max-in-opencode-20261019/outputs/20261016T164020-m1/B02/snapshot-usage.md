# B02 · snapshot-usage

## 状态与统计
completed。十件触点作品全部 open-snapshot 200 真实渲染与同名 .snapshot；
渲染 16 次（16 成功）、服务端时长合计 11.22s；
DSL 4 版本；5 次看图；1 基线 + 2 轮完整视觉迭代。

## 项目与设计系统
叠光共享工具房（演示品牌）——简要见 project-brief.md；
设计 tokens 见 design-system.json；触点-旅程见 touchpoint-map.json。
屏/纸双族通过 base/card 两级配色与 radius（14/10）切换，
组件 step_chips/gauge/bar_row/diamond_wave/brand_corner 跨十件复用。

## 检查与修复（真图检视）
1. baseline 双接触表可见「case-06 步骤条只显示最后一块」，先按隐形字处理
   ——已完成块文字与深底同色（visual-02：标签改琥珀底+深字）。
2. v2 证据重建放大暴露真相：三块 left 相同叠画 → step_chips 补 x 递进
   （visual-03），case-01 三块恢复独立可见。
3. v3 复看发现未完成块底（NEAVY2）与卡片底同色对比不足 → 未完成块底改
   NEAVY3（visual-04 重渲复验 case-01/06 双双通过）。
4. 案例构建期一处：b02_common 的 gauge 函数初版含死分支，第二次提交
   清理为单遍赋值（未消耗渲染，属语法级清理）。

## 文档与字体复用
未发起新的文档 HTTP 请求；沿用 tmp/docs/ 已缓存 ai-guide/DSL/layout/fonts。
字体规则沿用 A24/B01 结论：混排回 CJK，纯 ASCII 用 Inter。

## 未解决事项
无。所有画布内声明“演示品牌 · 非真实运营”，真实二维码处以占位注明
（替换真实码不属于 DSL 工作范围）。
