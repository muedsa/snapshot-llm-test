# B02 · 月度状态卡（1080×1080）

## 使用情境与用户任务
社区群转发方图，手机端 30 秒读
- 用户要完成的事：本月共约多少次、谁最受欢迎、志愿者贡献——建立社区正反馈

## 视觉选择
三大数 KPI 行 + 六工位热度横条（超过半数转青、低频灰蓝）

## DSL 实现要点
大号 Inter 数字 KPI、bar_row 双色阈值、footer 演示声明

## 设计系统引用
本件复用 `design-system.json` 定义的 tokens（色板/字号阶梯/组件/圆角），
品牌与演示声明每件必带：仅在印刷件使用 micro 字号。

## 交付
- `final.png`：open-snapshot 服务真实渲染（200）
- `final.snapshot`：完整 DSL（label `b02-case-07`）
