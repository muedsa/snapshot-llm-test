# A03 · 多层语义故障恢复 — 使用报告

## 完成状态

completed。最终图 `system-pulse.png`（1280×800）由 open-snapshot 服务真实渲染（A03-req-0009，HTTP 200，image/png），与已逐项目检的草稿 `fix-v7.png` 字节一致（MD5 相同）。修复过程严格分级记录在 [repair-log.json](repair-log.json)：4 个真实报错、2 个静默忽略、3 个仅视觉暴露的问题。

| 交付文件 | 说明 |
|---|---|
| [system-pulse.png](system-pulse.png) + [system-pulse.snapshot](system-pulse.snapshot) | 修复后的 System Pulse 监控卡 |
| [repair-log.json](repair-log.json) | 每个问题对应原稿位置、真实报错/文档依据、修改与验证；含全部失败版本路径 |
| [snapshot-usage.md](snapshot-usage.md)、[task-metrics.json](task-metrics.json) | 本报告与指标 |

过程证据（相对总任务根）：`tmp/run-20261011-01/A03/`（requests.jsonl、iterations.jsonl、drafts/ 内 broken-v0.error.json 与 fix-v1~v3 的错误响应、fix-v4~v7 各版本 PNG 与 DSL）。

## 原稿提交与真实报错

按要求先把 `inputs/broken.snapshot` **原样**提交（A03-req-0001），服务返回：

```
HTTP 400 {"code":"PARSE_ERROR","message":"Attr [padding] value format error at position 92 ...",
          "requestId":"aaade24e-d057-4d2b-9f7e-ddc32750c764"}
```

随后逐个修复、逐次重提交，让服务自己依次暴露后续问题（每次响应均保存在 drafts/ 下）：

1. `padding="24 32"` → PARSE_ERROR。文档《通用属性格式 · EdgeInsets》：padding 只支持 `"12"` / `"(8,16)"` / `"(8,12,16,20)"`，**括号和逗号是语法的一部分** → 改为 `"(24,32)"`。
2. `Transform rotate="-8"` → PARSE_ERROR `Attr [matrix] must not be null`。Transform 没有 rotate 属性，只有 matrix/origin/alignment → 用列主序 4×4 矩阵表达视觉逆时针 8°，`alignment="CENTER"` 绕标签中心旋转。
3. `Row` 内放 `Positioned` → RENDER_ERROR `renderBox.parentData must be StackParentData`。Positioned 只能是 Stack/IndexedStack 子节点 → 重构为根级 Stack，LIVE 用 Positioned 定位到右上。
4. `Snapshot width/height` 被**静默忽略**（Snapshot 只有 background/debug/type 三个属性），Column 无界 → RENDER_ERROR `Layout size is infinite` → 根级 `SizedBox 1280×800` 提供有界画布。

至此全部显式错误清零，取得第一张成功渲染（fix-v4.png）。没有删除任何出错区块：标题、指标卡、LIVE、REVIEW、模糊说明卡全部保留。

## 继续排查的静默与视觉问题（fix-v4 图上发现）

5. `Text font-size="44"` 被忽略（属性名区分大小写，必须 camelCase `fontSize`）——服务不报错，只在图上暴露：标题以默认小字号渲染。
6. `#33FFFFFF` 语义变更：文档《八位十六进制颜色的迁移》说明现在按 CSS `#RRGGBBAA` 解析，`#33FFFFFF` 变成不透明亮青色（图上 REVIEW 标签实测）。需求要“白底不透明度 20%、文字不透明” → 改 `#FFFFFF33` + 不透明白字 24 号。
7. `ImageFiltered` 包住整张卡会把**文字一起模糊**（图上说明文字不可读）。文档：ImageFiltered 对整棵子树做高斯模糊 → 改为分层：卡外细条锐利绘制；卡内 `ClipRRect(r=24)` 重绘同样的细条并各自包 `ImageFiltered sigma=10`；说明文字放在滤镜之外、圆角裁剪之内。
8. 修卡时踩到的新问题：`ClipRRect` 内的 `Stack` 若只有 Positioned 子节点，尺寸塌缩为 0，整卡被裁没（fix-v5.png 上说明卡消失）→ 加一个非 Positioned 基底 `SizedBox 500×150`。
9. 旋转后的 REVIEW 标签右下角越出 32px 安全边距约 3px → 左移 4px。

## 需求逐项核对（fix-v7.png / system-pulse.png 实际图像）

- 1280×800 画布、深底 `#0B1220`、安全边距 32、标题 `System Pulse` 44 号粗体 ✓
- 第一行三个等宽指标卡（各 389 宽，间距 24）：`USAGE 72%` / `LATENCY 148 ms` / `SUCCESS 99.2%`，文案 28 号 ✓
- 右上 LIVE 标签 96×36，与标题无重叠（标题在左、LIVE 在右端）✓
- 右下 REVIEW 标签 160×56，视觉逆时针 8°，白底 20%（像素采样为 20% 白与深底的合成值），文字不透明 24 号，四角完整可见 ✓
- 中央说明卡 500×150、圆角 24；两条彩色细条同时穿过卡片左右边界（细条 x∈[340,940]，卡片 x∈[390,890]）；**只模糊卡内背景**（卡外 rgb(60,187,248) 纯色锐利，卡内 rgb(39,97,136) 为模糊混合色），`Background-only blur` 文字清晰锐利、28 号 ✓
- 所有元素完整可见，无裁切、无遮挡 ✓

## 请求与迭代统计

- 渲染请求 9 次：4 次失败（真实报错，各保存错误 JSON）+ 5 次成功（fix-v4/v5/v6/v7 + 最终交付）。
- DSL 版本 9 个；语法修复迭代 3 次，完整视觉迭代 4 次（含基线查看）；看图 7 次（fix-v4/v5/v6/v7 + 最终图 + 局部像素核验）。
- 限流等待 0 秒，用户反馈等待 0 秒；请求耗时之和约 15.9 秒。

## 未解决事项

无。全部需求项满足，失败过程与依据完整留痕。
