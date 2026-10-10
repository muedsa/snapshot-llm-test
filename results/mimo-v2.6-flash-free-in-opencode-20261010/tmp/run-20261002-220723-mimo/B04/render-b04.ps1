param(
  [Parameter(Mandatory=$true)][string]$DslPath,
  [Parameter(Mandatory=$true)][string]$OutPath,
  [Parameter(Mandatory=$true)][string]$TaskId,
  [Parameter(Mandatory=$true)][string]$ReqId,
  [string]$CaseId = "",
  [string]$Url = "https://open-snapshot.muedsa.com/snapshot",
  [int]$MaxRetry = 8,
  [string]$LogPath = ""
)
$ErrorActionPreference = "Stop"
$utf8 = New-Object System.Text.UTF8Encoding($false)
if ($LogPath -eq "") {
  $root = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\B04')
  $LogPath = Join-Path $root "requests.jsonl"
}
$dir = Split-Path $OutPath -Parent
if ($dir -and !(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }

$tzId = [TimeZoneInfo]::Local.Id
$utcOff = [TimeZoneInfo]::Local.GetUtcOffset((Get-Date)).TotalMinutes
$tzLabel = "UTC{0:00}:{1:00}" -f [Math]::Floor($utcOff / 60), [Math]::Abs($utcOff % 60)

function Log-Line($obj) {
  $json = ($obj | ConvertTo-Json -Compress -Depth 6)
  [IO.File]::AppendAllText($LogPath, $json + "`n", $utf8)
}

$attempt = 0
$baseUrl = $Url
while ($attempt -le $MaxRetry) {
  $attempt++
  $rid = $ReqId
  if ($attempt -gt 1) { $rid = "$ReqId-a$attempt" }
  $hdr = Join-Path $env:TEMP ("hdr-" + [Guid]::NewGuid().ToString("N") + ".txt")
  $errBody = Join-Path $env:TEMP ("err-" + [Guid]::NewGuid().ToString("N") + ".bin")
  $start = (Get-Date).ToUniversalTime()
  $startLocal = (Get-Date)
  $t0 = Get-Date
  $code = curl.exe -sS -D $hdr -X POST $baseUrl -H "Content-Type: text/plain; charset=utf-8" --data-binary "@$DslPath" -o $errBody -w "%{http_code}"
  $ms = [math]::Round(((Get-Date)-$t0).TotalMilliseconds,1)
  $end = (Get-Date).ToUniversalTime()
  $headers = @{}
  Get-Content $hdr | ForEach-Object {
    if ($_ -match '^([^:]+):\s*(.*)$') { $headers[$matches[1].ToLower()] = $matches[2] }
  }
  $ctype = if ($headers.ContainsKey('content-type')) { $headers['content-type'] } else { $null }
  $reqIdHdr = if ($headers.ContainsKey('x-request-id')) { $headers['x-request-id'] } else { $null }
  $st = if ($headers.ContainsKey('server-timing')) { $headers['server-timing'] } else { $null }
  $rl = if ($headers.ContainsKey('x-ratelimit-remaining')) { $headers['x-ratelimit-remaining'] } else { $null }
  $bytes = if (Test-Path $errBody) { (Get-Item $errBody).Length } else { 0 }

  $entry = [ordered]@{
    id = $rid; task = $TaskId; case_id = $(if ($CaseId -ne "") { $CaseId } else { $null }); type = "render"
    dsl_chars = $(try { (Get-Item $DslPath).Length } catch { $null })
    started_utc = $start.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
    ended_utc = $end.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
    started_at = $startLocal.ToString("yyyy-MM-ddTHH:mm:ss.fffzzz")
    ended_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffzzz")
    timezone = $tzLabel
    tz_id = $tzId
    duration_ms = $ms
    method = "POST"; path = "/snapshot"
    http_status = [int]$code
    content_type = $ctype
    bytes = $bytes
    request_file = $DslPath
    response_file = $null
    request_id = $reqIdHdr
    server_timing = $st
    ratelimit_remaining = $rl
    error_summary = $null
    attempt = $attempt
  }

  if ($code -eq "200" -and $ctype -like "image/*") {
    Move-Item -Force $errBody $OutPath
    $entry.response_file = $OutPath
    Log-Line $entry
    Remove-Item $hdr -ErrorAction SilentlyContinue
    Write-Output "OK $code $ms ms $bytes B -> $OutPath"
    exit 0
  }

  $failDir = Join-Path (Split-Path $DslPath -Parent) "failures"
  if (!(Test-Path $failDir)) { New-Item -ItemType Directory -Force -Path $failDir | Out-Null }
  $failPath = Join-Path $failDir ($rid + ".body")
  Move-Item -Force $errBody $failPath
  $entry.response_file = $failPath
  $msg = ""
  try { $j = Get-Content $failPath -Raw | ConvertFrom-Json; $msg = "$($j.code): $($j.message)" } catch { $msg = (Get-Content $failPath -Raw) }
  $entry.error_summary = $msg
  Log-Line $entry
  Remove-Item $hdr -ErrorAction SilentlyContinue

  if ($code -eq "429" -or $code -eq "503") {
    $ra = 5
    if ($headers.ContainsKey('retry-after')) { $ra = [int]$headers['retry-after'] }
    Write-Output "RATE $code retry-after=$ra attempt=$attempt"
    Start-Sleep -Seconds ($ra + 1)
    continue
  }
  Write-Output "FAIL $code $msg"
  exit 1
}
Write-Output "FAIL exhausted retries"
exit 1
