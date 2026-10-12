$ErrorActionPreference = 'Stop'
$tmp = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B03')
$enc = New-Object System.Text.UTF8Encoding($false)
$iterLog = Join-Path $tmp 'iterations.jsonl'
$reqLog = Join-Path $tmp 'requests.jsonl'

if ([IO.File]::ReadAllText($iterLog, [Text.Encoding]::UTF8).Contains('ite-B03-c10-v5')) {
  throw 'c10-v5 already appended'
}
$reqs = @()
Get-Content $reqLog -Encoding UTF8 | ForEach-Object { $reqs += ($_ | ConvertFrom-Json) }

$bad = $null; $ok = $null
foreach ($x in $reqs) {
  if ($x.id -eq 'B03-case-10-r5') {
    if ($x.http_status -eq 200) { $ok = $x } else { $bad = $x }
  }
}
if ($null -eq $bad) { throw 'case-10 r5 400 row not found' }
if ($null -eq $ok)  { throw 'case-10 r5 200 row not found' }

$o1 = [ordered]@{
  iteration_id = 'ite-B03-c10-r5-syntaxfix'
  case_id = 'case-10'
  type = 'syntax-fix'
  version = $null
  parent_version = $null
  request_id = $bad.id
  http_status = $bad.http_status
  duration_ms = $bad.duration_ms
  render_started_utc = $bad.started_utc
  render_ended_utc = $bad.ended_utc
  change = "第三条图例行 items 写成 `@(`@('#7FB07A','树木'))`，PowerShell 的 `@()` 对已经是数组的表达式原样返回，外层括号被吃掉，items 变成扁平的字符串数组"
  observation = $bad.error_summary
  result = 'items[0] 退化成字符串 "#7FB07A"，[0] 取到首字符 "#"，服务端 400 PARSE_ERROR；改为 @(, $treePair) 强制保留一层数组后重发即 200'
  viewed = $false
  view_evidence = '服务端 400 文本已入 requests.jsonl 与 case-10/failures/B03-case-10-r5.body，无图像可看'
}
[IO.File]::AppendAllText($iterLog, ($o1 | ConvertTo-Json -Compress) + "`n", $enc)

$o2 = [ordered]@{
  iteration_id = 'ite-B03-c10-v5'
  case_id = 'case-10'
  type = 'visual'
  version = 'v5'
  parent_version = 'v4'
  request_id = $ok.id
  http_status = $ok.http_status
  duration_ms = $ok.duration_ms
  render_started_utc = $ok.started_utc
  render_ended_utc = $ok.ended_utc
  change = '新增第三条图例行「绿化 / 树木 #7FB07A」（y=300，单项 x140..294），键出 5 座 h=0.55 的绿色矮体'
  observation = 'round 4 已修正 5 座馆体的配色键，但图上仍有 5 个短绿块在图例里没有任何一行解释；图例必须能解释图上的每一种形体'
  result = 'round 5 渲染；读图确认三条图例齐全、图例块（x72..294 / y300..326）与图形最高点（(1,1) 馆顶面 x520..680 / y319）无重叠，指南针、页脚、底部条完好'
  viewed = $true
  view_evidence = '读图 outputs/.../B03/case-10/final.png（122860 字节，1200x1200）图例区与全区'
}
[IO.File]::AppendAllText($iterLog, ($o2 | ConvertTo-Json -Compress) + "`n", $enc)

'iterations: ' + (Get-Content $iterLog -Encoding UTF8).Count
