# doc-fetch.ps1 - GET a documentation URL with real timing and append to requests.jsonl
param(
  [Parameter(Mandatory=$true)][string]$Url,
  [Parameter(Mandatory=$true)][string]$OutPath,
  [Parameter(Mandatory=$true)][string]$ReqId,
  [Parameter(Mandatory=$true)][string]$LogPath,
  [string]$TaskId = 'A23',
  [string]$Corrects = '',
  [string]$Note = ''
)
$ErrorActionPreference = 'Stop'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$dir = Split-Path $OutPath -Parent
if ($dir -and !(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }

$hdr  = Join-Path $env:TEMP ("dh-" + [Guid]::NewGuid().ToString('N') + '.txt')
$t0   = Get-Date
$code = curl.exe -sS -L -D $hdr -o $OutPath -w '%{http_code}' $Url
$ms   = [math]::Round(((Get-Date) - $t0).TotalMilliseconds, 1)
$t1   = $t0.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
$t2   = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ')

$headers = @{}
if (Test-Path $hdr) {
  Get-Content $hdr | ForEach-Object {
    if ($_ -match '^([^:]+):\s*(.*)$') { $headers[$matches[1].ToLower()] = $matches[2] }
  }
  Remove-Item $hdr -Force
}
$ctype = $null
if ($headers.ContainsKey('content-type')) { $ctype = ($headers['content-type'] -split ';')[0].Trim() }
# NB: never name this $reqId - PowerShell variables are case-insensitive and it would
#     clobber the [string]$ReqId parameter (that is exactly what the first run did).
$hdrRequestId = $null
if ($headers.ContainsKey('x-request-id')) { $hdrRequestId = $headers['x-request-id'] }
$st = $null
if ($headers.ContainsKey('server-timing')) { $st = $headers['server-timing'] }
$rl = $null
if ($headers.ContainsKey('ratelimit-remaining')) { $rl = $headers['ratelimit-remaining'] }
$uri = [Uri]$Url
$bytes = 0
if (Test-Path $OutPath) { $bytes = (Get-Item $OutPath).Length }

$row = [pscustomobject][ordered]@{
  id = $ReqId; task = $TaskId; type = 'documentation'
  started_utc = $t1; ended_utc = $t2; tz = 'UTC'
  duration_ms = $ms; method = 'GET'; path = $uri.AbsolutePath
  http_status = [int]$code; content_type = $ctype; bytes = $bytes
  request_file = $Url; response_file = $OutPath
  request_id = $hdrRequestId; server_timing = $st; ratelimit_remaining = $rl
  error_summary = $(if ([int]$code -ge 400) { "HTTP $code" } else { $null }); attempt = 1
}
if ($Corrects -ne '') { $row | Add-Member -NotePropertyName 'corrects' -NotePropertyValue $Corrects }
if ($Note -ne '') { $row | Add-Member -NotePropertyName 'note' -NotePropertyValue $Note }
[IO.File]::AppendAllText($LogPath, (($row | ConvertTo-Json -Compress -Depth 6) + "`n"), $utf8)
Write-Output ("{0}  HTTP {1}  {2} ms  {3} bytes  {4}  -> {5}" -f $ReqId, $code, $ms, $bytes, $ctype, $OutPath)
