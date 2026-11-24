# B03 技术手记：十种服务于场景的 DSL 手法

本合集在首次渲染前以 `tmp/20261124T113838+0800-aac601/B03/plan-v001.json` 固定十件作品、受众、使用任务、观看环境和可观察标准。十件并非技术标签陈列：每一种手法都决定了一个实际信息产品如何被看见、阅读或使用。品牌、票号、地点、活动、排班和数值均为虚构或演示，不宣称真实部署、导航、安全认证、养护建议或天文预测。

## 共同文档与试验依据

实际读取并保留于 `tmp/20261124T113838+0800-aac601/_suite/shared/` 的服务指南、Parser 标签/文本、布局、绘制和媒体文档，是以下结论的依据。能力探针 `probe-v001` 至 `probe-v005` 均经真实 `/snapshot` 服务渲染；失败版本与原始请求/响应保留。最终图像逐件查看，并以 r003 整体接触表、200% 局部裁图、灰度/低亮度副本和计算记录复核；接触表不替代十张最终服务原图的查看。

共同边界：`Positioned`、`Container`、`ClipPath` 等单子节点节点不能直接并入多个并列子节点，需使用 `Stack`/`Row`/`Column`；`Text.height` 不是像素高度。实际根因是给 `Text` 写入像素 `width/height` 后复杂布局中的辅助文字消失，改为外层 `Container` 提供有限约束与对齐。Parser 不解码 HTML 实体，正式作品避免把 `&` 作为品牌文字。

## case-01 · Night Ferry cut-out ticket

- **独到手法**：同一 ClipPath 内用两个同向闭合轮廓形成 EVEN_ODD 舷窗孔，并以波浪轮廓完成票券下缘的真实镂空；孔洞透出独立 backing，而不是画一个白色圆冒充剪切。
- **文档依据**：`parser-tags.md:556–598` 的路径、viewBox、fit 和 fillRule。
- **试验与看图**：probe-v002/v003 验证双轮廓孔洞；r003 的 `case-01-porthole-wave-r003-200pct.png` 与平面遮罩服务参考实际比较，边缘连续且未侵入文字。文字约束失败后 v002 恢复，最终版本保留。
- **应用价值**：实体票根、入口卡和纪念票可用真实剪切建立识别，同时保留严格信息网格。
- **确认边界**：孔洞依赖奇偶填充而非 contour 方向；抗锯齿边缘需要 contrasting backing，不能假定会得到硬边矢量切割。

## case-02 · Crosswind cycling route poster

- **独到手法**：每段箭头是独立 DSL 模块，以有序 translate/rotate/scale 和明确 origin 放置，形成连续折线；编号、转向语义和 caution 卡不随箭头一起旋转。
- **文档依据**：`parser-tags.md:134–157、495–516` 的矩阵函数顺序、单位、origin 和 transformAlignment。
- **试验与看图**：probe 验证非中心旋转；`calculation-checks-r003.json` 记录五段长度、角度与地图面板边界，全部点在面板内。v002 提示卡首行贴顶，v003 增加 Center/Padding 后两行完整，r003 200% 复核通过。
- **应用价值**：公交/骑行/展览动线可将方向语义与可读文字解耦，避免整张信息图旋转。
- **确认边界**：变换不预留额外布局空间；父级过紧会裁掉旋转后的可见边界，路线数据仍只是虚构演示，不可导航。

## case-03 · Glasshouse visitor information panel

- **独到手法**：先绘制 DSL 植物背景，再叠 BackdropFilter 玻璃信息面板；滤镜只作用于已绘制背景，参观路线、三区信息和按钮保持锐利。
- **文档依据**：`parser-tags.md:518–548`；`painting.md:82–110` 对 backdrop 与 subtree blur 的区分。
- **试验与看图**：probe 用前后景色块确认滤镜作用域。r003 局部图显示背景柔化、前景清晰；三种背景的合成对比度计算中，最终 `#46566A` 副文字对比为 5.93、5.63、5.41，较旧色 3.55–3.89 提升。
- **应用价值**：游客中心、场馆导览和户外信息牌可在复杂实景式背景上保持 calm hierarchy。
- **确认边界**：BackdropFilter 需要先有背景；局部亮色仍会改变最终合成，半透明面板不能替代对比度计算。

## case-04 · Low Tide Observatory depth poster

- **独到手法**：三组完整波浪子树分别用不同 sigma 的 ImageFiltered 构造远、中、近景；清晰活动卡位于滤镜之外，空间深度由边缘软硬编码。
- **文档依据**：`parser-tags.md:518–538` 的 ImageFiltered 与自动输出边界；`painting.md:93–110`。
- **试验与看图**：probe 验证子树模糊；v002 修复文字约束后，r003 `case-04-wave-layers-r003-200pct.png` 显示三层软硬差异，输出留白完整，无透明硬切。
- **应用价值**：环境展陈、季节活动和教育海报可用受控景深建立叙事，而不把正文一起模糊。
- **确认边界**：滤镜会扩大输出边界，需给 sigma 留空间；这里的深度带是说明性视觉，不是实测海洋数据。

## case-05 · Two Lantern Theatre cast billboard

- **独到手法**：两个原创几何人物以 SRC_IN/MULTIPLY 生成钴蓝/珊瑚色面，并在中央真正交叠；第二个肖像包 Opacity，使交叠带成为“冲突”的视觉核心。
- **文档依据**：`parser-tags.md:518–538`；`painting.md:82–106` 的 ColorFiltered、blendMode 与 opacity 区别。
- **试验与看图**：probe 验证色块混合。v002 两肖像分离且透明区域出现 flattened 橙色底板；v003 将第二肖像移入交叠位置并降低不透明度，r003 200% 图显示蓝/珊瑚混合带，标题与演职员表仍在滤镜区外。
- **应用价值**：双人戏剧、对话活动和对立叙事可用颜色关系表达主题，同时保留长距离识别的标题。
- **确认边界**：当前服务中 MULTIPLY 的透明区域可能被 flatten，不能假定保留透明；需按完整子树试验，不能只依赖理论混合公式。

## case-06 · Fix-It Club inline workshop leaflet

- **独到手法**：编号图标是 WidgetSpan，和 Text/Raw 处于同一段落，随中文句子换行并按 MIDDLE 对齐；它们不是用 Row 绝对定位的伪行内图标。
- **文档依据**：`parser-tags.md:621–675`；`parser-text.md:15–23、46–101` 的继承、Raw 和共享段落流。
- **试验与看图**：probe-v002 显示 WidgetSpan 被 XML 转义，v003 修复节点转义。正式 v002 标准审计发现原计划要求四步而画面只有三步；v003 补入“离开前清点工具…”并压缩行距，r003 200% 复查四步全部在段落内。
- **应用价值**：工作坊、说明书和入门清单可在长句中嵌入状态图标，保持自然阅读节奏。
- **确认边界**：WidgetSpan 节点必须作为受信任 DSL 片段插入，普通用户文本仍需转义；行高与内边距要按最长句子实测。

## case-07 · Hand & Vessel fair pattern wrap

- **独到手法**：Pillow 生成 96×96 原创几何陶纹，再以 384×384 抗锯齿衍生并缩至 144×144；Image 以 dataUri、repeat=REPEAT、scale=1 和默认 SCALE_DOWN 生成连续纹样场。标题、地点与页脚由 DSL 实色面板打断。
- **文档依据**：`parser-tags.md:600–619`；`media-text.md:39–49` 的逻辑尺寸、像素密度与 repeat 限制。
- **试验与看图**：v003/v004 的 `fit=FILL` 虽看似重复，实际把单块纹样拉满目标盒。probe-v004/v005 和正式 v005 省略 fit，以 144 像素逻辑间距真实平铺；r003 200% 接缝图显示等距、连续、无意外缺口，信息区完全净空。
- **应用价值**：市集、节庆和包装识别可用一个小素材建立可扩展纹样，同时让关键信息拥有稳定读区。
- **确认边界**：scale 是像素密度而非直接显示缩放；默认 SCALE_DOWN 与 FILL 语义不同。服务 parser 不解码实体，品牌中的 `&` 改为 AND。素材仅限局部纹样，不是整图预绘。

## case-08 · Blue Hour sky-orientation dial

- **独到手法**：RADIAL 中心暮光场和 SWEEP 外盘使用显式 stops/angles，ClipOval 限定圆形；方向字母和活动卡位于颜色过渡之外。
- **文档依据**：`parser-tags.md:252–273` 的渐变类型、停止点和各类型约束。
- **试验与看图**：probe 验证扫描渐变；r003 200% 角度/径向图、灰度图和 35% 亮度副本实际查看，结构不依赖颜色单独表达，中央文字在低亮度审查副本仍可辨。
- **应用价值**：户外队列、定向活动和夜间导览可用角度场建立方向感，同时保留可手电阅读的中心信息。
- **确认边界**：stops 数量必须与颜色对应且非递减；此盘不是真实星图，方向和时间均为虚构演示。

## case-09 · Repair Commons modular timetable board

- **独到手法**：AspectRatio 图标、FractionallySizedBox 进度条、有限 Flexible/Expanded 三栏构成可复用模块；卡片尺寸按父宽缩放，字体采用独立可读下限。
- **文档依据**：`parser-tags.md:373–493`；`layout.md:90–159` 的有限约束和比例布局区别。
- **试验与看图**：全尺寸 v002 修复卡片越界。缩减探针 v001 在 1200×850 裁掉第二组卡片和底部说明；v002 将卡片高度、图标、间距、圆角按 0.684151 缩放，字号保持 0.78，六场数据和页脚完整。r003 计算与局部图一致。
- **应用价值**：社区日程、课程表和场所排班可在不同输出宽度保持结构，而不是每个尺寸重画。
- **确认边界**：Flexible/Expanded 必须有有限主轴；比例缩放几何不等于同比缩放文字，长标题仍需独立可读性检查。

## case-10 · Shadow Lab eclipse-night poster

- **独到手法**：Stack 内以 Opacity group 和 ClipOval 构造多层轨道盘，第二椭圆在组内覆盖第一椭圆，再以组透明度合成到背景；独立红色椭圆再次叠加。
- **文档依据**：`parser-tags.md:409–432、495–548`；`painting.md:82–91` 的子树 opacity 与合成区别。
- **试验与看图**：probe 检查组透明度；`calculation-checks-r003.json` 给出背景、组内蓝盘与红盘交叠的 RGB，r003 200% 图显示清楚层序、干净椭圆边缘和中心遮月，文字区不受影响。
- **应用价值**：天文夜、光影展和音乐活动的主视觉可用真实透明合成建立聚焦，而非粘贴预绘月亮。
- **确认边界**：组内不透明体会覆盖先绘制层，group alpha 不等于每个子层单独 alpha；轨道仅为概念图，不表示预测食相。

## 最终证据与复现

- 不可变计划：`tmp/20261124T113838+0800-aac601/B03/plan-v001.json`。
- 最终逐件审查：`tmp/20261124T113838+0800-aac601/B03/final-review.json`。
- 第三轮整体与细节：`tmp/20261124T113838+0800-aac601/B03/inspection/contact-sheet-final-r003.png`、`detail-contact-sheet-final-r003.png`。
- 计算：`tmp/20261124T113838+0800-aac601/B03/inspection/calculation-checks-r003.json`。
- 生成脚本：`tmp/20261124T113838+0800-aac601/B03/prepare_B03.py`；所有历史版本、原始请求/响应和日志均保留。
- 每张最终 PNG 与唯一成功响应字节完全相同；final.snapshot 与 UTF-8 请求体在 CRLF→LF 归一化后一致。未解决交付缺陷：无。
