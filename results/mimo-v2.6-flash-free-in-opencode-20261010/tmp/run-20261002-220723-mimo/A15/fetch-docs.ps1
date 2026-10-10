# A15 - fetch and retain the two DSL documents this task relied on, and append
# their rows to requests.jsonl with real status / timing / size.
# Both documents were already read earlier in this task (before any DSL was
# written) with the harness webfetch tool, which exposes no status, timing or
# bytes; this call re-fetches them so the source bytes are retained on disk and
# the request can be logged with measurable fields.
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A15'
$LOG = Join-Path $TMP 'requests.jsonl'
$ENC = New-Object Text.UTF8Encoding($false)

$docs = @(
  [pscustomobject]@{ id = 'A15-doc-01-parser-tags'; url = 'https://snapshot.muedsa.com/reference/parser-tags/';      out = 'doc-parser-tags.html';      ct = 'text/html'; rely = 'Tag vocabulary for Snapshot / Container / Positioned / Text / Stack and the attribute names actually emitted by gen.ps1' },
  [pscustomobject]@{ id = 'A15-doc-02-container';    url = 'https://snapshot.muedsa.com/widgets/layout/container/';   out = 'doc-container-widget.html'; ct = 'text/html'; rely = 'Container width/height/padding/color/border/borderRadius/alignment/boxShadow behaviour used for every card, pill and bar' }
)

$rows = @()
foreach ($d in $docs) {
  $startUtc = (Get-Date).ToUniversalTime()
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $status = $null; $err = $null; $bytes = $null; $respFile = $null; $ctype = $d.ct
  try {
    $r = Invoke-WebRequest -Uri $d.url -UseBasicParsing -TimeoutSec 60 -UserAgent 'snapshot-suite/1.0'
    $sw.Stop()
    $status = [int]$r.StatusCode
    $respFile = 'tmp\run-20261002-220723-mimo\A15\' + $d.out
    $abs = Join-Path $TMP $d.out
    [IO.File]::WriteAllBytes($abs, $r.RawContentStream.ToArray())
    $bytes = (Get-Item $abs).Length
    if ($r.Headers['Content-Type']) { $ctype = ($r.Headers['Content-Type'] -split ';')[0].Trim() }
  } catch {
    $sw.Stop()
    $err = $_.Exception.Message
    if ($_.Exception.Response) {
      $status = [int]$_.Exception.Response.StatusCode
      $respFile = $null
    }
  }
  $endUtc = (Get-Date).ToUniversalTime()

  $row = [ordered]@{
    id              = $d.id
    task            = 'A15'
    type            = 'document'
    started_utc     = $startUtc.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
    ended_utc       = $endUtc.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
    tz              = 'UTC'
    duration_ms     = [math]::Round($sw.Elapsed.TotalMilliseconds, 1)
    method          = 'GET'
    path            = $d.url
    http_status     = $status
    content_type    = $ctype
    bytes           = $bytes
    request_file    = $null
    response_file   = $respFile
    request_id      = $null
    server_timing   = $null
    ratelimit_remaining = $null
    error_summary   = $err
    attempt         = 1
    note            = 'Read earlier in this task with the harness webfetch tool (no status/timing/bytes exposed) before any DSL was written; re-fetched here so the source bytes are retained and the request could be logged with measurable fields. Used for: ' + $d.rely
  }
  $rows += $row
  [IO.File]::AppendAllText($LOG, (($row | ConvertTo-Json -Compress -Depth 5) + "`n"), $ENC)
  Write-Output ("{0}  status={1} bytes={2} ms={3} err={4}" -f $d.id, $status, $bytes, [math]::Round($sw.Elapsed.TotalMilliseconds, 1), $err)
}
