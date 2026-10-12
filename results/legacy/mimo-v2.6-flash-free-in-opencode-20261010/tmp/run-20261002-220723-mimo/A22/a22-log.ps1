# a22-log.ps1 - appends rows to A22's temp logs (requests.jsonl / iterations.jsonl).
# Append-only: a malformed row is never rewritten in place; a correction row is appended
# instead and references the row it supersedes.
#   -Doc                 -> append the single shared documentation row (no new HTTP request)
#   -IterId ... -ViewsJson '<json array>' -> append one iteration row
#   -Corrects <id>       -> this row supersedes an earlier malformed row with that id
param(
  [switch]$Doc,
  [string]$IterId = '',
  [int]$Round = 0,
  [string]$Type = '',
  [string]$ParentId = '',
  [string]$Corrects = '',
  [string]$Image = '',
  [string]$StartedAt = '',
  [string]$EndedAt = '',
  [string]$Problem = '',
  [string]$Change = '',
  [string]$Result = '',
  [array]$Views = @()
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $root
$RUN = 'run-20261002-220723-mimo'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$reqPath = "tmp\$RUN\A22\requests.jsonl"
$itPath = "tmp\$RUN\A22\iterations.jsonl"

if ($Doc) {
  $haveDoc = $false
  if (Test-Path $reqPath) {
    foreach ($ln in @(Get-Content $reqPath -Encoding UTF8)) { if ($ln -match 'A22-doc-000') { $haveDoc = $true } }
  }
  if ($haveDoc) { 'A22-doc-000 already present' }
  else {
    # NOTE: local variable is $docRow, not $doc - PowerShell variables are case-insensitive and
    # $doc = ... would try to assign to the [switch]$Doc parameter itself.
    $docRow = [pscustomobject][ordered]@{
      id = 'A22-doc-000'; task = 'A22'; type = 'document'
      started_utc = $null; ended_utc = $null; tz = 'UTC+08:00'; duration_ms = $null
      method = 'GET'; path = 'https://open-snapshot.muedsa.com/ai-guide.md'
      http_status = $null; content_type = 'text/markdown'; bytes = 3718
      request_file = $null
      response_file = "tmp\$RUN\A21\doc-ai-guide.md"
      request_id = $null; server_timing = $null; ratelimit_remaining = $null
      error_summary = $null; attempt = 1
      source = 'shared-suite-cache'
      note = 'A22 用工具实际重读了服务指南，但没有发起新的 HTTP 请求：该 URL 的唯一一次真实 GET 是 A21-doc-001（200 / 846.4 ms / 3718 B），按总 AGENTS「缓存文件/原请求/版本/来源保留并引用；仅复用时不在后题重复计为新 HTTP 请求」归为 shared。因此本行起止时间、耗时、HTTP 状态均记 null，不伪造请求；去重后全套仍只算一次文档访问。指南要点（POST /snapshot 用 UTF-8 纯文本而非 JSON、type="png"、颜色 CSS 语法含 #RRGGBBAA、fontFamily 逗号分隔且必须与 /fonts 返回值一致、不要臆造属性、非 2xx 响应是 code/message/requestId 的 JSON、429 参考 Retry-After、默认不要 errorImage=png）已用于本题 DSL 构造。'
    }
    [IO.File]::AppendAllText($reqPath, (($docRow | ConvertTo-Json -Depth 5 -Compress) + "`n"), $utf8)
    'logged A22-doc-000 (shared cache reuse, no new HTTP request)'
  }
}

if ($IterId) {
  $vlist = @($Views)
  $row = [pscustomobject][ordered]@{
    id = $IterId; task = 'A22'; round = $Round; type = $Type
    parent_id = $(if ($ParentId) { $ParentId } else { $null })
    corrects = $(if ($Corrects) { $Corrects } else { $null })
    image = $Image
    viewed_at = $StartedAt; viewed_at_ended = $EndedAt; timezone = 'UTC+08:00'
    views = $vlist
    view_count = $vlist.Count
    observable_problem = $Problem
    change = $Change
    result_after_view = $Result
    full_visual_iteration = ($Type -eq 'visual')
    note = '基线/语法修复/方案探索/重试/需求变更分别计数；只有「看旧图 -> 修改 -> 再渲染 -> 看新图并比较」才计一次完整视觉迭代。'
  }
  [IO.File]::AppendAllText($itPath, (($row | ConvertTo-Json -Depth 8 -Compress) + "`n"), $utf8)
  "logged $IterId (round $Round, type $Type, views $($vlist.Count))$(if ($Corrects) { " [corrects $Corrects]" } else { '' })"
}
