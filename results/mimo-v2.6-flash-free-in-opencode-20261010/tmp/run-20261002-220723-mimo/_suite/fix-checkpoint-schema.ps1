# fix-checkpoint-schema.ps1
# state-000027.json was written with a deviating field schema (source_state_copy as a
# path string, tasks_completed/tasks_in_progress/task_status_counts as scalars/objects,
# checkpoint_id with the .json suffix). Checkpoints must never be overwritten, so this
# appends a schema-conforming state-000028.json and records the supersession in events.
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture = [cultureinfo]::InvariantCulture
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $root
$enc = New-Object System.Text.UTF8Encoding($false)

$suiteTmp = 'tmp\run-20261002-220723-mimo\_suite'
$ssPath = 'outputs\run-20261002-220723-mimo\_suite\suite-state.json'
$now = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')

$ck27 = Join-Path $suiteTmp 'checkpoints\state-000027.json'
if (-not (Test-Path $ck27)) { throw 'state-000027.json missing' }
$s27 = Get-Content $ck27 -Raw | ConvertFrom-Json

$ss = Get-Content $ssPath -Raw | ConvertFrom-Json

# ---- build a schema-conforming checkpoint (same shape as state-000026) ----
# keep the established ordering: completed, in_progress, pending, ...
$order = @('completed', 'in_progress', 'pending', 'partial', 'blocked')
$counts = @($order | Where-Object { $n = $_; @($ss.tasks | Where-Object { $_.status -eq $n }).Count -gt 0 } |
  ForEach-Object { $n = $_; [pscustomobject]@{ status = $n; count = @($ss.tasks | Where-Object { $_.status -eq $n }).Count } })

$completedIds = @($ss.tasks | Where-Object { $_.status -eq 'completed' } | ForEach-Object { $_.id })
$inProgIds = @($ss.tasks | Where-Object { $_.status -eq 'in_progress' } | ForEach-Object { $_.id })
$inProg = ($inProgIds -join ', ')

$note = 'A23 关闭（events 48），A24 开启（events 49）。A23：19 个产物 = 7 组 PNG+DSL + limitations.md + frame-data.json + timing.json + snapshot-usage.md + task-metrics.json，12/12 指定交付齐全、生成器 problems=0；SVG / CMYK / 单文件 GIF 三项基于真实 openapi.yaml（svg/cmyk/icc/gif/animat/keyframe/timeline/duration/frame 命中全 0、仅 10 端点）与渲染指南 else -> error("Unsupported image type") 判定原生不支持，PNG 封面与透明 PNG 原生支持（探针 A23p1 实测 A=128 / A=0、colorType=6）；授权替代全部交付且未伪造目标格式文件；6 帧各 12 单元、6666 路径样本重叠 0、末帧 x=300 镜像对称、五步 30.45/30.46px 匀速；timing.json seamless=false 明写循环跳变 104.3px。请求 23 行全 200（渲染 16 + 文档 7，52443.2ms），失败 0、重试 0、限流 0；看图 26 次（fresh 13 / 陈旧缓冲 13，最终 7 张逐张打开 + 接触表确认）；迭代 4 行、完整视觉迭代 2。suite-state.json 中 A23=completed、A24=in_progress。本检查点 state-000028 按 state-000026 的字段schema 重建，取代字段schema 偏离的 state-000027（后者未被覆盖，原样保留）。'

$ckpt = [pscustomobject][ordered]@{
  schema_version = $ss.schema_version
  suite_version = $ss.suite_version
  run_id = $ss.run_id
  profile = $ss.profile
  status = $ss.status
  snapshot_at = $now
  checkpoint_id = 'state-000028'
  checkpoint_seq = 28
  event_seq = 50
  current_task = $ss.current_task
  current_status = 'in_progress'
  last_checkpoint = 'tmp/run-20261002-220723-mimo/_suite/checkpoints/state-000028.json'
  task_status_counts = $counts
  tasks_completed = $completedIds
  tasks_in_progress = $inProg
  checkpoint_note = $note
  suite_state = $ss
  source_state_copy = $ss
}

$ck28 = Join-Path $suiteTmp 'checkpoints\state-000028.json'
if (Test-Path $ck28) { throw "refusing to overwrite existing checkpoint: $ck28" }
[IO.File]::WriteAllText($ck28, ((ConvertTo-Json $ckpt -Depth 12) + "`n"), $enc)
'wrote ' + $ck28 + '  bytes=' + (Get-Item $ck28).Length

# ---- repoint the live pointer ----
$ss2 = Get-Content $ssPath -Raw | ConvertFrom-Json
$ss2.last_checkpoint = 'tmp/run-20261002-220723-mimo/_suite/checkpoints/state-000028.json'
$ss2.updated_at = $now
[IO.File]::WriteAllText($ssPath, ((ConvertTo-Json $ss2 -Depth 12) + "`n"), $enc)
'repointed suite-state.json last_checkpoint -> state-000028.json'

# ---- append event 50 (append-only correction) ----
$ev50 = [pscustomobject][ordered]@{
  seq = 50
  ts = $now
  type = 'checkpoint_corrected'
  task = 'A23'
  corrects = 'state-000027.json'
  note = 'state-000027.json 的字段 schema 与既有检查点不一致：source_state_copy 写成了路径字符串（既有为完整状态对象）、tasks_completed 写成整数 23（既有为任务 ID 数组）、tasks_in_progress 写成整数 1（既有为任务 ID 字符串）、task_status_counts 写成对象（既有为 {status,count} 数组）、checkpoint_id 带了 .json 后缀。按“检查点不可覆盖”的约定，state-000027.json 原样保留未改写，另行追加字段 schema 与 state-000026 一致的 state-000028.json，并把 suite-state.json 的 last_checkpoint 指向 000028。两者的 suite_state 内容一致（A23=completed、A24=in_progress、completed 23 / in_progress 1 / pending 6）。事件内容与进度事实未改变。'
}
[string[]]$l50 = @(ConvertTo-Json $ev50 -Depth 5 -Compress)
[IO.File]::AppendAllLines((Join-Path $suiteTmp 'events.jsonl'), $l50, $enc)
'events.jsonl now ' + (Get-Content (Join-Path $suiteTmp 'events.jsonl')).Count + ' lines'

# ---- verify ----
''
'--- verify state-000028 vs state-000026 schema ---'
$p = Get-Content (Join-Path $suiteTmp 'checkpoints\state-000026.json') -Raw | ConvertFrom-Json
$c = Get-Content $ck28 -Raw | ConvertFrom-Json
foreach ($k in ($p.PSObject.Properties.Name)) {
  $t1 = if ($p.$k -eq $null) { 'null' } else { $p.$k.GetType().Name }
  $t2 = if ($c.$k -eq $null) { 'null' } else { $c.$k.GetType().Name }
  $flag = if ($t1 -eq $t2) { '' } else { '   <-- MISMATCH' }
  "  {0,-24} prev={1,-14} cur={2,-14}{3}" -f $k, $t1, $t2, $flag
}
''
'  counts   = ' + (ConvertTo-Json $c.task_status_counts -Compress)
'  completed= ' + @($c.tasks_completed).Count + ' ids; in_progress = ' + $c.tasks_in_progress
'  ckpt id  = ' + $c.checkpoint_id + '  seq=' + $c.checkpoint_seq + ' event_seq=' + $c.event_seq
'  state-000027 still present = ' + (Test-Path $ck27)
$ssF = Get-Content $ssPath -Raw | ConvertFrom-Json
'  suite-state last_checkpoint = ' + $ssF.last_checkpoint
