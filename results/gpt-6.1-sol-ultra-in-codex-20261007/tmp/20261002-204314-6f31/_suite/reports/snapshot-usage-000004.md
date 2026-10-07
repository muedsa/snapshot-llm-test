# Snapshot 全套实际使用报告

运行：20261002-204314-6f31；生成时间：2026-10-03T17:01:00.247Z；配置：all；状态：in_progress。
当前题：A06；轮次：无；用例：无。
实际输出目录：D:/workspaces/gpt-6.1-sol-ultra/outputs/20261002-204314-6f31。实际临时目录：D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31。

状态数量：completed 5，in_progress 0，partial 0，blocked 0，pending 25。
已登记最终 PNG 6；独立创作用例 0；实际渲染请求 14（成功 10，失败 4）；文档请求 8；其他服务请求 1；完整视觉迭代 4；未完成视觉迭代 0；实际查看记录 28。

## 真实文档与 DSL 应用

下面的实际阅读/应用来自执行者保存的 shared-applications 记录；单纯取得文档响应不被当作已经阅读或应用。相同缓存跨题复用不新增 HTTP 请求。

[shared-applications-000001](../../../tmp/20261002-204314-6f31/_suite/shared-applications-000001.json)：Shared preparation genuinely read and applied by root during A01。
- shared-doc-000001：https://open-snapshot.muedsa.com/ai-guide.md。UTF-8 plain text POST /snapshot, real binary response, checked status/content-type/signature; no errorImage option. 对应实际成功请求已保留。
- shared-doc-000003：https://snapshot.muedsa.com/guides/parser/。One Snapshot root widget, correct case-sensitive DSL labels, CDATA special text, no HTML entity assumptions. 对应实际成功请求已保留。
- shared-doc-000004：https://snapshot.muedsa.com/reference/parser-tags/。Container decoration and shape, finite fixed canvas, Positioned axes, Text/Raw, column-major16value Transform matrices. 对应实际成功请求已保留。
- shared-doc-000005：https://snapshot.muedsa.com/guides/layout/。Finite parent constraints, Stack EXPAND, separate layout/painting clipping; absolute chart/table geometry. 对应实际成功请求已保留。
- shared-doc-000006：https://open-snapshot.muedsa.com/openapi.yaml。Read interface and error/retry response definitions and Server-Timing semantics. No retries occurred in A01. 对应实际成功请求已保留。
- 字体 shared-fonts-000001：Inter, Noto Sans CJK SC；实际请求核验 成功。

[shared-applications-000002](../../../tmp/20261002-204314-6f31/_suite/shared-applications-000002.json)：Additional official documentation actually fetched/read by root for A03。
- shared-request-000001：https://snapshot.muedsa.com/widgets/painting/backdrop-filter/。Confirmed backdrop filter reads already drawn background. Outer ClipRRect constrains region; foreground Text remains outside blur effect on background. 对应实际成功请求已保留。
- shared-request-000002：https://snapshot.muedsa.com/widgets/layout/transform/。Confirmed Transform only changes paint coordinates, not layout. Matrix column-major, center alignment, y-down CCW rotation and rotated bounding box must be checked. 对应实际成功请求已保留。

[shared-applications-000003](../../../tmp/20261002-204314-6f31/_suite/shared-applications-000003.json)：A03 background-only blur findings actually verified in real full images and crops。

## 缓存与真实请求证据

|范围|请求 ID|类型|HTTP|原始响应|
|---|---|---|---|---|
|shared|shared-doc-000002|document|200|[原始响应](../../../tmp/20261002-204314-6f31/_suite/shared-doc-000002-response.bin)|
|shared|shared-doc-000001|document|200|[原始响应](../../../tmp/20261002-204314-6f31/_suite/shared-doc-000001-response.bin)|
|shared|shared-fonts-000001|fonts|200|[原始响应](../../../tmp/20261002-204314-6f31/_suite/shared-fonts-000001-response.bin)|
|shared|shared-doc-000003|document|200|[原始响应](../../../tmp/20261002-204314-6f31/_suite/shared-doc-000003-response.bin)|
|shared|shared-doc-000004|document|200|[原始响应](../../../tmp/20261002-204314-6f31/_suite/shared-doc-000004-response.bin)|
|shared|shared-doc-000006|document|200|[原始响应](../../../tmp/20261002-204314-6f31/_suite/shared-doc-000006-response.bin)|
|shared|shared-doc-000005|document|200|[原始响应](../../../tmp/20261002-204314-6f31/_suite/shared-doc-000005-response.bin)|
|shared|shared-request-000001|document|200|[原始响应](../../../tmp/20261002-204314-6f31/_suite/requests/shared-request-000001/response.txt)|
|shared|shared-request-000002|document|200|[原始响应](../../../tmp/20261002-204314-6f31/_suite/requests/shared-request-000002/response.txt)|

## 实际工具与方法

- Node.js numeric calculations and DSL generation。
- PowerShell independent arithmetic review。
- HTTP fetch requests preserving raw response bytes。
- view_image actual service images。
- SHA-256 final byte identity checks。
- immutable progress snapshots。
- A02/shared：PIL via inspect-image.py；Create immutable crop of real wide PNG solely for actual dense-region visual QA; no final postprocessing；证据 ID A02-tool-000001。
- A03/shared：PIL via inspect-image.py；Actual visual crop QA of background-only blur; immutable derivative, no final edits；证据 ID A03-tool-000001。
- A03/shared：PIL via inspect-image.py；Actual same-region crop comparison of SRC blend trial, no final postprocessing；证据 ID A03-tool-000002。
- A03/shared：PIL via inspect-image.py；Final same-region real background-only blur QA crop; never modifies final；证据 ID A03-tool-000003。

所有最终图片保留原服务 PNG 字节并与完整同名 .snapshot 配对；本报告生成器读取留痕，不代替执行者的实际图像查看。

## 逐题状态与产物

|任务|状态|最终图/独立用例|渲染成功/失败|DSL/看图|完整/未完视觉迭代|入口|
|---|---|---|---|---|---|---|
|A01|completed|1/0|2/0|3/3|1/0|[单题报告](../A01/snapshot-usage.md)|
|A02|completed|2/0|2/0|2/7|0/0|[单题报告](../A02/snapshot-usage.md)|
|A03|completed|1/0|4/4|8/14|3/0|[单题报告](../A03/snapshot-usage.md)|
|A04|completed|1/0|1/0|1/3|0/0|[单题报告](../A04/snapshot-usage.md)|
|A05|completed|1/0|1/0|1/1|0/0|[单题报告](../A05/snapshot-usage.md)|
|A06|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A07|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A08|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A09|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A10|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A11|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A12|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A13|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A14|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A15|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A16|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A17|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A18|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A19|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A20|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A21|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A22|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A23|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|A24|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|B01|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|B02|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|B03|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|B04|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|B05|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|
|B06|pending|0/0|0/0|0/0|0/0|单题报告（文件尚未生成）|

## 可观察问题、修复与验证

- A01：Conclusion lines clipped in actual render despite correct text strings. 修改：Split into separate positioned text widgets with taller per-line boxes. 验证：Real image tool comparison showed all final conclusion lines complete.；[记录](../../../tmp/20261002-204314-6f31/_suite/shared-applications-000001.json)。
- A01：Amount unit touched highest tick in actual baseline. 修改：Moved the unit label away from tick labels. 验证：Viewed corrected actual PNG and published final output PNG.；[记录](../../../tmp/20261002-204314-6f31/_suite/shared-applications-000001.json)。
- A03：ImageFiltered blurred text; reconstructed BackdropFilter with SRC_OVER preserved sharp original stripes beneath a glow. 修改：ClipRRect-constrained BackdropFilter SRC trial; opaque foreground text. 验证：；[记录](../../../tmp/20261002-204314-6f31/_suite/shared-applications-000003.json)。
- A03：SRC removed sharp stripes but with Snapshot.background only, card became bright and reduced white-text contrast. 修改：Explicitly paint opaque root Container #0B1220 before stripes/filter. 验证：v008 full real PNG and same-region actual crop show dark soft interior, sharp outside and clear foreground text.；[记录](../../../tmp/20261002-204314-6f31/_suite/shared-applications-000003.json)。
- A03：4 real400 errors: padding format, missing matrix, Positioned parent, infinite layout. 修改： 验证：Preserved original842bytes exactly, every submitted DSL and raw JSON response; later successful PNG was still visually wrong and was not accepted.；[记录](../../../tmp/20261002-204314-6f31/_suite/shared-applications-000003.json)。
- A01/A01-v003：Split conclusion into independent positioned lines with 32/35px boxes; moved amount unit; clarified monthly conversion title. 比较结果：v002 clipped the second conclusion line and final recommendation; v003 shows all five lines in the card and the unit separately.；前后实际查看事件 A01-view-000001 → A01-view-000002。
- A03/A03-system-pulse-v006：Restore documented fonts, finite exact canvas, required cards, LIVE, REVIEW alpha/rotation/bbox; replace ImageFiltered with cropped BackdropFilter and crossing stripes. 比较结果：Compared with actual v005, title/font/metrics/labels/placement/alpha and foreground clarity now correct; actual v006 crop reveals persistent original sharp stripe centreline under default SRC_OVER. Not yet final.；前后实际查看事件 A03-view-000001 → A03-view-000002。
- A03/A03-system-pulse-v007：BackdropFilter blendMode SRC; title margin exactly32. 比较结果：Real same-region crop confirms sharp residual removed, but readback/background now pale and white text contrast too low. Further real backdrop painting required; not accepted.；前后实际查看事件 A03-view-000003 → A03-view-000005。
- A03/A03-system-pulse-v008：Draw opaque #0B1220 root Container before stripes and confined SRC BackdropFilter. 比较结果：Only changed painted root background. Actual same-region image recovers deep backdrop, no sharp interior stripes, bright white text remains clearly legible; all other restored elements unchanged and pass whole-image review.；前后实际查看事件 A03-view-000005 → A03-view-000007。

真实失败响应：
- A03-request-000001 HTTP 400：{"code":"PARSE_ERROR","message":"Attr [padding] value format error at position 92 near: \"png\">\r\n  <Container padding=\"24 32\" borderRadius=\"24\">\r\n   ","requestId":"535ce32b-a7ce-4221-b95b-0f8bb665ee20"}；[保留响应](../../../tmp/20261002-204314-6f31/A03/requests/A03-request-000001/response.json)。
- A03-request-000002 HTTP 400：{"code":"PARSE_ERROR","message":"Attr [matrix] must not be null at position 475 near:     <Spacer flex=\"1\"/>\r\n      <Transform rotate=\"-8\"><Contai","requestId":"24d7d1b4-18a0-42d9-a5d6-48e3dddf1171"}；[保留响应](../../../tmp/20261002-204314-6f31/A03/requests/A03-request-000002/response.json)。
- A03-request-000003 HTTP 400：{"code":"RENDER_ERROR","message":"renderBox.parentData must be StackParentData","requestId":"c1d213e5-2106-4c38-9b88-effc1d33bdd1"}；[保留响应](../../../tmp/20261002-204314-6f31/A03/requests/A03-request-000003/response.json)。
- A03-request-000004 HTTP 400：{"code":"RENDER_ERROR","message":"Layout size is infinite","requestId":"0230fe45-0342-4266-a22b-15681a3b7375"}；[保留响应](../../../tmp/20261002-204314-6f31/A03/requests/A03-request-000004/response.json)。

## 三轮预置与复用范围

A21/A22按第一轮归档后再执行第二、第三轮。轮次需求可提前访问，此模式不声称隐藏反馈盲测。每轮图像、DSL、报告、指标与变化证据分别归档；总指标只累计各题顶层加 shared，轮次/用例明细不再次相加。

## 总审查与剩余事项

Root has actually reviewed final A01–A05 images. Subsequent tasks remain pending.

尚未完成：A06 pending、A07 pending、A08 pending、A09 pending、A10 pending、A11 pending、A12 pending、A13 pending、A14 pending、A15 pending、A16 pending、A17 pending、A18 pending、A19 pending、A20 pending、A21 pending、A22 pending、A23 pending、A24 pending、B01 pending、B02 pending、B03 pending、B04 pending、B05 pending、B06 pending。
- A06–A24 and B01–B06 remain to execute; full-suite review pending.。

恢复检查点：[最新不可覆盖状态快照](../../../tmp/20261002-204314-6f31/_suite/checkpoints/state-000032.json)。恢复同一运行时沿用 20261002-204314-6f31，核对实际产物与日志后从未完成处继续。

## 真实消耗与计量边界

总墙钟起点：2026-10-02T12:43:45.012Z；结束：仍在执行；当前墙钟 101835.237 秒。
实际请求耗时之和（shared 加每题日志）：72.1433619 秒；此值不等于总墙钟。
真实 token、图像输入计费与金额：null。原因：The tools/service did not provide actual model token, image input, or billing consumption for this run.
完整消费汇总：[task-metrics.json](task-metrics.json)。已下载缓存、测试夹具与仅复用文档不作为新真实服务请求累计。
