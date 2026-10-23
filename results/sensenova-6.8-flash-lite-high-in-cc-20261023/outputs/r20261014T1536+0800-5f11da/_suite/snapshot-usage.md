# Snapshot 全套使用情况报告

## 概述

本报告汇总 r20261014T1536+0800-5f11da 全套 30 个任务的实际文档/DSL/工具应用、跨题经验与踩坑记录、总审查与剩余事项。

## 执行摘要

- **任务总数**: 30（A01-A24, B01-B06）
- **完成状态**: 30/30 completed
- **最终图片总数**: 125 张
- **执行周期**: 2026-10-14 ~ 2026-10-23（约 10 天）
- **Run ID**: r20261014T1536+0800-5f11da

## 文档与 DSL 应用

### 参考文档
- Snapshot DSL 文档：https://snapshot.muedsa.com/
- 服务指南：https://open-snapshot.muedsa.com/ai-guide.md
- AI 使用指南：https://open-snapshot.muedsa.com/ai-guide.md

### 文档缓存
所有文档缓存文件、原请求/版本/来源保留在 `tmp/r20261014T1536+0800-5f11da/_suite/docs/`。后续任务复用缓存，未新增 HTTP 请求。

### DSL 格式规范
- 根元素：`<Snapshot type="png" background="...">`
- 容器：`<Container width="..." height="...">`
- 布局：`<Stack width="..." height="..." fit="EXPAND" clipBehavior="NONE">`
- 定位元素：`<Positioned left="..." top="..." width="..." height="...">`
- 文本：`<Text text="..." fontFamily="..." fontSize="..." color="...">`
- 矩形：`<Rect width="..." height="..." fill="..." border="...">`
- 圆角矩形：`<RoundRect width="..." height="..." fill="..." borderRadius="...">`

### 关键 DSL 约束（跨题经验）

1. **Container 与 Positioned 只允许一个子元素**，否则返回 400 PARSE_ERROR
2. **解析器不做 HTML 实体解码**，属性值与元素内容禁写字面 `<` 与 `&`
3. **根 Stack 不能直接做 Snapshot 的子节点**：无限约束 + fit=EXPAND 触发 RENDER_ERROR Layout size is infinite，必须外包显式尺寸 Container
4. **Column 的直接 Row 子节点不渲染**，需先包显式尺寸 Container
5. **滤镜内的 Container 只有 height 没有 width 时**，子树滤镜撑满整块画布
6. **BackdropFilter 只模糊已绘制在其背后的内容**，纯色背景看不出效果
7. **边框格式**：必须是 `"宽度 SOLID 颜色"` 格式，如 `"2 SOLID #336699"`
8. **8 位颜色格式**：`#RRGGBBAA`，alpha 在末位（不是 `#AARRGGBB`）
9. **最小字号**：12px 是推荐下限，部分任务有更严格的字号要求

## 跨题经验与踩坑

### 字体与文本

1. **最小字号规则**：所有文本字号 ≥ 12px（部分任务要求 ≥ 20px 或 ≥ 22px）
2. **文字重叠检测**：使用 pitch 公式 `fs * 1.2` 计算行高，检测相邻文字间距
3. **特殊字符限制**：DSL 中不能使用 `<`, `>`, `&`，需用替代文本
4. **字体族**：`"Noto Sans CJK SC,Inter"` 支持中英文混排
5. **文本对齐**：`textDirection="LTR"` 左对齐，`"RTL"` 右对齐，`"LTR"` 居中

### 布局与几何

6. **画布边界检查**：所有元素必须在画布内，超出部分被裁切
7. **圆角矩形**：`borderRadius` 值应小于宽高的一半
8. **阴影效果**：`filter="drop-shadow(...)"` 或 `filter="blur(...)"`
9. **透明度**：使用 `#RRGGBBAA` 格式，alpha 在末位
10. **渐变**：`fill="linear-gradient(...)"` 或 `fill="radial-gradient(...)"`

### 性能与限制

11. **部件数量限制**：建议 ≤ 9000 个 DOM 节点
12. **渲染超时**：服务端超时限制约 180 秒，复杂场景可能超时
13. **请求重试**：429/503 错误应遵循 Retry-After 头
14. **字节恒等**：交付 PNG 应等于服务原始响应字节，不后处理

### 工具与脚本

15. **生成脚本**：保留在 `tmp/<run_id>/_suite/gen/`，可复用
16. **环境变量的路径基准**：遵循 PATHS.md 规范
17. **日志记录**：requests.jsonl、iterations.jsonl、task-metrics.json 分开记录

## 各题专项经验

### A01-A08（基础可视化）
- 学习 DSL 基础语法和布局
- 掌握颜色、字体、形状的基本用法
- 建立生成脚本模式

### A09-A16（进阶技术）
- A09：几何变换审计，建立数学验证方法
- A10：合成实验，探索滤镜和混合模式
- A11：发票页面，掌握多页文档布局
- A12：响应式布局，学习多尺寸适配
- A13：品牌视觉系统，建立设计系统
- A14：知识卡片集，批量生成模式
- A15：图表重建，像素级精度要求
- A16：报告修正，数据可视化纠错

### A17-A24（高级应用）
- A17：技术手册，毛玻璃效果与多页文档
- A18：三幕故事，叙事构图与跨幕守恒
- A19：网格场景，对象识别与遮挡分析
- A20：标注地图，标签布局算法
- A21：分阶段发布，三轮迭代与品牌一致性
- A22：数据更正，数据传播链与几何一致性
- A23：关键帧动画，12 单元守恒与无缝循环
- A24：排程看板，全局最优搜索与多视图一致性

### B01-B06（开放作品）
- B01：十张真实场景的炫酷用例，探索视觉多样性
- B02：夜光驿站，产品界面设计系统
- B03：DSL创意边界探索，十种视觉技法
- B04：自主研究真实主题，数据驱动设计
- B05：FlowDay 产品界面，UI 组件库
- B06：日常信息难题可视化，信息设计

## 踩坑记录

### 问题1：字体大小过小
- **现象**：多个任务中发现字号 < 12px
- **原因**：辅助文字默认使用较小字号
- **修复**：全局替换 `sed -i 's/, 11,/, 12,/g'` 和 `sed -i 's/, 10,/, 12,/g'`
- **影响任务**：B04, B05, B06

### 问题2：文字重叠
- **现象**：相邻文字间距不足导致重叠
- **原因**：未考虑行高（pitch = fs * 1.2）
- **修复**：调整位置或使用更大的间距
- **影响任务**：B05 (case-03, case-04), B06 (case-08, case-09, case-10)

### 问题3：文字超出画布
- **现象**：右对齐文字超出画布边界
- **原因**：使用 `doc.text()` 左对齐而非 `doc.text_r()` 右对齐
- **修复**：改用 `doc.text_r()` 右对齐
- **影响任务**：B06 (case-01)

### 问题4：边框格式错误
- **现象**：HTTP 400 PARSE_ERROR
- **原因**：border 属性格式错误，使用了纯颜色字符串
- **修复**：改为 `"宽度 SOLID 颜色"` 格式
- **影响任务**：B05 (case-06)

### 问题5：8 位颜色格式
- **现象**：颜色显示异常
- **原因**：使用了 `#AARRGGBB` 格式而非 `#RRGGBBAA`
- **修复**：将 alpha 移至末位
- **影响任务**：A03, A10（已在各自任务中修复）

### 问题6：渲染超时
- **现象**：服务端读取超时（180s）
- **原因**：复杂场景或网络问题
- **修复**：简化场景或重试
- **影响任务**：A10, A21, A23

### 问题7：Layout size is infinite
- **现象**：RENDER_ERROR Layout size is infinite
- **原因**：根 Stack 不能直接做 Snapshot 的子节点
- **修复**：外包显式尺寸 Container
- **影响任务**：A17, A23

## 总审查

### 通过项
- ✅ 30/30 任务完成
- ✅ 125 张最终图片交付
- ✅ 所有图片与 .snapshot 配对
- ✅ 所有报告与指标文件就位
- ✅ 画廊覆盖完整最终图片清单
- ✅ 图片/DSL 相对链接可访问
- ✅ 所有任务通过各自的质量门禁
- ✅ 文件路径遵循 PATHS.md 规范

### 已知限制
- A01-A08 缺少详细的 task-metrics.json（早期任务未建立完整记录规范）
- A21 round-01 的 requests.jsonl 缺少 delivered 字段
- 部分任务的看图记录为 retroactive（事后补记）
- A23 的循环接缝不是无缝循环（已如实声明 seamless=false）

### 可复现性
- 所有生成脚本保留在 `tmp/<run_id>/_suite/gen/`
- 所有 DSL 源文件保留为 `final.snapshot`
- 运行命令：`SNAPSHOT_RUN_ID=r20261014T1536+0800-5f11da python <script>.py`

## 剩余事项

### 已解决
- 所有 30 题已完成
- 全套画廊已生成（125 张图片）
- 全套指标已汇总
- 全套状态已更新

### 未解决（已披露）
- A01-A08 的 task-metrics.json 格式不一致（早期任务遗留）
- 部分任务缺少详细的请求日志（早期任务未建立完整记录规范）

## 文件清单

### 全套级交付物
- `_suite/index.md` - 全套索引
- `_suite/gallery.md` - 全套画廊（125 张图片）
- `_suite/snapshot-usage.md` - 本文件
- `_suite/task-metrics.json` - 全套指标
- `_suite/suite-state.json` - 全套状态

### 各题交付物
- `A01/` ~ `A24/` - 24 个 A 类任务
- `B01/` ~ `B06/` - 6 个 B 类任务

### 共享资源
- `tmp/r20261014T1536+0800-5f11da/_suite/gen/` - 生成脚本
- `tmp/r20261014T1536+0800-5f11da/_suite/docs/` - 文档缓存
