$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$os   = Join-Path $root 'outputs\run-20261002-220723-mimo\_suite'
$ts   = Join-Path $root 'tmp\run-20261002-220723-mimo\_suite'
$enc  = New-Object System.Text.UTF8Encoding($false)

$statePath = Join-Path $os 'suite-state.json'
if ([IO.File]::ReadAllText($statePath, [Text.Encoding]::UTF8).Contains('"id":  "B03",') -eq $false) { }
$raw = Get-Content $statePath -Raw -Encoding UTF8
$j = $raw | ConvertFrom-Json
$b03 = $j.tasks | Where-Object { $_.id -eq 'B03' }
$b04 = $j.tasks | Where-Object { $_.id -eq 'B04' }
if ($b03.status -eq 'completed') { throw 'B03 already completed - refusing to overwrite' }

$now = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss+08:00')

# ---------- artifacts ----------
$art = @()
$top = 'outputs/run-20261002-220723-mimo/B03'
foreach ($f in @('portfolio.json','portfolio.md','technique-notes.md','gallery.html','snapshot-usage.md','task-metrics.json')) {
  $art += "$top/$f"
}
for ($i = 1; $i -le 10; $i++) {
  $c = 'case-{0:d2}' -f $i
  $art += "$top/$c/final.png"
  $art += "$top/$c/final.snapshot"
  $art += "$top/$c/case.md"
}
$missing = $art | Where-Object { -not (Test-Path (Join-Path $root $_)) }
if ($missing.Count -gt 0) { throw ("missing artifacts: " + ($missing -join ', ')) }

# ---------- visual evidence ----------
$ev = @(
  "outputs/.../B03/case-01/final.png  1080x1528 263211 B（读图工具实际查看）：实心金黄行 + 6px 薄荷绿 STROKE 空心行两种字法可分；右上 047 空心水印补掉首版留白；四行信息标签左对齐，页脚 DEMO 可见",
  "outputs/.../B03/case-02/final.png  1920x720 244341 B（读图工具查看 2 次）：r1 读图发现四块玻璃全部没有虚化（面板内建筑边缘仍是硬边）→ 探针 p14-p18 定出两条硬规则 → r2 重做为一整块玻璃；像素证据 玻璃内 10px 天空缝 x=694→697 为硬切渐变、与卡外 y=660 形状一致",
  "outputs/.../B03/case-03/final.png  1600x640 65155 B（读图工具查看 2 次）：左上色带圆与方交叠处呈第三种深色（MULTIPLY 生效）；r2 合并存根标题为单行、右档补蓝色套印版画；票号 0481 / 流水号 / 日期三处互相对得上",
  "outputs/.../B03/case-04/final.png  1920x1080 179949 B（读图工具查看 3 次）：r1 先 400（Positioned 父数据类型）；r2 条带绝对坐标 756→400 回到巨型时间之后；r3 DELTA 独立卡，坐标核算四张右卡右边界同为 1848",
  "outputs/.../B03/case-05/final.png  1000x1414 182307 B（读图工具查看 2 次）：r1 读图发现图框下半与页脚上方两处死白；r2 补分隔线 y618 / 观测说明 / 采样时间与「辨识要点」第二段（+4 枚 chip），新增段落止于 y1190 与 y1200 起正文留 10px 未相撞",
  "outputs/.../B03/case-06/final.png  1080x1440 93707 B（读图工具查看 4 次）：r2 墨迹实测 x=63..891（未出血）；r3 加 maxLines 后 PNG 字节与 r2 完全相同（sha 516CCB8B…，maxLines 无效）；r4 框宽 1032→2000 后墨迹 x=63..1079 == 页宽-1，C 被页面齐平切断，真出血",
  "outputs/.../B03/case-07/final.png  1748x760 140684 B（读图工具查看 4 次）：r2 补右栏与「次日+1」对齐；r3 发现右栏 x880 与第四格 x900 相差 20px，改 900；r4 存根补旅客右对齐列、条码拉满 440px（1216..1656）与日期右端同列",
  "outputs/.../B03/case-08/final.png  1200x1500 209634 B（读图工具查看 3 次）：r1 先 400（boxShadow 纯数字）；r3 逐像素采样 y=1258..1312 左右两半完全相同（y=1272 均为 #E8EAEC）→ 原方案被 p19 推翻；r4 改版后左卡底 y=1223（框边 1224）vs 右卡底 y=1293，差 70px；r5 修掉指向不存在任务的 B08 引用并复看确认全图无 B08",
  "outputs/.../B03/case-09/final.png  1920x480 124832 B（读图工具查看 2 次）：首版即通过；逐项核对七列 x=72/300/840/1000/1160/1320/1660、行距 58、分隔线 y=108/176/234/292/350/408/432、页脚 y=444..470 均在画布内；复核 p08 实测 +tnum 改变字宽 294→325",
  "outputs/.../B03/case-10/final.png  1200x1200 122860 B（读图工具查看 3 次）：r1 读图诊断出 $U/$u 大小写冲突与矩阵重复平移两处结构错；r3 定点取色复核塔身 r2 #7FB07A（被树色盖）→ r3 #C98A4A/#E9B978/#DCA464（正确塔色）；r4 补 5 馆图例、r5 补 5 树图例（第三次 400 由 @() 数组折叠导致 color=\"#\"），坐标核算图例块 x72..294/y300..326 与图形最高点 x520..680/y319 横坐标不相交",
  "outputs/.../B03/portfolio.json  final_collection_review 十一项检查全 pass：10 组 png/snapshot/case.md/.round 齐全、10 张 PNG 字节数与最后一次成功响应 bytes 逐一相等（合计 1626680 B）、IHDR 与 DSL 首个 Container 宽高逐一相等、10 种画幅无重复、10 件各有真实受众与观看距离 0.25-10m、10 件 viewed=true 全覆盖、19 探针证据、无悬空交叉引用、图例与画面一致、10 件画面内 DEMO 可见",
  "tmp/.../B03/requests.jsonl  78 行 0 坏 JSON：渲染 58（用例 33 + 探针 25）+ 文档 20；200=68、400=10（PARSE_ERROR 原文留 case-XX/failures/ 与 probes/failures/）；请求耗时之和 216057ms；0 次 429、ratelimit_remaining 最低 110",
  "tmp/.../B03/iterations.jsonl  62 行 0 坏 JSON：baseline 10 / visual 21 / capability-probe 24 / syntax-fix 4 / evidence-correction 3；viewed=true 58",
  "tmp/.../B03/tool-usage.jsonl  9 行，含 tu-04 记录读图工具内容哈希缓存串图与 browser.disconnected 两处环境限制，如实登记为失败的工具尝试",
  "tmp/.../B03/probes.md + probes/*.png  19 个能力探针全部真实渲染；§2 p02、§6 p06、§9 p09 三节为读图印象被像素证据推翻后的更正版本"
)

# ---------- unresolved ----------
$unres = @(
  "无阻塞项：B03 已 completed，10/10 件独立主作品经真实 open-snapshot 服务渲染、终版全部用读图工具直接打开查看并复看通过，36 个产物齐全",
  "requests.jsonl 中 case-04-r1 / case-08-r1 / case-10-r5 三处重试沿用同一请求 ID（一次 400 + 一次 200），两条原始记录均保留未合并，属日志编号缺陷而非渲染缺陷",
  "attempts/ 中 case-10-r4 与 case-10-r4-2 为同一次 r4 内容的两次归档（首次归档后渲染 400，二次运行重复归档），按「不清理尝试」原则保留",
  "浏览器通道不可用（browser.disconnected: No desktop browser is connected），browser.preview 无法参与看图；改用 read 工具 + System.Drawing 像素采样双轨，已记录在 tu-04",
  "token、图像输入用量与费用：平台未提供本任务任何计量指标，task-metrics.json 全部记 null 并注明原因；排队等待不可测记 null；限流等待 0（本题未出现 429/Retry-After）",
  "probes.md 保留三条被推翻的初读结论（p02 / p06 / p09）作为更正记录，未删除原文痕迹"
)

# ---------- resume notes ----------
$resume = @"
completed；无阻塞，可继续 B04。10 件主作品：case-01 r2 1080x1528 / case-02 r2 1920x720 / case-03 r2 1600x640 / case-04 r3 1920x1080 / case-05 r2 1000x1414 / case-06 r4 1080x1440 / case-07 r4 1748x760 / case-08 r5 1200x1500 / case-09 r1 1920x480 / case-10 r5 1200x1200。请求 78 行串行（200=68、400=10），请求耗时之和 216057ms，0 限流 0 排队，墙钟 87610.396s（文档抓取 10-06 与渲染工作 10-07 之间跨日闲置）。迭代 62 行、visual 21、tool-usage 9 行、读图调用 70 次（58 行 viewed=true + 12 次终审复看），10 件终版全部取得过正确字节。交付 36 个产物，10 张 PNG 服务原始字节合计 1626680 B 无后处理、10 种画幅比例无重复、观看距离 0.25-10m、19 个能力探针。
关键发现（已写入 technique-notes.md，可直接复用）：(1) BackdropFilter 只有第一个生效且 Clip 必须直接包住它、中间不能夹 Container(color)；(2) Stack 裁子节点但从不裁 boxShadow（p19）；(3) SizedOverflowBox 把自己宽度当换行约束、maxLines 被渲染器忽略，出血须框宽大于字宽由页边当刀；(4) ColorFiltered 只与子节点混合；(5) IBlur 内部是相对定位且不能嵌 Positioned；(6) 对齐只有 (-1,0) 写法可用、LEFT_CENTER 应为 CENTER_LEFT；(7) boxShadows 必须写 ELEVATION_n 层级名。可复用：lib-b03.ps1 的 TX/TXW/Circ/Grad/CTint/IBlur/Glass/Frost/ClipAt/Bleed/Chip/IsoM/IsoTop/IsoLeft/IsoRight/Page/Write-Dsl/Report-Problems，render-b03.ps1 的 case_id/dsl_chars 字段化，docfetch.ps1；成品不得重复计数。
"@

# ---------- apply ----------
$b03.status = 'completed'
$b03.ended_at = $now
$b03.completed_cases = @('case-01','case-02','case-03','case-04','case-05','case-06','case-07','case-08','case-09','case-10')
$b03.artifacts = $art
$b03.visual_review_evidence = $ev
$b03.unresolved_issues = $unres
$b03.resume_notes = $resume

$b04.status = 'in_progress'
$b04.started_at = $now

$j.current_task = 'B04'
$j.updated_at = $now
$j.last_checkpoint = 'tmp/run-20261002-220723-mimo/_suite/checkpoints/state-000033.json'

$json = $j | ConvertTo-Json -Depth 8
[IO.File]::WriteAllText($statePath, $json, $enc)
$null = Get-Content $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
"suite-state.json updated: B03=completed, B04=in_progress, artifacts=$($art.Count)"

# ---------- checkpoint (immutable) ----------
$cpPath = Join-Path $ts 'checkpoints\state-000033.json'
if (Test-Path $cpPath) { throw "checkpoint $cpPath already exists - refusing to overwrite" }
[IO.File]::WriteAllText($cpPath, $json, $enc)
$null = Get-Content $cpPath -Raw -Encoding UTF8 | ConvertFrom-Json
"checkpoint written: state-000033.json ($((Get-Item $cpPath).Length) bytes)"

# ---------- event seq 57 ----------
$evPath = Join-Path $ts 'events.jsonl'
$seq = 57
$e = [ordered]@{
  seq = $seq
  ts = $now
  type = 'task_completed'
  task = 'B03'
  artifact_scope = 'outputs/run-20261002-220723-mimo/B03'
  renders_added = 58
  views_added = 70
  iterations_added = 62
  cases_completed = 10
  note = "B03 完成并关闭（用十件作品探索 DSL 的创意边界）。10 件独立主作品全部为纯 DSL、经真实 open-snapshot 服务渲染，终版 PNG 字节数与各自最后一次成功响应的 bytes 逐一相等（263211/244341/65155/179949/182307/93707/140684/209634/124832/122860，合计 1626680 B），IHDR 尺寸与 DSL 首个 Container 宽高逐一相等，10 种画幅比例无重复，观看距离 0.25-10m。请求 78 行（200=68、400=10 留存失败原文；渲染 58 = 用例 33 + 探针 25，文档 20），请求耗时之和 216057.2ms，首张可用图距首条请求 75713.924s，墙钟 87610.396s（文档 10-06 与渲染 10-07 跨日闲置），0 次 429。迭代 62 行（baseline 10 / visual 21 / capability-probe 24 / syntax-fix 4 / evidence-correction 3）、tool-usage 9 行、读图调用 70 次。交付 36 个产物：portfolio.json / portfolio.md / technique-notes.md（指定额外交付，13 节实测技术边界）/ gallery.html / snapshot-usage.md / task-metrics.json + 10 组 case-NN/{final.png,final.snapshot,case.md}。19 个能力探针全部真实渲染，三条读图初读结论（p02 BackdropFilter、p06 Stack 裁阴影、p09 SizedOverflowBox 出血）被像素/字节证据推翻并写回 probes.md。本轮新增动作：case-08 页脚悬空引用 B08 改为「本页为虚构规范演示」（本套只有 A01-A24 与 B01-B06）；case-10 新增第三条图例行「绿化 / 树木 #7FB07A」键出 5 个未被解释的绿色矮体（首发 400 由 @(@('a','b')) 被 @() 折叠致 color=\"#\"，改 @(, $pair) 后 200）。suite-state B03 -> completed，B04 -> in_progress。"
}
[IO.File]::AppendAllText($evPath, ($e | ConvertTo-Json -Compress) + "`n", $enc)
$last = Get-Content $evPath -Encoding UTF8 | Select-Object -Last 1 | ConvertFrom-Json
"events.jsonl appended: seq=$($last.seq)"
