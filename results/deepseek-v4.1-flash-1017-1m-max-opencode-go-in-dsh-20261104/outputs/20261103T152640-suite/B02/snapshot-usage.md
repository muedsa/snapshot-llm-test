# B02 · 一个自选项目的完整视觉生态 — Snapshot 使用与自检报告

- 状态：**completed**
- run_id：`20261103T152640-suite`
- 输出目录：`outputs/20261103T152640-suite/B02/`（path_base: suite_root）
- 临时目录：`tmp/20261103T152640-suite/B02/`
- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`，`text/plain` 请求体）

## 1. 任务与交付

为自拟的城市夜跑社群「夜巡跑团」建立十件触点的视觉生态：招新海报、小程序首页、路线图、号码布、月度日程卡、完赛证书、社交故事卡、补给站指示牌、会员卡、年度回顾。覆盖认知→了解→参与→现场→反馈→留存的完整旅程，共用一套颜色/字号/栅格与三箭头标志，但每件的密度与尺寸按观看距离重新设计。

| 文件 | 说明 |
|---|---|
| [case-01/final.png](case-01/final.png) | 招新海报 |
| [case-02/final.png](case-02/final.png) | 小程序首页 |
| [case-03/final.png](case-03/final.png) | 路线图 |
| [case-04/final.png](case-04/final.png) | 号码布 |
| [case-05/final.png](case-05/final.png) | 月度日程卡 |
| [case-06/final.png](case-06/final.png) | 完赛证书 |
| [case-07/final.png](case-07/final.png) | 社交故事卡 |
| [case-08/final.png](case-08/final.png) | 补给站指示牌 |
| [case-09/final.png](case-09/final.png) | 会员卡 |
| [case-10/final.png](case-10/final.png) | 年度回顾 |
| [case-01/final.snapshot](case-01/final.snapshot) | 对应 DSL |
| [case-02/final.snapshot](case-02/final.snapshot) | 对应 DSL |
| [case-03/final.snapshot](case-03/final.snapshot) | 对应 DSL |
| [case-04/final.snapshot](case-04/final.snapshot) | 对应 DSL |
| [case-05/final.snapshot](case-05/final.snapshot) | 对应 DSL |
| [case-06/final.snapshot](case-06/final.snapshot) | 对应 DSL |
| [case-07/final.snapshot](case-07/final.snapshot) | 对应 DSL |
| [case-08/final.snapshot](case-08/final.snapshot) | 对应 DSL |
| [case-09/final.snapshot](case-09/final.snapshot) | 对应 DSL |
| [case-10/final.snapshot](case-10/final.snapshot) | 对应 DSL |
| [project-brief.md](project-brief.md) | 项目简报 |
| [design-system.json](design-system.json) | 设计系统 |
| [touchpoint-map.json](touchpoint-map.json) | 触点映射 |
| [portfolio.json](portfolio.json) | 作品集数据 |
| [portfolio.md](portfolio.md) | 作品集说明 |
| [gallery.md](gallery.md) | 画廊 |
| [task-metrics.json](task-metrics.json) | 本题指标 |
| [snapshot-usage.md](snapshot-usage.md) | 本报告 |

## 2. 需求逐项核对

| 要求 | 证据 | 结论 |
|---|---|---|
| 至少 10 件独立完整主作品 | 十件，介质与尺寸各不相同 | 通过 |
| 项目像真实项目一样清楚 | project-brief 写明社群运作方式与四类真实问题 | 通过 |
| 十件各承担实际任务 | touchpoint-map 逐件写使用者需求与渠道 | 通过 |
| 能看出是同一项目 | 共用底色、荧光强调、三箭头标志与三档字号 | 通过 |
| 每件适合其内容与观看距离 | 手机 390px、展板 1600px、指示牌 900×1200 分别调密度 | 通过 |
| 可复用设计规则 | design-system.json 记录颜色/字号/栅格/组件 | 通过 |
| 全部由 DSL 制作并经真实服务渲染 | 十次 POST 全部 200 | 通过 |
| 逐件实际查看并修正 | 十件全部打开，四件返工 | 通过 |

## 3. 实际视觉自检记录

每张最终图都由视觉工具实际打开查看；以下为查看对象、观察与处置。

| 图像 | 观察 | 处置 |
|---|---|---|
| case-01 海报 | 首版标志被裁 | 改为独立裁剪后通过 |
| case-02 小程序 | 首版数字与按钮压字 | 重排后通过 |
| case-03 路线图 | 首版上半部空、标签压线 | 补街道/江面、标签同基线后通过 |
| case-04 号码布 | 大号码与二维码清晰 | 通过 |
| case-05 日程卡 | 八行日程、类型色条 | 通过 |
| case-06 证书 | 浅底证书、四宫格成绩 | 通过 |
| case-07 故事卡 | 首版下半部空 | 补提醒清单后通过 |
| case-08 指示牌 | 远读字号与物资列表 | 通过 |
| case-09 会员卡 | 横版卡片与点阵码 | 通过 |
| case-10 年度回顾 | 四宫格 + 月度柱 + 路线排行 | 通过 |

## 4. 设计与排版决策

- 同一套规则要在 390px 手机和 1600px 展板都成立：固定三档字号、固定 8px 栅格，只改密度。
- 荧光青柠只在每张图出现 3 处以内，保证「夜里的一道光」这个概念的稀缺性。
- 现场物料（号码布、指示牌）把字号提到 20px 以上并加大对比，牺牲信息量换可读性。

## 5. DSL 能力与文档应用

- 标志用三个独立的 44×44 ClipPath 叠放，避免单个容器裁剪掉整体。
- 路线图的折线用旋转长条拼接，节点用带描边的圆点覆盖线头。
- 十件共用同一组颜色常量与字号档位，改一处即可整体换肤。

## 6. 实际问题与修复

| 问题 | 原因/判断 | 修复与验证 |
|---|---|---|
| 标志三箭头被裁 | 路径带 i*34 偏移但容器只有 44 宽 | 改为每个 V 独立容器与局部路径 |
| 小程序页数字与单位重叠 | 「km」固定在 x=120，44px 数字更宽 | 单位右移到 160 |
| 底部按钮压住活动卡 | 三张卡按 82px 间距排到 772px | 卡高与间距压缩，按钮下移 |
| 路线图标签压在线上 | 标签跟随各点 y+26 | 统一到 y=548 基线 |
| 故事卡下半部空 | 时间线只到 1080px | 补三条当晚提醒 |
| 海报底部条纹压网址 | 条纹从 1160 起 | 下移到 1230 |

## 十个触点

- case-01 · 招新海报 · awareness · 1080×1350
- case-02 · 小程序首页 · usage · 390×844
- case-03 · 路线图 · usage · 1600×900
- case-04 · 号码布 · event · 800×600
- case-05 · 月度日程卡 · planning · 1080×1350
- case-06 · 完赛证书 · feedback · 1400×1000
- case-07 · 社交故事卡 · reminder · 1080×1920
- case-08 · 补给站指示牌 · event · 900×1200
- case-09 · 会员卡 · retention · 1000×600
- case-10 · 年度回顾 · feedback · 1200×1600
- 请求 24 次（成功 24），看图 10 次，墙钟 515.0 秒

## 7. 过程文件

| 路径（相对总任务根） | 说明 |
|---|---|
| `outputs/20261103T152640-suite/B02/case-01/final.png` | 触点 |
| `outputs/20261103T152640-suite/B02/case-02/final.png` | 触点 |
| `outputs/20261103T152640-suite/B02/case-03/final.png` | 触点 |
| `outputs/20261103T152640-suite/B02/case-04/final.png` | 触点 |
| `outputs/20261103T152640-suite/B02/case-05/final.png` | 触点 |
| `outputs/20261103T152640-suite/B02/case-06/final.png` | 触点 |
| `outputs/20261103T152640-suite/B02/case-07/final.png` | 触点 |
| `outputs/20261103T152640-suite/B02/case-08/final.png` | 触点 |
| `outputs/20261103T152640-suite/B02/case-09/final.png` | 触点 |
| `outputs/20261103T152640-suite/B02/case-10/final.png` | 触点 |
| `outputs/20261103T152640-suite/B02/project-brief.md` | 项目简报 |
| `outputs/20261103T152640-suite/B02/design-system.json` | 设计系统 |
| `outputs/20261103T152640-suite/B02/touchpoint-map.json` | 触点映射 |

## 8. 未解决事项

- 无。所有指定交付已生成、实际渲染并逐图查看。
