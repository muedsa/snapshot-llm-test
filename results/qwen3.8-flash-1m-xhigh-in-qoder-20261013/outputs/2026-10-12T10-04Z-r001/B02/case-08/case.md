# case-08 · 社区物资柜 · 封条清单

**触点**：物资柜封条清单（100×67 mm） ｜ **尺寸** 600×400 px ｜ 印 100×67 mm ｜ **主作品** `final.png`（真实服务响应）
**完成标准**：`tmp/2026-10-12T10-04Z-r001/B02/work-plan.json` vv1（首次渲染前建立）

## 谁在什么时候用

开柜取用的志愿者与仓管。要完成的事：30 cm 内核对品名、数量、检查日期。实际观看环境：柜门贴纸，30 cm，弱光。

## 内容

- 10 项物资：名称/数量/状态色块
- 4 项待处理明细
- 最近检查日期与复检规则
- 封条与开封登记行

## 视觉选择

最小的一件：18 px 在这张 100 mm 宽的贴纸上等于 3 mm 字高，是 30 cm 阅读的地板。

## 与其他触点的关系

清单数量与 case-05 任务板上的「物资柜开封」任务同一台账。

## 实际自检

- 构建期布局审计：文本 28 段 / 形 29 个 · 重叠 0 · 出界 0 · 最小字号 18px。
- 服务渲染 2 次成功，逐版实际打开看图；版本与观察见 `tmp/2026-10-12T10-04Z-r001/B02/iterations.jsonl`。
- 数字一致性：与 `tmp/2026-10-12T10-04Z-r001/B02/data-snapshot.json` 同源，可跨触点互相核对（见 `touchpoint-map.json`）。
- 对比度：正文/大字按 WCAG 相对亮度在生成脚本内断言（`tide.assert_contrast`）。

## 素材情况

纯 DSL，无外部图像素材（B 赛道允许辅助素材，本件未使用）。

## 复现

```
python tmp/2026-10-12T10-04Z-r001/B02/case08_label.py
python tmp/2026-10-12T10-04Z-r001/_suite/scripts/render.py --dsl tmp/2026-10-12T10-04Z-r001/B02/case08.snapshot   --out outputs/2026-10-12T10-04Z-r001/B02/case-08/final.png --log tmp/2026-10-12T10-04Z-r001/B02/requests.jsonl   --req-id B02-08-final --task B02 --kind final
```
