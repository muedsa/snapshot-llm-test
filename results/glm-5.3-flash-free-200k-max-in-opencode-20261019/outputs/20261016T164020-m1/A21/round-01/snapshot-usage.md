# A21 round-01 · snapshot-usage

## 状态
completed。交付 round-01/launch-portrait.png/.snapshot(1080×1350) 与
round-01/launch-wide.png/.snapshot(1440×810)，全部为 open-snapshot 200 真实响应。

## 设计系统（design-tokens.json / content-map.json 同步）
- 主色青 #2EE6D0 + 辅紫 #7C6CFF，深空底 #0B1220→#0D1A31 渐变；
  Inter(拉丁/数字) + Noto Sans CJK SC(中文)两级字体层级。
- 品牌 4 构件跨两图一致、分别构图：layer-stack 三层渐变横带 / halo-ring 双环 /
  beacon 信标点 / mesh-dots 点阵（透明装饰用预混实色，无 Opacity）。
- 文案最低层级 26px；主标题竖 68 横 60；数字/网址 30–46。
- 顶部/底部各留真实扩展区（竖 0–140/1180–1350，横 0–116/588–810），无占位文字。

## 视觉迭代
- 语法 6 连败：Opacity 多子节点、Opacity 直包 Positioned（parentData）、
  无界 Stack（Layout size is infinite）——改预混实色后成功。
- v02 修复：Text `height` 属性是行高倍数（误用 62/92 导致文字推出可视区），
  全部移除；&nbsp; 实体 → 真实 NBSP；chip 文字垂直居中；竖图 chip 下移至 1118、
  短线外移；横屏右栏 +30。
- v03 复检（两整图 + 两放大）：必需文案齐全、层级达标、品牌构件一致、无遮挡裁切。

## 实际查看记录
iterations.jsonl id=A21-r01-baseline-v02 / A21-r01-visual-v03，共 12 幅查看件
（两整图 half + 竖标题放大 + 横右栏放大 + chip 放大候选）。

## 未解决事项
无。
