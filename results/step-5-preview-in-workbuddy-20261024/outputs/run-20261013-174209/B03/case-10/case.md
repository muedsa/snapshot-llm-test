# case · 10 · 产品发布电子邀请函

- 画布：1080×1080（1:1 方卡）
- 受众：受邀嘉宾（邮件/社交分发）
- 使用场景：「秋迁观鸟季」启幕仪式电子邀请函
- 使用目标：一卡传递活动名、日期时间地点与 RSVP 入口
- 主导手法：WidgetSpan 行内嵌件（日期徽章/序号徽章/菱形分隔）+ 嵌套 Span 混排（SERIF/INTER 数字/金色强调）+ Noto Color Emoji + decoration 层级
- 视觉主张：夜蓝卡纸 + 双线金框 + 叶形徽标 + 92px 衬线主标题 + 渐变 RSVP 按钮
- 内容依据：虚构「秋迁观鸟季」启幕仪式邀请函；鹭洲湿地公园科普馆露台、回复截止等均为虚构演示信息（日期 2026-11-20 周五经 datetime 实算）
- 最终版本：case-10-v02（request_id 9c18a2b5-1ba1-4aee-bd74-cdedaaa7cdc5，耗时 8.453s，DSL 13722B）

## 完成标准与实际结果

### C10-1 WidgetSpan 行内嵌件与文本混排正确
- 实际结果：已达成
- 检查方法与证据：dsl：三段 rich_text——圆形「4」徽章（30×30）行内居中对齐、日期徽章（56×56）、菱形分隔（10×10）；view-zoom：徽章分区放大，序号圆与文字行距协调；日期徽章 v02 缩至 56px 后圆-文中心错位从 19px 降至 10.5px

### C10-2 嵌套 Span 颜色/字体混排可辨
- 实际结果：已达成
- 检查方法与证据：dsl：GOLD SERIF 活动名 + ORANGE INTER 数字（287/1/16:00–17:30）；view-zoom：正文分区放大混排层级清晰

### C10-3 Emoji 彩色渲染（Noto Color Emoji）
- 实际结果：已达成
- 检查方法与证据：dsl：fontFamily="Noto Color Emoji" + emoji 字符；pixel：🦢🍂🦆/🦆 三彩渲染实测（非单色字形）

### C10-4 STROKE 空心副题 + UNDERLINE 组合正确
- 实际结果：已达成
- 检查方法与证据：dsl：92px SERIF STROKE 1.8 + UNDERLINE 橙色；pixel：下划线实测 y466–470、x90–497 正落「启幕仪式」四字下方

## 渲染与迭代记录

- 渲染请求：8 次（成功 2，失败 6，均经自检拦截/参数修复/重试后成功）
- 版本链：v01 → v02（最终 v02）
- 迭代要点：v01 修 textShadow 5 令牌 PARSE_ERROR + 日期徽章 72→56px；v02 定稿
- [B03-c10-i01] visual-defect：① v01 首渲 4 连失败：Text textShadow 传了 5 令牌（0 6 24 0 #00000055）——服务端 textShadow 格式为 offsetX offsetY [blurSigma] [color] 最多 4 …
- 实际看图：整图、主标题区、顶部 Emoji、行内徽章、日期徽章 v01/v02、RSVP 区、页眉
- 字节核对：final.png 与服务响应 MD5 一致（5b86e7a197c2…）；final.snapshot 完整自包含（0d3c4e63b16a…）

## 未解决问题

无
