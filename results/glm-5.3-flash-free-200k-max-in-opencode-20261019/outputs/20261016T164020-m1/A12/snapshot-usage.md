# A12 · responsive-system（四断点完整内容视觉系统）— 使用记录

题面：`tasks/A12-responsive-system/TASK.md`。同一活动内容（`inputs/content.json`）四个画布：360×800 / 768×1024 / 1440×900 / 1920×1080；必显字段（title/subtitle/date/time/location/cta/website + 6 卡 title/detail）逐字符完整、真实渲染、无裁切/拉伸/整图 Image。

## 实际产物（路径基准 = 本题输出根）

| 文件 | 说明 |
| --- | --- |
| `mobile.png` + `.snapshot` | 360×800 单列纵排（v02，77,124B） |
| `tablet.png` + `.snapshot` | 768×1024，2×3 卡网格（v02，96,082B） |
| `desktop.png` + `.snapshot` | 1440×900，3×2 卡网格（v02，104,263B） |
| `stage.png` + `.snapshot` | 1920×1080，3×2 等比放大（v02，123,813B） |
| `design-tokens.json` | 调色板/字阶（32/52/64/88 标题、16/18/20/22 正文、18/22/24/26 卡题）/间距规则/组件规则（rail、chip、CTA pill、card、index_dot、website 下划线、底部收边条）/层级与断点规则 |
| `content-map.json` | 76 条必显记录（19×4：字段名/源文=实显文本/文字盒/字号/complete）、card_index（C1–C6 → 逐画布网格位 + 盒）、textbox_overlap_audit（四画布全 pass）、required_fields_audit |
| `task-metrics.json` | renders 8（全 200）/ iterations 2 / views 2 |
| 过程 | `tmp/<run_id>/A12/`：build_a12.py（一份内容+tokens 生成四 DSL）、finalize_a12.py、crops；steps/ 4 张放大件 |

## 设计与合规

- **一套系统**：深蓝底 (#0E1526)+卡面 #1B2542+强调蓝/琥珀；组件词汇恒定（认可线 rail、元信息 chips、琥珀 CTA pill、索引圆点卡），断点仅重排：手机 meta 三行堆叠+卡 1×6；平板 chips 一行+2×3；桌面/大屏 3×2 等比放大。
- **字号合规**：手机正文/meta/detail 16、卡题 18、title 32；其余正文 20–22、卡题 22–26、主标题 52/64/88（≥40）。全图最小 16px（手机）/20px（其余），无更小文字。
- **边距**：手机 16、其余 32（大屏 48）；构版外延盒审查：网格底 766/943/819/972 均在 H−M 内；content-map 两两求交 **零重叠**。
- **不裁切/变形**：全部文字单行完整（fit 审查 WARN 0）；CTA 为文字 pill（无二维码）。
- **ID 政策**：卡片不印 C1–C6（题面允许），content-map 以输入顺序行优先定位映射（校验：平板 C1 r1c1、大屏 C6 r2c3）。

## 迭代链（2 rounds / 8 requests，无失败）

- s01 baseline：v01 四张逐张查看——发现平板底部留白偏空、桌面/大屏卡内文字重心偏上、手机卡6 底距 2px（构建期的 1px 拟合与手机 68px 超框.WARN 已在渲染前修掉，未产生失败请求）。
- v02 visual：平板网格下移+卡加高；非手机卡文字块 0.26→0.32×卡高；手机卡高 64。四张 v02 终审通过 → 定稿。

## 交付与证据

- 四 PNG 全部为真实服务响应并有同名 .snapshot；字族沿用本 run 前置真实字体查询（Inter + Noto Sans CJK SC）。
- 审查方法与限制：content-map 盒为构版坐标+估宽外延（方法已记录），逐张实际看图核对（整图 8 次最终视图 + 放大件）；必显字段以源文=实显逐字符比对脚本核验。
- 无 429/认证/持续故障。
