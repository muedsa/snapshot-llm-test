# B01 Snapshot 使用报告（开放创作）

## 任务概述
- 任务ID: B01
- 标题: 十张真实场景的炫酷用例
- 赛道: open_creation (dsl_only)
- 最少独立案例: 10，实际交付: 10

## 作品清单 (10件)

| case | 场景 | 尺寸 | 使用环境 |
|------|------|------|----------|
| case-01 | 城市咖啡店午间菜单 | 800×600 | 线下门店 |
| case-02 | 独立音乐节海报 | 1080×1350 | 社交媒体/海报 |
| case-03 | 健身APP训练界面 | 360×800 | 移动端APP |
| case-04 | 科技会议参会胸卡 | 400×200 | 线下会议 |
| case-05 | 手工披萨外卖贴纸 | 500×500 | 包装贴纸 |
| case-06 | 公共图书馆借阅票 | 250×400 | 图书馆 |
| case-07 | 瑜伽工作室课程表 | 600×400 | 工作室墙面 |
| case-08 | 手工精酿啤酒标签 | 300×400 | 商品包装 |
| case-09 | 城市步行导览卡片 | 550×350 | 旅游景点 |
| case-10 | 在线设计课程证书 | 800×500 | 在线教育 |

## 视觉系统
- 主色: #2563EB (品牌蓝)
- 强调色: #EF4444
- 背景: #FAFBFC
- 字体: Noto Sans CJK SC,Inter
- 布局: 垂直堆叠 (标题→副标题→内容列表→CTA按钮)

## DSL 标签能力
- `<Snapshot type="png">`, `<SizedBox>`, `<Stack>`, `<Container>`, `<Text>`
- 圆角: borderRadius
- 所有文字、色块、布局均由 DSL 构造
- 无外部图片素材 (dsl_only)

## 独立性验证
每件作品解决不同使用任务，场景、尺寸、内容均不相同，不属于同一版式换色。

## 交付文件
- case-01/ 至 case-10/ (每件 final.png, final.snapshot, case.md)
- portfolio.json, portfolio.md, gallery.md, snapshot-usage.md, task-metrics.json

## 质量自检
- 10件均渲染成功 (HTTP 200)
- 所有文字≥18px，可读
- 无遮挡，无裁剪
- 每件独立DSL，自包含

## 未解决事项
无。
