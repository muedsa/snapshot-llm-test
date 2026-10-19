# A21 三轮累计 · snapshot-usage

## 状态
completed（round-01 / 02 / 03 全部完成）。最终 6 张指定图：
round-01/round-02/round-03 × (launch-portrait 1080×1350 / launch-wide 1440×810)，
每张同名完整 .snapshot 同目录配对；三条专用审计轮产物（design-tokens.json、
content-map.json、round-03/contrast-audit.json）+ 每轮 usage/metrics 就位。

## 服务/文档/工具应用（三轮持续有效）
- 服务 open-snapshot（POST /snapshot，PNG），全部真实渲染请求 20 条留痕于
  tmp/20261016T164020-m1/A21/requests.jsonl（22 行含 r02 的 2 行重复自留痕行；含 requestId、
  Server-Timing、失败原因）。
- 文档：ai-guide.md、parser-tags、layout、fonts（缓存于 tmp/docs/，跨题复用）。
- 字体：Inter（拉丁/数字）+ Noto Sans CJK SC（中文）实测可用。
- 能力实测：根 Snapshot>Stack+SizedBox 定版式；Container 渐变
  (LINEAR + gradientColors/BEGIN/END)、border SOLID、borderRadius 胶囊；Raw 行内
  兼色混排（sponsor 前缀/名双色）；textAlign CENTER/START；letterSpacing。

## 三轮要点
1. round-01（深空 v03）：横带三段渐变 + 双环 + 信标 + 点阵；幽灵装饰预混深底
   实色（#113850 等）；竖居中对称/横左右分栏双构图。
2. round-02（长标题+赞助+免费参加）：标题换长文 3 行 64/54（≥48），新增
   Northstar 承赞助 /云构工具（Raw 双色）与『免费参加 · 无需报名』胶囊；
   级联防碰撞逐级 ≥8px，无 Transform。
3. round-03（浅色主题+对比度审计）：底 #F5F8FC→#E9EFF7；TEAL_INK 加深
   #085F55；EN 副句新增；去文字辅助渲染 + 字形实测范围取最劣背景，
   24/24 段未舍入 ≥4.5（最小 5.199784），审计与修复过程透明留痕。

## 踩坑与经验（已写成可复用规则）
1. Opacity 仅接受一个子节点：多数场景套 Stack 再装多个 Positioned。
2. 无界 Stack 会 Layout size is infinite：先用 SizedBox 定画布，再叠全定位图层。
3. Positioned 不能直接子挂 Opacity（parentData 错），普通子节点改用预混色或
   调层次。
4. Text 的 height 是行高倍数不是像素，误用会把文字挤出定位框；行高用
   fontSize*1.45 定 Positioned 高即可。
5. `&nbsp;` 实体不解码：一律真实 NBSP（\u00a0）。
6. 结构性删除（去文字辅助版）要连『仅含 Text 的 Positioned 包装』一起删，否则
   ProxyWidget has no widget ×400。
7. 对比度审计对『文字实际背景』取最差样本时，用最终图前景匹配像素的紧外包
   （±2px）作字形范围，避免把范围外的信标/渐变条/胶囊边框/圆角外误判成文字背景。

## 请求/迭代/看图统计（累计，含辅助渲染）
- snapshot 渲染请求 20 条（成功 12 / 失败 8：r01 语法 6 + r03 辅助版 2）。
- DSL 版本 8（finals 变体 + helper strip 变体分别计数）。
- 完整视觉迭代 2（r01 布局重排、r03 TEAL_INK 修复）；syntax-fix/替代方案另记。
- 图像查看 22 次事件级记录（含整图、放大分区与去文字核对）。
- 墙钟含跨日间隔（10-17 19:49 → 10-18 12:0x），active 分轮计时如实拆分。

## 证据索引
- tmp/20261016T164020-m1/A21/requests.jsonl、iterations.jsonl、r02/r03-iterations.jsonl
- tmp/20261016T164020-m1/A21/bg-data/（去文字辅助 PNG/DSL，不清理）
- tmp/20261016T164020-m1/A21/steps/（half、分区放大、bg-half、v2 复查件）
- outputs/20261016T164020-m1/A21/round-0X/（各轮全部交付）

## 未解决事项
无。
