# case-10 · 过期药处置

- 设备/画布：iPhone 13 · 390×844
- 旅程节点：阿托伐他汀钙片只剩 7 天效期，剩下 3 片怎么办
- 服务请求：`B05-case10-disposal-v7`（200，2.579s，server render;dur=229.1, total;dur=232.5，X-Request-Id `33d58f8a-c5f9-4f3d-b1bf-fb0777b7c2c0`）
- 响应字节：120,247 B，sha256 `f16ade9488f11558…`
- 渲染次数：8（final, final2, v1, v2, v3, v4, v7, verify）
- DSL：`case-10/final.snapshot`

## 这一屏解决什么

只给通用三步，并声明本系统不含当地回收政策数据

## 屏上的具体信息

- 顶部只锁定 1 项：M3 效期 7 天、剩 3 片
- 三步处置每步都给出“为什么”，并声明未查证权威清单
- 结尾明确本系统不含当地回收政策数据

## 自检

- 生成器审计：overlap_n=0、outside_n=0、spill_n=0、truncated_n=0、below_min_font_n=0（27 段文字 / 17 个图形）
- 数字全部来自 `b05data.py` 生成的 data.json，与其他九屏同源
- final.png 为服务原始响应字节，未做后处理
- 实际看图：见 `iterations.jsonl` 的 view 事件

## 未验证的假设

- 处置步骤未查证权威指南，仅为通用做法
