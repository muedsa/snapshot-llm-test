# B02 · 预约看板 · 横屏（1920×1080）

## 使用情境与用户任务
工具房内电视/投屏，值班志愿者与进门居民共用，2–5 m
- 用户要完成的事：六个工位今日谁用/几点/什么风险，10 秒判定；报修找谁

## 视觉选择
斑马行六工位 + 状态药丸 + 每行 ▲ gauge 风险档；右列空闲统计与值班名条

## DSL 实现要点
gauge ▲ 字块（按 level 换色）、bar_row 空闲率、diamond_wave 卡内装饰带

## 设计系统引用
本件复用 `design-system.json` 定义的 tokens（色板/字号阶梯/组件/圆角），
品牌与演示声明每件必带：仅在印刷件使用 micro 字号。

## 交付
- `final.png`：open-snapshot 服务真实渲染（200）
- `final.snapshot`：完整 DSL（label `b02-case-02`）
