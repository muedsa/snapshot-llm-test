# case-05 · 手机推送与到期提醒（750×1624 iOS 锁屏 + 通知中心）

## 触点定位

- 媒介：iPhone 锁屏（390 pt 逻辑宽，@2x=780，此处按设计稿 750×1624 出图）
- 阅读情境：口袋里的手机被点亮，用户在**非App内**、站立或行走、只有一两秒
- 设计任务：逾期这件事只有在小屏幕上被看见才会真的被处理。通知文案必须在三行内
  说完「哪件、欠几天、多少钱、下一步能点什么」，并把「续借已经用尽」诚实标出来。
- 与其他触点互校：在借 3 件与 case-04 小票条目一致；额度 3/3 与 case-02 卡面一致；
  归还时间窗与 case-03 触摸屏、case-01 导视一致（同一 `brand.hours` / `rules`）。

## 版面结构

| 区 | 内容 | 数据来源 |
| --- | --- | --- |
| 状态栏 | 09:41 / 信号 / 5G / 电量 | 界面惯例，非业务数据 |
| 时钟 | 09:41、10月10日 星期六 | `rules.today=2026-10-10`（星期由 date.weekday() 算出） |
| 通知 1（展开） | 逾期件、逾期天数、逾期费算式、额度、两个动作、归还时间窗 | `active_loans[角磨机]`、`rules.late_fee_per_day/max_active/return_point`、`brand.hours`、`brand.sites[1]` |
| 通知 2/3 | 到期提醒（还剩几天、可续借至、工具编号） | `active_loans` 未逾期两条的 `days_left/due/due_after_renew/tool` |
| 通知 4 | 本周活动 | `brand.programs[0]` 拆分、`programs[1]` |
| 在借清单 | 3 行：名称、编号、剩余/逾期、应还日与欠费 | `active_loans` + `categories` 配色 |
| 底部 | 全馆在借/可借、micro 页脚、虚构声明 | `summary.in_borrow_now/available_now`、`brand.fiction_notice` |

TextFit 自检：43 条文本，0 条溢出。

## 迭代记录（真实看图后修改）

| 版本 | 请求 | 看到的问题 | 改了什么 |
| --- | --- | --- | --- |
| v01 | `B02-v01-20261010T052701Z`（见「过程错误」） | 满幅牛皮纸噪点在 750px 手机上读成 JPEG 压缩残骸而不是壁纸，方块甚至从卡片之间透出来；「续借（本件已用尽）」下面那条删除线伸出圆角外，像渲染故障；「逾期中只有你这一件」是编造——全馆 `overdue_loans=364`；「另有 季度修理市集」中间多一个空格且语义像排期 | 换壁纸与按钮态；删掉删除线；改文案 |
| v02 | `B02-case-05-v02-20261010T053108Z` | 壁纸改为 `noise=0` + 竖向色带渐变（新增 `B.gradient_bands`，整数行铺满并向下压边 1px），逐行取样 200 行最大行差 0.59 亮度，无可见横纹；不可用按钮改为只压暗文字（0.26 白）不划线；底部提示改为「归还角磨机后你的额度可恢复 1 件」（由 `max_active=3` 与在借 3 件推出的算术）；活动正文改「常设还有：季度修理市集」。放大卡片左上角后发现新缺陷：1px 顶部高光线按整宽绘制，线头伸出圆角外悬在背景上 | 高光线内缩 |
| v03 | `B02-case-05-v03-20261010T053218Z` | 圆角处不再有线头（3× 放大复查），全图复查通过 | 提升为 final |

## 过程错误（如实记录）

- 本用例三次渲染都错传了 `--task`。`render.py` 的 `request_id = f"{task}-{version}-{stamp}"`
  并且日志写到 `tmp/<run_id>/<task>/requests.jsonl`：
  - v01 用 `--task B02 --version v01` → 请求号 `B02-v01-…`，丢了用例键（用例事件仍需唯一 ID）；
  - v02/v03 用 `--task B02-case-05 --version v02/v03` → 请求号正确（`B02-case-05-v02-…`），
    但日志被写进了新建的 `tmp/<run_id>/B02-case-05/requests.jsonl`，`task_id` 字段也因此写成
    `B02-case-05`、`dsl_version` 写成 `v02` 而不是 `case-05-v02`。
  处理：两条记录**原样**并入 `tmp/<run_id>/B02/requests.jsonl`（现 30 条、request_id 全唯一），
  原文件保留在 `tmp/<run_id>/B02/case-05/_misplaced-log/requests.jsonl`，未删除任何字节；
  请求体/响应头/原始响应副本本来就在 `case-05/requests/` 下，路径字段无需修正。
  正确调用姿势（case-01~04 用的）是 `--task B02 --version case-05-vNN`。后续用例改用该写法。
- 没有为「补一个正确请求号」而重渲一次同样的 DSL（那会是空转请求）；提升用的 v03 响应
  与 `final.png` 由 md5 校验一致（`eef98a8fc47eba752789f68b5709f59b`）。

## 交付物

- `final.png`（750×1624，服务原始响应字节）/ `final.snapshot`（同一请求 body 切出的完整 DSL，47397 字符）
- 过程：`tmp/<run_id>/B02/case-05/` 下 v01~v03 的 png/snapshot、`requests/`（请求体、响应头、原始响应）、
  `qa-v01a/b/c.png`、`qa-v02-seam.png`、`qa-v03-corner.png`（PIL 放大裁切，仅作看图证据，不是成品）
