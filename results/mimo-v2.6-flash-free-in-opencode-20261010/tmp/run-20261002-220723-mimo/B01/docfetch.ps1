param(
  [Parameter(Mandatory=$true)][string]$Url,
  [Parameter(Mandatory=$true)][string]$TaskId,
  [Parameter(Mandatory=$true)][string]$ReqId,
  [Parameter(Mandatory=$true)][string]$OutPath,
  [string]$LogPath = ""
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
$err = $null
$status = $null
$ctype = $null
$bytes = $null
$reqIdHdr = $null
$stHdr = $null
try {
  $r = Invoke-WebRequest -Uri $Url -Method GET -UseBasicParsing -TimeoutSec 60
  $sw.Stop()
  $status = [int]$r.StatusCode
  $ctype = $r.Headers['Content-Type']
  $bytes = $r.RawContentLength
  $reqIdHdr = $r.Headers['X-Request-Id']
  $stHdr = $r.Headers['Server-Timing']
  [IO.File]::WriteAllText($OutPath, $r.Content, $utf8)
} catch {
  $sw.Stop()
  $resp = $_.Exception.Response
  if ($resp -ne $null) {
    $status = [int]$resp.StatusCode
    $ctype = $resp.Headers['Content-Type']
    try {
      $sr = New-Object IO.StreamReader($resp.GetResponseStream())
      $body = $sr.ReadToEnd()
      $sr.Close()
      $bytes = [Text.Encoding]::UTF8.GetByteCount($body)
      [IO.File]::WriteAllText($OutPath, $body, $utf8)
      $err = $body.Substring(0, [Math]::Min(400, $body.Length))
    } catch { $err = "read failed: " + $_.Exception.Message }
  } else {
    $err = $_.Exception.Message
    $status = $null
  }
}
$endUtc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
$endLocal = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss.fffzzz')

$obj = [pscustomobject][ordered]@{
  id = $ReqId
  task = $TaskId
  type = "documentation"
  started_utc = $startUtc
  started_at = $startLocal
  ended_at = $endLocal
  ended_utc = $endUtc
  timezone = $offStr
  tz_id = $tz
  duration_ms = [Math]::Round($sw.Elapsed.TotalMilliseconds, 1)
  method = "GET"
  url = $Url
  http_status = $status
  content_type = $ctype
  bytes = $bytes
  request_file = $null
  response_file = $(if ($status -eq 200) { $OutPath } else { $OutPath })
  request_id = $reqIdHdr
  server_timing = $stHdr
  ratelimit_remaining = $null
  error_summary = $err
}
$json = ($obj | ConvertTo-Json -Compress -Depth 5)
[IO.File]::AppendAllText($LogPath, $json + "`n", $utf8)
"{0} -> {1}  {2} ms  {3} bytes  {4}" -f $ReqId, $status, $obj.duration_ms, $bytes, $Url
