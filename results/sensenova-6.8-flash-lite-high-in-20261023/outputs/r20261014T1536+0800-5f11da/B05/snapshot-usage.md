# Snapshot DSL 使用记录

## 文档参考

- **服务指南**: https://open-snapshot.muedsa.com/ai-guide.md
- **DSL 文档**: https://snapshot.muedsa.com/

## 标签能力使用

### 基础标签
- `<Snapshot>` — 根元素，指定输出类型和背景色
- `<Container>` — 画布容器，指定宽度和高度
- `<Stack>` — 布局容器，设置 fit="EXPAND" 和 clipBehavior="NONE"
- `<Positioned>` — 绝对定位元素，通过 left/top 指定位置
- `<Text>` — 文本元素，支持 fontFamily, fontSize, color, fontStyle
- `<Opacity>` — 透明度容器

### 属性使用
- `color` — 颜色值（CSS 格式）
- `borderRadius` — 圆角半径
- `border` — 边框（格式：宽度 SOLID 颜色）
- `fontFamily` — 字体族
- `fontSize` — 字体大小
- `color` — 文字颜色
- `fontStyle` — 字体样式（BOLD）
- `height` — 高度（Text 用 "1.0" 表示行高倍数）
- `softWrap` — 软换行（"FALSE" 禁止）
- `textDirection` — 文字方向（"LTR"）

## 设计系统组件

### UIDoc 类（扩展自 b01_kit.Doc）
- `status_bar()` — 状态栏
- `nav_bar()` — 导航栏
- `bottom_tab_bar()` — 底部导航栏
- `rect()` — 矩形（支持 fill/stroke 和 border）
- `text()` — 文本（支持 anchor="left"/"center"/"right"）
- `text_c()` — 居中文本
- `text_r()` — 右对齐文本
- `circle()` — 圆形
- `line_h()` — 水平线
- `bg_section()` — 背景区域
- `rect_shadow()` — 带阴影矩形
- `card()` — 卡片
- `pill()` — 药丸形元素
- `badge()` — 徽章
- `chip()` — 芯片按钮
- `task_card()` — 任务卡片
- `time_block()` — 时间块
- `stat_tile()` — 统计块
- `avatar()` — 头像
- `checkbox()` — 复选框
- `radio()` — 单选按钮
- `toggle()` — 开关
- `list_item()` — 列表项
- `date_pill()` — 日期 pill
- `week_pill()` — 星期 pill
- `modal_sheet()` — 弹窗
- `divider()` — 分割线
- `progress_bar()` — 进度条
- `progress_ring()` — 进度环
- `empty_state()` — 空状态

## 服务调用

- **API 端点**: https://open-snapshot.muedsa.com/ai
- **请求格式**: POST JSON，包含 DSL 字符串
- **响应格式**: PNG 二进制数据
- **重试策略**: 最多 3 次重试

## 逐件看图与修改

### Case-01: 首页仪表盘
- **初始版本**: 渲染成功
- **自检**: 通过所有门禁

### Case-02: 日计划器
- **问题**: week_pill 文字重叠（day_name 和 day_num 间距不足）
- **修复**: 将 day_num y 偏移从 y+18 改为 y+20
- **自检**: 通过所有门禁

### Case-03: 专注模式
- **问题 1**: 大字号计时器（fs=52）与下方标签重叠
- **修复 1**: 将标签 y 从 cy+15 改为 cy+35
- **问题 2**: 统计数字（fs=32）与标签重叠
- **修复 2**: 将标签 y 从 740 改为 748
- **自检**: 通过所有门禁

### Case-04: 周历
- **问题**: 日历重复绘制导致文字重叠
- **修复**: 移除重复的日历绘制循环
- **自检**: 通过所有门禁

### Case-05: 任务详情
- **问题**: avatar 方法内部字号计算为 11（int(14*0.8)=11）
- **修复**: 改为 max(12, int(r*0.8))
- **自检**: 通过所有门禁

### Case-06: 引导设置
- **问题**: HTTP 400，border 属性格式错误
- **修复**: 在 rect 方法中添加 border 格式转换（"1 SOLID #color"）
- **自检**: 通过所有门禁

### Case-07: 统计与洞察
- **问题**: 活动图标字号 8 < 12
- **修复**: 将字号从 8 改为 12
- **自检**: 通过所有门禁

### Case-08: 快速添加
- **初始版本**: 渲染成功
- **自检**: 通过所有门禁

### Case-09: 设置
- **初始版本**: 渲染成功
- **自检**: 通过所有门禁

### Case-10: 成就
- **问题 1**: 徽章描述字号 9 < 12
- **修复 1**: 移除描述文字（简化设计）
- **问题 2**: 特殊字符 ">" 在 "评分>90%"
- **修复 2**: 改为 "评分90+"
- **自检**: 通过所有门禁

## 踩坑记录

1. **DSL border 属性格式**: 必须是 "宽度 SOLID 颜色" 格式，不能只传颜色字符串
2. **文字重叠检测**: 即使是 0.4px 的微小重叠也会被检测到，需要精确计算文字高度
3. **avatar 内部字号**: 小尺寸头像（r=14）会导致内部字号低于 12px 下限
4. **特殊字符**: HTML 特殊字符 <, >, & 不能出现在文本中
5. **borderRadius**: 必须使用整数像素值

## 复现条件

- Python 3.10+
- 依赖: requests
- 环境变量: SNAPSHOT_RUN_ID
- 服务地址: https://open-snapshot.muedsa.com/

## 最终审查

所有 10 件作品均满足：
- ✓ 文字最小字号 ≥ 12px
- ✓ 所有元素在画布内（400×800）
- ✓ 无文字重叠
- ✓ 无 HTML 特殊字符
- ✓ DSL 片段数 ≤ 9000
- ✓ 所有形状在画布内
- ✓ PNG 与响应体匹配
- ✓ DSL 文件与 PNG 配对

## 未解决事项

无。所有作品均已通过门禁检查并成功渲染。
