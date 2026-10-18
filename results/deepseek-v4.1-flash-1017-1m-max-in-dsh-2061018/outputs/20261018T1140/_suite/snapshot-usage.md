# 全套 Snapshot 使用与审查

## 结果
- run_id `20261018T1140`；30/30 题完成；124 张最终 PNG 与同名 DSL；A21/A22 各 3 轮；B01–B06 各 10 件（60 件）。
- 指标：301 次渲染请求（成功 264，失败 37，重试 16），140 个 DSL 版本，240 次看图，69 次完整视觉迭代。

## 文档与能力
- 实际阅读 ai-guide、parser-tags、layout guide；使用 Text/Raw/span、Container/Stack/Positioned、Transform、ClipPath/多边形、Opacity、ImageFiltered、边框/圆角/渐变、透明 PNG；未用 Image 嵌入主图。
- 关键经验：全 Positioned 的嵌套 Stack 会无限布局，需要非定位 SizedBox；Text trim 用 Raw/text 属性；Transform 必须矩阵；色彩 alpha 为 #RRGGBBAA。
- A23 已如实判定 SVG/CMYK/GIF/动画时间轴不原生支持，替代为 PNG 封面 + 6 透明关键帧 + timing。

## 全程问题
- 服务多次 TLS/empty reply/超时（A18、A20-A24、B05 等）；失败响应/重试都保留，最终图均 200。
- 长任务/大画布偶发超时；A22/A24 用重试与更长超时解决。
- B01 地质展底部遮挡、烘焙曲线方向、风险矩阵表头；B02 课表重复/物种空圆/旗签白字；B03 轨道中心/玻璃标题/日期；B04 封面重叠/年龄页/弱势页注释；B05 状态栏/星期/血压图/周报柱高；B06 账单柱图压页头/EOB 不闭合。均已修。
- 未解决：无已知交付缺陷；所有演示数据已标注，不构成医疗/法律/税务/保险建议。

## 审查
- 30 题逐题图已实际查看；A21/A22 保留三轮；B01–B06 每件 case.md/portfolio。
- 总画廊 124 张链接全部可访问；每张有 PNG/DSL 两链；无缺图/占位。
- 根 `.gitignore` 仅忽略运行时缓存，tmp/outputs 证据未忽略。
