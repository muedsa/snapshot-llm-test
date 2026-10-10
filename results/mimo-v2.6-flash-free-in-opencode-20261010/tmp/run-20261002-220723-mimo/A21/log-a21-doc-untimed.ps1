# log-a21-doc-untimed.ps1 - the ai-guide read A21 performed through the fetch tool at task start
# had no timestamps exposed by the environment; log it as its own row with null fields rather
# than folding it into another row or inventing values.
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$tmp = "tmp\$RUN\A21"
$utf8 = New-Object System.Text.UTF8Encoding($false)

$doc = [ordered]@{
  id = 'A21-doc-000'; task = 'A21'; type = 'doc'
  started_utc = $null; ended_utc = $null; tz = 'UTC'
  duration_ms = $null
  method = 'GET'; path = '/ai-guide.md'
  http_status = 200; content_type = 'text/markdown'; bytes = $null
  request_file = $null
  response_file = "$tmp/doc-ai-guide.md (经 A21-doc-001 落盘的同 URL 内容)"
  request_id = $null; server_timing = $null; ratelimit_remaining = $null
  error_summary = $null; attempt = 1
  note = '开工时按本题 AGENTS 通过取文工具实际读取了 https://open-snapshot.muedsa.com/ai-guide.md 全文，内容确已返回（UTF-8 纯文本请求体、成功响应为图片二进制、错误为带 code/message/requestId 的 JSON、GET /fonts 每行一个字体族等结论即来自该次阅读）。执行环境没有暴露这次工具调用的起止时刻、耗时与字节数，按约定全部记 null，不用其他量估造。A21-doc-001 是随后为把该文档落到本任务临时目录而发起的同 URL 带计时 GET。两次是同一 URL，因此 A21 的文档请求共 2 次、去重后仍是 1 篇文档。'
}
[IO.File]::AppendAllText("$tmp\requests.jsonl", (([pscustomobject]$doc | ConvertTo-Json -Depth 6 -Compress) + "`n"), $utf8)
# requests.jsonl stays strictly append-only: A21-doc-001's own note already cross-references this row.

$i = 0; $bad = 0
Get-Content "$tmp\requests.jsonl" -Encoding UTF8 | ForEach-Object { $i++; try { $null = $_ | ConvertFrom-Json } catch { $bad++ } }
"requests.jsonl -> $i rows, $bad bad"
Get-Content "$tmp\requests.jsonl" -Encoding UTF8 | ForEach-Object { $o = $_ | ConvertFrom-Json; "  {0,-14} type={1,-7} status={2}  {3} ms  dur_field_ok={4}" -f $o.id, $o.type, $o.http_status, $o.duration_ms, ($null -ne $o.duration_ms -or $o.id -eq 'A21-doc-000') }
