# close A18 / open A19 - appends events, updates suite-state.json (the live pointer),
# and writes the immutable checkpoint state-000019.json.
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root

$SUITE_OUT = "outputs\$RUN\_suite"
$SUITE_TMP = "tmp\$RUN\_suite"
$STATE     = "$SUITE_OUT\suite-state.json"
$EVENTS    = "$SUITE_TMP\events.jsonl"
$CKPT_DIR  = "$SUITE_TMP\checkpoints"
$TASK      = 'A18'
$NEXT      = 'A19'
$utf8      = [Text.UTF8Encoding]::new($false)

$close   = Get-Date
$closeTs = $close.ToString('yyyy-MM-ddTHH:mm:sszzz')

$metricsPath = "outputs\$RUN\A18\task-metrics.json"
$metrics = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($metricsPath, $utf8))
$A18End = [string]$metrics.ended_at
if ($A18End -notmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$') { throw "A18 ended_at is not a timezone-carrying timestamp: $A18End" }

$exDir = "outputs\$RUN\A18"
function HashOf([string]$f) { return (Get-FileHash $f -Algorithm SHA256).Hash }
function SizeOf([string]$f) { return (Get-Item $f).Length }

$png   = "$exDir\three-act-story.png";    $pngH   = HashOf $png;    $pngB   = SizeOf $png
$dsl   = "$exDir\three-act-story.snapshot"; $dslH = HashOf $dsl;    $dslB   = SizeOf $dsl
$audit = "$exDir\story-audit.json"

# ---------------------------------------------------------------- source state --
$sourceJson = [IO.File]::ReadAllText($STATE, $utf8)
$src = $sourceJson | ConvertFrom-Json

# ------------------------------------------------------------------ A18 close ---
$a18 = $src.tasks | Where-Object { $_.id -eq $TASK }
if ($null -eq $a18) { throw "$TASK entry not found in suite-state.json" }
if ($a18.status -ne 'in_progress') { throw "$TASK expected in_progress, found $($a18.status)" }

$a18.status     = 'completed'
$a18.ended_at   = $A18End
$a18.output_dir = "outputs/$RUN/A18/"
$a18.temp_dir   = "tmp/$RUN/A18/"
$a18.artifacts = @(
  'outputs/run-20261002-220723-mimo/A18/three-act-story.png',
  'outputs/run-20261002-220723-mimo/A18/three-act-story.snapshot',
  'outputs/run-20261002-220723-mimo/A18/story-audit.json',
  'outputs/run-20261002-220723-mimo/A18/rationale.md',
  'outputs/run-20261002-220723-mimo/A18/snapshot-usage.md',
  'outputs/run-20261002-220723-mimo/A18/task-metrics.json',
  'outputs/run-20261002-220723-mimo/A18/final-audit.md'
)
$a18.visual_review_evidence = @(
  'tmp/run-20261002-220723-mimo/A18/probe-04.png  探针图：括号列主序 16 浮点矩阵被服务接受，旋转图元完整不被 Positioned 盒裁切，据此定下箭头写法',
  'tmp/run-20261002-220723-mimo/A18/preview-a-v01.png  1600x1000 构图 A 首版：三条横带成立，但带高仅 254px、幕名浮在带外、幕一核心与外壳读不出层次',
  'tmp/run-20261002-220723-mimo/A18/preview-b-v01.png  1600x1000 构图 B 首版（第二条叙事构图，按题面要求单独渲染）：三条竖栏让幕一的单中心与幕三的三个出口读成互不相干的画面',
  '两条构图并排实看后选 A：三个节点放在同一条水平线上，"一个中心变成三个出口"一眼读出，且幕的顺序等于叙事顺序；两版预览都留在 tmp',
  'tmp/run-20261002-220723-mimo/A18/preview-a-v02.png  1600x1000：带高 254→294、幕名移入带内左上、幕一外椭圆 ry 96→118，三幕分区清楚',
  'tmp/run-20261002-220723-mimo/A18/thumb-a-v02-400.png  400x250 缩略图：标题与三条幕名可读，三幕仍分明，带结构保留',
  'tmp/run-20261002-220723-mimo/A18/preview-a-v03.png  1600x1000：幕一内椭圆 150,86→110,76 分出 5 个核心 + 10 个外壳，幕二外环 94→91；本次本地 read 返回缩放帧，改由独立子代理逐像素核对（iterations seq 11），并看出颜色在暗中编码位置的缺陷',
  'tmp/run-20261002-220723-mimo/A18/preview-a-v04.png  1600x1000：颜色置换 (0,5,10,1,6,11,…) 插入幕一/幕二位置序，蓝橙灰均匀穿插；幕二内环 56→58 摆脱 0.2px 相切',
  'tmp/run-20261002-220723-mimo/A18/thumb-a-v04-400.png  400x250 缩略图：标题、三条幕名可读，幕一宽散、幕二紧凑、幕三三簇三态分明',
  'tmp/run-20261002-220723-mimo/A18/preview-a-v01-recheck.png  重建件与原 v01 的 SHA256 完全一致（14D1947B524CB…），证明被覆盖的 v01 DSL 是逐字节还原而非近似',
  'tmp/run-20261002-220723-mimo/A18/preview-a-v05.png  1600x1000：幕名字号 26→32、文字盒高 40→56（避免 Text 的 CLIP 切掉行盒），幕名 31px vs 标题 39px 仍从属',
  'tmp/run-20261002-220723-mimo/A18/preview-a-v06.png  1600x1000（终稿）：幕二内环 58→64、外环 91→94，跨环圆心距 38.59 ≥36，15 条连线全部可见（v05 只见 13 条）',
  'tmp/run-20261002-220723-mimo/A18/thumb-a-v06-400.png  400x250 缩略图（终稿候选）：三幕仍是三种分明状态',
  'outputs/run-20261002-220723-mimo/A18/three-act-story.png  交付件原图 1600x1000：与 preview-a-v06.png SHA256 逐字节一致（' + $pngH.Substring(0,8) + '…' + $pngH.Substring($pngH.Length-4) + '），' + $pngB + ' 字节，服务原始字节、无后处理；三次独立全尺寸读帧确认恰好 4 条文字、每幕 15 单元 5/5/5、9 节点、幕二 15/15 连线、幕三每节点 5 连线 3 种颜色、最小圆间隙 3.8px、最小单元-节点间隙 3.0px、无裁切无重叠无字压图元',
  'outputs/run-20261002-220723-mimo/A18/three-act-story.png 的 400x250 缩略图：标题与三条幕名齐全，三幕仍读得出来（iterations seq 21）',
  'story-audit.json 逐幕单元 ID/颜色/坐标/接收节点 + 9 类硬约束断言：problems = 0、notes = 3',
  'check-a18.ps1 交付审计：7 个产物、PNG 签名与 1600x1000 尺寸、交付件与被看预览逐字节一致、DSL 无 BOM 无乱码、恰好 4 条逐字文字、绘制顺序 断言、三幕 15 单元 5/5/5、幕三 5 个/3 色、rationale 233 字 ≤300、17 次看图事件 —— final-audit.md problems = 0'
)
$a18.unresolved_issues = @(
  '本地 read 对 preview-a-v03.png 与交付件 three-act-story.png 各返回过一次缩放帧（内容正确但约 400px 宽）；两次都先用 SHA256 证明磁盘字节无误，再改由独立子代理全尺寸核对，iterations.jsonl seq 10/14 记被取代的本地读取、seq 11/15 记成功的委托读取，互不覆盖',
  'preview-a.snapshot 被当作工作文件复用，composition A 的 v01 DSL 在 v02 再生成时被覆盖（PNG 幸存）；已按记录的 5 处参数改动反向回退生成器副本重建，并重发 A18-previewAv01-recheck 得到与原图 SHA256 完全相同的 PNG，证明还原逐字节忠实，但被覆盖的原始请求字节本身不可再取回',
  '400px 缩略图里三条幕名的 CJK 笔画约 7px，能看到标签位置与三态差别，但逐字辨认需要放大；全尺寸为 30px 完全清晰，字号已由 26 提到 32 专门收窄此差距，属缩略图固有限制而非缺陷',
  '幕二中心节点的胶囊端口在 400px 缩略图里把白环切成两条，是全尺寸刻意特征的缩略图副产物',
  'A18 墙钟含一段约 6455s 的会话暂停（末次渲染 21:02:53 → 恢复写交付物 23:00:28，来自上下文检查点）；恢复时沿用原 run_id 与既有文件，未重做任何工作，已在 task-metrics.waiting.session_pause_s 如实单列',
  'token 与费用服务与运行时都不报数，task-metrics.json 全部记 null；服务端画布尺寸上限、Retry-After 实际取值从未观测到，同样不估算'
)
$a18.resume_notes = '12 次请求（全部 POST /snapshot），200=9、400=3（三条全部是刻意的 Transform 语法探针，失败响应体保留于 tmp/A18/failures/），0 限流、0 重试，请求耗时之和 35675.7ms（200 30028.0ms + 400 5647.7ms），收到 778619 字节（PNG 778006 + 错误体 613）。文档类请求 0 次：Transform 矩阵规则复用 A17 保留的 doc-parser-tags.html、属性表复用 A15、字体复用 A11 的 /fonts 结果。交付 7 个产物：three-act-story.png/.snapshot（1600x1000，' + $pngB + ' / ' + $dslB + ' 字节，服务原始字节）+ story-audit.json + rationale.md（233 字）+ snapshot-usage.md + task-metrics.json + final-audit.md。21 行 iterations（visual 13 / syntax-fix 4 / alternative 2 / baseline 1 / retry 1），5 轮完整视觉迭代，看图发现 5 个缺陷、测量发现 1 个（幕二 0.2px 相切）。题面要求的两条叙事构图各渲染过真实 1600x1000 预览后才选 A，两版预览均留在 tmp。选定构图迭代 6 版（v01→v06），每版都看过。17 次看图事件（本地 13 + 委托 4），含 4 次独立全尺寸核对与 4 次 400px 缩略图检查；交付图开过 4 次。4 个探针实测 Transform 矩阵只接受括号列主序 16 浮点无空格写法（逗号列表与 JSON 数组各 400 一次）。story-audit.json problems = 0，final-audit.md problems = 0。墙钟 ' + $metrics.wall_clock_s + 's（含 6455s 会话暂停）。'

# ------------------------------------------------------------------ A19 open -----
$a19 = $src.tasks | Where-Object { $_.id -eq $NEXT }
if ($null -eq $a19) { throw "$NEXT entry not found" }
if ($a19.status -ne 'pending') { throw "$NEXT expected pending, found $($a19.status)" }
$a19.status      = 'in_progress'
$a19.started_at  = $closeTs
$a19.output_dir  = "outputs/$RUN/$NEXT/"
$a19.temp_dir    = "tmp/$RUN/$NEXT/"
New-Item -ItemType Directory -Force -Path "outputs\$RUN\$NEXT" | Out-Null
New-Item -ItemType Directory -Force -Path "tmp\$RUN\$NEXT"     | Out-Null

# ------------------------------------------------------------ top-level pointer ---
$src.updated_at      = $closeTs
$src.current_task    = $NEXT
$src.current_round   = $null
$src.current_case    = $null
$src.last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000019.json"
$src.status          = 'in_progress'

# --------------------------------------------------------------- write state ------
[IO.File]::WriteAllText($STATE, ($src | ConvertTo-Json -Depth 12), $utf8)

# ----------------------------------------------------------------- events ---------
$evLines = New-Object System.Collections.Generic.List[string]
$ev35 = [ordered]@{
  seq  = 35
  ts   = $closeTs
  type = 'task_completed'
  task = $TASK
  artifacts = 7
  renders = 12
  views = 17
  visual_iterations = 5
  note = 'A18 三幕叙事完成：单张 1600x1000，7 个产物（three-act-story.png/.snapshot + story-audit.json + rationale.md + snapshot-usage.md + task-metrics.json + final-audit.md）。12 次请求全部为渲染，200=9、400=3（三条全是刻意的 Transform 语法探针，失败体保留），0 限流，请求耗时之和 35675.7ms，收到 778619 字节。题面要求先提出两条叙事构图并各渲染真实 1600x1000 预览，再择一深化：构图 A（横向三带）与构图 B（竖向三联）都已渲染并留在 tmp，实看后选 A。选定后 6 版迭代、5 轮完整视觉循环，看图发现 5 个缺陷（带高与幕名位置、幕一核心外壳不分、颜色暗中编码位置、幕二 0.2px 相切与幕名在缩略图过小、幕二 15 条连线只露出 13 条），测量发现 1 个（圆角方块 45° 极径 37.8px 导致的相切）。每次迭代都重新实看全图，并按题面要求看 400px 缩略图（4 次）。交付件与被看的 preview-a-v06.png SHA256 逐字节一致；独立子代理全尺寸核对确认恰好 4 条文字、三幕各 15 单元 5/5/5、9 个等大节点、幕三每节点 5 单元 3 种颜色、最小圆间隙 3.8px、最小单元-节点间隙 3.0px、无线遮圆、无字压图元。story-audit.json problems = 0，final-audit.md problems = 0。rationale.md 正文 233 字 ≤300。'
}
$ev36 = [ordered]@{
  seq  = 36
  ts   = $closeTs
  type = 'task_started'
  task = $NEXT
  note = ''
}
foreach ($e in @($ev35, $ev36)) {
  $evLines.Add((([pscustomobject]$e) | ConvertTo-Json -Depth 6 -Compress))
}
[IO.File]::AppendAllText($EVENTS, ([string]::Join([Environment]::NewLine, $evLines.ToArray()) + [Environment]::NewLine), $utf8)

# ---------------------------------------------------------------- checkpoint ------
$counts = @($src.tasks | Group-Object status | ForEach-Object { [pscustomobject]@{ status = $_.Name; count = $_.Count } })
$completedIds = @($src.tasks | Where-Object { $_.status -eq 'completed' } | ForEach-Object { $_.id })
$ckpt = [pscustomobject][ordered]@{
  schema_version   = 1
  suite_version    = $src.suite_version
  run_id           = $RUN
  profile          = $src.profile
  status           = $src.status
  snapshot_at      = $closeTs
  checkpoint_id    = 'state-000019'
  checkpoint_seq   = 19
  event_seq        = 36
  current_task     = $NEXT
  current_status   = 'in_progress'
  last_checkpoint  = "tmp/$RUN/_suite/checkpoints/state-000019.json"
  task_status_counts = $counts
  tasks_completed  = $completedIds
  tasks_in_progress = $NEXT
  checkpoint_note  = 'A18 关闭：7 个产物落盘，PNG 为服务原始字节并与 preview-a-v06.png 逐字节 SHA256 一致。12 次渲染请求（200=9、400=3 全为保留的语法探针），21 行 iterations，17 次看图事件覆盖交付图与 400px 缩略图，5 轮真实视觉迭代。两条叙事构图 A/B 各自渲染过真实预览后才选定 A，预览均保留于 tmp。story-audit.json 与 final-audit.md 均 problems = 0。suite-state.json 中 A18=completed、A19=in_progress。A19 于本时刻启动。'
  suite_state      = $src
  source_state_copy = ($sourceJson | ConvertFrom-Json)
}
$ckPath = "$CKPT_DIR\state-000019.json"
if (Test-Path $ckPath) { throw "checkpoint $ckPath already exists - never overwrite a historical snapshot" }
[IO.File]::WriteAllText($ckPath, ($ckpt | ConvertTo-Json -Depth 14), $utf8)

Write-Output "$TASK -> completed (ended_at $A18End)"
Write-Output "$NEXT -> in_progress (started_at $closeTs)"
Write-Output "events.jsonl  + seq 35 (task_completed $TASK), seq 36 (task_started $NEXT)"
Write-Output "suite-state.json updated_at = $closeTs  current_task = $NEXT  last_checkpoint = state-000019.json"
Write-Output "checkpoint -> $ckPath  bytes=$((Get-Item $ckPath).Length)"
Write-Output ("task_status_counts: " + (($counts | ForEach-Object { "$($_.status)=$($_.count)" }) -join ', '))
