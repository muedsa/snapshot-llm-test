$root = $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName })
Set-Location $root
$ssPath = "outputs\run-20261002-220723-mimo\_suite\suite-state.json"
$ckDir  = "tmp\run-20261002-220723-mimo\_suite\checkpoints"
$evPath = "tmp\run-20261002-220723-mimo\_suite\events.jsonl"

$now = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
$enc = New-Object System.Text.UTF8Encoding($false)

$old = Get-Content $ssPath -Raw -Encoding UTF8 | ConvertFrom-Json
$oldCopy = ($old | ConvertTo-Json -Depth 12) | ConvertFrom-Json

# ---- 1. append event 55 ----
$note = 'B01 关闭后修正（跨任务像素量测发现）：做 B02 交付前的环形量测时，用 System.Drawing 沿 B01 case-08 进度环逐 0.5 度取样，实测亮弧只有 50.14% 且自 90 度（3 点方向）起，与 case.md 声明的「75% 弧、12 点起顺时针」不符。根因是真实服务的 SWEEP 渐变不遵循 gradientStops 与 gradientStartAngle：stops=0,0.75,0.75,1 + start=-pi/2 被渲染成 [90 度, 0.75x360 度]；同一现象在 B02 case-01 以 f=0.62 复现（亮弧自 138 度起），故 B02 全程改用确定性 DialArc。修正动作：lib-b01.ps1 新增 DialArc（100 个 Rotate+C 分段，先铺暗弧后覆盖亮弧），gen-b01-b.ps1 把 case-08 的 RingProg 换成白色镂空圆 + DialArc(156,360,260,0.75,#FF8A5B,#F6E4D6,32,100)，RingProg 保留加注作为缺陷的代码证据；重新生成后 case-06/07/09/10 的 final.snapshot 哈希与修正前完全一致，仅 case-08 变化。验证：B01-c08-r2（200，4580.4ms，185785B）复测亮弧 542/720=75.28%、起点样本 716（358 度，即 12 点方向），读图工具打开 final.png 逐条核对 4 条完成标准全部通过；B01-c08-r1b 用归档的 v1 DSL 重建渲染（200，2867.3ms，179866B，与原响应字节数完全一致，说明服务渲染确定性）并打开查看，可见亮弧只覆盖 3 点->6 点->9 点的下半圈，直观复现缺陷。同步修订 case-08/case.md、portfolio.json、portfolio.md、gallery.html、snapshot-usage.md、task-metrics.json。B01 请求 31 行 = 渲染 24（200=22、400=2）+ 文档 7，渲染耗时之和 99299.1ms，请求耗时之和 108965.7ms；迭代 25 行（baseline 11 / visual-iteration 9 / visual-iteration-incomplete 1 / syntax-fix 2 / evidence-reconstruction 1 / capability-probe 1），完整视觉迭代 9；tool-usage 13 行；看图 26 次。B01 仍为 completed，current_task 仍是 B02。'
$e1 = [pscustomobject][ordered]@{
  seq = 55
  ts = $now
  type = 'task_corrected_post_closure'
  task = 'B01'
  artifact_scope = 'outputs/run-20261002-220723-mimo/B01'
  renders_added = 2
  views_added = 2
  iterations_added = 3
  note = $note
}
$line = ($e1 | ConvertTo-Json -Compress -Depth 6)
[IO.File]::AppendAllLines((Join-Path (Get-Location) $evPath), [string[]]@($line), $enc)
"events appended: 1 (seq 55); total = " + (Get-Content $evPath).Count

# ---- 2. update suite-state.json : B01 entry ----
$b01 = $null
foreach ($t in $old.tasks) { if ($t.id -eq 'B01') { $b01 = $t } }
if ($null -eq $b01) { throw 'B01 task entry not found' }

$b01.ended_at = $now
$b01.resume_notes = $b01.resume_notes + ' 【2026-10-06 关闭后修正】跨任务像素量测发现 case-08 进度环实为 50.14% 自 90 度起（根因：服务端 SWEEP 不遵循 gradientStops/gradientStartAngle）。已改用确定性 DialArc 重画并重渲染 B01-c08-r2，复测 75.28% 自 12 点起；另以归档 v1 DSL 重建渲染 B01-c08-r1b 保存被取代版本的图像证据（179866 B，与原响应字节数一致）。重新生成后 case-06/07/09/10 哈希与修正前完全一致，其余 9 件未受影响。修正后：请求 31 行（渲染 24、文档 7）、渲染耗时之和 99299.1ms、迭代 25 行、完整视觉迭代 9、tool-usage 13 行、看图 26 次；case-08 的 metrics/visual_review/evidence 已同步更新。'
$b01.unresolved_issues += '已由本修正解决的缺陷：case-08 首版进度环 50.14%（声明 75%）。遗留的服务行为知识：真实服务的 SWEEP 渐变不遵循 gradientStops 与 gradientStartAngle，任何需要精确弧度比例的进度环必须用分段构造（lib-b01.ps1 / lib-b02.ps1 的 DialArc）；B01 其余 9 件与 B02 未受影响'
$b01.visual_review_evidence += 'outputs/.../B01/case-08/final.png  1080x1080（读图工具查看修正版 B01-c08-r2，185785 B）：橙色亮弧自 12 点起顺时针到 9 点方向即止、缺口落在 9 点->12 点左上象限，System.Drawing 逐 0.5 度复测 542/720=75.28%、起点样本 716（358 度），环内 3/4、两张接种卡、10-24 预约日期与 2x2 注意事项均无位移，4 条完成标准全部通过'
$b01.visual_review_evidence += 'tmp/.../B01/attempts/pre-ringfix-20261006/case-08.v1-reconstructed.png  1080x1080（读图工具查看，179866 B，由归档 v1 DSL 经 B01-c08-r1b 重建）：橙色亮弧只覆盖 3 点->6 点->9 点的下半圈、上半圈整圈留白，与修正前 50.14% 自 90 度起的量测完全吻合，被取代尝试的缺陷可视化留档'

$old.updated_at = $now
$ckPathRel = 'tmp/run-20261002-220723-mimo/_suite/checkpoints/state-000031.json'
$old.last_checkpoint = $ckPathRel

$ssJson = $old | ConvertTo-Json -Depth 12
[IO.File]::WriteAllText((Join-Path (Get-Location) $ssPath), $ssJson, $enc)
"suite-state.json updated"

# ---- 3. checkpoint state-000031.json ----
$counts = @()
foreach ($st in @('completed','in_progress','pending','partial','blocked')) {
  $n = @($old.tasks | Where-Object { $_.status -eq $st }).Count
  $counts += [pscustomobject][ordered]@{ status = $st; count = $n }
}
$doneIds = @($old.tasks | Where-Object { $_.status -eq 'completed' } | ForEach-Object { $_.id })
$inProg  = (@($old.tasks | Where-Object { $_.status -eq 'in_progress' } | ForEach-Object { $_.id }) -join ',')
if ([string]::IsNullOrEmpty($inProg)) { $inProg = 'B02' }

$ckNote = '事件 55：B01 关闭后修正，未改变任务状态（B01 仍 completed，current_task 仍为 B02）。触发：B02 交付前的跨任务环形像素量测。缺陷：B01 case-08 进度环声明 75% 自 12 点起，实测 50.14% 自 90 度起。根因：真实服务 SWEEP 渐变不遵循 gradientStops 与 gradientStartAngle（同现象在 B02 case-01 以 f=0.62 复现）。修正：lib-b01.ps1 新增 DialArc、gen-b01-b.ps1 替换 RingProg、case-08 重渲染 B01-c08-r2、归档 v1 DSL 重建 B01-c08-r1b。验证：修正后 75.28% 自 358 度起，4 条完成标准逐条通过；回归 case-06/07/09/10 快照哈希与修正前完全一致。同步修订 case-08/case.md、portfolio.json、portfolio.md、gallery.html、snapshot-usage.md、task-metrics.json、suite-state 的 B01 条目。B01 修正后累计：请求 31 行（渲染 24：200=22、400=2；文档 7：200=7）、渲染耗时之和 99299.1ms、请求耗时之和 108965.7ms、迭代 25 行、tool-usage 13 行、看图 26 次。新增留痕：tmp/.../B01/write-logs-b01-fix.ps1、patch-portfolio.ps1、attempts/pre-ringfix-20261006/。'

$ck = [pscustomobject][ordered]@{
  schema_version = 1
  suite_version = '1.0.0'
  run_id = 'run-20261002-220723-mimo'
  profile = 'all'
  status = 'in_progress'
  snapshot_at = $now
  checkpoint_id = 'state-000031'
  checkpoint_seq = 31
  event_seq = 55
  current_task = 'B02'
  current_status = 'in_progress'
  last_checkpoint = $ckPathRel
  task_status_counts = $counts
  tasks_completed = $doneIds
  tasks_in_progress = $inProg
  checkpoint_note = $ckNote
  suite_state = $old
  source_state_copy = $oldCopy
}
$ckJson = $ck | ConvertTo-Json -Depth 14
$ckPath = Join-Path (Get-Location) "$ckDir\state-000031.json"
[IO.File]::WriteAllText($ckPath, $ckJson, $enc)
"checkpoint written: $ckPath"

# ---- verify ----
$v = Get-Content $ssPath -Raw -Encoding UTF8 | ConvertFrom-Json
$sB01 = ($v.tasks | Where-Object { $_.id -eq 'B01' }).status
$sB02 = ($v.tasks | Where-Object { $_.id -eq 'B02' }).status
"verify: B01=$sB01  B02=$sB02  current_task=$($v.current_task)  last_checkpoint=$($v.last_checkpoint)"
"verify counts: " + (($v.tasks | Group-Object status | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join ' ')
$vc = Get-Content "$ckDir\state-000031.json" -Raw -Encoding UTF8 | ConvertFrom-Json
"verify checkpoint: seq=$($vc.checkpoint_seq) event_seq=$($vc.event_seq) current=$($vc.current_task) completed=$($vc.tasks_completed.Count) inprog=$($vc.tasks_in_progress)"
