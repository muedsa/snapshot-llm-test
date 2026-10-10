# close A14 / open A15 - appends events, updates suite-state.json (the live pointer),
# and writes the immutable checkpoint state-000015.json.
$ErrorActionPreference = 'Stop'
[System.Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root

$SUITE_OUT = "outputs\$RUN\_suite"
$SUITE_TMP = "tmp\$RUN\_suite"
$STATE     = "$SUITE_OUT\suite-state.json"
$EVENTS    = "$SUITE_TMP\events.jsonl"
$CKPT_DIR  = "$SUITE_TMP\checkpoints"
$TASK      = 'A14'
$NEXT      = 'A15'

$close   = Get-Date
$closeTs = $close.ToString('yyyy-MM-ddTHH:mm:sszzz')

# ended_at is taken from the task's own metrics file so the two never drift.
$metricsPath = "outputs\$RUN\A14\task-metrics.json"
$metrics = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($metricsPath, [Text.UTF8Encoding]::new($false)))
$A14End = [string]$metrics.ended_at
if ($A14End -notmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$') { throw "A14 ended_at is not a timezone-carrying timestamp: $A14End" }

# ---------------------------------------------------------------- source state --
$sourceJson = [IO.File]::ReadAllText($STATE, [Text.UTF8Encoding]::new($false))
$src = $sourceJson | ConvertFrom-Json

# ------------------------------------------------------------------ A14 close ---
$a14 = $src.tasks | Where-Object { $_.id -eq $TASK }
if ($null -eq $a14) { throw "A14 entry not found in suite-state.json" }
if ($a14.status -ne 'in_progress') { throw "A14 expected in_progress, found $($a14.status)" }

$a14.status     = 'completed'
$a14.ended_at   = $A14End
$a14.output_dir = "outputs/$RUN/A14/"
$a14.temp_dir   = "tmp/$RUN/A14/"
$a14.artifacts = @(
  'outputs/run-20261002-220723-mimo/A14/card-K01.png',
  'outputs/run-20261002-220723-mimo/A14/card-K01.snapshot',
  'outputs/run-20261002-220723-mimo/A14/card-K02.png',
  'outputs/run-20261002-220723-mimo/A14/card-K02.snapshot',
  'outputs/run-20261002-220723-mimo/A14/card-K03.png',
  'outputs/run-20261002-220723-mimo/A14/card-K03.snapshot',
  'outputs/run-20261002-220723-mimo/A14/card-K04.png',
  'outputs/run-20261002-220723-mimo/A14/card-K04.snapshot',
  'outputs/run-20261002-220723-mimo/A14/card-K05.png',
  'outputs/run-20261002-220723-mimo/A14/card-K05.snapshot',
  'outputs/run-20261002-220723-mimo/A14/card-K06.png',
  'outputs/run-20261002-220723-mimo/A14/card-K06.snapshot',
  'outputs/run-20261002-220723-mimo/A14/card-K07.png',
  'outputs/run-20261002-220723-mimo/A14/card-K07.snapshot',
  'outputs/run-20261002-220723-mimo/A14/card-K08.png',
  'outputs/run-20261002-220723-mimo/A14/card-K08.snapshot',
  'outputs/run-20261002-220723-mimo/A14/batch-audit.json',
  'outputs/run-20261002-220723-mimo/A14/snapshot-usage.md',
  'outputs/run-20261002-220723-mimo/A14/task-metrics.json'
)
$a14.visual_review_evidence = @(
  'tmp/run-20261002-220723-mimo/A14/render-v1-probe-badges.png  状态符号探针：○ ◆ △ × 四个字形全部成字、颜色各异、无豆腐块 —— 批量前先证明字形可用',
  'tmp/run-20261002-220723-mimo/A14/render-v2-card-K01..K08.png  首个可见整套（8 张逐张打开）：内容与状态色全对，但 K01 是单行标题，下方空 188px，而两行卡填满区块 —— 标题块是顶对齐而非居中',
  'tmp/run-20261002-220723-mimo/A14/render-v3-card-K01..K08.png  居中后整套（8 张逐张打开）：标题已在区块内居中，但页脚离分隔线仅 24px、离安全线差 52px，下边距 82px 是上边距 40px 的两倍',
  'tmp/run-20261002-220723-mimo/A14/render-v4-card-K01.png  重排后抽查：仍只下移 10px，下方依旧 82px，且 8 张里 7 张右下角空着 —— 改为页脚整体底部锚定',
  'tmp/run-20261002-220723-mimo/A14/render-v5-card-K01..K08.png  最终版（8 张逐张打开）：讲者块底边贴 590、日期与讲者同行、本场取消与时间同行，四边 40/40',
  'tmp/run-20261002-220723-mimo/A14/render-v5-card-K01..K08.png 字节交叉验证：8 张 SHA256 互不相同，状态胶囊与分隔头逐卡正确（34D399 / F6B94A / A78BFA / F87171），标题带墨点数 8 个值全不相同',
  '独立 QA 会话 ses_efebc9497ffe0pb21lQxrPA8I7 逐张打开 8 张交付 PNG：逐行标题、时间、讲者、状态胶囊颜色+符号+文字、日期行全部符合；实测内容包围盒 (40,40)-(1158,589) 印证 40px 安全边距；无裁切、无重叠、无豆腐块、标题不碰徽标',
  'outputs/run-20261002-220723-mimo/A14/card-K01..K08.png  交付件原图：与 render-v5 对应文件 SHA256 逐字节一致，均为服务原始字节、无后处理',
  'outputs/run-20261002-220723-mimo/A14/batch-audit.json  verify.ps1 产出：8/8 PASS，每卡 24 项，含 image_views 查看证据'
)
$a14.unresolved_issues = @(
  '看图通道反复返回旧帧：已用"逐帧与所开文件的预期内容比对→不匹配即判过期重开→卡住时用唯一文件名的字节相同副本换帧→独立 QA 复核→交付文件字节交叉验证"五重兜底；问题属运行环境，交付文件本身经字节与独立复核证明正确',
  '交互式开图的精确时刻未埋点：iterations.jsonl 视觉类行的 started_at/ended_at 用"上一轮渲染真实结束时刻→下一轮渲染真实开始时刻"作区间上界，viewed_at 类字段置 null 并加 note，不编造时刻',
  'K02 标题在任何字号下都不存在自然断点（`读文档，也要读懂布局约束` 无标点可断），最终按均衡切分断在 `，` 处，natural_break=false；这是数据本身决定的，非缺陷',
  'r04 中间版 8 张只逐张看了 K01（页脚改动是单一共享规则，最终 8 张已在 r05 全部逐张复核），已在 iterations.jsonl seq 15 的 note 中写明',
  'gen.ps1 开发期曾以相同 -Ver 1 重跑并重写 card-K01-v1 / card-K02-v1 两个 DSL，两次输出字节完全一致，未丢失任何不同尝试；记录于 task-metrics.deliverables.overwritten_attempts_note',
  '讲者长名在本批数据里最多 1 行（最长 Northstar Research · 林川），两行讲者的排版规则已实现并有 585≤590 的守卫，但本批数据未触发实测'
)
$a14.resume_notes = '41 次 POST /snapshot：33×200、8×400、0 重试、0 限流，请求耗时之和 86004.4ms。8 张 1200x630 宣传卡（card-K01..K08.png）+ 8 份同名 .snapshot + batch-audit.json + snapshot-usage.md + task-metrics.json 共 19 个产物，PNG 为服务原始字节、与 render-v5 逐字节 SHA256 一致、无后处理。唯一参数化规则集：共享标题区 104..396 垂直居中、字号阶梯 112..36、按字符类分档宽度估算（全宽 1.05 / 拉丁 1.10）、穷举断行 + 标点优先 + 单行不压过断行；状态用颜色+符号+文字三重编码（○34D399 ◆F6B94A △A78BFA ×F87171）且胶囊宽度统一 135px；页脚底部锚定，讲者块底边贴安全线 590，日期与讲者同行、本场取消与时间同行。8 个生成器版本、5 轮渲染、20 行 iterations、34 次看图。3 个由看图发现的真实缺陷：单行标题顶对齐留洞、页脚上下边距 82/40 颠倒、重排后仍差 22px 且右下角空。8/8 通过每卡 24 项审计。墙钟 6183s，首个可用卡片图 2376.5s（r01 全 400 无图）。'

# ------------------------------------------------------------------ A15 open -----
$a15 = $src.tasks | Where-Object { $_.id -eq $NEXT }
if ($null -eq $a15) { throw "$NEXT entry not found" }
if ($a15.status -ne 'pending') { throw "$NEXT expected pending, found $($a15.status)" }
$a15.status      = 'in_progress'
$a15.started_at  = $closeTs
$a15.output_dir  = "outputs/$RUN/$NEXT/"
$a15.temp_dir    = "tmp/$RUN/$NEXT/"
New-Item -ItemType Directory -Force -Path "outputs\$RUN\$NEXT" | Out-Null
New-Item -ItemType Directory -Force -Path "tmp\$RUN\$NEXT"     | Out-Null

# ------------------------------------------------------------ top-level pointer ---
$src.updated_at      = $closeTs
$src.current_task    = $NEXT
$src.current_round   = $null
$src.current_case    = $null
$src.last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000015.json"
$src.status          = 'in_progress'

# --------------------------------------------------------------- write state ------
$stateText = $src | ConvertTo-Json -Depth 12
[IO.File]::WriteAllText($STATE, $stateText, [Text.UTF8Encoding]::new($false))

# ----------------------------------------------------------------- events ---------
$evLines = New-Object System.Collections.Generic.List[string]
$ev27 = [ordered]@{
  seq  = 27
  ts   = $closeTs
  type = 'task_completed'
  task = $TASK
  artifacts = 19
  renders = 41
  views = 34
  visual_iterations = 3
  note = 'A14 八组文案压力测试完成：card-K01..K08.png（均 1200x630，服务原始字节，与 render-v5 逐字节一致）+ 8 份同名 .snapshot + batch-audit.json + snapshot-usage.md + task-metrics.json 共 19 个产物。41 次请求：33x200、8x400、0 重试、0 限流。r01 由 $line 覆盖 $LINE（PowerShell 变量不分大小写）导致 8x400 PARSE_ERROR。唯一参数化规则集从 cards.json 生成全部 8 张，无逐条硬改；标题字号 56..112（>=36）最多 2 行（<=3），讲者 32px（>=22）最多 1 行（<=2），四边安全边距实测 40/40，标题不碰状态徽标。状态四重冗余：颜色+符号+文字+分隔头着色。K06 保留完整标题与 13:40 并加注本场取消，未删除也未只出灰底。3 个由看图发现的真实缺陷：单行标题顶对齐留 188px 洞、页脚 82/40 上下边距颠倒、重排后仍差 22px 且右下角空。8/8 通过每卡 24 项审计。task-metrics.ended_at = ' + $A14End + '（本事件时刻为状态落盘时刻）。'
}
$ev28 = [ordered]@{
  seq  = 28
  ts   = $closeTs
  type = 'task_started'
  task = $NEXT
  note = ''
}
foreach ($e in @($ev27, $ev28)) {
  $o = [pscustomobject]$e
  $evLines.Add(($o | ConvertTo-Json -Depth 6 -Compress))
}
$append = [string]::Join([Environment]::NewLine, $evLines.ToArray()) + [Environment]::NewLine
[IO.File]::AppendAllText($EVENTS, $append, [Text.UTF8Encoding]::new($false))

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
  checkpoint_id    = 'state-000015'
  checkpoint_seq   = 15
  event_seq        = 28
  current_task     = $NEXT
  current_status   = 'in_progress'
  last_checkpoint  = "tmp/$RUN/_suite/checkpoints/state-000015.json"
  task_status_counts = $counts
  tasks_completed  = $completedIds
  tasks_in_progress = $NEXT
  checkpoint_note  = 'A14 关闭：8 张 1200x630 宣传卡 + 8 份同名 .snapshot + batch-audit.json（8/8 PASS，每卡 24 项）+ snapshot-usage.md + task-metrics.json 共 19 个产物全部落盘，PNG 为服务原始字节并与 render-v5 逐字节 SHA256 一致。41 次请求（33x200、8x400、0 重试），20 行 iterations，34 次看图，3 轮真实视觉迭代。suite-state.json 中 A14=completed、A15=in_progress。A15 于本时刻启动。'
  suite_state      = $src
  source_state_copy = ($sourceJson | ConvertFrom-Json)
}
$ckPath = "$CKPT_DIR\state-000015.json"
if (Test-Path $ckPath) { throw "checkpoint $ckPath already exists - never overwrite a historical snapshot" }
[IO.File]::WriteAllText($ckPath, ($ckpt | ConvertTo-Json -Depth 14), [Text.UTF8Encoding]::new($false))

Write-Output "A14 -> completed (ended_at $A14End)"
Write-Output "A15 -> in_progress (started_at $closeTs)"
Write-Output "events.jsonl  + seq 27 (task_completed A14), seq 28 (task_started A15)"
Write-Output "suite-state.json updated_at = $closeTs  current_task = $NEXT  last_checkpoint = state-000015.json"
Write-Output "checkpoint -> $ckPath  bytes=$((Get-Item $ckPath).Length)"
Write-Output ("task_status_counts: " + (($counts | ForEach-Object { "$($_.status)=$($_.count)" }) -join ', '))
