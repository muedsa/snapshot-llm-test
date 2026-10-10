param(
  [Parameter(Mandatory=$true)][string]$Url,
  [Parameter(Mandatory=$true)][string]$TaskId,
  [Parameter(Mandatory=$true)][string]$ReqId,
  [Parameter(Mandatory=$true)][string]$OutPath,
  [string]$LogPath = "",
  [string]$Type = "research"
)
$ErrorActionPreference = "Stop"
$utf8 = New-Object System.Text.UTF8Encoding($false)
if ($LogPath -eq "") { $LogPath = Join-Path (Split-Path $MyInvocation.MyCommand.Path -Parent) "requests.jsonl" }
$d = Split-Path $OutPath -Parent
if ($d -and !(Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }

$tz = [TimeZoneInfo]::Local.Id
$utcOff = [TimeZoneInfo]::Local.GetUtcOffset((Get-Date)).TotalMinutes
$offStr = "UTC{0:00}:{1:00}" -f [Math]::Floor($utcOff / 60), [Math]::Abs($utcOff % 60)

$sw = [Diagnostics.Stopwatch]::StartNew()
$startUtc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
$startLocal = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss.fffzzz')
$err = $null; $status = $null; $ctype = $null; $bytes = $null; $reqIdHdr = $null; $stHdr = $null
try {
  $r = Invoke-WebRequest -Uri $Url -Method GET -UseBasicParsing -TimeoutSec 120 -Headers @{ 'User-Agent' = 'SnapshotSuite-Research/1.0 (educational visual editorial project)' }
  $sw.Stop()
  $status = [int]$r.StatusCode
  $ctype = $r.Headers['Content-Type']
  $reqIdHdr = $r.Headers['X-Request-Id']
  $stHdr = $r.Headers['Server-Timing']
  $fs = [IO.File]::Create($OutPath)
  $r.RawContentStream.Write($r.RawContentStream.ToArray(), 0, 0)
  $r.RawContentStream.Position = 0
  $r.RawContentStream.CopyTo($fs)
  $fs.Close()
  $bytes = (Get-Item $OutPath).Length
} catch {
  $sw.Stop()
  $resp = $_.Exception.Response
  if ($resp -ne $null) {
    $status = [int]$resp.StatusCode
    $ctype = $resp.Headers['Content-Type']
    try {
      $ms = New-Object IO.MemoryStream
      $resp.GetResponseStream().CopyTo($ms)
      [IO.File]::WriteAllBytes($OutPath, $ms.ToArray())
      $bytes = $ms.Length
      $err = "http " + $status
    } catch { $err = "read failed: " + $_.Exception.Message }
  } else {
    $err = $_.Exception.Message
  }
}
$endUtc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
$endLocal = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss.fffzzz')

$obj = [pscustomobject][ordered]@{
  id = $ReqId; task = $TaskId; type = $Type
  started_utc = $startUtc; started_at = $startLocal; ended_at = $endLocal; ended_utc = $endUtc
  timezone = $offStr; tz_id = $tz
  duration_ms = [Math]::Round($sw.Elapsed.TotalMilliseconds, 1)
  method = "GET"; url = $Url; http_status = $status; content_type = $ctype; bytes = $bytes
  request_file = $null; response_file = $OutPath
  request_id = $reqIdHdr; server_timing = $stHdr; ratelimit_remaining = $null
  error_summary = $err
}
[IO.File]::AppendAllText($LogPath, (($obj | ConvertTo-Json -Compress -Depth 5) + "`n"), $utf8)
"{0} -> {1}  {2} ms  {3} bytes  {4}" -f $ReqId, $status, $obj.duration_ms, $bytes, $Url
