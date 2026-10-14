# case-03 · 潮水位 · 实时预警页

**触点**：手机 App 预警页 ｜ **尺寸** 390×844 px ｜ 手机竖屏 1x ｜ **主作品** `final.png`（真实服务响应）
**完成标准**：`tmp/2026-10-12T10-04Z-r001/B02/work-plan.json` vv1（首次渲染前建立）

## 谁在什么时候用

已安装小程序的居民，夜里在家看手机。要完成的事：知道自家门口现在多深、会不会涨、现在该做什么。实际观看环境：手机竖屏，暗光，30 cm。

## 内容

- 门口水位大字与涨速
- 24 小时曲线 + 三条阈值线
- 当前等级行动卡
- 最近集合点与步行时间
- 两项待接任务
- 底部四标签

## 视觉选择

同一份站点数据在 390 pt 小屏上的密度版本：唯一的大字是决定性的那个数。

## 与其他触点的关系

曲线数据与海报、大屏、制图板同源（data.STATIONS）；行动文案来自同一 LEVELS 表。

## 实际自检

- 构建期布局审计：文本 42 段 / 形 66 个 · 重叠 0 · 出界 0 · 最小字号 11px。
- 服务渲染 4 次成功，逐版实际打开看图；版本与观察见 `tmp/2026-10-12T10-04Z-r001/B02/iterations.jsonl`。
- 数字一致性：与 `tmp/2026-10-12T10-04Z-r001/B02/data-snapshot.json` 同源，可跨触点互相核对（见 `touchpoint-map.json`）。
- 对比度：正文/大字按 WCAG 相对亮度在生成脚本内断言（`tide.assert_contrast`）。

## 素材情况

纯 DSL，无外部图像素材（B 赛道允许辅助素材，本件未使用）。

## 复现

```
python tmp/2026-10-12T10-04Z-r001/B02/case03_app.py
python tmp/2026-10-12T10-04Z-r001/_suite/scripts/render.py --dsl tmp/2026-10-12T10-04Z-r001/B02/case03.snapshot   --out outputs/2026-10-12T10-04Z-r001/B02/case-03/final.png --log tmp/2026-10-12T10-04Z-r001/B02/requests.jsonl   --req-id B02-03-final --task B02 --kind final
```
