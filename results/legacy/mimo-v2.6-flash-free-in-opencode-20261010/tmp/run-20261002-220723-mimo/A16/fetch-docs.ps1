# A16 - fetch and retain the documents this task relies on, appending rows to
# requests.jsonl with real status / timing / bytes.
# The guide was read for this task with the harness webfetch tool immediately
# before this script runs; webfetch exposes no status/timing/bytes, so this call
# re-fetches it so the source bytes are retained and the request is loggable.
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A16'
$LOG = Join-Path $TMP 'requests.jsonl'
$ENC = New-Object Text.UTF8Encoding($false)
New-Item -ItemType Directory -Force -Path $TMP | Out-Null

$docs = @(
  [pscustomobject]@{ id = 'A16-doc-01-ai-guide'; url = 'https://open-snapshot.muedsa.com/ai-guide.md'; out = 'doc-ai-guide.md'; rely = 'Request contract: POST /snapshot, UTF-8 plain-text body (not JSON), Content-Type text/plain; charset=utf-8, PNG binary response, error JSON shape (code/message/requestId), GET /fonts and comma-separated fontFamily names, 429/Retry-After handling, do not invent tag or attribute names' }
)

foreach ($d in $docs) {
  $startUtc = (Get-Date).ToUniversalTime()
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $status = $null; $err = $null; $bytes = $null; $respFile = $null; $ctype = $null
  try {
    $r = Invoke-WebRequest -Uri $d.url -UseBasicParsing -TimeoutSec 60 -UserAgent 'snapshot-suite/1.0'
    $sw.Stop()
    $status = [int]$r.StatusCode
    $respFile = 'tmp\run-20261002-220723-mimo\A16\' + $d.out
    $abs = Join-Path $TMP $d.out
    [IO.File]::WriteAllBytes($abs, $r.RawContentStream.ToArray())
    $bytes = (Get-Item $abs).Length
    if ($r.Headers['Content-Type']) { $ctype = ($r.Headers['Content-Type'] -split ';')[0].Trim() }
  } catch {
    $sw.Stop()
    $err = $_.Exception.Message
    if ($_.Exception.Response) { $status = [int]$_.Exception.Response.StatusCode }
  }
  $endUtc = (Get-Date).ToUniversalTime()

  $row = [ordered]@{
    id                  = $d.id
    task                = 'A16'
    type                = 'document'
    started_utc         = $startUtc.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
    ended_utc           = $endUtc.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
    tz                  = 'UTC'
    duration_ms         = [math]::Round($sw.Elapsed.TotalMilliseconds, 1)
    method              = 'GET'
    path                = $d.url
    http_status         = $status
    content_type        = $ctype
    bytes               = $bytes
    request_file        = $null
    response_file       = $respFile
    request_id          = $null
    server_timing       = $null
    ratelimit_remaining = $null
    error_summary       = $err
    attempt             = 1
    note                = 'Read for this task with the harness webfetch tool immediately before this call (webfetch exposes no status/timing/bytes); re-fetched here so the source bytes are retained on disk and the request can be logged with measurable fields. Relied on for: ' + $d.rely
  }
  [IO.File]::AppendAllText($LOG, (($row | ConvertTo-Json -Compress -Depth 5) + "`n"), $ENC)
  Write-Output ("{0}  status={1} bytes={2} ms={3} err={4}" -f $d.id, $status, $bytes, [math]::Round($sw.Elapsed.TotalMilliseconds, 1), $err)
}
