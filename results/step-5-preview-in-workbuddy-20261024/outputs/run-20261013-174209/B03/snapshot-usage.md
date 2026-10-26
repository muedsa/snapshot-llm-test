# B03 · Snapshot DSL 使用记录

服务：open-snapshot（run-config.json 指定），端点 `POST /snapshot`，Content-Type `image/png`。

## 请求统计

- 总请求：91 次（含 10 次渲染行为探测）
- 成功：37（HTTP 200；用例渲染 27 次，平均 "
6.61s）
- 失败：54（PARSE_ERROR×32；读超时×9；其他×4；RENDER_ERROR×4；SSL/连接错误×2；连接中断×3）
  - 网络层（读超时/连接中断/SSL）：服务间歇故障，由重试层覆盖（b03_net.py 200s 超时 ×4 次）
  - PARSE_ERROR / RENDER_ERROR：DSL 边界触碰，经探测实证后改写法（详见 technique-notes.md）

## DSL 能力实际使用范围

| 能力 | 使用情况 |
|---|---|
| Container 定尺/圆角/边框/阴影 | 10 件全部（600×800 至 1920×1080，8 种画布比例） |
| Stack + Positioned 绝对定位 | 10 件全部；全部元素绝对定位，坐标经脚本计算 |
| 渐变 LINEAR/RADIAL/SWEEP | 10 件全部（天色/霓虹/光晕/能量环/按钮渐变） |
| Transform matrix | 旋转光束（01）、60 根刻度（07）、47 根渐变色条拼弧（07）、曲线折线段 |
| 文本 Text | STROKE 空心（01/06/07/10）、textShadow 多层辉光（01/06/10）、decoration（06/10）、letterSpacing/height（06）、嵌套 Span + WidgetSpan + Emoji（10） |
| 富文本 Raw/Text 嵌套 | rich_text 助手（10）：嵌套 Span 颜色/字体混排 + WidgetSpan 行内嵌件 |
| ClipRect/ClipRRect/ClipOval/ClipPath | 出血裁切（02/09）、圆角（02/05/08/10）、镂空剪纸 EVEN_ODD（03）、自定义路径（02 行动条/08 叶形） |
| 滤镜 ColorFiltered/ImageFiltered/BackdropFilter | 双色调（04）、分层景深（08）、毛玻璃（02） |
| Flex Row/Column/Expanded/Flexible/Spacer | 时间轴（02）、大数字（04）、三档自适应（05）、数据行（09） |
| AspectRatio/FractionallySizedBox/ConstrainedBox/SizedOverflowBox | 约束构件三件套（05）、破界色带（09） |
| Opacity | 雾带（08）、loading 三点（08）、层次（02） |
| Image dataUri | 仅 case-04（PIL 生成灰度赛照，双色调映射底图，合法用途已注明） |
| Emoji（Noto Color Emoji） | case-10 顶部 🦢🍂🦆 与右下 🦆 |

## 实测边界与规避（详见 technique-notes.md）

1. **百分比尺寸完全非法**：Positioned/Container 等 width/height 只接受像素浮点（case-05 实证）
2. **ImageFiltered/ClipRect 只接受单一子级**：多元素必须先包 Stack fit=EXPAND（probe3/08/09 实证）
3. **SizedOverflowBox 内 Text 不溢出**（被盒约束），Container 子级可溢出——文字破版必须逐字 Positioned（case-09 实证）
4. **Positioned 不能嵌套**（父必须是 Stack/IndexedStack）；grad()/container_rotate() 等助手自带 Positioned，不能嵌入其他 Positioned 内
5. **ConstrainedBox 紧约束父级下 min/max 失效**；Align 松约束父级下正常生效（probe5 实证）
6. **SWEEP 语义异常**：亮区恒从 12 点起、startAngle 不影响起点、渐变反向映射、endAngle 与跨度非线性——进度弧改用渐变色旋转条拼成（probe6/7 实证）
7. **border 样式只支持 NONE/SOLID**（无 DASHED）；**textShadow 最多 4 令牌**（第 5 个 spread 仅容器 boxShadow 支持）
8. **2px 宽条有渲染丢失风险**（亚像素+圆角吞没，最小 3px）
9. **WidgetSpan 高于行高时按 BOTTOM 对齐**：文本被挤到嵌件下半部，徽章尺寸宜 ≤1.5 倍行高（case-10 实证）
10. **CENTER 对齐的 left 参数** 必须是 (容器宽-文本宽)/2 而非容器中心 x
11. **HTML 实体不被解码**；`+=` 会把返回 str 的助手按字符展开（返回 list 的助手才能 +=）

## 复用资产

- 共享助手：`tmp/run-20261013-174209/B03/b03_common.py`（T/rich_text/frosted/blurred/grad/rotate/clip_path 等）
- 逐用例生成器：`tmp/run-20261013-174209/B03/cases/case01_gen.py` … `case10_gen.py`
- 每份最终 `.snapshot` 完整自包含（无外部文件依赖），可独立重新提交渲染
- CRLF 说明：final.snapshot 由 `write_text` 写出（Windows CRLF 换行），与请求体仅差换行符
