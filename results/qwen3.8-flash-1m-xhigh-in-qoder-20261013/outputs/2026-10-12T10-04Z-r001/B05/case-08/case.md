# case-08 · 药师交接端

- 设备/画布：桌面 1440×900
- 旅程节点：复诊时把家庭药箱交给社区药师核对
- 服务请求：`B05-case08-pharmacist-v7`（200，2.579s，server render;dur=229.1, total;dur=232.5，X-Request-Id `33d58f8a-c5f9-4f3d-b1bf-fb0777b7c2c0`）
- 响应字节：227,116 B，sha256 `66e65c0a063cb52d…`
- 渲染次数：9（final, v1, v2, v3, v4, v5, v6, v7, verify）
- DSL：`case-08/final.snapshot`

## 这一屏解决什么

把“未采集字段”显式列出，避免打印件看起来比实际完整

## 屏上的具体信息

- 5 项交接清单：药品、服用者、处方来源、效期、剩余、状态
- 状态计数 全部 5 / 待药师确认 2 / 已核 3，与效期分级同源
- “未采集字段”显式列出批号、生产厂家、医保编码
- 右侧 A4 预览为 12–15px 缩小示意，真实排版见 case-09

## 自检

- 生成器审计：overlap_n=0、outside_n=0、spill_n=0、truncated_n=0、below_min_font_n=0（65 段文字 / 30 个图形）
- 数字全部来自 `b05data.py` 生成的 data.json，与其他九屏同源
- final.png 为服务原始响应字节，未做后处理
- 实际看图：见 `iterations.jsonl` 的 view 事件

## 未验证的假设

- 药师是否接受“未采集字段”这种显式留白，未做访谈
