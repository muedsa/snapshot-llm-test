# close A21 / open A22 - appends events, updates suite-state.json (the live pointer),
# and writes the immutable checkpoint state-000025.json.
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
$TASK      = 'A21'
$NEXT      = 'A22'
$utf8      = [Text.UTF8Encoding]::new($false)

$close   = Get-Date
$closeTs = $close.ToString('yyyy-MM-ddTHH:mm:sszzz')

$metricsPath = "outputs\$RUN\A21\task-metrics.json"
$metrics = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($metricsPath, $utf8))
$A21End  = [string]$metrics.ended_at
if ($A21End -notmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$') { throw "$TASK ended_at is not a timezone-carrying timestamp: $A21End" }
$wallS = [Math]::Round(($metrics.wall_clock_total_ms / 1000.0), 1)

$exDir = "outputs\$RUN\A21"
function HashOf([string]$f) { return (Get-FileHash $f -Algorithm SHA256).Hash }
function SizeOf([string]$f) { return (Get-Item $f).Length }
function IhdrOf([string]$p) {
  $fs = [IO.File]::OpenRead((Resolve-Path $p).Path); $buf = New-Object byte[] 24
  [void]$fs.Read($buf, 0, 24); $fs.Close()
  return @{ w = [BitConverter]::ToUInt32(@($buf[19],$buf[18],$buf[17],$buf[16]), 0)
            h = [BitConverter]::ToUInt32(@($buf[23],$buf[22],$buf[21],$buf[20]), 0) }
}

# ------------------------------------------------------------------- required ----
if (-not (Test-Path "$exDir\snapshot-usage.md")) { throw 'missing A21 root snapshot-usage.md' }
if ($metrics.quality.deliverables_present -ne 27) { throw "root metrics say $($metrics.quality.deliverables_present)/27 deliverables" }

$rounds = @(
  @{ r = 'round-01'; n = 8;  hashes = @{ 'launch-portrait.png' = 'A41B1C2954A9C88D6B9102327E000AF4'
                                         'launch-wide.png'     = 'BEAEFEB2D03C3AA0D69A6D2F75BAB68A' } },
  @{ r = 'round-02'; n = 8;  hashes = @{ 'launch-portrait.png' = 'F013863FB5E50783164AC44686249378'
                                         'launch-wide.png'     = 'A9B8F6D1E035323383DADDD9BAEAFAEC' } },
  @{ r = 'round-03'; n = 11; hashes = @{ 'launch-portrait.png' = '7F9497E8B17C04F9F780C41426C94ACD'
                                         'launch-wide.png'     = '9C626F24FB85198064D3DAFC75DB1FBF' } }
)
$totalFiles = 0
$allHashes  = @()
foreach ($rd in $rounds) {
  $files = @(Get-ChildItem "$exDir\$($rd.r)" -File)
  if ($files.Count -ne $rd.n) { throw "$($rd.r) has $($files.Count) files, expected $($rd.n)" }
  $totalFiles += $files.Count
  foreach ($k in $rd.hashes.Keys) {
    $h = HashOf "$exDir\$($rd.r)\$k"
    if (-not $h.StartsWith($rd.hashes[$k])) { throw "$($rd.r)/$k changed: $h" }
    $allHashes += $h
    if (-not (Test-Path "$exDir\$($rd.r)\$($k -replace '\.png$', '.snapshot')")) { throw "$($rd.r) missing .snapshot for $k" }
  }
  # every delivered PNG must be byte-identical to the service response and 0 <Image> in its DSL
  foreach ($png in @('launch-portrait.png', 'launch-wide.png')) {
    $srcPng = "tmp\$RUN\A21\" + ($png -replace '\.png$', "-r$($rd.r.Substring(6,2)).png")
    if ((HashOf "$exDir\$($rd.r)\$png") -ne (HashOf $srcPng)) { throw "$($rd.r)/$png is not byte-identical to the service response" }
    $dsl = [IO.File]::ReadAllText("$exDir\$($rd.r)\$($png -replace '\.png$', '.snapshot')", $utf8)
    if ($dsl -notmatch '^<Snapshot type="png"') { throw "$($rd.r) $png .snapshot root is not Snapshot" }
    if ($dsl -match '<Image') { throw "$($rd.r) $png .snapshot contains <Image" }
  }
}
if ($totalFiles -ne 27) { throw "27 deliverables expected, found $totalFiles" }

# round-03 contrast audit must pass (it is the task's only contrast-gated round)
$ca = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$exDir\round-03\contrast-audit.json", $utf8))
if (-not $ca.summary.pass) { throw 'round-03 contrast-audit summary.pass is not true' }
if (-not $ca.summary.entries_sufficient_per_image) { throw 'round-03 audit has fewer than 6 entries for an image' }
if (-not $ca.summary.all_entries_ge_4_5) { throw 'round-03 audit has an entry below 4.5:1' }

$req   = Get-Content "tmp\$RUN\A21\requests.jsonl" -Encoding UTF8
$iters = Get-Content "tmp\$RUN\A21\iterations.jsonl" -Encoding UTF8
if ($req.Count -ne 8) { throw "A21 requests.jsonl has $($req.Count) rows, expected 8" }
if ($iters.Count -ne 6) { throw "A21 iterations.jsonl has $($iters.Count) rows, expected 6" }
$badReq = @($req | ForEach-Object { $_ | ConvertFrom-Json } | Where-Object { $_.http_status -ne 200 })
if ($badReq.Count) { throw "A21 has $($badReq.Count) non-200 request rows" }

# ---------------------------------------------------------------- source state --
$sourceJson = [IO.File]::ReadAllText($STATE, $utf8)
$src = $sourceJson | ConvertFrom-Json

# ------------------------------------------------------------------ A21 close ---
$a21 = $src.tasks | Where-Object { $_.id -eq $TASK }
if ($null -eq $a21) { throw "$TASK entry not found in suite-state.json" }
if ($a21.status -ne 'in_progress') { throw "$TASK expected in_progress, found $($a21.status)" }
if ((@($a21.completed_rounds) -join ',') -ne 'round-01,round-02,round-03') { throw 'A21 all three rounds must already be recorded' }

$base = "outputs/run-20261002-220723-mimo/A21/"
$a21.status     = 'completed'
$a21.ended_at   = $A21End
$a21.output_dir = "outputs/$RUN/A21/"
$a21.temp_dir   = "tmp/$RUN/A21/"
$a21.artifacts = @($a21.artifacts) + @($base + 'snapshot-usage.md', $base + 'task-metrics.json')
$a21.unresolved_issues = @($a21.unresolved_issues) + @(
  'A21 已无未解决的视觉或需求问题：三轮均 problems = 0，52/52 探针命中，12/12 保留带为空，round-03 每图 10 处正文对比度全部 >=4.5:1（最低 5.63:1）'
)
$a21.resume_notes = 'A21 全部三轮完成，27 个产物（round-01 8 + round-02 8 + round-03 11）+ 任务根累计 snapshot-usage.md 与 task-metrics.json = 29 个文件。6 张交付 PNG 全部为服务原始响应字节、SHA-256 与响应文件逐字节相同、IHDR 实读为 1080x1350 x3 与 1440x810 x3，.snapshot 一一配对且 0 个 <Image>。请求 8 次（渲染 6 + 文档 2）全部 200、失败 0、重试 0、限流事件 0；渲染耗时之和 15846.2ms、文档 846.4ms，收到 587614 字节渲染返回。看图 12 次（每轮 4 次：两图整图 + 两个品牌标记 3x 放大）。迭代 6 行（baseline 1 / syntax-fix 3 / requirement-change 2），完整视觉迭代 0 —— 每轮首版看图即满足全部要求，按约定「一次合格时无需制造修改」。GDI+ 探针 52/52 命中声明背景，12/12 保留带为空，round-03 每图 10 处正文对比度按实测像素全部 >=4.5:1、最低 5.63:1、最大通道差 1（8-bit 取整容差，只用于校验叠层，不参与对比度结论）。跨轮踩坑 7 条已在任务根 snapshot-usage.md 第 6 节汇总，最重要的两条：PowerShell 5.1 把弯引号当定界符、逗号优先级高于乘法（只在多层背景时才暴露）。墙钟 ' + $wallS + 's。'

# ------------------------------------------------------------------ A22 open -----
$a22 = $src.tasks | Where-Object { $_.id -eq $NEXT }
if ($null -eq $a22) { throw "$NEXT entry not found" }
if ($a22.status -ne 'pending') { throw "$NEXT expected pending, found $($a22.status)" }
$a22.status      = 'in_progress'
$a22.started_at  = $closeTs
$a22.output_dir  = "outputs/$RUN/$NEXT/"
$a22.temp_dir    = "tmp/$RUN/$NEXT/"
New-Item -ItemType Directory -Force -Path "outputs\$RUN\$NEXT" | Out-Null
New-Item -ItemType Directory -Force -Path "tmp\$RUN\$NEXT"     | Out-Null

# ------------------------------------------------------------ top-level pointer ---
$src.updated_at      = $closeTs
$src.current_task    = $NEXT
$src.current_round   = $null
$src.current_case    = $null
$src.last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000025.json"
$src.status          = 'in_progress'

[IO.File]::WriteAllText($STATE, ($src | ConvertTo-Json -Depth 12), $utf8)

# --------------------------------------------------------------- write state ------
$evLines = New-Object System.Collections.Generic.List[string]
$ev44 = [ordered]@{
  seq = 44; ts = $closeTs; type = 'task_completed'; task = $TASK
  artifacts = 29; renders = 6; views = 12; visual_iterations = 0; rounds = 3
  note = 'A21 分期改版三轮全部完成：27 个轮次产物 + 任务根累计 snapshot-usage.md 与 task-metrics.json = 29 个文件。6 张交付 PNG（每轮 1 竖 1 横）全部为服务原始响应字节、SHA-256 与响应文件逐字节相同、IHDR 实读 1080x1350 x3 与 1440x810 x3、.snapshot 一一配对且 0 个 <Image>；三轮四张旧 PNG 的哈希 A41B1C29 / BEAEFEB2 / F013863F / A9B8F6D1 在后两轮归档时反复硬校验从未被覆盖。请求 8 次（渲染 6 + 文档 2）全部 200、失败 0、重试 0、限流事件 0，渲染耗时之和 15846.2ms、文档 846.4ms，收到 587614 字节。三轮需求：round-01 双尺寸基础版（标题以外 >=24、单主色 #5B4FE8、4 构件品牌图形、两图独立构图、真实留白带无占位文字）；round-02 换 27 字长标题（竖 56/横 52，2 行 <=3 行、>=48）并新增赞助方与免费参加胶囊，报告含长标题与新信息避免碰撞的四种机制；round-03 浅色主题 #F4F5FB/#FFFFFF + 新增 bandA(#5B4FE81F) 与 bandB(#FFB02029) 两条真半透明背景光带 + 网址正上方新增 Clarity through structure（竖 fs28/横 fs26 >=24）。round-03 每图 10 处正文对比度（>=6 要求）按 GDI+ 实测像素的 WCAG 2.1 比值全部 >=4.5:1、最低 5.63:1，problems 0；同一 bandB 在页面实测 #F5E9D7、在白色面板实测 #FFF2DB，两种不同合成色证明叠层真实参与 source-over 而不是只改两种颜色。GDI+ 探针 52/52 命中、12/12 保留带为空。看图 12 次（每轮 4 次），迭代 6 行（baseline 1 / syntax-fix 3 / requirement-change 2），完整视觉迭代 0 —— 每轮首版看图即合格，按约定不为凑迭代而改版。跨轮踩坑 7 条含：PowerShell 5.1 弯引号当定界符、逗号优先级高于乘法（Composite 的 @() 三元数组只在多层背景才走到，单层分支掩盖了两轮）、光带层描述缺冒号、layout-map 的 title 漏声明 bandA（由真实像素审计发现）、PS 变量大小写不敏感导致 $r 覆盖 $R。墙钟 ' + $wallS + 's。'
}
$ev45 = [ordered]@{
  seq = 45; ts = $closeTs; type = 'task_started'; task = $NEXT
  note = 'A22 staged-data-correction：数据订正的多阶段任务，读取 TASK.md / AGENTS.md / task.json 与 inputs/monthly.csv、rounds/round-02.md、rounds/round-03.md 后按题面要求推进'
}
foreach ($e in @($ev44, $ev45)) { $evLines.Add((([pscustomobject]$e) | ConvertTo-Json -Depth 6 -Compress)) }
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
  checkpoint_id    = 'state-000025'
  checkpoint_seq   = 25
  event_seq        = 45
  current_task     = $NEXT
  current_status   = 'in_progress'
  last_checkpoint  = "tmp/$RUN/_suite/checkpoints/state-000025.json"
  task_status_counts = $counts
  tasks_completed  = $completedIds
  tasks_in_progress = $NEXT
  checkpoint_note  = 'A21 关闭（三轮全部归档）：27 个轮次产物 + 任务根累计报告与指标 = 29 个文件。6 张交付 PNG 与服务响应逐字节相同、IHDR 实读 1080x1350 x3 / 1440x810 x3、.snapshot 一一配对且 0 <Image>；三轮旧 PNG 哈希未变。请求 8 次全 200、失败 0、重试 0；看图 12 次；迭代 6 行、完整视觉迭代 0；探针 52/52、保留带 12/12 空；round-03 每图 10 处正文对比度全部 >=4.5:1（最低 5.63:1）按实测像素计算，problems 0。suite-state.json 中 A21=completed、A22=in_progress。A22 于本时刻启动。'
  suite_state      = $src
  source_state_copy = ($sourceJson | ConvertFrom-Json)
}
$ckPath = "$CKPT_DIR\state-000025.json"
if (Test-Path $ckPath) { throw "checkpoint $ckPath already exists - never overwrite a historical snapshot" }
[IO.File]::WriteAllText($ckPath, ($ckpt | ConvertTo-Json -Depth 14), $utf8)

Write-Output "$TASK -> completed (ended_at $A21End, 3 rounds, 29 files)"
Write-Output "$NEXT -> in_progress (started_at $closeTs)"
Write-Output "events.jsonl  + seq 44 (task_completed $TASK), seq 45 (task_started $NEXT)"
Write-Output "suite-state.json updated_at = $closeTs  current_task = $NEXT  last_checkpoint = state-000025.json"
Write-Output "checkpoint -> $ckPath  bytes=$((Get-Item $ckPath).Length)"
Write-Output ("task_status_counts: " + (($counts | ForEach-Object { "$($_.status)=$($_.count)" }) -join ', '))
Write-Output ("completed: " + ($completedIds -join ','))
Write-Output "round deliverables = $totalFiles / 27   root files = 2   requests = $($req.Count)   iterations = $($iters.Count)"
Write-Output "round-03 contrast audit: portrait $($ca.images.'launch-portrait.png'.entry_count) + wide $($ca.images.'launch-wide.png'.entry_count) entries, min $($ca.summary.overall_min_contrast):1, pass=$($ca.summary.pass)"
Write-Output ("PNG sha256: " + (($allHashes | ForEach-Object { $_.Substring(0,16) }) -join ' / '))
