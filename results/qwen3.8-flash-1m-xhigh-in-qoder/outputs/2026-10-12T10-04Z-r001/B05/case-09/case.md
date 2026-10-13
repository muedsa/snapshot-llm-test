# case-09 · A4 随访摘要

- 设备/画布：794×1123（96dpi A4）
- 旅程节点：药师确认后的纸质留档，家属与药师签字
- 服务请求：`B05-case09-print-v7`（200，2.579s，server render;dur=229.1, total;dur=232.5，X-Request-Id `33d58f8a-c5f9-4f3d-b1bf-fb0777b7c2c0`）
- 响应字节：192,619 B，sha256 `b6e82b6f312c646c…`
- 渲染次数：7（final, v1, v2, v3, v4, v7, verify）
- DSL：`case-09/final.snapshot`

## 这一屏解决什么

黑白可打印：状态全部用文字，不依赖颜色

## 屏上的具体信息

- A4 单页：清单 + 近 7 天记录 + 需药师确认事项 + 双方签字
- 8 列表格，最长药名 11 字完整显示，不被截断
- 状态列全部用文字，黑白打印不依赖颜色
- 页脚标注“第 1 页 / 共 1 页 · 药盒 v0.9 导出”

## 自检

- 生成器审计：overlap_n=0、outside_n=0、spill_n=0、truncated_n=0、below_min_font_n=0（107 段文字 / 13 个图形）
- 数字全部来自 `b05data.py` 生成的 data.json，与其他九屏同源
- final.png 为服务原始响应字节，未做后处理
- 实际看图：见 `iterations.jsonl` 的 view 事件

## 未验证的假设

- A4 打印在真实激光打印机上的灰度表现未实测
