$ErrorActionPreference = 'Stop'
$tmp = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B03')
$enc = New-Object System.Text.UTF8Encoding($false)
$reqLog = Join-Path $tmp 'requests.jsonl'
$iterLog = Join-Path $tmp 'iterations.jsonl'
$toolLog = Join-Path $tmp 'tool-usage.jsonl'

foreach ($f in @($iterLog, $toolLog)) {
  $raw = [IO.File]::ReadAllText($f, [Text.Encoding]::UTF8)
  if ($raw.Contains('ite-B03-p19')) { throw 'p19 iteration already appended' }
}

$reqs = @()
Get-Content $reqLog -Encoding UTF8 | ForEach-Object { $reqs += ($_ | ConvertFrom-Json) }
$p19 = $null
foreach ($r in $reqs) { if ($r.id -eq 'B03-p19-stack-clip' -and $r.http_status -eq 200) { $p19 = $r } }
if ($null -eq $p19) { throw 'p19 request not found' }

# --- one syntax-fix row for the first p19 attempt (400 PARSE_ERROR) ---
$bad = $null
foreach ($r in $reqs) { if ($r.id -eq 'B03-p19-stack-clip' -and $r.http_status -ne 200) { $bad = $r } }
if ($null -ne $bad) {
  $o1 = [ordered]@{
    iteration_id = 'ite-B03-p19-syntaxfix'
    case_id = $null
    type = 'syntax-fix'
    version = $null
    parent_version = $null
    request_id = $p19.id
    http_status = $bad.http_status
    duration_ms = $bad.duration_ms
    render_started_utc = $bad.started_utc
    render_ended_utc = $bad.ended_utc
    change = '根节点 <Container> 直接挂多个 <Positioned> 改为 <Stack clipBehavior="NONE"> 包一层'
    observation = $bad.error_summary
    result = 'Container 只接受单个子节点；包 Stack 后重发即 200'
    viewed = $false
    view_evidence = '服务端 400 文本已入 requests.jsonl，无图像可看'
  }
  [IO.File]::AppendAllText($iterLog, ($o1 | ConvertTo-Json -Compress) + "`n", $enc)
}

# --- p19 capability-probe row ---
$o2 = [ordered]@{
  iteration_id = 'ite-B03-p19'
  case_id = $null
  type = 'capability-probe'
  version = $null
  parent_version = $null
  request_id = $p19.id
  http_status = $p19.http_status
  duration_ms = $p19.duration_ms
  render_started_utc = $p19.started_utc
  render_ended_utc = $p19.ended_utc
  change = '新增 4x2 对照探针：同一框体里放一个超出 100px 的子节点(A组)和一张带 boxShadow 的卡片(B组)，各测 <Stack> 默认 / NONE / HARD_EDGE / HARD_EDGE+SizedBox 四种写法'
  observation = 'A组橙块底 y=279(框底280)被裁 / y=379 溢出 / 279 / 279，即默认与 HARD_EDGE 都裁、只有 NONE 不裁；B组四张卡的阴影全部越过框底延伸到 y>=740，彼此完全相同'
  result = '定论：Stack 裁子节点、从不裁 boxShadow。推翻 p06 的阴影结论，并使 case-08 C 段从阴影对照改版为子节点裁剪对照'
  viewed = $true
  view_evidence = '读图 probes/p19-stack-clip.png + System.Drawing 按列求橙色墨迹底边与阴影底边'
}
[IO.File]::AppendAllText($iterLog, ($o2 | ConvertTo-Json -Compress) + "`n", $enc)

# --- tool-usage rows ---
$t1 = [ordered]@{
  tool_id = 'tu-08'
  tool = '探针 p19 生成与渲染（write + render-b03.ps1）'
  category = '生成程序'
  affected_cases = 'case-08'
  input = @('probes/p06-stack-shadow.snapshot', 'probes/p19-stack-clip.snapshot')
  output = @('tmp/run-20261002-220723-mimo/B03/probes/p19-stack-clip.png')
  purpose = '把 Stack 裁剪拆成 子节点 / boxShadow 两个变量 x 四种 clipBehavior 一次真实渲染，用像素底边定论'
  http_request_ids = @('B03-p19-stack-clip')
  note = '首次渲染 400 PARSE_ERROR（根 Container 挂多子节点）已入 requests.jsonl 并记 syntax-fix；重发 200，61339 字节与日志一致。A 组默认/HARD_EDGE/+SizedBox 均在框底 279 被裁、仅 NONE 溢出到 379；B 组四张卡阴影全部越过框底且彼此相同'
  double_counted = $false
}
$t2 = [ordered]@{
  tool_id = 'tu-09'
  tool = 'System.Drawing 逐像素裁剪与出血复核'
  category = '量测/放大'
  affected_cases = 'case-06, case-08, probes p06/p09/p19'
  input = @(
    'tmp/run-20261002-220723-mimo/B03/probes/p06-stack-shadow.png',
    'tmp/run-20261002-220723-mimo/B03/probes/p09-overflow-bleed.png',
    'tmp/run-20261002-220723-mimo/B03/probes/p19-stack-clip.png',
    'outputs/run-20261002-220723-mimo/B03/case-06/final.png',
    'outputs/run-20261002-220723-mimo/B03/case-08/final.png')
  output = @('probes.md 第 6、9 节更正', 'iterations.jsonl 的 evidence-correction 行')
  purpose = '用像素证据判定 Stack 是否裁剪、巨字是否真出血，替代读图主观判断'
  http_request_ids = @('B03-p06-stack-shadow', 'B03-p09-overflow-bleed', 'B03-p19-stack-clip', 'B03-case-06-r3', 'B03-case-06-r4', 'B03-case-08-r4')
  note = '纯本地像素读取，不产生新 HTTP 请求：p06 两半阴影逐点相同（唯一差异 y246..252 来自标签文字）→ 原结论推翻；p09 墨迹仅 2 字形 → 换行误读；case-06 墨迹 891→1079（页宽 1080）；case-08 左卡底 1223 / 右卡底 1293。Get-FileHash 用于确认 case-06 r2/r3 PNG 字节完全一致'
  double_counted = $false
}
[IO.File]::AppendAllText($toolLog, ($t1 | ConvertTo-Json -Compress -Depth 5) + "`n", $enc)
[IO.File]::AppendAllText($toolLog, ($t2 | ConvertTo-Json -Compress -Depth 5) + "`n", $enc)

"iterations: " + (Get-Content $iterLog -Encoding UTF8).Count
"tool-usage: " + (Get-Content $toolLog -Encoding UTF8).Count
