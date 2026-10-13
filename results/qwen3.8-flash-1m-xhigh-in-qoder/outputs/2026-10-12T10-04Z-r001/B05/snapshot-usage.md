# B05 药盒 · Snapshot 使用记录与踩坑

本题 71 次 `/snapshot` 请求全部 200，无失败、无重试；10 份 DSL 共渲染 71 次
（每题最多的是 case-04 与 case-08，各 9 次）。请求全部经
`tmp/<run_id>/_suite/scripts/render.py`（curl 传输）发出，逐条记录在
`tmp/<run_id>/B05/requests.jsonl`，含 X-Request-Id、server-timing 与响应字节路径。

## 1. 用到的 DSL 能力

十屏全部是类 DOM 结构：`Snapshot > Stack > Positioned > Container/Text`，
外加少量 `Transform`（旋转 1px 高的 Container 当作任意方向的细线/分隔线）。

| 能力 | 用法 | 注意 |
| --- | --- | --- |
| `Container` `borderRadius` + `boxShadow="0 6 18 #18202814"` | 所有卡片 | 阴影是自定义属性，四值 `x y blur color`，颜色带 alpha |
| `Container` `border="1 SOLID #DCD6C8"` | 描边胶囊、离线徽章 | 线宽 > 圆角时服务返回 500，bkit 已在构造前拦截 |
| `Text` `overflow="ELLIPSIS" maxLines="1"` | 有宽度预算的列 | 服务端截断不会通知调用方，因此 bkit 先用测量模型自行截断并计数 |
| `Transform` + `matrix2d(cos, sin)` | 时间线分隔线、周分隔线 | 必须同时给 `matrix` 与 `alignment`；`origin` 只接受 `"(x,y)"` |
| `Positioned` `left/top/width` | 全部定位 | `Positioned` 必须是 `Stack` 的直接子节点；`width` 只用于防裁切，不改变文本度量 |

字体固定 `Noto Sans CJK SC` 与 `Noto Sans Mono CJK SC`（数字列），由
`GET /fonts` 的实测清单选出；未使用任何外部素材、图片或表情符号。

## 2. 文本度量模型（实测，不是文档值）

| 量 | 值 | 来源 |
| --- | --- | --- |
| CJK 前进宽度 | 1.00 em | 11 字药名 @19px bold 实测 206px |
| 拉丁/数字 | 0.62 em（比例）/ 0.52 em（等宽） | 日期列、时间列逐像素核对 |
| 行距 | 1.46 em | 两行文字基线差 36px @17px 反推（含 4px gap） |
| 字形在 em 框内的下沉 | ≈ +6px @17px | 卡片边界与文字带逐像素比对 |
| 粗体 CJK | 仍 ≈1.0 em | 早期为防裁切引入的 ×1.14 只用于绘制框，不用于重叠判定 |

这套模型让「文字会不会溢出卡片」在**送服务之前**就能算出来；本题三次真实溢出
（case-03 错误提示、case-04 描述行、case-10 三步说明）全部先由模型报出，再由渲染确认。

## 3. 本题给 bkit 新增的三项自检

1. `Sheet.panel()` + `audit()["spill_n"]`：文字必须留在它所属卡片内。
   触发实例：case-04 描述第二行落在 409.6–427.6，而卡片止于 420。
2. `Sheet.text(maxw=)` + `audit()["truncated_n"]`：预算宽度会截断，但截断不是免费——
   case-08 的「372 滴」被 44px 预算截成「372…」，靠这项计数才发现。
3. `Sheet.clip_line()`：引导线长度受预算约束，返回实际终点，避免线与相邻文字重叠。

三项都断言为 0 才写文件，因此不存在「带缺陷的定稿」。

## 4. 踩坑清单

| 现象 | 根因 | 处理 |
| --- | --- | --- |
| 审计 0 重叠，渲染却明显压字 | 审计只查文字两两与画布，不查卡片 | 新增 panel/spill |
| 表格列「看起来挨在一起」 | 列间距按 `tw()` 留了 1px | 用像素回读量出真实字形右沿，重排列位 |
| 7 天格全绿却写「漏 4 次」 | 网格窗口与统计窗口不同源 | 网格改 14 天，与依从率同窗口 |
| 屏上写 94.1%，数据算出 92.9% | 统计是手写的 | 改为 `data.json → per_person`，并加断言 |
| 同一药在警报页 85 天、打印页 535 天 | 印刷效期与开封后效期混用 | 有效效期成为唯一口径，印刷值另存 `printed_expiry_days` |
| 11 字药名被 `name[:9]` 截半 | 列宽按截断后估算 | 放宽列位让 11 字完整显示，并禁止截断 |
| A4 缩略预览的 12–15px 文字被最小字号拦下 | 预览本来就是缩小示意，不是正文 | 以 `ignore_roles=("preview",)` 豁免该角色，并在屏上写明「预览为缩小示意，真实排版见第 09 屏」 |
| 颜色分级两屏不一致 | 警报页三级、冰箱卡两级 | 统一 7/30/90 三级 |
| 「漏服不要补吃双倍」 | 属于用药指示，越过产品边界 | 改为「以说明书或药师意见为准」 |
| 「本条依据等级：通用建议」 | 暗示做过指南查证，实际未查 | 改为「未查证权威清单」 |
| 界面里出现「已写入 product-brief」 | 交付物自指，破坏产品真实感 | 移到 case.md 与作品集说明 |

## 5. 服务侧观察

- 服务端渲染耗时 p50 226ms、p90 572ms，
  最小 22.7ms（手表小画布）；最大 1674.6ms 出现在本题第一次请求；客户端总耗时 162.1s / 71 次。
- 缓存：69 miss、2 hit。两次 hit 出现在同一 DSL 的重复渲染上，
  命中时 `server_timing` 只有 `cache;desc=hit, total;dur=…`，不带 `render;dur`，
  因此 69 条参与分位数统计（与 B04 的结论一致）。
- 本题没有触发 400/409/500：DSL 保守（无滤镜、无路径、无表情符号），
  元素最多的一屏是 case-07（约 310 个元素），远低于 4096 上限。

## 6. 可复现步骤

```
python tmp/<run_id>/B05/b05data.py         # data.json（含 9 条一致性断言）
python tmp/<run_id>/B05/b05pages.py all    # 10 份 DSL + 六项几何自检
python tmp/<run_id>/_suite/scripts/render.py --dsl ... --out ... --log ...
python tmp/<run_id>/B05/archive.py         # 校验字节并归档 case-NN/{final.png,final.snapshot,case.md}
python tmp/<run_id>/B05/make_docs.py       # portfolio / gallery / metrics / 日志
```

`archive.py` 会断言：归档 PNG 的 `request_file` 就是当前 DSL 文件，且响应字节以
`\x89PNG` 开头——即最终图确实是服务对该 DSL 的原始响应，不是后处理产物。

## 7. 与前后题的关系

- 复用 A01 抓取的本地文档缓存与 `GET /fonts` 结果，未新增文档请求。
- 复用 B03 建立的 bkit 与「先探针后作图」的习惯；本题反向把
  panel/truncated 两项检查补回 bkit，后续题（B06）直接受益。
- 与 B04 的统计口径一致：请求耗时与墙钟分开记，缓存命中的响应不计入渲染分位数。
