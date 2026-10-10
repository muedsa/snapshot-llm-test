$ErrorActionPreference = 'Stop'
$tmp = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B03')
$enc = New-Object System.Text.UTF8Encoding($false)
$iterLog = Join-Path $tmp 'iterations.jsonl'
$reqLog = Join-Path $tmp 'requests.jsonl'

if ([IO.File]::ReadAllText($iterLog, [Text.Encoding]::UTF8).Contains('ite-B03-c08-v5')) {
  throw 'c08-v5 already appended'
}
$reqs = @()
Get-Content $reqLog -Encoding UTF8 | ForEach-Object { $reqs += ($_ | ConvertFrom-Json) }
$r = $null
foreach ($x in $reqs) { if ($x.id -eq 'B03-case-08-r5' -and $x.http_status -eq 200) { $r = $x } }
if ($null -eq $r) { throw 'B03-case-08-r5 not found' }

$o = [ordered]@{
  iteration_id = 'ite-B03-c08-v5'
  case_id = 'case-08'
  type = 'visual'
  version = 'v5'
  parent_version = 'v4'
  request_id = $r.id
  http_status = $r.http_status
  duration_ms = $r.duration_ms
  render_started_utc = $r.started_utc
  render_ended_utc = $r.ended_utc
  change = '页脚「参考实现见 B08 设计系统」改为「本页为虚构规范演示」'
  observation = '交付前跨任务交叉引用核查：本套 catalog 的任务只有 A01-A24 与 B01-B06，不存在 B08，该句会指向一个查不到的产物；B02 的 design-system.json 也没有 elevation 字段可承接，因此不能改成 B02'
  result = 'round 5 渲染，读图确认页脚两段（左侧说明 / 右侧 DEMO . 演示数据）完好、全图无 B08'
  viewed = $true
  view_evidence = '读图 outputs/.../B03/case-08/final.png（209634 字节）页脚区域'
}
[IO.File]::AppendAllText($iterLog, ($o | ConvertTo-Json -Compress) + "`n", $enc)
'iterations: ' + (Get-Content $iterLog -Encoding UTF8).Count
